#!/bin/bash -xe

role="$1"
export ROLE="$role"

pushd /work/project
    mkdir build 
    pushd build 
        cmake ..
        make 
    popd
    echo "-- ROLE: $role --"
    if [ "${role}" == "manager" ]; then 
        echo "Running Manager..."
    else 
        echo ./bin/project -r ${role}
    fi
    bash
popd
