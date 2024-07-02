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

    void print(void) {
        fprintf(stdout, "MSGUDP: { ");
        fprintf(stdout, "ID=%d, ",       this->id);
        fprintf(stdout, "TS=%lu }",      this->ts);
    }

    char* str(void) {
        static char buf[1000] = { 0 };
        sprintf(buf, "MSGUDP: { ");
        sprintf(buf, "ID=%d, ",  this->id);
        sprintf(buf, "TS=%lu }", this->ts);

        return buf;
    }

    MsgUDP() : id(0), ts(0) {};
} MsgUDP_t;

int64_t timestamp(void);
int64_t deadline(float dur_sec);
double  get_percentile(const std::vector<int64_t>& data, double percentile);
double  get_variance(const std::vector<int64_t>& data);
double  get_stdev(const std::vector<int64_t>& data);
int     write_csv(const std::vector<int64_t>& data, std::string name);

#endif /* __COMMON__HPP */
