# Azure Private Link Configuration

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

# Private Link Service
resource "azurerm_private_link_service" "api" {
  name                = "api-private-link"
  location            = var.location
  resource_group_name = var.resource_group_name

  nat_ip_configuration {
    name      = "api-nat-config"
    primary   = true
    subnet_id = var.service_subnet_id
  }

  load_balancer_frontend_ip_configuration_ids = [
    azurerm_lb.api.frontend_ip_configuration[0].id
  ]

  visibility_subscription_ids = [data.azurerm_client_config.current.subscription_id]

  tags = {
    Name = "api-private-link"
  }
}

# Network Load Balancer
resource "azurerm_lb" "api" {
  name                = "api-lb"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "Standard"
  load_balancer_sku   = "Standard"

  frontend_ip_configuration {
    name                 = "api-frontend"
    subnet_id            = var.service_subnet_id
    private_ip_address_allocation = "Static"
    private_ip_address   = "10.2.2.10"
  }
}

resource "azurerm_lb_backend_address_pool" "api" {
  loadbalancer_id = azurerm_lb.api.id
  name            = "api-backend-pool"
}

resource "azurerm_lb_probe" "api" {
  loadbalancer_id = azurerm_lb.api.id
  name            = "api-health-probe"
  port            = 443
  protocol        = "Tcp"
  interval_in_seconds = 15
  number_of_probes    = 2
}

resource "azurerm_lb_rule" "api" {
  loadbalancer_id                = azurerm_lb.api.id
  name                           = "api-rule"
  protocol                       = "Tcp"
  frontend_port                  = 443
  backend_port                   = 443
  frontend_ip_configuration_name = "api-frontend"
  backend_address_pool_ids       = [azurerm_lb_backend_address_pool.api.id]
  probe_id                       = azurerm_lb_probe.api.id
  enable_tcp_reset               = true
  idle_timeout_in_minutes        = 15
}

# Private Endpoint (Consumer)
resource "azurerm_private_endpoint" "api_consumer" {
  name                = "api-endpoint"
  location            = var.location
  resource_group_name = var.consumer_resource_group
  subnet_id           = var.consumer_subnet_id

  private_service_connection {
    name              = "api-connection"
    is_manual_connection = false
    private_connection_resource_id = azurerm_private_link_service.api.id
    subresource_names  = [""]
  }

  private_dns_zone_group {
    name                 = "api-dns-group"
    private_dns_zone_ids = [azurerm_private_dns_zone.api.id]
  }

  tags = {
    Name = "api-private-endpoint"
  }
}

# Private DNS Zone
resource "azurerm_private_dns_zone" "api" {
  name                = "api.privatelink.example.com"
  resource_group_name = var.resource_group_name
}

resource "azurerm_private_dns_zone_virtual_network_link" "api" {
  name                  = "api-vnet-link"
  resource_group_name   = var.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.api.name
  virtual_network_id    = var.vnet_id
}

resource "azurerm_private_dns_a_record" "api" {
  name                = "api"
  zone_name           = azurerm_private_dns_zone.api.name
  resource_group_name = var.resource_group_name
  ttl                 = 300
  records             = ["10.2.2.10"]
}

# Data source for current context
data "azurerm_client_config" "current" {}

# Variables
variable "service_subnet_id" {
  type = string
}

variable "consumer_resource_group" {
  type = string
}

variable "consumer_subnet_id" {
  type = string
}

variable "vnet_id" {
  type = string
}

# Outputs
output "private_link_service_id" {
  value = azurerm_private_link_service.api.id
}

output "private_endpoint_id" {
  value = azurerm_private_endpoint.api_consumer.id
}

output "private_endpoint_network_interface_ids" {
  value = azurerm_private_endpoint.api_consumer.network_interface_ids
}
