#!/bin/bash -xe

role="$1"
addr="$2"
port="$3"

export ROLE="$role"
TAR="/work/project.tar.gz"
BUCKET=

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

upload() {
    pushd /work 
        echo "STARTING UPLOAD"
        tar -zcvf results.tar.gz ./logs
        mv results.tar.gz /work/logs
        mv project/schemas/docker.json /work/logs
        echo "FINISHED UPLOAD"
    popd
}

main() {
    setup
    pushd /work/project
        echo "-- ROLE: $role --"

        python3 -m manager -a manager -n ${role}  -i ${addr} -p ${port} -s schemas/docker.json
        upload

        bash
    popd
}

main
