#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <ctype.h>
#include <signal.h>
#include <errno.h>

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <arpa/inet.h>

#define PORT 8081
#define CLIENT 0
#define SERVER 1
#define BUFFER_SIZE 200

volatile int RUNNING = 0;

static char*    server_ip = NULL;
static struct   sockaddr_in server_addr, client_addr;

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
            server_ip = optarg;
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
    int server_fd, client_fd, n;
    char rx[BUFFER_SIZE] = { 0 }, tx[BUFFER_SIZE] = { 0 };
    socklen_t client_addrlen = sizeof(client_addr);

    if ( (server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    server_addr.sin_family       = AF_INET;
    server_addr.sin_port         = htons(PORT);
    server_addr.sin_addr.s_addr  = INADDR_ANY;
    printf("-- SERVER: %s:%i --\n", inet_ntoa(server_addr.sin_addr), ntohs(server_addr.sin_port));

    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        fprintf(stderr, "Failed to bind socket to server address\n");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 3) < 0) {
        fprintf(stderr, "Failed to listen onto socket\n");
        exit(EXIT_FAILURE);
    }

    if ((client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &client_addrlen )) < 0) {
        fprintf(stderr, "Failed to accept client connection onto server's socket\n");
        exit(EXIT_FAILURE);
    }
    printf("ACCEPTED: IP: %s\n", inet_ntoa(client_addr.sin_addr));

    do {
        if ( (n = read(client_fd, rx, BUFFER_SIZE)) < 0) {
            fprintf(stderr, "Failed to read\n");
            exit(EXIT_FAILURE);
        }

        for (int i=0; i<n; i++)  
            if (rx[i] == '\n')
                rx[i] = '\0';
        rx[n] = '\0';

        printf("RX DATA[%d]: %s | SRC IP: %s\n", n, rx, inet_ntoa(client_addr.sin_addr));
        for (int i=0; i<n; i++)  
            tx[i] = toupper(rx[i]);
        tx[n] = '\0';
        
        printf("TX DATA[%d]: %s\n", (int) strlen(tx), tx);
        send(client_fd, tx, strlen(tx), 0);
        close(client_fd);
    } while(RUNNING);

    puts("-- CLOSED --");
    close(server_fd);
    return 0;
}

int client() {
    int sockfd, n;
    char rx[BUFFER_SIZE] = { 0 }, tx[BUFFER_SIZE] = { 0 };

    if ( (sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    server_addr.sin_family       = AF_INET;
    server_addr.sin_port         = htons(PORT);
    server_addr.sin_addr.s_addr  = inet_addr( (server_ip) ? server_ip : "127.0.0.1");
    puts("-- CLIENT --");

    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        fprintf(stderr, "TCP Connection Failed\n");
        exit(EXIT_FAILURE);
    }
    printf("CONNECTED: IP: %s\n", inet_ntoa(server_addr.sin_addr));

    do {
        printf("ENTER: ");
        fgets(tx, sizeof(tx), stdin);
        printf("TX DATA[%d]: %s", (int) strlen(tx), tx);

        if ( (send(sockfd, tx, strlen(tx), 0)) < 0 ) {
            fprintf(stderr, "Failed to send\n");
            exit(EXIT_FAILURE);
        }

        if ( (n = read(sockfd, rx, BUFFER_SIZE)) < 0) {
            fprintf(stderr, "Failed to read\n");
            exit(EXIT_FAILURE);
        }
        printf("RX DATA[%d]: %s | SRC IP: %s\n", n, rx, inet_ntoa(server_addr.sin_addr));
    } while(RUNNING);

    puts("-- CLOSED --");
    close(sockfd);
    return 0;
}

void handler(int sig) {
    printf("SIGNAL RECEIVED: %s", strsignal(sig));
    RUNNING = 0;
}

int main(int argc, char **argv) {
    int role = parse(argc, argv);

    if (signal(SIGINT, handler) == SIG_ERR) {
        fprintf(stderr, "Failed to register signal handler\n");
        exit(EXIT_FAILURE);
    }

    if (role == CLIENT) client();
    else                server();

	return 0;
}
