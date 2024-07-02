#ifndef __LEMON__HPP
#define __LEMON__HPP

#include <cstdint>
#include <sys/types.h>

typedef struct LemonMsgUDP {
    uint32_t id;
    uint32_t src;
    uint64_t ts;

    LemonMsgUDP() : id(0), src(0), ts(0) {};
} LemonMsgUDP_t;

#endif /* __LEMON__HPP */

