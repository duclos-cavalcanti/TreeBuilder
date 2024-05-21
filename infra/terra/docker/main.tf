terraform {
    required_providers {
        docker = {
            source = "kreuzwerker/docker"
            version = "~> 3.0.1"
        }
    }
}

variable "pwd" {
    description = "Path to present working directory"
    type        = string
    default     = "/path"
}

variable "mode" {
  description = "Deployment mode."
  type        = string
  default     = "manager"
}

module "manager" {
    source = "./modules/manager/"
    count = (var.mode == "manager") ? 1 : 0
    pwd = var.pwd
}

module "udp" {
    source = "./modules/udp/"
    count = (var.mode == "udp") ? 1 : 0
    pwd = var.pwd
}

module "mcast" {
    source = "./modules/mcast/"
    count = (var.mode == "mcast") ? 1 : 0
    pwd = var.pwd
}
