#!/bin/bash -xe

ROLE=${ROLE}
CLOUD=${CLOUD}
BUCKET=${BUCKET}
IP_ADDR=${IP_ADDR}
PORT=${PORT}

echo "---- STARTUP ------"
echo "ROLE: $ROLE"
echo "CLOUD: $CLOUD"
echo "BUCKET: $BUCKET"
echo "IP_ADDR: $IP_ADDR"

setup() {
    mkdir -p /work/logs
    mkdir -p /work/project

    echo "EXTRACTING PROJECT"
    pushd /work
        gcloud storage cp gs://$BUCKET/project.tar.gz .
        tar -xzf project.tar.gz -C /work/project
    popd

    echo "COMPILING BINARIES"
    mkdir /work/project/build
    pushd /work/project/build
        cmake ..
        make
    popd
}

ttcs() {
    echo "DEPLOYING TTCS"
    pushd project/tools/ttcs
        chmod +x ./deploy_ttcs.sh
        ./deploy_ttcs.sh ./ttcs-agent.cfg $IP_ADDR
    popd
}

upload() {
    local TS=$(date +"%m-%d-%H:%M:%S")
    local RESULTS="exp-results-nyu-systems-multicast"
    local FOLDER="treefinder-$CLOUD-$TS/results.tar.gz"
    pushd /work 
        echo "COMPRESSING LOGS"
        tar -zcvf results.tar.gz ./logs
        gcloud storage cp results.tar.gz "gs://$RESULTS/$FOLDER/results.tar.gz"
        gcloud storage cp project/schemas/default.json "gs://$RESULTS/$FOLDER/default.json"
        echo "FINISHED UPLOAD"
    popd
}

main() {
    sleep 1s

    setup
    ttcs

    pushd /work/project
        echo "-- ROLE: $ROLE --"

        echo python3 -m manager -a manager -n $ROLE  -i $IP_ADDR -p $PORT
        upload

        bash
    popd
}

main
