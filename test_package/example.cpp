#include <iostream>
#include <libs3.h>

int main() {
    S3_initialize(nullptr, 0, nullptr);
    S3_deinitialize();
}
