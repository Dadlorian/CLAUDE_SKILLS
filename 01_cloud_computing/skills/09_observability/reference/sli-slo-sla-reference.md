# SLI, SLO, and SLA Reference

## Overview

Service Level Indicators (SLIs), Service Level Objectives (SLOs), and Service Level Agreements (SLAs) form the foundation of reliability engineering and customer-centric monitoring.

## Service Level Indicators (SLIs)

### Definition
**SLI**: A carefully defined quantitative measure of some aspect of the level of service provided.

### Characteristics
- **Measurable**: Can be objectively measured
- **Meaningful**: Reflects user experience
- **Simple**: Easy to understand and calculate
- **Controllable**: Team can improve the metric

### Common SLIs

#### Availability
```
Definition: Proportion of time service is available

Calculation:
  Availability = Successful requests / Total requests
  Availability = Uptime / (Uptime + Downtime)

Example:
  99.9% availability = 43.8 minutes downtime per month
  99.99% availability = 4.38 minutes downtime per month

Measurement:
  - HTTP status codes (2xx, 3xx = success)
  - Health check responses
  - Synthetic monitoring
```

#### Latency
```
Definition: Time to process a request

Metrics:
  - Median (p50): 50% of requests
  - p95: 95% of requests
  - p99: 99% of requests
  - p99.9: 99.9% of requests

Example:
  "95% of requests complete in < 200ms"

Measurement:
  - Request duration from client perspective
  - End-to-end transaction time
  - Per-endpoint latency
```

#### Error Rate
```
Definition: Proportion of requests that fail

Calculation:
  Error Rate = Failed requests / Total requests

Example:
  "99.9% of requests succeed" = 0.1% error rate

Measurement:
  - HTTP 5xx status codes
  - Application exceptions
  - Timeout errors
```

#### Throughput
```
Definition: Number of requests processed per unit time

Metrics:
  - Requests per second (RPS)
  - Queries per second (QPS)
  - Transactions per minute (TPM)

Example:
  "System handles 10,000 RPS"

Measurement:
  - Request counter
  - Transaction logs
  - Application metrics
```

#### Durability
```
Definition: Data retention and integrity

Metrics:
  - Data loss rate
  - Successful backups
  - Restore success rate

Example:
  "99.999999999% (11 nines) durability"

Measurement:
  - Backup verification
  - Data checksums
  - Corruption detection
```

### SLI Specification Template

```yaml
SLI: API Request Success Rate

Definition:
  The proportion of valid HTTP requests that return a success response

Measurement:
  numerator: count(http_requests{status=~"2..|3.."})
  denominator: count(http_requests)

Implementation:
  source: Prometheus
  query: |
    sum(rate(http_requests_total{status=~"2..|3.."}[5m]))
    /
    sum(rate(http_requests_total[5m]))

Valid Events:
  - HTTP requests from authenticated clients
  - Excludes: health checks, metrics endpoints

Valid Success:
  - HTTP status 200-399
  - Response within timeout (30s)

Measurement Window:
  - Rolling 30 days
  - Calculated every 5 minutes
```

## Service Level Objectives (SLOs)

### Definition
**SLO**: Target value or range for an SLI measured over a specific time window.

### Components
```yaml
SLO Components:
  - SLI: What we're measuring
  - Target: Desired percentage (e.g., 99.9%)
  - Time Window: Measurement period (e.g., 30 days)
  - Error Budget: Allowed failures (100% - SLO)
```

### SLO Examples

#### Availability SLO
```yaml
SLO: API Availability
Target: 99.9%
Time Window: 30 days rolling
Error Budget: 0.1% = 43.8 minutes/month

Calculation:
  - Total minutes in 30 days: 43,200
  - Allowed downtime: 43.2 minutes
  - Required uptime: 43,156.8 minutes
```

#### Latency SLO
```yaml
SLO: API Response Time
Target: 95% of requests < 200ms
Time Window: 7 days rolling
Error Budget: 5% can be slower

Calculation:
  - Total requests in 7 days: 10,000,000
  - Allowed slow requests: 500,000
  - Required fast requests: 9,500,000
```

#### Error Rate SLO
```yaml
SLO: Request Success Rate
Target: 99.95%
Time Window: 30 days rolling
Error Budget: 0.05% = 5 errors per 10,000 requests

Calculation:
  - Total requests in 30 days: 100,000,000
  - Allowed errors: 50,000
  - Required successes: 99,950,000
```

### Multi-Window, Multi-Burn-Rate Alerts

#### Burn Rate Concept
```
Burn Rate = Error consumption rate / Error budget allocation rate

Examples:
  - 1x burn rate: Consuming error budget at normal rate
  - 2x burn rate: Will exhaust budget in half the time
  - 10x burn rate: Critical, will exhaust quickly

Alert when burn rate exceeds threshold
```

#### Alert Specification
```yaml
# Fast burn alert (1 hour)
- alert: HighErrorBudgetBurn_1h
  expr: |
    (
      sum(rate(http_requests_total{status=~"5.."}[1h]))
      /
      sum(rate(http_requests_total[1h]))
    ) > (14.4 * 0.001)  # 14.4x burn rate of 99.9% SLO
  for: 2m
  severity: page

# Slow burn alert (6 hours)
- alert: ModerateErrorBudgetBurn_6h
  expr: |
    (
      sum(rate(http_requests_total{status=~"5.."}[6h]))
      /
      sum(rate(http_requests_total[6h]))
    ) > (6 * 0.001)  # 6x burn rate
  for: 15m
  severity: ticket
```

#### Standard Burn Rate Windows
```yaml
For 30-day SLO:

Fast Burn (Page immediately):
  - Window: 1 hour
  - Burn rate multiplier: 14.4x
  - Fires after: 2 minutes
  - Exhausts budget in: 2 days

Moderate Burn (Create ticket):
  - Window: 6 hours
  - Burn rate multiplier: 6x
  - Fires after: 15 minutes
  - Exhausts budget in: 5 days

Slow Burn (Warning):
  - Window: 24 hours
  - Burn rate multiplier: 3x
  - Fires after: 1 hour
  - Exhausts budget in: 10 days
```

## Error Budget

### Concept
```
Error Budget = 100% - SLO

Purpose:
  - Balance reliability and velocity
  - Make informed risk decisions
  - Prioritize work objectively

Examples:
  - 99.9% SLO → 0.1% error budget (43.8 min/month)
  - 99.95% SLO → 0.05% error budget (21.6 min/month)
  - 99.99% SLO → 0.01% error budget (4.32 min/month)
```

### Error Budget Policy

```yaml
Error Budget Policy:

When Error Budget > 0:
  - Continue feature development
  - Accept calculated risks
  - Ship new features
  - Experiment and innovate

When Error Budget = 0:
  - Freeze feature launches
  - Focus on reliability
  - Fix bugs and technical debt
  - Improve automation
  - No risky changes

When Error Budget < 0:
  - Emergency: Stop all changes
  - All hands on reliability
  - Root cause analysis
  - Postmortems for all incidents
  - Management escalation
```

### Error Budget Calculation

```python
# Error budget calculation
def calculate_error_budget(slo_target, window_days=30):
    """
    Calculate error budget for SLO.

    Args:
        slo_target: SLO percentage (e.g., 99.9)
        window_days: Time window in days

    Returns:
        Error budget details
    """
    error_budget_pct = 100 - slo_target
    minutes_in_window = window_days * 24 * 60
    allowed_downtime = minutes_in_window * (error_budget_pct / 100)

    return {
        'error_budget_percent': error_budget_pct,
        'window_days': window_days,
        'total_minutes': minutes_in_window,
        'allowed_downtime_minutes': allowed_downtime,
        'allowed_downtime_hours': allowed_downtime / 60
    }

# Example
budget = calculate_error_budget(99.9, 30)
# {
#   'error_budget_percent': 0.1,
#   'window_days': 30,
#   'total_minutes': 43200,
#   'allowed_downtime_minutes': 43.2,
#   'allowed_downtime_hours': 0.72
# }
```

### Error Budget Tracking

```promql
# Current error budget consumption
(
  1 - (
    sum(rate(http_requests_total{status=~"2..|3.."}[30d]))
    /
    sum(rate(http_requests_total[30d]))
  )
) / (1 - 0.999) * 100

# Percentage consumed
# 0% = No errors (full budget)
# 100% = Budget exhausted
# >100% = Over budget (SLO violated)
```

## Service Level Agreements (SLAs)

### Definition
**SLA**: Explicit or implicit contract with users that includes consequences of meeting (or missing) the SLOs.

### SLA vs SLO
```
SLO (Internal):
  - Team goal
  - More strict than SLA
  - Early warning system
  - No financial impact
  - Example: 99.95%

SLA (External):
  - Customer commitment
  - Legal/financial consequences
  - Safety buffer from SLO
  - Public commitment
  - Example: 99.9%

Buffer:
  SLO should be stricter than SLA
  Example: 99.95% SLO, 99.9% SLA
  Gives team warning before SLA breach
```

### SLA Components

```yaml
SLA Components:

1. Service Description:
   - What is covered
   - What is NOT covered

2. Performance Metrics:
   - Availability: 99.9% uptime
   - Latency: p95 < 200ms
   - Support response: < 1 hour

3. Measurement Method:
   - How metrics are calculated
   - Measurement tools
   - Exclusions (planned maintenance)

4. Responsibilities:
   - Provider obligations
   - Customer obligations

5. Remedies/Penalties:
   - Service credits
   - Refunds
   - Compensation

6. Exclusions:
   - Force majeure
   - Customer-caused issues
   - Third-party services
```

### SLA Example

```yaml
Example SLA: Payment API Service

Coverage Period: Monthly (calendar month)

Uptime Commitment:
  - 99.95%: No credit
  - 99.5% - 99.95%: 10% service credit
  - 99% - 99.5%: 25% service credit
  - <99%: 50% service credit

Latency Commitment:
  - p95 < 200ms: No credit
  - p95 200-500ms: 5% service credit
  - p95 > 500ms: 10% service credit

Exclusions:
  - Scheduled maintenance (< 4 hours/month)
  - Customer configuration errors
  - Third-party payment processor issues
  - DDoS attacks
  - Force majeure events

Measurement:
  - Synthetic monitoring from 3 regions
  - 1-minute interval checks
  - HTTP 200-399 = success
  - Timeout = 30 seconds

Service Credits:
  - Requested within 30 days
  - Applied to next month invoice
  - Maximum 50% of monthly fee
```

### SLA Tiers

```yaml
Tier Structure:

Free Tier:
  - SLA: None (best effort)
  - Support: Community
  - Availability: ~99%

Basic Tier:
  - SLA: 99.9%
  - Support: Email, 48h response
  - Service Credit: Up to 25%

Professional Tier:
  - SLA: 99.95%
  - Support: Email/Chat, 4h response
  - Service Credit: Up to 50%

Enterprise Tier:
  - SLA: 99.99%
  - Support: 24/7 phone, 1h response
  - Service Credit: Up to 100%
  - Dedicated account manager
```

## SLO Implementation

### Step 1: Choose SLIs

```yaml
Process:
1. Identify user journeys
2. Define what "good" means
3. Select measurable indicators
4. Ensure indicators are actionable

Example User Journey: "Make a payment"
  - SLI 1: Payment request succeeds (availability)
  - SLI 2: Payment completes in < 3s (latency)
  - SLI 3: Correct amount charged (correctness)
```

### Step 2: Set SLO Targets

```yaml
Process:
1. Measure current performance
2. Understand user expectations
3. Consider cost of reliability
4. Set achievable targets
5. Plan for gradual improvement

Example:
  - Current: 99.5% availability
  - User expectation: 99.9%
  - Initial SLO: 99.7% (achievable)
  - 6-month goal: 99.9%
  - 12-month goal: 99.95%
```

### Step 3: Implement Monitoring

```yaml
Implementation:
1. Instrument application (metrics)
2. Set up data collection (Prometheus)
3. Create SLO dashboards (Grafana)
4. Configure alerts (multi-burn-rate)
5. Document runbooks
```

### Step 4: Create Alerts

```yaml
Alert Strategy:
- Fast burn: Page on-call (high severity)
- Moderate burn: Create ticket (medium severity)
- Slow burn: Warning (low severity)
- Error budget: Status update (informational)

Alert Content:
  - Current burn rate
  - Time to budget exhaustion
  - Runbook link
  - Recent changes
  - Affected services
```

### Step 5: Review and Iterate

```yaml
Review Cycle:
- Weekly: Error budget status
- Monthly: SLO achievement review
- Quarterly: SLO target adjustment
- Yearly: SLI/SLO redesign

Questions:
- Are SLOs too strict or too loose?
- Do alerts provide enough warning?
- Are users happy with reliability?
- What's the cost of current SLO?
- Should we adjust targets?
```

## SLO Dashboard Examples

### Availability Dashboard
```
Panels:
1. Current SLO Achievement (99.95%)
2. Error Budget Remaining (67%)
3. Availability Trend (30 days)
4. Error Budget Burn Rate (1.2x)
5. Time to Budget Exhaustion (67 days)
6. Recent Incidents (timeline)
7. Top Error Sources (by endpoint)
```

### Latency Dashboard
```
Panels:
1. Current p95 Latency (180ms)
2. SLO Target (200ms)
3. Latency Compliance (98.5%)
4. Latency Distribution (histogram)
5. Slowest Endpoints (table)
6. Latency by Region (map)
```

## Best Practices

### SLI Selection
1. **User-centric**: Measure what users experience
2. **Simple**: Easy to understand and calculate
3. **Few metrics**: 3-5 SLIs per service
4. **Actionable**: Team can improve the metric
5. **Measurable**: Reliable data source

### SLO Setting
1. **Achievable**: Based on current capability
2. **Meaningful**: Reflects user expectations
3. **Documented**: Clear definition and calculation
4. **Reviewed**: Regular reassessment
5. **Gradual**: Improve over time

### Error Budget Management
1. **Transparent**: Share budget status with team
2. **Policy-driven**: Clear rules for budget use
3. **Balanced**: Don't over-optimize reliability
4. **Flexible**: Adjust based on business needs
5. **Actionable**: Use budget to guide decisions

### SLA Crafting
1. **Buffer**: SLA < SLO (safety margin)
2. **Measurable**: Clear measurement method
3. **Fair**: Reasonable for both parties
4. **Excludable**: Define exclusions clearly
5. **Remedied**: Specify consequences

## Common Pitfalls

### Anti-Patterns
1. **Too many SLIs**: Tracking everything
2. **Unrealistic SLOs**: 99.999% for non-critical service
3. **No error budget policy**: Unclear what to do when budget exhausted
4. **Vanity metrics**: Measuring what's easy, not what matters
5. **No buy-in**: Team doesn't trust or use SLOs
6. **Set and forget**: Never review or adjust
7. **SLO = SLA**: No safety buffer
8. **All or nothing**: Binary pass/fail instead of budget-based

### Solutions
1. **Start small**: 1-2 critical SLIs
2. **Measure first**: Know current performance
3. **Get buy-in**: Involve entire team
4. **Document**: Clear definitions and processes
5. **Review regularly**: Adjust based on data
6. **Automate**: Use tools for calculation and alerting
7. **Communicate**: Share status widely

## Tools and Resources

### SLO Platforms
- **Google Cloud SLO Monitoring**
- **Datadog SLO Tracking**
- **New Relic SLO Management**
- **Nobl9**: SLO platform
- **Sloth**: SLO generator for Prometheus

### Open Source Tools
- **Pyrra**: SLO monitoring for Prometheus
- **slo-generator**: Python SLO framework
- **Sloth**: SLO as code generator

### Books and Resources
- "Site Reliability Engineering" by Google
- "The Site Reliability Workbook" by Google
- "Implementing Service Level Objectives" by Alex Hidalgo
