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
int port = 0;
bool verbose = false;

void usage(int e) {
    std::cout << "Usage: ./child [-i IP_ADDR] [-p PORT] [-h] [-v]" << std::endl;
    exit(e);
}

int parse(int argc, char **argv) {
    int opt = 0;
    int ret = 0;
    while ( (opt = getopt (argc, argv, "hi:p:t:v") ) != -1 ) {
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

        default:
            usage(EXIT_FAILURE);
            break;
        }
    }

    if ((ip == "") || (!port)) usage(EXIT_FAILURE);
    if (optind > argc) usage(EXIT_FAILURE);

    return ret;
}

void print_latencies(void) {
    for(const auto& d: latencies) {
        fprintf(LOG, "LATENCY: \t%6luMS\n", d);
    }
}

int child(void) {
    int sockfd, n, len, cnt = 0;
    double perc;
    size_t sz = sizeof(MsgUDP_t);
    static char buf[1000] = { 0 };
    struct sockaddr_in sockaddr = { 0 }, senderaddr = { 0 };
    MsgUDP_t* msg;

    sockaddr.sin_family       = AF_INET;
    sockaddr.sin_port         = htons(port);
    sockaddr.sin_addr.s_addr  = inet_addr(ip == "localhost" ? "127.0.0.1" : ip.c_str());

    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
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

    if (verbose) fprintf(LOG, "CHILD: START => \n");
    while(1) {
        n = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr*) &senderaddr, (socklen_t *) &len);
        if (n < sz) {
            continue;
        }

        msg = reinterpret_cast<MsgUDP_t*>(buf);
        latencies.push_back(timestamp() - msg->ts);

        if (verbose) {
            fprintf(LOG, "CHILD: RECV[%4d] => %s | ", cnt,  msg->type_to_string(msg->type).c_str());
            msg->print();
        }

        if (msg->type == MsgType_t::END) {
            if (verbose) {
                fprintf(LOG, "CHILD: END\n");
                fprintf(LOG, "SUMMARY | RECV=%d | LATENCY_VECTOR=%lu\n", cnt, latencies.size());
            }
            break;
        }
        cnt++;
    }

    close(sockfd);
    if ((perc = get_percentile(latencies, 90)) != 0.0) {
        fprintf(stdout, "%d\n%lf\n", cnt, perc);
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
