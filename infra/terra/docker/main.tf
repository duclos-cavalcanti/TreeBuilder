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
    default     = ["9092", "9093", "9094", "9095", "9096"]
}

provider "docker" {}

resource "docker_volume" "shared_volume" {
    name = "shared_volume"
}

resource "docker_container" "manager" {
    name  = "manager"
    image = "ubuntu-base:jammy"

    volumes {
        host_path = "${var.pwd}/volume/"
        container_path = "/volume"
        volume_name    = docker_volume.shared_volume.name
    }

    upload {
        file = "/manager.sh"
        source = "${var.pwd}/scripts/manager.sh"
        executable = true
    }

    upload {
        file = "/work/project.tar.gz"
        source = "${var.pwd}/extract/project.tar.gz"
        executable = false
    }

    network_mode = "host"

    entrypoint = ["/bin/bash", "/manager.sh", "manager", "localhost", "9091"]

    rm         = true
    tty        = true
    stdin_open = true
}

resource "docker_container" "workers" {
    count = length(var.ports)
    name  = "worker${count.index}"
    image = "ubuntu-base:jammy"

    volumes {
        host_path = "${var.pwd}/volume/"
        container_path = "/volume"
        volume_name    = docker_volume.shared_volume.name
    }

    upload {
        file = "/worker.sh"
        source = "${var.pwd}/scripts/worker.sh"
        executable = true
    }

    upload {
        file = "/work/project.tar.gz"
        source = "${var.pwd}/extract/project.tar.gz"
        executable = false
    }

    network_mode = "host"

    entrypoint = ["/bin/bash", "/worker.sh", "worker", "localhost", var.ports[count.index], count.index]

    rm         = true
    tty        = true
    stdin_open = true
}
