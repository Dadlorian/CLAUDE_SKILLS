-- PERIODIC SNAPSHOT FACT TABLE
-- Grain: One row per account per day

CREATE TABLE FACT_ACCOUNT_BALANCE_DAILY (
    balance_key BIGSERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,
    account_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    branch_key INTEGER NOT NULL,
    
    -- Balance facts (semi-additive)
    beginning_balance DECIMAL(15,2),
    ending_balance DECIMAL(15,2),
    average_daily_balance DECIMAL(15,2),
    minimum_balance DECIMAL(15,2),
    maximum_balance DECIMAL(15,2),
    
    -- Activity facts (fully additive)
    transaction_count INTEGER,
    deposit_count INTEGER,
    withdrawal_count INTEGER,
    total_deposits DECIMAL(15,2),
    total_withdrawals DECIMAL(15,2),
    total_fees DECIMAL(10,2),
    total_interest DECIMAL(10,2),
    
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (date_key, account_key)
);

CREATE INDEX idx_balance_date ON FACT_ACCOUNT_BALANCE_DAILY(date_key);
CREATE INDEX idx_balance_account ON FACT_ACCOUNT_BALANCE_DAILY(account_key);
