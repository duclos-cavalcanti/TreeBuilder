#ifndef __COMMON__HPP
#define __COMMON__HPP

#include <cstdint>
#include <cstdio>

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <arpa/inet.h>

typedef enum MsgType {
    START = 0,
    ONGOING = 1,
    END = 2
} MsgType_t;

typedef struct MsgUDP {
    uint32_t id;
    uint64_t ts;
    MsgType_t type;
    uint64_t dur;
    uint64_t rate;

    void print() {
        fprintf(stdout, "MsgUDP[%d] {\n", this->id);
        fprintf(stdout, "\tID=%d\n",      this->id);
        fprintf(stdout, "\tTS=%lu\n",     this->ts);
        fprintf(stdout, "\tTYPE=%d\n",    this->type);
        fprintf(stdout, "\tDUR=%lu\n",    this->dur);
        fprintf(stdout, "\tRATE=%lu\n}\n",  this->rate);
    }

    MsgUDP() : id(0), ts(0), type(START), dur(0), rate(0) {};
} MsgUDP_t;

int send_udp(MsgUDP_t* m, int sockfd, struct sockaddr_in* addr, size_t addr_sz);
int recv_udp(int sockfd, char* buf, size_t buf_sz, struct sockaddr_in* addr);

#endif /* __COMMON__HPP */
