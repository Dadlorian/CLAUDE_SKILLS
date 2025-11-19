# Data Modeling Anti-Patterns Reference

## Overview

Anti-patterns are common mistakes that appear to solve problems but create technical debt, poor performance, and maintenance challenges. This reference identifies common data modeling anti-patterns and their solutions.

---

## Dimension Anti-Patterns

### 1. Excessive Snowflaking

**Anti-Pattern**:
```sql
-- Over-normalized product dimension
DIM_PRODUCT
- product_key
- product_name
- subcategory_key (FK to DIM_SUBCATEGORY)

DIM_SUBCATEGORY
- subcategory_key
- subcategory_name
- category_key (FK to DIM_CATEGORY)

DIM_CATEGORY
- category_key
- category_name
- department_key (FK to DIM_DEPARTMENT)

DIM_DEPARTMENT
- department_key
- department_name
- division_key (FK to DIM_DIVISION)
```

**Problems**:
- Complex queries (multiple joins required)
- Poor query performance
- Difficult for business users to understand
- Minimal storage savings in modern systems
- Increased ETL complexity

**Solution** (Star Schema):
```sql
DIM_PRODUCT
- product_key
- product_name
- product_subcategory
- product_category
- product_department
- product_division
-- Denormalized hierarchy in single table
```

**When Snowflaking IS Appropriate**:
- Very large dimensions (100M+ rows) with significant redundancy
- Outrigger dimensions for shared reference data
- Specific BI tool requirements

---

### 2. NULL Foreign Keys in Facts

**Anti-Pattern**:
```sql
FACT_SALES
- date_key (NULL when date unknown)
- customer_key (NULL for anonymous purchases)
- product_key (NULL for bundled items)
- promotion_key (NULL when no promotion)
```

**Problems**:
- Breaks referential integrity
- NULL handling in aggregations
- Inconsistent behavior across databases
- Complicates queries with LEFT JOINs

**Solution**:
```sql
-- Create "Unknown" member rows in dimensions
INSERT INTO DIM_CUSTOMER VALUES (0, 'UNKNOWN', 'Unknown Customer', ...);
INSERT INTO DIM_PROMOTION VALUES (0, 'NO_PROMO', 'No Promotion', ...);

-- Facts always have valid foreign keys
FACT_SALES
- date_key NOT NULL DEFAULT 0
- customer_key NOT NULL DEFAULT 0
- product_key NOT NULL
- promotion_key NOT NULL DEFAULT 0  -- 0 = "No Promotion"
```

**Unknown Member Types**:
- **Unknown (0)**: Legitimately unknown
- **Not Applicable (-1)**: Dimension doesn't apply to this fact
- **Missing (-2)**: Data quality issue, should have value
- **To Be Determined (-3)**: Value will be supplied later

---

### 3. Smart Keys

**Anti-Pattern**:
```sql
-- Embedded meaning in keys
customer_key = 'CA-GOLD-00123'  -- State-Segment-Number
product_key = 'ELECTRONICS-TV-55-SAMSUNG-001'  -- Category-Type-Size-Brand-Seq
```

**Problems**:
- Fragile (business rules change)
- Parsing required for queries
- No protection from changes
- Difficult to join
- Length and format inconsistencies

**Solution**:
```sql
-- Surrogate keys for joins, natural keys preserved separately
DIM_CUSTOMER
- customer_key INTEGER PRIMARY KEY  -- Simple surrogate: 1, 2, 3...
- customer_id VARCHAR(50)  -- Original business key
- customer_state CHAR(2)  -- CA
- customer_segment VARCHAR(20)  -- GOLD
```

---

### 4. Dimension Attributes in Fact Tables

**Anti-Pattern**:
```sql
FACT_SALES
- date_key
- product_key
- customer_key
- product_name  -- ❌ Dimension attribute in fact
- product_category  -- ❌ Dimension attribute in fact
- customer_name  -- ❌ Dimension attribute in fact
- quantity
- amount
```

**Problems**:
- Data redundancy
- Update anomalies
- Increased fact table size
- Inconsistent values
- Violates dimensional modeling principles

**Solution**:
```sql
-- Dimension attributes ONLY in dimensions
FACT_SALES
- date_key
- product_key
- customer_key
- quantity
- amount

DIM_PRODUCT
- product_key
- product_name
- product_category

-- Join for descriptive attributes
SELECT p.product_name, p.product_category, SUM(f.amount)
FROM FACT_SALES f
JOIN DIM_PRODUCT p ON f.product_key = p.product_key
GROUP BY p.product_name, p.product_category;
```

**Exception: Degenerate Dimensions**
Transaction numbers ARE appropriate in facts (no descriptive attributes exist).

---

### 5. Fact Tables Without Facts

**Anti-Pattern**:
```sql
-- "Fact" table with no numeric measures
FACT_PRODUCT_ASSIGNMENT
- date_key
- product_key
- store_key
- category_manager_key
-- No numeric facts!
```

**Analysis**:
- This is really a dimension attribute: "Which manager is assigned?"
- Should be attribute in DIM_PRODUCT or DIM_STORE
- OR if tracking changes, use SCD Type 2 in dimension

**Solution 1**: Dimension attribute
```sql
DIM_PRODUCT
- product_key
- product_name
- category_manager_key (FK or attribute)
- category_manager_name
```

**Solution 2**: Factless fact table (if tracking event occurrence)
```sql
-- If purpose is tracking WHEN assignment was made
FACT_PRODUCT_ASSIGNMENT_EVENT
- date_key
- product_key
- store_key
- manager_key
- assignment_count INTEGER DEFAULT 1  -- Dummy fact for counting
```

---

### 6. Multiple Grains in Single Fact Table

**Anti-Pattern**:
```sql
FACT_SALES  -- Mixed grain!
- order_number
- line_number
- quantity  -- Line item level
- line_amount  -- Line item level
- order_total  -- ORDER level (wrong grain!)
- customer_lifetime_value  -- CUSTOMER level (wrong grain!)
```

**Problems**:
- Ambiguous aggregations
- Double-counting
- Data redundancy
- Confusing to users
- Incorrect metrics

**Solution**: Separate fact tables for each grain
```sql
-- Line item grain
FACT_SALES_LINE_ITEM
- order_number (degenerate)
- line_number (degenerate)
- date_key
- product_key
- customer_key
- quantity
- line_amount

-- Order grain
FACT_SALES_ORDER
- order_number (degenerate)
- order_date_key
- customer_key
- order_total
- order_item_count
- shipping_amount

-- Customer grain (periodic snapshot)
FACT_CUSTOMER_MONTHLY
- month_key
- customer_key
- orders_count
- total_sales_amount
- customer_lifetime_value
```

---

## Fact Table Anti-Patterns

### 7. Pre-Aggregated Facts in Atomic Table

**Anti-Pattern**:
```sql
FACT_SALES_TRANSACTION  -- Atomic grain: one row per line item
- transaction_key
- date_key
- product_key
- line_quantity
- line_amount
- daily_product_total  -- ❌ Aggregate at different grain
- monthly_store_total  -- ❌ Aggregate at different grain
```

**Problems**:
- Data redundancy (same aggregate repeated in multiple rows)
- Update anomalies
- Wasted storage
- Confusion about which value to use

**Solution**: Create separate aggregate fact tables
```sql
-- Atomic (base) fact table
FACT_SALES_TRANSACTION
- line_quantity
- line_amount

-- Aggregated fact table (different grain)
FACT_SALES_DAILY_PRODUCT
- date_key
- product_key
- total_quantity
- total_amount
- transaction_count
```

---

### 8. Storing Aggregates Only (No Atomic Detail)

**Anti-Pattern**:
```sql
-- Only monthly summaries, no daily or transaction detail
FACT_SALES_MONTHLY_ONLY
- month_key
- product_key
- customer_key
- total_sales
-- Cannot drill down to daily, cannot answer unforeseen questions
```

**Problems**:
- Cannot answer detailed questions
- Cannot re-aggregate differently
- Limited drill-down capability
- Future requirements blocked

**Solution**: Store atomic grain, create aggregates for performance
```sql
-- Atomic grain (required)
FACT_SALES_TRANSACTION (line item level)

-- Aggregates for performance (optional)
FACT_SALES_DAILY (derived from atomic)
FACT_SALES_MONTHLY (derived from atomic or daily)
```

**Kimball's Principle**: "Always capture data at the most atomic level possible."

---

### 9. Text Measures in Facts

**Anti-Pattern**:
```sql
FACT_SALES
- quantity INTEGER
- amount DECIMAL(12,2)
- sales_status VARCHAR(20)  -- ❌ Text "fact"
- payment_method VARCHAR(20)  -- ❌ Text "fact"
- comments TEXT  -- ❌ Text "fact"
```

**Problems**:
- Cannot aggregate text
- Should be dimensions
- Violates fact table design
- Wastes fact table space

**Solution**: Text attributes belong in dimensions
```sql
FACT_SALES
- date_key
- product_key
- customer_key
- payment_method_key  -- FK to dimension or junk dimension
- sales_status_key  -- FK to dimension or junk dimension
- quantity
- amount

DIM_PAYMENT_METHOD
- payment_method_key
- payment_method_code
- payment_method_description

-- Or use junk dimension for multiple flags
DIM_TRANSACTION_FLAGS
- transaction_flags_key
- payment_method
- sales_status
- other_flags...
```

---

### 10. Fact-to-Fact Table Joins

**Anti-Pattern**:
```sql
-- Joining two fact tables directly
SELECT
    fs.product_key,
    SUM(fs.sales_amount) as total_sales,
    SUM(fi.inventory_quantity) as total_inventory
FROM FACT_SALES fs
JOIN FACT_INVENTORY fi ON fs.product_key = fi.product_key  -- ❌ Fact-to-fact join
GROUP BY fs.product_key;
```

**Problems**:
- Cartesian explosion (wrong results)
- Different grains multiply rows
- Incorrect aggregations
- Performance issues

**Example of Problem**:
```
FACT_SALES (daily grain): 365 rows per product
FACT_INVENTORY (monthly grain): 12 rows per product
Direct join: 365 × 12 = 4,380 rows (wrong!)
```

**Solution**: Drill-across via conformed dimensions
```sql
-- Separate queries, joined in presentation layer
WITH sales AS (
    SELECT
        p.product_key,
        p.product_name,
        SUM(fs.sales_amount) as total_sales
    FROM FACT_SALES fs
    JOIN DIM_PRODUCT p ON fs.product_key = p.product_key
    JOIN DIM_DATE d ON fs.date_key = d.date_key
    WHERE d.year = 2024
    GROUP BY p.product_key, p.product_name
),
inventory AS (
    SELECT
        p.product_key,
        AVG(fi.inventory_quantity) as avg_inventory
    FROM FACT_INVENTORY fi
    JOIN DIM_PRODUCT p ON fi.product_key = p.product_key
    JOIN DIM_DATE d ON fi.date_key = d.date_key
    WHERE d.year = 2024
    GROUP BY p.product_key
)
SELECT
    s.product_name,
    s.total_sales,
    i.avg_inventory
FROM sales s
JOIN inventory i ON s.product_key = i.product_key;
```

---

## SCD Anti-Patterns

### 11. Using Natural Keys as Foreign Keys

**Anti-Pattern**:
```sql
DIM_CUSTOMER (Type 2)
- customer_key (surrogate, changes with each version)
- customer_id (natural key, same across versions)

FACT_SALES
- customer_id  -- ❌ Using natural key as FK
```

**Problem**: When new SCD Type 2 row is created, which customer_key should facts use?

**Example**:
```
DIM_CUSTOMER history:
customer_key | customer_id | customer_name | segment | eff_date   | exp_date
1001         | CUST-123    | John Smith    | Silver  | 2023-01-01 | 2024-05-31
1002         | CUST-123    | John Smith    | Gold    | 2024-06-01 | 9999-12-31

FACT_SALES:
If FK is customer_id = 'CUST-123', which version? Both match!
```

**Solution**:
```sql
FACT_SALES
- customer_key  -- ✓ Surrogate key (1001 or 1002) based on transaction date
```

---

### 12. Type 2 on Rapidly Changing Attributes

**Anti-Pattern**:
```sql
DIM_CUSTOMER (Type 2 on everything including age, credit score)
- customer_key
- customer_name
- age  -- Changes yearly → 1 new row per year
- credit_score  -- Changes monthly → 12 new rows per year
- address  -- Changes occasionally

-- Result: 12+ new dimension rows per customer per year!
```

**Problems**:
- Dimension explosion
- Most rows nearly identical
- Performance degradation
- Excessive storage

**Solution**: Mini-dimension for rapidly changing attributes
```sql
DIM_CUSTOMER (stable attributes, Type 2 if needed)
- customer_key
- customer_name
- birth_date
- address (Type 2 if history needed)

DIM_CUSTOMER_DEMOGRAPHICS (rapidly changing, Type 1 or mini-dimension)
- demographics_key
- age_range  -- Bands instead of exact age
- credit_score_band  -- Bands instead of exact score

FACT_SALES
- customer_key  -- Stable
- demographics_key  -- Points to demographics at time of sale
```

---

## Naming Anti-Patterns

### 13. Inconsistent Naming Conventions

**Anti-Pattern**:
```sql
-- Inconsistent dimension prefixes
Customer  -- No prefix
DIM_Product  -- DIM_ prefix
tblStore  -- tbl prefix
d_Promotion  -- d_ prefix

-- Inconsistent key names
customer_id (natural key in dimension, but also used as FK in facts)
product_key (surrogate key)
store_sk (surrogate key with different suffix)
```

**Problems**:
- Confusing for developers and users
- Difficult to maintain
- Error-prone joins
- Poor self-documentation

**Solution**: Consistent naming standards
```sql
-- Dimensions
DIM_CUSTOMER, DIM_PRODUCT, DIM_STORE, DIM_PROMOTION

-- Fact tables
FACT_SALES, FACT_INVENTORY, FACT_ORDER

-- Keys
DIM_CUSTOMER.customer_key (PK, surrogate)
DIM_CUSTOMER.customer_id (natural business key)
FACT_SALES.customer_key (FK to DIM_CUSTOMER.customer_key)
```

---

### 14. Cryptic Abbreviations

**Anti-Pattern**:
```sql
DIM_CUST
- cst_k
- cst_nm
- cst_typ_cd
- cst_seg_cd
- cst_st_cd
```

**Problems**:
- Difficult to understand
- Ambiguous meanings
- Training overhead
- Error-prone

**Solution**: Descriptive, business-friendly names
```sql
DIM_CUSTOMER
- customer_key
- customer_name
- customer_type_code
- customer_segment_code
- customer_state_code
```

---

## ETL and Loading Anti-Patterns

### 15. No Audit Columns

**Anti-Pattern**:
```sql
DIM_PRODUCT
- product_key
- product_name
- category
-- No audit columns!
```

**Problems**:
- Cannot track when data was loaded
- Cannot identify source system
- Difficult troubleshooting
- No lineage information

**Solution**:
```sql
DIM_PRODUCT
- product_key
- product_name
- category
-- Audit columns
- created_date TIMESTAMP
- modified_date TIMESTAMP
- source_system VARCHAR(50)
- etl_batch_id BIGINT
```

---

### 16. No Data Quality Tracking

**Anti-Pattern**:
```sql
-- Load everything from source without quality checks
INSERT INTO DIM_CUSTOMER SELECT * FROM staging.customers;
```

**Problems**:
- Bad data in warehouse
- No visibility into quality issues
- Cannot quarantine poor quality data

**Solution**:
```sql
-- Quality dimension
DIM_DATA_QUALITY
- data_quality_key
- quality_score
- quality_level (Gold, Silver, Bronze)
- validation_errors
- data_completeness_pct

FACT_SALES
- data_quality_key  -- Track quality of each transaction
```

---

## Performance Anti-Patterns

### 17. No Partitioning on Large Facts

**Anti-Pattern**:
```sql
-- Billion-row fact table with no partitioning
CREATE TABLE FACT_SALES (
    ...
) -- No partitioning scheme
```

**Problems**:
- Full table scans
- Slow queries
- Difficult maintenance
- Inefficient archiving

**Solution**:
```sql
-- Partition by date (most common query filter)
CREATE TABLE FACT_SALES (
    sales_key BIGINT,
    date_key INTEGER NOT NULL,
    ...
)
PARTITION BY RANGE (date_key) (
    PARTITION p_2024_01 VALUES LESS THAN (20240201),
    PARTITION p_2024_02 VALUES LESS THAN (20240301),
    PARTITION p_2024_03 VALUES LESS THAN (20240401),
    ...
);
```

---

### 18. Missing or Wrong Indexes

**Anti-Pattern**:
```sql
-- Fact table with only primary key index
CREATE TABLE FACT_SALES (
    sales_key BIGINT PRIMARY KEY,  -- Clustered on surrogate key
    date_key INTEGER,
    product_key INTEGER,
    customer_key INTEGER,
    ...
);
-- No indexes on foreign keys or date_key!
```

**Problems**:
- Slow joins
- Full table scans
- Poor query performance

**Solution**:
```sql
-- Appropriate indexes for fact table
CREATE TABLE FACT_SALES (
    sales_key BIGINT PRIMARY KEY,
    date_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    amount DECIMAL(12,2)
);

-- Bitmap indexes on foreign keys (data warehouse)
CREATE BITMAP INDEX idx_sales_date ON FACT_SALES(date_key);
CREATE BITMAP INDEX idx_sales_product ON FACT_SALES(product_key);
CREATE BITMAP INDEX idx_sales_customer ON FACT_SALES(customer_key);

-- Or composite index on common query patterns
CREATE INDEX idx_sales_date_product ON FACT_SALES(date_key, product_key);
```

---

## Integration Anti-Patterns

### 19. No Conformed Dimensions

**Anti-Pattern**:
```sql
-- Different customer definitions in each data mart
DATAMART_SALES.DIM_CUSTOMER (customer_id, name, region)
DATAMART_SERVICE.DIM_CUSTOMER (cust_number, cust_name, territory)
DATAMART_FINANCE.DIM_CUSTOMER (client_id, client_name, zone)
```

**Problems**:
- Cannot integrate across data marts
- Different metrics for "same" customer
- Duplicated ETL effort
- No enterprise consistency

**Solution**: Conformed dimensions
```sql
-- Single, shared customer dimension
EDW.DIM_CUSTOMER (centrally managed)
- customer_key
- customer_id (standardized)
- customer_name (standardized)
- customer_region (standardized)

-- All data marts use same dimension
DATAMART_SALES.FACT_SALES → EDW.DIM_CUSTOMER
DATAMART_SERVICE.FACT_SERVICE_CALL → EDW.DIM_CUSTOMER
DATAMART_FINANCE.FACT_PAYMENT → EDW.DIM_CUSTOMER
```

---

### 20. Bypassing the EDW/Integration Layer

**Anti-Pattern**:
```sql
-- Data marts load directly from source systems
Source System A → Data Mart 1
Source System B → Data Mart 1
Source System A → Data Mart 2 (duplicate extract)
Source System B → Data Mart 2 (duplicate extract)
```

**Problems**:
- Duplicated ETL logic
- Inconsistent business rules
- Multiple extracts from source
- No single version of truth

**Solution**: Integration layer (Inmon) or Conformed dimensions (Kimball)
```sql
-- Inmon approach: EDW hub
Source Systems → EDW (3NF, integrated) → Data Marts (dimensional)

-- Kimball approach: Conformed dimensions
Source Systems → Data Marts (with conformed dimensions managed centrally)
```

---

## Quick Reference: Anti-Pattern Checklist

### Dimension Design
- [ ] Are dimensions denormalized (star schema, not snowflake)?
- [ ] Do all dimensions have surrogate keys?
- [ ] Are natural business keys preserved?
- [ ] Are "Unknown" member rows defined?
- [ ] Are fact foreign keys always NOT NULL?

### Fact Design
- [ ] Is grain explicitly defined and consistent?
- [ ] Are facts numeric and measurable?
- [ ] Are dimension attributes excluded from facts?
- [ ] Are multiple grains separated into different tables?
- [ ] Is atomic grain preserved?

### SCD Implementation
- [ ] Do facts use surrogate keys (not natural keys)?
- [ ] Are rapidly changing attributes in mini-dimensions?
- [ ] Are effective/expiration dates included for Type 2?

### Naming and Standards
- [ ] Are naming conventions consistent?
- [ ] Are names descriptive (not cryptic abbreviations)?
- [ ] Are prefixes standard (DIM_, FACT_)?
- [ ] Are key suffixes consistent (_key, _id)?

### Performance
- [ ] Are large fact tables partitioned?
- [ ] Are appropriate indexes defined?
- [ ] Are aggregate tables created for common queries?

### Audit and Quality
- [ ] Do all tables have audit columns?
- [ ] Is data quality tracked?
- [ ] Is source system identified?
- [ ] Is ETL batch information captured?

### Integration
- [ ] Are conformed dimensions defined?
- [ ] Is there a single version of truth?
- [ ] Is duplicate ETL logic eliminated?
