#include <nlohmann/json.hpp>
#include <iostream>
#include <vector>
#include <chrono>
#include <thread>
#include <fstream>
#include <sstream>

#include <cstdio>
#include <cstdlib>
#include <cstdarg>
#include <unistd.h>

#include "lemon.hpp"
#include "common.hpp"
#include "utils.hpp"
#include "log.hpp"

using json = nlohmann::json;

std::vector<std::string> vaddrs;
std::vector<std::vector<int64_t>> latencies;
std::vector<int64_t> recvs;

typedef struct Config {
    std::string name, schema, ip;
    int port, id;
    int64_t start;
    bool verbose;
    std::vector<struct sockaddr_in> addrs;

    bool valid(void) {
        if ( (this->port == 0) || (this->ip == "") ) 
            return false;

        if ( (this->schema == "") ) 
            return false;

        if (sizeof(LemonMsgUDP_t) > 44)
            return false;

        if ( this->start == 0 ) 
            return false;

        return true;
    }
    
    int read(void) {
        std::string path = "schemas/docker.json";
        std::ifstream f(path);
    
        if (!f.is_open()) {
            fprintf(stderr, "Could not open %s\n", path.c_str());
            exit(EXIT_FAILURE);
        }
    
        json j;

        f >> j;
        f.close();

        if ( ! (j.contains("addrs") && j["addrs"].is_array() ) ) {
            fprintf(stderr, "The key 'addrs' does not exist or is not an array in %s\n", path.c_str());
            exit(EXIT_FAILURE);
        }

        for (size_t i = 1; i < j["addrs"].size(); ++i) {
            vaddrs.push_back(j["addrs"][i]);
        }

        latencies.resize(vaddrs.size());
        recvs.resize(vaddrs.size(), 0);

        for (size_t i = 0; i < vaddrs.size(); ++i) {
            const auto& addr = vaddrs[i];
            if (addr != this->ip) {
                this->addrs.push_back( socketaddr(addr, this->port) );
            } else {
                this->id = i;
            }
        }

        if (latencies.size() == 0) {
            fprintf(stderr, "Empty latency vector\n");
            exit(EXIT_FAILURE);
        }

        if (this->id < 0) {
            fprintf(stderr, "Addrs list did not contain this node's ip: %s\n", this->ip.c_str());
            exit(EXIT_FAILURE);
        }

        return 0;
    }

    Config(): name(""), 
              schema(""),
              ip(""),
              port(0), 
              id(-1), 
              start(0), 
              verbose(false)
              {};
} Config_t;

void usage(int e) {
    std::string str = "Usage: ./lemon "
                      "[-i ip] [-p port] "
                      "[-s schema] "
                      "[-f future] "
                      "[-h] [-v]";

    fprintf(stdout, "%s\n", str.c_str());
    exit(e);
}

Config_t parse(int argc, char **argv) {
    int opt = 0;
    Config_t config;

    while ( (opt = getopt (argc, argv, "hvi:p:n:s:f:") ) != -1 ) {
        switch (opt) {
        case 'h':
            usage(EXIT_SUCCESS);
            break;

        case 'v':
            config.verbose = true;
            break;

        case 'i':
            config.ip = std::string{optarg};
            break;

        case 'p':
            config.port = atoi(optarg);
            break;

        case 's':
            config.schema = std::string{"schemas/" + std::string{optarg} + ".json"};
            break;

        case 'f':
            config.start = atoll(optarg);
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
    return config;
}

void receiver(Config_t config) {
    unsigned long cnt = 0;
    int sockfd, n, idx;
    static char buf[1000] = { 0 };
    struct sockaddr_in sockaddr = socketaddr(config.ip, config.port);
    struct sockaddr_in senderaddr = { 0 };
    socklen_t len = sizeof(senderaddr);
    uint64_t now;
    int64_t deadline_ts = future(config.start, 120 * (1.2));
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
        log("NODE: SOCKET BOUND => IP=%s | PORT=%d\n", config.ip.c_str(), config.port);
        log("NODE: WAITING ON START...\n");
        log("NODE: START => \n");
    }

    LemonMsgUDP_t* msg;
    int sz = sizeof(LemonMsgUDP_t);

    while(1) {
        n = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr*) &senderaddr, (socklen_t *) &len);
        if (n < sz) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                if (timestamp() >= deadline_ts) 
                    break;
                else
                    continue;
            } else {
                log("ERROR OCCURRED: %d\n", errno);
                break;
            }
        }

        msg = reinterpret_cast<LemonMsgUDP_t*>(buf);
        idx = msg->src;

        latencies[idx].push_back((now = timestamp()) - msg->ts);
        recvs[idx]++;

        if (config.verbose) {
            log("NODE: RECV[%4lu] AT TS=%lu FROM %d => ", cnt, now, idx);
            log("\n");
        }
        cnt++;
    }

}

void sender(Config_t config) {
    int sockfd;
    int cnt = 0, n, total = config.addrs.size();
    auto step = 10; // milliseconds
    auto duration = 120; // seconds
    auto packets = (duration * 1000) / (step);

    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        fprintf(stderr, "Failed to create socket\n");
        exit(EXIT_FAILURE);
    }

    if (config.verbose) {
        log("NODE: SOCKET OPENED\n");
    }

    while(1) {
        if (timestamp() >= config.start) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }

    if (config.verbose) {
        log("NODE: AWAKE\n");
    }

    for (int64_t i = 0; i < packets; i++) {
        LemonMsgUDP_t m = LemonMsgUDP_t();
        m.id  = (cnt++);
        m.src = config.id;
        m.ts  = timestamp();

        for (int j = 0; j<total; j++) {
            n = sendto(sockfd, &m, sizeof(LemonMsgUDP_t), 0, (struct sockaddr *) &config.addrs[j], sizeof(config.addrs[j]));
            if ( n < 0 ) {
                fprintf(stderr, "Failed to send\n");
                exit(EXIT_FAILURE);
            } else {
                if (config.verbose) {
                    log("NODE: SENT[%4lu] AT TS=%lu TO [%d] %d\n", cnt, m.ts, j, config.addrs[j].sin_addr.s_addr);
                }
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(step));
    }

    if (config.verbose)
        log("NODE: END\n");

    close(sockfd);
}

int output(std::vector<std::vector<int64_t>>& data, std::vector<int64_t>& recvs) {
    int ret = 0;
    try {
        for (size_t i = 0; i < data.size(); ++i) {
            double median = 0;
            if (data[i].size() != 0) median = get_percentile(data[i], 50);
            fprintf(stdout, "%s\n", vaddrs[i].c_str());
            fprintf(stdout, "%lf\n", median);
            fprintf(stdout, "%lu\n", recvs[i]);
        }
        ret = EXIT_SUCCESS;

    } catch (const std::runtime_error& e) {
        ret = EXIT_FAILURE;
    }

    return ret;
}

int main(int argc, char **argv) {
    Config_t config =  parse(argc, argv);
    config.read();

    std::thread rx(receiver, config);
    std::thread tx(sender, config);

    rx.join();
    tx.join();

    return output(latencies, recvs);
}
