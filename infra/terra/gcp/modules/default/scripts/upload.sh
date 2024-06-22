#!/bin/bash 

CLOUD=${CLOUD}

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

if [ -d /work/project ]; then 
    upload 
else 
    echo "DIR: /work/project doesn't exist"
fi
