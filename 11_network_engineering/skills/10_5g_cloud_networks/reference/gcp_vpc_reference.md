# GCP Virtual Private Cloud Reference

## GCP VPC Fundamentals

Google Cloud VPC provides global network architecture with automatic routing, sophisticated firewall rules, and seamless integration with Google Cloud services.

## VPC Architecture

### VPC Structure
- **Global resource** - Spans all regions
- **Custom subnets** - Per-region definition
- **Auto-expansion** - Automatic CIDR growth
- **Flexible addressing** - Multiple CIDR ranges per subnet

### Subnets
- **Regional** - Resources in single region
- **Automatic subnets** - Default VPC mode
- **Custom subnets** - Manual creation
- **Secondary ranges** - Additional CIDR blocks

### IP Addressing

#### Internal IP Addresses
- **Primary IP** - Main address per interface
- **Secondary IPs** - Alias IP ranges
- **Ephemeral IPs** - Temporary assignment
- **Reserved IPs** - Static allocation

#### External IP Addresses
- **Ephemeral external** - Session-based
- **Static external** - Persistent
- **Cloud NAT** - Outbound NAT service
- **Cloud DNS** - Managed DNS service

## Routing

### Route Types

#### System Routes
- **Subnet routes** - Automatic per subnet
- **Default route** - 0.0.0.0/0
- **Applicable routes** - Instance-level routing
- **Legacy networks** - Class A/B/C routes

#### Custom Routes

**Static Routes**
- **Next hops** - Instance, VPN gateway, gateway
- **Priority** - Lower value takes precedence
- **Destination** - CIDR range
- **Tag-based** - Route to specific instances

**Dynamic Routes**
- **BGP routes** - Cloud Router propagation
- **Cloud Interconnect** - Automatic BGP
- **VPN gateways** - BGP support
- **Route exchange** - BGP advertisements

### Cloud Router

**BGP Configuration**
- **ASN** - Autonomous system number
- **Peer BGP ASN** - Remote router ASN
- **Advertised groups** - Subnet/all-subnets
- **Learn routes** - Inbound route learning

**Use Cases**
- **Dynamic routing** - BGP-based routing
- **Multi-cloud** - Hybrid connectivity
- **Load sharing** - Equal-cost multi-path
- **Failover** - Automatic convergence

## Firewall Rules

### Firewall Fundamentals
- **Stateful** - Return traffic auto-allowed
- **Implicit deny** - Default drop
- **Global resource** - Applied to VPC
- **Priority-based** - Lower number wins

### Rule Configuration

**Ingress Rules**
- **Source CIDR** - Source IP range
- **Protocol** - TCP, UDP, ICMP, etc.
- **Port** - Destination port
- **Target** - All instances or tags

**Egress Rules**
- **Destination CIDR** - Target range
- **Protocol** - Allowed protocols
- **Port** - Destination port
- **Priority** - Rule precedence

### Service Accounts & Network Tags
- **Network tags** - Instance labeling
- **Service account** - VM identity
- **IAM policies** - Access control
- **Rule targeting** - Tag-based rules

## Connectivity Models

### VPC Peering

#### Standard Peering
- **RFC 1918 routes** - Private routes only
- **Custom routes** - Imported via peering
- **Non-transitive** - No transitive peering
- **Regional** - Same region peering

#### Full Mesh Peering
- **All-to-all connectivity** - Complete mesh
- **Route exchange** - Automatic
- **Transitive routes** - Via route table
- **Operational overhead** - Higher complexity

### Shared VPC

**Shared VPC Architecture**
- **Host project** - Central VPC
- **Service projects** - Workload projects
- **Subnet attachment** - Shared subnets
- **Centralized management** - Network administration

**Benefits**
- **Centralized management** - Single point control
- **Subnet sharing** - Resource efficiency
- **Network isolation** - Service project separation
- **Billing consolidation** - Simplified accounting

### VPN Connectivity

#### Cloud VPN
- **IPSec encryption** - Encrypted tunnels
- **High availability** - Route-based VPN
- **Dynamic routing** - BGP support
- **AWS/Azure compatible** - Interoperability

#### Cloud Interconnect
- **Dedicated connection** - 10/100 Gbps
- **Lower latency** - Private path
- **Dedicated interconnect** - Physical connection
- **Partner interconnect** - 50 Mbps - 10 Gbps

### Private Service Connection

#### Private Service Access
- **Database access** - CloudSQL, Memorystore
- **VPC peering** - Service network peering
- **No internet routing** - Private connection
- **IP range allocation** - Service peering range

#### Private Google Access
- **Google API access** - Internal routing
- **No public IP** - Instances without external IP
- **Cloud NAT** - Outbound NAT capability
- **Route configuration** - Automatic routes

## Network Service Tier

### Premium Tier
- **Global routing** - Anycast routing
- **High availability** - Multi-region HA
- **Lower latency** - Optimized paths
- **Higher cost** - Premium pricing

### Standard Tier
- **Regional routing** - Region-based
- **Lower cost** - Economy pricing
- **Sufficient latency** - Most use cases
- **No multi-region** - Regional only

## Load Balancing

### Global Load Balancing
- **Cloud Load Balancing** - Anycast IP
- **Cross-region** - Global distribution
- **Auto-scaling** - Dynamic capacity
- **SSL offloading** - HTTPS termination

**Load Balancer Types**
- **Network LB** - Layer 4, high throughput
- **HTTP(S) LB** - Layer 7, path-based routing
- **SSL Proxy LB** - Non-HTTP protocols
- **TCP Proxy LB** - TCP connection pooling

## Network Services

### Cloud DNS
- **Managed DNS** - Google-hosted zones
- **Private zones** - VPC-scoped DNS
- **DNS peering** - Zone sharing
- **DNSSEC** - DNS security extensions

### Cloud NAT
- **Outbound NAT** - Instance internet access
- **Stateful** - Connection tracking
- **Port mapping** - Automatic port allocation
- **Centralized** - Per-route gateway

### Cloud Armor
- **DDoS protection** - Attack mitigation
- **WAF rules** - Application protection
- **Geo-blocking** - Geographic filtering
- **Rate limiting** - Traffic rate control

## Monitoring & Observability

### VPC Flow Logs
- **All traffic** - Complete visibility
- **Sampling rate** - Configurable sampling
- **Metadata** - Rich flow information
- **Integration** - Cloud Logging, BigQuery

### Metrics & Insights
- **Firewall rules** - Rule hit count
- **Routes** - Route utilization
- **Connections** - Connection tracking
- **Bandwidth** - Traffic analysis

## Best Practices

### Network Design
- **Subnet planning** - Future-proof sizing
- **Firewall least privilege** - Minimal rules
- **Cloud Router** - Dynamic routing
- **Multiple regions** - High availability

### Security
- **IAM policies** - Least privilege access
- **Firewall rules** - Explicit allow
- **Cloud Armor** - DDoS/WAF protection
- **VPC Service Controls** - Perimeter security

### Performance
- **Premium tier** - Global optimizations
- **Private service access** - No internet routing
- **Cloud CDN** - Content caching
- **Cloud Interconnect** - High-bandwidth connectivity

### Cost Optimization
- **Standard tier** - Cost savings
- **Egress pricing** - Monitor data transfer
- **Shared VPC** - Resource consolidation
- **Committed use discounts** - Capacity discounts

---

**Reference:** GCP VPC Documentation
**Last Updated:** 2025-11-19
