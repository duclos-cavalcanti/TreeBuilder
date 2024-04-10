#include <stdio.h>
#include <stdlib.h>

#include <chrono>
#include <thread>
#include <string.h>
#include <unistd.h>

#include "ZMQSocket.hpp"

#define REQUEST_PORT    8083
#define REPLY_PORT      8081

void usage(const char* str, int e) {
    fprintf(stdout, "%s\n", str);
    exit(e);
}

void parse(int argc, char **argv) {
    int opt = 0;
    char usage_str[100] = { 0 };

    sprintf(usage_str, "Usage: %s [-r [client,server]] [-h]", argv[0]);

    while ( (opt = getopt (argc, argv, "r:n:h") ) != -1 ) {
        switch (opt) {
        case 'h':
            usage(usage_str, EXIT_SUCCESS);
            break;

        case 'r':
            if (std::string{optarg} == "client") {
                
            } else if (std::string{optarg} == "proxy") {

            } else {
                usage(usage_str, EXIT_FAILURE);
            }
            break;

        default:
            usage(usage_str, EXIT_FAILURE);
            break;
        }
    }

    if (optind > argc) {
        usage(usage_str, EXIT_FAILURE);
    }
}

int sender() {
    std::string PROTOCOL{"udp"};
    std::string IP{"localhost"};
    std::string PORT{std::to_string(REQUEST_PORT)};

    ZMQSocket Client(PROTOCOL, IP, PORT, zmq::socket_type::req, "SENDER");

    return 0;
}

int receiver() {
    std::string PROTOCOL{"udp"};
    std::string IP{"localhost"};
    std::string PORT{"8081"};

    ZMQSocket Receiver(PROTOCOL, IP, PORT, zmq::socket_type::rep, "RECEIVER");
    Receiver.connect();

    return 0;
}

int main(int argc, char **argv) {
    parse(argc, argv);

	return 0;
}
