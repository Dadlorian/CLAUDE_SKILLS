# GCP Shared VPC Configuration

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.host_project_id
  region  = "us-central1"
}

variable "host_project_id" {
  type = string
}

variable "service_project_ids" {
  type    = list(string)
  default = []
}

# Enable Shared VPC on host project
resource "google_compute_shared_vpc_host_project" "host" {
  project = var.host_project_id

  depends_on = [google_project_service.compute]
}

resource "google_project_service" "compute" {
  project = var.host_project_id
  service = "compute.googleapis.com"
}

# Attach service projects
resource "google_compute_shared_vpc_service_project" "service" {
  for_each = toset(var.service_project_ids)

  host_project    = google_compute_shared_vpc_host_project.host.project
  service_project = each.value
}

# Host VPC Network
resource "google_compute_network" "shared_vpc" {
  name                    = "shared-vpc"
  auto_create_subnetworks = false
  project                 = var.host_project_id
}

# Shared Subnet
resource "google_compute_subnetwork" "shared" {
  name          = "shared-subnet"
  ip_cidr_range = "10.0.0.0/20"
  region        = "us-central1"
  network       = google_compute_network.shared_vpc.id
  project       = var.host_project_id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.4.0.0/14"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.0.32.0/20"
  }

  private_ip_google_access = true
}

# Service Account for service projects
resource "google_service_account" "service_project_sa" {
  for_each = toset(var.service_project_ids)

  account_id   = "shared-vpc-sa"
  display_name = "Shared VPC Service Account"
  project      = each.value
}

# Grant Network User role to service accounts
resource "google_compute_subnetwork_iam_binding" "shared_network_user" {
  for_each = toset(var.service_project_ids)

  subnetwork = google_compute_subnetwork.shared.name
  region     = "us-central1"
  role       = "roles/compute.networkUser"

  members = [
    "serviceAccount:${google_service_account.service_project_sa[each.value].email}"
  ]
}

# Firewall Rules
resource "google_compute_firewall" "shared_allow_internal" {
  name      = "shared-allow-internal"
  network   = google_compute_network.shared_vpc.name
  project   = var.host_project_id

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  source_ranges = ["10.0.0.0/8"]
}

# Cloud Router
resource "google_compute_router" "shared" {
  name    = "shared-vpc-router"
  region  = "us-central1"
  network = google_compute_network.shared_vpc.id
  project = var.host_project_id

  bgp {
    asn = 64514
  }
}

# Outputs
output "shared_vpc_name" {
  value = google_compute_network.shared_vpc.name
}

output "shared_subnet_name" {
  value = google_compute_subnetwork.shared.name
}

output "shared_vpc_id" {
  value = google_compute_network.shared_vpc.id
}

output "router_name" {
  value = google_compute_router.shared.name
}
