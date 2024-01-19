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
    local COMMAND="sudo su; cd /home/uab2005"
    [ -z $1 ] && INSTANCE="recipient-dev" || INSTANCE="$1"
    gcloud compute ssh --zone "us-east4-c" \
                        "${INSTANCE}" \
                        --project "multicast1" \
                        --command="bash -i -c env" -- ${COMMAND}
}
