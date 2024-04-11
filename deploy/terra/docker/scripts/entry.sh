#!/bin/bash -xe

role="$1"

pushd /work/project
    mkdir build 
    pushd build 
        cmake ..
        make 
    popd
    echo "-- ROLE: $role --"
    ./bin/project -r ${role}
    bash
popd
