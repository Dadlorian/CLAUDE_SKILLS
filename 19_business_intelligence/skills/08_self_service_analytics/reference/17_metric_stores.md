# Metric Stores Architecture & Implementation

## Overview

A metric store (or metrics layer) is a centralized system that defines, computes, and serves business metrics consistently across an organization. This reference provides guidance on architecture, implementation, and best practices for building effective metric stores.

## Core Concepts

### What is a Metric Store?

```yaml
Metric Store Definition:
  - Centralized repository of metric definitions
  - Automatic metric computation engine
  - Consistent metric serving across tools
  - Single source of truth for KPIs

Benefits:
  - Eliminates metric duplication
  - Ensures consistency across teams
  - Reduces calculation errors
  - Enables rapid metric discovery
  - Simplifies maintenance

Traditional vs. Metric Store Approach:
  Traditional (Without Metric Store):
    - Dashboard 1: Custom SQL for revenue metric
    - Dashboard 2: Different SQL for revenue metric
    - Report 3: Yet another revenue calculation
    - Problem: All different, conflicting values

  With Metric Store:
    - Single definition of revenue metric
    - All dashboards use same calculation
    - Consistency, accuracy, maintainability
```

## Metric Store Architecture

### Layered Architecture

```
┌─────────────────────────────────────────┐
│        Data Consumption Layer           │
│  (BI Tools, ML Models, Apps, Reports)   │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│      Metric Serving Layer               │
│  (APIs, Query Engines, Caches)          │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│   Metric Definition & Computation       │
│  (Metric configs, Aggregation logic)    │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│      Data Transformation Layer          │
│  (dbt models, Data pipelines)           │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│      Data Source Layer                  │
│  (Data warehouse, lakes, databases)     │
└─────────────────────────────────────────┘
```

### Component Architecture

```yaml
Metric Definition Layer:
  - YAML/JSON configuration files
  - Metric specifications with formulas
  - Dimension definitions
  - Filter rules and business logic

  Example Structure:
    metric:
      name: monthly_revenue
      description: Revenue by month
      type: derived
      calculation: SUM(revenue)
      dimensions: [month, product, region]
      filters:
        - status != 'cancelled'
        - transaction_date >= '2025-01-01'

Computation Engine:
  - Query optimization
  - Metric aggregation
  - Cache management
  - Scheduling and refresh

  Responsibilities:
    - Parse metric definitions
    - Generate optimal queries
    - Execute computations
    - Manage refresh schedules

Serving Layer:
  - REST APIs for metric queries
  - GraphQL endpoints
  - Direct database access
  - Caching layer for performance

  Features:
    - Dynamic metric queries
    - Dimension filtering
    - Time-series queries
    - Comparison operations
```

## Metric Definition Models

### Simple Metrics (Table/Column Level)

```yaml
Type: Simple Count
metric:
  name: total_users
  description: Total count of active users
  type: table_metric
  table: dim_users
  column: user_id
  aggregation: COUNT
  filters:
    - status = 'active'
  dimensions:
    - signup_month
    - country
    - subscription_tier

Type: Derived Column
metric:
  name: user_ltv
  description: Lifetime value per user
  type: derived
  formula: SUM(total_spent) / COUNT(DISTINCT user_id)
  table: fact_transactions
  filters:
    - status = 'completed'
```

### Composite Metrics

```yaml
Type: Ratio/Percentage
metric:
  name: conversion_rate
  numerator: total_conversions
  denominator: total_visitors
  formula: (COUNT(DISTINCT CASE WHEN converted=1) / COUNT(DISTINCT visitor_id)) * 100
  dimensions:
    - date
    - traffic_source
    - product

Type: Cohort Metrics
metric:
  name: cohort_retention_week_2
  description: % of cohort retained in week 2
  type: cohort
  cohort_dimension: signup_week
  event: user_engagement
  timeframe: week 2
  calculation: COUNT(DISTINCT returning_users) / COUNT(DISTINCT cohort_users)
```

### Advanced Metrics

```yaml
Type: Time Series
metric:
  name: moving_average_revenue
  description: 30-day moving average of daily revenue
  base_metric: daily_revenue
  calculation: AVG(daily_revenue) OVER (ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW)
  dimensions:
    - product_line

Type: Comparison
metric:
  name: yoy_growth_rate
  description: Year-over-year revenue growth
  current_period: revenue
  comparison_period: revenue_previous_year
  formula: ((current - previous) / previous) * 100

Type: ML-Based
metric:
  name: predicted_churn_risk
  description: ML model predicted churn probability
  source: ml_model_endpoint
  refresh_frequency: daily
  features:
    - mrr
    - support_tickets
    - feature_usage
```

## Implementation Approaches

### Approach 1: dbt + Semantic Models

```yaml
Implementation Stack:
  - dbt: Data transformation
  - dbt Semantic Models: Metric definitions
  - dbt Explorer or MetricFlow: Metric serving

  Advantages:
    - Code-based definitions (version controlled)
    - Tight dbt integration
    - SQL generation automated
    - Active development by dbt Labs

  Example dbt YAML:
    models:
      - name: fct_transactions
        description: Fact table for transactions

        semantic_models:
          - name: revenue
            defaults:
              agg_time_dimension: transaction_date
            measures:
              - name: revenue_sum
                description: Total revenue
                agg: SUM
                expr: amount
            dimensions:
              - name: product_id
              - name: region
            entities:
              - name: customer
                type: foreign_key
                expr: customer_id

        metrics:
          - name: total_revenue
            type: simple
            expr: SUM(amount)
            timestamp: transaction_date
```

### Approach 2: Dedicated Metric Store Platform

```yaml
Commercial Platforms:
  - Looker (LookML Explores + measures)
  - Tableau (Custom SQL metrics)
  - Atlan (Metric as code)
  - Metric Flow (dbt native)
  - Transform (Metrics Platform)

Open Source Platforms:
  - Apache Superset: Metric definitions
  - Metabase: SQL-based metrics
  - Cube: Full semantic layer

Platform Features:
  - Web UI for metric configuration
  - API-based metric serving
  - Caching and optimization
  - Change tracking and versioning
  - Governance and access control
```

### Approach 3: Home-Grown Solution

```yaml
Architecture Components:
  - YAML/JSON configuration storage
  - Python-based metric computation engine
  - REST API server for metric serving
  - PostgreSQL for metric metadata

  Tech Stack Example:
    Configuration: YAML files in git
    Engine: Python with Airflow orchestration
    Storage: PostgreSQL for metadata
    API: FastAPI for serving
    Caching: Redis for hot metrics

  Development Effort:
    - Initial MVP: 4-8 weeks
    - Production ready: 3-4 months
    - Ongoing maintenance: 1 FTE
```

## Metric Definition Best Practices

### Clear Specifications

```yaml
Essential Metadata:
  Name:
    - Lowercase with underscores
    - Descriptive and unique
    - Example: customer_acquisition_cost

  Description:
    - Business context
    - Use cases
    - Limitations and caveats
    - Example: "Monthly marketing expense divided by new customers acquired"

  Owner:
    - Assigned steward
    - Contact for questions
    - Approval for changes

  Dimensions:
    - List all valid dimensions
    - Specify defaults
    - Document restrictions

Formula Documentation:
  - Plain English first
  - Then pseudocode
  - Then actual implementation
  - Example scenarios
```

### Governance Framework

```yaml
Metric Classification:
  Tier 1 - Core Metrics:
    - Mission-critical metrics
    - Executive KPIs
    - Regulated metrics
    - SLA: 99.9% accuracy
    - High review standards

  Tier 2 - Standard Metrics:
    - Common business metrics
    - Department KPIs
    - SLA: 99% accuracy
    - Standard review process

  Tier 3 - Ad-Hoc Metrics:
    - Experimental metrics
    - Analysis-specific
    - SLA: 95% accuracy
    - Minimal review

Change Management Process:
  1. Propose change with rationale
  2. Impact analysis (dependent dashboards/reports)
  3. Review by metric owner + data team
  4. Testing in development environment
  5. Staged rollout with monitoring
  6. Communication to stakeholders
```

## Metric Computation Strategy

### Computation Patterns

```yaml
Eager Computation (Pre-Aggregation):
  - Metrics computed on schedule
  - Results stored in cache/warehouse
  - Fast query response (<1 second)
  - Higher storage requirements
  - Use for: High-volume, frequently accessed metrics

  Schedule Examples:
    - Hourly: Real-time focused metrics
    - Daily: Standard business metrics
    - Weekly: Performance summary metrics

Lazy Computation (On-Demand):
  - Metrics computed when requested
  - Lower storage requirements
  - Higher query latency (1-30 seconds)
  - Better for: Low-frequency or ad-hoc metrics

  Use cases:
    - Custom segments
    - Deep exploratory analysis
    - Rarely accessed metrics

Hybrid Approach:
  - Core metrics: Pre-aggregated
  - Custom dimensions: On-demand
  - Blend of speed and flexibility
  - Recommended for most orgs
```

### Caching Strategy

```yaml
Cache Tiers:
  L1 - Memory Cache (Redis):
    - Hot metrics used constantly
    - Refresh: Every 30-60 minutes
    - Hit rate target: 80%+
    - Examples: Today's revenue, active users

  L2 - Database Cache (Materialized Views):
    - Standard metrics
    - Refresh: Every 4-6 hours
    - Maintain indexes for performance
    - Examples: Weekly KPIs

  L3 - Full Computation:
    - Rare or custom queries
    - On-demand execution
    - Query optimization essential
    - Timeout limits recommended

Cache Invalidation:
  Time-based: Refresh on schedule
  Event-based: Refresh on data updates
  Manual: Explicit cache clear
  Hybrid: Combine strategies
```

## Metric Serving APIs

### REST API Examples

```yaml
Get Metric Query:
  GET /api/metrics/revenue
  Query Parameters:
    - dimensions=date,product
    - filters=region:US,status:active
    - granularity=daily
    - time_range=2025-01-01:2025-11-19

  Response:
    {
      "metric": "revenue",
      "data": [
        {"date": "2025-01-01", "product": "A", "revenue": 50000},
        {"date": "2025-01-01", "product": "B", "revenue": 75000}
      ],
      "metadata": {"computed_at": "...", "last_refresh": "..."}
    }

Comparison Query:
  GET /api/metrics/compare
  Query Parameters:
    - metrics=revenue,cost
    - dimensions=month
    - comparison_type=yoy

  Response:
    {
      "current_period": {...},
      "comparison_period": {...},
      "growth_rate": 0.15,
      "confidence_interval": [0.12, 0.18]
    }
```

## Integration Patterns

### BI Tool Integration

```yaml
Looker Integration:
  - Use Explores for metric queries
  - Define measures in LookML
  - Leverage Native Queries
  - Example:
    view: metrics {
      measure: total_revenue {
        type: sum
        sql: ${fct_transactions.amount} ;;
        filters: [fct_transactions.status: "completed"]
      }
    }

Tableau Integration:
  - Published data sources with custom metrics
  - Tableau Custom SQL
  - Hyper data extracts
  - Query optimization important

Direct Query Integration:
  - Semantic layer generates SQL
  - Send to any SQL-compatible tool
  - Ensures consistency
```

## Monitoring & Maintenance

### Quality Assurance

```yaml
Automated Tests:
  - Query execution success
  - Result reasonableness checks
  - Freshness validation
  - Schema change detection

  Example Test:
    test metric_revenue_trend:
      expected: revenue today > 0.8 * revenue yesterday
      alert_threshold: failure or alert_level > warning

Manual Reviews:
  - Monthly metric spot checks
  - Peer review of new metrics
  - Stakeholder validation
  - Drift analysis (comparing to external sources)
```

### Performance Monitoring

```yaml
Key Metrics:
  - Query latency (p50, p95, p99)
  - Cache hit rates
  - Computation duration
  - API error rates
  - Data freshness age

  Targets:
    - p95 latency: <5 seconds
    - Cache hit rate: >70%
    - Freshness: <6 hours for core metrics
    - Error rate: <0.1%
```

## Migration Strategies

### From Ad-Hoc to Centralized

```yaml
Phase 1 - Assessment:
  - Audit existing metric definitions
  - Identify duplicates
  - Document inconsistencies
  - Timeline: 2-4 weeks

Phase 2 - Design:
  - Design metric store architecture
  - Select tooling
  - Create governance framework
  - Timeline: 4-6 weeks

Phase 3 - Pilot:
  - Implement 10-20 core metrics
  - Test on 1-2 departments
  - Gather feedback
  - Timeline: 4-8 weeks

Phase 4 - Rollout:
  - Migrate remaining metrics
  - Update dashboards and reports
  - Decommission old calculations
  - Train users
  - Timeline: 8-12 weeks

Phase 5 - Optimization:
  - Monitor performance
  - Optimize frequently used metrics
  - Gather user feedback
  - Continuous improvement
```

## Success Metrics for Metric Store

```yaml
Adoption:
  - % of dashboards using metric store definitions
  - % of analysts using APIs
  - Number of self-service metric queries

Quality:
  - Metric duplication reduction
  - Calculation inconsistency issues (trend down)
  - User-reported metric accuracy

Efficiency:
  - Time to add new metric
  - Time to update metric definition
  - Dashboard creation time reduction
  - Query latency improvement

ROI:
  - Analyst hours saved
  - Faster business decision-making
  - Reduced errors from inconsistent metrics
```
