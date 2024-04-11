FROM ubuntu:jammy

# LABEL RUN

# cmake, git, make, python and utils
RUN apt-get update  -yq
RUN apt-get install -yq curl wget cmake build-essential python3 python3-pip git vim gdb
# network utils
RUN apt-get install -yq telnet ethtool net-tools netcat inetutils-traceroute tcpdump inetutils-ping

# google's protobuf
RUN apt-get install -yq libprotobuf-c-dev libprotobuf-dev protobuf-compiler protobuf-codegen

# pkg-config
RUN apt-get install -yq pkg-config

# project
RUN mkdir -p /work/project

# https://github.com/zeromq/cppzmq
RUN cd /work && git clone https://github.com/zeromq/libzmq.git
RUN cd /work/libzmq && mkdir build && cd build && cmake -DENABLE_DRAFTS=ON .. && make -j4 install
RUN cd /work && git clone https://github.com/zeromq/cppzmq.git
RUN cd /work/cppzmq && mkdir build && cd build && cmake .. && make -j4 install

# update global libraries
RUN ldconfig
