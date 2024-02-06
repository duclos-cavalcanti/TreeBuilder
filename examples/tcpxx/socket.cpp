#include "main.h"

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <arpa/inet.h>

NetworkSocket::Socket::~Socket(void) {
    printf("-- ATTEMPT[%d] --\n", this->fd);

    if (this->_verbosity) 
        printf("-- CLOSED[%d] --\n", this->fd);

    ::close(this->fd);
}

NetworkSocket::~NetworkSocket(void) {
    if (this->_sockets.size() > 0)
        for(auto sock_ptr: this->_sockets)
            delete sock_ptr;
    this->_sockets.clear();
}

NetworkSocket::Socket::Socket(void) {

}

NetworkSocket::NetworkSocket(int PORT, const char* IP, int FAMILY, int TYPE, NetworkSocket::LOG_LEVEL VERBOSITY) {
    in_addr_t s_addr;

    if ( (this->_socket.fd = socket(FAMILY, TYPE, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    if (IP) s_addr = inet_addr(IP);
    else    s_addr = INADDR_ANY;
    
    this->_socket.addr.sin_family       = AF_INET;
    this->_socket.addr.sin_port         = htons(PORT);
    this->_socket.addr.sin_addr.s_addr  = s_addr;
    this->_socket.addrlen               = sizeof(this->_socket.addr);
    this->_socket.port                  = PORT;
    this->_socket._verbosity            = VERBOSITY;

    this->_verbosity = VERBOSITY;

    if (this->_verbosity) 
        printf("-- OPENED[%d] --\n", this->_socket.fd);
}

int NetworkSocket::connect(void) {
    // the socket function named 'connect' in <sys/socket.h>
    // clashes with this Class's connect function. The '::' operator 
    // explicitly tell CXX to use the global scope of the following 
    // function. This then causes it to find the correct socket procedur for it.
    int ret = ::connect(this->_socket.fd, 
                       (struct sockaddr *) &this->_socket.addr,
                       this->_socket.addrlen);


    if (ret < 0) {
        fprintf(stderr, "Failed to connect socket\n");
        exit(EXIT_FAILURE);
    }

    if (this->_verbosity) 
        printf("CONNECTED ON SOCKET[%d] -> %s\n", 
                this->_socket.fd,
                inet_ntoa(this->_socket.addr.sin_addr));
    return ret;
}

int NetworkSocket::bind(void) {
    if (::bind(this->_socket.fd, (struct sockaddr *)&(this->_socket.addr), this->_socket.addrlen) < 0) {
        fprintf(stderr, "Failed to bind socket to address = %s:%d\n", inet_ntoa(this->_socket.addr.sin_addr), this->_socket.port);
        exit(EXIT_FAILURE);
    }

    if (this->_verbosity) 
        printf("BOUND TO SOCKET[%d] -> %s\n", this->_socket.fd, inet_ntoa(this->_socket.addr.sin_addr));

    return 0;
}

int NetworkSocket::listen(int backlog) {
    if (::listen(this->_socket.fd, backlog) < 0) {
        fprintf(stderr, "Failed to listen onto socket\n");
        exit(EXIT_FAILURE);
    }

    if (this->_verbosity) 
        printf("LISTENING ON SOCKET[%d]\n", this->_socket.fd);

    return 0;
}

int NetworkSocket::accept(struct sockaddr_in* ret) {
    NetworkSocket::Socket* sock = new NetworkSocket::Socket();
    sock->addrlen =  sizeof(sock->addr);

    if (this->_verbosity) 
        printf("AWAITING CONNECTION ON SOCKET[%d] -> %s\n", 
                this->_socket.fd,
                inet_ntoa(this->_socket.addr.sin_addr));

    if ( (sock->fd = ::accept(this->_socket.fd, (struct sockaddr *)&(sock->addr), &(sock->addrlen))) < 0 ) {
        fprintf(stderr, "Failed to listen onto socket\n");
        exit(EXIT_FAILURE);
    }

    if ( (sock->_verbosity = this->_verbosity) ) 
        printf("ACCEPTED CONNECTION FROM SOCKET[%d] <- %s\n", 
                sock->fd, 
                inet_ntoa(sock->addr.sin_addr));

    this->_sockets.push_back(sock);
    ret = &(sock->addr);
    return sock->fd;
}

int NetworkSocket::load(const char* tx, int len, int sockfd) {
    struct Socket* sock = this->fetch(sockfd);

    if (len >= SOCKET_BUFFER) {
        fprintf(stderr, "Failed to load data into tx buffer\n");
        exit(EXIT_FAILURE);
    }

    for (int i=0; i<len; i++) 
        sock->tx[i] = tx[i];

    sock->txlen = len;
    return 0;
}

NetworkSocket::Socket* NetworkSocket::fetch(int sockfd) {
    struct Socket* ret = NULL;

    // get socket struct associated to the overloaded sock file descriptor
    if (sockfd < 0 || sockfd == this->_socket.fd) {
        ret = &(this->_socket);
    } else {
        for(auto _sock: this->_sockets) {
            if (_sock->fd == sockfd) {
                ret = _sock;    
                break;
            }
        }
    }

    if ( ret == NULL) {
        fprintf(stderr, "Failed to find socket structure from fd: %d\n", sockfd);
        exit(EXIT_FAILURE);
    }

    return ret;
}

int NetworkSocket::send(int sockfd) {
    struct Socket* sock = this->fetch(sockfd);
    if ( (::send(sock->fd, 
                 sock->tx, 
                 sock->txlen, 
                 0)) < 0 ) {
        fprintf(stderr, "Failed to send data through socket\n");
        exit(EXIT_FAILURE);
    }

    if (this->_verbosity) 
        printf("TX DATA[%d]: %s | SIZE: %d -> %s\n", 
                sock->fd, 
                sock->tx, 
                sock->txlen, 
                inet_ntoa(sock->addr.sin_addr));

    return 0;
}

int NetworkSocket::recv(int sockfd) {
    struct Socket* sock = this->fetch(sockfd);
    int ret = 0;

    if ( (ret = ::read(sock->fd, sock->rx, SOCKET_BUFFER)) < 0 ) {
        fprintf(stderr, "Failed to read data from socket\n");
        exit(EXIT_FAILURE);
    }
    sock->rx[ret] = '\0';

    if (this->_verbosity) 
        printf("RX DATA[%d]: %s | SIZE %d <- %s\n", 
                sock->fd,
                sock->rx, 
                ret, 
                inet_ntoa(sock->addr.sin_addr));

    return ret;
}

int NetworkSocket::offload(char* rx, int len, int sockfd) {
    struct Socket* sock = this->fetch(sockfd);
    if (len >= SOCKET_BUFFER) {
        fprintf(stderr, "Failed to recv data into rx buffer\n");
        exit(EXIT_FAILURE);
    }

    for (int i=0; i<len; i++) 
        rx[i] = sock->rx[i];
    rx[len] = '\0';

    return 0;
}

int NetworkSocket::setlog(NetworkSocket::LOG_LEVEL verbosity) {
    return (this->_verbosity = verbosity);
}

int NetworkSocket::setname(const char* name) {
    this->name = std::string (name);
    return 0;
}
