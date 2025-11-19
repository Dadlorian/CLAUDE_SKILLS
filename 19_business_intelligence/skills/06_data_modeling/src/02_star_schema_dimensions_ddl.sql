-- STAR SCHEMA DDL: DIMENSION TABLES
-- Database: PostgreSQL/SQL Server compatible
-- Purpose: Retail Sales Data Warehouse Dimensions

-- ============================================
-- DIM_DATE (Conformed Dimension)
-- ============================================
CREATE TABLE DIM_DATE (
    date_key INTEGER PRIMARY KEY,  -- Format: YYYYMMDD (e.g., 20240615)
    date DATE NOT NULL UNIQUE,
    
    -- Calendar attributes
    day_number_in_month SMALLINT,
    day_number_in_year SMALLINT,
    day_of_week SMALLINT,  -- 1=Monday, 7=Sunday
    day_name VARCHAR(10),  -- Monday, Tuesday, etc.
    day_abbreviation CHAR(3),  -- Mon, Tue, etc.
    
    week_number_in_year SMALLINT,
    week_begin_date DATE,
    week_end_date DATE,
    
    month_number SMALLINT,  -- 1-12
    month_name VARCHAR(10),  -- January, February, etc.
    month_abbreviation CHAR(3),  -- Jan, Feb, etc.
    
    quarter_number SMALLINT,  -- 1-4
    quarter_name CHAR(2),  -- Q1, Q2, Q3, Q4
    
    year SMALLINT,  -- 2024
    year_month INTEGER,  -- 202406
    
    -- Fiscal calendar
    fiscal_month_number SMALLINT,
    fiscal_quarter_number SMALLINT,
    fiscal_year SMALLINT,
    
    -- Flags
    is_weekday CHAR(1),  -- Y/N
    is_weekend CHAR(1),  -- Y/N
    is_holiday CHAR(1),  -- Y/N
    is_business_day CHAR(1),  -- Y/N
    is_last_day_of_month CHAR(1),
    
    holiday_name VARCHAR(50),
    
    -- Audit
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_date_year_month ON DIM_DATE(year, month_number);

-- ============================================
-- DIM_CUSTOMER (SCD Type 2)
-- ============================================
CREATE TABLE DIM_CUSTOMER (
    customer_key SERIAL PRIMARY KEY,  -- Surrogate key
    customer_id VARCHAR(50) NOT NULL,  -- Natural business key
    
    -- Descriptive attributes
    customer_name VARCHAR(100) NOT NULL,
    customer_type VARCHAR(20),  -- Individual, Business
    customer_segment VARCHAR(30),  -- Platinum, Gold, Silver, Bronze
    
    -- Contact information
    email_address VARCHAR(100),
    phone_number VARCHAR(20),
    
    -- Address (denormalized)
    street_address VARCHAR(200),
    city VARCHAR(50),
    state_code CHAR(2),
    state_name VARCHAR(50),
    zip_code VARCHAR(10),
    country VARCHAR(50),
    
    -- Demographics
    age_range VARCHAR(20),  -- 18-24, 25-34, 35-44, etc.
    income_band VARCHAR(20),  -- Low, Medium, High, Very High
    
    -- Geographic hierarchy (denormalized)
    region VARCHAR(30),
    district VARCHAR(30),
    territory VARCHAR(30),
    
    -- SCD Type 2 columns
    effective_date DATE NOT NULL,
    expiration_date DATE NOT NULL DEFAULT '9999-12-31',
    current_flag CHAR(1) NOT NULL DEFAULT 'Y',
    version_number INTEGER NOT NULL DEFAULT 1,
    
    -- Audit
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP,
    source_system VARCHAR(50),
    
    CONSTRAINT chk_current_flag CHECK (current_flag IN ('Y', 'N'))
);

CREATE INDEX idx_customer_id ON DIM_CUSTOMER(customer_id);
CREATE INDEX idx_customer_current ON DIM_CUSTOMER(customer_id, current_flag);
CREATE INDEX idx_customer_dates ON DIM_CUSTOMER(effective_date, expiration_date);
CREATE INDEX idx_customer_segment ON DIM_CUSTOMER(customer_segment);

-- Unknown member
INSERT INTO DIM_CUSTOMER (
    customer_key, customer_id, customer_name,
    effective_date, expiration_date, current_flag, source_system
) VALUES (
    0, 'UNKNOWN', 'Unknown Customer',
    '1900-01-01', '9999-12-31', 'Y', 'SYSTEM'
);

-- ============================================
-- DIM_PRODUCT (SCD Type 2)
-- ============================================
CREATE TABLE DIM_PRODUCT (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    sku VARCHAR(50),
    upc VARCHAR(20),
    
    -- Descriptive attributes
    product_name VARCHAR(200) NOT NULL,
    product_description TEXT,
    brand_name VARCHAR(100),
    manufacturer_name VARCHAR(100),
    
    -- Product hierarchy (denormalized)
    subcategory_name VARCHAR(100),
    category_name VARCHAR(100),
    department_name VARCHAR(100),
    division_name VARCHAR(100),
    
    -- Product attributes
    color VARCHAR(50),
    size VARCHAR(20),
    weight_grams DECIMAL(10,2),
    unit_of_measure VARCHAR(20),
    package_type VARCHAR(50),
    
    -- Pricing
    standard_cost DECIMAL(10,2),
    list_price DECIMAL(10,2),
    
    -- Status flags
    is_active CHAR(1) DEFAULT 'Y',
    is_discontinued CHAR(1) DEFAULT 'N',
    is_promotional CHAR(1) DEFAULT 'N',
    
    -- Important dates
    introduction_date DATE,
    discontinuation_date DATE,
    
    -- SCD Type 2
    effective_date DATE NOT NULL,
    expiration_date DATE NOT NULL DEFAULT '9999-12-31',
    current_flag CHAR(1) NOT NULL DEFAULT 'Y',
    version_number INTEGER NOT NULL DEFAULT 1,
    
    -- Audit
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP,
    source_system VARCHAR(50)
);

CREATE INDEX idx_product_id ON DIM_PRODUCT(product_id);
CREATE INDEX idx_product_sku ON DIM_PRODUCT(sku);
CREATE INDEX idx_product_current ON DIM_PRODUCT(product_id, current_flag);
CREATE INDEX idx_product_category ON DIM_PRODUCT(category_name);

-- Unknown member
INSERT INTO DIM_PRODUCT (
    product_key, product_id, product_name,
    effective_date, expiration_date, current_flag, source_system
) VALUES (
    0, 'UNKNOWN', 'Unknown Product',
    '1900-01-01', '9999-12-31', 'Y', 'SYSTEM'
);

-- ============================================
-- DIM_STORE
-- ============================================
CREATE TABLE DIM_STORE (
    store_key SERIAL PRIMARY KEY,
    store_id VARCHAR(50) NOT NULL UNIQUE,
    
    store_name VARCHAR(100) NOT NULL,
    store_number VARCHAR(20),
    
    -- Address
    street_address VARCHAR(200),
    city VARCHAR(50),
    state_code CHAR(2),
    state_name VARCHAR(50),
    zip_code VARCHAR(10),
    country VARCHAR(50),
    
    -- Store hierarchy (denormalized)
    region VARCHAR(30),
    district VARCHAR(30),
    market_name VARCHAR(50),
    
    -- Store attributes
    store_type VARCHAR(30),  -- Flagship, Standard, Express
    store_format VARCHAR(30),  -- Mall, Standalone, Strip Center
    square_feet INTEGER,
    opening_date DATE,
    closing_date DATE,
    
    -- Manager
    store_manager_name VARCHAR(100),
    
    -- Status
    is_active CHAR(1) DEFAULT 'Y',
    
    -- Audit
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP,
    source_system VARCHAR(50)
);

CREATE INDEX idx_store_id ON DIM_STORE(store_id);
CREATE INDEX idx_store_region ON DIM_STORE(region);

-- Unknown member
INSERT INTO DIM_STORE (
    store_key, store_id, store_name, is_active, source_system
) VALUES (
    0, 'UNKNOWN', 'Unknown Store', 'Y', 'SYSTEM'
);

-- ============================================
-- DIM_PROMOTION (SCD Type 2)
-- ============================================
CREATE TABLE DIM_PROMOTION (
    promotion_key SERIAL PRIMARY KEY,
    promotion_id VARCHAR(50) NOT NULL,
    
    promotion_name VARCHAR(100) NOT NULL,
    promotion_description TEXT,
    promotion_type VARCHAR(30),  -- Percentage Off, Dollar Off, BOGO, etc.
    
    discount_type VARCHAR(20),  -- Percentage, Fixed Amount
    discount_value DECIMAL(10,2),
    
    -- Promotion dates
    start_date DATE,
    end_date DATE,
    
    -- Promotion attributes
    minimum_purchase_amount DECIMAL(10,2),
    maximum_discount_amount DECIMAL(10,2),
    
    -- SCD Type 2
    effective_date DATE NOT NULL,
    expiration_date DATE NOT NULL DEFAULT '9999-12-31',
    current_flag CHAR(1) NOT NULL DEFAULT 'Y',
    
    -- Audit
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP,
    source_system VARCHAR(50)
);

CREATE INDEX idx_promotion_id ON DIM_PROMOTION(promotion_id);
CREATE INDEX idx_promotion_current ON DIM_PROMOTION(promotion_id, current_flag);

-- Unknown member (No Promotion)
INSERT INTO DIM_PROMOTION (
    promotion_key, promotion_id, promotion_name,
    effective_date, expiration_date, current_flag, source_system
) VALUES (
    0, 'NO_PROMO', 'No Promotion',
    '1900-01-01', '9999-12-31', 'Y', 'SYSTEM'
);
