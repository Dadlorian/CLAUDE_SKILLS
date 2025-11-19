# Cost Optimization Strategies for ETL/ELT

## Warehouse Cost Optimization

### Snowflake Cost Management

#### Warehouse Sizing
```sql
-- Use appropriate warehouse size
USE WAREHOUSE X_SMALL_WH;  -- Development, light queries
USE WAREHOUSE SMALL_WH;    -- Regular transformations
USE WAREHOUSE MEDIUM_WH;   -- Heavy batch processing
USE WAREHOUSE LARGE_WH;    -- Critical, time-sensitive loads

-- Auto-suspend & auto-resume
ALTER WAREHOUSE ETL_WH SET
    AUTO_SUSPEND = 60           -- Suspend after 1 minute idle
    AUTO_RESUME = TRUE          -- Auto-start on query
    INITIALLY_SUSPENDED = TRUE; -- Start suspended

-- Multi-cluster warehouses for varying load
CREATE WAREHOUSE VARIABLE_WH WITH
    WAREHOUSE_SIZE = 'MEDIUM'
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 5
    SCALING_POLICY = 'STANDARD'  -- or 'ECONOMY'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE;
```

#### Query Optimization
```sql
-- ❌ Expensive: Full table scan
SELECT COUNT(*) FROM large_table;
-- Cost: Scans all data

-- ✅ Cheap: Use metadata
SELECT ROW_COUNT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME = 'LARGE_TABLE';
-- Cost: Metadata query (free)

-- ❌ Expensive: Cross-region data transfer
SELECT * FROM eu_region.database.table;

-- ✅ Cheap: Same region
SELECT * FROM us_region.database.table;
```

#### Storage Optimization
```sql
-- Drop unused tables
DROP TABLE IF EXISTS temp_table;

-- Use transient tables (no Fail-safe, lower cost)
CREATE TRANSIENT TABLE staging_data AS
SELECT * FROM source;

-- Time travel retention
ALTER TABLE table_name SET DATA_RETENTION_TIME_IN_DAYS = 1;  -- Min for production
-- Default is 1 day, max 90 (costs more)

-- Clustering for better pruning
ALTER TABLE large_table CLUSTER BY (date, customer_id);
-- Reduces data scanned = lower cost
```

### BigQuery Cost Management

#### Query Cost Control
```sql
-- Set maximum bytes billed
SELECT * FROM large_table
WHERE date >= '2024-01-01'
LIMIT 1000000;  -- Prevent runaway queries

-- Use partition/clustering
SELECT *
FROM partitioned_table
WHERE _PARTITIONDATE = '2024-01-15'  -- Scans only one partition
  AND customer_id IN (1, 2, 3);      -- Uses clustering

-- ❌ Expensive: No partition filter
SELECT * FROM partitioned_table
WHERE amount > 100;  -- Scans ALL partitions

-- ✅ Cheap: Partition filter
SELECT * FROM partitioned_table
WHERE _PARTITIONDATE >= '2024-01-01'
  AND amount > 100;  -- Scans only needed partitions
```

#### Storage Tiers
```sql
-- Active storage: $0.02/GB/month
-- Long-term storage: $0.01/GB/month (after 90 days inactive)

-- Separate hot and cold data
CREATE TABLE active_orders
PARTITION BY DATE(order_date)
AS SELECT * FROM orders
WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY);

CREATE TABLE archived_orders
PARTITION BY DATE(order_date)
AS SELECT * FROM orders
WHERE order_date < DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY);
```

#### Materialized Views
```sql
-- Cache expensive aggregations
CREATE MATERIALIZED VIEW mv_daily_sales
PARTITION BY DATE(sale_date)
CLUSTER BY product_id
AS
SELECT
    DATE(order_timestamp) as sale_date,
    product_id,
    SUM(amount) as total_sales,
    COUNT(*) as order_count
FROM orders
GROUP BY sale_date, product_id;

-- Query MV instead of base table (cheaper)
SELECT * FROM mv_daily_sales WHERE sale_date = '2024-01-15';
```

### Redshift Cost Management

#### Distribution & Sort Keys
```sql
-- Proper distribution reduces data movement
CREATE TABLE fact_orders (
    order_id BIGINT,
    customer_id BIGINT,
    amount DECIMAL(10,2)
)
DISTSTYLE KEY
DISTKEY(customer_id)  -- Co-locate with dim_customers
SORTKEY(order_date);  -- Efficient range queries

-- Check distribution
SELECT slice, COUNT(*)
FROM stv_blocklist
WHERE tbl = (SELECT id FROM stv_tbl_perm WHERE name = 'fact_orders')
GROUP BY slice
ORDER BY slice;
-- Aim for even distribution
```

#### Vacuum & Analyze
```sql
-- Reclaim space from deleted rows
VACUUM DELETE ONLY fact_orders;

-- Update query planner statistics
ANALYZE fact_orders;

-- Automated: Use automatic vacuum
ALTER TABLE fact_orders SET
    VACUUM_SORT_BENEFIT_THRESHOLD = 50;
```

#### Reserved Capacity
```
-- Instead of on-demand pricing
-- Purchase reserved nodes (1-3 year commitment)
-- Save up to 75% vs on-demand

# AWS Console: Redshift → Reserved Nodes
# Choose: Node type, quantity, commitment term
```

## dbt Optimization

### Reduce Model Count
```sql
-- ❌ Many small models (overhead)
-- stg_orders_step1.sql
-- stg_orders_step2.sql
-- stg_orders_step3.sql

-- ✅ Combine into fewer, well-organized models
-- stg_orders.sql (all transformations)
WITH source AS (
    SELECT * FROM {{ source('db', 'orders') }}
),
cleaned AS (
    -- Cleaning logic
),
enriched AS (
    -- Enrichment logic
)
SELECT * FROM enriched
```

### Use Ephemeral Models
```sql
-- {{ config(materialized='ephemeral') }}
-- Not materialized, compiled as CTE
-- No table/view created = no storage cost

WITH ephemeral_cte AS (
    {{ ref('ephemeral_model') }}  -- Inlined as CTE
)
SELECT * FROM ephemeral_cte
```

### Incremental Models
```sql
-- ✅ Process only changed data
{{ config(materialized='incremental', unique_key='id') }}

SELECT * FROM {{ source('db', 'large_table') }}
{% if is_incremental() %}
WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}

-- vs ❌ Full refresh (expensive)
{{ config(materialized='table') }}
SELECT * FROM {{ source('db', 'large_table') }}  -- All rows every run
```

### Slim CI
```bash
# Only run/test modified models
dbt run --select state:modified+ --state ./prod-artifacts

# vs running everything
dbt run  # ❌ Expensive in CI
```

## Airflow Optimization

### Resource Pools
```python
# Limit concurrent expensive tasks
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'pool': 'heavy_compute',      # Shared resource pool
    'pool_slots': 2,              # Each task uses 2 slots
}

with DAG('resource_managed', default_args=default_args, ...) as dag:
    # Tasks will queue if pool is full
    # Prevents overwhelming warehouse
    heavy_task = BashOperator(...)
```

### Dynamic Workers
```yaml
# Kubernetes Executor: Scale workers dynamically
executor: KubernetesExecutor

kubernetes:
  worker_container_repository: apache/airflow
  worker_container_tag: 2.7.1
  namespace: airflow
  delete_worker_pods: True           # Clean up after tasks
  delete_worker_pods_on_failure: False

  # Resource requests (min)
  worker_memory_request: 512Mi
  worker_cpu_request: 0.5

  # Resource limits (max)
  worker_memory_limit: 2Gi
  worker_cpu_limit: 1.0
```

### Schedule Optimization
```python
# Run during off-peak hours
with DAG(
    'cost_optimized',
    schedule_interval='0 2 * * *',  # 2 AM (lowest demand)
    ...
):
    # Batch processing during cheap hours
```

## Data Ingestion Cost

### Batch vs Streaming
```python
# ❌ Expensive: Micro-batches (many warehouse starts)
schedule_interval='*/5 * * * *'  # Every 5 minutes

# ✅ Cheaper: Larger batches
schedule_interval='@hourly'      # Hourly batches

# Balance freshness requirements with cost
```

### Connector Optimization

#### Fivetran MAR Optimization
```yaml
# Reduce Monthly Active Rows (MAR)

1. Use incremental sync instead of full table
2. Exclude unnecessary columns
   blocked_columns:
     - table: users
       columns: [avatar_url, bio, preferences]

3. Filter rows at source
   custom_sql: "SELECT * FROM orders WHERE status != 'draft'"

4. Adjust sync frequency
   sync_frequency: 360  # 6 hours instead of 1 hour

5. Archive historical data
   # Move old data to cheaper storage
```

#### Airbyte Optimization
```yaml
# Optimize sync frequency per connector
connections:
  critical_data:
    schedule: "0 */1 * * *"  # Hourly
  regular_data:
    schedule: "0 */6 * * *"  # Every 6 hours
  historical_data:
    schedule: "0 0 * * *"    # Daily
```

## Storage Optimization

### Archive Old Data
```sql
-- Move to cheaper storage
-- Snowflake: Use stages for archival
COPY INTO @my_s3_stage/archive/orders_2020/
FROM (SELECT * FROM orders WHERE YEAR(order_date) = 2020)
FILE_FORMAT = (TYPE = PARQUET COMPRESSION = SNAPPY);

-- Drop from warehouse
DELETE FROM orders WHERE YEAR(order_date) = 2020;

-- BigQuery: Export to GCS
EXPORT DATA OPTIONS(
    uri='gs://archive-bucket/orders_2020_*.parquet',
    format='PARQUET',
    compression='SNAPPY',
    overwrite=true
) AS
SELECT * FROM orders WHERE EXTRACT(YEAR FROM order_date) = 2020;

-- Delete from BigQuery
DELETE FROM orders WHERE EXTRACT(YEAR FROM order_date) = 2020;
```

### Data Retention Policies
```sql
-- Automatic cleanup
CREATE OR REPLACE PROCEDURE cleanup_old_data()
RETURNS STRING
LANGUAGE JAVASCRIPT
AS
$$
    // Delete data older than 2 years
    var sql = `
        DELETE FROM orders
        WHERE order_date < DATEADD(year, -2, CURRENT_DATE());
    `;
    snowflake.execute({sqlText: sql});
    return 'Cleanup completed';
$$;

-- Schedule via Snowflake task
CREATE TASK monthly_cleanup
    WAREHOUSE = ADMIN_WH
    SCHEDULE = 'USING CRON 0 0 1 * * America/Los_Angeles'  -- First of month
AS
    CALL cleanup_old_data();

ALTER TASK monthly_cleanup RESUME;
```

### Compression
```sql
-- Use compressed file formats
-- Parquet with Snappy compression (good balance)
COPY INTO table FROM @stage
FILE_FORMAT = (TYPE = PARQUET COMPRESSION = SNAPPY);

-- vs uncompressed CSV (5-10x larger)
```

## Monitoring & Alerting

### Cost Monitoring Queries

#### Snowflake
```sql
-- Warehouse cost tracking
SELECT
    warehouse_name,
    SUM(credits_used) as total_credits,
    SUM(credits_used) * 3.00 as estimated_cost_usd  -- $3/credit example
FROM snowflake.account_usage.warehouse_metering_history
WHERE start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP)
GROUP BY warehouse_name
ORDER BY total_credits DESC;

-- Query cost
SELECT
    query_id,
    query_text,
    warehouse_name,
    credits_used_cloud_services,
    bytes_scanned / 1024 / 1024 / 1024 as gb_scanned
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP)
  AND credits_used_cloud_services > 0
ORDER BY credits_used_cloud_services DESC
LIMIT 100;

-- Storage cost
SELECT
    TABLE_CATALOG || '.' || TABLE_SCHEMA || '.' || TABLE_NAME as full_table_name,
    ACTIVE_BYTES / 1024 / 1024 / 1024 as active_gb,
    TIME_TRAVEL_BYTES / 1024 / 1024 / 1024 as time_travel_gb,
    FAILSAFE_BYTES / 1024 / 1024 / 1024 as failsafe_gb
FROM snowflake.account_usage.table_storage_metrics
WHERE ACTIVE_BYTES > 0
ORDER BY ACTIVE_BYTES DESC
LIMIT 100;
```

#### BigQuery
```sql
-- Query costs (last 7 days)
SELECT
    user_email,
    project_id,
    SUM(total_bytes_billed) / 1024 / 1024 / 1024 / 1024 as tb_billed,
    SUM(total_bytes_billed) / 1024 / 1024 / 1024 / 1024 * 5 as cost_usd  -- $5/TB
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND statement_type != 'SCRIPT'
GROUP BY user_email, project_id
ORDER BY tb_billed DESC;

-- Storage costs
SELECT
    table_schema,
    table_name,
    size_bytes / 1024 / 1024 / 1024 as size_gb,
    size_bytes / 1024 / 1024 / 1024 * 0.02 as monthly_cost_active,  -- $0.02/GB active
    size_bytes / 1024 / 1024 / 1024 * 0.01 as monthly_cost_longterm -- $0.01/GB long-term
FROM `project.dataset`.INFORMATION_SCHEMA.TABLE_STORAGE
ORDER BY size_bytes DESC
LIMIT 100;
```

### Cost Alerts
```python
# Alert on high costs
def check_warehouse_costs():
    """Alert if costs exceed threshold"""
    query = """
        SELECT SUM(credits_used) as total_credits
        FROM snowflake.account_usage.warehouse_metering_history
        WHERE start_time >= CURRENT_DATE
    """

    result = snowflake.execute(query)
    credits_used = result[0]['total_credits']

    # Alert if > 100 credits/day
    if credits_used > 100:
        send_alert(
            subject="High Warehouse Costs",
            message=f"Used {credits_used} credits today (threshold: 100)"
        )
```

## Best Practices Checklist

- [ ] Use appropriate warehouse size for workload
- [ ] Enable auto-suspend on warehouses
- [ ] Use incremental models instead of full refresh
- [ ] Partition large tables by date
- [ ] Cluster tables on filter columns
- [ ] Archive historical data to cheap storage
- [ ] Set data retention to minimum needed
- [ ] Use materialized views for expensive aggregations
- [ ] Schedule heavy jobs during off-peak hours
- [ ] Monitor and alert on cost anomalies
- [ ] Use transient tables for staging
- [ ] Compress data in transit and storage
- [ ] Limit query result sizes
- [ ] Use serverless/on-demand for variable workloads
- [ ] Reserve capacity for predictable workloads

## Cost Breakdown Example

### Typical Monthly Costs
```
Data Warehouse (Snowflake):
  - Compute (warehouses):     $1,500
  - Storage (active):         $200
  - Storage (time travel):    $50
  - Data transfer:            $30
  Total:                      $1,780

Data Ingestion (Fivetran):
  - MAR-based pricing:        $800
  - Premium connectors:       $200
  Total:                      $1,000

Orchestration (Airflow):
  - Infrastructure (K8s):     $400
  - Monitoring:               $50
  Total:                      $450

Overall Monthly Total:        $3,230

Per-User Cost (100 users):    $32.30/user/month
```

## Resources

- **Snowflake Pricing**: https://www.snowflake.com/pricing/
- **BigQuery Pricing**: https://cloud.google.com/bigquery/pricing
- **Redshift Pricing**: https://aws.amazon.com/redshift/pricing/
- **Fivetran Pricing**: https://fivetran.com/pricing
- **Cost Optimization Guide**: Specific to each platform's documentation
