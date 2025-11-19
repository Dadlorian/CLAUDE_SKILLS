-- BigQuery Star Schema DDL
-- E-commerce Data Warehouse
-- Platform: Google BigQuery
-- Description: Star schema with partitioning and clustering optimizations

-- ============================================
-- DIMENSION TABLES
-- ============================================

-- Date Dimension
CREATE OR REPLACE TABLE `project.dwh.dim_date`
(
    date_key INT64 NOT NULL,
    date_value DATE NOT NULL,
    day_of_week INT64,
    day_name STRING,
    day_of_month INT64,
    day_of_year INT64,
    week_of_year INT64,
    month_number INT64,
    month_name STRING,
    quarter INT64,
    quarter_name STRING,
    year INT64,
    is_weekend BOOL,
    is_holiday BOOL,
    holiday_name STRING,
    fiscal_year INT64,
    fiscal_quarter INT64,
    fiscal_month INT64,
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY RANGE_BUCKET(date_key, GENERATE_ARRAY(20200101, 20301231, 1))
CLUSTER BY date_value
OPTIONS(
    description="Date dimension with calendar and fiscal attributes",
    require_partition_filter=false
);

-- Customer Dimension (SCD Type 2)
CREATE OR REPLACE TABLE `project.dwh.dim_customer`
(
    customer_key INT64 NOT NULL,
    customer_id STRING NOT NULL,
    customer_name STRING,
    email STRING,
    phone STRING,
    customer_segment STRING,
    customer_tier STRING,
    loyalty_points INT64,
    lifetime_value NUMERIC(12, 2),
    -- Address
    country STRING,
    state STRING,
    city STRING,
    postal_code STRING,
    latitude FLOAT64,
    longitude FLOAT64,
    -- SCD Type 2 columns
    effective_date DATE NOT NULL,
    expiration_date DATE,
    is_current BOOL DEFAULT TRUE,
    row_hash STRING,
    -- Metadata
    source_system STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY effective_date
CLUSTER BY customer_id, is_current
OPTIONS(
    description="Customer dimension with SCD Type 2 tracking"
);

-- Product Dimension (SCD Type 2)
CREATE OR REPLACE TABLE `project.dwh.dim_product`
(
    product_key INT64 NOT NULL,
    product_id STRING NOT NULL,
    product_name STRING,
    product_description STRING,
    sku STRING,
    barcode STRING,
    -- Hierarchy
    brand STRING,
    category STRING,
    subcategory STRING,
    department STRING,
    product_line STRING,
    -- Attributes
    color STRING,
    size STRING,
    weight_kg NUMERIC(10, 3),
    dimensions_cm STRING,
    -- Pricing
    unit_cost NUMERIC(12, 2),
    unit_price NUMERIC(12, 2),
    msrp NUMERIC(12, 2),
    -- Flags
    is_active BOOL,
    is_discontinued BOOL,
    is_featured BOOL,
    -- SCD Type 2 columns
    effective_date DATE NOT NULL,
    expiration_date DATE,
    is_current BOOL DEFAULT TRUE,
    row_hash STRING,
    -- Metadata
    source_system STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY effective_date
CLUSTER BY product_id, is_current, category
OPTIONS(
    description="Product dimension with SCD Type 2 tracking"
);

-- Supplier Dimension
CREATE OR REPLACE TABLE `project.dwh.dim_supplier`
(
    supplier_key INT64 NOT NULL,
    supplier_id STRING NOT NULL,
    supplier_name STRING,
    contact_name STRING,
    phone STRING,
    email STRING,
    country STRING,
    state STRING,
    city STRING,
    postal_code STRING,
    payment_terms STRING,
    credit_rating STRING,
    is_active BOOL DEFAULT TRUE,
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY supplier_id
OPTIONS(
    description="Supplier dimension"
);

-- Warehouse Dimension
CREATE OR REPLACE TABLE `project.dwh.dim_warehouse`
(
    warehouse_key INT64 NOT NULL,
    warehouse_id STRING NOT NULL,
    warehouse_name STRING,
    warehouse_type STRING,
    capacity_cubic_meters INT64,
    country STRING,
    state STRING,
    city STRING,
    postal_code STRING,
    region STRING,
    manager_name STRING,
    opening_date DATE,
    is_active BOOL DEFAULT TRUE,
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY warehouse_id
OPTIONS(
    description="Warehouse location dimension"
);

-- ============================================
-- FACT TABLES
-- ============================================

-- Sales Fact (Transaction grain)
CREATE OR REPLACE TABLE `project.dwh.fact_sales`
(
    sales_key INT64 NOT NULL,
    -- Foreign Keys
    date_key INT64 NOT NULL,
    customer_key INT64 NOT NULL,
    product_key INT64 NOT NULL,
    warehouse_key INT64,
    -- Degenerate Dimensions
    order_id STRING NOT NULL,
    order_line_number INT64,
    invoice_number STRING,
    -- Measures
    quantity INT64,
    unit_price NUMERIC(12, 2),
    unit_cost NUMERIC(12, 2),
    gross_sales_amount NUMERIC(12, 2),
    discount_amount NUMERIC(12, 2),
    net_sales_amount NUMERIC(12, 2),
    tax_amount NUMERIC(12, 2),
    shipping_amount NUMERIC(12, 2),
    total_amount NUMERIC(12, 2),
    profit_amount NUMERIC(12, 2),
    margin_percentage NUMERIC(5, 2),
    -- Additional Attributes
    payment_method STRING,
    shipping_method STRING,
    currency_code STRING,
    -- Metadata
    transaction_timestamp TIMESTAMP,
    source_system STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(transaction_timestamp)
CLUSTER BY date_key, customer_key, product_key
OPTIONS(
    description="Sales transactions fact table at line item grain",
    require_partition_filter=true,
    partition_expiration_days=null
);

-- Inventory Fact (Periodic Snapshot)
CREATE OR REPLACE TABLE `project.dwh.fact_inventory`
(
    inventory_key INT64 NOT NULL,
    -- Foreign Keys
    date_key INT64 NOT NULL,
    product_key INT64 NOT NULL,
    warehouse_key INT64 NOT NULL,
    supplier_key INT64,
    -- Measures
    beginning_quantity INT64,
    received_quantity INT64,
    sold_quantity INT64,
    returned_quantity INT64,
    adjusted_quantity INT64,
    ending_quantity INT64,
    inventory_value NUMERIC(12, 2),
    average_cost NUMERIC(12, 2),
    days_of_supply INT64,
    reorder_point INT64,
    safety_stock INT64,
    -- Flags
    is_out_of_stock BOOL,
    is_overstock BOOL,
    is_slow_moving BOOL,
    -- Metadata
    snapshot_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY snapshot_date
CLUSTER BY date_key, warehouse_key, product_key
OPTIONS(
    description="Daily inventory snapshot fact table",
    require_partition_filter=true
);

-- Web Events Fact (Factless for clickstream)
CREATE OR REPLACE TABLE `project.dwh.fact_web_events`
(
    event_key INT64 NOT NULL,
    -- Foreign Keys
    date_key INT64 NOT NULL,
    customer_key INT64,
    product_key INT64,
    -- Degenerate Dimensions
    session_id STRING,
    event_id STRING,
    -- Event Attributes
    event_type STRING,
    event_category STRING,
    page_url STRING,
    referrer_url STRING,
    device_type STRING,
    browser STRING,
    os STRING,
    country STRING,
    -- Measures (semi-additive)
    duration_seconds INT64,
    scroll_depth_percentage INT64,
    -- Metadata
    event_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(event_timestamp)
CLUSTER BY date_key, event_type, customer_key
OPTIONS(
    description="Web clickstream events fact table",
    require_partition_filter=true,
    partition_expiration_days=730  -- Keep 2 years
);

-- Customer Subscription Fact (Accumulating Snapshot)
CREATE OR REPLACE TABLE `project.dwh.fact_subscription`
(
    subscription_key INT64 NOT NULL,
    -- Foreign Keys (milestone dates)
    signup_date_key INT64,
    trial_end_date_key INT64,
    first_payment_date_key INT64,
    cancellation_date_key INT64,
    churn_date_key INT64,
    customer_key INT64 NOT NULL,
    -- Degenerate Dimensions
    subscription_id STRING NOT NULL,
    -- Measures
    subscription_plan STRING,
    monthly_recurring_revenue NUMERIC(12, 2),
    total_revenue NUMERIC(12, 2),
    -- Lag measures
    signup_to_payment_days INT64,
    payment_to_cancellation_days INT64,
    total_lifetime_days INT64,
    -- Status flags
    is_trial BOOL,
    is_active BOOL,
    is_cancelled BOOL,
    is_churned BOOL,
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY RANGE_BUCKET(signup_date_key, GENERATE_ARRAY(20200101, 20301231, 1))
CLUSTER BY customer_key, is_active
OPTIONS(
    description="Subscription lifecycle accumulating snapshot"
);

-- ============================================
-- AGGREGATE / MATERIALIZED VIEWS
-- ============================================

-- Daily Sales Summary (Materialized View for performance)
CREATE MATERIALIZED VIEW `project.dwh.mv_daily_sales_summary`
PARTITION BY sales_date
CLUSTER BY warehouse_key, product_category
OPTIONS(
    enable_refresh=true,
    refresh_interval_minutes=60
)
AS
SELECT
    DATE(f.transaction_timestamp) AS sales_date,
    d.date_key,
    d.year,
    d.month_name,
    p.category AS product_category,
    p.brand AS product_brand,
    c.customer_segment,
    w.warehouse_id,
    w.warehouse_key,
    -- Aggregated measures
    COUNT(DISTINCT f.order_id) AS order_count,
    COUNT(*) AS line_item_count,
    SUM(f.quantity) AS total_quantity,
    SUM(f.gross_sales_amount) AS total_gross_sales,
    SUM(f.discount_amount) AS total_discount,
    SUM(f.net_sales_amount) AS total_net_sales,
    SUM(f.tax_amount) AS total_tax,
    SUM(f.total_amount) AS total_revenue,
    SUM(f.profit_amount) AS total_profit,
    AVG(f.margin_percentage) AS avg_margin_percentage,
    MAX(f.total_amount) AS max_transaction_amount
FROM `project.dwh.fact_sales` f
JOIN `project.dwh.dim_date` d ON f.date_key = d.date_key
JOIN `project.dwh.dim_product` p ON f.product_key = p.product_key AND p.is_current = TRUE
JOIN `project.dwh.dim_customer` c ON f.customer_key = c.customer_key AND c.is_current = TRUE
LEFT JOIN `project.dwh.dim_warehouse` w ON f.warehouse_key = w.warehouse_key
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9;

-- ============================================
-- VIEWS FOR REPORTING
-- ============================================

-- Current Customers View
CREATE OR REPLACE VIEW `project.dwh.vw_current_customers` AS
SELECT
    customer_key,
    customer_id,
    customer_name,
    email,
    phone,
    customer_segment,
    customer_tier,
    loyalty_points,
    lifetime_value,
    country,
    state,
    city,
    postal_code
FROM `project.dwh.dim_customer`
WHERE is_current = TRUE;

-- Current Products View
CREATE OR REPLACE VIEW `project.dwh.vw_current_products` AS
SELECT
    product_key,
    product_id,
    product_name,
    sku,
    brand,
    category,
    subcategory,
    department,
    unit_cost,
    unit_price,
    is_active
FROM `project.dwh.dim_product`
WHERE is_current = TRUE;

-- Sales Detail View
CREATE OR REPLACE VIEW `project.dwh.vw_sales_detail` AS
SELECT
    d.date_value AS sale_date,
    d.year,
    d.quarter,
    d.month_name,
    d.day_name,
    c.customer_name,
    c.customer_segment,
    c.customer_tier,
    c.city AS customer_city,
    c.state AS customer_state,
    p.product_name,
    p.sku,
    p.brand,
    p.category,
    p.subcategory,
    w.warehouse_name,
    w.region AS warehouse_region,
    f.order_id,
    f.invoice_number,
    f.quantity,
    f.unit_price,
    f.unit_cost,
    f.gross_sales_amount,
    f.discount_amount,
    f.net_sales_amount,
    f.tax_amount,
    f.total_amount,
    f.profit_amount,
    f.margin_percentage,
    f.payment_method,
    f.shipping_method
FROM `project.dwh.fact_sales` f
JOIN `project.dwh.dim_date` d ON f.date_key = d.date_key
JOIN `project.dwh.dim_customer` c ON f.customer_key = c.customer_key
JOIN `project.dwh.dim_product` p ON f.product_key = p.product_key
LEFT JOIN `project.dwh.dim_warehouse` w ON f.warehouse_key = w.warehouse_key;

-- ============================================
-- TABLE METADATA AND LABELS
-- ============================================

-- Add labels for data governance
ALTER TABLE `project.dwh.dim_customer`
SET OPTIONS(
    labels=[("pii", "true"), ("gdpr", "true"), ("data_classification", "sensitive")]
);

ALTER TABLE `project.dwh.fact_sales`
SET OPTIONS(
    labels=[("data_classification", "confidential"), ("business_critical", "true")]
);
