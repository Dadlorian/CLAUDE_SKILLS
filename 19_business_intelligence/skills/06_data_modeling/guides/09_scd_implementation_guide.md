# Slowly Changing Dimensions Implementation Guide

## SCD Type 1: Overwrite

**When**: Only current state matters, history not needed

**Implementation**:
```sql
UPDATE DIM_CUSTOMER
SET 
  customer_name = staging.customer_name,
  email = staging.email,
  modified_date = CURRENT_TIMESTAMP
FROM staging.customers staging
WHERE DIM_CUSTOMER.customer_id = staging.customer_id
  AND (DIM_CUSTOMER.customer_name <> staging.customer_name
       OR DIM_CUSTOMER.email <> staging.email);
```

**Use Cases**:
- Error corrections
- Non-historical attributes (phone, email)
- Reference data

## SCD Type 2: New Row

**When**: Full history required

**Structure**:
```sql
DIM_PRODUCT
- product_key (PK, surrogate - NEW for each change)
- product_id (natural key - SAME across versions)
- product_name
- category
- unit_price
- effective_date
- expiration_date  
- current_flag
- version_number
```

**Implementation**:
```sql
-- Step 1: Expire old row
UPDATE DIM_PRODUCT
SET 
  expiration_date = CURRENT_DATE - 1,
  current_flag = 'N'
WHERE product_id = 'P123'
  AND current_flag = 'Y';

-- Step 2: Insert new row
INSERT INTO DIM_PRODUCT (
  product_key, product_id, product_name, category,
  effective_date, expiration_date, current_flag, version_number
)
VALUES (
  NEXT_VALUE_FOR product_key_seq,
  'P123',
  'Updated Product Name',
  'New Category',
  CURRENT_DATE,
  '9999-12-31',
  'Y',
  (SELECT MAX(version_number) + 1 FROM DIM_PRODUCT WHERE product_id = 'P123')
);
```

**Best Practices**:
- Use surrogate keys (not natural keys) as FKs in facts
- Include effective/expiration dates
- Use current_flag for easy filtering
- '9999-12-31' for open-ended expiration
- Version number for clarity

## SCD Type 4: Mini-Dimension

**When**: Rapidly changing attributes causing explosion

See Mini-Dimensions Guide for details.

## Choosing SCD Type

| Scenario | Type | Reason |
|----------|------|--------|
| Price history critical | Type 2 | Full history needed |
| Customer segment changes | Type 2 | Analyze behavior by segment |
| Error corrections | Type 1 | Don't preserve errors |
| Phone number changes | Type 1 | Current contact info only |
| Age/demographics changing | Type 4 | Mini-dimension prevents explosion |
| One previous value needed | Type 3 | Simple before/after |

