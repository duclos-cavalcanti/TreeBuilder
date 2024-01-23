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
                large="python3 run.py create-template -r 100 -p 11 -b 10 -c 1 -rm dpdk -dm standard -conf 0"
                medium="python3 run.py create-template -r 10 -p 3 -b 2 -c 1 -rm dpdk -dm standard -conf 0"
                simple="python3 run.py create-template -r 1 -p 1 -b 1 -c 1 -rm dpdk -dm standard -conf 0"
                pushd module/gcp-deploy
                echo ${simple}
                ${simple}
                popd
                ;;
        
            deploy)
                command="python3 run.py deploy-stack"
                pushd module/gcp-deploy
                echo ${command}
                ${command}
                popd
                ;;
        
            package)
                rm -f dts.tar.gz
                tar -czf dts.tar.gz  --exclude .git -C ./module .
                gcloud storage cp dts.tar.gz gs://cdm-templates-nyu-systems-multicast/bundled_proj.tar.gz
                ;;
        
            delete)
                command="python3 run.py delete-stack"
                pushd module; pushd gcp-deploy
                echo ${command}
                ${command}
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
