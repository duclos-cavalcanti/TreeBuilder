#include "common.hpp"

#include <cstdlib>

int send_udp(MsgUDP_t* m, int sockfd, struct sockaddr_in* addr, size_t addr_sz) {
    int n = sendto(sockfd, m, sizeof(MsgUDP_t), 0, (struct sockaddr *)addr, addr_sz);
    if ( n > 0 ) {
        fprintf(stdout, "SENT=%d\n", n);
    }
    return n;
}

int recv_udp(int sockfd, char* buf, size_t buf_sz, struct sockaddr_in* addr) {
    int len, n = recvfrom(sockfd, buf, buf_sz, 0, (struct sockaddr*) addr, (socklen_t *) &len);
    if ( n > 0 ) {
        fprintf(stdout, "RECV=%d\n", n);
    }

    return n;
}
