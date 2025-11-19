# Data Modeling Best Practices for BI

## Modeling Approaches

### Star Schema (Recommended)
```
        Fact Table (Sales)
              │
    ┌─────────┼─────────┬─────────┐
    │         │         │         │
  Date    Product   Customer  Store
  Dim      Dim        Dim      Dim
```

**Benefits**:
- Simple to understand
- Fast queries
- Easy to extend
- Optimal for BI tools

### Snowflake Schema (Use Sparingly)
```
     Fact (Sales)
         │
    ┌────┼────┐
    │    │    │
  Date Product Customer
        │
     Category
```

**When to Use**:
- Storage constraints (rarely needed now)
- Existing normalized source
- Complex product hierarchies

## Dimension Design

### Slowly Changing Dimensions

**Type 1** (Overwrite):
```sql
-- Current value only, no history
UPDATE customers
SET city = 'New York'
WHERE customer_id = 123;
```

**Type 2** (Track History):
```sql
-- Multiple rows, date ranges
customer_id | name | city    | valid_from | valid_to | is_current
123        | John | Chicago | 2020-01-01 | 2024-10-31 | No
123        | John | New York| 2024-11-01 | 9999-12-31 | Yes
```

**Type 3** (Limited History):
```sql
-- Separate columns for current and previous
customer_id | name | current_city | previous_city
123        | John | New York    | Chicago
```

### Date Dimension
```sql
CREATE TABLE dim_date AS
SELECT
    date_id,
    date_value,
    day_of_week,
    day_name,
    week_of_year,
    month_number,
    month_name,
    quarter,
    year,
    is_weekend,
    is_holiday,
    fiscal_year,
    fiscal_quarter
FROM generate_date_series('2020-01-01', '2030-12-31');
```

## Fact Table Design

### Additive vs Non-Additive
```
Additive (can sum across all dimensions):
├─ Revenue
├─ Quantity
└─ Cost

Semi-Additive (can't sum across time):
├─ Account Balance (point in time)
└─ Inventory Level

Non-Additive (can't sum at all):
├─ Ratios (Price/Unit)
├─ Percentages
└─ Averages
```

### Grain Definition
```
Order Line Level:
- OrderID, LineNumber
- One row per product per order
- Most detailed level

Order Level:
- OrderID
- One row per order
- Pre-aggregated line details

Daily Summary:
- Date, Product, Store
- One row per combination per day
- Highest aggregation
```

## Performance Optimization

### Partitioning
```sql
-- Partition by date (common pattern)
CREATE TABLE sales (
    sale_date DATE,
    product_id INT,
    amount DECIMAL
)
PARTITION BY RANGE (sale_date) (
    PARTITION p_2023 VALUES LESS THAN ('2024-01-01'),
    PARTITION p_2024 VALUES LESS THAN ('2025-01-01')
);
```

### Indexing Strategy
```sql
-- Fact table indexes
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_product ON sales(product_id);
CREATE INDEX idx_sales_customer ON sales(customer_id);

-- Dimension table indexes
CREATE UNIQUE INDEX idx_product_pk ON dim_product(product_id);
CREATE INDEX idx_product_category ON dim_product(category);
```

### Aggregation Tables
```sql
-- Pre-aggregated monthly summary
CREATE TABLE sales_monthly AS
SELECT
    DATE_TRUNC('month', sale_date) AS month,
    product_id,
    store_id,
    SUM(amount) AS total_sales,
    COUNT(*) AS order_count,
    AVG(amount) AS avg_order_value
FROM sales
GROUP BY 1, 2, 3;
```

## Common Anti-Patterns

### ❌ One Big Table
```
sales_with_everything
├─ order_id
├─ customer_name ← Denormalized
├─ customer_city ← Denormalized
├─ product_name ← Denormalized
├─ product_category ← Denormalized
└─ ... (100+ columns)

Problems:
- Huge table size
- Difficult to maintain
- Slow queries
- Data duplication
```

### ❌ Over-Normalized
```
sales → line_items → products → sub_categories → categories → departments

Problems:
- Too many joins
- Complex queries
- Slow performance
```

### ✓ Balanced Star Schema
```
sales (fact)
├─ FK to customers (dim)
├─ FK to products (dim) ← Includes category, department
├─ FK to date (dim)
└─ FK to stores (dim)

Benefits:
- 4-5 joins max
- Clear relationships
- Good performance
```

## Checklist

- [ ] Star schema implemented
- [ ] All fact tables have date dimension
- [ ] Grain clearly defined
- [ ] Primary keys on dimensions
- [ ] Foreign keys in facts
- [ ] Appropriate indexes created
- [ ] Partitioning for large tables
- [ ] SCD strategy chosen
- [ ] Aggregation tables for performance
- [ ] Documentation complete

## Resources
- "The Data Warehouse Toolkit" - Ralph Kimball
- "Star Schema: The Complete Reference" - Christopher Adamson
- Kimball Group: https://www.kimballgroup.com/
