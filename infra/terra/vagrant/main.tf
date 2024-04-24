terraform {
    required_providers {
        vagrant = {
            source  = "bmatcuk/vagrant"
            version = "~> 4.0.0"
        }
    }
}

variable "pwd" {
    description = "Path to present working directory"
    type        = string
    default     = "/path"
}

resource "vagrant_vm" "virtualboxes" {
    vagrantfile_dir = "."
    get_ports = true
}

