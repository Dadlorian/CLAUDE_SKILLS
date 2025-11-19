# Junk Dimensions Implementation Guide

## Purpose
Consolidate low-cardinality flags and indicators into a single dimension to avoid cluttering fact tables.

## When to Use
- Multiple boolean/flag columns in fact
- Low-cardinality indicator fields (5-20 distinct values each)
- Combinations are finite and manageable
- Flags logically relate to same context

## Implementation

### Before (Anti-Pattern)
```sql
FACT_SALES
- payment_type (10 values)
- shipping_method (5 values)
- gift_wrap_flag (2 values)
- express_flag (2 values)
- first_time_buyer (2 values)
```

### After (Junk Dimension)
```sql
DIM_TRANSACTION_FLAGS
- transaction_flags_key (PK)
- payment_type
- shipping_method  
- gift_wrap_flag
- express_flag
- first_time_buyer

FACT_SALES
- transaction_flags_key (single FK)
```

## Loading Strategies

### Strategy 1: Pre-Generate All Combinations
```sql
-- For boolean flags (2^5 = 32 combinations)
INSERT INTO DIM_TRANSACTION_FLAGS
SELECT ROW_NUMBER() OVER (ORDER BY a,b,c,d,e),
  a, b, c, d, e
FROM 
  (SELECT 'Y' as flag UNION SELECT 'N') a
  CROSS JOIN (SELECT 'Y' UNION SELECT 'N') b
  CROSS JOIN (SELECT 'Y' UNION SELECT 'N') c
  CROSS JOIN (SELECT 'Y' UNION SELECT 'N') d
  CROSS JOIN (SELECT 'Y' UNION SELECT 'N') e;
```

### Strategy 2: Add On-Demand
```sql
-- Insert only combinations that actually occur
INSERT INTO DIM_TRANSACTION_FLAGS
SELECT DISTINCT payment_type, shipping_method, gift_wrap_flag
FROM staging.sales
WHERE NOT EXISTS (
  SELECT 1 FROM DIM_TRANSACTION_FLAGS d
  WHERE d.payment_type = staging.sales.payment_type
    AND d.shipping_method = staging.sales.shipping_method
    AND d.gift_wrap_flag = staging.sales.gift_wrap_flag
);
```

## Best Practices
- Maximum 10-15 attributes in junk dimension
- Keep logically related attributes together
- Document attribute meanings clearly
- Consider separate junk dimensions for unrelated flag groups
- Monitor size (limit to 10,000 rows or less)

## Benefits
- Reduces fact table width
- Eliminates many foreign keys
- Groups related indicators
- Simplifies fact ETL
- Improves query readability

