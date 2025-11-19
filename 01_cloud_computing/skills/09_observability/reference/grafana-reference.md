# Grafana Reference

## Overview

Grafana is an open-source analytics and visualization platform that supports multiple data sources including Prometheus, Elasticsearch, InfluxDB, and cloud monitoring services.

## Installation

### Binary
```bash
wget https://dl.grafana.com/oss/release/grafana-10.2.2.linux-amd64.tar.gz
tar -zxvf grafana-10.2.2.linux-amd64.tar.gz
cd grafana-10.2.2
./bin/grafana-server
```

### Docker
```bash
docker run -d -p 3000:3000 --name=grafana grafana/grafana-oss
```

### Kubernetes (Helm)
```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm install grafana grafana/grafana
```

## Data Sources

### Prometheus
```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    jsonData:
      timeInterval: '15s'
      httpMethod: POST
    editable: false
```

### Loki (Logs)
```yaml
datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    jsonData:
      maxLines: 1000
```

### Elasticsearch
```yaml
datasources:
  - name: Elasticsearch
    type: elasticsearch
    access: proxy
    url: http://elasticsearch:9200
    database: '[logs-]YYYY.MM.DD'
    jsonData:
      timeField: '@timestamp'
      esVersion: '8.0.0'
      logMessageField: 'message'
      logLevelField: 'level'
```

### CloudWatch
```yaml
datasources:
  - name: CloudWatch
    type: cloudwatch
    jsonData:
      authType: keys
      defaultRegion: us-east-1
    secureJsonData:
      accessKey: 'YOUR_ACCESS_KEY'
      secretKey: 'YOUR_SECRET_KEY'
```

## Dashboard Creation

### Dashboard JSON Structure
```json
{
  "dashboard": {
    "title": "API Metrics",
    "tags": ["api", "performance"],
    "timezone": "browser",
    "refresh": "30s",
    "time": {
      "from": "now-6h",
      "to": "now"
    },
    "panels": [],
    "templating": {
      "list": []
    }
  }
}
```

### Panel Types

#### Graph (Time Series)
```json
{
  "type": "graph",
  "title": "Request Rate",
  "targets": [
    {
      "expr": "sum(rate(http_requests_total[5m])) by (service)",
      "legendFormat": "{{service}}"
    }
  ],
  "yaxes": [
    {
      "format": "reqps",
      "label": "Requests/sec"
    }
  ]
}
```

#### Stat Panel
```json
{
  "type": "stat",
  "title": "Error Rate",
  "targets": [
    {
      "expr": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m]))"
    }
  ],
  "options": {
    "reduceOptions": {
      "values": false,
      "calcs": ["lastNotNull"]
    },
    "text": {
      "valueSize": 50
    }
  },
  "fieldConfig": {
    "defaults": {
      "unit": "percentunit",
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"value": null, "color": "green"},
          {"value": 0.01, "color": "yellow"},
          {"value": 0.05, "color": "red"}
        ]
      }
    }
  }
}
```

#### Gauge
```json
{
  "type": "gauge",
  "title": "CPU Usage",
  "targets": [
    {
      "expr": "avg(instance:node_cpu:ratio) * 100"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "percent",
      "min": 0,
      "max": 100,
      "thresholds": {
        "steps": [
          {"value": 0, "color": "green"},
          {"value": 60, "color": "yellow"},
          {"value": 80, "color": "red"}
        ]
      }
    }
  }
}
```

#### Table
```json
{
  "type": "table",
  "title": "Service Status",
  "targets": [
    {
      "expr": "up{job=\"api\"}",
      "instant": true,
      "format": "table"
    }
  ],
  "transformations": [
    {
      "id": "organize",
      "options": {
        "excludeByName": {
          "__name__": true,
          "Time": true
        },
        "indexByName": {},
        "renameByName": {
          "instance": "Instance",
          "Value": "Status"
        }
      }
    }
  ]
}
```

#### Heatmap
```json
{
  "type": "heatmap",
  "title": "Latency Distribution",
  "targets": [
    {
      "expr": "sum(rate(http_request_duration_seconds_bucket[5m])) by (le)",
      "format": "heatmap",
      "legendFormat": "{{le}}"
    }
  ],
  "dataFormat": "tsbuckets",
  "yAxis": {
    "format": "s"
  }
}
```

#### Logs Panel
```json
{
  "type": "logs",
  "title": "Application Logs",
  "targets": [
    {
      "expr": "{job=\"api\", level=\"error\"}",
      "refId": "A"
    }
  ],
  "options": {
    "showTime": true,
    "showLabels": true,
    "sortOrder": "Descending"
  }
}
```

## Variables (Templating)

### Query Variable
```json
{
  "templating": {
    "list": [
      {
        "type": "query",
        "name": "service",
        "label": "Service",
        "datasource": "Prometheus",
        "query": "label_values(http_requests_total, service)",
        "refresh": 1,
        "multi": true,
        "includeAll": true
      }
    ]
  }
}
```

### Custom Variable
```json
{
  "type": "custom",
  "name": "environment",
  "label": "Environment",
  "query": "production,staging,development",
  "multi": false,
  "includeAll": false,
  "current": {
    "text": "production",
    "value": "production"
  }
}
```

### Interval Variable
```json
{
  "type": "interval",
  "name": "interval",
  "label": "Interval",
  "auto": true,
  "auto_count": 30,
  "auto_min": "10s",
  "query": "1m,5m,10m,30m,1h,6h,12h,1d,7d",
  "current": {
    "text": "auto",
    "value": "$__auto_interval_interval"
  }
}
```

### Using Variables in Queries
```
# In PromQL
sum(rate(http_requests_total{service="$service"}[$interval])) by (method)

# Multi-select with regex
sum(rate(http_requests_total{service=~"$service"}[$interval]))

# All option
sum(rate(http_requests_total{service=~"${service:regex}"}[$interval]))
```

## Common Queries

### Request Rate (RED Method)
```promql
# Rate - Requests per second
sum(rate(http_requests_total{service="$service"}[5m])) by (method)

# Errors - Error rate
sum(rate(http_requests_total{service="$service",status=~"5.."}[5m])) /
sum(rate(http_requests_total{service="$service"}[5m]))

# Duration - p95 latency
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket{service="$service"}[5m])) by (le)
)
```

### Resource Usage (USE Method)
```promql
# Utilization - CPU
avg(instance:node_cpu:ratio{instance="$instance"}) * 100

# Saturation - Disk queue
avg(node_disk_io_time_seconds_total{instance="$instance"})

# Errors - Network errors
rate(node_network_transmit_errs_total{instance="$instance"}[5m])
```

### Availability
```promql
# Uptime percentage (30 days)
avg_over_time(up{job="$job"}[30d]) * 100

# Current status
up{job="$job"} == 1
```

## Alerting in Grafana

### Alert Rule
```json
{
  "alert": {
    "name": "High Error Rate",
    "message": "Error rate is above 5% for service $service",
    "conditions": [
      {
        "evaluator": {
          "type": "gt",
          "params": [0.05]
        },
        "operator": {
          "type": "and"
        },
        "query": {
          "params": ["A", "5m", "now"]
        },
        "reducer": {
          "type": "avg"
        },
        "type": "query"
      }
    ],
    "executionErrorState": "alerting",
    "for": "5m",
    "frequency": "1m",
    "noDataState": "no_data",
    "notifications": [
      {
        "uid": "slack-notifier"
      }
    ]
  }
}
```

### Notification Channels

#### Slack
```json
{
  "name": "Slack Alerts",
  "type": "slack",
  "settings": {
    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "recipient": "#alerts",
    "username": "Grafana",
    "icon_emoji": ":grafana:"
  }
}
```

#### PagerDuty
```json
{
  "name": "PagerDuty",
  "type": "pagerduty",
  "settings": {
    "integrationKey": "YOUR_INTEGRATION_KEY",
    "autoResolve": true
  }
}
```

#### Email
```json
{
  "name": "Email Alerts",
  "type": "email",
  "settings": {
    "addresses": "alerts@company.com",
    "singleEmail": true
  }
}
```

## Dashboard Design Patterns

### Service Overview Dashboard
```
Panels:
1. Request Rate (time series)
2. Error Rate (stat with threshold)
3. p95 Latency (gauge)
4. Service Status (stat)
5. Error Logs (logs panel)
6. Request by Endpoint (bar chart)
7. Status Code Distribution (pie chart)
8. Latency Heatmap (heatmap)
```

### Node/Infrastructure Dashboard
```
Panels:
1. CPU Usage (gauge per instance)
2. Memory Usage (graph)
3. Disk Usage (bar chart)
4. Network I/O (graph)
5. Load Average (stat)
6. Disk IOPS (graph)
7. Process Count (graph)
```

### Application Dashboard
```
Panels:
1. Request Rate (graph)
2. Active Users (stat)
3. Database Queries (graph)
4. Cache Hit Ratio (gauge)
5. Queue Depth (graph)
6. Background Job Status (table)
```

## Annotations

### Query-Based Annotations
```json
{
  "annotations": {
    "list": [
      {
        "datasource": "Prometheus",
        "enable": true,
        "expr": "ALERTS{alertstate=\"firing\"}",
        "iconColor": "red",
        "name": "Alerts",
        "step": "60s",
        "tagKeys": "alertname",
        "textFormat": "{{alertname}}",
        "titleFormat": "Alert"
      }
    ]
  }
}
```

### Deployment Annotations
```json
{
  "name": "Deployments",
  "datasource": "-- Grafana --",
  "iconColor": "blue",
  "enable": true,
  "tags": ["deployment"]
}
```

## Provisioning

### Dashboard Provisioning
```yaml
# dashboards.yml
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
      foldersFromFilesStructure: true
```

### Data Source Provisioning
```yaml
# datasources.yml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: false
```

### Alert Provisioning
```yaml
# alerting.yml
apiVersion: 1

contactPoints:
  - orgId: 1
    name: slack
    receivers:
      - uid: slack-1
        type: slack
        settings:
          url: https://hooks.slack.com/services/YOUR/WEBHOOK
          text: '{{ template "custom.message" . }}'

policies:
  - orgId: 1
    receiver: slack
    group_by: ['alertname', 'grafana_folder']
    group_wait: 10s
    group_interval: 5m
    repeat_interval: 12h
```

## Plugins

### Installing Plugins
```bash
# CLI
grafana-cli plugins install grafana-piechart-panel

# Docker
docker run -e "GF_INSTALL_PLUGINS=grafana-piechart-panel" grafana/grafana

# Kubernetes
env:
  - name: GF_INSTALL_PLUGINS
    value: "grafana-piechart-panel,grafana-worldmap-panel"
```

### Popular Plugins
- **grafana-piechart-panel**: Pie charts
- **grafana-worldmap-panel**: Geographic visualization
- **grafana-clock-panel**: Clock widget
- **alexanderzobnin-zabbix-app**: Zabbix integration
- **grafana-polystat-panel**: Multi-stat panel

## Advanced Features

### Transformations
```json
{
  "transformations": [
    {
      "id": "reduce",
      "options": {
        "reducers": ["mean"]
      }
    },
    {
      "id": "organize",
      "options": {
        "excludeByName": {
          "Time": true
        },
        "renameByName": {
          "Value": "Average"
        }
      }
    }
  ]
}
```

### Overrides
```json
{
  "fieldConfig": {
    "overrides": [
      {
        "matcher": {
          "id": "byName",
          "options": "errors"
        },
        "properties": [
          {
            "id": "color",
            "value": {
              "mode": "fixed",
              "fixedColor": "red"
            }
          }
        ]
      }
    ]
  }
}
```

### Dashboard Links
```json
{
  "links": [
    {
      "title": "Related Dashboard",
      "type": "link",
      "url": "/d/other-dashboard",
      "icon": "dashboard"
    },
    {
      "title": "Runbook",
      "type": "link",
      "url": "https://wiki.company.com/runbooks",
      "icon": "doc"
    }
  ]
}
```

## API Usage

### Create Dashboard
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d @dashboard.json \
  http://grafana:3000/api/dashboards/db
```

### Get Dashboard
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://grafana:3000/api/dashboards/uid/DASHBOARD_UID
```

### Search Dashboards
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "http://grafana:3000/api/search?query=api&starred=true"
```

### Create API Key
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{"name":"api-key","role":"Admin"}' \
  http://grafana:3000/api/auth/keys
```

## Configuration

### grafana.ini
```ini
[server]
http_port = 3000
domain = grafana.company.com
root_url = %(protocol)s://%(domain)s/

[database]
type = postgres
host = postgres:5432
name = grafana
user = grafana
password = password

[security]
admin_user = admin
admin_password = admin
secret_key = YOUR_SECRET_KEY

[auth]
disable_login_form = false
oauth_auto_login = false

[auth.anonymous]
enabled = true
org_role = Viewer

[smtp]
enabled = true
host = smtp.gmail.com:587
user = your_email@gmail.com
password = your_password
from_address = grafana@company.com

[alerting]
enabled = true
execute_alerts = true

[unified_alerting]
enabled = true
```

## Performance Optimization

### Query Optimization
```
1. Use recording rules for expensive queries
2. Limit time ranges
3. Use appropriate intervals
4. Avoid high-cardinality queries
5. Use query caching
```

### Dashboard Optimization
```
1. Limit number of panels (< 20)
2. Use appropriate refresh rates
3. Avoid auto-refresh on complex dashboards
4. Use variables to reduce panel count
5. Organize with rows and folders
```

## Best Practices

### Dashboard Design
1. **Golden Signal First**: Put most important metrics at top
2. **Consistent Layout**: Use grid alignment
3. **Color Coding**: Green/Yellow/Red thresholds
4. **Tooltips**: Add helpful descriptions
5. **Variables**: Enable filtering and reuse
6. **Time Range**: Default to relevant window

### Panel Configuration
1. **Clear Titles**: Descriptive panel names
2. **Units**: Always specify units
3. **Legends**: Use meaningful legend formats
4. **Thresholds**: Set appropriate warning/critical levels
5. **Decimals**: Limit decimal places

### Organization
1. **Folders**: Group related dashboards
2. **Tags**: Tag for easy discovery
3. **Naming**: Consistent naming convention
4. **Teams**: Use teams for access control
5. **Versioning**: Use dashboard versions

## Troubleshooting

### Data Source Issues
```bash
# Test data source connection
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://grafana:3000/api/datasources/proxy/1/api/v1/query?query=up

# Check Grafana logs
docker logs grafana
tail -f /var/log/grafana/grafana.log
```

### Dashboard Loading Slow
```
1. Check query performance in Explore
2. Reduce time range
3. Use recording rules
4. Increase scrape interval
5. Reduce number of series
```

### Missing Data
```
1. Verify data source configuration
2. Check time range selection
3. Verify metric name and labels
4. Test query in Explore
5. Check data source connectivity
```

## Resources

- **Official Docs**: https://grafana.com/docs/
- **Play**: https://play.grafana.org
- **Dashboards**: https://grafana.com/grafana/dashboards
- **Plugins**: https://grafana.com/grafana/plugins
- **Community**: https://community.grafana.com
