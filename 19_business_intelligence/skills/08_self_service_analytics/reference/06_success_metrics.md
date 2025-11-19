# Success Metrics Reference

## Overview

Measuring the success of self-service analytics initiatives is crucial for demonstrating value and guiding continuous improvement. This reference provides comprehensive metrics based on industry best practices.

## Metric Categories

### 1. Adoption Metrics

#### User Engagement
```yaml
Active Users:
  Definition: Unique users accessing analytics tools
  Measurement:
    - Daily Active Users (DAU)
    - Weekly Active Users (WAU)
    - Monthly Active Users (MAU)
  Targets:
    - Year 1: 30% of employees
    - Year 2: 50% of employees
    - Year 3: 70% of employees
  Calculation:
    SELECT
      COUNT(DISTINCT user_id) as active_users,
      COUNT(DISTINCT user_id) * 100.0 / total_employees as adoption_rate
    FROM analytics_usage_logs
    WHERE event_date >= CURRENT_DATE - 30

Stickiness Ratio:
  Definition: DAU / MAU ratio
  Measurement: (DAU / MAU) * 100
  Target: > 40%
  Significance: Indicates habitual usage
```

#### Usage Depth
```yaml
Query Volume:
  Metrics:
    - Total queries per day/week/month
    - Queries per active user
    - Growth rate month-over-month
  Target: 15-20% MoM growth in first year

Dashboard Views:
  Metrics:
    - Total dashboard views
    - Unique dashboards viewed
    - Views per user
    - Time spent on dashboards
  Target: 50+ dashboard views per user per month

Feature Adoption:
  Track usage of:
    - Data catalog searches
    - SQL query editor
    - Dashboard creation
    - Report scheduling
    - Data exports
  Target: 70% of users using 3+ features
```

#### User Distribution
```yaml
By Role:
  - Executive: ____%
  - Manager: ____%
  - Analyst: ____%
  - Individual Contributor: ____%
  Target: Broad distribution across roles

By Department:
  - Product: ____%
  - Sales: ____%
  - Marketing: ____%
  - Finance: ____%
  - Operations: ____%
  Target: All departments represented

By Skill Level:
  - Beginner: ____%
  - Intermediate: ____%
  - Advanced: ____%
  Target: Growth in intermediate+ users
```

### 2. Efficiency Metrics

#### Time to Insight
```yaml
Definition: Time from question to answer

Measurement Approaches:
  Self-Reported:
    Survey: "How long to answer your last data question?"
    Responses: <1 hour, 1-4 hours, 1 day, 2-3 days, >1 week

  Instrumented:
    Track: First query to dashboard creation
    Calculate: Median time to complete analysis

Benchmarks:
  Before Self-Service: 3-5 days
  Year 1 Target: 1-2 days
  Year 2 Target: <1 day
  Mature State: Hours, not days

Impact:
  - Faster decisions
  - Increased agility
  - More iterations
  - Better outcomes
```

#### Self-Service Rate
```yaml
Definition: % of data questions answered without analyst help

Calculation:
  self_service_rate = (
    questions_answered_by_users /
    total_data_questions
  ) * 100

Tracking:
  Before:
    - Count analyst request tickets
    - Survey: How often do you ask for help?

  After:
    - Monitor ticket volume change
    - Track direct tool usage
    - Compare against baseline

Targets:
  - Year 1: 40% self-service
  - Year 2: 60% self-service
  - Year 3: 75% self-service

Business Impact:
  - Analyst capacity freed
  - Faster answers
  - Reduced bottlenecks
  - Empowered users
```

#### Analyst Productivity
```yaml
Metrics:
  Request Backlog:
    - Number of pending requests
    - Age of oldest request
    - Target: <5 pending, <3 days old

  Request Resolution Time:
    - Time to complete analyst requests
    - Target: 50% reduction year-over-year

  Type of Work:
    - % time on ad-hoc requests (decrease)
    - % time on strategic projects (increase)
    - Target: 70% strategic, 30% ad-hoc

  Analyst-to-Employee Ratio:
    - Before: 1:50
    - After: 1:100+
    - Enabled by self-service
```

### 3. Quality Metrics

#### Data Quality Scores
```yaml
Completeness:
  Metric: % of required fields populated
  Target: >95%
  Measurement:
    SELECT
      table_name,
      column_name,
      (COUNT(*) - COUNT(column_name)) * 100.0 / COUNT(*) as null_pct
    FROM data_quality_checks
    GROUP BY 1, 2

Accuracy:
  Metric: % of records passing validation
  Target: >98%
  Tests:
    - Range checks
    - Format validation
    - Referential integrity

Freshness:
  Metric: Data age vs. SLA
  Target: >99% within SLA
  Measurement:
    - Expected: Update every 1 hour
    - Actual: Last updated timestamp
    - Alert if > 1.5 hours

Consistency:
  Metric: % of cross-system matches
  Target: >99%
  Example:
    - Salesforce revenue vs. warehouse
    - Marketing platform vs. analytics
```

#### Query Success Rate
```yaml
Definition: % of queries that execute successfully

Measurement:
  success_rate = (
    successful_queries /
    total_query_attempts
  ) * 100

Targets:
  - Overall: >95%
  - Beginner users: >90%
  - Advanced users: >98%

Common Failure Causes:
  - Syntax errors (improve training)
  - Permissions (improve access mgmt)
  - Timeouts (optimize performance)
  - Resource limits (increase quotas)

Improvement Actions:
  - Better error messages
  - Query validation
  - Auto-suggest
  - Example queries
```

#### Metric Consistency
```yaml
Definition: Same metric calculated the same way everywhere

Measurement:
  - Audit metrics across dashboards
  - Identify discrepancies
  - Track adoption of certified metrics

Metric Coverage:
  certified_metric_usage = (
    queries_using_certified_metrics /
    total_metric_queries
  ) * 100

Target: >80% of metrics from certified layer

Benefits:
  - Single source of truth
  - Reduced confusion
  - Increased trust
  - Fewer data disputes
```

### 4. User Satisfaction

#### Net Promoter Score (NPS)
```yaml
Question: "How likely are you to recommend our analytics platform to a colleague?"

Scale: 0-10
  - Promoters (9-10): Enthusiastic users
  - Passives (7-8): Satisfied but unenthusiastic
  - Detractors (0-6): Unhappy users

Calculation:
  NPS = % Promoters - % Detractors

Benchmarks:
  - Excellent: >50
  - Good: 30-50
  - Acceptable: 0-30
  - Needs Work: <0

Frequency: Quarterly survey

Follow-Up:
  - Ask for elaboration
  - Identify pain points
  - Close the loop
  - Track improvements
```

#### User Satisfaction Score
```yaml
Questions (1-5 scale):
  1. The analytics tools are easy to use
  2. I can find the data I need quickly
  3. The data is accurate and trustworthy
  4. I feel empowered to answer my own questions
  5. Training and support are adequate

Calculation:
  Average score across all questions

Target: >4.0 / 5.0

Segmentation:
  - By role
  - By experience level
  - By department
  - By tenure

Action Threshold:
  - Scores <3.0 require immediate attention
  - Track trends over time
  - Address systemic issues
```

#### Support Satisfaction
```yaml
Metrics:
  Response Time:
    - Target: <2 hours for first response
    - Measurement: Ticket system data

  Resolution Time:
    - Target: 80% resolved within 24 hours
    - Measurement: Ticket closed timestamp

  First Contact Resolution:
    - Target: >60%
    - Measurement: Single interaction resolution

  Support Rating:
    - Question: "How satisfied were you with support?"
    - Scale: 1-5
    - Target: >4.2
```

### 5. Business Impact

#### Cost Savings
```yaml
Analyst Time Saved:
  Calculation:
    requests_automated = 100 per month
    avg_time_per_request = 2 hours
    analyst_hourly_rate = $75
    monthly_savings = 100 * 2 * $75 = $15,000
    annual_savings = $180,000

Tool Consolidation:
  Before: 5 different tools at $50k each = $250k
  After: 1 unified platform at $100k = $100k
  Savings: $150k annually

Faster Decision Making:
  - Reduced time to market
  - Faster experimentation
  - More data-driven bets
  - Hard to quantify but significant

Resource Optimization:
  - Fewer analysts needed
  - Analysts focus on high-value work
  - Reduced external consulting
  - Lower training costs
```

#### Revenue Impact
```yaml
Attribution:
  - Faster product iterations
  - Better targeted marketing
  - Improved customer retention
  - Data-driven upsells

Measurement Challenges:
  - Hard to isolate analytics impact
  - Many confounding factors
  - Long attribution windows

Approaches:
  - A/B test data access
  - Survey decision makers
  - Track key decisions influenced
  - Measure velocity improvements

Example Impact:
  - 10% faster time to market
  - 5% improvement in conversion
  - 2% reduction in churn
  - Significant revenue impact
```

#### Decision Quality
```yaml
Metrics:
  Data-Driven Decisions:
    - % of decisions backed by data
    - Target: >80%
    - Survey: "Was data used in this decision?"

  Decision Confidence:
    - Scale: How confident in decision?
    - Target: Higher confidence with data
    - Comparison: With vs. without data

  Decision Outcomes:
    - Track decision success
    - Compare data-driven vs. gut-driven
    - Long-term measurement

  Experimentation Velocity:
    - Number of A/B tests run
    - Time to experiment results
    - % of changes tested first
```

### 6. Governance & Compliance

#### Data Access Compliance
```yaml
Metrics:
  Access Violations:
    - Number of unauthorized access attempts
    - Target: 0
    - Alert on any occurrence

  Access Review Completion:
    - % of quarterly access reviews completed
    - Target: 100%
    - Track: Reviewer completion rate

  Policy Acknowledgment:
    - % of users acknowledging policies
    - Target: 100%
    - Frequency: Annual + new user

  Audit Completeness:
    - % of access logged
    - Target: 100%
    - Spot check: Random audits
```

#### Data Quality Compliance
```yaml
SLA Adherence:
  - % of datasets meeting SLA
  - Target: >95%
  - Measure: Automated monitoring

Certification Coverage:
  - % of datasets with certification
  - Target: 80% of frequently used datasets
  - Measure: Catalog metadata

Test Coverage:
  - % of datasets with quality tests
  - Target: 100% of critical datasets
  - Measure: dbt/GE coverage reports

Issue Resolution:
  - Time to resolve quality issues
  - Target: Critical <4 hours, High <24 hours
  - Measure: Ticket system
```

## Measurement Dashboard

### Executive Dashboard
```yaml
Title: Self-Service Analytics Performance

KPIs (Monthly):
  Adoption:
    - Active Users: 523 (↑12%)
    - Adoption Rate: 62% (↑5%)
    - Queries/User: 18 (↑3%)

  Efficiency:
    - Time to Insight: 0.8 days (↓40%)
    - Self-Service Rate: 68% (↑15%)
    - Analyst Backlog: 3 requests (↓80%)

  Quality:
    - Data Quality Score: 94/100 (↑2%)
    - Query Success Rate: 97% (→)
    - Metric Consistency: 85% (↑10%)

  Satisfaction:
    - User NPS: +42 (↑8)
    - Satisfaction Score: 4.2/5 (↑0.3)
    - Support Rating: 4.5/5 (→)

  Business Impact:
    - Cost Savings: $180k/year
    - Decisions Data-Driven: 78%
    - Experiments Run: 45 this month

Charts:
  - Adoption trend (12 months)
  - User distribution by department
  - Top datasets accessed
  - Quality score trends
  - Support ticket volume
```

### Operational Dashboard
```yaml
Title: Self-Service Analytics Operations

Real-Time Metrics:
  - Current active users
  - Queries in progress
  - System performance
  - Error rates

Daily Metrics:
  - New users onboarded
  - Training completed
  - Support tickets opened/closed
  - Quality issues detected

Weekly Metrics:
  - Feature adoption
  - Dashboard creation
  - Data catalog searches
  - Certification requests

Alerts:
  - SLA violations
  - Quality issues
  - Security incidents
  - Performance degradation
```

## Reporting Cadence

### Weekly Reports
```yaml
Audience: Data team
Content:
  - User activity highlights
  - System performance
  - Issues and resolutions
  - Upcoming training sessions

Format: Email summary + dashboard link
```

### Monthly Reports
```yaml
Audience: Leadership
Content:
  - Adoption progress
  - Key achievements
  - Business impact
  - User feedback themes
  - Next month priorities

Format: Presentation + detailed report
```

### Quarterly Business Reviews
```yaml
Audience: Executive team
Content:
  - Strategic progress
  - ROI analysis
  - User testimonials
  - Roadmap updates
  - Investment requests

Format: Executive presentation
```

## Benchmarking

### Internal Benchmarks
```yaml
Compare:
  - Department vs. department
  - Team vs. team
  - Cohort vs. cohort
  - Time period vs. time period

Purpose:
  - Identify leaders
  - Share best practices
  - Address laggards
  - Celebrate wins
```

### External Benchmarks
```yaml
Industry Averages:
  Self-Service Adoption: 40-60%
  Time to Insight: 1-3 days
  Data Quality: 90-95%
  User Satisfaction: 3.8-4.2/5

Sources:
  - Gartner surveys
  - Forrester research
  - Industry conferences
  - Peer networks
```

## References

- "Measuring Analytics Success" by Wayne Eckerson
- Gartner: Analytics & BI Metrics That Matter
- Locally Optimistic: KPIs for Data Teams
- Amplitude Product Analytics Playbook
- Mode Analytics State of Data Report
