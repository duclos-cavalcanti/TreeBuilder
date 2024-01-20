#! /bin/bash

echo "START UP..."
touch LOG.TXT

get_metadata() {
  curl -s http://metadata.google.internal/computeMetadata/v1/instance/attributes/$1 -H "Metadata-Flavor: Google"
}

STACK="duclos-dev"
BUCKET="duclos-dev-storage"
DATA=$(get_metadata KEY)

echo "METADATA \$KEY: ${DATA}"
echo "DOWNLOADING PROJECT..."
{
    sudo rm -rf dom-tenant-service/
    sudo mkdir dom-tenant-service/
    gcloud storage cp gs://${BUCKET}/bundle.tar.gz .
    tar -xzf bundle.tar.gz -C dom-tenant-service/
    sudo chmod 777 dom-tenant-service/
    sudo chown -R root:root ./dom-tenant-service
} &>> LOG.TXT

echo "DPDK SETUP..."
{
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
} &>> LOG.TXT
