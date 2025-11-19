# BI Platform Performance Tuning Guide

## Performance Metrics Overview

### Key Performance Indicators
- **Query Response Time**: P50, P95, P99 percentiles
- **Dashboard Load Time**: Time to interactive (TTI)
- **Data Refresh Duration**: Extract/ETL completion time
- **Concurrent Users**: Maximum supported simultaneous users
- **Cache Hit Rate**: Percentage of queries served from cache
- **Resource Utilization**: CPU, memory, disk I/O

### Performance Targets
| Metric | Target | Good | Needs Improvement |
|--------|--------|------|-------------------|
| Dashboard Initial Load | < 3s | < 5s | > 5s |
| Query Response (Simple) | < 1s | < 2s | > 2s |
| Query Response (Complex) | < 5s | < 10s | > 10s |
| Extract Refresh (10M rows) | < 15min | < 30min | > 30min |
| Concurrent Users | 100+ | 50-100 | < 50 |

## Tableau Performance Optimization

### Extract Optimization
```sql
-- Materialized calculated fields in extract
-- Instead of calculating in Tableau, calculate in SQL
SELECT
    order_id,
    customer_id,
    order_date,
    -- Pre-calculate commonly used fields
    quantity * unit_price AS line_total,
    CASE
        WHEN quantity * unit_price > 1000 THEN 'High Value'
        WHEN quantity * unit_price > 100 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS order_tier,
    -- Pre-aggregate where possible
    DATE_TRUNC('month', order_date) AS order_month,
    DATE_TRUNC('week', order_date) AS order_week
FROM orders
WHERE order_date >= DATEADD(year, -2, CURRENT_DATE)
```

### Data Source Filters
```tableau
// Use data source filters (applied before data loads)
// Right-click data source → Edit Data Source Filters

// Context filters (higher priority than normal filters)
// Right-click filter → Add to Context

// Filtered extract definition
// Extract → Edit → Filters → Add
// Filter: Date >= TODAY() - 365
```

### Calculation Optimization
```tableau
// SLOW: Nested LOD with multiple calculations
{ FIXED [Customer] :
    SUM(
        { FIXED [Order] : SUM([Sales]) }
    ) / COUNTD([Order])
}

// FAST: Single LOD with direct calculation
{ FIXED [Customer] :
    SUM([Sales]) / COUNTD([Order])
}

// SLOW: String comparison in aggregation
SUM(IF [Category] = "Electronics" THEN [Sales] END)

// FAST: Use boolean field
// Create calculated field: Is Electronics = [Category] = "Electronics"
SUM([Sales (Electronics)])  // Created in data source

// Use ATTR() for single-value dimensions
ATTR([Customer Name])  // Instead of MIN([Customer Name])
```

### Dashboard Design for Performance
```
Best Practices:
1. Limit to 7±2 visualizations per dashboard
2. Use dashboard actions instead of filters when possible
3. Hide unused worksheets
4. Minimize use of parameters
5. Use fixed size layouts (not automatic)
6. Optimize image sizes
7. Reduce mark count (<10,000 per viz recommended)

// Sampling for large datasets
// Analysis → Table Layout → Show at Most (10,000 rows)

// Or use RAWSQLAGG for server-side aggregation
RAWSQLAGG_REAL("SELECT AVG(price) FROM products WHERE %1", [Category])
```

### Performance Recording Analysis
```
1. Help → Settings and Performance → Start Performance Recording
2. Interact with dashboard
3. Help → Settings and Performance → Stop Performance Recording

Key metrics to analyze:
- Computing Layouts: Dashboard design complexity
- Executing Query: Data source performance
- Geocoding: Map performance
- Blending Data: Cross-data source joins
- Server Rendering: Server-side image rendering

Optimization based on results:
- High "Executing Query": Optimize data source, use extracts
- High "Computing Layouts": Simplify dashboard, reduce marks
- High "Blending Data": Join in data source instead
```

## Power BI Performance Optimization

### Data Model Optimization
```dax
// Star schema preferred over snowflake
// Fact table with minimal columns
// Dimension tables denormalized

// Remove unnecessary columns in Power Query
Source = Sql.Database("server", "database"),
SelectColumns = Table.SelectColumns(
    Source,
    {"OrderID", "OrderDate", "CustomerID", "Amount"}  // Only needed columns
)

// Data types: Use smallest appropriate type
// Integer (whole number) instead of Decimal
// Date instead of DateTime if time not needed

// Disable auto date/time hierarchy if not needed
// File → Options → Data Load
// Uncheck "Auto date/time"
```

### DAX Performance
```dax
// Use variables for repeated calculations
// SLOW
Measure =
DIVIDE(
    CALCULATE(SUM(Sales[Amount]), Region[Name] = "West"),
    CALCULATE(SUM(Sales[Amount]), ALL(Region))
)

// FAST
Measure Optimized =
VAR WestSales = CALCULATE(SUM(Sales[Amount]), Region[Name] = "West")
VAR TotalSales = CALCULATE(SUM(Sales[Amount]), ALL(Region))
RETURN DIVIDE(WestSales, TotalSales)

// Avoid calculated columns for aggregates
// SLOW: Calculated column
Sales[TotalAmount] = Sales[Quantity] * Sales[Price]
// Then: SUM(Sales[TotalAmount])

// FAST: Calculate in measure
Total Sales = SUMX(Sales, Sales[Quantity] * Sales[Price])

// Or better: Push to Power Query
= Table.AddColumn(Source, "TotalAmount",
    each [Quantity] * [Price], type number)

// Use SELECTEDVALUE instead of IF(HASONEVALUE())
// SLOW
IF(HASONEVALUE(Product[Name]), VALUES(Product[Name]), "Multiple")

// FAST
SELECTEDVALUE(Product[Name], "Multiple")
```

### Aggregations
```dax
// Define aggregation table in model
// Detail table: Sales (millions of rows)
// Agg table: Sales_Monthly (thousands of rows)

// Power BI auto-uses aggregation when possible
// Configure via: Manage Aggregations

// Aggregation table example
Sales_Monthly =
SUMMARIZE(
    Sales,
    'Date'[Year],
    'Date'[Month],
    Product[Category],
    "Total_Sales", SUM(Sales[Amount]),
    "Total_Quantity", SUM(Sales[Quantity]),
    "Order_Count", COUNTROWS(Sales)
)
```

### Query Folding
```powerquery
// Ensure operations "fold" to database
// Check: Right-click step → View Native Query

// Operations that fold:
Source = Sql.Database("server", "db"),
Filter = Table.SelectRows(Source, each [Date] >= #date(2024,1,1)),
Select = Table.SelectColumns(Filter, {"ID", "Amount", "Date"}),
Group = Table.Group(Select, {"Date"}, {{"Total", each List.Sum([Amount])}})

// Operations that don't fold (avoid if possible):
// - Table.AddColumn with complex functions
// - Merging with local tables
// - Unpivoting
// - Text operations (except basic)

// Push transformations to source when possible
= Sql.Database("server", "db", [Query="
    SELECT
        Date,
        SUM(Amount) AS Total
    FROM Sales
    WHERE Date >= '2024-01-01'
    GROUP BY Date
"])
```

### DirectQuery Optimization
```dax
// Reduce visuals per page (3-5 for DirectQuery)
// Minimize use of complex DAX in DirectQuery
// Use composite model for best of both:

// Composite model pattern:
// - Import: Dimension tables (small, static)
// - DirectQuery: Fact tables (large, real-time)
// - Aggregations: Pre-aggregated fact tables (import)

// Dual storage mode
// Table properties → Storage mode → Dual
// Auto switches between Import/DirectQuery based on query
```

### Performance Analyzer
```
// Built-in performance tool
View → Performance Analyzer → Start Recording

// Analyze results:
1. DAX query duration
2. Visual display duration
3. Other (overhead)

// Common fixes:
// Long DAX query: Optimize measure logic, use variables
// Long display: Reduce visual complexity, limit data points
// Long other: Too many visuals, dashboard design issue
```

## Looker Performance Optimization

### Persistent Derived Tables (PDTs)
```lookml
view: daily_orders_summary {
  derived_table: {
    sql:
      SELECT
        DATE(created_at) AS order_date,
        customer_id,
        COUNT(*) AS order_count,
        SUM(total_amount) AS total_revenue,
        AVG(total_amount) AS avg_order_value
      FROM orders
      GROUP BY 1, 2 ;;

    # Rebuild strategy
    sql_trigger_value: SELECT DATE(CONVERT_TZ(NOW(), 'UTC', 'America/Los_Angeles')) ;;

    # Performance optimization
    indexes: ["order_date", "customer_id"]
    distribution: "customer_id"  # For Redshift/BigQuery
    partition_keys: ["order_date"]  # For BigQuery
  }

  # Use indexed fields in joins
  dimension: order_date {
    type: date
    sql: ${TABLE}.order_date ;;
  }

  dimension: customer_id {
    type: number
    sql: ${TABLE}.customer_id ;;
  }
}
```

### Aggregate Awareness
```lookml
explore: orders {
  # Define aggregate table
  aggregate_table: daily_rollup {
    query: {
      dimensions: [created_date, customer_id]
      measures: [count, total_amount]
    }

    materialization: {
      datagroup_trigger: daily_datagroup
    }
  }

  # Looker automatically uses aggregate when appropriate
}
```

### Query Optimization
```lookml
# Symmetric aggregates for better caching
measure: total_sales {
  type: sum
  sql: ${TABLE}.amount ;;
  # More cache-friendly than:
  # sql: ${TABLE}.quantity * ${TABLE}.price ;;
}

# Use datagroups for coordinated caching
datagroup: nightly_refresh {
  sql_trigger: SELECT MAX(id) FROM etl_log WHERE completed = 1 ;;
  max_cache_age: "24 hours"
}

# Apply to explores
explore: orders {
  persist_with: nightly_refresh
}

# Optimize field picker
dimension: internal_id {
  type: number
  sql: ${TABLE}.id ;;
  hidden: yes  # Don't show in field picker
}

# Use extends to reduce code and improve performance
view: base_orders {
  sql_table_name: public.orders ;;
  # Common dimensions
}

view: orders {
  extends: [base_orders]
  # Additional specific dimensions
}
```

## Qlik Sense Performance Optimization

### QVD Layering
```qlik
// 1. Extract QVD (raw data from source)
Orders_Extract:
LOAD *
FROM [database]
STORE Orders_Extract INTO [lib://QVD/Extract/Orders.qvd] (qvd);

// 2. Transform QVD (cleaned, transformed)
Orders_Transform:
LOAD
    OrderID,
    Date(OrderDate) AS OrderDate,
    CustomerID,
    ProductID,
    Quantity * UnitPrice AS TotalAmount,
    // Pre-calculate common expressions
    Year(OrderDate) AS Year,
    Month(OrderDate) AS Month
FROM [lib://QVD/Extract/Orders.qvd] (qvd)
WHERE OrderDate >= AddYears(Today(), -2);

STORE Orders_Transform INTO [lib://QVD/Transform/Orders.qvd] (qvd);

// 3. Load QVD in app (fast load)
Orders:
LOAD * FROM [lib://QVD/Transform/Orders.qvd] (qvd);
```

### Optimized Load Script
```qlik
// Qualify field names to avoid synthetic keys
QUALIFY *;
UNQUALIFY OrderID, CustomerID, ProductID;  // Keep keys unqualified

// Use EXISTS for conditional loading
Orders:
LOAD
    OrderID,
    CustomerID,
    OrderDate
FROM [source]
WHERE EXISTS(CustomerID);  // Only customers already loaded

// Optimize joins
// SLOW: Multiple left joins
LEFT JOIN (Orders)
LOAD CustomerID, CustomerName FROM Customers;
LEFT JOIN (Orders)
LOAD ProductID, ProductName FROM Products;

// FAST: Use mapping or appropriate join
CustomerMap:
MAPPING LOAD CustomerID, CustomerName FROM Customers;

Orders:
LOAD
    OrderID,
    OrderDate,
    ApplyMap('CustomerMap', CustomerID, 'Unknown') AS CustomerName
FROM [source];

// Buffer for repeated loads of same source
Buffer (incremental) LOAD * FROM [source];
```

### Set Analysis Optimization
```qlik
// Use set analysis instead of IF in aggregations
// SLOW
Sum(If(Year = 2024, Sales))

// FAST
Sum({<Year={2024}>} Sales)

// Cache set analysis in variables
// Variable: vCurrentYear = Max(Year)
// Variable: vPriorYear = $(vCurrentYear) - 1

// Use in expressions
Sum({<Year={"$(vCurrentYear)"}>} Sales)
```

### Chart Performance
```qlik
// Limit calculation in charts
// Enable "Calculate on Server" for complex expressions

// Use master items (calculated once, reused)
// Master measure: Total Sales = Sum(Sales)

// Avoid:
// - Too many dimensions (>3)
// - Too many expressions (>5)
// - Deeply nested IF statements

// Use aggr() wisely (creates temporary table)
// SLOW: Nested aggr
Sum(Aggr(Sum(Aggr(Sum(Sales), Customer)), Region))

// FAST: Simplify
Sum(Total <Region, Customer> Sales)
```

## Superset Performance Optimization

### Database Configuration
```python
# superset_config.py

# Query timeout
SUPERSET_WEBSERVER_TIMEOUT = 60

# SQL Lab async query execution
SQLLAB_ASYNC_TIME_LIMIT_SEC = 300
SQLLAB_TIMEOUT = 300

# Results backend (for async queries)
from cachelib.redis import RedisCache
RESULTS_BACKEND = RedisCache(
    host='localhost',
    port=6379,
    key_prefix='superset_results'
)

# Cache configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,  # 1 day
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 1
}

# Database connection pool
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 20
}
```

### Query Optimization
```sql
-- Create materialized views for common queries
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT
    DATE(order_date) AS sale_date,
    product_category,
    COUNT(*) AS order_count,
    SUM(amount) AS total_sales,
    AVG(amount) AS avg_order_value
FROM orders
GROUP BY 1, 2;

-- Create indexes
CREATE INDEX idx_sales_date ON mv_daily_sales(sale_date);
CREATE INDEX idx_sales_category ON mv_daily_sales(product_category);

-- Refresh strategy
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales;
```

### Virtual Datasets
```sql
-- Define reusable SQL in virtual dataset
SELECT
    o.order_id,
    o.order_date,
    c.customer_name,
    c.customer_segment,
    p.product_name,
    p.category,
    o.quantity * o.unit_price AS line_total,
    -- Pre-calculate common metrics
    CASE
        WHEN o.quantity * o.unit_price > 1000 THEN 'High'
        WHEN o.quantity * o.unit_price > 100 THEN 'Medium'
        ELSE 'Low'
    END AS value_tier
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN products p ON o.product_id = p.id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '2 years'
```

### Chart-Level Caching
```python
# Enable chart caching in UI
# Chart → Edit → Advanced → Cache Timeout: 3600 (seconds)

# Or in chart JSON metadata
{
    "cache_timeout": 3600,
    "force": false  # Don't force refresh
}
```

## General Performance Best Practices

### Data Architecture
1. **Star Schema**: Fact table + dimension tables
2. **Incremental Loads**: Only load changed data
3. **Partitioning**: Date-based partitions for large tables
4. **Indexing**: On filter columns and join keys
5. **Compression**: Use columnar formats (Parquet, ORC)
6. **Archival**: Move old data to cheaper storage

### Dashboard Design
1. **Lazy Loading**: Load secondary tabs on demand
2. **Pagination**: Limit initial row count
3. **Sampling**: For exploratory analysis on large datasets
4. **Progressive Disclosure**: Summary → Detail on demand
5. **Minimize Filters**: Each filter = additional query
6. **Smart Defaults**: Reasonable date ranges

### Caching Strategy
```
L1: Query Result Cache (minutes to hours)
    - Exact query match
    - Short TTL for frequently changing data

L2: Extract/PDT/Aggregate Cache (hours to days)
    - Pre-aggregated data
    - Scheduled refresh

L3: Warm Cache (pre-computed)
    - Run queries before business hours
    - Cache popular dashboards
```

### Monitoring
```python
# Example monitoring script
import time
import requests

def monitor_dashboard_performance(dashboard_url, threshold_seconds=5):
    """Monitor dashboard load time"""
    start = time.time()
    response = requests.get(dashboard_url)
    duration = time.time() - start

    if duration > threshold_seconds:
        send_alert(f"Dashboard slow: {duration}s")

    log_metric('dashboard_load_time', duration, {
        'url': dashboard_url,
        'status': response.status_code
    })

    return duration
```

## Platform-Specific Bottleneck Identification

| Platform | Tool | Key Metrics |
|----------|------|-------------|
| Tableau | Performance Recorder | Query time, layout computation, rendering |
| Power BI | Performance Analyzer | DAX query, visual display, other |
| Looker | Query History | SQL execution time, cache hits |
| Qlik | Operations Monitor | RAM usage, CPU, response times |
| Superset | Slow Query Log | SQL execution, cache performance |

## Quick Wins Checklist

- [ ] Use extracts/aggregations for large datasets
- [ ] Remove unnecessary columns from data model
- [ ] Optimize join relationships (star schema)
- [ ] Enable query result caching
- [ ] Limit dashboard visuals (7±2 rule)
- [ ] Use incremental data refreshes
- [ ] Add indexes to filter columns
- [ ] Pre-calculate common metrics
- [ ] Implement data retention policies
- [ ] Monitor and alert on slow queries
