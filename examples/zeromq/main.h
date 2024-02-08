#ifndef __MAIN__H
#define __MAIN__H

#include <vector>

#include <string>
#include <sys/socket.h>
#include <netinet/in.h>

class NetworkSocket {
public:
    typedef enum {
        NONE = 0,
        INFO = 1, 
        WARNING = 2, 
        ERR = 3
    } LOG_LEVEL;

    struct Socket {
        int fd;
        int port;
        sockaddr_in addr;
        socklen_t addrlen;

        Socket(void);
        ~Socket(void);
    };

    int connect(void);
    int bind(void);
    int listen(int backlog=5);
    int accept(struct sockaddr_in* ret);

    int send(char* tx, int txlen, int sockfd=-1);
    int recv(char* rx, int rxlen, int sockfd=-1);

    int setlog(LOG_LEVEL verbosity);

    NetworkSocket(int PORT, 
                  const char* IP, 
                  int FAMILY=AF_INET, 
                  int TYPE=SOCK_STREAM, 
                  NetworkSocket::LOG_LEVEL VERBOSITY=NetworkSocket::LOG_LEVEL::INFO);
    ~NetworkSocket();
private:
    LOG_LEVEL _verbosity;

    Socket _socket;
    std::vector<Socket*> _sockets;

    Socket* fetch(int sockfd);
};

#endif /* __MAIN__H */

