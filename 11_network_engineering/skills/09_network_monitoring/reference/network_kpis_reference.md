# Network KPIs Reference

## Overview
Network Key Performance Indicators (KPIs) define measurable thresholds for assessing network health, performance, and business impact.

## Availability Metrics

### Uptime & Reliability

#### Device Availability
```
Definition: Percentage of time device responds to monitoring
Formula: (Operating Hours / Total Hours) × 100
Target: 99.9% (99.99% for critical systems)
Typical: 95-99.95%

Calculation:
99.0% = 7.2 hours downtime/month
99.5% = 3.6 hours downtime/month
99.9% = 43.2 minutes downtime/month
99.99% = 4.32 minutes downtime/month
```

#### Service Availability
```
Definition: Percentage of time service is functional
Example: BGP neighbor availability
Target: 99.99%+ for critical routes
```

#### MTBF & MTTR
```
MTBF (Mean Time Between Failures)
- Track: Average time between device failures
- Target: 40,000+ hours (>4 years)
- Industry standard: 100,000-200,000 hours

MTTR (Mean Time To Repair)
- Definition: Average time to restore service
- Target: <15 minutes for critical systems
- Track: Detection time + resolution time
```

## Performance Metrics

### Latency

#### Round Trip Time (RTT)
```
Definition: Time for packet to travel to destination and back
Measurement: ICMP Echo Request/Reply (ping)
Typical:
  LAN: < 5 ms
  WAN: 20-100 ms
  Internet: 50-200 ms
Critical threshold: >200 ms
Alert threshold: >150 ms
```

#### One-Way Latency
```
Definition: Time for packet to reach destination only
Measurement: Specialized tools (network taps)
Typical:
  LAN: < 3 ms
  Continental links: 30-80 ms
  Intercontinental: 100-300 ms
```

#### Jitter
```
Definition: Variation in latency (standard deviation)
Formula: StdDev(RTT measurements)
Target: < 50 ms (voice acceptable)
         < 30 ms (optimal)
Calculation: Measure 10+ samples, calculate variance
```

#### Packet Loss
```
Definition: Percentage of packets that don't reach destination
Formula: (Lost Packets / Sent Packets) × 100
Target: 0% (zero loss target)
Acceptable: < 0.1% for data
          < 0.05% for voice
Critical: > 1% indicates serious issues

Example:
Sent: 100, Received: 99, Lost: 1
Loss Rate: 1%
```

### Throughput Metrics

#### Bandwidth Utilization
```
Definition: Actual bandwidth used vs provisioned capacity
Formula: (Current Traffic / Link Capacity) × 100

Healthy: < 50% average, < 70% peak
Caution: 70-85% average usage
Critical: > 85% average, > 95% peak

Example:
10 Gbps link with 3 Gbps average traffic:
Utilization = (3 / 10) × 100 = 30%
```

#### Throughput Efficiency
```
Definition: Actual useful traffic vs total link capacity
Formula: (Goodput / Link Capacity) × 100

TCP Efficiency:
- Ideal: ~95-98% (5-2% overhead)
- Typical: ~85-95%
- Poor: < 80%

Overhead sources:
- TCP/IP headers
- Retransmissions
- Protocol inefficiencies
```

#### Goodput
```
Definition: Useful application-layer traffic rate
Formula: Total traffic - Protocol overhead
Example:
  Raw bandwidth: 100 Mbps
  TCP/IP overhead: 3 Mbps (3%)
  Goodput: 97 Mbps
```

### Application Performance

#### Response Time
```
Definition: Time from request sent to response received
Target: < 200 ms (interactive apps)
        < 1000 ms (background jobs)
        < 5000 ms (batch processes)

Percentile tracking:
- p50: Median response time
- p95: 95th percentile
- p99: 99th percentile
- p99.9: 99.9th percentile

Example:
p95 < 300 ms means 95% of requests respond in <300ms
```

#### Transaction Success Rate
```
Definition: Percentage of transactions completing successfully
Formula: (Successful / Total) × 100
Target: > 99.95% for critical systems
       > 99.9% for standard services

Track:
- Connection attempts: successful vs failed
- Request completion: success vs timeout vs error
- Application errors: 4xx, 5xx responses
```

#### Network Round Trip Time (NRTT)
```
Definition: Network component of total response time
Calculation: Total RTT - processing time
Tools: NetFlow timing data, network taps
```

## Reliability Metrics

### Packet Loss Analysis

#### Loss Rate by Path
```
Definition: Packet loss percentage for specific route
Measurement: Continuous ping, TWAMP, OWAMP
Target: 0% normal, <0.1% acceptable
Alert: Any sustained loss

Trending: Track loss spikes for correlation
```

#### Burst Loss Detection
```
Definition: Consecutive packet loss events
Pattern: Loss[n], Loss[n+1], Loss[n+2]
Significance: Indicates congestion or device issues
Analysis: Correlate with interface errors
```

#### Loss Asymmetry
```
Definition: Packet loss differences between directions
Example:
  A→B loss: 0.5%
  B→A loss: 2.0%
Indicates: Potential path asymmetry or congestion
```

### Error Metrics

#### CRC Errors
```
Definition: Cyclic Redundancy Check failures
Typical cause: Physical layer issues
Target: 0 errors
Action: Investigate immediately
Commands:
  show interfaces [interface]
  ethtool -S [interface]
```

#### Collisions (Half-Duplex Only)
```
Definition: Simultaneous transmission attempts
Modern: Minimal (full-duplex standard)
Legacy: Track for half-duplex links
```

#### FCS Errors (Frame Check Sequence)
```
Definition: Frame validation failures
Cause: Corruption, noise, EMI
Target: 0 errors
Investigation: Check cabling, EMI, duplex mismatch
```

### Reachability Metrics

#### BGP Convergence Time
```
Definition: Time to detect and propagate topology changes
Target: < 1 second for fast convergence
Typical: 1-3 seconds
Slowest acceptable: 5 seconds

Calculation:
  Time from link failure → BGP notification sent
  + Time to process notification
  + Time to propagate to all neighbors
```

#### OSPF Convergence
```
Definition: Time for OSPF to detect and adapt to changes
Target: < 1 second (with BFD)
Typical: 1-2 seconds
Without fast timers: 30-40 seconds
```

#### Route Flapping
```
Definition: Rapid on/off cycling of a route
Cause: Flaky interface, instability, misconfiguration
Metric: Flaps per minute/hour
Target: 0 flaps
Alert: >1 flap per hour
```

## Quality Metrics

### Mean Opinion Score (MOS) - VoIP

```
Definition: Perceived voice quality on scale 1-5
  5.0 = Excellent (no perceptible issues)
  4.0 = Good (slightly perceptible, no disturbance)
  3.0 = Fair (perceptible, minor disturbance)
  2.0 = Poor (perceptible, frequently annoying)
  1.0 = Bad (very annoying, unintelligible)

MOS Calculation:
MOS = 4.45 - (4.45 × D / 100) - R
  D = Delay in ms
  R = Concealments per second

Target: > 3.5 for acceptable voice quality
       > 4.0 for good quality
       > 4.3 for excellent quality

Network requirements:
  Latency: < 150 ms
  Loss: < 1%
  Jitter: < 50 ms
```

## Capacity Metrics

### Interface Saturation
```
Definition: Operating point relative to capacity
Metric: Percentage of link capacity
  0-50%: Healthy
  50-70%: Monitor
  70-85%: Caution
  85-95%: Warning
  >95%: Critical

Example:
  1 Gbps link with 900 Mbps sustained = 90% saturation
```

### Queue Depth
```
Definition: Number of packets awaiting transmission
Metric: Packets or bytes in queue
Target: Minimal queue depth (<100 packets)
Rising: Indicates congestion
Sustained: Need capacity increase
```

### Dropped Packets
```
Definition: Packets discarded due to congestion
Source: Queue overflow, policer, WRED
Target: 0 packets dropped
Monitoring: Ifoutdiscards, Ifindiscards (SNMP)
Trending: Predict need for capacity increase
```

## Business Metrics

### User Experience Metrics

#### Page Load Time
```
Definition: Time to render complete webpage
Target: < 1 second (perceived instantaneous)
       < 3 seconds (good experience)
       > 5 seconds (user abandon)

Components:
- DNS resolution
- TCP connection
- TLS handshake
- HTTP request/response
- Rendering
```

#### Application Responsiveness
```
Definition: Perceived lag from user perspective
Target: < 200 ms (imperceptible)
       < 500 ms (noticeable but acceptable)
       > 1000 ms (unacceptable)
```

### Availability Impact Metrics

#### Business Hours Availability
```
Definition: Availability during business hours only
Example:
  All-time: 99.0%
  Business hours (9-5): 99.95%
  After-hours: 95%

Calculation: Weighted average by time period
```

## Implementation Checklist

- [ ] Define baseline performance metrics
- [ ] Establish alert thresholds
- [ ] Implement measurement tools
- [ ] Create dashboards for KPI visualization
- [ ] Set up automated alerting
- [ ] Establish SLA targets
- [ ] Configure trending and reporting
- [ ] Schedule regular reviews
- [ ] Correlate KPIs with business impact
- [ ] Document metric definitions
- [ ] Train team on KPI interpretation
- [ ] Plan capacity based on KPI trends

---

**Reference Type**: Performance Standards
**Primary Use**: Service Level monitoring and planning
**Review Interval**: Weekly (trending), Monthly (trends)
**Last Updated**: 2025-11-19
