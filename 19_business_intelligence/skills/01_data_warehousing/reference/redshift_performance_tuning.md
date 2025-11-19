# Redshift Performance Tuning Reference

Quick reference for Amazon Redshift performance optimization, including distribution styles, sort keys, and query tuning.

## Table Design

### Distribution Styles

```sql
-- EVEN distribution (default) - round-robin
CREATE TABLE events (
    event_id BIGINT,
    event_data VARCHAR(1000)
)
DISTSTYLE EVEN;

-- KEY distribution - distribute by specific column
CREATE TABLE orders (
    order_id BIGINT,
    customer_id BIGINT,
    order_date DATE
)
DISTKEY(customer_id);  -- Co-locate with customers table

-- ALL distribution - replicate to all nodes (small dimension tables)
CREATE TABLE countries (
    country_code CHAR(2),
    country_name VARCHAR(100)
)
DISTSTYLE ALL;

-- AUTO distribution - let Redshift decide
CREATE TABLE products (
    product_id BIGINT,
    product_name VARCHAR(200)
)
DISTSTYLE AUTO;
```

**Distribution Style Selection:**
- **EVEN**: Default, use when no JOIN or GROUP BY patterns
- **KEY**: Large fact tables, join frequently with dimension tables
- **ALL**: Small dimension tables (< 3M rows), frequently joined
- **AUTO**: Let Redshift optimize based on table size and usage

### Sort Keys

```sql
-- Single column sort key
CREATE TABLE orders (
    order_id BIGINT,
    order_date DATE,
    customer_id BIGINT
)
SORTKEY(order_date);

-- Compound sort key (prefix matching)
CREATE TABLE events (
    event_id BIGINT,
    event_date DATE,
    event_time TIMESTAMP,
    user_id BIGINT
)
COMPOUND SORTKEY(event_date, event_time);

-- Interleaved sort key (equal weight to all columns)
CREATE TABLE customer_events (
    customer_id BIGINT,
    event_date DATE,
    event_type VARCHAR(50)
)
INTERLEAVED SORTKEY(customer_id, event_date, event_type);

-- No sort key
CREATE TABLE staging_data (...)
DISTSTYLE EVEN;  -- No SORTKEY for staging tables
```

**Sort Key Selection:**
- **Compound**: Use for common query patterns with specific column order
- **Interleaved**: Use when filtering on different column combinations
- **Single**: Use for time-series data (ORDER BY date/timestamp)
- **None**: Staging tables, no common query patterns

### Column Encoding (Compression)

```sql
-- Let Redshift choose encoding automatically
CREATE TABLE orders (
    order_id BIGINT ENCODE AZ64,
    customer_id BIGINT ENCODE AZ64,
    order_date DATE ENCODE AZ64,
    status VARCHAR(20) ENCODE LZO,
    total DECIMAL(10,2) ENCODE AZ64
);

-- Analyze table for encoding recommendations
ANALYZE COMPRESSION orders;

-- Common encodings:
-- AZ64: Good for all numeric types (default for SORTKEY columns)
-- LZO: Good for VARCHAR/CHAR
-- ZSTD: Good compression ratio for all types
-- DELTA: Good for sequential numbers (IDs)
-- RUNLENGTH: Good for repetitive data
-- RAW: No compression (use for highly unique data)
```

### Constraints

```sql
-- Primary key (not enforced, but used by query optimizer)
CREATE TABLE customers (
    customer_id BIGINT PRIMARY KEY,
    customer_name VARCHAR(100)
);

-- Foreign key (not enforced, informational only)
CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT REFERENCES customers(customer_id)
);

-- NOT NULL constraint (enforced)
CREATE TABLE products (
    product_id BIGINT NOT NULL,
    product_name VARCHAR(200) NOT NULL
);
```

## Query Optimization

### EXPLAIN Plans

```sql
-- View query execution plan
EXPLAIN
SELECT c.customer_name, COUNT(*) as order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= '2024-01-01'
GROUP BY c.customer_name;

-- Look for:
-- DS_DIST_ALL_NONE: No redistribution (good!)
-- DS_BCAST_INNER: Broadcasting small table (good for small dims)
-- DS_DIST_BOTH: Redistributing both tables (expensive!)
-- Nested Loop: Can be expensive, prefer Hash Join
```

### JOIN Optimization

```sql
-- ❌ BAD: Large table redistribution
SELECT *
FROM large_fact_table f
JOIN dimension_table d ON f.dim_id = d.dim_id;

-- ✅ GOOD: Use matching DISTKEY
CREATE TABLE fact_table (...) DISTKEY(customer_id);
CREATE TABLE customers (...) DISTKEY(customer_id);

-- ✅ GOOD: Use DISTSTYLE ALL for small dimensions
CREATE TABLE dimension_table (...) DISTSTYLE ALL;

-- ✅ GOOD: Join order (smaller table last for broadcast)
SELECT f.*
FROM large_fact f
JOIN small_dim d ON f.dim_id = d.dim_id;
```

### WHERE Clause Optimization

```sql
-- ✅ GOOD: Filter on SORTKEY columns
SELECT *
FROM orders
WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31';

-- ✅ GOOD: Use zone maps (first column of sort key)
SELECT *
FROM events
WHERE event_date = '2024-01-15'
  AND event_type = 'purchase';  -- event_date is first in SORTKEY

-- ❌ BAD: Functions on columns prevent zone map usage
SELECT *
FROM orders
WHERE DATE_TRUNC('month', order_date) = '2024-01-01';

-- ✅ GOOD: Avoid functions on filtered columns
SELECT *
FROM orders
WHERE order_date >= '2024-01-01' AND order_date < '2024-02-01';
```

### GROUP BY Optimization

```sql
-- ✅ GOOD: Group by DISTKEY to avoid redistribution
SELECT customer_id, SUM(total)
FROM orders
GROUP BY customer_id;  -- customer_id is DISTKEY

-- Use APPROXIMATE COUNT DISTINCT for large datasets
SELECT
    customer_id,
    APPROXIMATE COUNT(DISTINCT product_id) as unique_products
FROM order_items
GROUP BY customer_id;
```

## Workload Management (WLM)

### WLM Queue Configuration

```sql
-- View current WLM configuration
SELECT * FROM stv_wlm_classification_config;

-- View query queue assignment
SELECT query, queue, slot_count
FROM stl_wlm_query
WHERE userid = 100
ORDER BY query DESC
LIMIT 10;

-- Set query group for session
SET query_group TO 'reporting';

-- Reset query group
RESET query_group;
```

**WLM Best Practices:**
1. Create separate queues for different workload types
2. ETL queue: Higher memory, lower concurrency
3. Reporting queue: Lower memory, higher concurrency
4. Short query acceleration (SQA) for fast queries
5. Concurrency scaling for read-heavy workloads

### Short Query Acceleration (SQA)

```sql
-- Enabled in WLM parameter group
-- Automatically runs short queries in dedicated queue
-- Bypasses WLM queues for queries < 20 seconds

-- View SQA queries
SELECT query, elapsed, queue_name
FROM STL_WLM_QUERY
WHERE queue_name = 'Short query queue'
ORDER BY query DESC
LIMIT 100;
```

### Concurrency Scaling

```sql
-- Enabled in WLM configuration
-- Automatically adds cluster capacity for read queries
-- Only pay when scaling is active

-- View concurrency scaling usage
SELECT
    TO_CHAR(start_time, 'YYYY-MM-DD HH24:MI') as time_period,
    SUM(concurrency_scaling_seconds) / 3600.0 as scaling_hours
FROM svl_concurrency_scaling_usage
WHERE start_time >= DATEADD(day, -7, CURRENT_DATE)
GROUP BY 1
ORDER BY 1;
```

## Vacuum and Analyze

### VACUUM

```sql
-- Full vacuum (reclaim space and sort)
VACUUM orders;

-- Vacuum only (skip sort)
VACUUM DELETE ONLY orders;

-- Vacuum sort only
VACUUM SORT ONLY orders;

-- Vacuum to a threshold
VACUUM orders TO 95 PERCENT;

-- Vacuum boost option (more intensive)
VACUUM BOOST orders;

-- Check vacuum progress
SELECT
    table_name,
    unsorted_pct,
    vacuum_sort_benefit
FROM svv_table_info
WHERE unsorted_pct > 10
ORDER BY vacuum_sort_benefit DESC;
```

### ANALYZE

```sql
-- Analyze table statistics
ANALYZE orders;

-- Analyze specific columns
ANALYZE orders (customer_id, order_date);

-- Analyze with threshold
ANALYZE orders PREDICATE COLUMNS;

-- Check if analyze is needed
SELECT
    table_name,
    stats_off
FROM svv_table_info
WHERE stats_off > 10
ORDER BY stats_off DESC;
```

### Automated Vacuum and Analyze

```sql
-- Enable automatic VACUUM DELETE
-- (Enabled by default in Redshift)

-- Enable automatic ANALYZE
-- (Enabled by default in Redshift)

-- Check automatic vacuum/analyze activity
SELECT
    table_name,
    last_vacuum_time,
    last_analyze_time
FROM svv_table_info
ORDER BY last_vacuum_time DESC;
```

## Data Loading

### COPY Command

```sql
-- Load from S3 (fastest method)
COPY orders
FROM 's3://mybucket/data/orders/'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftRole'
FORMAT AS PARQUET;

-- Load CSV with options
COPY customers
FROM 's3://mybucket/data/customers.csv'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftRole'
FORMAT AS CSV
DELIMITER ','
IGNOREHEADER 1
DATEFORMAT 'YYYY-MM-DD'
TIMEFORMAT 'YYYY-MM-DD HH:MI:SS'
ACCEPTINVCHARS
TRUNCATECOLUMNS
MAXERROR 100;

-- Load with manifest
COPY events
FROM 's3://mybucket/manifest.json'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftRole'
MANIFEST
FORMAT AS JSON 'auto';

-- Load with compression
COPY orders
FROM 's3://mybucket/orders.gz'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftRole'
GZIP;
```

### COPY Optimization

```sql
-- Use multiple files (1 per slice recommended)
-- Number of files = multiple of cluster slices
-- Example: 8-node cluster = 16 slices = 16+ files

-- Use columnar formats (Parquet, ORC) when possible
COPY events
FROM 's3://mybucket/events/'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftRole'
FORMAT AS PARQUET;

-- Use COMPUPDATE OFF after initial load
COPY orders
FROM 's3://mybucket/orders/'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftRole'
COMPUPDATE OFF;

-- Check COPY errors
SELECT * FROM stl_load_errors
ORDER BY starttime DESC
LIMIT 10;
```

### UNLOAD Data

```sql
-- Unload to S3
UNLOAD ('SELECT * FROM orders WHERE order_date >= ''2024-01-01''')
TO 's3://mybucket/unload/orders_'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftRole'
PARQUET
PARALLEL ON
ALLOWOVERWRITE;

-- Unload with partitioning
UNLOAD ('SELECT * FROM orders')
TO 's3://mybucket/unload/orders/'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftRole'
PARTITION BY (order_date)
PARQUET;
```

## Performance Monitoring

### Query Performance

```sql
-- Slowest queries
SELECT
    query,
    TRIM(querytxt) as sql,
    starttime,
    endtime,
    DATEDIFF(seconds, starttime, endtime) as duration_seconds
FROM stl_query
WHERE userid > 1
  AND starttime >= DATEADD(day, -1, CURRENT_DATE)
ORDER BY duration_seconds DESC
LIMIT 20;

-- Queries with disk-based operations (spills to disk)
SELECT
    query,
    step,
    rows,
    bytes,
    workmem,
    is_diskbased
FROM svl_query_summary
WHERE is_diskbased = 't'
  AND query IN (
      SELECT query FROM stl_query
      WHERE userid > 1
      AND starttime >= DATEADD(day, -1, CURRENT_DATE)
  )
ORDER BY query DESC;

-- Queue wait times
SELECT
    query,
    queue_start_time,
    exec_start_time,
    DATEDIFF(seconds, queue_start_time, exec_start_time) as queue_seconds
FROM stl_wlm_query
WHERE queue_seconds > 10
ORDER BY queue_seconds DESC
LIMIT 20;
```

### Table Statistics

```sql
-- Table sizes and information
SELECT
    TRIM(pgn.nspname) AS schema_name,
    TRIM(a.name) AS table_name,
    ((b.mbytes / part.total::DECIMAL) * 100)::DECIMAL(5, 2) AS table_pct_of_total,
    b.mbytes,
    b.unsorted_mbytes,
    ((b.unsorted_mbytes / b.mbytes::DECIMAL) * 100)::DECIMAL(5, 2) AS pct_unsorted
FROM (
    SELECT
        tbl,
        COUNT(*) AS total
    FROM stv_blocklist
    GROUP BY tbl
) part
JOIN (
    SELECT
        tbl,
        SUM(DECODE(unsorted, 1, 1, 0)) AS unsorted_mbytes,
        COUNT(*) AS mbytes
    FROM stv_blocklist
    GROUP BY tbl
) b ON part.tbl = b.tbl
JOIN stv_tbl_perm a ON a.id = b.tbl
JOIN pg_namespace pgn ON pgn.oid = a.nspname_oid
WHERE pgn.nspname NOT IN ('pg_catalog', 'information_schema')
ORDER BY b.mbytes DESC;

-- Table skew (data distribution across nodes)
SELECT
    TRIM(name) AS table_name,
    slice,
    num_values,
    minvalue,
    maxvalue
FROM svv_diskusage
WHERE name IN ('large_table')
ORDER BY slice;
```

### Disk Space

```sql
-- Disk space usage by table
SELECT
    TRIM(pgdb.datname) AS database,
    TRIM(pgn.nspname) AS schema,
    TRIM(a.name) AS table,
    ((b.mbytes / 1024.0))::DECIMAL(10, 2) AS size_gb
FROM (
    SELECT db_id, id, name
    FROM stv_tbl_perm
) a
JOIN pg_database pgdb ON pgdb.oid = a.db_id
JOIN pg_namespace pgn ON pgn.oid = a.nspname_oid
JOIN (
    SELECT tbl, COUNT(*) AS mbytes
    FROM stv_blocklist
    GROUP BY tbl
) b ON a.id = b.tbl
ORDER BY size_gb DESC
LIMIT 50;
```

## Best Practices

### Table Design
1. Choose appropriate **DISTKEY** for large fact tables
2. Use **DISTSTYLE ALL** for small dimension tables
3. Use **SORTKEY** on frequently filtered columns (esp. dates)
4. Let Redshift choose **column encoding** (ANALYZE COMPRESSION)
5. Define **PRIMARY KEY** and **FOREIGN KEY** constraints (for optimizer)

### Query Optimization
1. Filter on **SORTKEY** columns when possible
2. Avoid functions on filtered columns
3. Use **APPROXIMATE** functions for large aggregations
4. Join on **DISTKEY** columns to avoid redistribution
5. Review **EXPLAIN** plans for expensive operations

### Maintenance
1. Run **VACUUM** when unsorted_pct > 5%
2. Run **ANALYZE** after significant data changes
3. Enable **automatic VACUUM and ANALYZE**
4. Monitor **table statistics** regularly
5. Check for **data skew** on large tables

### Loading Data
1. Use **COPY** from S3 (fastest method)
2. Load **compressed files** (gzip, Parquet, ORC)
3. Use **multiple files** (1+ per slice)
4. Use **columnar formats** when possible
5. Enable **COMPUPDATE** only on first load

### WLM Configuration
1. Create separate queues for different workloads
2. Enable **Short Query Acceleration** (SQA)
3. Enable **Concurrency Scaling** for read-heavy workloads
4. Monitor **queue wait times**
5. Adjust **memory allocation** based on query patterns

### Monitoring
1. Review slowest queries daily
2. Monitor disk-based operations (spills)
3. Check queue wait times
4. Monitor disk space usage
5. Track concurrency scaling costs
