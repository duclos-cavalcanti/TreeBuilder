variable "commands" {
    description = "Commands to build image"
    type        = list(string)
    default = [
        "/bin/bash -c 'apt-get update'",
        "/bin/bash -c 'apt-get install -yq curl wget cmake build-essential python3 python3-pip git'",
        "/bin/bash -c 'apt-get install libprotobuf-c-dev libprotobuf-dev protobuf-compiler protobuf-codegen  -yq'",
        "/bin/bash -c 'mkdir /work'",
        "/bin/bash -c 'mkdir /work/project'",
        # https://github.com/zeromq/cppzmq
        "/bin/bash -c 'cd /work && git clone https://github.com/zeromq/libzmq.git'",
        "/bin/bash -c 'cd /work/libzmq && mkdir build && cd build && cmake .. && make -j4 install'",
        "/bin/bash -c 'cd /work && git clone https://github.com/zeromq/cppzmq.git'",
        "/bin/bash -c 'cd /work/cppzmq && mkdir build && cd build && cmake .. && make -j4 install'",
    ]
}
