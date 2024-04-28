packer {
    required_plugins {
        googlecompute = {
          version = ">= 1.1.4"
          source  = "github.com/hashicorp/googlecompute"
        }
    }
}

variable "name" {
    type    = string
    default = "ubuntu-base-disk"
}

variable "commands" {
    description = "Commands to build image"
    type        = list(string)
}

source "googlecompute" "ubuntu" {
    project_id                = "multicast1"
    source_image_family       = "ubuntu-2204-lts"
    zone                      = "us-east4-a"
    disk_size                 = 10
    machine_type              = "e2-standard-4"
    ssh_username              = "root"
    image_name                = var.name
}

build {
    sources = [
        "source.googlecompute.ubuntu"
    ]

    provisioner "shell" {
        inline = var.commands
    }
}
