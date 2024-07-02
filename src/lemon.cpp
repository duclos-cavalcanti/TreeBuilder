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

typedef struct Config {
    std::string name, schema, ip;
    json j;
    int port;
    bool verbose;
    std::vector<std::string> addrs;
    std::vector<struct sockaddr_in> sockaddrs;
    std::vector<int> idxs;

    bool valid(void) {
        if ( (this->port == 0) || (this->ip == "") ) 
            return false;

        if ( (this->schema == "") ) 
            return false;

        if (sizeof(LemonMsgUDP_t) > 44)
            return false;

        return true;
    }
    
    int read(void) {
        bool valid = false;
        std::string path = "schemas/docker.json";
        std::ifstream f(path);
    
        if (!f.is_open()) {
            fprintf(stderr, "Could not open %s\n", path.c_str());
            exit(EXIT_FAILURE);
        }
    
        f >> this->j;
        f.close();

        if ( ! (j.contains("addrs") && j["addrs"].is_array() ) ) {
            fprintf(stderr, "The key 'addrs' does not exist or is not an array in %s\n", path.c_str());
            exit(EXIT_FAILURE);
        }
    
        this->addrs = j["addrs"].get<std::vector<std::string>>();

        for (size_t i = 0; i < addrs.size(); ++i) {
            const auto& addr = addrs[i];
            if (addr != this->ip) {
                this->sockaddrs.push_back( socketaddr(addr, this->port) );
                this->idxs.push_back(i);
            } else {
                valid = true;
            }
        }

        if (!valid) {
            fprintf(stderr, "addrs list did not contain this node's addr: %s\n", this->ip.c_str());
            exit(EXIT_FAILURE);
        }

        return 0;
    }

    Config(): name(""), 
              schema(""),
              ip(""),
              port(0), 
              verbose(false)
              {};
} Config_t;

void usage(int e) {
    std::string str = "Usage: ./lemon "
                      "[-i ip] [-p port] "
                      "[-s schema] "
                      "[-h] [-v]";

    fprintf(stdout, "%s\n", str.c_str());
    exit(e);
}

Config_t parse(int argc, char **argv) {
    int opt = 0;
    Config_t config;

    while ( (opt = getopt (argc, argv, "hvi:p:n:s:") ) != -1 ) {
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

}

void sender(Config_t config) {

}

int main(int argc, char **argv) {
    Config_t config =  parse(argc, argv);
    config.read();

    // std::thread rx(receiver, config);
    // std::thread tx(sender, config);

    // rx.join();
    // tx.join();

    return 0;
}
