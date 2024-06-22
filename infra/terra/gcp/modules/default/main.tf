terraform {
    required_providers {
        google = {
            source = "hashicorp/google"
            version = "4.51.0"
        }
    }
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

variable "addrs" {
    description = "List of ip addresses"
    type        = list(string)
    default     = ["localhost"]
}

variable "port" {
    description = "List of ports"
    type        = number
    default     = 9091
}

variable "saddrs" {
    description = "List of service ip addresses"
    type        = list(string)
    default     = ["localhost"]
}

variable "names" {
    description = "List of node names"
    type        = list(string)
    default     = ["name"]
}

resource "google_storage_bucket" "bucket" {
    name     = var.bucket
    location = "us-east4"
    uniform_bucket_level_access = true
    force_destroy = true

    lifecycle_rule {
        condition {
          age = 365
        }
        action {
          type = "Delete"
        }
    }
}

resource "google_storage_bucket_object" "object" {
    name   = "project.tar.gz"
    source = "./extract/project.tar.gz"
    bucket = google_storage_bucket.bucket.name
}

data "google_compute_network" "multicast-service" {
    name                    = "multicast-service"
}

data "google_compute_network" "multicast-management" {
    name                    = "multicast-management"
}

data "google_compute_subnetwork" "multicast-service-subnet" {
    name                     = "multicast-service"
    region                   = "us-east4"
}

data "google_compute_subnetwork" "multicast-management-subnet" {
    name                     = "multicast-management"
    region                   = "us-east4"
}

resource "google_compute_instance" "manager_instance" {
    name         = "manager"
    machine_type = var.machine
    zone         = "us-east4-c"

    tags = ["manager"]

    metadata = {
        "enable-oslogin" = "TRUE"
        "startup-script" = templatefile("${path.cwd}/modules/default/scripts/manager.sh", {
            ROLE         = var.names[0],
            CLOUD        = "GCP",
            IP_ADDR      = var.addrs[0],
            PORT         = var.port,
            BUCKET       = var.bucket
        })
    }

    provisioner "file" {
        content     = templatefile("${path.cwd}/modules/default/scripts/upload.sh", {
            CLOUD        = "GCP",
        })
        destination = "/work/upload.sh"
    }

    provisioner "remote-exec" {
        inline = [
            "chmod +x /work/upload.sh",
        ]
    }

    network_interface {
        network     = data.google_compute_network.multicast-management.name
        subnetwork  = data.google_compute_subnetwork.multicast-management-subnet.name
        network_ip  = var.addrs[0]
        nic_type    = "GVNIC"
        stack_type  = "IPV4_ONLY"
    }

    network_interface {
        network     = data.google_compute_network.multicast-service.name
        subnetwork  = data.google_compute_subnetwork.multicast-service-subnet.name
        network_ip  = var.saddrs[0]
        nic_type    = "GVNIC"
        stack_type  = "IPV4_ONLY"
    }


    boot_disk {
        auto_delete = true
        initialize_params {
            image = "projects/multicast1/global/images/${var.image}"
        }
    }

    service_account {
        email  = "multicast-service-vm@multicast1.iam.gserviceaccount.com"
        scopes = [
            "https://www.googleapis.com/auth/cloud-platform", 
        ]
    }
}

resource "google_compute_instance" "worker_instance" {
    count = length(var.addrs) - 1
    name  = "worker${count.index}"
    machine_type = var.machine
    zone         = "us-east4-c"

    tags = ["worker"]

    metadata = {
        "enable-oslogin" = "TRUE"
        "startup-script" = templatefile("${path.cwd}/modules/default/scripts/worker.sh", {
            ROLE         = var.names[count.index + 1],
            CLOUD        = "GCP",
            IP_ADDR      = var.addrs[count.index + 1],
            PORT         = var.port,
            BUCKET       = var.bucket
        })
    }

    network_interface {
        network     = data.google_compute_network.multicast-management.name
        subnetwork  = data.google_compute_subnetwork.multicast-management-subnet.name
        network_ip  = var.addrs[count.index + 1]
        nic_type    = "GVNIC"
        stack_type  = "IPV4_ONLY"
    }

    network_interface {
        network     = data.google_compute_network.multicast-service.name
        subnetwork  = data.google_compute_subnetwork.multicast-service-subnet.name
        network_ip  = var.saddrs[count.index + 1]
        nic_type    = "GVNIC"
        stack_type  = "IPV4_ONLY"
    }


    boot_disk {
        auto_delete = true
        initialize_params {
            image = "projects/multicast1/global/images/${var.image}"
        }
    }

    service_account {
        email  = "multicast-service-vm@multicast1.iam.gserviceaccount.com"
        scopes = [
            "https://www.googleapis.com/auth/cloud-platform", 
        ]
    }
}
