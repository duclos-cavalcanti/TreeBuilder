#include <iostream>
#include <chrono>

#include <cstdio>
#include <cstdlib>
#include <unistd.h>

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <arpa/inet.h>

#include "main.hpp"

static char* IP = NULL;
static char* PORT = NULL;

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
            IP = optarg;
            break;

        case 'p':
            PORT = optarg;
            break;

        default:
            usage(EXIT_FAILURE);
            break;
        }
    }

    if ((!IP) || (!PORT)) usage(EXIT_FAILURE);
    if (optind > argc) usage(EXIT_FAILURE);

    fprintf(stdout, "IP: %s | PORT: %s\n", IP, PORT);
    return ret;
}

int child(void) {
    int sockfd, port, n, len;
    MsgUDP_t* msg;
    int sz = static_cast<int>(sizeof(MsgUDP_t));
    char buf[1000] = { 0 };
    struct sockaddr_in sockaddr = { 0 }, _addr = { 0 };

    sockaddr.sin_family       = AF_INET;
    sockaddr.sin_port         = htons(port = atoi(PORT));
    sockaddr.sin_addr.s_addr  = inet_addr(IP);

    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    if( bind(sockfd, (struct sockaddr*)&sockaddr, sizeof(sockaddr)) < 0) {
        fprintf(stderr, "Failed to bind socket to port: %d\n", port);
        exit(EXIT_FAILURE);
    }

    while(1) {
        if ( (n = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr*)&_addr, (socklen_t *) &len)) < 0 ) {
            fprintf(stderr, "Failed to receive\n");
            exit(EXIT_FAILURE);
        }

        if (n < sz) continue;

        msg = reinterpret_cast<MsgUDP_t*>(buf);
        msg->print();
    }

    close(sockfd);
    return 0;
}


int main(int argc, char **argv) {
    parse(argc, argv);
    child();

	return 0;
}
