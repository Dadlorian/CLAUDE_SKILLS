# Metrics Layer Pattern

**Category**: Pattern
**Maturity Level**: Production-Ready
**Last Updated**: November 2025

## Pattern Overview

The Metrics Layer pattern establishes a centralized, version-controlled system for defining business metrics independently of BI tools. This creates a single source of truth that ensures consistency across dashboards, reports, and applications while enabling headless BI architectures.

**Problem Solved**: Without a metrics layer, organizations face:
- Inconsistent metric definitions across tools and teams
- Duplicated business logic in multiple dashboards
- Inability to change metric logic without updating every dashboard
- No clear ownership or documentation for metrics
- Difficult to trace metric lineage and dependencies

**Solution**: Implement a semantic layer that centralizes metric definitions, business logic, and dimensional relationships in a single, version-controlled repository that can be consumed by any BI tool or application.

---

## Architecture Pattern

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Consumption Layer                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Tableau  │  │  Looker  │  │  Custom  │  │   API    │   │
│  │          │  │          │  │   Apps   │  │  Clients │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Metrics API Layer                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         GraphQL / REST API                             │ │
│  │  - Query metrics by dimensions                         │ │
│  │  - Apply filters and time ranges                       │ │
│  │  - Return aggregated results                           │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  Metrics Computation Engine                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         SQL/Query Generator                            │ │
│  │  - Translate metric requests to SQL                   │ │
│  │  - Resolve dimensions and joins                       │ │
│  │  - Apply business logic                               │ │
│  │  - Optimize queries                                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Caching Layer (Optional)                       │ │
│  │  - Redis/Memcached for frequent queries              │ │
│  │  - Pre-aggregated metric values                      │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              Metrics Definition Layer (Git)                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Metric Definitions (YAML/Python/LookML)        │ │
│  │                                                        │ │
│  │  metrics/                                              │ │
│  │  ├── revenue.yml                                       │ │
│  │  ├── customers.yml                                     │ │
│  │  ├── engagement.yml                                    │ │
│  │  └── ...                                               │ │
│  │                                                        │ │
│  │  dimensions/                                           │ │
│  │  ├── date.yml                                          │ │
│  │  ├── geography.yml                                     │ │
│  │  └── product.yml                                       │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Data Warehouse                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Snowflake / BigQuery / Redshift / Databricks         │ │
│  │  - Fact tables                                         │ │
│  │  - Dimension tables                                    │ │
│  │  - Pre-aggregated rollups (optional)                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Approaches

### Approach 1: dbt Semantic Layer

**Technology**: dbt Core + dbt Cloud + MetricFlow

**Metric Definition (YAML)**

```yaml
# models/metrics/revenue_metrics.yml
version: 2

metrics:
  - name: total_revenue
    label: Total Revenue
    model: ref('fct_orders')
    description: "Sum of all order revenue excluding refunds"

    calculation_method: sum
    expression: order_amount

    timestamp: order_date
    time_grains: [day, week, month, quarter, year]

    dimensions:
      - customer_id
      - product_id
      - region
      - sales_channel

    filters:
      - field: order_status
        operator: '='
        value: "'completed'"
      - field: is_refund
        operator: '='
        value: "false"

    meta:
      owner: "finance-team@company.com"
      tags: ["revenue", "kpi", "executive"]

  - name: revenue_growth_rate
    label: Revenue Growth Rate (MoM)
    model: ref('fct_orders')
    description: "Month-over-month revenue growth rate"

    calculation_method: derived
    expression: |
      ({{ metric('total_revenue') }} -
       {{ metric('total_revenue', offset=-1, time_grain='month') }}) /
       {{ metric('total_revenue', offset=-1, time_grain='month') }}

    timestamp: order_date
    time_grains: [month, quarter, year]

    dimensions:
      - region
      - product_category

  - name: average_order_value
    label: Average Order Value (AOV)
    model: ref('fct_orders')
    description: "Average revenue per order"

    calculation_method: average
    expression: order_amount

    timestamp: order_date
    time_grains: [day, week, month, quarter, year]

    dimensions:
      - customer_id
      - product_id
      - region

    filters:
      - field: order_status
        operator: '='
        value: "'completed'"

  - name: customer_lifetime_value
    label: Customer Lifetime Value (CLV)
    model: ref('fct_customer_orders')
    description: "Total revenue generated by a customer over their lifetime"

    calculation_method: sum
    expression: order_amount

    timestamp: first_order_date
    time_grains: [month, quarter, year]

    dimensions:
      - customer_cohort
      - acquisition_channel
      - region

    filters:
      - field: order_status
        operator: '='
        value: "'completed'"
```

**Querying Metrics via dbt**

```bash
# Query a metric with dbt CLI
dbt run-operation query_metric --args '{
  "metric": "total_revenue",
  "grain": "month",
  "dimensions": ["region"],
  "where": "order_date >= '2024-01-01'"
}'

# Generate SQL for a metric
dbt compile --select metric:total_revenue
```

**Generated SQL (Example)**

```sql
-- SQL generated by dbt Semantic Layer for total_revenue
WITH base AS (
  SELECT
    DATE_TRUNC('month', order_date) AS time_dimension,
    region,
    SUM(order_amount) AS total_revenue
  FROM analytics.fct_orders
  WHERE order_status = 'completed'
    AND is_refund = false
    AND order_date >= '2024-01-01'
  GROUP BY 1, 2
)
SELECT * FROM base
ORDER BY time_dimension, region
```

**Integration with BI Tools**

```python
# Python client for dbt Semantic Layer
from dbt_semantic_interfaces.client import SemanticLayerClient

client = SemanticLayerClient(
    host="semantic-layer.cloud.getdbt.com",
    api_key="your_api_key"
)

# Query metric
result = client.query(
    metrics=["total_revenue", "average_order_value"],
    group_by=["metric_time__month", "region"],
    where=[
        "metric_time >= '2024-01-01'",
        "region IN ('US', 'EU')"
    ]
)

# Returns pandas DataFrame
print(result.to_df())
```

---

### Approach 2: Cube.js (Headless BI)

**Technology**: Cube.js (open-source semantic layer)

**Data Schema Definition (JavaScript)**

```javascript
// schema/Orders.js
cube('Orders', {
  sql: `SELECT * FROM analytics.fct_orders`,

  joins: {
    Customers: {
      sql: `${CUBE}.customer_id = ${Customers}.customer_id`,
      relationship: 'belongsTo'
    },
    Products: {
      sql: `${CUBE}.product_id = ${Products}.product_id`,
      relationship: 'belongsTo'
    }
  },

  measures: {
    totalRevenue: {
      sql: 'order_amount',
      type: 'sum',
      description: 'Total revenue from completed orders',
      filters: [
        { sql: `${CUBE}.order_status = 'completed'` },
        { sql: `${CUBE}.is_refund = false` }
      ],
      meta: {
        owner: 'finance-team@company.com',
        tags: ['revenue', 'kpi']
      }
    },

    averageOrderValue: {
      sql: 'order_amount',
      type: 'avg',
      description: 'Average order value',
      filters: [
        { sql: `${CUBE}.order_status = 'completed'` }
      ]
    },

    orderCount: {
      type: 'count',
      description: 'Number of orders'
    },

    revenueGrowthRate: {
      sql: `
        (${totalRevenue} - ${totalRevenue.offset('1 month')}) /
        ${totalRevenue.offset('1 month')}
      `,
      type: 'number',
      format: 'percent',
      description: 'Month-over-month revenue growth'
    },

    // Funnel conversion metric
    conversionRate: {
      sql: `
        ${Orders.completedOrders.count} /
        NULLIF(${Orders.count}, 0)
      `,
      type: 'number',
      format: 'percent'
    }
  },

  dimensions: {
    orderId: {
      sql: 'order_id',
      type: 'string',
      primaryKey: true
    },

    orderDate: {
      sql: 'order_date',
      type: 'time'
    },

    region: {
      sql: 'region',
      type: 'string'
    },

    salesChannel: {
      sql: 'sales_channel',
      type: 'string'
    },

    productCategory: {
      sql: `${Products.category}`,
      type: 'string'
    },

    customerSegment: {
      sql: `${Customers.segment}`,
      type: 'string'
    }
  },

  segments: {
    highValue: {
      sql: `${CUBE}.order_amount > 1000`,
      description: 'Orders over $1,000'
    },

    newCustomers: {
      sql: `${Customers.isNew} = true`,
      description: 'Orders from new customers'
    }
  },

  preAggregations: {
    main: {
      measures: [totalRevenue, averageOrderValue, orderCount],
      dimensions: [region, salesChannel, productCategory],
      timeDimension: orderDate,
      granularity: 'day',
      partitionGranularity: 'month',
      refreshKey: {
        every: '1 hour'
      }
    }
  }
});
```

**Customers Dimension (JavaScript)**

```javascript
// schema/Customers.js
cube('Customers', {
  sql: `SELECT * FROM analytics.dim_customers`,

  dimensions: {
    customerId: {
      sql: 'customer_id',
      type: 'string',
      primaryKey: true
    },

    name: {
      sql: 'customer_name',
      type: 'string'
    },

    email: {
      sql: 'email',
      type: 'string',
      meta: {
        pii: true  // Mark as PII for governance
      }
    },

    segment: {
      sql: 'customer_segment',
      type: 'string'
    },

    country: {
      sql: 'country',
      type: 'string'
    },

    region: {
      sql: `
        CASE
          WHEN country IN ('US', 'CA', 'MX') THEN 'North America'
          WHEN country IN ('GB', 'DE', 'FR', 'IT', 'ES') THEN 'Europe'
          WHEN country IN ('CN', 'JP', 'IN', 'SG') THEN 'Asia'
          ELSE 'Other'
        END
      `,
      type: 'string'
    },

    lifetimeValue: {
      sql: 'lifetime_value',
      type: 'number',
      format: 'currency'
    },

    firstOrderDate: {
      sql: 'first_order_date',
      type: 'time'
    },

    isNew: {
      sql: `DATEDIFF(day, first_order_date, CURRENT_DATE) <= 90`,
      type: 'boolean'
    }
  },

  measures: {
    count: {
      type: 'count'
    },

    avgLifetimeValue: {
      sql: 'lifetime_value',
      type: 'avg',
      format: 'currency'
    }
  }
});
```

**Querying Cube.js Metrics**

```javascript
// REST API query
POST /cubejs-api/v1/load
{
  "measures": [
    "Orders.totalRevenue",
    "Orders.averageOrderValue",
    "Orders.orderCount"
  ],
  "timeDimensions": [{
    "dimension": "Orders.orderDate",
    "granularity": "month",
    "dateRange": ["2024-01-01", "2024-12-31"]
  }],
  "dimensions": [
    "Orders.region",
    "Orders.salesChannel"
  ],
  "filters": [{
    "member": "Orders.region",
    "operator": "equals",
    "values": ["US", "EU"]
  }]
}

// Response (JSON)
{
  "data": [
    {
      "Orders.orderDate.month": "2024-01-01T00:00:00.000",
      "Orders.region": "US",
      "Orders.salesChannel": "Online",
      "Orders.totalRevenue": 1245678.50,
      "Orders.averageOrderValue": 156.23,
      "Orders.orderCount": 7972
    },
    // ... more rows
  ]
}
```

**React Integration**

```javascript
// React component using Cube.js
import { useCubeQuery } from '@cubejs-client/react';

function RevenueChart() {
  const { resultSet, isLoading, error } = useCubeQuery({
    measures: ['Orders.totalRevenue', 'Orders.orderCount'],
    timeDimensions: [{
      dimension: 'Orders.orderDate',
      granularity: 'month',
      dateRange: 'Last 12 months'
    }],
    dimensions: ['Orders.region']
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const chartData = resultSet.chartPivot();

  return <LineChart data={chartData} />;
}
```

---

### Approach 3: Custom Python Metrics Framework

**Technology**: Python + Jinja2 + SQLAlchemy

**Metric Definition (YAML + Python)**

```yaml
# metrics/revenue_metrics.yaml
metrics:
  total_revenue:
    display_name: "Total Revenue"
    description: "Sum of order revenue excluding refunds"
    type: sum
    sql: "order_amount"
    table: "analytics.fct_orders"
    filters:
      - "order_status = 'completed'"
      - "is_refund = false"
    dimensions:
      - date
      - region
      - product_id
      - customer_segment
    time_dimension: "order_date"
    time_grains: ["day", "week", "month", "quarter", "year"]
    owner: "finance@company.com"
    tags: ["revenue", "kpi", "certified"]

  customer_lifetime_value:
    display_name: "Customer Lifetime Value"
    description: "Total revenue per customer over their lifetime"
    type: sum
    sql: "order_amount"
    table: "analytics.fct_orders"
    group_by: ["customer_id"]
    filters:
      - "order_status = 'completed'"
    dimensions:
      - acquisition_channel
      - customer_cohort
      - region
    owner: "growth@company.com"
    tags: ["customer", "ltv", "certified"]

  revenue_per_user:
    display_name: "Revenue Per User (RPU)"
    description: "Average revenue per active user"
    type: derived
    formula: "{{ metric('total_revenue') }} / {{ metric('active_users') }}"
    dimensions:
      - date
      - region
    owner: "product@company.com"
```

**Python Metrics Engine**

```python
# metrics_engine.py
import yaml
from jinja2 import Template
from typing import List, Dict, Any
import pandas as pd
from sqlalchemy import create_engine

class MetricsEngine:
    def __init__(self, config_path: str, db_connection_string: str):
        self.metrics = self._load_metrics(config_path)
        self.engine = create_engine(db_connection_string)

    def _load_metrics(self, path: str) -> Dict[str, Any]:
        """Load metric definitions from YAML files."""
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _generate_sql(
        self,
        metric_name: str,
        dimensions: List[str] = None,
        filters: List[str] = None,
        time_grain: str = 'day',
        date_range: tuple = None
    ) -> str:
        """Generate SQL for a metric query."""
        metric = self.metrics['metrics'][metric_name]

        # Base metric SQL
        if metric['type'] == 'sum':
            measure_sql = f"SUM({metric['sql']}) AS {metric_name}"
        elif metric['type'] == 'avg':
            measure_sql = f"AVG({metric['sql']}) AS {metric_name}"
        elif metric['type'] == 'count':
            measure_sql = f"COUNT({metric['sql']}) AS {metric_name}"
        else:
            raise ValueError(f"Unknown metric type: {metric['type']}")

        # Time dimension
        time_dim = metric.get('time_dimension')
        if time_dim and time_grain:
            time_sql = f"DATE_TRUNC('{time_grain}', {time_dim}) AS time_dimension"
        else:
            time_sql = None

        # Dimensions
        dim_sql = ', '.join(dimensions) if dimensions else None

        # Assemble SELECT clause
        select_parts = [p for p in [time_sql, dim_sql, measure_sql] if p]
        select_clause = ', '.join(select_parts)

        # Filters
        filter_clauses = metric.get('filters', [])
        if filters:
            filter_clauses.extend(filters)
        if date_range and time_dim:
            filter_clauses.append(
                f"{time_dim} BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
            )

        where_clause = (
            'WHERE ' + ' AND '.join(filter_clauses)
            if filter_clauses else ''
        )

        # GROUP BY
        group_by_parts = []
        if time_sql:
            group_by_parts.append('1')
        if dimensions:
            start_idx = 2 if time_sql else 1
            group_by_parts.extend([
                str(i) for i in range(start_idx, start_idx + len(dimensions))
            ])
        group_by_clause = (
            'GROUP BY ' + ', '.join(group_by_parts)
            if group_by_parts else ''
        )

        # Assemble final SQL
        sql = f"""
        SELECT
            {select_clause}
        FROM {metric['table']}
        {where_clause}
        {group_by_clause}
        ORDER BY 1
        """

        return sql.strip()

    def query_metric(
        self,
        metric_name: str,
        dimensions: List[str] = None,
        filters: List[str] = None,
        time_grain: str = 'day',
        date_range: tuple = None
    ) -> pd.DataFrame:
        """Query a metric and return results as DataFrame."""
        sql = self._generate_sql(
            metric_name, dimensions, filters, time_grain, date_range
        )

        print(f"Executing SQL:\n{sql}\n")

        return pd.read_sql(sql, self.engine)

    def query_multiple_metrics(
        self,
        metric_names: List[str],
        dimensions: List[str] = None,
        time_grain: str = 'day',
        date_range: tuple = None
    ) -> pd.DataFrame:
        """Query multiple metrics and join results."""
        dataframes = []

        for metric_name in metric_names:
            df = self.query_metric(
                metric_name, dimensions, None, time_grain, date_range
            )
            dataframes.append(df)

        # Join all dataframes
        result = dataframes[0]
        for df in dataframes[1:]:
            join_keys = ['time_dimension'] + (dimensions or [])
            result = result.merge(df, on=join_keys, how='outer')

        return result

    def get_metric_info(self, metric_name: str) -> Dict[str, Any]:
        """Get metadata about a metric."""
        metric = self.metrics['metrics'][metric_name]
        return {
            'name': metric_name,
            'display_name': metric['display_name'],
            'description': metric['description'],
            'type': metric['type'],
            'owner': metric['owner'],
            'tags': metric['tags'],
            'available_dimensions': metric.get('dimensions', []),
            'time_grains': metric.get('time_grains', [])
        }

    def list_metrics(self, tag: str = None) -> List[str]:
        """List all available metrics, optionally filtered by tag."""
        metrics = self.metrics['metrics']

        if tag:
            return [
                name for name, meta in metrics.items()
                if tag in meta.get('tags', [])
            ]

        return list(metrics.keys())
```

**Usage Example**

```python
# Usage example
from metrics_engine import MetricsEngine

# Initialize engine
engine = MetricsEngine(
    config_path='metrics/revenue_metrics.yaml',
    db_connection_string='snowflake://user:pass@account/db/schema'
)

# Query single metric
revenue_df = engine.query_metric(
    metric_name='total_revenue',
    dimensions=['region', 'sales_channel'],
    time_grain='month',
    date_range=('2024-01-01', '2024-12-31')
)

print(revenue_df.head())
# Output:
#   time_dimension    region  sales_channel  total_revenue
# 0     2024-01-01        US         Online      1245678.50
# 1     2024-01-01        US        Offline       892345.20
# 2     2024-01-01        EU         Online       734521.80
# ...

# Query multiple metrics
combined_df = engine.query_multiple_metrics(
    metric_names=['total_revenue', 'customer_lifetime_value'],
    dimensions=['region'],
    time_grain='month',
    date_range=('2024-01-01', '2024-06-30')
)

# Get metric metadata
info = engine.get_metric_info('total_revenue')
print(info)
# Output:
# {
#   'name': 'total_revenue',
#   'display_name': 'Total Revenue',
#   'description': 'Sum of order revenue excluding refunds',
#   'type': 'sum',
#   'owner': 'finance@company.com',
#   'tags': ['revenue', 'kpi', 'certified'],
#   'available_dimensions': ['date', 'region', 'product_id', ...],
#   'time_grains': ['day', 'week', 'month', 'quarter', 'year']
# }

# List all KPI metrics
kpi_metrics = engine.list_metrics(tag='kpi')
print(kpi_metrics)
# Output: ['total_revenue', 'active_users', 'conversion_rate', ...]
```

**REST API Wrapper (FastAPI)**

```python
# api.py
from fastapi import FastAPI, Query
from typing import List, Optional
from metrics_engine import MetricsEngine

app = FastAPI(title="Metrics API")

engine = MetricsEngine(
    config_path='metrics/revenue_metrics.yaml',
    db_connection_string='snowflake://...'
)

@app.get("/metrics")
def list_metrics(tag: Optional[str] = None):
    """List all available metrics."""
    return {"metrics": engine.list_metrics(tag=tag)}

@app.get("/metrics/{metric_name}")
def get_metric_info(metric_name: str):
    """Get metadata for a specific metric."""
    return engine.get_metric_info(metric_name)

@app.post("/metrics/query")
def query_metric(
    metric_name: str,
    dimensions: Optional[List[str]] = Query(None),
    filters: Optional[List[str]] = Query(None),
    time_grain: str = 'day',
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Query a metric and return results."""
    date_range = (start_date, end_date) if start_date and end_date else None

    df = engine.query_metric(
        metric_name=metric_name,
        dimensions=dimensions,
        filters=filters,
        time_grain=time_grain,
        date_range=date_range
    )

    return {
        "metric": metric_name,
        "data": df.to_dict(orient='records')
    }

# Run with: uvicorn api:app --reload
```

---

## Governance & Best Practices

### Metric Certification Process

```yaml
# metrics/governance.yaml
certification_levels:
  certified:
    description: "Official company metric, approved for executive reporting"
    requirements:
      - Code review by data team
      - Approved by metric owner
      - Documentation complete
      - Testing coverage > 90%
      - Used in production for 30+ days
    badge: "✓ Certified"

  experimental:
    description: "New metric under development"
    requirements:
      - Code review
      - Basic documentation
    badge: "⚠ Experimental"

  deprecated:
    description: "Metric scheduled for removal"
    requirements:
      - Migration plan documented
      - Sunset date specified
    badge: "⛔ Deprecated"

metric_approval_workflow:
  steps:
    1_submit:
      description: "Create pull request with new metric definition"
      required_files:
        - metric YAML definition
        - documentation
        - test queries

    2_review:
      description: "Code review by data team"
      reviewers:
        - data_eng_team
        - metric_owner
      checks:
        - SQL correctness
        - Performance impact
        - Naming conventions
        - Documentation quality

    3_validate:
      description: "Automated validation"
      tests:
        - Generate SQL successfully
        - Query executes < 30 seconds
        - Results match expected ranges
        - No PII exposure

    4_approve:
      description: "Final approval"
      approvers:
        - head_of_data
        - metric_owner_director

    5_deploy:
      description: "Deploy to production"
      actions:
        - Merge to main branch
        - Update metric catalog
        - Notify stakeholders
```

### Metric Naming Conventions

```yaml
# standards/naming_conventions.yaml
naming_standards:
  metrics:
    pattern: "{domain}_{entity}_{aggregation}_{timeframe?}"
    examples:
      good:
        - "revenue_total"
        - "customers_active_monthly"
        - "orders_avg_value"
        - "churn_rate_monthly"
      bad:
        - "rev"  # Too abbreviated
        - "TotalRevenue"  # Use snake_case
        - "the_revenue"  # No articles

  dimensions:
    pattern: "{entity}_{attribute}"
    examples:
      good:
        - "customer_segment"
        - "product_category"
        - "geo_region"
      bad:
        - "segment"  # Not specific enough
        - "customerSegment"  # Use snake_case

  time_dimensions:
    standard: "{entity}_date"
    examples:
      - "order_date"
      - "signup_date"
      - "churn_date"
```

### Testing Strategy

```python
# tests/test_metrics.py
import pytest
from metrics_engine import MetricsEngine

@pytest.fixture
def engine():
    return MetricsEngine(
        config_path='metrics/revenue_metrics.yaml',
        db_connection_string='snowflake://test'
    )

def test_total_revenue_sql_generation(engine):
    """Test that total_revenue metric generates correct SQL."""
    sql = engine._generate_sql(
        metric_name='total_revenue',
        dimensions=['region'],
        time_grain='month',
        date_range=('2024-01-01', '2024-12-31')
    )

    # Assert key components present
    assert 'SUM(order_amount)' in sql
    assert "order_status = 'completed'" in sql
    assert 'is_refund = false' in sql
    assert 'DATE_TRUNC' in sql
    assert 'GROUP BY' in sql

def test_metric_query_returns_data(engine):
    """Test that querying a metric returns expected data."""
    df = engine.query_metric(
        metric_name='total_revenue',
        dimensions=['region'],
        time_grain='month',
        date_range=('2024-01-01', '2024-01-31')
    )

    assert not df.empty
    assert 'total_revenue' in df.columns
    assert 'region' in df.columns
    assert df['total_revenue'].dtype in ['float64', 'int64']

def test_metric_value_ranges(engine):
    """Test that metric values are within expected ranges."""
    df = engine.query_metric(
        metric_name='total_revenue',
        time_grain='month',
        date_range=('2024-01-01', '2024-01-31')
    )

    revenue = df['total_revenue'].sum()

    # Revenue should be positive and within reasonable range
    assert revenue > 0
    assert revenue < 100_000_000  # Adjust based on your business

def test_all_metrics_load_successfully(engine):
    """Test that all defined metrics can be loaded."""
    metrics = engine.list_metrics()

    assert len(metrics) > 0

    for metric_name in metrics:
        info = engine.get_metric_info(metric_name)
        assert 'display_name' in info
        assert 'description' in info
        assert 'owner' in info

def test_derived_metric_calculation(engine):
    """Test that derived metrics calculate correctly."""
    # Query the derived metric
    df = engine.query_metric(
        metric_name='revenue_per_user',
        time_grain='month',
        date_range=('2024-01-01', '2024-01-31')
    )

    # Also query the base metrics
    revenue_df = engine.query_metric(
        metric_name='total_revenue',
        time_grain='month',
        date_range=('2024-01-01', '2024-01-31')
    )

    users_df = engine.query_metric(
        metric_name='active_users',
        time_grain='month',
        date_range=('2024-01-01', '2024-01-31')
    )

    # Verify calculation
    expected_rpu = (
        revenue_df['total_revenue'].sum() /
        users_df['active_users'].sum()
    )

    assert abs(df['revenue_per_user'].sum() - expected_rpu) < 0.01
```

---

## Migration Strategy

### Phase 1: Inventory Existing Metrics (2 weeks)

1. **Audit current state**:
   - List all dashboards and reports
   - Extract metric definitions
   - Identify duplicates and inconsistencies
   - Document business logic

2. **Prioritize metrics**:
   - Tier 1: Executive KPIs (10-20 metrics)
   - Tier 2: Team-level metrics (50-100 metrics)
   - Tier 3: Exploratory metrics (100+ metrics)

### Phase 2: Build Core Metrics (4-6 weeks)

1. **Start with Tier 1 metrics**
2. **Define in metrics layer**
3. **Create comprehensive tests**
4. **Document thoroughly**
5. **Get stakeholder approval**

### Phase 3: Parallel Run (4-8 weeks)

1. **Run metrics layer alongside existing dashboards**
2. **Compare results (should match 100%)**
3. **Fix discrepancies**
4. **Build confidence**

### Phase 4: Migration (8-12 weeks)

1. **Rebuild key dashboards using metrics layer**
2. **Train BI developers**
3. **Deprecate old definitions**
4. **Enforce metrics layer for new dashboards**

### Phase 5: Optimization (Ongoing)

1. **Monitor query performance**
2. **Add pre-aggregations for slow metrics**
3. **Refine metric definitions based on usage**
4. **Expand metric coverage**

---

## Success Metrics

Track these metrics to measure metrics layer adoption:

```yaml
# Track your metrics layer success
metrics_layer_kpis:
  adoption:
    - name: "Metrics coverage"
      target: "> 80% of dashboards use metrics layer"

    - name: "Metric reuse"
      target: "Average metric used in 5+ dashboards"

    - name: "Certification rate"
      target: "> 90% of metrics are certified"

  performance:
    - name: "Query latency (p95)"
      target: "< 5 seconds"

    - name: "Cache hit rate"
      target: "> 70%"

  quality:
    - name: "Metric consistency"
      target: "0 conflicting definitions"

    - name: "Test coverage"
      target: "> 90% of metrics have tests"

  governance:
    - name: "Documentation completeness"
      target: "100% of certified metrics documented"

    - name: "Ownership"
      target: "100% of metrics have assigned owners"
```

---

## Conclusion

The Metrics Layer pattern is essential for organizations that have:
- Multiple BI tools
- Inconsistent metric definitions
- Growing number of analysts and dashboards
- Need for governance and auditability

**Key Benefits**:
✓ Single source of truth for metrics
✓ Consistent definitions across tools
✓ Version control for business logic
✓ Faster dashboard development (reuse vs rebuild)
✓ Better governance and lineage

**Implementation Effort**:
- Small org (< 100 employees): 1-2 months
- Mid-size (100-1,000): 3-6 months
- Enterprise (1,000+): 6-12 months

**Tools Recommendation**:
- **Start with dbt Semantic Layer** if using dbt
- **Use Cube.js** for headless BI / embedded analytics
- **Build custom** only if very specific needs

The metrics layer is the foundation for data democratization and self-service analytics at scale.

---

## References

1. dbt Semantic Layer Documentation: https://docs.getdbt.com/docs/use-dbt-semantic-layer
2. Cube.js Documentation: https://cube.dev/docs
3. Transform (Metrics Store): https://transform.co
4. Airbnb Minerva Architecture: https://medium.com/airbnb-engineering
5. Uber uMetric: https://eng.uber.com/umetric/
6. "The Rise of the Semantic Layer" (Benn Stancil, Mode Analytics)
7. MetricFlow (acquired by dbt Labs): https://github.com/transform-data/metricflow
