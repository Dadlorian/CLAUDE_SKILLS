# Prometheus Network Monitoring Reference

## Prometheus Architecture for Networks

### Components

```
Network Devices
    ↓ (SNMP, gRPC, HTTP)
Exporters (SNMP Exporter, Node Exporter, etc.)
    ↓
Prometheus Scraper (Pull Model)
    ↓
Time Series Database (TSDB)
    ↓
Query Engine & Alerting
    ↓
Grafana Visualization
```

## SNMP Exporter Configuration

### Installation & Setup
```bash
# Download and install
wget https://github.com/prometheus/snmp_exporter/releases/download/v0.24.0/snmp_exporter-0.24.0.linux-amd64.tar.gz
tar xzf snmp_exporter-0.24.0.linux-amd64.tar.gz
cd snmp_exporter-0.24.0.linux-amd64

# Generate config from MIBs
./snmp_exporter/generator generate
```

### snmp.yml Configuration

#### Basic Device Monitoring
```yaml
modules:
  if_mib:
    walk:
      - sysDescr
      - sysUptime
      - interfaces
    get:
      - sysDescr.0
    metrics:
      - name: sysUptime
        oid: 1.3.6.1.2.1.1.3
        type: gauge
        help: System uptime
      - name: ifInOctets
        oid: 1.3.6.1.2.1.2.2.1.10
        type: counter
        help: Input octets
      - name: ifOutOctets
        oid: 1.3.6.1.2.1.2.2.1.16
        type: counter
        help: Output octets
      - name: ifInErrors
        oid: 1.3.6.1.2.1.2.2.1.14
        type: counter
        help: Input errors
      - name: ifOutErrors
        oid: 1.3.6.1.2.1.2.2.1.20
        type: counter
        help: Output errors

  snmpv3:
    version: 3
    security_level: authPriv
    username: monitoring
    auth_protocol: SHA
    auth_password: ${SNMP_AUTH_PASSWORD}
    priv_protocol: AES
    priv_password: ${SNMP_PRIV_PASSWORD}
    context_name: ""

  router_metrics:
    walk:
      - 1.3.6.1.2.1.1
      - 1.3.6.1.2.1.2
      - 1.3.6.1.2.1.25
    metrics:
      - name: sysName
        oid: 1.3.6.1.2.1.1.5
        type: OctetString
```

### Prometheus Scrape Configuration

#### Static Targets
```yaml
scrape_configs:
  - job_name: 'snmp_routers'
    static_configs:
      - targets:
          - 192.168.1.1
          - 192.168.1.2
        labels:
          site: 'main'
          type: 'router'
    metrics_path: /snmp
    params:
      module: [if_mib]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9116
```

#### Dynamic Discovery (File-based)
```yaml
scrape_configs:
  - job_name: 'snmp_devices'
    file_sd_configs:
      - files:
          - 'targets/snmp_devices.json'
        refresh_interval: 5m
    metrics_path: /snmp
    params:
      module: [if_mib]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9116
```

#### Dynamic Discovery (Consul)
```yaml
scrape_configs:
  - job_name: 'snmp_consul'
    consul_sd_configs:
      - server: 'localhost:8500'
        datacenter: 'dc1'
    metrics_path: /snmp
    params:
      module: [if_mib]
```

## Network Metrics

### Standard Network Metrics

#### Interface Metrics
```
# Interface status
node_network_up{device="eth0"} 1        # 1=up, 0=down

# Interface counters (per second)
rate(ifInOctets[5m])                    # Input throughput
rate(ifOutOctets[5m])                   # Output throughput
rate(ifInErrors[5m])                    # Input errors/sec
rate(ifOutErrors[5m])                   # Output errors/sec
rate(ifInDiscards[5m])                  # Input discards/sec

# Link utilization
(rate(ifInOctets[5m])*8) / ifSpeed * 100
```

#### Device Health
```
# System uptime
sysUptime / 100 seconds (for centiseconds)

# CPU utilization
sysLoad5 / sysLoadAverage * 100

# Memory utilization
(hrStorageUsed / hrStorageSize) * 100
```

### Custom Network Exporters

#### Node Exporter for Network Metrics
```yaml
# Scrape node exporter for OS metrics
scrape_configs:
  - job_name: 'node_networks'
    static_configs:
      - targets: ['localhost:9100']
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: 'node_network_.*'
        action: keep
```

#### Cisco Device Exporter Example
```python
from prometheus_client import start_http_server, Gauge, Counter
import netmiko
import time

# Define metrics
interface_status = Gauge('cisco_interface_status',
    'Interface up/down status',
    ['device', 'interface'])
interface_throughput = Gauge('cisco_interface_throughput_bps',
    'Interface throughput in bits/second',
    ['device', 'interface', 'direction'])

def collect_metrics():
    device = {
        'device_type': 'cisco_ios',
        'host': '192.168.1.1',
        'username': 'admin',
        'password': 'password'
    }

    conn = netmiko.ConnectHandler(**device)
    output = conn.send_command('show interfaces')

    # Parse and populate metrics
    # ... parsing logic ...

    conn.disconnect()

if __name__ == '__main__':
    start_http_server(8000)
    while True:
        collect_metrics()
        time.sleep(60)
```

## PromQL Queries for Network Monitoring

### Basic Queries

#### Current Interface Status
```promql
# Find all down interfaces
node_network_up == 0

# Find interfaces with errors
rate(ifInErrors[5m]) > 0
```

#### Bandwidth Utilization
```promql
# Calculate percentage utilization
(rate(ifInOctets[5m]) * 8) / ifSpeed * 100

# Interfaces over 70% utilization
((rate(ifInOctets[5m]) + rate(ifOutOctets[5m])) * 8 / ifSpeed) > 0.7
```

#### Packet Loss Detection
```promql
# Input error rate
rate(ifInErrors[5m]) / rate(ifInPackets[5m]) > 0.001

# Output error rate
rate(ifOutErrors[5m]) / rate(ifOutPackets[5m]) > 0.001
```

### Advanced Queries

#### Traffic Growth Trending
```promql
# Weekly growth rate
(rate(ifInOctets[1w] offset 0h) - rate(ifInOctets[1w] offset 1w))
/ rate(ifInOctets[1w] offset 1w) * 100
```

#### Top Talkers
```promql
# Top 5 interfaces by input traffic
topk(5, rate(ifInOctets[5m]) * 8)
```

#### Device Health Score
```promql
# Combined health metric (0-100)
(
  (sysUptime > 3600 ? 100 : 0) +
  (rate(ifInErrors[5m]) == 0 ? 100 : 0) +
  (node_memory_MemFree_bytes > 1e9 ? 100 : 0)
) / 3
```

## Recording Rules

### Pre-computed Metrics
```yaml
groups:
  - name: network_recording_rules
    interval: 15s
    rules:
      # Interface bandwidth utilization
      - record: network:interface_utilization:pct
        expr: |
          ((rate(ifInOctets[5m]) + rate(ifOutOctets[5m])) * 8 / ifSpeed) * 100

      # Interface error rate
      - record: network:interface_error_rate:pct
        expr: |
          ((rate(ifInErrors[5m]) + rate(ifOutErrors[5m])) /
           (rate(ifInPackets[5m]) + rate(ifOutPackets[5m]))) * 100

      # Per-device bandwidth
      - record: network:device_bandwidth:bytes_per_sec
        expr: |
          sum by (instance) (rate(ifInOctets[5m]) + rate(ifOutOctets[5m]))

      # Interface availability
      - record: network:interface_availability:pct
        expr: |
          (count by (device) (node_network_up == 1) /
           count by (device) (node_network_up)) * 100
```

## Alerting Rules

### Critical Alerts
```yaml
groups:
  - name: network_alerts
    rules:
      # Interface down
      - alert: InterfaceDown
        expr: node_network_up == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Interface {{ $labels.device }} is down"
          description: "Interface has been down for > 2 minutes"

      # High error rate
      - alert: HighPacketErrorRate
        expr: |
          rate(ifInErrors[5m]) + rate(ifOutErrors[5m]) > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate on {{ $labels.instance }}"

      # Link saturation
      - alert: LinkSaturation
        expr: |
          ((rate(ifInOctets[5m]) + rate(ifOutOctets[5m])) * 8 / ifSpeed) > 0.85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "{{ $labels.instance }} link utilization > 85%"
          description: "Current utilization: {{ humanize $value }}%"
```

## Troubleshooting Common Issues

### Metric Not Appearing
```
1. Verify exporter is running and responding
   curl http://localhost:9116/snmp?module=if_mib&target=192.168.1.1

2. Check Prometheus scrape logs
   curl http://localhost:9090/api/v1/status/runtimes

3. Verify SNMP community/credentials are correct
   snmpwalk -v 2c -c public 192.168.1.1 sysDescr

4. Check OID path is correct
   snmptranslate -On IF-MIB::ifInOctets
```

### High Cardinality Issues
```
1. Use metric_relabel_configs to drop unnecessary labels
2. Group by higher-level dimensions
3. Use recording rules for pre-aggregation
4. Monitor cardinality
   rate(prometheus_tsdb_symbol_table_size_bytes[5m])
```

### Performance Optimization
```yaml
# Reduce scrape frequency for non-critical jobs
scrape_configs:
  - job_name: 'snmp_devices'
    scrape_interval: 2m      # Instead of 15s
    scrape_timeout: 30s

# Use metric relabeling to reduce storage
metric_relabel_configs:
  - source_labels: [__name__]
    regex: 'go_.*'
    action: drop
```

## Implementation Checklist

- [ ] Install Prometheus and SNMP exporter
- [ ] Generate SNMP exporter configuration from MIBs
- [ ] Configure SNMPv3 credentials
- [ ] Create Prometheus scrape configuration
- [ ] Verify metrics are being collected
- [ ] Create recording rules for common queries
- [ ] Define alerting rules
- [ ] Test alerting notifications
- [ ] Build Grafana dashboards
- [ ] Configure data retention
- [ ] Set up backup procedures
- [ ] Document custom exporters

---

**Reference Type**: Prometheus Configuration
**Primary Use**: Time series metrics collection
**Data Retention**: 2 weeks (default), configurable
**Last Updated**: 2025-11-19
