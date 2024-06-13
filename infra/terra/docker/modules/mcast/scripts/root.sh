#!/bin/bash -xe

role="$1" 
shift 1
command="$@"

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
        command="${command} -v"
        sleep 2s
        echo ${command}
        ${command}
        echo "RET: ${?}"
    popd
    bash
popd
