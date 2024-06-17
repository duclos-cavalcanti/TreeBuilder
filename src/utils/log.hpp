#ifndef __LOG__HPP
#define __LOG__HPP

#include <cstdio>
#include <cstdlib>
#include <cstdarg>
#include <unistd.h>

FILE* LOG=stdout;

void log(const char* format, ...) {
    va_list args;
    va_start(args, format);
        vfprintf(LOG, format, args);
    va_end(args);
}


#endif /* __LOG__HPP */
