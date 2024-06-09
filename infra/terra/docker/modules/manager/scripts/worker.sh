#!/bin/bash -xe

role="$1"
addr="$2"
port="$3"
id="$4"

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
    python3 main.py -m manager -a worker -n ${role}  -i ${addr} -p ${port}
    # PID=$!
    # echo "PID: ${PID}"
    bash
popd
