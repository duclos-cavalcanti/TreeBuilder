FROM ubuntu
# inspired from https://github.com/shanakaprageeth/docker-dpdk/tree/master

LABEL RUN docker run -it --name ubuntu-dpdk-build

# install dev packages
RUN apt-get update -yq
RUN apt-get install vim curl build-essential python3 python3-pip git wget -yq
RUN pip install compiledb

# install DPDK packages 
# https://cloud.google.com/compute/docs/networking/use-dpdk#gcloud
RUN apt-get install build-essential ninja-build pkg-config libnuma-dev pciutils -yq
RUN apt-get install linux-image-$(uname -r) -yq
RUN apt-get install linux-headers-$(uname -r) -yq
RUN pip install pyelftools meson

# DPDK
RUN wget https://fast.dpdk.org/rel/dpdk-23.07.tar.xz
RUN tar xvf dpdk-23.07.tar.xz
RUN cd dpdk-23.07 && meson setup -Dexamples=all build && ninja -C build install
RUN ldconfig

# PROTOBUF
RUN apt-get install libprotobuf-c-dev libprotobuf-dev protobuf-compiler protobuf-codegen  -yq

# LIBURING
RUN git clone https://github.com/axboe/liburing.git
RUN cd liburing && ./configure --cc=gcc --cxx=g++
RUN cd liburing && make && make install

# BPF
RUN apt-get install libbpf-dev -yq

RUN mv dpdk*    /root
RUN mv liburing /root
COPY assets/docker/entry.sh /root/entry.sh
RUN chmod +x /root/entry.sh
ENTRYPOINT [ "/root/entry.sh" ]

WORKDIR /root
