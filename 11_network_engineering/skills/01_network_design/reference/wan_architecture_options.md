# WAN Architecture Options

## Introduction
WAN (Wide Area Network) design connects geographically distributed sites. This reference covers topology options, technologies, and design patterns.

## WAN Topology Models

### Hub-and-Spoke Model

```
Architecture:
              Internet/MPLS
                  Cloud
                    │
                    │
            ┌───────┴───────┐
            │               │
        ┌───┴────┐      ┌──┴────┐
        │Hub Site│      │Backup │
        │(Primary)      │(Optional)
        └───┬────┘      └──┬────┘
            │               │
      ┌─────┼────────────┬──┼───────┐
      │     │            │  │       │
    ┌─┴─┐ ┌─┴─┐       ┌─┴──┘   ┌──┴─┐
    │B-1│ │B-2│ ...   │B-10    │B-11│
    └───┘ └───┘       └─────┘  └────┘

Spoke Sites: Branch offices, remote locations
Hub Site: Headquarters, Data center

Characteristics:
- All traffic flows through hub
- Centralized security and policy
- Hub becomes bottleneck
- Single point of failure
- Simplest to manage

Bandwidth sizing:
  Hub uplink = Sum of all spoke uplinks
  Example: 11 branches × 50 Mbps = 550 Mbps minimum hub link
```

### Full Mesh Model

```
Complete Connectivity:

    Branch-1
     /│ │\
    / │ │ \
   /  │ │  \
Branch-2  Branch-3
   \  │ │  /
    \ │ │ /
     \│ │/
    Branch-4

Each site connects to every other site:
- Number of connections = N × (N-1) / 2
- 5 sites = 10 point-to-point connections
- 10 sites = 45 point-to-point connections

Benefits:
- Optimal path between any two sites
- No single point of failure
- Direct communication
- Lower latency

Disadvantages:
- High cost (N² scaling)
- Complex management
- Difficult to add new sites
- Overkill for most enterprises

Use case: Financial trading floors, real-time systems, <5 sites
```

### Partial Mesh (Hybrid) Model

```
Strategic Full Mesh + Hub-and-Spoke:

                Data Center A
                      │
      ┌───────────────┼───────────────┐
      │               │               │
Data Ctr B        Regional1      Regional2
      │    \         /│\          /│
      │     \       / │ \        / │
      │      \     /  │  \      /  │
   ┌──┴──┐  ┌─────┐  ┌─────┐ ┌────┴─┐
   │ B-1 │  │ B-2 │  │ B-3 │ │ B-4 │
   └─────┘  └─────┘  └─────┘ └─────┘

Tier-1 (Data Centers): Full mesh (direct links)
Tier-2 (Regional): Multiple connections
Tier-3 (Branches): 1-2 connections to regional hub

Design benefits:
- Redundancy where it matters
- Cost optimization
- Balanced performance
- Scalable growth
```

## WAN Technologies

### MPLS (Multiprotocol Label Switching)

```
Architecture:
  Provider backbone creates secure paths (LSPs)
  Each site connects via MPLS circuits

Configuration example:

Site A ─── 50 Mbps MPLS to Site B
       └── 100 Mbps MPLS to Site C (primary)
           └── 50 Mbps MPLS to Site C (backup)

MPLS Label Format:
  ┌────────────────┬─────────┬──────┬──────┐
  │ Label (20b)    │ Exp (3b)│ S (1b)│TTL(8b)
  └────────────────┴─────────┴──────┴──────┘

Benefits:
- Guaranteed QoS
- Traffic engineering
- Provider-managed redundancy
- VPN support (MPLS VPN)

Disadvantages:
- Requires carrier support
- Higher cost than internet
- Provider dependent
- Setup time: 2-4 weeks

Typical pricing: $500-$2000/month per site
```

### SD-WAN (Software-Defined WAN)

```
Modern, programmable WAN approach:

Architecture:
  ┌─────────────────────────────────────┐
  │    SD-WAN Controller (Cloud-based)   │
  │    - Path optimization              │
  │    - Application awareness          │
  │    - QoS management                 │
  └─────────────────────────────────────┘
           ↑   ↑   ↑   ↑
           │   │   │   │
     ┌─────┴─┐ │   │ ┌─┴─────┐
     │Branch1│ │   │ │Branch2│
     │CPE    │ │   │ │CPE    │
     └─────┬─┘ │   │ └─┬─────┘
           │   │   │   │
      ┌────┴───┼───┼───┴────┐
      │ Multiple Path Options│
      │ - Internet (cheap)   │
      │ - MPLS (reliable)    │
      │ - LTE (mobile)       │
      │ - Satellite (remote) │
      └──────────────────────┘

Benefits:
- Uses multiple links simultaneously
- Automatic failover
- Application-aware routing
- Lower cost (internet-based)
- Easy scaling

Example deployment:
  Site A:
    - Primary: 100 Mbps Internet (cheap)
    - Secondary: 50 Mbps 4G LTE (mobile backup)
    - Failover: Automatic, <100ms
    - Cost: $300/month total

  Traditional approach (same requirement):
    - Primary: MPLS 100 Mbps ($1,500/month)
    - Secondary: MPLS 50 Mbps ($800/month)
    - Total: $2,300/month
```

### IPsec VPN

```
Internet-based encryption tunnels:

Configuration:
  Site A Router ─── IPsec Tunnel ─── Site B Router
         │                                  │
         └──────── Internet ────────────────┘

IPsec Stack:
  ┌──────────────────────────┐
  │ IKE (Key negotiation)    │ UDP 500
  │ ESP (Encryption)         │ IP Protocol 50
  │ AH (Authentication)      │ IP Protocol 51
  └──────────────────────────┘

Encryption algorithms:
  - AES-256 (strong)
  - AES-192 (good)
  - 3DES (legacy, avoid)

DPD (Dead Peer Detection):
  - Detects link failure: 3-10 seconds
  - Automatic renegotiation
  - Convergence time: 10-30 seconds

Advantages:
- Lowest cost (uses existing internet)
- Flexible routing
- Portable (works with any ISP)
- Easy to scale

Disadvantages:
- Variable latency
- No guaranteed QoS
- Internet-dependent
- CPU intensive (encryption)

Typical cost: $0 (software) to $5,000 (hardware)
```

## WAN Design Patterns

### Multi-ISP Design

```
Internet diversity pattern:

        ┌────────────────────────────┐
        │   HQ Data Center           │
        └────────┬─────────┬─────────┘
                 │         │
         ┌───────┘         └────────┐
         │                          │
      ┌──┴──┐                   ┌──┴──┐
      │ISP A│                   │ISP B│
      │BGP  │                   │BGP  │
      │AS65│                   │AS6502
      └─────┘                   └─────┘
        Internet Connection Options:
        - AT&T fiber: 1 Gbps
        - Verizon fiber: 1 Gbps

BGP Configuration (Dual BGP):

router bgp 65001
  neighbor 192.0.2.1 remote-as 65100  (ISP A gateway)
  neighbor 203.0.113.1 remote-as 65101 (ISP B gateway)
  !
  address-family ipv4 unicast
    neighbor 192.0.2.1 activate
    neighbor 203.0.113.1 activate
    !
    network 10.0.0.0 mask 255.0.0.0
    !
    maximum-paths 2  (load balance across both)

Load balancing:
  - Traffic distributed: 50% ISP A, 50% ISP B
  - Automatic failover if one fails
  - Convergence: <30 seconds
  - Preferred over failover approaches
```

### Branch Site Connectivity

```
Typical branch design (25-50 users):

   ┌──────────────────────────────────┐
   │   Branch Office (25-50 users)    │
   └──────────────────────────────────┘
             │              │
       100 Mbps Fiber  20 Mbps 4G LTE
       (primary)        (backup)
             │              │
       ┌─────┴──────────────┴─────┐
       │    Branch CPE Router     │
       │  - SD-WAN enabled        │
       │  - Dual WAN              │
       │  - Local security        │
       └────────────┬─────────────┘
                    │
              IPsec/MPLS tunnel
                    │
         ┌──────────┴──────────┐
         │   Data Center       │
         │   (HQ)              │
         └─────────────────────┘

Configuration (Cisco ASR 1000):
  Interface Gi0/0/0:
    Internet provider 1 (primary)
    IP: 203.0.113.50
    Speed: 100 Mbps

  Interface Cellular0/1/0:
    4G LTE backup
    IP: Obtained via DHCP
    Speed: 20 Mbps

  IPsec Tunnel:
    Source: Primary or backup interface
    Destination: DC Site
    Route: Default route via tunnel
    Traffic: All from branch to DC

  Failover trigger:
    Primary link down → Reroute to backup
    Backup link down → Reroute to primary
    Time: <100ms (SD-WAN) to 3-5 sec (traditional)
```

## WAN Design Considerations

### Bandwidth Sizing

```
Calculation method:

1. Identify traffic types:
   - Data center access: 30%
   - Cloud services: 40%
   - Internet: 20%
   - VoIP/Video: 10%

2. Peak usage estimation:
   - 100 users
   - Average per-user: 2 Mbps
   - Peak ratio: 2.5x
   - Peak total: 100 × 2 × 2.5 = 500 Mbps

3. Add headroom:
   - Peak: 500 Mbps
   - Growth (2 years): 30% = 150 Mbps
   - Protocol overhead: 5% = 25 Mbps
   - Target: 675 Mbps

4. Choose circuit:
   - 1 Gbps primary (MPLS or Fiber)
   - 500 Mbps backup (LTE or secondary ISP)
   - Cost: $5,000-$10,000/month
```

### Latency Requirements

```
Application Latency Thresholds:

Application | Max Latency | Min Available | Priority
------------|------------|---------------|----------
VoIP        | <150ms     | 99.9%         | High
Video Call  | <200ms     | 99.9%         | High
Real-time DB| <10ms      | 99.99%        | Critical
Web browsing| <500ms     | 95%           | Low
Email       | <2000ms    | 99%           | Low
Backup      | <5000ms    | 80%           | Very low

Design pattern:
  VoIP/Video → Prioritized queue, guaranteed 50 Mbps
  DB/Apps    → Standard queue, best-effort
  Backup     → Low-priority queue, off-peak only
  Internet   → Remaining bandwidth
```

### Convergence Time

```
Failover scenario - Branch loses primary link:

Traditional Approach (3-5 seconds):
  1. Link down detected: 1 sec
  2. Routing protocol detects: 1-2 sec
  3. BGP/OSPF reconverges: 1-2 sec
  4. Data reroutes: 1 sec
  Total: 3-5 seconds
  Impact: VoIP calls drop, TCP resets

SD-WAN Approach (<1 second):
  1. Link quality detected: 0.1 sec
  2. Controller notified: 0.1 sec
  3. Alternate path activated: 0.2 sec
  4. Data reroutes: 0.1 sec
  Total: <0.5 seconds
  Impact: Minimal, flows continue

MPLS Fast Reroute (<50ms):
  1. Link down: 0 sec
  2. Pre-computed backup: 0.01 sec
  3. Traffic rerouted: 0.02 sec
  Total: <0.05 seconds
  Impact: No loss for well-designed FRR
```

## WAN Design Selection Matrix

| Factor | Hub-Spoke | Full Mesh | Partial Mesh | SD-WAN |
|--------|-----------|-----------|--------------|--------|
| Cost | Low | Very High | Medium | Medium |
| Scalability | High | Low | Medium | High |
| Latency | Variable | Optimal | Good | Variable |
| Complexity | Simple | Complex | Medium | Medium |
| Redundancy | Low | Very High | Medium | High |
| Sites | 5-100 | 2-5 | 5-50 | Any |
| Best for | Branch networks | Tier-1 sites | Mixed | Modern |

---

**Reference Version:** 1.0
**Last Updated:** November 2025
**Standards:** RFC 2547 (MPLS VPN), RFC 4301 (IPsec), SDNF
