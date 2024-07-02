packer {
    required_plugins {
        docker = {
            version = ">= 1.0.8"
            source = "github.com/hashicorp/docker"
        }
    }
}

variable "commands" {
    description = "Commands to build image"
    type        = list(string)
}

variable "name" {
    type    = string
    default = "ubuntu-base"
}

variable "source" {
    type    = string
    default = "ubuntu:jammy"
}

source "docker" "ubuntu" {
    image  = var.source
    commit = true
}

build {
    name = var.name
    sources = ["source.docker.ubuntu"]

    provisioner "shell" {
        inline = [ 
            "apt-get update && apt-get install -y sudo"
        ]
    }

    provisioner "shell" {
        environment_vars = [
            "DEBIAN_FRONTEND=noninteractive",
        ]
        inline = var.commands
    }

    post-processor "docker-tag" {
        repository = "ubuntu-base"
        tags       = ["jammy"]
    }
}
