# Self-Service Analytics Training Materials

## Version 1.0
**Last Updated:** November 2024
**Audience:** Data Analysts, Business Analysts, Non-Technical Stakeholders

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Concepts](#core-concepts)
3. [Navigation & Interface](#navigation--interface)
4. [Running Queries](#running-queries)
5. [Creating Dashboards](#creating-dashboards)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Topics](#advanced-topics)

---

## Getting Started

### Prerequisites
- Active company email account
- Access credentials to data warehouse (Snowflake/Redshift/BigQuery)
- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+)
- Basic SQL knowledge (helpful but not required)

### Initial Setup (First-Time Users)
1. Navigate to analytics portal: `https://analytics.company.com`
2. Click "Sign In" and authenticate with SSO
3. Complete the onboarding checklist (15 minutes)
4. Review role-based access level
5. Start with pre-built templates

### Roles & Permissions
- **Viewer**: Access to dashboards and reports
- **Analyst**: Query builder, dashboard creation, sandbox queries
- **Engineer**: Data pipeline management, schema creation
- **Admin**: Full platform access, user management

---

## Core Concepts

### Metrics
Standardized, business-approved calculations that drive consistency across all analytics.

**Key Characteristics:**
- Owned by specific teams (Finance, Product, Marketing)
- SLA enforcement (daily, hourly refresh)
- Built-in drill-down dimensions
- Version controlled and documented
- Certification status tracked

**Example Metrics:**
- Monthly Recurring Revenue (MRR)
- Daily Active Users (DAU)
- Customer Acquisition Cost (CAC)

### Data Models
Logical representations of physical tables in the warehouse.

- **Dimensions**: Descriptive attributes (customers, products, dates)
- **Facts**: Measurable events (transactions, clicks, sessions)
- **Intermediate**: Staging/transformation tables

### Dimensions
Categorical grouping columns available for analysis.

Common dimensions across all models:
- Time dimensions: date, week, month, quarter, year
- Geography: region, country, city
- Customer: segment, cohort, acquisition_channel
- Product: category, line, tier

### Filters
Applied constraints that narrow result sets.

**Types:**
- Static: constant value (e.g., country = 'USA')
- Dynamic: user/session-based (e.g., assigned_territory_id)
- Temporal: relative date ranges (e.g., last 90 days)

---

## Navigation & Interface

### Dashboard Homepage
Main entry point with:
- **Featured Dashboards**: Most-used and high-impact reports
- **My Dashboards**: Custom dashboards you've created
- **Shared with Me**: Dashboards other users shared
- **Recent Views**: Last 10 dashboards accessed
- **Quick Links**: New query, create dashboard, documentation

### Query Editor
IDE for writing SQL queries with:
- Syntax highlighting and autocomplete
- Schema browser and metadata explorer
- Query history and saved queries
- Execution plan viewer
- Result caching (5-minute default)

### Dashboard Builder
Visual interface for composing reports:
- Drag-and-drop tiles
- Pre-built chart types (table, line, bar, pie, map, gauge)
- Metric selection with quick filters
- Parameter and variable support
- Alert configuration

---

## Running Queries

### Using the Query Editor

**Basic Query Structure:**
```sql
SELECT
  DATE_TRUNC('month', event_date) as month,
  user_segment,
  COUNT(DISTINCT user_id) as dau,
  SUM(event_value) as total_value
FROM analytics.events
WHERE event_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY 1, 2
ORDER BY 1 DESC, 2
LIMIT 10000;
```

### Execution Best Practices
1. **Use LIMIT**: Always add LIMIT to prevent runaway queries
2. **Sample First**: Test with TABLESAMPLE before full run
3. **Check Plan**: Review query plan for full table scans
4. **Schedule Large**: Long-running queries (>5 min) via scheduler
5. **Use Caching**: Leverage cached results for ad-hoc analysis

### Query Guidelines
- **Max Runtime**: 10 minutes for interactive queries
- **Result Rows**: 100k for UI display, 1M for export
- **Concurrency**: 5 active queries per user
- **Cost Control**: Estimated credits shown before execution

---

## Creating Dashboards

### Step-by-Step Guide

#### 1. Start Dashboard
- Click "New Dashboard"
- Name: descriptive, e.g., "Q4 Sales Performance"
- Description: purpose and audience
- Set privacy: Personal, Team, or Public

#### 2. Add Tiles
- Click "Add Tile"
- Choose source: Metric, Query, or Visualization
- If Metric: Select metric + dimensions + filters
- If Query: Enter custom SQL
- Configure chart type and styling

#### 3. Configure Filters
- Add dashboard-level filters (apply to multiple tiles)
- Types: dropdown, date range, text input
- Link to tile columns for interaction

#### 4. Set Parameters
- Create dynamic values (e.g., ${current_month})
- Use in queries with ${parameter_name}
- Support cascading parameters

#### 5. Save & Share
- Click "Publish"
- Set auto-refresh: manual, hourly, daily
- Share with users/teams
- Configure alerts on thresholds

### Dashboard Template Best Practices

**Title & Context:**
- Clear, action-oriented title
- Executive summary or key insight
- Last refresh timestamp

**Layout:**
- No more than 6 tiles per row
- Related tiles grouped together
- Priority top-left, supporting lower-right

**Interactivity:**
- Filter by business dimension (region, product)
- Drill-through for investigation
- Temporal navigation (month/year)

**Documentation:**
- Hover-text explaining metrics
- Links to underlying data dictionary
- Owner contact information

---

## Best Practices

### Query Performance

**Dos:**
- ✓ Use indexes on WHERE clause columns
- ✓ Join on primary keys when possible
- ✓ Aggregate in warehouse, not BI tool
- ✓ Use date partitioning for large tables
- ✓ Cache intermediate results

**Don'ts:**
- ✗ SELECT * (always specify columns)
- ✗ Join large fact tables without filtering
- ✗ Nested subqueries (use CTEs instead)
- ✗ UDF functions on large result sets
- ✗ Implicit type conversions

### Dashboard Design

**Dos:**
- ✓ Start with hypothesis, then visualize
- ✓ Use color purposefully (red = alert)
- ✓ Include comparative context (YoY, benchmarks)
- ✓ Label axes and legends clearly
- ✓ Provide drill-down paths

**Don'ts:**
- ✗ Pie charts with >5 segments
- ✗ Dual-axis charts (hard to interpret)
- ✗ Decorative charts (no business logic)
- ✗ Metrics without dimension breakdown
- ✗ Dashboards without refresh schedule

### Data Governance

- **Document assumptions**: Filter logic, exclusions, calculations
- **Cite sources**: Link to underlying tables and queries
- **Track versions**: Use dashboard version history
- **Get certified**: Metrics go through approval workflow
- **Audit access**: Monitor who views sensitive data

---

## Troubleshooting

### Common Issues

**"Query Timeout" Error**
- Problem: Query exceeds 10-minute limit
- Solution:
  - Add WHERE clause to reduce data scope
  - Use SAMPLE() for exploratory analysis
  - Schedule query to run in background

**"Insufficient Permissions" Error**
- Problem: Missing role for dataset
- Solution:
  - Submit access request to admin
  - Check data governance policies
  - Try Analyst role sandbox schema

**"Stale Data" Issue**
- Problem: Dashboard shows old values
- Solution:
  - Check refresh schedule configuration
  - Force refresh (Ctrl+Shift+R)
  - Verify upstream pipeline completion

**"No Results" Returned**
- Problem: Query runs but returns 0 rows
- Solution:
  - Check filter conditions (too restrictive?)
  - Verify table has data for date range
  - Review join logic for NULL mismatches

### Getting Help

- **Chat Support**: Click help icon (M-F 9-5 PT)
- **Documentation**: Search knowledge base
- **Slack Channel**: #analytics-help
- **Email**: analytics-team@company.com
- **Status Page**: https://status.company.com

---

## Advanced Topics

### User-Defined Filters (UDF)

Create reusable filter logic:
```yaml
filter: active_customers
definition: |
  AND customer_status = 'active'
  AND subscription_end_date IS NULL
  AND ltv > 1000
owner: customer_analytics_team
```

### Row-Level Security (RLS)

Automatic data filtering by user attributes:
- Sales reps see only assigned territories
- Regional managers see region + subordinate territories
- Configured in data governance layer

### Scheduled Query Execution

For computationally expensive queries:
- Set schedule: daily, weekly, custom cron
- Define output location: table or email
- Monitor execution logs
- Alert on failures

### API Integration

Embed dashboards and metrics in applications:
```python
from analytics_sdk import Client

client = Client(api_key='...')
metric_data = client.get_metric(
  'daily_active_users',
  dimensions=['platform', 'country'],
  filters={'date': 'last_90_days'}
)
```

---

## Glossary

- **Fact**: A measurable, quantifiable event (sales, pageview, signup)
- **Dimension**: A categorical attribute used for grouping (date, region, product)
- **Grain**: Level of detail (daily, weekly, per-user)
- **SLA**: Service Level Agreement (e.g., data refreshed by 9 AM)
- **Lineage**: Data flow from source to final report
- **Mart**: Curated dataset for specific business purpose
- **Cardinality**: Number of unique values in a column

---

## Resources

- [Data Dictionary](https://docs.company.com/data-dictionary)
- [SQL Quick Reference](https://docs.company.com/sql-reference)
- [dbt Documentation](https://docs.company.com/dbt)
- [Governance Policies](https://docs.company.com/governance)
- [Training Videos](https://video.company.com/analytics-training)

