terraform {
    required_providers {
        docker = {
            source = "kreuzwerker/docker"
            version = "~> 3.0.1"
        }
    }
}

resource "docker_network" "custom_network" {
    name = "custom_network"
    ipam_config {
      subnet  = "10.1.1.0/24"
      gateway = "10.1.1.254"
    }
}

variable "addrs" {
    description = "List of ip addresses"
    type        = list(string)
    default     = ["localhost"]
}

variable "port" {
    description = "List of ports"
    type        = number
    default     = 9091
}

variable "names" {
    description = "List of node names"
    type        = list(string)
    default     = ["name"]
}

variable "commands" {
    description = "List of commands to run"
    type        = list(string)
    default     = ["echo hi"]
}

resource "docker_container" "manager" {
    name  = "manager"
    image = "ubuntu-base:jammy"

    volumes {
        host_path = "${path.cwd}/modules/default/volume/"
        container_path = "/work/logs"
        # volume_name    = docker_volume.shared_volume.name
    }

    upload {
        file = "/manager.sh"
        source = "${path.cwd}/modules/lemondrop/scripts/manager.sh"
        executable = true
    }

    upload {
        file = "/work/project.tar.gz"
        source = "${path.cwd}/extract/project.tar.gz"
        executable = false
    }

    networks_advanced {
        name         = docker_network.custom_network.name
        ipv4_address = var.addrs[0]
    }

    entrypoint = ["/bin/bash", "/manager.sh", var.names[0], var.addrs[0], var.port ]

    rm         = true
    tty        = true
    stdin_open = true
}

resource "docker_container" "workers" {
    count = length(var.addrs) - 1
    name  = "worker${count.index}"
    image = "ubuntu-base:jammy"

    volumes {
        host_path = "${path.cwd}/modules/default/volume/"
        container_path = "/work/logs"
        # volume_name    = docker_volume.shared_volume.name
    }

    upload {
        file = "/worker.sh"
        source = "${path.cwd}/modules/lemondrop/scripts/worker.sh"
        executable = true
    }

    upload {
        file = "/work/project.tar.gz"
        source = "${path.cwd}/extract/project.tar.gz"
        executable = false
    }

    networks_advanced {
        name         = docker_network.custom_network.name
        ipv4_address = var.addrs[1 + count.index]
    }

    entrypoint = ["/bin/bash", "/worker.sh", var.names[count.index + 1], var.addrs[count.index + 1], var.port, count.index]

    privileged = true
    rm         = true
    tty        = true
    stdin_open = true
}
