#include <stdio.h>
#include <stdlib.h>

#include <iostream>
#include <chrono>
#include <string.h>
#include <unistd.h>

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <arpa/inet.h>

#define PORT    8083

void usage(int e) {
    std::cout << "Usage: ./child [-h]" << std::endl;
    exit(e);
}

int child(void) {
    int sockfd;
    struct sockaddr_in sockaddr;

    memset(&sockaddr, 0, sizeof(sockaddr));

    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    return 0;
}

int parse(int argc, char **argv) {
    int opt = 0;
    int ret = 0;
    while ( (opt = getopt (argc, argv, "h") ) != -1 ) {
        switch (opt) {
        case 'h':
            usage(EXIT_SUCCESS);
            break;

        default:
            usage(EXIT_FAILURE);
            break;
        }
    }

    if (optind > argc) usage(EXIT_FAILURE);
    return ret;
}

int main(int argc, char **argv) {
    parse(argc, argv);
    child();

	return 0;
}
