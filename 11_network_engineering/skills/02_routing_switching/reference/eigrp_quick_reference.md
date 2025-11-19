# EIGRP Quick Reference Guide

## Protocol Basics

- **Protocol Type:** Interior Gateway Protocol (IGP), Advanced Distance Vector
- **Protocol Number:** 88 (IP)
- **Administrative Distance:** Internal 90, Summary 91, External 170
- **Multicast Address:** 224.0.0.10
- **Update Type:** Partial (incremental) and triggered updates
- **Metric:** Composite (bandwidth, delay, reliability, load, MTU)
- **Default K-values:** K1=1, K2=0, K3=1, K4=0, K5=0
- **Process ID:** 1-65535 (locally significant)

## EIGRP Metric Calculation

```
Metric = K1×BW + (K2×BW)/(256-LOAD) + K3×DELAY + K5/(K4+RELIABILITY)

Default (K1=1, K2=0, K3=1, K4=0, K5=0):
Metric = BW + DELAY

Where:
BW = 10^7 / minimum bandwidth (kbps) in path
DELAY = sum of delays / 10 (microseconds)

Examples:
- 100Mbps + 1000us = 10,000,000/100,000 + 100 = 100 + 100 = 200
- 1Gbps + 100us = 10,000,000/1,000,000 + 10 = 10 + 10 = 20
```

## EIGRP Timers

| Timer | Default (Broadcast) | Default (Point-to-Point) | Multiplier |
|-------|---------------------|--------------------------|-----------|
| Hello | 5 seconds | 5 seconds | - |
| Hold | 15 seconds | 15 seconds | - |
| Retransmit | 50 milliseconds | 50 milliseconds | - |

### Alternate Delay Network Timers
- **Hello:** 60 seconds
- **Hold:** 180 seconds
- Configured via `timers active-time` and `timers hello-interval`

## EIGRP Packet Types

| Type | Purpose |
|------|---------|
| Hello | Neighbor discovery and keepalive |
| Update | Route information and changes |
| Query | Successor lost, asking for alternative |
| Reply | Response to query |
| ACK | Acknowledges reliable packet receipt |

## Route States

| State | Meaning | Routes Advertised |
|-------|---------|-------------------|
| Passive | Stable, has successor | Yes |
| Active | No successor, querying neighbors | No (SIA after 3 minutes) |
| SIA (Stuck In Active) | Query timeout after 3 minutes | Terminates neighbor adjacency |

## Key EIGRP Concepts

### Feasible Distance (FD)
- Advertised Distance (AD) from neighbor + metric to neighbor
- Best distance to reach destination

### Advertised Distance (AD)
- Metric advertised by neighbor (distance from neighbor to destination)
- Used for feasibility check

### Successor
- Neighbor with lowest FD to destination
- Primary route used for traffic

### Feasible Successor (FS)
- Neighbor where AD < current FD (loop prevention)
- Available for fast reroute without query

**Feasibility Rule:** AD < FD ensures loop-free path

## EIGRP Configurations

### Named Mode vs Classic Mode
- **Named Mode:** Hierarchical, per-address-family, recommended
- **Classic Mode:** Legacy, single configuration, being phased out

## Summary Metrics

| Metric Component | Default Path Value |
|------------------|-------------------|
| Bandwidth | Minimum along path |
| Delay | Sum of all delays |
| Reliability | Minimum along path |
| Load | Maximum along path |
| MTU | Minimum along path (informational) |
| Hop Count | Number of routers + 1 |

## EIGRP for IPv6

- **Process Number:** 1-65535 (separate from IPv4)
- **Address Family:** ipv6 alongside ipv4
- **Metric:** Same calculation as IPv4
- **Link-local:** Interfaces configure on link-local addresses
- **Multicast:** FF02::A (IPv6 version of 224.0.0.10)

## EIGRP Authentication

### MD5 Authentication
```
key chain name
  key 1
    key-string password

interface GigabitEthernet0/0
  ip authentication key-chain eigrp AS-number name
  ip authentication mode eigrp AS-number md5
```

### SHA Authentication
```
key chain name
  key 1
    key-string password
    cryptographic-algorithm hmac-sha-256

interface GigabitEthernet0/0
  ip authentication key-chain eigrp AS-number name
  ip authentication mode eigrp AS-number hmac-sha-256
```

## EIGRP Stub Features

| Stub Type | Advertises | Use Case |
|-----------|------------|----------|
| Connected | Connected networks | Hub/spoke |
| Redistributed | Redistributed networks | Branch office |
| Summary | Summarized routes | Branch office |
| Static | Static routes | Branch office |
| Receive-only | Nothing (queries only) | Spoke-only |

## Unequal Cost Load Balancing

```
variance multiplier (1-128)

Uses: variance × metric value
Only use feasible successors
```

## Auto-summarization

- **Enabled by default in Classic mode** (IPv4)
- **Disabled by default in Named mode**
- **Effect:** Summarizes at classful boundary (10.0.0.0/8, 172.16.0.0/12)
- **Disable:** `no auto-summary`

## Filtering

| Method | Scope |
|--------|-------|
| distribute-list in | Inbound EIGRP routes |
| distribute-list out | Outbound EIGRP advertisements |
| prefix-list | Specific prefix matching |
| route-map | Prefix + metric manipulation |
| offset-list | Metric adjustment (in/out) |

## Best Practices

1. Use named mode for new deployments
2. Adjust K-values only when needed (defaults optimal)
3. Use feasible successors for fast failover
4. Implement MD5/SHA authentication
5. Configure appropriate hello/hold timers for network type
6. Monitor SIA (Stuck In Active) conditions
7. Use variance cautiously (unequal load balancing)
8. Implement summarization at area boundaries
9. Use distribute-lists to filter unnecessary routes
10. Tune minimum bandwidth calculation for WAN links
