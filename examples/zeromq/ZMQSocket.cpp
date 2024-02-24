#include "ZMQSocket.hpp"

#include <stdexcept>
#include <iostream>
#include <ostream>

typedef std::initializer_list<std::string> str_list;

static std::string concatenate(const std::initializer_list<std::string>& strings) {
    std::ostringstream stream;
    for (const auto& str:strings)
        stream << str;

    return stream.str();
}

std::string ZMQSocket::get_ip(void) {
    return std::string{this->ip};
}

std::string ZMQSocket::get_port(void) {
    return std::string{this->port};
}

std::string ZMQSocket::get_format(void) {
    return std::string{this->format};
}

void ZMQSocket::set_log(ZMQSocket::LOG_LEVEL level) {
    this->_level = level;
}

void ZMQSocket::set_name(std::string name) {
    this->_name = name;
}

void ZMQSocket::log(const std::initializer_list<std::string>& strings) {
    if (this->_level == ZMQSocket::LOG_LEVEL::NONE)
        return;

    std::string data{concatenate(strings)};
    std::cout << "ZMQLOG::" 
              << this->_name
              << " "
              << data 
              << std::endl;
}

void ZMQSocket::log_term(const std::initializer_list<std::string>& strings, ZMQSocket::COLOR color) {
    if (this->_level == ZMQSocket::LOG_LEVEL::NONE)
        return;

    std::string data{concatenate(strings)};
    std::cout << color
              << "ZMQLOG::" 
              << this->_name
              << " "
              << data 
              << std::endl;
}

void ZMQSocket::log_err(const std::initializer_list<std::string>& strings, const zmq::error_t& e) {
    if (this->_level == ZMQSocket::LOG_LEVEL::NONE) {
        throw(e);
        return;
    }

    std::string data{concatenate(strings)};
    std::cerr << "LOGERR: " << data << std::endl;
    std::cerr << "\tERRNO: " << e.num() << " => " << e.what() << std::endl;
}

ZMQSocket::~ZMQSocket(void) {
    this->log({"CLOSED:  PORT=", this->port, " IP=", this->ip});
}

ZMQSocket::ZMQSocket(std::string PROTOCOL,
                    std::string IP,
                    std::string PORT,
                    zmq::socket_type TYPE, 
                    std::string NAME,
                    int CONTEXT) : 
    _level(ZMQSocket::LOG_LEVEL::INFO), 
    _name(NAME)
{

    this->ip        = IP;
    this->port      = PORT;
    this->format    = std::string{PROTOCOL + "://" + IP + ":" + PORT};

    this->context   = zmq::context_t{CONTEXT};
    this->socket    = zmq::socket_t{this->context, (this->type = TYPE)};
    this->log({"OPENED"});
}


void ZMQSocket::connect(void) {
    this->socket.connect(this->format);
    this->log({"CONNECTED IP=", this->ip, " PORT=", this->port});
}

void ZMQSocket::connect(std::string PROTOCOL, std::string IP, std::string PORT) {
    this->socket.connect(std::string{PROTOCOL + "://" + IP + ":" + PORT});
    this->log({"CONNECTED IP=", IP, " PORT=", PORT});
}

void ZMQSocket::bind(void) {
    this->socket.bind(this->format);
    this->log({"BOUND IP=", this->ip, " PORT=", this->port});
}

void ZMQSocket::monitor(std::string addr, int events) {
    // this->socket.monitor(addr, events);
    this->_monitor = zmq::socket_t (this->context, ZMQ_PAIR);
    // this->_monitor.connect(addr);
}


int ZMQSocket::send(zmq::message_t& msg, zmq::send_flags flags) {
    auto res = this->socket.send(msg, flags);
    if (res.has_value()) {
        this->log({"SENT DATA"});
        return res.value();
    }

    throw(std::runtime_error("Failed to send data"));
}

int ZMQSocket::recv(zmq::message_t& msg, zmq::recv_flags flags) {
    this->log({"RECV WAIT"});
    try {
        auto res = this->socket.recv(msg, flags);
        if (res.has_value()) {
            this->log({"RECV DATA"});
            return res.value();
        } else {
            this->log({"RECV EMPTY DATA"});
            return 0;
        }
    } catch (const zmq::error_t& e) {
        this->log_err({"ERROR ON SOCKET RECV"}, e);
        exit(EXIT_FAILURE);
    }
}

zmq::message_t ZMQSocket::recv(zmq::recv_flags flags) {
    zmq::message_t zmqmsg;
    this->recv(zmqmsg, flags);
    return zmqmsg;
}

int ZMQSocket::send_message(ManagementMsg msg, int message_type) {
    msg.set_msg_type(message_type);
    return this->send_message(msg);
}

int ZMQSocket::send_message(ManagementMsg msg) {
    std::string data;
    msg.SerializeToString(&data);
    zmq::message_t zmqmsg(data);
    this->log({"SENT MESSAGE TYPE: ", std::to_string(msg.msg_type())});
    return this->send(zmqmsg);
}

int ZMQSocket::send_message_to(ManagementMsg msg, int routing_id) {
    std::string data;
    msg.SerializeToString(&data);
    zmq::message_t zmqmsg{data};
    zmqmsg.set_routing_id(routing_id);
    this->log({"SENT MESSAGE TYPE: ", std::to_string(msg.msg_type())});
    return this->send(zmqmsg);
}

int ZMQSocket::recv_message(ManagementMsg& msg) {
    zmq::message_t zmqmsg;
    int n = this->recv(zmqmsg);
    if (n > 0) 
        msg.ParseFromArray((char* )zmqmsg.data(), n);

    this->log({"RECV MESSAGE TYPE: ", std::to_string(msg.msg_type())});
    return n;
}

ManagementMsg ZMQSocket::recv_message(void) {
    ManagementMsg msg;
    zmq::message_t zmqmsg;
    int n = this->recv(zmqmsg);
    if (n > 0) 
        msg.ParseFromArray((char* )zmqmsg.data(), n);

    this->log({"RECV MESSAGE TYPE: ", std::to_string(msg.msg_type())});
    return msg;
}

int ZMQSocket::recv_message_from(ManagementMsg& msg, int& id) {
    zmq::message_t zmqmsg;
    int n = this->recv(zmqmsg);
    id = zmqmsg.routing_id();
    if (n > 0) 
        msg.ParseFromArray((char* )zmqmsg.data(), n);

    this->log({"RECV MESSAGE TYPE: ", std::to_string(msg.msg_type())});
    return n;
}
