# Fact Table Design Patterns Reference

## Overview

Fact tables are the central tables in dimensional models, containing numeric measurements (facts) and foreign keys to dimension tables. The grain of a fact table defines what each row represents.

---

## Transaction Fact Tables

### Definition
One row per business transaction or event at the most atomic level.

### Characteristics
- Highest level of detail
- Unpredictable row growth (driven by events)
- Sparse (not all dimension combinations occur)
- Typically additive measures
- Large row counts
- Time-stamped events

### Grain Statement
"One row per [transaction/event]"
- One row per sales transaction line item
- One row per ATM withdrawal
- One row per website clickstream event
- One row per call detail record

### Structure
```sql
CREATE TABLE FACT_SALES_TRANSACTION (
    -- Surrogate key
    sales_transaction_key BIGINT PRIMARY KEY,

    -- Foreign keys to dimensions
    date_key INTEGER NOT NULL,
    time_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    store_key INTEGER NOT NULL,
    promotion_key INTEGER NOT NULL,
    payment_method_key INTEGER NOT NULL,

    -- Degenerate dimensions (no separate dimension table)
    transaction_number VARCHAR(20) NOT NULL,
    receipt_number VARCHAR(20),

    -- Facts/Measures (additive)
    quantity DECIMAL(10,2),
    unit_price DECIMAL(10,2),
    extended_price DECIMAL(12,2),
    discount_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    total_amount DECIMAL(12,2),
    cost_amount DECIMAL(12,2),
    profit_amount DECIMAL(12,2),

    -- Audit columns
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_system VARCHAR(50)
);
```

### Example Data
```
transaction_key | date_key | product_key | customer_key | transaction_number | quantity | unit_price | total_amount
100001         | 20240615 | 5001        | 2001         | TXN-2024-000123    | 2.00     | 19.99      | 39.98
100002         | 20240615 | 5002        | 2001         | TXN-2024-000123    | 1.00     | 49.99      | 49.99
100003         | 20240615 | 5001        | 2002         | TXN-2024-000124    | 1.00     | 19.99      | 19.99
```

### Best Practices
1. **Atomic Grain**: Store at lowest level of detail
2. **Additive Facts**: Prefer fully additive measures
3. **Degenerate Dimensions**: Transaction IDs belong in fact table
4. **No Nulls**: Use "Unknown" dimension members instead
5. **Consistent Grain**: Every row represents same thing
6. **Efficient Storage**: Optimize data types for volume

### Query Patterns
```sql
-- Aggregation by dimension
SELECT
    d.date,
    p.product_category,
    SUM(f.quantity) as total_quantity,
    SUM(f.total_amount) as total_sales
FROM FACT_SALES_TRANSACTION f
JOIN DIM_DATE d ON f.date_key = d.date_key
JOIN DIM_PRODUCT p ON f.product_key = p.product_key
WHERE d.year = 2024 AND d.month = 6
GROUP BY d.date, p.product_category;

-- Drill-down to transaction detail
SELECT
    f.transaction_number,
    d.date,
    c.customer_name,
    p.product_name,
    f.quantity,
    f.total_amount
FROM FACT_SALES_TRANSACTION f
JOIN DIM_DATE d ON f.date_key = d.date_key
JOIN DIM_CUSTOMER c ON f.customer_key = c.customer_key
JOIN DIM_PRODUCT p ON f.product_key = p.product_key
WHERE c.customer_id = 'CUST-12345';
```

---

## Periodic Snapshot Fact Tables

### Definition
One row per period per entity, capturing state at regular time intervals.

### Characteristics
- Regular, predictable intervals (daily, weekly, monthly)
- Dense (rows exist for all periods and entities)
- Semi-additive measures (balances, levels)
- Predictable row growth
- Point-in-time state

### Grain Statement
"One row per [entity] per [time period]"
- One row per account per day
- One row per product per week
- One row per warehouse location per month

### Structure
```sql
CREATE TABLE FACT_ACCOUNT_BALANCE_DAILY (
    -- Surrogate key
    account_balance_key BIGINT PRIMARY KEY,

    -- Foreign keys
    date_key INTEGER NOT NULL,
    account_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    branch_key INTEGER NOT NULL,
    account_type_key INTEGER NOT NULL,

    -- Facts - Balances (semi-additive)
    beginning_balance DECIMAL(15,2),
    ending_balance DECIMAL(15,2),
    average_daily_balance DECIMAL(15,2),
    minimum_balance DECIMAL(15,2),
    maximum_balance DECIMAL(15,2),

    -- Facts - Counts (fully additive)
    transaction_count INTEGER,
    deposit_count INTEGER,
    withdrawal_count INTEGER,

    -- Facts - Amounts (fully additive)
    total_deposits DECIMAL(15,2),
    total_withdrawals DECIMAL(15,2),
    total_fees DECIMAL(10,2),
    total_interest DECIMAL(10,2),

    -- Audit columns
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_system VARCHAR(50),

    UNIQUE (date_key, account_key)
);
```

### Example Data
```
balance_key | date_key | account_key | beginning_balance | ending_balance | avg_balance | transaction_count
200001      | 20240613 | 1001        | 5000.00          | 5250.00        | 5125.00     | 3
200002      | 20240614 | 1001        | 5250.00          | 4800.00        | 5025.00     | 5
200003      | 20240615 | 1001        | 4800.00          | 5100.00        | 4950.00     | 2
```

### Semi-Additive Facts
Balance measures are semi-additive:
- ✓ Additive across accounts (sum all account balances)
- ✗ NOT additive across time (can't sum daily balances)
- Use AVG or end-of-period value for time aggregation

```sql
-- Correct: Sum balances across accounts for one day
SELECT
    d.date,
    SUM(f.ending_balance) as total_balance
FROM FACT_ACCOUNT_BALANCE_DAILY f
JOIN DIM_DATE d ON f.date_key = d.date_key
WHERE d.date = '2024-06-15'
GROUP BY d.date;

-- Correct: Average balance over time for one account
SELECT
    a.account_number,
    AVG(f.ending_balance) as avg_balance_for_month
FROM FACT_ACCOUNT_BALANCE_DAILY f
JOIN DIM_ACCOUNT a ON f.account_key = a.account_key
JOIN DIM_DATE d ON f.date_key = d.date_key
WHERE d.year = 2024 AND d.month = 6
  AND a.account_number = 'ACC-12345'
GROUP BY a.account_number;

-- WRONG: Don't sum balances across time
-- This would count the same money multiple times!
SELECT SUM(f.ending_balance) FROM FACT_ACCOUNT_BALANCE_DAILY -- ❌
```

### Loading Pattern
```sql
-- Daily snapshot load
INSERT INTO FACT_ACCOUNT_BALANCE_DAILY (
    date_key, account_key, customer_key, branch_key,
    beginning_balance, ending_balance, average_daily_balance,
    transaction_count, total_deposits, total_withdrawals
)
SELECT
    20240615 as date_key,
    a.account_key,
    c.customer_key,
    b.branch_key,
    s.beginning_balance,
    s.ending_balance,
    s.average_daily_balance,
    s.transaction_count,
    s.total_deposits,
    s.total_withdrawals
FROM staging.daily_account_snapshot s
JOIN DIM_ACCOUNT a ON s.account_number = a.account_number
JOIN DIM_CUSTOMER c ON a.customer_key = c.customer_key
JOIN DIM_BRANCH b ON a.branch_key = b.branch_key;
```

---

## Accumulating Snapshot Fact Tables

### Definition
One row per process instance, updated as the process progresses through defined milestones.

### Characteristics
- Rows are UPDATED (exception to insert-only rule)
- Multiple date foreign keys (one per milestone)
- Lag calculations (days between milestones)
- Relatively small row counts
- Tracks process/pipeline/workflow

### Grain Statement
"One row per [process instance]"
- One row per order (updated from order to fulfillment to delivery)
- One row per insurance claim
- One row per manufacturing job
- One row per student enrollment

### Structure
```sql
CREATE TABLE FACT_ORDER_FULFILLMENT (
    -- Surrogate key
    order_fulfillment_key BIGINT PRIMARY KEY,

    -- Multiple date foreign keys (milestones)
    order_date_key INTEGER,
    payment_date_key INTEGER,
    fulfillment_date_key INTEGER,
    ship_date_key INTEGER,
    delivery_date_key INTEGER,
    return_date_key INTEGER,

    -- Other dimensions
    customer_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    warehouse_key INTEGER,
    shipping_key INTEGER,

    -- Degenerate dimension
    order_number VARCHAR(20) NOT NULL,

    -- Facts - Amounts
    order_amount DECIMAL(12,2),
    tax_amount DECIMAL(10,2),
    shipping_amount DECIMAL(10,2),

    -- Facts - Lag measures (calculated from dates)
    days_to_payment INTEGER,
    days_to_fulfillment INTEGER,
    days_to_ship INTEGER,
    days_to_deliver INTEGER,
    total_days_to_deliver INTEGER,

    -- Status (changes over time)
    current_status VARCHAR(20),

    -- Audit columns
    created_date TIMESTAMP,
    last_updated_date TIMESTAMP,
    source_system VARCHAR(50),

    UNIQUE (order_number)
);
```

### Lifecycle Example
```
Initial state (order placed):
order_key | order_date_key | payment_date_key | ship_date_key | delivery_date_key | current_status
10001     | 20240610       | NULL             | NULL          | NULL              | ORDERED

After payment:
order_key | order_date_key | payment_date_key | ship_date_key | delivery_date_key | days_to_payment | current_status
10001     | 20240610       | 20240610         | NULL          | NULL              | 0               | PAID

After shipment:
order_key | order_date_key | payment_date_key | ship_date_key | delivery_date_key | days_to_ship | current_status
10001     | 20240610       | 20240610         | 20240612      | NULL              | 2            | SHIPPED

After delivery:
order_key | order_date_key | payment_date_key | ship_date_key | delivery_date_key | days_to_deliver | total_days | current_status
10001     | 20240610       | 20240610         | 20240612      | 20240615          | 3               | 5          | DELIVERED
```

### Loading Pattern
```sql
-- Insert new orders
INSERT INTO FACT_ORDER_FULFILLMENT (
    order_number, order_date_key, customer_key, product_key,
    order_amount, current_status
)
SELECT order_number, order_date_key, customer_key, product_key,
       order_amount, 'ORDERED'
FROM staging.new_orders
WHERE order_number NOT IN (SELECT order_number FROM FACT_ORDER_FULFILLMENT);

-- Update existing orders with new milestones
UPDATE FACT_ORDER_FULFILLMENT f
SET payment_date_key = s.payment_date_key,
    days_to_payment = DATEDIFF(s.payment_date, f.order_date),
    current_status = 'PAID',
    last_updated_date = CURRENT_TIMESTAMP
FROM staging.payments s
WHERE f.order_number = s.order_number
  AND f.payment_date_key IS NULL;
```

### Query Patterns
```sql
-- Average time to deliver by product category
SELECT
    p.product_category,
    AVG(f.total_days_to_deliver) as avg_days_to_deliver,
    AVG(f.days_to_ship) as avg_days_to_ship,
    COUNT(*) as order_count
FROM FACT_ORDER_FULFILLMENT f
JOIN DIM_PRODUCT p ON f.product_key = p.product_key
WHERE f.delivery_date_key IS NOT NULL
GROUP BY p.product_category;

-- Orders still in progress
SELECT
    f.order_number,
    do.date as order_date,
    c.customer_name,
    f.current_status,
    DATEDIFF(CURRENT_DATE, do.date) as days_since_order
FROM FACT_ORDER_FULFILLMENT f
JOIN DIM_DATE do ON f.order_date_key = do.date_key
JOIN DIM_CUSTOMER c ON f.customer_key = c.customer_key
WHERE f.delivery_date_key IS NULL
  AND f.current_status <> 'CANCELLED';
```

---

## Factless Fact Tables

### Definition
Fact tables with no numeric measures, capturing events, coverage, or eligibility.

### Types

#### Type 1: Event Tracking
Records that an event occurred.

```sql
CREATE TABLE FACT_STUDENT_ATTENDANCE (
    attendance_key BIGINT PRIMARY KEY,
    date_key INTEGER NOT NULL,
    student_key INTEGER NOT NULL,
    course_key INTEGER NOT NULL,
    instructor_key INTEGER NOT NULL,
    classroom_key INTEGER NOT NULL,
    time_slot_key INTEGER NOT NULL,
    attendance_status_key INTEGER NOT NULL,

    -- Optional: dummy fact for counting
    attendance_count INTEGER DEFAULT 1,

    -- Audit
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_system VARCHAR(50),

    UNIQUE (date_key, student_key, course_key, time_slot_key)
);
```

**Queries**:
```sql
-- Count attendance by student
SELECT
    s.student_name,
    COUNT(*) as days_attended
FROM FACT_STUDENT_ATTENDANCE f
JOIN DIM_STUDENT s ON f.student_key = s.student_key
JOIN DIM_DATE d ON f.date_key = d.date_key
WHERE d.year = 2024 AND d.semester = 'Spring'
GROUP BY s.student_name;

-- Attendance rate by course
SELECT
    c.course_name,
    COUNT(DISTINCT f.student_key) as unique_students,
    COUNT(*) as total_attendance_records,
    COUNT(*) / (COUNT(DISTINCT f.student_key) * COUNT(DISTINCT f.date_key)) as attendance_rate
FROM FACT_STUDENT_ATTENDANCE f
JOIN DIM_COURSE c ON f.course_key = c.course_key
GROUP BY c.course_name;
```

#### Type 2: Coverage/Eligibility
Records what could have happened (conditions, eligibility).

```sql
CREATE TABLE FACT_PROMOTION_COVERAGE (
    coverage_key BIGINT PRIMARY KEY,
    promotion_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    store_key INTEGER NOT NULL,
    start_date_key INTEGER NOT NULL,
    end_date_key INTEGER NOT NULL,

    -- Optionally include expected impact
    coverage_count INTEGER DEFAULT 1,

    -- Audit
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_system VARCHAR(50),

    UNIQUE (promotion_key, product_key, store_key)
);
```

**Queries**:
```sql
-- Which products were on promotion but had no sales?
SELECT
    p.product_name,
    prom.promotion_name,
    s.store_name
FROM FACT_PROMOTION_COVERAGE fc
JOIN DIM_PRODUCT p ON fc.product_key = p.product_key
JOIN DIM_PROMOTION prom ON fc.promotion_key = prom.promotion_key
JOIN DIM_STORE s ON fc.store_key = s.store_key
WHERE NOT EXISTS (
    SELECT 1 FROM FACT_SALES_TRANSACTION fs
    WHERE fs.product_key = fc.product_key
      AND fs.store_key = fc.store_key
      AND fs.date_key BETWEEN fc.start_date_key AND fc.end_date_key
      AND fs.promotion_key = fc.promotion_key
);
```

---

## Consolidated Fact Tables

### Definition
Multiple business processes at the same grain combined into one fact table.

### When to Use
- Same grain
- Same dimensionality
- Simplifies reporting
- Reduces join complexity

### Structure
```sql
CREATE TABLE FACT_CUSTOMER_ACTIVITY (
    activity_key BIGINT PRIMARY KEY,
    date_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    product_key INTEGER,
    channel_key INTEGER NOT NULL,

    -- Purchases
    purchase_count INTEGER DEFAULT 0,
    purchase_amount DECIMAL(12,2) DEFAULT 0,

    -- Returns
    return_count INTEGER DEFAULT 0,
    return_amount DECIMAL(12,2) DEFAULT 0,

    -- Service calls
    service_call_count INTEGER DEFAULT 0,
    service_call_duration_minutes INTEGER DEFAULT 0,

    -- Web activity
    website_visit_count INTEGER DEFAULT 0,
    page_view_count INTEGER DEFAULT 0,

    -- Email activity
    email_opened_flag CHAR(1) DEFAULT 'N',
    email_clicked_flag CHAR(1) DEFAULT 'N',

    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Benefits
- Single query for multiple metrics
- Reduced joins
- Easier cross-process analysis

### Drawbacks
- Sparse (many zeros/nulls)
- Larger row size
- Less flexible for different grains

---

## Aggregate Fact Tables

### Definition
Pre-aggregated facts at higher grain for query performance.

### Structure
```sql
-- Atomic grain: FACT_SALES_TRANSACTION (line item level)
-- Aggregate grain: FACT_SALES_DAILY (day + product + store level)

CREATE TABLE FACT_SALES_DAILY_AGGREGATE (
    sales_daily_key BIGINT PRIMARY KEY,
    date_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    store_key INTEGER NOT NULL,

    -- Aggregated facts
    transaction_count INTEGER,
    total_quantity DECIMAL(12,2),
    total_sales_amount DECIMAL(15,2),
    total_cost_amount DECIMAL(15,2),
    total_profit_amount DECIMAL(15,2),
    average_unit_price DECIMAL(10,2),

    -- Min/Max
    min_transaction_amount DECIMAL(12,2),
    max_transaction_amount DECIMAL(12,2),

    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (date_key, product_key, store_key)
);
```

### Loading Pattern
```sql
INSERT INTO FACT_SALES_DAILY_AGGREGATE (
    date_key, product_key, store_key,
    transaction_count, total_quantity, total_sales_amount,
    average_unit_price
)
SELECT
    date_key,
    product_key,
    store_key,
    COUNT(*) as transaction_count,
    SUM(quantity) as total_quantity,
    SUM(total_amount) as total_sales_amount,
    AVG(unit_price) as average_unit_price
FROM FACT_SALES_TRANSACTION
WHERE date_key = 20240615
GROUP BY date_key, product_key, store_key;
```

---

## Best Practices Summary

### Grain Declaration
1. **Explicitly state grain** in documentation
2. **One grain per fact table** (never mix)
3. **Atomic grain preferred** for flexibility
4. **Consistent grain** across all rows

### Fact Selection
1. **Additive facts preferred** (can sum across all dimensions)
2. **Semi-additive facts** clearly documented (balances, levels)
3. **Non-additive facts** avoided or stored as attributes
4. **Null facts** handled with zeros or "not applicable" logic

### Foreign Keys
1. **All dimension foreign keys NOT NULL** (use "Unknown" members)
2. **Surrogate keys** for dimension references
3. **Consistent naming** (table_name_key)
4. **Referential integrity** enforced

### Degenerate Dimensions
1. **Transaction IDs** in fact table (not separate dimension)
2. **No descriptive attributes** (those belong in proper dimensions)
3. **High cardinality** operational identifiers

### Performance
1. **Partition** by date for large fact tables
2. **Index** on foreign keys and date columns
3. **Bitmap indexes** for low-cardinality dimensions
4. **Aggregate tables** for common query patterns
5. **Columnstore indexes** for analytics workloads

## Fact Table Type Selection Matrix

| Requirement | Transaction | Periodic Snapshot | Accumulating Snapshot | Factless |
|-------------|-------------|-------------------|----------------------|----------|
| Event-level detail | ✓ | | | ✓ |
| Regular intervals | | ✓ | | |
| Process tracking | | | ✓ | |
| Balances/levels | | ✓ | | |
| Coverage/eligibility | | | | ✓ |
| Updates needed | | | ✓ | |
| Insert-only | ✓ | ✓ | | ✓ |
| Predictable size | | ✓ | ✓ | |
| Unpredictable size | ✓ | | | ✓ |
