#!/bin/bash -xe

role="$1"
port="$2"

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
        python3 main.py -m manager -a server &
    else 
        echo "Running Client[${port}]..."
        python3 main.py -m manager -a client -p ${port} -n ${role} &
    fi
    bash
popd
