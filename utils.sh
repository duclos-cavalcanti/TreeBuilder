#!/bin/bash 

gsh() {
    [ -z $1 ] && INSTANCE="recipient-dev" || INSTANCE="$1"
    gcloud compute ssh --zone "us-east4-c" "${INSTANCE}" --project "multicast1"
}

gjn() {
    [ -z $1 ] && INSTANCE="recipient-dev" || INSTANCE="$1"
    gcloud compute ssh --zone "us-east4-c" \
                        "${INSTANCE}" \
                        --project "multicast1" \
                        --command="sudo journalctl -u google-startup-scripts.service"
}

glog() {
    [ -z $1 ] && INSTANCE="recipient-dev" || INSTANCE="$1"
    gjn ${INSTANCE} > LOG.TXT
}
