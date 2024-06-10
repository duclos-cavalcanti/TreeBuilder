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
    default     = "ubuntu-base-disk"
}

variable "bucket" {
    description = "Bucket Name"
    type        = string
    default     = "treedrop-nyu-systems"
}

resource "google_storage_bucket" "bucket" {
    name     = var.bucket
    location = "us-east4"
    uniform_bucket_level_access = true

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

# resource "google_compute_network" "multicast-service" {
#     name                    = "multicast-service"
#     auto_create_subnetworks = "true"
#     mtu                     = 1460
# }
# 
# resource "google_compute_network" "multicast-management" {
#     name                    = "multicast-management"
#     auto_create_subnetworks = "true"
#     mtu                     = 1460
# }
# 
# resource "google_compute_subnetwork" "multicast-service-subnet" {
#     description              = "VPC Service-Subnet"
#     network                  = google_compute_network.multicast-service.name
#     name                     = "multicast-service"
#     region                   = "us-east4"
#     ip_cidr_range            = "10.0.0.0/16"
#     private_ip_google_access = true
# }
# 
# resource "google_compute_subnetwork" "multicast-management-subnet" {
#     description              = "VPC Management-Subnet"
#     network                  = google_compute_network.multicast-management.name
#     name                     = "multicast-management"
#     region                   = "us-east4"
#     ip_cidr_range            = "10.1.0.0/16"
#     private_ip_google_access = true
# }


resource "google_compute_instance" "custom_instance" {
    name         = "ubuntu-test-instance"
    machine_type = var.machine
    zone         = "us-east4-c"

    tags = ["test"]

    metadata = {
        "enable-oslogin" = "TRUE"
        "startup-script" = templatefile("${path.cwd}/modules/jasper/scripts/start.sh", {
            ROLE         = "TEST",
            CLOUD        = "GCP",
            BUCKET       = var.bucket
        })
    }

    network_interface {
        network     = data.google_compute_network.multicast-management.name
        subnetwork  = data.google_compute_subnetwork.multicast-management-subnet.name
        network_ip  = "10.1.1.0"
        nic_type    = "GVNIC"
        stack_type  = "IPV4_ONLY"
    }

    network_interface {
        network     = data.google_compute_network.multicast-service.name
        subnetwork  = data.google_compute_subnetwork.multicast-service-subnet.name
        network_ip  = "10.0.1.0"
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
