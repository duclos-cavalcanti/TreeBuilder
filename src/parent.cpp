#include <iostream>
#include <vector>
#include <chrono>
#include <thread>
#include <sstream>

#include <cstdio>
#include <cstdlib>
#include <unistd.h>

#include "common.hpp"

FILE* LOG=stdout;

std::vector<struct sockaddr_in> addrs;
int rate = 0, duration = 0;
bool verbose = false;

void usage(int e) {
    std::cout << "Usage: ./parent [-a ADDR_1 ADDR_2] [-r rate] [-d duration] [-h] [-v]" << std::endl;
    exit(e);
}

std::vector<std::string> split(const std::string& s, char delimiter) {
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream tokenStream(s);
    
    while (std::getline(tokenStream, token, delimiter)) {
        tokens.push_back(token);
    }

    if (tokens.size() != 2) {
        fprintf(stderr, "EXPECTED ADDR: 'IP:PORT' |  RECEIVED: %s\n", s.c_str());
        exit(EXIT_FAILURE);
    }
    
    return tokens;
}

int parse(int argc, char **argv) {
    int opt = 0, opti = 0;
    int ret = 0;
    while ( (opt = getopt (argc, argv, "ha:r:d:v") ) != -1 ) {
        switch (opt) {
        case 'h':
            usage(EXIT_SUCCESS);
            break;

        case 'v':
            verbose = true;
            break;

        case 'a':
            opti = optind - 1;
            while (optind < argc && argv[opti][0] != '-') {
                auto parts = split(std::string {argv[opti]}, ':');
                std::string ip = parts[0];
                int port = atoi(parts[1].c_str());

                struct sockaddr_in addr;
                addr.sin_family = AF_INET,
                addr.sin_port = htons(port),
                addr.sin_addr.s_addr  = inet_addr(ip == "localhost" ? "127.0.0.1" : ip.c_str());

                addrs.push_back(addr);
                opti++;
            }
            optind = opti - 1;
            break;

        case 'r':
            rate = atoi(optarg);
            break;

        case 'd':
            duration = atoi(optarg);
            break;

        default:
            usage(EXIT_FAILURE);
            break;
        }
    }

    if (addrs.empty()) usage(EXIT_FAILURE);
    if (optind > argc) usage(EXIT_FAILURE);

    return ret;
}

int parent(void) {
    int sockfd;
    int cnt = 0, n, total = addrs.size();
    auto packets = (int64_t)rate * duration;

    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    if (verbose) {
        fprintf(LOG, "PARENT: SOCKET BOUND\n");
        fprintf(LOG, "PARENT: PACKETS=%lu | DURATION=%d | RATE=%d\n", packets, duration, rate);
    }

    auto start  = std::chrono::system_clock::now();
    auto step = std::chrono::duration<double>(1) / rate;

    for (int64_t i = 0; i < packets; i++) {
        MsgUDP_t m = MsgUDP();
        m.id  = (cnt++);
        m.ts  = timestamp();
        for (int j = 0; j<total; j++) {
            n = sendto(sockfd, &m, sizeof(MsgUDP_t), 0, (struct sockaddr *) &addrs[j], sizeof(addrs[j]));
            if ( n < 0 ) {
                fprintf(stderr, "Failed to send\n");
                exit(EXIT_FAILURE);
            } else {
                if (verbose) {
                    fprintf(LOG, "PARENT: SENT[%4lu] => ADDR[%d]\n", i, j);
                }
            }
        }
        std::this_thread::sleep_until(start + (step * i));
    }

    if (verbose) {
        fprintf(LOG, "PARENT: END\n");
    }
    close(sockfd);
    return 0;
}

int main(int argc, char **argv) {
    parse(argc, argv);
    return parent();
}
