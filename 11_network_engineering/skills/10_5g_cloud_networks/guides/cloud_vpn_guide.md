# Cloud VPN Guide

## VPN Architecture Planning

### VPN Types

**Site-to-Site VPN**
- Connects networks (data center to cloud)
- IPSec encryption
- BGP routing support
- High availability models

**Client-to-Site VPN**
- Individual user access
- Certificate or credential-based
- Mobile worker support

**Multi-Cloud VPN**
- Connecting multiple cloud providers
- Transit routing
- Centralized control

## Step 1: AWS Site-to-Site VPN Setup

### Create Customer Gateway

```bash
#!/bin/bash

# Create customer gateway (on-premises VPN endpoint)
aws ec2 create-customer-gateway \
  --type ipsec.1 \
  --public-ip 203.0.113.1 \
  --bgp-asn 65000 \
  --region us-east-1
```

### Using Terraform

```hcl
resource "aws_customer_gateway" "onprem" {
  bgp_asn    = 65000
  public_ip  = "203.0.113.1"
  type       = "ipsec.1"

  tags = {
    Name = "on-premises-gateway"
  }
}

resource "aws_vpn_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "vpn-gateway"
  }
}

resource "aws_vpn_gateway_attachment" "main" {
  vpn_gateway_id = aws_vpn_gateway.main.id
  vpc_id         = aws_vpc.main.id
}

resource "aws_vpn_connection" "onprem" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.onprem.id
  type                = "ipsec.1"
  static_routes_only  = false

  tags = {
    Name = "vpn-onprem"
  }
}

resource "aws_vpn_connection_route" "onprem" {
  destination_cidr_block = "192.168.0.0/16"
  vpn_connection_id      = aws_vpn_connection.onprem.id
}

resource "aws_vpn_gateway_route_propagation" "main" {
  vpn_gateway_id = aws_vpn_gateway.main.id
  route_table_id = aws_route_table.main.id
}
```

## Step 2: Azure VPN Configuration

### VPN Gateway Setup

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

  ip_configuration {
    name                          = "vnetGatewayConfig"
    public_ip_address_id          = azurerm_public_ip.vpn_gateway.id
    private_ip_address_allocation = "Dynamic"
    subnet_id                     = azurerm_subnet.gateway.id
  }
}

resource "azurerm_local_network_gateway" "onprem" {
  name                = "lng-onprem"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  gateway_address     = "203.0.113.1"
  address_space       = ["192.168.0.0/16"]

  bgp_settings {
    asn             = 65000
    bgp_peering_address = "192.168.0.1"
  }
}

resource "azurerm_vpn_gateway_connection" "onprem" {
  name                = "vpn-onprem"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  type                       = "IPsec"
  virtual_network_gateway_id = azurerm_vpn_gateway.main.id
  local_network_gateway_id   = azurerm_local_network_gateway.onprem.id
  shared_key                 = "SuperSecret123!"

  enable_bgp = true
}
```

## Step 3: GCP Cloud VPN

### VPN Gateway Configuration

```hcl
resource "google_compute_vpn_gateway" "main" {
  name    = "vpn-gateway"
  network = google_compute_network.main.id
  region  = "us-central1"
}

resource "google_compute_address" "vpn_static" {
  name   = "vpn-static-ip"
  region = "us-central1"
}

# Forwarding rules for VPN
resource "google_compute_forwarding_rule" "esp" {
  name        = "vpn-esp"
  ip_protocol = "ESP"
  ip_address  = google_compute_address.vpn_static.address
  target_vpn_gateway = google_compute_vpn_gateway.main.id
  region      = "us-central1"
}

resource "google_compute_vpn_tunnel" "onprem" {
  name          = "vpn-tunnel-onprem"
  region        = "us-central1"
  peer_ip       = "203.0.113.1"
  shared_secret = "SuperSecret456!"
  ike_version   = 2
  vpn_gateway   = google_compute_vpn_gateway.main.name

  depends_on = [
    google_compute_forwarding_rule.esp,
    google_compute_forwarding_rule.udp500,
    google_compute_forwarding_rule.udp4500
  ]
}

resource "google_compute_route" "onprem" {
  name           = "route-onprem"
  dest_range     = "192.168.0.0/16"
  network        = google_compute_network.main.name
  next_hop_vpn_tunnel = google_compute_vpn_tunnel.onprem.id
  priority       = 1000
}
```

## Step 4: BGP Configuration

### Dynamic Routing Setup

```hcl
# AWS BGP for dynamic routing
resource "aws_vpn_connection_options" "bgp" {
  vpn_connection_id = aws_vpn_connection.onprem.id
  static_routes_only = false
}

# Azure BGP
resource "azurerm_vpn_gateway_connection" "bgp_settings" {
  name                           = "vpn-connection-bgp"
  resource_group_name            = azurerm_resource_group.main.name
  vpn_gateway_id                 = azurerm_vpn_gateway.main.id
  local_network_gateway_id       = azurerm_local_network_gateway.onprem.id
  type                           = "IPsec"
  shared_key                     = "SharedSecret789!"
  enable_bgp                     = true
  use_local_azure_ip_address     = true
  routing_weight                 = 100

  ipsec_policy {
    dh_group         = "DHGroup14"
    ike_encryption   = "AES256"
    ike_integrity    = "SHA256"
    ipsec_encryption = "AES256"
    ipsec_integrity  = "SHA256"
    pfs_group        = "PFS2048"
    sa_datasize      = 102400000
    sa_lifetime      = 27000
  }
}

# GCP BGP with Cloud Router
resource "google_compute_router" "main" {
  name    = "vpn-router"
  region  = "us-central1"
  network = google_compute_network.main.id

  bgp {
    asn = 64514
  }
}

resource "google_compute_router_interface" "onprem" {
  name       = "interface-onprem"
  router     = google_compute_router.main.name
  region     = "us-central1"
  ip_range   = "169.254.34.1/30"
  vpn_tunnel = google_compute_vpn_tunnel.onprem.name
}

resource "google_compute_router_peer" "onprem" {
  name            = "peer-onprem"
  router          = google_compute_router.main.name
  region          = "us-central1"
  peer_asn        = 65000
  peer_ip_address = "169.254.34.2"
  interface       = google_compute_router_interface.onprem.name
}
```

## Step 5: IPSec Configuration

### IPSec Parameters

```
Phase 1 (IKE):
- Encryption: AES-256
- Hash: SHA-256
- Authentication: Pre-shared key
- Diffie-Hellman Group: Group 14
- Lifetime: 28800 seconds (8 hours)
- Mode: Main mode

Phase 2 (IPSec):
- Protocol: ESP
- Encryption: AES-256-GCM
- Authentication: SHA-256
- Perfect Forward Secrecy: Enabled (DH Group 14)
- Lifetime: 3600 seconds (1 hour)
```

### Terraform IPSec Configuration

```hcl
resource "aws_vpn_connection_options" "ipsec" {
  vpn_connection_id = aws_vpn_connection.onprem.id

  local_authentication_options {
    type = "certificate"
  }

  remote_authentication_options {
    type = "certificate"
  }

  tunnel_options {
    tunnel_inside_cidr = "169.254.10.0/30"

    phase1_encryption_algorithms = ["AES256"]
    phase1_hash_algorithms       = ["SHA2-256"]
    phase1_dh_group_numbers      = ["14"]
    phase1_lifetime_seconds      = 28800

    phase2_encryption_algorithms = ["AES256-GCM16"]
    phase2_hash_algorithms       = ["SHA2-256"]
    phase2_dh_group_numbers      = ["14"]
    phase2_lifetime_seconds      = 3600
  }
}
```

## Step 6: High Availability VPN

### Redundant VPN Tunnels

```hcl
# AWS creates two tunnels by default for high availability
resource "aws_vpn_connection" "redundant" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.onprem.id
  type                = "ipsec.1"
  static_routes_only  = false

  tags = {
    Name = "redundant-vpn"
  }
}

# Both tunnels active
resource "aws_vpn_gateway_route_propagation" "both_tunnels" {
  vpn_gateway_id = aws_vpn_gateway.main.id
  route_table_id = aws_route_table.main.id

  depends_on = [aws_vpn_connection.redundant]
}
```

### Azure Active-Active Configuration

```lcl
resource "azurerm_vpn_gateway_connection" "active_active" {
  name                          = "vpn-active-active"
  location                      = azurerm_resource_group.main.location
  resource_group_name           = azurerm_resource_group.main.name
  type                          = "IPsec"
  virtual_network_gateway_id    = azurerm_vpn_gateway.main.id
  local_network_gateway_id      = azurerm_local_network_gateway.onprem.id
  shared_key                    = "SuperSecret@123!"
  enable_bgp                    = true
  use_local_azure_ip_address    = true
  express_route_circuit_id      = null  # Optional
}

# Second connection for redundancy
resource "azurerm_vpn_gateway_connection" "active_active_secondary" {
  name                          = "vpn-active-active-secondary"
  location                      = azurerm_resource_group.main.location
  resource_group_name           = azurerm_resource_group.main.name
  type                          = "IPsec"
  virtual_network_gateway_id    = azurerm_vpn_gateway.main.id
  local_network_gateway_id      = azurerm_local_network_gateway.onprem.id
  shared_key                    = "SuperSecret@456!"
  enable_bgp                    = true
}
```

## Step 7: Monitoring & Troubleshooting

### VPN Monitoring

```bash
# AWS VPN connection status
aws ec2 describe-vpn-connections \
  --vpn-connection-ids vpn-0123456789abcdef0 \
  --query 'VpnConnections[*].[VpnConnectionId,State,CustomerGatewayConfiguration]'

# Azure VPN connection status
az network vpn-connection list \
  --resource-group prod-rg \
  --query '[*].[name,connectionStatus]'

# GCP VPN tunnel status
gcloud compute vpn-tunnels list \
  --format="table(name,status)"
```

### Troubleshooting Commands

```bash
# Check IPSec tunnel status (on-premises)
ipsec status
ipsec stroke status

# View VPN logs
tail -f /var/log/auth.log | grep vpn
tcpdump -i eth0 'esp or (udp and port 500) or (udp and port 4500)'

# Test connectivity
ping -c 4 10.0.0.0  # AWS VPC
ping -c 4 10.2.0.0  # Azure VNet
ping -c 4 10.4.0.0  # GCP VPC
```

## Step 8: Cost Optimization

### VPN Cost Management

```
AWS:
- VPN Connection: $0.36/hour
- Data transfer (out): $0.02/GB
- Data transfer (CloudFront): Reduced rates

Azure:
- VPN Gateway: $0.40/hour
- Data transfer (out): $0.03/GB
- ExpressRoute (better for high volume)

GCP:
- Cloud VPN: $0.04/hour per tunnel
- Egress: $0.12/GB (between regions)
```

### Cost Optimization Strategies

1. Use dedicated interconnect for high-volume (> 1 Tbps)
2. Optimize traffic routing (local data processing)
3. Compress traffic (gzip, compression algorithms)
4. Cache at edge (CDN)
5. Monitor egress continuously

## Best Practices

1. **Always use redundant tunnels**
2. **Enable BGP for dynamic routing**
3. **Encrypt with strong ciphers**
4. **Monitor tunnel health continuously**
5. **Plan for bandwidth growth**
6. **Test failover regularly**
7. **Document all configurations**
8. **Implement access controls**
9. **Regular security reviews**
10. **Maintain compliance documentation**

---

**Last Updated:** 2025-11-19
