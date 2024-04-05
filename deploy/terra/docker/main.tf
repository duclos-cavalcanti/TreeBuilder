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
  name         = "ubuntu_image"
  keep_locally = false
}

resource "docker_container" "nginx" {
  name  = "base"
  image = docker_image.ubuntu_image.image_id
  ports {
    internal = 80
    external = 8000
  }
  command = ["/bin/bash", "-c", "apt-get update && apt-get install -y cmake"]
}
