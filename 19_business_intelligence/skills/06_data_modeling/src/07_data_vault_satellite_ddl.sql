-- DATA VAULT 2.0: SATELLITE TABLES
-- Satellites store descriptive attributes and track history

CREATE TABLE SAT_CUSTOMER (
    customer_hash_key CHAR(32) NOT NULL,
    load_date TIMESTAMP NOT NULL,
    load_end_date TIMESTAMP,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(200),
    city VARCHAR(50),
    state CHAR(2),
    zip VARCHAR(10),
    hash_diff CHAR(32) NOT NULL,  -- Hash of all attributes
    record_source VARCHAR(50),
    PRIMARY KEY (customer_hash_key, load_date),
    FOREIGN KEY (customer_hash_key) REFERENCES HUB_CUSTOMER(customer_hash_key)
);

CREATE TABLE SAT_PRODUCT (
    product_hash_key CHAR(32) NOT NULL,
    load_date TIMESTAMP NOT NULL,
    load_end_date TIMESTAMP,
    product_name VARCHAR(200),
    category VARCHAR(100),
    unit_price DECIMAL(10,2),
    hash_diff CHAR(32) NOT NULL,
    record_source VARCHAR(50),
    PRIMARY KEY (product_hash_key, load_date),
    FOREIGN KEY (product_hash_key) REFERENCES HUB_PRODUCT(product_hash_key)
);
