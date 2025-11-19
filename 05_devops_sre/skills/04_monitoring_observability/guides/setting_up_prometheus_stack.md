# Setting Up Prometheus Stack Guide

This guide walks you through setting up a complete production-ready Prometheus monitoring stack including Prometheus, Grafana, Alertmanager, and various exporters.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Installing Prometheus](#installing-prometheus)
4. [Installing Node Exporter](#installing-node-exporter)
5. [Installing Alertmanager](#installing-alertmanager)
6. [Installing Grafana](#installing-grafana)
7. [Configuring Service Discovery](#configuring-service-discovery)
8. [Setting Up Recording Rules](#setting-up-recording-rules)
9. [Setting Up Alerting Rules](#setting-up-alerting-rules)
10. [Creating Grafana Dashboards](#creating-grafana-dashboards)
11. [High Availability Setup](#high-availability-setup)
12. [Security Hardening](#security-hardening)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Monitored Systems                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Node    │  │  Node    │  │  App     │  │  Custom  │   │
│  │ Exporter │  │ Exporter │  │ Metrics  │  │ Exporter │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼─────────┘
        │             │             │             │
        │ :9100       │ :9100       │ :8080       │ :9200
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                      │ (scrape)
                      ▼
        ┌─────────────────────────────┐
        │       Prometheus             │
        │         :9090                │
        │                              │
        │  - Time series database      │
        │  - Recording rules           │
        │  - Alerting rules            │
        └──────┬──────────────┬────────┘
               │              │
               │ (query)      │ (alerts)
               │              │
               ▼              ▼
    ┌──────────────┐   ┌──────────────┐
    │   Grafana    │   │ Alertmanager │
    │    :3000     │   │    :9093     │
    │              │   │              │
    │ - Dashboards │   │ - Routing    │
    │ - Alerts     │   │ - Grouping   │
    │ - Panels     │   │ - Silencing  │
    └──────────────┘   └──────┬───────┘
                              │
                              │ (notifications)
                              ▼
                       ┌──────────────┐
                       │ Slack/Email/ │
                       │  PagerDuty   │
                       └──────────────┘
```

---

## Prerequisites

- Linux server (Ubuntu 20.04+ or CentOS 7+)
- Root or sudo access
- Minimum 4GB RAM, 2 CPU cores
- 50GB+ disk space for time series data
- Network connectivity between components

---

## Installing Prometheus

### Method 1: Binary Installation

```bash
# Create prometheus user
sudo useradd --no-create-home --shell /bin/false prometheus

# Create directories
sudo mkdir -p /etc/prometheus
sudo mkdir -p /var/lib/prometheus

# Download Prometheus (replace with latest version)
PROM_VERSION="2.45.0"
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v${PROM_VERSION}/prometheus-${PROM_VERSION}.linux-amd64.tar.gz

# Extract
tar xvf prometheus-${PROM_VERSION}.linux-amd64.tar.gz
cd prometheus-${PROM_VERSION}.linux-amd64

# Copy binaries
sudo cp prometheus /usr/local/bin/
sudo cp promtool /usr/local/bin/

# Copy configuration files
sudo cp -r consoles /etc/prometheus/
sudo cp -r console_libraries /etc/prometheus/

# Set ownership
sudo chown -R prometheus:prometheus /etc/prometheus
sudo chown -R prometheus:prometheus /var/lib/prometheus
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool
```

### Prometheus Configuration

Create `/etc/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'production'
    region: 'us-east-1'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - 'localhost:9093'

# Load rules once and periodically evaluate them
rule_files:
  - "/etc/prometheus/rules/*.yml"

# Scrape configurations
scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
        labels:
          env: 'production'

  # Node exporters
  - job_name: 'node'
    static_configs:
      - targets:
          - 'node1.example.com:9100'
          - 'node2.example.com:9100'
          - 'node3.example.com:9100'
        labels:
          env: 'production'
          datacenter: 'dc1'

  # Application metrics
  - job_name: 'api-server'
    static_configs:
      - targets:
          - 'api1.example.com:8080'
          - 'api2.example.com:8080'
        labels:
          env: 'production'
          service: 'api'

  # Kubernetes pod discovery (if using Kubernetes)
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
```

### Create Systemd Service

Create `/etc/systemd/system/prometheus.service`:

```ini
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/var/lib/prometheus/ \
  --storage.tsdb.retention.time=30d \
  --storage.tsdb.retention.size=50GB \
  --web.console.templates=/etc/prometheus/consoles \
  --web.console.libraries=/etc/prometheus/console_libraries \
  --web.listen-address=0.0.0.0:9090 \
  --web.enable-lifecycle

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Start Prometheus

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable and start Prometheus
sudo systemctl enable prometheus
sudo systemctl start prometheus

# Check status
sudo systemctl status prometheus

# View logs
sudo journalctl -u prometheus -f

# Verify Prometheus is running
curl http://localhost:9090/-/healthy
```

---

## Installing Node Exporter

Node Exporter exposes system metrics.

```bash
# Download Node Exporter
NODE_EXPORTER_VERSION="1.6.1"
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz

# Extract
tar xvf node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz

# Copy binary
sudo cp node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64/node_exporter /usr/local/bin/

# Create user
sudo useradd --no-create-home --shell /bin/false node_exporter

# Set ownership
sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter
```

### Create Systemd Service

Create `/etc/systemd/system/node_exporter.service`:

```ini
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter \
  --collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/) \
  --collector.netclass.ignored-devices=^(veth.*|docker.*|br-.*)$ \
  --collector.netdev.device-exclude=^(veth.*|docker.*|br-.*)$

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Start Node Exporter

```bash
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
sudo systemctl status node_exporter

# Verify metrics
curl http://localhost:9100/metrics
```

---

## Installing Alertmanager

```bash
# Download Alertmanager
ALERTMANAGER_VERSION="0.26.0"
cd /tmp
wget https://github.com/prometheus/alertmanager/releases/download/v${ALERTMANAGER_VERSION}/alertmanager-${ALERTMANAGER_VERSION}.linux-amd64.tar.gz

# Extract
tar xvf alertmanager-${ALERTMANAGER_VERSION}.linux-amd64.tar.gz
cd alertmanager-${ALERTMANAGER_VERSION}.linux-amd64

# Copy binaries
sudo cp alertmanager /usr/local/bin/
sudo cp amtool /usr/local/bin/

# Create user and directories
sudo useradd --no-create-home --shell /bin/false alertmanager
sudo mkdir /etc/alertmanager
sudo mkdir /var/lib/alertmanager

# Set ownership
sudo chown alertmanager:alertmanager /usr/local/bin/alertmanager
sudo chown alertmanager:alertmanager /usr/local/bin/amtool
sudo chown -R alertmanager:alertmanager /etc/alertmanager
sudo chown -R alertmanager:alertmanager /var/lib/alertmanager
```

### Alertmanager Configuration

Create `/etc/alertmanager/alertmanager.yml`:

```yaml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'

# Templates for notifications
templates:
  - '/etc/alertmanager/templates/*.tmpl'

# Route tree
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'

  routes:
    # Critical alerts to PagerDuty
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      continue: true

    # Critical alerts also to Slack
    - match:
        severity: critical
      receiver: 'slack-critical'

    # Warning alerts to Slack
    - match:
        severity: warning
      receiver: 'slack-warnings'

# Inhibition rules
inhibit_rules:
  # Inhibit warning if critical is firing
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'cluster', 'service']

receivers:
  - name: 'default'
    slack_configs:
      - channel: '#alerts-default'
        title: 'Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'slack-critical'
    slack_configs:
      - channel: '#alerts-critical'
        title: ':fire: CRITICAL: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}*Summary:* {{ .Annotations.summary }}\n*Description:* {{ .Annotations.description }}\n*Severity:* {{ .Labels.severity }}{{ end }}'
        send_resolved: true

  - name: 'slack-warnings'
    slack_configs:
      - channel: '#alerts-warnings'
        title: ':warning: Warning: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
        description: '{{ .GroupLabels.alertname }}: {{ .GroupLabels.instance }}'
```

### Create Systemd Service

Create `/etc/systemd/system/alertmanager.service`:

```ini
[Unit]
Description=Alertmanager
Wants=network-online.target
After=network-online.target

[Service]
User=alertmanager
Group=alertmanager
Type=simple
ExecStart=/usr/local/bin/alertmanager \
  --config.file=/etc/alertmanager/alertmanager.yml \
  --storage.path=/var/lib/alertmanager/ \
  --web.listen-address=0.0.0.0:9093

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Start Alertmanager

```bash
sudo systemctl daemon-reload
sudo systemctl enable alertmanager
sudo systemctl start alertmanager
sudo systemctl status alertmanager

# Verify
curl http://localhost:9093/-/healthy
```

---

## Installing Grafana

### Using APT (Debian/Ubuntu)

```bash
# Add Grafana GPG key
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -

# Add repository
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

# Update and install
sudo apt-get update
sudo apt-get install -y grafana

# Enable and start
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
sudo systemctl status grafana-server
```

### Using YUM (RHEL/CentOS)

```bash
# Create repo file
cat <<EOF | sudo tee /etc/yum.repos.d/grafana.repo
[grafana]
name=grafana
baseurl=https://packages.grafana.com/oss/rpm
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://packages.grafana.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
EOF

# Install
sudo yum install -y grafana

# Enable and start
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
sudo systemctl status grafana-server
```

### Grafana Configuration

Edit `/etc/grafana/grafana.ini`:

```ini
[server]
protocol = http
http_addr = 0.0.0.0
http_port = 3000
domain = grafana.example.com
root_url = https://grafana.example.com

[database]
type = postgres
host = postgres.example.com:5432
name = grafana
user = grafana
password = your_password

[security]
admin_user = admin
admin_password = change_this_password
secret_key = SW2YcwTIb9zpOOhoPsMm
disable_gravatar = true
cookie_secure = true
cookie_samesite = strict

[auth]
disable_login_form = false
disable_signout_menu = false

[auth.anonymous]
enabled = false

[snapshots]
external_enabled = false

[users]
allow_sign_up = false
allow_org_create = false
auto_assign_org = true
auto_assign_org_role = Viewer

[log]
mode = console file
level = info
```

Restart Grafana:

```bash
sudo systemctl restart grafana-server
```

### Access Grafana

1. Open browser: `http://your-server:3000`
2. Login: `admin` / `admin` (change password on first login)

### Add Prometheus Data Source

Via UI:
1. Go to Configuration → Data Sources
2. Click "Add data source"
3. Select "Prometheus"
4. URL: `http://localhost:9090`
5. Click "Save & Test"

Via Provisioning (recommended for production):

Create `/etc/grafana/provisioning/datasources/prometheus.yml`:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://localhost:9090
    isDefault: true
    editable: false
    jsonData:
      timeInterval: 15s
      queryTimeout: 60s
      httpMethod: POST
```

---

## Configuring Service Discovery

### Kubernetes Service Discovery

```yaml
scrape_configs:
  # Scrape Kubernetes nodes
  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
      - role: node
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)

  # Scrape Kubernetes pods
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      # Only scrape pods with annotation prometheus.io/scrape=true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      # Use custom metrics path if specified
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      # Use custom port if specified
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      # Add namespace label
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      # Add pod name label
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: kubernetes_pod_name
```

### Consul Service Discovery

```yaml
scrape_configs:
  - job_name: 'consul-services'
    consul_sd_configs:
      - server: 'consul.example.com:8500'
        datacenter: 'dc1'
        services: []  # Empty means all services
    relabel_configs:
      - source_labels: [__meta_consul_service]
        target_label: job
      - source_labels: [__meta_consul_tags]
        target_label: consul_tags
```

### File-Based Service Discovery

```yaml
scrape_configs:
  - job_name: 'file-discovery'
    file_sd_configs:
      - files:
          - '/etc/prometheus/targets/*.json'
        refresh_interval: 5m
```

Create `/etc/prometheus/targets/production.json`:

```json
[
  {
    "targets": ["api1.example.com:8080", "api2.example.com:8080"],
    "labels": {
      "env": "production",
      "service": "api",
      "team": "backend"
    }
  },
  {
    "targets": ["db1.example.com:9100", "db2.example.com:9100"],
    "labels": {
      "env": "production",
      "service": "database",
      "team": "data"
    }
  }
]
```

---

## Setting Up Recording Rules

Create `/etc/prometheus/rules/recording_rules.yml`:

```yaml
groups:
  - name: http_recording_rules
    interval: 15s
    rules:
      # Request rate
      - record: job:http_requests:rate5m
        expr: sum by (job) (rate(http_requests_total[5m]))

      # Error rate
      - record: job:http_errors:rate5m
        expr: sum by (job) (rate(http_requests_total{status=~"5.."}[5m]))

      # Error ratio
      - record: job:http_error_ratio:rate5m
        expr: |
          job:http_errors:rate5m / job:http_requests:rate5m

  - name: resource_recording_rules
    interval: 30s
    rules:
      # CPU utilization
      - record: instance:cpu_utilization:ratio
        expr: |
          1 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m]))

      # Memory utilization
      - record: instance:memory_utilization:ratio
        expr: |
          1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)
```

Reload Prometheus:

```bash
# Check config
promtool check config /etc/prometheus/prometheus.yml

# Reload (requires --web.enable-lifecycle flag)
curl -X POST http://localhost:9090/-/reload

# Or restart service
sudo systemctl restart prometheus
```

---

## Setting Up Alerting Rules

Create `/etc/prometheus/rules/alerting_rules.yml`:

```yaml
groups:
  - name: instance_alerts
    rules:
      - alert: InstanceDown
        expr: up == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Instance {{ $labels.instance }} down"
          description: "{{ $labels.instance }} of job {{ $labels.job }} has been down for more than 5 minutes."

      - alert: HighCPUUsage
        expr: instance:cpu_utilization:ratio > 0.85
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is {{ $value | humanizePercentage }} on {{ $labels.instance }}"

      - alert: HighMemoryUsage
        expr: instance:memory_utilization:ratio > 0.90
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is {{ $value | humanizePercentage }} on {{ $labels.instance }}"
```

Reload Prometheus after adding rules.

---

## Creating Grafana Dashboards

### Import Pre-built Dashboards

1. Go to Dashboards → Import
2. Enter dashboard ID:
   - **1860**: Node Exporter Full
   - **3662**: Prometheus 2.0 Overview
   - **12537**: Alertmanager
3. Select Prometheus data source
4. Click "Import"

### Provision Dashboards

Create `/etc/grafana/provisioning/dashboards/default.yml`:

```yaml
apiVersion: 1

providers:
  - name: 'Default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
```

Place dashboard JSON files in `/var/lib/grafana/dashboards/`.

---

## High Availability Setup

### Prometheus HA with Thanos

```yaml
# Prometheus with Thanos sidecar
version: '3'
services:
  prometheus-1:
    image: prom/prometheus:latest
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.min-block-duration=2h'
      - '--storage.tsdb.max-block-duration=2h'
      - '--web.enable-lifecycle'
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus1-data:/prometheus

  thanos-sidecar-1:
    image: thanosio/thanos:latest
    command:
      - 'sidecar'
      - '--tsdb.path=/prometheus'
      - '--prometheus.url=http://prometheus-1:9090'
      - '--objstore.config-file=/etc/thanos/bucket.yml'
    volumes:
      - prometheus1-data:/prometheus
      - ./thanos-bucket.yml:/etc/thanos/bucket.yml

  thanos-query:
    image: thanosio/thanos:latest
    command:
      - 'query'
      - '--http-address=0.0.0.0:9090'
      - '--store=thanos-sidecar-1:10901'
      - '--store=thanos-sidecar-2:10901'
    ports:
      - '9090:9090'
```

### Grafana HA with Load Balancer

```nginx
# /etc/nginx/sites-available/grafana
upstream grafana {
    server grafana1.example.com:3000;
    server grafana2.example.com:3000;
    server grafana3.example.com:3000;
}

server {
    listen 80;
    server_name grafana.example.com;

    location / {
        proxy_pass http://grafana;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Security Hardening

### Enable Authentication

#### Prometheus Basic Auth

Create password file:

```bash
htpasswd -c /etc/prometheus/.htpasswd admin
```

Add to Prometheus command line:

```ini
ExecStart=/usr/local/bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --web.config.file=/etc/prometheus/web.yml
```

Create `/etc/prometheus/web.yml`:

```yaml
basic_auth_users:
  admin: $2y$10$...  # bcrypt hash from htpasswd
```

#### Enable TLS

Generate certificate:

```bash
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
  -keyout /etc/prometheus/prometheus.key \
  -out /etc/prometheus/prometheus.crt
```

Update `/etc/prometheus/web.yml`:

```yaml
tls_server_config:
  cert_file: /etc/prometheus/prometheus.crt
  key_file: /etc/prometheus/prometheus.key
```

### Firewall Rules

```bash
# Allow Prometheus
sudo ufw allow 9090/tcp

# Allow Grafana
sudo ufw allow 3000/tcp

# Allow Node Exporter (from Prometheus only)
sudo ufw allow from prometheus_ip to any port 9100

# Allow Alertmanager
sudo ufw allow 9093/tcp
```

### SELinux (CentOS/RHEL)

```bash
# Allow Prometheus to bind to port
sudo semanage port -a -t http_port_t -p tcp 9090

# Set context for Prometheus directories
sudo semanage fcontext -a -t var_lib_t "/var/lib/prometheus(/.*)?"
sudo restorecon -Rv /var/lib/prometheus
```

---

## Verification and Testing

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Prometheus rules
curl http://localhost:9090/api/v1/rules

# Query Prometheus
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=up'

# Test alert
curl -X POST http://localhost:9093/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d '[{"labels":{"alertname":"TestAlert","severity":"warning"}}]'

# Check Grafana health
curl http://localhost:3000/api/health
```

## Conclusion

You now have a complete Prometheus monitoring stack with:
- Prometheus for metrics collection and storage
- Node Exporter for system metrics
- Alertmanager for alert routing
- Grafana for visualization

Next steps:
- Add more exporters (blackbox, postgres, redis, etc.)
- Create custom recording and alerting rules
- Build comprehensive Grafana dashboards
- Implement SLO monitoring
- Set up long-term storage with Thanos or Cortex
