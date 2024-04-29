packer {
    required_plugins {
        vagrant = {
            version = "~> 1"
            source = "github.com/hashicorp/vagrant"
        }
    }
}

variable "commands" {
    description = "Commands to build image"
    type        = list(string)
}

source "vagrant" "box" {
    source_path  = "ubuntu/jammy64"
    add_force    = true
    communicator = "ssh"
    provider     = "virtualbox"
}

build {
    sources = ["source.vagrant.box"]

    provisioner "shell" {
        environment_vars = [
            "DEBIAN_FRONTEND=noninteractive",
        ]
        inline = var.commands
    }

    post-processor "vagrant" {
        keep_input_artifact = true
        provider_override   = "virtualbox"
    }

    post-processor "shell-local" {
        inline = ["vagrant box add --name ubuntu-base ./output-box/package.box --force"]
    }
}
