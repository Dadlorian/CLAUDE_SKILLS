# Data Quality Patterns for Data Warehousing Reference

## Overview

Data quality is critical for data warehouse success. Poor quality data leads to incorrect insights and lost user trust. This reference covers patterns for ensuring, monitoring, and improving data quality.

**Six Dimensions of Data Quality**:
1. **Accuracy**: Correctness of data values
2. **Completeness**: Presence of all required data
3. **Consistency**: Uniformity across sources and time
4. **Timeliness**: Data available when needed
5. **Validity**: Conformance to business rules and formats
6. **Uniqueness**: No duplicate records

---

## Data Quality Validation Patterns

### 1. NOT NULL Validation

**Pattern**: Ensure required fields are populated.

**Implementation**:
```sql
-- Database constraint
CREATE TABLE DIM_CUSTOMER (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,  -- Business key required
    customer_name VARCHAR(100) NOT NULL,  -- Name required
    email VARCHAR(100),  -- Optional
    created_date TIMESTAMP NOT NULL
);

-- ETL validation
SELECT
    'customer_id NULL' as error_type,
    COUNT(*) as error_count
FROM staging.customers
WHERE customer_id IS NULL

UNION ALL

SELECT
    'customer_name NULL' as error_type,
    COUNT(*) as error_count
FROM staging.customers
WHERE customer_name IS NULL;
```

**Error Handling**:
```sql
-- Reject records with NULL required fields
INSERT INTO reject_log
SELECT 'customer_name NULL', customer_id, CURRENT_TIMESTAMP
FROM staging.customers
WHERE customer_name IS NULL;

-- Load only valid records
INSERT INTO DIM_CUSTOMER
SELECT *
FROM staging.customers
WHERE customer_id IS NOT NULL
  AND customer_name IS NOT NULL;
```

---

### 2. Referential Integrity Validation

**Pattern**: Ensure foreign keys reference existing records.

**Database Constraints**:
```sql
CREATE TABLE FACT_SALES (
    sales_key BIGINT PRIMARY KEY,
    date_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    amount DECIMAL(12,2),
    FOREIGN KEY (date_key) REFERENCES DIM_DATE(date_key),
    FOREIGN KEY (customer_key) REFERENCES DIM_CUSTOMER(customer_key),
    FOREIGN KEY (product_key) REFERENCES DIM_PRODUCT(product_key)
);
```

**ETL Validation**:
```sql
-- Find orphaned customer references
SELECT
    'Orphaned customer_key' as error_type,
    s.customer_id,
    COUNT(*) as transaction_count
FROM staging.sales s
LEFT JOIN DIM_CUSTOMER c ON s.customer_id = c.customer_id AND c.current_flag = 'Y'
WHERE c.customer_key IS NULL
GROUP BY s.customer_id;

-- Options:
-- 1. Reject invalid records
-- 2. Create "Unknown" customer record
-- 3. Default to "Unknown" member (key = 0)
```

**Unknown Member Pattern**:
```sql
-- Insert unknown member row in every dimension
INSERT INTO DIM_CUSTOMER VALUES (
    0,  -- customer_key
    'UNKNOWN',
    'Unknown Customer',
    NULL,  -- email
    NULL,  -- phone
    '1900-01-01',  -- effective_date
    '9999-12-31',  -- expiration_date
    'Y',  -- current_flag
    'SYSTEM',  -- source_system
    CURRENT_TIMESTAMP  -- created_date
);

-- Use unknown member for missing references
INSERT INTO FACT_SALES (customer_key, ...)
SELECT
    COALESCE(c.customer_key, 0) as customer_key,  -- Default to unknown
    ...
FROM staging.sales s
LEFT JOIN DIM_CUSTOMER c ON s.customer_id = c.customer_id;
```

---

### 3. Uniqueness Validation

**Pattern**: Ensure no duplicate business keys.

**Database Constraint**:
```sql
CREATE UNIQUE INDEX idx_customer_id_unique
ON DIM_CUSTOMER(customer_id)
WHERE current_flag = 'Y';  -- Unique among current records only (for SCD Type 2)
```

**ETL Validation**:
```sql
-- Find duplicates in source
SELECT
    customer_id,
    COUNT(*) as duplicate_count
FROM staging.customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- De-duplicate strategy
WITH ranked_customers AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY modified_date DESC) as rn
    FROM staging.customers
)
SELECT * FROM ranked_customers WHERE rn = 1;  -- Keep most recent only
```

---

### 4. Value Range Validation

**Pattern**: Ensure values fall within acceptable ranges.

**Check Constraints**:
```sql
CREATE TABLE FACT_SALES (
    sales_key BIGINT PRIMARY KEY,
    quantity DECIMAL(10,2) CHECK (quantity > 0),
    unit_price DECIMAL(10,2) CHECK (unit_price >= 0),
    discount_percent DECIMAL(5,2) CHECK (discount_percent BETWEEN 0 AND 100),
    transaction_date DATE CHECK (transaction_date >= '2000-01-01')
);
```

**ETL Validation**:
```sql
-- Validate ranges
SELECT
    'Negative quantity' as error_type,
    COUNT(*) as error_count
FROM staging.sales
WHERE quantity <= 0

UNION ALL

SELECT
    'Invalid discount percent',
    COUNT(*)
FROM staging.sales
WHERE discount_percent NOT BETWEEN 0 AND 100

UNION ALL

SELECT
    'Future date',
    COUNT(*)
FROM staging.sales
WHERE transaction_date > CURRENT_DATE;
```

**Automatic Correction**:
```sql
-- Apply business rules to fix common issues
UPDATE staging.sales
SET
    quantity = ABS(quantity)  -- Fix negative quantities
WHERE quantity < 0;

UPDATE staging.sales
SET
    discount_percent = CASE
        WHEN discount_percent < 0 THEN 0
        WHEN discount_percent > 100 THEN 100
        ELSE discount_percent
    END;
```

---

### 5. Domain Validation

**Pattern**: Ensure values are from allowed set.

**Reference Data**:
```sql
-- Valid states
CREATE TABLE REF_STATE (
    state_code CHAR(2) PRIMARY KEY,
    state_name VARCHAR(50),
    country_code CHAR(2),
    is_active CHAR(1) DEFAULT 'Y'
);

-- Valid product categories
CREATE TABLE REF_PRODUCT_CATEGORY (
    category_code VARCHAR(20) PRIMARY KEY,
    category_name VARCHAR(100),
    parent_category_code VARCHAR(20),
    is_active CHAR(1) DEFAULT 'Y'
);
```

**Validation**:
```sql
-- Find invalid state codes
SELECT
    'Invalid state_code' as error_type,
    c.state_code,
    COUNT(*) as customer_count
FROM staging.customers c
LEFT JOIN REF_STATE s ON c.state_code = s.state_code AND s.is_active = 'Y'
WHERE s.state_code IS NULL
  AND c.state_code IS NOT NULL
GROUP BY c.state_code;

-- Find invalid categories
SELECT
    'Invalid category' as error_type,
    p.category,
    COUNT(*) as product_count
FROM staging.products p
LEFT JOIN REF_PRODUCT_CATEGORY c ON p.category = c.category_code AND c.is_active = 'Y'
WHERE c.category_code IS NULL
  AND p.category IS NOT NULL
GROUP BY p.category;
```

---

### 6. Format Validation

**Pattern**: Ensure values match expected patterns.

**Examples**:
```sql
-- Email format validation
SELECT
    'Invalid email format' as error_type,
    email,
    COUNT(*) as count
FROM staging.customers
WHERE email IS NOT NULL
  AND email NOT LIKE '%@%.%'  -- Simple regex
GROUP BY email;

-- Phone number format validation (U.S. pattern)
SELECT
    'Invalid phone format',
    phone,
    COUNT(*)
FROM staging.customers
WHERE phone IS NOT NULL
  AND phone NOT SIMILAR TO '\(\d{3}\) \d{3}-\d{4}'  -- (123) 456-7890
GROUP BY phone;

-- ZIP code format validation
SELECT
    'Invalid ZIP format',
    zip_code,
    COUNT(*)
FROM staging.customers
WHERE zip_code IS NOT NULL
  AND zip_code NOT SIMILAR TO '\d{5}(-\d{4})?'  -- 12345 or 12345-6789
GROUP BY zip_code;
```

**Standardization**:
```sql
-- Standardize phone numbers
UPDATE staging.customers
SET phone = REGEXP_REPLACE(phone, '[^0-9]', '', 'g')  -- Remove non-digits
WHERE phone IS NOT NULL;

-- Then format consistently
UPDATE staging.customers
SET phone = '(' || SUBSTR(phone, 1, 3) || ') ' || SUBSTR(phone, 4, 3) || '-' || SUBSTR(phone, 7, 4)
WHERE LENGTH(phone) = 10;

-- Standardize names
UPDATE staging.customers
SET customer_name = UPPER(TRIM(customer_name));
```

---

### 7. Cross-Field Validation

**Pattern**: Validate relationships between multiple fields.

**Examples**:
```sql
-- Ship date should be >= order date
SELECT
    'Ship date before order date' as error_type,
    order_id,
    order_date,
    ship_date
FROM staging.orders
WHERE ship_date < order_date;

-- Discount amount should not exceed total amount
SELECT
    'Discount exceeds total' as error_type,
    order_id,
    total_amount,
    discount_amount
FROM staging.orders
WHERE discount_amount > total_amount;

-- End date should be >= start date
SELECT
    'End date before start date',
    promotion_id,
    start_date,
    end_date
FROM staging.promotions
WHERE end_date < start_date;
```

---

## Data Quality Dimensions

### Data Quality Dimension Table

**Pattern**: Track quality metrics per record.

```sql
CREATE TABLE DIM_DATA_QUALITY (
    data_quality_key INTEGER PRIMARY KEY,
    quality_level VARCHAR(20),  -- Gold, Silver, Bronze
    completeness_score INTEGER,  -- 0-100
    accuracy_score INTEGER,  -- 0-100
    validation_errors TEXT,  -- Comma-separated list of errors
    data_quality_flags BIGINT  -- Bitmap of quality issues
);

-- Sample records
INSERT INTO DIM_DATA_QUALITY VALUES
    (1, 'Gold', 100, 100, NULL, 0),  -- Perfect quality
    (2, 'Silver', 90, 95, 'Missing optional field', 1),
    (3, 'Bronze', 70, 80, 'Invalid email, missing phone', 3),
    (0, 'Unknown', 0, 0, 'Multiple critical errors', 999);

-- Add to fact tables
ALTER TABLE FACT_SALES ADD data_quality_key INTEGER;
```

**Usage in ETL**:
```sql
-- Assign quality level based on validation results
INSERT INTO FACT_SALES (data_quality_key, ...)
SELECT
    CASE
        WHEN validation_error_count = 0 THEN 1  -- Gold
        WHEN validation_error_count BETWEEN 1 AND 2 THEN 2  -- Silver
        WHEN validation_error_count > 2 THEN 3  -- Bronze
        ELSE 0  -- Unknown
    END as data_quality_key,
    ...
FROM staging.sales_validated;
```

---

### Quality Tracking Columns

**Pattern**: Add quality metadata to dimension tables.

```sql
CREATE TABLE DIM_CUSTOMER (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR(50),
    customer_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),

    -- Data quality tracking
    data_completeness_pct DECIMAL(5,2),  -- % of fields populated
    data_quality_score INTEGER,  -- 0-100
    validation_errors VARCHAR(500),  -- List of validation issues
    is_verified CHAR(1),  -- Manual verification flag
    verified_date DATE,

    -- Standard audit
    created_date TIMESTAMP,
    modified_date TIMESTAMP,
    source_system VARCHAR(50)
);
```

**Calculate Completeness**:
```sql
UPDATE DIM_CUSTOMER
SET data_completeness_pct =
    (CASE WHEN customer_name IS NOT NULL THEN 20 ELSE 0 END +
     CASE WHEN email IS NOT NULL THEN 20 ELSE 0 END +
     CASE WHEN phone IS NOT NULL THEN 20 ELSE 0 END +
     CASE WHEN address IS NOT NULL THEN 20 ELSE 0 END +
     CASE WHEN city IS NOT NULL THEN 20 ELSE 0 END);
```

---

## Data Quality Monitoring

### Quality Dashboard Metrics

**Example Metrics Table**:
```sql
CREATE TABLE DATA_QUALITY_METRICS (
    metric_date DATE,
    table_name VARCHAR(100),
    metric_name VARCHAR(100),
    metric_value DECIMAL(15,2),
    threshold_value DECIMAL(15,2),
    threshold_exceeded CHAR(1),
    recorded_timestamp TIMESTAMP
);

-- Daily metrics collection
INSERT INTO DATA_QUALITY_METRICS
SELECT
    CURRENT_DATE,
    'DIM_CUSTOMER',
    'NULL customer_name count',
    COUNT(*),
    0,  -- Threshold: 0 nulls allowed
    CASE WHEN COUNT(*) > 0 THEN 'Y' ELSE 'N' END,
    CURRENT_TIMESTAMP
FROM DIM_CUSTOMER
WHERE customer_name IS NULL AND current_flag = 'Y';

INSERT INTO DATA_QUALITY_METRICS
SELECT
    CURRENT_DATE,
    'FACT_SALES',
    'Orphaned customer_key count',
    COUNT(*),
    100,  -- Threshold: max 100 orphans allowed
    CASE WHEN COUNT(*) > 100 THEN 'Y' ELSE 'N' END,
    CURRENT_TIMESTAMP
FROM FACT_SALES f
LEFT JOIN DIM_CUSTOMER c ON f.customer_key = c.customer_key
WHERE c.customer_key IS NULL;
```

---

### Profile Source Data

**Pattern**: Analyze source data before loading.

```sql
-- Profiling query
SELECT
    'Total records' as metric,
    COUNT(*) as value
FROM staging.customers

UNION ALL

SELECT
    'NULL customer_id',
    COUNT(*)
FROM staging.customers
WHERE customer_id IS NULL

UNION ALL

SELECT
    'NULL customer_name',
    COUNT(*)
FROM staging.customers
WHERE customer_name IS NULL

UNION ALL

SELECT
    'Duplicate customer_id',
    COUNT(DISTINCT customer_id) - COUNT(*)
FROM staging.customers

UNION ALL

SELECT
    'Invalid email format',
    COUNT(*)
FROM staging.customers
WHERE email NOT LIKE '%@%.%'

UNION ALL

SELECT
    'Records outside expected date range',
    COUNT(*)
FROM staging.customers
WHERE created_date < '2000-01-01' OR created_date > CURRENT_DATE + INTERVAL '1 day';
```

---

### Data Quality Reconciliation

**Pattern**: Reconcile counts and totals between source and target.

```sql
CREATE TABLE RECONCILIATION_LOG (
    load_date DATE,
    source_system VARCHAR(50),
    source_table VARCHAR(100),
    target_table VARCHAR(100),
    source_count BIGINT,
    target_count BIGINT,
    variance BIGINT,
    source_sum DECIMAL(20,2),
    target_sum DECIMAL(20,2),
    sum_variance DECIMAL(20,2),
    reconciliation_status VARCHAR(20),  -- PASS, FAIL
    recorded_timestamp TIMESTAMP
);

-- Daily reconciliation
INSERT INTO RECONCILIATION_LOG
SELECT
    CURRENT_DATE,
    'ERP_SYSTEM',
    'SOURCE.ORDERS',
    'FACT_SALES',
    (SELECT COUNT(*) FROM source.orders WHERE order_date = CURRENT_DATE - 1),
    (SELECT COUNT(*) FROM FACT_SALES WHERE date_key = TO_CHAR(CURRENT_DATE - 1, 'YYYYMMDD')::INTEGER),
    (SELECT COUNT(*) FROM source.orders WHERE order_date = CURRENT_DATE - 1) -
    (SELECT COUNT(*) FROM FACT_SALES WHERE date_key = TO_CHAR(CURRENT_DATE - 1, 'YYYYMMDD')::INTEGER),
    (SELECT SUM(order_total) FROM source.orders WHERE order_date = CURRENT_DATE - 1),
    (SELECT SUM(total_amount) FROM FACT_SALES WHERE date_key = TO_CHAR(CURRENT_DATE - 1, 'YYYYMMDD')::INTEGER),
    (SELECT SUM(order_total) FROM source.orders WHERE order_date = CURRENT_DATE - 1) -
    (SELECT SUM(total_amount) FROM FACT_SALES WHERE date_key = TO_CHAR(CURRENT_DATE - 1, 'YYYYMMDD')::INTEGER),
    CASE
        WHEN ABS(variance) = 0 AND ABS(sum_variance) < 0.01 THEN 'PASS'
        ELSE 'FAIL'
    END,
    CURRENT_TIMESTAMP;
```

---

## Error Handling Patterns

### Reject/Quarantine Pattern

**Pattern**: Separate invalid records for review.

```sql
-- Reject table (same structure as target + error info)
CREATE TABLE REJECT_DIM_CUSTOMER (
    customer_id VARCHAR(50),
    customer_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    reject_reason VARCHAR(500),
    reject_date TIMESTAMP,
    source_record TEXT  -- JSON or XML of full source record
);

-- ETL: Load valid records, reject invalid
-- Valid records
INSERT INTO DIM_CUSTOMER (customer_id, customer_name, email, phone)
SELECT customer_id, customer_name, email, phone
FROM staging.customers
WHERE customer_id IS NOT NULL
  AND customer_name IS NOT NULL
  AND email LIKE '%@%.%';

-- Invalid records
INSERT INTO REJECT_DIM_CUSTOMER
SELECT
    customer_id,
    customer_name,
    email,
    phone,
    CASE
        WHEN customer_id IS NULL THEN 'Missing customer_id'
        WHEN customer_name IS NULL THEN 'Missing customer_name'
        WHEN email NOT LIKE '%@%.%' THEN 'Invalid email format'
    END as reject_reason,
    CURRENT_TIMESTAMP,
    ROW_TO_JSON(staging.customers.*) as source_record
FROM staging.customers
WHERE customer_id IS NULL
   OR customer_name IS NULL
   OR email NOT LIKE '%@%.%';
```

---

### Correction Pattern

**Pattern**: Automatically fix common data quality issues.

```sql
-- Create correction rules table
CREATE TABLE DATA_CORRECTION_RULES (
    rule_id INTEGER PRIMARY KEY,
    rule_name VARCHAR(100),
    table_name VARCHAR(100),
    column_name VARCHAR(100),
    condition TEXT,
    correction_logic TEXT,
    is_active CHAR(1),
    created_date TIMESTAMP
);

-- Example rules
INSERT INTO DATA_CORRECTION_RULES VALUES
    (1, 'Trim whitespace', 'DIM_CUSTOMER', 'customer_name',
     'customer_name LIKE ''% '' OR customer_name LIKE '' %''',
     'TRIM(customer_name)', 'Y', CURRENT_TIMESTAMP),
    (2, 'Uppercase names', 'DIM_CUSTOMER', 'customer_name',
     NULL, 'UPPER(customer_name)', 'Y', CURRENT_TIMESTAMP),
    (3, 'Fix negative quantities', 'FACT_SALES', 'quantity',
     'quantity < 0', 'ABS(quantity)', 'Y', CURRENT_TIMESTAMP);

-- Apply corrections
UPDATE staging.customers
SET customer_name = UPPER(TRIM(customer_name));

UPDATE staging.sales
SET quantity = ABS(quantity)
WHERE quantity < 0;
```

---

## Best Practices

### Prevention
1. **Define quality rules** upfront with business
2. **Validate at source** when possible
3. **Implement constraints** (NOT NULL, CHECK, FK)
4. **Standardize early** in ETL process
5. **Use reference data** for domain validation

### Detection
1. **Profile source data** before loading
2. **Monitor metrics** daily
3. **Reconcile** source to target
4. **Alert on thresholds** exceeded
5. **Track trends** over time

### Correction
1. **Automated fixes** for known patterns
2. **Quarantine** invalid records
3. **Manual review** process for rejects
4. **Root cause** analysis for recurring issues
5. **Feedback to source** systems

### Monitoring
1. **Quality dashboards** for visibility
2. **Quality dimensions** in data model
3. **Trend analysis** (improving or degrading?)
4. **SLA tracking** for data freshness
5. **Regular audits** of data quality

---

## Quick Reference Checklist

- [ ] NOT NULL validation for required fields
- [ ] Referential integrity checked
- [ ] Uniqueness constraints on business keys
- [ ] Value range validation
- [ ] Domain validation against reference data
- [ ] Format validation and standardization
- [ ] Cross-field validation
- [ ] Data quality dimension in fact tables
- [ ] Quality metrics tracked and monitored
- [ ] Reconciliation between source and target
- [ ] Reject/quarantine process for invalid records
- [ ] Automated correction rules for common issues
- [ ] Quality dashboard for visibility
- [ ] Regular data profiling
- [ ] Root cause analysis for quality issues
