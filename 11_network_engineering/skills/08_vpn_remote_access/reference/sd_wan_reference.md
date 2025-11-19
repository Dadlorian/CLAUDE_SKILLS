# SD-WAN (Software-Defined Wide Area Network) Reference

## Architecture Overview

SD-WAN decouples network control from data forwarding, enabling intelligent, flexible WAN architectures with multiple transport options.

## Core Components

### 1. Control Plane
- **Orchestrator/Controller**: Centralized management and policy creation
- **Policy Engine**: Defines routing and security policies
- **Analytics**: Traffic analysis and optimization recommendations
- **Management Interface**: GUI or API for configuration

### 2. Data Plane
- **SD-WAN Edge Devices**: Customer premise equipment (CPE)
- **Multiple Transport Types**: MPLS, Internet, 4G/LTE, DIA
- **Encryption**: End-to-end tunnel encryption
- **Direct Internet Access**: Not backhauled through data center

### 3. Application Intelligence
- **Deep Packet Inspection (DPI)**: Application identification
- **Quality of Service (QoS)**: Per-application QoS policies
- **Path Selection**: Intelligent routing per application
- **Real-time Analytics**: Performance monitoring

## Key Technologies

### Cisco SD-WAN (Catalyst, Meraki)

#### Catalyst SD-WAN Architecture
- **vManage**: Management and orchestration
- **vSmart**: Central controller (policies, route updates)
- **vBond**: Bootstrapping and NAT traversal
- **Vedge/Cedge**: Edge devices (virtual or hardware)

#### Concepts
- **OMP (Overlay Management Protocol)**: Control plane protocol
- **TLOC (Transport Locator)**: Interface with specific transport
- **Tunnel Interface**: Encrypted overlay tunnels
- **Service Chain**: Apply services to traffic paths

#### Deployment Models
- **Controller-based**: Cisco vManage and vSmart
- **Controller-less**: Edge-to-edge, no centralized control
- **Hybrid**: Combination of both models

### Viptela Underlays and Overlays

#### Underlay Layer
- Physical transport (MPLS, Internet, 4G, DIA)
- Multiple providers supported
- Active-active or active-passive failover
- Cost optimization across transports

#### Overlay Layer
- SD-WAN tunnels over underlay
- Application-aware routing
- Per-packet load balancing possible
- Multipath support

### Vedge (Viptela Edge Devices)
- **Vedge 100**: Small branch
- **Vedge 1000**: Medium branch
- **Vedge 2000**: Large branch/data center
- **Vedge Cloud**: Virtual deployment on AWS, Azure

### Cedge (Cisco Edge Devices)
- Cisco IOS XE devices running SD-WAN
- **Catalyst 8000**: Modern Cisco edge platform
- Existing ISR, ASR platforms reused
- Native Cisco OS integration

## Application-Aware Routing

### Concept
- Applications (not just traffic) determine path
- Quality of Service (QoS) per application
- Performance requirements met per application class
- Automatic failover to alternate path if SLA violated

### Implementation
1. **Traffic Classification**
   - Deep Packet Inspection identifies application
   - URL filtering for web applications
   - DNS-based classification
   - Custom classification rules

2. **Policy Application**
   - SLA parameters per application (latency, jitter, loss)
   - Preferred transport (MPLS, Internet, etc.)
   - Priority and weight settings
   - Fallback path if primary unavailable

3. **Path Selection**
   - Real-time measurement of SLAs
   - Multiple path availability check
   - Automatic switchover if SLA violated
   - Per-packet load balancing option

### Example Policy
```
Application: Salesforce
  SLA: Latency < 50ms, Loss < 1%, Jitter < 10ms
  Primary Path: MPLS
  Backup Path: Internet
  Priority: High
  Encryption: AES-256

Application: YouTube
  SLA: Bandwidth 5Mbps
  Primary Path: Direct Internet
  Priority: Best Effort
  QoS: Limited to 20Mbps
```

## Zero-Touch Provisioning (ZTP)

### Process
1. **Physical Deployment**: Edge device shipped to branch
2. **Power On**: Device boots with factory configuration
3. **Automatic Discovery**: Device contacts orchestrator
4. **Certificate Exchange**: Device authenticated to controller
5. **Policy Download**: Device downloads site-specific policies
6. **Automated Configuration**: No manual CLI needed

### Benefits
- Rapid branch deployment
- Reduced field engineer time
- Consistent configuration across branches
- Error reduction

## Multi-Transport Optimization

### Transport Options
- **MPLS**: Predictable performance, managed service
- **Internet DIA**: Direct internet access, lowest cost
- **4G/LTE**: Backup transport, mobile connectivity
- **SD-WAN over MPLS**: Hybrid approach

### Transport Selection
- Primary and backup transports per site
- Automatic failover on path failure
- Load balancing across multiple transports
- Cost-based routing optimization

### Bandwidth Management
- Bandwidth available per transport
- WAN optimization integration
- Bandwidth reservation per application
- Congestion detection and rerouting

## Encryption and Security

### Control Plane Encryption
- IKEv2 with AES-256-GCM
- Perfect Forward Secrecy (PFS)
- Certificate-based authentication
- OMP encryption (IKE tunnels)

### Data Plane Encryption
- IPsec encryption of overlay tunnels
- End-to-end data encryption
- AES-256, AES-128 options
- No per-application encryption overhead

### Key Management
- Automatic key exchange via IKE
- Perfect Forward Secrecy support
- Key rotation policies
- Secure key storage

## Scalability and Performance

### Scalability
- **Hub-and-Spoke**: 1000s of branches
- **Any-to-Any**: Limited by controller
- **Multi-Region**: Regional controllers
- **Multi-Vendor**: Interoperability considerations

### Performance
- Throughput: Depends on hardware and encryption
- Latency: Minimal overlay overhead
- CPU: Hardware acceleration available
- Bandwidth: Efficient utilization across transports

## Management and Monitoring

### Centralized Management
- Single pane of glass for all branches
- Policy templates and enforcement
- Automated provisioning
- Bulk configuration changes

### Real-time Analytics
- Application performance monitoring
- Bandwidth utilization tracking
- Path quality metrics
- Anomaly detection

### Reporting
- SLA compliance reporting
- Transport cost analysis
- Application usage patterns
- Security event logs

## Integration with Other Technologies

### WAN Optimization
- Deduplication and compression
- Caching of frequently accessed content
- Application acceleration
- Bandwidth saving

### Firewalling
- Integrated stateful firewall
- Next-generation firewall (NGFW) features
- Threat prevention
- URL filtering and DNS security

### Routing
- BGP and OSPF support
- Static and dynamic routing
- Route redistribution
- Multipath routing

## Common Deployment Patterns

### Pattern 1: Internet + MPLS Hybrid
```
All Sites:
  Primary: MPLS (guaranteed SLAs)
  Backup: Internet DIA (auto-failover)

Critical Applications:
  Always use MPLS path

Non-Critical Applications:
  Use Internet for cost savings
```

### Pattern 2: Multi-Provider Redundancy
```
Site Configuration:
  Transport 1: ISP A Internet
  Transport 2: ISP B Internet
  Transport 3: 4G Mobile backup

Load Balancing:
  ISP A: 40% traffic
  ISP B: 40% traffic
  Backup: 20% (standby)
```

### Pattern 3: Regional Data Center
```
Branch to Regional DC:
  Application-aware routing
  Local break-out for internet applications
  Direct DC access for corporate apps

Regional DC Configuration:
  Multiple entry points for redundancy
  Application server placement
  Content caching
```

## Migration from Traditional WAN

### Assessment Phase
- Catalog existing WAN services (MPLS, DIA)
- Identify application requirements
- Current transport costs
- Performance SLA documentation

### Pilot Phase
- Deploy at selected sites
- Validate performance with existing transports
- Measure cost savings
- Assess operational impact

### Production Phase
- Phased rollout across organization
- Parallel run with legacy WAN
- Monitor and optimize policies
- Decommission old technologies

## Comparison with Traditional WAN

| Aspect | Traditional WAN | SD-WAN |
|--------|-----------------|--------|
| **Transport** | MPLS primary | Multiple options |
| **Cost** | Higher (MPLS) | Lower (Internet) |
| **Agility** | Slow changes | Fast policy updates |
| **Automation** | Manual config | Automated provisioning |
| **Scalability** | Limited | Highly scalable |
| **App-aware** | Limited | Full support |
| **Management** | Per-site CLI | Centralized GUI |
| **Reliability** | MPLS SLA | Dual/triple redundancy |

## Security Best Practices

1. **Encryption Always**: End-to-end encryption mandatory
2. **Authentication**: Mutual device authentication
3. **Access Control**: Restrict management access
4. **Monitoring**: Audit all policy changes
5. **Segmentation**: Separate traffic by security level
6. **DLP**: Data loss prevention on WAN traffic
7. **Threat Prevention**: Integrated IPS/IDS
8. **Logging**: Centralized security logging
