#include <stdio.h>
#include <stdlib.h>

#include <chrono>
#include <thread>
#include <string.h>
#include <unistd.h>

#include "ZMQSocket.hpp"

#define SEND_ROLE    2
#define RECV_ROLE    2
#define RECV_PORT    8081


void usage(int e) {
    std::cout << "Usage: ./project [-r [client,server]] [-h]" << std::endl;
    exit(e);
}

int parse(int argc, char **argv) {
    int opt = 0;
    int ret = 0;
    while ( (opt = getopt (argc, argv, "r:h") ) != -1 ) {
        switch (opt) {
        case 'h':
            usage(EXIT_SUCCESS);
            break;

        case 'r':
            if (std::string{optarg} == "sender") ret = 1;
            else if (std::string{optarg} == "receiver") ret = 2;
            else usage(EXIT_FAILURE);
            break;

        default:
            usage(EXIT_FAILURE);
            break;
        }
    }

    if (optind > argc) usage(EXIT_FAILURE);
    return ret;
}

int sender() {
    ZMQSocket Sender(std::string {"tcp"}, 
                     std::string{"localhost"}, 
                     std::to_string(RECV_PORT), 
                     zmq::socket_type::push, 
                     "SENDER");
    Sender.connect();
    for (int i = 0; i != 10; i++) {
        zmq::message_t request {std::string{"Hello=" + std::to_string(i)}};
        Sender.send(request);
        sleep(1);
    }

    return 0;
}

int receiver() {
    ZMQSocket Receiver(std::string {"tcp"}, 
                       std::string{"localhost"}, 
                       std::to_string(RECV_PORT), 
                       zmq::socket_type::pull, 
                       "RECEIVER");
    Receiver.bind();

    while(true) {
        zmq::message_t request;
        Receiver.recv(request);
        std::cout << "Received: " << request.to_string() << std::endl;
    }

    return 0;
}

int main(int argc, char **argv) {
    int role = parse(argc, argv);

    if (role == 1) {
        sender();
    } else if (role == 2) { 
        receiver();
    } else {
        std::cout << "Unknown role: " << role << std::endl;
        exit(-2);
    }

	return 0;
}
