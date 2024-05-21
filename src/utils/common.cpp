#include "common.hpp"

#include <cstdlib>
#include <chrono>
#include <iostream>
#include <algorithm>
#include <random>

int64_t timestamp(void) {
    auto cur    = std::chrono::system_clock::now();
    auto epoch  = cur.time_since_epoch();
    auto us     = std::chrono::duration_cast<std::chrono::microseconds>(epoch);
    int64_t ts  = us.count();
    return ts;
}

int64_t deadline(float dur_sec) {
    auto cur    = std::chrono::system_clock::now();
    auto dur    = std::chrono::duration<float>(dur_sec);
    auto future = cur + std::chrono::duration_cast<std::chrono::system_clock::duration>(dur);
    auto epoch  = future.time_since_epoch();
    auto us     = std::chrono::duration_cast<std::chrono::microseconds>(epoch);
    int64_t ts  = us.count();
    return ts;
}

double get_percentile(const std::vector<int64_t>& data, double percentile) {
    if (data.empty()) return 0.0;

    std::vector<int64_t> sorted_data = data;
    std::sort(sorted_data.begin(), sorted_data.end());

    int index = (percentile / 100.0) * (sorted_data.size() - 1);

    if (index == floor(index)) {
        return sorted_data[static_cast<size_t>(index)];
    } else {
        size_t floorIndex = static_cast<size_t>(floor(index));
        size_t ceilIndex = static_cast<size_t>(ceil(index));
        int floorValue = sorted_data[floorIndex];
        int ceilValue = sorted_data[ceilIndex];
        return floorValue + (index - floor(index)) * (ceilValue - floorValue);
    }
}

struct timeval timeout(int dur_ms) {
    struct timeval timeout;
    int N = dur_ms;
    timeout.tv_sec = N / 1000;
    timeout.tv_usec = (N % 1000) * 1000;
    return timeout;
}
