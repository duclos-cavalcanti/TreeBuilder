terraform {
    required_providers {
        docker = {
            source = "kreuzwerker/docker"
            version = "~> 3.0.1"
        }
    }
}

variable "names" {
    description = "List of container names"
    type        = list(string)
    default     = ["manager", "worker1", "worker2"]
}

variable "ports" {
    description = "List of ports"
    type        = list(string)
    default     = ["9091", "9092", "9093"]
}

variable "entryscripts" {
    description = "List of container's entryscripts"
    type        = list(string)
    default     = ["manager.sh", "worker.sh", "worker.sh"]
}

variable "pwd" {
    description = "Path to present working directory"
    type        = string
    default     = "/path"
}

provider "docker" {}

resource "docker_volume" "shared_volume" {
    name = "shared_volume"
}

resource "docker_container" "ubuntu" {
    count = length(var.names)

    name  = var.names[count.index]
    image = "ubuntu-base:jammy"

    volumes {
        host_path = "${var.pwd}/volume/"
        container_path = "/volume"
        volume_name    = docker_volume.shared_volume.name
    }

    upload {
        file = "/${var.entryscripts[count.index]}"
        source = "${var.pwd}/scripts/${var.entryscripts[count.index]}"
        executable = true
    }

    upload {
        file = "/work/project.tar.gz"
        source = "${var.pwd}/extract/project.tar.gz"
        executable = false
    }

    network_mode = "host"

    entrypoint = ["/bin/bash", "/${var.entryscripts[count.index]}", var.names[count.index], "localhost", var.ports[count.index], count.index]

    rm         = true
    tty        = true
    stdin_open = true
}
