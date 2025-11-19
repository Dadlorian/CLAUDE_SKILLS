# BGP Route Filtering Guide

## Filtering Methods Overview

| Method | Scope | Efficiency | Flexibility |
|--------|-------|-----------|--------------|
| Access List | IP prefix | Low | Basic |
| Prefix List | IP prefix with length | Medium | Standard |
| AS-Path ACL | AS sequence | Medium | Limited |
| Community List | Community value | Low | Limited |
| Route-Map | Multiple criteria | High | Advanced |

## Prefix-List Filtering

### Basic Prefix-List Syntax
```
ip prefix-list UPSTREAM-ROUTES seq 10 permit 203.0.113.0/24
ip prefix-list UPSTREAM-ROUTES seq 20 permit 203.0.113.1/32

ip prefix-list DEFAULT seq 10 permit 0.0.0.0/0
ip prefix-list DEFAULT seq 20 deny 0.0.0.0/0 le 32

! Apply to neighbor
neighbor 10.0.0.1 prefix-list UPSTREAM-ROUTES in
```

### Prefix-List Ranges

```
! Block /24 and smaller, allow only /25-/32
ip prefix-list BLOCK-SMALL seq 10 deny 0.0.0.0/0 le 24
ip prefix-list BLOCK-SMALL seq 20 permit 0.0.0.0/0 ge 25

! Allow /8 to /16 only
ip prefix-list CORE-ONLY seq 10 permit 0.0.0.0/0 ge 8 le 16

! Allow exact /24 only
ip prefix-list EXACT-24 seq 10 permit 0.0.0.0/0 eq 24
```

### Inbound Filtering
```
! Receive only authorized routes from neighbor
router bgp 65000
  neighbor 10.0.0.1 prefix-list ALLOWED-PREFIXES in
  ! Drops any routes not matching list
```

### Outbound Filtering
```
! Advertise only authorized routes to neighbor
router bgp 65000
  neighbor 10.0.0.1 prefix-list MY-ROUTES out
  ! Prevents accidental advertisements
```

## AS-Path Access Lists

### AS-Path Patterns
```
! Deny routes from specific AS
ip as-path access-list 10 deny _65001_
ip as-path access-list 10 permit .*

! Deny routes with specific AS in middle
ip as-path access-list 20 deny _65001_65002_
ip as-path access-list 20 permit .*

! Deny customers' customers (ASes > 2 hops)
ip as-path access-list 30 deny _[0-9]+_[0-9]+_[0-9]+_
ip as-path access-list 30 permit .*
```

### AS-Path ACL Application
```
route-map FILTER-AS-PATH in
  match as-path 10
  deny

router bgp 65000
  neighbor 10.0.0.1 route-map FILTER-AS-PATH in
```

## Community-Based Filtering

### Standard Community Lists
```
! Match specific community
ip community-list 1 permit 65000:100
ip community-list 1 permit 65000:200

! Match by pattern
ip community-list expanded 2 permit "^65000:"
ip community-list expanded 2 permit "65001:"

! Apply in route-map
route-map COMMUNITY-FILTER in
  match community 1
  set local-preference 150

router bgp 65000
  neighbor 10.0.0.1 route-map COMMUNITY-FILTER in
```

### Extended Communities
```
ip extcommunity-list 1 permit rt 65000:100

route-map EC-FILTER in
  match extcommunity 1
  permit

router bgp 65000
  neighbor 10.0.0.1 route-map EC-FILTER in
```

## Route-Map Filtering

### Complex Filtering with Route-Map
```
route-map COMPLEX-FILTER in
  ! Deny specific routes
  match ip address prefix-list BLOCK-THESE
  deny

  ! Allow with manipulation
  match ip address prefix-list ALLOW-THESE
  set local-preference 150
  permit

  ! Default deny
  deny

router bgp 65000
  neighbor 10.0.0.1 route-map COMPLEX-FILTER in
```

## Inbound Filtering Strategies

### ISP Link Receiving Routes
```
! Only accept default and routes they announce
ip prefix-list ISP-ROUTES seq 10 permit 0.0.0.0/0
ip prefix-list ISP-ROUTES seq 20 permit 203.0.113.0/24
ip prefix-list ISP-ROUTES seq 30 permit 203.0.113.1/32

router bgp 65000
  neighbor 10.0.0.1 prefix-list ISP-ROUTES in
  ! Prevents route leaks from ISP
```

### Peer Link Receiving Routes
```
! Only accept customer's own prefixes
ip prefix-list CUSTOMER-PREFIXES seq 10 permit 192.0.2.0/24
ip prefix-list CUSTOMER-PREFIXES seq 20 permit 198.51.100.0/24

router bgp 65000
  neighbor 10.0.0.2 prefix-list CUSTOMER-PREFIXES in
  ! Prevent customer from announcing other routes
```

### Upstream Transit Provider
```
! Accept everything (default deny last)
ip prefix-list ANY seq 10 permit 0.0.0.0/0 le 32

router bgp 65000
  neighbor 10.0.0.3 prefix-list ANY in
```

## Outbound Filtering Strategies

### Advertisement to Upstream ISP
```
! Advertise only your own routes
ip prefix-list OUR-ROUTES seq 10 permit 10.0.0.0/8
ip prefix-list OUR-ROUTES seq 20 permit 192.168.0.0/16

router bgp 65000
  neighbor 10.0.0.1 prefix-list OUR-ROUTES out
  ! Prevent leaking routes from other sources
```

### Advertisement to Customers
```
! Advertise your routes + transit routes
route-map CUSTOMER-ADVERTISEMENT out
  match ip address prefix-list OUR-ROUTES
  permit

  match ip address prefix-list TRANSIT-ROUTES
  permit

router bgp 65000
  neighbor 10.0.0.2 route-map CUSTOMER-ADVERTISEMENT out
```

### Advertisement to Peers
```
! Advertise only your own, not customer routes
route-map PEER-ADVERTISEMENT out
  match ip address prefix-list OUR-ROUTES
  permit

  ! Explicit deny of customer routes
  match ip address prefix-list CUSTOMER-ROUTES
  deny

router bgp 65000
  neighbor 10.0.0.3 route-map PEER-ADVERTISEMENT out
```

## Multi-Criteria Filtering

### Combine Prefix + Community
```
route-map COMBINED-FILTER in
  ! High priority routes with specific community
  match ip address prefix-list CRITICAL
  match community 100
  set local-preference 200
  permit

  ! Other routes with different community
  match ip address prefix-list STANDARD
  match community 200
  set local-preference 100
  permit

  ! Default deny
  deny
```

### Combine AS-Path + Prefix
```
route-map AS-PREFIX-FILTER in
  match as-path 10        ! Specific AS
  match ip address prefix-list EXPECTED-ROUTES
  set local-preference 150
  permit

  ! Unexpected routes from that AS blocked
  deny

router bgp 65000
  neighbor 10.0.0.1 route-map AS-PREFIX-FILTER in
```

## Filtering for Loop Prevention

### Prevent Transit Loop
```
! Don't accept routes if our ASN in path
ip as-path access-list 50 deny _65000_
ip as-path access-list 50 permit .*

route-map NO-LOOP in
  match as-path 50
  deny

! Also prevent customer advertising our routes
ip prefix-list NOT-OUR-ROUTES seq 10 deny 10.0.0.0/8
ip prefix-list NOT-OUR-ROUTES seq 20 permit 0.0.0.0/0 le 32
```

## Filtering Best Practices

### Inbound Filtering Rules
```
1. Accept only expected routes (whitelist)
2. Set metrics/preference appropriately
3. Reject any others

Example:
! Step 1: Define allowed
ip prefix-list ALLOWED seq 10 permit 203.0.113.0/24

! Step 2: Metric manipulation
route-map INBOUND in
  match ip address prefix-list ALLOWED
  set local-preference 100
  permit

! Step 3: Implicit deny (anything not matched)
```

### Outbound Filtering Rules
```
1. Advertise only what you own + agreed routes
2. Never advertise customer's routes to other customers
3. Filter unintended leaks

Example:
ip prefix-list OUR-ROUTES seq 10 permit 10.0.0.0/8
ip prefix-list CUSTOMER-A seq 10 permit 192.0.2.0/24

route-map TO-ISP out
  match ip address prefix-list OUR-ROUTES
  permit

route-map TO-CUSTOMER-A out
  match ip address prefix-list CUSTOMER-A
  permit
  match ip address prefix-list OUR-ROUTES
  permit
```

## Monitoring Filtered Routes

### View Advertised Routes
```
show ip bgp neighbors 10.0.0.1 advertised-routes
! Shows routes we advertise to neighbor

show ip bgp neighbors 10.0.0.1 received-routes
! Shows routes we receive from neighbor (before filtering)

show ip bgp neighbors 10.0.0.1 routes
! Shows routes from neighbor (after filtering)
```

### Verify Filtering Working
```
show ip prefix-list summary
show ip prefix-list detail

! Route-map hit counters
show route-map
! Increments show filtering is working

show access-lists
! For AS-path and community lists
```

## Troubleshooting Filters

### Routes Not Received
```
1. Check prefix-list:
   show ip prefix-list UPSTREAM-ROUTES

2. Check route-map:
   show route-map IN-FILTER

3. Check neighbor configuration:
   show bgp neighbors 10.0.0.1 | include prefix-list

4. Check if routes exist at source:
   ping <route destination>
   traceroute <route destination>
```

### Routes Unexpectedly Filtered
```
1. Verify matching criteria:
   ip prefix-list <name> hit <prefix>
   ! Shows if matches

2. Check for typos:
   show ip prefix-list detail

3. Verify permit/deny logic:
   show route-map <name>
```

## Deployment Checklist

### Planning
- [ ] Document what routes should be filtered
- [ ] Define whitelist (allowed routes)
- [ ] Identify potential security issues
- [ ] Plan for route growth

### Configuration
- [ ] Create prefix-lists for each neighbor type
- [ ] Create AS-path ACLs if filtering AS-path
- [ ] Configure route-maps with metrics
- [ ] Apply filters to neighbors (in/out)
- [ ] Test in lab first

### Verification
- [ ] Verify expected routes received: `show ip bgp`
- [ ] Check advertised routes: `show ip bgp advertised-routes`
- [ ] Monitor route counts
- [ ] Verify no unintended filtering

### Monitoring
- [ ] Track route count trends
- [ ] Alert on unexpected route loss
- [ ] Monitor filter hit counters
- [ ] Track prefix-list changes

## Best Practices Summary

1. **Whitelist approach:** Define what's allowed, deny rest
2. **Prefix-lists:** More efficient than ACLs
3. **Document intent:** Why each filter exists
4. **Test changes:** Lab test before production
5. **Monitor effectiveness:** Verify filters working
6. **Periodic review:** Ensure filters still needed
7. **Layered security:** Multiple filters at different points
8. **Route logging:** Track changes for audit
9. **Default deny:** Always end filters with deny
10. **Simplify gradually:** Remove filters as systems mature
