terraform {
    required_providers {
        docker = {
            source = "kreuzwerker/docker"
            version = "~> 3.0.1"
        }
    }
}

variable "pwd" {
    description = "Path to present working directory"
    type        = string
    default     = "/path"
}

variable "ports" {
    description = "List of ports"
    type        = list(string)
    default     = ["8083"]
}

resource "docker_container" "parent" {
    name  = "parent"
    image = "ubuntu-base:jammy"

    upload {
        file = "/parent.sh"
        source = "${var.pwd}/modules/udp/scripts/parent.sh"
        executable = true
    }

    upload {
        file = "/work/project.tar.gz"
        source = "${var.pwd}/extract/project.tar.gz"
        executable = false
    }

    network_mode = "host"

    entrypoint = ["/bin/bash", "/parent.sh", "parent", "localhost", "9091"]

    rm         = true
    tty        = true
    stdin_open = true
}

resource "docker_container" "children" {
    count = length(var.ports)
    name  = "child${count.index}"
    image = "ubuntu-base:jammy"

    upload {
        file = "/child.sh"
        source = "${var.pwd}/modules/udp/scripts/child.sh"
        executable = true
    }

    upload {
        file = "/work/project.tar.gz"
        source = "${var.pwd}/extract/project.tar.gz"
        executable = false
    }

    network_mode = "host"

    entrypoint = ["/bin/bash", "/child.sh", "child${count.index}", "localhost", var.ports[count.index], count.index]

    rm         = true
    tty        = true
    stdin_open = true
}