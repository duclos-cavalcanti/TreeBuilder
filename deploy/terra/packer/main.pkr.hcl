packer {
  required_plugins {
    docker = {
      version = ">= 1.0.8"
      source = "github.com/hashicorp/docker"
    }
  }
}

source "docker" "ubuntu" {
  image  = "ubuntu:jammy"
  commit = true
}

variable "file" {
    description = "Path to project folder bundle that is copied over to the image"
    type        = string
    default     = "path"
}

build {
    name    = "ubuntu-ma"

    sources = [
      "source.docker.ubuntu"
    ]

    provisioner "file" {
        destination = "/home/"
        source      = var.file
    }

    provisioner "shell" {
        inline = var.commands
    }

    post-processor "docker-tag" {
        repository = "ubuntu-ma"
        tags       = ["ubuntu-jammy"]
    }
}

