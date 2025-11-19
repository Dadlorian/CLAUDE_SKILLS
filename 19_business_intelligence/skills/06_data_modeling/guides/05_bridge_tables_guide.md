# Bridge Tables Implementation Guide

## Purpose
Handle many-to-many relationships in dimensional models by providing a bridge between fact and dimension tables.

## Common Scenarios

### Multi-Valued Dimensions
**Problem**: Account has multiple customers
**Solution**: Bridge table with weighting factor

```
DIM_CUSTOMER
DIM_ACCOUNT
BRIDGE_ACCOUNT_CUSTOMER (many-to-many)
- account_key
- customer_key
- allocation_percentage
- primary_customer_flag  
- weighting_factor (1/customer_count)
FACT_ACCOUNT_BALANCE
```

### Ragged Hierarchies
**Problem**: Organizational chart with varying depths
**Solution**: Bridge table flattening hierarchy

```
DIM_EMPLOYEE
BRIDGE_EMPLOYEE_HIERARCHY
- employee_key
- manager_key
- hierarchy_level
- top_flag
- bottom_flag
```

## Weighting Factor Pattern

**Purpose**: Avoid double-counting in aggregations

**Calculation**:
```
If account has 2 customers: weighting_factor = 0.5
If account has 3 customers: weighting_factor = 0.333
```

**Query Usage**:
```sql
SELECT 
  c.customer_name,
  SUM(f.balance * b.weighting_factor) as allocated_balance
FROM FACT_ACCOUNT_BALANCE f
JOIN BRIDGE_ACCOUNT_CUSTOMER b ON f.account_key = b.account_key
JOIN DIM_CUSTOMER c ON b.customer_key = c.customer_key
GROUP BY c.customer_name;
```

## Implementation Steps

1. Identify many-to-many relationship
2. Create bridge table structure
3. Calculate weighting factors
4. Add effective/expiration dates if relationships change
5. Document query patterns for users
6. Test aggregations for accuracy

## Best Practices
- Always include weighting factor
- Document allocation rules
- Consider time-variance
- Provide example queries
- Monitor query performance

