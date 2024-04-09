terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {}

resource "docker_container" "ubuntu" {
    name  = var.name
    image = "ubuntu-ma:ubuntu-jammy"

    ports {
        internal = 80
        external = var.exposed_port
    }

    volumes {
        host_path      = var.pwd
        container_path = "/work/project"
    }

    volumes {
        host_path      = var.entry
        container_path = "/entry.sh"
    }

    entrypoint = ["/bin/bash", "/entry.sh"]

    rm = true
    tty = true
    stdin_open = true
}
