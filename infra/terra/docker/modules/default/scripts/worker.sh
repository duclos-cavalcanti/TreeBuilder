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

pushd /work/project
    echo "-- ROLE: $role [ ${addr}:${port} ] --"
    if [ $count -gt 0 ] && (( $count % 2 == 0)); then 
        delay=300
        echo "DELAY: ${delay}ms"
        sudo tc qdisc add dev "eth0" root netem delay ${delay}ms
    fi
    python3 -m manager -a worker -n ${role}  -i ${addr} -p ${port}
    bash
popd
