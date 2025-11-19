# Metric Layer Architecture Reference

## Overview

A metric layer (also called semantic layer or headless BI) provides a centralized repository of business logic and metric definitions. This reference details architectural patterns based on implementations at Airbnb (Minerva), Airbnb, Transform, and other leading companies.

## Core Concepts

### What is a Metric Layer?

```yaml
Definition:
  An abstraction layer that sits between data warehouses and
  consumption tools, providing consistent business logic and
  metric definitions across all analytics interfaces.

Purpose:
  - Single source of truth for metrics
  - Centralized business logic
  - Consistent calculations
  - Simplified data access
  - Reduced technical debt

Key Benefits:
  - No more metric inconsistencies
  - Faster dashboard development
  - Easier metric evolution
  - Better governance
  - Improved trust in data
```

### The Metric Stack

```
┌─────────────────────────────────────┐
│   Consumption Layer                 │
│   - BI Tools (Tableau, Looker)     │
│   - SQL Interfaces (Mode, Hex)     │
│   - Python/R Notebooks             │
│   - REST APIs                       │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│   METRIC LAYER                      │
│   - Metric definitions              │
│   - Business logic                  │
│   - Dimension management            │
│   - Access control                  │
│   - Caching                         │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│   Data Transformation Layer         │
│   - dbt models                      │
│   - Data modeling                   │
│   - Quality tests                   │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│   Data Warehouse                    │
│   - Snowflake / BigQuery / Redshift │
└─────────────────────────────────────┘
```

## Architecture Patterns

### Pattern 1: Code-Based Definitions (dbt Metrics, LookML)

```yaml
# dbt metric example
metrics:
  - name: monthly_recurring_revenue
    label: Monthly Recurring Revenue
    model: ref('fct_subscriptions')
    description: >
      Sum of all active subscription amounts at the end of the month.
      Excludes trials and cancelled subscriptions.

    calculation_method: sum
    expression: subscription_amount

    timestamp: subscription_date
    time_grains: [day, week, month, quarter, year]

    dimensions:
      - subscription_tier
      - customer_segment
      - region

    filters:
      - field: subscription_status
        operator: '='
        value: "'active'"
      - field: is_trial
        operator: '='
        value: 'false'

    meta:
      owner: finance_analytics
      certification: verified
      sla: daily_by_9am
```

**Pros:**
- Version controlled (Git)
- Code review process
- Easy to test
- CI/CD integration
- Documentation as code

**Cons:**
- Requires technical skills
- Deployment process needed
- Less accessible to business users

**Best For:**
- Engineering-led organizations
- Complex calculations
- High governance needs

### Pattern 2: Configuration-Based (Cube.js)

```javascript
// Cube.js schema
cube(`Subscriptions`, {
  sql: `SELECT * FROM fct_subscriptions`,

  measures: {
    monthly_recurring_revenue: {
      sql: `subscription_amount`,
      type: `sum`,
      description: 'Sum of all active subscription amounts',
      filters: [
        { sql: `${CUBE}.subscription_status = 'active'` },
        { sql: `${CUBE}.is_trial = false` }
      ]
    },

    active_subscriptions: {
      sql: `subscription_id`,
      type: `countDistinct`,
      description: 'Number of active subscriptions'
    },

    arpu: {
      sql: `${monthly_recurring_revenue} / ${active_subscriptions}`,
      type: `number`,
      description: 'Average revenue per subscription'
    }
  },

  dimensions: {
    subscription_tier: {
      sql: `tier`,
      type: `string`
    },

    customer_segment: {
      sql: `segment`,
      type: `string`
    },

    subscription_date: {
      sql: `date`,
      type: `time`
    }
  }
});
```

**Pros:**
- Flexible configuration
- API-first design
- Real-time queries
- Good caching

**Cons:**
- JavaScript/YAML knowledge required
- Self-hosted complexity
- Learning curve

**Best For:**
- API-driven applications
- Embedded analytics
- Real-time dashboards

### Pattern 3: UI-Based (Transform, Superset Metrics)

```yaml
# Transform metric definition (UI represented as YAML)
metric:
  name: Monthly Recurring Revenue
  sql_name: monthly_recurring_revenue

  type: simple
  aggregation: sum
  sql_expression: subscription_amount

  base_table: fct_subscriptions

  filters:
    - column: subscription_status
      operator: equals
      value: active
    - column: is_trial
      operator: equals
      value: false

  default_dimensions:
    - subscription_tier
    - customer_segment

  time_dimension: subscription_date
  default_time_grain: month

  owner: finance_analytics@company.com
  certified: true

  description: >
    Total monthly subscription revenue from active,
    non-trial subscriptions.
```

**Pros:**
- No code required
- Visual interface
- Quick to create
- Business user friendly

**Cons:**
- Less version control
- Harder to review changes
- Potential for drift
- Export/import complexity

**Best For:**
- Business-led analytics
- Rapid prototyping
- Non-technical teams

## Key Components

### 1. Metric Definitions

#### Metric Types

```yaml
Simple Metrics:
  Definition: Single aggregation on a column
  Example:
    name: total_revenue
    type: sum
    column: revenue_amount

Derived Metrics:
  Definition: Calculation based on other metrics
  Example:
    name: conversion_rate
    type: ratio
    numerator: conversions
    denominator: visitors

Funnel Metrics:
  Definition: Sequential step analysis
  Example:
    name: signup_funnel
    steps:
      - visit
      - signup_start
      - email_verify
      - signup_complete

Cohort Metrics:
  Definition: Time-based grouping
  Example:
    name: cohort_retention
    cohort_dimension: signup_month
    retention_event: monthly_active
```

#### Metric Metadata

```yaml
Required Fields:
  - name: Unique identifier
  - label: Display name
  - description: What it measures
  - calculation: How it's computed
  - owner: Who maintains it

Optional Fields:
  - certification: verified | draft | deprecated
  - sla: Data freshness expectation
  - tags: Categorization
  - related_metrics: Similar or related
  - documentation_url: Detailed docs
  - change_log: Version history
```

### 2. Dimensions

```yaml
Dimension Types:

Categorical:
  Examples:
    - customer_segment: [enterprise, mid_market, smb]
    - product_category: [software, hardware, services]
    - region: [north_america, europe, asia_pacific]

Temporal:
  Examples:
    - order_date
    - signup_timestamp
    - fiscal_quarter
  Grains: [hour, day, week, month, quarter, year]

Boolean:
  Examples:
    - is_trial
    - has_paid
    - is_active

Numeric (for filtering/segmentation):
  Examples:
    - account_age_days
    - lifetime_value
    - number_of_users
```

### 3. Filters

```yaml
Filter Types:

Metric-Level Filters:
  Applied to specific metric calculations
  Example:
    metric: active_users
    filter: WHERE last_seen_date >= CURRENT_DATE - 30

Dimension Filters:
  User-selected at query time
  Example:
    dimension: region
    values: [north_america, europe]

Row-Level Security:
  Automatic filtering based on user context
  Example:
    sales_rep: WHERE territory = current_user_territory()
```

### 4. Relationships

```yaml
Join Paths:
  Define how tables connect

  Example:
    customers:
      - to: orders
        type: one_to_many
        join_on: customers.customer_id = orders.customer_id

      - to: subscriptions
        type: one_to_many
        join_on: customers.customer_id = subscriptions.customer_id

Fan-Out Protection:
  Prevent double-counting from joins

  Strategies:
    - Use COUNT DISTINCT instead of COUNT
    - Pre-aggregate before joining
    - Define primary metrics per grain
```

## Implementation Approaches

### Approach 1: Airbnb's Minerva

```yaml
Architecture:
  - Metadata service (metric definitions)
  - Query generation engine
  - Caching layer
  - Access control
  - Multiple interfaces (SQL, API, UI)

Key Features:
  - Version controlled metrics
  - Dimensional modeling
  - Time intelligence
  - Certification workflow
  - Usage tracking

Tech Stack:
  - Python backend
  - React frontend
  - Presto/Hive for querying
  - Internal metadata store

Governance:
  - Metric owners required
  - Certification process
  - Change management
  - Deprecation workflow
```

### Approach 2: dbt Metrics

```yaml
Architecture:
  - Metrics defined in YAML
  - dbt transformations
  - Adapter-based querying
  - Integration via dbt Semantic Layer API

Key Features:
  - Git version control
  - dbt testing framework
  - Documentation generation
  - CI/CD integration

Tech Stack:
  - dbt Core/Cloud
  - SQL transformations
  - YAML configurations
  - Semantic Layer Server (dbt Cloud)

Governance:
  - Code review process
  - Automated testing
  - Documentation requirements
  - Ownership in metadata
```

### Approach 3: Cube.js Headless BI

```yaml
Architecture:
  - Cube.js server
  - Schema definitions
  - Caching layer (Redis)
  - REST/GraphQL APIs
  - Frontend SDK

Key Features:
  - Pre-aggregations
  - Real-time queries
  - Multi-tenancy
  - SQL push-down

Tech Stack:
  - Node.js backend
  - Redis for caching
  - Any SQL database
  - REST/GraphQL API

Governance:
  - Schema version control
  - Access control policies
  - Query logging
  - Cost monitoring
```

## Design Patterns

### Pattern: Incremental Metric Adoption

```yaml
Phase 1: Core Metrics
  Scope: 10-20 most important metrics
  Timeline: 1-2 months
  Metrics:
    - Revenue (MRR, ARR)
    - User engagement (DAU, MAU)
    - Growth (new customers, churn)

Phase 2: Department Metrics
  Scope: 50-100 metrics
  Timeline: 3-6 months
  Coverage:
    - Sales metrics
    - Marketing metrics
    - Product metrics
    - Operations metrics

Phase 3: Comprehensive Coverage
  Scope: 200-500 metrics
  Timeline: 12+ months
  Goal: All standardized metrics in layer
```

### Pattern: Metric Namespaces

```yaml
Structure:
  domain.entity.metric_name

Examples:
  finance.revenue.mrr
  finance.revenue.arr
  finance.costs.cogs

  product.users.dau
  product.users.mau
  product.users.stickiness

  marketing.acquisition.cac
  marketing.acquisition.conversion_rate

Benefits:
  - Clear organization
  - Avoid naming conflicts
  - Easy to find related metrics
  - Scalable structure
```

### Pattern: Metric Versioning

```yaml
Scenario: Need to change MRR calculation

Approach 1: Version Suffix
  - mrr_v1 (deprecated)
  - mrr_v2 (current)

  Pros: Clear history, parallel use
  Cons: Namespace pollution

Approach 2: Effective Dating
  - mrr (always points to current)
  - effective_from: 2025-01-01
  - previous_version: archived

  Pros: Clean namespace, historical accuracy
  Cons: More complex implementation

Approach 3: Git-Style Versioning
  - Metric definitions in Git
  - Tags for versions
  - Checkout specific version

  Pros: Full history, diff capability
  Cons: Requires Git integration
```

## Query Translation

### From Metric Layer to SQL

```yaml
User Request:
  metric: monthly_recurring_revenue
  dimensions: [subscription_tier]
  filters:
    - region = 'north_america'
  time_grain: month
  date_range: last_12_months

Generated SQL:
  SELECT
    DATE_TRUNC('month', subscription_date) as month,
    subscription_tier,
    SUM(subscription_amount) as monthly_recurring_revenue
  FROM fct_subscriptions
  WHERE subscription_status = 'active'
    AND is_trial = false
    AND region = 'north_america'
    AND subscription_date >= CURRENT_DATE - INTERVAL '12 months'
  GROUP BY 1, 2
  ORDER BY 1, 2
```

## Performance Optimization

### Caching Strategies

```yaml
Query-Level Caching:
  - Cache query results
  - TTL: 1 hour for most metrics
  - Refresh on data update
  - User-specific cache keys

Pre-Aggregations:
  - Materialize common rollups
  - Daily: All metrics by day
  - Monthly: All metrics by month
  - By dimension: Top dimensions

  Example:
    CREATE TABLE mrr_by_tier_month AS
    SELECT
      DATE_TRUNC('month', date) as month,
      subscription_tier,
      SUM(subscription_amount) as mrr
    FROM fct_subscriptions
    WHERE subscription_status = 'active'
    GROUP BY 1, 2

Incremental Updates:
  - Only process new/changed data
  - Use dbt incremental models
  - Partition by date
  - Merge updates
```

### Query Optimization

```yaml
Best Practices:
  - Push filters down to base tables
  - Use columnar storage
  - Partition large tables
  - Create covering indexes
  - Limit result sizes
  - Implement query timeouts

Example Optimization:
  Bad:
    SELECT * FROM orders
    JOIN customers USING (customer_id)
    WHERE order_date >= '2025-01-01'

  Good:
    SELECT o.* FROM orders o
    WHERE o.order_date >= '2025-01-01'
    -- Filtered before join
    JOIN customers c ON o.customer_id = c.customer_id
```

## Access Control

```yaml
Metric-Level Permissions:
  public_metrics:
    - Can be queried by anyone
    - Example: DAU, page views

  internal_metrics:
    - Require employee access
    - Example: MRR, churn rate

  confidential_metrics:
    - Restricted to specific roles
    - Example: Unit economics, margins

Dimension-Level Permissions:
  Row-Level Security:
    - Sales rep sees own territory
    - Manager sees team data
    - Executive sees all

  Column-Level Security:
    - Hide sensitive dimensions
    - Mask PII data
    - Restrict financial details
```

## Testing & Validation

```yaml
Metric Tests:

Unit Tests:
  - Known input → expected output
  - Edge case handling
  - Null value treatment
  - Type validation

Integration Tests:
  - Cross-metric consistency
  - Dimension compatibility
  - Filter application
  - Join correctness

Reconciliation Tests:
  - Compare to source systems
  - Check against manual calculations
  - Validate historical data
  - Cross-tool comparison

Example dbt Test:
  - name: mrr_positive
    description: MRR should always be positive
    sql: |
      SELECT * FROM {{ ref('mrr') }}
      WHERE monthly_recurring_revenue < 0
```

## Migration Strategy

```yaml
From Legacy to Metric Layer:

Step 1: Inventory
  - List all existing metrics
  - Document current calculations
  - Identify inconsistencies
  - Prioritize migration

Step 2: Define
  - Create metric definitions
  - Standardize calculations
  - Add documentation
  - Get stakeholder buy-in

Step 3: Implement
  - Build metric layer
  - Create tests
  - Validate results
  - Performance tune

Step 4: Adopt
  - Train users
  - Migrate dashboards
  - Deprecate old calculations
  - Monitor usage

Step 5: Optimize
  - Add caching
  - Create pre-aggregations
  - Refine definitions
  - Expand coverage
```

## References

- Airbnb Minerva blog post
- dbt Metrics documentation
- Cube.js best practices
- Transform Metrics Layer Guide
- "The Semantic Layer" by Benn Stancil
