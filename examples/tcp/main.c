#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <ctype.h>
#include <signal.h>

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <arpa/inet.h>

#define PORT 8080
#define CLIENT 0
#define SERVER 1

static char*    srv_ip = NULL;
static struct   sockaddr_in srv, cli;
static int      sockfd;

void handler(int sig) {
    puts("Signal Received!");
}

int parse(int argc, char **argv) {
    int opt, ret = 0;
    while ( (opt = getopt (argc, argv, "r:p:h") ) != -1 ) {
        switch (opt) {
        case 'h':
            ret = EXIT_SUCCESS;
            goto exit;
            break;

        case 'r':
            if (strcmp(optarg, "client") == 0) {
                ret = CLIENT;
            } else if (strcmp(optarg, "server") == 0) {
                ret = SERVER;
            } else {
                ret = EXIT_FAILURE;
                goto exit;
            }
            break;

        case 'p':
            srv_ip = optarg;
            break;

        default:
exit:
            fprintf(stderr, "Usage: %s [-r [client,server]] [-p IP_ADDRESS] [-h]\n", argv[0]);
            exit(ret);
            break;
        }
    }

    if (optind > argc) goto exit;
    return ret;
}

int server() {
    int len, n;
    char buf[200] = { 0 }, out[200] = { 0 };

    puts("-- SERVER --");

    if( bind(sockfd, (struct sockaddr*)&srv, sizeof(srv)) < 0) {
        fprintf(stderr, "Failed to bind to port\n");
        exit(EXIT_FAILURE);
    }

    len = sizeof(cli);
    do {
        if ( (n = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr*)&cli, (socklen_t *) &len)) < 0 ) {
            fprintf(stderr, "Failed to receive\n");
            exit(EXIT_FAILURE);
        }

        for (int i=0; i<n; i++)  
            if (buf[i] == '\n')
                buf[i] = '\0';
        buf[n] = '\0';

        printf("RX DATA: %s | IP: %s | PORT: %i | LEN: %d\n", buf, inet_ntoa(cli.sin_addr), ntohs(cli.sin_port), len);
        
        for (int i=0; i<n; i++)  out[i] = toupper(buf[i]);
        
        if ( (sendto(sockfd, out, n, 0, (struct sockaddr*)&cli, sizeof(cli))) < 0 ) {
            fprintf(stderr, "Failed to send\n");
            exit(EXIT_FAILURE);
        }

        puts("TX DATA");
    } while(0);

    puts("-- CLOSED --");
    close(sockfd);
    return 0;
}

int client() {
    int len, n;
    char buf[200] = { 0 }, out[200] = { 0 };
    puts("-- CLIENT --");

    len = sizeof(srv);
    do {
        printf("TX DATA: ");
        fgets(out, sizeof(out), stdin);
        if ( (sendto(sockfd, out, strlen(out), 0, (struct sockaddr*)&srv, sizeof(srv))) < 0 ) {
            fprintf(stderr, "Failed to send\n");
            exit(EXIT_FAILURE);
        }

        if ( (n = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr*)&srv, (socklen_t *) &len)) < 0 ) {
            fprintf(stderr, "Failed to receive\n");
            exit(EXIT_FAILURE);
        }

        printf("RX DATA: %s | IP: %s | PORT: %i | LEN: %d\n", buf, inet_ntoa(srv.sin_addr), ntohs(srv.sin_port), len);
    } while(0);

    puts("-- CLOSED --");
    close(sockfd);
    return 0;
}

int main(int argc, char **argv) {
    int role = parse(argc, argv);

    if (signal(SIGINT, handler) == SIG_ERR) {
        fprintf(stderr, "Failed to register signal handler\n");
        exit(EXIT_FAILURE);
    }

    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }
    memset(&srv, 0, sizeof(srv));
    memset(&cli, 0, sizeof(cli));

    srv.sin_family       = AF_INET;
    srv.sin_port         = htons(PORT);
    srv.sin_addr.s_addr  = inet_addr( (srv_ip) ? srv_ip : "127.0.0.1");

    if (role == CLIENT) client();
    else                server();

	return 0;
}
