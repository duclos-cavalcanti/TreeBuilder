variable "commands" {
    description = "Commands to build image"
    type        = list(string)
    default = [
        "/bin/bash -c 'apt-get update'",
        "/bin/bash -c 'apt-get install -yq cmake curl build-essential python3 python3-pip git wget'",
        "/bin/bash -c 'apt-get install libprotobuf-c-dev libprotobuf-dev protobuf-compiler protobuf-codegen  -yq'",
        "/bin/bash -c 'mkdir /work'",
        "/bin/bash -c 'mkdir /work/project'",
        "/bin/bash -c 'cd /work && git clone https://github.com/zeromq/libzmq.git'",
        "/bin/bash -c 'cd /work && git clone https://github.com/zeromq/cppzmq.git'",
    ]
}
