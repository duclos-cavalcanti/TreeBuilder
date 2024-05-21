#include <iostream>
#include <chrono>
#include <vector>

#include <cstdio>
#include <cstdlib>
#include <unistd.h>

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <arpa/inet.h>

#include "common.hpp"

FILE* LOG=stdout;

std::vector<int64_t> latencies;
std::string ip = "";

int duration=0, port = 0;

bool verbose = false;

void usage(int e) {
    std::cout << "Usage: ./child [-i IP_ADDR] [-d DUR] [-p PORT] [-h] [-v]" << std::endl;
    exit(e);
}

int parse(int argc, char **argv) {
    int opt = 0;
    int ret = 0;
    while ( (opt = getopt (argc, argv, "hi:p:t:d:v") ) != -1 ) {
        switch (opt) {
        case 'h':
            usage(EXIT_SUCCESS);
            break;

        case 'v':
            verbose = true;
            break;

        case 'i':
            ip =  std::string{optarg};
            break;

        case 'p':
            port = atoi(optarg);
            break;

        case 'd':
            duration = atoi(optarg);
            break;

        default:
            usage(EXIT_FAILURE);
            break;
        }
    }

    if (!duration)             usage(EXIT_FAILURE);
    if ((ip == "") || (!port)) usage(EXIT_FAILURE);
    if (optind > argc)         usage(EXIT_FAILURE);

    return ret;
}

void print_latencies(void) {
    for(const auto& d: latencies) {
        fprintf(LOG, "LATENCY: \t%6luMS\n", d);
    }
}

int child(void) {
    unsigned long cnt = 0;
    int sockfd, n, len;
    double perc;
    int sz = sizeof(MsgUDP_t);
    static char buf[1000] = { 0 };
    struct sockaddr_in sockaddr = { 0 }, senderaddr = { 0 };
    MsgUDP_t* msg;
    uint64_t now;

    auto deadline_ts = deadline(1.2  * duration);
    auto t = timeout(100);

    sockaddr.sin_family       = AF_INET;
    sockaddr.sin_port         = htons(port);
    sockaddr.sin_addr.s_addr  = inet_addr(ip == "localhost" ? "127.0.0.1" : ip.c_str());

    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, (const char*)&t, sizeof(t)) < 0) {
        perror("Failed setsockopt recv timeout");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    if( bind(sockfd, (struct sockaddr*)&sockaddr, sizeof(sockaddr)) < 0) {
        fprintf(stderr, "Failed to bind socket to port: %d\n", port);
        exit(EXIT_FAILURE);
    }

    if (verbose) {
        fprintf(LOG, "CHILD: SOCKET BOUND => IP=%s | PORT=%d\n", ip.c_str(), port);
        fprintf(LOG, "CHILD: WAITING ON START...\n");
    }

    if (verbose) {
        fprintf(LOG, "CHILD: START => \n");
    }

    while(1) {
        n = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr*) &senderaddr, (socklen_t *) &len);
        if (n < sz) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                if (verbose) 
                    fprintf(LOG, "CHILD: SOCKET TIMED OUT\n");

                if (timestamp() >= deadline_ts)
                    break;
            }
            continue;
        }

        msg = reinterpret_cast<MsgUDP_t*>(buf);
        latencies.push_back((now = timestamp()) - msg->ts);

        if (verbose) {
            fprintf(LOG, "CHILD: RECV[%4lu] AT TS=%lu => ", cnt, now);
            msg->print();
            fprintf(LOG, "\n");
        }

        cnt++;
    }

    if (verbose) {
        fprintf(LOG, "CHILD: END\n");
        fprintf(LOG, "SUMMARY | RECV=%lu | LATENCY_VECTOR=%lu\n", cnt, latencies.size());
    }

    close(sockfd);
    if ((perc = get_percentile(latencies, 90)) != 0.0) {
        fprintf(stdout, "%lu\n%lf\n", cnt, perc);
        return EXIT_SUCCESS;
    } else {
        fprintf(stdout, "EMPTY LATENCY VECTOR!\n");
        return EXIT_FAILURE;
    }
}


int main(int argc, char **argv) {
    parse(argc, argv);
    return child();
}
