#include "common.hpp"

#include <cstdlib>
#include <chrono>
#include <fstream>
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

int64_t future (int64_t timestamp, float dur_sec) {
    int64_t dur = static_cast<int64_t>(dur_sec * 1'000'000);
    return timestamp + dur;
}

double get_percentile(const std::vector<int64_t>& data, double percentile) {
    if (data.empty()) {
        throw std::runtime_error("Data vector is empty");
    }

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

double get_variance(const std::vector<int64_t>& data) {
    if (data.empty()) {
        throw std::runtime_error("Data vector is empty");
    }

    double mean = std::accumulate(data.begin(), data.end(), 0.0) / data.size();
    double sum = 0.0, variance = 0.0;

    for(const auto& latency : data) {
        sum += std::pow(latency - mean, 2);
    }

    variance = sum / data.size();
    return variance;
}

double get_mean(const std::vector<int64_t>& data) {
    if (data.empty()) {
        throw std::runtime_error("Data vector is empty");
    }
    double mean = std::accumulate(data.begin(), data.end(), 0.0) / data.size();
    return mean;
}

double get_stdev(const std::vector<int64_t>& data) {
    if (data.empty()) {
        throw std::runtime_error("Data vector is empty");
    }

    double mean = std::accumulate(data.begin(), data.end(), 0.0) / data.size();
    double sum = 0.0, variance = 0.0, stddev = 0.0;

    for (const auto& latency : data) {
        sum += std::pow(latency - mean, 2);
    }

    variance = sum / data.size();
    stddev = std::sqrt(variance);
    return stddev;
}

int write_csv(const std::vector<int64_t>& data, std::string name, std::string header) {
    std::string filename    = "/work/logs/" + name + ".csv";
    std::ofstream f(filename);

    if (!f.is_open())
        return -1;

    if (header != "") {
        f << header << "\n";
    }

    for (size_t i = 0; i < data.size(); ++i)
        f << i << "," << data[i] << "\n";

    f.close();
    return 0;
}
