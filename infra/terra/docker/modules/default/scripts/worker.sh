#!/bin/bash -xe

role="$1"
addr="$2"
port="$3"
count=$4

export ROLE="$role"

TAR="/work/project.tar.gz"
mkdir -p /work/logs
mkdir -p /work/project
tar -xzf ${TAR} -C /work/project

mkdir /work/project/build
pushd /work/project/build
    cmake ..
    make
popd

edelay() {
    dur="$1"
    sudo tc qdisc add dev "eth0" root netem delay ${dur}ms
    echo "SUCCESSFULL EGRESS DELAY: ${dur}ms"
}

idelay() {
    dur="$1"
    sudo ip link add ifb0 type ifb
    sudo ip link set ifb0 up
    sudo tc qdisc add dev eth0 handle ffff: ingress
    sudo tc filter add dev eth0 parent ffff: protocol ip u32 match u32 0 0 action mirred egress redirect dev ifb0
    sudo tc qdisc add dev ifb0 root netem delay ${dur}ms
    echo "SUCCESSFULL INGRESS DELAY: ${dur}ms"
}

pushd /work/project
    echo "-- ROLE: $role [ ${addr}:${port} ] --"

    if [ $count -gt 2 ] && (( $count % 2 == 0)); then 
        idelay 10
    fi

    python3 -m manager -a worker -n ${role}  -i ${addr} -p ${port}
    bash
popd
