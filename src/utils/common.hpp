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

    std::string type_to_string(MsgType_t t) {
        switch (t) {
            case START:   return "START  ";
            case ONGOING: return "ONGOING";
            case END:     return "END    ";
            default:      return "ERR";
        }
    }

    void print(void) {
        fprintf(stdout, "MSGUDP: { ");
        fprintf(stdout, "ID=%d, ",       this->id);
        fprintf(stdout, "TS=%lu, ",      this->ts);
        fprintf(stdout, "TYPE=%s, ",     this->type_to_string(this->type).c_str());
        fprintf(stdout, "DUR=%lu, ",     this->dur);
        fprintf(stdout, "RATE=%lu }\n",  this->rate);
    }

    MsgUDP() : id(0), ts(0), type(START), dur(0), rate(0) {};
} MsgUDP_t;

int64_t timestamp(void);
double  get_percentile(const std::vector<int64_t>& data, double percentile);

#endif /* __COMMON__HPP */
