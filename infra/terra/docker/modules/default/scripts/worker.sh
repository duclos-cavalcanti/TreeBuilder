#!/bin/bash -xe

role="$1"
addr="$2"
port="$3"
count=$4
suffix="$5"

export ROLE="$role"
TAR="/work/project.tar.gz"

FOLDER="treefinder-docker-${suffix}"

setup() {
    mkdir -p /work/logs
    mkdir -p /work/project
    mkdir -p /work/results
    tar -xzf ${TAR} -C /work/project

    mkdir /work/project/build
    pushd /work/project/build
        cmake ..
        make
    popd
}

tzone() {
    sudo ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime && echo 'America/New_York' > /etc/timezone
    cat /etc/timezone
}

edelay() {
    dur="$1"
    sudo tc qdisc add dev "eth0" root netem delay ${dur}ms
    echo "SUCCESSFULL EGRESS DELAY: ${dur}ms"
}

idelay() {
    dur="$1"
    sudo ip link add ifb0 type ifb
    sudo ip link set ifb0 up
    sudo tc qdisc add dev eth0 handle ffff: ingress
    sudo tc filter add dev eth0 parent ffff: protocol ip u32 match u32 0 0 action mirred egress redirect dev ifb0
    sudo tc qdisc add dev ifb0 root netem delay ${dur}ms
    echo "SUCCESSFULL INGRESS DELAY: ${dur}ms"
}

idelay_probabilistic() {
    dur="$1"
    stddev="$2"

    sudo ip link add ifb0 type ifb
    sudo ip link set ifb0 up
    sudo tc qdisc add dev eth0 handle ffff: ingress
    sudo tc filter add dev eth0 parent ffff: protocol ip u32 match u32 0 0 action mirred egress redirect dev ifb0
    sudo tc qdisc add dev ifb0 root netem delay ${dur}ms ${stddev}ms distribution normal
    echo "SUCCESSFUL INGRESS DELAY: ${dur}ms ± ${stddev}ms (normal distribution)"
}

upload() {
    local TARFILE="${role}.tar.gz"
    pushd /work
        echo "COMPRESSING"
        tar -zcvf ${TARFILE} ./logs
        mv ${TARFILE} /work/results/${FOLDER}/
    popd 
}

main() {
    setup
    pushd /work/project
        echo "-- ROLE: $role [ ${addr}:${port} ] --"
    
        tzone

        # node0 0
        if [ $count -eq 0 ]; then 
            # make obviously a bad choice
            # 500 us
            idelay 0.3
            edelay 0.3
        else
            # all even numbered nodes

            # slightly worst
            if  (( $count % 2 == 0)); then 
                # delay of 200 us
                if [ $count -gt 12 ]; then
                    idelay 0.4
                fi

            # odd numbered workers
            else
                # greater than 9
                if [ $count -gt 11 ]; then
                    # 400 us delay with 150 us standard deviation
                    idelay_probabilistic 0.4 0.02
                fi
            fi
        fi

        echo python3 -m manager -a worker -n ${role}  -i ${addr} -p ${port} -s schemas/default.json
        python3 -m manager -a worker -n ${role}  -i ${addr} -p ${port} -s schemas/default.json

        upload

        bash
    popd
}

main
