-- Dimensional Data Warehouse DDL Example
-- Star Schema for E-Commerce Analytics

-- ================================================
-- DIMENSION TABLES
-- ================================================

-- Date Dimension
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    date_value DATE NOT NULL,
    day_of_week INTEGER,
    day_name VARCHAR(10),
    day_of_month INTEGER,
    day_of_year INTEGER,
    week_of_year INTEGER,
    month_number INTEGER,
    month_name VARCHAR(10),
    quarter INTEGER,
    year INTEGER,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    fiscal_year INTEGER,
    fiscal_quarter INTEGER,
    fiscal_month INTEGER
);

CREATE INDEX idx_date_value ON dim_date(date_value);
CREATE INDEX idx_date_month ON dim_date(year, month_number);

-- Product Dimension (SCD Type 2)
CREATE TABLE dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    product_name VARCHAR(200),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    supplier VARCHAR(200),
    unit_cost DECIMAL(10,2),
    list_price DECIMAL(10,2),
    -- SCD Type 2 fields
    effective_date DATE NOT NULL,
    expiration_date DATE NOT NULL DEFAULT '9999-12-31',
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_product_id ON dim_product(product_id, is_current);
CREATE INDEX idx_product_category ON dim_product(category);

-- Customer Dimension (SCD Type 2)
CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(200),
    email VARCHAR(255),
    phone VARCHAR(50),
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    customer_segment VARCHAR(50),
    -- SCD Type 2 fields
    effective_date DATE NOT NULL,
    expiration_date DATE NOT NULL DEFAULT '9999-12-31',
    is_current BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_customer_id ON dim_customer(customer_id, is_current);
CREATE INDEX idx_customer_segment ON dim_customer(customer_segment);

-- Store Dimension
CREATE TABLE dim_store (
    store_key SERIAL PRIMARY KEY,
    store_id VARCHAR(50) NOT NULL,
    store_name VARCHAR(200),
    store_type VARCHAR(50),
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(100),
    region VARCHAR(50),
    district VARCHAR(50),
    manager_name VARCHAR(200),
    opening_date DATE,
    square_footage INTEGER,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_store_region ON dim_store(region);

-- ================================================
-- FACT TABLES
-- ================================================

-- Sales Fact (Transaction Grain)
CREATE TABLE fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
    customer_key INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    store_key INTEGER NOT NULL REFERENCES dim_store(store_key),
    -- Degenerate dimensions
    order_id VARCHAR(50),
    line_number INTEGER,
    -- Measures
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    cost_amount DECIMAL(10,2),
    profit_amount DECIMAL(10,2)
);

-- Partitioning by date for performance
CREATE TABLE fact_sales_2024_01 PARTITION OF fact_sales
    FOR VALUES FROM ('20240101') TO ('20240201');

CREATE INDEX idx_sales_date ON fact_sales(date_key);
CREATE INDEX idx_sales_product ON fact_sales(product_key);
CREATE INDEX idx_sales_customer ON fact_sales(customer_key);
CREATE INDEX idx_sales_store ON fact_sales(store_key);

-- Inventory Snapshot Fact (Periodic Snapshot)
CREATE TABLE fact_inventory_snapshot (
    snapshot_key BIGSERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
    store_key INTEGER NOT NULL REFERENCES dim_store(store_key),
    -- Measures (as of snapshot date)
    quantity_on_hand INTEGER,
    quantity_allocated INTEGER,
    quantity_available INTEGER,
    reorder_point INTEGER,
    reorder_quantity INTEGER,
    unit_cost DECIMAL(10,2),
    total_value DECIMAL(12,2)
);

CREATE INDEX idx_inventory_date ON fact_inventory_snapshot(date_key);
CREATE INDEX idx_inventory_product ON fact_inventory_snapshot(product_key);

-- Customer Account Snapshot (Accumulating Snapshot)
CREATE TABLE fact_customer_lifecycle (
    customer_key INTEGER PRIMARY KEY REFERENCES dim_customer(customer_key),
    -- Milestone dates
    registration_date_key INTEGER REFERENCES dim_date(date_key),
    first_purchase_date_key INTEGER REFERENCES dim_date(date_key),
    last_purchase_date_key INTEGER REFERENCES dim_date(date_key),
    -- Cumulative measures
    lifetime_orders INTEGER,
    lifetime_revenue DECIMAL(12,2),
    lifetime_profit DECIMAL(12,2),
    -- Current status
    customer_status VARCHAR(50),
    last_updated_at TIMESTAMP
);
