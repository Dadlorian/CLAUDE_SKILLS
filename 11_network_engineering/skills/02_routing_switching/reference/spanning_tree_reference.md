# Spanning Tree Protocol Quick Reference

## STP Versions

| Version | Standard | Priority | Convergence | MST Support |
|---------|----------|----------|-------------|------------|
| STP | 802.1D | 32768 | ~30-50s | No |
| RSTP | 802.1w | 32768 | ~6s | No |
| MSTP | 802.1s | 32768 | ~6s per region | Yes |

## STP Timers

| Timer | Default | Range | Purpose |
|-------|---------|-------|---------|
| Hello Time | 2 seconds | 1-10s | BPDU transmission |
| Forward Delay | 15 seconds | 4-30s | Port state transitions |
| Max Age | 20 seconds | 6-40s | BPDU staleness |
| Message Age | Increment | N/A | BPDU aging in transit |

**Constraint:** Max Age > 2 × (Hello Time + 1 second)
**Constraint:** Forward Delay > Hello Time + 1 second

## Root Bridge Election

1. **Bridge Priority** (lower wins): 0-61440 (increment 4096)
   - Format: `priority value` or `priority-hello-delay forward-delay max-age`
2. **MAC Address** (lower wins, tiebreaker): 48-bit hardware address

```
! Set root bridge (priority 0)
spanning-tree vlan 10 root primary

! Set secondary root (priority 4096 + existing)
spanning-tree vlan 10 root secondary

! Manual priority
spanning-tree vlan 10 priority 8192
```

## Port Role and State

### Port Roles

| Role | Purpose |
|------|---------|
| Root Port | Lowest-cost path to root bridge |
| Designated Port | Segment toward non-root switch |
| Alternate Port | Backup for root port (RSTP) |
| Backup Port | Backup for designated port (RSTP) |
| Disabled Port | Manually disabled or blocked |

### Port States

| State | BPDU | MAC Learning | Frame Forward |
|-------|------|--------------|---------------|
| Disabled | No | No | No |
| Blocking | Yes | No | No |
| Listening | Yes | No | No |
| Learning | Yes | Yes | No |
| Forwarding | Yes | Yes | Yes |

**Note:** RSTP merges Listening & Learning into single Discarding state

## Port Cost Calculation

### 802.1D (Legacy)

| Link Speed | Cost |
|-----------|------|
| 4 Mbps | 250 |
| 10 Mbps | 100 |
| 16 Mbps | 62 |
| 100 Mbps | 19 |
| 1 Gbps | 4 |
| 10 Gbps | 2 |

### 802.1w/802.1s (RSTP/MSTP)

| Link Speed | Cost |
|-----------|------|
| 10 Mbps | 2,000,000 |
| 100 Mbps | 200,000 |
| 1 Gbps | 20,000 |
| 10 Gbps | 2,000 |
| 100 Gbps | 200 |
| 1 Tbps | 20 |

```
! Modify port cost
interface GigabitEthernet0/1
  spanning-tree cost 100
```

## Bridge Protocol Data Unit (BPDU)

### BPDU Frame Structure
- **Destination MAC:** 01:80:C2:00:00:00
- **SSAP/DSAP:** 0x42 (STP/RSTP)
- **Control Byte:** 0x03
- **Protocol ID:** 0x0000
- **Protocol Version:** 0 (STP), 2 (RSTP), 4 (MSTP)
- **BPDU Type:** Configuration/TCN/RSTP/MST

### Configuration BPDU Fields
1. Root Bridge ID (Priority + MAC)
2. Root Path Cost
3. Bridge ID (Priority + MAC)
4. Port ID
5. Message Age
6. Max Age
7. Hello Time
8. Forward Delay

## RSTP (802.1w)

### Key Improvements
- **Faster Convergence:** 6 seconds instead of 30-50 seconds
- **Port Roles:** Root, Designated, Alternate, Backup
- **Port States:** Discarding, Learning, Forwarding
- **Proposal/Agreement:** Mechanism for rapid transitions
- **Backward Compatible:** With 802.1D switches

### RSTP Port Types
- **Edge Port:** Connected to end devices (PortFast-equivalent)
- **Point-to-Point:** Full-duplex link (rapid transition)
- **Shared:** Half-duplex/shared media

## MSTP (802.1s)

### Multiple Spanning Tree Regions
- **Region Name:** Unique identifier (32 bytes)
- **Revision Level:** 0-65535 (all switches must match)
- **Instances:** 0 (CST) + 1-4094 (MST instances)

```
! Configure MSTP
spanning-tree mode mst
spanning-tree mst configuration
  name ciscocert
  revision 1
  instance 1 vlan 10,20,30
  instance 2 vlan 40,50,60

spanning-tree mst 1 root primary
spanning-tree mst 1 priority 8192
```

## STP Enhancements

### PortFast
```
interface GigabitEthernet0/1
  spanning-tree portfast
```
- Skip Listening/Learning states
- Use on access/host ports only
- Risk: VLAN loop if misconfigured

### BPDU Guard
```
interface GigabitEthernet0/1
  spanning-tree bpduguard enable
```
- Disable port if BPDU received
- Prevents unauthorized STP devices
- Requires PortFast enabled

### Root Guard
```
interface GigabitEthernet0/1
  spanning-tree guard root
```
- Prevent port becoming root port
- Protects root bridge
- Port transitions to Discarding if superior BPDU received

### Loop Guard
```
interface GigabitEthernet0/1
  spanning-tree guard loop
```
- Prevent loop guard via unidirectional link failure
- Port transitions to Loop Inconsistent
- Requires point-to-point link

### BPDU Filter
```
interface GigabitEthernet0/1
  spanning-tree bpdufilter enable
```
- Stop sending/receiving BPDUs
- On PortFast ports only
- Use with caution (creates loops)

## STP Troubleshooting

```
! View STP status
show spanning-tree
show spanning-tree summary
show spanning-tree vlan 10
show spanning-tree interface GigabitEthernet0/1
show spanning-tree inconsistency

! Debug STP events
debug spanning-tree events
debug spanning-tree detail
debug spanning-tree packets
```

## Best Practices

1. Use RSTP (802.1w) on modern networks
2. Configure primary and secondary root bridges explicitly
3. Implement PortFast + BPDU Guard on access ports
4. Implement BPDU Guard on trunk ports to untrusted devices
5. Use consistent timers across topology (preferably defaults)
6. Monitor for topology changes and loops
7. Document STP design (VLAN blocking, root placement)
8. Use MSTP for large networks (>3 spanning trees)
9. Avoid manual cost/priority adjustments
10. Enable loop guard on switch-to-switch links
