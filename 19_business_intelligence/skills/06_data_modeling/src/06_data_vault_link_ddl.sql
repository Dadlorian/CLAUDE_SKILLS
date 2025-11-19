-- DATA VAULT 2.0: LINK TABLES
-- Links represent relationships between hubs

CREATE TABLE LINK_ORDER (
    order_hash_key CHAR(32) PRIMARY KEY,
    customer_hash_key CHAR(32) NOT NULL,
    product_hash_key CHAR(32) NOT NULL,
    order_line_number INTEGER NOT NULL,
    load_date TIMESTAMP NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    FOREIGN KEY (customer_hash_key) REFERENCES HUB_CUSTOMER(customer_hash_key),
    FOREIGN KEY (product_hash_key) REFERENCES HUB_PRODUCT(product_hash_key)
);

CREATE INDEX idx_link_order_customer ON LINK_ORDER(customer_hash_key);
CREATE INDEX idx_link_order_product ON LINK_ORDER(product_hash_key);
