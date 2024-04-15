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
    default     = ["manager", "receiver", "sender"]
}

provider "docker" {}

resource "docker_image" "ubuntu-ma-instance" {
    name = "ubuntu-ma-instance:jammy"
    build {
        context = "."
        tag     = ["ubuntu-ma-instance:jammy"]
    }
    keep_locally = false
}

resource "docker_container" "ubuntu" {
    count = length(var.names)

    name  = var.names[count.index]
    image = docker_image.ubuntu-ma-instance.name

    network_mode = "host"

    entrypoint = ["/bin/bash", "/entry.sh", var.names[count.index], "8081"]

    rm         = true
    tty        = true
    stdin_open = true
}
