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

resource "docker_container" "root" {
    name  = "root"
    image = "ubuntu-base:jammy"

    upload {
        file = "/parent.sh"
        source = "${path.cwd}/modules/udp/scripts/parent.sh"
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

    entrypoint = ["/bin/bash", "/parent.sh", "parent", var.commands[0]]

    rm         = true
    tty        = true
    stdin_open = true
}

resource "docker_container" "children" {
    count = length(var.commands) - 1
    name  = "child${count.index}"
    image = "ubuntu-base:jammy"

    upload {
        file = "/child.sh"
        source = "${path.cwd}/modules/udp/scripts/child.sh"
        executable = true
    }

    upload {
        file = "/work/project.tar.gz"
        source = "${path.cwd}/extract/project.tar.gz"
        executable = false
    }

    networks_advanced {
        name         = docker_network.custom_network.name
        ipv4_address = var.addrs[count.index + 1]
    }

    entrypoint = [ "/bin/bash", "/child.sh", "child${count.index}", count.index, var.commands[count.index + 1]]

    privileged = true
    rm         = true
    tty        = true
    stdin_open = true
}
