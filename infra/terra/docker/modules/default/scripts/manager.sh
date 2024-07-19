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

tzone() {
    sudo ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime && echo 'America/New_York' > /etc/timezone
    cat /etc/timezone
}

upload() {
    local TS=$(date +"%m-%d-%H:%M:%S")
    local FOLDER="treefinder-docker-$TS"
    pushd /work 
        echo "COMPRESSING LOGS"
        mv project/schemas/docker.json /work/logs/
        tar -zcvf results.tar.gz ./logs

        echo "MAKING DIR=$FOLDER"
        mkdir /work/logs/$FOLDER

        mv results.tar.gz /work/logs/$FOLDER
        echo "FINISHED UPLOAD"
    popd
}

main() {
    setup
    pushd /work/project
        echo "-- ROLE: $role --"

        tzone

        echo python3 -m manager -a manager -n ${role}  -i ${addr} -p ${port} -s schemas/docker.json
        python3 -m manager -a manager -n ${role}  -i ${addr} -p ${port} -s schemas/docker.json
        upload

        bash
    popd
}

main
