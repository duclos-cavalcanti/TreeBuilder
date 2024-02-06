#include <stdio.h>
#include <stdlib.h>

// strings
#include <string.h>

// getopt
#include <unistd.h>

#include "main.h"

#define PORT 8081
#define CLIENT 0
#define SERVER 1
#define BUFFER_SIZE 200

static char* IP = NULL;

int parse(int argc, char **argv) {
    int opt, ret = 0;
    while ( (opt = getopt (argc, argv, "r:p:h") ) != -1 ) {
        switch (opt) {
        case 'h':
            fprintf(stderr, "Usage: %s [-r [client,server]] [-p IP_ADDRESS] [-h]\n", argv[0]);
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

        case 'p':
            IP = optarg;
            break;

        default:
err:
            fprintf(stderr, "Usage: %s [-r [client,server]] [-p IP_ADDRESS] [-h]\n", argv[0]);
            exit(EXIT_SUCCESS);
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
    char rx[BUFFER_SIZE] = { 0 }, tx[BUFFER_SIZE] = { 0 };
    printf("######## SERVER ########\n");
    {
        NetworkSocket Server(PORT, NULL, AF_INET, SOCK_STREAM);
        Server.bind();
        Server.listen();
        do {
            struct sockaddr_in addr;
            int clientfd = Server.accept(&addr);
            int n = Server.recv(clientfd);
            Server.offload(rx, n, clientfd);

            for (int i=0; i<n; i++)   {
                if (rx[i] == '\n')
                    rx[i] = '\0';
            }
            rx[n] = '\0';
            
            for (int i=0; i<n; i++)   {
                tx[i] = toupper(rx[i]);
            }
            tx[n] = '\0';
            
            Server.load(tx, strlen(tx), clientfd);
            Server.send(clientfd);

        } while(0);
    }

    return 0;
}

int client() {
    char rx[BUFFER_SIZE] = { 0 }, tx[BUFFER_SIZE] = { 0 };
    printf("######## CLIENT ########\n");
    {
        NetworkSocket Client(PORT, (IP) ? IP : "127.0.0.1", AF_INET, SOCK_STREAM);
        Client.connect();

        do {
            printf("ENTER: ");
            fgets(tx, sizeof(tx), stdin); tx[strlen(tx) - 1] = '\0';

            Client.load(tx, strlen(tx));
            Client.send();
            int n = Client.recv();
            Client.offload(rx, n);

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
