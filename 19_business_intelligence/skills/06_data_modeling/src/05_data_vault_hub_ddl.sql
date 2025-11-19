-- DATA VAULT 2.0: HUB TABLES
-- Hubs store unique business keys

CREATE TABLE HUB_CUSTOMER (
    customer_hash_key CHAR(32) PRIMARY KEY,  -- MD5 hash of customer_id
    customer_id VARCHAR(50) NOT NULL UNIQUE,  -- Natural business key
    load_date TIMESTAMP NOT NULL,  -- When first seen
    record_source VARCHAR(50) NOT NULL,  -- Source system
    CONSTRAINT idx_hub_customer_id UNIQUE (customer_id)
);

CREATE TABLE HUB_PRODUCT (
    product_hash_key CHAR(32) PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    load_date TIMESTAMP NOT NULL,
    record_source VARCHAR(50) NOT NULL
);

CREATE TABLE HUB_ORDER (
    order_hash_key CHAR(32) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL UNIQUE,
    load_date TIMESTAMP NOT NULL,
    record_source VARCHAR(50) NOT NULL
);
