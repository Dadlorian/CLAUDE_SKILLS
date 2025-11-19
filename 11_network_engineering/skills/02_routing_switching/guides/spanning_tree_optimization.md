# Spanning Tree Optimization Guide

## Choosing STP Version

### Migration Path: STP → RSTP → MSTP

**STP (802.1D):**
- Legacy, slow convergence (30-50s)
- Use only on very old equipment
- Simple configuration

**RSTP (802.1w):**
- Modern standard, faster convergence (6s)
- Recommended for most networks
- Backward compatible with 802.1D

**MSTP (802.1s):**
- Advanced multi-instance support
- Fast convergence per instance
- Complex configuration, requires planning

### Enable RSTP
```
spanning-tree mode rapid-pvst
! Or MSTP:
spanning-tree mode mst
```

## Root Bridge Optimization

### Primary and Secondary Root Placement

**Two-Tier Network:**
```
                    Core
                  [Root 1]
                  [Root 2]
                   (Primary)
                      ↓
            Distribution Layer
            ├─ Switch-A
            ├─ Switch-B
            └─ Switch-C
                      ↓
            Access Layer
            └─ Various Switches
```

**Three-Tier Network:**
```
            Main Campus (Root)
                    ↓
        ┌──────┬──────┬──────┐
    Building-A  B  C  D  (Secondary Roots)
        ↓       ↓  ↓  ↓
     Access   Access Access Access
```

### Root Bridge Configuration
```
! Configure primary root (lowest priority = 0)
spanning-tree vlan 100 root primary

! Configure secondary root (priority = 28672)
spanning-tree vlan 100 root secondary

! Manual priority setting
spanning-tree vlan 100 priority 8192

! View root status
show spanning-tree vlan 100 | include Root
```

## Port Cost Optimization

### Legacy vs Modern Costs
```
! Use modern costs (802.1w) on all new switches
spanning-tree pathcost method short  ! Legacy (default)
spanning-tree pathcost method long   ! Modern

! Manual cost on interface
interface GigabitEthernet0/1
  spanning-tree cost 20000  ! Force path priority
```

### Preferred Path Selection
```
! High-speed links prefer low cost
interface GigabitEthernet0/1 (10Gbps)
  spanning-tree cost 100    ! Lower = preferred

! Lower-speed link deprioritized
interface GigabitEthernet0/2 (1Gbps)
  spanning-tree cost 1000   ! Higher = less preferred
```

## Port Roles and Optimization

### Root Port Selection
```
! Port with lowest cost to root
! Automatically selected

! View root port
show spanning-tree vlan 100 | include Root Port
```

### Designated Port Optimization
```
! Fastest link becomes designated
! Can be forced with cost adjustment
interface GigabitEthernet0/48
  spanning-tree cost 100      ! Primary designated port

interface GigabitEthernet0/47
  spanning-tree cost 1000     ! Backup designated port
```

### Blocked Port Behavior
```
! Alternate port (ready for failover)
! Backup port (backup designated)
! Both block traffic, learn MAC addresses

! View port roles
show spanning-tree detail | include Role
```

## RSTP Enhancements

### Point-to-Point Link Detection
```
! Automatic on full-duplex links
! Manual specification:
interface GigabitEthernet0/1
  spanning-tree link-type point-to-point

! Alternative:
interface GigabitEthernet0/1
  spanning-tree link-type shared
```

### Edge Port Configuration
```
! Skip listening/learning states
interface GigabitEthernet0/1 (connected to host)
  spanning-tree portfast

! On all access ports (global)
spanning-tree portfast default
```

### BPDU Guard and Root Guard
```
! Enable on edge ports globally
spanning-tree portfast bpduguard default

! Per-port override
interface GigabitEthernet0/1
  spanning-tree bpduguard enable

! Prevent becoming root port
interface GigabitEthernet0/48 (Uplink)
  spanning-tree guard root
  ! Port goes to root inconsistent if superior BPDU received
```

## Loop Guard and UDLD

### Loop Guard (Prevents Alternate Port Loops)
```
! Enable on trunk ports
interface GigabitEthernet0/48
  spanning-tree guard loop

! Global:
spanning-tree loopguard default

! Monitor loops
show spanning-tree inconsistency
```

### UDLD (Unidirectional Link Detection)
```
! Prevent uni-directional links causing loops
udld enable

interface GigabitEthernet0/48
  udld port aggressive  ! Err-disable on failure

! View UDLD status
show udld neighbors
```

## MSTP Configuration

### Multi-Instance Spanning Tree

**Region Definition:**
```
spanning-tree mode mst
spanning-tree mst configuration
  name myregion
  revision 1

  ! Create instances
  instance 1 vlan 100,110,120
  instance 2 vlan 200,210,220
  instance 3 vlan 300,310,320
```

**Instance-Specific Root:**
```
spanning-tree mst 0 priority 4096    ! CST (common spanning tree)
spanning-tree mst 1 root primary     ! Instance 1 root
spanning-tree mst 2 root primary     ! Instance 2 root
spanning-tree mst 3 root primary     ! Instance 3 root

! Secondary roots for failover
spanning-tree mst 1 root secondary
```

### MSTP Design Benefits
- Load balancing across instances
- Fast convergence per instance
- Reduced BPDUs compared to PVST+

## Timer Optimization

### Default Timers (Usually Optimal)
```
Hello Time: 2 seconds
Forward Delay: 15 seconds
Max Age: 20 seconds

! Relationship constraints:
! Max Age = 2 × (Hello + 1)
! Forward Delay = Hello + 1

! Change timers (usually not needed)
spanning-tree vlan 100 hello-time 2
spanning-tree vlan 100 forward-time 15
spanning-tree vlan 100 max-age 20
```

### Fast Convergence (RSTP)
```
! RSTP converges much faster
! Timer values less critical
! Typically 1-6 seconds total
```

## EtherChannel and Spanning Tree

### EtherChannel as Single Link
```
! Port-channel treated as single link by STP
interface Port-channel 1
  spanning-tree cost 100    ! Entire port-channel cost

! Individual ports inherit cost
```

### Port-Channel with Load Balancing
```
! STP sees port-channel as single path
! EtherChannel distributes load
! Best of both worlds
```

## Monitoring and Diagnostics

### STP Status Verification
```
show spanning-tree
show spanning-tree summary
show spanning-tree vlan 100 detail
show spanning-tree interface GigabitEthernet0/1

! View BPDU details
show spanning-tree interface GigabitEthernet0/1 detail
```

### Troubleshooting Commands
```
! Topology changes
show spanning-tree vlan 100 | include Changes

! Inconsistent ports
show spanning-tree inconsistency

! Rapid STP protocol
debug spanning-tree bpdu

! Loop detection
show spanning-tree statistics
```

## Convergence Testing

### Manual Failover Test
```
! Disable link and measure convergence
interface GigabitEthernet0/48
  shutdown

! Measure time until traffic resumes via alternate path
! RSTP should converge in <6 seconds

! Re-enable link
no shutdown
```

### STP Stability Monitoring
```
! Excessive topology changes = unstable network
show spanning-tree [vlan 100] | include Changes

! Investigate causes:
- Flapping ports
- Unstable link quality
- Equipment failures
```

## Best Practices for Optimization

1. **Use RSTP** (802.1w) on modern equipment
2. **Two root bridges** for redundancy
3. **Consistent native VLAN** on all trunks
4. **PortFast on access ports** with BPDU Guard
5. **Root Guard on uplinks** to prevent topology takeover
6. **Loop Guard on trunk ports** to prevent loops
7. **Tune port costs** to prefer desired paths
8. **Use MSTP** for large networks (30+ VLANs)
9. **Monitor topology changes** actively
10. **Document STP design** clearly

## Performance Metrics

### Desired STP Metrics
- **Convergence time:** <6 seconds (RSTP)
- **BPDU count:** Stable (no flapping)
- **Port role stability:** No unexpected changes
- **Topology changes:** <1 per hour (ideally zero)

### Warning Signs
- **Topology changes:** >10 per hour (indicates instability)
- **Convergence time:** >10 seconds (indicates delay)
- **Blocked ports:** More than expected (check design)
- **BPDU Guard violations:** High (check port security)

## Deployment Checklist

### Pre-Deployment
- [ ] Choose STP version (RSTP recommended)
- [ ] Design root placement strategy
- [ ] Plan instance allocation (if using MSTP)
- [ ] Document switch priorities
- [ ] Plan port cost strategy

### Configuration
- [ ] Enable appropriate STP version
- [ ] Configure root bridges (primary/secondary)
- [ ] Set port costs on strategic links
- [ ] Enable PortFast on access ports
- [ ] Enable BPDU Guard globally
- [ ] Configure Root Guard on uplinks
- [ ] Set up UDLD on important links
- [ ] Configure timers (if needed)

### Verification
- [ ] Verify spanning-tree mode: `show spanning-tree`
- [ ] Check root bridge: `show spanning-tree root`
- [ ] Verify port roles: `show spanning-tree detail`
- [ ] Test convergence with link failures
- [ ] Monitor for topology changes

### Production Monitoring
- [ ] Alert on topology changes
- [ ] Monitor convergence time
- [ ] Track BPDU Guard violations
- [ ] Monitor for loops (loop guard)
- [ ] Track port state changes
