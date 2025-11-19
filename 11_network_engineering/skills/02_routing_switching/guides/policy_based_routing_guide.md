# Policy-Based Routing Guide

## PBR Fundamentals

### PBR vs Standard Routing

**Standard Routing:**
- Destination-based only
- Uses longest match
- Cannot differentiate on source, port, protocol

**Policy-Based Routing:**
- Multiple criteria (source, destination, protocol, port)
- Bypass routing table lookup
- Forward based on policy, not best path

### PBR Use Cases

1. **Traffic Engineering:** Steer traffic via specific paths
2. **Cost Optimization:** Use cheaper link for low-priority traffic
3. **Traffic Segregation:** ISP A for web, ISP B for video
4. **Source-Based Routing:** Different routes per department
5. **QoS Integration:** Apply marking before forwarding

## Route-Map Syntax

### Basic Structure
```
route-map policy-name [permit | deny] sequence
  match [criteria...]
  set [action...]
```

### Match Criteria
```
match ip address [access-list | prefix-list]
match ip address access-list 101
match ip address prefix-list MY-PREFIXES

match source-address [address]
match source-address 10.0.0.0 255.0.0.0

match protocol [protocol]
match protocol tcp
match protocol udp

match length [min-length max-length]
match length 1500 1500  ! Exact 1500 bytes

match interface [interface]
match interface GigabitEthernet0/1
```

## Set Actions

### Forward to Next-Hop
```
set ip next-hop 10.0.0.254
! Must be directly reachable

set ip next-hop verify availability 10.0.0.254
! Verify next-hop is alive, fallback to routing table if not

set ip next-hop recursive 10.0.0.254
! Resolve via routing table if not directly reachable
```

### Set Outgoing Interface
```
set interface GigabitEthernet0/0
! Forward out specific interface

set interface FastEthernet0/1 FastEthernet0/2 FastEthernet0/3
! Multiple interfaces (load balancing)
```

### Set Default Next-Hop
```
set default ip next-hop 10.0.0.254
! Used if normal routing fails
```

### Mark for QoS
```
set ip dscp af31
! Set DSCP for differentiated services

set precedence critical
! Set IP precedence

set mpls experimental 7
! Set MPLS EXP bits
```

## PBR Implementation Examples

### Example 1: Source-Based Routing
```
! Traffic from Engineering dept via ISP-A
ip access-list extended ENGINEERING
  permit ip 10.10.0.0 0.0.255.255 any

route-map ENGINEER-POLICY permit 10
  match ip address ENGINEERING
  set ip next-hop 203.0.113.1

! Traffic from Sales via ISP-B
ip access-list extended SALES
  permit ip 10.20.0.0 0.0.255.255 any

route-map SALES-POLICY permit 20
  match ip address SALES
  set ip next-hop 198.51.100.1

! Apply on ingress interface
interface GigabitEthernet0/0
  ip policy route-map ENGINEER-POLICY
  ip policy route-map SALES-POLICY
```

### Example 2: Protocol-Based Routing
```
! Video traffic via high-capacity link
route-map VIDEO-POLICY permit 10
  match ip address VIDEO-TRAFFIC
  match protocol tcp
  set ip next-hop 172.16.1.1

ip access-list extended VIDEO-TRAFFIC
  permit tcp any any eq 80
  permit tcp any any eq 443
  permit tcp any any eq 8080

! Web traffic via standard link
route-map WEB-POLICY permit 20
  match ip address WEB-TRAFFIC
  set ip next-hop 172.16.2.1

ip access-list extended WEB-TRAFFIC
  permit tcp any any eq 80
  permit tcp any any eq 443

interface GigabitEthernet0/0
  ip policy route-map VIDEO-POLICY
  ip policy route-map WEB-POLICY
```

### Example 3: Load Balancing via PBR
```
! Round-robin load balancing across links
route-map LOAD-BALANCE permit 10
  match length 1000 1000
  set ip next-hop 10.0.0.1

route-map LOAD-BALANCE permit 20
  match length 1001 2000
  set ip next-hop 10.0.0.2

route-map LOAD-BALANCE permit 30
  match length 2001 3000
  set ip next-hop 10.0.0.3

! Note: Not as elegant as ECMP, but provides control
```

## PBR with Access Lists

### Extended ACLs for PBR
```
! Combine source, destination, protocol, port
ip access-list extended PBR-POLICY
  permit tcp 10.10.0.0 0.0.255.255 any eq 443
  permit udp 10.20.0.0 0.0.255.255 any eq 5060
  deny ip any any

route-map PBR-RULE permit 10
  match ip address PBR-POLICY
  set ip next-hop 192.168.1.1

interface GigabitEthernet0/1
  ip policy route-map PBR-RULE
```

### Prefix-List for Destinations
```
ip prefix-list CORPORATE seq 10 permit 10.0.0.0/8
ip prefix-list ISP-ROUTES seq 10 permit 0.0.0.0/0 le 32

route-map CORPORATE-ROUTE permit 10
  match ip address prefix-list CORPORATE
  set ip next-hop 10.0.0.254

route-map ISP-ROUTE permit 20
  match ip address prefix-list ISP-ROUTES
  set ip next-hop 10.0.0.1
```

## PBR Monitoring

### Verify PBR Configuration
```
show route-map
show route-map ENGINEER-POLICY
show access-lists

! View policy applied to interface
show ip policy
```

### PBR Statistics
```
show route-map statistics
show policy-map interface GigabitEthernet0/0

! View packets processed by PBR
show policy-map output
```

### Debugging PBR
```
debug ip policy
debug policy-map
debug route-map

! Will show which route-map entries matched
```

## PBR Verification

### Test Traffic
```
! Source from specific address
ping -S 10.10.1.1 8.8.8.8
! Should follow ENGINEER-POLICY

traceroute -S 10.10.1.1 8.8.8.8
! Verify next-hop taken

! Monitor hits on route-map
show route-map ENGINEER-POLICY
! Counter should increment after traffic
```

## PBR with VRF

### PBR in VRF Context
```
vrf definition CUSTOMER-A
  rd 65000:100
  route-target export 65000:100
  route-target import 65000:100

interface GigabitEthernet0/1
  vrf forwarding CUSTOMER-A
  ip address 10.0.0.1 255.255.255.0
  ip policy route-map CUSTOMER-A-POLICY

route-map CUSTOMER-A-POLICY permit 10
  match ip address CUSTOMER-A-TRAFFIC
  set ip next-hop vrf CUSTOMER-A 192.168.1.1
  ! Or different VRF:
  set ip next-hop vrf CUSTOMER-B 192.168.2.1
```

## PBR Performance Considerations

### CPU Impact
```
! PBR adds per-packet lookup overhead
! Monitor CPU usage after deployment
show processes | include CPU

! Use appropriate match criteria (most specific first)
```

### Optimization
```
! Order route-map entries by traffic volume (largest first)
route-map POLICY permit 10   ! 80% of traffic
  match ip address COMMON-TRAFFIC
  set ip next-hop 10.0.0.1

route-map POLICY permit 20   ! 15% of traffic
  match ip address UNCOMMON-TRAFFIC
  set ip next-hop 10.0.0.2

route-map POLICY permit 30   ! 5% of traffic
  match ip address RARE-TRAFFIC
  set ip next-hop 10.0.0.3
```

## PBR Limitations

### Issues and Workarounds

| Issue | Limitation | Solution |
|-------|-----------|----------|
| Egress PBR | Policy on ingress only | Use CBWFQ for egress |
| Recursive lookup | Can't force off network | Use verify availability |
| Loop prevention | Policy can create loops | Design carefully |
| CPU overhead | Per-packet processing | Use sparingly |
| Interoperability | Cisco-specific | Not multi-vendor |

## Best Practices

1. **Use for specific scenarios:** Don't over-engineer with PBR
2. **Order efficiently:** Most common traffic first
3. **Document policy:** Clearly explain intent
4. **Monitor performance:** Track CPU usage
5. **Test thoroughly:** Validate before production
6. **Use next-hop groups:** Multiple paths per policy
7. **Combine with QoS:** Mark traffic first, route second
8. **Avoid loops:** Ensure policy doesn't create circular routing
9. **Default to routing table:** Always provide fallback
10. **Simplify gradually:** Remove PBR when standard routing sufficient

## Deployment Checklist

### Planning
- [ ] Identify traffic requiring special handling
- [ ] Define match criteria (source, dest, protocol)
- [ ] Plan next-hop assignments
- [ ] Design fallback to routing table
- [ ] Consider CPU impact

### Configuration
- [ ] Create access-lists or prefix-lists
- [ ] Design route-map entries
- [ ] Order by traffic volume (largest first)
- [ ] Apply to ingress interfaces
- [ ] Configure verify availability if needed

### Testing
- [ ] Test each policy separately
- [ ] Verify next-hop selection
- [ ] Monitor for loops
- [ ] Test fallback behavior
- [ ] Check CPU impact

### Verification
- [ ] Verify policy applied: `show ip policy`
- [ ] Check traffic hits: `show route-map`
- [ ] Trace actual traffic: `traceroute -S`
- [ ] Monitor statistics: `debug ip policy`

### Monitoring
- [ ] Track policy hits/misses
- [ ] Monitor CPU usage
- [ ] Alert on unusual patterns
- [ ] Track interface utilization
- [ ] Verify fallback usage
