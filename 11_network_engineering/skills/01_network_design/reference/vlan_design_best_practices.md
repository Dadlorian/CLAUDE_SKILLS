# VLAN Design Best Practices

## Introduction
Virtual Local Area Networks (VLANs) are fundamental to network design, enabling logical network segmentation, traffic isolation, and policy enforcement across physical infrastructure.

## VLAN Fundamentals

### VLAN Tagging (IEEE 802.1Q)

```
Ethernet Frame with VLAN Tagging:
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ Dest MAC │ Src MAC  │VLAN Tag  │EtherType │   Data   │   FCS    │
│(6 bytes) │(6 bytes) │(4 bytes) │(2 bytes) │(46-1500) │(4 bytes) │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘

VLAN Tag Structure:
┌──────────────────┬─────────┬──────────────────────────────┐
│ TPID: 0x8100    │ Priority │ Canonical Format Indicator   │
│ (2 bytes)       │ (3 bits) │ (1 bit)                      │
└──────────────────┴─────────┴──────────────────────────────┘
                                      │
                                      └─ VLAN ID (12 bits)
                                          Range: 1-4094
```

### VLAN ID Ranges

```
Reserved VLANs:
- 0: Reserved (not used)
- 1: Default VLAN (untagged native VLAN)
- 2-1001: Normal range (not for cloud/storage)
- 1002-1005: Reserved for Token Ring, FDDI, deprecated
- 1006-4094: Extended range (some restrictions apply)
```

## Campus Network VLAN Design

### Departmental VLANs Model

```
VLAN Structure Example:

VLAN 10 - Executive
  - IP: 10.10.10.0/24
  - Gateway: 10.10.10.1
  - Access: Building A, Floor 1
  - Users: 40

VLAN 20 - Finance
  - IP: 10.10.20.0/24
  - Gateway: 10.10.20.1
  - Access: Building A, Floor 2-3
  - Users: 120

VLAN 30 - Engineering
  - IP: 10.10.30.0/24
  - Gateway: 10.10.30.1
  - Access: Building B, All Floors
  - Users: 180

VLAN 40 - Operations
  - IP: 10.10.40.0/24
  - Gateway: 10.10.40.1
  - Access: Building C, All Floors
  - Users: 95

VLAN 50 - Sales
  - IP: 10.10.50.0/24
  - Gateway: 10.10.50.1
  - Access: Building A, Floor 4
  - Users: 75

VLAN 100 - WiFi Guest
  - IP: 10.10.100.0/24
  - Gateway: 10.10.100.1
  - Internet: Direct to firewall
  - Isolation: No internal access

VLAN 110 - Voice/VoIP
  - IP: 10.10.110.0/24
  - Gateway: 10.10.110.1
  - QoS: High priority
  - Isolated: Yes

VLAN 120 - Printers
  - IP: 10.10.120.0/24
  - Gateway: 10.10.120.1
  - Access: All departments
  - Restricted: Yes
```

### Building-Based VLAN Design

```
Alternative hierarchical approach:

Building A (10.10.0.0/20)
  ├─ VLAN 110: Floor 1 (10.10.0.0/24)
  ├─ VLAN 111: Floor 2 (10.10.1.0/24)
  ├─ VLAN 112: Floor 3 (10.10.2.0/24)
  └─ VLAN 113: Floor 4 (10.10.3.0/24)

Building B (10.10.16.0/20)
  ├─ VLAN 210: Floor 1 (10.10.16.0/24)
  ├─ VLAN 211: Floor 2 (10.10.17.0/24)
  └─ VLAN 212: Floor 3 (10.10.18.0/24)

Building C (10.10.32.0/20)
  ├─ VLAN 310: Floor 1 (10.10.32.0/24)
  ├─ VLAN 311: Floor 2 (10.10.33.0/24)
  └─ VLAN 312: Floor 3 (10.10.34.0/24)
```

## Data Center VLAN Design

### Function-Based VLANs

```
VLAN 1000 - Hypervisor Management
  - IP: 10.100.0.0/24
  - Access: Management network only
  - Traffic: ESXi/Hyper-V management
  - Isolation: Restricted

VLAN 1010 - VM Production
  - IP: 10.100.10.0/24
  - Access: VM network traffic
  - Tenant: Customer A
  - Isolation: L3 enforced

VLAN 1020 - VM Production
  - IP: 10.100.20.0/24
  - Access: VM network traffic
  - Tenant: Customer B
  - Isolation: L3 enforced

VLAN 1030 - Storage iSCSI
  - IP: 10.100.30.0/24
  - Performance: Jumbo frames (MTU 9000)
  - Access: Dedicated storage path
  - QoS: Reserved bandwidth

VLAN 1040 - Storage NFS
  - IP: 10.100.40.0/24
  - Performance: Jumbo frames (MTU 9000)
  - Access: Storage array and servers
  - QoS: Reserved bandwidth

VLAN 1050 - vMotion
  - IP: 10.100.50.0/24
  - Performance: Jumbo frames (MTU 9000)
  - Access: Hypervisor-to-hypervisor
  - Bandwidth: Dedicated uplinks

VLAN 1060 - Backup Network
  - IP: 10.100.60.0/24
  - Access: Backup servers and storage
  - Isolation: Separate from production
  - Throttling: Applied at 40Gbps
```

## VLAN Trunk Design

### Trunk Configuration

```
Access Switch Port (Untagged):
  - Single VLAN attached
  - Native VLAN for untagged frames
  - No VLAN tag in frame

  Example: Interface Gi0/0/1
    Description: Desktop PC
    Mode: Access
    Access VLAN: 20 (Finance)

Trunk Port Configuration:
  - Multiple VLANs
  - All frames tagged (except native)
  - Native VLAN: 1 (or management VLAN)

  Example: Interface Gi0/0/48 (to distribution)
    Mode: Trunk
    Allowed VLANs: 10,20,30,40,50,100,110,120
    Native VLAN: 1
    Encapsulation: 802.1Q
```

### Trunk Negotiation (DTP)

```
DTP States:
- desirable: Actively negotiate trunk (default)
- auto: Passively accept trunk
- nonegotiate: Force trunk, no negotiation
- on: Force trunk
- off: Force access mode

Recommendation:
  - Turn off DTP (nonegotiate on both sides)
  - Manually configure trunk/access
  - Reduces security risks from VLAN hopping
```

## VLAN Best Practices

### Numbering Conventions

```
Recommended VLAN numbering:
- 1-9: Reserved/Management
- 10-99: Departmental/Functional
- 100-199: Data Center
- 200-299: Wireless
- 300-399: Guest/Contractor
- 400-499: IoT/Sensors
- 500-599: VoIP/Unified Communications
- 600-699: Reserved for future
- 700-799: Lab/Testing
- 800-899: Infrastructure
- 900-999: Reserved
- 1000+: Extended range
```

### Size Calculations

```
VLAN Sizing Formula:
  Required IPs = Current Users × 1.3 + Reserved

  Example: 100 users in Engineering
    Required IPs = 100 × 1.3 + 20 reserved = 150
    Network size: /25 (126 usable) = TOO SMALL
    Better choice: /24 (254 usable) = GOOD

VLAN 30 - Engineering Revised:
  - Network: 10.10.30.0/24
  - Current: 100 users
  - Reserved: 50 future users
  - Printers/devices: 10
  - Growth: 3 years planned
  - Status: ADEQUATE
```

### Spanning Tree Considerations

```
VLAN-based Spanning Tree:

Per-VLAN Spanning Tree Plus (PVST+):
  - One STP instance per VLAN
  - Root bridge per VLAN
  - Granular control
  - Complexity: Higher
  - Resource usage: Higher

Rapid PVST+ (RPVST+):
  - IEEE 802.1w standard
  - Faster convergence (< 1 second)
  - Recommended for modern networks

  Configuration:
  ┌──────────────┐      ┌──────────────┐
  │ Distribution │      │ Distribution │
  │    Layer     │------│    Layer     │
  │  (Pri Root)  │      │  (Sec Root)  │
  └──────┬───────┘      └───────┬──────┘
         │                      │
         │                      │
      ┌──┴───┐              ┌───┴──┐
      │Access│              │Access│
      │Switch│              │Switch│
      └──────┘              └──────┘

  VLAN 10 Root: Distribution-1
  VLAN 20 Root: Distribution-1
  VLAN 30 Root: Distribution-2 (balance load)
```

## VLAN Routing

### Inter-VLAN Routing Methods

**Router-on-a-Stick (Legacy)**
```
Single physical link carrying multiple VLANs
  Switch Port: Trunk mode
  Router Interface: Subinterfaces

  Limitations:
  - Single link bottleneck
  - High latency
  - Not recommended for modern networks
```

**Native VLAN Routing (Modern)**
```
L3 capable switch (multilayer switch)
  SVI (Switch Virtual Interface) per VLAN
  Native routing hardware
  Wire-speed routing

  Configuration:
  VLAN 10 SVI: 10.10.10.1/24
  VLAN 20 SVI: 10.10.20.1/24
  VLAN 30 SVI: 10.10.30.1/24

  Gateway for each VLAN on same device
```

## VLAN Isolation and Security

### Access Control

```
VLAN ACLs (VACLs):
  - Control traffic between VLANs
  - Applied to VLAN interfaces
  - Independent of routing ACLs

  Example - Restrict Finance VLAN:
    VLAN 20 can communicate with:
    - VLAN 100 (Shared resources)
    - VLAN 120 (Printers)
    Blocked: Direct access to other VLANs

Guest VLAN Isolation:
    VLAN 100 (Guest)
    - Cannot reach any internal VLAN
    - Direct Internet gateway
    - DNS server: External only
    - DHCP: Isolated pool
```

### Private VLAN (Protected Ports)

```
Scenario: Multiple customers in same VLAN
  - Shared services (printers, gateways)
  - Isolated customer data

Configuration:
  - Primary VLAN: 1000
  - Community VLANs: 1001, 1002, 1003
  - Isolated ports: Customer-specific

Traffic patterns:
  ✓ Customer A ↔ Gateway
  ✓ Customer B ↔ Gateway
  ✓ Both customers ↔ Shared printer
  ✗ Customer A ↔ Customer B (Blocked)
```

## VLAN QoS Considerations

```
Traffic Classification by VLAN:

VLAN 110 (Voice/VoIP):
  - Priority: High (PCP = 5)
  - DSCP: EF (46)
  - Bandwidth: Reserved 30 Mbps
  - Jitter: < 30ms

VLAN 1030 (Storage iSCSI):
  - Priority: High (PCP = 4)
  - DSCP: AF31 (26)
  - Bandwidth: Reserved 20 Gbps
  - Loss rate: < 0.001%

VLAN 30 (Engineering):
  - Priority: Medium (PCP = 3)
  - DSCP: AF11 (10)
  - Bandwidth: Best effort
  - Loss rate: < 1%

VLAN 100 (Guest):
  - Priority: Low (PCP = 1)
  - DSCP: BE (0)
  - Bandwidth: Throttle to 100 Mbps
  - Loss rate: Acceptable
```

## Summary Table

| Aspect | Best Practice | Rationale |
|--------|---------------|-----------|
| VLAN ID Range | 10-4094 | Avoid reserved 0, 1, 1002-1005 |
| Naming | Descriptive prefix | Easy identification and audit |
| Size | Oversized by 30% | Plan for growth |
| Numbering | Grouped by function | Logical organization |
| Trunking | Manual config | Security and manageability |
| Routing | Native on L3 switch | Performance and scalability |
| STP | RPVST+ | Fast convergence |
| Isolation | Policy-enforced | Defense in depth |
| Documentation | VlanDB system | Centralized source of truth |

---

**Reference Version:** 1.0
**Last Updated:** November 2025
**Standards:** IEEE 802.1Q, RFC 3021
