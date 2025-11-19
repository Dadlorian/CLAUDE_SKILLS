# DMVPN (Dynamic Multipoint VPN) Reference

## Overview

DMVPN is a Cisco technology that simplifies large-scale hub-and-spoke VPN deployments by enabling dynamic discovery of tunnel endpoints and direct spoke-to-spoke communication.

## Core Components

### 1. NHRP (Next Hop Resolution Protocol)

**Purpose**
- Maps logical addresses to physical tunnel endpoints
- Enables dynamic discovery of spoke routers
- Allows direct tunnel establishment between spokes
- Reduces hub congestion for inter-spoke traffic

**Mechanism**
- Hub acts as NHRP server
- Spokes register with hub (NHRP Register)
- Spokes query hub for peer information (NHRP Request)
- Hub responds with peer details (NHRP Reply)

**NHRP Packet Types**
- **Resolution Request**: Query for peer endpoint
- **Resolution Reply**: Response with endpoint information
- **Registration Request**: Spoke announces its public IP
- **Registration Reply**: Acknowledgment of registration
- **Purge Request**: Remove entry from cache
- **Error Indication**: Error notification

### 2. IPsec Encryption

**Tunnel Types**
- **Encrypted Tunnel Interface**: mGRE with IPsec encryption
- **Multi-GRE**: Single interface carries multiple logical tunnels
- **IPsec encapsulation**: Standard IPsec over GRE

**Crypto Topologies**
- **Unified**: Single crypto ACL for all tunnels
- **Separate**: Different keys for hub and spoke tunnels

### 3. Routing Protocol

**Options**
- **EIGRP**: Most common choice (dynamic route redistribution)
- **BGP**: For large-scale deployments (path control)
- **OSPF**: Alternative option (less common)
- **Static**: Manual routes (limited DMVPN benefit)

**Dynamic Routing Benefits**
- Automatic path discovery
- Hub failure detection
- Load balancing across multiple hubs
- Convergence on topology changes

## DMVPN Phases

### Phase 1: Hub-and-Spoke Only

**Topology**
- All spoke-to-spoke traffic through hub
- Direct tunnels not established
- Simple NHRP configuration
- Spoke-to-spoke traffic: Spoke → Hub → Spoke

**Characteristics**
- Lowest CPU overhead on spokes
- Hub becomes bottleneck for inter-spoke traffic
- Scalability limited (hub bandwidth)
- Configuration simplicity

**Use Cases**
- Small deployments (< 20 spokes)
- Limited inter-spoke traffic
- Hub has bandwidth available

### Phase 2: Spoke-to-Spoke Direct

**Topology**
- Direct tunnels between spokes (on-demand)
- Hub used for initial path discovery only
- NHRP provides endpoint resolution
- Spoke-to-spoke traffic: Spoke → Spoke

**Characteristics**
- Spoke-to-spoke traffic not through hub
- Requires NHRP peer information to establish tunnel
- First packet through hub until route established
- Offloads hub for inter-spoke traffic

**Implementation**
- Enable spoke-to-spoke capability in NHRP
- Configure cryptographic keys appropriately
- Routing converges on direct tunnel establishment

**Challenges**
- Routing oscillation (recursive routing issues)
- MTU complications (two levels of encapsulation)
- Split tunneling issues with summarized routes
- Complex troubleshooting

### Phase 3: Advanced Routing Optimization

**Topology**
- Spoke-to-spoke direct tunnels (proactive)
- Routing driven by protocol updates (not traffic)
- EIGRP NHRP redirect shortcuts
- Faster convergence than Phase 2

**Characteristics**
- EIGRP redistributes NHRP shortcuts
- Spokes establish tunnels based on EIGRP updates
- Prevents routing oscillation
- Easier troubleshooting than Phase 2

**EIGRP NHRP Redirect**
- EIGRP announces routes to each spoke
- Spoke sees hub as next-hop in initial update
- NHRP informs of direct tunnel availability
- EIGRP switches next-hop to direct tunnel

**Advantages over Phase 2**
- Eliminates routing oscillation
- Convergence based on routing protocol
- Better interoperability with complex topologies
- Supports multi-hub designs

**Use Cases**
- Large deployments (100+ spokes)
- Heavy inter-spoke traffic
- Multiple hubs for redundancy
- Production enterprise networks

## Multi-Hub Design

### Configuration Types

#### Dual Hub Redundancy
```
Topology:
  Hub1 ←→ Hub2 (backup tunnel)
  Spoke1 ←→ Hub1, Hub2
  Spoke2 ←→ Hub1, Hub2
```

**Characteristics**
- Primary and backup NHRP servers
- Spokes configured for both hubs
- Traffic load on primary hub
- Failover to secondary on hub loss

#### Load Balanced Multi-Hub
```
Topology:
  Hub1 - Even numbered spokes
  Hub2 - Odd numbered spokes
  All spokes can reach both hubs
```

**Characteristics**
- Traffic distributed across hubs
- Better bandwidth utilization
- More complex NHRP configuration
- Traffic engineering possible

#### Full Mesh Hub
```
Topology:
  Hub1 ↔ Hub2 ↔ Hub3
  All hubs interconnected
  Spokes connect to one or more hubs
```

**Characteristics**
- Hub-to-hub redundancy
- Any hub can serve any spoke
- Complex routing
- High availability design

## NHRP Configuration Details

### NHRP Server (Hub)
```
interface tunnel 0
  ip nhrp network-id 100
  ip nhrp server-only
  ip nhrp authentication [password]
```

**Parameters**
- **network-id**: Identifier for NHRP domain
- **server-only**: Hub acts as NHRP server
- **authentication**: Security key for NHRP

### NHRP Client (Spoke)
```
interface tunnel 0
  ip nhrp network-id 100
  ip nhrp nhs [hub-ip] multicast
  ip nhrp registration timeout 600
  ip nhrp holdtime 600
```

**Parameters**
- **nhs**: Next Hop Server (hub) address
- **multicast**: Multicast traffic goes to hub
- **registration timeout**: How often to re-register
- **holdtime**: How long to keep NHRP entry

## Routing Considerations

### EIGRP with DMVPN

**Key Features**
- **NHRP Redirect**: Automatic shortcut activation
- **Split Horizon**: Must be disabled on hub
- **Summarization**: Affects shortcut creation
- **Stub Routing**: Can be used on spokes

**Configuration**
```
router eigrp [AS]
  network [tunnel-network]
  no auto-summary
  eigrp log-neighbor-changes

interface tunnel 0
  no ip split-horizon eigrp [AS]
  ip summary-address eigrp [AS] [summary] [mask]
```

**Bandwidth Considerations**
- EIGRP traffic on all spokes
- Hello packets to all neighbors
- Query packets for topology changes
- Bandwidth consumption grows with spokes

### BGP with DMVPN

**Advantages**
- Hierarchical design (more scalable)
- Path control and traffic engineering
- Better for large deployments (500+ spokes)
- Reduced convergence overhead

**Considerations**
- More complex to configure
- More overhead than EIGRP for small deployments
- Aggregation possible for summarization
- Less suitable for small networks

## High Availability

### Spoke Redundancy
- Multiple hubs per spoke
- EIGRP load balancing
- Fast failover on hub loss
- Active-active or active-passive

### Hub Redundancy
- Multiple hub clusters
- NHRP server hierarchy
- Route redistribution between clusters
- N+1 redundancy typical

### QoS Considerations
- Bandwidth guarantee per site
- Traffic prioritization
- Multicast handling (ReachabilityUpdate traffic)
- Voice optimization

## MTU and Path MTU Discovery (PMTUD)

### Tunnel Overhead Calculation
```
GRE Overhead: 24 bytes
IPsec Overhead: 50-73 bytes (depends on cipher)
Total Overhead: 74-97 bytes

Standard MTU: 1500 bytes
Tunnel MTU: 1500 - 97 = 1403 bytes
```

### PMTUD Implementation
- Hub may not reply to ICMP fragmentation needed
- Spokes see expanded packets from direct spokes
- MTU must account for encryption overhead

### Best Practice
- Set tunnel MTU explicitly
- Use ip mtu [size] on tunnel interface
- Typically 1400 or less
- Test with ping -DF (don't fragment)

## Spoke-to-Spoke Tunnel Establishment

### Process
1. **Initial State**: Spoke has route via hub
2. **Trigger**: Traffic destined to remote spoke
3. **NHRP Query**: Spoke queries hub for remote spoke IP
4. **NHRP Reply**: Hub responds with remote spoke public IP
5. **Tunnel Creation**: IPsec tunnel established to remote spoke
6. **Routing Update**: Routing protocol switches next-hop
7. **Direct Traffic**: Spoke-to-spoke traffic flows direct

### Timeout Considerations
- **NHRP cache timeout**: How long to keep learned entries
- **Route timeout**: How long route is valid
- **Tunnel teardown**: Idle tunnels may be torn down
- **Convergence**: Time to establish direct path

## Troubleshooting DMVPN

### Common Issues

#### Spoke Cannot Register with Hub
- **Cause**: Hub not reachable, NHRP disabled, wrong network-id
- **Solution**: Verify tunnel status, NHRP settings, network-id match

#### Spoke-to-Spoke Tunnel Not Established
- **Cause**: NHRP redirect not working, routing policy blocking
- **Solution**: Verify EIGRP NHRP redirect, check routing policy

#### Routing Oscillation
- **Cause**: Phase 2 with summarization, recursive routing
- **Solution**: Use Phase 3, avoid summarization, review routing

#### Poor Performance
- **Cause**: All traffic through hub, encryption bottleneck
- **Solution**: Verify spoke-to-spoke established, check throughput

### Diagnostic Commands
```
# Show NHRP information
show ip nhrp

# Show tunnel status
show interface tunnel 0

# Show EIGRP neighbors
show ip eigrp neighbors

# Show EIGRP routes
show ip eigrp topology

# Show BGP routes (if using BGP)
show ip bgp

# Check NHRP cache
show ip nhrp cache

# Monitor NHRP traffic
debug ip nhrp

# Monitor EIGRP activity
debug eigrp packets
```

## Security Considerations

### Encryption
- IPsec encryption mandatory for security
- Pre-shared keys or certificates
- Crypto ACL specifies protected traffic
- Phase 3 prefers encrypted tunnels

### Authentication
- NHRP authentication (optional but recommended)
- IPsec authentication for integrity
- EIGRP authentication (optional)
- BGP authentication (optional)

### DDoS Protection
- NHRP can be targeted for DoS
- IPsec protects encrypted tunnels
- Rate limiting on NHRP queries
- Spoof protection for NHRP

## DMVPN Use Cases

### Branch Connectivity
- Multiple branch offices connecting to data center
- Scalable alternative to point-to-point VPNs
- Reduced WAN costs
- Simplified configuration

### Disaster Recovery
- Multiple data centers with branch redundancy
- Active-active configuration possible
- Fast failover between data centers
- Geographic redundancy

### Cloud Connectivity
- AWS, Azure, Google Cloud integration
- Hybrid cloud WAN
- Overlay network over cloud infrastructure
- Dynamic branch connectivity
