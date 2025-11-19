-- STAR SCHEMA: FACT TABLE DDL
-- FACT_SALES_TRANSACTION
-- Grain: One row per product per sales transaction line item

CREATE TABLE FACT_SALES_TRANSACTION (
    -- Surrogate primary key
    sales_transaction_key BIGSERIAL PRIMARY KEY,
    
    -- Foreign keys to dimensions
    date_key INTEGER NOT NULL,
    time_key INTEGER,  -- Optional: for intraday analysis
    customer_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    store_key INTEGER NOT NULL,
    promotion_key INTEGER NOT NULL,
    
    -- Degenerate dimensions (no separate dimension table)
    transaction_number VARCHAR(20) NOT NULL,
    receipt_number VARCHAR(20),
    register_number VARCHAR(10),
    line_number SMALLINT NOT NULL,
    
    -- Facts (numeric measurements)
    quantity DECIMAL(10,2) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    extended_price DECIMAL(12,2) NOT NULL,  -- quantity * unit_price
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL,  -- extended_price - discount + tax
    cost_amount DECIMAL(12,2),
    profit_amount DECIMAL(12,2),  -- total_amount - cost_amount
    
    -- Audit columns
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_system VARCHAR(50),
    
    -- Foreign key constraints
    CONSTRAINT fk_sales_date FOREIGN KEY (date_key)
        REFERENCES DIM_DATE(date_key),
    CONSTRAINT fk_sales_customer FOREIGN KEY (customer_key)
        REFERENCES DIM_CUSTOMER(customer_key),
    CONSTRAINT fk_sales_product FOREIGN KEY (product_key)
        REFERENCES DIM_PRODUCT(product_key),
    CONSTRAINT fk_sales_store FOREIGN KEY (store_key)
        REFERENCES DIM_STORE(store_key),
    CONSTRAINT fk_sales_promotion FOREIGN KEY (promotion_key)
        REFERENCES DIM_PROMOTION(promotion_key),
        
    -- Business rule constraints
    CONSTRAINT chk_quantity_positive CHECK (quantity > 0),
    CONSTRAINT chk_unit_price_nonnegative CHECK (unit_price >= 0),
    CONSTRAINT chk_extended_price_calc CHECK (extended_price = quantity * unit_price),
    CONSTRAINT chk_total_calc CHECK (total_amount = extended_price - discount_amount + tax_amount)
);

-- Indexes for query performance
CREATE INDEX idx_sales_date ON FACT_SALES_TRANSACTION(date_key);
CREATE INDEX idx_sales_customer ON FACT_SALES_TRANSACTION(customer_key);
CREATE INDEX idx_sales_product ON FACT_SALES_TRANSACTION(product_key);
CREATE INDEX idx_sales_store ON FACT_SALES_TRANSACTION(store_key);
CREATE INDEX idx_sales_promotion ON FACT_SALES_TRANSACTION(promotion_key);

-- Composite index for common query patterns
CREATE INDEX idx_sales_date_store ON FACT_SALES_TRANSACTION(date_key, store_key);
CREATE INDEX idx_sales_date_product ON FACT_SALES_TRANSACTION(date_key, product_key);

-- Index for transaction lookup
CREATE INDEX idx_sales_transaction_num ON FACT_SALES_TRANSACTION(transaction_number);

-- Partitioning (PostgreSQL syntax) - by month
-- Note: Partitions would be created separately for each month
-- ALTER TABLE FACT_SALES_TRANSACTION PARTITION BY RANGE (date_key);
