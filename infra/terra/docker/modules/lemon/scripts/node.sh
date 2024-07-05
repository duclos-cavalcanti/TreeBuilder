#!/bin/bash -xe

role="$1" 
count="$2" 
shift 2
command="$@"

export ROLE="$role"
TAR="/work/project.tar.gz"

tzone() {
    sudo ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime && echo 'America/New_York' > /etc/timezone
    cat /etc/timezone
}

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

setup() {
    mkdir -p /work/logs
    mkdir -p /work/project
    tar -xzf ${TAR} -C /work/project

    mkdir /work/project/build
    pushd /work/project/build
        cmake ..
        make
    popd
}

main() {
    setup
    pushd /work/project
        echo "-- ROLE: $role --"

        tzone

        # even numbered workers with index greater than 0
        if [ $count -gt 0 ] && (( $count % 2 == 0)); then 
            idelay 0.3
        fi
    
        echo ${command}
        ${command} -v

        echo "RET: ${?}"
    popd
}

main
bash

