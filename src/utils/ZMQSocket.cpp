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
    this->prot      = PROTOCOL;
    this->format    = std::string{PROTOCOL + "://" + IP + ":" + PORT};

    this->context   = zmq::context_t{CONTEXT};
    this->socket    = zmq::socket_t{this->context, (this->type = TYPE)};
    this->log({"OPENED"});
}


void ZMQSocket::connect(void) {
    this->log({"ATTEMPT CONNECT IP=", this->ip, " PORT=", this->port, " PROTOCOL=", this->prot});
    this->socket.connect(this->format);
    this->log({"CONNECTED IP=", this->ip, " PORT=", this->port});
}

void ZMQSocket::connect(std::string PROTOCOL, std::string IP, std::string PORT) {
    this->log({"ATTEMPT CONNECT IP=", IP, " PORT=", PORT, " PROTOCOL=", PROTOCOL});
    this->socket.connect(std::string{PROTOCOL + "://" + IP + ":" + PORT});
    this->log({"CONNECTED IP=", IP, " PORT=", PORT});
}

void ZMQSocket::bind(void) {
    this->log({"ATTEMPT BIND IP=", this->ip, " PORT=", this->port, " PROTOCOL=", this->prot});
    this->socket.bind(this->format);
    this->log({"BOUND IP=", this->ip, " PORT=", this->port});
}

void ZMQSocket::join(std::string group) {
    // this->socket.join(group.c_str());
    this->log({"JOINED=", group});
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
