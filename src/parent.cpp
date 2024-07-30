#include <iostream>
#include <vector>
#include <chrono>
#include <thread>
#include <sstream>

#include <cstdio>
#include <cstdlib>
#include <cstdarg>
#include <unistd.h>

#include "common.hpp"
#include "utils.hpp"
#include "log.hpp"

typedef struct Config {
    std::string name;
    int rate, duration, warmup;
    bool verbose;
    std::vector<struct sockaddr_in> addrs;

    bool valid(void) {
        if (this->duration == 0)
            return false;

        if (this->rate == 0)
            return false;

        if (this->addrs.empty()) 
            return false;

        return true;
    }

    Config(): name(""), 
              rate(0), 
              duration(0), 
              warmup(0), 
              verbose(false)
              {};
} Config_t;

Config_t config;

void usage(int e) {
    std::string str = "Usage: ./parent "
                      "[-a ADDR_1 ADDR_2] "
                      "[-r rate] [-d duration] "
                      "[-h] [-v]";

    fprintf(stdout, "%s\n", str.c_str());
    exit(e);
}

int parse(int argc, char **argv) {
    int opt = 0, opti = 0;
    int ret = 0;
    while ( (opt = getopt (argc, argv, "ha:r:d:w:v") ) != -1 ) {
        switch (opt) {
        case 'h':
            usage(EXIT_SUCCESS);
            break;

        case 'v':
            config.verbose = true;
            break;

        case 'a':
            opti = optind - 1;
            while (optind < argc && argv[opti][0] != '-') {
                auto parts = split(std::string {argv[opti]}, ':');
                config.addrs.push_back(socketaddr(parts[0], atoi(parts[1].c_str())));
                opti++;
            }
            optind = opti - 1;
            break;

        case 'r':
            config.rate = atoi(optarg);
            break;

        case 'd':
            config.duration = atoi(optarg);
            break;

        case 'w':
            config.warmup = atoi(optarg);
            break;

        default:
            usage(EXIT_FAILURE);
            break;
        }
    }

    if (optind > argc || !config.valid()) usage(EXIT_FAILURE);
    return ret;
}

int parent(void) {
    int sockfd;
    int cnt = 0, n, total = config.addrs.size();
    auto packets = (int64_t)config.rate * (config.duration + config.warmup);

    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    if (config.verbose) {
        log("PARENT: SOCKET OPENED\n");
        log("PARENT: PACKETS=%lu | DURATION=%d | RATE=%d\n", packets, config.duration, config.rate);
    }

    auto start  = std::chrono::system_clock::now();
    auto step = std::chrono::duration<double>(1) / config.rate;

    for (int64_t i = 0; i < packets; i++) {
        MsgUDP_t m = MsgUDP();
        m.id  = (cnt++);
        m.ts  = timestamp();

        for (int j = 0; j<total; j++) {
            n = sendto(sockfd, &m, sizeof(MsgUDP_t), 0, (struct sockaddr *) &config.addrs[j], sizeof(config.addrs[j]));
            if ( n < 0 ) {
                fprintf(stderr, "Failed to send\n");
                exit(EXIT_FAILURE);
            } else {
                if (config.verbose)
                    log("PARENT: SENT[%4lu] => ADDR[%d]\n", i, j);
            }
        }
        std::this_thread::sleep_until(start + (step * i));
    }

    if (config.verbose)
        log("PARENT: END\n");

    close(sockfd);
    return 0;
}

int main(int argc, char **argv) {
    parse(argc, argv);
    return parent();
}
