#!/bin/bash -xe

role="$1"
addr="$2"
port="$3"
id="$4"

export ROLE="$role"

TAR="/work/project.tar.gz"
mkdir /work/project
tar -xzf ${TAR} -C /work/project

mkdir /work/project/build
pushd /work/project/build
    echo "-- ROLE: $role [ $id ] --"
    ls
    cmake ..
    make
    bash
popd
