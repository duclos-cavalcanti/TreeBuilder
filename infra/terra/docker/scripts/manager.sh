#!/bin/bash -xe

role="$1"
addr="$2"
port="$3"
id="$4"

export ROLE="$role"

TAR="/work/project.tar.gz"
mkdir /work/project
tar -xzf ${TAR} -C /work/project

pushd /work/project
    echo "-- ROLE: $role --"
    python3 main.py -m manager -a manager -i ${addr} -p ${port}
    # PID=$!
    # echo "PID: ${PID}"
    bash
popd
