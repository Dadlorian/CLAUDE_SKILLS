# Network Performance Benchmarks

## Executive Summary

This document establishes baseline performance benchmarks and standards for enterprise network infrastructure. These benchmarks guide capacity planning, validate network performance, and enable data-driven decision-making for network optimization and expansion.

**Version**: 1.0
**Last Updated**: 2025-11-19
**Reference Standards**: RFC 2680 (IPPM Metrics), RFC 3393 (Delay Metrics), RFC 3432 (Loss Metrics)

---

## 1. Link Performance Benchmarks

### 1.1 Gigabit Ethernet Performance

**Standard Conditions**:
- Payload: 1500 byte (MTU 1500) Ethernet frames
- Protocol: TCP over Ethernet (no MPLS/tunneling)
- Load: Variable (0-100%)
- Testing tool: iperf3, pktgen, or vendor tools

**Expected Performance**:

```
GIGABIT ETHERNET (1000 Mbps)
═════════════════════════════════════════════

Load Condition              Throughput    Observations
──────────────────────────  ──────────────  ─────────────────────────
Unloaded (0%)               ~0 Mbps         Idle network
Light (10%)                 ~100 Mbps       Email, web browsing
Medium (40%)                ~400 Mbps       File transfers, backup
Heavy (80%)                 ~800 Mbps       Peak hour congestion
Maximum (100%)              940-980 Mbps    Line-rate theoretical max

Loss rate (no congestion):  < 0.01%         Single interface
Latency (LAN):              < 1 ms          Direct connection
Latency (WAN):              50-100 ms       Typical intercity
Jitter (LAN):               < 0.5 ms        Minimal variation
Jitter (WAN):               5-20 ms         Acceptable for voice

Practical considerations:
  ✓ Maximum achievable: ~965 Mbps (overhead: 3.5%)
    Overhead = Preamble + SFD + CRC + IFG
  ✓ Shared medium may reduce capacity
  ✓ Switch congestion impacts real throughput
  ✓ TCP overhead reduces throughput 5-10%
```

### 1.2 10 Gigabit Ethernet Performance

```
10 GIGABIT ETHERNET (10 Gbps)
═════════════════════════════════════════════

Load Condition              Throughput    Observations
──────────────────────────  ──────────────  ─────────────────────────
Line-rate maximum           9.7-9.8 Gbps    95-98% of 10G capacity
TCP throughput              8.5-9.2 Gbps    10% overhead typical
UDP throughput              9.8 Gbps        Minimal overhead
Oversubscription (10:1)     1 Gbps           Shared between 10 connections

Latency characteristics:
  Physical latency:          5.2 µs/meter    Speed of light in fiber
  Fiber-10km link:           52 µs           One-way latency for 10km
  Switch fabric:             1-5 µs          Per-hop switching delay
  End-to-end (DFW-NYC):      ~32 ms          Fiber distance ~1500 miles

QoS impact (with traffic shaping):
  100% capacity available:   9.8 Gbps        Full throughput
  With 8 CoS queues:         9.7 Gbps        ~0.1% overhead for classification
  With rate limiting:        Variable        Depends on policy

Typical deployment:
  ✓ Core network aggregation
  ✓ Data center interconnect
  ✓ Storage area network (SAN)
  ✓ High-frequency trading systems
```

### 1.3 40 Gigabit and 100 Gigabit Ethernet

```
40/100 GIGABIT ETHERNET PERFORMANCE
═════════════════════════════════════════════

Speed           Available Throughput   Applications
────────        ────────────────────   ────────────────────────
40 Gbps         38-39 Gbps              Inter-DC links, large campus
100 Gbps        97-98 Gbps              Backbone, cloud providers
200 Gbps        197-198 Gbps            Content delivery, service providers
400 Gbps        397-398 Gbps            Future (emerging standard)

Latency benchmarks:
  Single fiber link:         ~5 µs/km        Fiber propagation
  Switch fabric:             2-8 µs          Modern switching ASICs
  Typical metro (50km):      ~250 µs         One-way across city
  Typical WAN (300km):       ~1.5 ms         One-way across region

Loss characteristics (no congestion):
  Perfect link:              < 0.001%        New fiber, good equipment
  Aged link (5+ years):      < 0.01%         Still acceptable
  Link with errors:          > 0.1%          Require investigation

Buffer requirements for full line-rate:
  40G link:                  ~1 MB            Modern switches adequate
  100G link:                 ~2 MB            Standard buffer size
  Congestion prevention:     10+ MB           Absorb traffic bursts
```

---

## 2. Wide Area Network (WAN) Benchmarks

### 2.1 MPLS Circuit Performance

```
ENTERPRISE MPLS CIRCUIT BENCHMARKS
═════════════════════════════════════════════

Circuit Speed           Typical SLA         Latency Target
────────────           ──────────────────   ──────────────
10 Mbps (traditional)  99.0% availability   < 40 ms
20-50 Mbps (standard)  99.5% availability   < 40 ms
100 Mbps (fast)        99.9% availability   < 30 ms
1 Gbps (premium)       99.99% availability  < 25 ms
10 Gbps (enterprise)   99.99% availability  < 20 ms

Performance metrics breakdown:

Latency (one-way):
  ├─ Ingress processing:    0.1-0.5 ms
  ├─ MPLS forwarding:       0.5-2 ms (vendor dependent)
  ├─ Fiber propagation:     5 µs/km (depends on distance)
  ├─ Egress processing:     0.1-0.5 ms
  └─ Total (100km):         1-3 ms typical

Jitter (latency variation):
  Target: < 10 ms variance
  Cause: MPLS CoS queue discipline
  Impact: Voice quality degradation at > 50ms jitter

Packet loss:
  SLA target: < 0.1% (one-way)
  Congestion: May spike to 1-5%
  Buffer overflow: Causes drops
  Recovery: Re-transmission overhead

Circuit resiliency:
  Active/Active load balance: 50/50 split
  Active/Standby failover: < 100 ms convergence
  Dual-homed circuits: Recommended for critical sites
```

### 2.2 Internet Direct Access (DIA)

```
INTERNET DIRECT ACCESS (DIA) BENCHMARKS
═════════════════════════════════════════════

Circuit Type            Typical SLA         Notes
────────────            ──────────────────  ──────────────────
Best Effort             95% availability    Low cost, variable performance
Standard DIA            99.0% availability  Fixed bandwidth guarantee
Premium DIA             99.5% availability  QoS priority, dedicated
Enterprise DIA          99.9% availability  Redundant paths, fast support

Latency to major internet destinations:
  Google (backbone):         10-30 ms
  Amazon AWS (nearest):      15-40 ms
  Microsoft Azure (nearest): 15-40 ms
  Akamai CDN:                < 50 ms typical

Performance characteristics:
  Upload speed:              10-500 Mbps (varies by location)
  Download speed:            50-1000 Mbps (varies by location)
  Consistency:               ±20% variance typical
  Peak hours impact:         20-30% capacity reduction at 5-7 PM

Quality benchmarks for SaaS:
  Microsoft 365 (Office 365):
    ├─ Minimum: 2.5 Mbps per user
    ├─ Recommended: 10 Mbps per user
    └─ Enterprise optimal: 50 Mbps for 50 users

  Salesforce:
    ├─ Minimum: 1 Mbps per user
    ├─ Recommended: 5 Mbps per user
    └─ Enterprise optimal: 25 Mbps for 50 users

  Zoom/WebEx Video:
    ├─ HD (recommended): 2.5-4 Mbps per participant
    ├─ 1080p (optimal): 4-8 Mbps per participant
    └─ Multiple participants: 15-25 Mbps total
```

### 2.3 Private Wireless WAN (SD-WAN)

```
SD-WAN PERFORMANCE BENCHMARKS
═════════════════════════════════════════════

Metric                          Benchmark Value
──────────────────────────────  ──────────────────────────
Path failover time              < 100 ms (auto-detection)
Application acceleration:       20-40% throughput improvement
Encryption overhead:            5-15% CPU, 1-3% latency
Compression efficiency:         3:1 to 5:1 (variable data)
Path health detection interval: 100-500 ms
Control plane latency:          < 50 ms RTT to cloud controller

Multi-path aggregation (dual WAN):
  ├─ Active/Active: Both paths used (50/50)
  ├─ Bandwidth sum: Near-linear (95% efficiency)
  ├─ Failover time: < 1 second to backup path
  └─ Jitter: Increases slightly with multiple paths

Real-world performance gains:
  File transfers (compression): 2-5x improvement
  Cloud SaaS (optimization):    15-30% improvement
  Voice/Video (QoS):            < 50 ms latency maintained
  Bandwidth cost:               30-50% reduction (less fat pipes needed)
```

---

## 3. Application Layer Benchmarks

### 3.1 Response Time Standards

```
APPLICATION RESPONSE TIME STANDARDS
═════════════════════════════════════════════

Application Type           Acceptable      Optimal         Excellent
─────────────────────────  ──────────────  ────────────────  ──────────
Interactive (Database):    < 500 ms        < 200 ms        < 100 ms
Web Application:           < 2 sec         < 1 sec         < 500 ms
File Download (1GB):       < 5 minutes     2-3 minutes     1 minute
Email (SMTP send):         < 5 sec         < 1 sec         < 500 ms
VoIP (SIP):               < 100 ms        < 50 ms         < 30 ms
Video Conference:          < 150 ms        < 100 ms        < 50 ms
Remote Desktop (RDP):      < 300 ms        < 150 ms        < 100 ms
DNS resolution:            < 100 ms        < 50 ms         < 20 ms
SSH/Terminal:              < 200 ms        < 100 ms        < 50 ms

Business impact:
  ✓ > 2 seconds: Users perceive slowness
  ✓ > 5 seconds: Users abandon task
  ✓ > 10 seconds: Support calls increase
  ✓ Consistency more important than speed (jitter matters)

Calculation for end-to-end latency:
  Total = Network latency + Server processing + Client rendering

  Example:
    Network: 30 ms (WAN)
    Server processing: 150 ms (database query)
    Client rendering: 20 ms (browser)
    Total: 200 ms (acceptable)
```

### 3.2 Voice and Video Quality Metrics

```
VOICE QUALITY (VoIP) BENCHMARKS
═════════════════════════════════════════════

Metric                    Poor        Fair        Good        Excel
──────────────────────────────────────────────────────────────────
One-way latency           > 150 ms    100-150ms   50-100ms    < 50 ms
Jitter                    > 100 ms    50-100ms    20-50ms     < 20 ms
Packet loss               > 1%        0.5-1%      0.1-0.5%    < 0.1%
Bandwidth required        64 kbps     96 kbps     128 kbps    192 kbps

MOS Score (Mean Opinion Score):
  3.0 = Acceptable for emergency use
  3.5 = Acceptable for regular use
  4.0+ = Good to excellent quality

Required network performance:
  MOS 4.0 requires:
    ✓ Latency < 50 ms one-way
    ✓ Jitter < 20 ms
    ✓ Packet loss < 0.1%
    ✓ Bandwidth: 80-128 kbps per call (depends on codec)


VIDEO CONFERENCE QUALITY BENCHMARKS
═════════════════════════════════════════════

Resolution              Bandwidth       Latency Req    Participants
────────────────────    ──────────────  ──────────────  ──────────────
QCIF (176x144)         0.5 Mbps        100-200 ms      8-10
VGA (640x480)          2-3 Mbps        100-150 ms      4-6
720p (1280x720)        5-10 Mbps       < 150 ms        2-4
1080p (1920x1080)      15-25 Mbps      < 100 ms        1-2

Performance expectations:
  ✓ Up to 5 participants: 2-5 Mbps total recommended
  ✓ Large meetings (50+): 15-25 Mbps total
  ✓ Frame rate: 30 fps minimum (60 fps preferred)
  ✓ Audio is critical: never deprioritize voice
```

---

## 4. Storage and Backup Benchmarks

### 4.1 Storage Area Network (SAN)

```
FIBRE CHANNEL AND SAN BENCHMARKS
═════════════════════════════════════════════

Link Speed         Latency Target    Queue Depth    IOPS Target
────────────────   ────────────────  ──────────────  ──────────────
1 Gbps FC          < 5 ms            32-64          1,000-2,000
2 Gbps FC          < 2 ms            64-128         2,000-5,000
4 Gbps FC          < 1 ms            128-256        5,000-10,000
8 Gbps FC          < 0.5 ms          256-512        10,000-20,000
10 Gbps Ethernet   < 0.5 ms          256-512        15,000-30,000
16 Gbps FC         < 0.2 ms          512-1024       20,000-40,000
32 Gbps FC         < 0.1 ms          1024+          40,000-80,000

Storage array performance:
  SSD (solid state):         50,000+ IOPS    Latency: < 1 ms
  SAS (fast disk):           5,000-15,000    Latency: 2-5 ms
  SATA (high capacity):      500-3,000       Latency: 5-15 ms
  Hybrid (SSD + SAS):        15,000-30,000   Latency: < 5 ms

Backup throughput targets:
  Daily incremental backup:  > 1 TB/hour
  Weekly full backup:        > 500 GB/hour
  Recovery speed:            Same as backup (symmetric)
  RPO (Recovery Point Objective): 4-24 hours
  RTO (Recovery Time Objective): < 1-4 hours
```

### 4.2 Data Replication and Synchronization

```
DATA REPLICATION BENCHMARKS
═════════════════════════════════════════════

Replication Type        RPO             Bandwidth       Latency Impact
─────────────────────   ─────────────   ──────────────  ────────────────
Synchronous             0 (zero data)   Full link      5-10 ms overhead
                        loss            capacity       (write waits)

Asynchronous            15-60 min       10-50% of      < 1 ms write
                                        link capacity  impact

Journal-based           Few seconds     Variable       Negligible
                                        (on demand)    write impact

Snapshot-based          1-24 hours      Depends on     No write impact
                                        schedule

Database replication:
  MySQL replication:           50-100 ms typical lag
  SQL Server (Always On):      < 10 ms acceptable latency
  Oracle DataGuard:            < 5 ms acceptable latency
  PostgreSQL Streaming:        < 50 ms typical lag

Impact on production system:
  Synchronous replication:     10-20% latency increase
  Asynchronous replication:    < 2% latency increase
  No replication:              Baseline
```

---

## 5. Capacity Planning Benchmarks

### 5.1 User Density and Bandwidth Requirements

```
PER-USER BANDWIDTH REQUIREMENTS
═════════════════════════════════════════════

User Type              Typical      Peak Hour    Concurrent Users
──────────────────────────────────────────────────────────────────
Casual office user     100-200 kbps 300-500 kbps 100-150 per Mbps
Active knowledge work  200-500 kbps 1-2 Mbps     50-100 per Mbps
Developer/Designer     500-1000kbps 5-10 Mbps    10-50 per Mbps
Video user             1-5 Mbps     2-10 Mbps    1-10 per Mbps
Streamer (4K)          10-25 Mbps   20-40 Mbps   < 5 per 100 Mbps

Recommendations:
  200 users with 75% active:  = 150 users
  Typical office worker:      = 200 kbps = 30 Mbps total
  Peak hour multiplier:       = 3x = 90 Mbps
  Design headroom (30%):      = 117 Mbps recommended

Site access switch capacity:
  1000 users office:
    ├─ Average load: 50-100 Mbps (10-20 kbps per user)
    ├─ Peak load: 150-300 Mbps (30-60 kbps per user)
    └─ Oversubscription: Recommended 10:1 max
```

### 5.2 Growth Projections

```
NETWORK GROWTH FORECASTING
═════════════════════════════════════════════

Historical Growth Rates (Industry Average):
  Bandwidth: 25-40% YoY (doubling every 2-3 years)
  Devices: 15-25% YoY (smartphones, IoT)
  Applications: 30-50% YoY (cloud, SaaS)
  Data volume: 40-60% YoY (video, big data)

Capacity planning timeline:
  Current year:         100% of capacity
  Year 1-2:             40-50% spare capacity
  Year 2-3:             20-30% spare capacity
  Year 3-4:             Upgrade planning begins
  Year 4-5:             Upgrade execution

Example: Dallas site current 1 Gbps core
─────────────────────────────────────────

Year 1 (2026):  Current: 400 Mbps   → Available: 600 Mbps
Year 2 (2027):  Current: 650 Mbps   → Available: 350 Mbps
Year 3 (2028):  Current: 1000 Mbps  → Available: 0 Mbps (UPGRADE!)

Action: Upgrade to 10 Gbps in Q3 2027 (before hitting 100%)

Recommendation headroom:
  ✓ Maintain 30-40% headroom in production network
  ✓ Design for 5-year growth (40% CAGR = 2.3x growth)
  ✓ Plan upgrades 18 months in advance
  ✓ Budget constraints may require 3-year cycle
```

---

## 6. Measurement and Validation Procedures

### 6.1 Network Performance Testing

```
PERFORMANCE TEST METHODOLOGY
═════════════════════════════════════════════

TEST: Throughput Baseline (new circuit)
──────────────────────────────────────

Objective: Establish maximum sustainable throughput

Tools: iperf3, pktgen, or vendor-supplied
Duration: 10 minutes sustained load
Traffic profile: TCP/UDP mixture (realistic)

Procedure:
  1. Clear interface counters
  2. Start traffic generation (source)
  3. Monitor for 5 min (let network stabilize)
  4. Record 5-min average throughput
  5. Stop traffic, document results

Expected results (1 Gbps Ethernet):
  ✓ TCP throughput: 900-950 Mbps
  ✓ UDP throughput: 970-990 Mbps
  ✓ Jitter: < 1 ms
  ✓ Packet loss: 0%


TEST: Latency and RTT (Round-trip Time)
─────────────────────────────────────────

Objective: Measure one-way latency

Tools: ping, tracert, or specialized tools
Packet size: 1500 bytes (MTU), 56 bytes (minimum)
Sample size: 1000+ packets

Procedure:
  1. Send 1000 ICMP echo requests
  2. Calculate min, max, average, stddev
  3. Jitter = (max RTT - min RTT) / 2
  4. Document results with timestamp

Expected results (metro WAN, 50km):
  ✓ Min latency: 0.5-1 ms
  ✓ Avg latency: 1-2 ms
  ✓ Max latency: 5-10 ms
  ✓ Jitter (stddev): < 1 ms


TEST: Packet Loss Detection
──────────────────────────────

Objective: Identify frame loss under load

Tools: pktgen, custom scripts
Conditions: Various loads (10%, 50%, 100%)

Procedure:
  1. Send known number of packets (10M packets)
  2. Verify count at destination
  3. Calculate loss: (sent - received) / sent * 100%
  4. Repeat at different loads

Acceptable results:
  ✓ 0% at all loads (healthy network)
  ✓ < 0.01% at congestion (minimal impact)
  ✓ > 0.1% indicates issues (investigate)
```

### 6.2 Baseline Documentation

```
NETWORK BASELINE TEMPLATE
═════════════════════════════════════════════

CIRCUIT: DFW-Core-01 to NYC-Core-01 (primary WAN link)
─────────────────────────────────────────────────────

ESTABLISHMENT DETAILS:
  Date measured: 2025-11-19
  Time of day: 14:30 UTC
  Network load: Light (10%)
  Traffic type: Baseline measurement (no user traffic)

PHYSICAL CHARACTERISTICS:
  Circuit speed:           100 Mbps (committed)
  Distance:               1500 miles (fiber optic)
  Circuitty provider:      AT&T (MPLS)
  Link type:              MPLS with QoS

MEASURED PERFORMANCE:
  Throughput:
    ├─ TCP (9500-byte frames):  95.2 Mbps
    ├─ UDP (same frames):       98.1 Mbps
    └─ Measurement tool:        iperf3

  Latency:
    ├─ Ping (1500 bytes):       28.5 ms (average)
    ├─ RTT variance:            ± 0.8 ms (jitter)
    ├─ Min latency:             27.2 ms
    └─ Max latency:             30.3 ms

  Packet loss:
    ├─ 10 million packets:      0 lost (0.00%)
    ├─ Test conditions:         Sustained 50 Mbps
    └─ Conclusion:              Healthy link

QUALITY METRICS:
  Voice suitability (MOS):      4.2 (good)
  Video conference capacity:    Supports 2-3 simultaneous 720p calls
  File transfer performance:    10 MB file in ~0.8 seconds

ENVIRONMENTAL FACTORS:
  Temperature:            72°F (normal)
  Humidity:              45% (normal)
  Cross-talk:           None detected
  Weather conditions:    Clear (affects fiber minimally)

BASELINE CONCLUSION:
  ✓ Circuit performing to specification
  ✓ Suitable for production enterprise traffic
  ✓ Link ready for deployment
  ✓ Next review: 2026-05-19

SIGNATURE:
  Measured by: J. Smith (Senior Network Engineer)
  Date: 2025-11-19
  Approved by: M. Johnson (Network Manager)
```

---

## 7. References and Standards

- **RFC 2680**: A One-way Delay Metric for IPPM
- **RFC 3393**: IP Packet Delay Variation Metric
- **RFC 3432**: Network performance measurement with periodic streams
- **RFC 6348**: IMIX Genome

**Industry Standards**:
- **TIA/EIA-568**: Cabling Standards
- **IEEE 802.3**: Ethernet Standards
- **ITU-T G.114**: One-way transmission time
- **ITU-T Y.1541**: Network performance objectives

**Last Revision**: 2025-11-19
**Next Review**: 2026-05-19
**Owner**: Network Operations and Performance Team
