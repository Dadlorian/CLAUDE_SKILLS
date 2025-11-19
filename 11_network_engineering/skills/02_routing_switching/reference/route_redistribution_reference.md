# Route Redistribution Quick Reference

## Redistribution Basics

- **Purpose:** Move routes between different routing protocols
- **AD Impact:** External routes have lower priority (AD+10 usually)
- **Metric:** Must be specified or uses default
- **Two-way:** Must be configured on both directions if mutual

## Default Metrics for Redistribution

| Protocol | Default Metric | Format | Override |
|----------|----------------|--------|----------|
| RIPv2 | 16 (invalid) | Hop count | `metric [0-15]` |
| EIGRP | Infinite (cannot redistribute) | BW, delay, etc | Network command |
| OSPF | 20 | Cost | `metric [1-16777214]` |
| BGP | 0 | MED | `metric [0-4294967295]` |
| Static | 0 (variable) | N/A | As configured |
| Connected | Variable by protocol | N/A | N/A |

## Redistribution Syntax

### OSPF to EIGRP
```
router eigrp 100
  redistribute ospf 1 metric 1000 100 255 1 1500
  ! metric: bandwidth delay reliability load mtu
```

### EIGRP to OSPF
```
router ospf 1
  redistribute eigrp 100 metric 100 metric-type 2
```

### BGP to OSPF
```
router ospf 1
  redistribute bgp 65000 metric 100 metric-type 2
```

### OSPF to BGP
```
router bgp 65000
  redistribute ospf 1
```

### Static Routes
```
router ospf 1
  redistribute static metric 100
```

### Connected Routes
```
router eigrp 100
  redistribute connected metric 1000 100 255 1 1500
```

## Metric Translation Reference

### EIGRP Metric Components (BW, Delay, Reliability, Load, MTU)

```
RIPv2 to EIGRP:
redistribute rip metric 1000 100 255 1 1500
(BW=1000, Delay=100*10us, Reliability=255, Load=1, MTU=1500)

OSPF to EIGRP:
redistribute ospf 1 metric 1000 100 255 1 1500
(Same as above - requires manual specification)

EIGRP to OSPF:
redistribute eigrp 100 metric 100
(OSPF cost, default for type-5 LSAs)
```

### OSPF Cost Calculation
```
Cost = 10^8 / Bandwidth (kbps)

Examples:
- Metric 100 = 10^8 / 1,000,000 = 100 (1Gbps)
- Metric 1000 = 10^8 / 100,000 = 1000 (100Mbps)
- Metric 1000000 = 10^8 / 100 = 1000000 (100kbps)
```

## Route Filtering During Redistribution

### ACL-Based Filtering
```
access-list 10 permit 10.0.0.0 0.255.255.255
access-list 10 deny any

router ospf 1
  redistribute eigrp 100 metric 100 match internal
  distribute-list 10 out eigrp 100
```

### Prefix-List Filtering
```
ip prefix-list ALLOWED seq 10 permit 10.0.0.0/8
ip prefix-list ALLOWED seq 20 deny 0.0.0.0/0 le 32

router ospf 1
  redistribute eigrp 100 metric 100
  distribute-list prefix ALLOWED out eigrp 100
```

### Route-Map Filtering
```
route-map REDIST_CONTROL in
  match ip address prefix-list ALLOWED
  set metric 100
  set metric-type type-2

router ospf 1
  redistribute eigrp 100 route-map REDIST_CONTROL
```

## Tag-Based Redistribution

- **Purpose:** Loop prevention and selective redistribution
- **Scope:** Within routing domains
- **Implementation:** Tag on redistribution, match on re-redistribution

```
! First ASBR (redistribute OSPF to BGP)
route-map TAG_OSPF out
  set tag 100

router bgp 65000
  redistribute ospf 1 route-map TAG_OSPF

! Second ASBR (prevent re-redistribution)
route-map PREVENT_LOOP deny 10
  match tag 100

route-map ALLOW_OTHER permit 20

router ospf 1
  redistribute bgp 65000 route-map PREVENT_LOOP route-map ALLOW_OTHER
```

## Mutual Redistribution (Bidirectional)

### Configuration Pattern
```
! Router-A: OSPF to EIGRP
router eigrp 100
  redistribute ospf 1 metric 1000 100 255 1 1500
  default-metric 1000 100 255 1 1500

! Router-A: EIGRP to OSPF
router ospf 1
  redistribute eigrp 100 metric 100 metric-type 2

! Router-B: EIGRP to OSPF
router ospf 1
  redistribute eigrp 100 metric 100 metric-type 2

! Router-B: OSPF to EIGRP
router eigrp 100
  redistribute ospf 1 metric 1000 100 255 1 1500
```

### Loop Prevention
```
! Use tags to prevent loops
route-map FROM_OSPF out
  set tag 100

route-map FROM_EIGRP out
  set tag 200

! Deny based on incoming tag
route-map NO_LOOP_OSPF deny 10
  match tag 200  ! Came from EIGRP, don't send back

route-map NO_LOOP_EIGRP deny 10
  match tag 100  ! Came from OSPF, don't send back
```

## Default Route Redistribution

### Static Default Route
```
ip route 0.0.0.0 0.0.0.0 10.0.0.1

router ospf 1
  redistribute static

! Or use default-information originate
router ospf 1
  default-information originate always metric 100
```

### OSPF Default Route Injection
```
! ASBR injects default
router ospf 1
  default-information originate metric 100 metric-type 2
  default-information originate always ! Even without default route
```

## OSPF Metric Type

| Type | Meaning | AD |
|------|---------|-----|
| Type 1 (E1) | External + internal distance | 110 |
| Type 2 (E2) | External only (default) | 110 |
| Type 2 (E2) | Lower cost path possible (different cost) | 110 |

```
router ospf 1
  redistribute bgp 65000 metric 100 metric-type 1
```

## Redistribution Loop Scenarios

### Scenario 1: Direct Redistribution Loop
```
OSPF (Area 1) <-> ASBR <-> EIGRP (AS 100)

If ASBR redistributes both directions without tags:
- OSPF route → EIGRP (correctly)
- EIGRP route → OSPF (now in OSPF again - loop)
```

### Scenario 2: Multiple ASBR Loop
```
OSPF (Area 1) <-> ASBR1 <-> EIGRP <-> ASBR2 <-> OSPF (Area 2)

Without tagging, ASBR1 could receive own routes back via ASBR2
```

### Scenario 3: BGP Re-redistribution
```
OSPF ← ASBR1 ← BGP ← ASBR2 ← OSPF

BGP advertises OSPF routes, ASBR2 redistributes back to OSPF
```

## Route Summarization in Redistribution

```
! EIGRP auto-summary (disabled by default now)
no auto-summary
ip summary-address eigrp 100 10.0.0.0 255.0.0.0

! Manual aggregation
aggregate-address 10.0.0.0 255.0.0.0
```

## Redistribution Best Practices

1. Always specify metric explicitly (never use default)
2. Implement tag-based loop prevention
3. Use route-maps for selective redistribution
4. Filter unnecessary routes (reduce overhead)
5. Document redistribution points and flows
6. Test bidirectional redistribution for loops
7. Monitor admin distance (prefer primary paths)
8. Use metric manipulation to control traffic flow
9. Implement graceful migration between protocols
10. Monitor route count and convergence time
