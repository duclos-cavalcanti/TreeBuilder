#!/bin/bash 

CLOUD=aws
DEPLOY="${CLOUD}-deploy"

usage() {
    local string="USAGE: ${0} <action> [ <cloud> ]"
    echo "${string}"
}

main() {
    local action="$1"
    local arg="$2"
    local dir=$(basename $(pwd))
    if [ -d "${DEPLOY}" ]; then 
        case $action in
            create)
                simple="python3 run.py create-template -r 1 -p 1 -b 1 -c 1 -rm dpdk -dm standard -conf 0"
                medium="python3 run.py create-template -r 10 -p 3 -b 2 -c 1 -rm dpdk -dm large -conf 0"
                large="python3 run.py create-template -r 100 -p 11 -b 10 -c 1 -rm dpdk -dm large -conf 0"
                unicast="python3 run.py create-template -r 100 -p 1 -b 100 -c 1 -rm dpdk -dm large -conf 0"
                chain="python3 run.py create-template -r 1 -p 2 -b 1 -c 1 -rm dpdk -dm large -conf 0"
                zmq="python3 run.py create-template -r 8 -p 7 -b 2 -c 1 -rm dpdk -dm large -conf 0"

                [ -z ${arg} ] && arg="simple"
                echo $arg

                command=$(eval "echo \${$arg}")
                pushd ${DEPLOY}
                echo "${command}"
                ${command}
                popd
                ;;
        
            deploy)
                command="python3 run.py deploy-stack -dm large"
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

            lint)
                cpplint --output=sed \
                    --recursive \
                    --exclude src/build \
                    --exclude src/kernel_modules \
                    --exclude src/nlohmann \
                    --exclude include \
                    --exclude src/multicast_receiver/xdp-deduplication.c \
                    --exclude src/multicast_proxy/tc-replication.c \
                    --exclude src/cameron314/readerwriterqueue.h \
                    --exclude src/cameron314/atomicops.h \
                    --exclude test .
                ;;
            *)
                usage
                echo "INVALID ACTION: ${action}"
                exit 1
                ;;
        esac
    else 
        echo "NO DEPLOY DIR"
        exit 1
    fi
}

if [ -z "${1}" ]; then
    usage
    exit 1 
fi

main $@
