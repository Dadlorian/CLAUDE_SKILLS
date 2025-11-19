# Data Warehouse Capacity Planning Guide

Quick reference for sizing, scaling, and capacity planning across cloud data warehouse platforms.

## Storage Capacity Planning

### Data Growth Estimation

**Historical Growth Analysis**:
```sql
-- Snowflake storage growth tracking
SELECT
    DATE_TRUNC('month', usage_date) as month,
    SUM(average_stage_bytes) / POW(1024, 3) as stage_gb,
    SUM(average_database_bytes) / POW(1024, 3) as database_gb,
    SUM(average_failsafe_bytes) / POW(1024, 3) as failsafe_gb
FROM snowflake.account_usage.storage_usage
WHERE usage_date >= DATEADD(year, -1, CURRENT_DATE())
GROUP BY DATE_TRUNC('month', usage_date)
ORDER BY month;

-- Calculate month-over-month growth
WITH monthly_storage AS (
    SELECT
        DATE_TRUNC('month', usage_date) as month,
        AVG(database_bytes) / POW(1024, 4) as storage_tb
    FROM snowflake.account_usage.storage_usage
    GROUP BY DATE_TRUNC('month', usage_date)
)
SELECT
    month,
    storage_tb,
    LAG(storage_tb) OVER (ORDER BY month) as prev_month_tb,
    storage_tb - LAG(storage_tb) OVER (ORDER BY month) as growth_tb,
    ROUND(100 * (storage_tb - LAG(storage_tb) OVER (ORDER BY month)) /
          NULLIF(LAG(storage_tb) OVER (ORDER BY month), 0), 2) as growth_pct
FROM monthly_storage
ORDER BY month;
```

**Projection Formula**:
```
Future Storage = Current Storage × (1 + Monthly Growth Rate) ^ Months

Example:
Current: 10 TB
Growth: 5% per month
12-month projection: 10 × (1.05)^12 = 17.96 TB

Conservative estimate: Add 20% buffer = 21.55 TB
```

### Storage Cost Estimation

**Snowflake**:
```
Active storage: $23-40 per TB/month (varies by region/cloud)
Time Travel: Included (1-90 days based on edition)
Fail-safe: Included (7 days)

Example:
20 TB active storage × $30/TB = $600/month
```

**BigQuery**:
```
Active storage: $20 per TB/month
Long-term (90+ days unchanged): $10 per TB/month

Example:
15 TB active × $20 = $300/month
5 TB long-term × $10 = $50/month
Total: $350/month
```

**Redshift**:
```
RA3 managed storage: $24 per TB/month

Example:
20 TB × $24 = $480/month
```

## Compute Capacity Planning

### User Concurrency Analysis

```sql
-- Peak concurrency tracking (Snowflake)
SELECT
    DATE_TRUNC('hour', start_time) as hour,
    warehouse_name,
    COUNT(DISTINCT query_id) as query_count,
    COUNT(DISTINCT user_name) as concurrent_users
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(day, -7, CURRENT_DATE())
GROUP BY DATE_TRUNC('hour', start_time), warehouse_name
ORDER BY concurrent_users DESC
LIMIT 100;

-- Identify peak usage periods
WITH hourly_usage AS (
    SELECT
        DATE_TRUNC('hour', start_time) as hour,
        warehouse_name,
        COUNT(*) as query_count
    FROM snowflake.account_usage.query_history
    WHERE start_time >= DATEADD(day, -30, CURRENT_DATE())
    GROUP BY 1, 2
)
SELECT
    EXTRACT(HOUR FROM hour) as hour_of_day,
    warehouse_name,
    AVG(query_count) as avg_queries,
    MAX(query_count) as peak_queries
FROM hourly_usage
GROUP BY 1, 2
ORDER BY 1, 2;
```

### Warehouse Sizing

**Snowflake Warehouse Sizing**:
```
Warehouse Size | Credits/Hour | Use Case
---------------|--------------|----------------------------------
X-Small        | 1            | Small queries, low concurrency
Small          | 2            | Development, testing
Medium         | 4            | Production BI, < 50 concurrent users
Large          | 8            | Heavy ETL, 50-100 concurrent users
X-Large        | 16           | Large ETL, 100-200 concurrent users
2X-Large       | 32           | Very large ETL, 200-400 concurrent users
3X-Large       | 64           | Massive ETL, 400-800 concurrent users
4X-Large       | 128          | Extreme workloads

Sizing Guidelines:
- Scale UP for: Slow individual queries, complex joins
- Scale OUT (multi-cluster): High concurrency

Multi-Cluster Warehouses:
- Min clusters: 1-2
- Max clusters: Based on peak concurrency
- Scaling policy: ECONOMY (cost) or STANDARD (performance)
```

**BigQuery Slot Estimation**:
```
On-Demand: Automatic (up to 2,000 slots burst)
Flat-Rate: Purchase in increments of 100 slots

Slot Calculation:
Slots needed = (Query duration in seconds × Number of concurrent queries) / Time window

Example:
Average query: 10 seconds
Peak concurrency: 50 queries
Slots needed = (10 × 50) / 10 = 50 slots minimum
Recommended: 100 slots (for buffer and burst)

Cost:
100 slots = $2,000/month (US multi-region)
```

**Redshift Node Sizing**:
```
Node Type      | vCPU | RAM   | Storage | Price/hour (on-demand)
---------------|------|-------|---------|------------------------
dc2.large      | 2    | 15 GB | 160 GB  | $0.25
dc2.8xlarge    | 32   | 244 GB| 2.56 TB | $4.80
ra3.xlplus     | 4    | 32 GB | Managed | $1.086
ra3.4xlarge    | 12   | 96 GB | Managed | $3.26
ra3.16xlarge   | 48   | 384 GB| Managed | $13.04

Cluster Sizing:
- Start with 2 nodes minimum (redundancy)
- Add nodes for: More storage, higher concurrency, faster queries
- Leader node: Free (handles query planning)

Example Small Cluster:
2 × ra3.4xlarge = $6.52/hour × 8 hours/day × 22 days = $1,147/month

Example Large Cluster:
10 × ra3.4xlarge = $32.60/hour × 24 hours × 30 days = $23,472/month
Reserved (3-year): ~$7,000/month (70% savings)
```

## Workload Profiling

### Query Patterns

```sql
-- Classify queries by duration (Snowflake)
SELECT
    CASE
        WHEN total_elapsed_time < 1000 THEN '< 1 second'
        WHEN total_elapsed_time < 10000 THEN '1-10 seconds'
        WHEN total_elapsed_time < 60000 THEN '10-60 seconds'
        WHEN total_elapsed_time < 300000 THEN '1-5 minutes'
        ELSE '> 5 minutes'
    END as duration_bucket,
    COUNT(*) as query_count,
    ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as pct_of_total
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(day, -7, CURRENT_DATE())
  AND execution_status = 'SUCCESS'
GROUP BY 1
ORDER BY MIN(total_elapsed_time);

-- Data scanned analysis (BigQuery)
SELECT
    CASE
        WHEN total_bytes_processed < POW(1024, 3) THEN '< 1 GB'
        WHEN total_bytes_processed < 10 * POW(1024, 3) THEN '1-10 GB'
        WHEN total_bytes_processed < 100 * POW(1024, 3) THEN '10-100 GB'
        WHEN total_bytes_processed < POW(1024, 4) THEN '100 GB - 1 TB'
        ELSE '> 1 TB'
    END as data_scanned_bucket,
    COUNT(*) as query_count,
    SUM(total_bytes_processed) / POW(1024, 4) as total_tb_processed,
    SUM(total_bytes_processed) / POW(1024, 4) * 5 as estimated_cost_usd
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE DATE(creation_time) >= CURRENT_DATE() - 30
GROUP BY 1
ORDER BY total_tb_processed DESC;
```

### ETL vs BI Workload Split

```sql
-- Identify ETL vs BI queries
SELECT
    warehouse_name,
    CASE
        WHEN warehouse_name LIKE '%etl%' THEN 'ETL'
        WHEN warehouse_name LIKE '%bi%' THEN 'BI'
        WHEN warehouse_name LIKE '%adhoc%' THEN 'Ad-hoc'
        ELSE 'Other'
    END as workload_type,
    COUNT(*) as query_count,
    SUM(credits_used) as total_credits,
    AVG(total_elapsed_time) / 1000 as avg_duration_seconds,
    SUM(bytes_scanned) / POW(1024, 4) as tb_scanned
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(day, -30, CURRENT_DATE())
GROUP BY 1, 2
ORDER BY total_credits DESC;
```

## Performance Benchmarking

### Baseline Metrics

**Query Performance**:
```
Target P50 (median): < 3 seconds
Target P95: < 30 seconds
Target P99: < 60 seconds

Measure:
- Query compilation time
- Queue wait time
- Execution time
- Network transfer time
```

**Concurrency**:
```
Maximum concurrent queries: 50-100 per warehouse
Average queries per second: 5-20
Peak hour multiplier: 2-3x average
```

**Data Freshness**:
```
Batch ETL: Nightly (< 8 hours old)
Real-time: < 15 minutes
Streaming: < 1 minute
```

### Load Testing

```sql
-- Simulate concurrent queries
-- Run multiple instances of typical queries

-- Typical BI query
SELECT
    customer_id,
    COUNT(*) as order_count,
    SUM(amount) as total_amount
FROM orders
WHERE order_date >= DATEADD(month, -3, CURRENT_DATE())
GROUP BY customer_id
ORDER BY total_amount DESC
LIMIT 1000;

-- Typical ETL query
INSERT INTO fact_orders
SELECT
    o.order_id,
    o.customer_id,
    o.product_id,
    o.order_date,
    o.amount,
    o.quantity,
    CURRENT_TIMESTAMP() as etl_timestamp
FROM staging.orders o
WHERE o.order_date >= DATEADD(day, -1, CURRENT_DATE());
```

## Scaling Strategies

### Vertical Scaling (Scale Up)

**When to scale up**:
- Individual queries are slow
- Complex joins/aggregations
- Large data scans
- Heavy transformations

**Snowflake example**:
```sql
-- Increase warehouse size
ALTER WAREHOUSE analytics_wh SET WAREHOUSE_SIZE = 'X-LARGE';

-- Impact: 2x size = 2x speed (approximately)
-- Medium (4 credits/hour) → X-Large (16 credits/hour)
-- Query time: 60 seconds → 15 seconds
-- Cost efficiency: Same or better (4x faster for 4x cost)
```

### Horizontal Scaling (Scale Out)

**When to scale out**:
- High query concurrency
- Many simultaneous users
- Queue wait times increasing

**Snowflake multi-cluster example**:
```sql
ALTER WAREHOUSE bi_wh SET
    MIN_CLUSTER_COUNT = 1,
    MAX_CLUSTER_COUNT = 5,
    SCALING_POLICY = 'ECONOMY';

-- Automatically adds clusters when:
-- - Query queuing occurs
-- - Current clusters at capacity
-- - Scaling policy threshold met

-- ECONOMY: More conservative (lower cost)
-- STANDARD: More aggressive (better performance)
```

**BigQuery autoscaling**:
```
Automatically handled by Google
On-demand: Up to 2,000 slots burst
Flat-rate: Can purchase additional slots on-demand
```

### Auto-Scaling Configuration

**Snowflake**:
```sql
-- Development warehouse (aggressive suspend)
CREATE WAREHOUSE dev_wh WITH
    WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 60           -- 1 minute
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

-- Production BI (moderate suspend)
CREATE WAREHOUSE bi_wh WITH
    WAREHOUSE_SIZE = 'MEDIUM'
    AUTO_SUSPEND = 300          -- 5 minutes
    AUTO_RESUME = TRUE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 3
    SCALING_POLICY = 'ECONOMY';

-- ETL warehouse (minimal suspend, large size)
CREATE WAREHOUSE etl_wh WITH
    WAREHOUSE_SIZE = 'X-LARGE'
    AUTO_SUSPEND = 600          -- 10 minutes
    AUTO_RESUME = TRUE;
```

## Capacity Monitoring

### Key Metrics to Track

**Storage Metrics**:
```sql
-- Snowflake storage by schema
SELECT
    table_schema,
    SUM(bytes) / POW(1024, 3) as storage_gb,
    SUM(row_count) as total_rows
FROM snowflake.account_usage.table_storage_metrics
WHERE catalog_name = CURRENT_DATABASE()
GROUP BY table_schema
ORDER BY storage_gb DESC;

-- Table growth rate
WITH daily_storage AS (
    SELECT
        table_name,
        DATE_TRUNC('day', creation_time) as day,
        active_bytes / POW(1024, 3) as size_gb
    FROM snowflake.account_usage.table_storage_metrics
    WHERE table_schema = 'PUBLIC'
)
SELECT
    table_name,
    MAX(size_gb) as current_size_gb,
    AVG(size_gb - LAG(size_gb) OVER (PARTITION BY table_name ORDER BY day))
        as avg_daily_growth_gb
FROM daily_storage
GROUP BY table_name
ORDER BY avg_daily_growth_gb DESC NULLS LAST;
```

**Compute Metrics**:
```sql
-- Warehouse utilization
SELECT
    warehouse_name,
    DATE(start_time) as date,
    SUM(credits_used) as daily_credits,
    COUNT(DISTINCT query_id) as query_count,
    AVG(total_elapsed_time) / 1000 as avg_query_seconds
FROM snowflake.account_usage.warehouse_metering_history
WHERE start_time >= DATEADD(day, -30, CURRENT_DATE())
GROUP BY warehouse_name, DATE(start_time)
ORDER BY date DESC, daily_credits DESC;

-- Cost per query
SELECT
    warehouse_name,
    COUNT(*) as query_count,
    SUM(credits_used) as total_credits,
    SUM(credits_used) / COUNT(*) as credits_per_query,
    SUM(credits_used) * 2.50 / COUNT(*) as cost_per_query_usd
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(day, -7, CURRENT_DATE())
  AND credits_used > 0
GROUP BY warehouse_name
ORDER BY cost_per_query_usd DESC;
```

## Capacity Planning Worksheet

### Current State Assessment
```
Storage:
- Current total: _____ TB
- Monthly growth: _____ %
- 12-month projection: _____ TB
- Storage cost projection: $ _____/month

Compute:
- Active users: _____
- Peak concurrency: _____ queries
- Average query duration: _____ seconds
- Daily query volume: _____
- Compute cost: $ _____/month

Total Monthly Cost: $ _____
```

### Future State Planning
```
Expected Growth:
- User growth: _____ % (next 12 months)
- Data growth: _____ % (next 12 months)
- Query growth: _____ % (next 12 months)

Scaling Plan:
- Storage increase: From _____ TB to _____ TB
- Warehouse size: From _____ to _____
- Max clusters: From _____ to _____

Projected Cost (12 months):
- Storage: $ _____/month
- Compute: $ _____/month
- Total: $ _____/month
- Budget: $ _____/month
- Variance: $ _____/month (_____ %)
```

## Optimization Recommendations

### Storage Optimization
- [ ] Drop unused tables and views
- [ ] Implement data retention policies
- [ ] Partition large tables by date
- [ ] Compress data efficiently
- [ ] Archive historical data to object storage

### Compute Optimization
- [ ] Right-size warehouses (not too large)
- [ ] Enable auto-suspend (60-300 seconds)
- [ ] Use multi-cluster for concurrency
- [ ] Separate ETL and BI workloads
- [ ] Optimize slow queries
- [ ] Implement result caching
- [ ] Use materialized views

### Cost Optimization
- [ ] Monitor daily spend
- [ ] Set up cost alerts
- [ ] Review top cost queries
- [ ] Evaluate reserved capacity
- [ ] Implement chargeback by department
- [ ] Regular quarterly cost reviews

## Emergency Scaling

### Rapid Scale-Up Procedure
```sql
-- Immediate performance boost
ALTER WAREHOUSE critical_wh SET WAREHOUSE_SIZE = '4X-LARGE';
ALTER WAREHOUSE critical_wh SET MAX_CLUSTER_COUNT = 10;

-- Add dedicated warehouse for critical workload
CREATE WAREHOUSE emergency_wh WITH
    WAREHOUSE_SIZE = 'X-LARGE'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;

-- Migrate critical queries
USE WAREHOUSE emergency_wh;
```

### Scale-Down After Peak
```sql
-- Return to normal sizing
ALTER WAREHOUSE critical_wh SET WAREHOUSE_SIZE = 'LARGE';
ALTER WAREHOUSE critical_wh SET MAX_CLUSTER_COUNT = 3;

-- Drop temporary warehouses
DROP WAREHOUSE emergency_wh;
```

## Capacity Planning Best Practices

1. **Monitor continuously**: Track storage, compute, costs daily
2. **Plan ahead**: Forecast 12-18 months out
3. **Test scaling**: Load test before production peaks
4. **Budget conservatively**: Add 20-30% buffer
5. **Review quarterly**: Adjust based on actual usage
6. **Optimize first**: Before scaling, optimize queries
7. **Document baselines**: Know your performance targets
8. **Automate alerts**: Get notified of capacity issues
