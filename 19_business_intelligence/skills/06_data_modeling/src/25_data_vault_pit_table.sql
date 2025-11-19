-- DATA VAULT: Point-in-Time (PIT) Table
CREATE TABLE PIT_CUSTOMER_DAILY (
    customer_hash_key CHAR(32) NOT NULL,
    snapshot_date DATE NOT NULL,
    sat_customer_hash_key CHAR(32),
    sat_customer_load_date TIMESTAMP,
    PRIMARY KEY (customer_hash_key, snapshot_date)
);
