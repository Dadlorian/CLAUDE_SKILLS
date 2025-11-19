# Cloud VPN Configuration for Multi-Cloud

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

# AWS-to-Azure VPN
resource "aws_vpn_gateway" "to_azure" {
  provider = aws.aws
  vpc_id   = var.aws_vpc_id

  tags = {
    Name = "vpn-to-azure"
  }
}

resource "aws_customer_gateway" "azure" {
  provider   = aws.aws
  bgp_asn    = 65002
  public_ip  = azurerm_public_ip.vpn_gateway.ip_address
  type       = "ipsec.1"

  tags = {
    Name = "azure-cgw"
  }
}

resource "aws_vpn_connection" "to_azure" {
  provider            = aws.aws
  vpn_gateway_id      = aws_vpn_gateway.to_azure.id
  customer_gateway_id = aws_customer_gateway.azure.id
  type                = "ipsec.1"
  static_routes_only  = false

  tags = {
    Name = "vpn-aws-azure"
  }
}

# Azure-to-GCP VPN
resource "azurerm_local_network_gateway" "gcp" {
  provider            = azurerm.azure
  name                = "lng-gcp"
  resource_group_name = var.azure_resource_group
  location            = var.azure_location
  gateway_address     = google_compute_address.vpn_ip[0].address
  address_space       = ["10.4.0.0/16", "10.5.0.0/16"]

  bgp_settings {
    asn             = 65003
    bgp_peering_address = "10.6.0.1"
  }
}

resource "azurerm_vpn_gateway_connection" "to_gcp" {
  provider                   = azurerm.azure
  name                       = "conn-azure-gcp"
  resource_group_name        = var.azure_resource_group
  vpn_gateway_id             = azurerm_vpn_gateway.main[0].id
  local_network_gateway_id   = azurerm_local_network_gateway.gcp.id
  type                       = "IPsec"
  shared_key                 = "SharedSecret123!"
  enable_bgp                 = true

  tags = {
    Name = "vpn-azure-gcp"
  }
}

# GCP-to-AWS VPN
resource "google_compute_vpn_gateway" "to_aws" {
  provider = google.gcp
  name     = "vpn-to-aws"
  network  = var.gcp_vpc_id
  region   = "us-central1"
}

resource "google_compute_vpn_tunnel" "to_aws" {
  provider            = google.gcp
  name                = "tunnel-to-aws"
  vpn_gateway         = google_compute_vpn_gateway.to_aws.name
  peer_ip             = aws_vpn_connection.to_azure.customer_gateway_configuration
  shared_secret       = "SharedSecret456!"
  ike_version         = 2
  router              = google_compute_router.main[0].name
  region              = "us-central1"
}

# BGP Configuration
resource "google_compute_router_interface" "to_aws" {
  provider            = google.gcp
  name                = "interface-aws"
  router              = google_compute_router.main[0].name
  region              = "us-central1"
  ip_range            = "169.254.34.1/30"
  vpn_tunnel          = google_compute_vpn_tunnel.to_aws.name
}

resource "google_compute_router_peer" "to_aws" {
  provider            = google.gcp
  name                = "peer-aws"
  router              = google_compute_router.main[0].name
  region              = "us-central1"
  peer_asn            = 65000
  peer_ip_address     = "169.254.34.2"
  interface           = google_compute_router_interface.to_aws.name
}

# Variables
variable "aws_vpc_id" {
  type = string
}

variable "gcp_project_id" {
  type = string
}

variable "gcp_vpc_id" {
  type = string
}

variable "azure_resource_group" {
  type = string
}

variable "azure_location" {
  type = string
}

# Outputs
output "aws_vpn_id" {
  value = aws_vpn_connection.to_azure.id
}

output "azure_vpn_id" {
  value = azurerm_vpn_gateway_connection.to_gcp.id
}

output "gcp_vpn_tunnel_id" {
  value = google_compute_vpn_tunnel.to_aws.id
}
