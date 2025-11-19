# Grafana Dashboards Reference

## Dashboard Design Principles

### Information Architecture
```
Dashboard Hierarchy:
├── Executive Dashboard (Top-level business metrics)
├── Operations Dashboard (Real-time system health)
├── Detailed Dashboards (Device/service specific)
└── Investigation Dashboards (Troubleshooting tools)
```

### Visual Design Best Practices

#### Color Usage
```
Status Indicators:
- Green (#299C46): Up, healthy, normal
- Yellow (#F2F97D): Warning, caution
- Red (#FF3838): Critical, down, error
- Blue (#1F60C4): Informational

Gradients:
- Performance: Green → Yellow → Red
- Utilization: Green → Orange → Red
```

#### Panel Types & Use Cases

| Panel Type | Use Case | Best For |
|-----------|----------|----------|
| Time Series | Metrics over time | Bandwidth, errors, latency |
| Stat | Single metric value | Uptime %, device count |
| Gauge | Percentage/capacity | CPU%, memory, link util |
| Table | Multi-row data | Interface stats, device list |
| Bar Chart | Comparison | Top 10 talkers, protocol dist |
| Pie Chart | Composition | Traffic by application |
| Map | Geographic distribution | Site status, device location |
| Heatmap | Time-based patterns | Traffic patterns by hour |
| Dashboard List | Navigation | Main menu structure |

### Layout Principles
```
Key Rules:
1. Top-left: Most important metric (executive metric)
2. Left column: Status/health metrics
3. Right column: Trend/time series data
4. Bottom: Details and drill-down information

Grid sizing:
- Executive dashboard: 4 panels
- Operations dashboard: 12-16 panels
- Detail dashboard: 20+ panels
```

## Network Dashboard Templates

### Executive Dashboard
```json
{
  "dashboard": {
    "title": "Network Executive Dashboard",
    "panels": [
      {
        "title": "Network Availability",
        "targets": [
          {
            "expr": "(count(node_network_up == 1) / count(node_network_up)) * 100"
          }
        ],
        "type": "stat",
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "thresholds": {
              "mode": "percentage",
              "steps": [
                {"color": "red", "value": null},
                {"color": "yellow", "value": 95},
                {"color": "green", "value": 99.5}
              ]
            }
          }
        }
      },
      {
        "title": "Active Interfaces",
        "targets": [
          {
            "expr": "count(node_network_up == 1)"
          }
        ],
        "type": "stat"
      },
      {
        "title": "Total Network Traffic",
        "targets": [
          {
            "expr": "sum(rate(ifInOctets[5m])) * 8"
          }
        ],
        "type": "stat",
        "fieldConfig": {
          "defaults": {
            "unit": "bps"
          }
        }
      },
      {
        "title": "Critical Alerts",
        "targets": [
          {
            "expr": "count(ALERTS{severity='critical'})"
          }
        ],
        "type": "stat"
      }
    ]
  }
}
```

### Operations Dashboard
```json
{
  "dashboard": {
    "title": "Network Operations Center (NOC) Dashboard",
    "refresh": "30s",
    "panels": [
      {
        "title": "Device Status",
        "type": "table",
        "targets": [
          {
            "expr": "topk(20, sysUptime)"
          }
        ]
      },
      {
        "title": "Link Utilization (All Devices)",
        "type": "time_series",
        "targets": [
          {
            "expr": "((rate(ifInOctets[5m]) + rate(ifOutOctets[5m])) * 8 / ifSpeed) * 100"
          }
        ]
      },
      {
        "title": "Packet Errors (Last 24h)",
        "type": "bar",
        "targets": [
          {
            "expr": "topk(10, increase(ifInErrors[24h]))"
          }
        ]
      },
      {
        "title": "BGP Neighbors",
        "type": "stat",
        "targets": [
          {
            "expr": "count(bgp_neighbor_state == 1)"
          }
        ]
      },
      {
        "title": "Interface Errors Rate",
        "type": "time_series",
        "targets": [
          {
            "expr": "rate(ifInErrors[5m]) + rate(ifOutErrors[5m])"
          }
        ]
      },
      {
        "title": "Top Talkers",
        "type": "bar",
        "targets": [
          {
            "expr": "topk(10, rate(ifInOctets[5m]))"
          }
        ]
      }
    ]
  }
}
```

### Device Detail Dashboard
```json
{
  "dashboard": {
    "title": "Device Detail: $device",
    "templating": {
      "list": [
        {
          "name": "device",
          "type": "query",
          "datasource": "Prometheus",
          "query": "label_values(sysUptime, instance)"
        },
        {
          "name": "interface",
          "type": "query",
          "datasource": "Prometheus",
          "query": "label_values(ifInOctets{instance='$device'}, ifName)"
        }
      ]
    },
    "panels": [
      {
        "title": "System Uptime",
        "targets": [
          {
            "expr": "sysUptime{instance='$device'} / 100 / 86400"
          }
        ],
        "type": "stat",
        "fieldConfig": {
          "defaults": {
            "unit": "days"
          }
        }
      },
      {
        "title": "CPU Utilization",
        "targets": [
          {
            "expr": "sysLoad5{instance='$device'} * 100"
          }
        ],
        "type": "gauge"
      },
      {
        "title": "Memory Utilization",
        "targets": [
          {
            "expr": "(hrStorageUsed{instance='$device', hrStorageType='1.3.6.1.2.1.25.2.1.2'} / hrStorageSize) * 100"
          }
        ],
        "type": "gauge"
      },
      {
        "title": "Interface Status: $interface",
        "type": "time_series",
        "targets": [
          {
            "expr": "ifOperStatus{instance='$device', ifName='$interface'}"
          }
        ]
      },
      {
        "title": "Interface Throughput: $interface",
        "type": "time_series",
        "targets": [
          {
            "expr": "rate(ifInOctets{instance='$device', ifName='$interface'}[5m]) * 8"
          },
          {
            "expr": "-rate(ifOutOctets{instance='$device', ifName='$interface'}[5m]) * 8"
          }
        ]
      }
    ]
  }
}
```

### Troubleshooting Dashboard
```json
{
  "dashboard": {
    "title": "Network Troubleshooting",
    "panels": [
      {
        "title": "Recent Alerts",
        "type": "alert_list",
        "options": {
          "showOptions": "current",
          "maxItems": 20
        }
      },
      {
        "title": "Error Spike Detection",
        "type": "time_series",
        "targets": [
          {
            "expr": "increase(ifInErrors[5m] + ifOutErrors[5m])"
          }
        ],
        "alert": {
          "conditions": [
            {
              "evaluator": {"params": [100], "type": "gt"},
              "operator": {"type": "and"}
            }
          ]
        }
      },
      {
        "title": "Packet Loss Detection",
        "type": "bar",
        "targets": [
          {
            "expr": "topk(10, rate(ifInErrors[5m]) / rate(ifInPackets[5m]))"
          }
        ]
      },
      {
        "title": "Bandwidth Saturation",
        "type": "table",
        "targets": [
          {
            "expr": "topk(20, ((rate(ifInOctets[5m]) + rate(ifOutOctets[5m])) * 8 / ifSpeed) > 0.8)"
          }
        ]
      },
      {
        "title": "Circuit Quality (Jitter Detection)",
        "type": "time_series",
        "targets": [
          {
            "expr": "stddev(rate(rtt_ms[1m]))"
          }
        ]
      }
    ]
  }
}
```

## Dashboard Variables (Templating)

### Single Value Selection
```json
{
  "name": "device",
  "label": "Device",
  "type": "query",
  "datasource": "Prometheus",
  "query": "label_values(node_network_up, instance)",
  "multi": false
}
```

### Multi-Select Variables
```json
{
  "name": "sites",
  "label": "Sites",
  "type": "query",
  "datasource": "Prometheus",
  "query": "label_values(node_network_up, site)",
  "multi": true
}
```

### Custom Variables
```json
{
  "name": "time_range",
  "label": "Time Range",
  "type": "custom",
  "options": ["1h", "6h", "24h", "7d", "30d"],
  "current": {"text": "24h", "value": "24h"}
}
```

## Alert Integration

### Alert State Display
```json
{
  "panel": {
    "type": "alert_list",
    "options": {
      "showOptions": "current",
      "maxItems": 50,
      "sortOrder": 1,
      "dashboardAlerts": false
    }
  }
}
```

### Alert Annotation Tracking
```json
{
  "panel": {
    "type": "time_series",
    "options": {
      "tooltip": {
        "mode": "multi",
        "sort": "asc"
      }
    },
    "fieldConfig": {
      "custom": {
        "hideFrom": {
          "tooltip": false,
          "viz": false,
          "legend": false
        }
      }
    },
    "targets": [
      {
        "expr": "increase(ifInErrors[5m])",
        "annotations": true
      }
    ]
  }
}
```

## Advanced Features

### Heatmaps for Pattern Detection
```json
{
  "title": "Traffic Patterns Heatmap",
  "type": "heatmap",
  "targets": [
    {
      "expr": "histogram_quantile(0.95, rate(request_duration_seconds_bucket[5m]))"
    }
  ],
  "options": {
    "calculate": false,
    "cellGap": 1,
    "cellRadius": 2,
    "color": {
      "scheme": "Viridis"
    }
  }
}
```

### Service/Application Topology
```json
{
  "title": "Network Topology",
  "type": "nodeGraph",
  "targets": [
    {
      "expr": "netdev_carrier{job='network_devices'}"
    }
  ]
}
```

### Geo-Map for Geographic Monitoring
```json
{
  "title": "Site Status Map",
  "type": "geomap",
  "targets": [
    {
      "expr": "node_network_up",
      "format": "table"
    }
  ]
}
```

## Sharing & Collaboration

### Dashboard Permissions
```
1. Viewer: Read-only access
2. Editor: Can modify dashboard
3. Admin: Full access including sharing

Set at organization or folder level
```

### Public Dashboards
```
Enable public access:
Dashboard settings → Permissions → Public access
Share via URL with non-authenticated users
```

### Dashboard Versioning
```
Track changes via:
- Grafana audit log
- Git integration (provisioned dashboards)
- Backup external JSON exports
```

## Performance Optimization

### Panel Refresh Rates
```
Executive Dashboard: 1 minute (low overhead)
Operations Dashboard: 30 seconds (real-time feel)
Troubleshooting Dashboard: 5-10 seconds (reactive)
```

### Query Optimization
```
1. Use recording rules for pre-computed metrics
2. Increase scrape interval for non-critical metrics
3. Use metric_relabel to drop unnecessary labels
4. Aggregate at collection time, not query time
```

### Large Dashboard Handling
```
Split into multiple dashboards:
- Use dashboard lists for navigation
- Create hierarchical structure
- Limit panels per dashboard (12-16 optimal)
```

## Implementation Checklist

- [ ] Design dashboard hierarchy
- [ ] Create executive dashboard
- [ ] Build operations dashboard
- [ ] Develop device-specific dashboards
- [ ] Create troubleshooting dashboard
- [ ] Implement template variables
- [ ] Configure alerting annotations
- [ ] Test mobile responsiveness
- [ ] Set up sharing/permissions
- [ ] Document dashboard refresh rates
- [ ] Establish dashboard backup procedure
- [ ] Create dashboard review schedule

---

**Reference Type**: Visualization Best Practices
**Primary Tool**: Grafana (v8+)
**Update Frequency**: Quarterly
**Last Updated**: 2025-11-19
