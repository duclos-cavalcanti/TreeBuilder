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

#include "common.hpp"

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

    fprintf(stdout, "IP: %s;PORT: %s\n", IP, PORT);
    return ret;
}

int child(void) {
    int sockfd, port, n;
    static char buf[1000] = { 0 };
    struct sockaddr_in sockaddr = { 0 }, parentaddr = { 0 };
    std::string ip { IP };
    MsgUDP_t* msg;

    sockaddr.sin_family       = AF_INET;
    sockaddr.sin_port         = htons(port = atoi(PORT));
    sockaddr.sin_addr.s_addr  = inet_addr(ip == "localhost" ? "127.0.0.1" : ip.c_str());

    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    if( bind(sockfd, (struct sockaddr*)&sockaddr, sizeof(sockaddr)) < 0) {
        fprintf(stderr, "Failed to bind socket to port: %d\n", port);
        exit(EXIT_FAILURE);
    }

    fprintf(stdout, "CHILD: IP=%s | PORT=%d\n", IP, port);
    fprintf(stdout, "CHILD: WAITING ON STREAM START...\n");

    while(1) {
        n = recv_udp(sockfd, buf, sizeof(buf), &parentaddr);
        if (n < sizeof(MsgUDP_t)) continue;

        msg = reinterpret_cast<MsgUDP_t*>(buf);

        if (msg->type == MsgType_t::START) { 
            fprintf(stdout, "CHILD: STREAM START => IP=%s | PORT=%i\n", inet_ntoa(parentaddr.sin_addr), ntohs(parentaddr.sin_port));
        } else if (msg->type == MsgType_t::END) {
            fprintf(stdout, "CHILD: STREAM END\n");
            break;
        }

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
