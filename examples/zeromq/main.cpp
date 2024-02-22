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

int parse(int argc, char **argv) {
    int opt, ret = 0;
    while ( (opt = getopt (argc, argv, "r:h") ) != -1 ) {
        switch (opt) {
        case 'h':
            fprintf(stdout, "Usage: %s [-r [client,server]] [-h]\n", argv[0]);
            exit(EXIT_SUCCESS);
            break;

        case 'r':
            if (strcmp(optarg, "client") == 0) {
                ret = CLIENT;
            } else if (strcmp(optarg, "proxy") == 0) {
                ret = PROXY;
            } else if (strcmp(optarg, "receiver") == 0) {
                ret = RECEIVER;
            } else {
                goto err;
            }
            break;

        default:
err:
            fprintf(stderr, "Usage: %s [-r [client,server]] [-h]\n", argv[0]);
            exit(EXIT_FAILURE);
            break;
        }
    }

    if (optind > argc) {
        fprintf(stderr, "Usage: %s [-r [client,server]] [-p IP_ADDRESS] [-h]\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    return ret;
}

int client() {
    printf("Server\n");
    {
        std::string PROTOCOL{"tcp"};
        std::string IP{"localhost"};
        std::string PORT{"8081"};
        ZMQSocket Client(PROTOCOL, IP, PORT, zmq::socket_type::client, "CLIENT");

        Client.send(zmq::message_t{std::string("CLIENT REQ")});
    }

    return 0;
}

int proxy() {
    printf("Proxy\n");
    {
        std::string PROTOCOL{"tcp"};
        std::string IP{"localhost"};
        std::string PORT{"8081"};

        ZMQSocket Proxy(PROTOCOL, IP, PORT, zmq::socket_type::router, "PROXY");
        Proxy.bind();

        uint32_t client_id = 0;

        while(1) {
            auto msg = Proxy.recv();
            auto id = msg.routing_id();

            if (msg.str() == "CLIENT REQ") {
                Proxy.log({"RECV: CLIENT REQ"});
                client_id = id;
            }
        }

    }
    return 0;
}


int receiver() {
    printf("Receiver\n");
    {
        std::string PROTOCOL{"tcp"};
        std::string IP{"localhost"};
        std::string PORT{"8081"};
        ZMQSocket Receiver(PROTOCOL, IP, PORT, zmq::socket_type::client, "RECEIVER");
        Receiver.connect();

        int n = 10;
        while(n) {
            Receiver.send(zmq::message_t{std::string("CLIENT REQ")});
            n--;
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }

    }
    return 0;
}

int main(int argc, char **argv) {

    int role = parse(argc, argv);

    if (role == CLIENT)        client();
    else if (role == PROXY)    proxy();
    else                       receiver();

	return 0;
}
