#!/bin/bash -xe

echo "ARGS: $@"
role="$1" 
shift 1
args="$@"

export ROLE="$role"

TAR="/work/project.tar.gz"
mkdir /work/project
tar -xzf ${TAR} -C /work/project

mkdir /work/project/build
pushd /work/project/build
    echo "-- ROLE: $role --"
    cmake ..
    make mcast
    pushd /work/project/
        command="./bin/mcast ${args} -n ${role} -v"
        echo ${command}
        ${command}
        echo "RET: ${?}"
    popd
    bash
popd
