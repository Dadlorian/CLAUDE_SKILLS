# Azure Virtual Network (VNet) Reference

## Azure VNet Fundamentals

Azure Virtual Network provides a foundation for Azure resources with complete network isolation, multiple layers of security, and flexible connectivity options.

## VNet Architecture

### VNet Components

#### Subnets
- **IP address delegation** - Subnet address space
- **Service endpoints** - Direct Azure service access
- **Service delegation** - Managed services in subnet
- **Network policies** - NSG and UDR association

#### Network Security Groups (NSGs)
- **Inbound rules** - Ingress traffic filtering
- **Outbound rules** - Egress traffic control
- **Service tags** - Azure service CIDR ranges
- **Application security groups** - Logical grouping

#### User Defined Routes (UDRs)
- **Custom routes** - Override default routing
- **Next hop types** - Virtual appliance, gateway, internet
- **Route tables** - Collection of routes
- **Subnet association** - Applied to subnet

### Network Interfaces
- **Primary NIC** - VM connectivity
- **Secondary NICs** - Multiple IPs per VM
- **IP configurations** - Public/private IPs
- **DNS settings** - Custom DNS servers

## Connectivity Models

### Intra-VNet Communication
- **Default routing** - Automatic within VNet
- **Peering through gateway** - Optional
- **No internet required** - Private communication
- **Automatic DNS** - VNet DNS resolution

### Inter-VNet Communication

#### VNet Peering
- **Regional peering** - Same region connection
- **Global peering** - Cross-region connection
- **Transitive peering** - Available with gateway
- **Bandwidth** - Full bandwidth utilization

#### Virtual Network Gateway
- **VPN Gateway** - Site-to-site connectivity
- **ExpressRoute Gateway** - Dedicated connectivity
- **Gateway subnet** - Required /27 or larger
- **HA across AZs** - Automatic redundancy

### External Connectivity

#### ExpressRoute
- **Dedicated connection** - 50 Mbps to 100 Gbps
- **BGP peering** - Dynamic routing
- **Multiple circuit types** - CloudExchange, Point-to-point, Any-to-any
- **Redundancy options** - Primary/secondary circuits

#### Site-to-Site VPN
- **IPSec/IKEv2** - Encryption protocols
- **BGP support** - Dynamic routing
- **Redundant tunnels** - High availability
- **Quick provisioning** - Minutes to setup

#### Point-to-Site VPN
- **Client-based VPN** - Individual connection
- **SSTP/OpenVPN/IKEv2** - Protocol options
- **Certificate-based** - Authentication method
- **Address pool** - Dynamic IP assignment

## Azure Network Services

### Load Balancing

#### Public Load Balancer
- **Inbound NAT** - Port translation
- **Load balancing** - Traffic distribution
- **Frontend IP** - Public/private
- **Backend pools** - VM collection

#### Application Gateway
- **Layer 7** - Application-level routing
- **Path-based routing** - URL-based destination
- **Host-based routing** - Hostname routing
- **SSL/TLS offloading** - Certificate management

#### Azure Front Door
- **Global load balancing** - Multi-region
- **WAF integration** - Web application firewall
- **Anycast routing** - Optimal path selection
- **DDoS protection** - Built-in

### Private Link

#### Private Link Service
- **Service exposure** - Private connection
- **Multiple addresses** - Single service entry
- **Load balancing** - Built-in
- **Cross-subscription** - Private connectivity

#### Private Link Endpoint
- **Service consumption** - Private access
- **ENI in subnet** - Virtual NIC in consumer VNet
- **DNS integration** - Automatic DNS
- **No public exposure** - Fully private

## IP Addressing

### Addressing Schemes
- **Private ranges** - RFC 1918 addresses
- **Public IPs** - Static or dynamic
- **Public IP prefixes** - CIDR aggregation
- **Reserved addresses** - Gateway, broadcast, etc.

### IP Allocation
- **Static allocation** - Fixed IP assignment
- **Dynamic allocation** - DHCP assignment
- **Per-NIC** - Multiple IPs per interface
- **Per-subnet** - Subnet-level pools

## DNS

### Azure DNS
- **Hosted zones** - Domain management
- **Record types** - A, AAAA, MX, TXT, etc.
- **Private resolver** - Conditional forwarding
- **Traffic Manager** - DNS-based routing

### Custom DNS
- **Custom servers** - Non-Azure DNS
- **VNet DNS settings** - Per-VNet configuration
- **DNS forwarding** - Conditional rules
- **Split-brain DNS** - Different responses

## Monitoring & Diagnostics

### Network Watcher
- **IP flow verify** - Traffic allowance check
- **Next hop** - Routing verification
- **NSG flow logs** - Traffic analysis
- **Packet capture** - Traffic inspection
- **Connection monitor** - Connectivity tracking

### Metrics & Logs
- **Application Insights** - Application monitoring
- **Log Analytics** - Log analysis
- **Network Insights** - Topology visualization
- **Diagnostic settings** - Log configuration

## Security

### Network Security

#### NSGs Best Practices
- **Deny by default** - Explicit allow rules
- **Source/destination** - Specific CIDR ranges
- **Application security groups** - Logical grouping
- **Service tags** - Azure service abbreviation

#### DDoS Protection
- **Basic tier** - Free, always-on
- **Standard tier** - Enhanced protection
- **Alerts** - Real-time notifications
- **Reports** - Attack analysis

### Azure Firewall
- **Stateful inspection** - Full-stack firewall
- **Threat intelligence** - Malware detection
- **FQDN filtering** - DNS name rules
- **Application rules** - Layer 7 filtering

## VNet Integration Patterns

### Hub-and-Spoke
- **Hub VNet** - Central connectivity
- **Spoke VNets** - Workload networks
- **Hub peering** - Star topology
- **Transitive routing** - Through hub

### Mesh Network
- **Full mesh peering** - All-to-all connectivity
- **High connectivity** - Direct paths
- **Operational overhead** - More peerings
- **Bandwidth utilization** - Full duplex

## Multi-Region Architecture

### Regional Deployment
- **Region-to-region peering** - Cross-region connectivity
- **GlobalPeering** - Low-latency paths
- **Traffic Manager** - Geographic routing
- **Failover strategies** - RTO/RPO targets

## Cost Optimization

### Bandwidth Management
- **Inbound** - No charge
- **Outbound** - Regional tier pricing
- **Inter-region** - Higher cost
- **Azure Data Box** - Bulk data transfer

### Service Optimization
- **VNet peering** - Lower cost than VPN
- **ExpressRoute** - Better for high-volume
- **NAT Gateway** - Outbound connectivity
- **Reserved bandwidth** - Cost savings

## Compliance & Governance

### Network Policies
- **Azure Policy** - Compliance enforcement
- **Network policies** - Traffic control
- **Service endpoints** - Secure service access
- **Private endpoints** - Private connectivity

### Audit & Logging
- **Activity logs** - Operation tracking
- **Network flow logs** - Traffic analysis
- **NSG flow logs** - Packet-level data
- **Diagnostic logs** - Detailed diagnostics

---

**Reference:** Azure VNet Documentation
**Last Updated:** 2025-11-19
