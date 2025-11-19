# Multicast Deployment Guide

## Multicast Network Design

### Addressing Strategy

```
224.0.0.0/8:    Reserved (control messages)
224.0.1.0/24:   Globally scoped addresses
232.0.0.0/8:    Source-Specific Multicast (SSM)
239.0.0.0/8:    Organization-local scope (private)
```

### Allocation Plan
```
239.0.0.0 - 239.255.255.255: Organization-local scope
├─ 239.1.0.0 - 239.1.255.255:    Video/Media
├─ 239.2.0.0 - 239.2.255.255:    Data Replication
├─ 239.3.0.0 - 239.3.255.255:    Financial Feeds
└─ 239.4.0.0 - 239.4.255.255:    VoIP/Audio
```

## IGMP Deployment

### Enable IGMP
```
ip multicast-routing  ! Global multicast enable

interface Vlan100
  ip igmp version 3    ! Version 3 supports source filtering
  ip igmp query-interval 60

! Disable on unnecessary interfaces
interface GigabitEthernet0/48
  no ip igmp
```

### IGMP Versions

**IGMPv1:** Legacy, no leave
**IGMPv2:** Standard, explicit leave
**IGMPv3:** Modern, source filtering (recommended)

```
! Default version per interface
interface Vlan100
  ip igmp version 3
```

## PIM Sparse Mode Deployment

### RP (Rendezvous Point) Design

**Single RP Architecture:**
```
                    INTERNET
                       ↓
                    ASBR (BGP)
                       ↓
                 RP (Loopback 0)  ← Elected
                    /     \
            Core Switch   Core Switch
              /   |   \      /   |   \
           Access Access Access...
```

**Multi-RP for Redundancy:**
```
              RP-1 (Active)
              RP-2 (Standby)
              RP-3 (Standby)
                   ↓
            Shared MSDP domain
```

### RP Configuration - Static
```
! Configure RP (central location)
interface Loopback 0
  ip address 192.168.255.1 255.255.255.255

! Advertise RP address to all routers
ip pim rp-address 192.168.255.1 access-list 10

! Define multicast groups
access-list 10 permit 224.0.0.0 15.255.255.255
```

### RP Configuration - Auto-RP

**Advantages:** Automatic RP election, dynamic failover

```
! RP Candidates (any router that can be RP)
interface Loopback 0
  ip pim send-rp-announce Loopback0 scope 32

! RP Mapping Agents (elect which RP to use)
ip pim send-rp-discovery Loopback0 scope 32

! View elected RP
show ip pim rp mapping
```

### RP Configuration - BSR

**Bootstrap Router (RFC 5059):**

```
! BSR Candidate
interface Loopback 0
  ip pim bsr-candidate Loopback0 0

! RP Candidate
ip pim rp-candidate Loopback0 0

! View BSR state
show ip pim bsr
```

## PIM Dense Mode (Legacy)

### Dense Mode Configuration
```
interface Vlan100
  ip pim dense-mode

interface Vlan200
  ip pim dense-mode

! View multicast tree
show ip mroute
```

**Issues with Dense Mode:**
- Initial flooding (inefficient)
- Prune-graft overhead
- Not recommended for modern networks

## Multicast Tree Optimization

### Shared Tree (RP-based)
```
Source → RP → Receivers
(*, G) MRIB entries
Controlled by RP location
```

### Source Tree (SPT)
```
Source → Receivers (Direct)
(S, G) MRIB entries
Faster after switchover
```

### SPT Switchover Configuration
```
! Switchover immediately
ip pim spt-threshold 0

! Switchover after 100 kbps
ip pim spt-threshold 100

! Disable SPT (remain on shared tree)
ip pim spt-threshold infinity
```

## Multicast Convergence

### Link Failures
```
! BFD integration
interface GigabitEthernet0/1
  ip pim bfd
  ip pim hello-interval 1
  ip pim dr-priority 100

! Fast convergence:
ip pim neighbor-timeout 90
ip pim join-prune-interval 10
```

## MSDP Configuration

### Multi-Domain Multicast
```
! Connect multiple PIM-SM domains
ip msdp peer 10.0.0.1 connect-source Loopback0

! View MSDP peers
show ip msdp peer
show ip msdp sa  ! Source-Active cache

! MSDP filtering
ip msdp sa-limit 20000  ! Max sources
ip msdp originator-id Loopback0
```

## Multicast Routing Verification

### Check Multicast Status
```
show ip multicast
show ip multicast summary
show ip pim interface
show ip pim neighbor
show ip pim rp
show ip igmp groups
show ip mroute
show ip mroute count
```

### View Specific Route
```
show ip mroute 232.1.1.1
! Shows (S,G) or (*,G) information

show ip mroute summary
! Multicast routing table summary
```

## Multicast Security

### IGMP Snooping (Switch-level)
```
ip igmp snooping
no ip igmp snooping vlan 1

! Limit flooding to subscribed ports
ip igmp snooping fast-leave
ip igmp snooping querier
```

### Multicast Access Control
```
! Deny specific multicast groups
access-list 110 deny ip any 232.0.0.0 0.0.0.255

route-map NO-MULTICAST in
  match ip address 110
  deny

router ospf 1
  distribute-list route-map NO-MULTICAST in
```

### RFC 1918 Multicast
```
! 239.192.0.0/14 for private use
! Ensure no leakage to internet
access-list 120 deny ip any 224.0.0.0 15.255.255.255
access-list 120 permit ip any any
```

## Multicast Application Considerations

### Video Streaming
```
! Separate multicast group per stream
239.1.1.1 - Video Stream 1
239.1.1.2 - Video Stream 2

! QoS for video
interface Vlan100
  mls qos trust cos
  priority-queue out

! BW allocation
bandwidth multicast 200000  ! 200 Mbps multicast capability
```

### Financial Market Data
```
! Multiple data feeds
239.2.1.1 - Equity Prices
239.2.1.2 - Options Data
239.2.1.3 - Futures

! Redundancy
source1:239.2.1.1
source2:239.2.1.1  ! Dual feeds
```

### IP TV (IPTV)
```
! Centralized RP for scalability
! SSM (232.x.x.x) for source specificity
! Separate VRF for IPTV traffic

interface Vlan199
  ip vrf forwarding IPTV
  ip address 10.99.0.1 255.255.255.0
  ip pim sparse-mode
  ip igmp version 3
```

## Monitoring and Troubleshooting

### Multicast Flow Verification
```
! Check if multicast flowing
show ip mroute 239.1.1.1 | include Outgoing

! View packet statistics
show ip mroute 239.1.1.1 count

! Monitor for issues
show ip mroute summary | include Incomplete
```

### Debug Multicast
```
debug ip pim
debug ip igmp
debug ip mroute
debug ip msdp

! View real-time operations
show ip pim neighbors detail
show ip igmp interface detail
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| No multicast received | IGMP not enabled | Enable: `ip igmp` |
| Receiver sees no source | RP unreachable | Check RP connectivity |
| Flooding everywhere | Dense mode active | Switch to sparse mode |
| Slow convergence | High join-prune interval | Reduce interval |

## Multicast Deployment Checklist

### Pre-Deployment
- [ ] Define multicast addressing scheme
- [ ] Plan RP placement (centralized)
- [ ] Design MSDP if multi-domain
- [ ] Plan source locations
- [ ] Design QoS for multicast traffic

### Configuration
- [ ] Enable multicast globally
- [ ] Configure IGMP on all access VLANs
- [ ] Configure PIM sparse mode on core
- [ ] Configure RP (static or dynamic)
- [ ] Implement filtering if needed
- [ ] Configure MSDP if multi-domain
- [ ] Set SPT thresholds

### Verification
- [ ] Verify IGMP enabled: `show ip igmp interface`
- [ ] Check RP status: `show ip pim rp`
- [ ] Verify neighbors: `show ip pim neighbor`
- [ ] Test with multicast ping: `ping 239.1.1.1`
- [ ] Monitor MROUTE: `show ip mroute`

### Monitoring
- [ ] Track active multicast groups
- [ ] Monitor RP reachability
- [ ] Alert on RP failures
- [ ] Track MSDP peering
- [ ] Monitor bandwidth usage
- [ ] Alert on group explosions

## Multicast Best Practices

1. **Sparse mode:** Default for most networks
2. **Centralized RP:** Easier to manage
3. **Auto-RP or BSR:** Dynamic RP election
4. **SSM for security:** Source-specific multicast
5. **MSDP for domains:** Connect PIM-SM domains
6. **Filtering controls:** Limit multicast scope
7. **Monitoring active:** Track groups in use
8. **QoS integration:** Reserve bandwidth for multicast
9. **Documentation:** Record multicast addresses
10. **Testing:** Lab test before deployment

## Multicast Scalability Limits

- **Groups per router:** 100,000+ (hardware dependent)
- **Sources per group:** Unlimited (memory dependent)
- **MSDP peers:** 10-20 practical limit
- **RP capacity:** 1000s of groups
- **Bandwidth:** Depends on link capacity
