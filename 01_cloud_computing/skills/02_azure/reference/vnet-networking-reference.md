# Azure Virtual Network (VNet) and Networking Reference

## Virtual Network Fundamentals

### VNet Characteristics
- **Isolation**: Private network in Azure
- **Segmentation**: Divide into multiple subnets
- **Connectivity**: Connect to on-premises, other VNets, internet
- **Filtering**: Network Security Groups and firewalls
- **Routing**: System routes and custom user-defined routes
- **Free**: No charge for VNet itself (only associated resources)

### Address Space Planning

**Private IP Ranges** (RFC 1918):
- 10.0.0.0/8 (10.0.0.0 - 10.255.255.255)
- 172.16.0.0/12 (172.16.0.0 - 172.31.255.255)
- 192.168.0.0/16 (192.168.0.0 - 192.168.255.255)

**Reserved IPs per Subnet**:
- .0: Network address
- .1: Azure gateway
- .2, .3: Azure DNS
- .255: Broadcast address

**Example**: 10.0.1.0/24 subnet has 256 IPs, 251 usable (5 reserved)

### Subnet Design Patterns

```
Example Multi-Tier Application VNet: 10.0.0.0/16

├── GatewaySubnet: 10.0.0.0/27 (VPN/ExpressRoute gateway)
├── AzureFirewallSubnet: 10.0.1.0/26 (Azure Firewall)
├── AzureBastionSubnet: 10.0.2.0/26 (Azure Bastion)
├── Web-Subnet: 10.0.10.0/24 (Web tier)
├── App-Subnet: 10.0.11.0/24 (Application tier)
├── Data-Subnet: 10.0.12.0/24 (Database tier)
├── AKS-Subnet: 10.0.20.0/22 (Kubernetes cluster)
└── PrivateEndpoints-Subnet: 10.0.30.0/24 (Private endpoints)
```

## Network Security Groups (NSG)

### NSG Rules

```bash
# Create NSG
az network nsg create \
  --resource-group myRG \
  --name web-nsg \
  --location eastus

# Add rule to allow HTTP
az network nsg rule create \
  --resource-group myRG \
  --nsg-name web-nsg \
  --name allow-http \
  --priority 100 \
  --source-address-prefixes Internet \
  --source-port-ranges '*' \
  --destination-address-prefixes '*' \
  --destination-port-ranges 80 \
  --access Allow \
  --protocol Tcp \
  --direction Inbound

# Add rule to allow HTTPS
az network nsg rule create \
  --resource-group myRG \
  --nsg-name web-nsg \
  --name allow-https \
  --priority 110 \
  --destination-port-ranges 443 \
  --access Allow \
  --protocol Tcp
```

### Service Tags

**Common Service Tags**:
- `VirtualNetwork`: All addresses in VNet address space
- `Internet`: Public internet addresses
- `AzureLoadBalancer`: Azure load balancer probe IP
- `Storage`: Azure Storage service IPs
- `Sql`: Azure SQL Database service IPs
- `AzureKeyVault`: Azure Key Vault service IPs
- `AzureActiveDirectory`: Azure AD service IPs

**Example Rule with Service Tag**:
```bash
az network nsg rule create \
  --resource-group myRG \
  --nsg-name app-nsg \
  --name allow-storage \
  --priority 200 \
  --destination-address-prefixes Storage \
  --destination-port-ranges 443 \
  --access Allow \
  --protocol Tcp
```

### Application Security Groups (ASG)

```bash
# Create ASGs
az network asg create --resource-group myRG --name web-asg
az network asg create --resource-group myRG --name app-asg
az network asg create --resource-group myRG --name db-asg

# NSG rule using ASGs
az network nsg rule create \
  --resource-group myRG \
  --nsg-name app-nsg \
  --name web-to-app \
  --priority 100 \
  --source-asgs web-asg \
  --destination-asgs app-asg \
  --destination-port-ranges 8080 \
  --access Allow \
  --protocol Tcp

# Assign NIC to ASG
az network nic ip-config update \
  --resource-group myRG \
  --nic-name myNIC \
  --name ipconfig1 \
  --application-security-groups web-asg
```

### NSG Best Practices

**Rule Priority**: 100-4096 (lower number = higher priority)

**Default Rules** (cannot be deleted):
- AllowVNetInBound: Priority 65000
- AllowAzureLoadBalancerInBound: Priority 65001
- DenyAllInBound: Priority 65500

**Best Practices**:
1. Start priorities at 100, increment by 10 (room for insertions)
2. Use service tags instead of IP addresses
3. Use ASGs for application-based grouping
4. Deny by default, allow specific traffic
5. Log NSG flow for security analysis

## VNet Peering

### Peering Types

**VNet Peering** (same region):
- Low latency, high bandwidth
- Private IP communication
- No gateway required
- $0.01/GB ingress and egress

**Global VNet Peering** (cross-region):
- Connect VNets across regions
- Private backbone network
- No public internet
- $0.035/GB ingress and egress

### Create Peering

```bash
# Get VNet IDs
vnet1Id=$(az network vnet show --resource-group rg1 --name vnet1 --query id -o tsv)
vnet2Id=$(az network vnet show --resource-group rg2 --name vnet2 --query id -o tsv)

# Create peering from vnet1 to vnet2
az network vnet peering create \
  --resource-group rg1 \
  --name vnet1-to-vnet2 \
  --vnet-name vnet1 \
  --remote-vnet $vnet2Id \
  --allow-vnet-access \
  --allow-forwarded-traffic

# Create reverse peering from vnet2 to vnet1
az network vnet peering create \
  --resource-group rg2 \
  --name vnet2-to-vnet1 \
  --vnet-name vnet2 \
  --remote-vnet $vnet1Id \
  --allow-vnet-access \
  --allow-forwarded-traffic
```

### Gateway Transit

```bash
# Hub VNet allows gateway to be used
az network vnet peering update \
  --resource-group hub-rg \
  --name hub-to-spoke \
  --vnet-name hub-vnet \
  --set allowGatewayTransit=true

# Spoke VNet uses hub's gateway
az network vnet peering update \
  --resource-group spoke-rg \
  --name spoke-to-hub \
  --vnet-name spoke-vnet \
  --set useRemoteGateways=true
```

## Load Balancers

### Azure Load Balancer (Layer 4)

**SKUs**: Basic (free), Standard

**Standard Load Balancer**:
```bash
# Create public IP
az network public-ip create \
  --resource-group myRG \
  --name myPublicIP \
  --sku Standard \
  --allocation-method Static

# Create load balancer
az network lb create \
  --resource-group myRG \
  --name myLB \
  --sku Standard \
  --public-ip-address myPublicIP \
  --frontend-ip-name myFrontEnd \
  --backend-pool-name myBackEndPool

# Add health probe
az network lb probe create \
  --resource-group myRG \
  --lb-name myLB \
  --name myHealthProbe \
  --protocol tcp \
  --port 80 \
  --interval 15 \
  --threshold 2

# Add load balancer rule
az network lb rule create \
  --resource-group myRG \
  --lb-name myLB \
  --name myLBRule \
  --protocol tcp \
  --frontend-port 80 \
  --backend-port 80 \
  --frontend-ip-name myFrontEnd \
  --backend-pool-name myBackEndPool \
  --probe-name myHealthProbe
```

**Internal Load Balancer**:
```bash
az network lb create \
  --resource-group myRG \
  --name myInternalLB \
  --sku Standard \
  --vnet-name myVNet \
  --subnet mySubnet \
  --frontend-ip-name myFrontEnd \
  --backend-pool-name myBackEndPool
```

### Application Gateway (Layer 7)

**Features**:
- SSL termination
- Cookie-based session affinity
- URL path-based routing
- Multi-site hosting
- Web Application Firewall (WAF)
- Autoscaling

```bash
# Create Application Gateway
az network application-gateway create \
  --resource-group myRG \
  --name myAppGateway \
  --location eastus \
  --vnet-name myVNet \
  --subnet myAGSubnet \
  --capacity 2 \
  --sku Standard_v2 \
  --http-settings-cookie-based-affinity Disabled \
  --frontend-port 80 \
  --http-settings-port 80 \
  --http-settings-protocol Http \
  --public-ip-address myAGPublicIP \
  --servers 10.0.1.4 10.0.1.5
```

**Path-Based Routing**:
```bash
# Create path map
az network application-gateway url-path-map create \
  --resource-group myRG \
  --gateway-name myAppGateway \
  --name myPathMap \
  --paths /images/* \
  --http-settings myHTTPSettings \
  --address-pool imagesBackendPool
```

### Azure Front Door

**Global Load Balancing with**:
- Global HTTP load balancing
- SSL offload
- URL-based routing
- WAF
- Caching (CDN)

```bash
az afd profile create \
  --resource-group myRG \
  --profile-name myFrontDoor \
  --sku Standard_AzureFrontDoor
```

## VPN Gateway

### Site-to-Site VPN

```bash
# Create local network gateway (on-premises)
az network local-gateway create \
  --resource-group myRG \
  --name myLocalGW \
  --gateway-ip-address 203.0.113.10 \
  --local-address-prefixes 192.168.0.0/16

# Create VPN gateway
az network vnet-gateway create \
  --resource-group myRG \
  --name myVPNGateway \
  --vnet myVNet \
  --public-ip-addresses myGWPublicIP \
  --gateway-type Vpn \
  --vpn-type RouteBased \
  --sku VpnGw2 \
  --generation Generation2

# Create connection
az network vpn-connection create \
  --resource-group myRG \
  --name myConnection \
  --vnet-gateway1 myVPNGateway \
  --local-gateway2 myLocalGW \
  --location eastus \
  --shared-key "MySharedKey123!"
```

### Point-to-Site VPN

```bash
# Generate certificates (use PowerShell or openssl)

# Configure P2S
az network vnet-gateway update \
  --resource-group myRG \
  --name myVPNGateway \
  --client-protocol OpenVPN \
  --address-prefixes 172.16.0.0/24 \
  --root-cert-name RootCert \
  --root-cert-data "BASE64_ENCODED_CERT"
```

**VPN Gateway SKUs**:
| SKU | Tunnels | Throughput | BGP | Zone-Redundant |
|-----|---------|------------|-----|----------------|
| Basic | 10 | 100 Mbps | No | No |
| VpnGw1 | 30 | 650 Mbps | Yes | No |
| VpnGw2 | 30 | 1 Gbps | Yes | No |
| VpnGw3 | 30 | 1.25 Gbps | Yes | No |
| VpnGw1AZ | 30 | 650 Mbps | Yes | Yes |

## ExpressRoute

**Private Connection**: Dedicated circuit from on-premises to Azure

**Benefits**:
- Predictable performance
- No public internet
- Supports up to 100 Gbps
- Microsoft peering (Microsoft 365, Azure PaaS)
- Private peering (Azure IaaS in VNets)

```bash
# Create ExpressRoute circuit
az network express-route create \
  --resource-group myRG \
  --name myCircuit \
  --peering-location "Silicon Valley" \
  --bandwidth 200 \
  --provider "Equinix" \
  --sku-family MeteredData \
  --sku-tier Standard

# Create ExpressRoute gateway
az network vnet-gateway create \
  --resource-group myRG \
  --name myERGateway \
  --vnet myVNet \
  --gateway-type ExpressRoute \
  --sku Standard \
  --public-ip-addresses myGWPublicIP
```

**SKUs and Bandwidth**:
| SKU | Bandwidth | Circuits |
|-----|-----------|----------|
| Standard | Up to 1 Gbps | 10 |
| High Performance | Up to 2 Gbps | 10 |
| Ultra Performance | Up to 10 Gbps | 10 |
| ErGw1AZ | Up to 1 Gbps | 10 |
| ErGw2AZ | Up to 2 Gbps | 10 |
| ErGw3AZ | Up to 10 Gbps | 10 |

## Azure Firewall

**Features**:
- Stateful firewall as a service
- Built-in high availability
- Threat intelligence
- FQDN filtering
- Network and application rules
- DNS proxy

```bash
# Create Azure Firewall
az network firewall create \
  --resource-group myRG \
  --name myFirewall \
  --location eastus \
  --vnet-name myVNet

# Create public IP for firewall
az network public-ip create \
  --resource-group myRG \
  --name myFirewallIP \
  --sku Standard \
  --allocation-method Static

# Configure firewall
az network firewall ip-config create \
  --resource-group myRG \
  --firewall-name myFirewall \
  --name myFirewallConfig \
  --public-ip-address myFirewallIP \
  --vnet-name myVNet
```

**Application Rule**:
```bash
az network firewall application-rule create \
  --resource-group myRG \
  --firewall-name myFirewall \
  --collection-name AllowWeb \
  --name AllowGoogle \
  --source-addresses 10.0.0.0/24 \
  --protocols Http=80 Https=443 \
  --target-fqdns www.google.com \
  --priority 200 \
  --action Allow
```

**Network Rule**:
```bash
az network firewall network-rule create \
  --resource-group myRG \
  --firewall-name myFirewall \
  --collection-name AllowDNS \
  --name AllowDNS \
  --source-addresses 10.0.0.0/16 \
  --destination-addresses 8.8.8.8 8.8.4.4 \
  --destination-ports 53 \
  --protocols UDP \
  --priority 200 \
  --action Allow
```

**SKUs**:
- **Basic**: Small deployments, 250 Mbps
- **Standard**: Production, threat intelligence
- **Premium**: TLS inspection, IDPS, advanced threats

## Private Endpoints

**Use Case**: Private connectivity to Azure PaaS services

**Supported Services**:
- Storage (Blob, File, Queue, Table, Data Lake)
- SQL Database
- Cosmos DB
- Key Vault
- App Service
- Container Registry
- Event Hubs
- And many more...

```bash
# Disable private endpoint network policies
az network vnet subnet update \
  --resource-group myRG \
  --vnet-name myVNet \
  --name mySubnet \
  --disable-private-endpoint-network-policies true

# Create private endpoint for Storage Account
az network private-endpoint create \
  --resource-group myRG \
  --name myPrivateEndpoint \
  --vnet-name myVNet \
  --subnet mySubnet \
  --private-connection-resource-id /subscriptions/.../storageAccounts/mystorageaccount \
  --group-id blob \
  --connection-name myConnection

# Create private DNS zone
az network private-dns zone create \
  --resource-group myRG \
  --name privatelink.blob.core.windows.net

# Link DNS zone to VNet
az network private-dns link vnet create \
  --resource-group myRG \
  --zone-name privatelink.blob.core.windows.net \
  --name myDNSLink \
  --virtual-network myVNet \
  --registration-enabled false
```

## Service Endpoints

**Use Case**: Secure Azure service access via VNet

**Differences from Private Endpoints**:
- Service endpoints: Traffic stays on Azure backbone, service still has public IP
- Private endpoints: Service gets private IP in your VNet

```bash
# Enable service endpoint on subnet
az network vnet subnet update \
  --resource-group myRG \
  --vnet-name myVNet \
  --name mySubnet \
  --service-endpoints Microsoft.Storage Microsoft.Sql

# Configure storage account to allow only from VNet
az storage account network-rule add \
  --resource-group myRG \
  --account-name mystorageaccount \
  --vnet-name myVNet \
  --subnet mySubnet
```

## DNS

### Azure DNS (Public)

```bash
# Create DNS zone
az network dns zone create \
  --resource-group myRG \
  --name example.com

# Add A record
az network dns record-set a add-record \
  --resource-group myRG \
  --zone-name example.com \
  --record-set-name www \
  --ipv4-address 203.0.113.10
```

### Azure Private DNS

```bash
# Create private DNS zone
az network private-dns zone create \
  --resource-group myRG \
  --name contoso.local

# Link to VNet
az network private-dns link vnet create \
  --resource-group myRG \
  --zone-name contoso.local \
  --name myDNSLink \
  --virtual-network myVNet \
  --registration-enabled true

# Add record
az network private-dns record-set a add-record \
  --resource-group myRG \
  --zone-name contoso.local \
  --record-set-name db \
  --ipv4-address 10.0.12.5
```

## Network Watcher

**Tools**:
- IP Flow Verify
- Next Hop
- Connection Troubleshoot
- NSG Flow Logs
- Packet Capture
- VPN Troubleshoot

```bash
# Enable Network Watcher
az network watcher configure \
  --resource-group myRG \
  --locations eastus \
  --enabled true

# Test connectivity
az network watcher test-connectivity \
  --resource-group myRG \
  --source-resource myVM \
  --dest-address www.google.com \
  --dest-port 80

# Enable NSG flow logs
az network watcher flow-log create \
  --resource-group myRG \
  --nsg myNSG \
  --name myFlowLog \
  --storage-account mystorageaccount \
  --enabled true \
  --retention 90
```

## Monitoring and Diagnostics

### Key Metrics
- DDoS attack metrics
- Firewall throughput
- VPN Gateway bandwidth
- Load balancer health probe status
- Application Gateway throughput

### Diagnostic Logs
```bash
# Enable diagnostics for NSG
az monitor diagnostic-settings create \
  --resource /subscriptions/.../networkSecurityGroups/myNSG \
  --name myDiagnostics \
  --workspace /subscriptions/.../workspaces/myWorkspace \
  --logs '[{"category": "NetworkSecurityGroupEvent", "enabled": true}]'
```

## Best Practices Summary

1. **Plan Address Space**: Non-overlapping, room for growth
2. **Use Hub-Spoke Topology**: Centralized security and connectivity
3. **Implement Defense in Depth**: NSGs, Firewall, Private Endpoints
4. **Use Service Tags and ASGs**: Simplify rule management
5. **Enable NSG Flow Logs**: Security analysis and compliance
6. **Use Private Endpoints**: Secure PaaS access
7. **Implement DNS Properly**: Private DNS for internal resolution
8. **Monitor and Alert**: Network Watcher, Azure Monitor
9. **Document Network Design**: IP ranges, routes, dependencies
10. **Regular Security Reviews**: NSG rules, exposed endpoints
