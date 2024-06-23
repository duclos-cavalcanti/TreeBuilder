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
    pushd /work/project/tools/ttcs
        sudo chmod +x ./deploy_ttcs.sh
        sudo ./deploy_ttcs.sh ./ttcs-agent.cfg $IP_ADDR
    popd
}

upload() {
    local TS=$(date +"%m-%d-%H:%M:%S")
    local RESULTS="exp-results-nyu-systems-multicast"
    local FOLDER="treefinder-$CLOUD-$TS/results.tar.gz"
    pushd /work 
        echo "COMPRESSING LOGS"
        mv project/schemas/default.json /work/logs/
        tar -zcvf results.tar.gz ./logs
        gcloud storage cp results.tar.gz "gs://$RESULTS/$FOLDER/results.tar.gz"
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
        # upload
    popd
}

main