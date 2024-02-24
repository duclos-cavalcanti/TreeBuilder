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

    void monitor(std::string addr, int events);

    int send(zmq::message_t& msg, zmq::send_flags flags=zmq::send_flags::none);
    int recv(zmq::message_t& msg, zmq::recv_flags flags=zmq::recv_flags::none);
    
    zmq::message_t recv(zmq::recv_flags flags=zmq::recv_flags::none);

    int send_message_to(ManagementMsg msg, int routing_id);
    int send_message(ManagementMsg msg, int message_type);
    int send_message(ManagementMsg msg);
    int recv_message(ManagementMsg& msg);
    int recv_message_from(ManagementMsg& msg, int& id);
    ManagementMsg recv_message(void);

    void set_log(LOG_LEVEL verbosity);
    void set_name(std::string name);

    void log(const std::initializer_list<std::string>& strings);
    void log_term(const std::initializer_list<std::string>& strings, COLOR color=COLOR::CLEAR);
    void log_err(const std::initializer_list<std::string>& strings, const zmq::error_t& e);

    std::string get_ip(void);
    std::string get_port(void);
    std::string get_format(void);

private:
    std::string         ip;
    std::string         port;
    std::string         format;

    zmq::context_t      context;
    zmq::socket_type    type;

    const std::string red{"\033[31m"};
    const std::string green{"\033[32m"};
    const std::string clear{"\033[0m"};

    LOG_LEVEL           _level;
    std::string         _name;
};

#endif /* __ZMQSOCKET__HPP */

