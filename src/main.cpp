// Copyright [2023] NYU

#include <cstdlib>

int main(int argc, char *argv[]) {
    int ret = rte_eal_init(argc, argv);

    if (ret < 0) {
        rte_exit(EXIT_FAILURE, "Error with EAL initialization\n");
    }

    return 0;
}
