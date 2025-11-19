# Data Warehouse Cost Optimization Strategies

Comprehensive guide to reducing cloud data warehouse costs while maintaining performance and functionality.

## Cost Components

### Snowflake Cost Breakdown
```
1. Compute (Credits)
   - Virtual warehouse usage
   - Snowpipe streaming
   - Materialized view maintenance
   - Search optimization service

2. Storage
   - Data storage
   - Time Travel storage
   - Fail-safe storage

3. Data Transfer
   - Egress to external clouds
   - Cross-region transfers
   - External function calls
```

### BigQuery Cost Breakdown
```
1. Analysis (Queries)
   - On-demand: $5/TB processed
   - Flat-rate: Reserved slots

2. Storage
   - Active: $20/TB/month
   - Long-term (90+ days): $10/TB/month

3. Streaming Inserts
   - $0.01 per 200 MB

4. Other
   - BigQuery ML
   - BI Engine
   - Data Transfer
```

### Redshift Cost Breakdown
```
1. Compute Nodes
   - On-demand per node/hour
   - Reserved instances (1-3 year)
   - Serverless (RPU-hours)

2. Storage (RA3 only)
   - Managed storage pricing

3. Additional Services
   - Redshift Spectrum ($5/TB scanned)
   - Concurrency Scaling
   - Data Transfer
```

## Cost Optimization Strategies

### 1. Compute Optimization

#### Snowflake: Right-Size Warehouses

```sql
-- Monitor warehouse utilization
SELECT
    warehouse_name,
    AVG(avg_running) as avg_concurrent_queries,
    AVG(avg_queued_load) as avg_queue_depth,
    SUM(credits_used) as total_credits
FROM snowflake.account_usage.warehouse_load_history
WHERE start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
GROUP BY warehouse_name
ORDER BY total_credits DESC;

-- Recommendations:
-- If avg_concurrent_queries < 1: Warehouse too large, downsize
-- If avg_queue_depth > 5: Warehouse too small, upsize or add clusters
-- If avg_concurrent_queries 1-3: Size is appropriate
```

**Auto-Suspend Configuration:**
```sql
-- Set aggressive auto-suspend for development
ALTER WAREHOUSE dev_wh SET AUTO_SUSPEND = 60;  -- 1 minute

-- Moderate for production (balance cost vs. startup time)
ALTER WAREHOUSE prod_wh SET AUTO_SUSPEND = 300;  -- 5 minutes

-- Cost Impact: Can save 50-80% on idle warehouses
```

**Multi-Cluster Warehouses:**
```sql
-- Scale out instead of up for concurrent users
CREATE WAREHOUSE reporting_wh
    WAREHOUSE_SIZE = 'MEDIUM'
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 5  -- Auto-scale for concurrency
    SCALING_POLICY = 'ECONOMY';  -- Favor cost over speed

-- ECONOMY: Conservatively add clusters (slower scale-up, lower cost)
-- STANDARD: Aggressively add clusters (faster scale-up, higher cost)
```

#### BigQuery: Query Cost Management

```sql
-- Estimate query cost before running (dry run)
-- In BigQuery UI: Check "Dry run" option
-- Via API: jobs.query with dryRun=true

-- Set maximum bytes billed per query
ALTER PROJECT `project-id`
SET OPTIONS (
    `maximum_bytes_billed` = 1099511627776  -- 1 TB limit
);

-- Per-query limit (overrides project default)
#standardSQL
-- @run_at_project_limit = 1099511627776
SELECT * FROM large_table;
```

**Flat-Rate vs. On-Demand:**
```
On-Demand: $5/TB processed
Flat-Rate: $2,000/month per 100 slots

Break-even: ~400 TB/month
- Process < 400 TB/month: Use on-demand
- Process > 400 TB/month: Consider flat-rate
- Highly variable workload: On-demand
- Steady predictable workload: Flat-rate
```

#### Redshift: Reserved Instances

```
Reserved Instance Savings:
- 1-year no upfront: ~40% savings
- 1-year all upfront: ~45% savings
- 3-year all upfront: ~75% savings

Recommendation:
- Use RI for base capacity
- Use on-demand for peak overflow
- Use Serverless for sporadic workloads
```

### 2. Storage Optimization

#### Reduce Storage Costs

**Compression:**
```sql
-- Snowflake (automatic compression)
-- No action needed, but monitor compression ratio

-- Analyze compression effectiveness
SELECT
    table_name,
    bytes_uncompressed / 1024 / 1024 / 1024 as gb_uncompressed,
    bytes_compressed / 1024 / 1024 / 1024 as gb_compressed,
    ROUND(100 * (1 - bytes_compressed / bytes_uncompressed), 2) as compression_pct
FROM (
    SELECT
        table_name,
        SUM(active_bytes) as bytes_compressed,
        SUM(active_bytes / compression_ratio) as bytes_uncompressed
    FROM snowflake.account_usage.table_storage_metrics
    WHERE table_schema = 'PUBLIC'
    GROUP BY table_name
)
ORDER BY gb_compressed DESC;
```

**Archival and Retention:**
```sql
-- Set table expiration (temporary data)
-- Snowflake
CREATE TRANSIENT TABLE temp_data (...);  -- No fail-safe (7 day recovery)

-- BigQuery
CREATE TABLE temp_data (...)
OPTIONS(
    expiration_timestamp=TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
);

-- Set partition expiration
ALTER TABLE event_logs
SET OPTIONS(partition_expiration_days=90);  -- BigQuery

-- Reduce time travel retention
ALTER TABLE staging_data
SET DATA_RETENTION_TIME_IN_DAYS = 1;  -- Snowflake (minimum 0-1 days)
```

**Archive Old Data:**
```sql
-- Move old data to cheaper storage
-- Option 1: External tables on S3/GCS (query occasionally)
CREATE EXTERNAL TABLE archived_data (...)
LOCATION = 's3://archive-bucket/data/';

-- Option 2: Unload to object storage (query rarely)
-- Snowflake
COPY INTO @external_stage/archive/
FROM (SELECT * FROM old_data WHERE year < 2020)
FILE_FORMAT = (TYPE = 'PARQUET' COMPRESSION = 'SNAPPY');

-- Then drop from warehouse
DROP TABLE old_data;

-- Cost Reduction:
-- Warehouse storage: $20-40/TB/month
-- Object storage: $20-23/TB/month (S3/GCS)
-- Object storage (archive): $1-4/TB/month (Glacier/Archive)
```

#### BigQuery Long-Term Storage

```sql
-- Automatically cheaper after 90 days of no modifications
-- Active: $20/TB/month
-- Long-term: $10/TB/month

-- Maximize long-term storage:
-- 1. Don't modify tables unnecessarily
-- 2. Partition tables (old partitions become long-term)
-- 3. Separate append-only tables from frequently updated ones

-- Check long-term storage savings
SELECT
    table_name,
    ROUND(active_logical_bytes / POW(10, 12), 2) as active_tb,
    ROUND(long_term_logical_bytes / POW(10, 12), 2) as longterm_tb,
    ROUND(long_term_logical_bytes * 10 / POW(10, 12), 2) as longterm_cost_usd
FROM `project.dataset.__TABLES__`
WHERE long_term_logical_bytes > 0;
```

### 3. Query Optimization for Cost

#### Avoid SELECT *

```sql
-- Cost comparison
-- ❌ BAD: SELECT *
SELECT * FROM wide_table WHERE date = '2024-01-01';
-- Scans: 100 GB (all 50 columns)
-- Cost: $0.50 (BigQuery on-demand)

-- ✅ GOOD: Select specific columns
SELECT id, customer_id, amount FROM wide_table WHERE date = '2024-01-01';
-- Scans: 5 GB (3 columns)
-- Cost: $0.025 (BigQuery on-demand)
-- Savings: 95%
```

#### Partition Filtering

```sql
-- Always filter on partition column
-- ✅ GOOD
SELECT * FROM events
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-31';
-- Scans: 31 partitions (~10 GB)
-- Cost: $0.05

-- ❌ BAD
SELECT * FROM events
WHERE user_id = 12345;
-- Scans: ALL partitions (~10 TB)
-- Cost: $50
-- Cost Difference: 1000x
```

#### Use Approximation Functions

```sql
-- ✅ Approximate (much cheaper)
SELECT
    country,
    APPROX_COUNT_DISTINCT(user_id) as unique_users  -- BigQuery
    -- OR HLL_COUNT.INIT(user_id) for HyperLogLog
FROM events
GROUP BY country;
-- Scans: 10 GB
-- Accuracy: ~99%
-- Cost: $0.05

-- ❌ Exact (expensive)
SELECT
    country,
    COUNT(DISTINCT user_id) as unique_users
FROM events
GROUP BY country;
-- Scans: 100 GB (needs to deduplicate)
-- Accuracy: 100%
-- Cost: $0.50
```

#### Materialize Expensive Queries

```sql
-- Instead of running expensive query repeatedly:
-- Create materialized view (one-time cost)
CREATE MATERIALIZED VIEW daily_user_summary AS
SELECT
    DATE(event_timestamp) as event_date,
    user_id,
    COUNT(*) as event_count,
    COUNT(DISTINCT session_id) as session_count
FROM events
GROUP BY DATE(event_timestamp), user_id;

-- Query materialized view (cheap)
SELECT * FROM daily_user_summary
WHERE event_date >= '2024-01-01';
-- Cost: Minimal (small MV)

-- vs. Querying base table each time (expensive)
-- Cost: High (large fact table)
```

### 4. Result Caching

**Leverage Query Result Cache:**
```sql
-- Most platforms cache results for 24 hours
-- Identical query = $0 cost

-- Best Practices:
-- 1. Standardize queries (exact match required)
-- 2. Use parameterized queries/views
-- 3. Schedule reports during same time window
-- 4. Educate users to check cache before re-running

-- Snowflake: Check if query used cache
SELECT
    query_id,
    query_text,
    execution_time,
    bytes_scanned,
    query_result_reused
FROM snowflake.account_usage.query_history
WHERE start_time >= CURRENT_DATE()
ORDER BY start_time DESC;
```

### 5. Workload Management

#### Separate Workloads by Cost Profile

```sql
-- Snowflake: Multiple warehouses for different workloads
-- ETL Warehouse (X-Large, runs 2 hours/day)
CREATE WAREHOUSE etl_wh
    WAREHOUSE_SIZE = 'X-LARGE'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;
-- Daily cost: ~$8 (2 hours × 16 credits × $2.50)

-- BI Warehouse (Medium, runs 8 hours/day, multi-cluster)
CREATE WAREHOUSE bi_wh
    WAREHOUSE_SIZE = 'MEDIUM'
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 3
    AUTO_SUSPEND = 300;
-- Daily cost: ~$32 (8 hours × 4 credits × $2.50 × ~2.5 avg clusters)

-- Ad-hoc Warehouse (Small, intermittent)
CREATE WAREHOUSE adhoc_wh
    WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 60;  -- Aggressive suspend
-- Daily cost: ~$1 (variable usage)
```

#### BigQuery: Slot Reservations

```sql
-- Reserve slots for predictable workloads
-- Baseline: 500 slots ($4,000/month)
-- Burst: On-demand for overflow

-- Cost savings:
-- Without reservation: ~$6,000/month (1200 TB × $5/TB)
-- With reservation: ~$4,000/month (500 slots)
-- Savings: $2,000/month (33%)
```

### 6. Monitoring and Alerting

#### Set Up Cost Alerts

**Snowflake Resource Monitors:**
```sql
-- Create resource monitor with alerts
CREATE RESOURCE MONITOR monthly_limit WITH
    CREDIT_QUOTA = 5000
    FREQUENCY = MONTHLY
    START_TIMESTAMP = IMMEDIATELY
    TRIGGERS
        ON 75 PERCENT DO NOTIFY
        ON 100 PERCENT DO SUSPEND
        ON 110 PERCENT DO SUSPEND_IMMEDIATE;

-- Assign to warehouse
ALTER WAREHOUSE prod_wh SET RESOURCE_MONITOR = monthly_limit;
```

**BigQuery Cost Controls:**
```sql
-- Set project-level daily limit
-- In UI: BigQuery → Settings → Set custom quota
-- Via API: Set maximum bytes billed

-- Monitor daily costs
SELECT
    DATE(creation_time) as query_date,
    user_email,
    SUM(total_bytes_processed) / POW(10, 12) as tb_processed,
    SUM(total_bytes_processed) / POW(10, 12) * 5 as estimated_cost_usd
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE DATE(creation_time) >= CURRENT_DATE() - 7
GROUP BY query_date, user_email
ORDER BY query_date DESC, estimated_cost_usd DESC;
```

#### Track Cost Per User/Team

```sql
-- Snowflake: Cost by user
SELECT
    user_name,
    warehouse_name,
    SUM(credits_used) as total_credits,
    SUM(credits_used) * 2.5 as estimated_cost_usd  -- Adjust rate
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(month, -1, CURRENT_TIMESTAMP())
GROUP BY user_name, warehouse_name
ORDER BY total_credits DESC;

-- Assign warehouses by team/cost center for chargeback
```

## Cost Optimization Checklist

### Immediate Actions (Quick Wins)
- [ ] Enable auto-suspend on all warehouses (60-300 seconds)
- [ ] Set partition expiration on temporary tables
- [ ] Implement result caching strategy
- [ ] Review and resize oversized warehouses
- [ ] Set up cost monitoring and alerts
- [ ] Audit expensive queries (top 10%)
- [ ] Drop unused tables and views
- [ ] Disable unused warehouses/clusters

### Short-Term (1-4 Weeks)
- [ ] Implement partition pruning on large tables
- [ ] Create materialized views for repeated queries
- [ ] Optimize top 20% most expensive queries
- [ ] Migrate low-priority workloads to smaller warehouses
- [ ] Implement workload separation (ETL, BI, ad-hoc)
- [ ] Review and adjust time travel retention
- [ ] Archive historical data to object storage
- [ ] Educate users on cost-efficient query patterns

### Long-Term (1-3 Months)
- [ ] Evaluate reserved capacity vs. on-demand
- [ ] Implement comprehensive data lifecycle policies
- [ ] Build cost dashboard and chargeback system
- [ ] Establish query performance baselines
- [ ] Implement automated query optimization
- [ ] Review table design and clustering
- [ ] Evaluate platform-specific features (BI Engine, etc.)
- [ ] Conduct quarterly cost optimization reviews

## ROI Calculations

### Example Cost Reduction Scenarios

**Scenario 1: Auto-Suspend Optimization**
```
Before: 10 warehouses, 24/7 running, Medium (4 credits/hour)
Cost: 10 × 24 × 30 × 4 × $2.50 = $72,000/month

After: Auto-suspend 60 seconds, actual usage 8 hours/day
Cost: 10 × 8 × 30 × 4 × $2.50 = $24,000/month

Savings: $48,000/month (67%)
Effort: 30 minutes
```

**Scenario 2: Partition Pruning**
```
Before: 1000 queries/day, average 10 TB scanned
Cost: 1000 × 10 × $5 / 1000 = $50/day = $1,500/month

After: Implement partitioning, average 100 GB scanned
Cost: 1000 × 0.1 × $5 / 1000 = $0.50/day = $15/month

Savings: $1,485/month (99%)
Effort: 1-2 weeks (one-time)
```

**Scenario 3: Reserved Capacity**
```
Before: BigQuery on-demand, 800 TB/month
Cost: 800 × $5 = $4,000/month

After: 100 slots flat-rate reservation
Cost: $2,000/month

Savings: $2,000/month (50%)
Commitment: Monthly or annual
```

## Tools and Resources

### Cost Monitoring Tools
- **Snowflake**: Resource Monitors, Account Usage views
- **BigQuery**: Cost breakdown in UI, INFORMATION_SCHEMA
- **Redshift**: CloudWatch, System Tables, Cost Explorer
- **Third-Party**: Select Star, DataFold, Monte Carlo

### Best Practices Resources
- Platform-specific cost optimization guides
- Cost calculators and estimators
- Community forums and user groups
- Vendor professional services

### Automation
- dbt for query optimization testing
- Airflow for scheduled maintenance (vacuum, analyze)
- Lambda/Cloud Functions for automated alerts
- Terraform for infrastructure as code
