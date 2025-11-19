# Network Hardware Selection

## Introduction
Selecting appropriate network hardware is critical for achieving performance, reliability, and cost objectives. This reference provides selection criteria and platform comparisons.

## Selection Methodology

### Step 1: Define Requirements

```
Requirement assessment worksheet:

Performance Requirements:
  - Throughput: 100 Gbps (total fabric capacity)
  - Latency: <1 microsecond for intra-switch
  - Jitter: <100 microseconds acceptable
  - Switching capacity: 65 Tbps (wire-speed)
  - Packet forwarding rate: 1,500 Mpps

Scalability Requirements:
  - VLAN capacity: 4,000+
  - ACL entries: 50,000+
  - Routing table entries: 1,000,000+
  - Multicast groups: 10,000+
  - Dynamic port groups: 500+

Redundancy Requirements:
  - Dual supervisors: Required
  - Dual fabric cards: Required
  - Redundant power supplies: 2N (minimum 3 supplies)
  - Redundant cooling: 2N (minimum 3 fans)
  - MTBF: >100,000 hours

Environmental Requirements:
  - Power: Maximum 15 kW per switch
  - Cooling: Hot/cold aisle capable
  - Noise: <75 dB acceptable
  - Footprint: 1 RU preferred (< 2 RU)
  - Weight: <100 lbs (datacenter constraint)

Support Requirements:
  - Warranty: 5-year preferred (3-year minimum)
  - Support SLA: 4-hour response
  - Training: Vendor provided
  - Documentation: Comprehensive
  - Community: Active forum/knowledge base
```

### Step 2: Tier Selection

```
Tier 1 (Core Layer):
  Role: Backbone switching, BGP routing
  Criticality: Mission-critical
  Performance: Extreme (>100 Tbps)
  Cost: >$200,000 per unit
  Examples: Nexus 9516, Arista 7368

Tier 2 (Distribution Layer):
  Role: Traffic aggregation, policy enforcement
  Criticality: High (redundancy required)
  Performance: Very High (10-65 Tbps)
  Cost: $50,000-$150,000 per unit
  Examples: Catalyst 9500, Arista 7050

Tier 3 (Access Layer):
  Role: End-device connectivity
  Criticality: Medium (distributed failure)
  Performance: High (500 Gbps - 1 Tbps)
  Cost: $10,000-$30,000 per unit
  Examples: Catalyst 9200L, Arista 7050SX
```

## Platform Comparison

### Enterprise Campus - Cisco Catalyst

```
Cisco Catalyst 9500 (Distribution/Core)
  Models: 9500, 9500X, 9500H
  Throughput: 65 Tbps
  Port density: 48 × 1/10/25G + 6 × 40/100G
  Latency: <1 microsecond
  Power: 800W typical
  Redundancy: Dual sup, N+1 fabric
  VLAN capacity: 4,094
  Warranty: 5 years (with SMARTnet)
  Price: $50,000-$80,000

Cisco Catalyst 9300 (Distribution)
  Throughput: 8 Tbps
  Port density: 24-48 × 1/10G
  Latency: <1 microsecond
  Power: 500W typical
  Redundancy: Dual sup
  Price: $20,000-$35,000

Cisco Catalyst 9200L (Access)
  Throughput: 680 Gbps
  Port density: 24-48 × 1G + 4 × 10G
  Latency: <3 microseconds
  Power: 200W typical
  Redundancy: Single sup
  PoE: 885W (24-port)
  Price: $15,000-$25,000

Cisco Catalyst 9100 (Lightweight)
  Throughput: 176 Gbps
  Port density: 8-16 × 1G
  Wireless: Built-in AP controller
  Price: $8,000-$15,000
```

### Enterprise Campus - Arista

```
Arista 7368 (Core/Super-Spine)
  Throughput: 300+ Tbps
  Port options: Modular (up to 288 × 100G)
  Latency: <400 nanoseconds
  Power: 25 kW maximum
  Redundancy: Full (dual everything)
  Price: $200,000-$350,000

Arista 7050SX (Distribution/Spine)
  Throughput: 480 Gbps
  Port density: 32 × 10G + 8 × 40G
  Latency: <500 nanoseconds
  Power: 4.5 kW
  Redundancy: Full
  Price: $25,000-$40,000

Arista 7050QX (Distribution)
  Throughput: 864 Gbps
  Port density: 48 × 40G + 6 × 100G
  Power: 6.5 kW
  Price: $35,000-$50,000

Arista 7050TX (Access/Leaf)
  Throughput: 192 Gbps
  Port density: 48 × 10G + 4 × 40G
  PoE: Optional modules
  Power: 2.5 kW
  Price: $12,000-$20,000
```

### Data Center - Cisco Nexus

```
Nexus 9516 (Core)
  Throughput: 300 Tbps
  Modules: 6 line cards + 2 fabric cards (N+1)
  Interface speeds: 40G, 100G, 400G options
  Maximum bandwidth: 51.2 Tbps (single direction)
  Latency: <500 nanoseconds
  Power: 35 kW maximum
  Redundancy: Dual supervisors, N+1 fabric
  Price: $250,000-$400,000

Nexus 9372 (Distribution/Leaf)
  Throughput: 28.8 Tbps
  Port density: 48 × 100G + 8 × 100G QSFP28
  Power: 6 kW
  Price: $80,000-$120,000

Nexus 9396 (Leaf)
  Throughput: 19.2 Tbps
  Port density: 48 × 100G
  PoE: Optional
  Price: $60,000-$80,000
```

## Hardware Selection Decision Matrix

| Factor | Cisco | Arista | Juniper | Cumulus |
|--------|-------|--------|---------|---------|
| Throughput | Very High | Very High | High | High |
| Price | Medium-High | Medium | Medium-High | Low |
| Management | IOS-XE | EOS | Junos | Linux |
| Learning curve | Medium | Medium | High | Low |
| Enterprise support | Excellent | Good | Good | Good |
| Industry adoption | Highest | Growing | Solid | Growing |
| Warranty (5yr) | Available | Available | Available | Limited |

## Interface Speed Selection

```
Link speed considerations:

Access layer (user connections):
  - 1 Gbps: Standard for offices (< 100 users)
  - 2.5 Gbps: Hybrid (office + wireless)
  - 5 Gbps: Dense office areas
  - 10 Gbps: High-density (>200 users per switch)

Distribution uplinks:
  - 10 Gbps: Minimum for modern networks
  - 25 Gbps: Recommended for aggregation
  - 40 Gbps: High-performance requirements
  - 100 Gbps: Large campuses (>5,000 users)

Core interconnects:
  - 40 Gbps: Minimum for dual core
  - 100 Gbps: Recommended for redundancy
  - 400 Gbps: Next-generation, future-proof

Data center fabric:
  - 25 Gbps: Small clusters (< 50 servers)
  - 100 Gbps: Standard (50-500 servers)
  - 400 Gbps: Hyper-scale (>1,000 servers)
```

## Power and Cooling Calculation

```
Power budget example (Catalyst 9500):

Device power consumption:
  - Supervisor: 150W
  - Line cards (4 × 12x100G): 800W
  - Fabric: 100W
  - Total typical: 1,050W
  - Peak: 1,200W (warm startup)

Redundancy:
  - PSU count: 3 (2N redundancy)
  - PSU capacity: 400W × 3 = 1,200W available
  - Margin: 150W (adequate)

Cooling requirement:
  - Heat dissipation: 1,050W ≈ 3,580 BTU/hour
  - Fan airflow: 300-400 CFM (cubic feet per minute)
  - Recommended: Separate cold aisle

Rack power allocation:
  - Single PDU: 20 amps × 120V = 2,400W
  - Dual PDU (redundancy): 2 × 20 amps = 4,800W
  - Multiple switches: Use multiple PDUs

Example 4-switch distribution pair:
  4 × 1,200W = 4,800W = 4 × 20 amp circuits needed
  Recommended: 2 × 30 amp circuits (redundancy + growth)
```

## Module and Interface Selection

```
Catalyst 9500 Line Card Options:

48-port 1G + 4-port 10G module (C9500-LM-24X)
  Cost: $3,000 per module
  Throughput: 96 Gbps
  Density: 48 × 1G copper (RJ45)
  Use: Access layer with PoE

48-port 10G module (C9500-LM-48X)
  Cost: $8,000 per module
  Throughput: 960 Gbps
  Density: 48 × 10G SFP+ ports
  Use: High-speed access or distribution

8-port 100G module (C9500-LM-8X100G)
  Cost: $12,000 per module
  Throughput: 1.6 Tbps
  Density: 8 × 100G QSFP28
  Use: Core/distribution uplinks

Transceiver options (per interface):
  - Copper 10G: $200-$400
  - Fiber 10G: $150-$300 (with licensing)
  - Copper 25G: $300-$500
  - Fiber 100G: $400-$800
  - Fiber 400G: $800-$1,500

Power budgets:
  Copper interfaces: Minimal power draw
  Optics: 0.5-2W per port
  High-speed optics (100G+): 1-3W per port
```

## Redundancy Selection

```
Supervisor card configuration:

Single supervisor (basic):
  - Risk: Complete switch failure forces replacement
  - Failover: Manual intervention required
  - Availability: 99%
  - Cost: -$20,000

Dual supervisors (recommended):
  - Risk: Switch remains operational
  - Failover: Automatic via SSO (Stateful Switchover)
  - Convergence: <30 seconds
  - Availability: 99.9%
  - Cost: Standard in enterprise switches

N+1 fabric (Nexus 9516):
  - Risk: Switch survives single fabric failure
  - Failover: Automatic, transparent
  - Convergence: <1 millisecond
  - Availability: 99.99%
  - Cost: +$50,000 (for large switches)
```

## Interface Transceiver Selection

```
Transceiver types and costs:

10GBase-SR (Multimode fiber, 300m):
  - Cost: $150-$250
  - Typical use: Data center intra-rack
  - Wave: 850 nm (short wavelength)
  - Budget: Best for short distances

10GBase-LR (Single-mode fiber, 10km):
  - Cost: $200-$350
  - Typical use: Campus backbone
  - Wave: 1310 nm (long wavelength)
  - Budget: Good for campus distances

10GBase-ZR (Single-mode fiber, 80km):
  - Cost: $300-$500
  - Typical use: Long-distance WAN
  - Wave: 1550 nm (telecom standard)
  - Budget: Extreme long distance

25GBase-SR (Multimode fiber):
  - Cost: $300-$500
  - Typical use: Data center
  - Distance: 100-150m
  - Bandwidth: 25 Gbps

100GBase-SR4 (Multimode fiber):
  - Cost: $400-$800
  - Typical use: Data center
  - Distance: 100m
  - Bandwidth: 100 Gbps

Copper options (10G):
  - RJ45 (requires Cat6A): $200-$400
  - Distance: Limited to 100m
  - Latency: Slightly higher than fiber
  - Advantage: Easy installation, no SFP modules
```

## Cost Optimization Strategies

```
Total Cost of Ownership (TCO) analysis:

5-year cost comparison:

Premium Solution (Catalyst 9500 × 4):
  Hardware: 4 × $70,000 = $280,000
  Interfaces (upgrades): $50,000
  Installation/Config: $30,000
  Maintenance (5 yrs): $50,000/year × 5 = $250,000
  Power/Cooling: $20,000/year × 5 = $100,000
  Total: $710,000

Mid-range Solution (Catalyst 9300 × 6 + upgrades):
  Hardware: 6 × $25,000 = $150,000
  Interfaces: $40,000
  Installation: $30,000
  Maintenance: $30,000/year × 5 = $150,000
  Power/Cooling: $12,000/year × 5 = $60,000
  Total: $430,000

Cost savings: $280,000 (39% reduction)
Trade-off: Slight performance reduction, more devices to manage

Recommendation: Mid-range with growth plan
  - Phase 1: Deploy mid-range
  - Phase 2 (Year 2): Upgrade core to premium
  - Balances cost with future scalability
```

## Lifecycle and Upgrade Planning

```
Typical hardware lifecycle:

Acquisition: Year 0
  - Deployment of new hardware
  - Integration with existing network
  - Baseline performance measurement

Operations: Years 1-3
  - Standard maintenance
  - Software updates
  - Warranty support (included)

Decline: Years 4-5
  - Extended support costs increase
  - Performance adequate but aging
  - Industry moving to newer standards

End of life: Year 5+
  - Vendor support ends
  - Extended support premium (50%+ of maintenance)
  - Replacement parts scarce
  - Security vulnerabilities unfixed

Upgrade trigger:
  - Capacity: Consistently > 70% utilization
  - Performance: Latency degradation observed
  - Availability: Failures increasing
  - Support: Vendor declares end-of-life
  - Security: Critical vulnerabilities with no patch
```

---

**Reference Version:** 1.0
**Last Updated:** November 2025
**Manufacturers:** Cisco, Arista, Juniper, Cumulus
