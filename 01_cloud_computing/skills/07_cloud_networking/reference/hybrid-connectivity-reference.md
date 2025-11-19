# Hybrid Connectivity Reference

## Introduction

Hybrid connectivity bridges on-premises data centers with cloud infrastructure, enabling organizations to leverage cloud benefits while maintaining existing investments and meeting compliance requirements.

## Connectivity Options Overview

### Dedicated Connections

**AWS Direct Connect**:
- Private, dedicated network connection
- 1 Gbps or 10 Gbps (dedicated)
- 50 Mbps to 500 Mbps (hosted)
- Consistent network performance
- Reduced data transfer costs

**Azure ExpressRoute**:
- Private connection to Azure
- 50 Mbps to 10 Gbps
- Microsoft peering and private peering
- Global reach for multi-region
- Integration with Office 365 and Dynamics 365

**GCP Cloud Interconnect**:
- Dedicated Interconnect: 10 Gbps or 100 Gbps
- Partner Interconnect: 50 Mbps to 50 Gbps
- Direct connection to GCP
- Low latency, high bandwidth

### VPN Connections

**Site-to-Site VPN**:
- Encrypted tunnel over internet
- Lower cost than dedicated
- Variable performance
- Quick to set up
- Multiple VPN tunnels for redundancy

**Comparison Table**:

| Feature | Dedicated | VPN |
|---------|-----------|-----|
| Bandwidth | High (1-100 Gbps) | Medium (up to 1.25 Gbps) |
| Latency | Low, consistent | Variable |
| Cost | Higher | Lower |
| Setup Time | Weeks | Hours |
| Security | Private connection | Encrypted tunnel |
| Availability | 99.9%+ SLA | Variable |

## AWS Direct Connect

### Architecture Components

**Connection Types**:

1. **Dedicated Connection**:
   - Physical Ethernet connection
   - 1 Gbps, 10 Gbps, 100 Gbps
   - Direct to AWS
   - Single customer

2. **Hosted Connection**:
   - Through AWS Partner
   - 50 Mbps to 10 Gbps
   - Shared infrastructure
   - Faster provisioning

### Virtual Interfaces (VIFs)

**Private VIF**:
```
On-Premises --> Direct Connect --> Virtual Private Gateway --> VPC
```

**Public VIF**:
```
On-Premises --> Direct Connect --> AWS Public Services (S3, DynamoDB)
```

**Transit VIF**:
```
On-Premises --> Direct Connect --> Transit Gateway --> Multiple VPCs
```

### High Availability Design

**Dual Direct Connect**:

```
Data Center                  AWS Region
    |                             |
    +--- DX Connection 1 ----> VGW/TGW
    |                             |
    +--- DX Connection 2 ----> VGW/TGW

(Active/Active or Active/Passive)
```

**Hybrid with VPN Backup**:

```
Primary:   Direct Connect
Backup:    VPN over Internet
Failover:  Route-based (BGP)
```

### BGP Configuration

**BGP Settings**:
- ASN: Customer ASN (private: 64512-65534)
- BGP authentication: MD5
- Prefixes: Advertised routes
- Communities: Route tagging

**Example**:
```
Customer ASN: 65001
AWS ASN: 7224 (us-east-1)
BGP Hold Time: 90 seconds
```

## Azure ExpressRoute

### Architecture Components

**Peering Types**:

1. **Azure Private Peering**:
   - Access to Azure VNets
   - Virtual network gateway
   - Private IP addressing

2. **Microsoft Peering**:
   - Access to Microsoft services
   - Public IP addressing
   - Office 365, Dynamics 365, Azure public services

### Circuit Models

**Circuit SKUs**:
- Local (single metro area)
- Standard (same geopolitical region)
- Premium (global connectivity)

**Bandwidth Options**:
- 50 Mbps, 100 Mbps, 200 Mbps
- 500 Mbps, 1 Gbps, 2 Gbps
- 5 Gbps, 10 Gbps

### High Availability

**Zone-Redundant Gateway**:
```
ExpressRoute Circuit
    |
    +---> Primary Connection
    |
    +---> Secondary Connection
    |
Zone-Redundant VNet Gateway
```

**Geo-Redundant Setup**:
```
Primary Region:
  ExpressRoute Circuit --> VNet

Secondary Region:
  ExpressRoute Circuit --> VNet

Global VNet Peering
```

### ExpressRoute Global Reach

**Cross-Location Connectivity**:

```
Office (Location A)      Data Center (Location B)
        |                        |
   ExpressRoute            ExpressRoute
        |                        |
        +------ Global Reach ----+
                    |
              Azure Backbone
```

## GCP Cloud Interconnect

### Dedicated Interconnect

**Architecture**:

```
On-Premises Router
    |
    +--- 10 Gbps Link --> Google Edge
    |
    +--- 10 Gbps Link --> Google Edge
          (Redundant)
              |
           GCP VPC
```

**Requirements**:
- 10 Gbps or 100 Gbps
- Single-mode fiber
- 10GBASE-LR or 100GBASE-LR
- LACP for bundling

### Partner Interconnect

**Tiers**:
- 50 Mbps, 100 Mbps, 200 Mbps
- 300 Mbps, 400 Mbps, 500 Mbps
- 1 Gbps, 2 Gbps, 5 Gbps, 10 Gbps, 20 Gbps, 50 Gbps

**Architecture**:
```
On-Premises --> Service Provider --> Google Partner Network --> VPC
```

### Cloud VPN Integration

**Hybrid Connectivity**:

```
Primary:   Cloud Interconnect (high bandwidth)
Backup:    Cloud VPN (failover)
Protocol:  BGP for dynamic routing
```

## Site-to-Site VPN

### AWS VPN

**Architecture**:

```
On-Premises VPN Device
    |
    +--- Tunnel 1 (AZ-1) --+
    |                      |
    +--- Tunnel 2 (AZ-2) --+--> Virtual Private Gateway --> VPC
```

**Specifications**:
- IPsec VPN tunnels
- IKEv1 and IKEv2
- Up to 1.25 Gbps per tunnel
- BGP or static routing
- Dual tunnels for HA

**VPN over Direct Connect**:
```
On-Premises --> Direct Connect --> Transit Gateway --> VPN
(Encrypted traffic over private connection)
```

### Azure VPN Gateway

**Gateway Types**:

**Route-Based**:
- Dynamic routing with BGP
- Multiple site-to-site connections
- Point-to-site VPN
- ExpressRoute coexistence

**Policy-Based**:
- Static routing
- Single site-to-site connection
- Legacy support

**Gateway SKUs**:
- Basic: 100 Mbps
- VpnGw1: 650 Mbps
- VpnGw2: 1 Gbps
- VpnGw3: 1.25 Gbps
- VpnGw4/5: Higher performance

### GCP Cloud VPN

**Types**:

**HA VPN**:
- 99.99% SLA
- Two tunnels to two interfaces
- Dynamic routing (BGP)
- Regional resource

**Classic VPN**:
- 99.9% SLA
- Single tunnel
- Static or dynamic routing
- Legacy option

**Architecture**:
```
On-Premises Router
    |
    +--- Tunnel 1 --> HA VPN Gateway Interface 0
    |                       |
    +--- Tunnel 2 --> HA VPN Gateway Interface 1
                            |
                         VPC Network
```

## SD-WAN Integration

### Cloud-Integrated SD-WAN

**Architecture**:

```
Branch Offices (SD-WAN)
    |
    +--- Internet Path
    |
    +--- MPLS Path
    |
    +--- LTE/5G Path
         |
    SD-WAN Controller
         |
    Cloud Edge (Direct Connect/ExpressRoute)
         |
    Cloud VPC/VNet
```

**Benefits**:
- Application-aware routing
- Multiple transport links
- Centralized management
- Quality of Service (QoS)
- Cost optimization

### Vendor Solutions

**Major Providers**:
- Cisco SD-WAN (Viptela)
- VMware SD-WAN (VeloCloud)
- Silver Peak
- Fortinet
- Palo Alto Prisma SD-WAN

## Network as a Service (NaaS)

### Cloud Network Services

**Megaport**:
- On-demand connectivity
- Multi-cloud connections
- Software-defined networking
- Elastic scaling

**Equinix Network Edge**:
- Virtual network services
- Global interconnection
- On-demand provisioning

**PacketFabric**:
- Private, direct connectivity
- Multi-cloud networking
- Pay-as-you-go pricing

## Routing and Traffic Engineering

### BGP Routing

**Route Preferences**:

```
AWS:
1. Longest prefix match
2. AS_PATH (shortest)
3. Local preference

Azure:
1. Longest prefix match
2. AS_PATH length
3. Origin type

GCP:
1. Longest prefix match
2. AS_PATH length
```

**AS Path Prepending**:
```
Preferred Path: AS 65001
Backup Path:    AS 65001 65001 65001 (less preferred)
```

### Traffic Engineering

**Outbound Traffic Control**:
- BGP local preference
- AS path prepending
- MED (Multi-Exit Discriminator)

**Inbound Traffic Control**:
- Advertise specific prefixes
- AS path prepending
- BGP communities

## Security Considerations

### Encryption

**VPN Encryption**:
- IPsec: AES-256, SHA-256
- IKEv2 with Perfect Forward Secrecy
- Tunnel mode

**MACsec (Direct Connect)**:
- Layer 2 encryption
- 256-bit AES-GCM
- 10 Gbps and 100 Gbps

### Access Control

**Network Segmentation**:
- Separate VIFs/connections per environment
- Security groups and NACLs
- Firewall at edge

**Authentication**:
- BGP MD5 authentication
- Certificate-based VPN
- Pre-shared keys

### Monitoring and Logging

**Connection Monitoring**:
- BGP session status
- Tunnel status
- Bandwidth utilization
- Packet loss and latency

**Logging**:
- VPN connection logs
- Flow logs
- CloudWatch/Monitor metrics

## High Availability Patterns

### Active-Active

**Dual Connections**:
```
Both connections active
Traffic distributed via ECMP
Full redundancy
Increased bandwidth
```

### Active-Passive

**Primary/Backup**:
```
Primary: Direct Connect
Backup:  VPN (lower cost)
Failover: Automatic via BGP
```

### Multi-Region HA

**Global Redundancy**:

```
Region 1:               Region 2:
Direct Connect 1        Direct Connect 2
    |                       |
Transit Gateway 1       Transit Gateway 2
    |                       |
    +------- Peering -------+
```

## Performance Optimization

### Bandwidth Planning

**Calculate Requirements**:
```
Peak Usage + 30% headroom
Consider:
- Backup/replication traffic
- Bursty workloads
- Migration traffic
```

### Latency Reduction

**Strategies**:
- Colocation near cloud region
- Multiple connection points
- Direct Connect vs VPN
- Route optimization

### QoS and Traffic Shaping

**Prioritization**:
```
High Priority:   VoIP, video conferencing
Medium Priority: Transactional applications
Low Priority:    Backup, batch jobs
```

## Cost Optimization

### Direct Connect Pricing

**AWS Costs**:
- Port hours (dedicated connection)
- Data transfer out
- Hosted connection fees (partner)

**Cost Reduction**:
- Use VPC endpoints for AWS services
- Optimize data transfer patterns
- Consider hosted connections for lower bandwidth

### ExpressRoute Pricing

**Azure Costs**:
- Circuit (metered or unlimited data)
- Gateway charges
- Global Reach fees

**Optimization**:
- Unlimited data plan for high usage
- Zone-redundant vs standard gateway
- Regional vs premium circuit

### Data Transfer Optimization

**Strategies**:
- Compress data before transfer
- Use cloud services in same region
- Schedule large transfers off-peak
- Implement caching
- Optimize application protocols

## Troubleshooting

### Common Issues

**BGP Not Establishing**:
- Verify ASN configuration
- Check MD5 authentication
- Confirm IP addressing
- Review firewall rules

**High Latency**:
- Check physical path
- Verify QoS settings
- Analyze hop count
- Review bandwidth utilization

**Intermittent Connectivity**:
- Check for packet loss
- Verify redundancy configuration
- Review BGP flapping
- Analyze failover behavior

### Diagnostic Tools

**Network Testing**:
- ping, traceroute, MTR
- iperf for bandwidth testing
- BGP route analysis
- Packet capture (tcpdump, Wireshark)

**Cloud Provider Tools**:
- AWS Network Manager
- Azure Network Watcher
- GCP Network Intelligence Center

## Best Practices

### Design

1. Implement redundant connections
2. Use BGP for dynamic routing
3. Design for failure scenarios
4. Plan IP addressing carefully
5. Document network architecture

### Security

1. Enable encryption (VPN or MACsec)
2. Implement BGP authentication
3. Use security groups and NACLs
4. Monitor for anomalies
5. Regular security audits

### Operations

1. Monitor connection health
2. Set up alerting for failures
3. Document runbooks
4. Test failover regularly
5. Maintain network inventory

### Cost Management

1. Right-size bandwidth
2. Use appropriate connection type
3. Optimize data transfer
4. Monitor usage patterns
5. Review costs monthly

## Compliance and Governance

### Compliance Frameworks

**PCI-DSS**:
- Encrypted connections
- Network segmentation
- Access controls

**HIPAA**:
- Private connectivity preferred
- Encryption in transit
- Audit logging

**Data Sovereignty**:
- Keep data in specific regions
- Use private connections
- Document data flows

## Migration Strategies

### Phased Migration

**Approach**:
```
Phase 1: Establish connectivity
Phase 2: Migrate non-critical workloads
Phase 3: Migrate databases
Phase 4: Migrate critical applications
Phase 5: Decommission on-premises
```

### Hybrid Operating Model

**Long-Term Hybrid**:
- Keep sensitive data on-premises
- Cloud for compute and scaling
- Hybrid applications
- Data synchronization

## Conclusion

Hybrid connectivity is essential for cloud adoption, providing secure, reliable, and performant connections between on-premises and cloud infrastructure. Choose the right connectivity option based on bandwidth, latency, cost, and availability requirements.
