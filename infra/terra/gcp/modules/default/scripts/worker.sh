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

sleep 1s

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

main() {
    sleep 1s

    setup
    ttcs

    pushd /work/project
        echo "-- ROLE: $ROLE --"

        python3 -m manager -a worker -n $ROLE  -i $IP_ADDR -p $PORT

        bash
    popd
}

main
