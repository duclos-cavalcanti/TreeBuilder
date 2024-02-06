#!/bin/bash 

CLOUD=${2:-aws}
DEPLOY="module/${CLOUD}-deploy"

usage() {
    local string="USAGE: ${0} <action> [ <cloud> ]"
    echo "${string}"
}

main() {
    local action="$1"
    local arg="$2"
    local dir=$(basename $(pwd))
    if [ -d "./module" ]; then 
        case $action in
            create)
                simple="python3 run.py create-template -r 1 -p 1 -b 1 -c 1 -rm dpdk -dm standard -conf 0"
                medium="python3 run.py create-template -r 10 -p 3 -b 2 -c 1 -rm dpdk -dm standard -conf 0"
                large="python3 run.py create-template -r 100 -p 11 -b 10 -c 1 -rm dpdk -dm standard -conf 0"
                unicast="python3 run.py create-template -r 100 -p 1 -b 100 -c 1 -rm dpdk -dm standard -conf 0"
                chain="python3 run.py create-template -r 1 -p 2 -b 1 -c 1 -rm dpdk -dm standard -conf 0"

                [ -z ${arg} ] && arg="simple"
                echo $arg

                command=$(eval "echo \${$arg}")
                pushd ${DEPLOY}
                echo "${command}"
                ${command}
                popd
                ;;
        
            deploy)
                command="python3 run.py deploy-stack"
                pushd ${DEPLOY}
                echo ${command}
                ${command}
                popd
                ;;

            delete)
                command="python3 run.py delete-stack"
                pushd ${DEPLOY}
                echo ${command}
                ${command}
                popd
                ;;
            *)
                usage
                echo "INVALID ACTION: ${action}"
                exit 1
                ;;
        esac
    else 
        echo "NO MODULE DIR"
        exit 1
    fi
}

if [ -z "${1}" ]; then
    usage
    exit 1 
fi

main $@
