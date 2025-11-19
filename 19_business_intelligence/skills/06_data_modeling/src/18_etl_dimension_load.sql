-- ETL: Dimension Loading with SCD Type 2
INSERT INTO DIM_CUSTOMER (customer_id, customer_name, customer_segment, ...)
SELECT DISTINCT customer_id, customer_name, customer_segment, ...
FROM staging.customers
WHERE NOT EXISTS (SELECT 1 FROM DIM_CUSTOMER WHERE customer_id = staging.customers.customer_id);

-- Update existing (SCD Type 2)
-- See file 04 for complete implementation
