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

resource "google_compute_network" "treefinder-management" {
    name                    = "treefinder-management"
    auto_create_subnetworks = false
    mtu                     = 1460
}

resource "google_compute_subnetwork" "treefinder-management-subnet" {
    description              = "treefinder-management subnetwork"
    network                  = google_compute_network.treefinder-management.name
    name                     = "treefinder-management-subnet"
    region                   = "us-east4"
    ip_cidr_range            = "10.0.0.0/16"
    stack_type               = "IPV4_ONLY"
    private_ip_google_access = true
}

resource "google_compute_firewall" "allow-ssh-ingress" {
    description = "Allows TCP connections from any source to any instance on the network using port 22."
    name    = "allow-ssh-ingress"
    network = google_compute_network.treefinder-management.name
    priority = 65534

    direction = "INGRESS"

    allow {
        protocol = "tcp"
        ports    = ["22"]
    }

    source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_firewall" "management-internal" {
    name    = "management-internal"
    network = google_compute_network.treefinder-management.name

    direction = "INGRESS"

    allow {
        protocol = "all"
    }

    source_ranges = ["10.0.0.0/16"]

    log_config {
        metadata = "EXCLUDE_ALL_METADATA"
    }
}

resource "google_compute_firewall" "ttcs-multicast-management-ingress" {
    name    = "ttcs-management-internal-ingress"
    network = google_compute_network.treefinder-management.name
    priority = 1000

    direction = "INGRESS"

    allow {
        protocol = "tcp"
        ports    = ["6171", "6176"]
    }

    allow {
        protocol = "udp"
        ports    = ["3190"]
    }

    source_ranges = ["0.0.0.0/0"]

    log_config {
        metadata = "INCLUDE_ALL_METADATA"
    }
}

resource "google_compute_firewall" "ttcs-multicast-management-egress" {
    name    = "ttcs-management-internal-egress"
    network = google_compute_network.treefinder-management.name
    priority = 1000

    direction = "EGRESS"

    allow {
        protocol = "tcp"
        ports    = ["6171", "6176"]
    }

    allow {
        protocol = "udp"
        ports    = ["3190"]
    }

    destination_ranges = ["0.0.0.0/0"]

    log_config {
        metadata = "INCLUDE_ALL_METADATA"
    }
}

resource "google_compute_instance" "instance" {
    name         = "treefinder-test-instance"
    machine_type = var.machine
    zone         = "us-east4-c"

    tags = ["test"]

    metadata = {
        "enable-oslogin" = "TRUE"
        "startup-script" = templatefile("${path.cwd}/modules/test/scripts/start.sh", {
            ROLE         = "TEST",
            CLOUD        = "GCP",
            IP_ADDR      = "10.0.255.245",
            BUCKET       = var.bucket
        })
    }

    network_interface {
        network     = google_compute_network.treefinder-management.name
        subnetwork  = google_compute_subnetwork.treefinder-management-subnet.name
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
