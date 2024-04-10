variable "commands" {
    description = "Commands to build image"
    type        = list(string)
    default = [
        # dependencies
        "/bin/bash -c 'apt-get update'",
        # cmake, git, make, python and utils
        "/bin/bash -c 'apt-get install -yq curl wget cmake build-essential python3 python3-pip git'",
        # google's protobuf
        "/bin/bash -c 'apt-get install -yq libprotobuf-c-dev libprotobuf-dev protobuf-compiler protobuf-codegen'",
        # pkg-config
        "/bin/bash -c 'apt-get install -yq pkg-config'",
        # project
        "/bin/bash -c 'mkdir -p /work/project'",
        "/bin/bash -c 'tar -xzvf /home/project.tar.gz -C /work/project'",
        # https://github.com/zeromq/cppzmq
        "/bin/bash -c 'cd /work && git clone https://github.com/zeromq/libzmq.git'",
        "/bin/bash -c 'cd /work/libzmq && mkdir build && cd build && cmake -DENABLE_DRAFTS=ON .. && make -j4 install'",
        "/bin/bash -c 'cd /work && git clone https://github.com/zeromq/cppzmq.git'",
        "/bin/bash -c 'cd /work/cppzmq && mkdir build && cd build && cmake .. && make -j4 install'",
    ]
}
