# Cloud Interconnect Guide

## Interconnect Technology Comparison

### Connection Types

**AWS Direct Connect**
- Dedicated physical connection
- 1 Gbps, 10 Gbps, 100 Gbps options
- $0.30/hour (1Gbps) to $14.40/hour (100Gbps)
- Data transfer: $0.02/GB

**Azure ExpressRoute**
- Dedicated circuit through providers
- 50 Mbps to 100 Gbps
- Metered or unlimited data
- $30-$2,900/month

**GCP Cloud Interconnect**
- Dedicated: 10/100 Gbps
- Partner Interconnect: 50 Mbps to 10 Gbps
- $0.04-$0.08/hour
- No data transfer charges

## Step 1: AWS Direct Connect Setup

### Request Direct Connect Connection

```bash
#!/bin/bash

# 1. Find eligible locations
aws directconnect describe-locations \
  --region us-east-1

# 2. Create connection
CONNECTION_ID=$(aws directconnect create-connection \
  --location us-east-1-dc \
  --bandwidth 10Gbps \
  --connection-name onprem-aws-dx \
  --tags Key=Environment,Value=Production \
  --query 'connection.connectionId' \
  --output text)

echo "Connection ID: $CONNECTION_ID"

# 3. View connection details
aws directconnect describe-connections \
  --connection-id $CONNECTION_ID
```

### Using Terraform

```hcl
# Create Direct Connect connection
resource "aws_dx_connection" "main" {
  name      = "onprem-aws"
  location  = "SFO1"
  bandwidth = "10Gbps"
  tags = {
    Name = "main-dx"
  }
}

# Create Virtual Interface (VIF)
resource "aws_dx_virtual_interface" "private_vif" {
  connection_id      = aws_dx_connection.main.id
  name               = "private-vif"
  vlan               = 100
  asn                = 65000
  auth_key           = "auth-key-value"
  amazon_address     = "169.254.10.1/30"
  customer_address   = "169.254.10.2/30"
  address_family     = "ipv4"
  virtual_gateway_id = aws_vpn_gateway.main.id

  depends_on = [aws_vpn_gateway.main]
}

# Create public VIF (optional, for AWS public services)
resource "aws_dx_virtual_interface" "public_vif" {
  connection_id    = aws_dx_connection.main.id
  name             = "public-vif"
  vlan             = 101
  asn              = 65000
  auth_key         = "auth-key-value"
  amazon_address   = "169.254.11.1/30"
  customer_address = "169.254.11.2/30"
  address_family   = "ipv4"
}

# BGP configuration for dynamic routing
resource "aws_dx_bgp_config" "main" {
  connection_id = aws_dx_connection.main.id
  asn           = 65000

  depends_on = [aws_dx_virtual_interface.private_vif]
}
```

### Configure Customer Side (On-Premises)

```yaml
# Cisco IOS Configuration Example
interface GigabitEthernet0/0/0
  description AWS Direct Connect
  bandwidth 10000000
  ip address 203.0.113.2 255.255.255.0
  no shut

router bgp 65000
  bgp router-id 203.0.113.1
  neighbor 203.0.113.1 remote-as 65001
  !
  address-family ipv4
    neighbor 203.0.113.1 activate
    network 10.0.0.0 mask 255.255.0.0
  exit-address-family
```

## Step 2: Azure ExpressRoute Setup

### Create ExpressRoute Circuit

```hcl
resource "azurerm_express_route_circuit" "main" {
  name                = "main-expressroute"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
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

# Configure peering
resource "azurerm_express_route_circuit_peering" "azure_private_peering" {
  peering_type                  = "AzurePrivatePeering"
  express_route_circuit_name    = azurerm_express_route_circuit.main.name
  resource_group_name           = azurerm_resource_group.main.name
  peer_asn                      = 65000
  primary_peer_address_prefix   = "169.254.21.0/30"
  secondary_peer_address_prefix = "169.254.22.0/30"
  vlan_id                       = 300
  shared_key                    = "SecureKey123"
}

# Link to VNet
resource "azurerm_virtual_network_gateway" "expressroute" {
  name                = "expressroute-gateway"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  type                = "ExpressRoute"
  vpn_type            = "PolicyBased"

  ip_configuration {
    name                          = "vnetGatewayConfig"
    public_ip_address_id          = azurerm_public_ip.expressroute_gateway.id
    private_ip_address_allocation = "Dynamic"
    subnet_id                     = azurerm_subnet.gateway.id
  }
}

# Create circuit connection
resource "azurerm_express_route_circuit_connection" "main" {
  name                            = "circuitConnection"
  express_route_circuit_id        = azurerm_express_route_circuit.main.id
  express_route_circuit_peering_id = azurerm_express_route_circuit_peering.azure_private_peering.id
  peer_express_route_circuit_id   = azurerm_express_route_circuit.peer.id
}
```

## Step 3: GCP Cloud Interconnect

### Dedicated Interconnect

```hcl
# Request dedicated interconnect
resource "google_compute_interconnect" "main" {
  name                  = "main-interconnect"
  interconnect_type     = "DEDICATED"
  requested_link_count  = 2
  link_type             = "LINK_TYPE_ETHERNET_100G"
  location              = "lax-zone1-901"
  admin_enabled         = true

  depends_on = [google_project_service.compute]
}

# Create attachment
resource "google_compute_interconnect_attachment" "prod" {
  name            = "prod-attachment"
  type            = "DEDICATED"
  router          = google_compute_router.main.name
  interconnect    = google_compute_interconnect.main.self_link
  candidate_ipv4_subnets = ["169.254.33.0/30"]
  vlan_tag8021q   = 200
  edge_availability_domain = "availability-domain-1"
  admin_enabled   = true
}

# Configure Cloud Router for BGP
resource "google_compute_router_interface" "interconnect" {
  name       = "interconnect-interface"
  router     = google_compute_router.main.name
  region     = "us-central1"
  ip_range   = "169.254.33.1/30"
  interconnect_attachment = google_compute_interconnect_attachment.prod.self_link
}

resource "google_compute_router_peer" "interconnect" {
  name            = "interconnect-peer"
  router          = google_compute_router.main.name
  region          = "us-central1"
  peer_asn        = 65000
  peer_ip_address = "169.254.33.2"
  interface       = google_compute_router_interface.interconnect.name
}
```

### Partner Interconnect (Faster)

```lc
# Partner interconnect (through service provider)
resource "google_compute_interconnect_attachment" "partner" {
  name            = "partner-attachment"
  type            = "PARTNER"
  router          = google_compute_router.main.name
  interconnect    = google_compute_interconnect_attachment.partner_interconnect.id
  vlan_tag8021q   = 201
  candidate_ipv4_subnets = ["169.254.34.0/30"]
}
```

## Step 4: BGP Configuration

### BGP Peer Setup

```hcl
# AWS BGP configuration
resource "aws_bgp_configuration" "main" {
  connection_id         = aws_dx_connection.main.id
  asn                   = 65000
  auth_key              = "bgp-auth-key"
  bgp_status            = "available"
  customer_address      = "169.254.10.2"
  amazon_address        = "169.254.10.1"
  address_family        = "ipv4"
}

# Azure BGP configuration
resource "azurerm_express_route_circuit_peering" "bgp_config" {
  peering_type                  = "AzurePrivatePeering"
  express_route_circuit_name    = azurerm_express_route_circuit.main.name
  resource_group_name           = azurerm_resource_group.main.name
  peer_asn                      = 65000
  primary_peer_address_prefix   = "169.254.21.0/30"
  secondary_peer_address_prefix = "169.254.22.0/30"
  vlan_id                       = 300
  shared_key                    = "MyBGPAuthKey"
}

# GCP BGP configuration
resource "google_compute_router_bgp" "bgp" {
  router                  = google_compute_router.main.name
  asn                     = 64514
  advertise_mode          = "CUSTOM"
  advertised_groups       = ["ALL_SUBNETS"]
  advertised_ip_ranges {
    range = "10.0.0.0/16"
  }
}
```

## Step 5: High Availability Configuration

### Redundant Interconnects

```hcl
# AWS: Dual Direct Connect connections
resource "aws_dx_connection" "primary" {
  name      = "dx-primary"
  location  = "SFO1"
  bandwidth = "10Gbps"
  tags = { Name = "dx-primary" }
}

resource "aws_dx_connection" "secondary" {
  name      = "dx-secondary"
  location  = "SFO1"
  bandwidth = "10Gbps"
  tags = { Name = "dx-secondary" }
}

# Create VIFs on both connections
resource "aws_dx_virtual_interface" "primary_vif" {
  connection_id    = aws_dx_connection.primary.id
  virtual_gateway_id = aws_vpn_gateway.main.id
  vlan             = 100
  asn              = 65000
  amazon_address   = "169.254.10.1/30"
  customer_address = "169.254.10.2/30"
}

resource "aws_dx_virtual_interface" "secondary_vif" {
  connection_id    = aws_dx_connection.secondary.id
  virtual_gateway_id = aws_vpn_gateway.main.id
  vlan             = 101
  asn              = 65000
  amazon_address   = "169.254.11.1/30"
  customer_address = "169.254.11.2/30"
}

# Route priority: use AS_PATH prepending for failover
resource "aws_ec2_route" "failover_primary" {
  route_table_id            = aws_route_table.main.id
  destination_cidr_block    = "10.0.0.0/16"
  vpc_peering_connection_id = aws_vpc_peering_connection.primary.id
}

resource "aws_ec2_route" "failover_secondary" {
  route_table_id            = aws_route_table.main.id
  destination_cidr_block    = "10.1.0.0/16"
  vpc_peering_connection_id = aws_vpc_peering_connection.secondary.id
}
```

## Step 6: Monitoring & Observability

### Connection Health Monitoring

```bash
# AWS Direct Connect health checks
aws directconnect describe-virtual-interfaces \
  --query 'virtualInterfaces[*].[connectionId,virtualInterfaceState,asn]'

# Check BGP status
aws directconnect describe-bgp-status \
  --connection-id dxcon-xxxxxxxx

# Azure ExpressRoute circuit status
az network express-route list \
  --resource-group prod-rg \
  --query '[*].[name,circuitProvisioningState,serviceProviderProvisioningState]'

# GCP Cloud Interconnect status
gcloud compute interconnects list \
  --format="table(name,state,interconnectType)"
```

### CloudWatch / Azure Monitor Metrics

```hcl
# AWS CloudWatch alarms
resource "aws_cloudwatch_metric_alarm" "dx_connection_down" {
  alarm_name          = "dx-connection-down"
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "ConnectionState"
  namespace           = "AWS/DX"
  period              = "60"
  statistic           = "Average"
  threshold           = "0"
  alarm_description   = "Alert when Direct Connect is down"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ConnectionId = aws_dx_connection.main.id
  }
}

# Azure Monitor alert
resource "azurerm_monitor_metric_alert" "expressroute_availability" {
  name                = "expressroute-availability"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_express_route_circuit.main.id]
  description         = "Alert when ExpressRoute is degraded"
  severity            = 2
  frequency           = "PT1M"
  window_size         = "PT5M"

  criteria {
    metric_name      = "BgpAvailability"
    aggregation      = "Average"
    operator         = "LessThan"
    threshold        = "100"
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
}
```

## Step 7: Cost Management

### Cost Optimization Strategies

```
AWS Direct Connect:
- Commit to 1-year or 3-year terms (-50% discount)
- Use consolidation to reduce ports needed
- Monitor data transfer (add up quickly)
- Use AWS Savings Plans for egress costs

Azure ExpressRoute:
- Choose between Metered or Unlimited
- Peer with Microsoft (cheaper for Office 365)
- Consider ExpressRoute FastPath for direct forwarding
- Leverage global reach for multi-region

GCP Cloud Interconnect:
- Pricing scales with bandwidth used
- Partner interconnect often cheaper
- Commit for 1 or 3 years for discounts
- Monitor egress (cheaper than others)
```

### Cost Tracking Terraform

```hcl
resource "aws_ce_cost_category" "interconnect" {
  name = "interconnect-costs"
  rules {
    rule  = "SERVICE like %Direct%"
    value = "DIRECT_CONNECT"
  }
  rules {
    rule  = "SERVICE like %Data%Transfer%"
    value = "DATA_TRANSFER"
  }
}

# Tag for cost tracking
resource "aws_dx_connection" "tagged" {
  name      = "cost-tracked-dx"
  location  = "SFO1"
  bandwidth = "10Gbps"
  tags = {
    CostCenter      = "network-ops"
    Environment     = "production"
    InterconnectType = "dedicated"
  }
}
```

## Step 8: Troubleshooting Guide

### Common Issues

**Issue: BGP session down**
```bash
# Check on-premises side
show bgp summary
show bgp ipv4 unicast neighbors
show bgp ipv4 unicast neighbors 169.254.10.1

# Check AWS side
aws directconnect describe-bgp-status --connection-id dxcon-xxx
```

**Issue: Low throughput**
- Check duplex and MTU settings (1500)
- Monitor packet loss (tcpdump)
- Check AS_PATH prepending not blocking

**Issue: High latency**
- Use traceroute to find bottleneck
- Check if using optimal path
- Monitor jitter

---

**Last Updated:** 2025-11-19
