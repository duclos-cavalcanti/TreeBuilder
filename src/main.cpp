#include <rte_eal.h>
#include <rte_cycles.h>
#include <rte_errno.h>
#include <rte_ethdev.h>
#include <rte_ether.h>
#include <rte_ip.h>
#include <rte_lcore.h>
#include <rte_mbuf.h>
#include <rte_malloc.h>
#include <rte_udp.h>

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
