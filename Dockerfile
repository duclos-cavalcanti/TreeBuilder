FROM ubuntu:jammy

# cmake, git, make, python and utils
RUN apt-get update  -yq
RUN apt-get install -yq curl wget cmake build-essential python3 python3-pip git vim gdb
# network utils
RUN apt-get install -yq telnet ethtool net-tools netcat inetutils-traceroute tcpdump inetutils-ping iproute2

# google's protobuf
RUN apt-get install -yq libprotobuf-c-dev libprotobuf-dev protobuf-compiler

# BPF
RUN apt-get install libbpf-dev -yq

# pkg-config
RUN apt-get install -yq pkg-config


RUN mkdir /work

# DPDK
RUN pip install pyelftools meson
RUN apt-get install build-essential ninja-build pkg-config libnuma-dev pciutils -yq
RUN apt-get install linux-image-$(uname -r) -y
RUN apt-get install linux-headers-$(uname -r) -y

RUN cd /work &&  wget https://fast.dpdk.org/rel/dpdk-23.07.tar.xz
RUN cd /work && tar xvf dpdk-23.07.tar.xz
RUN cd /work/dpdk-23.07 && meson setup build && ninja -C build install

ENV RTE_SDK=/work/dpdk-23.07

# https://github.com/zeromq/cppzmq
RUN cd /work && git clone https://github.com/zeromq/libzmq.git
RUN cd /work/libzmq && mkdir build && cd build && cmake -DENABLE_DRAFTS=ON .. && make -j4 install
RUN cd /work && git clone https://github.com/zeromq/cppzmq.git
RUN cd /work/cppzmq && mkdir build && cd build && cmake .. && make -j4 install


# python
RUN pip install pyzmq

# igb_uio module version
# RUN apt install software-properties-common -yq
# RUN add-apt-repository ppa:ubuntu-toolchain-r/test -y
# RUN apt-get update -y
# RUN apt-get install -y gcc-12 g++-12
# RUN cd /work && git clone https://dpdk.org/git/dpdk-kmods
# RUN cd /work/dpdk-kmods/linux/igb_uio && make 
# RUN cd /work/dpdk-kmods/linux/igb_uio depmod && insmod igb_uio.ko

# update global libraries
RUN ldconfig
