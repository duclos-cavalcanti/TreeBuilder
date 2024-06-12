#!/bin/bash -xe

ROLE=${ROLE}
CLOUD=${CLOUD}
BUCKET=${BUCKET}
IP_ADDR=${IP_ADDR}

echo "---- STARTUP ------"
echo "ROLE: $ROLE"
echo "CLOUD: $CLOUD"
echo "BUCKET: $BUCKET"
echo "IP_ADDR: $IP_ADDR"

sleep 1s

mkdir -p /work/logs
mkdir -p /work/project

pushd /work
gcloud storage cp gs://$BUCKET/project.tar.gz .
tar -xzf project.tar.gz -C project

pushd project

pushd tools/ttcs
chmod +x ./deploy_ttcs.sh
./deploy_ttcs.sh ./ttcs-agent.cfg $IP_ADDR
popd
