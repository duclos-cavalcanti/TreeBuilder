#include <stdio.h>
#include <stdlib.h>

#include <chrono>
#include <thread>
#include <string.h>
#include <unistd.h>

#include "ZMQSocket.hpp"

#define CLIENT      0
#define PROXY       1
#define RECEIVER    2

#define CLIENT_PORT 8081
#define PROXY_PORT  8082
#define RECV_PORT   8083

struct State {
    int role;
    int n;
};

static State state = { 0 };

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

        case 'n':
            state.n = std::stoi(optarg);
            break;

        case 'r':
            if (std::string{optarg} == "client") {
                state.role = CLIENT;
            } else if (std::string{optarg} == "proxy") {
                state.role = PROXY;
            } else if (std::string{optarg} == "receiver") {
                state.role = RECEIVER;
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

int client() {
    std::string PROTOCOL{"tcp"};
    std::string IP{"localhost"};
    std::string PORT{std::to_string(CLIENT_PORT)};

    ZMQSocket Client(PROTOCOL, IP, PORT, zmq::socket_type::client, "CLIENT");

    return 0;
}

int proxy() {
    std::string PROTOCOL{"tcp"};
    std::string IP{"localhost"};
    std::string PORT{"8081"};

    ZMQSocket Proxy(PROTOCOL, IP, PORT, zmq::socket_type::server, "PROXY");
    Proxy.bind();

    uint32_t client_id = 0;
    uint32_t receiver_id = 0;

    while(1) {
       auto msg = Proxy.recv();
       auto id = msg.routing_id();

       if (msg.str() == "CLIENT REQ") {
           Proxy.log({"RECV: CLIENT REQ"});
           client_id = id;
       }
    }

    return 0;
}


int receiver() {
    std::string PROTOCOL{"tcp"};
    std::string IP{"localhost"};
    std::string PORT{"8081"};

    ZMQSocket Receiver(PROTOCOL, IP, PORT, zmq::socket_type::client, "RECEIVER");
    Receiver.connect();

    return 0;
}

int main(int argc, char **argv) {

    parse(argc, argv);

    if (state.role == CLIENT)       client();
    else if (state.role == PROXY)   proxy();
    else                            receiver();

	return 0;
}
