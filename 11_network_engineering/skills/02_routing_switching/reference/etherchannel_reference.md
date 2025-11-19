# EtherChannel Quick Reference Guide

## EtherChannel Protocols

### LACP (Link Aggregation Control Protocol)
- **Standard:** IEEE 802.3ad
- **Vendor:** Multi-vendor standard
- **Modes:**
  - **Active:** Initiates LACP negotiation
  - **Passive:** Responds to LACP negotiation
- **Max Ports:** 16 (all active), 8 per group
- **Timing:** 30 seconds (slow) or 1 second (fast)

### PAgP (Port Aggregation Protocol)
- **Standard:** Cisco proprietary
- **Modes:**
  - **Desirable:** Initiates PAgP negotiation
  - **Auto:** Responds to PAgP negotiation
- **Max Ports:** 16 (all active), 8 per group
- **Timing:** Slower than LACP

### Static EtherChannel
- **Mode:** On/On (no negotiation)
- **Negotiation:** None
- **Use Case:** Non-standard equipment or minimal overhead

## EtherChannel Configuration

```
! LACP Configuration
interface range GigabitEthernet0/1-2
  channel-group 1 mode active
  channel-protocol lacp

! Alternative: Passive for one side
interface range GigabitEthernet0/1-2
  channel-group 1 mode passive

! PAgP Configuration (legacy)
interface range GigabitEthernet0/1-2
  channel-group 1 mode desirable
  channel-protocol pagp

! Static EtherChannel
interface range GigabitEthernet0/1-2
  channel-group 1 mode on

! Configure port-channel interface
interface Port-channel 1
  switchport mode trunk
  switchport trunk encapsulation dot1q
```

## EtherChannel Port-Channel Interface

```
! Verify EtherChannel status
show etherchannel 1 summary
show etherchannel 1 detail
show etherchannel port-channel
show interfaces port-channel 1

! Port-channel configuration
interface Port-channel 1
  description Trunk to Switch-B
  switchport mode trunk
  spanning-tree cost 100
  ip address 10.0.0.1 255.255.255.0
```

## Load Balancing Algorithms

| Algorithm | Method | Use Case |
|-----------|--------|----------|
| dest-mac | Destination MAC address | Layer 2 |
| src-mac | Source MAC address | Layer 2 |
| dest-ip | Destination IP address | Layer 3 |
| src-ip | Source IP address | Layer 3 |
| dest-port | Destination TCP/UDP port | Layer 4 |
| src-port | Source TCP/UDP port | Layer 4 |
| src-dst-ip | Source + Destination IP | Layer 3 |
| src-dst-port | Source + Destination ports | Layer 4 |
| src-dst-mac | Source + Destination MAC | Layer 2 |

```
! View load balancing algorithm
show etherchannel load-balance

! Set algorithm (global)
port-channel load-balance [algorithm]

Example:
port-channel load-balance dst-ip
```

## LACP Configuration Details

### LACP Rate
```
! Fast LACP (1 second)
interface Port-channel 1
  lacp rate fast

! Slow LACP (30 seconds, default)
interface Port-channel 1
  lacp rate slow
```

### LACP Timeout
```
! Short timeout (3 seconds)
lacp system-priority 32768
lacp port-priority 32768
```

### LACP System ID
- **Priority:** 0-65535 (lower preferred)
- **MAC Address:** System MAC address
- **Format:** `priority:MAC` (e.g., 32768:aabb.ccdd.eeff)

## EtherChannel Constraints

### Port Requirements
- Same speed/duplex
- Same VLAN assignment
- Same spanning-tree settings
- Same native VLAN (for trunks)
- Same port-security configuration
- Same QoS configuration

### Configuration Consistency
- Access/Trunk mode must match
- Allowed VLAN lists must match
- Port configurations must be identical

## EtherChannel Negotiation

### LACP Active-Active
```
Switch-A: channel-group 1 mode active
Switch-B: channel-group 1 mode active
! Result: EtherChannel UP
```

### LACP Active-Passive
```
Switch-A: channel-group 1 mode active
Switch-B: channel-group 1 mode passive
! Result: EtherChannel UP
```

### LACP Passive-Passive
```
Switch-A: channel-group 1 mode passive
Switch-B: channel-group 1 mode passive
! Result: EtherChannel DOWN (no negotiation)
```

### Static On-On
```
Switch-A: channel-group 1 mode on
Switch-B: channel-group 1 mode on
! Result: EtherChannel UP (no protocol)
```

## EtherChannel Guard

```
! Enable EtherChannel Guard
etherchannel guard misconfig
```

- Detects misconfigured EtherChannels
- Shuts down affected ports
- Prevents unidirectional misconfiguration
- Error: PortFast mismatch, speed mismatch, duplex mismatch

## Troubleshooting EtherChannel

```
! Verify EtherChannel status
show etherchannel summary

! Detailed interface information
show interfaces port-channel 1

! LACP protocol details
show lacp 1 neighbor
show lacp 1 internal

! PAgP protocol details (legacy)
show pagp 1 neighbor
show pagp 1 internal

! Check for misconfigurations
show etherchannel misconfig
```

## EtherChannel Troubleshooting Scenarios

| Symptom | Cause | Resolution |
|---------|-------|------------|
| Channel DOWN | Mode mismatch | Set both to active or active/passive |
| Port suspended | Config mismatch | Verify identical configurations |
| EtherChannel not forming | Protocol mismatch | Enable same protocol on both sides |
| Unequal load distribution | Hash algorithm | Choose better algorithm or verify load |

## Best Practices

1. Use LACP for multi-vendor environments
2. Use Active-Passive LACP (avoids negotiation loops)
3. Maintain identical port configurations
4. Use Port-channel interfaces for management
5. Apply STP settings at Port-channel level
6. Enable EtherChannel guard
7. Monitor load distribution
8. Use fast LACP for data center environments
9. Document EtherChannel design and numbering
10. Test failover by disabling individual ports
