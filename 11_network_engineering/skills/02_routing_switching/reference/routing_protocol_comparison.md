# Interior vs Exterior Routing Protocol Comparison

## Protocol Characteristics Matrix

| Feature | RIPv2 | EIGRP | OSPF | BGP |
|---------|-------|-------|------|-----|
| Type | IGP | IGP | IGP | EGP |
| Algorithm | Bellman-Ford | DUAL | Dijkstra | Path Vector |
| AD (Internal) | 120 | 90 | 110 | 20 (eBGP) |
| AD (External) | - | 170 | 110 | 200 (iBGP) |
| Metric | Hop Count | Composite | Cost (BW) | AS-Path |
| Convergence | Slow (90s) | Fast (1-3s) | Fast (10-30s) | Slow (few min) |
| Scalability | Small | Large | Large | Global |
| Multicast | 224.0.0.9 | 224.0.0.10 | 224.0.0.5/6 | TCP 179 |
| Updates | Periodic | Triggered | Triggered | Triggered |

## Convergence Comparison

### Fast Convergence Protocols (IGP)
1. **EIGRP:** 1-3 seconds (Feasible successor pre-computed)
2. **OSPF:** 10-30 seconds (SPF calculation required)
3. **RIPv2:** ~90 seconds (Full routing table required)

### Slow Convergence Protocols (EGP)
1. **BGP:** Minutes to 10+ minutes (Policy filtering, dampening)

## Scalability Limits

| Protocol | Practical Limit | Reason |
|----------|-----------------|--------|
| RIPv2 | 15 hops | Hop count metric limitation |
| EIGRP | 224 hops | Hop count limitation |
| OSPF | 50-100 routers/area | SPF calculation overhead |
| BGP | Unlimited | Built for global routing |

## Metric Comparison

### Metric Type
| Protocol | Metric Type | Unit | Formula |
|----------|-------------|------|---------|
| RIPv2 | Simple count | Hops | Incremental |
| EIGRP | Composite | Various | K1×BW + K3×DELAY |
| OSPF | Cost-based | Bandwidth | 100M/bandwidth |
| BGP | AS-Path | AS count | Number of AS traversals |

## Update Characteristics

| Protocol | Update Type | Frequency | Bandwidth |
|----------|------------|-----------|-----------|
| RIPv2 | Full table | 30 seconds | High |
| EIGRP | Partial/Incremental | On change | Very low |
| OSPF | Incremental (LSA) | On change | Low |
| BGP | Incremental | On change | Low |

## Convergence Speed Factors

### EIGRP
- Feasible successors available (no query)
- DUAL computation minimal
- Topology change limited impact
- SIA (Stuck In Active) issues possible

### OSPF
- Full SPF required on topology change
- Multi-area delays (area flooding)
- Event-triggered SPF recalculation
- No precomputed alternatives

### BGP
- Policy evaluation time-consuming
- Route dampening delays announcement
- Convergence depends on timers
- Session stability critical

## Selection Criteria

| Use Case | Protocol | Reason |
|----------|----------|--------|
| Small campus | RIPv2 or EIGRP | Simple, low CPU |
| Medium campus | OSPF or EIGRP | Scalability, convergence |
| Large campus | OSPF | Standards-based, hierarchical |
| Inter-AS routing | BGP | Required, policy control |
| WAN (private) | EIGRP or OSPF | Efficiency, control |
| Vendor-agnostic | OSPF | Standards-based |
| Cisco-only | EIGRP | Efficiency, features |

## Migration Paths

### RIPv2 to EIGRP
```
Advantages: Better convergence, higher metrics
Risk: Lower AD means EIGRP wins (intentional)
Method: Gradual redistribution
```

### RIPv2 to OSPF
```
Advantages: Standards-based, scalability
Risk: Different metric system, longer convergence
Method: Redistribution with metric tuning
```

### EIGRP to OSPF
```
Advantages: Vendor-independence, hierarchical design
Risk: Slower convergence, increased CPU/memory
Method: Redistribution with area design
```

### OSPF to BGP (Inter-AS)
```
Advantages: Policy control, AS-path awareness
Risk: More complex, slower convergence
Method: iBGP + OSPF (hybrid approach)
```

## Hybrid Routing Designs

### Option 1: IGP + BGP
```
Use case: Backbone with BGP, campus with OSPF/EIGRP
Architecture:
- BGP between regions
- OSPF/EIGRP within region
- Redistribution at region boundaries
```

### Option 2: Dual IGP
```
Use case: Migration or gradual replacement
Architecture:
- Run both protocols simultaneously
- Adjust metrics to control traffic
- Gradually migrate to new protocol
```

### Option 3: IGP + MPLS-TE
```
Use case: Advanced traffic engineering
Architecture:
- IGP for base routing
- MPLS TE-tunnels for policy enforcement
- BGP for policy distribution
```

## Administrative Distance Reference

| Source | AD |
|--------|-----|
| Connected Interface | 0 |
| Static Route | 1 |
| EIGRP Summary | 5 |
| External BGP | 20 |
| EIGRP (Internal) | 90 |
| OSPF | 110 |
| IS-IS | 115 |
| RIPv2 | 120 |
| EIGRP (External) | 170 |
| Internal BGP | 200 |
| Unknown | 255 (unreachable) |

## Best Practices for Selection

1. **Standardize on one or two protocols** for management simplicity
2. **Use OSPF for multi-vendor environments** (standards-based)
3. **Use EIGRP for Cisco-only networks** (superior convergence)
4. **Use BGP at network edges** (policy control)
5. **Avoid RIPv2** (legacy, poor scalability)
6. **Consider redistribution overhead** when running multiple protocols
7. **Monitor convergence** with BFD for fast failure detection
8. **Document protocol roles** clearly for operations
9. **Test failover scenarios** before production deployment
10. **Implement graceful restart** for non-disruptive upgrades
