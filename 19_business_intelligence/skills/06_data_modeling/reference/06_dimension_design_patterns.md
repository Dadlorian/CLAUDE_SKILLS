# Dimension Design Patterns Reference

## Overview

Dimension tables contain descriptive attributes for analysis and filtering. Well-designed dimensions are the foundation of usable, performant dimensional models.

---

## Standard Dimension Pattern

### Structure
```sql
CREATE TABLE DIM_CUSTOMER (
    -- Surrogate key (primary key for joins)
    customer_key INTEGER PRIMARY KEY,

    -- Natural business key
    customer_id VARCHAR(50) NOT NULL,

    -- Descriptive attributes
    customer_name VARCHAR(100),
    customer_type VARCHAR(20),

    -- Address attributes
    street_address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    country VARCHAR(50),

    -- Demographics
    age_range VARCHAR(20),
    income_band VARCHAR(20),
    credit_score_band VARCHAR(20),

    -- Hierarchy (denormalized)
    customer_segment VARCHAR(30),
    customer_region VARCHAR(30),
    customer_district VARCHAR(30),
    customer_territory VARCHAR(30),

    -- SCD Type 2 tracking
    effective_date DATE NOT NULL,
    expiration_date DATE NOT NULL DEFAULT '9999-12-31',
    current_flag CHAR(1) NOT NULL DEFAULT 'Y',
    version_number INTEGER NOT NULL DEFAULT 1,

    -- Audit columns
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP,
    source_system VARCHAR(50),

    UNIQUE (customer_id, effective_date)
);
```

### Design Principles
1. **Denormalized**: Include hierarchies in single table
2. **Descriptive**: Business-friendly attribute names
3. **Surrogate keys**: Artificial primary keys for joins
4. **Natural keys**: Preserve business keys
5. **Wide tables**: Many columns acceptable
6. **Text-heavy**: Contain descriptive text, not codes

---

## Date Dimension Pattern

### Definition
The most important dimension in any data warehouse. Contains one row per calendar date with extensive date attributes.

### Complete Structure
```sql
CREATE TABLE DIM_DATE (
    date_key INTEGER PRIMARY KEY,  -- YYYYMMDD format: 20240615
    date DATE NOT NULL UNIQUE,

    -- Calendar attributes
    day_number_in_month INTEGER,
    day_number_in_year INTEGER,
    day_of_week INTEGER,  -- 1=Monday, 7=Sunday
    day_name VARCHAR(10),  -- Monday, Tuesday, etc.
    day_abbreviation CHAR(3),  -- Mon, Tue, etc.

    week_number_in_year INTEGER,
    week_number_in_month INTEGER,
    week_begin_date DATE,
    week_end_date DATE,

    month_number INTEGER,  -- 1-12
    month_name VARCHAR(10),  -- January, February, etc.
    month_abbreviation CHAR(3),  -- Jan, Feb, etc.
    month_year VARCHAR(7),  -- 2024-06

    quarter_number INTEGER,  -- 1-4
    quarter_name VARCHAR(2),  -- Q1, Q2, Q3, Q4
    quarter_year VARCHAR(7),  -- 2024-Q2

    year INTEGER,  -- 2024
    year_month INTEGER,  -- 202406

    -- Fiscal calendar
    fiscal_day_number INTEGER,
    fiscal_week_number INTEGER,
    fiscal_month_number INTEGER,
    fiscal_month_name VARCHAR(10),
    fiscal_quarter_number INTEGER,
    fiscal_quarter_name VARCHAR(7),
    fiscal_year INTEGER,
    fiscal_year_month INTEGER,

    -- Flags and indicators
    is_weekday CHAR(1),  -- Y/N
    is_weekend CHAR(1),  -- Y/N
    is_holiday CHAR(1),  -- Y/N
    is_business_day CHAR(1),  -- Y/N
    is_last_day_of_month CHAR(1),
    is_last_day_of_quarter CHAR(1),
    is_last_day_of_year CHAR(1),

    holiday_name VARCHAR(50),

    -- Relative dates
    days_ago INTEGER,  -- For "last 30 days" queries
    weeks_ago INTEGER,
    months_ago INTEGER,
    years_ago INTEGER,

    -- Business calendar
    business_days_in_month INTEGER,
    business_days_in_quarter INTEGER,
    business_days_in_year INTEGER,

    -- Season (for retail)
    retail_season VARCHAR(20),  -- Spring, Summer, Fall, Winter, Holiday

    -- ISO standards
    iso_week_number INTEGER,
    iso_year INTEGER
);
```

### Population Pattern
```sql
-- Generate 10 years of dates
DECLARE @StartDate DATE = '2020-01-01';
DECLARE @EndDate DATE = '2029-12-31';

WITH DateSequence AS (
    SELECT @StartDate AS DateValue
    UNION ALL
    SELECT DATEADD(DAY, 1, DateValue)
    FROM DateSequence
    WHERE DateValue < @EndDate
)
INSERT INTO DIM_DATE (
    date_key,
    date,
    day_number_in_month,
    day_number_in_year,
    day_of_week,
    day_name,
    month_number,
    month_name,
    quarter_number,
    year,
    is_weekday,
    is_weekend
)
SELECT
    CAST(FORMAT(DateValue, 'yyyyMMdd') AS INTEGER) as date_key,
    DateValue as date,
    DATEPART(DAY, DateValue) as day_number_in_month,
    DATEPART(DAYOFYEAR, DateValue) as day_number_in_year,
    DATEPART(WEEKDAY, DateValue) as day_of_week,
    DATENAME(WEEKDAY, DateValue) as day_name,
    DATEPART(MONTH, DateValue) as month_number,
    DATENAME(MONTH, DateValue) as month_name,
    DATEPART(QUARTER, DateValue) as quarter_number,
    DATEPART(YEAR, DateValue) as year,
    CASE WHEN DATEPART(WEEKDAY, DateValue) BETWEEN 2 AND 6 THEN 'Y' ELSE 'N' END as is_weekday,
    CASE WHEN DATEPART(WEEKDAY, DateValue) IN (1,7) THEN 'Y' ELSE 'N' END as is_weekend
FROM DateSequence
OPTION (MAXRECURSION 0);
```

### Best Practices
- Pre-populate for full date range (past and future)
- Integer surrogate key in YYYYMMDD format
- Include both calendar and fiscal dates
- Add holiday flags
- Never use actual dates as foreign keys in facts
- Create separate time dimension for intraday analysis

---

## Time Dimension Pattern

### Definition
For businesses requiring intraday time analysis (24 hours × 60 minutes = 1,440 rows).

### Structure
```sql
CREATE TABLE DIM_TIME (
    time_key INTEGER PRIMARY KEY,  -- HHMMSS format: 143000
    time TIME NOT NULL UNIQUE,

    -- Hour attributes
    hour_24 INTEGER,  -- 0-23
    hour_12 INTEGER,  -- 1-12
    am_pm CHAR(2),  -- AM/PM
    hour_name VARCHAR(20),  -- 2:00 PM

    -- Minute attributes
    minute INTEGER,  -- 0-59
    minute_in_day INTEGER,  -- 0-1439

    -- Second attributes
    second INTEGER,  -- 0-59

    -- Business categorization
    time_of_day VARCHAR(20),  -- Morning, Afternoon, Evening, Night
    business_hours_flag CHAR(1),  -- Y/N (9am-5pm)
    peak_hours_flag CHAR(1),  -- Y/N (business-defined)

    -- Shift information
    shift_name VARCHAR(20),  -- First Shift, Second Shift, Third Shift
    shift_number INTEGER  -- 1, 2, 3
);
```

---

## Product Dimension Pattern

### Complete Product Dimension
```sql
CREATE TABLE DIM_PRODUCT (
    product_key INTEGER PRIMARY KEY,

    -- Business keys
    product_id VARCHAR(50) NOT NULL,
    sku VARCHAR(50),
    upc VARCHAR(20),

    -- Descriptive attributes
    product_name VARCHAR(200),
    product_description TEXT,
    brand_name VARCHAR(100),
    manufacturer_name VARCHAR(100),

    -- Denormalized hierarchy
    subcategory_name VARCHAR(100),
    category_name VARCHAR(100),
    department_name VARCHAR(100),
    division_name VARCHAR(100),

    -- Product attributes
    color VARCHAR(50),
    size VARCHAR(20),
    weight_grams DECIMAL(10,2),
    unit_of_measure VARCHAR(20),
    package_type VARCHAR(50),

    -- Pricing
    standard_cost DECIMAL(10,2),
    list_price DECIMAL(10,2),

    -- Status flags
    is_active CHAR(1),
    is_discontinued CHAR(1),
    is_promotional CHAR(1),

    -- Dates
    introduction_date DATE,
    discontinuation_date DATE,

    -- SCD Type 2
    effective_date DATE NOT NULL,
    expiration_date DATE NOT NULL DEFAULT '9999-12-31',
    current_flag CHAR(1) NOT NULL DEFAULT 'Y',

    -- Audit
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_system VARCHAR(50),

    UNIQUE (product_id, effective_date)
);
```

---

## Junk Dimension Pattern

### Definition
Consolidates low-cardinality flags and indicators into a single dimension.

### Before (Anti-Pattern)
```sql
-- Too many flags in fact table
FACT_SALES
- payment_type
- shipping_method
- gift_wrap_flag
- express_flag
- international_flag
- first_time_buyer_flag
```

### After (Junk Dimension)
```sql
CREATE TABLE DIM_TRANSACTION_FLAGS (
    transaction_flags_key INTEGER PRIMARY KEY,

    -- Payment indicators
    payment_type_code VARCHAR(10),
    payment_type_desc VARCHAR(50),

    -- Shipping indicators
    shipping_method_code VARCHAR(10),
    shipping_method_desc VARCHAR(50),
    express_flag CHAR(1),
    international_flag CHAR(1),

    -- Purchase indicators
    gift_wrap_flag CHAR(1),
    gift_message_flag CHAR(1),
    first_time_buyer_flag CHAR(1),
    loyalty_member_flag CHAR(1),

    UNIQUE (
        payment_type_code,
        shipping_method_code,
        express_flag,
        international_flag,
        gift_wrap_flag,
        gift_message_flag,
        first_time_buyer_flag,
        loyalty_member_flag
    )
);

-- Fact table now has single FK
FACT_SALES
- transaction_flags_key (FK)
```

### Loading Strategy

**Option 1: Pre-generate all combinations**
```sql
-- For 3 binary flags (2^3 = 8 combinations)
INSERT INTO DIM_TRANSACTION_FLAGS
SELECT
    ROW_NUMBER() OVER (ORDER BY a.flag, b.flag, c.flag) as transaction_flags_key,
    a.flag as gift_wrap_flag,
    b.flag as express_flag,
    c.flag as international_flag
FROM (SELECT 'Y' as flag UNION SELECT 'N') a
CROSS JOIN (SELECT 'Y' as flag UNION SELECT 'N') b
CROSS JOIN (SELECT 'Y' as flag UNION SELECT 'N') c;
```

**Option 2: Add on-demand**
```sql
-- Insert only combinations that actually occur
INSERT INTO DIM_TRANSACTION_FLAGS (
    payment_type_code, shipping_method_code, gift_wrap_flag, express_flag
)
SELECT DISTINCT
    payment_type, shipping_method, gift_wrap_flag, express_flag
FROM staging.sales
WHERE NOT EXISTS (
    SELECT 1 FROM DIM_TRANSACTION_FLAGS d
    WHERE d.payment_type_code = staging.sales.payment_type
      AND d.shipping_method_code = staging.sales.shipping_method
      AND d.gift_wrap_flag = staging.sales.gift_wrap_flag
      AND d.express_flag = staging.sales.express_flag
);
```

---

## Role-Playing Dimension Pattern

### Definition
Same dimension used multiple times in fact table with different meanings.

### Example: Date Dimension
```sql
FACT_ORDER
- order_date_key (FK to DIM_DATE)
- payment_date_key (FK to DIM_DATE)
- ship_date_key (FK to DIM_DATE)
- delivery_date_key (FK to DIM_DATE)
```

### Implementation

**Physical**: Single table, multiple foreign keys
```sql
-- Single DIM_DATE table, referenced multiple times
SELECT
    f.order_number,
    od.date as order_date,
    sd.date as ship_date,
    dd.date as delivery_date
FROM FACT_ORDER f
JOIN DIM_DATE od ON f.order_date_key = od.date_key
JOIN DIM_DATE sd ON f.ship_date_key = sd.date_key
JOIN DIM_DATE dd ON f.delivery_date_key = dd.date_key;
```

**Logical**: Views or aliases for clarity
```sql
-- Create views for each role
CREATE VIEW DIM_ORDER_DATE AS SELECT * FROM DIM_DATE;
CREATE VIEW DIM_SHIP_DATE AS SELECT * FROM DIM_DATE;
CREATE VIEW DIM_DELIVERY_DATE AS SELECT * FROM DIM_DATE;

-- BI tools see three "different" dimensions
SELECT
    f.order_number,
    od.date as order_date,
    sd.date as ship_date,
    dd.date as delivery_date
FROM FACT_ORDER f
JOIN DIM_ORDER_DATE od ON f.order_date_key = od.date_key
JOIN DIM_SHIP_DATE sd ON f.ship_date_key = sd.date_key
JOIN DIM_DELIVERY_DATE dd ON f.delivery_date_key = dd.date_key;
```

---

## Outrigger Dimension Pattern

### Definition
Normalized sub-dimension referenced from main dimension (controlled snowflaking).

### When to Use
- Large, slowly changing reference data
- Shared across multiple dimensions
- Frequent updates to reference data
- Storage optimization for very large dimensions

### Example: Geographic Hierarchy
```sql
-- Main dimension with outrigger FK
CREATE TABLE DIM_CUSTOMER (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(100),
    street_address VARCHAR(200),
    city VARCHAR(50),
    state_key INTEGER,  -- FK to outrigger
    -- other attributes
);

-- Outrigger dimension
CREATE TABLE DIM_STATE (
    state_key INTEGER PRIMARY KEY,
    state_code CHAR(2) NOT NULL,
    state_name VARCHAR(50),
    state_abbreviation CHAR(2),
    region_code VARCHAR(10),
    region_name VARCHAR(50),
    country_code CHAR(2),
    country_name VARCHAR(50),
    continent_name VARCHAR(50)
);
```

### Query Impact
```sql
-- Requires additional join
SELECT
    c.customer_name,
    s.state_name,
    s.region_name,
    SUM(f.sales_amount)
FROM FACT_SALES f
JOIN DIM_CUSTOMER c ON f.customer_key = c.customer_key
JOIN DIM_STATE s ON c.state_key = s.state_key  -- Additional join
GROUP BY c.customer_name, s.state_name, s.region_name;
```

---

## Mini-Dimension Pattern

### Definition
Rapidly changing attributes separated into smaller dimension to avoid SCD Type 2 explosion.

### Problem: Dimension Explosion
```sql
-- Customer with demographics (SCD Type 2)
-- Age updates yearly, credit score monthly → 12+ new rows/year per customer
DIM_CUSTOMER (all attributes, Type 2)
- customer_key (new key for each change)
- customer_id
- customer_name
- age  -- Changes yearly
- credit_score  -- Changes monthly
- income_band  -- Changes occasionally
```

### Solution: Mini-Dimension
```sql
-- Stable attributes (Type 2 if needed)
CREATE TABLE DIM_CUSTOMER (
    customer_key INTEGER PRIMARY KEY,  -- Durable key
    customer_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(100),
    birth_date DATE,
    signup_date DATE
);

-- Rapidly changing attributes (Type 1 or separate tracking)
CREATE TABLE DIM_CUSTOMER_DEMOGRAPHICS (
    demographics_key INTEGER PRIMARY KEY,
    age_range VARCHAR(20),  -- 18-24, 25-34, etc.
    income_band VARCHAR(20),  -- Low, Medium, High, Very High
    credit_score_band VARCHAR(20),  -- Poor, Fair, Good, Excellent
    customer_segment VARCHAR(30)  -- Derived from above
);

-- Fact table references both
CREATE TABLE FACT_SALES (
    sales_key BIGINT PRIMARY KEY,
    date_key INTEGER,
    customer_key INTEGER,  -- Stable customer reference
    demographics_key INTEGER,  -- Demographics at time of sale
    product_key INTEGER,
    sales_amount DECIMAL(12,2)
);
```

### Benefits
- Prevents dimension explosion
- Maintains historical demographic accuracy
- Stable customer key for long-term tracking
- Pre-generate mini-dimension combinations (age × income × credit)

---

## Bridge Table for Many-to-Many

### Problem: Many-to-Many Relationship
Account can have multiple customers, customer can have multiple accounts.

### Solution: Bridge Table
```sql
-- Customer dimension
CREATE TABLE DIM_CUSTOMER (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR(50),
    customer_name VARCHAR(100)
);

-- Account dimension (fact surrogate)
CREATE TABLE DIM_ACCOUNT (
    account_key INTEGER PRIMARY KEY,
    account_number VARCHAR(50),
    account_type VARCHAR(20)
);

-- Bridge table (many-to-many)
CREATE TABLE BRIDGE_ACCOUNT_CUSTOMER (
    account_key INTEGER,
    customer_key INTEGER,
    allocation_percentage DECIMAL(5,2),  -- For distributing amounts
    primary_customer_flag CHAR(1),
    weighting_factor DECIMAL(5,4),  -- 1 / customer_count to avoid double-counting
    effective_date DATE,
    expiration_date DATE,
    PRIMARY KEY (account_key, customer_key, effective_date)
);

-- Fact table
CREATE TABLE FACT_ACCOUNT_BALANCE (
    balance_key BIGINT PRIMARY KEY,
    date_key INTEGER,
    account_key INTEGER,  -- Links through bridge to customers
    balance_amount DECIMAL(15,2)
);
```

### Querying with Weighting Factor
```sql
-- Total balance by customer (with weighting to avoid double-counting)
SELECT
    c.customer_name,
    SUM(f.balance_amount * b.weighting_factor) as allocated_balance
FROM FACT_ACCOUNT_BALANCE f
JOIN BRIDGE_ACCOUNT_CUSTOMER b ON f.account_key = b.account_key
    AND f.date_key BETWEEN b.effective_date_key AND b.expiration_date_key
JOIN DIM_CUSTOMER c ON b.customer_key = c.customer_key
WHERE b.current_flag = 'Y'
GROUP BY c.customer_name;
```

### Weighting Factor Calculation
```sql
-- If account has 2 customers: weighting_factor = 0.5
-- If account has 3 customers: weighting_factor = 0.333
UPDATE BRIDGE_ACCOUNT_CUSTOMER b
SET weighting_factor = 1.0 / (
    SELECT COUNT(*)
    FROM BRIDGE_ACCOUNT_CUSTOMER b2
    WHERE b2.account_key = b.account_key
      AND b2.current_flag = 'Y'
);
```

---

## Degenerate Dimension Pattern

### Definition
Dimension attribute stored in fact table without separate dimension table.

### Examples
- Transaction numbers
- Order numbers
- Invoice numbers
- Ticket numbers

### Implementation
```sql
CREATE TABLE FACT_SALES_TRANSACTION (
    sales_transaction_key BIGINT PRIMARY KEY,
    date_key INTEGER,
    product_key INTEGER,
    customer_key INTEGER,

    -- Degenerate dimensions (no separate table)
    transaction_number VARCHAR(20) NOT NULL,
    receipt_number VARCHAR(20),
    register_number VARCHAR(10),

    quantity DECIMAL(10,2),
    amount DECIMAL(12,2)
);
```

### When to Use
- High-cardinality operational identifiers
- No descriptive attributes needed
- Used only for grouping or filtering
- Transaction/document control numbers

---

## Unknown/Missing Member Row

### Definition
Special row in every dimension to handle missing or unknown foreign keys.

### Structure
```sql
-- First row in every dimension is "Unknown"
INSERT INTO DIM_CUSTOMER VALUES (
    0,  -- customer_key
    'UNKNOWN',  -- customer_id
    'Unknown Customer',  -- customer_name
    'Unknown',  -- all other attributes set to 'Unknown', 0, or appropriate default
    ...
    '1900-01-01',  -- effective_date
    '9999-12-31',  -- expiration_date
    'Y'  -- current_flag
);

-- Use for missing/invalid references
INSERT INTO FACT_SALES
SELECT
    ...,
    COALESCE(c.customer_key, 0),  -- Use 0 if customer not found
    ...
FROM staging.sales s
LEFT JOIN DIM_CUSTOMER c ON s.customer_id = c.customer_id;
```

### Types of Special Rows

**Unknown (0)**: Truly unknown
**Not Applicable (-1)**: Dimension doesn't apply
**Missing (-2)**: Data quality issue, should have value
**TBD (-3)**: Value will be provided later

---

## Dimension Best Practices

1. **Surrogate Keys**: Always use integer surrogate keys
2. **Natural Keys**: Preserve business keys in dimension
3. **Denormalize**: Keep hierarchies in single table (star schema)
4. **Descriptive**: Use full text descriptions, not codes
5. **Wide Tables**: Many columns are acceptable
6. **Unknown Members**: Include special rows for missing data
7. **SCD Strategy**: Document Type 1, 2, or 3 per attribute
8. **Audit Columns**: Include created_date, modified_date, source_system
9. **Indexes**: Index natural keys and commonly filtered attributes
10. **Naming**: Consistent naming (DIM_ prefix, _key suffix)

## Quick Reference

| Pattern | Purpose | When to Use |
|---------|---------|-------------|
| Standard | Core dimension | Most dimensions |
| Date | Calendar analysis | Required in all warehouses |
| Time | Intraday analysis | When time-of-day matters |
| Junk | Consolidate flags | Many low-cardinality flags |
| Role-Playing | Multiple meanings | Same dimension, different roles |
| Outrigger | Normalize specific attributes | Large shared reference data |
| Mini-Dimension | Rapidly changing | Avoid SCD Type 2 explosion |
| Bridge | Many-to-many | Complex relationships |
| Degenerate | Operational IDs | Transaction/document numbers |
