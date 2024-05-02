#include <iostream>
#include <vector>
#include <chrono>
#include <thread>
#include <sstream>

#include <cstdio>
#include <cstdlib>
#include <unistd.h>

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <arpa/inet.h>

#include "main.hpp"

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
        fprintf(stderr, "Expected addr of form 'ip:port'\n");
        exit(EXIT_FAILURE);
    } else {
        fprintf(stderr, "IP=%s |  PORT=%s\n", tokens[0].c_str(), tokens[1].c_str());
    }
    
    return tokens;
}

int generate(std::vector<std::string>& str_addrs) {
    std::string ip; 
    int port;
    for (const auto& s : str_addrs) {
        auto parts = split(s, ':');
        ip = parts[0];
        port = atoi(parts[1].c_str());

        struct sockaddr_in addr;
        addr.sin_family = AF_INET,
        addr.sin_port = htons(port),
        addr.sin_addr.s_addr  = inet_addr(ip.c_str());

        addrs.push_back(addr);
    }


    return 0;
}

int parse(int argc, char **argv) {
    std::vector<std::string> addrs;
    int opt = 0;
    int ret = 0;
    while ( (opt = getopt (argc, argv, "ha:r:d:") ) != -1 ) {
        switch (opt) {
        case 'h':
            usage(EXIT_SUCCESS);
            break;

        case 'a':
            while (optind < argc && argv[optind][0] != '-') {
                addrs.push_back(argv[optind]);
                optind++;
            }
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

    generate(addrs);

    return ret;
}

int parent(void) {
    std::vector<struct sockaddr_in> sockaddrs;
    int sockfd;
    int sz = static_cast<int>(sizeof(MsgUDP_t));

    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    int cnt = 0, n;
    auto total = (int64_t)rate * duration;
    auto now  = std::chrono::system_clock::now();
    auto step = std::chrono::duration<double>(1) / rate;

    for (int64_t i = 0; i < total; i++) {
        MsgUDP_t* msg = { 0 };
        msg->id = (cnt++);
        for (auto& addr : addrs) {
            n = sendto(sockfd, msg, sz, 0, (struct sockaddr *)&addr, sizeof(addr));
            if ( n < 0 ) {
                fprintf(stderr, "Failed to send\n");
                exit(EXIT_FAILURE);
            }
        }

        std::this_thread::sleep_until(now + (step * i));
    }

    close(sockfd);
    return 0;

}

int main(int argc, char **argv) {
    parse(argc, argv);

	return 0;
}
