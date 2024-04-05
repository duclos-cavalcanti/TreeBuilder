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

build {
    name    = "ubuntu-ma"

    sources = [
      "source.docker.ubuntu"
    ]

    provisioner "shell" {
        inline = var.commands
    }

    post-processor "docker-tag" {
        repository = "ubuntu-ma"
        tags       = ["ubuntu-jammy"]
    }
}

