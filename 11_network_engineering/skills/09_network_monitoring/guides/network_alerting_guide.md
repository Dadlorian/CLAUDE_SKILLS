# Network Alerting Guide

## Alert Strategy Framework

### Severity Levels

#### Critical (Severity 1)
```
Definition: Immediate impact, customer-facing outage
Response Time: 5 minutes
Escalation: Page on-call immediately
Examples:
  - BGP neighbor down
  - Internet link down
  - Critical device unreachable
  - Packet loss > 5%

Action: Emergency response
  1. Acknowledge alert
  2. Investigate root cause
  3. Implement workaround
  4. Permanent fix
  5. Post-mortem review
```

#### Warning (Severity 2)
```
Definition: Potential issue, needs investigation
Response Time: 1 hour
Escalation: Team notification
Examples:
  - Link utilization > 80%
  - CPU utilization > 90%
  - Error rate > 1%
  - Interface flapping

Action: Planned investigation
  1. Verify the alert
  2. Gather context
  3. Diagnose issue
  4. Plan remediation
  5. Execute fix
```

#### Info (Severity 3)
```
Definition: Awareness, normal behavior
Response Time: Next business day
Escalation: Log and track
Examples:
  - Interface up/down
  - Configuration change
  - Routine maintenance
  - Policy enforcement

Action: Trending and reporting
  1. Log event
  2. Correlate with others
  3. Trend analysis
  4. Capacity planning
```

## Alert Rule Design

### Rule Development Process

#### Step 1: Define Metric
```
Good:
  - "BGP neighbor state"
  - "Interface utilization percentage"
  - "Packet loss rate"

Bad:
  - "Network is slow"
  - "Something is wrong"
  - "High traffic"

Metric must be:
  - Quantifiable
  - Measurable
  - Observable from monitoring system
```

#### Step 2: Set Threshold
```
Methodology:
  1. Establish baseline (2-4 weeks data)
  2. Calculate percentile (usually p95 or p99)
  3. Add safety margin (10-20%)
  4. Set threshold

Example:
  Baseline p95 interface util: 60%
  Safety margin: +15%
  Threshold: 75%

Alert at: 75% for 10 minutes
```

#### Step 3: Set Duration
```
Purpose: Filter out spikes
Reduces false positives

Examples:
  - Interface down: 2 minutes (brief blips acceptable)
  - High CPU: 10 minutes (transient spikes ok)
  - Link saturation: 10 minutes (sustained congestion)
  - Packet loss: 2 minutes (immediate visibility)

Rule of thumb:
  Critical: 1-5 minutes
  Warning: 5-15 minutes
  Info: 30-60 minutes
```

## Alert Rule Examples

### Prometheus AlertManager Rules

#### Interface Availability
```yaml
groups:
  - name: network_interface_alerts
    rules:
      - alert: InterfaceDown
        expr: node_network_up == 0
        for: 2m
        labels:
          severity: critical
          service: network
        annotations:
          summary: "Interface down: {{ $labels.device }}/{{ $labels.interface }}"
          description: "Interface {{ $labels.interface }} on {{ $labels.device }} is down"
          runbook: "https://wiki.example.com/runbooks/interface-down"
          dashboard: "http://grafana.example.com/d/interface-status"
```

#### Bandwidth Utilization
```yaml
      - alert: LinkSaturation
        expr: |
          ((rate(ifInOctets[5m]) + rate(ifOutOctets[5m])) * 8 / ifSpeed) > 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Link {{ $labels.instance }}/{{ $labels.ifName }} utilization >80%"
          description: "Current utilization: {{ humanize $value }}%"
          value: "{{ $value | humanizePercentage }}"
```

#### Packet Loss Detection
```yaml
      - alert: HighPacketLoss
        expr: |
          (rate(ifInErrors[5m]) + rate(ifOutErrors[5m])) /
          (rate(ifInPackets[5m]) + rate(ifOutPackets[5m])) > 0.01
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Packet loss >1% on {{ $labels.instance }}"
          description: "Loss rate: {{ $value | humanizePercentage }}"
```

#### BGP Neighbor Status
```yaml
      - alert: BGPNeighborDown
        expr: bgp_neighbor_state == 0
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "BGP neighbor {{ $labels.neighbor }} is down"
          description: "BGP session to {{ $labels.neighbor }} on device {{ $labels.device }} is not established"
```

#### Device Reachability
```yaml
      - alert: DeviceUnreachable
        expr: up == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Device {{ $labels.instance }} is unreachable"
          description: "Cannot scrape metrics from {{ $labels.instance }}"
```

## Alert Tuning

### Reducing False Positives

#### Use Aggregation
```yaml
# Bad (too sensitive)
- alert: HighCPU
  expr: cpu_usage > 80
  for: 1m

# Better (acknowledges spikes)
- alert: HighCPU
  expr: |
    avg_over_time(cpu_usage[10m]) > 80
  for: 5m
```

#### Use Moving Averages
```yaml
# Baseline-relative alerting
- alert: UnusualTraffic
  expr: |
    (rate(ifInOctets[5m]) /
     avg_over_time(rate(ifInOctets[5m])[7d])) > 2
  for: 10m
  # Alert if traffic is 2x normal for current time of day
```

#### Exclude Maintenance Windows
```yaml
- alert: MaintenanceAlert
  expr: |
    node_network_up == 0 and
    (now() < 1734892200 or now() > 1734895800)
    # Don't alert during maintenance window
```

### Alert Validation Checklist
```
For each alert:
  [ ] Metric is observable and reliable
  [ ] Threshold is based on baseline data
  [ ] Duration filters transient spikes
  [ ] Severity level is appropriate
  [ ] Runbook exists and is current
  [ ] False positive rate acceptable (<1/week)
  [ ] True positive rate high (>95%)
  [ ] Team trained to respond
```

## Notification Configuration

### Alertmanager Routing

#### Route by Severity
```yaml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK'

route:
  receiver: 'default'
  group_by: ['instance', 'alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h

  routes:
    # Critical alerts to PagerDuty
    - match:
        severity: critical
      receiver: 'pagerduty'
      repeat_interval: 1h

    # Warning alerts to Slack
    - match:
        severity: warning
      receiver: 'slack_warnings'
      repeat_interval: 4h

    # Info to email daily
    - match:
        severity: info
      receiver: 'email_digest'
      repeat_interval: 24h

receivers:
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_SERVICE_KEY'
        description: '{{ .GroupLabels.alertname }}'

  - name: 'slack_warnings'
    slack_configs:
      - channel: '#network-alerts'
        title: 'Warning: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'email_digest'
    email_configs:
      - to: 'team@example.com'
        from: 'alerts@example.com'
        smarthost: 'smtp.example.com:587'
        auth_username: 'alerts@example.com'
```

### Testing Notifications
```bash
# Send test alert to AlertManager
curl -X POST http://localhost:9093/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d '[
    {
      "labels": {
        "alertname": "TestAlert",
        "severity": "critical"
      },
      "annotations": {
        "summary": "Test alert",
        "description": "This is a test alert"
      }
    }
  ]'

# Verify in Slack/PagerDuty/Email
```

## Escalation Procedures

### Escalation Matrix
```
Alert Level          Initial Response    Escalation Time
─────────────────────────────────────────────────────────
Critical             On-call engineer     15 minutes
Warning              Team lead            1 hour
Info                 Team member          Next day

Escalation:
  L1: On-call engineer
  L2: Team lead
  L3: Engineering manager
  L4: Director/VP
```

### On-Call Procedures
```
Responsibilities:
  1. Acknowledge alert within 5 minutes
  2. Understand the problem
  3. Determine impact
  4. Initiate response
  5. Communicate status
  6. Work resolution
  7. Complete post-mortem

Tools:
  - Runbooks (step-by-step procedures)
  - Dashboard links (context)
  - Contact lists (escalation)
  - Change window calendar (avoid pushes during incidents)
```

## Alert Documentation

### Runbook Template
```
# Interface Down Alert

## Alert Name
InterfaceDown

## Severity
Critical

## Alert Condition
Interface is administratively up but operationally down for >2 minutes

## Common Causes
1. Unplugged cable
2. Device interface shutdown
3. Upstream device rebooted
4. Layer 1 failure

## Investigation Steps
1. ssh to device
2. show interfaces <interface_name>
3. Check physical port
4. Check if configured correctly
5. Check upstream device

## Resolution
1. If cable issue: reseat/replace cable
2. If config issue: apply correct config
3. If device issue: investigate device health

## Testing
After resolution:
1. Ping across interface
2. Verify BGP neighbors up
3. Check traffic flowing
4. Verify no errors/discards

## Escalation
If unable to resolve in 15 minutes → escalate to L2
```

## Implementation Checklist

- [ ] Define alert strategy and severity levels
- [ ] Identify key metrics to monitor
- [ ] Establish performance baselines
- [ ] Create alert rules (start conservative)
- [ ] Configure notification channels
- [ ] Set up Alertmanager routing
- [ ] Create runbooks for each alert type
- [ ] Test alert notifications
- [ ] Train team on response procedures
- [ ] Establish escalation procedures
- [ ] Monitor alert false positive rate
- [ ] Quarterly review and tuning
- [ ] Document alert catalog

---

**Guide Type**: Operations & Procedures
**Tools**: Prometheus/Alertmanager, PagerDuty, Slack
**Typical Alerts**: 20-50 per environment
**Timeline**: 2-3 weeks
**Last Updated**: 2025-11-19
