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

std::vector<int64_t> diffs;
std::string ip = "";
int port = 0, rate, duration;
int64_t packets;

void usage(int e) {
    std::cout << "Usage: ./child [-i IP_ADDR] [-p PORT] [-h]" << std::endl;
    exit(e);
}

int parse(int argc, char **argv) {
    int opt = 0;
    int ret = 0;
    while ( (opt = getopt (argc, argv, "hi:p:") ) != -1 ) {
        switch (opt) {
        case 'h':
            usage(EXIT_SUCCESS);
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

int child(void) {
    int sockfd, n, len, cnt = 0;
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

    fprintf(LOG, "CHILD: SOCKET BOUND => IP=%s | PORT=%d\n", ip.c_str(), port);
    fprintf(LOG, "CHILD: WAITING ON START...\n");

    while(1) {
        n = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr*) &senderaddr, (socklen_t *) &len);
        if (n < (int) sizeof(MsgUDP_t)) {
            continue;
        }

        msg = reinterpret_cast<MsgUDP_t*>(buf);

        if (msg->type == MsgType_t::START) { 
            rate = msg->rate;
            duration = msg->dur;
            packets = (int64_t)rate * duration;
            fprintf(LOG, "CHILD: START => IP=%s | PORT=%i | PACKETS=%lu | RATE=%d | DURATION=%d\n", inet_ntoa(senderaddr.sin_addr), ntohs(senderaddr.sin_port), packets, rate, duration);
            break;
        } else {
            fprintf(stderr, "Failed to start stream\n");
            exit(EXIT_FAILURE);
        }
    }

    while(1) {
        n = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr*) &senderaddr, (socklen_t *) &len);
        if (n < (int) sizeof(MsgUDP_t)) {
            continue;
        }

        msg = reinterpret_cast<MsgUDP_t*>(buf);
        diffs.push_back(timestamp() - msg->ts);

        fprintf(LOG, "CHILD: RECV[%4d] => %s | ", cnt++,  msg->type_to_string(msg->type).c_str());
        msg->print();

        if (msg->type == MsgType_t::END) {
            fprintf(LOG, "CHILD: END\n");
            fprintf(LOG, "SUMMARY | RECV=%d | TOTAL=%lu | DROPPED=%lu | DIFF_VECTOR=%lu\n", cnt, packets, packets - cnt, diffs.size());
            for(const auto& d: diffs) {
                fprintf(LOG, "DIFF: \t%6luMS\n", d);
            }
            break;
        }
    }

    close(sockfd);
    return 0;
}


int main(int argc, char **argv) {
    parse(argc, argv);
    child();

	return 0;
}
