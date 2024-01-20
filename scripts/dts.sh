#!/bin/bash 

err() {
    echo -e "${1}"
    exit 1
}

usage() {
    local string=" USAGE: ${0} <action>\nactions: create, deploy, delete"
    err "${string}"
}

main() {
    local action="$1"
    local dir=$(basename $(pwd))
    if [ -d "./dom-tenant-service" ]; then 
        pushd dom-tenant-service
            pushd gcp-deploy
                case $action in
                    create)
                        python3 run.py create-template -r 10 -p 3 -b 2 -c 1 -rm dpdk -dm standard -conf 0
                        ;;

                    deploy)
                        python3 run.py deploy-stack
                        ;;

                    delete)
                        python3 run.py delete-stack
                        ;;
                    *)
                        err "INVALID OPTION: ${action}"
                        ;;
                esac
            popd
        popd
    else 
        err "Incorrect base directory: ${dir}"
    fi
}

[ -z "${1}" ] &&  usage
main $@
