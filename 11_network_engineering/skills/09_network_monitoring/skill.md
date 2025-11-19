# Network Monitoring & Observability Subskill

## Overview
Complete mastery of network monitoring, observability platforms, and performance measurement technologies for enterprise network operations.

## Core Competencies

### 1. SNMP (Simple Network Management Protocol)
- **SNMPv1, v2c, v3 configuration** - Protocol versions and backward compatibility
- **MIB (Management Information Base)** - Standard and custom MIBs, OID hierarchies
- **SNMP traps and notifications** - Event-driven monitoring, trap handling
- **Community strings and security** - Authentication, privacy, access controls
- **Polling strategies** - Interval optimization, threshold detection

### 2. NetFlow & Flow Analysis
- **NetFlow v5, v9, IPFIX** - Version differences and capabilities
- **Flow data collection** - Exporter configuration, sampling strategies
- **Traffic analysis** - Application identification, bandwidth accounting
- **Flow analytics** - Top talkers, protocol distribution, traffic patterns
- **Flow storage and analysis** - Database design, query optimization

### 3. Streaming Telemetry
- **gRPC and subscription models** - Push-based telemetry
- **Model-driven telemetry** - YANG data models, NETCONF/RESTCONF
- **Cisco Streaming Telemetry** - IOS-XE, IOS-XR platforms
- **Junos Telemetry Interface (JTI)** - Juniper implementations
- **OpenConfig and standard schemas** - Vendor-neutral models

### 4. Syslog & Event Management
- **Syslog protocol (RFC 3164/5424)** - Message format, severity levels
- **Syslog servers and aggregation** - Centralized logging infrastructure
- **Log parsing and correlation** - Structured logging, log processing
- **Event classification** - Alert severity, impact analysis
- **Log retention and archival** - Compliance, storage optimization

### 5. Packet Capture & Analysis
- **Tcpdump and WinDump** - Packet capture tools and filters
- **Wireshark analysis** - Deep packet inspection, protocol analysis
- **Display filters and capture filters** - Advanced filtering techniques
- **Packet forensics** - Evidence collection, investigation techniques
- **Payload analysis** - Content inspection, security analysis

### 6. Network KPIs & Metrics
- **Latency measurement** - RTT, jitter, MOS
- **Throughput and bandwidth** - Actual vs provisioned, saturation analysis
- **Packet loss monitoring** - Loss rate, packet error detection
- **Availability metrics** - Uptime percentage, MTBF/MTTR
- **Application performance** - Response time, transaction tracking

### 7. Observability Platforms

#### Prometheus for Network Monitoring
- **Network exporters** - SNMP exporter, network device exporters
- **Custom metrics** - Application-specific metrics, derived metrics
- **Time series storage** - Retention, compression, optimization
- **Querying and alerting** - PromQL, alert rules, routing

#### Grafana Dashboard Design
- **Network visualization** - Topology maps, flow diagrams
- **Real-time dashboards** - Auto-refresh, interactive elements
- **Dashboard templates** - Reusable components, standardization
- **Alerting integration** - Alert annotations, incident tracking

#### ELK Stack Integration
- **Logstash pipelines** - Network log processing, field extraction
- **Elasticsearch indexing** - Log storage, search optimization
- **Kibana visualization** - Log analysis, correlation searching

### 8. Advanced Monitoring Tools
- **Neteye and network automation** - Integrated monitoring platforms
- **Telegraf and Influx** - Metrics collection and time series database
- **NetBox integration** - Network IPAM and monitoring correlation
- **Splunk for network analytics** - Enterprise log and metrics platform
- **Datadog and cloud monitoring** - Cloud-native observability

### 9. Network Troubleshooting Methodology
- **Layered diagnostics** - Bottom-up and top-down approaches
- **Baseline establishment** - Historical data, anomaly detection
- **Root cause analysis** - Systematic elimination, correlation analysis
- **Performance optimization** - Bottleneck identification and resolution
- **Incident response** - Triage, escalation, documentation

### 10. Observability Best Practices
- **Instrumentation strategy** - What to monitor, sampling decisions
- **Metric design** - Cardinality management, aggregation
- **Alert tuning** - False positive reduction, alert fatigue prevention
- **Data retention** - Storage costs vs visibility tradeoffs
- **Security and privacy** - Data protection, sensitive field masking

## Reference Materials

### Key Documents
- **SNMP Monitoring Reference** - Protocol details, OID management
- **NetFlow/sFlow/IPFIX Reference** - Flow data standards
- **Streaming Telemetry Reference** - Push-based data collection
- **Syslog Reference** - Log message standards
- **Packet Capture Reference** - Capture techniques and analysis
- **Network KPIs Reference** - Metric definitions and targets
- **Monitoring Tools Comparison** - Feature matrix and selection criteria
- **Prometheus Network Monitoring** - Exporter configuration
- **Grafana Dashboards Reference** - Dashboard best practices
- **Wireshark Reference** - Protocol dissectors and analysis
- **Network Troubleshooting Tools** - Diagnostic tool reference
- **Observability Best Practices** - Industry standards

## Implementation Guides

### Configuration Guides
1. **SNMP Deployment Guide** - End-to-end SNMP setup
2. **NetFlow Implementation Guide** - NetFlow collector setup
3. **Streaming Telemetry Guide** - Telemetry configuration
4. **Network Observability Guide** - Full observability implementation
5. **ELK Stack Network Monitoring** - Log processing pipeline

### Platform Guides
6. **Prometheus & Grafana Setup** - Complete monitoring stack
7. **Packet Capture Analysis Guide** - Tcpdump and Wireshark
8. **Syslog Centralization Guide** - Log aggregation architecture
9. **Network Performance Monitoring** - Performance metrics strategy
10. **Network Alerting Guide** - Alert rule design and management

### Advanced Guides
11. **Capacity Planning Guide** - Growth projection and trending
12. **Troubleshooting Methodology** - Systematic problem-solving

## Implementation Resources

### Configuration Files
- SNMPv3 configuration templates
- NetFlow exporter configurations
- sFlow and IPFIX setups
- Streaming telemetry configs
- Prometheus/Grafana configurations
- Telegraf network monitoring configs
- ELK Stack pipeline definitions

### Automation Scripts
- SNMP monitoring and discovery scripts
- NetFlow analyzer implementations
- Packet capture automation
- Network baseline monitoring
- Syslog parsing utilities
- Network health check scripts
- Bandwidth and latency monitoring
- Wireshark filter templates
- Troubleshooting automation scripts

### Configuration Standards
- Display filter templates
- Capture filter examples
- tcpdump command reference
- Syslog format patterns

## Monitoring Architecture

### Pull-Based (SNMP)
```
NMS (Network Management System)
    ↓ SNMP GET/WALK
Device Agents (SNMP v1/v2c/v3)
    ↓ Traps
NMS Trap Receiver
```

### Push-Based (Streaming Telemetry)
```
Network Devices (Telemetry Agents)
    ↓ gRPC/UDP Streaming
Telemetry Collectors
    ↓
Time Series Database/Message Queue
    ↓
Analytics & Dashboards
```

### Flow-Based (NetFlow)
```
Network Devices (Flow Exporters)
    ↓ NetFlow v9/IPFIX
Flow Collector
    ↓
Flow Database
    ↓
Flow Analysis & Reporting
```

### Log-Based (Syslog)
```
Network Devices (Syslog Agents)
    ↓ Syslog (UDP 514 / TCP 514/601)
Syslog Server
    ↓ Logstash Processing
Elasticsearch
    ↓
Kibana/Analytics
```

## Key Technologies & Versions

### Protocol Versions
- **SNMP**: v1, v2c, v3 (current standard)
- **NetFlow**: v5, v9, IPFIX (RFC 7011)
- **Syslog**: RFC 3164 (legacy), RFC 5424 (current)
- **Telemetry**: NETCONF (RFC 6241), YANG (RFC 6020)

### Monitoring Platforms
- **Prometheus**: Time series database + alerting
- **Grafana**: Visualization layer
- **Elasticsearch + Logstash + Kibana (ELK)**: Log aggregation
- **Influx + Telegraf**: Agent-based metrics collection
- **NetBox**: IPAM and network source of truth

### Tools & Utilities
- **Tcpdump/WinDump**: Packet capture
- **Wireshark**: Interactive packet analysis
- **Neteye**: Integrated monitoring platform
- **Netmiko**: Network device automation
- **Scapy**: Packet manipulation library

## Troubleshooting Common Monitoring Issues

### Issue 1: SNMP Timeout or No Response

**Symptoms**:
- SNMP queries timeout
- "No Response from" errors in NMS
- Incomplete device data

**Diagnostic Steps**:
```bash
# Test SNMP connectivity
snmpwalk -v2c -c public 192.168.1.1 system

# Check specific OID
snmpget -v2c -c public 192.168.1.1 1.3.6.1.2.1.1.1.0

# Test SNMPv3
snmpwalk -v3 -l authPriv -u admin -a SHA -A authpass -x AES -X privpass \
  192.168.1.1 system

# Verify UDP port 161 is open
nmap -sU -p 161 192.168.1.1
```

**Solutions**:
- Verify SNMP is enabled on device: `show snmp` (Cisco)
- Check community string or SNMPv3 credentials
- Verify ACLs allow SNMP from monitoring server
- Increase timeout values in NMS configuration
- Check firewall rules between NMS and device
- Ensure correct SNMP version (v1/v2c/v3)

### Issue 2: NetFlow Data Not Received

**Symptoms**:
- No flow data in collector
- Incomplete traffic statistics
- Missing flow records

**Diagnostic Steps**:
```bash
# Check NetFlow collector is listening
netstat -uan | grep 2055

# Verify flow export configuration on device
show ip flow export  # Cisco IOS
show flow-export     # Juniper

# Capture NetFlow packets
tcpdump -i eth0 udp port 2055 -vv

# Test flow export manually
# On collector
nfdump -l /var/cache/nfdump/flows

# Check flow statistics
nfdump -R /var/cache/nfdump/flows -s srcip -n 10
```

**Solutions**:
- Configure flow export on device:
  ```
  # Cisco IOS
  ip flow-export destination 192.168.1.100 2055
  ip flow-export version 9
  interface GigabitEthernet0/1
    ip flow ingress
  ```
- Verify collector is running and listening
- Check sampling rate (1:100, 1:1000)
- Ensure firewall allows UDP port 2055
- Verify flow cache size is adequate
- Check for packet loss between device and collector

### Issue 3: Missing or Incorrect Metrics in Prometheus

**Symptoms**:
- Gaps in time series data
- "No data" in Grafana dashboards
- Stale metrics

**Diagnostic Steps**:
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Query specific metric
curl 'http://localhost:9090/api/v1/query?query=up'

# Check exporter health
curl http://exporter-host:9100/metrics

# View Prometheus logs
journalctl -u prometheus -f

# Check scrape configuration
promtool check config /etc/prometheus/prometheus.yml
```

**Solutions**:
- Verify exporter is running and accessible
- Check scrape interval and timeout settings
  ```yaml
  scrape_configs:
    - job_name: 'network_devices'
      scrape_interval: 60s
      scrape_timeout: 30s
      static_configs:
        - targets: ['192.168.1.1:9100']
  ```
- Ensure network connectivity to exporters
- Check for certificate issues (HTTPS exporters)
- Verify authentication credentials
- Increase retention period if historical data missing
- Check storage capacity

### Issue 4: Syslog Messages Not Being Received

**Symptoms**:
- Missing log entries
- Logs appear on device but not in syslog server
- Partial log collection

**Diagnostic Steps**:
```bash
# Check syslog server is listening
netstat -uan | grep 514

# Test syslog reception
logger -n syslog-server -P 514 "Test message"

# Monitor syslog in real-time
tail -f /var/log/syslog

# Check device syslog configuration
show logging  # Cisco
show log      # Juniper

# Capture syslog packets
tcpdump -i eth0 port 514 -A
```

**Solutions**:
- Configure syslog on network devices:
  ```
  # Cisco IOS
  logging host 192.168.1.100
  logging trap informational
  logging source-interface GigabitEthernet0/0
  ```
- Verify syslog daemon is running
  ```bash
  systemctl status rsyslog
  ```
- Check firewall allows UDP/TCP port 514
- Ensure correct facility and severity levels
- Verify log rotation not causing data loss
- Use TCP instead of UDP for reliability
- Check disk space on syslog server

### Issue 5: High CPU/Memory on Monitoring Server

**Symptoms**:
- Slow dashboard loading
- Query timeouts
- Monitoring server unresponsive

**Diagnostic Steps**:
```bash
# Check resource usage
top
htop

# Prometheus resource usage
ps aux | grep prometheus

# Check data size
du -sh /var/lib/prometheus/data

# Query performance
curl 'http://localhost:9090/api/v1/query?query=prometheus_tsdb_head_series'

# Check cardinality
curl http://localhost:9090/api/v1/status/tsdb
```

**Solutions**:
- Reduce data retention period
  ```bash
  --storage.tsdb.retention.time=15d
  ```
- Decrease scrape frequency for less critical metrics
- Use recording rules for expensive queries
  ```yaml
  groups:
    - name: network_rules
      interval: 60s
      rules:
        - record: network:interface_bytes_total:rate5m
          expr: rate(interface_bytes_total[5m])
  ```
- Implement metric filtering/relabeling
- Scale horizontally (Prometheus federation)
- Upgrade server resources
- Use remote storage for long-term data

## Practical Implementation Examples

### Example 1: Complete Prometheus + Grafana Setup for Network Monitoring

```yaml
# prometheus.yml
global:
  scrape_interval: 60s
  evaluation_interval: 60s

scrape_configs:
  # SNMP Exporter for network devices
  - job_name: 'snmp'
    static_configs:
      - targets:
        - 192.168.1.1  # Router 1
        - 192.168.1.2  # Switch 1
        - 192.168.1.3  # Firewall 1
    metrics_path: /snmp
    params:
      module: [if_mib]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9116  # SNMP exporter address

  # Blackbox exporter for connectivity monitoring
  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [icmp]
    static_configs:
      - targets:
        - 8.8.8.8
        - 1.1.1.1
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - target_label: __address__
        replacement: localhost:9115

# Alert rules
rule_files:
  - 'alerts/*.yml'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']
```

```yaml
# alerts/network_alerts.yml
groups:
  - name: network_alerts
    rules:
      - alert: InterfaceDown
        expr: ifOperStatus == 2
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Interface {{ $labels.ifDescr }} is down"
          description: "Interface {{ $labels.ifDescr }} on {{ $labels.instance }} has been down for 5 minutes"

      - alert: HighInterfaceUtilization
        expr: rate(ifHCInOctets[5m]) * 8 / ifHighSpeed > 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High interface utilization on {{ $labels.ifDescr }}"
          description: "Interface utilization is above 80% for 10 minutes"

      - alert: DeviceUnreachable
        expr: probe_success == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Device {{ $labels.instance }} is unreachable"
          description: "Failed to ping {{ $labels.instance }} for 5 minutes"
```

### Example 2: ELK Stack for Network Log Analysis

```yaml
# logstash/conf.d/10-syslog-input.conf
input {
  tcp {
    port => 5514
    type => syslog
  }
  udp {
    port => 5514
    type => syslog
  }
}

filter {
  if [type] == "syslog" {
    grok {
      match => {
        "message" => "%{SYSLOGTIMESTAMP:syslog_timestamp} %{SYSLOGHOST:hostname} %{DATA:program}(?:\[%{POSINT:pid}\])?: %{GREEDYDATA:message}"
      }
      overwrite => [ "message" ]
    }

    # Parse Cisco logs
    if [program] =~ "SEC-6-IPACCESSLOG" {
      grok {
        match => {
          "message" => "list %{NOTSPACE:acl_name} %{WORD:action} %{WORD:protocol} %{IP:src_ip}\(%{INT:src_port}\) -> %{IP:dst_ip}\(%{INT:dst_port}\)"
        }
      }
    }

    # GeoIP for source IPs
    geoip {
      source => "src_ip"
      target => "src_geoip"
    }

    date {
      match => [ "syslog_timestamp", "MMM  d HH:mm:ss", "MMM dd HH:mm:ss" ]
      timezone => "UTC"
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "network-logs-%{+YYYY.MM.dd}"
  }
}
```

### Example 3: Python Script for Network Baseline Monitoring

```python
#!/usr/bin/env python3
"""
Network baseline monitoring and anomaly detection
Collects interface metrics and detects deviations from baseline
"""

from pysnmp.hlapi import *
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

class NetworkBaselineMonitor:
    def __init__(self, devices):
        self.devices = devices
        self.baselines = defaultdict(dict)
        self.history = defaultdict(list)

    def get_interface_metrics(self, device, community='public'):
        """Collect interface metrics via SNMP"""
        metrics = {}

        # Interface names
        oid_ifDescr = '1.3.6.1.2.1.2.2.1.2'
        # Interface status
        oid_ifOperStatus = '1.3.6.1.2.1.2.2.1.8'
        # Interface counters
        oid_ifInOctets = '1.3.6.1.2.1.31.1.1.1.6'
        oid_ifOutOctets = '1.3.6.1.2.1.31.1.1.1.10'

        for (errorIndication, errorStatus, errorIndex, varBinds) in bulkCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((device, 161)),
            ContextData(),
            0, 50,
            ObjectType(ObjectIdentity(oid_ifDescr)),
            lexicographicMode=False
        ):
            if errorIndication or errorStatus:
                print(f"SNMP error: {errorIndication or errorStatus}")
                continue

            for varBind in varBinds:
                oid, value = varBind
                if_index = oid[-1]
                metrics[if_index] = {'ifDescr': str(value)}

        return metrics

    def calculate_baseline(self, interface_id, samples_needed=20):
        """Calculate baseline from historical data"""
        history = self.history[interface_id]

        if len(history) < samples_needed:
            return None

        in_octets = [s['in_octets'] for s in history[-samples_needed:]]
        out_octets = [s['out_octets'] for s in history[-samples_needed:]]

        baseline = {
            'in_mean': statistics.mean(in_octets),
            'in_stdev': statistics.stdev(in_octets),
            'out_mean': statistics.mean(out_octets),
            'out_stdev': statistics.stdev(out_octets)
        }

        return baseline

    def detect_anomaly(self, current, baseline, threshold_sigma=3):
        """Detect if current value deviates from baseline"""
        anomalies = []

        # Check inbound traffic
        in_deviation = abs(current['in_octets'] - baseline['in_mean'])
        if in_deviation > (threshold_sigma * baseline['in_stdev']):
            anomalies.append({
                'type': 'inbound_traffic',
                'current': current['in_octets'],
                'expected': baseline['in_mean'],
                'deviation': in_deviation
            })

        # Check outbound traffic
        out_deviation = abs(current['out_octets'] - baseline['out_mean'])
        if out_deviation > (threshold_sigma * baseline['out_stdev']):
            anomalies.append({
                'type': 'outbound_traffic',
                'current': current['out_octets'],
                'expected': baseline['out_mean'],
                'deviation': out_deviation
            })

        return anomalies

    def monitor(self, interval=60, duration_hours=24):
        """Main monitoring loop"""
        end_time = datetime.now() + timedelta(hours=duration_hours)

        while datetime.now() < end_time:
            for device in self.devices:
                print(f"Monitoring {device['host']} at {datetime.now()}")

                metrics = self.get_interface_metrics(
                    device['host'],
                    device.get('community', 'public')
                )

                for if_id, data in metrics.items():
                    # Store current metrics
                    current = {
                        'timestamp': datetime.now(),
                        'in_octets': data.get('in_octets', 0),
                        'out_octets': data.get('out_octets', 0)
                    }

                    self.history[f"{device['host']}-{if_id}"].append(current)

                    # Calculate and check baseline
                    baseline = self.calculate_baseline(f"{device['host']}-{if_id}")
                    if baseline:
                        anomalies = self.detect_anomaly(current, baseline)
                        if anomalies:
                            print(f"⚠ Anomalies detected on {device['host']} interface {if_id}:")
                            for anomaly in anomalies:
                                print(f"  - {anomaly['type']}: {anomaly['deviation']:.2f} above normal")

            time.sleep(interval)

# Usage
devices = [
    {'host': '192.168.1.1', 'community': 'public'},
    {'host': '192.168.1.2', 'community': 'public'}
]

monitor = NetworkBaselineMonitor(devices)
monitor.monitor(interval=300, duration_hours=24)
```

## Career Path
Network monitoring and observability expertise is critical for:
- Network Operations Center (NOC) engineers
- Network architects designing observability
- DevOps engineers implementing monitoring
- Cloud platform engineers
- Security operations center (SOC) analysts
- Site Reliability Engineers (SRE)
- Network automation engineers

## Certification Alignment
- CCNA: Network monitoring basics
- CCNP Enterprise: Advanced monitoring
- Certified Kubernetes Administrator (CKA): Container observability
- Splunk User Certification: Log analysis
- Prometheus Certified Associate: Metrics and alerting
- Grafana Certified Associate: Dashboard design

---

**Last Updated**: 2025-11-19
**Skill Level**: Advanced
**Status**: Complete
