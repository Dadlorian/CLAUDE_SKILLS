# BigQuery Optimization Guide

Comprehensive reference for optimizing BigQuery performance, cost, and query efficiency.

## Table Design Optimization

### Partitioning

#### Time-Based Partitioning
```sql
-- Partition by ingestion time
CREATE TABLE events (
    event_id STRING,
    event_data STRING,
    created_at TIMESTAMP
)
PARTITION BY _PARTITIONDATE;

-- Partition by DATE column
CREATE TABLE orders (
    order_id STRING,
    customer_id STRING,
    order_date DATE
)
PARTITION BY order_date;

-- Partition by TIMESTAMP (day granularity)
CREATE TABLE logs (
    log_id STRING,
    message STRING,
    timestamp TIMESTAMP
)
PARTITION BY DATE(timestamp);

-- Partition by TIMESTAMP (hour granularity)
CREATE TABLE events_hourly (
    event_id STRING,
    event_timestamp TIMESTAMP
)
PARTITION BY TIMESTAMP_TRUNC(event_timestamp, HOUR);
```

#### Integer Range Partitioning
```sql
-- Partition by integer range
CREATE TABLE customers (
    customer_id INT64,
    customer_name STRING,
    country STRING
)
PARTITION BY RANGE_BUCKET(customer_id, GENERATE_ARRAY(0, 1000000, 10000));
```

#### Partition Expiration
```sql
-- Set partition expiration (90 days)
CREATE TABLE logs (
    log_id STRING,
    message STRING,
    timestamp TIMESTAMP
)
PARTITION BY DATE(timestamp)
OPTIONS(
    partition_expiration_days=90
);

-- Require partition filter
ALTER TABLE logs
SET OPTIONS(require_partition_filter=true);
```

### Clustering

```sql
-- Single column clustering
CREATE TABLE events (
    event_id STRING,
    user_id STRING,
    event_type STRING,
    event_date DATE
)
PARTITION BY event_date
CLUSTER BY user_id;

-- Multi-column clustering (order matters!)
CREATE TABLE orders (
    order_id STRING,
    customer_id STRING,
    country STRING,
    order_date DATE
)
PARTITION BY order_date
CLUSTER BY country, customer_id;

-- Clustering best practices:
-- 1. Cluster by frequently filtered columns
-- 2. Cluster by high-cardinality columns first
-- 3. Up to 4 clustering columns recommended
-- 4. Order: high-cardinality to low-cardinality
```

## Query Optimization

### SELECT Optimization

```sql
-- ❌ BAD: SELECT *
SELECT * FROM large_table;

-- ✅ GOOD: Select specific columns
SELECT order_id, customer_id, total
FROM large_table;

-- ✅ GOOD: Use _PARTITIONTIME for ingestion-time partitioned tables
SELECT event_id, event_data
FROM events
WHERE _PARTITIONTIME >= TIMESTAMP('2024-01-01')
  AND _PARTITIONTIME < TIMESTAMP('2024-02-01');

-- ✅ GOOD: Filter on partitioned column
SELECT order_id, total
FROM orders
WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31';

-- ✅ GOOD: Filter on clustered columns
SELECT order_id, total
FROM orders
WHERE country = 'USA'
  AND customer_id = '12345';
```

### JOIN Optimization

```sql
-- Put larger table first (broadcast join optimization)
-- BigQuery optimizes automatically, but helps to understand

-- ✅ GOOD: Join on partitioned/clustered columns
SELECT
    o.order_id,
    c.customer_name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= '2024-01-01';

-- ✅ GOOD: Pre-filter before joining
SELECT
    o.order_id,
    c.customer_name
FROM (
    SELECT order_id, customer_id
    FROM orders
    WHERE order_date >= '2024-01-01'
) o
JOIN customers c ON o.customer_id = c.customer_id;

-- Use CROSS JOIN sparingly
-- Use ARRAY_AGG instead of multiple self-joins when possible
```

### Window Function Optimization

```sql
-- Window functions are optimized in BigQuery
-- But can be expensive on large datasets

-- ✅ GOOD: Filter before windowing
WITH filtered_data AS (
    SELECT user_id, event_timestamp, event_type
    FROM events
    WHERE event_date >= '2024-01-01'
)
SELECT
    user_id,
    event_type,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_timestamp) as event_num
FROM filtered_data;

-- ✅ GOOD: Use QUALIFY for window function filters
SELECT
    user_id,
    event_type,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_timestamp) as rn
FROM events
WHERE event_date >= '2024-01-01'
QUALIFY rn = 1;  -- Get first event per user
```

### GROUP BY Optimization

```sql
-- ✅ GOOD: Use APPROX_COUNT_DISTINCT for large datasets
SELECT
    country,
    APPROX_COUNT_DISTINCT(user_id) as unique_users
FROM events
GROUP BY country;

-- Exact count (more expensive)
SELECT
    country,
    COUNT(DISTINCT user_id) as unique_users
FROM events
GROUP BY country;

-- ✅ GOOD: Use HyperLogLog++ for count distinct
SELECT
    country,
    HLL_COUNT.MERGE(user_id_hll) as unique_users
FROM (
    SELECT country, HLL_COUNT.INIT(user_id) as user_id_hll
    FROM events
    GROUP BY country, user_id
)
GROUP BY country;
```

## Materialized Views

```sql
-- Create materialized view
CREATE MATERIALIZED VIEW `project.dataset.daily_summary`
PARTITION BY event_date
CLUSTER BY country
AS
SELECT
    DATE(event_timestamp) as event_date,
    country,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as unique_users
FROM `project.dataset.events`
GROUP BY event_date, country;

-- Materialized view best practices:
-- 1. Use for frequently queried aggregations
-- 2. Partition and cluster materialized views
-- 3. Keep queries simple (limited JOIN complexity)
-- 4. Monitor refresh costs

-- Query materialized view (automatic query rewrite)
SELECT event_date, SUM(event_count)
FROM `project.dataset.daily_summary`
WHERE event_date >= '2024-01-01'
GROUP BY event_date;
```

## BI Engine Optimization

```sql
-- Enable BI Engine (reservation-based)
-- In UI: Navigation > BI Engine > Create Reservation

-- Optimize for BI Engine:
-- 1. Use smaller, aggregated tables
-- 2. Partition and cluster tables
-- 3. Use materialized views
-- 4. Keep frequently queried data in scope

-- Check BI Engine usage
SELECT
    query,
    bi_engine_statistics.bi_engine_mode,
    bi_engine_statistics.bi_engine_reasons
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE bi_engine_statistics.bi_engine_mode IN ('FULL', 'PARTIAL')
ORDER BY creation_time DESC
LIMIT 100;
```

## Cost Optimization

### Storage Costs

```sql
-- Use table expiration
CREATE TABLE temp_table (...)
OPTIONS(
    expiration_timestamp=TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
);

-- Use partition expiration
ALTER TABLE logs
SET OPTIONS(partition_expiration_days=90);

-- Long-term storage (90+ days, cheaper)
-- Automatically applied to tables not modified for 90 days

-- Check table size
SELECT
    table_schema,
    table_name,
    ROUND(size_bytes/POW(10,9), 2) as size_gb,
    ROUND(size_bytes/POW(10,12), 2) as size_tb
FROM `project.dataset.__TABLES__`
ORDER BY size_bytes DESC;
```

### Query Costs

```sql
-- Check query costs
SELECT
    user_email,
    query,
    total_bytes_processed,
    ROUND(total_bytes_processed/POW(10,12), 2) as tb_processed,
    ROUND(total_bytes_processed/POW(10,12) * 5, 2) as estimated_cost_usd
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE DATE(creation_time) = CURRENT_DATE()
ORDER BY total_bytes_processed DESC
LIMIT 100;

-- On-demand pricing: $5 per TB processed (as of 2024)
-- Flat-rate pricing: Monthly commitment for slots

-- Use query dry run to estimate cost
-- In UI: More > Query Settings > Disable cache, check "Use cached results"
-- Via API: jobs.query with dryRun=true
```

### Cost-Saving Strategies

```sql
-- 1. Use clustered tables to reduce scan size
-- 2. Partition tables and filter on partition column
-- 3. Avoid SELECT * - select only needed columns
-- 4. Use materialized views for repeated aggregations
-- 5. Use APPROX functions when exact counts not needed
-- 6. Enable result caching
-- 7. Use streaming inserts judiciously (costs more)
-- 8. Consider flat-rate pricing for high query volume

-- Cost estimation query
SELECT
    5 * (SUM(size_bytes)/POW(10,12)) as estimated_full_scan_cost_usd
FROM `project.dataset.__TABLES__`
WHERE table_name = 'large_table';
```

## Performance Monitoring

### Query Performance

```sql
-- Slowest queries today
SELECT
    user_email,
    query,
    total_slot_ms,
    total_bytes_processed,
    TIMESTAMP_DIFF(end_time, start_time, SECOND) as duration_seconds
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE DATE(creation_time) = CURRENT_DATE()
  AND state = 'DONE'
  AND error_result IS NULL
ORDER BY total_slot_ms DESC
LIMIT 20;

-- Most expensive queries (bytes processed)
SELECT
    query,
    COUNT(*) as execution_count,
    AVG(total_bytes_processed) as avg_bytes_processed,
    SUM(total_bytes_processed) as total_bytes_processed
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE DATE(creation_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY query
ORDER BY total_bytes_processed DESC
LIMIT 20;
```

### Table Statistics

```sql
-- Table usage statistics
SELECT
    table_schema,
    table_name,
    ROUND(size_bytes/POW(10,9), 2) as size_gb,
    row_count,
    TIMESTAMP_MILLIS(creation_time) as created,
    TIMESTAMP_MILLIS(last_modified_time) as last_modified
FROM `project.dataset.__TABLES__`
ORDER BY size_bytes DESC;

-- Partition information
SELECT
    table_name,
    partition_id,
    ROUND(total_rows/1000000, 2) as million_rows,
    ROUND(total_logical_bytes/POW(10,9), 2) as size_gb
FROM `project.dataset.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'partitioned_table'
ORDER BY partition_id DESC
LIMIT 100;
```

## Best Practices Summary

### Table Design
1. **Partition** tables > 1 GB, especially time-series data
2. **Cluster** tables on high-cardinality filter columns
3. Use **appropriate data types** (INT64 vs STRING for IDs)
4. Set **partition expiration** for temporary data
5. Use **nested and repeated fields** for denormalization

### Query Design
1. **SELECT specific columns**, never SELECT *
2. **Filter on partitioned columns** early
3. **Filter on clustered columns** when possible
4. Use **APPROX functions** for large aggregations
5. **Pre-filter** before JOINs and window functions
6. Use **QUALIFY** for window function filtering
7. Avoid **SELECT DISTINCT** on large datasets if possible

### Cost Management
1. Monitor query costs daily
2. Use **materialized views** for repeated aggregations
3. Enable **BI Engine** for BI tools
4. Consider **flat-rate pricing** for predictable workloads
5. Set up **custom cost controls** and alerts
6. Use **cached results** when appropriate
7. Archive old data to **Cloud Storage**

### Performance Monitoring
1. Review slowest queries weekly
2. Monitor slot utilization
3. Optimize high-cost queries
4. Track table growth
5. Monitor materialized view refresh costs

### Security & Governance
1. Use **column-level security** for sensitive data
2. Implement **row-level security** for multi-tenant data
3. Enable **audit logs** for compliance
4. Use **authorized views** for data access control
5. Implement **data classification** and **DLP**

## Common Anti-Patterns

❌ **Don't:**
- SELECT * on large tables
- Query without partition filters on partitioned tables
- Use self-JOINs when ARRAY_AGG would work
- Create too many small partitions (< 1 GB)
- Cluster on low-cardinality columns
- Stream inserts for batch data
- Use nested subqueries when CTEs are clearer

✅ **Do:**
- Select only needed columns
- Always filter partitioned tables
- Use ARRAY and STRUCT for denormalization
- Aim for 1+ GB partitions
- Cluster on frequently filtered columns
- Use batch loading for bulk data
- Use CTEs for readability and optimization
