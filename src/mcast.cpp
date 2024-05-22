#include <iostream>
#include <vector>
#include <chrono>
#include <thread>
#include <sstream>

#include <cstdio>
#include <cstdlib>
#include <cstdarg>
#include <unistd.h>

#include "common.hpp"

FILE* LOG=stdout;

std::vector<struct sockaddr_in> addrs;
std::vector<int64_t> latencies;
std::string ip   = "";
std::string name = "";
int port = 0;
int rate = 0, duration = 0;
bool ROOT    = false;
bool LEAF    = false;
bool verbose = false;

void log(const char* format, ...) {
    if (!verbose) {
        return;
    }

    va_list args;
    va_start(args, format);
        vfprintf(LOG, format, args);
    va_end(args);
}

void usage(int e) {
    std::cout << "Usage: ./mcast [-a ADDR_1 ADDR_2] [-r rate] [-i ip] [-p port] [-d duration] [-R] [-L] [-h] [-v]" << std::endl;
    exit(e);
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

int parse(int argc, char **argv) {
    int opt = 0, opti = 0;
    int ret = 0;
    while ( (opt = getopt (argc, argv, "hn:i:p:a:r:d:vRL") ) != -1 ) {
        switch (opt) {
        case 'h':
            usage(EXIT_SUCCESS);
            break;

        case 'v':
            verbose = true;
            break;

        case 'a':
            opti = optind - 1;
            while (optind < argc && argv[opti][0] != '-') {
                auto parts = split(std::string {argv[opti]}, ':');
                std::string ip = parts[0];
                int port = atoi(parts[1].c_str());

                struct sockaddr_in addr;
                addr.sin_family = AF_INET,
                addr.sin_port = htons(port),
                addr.sin_addr.s_addr  = inet_addr(ip == "localhost" ? "127.0.0.1" : ip.c_str());

                addrs.push_back(addr);
                opti++;
            }
            optind = opti - 1;
            break;

        case 'i':
            ip =  std::string{optarg};
            break;

        case 'p':
            port = atoi(optarg);
            break;

        case 'r':
            rate = atoi(optarg);
            break;

        case 'd':
            duration = atoi(optarg);
            break;

        case 'L':
            LEAF = true;
            break;

        case 'R':
            ROOT = true;
            break;

        case 'n':
            name = std::string{optarg};
            break;

        default:
            usage(EXIT_FAILURE);
            break;
        }
    }


    if (!ROOT && ip == "")               usage(EXIT_FAILURE);
    if (!ROOT && port == 0)              usage(EXIT_FAILURE);
    if (addrs.empty() && !LEAF) usage(EXIT_FAILURE);
    if (optind > argc)          usage(EXIT_FAILURE);
    return ret;
}

int root(void) {
    int sockfd;
    int cnt = 0, n, total = addrs.size();
    auto packets = (int64_t)rate * duration;

    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    log("ROOT::%s: SOCKET OPENED\n", name.c_str());
    log("ROOT::%s: PACKETS=%lu | DURATION=%d | RATE=%d\n", name.c_str(), packets, duration, rate);

    auto start  = std::chrono::system_clock::now();
    auto step = std::chrono::duration<double>(1) / rate;

    for (int64_t i = 0; i < packets; i++) {
        MsgUDP_t m = MsgUDP();
        m.id  = (cnt++);
        m.ts  = timestamp();

        for (int j = 0; j<total; j++) {
            n = sendto(sockfd, &m, sizeof(MsgUDP_t), 0, (struct sockaddr *) &addrs[j], sizeof(addrs[j]));
            if ( n < 0 ) {
                fprintf(stderr, "Failed to send\n");
                exit(EXIT_FAILURE);
            } else {
                log("ROOT::%s: SENT[%4lu] => ADDR[%d] | TS=%lu\n", name.c_str(), i, j, m.ts);
            }
        }
        std::this_thread::sleep_until(start + (step * i));
    }

    log("ROOT::%s: END\n", name.c_str());
    close(sockfd);
    return 0;
}

int proxy(void) {
    int sockfd;
    unsigned long cnt = 0;
    int n, total = addrs.size();
    auto packets = (int64_t)rate * duration;
    int sz = sizeof(MsgUDP_t);
    static char buf[1000] = { 0 };
    struct sockaddr_in sockaddr = { 0 }, senderaddr = { 0 };
    socklen_t len = sizeof(senderaddr);
    MsgUDP_t* msg;

    auto deadline_ts = deadline(1.5  * duration);
    auto t = timeout(1);

    sockaddr.sin_family       = AF_INET;
    sockaddr.sin_port         = htons(port);
    sockaddr.sin_addr.s_addr  = inet_addr(ip == "localhost" ? "127.0.0.1" : ip.c_str());


    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, (const char*)&t, sizeof(t)) < 0) {
        perror("Failed setsockopt recv timeout");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    if( bind(sockfd, (struct sockaddr*)&sockaddr, sizeof(sockaddr)) < 0) {
        fprintf(stderr, "Failed to bind socket to port: %d\n", port);
        exit(EXIT_FAILURE);
    }

    log("PROXY::%s: SOCKET BOUND=> IP=%s | PORT=%d\n", name.c_str(), ip.c_str(), port);
    log("PROXY::%s: PACKETS=%lu | DURATION=%d | RATE=%d\n", name.c_str(), packets, duration, rate);
    log("PROXY::%s: START\n", name.c_str());

    while(1) {
        n = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr*) &senderaddr, (socklen_t *) &len);
        if (n < sz) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                if (timestamp() >= deadline_ts) break;
                continue;
            } else {
                log("ERROR OCCURRED: %d\n", errno);
                break;
            }
        }

        msg = reinterpret_cast<MsgUDP_t*>(buf);
        log("CHILD: RCV[%4lu]\n", cnt++);

        for (int j = 0; j<total; j++) {
            n = sendto(sockfd, msg, sizeof(MsgUDP_t), 0, (struct sockaddr *) &addrs[j], sizeof(addrs[j]));
            if ( n < 0 ) {
                fprintf(stderr, "Failed to send\n");
                exit(EXIT_FAILURE);
            } else {
                log("PROXY::%s: FWD[%4lu] => ADDR[%d]\n", name.c_str(), cnt, j);
            }
        }

    }

    log("PROXY::%s: END\n", name.c_str());
    log("PROXY::%s: SUMMARY => RECV=%lu\n", name.c_str(), cnt);
    close(sockfd);
    return 0;
}

int leaf(void) {
    int sockfd;
    unsigned long cnt = 0;
    double perc;
    int n;
    auto packets = (int64_t)rate * duration;
    int sz = sizeof(MsgUDP_t);
    static char buf[1000] = { 0 };
    struct sockaddr_in sockaddr = { 0 }, senderaddr = { 0 };
    socklen_t len = sizeof(senderaddr);
    MsgUDP_t* msg;

    auto deadline_ts = deadline(1.5  * duration);
    auto t = timeout(1);

    sockaddr.sin_family       = AF_INET;
    sockaddr.sin_port         = htons(port);
    sockaddr.sin_addr.s_addr  = inet_addr(ip == "localhost" ? "127.0.0.1" : ip.c_str());

    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, (const char*)&t, sizeof(t)) < 0) {
        perror("Failed setsockopt recv timeout");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    if( bind(sockfd, (struct sockaddr*)&sockaddr, sizeof(sockaddr)) < 0) {
        fprintf(stderr, "Failed to bind socket to port: %d\n", port);
        exit(EXIT_FAILURE);
    }

    log("LEAF::%s: SOCKET BOUND=> IP=%s | PORT=%d\n", name.c_str(), ip.c_str(), port);
    log("LEAF::%s: PACKETS=%lu | DURATION=%d | RATE=%d\n", name.c_str(), packets, duration, rate);
    log("LEAF::%s: START\n", name.c_str());

    while(1) {
        n = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr*) &senderaddr, (socklen_t *) &len);
        if (n < sz) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                if (timestamp() >= deadline_ts) break;
                continue;
            } else {
                log("ERROR OCCURRED: %d\n", errno);
                break;
            }
        }

        msg = reinterpret_cast<MsgUDP_t*>(buf);
        latencies.push_back(timestamp() - msg->ts);

        log("LEAF::%s: RECV[%4lu] => ", name.c_str(), cnt++);
        log(msg->str());
        log("\n");
    }

    log("LEAF::%s: END\n", name.c_str());
    log("LEAF::%s: SUMMARY => RECV=%lu\n", name.c_str(), cnt);
    close(sockfd);

    if ((perc = get_percentile(latencies, 90)) != 0.0) {
        fprintf(stdout, "%lu\n%lf\n", cnt, perc);
        return EXIT_SUCCESS;
    } else {
        fprintf(stdout, "-1\n-1\n");
        return EXIT_FAILURE;
    }
}

int main(int argc, char **argv) {
    parse(argc, argv);
    if (ROOT)       return root();
    else if (LEAF)  return leaf();
    else            return proxy();
}
