# SLO/SLI Reference Guide

## Table of Contents
1. [SLI, SLO, and SLA Fundamentals](#sli-slo-and-sla-fundamentals)
2. [Defining SLIs](#defining-slis)
3. [Setting SLOs](#setting-slos)
4. [Error Budgets](#error-budgets)
5. [Monitoring SLOs](#monitoring-slos)
6. [Multi-Window Multi-Burn-Rate Alerts](#multi-window-multi-burn-rate-alerts)
7. [Best Practices](#best-practices)

---

## SLI, SLO, and SLA Fundamentals

### Definitions

#### Service Level Indicator (SLI)
A carefully defined quantitative measure of some aspect of the level of service provided.

**Examples:**
- Request latency: Percentage of requests served within 100ms
- Availability: Percentage of successful requests
- Throughput: Requests per second successfully handled
- Durability: Percentage of records successfully retained

#### Service Level Objective (SLO)
A target value or range for a service level measured by an SLI.

**Examples:**
- 99.9% of requests should complete successfully
- 95% of requests should complete within 100ms
- 99.99% of stored records should be retained

#### Service Level Agreement (SLA)
An explicit or implicit contract with users that includes consequences of meeting (or missing) the SLOs.

**Example:**
- If availability falls below 99.9%, customers receive a 25% credit
- If availability falls below 99.0%, customers receive a 100% credit

### Relationship

```
┌─────────────────────────────────────────────────┐
│                     SLA                          │
│  "We promise 99.9% availability or you get     │
│   a service credit"                             │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │               SLO                         │ │
│  │  "We target 99.95% availability"          │ │
│  │                                           │ │
│  │  ┌─────────────────────────────────────┐ │ │
│  │  │           SLI                       │ │ │
│  │  │  "Percentage of successful HTTP    │ │ │
│  │  │   requests over total requests"    │ │ │
│  │  └─────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘

SLO > SLA (internal target is stricter than customer promise)
```

---

## Defining SLIs

### SLI Categories

#### Request-Driven SLIs
For services that respond to user requests.

**Availability**
```
SLI = (Successful requests) / (Total requests)
```

**Latency**
```
SLI = (Requests faster than threshold) / (Total requests)
```

**Quality**
```
SLI = (Requests with correct data) / (Total requests)
```

#### Data-Driven SLIs
For data processing pipelines.

**Freshness**
```
SLI = (Records processed within SLA time) / (Total records)
```

**Correctness**
```
SLI = (Correctly processed records) / (Total records)
```

**Coverage**
```
SLI = (Records processed) / (Records received)
```

#### Storage SLIs

**Durability**
```
SLI = (Records successfully stored) / (Records attempted to store)
```

**Throughput**
```
SLI = (Successful writes per second) / (Target writes per second)
```

### SLI Specification Template

```yaml
sli:
  name: api_availability
  description: Percentage of successful API requests

  sli_specification:
    # What makes a request valid?
    valid_events:
      - All HTTP requests to /api/* endpoints
      - Exclude health checks (/health, /readiness)
      - Exclude synthetic monitoring requests

    # What makes a request good?
    good_events:
      - HTTP status codes 200-299
      - HTTP status codes 400-499 (client errors are "good" from SLO perspective)
      - Exclude 429 (rate limiting) from good events

    # Measurement
    measurement_method: request_based
    measurement_window: 30_days

    # PromQL query
    promql:
      good_events: |
        sum(rate(http_requests_total{
          path=~"/api/.*",
          path!~"/(health|readiness)",
          status=~"[2-4].."}[5m]
        ))
      valid_events: |
        sum(rate(http_requests_total{
          path=~"/api/.*",
          path!~"/(health|readiness)"}[5m]
        ))
```

### SLI Examples

#### HTTP Availability
```promql
# Good events: successful requests
sum(rate(http_requests_total{status=~"[2-4].."}[5m]))

# Valid events: all requests
sum(rate(http_requests_total[5m]))

# SLI
sum(rate(http_requests_total{status=~"[2-4].."}[5m]))
/
sum(rate(http_requests_total[5m]))
```

#### HTTP Latency (P95 < 100ms)
```promql
# Good events: requests under 100ms
sum(rate(http_request_duration_seconds_bucket{le="0.1"}[5m]))

# Valid events: all requests
sum(rate(http_request_duration_seconds_count[5m]))

# SLI
sum(rate(http_request_duration_seconds_bucket{le="0.1"}[5m]))
/
sum(rate(http_request_duration_seconds_count[5m]))
```

#### Database Query Success Rate
```promql
# Good events: successful queries
sum(rate(db_queries_total{status="success"}[5m]))

# Valid events: all queries
sum(rate(db_queries_total[5m]))

# SLI
sum(rate(db_queries_total{status="success"}[5m]))
/
sum(rate(db_queries_total[5m]))
```

#### Message Processing Freshness
```promql
# Good events: messages processed within 5 minutes
sum(rate(messages_processed_total{processing_time_le="300"}[5m]))

# Valid events: all messages
sum(rate(messages_received_total[5m]))

# SLI
sum(rate(messages_processed_total{processing_time_le="300"}[5m]))
/
sum(rate(messages_received_total[5m]))
```

---

## Setting SLOs

### SLO Structure

```yaml
slo:
  name: api_availability_slo
  description: API should be available 99.9% of the time

  sli: api_availability  # Reference to SLI definition

  target: 0.999  # 99.9%

  window: 30d  # 30-day rolling window

  error_budget:
    total: 0.001  # 0.1% = 100% - 99.9%
    # For 30 days: 43,200 minutes
    # Error budget: 43.2 minutes of downtime per 30 days
```

### Setting Realistic SLOs

#### Step 1: Measure Current Performance
```promql
# Last 30 days availability
sum(increase(http_requests_total{status=~"[2-4].."}[30d]))
/
sum(increase(http_requests_total[30d]))

# Result: 0.9987 (99.87%)
```

#### Step 2: Analyze User Expectations
- What do users expect?
- What do competitors offer?
- What can we realistically achieve?

#### Step 3: Consider Cost vs. Reliability

| SLO | Downtime/30d | Cost | Complexity |
|-----|--------------|------|------------|
| 99% | 7.2 hours | Low | Low |
| 99.9% | 43 minutes | Medium | Medium |
| 99.95% | 22 minutes | High | High |
| 99.99% | 4.3 minutes | Very High | Very High |
| 99.999% | 26 seconds | Extremely High | Extremely High |

#### Step 4: Set Aspirational SLO
```
Current performance: 99.87%
User expectation: 99.9%
SLA commitment: 99.9%
Internal SLO: 99.95% (buffer above SLA)
```

### Multiple SLOs for Different Aspects

```yaml
service: api-server

slos:
  - name: availability
    target: 0.999
    window: 30d
    sli: |
      sum(rate(http_requests_total{status=~"[2-4].."}[5m]))
      /
      sum(rate(http_requests_total[5m]))

  - name: latency_p95
    target: 0.95
    window: 30d
    description: 95% of requests should complete within 100ms
    sli: |
      sum(rate(http_request_duration_seconds_bucket{le="0.1"}[5m]))
      /
      sum(rate(http_request_duration_seconds_count[5m]))

  - name: latency_p99
    target: 0.99
    window: 30d
    description: 99% of requests should complete within 500ms
    sli: |
      sum(rate(http_request_duration_seconds_bucket{le="0.5"}[5m]))
      /
      sum(rate(http_request_duration_seconds_count[5m]))
```

### Composite SLOs

Combine multiple SLIs into a single SLO.

```yaml
composite_slo:
  name: user_experience
  description: Overall user experience quality

  components:
    - sli: availability
      weight: 0.5
      target: 0.999

    - sli: latency_p95
      weight: 0.3
      target: 0.95

    - sli: error_rate
      weight: 0.2
      target: 0.99

  # Overall target: weighted average must be > 0.98
  target: 0.98
```

---

## Error Budgets

### Error Budget Calculation

```
Error Budget = 1 - SLO Target

For SLO of 99.9%:
Error Budget = 1 - 0.999 = 0.001 = 0.1%
```

### Error Budget in Time

```
30-day window:
Total time: 30 days × 24 hours × 60 minutes = 43,200 minutes
Error budget (0.1%): 43,200 × 0.001 = 43.2 minutes

7-day window:
Total time: 7 days × 24 hours × 60 minutes = 10,080 minutes
Error budget (0.1%): 10,080 × 0.001 = 10.08 minutes

1-day window:
Total time: 1 day × 24 hours × 60 minutes = 1,440 minutes
Error budget (0.1%): 1,440 × 0.001 = 1.44 minutes
```

### Error Budget in Requests

```
Assuming 1,000,000 requests per 30 days:
Error budget (0.1%): 1,000,000 × 0.001 = 1,000 failed requests

Assuming 1,000 requests per second:
Requests per 30 days: 1,000 × 60 × 60 × 24 × 30 = 2,592,000,000
Error budget (0.1%): 2,592,000,000 × 0.001 = 2,592,000 failed requests
```

### Error Budget Remaining

```promql
# Current SLI over 30 days
sum(increase(http_requests_total{status=~"[2-4].."}[30d]))
/
sum(increase(http_requests_total[30d]))

# If result is 0.9995 (99.95%):
# Error budget consumed: 0.999 - 0.9995 = -0.0005 (negative = under budget)
# Error budget remaining: 0.001 - 0.0005 = 0.0005 (50% remaining)

# If result is 0.9985 (99.85%):
# Error budget consumed: 0.999 - 0.9985 = 0.0005
# Error budget remaining: 0.001 - 0.0005 = 0.0005 (50% remaining)

# If result is 0.998 (99.8%):
# Error budget consumed: 0.999 - 0.998 = 0.001
# Error budget remaining: 0.001 - 0.001 = 0 (100% consumed!)
```

### Error Budget Policy

```yaml
error_budget_policy:
  name: Development Velocity Control

  states:
    - name: healthy
      condition: error_budget_remaining > 0.5  # > 50% remaining
      actions:
        - Allow risky deployments
        - Focus on feature development
        - Aggressive experimentation
        - Reduced testing requirements

    - name: warning
      condition: 0.2 < error_budget_remaining <= 0.5  # 20-50% remaining
      actions:
        - Increase deployment scrutiny
        - Balance features and reliability
        - Standard testing requirements
        - Monitor closely

    - name: critical
      condition: 0 < error_budget_remaining <= 0.2  # 0-20% remaining
      actions:
        - Freeze feature development
        - Focus on reliability improvements
        - Enhanced testing requirements
        - Root cause analysis for all incidents

    - name: exhausted
      condition: error_budget_remaining <= 0  # Exhausted
      actions:
        - Complete deployment freeze (except critical fixes)
        - Emergency response mode
        - Mandatory postmortems
        - Executive escalation
```

---

## Monitoring SLOs

### Recording Rules for SLOs

```yaml
groups:
  - name: slo_recording_rules
    interval: 30s
    rules:
      # Record good and total events
      - record: slo:http_requests:good_events:rate5m
        expr: |
          sum(rate(http_requests_total{status=~"[2-4].."}[5m]))

      - record: slo:http_requests:total_events:rate5m
        expr: |
          sum(rate(http_requests_total[5m]))

      # Calculate SLI
      - record: slo:http_requests:success_ratio:rate5m
        expr: |
          slo:http_requests:good_events:rate5m
          /
          slo:http_requests:total_events:rate5m

      # Calculate error ratio (inverse of SLI)
      - record: slo:http_requests:error_ratio:rate5m
        expr: |
          1 - slo:http_requests:success_ratio:rate5m

      # Error budget consumption rate
      - record: slo:http_requests:error_budget_consumption:rate1h
        expr: |
          (1 - slo:http_requests:success_ratio:rate5m) / (1 - 0.999)
```

### SLO Dashboards

#### Current SLI vs SLO Target
```promql
# Query for gauge panel
slo:http_requests:success_ratio:rate5m

# Add threshold lines at:
# - 0.999 (SLO target)
# - 0.9995 (50% error budget line)
```

#### Error Budget Remaining (30-day)
```promql
# Good events in 30 days
sum(increase(http_requests_total{status=~"[2-4].."}[30d]))

# Total events in 30 days
sum(increase(http_requests_total[30d]))

# Current SLI
sum(increase(http_requests_total{status=~"[2-4].."}[30d]))
/
sum(increase(http_requests_total[30d]))

# Error budget remaining (as percentage)
(
  0.001  # Total error budget (0.1%)
  -
  (
    1 - (
      sum(increase(http_requests_total{status=~"[2-4].."}[30d]))
      /
      sum(increase(http_requests_total[30d]))
    )
  )
)
/
0.001 * 100

# Result: Percentage of error budget remaining (0-100%)
```

#### Error Budget Burn Rate
```promql
# Current burn rate (how fast we're consuming error budget)
# Burn rate of 1.0 = consuming at exactly the sustainable rate
# Burn rate > 1.0 = consuming faster than sustainable
# Burn rate < 1.0 = consuming slower than sustainable

(1 - slo:http_requests:success_ratio:rate5m) / (1 - 0.999)

# Example results:
# 0.5 = consuming at 50% of sustainable rate (good)
# 1.0 = consuming at exactly sustainable rate (acceptable)
# 2.0 = consuming at 200% of sustainable rate (warning)
# 10.0 = consuming at 1000% of sustainable rate (critical)
```

#### SLI Trend (7-day)
```promql
# 7-day SLI with 1-hour resolution
sum(increase(http_requests_total{status=~"[2-4].."}[1h]))
/
sum(increase(http_requests_total[1h]))
```

---

## Multi-Window Multi-Burn-Rate Alerts

Google's recommended approach for SLO-based alerting.

### Concept

Alert when error budget is being consumed at an unsustainable rate, using multiple time windows to balance sensitivity and precision.

### Alert Categories

| Alert | Burn Rate | Time Window | Notification | Error Budget Consumed |
|-------|-----------|-------------|--------------|----------------------|
| Critical (Page) | 14.4x | 1h | Immediate page | 2% in 1 hour |
| High (Page) | 6x | 6h | Immediate page | 5% in 6 hours |
| Medium (Ticket) | 3x | 24h | Create ticket | 10% in 1 day |
| Low (Ticket) | 1x | 3d | Create ticket | 10% in 3 days |

### Implementation

#### Critical Alert (Fast Burn)
```yaml
- alert: SLOErrorBudgetFastBurn
  expr: |
    (
      (1 - slo:http_requests:success_ratio:rate5m) / (1 - 0.999) > 14.4
      and
      (1 - (
        sum(increase(http_requests_total{status=~"[2-4].."}[1h]))
        /
        sum(increase(http_requests_total[1h]))
      )) / (1 - 0.999) > 14.4
    )
    or
    (
      (1 - slo:http_requests:success_ratio:rate5m) / (1 - 0.999) > 6
      and
      (1 - (
        sum(increase(http_requests_total{status=~"[2-4].."}[6h]))
        /
        sum(increase(http_requests_total[6h]))
      )) / (1 - 0.999) > 6
    )
  for: 5m
  labels:
    severity: critical
    page: "true"
  annotations:
    summary: "Critical SLO error budget burn detected"
    description: "Error budget is being consumed at {{ $value }}x the sustainable rate"
```

#### Medium Alert (Slow Burn)
```yaml
- alert: SLOErrorBudgetSlowBurn
  expr: |
    (
      (1 - slo:http_requests:success_ratio:rate5m) / (1 - 0.999) > 3
      and
      (1 - (
        sum(increase(http_requests_total{status=~"[2-4].."}[24h]))
        /
        sum(increase(http_requests_total[24h]))
      )) / (1 - 0.999) > 3
    )
    or
    (
      (1 - slo:http_requests:success_ratio:rate5m) / (1 - 0.999) > 1
      and
      (1 - (
        sum(increase(http_requests_total{status=~"[2-4].."}[3d]))
        /
        sum(increase(http_requests_total[3d]))
      )) / (1 - 0.999) > 1
    )
  for: 30m
  labels:
    severity: warning
    page: "false"
  annotations:
    summary: "SLO error budget slow burn detected"
    description: "Error budget is being consumed at {{ $value }}x the sustainable rate"
```

### Calculating Burn Rates

```
For a 30-day SLO window with 99.9% target (0.1% error budget):

Fast burn (2% of budget in 1 hour):
- 1 hour is 1/720 of 30 days
- To consume 2% of budget in 1/720 of the time
- Burn rate = 0.02 / (1/720) = 14.4x

Medium burn (5% of budget in 6 hours):
- 6 hours is 1/120 of 30 days
- To consume 5% of budget in 1/120 of the time
- Burn rate = 0.05 / (1/120) = 6x

Slow burn (10% of budget in 1 day):
- 1 day is 1/30 of 30 days
- To consume 10% of budget in 1/30 of the time
- Burn rate = 0.10 / (1/30) = 3x
```

---

## Best Practices

### Defining SLIs

1. **User-centric metrics**
   - Measure what users actually experience
   - Focus on request success, not system health

2. **Simple and understandable**
   - Easy to explain to non-technical stakeholders
   - Clear definition of "good" vs "bad"

3. **Measurable and reliable**
   - Based on actual measurements, not assumptions
   - Instrumentation must be reliable

4. **Appropriate granularity**
   - Not too broad (e.g., "overall system health")
   - Not too narrow (e.g., "CPU usage on instance-3")

### Setting SLOs

1. **Start with current performance**
   - Measure baseline before setting targets
   - Don't set unrealistic targets

2. **Leave margin above SLA**
   ```
   SLA: 99.9%
   SLO: 99.95%
   Margin: 0.05% (buffer for unexpected issues)
   ```

3. **Consider multiple SLOs**
   - Availability, latency, quality
   - Different SLOs for different endpoints
   - Different SLOs for different user tiers

4. **Iterate and refine**
   - Review SLOs quarterly
   - Adjust based on user feedback and business needs

### Managing Error Budgets

1. **Use error budgets to inform decisions**
   - Healthy budget → More aggressive development
   - Low budget → Focus on reliability

2. **Track error budget consumption**
   - Daily, weekly, monthly views
   - Identify trends and patterns

3. **Define clear policies**
   - What actions to take at different budget levels
   - Who has authority to make decisions

4. **Communicate with stakeholders**
   - Regular SLO reviews with product and business teams
   - Transparent reporting of SLO performance

### Alerting on SLOs

1. **Use multi-window multi-burn-rate alerts**
   - Faster detection of critical issues
   - Fewer false positives

2. **Don't alert on SLO violations directly**
   ```
   # Bad: Alert when SLI drops below SLO
   alert: SLOViolation
   expr: slo:http_requests:success_ratio:rate5m < 0.999

   # Good: Alert on error budget burn rate
   alert: SLOErrorBudgetBurn
   expr: (1 - slo:http_requests:success_ratio:rate5m) / (1 - 0.999) > 14.4
   ```

3. **Separate pages from tickets**
   - Page for fast burns (immediate action required)
   - Ticket for slow burns (investigation needed)

4. **Include actionable information**
   - Current burn rate
   - Error budget remaining
   - Link to relevant dashboards and runbooks

### Documentation

1. **Document SLI definitions**
   - What is measured
   - How it's measured
   - Why this metric matters

2. **Document SLO rationale**
   - Why this target was chosen
   - User expectations and business requirements
   - Historical context

3. **Maintain runbooks**
   - What to do when SLO is at risk
   - Common causes and remediation steps
   - Escalation procedures

### Review and Iteration

1. **Regular SLO reviews**
   - Quarterly review of SLO targets
   - Annual comprehensive review

2. **Postmortem SLO impact**
   - Every incident should note SLO impact
   - Track error budget consumption per incident

3. **Adjust based on reality**
   - If SLO is consistently missed → Lower target or improve service
   - If SLO is always met with large margin → Raise target or invest in features

4. **User feedback integration**
   - Survey users about their experience
   - Compare SLO compliance with user satisfaction
   - Adjust SLOs to align with user expectations
