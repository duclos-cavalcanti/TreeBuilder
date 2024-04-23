provider "google" {
  project = "<YOUR_PROJECT_ID>"
  region  = "us-central1"
}

resource "google_compute_instance" "custom_instance" {
  name         = "custom-instance"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
    }
  }

  metadata_startup_script = file("install_cmake.sh")
}

resource "google_compute_image" "custom_image" {
  name   = "custom-image"
  source_disk = google_compute_instance.custom_instance.boot_disk.0.source
}
