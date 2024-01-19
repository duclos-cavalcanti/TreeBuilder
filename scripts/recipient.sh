#! /bin/bash

echo "Starting script..."

get_metadata() {
  curl -s http://metadata.google.internal/computeMetadata/v1/instance/attributes/$1 -H "Metadata-Flavor: Google"
}

echo "Fetching metadata"

# Common Variables
IP_ADDR=$(get_metadata IP_ADDR)
INSTANCE_NUM=$(get_metadata INSTANCE_NUM)
BKT_NAME=$(get_metadata BKT_NAME)
RUN_MODE=$(get_metadata RUN_MODE)
CLOUD=$(get_metadata CLOUD)

echo "IP Address: $IP_ADDR"
echo "Instance Number: $INSTANCE_NUM"
echo "Bucket Name: $BKT_NAME"
echo "Run Mode: $RUN_MODE"
echo "Cloud: $CLOUD"

# Variables for branching VMs
BRANCHING_FACTOR=$(get_metadata BRANCHING_FACTOR)
REDUNDANCY_FACTOR=$(get_metadata REDUNDANCY_FACTOR)
TOTAL_NON_REDUNDANT_PROXIES=$(get_metadata TOTAL_NON_REDUNDANT_PROXIES)
DUPLICATION_FACTOR=$(get_metadata DUPLICATION_FACTOR)

echo "Branching Factor: $BRANCHING_FACTOR"
echo "Redundancy Factor: $REDUNDANCY_FACTOR"
echo "Total Non-redundant Proxies: $TOTAL_NON_REDUNDANT_PROXIES"
echo "Duplication Factor: $DUPLICATION_FACTOR"

echo "Downloading service bundle"
cd /home/uab2005
sudo rm -rf src/
sudo mkdir src/
sudo chmod 777 src/
sudo chown -R root:root ./src

gcloud storage cp gs://duclos-dev-storage/bundle.tar.gz .
tar -xzf bundle.tar.gz -C src/
# sudo rm -rf dom-tenant-service/
# sudo mkdir dom-tenant-service/
# sudo chmod 777 dom-tenant-service/
# sudo chown -R root:root ./dom-tenant-service
#
# gcloud storage cp gs://cdm-templates-nyu-systems-multicast/bundled_proj.tar.gz .
# tar -xzf bundled_proj.tar.gz -C dom-tenant-service/
export HOME=/root

echo "Starting DPDK for ens5 and saving ens4 information"
cat /sys/class/net/ens5/address > mac.txt
cat /sys/class/net/ens4/address > macsocket.txt
ip -o -4 addr show dev ens5 | cut -d' ' -f7 | cut -d'/' -f1 > ip.txt
ip -o -4 addr show dev ens4 | cut -d' ' -f7 | cut -d'/' -f1 > ipsocket.txt
sudo modprobe igb_uio
ip link set dev ens5 down
sysctl -w vm.nr_hugepages=5000
sudo dpdk-devbind.py --bind=igb_uio 00:05.0
sudo dpdk-devbind.py --status

[ -d /mnt/huge ] || sudo mkdir /mnt/huge
sudo mount -t hugetlbfs -o pagesize=1G none /mnt/huge
sudo bash -c 'echo 4 > /sys/kernel/mm/hugepages/hugepages-1048576kB/nr_hugepages'
sudo bash -c 'echo 1024 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages'


# echo "Deploying ttcs"
# cd dom-tenant-service/gcp-deploy
# sudo chmod +x ../aws-deploy/stats_to_s3.sh
# sudo chmod +x ./deploy_ttcs.sh
# sudo ./deploy_ttcs.sh ./assets/ttcs-agent.cfg $IP_ADDR

# cd ..
# cp ./../mac.txt ./config/mac.txt
# cp ./../macsocket.txt ./config/macsocket.txt
# cp ./../ip.txt ./config/ip.txt
# cp ./../ipsocket.txt ./config/ipsocket.txt
# cd ./src
# 
# echo "Compiling receiver"
# make multicast_receivers
# 
# echo "Starting receiver"
# ./build/multicast_receivers $INSTANCE_NUM $DUPLICATION_FACTOR $RUN_MODE $BRANCHING_FACTOR $REDUNDANCY_FACTOR $TOTAL_NON_REDUNDANT_PROXIES $CLOUD
