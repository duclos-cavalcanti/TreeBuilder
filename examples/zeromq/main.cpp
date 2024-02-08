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
    int n;
    char rx[BUFFER_SIZE] = { 0 }, tx[BUFFER_SIZE] = { 0 };
    printf("######## RESPONDER ########\n");
    {
        do {
            for (int i=0; i<n; i++)   {
                if (rx[i] == '\n')
                    rx[i] = '\0';
            }
            rx[n] = '\0';
            
            for (int i=0; i<n; i++)   {
                tx[i] = toupper(rx[i]);
            }
            tx[n] = '\0';
        } while(0);
    }

    return 0;
}

int client() {
    char rx[BUFFER_SIZE] = { 0 }, tx[BUFFER_SIZE] = { 0 };
    printf("######## REQUESTER ########\n");
    {
        do {
            printf("ENTER: ");
            fgets(tx, sizeof(tx), stdin); tx[strlen(tx) - 1] = '\0';
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
