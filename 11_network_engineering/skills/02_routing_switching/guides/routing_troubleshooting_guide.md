# Routing Troubleshooting Guide

## Systematic Troubleshooting Approach

### The OSI Model Troubleshooting Process

1. **Layer 1 (Physical):** Verify cables, interfaces
2. **Layer 2 (Data Link):** Verify switching, VLANs
3. **Layer 3 (Network):** Verify routing, neighbors
4. **Layer 4+ (Transport):** Verify applications

### Routing Troubleshooting Flowchart

```
Host A can't reach Host B
    ↓
1. Ping local gateway
    ├─ Fails: Layer 2/1 issue (switch, VLAN)
    └─ Success: Continue
2. Ping remote gateway
    ├─ Fails: Routing issue
    └─ Success: Continue
3. Check route to destination
    ├─ No route: Redistribution issue
    └─ Route exists: Protocol/metric issue
4. Check protocol neighbor status
    ├─ Neighbor down: Adjacency problem
    └─ Neighbor up: Route advertisement issue
```

## Layer 1 and 2 Verification

### Interface Status
```
show interfaces
! Interface is up/down physically

show interfaces status
! Quick status of all interfaces

show interfaces GigabitEthernet0/1
! Detailed interface statistics

! Must show "up up" or "up(up)"
```

### VLAN Verification
```
show vlan brief
! Verify VLAN exists

show interfaces GigabitEthernet0/1 switchport
! Check VLAN assignment

show interfaces trunk
! Verify trunk configuration, allowed VLANs
```

### Spanning Tree Status
```
show spanning-tree
! Root bridge, costs, port roles

show spanning-tree vlan 100
! STP status per VLAN

show spanning-tree inconsistency
! Problems: BPDU Guard violations, Root Guard
```

## Layer 3 Verification

### IP Address and Routing Table

**Check IP Configuration:**
```
show ip interface brief
show ip interface GigabitEthernet0/1

! Must show IP address configured
! Interface must be "up"
```

**Check Routing Table:**
```
show ip route
! All known routes, administrative distance

show ip route [destination]
! Specific route details

show ip route summary
! Route count by source (connected, static, ospf, etc)
```

### Reachability Testing

```
ping [destination]
! Check layer 3 connectivity

ping -c 10 -S 10.0.0.1 10.0.0.2
! Ping from specific source

traceroute [destination]
! Show path to destination
```

## IGP Troubleshooting

### Protocol Status

**OSPF:**
```
show ip ospf process-id
! OSPF process running?

show ip ospf neighbor
! Neighbor relationships established?

show ip ospf database
! LSDB populated?

show ip route ospf
! Routes in routing table?
```

**EIGRP:**
```
show ip eigrp neighbors
! Neighbor relationships established?

show ip eigrp topology
! Routes in topology table?

show ip route eigrp
! Routes in routing table?
```

**RIPv2:**
```
show ip rip database
! RIP routes known?

show ip route rip
! Routes in routing table?
```

### Neighbor Adjacency Issues

**Common Causes:**
1. No direct IP connectivity
2. Firewall blocking protocol
3. Different subnet masks
4. Authentication failure
5. Passive interface enabled
6. Wrong network statement

**Diagnostic:**
```
show ip route [neighbor-ip]
! Can we reach the neighbor?

show ip eigrp neighbors
! Do we see neighbor?

show access-lists
! Any blocking filters?

debug ip eigrp | include [neighbor-ip]
! See negotiation process
```

### Route Advertisement Issues

**Routes not appearing:**
```
1. Check network statement
   show run | include network

2. Check route exists at source
   show ip route [route]

3. Check filtering
   show distribute-list
   show route-map
   show prefix-list

4. Check metric
   show ip route [route] | include metric
```

## BGP Troubleshooting

### BGP Neighbor Status

```
show ip bgp summary
! All neighbors and their status

show ip bgp neighbors 10.0.0.1
! Detailed neighbor information

show ip bgp neighbors 10.0.0.1 received-routes
! Routes received (before filtering)

show ip bgp neighbors 10.0.0.1 advertised-routes
! Routes advertised to neighbor
```

### BGP States

| State | Meaning | Issue |
|-------|---------|-------|
| Idle | Waiting to start | TCP/config issue |
| Connect | Attempting TCP | IP connectivity |
| Active | TCP established | Waiting for Open |
| OpenSent | Open message sent | Neighbor responding |
| OpenConfirm | Open confirmed | Finalizing |
| Established | Neighbor active | Working normally |

### Common BGP Issues

**Routes not received:**
```
1. Check neighbor status
   show ip bgp neighbors | include BGP

2. Check if routes exist at source
   show ip bgp neighbors 10.0.0.1 received-routes
   ! Shows all received (before filtering)

3. Check filtering
   show ip bgp dampening
   show prefix-list [name] detail
   show route-map [name]

4. Check community filtering
   show ip community-list
   show ip bgp [route] | include Community
```

**Routes not advertised:**
```
show ip bgp neighbors 10.0.0.1 advertised-routes
! Shows what we send

show ip bgp [route]
! Verify route is in our table

show route-map [name] | include permit
! Verify route-map permitting it
```

### BGP Best Path Selection

```
show ip bgp [route]
! Shows selected best path

show ip bgp [route] longer-prefixes
! Shows variants of route

show ip bgp [route] community [value]
! Routes with specific community
```

## Convergence Issues

### Slow Convergence

**Check timers:**
```
OSPF:
  show ip ospf | include Timer

EIGRP:
  show ip eigrp interface detail

BGP:
  show ip bgp neighbors | include Timers
```

**Improve convergence:**
```
OSPF: Reduce hello/dead timers
EIGRP: Tune SPF timers
BGP: Increase keepalive interval consistency
```

### Flapping Routes

**Identify source:**
```
show ip bgp dampening
! Route dampening active?

debug ip bgp updates
! See actual updates

show ip bgp [route] dampening
! Dampening state
```

**Cause root causes:**
1. Link instability (flapping)
2. Routing protocol instability
3. Configuration changes
4. Hardware issues (memory, CPU)

## Route Redistribution Troubleshooting

### Routing Loop Detection

```
show ip route [destination]
! Check source of route

show ip protocol
! Administrative distances

show ip bgp [route] | include AS-Path
! BGP path for loop check

debug ip routing
! See routing table changes
```

### Filtering Issues

```
show distribute-list
! Active filters

show route-map
! Route-map statistics

show access-lists
! ACL details

! Test prefix-list matching
ip prefix-list [name] description test
```

## Monitoring and Long-Term Troubleshooting

### Route Flapping Detection
```
show ip bgp flap-statistics
show ip bgp [route] | include Flap

! Configure dampening
router bgp 65000
  bgp dampening 15 750 2000 60
```

### Protocol Stability Metrics

**Track in operational environment:**
```
- Route count: show ip route summary
- Convergence time: test link failures
- Neighbor stability: monitor state changes
- CPU usage: show processes cpu
- Memory usage: show memory
```

### Syslog-Based Monitoring

```
logging 192.168.1.1
logging facility local0
logging level 6

! Critical events:
%OSPF-5-ADJCHG: OSPF adjacency change
%EIGRP-5-NBRCHANGE: EIGRP neighbor change
%BGP-3-NOTIFICATION: BGP neighbor down
```

## Common Scenarios and Solutions

### Scenario 1: Suboptimal Routing
**Problem:** Traffic taking longer path than expected

**Solution Steps:**
```
1. Check routing table:
   show ip route [destination]

2. Check costs/metrics:
   show ip ospf database
   show ip eigrp topology

3. Compare to alternative routes:
   traceroute [destination]

4. Adjust cost if needed:
   Interface cost adjustment
   Manual metric override
```

### Scenario 2: Intermittent Connectivity
**Problem:** Sometimes works, sometimes doesn't

**Solution Steps:**
```
1. Check for flapping:
   show interfaces [interface]
   show ip bgp flap-statistics

2. Check CPU/memory:
   show processes cpu
   show memory

3. Check for convergence delays:
   Monitor neighbor state changes

4. Check QoS queue drops:
   show interface [interface] | include drops
```

### Scenario 3: Routes Disappear
**Problem:** Route was there, now it's gone

**Solution Steps:**
```
1. Check neighbor status:
   show ip ospf neighbor
   show ip eigrp neighbor

2. Check for redistribution:
   show distribute-list
   show route-map

3. Check filtering:
   show access-lists
   show ip prefix-list

4. Check AD:
   show ip protocol
   show ip route [route]
```

## Debugging Commands

### Safe Debugging (Production)
```
! Conditional debugging (light CPU impact)
debug ip routing updatesout-fast
debug ip bgp keepalives
debug ip ospf adj

! Time-limited debugging
! terminal monitor
! undebug all (30 minutes later)
```

### Comprehensive Debugging (Lab/Maintenance)
```
debug ip packet
debug ip ospf events
debug ip eigrp packets
debug ip bgp updates

! Monitor output in separate session
! terminal monitor
show log
```

### Disable Debugging
```
no debug all
undebug all
! Verify: show debug
```

## Performance Baseline

### Capture Baseline Metrics
```
! Routing table size
show ip route summary

! Neighbor count
show ip ospf neighbor | include FULL

! Route convergence
test - failover a link, measure time to reroute

! CPU/Memory
show processes cpu
show memory
```

### Compare During Issues
```
! If performance degraded, compare to baseline
! Increased routes? CPU higher? Neighbors down?
```

## Troubleshooting Checklist

### For Any Routing Issue:
- [ ] Verify layer 1/2 connectivity
- [ ] Check interface status: `show interfaces`
- [ ] Verify IP addressing: `show ip interface brief`
- [ ] Check routing table: `show ip route`
- [ ] Check protocol neighbors: `show [igp] neighbors`
- [ ] Check network statements: `show run | include network`
- [ ] Test with ping/traceroute
- [ ] Review recent changes
- [ ] Check CPU/memory: `show processes`
- [ ] Review logs: `show log`

### For IGP Issues:
- [ ] Verify neighbor adjacency
- [ ] Check topology table: `show ip [igp] topology`
- [ ] Verify route metrics
- [ ] Check for loops
- [ ] Monitor convergence time

### For BGP Issues:
- [ ] Verify neighbor status
- [ ] Check received routes: `show ip bgp neighbors x.x.x.x received-routes`
- [ ] Verify filtering
- [ ] Check community/attributes
- [ ] Monitor dampening

## Best Practices

1. **Know your baseline:** Establish normal metrics
2. **Monitor proactively:** Don't wait for complaints
3. **Test frequently:** Failover scenarios, link failures
4. **Document changes:** Track what was modified
5. **Use syslog:** Centralize log collection
6. **Implement alerts:** CPU, memory, adjacency changes
7. **Keep lab updated:** Test in environment matching prod
8. **Training:** Team knowledge of protocols
9. **Simplicity:** Fewer protocols = easier troubleshooting
10. **Systematic approach:** OSI model top-to-bottom
