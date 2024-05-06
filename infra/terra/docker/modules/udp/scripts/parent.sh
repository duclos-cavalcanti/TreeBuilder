#!/bin/bash -xe

echo "ARGS: $@"
role="$1" 
shift 1

addrs="$@"

export ROLE="$role"

TAR="/work/project.tar.gz"
mkdir /work/project
tar -xzf ${TAR} -C /work/project

mkdir /work/project/build
pushd /work/project/build
    echo "-- ROLE: $role --"
    cmake ..
    make
    pushd /work/project/
        echo ./bin/parent -a ${addrs} -r 10 -d 10
        ./bin/parent -a ${addrs} -r 10 -d 10
        echo "RET: ${?}"
    popd
    bash
popd
