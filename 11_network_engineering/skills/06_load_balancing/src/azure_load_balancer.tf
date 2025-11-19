# Azure Load Balancer Configuration
# Terraform - Production Load Balancing Setup
# Last Updated: 2025-11-19

terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "prod-lb-rg"
  location = var.azure_location
}

# Public IP for Load Balancer
resource "azurerm_public_ip" "main" {
  name                = "prod-lb-pip"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = {
    Environment = "production"
  }
}

# Network Interface for Load Balancer
resource "azurerm_network_interface" "main" {
  name                = "prod-lb-nic"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "prod-lb-ipconfig"
    subnet_id                     = var.subnet_id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.main.id
  }
}

# Load Balancer
resource "azurerm_lb" "main" {
  name                = "prod-lb"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"

  frontend_ip_configuration {
    name                 = "prod-frontend"
    public_ip_address_id = azurerm_public_ip.main.id
  }

  tags = {
    Environment = "production"
  }
}

# Backend Address Pool
resource "azurerm_lb_backend_address_pool" "web" {
  loadbalancer_id = azurerm_lb.main.id
  name            = "prod-web-backend"
}

resource "azurerm_lb_backend_address_pool" "api" {
  loadbalancer_id = azurerm_lb.main.id
  name            = "prod-api-backend"
}

# Health Probe for Web
resource "azurerm_lb_probe" "web_health" {
  loadbalancer_id = azurerm_lb.main.id
  name            = "web-health-probe"
  protocol        = "Http"
  request_path    = "/health"
  port            = 80
  interval_in_seconds = 30
  number_of_probes    = 2
}

# Health Probe for API
resource "azurerm_lb_probe" "api_health" {
  loadbalancer_id = azurerm_lb.main.id
  name            = "api-health-probe"
  protocol        = "Http"
  request_path    = "/api/health"
  port            = 8080
  interval_in_seconds = 10
  number_of_probes    = 2
}

# Load Balancing Rule for HTTP
resource "azurerm_lb_rule" "http" {
  loadbalancer_id            = azurerm_lb.main.id
  name                       = "http-rule"
  protocol                   = "Tcp"
  frontend_port              = 80
  backend_port               = 80
  frontend_ip_configuration_name = "prod-frontend"
  backend_address_pool_ids   = [azurerm_lb_backend_address_pool.web.id]
  probe_id                   = azurerm_lb_probe.web_health.id
  load_distribution          = "SourceIPProtocol"  # Session affinity
  idle_timeout_in_minutes    = 15
  enable_floating_ip         = false
}

# Load Balancing Rule for HTTPS
resource "azurerm_lb_rule" "https" {
  loadbalancer_id            = azurerm_lb.main.id
  name                       = "https-rule"
  protocol                   = "Tcp"
  frontend_port              = 443
  backend_port               = 443
  frontend_ip_configuration_name = "prod-frontend"
  backend_address_pool_ids   = [azurerm_lb_backend_address_pool.web.id]
  probe_id                   = azurerm_lb_probe.web_health.id
  load_distribution          = "SourceIP"
  idle_timeout_in_minutes    = 15
}

# Load Balancing Rule for API
resource "azurerm_lb_rule" "api" {
  loadbalancer_id            = azurerm_lb.main.id
  name                       = "api-rule"
  protocol                   = "Tcp"
  frontend_port              = 8080
  backend_port               = 8080
  frontend_ip_configuration_name = "prod-frontend"
  backend_address_pool_ids   = [azurerm_lb_backend_address_pool.api.id]
  probe_id                   = azurerm_lb_probe.api_health.id
  load_distribution          = "SourceIP"
  idle_timeout_in_minutes    = 30
}

# Network Security Group
resource "azurerm_network_security_group" "main" {
  name                = "prod-lb-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "AllowHTTP"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 101
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowAPI"
    priority                   = 102
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8080"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = {
    Environment = "production"
  }
}

# Application Insights for Monitoring
resource "azurerm_application_insights" "main" {
  name                = "prod-lb-ai"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"
  retention_in_days   = 30
}

# Monitor Alert - Unhealthy Backend Count
resource "azurerm_monitor_metric_alert" "unhealthy_backends" {
  name                = "prod-lb-unhealthy-backends"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_lb.main.id]

  criteria {
    metric_name      = "DipAvailability"
    operator         = "LessThan"
    aggregation      = "Average"
    metric_namespace = "Microsoft.Network/loadBalancers"
    threshold        = 100
  }

  window_size  = "PT5M"
  frequency    = "PT1M"
  description  = "Alert when backend availability drops below 100%"
}

# Monitor Alert - High Data Processing
resource "azurerm_monitor_metric_alert" "high_data_processing" {
  name                = "prod-lb-high-data-processing"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_lb.main.id]

  criteria {
    metric_name      = "ByteCount"
    operator         = "GreaterThan"
    aggregation      = "Total"
    metric_namespace = "Microsoft.Network/loadBalancers"
    threshold        = 1000000000  # 1GB
  }

  window_size  = "PT5M"
  frequency    = "PT1M"
  description  = "Alert when data processing exceeds 1GB in 5 minutes"
}

# Outputs
output "load_balancer_id" {
  description = "ID of the load balancer"
  value       = azurerm_lb.main.id
}

output "public_ip_address" {
  description = "Public IP address of the load balancer"
  value       = azurerm_public_ip.main.ip_address
}

output "backend_pool_web_id" {
  description = "ID of the web backend address pool"
  value       = azurerm_lb_backend_address_pool.web.id
}

output "backend_pool_api_id" {
  description = "ID of the API backend address pool"
  value       = azurerm_lb_backend_address_pool.api.id
}
