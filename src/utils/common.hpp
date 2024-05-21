#ifndef __COMMON__HPP
#define __COMMON__HPP

#include <string>

#include <cstdint>
#include <cstdio>
#include <vector>

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <arpa/inet.h>
#include <unistd.h>

typedef struct MsgUDP {
    uint32_t id;
    uint64_t ts;
    uint64_t deadline;

    void print(void) {
        fprintf(stdout, "MSGUDP: { ");
        fprintf(stdout, "ID=%d, ",       this->id);
        fprintf(stdout, "TS=%lu }",      this->ts);
    }

    MsgUDP() : id(0), ts(0) {};
} MsgUDP_t;

struct timeval timeout(int dur_ms);
int64_t timestamp(void);
int64_t deadline(float dur_sec);
double  get_percentile(const std::vector<int64_t>& data, double percentile);

#endif /* __COMMON__HPP */
