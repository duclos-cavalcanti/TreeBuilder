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
                        --command="sudo journalctl -u google-startup-scripts.service"
}

glogf() {
    [ -z $1 ] && INSTANCE="recipient-dev" || INSTANCE="$1"
    glog ${INSTANCE} > LOG.TXT
}

groot() {
    [ -z $1 ] && INSTANCE="recipient-dev" || INSTANCE="$1"
    gcloud compute ssh "root@${INSTANCE}" --zone "us-east4-c" --project "multicast1" -- "cd /home/uab2005; bash"
}
