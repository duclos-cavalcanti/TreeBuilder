#include <iostream>
#include <chrono>
#include <vector>

#include <cstdio>
#include <cstdlib>
#include <cstdarg>
#include <unistd.h>

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <arpa/inet.h>

#include "common.hpp"
#include "utils.hpp"
#include "log.hpp"

int output(std::vector<int64_t>& data, unsigned long cnt);

typedef struct Config {
    std::string name, ip;
    int port, rate, duration;
    float killfactor;
    bool verbose;

    bool valid(void) {
        if (this->duration == 0)
            return false;

        if (this->port == 0)
            return false;

        if (this->ip == "")
            return false;

        return true;
    }

    Config(): name(""), 
              ip(""),
              port(0),
              rate(0), 
              duration(0), 
              killfactor(0.0),
              verbose(false)
              {};
} Config_t;

Config_t config;

void usage(int e) {
    std::string str = "Usage: ./child "
                      "[-r rate] [-d duration] "
                      "[-i ip] [-p port] [-n name]"
                      "[-h] [-v]";

    fprintf(stdout, "%s\n", str.c_str());
    exit(e);
}

int parse(int argc, char **argv) {
    int opt = 0;
    int ret = 0;
    while ( (opt = getopt (argc, argv, "hi:p:t:d:r:n:k:v") ) != -1 ) {
        switch (opt) {
        case 'h':
            usage(EXIT_SUCCESS);
            break;

        case 'v':
            config.verbose = true;
            break;

        case 'i':
            config.ip =  std::string{optarg};
            break;

        case 'p':
            config.port = atoi(optarg);
            break;

        case 'r':
            config.rate = atoi(optarg);
            break;

        case 'n':
            config.name = std::string{optarg};
            break;

        case 'k': 
            config.killfactor = std::stof(optarg);
            break;

        case 'd':
            config.duration = atoi(optarg);
            break;

        default:
            usage(EXIT_FAILURE);
            break;
        }
    }

    if (optind > argc || !config.valid()) usage(EXIT_FAILURE);
    return ret;
}

int child(void) {
    unsigned long cnt = 0;
    int sockfd, n;
    static char buf[1000] = { 0 };
    struct sockaddr_in sockaddr = socketaddr(config.ip, config.port);
    struct sockaddr_in senderaddr = { 0 };
    socklen_t len = sizeof(senderaddr);
    MsgUDP_t* msg;
    int sz = sizeof(MsgUDP_t);
    uint64_t now;
    std::vector<int64_t> latencies;
    float killfactor = ( config.killfactor == 0.0 ? 1.5 : config.killfactor );

    auto deadline_ts = deadline((killfactor) * config.duration);
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
        log("CHILD: SOCKET BOUND => IP=%s | PORT=%d\n", config.ip.c_str(), config.port);
        log("CHILD: WAITING ON START...\n");
        log("CHILD: START => \n");
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
        latencies.push_back((now = timestamp()) - msg->ts);

        if (config.verbose) {
            log("CHILD: RECV[%4lu] AT TS=%lu => ", cnt, now);
            log(msg->str());
            log("\n");
        }
        cnt++;
    }

    if (config.verbose) {
        log("CHILD: END\n");
        log("SUMMARY | RECV=%lu | LATENCY_VECTOR=%lu\n", cnt, latencies.size());
    }
    
    close(sockfd);
    return output(latencies, cnt);
}


int output(std::vector<int64_t>& data, unsigned long cnt) {
    int     ret = 0;
    int64_t ts  = timestamp();
    std::string errout = "-1\n-1\n-1\n-1\n-1\n-1";
    std::string name = ( config.name == "" ? "results" : config.name ) + "_child_" + std::to_string(ts);

    try {
        double p90 = get_percentile(data, 90);
        double p75 = get_percentile(data, 75);
        double p50 = get_percentile(data, 50);
        double p25 = get_percentile(data, 25);
        double dev = get_stdev(data);
        double mean = get_mean(data);

        fprintf(stdout, "%lu\n", cnt);
        fprintf(stdout, "%lf\n", p90);
        fprintf(stdout, "%lf\n", p75);
        fprintf(stdout, "%lf\n", p50);
        fprintf(stdout, "%lf\n", p25);
        fprintf(stdout, "%lf\n", dev);
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
    return child();
}
