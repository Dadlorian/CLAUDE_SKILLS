# Azure ExpressRoute Terraform Configuration

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

variable "subscription_id" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

# ExpressRoute Circuit
resource "azurerm_express_route_circuit" "main" {
  name                = "main-expressroute"
  resource_group_name = var.resource_group_name
  location            = var.location
  service_provider_name = "Equinix"
  peering_location    = "Silicon Valley"
  bandwidth_in_mbps   = 10000

  sku {
    tier   = "Premium"
    family = "MeteredData"
  }

  allow_classic_operations = false

  tags = {
    Name = "main-expressroute"
  }
}

# Private Peering Configuration
resource "azurerm_express_route_circuit_peering" "azure_private_peering" {
  peering_type                  = "AzurePrivatePeering"
  express_route_circuit_name    = azurerm_express_route_circuit.main.name
  resource_group_name           = var.resource_group_name
  peer_asn                      = 65000
  primary_peer_address_prefix   = "169.254.21.0/30"
  secondary_peer_address_prefix = "169.254.22.0/30"
  vlan_id                       = 300
  shared_key                    = "SecureSharedKey123"

  depends_on = [azurerm_express_route_circuit.main]
}

# Microsoft Peering Configuration
resource "azurerm_express_route_circuit_peering" "microsoft_peering" {
  peering_type              = "MicrosoftPeering"
  express_route_circuit_name = azurerm_express_route_circuit.main.name
  resource_group_name       = var.resource_group_name
  peer_asn                  = 65000
  primary_peer_address_prefix = "169.254.31.0/30"
  secondary_peer_address_prefix = "169.254.32.0/30"
  vlan_id                   = 400
  shared_key                = "MicrosoftPeeringKey456"
  advertised_public_prefixes = ["203.0.113.0/24"]

  depends_on = [azurerm_express_route_circuit.main]
}

# VPN Gateway for ExpressRoute
resource "azurerm_public_ip" "expressroute_gateway" {
  name                = "pip-expressroute-gateway"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_virtual_network_gateway" "expressroute_gateway" {
  name                = "expressroute-gateway"
  location            = var.location
  resource_group_name = var.resource_group_name
  type                = "ExpressRoute"
  vpn_type            = "PolicyBased"

  ip_configuration {
    name                          = "vnetGatewayConfig"
    public_ip_address_id          = azurerm_public_ip.expressroute_gateway.id
    private_ip_address_allocation = "Dynamic"
    subnet_id                      = var.gateway_subnet_id
  }

  depends_on = [azurerm_public_ip.expressroute_gateway]
}

# Connection to ExpressRoute
resource "azurerm_virtual_network_gateway_connection" "expressroute" {
  name                = "expressroute-connection"
  location            = var.location
  resource_group_name = var.resource_group_name

  type                       = "ExpressRoute"
  virtual_network_gateway_id = azurerm_virtual_network_gateway.expressroute_gateway.id
  express_route_circuit_id   = azurerm_express_route_circuit.main.id

  depends_on = [azurerm_virtual_network_gateway.expressroute_gateway]
}

# Route Table for ExpressRoute routes
resource "azurerm_route_table" "expressroute" {
  name                = "expressroute-rt"
  location            = var.location
  resource_group_name = var.resource_group_name
  disable_bgp_route_propagation = false

  route {
    name           = "default-route"
    address_prefix = "0.0.0.0/0"
    next_hop_type  = "VirtualNetworkGateway"
  }

  tags = {
    Name = "expressroute-rt"
  }
}

# Outputs
output "expressroute_circuit_id" {
  value = azurerm_express_route_circuit.main.id
}

output "expressroute_circuit_service_key" {
  value     = azurerm_express_route_circuit.main.service_key
  sensitive = true
}

output "gateway_id" {
  value = azurerm_virtual_network_gateway.expressroute_gateway.id
}

# Required variables
variable "gateway_subnet_id" {
  type = string
}
