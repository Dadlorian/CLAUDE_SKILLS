# Indexing Strategies for Data Warehouses Reference

## Overview

Indexing strategies for data warehouses differ significantly from OLTP systems. Data warehouses prioritize query performance over update performance, handle large volumes, and have predictable query patterns.

**Key Principle**: Index for query patterns, not for every column.

---

## Index Types for Data Warehousing

### 1. B-Tree Indexes (Standard)

**Definition**: Traditional balanced tree structure. Default index type in most databases.

**Best For**:
- Primary keys
- Foreign keys (in OLTP-style dimensions)
- High-cardinality columns
- Range queries
- Equality searches

**Structure**:
```sql
CREATE INDEX idx_customer_id ON DIM_CUSTOMER(customer_id);
CREATE INDEX idx_product_category ON DIM_PRODUCT(product_category, product_subcategory);
```

**Characteristics**:
- Good for selective queries (returns small % of rows)
- Poor for low-cardinality columns
- Updates expensive (insert/update/delete)
- Moderate storage overhead

**Use Cases in DW**:
- Dimension table primary keys
- Dimension table natural business keys
- Date range queries on dimensions
- High-cardinality lookup columns

---

### 2. Bitmap Indexes

**Definition**: Uses bit vectors to represent presence/absence of values. Highly efficient for low to medium cardinality columns in read-heavy environments.

**Best For**:
- Low-cardinality columns (few distinct values)
- Data warehouses (read-heavy, few updates)
- Multiple index intersection queries
- Fact table foreign keys
- Boolean/flag columns

**Example**:
```sql
-- Oracle bitmap indexes on fact table
CREATE BITMAP INDEX idx_sales_date ON FACT_SALES(date_key);
CREATE BITMAP INDEX idx_sales_product ON FACT_SALES(product_key);
CREATE BITMAP INDEX idx_sales_customer ON FACT_SALES(customer_key);
CREATE BITMAP INDEX idx_sales_store ON FACT_SALES(store_key);
CREATE BITMAP INDEX idx_sales_promotion ON FACT_SALES(promotion_key);

-- Query using multiple indexed columns
SELECT SUM(sales_amount)
FROM FACT_SALES
WHERE date_key BETWEEN 20240601 AND 20240630  -- Uses bitmap index
  AND store_key = 15  -- Uses bitmap index
  AND promotion_key = 5;  -- Uses bitmap index
-- Database can AND the bitmaps together very efficiently
```

**How Bitmap Indexes Work**:
```
For column "gender" with values (M, F):

Row | Gender | Bitmap M | Bitmap F
----|--------|----------|----------
1   | M      | 1        | 0
2   | F      | 0        | 1
3   | M      | 1        | 0
4   | F      | 0        | 1
5   | M      | 1        | 0

Query: WHERE gender = 'M' AND age_range = '25-34'
→ AND the bitmaps together: 10101 AND 11001 = 10001
→ Rows 1 and 5 match
```

**Advantages**:
- Extremely space-efficient
- Fast multi-column queries (bitmap AND/OR operations)
- Excellent for star schema queries
- Great for aggregations

**Disadvantages**:
- Slow for updates (entire bitmap must be rewritten)
- Inefficient for high-cardinality columns
- Not supported in all databases (Oracle, PostgreSQL, others)
- Lock contention on updates

**Best Practices**:
- Use on fact table foreign keys (date_key, product_key, etc.)
- Use on low-cardinality dimensions (status, type, category)
- Avoid on OLTP tables
- Rebuild periodically if bulk loading

---

### 3. Columnstore Indexes

**Definition**: Store data by column rather than by row. Optimized for analytical queries.

**Best For**:
- Large fact tables
- Analytical queries (aggregations, scans)
- Data warehouses
- Compression

**Example (SQL Server)**:
```sql
-- Clustered columnstore index (table stored as columnstore)
CREATE CLUSTERED COLUMNSTORE INDEX cci_sales
ON FACT_SALES;

-- Nonclustered columnstore index
CREATE NONCLUSTERED COLUMNSTORE INDEX ncci_sales
ON FACT_SALES (date_key, product_key, customer_key, sales_amount, quantity);
```

**How Columnstore Works**:
```
Row-based storage:
Row 1: [2024-06-15, P123, C456, 100.00, 2]
Row 2: [2024-06-15, P456, C789, 250.00, 1]
Row 3: [2024-06-16, P123, C456, 100.00, 2]

Column-based storage:
date_key:     [2024-06-15, 2024-06-15, 2024-06-16]
product_key:  [P123, P456, P123]
customer_key: [C456, C789, C456]
sales_amount: [100.00, 250.00, 100.00]
quantity:     [2, 1, 2]
```

**Advantages**:
- Extreme compression (10x typical)
- Fast aggregations (read only needed columns)
- Batch mode processing
- Excellent for scans of large tables

**Disadvantages**:
- Not good for singleton lookups
- Not good for frequent updates
- Requires sufficient memory
- Some query patterns slower than row storage

**Use Cases**:
- Large fact tables (millions+ rows)
- Aggregation-heavy queries
- Reporting and analytics
- Historical/archive data

---

### 4. Hash Indexes

**Definition**: Hash function maps keys to index locations. Fast equality searches.

**Best For**:
- Exact match lookups
- Equality joins
- Distributed/parallel databases

**Example (PostgreSQL, MySQL Memory tables)**:
```sql
CREATE INDEX idx_customer_email USING HASH ON DIM_CUSTOMER(email);
```

**Characteristics**:
- Very fast equality searches: WHERE email = 'john@example.com'
- Cannot support range queries: WHERE email > 'john@example.com' ❌
- Cannot support sorting
- Fixed size

**Use Cases in DW**:
- Distributed databases (Greenplum, Redshift)
- Hash joins in MPP systems
- Exact lookups on high-cardinality columns

---

### 5. Covering Indexes

**Definition**: Index includes all columns needed for a query (index-only scan possible).

**Example**:
```sql
-- Frequent query pattern
SELECT product_name, product_category, unit_price
FROM DIM_PRODUCT
WHERE product_category = 'Electronics';

-- Covering index (includes all SELECTed columns)
CREATE INDEX idx_product_covering
ON DIM_PRODUCT(product_category)
INCLUDE (product_name, unit_price);
-- Query can be satisfied entirely from index, no table lookup needed
```

**Benefits**:
- No table access needed (index-only scan)
- Faster query performance
- Reduced I/O

**Trade-offs**:
- Larger index size
- More expensive to maintain
- Only beneficial for specific query patterns

---

## Indexing Strategy by Table Type

### Dimension Tables

**Primary Key**:
```sql
-- Surrogate key (clustered or primary key)
CREATE UNIQUE INDEX pk_customer ON DIM_CUSTOMER(customer_key);
-- Clustered in SQL Server, primary in others
```

**Natural Business Key**:
```sql
-- For lookups during ETL and user queries
CREATE INDEX idx_customer_id ON DIM_CUSTOMER(customer_id);
CREATE INDEX idx_product_sku ON DIM_PRODUCT(sku);
```

**SCD Type 2 Columns**:
```sql
-- For current record lookups
CREATE INDEX idx_customer_current
ON DIM_CUSTOMER(customer_id, current_flag);

-- For point-in-time queries
CREATE INDEX idx_customer_dates
ON DIM_CUSTOMER(customer_id, effective_date, expiration_date);
```

**Frequently Filtered Attributes**:
```sql
-- Based on common query patterns
CREATE INDEX idx_customer_segment ON DIM_CUSTOMER(customer_segment);
CREATE INDEX idx_product_category ON DIM_PRODUCT(product_category);
```

**Complete Dimension Example**:
```sql
CREATE TABLE DIM_CUSTOMER (
    customer_key INTEGER PRIMARY KEY,  -- Automatic index
    customer_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(100),
    customer_segment VARCHAR(30),
    state_code CHAR(2),
    effective_date DATE,
    expiration_date DATE,
    current_flag CHAR(1)
);

-- Indexes for dimension
CREATE INDEX idx_cust_id ON DIM_CUSTOMER(customer_id);
CREATE INDEX idx_cust_current ON DIM_CUSTOMER(customer_id, current_flag);
CREATE INDEX idx_cust_segment ON DIM_CUSTOMER(customer_segment);
CREATE INDEX idx_cust_dates ON DIM_CUSTOMER(effective_date, expiration_date);
```

---

### Fact Tables (Small to Medium)

**Approach**: B-tree indexes on foreign keys

```sql
CREATE TABLE FACT_SALES (
    sales_key BIGINT PRIMARY KEY,
    date_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    store_key INTEGER NOT NULL,
    sales_amount DECIMAL(12,2),
    quantity DECIMAL(10,2)
);

-- B-tree indexes on foreign keys
CREATE INDEX idx_sales_date ON FACT_SALES(date_key);
CREATE INDEX idx_sales_product ON FACT_SALES(product_key);
CREATE INDEX idx_sales_customer ON FACT_SALES(customer_key);
CREATE INDEX idx_sales_store ON FACT_SALES(store_key);

-- Composite index for common query pattern
CREATE INDEX idx_sales_date_store
ON FACT_SALES(date_key, store_key);
```

---

### Fact Tables (Large, Oracle/PostgreSQL)

**Approach**: Bitmap indexes on foreign keys

```sql
-- Bitmap indexes for low-cardinality foreign keys
CREATE BITMAP INDEX idx_sales_date ON FACT_SALES(date_key);
CREATE BITMAP INDEX idx_sales_product ON FACT_SALES(product_key);
CREATE BITMAP INDEX idx_sales_customer ON FACT_SALES(customer_key);
CREATE BITMAP INDEX idx_sales_store ON FACT_SALES(store_key);
CREATE BITMAP INDEX idx_sales_promotion ON FACT_SALES(promotion_key);

-- Bitmap indexes on flags/categories
CREATE BITMAP INDEX idx_sales_return_flag ON FACT_SALES(return_flag);
CREATE BITMAP INDEX idx_sales_channel ON FACT_SALES(sales_channel);
```

---

### Fact Tables (Very Large, SQL Server)

**Approach**: Columnstore index

```sql
-- Clustered columnstore for entire table
CREATE CLUSTERED COLUMNSTORE INDEX cci_sales
ON FACT_SALES;

-- No additional indexes needed in most cases
-- Columnstore handles all analytical queries efficiently

-- Optional: nonclustered B-tree for specific lookups
CREATE NONCLUSTERED INDEX idx_sales_transaction
ON FACT_SALES(transaction_number)
WHERE transaction_number IS NOT NULL;
```

---

## Partitioning Strategies

### Range Partitioning (Most Common)

**Definition**: Partition by value ranges, typically dates.

**Example**:
```sql
-- Partition by month (PostgreSQL syntax)
CREATE TABLE FACT_SALES (
    sales_key BIGINT,
    date_key INTEGER NOT NULL,
    product_key INTEGER,
    amount DECIMAL(12,2)
) PARTITION BY RANGE (date_key);

-- Monthly partitions
CREATE TABLE fact_sales_2024_01 PARTITION OF FACT_SALES
    FOR VALUES FROM (20240101) TO (20240201);

CREATE TABLE fact_sales_2024_02 PARTITION OF FACT_SALES
    FOR VALUES FROM (20240201) TO (20240301);

-- ... one partition per month

-- Indexes on each partition
CREATE INDEX idx_sales_2024_01_product ON fact_sales_2024_01(product_key);
CREATE INDEX idx_sales_2024_02_product ON fact_sales_2024_02(product_key);
```

**Benefits**:
- Partition pruning (query only relevant partitions)
- Easy archival (drop old partitions)
- Parallel operations (load, index, query)
- Faster maintenance (rebuild indexes per partition)

**Query Example**:
```sql
-- Only scans June 2024 partition
SELECT SUM(amount)
FROM FACT_SALES
WHERE date_key BETWEEN 20240601 AND 20240630;
```

---

### Hash Partitioning

**Definition**: Distribute rows across partitions using hash function.

**Use Cases**:
- Even distribution of data
- Parallel processing
- No natural range key

**Example**:
```sql
-- Partition by customer_key hash (4 partitions)
CREATE TABLE FACT_SALES (...)
PARTITION BY HASH (customer_key) PARTITIONS 4;
```

---

### List Partitioning

**Definition**: Partition by discrete list of values.

**Example**:
```sql
-- Partition by region
CREATE TABLE FACT_SALES (...)
PARTITION BY LIST (region);

CREATE TABLE fact_sales_north PARTITION OF FACT_SALES
    FOR VALUES IN ('North', 'Northeast', 'Northwest');

CREATE TABLE fact_sales_south PARTITION OF FACT_SALES
    FOR VALUES IN ('South', 'Southeast', 'Southwest');
```

---

## Index Optimization Techniques

### 1. Composite Indexes (Multi-Column)

**Purpose**: Optimize queries with multiple WHERE clauses.

**Example**:
```sql
-- Common query pattern
SELECT SUM(amount)
FROM FACT_SALES
WHERE date_key = 20240615
  AND store_key = 25;

-- Composite index
CREATE INDEX idx_sales_date_store
ON FACT_SALES(date_key, store_key);
```

**Column Order Rules**:
1. Most selective column first (or most frequently filtered alone)
2. Equality conditions before range conditions
3. Columns used together in queries

**Examples**:
```sql
-- Good: date first (used in most queries, selective)
CREATE INDEX idx_good ON FACT_SALES(date_key, product_key, customer_key);

-- Bad: less selective column first
CREATE INDEX idx_bad ON FACT_SALES(promotion_key, date_key, product_key);
-- promotion_key has many NULLs, not selective
```

---

### 2. Filtered/Partial Indexes

**Purpose**: Index only subset of rows.

**Example (SQL Server)**:
```sql
-- Index only current dimension records
CREATE INDEX idx_customer_current
ON DIM_CUSTOMER(customer_id, customer_name)
WHERE current_flag = 'Y';

-- Index only non-null values
CREATE INDEX idx_sales_promotion
ON FACT_SALES(promotion_key)
WHERE promotion_key IS NOT NULL;
```

**Benefits**:
- Smaller index size
- Faster index maintenance
- Better selectivity

---

### 3. Indexed Views/Materialized Views

**Purpose**: Pre-aggregate and index common queries.

**Example (SQL Server Indexed View)**:
```sql
-- Create view with aggregation
CREATE VIEW vw_sales_daily_product
WITH SCHEMABINDING
AS
SELECT
    date_key,
    product_key,
    COUNT_BIG(*) as transaction_count,
    SUM(sales_amount) as total_amount,
    SUM(quantity) as total_quantity
FROM dbo.FACT_SALES
GROUP BY date_key, product_key;

-- Index the view
CREATE UNIQUE CLUSTERED INDEX idx_sales_daily_product
ON vw_sales_daily_product(date_key, product_key);
```

**Example (PostgreSQL Materialized View)**:
```sql
CREATE MATERIALIZED VIEW mv_sales_daily_product AS
SELECT
    date_key,
    product_key,
    COUNT(*) as transaction_count,
    SUM(sales_amount) as total_amount
FROM FACT_SALES
GROUP BY date_key, product_key;

CREATE INDEX idx_mv_sales_date ON mv_sales_daily_product(date_key);

-- Refresh periodically
REFRESH MATERIALIZED VIEW mv_sales_daily_product;
```

---

## Index Maintenance

### Rebuild vs Reorganize

**Rebuild**: Recreates index from scratch
```sql
-- Rebuild single index
ALTER INDEX idx_sales_date ON FACT_SALES REBUILD;

-- Rebuild all indexes on table
ALTER INDEX ALL ON FACT_SALES REBUILD;
```

**Reorganize**: Defragments existing index
```sql
ALTER INDEX idx_sales_date ON FACT_SALES REORGANIZE;
```

**When to Rebuild vs Reorganize**:
- Fragmentation < 10%: No action needed
- Fragmentation 10-30%: Reorganize
- Fragmentation > 30%: Rebuild

---

### Statistics Updates

```sql
-- Update statistics for query optimizer
UPDATE STATISTICS FACT_SALES;

-- Update with full scan for accuracy
UPDATE STATISTICS FACT_SALES WITH FULLSCAN;

-- Auto-update statistics (SQL Server)
ALTER DATABASE DataWarehouse SET AUTO_UPDATE_STATISTICS ON;
```

---

### Monitoring Index Usage

**SQL Server**:
```sql
-- Find unused indexes
SELECT
    OBJECT_NAME(i.object_id) AS table_name,
    i.name AS index_name,
    s.user_seeks,
    s.user_scans,
    s.user_lookups,
    s.user_updates
FROM sys.indexes i
LEFT JOIN sys.dm_db_index_usage_stats s
    ON i.object_id = s.object_id AND i.index_id = s.index_id
WHERE s.user_seeks = 0
  AND s.user_scans = 0
  AND s.user_lookups = 0
  AND i.name IS NOT NULL;
```

---

## Best Practices

### General
1. **Index for query patterns**, not every column
2. **Measure before indexing**: Identify slow queries first
3. **Monitor index usage**: Remove unused indexes
4. **Balance**: Too few indexes = slow queries, too many = slow loads
5. **Test**: Benchmark queries with and without indexes

### Dimensions
1. Index primary key (surrogate)
2. Index natural business key
3. Index frequently filtered attributes
4. Index SCD Type 2 columns (current_flag, dates)
5. Consider covering indexes for common queries

### Facts
1. **Small/Medium tables**: B-tree indexes on foreign keys
2. **Large tables (Oracle/PostgreSQL)**: Bitmap indexes on foreign keys
3. **Very large tables (SQL Server)**: Columnstore index
4. Partition large fact tables by date
5. Create indexes on partitions, not base table

### Maintenance
1. Rebuild indexes periodically (after bulk loads)
2. Update statistics regularly
3. Monitor fragmentation
4. Schedule during maintenance windows
5. Automate where possible

### Performance
1. Use composite indexes for multi-column queries
2. Order composite index columns by selectivity
3. Use filtered indexes for sparse data
4. Consider covering indexes for critical queries
5. Create aggregate tables/views for common patterns

---

## Quick Reference

| Table Type | Size | Strategy |
|------------|------|----------|
| Dimension | Any | B-tree on PK, business key, common filters |
| Fact | < 10M rows | B-tree on foreign keys |
| Fact | 10M - 100M | Bitmap (Oracle/PG) or B-tree |
| Fact | > 100M rows | Columnstore (SQL Server) or Bitmap + partitioning |
| Fact | > 1B rows | Columnstore + partitioning or Bitmap + partitioning |

| Index Type | Best For | Avoid For |
|------------|----------|-----------|
| B-tree | High cardinality, ranges, sorting | Low cardinality, read-only DW |
| Bitmap | Low cardinality, FK, DW | OLTP, frequent updates |
| Columnstore | Large facts, aggregations | Lookups, small tables |
| Hash | Equality, distributed | Ranges, sorting |
| Covering | Specific queries | General purpose |
