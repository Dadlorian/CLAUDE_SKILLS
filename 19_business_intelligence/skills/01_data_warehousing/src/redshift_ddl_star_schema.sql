-- Amazon Redshift Star Schema DDL
-- Retail Analytics Data Warehouse
-- Platform: Amazon Redshift
-- Description: Optimized star schema with distribution and sort keys

-- ============================================
-- DIMENSION TABLES
-- ============================================

-- Date Dimension
CREATE TABLE dim_date (
    date_key INTEGER NOT NULL,
    date_value DATE NOT NULL,
    day_of_week INTEGER,
    day_name VARCHAR(10),
    day_of_month INTEGER,
    day_of_year INTEGER,
    week_of_year INTEGER,
    month_number INTEGER,
    month_name VARCHAR(10),
    quarter INTEGER,
    quarter_name VARCHAR(2),
    year INTEGER,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    holiday_name VARCHAR(100),
    fiscal_year INTEGER,
    fiscal_quarter INTEGER,
    fiscal_month INTEGER,
    created_at TIMESTAMP DEFAULT GETDATE(),
    updated_at TIMESTAMP DEFAULT GETDATE(),
    PRIMARY KEY (date_key)
)
DISTSTYLE ALL  -- Replicate to all nodes (small dimension)
SORTKEY (date_value);

COMMENT ON TABLE dim_date IS 'Date dimension with calendar and fiscal attributes';

-- Customer Dimension (SCD Type 2)
CREATE TABLE dim_customer (
    customer_key INTEGER IDENTITY(1,1) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(200),
    email VARCHAR(200),
    phone VARCHAR(50),
    customer_segment VARCHAR(50),
    customer_tier VARCHAR(20),
    country VARCHAR(100),
    state VARCHAR(100),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    -- SCD Type 2 columns
    effective_date DATE NOT NULL,
    expiration_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    -- Metadata
    source_system VARCHAR(50),
    created_at TIMESTAMP DEFAULT GETDATE(),
    updated_at TIMESTAMP DEFAULT GETDATE(),
    PRIMARY KEY (customer_key)
)
DISTSTYLE KEY
DISTKEY (customer_key)
SORTKEY (customer_id, is_current);

COMMENT ON TABLE dim_customer IS 'Customer dimension with SCD Type 2 tracking';

-- Product Dimension (SCD Type 2)
CREATE TABLE dim_product (
    product_key INTEGER IDENTITY(1,1) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    product_name VARCHAR(200),
    product_description VARCHAR(1000),
    sku VARCHAR(100),
    brand VARCHAR(100),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    department VARCHAR(100),
    unit_cost DECIMAL(12, 2),
    unit_price DECIMAL(12, 2),
    is_active BOOLEAN,
    -- SCD Type 2 columns
    effective_date DATE NOT NULL,
    expiration_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    -- Metadata
    source_system VARCHAR(50),
    created_at TIMESTAMP DEFAULT GETDATE(),
    updated_at TIMESTAMP DEFAULT GETDATE(),
    PRIMARY KEY (product_key)
)
DISTSTYLE KEY
DISTKEY (product_key)
SORTKEY (product_id, is_current, category);

COMMENT ON TABLE dim_product IS 'Product dimension with SCD Type 2 tracking';

-- Store Dimension
CREATE TABLE dim_store (
    store_key INTEGER IDENTITY(1,1) NOT NULL,
    store_id VARCHAR(50) NOT NULL,
    store_name VARCHAR(200),
    store_type VARCHAR(50),
    store_size_sq_ft INTEGER,
    country VARCHAR(100),
    state VARCHAR(100),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    region VARCHAR(100),
    district VARCHAR(100),
    manager_name VARCHAR(200),
    opening_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT GETDATE(),
    updated_at TIMESTAMP DEFAULT GETDATE(),
    PRIMARY KEY (store_key)
)
DISTSTYLE ALL  -- Replicate to all nodes (small dimension)
SORTKEY (store_id);

-- Employee Dimension
CREATE TABLE dim_employee (
    employee_key INTEGER IDENTITY(1,1) NOT NULL,
    employee_id VARCHAR(50) NOT NULL,
    employee_name VARCHAR(200),
    job_title VARCHAR(100),
    department VARCHAR(100),
    manager_id VARCHAR(50),
    hire_date DATE,
    -- SCD Type 2 columns
    effective_date DATE NOT NULL,
    expiration_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT GETDATE(),
    updated_at TIMESTAMP DEFAULT GETDATE(),
    PRIMARY KEY (employee_key)
)
DISTSTYLE ALL
SORTKEY (employee_id, is_current);

-- ============================================
-- FACT TABLES
-- ============================================

-- Sales Fact (Transaction grain)
CREATE TABLE fact_sales (
    sales_key INTEGER IDENTITY(1,1) NOT NULL,
    -- Foreign Keys
    date_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    store_key INTEGER NOT NULL,
    employee_key INTEGER,
    -- Degenerate Dimensions
    transaction_id VARCHAR(100) NOT NULL,
    line_item_number INTEGER,
    -- Measures
    quantity INTEGER,
    unit_price DECIMAL(12, 2),
    unit_cost DECIMAL(12, 2),
    gross_sales_amount DECIMAL(12, 2),
    discount_amount DECIMAL(12, 2),
    net_sales_amount DECIMAL(12, 2),
    tax_amount DECIMAL(12, 2),
    total_amount DECIMAL(12, 2),
    profit_amount DECIMAL(12, 2),
    -- Metadata
    transaction_timestamp TIMESTAMP,
    source_system VARCHAR(50),
    created_at TIMESTAMP DEFAULT GETDATE(),
    updated_at TIMESTAMP DEFAULT GETDATE(),
    PRIMARY KEY (sales_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (store_key) REFERENCES dim_store(store_key)
)
DISTSTYLE KEY
DISTKEY (customer_key)  -- Distribute on most common join key
COMPOUND SORTKEY (date_key, store_key, customer_key);

COMMENT ON TABLE fact_sales IS 'Sales transactions at line item grain';

-- Inventory Snapshot Fact (Periodic Snapshot)
CREATE TABLE fact_inventory_snapshot (
    inventory_snapshot_key INTEGER IDENTITY(1,1) NOT NULL,
    -- Foreign Keys
    date_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    store_key INTEGER NOT NULL,
    -- Measures
    beginning_inventory INTEGER,
    units_received INTEGER,
    units_sold INTEGER,
    units_returned INTEGER,
    units_adjusted INTEGER,
    ending_inventory INTEGER,
    inventory_value DECIMAL(12, 2),
    days_of_supply INTEGER,
    reorder_point INTEGER,
    is_out_of_stock BOOLEAN,
    -- Metadata
    snapshot_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT GETDATE(),
    PRIMARY KEY (inventory_snapshot_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (store_key) REFERENCES dim_store(store_key)
)
DISTSTYLE KEY
DISTKEY (product_key)
COMPOUND SORTKEY (date_key, store_key);

-- Order Fulfillment Fact (Accumulating Snapshot)
CREATE TABLE fact_order_fulfillment (
    order_fulfillment_key INTEGER IDENTITY(1,1) NOT NULL,
    -- Foreign Keys (Date keys for each milestone)
    order_date_key INTEGER,
    payment_date_key INTEGER,
    ship_date_key INTEGER,
    delivery_date_key INTEGER,
    customer_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    store_key INTEGER,
    -- Degenerate Dimensions
    order_id VARCHAR(100) NOT NULL,
    -- Measures
    quantity INTEGER,
    order_amount DECIMAL(12, 2),
    -- Lag measures
    order_to_payment_lag INTEGER,
    payment_to_ship_lag INTEGER,
    ship_to_delivery_lag INTEGER,
    order_to_delivery_lag INTEGER,
    -- Status flags
    is_paid BOOLEAN DEFAULT FALSE,
    is_shipped BOOLEAN DEFAULT FALSE,
    is_delivered BOOLEAN DEFAULT FALSE,
    is_cancelled BOOLEAN DEFAULT FALSE,
    -- Metadata
    created_at TIMESTAMP DEFAULT GETDATE(),
    updated_at TIMESTAMP DEFAULT GETDATE(),
    PRIMARY KEY (order_fulfillment_key)
)
DISTSTYLE KEY
DISTKEY (customer_key)
SORTKEY (order_date_key, customer_key);

-- ============================================
-- AGGREGATE FACT TABLES
-- ============================================

-- Daily Sales Aggregate
CREATE TABLE fact_daily_sales_agg (
    date_key INTEGER NOT NULL,
    store_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    -- Aggregated Measures
    total_quantity INTEGER,
    total_transactions INTEGER,
    total_gross_sales DECIMAL(12, 2),
    total_discount DECIMAL(12, 2),
    total_net_sales DECIMAL(12, 2),
    total_tax DECIMAL(12, 2),
    total_amount DECIMAL(12, 2),
    total_profit DECIMAL(12, 2),
    average_transaction_value DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT GETDATE(),
    PRIMARY KEY (date_key, store_key, product_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (store_key) REFERENCES dim_store(store_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key)
)
DISTSTYLE KEY
DISTKEY (product_key)
SORTKEY (date_key, store_key);

-- ============================================
-- MATERIALIZED VIEWS
-- ============================================

-- Current Customer View
CREATE MATERIALIZED VIEW mv_current_customers AS
SELECT
    customer_key,
    customer_id,
    customer_name,
    email,
    phone,
    customer_segment,
    customer_tier,
    country,
    state,
    city,
    postal_code
FROM dim_customer
WHERE is_current = TRUE;

-- Current Product View
CREATE MATERIALIZED VIEW mv_current_products AS
SELECT
    product_key,
    product_id,
    product_name,
    product_description,
    sku,
    brand,
    category,
    subcategory,
    department,
    unit_cost,
    unit_price,
    is_active
FROM dim_product
WHERE is_current = TRUE;

-- Sales Summary View
CREATE MATERIALIZED VIEW mv_sales_summary AS
SELECT
    d.date_value,
    d.year,
    d.quarter,
    d.month_name,
    c.customer_name,
    c.customer_segment,
    p.product_name,
    p.category,
    p.brand,
    s.store_name,
    s.region,
    f.transaction_id,
    f.quantity,
    f.unit_price,
    f.gross_sales_amount,
    f.discount_amount,
    f.net_sales_amount,
    f.tax_amount,
    f.total_amount,
    f.profit_amount
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_customer c ON f.customer_key = c.customer_key
JOIN dim_product p ON f.product_key = p.product_key
JOIN dim_store s ON f.store_key = s.store_key;

-- ============================================
-- PERFORMANCE OPTIMIZATION INDEXES
-- ============================================

-- Note: Redshift doesn't use traditional indexes
-- Instead, we use:
-- 1. SORTKEY for data sorting (already defined in CREATE TABLE)
-- 2. DISTKEY for data distribution (already defined in CREATE TABLE)
-- 3. ANALYZE to update statistics
-- 4. VACUUM to reorganize data

-- ============================================
-- MAINTENANCE PROCEDURES
-- ============================================

-- Analyze tables to update statistics
ANALYZE dim_date;
ANALYZE dim_customer;
ANALYZE dim_product;
ANALYZE dim_store;
ANALYZE dim_employee;
ANALYZE fact_sales;
ANALYZE fact_inventory_snapshot;
ANALYZE fact_order_fulfillment;
ANALYZE fact_daily_sales_agg;

-- Vacuum to reclaim space and sort
VACUUM FULL fact_sales;
VACUUM FULL fact_inventory_snapshot;

-- ============================================
-- COMPRESSION ENCODING
-- ============================================

-- Analyze compression for optimal storage
-- Run this after loading sample data:
/*
ANALYZE COMPRESSION dim_customer;
ANALYZE COMPRESSION dim_product;
ANALYZE COMPRESSION fact_sales;

-- Apply recommended compression manually or use automatic:
ALTER TABLE fact_sales
ALTER COLUMN transaction_id ENCODE ZSTD,
ALTER COLUMN quantity ENCODE AZ64,
ALTER COLUMN unit_price ENCODE AZ64,
ALTER COLUMN total_amount ENCODE AZ64;
*/

-- ============================================
-- WORKLOAD MANAGEMENT (WLM) QUEUE SETUP
-- ============================================

-- Configure WLM queues in Redshift console or parameter group
-- Example queue configuration (JSON):
/*
[
  {
    "query_concurrency": 5,
    "query_group": "dashboard",
    "memory_percent_to_use": 30,
    "user_group": ["dashboard_users"]
  },
  {
    "query_concurrency": 3,
    "query_group": "etl",
    "memory_percent_to_use": 50,
    "user_group": ["etl_users"]
  },
  {
    "query_concurrency": 2,
    "query_group": "reporting",
    "memory_percent_to_use": 20,
    "user_group": ["report_users"]
  }
]
*/

-- ============================================
-- QUERY MONITORING RULES (QMR)
-- ============================================

-- Create rules to abort or log long-running queries
/*
-- Abort queries running longer than 10 minutes
CREATE OR REPLACE VIEW admin.v_abort_long_queries AS
SELECT *
FROM stv_inflight
WHERE run_time > 600000  -- 10 minutes in milliseconds
  AND userid > 1;  -- Exclude superuser

-- Log queries scanning more than 1 billion rows
CREATE OR REPLACE VIEW admin.v_log_large_scans AS
SELECT *
FROM stv_inflight
WHERE rows > 1000000000;
*/

-- ============================================
-- DATA LOADING EXAMPLES
-- ============================================

-- Load data from S3 using COPY command
/*
-- Load dimension from S3
COPY dim_customer
FROM 's3://bucket-name/data/customers/'
IAM_ROLE 'arn:aws:iam::account-id:role/RedshiftCopyRole'
FORMAT AS PARQUET
COMPUPDATE OFF
STATUPDATE OFF;

-- Load fact from S3 with manifest
COPY fact_sales
FROM 's3://bucket-name/data/sales/manifest.json'
IAM_ROLE 'arn:aws:iam::account-id:role/RedshiftCopyRole'
FORMAT AS PARQUET
MANIFEST
COMPUPDATE OFF
STATUPDATE ON;

-- Incremental load pattern
BEGIN TRANSACTION;

-- Load to staging
COPY staging.stg_sales
FROM 's3://bucket-name/data/sales/incremental/'
IAM_ROLE 'arn:aws:iam::account-id:role/RedshiftCopyRole'
FORMAT AS CSV
DELIMITER ','
IGNOREHEADER 1
DATEFORMAT 'auto'
TIMEFORMAT 'auto'
TRUNCATECOLUMNS
ACCEPTINVCHARS;

-- Merge to fact
DELETE FROM fact_sales
USING staging.stg_sales
WHERE fact_sales.transaction_id = staging.stg_sales.transaction_id
  AND fact_sales.line_item_number = staging.stg_sales.line_item_number;

INSERT INTO fact_sales
SELECT * FROM staging.stg_sales;

END TRANSACTION;
*/

-- ============================================
-- MONITORING QUERIES
-- ============================================

-- Check table sizes
SELECT
    TRIM(pgdb.datname) AS database,
    TRIM(pgn.nspname) AS schema,
    TRIM(a.name) AS table,
    b.mbytes,
    a.rows
FROM (
    SELECT db_id, id, name, SUM(rows) AS rows
    FROM stv_tbl_perm a
    GROUP BY db_id, id, name
) AS a
JOIN pg_class AS pgc ON pgc.oid = a.id
JOIN pg_namespace AS pgn ON pgn.oid = pgc.relnamespace
JOIN pg_database AS pgdb ON pgdb.oid = a.db_id
JOIN (
    SELECT tbl, COUNT(*) AS mbytes
    FROM stv_blocklist
    GROUP BY tbl
) AS b ON a.id = b.tbl
WHERE pgn.nspname NOT IN ('pg_catalog', 'information_schema')
ORDER BY mbytes DESC, a.db_id, a.name;

-- Check query performance
SELECT
    query,
    TRIM(querytxt) AS SQL,
    starttime,
    endtime,
    DATEDIFF(seconds, starttime, endtime) AS duration_seconds,
    aborted
FROM stl_query
WHERE userid > 1  -- Exclude superuser
  AND starttime >= DATEADD(hour, -24, GETDATE())
ORDER BY duration_seconds DESC
LIMIT 20;
