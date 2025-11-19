# Route Redistribution Guide

## When to Redistribute Routes

### Use Cases

1. **Protocol Migration:** Transitioning from RIPv2 to OSPF
2. **Multi-Protocol Network:** Different departments running different IGPs
3. **External Route Injection:** Connecting to ISP or partner networks
4. **Legacy Systems:** Supporting older routing protocols

### Avoid Redistribution When Possible

- Simple networks: Use single IGP
- Redundant paths: May create suboptimal routing
- Policy-heavy environments: Increased complexity

## Metric Strategy

### Metric Translation Principle

```
Source Protocol  →  Target Protocol
EIGRP 1000       →  OSPF ?
                    RIPv2 ?
                    BGP ?
```

### Metric Selection

```
EIGRP to OSPF:
redistribute eigrp 100 metric 100 metric-type 2

! OSPF cost 100 = approximately 10Mbps link
! Adjust based on actual link speed

OSPF to EIGRP:
redistribute ospf 1 metric 1000 100 255 1 1500
! BW=1000, Delay=100*10us, Reliability=255, Load=1, MTU=1500
```

### Default Metrics

```
EIGRP: Cannot accept routes without metric spec
OSPF:  Metric 20 (type-2) if not specified
RIPv2: Metric 16 (invalid/unreachable) if not specified
BGP:   MED 0 if not specified
```

## Single Redistribution Point Architecture

### Hub-and-Spoke Design
```
ISP (BGP)
  ↓ ASBR A (Single point)
  ├── OSPF Campus
  ├── EIGRP WAN
  └── RIPv2 Legacy

All external routes → ASBR A
All internal routes → respective IGPs
```

### Configuration
```
! ASBR A
router ospf 1
  redistribute bgp 65000 metric 100 metric-type 2
  redistribute eigrp 100 metric 100 metric-type 2

router eigrp 100
  redistribute ospf 1 metric 1000 100 255 1 1500
  redistribute bgp 65000 metric 1000 100 255 1 1500

router bgp 65000
  redistribute ospf 1
  redistribute eigrp 100
```

## Bidirectional Redistribution (Loop Prevention)

### Tag-Based Loop Prevention
```
! Router-A: Export from OSPF, Import into EIGRP
route-map OSPF_TO_EIGRP out
  set tag 100
! Applied outbound

route-map PREVENT_LOOP_EIGRP in
  match tag 100
  deny  ! Deny routes tagged from OSPF
! Applied inbound on EIGRP imports

! Router-B: Same concept in reverse
route-map EIGRP_TO_OSPF out
  set tag 200

route-map PREVENT_LOOP_OSPF in
  match tag 200
  deny
```

### Distance-Based Loop Prevention
```
! Increase external distance to prefer internal
router eigrp 100
  distance eigrp 90 200  ! Internal 90, External 200

! Locally originated < redistribution
network 10.0.0.0        ! Preferred over redistributed
```

## Filtering During Redistribution

### Distribute-List Filtering
```
! OSPF to EIGRP with filtering
access-list 1 permit 10.0.0.0 0.255.255.255

route-map FILTER_OSPF in
  match ip address 1
  set metric 1000 100 255 1 1500

router eigrp 100
  redistribute ospf 1 route-map FILTER_OSPF
```

### Prefix-List Filtering
```
! More scalable than ACLs
ip prefix-list OSPF_ROUTES seq 10 permit 10.0.0.0/8
ip prefix-list OSPF_ROUTES seq 20 permit 10.1.0.0/16
ip prefix-list OSPF_ROUTES seq 30 deny 0.0.0.0/0 le 32

route-map OSPF_FILTER in
  match ip address prefix-list OSPF_ROUTES

router eigrp 100
  redistribute ospf 1 route-map OSPF_FILTER
```

## Multi-Point Redistribution

### When Single Point Fails
```
ISP (BGP)
  ↓
┌─────────────────────┐
ASBR-A              ASBR-B (Backup)
  ├── OSPF Campus ←→ OSPF Campus
  └─ EIGRP WAN  ←→ EIGRP WAN
```

### Configuration Strategy
```
! Both ASBR-A and ASBR-B:
route-map FROM_BGP_A in
  set tag 100
  set local-preference 200  ! Prefer primary

route-map FROM_BGP_B in
  set tag 200
  set local-preference 100  ! Backup

! On receiving routers:
route-map NO_LOOP in
  match tag 100,200
  deny    ! No re-redistribution

! Prevent ASBR-A from receiving from ASBR-B
route-map PREVENT_LOOP in
  match tag 200  ! From backup ASBR
  deny
```

## Default Route Injection

### Static Default to OSPF
```
ip route 0.0.0.0 0.0.0.0 10.0.0.254

router ospf 1
  default-information originate metric 100
  ! Or always originate:
  default-information originate always metric 100
```

### Default Route to EIGRP (via Static)
```
ip route 0.0.0.0 0.0.0.0 10.0.0.254

router eigrp 100
  redistribute static metric 1000 100 255 1 1500
  ! Or explicit:
  network 0.0.0.0
```

## OSPF Metric Types

### Type 1 (E1) vs Type 2 (E2)
```
Type 1 (E1):
Cost = External Metric + Internal Path Cost to ASBR
Prefers closer ASBR

Type 2 (E2) - Default:
Cost = External Metric Only
Any ASBR equally preferred
```

### Selection Guidance
```
redistribute bgp 65000 metric 100 metric-type 1
! Use Type 1 if:
- Multiple ASBRs redistributing same routes
- Prefer closest exit point
- WAN topology with variable link costs

redistribute bgp 65000 metric 100 metric-type 2
! Use Type 2 if:
- Simple redundancy
- All exit points equivalent
- Reduce routing computation
```

## Mutual Redistribution Example

### OSPF and EIGRP Coexistence
```
! Router A (at boundary)
router ospf 1
  redistribute eigrp 100 metric 100 metric-type 2
  distribute-list prefix OSPF_ONLY out eigrp 100

router eigrp 100
  redistribute ospf 1 metric 1000 100 255 1 1500
  distribute-list prefix EIGRP_ONLY out ospf 1

! IP Prefix lists
ip prefix-list OSPF_ONLY permit 10.1.0.0/16
ip prefix-list OSPF_ONLY permit 10.2.0.0/16
ip prefix-list EIGRP_ONLY permit 192.168.1.0/24
ip prefix-list EIGRP_ONLY permit 192.168.2.0/24
```

## Summarization During Redistribution

### Reduce Routing Table Size
```
! Summary static routes before redistribution
ip route 10.0.0.0 255.0.0.0 null0

router eigrp 100
  redistribute static metric 1000 100 255 1 1500
  ! Advertises single 10.0.0.0/8 instead of /16s
```

### Aggregate in Target Protocol
```
! OSPF aggregation at ABR
router ospf 1
  area 0 range 10.0.0.0 255.0.0.0
  ! Suppresses detailed routes in other areas

! EIGRP aggregation
interface GigabitEthernet0/0
  ip summary-address eigrp 100 192.168.0.0 255.255.0.0
  ! Reduces advertisements from WAN
```

## Verification Commands

### Verify Redistribution
```
show ip route [protocol]  ! View redistributed routes
show ip route bgp         ! BGP-redistributed routes
show ip route eigrp       ! EIGRP-redistributed routes
show ip route ospf        ! OSPF-redistributed routes

! Check source of route
show ip route 10.0.0.0/8
! Should show [redistribution source number/AD]
```

### Metrics in Detail
```
show ip bgp 10.0.0.0/8           ! BGP metric details
show ip eigrp topology 10.0.0.0/8  ! EIGRP metric breakdown
show ip ospf database external   ! OSPF external LSAs
```

## Troubleshooting

### Routes Not Appearing

**Check:**
1. Source protocol generates routes: `show ip route [protocol]`
2. Redistribution configured: `show run | include redistribute`
3. Filtering blocking routes: `show route-map`
4. Metrics configured: `show redistribute`

### Suboptimal Routing

**Check:**
1. Administrative distance: `show ip protocol`
2. Metrics equal: `show ip route [destination]`
3. Load balancing: `show ip route [destination] | include via`

### Loop Detection

**Check:**
1. Tags applied: `show ip bgp [route] | include tag`
2. Distance set appropriately
3. Neighbor routing table not advertising back

## Deployment Checklist

### Planning
- [ ] Identify redistribution points
- [ ] Plan metrics (translate between protocols)
- [ ] Design loop prevention (tags or distance)
- [ ] Plan filtering strategy
- [ ] Document flow of routes

### Configuration
- [ ] Configure redistribute commands
- [ ] Specify metrics appropriately
- [ ] Implement route-maps for filtering
- [ ] Apply tags for loop prevention
- [ ] Test in lab first

### Verification
- [ ] Verify routes appear: `show ip route [protocol]`
- [ ] Check metrics: `show ip route [destination]`
- [ ] Validate path selection
- [ ] Test with ping/traceroute
- [ ] Monitor for loops

### Monitoring
- [ ] Track route count
- [ ] Monitor convergence time
- [ ] Alert on unexpected route changes
- [ ] Verify no routing loops
- [ ] Track redistribution changes

## Best Practices

1. **Single redistribution point:** Simplifies design
2. **Explicit metrics:** Never rely on defaults
3. **Tag-based filtering:** Prevents accidental loops
4. **Documentation:** Record metric decisions
5. **Gradual migration:** Don't redistribute everything immediately
6. **Redundancy planning:** Multiple redistribution points if critical
7. **Summarization:** Reduce routing table size
8. **Testing:** Lab validation before production
9. **Monitoring:** Active tracking of redistributed routes
10. **Simplification goal:** Eventually migrate to single protocol
