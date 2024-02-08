#ifndef __MAIN__H
#define __MAIN__H

#include <iostream>
#include <vector>
#include <string>

#include "zmq.hpp"

typedef zmq::socket_type    NetworkSocketType;
typedef zmq::send_flags     NetworkSocketSendFlags;
typedef zmq::recv_flags     NetworkSocketRecvFlags;
typedef zmq::message_t      NetworkMessage;

class NetworkSocket {
public:
    typedef enum {
        NONE = 0,
        INFO = 1, 
        WARNING = 2, 
        ERR = 3
    } LOG_LEVEL;

    void connect(void);
    void bind(void);

    int send(NetworkMessage& msg, NetworkSocketSendFlags flags=NetworkSocketSendFlags::none);
    int recv(NetworkMessage& msg, NetworkSocketRecvFlags flags=NetworkSocketRecvFlags::none);

    int setlog(LOG_LEVEL verbosity);
    void log(std::string);

    NetworkSocket(std::string FORMAT, NetworkSocketType TYPE, int CONTEXT=1);
    ~NetworkSocket();

private:
    std::string         format;
    zmq::socket_type    type;
    zmq::context_t      context;
    zmq::socket_t       socket;

    LOG_LEVEL _level;
};

#endif /* __MAIN__H */

