-- DATA QUALITY CHECKS
-- Check for orphaned FKs
SELECT COUNT(*) FROM FACT_SALES f LEFT JOIN DIM_CUSTOMER c ON f.customer_key = c.customer_key WHERE c.customer_key IS NULL;

-- Check for NULL required fields
SELECT COUNT(*) FROM DIM_CUSTOMER WHERE customer_name IS NULL;

-- Check for duplicate keys
SELECT customer_id, COUNT(*) FROM DIM_CUSTOMER WHERE current_flag='Y' GROUP BY customer_id HAVING COUNT(*)>1;
