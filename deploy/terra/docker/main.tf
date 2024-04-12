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
    default     = ["receiver", "sender", "manager"]
}

provider "docker" {}

resource "docker_container" "ubuntu" {
    count = length(var.names)

    name  = var.names[count.index]
    image = "ubuntu-ma-instance:jammy"

    network_mode = "host"

    entrypoint = ["/bin/bash", "/entry.sh", var.names[count.index]]

    rm         = true
    tty        = true
    stdin_open = true
}
