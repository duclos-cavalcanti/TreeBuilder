#!/bin/bash -xe

role="$1" 
count="$2" 
shift 2
command="$@"

export ROLE="$role"

delay() {
    if [ $count -gt 0 ] && (( $count % 2 == 0)); then 
        dur=300
        sudo tc qdisc add dev "eth0" root netem delay ${dur}ms
        echo "SUCCESSFULL DELAY: ${dur}ms"
    fi
}

TAR="/work/project.tar.gz"
mkdir /work/project
tar -xzf ${TAR} -C /work/project

mkdir /work/project/build
pushd /work/project/build
    echo "-- ROLE: $role --"
    cmake ..
    make
    pushd /work/project/
        delay
        command="${command} -v"
        echo ${command}
        ${command}
        echo "RET: ${?}"
    popd
    bash
popd
