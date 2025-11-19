-- AGGREGATE FACT TABLE (Daily Summary)
CREATE TABLE FACT_SALES_DAILY (
    sales_daily_key BIGSERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    store_key INTEGER NOT NULL,
    transaction_count INTEGER,
    total_quantity DECIMAL(12,2),
    total_sales_amount DECIMAL(15,2),
    UNIQUE (date_key, product_key, store_key)
);
