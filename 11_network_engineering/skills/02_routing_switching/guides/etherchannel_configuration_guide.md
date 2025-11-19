# EtherChannel Configuration Guide

## Pre-Configuration Checklist

### Port Requirements
```
Before bundling ports into EtherChannel:
- [ ] Same speed (100Mbps, 1Gbps, 10Gbps)
- [ ] Same duplex (full-duplex required)
- [ ] Same VLAN assignment
- [ ] Same native VLAN (if trunk)
- [ ] Same allowed VLAN list (if trunk)
- [ ] Same port-security config
- [ ] Same QoS settings
- [ ] Same spanning-tree settings
```

## LACP Configuration

### Active-Passive LACP (Recommended)
```
! Side A (Active)
interface range GigabitEthernet0/1-2
  channel-group 1 mode active
  channel-protocol lacp
  no shutdown

! Side B (Passive)
interface range GigabitEthernet0/1-2
  channel-group 1 mode passive
  channel-protocol lacp
  no shutdown

! Verify formation
show etherchannel 1 summary
show lacp 1 neighbor
```

### Active-Active LACP (Also Valid)
```
! Both sides active
interface range GigabitEthernet0/1-2
  channel-group 1 mode active
  channel-protocol lacp

! Risk: Both initiate, ensure one side can become passive
```

## Port-Channel Interface Configuration

### Basic Port-Channel Setup
```
interface Port-channel 1
  description LAG-to-Switch-B
  switchport mode trunk
  switchport trunk encapsulation dot1q
  switchport trunk native vlan 99
  switchport trunk allowed vlan 10-99,100-299
  no shutdown
```

### Access Port EtherChannel
```
interface Port-channel 1
  description LAG-to-Server
  switchport mode access
  switchport access vlan 100
  spanning-tree portfast
  no shutdown
```

## PAgP Configuration (Legacy)

### Desirable-Auto (Negotiation)
```
! Switch A - Initiates negotiation
interface range GigabitEthernet0/1-2
  channel-group 1 mode desirable
  channel-protocol pagp
  no shutdown

! Switch B - Responds to negotiation
interface range GigabitEthernet0/1-2
  channel-group 1 mode auto
  channel-protocol pagp
  no shutdown
```

### Desirable-Desirable (Negotiation)
```
! Both sides desirable (also works)
interface range GigabitEthernet0/1-2
  channel-group 1 mode desirable
  channel-protocol pagp
```

## Static EtherChannel Configuration

### On-On Mode (No Negotiation)
```
! Both sides on
interface range GigabitEthernet0/1-2
  channel-group 1 mode on
  no shutdown

! Risk: No protocol, verify manually that both sides match
```

## Load Balancing Configuration

### Default Algorithm (src-dst-mac)
```
show etherchannel load-balance
! Display current algorithm

! Most common and effective for most traffic
```

### Change Algorithm
```
port-channel load-balance [algorithm]

! Available algorithms:
! - src-ip: Hash on source IP
! - dst-ip: Hash on destination IP
! - src-dst-ip: Hash on both IPs (default on many)
! - src-port: Hash on source port
! - dst-port: Hash on destination port
! - src-dst-port: Hash on both ports
! - src-mac: Hash on source MAC
! - dst-mac: Hash on destination MAC
! - src-dst-mac: Hash on both MACs (default on switches)

! Example:
port-channel load-balance src-dst-ip
! Better for IP traffic

show etherchannel load-balance
```

### Load Distribution Verification
```
show etherchannel 1 load-balance
show etherchannel port-channel 1

! Monitor traffic distribution
show interfaces Port-channel 1
show etherchannel detail
```

## LACP Configuration Options

### LACP Rate (Fast vs Slow)
```
! Default slow (30 seconds)
interface Port-channel 1
  lacp rate slow

! Fast (1 second) - for stability detection
interface Port-channel 1
  lacp rate fast
```

### LACP System Priority
```
! Default 32768 (lower = more preferred)
lacp system-priority 4096
! All ports use this system priority for LACP negotiation
```

### LACP Port Priority
```
interface GigabitEthernet0/1
  lacp port-priority 32768
! Higher priority = preferred in port-channel
```

## EtherChannel with STP

### Port-Channel STP Cost
```
interface Port-channel 1
  spanning-tree cost 100
  ! Entire port-channel has single cost
```

### Per-VLAN STP Optimization
```
interface Port-channel 1.100
  spanning-tree cost 100  ! VLAN 100
  spanning-tree cost 200  ! VLAN 200 (different cost)
```

## Trunk EtherChannel

### Multi-VLAN Trunk Bundle
```
interface range GigabitEthernet0/45-48
  description Inter-Switch-Trunk
  channel-group 1 mode active
  channel-protocol lacp

interface Port-channel 1
  switchport mode trunk
  switchport trunk native vlan 99
  switchport trunk allowed vlan 10-99,100-299
  spanning-tree portfast disable  ! Required for trunks
  no shutdown
```

### Cross-Stack EtherChannel (Stackable)
```
! Cisco stacks allow EtherChannel across members
interface range GigabitEthernet1/0/1-2,GigabitEthernet2/0/1-2
  channel-group 1 mode active
  ! Bundles ports from multiple stack members
```

## EtherChannel Guard

### Enable EtherChannel Guard
```
etherchannel guard misconfig
! Detects and disables misconfigured ports
! Prevents:
! - Speed/duplex mismatch
! - VLAN/allowed-VLAN mismatch
! - Port-security mismatch
```

### View Guard Status
```
show etherchannel misconfig
! Displays any misconfigurations detected
```

## Load Balancing Testing

### Verify Load Distribution
```
! View traffic on individual ports
show interfaces GigabitEthernet0/1 | include packets
show interfaces GigabitEthernet0/2 | include packets

! Should see roughly equal distribution
! If imbalanced, consider changing load-balance algorithm
```

### Algorithm Selection for Traffic Type
```
! Web traffic (mostly unidirectional):
port-channel load-balance src-dst-port
! Distributes based on session

! IP multicast:
port-channel load-balance dst-ip
! Multicast sources often same, destinations differ

! IP unicast:
port-channel load-balance src-dst-ip
! Most balanced for typical traffic
```

## EtherChannel Failover Testing

### Manual Port Shutdown Test
```
interface GigabitEthernet0/1
  shutdown
  ! Traffic should continue on remaining ports

show etherchannel 1 summary
! Shows port as suspended

no shutdown
! Port rejoins active port-channel
```

### Monitor Failover Impact
```
! Measure convergence
! With proper LACP fast (1s), minimal packet loss

! Individual port failures transparent to port-channel
! No STP reconvergence needed
```

## Monitoring EtherChannel

### Status Verification
```
show etherchannel summary
show etherchannel brief
show etherchannel 1 detail
show etherchannel port-channel
show etherchannel neighbors  ! LACP neighbors
```

### Per-Port Monitoring
```
show interfaces Port-channel 1
show interfaces GigabitEthernet0/1 | include PortChannel
show etherchannel 1 port-neighbor
```

### LACP Protocol Details
```
show lacp 1 neighbor    ! LACP neighbor details
show lacp 1 internal    ! LACP internal state
show lacp detail
```

## Troubleshooting EtherChannel Issues

### Issue: Channel Not Forming

**Symptom:** Ports show as "suspended" in channel-group

**Causes:**
```
1. Mode mismatch (active vs passive, etc)
2. Configuration differences (speed, duplex, VLAN)
3. Protocol mismatch (LACP vs PAgP)
4. Portfast/spanning-tree conflicts

Verification:
show etherchannel detail
show etherchannel port-neighbor
show interfaces Port-channel 1
```

### Issue: Unequal Load Distribution

**Symptom:** Traffic imbalanced across ports

**Causes:**
```
1. Default algorithm not optimal for traffic type
2. Hash function limited by traffic patterns
3. Single flow dominates (high-bandwidth link)

Solution:
port-channel load-balance src-dst-port  ! Often better
! Or accept imbalance (individual flows still get full bandwidth)
```

### Issue: Ports Suspended

**Symptom:** Some ports not participating

**Causes:**
```
1. Configuration mismatch (different VLAN, speed)
2. Port-security limit reached
3. STP blocking (if portfast not set)

Resolution:
show etherchannel misconfig
show spanning-tree | include Port-channel
Fix misconfigurations and re-enable
```

## Deployment Checklist

### Pre-Deployment
- [ ] Verify all ports match (speed, duplex, VLAN)
- [ ] Choose LACP (standard) or PAgP (Cisco)
- [ ] Plan load-balancing algorithm
- [ ] Document channel-group numbers
- [ ] Plan active-passive or active-active roles

### Configuration
- [ ] Configure physical ports with channel-group
- [ ] Specify channel-protocol (lacp/pagp)
- [ ] Configure port-channel interface
- [ ] Set trunk/access mode on port-channel
- [ ] Configure spanning-tree settings
- [ ] Set load-balancing algorithm
- [ ] Enable EtherChannel Guard

### Verification
- [ ] Verify channel formation: `show etherchannel summary`
- [ ] Check protocol status: `show lacp neighbor` or `show pagp neighbor`
- [ ] Verify load distribution
- [ ] Test failover with port shutdown
- [ ] Validate spanning-tree status

### Production Monitoring
- [ ] Monitor channel status (suspended ports)
- [ ] Track load distribution
- [ ] Alert on channel breakage
- [ ] Monitor port failures
- [ ] Verify consistent configuration across switches

## Best Practices

1. **Use LACP** over PAgP (standards-based, multi-vendor)
2. **Active-Passive LACP** (avoids negotiation issues)
3. **Consistent configuration** across all ports in bundle
4. **Port-channel interface** for management/STP
5. **EtherChannel Guard** to catch misconfigurations
6. **Load balancing algorithm** tuned for traffic type
7. **LACP rate slow** for WAN, fast for LAN
8. **Individual port monitoring** for troubleshooting
9. **Documentation** of bundle membership and numbering
10. **Testing** of failover before production use
