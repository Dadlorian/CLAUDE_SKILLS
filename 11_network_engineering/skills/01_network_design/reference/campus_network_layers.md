# Campus Network Layers

## Three-Tier Hierarchical Model Overview

The three-tier model separates network functions into distinct layers, each with specific responsibilities, creating a scalable, manageable network architecture.

```
                    ┌──────────────┐
                    │  Core Layer  │
                    │ (Backbone)   │
                    └──────────────┘
                           ▲
                  ┌────────┴────────┐
                  │                 │
         ┌────────▼────────┐ ┌─────▼────────┐
         │ Distribution    │ │ Distribution │
         │ Layer           │ │ Layer        │
         │ (Aggregation)   │ │ (Aggregation)│
         └────────┬────────┘ └─────┬────────┘
                  │                 │
         ┌────────┴─────────────────┴────────┐
         │                                   │
    ┌────▼────┐  ┌────────┐  ┌────────┐  ┌─▼────┐
    │ Access  │  │ Access │  │ Access │  │Access│
    │ Layer   │  │ Layer  │  │ Layer  │  │Layer │
    │(Building│  │(Building  │(Building  │(Build│
    │   A)    │  │   B)      │   C)      │ D)   │
    └─────────┘  └────────┘  └────────┘  └──────┘
        │            │          │          │
      Users       Users      Users      Users
```

## Access Layer

### Primary Functions
1. **Connectivity** - Provide network connectivity to end devices
2. **Port security** - Control device attachment
3. **VLAN membership** - Assign users to logical networks
4. **PoE delivery** - Power IP phones and wireless APs
5. **Link aggregation** - Uplink redundancy and bandwidth

### Access Layer Design

```
Access Switch Specifications:

Cisco Catalyst 9200L:
  - Throughput: 680 Gbps
  - Ports: 24-port, 48-port options
  - Uplink: 10G SFP+
  - PoE: 885W (24 ports) to 1000W (48 ports)
  - Latency: <3 microseconds
  - Price range: $15,000-$25,000 per switch

Arista 7050SX:
  - Throughput: 480 Gbps
  - Ports: 32 x 10G + 8 x 40G
  - PoE: Optional external
  - Redundancy: Dual power/fan
  - Price range: $12,000-$20,000 per switch

Placement:
  - One per building or floor
  - Max cable distance: 100 meters (twisted pair)
  - Max 100-150 users per switch
  - Dual uplinks to distribution layer
```

### Access Layer Configuration Example

```
Cisco Catalyst 9200L Configuration:

interface GigabitEthernet 1/0/1
 description Desktop PC - Finance
 switchport mode access
 switchport access vlan 20
 switchport port-security
 switchport port-security maximum 2
 spanning-tree portfast
 spanning-tree bpdu-guard enable
 !

interface GigabitEthernet 1/0/45
 description IP Phone - Finance
 switchport mode access
 switchport access vlan 110
 switchport voice vlan 110
 power inline auto
 !

interface GigabitEthernet 1/0/47
 description Wireless AP - Floor 2
 switchport mode access
 switchport access vlan 200
 power inline auto
 !

interface GigabitEthernet 1/0/48
 description Uplink to Distribution - Port-Channel
 channel-group 1 mode active
 !

interface Port-channel 1
 description Uplink to Distribution Layer
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40,50,100,110,120
 speed 10000
 duplex full
 !
```

### Access Layer Best Practices

```
Configuration Standards:
- Port descriptions: Mandatory for every port
- VLAN assignment: Explicit (no untagged traffic on trunk)
- Port security: Enabled on all access ports (MAC limit: 2)
- STP: PortFast enabled on all access ports
- BPDU Guard: Enabled on all access ports
- Storm control: Broadcast/multicast flood protection

Uplink configuration:
- EtherChannel to distribution (2-4 links)
- LACP for dynamic negotiation
- Minimum 10G speeds
- MTU 1500 (standard) or 9000 (jumbo for specific VLANs)

PoE Configuration:
- Power budgeting: Reserve 20% for growth
- Monitoring: Track power consumption
- IP phones: High priority
- Wireless APs: High priority
- Cameras: Medium priority
- Generic devices: Lower priority
```

## Distribution Layer

### Primary Functions
1. **Traffic aggregation** - Collect from multiple access switches
2. **Policy enforcement** - Apply QoS, ACLs, filtering
3. **VLAN routing** - Route between VLANs
4. **Redundancy** - Gateway redundancy with HSRP/VRRP
5. **Access list filtering** - Security enforcement

### Distribution Layer Design

```
Distribution Switch Specifications:

Cisco Catalyst 9500:
  - Throughput: 65 Tbps
  - Ports: 48 x 1/10G + 6 x 40/100G
  - VLAN capacity: 4,094 active
  - ACL capacity: Large
  - Latency: <1 microsecond
  - Price range: $50,000-$80,000

Arista 7050SX:
  - Throughput: 480 Gbps
  - Ports: 32 x 10G + 8 x 40G
  - VLAN capacity: 4,000+
  - Redundancy: Built-in
  - Price range: $25,000-$40,000

Placement:
  - One pair per building or site
  - Dual links to core layer
  - HSRP/VRRP for gateway redundancy
  - Maximum 16 access layer switches per distribution pair
```

### Distribution Layer Design Patterns

```
Distribution Layer Topology:

Building A:
  Access-A1 ─┐
             ├─→ Distribution-A (Primary)
  Access-A2 ─┘     │
                   │ Dual links (EtherChannel)
  Access-A3 ─┐     │
             ├─→ Distribution-B (Backup)
  Access-A4 ─┘     │
                   │ (HSRP/VRRP for gateway redundancy)

VLAN 20 (Finance):
  - Subnet: 10.10.20.0/24
  - Gateway (virtual): 10.10.20.1
  - Distribution-A (Active): 10.10.20.2
  - Distribution-B (Standby): 10.10.20.3
  - HSRP/VRRP priority on Dist-A: 150

Data flow (normal):
  Finance PC → Default gateway 10.10.20.1 (virtual)
            → ARP resolves to 10.10.20.2 (Dist-A)
            → Dist-A routes traffic to destination
```

### Distribution Layer Configuration Example

```
HSRP Configuration on Cisco Catalyst 9500:

interface Vlan 20
 ip address 10.10.20.2 255.255.255.0
 standby 20 ip 10.10.20.1
 standby 20 priority 150
 standby 20 preempt
 no shutdown

interface Vlan 30
 ip address 10.10.30.2 255.255.255.0
 standby 30 ip 10.10.30.1
 standby 30 priority 100
 standby 30 preempt
 no shutdown

interface Vlan 40
 ip address 10.10.40.2 255.255.255.0
 standby 40 ip 10.10.40.1
 standby 40 priority 150
 standby 40 preempt
 no shutdown

! Load balancing: Distribution-A active for VLANs 20,40
!                Distribution-B active for VLAN 30

! ACL enforcement
ip access-list extended FINANCE_ALLOW
 permit ip 10.10.20.0 0.0.0.255 10.10.0.0 0.0.15.255
 permit ip 10.10.20.0 0.0.0.255 10.10.120.0 0.0.0.255
 deny ip 10.10.20.0 0.0.0.255 10.10.30.0 0.0.0.255
 deny ip any any log

! Apply to VLAN interface
interface Vlan 20
 ip access-group FINANCE_ALLOW in
```

## Core Layer

### Primary Functions
1. **Backbone connectivity** - High-speed transport
2. **BGP routing** - Dynamic routing between network segments
3. **Traffic aggregation** - Maximum throughput
4. **Redundancy** - Multiple active paths
5. **Low latency** - Fast packet forwarding

### Core Layer Design

```
Core Switch Specifications:

Cisco Nexus 9516:
  - Throughput: 300 Tbps
  - Modules: 6 line cards, 2 fabric cards
  - Interface options: 40G, 100G, 400G
  - Redundancy: Dual supervisors, N+1 fabric
  - Price: $250,000-$400,000

Arista 7368:
  - Throughput: 300 Tbps
  - Fabric capacity: Modular
  - Interface speeds: 100G, 400G
  - Redundancy: Full
  - Price: $200,000-$350,000

Typical sizing:
  - Two core switches minimum
  - Full mesh or near-full mesh connectivity
  - Every distribution switch connects to both cores
  - Interface speeds: 100G minimum, 400G for large campuses
```

### Core Layer Topology Example

```
Full Mesh Core Design (5 distribution switches):

              ┌────────────┐
              │   Core-1   │
              │ IP: 10.255.1.1
              └────────────┘
              ╱    │    ╲
             ╱     │     ╲
            ╱      │      ╲
        ┌──┴──┬────┼────┬──┴──┐
        │     │    │    │     │
    Dist-A Dist-B Dist-C Dist-D Dist-E
        │     │    │    │     │
        └──┬──┴────┼────┴──┬──┘
           │       │       │
           │   ┌───┼───┐   │
           └─┐ │   │   │ ┌─┘
             │ │   │   │ │
              ┌────────────┐
              │   Core-2   │
              │ IP: 10.255.1.2
              └────────────┘

Bandwidth calculation:
- Core link speed: 100G
- Distribution switches: 5
- Connections from each Dist to both Cores: 2
- Total uplinks: 5 × 2 = 10 links
- Total capacity: 10 × 100G = 1 Tbps
- Core-to-Core link: 100-400G
```

### Core Layer Configuration

```
Cisco Nexus 9516 BGP Configuration:

router bgp 65001
  address-family ipv4 unicast
    redistribute static route-map STATIC_TO_BGP
  neighbor 10.255.1.2 remote-as 65001
  neighbor 10.255.1.2 description Core-2
  neighbor 10.255.1.2 timers 3 10
  !
  neighbor 10.10.1.2 remote-as 65001
  neighbor 10.10.1.2 description Dist-A
  !
  address-family ipv4 unicast
    neighbor 10.255.1.2 activate
    neighbor 10.255.1.2 next-hop-self
    neighbor 10.10.1.2 activate
    neighbor 10.10.1.2 next-hop-self
    !
    network 10.0.0.0 mask 255.0.0.0
    !
  address-family ipv4 multicast
    neighbor 10.10.1.2 activate

! ECMP load balancing
router bgp 65001
  address-family ipv4 unicast
    maximum-paths 16
    maximum-paths ibgp 16
```

## Layer-to-Layer Traffic Flow

### Intra-Department Communication

```
Scenario: Finance user (10.10.20.50) sends email to Finance server (10.10.20.100)

1. PC sends frame:
   - Source: 10.10.20.50 (Finance PC)
   - Dest: 10.10.20.100 (Finance server)
   - VLAN: 20
   - Path: Access-A2 → Intra-VLAN switching

2. Access switch lookup:
   - Destination MAC in VLAN 20 learned locally
   - Direct forwarding (low latency, no routing)
   - Time: < 1 millisecond

Result: Direct L2 switching, no distribution involvement
```

### Inter-Department Communication

```
Scenario: Finance user (10.10.20.50) accesses engineering server (10.10.30.100)

1. PC sends frame:
   - Source: 10.10.20.50
   - Dest: Gateway 10.10.20.1 (virtual)
   - VLAN: 20

2. Access switch:
   - Destination not in VLAN 20
   - Sends to distribution via uplink
   - Time: < 0.5 milliseconds

3. Distribution layer (Dist-A):
   - Receives frame from Finance VLAN
   - Performs routing decision
   - Looks up 10.10.30.0/24 → Engineering VLAN 30
   - Checks ACL (allowed)
   - Encapsulates in VLAN 30 frame
   - Sends out VLAN 30 interface
   - Time: < 1 microsecond

4. Distribution forwards:
   - Via uplink to access switch for Engineering
   - Time: < 1 millisecond

5. Access switch (Engineering):
   - Receives VLAN 30 frame
   - Delivers to Engineering server
   - Time: < 0.5 milliseconds

Total latency: ~3 milliseconds
```

### Upstream Communication

```
Scenario: Campus user accesses Internet

Source: 10.10.20.50 (Finance)
Destination: 8.8.8.8 (Google DNS - External)

Path:
Access-A2
  ↓ (via uplink)
Distribution-A
  ↓ (routing decision)
Core-1
  ↓ (via default route or BGP)
Core-2 (optional alternate path)
  ↓ (via ECMP)
Firewall
  ↓
Internet Router
  ↓
ISP Network
  ↓
Google DNS
```

## Layer Sizing Guidelines

| Parameter | Access Layer | Distribution Layer | Core Layer |
|-----------|--------------|-------------------|-----------|
| Switch count | Many | Few (N+1 per site) | 2-4 |
| Throughput | 50-100G | 10-100 Tbps | 100+ Tbps |
| Interface speed | 1G/10G | 10G/40G/100G | 40G/100G/400G |
| Latency | <3µs | <1µs | <1µs |
| VLAN count | 1-2 | All | Transit |
| Cost/port | Low | Medium | High |
| Failure impact | Single switch | Multiple users | Campus-wide |

---

**Reference Version:** 1.0
**Last Updated:** November 2025
**Standards:** Cisco, RFC 1195 (OSI routing)
