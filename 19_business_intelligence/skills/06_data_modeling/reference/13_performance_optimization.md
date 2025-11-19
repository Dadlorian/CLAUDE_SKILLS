# Performance Optimization Patterns Reference

## Overview

Data warehouse performance optimization requires balancing query speed, load performance, storage efficiency, and maintainability. Optimize based on actual usage patterns, not theoretical scenarios.

**Principle**: Measure first, optimize second. Don't guess at bottlenecks.

---

## Query Performance Optimization

### 1. Partitioning

**Strategy**: Divide large tables into smaller, manageable pieces.

**Range Partitioning (Most Common)**:
```sql
-- Partition by month
CREATE TABLE FACT_SALES (
    sales_key BIGINT,
    date_key INTEGER NOT NULL,
    amount DECIMAL(12,2)
)
PARTITION BY RANGE (date_key) (
    PARTITION p202401 VALUES LESS THAN (20240201),
    PARTITION p202402 VALUES LESS THAN (20240301),
    PARTITION p202403 VALUES LESS THAN (20240401),
    ...
);
```

**Benefits**:
- **Partition Pruning**: Only scan relevant partitions
- **Parallel Processing**: Each partition processed separately
- **Easy Archival**: Drop old partitions
- **Faster Index Rebuilds**: Per partition instead of entire table

**Example Query Optimization**:
```sql
-- Without partitioning: Scans 1 billion rows
SELECT SUM(amount)
FROM FACT_SALES
WHERE date_key BETWEEN 20240601 AND 20240630;

-- With monthly partitioning: Scans only June partition (~80M rows)
-- Partition pruning automatically limits scan
```

**Partitioning Strategies**:
- **Monthly**: Most common for facts (balance between granularity and maintenance)
- **Daily**: High-volume transactional systems
- **Yearly**: Low-volume or historical data
- **Composite**: Partition by date, sub-partition by region/category

**Best Practices**:
- Partition on most frequently filtered column (usually date)
- Align partition boundaries with business calendar
- Automate partition creation (rolling window)
- Monitor partition sizes (avoid skew)

---

### 2. Aggregate Tables

**Strategy**: Pre-calculate common aggregations.

**Example**:
```sql
-- Atomic grain: 1 billion rows
FACT_SALES_TRANSACTION (line item level)

-- Daily aggregate: 365 days × 10,000 products = 3.65M rows
CREATE TABLE FACT_SALES_DAILY AS
SELECT
    date_key,
    product_key,
    store_key,
    COUNT(*) as transaction_count,
    SUM(quantity) as total_quantity,
    SUM(amount) as total_amount,
    AVG(unit_price) as avg_unit_price
FROM FACT_SALES_TRANSACTION
GROUP BY date_key, product_key, store_key;

-- Monthly aggregate: 12 months × 10,000 products = 120K rows
CREATE TABLE FACT_SALES_MONTHLY AS
SELECT
    month_key,
    product_key,
    store_key,
    SUM(transaction_count) as transaction_count,
    SUM(total_quantity) as total_quantity,
    SUM(total_amount) as total_amount,
    AVG(avg_unit_price) as avg_unit_price
FROM FACT_SALES_DAILY
GROUP BY month_key, product_key, store_key;
```

**Aggregate Navigation**:
```sql
-- BI tool or query rewrite logic:
-- User requests monthly sales → Use FACT_SALES_MONTHLY (fast)
-- User requests hourly sales → Use FACT_SALES_TRANSACTION (slower but only option)
```

**When to Create Aggregates**:
- Query pattern is predictable and frequent
- Aggregation involves many rows
- Calculation is expensive (complex joins, calculations)
- Users need sub-second response

**Maintenance**:
```sql
-- Incremental update (append yesterday's data)
INSERT INTO FACT_SALES_DAILY
SELECT
    date_key,
    product_key,
    store_key,
    COUNT(*),
    SUM(quantity),
    SUM(amount),
    AVG(unit_price)
FROM FACT_SALES_TRANSACTION
WHERE date_key = (CURRENT_DATE - 1)
GROUP BY date_key, product_key, store_key;
```

---

### 3. Materialized Views

**Definition**: Physically stored query results, refreshed periodically.

**Example (PostgreSQL)**:
```sql
CREATE MATERIALIZED VIEW mv_sales_by_category AS
SELECT
    d.year,
    d.quarter,
    p.category,
    COUNT(*) as sales_count,
    SUM(f.amount) as total_sales
FROM FACT_SALES f
JOIN DIM_DATE d ON f.date_key = d.date_key
JOIN DIM_PRODUCT p ON f.product_key = p.product_key
GROUP BY d.year, d.quarter, p.category;

-- Create index on materialized view
CREATE INDEX idx_mv_sales_cat ON mv_sales_by_category(year, quarter, category);

-- Refresh (can be scheduled)
REFRESH MATERIALIZED VIEW mv_sales_by_category;
```

**Example (SQL Server Indexed View)**:
```sql
CREATE VIEW vw_sales_by_category
WITH SCHEMABINDING
AS
SELECT
    d.year,
    d.quarter,
    p.category,
    COUNT_BIG(*) as sales_count,
    SUM(f.amount) as total_sales
FROM dbo.FACT_SALES f
JOIN dbo.DIM_DATE d ON f.date_key = d.date_key
JOIN dbo.DIM_PRODUCT p ON f.product_key = p.product_key
GROUP BY d.year, d.quarter, p.category;

-- Index the view (makes it materialized)
CREATE UNIQUE CLUSTERED INDEX idx_vw_sales_cat
ON vw_sales_by_category(year, quarter, category);
```

**Benefits**:
- Transparent to users (query optimizer uses automatically)
- Complex joins pre-computed
- Aggregations pre-calculated

**Drawbacks**:
- Storage overhead
- Refresh latency
- Maintenance complexity

---

### 4. Columnstore Indexes

**Strategy**: Store data by column instead of row.

**Implementation (SQL Server)**:
```sql
-- Clustered columnstore (entire table)
CREATE CLUSTERED COLUMNSTORE INDEX cci_sales
ON FACT_SALES;
```

**How It Works**:
```
Traditional row storage:
[Row 1: date=2024-06-15, product=P123, amount=100]
[Row 2: date=2024-06-15, product=P456, amount=250]

Columnstore:
[date:    2024-06-15, 2024-06-15, ...]
[product: P123, P456, ...]
[amount:  100, 250, ...]
```

**Benefits**:
- **Compression**: 10x typical compression ratio
- **Scan Performance**: Read only needed columns
- **Aggregation**: Vectorized processing (batch mode)
- **Storage**: Significantly reduced

**When to Use**:
- Large fact tables (>10M rows)
- Analytical queries (scans and aggregations)
- Read-mostly workloads
- Data warehouse facts

**When NOT to Use**:
- Small tables
- OLTP workloads (frequent updates)
- Singleton lookups by key

---

### 5. Summary Tables at Multiple Grains

**Strategy**: Create multiple levels of aggregation.

**Example Hierarchy**:
```
FACT_SALES_TRANSACTION (atomic: 1B rows)
    ↓
FACT_SALES_HOURLY (10M rows)
    ↓
FACT_SALES_DAILY (3.6M rows)
    ↓
FACT_SALES_MONTHLY (120K rows)
    ↓
FACT_SALES_YEARLY (10K rows)
```

**Query Routing**:
```sql
-- User needs yearly totals → Use FACT_SALES_YEARLY (10K rows)
-- User needs daily breakdown → Use FACT_SALES_DAILY (3.6M rows)
-- User needs transaction detail → Use FACT_SALES_TRANSACTION (1B rows)
```

**Build Process**:
```sql
-- Build from most atomic to most aggregated
FACT_SALES_TRANSACTION (source system)
    ↓ aggregate
FACT_SALES_DAILY (aggregate from transaction)
    ↓ aggregate
FACT_SALES_MONTHLY (aggregate from daily, not transaction)
    ↓ aggregate
FACT_SALES_YEARLY (aggregate from monthly)
```

---

## ETL Performance Optimization

### 1. Bulk Loading

**Strategy**: Use database bulk load utilities instead of INSERT statements.

**Example (PostgreSQL COPY)**:
```sql
-- Slow: Row-by-row inserts
INSERT INTO FACT_SALES VALUES (1, ...);
INSERT INTO FACT_SALES VALUES (2, ...);
-- 1M rows = hours

-- Fast: Bulk load
COPY FACT_SALES FROM '/path/to/data.csv'
WITH (FORMAT CSV, HEADER TRUE);
-- 1M rows = minutes
```

**Example (SQL Server BULK INSERT)**:
```sql
BULK INSERT FACT_SALES
FROM '/path/to/data.csv'
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK,
    ROWS_PER_BATCH = 100000
);
```

**Best Practices**:
- Use native bulk load utilities
- Disable indexes before bulk load, rebuild after
- Use minimal logging mode
- Batch size: 10K-100K rows
- Parallel streams for very large loads

---

### 2. Incremental Loading

**Strategy**: Load only changed data, not full extract.

**Change Data Capture (CDC)**:
```sql
-- Source system tracks changes
SOURCE.CUSTOMER_CDC
- operation (I=Insert, U=Update, D=Delete)
- change_timestamp
- customer_id
- changed_columns...

-- ETL loads only CDC records since last load
SELECT *
FROM SOURCE.CUSTOMER_CDC
WHERE change_timestamp > (SELECT MAX(last_load_timestamp) FROM ETL.LOAD_LOG);
```

**Timestamp-Based Incremental**:
```sql
-- Extract only changed records
SELECT *
FROM SOURCE.ORDERS
WHERE modified_date > (SELECT MAX(load_date) FROM DW.ETL_LOG);
```

**Key-Based Incremental**:
```sql
-- Extract only new records
SELECT *
FROM SOURCE.ORDERS
WHERE order_id > (SELECT MAX(source_order_id) FROM DW.FACT_ORDERS);
```

---

### 3. Parallel Processing

**Strategy**: Process multiple data streams simultaneously.

**Parallel Extraction**:
```sql
-- Split extraction by partition
Thread 1: SELECT * FROM SOURCE.ORDERS WHERE region = 'North'
Thread 2: SELECT * FROM SOURCE.ORDERS WHERE region = 'South'
Thread 3: SELECT * FROM SOURCE.ORDERS WHERE region = 'East'
Thread 4: SELECT * FROM SOURCE.ORDERS WHERE region = 'West'
```

**Parallel Loading**:
```sql
-- Load different tables in parallel
Thread 1: Load DIM_CUSTOMER
Thread 2: Load DIM_PRODUCT
Thread 3: Load DIM_STORE
-- All dimensions done before facts

Thread 4: Load FACT_SALES partition 1
Thread 5: Load FACT_SALES partition 2
Thread 6: Load FACT_SALES partition 3
```

---

### 4. Staging Table Strategy

**Strategy**: Land data in staging first, then transform.

**Process**:
```sql
-- Step 1: Fast bulk load to staging (no indexes, no constraints)
CREATE TABLE STG_ORDERS (LIKE SOURCE.ORDERS);
BULK INSERT INTO STG_ORDERS...;

-- Step 2: Transform in staging
UPDATE STG_ORDERS SET standardized_name = UPPER(TRIM(customer_name));

-- Step 3: Load to target with business logic
INSERT INTO FACT_ORDERS
SELECT
    o.order_id,
    d.date_key,
    c.customer_key,
    ...
FROM STG_ORDERS o
JOIN DIM_DATE d ON o.order_date = d.date
JOIN DIM_CUSTOMER c ON o.customer_id = c.customer_id;

-- Step 4: Truncate staging
TRUNCATE TABLE STG_ORDERS;
```

---

### 5. Batch Processing

**Strategy**: Process records in batches, not one-by-one.

**Bad (Row-by-Row)**:
```sql
FOR EACH customer IN staging.customers LOOP
    INSERT INTO DIM_CUSTOMER VALUES (customer.*)
END LOOP
-- 1M customers = 1M separate inserts (hours)
```

**Good (Set-Based)**:
```sql
INSERT INTO DIM_CUSTOMER
SELECT * FROM staging.customers;
-- 1M customers = 1 insert (minutes)
```

---

## Storage Optimization

### 1. Compression

**Enable Compression**:
```sql
-- SQL Server: Page compression
ALTER TABLE FACT_SALES
REBUILD WITH (DATA_COMPRESSION = PAGE);

-- PostgreSQL: TOAST compression (automatic for large values)
ALTER TABLE FACT_SALES ALTER COLUMN description SET STORAGE EXTENDED;

-- Columnstore: Compression automatic
CREATE CLUSTERED COLUMNSTORE INDEX ON FACT_SALES;
```

**Benefits**:
- Reduced storage costs (50-90% savings)
- Reduced I/O (less data to read)
- Faster queries (less data to scan)

**Trade-offs**:
- CPU overhead for compression/decompression
- Usually worth it for data warehouses

---

### 2. Vertical Partitioning

**Strategy**: Split wide tables into multiple narrower tables.

**Problem**: Wide dimension with infrequently used columns
```sql
DIM_CUSTOMER (100 columns)
- customer_key
- customer_name
- ... (98 other columns, rarely used)
```

**Solution**: Split into core and extended
```sql
DIM_CUSTOMER (10 frequently used columns)
- customer_key
- customer_id
- customer_name
- customer_segment
- ...

DIM_CUSTOMER_EXTENDED (90 rarely used columns)
- customer_key (FK to DIM_CUSTOMER)
- detailed_demographics
- ...
```

---

### 3. Archive Old Data

**Strategy**: Move old data to archive tables or separate database.

**Example**:
```sql
-- Active data (last 2 years)
FACT_SALES (500M rows)

-- Archive (older than 2 years)
FACT_SALES_ARCHIVE (2B rows, on slower/cheaper storage)

-- View combining both
CREATE VIEW FACT_SALES_ALL AS
SELECT * FROM FACT_SALES
UNION ALL
SELECT * FROM FACT_SALES_ARCHIVE;
```

**Archival Process**:
```sql
-- Monthly: Move old data to archive
INSERT INTO FACT_SALES_ARCHIVE
SELECT * FROM FACT_SALES
WHERE date_key < (CURRENT_DATE - INTERVAL '2 years');

DELETE FROM FACT_SALES
WHERE date_key < (CURRENT_DATE - INTERVAL '2 years');
```

---

## Query Optimization Techniques

### 1. Avoid SELECT *

**Bad**:
```sql
SELECT * FROM FACT_SALES;
-- Retrieves all columns, even if only need 2
```

**Good**:
```sql
SELECT date_key, SUM(amount)
FROM FACT_SALES
GROUP BY date_key;
-- Only reads needed columns (especially important with columnstore)
```

---

### 2. Filter Early

**Bad**:
```sql
SELECT
    p.product_name,
    SUM(f.amount)
FROM FACT_SALES f
JOIN DIM_PRODUCT p ON f.product_key = p.product_key
JOIN DIM_DATE d ON f.date_key = d.date_key
WHERE d.year = 2024  -- Filter AFTER join
GROUP BY p.product_name;
```

**Good**:
```sql
SELECT
    p.product_name,
    SUM(f.amount)
FROM FACT_SALES f
JOIN DIM_PRODUCT p ON f.product_key = p.product_key
JOIN (SELECT date_key FROM DIM_DATE WHERE year = 2024) d  -- Filter BEFORE join
    ON f.date_key = d.date_key
GROUP BY p.product_name;
```

---

### 3. Use Appropriate JOIN Types

**INNER JOIN** (when you need matching records only):
```sql
SELECT ... FROM FACT_SALES f
INNER JOIN DIM_CUSTOMER c ON f.customer_key = c.customer_key;
```

**LEFT JOIN** (when you need all fact records):
```sql
-- Usually avoid in DW (all FKs should have matching dimension records)
-- If needed, indicates data quality issue
```

---

### 4. Leverage Query Hints/Optimizer Directives

**SQL Server Hints**:
```sql
-- Force specific index
SELECT ... FROM FACT_SALES WITH (INDEX(idx_sales_date))

-- Force parallel execution
SELECT ... FROM FACT_SALES OPTION (MAXDOP 8)
```

**Oracle Hints**:
```sql
-- Use bitmap index
SELECT /*+ INDEX(f idx_sales_product_bitmap) */ ...

-- Parallel query
SELECT /*+ PARALLEL(f 8) */ ...
```

---

### 5. Analyze Execution Plans

**Key Metrics**:
- Table scans vs index seeks
- Join algorithms (nested loop, hash, merge)
- Estimated vs actual rows
- CPU time, I/O time
- Parallel operations

**Common Issues**:
- Missing index → full table scan
- Outdated statistics → wrong execution plan
- Implicit conversions → no index usage
- Too many joins → complexity

---

## Monitoring and Tuning

### Performance Metrics

**Query Performance**:
```sql
-- SQL Server: Find slow queries
SELECT
    qs.total_elapsed_time / qs.execution_count as avg_elapsed_time,
    qs.total_worker_time / qs.execution_count as avg_cpu_time,
    qs.total_logical_reads / qs.execution_count as avg_logical_reads,
    SUBSTRING(qt.text, qs.statement_start_offset/2, qs.statement_end_offset/2) as query_text
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) qt
ORDER BY avg_elapsed_time DESC;
```

**Index Usage**:
```sql
-- Find unused indexes
SELECT
    OBJECT_NAME(i.object_id) as table_name,
    i.name as index_name,
    s.user_seeks + s.user_scans + s.user_lookups as total_reads,
    s.user_updates as total_writes
FROM sys.indexes i
LEFT JOIN sys.dm_db_index_usage_stats s
    ON i.object_id = s.object_id AND i.index_id = s.index_id
WHERE total_reads = 0 AND s.user_updates > 0;
```

**ETL Performance**:
```sql
-- Track load times
CREATE TABLE ETL_LOG (
    load_id BIGINT PRIMARY KEY,
    table_name VARCHAR(100),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    rows_inserted INTEGER,
    rows_updated INTEGER,
    duration_seconds INTEGER,
    status VARCHAR(20)
);
```

---

## Best Practices Summary

### Design Phase
1. **Atomic grain** for flexibility, aggregates for performance
2. **Partitioning** strategy for large tables
3. **Indexing** strategy per table type
4. **Compression** where beneficial

### ETL Phase
1. **Bulk loading** for large volumes
2. **Incremental** extraction and loading
3. **Parallel** processing where possible
4. **Batch** operations (set-based, not row-by-row)
5. **Staging** tables for transformation

### Query Phase
1. **Aggregate** tables for common patterns
2. **Materialized views** for complex queries
3. **Column selection** (not SELECT *)
4. **Early filtering** in WHERE clauses
5. **Execution plan** analysis

### Maintenance Phase
1. **Monitor** query and ETL performance
2. **Update** statistics regularly
3. **Rebuild** indexes periodically
4. **Archive** old data
5. **Review** and optimize continuously

---

## Performance Tuning Checklist

- [ ] Large fact tables partitioned by date
- [ ] Appropriate indexes created (bitmap, columnstore, B-tree)
- [ ] Statistics updated regularly
- [ ] Aggregate tables for common queries
- [ ] Compression enabled where beneficial
- [ ] ETL using bulk load operations
- [ ] Incremental loading (not full refresh)
- [ ] Parallel processing for large loads
- [ ] Query execution plans analyzed
- [ ] Slow queries identified and optimized
- [ ] Index usage monitored
- [ ] Old data archived
- [ ] Performance metrics tracked over time
