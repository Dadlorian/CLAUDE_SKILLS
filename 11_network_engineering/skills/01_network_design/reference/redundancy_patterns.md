# Network Redundancy Patterns

## Introduction
Redundancy is critical for network availability. This reference covers proven patterns for implementing fault-tolerant network designs across different architectural tiers.

## Availability Definitions

### Downtime Targets

```
Availability Tier | Downtime/Year | Minutes/Year | Nines | Technology Cost |
------------------|---------------|--------------|-------|-----------------|
99.00%           | 87.6 hours    | 5,256        | 2     | Low            |
99.90%           | 8.76 hours    | 526          | 3     | Medium         |
99.99%           | 52.6 minutes  | 52.6         | 4     | High           |
99.999%          | 5.26 minutes  | 5.26         | 5     | Very High      |

Common Targets:
- Small business: 99%
- Medium business: 99.9%
- Enterprise: 99.99%
- Mission-critical: 99.999%
```

## Link Redundancy

### Dual Uplink Design

```
Access Switch with Dual Uplinks:

┌──────────────────────────────────────────┐
│           Distribution Switch 1           │
│  (Core Link A - Primary)                  │
│  Port Gi0/0/47 (100G)                     │
└──────────────────────────────────────────┘
    │
    │ (Primary path, active)
    │
┌───┴───────────────────────────────────────┐
│         Access Switch-1                    │
│  Port Gi0/0/47 (primary)                   │
│  Port Gi0/0/48 (backup)                    │
│                                           │
│  Ports Gi0/0/1-46: End devices            │
└────────┬──────────────────────────────────┘
         │
         │ (Backup path)
         │
    ┌────┴──────────────────────────────────┐
    │  Distribution Switch 2                  │
    │  (Backup Link)                          │
    │  Port Gi0/0/47 (100G)                   │
    └─────────────────────────────────────────┘

Configuration:
- Port Gi0/0/47: Active (VLAN 1-4094)
- Port Gi0/0/48: Standby (blocked by STP)
- Failover time: 30-50 seconds (STP)
- Failover latency: Acceptable for data traffic
```

### Link Aggregation (EtherChannel)

```
Port Channel for Load Distribution:

┌──────────────────────────────────────┐
│    Distribution Layer Switch          │
│  Po1: EtherChannel to Access-1        │
│    Gi0/0/1: Member 1 (100% capacity)  │
│    Gi0/0/2: Member 2 (100% capacity)  │
│    Gi0/0/3: Member 3 (100% capacity)  │
│                                       │
│  Total bandwidth: 300 Gbps            │
│  Single link failure: Capacity = 200G │
└──────────────────────────────────────┘
         │
         │ EtherChannel (active-active load balancing)
         │
┌────────┴───────────────────────────────┐
│      Access Switch-1                    │
│  Po1: EtherChannel to Distribution     │
│    Gi0/0/1: Member 1                  │
│    Gi0/0/2: Member 2                  │
│    Gi0/0/3: Member 3                  │
└─────────────────────────────────────────┘

Load Balancing Algorithm (per-flow):
  Hash = (Source IP + Dest IP) mod (3 members)
  Flow 1: 10.1.1.5 → 10.10.1.10 = Hash to Gi0/0/1
  Flow 2: 10.1.1.6 → 10.10.1.10 = Hash to Gi0/0/2
  Flow 3: 10.1.1.7 → 10.10.1.10 = Hash to Gi0/0/3

Benefits:
- Bandwidth aggregation
- Active-active redundancy
- Fast failover (<50ms)
- No protocol overhead
```

## Core Layer Redundancy

### Full Mesh Core Architecture

```
Core Layer with Full Mesh Topology:

        ┌─────────────────────────────────────┐
        │                                     │
    ┌───┴────┐      ┌──────────┐      ┌─────┴──┐
    │ Core-1 │------│ Core-2   │------│ Core-3 │
    │ ASN    │  100G│ ASN 65001│ 100G │ ASN    │
    │ 65001  │------│          │------│ 65001  │
    └───┬────┘      └────┬─────┘      └─────┬──┘
        │                │                   │
        │ BGP            │ BGP              │ BGP
        │                │                   │
    ┌───┴────────┬───────┴───────┬───────────┴──┐
    │ Dist-1    │ Dist-2        │ Dist-3       │
    │ ASN 65002 │ ASN 65002     │ ASN 65002    │
    └────────────┴───────────────┴──────────────┘

Bandwidth per core pair: 100-400 Gbps
Failure scenarios:
- Single core failure: 66% capacity maintained
- Single link failure: 50% capacity per direction
- All links utilized (ECMP routing)
```

### Redundant Core Design (N+1)

```
N+1 Redundancy Model:

┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ Active  │  │ Active  │  │ Active  │  │ Standby │
│ Core-1  │  │ Core-2  │  │ Core-3  │  │ Core-4  │
└────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘
     │           │            │            │
     └───────────┴────────────┴────────────┘
           (Full mesh internally)

Benefits:
- Any single core can fail
- Network continues at N capacity
- Upgrade/maintenance without impact
- Cost: +25% additional equipment
```

## Distribution Layer Redundancy

### Active-Passive with VRRP

```
Virtual Router Redundancy Protocol (VRRP):

         VLAN 10 Traffic
               │
               ↓
      ┌─────────────────┐
      │ Virtual Gateway │
      │  10.10.10.1     │
      │  (Priority 150) │
      └────────┬────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───┴────────┐     ┌──────┴──┐
│   Dist-A   │     │  Dist-B │
│ (Master)   │     │(Backup) │
│   Pri: 150 │     │Pri: 100 │
│ IP: *.*.*.2│     │IP: *.*.*.3
└────┬───────┘     └──────┬──┘
     │                    │
     └────────┬───────────┘
              │
         ┌────┴────────────────┐
         │  Access Switches    │
         │  (Forward to *.*.*.1)
         └─────────────────────┘

Failover mechanism:
1. Master sends VRRP advertisements every 1 second
2. Backup receives advertisements, stays passive
3. Master fails: No advertisements received
4. Backup detects failure (3 x 1 second = 3 seconds max)
5. Backup becomes active
6. Backup ARP for Virtual IP, takes ownership
7. Traffic reroutes through new master (< 5 seconds)

Multiple VRRP instances (per VLAN):
- VLAN 10: Master on Dist-A, Backup on Dist-B
- VLAN 20: Master on Dist-B, Backup on Dist-A
- VLAN 30: Master on Dist-A, Backup on Dist-B
(Load balanced across both distribution switches)
```

### HSRP (Hot Standby Router Protocol)

```
Similar to VRRP but Cisco-proprietary:

┌──────────────────────────────────────────┐
│  Standby Group: 10 (VLAN 10 Gateway)     │
│  Virtual IP: 10.10.10.1                  │
│  Priority range: 0-255 (default 100)     │
└──────────────────────────────────────────┘

         ┌─────────────────┐
         │  Active Router  │
         │  Priority 150   │
         │  Dist-A IP: .2  │
         └────────┬────────┘
                  │
         ┌────────┴────────┐
         │  Standby Router │
         │  Priority 100   │
         │  Dist-B IP: .3  │
         └─────────────────┘

Preemption configuration:
  - Enabled: Higher priority router takes over immediately
  - Disabled: Active stays active even if higher priority available
  - Recommended: Disable for stability, enable for controlled failover

Convergence time: 3-6 seconds
State transitions:
  Disabled → Initial → Listen → Speak → Standby/Active
```

## WAN Redundancy

### Dual Internet Connection Design

```
Redundant Internet Architecture:

        ┌─────────────────────────────┐
        │    Enterprise Network       │
        │    Core Routers             │
        └────────┬────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
    ┌────┴─────┐    ┌────┴─────┐
    │ Router-A │    │ Router-B  │
    │ (Primary)│    │ (Backup)  │
    └────┬─────┘    └────┬──────┘
         │               │
         │               │
    ┌────┴────┐     ┌────┴─────┐
    │ISP A    │     │ ISP B     │
    │BGP AS   │     │ BGP AS    │
    │65100    │     │ 65101     │
    └─────────┘     └───────────┘

BGP Configuration (Router-A primary):
  - ISP A: Primary path (lower local-preference)
  - ISP B: Backup path (higher local-preference)
  - Failover: Automatic on ISP A link failure
  - Convergence: 3-30 seconds (depends on BGP timers)

Traffic distribution:
- Normal: 90% ISP-A, 10% ISP-B (load balancing)
- ISP-A down: 100% ISP-B
- ISP-A recovery: 90% ISP-A, 10% ISP-B (converge back)
```

### Data Center to Data Center Redundancy

```
Active-Active Data Center Design:

  ┌─────────────────────┐         ┌──────────────────────┐
  │   Data Center A     │         │   Data Center B      │
  │                     │         │                      │
  │  Core Switches      │         │  Core Switches       │
  │  ASN: 65001         │         │  ASN: 65001          │
  │  IP: 10.100.0.0/16  │         │  IP: 10.101.0.0/16   │
  │                     │         │                      │
  │  ┌─────────────┐    │         │  ┌──────────────┐    │
  │  │ Primary DB  │    │         │  │  Secondary   │    │
  │  │  Replication─────────────────→ DB            │    │
  │  └─────────────┘    │         │  └──────────────┘    │
  └─────────┬───────────┘         └──────────┬───────────┘
            │                               │
            │   100G Dark Fiber             │
            │   MPLS LSP Primary            │
            │   MPLS LSP Backup             │
            │                               │
            ├───────────────────────────────┤
            │   IPsec Tunnel (Backup)       │
            └───────────────────────────────┘

Failover scenarios:
1. Primary link down: Traffic switches to backup LSP
   - Convergence: <50ms (hardware based)
   - Synchronization: Real-time replication

2. Data Center A down: All traffic to Data Center B
   - Convergence: 1-2 seconds (BGP)
   - Application: Connection reestablishment required
   - Data: Replicated (zero loss)

3. Partial connectivity: Split-brain risk
   - Mitigation: Cluster heartbeat monitoring
   - Consensus: Based on quorum rules
```

## Redundancy Patterns Summary

| Pattern | Convergence | Cost | Complexity | Use Case |
|---------|-------------|------|-----------|----------|
| Dual Uplink + STP | 30-50s | Low | Low | Basic campus |
| EtherChannel | <50ms | Low | Low | High throughput |
| HSRP/VRRP | 3-6s | Low | Medium | Gateway redundancy |
| Full Mesh | <50ms | High | High | Core layer |
| N+1 Core | <50ms | High | High | Enterprise core |
| Dual ISP | 3-30s | Medium | Medium | Internet connectivity |
| DC-DC Active-Active | <50ms | High | High | Mission-critical |

## Redundancy Calculation

### Availability with Redundancy

```
Single device availability: 99.9%
Downtime per year: 8.76 hours

With passive redundancy (N+1):
Availability = 1 - (Device Failure × Failover Detection)
            = 1 - (0.001 × 0.1)
            = 1 - 0.0001
            = 99.99% (52.6 min/year)

Failover detection time: 10 seconds average

With active-active redundancy:
Availability = 1 - (Both device failure simultaneously)
            = 1 - (0.001 × 0.001)
            = 1 - 0.000001
            = 99.9999% (5.26 min/year)

Note: This assumes independent failure modes
      Correlated failures reduce actual availability
```

---

**Reference Version:** 1.0
**Last Updated:** November 2025
**Standards:** RFC 2338 (VRRP), RFC 3768 (VRRP v3)
