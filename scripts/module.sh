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
                pushd module/gcp-deploy
                echo "${command}"
                ${command}
                popd
                ;;
        
            deploy)
                command="python3 run.py deploy-stack"
                pushd module/gcp-deploy
                echo ${command}
                ${command}
                popd
                ;;

            size)
                command="du -ha --time module/gcp-deploy/build"
                echo ${command}
                ${command}
                ;;
        
            restart)
                echo "Deleting..."
                ${0} delete
                sleep 3s
                echo "Deploying..."
                ${0} deploy
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
