#include <stdio.h>
#include <stdlib.h>

#include <chrono>
#include <thread>
#include <string.h>
#include <unistd.h>

#include "ZMQSocket.hpp"

#define RECV_PORT    8081

void usage(const char* str, int e) {
    fprintf(stdout, "%s\n", str);
    exit(e);
}

int parse(int argc, char **argv) {
    int opt = 0;
    int ret = 0;
    char usage_str[100] = { 0 };

    sprintf(usage_str, "Usage: %s [-r [client,server]] [-h]", argv[0]);
    while ( (opt = getopt (argc, argv, "r:h") ) != -1 ) {
        switch (opt) {
        case 'h':
            usage(usage_str, EXIT_SUCCESS);
            break;

        case 'r':
            if (std::string{optarg} == "sender") ret = 1;
            else if (std::string{optarg} == "receiver") ret = 2;
            else usage(usage_str, EXIT_FAILURE);
            break;

        default:
            usage(usage_str, EXIT_FAILURE);
            break;
        }
    }

    if (optind > argc) {
        usage(usage_str, EXIT_FAILURE);
    }

    return ret;
}

int sender() {
    ZMQSocket Sender(std::string {"tcp"}, 
                     std::string{"172.18.0.2"}, 
                     std::to_string(RECV_PORT), 
                     zmq::socket_type::req, 
                     "SENDER");
    Sender.connect();
    for (int i = 0; i != 10; i++) {
        zmq::message_t request {std::string{"Hello"}};
        zmq::message_t reply;
        Sender.send(request);
        Sender.recv(reply);
        sleep(1);
    }

    return 0;
}

int receiver() {
    ZMQSocket Receiver(std::string {"tcp"}, 
                       std::string{"0.0.0.0"}, 
                       std::to_string(RECV_PORT), 
                       zmq::socket_type::rep, 
                       "RECEIVER");
    Receiver.bind();

    while(true) {
        zmq::message_t request;
        zmq::message_t reply {std::string{"World"}};
        Receiver.recv(request);
        std::cout << "Received: " << std::string(static_cast<char*>(request.data()), request.size()) << std::endl;
        Receiver.send(reply);
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
        return -2;
    }

	return 0;
}
