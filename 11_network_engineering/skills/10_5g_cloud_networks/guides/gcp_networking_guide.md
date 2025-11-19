# GCP Networking Guide

## GCP VPC Design

### Network Architecture

```
Organization
└── Project: prod-project
    └── VPC: prod-vpc
        ├── Subnet: web-subnet (us-central1) - 10.0.1.0/24
        ├── Subnet: app-subnet (us-central1) - 10.0.2.0/24
        ├── Subnet: db-subnet (us-central1) - 10.0.3.0/24
        ├── Cloud Router: prod-router
        └── Firewall Rules
```

### IP Address Planning

```
Custom VPC: 10.0.0.0/16 (65,536 addresses)
├── Web Tier: 10.0.1.0/24 (256 addresses)
├── App Tier: 10.0.2.0/23 (512 addresses)
├── DB Tier: 10.0.4.0/24 (256 addresses)
├── Secondary IP Ranges: 10.0.100.0/20
└── Reserved: 10.1.0.0/16
```

## Step 1: Create VPC using Terraform

```hcl
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

resource "google_compute_network" "prod_vpc" {
  name                    = "prod-vpc"
  auto_create_subnetworks = false

  depends_on = [google_project_service.compute]
}

# Enable required APIs
resource "google_project_service" "compute" {
  project = var.gcp_project_id
  service = "compute.googleapis.com"
}
```

## Step 2: Create Subnets

```hcl
resource "google_compute_subnetwork" "web" {
  name          = "web-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = "us-central1"
  network       = google_compute_network.prod_vpc.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.4.0.0/14"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.0.32.0/20"
  }

  private_ip_google_access = true
  flow_logs_config {
    enable        = true
    sampling_rate = 0.5
    metadata      = "INCLUDE_ALL_METADATA"
  }
}

resource "google_compute_subnetwork" "app" {
  name          = "app-subnet"
  ip_cidr_range = "10.0.2.0/24"
  region        = "us-central1"
  network       = google_compute_network.prod_vpc.id

  private_ip_google_access = true
}

resource "google_compute_subnetwork" "db" {
  name          = "db-subnet"
  ip_cidr_range = "10.0.4.0/24"
  region        = "us-central1"
  network       = google_compute_network.prod_vpc.id

  private_ip_google_access = true
}
```

## Step 3: Firewall Rules

### Web Firewall Rules

```hcl
resource "google_compute_firewall" "allow_http" {
  name      = "allow-http"
  network   = google_compute_network.prod_vpc.name
  direction = "INGRESS"
  priority  = 1000

  allow {
    protocol = "tcp"
    ports    = ["80"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["web-server"]
}

resource "google_compute_firewall" "allow_https" {
  name      = "allow-https"
  network   = google_compute_network.prod_vpc.name
  direction = "INGRESS"
  priority  = 1000

  allow {
    protocol = "tcp"
    ports    = ["443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["web-server"]
}
```

### App Firewall Rules

```hcl
resource "google_compute_firewall" "allow_app" {
  name      = "allow-app"
  network   = google_compute_network.prod_vpc.name
  direction = "INGRESS"
  priority  = 1000

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  source_ranges = ["10.0.1.0/24"]
  target_tags   = ["app-server"]
}
```

### Database Firewall Rules

```hcl
resource "google_compute_firewall" "allow_database" {
  name      = "allow-database"
  network   = google_compute_network.prod_vpc.name
  direction = "INGRESS"
  priority  = 1000

  allow {
    protocol = "tcp"
    ports    = ["5432"]
  }

  source_ranges = ["10.0.2.0/24"]
  target_tags   = ["database"]
}
```

### Default Deny Rules

```hcl
resource "google_compute_firewall" "deny_all" {
  name      = "deny-all"
  network   = google_compute_network.prod_vpc.name
  direction = "INGRESS"
  priority  = 65534

  deny {
    protocol = "all"
  }

  source_ranges = ["0.0.0.0/0"]
}
```

## Step 4: Cloud Router & Cloud NAT

### Cloud Router Setup

```lcl
resource "google_compute_router" "prod_router" {
  name    = "prod-router"
  region  = "us-central1"
  network = google_compute_network.prod_vpc.id

  bgp {
    asn = 64514
  }
}
```

### Cloud NAT Configuration

```hcl
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
```

## Step 5: Cloud VPN

### Cloud VPN Gateway

```hcl
resource "google_compute_vpn_gateway" "prod_vpn" {
  name    = "prod-vpn-gateway"
  network = google_compute_network.prod_vpc.id
  region  = "us-central1"
}

resource "google_compute_address" "vpn_static_ip" {
  name   = "vpn-static-ip"
  region = "us-central1"
}
```

### VPN Tunnel

```hcl
resource "google_compute_vpn_tunnel" "onprem" {
  name          = "onprem-tunnel"
  region        = "us-central1"
  peer_ip       = "203.0.113.1"
  shared_secret = "your-secret-key"
  ike_version   = 2
  vpn_gateway   = google_compute_vpn_gateway.prod_vpn.name

  target_vpn_gateway = google_compute_vpn_gateway.prod_vpn.id

  depends_on = [
    google_compute_forwarding_rule.esp,
    google_compute_forwarding_rule.udp500,
    google_compute_forwarding_rule.udp4500
  ]
}

# Forwarding rules for VPN
resource "google_compute_forwarding_rule" "esp" {
  name        = "vpn-esp"
  ip_protocol = "ESP"
  ip_address  = google_compute_address.vpn_static_ip.address
  target_vpn_gateway = google_compute_vpn_gateway.prod_vpn.id
  region      = "us-central1"
}

resource "google_compute_forwarding_rule" "udp500" {
  name        = "vpn-udp500"
  ip_protocol = "UDP"
  load_balancing_scheme = "EXTERNAL"
  ip_address  = google_compute_address.vpn_static_ip.address
  ports       = ["500"]
  target_vpn_gateway = google_compute_vpn_gateway.prod_vpn.id
  region      = "us-central1"
}
```

### Route Configuration

```hcl
resource "google_compute_route" "onprem" {
  name           = "route-to-onprem"
  dest_range     = "192.168.0.0/16"
  network        = google_compute_network.prod_vpc.name
  next_hop_vpn_tunnel = google_compute_vpn_tunnel.onprem.id
  priority       = 1000
}
```

## Step 6: Cloud Interconnect (VPN Alternative)

### Partner Interconnect

```hcl
resource "google_compute_interconnect_attachment" "prod" {
  name                     = "prod-interconnect"
  type                     = "PARTNER"
  router                   = google_compute_router.prod_router.name
  interconnect             = google_compute_interconnect.prod.self_link
  admin_enabled            = true
  vlan_tag8021q            = 200
  peer_asn                 = 65000
  peer_ip_address          = "10.0.0.1"
  cloud_router_ip_address  = "10.0.0.2"
}

resource "google_compute_router_interface" "prod" {
  name       = "prod-interface"
  router     = google_compute_router.prod_router.name
  region     = "us-central1"
  ip_range   = "10.0.0.2/30"
  interconnect_attachment = google_compute_interconnect_attachment.prod.self_link
}

resource "google_compute_router_peer" "prod" {
  name                      = "prod-peer"
  router                    = google_compute_router.prod_router.name
  region                    = "us-central1"
  peer_asn                  = 65000
  advertised_route_priority = 100
  interface                 = google_compute_router_interface.prod.name
  peer_ip_address           = "10.0.0.1"
}
```

## Step 7: Shared VPC (Multi-Project)

### Host Project Setup

```hcl
resource "google_compute_shared_vpc_host_project" "host" {
  project = google_google_project.host.project_id
}

resource "google_compute_shared_vpc_service_project" "service" {
  host_project    = google_compute_shared_vpc_host_project.host.project
  service_project = google_google_project.service.project_id
}
```

### Shared Subnet Assignment

```hcl
resource "google_compute_subnetwork_iam_binding" "shared_web" {
  subnetwork = google_compute_subnetwork.web.name
  region     = "us-central1"
  role       = "roles/compute.networkUser"

  members = [
    "serviceAccount:${google_service_account.service_project.email}"
  ]
}
```

## Step 8: Cloud DNS

### Private DNS Zone

```hcl
resource "google_dns_managed_zone" "private" {
  name        = "prod-internal"
  dns_name    = "prod.internal."
  description = "Private DNS zone for prod VPC"
  visibility  = "private"

  private_visibility_config {
    networks_list {
      network_url = google_compute_network.prod_vpc.id
    }
  }
}

resource "google_dns_record_set" "api" {
  name         = "api.prod.internal."
  managed_zone = google_dns_managed_zone.private.name
  type         = "A"
  ttl          = 300
  rrdatas      = ["10.0.2.10"]
}
```

## Step 9: Load Balancing

### Network Load Balancer

```hcl
resource "google_compute_backend_service" "app" {
  name            = "app-backend-service"
  health_checks   = [google_compute_health_check.app.id]
  load_balancing_scheme = "INTERNAL"
  region          = "us-central1"
}

resource "google_compute_health_check" "app" {
  name = "app-health-check"

  tcp_health_check {
    port = "8080"
  }
}

resource "google_compute_forwarding_rule" "app" {
  name                  = "app-forwarding-rule"
  load_balancing_scheme = "INTERNAL"
  backend_service       = google_compute_backend_service.app.id
  network               = google_compute_network.prod_vpc.name
  subnetwork            = google_compute_subnetwork.app.name
  all_ports             = true
  region                = "us-central1"
}
```

## Step 10: Monitoring

### VPC Flow Logs Analysis

```hcl
resource "google_logging_project_sink" "vpc_flow_logs" {
  name        = "vpc-flow-logs-sink"
  destination = "bigquery.googleapis.com/projects/${var.gcp_project_id}/datasets/vpc_logs"

  filter = "resource.type=\"gce_subnetwork\" AND logName=~\"projects/[^/]*/logs/compute.googleapis.com\""

  unique_writer_identity = true
}

resource "google_bigquery_dataset" "vpc_logs" {
  dataset_id    = "vpc_logs"
  friendly_name = "VPC Flow Logs"
  location      = "US"

  access {
    role          = "OWNER"
    user_by_email = google_logging_project_sink.vpc_flow_logs.writer_identity
  }
}
```

## Best Practices

- [ ] Use custom VPC (not default)
- [ ] Enable Private Google Access
- [ ] Enable VPC Flow Logs
- [ ] Implement firewall rules (whitelist approach)
- [ ] Use Cloud NAT for private instance internet access
- [ ] Configure Cloud Router for BGP
- [ ] Use Shared VPC for multi-team projects
- [ ] Implement Private DNS for internal names
- [ ] Enable audit logging
- [ ] Monitor network throughput and latency

---

**Last Updated:** 2025-11-19
