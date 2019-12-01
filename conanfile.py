from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.util.files import mkdir
from conans.client.tools import check_output
from conans.util.files import mkdir 

class Libs3Conan(ConanFile):
    name = "libs3"
    version = "4.1"
    license = "LGPL"
    author = "Bryan Ischo <bryan@ischo.com>"
    url = "https://github.com/bji/libs3"
    description = "C Library and Tools for Amazon S3 Access"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"

    @property
    def makefile(self):
        makefile = 'GNUmakefile'
        if self.settings.os == 'Macos':
            makefile = 'GNUmakefile.osx'
        elif self.settings.os == 'Windows':
            makefile = 'GNUmakefile.mingw'
        return makefile

    def source(self):
        self.run("git clone https://github.com/bji/libs3.git")

    def requirements(self):
        if self.run('curl-config --version', ignore_errors=True) != 0:
            self.requires('libcurl/7.64.1')
            self.requires('openssl/1.0.2t')
        if self.run('xml2-config --version', ignore_errors=True) != 0:
            self.requires('libxml2/2.9.9')
            self.requires('libiconv/1.15')
            self.requires('zlib/1.2.11')

    def dependency_flags(self, dependency_name):
        cflags = ' '.join([f'-I{path}' for path in self.deps_cpp_info[dependency_name].include_paths])
        libs = ' '.join([f'-l{lib}' for lib in self.deps_cpp_info[dependency_name].libs] + [f'-L{dir}' for dir in self.deps_cpp_info[dependency_name].lib_paths])
        return cflags, libs

    def build(self):
        with tools.chdir("libs3"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools_vars = autotools.vars
            autotools_vars['CFLAGS'] = '-Wno-error=unused-parameter'
            if 'libcurl' in self.deps_cpp_info.deps:
                autotools_vars['CURL_CFLAGS'], autotools_vars['CURL_LIBS'] = self.dependency_flags('libcurl')
                for lib in ['openssl']:
                    autotools_vars['CURL_LIBS'] +=  ' ' + self.dependency_flags(lib)[1]
            if 'libxml2' in self.deps_cpp_info.deps:
                autotools_vars['LIBXML2_CFLAGS'], autotools_vars['LIBXML2_LIBS'] = self.dependency_flags('libxml2')
                for lib in ['libiconv', 'zlib']:
                    autotools_vars['LIBXML2_LIBS'] +=  ' ' + self.dependency_flags(lib)[1]
            autotools.make(args=['-f', self.makefile], vars=autotools_vars)

    def package(self):
        with tools.chdir("libs3"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools_vars = autotools.vars
            autotools_vars['DESTDIR'] = self.package_folder
            for dir in ['bin', 'lib', 'include']:
                mkdir(f'{self.package_folder}/{dir}')
            autotools.install(args=['-f', self.makefile], vars=autotools_vars)

    def package_info(self):
        self.cpp_info.libs = ["s3"]

