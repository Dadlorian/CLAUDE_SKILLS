# Azure Networking Guide

## Azure VNet Planning

### Network Design

```
Resource Group: prod-rg
├── VNet: prod-vnet (10.0.0.0/16)
│   ├── Subnet: web-subnet (10.0.1.0/24)
│   ├── Subnet: app-subnet (10.0.2.0/24)
│   └── Subnet: db-subnet (10.0.3.0/24)
├── Network Security Group: nsg-web
├── Network Security Group: nsg-app
└── Network Security Group: nsg-db
```

### IP Addressing Strategy

```
Total: 10.0.0.0/16 (65,536 addresses)
├── Web Tier: 10.0.1.0/24 (256 addresses)
├── App Tier: 10.0.2.0/25, 10.0.2.128/25 (512 addresses)
├── DB Tier: 10.0.3.0/24 (256 addresses)
├── Gateway Subnet: 10.0.4.0/27 (32 addresses) - Required for VPN/ExpressRoute
└── Reserved: 10.0.100.0/22 (1,024 addresses)
```

## Step 1: Create VNet using Terraform

```hcl
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
  subscription_id = var.azure_subscription_id
}

resource "azurerm_resource_group" "main" {
  name     = "prod-rg"
  location = "East US"
}

resource "azurerm_virtual_network" "main" {
  name                = "prod-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = {
    Environment = "production"
  }
}
```

## Step 2: Create Subnets

```hcl
resource "azurerm_subnet" "web" {
  name                 = "web-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]

  service_endpoints = ["Microsoft.Storage", "Microsoft.Sql"]
}

resource "azurerm_subnet" "app" {
  name                 = "app-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/25"]

  delegation {
    name = "delegation"

    service_delegation {
      name    = "Microsoft.ContainerInstance/containerGroups"
      actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
    }
  }
}

resource "azurerm_subnet" "db" {
  name                 = "db-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.3.0/24"]

  service_endpoints = ["Microsoft.Sql"]
}

resource "azurerm_subnet" "gateway" {
  name                 = "GatewaySubnet"  # Must be named GatewaySubnet
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.4.0/27"]
}
```

## Step 3: Network Security Groups

### Web NSG

```hcl
resource "azurerm_network_security_group" "web" {
  name                = "nsg-web"
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
    name                       = "DenyAll"
    priority                   = 4096
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "web" {
  subnet_id                 = azurerm_subnet.web.id
  network_security_group_id = azurerm_network_security_group.web.id
}
```

### App NSG

```hcl
resource "azurerm_network_security_group" "app" {
  name                = "nsg-app"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "AllowFromWeb"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8080"
    source_address_prefix      = "10.0.1.0/24"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "app" {
  subnet_id                 = azurerm_subnet.app.id
  network_security_group_id = azurerm_network_security_group.app.id
}
```

## Step 4: VPN Gateway Setup

### VPN Gateway Configuration

```hcl
resource "azurerm_public_ip" "vpn_gateway" {
  name                = "pip-vpn-gateway"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_vpn_gateway" "main" {
  name                = "vpn-gateway"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  type                = "Vpn"
  vpn_type            = "RouteBased"
  active_active       = true

  ip_configuration {
    name                          = "vnetGatewayConfig"
    public_ip_address_id          = azurerm_public_ip.vpn_gateway.id
    private_ip_address_allocation = "Dynamic"
    subnet_id                     = azurerm_subnet.gateway.id
  }

  vpn_client_configuration {
    address_space        = ["172.16.201.0/24"]
    vpn_client_protocols = ["OpenVPN", "SSTP"]
    aad_audience         = "41b23e61-6c1e-4545-b367-ff0b18a9bbb1"
    aad_issuer           = "https://sts.windows.net/${data.azurerm_client_config.current.tenant_id}/"
    aad_tenant           = "https://login.microsoftonline.com/${data.azurerm_client_config.current.tenant_id}"
  }
}
```

### Local Network Gateway (On-Premises)

```hcl
resource "azurerm_local_network_gateway" "onprem" {
  name                = "lng-onprem"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  gateway_address     = "203.0.113.1"  # On-premises VPN endpoint
  address_space       = ["192.168.0.0/16"]

  bgp_settings {
    asn             = 65000
    bgp_peering_address = "10.0.1.1"
  }
}

resource "azurerm_vpn_gateway_connection" "onprem" {
  name                = "vpn-connection-onprem"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  type                       = "IPsec"
  virtual_network_gateway_id = azurerm_vpn_gateway.main.id
  local_network_gateway_id   = azurerm_local_network_gateway.onprem.id
  shared_key                 = "P@ssw0rd1234!"

  enable_bgp = true
}
```

## Step 5: Load Balancer Setup

### Application Gateway

```hcl
resource "azurerm_public_ip" "app_gateway" {
  name                = "pip-app-gateway"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_application_gateway" "main" {
  name                = "app-gateway"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  sku {
    name     = "WAF_v2"
    tier     = "WAF_v2"
    capacity = 2
  }

  gateway_ip_configuration {
    name      = "gateway-ip-config"
    subnet_id = azurerm_subnet.app.id
  }

  frontend_port {
    name = "http"
    port = 80
  }

  frontend_port {
    name = "https"
    port = 443
  }

  frontend_ip_configuration {
    name                 = "frontend-ip"
    public_ip_address_id = azurerm_public_ip.app_gateway.id
  }

  backend_address_pool {
    name = "backend-pool"
  }

  backend_http_settings {
    name                  = "http-settings"
    cookie_based_affinity = "Disabled"
    port                  = 80
    protocol              = "Http"
    request_timeout       = 60
  }

  http_listener {
    name                           = "http-listener"
    frontend_ip_configuration_name = "frontend-ip"
    frontend_port_name             = "http"
    protocol                       = "Http"
  }

  request_routing_rule {
    name                       = "routing-rule"
    rule_type                  = "Basic"
    http_listener_name         = "http-listener"
    backend_address_pool_name  = "backend-pool"
    backend_http_settings_name = "http-settings"
    priority                   = 1
  }

  waf_configuration {
    enabled          = true
    firewall_mode    = "Prevention"
    rule_set_type    = "OWASP"
    rule_set_version = "3.1"
  }
}
```

## Step 6: VNet Peering

### Peering Configuration

```hcl
resource "azurerm_virtual_network" "peer" {
  name                = "peer-vnet"
  address_space       = ["10.1.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_virtual_network_peering" "main_to_peer" {
  name                      = "main-to-peer"
  resource_group_name       = azurerm_resource_group.main.name
  virtual_network_name      = azurerm_virtual_network.main.name
  remote_virtual_network_id = azurerm_virtual_network.peer.id

  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
  allow_gateway_transit        = true
}

resource "azurerm_virtual_network_peering" "peer_to_main" {
  name                      = "peer-to-main"
  resource_group_name       = azurerm_resource_group.main.name
  virtual_network_name      = azurerm_virtual_network.peer.name
  remote_virtual_network_id = azurerm_virtual_network.main.id

  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
  use_remote_gateways          = true
}
```

## Step 7: Private Endpoints

### Azure SQL Private Endpoint

```hcl
resource "azurerm_private_endpoint" "sql" {
  name                = "pe-sql"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.db.id

  private_service_connection {
    name                           = "psc-sql"
    is_manual_connection           = false
    private_connection_resource_id = azurerm_mssql_server.main.id
    subresource_names              = ["sqlServer"]
  }
}

resource "azurerm_private_dns_zone" "sql" {
  name                = "privatelink.database.windows.net"
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "sql" {
  name                  = "sql-vnet-link"
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.sql.name
  virtual_network_id    = azurerm_virtual_network.main.id
}

resource "azurerm_private_dns_a_record" "sql" {
  name                = azurerm_mssql_server.main.name
  zone_name           = azurerm_private_dns_zone.sql.name
  resource_group_name = azurerm_resource_group.main.name
  ttl                 = 300
  records             = [azurerm_private_endpoint.sql.private_service_connection[0].private_ip_address]
}
```

## Step 8: Monitoring

### Enable VNet Flow Logs

```hcl
resource "azurerm_network_watcher" "main" {
  name                = "nw-prod"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_network_watcher_flow_log" "main" {
  network_watcher_name       = azurerm_network_watcher.main.name
  resource_group_name        = azurerm_resource_group.main.name
  network_security_group_id  = azurerm_network_security_group.web.id
  storage_account_id         = azurerm_storage_account.flow_logs.id
  enabled                    = true
  version                    = 2
  retention_policy {
    enabled = true
    days    = 7
  }

  traffic_analytics {
    enabled               = true
    workspace_id          = azurerm_log_analytics_workspace.main.workspace_id
    workspace_region      = azurerm_log_analytics_workspace.main.location
    workspace_resource_id = azurerm_log_analytics_workspace.main.id
    interval_in_minutes   = 10
  }
}
```

## Best Practices

- [ ] Plan IP address space (20% growth buffer)
- [ ] Separate web, app, and database subnets
- [ ] Use NSGs for network segmentation
- [ ] Configure VPN/ExpressRoute for hybrid
- [ ] Enable VNet Flow Logs for monitoring
- [ ] Use Private Endpoints for PaaS services
- [ ] Implement load balancing for HA
- [ ] Configure NAT Gateway for outbound traffic
- [ ] Enable DDoS protection (Standard or Premium)
- [ ] Document network topology and routing

---

**Last Updated:** 2025-11-19
