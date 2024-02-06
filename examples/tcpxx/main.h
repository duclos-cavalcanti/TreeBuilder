#ifndef __MAIN__H
#define __MAIN__H

#include <vector>

#include <string>
#include <sys/socket.h>
#include <netinet/in.h>

#define SOCKET_BUFFER 200

class NetworkSocket {
public:
    typedef enum {
        NONE = 0,
        INFO = 1, 
        WARNING = 2, 
        ERR = 3
    } LOG_LEVEL;

    struct Socket {
        char rx[SOCKET_BUFFER], rxlen;
        char tx[SOCKET_BUFFER], txlen;
        int fd;
        int port;
        sockaddr_in addr;
        socklen_t addrlen;

        NetworkSocket::LOG_LEVEL _verbosity;

        Socket(void);
        ~Socket(void);
    };

    int setlog(LOG_LEVEL verbosity);
    int setname(const char* name);

    int connect(void);
    int bind(void);
    int listen(int backlog=5);
    int accept(struct sockaddr_in* ret);

    int load(const char* tx, int len, int sockfd=-1);
    int offload(char* rx, int len, int sockfd=-1);

    int send(int sockfd=-1);
    int recv(int sockfd=-1);

    NetworkSocket(int PORT, 
                  const char* IP, 
                  int FAMILY=AF_INET, 
                  int TYPE=SOCK_STREAM, 
                  NetworkSocket::LOG_LEVEL VERBOSITY=NetworkSocket::LOG_LEVEL::INFO);
    ~NetworkSocket();
private:
    std::string name;
    LOG_LEVEL _verbosity;

    Socket _socket;
    std::vector<Socket*> _sockets;

    Socket* fetch(int sockfd);
};

#endif /* __MAIN__H */

