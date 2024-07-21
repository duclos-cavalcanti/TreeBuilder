#!/bin/bash -xe

ROLE="${1}"
CLOUD="${2}"
FOLDER="${3}"

TARFILE="$ROLE.tar.gz"

echo "ROLE: $ROLE"
echo "CLOUD: $CLOUD"
echo "SUFFIX: $ROLE"
echo "TARFILE: $TARFILE"
echo "FOLDER: $FOLDER"

pushd /work
    echo "COMPRESSING"
    tar -zcvf $TARFILE ./logs

    echo "UPLOADING"
    gcloud storage cp $TARFILE "gs://exp-results-nyu-systems-multicast/${FOLDER}/"

    echo "FINISHED"
popd
