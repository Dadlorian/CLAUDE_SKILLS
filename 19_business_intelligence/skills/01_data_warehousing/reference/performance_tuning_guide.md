# Data Warehouse Performance Tuning Guide

Quick reference for diagnosing and resolving common data warehouse performance issues across platforms.

## Performance Diagnostics

### Query Performance Analysis

**Key Metrics to Monitor:**
- Query execution time (P50, P95, P99)
- Data scanned/processed
- Rows returned
- Spill to disk (memory overflow)
- Network transfer time
- Compilation/planning time

### Common Performance Problems

| Symptom | Likely Cause | Solution |
|---------|-------------|----------|
| Slow queries overall | Missing partitioning/clustering | Implement partitioning on date columns |
| Queries that used to be fast are now slow | Data growth, stale statistics | Update statistics, consider partitioning |
| Some queries fast, others slow | Query-specific issues | Analyze slow query plans |
| Spilling to disk | Insufficient memory | Increase warehouse size, optimize joins |
| Long queue times | Insufficient concurrency | Add warehouses, enable auto-scaling |
| High costs | Inefficient queries | Optimize queries, use result caching |

## Platform-Specific Tuning

### Snowflake Performance Tuning

#### 1. Warehouse Sizing
```sql
-- Start with right-sized warehouse
-- Too small: Queries take longer, spill to disk
-- Too large: Wasted credits

-- Monitor warehouse load
SELECT
    warehouse_name,
    AVG(avg_running) as avg_concurrent_queries,
    AVG(avg_queued_load) as avg_queue_depth
FROM snowflake.account_usage.warehouse_load_history
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY warehouse_name;

-- If avg_concurrent_queries near max, scale up or enable multi-cluster
```

#### 2. Clustering Keys
```sql
-- Check clustering health
SELECT SYSTEM$CLUSTERING_INFORMATION('table_name');

-- If average_depth > 4, consider reclustering
ALTER TABLE table_name CLUSTER BY (date_column, frequently_filtered_column);

-- Monitor clustering depth
SELECT
    table_name,
    SYSTEM$CLUSTERING_DEPTH(table_name) as clustering_depth
FROM information_schema.tables
WHERE table_schema = 'PUBLIC';
```

#### 3. Query Profile Analysis
```sql
-- Find queries with high percentage scanned
SELECT
    query_id,
    query_text,
    total_elapsed_time,
    bytes_scanned,
    bytes_scanned / NULLIF(bytes_written_to_result, 0) as scan_efficiency
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(day, -1, CURRENT_TIMESTAMP())
  AND bytes_scanned > 1000000000  -- > 1 GB scanned
ORDER BY bytes_scanned DESC
LIMIT 20;
```

### BigQuery Performance Tuning

#### 1. Partitioning Effectiveness
```sql
-- Check partition pruning
SELECT
    job_id,
    query,
    total_bytes_processed,
    total_bytes_billed,
    total_slot_ms
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
  AND query LIKE '%partitioned_table%'
ORDER BY total_bytes_processed DESC;

-- Ensure partition filters are being used
-- Look for partition_filter in query execution details
```

#### 2. Clustering Effectiveness
```sql
-- Check clustering statistics
SELECT
    table_name,
    clustering_ordinal_position,
    clustering_column_name
FROM `project.dataset.INFORMATION_SCHEMA.CLUSTERING_COLUMNS`
WHERE table_name = 'your_table';

-- Monitor clustering benefit
-- Check if queries filtering on clustered columns scan less data
```

#### 3. BI Engine Optimization
```sql
-- Check BI Engine usage
SELECT
    query,
    bi_engine_statistics.bi_engine_mode,
    bi_engine_statistics.bi_engine_reasons,
    total_bytes_processed
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE DATE(creation_time) = CURRENT_DATE()
  AND bi_engine_statistics.bi_engine_mode IN ('FULL', 'PARTIAL', 'DISABLED')
ORDER BY creation_time DESC;

-- Optimize for BI Engine:
-- 1. Keep tables < 100 GB
-- 2. Use materialized views
-- 3. Partition and cluster tables
```

### Redshift Performance Tuning

#### 1. Distribution Key Optimization
```sql
-- Check table skew (uneven distribution)
SELECT
    TRIM(name) AS table_name,
    slice,
    num_values,
    minvalue,
    maxvalue
FROM svv_diskusage
WHERE name = 'large_table'
ORDER BY slice;

-- If skew > 10%, consider different DISTKEY
-- Ideal: All slices have similar num_values

-- Analyze distribution style effectiveness
SELECT
    query,
    segment,
    step,
    label,
    is_diskbased
FROM svl_query_summary
WHERE query = <query_id>
  AND label LIKE '%dist%';
```

#### 2. Sort Key Optimization
```sql
-- Check sort key effectiveness
SELECT
    TRIM(pgn.nspname) AS schema,
    TRIM(a.name) AS table,
    ((b.unsorted_rows / b.total_rows::FLOAT) * 100)::DECIMAL(5, 2) AS unsorted_pct
FROM (
    SELECT
        db_id,
        id,
        name,
        unsorted,
        SUM(rows) AS total_rows,
        SUM(CASE WHEN unsorted THEN rows ELSE 0 END) AS unsorted_rows
    FROM stv_tbl_perm
    GROUP BY 1, 2, 3, 4
) b
JOIN stv_tbl_perm a ON a.id = b.id
JOIN pg_namespace pgn ON pgn.oid = a.nspname_oid
WHERE b.unsorted_rows > 0
ORDER BY unsorted_pct DESC;

-- If unsorted_pct > 5%, run VACUUM
VACUUM table_name;
```

#### 3. WLM Queue Tuning
```sql
-- Analyze queue wait times
SELECT
    w.query,
    q.querytxt,
    w.queue_start_time,
    w.exec_start_time,
    DATEDIFF(seconds, w.queue_start_time, w.exec_start_time) AS queue_seconds,
    w.total_exec_time / 1000000 AS exec_seconds
FROM stl_wlm_query w
JOIN stl_query q ON w.query = q.query
WHERE queue_seconds > 10
ORDER BY w.queue_start_time DESC
LIMIT 100;

-- If many queries queuing:
-- 1. Enable concurrency scaling
-- 2. Adjust WLM memory allocation
-- 3. Add more queues for different workload types
```

## General Optimization Techniques

### 1. Partition Strategy

**Best Practices:**
```sql
-- Partition by frequently filtered date column
CREATE TABLE events (
    event_id BIGINT,
    event_date DATE,
    user_id BIGINT,
    event_data VARCHAR(1000)
)
PARTITION BY event_date;  -- Most platforms

-- Partition granularity:
-- Daily: Most common, good for time-series
-- Hourly: For high-volume, real-time data
-- Monthly: For slower-moving data

-- Always filter on partition column
-- ✅ GOOD
SELECT * FROM events WHERE event_date >= '2024-01-01';

-- ❌ BAD (full table scan)
SELECT * FROM events WHERE event_id = 12345;
```

### 2. Clustering/Sorting Strategy

**Clustering Column Selection:**
1. **High-cardinality first**: customer_id before country
2. **Frequently filtered**: Columns in WHERE clauses
3. **Join columns**: Improve join performance
4. **Limit to 3-4 columns**: More columns = diminishing returns

```sql
-- ✅ GOOD clustering order (high to low cardinality)
CLUSTER BY (customer_id, country, order_status);

-- ❌ BAD clustering order (low to high cardinality)
CLUSTER BY (order_status, country, customer_id);
```

### 3. Materialized Views

**When to Use:**
- Repeated complex aggregations
- Expensive joins on large tables
- Frequently accessed summary data
- Dashboard queries

```sql
-- Example: Daily customer summary
CREATE MATERIALIZED VIEW daily_customer_summary AS
SELECT
    DATE(order_timestamp) as order_date,
    customer_id,
    COUNT(*) as order_count,
    SUM(order_amount) as total_amount,
    AVG(order_amount) as avg_amount
FROM orders
GROUP BY DATE(order_timestamp), customer_id;

-- Refresh strategy depends on platform:
-- Snowflake: Automatic refresh
-- BigQuery: Manual or scheduled refresh
-- Redshift: Manual refresh
```

### 4. Query Result Caching

**Leverage Caching:**
```sql
-- Most platforms cache results for 24 hours
-- Same query = instant results

-- Ensure queries are identical:
-- ✅ Same: SELECT * FROM orders WHERE date = '2024-01-01';
-- ❌ Different: SELECT * FROM orders WHERE date = '2024-01-01' ;  -- Extra space

-- Disable cache for testing
ALTER SESSION SET USE_CACHED_RESULT = FALSE;  -- Snowflake
```

### 5. Avoid SELECT *

**Impact:**
```sql
-- ❌ BAD: Scans all columns
SELECT * FROM large_table WHERE date = '2024-01-01';
-- Scans: 100 GB (all 50 columns)

-- ✅ GOOD: Scans only needed columns
SELECT id, customer_id, amount FROM large_table WHERE date = '2024-01-01';
-- Scans: 5 GB (3 columns)

-- Cost reduction: 95%
-- Performance improvement: 20x
```

### 6. Join Optimization

**Join Order:**
```sql
-- Put largest table first (most platforms optimize automatically)
-- Filter before joining

-- ✅ GOOD: Filter before join
SELECT o.*, c.*
FROM (
    SELECT * FROM orders WHERE order_date >= '2024-01-01'
) o
JOIN customers c ON o.customer_id = c.customer_id;

-- ❌ BAD: Join then filter
SELECT o.*, c.*
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= '2024-01-01';
```

**Join Type Selection:**
- **INNER JOIN**: Most efficient, use when possible
- **LEFT/RIGHT JOIN**: More expensive, use only when needed
- **FULL OUTER JOIN**: Most expensive, avoid if possible
- **CROSS JOIN**: Extremely expensive, use with caution

### 7. Window Function Optimization

```sql
-- ✅ GOOD: Filter before windowing
WITH filtered AS (
    SELECT * FROM events WHERE event_date >= '2024-01-01'
)
SELECT
    user_id,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_timestamp) as rn
FROM filtered;

-- ✅ GOOD: Use QUALIFY for window function filtering (Snowflake, BigQuery)
SELECT user_id, event_timestamp
FROM events
WHERE event_date >= '2024-01-01'
QUALIFY ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_timestamp) = 1;
```

## Common Anti-Patterns and Fixes

### Anti-Pattern 1: No Partitioning on Large Tables

❌ **Problem:**
```sql
CREATE TABLE events (
    event_id BIGINT,
    event_date DATE,
    data VARCHAR(1000)
);
-- No partitioning, full table scans
```

✅ **Solution:**
```sql
CREATE TABLE events (
    event_id BIGINT,
    event_date DATE,
    data VARCHAR(1000)
)
PARTITION BY event_date;
```

### Anti-Pattern 2: Functions on Filtered Columns

❌ **Problem:**
```sql
SELECT * FROM orders
WHERE YEAR(order_date) = 2024;
-- Prevents partition pruning and index usage
```

✅ **Solution:**
```sql
SELECT * FROM orders
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01';
```

### Anti-Pattern 3: Large Result Sets

❌ **Problem:**
```sql
SELECT * FROM events;  -- Returns 1 billion rows
```

✅ **Solution:**
```sql
-- Use LIMIT for exploration
SELECT * FROM events LIMIT 1000;

-- Aggregate instead of returning all rows
SELECT date, COUNT(*) FROM events GROUP BY date;

-- Use pagination
SELECT * FROM events
WHERE event_id > :last_seen_id
ORDER BY event_id
LIMIT 1000;
```

### Anti-Pattern 4: Repeated Subqueries

❌ **Problem:**
```sql
SELECT
    customer_id,
    (SELECT COUNT(*) FROM orders WHERE customer_id = c.customer_id) as order_count,
    (SELECT SUM(amount) FROM orders WHERE customer_id = c.customer_id) as total_amount
FROM customers c;
-- Executes subquery for each customer
```

✅ **Solution:**
```sql
SELECT
    c.customer_id,
    COUNT(o.order_id) as order_count,
    SUM(o.amount) as total_amount
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id;
```

### Anti-Pattern 5: Cartesian Products

❌ **Problem:**
```sql
SELECT * FROM table1, table2;  -- Returns all combinations
-- 1000 rows × 1000 rows = 1,000,000 rows
```

✅ **Solution:**
```sql
SELECT * FROM table1
INNER JOIN table2 ON table1.id = table2.table1_id;
```

## Monitoring and Alerting

### Key Metrics to Track

**Query Performance:**
```sql
-- Track P95 query execution time
-- Alert if > threshold (e.g., 10 seconds)

-- Track queries scanning > X TB
-- Alert if unexpected large scans

-- Track failed queries
-- Alert on query failures
```

**Resource Utilization:**
```sql
-- Warehouse/cluster CPU utilization
-- Alert if consistently > 80%

-- Memory utilization
-- Alert on spills to disk

-- Query queue depth
-- Alert if > 10 queries queuing
```

**Cost Management:**
```sql
-- Daily query cost
-- Alert if > expected budget

-- Storage growth rate
-- Alert if > X% per month

-- Top cost queries
-- Review and optimize weekly
```

## Performance Tuning Checklist

### Table Design
- [ ] Partition large tables by date
- [ ] Cluster on frequently filtered columns
- [ ] Use appropriate data types (avoid VARCHAR(MAX))
- [ ] Implement proper compression/encoding
- [ ] Set data retention policies

### Query Design
- [ ] Select only needed columns
- [ ] Filter on partition/cluster columns
- [ ] Avoid functions on filtered columns
- [ ] Use CTEs for complex logic
- [ ] Leverage window functions appropriately
- [ ] Use EXIST instead of IN for subqueries

### Maintenance
- [ ] Update statistics regularly
- [ ] Vacuum/reorganize tables as needed
- [ ] Monitor clustering depth
- [ ] Review slow query log weekly
- [ ] Archive old partitions
- [ ] Drop unused tables/views

### Optimization
- [ ] Create materialized views for repeated queries
- [ ] Enable result caching
- [ ] Right-size warehouses/clusters
- [ ] Enable auto-scaling for variable workloads
- [ ] Implement workload management (WLM)
- [ ] Monitor and optimize join strategies

## Performance Testing

### Baseline Metrics
```sql
-- Establish baseline before optimization
1. Record query execution time
2. Note data scanned
3. Check resource utilization
4. Document cost
```

### A/B Testing
```sql
-- Test optimization impact
1. Run original query 10 times, record metrics
2. Apply optimization
3. Run optimized query 10 times, record metrics
4. Compare: execution time, data scanned, cost
5. Validate results match
```

### Regression Testing
```sql
-- Prevent performance degradation
1. Maintain suite of critical queries
2. Run weekly and record performance
3. Alert on > 20% degradation
4. Investigate and fix regressions
```

## Tools and Resources

### Snowflake
- Query Profile (UI)
- SYSTEM$ functions (CLUSTERING_INFORMATION, etc.)
- ACCOUNT_USAGE views
- Resource Monitors

### BigQuery
- Query Execution Details (UI)
- INFORMATION_SCHEMA views
- Query Plan Explanation
- BI Engine metrics

### Redshift
- Query Plan (EXPLAIN)
- System Tables (STL_, STV_, SVL_, SVV_)
- Performance Insights
- CloudWatch metrics

### General
- dbt for transformation testing
- Great Expectations for data quality
- Monte Carlo/Datafold for data observability
- Custom monitoring dashboards
