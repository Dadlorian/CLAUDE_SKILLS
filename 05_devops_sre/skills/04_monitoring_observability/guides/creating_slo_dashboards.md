# Creating SLO Dashboards Guide

This guide walks you through creating comprehensive SLO (Service Level Objective) dashboards in Grafana with Prometheus as the data source.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Setting Up SLI Recording Rules](#setting-up-sli-recording-rules)
3. [Creating the Main SLO Dashboard](#creating-the-main-slo-dashboard)
4. [Building Individual SLO Panels](#building-individual-slo-panels)
5. [Error Budget Visualization](#error-budget-visualization)
6. [Multi-Window Burn Rate Alerts](#multi-window-burn-rate-alerts)
7. [SLO Report Dashboard](#slo-report-dashboard)
8. [Best Practices](#best-practices)

---

## Prerequisites

- Prometheus running and collecting metrics
- Grafana installed and configured
- Application metrics available (HTTP requests, latency, etc.)
- Basic understanding of PromQL

---

## Setting Up SLI Recording Rules

First, we need to create recording rules for our SLIs.

Create `/etc/prometheus/rules/slo_recording_rules.yml`:

```yaml
groups:
  - name: slo_availability_recording_rules
    interval: 30s
    rules:
      # API Availability SLI
      - record: slo:api:availability:good_events:rate5m
        expr: |
          sum(rate(http_requests_total{
            job="api-server",
            status=~"[2-4].."
          }[5m]))

      - record: slo:api:availability:total_events:rate5m
        expr: |
          sum(rate(http_requests_total{job="api-server"}[5m]))

      - record: slo:api:availability:success_ratio:rate5m
        expr: |
          slo:api:availability:good_events:rate5m
          /
          slo:api:availability:total_events:rate5m

      # Calculate over different time windows for multi-window alerting
      - record: slo:api:availability:success_ratio:rate1h
        expr: |
          sum(increase(http_requests_total{
            job="api-server",
            status=~"[2-4].."
          }[1h]))
          /
          sum(increase(http_requests_total{job="api-server"}[1h]))

      - record: slo:api:availability:success_ratio:rate6h
        expr: |
          sum(increase(http_requests_total{
            job="api-server",
            status=~"[2-4].."
          }[6h]))
          /
          sum(increase(http_requests_total{job="api-server"}[6h]))

      - record: slo:api:availability:success_ratio:rate24h
        expr: |
          sum(increase(http_requests_total{
            job="api-server",
            status=~"[2-4].."
          }[24h]))
          /
          sum(increase(http_requests_total{job="api-server"}[24h]))

      - record: slo:api:availability:success_ratio:rate30d
        expr: |
          sum(increase(http_requests_total{
            job="api-server",
            status=~"[2-4].."
          }[30d]))
          /
          sum(increase(http_requests_total{job="api-server"}[30d]))

  - name: slo_latency_recording_rules
    interval: 30s
    rules:
      # Latency SLI (95% of requests < 100ms)
      - record: slo:api:latency_100ms:good_events:rate5m
        expr: |
          sum(rate(http_request_duration_seconds_bucket{
            job="api-server",
            le="0.1"
          }[5m]))

      - record: slo:api:latency_100ms:total_events:rate5m
        expr: |
          sum(rate(http_request_duration_seconds_count{
            job="api-server"
          }[5m]))

      - record: slo:api:latency_100ms:success_ratio:rate5m
        expr: |
          slo:api:latency_100ms:good_events:rate5m
          /
          slo:api:latency_100ms:total_events:rate5m

      # 30-day latency SLI
      - record: slo:api:latency_100ms:success_ratio:rate30d
        expr: |
          sum(increase(http_request_duration_seconds_bucket{
            job="api-server",
            le="0.1"
          }[30d]))
          /
          sum(increase(http_request_duration_seconds_count{
            job="api-server"
          }[30d]))

  - name: slo_error_budget_rules
    interval: 30s
    rules:
      # Error budget consumption rate (for 99.9% SLO)
      # SLO target
      - record: slo:api:target
        expr: 0.999

      # Current error ratio (5m)
      - record: slo:api:error_ratio:rate5m
        expr: |
          1 - slo:api:availability:success_ratio:rate5m

      # Error budget (total allowable error)
      - record: slo:api:error_budget:total
        expr: |
          1 - slo:api:target

      # Burn rate (how fast we're consuming error budget)
      - record: slo:api:error_budget:burn_rate:rate1h
        expr: |
          (1 - slo:api:availability:success_ratio:rate1h)
          /
          (1 - slo:api:target)

      - record: slo:api:error_budget:burn_rate:rate6h
        expr: |
          (1 - slo:api:availability:success_ratio:rate6h)
          /
          (1 - slo:api:target)

      - record: slo:api:error_budget:burn_rate:rate24h
        expr: |
          (1 - slo:api:availability:success_ratio:rate24h)
          /
          (1 - slo:api:target)

      # Error budget remaining (30-day window)
      - record: slo:api:error_budget:remaining:ratio30d
        expr: |
          (
            (1 - slo:api:target) -
            (1 - slo:api:availability:success_ratio:rate30d)
          )
          /
          (1 - slo:api:target)
```

Reload Prometheus:

```bash
promtool check rules /etc/prometheus/rules/slo_recording_rules.yml
curl -X POST http://localhost:9090/-/reload
```

---

## Creating the Main SLO Dashboard

### Dashboard JSON Structure

Create a new Grafana dashboard or import this JSON:

```json
{
  "dashboard": {
    "title": "Service Level Objectives (SLO)",
    "tags": ["slo", "sli", "reliability"],
    "timezone": "browser",
    "refresh": "30s",
    "time": {
      "from": "now-7d",
      "to": "now"
    },
    "panels": [],
    "templating": {
      "list": [
        {
          "name": "slo_target",
          "type": "constant",
          "current": {
            "value": "0.999",
            "text": "99.9%"
          },
          "hide": 2
        },
        {
          "name": "window",
          "type": "custom",
          "query": "1h,6h,24h,7d,30d",
          "current": {
            "value": "30d",
            "text": "30 days"
          },
          "multi": false
        }
      ]
    }
  }
}
```

---

## Building Individual SLO Panels

### Panel 1: Current SLI vs SLO Target

**Panel Type:** Gauge

**Query:**
```promql
slo:api:availability:success_ratio:rate30d
```

**Configuration:**
```json
{
  "type": "gauge",
  "title": "API Availability (30-day)",
  "targets": [
    {
      "expr": "slo:api:availability:success_ratio:rate30d",
      "legendFormat": "Current SLI"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "percentunit",
      "min": 0.995,
      "max": 1.0,
      "decimals": 4,
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"value": null, "color": "red"},
          {"value": 0.999, "color": "yellow"},
          {"value": 0.9995, "color": "green"}
        ]
      },
      "mappings": []
    }
  },
  "options": {
    "showThresholdLabels": true,
    "showThresholdMarkers": true
  }
}
```

### Panel 2: Error Budget Remaining

**Panel Type:** Bar Gauge

**Query:**
```promql
slo:api:error_budget:remaining:ratio30d * 100
```

**Configuration:**
```json
{
  "type": "bargauge",
  "title": "Error Budget Remaining (30-day)",
  "targets": [
    {
      "expr": "slo:api:error_budget:remaining:ratio30d * 100",
      "legendFormat": "Error Budget %"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "percent",
      "min": 0,
      "max": 100,
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"value": null, "color": "red"},
          {"value": 20, "color": "orange"},
          {"value": 50, "color": "yellow"},
          {"value": 75, "color": "green"}
        ]
      }
    }
  },
  "options": {
    "displayMode": "gradient",
    "orientation": "horizontal"
  }
}
```

### Panel 3: SLI Trend Over Time

**Panel Type:** Time Series

**Queries:**
```promql
# Current SLI
slo:api:availability:success_ratio:rate5m

# SLO Target (horizontal line)
slo:api:target
```

**Configuration:**
```json
{
  "type": "timeseries",
  "title": "Availability SLI Trend",
  "targets": [
    {
      "expr": "slo:api:availability:success_ratio:rate5m",
      "legendFormat": "Current SLI (5m)"
    },
    {
      "expr": "slo:api:target",
      "legendFormat": "SLO Target (99.9%)"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "percentunit",
      "decimals": 4,
      "custom": {
        "drawStyle": "line",
        "lineWidth": 2,
        "fillOpacity": 10,
        "spanNulls": true
      },
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"value": null, "color": "green"},
          {"value": 0.999, "color": "red"}
        ]
      }
    },
    "overrides": [
      {
        "matcher": {"id": "byName", "options": "SLO Target (99.9%)"},
        "properties": [
          {
            "id": "custom.lineStyle",
            "value": {"fill": "dash"}
          },
          {
            "id": "color",
            "value": {"mode": "fixed", "fixedColor": "red"}
          }
        ]
      }
    ]
  }
}
```

### Panel 4: Error Budget Burn Rate

**Panel Type:** Time Series

**Queries:**
```promql
# 1-hour burn rate
slo:api:error_budget:burn_rate:rate1h

# 24-hour burn rate
slo:api:error_budget:burn_rate:rate24h

# Sustainable burn rate (1.0)
1
```

**Configuration:**
```json
{
  "type": "timeseries",
  "title": "Error Budget Burn Rate",
  "targets": [
    {
      "expr": "slo:api:error_budget:burn_rate:rate1h",
      "legendFormat": "1h Burn Rate"
    },
    {
      "expr": "slo:api:error_budget:burn_rate:rate24h",
      "legendFormat": "24h Burn Rate"
    },
    {
      "expr": "1",
      "legendFormat": "Sustainable (1.0x)"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "short",
      "decimals": 2,
      "custom": {
        "drawStyle": "line",
        "lineWidth": 2
      },
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"value": null, "color": "green"},
          {"value": 2, "color": "yellow"},
          {"value": 10, "color": "red"}
        ]
      }
    }
  },
  "options": {
    "tooltip": {
      "mode": "multi"
    },
    "legend": {
      "displayMode": "table",
      "placement": "bottom",
      "calcs": ["mean", "max", "last"]
    }
  }
}
```

### Panel 5: Request Volume

**Panel Type:** Time Series

**Query:**
```promql
sum(rate(http_requests_total{job="api-server"}[5m]))
```

**Configuration:**
```json
{
  "type": "timeseries",
  "title": "Request Rate",
  "targets": [
    {
      "expr": "sum(rate(http_requests_total{job=\"api-server\"}[5m]))",
      "legendFormat": "Requests/sec"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "reqps",
      "custom": {
        "drawStyle": "line",
        "fillOpacity": 20
      }
    }
  }
}
```

### Panel 6: Error Rate

**Panel Type:** Time Series

**Query:**
```promql
sum(rate(http_requests_total{job="api-server",status=~"5.."}[5m]))
```

**Configuration:**
```json
{
  "type": "timeseries",
  "title": "Error Rate (5xx)",
  "targets": [
    {
      "expr": "sum(rate(http_requests_total{job=\"api-server\",status=~\"5..\"}[5m]))",
      "legendFormat": "Errors/sec"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "reqps",
      "custom": {
        "drawStyle": "line",
        "fillOpacity": 20
      },
      "color": {
        "mode": "fixed",
        "fixedColor": "red"
      }
    }
  }
}
```

---

## Error Budget Visualization

### Panel 7: Error Budget Consumption Over Time

**Panel Type:** Time Series (Stacked Area)

**Query:**
```promql
# Error budget consumed (cumulative)
(
  1 - (
    sum(increase(http_requests_total{job="api-server",status=~"[2-4].."}[1h]))
    /
    sum(increase(http_requests_total{job="api-server"}[1h]))
  )
)
/
(1 - 0.999) * 100
```

**Configuration:**
```json
{
  "type": "timeseries",
  "title": "Error Budget Consumption (% of total budget)",
  "targets": [
    {
      "expr": "(1 - (sum(increase(http_requests_total{job=\"api-server\",status=~\"[2-4]..\"}[1h])) / sum(increase(http_requests_total{job=\"api-server\"}[1h])))) / (1 - 0.999) * 100",
      "legendFormat": "Budget Consumed %"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "percent",
      "min": 0,
      "max": 100,
      "custom": {
        "drawStyle": "line",
        "fillOpacity": 30,
        "lineWidth": 2
      },
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"value": null, "color": "green"},
          {"value": 50, "color": "yellow"},
          {"value": 80, "color": "orange"},
          {"value": 100, "color": "red"}
        ]
      }
    }
  }
}
```

### Panel 8: Time Until Error Budget Exhaustion

**Panel Type:** Stat

**Query:**
```promql
# Estimated hours until budget exhausted (simplified)
(
  slo:api:error_budget:remaining:ratio30d
  /
  (1 - slo:api:availability:success_ratio:rate1h)
) * 720  # 30 days in hours
```

**Configuration:**
```json
{
  "type": "stat",
  "title": "Hours Until Budget Exhausted (at current rate)",
  "targets": [
    {
      "expr": "(slo:api:error_budget:remaining:ratio30d / (1 - slo:api:availability:success_ratio:rate1h)) * 720",
      "legendFormat": "Hours"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "h",
      "decimals": 1,
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"value": null, "color": "red"},
          {"value": 24, "color": "orange"},
          {"value": 72, "color": "yellow"},
          {"value": 168, "color": "green"}
        ]
      }
    }
  },
  "options": {
    "colorMode": "background",
    "graphMode": "area",
    "textMode": "value_and_name"
  }
}
```

---

## Multi-Window Burn Rate Alerts

### Panel 9: Burn Rate Alert Status

**Panel Type:** State Timeline

**Queries:**
```promql
# Fast burn (14.4x over 1h)
(slo:api:error_budget:burn_rate:rate1h > 14.4) * 3

# Medium burn (6x over 6h)
(slo:api:error_budget:burn_rate:rate6h > 6) * 2

# Slow burn (3x over 24h)
(slo:api:error_budget:burn_rate:rate24h > 3) * 1
```

**Configuration:**
```json
{
  "type": "state-timeline",
  "title": "Burn Rate Alert Levels",
  "targets": [
    {
      "expr": "(slo:api:error_budget:burn_rate:rate1h > 14.4) * 3",
      "legendFormat": "Critical (14.4x / 1h)"
    },
    {
      "expr": "(slo:api:error_budget:burn_rate:rate6h > 6) * 2",
      "legendFormat": "High (6x / 6h)"
    },
    {
      "expr": "(slo:api:error_budget:burn_rate:rate24h > 3) * 1",
      "legendFormat": "Medium (3x / 24h)"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "custom": {
        "fillOpacity": 70
      },
      "mappings": [
        {
          "type": "value",
          "options": {
            "0": {"text": "OK", "color": "green"},
            "1": {"text": "Medium", "color": "yellow"},
            "2": {"text": "High", "color": "orange"},
            "3": {"text": "Critical", "color": "red"}
          }
        }
      ]
    }
  }
}
```

---

## SLO Report Dashboard

### Panel 10: SLO Compliance Table

**Panel Type:** Table

**Queries:**
```promql
# Availability (30d)
slo:api:availability:success_ratio:rate30d

# Latency (30d)
slo:api:latency_100ms:success_ratio:rate30d

# Error budget remaining
slo:api:error_budget:remaining:ratio30d * 100
```

**Configuration:**
```json
{
  "type": "table",
  "title": "SLO Compliance Summary (30-day)",
  "targets": [
    {
      "expr": "slo:api:availability:success_ratio:rate30d",
      "format": "table",
      "instant": true,
      "legendFormat": "Availability"
    },
    {
      "expr": "slo:api:latency_100ms:success_ratio:rate30d",
      "format": "table",
      "instant": true,
      "legendFormat": "Latency"
    },
    {
      "expr": "slo:api:error_budget:remaining:ratio30d * 100",
      "format": "table",
      "instant": true,
      "legendFormat": "Error Budget %"
    }
  ],
  "fieldConfig": {
    "overrides": [
      {
        "matcher": {"id": "byName", "options": "Value"},
        "properties": [
          {
            "id": "unit",
            "value": "percentunit"
          },
          {
            "id": "decimals",
            "value": 4
          },
          {
            "id": "custom.displayMode",
            "value": "color-background"
          },
          {
            "id": "thresholds",
            "value": {
              "mode": "absolute",
              "steps": [
                {"value": null, "color": "red"},
                {"value": 0.999, "color": "green"}
              ]
            }
          }
        ]
      }
    ]
  }
}
```

### Panel 11: Historical SLO Compliance

**Panel Type:** Time Series (Heatmap alternative)

**Query:**
```promql
# Show SLI over last 30 days with 1-hour resolution
avg_over_time(slo:api:availability:success_ratio:rate1h[30d:1h])
```

---

## Best Practices

### 1. Dashboard Organization

Organize panels in logical groups:
- **Overview Row**: Current SLI, error budget remaining
- **Trends Row**: SLI over time, burn rate
- **Details Row**: Request volume, error rate, latency
- **Alerts Row**: Burn rate alert status

### 2. Use Consistent Colors

- **Green**: SLO met, healthy state
- **Yellow**: Warning, approaching SLO
- **Orange**: Error budget critical
- **Red**: SLO violated, error budget exhausted

### 3. Add Annotations

```json
{
  "annotations": {
    "list": [
      {
        "datasource": "Prometheus",
        "enable": true,
        "expr": "ALERTS{alertname=~\"SLO.*\", alertstate=\"firing\"}",
        "iconColor": "red",
        "name": "SLO Alerts",
        "tagKeys": "alertname,severity",
        "titleFormat": "{{ alertname }}",
        "textFormat": "{{ annotations.summary }}"
      },
      {
        "datasource": "-- Grafana --",
        "enable": true,
        "iconColor": "blue",
        "name": "Deployments",
        "tags": ["deployment"]
      }
    ]
  }
}
```

### 4. Template Variables for Multiple Services

```json
{
  "templating": {
    "list": [
      {
        "name": "service",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(http_requests_total, job)",
        "refresh": 1,
        "multi": false
      }
    ]
  }
}
```

Update queries to use variable:
```promql
slo:$service:availability:success_ratio:rate30d
```

### 5. Link to Related Dashboards

```json
{
  "links": [
    {
      "title": "Service Dashboard",
      "type": "link",
      "url": "/d/service-overview",
      "targetBlank": false
    },
    {
      "title": "Incident Log",
      "type": "link",
      "url": "/d/incident-log",
      "targetBlank": true
    }
  ]
}
```

### 6. Add Documentation

Use text panels to document:
- SLO targets and rationale
- Error budget policy
- Links to runbooks
- Contact information

```json
{
  "type": "text",
  "title": "SLO Policy",
  "content": "## API Service SLO\\n\\n**Target:** 99.9% availability over 30 days\\n\\n**Error Budget Policy:**\\n- >50% remaining: Normal development\\n- 20-50% remaining: Increased scrutiny\\n- <20% remaining: Feature freeze\\n\\n**Runbook:** [Link](https://runbooks.example.com/slo)"
}
```

---

## Complete Dashboard JSON

Here's a complete dashboard combining all panels:

```json
{
  "dashboard": {
    "title": "Service Level Objectives",
    "uid": "slo-dashboard",
    "tags": ["slo", "reliability"],
    "timezone": "browser",
    "refresh": "30s",
    "time": {
      "from": "now-7d",
      "to": "now"
    },
    "templating": {
      "list": [
        {
          "name": "slo_target",
          "type": "constant",
          "current": {"value": "0.999"},
          "hide": 2
        }
      ]
    },
    "panels": [
      {
        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
        "type": "gauge",
        "title": "Availability (30d)",
        "targets": [
          {
            "expr": "slo:api:availability:success_ratio:rate30d"
          }
        ]
      },
      {
        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0},
        "type": "bargauge",
        "title": "Error Budget Remaining",
        "targets": [
          {
            "expr": "slo:api:error_budget:remaining:ratio30d * 100"
          }
        ]
      },
      {
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
        "type": "stat",
        "title": "SLO Summary",
        "targets": [
          {
            "expr": "slo:api:availability:success_ratio:rate30d"
          }
        ]
      }
    ]
  }
}
```

---

## Provisioning Dashboards

To provision the dashboard automatically:

Create `/etc/grafana/provisioning/dashboards/slo.yml`:

```yaml
apiVersion: 1

providers:
  - name: 'SLO Dashboards'
    orgId: 1
    folder: 'SLO'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards/slo
```

Place dashboard JSON in `/var/lib/grafana/dashboards/slo/main-slo-dashboard.json`.

---

## Conclusion

You now have comprehensive SLO dashboards that show:
- Current SLI vs SLO target
- Error budget remaining and consumption rate
- Burn rate alerts
- Historical trends
- Compliance reports

These dashboards enable data-driven decisions about reliability vs. feature development velocity.

Next steps:
- Set up multi-window burn rate alerts
- Create per-service SLO dashboards
- Implement error budget policies
- Integrate with incident management
- Build executive SLO reports
