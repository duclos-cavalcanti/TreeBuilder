#!/bin/bash -xe

ROLE=${ROLE}
CLOUD=${CLOUD}
BUCKET=${BUCKET}

echo "---- STARTUP ------"
echo "ROLE: $ROLE"
echo "CLOUD: $CLOUD"

sleep 5s

mkdir -p /work/project
pushd /work
gcloud storage cp gs://$BUCKET/project.tar.gz .
tar -xzf project.tar.gz -C project

ls project
