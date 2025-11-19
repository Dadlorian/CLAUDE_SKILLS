# BGP Best Practices Guide

## BGP Network Design Principles

### BGP Hierarchy

1. **Tier 1 (Backbone):** Core AS with iBGP mesh or RR
2. **Tier 2 (Regional):** Secondary ASes with hub-and-spoke
3. **Tier 3 (Edge):** Customer/branch ASes single-homed or dual-homed

### Address Space Planning

- **Public ASN Range:** 1-64511 (globally routed)
- **Private ASN Range:** 64512-65534 (internal only)
- **BGP Communities:** Plan allocation scheme
- **Route Targets:** RT scheme for VPN

## eBGP Peer Configuration

### Basic Peering
```
router bgp 65001
  bgp log-neighbor-changes
  neighbor 10.0.0.1 remote-as 65000
  neighbor 10.0.0.1 description "Link-to-ISP"
  neighbor 10.0.0.1 timers 60 180 180 300
  ! (Keepalive, Hold, Connect-Retry, Read-Timer)

  address-family ipv4
    neighbor 10.0.0.1 activate
    neighbor 10.0.0.1 soft-reconfiguration inbound
```

### eBGP Timers Strategy
- **Default:** 60s keepalive, 180s hold
- **Fast failover:** 3s keepalive, 9s hold
- **WAN links:** 30-60s keepalive (reduce churn)

### TTL and Security
```
neighbor 10.0.0.1 ebgp-multihop 2  ! For non-direct neighbors

neighbor 10.0.0.1 password MYPASSWORD  ! Authentication
```

## iBGP Peer Configuration

### Full Mesh
```
router bgp 65001
  ! For small AS (<50 routers)
  neighbor 192.168.1.1 remote-as 65001
  neighbor 192.168.1.2 remote-as 65001
  neighbor 192.168.1.3 remote-as 65001
```

### Route Reflector
```
! RR Configuration
router bgp 65001
  bgp cluster-id 1

  neighbor 192.168.1.1 remote-as 65001
  neighbor 192.168.1.1 route-reflector-client

  neighbor 192.168.1.2 remote-as 65001
  neighbor 192.168.1.2 route-reflector-client

! Client Configuration
router bgp 65001
  neighbor 192.168.1.100 remote-as 65001
  ! Routes learned from RR, no additional configuration
```

### Confederation
```
router bgp 65000
  bgp confederation identifier 65000
  bgp confederation peers 65001 65002 65003

  neighbor 10.0.0.1 remote-as 65001  ! Confederation peer
  neighbor 192.168.1.1 remote-as 65000  ! Internal peer
```

## Traffic Engineering with BGP

### AS-Path Prepending
```
route-map PREPEND_AS
  match ip address prefix-list CUSTOMER-A
  set as-path prepend 65001 65001
  ! Make route less preferred (longer path)

route-map PREPEND_AS
  match ip address prefix-list CUSTOMER-B
  set as-path prepend 65001
  ! Make route slightly less preferred

route-map PREPEND_AS
  match ip address prefix-list CUSTOMER-C
  permit
  ! Route cost not modified
```

### Local Preference for Exit Selection
```
route-map PREFER_PRIMARY in
  match ip address prefix-list CRITICAL
  set local-preference 200

route-map PREFER_BACKUP in
  match ip address prefix-list CRITICAL
  set local-preference 100

! Apply to neighbors
neighbor 10.0.0.1 route-map PREFER_PRIMARY in
neighbor 10.1.0.1 route-map PREFER_BACKUP in
```

### MED Optimization for Entry
```
! Advertise with MED for upstream to optimize entry
route-map SET_MED out
  match ip address prefix-list MY_ROUTES
  set metric 100  ! Preferred entry path

neighbor 10.0.0.1 route-map SET_MED out

! Receive MED from all sources
router bgp 65001
  bgp always-compare-med
  bgp deterministic-med
```

## Community-Based Filtering

### Standard Communities
```
! Define action per community
route-map COMMUNITY_POLICY in
  match community CUSTOMER_A
  set local-preference 150

route-map COMMUNITY_POLICY in
  match community CUSTOMER_B
  set local-preference 100

! Apply to all neighbors
neighbor 10.0.0.0 0.0.0.255 route-map COMMUNITY_POLICY in

! Define communities
ip community-list 1 permit 65001:100
ip community-list 2 permit 65001:200
```

### Extended Communities
```
! For VPN route filtering
route-map SET_RT out
  set extcommunity rt 65001:100
  set extcommunity cost 65001:50

! Receive and filter
route-map FILTER_RT in
  match extcommunity RT_VPN1
  permit

ip extcommunity-list 1 permit rt 65001:100
```

## Prefix Filtering Strategies

### Inbound Filtering (Receive)
```
! Prevent receipt of unwanted routes
ip prefix-list UPSTREAM_SUBNETS seq 10 permit 203.0.113.0/24
ip prefix-list UPSTREAM_SUBNETS seq 20 deny 0.0.0.0/0 le 32

neighbor 10.0.0.1 prefix-list UPSTREAM_SUBNETS in
```

### Outbound Filtering (Advertise)
```
! Advertise only authorized routes
ip prefix-list MY_ROUTES seq 10 permit 10.0.0.0/8
ip prefix-list MY_ROUTES seq 20 permit 192.168.0.0/16
ip prefix-list MY_ROUTES seq 30 deny 0.0.0.0/0 le 32

neighbor 10.0.0.1 prefix-list MY_ROUTES out
```

### Prefix-List Optimization
```
ip prefix-list CUSTOMER_A seq 10 permit 10.1.0.0/16
ip prefix-list CUSTOMER_A seq 20 permit 10.2.0.0/16
ip prefix-list CUSTOMER_A seq 30 deny 0.0.0.0/0 le 32

! Use ge/le for ranges
ip prefix-list BLOCK_SMALL seq 10 deny 0.0.0.0/0 le 24
ip prefix-list BLOCK_SMALL seq 20 permit 0.0.0.0/0 ge 25
! Blocks /24 and smaller, allows /25-/32
```

## Convergence Optimization

### Graceful Restart
```
router bgp 65001
  bgp graceful-restart
  bgp graceful-restart restart-time 300  ! Seconds
  ! Neighbors retain routes during restart
```

### Route Refresh
```
router bgp 65001
  neighbor 10.0.0.1 soft-reconfiguration inbound
  ! Stores pre-policy routes for re-evaluation
```

### BGP Route Dampening
```
router bgp 65001
  address-family ipv4
    bgp dampening 15 750 2000 60
    ! (Half-life, Reuse, Suppress, Max-suppress)
```

## Monitoring and Troubleshooting

### Key Commands
```
show ip bgp [neighbor | summary | vpnv4]
show ip bgp neighbors 10.0.0.1 [routes | advertised-routes]
show ip bgp [prefix] [longer-prefixes | community | as-path]
show ip bgp statistics
```

### Debugging
```
debug ip bgp [keepalives | updates | fsm | filters]
clear ip bgp [neighbor | *] [soft | hard]
```

## Deployment Checklist

### Planning Phase
- [ ] Define AS numbering scheme
- [ ] Plan BGP community usage
- [ ] Design traffic engineering strategy
- [ ] Document filtering policy
- [ ] Determine RR vs full mesh vs confederation

### Configuration Phase
- [ ] Configure loopback for iBGP
- [ ] Establish eBGP sessions
- [ ] Configure iBGP sessions (RR or full mesh)
- [ ] Implement prefix filtering
- [ ] Set local-preference for exit control
- [ ] Configure AS-path prepending if needed
- [ ] Implement community tagging
- [ ] Set up graceful restart

### Verification Phase
- [ ] Check neighbor status: `show ip bgp summary`
- [ ] Verify route advertisement: `show ip bgp neighbors x.x.x.x advertised-routes`
- [ ] Check received routes: `show ip bgp neighbors x.x.x.x received-routes`
- [ ] Validate filtering: `show ip bgp [prefix] | include Community`
- [ ] Test failover: Check rerouting on link failure

### Production Monitoring
- [ ] Monitor BGP convergence time
- [ ] Alert on route flapping
- [ ] Track community/attribute changes
- [ ] Monitor prefix counts (for leaks)
- [ ] Track session stability

## Common BGP Issues and Resolution

| Issue | Cause | Solution |
|-------|-------|----------|
| Neighbors not forming | AS mismatch, IP unreachable | Verify AS, routing, passwords |
| Routes not received | Filtering, no advertised | Check prefix-lists, route-maps |
| Suboptimal routing | Local-pref or MED | Adjust policy, check comparison |
| Route flapping | Unstable link, failover churn | Stabilize link, adjust timers |
| Slow convergence | Timer delays, large ASLB | Tune timers, optimize filtering |
| High CPU | Too many routes, frequent updates | Filter, summarize, use RR |

## Best Practices Summary

1. **Automation:** Use templates and configuration management
2. **Filtering:** Always filter received and sent routes
3. **Documentation:** Document policies and community meanings
4. **Monitoring:** Track all BGP metrics actively
5. **Security:** Use MD5 on all eBGP sessions
6. **Scalability:** Use RR for iBGP scaling
7. **Convergence:** Implement graceful restart, tune timers
8. **Testing:** Test all policy changes in lab first
9. **Standards:** Follow RFC 7908 (BGP Best Practices)
10. **Gradual:** Implement changes incrementally, monitor impact
