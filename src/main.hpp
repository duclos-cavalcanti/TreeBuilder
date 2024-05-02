#ifndef __MAIN__HPP
#define __MAIN__HPP

#include <cstdint>
#include <cstdio>

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
        fprintf(stdout, "MsgUDP[%d] {", this->id);
        fprintf(stdout, "\tTS=%lu",     this->ts);
        fprintf(stdout, "\tTYPE=%d",    this->type);
        fprintf(stdout, "\tDUR=%lu",    this->dur);
        fprintf(stdout, "\tRATE=%lu\n}",   this->rate);
    }

    MsgUDP() : id(0), ts(0), type(START), dur(0), rate(0) {};
} MsgUDP_t;

#endif /* __MAIN__HPP */
