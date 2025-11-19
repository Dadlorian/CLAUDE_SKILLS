# GCP Cloud Interconnect Configuration

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

variable "customer_bgp_asn" {
  type    = number
  default = 65000
}

# Dedicated Interconnect
resource "google_compute_interconnect" "main" {
  name                  = "main-interconnect"
  interconnect_type     = "DEDICATED"
  requested_link_count  = 2
  link_type             = "LINK_TYPE_ETHERNET_100G"
  location              = "lax-zone1-901"
  admin_enabled         = true

  depends_on = [google_project_service.compute]
}

# Enable Compute API
resource "google_project_service" "compute" {
  project = var.gcp_project_id
  service = "compute.googleapis.com"
}

# Cloud Router
resource "google_compute_router" "interconnect" {
  name    = "interconnect-router"
  region  = "us-central1"
  network = var.vpc_network_id

  bgp {
    asn = 64514
  }
}

# Interconnect Attachment
resource "google_compute_interconnect_attachment" "prod" {
  name             = "prod-attachment"
  type             = "DEDICATED"
  router           = google_compute_router.interconnect.name
  interconnect     = google_compute_interconnect.main.self_link
  vlan_tag8021q    = 200
  candidate_ipv4_subnets = ["169.254.33.0/30"]
  admin_enabled    = true

  depends_on = [google_compute_router.interconnect]
}

# Router Interface
resource "google_compute_router_interface" "interconnect" {
  name                    = "interconnect-interface"
  router                  = google_compute_router.interconnect.name
  region                  = "us-central1"
  ip_range                = "169.254.33.1/30"
  interconnect_attachment = google_compute_interconnect_attachment.prod.self_link
}

# Router BGP Peer
resource "google_compute_router_peer" "interconnect" {
  name             = "interconnect-peer"
  router           = google_compute_router.interconnect.name
  region           = "us-central1"
  peer_asn         = var.customer_bgp_asn
  peer_ip_address  = "169.254.33.2"
  interface        = google_compute_router_interface.interconnect.name
  advertised_route_priority = 100
}

# Route for on-premises network
resource "google_compute_route" "onprem" {
  name             = "route-onprem"
  dest_range       = "10.0.0.0/16"
  network          = var.vpc_network_name
  next_hop_ip      = "169.254.33.2"
  priority         = 1000

  depends_on = [google_compute_router_peer.interconnect]
}

# Outputs
output "interconnect_name" {
  value = google_compute_interconnect.main.name
}

output "interconnect_id" {
  value = google_compute_interconnect.main.id
}

output "attachment_id" {
  value = google_compute_interconnect_attachment.prod.id
}

output "router_name" {
  value = google_compute_router.interconnect.name
}

# Required variables
variable "vpc_network_id" {
  type = string
}

variable "vpc_network_name" {
  type = string
}
