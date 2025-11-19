# Transaction Fact Tables Guide

## Purpose
Capture individual business events at most atomic level.

## Characteristics
- One row per event/transaction
- Highest granularity
- Unpredictable row growth
- Sparse (not all dimension combinations)
- Additive measures
- Insert-only

## Examples
- Retail sales (one row per line item)
- ATM withdrawals (one row per withdrawal)
- Web clicks (one row per page view)
- Phone calls (one row per call)

## Design

### Grain Declaration
"One row per [specific event]"

Example: "One row per product per sales transaction line item"

### Structure
```sql
FACT_SALES_TRANSACTION
- sales_transaction_key (PK, surrogate)
-- Foreign keys
- date_key
- time_key
- customer_key
- product_key
- store_key
- cashier_key
-- Degenerate dimensions
- transaction_number
- receipt_number
-- Additive facts
- quantity
- unit_price
- extended_price
- discount_amount
- tax_amount
- total_amount
```

## Loading Pattern
Insert-only (never update):
```sql
INSERT INTO FACT_SALES_TRANSACTION
SELECT 
  NEXT_VALUE_FOR sales_key_seq,
  d.date_key,
  c.customer_key,
  p.product_key,
  s.quantity,
  s.amount
FROM staging.sales s
JOIN DIM_DATE d ON s.transaction_date = d.date
JOIN DIM_CUSTOMER c ON s.customer_id = c.customer_id
  AND s.transaction_date BETWEEN c.effective_date AND c.expiration_date
JOIN DIM_PRODUCT p ON s.product_id = p.product_id
  AND s.transaction_date BETWEEN p.effective_date AND p.expiration_date;
```

## Query Patterns

### Aggregation by Dimension
```sql
SELECT 
  d.month_name,
  p.category,
  SUM(quantity) as total_quantity,
  SUM(total_amount) as total_sales
FROM FACT_SALES_TRANSACTION f
JOIN DIM_DATE d ON f.date_key = d.date_key
JOIN DIM_PRODUCT p ON f.product_key = p.product_key
WHERE d.year = 2024
GROUP BY d.month_name, p.category;
```

### Drill-Down to Detail
```sql
SELECT 
  transaction_number,
  d.date,
  c.customer_name,
  p.product_name,
  quantity,
  total_amount
FROM FACT_SALES_TRANSACTION f
JOIN DIM_DATE d ON f.date_key = d.date_key
JOIN DIM_CUSTOMER c ON f.customer_key = c.customer_key
JOIN DIM_PRODUCT p ON f.product_key = p.product_key
WHERE c.customer_id = 'C12345';
```

## Performance Optimization
- Partition by date_key
- Bitmap indexes on foreign keys (data warehouse)
- Columnstore index for very large tables
- Create aggregate fact tables for common queries

## Best Practices
- Store at atomic grain
- Additive facts preferred
- Degenerate dimensions for transaction IDs
- No nulls in foreign keys (use unknown members)
- Maintain grain consistency

