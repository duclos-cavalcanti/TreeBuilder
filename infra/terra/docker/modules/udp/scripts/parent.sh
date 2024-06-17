#!/bin/bash -xe

role="$1" 
shift 1
command="$@"

export ROLE="$role"
TAR="/work/project.tar.gz"

setup() {
    mkdir -p /work/logs
    mkdir -p /work/project
    tar -xzf ${TAR} -C /work/project

    mkdir /work/project/build
    pushd /work/project/build
        cmake ..
        make
    popd
}

main() {
    setup
    sleep 2s 
    pushd /work/project
        echo "-- ROLE: $role --"
    
        echo ${command}
        ${command} -v

        echo "RET: ${?}"
        bash
    popd
}

main
