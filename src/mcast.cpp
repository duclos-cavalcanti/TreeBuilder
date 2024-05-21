#include <iostream>
#include <vector>
#include <chrono>
#include <thread>
#include <sstream>

#include <cstdio>
#include <cstdlib>
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

    if (verbose) {
        fprintf(LOG, "ROOT::%s: SOCKET OPENED\n", name.c_str());
        fprintf(LOG, "ROOT::%s: PACKETS=%lu | DURATION=%d | RATE=%d\n", name.c_str(), packets, duration, rate);
    }

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
                if (verbose) {
                    fprintf(LOG, "ROOT::%s: SENT[%4lu] => ADDR[%d] | TS=%lu\n", name.c_str(), i, j, m.ts);
                }
            }
        }
        std::this_thread::sleep_until(start + (step * i));
    }

    if (verbose) {
        fprintf(LOG, "ROOT::%s: END\n", name.c_str());
    }

    close(sockfd);
    return 0;
}

int proxy(void) {
    int sockfd;
    unsigned long cnt = 0;
    int len, n, total = addrs.size();
    auto packets = (int64_t)rate * duration;
    int sz = sizeof(MsgUDP_t);
    static char buf[1000] = { 0 };
    struct sockaddr_in sockaddr = { 0 }, senderaddr = { 0 };
    MsgUDP_t* msg;

    auto deadline_ts = deadline(1.2  * duration);

    sockaddr.sin_family       = AF_INET;
    sockaddr.sin_port         = htons(port);
    sockaddr.sin_addr.s_addr  = inet_addr(ip == "localhost" ? "127.0.0.1" : ip.c_str());


    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    if( bind(sockfd, (struct sockaddr*)&sockaddr, sizeof(sockaddr)) < 0) {
        fprintf(stderr, "Failed to bind socket to port: %d\n", port);
        exit(EXIT_FAILURE);
    }

    if (verbose) {
        fprintf(LOG, "PROXY::%s: SOCKET BOUND=> IP=%s | PORT=%d\n", name.c_str(), ip.c_str(), port);
        fprintf(LOG, "PROXY::%s: PACKETS=%lu | DURATION=%d | RATE=%d\n", name.c_str(), packets, duration, rate);
    }

    if (verbose) {
        fprintf(LOG, "PROXY::%s: START\n", name.c_str());
    }

    while(1) {
        n = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr*) &senderaddr, (socklen_t *) &len);
        if (n < sz) {
            continue;
        }

        msg = reinterpret_cast<MsgUDP_t*>(buf);

        if (verbose) {
            fprintf(LOG, "CHILD: RCV[%4lu]\n", cnt);
        }

        cnt++;

        for (int j = 0; j<total; j++) {
            n = sendto(sockfd, msg, sizeof(MsgUDP_t), 0, (struct sockaddr *) &addrs[j], sizeof(addrs[j]));
            if ( n < 0 ) {
                fprintf(stderr, "Failed to send\n");
                exit(EXIT_FAILURE);
            } else {
                if (verbose) {
                    fprintf(LOG, "PROXY::%s: FWD[%4lu] => ADDR[%d]\n", name.c_str(), cnt, j);
                }
            }
        }

        if (1) {
            if (verbose) {
                fprintf(LOG, "PROXY::%s: SUMMARY => RECV=%lu\n", name.c_str(), cnt);
            }
            break;
        }
    }

    if (verbose) {
        fprintf(LOG, "PROXY::%s: END\n", name.c_str());
    }

    close(sockfd);
    return 0;
}

int leaf(void) {
    int sockfd;
    unsigned long cnt = 0;
    double perc;
    int len, n;
    auto packets = (int64_t)rate * duration;
    int sz = sizeof(MsgUDP_t);
    static char buf[1000] = { 0 };
    struct sockaddr_in sockaddr = { 0 }, senderaddr = { 0 };
    MsgUDP_t* msg;

    sockaddr.sin_family       = AF_INET;
    sockaddr.sin_port         = htons(port);
    sockaddr.sin_addr.s_addr  = inet_addr(ip == "localhost" ? "127.0.0.1" : ip.c_str());

    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    if( bind(sockfd, (struct sockaddr*)&sockaddr, sizeof(sockaddr)) < 0) {
        fprintf(stderr, "Failed to bind socket to port: %d\n", port);
        exit(EXIT_FAILURE);
    }

    if (verbose) {
        fprintf(LOG, "LEAF::%s: SOCKET BOUND=> IP=%s | PORT=%d\n", name.c_str(), ip.c_str(), port);
        fprintf(LOG, "LEAF::%s: PACKETS=%lu | DURATION=%d | RATE=%d\n", name.c_str(), packets, duration, rate);
    }

    if (verbose) {
        fprintf(LOG, "LEAF::%s: START\n", name.c_str());
    }

    while(1) {
        n = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr*) &senderaddr, (socklen_t *) &len);
        if (n < sz) {
            continue;
        }

        msg = reinterpret_cast<MsgUDP_t*>(buf);
        latencies.push_back(timestamp() - msg->ts);

        if (verbose) {
            fprintf(LOG, "LEAF::%s: RCV[%4lu] => ", name.c_str(), cnt);
            msg->print();
            fprintf(LOG, "\n");
        }

        cnt++;

        if (1) {
            if (verbose) {
                fprintf(LOG, "LEAF::%s: SUMMARY => RECV=%lu\n", name.c_str(), cnt);
            }
            break;
        }
    }

    if (verbose) {
        fprintf(LOG, "LEAF::%s: END\n", name.c_str());
    }

    close(sockfd);

    if ((perc = get_percentile(latencies, 90)) != 0.0) {
        fprintf(stdout, "%lu\n%lf\n", cnt, perc);
        return EXIT_SUCCESS;
    } else {
        fprintf(stdout, "EMPTY LATENCY VECTOR!\n");
        return EXIT_FAILURE;
    }
}

int main(int argc, char **argv) {
    parse(argc, argv);
    if (ROOT)       return root();
    else if (LEAF)  return leaf();
    else            return proxy();
}
