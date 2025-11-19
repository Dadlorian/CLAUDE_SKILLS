# SD-WAN Reference

## Definition
Software-Defined WAN (SD-WAN) applies SDN principles to WAN infrastructure, enabling centralized management, application-aware routing, and multi-path optimization.

## SD-WAN Architecture

### Three-Tier Model
```
Applications/Branches
    ↓ (CPE devices - Cisco vEdge, Versa, Fortinet, etc.)
  vEdge/CPE
    ↓ (Control and Data Plane)
WAN Cloud (Multi-path)
    ↓ (MPLS, Internet, 4G/LTE, Satellite)
Head Office/Data Center
    ↓
Applications
```

### Key Components

#### vEdge (Virtual Edge) / CPE (Customer Premises Equipment)
**Role**: Branch edge device
```
vEdge
├─ WLAN Interface
├─ LAN Interface (local connections)
├─ Multiple WAN links (MPLS, Internet, 4G)
│  ├─ Link 1: MPLS (primary)
│  ├─ Link 2: Internet (backup)
│  └─ Link 3: 4G (failover)
├─ IPsec Tunnels (to hub/other branches)
├─ Local Forwarding
└─ Policy Enforcement
```

#### SD-WAN Controller (Orchestrator)
**Role**: Centralized management and control
```
SD-WAN Controller
├─ Device Onboarding
├─ Policy Management
├─ Traffic Engineering
├─ Analytics & Monitoring
├─ Application Recognition
└─ Optimization Rules
```

#### SD-WAN Manager
**Role**: Operations and visibility
- Dashboard and reporting
- Policy visualization
- Application monitoring
- Event alerting

## Control vs Data Plane

### Control Plane Functions
- **Device Registry**: Maintain vEdge inventory
- **Key Management**: IPsec key distribution
- **Policy Distribution**: Push policies to vEdges
- **Telemetry**: Collect performance data

### Data Plane Functions
- **Packet Forwarding**: Local switching/routing
- **Application Recognition**: DPI for application identification
- **Traffic Engineering**: Route selection based on policy
- **IPsec Encryption**: Secure tunnels to hub/peers
- **QoS Application**: Priority marking per app

## SD-WAN Protocols

### Overlay Tunnels
**IPsec**: Default tunnel protocol
- Encryption: AES-256
- Authentication: SHA-256
- Tunnel per WAN link

**DTLS**: Optional (lower CPU vs IPsec)
- Datagram TLS
- Reduced overhead

### Control Plane Protocols

**TLOC (Transport Locator) Routing**:
- TLOC = (IP address, Color, Carrier)
- Color represents WAN type (mpls, internet, 4g)
- Preference/Restriction policies

**OMP (Overlay Management Protocol)**:
- Proprietary control plane protocol
- Advertises TLOC routes and policies
- Builds overlay mesh

## Application Routing

### DPI (Deep Packet Inspection)
```
Packet arrives at vEdge
    ↓
DPI Engine (signature-based)
    ├─ Application ID (web, video, voice, etc.)
    ├─ Traffic Class (critical, high, medium, low)
    └─ Tunnel Selection
```

### Policy-Based Routing

**Example Policy**:
```
Application: Salesforce (SaaS cloud app)
├─ Best Path: Internet (direct to cloud)
├─ Preference: 1 (highest)
└─ Failover: MPLS

Application: Corporate ERP
├─ Best Path: MPLS (via DC)
├─ Preference: 1
└─ Failover: Internet

Application: YouTube
├─ Allow: Yes/No or Limited (quota)
└─ Path: Internet (if allowed)
```

### QoS and Queuing
```
Traffic Classification
    ├─ Real-Time (voice/video): Priority queue
    ├─ Transactional (web): Standard queue
    ├─ Bulk (backup): Low-priority queue
    └─ Management: Control plane priority
```

## Multi-Path Optimization

### EDCA (Equal-Cost Delivery Algorithm)
**Concept**: Use multiple paths simultaneously
```
                 Path 1 (MPLS)
Data Stream  ──┬──────────→ Hub
                 Path 2 (Internet)

Result: ~2x throughput, packet-level load balance
```

### Path Metrics
- **Latency**: One-way delay
- **Jitter**: Latency variation
- **Loss**: Packet loss percentage
- **Bandwidth**: Available capacity
- **Cost**: Monthly price (MPLS vs Internet)

### Intelligent Path Selection
```
Continuous Monitoring
    ↓
Measure path metrics every 30-60 seconds
    ↓
Compare against policy thresholds
    ↓
Switch traffic if better path available
    ↓
Automatic failover on link failure
```

## Branch Resiliency

### Failover Scenarios

#### Primary Link Failure
```
Normal:
Branch ──[MPLS]→ Hub ──→ DC

Link Down:
Branch ──[Internet]→ Hub ──→ DC
        (automatic failover)
```

#### Hub-to-Branch Connection
**Active-Active Hub Redundancy**:
- Multiple hub connections
- Load distribution
- Fast failover

## Branch Connectivity Models

### Hub-and-Spoke
```
        Hub
       / | \
      /  |  \
    B1  B2  B3
```
- Simplest model
- All traffic through hub
- Easy to monitor/manage

### Full Mesh
```
B1 ←→ B2
↑     ↓
B3 ←→ B4
```
- Branch-to-branch direct
- Better for regional offices
- More complex management

### Hybrid Mesh
```
Hub (central)
├─ Spoke (branch offices)
└─ Mesh (regional offices)
```
- Balance of performance and management
- Selective direct paths

## Deployment Scenarios

### Cloud-First Branch
```
Branch vEdge
├─ Direct to SaaS apps (Internet path)
├─ Direct to public cloud (Internet path)
├─ Back to DC via MPLS (for legacy apps)
└─ Optimized for cloud-native
```

### Hybrid Cloud Connectivity
```
Branch → Internet → Cloud Provider → Public SaaS
           ↓
        Private Cloud (DC)
```

## Security Features

### Zero-Trust Implementation
```
Device Authentication
    ↓ Verify device identity/compliance
vEdge ──→ SD-WAN Controller
    ↓ Issue certificate
Access Granted
    ↓
Policy Enforcement per application/user
```

### DLP (Data Loss Prevention)
- Application-based blocking
- URL filtering
- File transfer restrictions

### Integrated Firewall
- Stateful inspection
- Intrusion prevention
- Threat prevention (sandbox integration)

### Encryption
- All traffic tunneled (IPsec/DTLS)
- Optional: SSL/TLS inspection
- Per-app encryption policies

## Analytics and Monitoring

### Real-Time Visibility
```
SD-WAN Manager Dashboard
├─ Network Health (link status, quality)
├─ Application Performance (latency, jitter)
├─ Device Status (CPU, memory, tunnel count)
├─ Traffic Statistics (bandwidth by app)
└─ Alerts (threshold breaches, failures)
```

### Historical Analytics
- Application trend analysis
- Path utilization over time
- Cost optimization recommendations
- Anomaly detection

### Integration
- SNMP export
- NetFlow/sFlow
- REST API
- Syslog alerts

## Common SD-WAN Platforms

### Cisco Meraki / Cisco Catalyst
- Cloud-managed
- Automatic device provisioning
- Zero-touch deployment

### Cisco vSmart + vEdge + vManage
- On-premises option
- Full control and visibility
- Largest install base

### Versa
- Cloud and on-premises
- Good analytics
- Strong encryption options

### Fortinet FortiGate
- Integrated with firewall
- Good performance
- Enterprise support

### VMware VeloCloud (now Broadcom)
- AI-powered routing
- Private cloud option
- Enterprise scale

### Arista 400 Series
- Hardware-based SD-WAN
- High performance
- Carrier-grade

## SD-WAN vs MPLS

| Aspect | SD-WAN | MPLS |
|--------|--------|------|
| **Cost** | Lower (uses Internet) | Higher (dedicated circuits) |
| **Setup** | Quick (weeks) | Slow (months) |
| **Scalability** | Easy (add branches) | Complex (circuit management) |
| **Application Awareness** | Yes (DPI) | Limited |
| **Flexibility** | High | Low |
| **Carrier Dependence** | Less | More |
| **Reliability** | Good (multi-path) | Excellent (SLA-backed) |
| **Migration** | Parallel with MPLS | Forklift replacement |

## Deployment Stages

### Stage 1: Baseline
- Establish SD-WAN fabric
- Configure basic policies
- Monitor baseline performance

### Stage 2: Optimization
- Implement DPI policies
- Application-aware routing
- Performance tuning

### Stage 3: Security Integration
- Add DLP policies
- Firewall integration
- Threat prevention

### Stage 4: Cloud Integration
- Direct cloud paths
- SaaS acceleration
- Hybrid routing

## Best Practices

### Design
- Map applications to optimal paths
- Plan failover strategy
- Allocate sufficient bandwidth
- Design for redundancy

### Deployment
- Pilot at 1-2 sites
- Parallel run during cutover
- Staff training before rollout
- Phased rollout to 100% branches

### Operations
- Monitor path quality continuously
- Tune policies based on metrics
- Regular firmware updates
- Backup and recovery planning

### Security
- Enable encryption on all paths
- Implement zero-trust policies
- Monitor for anomalies
- Regular security audits

## Common Challenges

### Challenge: Legacy Application Compatibility
- **Solution**: MPLS fallback for sensitive apps

### Challenge: ISP Quality Variations
- **Solution**: Multi-ISP paths, SLA monitoring

### Challenge: Mobile/Cellular Reliability
- **Solution**: 4G as backup, not primary

### Challenge: Latency-Sensitive Apps
- **Solution**: Smart path selection, optimization

### Challenge: Management Complexity
- **Solution**: Automation, centralized policies
