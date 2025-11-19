-- SCD TYPE 2 IMPLEMENTATION EXAMPLES
-- Slowly Changing Dimension Type 2: Add New Row for Changes

-- ============================================
-- SCENARIO 1: New Customer (INSERT)
-- ============================================
-- Business key 'C123' doesn't exist yet

INSERT INTO DIM_CUSTOMER (
    customer_id,
    customer_name,
    customer_segment,
    email_address,
    city,
    state_code,
    effective_date,
    expiration_date,
    current_flag,
    version_number,
    source_system
)
VALUES (
    'C123',
    'John Smith',
    'Silver',
    'john@email.com',
    'Seattle',
    'WA',
    '2024-01-15',
    '9999-12-31',
    'Y',
    1,
    'CRM_SYSTEM'
);

-- Result: customer_key=1001, version=1, current=Y

-- ============================================
-- SCENARIO 2: Customer Segment Changes (SCD Type 2)
-- ============================================
-- John Smith upgraded from Silver to Gold on 2024-06-01

BEGIN TRANSACTION;

-- Step 1: Expire the old record
UPDATE DIM_CUSTOMER
SET 
    expiration_date = '2024-05-31',
    current_flag = 'N',
    modified_date = CURRENT_TIMESTAMP
WHERE customer_id = 'C123'
  AND current_flag = 'Y';

-- Step 2: Insert new record with changes
INSERT INTO DIM_CUSTOMER (
    customer_id,
    customer_name,
    customer_segment,  -- CHANGED from Silver to Gold
    email_address,
    city,
    state_code,
    effective_date,
    expiration_date,
    current_flag,
    version_number,
    source_system
)
SELECT
    'C123',
    customer_name,  -- Keep same
    'Gold',  -- NEW value
    email_address,  -- Keep same
    city,  -- Keep same
    state_code,  -- Keep same
    '2024-06-01',  -- NEW effective date
    '9999-12-31',
    'Y',
    (SELECT MAX(version_number) + 1 FROM DIM_CUSTOMER WHERE customer_id = 'C123'),
    'CRM_SYSTEM'
FROM DIM_CUSTOMER
WHERE customer_id = 'C123'
  AND current_flag = 'N'
  AND expiration_date = '2024-05-31';

COMMIT;

-- Result after change:
-- customer_key | customer_id | segment | effective  | expiration | current
-- 1001         | C123        | Silver  | 2024-01-15 | 2024-05-31 | N
-- 1002         | C123        | Gold    | 2024-06-01 | 9999-12-31 | Y

-- ============================================
-- SCENARIO 3: Fact Table Loading with SCD Type 2
-- ============================================
-- Load sales facts, joining to correct customer version based on transaction date

INSERT INTO FACT_SALES_TRANSACTION (
    date_key,
    customer_key,
    product_key,
    store_key,
    transaction_number,
    quantity,
    total_amount
)
SELECT
    d.date_key,
    c.customer_key,  -- Will be 1001 or 1002 depending on transaction date
    p.product_key,
    s.store_key,
    staging.transaction_number,
    staging.quantity,
    staging.total_amount
FROM staging.sales_transactions staging
JOIN DIM_DATE d 
    ON staging.transaction_date = d.date
JOIN DIM_CUSTOMER c 
    ON staging.customer_id = c.customer_id
    AND d.date BETWEEN c.effective_date AND c.expiration_date  -- Time-sensitive join
JOIN DIM_PRODUCT p 
    ON staging.product_id = p.product_id
    AND d.date BETWEEN p.effective_date AND p.expiration_date
JOIN DIM_STORE s 
    ON staging.store_id = s.store_id;

-- Example results:
-- Transaction on 2024-03-15 → customer_key = 1001 (Silver segment)
-- Transaction on 2024-07-20 → customer_key = 1002 (Gold segment)

-- ============================================
-- QUERY EXAMPLES
-- ============================================

-- Get current customers only
SELECT *
FROM DIM_CUSTOMER
WHERE current_flag = 'Y';

-- Get customer as of specific date
SELECT *
FROM DIM_CUSTOMER
WHERE customer_id = 'C123'
  AND '2024-03-15' BETWEEN effective_date AND expiration_date;

-- Get full history for customer
SELECT 
    customer_key,
    customer_id,
    customer_segment,
    effective_date,
    expiration_date,
    current_flag,
    version_number
FROM DIM_CUSTOMER
WHERE customer_id = 'C123'
ORDER BY effective_date;

-- Sales by customer's segment at time of purchase
SELECT
    c.customer_segment as segment_at_purchase,
    SUM(f.total_amount) as total_sales,
    COUNT(*) as transaction_count
FROM FACT_SALES_TRANSACTION f
JOIN DIM_CUSTOMER c ON f.customer_key = c.customer_key
GROUP BY c.customer_segment;

-- ============================================
-- GENERIC SCD TYPE 2 PROCEDURE (PostgreSQL)
-- ============================================
CREATE OR REPLACE FUNCTION update_customer_scd2(
    p_customer_id VARCHAR,
    p_customer_name VARCHAR,
    p_customer_segment VARCHAR,
    p_email VARCHAR,
    p_effective_date DATE
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_changes_exist BOOLEAN;
    v_new_customer_key INTEGER;
BEGIN
    -- Check if this is a new customer or if attributes changed
    SELECT EXISTS (
        SELECT 1
        FROM DIM_CUSTOMER
        WHERE customer_id = p_customer_id
          AND current_flag = 'Y'
          AND (customer_name <> p_customer_name
               OR customer_segment <> p_customer_segment
               OR email_address <> p_email)
    ) INTO v_changes_exist;
    
    IF v_changes_exist THEN
        -- Expire old record
        UPDATE DIM_CUSTOMER
        SET expiration_date = p_effective_date - INTERVAL '1 day',
            current_flag = 'N',
            modified_date = CURRENT_TIMESTAMP
        WHERE customer_id = p_customer_id
          AND current_flag = 'Y';
        
        -- Insert new record
        INSERT INTO DIM_CUSTOMER (
            customer_id, customer_name, customer_segment,
            email_address, effective_date, expiration_date,
            current_flag, version_number, source_system
        )
        SELECT
            p_customer_id,
            p_customer_name,
            p_customer_segment,
            p_email,
            p_effective_date,
            '9999-12-31',
            'Y',
            COALESCE(MAX(version_number), 0) + 1,
            'ETL_PROCESS'
        FROM DIM_CUSTOMER
        WHERE customer_id = p_customer_id
        RETURNING customer_key INTO v_new_customer_key;
        
        RETURN v_new_customer_key;
    ELSE
        -- No changes, return current key
        SELECT customer_key INTO v_new_customer_key
        FROM DIM_CUSTOMER
        WHERE customer_id = p_customer_id
          AND current_flag = 'Y';
        
        RETURN v_new_customer_key;
    END IF;
END;
$$;
