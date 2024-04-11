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

variable "exposed_ports" {
  description = "List of port numbers on host machine"
  type        = list(number)
  default     = [8081, 8082, 8083]
}

provider "docker" {}

resource "docker_container" "ubuntu" {
  count = length(var.names)

  name  = var.names[count.index]
  image = "ubuntu-ma-instance:jammy"

  ports {
    internal = var.exposed_ports[count.index]
    external = var.exposed_ports[count.index]
  }

  entrypoint = ["/bin/bash", "/entry.sh", var.names[count.index]]

  rm         = true
  tty        = true
  stdin_open = true
}
