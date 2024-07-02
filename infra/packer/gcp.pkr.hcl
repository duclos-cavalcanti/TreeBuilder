packer {
    required_plugins {
        googlecompute = {
          version = ">= 1.1.4"
          source  = "github.com/hashicorp/googlecompute"
        }
    }
}

variable "commands" {
    description = "Commands to build image"
    type        = list(string)
}

variable "name" {
    type    = string
    default = "treefinder-image"
}

variable "source" {
    type    = string
    default = "multicast-ebpf-zmq-grub-disk"
}

source "googlecompute" "ubuntu" {
    project_id                = "multicast1"
    source_image_family       = "ubuntu-2204-lts"
    source_image              = var.source
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
        environment_vars = [
            "DEBIAN_FRONTEND=noninteractive",
        ]
        inline = var.commands
    }
}
