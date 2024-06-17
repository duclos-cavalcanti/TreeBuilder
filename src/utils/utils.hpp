#ifndef __UTILS__HPP
#define __UTILS__HPP

#include <string>
#include <vector>

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <arpa/inet.h>
#include <unistd.h>

struct sockaddr_in socketaddr(std::string ip, int port);
struct timeval timeout(int dur_sec);
std::vector<std::string> split(const std::string& s, char delimiter);

#endif /* __UTILS__HPP */
