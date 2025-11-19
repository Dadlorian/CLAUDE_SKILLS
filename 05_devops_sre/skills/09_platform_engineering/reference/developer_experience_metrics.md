# Developer Experience Metrics Reference

## Overview

Developer Experience (DevEx) metrics help measure the effectiveness of your platform engineering efforts. These metrics focus on productivity, satisfaction, and the overall experience of developers using your platform.

## Key Frameworks

### DORA Metrics

The four key DORA (DevOps Research and Assessment) metrics:

#### 1. Deployment Frequency

How often code is deployed to production.

```yaml
Metric: Deployment Frequency
Target: On-demand (multiple deploys per day)
Elite: Multiple deploys per day
High: Once per day to once per week
Medium: Once per week to once per month
Low: Less than once per month

Measurement:
  query: |
    SELECT
      COUNT(*) as deployments,
      COUNT(*) / COUNT(DISTINCT DATE(deployed_at)) as deploys_per_day
    FROM deployments
    WHERE
      environment = 'production'
      AND deployed_at > NOW() - INTERVAL '30 days'
```

#### 2. Lead Time for Changes

Time from code commit to production deployment.

```yaml
Metric: Lead Time for Changes
Target: Less than one hour
Elite: Less than one hour
High: One day to one week
Medium: One week to one month
Low: More than one month

Measurement:
  query: |
    SELECT
      AVG(EXTRACT(EPOCH FROM (deployed_at - committed_at)) / 3600) as avg_lead_time_hours,
      PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY deployed_at - committed_at) as p50_lead_time,
      PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY deployed_at - committed_at) as p95_lead_time
    FROM deployments
    WHERE
      environment = 'production'
      AND deployed_at > NOW() - INTERVAL '30 days'
```

#### 3. Change Failure Rate

Percentage of deployments causing failures in production.

```yaml
Metric: Change Failure Rate
Target: 0-15%
Elite: 0-15%
High: 16-30%
Medium: 31-45%
Low: More than 45%

Measurement:
  query: |
    SELECT
      COUNT(*) FILTER (WHERE failed = true) * 100.0 / COUNT(*) as failure_rate,
      COUNT(*) FILTER (WHERE failed = true) as failed_deployments,
      COUNT(*) as total_deployments
    FROM deployments
    WHERE
      environment = 'production'
      AND deployed_at > NOW() - INTERVAL '30 days'
```

#### 4. Time to Restore Service

Time to recover from production incidents.

```yaml
Metric: Mean Time to Restore (MTTR)
Target: Less than one hour
Elite: Less than one hour
High: Less than one day
Medium: One day to one week
Low: More than one week

Measurement:
  query: |
    SELECT
      AVG(EXTRACT(EPOCH FROM (resolved_at - detected_at)) / 3600) as avg_mttr_hours,
      PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY resolved_at - detected_at) as p50_mttr,
      PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY resolved_at - detected_at) as p95_mttr
    FROM incidents
    WHERE
      severity IN ('critical', 'high')
      AND resolved_at > NOW() - INTERVAL '30 days'
```

### SPACE Framework

A comprehensive framework for developer productivity:

#### 1. Satisfaction and Wellbeing

Developer happiness and health.

```yaml
Metrics:
  - Developer Satisfaction Score (DSS)
  - Platform NPS (Net Promoter Score)
  - Cognitive Load Rating
  - Work-Life Balance Score
  - Burnout Index

Survey Questions:
  satisfaction:
    - "How satisfied are you with your development tools?" (1-5)
    - "How satisfied are you with deployment processes?" (1-5)
    - "How satisfied are you with documentation quality?" (1-5)

  cognitive_load:
    - "How easy is it to understand our systems?" (1-5)
    - "How often do you feel overwhelmed by complexity?" (1-5)

  nps:
    - "How likely are you to recommend our platform to other developers?" (0-10)

Calculation:
  DSS = Average of all satisfaction scores
  NPS = (% Promoters - % Detractors)
    Promoters: Score 9-10
    Passives: Score 7-8
    Detractors: Score 0-6
```

#### 2. Performance

The outcomes of development work.

```yaml
Metrics:
  - Lines of Code Changed
  - Pull Requests Merged
  - Code Review Time
  - Build Success Rate
  - Test Coverage
  - Bug Escape Rate

Measurement:
  pr_velocity:
    query: |
      SELECT
        COUNT(*) as prs_merged,
        AVG(EXTRACT(EPOCH FROM (merged_at - created_at)) / 3600) as avg_pr_time_hours
      FROM pull_requests
      WHERE
        state = 'merged'
        AND merged_at > NOW() - INTERVAL '30 days'

  build_success_rate:
    query: |
      SELECT
        COUNT(*) FILTER (WHERE status = 'success') * 100.0 / COUNT(*) as success_rate
      FROM ci_builds
      WHERE created_at > NOW() - INTERVAL '30 days'
```

#### 3. Activity

Volume of work and contributions.

```yaml
Metrics:
  - Commits per Day
  - Active Development Days
  - Code Churn
  - Review Activity
  - Documentation Updates

Measurement:
  developer_activity:
    query: |
      SELECT
        developer_id,
        COUNT(DISTINCT DATE(committed_at)) as active_days,
        COUNT(*) as total_commits,
        SUM(lines_added + lines_removed) as total_lines_changed
      FROM commits
      WHERE committed_at > NOW() - INTERVAL '30 days'
      GROUP BY developer_id

  code_churn:
    query: |
      SELECT
        SUM(lines_deleted) * 100.0 / NULLIF(SUM(lines_added), 0) as churn_rate
      FROM commits
      WHERE
        committed_at > NOW() - INTERVAL '30 days'
        AND committed_at > created_at + INTERVAL '1 day'
```

#### 4. Communication and Collaboration

How developers work together.

```yaml
Metrics:
  - Code Review Participation
  - Review Response Time
  - Pull Request Comments
  - Documentation Contributions
  - Knowledge Sharing Sessions

Measurement:
  collaboration:
    query: |
      SELECT
        COUNT(DISTINCT reviewer_id) as unique_reviewers,
        AVG(comment_count) as avg_comments_per_pr,
        AVG(EXTRACT(EPOCH FROM (first_review - created_at)) / 3600) as avg_response_time_hours
      FROM pull_requests
      WHERE created_at > NOW() - INTERVAL '30 days'
```

#### 5. Efficiency and Flow

Ability to complete work with minimal interruptions.

```yaml
Metrics:
  - Time in Zone (uninterrupted coding time)
  - Context Switches
  - Wait Time for Reviews
  - CI/CD Pipeline Duration
  - Environment Setup Time

Measurement:
  flow_metrics:
    query: |
      SELECT
        AVG(coding_session_duration) as avg_flow_time_minutes,
        AVG(interruptions_per_day) as avg_interruptions,
        AVG(context_switches_per_day) as avg_context_switches
      FROM developer_activity
      WHERE date > NOW() - INTERVAL '30 days'

  wait_times:
    query: |
      SELECT
        AVG(EXTRACT(EPOCH FROM (first_review - created_at)) / 3600) as pr_wait_time_hours,
        AVG(EXTRACT(EPOCH FROM (build_complete - build_start)) / 60) as build_time_minutes
      FROM pull_requests
      WHERE created_at > NOW() - INTERVAL '30 days'
```

## Platform-Specific Metrics

### Self-Service Adoption

Measure how developers use self-service capabilities.

```yaml
Metrics:
  - Platform API Usage
  - Template Usage
  - CLI Command Usage
  - Portal Page Views
  - Documentation Access

Measurement:
  api_usage:
    query: |
      SELECT
        endpoint,
        COUNT(*) as request_count,
        COUNT(DISTINCT user_id) as unique_users,
        AVG(response_time_ms) as avg_response_time
      FROM api_requests
      WHERE timestamp > NOW() - INTERVAL '30 days'
      GROUP BY endpoint
      ORDER BY request_count DESC

  template_adoption:
    query: |
      SELECT
        template_name,
        COUNT(*) as uses,
        COUNT(*) FILTER (WHERE success = true) as successful_uses,
        COUNT(*) FILTER (WHERE success = true) * 100.0 / COUNT(*) as success_rate
      FROM template_executions
      WHERE executed_at > NOW() - INTERVAL '30 days'
      GROUP BY template_name
```

### Time to Value

How quickly developers can be productive.

```yaml
Metrics:
  - Time to First Deploy
  - Environment Setup Time
  - Onboarding Time
  - First Contribution Time

Measurement:
  time_to_value:
    query: |
      SELECT
        AVG(EXTRACT(EPOCH FROM (first_deploy - account_created)) / 86400) as days_to_first_deploy,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY first_deploy - account_created) as p50_time_to_deploy
      FROM developers
      WHERE first_deploy IS NOT NULL
      AND account_created > NOW() - INTERVAL '90 days'

  onboarding_time:
    query: |
      SELECT
        AVG(EXTRACT(EPOCH FROM (onboarding_complete - start_date)) / 86400) as avg_onboarding_days
      FROM onboarding_sessions
      WHERE start_date > NOW() - INTERVAL '90 days'
```

### Toil Reduction

Measure reduction in manual, repetitive work.

```yaml
Metrics:
  - Automated vs Manual Operations
  - Manual Ticket Volume
  - Time Spent on Toil
  - Automation Coverage

Measurement:
  toil_metrics:
    query: |
      SELECT
        SUM(CASE WHEN automated = true THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as automation_rate,
        SUM(CASE WHEN automated = false THEN time_spent_minutes ELSE 0 END) as manual_minutes,
        AVG(CASE WHEN automated = false THEN time_spent_minutes ELSE 0 END) as avg_manual_time
      FROM operations
      WHERE performed_at > NOW() - INTERVAL '30 days'

  ticket_reduction:
    query: |
      SELECT
        DATE_TRUNC('week', created_at) as week,
        COUNT(*) as ticket_count,
        AVG(resolution_time_hours) as avg_resolution_time
      FROM support_tickets
      WHERE
        category = 'manual_operation'
        AND created_at > NOW() - INTERVAL '90 days'
      GROUP BY week
      ORDER BY week
```

### Platform Reliability

Platform uptime and availability metrics.

```yaml
Metrics:
  - Platform Uptime (SLA)
  - API Success Rate
  - Build System Availability
  - Documentation Availability
  - Portal Uptime

Measurement:
  platform_reliability:
    query: |
      SELECT
        COUNT(*) FILTER (WHERE status = 'up') * 100.0 / COUNT(*) as uptime_percentage,
        SUM(EXTRACT(EPOCH FROM downtime_duration)) / 3600 as total_downtime_hours
      FROM platform_health_checks
      WHERE checked_at > NOW() - INTERVAL '30 days'

  api_reliability:
    query: |
      SELECT
        endpoint,
        COUNT(*) FILTER (WHERE status_code < 500) * 100.0 / COUNT(*) as success_rate,
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time_ms) as p99_latency
      FROM api_requests
      WHERE timestamp > NOW() - INTERVAL '30 days'
      GROUP BY endpoint
```

## Developer Survey Metrics

### Regular Pulse Surveys

Monthly or quarterly surveys to gauge developer sentiment.

```yaml
Survey Template:
  frequency: monthly
  questions:
    satisfaction:
      - question: "How satisfied are you with our platform?"
        type: scale
        scale: 1-5
        labels:
          1: "Very Dissatisfied"
          5: "Very Satisfied"

      - question: "How easy is it to deploy a new service?"
        type: scale
        scale: 1-5
        labels:
          1: "Very Difficult"
          5: "Very Easy"

    productivity:
      - question: "How would you rate your productivity this month?"
        type: scale
        scale: 1-5

      - question: "What blocks your productivity the most?"
        type: multiple_choice
        options:
          - "Waiting for reviews"
          - "Slow CI/CD pipelines"
          - "Complex deployment process"
          - "Poor documentation"
          - "Flaky tests"
          - "Other"

    improvements:
      - question: "What one thing would most improve your experience?"
        type: text

      - question: "What's working well?"
        type: text

Analysis:
  satisfaction_score:
    calculation: Average of all satisfaction ratings
    target: "> 4.0"

  productivity_blockers:
    calculation: Top 3 most selected options
    action: Create improvement initiatives for top blockers
```

### Annual Deep Dive Surveys

Comprehensive annual surveys for strategic insights.

```yaml
Survey Template:
  frequency: annual
  sections:
    tools_and_platform:
      - "Rate the quality of our developer tools"
      - "Which tools cause the most friction?"
      - "What tools are missing from our platform?"

    processes:
      - "How effective is our code review process?"
      - "How well does our release process work?"
      - "Are our standards and guidelines clear?"

    documentation:
      - "How helpful is our documentation?"
      - "What documentation is missing or unclear?"
      - "How easy is it to find what you need?"

    collaboration:
      - "How well do teams collaborate?"
      - "How effective is knowledge sharing?"
      - "Do you feel supported by platform team?"

    career_and_growth:
      - "Are you learning new skills?"
      - "Do you have opportunities to grow?"
      - "Are you satisfied with your career trajectory?"
```

## Operational Metrics

### Platform Usage

Track overall platform adoption and usage.

```yaml
Metrics:
  - Active Users (Daily/Weekly/Monthly)
  - Services Managed
  - Deployments per Day
  - API Requests per Day
  - Support Tickets per Week

Dashboard:
  queries:
    active_users:
      daily: |
        SELECT COUNT(DISTINCT user_id)
        FROM platform_events
        WHERE timestamp > NOW() - INTERVAL '24 hours'

      weekly: |
        SELECT COUNT(DISTINCT user_id)
        FROM platform_events
        WHERE timestamp > NOW() - INTERVAL '7 days'

    platform_adoption:
      query: |
        SELECT
          DATE_TRUNC('week', created_at) as week,
          COUNT(*) as new_services,
          SUM(COUNT(*)) OVER (ORDER BY DATE_TRUNC('week', created_at)) as cumulative_services
        FROM services
        GROUP BY week
        ORDER BY week
```

### Support and Toil

Measure platform team workload.

```yaml
Metrics:
  - Support Ticket Volume
  - Ticket Resolution Time
  - Escalation Rate
  - Manual Operations Count
  - Interrupt Rate

Measurement:
  support_metrics:
    query: |
      SELECT
        COUNT(*) as total_tickets,
        AVG(EXTRACT(EPOCH FROM (resolved_at - created_at)) / 3600) as avg_resolution_hours,
        COUNT(*) FILTER (WHERE escalated = true) * 100.0 / COUNT(*) as escalation_rate,
        COUNT(*) FILTER (WHERE category = 'manual_operation') as manual_ops
      FROM support_tickets
      WHERE created_at > NOW() - INTERVAL '30 days'

  interrupt_tracking:
    query: |
      SELECT
        DATE_TRUNC('day', occurred_at) as day,
        COUNT(*) as interrupts,
        SUM(time_spent_minutes) as total_interrupt_time
      FROM platform_team_interrupts
      WHERE occurred_at > NOW() - INTERVAL '30 days'
      GROUP BY day
```

### Cost Efficiency

Track platform operational costs.

```yaml
Metrics:
  - Cost per Developer
  - Cost per Service
  - Infrastructure Cost Trends
  - License Costs
  - Platform Team FTE

Measurement:
  cost_metrics:
    query: |
      SELECT
        SUM(cost) / COUNT(DISTINCT developer_id) as cost_per_developer,
        SUM(cost) / COUNT(DISTINCT service_id) as cost_per_service,
        SUM(cost) as total_monthly_cost
      FROM (
        SELECT * FROM infrastructure_costs
        UNION ALL
        SELECT * FROM license_costs
        UNION ALL
        SELECT * FROM platform_team_costs
      ) costs
      WHERE month = DATE_TRUNC('month', NOW() - INTERVAL '1 month')
```

## Dashboards and Reporting

### Executive Dashboard

High-level metrics for leadership.

```yaml
Dashboard: Executive View
Refresh: Daily
Metrics:
  - Developer Satisfaction Score (trend)
  - DORA Metrics (all four, with targets)
  - Platform Adoption Rate
  - Cost per Developer
  - Key Initiative Progress

Layout:
  row1:
    - title: "Developer Satisfaction"
      type: score_card
      metric: developer_satisfaction_score
      target: 4.0
      trend: 7_days

    - title: "Platform NPS"
      type: score_card
      metric: net_promoter_score
      trend: 30_days

  row2:
    - title: "Deployment Frequency"
      type: time_series
      metric: deployments_per_day
      period: 90_days

    - title: "Lead Time for Changes"
      type: histogram
      metric: lead_time_hours
      percentiles: [50, 95, 99]

  row3:
    - title: "Platform Adoption"
      type: line_chart
      metrics:
        - active_users_weekly
        - services_managed
      period: 180_days
```

### Team Dashboard

Detailed metrics for platform team.

```yaml
Dashboard: Platform Team View
Refresh: Real-time
Sections:
  platform_health:
    - API Success Rate (99.9% SLO)
    - API Latency (p50, p95, p99)
    - Build System Queue Depth
    - Portal Uptime

  developer_experience:
    - Recent Satisfaction Scores
    - Top Pain Points (from surveys)
    - Support Ticket Trends
    - Documentation Access Patterns

  self_service:
    - Template Usage This Week
    - API Call Volume
    - CLI Active Users
    - Successful vs Failed Operations

  toil_and_support:
    - Open Tickets by Priority
    - Manual Operations Today
    - Interrupts This Week
    - On-call Metrics
```

### Developer Dashboard

Self-service metrics for development teams.

```yaml
Dashboard: Developer View
Refresh: Hourly
Personalization: Team and user level
Sections:
  my_services:
    - Service Health Status
    - Recent Deployments
    - Active Incidents
    - Upcoming Maintenance

  my_productivity:
    - PRs Merged This Week
    - Average PR Time
    - Build Success Rate
    - Test Coverage Trend

  my_team:
    - Team Velocity
    - Deployment Frequency
    - Lead Time Trend
    - On-call Schedule
```

## Alerting and Actions

### Metric Thresholds

Set alerts for concerning trends.

```yaml
Alerts:
  developer_satisfaction:
    metric: developer_satisfaction_score
    threshold: "< 3.5"
    action: "Investigate and create improvement plan"
    notify: ["platform-lead", "engineering-vp"]

  deployment_frequency:
    metric: deployments_per_day
    threshold: "< 5"
    window: "7 days"
    action: "Review deployment friction"
    notify: ["platform-team"]

  change_failure_rate:
    metric: change_failure_rate
    threshold: "> 15%"
    window: "7 days"
    action: "Review recent deployments and testing"
    notify: ["platform-team", "sre-team"]

  time_to_restore:
    metric: mean_time_to_restore_hours
    threshold: "> 4"
    window: "30 days"
    action: "Review incident response process"
    notify: ["platform-lead", "sre-lead"]

  support_ticket_volume:
    metric: support_tickets_per_week
    threshold: "> 50"
    action: "Identify automation opportunities"
    notify: ["platform-team"]
```

## Continuous Improvement

### Metric Review Cadence

```yaml
Daily:
  - Platform uptime and availability
  - Critical incidents
  - Support ticket queue

Weekly:
  - DORA metrics trends
  - API usage patterns
  - Support ticket analysis
  - Team retrospective

Monthly:
  - Developer satisfaction survey results
  - Productivity metrics deep dive
  - Cost analysis
  - Platform adoption trends
  - OKR progress

Quarterly:
  - Comprehensive DevEx review
  - Strategic planning
  - Investment prioritization
  - Benchmarking against industry

Annual:
  - Full platform assessment
  - Developer survey analysis
  - Multi-year roadmap
  - Team skills and growth
```

### Action Framework

```yaml
Process:
  1. Measure:
     - Collect metrics consistently
     - Run regular surveys
     - Gather qualitative feedback

  2. Analyze:
     - Identify trends and patterns
     - Correlate different metrics
     - Find root causes

  3. Prioritize:
     - Impact vs effort analysis
     - Developer pain severity
     - Business alignment

  4. Act:
     - Launch improvement initiatives
     - Automate toil
     - Build new capabilities

  5. Validate:
     - Measure impact of changes
     - Collect feedback
     - Iterate
```

## Tools and Implementation

### Metrics Collection

```python
# Example metrics collection
from datadog import initialize, statsd
from prometheus_client import Counter, Histogram, Gauge

# Datadog
options = {
    'api_key': os.environ['DATADOG_API_KEY'],
    'app_key': os.environ['DATADOG_APP_KEY']
}
initialize(**options)

# Track deployment
statsd.increment('platform.deployments',
    tags=['environment:production', 'service:user-api'])

# Track API latency
statsd.histogram('platform.api.latency',
    response_time_ms,
    tags=['endpoint:/api/services', 'method:POST'])

# Prometheus
deployments = Counter('deployments_total',
    'Total deployments',
    ['environment', 'service'])

api_latency = Histogram('api_request_duration_seconds',
    'API request latency',
    ['endpoint', 'method'])

active_services = Gauge('active_services',
    'Number of active services')
```

### Survey Tools

- Officevibe
- Culture Amp
- Lattice
- Custom internal surveys
- Slack polls

### Analytics Platforms

- Datadog
- New Relic
- Grafana
- Tableau
- Looker
- Custom dashboards

## Resources

- DORA Metrics: https://dora.dev/
- SPACE Framework: https://queue.acm.org/detail.cfm?id=3454124
- Developer Productivity: https://martinfowler.com/articles/developer-effectiveness.html
- Platform Metrics: https://platformengineering.org/blog/measuring-success
