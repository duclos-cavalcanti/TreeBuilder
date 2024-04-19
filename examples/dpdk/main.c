#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>
#include <sys/queue.h>

#include <rte_memory.h>
#include <rte_ethdev.h>
#include <rte_memzone.h>
#include <rte_launch.h>
#include <rte_eal.h>
#include <rte_per_lcore.h>
#include <rte_lcore.h>
#include <rte_debug.h>

#define RX_RING_SIZE    128
#define NUM_MBUFS       8191
#define MBUF_CACHE_SIZE 250
#define BURST_SIZE      32

static char errstr[100] = { 0 };

static const struct rte_eth_conf port_conf_default = {};
struct rte_mempool *mbuf_pool;

int run() {
    long unsigned int cnt = 0;
    struct rte_mbuf *bufs[BURST_SIZE];

    puts("-- DPDK UDP PACKET CAPTURE --\n");
    while (1) {
        uint16_t nb_rx = rte_eth_rx_burst(portid, 0, bufs, BURST_SIZE);
        for (int i = 0; i < nb_rx; i++) {
            struct rte_mbuf *m = bufs[i];
            struct rte_ether_hdr *eth_hdr  = rte_pktmbuf_mtod(m, struct rte_ether_hdr *);
            struct rte_ipv4_hdr  *ipv4_hdr = (struct rte_ipv4_hdr *)(eth_hdr + 1);
            struct rte_udp_hdr   *udp_hdr  = (struct rte_udp_hdr *)(ipv4_hdr + 1);

            if (eth_hdr->ether_type == rte_be_to_cpu_16(RTE_ETHER_TYPE_IPV4)) {
                if (ipv4_hdr->next_proto_id == IPPROTO_UDP) {
                    printf("Received: %u bytes | %d\n", rte_be_to_cpu_16(udp_hdr->dgram_len), cnt++);
                }
            }

            rte_pktmbuf_free(m);
        }
    }
    return 0;
}

int main(int argc, char **argv) {
    int ret;
    uint16_t portid = 0;

    // EAL Initialization
	ret = rte_eal_init(argc, argv);
	if (ret < 0) {
		rte_exit(EXIT_FAILURE, "Error: EAL Initialization\n");
    }

    // Port Availability
    unsigned int nb_ports = rte_eth_dev_count_avail();
	if (nb_ports == 0) {
        sprintf(errstr, "Error: Port Availability: n = %d\n", nb_ports);
		rte_exit(EXIT_FAILURE, errstr);
    }

    // Eth Device Configuration
    ret = rte_eth_dev_configure(portid, 1, 0, &port_conf_default);
    if (ret < 0) {
        rte_exit(EXIT_FAILURE, "Error: Ethernet Device Configuration\n");
    }

    // Memory Pool Creation
    mbuf_pool = rte_pktmbuf_pool_create("MBUF_POOL", 
                                        NUM_MBUFS,
                                        MBUF_CACHE_SIZE, 
                                        0, 
                                        RTE_MBUF_DEFAULT_BUF_SIZE,
                                        rte_socket_id());
    if (mbuf_pool == NULL) {
        rte_exit(EXIT_FAILURE, "Error: MBUF POOL Creation\n");
    }

    // RX QUEUE Setup
    ret = rte_eth_rx_queue_setup(portid, 0, RX_RING_SIZE, rte_eth_dev_socket_id(portid), NULL, mbuf_pool);
    if (ret < 0) {
        rte_exit(EXIT_FAILURE, "Error: RX QUEUE Setup\n");
    }

    // Ethernet Device Launch
    ret = rte_eth_dev_start(portid);
    if (ret < 0) {
        rte_exit(EXIT_FAILURE, "Error: Ethernet Device Start\n");
    }

	return run(portid);
}
