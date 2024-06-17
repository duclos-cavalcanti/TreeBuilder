#include "utils.hpp"

#include <sstream>

struct timeval timeout(int dur_sec) {
    struct timeval timeout;
    timeout.tv_sec  = dur_sec;
    timeout.tv_usec = 0;
    return timeout;
}

struct sockaddr_in socketaddr(std::string ip, int port) {
    struct sockaddr_in ret = { 0 };
    ret.sin_family       = AF_INET;
    ret.sin_port         = htons(port);
    ret.sin_addr.s_addr  = inet_addr(ip == "localhost" ? "127.0.0.1" : ip.c_str());

    return ret;
}

std::vector<std::string> split(const std::string& s, char delimiter) {
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream tokenStream(s);
    
    while (std::getline(tokenStream, token, delimiter)) {
        tokens.push_back(token);
    }

    if (tokens.size() != 2) {
        fprintf(stderr, "EXPECTED ADDR: 'IP:PORT' |  RECEIVED: %s\n", s.c_str());
        exit(EXIT_FAILURE);
    }
    
    return tokens;
}

