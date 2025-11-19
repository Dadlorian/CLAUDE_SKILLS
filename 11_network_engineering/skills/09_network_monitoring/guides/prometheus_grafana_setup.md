# Prometheus & Grafana Complete Setup Guide

## System Requirements

### Minimum Hardware
```
Single Server Setup:
  CPU: 2 vCPU (4 for production)
  RAM: 8GB (16GB+ recommended)
  Disk: 50GB SSD (100GB+ for 1+ year retention)
  Network: 1 Gbps

HA Cluster:
  Prometheus: 3 nodes × (4 vCPU, 16GB RAM, 200GB disk)
  Elasticsearch: 3 nodes × (4 vCPU, 16GB RAM, 500GB disk)
  Grafana: 2 nodes × (2 vCPU, 4GB RAM, 50GB disk)
```

## Prometheus Installation

### Option 1: Binary Installation
```bash
# Download latest
VERSION=2.45.0
wget https://github.com/prometheus/prometheus/releases/download/v${VERSION}/prometheus-${VERSION}.linux-amd64.tar.gz
tar xzf prometheus-${VERSION}.linux-amd64.tar.gz
cd prometheus-${VERSION}.linux-amd64

# Create system user
sudo useradd --no-create-home --shell /bin/false prometheus

# Install
sudo mkdir -p /etc/prometheus /var/lib/prometheus
sudo cp prometheus promtool /usr/local/bin/
sudo cp -r consoles/ console_libraries/ /etc/prometheus/
sudo chown -R prometheus:prometheus /etc/prometheus /var/lib/prometheus

# Create config (see section below)
sudo cp prometheus.yml /etc/prometheus/

# Create systemd service
sudo tee /etc/systemd/system/prometheus.service << EOF
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
  --config.file /etc/prometheus/prometheus.yml \
  --storage.tsdb.path /var/lib/prometheus \
  --web.enable-lifecycle

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl start prometheus
sudo systemctl status prometheus
```

### Option 2: Docker Installation
```bash
# Create config directory
mkdir -p /opt/prometheus/etc

# prometheus.yml (see below)
nano /opt/prometheus/etc/prometheus.yml

# Docker Compose
cat > /opt/prometheus/docker-compose.yml << 'EOF'
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:v2.45.0
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./etc/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    networks:
      - monitoring

volumes:
  prometheus_data:

networks:
  monitoring:
    driver: bridge
EOF

docker-compose up -d
```

## Prometheus Configuration

### Basic prometheus.yml
```yaml
global:
  scrape_interval: 2m
  evaluation_interval: 1m
  external_labels:
    monitor: 'network-monitoring'
    site: 'primary'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - localhost:9093

# Load rules
rule_files:
  - "/etc/prometheus/rules/*.yml"

scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # SNMP monitoring
  - job_name: 'snmp_routers'
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

  # Node exporter (system metrics)
  - job_name: 'node_exporter'
    static_configs:
      - targets:
          - localhost:9100
```

### Recording Rules
```yaml
# /etc/prometheus/rules/network.yml
groups:
  - name: network_aggregation
    interval: 30s
    rules:
      # Interface bandwidth utilization
      - record: network:interface_utilization_pct
        expr: |
          ((rate(ifInOctets[5m]) + rate(ifOutOctets[5m])) * 8 / ifSpeed) * 100

      # Per-device total traffic
      - record: network:device_bandwidth_mbps
        expr: |
          sum by (instance) (rate(ifInOctets[5m]) * 8) / 1000000

      # Interface error rate
      - record: network:interface_error_rate
        expr: |
          (rate(ifInErrors[5m]) + rate(ifOutErrors[5m])) /
          (rate(ifInPackets[5m]) + rate(ifOutPackets[5m]))
```

## SNMP Exporter Setup

### Installation
```bash
# Download
VERSION=0.24.0
wget https://github.com/prometheus/snmp_exporter/releases/download/v${VERSION}/snmp_exporter-${VERSION}.linux-amd64.tar.gz
tar xzf snmp_exporter-${VERSION}.linux-amd64.tar.gz

# Generate config from MIBs
cd snmp_exporter-${VERSION}.linux-amd64
./generator generate

# Create user and directories
sudo useradd --no-create-home --shell /bin/false snmp_exporter
sudo mkdir -p /etc/snmp_exporter
sudo cp snmp.yml /etc/snmp_exporter/
sudo chown snmp_exporter:snmp_exporter /etc/snmp_exporter/snmp.yml

# Systemd service
sudo tee /etc/systemd/system/snmp_exporter.service << 'EOF'
[Unit]
Description=SNMP Exporter
After=network.target

[Service]
Type=simple
User=snmp_exporter
Group=snmp_exporter
ExecStart=/usr/local/bin/snmp_exporter --config.file=/etc/snmp_exporter/snmp.yml

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable snmp_exporter
sudo systemctl start snmp_exporter
```

## Grafana Installation

### Option 1: Binary Installation
```bash
# Download
VERSION=10.0.0
wget https://dl.grafana.com/oss/release/grafana-${VERSION}.linux-amd64.tar.gz
tar xzf grafana-${VERSION}.linux-amd64.tar.gz

# Setup
sudo mkdir -p /opt/grafana /var/lib/grafana
sudo cp grafana-${VERSION}/conf /opt/grafana/
sudo cp grafana-${VERSION}/bin/grafana-server /usr/local/bin/

# Create user
sudo useradd --no-create-home --shell /bin/false grafana

# Configuration
sudo mkdir -p /etc/grafana
sudo tee /etc/grafana/grafana.ini << 'EOF'
[paths]
data = /var/lib/grafana
logs = /var/log/grafana

[server]
http_port = 3000
protocol = http
domain = localhost

[security]
admin_user = admin
admin_password = changeme123
secret_key = your-secret-key-here

[auth.basic]
enabled = true

[users]
allow_sign_up = false

[install_plugins]
admin_generic_datasource_plugin
EOF

# Systemd service
sudo tee /etc/systemd/system/grafana.service << 'EOF'
[Unit]
Description=Grafana
After=network.target

[Service]
User=grafana
Group=grafana
ExecStart=/usr/local/bin/grafana-server \
  --config=/etc/grafana/grafana.ini

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

### Option 2: Docker Installation
```bash
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -v grafana_data:/var/lib/grafana \
  -e "GF_SECURITY_ADMIN_PASSWORD=admin123" \
  grafana/grafana:10.0.0
```

## Integration & Testing

### Verify Prometheus
```bash
# Check if Prometheus is running
curl http://localhost:9090/-/healthy
# Should return 200 OK

# Access web UI
# http://localhost:9090
# Go to Status → Targets to see scrape status

# Query metrics
curl 'http://localhost:9090/api/v1/query?query=up'
```

### Add Prometheus Data Source to Grafana
```
1. Login to Grafana (default: admin/admin)
2. Navigate to Configuration → Data Sources
3. Click "Add data source"
4. Select "Prometheus"
5. Set URL to: http://localhost:9090
6. Click "Save & Test"
```

### Import Pre-built Dashboards
```
1. Go to Dashboards → Browse
2. Click "+ New" or "Import"
3. Use Grafana dashboard ID:
   - 1860: Node Exporter for Prometheus
   - 3662: Prometheus Stats
   - 12114: SNMP Network Monitoring
4. Select Prometheus data source
5. Click Import
```

## High Availability Setup

### Prometheus Clustering with Thanos
```yaml
# prometheus.yml additions for Thanos
global:
  external_labels:
    cluster: 'us-east-1'
    replica: '0'  # 0, 1, 2 for 3-replica setup

# Thanos sidecar
thanos:
  sidecar:
    enabled: true
    address: ':10901'
    objstore:
      config:
        bucket: 'prometheus-thanos'
        provider: 's3'
        s3:
          bucket: 'my-prometheus-bucket'
          region: 'us-east-1'
```

### Thanos Query Setup
```bash
# Deploy Thanos Query on separate server
docker run -d \
  --name thanos-query \
  -p 10902:10902 \
  quay.io/thanos/thanos:latest query \
  --query.addresses=prometheus1:10901,prometheus2:10901,prometheus3:10901

# Access: http://localhost:10902
```

## Backup & Restore

### Prometheus Data Backup
```bash
# Create snapshot
curl -X POST http://localhost:9090/api/v1/admin/tsdb/snapshot
# Returns: {"name":"20240101T000000Z-abc123"}

# Backup directory
tar czf prometheus_backup_$(date +%s).tar.gz /var/lib/prometheus/snapshots/

# Store offsite
scp prometheus_backup_*.tar.gz backup@backup-server:/backups/
```

### Grafana Dashboard Backup
```bash
# Export all dashboards
for dash_id in $(curl -s http://localhost:3000/api/search \
  -H "Authorization: Bearer $API_TOKEN" \
  | jq -r '.[].id'); do
  curl -s http://localhost:3000/api/dashboards/uid/$dash_id \
    -H "Authorization: Bearer $API_TOKEN" > dashboard_$dash_id.json
done

# Or use grafana-api-org-dashboards tool
pip install grafana-api-org-dashboards
grafana-api-org-dashboards \
  --url http://localhost:3000 \
  --api-token $API_TOKEN \
  --backup-dir ./dashboards/
```

## Maintenance Tasks

### Daily
```bash
# Check system resources
df -h /var/lib/prometheus

# Verify scrape success
curl http://localhost:9090/api/v1/query?query=up | jq '.data.result[] | select(.value[1]=="0")'

# Check Grafana logs
tail -100 /var/log/grafana/grafana.log
```

### Weekly
```bash
# Review alert history
curl http://localhost:9090/api/v1/alerts | jq '.data.alerts | length'

# Check metric cardinality
curl http://localhost:9090/api/v1/label/__name__/values | jq 'length'
```

### Monthly
```bash
# Backup Prometheus data
./backup_prometheus.sh

# Backup Grafana dashboards
./backup_grafana_dashboards.sh

# Review retention requirements
du -sh /var/lib/prometheus/

# Plan capacity if >80% used
```

## Implementation Checklist

- [ ] Install Prometheus
- [ ] Install SNMP Exporter
- [ ] Configure device monitoring
- [ ] Install Grafana
- [ ] Add Prometheus data source
- [ ] Import/create base dashboards
- [ ] Configure recording rules
- [ ] Set up alerting rules
- [ ] Configure Alertmanager
- [ ] Test notifications
- [ ] Create user accounts
- [ ] Document procedures
- [ ] Plan backup strategy
- [ ] Schedule maintenance tasks

---

**Guide Type**: Installation & Configuration
**Technology Stack**: Prometheus 2.x, Grafana 10.x
**Target Audience**: Operations engineers
**Timeline**: 1-2 weeks
**Last Updated**: 2025-11-19
