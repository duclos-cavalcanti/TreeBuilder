// Copyright [2023] NYU

#include <rte_eal.h>
#include <rte_cycles.h>
#include <rte_errno.h>
#include <rte_ethdev.h>

#include <cstdlib>
#include <cstdio>

int main(int argc, char *argv[]) {
    int ret = rte_eal_init(argc, argv);

    if (ret < 0) {
        rte_exit(EXIT_FAILURE, "Error with EAL initialization\n");
    }

    printf("Number of ETHERNET DEVICES: %d", rte_eth_dev_count_avail());
    return 0;
}
