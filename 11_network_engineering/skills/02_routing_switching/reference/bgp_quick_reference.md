# BGP Quick Reference Guide

## Protocol Basics

- **Protocol Type:** Exterior Gateway Protocol (EGP), Path-Vector
- **TCP Port:** 179 (Unicast TCP connection)
- **Administrative Distance:** eBGP=20, iBGP=200
- **Process ID:** BGP AS number (65535 max, private: 64512-65534)
- **Updates:** Incremental (triggered + periodic refresh every 30 minutes)
- **Keepalive Interval:** 60 seconds
- **Hold Time:** 180 seconds (default)
- **Best Path Algorithm:** Weight > Local Pref > AS-Path > Origin > MED > Type > OSPF metric

## BGP Neighbor States

| State | Meaning |
|-------|---------|
| Idle | Waiting for start event |
| Connect | Attempting TCP connection |
| Active | Waiting for TCP connection to complete |
| OpenSent | Open message sent |
| OpenConfirm | Open confirmed, waiting for keepalive |
| Established | Neighbor relationship active, routes exchanged |

## BGP Message Types

| Type | Purpose |
|------|---------|
| Open | Establish peer relationship |
| Update | Advertise/withdraw routes |
| Notification | Error condition |
| Keepalive | Confirm neighbor connectivity |

## BGP Attributes (Path Attributes)

### Well-Known Mandatory
- **Origin:** IGP (0), EGP (1), Incomplete (2) - Source of route
- **AS_Path:** Sequence of ASes the route traversed
- **Next_Hop:** Next hop IP address toward destination

### Well-Known Discretionary
- **Local_Preference:** Preference for exit point from AS (default 100)
- **Atomic_Aggregate:** Indicates aggregation (suppress subpaths)

### Optional Transitive
- **Aggregator:** Origin and AS of aggregation
- **Communities:** Tag for route grouping (0:0 to 4294967295)
- **Originator_ID:** iBGP route-reflector originator
- **Cluster_List:** Route reflector cluster path

### Optional Non-Transitive
- **Multi_Exit_Disc (MED):** Metric preference for entry point (lower=preferred)
- **Extended Communities:** Enhanced tagging (RT, ST formats)
- **Connector:** BGP-LS-SPF connector attribute

## Path Selection Criteria (Order)

1. **Weight** (0-65535, higher preferred, Cisco-only)
2. **Local Preference** (0-4294967295, higher preferred, iBGP only)
3. **Locally Originated** (network/aggregate vs. received)
4. **AS-Path Length** (shorter preferred)
5. **Origin Type** (IGP > EGP > Incomplete)
6. **MED** (lower preferred, comparing equal-AS routes)
7. **eBGP vs iBGP** (eBGP preferred)
8. **IGP Metric to Next-Hop** (lower preferred)
9. **Route-Reflector Cluster List** (shorter preferred)
10. **Neighbor Router ID** (higher preferred)
11. **Neighbor IP Address** (higher preferred)

## Route Types

| Type | Origination | Default Local_Pref |
|------|-------------|-------------------|
| Network (IGP) | network command | 200 (Cisco) |
| Aggregate | aggregate-address | varies |
| Redistributed | redistribute | 200 (Cisco) |
| Received iBGP | iBGP peer | 100 |
| Received eBGP | eBGP peer | 100 |

## BGP Timers

| Timer | Default | Minimum |
|-------|---------|---------|
| Keepalive | 60s | 0s (disabled if 0) |
| Hold Time | 180s | 3s |
| Connect Retry | 120s | 1s |
| MinRouteAdv | 30s for routes, 0s for withdrawals | N/A |

## BGP Communities

### Standard Community (2-byte AS + 2-byte value)
- Format: `AS:Value` (e.g., 65000:100)
- Well-known: no-export (65535:65281), no-advertise (65535:65282), local-as (65535:65283)

### Extended Community (8-byte total)
- Format: `Type:Value` (e.g., rt 65000:100)
- Types: RT (Route Target), ST (Site Target), SoO (Site of Origin)

## BGP Route Filtering Methods

| Method | Scope | Matches |
|--------|-------|---------|
| access-list | prefix | exact IP prefix |
| prefix-list | prefix | prefix with length range |
| route-map | prefix + attributes | multiple criteria |
| AS-path ACL | AS-path | AS sequences/patterns |
| Community list | community | exact/standard/expanded |
| Extended community list | ext-community | extended community values |

## BGP Neighbor Types

### eBGP (External BGP)
- Different AS numbers
- Default: direct connection required (TTL=1)
- Admin distance: 20
- No next-hop-self required to neighbors in different AS

### iBGP (Internal BGP)
- Same AS number
- Full mesh or route reflector/confederation required
- Admin distance: 200
- Advertised routes use same next-hop
- Next-hop-self applied toward remote AS networks

## Route Reflector Design

- **RR (Route Reflector):** Re-advertises iBGP routes
- **Clients:** Routers served by RR
- **Peers:** Routers in same cluster as RR

**Cluster List:** Prevents loop, resets when route exits cluster

## BGP Confederation

- Divides AS into sub-ASes (confed sub-as)
- Internal confederation eBGP between sub-ASes
- All sub-ASes appear as single AS to external BGP
- Reduce iBGP mesh requirements
- Parameter format: `bgp confederation identifier 65000` + `bgp confederation peers`

## Best Practices

1. Always configure keepalive/hold timers appropriately for stability
2. Use local-preference in iBGP for traffic engineering
3. Use MED for eBGP entry point optimization
4. Implement communities for scalable policy
5. Filter route advertisements at network boundaries
6. Use prefix-lists over access-lists for efficiency
7. Document AS-path prepending rationale
8. Implement BGP graceful restart for non-disruptive upgrades
9. Monitor convergence and stability metrics
10. Use route-reflectors (not full mesh) for iBGP scalability
