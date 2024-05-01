terraform {
    required_providers {
        google = {
            source = "hashicorp/google"
            version = "4.51.0"
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
  default     = "default"
}

provider "google" {
    project = "multicast1"
    region  = "us-east4"
    zone    = "us-east4-a"
}

module "default" {
    source = "./modules/default/"
    count = (var.mode == "default") ? 1 : 0
    pwd = var.pwd
}

module "test" {
    source = "./modules/test/"
    count = (var.mode == "test") ? 1 : 0
    pwd = var.pwd
}
