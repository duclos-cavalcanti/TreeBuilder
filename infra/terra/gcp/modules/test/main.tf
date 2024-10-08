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

resource "google_compute_instance" "instance" {
    name         = "treefinder"
    machine_type = var.machine
    zone         = "us-east4-c"

    tags = ["test"]

    metadata = {
        "enable-oslogin" = "TRUE"
        "startup-script" = templatefile("${path.cwd}/modules/test/scripts/start.sh", {
            ROLE         = "TEST",
            CLOUD        = "GCP",
            IP_ADDR      = "10.1.255.245",
            BUCKET       = var.bucket
        })
    }

    network_interface {
        network     = data.google_compute_network.multicast-management.name
        subnetwork  = data.google_compute_subnetwork.multicast-management-subnet.name
        network_ip  = "10.1.255.245"
        nic_type    = "GVNIC"
        stack_type  = "IPV4_ONLY"
    }

    network_interface {
        network     = data.google_compute_network.multicast-service.name
        subnetwork  = data.google_compute_subnetwork.multicast-service-subnet.name
        network_ip  = "10.0.255.245"
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
