# GCP VPC Terraform Configuration

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = "us-central1"
}

variable "gcp_project_id" {
  type = string
}

# Create VPC Network
resource "google_compute_network" "prod_vpc" {
  name                    = "prod-vpc"
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"

  depends_on = [google_project_service.compute]
}

# Enable required APIs
resource "google_project_service" "compute" {
  project = var.gcp_project_id
  service = "compute.googleapis.com"
}

# Web Subnet
resource "google_compute_subnetwork" "web" {
  name          = "web-subnet"
  ip_cidr_range = "10.4.1.0/24"
  region        = "us-central1"
  network       = google_compute_network.prod_vpc.id
  private_ip_google_access = true

  flow_logs_config {
    enable        = true
    sampling_rate = 0.5
    metadata      = "INCLUDE_ALL_METADATA"
  }
}

# App Subnet
resource "google_compute_subnetwork" "app" {
  name          = "app-subnet"
  ip_cidr_range = "10.4.2.0/24"
  region        = "us-central1"
  network       = google_compute_network.prod_vpc.id
  private_ip_google_access = true

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.4.64.0/18"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.4.0.0/20"
  }
}

# Database Subnet
resource "google_compute_subnetwork" "database" {
  name          = "database-subnet"
  ip_cidr_range = "10.4.3.0/24"
  region        = "us-central1"
  network       = google_compute_network.prod_vpc.id
  private_ip_google_access = true
}

# Firewall Rules - Allow HTTP
resource "google_compute_firewall" "allow_http" {
  name    = "allow-http"
  network = google_compute_network.prod_vpc.name
  allow {
    protocol = "tcp"
    ports    = ["80"]
  }
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["web-server"]
}

# Firewall Rules - Allow HTTPS
resource "google_compute_firewall" "allow_https" {
  name    = "allow-https"
  network = google_compute_network.prod_vpc.name
  allow {
    protocol = "tcp"
    ports    = ["443"]
  }
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["web-server"]
}

# Firewall Rules - Allow App traffic
resource "google_compute_firewall" "allow_app" {
  name    = "allow-app"
  network = google_compute_network.prod_vpc.name
  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }
  source_ranges = ["10.4.1.0/24"]
  target_tags   = ["app-server"]
}

# Firewall Rules - Allow Database traffic
resource "google_compute_firewall" "allow_database" {
  name    = "allow-database"
  network = google_compute_network.prod_vpc.name
  allow {
    protocol = "tcp"
    ports    = ["5432"]
  }
  source_ranges = ["10.4.2.0/24"]
  target_tags   = ["database"]
}

# Firewall Rules - Deny all
resource "google_compute_firewall" "deny_all" {
  name      = "deny-all"
  network   = google_compute_network.prod_vpc.name
  priority  = 65534
  deny {
    protocol = "all"
  }
  source_ranges = ["0.0.0.0/0"]
}

# Cloud Router
resource "google_compute_router" "prod_router" {
  name    = "prod-router"
  region  = "us-central1"
  network = google_compute_network.prod_vpc.id

  bgp {
    asn = 64514
  }
}

# Cloud NAT
resource "google_compute_router_nat" "prod_nat" {
  name                               = "prod-nat"
  router                             = google_compute_router.prod_router.name
  region                             = google_compute_router.prod_router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Outputs
output "vpc_name" {
  value = google_compute_network.prod_vpc.name
}

output "vpc_id" {
  value = google_compute_network.prod_vpc.id
}

output "web_subnet_name" {
  value = google_compute_subnetwork.web.name
}

output "app_subnet_name" {
  value = google_compute_subnetwork.app.name
}

output "database_subnet_name" {
  value = google_compute_subnetwork.database.name
}

output "router_name" {
  value = google_compute_router.prod_router.name
}
