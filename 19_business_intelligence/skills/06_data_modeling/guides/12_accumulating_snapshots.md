# Accumulating Snapshot Fact Tables Guide

## Purpose
Track process/pipeline/workflow from start to finish with multiple milestone dates.

## Characteristics
- One row per process instance
- Rows UPDATED as process progresses (exception to insert-only)
- Multiple date foreign keys (one per milestone)
- Lag calculations (days between milestones)
- Current status column

## Example: Order Fulfillment

### Grain
"One row per order, updated as order progresses through fulfillment"

### Structure
```sql
FACT_ORDER_FULFILLMENT
- order_key (PK)
-- Multiple date milestones
- order_date_key
- payment_date_key
- fulfillment_date_key
- ship_date_key
- delivery_date_key
-- Dimensions
- customer_key
- product_key
-- Degenerate
- order_number
-- Facts
- order_amount
-- Lag measures (calculated)
- days_to_payment
- days_to_ship
- days_to_deliver
-- Status
- current_status
```

### Lifecycle

**Initial State** (order placed):
```
order_key | order_date | payment | ship | delivery | status
1001      | 20240610   | NULL    | NULL | NULL     | ORDERED
```

**After Payment**:
```
order_key | order_date | payment  | ship | delivery | days_to_pay | status
1001      | 20240610   | 20240610 | NULL | NULL     | 0           | PAID
```

**After Shipment**:
```
order_key | order_date | payment  | ship     | delivery | days_to_ship | status
1001      | 20240610   | 20240610 | 20240612 | NULL     | 2            | SHIPPED
```

**Complete**:
```
order_key | order_date | payment  | ship     | delivery | total_days | status
1001      | 20240610   | 20240610 | 20240612 | 20240615 | 5          | DELIVERED
```

## Implementation

### Initial Load
```sql
INSERT INTO FACT_ORDER_FULFILLMENT
SELECT 
  order_id, order_date_key, customer_key, product_key,
  order_amount, 'ORDERED' as status
FROM staging.new_orders;
```

### Update as Milestones Occur
```sql
UPDATE FACT_ORDER_FULFILLMENT
SET 
  ship_date_key = staging.ship_date_key,
  days_to_ship = DATEDIFF(staging.ship_date, order_date),
  current_status = 'SHIPPED'
FROM staging.shipments
WHERE order_number = staging.order_number
  AND ship_date_key IS NULL;
```

## Use Cases
- Order fulfillment
- Insurance claims processing
- Student enrollment lifecycle
- Loan applications
- Manufacturing jobs
- Help desk tickets

## Query Examples

### Average Fulfillment Time
```sql
SELECT 
  p.product_category,
  AVG(days_to_deliver) as avg_days
FROM FACT_ORDER_FULFILLMENT
WHERE delivery_date_key IS NOT NULL
GROUP BY p.product_category;
```

### Orders Still in Progress
```sql
SELECT order_number, current_status, days_since_order
FROM FACT_ORDER_FULFILLMENT
WHERE delivery_date_key IS NULL
  AND DATEDIFF(CURRENT_DATE, order_date) > 7;
```

## Best Practices
- One row per process instance only
- Update in place (don't create new rows)
- NULL for milestones not yet reached
- Calculate lag measures automatically
- Include current status
- Index on status for filtering

