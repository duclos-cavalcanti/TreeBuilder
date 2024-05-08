#!/bin/bash -xe

echo "ARGS: $@"
role="$1" 
shift 1
rate=10
dur=10

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
        command="./bin/parent -a ${addrs} -r ${rate} -d ${dur} -v"
        sleep 2s
        echo ${command}
        ${command}
        echo "RET: ${?}"
    popd
    bash
popd
