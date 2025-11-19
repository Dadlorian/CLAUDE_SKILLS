# ETL/ELT Performance Tuning Guide

## Query Optimization

### Use Incremental Loading
```sql
-- ❌ Slow: Full table scan every time
SELECT * FROM large_table

-- ✅ Fast: Incremental with indexed timestamp
SELECT *
FROM large_table
WHERE updated_at > (SELECT MAX(updated_at) FROM target_table)
-- Requires index on updated_at
```

### Partition Pruning
```sql
-- BigQuery partition pruning
SELECT *
FROM partitioned_table
WHERE DATE(timestamp_column) = '2024-01-15'  -- ✅ Scans only one partition

-- ❌ No partition pruning (scans all)
SELECT *
FROM partitioned_table
WHERE timestamp_column BETWEEN '2024-01-15 00:00:00' AND '2024-01-15 23:59:59'
```

### Cluster Key Usage
```sql
-- Snowflake: Use cluster keys in WHERE clause
SELECT *
FROM clustered_table
WHERE customer_id = 12345  -- ✅ Uses cluster key
  AND region = 'US'        -- ✅ Uses cluster key

-- ❌ Not using cluster keys (full scan)
SELECT *
FROM clustered_table
WHERE random_column = 'value'
```

### Predicate Pushdown
```sql
-- ✅ Filter before join (smaller dataset)
WITH filtered_orders AS (
    SELECT *
    FROM orders
    WHERE order_date >= '2024-01-01'  -- Filter early
)
SELECT
    f.*,
    c.customer_name
FROM filtered_orders f
JOIN customers c ON f.customer_id = c.id

-- ❌ Filter after join (larger dataset)
SELECT
    o.*,
    c.customer_name
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.order_date >= '2024-01-01'  -- Filter late
```

### Join Optimization
```sql
-- ✅ Join smaller table first
FROM small_table s
LEFT JOIN large_table l ON s.id = l.small_table_id

-- ❌ Join larger table first
FROM large_table l
LEFT JOIN small_table s ON l.small_table_id = s.id

-- ✅ Use appropriate join type
INNER JOIN  -- When you need matching records only
LEFT JOIN   -- When you need all from left side
```

## dbt Model Optimization

### Materialization Strategy
```sql
-- Use appropriate materialization
{{ config(materialized='view') }}       -- ✅ For simple transformations, low usage
{{ config(materialized='table') }}      -- ✅ For complex queries, high usage
{{ config(materialized='incremental') }}-- ✅ For large tables, frequent updates
{{ config(materialized='ephemeral') }}  -- ✅ For CTEs in dependent models
```

### Incremental Model Performance
```sql
{{ config(
    materialized='incremental',
    unique_key='id',
    on_schema_change='sync_all_columns',
    incremental_strategy='merge',  -- or 'delete+insert', 'append'
) }}

-- ✅ Efficient: Uses indexed column
{% if is_incremental() %}
WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}

-- ❌ Inefficient: Scans entire source
{% if is_incremental() %}
WHERE id NOT IN (SELECT id FROM {{ this }})
{% endif %}
```

### Reduce Model Scope
```sql
-- ✅ Process only needed data
{{ config(materialized='incremental') }}

SELECT
    id,
    customer_id,
    amount,
    created_at
FROM {{ source('db', 'orders') }}
WHERE status != 'cancelled'  -- Exclude unnecessary data

{% if is_incremental() %}
  AND updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

## Warehouse-Specific Optimizations

### Snowflake
```sql
-- Use appropriate warehouse size
USE WAREHOUSE SMALL_WH;      -- Light queries
USE WAREHOUSE LARGE_WH;      -- Heavy transformations
USE WAREHOUSE X_LARGE_WH;    -- Batch processing

-- Cluster tables
ALTER TABLE large_table CLUSTER BY (customer_id, order_date);

-- Materialized views for aggregations
CREATE MATERIALIZED VIEW daily_sales AS
SELECT
    DATE(order_date) as date,
    SUM(amount) as total_sales
FROM orders
GROUP BY DATE(order_date);

-- Result caching (automatic)
-- Identical queries return cached results within 24 hours

-- Partition large tables
CREATE TABLE orders (
    id NUMBER,
    order_date DATE,
    amount NUMBER
)
CLUSTER BY (order_date);
```

### BigQuery
```sql
-- Partition tables
CREATE TABLE orders
PARTITION BY DATE(order_date)
CLUSTER BY customer_id, product_id
AS SELECT * FROM source_table;

-- Use partitioning in queries
SELECT *
FROM orders
WHERE DATE(order_date) BETWEEN '2024-01-01' AND '2024-01-31'
  AND customer_id IN (1, 2, 3);  -- Uses clustering

-- Materialized views
CREATE MATERIALIZED VIEW mv_daily_sales
AS
SELECT
    DATE(order_timestamp) as date,
    product_id,
    SUM(amount) as total_sales
FROM orders
GROUP BY date, product_id;

-- BI Engine (in-memory acceleration)
ALTER MATERIALIZED VIEW mv_daily_sales
SET OPTIONS(enable_refresh=true, refresh_interval_minutes=60);
```

### Redshift
```sql
-- Distribution keys
CREATE TABLE orders (
    order_id BIGINT,
    customer_id BIGINT,
    amount DECIMAL(10,2)
)
DISTSTYLE KEY
DISTKEY(customer_id)  -- Distribute by join key
SORTKEY(order_date);  -- Sort by filter key

-- Analyze tables
ANALYZE orders;

-- Vacuum tables
VACUUM DELETE ONLY orders;
VACUUM SORT ONLY orders;

-- Use COPY command for loading
COPY orders
FROM 's3://bucket/data/'
IAM_ROLE 'arn:aws:iam::123:role/RedshiftRole'
FORMAT AS PARQUET;
```

## Parallelization

### Airflow Parallelization
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

with DAG('parallel_processing', ...) as dag:

    # Process multiple tables in parallel
    tables = ['orders', 'customers', 'products', 'inventory']

    for table in tables:
        PythonOperator(
            task_id=f'process_{table}',
            python_callable=process_table,
            op_kwargs={'table': table},
            pool='heavy_compute',  # Limit concurrency
            pool_slots=1,
        )

    # Or use dynamic task mapping (Airflow 2.3+)
    from airflow.decorators import task

    @task
    def process_table_dynamic(table_name):
        # Process logic
        pass

    process_table_dynamic.expand(table_name=tables)
```

### dbt Parallelization
```bash
# Run with multiple threads
dbt run --threads 8

# Configure in dbt_project.yml
threads: 8  # Default for this project
```

```yaml
# profiles.yml
my_project:
  target: prod
  outputs:
    prod:
      type: snowflake
      threads: 16  # Max parallel model execution
      # Other config...
```

## Batch Processing

### Micro-Batching
```python
def process_in_batches(records, batch_size=1000):
    """Process large datasets in batches"""
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]

        # Process batch
        transformed = transform_batch(batch)

        # Load batch
        load_batch(transformed)

        # Commit after each batch
        db.commit()

        print(f"Processed {i + len(batch)} / {len(records)} records")
```

### Date-Based Batching
```sql
-- Process one day at a time
{% for date in date_range(start_date, end_date) %}
    INSERT INTO target_table
    SELECT * FROM source_table
    WHERE DATE(timestamp_column) = '{{ date }}'
    {{ "UNION ALL" if not loop.last }}
{% endfor %}
```

## Caching Strategies

### dbt Incremental Caching
```sql
-- Cache intermediate results
{{ config(
    materialized='incremental',
    on_schema_change='sync_all_columns'
) }}

-- Expensive calculation cached as incremental model
WITH expensive_calculation AS (
    SELECT
        customer_id,
        complex_aggregation(...) as metric
    FROM large_table
    {% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
)
SELECT * FROM expensive_calculation
```

### Warehouse Result Caching
```sql
-- Snowflake: Automatic result caching
-- Identical queries within 24 hours return cached results
-- No configuration needed

-- BigQuery: Cached results (24 hours)
-- Use cache:
SELECT * FROM large_table WHERE date = '2024-01-15'

-- Bypass cache:
SELECT * FROM large_table WHERE date = CURRENT_DATE()
```

## Memory Optimization

### Reduce Memory Footprint
```python
# ✅ Stream processing (low memory)
def process_large_file_streaming(file_path):
    with open(file_path, 'r') as f:
        for line in f:  # Read one line at a time
            record = json.loads(line)
            yield transform_record(record)

# ❌ Load entire file (high memory)
def process_large_file_all_at_once(file_path):
    with open(file_path, 'r') as f:
        all_records = json.load(f)  # Entire file in memory
        return [transform_record(r) for r in all_records]
```

### Use Generators
```python
# ✅ Generator (lazy evaluation)
def extract_records():
    for batch in fetch_batches():
        for record in batch:
            yield record

# Process without loading all into memory
for record in extract_records():
    process_record(record)
```

## Network & I/O Optimization

### Compression
```python
# Use compression for data transfer
import gzip
import json

# Write compressed
with gzip.open('data.json.gz', 'wt') as f:
    json.dump(data, f)

# Read compressed
with gzip.open('data.json.gz', 'rt') as f:
    data = json.load(f)

# SQL: Load compressed files
COPY table FROM 's3://bucket/data.csv.gz' GZIP;
```

### Columnar Formats
```python
# ✅ Parquet (efficient for analytics)
df.to_parquet('data.parquet', compression='snappy')

# Smaller file size, faster queries
# Only read needed columns
pd.read_parquet('data.parquet', columns=['id', 'amount'])

# ❌ CSV (larger, slower)
df.to_csv('data.csv')
```

## Monitoring & Profiling

### dbt Performance
```bash
# Run with timing
dbt run --profile perf_profile

# Check run_results.json
cat target/run_results.json | jq '.results[] | {model: .unique_id, time: .execution_time}'

# dbt Cloud: Use run history graphs
```

### SQL Query Plans
```sql
-- Snowflake
EXPLAIN SELECT * FROM large_table WHERE customer_id = 123;

-- BigQuery
SELECT * FROM large_table WHERE customer_id = 123
-- View execution plan in console

-- Postgres/Redshift
EXPLAIN ANALYZE SELECT * FROM large_table WHERE customer_id = 123;
```

### Airflow Task Performance
```python
from airflow.utils.log.logging_mixin import LoggingMixin
import time

def monitored_task(**context):
    """Task with performance monitoring"""
    logger = LoggingMixin().log

    start = time.time()

    # Your logic
    result = process_data()

    duration = time.time() - start

    logger.info(f"Task completed in {duration:.2f} seconds")
    logger.info(f"Processed {result['count']} records")
    logger.info(f"Rate: {result['count'] / duration:.2f} records/sec")

    return result
```

## Best Practices Checklist

- [ ] Use incremental loading for large tables
- [ ] Partition tables by date
- [ ] Cluster tables on filter/join columns
- [ ] Create indexes on foreign keys and timestamps
- [ ] Use appropriate data types (not VARCHAR(MAX) everywhere)
- [ ] Avoid SELECT * (specify columns)
- [ ] Filter early, join late
- [ ] Use materialized views for expensive aggregations
- [ ] Process in parallel when possible
- [ ] Compress data in transit and at rest
- [ ] Monitor query performance regularly
- [ ] Set appropriate warehouse/cluster size
- [ ] Use result caching
- [ ] Archive historical data

## Performance Metrics

### Key Metrics to Track
```sql
-- Query execution time
SELECT
    query_id,
    query_text,
    execution_time_ms,
    rows_scanned,
    bytes_scanned
FROM query_history
WHERE execution_time_ms > 10000  -- Slow queries (>10s)
ORDER BY execution_time_ms DESC;

-- Warehouse utilization (Snowflake)
SELECT
    warehouse_name,
    AVG(avg_running) as avg_concurrent_queries,
    SUM(credits_used) as total_credits
FROM warehouse_metering_history
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP)
GROUP BY warehouse_name;

-- Table scan efficiency
SELECT
    table_name,
    bytes_scanned,
    rows_scanned,
    bytes_scanned / NULLIF(rows_scanned, 0) as bytes_per_row
FROM table_scan_statistics
WHERE scan_date = CURRENT_DATE
ORDER BY bytes_scanned DESC;
```

## Resources

- **Snowflake Performance**: https://docs.snowflake.com/en/user-guide/performance
- **BigQuery Best Practices**: https://cloud.google.com/bigquery/docs/best-practices-performance
- **Redshift Performance**: https://docs.aws.amazon.com/redshift/latest/dg/c_designing-queries-best-practices.html
- **dbt Performance**: https://docs.getdbt.com/docs/deploy/performance
