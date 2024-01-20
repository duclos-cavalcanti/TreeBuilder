#!/bin/bash 

err() {
    echo "${1}"
    exit 1
}

run() {
    delete="python3 run.py delete-stack"
    switch
}

main() {
    local dir=$(basename $(pwd))
    if [ -d "./dom-tenant-service" ]; then 
        pushd dom-tenant-service
            pushd gcp-deploy
                python3 run.py delete-stack
            popd
        popd
    else 
        err "Incorrect base directory: ${dir}"
    fi
}

main $@
