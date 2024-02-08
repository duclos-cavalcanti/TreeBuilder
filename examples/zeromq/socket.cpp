#include "main.h"

#include <stdexcept>
#include <iostream>

int NetworkSocket::setlog(NetworkSocket::LOG_LEVEL level) {
    return (this->_level = level);
}

void NetworkSocket::log(std::string str) {
    if (this->_level == NetworkSocket::LOG_LEVEL::NONE)
        return;

    std::cout << "LOG: " << str << std::endl;
}

void NetworkSocket::connect(void) {
    if(this->type != zmq::socket_type::req) {
        throw(std::runtime_error("Failed to bind socket with type other than 'zmq::socket_type::rep'"));
    }

    this->socket.connect(this->format);
    this->log("SOCKET CONNECTED");
}

void NetworkSocket::bind(void) {
    if(this->type != zmq::socket_type::rep) {
        throw(std::runtime_error("Failed to bind socket with type other than 'zmq::socket_type::rep'"));
    }

    this->socket.bind(this->format);
    this->log("SOCKET BOUND");
}

int NetworkSocket::send(NetworkMessage& msg, zmq::send_flags flags) {
    auto res = this->socket.send(msg, flags);
    if (res.has_value()) {
        this->log("SOCKET SENT DATA");
        return res.value();
    }

    throw(std::runtime_error("Failed to send data"));
}

int NetworkSocket::recv(NetworkMessage& msg, NetworkSocketRecvFlags flags) {
    auto res = this->socket.recv(msg, flags);
    if (res.has_value()) {
        this->log("SOCKET RECEIVED");
        return res.value();
    }

    throw(std::runtime_error("Failed to recv data"));
}

NetworkSocket::~NetworkSocket(void) {

}

NetworkSocket::NetworkSocket(std::string FORMAT, NetworkSocketType TYPE, int CONTEXT) : _level(NetworkSocket::LOG_LEVEL::INFO) {
    this->context = zmq::context_t{CONTEXT};
    this->socket  = zmq::socket_t{this->context, (this->type = TYPE)};
    this->format  = std::string{FORMAT};

    this->log("SOCKET CREATED");
}

