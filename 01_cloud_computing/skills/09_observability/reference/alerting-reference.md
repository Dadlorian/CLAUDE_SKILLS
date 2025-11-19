# Alerting Reference

## Overview

Effective alerting is critical for maintaining system reliability. Good alerts are actionable, timely, and provide sufficient context for rapid response.

## Alert Principles

### Philosophy
```yaml
Good Alerts Are:
  - Actionable: Recipient can and should take action
  - Timely: Detected early enough to prevent impact
  - Contextual: Provide enough information to respond
  - Rare: Only for significant issues
  - Routed: To the right person/team

Bad Alerts Are:
  - Noisy: Frequent false positives
  - Vague: Unclear what's wrong or what to do
  - Late: Problem already impacted users
  - Ignored: Too frequent, team stops responding
  - Over-broadcast: Everyone gets everything
```

### Alert vs Ticket vs Log
```
ALERT (Page/Notification):
  - Requires immediate action
  - User-impacting or about to be
  - Can't wait until next business day
  Example: Service down, error budget exhausted

TICKET (Create Issue):
  - Requires action soon (hours/days)
  - Not immediately user-impacting
  - Can be handled during business hours
  Example: Disk 80% full, slow queries

LOG/DASHBOARD (Record Only):
  - Informational
  - No action required
  - Reference for investigation
  Example: Request completed, cache hit
```

## Alert Severity Levels

### P0/Critical/Page
```yaml
Definition: Service is down or severely degraded

Characteristics:
  - Immediate user impact
  - Revenue loss
  - SLA breach imminent
  - Requires immediate response

Response:
  - Page on-call engineer immediately
  - War room if not resolved quickly
  - Executive notification

Examples:
  - API returning 100% errors
  - Database is down
  - Payment processing failed
  - Website unreachable

Response Time: < 5 minutes
```

### P1/High/Urgent
```yaml
Definition: Significant degradation, partial outage

Characteristics:
  - Some users affected
  - Feature unavailable
  - Performance severely degraded
  - Will become P0 if not addressed

Response:
  - Page on-call during business hours
  - Escalate if after hours
  - Create incident

Examples:
  - 20% error rate
  - High latency (p95 > 5s)
  - One region down
  - Database read replicas failing

Response Time: < 15 minutes
```

### P2/Medium/Warning
```yaml
Definition: Abnormal behavior, not yet user-impacting

Characteristics:
  - No current user impact
  - Could escalate
  - Needs investigation
  - Error budget burning

Response:
  - Create ticket
  - Investigate during business hours
  - Monitor closely

Examples:
  - Disk 80% full
  - Memory usage high
  - Error rate above baseline
  - Slow database queries

Response Time: < 4 hours
```

### P3/Low/Info
```yaml
Definition: Informational, no action required

Characteristics:
  - FYI only
  - Good to know
  - Historical data
  - Trend information

Response:
  - No immediate action
  - Review periodically
  - Context for investigations

Examples:
  - Deployment completed
  - Cache cleared
  - Configuration changed
  - Capacity report

Response Time: Next business day
```

## Alert Anatomy

### Required Fields
```yaml
Alert Components:

1. Summary:
   "High error rate on payment API"

2. Severity:
   P1 / Critical

3. Service/Component:
   payment-api / checkout-service

4. Metric/Condition:
   error_rate > 5% for 5 minutes

5. Current Value:
   12.5% error rate

6. Threshold:
   > 5%

7. Runbook Link:
   https://wiki.company.com/runbooks/payment-api-errors

8. Dashboard Link:
   https://grafana.company.com/d/payment-api

9. Timestamps:
   - First detected: 2024-01-15 10:30:00
   - Last updated: 2024-01-15 10:35:00

10. Context:
   - Recent deployments
   - Related alerts
   - Affected regions
```

### Alert Template
```yaml
# Prometheus Alert Example
alert: HighErrorRate
expr: |
  (
    sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
    /
    sum(rate(http_requests_total[5m])) by (service)
  ) > 0.05
for: 5m
labels:
  severity: critical
  service: "{{ $labels.service }}"
  team: backend
annotations:
  summary: "High error rate on {{ $labels.service }}"
  description: |
    {{ $labels.service }} has {{ $value | humanizePercentage }} error rate.
    Threshold: 5%
    Current: {{ $value | humanizePercentage }}

  runbook: https://wiki.company.com/runbooks/high-error-rate
  dashboard: https://grafana.company.com/d/{{ $labels.service }}
  playbook: |
    1. Check recent deployments
    2. Review error logs
    3. Check dependency services
    4. Rollback if caused by deployment
```

## Alert Types

### Threshold-Based Alerts
```promql
# Static threshold
cpu_usage_percent > 80

# Error rate above threshold
error_rate > 0.01

# Latency above threshold
http_request_duration_seconds{quantile="0.95"} > 1.0

# Disk usage
disk_used_percent > 90
```

### Rate of Change Alerts
```promql
# Sudden spike in errors
rate(errors_total[5m]) >
  (avg_over_time(rate(errors_total[5m])[1h]) * 2)

# Traffic drop (50% decrease)
rate(requests_total[5m]) <
  (avg_over_time(rate(requests_total[5m])[1h]) * 0.5)
```

### Anomaly Detection Alerts
```promql
# Deviation from baseline
abs(
  rate(requests_total[5m]) -
  avg_over_time(rate(requests_total[5m])[1h:5m] offset 1w)
) > 1000

# Standard deviation based
abs(
  metric - avg_over_time(metric[1h])
) > (3 * stddev_over_time(metric[1h]))
```

### Ratio Alerts
```promql
# Error ratio
sum(rate(errors_total[5m])) /
sum(rate(requests_total[5m])) > 0.01

# Success ratio
sum(rate(successful_jobs[5m])) /
sum(rate(total_jobs[5m])) < 0.99

# Cache hit ratio
sum(rate(cache_hits[5m])) /
sum(rate(cache_requests[5m])) < 0.80
```

### Composite Alerts
```promql
# High error rate AND high latency
(error_rate > 0.05) AND (p95_latency > 1.0)

# High CPU OR high memory
(cpu_usage > 80) OR (memory_usage > 90)

# Service down for multiple consecutive checks
up == 0 for 2m
```

### Absence Alerts
```promql
# Metric stopped being reported
absent(up{job="api-server"})

# No requests in last 5 minutes
absent(rate(requests_total[5m])) or
rate(requests_total[5m]) == 0
```

### Burn Rate Alerts (SLO-based)
```promql
# Fast burn (14.4x over 1 hour)
(
  1 - (
    sum(rate(http_requests_total{status=~"2..|3.."}[1h]))
    /
    sum(rate(http_requests_total[1h]))
  )
) > (14.4 * (1 - 0.999))

# Slow burn (3x over 24 hours)
(
  1 - (
    sum(rate(http_requests_total{status=~"2..|3.."}[24h]))
    /
    sum(rate(http_requests_total[24h]))
  )
) > (3 * (1 - 0.999))
```

## Alert Routing

### Routing Rules
```yaml
# AlertManager routing config
route:
  receiver: default
  group_by: ['alertname', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h

  routes:
    # Critical alerts - page immediately
    - match:
        severity: critical
      receiver: pagerduty-critical
      group_wait: 0s
      repeat_interval: 5m

    # High severity - page during business hours
    - match:
        severity: high
      receiver: pagerduty-high
      group_wait: 5m
      repeat_interval: 1h

    # Medium severity - create ticket
    - match:
        severity: medium
      receiver: jira-tickets
      group_wait: 30m
      repeat_interval: 24h

    # Team-specific routing
    - match:
        team: backend
      receiver: backend-oncall

    - match:
        team: frontend
      receiver: frontend-oncall

    # Service-specific escalation
    - match:
        service: payment-api
      receiver: payment-team
      continue: true  # Also notify default
```

### Receiver Configuration
```yaml
receivers:
  # PagerDuty for critical alerts
  - name: pagerduty-critical
    pagerduty_configs:
      - service_key: YOUR_PAGERDUTY_KEY
        severity: '{{ .GroupLabels.severity }}'
        description: '{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.summary }}'

  # Slack for medium alerts
  - name: slack-alerts
    slack_configs:
      - api_url: YOUR_WEBHOOK_URL
        channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ .CommonAnnotations.description }}'
        color: '{{ if eq .Status "firing" }}danger{{ else }}good{{ end }}'

  # Email for low priority
  - name: email-team
    email_configs:
      - to: 'team@company.com'
        from: 'alerts@company.com'
        subject: '[{{ .Status }}] {{ .GroupLabels.alertname }}'
        html: |
          <h2>{{ .GroupLabels.alertname }}</h2>
          <p>{{ .CommonAnnotations.description }}</p>

  # Webhook for ticket creation
  - name: jira-tickets
    webhook_configs:
      - url: 'https://jira.company.com/api/alert'
        send_resolved: true
```

## Alert Grouping

### Why Group Alerts
```yaml
Problem: 100 servers down → 100 alerts
Solution: Group by cluster → 1 alert

Problem: Same issue across regions → 5 alerts
Solution: Group by alertname → 1 alert

Problem: Multiple symptoms of one issue → 3 alerts
Solution: Group by root cause → 1 alert
```

### Grouping Strategies
```yaml
# By alert name
group_by: ['alertname']
Result: All "HighCPU" alerts grouped together

# By service
group_by: ['service']
Result: All alerts for "payment-api" grouped

# By severity
group_by: ['severity']
Result: All critical alerts grouped

# Multi-dimensional
group_by: ['alertname', 'cluster', 'service']
Result: "HighCPU on payment-api in us-east-1"
```

## Alert Silencing and Inhibition

### Silencing (Temporary Mute)
```yaml
# During maintenance window
silences:
  - matchers:
      - service="payment-api"
      - severity="critical"
    startsAt: "2024-01-15T10:00:00Z"
    endsAt: "2024-01-15T12:00:00Z"
    createdBy: "john@company.com"
    comment: "Scheduled maintenance"

# CLI
amtool silence add \
  service="payment-api" \
  --start="2024-01-15T10:00:00Z" \
  --end="2024-01-15T12:00:00Z" \
  --comment="Maintenance"
```

### Inhibition (Suppress Related Alerts)
```yaml
# Suppress dependent service alerts when main service down
inhibit_rules:
  - source_match:
      alertname: ServiceDown
      service: database
    target_match:
      service: api
    equal: ['cluster']

  # Don't alert on high latency if there are errors
  - source_match:
      alertname: HighErrorRate
    target_match:
      alertname: HighLatency
    equal: ['service']

  # Suppress warning if critical firing
  - source_match:
      severity: critical
    target_match:
      severity: warning
    equal: ['alertname', 'service']
```

## Alert Fatigue Prevention

### Causes of Alert Fatigue
```yaml
1. Too Many Alerts:
   - Everything generates alerts
   - No prioritization
   - Alert spam

2. False Positives:
   - Incorrect thresholds
   - Noisy metrics
   - Flapping alerts

3. Non-Actionable:
   - Nothing to do
   - Out of team's control
   - Unclear next steps

4. Poorly Timed:
   - Alerts during known maintenance
   - Ignored outside business hours
   - Repeat alerts too frequently
```

### Solutions
```yaml
1. Reduce Alert Volume:
   - Alert only on user-impacting issues
   - Use error budgets instead of thresholds
   - Create tickets for non-urgent issues
   - Aggregate similar alerts

2. Improve Signal Quality:
   - Tune thresholds based on historical data
   - Use multi-window alerts (prevent flapping)
   - Add "for" clause to avoid transient spikes
   - Regular alert review and cleanup

3. Make Alerts Actionable:
   - Include runbook links
   - Provide context and recent changes
   - Clear next steps
   - Auto-remediation where possible

4. Smart Routing:
   - Route by severity and time
   - Use escalation policies
   - Silence during maintenance
   - Inhibit redundant alerts
```

### Alert Review Process
```yaml
Weekly Review:
  1. Top 10 alerts by frequency
  2. Identify and fix noisy alerts
  3. Review false positives
  4. Check alert-to-incident ratio

Monthly Review:
  1. Alert effectiveness metrics
  2. Mean time to acknowledge (MTTA)
  3. Mean time to resolve (MTTR)
  4. Alert accuracy rate
  5. On-call load analysis

Metrics to Track:
  - Alerts per day/week
  - False positive rate
  - Alert-to-incident conversion rate
  - Time to acknowledge
  - Time to resolve
  - Repeat alerts
```

## On-Call Best Practices

### On-Call Rotation
```yaml
Rotation Schedule:
  - Primary: Week-long shifts
  - Secondary: Backup for primary
  - Shadow: Training rotation
  - Handoff: Monday morning sync

Schedule Types:
  - Follow-the-sun: 24/7 coverage across timezones
  - Business hours: 9am-5pm coverage
  - Full-time: 24/7 single timezone

Compensation:
  - On-call pay
  - Time in lieu
  - Extra vacation days
  - Rotation frequency limits
```

### On-Call Runbooks
```yaml
Runbook Template:

Title: High Error Rate on Payment API

Severity: P1 / Critical

Symptoms:
  - Error rate > 5%
  - User complaints
  - Payment failures

Possible Causes:
  1. Recent deployment
  2. Database issues
  3. Third-party API down
  4. Resource exhaustion

Investigation Steps:
  1. Check recent deployments (last 2 hours)
  2. Review error logs in Kibana
  3. Check database connectivity
  4. Verify third-party API status
  5. Check resource usage (CPU, memory)

Resolution Steps:
  1. If deployment related: Rollback
  2. If database issue: Failover to replica
  3. If third-party down: Enable circuit breaker
  4. If resource issue: Scale up

Escalation:
  - After 30 minutes: Escalate to senior engineer
  - After 1 hour: Escalate to management
  - Payment team: @payment-team
  - Infrastructure: @infra-team

Related Runbooks:
  - Database Failover Procedure
  - Deployment Rollback Guide
  - Circuit Breaker Configuration
```

## Alert Integration Examples

### PagerDuty
```yaml
# AlertManager configuration
receivers:
  - name: pagerduty
    pagerduty_configs:
      - service_key: <integration_key>
        severity: '{{ .GroupLabels.severity }}'
        description: |
          {{ .GroupLabels.alertname }}
          {{ .CommonAnnotations.summary }}
        details:
          firing: '{{ .Alerts.Firing | len }}'
          resolved: '{{ .Alerts.Resolved | len }}'
          dashboard: '{{ .CommonAnnotations.dashboard }}'
          runbook: '{{ .CommonAnnotations.runbook }}'
```

### Slack
```yaml
receivers:
  - name: slack
    slack_configs:
      - api_url: <webhook_url>
        channel: '#alerts'
        username: 'AlertBot'
        title: '{{ .GroupLabels.alertname }}'
        text: |
          *Severity:* {{ .GroupLabels.severity }}
          *Service:* {{ .GroupLabels.service }}
          *Summary:* {{ .CommonAnnotations.summary }}
          *Runbook:* {{ .CommonAnnotations.runbook }}
        color: '{{ if eq .Status "firing" }}danger{{ else }}good{{ end }}'
        send_resolved: true
        actions:
          - type: button
            text: 'View Dashboard'
            url: '{{ .CommonAnnotations.dashboard }}'
          - type: button
            text: 'View Runbook'
            url: '{{ .CommonAnnotations.runbook }}'
```

### Opsgenie
```yaml
receivers:
  - name: opsgenie
    opsgenie_configs:
      - api_key: <api_key>
        message: '{{ .GroupLabels.alertname }}'
        description: '{{ .CommonAnnotations.description }}'
        priority: '{{ .CommonLabels.severity }}'
        tags: 'service={{ .GroupLabels.service }}'
        details:
          Dashboard: '{{ .CommonAnnotations.dashboard }}'
          Runbook: '{{ .CommonAnnotations.runbook }}'
```

## Advanced Alert Patterns

### Predictive Alerts
```promql
# Predict disk will fill in 4 hours
predict_linear(disk_used_bytes[1h], 4*3600) > disk_total_bytes
```

### Correlation Alerts
```promql
# High latency correlates with high CPU
(
  (http_latency_p95 > 1.0)
  and
  (cpu_usage_percent > 80)
)
```

### Seasonality-Aware Alerts
```promql
# Compare to same time last week
abs(
  rate(requests_total[5m]) -
  rate(requests_total[5m] offset 1w)
) > 1000
```

## Alert Metrics

### Measuring Alert Effectiveness
```yaml
Key Metrics:

1. Alert Volume:
   - Alerts per day
   - Alerts per service
   - Alerts per severity

2. Alert Accuracy:
   - True positive rate
   - False positive rate
   - Alert-to-incident ratio

3. Response Metrics:
   - Mean time to acknowledge (MTTA)
   - Mean time to resolve (MTTR)
   - Time to escalate

4. On-Call Load:
   - Pages per shift
   - After-hours pages
   - Weekend pages
   - Sleep interruptions

Goals:
  - <5 pages per week per person
  - >90% true positive rate
  - <15 min MTTA
  - <1 hour MTTR (for critical)
```

## Tools and Platforms

### Alert Managers
- **Prometheus AlertManager**: Prometheus ecosystem
- **PagerDuty**: Incident management
- **Opsgenie**: Alert management and on-call
- **VictorOps**: Incident response

### Notification Channels
- **Slack**: Team communication
- **Email**: Traditional notification
- **SMS**: Critical alerts
- **Phone**: Voice calls for urgent issues
- **Microsoft Teams**: Enterprise communication
- **Webhook**: Custom integrations
