# Network Observability Guide

## Observability Foundation

### Three Pillars Implementation

#### Metrics (Prometheus)
```
Setup:
  1. Deploy Prometheus server
  2. Configure SNMP/network exporters
  3. Define recording rules
  4. Create dashboards

Key metrics:
  - Interface status/throughput
  - Device health (CPU, memory)
  - BGP neighbor status
  - Error rates
  - Latency measurements
```

#### Logs (ELK/Loki)
```
Setup:
  1. Deploy log aggregation (syslog)
  2. Configure Logstash/Fluentd
  3. Index in Elasticsearch/Loki
  4. Create dashboards

Key logs:
  - Device syslog messages
  - Configuration changes
  - Interface transitions
  - Error conditions
```

#### Traces (Optional for Advanced)
```
Setup:
  1. Instrument network APIs
  2. Deploy trace collector (Jaeger)
  3. Track request paths
  4. Analyze latency breakdown

Use cases:
  - Multi-device transactions
  - Microservice integration
  - End-to-end request tracing
```

## Architecture Design

### Single Site Small Network (<100 devices)
```
┌─ Devices (SNMP, Syslog)
├─ Prometheus (2GB RAM, 100GB disk)
├─ Grafana (1GB RAM)
├─ Elasticsearch (4GB RAM)
└─ Logstash (1GB RAM)

Hardware:
  - Single server: 32GB RAM, 500GB SSD
  - Alternatively: VM cluster on hypervisor
```

### Multi-Site Large Network (1000+ devices)
```
┌─ Site 1 Devices
│  └─ Local Prometheus + ELK
├─ Site 2 Devices
│  └─ Local Prometheus + ELK
└─ Central Aggregation
   ├─ Thanos (central storage)
   ├─ Grafana (queries all sites)
   ├─ Central Elasticsearch
   └─ Analytics

Features:
  - Federated Prometheus
  - Central Grafana
  - Shared storage
  - Global dashboards
```

### High Availability Architecture
```
┌─ Prometheus Cluster (3 nodes)
│  ├─ Node 1 (Scraper)
│  ├─ Node 2 (Scraper)
│  └─ Node 3 (Scraper)
├─ Thanos
│  ├─ Query (load balanced)
│  ├─ Sidecar (per Prometheus)
│  └─ Object Storage (S3/GCS)
├─ Elasticsearch Cluster (3+ nodes)
├─ Grafana Cluster (2+ nodes, load balanced)
└─ Alertmanager Cluster (3 nodes)

Features:
  - No single points of failure
  - Automatic failover
  - Long-term storage
```

## Deployment Steps

### Step 1: Set Up Prometheus

#### Install & Configure
```bash
# Download
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xzf prometheus-2.45.0.linux-amd64.tar.gz
cd prometheus-2.45.0.linux-amd64

# Create prometheus.yml
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 2m
  evaluation_interval: 1m

scrape_configs:
  - job_name: 'snmp_devices'
    static_configs:
      - targets:
          - 192.168.1.1
          - 192.168.1.2
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
EOF

# Start Prometheus
./prometheus --config.file=prometheus.yml
```

### Step 2: Set Up Logging

#### Configure Syslog Aggregation
```bash
# /etc/rsyslog.d/network.conf
input(type="imudp" port="514")
input(type="imtcp" port="514")

$Template DynamicFile,"/var/log/network/%HOSTNAME%/%PROGRAMNAME%.log"

local0.* ?DynamicFile
local1.* ?DynamicFile

# Restart rsyslog
sudo systemctl restart rsyslog

# Monitor incoming logs
sudo tail -f /var/log/network/*/*.log
```

#### Deploy Logstash
```bash
# Download
wget https://artifacts.elastic.co/downloads/logstash/logstash-8.10.0-linux-x86_64.tar.gz
tar xzf logstash-8.10.0-linux-x86_64.tar.gz

# Create pipeline
cat > logstash.conf << 'EOF'
input {
  udp {
    host => "0.0.0.0"
    port => 514
    codec => "plain"
  }
}

filter {
  grok {
    match => { "message" => "%{SYSLOGLINE}" }
  }

  date {
    match => [ "timestamp", "MMM  d HH:mm:ss" ]
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "network-logs-%{+YYYY.MM.dd}"
  }
}
EOF

# Start Logstash
./bin/logstash -f logstash.conf
```

### Step 3: Set Up Visualization

#### Deploy Grafana
```bash
# Download
wget https://dl.grafana.com/oss/release/grafana-10.0.0.linux-amd64.tar.gz
tar xzf grafana-10.0.0.linux-amd64.tar.gz

# Configure
cat > conf/defaults.ini << 'EOF'
[server]
http_port = 3000
protocol = http

[database]
type = sqlite3
path = grafana.db

[security]
admin_password = admin123
EOF

# Start Grafana
./bin/grafana-server
# Access at http://localhost:3000
```

#### Create Data Sources
```
1. Add Prometheus
   - URL: http://localhost:9090
   - Type: Prometheus
   - Access: Server

2. Add Elasticsearch
   - URL: http://localhost:9200
   - Type: Elasticsearch
   - Index pattern: network-logs-*
```

### Step 4: Create Base Dashboards

#### Executive Dashboard
```
Panels:
  1. Network Availability (%)
  2. Critical Alerts (Count)
  3. Total Traffic (Gbps)
  4. Top Sites by Traffic
  5. Last 24h Traffic Trend
```

#### Operations Dashboard
```
Panels:
  1. Active Interfaces (map)
  2. Interface Errors (timeline)
  3. Device CPU Utilization (gauge)
  4. BGP Neighbor Status (table)
  5. Recent Alerts (list)
```

## Instrumentation Strategy

### What to Monitor
```
Priority 1 (Critical):
  - Network availability
  - BGP neighbor status
  - Internet link health
  - Core infrastructure

Priority 2 (Important):
  - Interface errors/discards
  - CPU/memory trends
  - Bandwidth utilization
  - Configuration changes

Priority 3 (Informational):
  - System uptime
  - Device inventory
  - License status
  - Routine events
```

### Metric Collection Points
```
Device Level:
  - SNMP polling (2-5 min)
  - Streaming telemetry (real-time)

Flow Level:
  - NetFlow/sFlow collection
  - Analysis of top talkers

Application Level:
  - API monitoring
  - Transaction logging
  - Performance tracking
```

## Alerting Setup

### Alert Rule Development

#### Critical Alerts
```yaml
groups:
  - name: network_critical
    rules:
      - alert: InterfaceDown
        expr: node_network_up == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Interface down: {{ $labels.device }}"
          description: "Interface has been down for > 2 minutes"
          runbook: "https://wiki/runbooks/interface-down"
```

#### Warning Alerts
```yaml
      - alert: HighPacketErrors
        expr: rate(ifInErrors[5m]) > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High packet errors: {{ $labels.instance }}"
```

### Notification Configuration
```
Alertmanager Routing:
  - Critical → PagerDuty (immediate page)
  - Warning → Slack #network-alerts
  - Info → Email daily digest
```

## Monitoring the Monitoring

### Observability Metrics
```
Monitor Prometheus:
  - Scrape duration
  - Scrape errors
  - Storage usage
  - Cardinality

Monitor Logstash:
  - Ingestion rate
  - Processing latency
  - Queue depth
  - Error rate

Monitor Grafana:
  - Dashboard response time
  - Query duration
  - Data source health
```

## Scaling Considerations

### From 100 to 1000 Devices
```
Changes needed:
  1. Increase Prometheus scrape intervals (5 min)
  2. Implement federation/Thanos
  3. Add Elasticsearch cluster
  4. Load balance Grafana
  5. Implement data retention tiers

Hardware scaling:
  - Prometheus: Vertical (bigger machine)
  - Elasticsearch: Horizontal (more nodes)
  - Storage: Add NAS/S3
```

### Cost Optimization
```
Development:
  - All on single server: $2K
  - Annual SSD replacement: $500

Production:
  - HA cluster: $10K
  - Storage (1TB/year): $1K
  - Bandwidth: $500
  - Annual updates: $2K

ROI:
  - Faster troubleshooting: 20 hrs/month saved
  - Fewer outages: $10K impact average
  - Capacity planning: Prevents over-provisioning
```

## Implementation Checklist

- [ ] Design observability architecture
- [ ] Deploy Prometheus infrastructure
- [ ] Configure metric collection
- [ ] Deploy log aggregation
- [ ] Install Grafana
- [ ] Create base dashboards
- [ ] Define alerting rules
- [ ] Configure notifications
- [ ] Test failover scenarios
- [ ] Document runbooks
- [ ] Train team
- [ ] Plan scaling strategy
- [ ] Establish SLAs for monitoring

---

**Guide Type**: Architecture & Implementation
**Scope**: Complete observability system
**Timeline**: 4-8 weeks
**Typical Scale**: 100-10,000+ devices
**Last Updated**: 2025-11-19
