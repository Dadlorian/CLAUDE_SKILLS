-- INDEXING STRATEGY
-- Fact table: bitmap indexes on FKs (Oracle/PostgreSQL)
CREATE INDEX idx_sales_date_bitmap ON FACT_SALES_TRANSACTION USING BITMAP(date_key);

-- Dimension: B-tree on business key
CREATE INDEX idx_customer_id ON DIM_CUSTOMER(customer_id);

-- Composite for common queries
CREATE INDEX idx_sales_date_product ON FACT_SALES_TRANSACTION(date_key, product_key);
