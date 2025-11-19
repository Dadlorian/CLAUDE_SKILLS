# Hybrid Cloud Connectivity Configuration
# On-Premises to Multi-Cloud Integration

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
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
  alias  = "aws"
}

# Azure Provider
provider "azurerm" {
  features {}
  alias = "azure"
}

# GCP Provider
provider "google" {
  project = var.gcp_project_id
  region  = "us-central1"
  alias   = "gcp"
}

# ============================================================
# AWS - On-Premises Connectivity
# ============================================================

resource "aws_customer_gateway" "onprem" {
  provider   = aws.aws
  bgp_asn    = 65000
  public_ip  = var.onprem_vpn_ip
  type       = "ipsec.1"

  tags = {
    Name = "onprem-gateway"
  }
}

resource "aws_vpn_gateway" "onprem" {
  provider = aws.aws
  vpc_id   = var.aws_vpc_id

  tags = {
    Name = "onprem-vpn-gateway"
  }
}

resource "aws_vpn_connection" "onprem" {
  provider            = aws.aws
  vpn_gateway_id      = aws_vpn_gateway.onprem.id
  customer_gateway_id = aws_customer_gateway.onprem.id
  type                = "ipsec.1"
  static_routes_only  = false

  tags = {
    Name = "vpn-onprem-aws"
  }
}

resource "aws_vpn_gateway_route_propagation" "onprem" {
  provider       = aws.aws
  vpn_gateway_id = aws_vpn_gateway.onprem.id
  route_table_id = var.aws_route_table_id
}

# ============================================================
# Azure - On-Premises Connectivity
# ============================================================

resource "azurerm_local_network_gateway" "onprem" {
  provider            = azurerm.azure
  name                = "lng-onprem"
  resource_group_name = var.azure_resource_group
  location            = var.azure_location
  gateway_address     = var.onprem_vpn_ip
  address_space       = [var.onprem_cidr]

  bgp_settings {
    asn             = 65000
    bgp_peering_address = var.onprem_bgp_ip
  }

  tags = {
    Name = "onprem-gateway"
  }
}

resource "azurerm_vpn_gateway_connection" "onprem" {
  provider                   = azurerm.azure
  name                       = "vpn-onprem"
  resource_group_name        = var.azure_resource_group
  vpn_gateway_id             = azurerm_vpn_gateway.main[0].id
  local_network_gateway_id   = azurerm_local_network_gateway.onprem.id
  type                       = "IPsec"
  shared_key                 = "HybridCloudSecret123!"
  enable_bgp                 = true

  tags = {
    Name = "vpn-onprem-azure"
  }
}

# ============================================================
# GCP - On-Premises Connectivity
# ============================================================

resource "google_compute_vpn_gateway" "onprem" {
  provider = google.gcp
  name     = "vpn-to-onprem"
  network  = var.gcp_vpc_id
  region   = "us-central1"
}

resource "google_compute_vpn_tunnel" "onprem" {
  provider            = google.gcp
  name                = "tunnel-onprem"
  vpn_gateway         = google_compute_vpn_gateway.onprem.name
  peer_ip             = var.onprem_vpn_ip
  shared_secret       = "HybridCloudSecret456!"
  ike_version         = 2
  router              = google_compute_router.onprem[0].name
  region              = "us-central1"
}

resource "google_compute_router" "onprem" {
  provider = google.gcp
  name     = "router-onprem"
  region   = "us-central1"
  network  = var.gcp_vpc_id

  bgp {
    asn = 64514
  }
}

resource "google_compute_router_interface" "onprem" {
  provider            = google.gcp
  name                = "interface-onprem"
  router              = google_compute_router.onprem[0].name
  region              = "us-central1"
  ip_range            = "169.254.21.1/30"
  vpn_tunnel          = google_compute_vpn_tunnel.onprem.name
}

resource "google_compute_router_peer" "onprem" {
  provider            = google.gcp
  name                = "peer-onprem"
  router              = google_compute_router.onprem[0].name
  region              = "us-central1"
  peer_asn            = 65000
  peer_ip_address     = var.onprem_bgp_ip
  interface           = google_compute_router_interface.onprem.name
}

# ============================================================
# AWS Transit Gateway for Multi-Cloud
# ============================================================

resource "aws_ec2_transit_gateway" "hybrid" {
  provider                       = aws.aws
  description                    = "Hybrid Cloud Transit Gateway"
  default_route_table_association = "enable"
  default_route_table_propagation = "enable"

  tags = {
    Name = "hybrid-tgw"
  }
}

resource "aws_ec2_transit_gateway_vpc_attachment" "aws_vpc" {
  provider           = aws.aws
  subnet_ids         = var.aws_subnet_ids
  transit_gateway_id = aws_ec2_transit_gateway.hybrid.id
  vpc_id             = var.aws_vpc_id

  tags = {
    Name = "aws-tgw-attachment"
  }
}

# Route to on-premises through TGW
resource "aws_route" "to_onprem_tgw" {
  provider               = aws.aws
  route_table_id         = var.aws_route_table_id
  destination_cidr_block = var.onprem_cidr
  transit_gateway_id     = aws_ec2_transit_gateway.hybrid.id
}

# Route to Azure
resource "aws_route" "to_azure" {
  provider               = aws.aws
  route_table_id         = var.aws_route_table_id
  destination_cidr_block = var.azure_vnet_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.aws_azure[0].id
}

resource "aws_vpc_peering_connection" "aws_azure" {
  provider  = aws.aws
  vpc_id    = var.aws_vpc_id
  peer_vpc_id = var.azure_vnet_id

  tags = {
    Name = "aws-azure-peering"
  }
}

# ============================================================
# Variables
# ============================================================

variable "onprem_vpn_ip" {
  type = string
}

variable "onprem_cidr" {
  type = string
}

variable "onprem_bgp_ip" {
  type = string
}

variable "aws_vpc_id" {
  type = string
}

variable "aws_subnet_ids" {
  type = list(string)
}

variable "aws_route_table_id" {
  type = string
}

variable "azure_resource_group" {
  type = string
}

variable "azure_location" {
  type = string
}

variable "azure_vnet_id" {
  type = string
}

variable "azure_vnet_cidr" {
  type = string
}

variable "gcp_project_id" {
  type = string
}

variable "gcp_vpc_id" {
  type = string
}

# ============================================================
# Outputs
# ============================================================

output "aws_vpn_connection_id" {
  value = aws_vpn_connection.onprem.id
}

output "azure_vpn_connection_id" {
  value = azurerm_vpn_gateway_connection.onprem.id
}

output "gcp_vpn_tunnel_id" {
  value = google_compute_vpn_tunnel.onprem.id
}

output "transit_gateway_id" {
  value = aws_ec2_transit_gateway.hybrid.id
}
