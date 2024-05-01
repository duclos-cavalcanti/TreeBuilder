#ifndef __ZMQSOCKET__HPP
#define __ZMQSOCKET__HPP

#include <iostream>
#include <vector>
#include <string>

#include <zmq.hpp>
#include "message.pb.h"

class ZMQSocket {
public:
    ZMQSocket(std::string PROTOCOL,
              std::string IP,
              std::string PORT,
              zmq::socket_type TYPE, 
              std::string NAME, 
              int CONTEXT=1);
    ~ZMQSocket();

    typedef enum {
        RED = 0,
        GREEN = 1, 
        CLEAR = 2
    } COLOR;

    typedef enum {
        NONE = 0,
        INFO = 1, 
        WARNING = 2, 
        ERR = 3
    } LOG_LEVEL;

    zmq::socket_t       socket;
    zmq::socket_t       _monitor;

    void connect(void);
    void connect(std::string PROTOCOL, std::string IP, std::string PORT);
    void bind(void);
    void join(std::string);

    int send(zmq::message_t& msg, zmq::send_flags flags=zmq::send_flags::none);

    int recv(zmq::message_t& msg, zmq::recv_flags flags=zmq::recv_flags::none);
    zmq::message_t recv(zmq::recv_flags flags=zmq::recv_flags::none);

    void set_log(LOG_LEVEL verbosity);
    void set_name(std::string name);

    void log(const std::initializer_list<std::string>& strings);
    void log_err(const std::initializer_list<std::string>& strings, const zmq::error_t& e);

    std::string get_ip(void);
    std::string get_port(void);
    std::string get_format(void);

private:
    std::string         ip;
    std::string         port;
    std::string         prot;
    std::string         format;

    zmq::context_t      context;
    zmq::socket_type    type;

    LOG_LEVEL           _level;
    std::string         _name;
};

#endif /* __ZMQSOCKET__HPP */

