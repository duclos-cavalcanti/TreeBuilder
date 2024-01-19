#!/bin/bash 

gsh() {
    [ -z $1 ] && INSTANCE="recipient-dev" || INSTANCE="$1"
    gcloud compute ssh --zone "us-east4-c" "${INSTANCE}" --project "multicast1"
}

glog() {
    [ -z $1 ] && INSTANCE="recipient-dev" || INSTANCE="$1"
    gcloud compute ssh --zone "us-east4-c" \
                        "${INSTANCE}" \
                        --project "multicast1" \
                        --command="sudo journalctl -u google-startup-scripts.service" | less
}

glogf() {
    [ -z $1 ] && INSTANCE="recipient-dev" || INSTANCE="$1"
    [ -z $2 ] && LOG="LOG.TXT" || LOG="$2"
    glog ${INSTANCE} > ${LOG}
}

groot() {
    [ -z "$1" ] && INSTANCE="recipient-dev" || INSTANCE="$1"
    [ -z "$2" ] && COMMAND="cd /home/uab2005" || COMMAND="$2"
    gcloud compute ssh "root@${INSTANCE}" --zone "us-east4-c" --project "multicast1" -- "${COMMAND}; bash"
}

gcli() {
    groot client0000 "cd /home/uab2005/dom-tenant-service/src"
}

gprox() {
    groot proxy0000
}

grec() {
    groot recipient0000
}
