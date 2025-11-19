# Terraform Network Providers Reference

## Overview

Terraform providers enable infrastructure-as-code management of network devices and cloud network resources.

## Cisco Provider

### Installation
```hcl
terraform {
  required_providers {
    iosxe = {
      source  = "CiscoDevNet/iosxe"
      version = "~> 0.4.0"
    }
  }
}

provider "iosxe" {
  username = var.device_username
  password = var.device_password
  url      = "https://${var.device_ip}:443"
  insecure = true  # Skip SSL verification (dev only)
}
```

### Cisco IOS-XE Resources

#### Interface Configuration
```hcl
resource "iosxe_interface_ethernet" "example" {
  device = iosxe_device_netconf.device.device
  name   = "GigabitEthernet0/0/1"

  description = "WAN Interface"
  enabled     = true
  mtu         = 1500

  ip_address = "192.168.1.1"
  ip_mask    = "255.255.255.0"
}

resource "iosxe_device_netconf" "device" {
  device = "192.168.1.1"
  user   = "admin"
  pass   = "password"
}
```

#### BGP Configuration
```hcl
resource "iosxe_bgp" "example" {
  device        = iosxe_device_netconf.device.device
  asn           = 65001
  router_id     = "10.1.1.1"
  bgp_log       = true
  graceful_restart = true

  neighbors = [
    {
      address      = "10.0.0.1"
      remote_asn   = 65002
      description  = "ISP Router"
      update_source = "Loopback0"
    },
    {
      address    = "10.0.0.2"
      remote_asn = 65002
    }
  ]

  address_family_ipv4 = [
    {
      network       = "10.0.0.0"
      mask          = "255.255.255.0"
      next_hop_self = true
    }
  ]
}
```

#### OSPF Configuration
```hcl
resource "iosxe_ospf" "example" {
  device      = iosxe_device_netconf.device.device
  process_id  = 1
  router_id   = "10.1.1.1"
  log_changes = true

  networks = [
    {
      network = "10.0.0.0"
      area    = "0"
      mask    = "0.0.0.255"
    },
    {
      network = "192.168.0.0"
      area    = "1"
      mask    = "0.0.0.255"
    }
  ]

  redistribute_bgp = [
    {
      asn    = 65001
      metric = 100
    }
  ]
}
```

#### ACL Configuration
```hcl
resource "iosxe_acl" "example" {
  device   = iosxe_device_netconf.device.device
  name     = "SSH_ACCESS"
  type     = "standard"
  sequence = 10

  lines = [
    {
      seq    = 10
      action = "permit"
      source = "10.0.0.0"
      mask   = "0.0.0.255"
    },
    {
      seq    = 20
      action = "deny"
      source = "any"
    }
  ]
}
```

## Juniper Provider

### Installation
```hcl
terraform {
  required_providers {
    junos = {
      source  = "Juniper/junos"
      version = "~> 2.0.0"
    }
  }
}

provider "junos" {
  host     = var.device_ip
  username = var.device_username
  password = var.device_password
}
```

### Juniper Resources

#### Interface Configuration
```hcl
resource "junos_interface_physical" "example" {
  name        = "ge-0/0/0"
  description = "WAN Interface"
  mtu         = 1500
  enable      = true
}

resource "junos_interface_logical" "example" {
  name        = "ge-0/0/0.0"
  description = "Unit 0"

  family_inet {
    address {
      cidr_ip = "192.168.1.1/24"
    }
  }

  family_inet6 {
    address {
      cidr_ip = "2001:db8::1/64"
    }
  }
}
```

#### Routing Configuration
```hcl
resource "junos_static_route" "example" {
  destination = "192.168.0.0/24"
  next_hop    = ["10.0.0.1"]
}

resource "junos_bgp_neighbor" "example" {
  group             = "upstream"
  ip                = "10.0.0.1"
  description       = "ISP Router"
  local_as          = 65001
  peer_as           = 65002
  type              = "external"
  authentication_key = "secret"
}

resource "junos_bgp_group" "example" {
  name       = "upstream"
  local_as   = 65001
  type       = "external"
  import_policy  = ["IMPORT_POLICY"]
  export_policy  = ["EXPORT_POLICY"]
}
```

#### Security Policy
```hcl
resource "junos_security_policy" "example" {
  from_zone = "untrust"
  to_zone   = "trust"
  name      = "allow_ssh"

  policy {
    name        = "allow-ssh"
    description = "Allow SSH from outside"

    match_from_port = "ssh"
    match_source    = "any"
    match_destination = "any"

    then_allow = true
  }
}
```

## AWS Provider

### VPC Configuration
```hcl
resource "aws_vpc" "example" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name = "production-vpc"
  }
}

resource "aws_subnet" "example" {
  vpc_id            = aws_vpc.example.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "production-subnet"
  }
}
```

### EC2 Network Interface
```hcl
resource "aws_network_interface" "example" {
  subnet_id = aws_subnet.example.id

  private_ips = ["10.0.1.10"]

  security_groups = [aws_security_group.example.id]

  tags = {
    Name = "primary-eni"
  }
}

resource "aws_security_group" "example" {
  name        = "allow_ssh"
  description = "Allow SSH access"
  vpc_id      = aws_vpc.example.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### Route Table
```hcl
resource "aws_route_table" "example" {
  vpc_id = aws_vpc.example.id

  route {
    cidr_block      = "0.0.0.0/0"
    gateway_id      = aws_internet_gateway.example.id
  }

  tags = {
    Name = "production-routes"
  }
}

resource "aws_route_table_association" "example" {
  subnet_id      = aws_subnet.example.id
  route_table_id = aws_route_table.example.id
}
```

### Internet Gateway
```hcl
resource "aws_internet_gateway" "example" {
  vpc_id = aws_vpc.example.id

  tags = {
    Name = "production-igw"
  }
}
```

## Azure Provider

### Virtual Network
```hcl
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "example" {
  name     = "production-rg"
  location = "East US"
}

resource "azurerm_virtual_network" "example" {
  name                = "production-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
}

resource "azurerm_subnet" "example" {
  name                 = "production-subnet"
  resource_group_name  = azurerm_resource_group.example.name
  virtual_network_name = azurerm_virtual_network.example.name
  address_prefixes     = ["10.0.1.0/24"]
}
```

### Network Security Group
```hcl
resource "azurerm_network_security_group" "example" {
  name                = "allow-ssh"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  security_rule {
    name                       = "allow_ssh"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}
```

## HashiCorp Cloud Provider

### Network Resources
```hcl
provider "hcp" {
  project_id = var.hcp_project_id
}

resource "hcp_hvn" "example" {
  hvn_id         = "production-hvn"
  cloud_provider = "aws"
  region         = "us-east-1"
  cidr_block     = "172.25.16.0/20"
}

resource "hcp_hvn_route" "example" {
  hvn_link         = hcp_hvn.example.self_link
  hvn_route_id     = "peering-route"
  destination_cidr = "10.0.0.0/16"
  target_link      = hcp_aws_network_peering.example.self_link
}
```

## Common Patterns

### Multi-Device Configuration
```hcl
variable "devices" {
  type = map(object({
    ip       = string
    username = string
    password = string
  }))

  default = {
    router1 = {
      ip       = "192.168.1.1"
      username = "admin"
      password = "password"
    }
    router2 = {
      ip       = "192.168.1.2"
      username = "admin"
      password = "password"
    }
  }
}

provider "iosxe" {
  for_each = var.devices

  username = each.value.username
  password = each.value.password
  url      = "https://${each.value.ip}:443"
}

resource "iosxe_interface_ethernet" "example" {
  for_each = var.devices

  device      = iosxe_device_netconf.device[each.key].device
  name        = "GigabitEthernet0/0/1"
  description = "WAN Interface on ${each.key}"
}
```

### Module Structure
```hcl
module "network" {
  source = "./modules/network"

  vpc_cidr = "10.0.0.0/16"
  subnets  = {
    public  = "10.0.1.0/24"
    private = "10.0.2.0/24"
  }

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}
```

---

**Last Updated**: 2025-11-19
**Reference**: terraform.io/providers, registry.terraform.io/providers
