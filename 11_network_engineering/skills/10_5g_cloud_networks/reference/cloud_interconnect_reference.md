# Cloud Interconnect Reference

## Cloud Interconnect Overview

Multi-cloud interconnect strategies enable organizations to connect hybrid cloud environments with low-latency, high-bandwidth, and secure connections across providers.

## AWS Direct Connect

### Architecture

#### Physical Connection
- **Dedicated physical connection** - 1, 10, or 100 Gbps
- **Hosted connection** - Partner-provided (50 Mbps - 10 Gbps)
- **Redundant connectivity** - Multiple connections for HA
- **LAG (Link Aggregation Group)** - Multiple connections

#### Logical Interfaces

**VIF (Virtual Interface)**
- **Public VIF** - Public AWS services
- **Private VIF** - VPC access
- **Transit VIF** - Transit Gateway access
- **BGP session** - Dynamic routing

### Configuration

#### Connection Setup
1. Request Direct Connect connection
2. AWS allocates port and location
3. Establish physical connection
4. Configure VIFs
5. Enable BGP routing
6. Verify connectivity

#### BGP Configuration
```
BGP ASN: Customer-provided
AWS-side ASN: 64512 (private range)
Routing: Dynamic via BGP
Failover: Automatic convergence
```

### Use Cases
- **Consistent bandwidth** - No internet contention
- **Predictable latency** - Direct path
- **Data-intensive workloads** - Large data transfer
- **Real-time applications** - Low-latency needs
- **Compliance** - Dedicated path requirements

## Azure ExpressRoute

### Circuit Models

#### Microsoft Peering
- **Public Azure services** - SQL, Storage, Office 365
- **Public IP addresses** - Microsoft infrastructure
- **Route advertisements** - Service subnets
- **BGP sessions** - Provider-configured

#### Private Peering
- **VNet connectivity** - Azure virtual networks
- **Private IP** - VNet address space
- **Direct connection** - Dedicated path
- **BGP routing** - Dynamic routing

#### Azure Public Peering (Deprecated)
- **Legacy model** - Deprecated in 2019
- **Migrate to private/Microsoft** - Required
- **Windows Server AD** - Active Directory federation

### Redundancy Models

#### Dual Provider
- **Two different providers** - Provider redundancy
- **Different paths** - Path diversity
- **Active-active** - Load distribution
- **Costs** - Double bandwidth fees

#### Dual Connectivity
- **Same provider** - Provider redundancy
- **Different locations** - Geographic diversity
- **Primary/secondary** - Automatic failover
- **Managed by provider** - Provider-managed

### Configuration

#### Circuit Setup
1. Create ExpressRoute circuit
2. Request connection with provider
3. Obtain BGP configuration
4. Configure VNet gateway
5. Link circuit to VNet
6. Establish BGP session

#### BGP Parameters
```
Peer ASN: Customer ASN
Azure ASN: 12076 (public), 65200-65300 (private)
Route filtering: Optional
Community values: Tagging
```

## GCP Cloud Interconnect

### Dedicated Interconnect

#### Connection Details
- **10 Gbps or 100 Gbps** - Bandwidth options
- **Direct connection** - Physical fiber link
- **Multiple locations** - Worldwide presence
- **Redundant paths** - High availability

#### Configuration
1. Request dedicated connection
2. Provision at exchange location
3. Configure VLAN attachment
4. Establish BGP session
5. Advertise routes via BGP

### Partner Interconnect

**Service Providers**
- **Direct connection** - Through service provider
- **50 Mbps to 10 Gbps** - Flexible bandwidth
- **Simplified provisioning** - Provider-managed
- **Global reach** - Worldwide providers

### BGP Routing

```
GCP ASN: 15169
Customer ASN: User-provided
Route exchange: BGP advertisements
Community values: Tagging
AS Path: Route prioritization
```

## Multi-Cloud Interconnect Architecture

### Hub-and-Spoke Design

**Hub Model**
- **Single hub region** - Central connectivity
- **Spoke clouds** - AWS, Azure, GCP
- **Hub-based routing** - Transitive connectivity
- **Simplified management** - Central control point

**Implementation**
1. Establish hub cloud
2. Deploy interconnects to all spokes
3. Configure central routing
4. Implement routing policies
5. Monitor and optimize

### Mesh Design

**Full Mesh Connectivity**
- **Direct peer connections** - All-to-all
- **Optimal paths** - Direct routing
- **Higher operational overhead** - More connections
- **Better latency** - No transitive delays

**Implementation Challenges**
- **BGP complexity** - Multiple ASNs
- **Route aggregation** - Prefix optimization
- **Policy enforcement** - Consistent rules
- **Scaling limitations** - N² connections

### Hybrid Design

**Multi-Hub Architecture**
- **Regional hubs** - Per-region connectivity points
- **Hub peering** - Inter-hub communication
- **Spoke attachment** - To nearest hub
- **Geo-distributed** - Improved latency

## Network Slicing & VLANs

### VLAN Management

#### VPC/VNet Isolation
- **VLAN per VPC** - Isolated domains
- **VLAN ID assignment** - Provider-managed
- **Q-in-Q tagging** - VLAN stacking
- **MTU considerations** - 1500 vs 1522 bytes

### QoS Implementation
- **Traffic classification** - Service type
- **Rate limiting** - Bandwidth allocation
- **Priority queues** - Prioritization
- **SLA guarantees** - Service contracts

## Security

### Encryption Options

**Layer 2 Security**
- **VLAN isolation** - Logical separation
- **MAC filtering** - Address-based control
- **Port security** - Port lockdown
- **Link encryption** - Physical layer

**Layer 3 Security**
- **IPSec tunnels** - Encrypted overlays
- **BGP MD5** - Route authentication
- **BGP RPKI** - Route origin validation
- **Firewall rules** - Traffic filtering

### Access Control

**Provider Access**
- **Dedicated connection** - Provider-only
- **Port security** - Restricted access
- **VPN overlay** - Additional encryption
- **Multi-layer security** - Defense in depth

## Redundancy & Failover

### Failover Scenarios

#### Single Connection Failure
- **Automatic convergence** - BGP rerouting
- **RTO: < 60 seconds** - BGP convergence time
- **Manual intervention** - Optional
- **Automatic traffic reroute** - Via alternate path

#### Multi-Connection Strategy
- **Active-active load balancing** - Distribute traffic
- **Active-passive failover** - Standby connection
- **Cost vs availability** - Trade-off analysis
- **Geographic diversity** - Multi-region setup

### Health Monitoring

**BGP Health**
- **Session status** - Up/down monitoring
- **Route advertisements** - Prefix tracking
- **AS Path analysis** - Route quality
- **Community values** - Custom tagging

**Application Health**
- **Synthetic tests** - Connectivity verification
- **Path analysis** - Route validation
- **Latency monitoring** - Performance tracking
- **Packet loss detection** - Quality issues

## Capacity Planning

### Bandwidth Estimation
- **Current usage** - Baseline measurement
- **Growth projections** - Future demand
- **Peak utilization** - Peak planning
- **Utilization targets** - 70-80% rule

### Scaling Strategy
- **Incremental upgrades** - Staged migration
- **Graceful degradation** - Fallback paths
- **Cost optimization** - Right-sizing
- **Reserve capacity** - Contingency planning

## Management & Operations

### Configuration Management
- **IaC (Infrastructure as Code)** - Terraform modules
- **Version control** - Git-based configs
- **Change management** - Approval workflows
- **Audit trails** - Configuration history

### Monitoring & Observability
- **Connection status** - Up/down alerts
- **BGP metrics** - Route count, convergence
- **Bandwidth utilization** - Capacity monitoring
- **Latency analysis** - Performance tracking

## Cost Considerations

### Direct Connect/Interconnect Costs
- **Port hour charges** - Per-port cost
- **Data transfer charges** - Egress pricing
- **Redundant connections** - Additional costs
- **Partner interconnect** - Service provider fees

### Optimization Strategies
- **Reserved capacity** - Commitment discounts
- **Traffic engineering** - Efficient routing
- **Cloud acceleration** - Optimized paths
- **Regional deployments** - Reduced data transfer

---

**Reference:** AWS Direct Connect, Azure ExpressRoute, GCP Cloud Interconnect Documentation
**Last Updated:** 2025-11-19
