terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {}

resource "docker_image" "ubuntu" {
    name = "ubuntu-ma"
    keep_locally = false
}

resource "docker_container" "ubuntu" {
    name  = var.name
    image = docker_image.ubuntu.image_id
    ports {
        internal = 80
        external = var.exposed_port
    }
    command = var.commands
}
