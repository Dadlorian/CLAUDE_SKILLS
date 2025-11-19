# Slowly Changing Dimensions (SCD) Reference

## Overview

Slowly Changing Dimensions (SCD) are techniques for managing dimension attribute changes over time in data warehouses. The approach chosen impacts historical accuracy, storage requirements, and query complexity.

---

## SCD Type 0: Retain Original

### Definition
Original value is never changed. Dimension attributes are fixed at the time of first load.

### Characteristics
- No updates allowed
- Original value preserved forever
- Simplest implementation
- No history tracking

### Structure
```
DIM_PRODUCT
- product_key (PK, surrogate)
- product_id (natural key)
- original_product_name
- original_category
- original_price
```

### Use Cases
- Attributes that should never change (birth date, original value)
- Historical reference points
- Compliance requirements for original values
- Audit baseline data

### Implementation
```sql
-- Load new records only, never update
INSERT INTO DIM_PRODUCT (product_id, product_name, category)
SELECT product_id, product_name, category
FROM staging.products
WHERE product_id NOT IN (SELECT product_id FROM DIM_PRODUCT);

-- Updates are rejected or logged as errors
```

### Example
```
product_key | product_id | product_name     | category
1001        | P123       | Original Widget  | Tools
-- Product name changes to "Super Widget" - NO UPDATE occurs
```

---

## SCD Type 1: Overwrite

### Definition
Old value is overwritten with new value. No history is maintained.

### Characteristics
- Current state only
- No historical tracking
- Minimal storage
- Simple implementation
- Past facts see current dimension values

### Structure
```
DIM_CUSTOMER
- customer_key (PK, surrogate)
- customer_id (natural key)
- customer_name
- email
- address
- city
- state
- zip
- last_updated_date
```

### Use Cases
- Correcting data errors
- Attributes where history is not important
- Rapidly changing attributes where history is impractical
- Reference data that needs current values

### Implementation
```sql
-- Update existing records with new values
UPDATE DIM_CUSTOMER
SET customer_name = s.customer_name,
    email = s.email,
    address = s.address,
    last_updated_date = CURRENT_DATE
FROM staging.customers s
WHERE DIM_CUSTOMER.customer_id = s.customer_id
  AND (DIM_CUSTOMER.customer_name <> s.customer_name
       OR DIM_CUSTOMER.email <> s.email
       OR DIM_CUSTOMER.address <> s.address);
```

### Example
```
Before change:
customer_key | customer_id | customer_name | email
2001         | C456        | John Smith    | john@oldmail.com

After change (email updated):
customer_key | customer_id | customer_name | email
2001         | C456        | John Smith    | john@newmail.com
```

### Impact
- Historical facts now show current customer email
- Cannot report "sales by customer email at time of sale"
- Storage efficient
- No way to recover old values

---

## SCD Type 2: Add New Row

### Definition
Add a new row with new surrogate key when attribute changes. Most common method for tracking history.

### Characteristics
- Complete history maintained
- New row for each change
- Multiple rows per business entity
- Effective dates track validity
- Current flag for latest row
- Most complex but most powerful

### Structure
```
DIM_PRODUCT
- product_key (PK, surrogate) -- NEW key for each version
- product_id (natural key) -- same for all versions
- product_name
- category
- unit_price
- effective_date
- expiration_date
- current_flag (Y/N or 1/0)
- version_number
```

### Use Cases
- Attributes where history is critical
- Price changes
- Customer segmentation changes
- Product categorization changes
- Organizational hierarchies

### Implementation
```sql
-- Expire old record
UPDATE DIM_PRODUCT
SET expiration_date = CURRENT_DATE - 1,
    current_flag = 'N'
WHERE product_id = 'P123'
  AND current_flag = 'Y';

-- Insert new record
INSERT INTO DIM_PRODUCT (
    product_key,
    product_id,
    product_name,
    category,
    unit_price,
    effective_date,
    expiration_date,
    current_flag,
    version_number
)
VALUES (
    NEXT_VALUE_FOR product_key_seq,
    'P123',
    'Super Widget',
    'Premium Tools',
    29.99,
    CURRENT_DATE,
    '9999-12-31',
    'Y',
    2
);
```

### Example
```
Original record:
product_key | product_id | product_name  | price | effective_date | expiration_date | current_flag
1001        | P123       | Widget        | 19.99 | 2023-01-01     | 9999-12-31      | Y

After price change on 2024-06-01:
product_key | product_id | product_name  | price | effective_date | expiration_date | current_flag
1001        | P123       | Widget        | 19.99 | 2023-01-01     | 2024-05-31      | N
1002        | P123       | Widget        | 24.99 | 2024-06-01     | 9999-12-31      | Y
```

### Querying Type 2
```sql
-- Get current version only
SELECT * FROM DIM_PRODUCT
WHERE current_flag = 'Y';

-- Get version as of specific date
SELECT * FROM DIM_PRODUCT
WHERE product_id = 'P123'
  AND '2024-03-15' BETWEEN effective_date AND expiration_date;

-- Get all versions (history)
SELECT * FROM DIM_PRODUCT
WHERE product_id = 'P123'
ORDER BY effective_date;
```

### Best Practices
- Use surrogate keys (not natural keys) as foreign keys in facts
- Always include effective_date, expiration_date, current_flag
- Use '9999-12-31' or NULL for open-ended expiration
- Index on natural key + current_flag
- Handle late-arriving facts carefully

---

## SCD Type 3: Add New Column

### Definition
Add new column to store previous value. Limited history (typically one previous value).

### Characteristics
- Stores limited history (current + previous)
- No new rows
- Fixed number of historical snapshots
- Simple queries

### Structure
```
DIM_CUSTOMER
- customer_key (PK, surrogate)
- customer_id (natural key)
- customer_name
- current_segment
- previous_segment
- segment_change_date
```

### Use Cases
- Tracking one previous value
- Before/after analysis
- Limited history requirements
- Dimensional attribute with two states to compare

### Implementation
```sql
-- Update when segment changes
UPDATE DIM_CUSTOMER
SET previous_segment = current_segment,
    current_segment = 'Gold',
    segment_change_date = CURRENT_DATE
WHERE customer_id = 'C456'
  AND current_segment <> 'Gold';
```

### Example
```
Before:
customer_key | customer_id | current_segment | previous_segment | segment_change_date
2001         | C456        | Silver          | Bronze           | 2024-01-15

After promotion to Gold:
customer_key | customer_id | current_segment | previous_segment | segment_change_date
2001         | C456        | Gold            | Silver           | 2024-06-01
```

### Advantages
- Simple implementation
- No new rows (stable foreign keys)
- Easy to compare current vs previous

### Disadvantages
- Limited history (only one previous value)
- History beyond previous value is lost
- Not suitable for frequent changes

---

## SCD Type 4: Mini-Dimension

### Definition
Separate rapidly changing attributes into a separate dimension table.

### Characteristics
- Main dimension remains stable (Type 1 or 2)
- Rapidly changing attributes in separate mini-dimension
- Fact table has foreign keys to both dimensions
- Reduces main dimension growth

### Structure
```
DIM_CUSTOMER (stable attributes)
- customer_key (PK)
- customer_id
- customer_name
- birth_date
- signup_date

DIM_CUSTOMER_DEMOGRAPHICS (mini-dimension, rapidly changing)
- demographics_key (PK)
- age_range
- income_band
- credit_score_band
- customer_segment

FACT_SALES
- sale_key
- customer_key (FK to DIM_CUSTOMER)
- demographics_key (FK to DIM_CUSTOMER_DEMOGRAPHICS)
- date_key
- product_key
- amount
```

### Use Cases
- Demographics (age ranges, income bands)
- Scores and ratings that change frequently
- Calculated segmentation
- Large dimensions with subset of rapidly changing attributes

### Implementation
```sql
-- Build demographics mini-dimension with all combinations
INSERT INTO DIM_CUSTOMER_DEMOGRAPHICS
    (age_range, income_band, credit_score_band, customer_segment)
SELECT DISTINCT
    age_range,
    income_band,
    credit_score_band,
    CASE
        WHEN income_band = 'High' AND credit_score_band = 'Excellent' THEN 'Platinum'
        WHEN income_band IN ('High','Medium') THEN 'Gold'
        ELSE 'Silver'
    END as customer_segment
FROM staging.customer_attributes;

-- Fact table gets current demographics key at transaction time
INSERT INTO FACT_SALES
SELECT
    s.sale_id,
    dc.customer_key,
    dd.demographics_key,  -- Current demographics at time of sale
    s.date_key,
    s.product_key,
    s.amount
FROM staging.sales s
JOIN DIM_CUSTOMER dc ON s.customer_id = dc.customer_id
JOIN DIM_CUSTOMER_DEMOGRAPHICS dd ON
    s.age_range = dd.age_range AND
    s.income_band = dd.income_band AND
    s.credit_score_band = dd.credit_score_band;
```

### Example
```
DIM_CUSTOMER:
customer_key | customer_id | customer_name
5001         | C789        | Alice Johnson

DIM_CUSTOMER_DEMOGRAPHICS:
demographics_key | age_range | income_band | segment
101              | 25-34     | Medium      | Gold
102              | 25-34     | High        | Platinum
103              | 35-44     | High        | Platinum

FACT_SALES (Alice's purchases over time):
sale_key | customer_key | demographics_key | sale_date  | amount
S001     | 5001         | 101              | 2023-05-15 | 100.00
S002     | 5001         | 102              | 2024-02-20 | 250.00
(Alice moved from Medium to High income band)
```

---

## SCD Type 5: Mini-Dimension + Type 1 Outrigger

### Definition
Combination of Type 4 (mini-dimension) with an outrigger in the main dimension that provides current values via Type 1.

### Structure
```
DIM_CUSTOMER
- customer_key (PK)
- customer_id
- customer_name
- current_demographics_key (FK to DIM_CUSTOMER_DEMOGRAPHICS) -- Type 1 outrigger

DIM_CUSTOMER_DEMOGRAPHICS
- demographics_key (PK)
- age_range
- income_band
- segment

FACT_SALES
- customer_key (FK)
- demographics_key (FK) -- Historical value at time of transaction
```

### Use Cases
- Need both current and historical values
- Current segmentation for customer queries
- Historical segmentation for transaction analysis

### Benefits
- Query current demographics via DIM_CUSTOMER.current_demographics_key
- Query historical demographics via FACT.demographics_key
- Single customer record with current pointer

---

## SCD Type 6: Hybrid (1+2+3)

### Definition
Combination of Type 1, Type 2, and Type 3. Also called "Type 1+2+3" or "Unpredictable".

### Characteristics
- Type 2: New row for each change (history)
- Type 3: Current value column in all rows (overwrite)
- Type 1: Update current value column across all rows

### Structure
```
DIM_PRODUCT
- product_key (PK, surrogate)
- product_id (natural key)
- historical_category (Type 2 - specific to this row)
- current_category (Type 1 - updated in all rows)
- previous_category (Type 3 - one prior value)
- effective_date
- expiration_date
- current_flag
```

### Implementation
When category changes from "Tools" to "Premium Tools":

1. **Type 2**: Insert new row with new category
2. **Type 3**: Store previous category in new row
3. **Type 1**: Update current_category in ALL rows for this product_id

```sql
-- Update current_category in all rows (Type 1)
UPDATE DIM_PRODUCT
SET current_category = 'Premium Tools'
WHERE product_id = 'P123';

-- Expire old row (Type 2)
UPDATE DIM_PRODUCT
SET expiration_date = CURRENT_DATE - 1,
    current_flag = 'N'
WHERE product_id = 'P123'
  AND current_flag = 'Y';

-- Insert new row (Type 2 + Type 3)
INSERT INTO DIM_PRODUCT (
    product_key, product_id,
    historical_category,
    current_category,
    previous_category,
    effective_date, expiration_date, current_flag
)
VALUES (
    1002, 'P123',
    'Premium Tools',      -- historical (specific to this row)
    'Premium Tools',      -- current (updated in all rows)
    'Tools',              -- previous (Type 3)
    CURRENT_DATE, '9999-12-31', 'Y'
);
```

### Example
```
After first change:
product_key | product_id | historical_cat | current_cat    | previous_cat | eff_date   | exp_date   | current
1001        | P123       | Tools          | Premium Tools  | NULL         | 2023-01-01 | 2024-05-31 | N
1002        | P123       | Premium Tools  | Premium Tools  | Tools        | 2024-06-01 | 9999-12-31 | Y

After second change to "Elite Tools":
product_key | product_id | historical_cat | current_cat | previous_cat  | eff_date   | exp_date   | current
1001        | P123       | Tools          | Elite Tools | NULL          | 2023-01-01 | 2024-05-31 | N
1002        | P123       | Premium Tools  | Elite Tools | Tools         | 2024-06-01 | 2024-11-30 | N
1003        | P123       | Elite Tools    | Elite Tools | Premium Tools | 2024-12-01 | 9999-12-31 | Y
```

### Use Cases
- Need to report with both historical and current values
- Compare historical transactions with current product categorization
- "What category was this product in when sold, vs what category is it in now?"

### Query Examples
```sql
-- Sales by historical category (as it was at time of sale)
SELECT p.historical_category, SUM(f.amount)
FROM FACT_SALES f
JOIN DIM_PRODUCT p ON f.product_key = p.product_key
GROUP BY p.historical_category;

-- Sales by current category (all sales re-categorized to current)
SELECT p.current_category, SUM(f.amount)
FROM FACT_SALES f
JOIN DIM_PRODUCT p ON f.product_key = p.product_key
GROUP BY p.current_category;

-- Compare historical vs current
SELECT
    p.historical_category,
    p.current_category,
    SUM(f.amount)
FROM FACT_SALES f
JOIN DIM_PRODUCT p ON f.product_key = p.product_key
WHERE p.historical_category <> p.current_category
GROUP BY p.historical_category, p.current_category;
```

---

## SCD Type 7: Dual Type 1 and Type 2

### Definition
Two separate dimensions: one Type 1 (current values) and one Type 2 (historical values). Fact table has foreign keys to both.

### Structure
```
DIM_CUSTOMER_CURRENT (Type 1)
- customer_key (PK, durable surrogate key)
- customer_id
- customer_name
- current_segment
- current_address

DIM_CUSTOMER_HISTORY (Type 2)
- customer_history_key (PK, new key for each change)
- customer_key (FK to current, durable)
- customer_id
- customer_name
- segment
- address
- effective_date
- expiration_date

FACT_SALES
- customer_key (FK to current)
- customer_history_key (FK to historical)
```

### Benefits
- Easy access to current values without filtering on current_flag
- Complete history maintained separately
- Clear separation of concerns

---

## Comparison Matrix

| Type | History | Storage | Complexity | Use Case |
|------|---------|---------|------------|----------|
| Type 0 | None | Minimal | Very Low | Original values, never change |
| Type 1 | None | Minimal | Low | Current state only, corrections |
| Type 2 | Complete | High | Medium | Full history tracking (most common) |
| Type 3 | Limited | Low | Low | One previous value, before/after |
| Type 4 | Complete | Medium | Medium | Rapidly changing attributes |
| Type 5 | Complete + Current | Medium | High | Historical + current values |
| Type 6 | Complete + Current | High | High | Historical with current rollup |
| Type 7 | Complete | Medium | Medium | Separate current/historical |

---

## Best Practices

### Choosing SCD Type
1. **Default to Type 2** for most dimension attributes requiring history
2. **Use Type 1** for error corrections and non-historical attributes
3. **Use Type 4** for rapidly changing attributes in large dimensions
4. **Use Type 6** when need both historical and current perspectives
5. **Avoid Type 3** unless truly need only one previous value

### Implementation Guidelines
1. Always use surrogate keys as foreign keys in facts
2. Include audit columns: effective_date, expiration_date, created_date, modified_date
3. Use current_flag for easy filtering (better than querying expiration_date)
4. Use '9999-12-31' for open expiration dates (better than NULL for date range queries)
5. Index appropriately: (natural_key, current_flag), (effective_date, expiration_date)

### ETL Considerations
1. **Late-Arriving Facts**: May reference expired dimension rows
2. **Late-Arriving Dimensions**: May require back-dating effective dates
3. **Change Detection**: Use hash values or column-by-column comparison
4. **Bulk Loading**: Process changes in batches, not row-by-row

### Performance Optimization
1. Partition Type 2 dimensions by effective_date if very large
2. Index on (natural_key, current_flag) for current value lookups
3. Consider Type 7 for very large dimensions with frequent queries on current
4. Use bitmap indexes on current_flag in data warehouses

---

## Common Mistakes

1. **Using Natural Keys as Foreign Keys**
   - ❌ FACT has FK to product_id
   - ✓ FACT has FK to product_key (surrogate)

2. **No Expiration Date**
   - ❌ Only current_flag, no date ranges
   - ✓ Include effective_date and expiration_date

3. **Mixing SCD Types Inconsistently**
   - ❌ Random mix with no documentation
   - ✓ Document strategy per attribute

4. **Type 2 Explosion**
   - ❌ Type 2 on rapidly changing attributes
   - ✓ Use Type 4 (mini-dimension) instead

5. **Null Expiration Dates**
   - ❌ NULL for current rows (hard to query ranges)
   - ✓ Use '9999-12-31' for consistency
