resource "google_compute_network" "multicast-service" {
    name                    = "multicast-service"
    auto_create_subnetworks = "true"
    mtu                     = 1460
}

resource "google_compute_network" "multicast-management" {
    name                    = "multicast-management"
    auto_create_subnetworks = "true"
    mtu                     = 1460
}

resource "google_compute_subnetwork" "multicast-service-subnet" {
    description              = "VPC Service-Subnet"
    network                  = google_compute_network.multicast-service.name
    name                     = "multicast-service"
    region                   = "us-east4"
    ip_cidr_range            = "10.0.0.0/16"
    private_ip_google_access = true
}

resource "google_compute_subnetwork" "multicast-management-subnet" {
    description              = "VPC Management-Subnet"
    network                  = google_compute_network.multicast-management.name
    name                     = "multicast-management"
    region                   = "us-east4"
    ip_cidr_range            = "10.1.0.0/16"
    private_ip_google_access = true
}

