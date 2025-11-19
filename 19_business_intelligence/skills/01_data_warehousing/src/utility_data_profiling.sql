-- Data Profiling Utility Queries
-- Platform-agnostic data profiling and quality assessment
-- Description: Comprehensive data profiling for data warehouse tables

-- ============================================
-- TABLE PROFILING - Row Counts and Size
-- ============================================

-- Get row counts for all tables in a schema
SELECT
    table_schema,
    table_name,
    table_type,
    row_count,
    bytes / (1024 * 1024) AS size_mb,
    bytes / (1024 * 1024 * 1024) AS size_gb
FROM information_schema.tables
WHERE table_schema = 'DIM' OR table_schema = 'FACT'
ORDER BY bytes DESC;

-- Snowflake-specific table size query
SELECT
    table_schema,
    table_name,
    row_count,
    bytes / (1024 * 1024 * 1024) AS size_gb,
    active_bytes / (1024 * 1024 * 1024) AS active_size_gb,
    time_travel_bytes / (1024 * 1024 * 1024) AS time_travel_gb,
    failsafe_bytes / (1024 * 1024 * 1024) AS failsafe_gb
FROM snowflake.account_usage.table_storage_metrics
WHERE table_schema IN ('DIM', 'FACT')
ORDER BY bytes DESC;

-- BigQuery-specific table size query
SELECT
    table_schema,
    table_name,
    row_count,
    size_bytes / (1024 * 1024 * 1024) AS size_gb,
    TIMESTAMP_MILLIS(creation_time) AS created_at,
    TIMESTAMP_MILLIS(last_modified_time) AS last_modified_at
FROM `project.dataset.__TABLES__`
ORDER BY size_bytes DESC;

-- ============================================
-- COLUMN PROFILING - Data Distribution
-- ============================================

-- Generic column profiling template (replace TABLE_NAME and COLUMN_NAME)
SELECT
    'TABLE_NAME' AS table_name,
    'COLUMN_NAME' AS column_name,
    COUNT(*) AS total_rows,
    COUNT(COLUMN_NAME) AS non_null_count,
    COUNT(*) - COUNT(COLUMN_NAME) AS null_count,
    ROUND(100.0 * COUNT(COLUMN_NAME) / COUNT(*), 2) AS non_null_percentage,
    COUNT(DISTINCT COLUMN_NAME) AS distinct_count,
    ROUND(100.0 * COUNT(DISTINCT COLUMN_NAME) / COUNT(COLUMN_NAME), 2) AS cardinality_percentage,
    MIN(COLUMN_NAME) AS min_value,
    MAX(COLUMN_NAME) AS max_value
FROM TABLE_NAME;

-- ============================================
-- NUMERIC COLUMN PROFILING
-- ============================================

-- Statistical analysis for numeric columns
SELECT
    'sales_amount' AS column_name,
    COUNT(*) AS total_rows,
    COUNT(sales_amount) AS non_null_count,
    AVG(sales_amount) AS mean,
    MEDIAN(sales_amount) AS median,
    MODE(sales_amount) AS mode,
    STDDEV(sales_amount) AS std_deviation,
    VARIANCE(sales_amount) AS variance,
    MIN(sales_amount) AS min_value,
    MAX(sales_amount) AS max_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY sales_amount) AS percentile_25,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY sales_amount) AS percentile_50,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY sales_amount) AS percentile_75,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY sales_amount) AS percentile_95,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY sales_amount) AS percentile_99
FROM FACT.FACT_SALES;

-- Detect outliers using IQR method
WITH stats AS (
    SELECT
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY sales_amount) AS q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY sales_amount) AS q3,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY sales_amount) -
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY sales_amount) AS iqr
    FROM FACT.FACT_SALES
)
SELECT
    sales_key,
    sales_amount,
    CASE
        WHEN sales_amount < (q1 - 1.5 * iqr) THEN 'Lower Outlier'
        WHEN sales_amount > (q3 + 1.5 * iqr) THEN 'Upper Outlier'
        ELSE 'Normal'
    END AS outlier_status
FROM FACT.FACT_SALES, stats
WHERE sales_amount < (q1 - 1.5 * iqr)
   OR sales_amount > (q3 + 1.5 * iqr);

-- ============================================
-- STRING COLUMN PROFILING
-- ============================================

-- Analyze string column patterns
SELECT
    'customer_email' AS column_name,
    COUNT(*) AS total_rows,
    COUNT(customer_email) AS non_null_count,
    COUNT(DISTINCT customer_email) AS distinct_count,
    AVG(LENGTH(customer_email)) AS avg_length,
    MIN(LENGTH(customer_email)) AS min_length,
    MAX(LENGTH(customer_email)) AS max_length,
    -- Pattern detection
    SUM(CASE WHEN customer_email LIKE '%@%' THEN 1 ELSE 0 END) AS has_at_symbol,
    SUM(CASE WHEN customer_email LIKE '%.com%' THEN 1 ELSE 0 END) AS has_com_domain,
    SUM(CASE WHEN customer_email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        THEN 1 ELSE 0 END) AS valid_email_format
FROM DIM.DIM_CUSTOMER;

-- Top values for categorical columns
SELECT
    customer_segment,
    COUNT(*) AS count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage,
    ROUND(100.0 * SUM(COUNT(*)) OVER (ORDER BY COUNT(*) DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / SUM(COUNT(*)) OVER (), 2) AS cumulative_percentage
FROM DIM.DIM_CUSTOMER
WHERE is_current = TRUE
GROUP BY customer_segment
ORDER BY count DESC;

-- ============================================
-- DATE COLUMN PROFILING
-- ============================================

-- Analyze date columns
SELECT
    'order_date' AS column_name,
    COUNT(*) AS total_rows,
    COUNT(order_date) AS non_null_count,
    MIN(order_date) AS earliest_date,
    MAX(order_date) AS latest_date,
    DATEDIFF(day, MIN(order_date), MAX(order_date)) AS date_range_days,
    COUNT(DISTINCT order_date) AS distinct_dates,
    -- Date distribution by year
    COUNT(CASE WHEN YEAR(order_date) = 2023 THEN 1 END) AS year_2023_count,
    COUNT(CASE WHEN YEAR(order_date) = 2024 THEN 1 END) AS year_2024_count,
    -- Recency
    DATEDIFF(day, MAX(order_date), CURRENT_DATE()) AS days_since_last_record
FROM FACT.FACT_SALES;

-- Date gap analysis
WITH date_sequence AS (
    SELECT
        order_date,
        LAG(order_date) OVER (ORDER BY order_date) AS previous_date,
        DATEDIFF(day, LAG(order_date) OVER (ORDER BY order_date), order_date) AS days_gap
    FROM (
        SELECT DISTINCT order_date
        FROM FACT.FACT_SALES
    )
)
SELECT
    order_date,
    previous_date,
    days_gap,
    CASE
        WHEN days_gap = 1 THEN 'Consecutive'
        WHEN days_gap <= 7 THEN 'Within Week'
        WHEN days_gap <= 30 THEN 'Within Month'
        ELSE 'Large Gap'
    END AS gap_category
FROM date_sequence
WHERE days_gap > 1
ORDER BY days_gap DESC;

-- ============================================
-- DATA QUALITY CHECKS
-- ============================================

-- Null value analysis across all columns
SELECT
    'DIM_CUSTOMER' AS table_name,
    'customer_name' AS column_name,
    COUNT(*) AS total_rows,
    SUM(CASE WHEN customer_name IS NULL THEN 1 ELSE 0 END) AS null_count,
    ROUND(100.0 * SUM(CASE WHEN customer_name IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS null_percentage
FROM DIM.DIM_CUSTOMER
UNION ALL
SELECT
    'DIM_CUSTOMER',
    'email',
    COUNT(*),
    SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END),
    ROUND(100.0 * SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2)
FROM DIM.DIM_CUSTOMER
UNION ALL
SELECT
    'DIM_CUSTOMER',
    'customer_segment',
    COUNT(*),
    SUM(CASE WHEN customer_segment IS NULL THEN 1 ELSE 0 END),
    ROUND(100.0 * SUM(CASE WHEN customer_segment IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2)
FROM DIM.DIM_CUSTOMER;

-- Duplicate detection
SELECT
    customer_id,
    COUNT(*) AS duplicate_count
FROM DIM.DIM_CUSTOMER
WHERE is_current = TRUE
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Referential integrity check
SELECT
    'FACT_SALES -> DIM_CUSTOMER' AS relationship,
    COUNT(*) AS orphaned_records
FROM FACT.FACT_SALES f
LEFT JOIN DIM.DIM_CUSTOMER c ON f.customer_key = c.customer_key
WHERE c.customer_key IS NULL;

-- ============================================
-- CROSS-TABLE PROFILING
-- ============================================

-- Compare dimension to fact grain
SELECT
    'Customer' AS dimension,
    (SELECT COUNT(DISTINCT customer_id) FROM DIM.DIM_CUSTOMER WHERE is_current = TRUE) AS dim_count,
    (SELECT COUNT(DISTINCT customer_key) FROM FACT.FACT_SALES) AS fact_count,
    (SELECT COUNT(DISTINCT customer_key) FROM FACT.FACT_SALES) -
    (SELECT COUNT(DISTINCT customer_id) FROM DIM.DIM_CUSTOMER WHERE is_current = TRUE) AS difference;

-- ============================================
-- TREND ANALYSIS
-- ============================================

-- Daily record volume trend
SELECT
    DATE_TRUNC('day', transaction_timestamp) AS date,
    COUNT(*) AS record_count,
    SUM(total_amount) AS total_sales,
    AVG(total_amount) AS avg_transaction,
    MIN(total_amount) AS min_transaction,
    MAX(total_amount) AS max_transaction
FROM FACT.FACT_SALES
WHERE transaction_timestamp >= CURRENT_DATE() - 90
GROUP BY DATE_TRUNC('day', transaction_timestamp)
ORDER BY date DESC;

-- ============================================
-- COMPREHENSIVE TABLE PROFILE FUNCTION
-- ============================================

-- Create a stored procedure for comprehensive profiling (Snowflake)
CREATE OR REPLACE PROCEDURE SP_PROFILE_TABLE(
    TABLE_NAME VARCHAR,
    SAMPLE_SIZE INTEGER DEFAULT 1000000
)
RETURNS TABLE()
LANGUAGE SQL
AS
$$
DECLARE
    profile_sql VARCHAR;
BEGIN
    profile_sql := '
        SELECT
            :TABLE_NAME AS table_name,
            COUNT(*) AS total_rows,
            COUNT(DISTINCT *) AS distinct_rows,
            CURRENT_TIMESTAMP() AS profiled_at
        FROM IDENTIFIER(:TABLE_NAME)
        SAMPLE (' || :SAMPLE_SIZE || ' ROWS)
    ';

    RETURN TABLE(SELECT * FROM TABLE(RESULT_SCAN(LAST_QUERY_ID())));
END;
$$;

-- ============================================
-- DATA FRESHNESS CHECK
-- ============================================

-- Check when tables were last updated
SELECT
    table_schema,
    table_name,
    MAX(created_at) AS last_insert,
    MAX(updated_at) AS last_update,
    DATEDIFF(hour, MAX(updated_at), CURRENT_TIMESTAMP()) AS hours_since_update,
    CASE
        WHEN DATEDIFF(hour, MAX(updated_at), CURRENT_TIMESTAMP()) < 24 THEN 'Fresh'
        WHEN DATEDIFF(hour, MAX(updated_at), CURRENT_TIMESTAMP()) < 48 THEN 'Recent'
        WHEN DATEDIFF(hour, MAX(updated_at), CURRENT_TIMESTAMP()) < 168 THEN 'Stale'
        ELSE 'Very Stale'
    END AS freshness_status
FROM (
    SELECT 'DIM' AS table_schema, 'DIM_CUSTOMER' AS table_name, created_at, updated_at
    FROM DIM.DIM_CUSTOMER
    UNION ALL
    SELECT 'FACT', 'FACT_SALES', created_at, updated_at
    FROM FACT.FACT_SALES
)
GROUP BY table_schema, table_name;

-- ============================================
-- SCHEMA DRIFT DETECTION
-- ============================================

-- Compare current schema to expected schema
WITH expected_schema AS (
    SELECT 'FACT_SALES' AS table_name, 'date_key' AS column_name, 'INTEGER' AS expected_type
    UNION ALL SELECT 'FACT_SALES', 'customer_key', 'INTEGER'
    UNION ALL SELECT 'FACT_SALES', 'product_key', 'INTEGER'
    UNION ALL SELECT 'FACT_SALES', 'quantity', 'INTEGER'
    UNION ALL SELECT 'FACT_SALES', 'total_amount', 'DECIMAL(12,2)'
),
actual_schema AS (
    SELECT
        table_name,
        column_name,
        data_type
    FROM information_schema.columns
    WHERE table_schema = 'FACT' AND table_name = 'FACT_SALES'
)
SELECT
    COALESCE(e.table_name, a.table_name) AS table_name,
    COALESCE(e.column_name, a.column_name) AS column_name,
    e.expected_type,
    a.data_type AS actual_type,
    CASE
        WHEN e.column_name IS NULL THEN 'Unexpected Column'
        WHEN a.column_name IS NULL THEN 'Missing Column'
        WHEN e.expected_type != a.data_type THEN 'Type Mismatch'
        ELSE 'OK'
    END AS status
FROM expected_schema e
FULL OUTER JOIN actual_schema a
    ON e.table_name = a.table_name AND e.column_name = a.column_name
WHERE e.expected_type != a.data_type
   OR e.column_name IS NULL
   OR a.column_name IS NULL;
