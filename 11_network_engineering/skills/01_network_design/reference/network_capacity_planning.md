# Network Capacity Planning

## Introduction
Network capacity planning ensures infrastructure meets current and future needs while optimizing costs. This reference covers methodologies and calculations.

## Capacity Planning Methodology

### Step 1: Baseline Assessment

```
Collect current data:

1. User count and growth rate
   - Current: 500 users
   - Growth: 10% annually
   - Projected (3 years): 665 users

2. Device inventory
   - Desktop/Laptop: 500 (2x per user for hot seating)
   - IP Phones: 350
   - Printers: 75
   - Wireless devices: 200 (average)
   - IoT/Sensors: 100
   - Total: ~1,225 devices

3. Network infrastructure
   - Campus size: 4 buildings, 3 floors each
   - Wiring: Cat6A (100m runs)
   - Current WAN: Dual 100 Mbps MPLS
   - Current LAN: 1 Gbps edge to Gigabit switches

4. Traffic characteristics
   - Peak hours: 8am-12pm, 1pm-4pm
   - Video streaming: 25% increase last year
   - Cloud adoption: SaaS migration 40% apps
   - VoIP: 350 active calls during peak
```

### Step 2: Traffic Analysis

```
Method: NetFlow analysis, SNMP polling, or packet capture

Device: Cisco Catalyst 9500 with NetFlow v9

Sample 24-hour data:

Hour | Utilization | Peak Flow | Direction
-----|------------|-----------|----------
8:00 | 45%        | 450 Mbps  | Up+Down
9:00 | 62%        | 620 Mbps  | Up+Down
10:00| 78%        | 780 Mbps  | Down
11:00| 85%        | 850 Mbps  | Down
12:00| 65%        | 650 Mbps  | Down
1:00 | 35%        | 350 Mbps  | Mixed
2:00 | 71%        | 710 Mbps  | Up
3:00 | 82%        | 820 Mbps  | Up
4:00 | 58%        | 580 Mbps  | Down
5:00 | 32%        | 320 Mbps  | Mixed

Daily Peak: 850 Mbps (11am)
Average: 562 Mbps
Night avg: 150 Mbps

Application breakdown:
- Video streaming: 35% of peak traffic
- Cloud apps (Salesforce, O365): 25%
- File transfer: 15%
- Email: 10%
- Web browsing: 10%
- Other: 5%
```

### Step 3: Growth Projection

```
Formula:
  Projected Demand = Current Demand × (1 + Growth Rate)^Years

Example:
  Current peak: 850 Mbps
  Growth rate: 15% annually (aggressive)

  Year 1: 850 × 1.15 = 977.5 Mbps
  Year 2: 850 × 1.15² = 1,124 Mbps
  Year 3: 850 × 1.15³ = 1,293 Mbps

Headroom calculation:
  Projected: 1,293 Mbps
  Target utilization: 70% (max allowed)
  Required capacity: 1,293 / 0.70 = 1,847 Mbps ≈ 2 Gbps

Recommended action:
  Current: 2 × 100 Mbps (200 Mbps) → OVERLOADED
  Near term: Upgrade to 500 Mbps
  Year 2: Upgrade to 1 Gbps
  Year 3: Upgrade to 2 Gbps
```

## LAN Capacity Planning

### Access Layer Sizing

```
Formula:
  Ports needed = (Total devices × 1.2) / Switch utilization

Example:
  1,225 devices calculated above
  Target utilization: 75% (typically 60-80%)
  Ports needed: (1,225 × 1.2) / 0.75 = 1,960 ports

Switch selection:
  48-port Catalyst 9200L: Cost $18,000
  Number needed: 1,960 / 48 = 40.8 ≈ 42 switches
  Total cost: 42 × $18,000 = $756,000

Optimization:
  If we allow 85% utilization:
    (1,225 × 1.2) / 0.85 = 1,730 ports
    1,730 / 48 = 36 switches needed
    Savings: $108,000

Trade-off: Higher utilization means less headroom for growth
```

### Uplink Capacity

```
Aggregation formula:
  Uplink capacity = (Access port bandwidth × port count × utilization%)
                    / EtherChannel member count

Example:
  - 48 access ports at 1 Gbps each
  - Average utilization: 35% during peak
  - EtherChannel: 4 × 10G uplinks

  Needed capacity: (48 × 1 × 0.35) = 16.8 Gbps
  Provided capacity: 4 × 10 = 40 Gbps

  Oversubscription ratio: 40 / 16.8 = 2.4:1 (acceptable)

  Recommendation: 4 × 10G sufficient, plan for 8 × 10G in 3 years
```

### Distribution Layer

```
Formula:
  Distribution capacity = (All access uplinks sum) + (WAN capacity)

Example:
  12 access switches, each with 4 × 10G uplinks
  Total access uplinks: 12 × 4 × 10G = 480 Gbps

  WAN requirement: 2 Gbps (as calculated above)

  Distribution fabric needed: 480 + 2 = 482 Gbps

  To distribution: Use 2 x Catalyst 9500 (65 Tbps each)
  Dual core links: 2 × 100G = 200 Gbps

  Result: Excellent headroom for growth
```

## WAN Capacity Planning

### Internet Circuit Sizing

```
Traffic distribution model:

Total peak: 850 Mbps (calculated above)

Distribution:
  - Data center: 30% (255 Mbps)
  - Cloud/SaaS: 40% (340 Mbps)
  - Internet: 20% (170 Mbps)
  - VoIP/Video: 10% (85 Mbps)

WAN requirements:
  - DC access: 255 Mbps (MPLS primary)
  - Cloud + Internet: 340 + 170 = 510 Mbps (Internet/SD-WAN)
  - VoIP: 85 Mbps (Low-latency guaranteed)

  Total WAN: 850 Mbps needed
  But asymmetric:
    Downstream: 510 Mbps (video streaming, downloads)
    Upstream: 340 Mbps (SaaS, uploads, backup)
```

### Internet ISP Selection

```
Sizing table for 500-user office:

Traffic: 850 Mbps peak

Option 1: Single Fiber Circuit
  - Symmetric 1 Gbps fiber
  - Cost: $3,500/month
  - Redundancy: None (ISP internal only)
  - Setup: 4-6 weeks
  - Risk: Single point of failure

Option 2: Dual ISP (Recommended)
  - Primary: 1 Gbps fiber (AT&T)
  - Backup: 500 Mbps cable (Comcast)
  - Cost: $3,500 + $2,200 = $5,700/month
  - Setup: 4-6 weeks
  - Redundancy: N+1 (500 Mbps failover)
  - Configuration: SD-WAN or dual BGP

Option 3: Fiber + LTE + Backup
  - Primary: 1 Gbps fiber
  - Secondary: 300 Mbps LTE
  - Backup: 100 Mbps DSL
  - Cost: $5,000/month
  - Redundancy: Multiple paths
  - Setup: 2-4 weeks (LTE/DSL much faster)
  - Best for: Business continuity critical
```

### MPLS and Private Circuit Sizing

```
Data center connectivity:

Peak DC traffic: 255 Mbps
Target utilization: 60%
Headroom for growth: 40%

Required capacity:
  Current need: 255 Mbps
  With 40% headroom: 255 / 0.60 = 425 Mbps

Choose circuit:
  - 500 Mbps MPLS (common increment)
  - Cost: $2,500/month
  - Redundancy: 100 Mbps backup recommended ($1,200/month)
  - Total: $3,700/month

Multi-site consideration:
  5 branch sites × 100 Mbps = 500 Mbps total needed
  But with statistical multiplexing: 300 Mbps sufficient

  Hub-and-spoke design:
  - Hub uplink: 500 Mbps (peak of all spokes + HQ)
  - Spoke uplinks: 100 Mbps each
  - Total: 1 × 500 + 5 × 100 = 1,000 Mbps
  - Cost vs full mesh: 55% lower
```

## Storage Network Capacity

### iSCSI/FC Network

```
Data center storage network:

Calculation:
  VM backup requirement: 2 TB/day
  Backup window: 6 hours (10pm-4am)
  Required bandwidth: 2 TB × 8 bits/byte / 21,600 seconds
                    = 16 Tbps / 21,600 sec = 741 Mbps

  Add protocol overhead: 741 × 1.15 = 852 Mbps

  Design decision:
  - Option 1: 10G iSCSI (adequate with margin)
  - Option 2: 10G + 10G redundant (recommended)
  - Option 3: 40G iSCSI (future-proof for 100x scale)

  Recommended: 2 × 10G iSCSI links per storage path
  Cost per server: 2 × $800 (SFP+ interfaces) = $1,600
```

## Voice Network Capacity

### VoIP Bandwidth Planning

```
Codec and bandwidth calculation:

G.711 codec (standard):
  - Sample rate: 8 kHz
  - Sample size: 8 bits
  - Payload per packet: 20 ms = 160 bytes
  - Packet header: IP(20) + UDP(8) + RTP(12) = 40 bytes
  - Total per packet: 200 bytes
  - Packets/second: 50
  - Bandwidth: 200 bytes × 50 = 10,000 bytes/sec = 80 Kbps

G.729 codec (compressed):
  - Payload: 10 bytes per 10ms
  - Bandwidth: ~24 Kbps (with overhead)

Planning:
  350 simultaneous VoIP calls at peak
  G.711: 350 × 80 Kbps = 28 Mbps
  G.729: 350 × 24 Kbps = 8.4 Mbps

  Add video conferencing (50 participants):
  - Each participant: 2.5 Mbps (HD video)
  - Total: 50 × 2.5 = 125 Mbps

  Total voice + video: 28 + 125 = 153 Mbps reserved

VLAN QoS configuration:
  Voice VLAN (110): Reserve 200 Mbps (30% buffer)
  Video VLAN (111): Reserve 200 Mbps (30% buffer)
  Other traffic: Uses remaining capacity
```

## Video Conferencing Capacity

```
HD Video Conferencing Requirements:

1080p Video Conference:
  - Codec: H.264/VP9
  - Bitrate: 2.5-4 Mbps per participant
  - Multiple participants: 100 participant meeting
    Incoming stream: 1 HD feed (2.5 Mbps)
    Outgoing stream: 1 HD feed (2.5 Mbps)
    Total: 5 Mbps per participant

    Scaled: 100 × 5 = 500 Mbps total bandwidth

    Reality: Compression and selective streams
    Actual: 50-100 Mbps for same meeting

Capacity planning:
  Concurrent meetings: 10 × (average 25 participants)
  Peak bandwidth: 10 × 50 Mbps = 500 Mbps

  From WAN: 340 Mbps cloud allocation covers this
  From LAN: Video VLAN at 200 Mbps is constrained

  Action: Increase video VLAN to 400 Mbps
```

## Capacity Monitoring and Adjustment

```
Monitoring thresholds:

Link utilization:
  Green (< 50%): Good, normal operations
  Yellow (50-70%): Caution, plan upgrades
  Red (70-85%): Action needed within 6 months
  Critical (> 85%): Emergency upgrade required

Device utilization:
  CPU: Keep below 75% sustained
  Memory: Keep below 80% sustained
  Buffer: Keep below 90% sustained

Response timeline:
  < 50%: No action
  50-70%: Plan for 12-month replacement cycle
  70-85%: Order replacement, plan for 6-month implementation
  > 85%: Emergency procurement, implement within 1-3 months

Escalation procedures:
  Yellow alert: Schedule meeting to review growth
  Red alert: Initiate procurement process
  Critical: Executive escalation, emergency budget approval
```

## Cost Optimization Techniques

```
Capacity vs Cost trade-off analysis:

Scenario A: Over-provisioned (80% headroom)
  - Infrastructure: $1,000,000
  - Maintenance: $150,000/year
  - Upgrade frequency: Every 5 years
  - Downtime risk: Very low
  - Total 5-year cost: $1,750,000

Scenario B: Balanced (40% headroom)
  - Infrastructure: $700,000
  - Maintenance: $120,000/year
  - Upgrade frequency: Every 3 years
  - Downtime risk: Low
  - Total 5-year cost: $1,300,000

Scenario C: Just-in-time (10% headroom)
  - Infrastructure: $500,000
  - Maintenance: $100,000/year
  - Upgrade frequency: Every 18 months
  - Downtime risk: Medium
  - Total 5-year cost: $1,300,000

Recommendation: Scenario B (balanced)
  - Adequate capacity for business needs
  - Reasonable upgrade cycle
  - Lower downtime risk than just-in-time
  - Cost competitive with over-provisioned approach
```

---

**Reference Version:** 1.0
**Last Updated:** November 2025
**Standards:** RFC 2475 (Capacity Planning Framework)
