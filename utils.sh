#!/bin/bash 

check() {
    if ! command -v ${1} &>/dev/null; then
        echo "${1} is not installed!"
        exit 1
    fi
}

check fzf 
check gcloud

glog() {
    local INSTANCE=$(gcloud compute instances list | tail -n +2 | awk '{print $1}' |  fzf --height 40% --reverse)
    gcloud compute ssh --zone "us-east4-c" \
                        "${INSTANCE}" \
                        --project "multicast1" \
                        --command="sudo journalctl -u google-startup-scripts.service" | less
}

gboot() {
    [ -z "$1" ] && INSTANCE="base-dev" || INSTANCE="$1"
    gcloud compute instances reset ${INSTANCE} --zone="us-east4-c"
}

groot() {
    [ -z "$1" ] && INSTANCE="base-dev" || INSTANCE="$1"
    [ -z "$2" ] && COMMAND="cd /home/uab2005" || COMMAND="$2"
    gcloud compute ssh "root@${INSTANCE}" --zone "us-east4-c" --project "multicast1" -- "${COMMAND}; bash"
}

gcli() {
    groot client0000 "cd /home/uab2005/dom-tenant-service/src"
}

gprox() {
    groot proxy0000 "cd /home/uab2005/dom-tenant-service/src; sudo journalctl -f -u google-startup-scripts.service"
}

grec() {
    groot recipient0000 "cd /home/uab2005/dom-tenant-service/src; sudo journalctl -f -u google-startup-scripts.service"
}

gsh() {
    local INSTANCE=${1}
    local COMMAND=${2}
    gcloud compute ssh "root@${INSTANCE}" --zone "us-east4-c" --project "multicast1" -- "${COMMAND}; bash"
}

gsel() {
    local INSTANCE=$(gcloud compute instances list | tail -n +2 | awk '{print $1}' |  fzf --height 40% --reverse)
    [ -z "$1" ] && COMMAND="cd /home/uab2005" || COMMAND="$1"
    gsh ${INSTANCE} ${COMMAND}
}
