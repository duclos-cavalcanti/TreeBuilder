#include <stdio.h>
#include <stdlib.h>

// strings
#include <string.h>

// getopt
#include <unistd.h>

#include "main.h"

#define CLIENT 0
#define SERVER 1

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
            } else if (strcmp(optarg, "server") == 0) {
                ret = SERVER;
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

int server() {
    printf("Server\n");
    {
        std::string PROTOCOL{"tcp"};
        std::string IP{"*"};
        std::string PORT{"8081"};
        std::string FORMAT{PROTOCOL + "://" + IP + ":" + PORT};
        // "tcp//*:8081"

        NetworkSocket Server(FORMAT, NetworkSocketType::rep);
        Server.bind();

        do {
            NetworkMessage msg{};
            Server.recv(msg);
            Server.log("SERVER RECV: " + msg.to_string());

            NetworkMessage reply{std::string{msg.to_string() + " ACKED"}};
            Server.send(reply);
        } while(0);
    }

    return 0;
}

int client() {
    printf("Client\n");
    {
        std::string PROTOCOL{"tcp"};
        std::string IP{"localhost"};
        std::string PORT{"8081"};
        std::string FORMAT{PROTOCOL + "://" + IP + ":" + PORT};
        // "tcp//localhost:8081"

        NetworkSocket Client(FORMAT, NetworkSocketType::req);
        Client.connect();

        do {
            NetworkMessage msg{std::string("HELLO")};
            NetworkMessage resp{};

            Client.send(msg);
            Client.recv(resp);
            Client.log("CLIENT RECV: " + resp.to_string());
        } while(0);
    }
    return 0;
}

int main(int argc, char **argv) {
    int role = parse(argc, argv);

    if (role == CLIENT) client();
    else                server();

	return 0;
}
