# Performance Tuning Guide

## Quick Diagnostics

### Find Slow Queries
```sql
-- Snowflake: Slowest queries last 7 days
SELECT
  query_id,
  user_name,
  query_text,
  execution_time / 1000 as seconds,
  bytes_scanned / 1024 / 1024 / 1024 as gb_scanned
FROM TABLE(information_schema.query_history())
WHERE execution_status = 'SUCCESS'
  AND start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
  AND execution_time > 30000  -- > 30 seconds
ORDER BY execution_time DESC
LIMIT 20;
```

### Common Issues & Fixes

#### Issue 1: Full Table Scans
```sql
-- Problem Query
SELECT * FROM orders
WHERE YEAR(order_date) = 2025;

-- Optimized Query
SELECT * FROM orders
WHERE order_date >= '2025-01-01'
  AND order_date < '2026-01-01';
-- Enables partition pruning
```

#### Issue 2: Expensive Joins
```sql
-- Problem: Large Cartesian product
SELECT o.*, c.*
FROM orders o
CROSS JOIN customers c
WHERE o.customer_id = c.customer_id;

-- Fixed: Proper join
SELECT o.*, c.*
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;
```

#### Issue 3: Not Using Aggregates
```sql
-- Problem: Aggregating billions of rows
SELECT
  DATE(order_timestamp) as date,
  SUM(amount) as revenue
FROM orders
GROUP BY date;

-- Fixed: Query pre-aggregated table
SELECT
  date,
  revenue
FROM daily_revenue
WHERE date >= '2025-01-01';
```

## Optimization Techniques

### 1. Partitioning
```sql
-- Create partitioned table
CREATE TABLE orders_partitioned (
  order_id INT,
  order_date DATE,
  customer_id INT,
  amount DECIMAL
)
PARTITION BY DATE(order_date);

-- Queries automatically faster
SELECT * FROM orders_partitioned
WHERE order_date = '2025-01-15';
-- Only scans 1 day's partition
```

### 2. Clustering
```sql
-- Snowflake clustering
ALTER TABLE large_table
  CLUSTER BY (region, product_category);

-- Queries on these columns now faster
SELECT * FROM large_table
WHERE region = 'US'
  AND product_category = 'Software';
```

### 3. Materialized Views
```sql
-- Pre-compute expensive aggregation
CREATE MATERIALIZED VIEW daily_metrics AS
SELECT
  DATE(timestamp) as date,
  product_id,
  COUNT(*) as orders,
  SUM(amount) as revenue
FROM orders
GROUP BY 1, 2;

-- Refresh strategy
REFRESH MATERIALIZED VIEW daily_metrics;
```

### 4. Caching
```yaml
BI Tool Level:
  Looker:
    persist_for: "1 hour"

  Tableau:
    - Use extracts
    - Scheduled refresh

Database Level:
  - Result caching (automatic)
  - Requires exact query match
  - 24-hour TTL

Application Level:
  - Redis cache
  - TTL: 5-60 minutes
  - Invalidate on data changes
```

## Performance Targets

```yaml
Dashboard Load: <3 seconds
  - Above fold: <1 second
  - Full page: <3 seconds
  - Heavy drill-down: <10 seconds

Query Execution: <5 seconds
  - Simple aggregates: <1 second
  - Complex joins: <5 seconds
  - Large scans: <30 seconds

Data Freshness: <1 hour
  - Real-time: <5 minutes
  - Hourly: <15 minutes past hour
  - Daily: By 6am
```

## Quick Wins Checklist

```yaml
□ Add partition pruning to date filters
□ Create materialized views for dashboards
□ Enable result caching
□ Remove SELECT * queries
□ Add clustering to large tables
□ Pre-aggregate common metrics
□ Set query timeouts
□ Implement auto-suspend on warehouses
□ Use appropriate warehouse sizes
□ Monitor and kill runaway queries
```

## Monitoring Dashboard

```yaml
Key Metrics:
  - P50, P90, P99 query time
  - Queries >30 seconds
  - Cache hit rate
  - Data scanned per query
  - Cost per query
  - Failed queries

Alerts:
  - Query >5 minutes
  - User hitting timeout frequently
  - Cache hit rate <50%
  - Cost spike >2x average
```
