# Slowly Changing Dimensions (SCD) Implementation Guide

Comprehensive reference for implementing all SCD types with SQL examples and best practices.

## SCD Type 0: Retain Original

### Concept
Never update the attribute value; retain the original forever.

### Use Cases
- Birth date
- Original credit score at account opening
- Hire date
- Account opening date

### Implementation

```sql
CREATE TABLE customer_dim (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR(20),
    customer_name VARCHAR(100),

    -- Type 0 attributes (never change)
    birth_date DATE,
    original_signup_date DATE,
    original_country VARCHAR(50),

    -- Other attributes...
    current_email VARCHAR(100)
);

-- Update logic: Simply don't update these columns
UPDATE customer_dim
SET current_email = 'new@email.com'  -- Can update other columns
WHERE customer_id = 'C001';
-- birth_date, original_signup_date remain unchanged
```

## SCD Type 1: Overwrite

### Concept
Overwrite the old value with the new value; no history retention.

### Use Cases
- Corrections to data errors
- Non-critical attribute changes
- Email address updates
- Phone number updates
- Current status flags

### Implementation

```sql
CREATE TABLE customer_dim (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR(20),
    customer_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(200),
    updated_datetime TIMESTAMP
);

-- Simple update
UPDATE customer_dim
SET email = 'newemail@example.com',
    updated_datetime = CURRENT_TIMESTAMP
WHERE customer_id = 'C001';
```

**Before Update:**
```
customer_key | customer_id | email           | phone
1           | C001        | old@example.com | 555-1234
```

**After Update:**
```
customer_key | customer_id | email           | phone
1           | C001        | new@example.com | 555-1234
```

### Pros & Cons
✅ Simple to implement
✅ Minimal storage requirements
✅ Easy to understand
❌ No historical tracking
❌ Can't analyze trends over time
❌ Data loss on updates

## SCD Type 2: Add New Row

### Concept
Insert a new row for each change; maintain full history with effective dates.

### Use Cases
- Customer address changes
- Product category changes
- Pricing changes
- Status changes requiring historical analysis
- Most common SCD type

### Implementation - Basic

```sql
CREATE TABLE customer_dim (
    customer_key INTEGER PRIMARY KEY,        -- Surrogate key (auto-increment)
    customer_id VARCHAR(20),                 -- Natural key (business key)
    customer_name VARCHAR(100),
    address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(2),

    -- SCD Type 2 tracking columns
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN,

    -- Audit columns
    created_datetime TIMESTAMP,
    updated_datetime TIMESTAMP
);

-- Create index on natural key + is_current for lookups
CREATE INDEX idx_customer_current ON customer_dim(customer_id, is_current);
```

### Insert New Record Process

```sql
-- Step 1: Expire current record
UPDATE customer_dim
SET end_date = CURRENT_DATE - INTERVAL '1 day',
    is_current = FALSE,
    updated_datetime = CURRENT_TIMESTAMP
WHERE customer_id = 'C001'
  AND is_current = TRUE;

-- Step 2: Insert new record
INSERT INTO customer_dim (
    customer_id,
    customer_name,
    address,
    city,
    state,
    effective_date,
    end_date,
    is_current,
    created_datetime
)
VALUES (
    'C001',
    'John Doe',
    '456 New Street',      -- New address
    'Boston',              -- New city
    'MA',
    CURRENT_DATE,
    DATE '9999-12-31',     -- Far future date
    TRUE,
    CURRENT_TIMESTAMP
);
```

**Historical Tracking Example:**
```
customer_key | customer_id | city        | effective_date | end_date   | is_current
1           | C001        | New York    | 2020-01-01    | 2023-06-30 | false
2           | C001        | Los Angeles | 2023-07-01    | 2024-02-14 | false
3           | C001        | Boston      | 2024-02-15    | 9999-12-31 | true
```

### Querying Type 2 Dimensions

```sql
-- Get current record
SELECT *
FROM customer_dim
WHERE customer_id = 'C001'
  AND is_current = TRUE;

-- Get record as of specific date
SELECT *
FROM customer_dim
WHERE customer_id = 'C001'
  AND effective_date <= '2023-08-01'
  AND end_date >= '2023-08-01';

-- Get all history for a customer
SELECT *
FROM customer_dim
WHERE customer_id = 'C001'
ORDER BY effective_date;

-- Join facts to dimension at transaction date
SELECT
    f.order_date,
    f.order_amount,
    c.city,
    c.state
FROM sales_fact f
JOIN customer_dim c
    ON f.customer_key = c.customer_key
WHERE f.order_date BETWEEN c.effective_date AND c.end_date;
```

### Merge Statement for Type 2 (Advanced)

```sql
-- Snowflake/Modern Warehouse MERGE for SCD Type 2
MERGE INTO customer_dim AS target
USING customer_staging AS source
ON target.customer_id = source.customer_id
   AND target.is_current = TRUE

WHEN MATCHED AND (
    target.address <> source.address OR
    target.city <> source.city
) THEN
    UPDATE SET
        end_date = CURRENT_DATE - INTERVAL '1 day',
        is_current = FALSE,
        updated_datetime = CURRENT_TIMESTAMP

WHEN NOT MATCHED THEN
    INSERT (
        customer_id,
        customer_name,
        address,
        city,
        effective_date,
        end_date,
        is_current,
        created_datetime
    )
    VALUES (
        source.customer_id,
        source.customer_name,
        source.address,
        source.city,
        CURRENT_DATE,
        DATE '9999-12-31',
        TRUE,
        CURRENT_TIMESTAMP
    );

-- Insert new versions for changed records
INSERT INTO customer_dim (
    customer_id,
    customer_name,
    address,
    city,
    effective_date,
    end_date,
    is_current,
    created_datetime
)
SELECT
    s.customer_id,
    s.customer_name,
    s.address,
    s.city,
    CURRENT_DATE,
    DATE '9999-12-31',
    TRUE,
    CURRENT_TIMESTAMP
FROM customer_staging s
JOIN customer_dim d
    ON s.customer_id = d.customer_id
WHERE d.is_current = FALSE
  AND d.end_date = CURRENT_DATE - INTERVAL '1 day';
```

## SCD Type 3: Add New Attribute

### Concept
Add columns to store previous value(s); limited history (usually just one previous value).

### Use Cases
- Need to track only one previous value
- Before/after analysis
- Product category reassignments
- Territory changes
- Limited storage/simple requirements

### Implementation

```sql
CREATE TABLE customer_dim (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR(20),
    customer_name VARCHAR(100),

    -- Current values
    current_city VARCHAR(50),
    current_state VARCHAR(2),
    current_country VARCHAR(50),

    -- Previous values (Type 3)
    previous_city VARCHAR(50),
    previous_state VARCHAR(2),
    previous_country VARCHAR(50),

    -- Change tracking
    location_change_date DATE,

    updated_datetime TIMESTAMP
);
```

### Update Logic

```sql
-- Update with previous value preservation
UPDATE customer_dim
SET previous_city = current_city,
    previous_state = current_state,
    current_city = 'Boston',
    current_state = 'MA',
    location_change_date = CURRENT_DATE,
    updated_datetime = CURRENT_TIMESTAMP
WHERE customer_id = 'C001';
```

**Before Update:**
```
customer_key | customer_id | current_city | previous_city | current_state | previous_state
1           | C001        | Los Angeles  | New York      | CA           | NY
```

**After Update:**
```
customer_key | customer_id | current_city | previous_city | current_state | previous_state
1           | C001        | Boston       | Los Angeles   | MA           | CA
```

### Querying Type 3

```sql
-- Customers who moved from CA to MA
SELECT customer_id, customer_name
FROM customer_dim
WHERE previous_state = 'CA'
  AND current_state = 'MA';

-- Compare current vs previous
SELECT
    customer_id,
    current_city,
    previous_city,
    location_change_date,
    DATEDIFF(day, location_change_date, CURRENT_DATE) as days_in_current_city
FROM customer_dim
WHERE previous_city IS NOT NULL;
```

## SCD Type 4: Add History Table

### Concept
Keep current data in main dimension, store history in separate history table.

### Use Cases
- Reduce main dimension size
- Separate current/historical query patterns
- Performance optimization
- Audit trail requirements

### Implementation

```sql
-- Current dimension (Type 1 style)
CREATE TABLE customer_dim (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR(20) UNIQUE,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(2),
    updated_datetime TIMESTAMP
);

-- Separate history table
CREATE TABLE customer_dim_history (
    history_key INTEGER PRIMARY KEY,
    customer_key INTEGER,
    customer_id VARCHAR(20),
    customer_name VARCHAR(100),
    email VARCHAR(100),
    address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(2),
    effective_date DATE,
    end_date DATE,
    change_reason VARCHAR(200),
    created_datetime TIMESTAMP,

    FOREIGN KEY (customer_key) REFERENCES customer_dim(customer_key)
);
```

### Update Logic with History

```sql
-- Step 1: Insert current state into history
INSERT INTO customer_dim_history (
    customer_key,
    customer_id,
    customer_name,
    email,
    address,
    city,
    state,
    effective_date,
    end_date,
    change_reason,
    created_datetime
)
SELECT
    customer_key,
    customer_id,
    customer_name,
    email,
    address,
    city,
    state,
    LAG(updated_datetime, 1, created_datetime) OVER (ORDER BY updated_datetime),
    updated_datetime,
    'Address change',
    CURRENT_TIMESTAMP
FROM customer_dim
WHERE customer_id = 'C001';

-- Step 2: Update current dimension
UPDATE customer_dim
SET address = '456 New Street',
    city = 'Boston',
    state = 'MA',
    updated_datetime = CURRENT_TIMESTAMP
WHERE customer_id = 'C001';
```

### Querying Type 4

```sql
-- Current data (fast)
SELECT * FROM customer_dim WHERE customer_id = 'C001';

-- Historical data
SELECT * FROM customer_dim_history WHERE customer_id = 'C001' ORDER BY effective_date;

-- All data (current + history)
SELECT customer_id, address, city, state, updated_datetime as effective_date, NULL as end_date
FROM customer_dim
WHERE customer_id = 'C001'
UNION ALL
SELECT customer_id, address, city, state, effective_date, end_date
FROM customer_dim_history
WHERE customer_id = 'C001'
ORDER BY effective_date DESC;
```

## SCD Type 5: Mini-Dimension

### Concept
Split rapidly changing attributes into separate "mini-dimension" to avoid dimension explosion.

### Use Cases
- Demographic attributes (age bands, income ranges)
- Credit score bands
- Behavioral segments
- Any high-volatility attributes

### Implementation

```sql
-- Main customer dimension (stable attributes)
CREATE TABLE customer_dim (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR(20),
    customer_name VARCHAR(100),
    birth_date DATE,
    gender VARCHAR(10),
    -- Stable attributes only
    created_datetime TIMESTAMP
);

-- Mini-dimension for rapidly changing attributes
CREATE TABLE customer_demographic_dim (
    demographic_key INTEGER PRIMARY KEY,
    age_band VARCHAR(20),        -- 18-25, 26-35, etc.
    income_range VARCHAR(20),    -- 0-50K, 50K-100K, etc.
    credit_score_band VARCHAR(20), -- Poor, Fair, Good, Excellent
    customer_segment VARCHAR(50)   -- Value, Growth, At-Risk, etc.
);

-- Fact table references both
CREATE TABLE sales_fact (
    date_key INTEGER,
    customer_key INTEGER,
    demographic_key INTEGER,  -- Points to mini-dimension
    product_key INTEGER,
    amount DECIMAL(10,2)
);

-- Optional: Track demographic history
CREATE TABLE customer_demographic_bridge (
    customer_key INTEGER,
    demographic_key INTEGER,
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN,
    PRIMARY KEY (customer_key, effective_date)
);
```

### Querying Type 5

```sql
-- Sales by customer segment (using mini-dimension)
SELECT
    d.customer_segment,
    d.age_band,
    SUM(f.amount) as total_sales
FROM sales_fact f
JOIN customer_demographic_dim d ON f.demographic_key = d.demographic_key
WHERE f.date_key >= 20240101
GROUP BY d.customer_segment, d.age_band;
```

## SCD Type 6: Hybrid (Type 1 + 2 + 3)

### Concept
Combine Type 1 (overwrite), Type 2 (history), and Type 3 (previous value) for flexible analysis.

### Use Cases
- Need full history AND current value in all rows
- Enable trend analysis AND current state analysis
- Complex reporting requirements

### Implementation

```sql
CREATE TABLE customer_dim (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR(20),
    customer_name VARCHAR(100),

    -- Type 1: Always current (overwritten in all rows)
    current_email VARCHAR(100),
    current_phone VARCHAR(20),
    current_status VARCHAR(20),

    -- Type 2: Historical values
    historical_address VARCHAR(200),
    historical_city VARCHAR(50),
    historical_state VARCHAR(2),

    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN,

    -- Type 3: Previous value
    previous_state VARCHAR(2),
    state_change_date DATE
);
```

### Update Logic for Type 6

```sql
-- Step 1: Update Type 1 attributes across ALL rows for this customer
UPDATE customer_dim
SET current_email = 'newemail@example.com',
    current_status = 'Active'
WHERE customer_id = 'C001';

-- Step 2: Type 2 - Expire current row
UPDATE customer_dim
SET end_date = CURRENT_DATE - INTERVAL '1 day',
    is_current = FALSE
WHERE customer_id = 'C001'
  AND is_current = TRUE;

-- Step 3: Type 2 + Type 3 - Insert new row
INSERT INTO customer_dim (
    customer_id,
    customer_name,
    current_email,           -- Type 1 (same across all rows)
    current_phone,          -- Type 1
    current_status,         -- Type 1
    historical_address,     -- Type 2 (new value)
    historical_city,        -- Type 2
    historical_state,       -- Type 2
    previous_state,         -- Type 3 (from previous row)
    state_change_date,      -- Type 3
    effective_date,
    end_date,
    is_current
)
SELECT
    'C001',
    customer_name,
    'newemail@example.com',  -- Current value
    current_phone,
    'Active',
    '789 New Address',       -- New historical value
    'Boston',
    'MA',
    historical_state,        -- Previous state from old current row
    CURRENT_DATE,
    CURRENT_DATE,
    DATE '9999-12-31',
    TRUE
FROM customer_dim
WHERE customer_id = 'C001'
  AND is_current = FALSE
  AND end_date = CURRENT_DATE - INTERVAL '1 day';
```

**Example Data:**
```
customer_key | customer_id | current_email  | historical_city | previous_city | effective_date | is_current
1           | C001        | new@email.com  | New York       | NULL         | 2020-01-01    | false
2           | C001        | new@email.com  | Los Angeles    | New York     | 2023-07-01    | false
3           | C001        | new@email.com  | Boston         | Los Angeles  | 2024-02-15    | true
```

### Benefits of Type 6

✅ Current values always available (no joins needed)
✅ Full historical tracking
✅ Previous value for comparisons
✅ Flexible analysis options

## Choosing the Right SCD Type

| SCD Type | History Tracking | Storage | Complexity | Common Use |
|----------|-----------------|---------|------------|------------|
| Type 0   | None (frozen)   | Low     | Very Low   | Birth dates, original values |
| Type 1   | None            | Low     | Low        | Corrections, non-critical changes |
| Type 2   | Full            | High    | Medium     | Most common, full history needed |
| Type 3   | Limited (1-2)   | Low     | Low        | Simple before/after analysis |
| Type 4   | Full (separate) | High    | Medium     | Performance optimization |
| Type 5   | Full (mini-dim) | Medium  | High       | Rapidly changing attributes |
| Type 6   | Full + Current  | High    | High       | Complex reporting needs |

## Best Practices

### General Guidelines
1. **Use Type 2 as default** for most slowly changing attributes
2. **Use Type 1 for corrections** and non-historical data
3. **Combine types** in same dimension based on attribute needs
4. **Always use surrogate keys** for Type 2
5. **Index properly**: (natural_key, is_current) for Type 2

### Performance Optimization
1. Partition Type 2 dimensions by effective_date
2. Create indexed views for "current only" queries
3. Use materialized views for complex Type 6 queries
4. Consider Type 4 for very large dimensions
5. Archive old Type 2 history if not frequently accessed

### Data Quality
1. Validate date ranges don't overlap
2. Ensure exactly one is_current = TRUE per natural key
3. Use constraints: end_date > effective_date
4. Implement data quality tests in dbt or Great Expectations
5. Monitor dimension growth (Type 2 can grow quickly)

### Common Pitfalls
❌ Using natural keys in fact tables (use surrogate keys!)
❌ Not indexing (natural_key, is_current)
❌ Forgetting to expire old rows in Type 2
❌ Using NULL instead of 9999-12-31 for open end_date
❌ Mixing SCD types inconsistently across similar attributes
