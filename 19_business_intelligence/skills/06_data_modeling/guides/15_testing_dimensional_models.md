# Testing Dimensional Models Guide

## Test Phases

### 1. Unit Testing (ETL Components)

**Dimension Loading**:
```sql
-- Test: All source records loaded
SELECT COUNT(*) FROM staging.customers;
SELECT COUNT(*) FROM DIM_CUSTOMER WHERE current_flag = 'Y';
-- Counts should match (or explain differences)

-- Test: No duplicate business keys
SELECT customer_id, COUNT(*)
FROM DIM_CUSTOMER
WHERE current_flag = 'Y'
GROUP BY customer_id
HAVING COUNT(*) > 1;
-- Should return 0 rows

-- Test: Unknown member exists
SELECT * FROM DIM_CUSTOMER WHERE customer_key = 0;
-- Should return exactly 1 row
```

**Fact Loading**:
```sql
-- Test: Row counts match
SELECT COUNT(*) FROM staging.sales;
SELECT COUNT(*) FROM FACT_SALES;
-- Investigate differences

-- Test: No orphaned foreign keys
SELECT COUNT(*)
FROM FACT_SALES f
LEFT JOIN DIM_CUSTOMER c ON f.customer_key = c.customer_key
WHERE c.customer_key IS NULL;
-- Should return 0 (all FKs valid)

-- Test: Sum totals match
SELECT SUM(total_amount) FROM staging.sales;
SELECT SUM(total_amount) FROM FACT_SALES;
-- Should match
```

**SCD Type 2 Logic**:
```sql
-- Test: Changes create new rows
-- 1. Note current row count
-- 2. Update source record
-- 3. Run ETL
-- 4. Verify:
SELECT customer_id, COUNT(*) as version_count
FROM DIM_CUSTOMER
WHERE customer_id = 'TEST123'
GROUP BY customer_id;
-- Should show 2 versions

-- Test: Old row expired
SELECT * FROM DIM_CUSTOMER
WHERE customer_id = 'TEST123'
  AND current_flag = 'N';
-- Should have expiration_date set

-- Test: New row current
SELECT * FROM DIM_CUSTOMER
WHERE customer_id = 'TEST123'
  AND current_flag = 'Y';
-- Should have expiration_date = '9999-12-31'
```

### 2. Integration Testing

**End-to-End Flow**:
```sql
-- Test: Source to report flow
-- 1. Insert test transaction in source
-- 2. Run full ETL
-- 3. Query fact table
SELECT *
FROM FACT_SALES f
JOIN DIM_CUSTOMER c ON f.customer_key = c.customer_key
JOIN DIM_PRODUCT p ON f.product_key = p.product_key
WHERE transaction_number = 'TEST-TRANS-123';
-- Should return test transaction with correct attributes
```

**Conformed Dimensions**:
```sql
-- Test: Same customer key across data marts
SELECT customer_key, customer_id
FROM SALES_MART.DIM_CUSTOMER
WHERE customer_id = 'C123'
UNION
SELECT customer_key, customer_id
FROM SERVICE_MART.DIM_CUSTOMER
WHERE customer_id = 'C123';
-- Should return same customer_key
```

### 3. Data Quality Testing

**Completeness**:
```sql
-- Test: Required fields populated
SELECT 
  'NULL customer_name' as issue,
  COUNT(*) as count
FROM DIM_CUSTOMER
WHERE customer_name IS NULL

UNION ALL

SELECT 
  'NULL product_name',
  COUNT(*)
FROM DIM_PRODUCT
WHERE product_name IS NULL;
```

**Referential Integrity**:
```sql
-- Test: All FKs reference valid dimensions
SELECT 
  'Invalid date_key' as issue,
  COUNT(*) as count
FROM FACT_SALES f
LEFT JOIN DIM_DATE d ON f.date_key = d.date_key
WHERE d.date_key IS NULL

UNION ALL

SELECT 
  'Invalid customer_key',
  COUNT(*)
FROM FACT_SALES f
LEFT JOIN DIM_CUSTOMER c ON f.customer_key = c.customer_key
WHERE c.customer_key IS NULL;
```

**Business Rules**:
```sql
-- Test: Quantity > 0
SELECT COUNT(*)
FROM FACT_SALES
WHERE quantity <= 0;

-- Test: Ship date >= order date
SELECT COUNT(*)
FROM FACT_ORDER
WHERE ship_date_key < order_date_key;

-- Test: Discount <= total
SELECT COUNT(*)
FROM FACT_SALES
WHERE discount_amount > total_amount;
```

### 4. Performance Testing

**Query Response Time**:
```sql
-- Measure common query patterns
SET STATISTICS TIME ON;

SELECT 
  d.month_name,
  SUM(f.total_amount) as total_sales
FROM FACT_SALES f
JOIN DIM_DATE d ON f.date_key = d.date_key
WHERE d.year = 2024
GROUP BY d.month_name;
-- Target: < 2 seconds for typical query
```

**ETL Performance**:
- Measure load time for daily batch
- Test incremental vs full load
- Monitor resource utilization
- Validate parallel loading

### 5. User Acceptance Testing

**Business Validation**:
- Users run known queries
- Compare results to legacy system
- Verify business logic
- Validate metric calculations

**Usability Testing**:
- BI tool connection
- Report creation
- Self-service capabilities
- Performance from user perspective

## Testing Checklist

### Pre-Deployment
- [ ] All unit tests pass
- [ ] Row count reconciliation complete
- [ ] Sum total reconciliation complete
- [ ] No orphaned FKs
- [ ] No duplicate business keys
- [ ] SCD logic validated
- [ ] Data quality checks pass
- [ ] Performance benchmarks met
- [ ] Business user sign-off

### Post-Deployment
- [ ] Production data load successful
- [ ] Reports produce expected results
- [ ] Performance acceptable
- [ ] No critical errors in logs
- [ ] Users able to access
- [ ] Backup and recovery tested

## Automated Testing

Create test harness:
```sql
CREATE TABLE ETL_TEST_RESULTS (
  test_date DATE,
  test_name VARCHAR(100),
  expected_result VARCHAR(100),
  actual_result VARCHAR(100),
  pass_fail CHAR(1),
  notes TEXT
);

-- Run tests and log results
INSERT INTO ETL_TEST_RESULTS
VALUES (
  CURRENT_DATE,
  'Fact row count reconciliation',
  '10000',
  (SELECT COUNT(*) FROM FACT_SALES WHERE date_key = 20240615),
  CASE WHEN ... THEN 'P' ELSE 'F' END,
  'Daily sales load'
);
```

## Best Practices

1. **Automate**: Script all tests for repeatability
2. **Document**: Clear test cases and expected results
3. **Version Control**: Tests alongside code
4. **Continuous**: Run tests on every deployment
5. **Comprehensive**: Test all layers (unit, integration, E2E)
6. **Business-Driven**: Validate against business expectations
7. **Performance**: Test with production-like volumes

