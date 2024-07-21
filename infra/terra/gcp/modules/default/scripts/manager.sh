#!/bin/bash -xe

ROLE=${ROLE}
CLOUD=${CLOUD}
SUFFIX=${SUFFIX}
BUCKET=${BUCKET}
IP_ADDR=${IP_ADDR}
PORT=${PORT}

FOLDER="treefinder-$CLOUD-$SUFFIX"

echo "---- STARTUP ------"
echo "ROLE: $ROLE"
echo "CLOUD: $CLOUD"
echo "BUCKET: $BUCKET"
echo "IP_ADDR: $IP_ADDR"
echo "SUFFIX: $SUFFIX"
echo "FOLDER: $FOLDER"

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

main() {
    sleep 1s

    setup

    echo "FOLDER: $FOLDER"
    gcloud storage cp /work/project/schemas/default.json "gs://exp-results-nyu-systems-multicast/$FOLDER/"

    ttcs

    pushd /work/project
        echo "-- ROLE: $ROLE --"
        echo python3 -m manager -a manager -n $ROLE  -i $IP_ADDR -p $PORT -s schemas/default.json
        echo /work/project/scripts/upload.sh $ROLE $CLOUD $FOLDER
    popd
}

main
