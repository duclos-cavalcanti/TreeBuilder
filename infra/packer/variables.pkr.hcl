commands = [
    "sudo apt-get update  -yq",
    "sudo apt-get install -yq curl wget cmake build-essential python3 python3-pip git vim gdb",
    "sudo apt-get install -yq telnet ethtool net-tools netcat inetutils-traceroute tcpdump inetutils-ping iproute2",
    "sudo apt-get install -yq libprotobuf-c-dev libprotobuf-dev protobuf-compiler",
    "sudo apt-get install -yq libbpf-dev",
    "sudo apt-get install -yq pkg-config",
    "sudo mkdir /work",
    "cd /work && sudo git clone https://github.com/zeromq/libzmq.git",
    "sudo mkdir /work/libzmq/build",
    "cd /work/libzmq/build && sudo cmake -DENABLE_DRAFTS=ON ..",
    "cd /work/libzmq/build && sudo make install",
    "cd /work && sudo git clone https://github.com/zeromq/cppzmq.git",
    "sudo mkdir /work/cppzmq/build",
    "cd /work/cppzmq/build && sudo cmake ..",
    "cd /work/cppzmq/build && sudo make install",
    "cd /work && sudo git clone https://github.com/axboe/liburing.git",
    "cd /work/liburing && sudo ./configure --cc=gcc --cxx=g++",
    "cd /work/liburing && sudo make && sudo make install",
    "sudo pip install pyelftools meson",
    "sudo apt-get install build-essential ninja-build pkg-config libnuma-dev pciutils -yq",
    "sudo apt-get install linux-image-$(uname -r) -y",
    "sudo apt-get install linux-headers-$(uname -r) -y",
    "cd /work && sudo wget https://fast.dpdk.org/rel/dpdk-23.07.tar.xz",
    "cd /work && sudo tar xvf dpdk-23.07.tar.xz",
    "cd /work/dpdk-23.07 && sudo meson setup build && sudo ninja -C build install",
    "export RTE_SDK=/work/dpdk-23.07",
    "sudo pip install pyzmq",
    "sudo ldconfig",
]
