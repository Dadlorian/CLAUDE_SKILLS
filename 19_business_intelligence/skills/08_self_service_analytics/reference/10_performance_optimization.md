# Performance Optimization Reference

## Overview

Fast query performance is critical for self-service analytics adoption. Slow queries frustrate users and hinder data exploration. This reference provides comprehensive optimization strategies.

## Query Performance Targets

```yaml
User Experience Tiers:

Instant (<1 second):
  - Cached results
  - Pre-aggregated metrics
  - Simple lookups
  - User perception: "Fast and responsive"

Fast (1-5 seconds):
  - Most dashboard loads
  - Common analytical queries
  - Moderate complexity
  - User perception: "Acceptable"

Acceptable (5-30 seconds):
  - Complex analyses
  - Large data scans
  - Ad-hoc exploration
  - User perception: "Worth the wait"

Slow (30-120 seconds):
  - Very large datasets
  - Extensive computations
  - Batch operations
  - User perception: "Too slow for interactive use"

Unacceptable (>120 seconds):
  - Should be rare
  - Requires optimization
  - Consider pre-computation
  - User perception: "Broken"
```

## Database-Level Optimizations

### 1. Partitioning

```sql
-- Snowflake: Automatic micro-partitioning
CREATE TABLE orders (
  order_id INT,
  order_date DATE,
  customer_id INT,
  amount DECIMAL
)
CLUSTER BY (order_date);
-- Automatically maintains clustering

-- BigQuery: Partitioned table
CREATE TABLE orders
PARTITION BY DATE(order_date)
CLUSTER BY customer_id
AS SELECT * FROM source_orders;

-- Benefits:
-- - Partition pruning (scan only relevant partitions)
-- - Faster queries on date ranges
-- - Lower query costs

-- Query optimization:
SELECT *
FROM orders
WHERE order_date >= '2025-01-01'  -- Only scans Jan 2025+ partitions
  AND order_date < '2025-02-01';
```

### 2. Clustering/Indexing

```sql
-- Snowflake clustering
ALTER TABLE large_table CLUSTER BY (region, product_category);

-- Traditional indexes (PostgreSQL/MySQL)
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_compound ON orders(customer_id, order_date);

-- Covering index
CREATE INDEX idx_orders_covering ON orders(customer_id, order_date)
INCLUDE (order_amount);  -- Avoid table lookup

-- When to use:
-- - High-cardinality columns
-- - Frequently filtered columns
-- - Foreign key columns
-- - Sort columns
```

### 3. Materialized Views

```sql
-- Pre-compute expensive aggregations
CREATE MATERIALIZED VIEW daily_revenue AS
SELECT
  DATE(order_date) as date,
  SUM(amount) as total_revenue,
  COUNT(*) as order_count,
  COUNT(DISTINCT customer_id) as unique_customers
FROM orders
GROUP BY DATE(order_date);

-- Refresh strategy
REFRESH MATERIALIZED VIEW daily_revenue;  -- Manual

-- Auto-refresh (Snowflake)
CREATE MATERIALIZED VIEW daily_revenue
  AUTO_REFRESH = TRUE
  AS SELECT ...;

-- Benefits:
-- - Query pre-computed view (fast)
-- - No real-time computation needed
-- - Smaller data to scan

-- Use cases:
-- - Dashboard KPIs
-- - Daily/hourly aggregations
-- - Complex joins
-- - Slow-changing data
```

### 4. Pre-Aggregation Tables

```yaml
# dbt incremental model for daily aggregates
{{ config(
    materialized='incremental',
    unique_key='date'
) }}

SELECT
  DATE(order_timestamp) as date,
  product_category,
  SUM(order_amount) as total_revenue,
  COUNT(*) as order_count,
  AVG(order_amount) as avg_order_value
FROM {{ ref('orders') }}
{% if is_incremental() %}
  WHERE DATE(order_timestamp) > (SELECT MAX(date) FROM {{ this }})
{% endif %}
GROUP BY 1, 2

-- Query pre-aggregated table (fast):
SELECT * FROM daily_product_metrics
WHERE date >= '2025-01-01'

-- vs. raw aggregation (slow):
SELECT
  DATE(order_timestamp),
  product_category,
  SUM(order_amount)
FROM orders
WHERE order_timestamp >= '2025-01-01'
GROUP BY 1, 2
```

## Query-Level Optimizations

### 1. Efficient Filtering

```sql
-- Good: Filter early, scan less data
SELECT *
FROM orders
WHERE order_date >= '2025-01-01'  -- Partition pruning
  AND order_date < '2025-02-01'
  AND region = 'US'  -- Additional filters

-- Bad: Filter after scanning all data
SELECT *
FROM orders
WHERE YEAR(order_date) = 2025  -- Can't use partition pruning
  AND MONTH(order_date) = 1

-- Good: Use indexed columns
SELECT * FROM orders WHERE customer_id = 12345

-- Bad: Function on indexed column prevents index use
SELECT * FROM orders WHERE UPPER(customer_id) = '12345'
```

### 2. Efficient Joins

```sql
-- Good: Join on indexed columns, filter first
SELECT o.*, c.customer_name
FROM (
  SELECT *
  FROM orders
  WHERE order_date >= '2025-01-01'  -- Filter first
) o
JOIN customers c ON o.customer_id = c.customer_id

-- Bad: Large Cartesian product
SELECT o.*, c.*
FROM orders o
CROSS JOIN customers c
WHERE o.customer_id = c.customer_id  -- Filter after join

-- Good: Use appropriate join type
SELECT o.*, c.customer_name
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
-- Only include customers that have orders

-- Avoid fan-out: Use DISTINCT or aggregation carefully
SELECT DISTINCT o.order_id, o.order_date
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
-- DISTINCT prevents duplicate orders from multiple items
```

### 3. Efficient Aggregations

```sql
-- Good: Pre-filter, then aggregate
SELECT
  customer_id,
  COUNT(*) as order_count,
  SUM(amount) as total_amount
FROM orders
WHERE order_date >= '2025-01-01'  -- Filter first
GROUP BY customer_id

-- Good: Use appropriate aggregate functions
SELECT COUNT(*) FROM orders;  -- Fast
SELECT COUNT(DISTINCT customer_id) FROM orders;  -- Slower but necessary

-- Consider approximation for large datasets
SELECT APPROX_COUNT_DISTINCT(customer_id) FROM orders;  -- Much faster

-- Use window functions efficiently
SELECT
  order_id,
  customer_id,
  order_amount,
  SUM(order_amount) OVER (PARTITION BY customer_id) as customer_lifetime_value
FROM orders
-- Single scan vs. self-join
```

### 4. Limit Result Sets

```sql
-- Always use LIMIT for exploration
SELECT * FROM large_table LIMIT 100;

-- Use pagination for large results
SELECT *
FROM orders
ORDER BY order_id
LIMIT 1000 OFFSET 0;  -- First page

SELECT *
FROM orders
WHERE order_id > 1000  -- More efficient than OFFSET
ORDER BY order_id
LIMIT 1000;  -- Second page
```

## Caching Strategies

### 1. Query Result Caching

```yaml
BI Tool Caching (Looker example):
  persist_for: "1 hour"
  # Re-use results for 1 hour

  persist_for: "datagroup: daily_refresh"
  # Invalidate when datagroup refreshes

Database Result Caching:
  Snowflake:
    - Automatic result caching (24 hours)
    - Exact query match required
    - No data changes

  BigQuery:
    - Cached results (24 hours)
    - Requires exact match
    - No charge for cached results

Application Caching:
  Redis:
    - Cache dashboard results
    - TTL: 5-60 minutes
    - Key: hash(query + filters)
```

### 2. Semantic Layer Caching (Cube.js)

```javascript
cube('Orders', {
  // Pre-aggregations
  preAggregations: {
    main: {
      measures: [Orders.count, Orders.totalAmount],
      dimensions: [Orders.status, Orders.createdDate],
      timeDimension: Orders.createdDate,
      granularity: `day`,
      partitionGranularity: `month`,
      refreshKey: {
        every: `1 hour`,
      },
    },
  },

  measures: {
    count: {
      type: `count`,
    },
    totalAmount: {
      sql: `amount`,
      type: `sum`,
    },
  },
});
```

### 3. Dashboard Caching

```yaml
Strategies:

Scheduled Refresh:
  - Regenerate dashboards on schedule
  - Store results in cache
  - Serve cached version to users
  - Example: Refresh every hour at :00

On-Demand Refresh:
  - User can manually refresh
  - Cache updates immediately
  - Other users get old cache until refresh
  - Example: "Refresh" button

Smart Refresh:
  - Detect data updates
  - Refresh only when data changes
  - Minimal unnecessary refreshes
  - Example: dbt datagroups, data freshness checks

Multi-Tier Caching:
  - L1: In-memory cache (seconds)
  - L2: Redis cache (minutes)
  - L3: Database cache (hours)
  - Fallback: Re-compute query
```

## BI Tool Optimizations

### 1. Dashboard Design

```yaml
Best Practices:

Lazy Loading:
  - Load above-the-fold first
  - Defer off-screen charts
  - Progressive enhancement
  - User sees content faster

Limit Visuals:
  - 5-10 charts per dashboard
  - Avoid 20+ chart dashboards
  - Use tabs/pages for more
  - Each chart = separate query

Efficient Filters:
  - Apply filters before query
  - Use cascading filters
  - Default to reasonable ranges
  - Avoid "All time" defaults

Aggregation Level:
  - Show daily, not hourly by default
  - Drill down for detail
  - Start high-level
  - Users can zoom in

Data Limits:
  - Top 10/20/50, not all
  - Pagination for tables
  - Sampling for large datasets
  - Download for full export
```

### 2. Looker Optimizations

```lookml
# Persistent derived table
view: daily_orders {
  derived_table: {
    sql: SELECT
      DATE(order_timestamp) as date,
      COUNT(*) as order_count,
      SUM(amount) as total_revenue
    FROM orders
    GROUP BY 1 ;;

    datagroup_trigger: daily_refresh
    # Rebuilds when datagroup invalidated

    distribution_style: all
    # Redshift optimization

    partition_keys: ["date"]
    # BigQuery optimization
  }
}

# Aggregate awareness
view: orders {
  dimension: order_date {
    type: date
    sql: ${TABLE}.order_date ;;
  }

  measure: count {
    type: count
  }

  # Use aggregate table when possible
  aggregate_table: daily_rollup {
    query: {
      dimensions: [order_date]
      measures: [count]
      filters: [
        order_date: "7 days"
      ]
    }
    materialization: {
      datagroup_trigger: daily_refresh
    }
  }
}
```

### 3. Tableau Optimizations

```yaml
Extract vs. Live:
  Extract (TDE/Hyper):
    - Fast performance
    - In-memory processing
    - Scheduled refreshes
    - Good for: <10GB data, fast viz

  Live Connection:
    - Real-time data
    - Leverages database power
    - No data duplication
    - Good for: Large datasets, need freshness

Optimization Techniques:
  - Use data source filters
  - Aggregate data before extract
  - Hide unused fields
  - Use context filters
  - Materialize calculations
  - Optimize joins
  - Use data blending sparingly
```

## Monitoring & Troubleshooting

### 1. Query Performance Monitoring

```sql
-- Snowflake: Query history
SELECT
  query_id,
  query_text,
  user_name,
  execution_status,
  total_elapsed_time / 1000 as seconds,
  bytes_scanned / 1024 / 1024 / 1024 as gb_scanned,
  credits_used_cloud_services
FROM TABLE(information_schema.query_history())
WHERE execution_status = 'SUCCESS'
  AND total_elapsed_time > 10000  -- >10 seconds
ORDER BY total_elapsed_time DESC
LIMIT 100;

-- BigQuery: Query history
SELECT
  job_id,
  user_email,
  statement_type,
  total_bytes_processed / 1024 / 1024 / 1024 as gb_processed,
  total_slot_ms / 1000 / 60 as slot_minutes,
  total_bytes_billed / 1024 / 1024 / 1024 as gb_billed,
  creation_time,
  end_time,
  TIMESTAMP_DIFF(end_time, creation_time, SECOND) as duration_seconds
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_USER
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
  AND job_type = 'QUERY'
  AND state = 'DONE'
ORDER BY duration_seconds DESC
LIMIT 100;
```

### 2. Performance Dashboard

```yaml
Key Metrics:

Query Performance:
  - P50, P90, P99 latency
  - Queries > 30s
  - Failed queries
  - Timeout rate

Resource Usage:
  - Compute credits/slot-hours
  - Data scanned
  - Cache hit rate
  - Concurrent queries

User Experience:
  - Dashboard load times
  - User complaints
  - Abandonment rate
  - Refresh rates

Cost Efficiency:
  - Cost per query
  - Most expensive queries
  - Most expensive users
  - Optimization opportunities
```

### 3. Query Optimization Process

```yaml
1. Identify Slow Queries:
   - Monitor query logs
   - User complaints
   - Automated alerts
   - Regular audits

2. Analyze Query:
   - Use EXPLAIN PLAN
   - Check execution stats
   - Identify bottlenecks
   - Review data volumes

3. Optimize:
   - Add filters
   - Improve joins
   - Add indexes
   - Use pre-aggregations
   - Rewrite query

4. Test:
   - Compare performance
   - Validate results match
   - Check edge cases
   - Load test

5. Deploy:
   - Update queries/views
   - Document changes
   - Notify users
   - Monitor impact
```

## Cost Optimization

```yaml
Strategies:

Data Lifecycle:
  - Archive old data
  - Compress historical data
  - Delete unnecessary data
  - Use tiered storage

Query Optimization:
  - Reduce data scanned
  - Use partitioning
  - Implement caching
  - Limit result sets

Warehouse Sizing:
  - Right-size compute
  - Auto-suspend idle warehouses
  - Use multi-cluster warehouses
  - Separate workloads

Storage Optimization:
  - Remove duplicates
  - Drop unused tables
  - Compress data
  - Use appropriate data types

Monitoring:
  - Track costs by user
  - Alert on spikes
  - Identify waste
  - Regular optimization
```

## Best Practices Summary

```yaml
Database Layer:
  ✓ Partition large tables
  ✓ Cluster on common filters
  ✓ Create appropriate indexes
  ✓ Use materialized views
  ✓ Pre-aggregate common metrics

Query Layer:
  ✓ Filter early and often
  ✓ Use efficient joins
  ✓ Limit result sets
  ✓ Avoid SELECT *
  ✓ Use EXPLAIN to understand

Caching Layer:
  ✓ Implement multi-tier caching
  ✓ Cache expensive queries
  ✓ Smart cache invalidation
  ✓ Pre-compute common queries

BI Tool Layer:
  ✓ Design efficient dashboards
  ✓ Use extracts when appropriate
  ✓ Implement lazy loading
  ✓ Aggregate before visualizing

Monitoring:
  ✓ Track query performance
  ✓ Alert on slow queries
  ✓ Regular optimization
  ✓ Cost monitoring
```

## References

- Snowflake Performance Optimization Guide
- BigQuery Best Practices
- dbt Performance Tuning
- "The Data Warehouse Toolkit" - Ralph Kimball
- Looker Performance Best Practices
