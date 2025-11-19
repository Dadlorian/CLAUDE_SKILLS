# Grafana Reference Guide

## Table of Contents
1. [Dashboard Creation](#dashboard-creation)
2. [Panel Types and Visualization](#panel-types-and-visualization)
3. [Templating and Variables](#templating-and-variables)
4. [Alerting](#alerting)
5. [Data Sources](#data-sources)
6. [Best Practices](#best-practices)

---

## Dashboard Creation

### Dashboard Structure

A Grafana dashboard is composed of:
- **Rows**: Containers for organizing panels
- **Panels**: Individual visualizations (graphs, tables, stats, etc.)
- **Variables**: Dynamic filters for queries
- **Time range**: Global or per-panel time selection

### Creating a Dashboard

#### Via UI
1. Click "+" → "Dashboard"
2. Click "Add new panel"
3. Configure visualization and query
4. Save dashboard

#### Via JSON
```json
{
  "dashboard": {
    "title": "Application Performance",
    "tags": ["application", "performance"],
    "timezone": "browser",
    "editable": true,
    "graphTooltip": 1,
    "panels": [],
    "time": {
      "from": "now-6h",
      "to": "now"
    },
    "timepicker": {
      "refresh_intervals": ["5s", "10s", "30s", "1m", "5m", "15m", "30m", "1h", "2h", "1d"]
    },
    "refresh": "30s",
    "version": 1
  }
}
```

### Dashboard Settings

#### General Settings
```json
{
  "title": "Production Monitoring",
  "description": "Real-time monitoring of production services",
  "tags": ["production", "monitoring"],
  "timezone": "utc",
  "editable": true,
  "graphTooltip": 1,  // 0: Default, 1: Shared crosshair, 2: Shared tooltip
  "refresh": "30s"
}
```

#### Time Settings
```json
{
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {
    "refresh_intervals": ["10s", "30s", "1m", "5m", "15m", "30m", "1h"],
    "time_options": ["5m", "15m", "1h", "6h", "12h", "24h", "2d", "7d", "30d"]
  }
}
```

#### Links
```json
{
  "links": [
    {
      "title": "Related Dashboards",
      "type": "dashboards",
      "tags": ["production"],
      "asDropdown": true,
      "includeVars": true
    },
    {
      "title": "Runbook",
      "type": "link",
      "url": "https://runbooks.example.com/production",
      "targetBlank": true
    }
  ]
}
```

---

## Panel Types and Visualization

### Time Series (Graph)

Most common panel type for time-based data.

```json
{
  "type": "timeseries",
  "title": "Request Rate",
  "targets": [
    {
      "expr": "sum(rate(http_requests_total[5m]))",
      "legendFormat": "Total Requests/s",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "custom": {
        "drawStyle": "line",
        "lineInterpolation": "linear",
        "lineWidth": 2,
        "fillOpacity": 10,
        "showPoints": "never",
        "spanNulls": true
      },
      "unit": "reqps",
      "decimals": 2,
      "min": 0
    }
  },
  "options": {
    "tooltip": {
      "mode": "multi",
      "sort": "desc"
    },
    "legend": {
      "displayMode": "table",
      "placement": "bottom",
      "calcs": ["mean", "max", "last"]
    }
  }
}
```

#### Draw Styles
- **line**: Standard line graph
- **bars**: Bar chart
- **points**: Scatter plot

#### Line Interpolation
- **linear**: Straight lines between points
- **smooth**: Curved lines
- **stepBefore**: Step before data point
- **stepAfter**: Step after data point

### Stat Panel

Single value visualization with sparkline.

```json
{
  "type": "stat",
  "title": "Total Requests (24h)",
  "targets": [
    {
      "expr": "sum(increase(http_requests_total[24h]))",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "short",
      "decimals": 0,
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {
            "value": null,
            "color": "green"
          },
          {
            "value": 1000000,
            "color": "yellow"
          },
          {
            "value": 5000000,
            "color": "red"
          }
        ]
      }
    }
  },
  "options": {
    "graphMode": "area",
    "colorMode": "background",
    "orientation": "auto",
    "textMode": "value_and_name",
    "reduceOptions": {
      "values": false,
      "calcs": ["lastNotNull"]
    }
  }
}
```

### Gauge Panel

Circular or horizontal gauge for percentage values.

```json
{
  "type": "gauge",
  "title": "CPU Usage",
  "targets": [
    {
      "expr": "avg(instance:cpu_utilization:ratio) * 100",
      "refId": "A"
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
          {"value": null, "color": "green"},
          {"value": 70, "color": "yellow"},
          {"value": 90, "color": "red"}
        ]
      }
    }
  },
  "options": {
    "showThresholdLabels": true,
    "showThresholdMarkers": true,
    "orientation": "auto"
  }
}
```

### Bar Gauge

Horizontal or vertical bar representation.

```json
{
  "type": "bargauge",
  "title": "Service Health",
  "targets": [
    {
      "expr": "avg by (service) (up)",
      "legendFormat": "{{ service }}",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "percentunit",
      "min": 0,
      "max": 1,
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"value": null, "color": "red"},
          {"value": 0.5, "color": "yellow"},
          {"value": 0.9, "color": "green"}
        ]
      }
    }
  },
  "options": {
    "displayMode": "gradient",
    "orientation": "horizontal",
    "reduceOptions": {
      "values": false,
      "calcs": ["lastNotNull"]
    },
    "showUnfilled": true
  }
}
```

### Table Panel

Tabular data display with formatting.

```json
{
  "type": "table",
  "title": "Service Status",
  "targets": [
    {
      "expr": "up",
      "format": "table",
      "instant": true,
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "custom": {
        "align": "auto",
        "displayMode": "auto"
      }
    },
    "overrides": [
      {
        "matcher": {"id": "byName", "options": "Value"},
        "properties": [
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
                {"value": 1, "color": "green"}
              ]
            }
          }
        ]
      }
    ]
  },
  "options": {
    "showHeader": true,
    "sortBy": [
      {
        "displayName": "job",
        "desc": false
      }
    ]
  }
}
```

### Heatmap

Distribution of values over time.

```json
{
  "type": "heatmap",
  "title": "Request Duration Heatmap",
  "targets": [
    {
      "expr": "sum(increase(http_request_duration_seconds_bucket[5m])) by (le)",
      "format": "heatmap",
      "legendFormat": "{{ le }}",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "custom": {
        "hideFrom": {
          "tooltip": false,
          "viz": false,
          "legend": false
        }
      }
    }
  },
  "options": {
    "calculate": false,
    "cellGap": 2,
    "color": {
      "scheme": "Spectral",
      "steps": 128
    },
    "yAxis": {
      "unit": "s",
      "decimals": 2
    },
    "legend": {
      "show": true
    },
    "tooltip": {
      "show": true,
      "yHistogram": false
    }
  }
}
```

### Pie Chart

Distribution visualization.

```json
{
  "type": "piechart",
  "title": "Requests by Status Code",
  "targets": [
    {
      "expr": "sum by (status) (increase(http_requests_total[1h]))",
      "legendFormat": "{{ status }}",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "short"
    }
  },
  "options": {
    "pieType": "pie",
    "displayLabels": ["name", "percent"],
    "legend": {
      "displayMode": "table",
      "placement": "right",
      "values": ["value", "percent"]
    },
    "tooltip": {
      "mode": "single"
    }
  }
}
```

### State Timeline

Show state changes over time.

```json
{
  "type": "state-timeline",
  "title": "Service Availability",
  "targets": [
    {
      "expr": "up",
      "legendFormat": "{{ instance }}",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "custom": {
        "lineWidth": 0,
        "fillOpacity": 70
      },
      "mappings": [
        {
          "type": "value",
          "options": {
            "0": {
              "text": "Down",
              "color": "red"
            },
            "1": {
              "text": "Up",
              "color": "green"
            }
          }
        }
      ]
    }
  },
  "options": {
    "mergeValues": true,
    "showValue": "never",
    "alignValue": "left",
    "rowHeight": 0.9,
    "legend": {
      "displayMode": "list",
      "placement": "bottom"
    },
    "tooltip": {
      "mode": "single"
    }
  }
}
```

---

## Templating and Variables

Variables allow dashboards to be dynamic and reusable.

### Query Variable

Pull values from Prometheus queries.

```json
{
  "templating": {
    "list": [
      {
        "name": "job",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(up, job)",
        "refresh": 1,
        "sort": 1,
        "multi": true,
        "includeAll": true,
        "allValue": ".*",
        "regex": "",
        "current": {
          "selected": true,
          "text": "All",
          "value": "$__all"
        }
      }
    ]
  }
}
```

#### Variable Options
- **refresh**: 0 (never), 1 (on dashboard load), 2 (on time range change)
- **sort**: 0 (disabled), 1 (alphabetical asc), 2 (alphabetical desc), 3 (numerical asc), 4 (numerical desc), 5 (case-insensitive asc), 6 (case-insensitive desc)
- **multi**: Allow multiple selections
- **includeAll**: Add "All" option
- **allValue**: Value to use when "All" is selected (often ".*" for regex)

### Chained Variables

Variables that depend on other variables.

```json
{
  "templating": {
    "list": [
      {
        "name": "datacenter",
        "type": "query",
        "query": "label_values(up, datacenter)",
        "refresh": 1,
        "multi": false,
        "includeAll": false
      },
      {
        "name": "cluster",
        "type": "query",
        "query": "label_values(up{datacenter=\"$datacenter\"}, cluster)",
        "refresh": 1,
        "multi": false,
        "includeAll": false
      },
      {
        "name": "instance",
        "type": "query",
        "query": "label_values(up{datacenter=\"$datacenter\", cluster=\"$cluster\"}, instance)",
        "refresh": 2,
        "multi": true,
        "includeAll": true,
        "allValue": ".*"
      }
    ]
  }
}
```

### Custom Variable

Manually defined list of values.

```json
{
  "name": "environment",
  "type": "custom",
  "query": "production,staging,development",
  "multi": false,
  "includeAll": false,
  "current": {
    "text": "production",
    "value": "production"
  }
}
```

### Constant Variable

Hidden variable for storing values.

```json
{
  "name": "slo_target",
  "type": "constant",
  "query": "0.999",
  "hide": 2
}
```

### Interval Variable

Auto-adjusting time interval based on time range.

```json
{
  "name": "interval",
  "type": "interval",
  "query": "1m,5m,10m,30m,1h,6h,12h,1d,7d",
  "auto": true,
  "auto_count": 30,
  "auto_min": "1m",
  "current": {
    "text": "auto",
    "value": "$__auto_interval_interval"
  }
}
```

### Using Variables in Queries

```promql
# Simple variable usage
rate(http_requests_total{job="$job"}[5m])

# Multi-value variable with regex
rate(http_requests_total{job=~"$job"}[5m])

# Variable in legend
rate(http_requests_total{job=~"$job"}[$interval])

# Multiple variables
rate(http_requests_total{job=~"$job", instance=~"$instance"}[$interval])
```

### Advanced Variable Usage

#### Regex Filtering
```json
{
  "name": "instance",
  "type": "query",
  "query": "label_values(up{job=\"api-server\"}, instance)",
  "regex": "/([^:]+):.*/",  // Extract hostname before port
  "refresh": 1
}
```

#### Using Variables in Annotations
```json
{
  "annotations": {
    "list": [
      {
        "datasource": "Prometheus",
        "enable": true,
        "expr": "ALERTS{job=~\"$job\", alertstate=\"firing\"}",
        "iconColor": "red",
        "name": "Alerts",
        "tagKeys": "alertname,severity",
        "textFormat": "{{ alertname }}",
        "titleFormat": "Alert"
      }
    ]
  }
}
```

---

## Alerting

Grafana supports unified alerting (Grafana 8+) with alert rules, notification policies, and contact points.

### Alert Rules

```json
{
  "uid": "high_error_rate",
  "title": "High Error Rate",
  "condition": "B",
  "data": [
    {
      "refId": "A",
      "queryType": "range",
      "relativeTimeRange": {
        "from": 300,
        "to": 0
      },
      "datasourceUid": "prometheus-uid",
      "model": {
        "expr": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m]))",
        "refId": "A"
      }
    },
    {
      "refId": "B",
      "queryType": "",
      "datasourceUid": "__expr__",
      "model": {
        "type": "reduce",
        "expression": "A",
        "reducer": "last",
        "refId": "B"
      }
    },
    {
      "refId": "C",
      "queryType": "",
      "datasourceUid": "__expr__",
      "model": {
        "type": "threshold",
        "expression": "B",
        "conditions": [
          {
            "evaluator": {
              "params": [0.05],
              "type": "gt"
            }
          }
        ],
        "refId": "C"
      }
    }
  ],
  "noDataState": "NoData",
  "execErrState": "Error",
  "for": "5m",
  "annotations": {
    "description": "Error rate is above 5% for the last 5 minutes",
    "runbook_url": "https://runbooks.example.com/high-error-rate",
    "summary": "High error rate detected"
  },
  "labels": {
    "severity": "warning",
    "team": "backend"
  }
}
```

### Alert States

- **Normal**: Alert condition is false
- **Pending**: Alert condition is true but hasn't exceeded `for` duration
- **Alerting**: Alert condition has been true for longer than `for` duration
- **NoData**: No data received
- **Error**: Error evaluating the alert

### Contact Points

```json
{
  "name": "email-ops",
  "type": "email",
  "settings": {
    "addresses": "ops@example.com",
    "singleEmail": true
  },
  "disableResolveMessage": false
}
```

#### Slack Contact Point
```json
{
  "name": "slack-alerts",
  "type": "slack",
  "settings": {
    "url": "https://hooks.slack.com/services/XXX/YYY/ZZZ",
    "recipient": "#alerts",
    "username": "Grafana",
    "icon_emoji": ":grafana:",
    "mentionChannel": "here",
    "text": "{{ range .Alerts }}\n*Alert:* {{ .Labels.alertname }}\n*Status:* {{ .Status }}\n*Severity:* {{ .Labels.severity }}\n*Summary:* {{ .Annotations.summary }}\n*Description:* {{ .Annotations.description }}\n{{ end }}"
  }
}
```

#### PagerDuty Contact Point
```json
{
  "name": "pagerduty-critical",
  "type": "pagerduty",
  "settings": {
    "integrationKey": "your-integration-key",
    "severity": "critical",
    "class": "production",
    "component": "api-server"
  }
}
```

### Notification Policies

```json
{
  "receiver": "default-receiver",
  "group_by": ["alertname", "cluster"],
  "group_wait": "30s",
  "group_interval": "5m",
  "repeat_interval": "4h",
  "routes": [
    {
      "receiver": "slack-alerts",
      "matchers": [
        {
          "name": "severity",
          "value": "warning",
          "isRegex": false
        }
      ],
      "group_by": ["alertname"],
      "continue": true
    },
    {
      "receiver": "pagerduty-critical",
      "matchers": [
        {
          "name": "severity",
          "value": "critical",
          "isRegex": false
        }
      ],
      "group_wait": "10s",
      "repeat_interval": "30m"
    }
  ]
}
```

---

## Data Sources

### Prometheus Data Source

```json
{
  "name": "Prometheus",
  "type": "prometheus",
  "access": "proxy",
  "url": "http://prometheus:9090",
  "jsonData": {
    "timeInterval": "15s",
    "queryTimeout": "60s",
    "httpMethod": "POST",
    "customQueryParameters": "",
    "cacheLevel": "High"
  }
}
```

### Loki Data Source

```json
{
  "name": "Loki",
  "type": "loki",
  "access": "proxy",
  "url": "http://loki:3100",
  "jsonData": {
    "maxLines": 1000,
    "derivedFields": [
      {
        "name": "TraceID",
        "matcherRegex": "trace_id=(\\w+)",
        "url": "http://jaeger:16686/trace/$${__value.raw}",
        "datasourceUid": "jaeger-uid"
      }
    ]
  }
}
```

### Jaeger Data Source

```json
{
  "name": "Jaeger",
  "type": "jaeger",
  "access": "proxy",
  "url": "http://jaeger:16686",
  "jsonData": {
    "tracesToLogs": {
      "datasourceUid": "loki-uid",
      "tags": ["pod", "namespace"],
      "mappedTags": [
        {
          "key": "service.name",
          "value": "job"
        }
      ],
      "spanStartTimeShift": "-1h",
      "spanEndTimeShift": "1h",
      "filterByTraceID": true,
      "filterBySpanID": false
    }
  }
}
```

---

## Best Practices

### Dashboard Design

1. **Organize with rows**
   - Group related panels together
   - Use collapsible rows for detailed metrics
   - Keep overview metrics always visible

2. **Consistent time ranges**
   - Use dashboard time range when possible
   - Override only when necessary (e.g., comparing with historical data)

3. **Meaningful titles and descriptions**
   - Clear, concise panel titles
   - Add descriptions for complex visualizations
   - Use annotations to explain spikes or anomalies

4. **Appropriate refresh rates**
   - Production: 30s - 1m
   - Development: 5s - 10s
   - Historical analysis: Disable auto-refresh

5. **Performance optimization**
   - Use recording rules for expensive queries
   - Limit number of panels per dashboard (< 20-30)
   - Use appropriate time ranges
   - Cache query results when possible

### Visualization Selection

1. **Time series graphs** for trends over time
2. **Stat panels** for single values and KPIs
3. **Gauges** for percentage-based metrics
4. **Tables** for detailed breakdowns
5. **Heatmaps** for distribution analysis
6. **Pie charts** for composition (use sparingly)

### Templating Best Practices

1. **Use descriptive variable names**
   - `environment` instead of `env`
   - `service_name` instead of `svc`

2. **Provide sensible defaults**
   - Default to most commonly used values
   - Consider "All" for overview dashboards

3. **Limit multi-select variables**
   - Too many selections can make queries slow
   - Use with caution on high-cardinality labels

4. **Chain variables logically**
   - Region → Cluster → Namespace → Service
   - Make dependencies clear in variable order

### Query Optimization

1. **Use recording rules**
   ```promql
   # Instead of this in multiple panels:
   histogram_quantile(0.95,
     sum by (le) (rate(http_request_duration_seconds_bucket[5m]))
   )

   # Use a recording rule:
   http_request_duration:p95
   ```

2. **Limit time ranges**
   - Use `$__range` variable for dynamic ranges
   - Avoid unnecessarily long time ranges

3. **Use variables for intervals**
   ```promql
   rate(http_requests_total[$__rate_interval])
   ```

4. **Aggregate before functions**
   ```promql
   # Good
   histogram_quantile(0.95,
     sum by (le) (rate(http_request_duration_seconds_bucket[5m]))
   )

   # Bad
   histogram_quantile(0.95,
     rate(http_request_duration_seconds_bucket[5m])
   )
   ```

### Alerting Best Practices

1. **Meaningful alert names**
   - Clear, action-oriented names
   - Include affected component

2. **Comprehensive annotations**
   - Summary: One-line description
   - Description: Detailed context
   - Runbook URL: Link to troubleshooting steps

3. **Appropriate thresholds**
   - Based on SLOs and historical data
   - Avoid alerting on noise

4. **Proper severity levels**
   - Critical: Immediate action required
   - Warning: Investigate during business hours
   - Info: For awareness only

5. **Use `for` duration**
   - Avoid alerting on transient issues
   - Balance between false positives and response time

### Access Control

1. **Use folders for organization**
   - Organize by team, service, or environment
   - Set folder-level permissions

2. **Implement RBAC**
   - Viewer: Read-only access
   - Editor: Can modify dashboards
   - Admin: Full control

3. **Use teams**
   - Create teams based on organizational structure
   - Assign permissions to teams, not individuals

### Version Control

1. **Export dashboards as JSON**
   - Store in version control (Git)
   - Use CI/CD for deployment

2. **Use provisioning**
   ```yaml
   # dashboards.yml
   apiVersion: 1
   providers:
     - name: 'default'
       orgId: 1
       folder: ''
       type: file
       options:
         path: /etc/grafana/provisioning/dashboards
   ```

3. **Document changes**
   - Use dashboard version history
   - Add comments in JSON for complex configurations

### Naming Conventions

1. **Dashboards**
   - `[Environment] Service Name - Component`
   - Example: `Production API Server - Performance`

2. **Panels**
   - Descriptive and concise
   - Include units when relevant
   - Example: `Request Rate (req/s)`

3. **Variables**
   - Lowercase with underscores
   - Example: `service_name`, `environment`, `time_range`

### Performance Tips

1. **Limit concurrent queries**
   - Default: 4 concurrent queries per panel
   - Increase cautiously based on data source capacity

2. **Use query caching**
   - Enable caching in data source settings
   - Set appropriate TTL

3. **Optimize panel queries**
   - Use `instant` queries for current values
   - Use `range` queries for time series
   - Avoid unnecessary `sort` operations

4. **Dashboard links**
   - Link to detailed dashboards instead of embedding all metrics
   - Create drill-down hierarchies
