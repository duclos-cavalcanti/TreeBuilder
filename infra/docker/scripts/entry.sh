#!/bin/bash -xe

role="$1"
addr="$2"
port="$3"

export ROLE="$role"

pushd /work/project
    mkdir build 
    pushd build 
        cmake ..
        make 
    popd
    echo "-- ROLE: $role --"
    if [ "${role}" == "manager" ]; then 
        echo "Running Manager[${port}]..."
        python3 main.py -m manager -a server -i ${addr} -p ${port}  &
    else 
        echo "Running Client[${port}]..."
        python3 main.py -m manager -a client -i ${addr} -p ${port} -n ${role} &
    fi
    bash
popd
