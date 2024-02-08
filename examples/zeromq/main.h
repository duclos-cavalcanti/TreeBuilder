#ifndef __MAIN__H
#define __MAIN__H

#include <vector>
#include <string>
#include "zmq.hpp"

class NetworkSocket {
public:
    typedef enum {
        NONE = 0,
        INFO = 1, 
        WARNING = 2, 
        ERR = 3
    } LOG_LEVEL;

    int connect(void);
    int bind(void);
    int accept(void);

    int send(char* tx, int txlen, int sockfd=-1);
    int recv(char* rx, int rxlen, int sockfd=-1);

    int setlog(LOG_LEVEL verbosity);

    NetworkSocket(const char* FORMAT, int TYPE);
    ~NetworkSocket();

private:
    zmq::context_t context;

    LOG_LEVEL _level;
};

#endif /* __MAIN__H */

