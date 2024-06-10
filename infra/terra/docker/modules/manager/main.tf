terraform {
    required_providers {
        docker = {
            source = "kreuzwerker/docker"
            version = "~> 3.0.1"
        }
    }
}

variable "yaml" {
    description = "Path to present working directory"
    type        = string
    default     = "./plans/default.yaml"
}

variable "ports" {
    description = "List of ports"
    type        = list(string)
    default     = ["9092", "9093", "9094", "9095", "9096", "9097", "9098", "9099"]
}

resource "docker_container" "manager" {
    name  = "manager"
    image = "ubuntu-base:jammy"

    volumes {
        host_path = "${path.cwd}/modules/manager/volume/"
        container_path = "/work/logs"
        # volume_name    = docker_volume.shared_volume.name
    }

    upload {
        file = "/manager.sh"
        source = "${path.cwd}/modules/manager/scripts/manager.sh"
        executable = true
    }

    upload {
        file = "/work/project.tar.gz"
        source = "${path.cwd}/extract/project.tar.gz"
        executable = false
    }

    network_mode = "host"

    entrypoint = ["/bin/bash", "/manager.sh", "manager", "localhost", "9091", "${var.yaml}" ]

    rm         = true
    tty        = true
    stdin_open = true
}

resource "docker_container" "workers" {
    count = length(var.ports)
    name  = "worker${count.index}"
    image = "ubuntu-base:jammy"

    volumes {
        host_path = "${path.cwd}/modules/manager/volume/"
        container_path = "/work/logs"
        # volume_name    = docker_volume.shared_volume.name
    }

    upload {
        file = "/worker.sh"
        source = "${path.cwd}/modules/manager/scripts/worker.sh"
        executable = true
    }

    upload {
        file = "/work/project.tar.gz"
        source = "${path.cwd}/extract/project.tar.gz"
        executable = false
    }

    network_mode = "host"

    entrypoint = ["/bin/bash", "/worker.sh", "worker${count.index}", "localhost", var.ports[count.index], count.index]

    rm         = true
    tty        = true
    stdin_open = true
}
