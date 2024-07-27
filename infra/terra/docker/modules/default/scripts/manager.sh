#!/bin/bash -xe

role="$1"
addr="$2"
port="$3"
suffix="$4"

export ROLE="$role"
TAR="/work/project.tar.gz"

FOLDER="treefinder-docker-${suffix}"

setup() {
    mkdir -p /work/logs
    mkdir -p /work/project
    mkdir -p /work/results
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
    local TARFILE="${role}.tar.gz"
    pushd /work
        echo "COMPRESSING"
        tar -zcvf ${TARFILE} ./logs
        mv ${TARFILE} /work/results/${FOLDER}/
    popd 
}

main() {
    setup
    pushd /work/project
        echo "-- ROLE: $role --"

        tzone

        mkdir -p /work/results/${FOLDER}
        cp schemas/default.json /work/results/${FOLDER}

        echo python3 -m manager -a manager -n ${role}  -i ${addr} -p ${port} -s schemas/default.json
        time python3 -m manager -a manager -n ${role}  -i ${addr} -p ${port} -s schemas/default.json

        upload
        echo "FOLDER: $FOLDER"

        bash
    popd
}

main
