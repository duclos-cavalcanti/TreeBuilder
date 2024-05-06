#include "common.hpp"

#include <cstdlib>

int send_udp(MsgUDP_t* m, int sockfd, struct sockaddr_in* addr, size_t addr_sz) {
    int n = sendto(sockfd, m, sizeof(MsgUDP_t), 0, (struct sockaddr *)addr, addr_sz);
    if ( n < 0 ) {
        fprintf(stderr, "Failed to send\n");
        exit(EXIT_FAILURE);
    } else {
        fprintf(stdout, "SENT=%d\n", n);
    }
    return n;
}

int recv_udp(int sockfd, char* buf, size_t buf_sz, struct sockaddr_in* addr) {
    int n, len;
    if ( (n = recvfrom(sockfd, buf, buf_sz, 0, (struct sockaddr*) addr, (socklen_t *) &len)) < 0 ) {
        fprintf(stderr, "Failed to receive[%d]\n", n);
        exit(EXIT_FAILURE);
    } else {
        fprintf(stdout, "RECV=%d\n", n);
    }

    return n;
}
