#include "common.hpp"

#include <cstdlib>
#include <chrono>

int64_t timestamp(void) {
    auto cur    = std::chrono::system_clock::now();
    auto epoch  = cur.time_since_epoch();
    auto ms     = std::chrono::duration_cast<std::chrono::microseconds>(epoch);
    int64_t ts = ms.count();
    return ts;
}
