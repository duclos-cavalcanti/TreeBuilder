#!/bin/bash -xe

role="$1" 
count="$2" 
shift 2
command="$@"

export ROLE="$role"

edelay() {
    if [ $count -gt 0 ] && (( $count % 2 == 0)); then 
        dur=300
        sudo tc qdisc add dev "eth0" root netem delay ${dur}ms
        echo "SUCCESSFULL EGRESS DELAY: ${dur}ms"
    fi
}

idelay() {
    if [ $count -gt 0 ] && (( $count % 2 == 0)); then 
        dur=300
        sudo modprobe ifb 
        sudo modprobe sch_netem
        sudo ip link add ifb0 type ifb
        sudo ip link set ifb0 up
        sudo tc qdisc add dev eth0 handle ffff: ingress
        sudo tc filter add dev eth0 parent ffff: protocol ip u32 match u32 0 0 action mirred egress redirect dev ifb0
        sudo tc qdisc add dev ifb0 root netem delay ${dur}ms
        echo "SUCCESSFULL INGRESS DELAY: ${dur}ms"
    fi
}

TAR="/work/project.tar.gz"
mkdir /work/project
tar -xzf ${TAR} -C /work/project

mkdir /work/project/build
pushd /work/project/build
    echo "-- ROLE: $role --"
    cmake ..
    make
    pushd /work/project/
        delay
        command="${command} -v"
        echo ${command}
        ${command}
        echo "RET: ${?}"
    popd
    bash
popd
