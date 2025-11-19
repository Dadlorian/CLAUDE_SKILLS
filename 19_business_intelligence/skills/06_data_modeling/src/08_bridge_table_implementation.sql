-- BRIDGE TABLES: Many-to-Many Relationships

CREATE TABLE DIM_ACCOUNT (
    account_key SERIAL PRIMARY KEY,
    account_number VARCHAR(50) NOT NULL UNIQUE,
    account_type VARCHAR(30),
    opening_date DATE
);

CREATE TABLE BRIDGE_ACCOUNT_CUSTOMER (
    account_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    allocation_percentage DECIMAL(5,2),  -- For distributing amounts
    primary_customer_flag CHAR(1),
    weighting_factor DECIMAL(5,4),  -- 1 / customer_count
    effective_date DATE NOT NULL,
    expiration_date DATE NOT NULL DEFAULT '9999-12-31',
    current_flag CHAR(1) DEFAULT 'Y',
    PRIMARY KEY (account_key, customer_key, effective_date),
    FOREIGN KEY (account_key) REFERENCES DIM_ACCOUNT(account_key),
    FOREIGN KEY (customer_key) REFERENCES DIM_CUSTOMER(customer_key)
);

-- Query example with weighting to avoid double-counting
-- SELECT customer_name, SUM(balance * weighting_factor) as allocated_balance
-- FROM FACT_ACCOUNT_BALANCE f
-- JOIN BRIDGE_ACCOUNT_CUSTOMER b ON f.account_key = b.account_key
-- JOIN DIM_CUSTOMER c ON b.customer_key = c.customer_key
-- WHERE b.current_flag = 'Y' GROUP BY customer_name;
