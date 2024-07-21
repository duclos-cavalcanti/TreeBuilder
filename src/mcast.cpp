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
#include "utils.hpp"
#include "log.hpp"

int output(std::vector<int64_t>& data, unsigned long cnt);

typedef struct Config {
    std::string name, ip;
    int port, rate, duration;
    bool root, verbose;
    std::vector<struct sockaddr_in> addrs;

    bool valid(void) {
        if (this->duration == 0)
            return false;

        if ( !this->root && ((this->port == 0) || this->ip == "" ) )
            return false;

        return true;
    }

    Config(): name(""), 
              ip(""),
              port(0), 
              rate(0), 
              duration(0), 
              root(false), 
              verbose(false)
              {};
} Config_t;

Config_t config;

void usage(int e) {
    std::string str = "Usage: ./mcast "
                      "[-a ADDR_1 ADDR_2] "
                      "[-r rate] [-d duration] "
                      "[-i ip] [-p port] [-R] "
                      "[-h] [-v]";

    fprintf(stdout, "%s\n", str.c_str());
    exit(e);
}

int parse(int argc, char **argv) {
    int opt = 0, opti = 0;
    int ret = 0;
    while ( (opt = getopt (argc, argv, "hn:i:p:a:r:d:vR") ) != -1 ) {
        switch (opt) {
        case 'h':
            usage(EXIT_SUCCESS);
            break;

        case 'v':
            config.verbose = true;
            break;

        case 'a':
            opti = optind - 1;
            while (optind < argc && argv[opti][0] != '-') {
                auto parts = split(std::string {argv[opti]}, ':');
                config.addrs.push_back(socketaddr(parts[0], atoi(parts[1].c_str())));
                opti++;
            }
            optind = opti - 1;
            break;

        case 'i':
            config.ip = std::string{optarg};
            break;

        case 'p':
            config.port = atoi(optarg);
            break;

        case 'r':
            config.rate = atoi(optarg);
            break;

        case 'd':
            config.duration = atoi(optarg);
            break;

        case 'R':
            config.root = true;
            break;

        case 'n':
            config.name = std::string{optarg};
            break;

        default:
            usage(EXIT_FAILURE);
            break;
        }
    }


    if (optind > argc || !config.valid()) usage(EXIT_FAILURE);
    return ret;
}

int root(void) {
    int sockfd;
    int cnt = 0, n, total = config.addrs.size();
    auto packets = (int64_t)config.rate * config.duration;

    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    if (config.verbose) {
        log("ROOT::%s: SOCKET OPENED\n", config.name.c_str());
        log("ROOT::%s: PACKETS=%lu | DURATION=%d | RATE=%d\n", config.name.c_str(), packets, config.duration, config.rate);
    }

    auto start  = std::chrono::system_clock::now();
    auto step = std::chrono::duration<double>(1) / config.rate;

    for (int64_t i = 0; i < packets; i++) {
        MsgUDP_t m = MsgUDP();
        m.id  = (cnt++);
        m.ts  = timestamp();

        for (int j = 0; j<total; j++) {
            n = sendto(sockfd, &m, sizeof(MsgUDP_t), 0, (struct sockaddr *) &config.addrs[j], sizeof(config.addrs[j]));
            if ( n < 0 ) {
                fprintf(stderr, "Failed to send\n");
                exit(EXIT_FAILURE);
            } else {
                if (config.verbose) 
                    log("ROOT::%s: SENT[%4lu] => ADDR[%d] | TS=%lu\n", config.name.c_str(), i, j, m.ts);
            }
        }
        std::this_thread::sleep_until(start + (step * i));
    }

    if (config.verbose) 
        log("ROOT::%s: END\n", config.name.c_str());

    close(sockfd);
    return 0;
}

int proxy(void) {
    int sockfd;
    unsigned long cnt = 0;
    int n, total = config.addrs.size();
    auto packets = (int64_t)config.rate * config.duration;
    static char buf[1000] = { 0 };
    struct sockaddr_in sockaddr = socketaddr(config.ip, config.port);
    struct sockaddr_in senderaddr = { 0 };
    socklen_t len = sizeof(senderaddr);
    MsgUDP_t* msg;
    int sz = sizeof(MsgUDP_t);

    auto deadline_ts = deadline(1.5  * config.duration);
    auto t = timeout(1);

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
        fprintf(stderr, "Failed to bind socket to port: %d\n", config.port);
        exit(EXIT_FAILURE);
    }

    if (config.verbose) {
        log("PROXY::%s: SOCKET BOUND=> IP=%s | PORT=%d\n", config.name.c_str(), config.ip.c_str(), config.port);
        log("PROXY::%s: PACKETS=%lu | DURATION=%d | RATE=%d\n", config.name.c_str(), packets, config.duration, config.rate);
        log("PROXY::%s: START\n", config.name.c_str());
    }

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
        for (int j = 0; j<total; j++) {
            n = sendto(sockfd, msg, sizeof(MsgUDP_t), 0, (struct sockaddr *) &config.addrs[j], sizeof(config.addrs[j]));
            if ( n < 0 ) {
                fprintf(stderr, "Failed to send\n");
                exit(EXIT_FAILURE);
            } else {
                if (config.verbose) 
                    log("PROXY::%s: FWD[%4lu] => ADDR[%d]\n", config.name.c_str(), cnt, j);
            }
        }
        cnt++;
    }

    if (config.verbose)  {
        log("PROXY::%s: END\n", config.name.c_str());
        log("PROXY::%s: SUMMARY => RECV=%lu\n", config.name.c_str(), cnt);
    }

    close(sockfd);
    return 0;
}

int leaf(void) {
    int sockfd, n;
    unsigned long cnt = 0;
    auto packets = (int64_t)config.rate * config.duration;
    static char buf[1000] = { 0 };
    struct sockaddr_in sockaddr = socketaddr(config.ip, config.port);
    struct sockaddr_in senderaddr = { 0 };
    socklen_t len = sizeof(senderaddr);
    MsgUDP_t* msg;
    int sz = sizeof(MsgUDP_t);
    std::vector<int64_t> latencies;

    auto deadline_ts = deadline(1.5  * config.duration);
    auto t = timeout(1);

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
        fprintf(stderr, "Failed to bind socket to port: %d\n", config.port);
        exit(EXIT_FAILURE);
    }

    if (config.verbose) {
        log("LEAF::%s: SOCKET BOUND=> IP=%s | PORT=%d\n", config.name.c_str(), config.ip.c_str(), config.port);
        log("LEAF::%s: PACKETS=%lu | DURATION=%d | RATE=%d\n", config.name.c_str(), packets, config.duration, config.rate);
        log("LEAF::%s: START\n", config.name.c_str());
    }

    while(1) {
        n = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr*) &senderaddr, (socklen_t *) &len);
        if (n < sz) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                if (timestamp() >= deadline_ts) break;
                continue;
            } else {
                if (config.verbose)
                    log("ERROR OCCURRED: %d\n", errno);
                break;
            }
        }

        msg = reinterpret_cast<MsgUDP_t*>(buf);
        latencies.push_back(timestamp() - msg->ts);

        if (config.verbose) {
            log("LEAF::%s: RECV[%4lu] => ", config.name.c_str(), cnt);
            log(msg->str());
            log("\n");
        }
        cnt++;
    }

    if (config.verbose) {
        log("LEAF::%s: END\n", config.name.c_str());
        log("LEAF::%s: SUMMARY => RECV=%lu\n", config.name.c_str(), cnt);
    }

    close(sockfd);
    return output(latencies, cnt);
}

int output(std::vector<int64_t>& data, unsigned long cnt) {
    int ret = 0;
    std::string errout = "-1\n-1\n-1\n-1\n-1\n-1";
    int64_t ts  = timestamp();
    std::string name = ( config.name == "" ? "results" : config.name ) + "_mcast_" + std::to_string(ts);

    try {
        double p90 = get_percentile(data, 90);
        double p75 = get_percentile(data, 75);
        double p50 = get_percentile(data, 50);
        double p25 = get_percentile(data, 25);
        double var = get_stdev(data);
        double mean = get_mean(data);

        fprintf(stdout, "%lu\n", cnt);
        fprintf(stdout, "%lf\n", p90);
        fprintf(stdout, "%lf\n", p75);
        fprintf(stdout, "%lf\n", p50);
        fprintf(stdout, "%lf\n", p25);
        fprintf(stdout, "%lf\n", var);
        fprintf(stdout, "%lf\n", mean);
        ret = EXIT_SUCCESS;

    } catch (const std::runtime_error& e) {
        fprintf(stdout, "%s\n", errout.c_str());
        ret = EXIT_FAILURE;
    }

    std::string header =   config.ip + ","
                         + std::to_string(config.rate) + "," 
                         + std::to_string(config.duration) + ","
                         + std::to_string(ts);

    if (ret)    return ret;
    else        return (ret = write_csv(data, name, header));
}

int main(int argc, char **argv) {
    parse(argc, argv);
    if (config.root)                return root();
    else if (!config.addrs.empty()) return proxy();
    else                            return leaf();
}
