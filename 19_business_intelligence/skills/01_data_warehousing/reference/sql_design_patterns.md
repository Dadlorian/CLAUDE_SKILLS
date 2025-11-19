# SQL Design Patterns for Data Warehousing

Common SQL patterns and best practices for data warehouse development, ETL/ELT, and analytics queries.

## Window Functions

### Running Totals
```sql
-- Running total by date
SELECT
    order_date,
    order_amount,
    SUM(order_amount) OVER (
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as running_total
FROM orders
ORDER BY order_date;

-- Running total by category
SELECT
    category,
    order_date,
    order_amount,
    SUM(order_amount) OVER (
        PARTITION BY category
        ORDER BY order_date
    ) as category_running_total
FROM orders
ORDER BY category, order_date;
```

### Row Numbering & Ranking
```sql
-- Get most recent record per customer
SELECT *
FROM (
    SELECT
        customer_id,
        order_date,
        order_amount,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY order_date DESC
        ) as rn
    FROM orders
)
WHERE rn = 1;

-- Top N per group
SELECT *
FROM (
    SELECT
        category,
        product_name,
        sales_amount,
        RANK() OVER (
            PARTITION BY category
            ORDER BY sales_amount DESC
        ) as sales_rank
    FROM product_sales
)
WHERE sales_rank <= 10;

-- Dense rank (no gaps in ranking)
SELECT
    product_name,
    sales_amount,
    DENSE_RANK() OVER (ORDER BY sales_amount DESC) as dense_rank,
    RANK() OVER (ORDER BY sales_amount DESC) as rank,
    ROW_NUMBER() OVER (ORDER BY sales_amount DESC) as row_num
FROM product_sales;
```

### LAG and LEAD (Previous/Next Values)
```sql
-- Compare to previous period
SELECT
    order_date,
    total_sales,
    LAG(total_sales, 1) OVER (ORDER BY order_date) as previous_day_sales,
    total_sales - LAG(total_sales, 1) OVER (ORDER BY order_date) as daily_change,
    ROUND(
        100.0 * (total_sales - LAG(total_sales, 1) OVER (ORDER BY order_date)) /
        NULLIF(LAG(total_sales, 1) OVER (ORDER BY order_date), 0),
        2
    ) as pct_change
FROM daily_sales
ORDER BY order_date;

-- Next value (LEAD)
SELECT
    customer_id,
    order_date,
    order_amount,
    LEAD(order_date, 1) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
    ) as next_order_date,
    DATEDIFF(
        day,
        order_date,
        LEAD(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date)
    ) as days_to_next_order
FROM orders;
```

### Moving Averages
```sql
-- 7-day moving average
SELECT
    order_date,
    daily_sales,
    AVG(daily_sales) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg_7day,
    AVG(daily_sales) OVER (
        ORDER BY order_date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) as moving_avg_30day
FROM daily_sales
ORDER BY order_date;

-- Centered moving average
SELECT
    order_date,
    daily_sales,
    AVG(daily_sales) OVER (
        ORDER BY order_date
        ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING
    ) as centered_avg_7day
FROM daily_sales;
```

### Percentiles and NTILE
```sql
-- Percentile ranking
SELECT
    customer_id,
    total_spend,
    PERCENT_RANK() OVER (ORDER BY total_spend) as pct_rank,
    CUME_DIST() OVER (ORDER BY total_spend) as cumulative_dist,
    NTILE(10) OVER (ORDER BY total_spend) as decile,
    NTILE(100) OVER (ORDER BY total_spend) as percentile
FROM customer_totals;

-- Customer segmentation by spend
SELECT
    customer_id,
    total_spend,
    CASE NTILE(4) OVER (ORDER BY total_spend)
        WHEN 4 THEN 'Platinum'
        WHEN 3 THEN 'Gold'
        WHEN 2 THEN 'Silver'
        WHEN 1 THEN 'Bronze'
    END as customer_tier
FROM customer_totals;
```

## Incremental Loading Patterns

### High Watermark Pattern
```sql
-- Get max timestamp from target
CREATE OR REPLACE TEMPORARY TABLE watermark AS
SELECT COALESCE(MAX(updated_timestamp), '1900-01-01'::TIMESTAMP) as last_updated
FROM target_table;

-- Load only new/changed records
INSERT INTO target_table
SELECT s.*
FROM source_table s
CROSS JOIN watermark w
WHERE s.updated_timestamp > w.last_updated;
```

### Upsert (MERGE) Pattern
```sql
-- Snowflake/Modern warehouse MERGE
MERGE INTO target_table t
USING source_table s
ON t.id = s.id

WHEN MATCHED AND s.updated_timestamp > t.updated_timestamp THEN
    UPDATE SET
        t.column1 = s.column1,
        t.column2 = s.column2,
        t.updated_timestamp = s.updated_timestamp

WHEN NOT MATCHED THEN
    INSERT (id, column1, column2, updated_timestamp)
    VALUES (s.id, s.column1, s.column2, s.updated_timestamp);
```

### Delete Detection
```sql
-- Soft delete approach
MERGE INTO target_table t
USING (
    SELECT id FROM source_table
) s
ON t.id = s.id

WHEN MATCHED THEN
    UPDATE SET t.is_deleted = FALSE

WHEN NOT MATCHED BY SOURCE THEN
    UPDATE SET t.is_deleted = TRUE, t.deleted_timestamp = CURRENT_TIMESTAMP();

-- Hard delete approach (use cautiously)
DELETE FROM target_table
WHERE id NOT IN (SELECT id FROM source_table);
```

### Incremental with Deduplication
```sql
-- Remove duplicates before loading
INSERT INTO target_table
SELECT *
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY id
            ORDER BY updated_timestamp DESC
        ) as rn
    FROM staging_table
)
WHERE rn = 1;
```

## Slowly Changing Dimension (SCD) Patterns

### SCD Type 2 Insert Logic
```sql
-- Step 1: Expire changed records
UPDATE customer_dim
SET end_date = CURRENT_DATE - 1,
    is_current = FALSE
FROM customer_staging s
WHERE customer_dim.customer_id = s.customer_id
  AND customer_dim.is_current = TRUE
  AND (
      customer_dim.address != s.address OR
      customer_dim.city != s.city OR
      customer_dim.state != s.state
  );

-- Step 2: Insert new versions
INSERT INTO customer_dim
SELECT
    s.customer_id,
    s.customer_name,
    s.address,
    s.city,
    s.state,
    CURRENT_DATE as effective_date,
    DATE '9999-12-31' as end_date,
    TRUE as is_current
FROM customer_staging s
LEFT JOIN customer_dim d
    ON s.customer_id = d.customer_id
    AND d.is_current = TRUE
WHERE d.customer_id IS NULL  -- New customers
   OR (  -- Changed customers
      d.address != s.address OR
      d.city != s.city OR
      d.state != s.state
   );
```

### SCD Type 2 with Hashing (Efficient Change Detection)
```sql
-- Add hash column to dimension
ALTER TABLE customer_dim ADD COLUMN record_hash VARCHAR(64);

-- Calculate hash of change-tracked columns
UPDATE customer_staging
SET record_hash = MD5(
    CONCAT_WS('|',
        COALESCE(address, ''),
        COALESCE(city, ''),
        COALESCE(state, '')
    )
);

-- Detect changes by comparing hash
UPDATE customer_dim
SET end_date = CURRENT_DATE - 1,
    is_current = FALSE
FROM customer_staging s
WHERE customer_dim.customer_id = s.customer_id
  AND customer_dim.is_current = TRUE
  AND customer_dim.record_hash != s.record_hash;
```

## Aggregation Patterns

### Pivot Tables
```sql
-- Pivot sales by month
SELECT
    product_category,
    SUM(CASE WHEN MONTH(order_date) = 1 THEN sales_amount ELSE 0 END) as jan_sales,
    SUM(CASE WHEN MONTH(order_date) = 2 THEN sales_amount ELSE 0 END) as feb_sales,
    SUM(CASE WHEN MONTH(order_date) = 3 THEN sales_amount ELSE 0 END) as mar_sales,
    SUM(CASE WHEN MONTH(order_date) = 4 THEN sales_amount ELSE 0 END) as apr_sales
FROM sales
WHERE YEAR(order_date) = 2024
GROUP BY product_category;

-- Modern PIVOT syntax (Snowflake, SQL Server)
SELECT *
FROM sales
PIVOT (
    SUM(sales_amount)
    FOR month_name IN ('January', 'February', 'March', 'April')
) as pivoted_sales;
```

### Unpivot (Normalize Wide Tables)
```sql
-- Manual unpivot
SELECT product_category, 'January' as month, jan_sales as sales FROM monthly_sales
UNION ALL
SELECT product_category, 'February' as month, feb_sales as sales FROM monthly_sales
UNION ALL
SELECT product_category, 'March' as month, mar_sales as sales FROM monthly_sales;

-- Modern UNPIVOT syntax
SELECT product_category, month, sales
FROM monthly_sales
UNPIVOT (
    sales FOR month IN (jan_sales, feb_sales, mar_sales)
);
```

### CUBE and ROLLUP (Multidimensional Aggregation)
```sql
-- ROLLUP (hierarchical subtotals)
SELECT
    region,
    country,
    city,
    SUM(sales_amount) as total_sales
FROM sales
GROUP BY ROLLUP (region, country, city)
ORDER BY region, country, city;

-- CUBE (all possible combinations)
SELECT
    region,
    product_category,
    SUM(sales_amount) as total_sales
FROM sales
GROUP BY CUBE (region, product_category);

-- GROUPING SETS (specific combinations)
SELECT
    region,
    product_category,
    SUM(sales_amount) as total_sales
FROM sales
GROUP BY GROUPING SETS (
    (region),
    (product_category),
    (region, product_category),
    ()  -- Grand total
);
```

## Time Series Patterns

### Generate Date Dimension
```sql
-- Generate dates using recursive CTE
WITH RECURSIVE date_series AS (
    SELECT DATE '2020-01-01' as date_value
    UNION ALL
    SELECT date_value + INTERVAL '1 day'
    FROM date_series
    WHERE date_value < DATE '2030-12-31'
)
SELECT
    date_value,
    EXTRACT(YEAR FROM date_value) as year,
    EXTRACT(MONTH FROM date_value) as month,
    EXTRACT(DAY FROM date_value) as day,
    TO_CHAR(date_value, 'Day') as day_name,
    TO_CHAR(date_value, 'Month') as month_name,
    EXTRACT(QUARTER FROM date_value) as quarter,
    EXTRACT(DOW FROM date_value) as day_of_week,
    CASE WHEN EXTRACT(DOW FROM date_value) IN (0, 6) THEN TRUE ELSE FALSE END as is_weekend
FROM date_series;
```

### Fill Missing Dates (Gap Filling)
```sql
-- Create complete date series and fill gaps
WITH date_range AS (
    SELECT DATE '2024-01-01' + (ROW_NUMBER() OVER () - 1) as date_value
    FROM TABLE(GENERATOR(ROWCOUNT => 365))
)
SELECT
    d.date_value,
    COALESCE(s.sales_amount, 0) as sales_amount
FROM date_range d
LEFT JOIN daily_sales s ON d.date_value = s.sale_date
ORDER BY d.date_value;
```

### Year-over-Year Comparison
```sql
SELECT
    EXTRACT(YEAR FROM order_date) as year,
    EXTRACT(MONTH FROM order_date) as month,
    SUM(sales_amount) as current_period_sales,
    LAG(SUM(sales_amount), 12) OVER (ORDER BY order_date) as prior_year_sales,
    SUM(sales_amount) - LAG(SUM(sales_amount), 12) OVER (ORDER BY order_date) as yoy_change,
    ROUND(
        100.0 * (SUM(sales_amount) - LAG(SUM(sales_amount), 12) OVER (ORDER BY order_date)) /
        NULLIF(LAG(SUM(sales_amount), 12) OVER (ORDER BY order_date), 0),
        2
    ) as yoy_pct_change
FROM sales
GROUP BY EXTRACT(YEAR FROM order_date), EXTRACT(MONTH FROM order_date)
ORDER BY year, month;
```

## Cohort Analysis Pattern

```sql
-- User cohort retention analysis
WITH user_cohorts AS (
    SELECT
        user_id,
        DATE_TRUNC('month', MIN(order_date)) as cohort_month
    FROM orders
    GROUP BY user_id
),
cohort_activity AS (
    SELECT
        c.cohort_month,
        DATE_TRUNC('month', o.order_date) as activity_month,
        COUNT(DISTINCT o.user_id) as active_users
    FROM user_cohorts c
    JOIN orders o ON c.user_id = o.user_id
    GROUP BY c.cohort_month, DATE_TRUNC('month', o.order_date)
),
cohort_size AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT user_id) as cohort_size
    FROM user_cohorts
    GROUP BY cohort_month
)
SELECT
    ca.cohort_month,
    ca.activity_month,
    DATEDIFF(month, ca.cohort_month, ca.activity_month) as months_since_cohort,
    ca.active_users,
    cs.cohort_size,
    ROUND(100.0 * ca.active_users / cs.cohort_size, 2) as retention_rate
FROM cohort_activity ca
JOIN cohort_size cs ON ca.cohort_month = cs.cohort_month
ORDER BY ca.cohort_month, ca.activity_month;
```

## Data Quality Patterns

### Duplicate Detection
```sql
-- Find duplicates
SELECT
    id,
    COUNT(*) as duplicate_count
FROM table_name
GROUP BY id
HAVING COUNT(*) > 1;

-- Get full duplicate records
WITH duplicates AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_timestamp DESC) as rn
    FROM table_name
)
SELECT *
FROM duplicates
WHERE id IN (
    SELECT id
    FROM duplicates
    GROUP BY id
    HAVING COUNT(*) > 1
)
ORDER BY id, rn;
```

### NULL Analysis
```sql
-- Count NULLs per column
SELECT
    COUNT(*) as total_rows,
    COUNT(column1) as column1_non_null,
    COUNT(*) - COUNT(column1) as column1_null,
    ROUND(100.0 * (COUNT(*) - COUNT(column1)) / COUNT(*), 2) as column1_null_pct,
    COUNT(column2) as column2_non_null,
    COUNT(*) - COUNT(column2) as column2_null,
    ROUND(100.0 * (COUNT(*) - COUNT(column2)) / COUNT(*), 2) as column2_null_pct
FROM table_name;
```

### Referential Integrity Check
```sql
-- Check orphaned records (foreign key violations)
SELECT f.*
FROM fact_table f
LEFT JOIN dimension_table d ON f.dim_key = d.dim_key
WHERE d.dim_key IS NULL;

-- Check for missing dimension values
SELECT DISTINCT f.dim_key
FROM fact_table f
WHERE f.dim_key NOT IN (SELECT dim_key FROM dimension_table);
```

## Performance Optimization Patterns

### Avoid SELECT *
```sql
-- ❌ BAD
SELECT * FROM large_table WHERE date = '2024-01-01';

-- ✅ GOOD
SELECT id, customer_id, order_amount FROM large_table WHERE date = '2024-01-01';
```

### Use CTEs for Readability and Optimization
```sql
-- Multiple CTEs for complex logic
WITH filtered_orders AS (
    SELECT * FROM orders WHERE order_date >= '2024-01-01'
),
customer_totals AS (
    SELECT
        customer_id,
        SUM(order_amount) as total_amount
    FROM filtered_orders
    GROUP BY customer_id
),
top_customers AS (
    SELECT customer_id
    FROM customer_totals
    WHERE total_amount > 10000
)
SELECT
    o.*,
    c.customer_name
FROM filtered_orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.customer_id IN (SELECT customer_id FROM top_customers);
```

### Push-Down Predicates
```sql
-- ❌ BAD: Filter after join
SELECT o.*, c.*
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= '2024-01-01';

-- ✅ GOOD: Filter before join
SELECT o.*, c.*
FROM (
    SELECT * FROM orders WHERE order_date >= '2024-01-01'
) o
JOIN customers c ON o.customer_id = c.customer_id;
```

### Avoid Functions on Indexed Columns in WHERE
```sql
-- ❌ BAD: Function on column prevents index usage
SELECT * FROM orders WHERE YEAR(order_date) = 2024;

-- ✅ GOOD: Use range on raw column
SELECT * FROM orders
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01';
```

## Best Practices

### Naming Conventions
```sql
-- Use descriptive names
-- ❌ BAD
SELECT a, b, c FROM t1 JOIN t2 ON t1.id = t2.id;

-- ✅ GOOD
SELECT
    o.order_id,
    o.order_amount,
    c.customer_name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;
```

### Always Use Explicit JOINs
```sql
-- ❌ BAD: Implicit join (old style)
SELECT o.*, c.*
FROM orders o, customers c
WHERE o.customer_id = c.customer_id;

-- ✅ GOOD: Explicit join
SELECT o.*, c.*
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id;
```

### Handle NULLs Explicitly
```sql
-- Use COALESCE for default values
SELECT
    customer_id,
    COALESCE(phone, 'Not provided') as phone,
    COALESCE(email, 'Not provided') as email
FROM customers;

-- Use NULLIF to convert empty strings to NULL
SELECT
    customer_id,
    NULLIF(TRIM(phone), '') as phone
FROM customers;
```

### Use EXISTS instead of IN for Subqueries
```sql
-- ❌ SLOWER: IN with subquery
SELECT * FROM customers c
WHERE c.customer_id IN (SELECT customer_id FROM orders WHERE order_date >= '2024-01-01');

-- ✅ FASTER: EXISTS
SELECT * FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.customer_id = c.customer_id
    AND o.order_date >= '2024-01-01'
);
```
