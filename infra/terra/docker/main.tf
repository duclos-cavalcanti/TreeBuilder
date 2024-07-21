terraform {
    required_providers {
        docker = {
            source = "kreuzwerker/docker"
            version = "~> 3.0.1"
        }
    }
}

locals {
    data = jsondecode(file("${path.cwd}/extract/data.json"))
}

variable "mode" {
    description = "Deployment mode."
    type        = string
    default     = "manager"
}

locals {
    addrs    = local.data.addrs
    port     = local.data.port
    names    = local.data.names
    commands = local.data.commands
    suffix   = local.data.suffix
}

module "default" {
    source  = "./modules/default/"
    count   = (var.mode == "default" || var.mode == "lemondrop") ? 1 : 0

    addrs   = local.addrs
    names   = local.names
    port    = local.port
    suffix  = local.suffix
}

module "udp" {
    source = "./modules/udp/"
    count = (var.mode == "udp") ? 1 : 0

    addrs    = local.addrs
    commands = local.commands
}

module "mcast" {
    source = "./modules/mcast/"
    count = (var.mode == "mcast") ? 1 : 0

    addrs    = local.addrs
    commands = local.commands
}

module "lemon" {
    source = "./modules/lemon/"
    count = (var.mode == "lemon") ? 1 : 0

    addrs    = local.addrs
    commands = local.commands
}
