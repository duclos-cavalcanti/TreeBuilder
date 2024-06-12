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

if [ $count -gt 0 ] && (( $count % 2 == 0)); then 
    echo tc qdisc add dev "eth0" root netem delay 300ms
    sudo tc qdisc add dev "eth0" root netem delay 400ms
fi

mkdir /work/project/build
pushd /work/project/build
    cmake ..
    make
popd

pushd /work/project
    echo "-- ROLE: $role [ ${addr}:${port} ] --"
    python3 -m manager -a worker -n ${role}  -i ${addr} -p ${port}
    bash
popd
