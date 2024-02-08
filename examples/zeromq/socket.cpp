#include "main.h"
#include "zmq.hpp"

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

NetworkSocket::~NetworkSocket(void) {

}

NetworkSocket::NetworkSocket(const char* FORMAT, int TYPE=ZMQ_REP) : _level(NetworkSocket::LOG_LEVEL::INFO) {

}

int NetworkSocket::connect(void) {

    return 0;
}

int NetworkSocket::bind(void) {

    return 0;
}

int NetworkSocket::send(char* tx, int txlen, int sockfd) {

    return 0;
}

int NetworkSocket::recv(char* rx, int rxlen, int sockfd) {
    int n = 0;

    return n;
}

int NetworkSocket::setlog(NetworkSocket::LOG_LEVEL level) {
    return (this->_level = level);
}
