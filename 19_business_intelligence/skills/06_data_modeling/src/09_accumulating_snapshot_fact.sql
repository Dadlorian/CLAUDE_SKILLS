-- ACCUMULATING SNAPSHOT FACT TABLE
-- Grain: One row per order, updated as order progresses

CREATE TABLE FACT_ORDER_FULFILLMENT (
    order_fulfillment_key BIGSERIAL PRIMARY KEY,
    
    -- Multiple date milestones
    order_date_key INTEGER,
    payment_date_key INTEGER,
    fulfillment_date_key INTEGER,
    ship_date_key INTEGER,
    delivery_date_key INTEGER,
    
    -- Dimensions
    customer_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    warehouse_key INTEGER,
    carrier_key INTEGER,
    
    -- Degenerate dimension
    order_number VARCHAR(20) NOT NULL UNIQUE,
    
    -- Facts
    order_amount DECIMAL(12,2),
    shipping_amount DECIMAL(10,2),
    
    -- Lag measures (calculated from dates)
    days_to_payment INTEGER,
    days_to_fulfillment INTEGER,
    days_to_ship INTEGER,
    days_to_deliver INTEGER,
    total_cycle_time_days INTEGER,
    
    -- Current status
    current_status VARCHAR(20),  -- ORDERED, PAID, FULFILLED, SHIPPED, DELIVERED
    
    -- Audit
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated_date TIMESTAMP
);

CREATE INDEX idx_order_fulfillment_customer ON FACT_ORDER_FULFILLMENT(customer_key);
CREATE INDEX idx_order_fulfillment_status ON FACT_ORDER_FULFILLMENT(current_status);
