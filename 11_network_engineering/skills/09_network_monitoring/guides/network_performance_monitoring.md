# Network Performance Monitoring Guide

## Performance Baseline Establishment

### Step 1: Define Baseline Period
```
Duration: 2-4 weeks of normal operation
Avoid: Maintenance windows, planned changes
Sample: Representative week (different days/times)

Metrics to capture:
  - Interface throughput (input/output)
  - Bandwidth utilization %
  - Latency (ping RTT)
  - Packet loss
  - Error rates
```

### Step 2: Collect Baseline Data

#### Using SNMP
```bash
# Script to collect interface stats
#!/bin/bash

TARGET_IP="192.168.1.1"
INTERFACE="GigabitEthernet0/0"
OUTPUT_FILE="baseline_$(date +%Y%m%d).txt"

# Collect every 5 minutes for 24 hours
for i in {1..288}; do
  echo "=== Sample $i at $(date) ===" >> $OUTPUT_FILE

  # Get interface stats
  snmpget -v 3 -u monitoring -a SHA -A pass1 \
    -x AES -X pass2 \
    $TARGET_IP \
    1.3.6.1.2.1.2.2.1.16.$INTERFACE \
    1.3.6.1.2.1.2.2.1.20.$INTERFACE \
    >> $OUTPUT_FILE

  sleep 300  # 5 minutes
done
```

#### Using Prometheus Queries
```yaml
# Export baseline queries
queries:
  - name: "interface_throughput"
    query: "rate(ifInOctets[5m]) * 8"  # bits per second
    scrape_interval: 5m

  - name: "interface_utilization"
    query: "((rate(ifInOctets[5m]) + rate(ifOutOctets[5m])) * 8 / ifSpeed) * 100"
    scrape_interval: 5m

  - name: "packet_loss"
    query: "rate(ifInErrors[5m]) / rate(ifInPackets[5m])"
    scrape_interval: 5m
```

### Step 3: Analyze Baseline

#### Calculate Percentiles
```
Throughput baseline:
  p50 (median): 500 Mbps
  p95: 1.2 Gbps
  p99: 1.8 Gbps
  Max: 2.4 Gbps

Utilization baseline:
  Average: 25%
  Peak: 60%
  Safe threshold: 70% (alert at 80%)

Latency baseline:
  p50: 15 ms
  p95: 25 ms
  p99: 35 ms
```

#### Create Baseline Report
```
Network Link Baseline Report
Generated: [date]
Link: Internet Uplink (10 Gbps)
Collection Period: 2 weeks

Throughput:
  Average: 2.3 Gbps
  Peak: 8.9 Gbps (peak hours)
  Min: 0.5 Gbps (off-hours)
  Growth rate: +5%/month

Utilization:
  Average: 23%
  95th percentile: 59%
  99th percentile: 78%
  Peak: 89%

Error rate:
  Average: 0.0% packet loss
  Max: 0.02% (momentary spike)
  CRC errors: 0
  Discards: 0

Latency:
  Average RTT: 18 ms
  99th percentile: 32 ms
  Jitter: 2 ms
```

## Performance Trending

### Set Up Trend Analysis

#### Prometheus Recording Rules
```yaml
groups:
  - name: network_trends
    interval: 1h
    rules:
      # Monthly average
      - record: network:interface_throughput:30d_avg
        expr: avg_over_time(rate(ifInOctets[5m])[30d:1h])

      # Growth rate (week-over-week)
      - record: network:interface_growth:wow
        expr: |
          (avg_over_time(rate(ifInOctets[5m])[7d] offset 0d) -
           avg_over_time(rate(ifInOctets[5m])[7d] offset 7d)) /
          avg_over_time(rate(ifInOctets[5m])[7d] offset 7d) * 100

      # Utilization trend
      - record: network:link_utilization:trend
        expr: |
          ((rate(ifInOctets[5m]) + rate(ifOutOctets[5m])) * 8 / ifSpeed) * 100
```

#### Grafana Trend Visualization
```json
{
  "dashboard": {
    "title": "Network Trend Analysis",
    "panels": [
      {
        "title": "Monthly Throughput Trend",
        "type": "time_series",
        "targets": [
          {
            "expr": "rate(ifInOctets[5m])",
            "range": "180d",
            "step": "24h"
          }
        ],
        "fieldConfig": {
          "custom": {
            "lineWidth": 2,
            "drawStyle": "line"
          }
        }
      },
      {
        "title": "Growth Rate (%)​",
        "type": "stat",
        "targets": [
          {
            "expr": "network:interface_growth:wow"
          }
        ]
      }
    ]
  }
}
```

## Bottleneck Identification

### Systematic Approach

#### Step 1: Identify Congestion Points
```
Tools:
  - Interface utilization graphs
  - NetFlow top talkers
  - Packet capture analysis
  - Path analysis (traceroute)

Look for:
  - Interfaces consistently >70% utilized
  - Traffic spikes at specific times
  - Traffic concentration (backbone vs access)
  - Asymmetric traffic patterns
```

#### Step 2: Trace Traffic Path
```bash
# Identify bottleneck device
# 1. Source IP: 10.0.1.10
# 2. Destination: 8.8.8.8

traceroute -m 15 8.8.8.8
# Output:
# 1  10.0.1.1        gateway
# 2  10.0.0.1        router1
# 3  10.0.0.254      router2 (CONGESTED - high latency)
# 4  ISP.12.34        ISP
# ...

# Verify with packet capture on router2
tcpdump -i gi0/0 -w trace_router2.pcap 'host 10.0.1.10 and 8.8.8.8'
```

#### Step 3: Validate Root Cause
```
Likely causes of congestion:
  1. Bandwidth limitation
     - Interface speed too low
     - Multiple flows sharing link
     - Application generating excessive traffic

  2. Latency issues
     - Geographical distance
     - Processing delays
     - Queue buildup

  3. Quality of service
     - No QoS configured
     - Wrong priority marking
     - Insufficient buffer space
```

## Performance Optimization Strategies

### Bandwidth Optimization

#### Identify Top Talkers
```bash
# NetFlow query (Elasticsearch)
GET netflow-*/_search
{
  "query": {
    "range": {
      "@timestamp": { "gte": "now-7d" }
    }
  },
  "aggs": {
    "top_sources": {
      "terms": {
        "field": "netflow.ipv4_src_addr",
        "size": 10
      }
    }
  }
}
```

#### Implement Traffic Shaping
```
Cisco IOS:
  ! Create class map
  class-map match-all BULK_TRAFFIC
    match dscp af31

  ! Create policy
  policy-map TRAFFIC_POLICY
    class BULK_TRAFFIC
      police rate 500 mbps

  ! Apply to interface
  interface GigabitEthernet0/1
    service-policy output TRAFFIC_POLICY
```

### Latency Optimization

#### Monitor Latency Spikes
```
Prometheus alert:
  - alert: HighLatency
    expr: histogram_quantile(0.95, latency_ms) > 100
    for: 5m
    action: Investigate and prioritize

Investigation:
  1. Check interface utilization
  2. Check for packet loss
  3. Verify routing stability
  4. Check application load
```

#### Path Optimization
```
BGP path selection:
  1. Measure performance on multiple paths
  2. Use BGP prepend/communities to influence routing
  3. Monitor performance improvement

Example:
  Path A: 50ms latency, but 2% loss
  Path B: 80ms latency, but 0% loss
  Decision: Prefer Path B for quality

Implementation:
    route-map PREFER_STABLE permit 10
      set local-preference 200
    route-map ACCEPT_LOSS permit 10
      set local-preference 100
```

## Alerting Strategy

### Performance-Based Alerts

#### Critical Alerts
```yaml
- alert: LinkSaturation
  expr: ((rate(ifInOctets[5m]) + rate(ifOutOctets[5m])) * 8 / ifSpeed) > 0.95
  for: 5m
  # Immediate action needed

- alert: HighPacketLoss
  expr: rate(ifInErrors[5m]) / rate(ifInPackets[5m]) > 0.01
  for: 2m
  # 1% loss is critical
```

#### Warning Alerts
```yaml
- alert: IncreasingCongestion
  expr: |
    rate(network:interface_throughput:30d_avg[7d]) >
    rate(network:interface_throughput:30d_avg[7d] offset 7d) * 1.1
  for: 1h
  # More than 10% week-over-week growth
```

## Capacity Planning

### Forecast Demand
```
Method 1: Linear Trend
  Current: 2 Gbps
  Growth: 5%/month
  Timeline:
    3 months: 2.3 Gbps
    6 months: 2.6 Gbps
    12 months: 3.1 Gbps

Method 2: Exponential Growth
  If growth accelerating, use exponential model
  y = a * e^(bx)

Method 3: Seasonal Analysis
  Account for business cycles
  Q4 higher than Q2
  Adjust for anomalies
```

### Plan for Upgrades
```
Upgrade triggers:
  1. Projected to exceed 80% capacity in 6 months
  2. P99 utilization already at 80%
  3. Growth rate accelerating

Pre-upgrade validation:
  1. Order equipment 3-6 months early
  2. Test in lab
  3. Plan maintenance window
  4. Execute and monitor
  5. Document new baselines
```

## Implementation Checklist

- [ ] Establish performance baseline
- [ ] Define KPI targets
- [ ] Set up trend analysis
- [ ] Create performance dashboards
- [ ] Configure performance alerts
- [ ] Document baselines
- [ ] Establish review cadence (monthly)
- [ ] Identify bottlenecks
- [ ] Plan optimization efforts
- [ ] Forecast capacity needs
- [ ] Create upgrade plan
- [ ] Monitor improvement

---

**Guide Type**: Performance Analysis
**Tools**: Prometheus, Grafana, NetFlow, packet capture
**Use Case**: Network optimization and capacity planning
**Review Frequency**: Monthly
**Last Updated**: 2025-11-19
