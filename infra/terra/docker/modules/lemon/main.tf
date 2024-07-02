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

variable "commands" {
    description = "List of commands to run"
    type        = list(string)
    default     = ["echo hi"]
}

resource "docker_container" "nodes" {
    count = length(var.commands)
    name  = "node${count.index}"
    image = "ubuntu-base:jammy"

    volumes {
        host_path = "${path.cwd}/modules/default/volume/"
        container_path = "/work/logs"
        # volume_name    = docker_volume.shared_volume.name
    }

    upload {
        file = "/node.sh"
        source = "${path.cwd}/modules/lemon/scripts/node.sh"
        executable = true
    }

    upload {
        file = "/work/project.tar.gz"
        source = "${path.cwd}/extract/project.tar.gz"
        executable = false
    }

    networks_advanced {
        name         = docker_network.custom_network.name
        ipv4_address = var.addrs[count.index]
    }

    entrypoint = [ "/bin/bash", "/node.sh", "node${count.index}", count.index, var.commands[count.index]]

    privileged = true
    rm         = true
    tty        = true
    stdin_open = true
}
