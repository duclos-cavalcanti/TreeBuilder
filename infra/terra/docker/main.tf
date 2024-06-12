terraform {
    required_providers {
        docker = {
            source = "kreuzwerker/docker"
            version = "~> 3.0.1"
        }
    }
}

locals {
    data = jsondecode(file("${path.cwd}/data.json"))
}

variable "mode" {
    description = "Deployment mode."
    type        = string
    default     = "manager"
}

locals {
    addrs = local.data.addrs
    port  = local.data.port
}

module "default" {
    source  = "./modules/default/"
    count   = (var.mode == "default") ? 1 : 0
    addrs   = local.addrs
    port    = local.port
}

module "udp" {
    source = "./modules/udp/"
    count = (var.mode == "udp") ? 1 : 0
}

module "mcast" {
    source = "./modules/mcast/"
    count = (var.mode == "mcast") ? 1 : 0
}
