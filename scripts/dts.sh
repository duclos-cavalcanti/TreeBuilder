#!/bin/bash 

err() {
    echo -e "${1}"
    exit 1
}

usage() {
    local string=" USAGE: ${0} <action>"
    err "${string}"
}

main() {
    local action="$1"
    local dir=$(basename $(pwd))
    if [ -d "./module" ]; then 
        case $action in
            create)
                pushd module; pushd gcp-deploy
                python3 run.py create-template -r 10 -p 3 -b 2 -c 1 -rm dpdk -dm standard -conf 0
                popd; popd
                ;;
        
            deploy)
                pushd module; pushd gcp-deploy
                python3 run.py deploy-stack
                popd; popd
                ;;
        
            package)
                rm -f dts.tar.gz
                tar -czf dts.tar.gz  --exclude .git -C ./module .
                gcloud storage cp dts.tar.gz gs://cdm-templates-nyu-systems-multicast/bundled_proj.tar.gz
                ;;
        
            delete)
                pushd module; pushd gcp-deploy
                python3 run.py delete-stack
                popd; popd
                ;;
            *)
                err "INVALID OPTION: ${action}"
                ;;
        esac
    else 
        err "Incorrect base directory: $(pwd)\nCouldn't find submodule"
    fi
}

[ -z "${1}" ] &&  usage
main $@
