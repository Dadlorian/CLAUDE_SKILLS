# Multicast Routing Quick Reference

## Multicast Address Space

### IPv4 Multicast
- **Range:** 224.0.0.0 to 239.255.255.255 (Class D)
- **Scope:**
  - **224.0.0.0/24:** Local network control block (never routed)
  - **224.0.1.0 to 238.255.255.255:** Globally scoped
  - **239.0.0.0/8:** Limited scope (private use)

### IPv6 Multicast
- **Prefix:** ff00::/8
- **Format:** ff[scope][group]
- **Scope:** 0x1 (node), 0x2 (link), 0x5 (site), 0x8 (org), 0xe (global)

## IGMP (Internet Group Management Protocol)

### IGMP Versions

| Version | Purpose | Timers | Efficiency |
|---------|---------|--------|-----------|
| IGMPv1 | Basic group membership | No leave | Legacy |
| IGMPv2 | Group membership + leave | Leave timers | Standard |
| IGMPv3 | Source filtering (S,G) | Multiple timers | Advanced |

### IGMP Configuration
```
! Enable IGMP globally
ip multicast-routing

! Disable on interface (explicit)
interface GigabitEthernet0/1
  no ip igmp

! Set IGMP version
interface GigabitEthernet0/1
  ip igmp version 3

! Set query interval
interface GigabitEthernet0/1
  ip igmp query-interval 60

! Set query response interval
interface GigabitEthernet0/1
  ip igmp query-max-response-time 10

! View IGMP status
show ip igmp interface
show ip igmp groups
```

## PIM (Protocol Independent Multicast)

### PIM Modes

#### PIM Sparse Mode (PIM-SM)
- **Model:** Rendezvous Point (RP) based
- **Default:** Explicit join-based
- **Efficiency:** Good for sparse, long-distance
- **Trees:** Shared trees, source trees (SPT switchover)

#### PIM Dense Mode (PIM-DM)
- **Model:** Flood and prune
- **Default:** Flood to all, prune non-receivers
- **Efficiency:** Good for dense, low latency
- **Trees:** Source trees only
- **Note:** RFC 3973 experimental, rarely used

### PIM Configuration
```
! Enable PIM sparse mode
ip multicast-routing
interface GigabitEthernet0/1
  ip pim sparse-mode

! Enable PIM dense mode (legacy)
interface GigabitEthernet0/1
  ip pim dense-mode

! Enable on loopback (RP interface)
interface Loopback 0
  ip pim sparse-mode
```

### Rendezvous Point (RP)

#### Static RP Configuration
```
! Configure RP address globally
ip pim rp-address 10.0.0.100 access-list 10

! Define multicast groups
access-list 10 permit 224.0.0.0 15.255.255.255

! View RP
show ip pim rp
```

#### Auto-RP (Dynamic RP Election)
```
! Configure RP candidate
interface Loopback 0
  ip pim send-rp-announce Loopback0 scope 32

! Configure RP mapping agent
ip pim send-rp-discovery Loopback0 scope 32

! View auto-RP
show ip pim rp mapping
show ip pim rp auto-rp
```

#### BSR (Bootstrap Router)
```
! Configure BSR candidate
ip pim bsr-candidate Loopback0 0

! Configure RP candidate
ip pim rp-candidate Loopback0 0

! View BSR
show ip pim bsr
```

### PIM Timers

| Timer | Default | Purpose |
|-------|---------|---------|
| Hello | 30 seconds | Neighbor discovery |
| Join-Prune | 60 seconds | Group membership |
| Assert | 180 seconds | RPF interface selection |
| Keep-alive | 210 seconds (3 × J/P) | Source activity |

## Multicast Routing Trees

### Shared Tree (RP-based)
```
Source → RP ← Receiver
(*, G) MRIB entries
Controlled by RP
```

### Source Tree (SPT)
```
Source → Receiver (Direct)
(S, G) MRIB entries
Used after SPT switchover
```

### SPT Switchover
```
! Threshold for switching to SPT
ip pim spt-threshold [rate | infinity] [group-list]

! Disable SPT switchover
ip pim spt-threshold infinity

! Enable SPT for all traffic
ip pim spt-threshold 0
```

## Multicast Routing Information Base (MRIB)

```
! View MRIB entries
show ip mroute
show ip mroute summary
show ip mroute [source | group]
show ip mroute count

! View incoming interface
show ip mroute [source] [group] | include RPF
```

### MRIB Entry Fields
- **(S,G):** (Source, Group) pair
- **RPF Interface:** Reverse Path Forwarding interface
- **Outgoing Interfaces:** (OIL) Interfaces sending multicast

## Multicast Reverse Path Forwarding (RPF)

```
! RPF check based on routing table
ip multicast rpf [lookup | lookup vrf | policy-based]

! View RPF information
show ip mroute [source] [group] | include RPF
```

## MSDP (Multicast Source Discovery Protocol)

- **Purpose:** Discover sources across PIM-SM domains
- **Use:** Connect multiple RP domains
- **Port:** TCP 639

```
! Configure MSDP peer
ip msdp peer 10.0.0.1 connect-source Loopback0

! View MSDP peers
show ip msdp peer
show ip msdp sa

! MSDP timer
ip msdp timer keepalive 30 connect-retry 30
```

## Multicast VRF

```
! Enable multicast in VRF
ip multicast-routing vrf CUSTOMER

! PIM sparse mode in VRF
interface GigabitEthernet0/1
  ip vrf forwarding CUSTOMER
  ip pim sparse-mode
```

## Multicast Filtering

```
! Deny specific multicast source
access-list 10 permit 224.0.0.0 15.255.255.255

! Apply to incoming PIM joins
ip pim accept-rp 10.0.0.100 access-list 10

! Scope limiting
ip multicast boundary access-list 20
access-list 20 deny 224.0.0.0 15.255.255.255
```

## Multicast Troubleshooting

```
! View multicast status
show ip multicast
show ip multicast summary

! View PIM neighbors
show ip pim neighbor
show ip pim interface

! View multicast routes
show ip mroute [source] [group]
show ip mroute [source] [group] count

! View RP information
show ip pim rp
show ip pim rp mapping

! Enable debugging
debug ip pim
debug ip igmp
debug ip mroute
debug ip msdp
```

## Multicast Application Support

### Well-Known Multicast Groups

| Address | Purpose |
|---------|---------|
| 224.0.0.1 | All hosts on local network |
| 224.0.0.2 | All routers on local network |
| 224.0.0.5 | OSPF routers |
| 224.0.0.6 | OSPF designated routers |
| 224.0.0.10 | EIGRP routers |
| 239.x.x.x | Locally scoped (private) |

## Multicast Best Practices

1. **Design:**
   - Choose RP redundancy strategy (multiple RPs or BSR)
   - Plan multicast address allocation
   - Document RP placement

2. **Configuration:**
   - Enable IGMP on all access networks
   - Configure PIM on all intermediate routers
   - Set appropriate scope limits

3. **Optimization:**
   - Tune SPT switchover thresholds
   - Optimize RP placement for latency
   - Monitor MSDP if multi-domain

4. **Monitoring:**
   - Track multicast groups in use
   - Monitor source activity
   - Alert on routing changes

5. **Security:**
   - Filter unauthorized sources
   - Limit scope with boundaries
   - Monitor for multicast flooding

6. **IPv6 Multicast:**
   - Use ff02::/8 for link-local
   - Plan ff05::/8 for site-local (if needed)
   - Document group allocation
