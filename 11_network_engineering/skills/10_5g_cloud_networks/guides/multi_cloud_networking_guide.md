# Multi-Cloud Networking Guide

## Multi-Cloud Strategy Design

### Network Topology Selection

**Hub-and-Spoke:**
```
AWS VPC
    \
     \---> On-Premises / Central Hub <---/ Azure VNet
    /
GCP VPC
```

**Full Mesh:**
```
AWS VPC <---> Azure VNet
  ^               ^
  |               |
  +----> GCP VPC <+
```

## Step 1: Design Multi-Cloud Network

### Terraform Multi-Cloud Setup

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

# AWS Provider
provider "aws" {
  region = "us-east-1"
}

# Azure Provider
provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
}

# GCP Provider
provider "google" {
  project = var.gcp_project_id
  region  = "us-central1"
}
```

## Step 2: AWS Multi-Region Setup

### AWS VPC Configuration

```hcl
# US-East VPC
resource "aws_vpc" "us_east" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name   = "us-east-vpc"
    Region = "us-east-1"
  }
}

# EU-West VPC
resource "aws_vpc" "eu_west" {
  provider             = aws.eu_west
  cidr_block           = "10.1.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name   = "eu-west-vpc"
    Region = "eu-west-1"
  }
}

# AWS Transit Gateway for inter-region connectivity
resource "aws_ec2_transit_gateway" "main" {
  description                    = "Multi-region Transit Gateway"
  default_route_table_association = "enable"
  default_route_table_propagation = "enable"

  tags = {
    Name = "prod-tgw"
  }
}

# TGW Attachments
resource "aws_ec2_transit_gateway_vpc_attachment" "us_east" {
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  vpc_id             = aws_vpc.us_east.id
  subnet_ids         = [aws_subnet.us_east_private.id]

  tags = {
    Name = "tgw-us-east"
  }
}

resource "aws_ec2_transit_gateway_vpc_attachment" "eu_west" {
  provider           = aws.eu_west
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  vpc_id             = aws_vpc.eu_west.id
  subnet_ids         = [aws_subnet.eu_west_private.id]

  tags = {
    Name = "tgw-eu-west"
  }
}
```

## Step 3: Azure Multi-Region Setup

### Azure VNet Configuration

```hcl
# US East VNet
resource "azurerm_virtual_network" "us_east" {
  name                = "us-east-vnet"
  address_space       = ["10.2.0.0/16"]
  location            = "East US"
  resource_group_name = azurerm_resource_group.us_east.name
}

# EU West VNet
resource "azurerm_virtual_network" "eu_west" {
  provider            = azurerm.eu
  name                = "eu-west-vnet"
  address_space       = ["10.3.0.0/16"]
  location            = "West Europe"
  resource_group_name = azurerm_resource_group.eu_west.name
}

# Virtual WAN for multi-region connectivity
resource "azurerm_virtual_wan" "main" {
  name                = "prod-vwan"
  resource_group_name = azurerm_resource_group.main.name
  location            = "East US"
}

# Virtual Hub
resource "azurerm_virtual_hub" "us_east" {
  name                = "hub-us-east"
  resource_group_name = azurerm_resource_group.main.name
  location            = "East US"
  virtual_wan_id      = azurerm_virtual_wan.main.id
  address_prefix      = "10.10.0.0/23"
}

resource "azurerm_virtual_hub" "eu_west" {
  name                = "hub-eu-west"
  resource_group_name = azurerm_resource_group.main.name
  location            = "West Europe"
  virtual_wan_id      = azurerm_virtual_wan.main.id
  address_prefix      = "10.11.0.0/23"
}

# Hub connection
resource "azurerm_virtual_hub_connection" "us_east" {
  name                      = "vnet-connection-us-east"
  virtual_hub_id            = azurerm_virtual_hub.us_east.id
  remote_virtual_network_id = azurerm_virtual_network.us_east.id
  internet_security_enabled = true
}
```

## Step 4: GCP Multi-Region Setup

### GCP VPC and Routing

```hcl
# Global VPC
resource "google_compute_network" "prod_vpc" {
  name                    = "prod-vpc"
  auto_create_subnetworks = false
}

# US-Central Subnet
resource "google_compute_subnetwork" "us_central" {
  name          = "us-central-subnet"
  ip_cidr_range = "10.4.0.0/20"
  region        = "us-central1"
  network       = google_compute_network.prod_vpc.id
}

# Europe-West Subnet
resource "google_compute_subnetwork" "eu_west" {
  name          = "eu-west-subnet"
  ip_cidr_range = "10.5.0.0/20"
  region        = "europe-west1"
  network       = google_compute_network.prod_vpc.id
}

# Cloud Router for dynamic routing
resource "google_compute_router" "us_central" {
  name    = "router-us-central"
  region  = "us-central1"
  network = google_compute_network.prod_vpc.id

  bgp {
    asn = 64514
  }
}

resource "google_compute_router" "eu_west" {
  name    = "router-eu-west"
  region  = "europe-west1"
  network = google_compute_network.prod_vpc.id

  bgp {
    asn = 64515
  }
}
```

## Step 5: Inter-Cloud Connectivity

### AWS-to-Azure VPN

```hcl
# AWS Side
resource "aws_vpn_gateway" "azure_connection" {
  vpc_id = aws_vpc.us_east.id

  tags = {
    Name = "vpn-to-azure"
  }
}

resource "aws_customer_gateway" "azure" {
  bgp_asn    = 65002
  public_ip  = azurerm_public_ip.vpn_gateway.ip_address
  type       = "ipsec.1"

  tags = {
    Name = "azure-cgw"
  }
}

resource "aws_vpn_connection" "azure" {
  vpn_gateway_id      = aws_vpn_gateway.azure_connection.id
  customer_gateway_id = aws_customer_gateway.azure.id
  type                = "ipsec.1"
  static_routes_only  = false

  tags = {
    Name = "vpn-aws-azure"
  }
}
```

### Azure-to-GCP VPN

```hcl
# Azure Side
resource "azurerm_local_network_gateway" "gcp" {
  name                = "lng-gcp"
  resource_group_name = azurerm_resource_group.main.name
  location            = "East US"
  gateway_address     = google_compute_address.vpn_ip.address
  address_space       = ["10.4.0.0/20", "10.5.0.0/20"]

  bgp_settings {
    asn             = 65003
    bgp_peering_address = "10.6.0.1"
  }
}

resource "azurerm_vpn_gateway_connection" "gcp" {
  name                = "conn-azure-gcp"
  resource_group_name = azurerm_resource_group.main.name
  vpn_gateway_id      = azurerm_vpn_gateway.main.id
  local_network_gateway_id = azurerm_local_network_gateway.gcp.id
  type                = "IPsec"
  shared_key          = "SharedSecret123!"

  enable_bgp = true
}
```

### GCP-to-AWS VPN

```hcl
# GCP Side
resource "google_compute_vpn_gateway" "aws_connection" {
  name    = "vpn-to-aws"
  network = google_compute_network.prod_vpc.id
  region  = "us-central1"
}

resource "google_compute_vpn_tunnel" "aws" {
  name              = "tunnel-to-aws"
  vpn_gateway       = google_compute_vpn_gateway.aws_connection.name
  peer_ip           = aws_vpn_connection.azure.customer_gateway_address
  shared_secret      = "SharedSecret456!"
  ike_version       = 2
  router            = google_compute_router.us_central.name
  region            = "us-central1"
}

resource "google_compute_router_interface" "aws" {
  name       = "interface-aws"
  router     = google_compute_router.us_central.name
  region     = "us-central1"
  ip_range   = "169.254.34.1/30"
  vpn_tunnel = google_compute_vpn_tunnel.aws.name
}

resource "google_compute_router_peer" "aws" {
  name            = "peer-aws"
  router          = google_compute_router.us_central.name
  region          = "us-central1"
  peer_asn        = 65000
  peer_ip_address = "169.254.34.2"
  interface       = google_compute_router_interface.aws.name
}
```

## Step 6: DNS Configuration

### Multi-Cloud DNS Strategy

```hcl
# AWS Route53 for global DNS
resource "aws_route53_zone" "prod" {
  name = "prod.multicloud.example.com"

  tags = {
    Name = "prod-zone"
  }
}

# Route53 Health Check
resource "aws_route53_health_check" "aws_primary" {
  ip_address        = aws_lb.main.dns_name
  port              = 443
  type              = "HTTPS"
  failure_threshold = 3
  request_interval  = 30

  tags = {
    Name = "health-check-aws"
  }
}

# Weighted routing policy for multi-cloud
resource "aws_route53_record" "api_multi_cloud" {
  zone_id = aws_route53_zone.prod.zone_id
  name    = "api.prod.multicloud.example.com"
  type    = "A"

  weighted_routing_policy {
    weight = 50
  }

  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }

  set_identifier = "aws-primary"
}

resource "aws_route53_record" "api_azure" {
  zone_id = aws_route53_zone.prod.zone_id
  name    = "api.prod.multicloud.example.com"
  type    = "A"

  weighted_routing_policy {
    weight = 50
  }

  alias {
    name                   = azurerm_public_ip.app_gateway.fqdn
    zone_id                = "Z1H1FL5HABSF5"  # Azure static zone ID
    evaluate_target_health = false
  }

  set_identifier = "azure-secondary"
}
```

## Step 7: Monitoring & Observability

### Centralized Monitoring

```hcl
# CloudWatch for AWS metrics
resource "aws_cloudwatch_log_group" "multi_cloud" {
  name              = "/aws/multicloud/networking"
  retention_in_days = 30
}

# Log Insights queries
resource "aws_cloudwatch_log_group" "vpn_logs" {
  name              = "/aws/vpc/vpn"
  retention_in_days = 7
}

# Azure Log Analytics
resource "azurerm_log_analytics_workspace" "main" {
  name                = "multi-cloud-law"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
}

# GCP Cloud Monitoring
resource "google_monitoring_alert_policy" "vpn_health" {
  display_name = "Multi-cloud VPN Health"
  combiner     = "OR"

  conditions {
    display_name = "VPN Tunnel Down"

    condition_threshold {
      filter          = "resource.type=\"vpn_tunnel\" AND metric.type=\"compute.googleapis.com/vpn_gateway/tunnel_data_received\""
      duration        = "300s"
      comparison      = "COMPARISON_LT"
      threshold_value = 1000000  # 1MB minimum
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]
}
```

## Step 8: Cost Optimization

### Cross-Cloud Traffic Engineering

```hcl
# Local data processing to minimize inter-cloud transfers
resource "aws_ec2_capacity_reservation" "local_processing" {
  availability_zone       = "us-east-1a"
  instance_count          = 5
  instance_platform       = "Linux/UNIX"
  instance_type           = "c5.4xlarge"
  ebsOptimized            = true
  end_date_type           = "unlimited"
  reservation_type        = "default"

  tags = {
    Name = "local-processing"
  }
}

# Track egress costs
resource "aws_ce_cost_category" "multicloud_egress" {
  name = "multicloud-egress"

  rules {
    rule = "SERVICE like %Data Transfer%"
    value = "CROSS_CLOUD"
  }
}
```

## Best Practices

1. **Design Principle** - Keep data local, process at source
2. **Latency** - Minimize inter-cloud round trips
3. **Cost** - Monitor egress costs closely
4. **Redundancy** - Multiple paths between clouds
5. **Security** - Encrypt all inter-cloud traffic
6. **Monitoring** - Centralized observability
7. **Failover** - Automatic failover between clouds
8. **Documentation** - Keep network topology current

---

**Last Updated:** 2025-11-19
