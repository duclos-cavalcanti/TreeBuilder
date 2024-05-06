#include <iostream>
#include <vector>
#include <chrono>
#include <thread>
#include <sstream>

#include <cstdio>
#include <cstdlib>
#include <unistd.h>

#include "common.hpp"

std::vector<struct sockaddr_in> addrs;
int rate = 0, duration = 0;

void usage(int e) {
    std::cout << "Usage: ./parent [-a ADDR_1 ADDR_2] [-r rate] [-d duration] [-h]" << std::endl;
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
    } else {
        fprintf(stdout, "IP=%s;PORT=%s\n", tokens[0].c_str(), tokens[1].c_str());
    }
    
    return tokens;
}

int parse(int argc, char **argv) {
    int opt = 0, opti = 0, i = 0;
    int ret = 0;
    while ( (opt = getopt (argc, argv, "ha:r:d:") ) != -1 ) {
        switch (opt) {
        case 'h':
            usage(EXIT_SUCCESS);
            break;

        case 'a':
            opti = optind - 1;
            while (optind < argc && argv[opti][0] != '-') {
                fprintf(stdout, "ADDR[%d]: ", i++);

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
            fprintf(stdout, "RATE=%d\n", rate);
            break;

        case 'd':
            duration = atoi(optarg);
            fprintf(stdout, "DURATION=%d\n", duration);
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
    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }
    fprintf(stdout, "SOCKET BOUND\n");

    int cnt = 0, n, lim = addrs.size();
    auto total = (int64_t)rate * duration;
    auto now  = std::chrono::system_clock::now();
    auto step = std::chrono::duration<double>(1) / rate;

    fprintf(stdout, "PARENT: PACKETS=%lu | DURATION=%d | RATE=%d\n", total, duration, rate);

    MsgUDP_t m = MsgUDP();
    m.type = MsgType_t::START;

    for (int j = 0; j<lim; j++) {
        fprintf(stdout, "PARENT: STREAM START[%d] => IP=%s | PORT=%d \n", j, inet_ntoa(addrs[j].sin_addr), ntohs(addrs[j].sin_port));
        n = send_udp(&m, sockfd, &addrs[j], sizeof(addrs[j]));
    }

    for (int64_t i = 0; i < total; i++) {
        MsgUDP_t m = MsgUDP();
        m.id = (cnt++);
        if (i == (total - 1)) m.type = MsgType_t::END;
        else                  m.type = MsgType_t::ONGOING;

        for (int j = 0; j<lim; j++) {
            n = send_udp(&m, sockfd, &addrs[j], sizeof(addrs[j]));
        }

        std::this_thread::sleep_until(now + (step * i));
    }

    fprintf(stdout, "PARENT: STREAM END\n");
    close(sockfd);
    return 0;

}

int main(int argc, char **argv) {
    parse(argc, argv);
    parent();

	return 0;
}
