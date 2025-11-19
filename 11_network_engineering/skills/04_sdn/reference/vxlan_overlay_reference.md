# VXLAN Overlay Reference

## VXLAN Fundamentals

### Definition
VXLAN (Virtual eXtensible LAN) is a Layer 2 overlay networking protocol that encapsulates Ethernet frames within UDP packets, enabling virtual networks to scale across Layer 3 infrastructure.

### RFC 7348
- **Key Concept**: Mac-in-UDP encapsulation
- **Purpose**: Layer 2 over Layer 3
- **Scope**: Global deployment
- **Scale**: Up to 16M VXLANs (24-bit VXLAN Network ID)

## Architecture

### Key Components

#### VTEP (VXLAN Tunnel Endpoint)
**Role**: Encapsulates/decapsulates VXLAN packets
**Location**: Hypervisors, switches, appliances
**Functions**:
- Ingress: Adds VXLAN header to Ethernet frames
- Egress: Removes VXLAN header and forwards to destination VM/host
- MAC learning: Learns MAC addresses from arriving packets

#### VXLAN Network ID (VNI)
- **Size**: 24 bits (16,777,216 possible values)
- **Purpose**: Tenant isolation (like VLAN but massive scale)
- **Multicast Group**: Optional, for broadcast/multicast traffic

### VXLAN Frame Structure

```
Original Ethernet Frame
├─ Destination MAC
├─ Source MAC
├─ VLAN Tag (optional)
└─ Payload (L3+ data)
    ↓ Encapsulation
VXLAN Packet
├─ Outer Ethernet Header (transport)
├─ Outer IP Header (source VTEP, dest VTEP)
├─ UDP Header (port 4789)
├─ VXLAN Header (VNI, flags)
├─ Original Ethernet Frame (inner)
└─ CRC
```

### Packet Format

```
Outer Ethernet (14 bytes)
├─ Dst MAC: Next hop to destination VTEP
├─ Src MAC: Source VTEP MAC
└─ Type: IPv4 (0x0800) or IPv6 (0x86DD)

Outer IP Header (20 bytes IPv4, 40 bytes IPv6)
├─ Source IP: Source VTEP
├─ Destination IP: Destination VTEP
├─ TTL: Decremented per hop
└─ Protocol: UDP (17)

UDP Header (8 bytes)
├─ Source Port: 49152-65535 (usually)
├─ Destination Port: 4789 (standard) or 4790 (VLAN)
└─ Checksum: Optional

VXLAN Header (8 bytes)
├─ Flags: R|R|R|I|R|R|R|R (I = VNI present)
├─ Reserved: 24 bits (0x000000)
├─ VXLAN Network ID (VNI): 24 bits
└─ Reserved: 8 bits (0x00)

Inner Ethernet Frame
├─ Destination MAC
├─ Source MAC
├─ Type/Length
├─ Payload (IP, ARP, etc.)
└─ FCS
```

## VXLAN Deployment Models

### Unicast Mode
**Description**: Point-to-point VXLAN tunnels with known endpoints
```
VM1 on Host-A ──→ VTEP-A ══════ VTEP-B ──→ VM2 on Host-B
                  (encapsulate)   (decapsulate)
```
**Advantages**: Works in restricted multicast environments
**Disadvantages**: Requires MAC/IP mapping distribution

### Multicast Mode
**Description**: Uses multicast for BUM (Broadcast, Unknown Unicast, Multicast)
```
VTEP-A ──→ Multicast Group 224.1.1.1:4789 ←── VTEP-B
```
**Advantages**: Simpler deployment, dynamic learning
**Disadvantages**: Requires multicast infrastructure

### Hybrid Mode
**Description**: Unicast for known destinations, multicast for BUM
**Advantages**: Best of both worlds
**Disadvantages**: More complex configuration

## Control Plane Mechanisms

### Dynamic MAC Learning
- **Process**: VTEPs learn MAC-to-IP mappings from received traffic
- **Flooding**: Unknown unicast flooded via multicast or all known tunnels
- **Timeout**: Learned entries age out after period (typically 1-2 hours)

### BGP EVPN (Ethernet VPN)
**RFC 7432** - Standards-based control plane for VXLAN
```
VTEP-A ──BGP EVPN──→ BGP Server ←──BGP EVPN── VTEP-B
        (advertises learned MACs)
```

**Advantages**:
- Standardized control plane
- Better scalability
- Reduced broadcast traffic
- Faster convergence

**AFI/SAFI**: 25/70 (L2VPN EVPN)

**Route Types**:
1. **Type 1**: Ethernet AD Route (link state)
2. **Type 2**: MAC/IP Advertisement Route
3. **Type 3**: Inclusive Multicast Ethernet Tag Route
4. **Type 4**: Ethernet Segment Route
5. **Type 5**: IP Prefix Route

### MP-BGP RD/RT
**Route Distinguisher (RD)**: Makes overlapping MAC addresses unique
**Route Target (RT)**: Import/Export policy

```
Example:
AS:VNI format: 65001:101 (AS 65001, VNI 101)
Administrator_IP:VNI format: 10.1.1.1:101
```

## Symmetric vs Asymmetric IRB

### Asymmetric IRB
**Process**:
- Ingress VTEP routes L3 traffic
- Egress VTEP bridges back to VLAN

**Advantage**: Works with standard routing
**Disadvantage**: Asymmetric paths, higher latency

### Symmetric IRB
**Process**:
- Both ingress and egress VTEPs route
- Symmetric traffic paths

**Advantage**: Lower latency, cleaner design
**Disadvantage**: Requires BGP EVPN route type 5

## VXLAN with Segment Routing

### SR-VXLAN
**Concept**: Combine segment routing with VXLAN encapsulation
**Benefit**: Simplified path engineering without RSVP

```
VXLAN Encapsulation + SR labels + Network namespace
= Powerful isolation + efficient routing
```

## Performance Characteristics

### MTU Considerations
```
Physical Link MTU: 1500 bytes (standard)
VXLAN Overhead: 50 bytes (Ethernet + IP + UDP + VXLAN)
Effective Payload: 1450 bytes

Solution: Increase physical MTU to 1550-1600 (jumbo frames)
```

### Latency Impact
- Encapsulation/Decapsulation: 1-3 microseconds
- Hardware offload: Negligible overhead
- Software implementation: May add 100+ microseconds

### Scalability
- **VTEPs per Site**: Thousands supported
- **VXLANs per VTEP**: Limited by memory (10K-100K)
- **MAC Addresses**: Distributed scale-out model
- **Control Plane**: BGP EVPN can handle millions of routes

## VXLAN Use Cases

### 1. Data Center Overlay
```
Multiple Pods connected via VXLAN overlay
├─ Tenant segregation
├─ Multi-pod stretched VLANs
└─ VM mobility across pods
```

### 2. Cloud Provider Infrastructure
- Multi-tenant isolation
- Rapid resource provisioning
- Workload portability

### 3. Enterprise WAN
- Overlay VPN without IPsec overhead
- Scalable branch connectivity
- Simplified operations

### 4. Hybrid Cloud
- Connect on-premises to cloud
- Consistent networking model
- Simplified migration

## VXLAN Gateway Functions

### L2 Gateway
**Role**: Bridge between VXLAN and traditional VLAN networks
**Implementation**: Physical or virtual device
**Function**: Encapsulate/decapsulate at domain boundary

### L3 Gateway
**Role**: Route between VXLAN VNIs and traditional networks
**Implementation**: Distributed router in hypervisors
**Function**: Integrated routing and bridging (IRB)

## Troubleshooting VXLAN

### Common Issues

#### VXLAN Tunnel Down
- Verify VTEP reachability (ping outer IP)
- Check multicast routing (if multicast mode)
- Verify BFD for fast detection

#### MAC Learning Problems
- Check for ARP suppression issues
- Verify BGP EVPN adjacencies
- Validate RT/RD configuration

#### High MTU Issues
- Validate physical MTU settings
- Check for fragmentation
- Confirm underlay MTU adequate

#### Performance Degradation
- Monitor CPU usage during encapsulation
- Check for hardware offload availability
- Verify bandwidth utilization

## Security Aspects

### Tenant Isolation
- VNI provides logical separation
- Layer 2 cannot cross VNI boundaries
- Requires explicit routing for inter-VNI

### Spoofing Prevention
- MAC-to-IP binding validation
- Dynamic learning limitations
- BGP EVPN route filtering

### Encryption
- Underlay encryption for complete security
- TLS for control plane (BGP)
- Optional: IPsec tunnel encryption
