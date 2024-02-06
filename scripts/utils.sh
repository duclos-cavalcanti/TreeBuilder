#!/bin/bash 

check() {
    if ! command -v ${1} &>/dev/null; then
        echo "${1} is not installed!"
        exit 1
    fi
}

check fzf 
check gcloud

gsh_() {
    local INSTANCE=${1}
    local COMMAND=${2}
    gcloud compute ssh "root@${INSTANCE}" --zone "us-east4-c" --project "multicast1" -- "${COMMAND}; bash"
}

gsh() {
    local INSTANCE=$(gcloud compute instances list | tail -n +2 | awk '{print $1}' |  fzf --height 40% --reverse)
    local COMMAND="${1:-cd /home/uab2005}"
    gsh_ ${INSTANCE} ${COMMAND}
}


gcli() {
    local mac="./build/multicast_client -a mac -t 10 -i 0 -s test"
    local run="./build/multicast_client -a messages -t 10 -i 0 -s test"
    local command="ls"
    echo -n "${mac}" | xclip -i -sel clip
    gsh_ client0000 "cd /home/uab2005/dom-tenant-service/src && ${command}"
}

gprox() {
    gsh_ proxy0000 "cd /home/uab2005/dom-tenant-service/src; sudo journalctl -f -u google-startup-scripts.service -o cat"
}

grec() {
    gsh_ recipient0000 "cd /home/uab2005/dom-tenant-service/src; sudo journalctl -f -u google-startup-scripts.service -o cat"
}

gcp() {
    local INSTANCE="${1}"
    local SRC="${2}"
    local DST=${SRC}
    gcloud compute scp "root@${INSTANCE}:/home/uab2005/dom-tenant-service/src/${SRC}" ./${DST} --zone "us-east4-c" --project "multicast1" 
}

glog() {
    local INSTANCE=$(gcloud compute instances list | tail -n +2 | awk '{print $1}' |  fzf --height 40% --reverse)
    [ -n "$INSTANCE" ] || exit 1
    gcloud compute ssh --zone "us-east4-c" \
                        "root@${INSTANCE}" \
                        --project "multicast1" \
                        --command="journalctl -u google-startup-scripts.service -o cat"
}

gcreate() {
    local arg=$1
    ./scripts/module.sh create $arg
}

gdeploy() {
    ./scripts/module.sh deploy
}

gdelete() {
    ./scripts/module.sh delete
}

gsize() {
    ./scripts/module.sh size
}

