terraform {
    required_providers {
        google = {
            source = "hashicorp/google"
            version = "4.51.0"
        }
    }
}

variable "mode" {
  description = "Deployment mode."
  type        = string
  default     = "default"
}

variable "machine" {
    description = "Machine Type"
    type        = string
    default     = "e2-standard-4"
}

variable "image" {
    description = "Machine Image"
    type        = string
    default     = "treefinder-image"
}

variable "bucket" {
    description = "Bucket Name"
    type        = string
    default     = "treefinder-nyu-systems"
}

locals {
    data = jsondecode(file("${path.cwd}/data.json"))
}

locals {
    addrs   = local.data.addrs
    saddrs  = local.data.saddrs
    port    = local.data.port
}

provider "google" {
    project = "multicast1"
    region  = "us-east4"
    zone    = "us-east4-a"
}

module "default" {
    source = "./modules/default/"
    count = (var.mode == "default") ? 1 : 0

    image   = var.image
    machine = var.machine
    bucket  = var.bucket
    addrs   = local.addrs
    saddrs  = local.saddrs
    port    = local.port
}

module "test" {
    source = "./modules/test/"
    count  = (var.mode == "test") ? 1 : 0

    image   = var.image
    machine = var.machine
    bucket  = var.bucket
}

module "new" {
    source = "./modules/new/"
    count = (var.mode == "new") ? 1 : 0

    image   = var.image
    machine = var.machine
    bucket  = var.bucket
}
