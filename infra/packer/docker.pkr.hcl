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

source "docker" "ubuntu" {
    image  = "ubuntu:jammy"
    commit = true
}

build {
    name = "ubuntu-base"
    sources = ["source.docker.ubuntu"]

    provisioner "shell" {
        inline = var.commands
    }

    post-processor "docker-tag" {
        repository = "ubuntu-base"
        tags       = ["jammy"]
    }
}