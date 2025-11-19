# Data Vault 2.0 Patterns Reference

Quick reference for Data Vault 2.0 modeling patterns, best practices, and implementation examples.

## Core Concepts

### Three Main Entities

**Hubs**: Business Keys
```
- Store unique business keys
- Contain no descriptive attributes
- Immutable
- Never deleted
```

**Links**: Relationships
```
- Connect Hubs together
- Represent business events/transactions
- Can connect 2+ Hubs
- Immutable
```

**Satellites**: Context/Attributes
```
- Descriptive information
- Temporal (track history)
- Can be attached to Hubs or Links
- Support SCD Type 2 automatically
```

## Hub Tables

### Hub Structure
```sql
CREATE TABLE hub_customer (
    customer_hk BINARY(16) PRIMARY KEY,      -- Hash key (surrogate)
    customer_id VARCHAR(50) NOT NULL,        -- Business key
    load_date TIMESTAMP NOT NULL,            -- When first seen
    record_source VARCHAR(50) NOT NULL,      -- Source system

    UNIQUE (customer_id)
);
```

### Hub Loading Pattern
```sql
INSERT INTO hub_customer (
    customer_hk,
    customer_id,
    load_date,
    record_source
)
SELECT DISTINCT
    MD5(CONCAT(customer_id)) as customer_hk,
    customer_id,
    CURRENT_TIMESTAMP() as load_date,
    'CRM' as record_source
FROM staging_customers
WHERE customer_id NOT IN (
    SELECT customer_id FROM hub_customer
);
```

### Composite Business Keys
```sql
CREATE TABLE hub_product (
    product_hk BINARY(16) PRIMARY KEY,
    product_code VARCHAR(50) NOT NULL,
    product_region VARCHAR(10) NOT NULL,     -- Part of composite key
    load_date TIMESTAMP NOT NULL,
    record_source VARCHAR(50) NOT NULL,

    UNIQUE (product_code, product_region)
);

-- Hash composite key
SELECT
    MD5(CONCAT(product_code, '||', product_region)) as product_hk
FROM staging_products;
```

## Link Tables

### Link Structure (2 Hubs)
```sql
CREATE TABLE link_order (
    order_link_hk BINARY(16) PRIMARY KEY,    -- Hash of all foreign keys
    customer_hk BINARY(16) NOT NULL,
    product_hk BINARY(16) NOT NULL,
    order_id VARCHAR(50) NOT NULL,           -- Degenerate business key
    load_date TIMESTAMP NOT NULL,
    record_source VARCHAR(50) NOT NULL,

    FOREIGN KEY (customer_hk) REFERENCES hub_customer(customer_hk),
    FOREIGN KEY (product_hk) REFERENCES hub_product(product_hk)
);
```

### Link Loading Pattern
```sql
INSERT INTO link_order (
    order_link_hk,
    customer_hk,
    product_hk,
    order_id,
    load_date,
    record_source
)
SELECT DISTINCT
    MD5(CONCAT(
        hc.customer_hk,
        hp.product_hk,
        s.order_id
    )) as order_link_hk,
    hc.customer_hk,
    hp.product_hk,
    s.order_id,
    CURRENT_TIMESTAMP() as load_date,
    'ECOMMERCE' as record_source
FROM staging_orders s
JOIN hub_customer hc ON s.customer_id = hc.customer_id
JOIN hub_product hp ON s.product_code = hp.product_code
WHERE NOT EXISTS (
    SELECT 1 FROM link_order l
    WHERE l.order_link_hk = MD5(CONCAT(
        hc.customer_hk,
        hp.product_hk,
        s.order_id
    ))
);
```

### Multi-Hub Link (3+ Hubs)
```sql
CREATE TABLE link_shipment (
    shipment_link_hk BINARY(16) PRIMARY KEY,
    order_link_hk BINARY(16) NOT NULL,
    warehouse_hk BINARY(16) NOT NULL,
    carrier_hk BINARY(16) NOT NULL,
    shipment_id VARCHAR(50) NOT NULL,
    load_date TIMESTAMP NOT NULL,
    record_source VARCHAR(50) NOT NULL,

    FOREIGN KEY (order_link_hk) REFERENCES link_order(order_link_hk),
    FOREIGN KEY (warehouse_hk) REFERENCES hub_warehouse(warehouse_hk),
    FOREIGN KEY (carrier_hk) REFERENCES hub_carrier(carrier_hk)
);
```

### Link Without Business Key (Relationship Link)
```sql
CREATE TABLE link_customer_product (
    customer_product_link_hk BINARY(16) PRIMARY KEY,
    customer_hk BINARY(16) NOT NULL,
    product_hk BINARY(16) NOT NULL,
    load_date TIMESTAMP NOT NULL,
    record_source VARCHAR(50) NOT NULL,

    UNIQUE (customer_hk, product_hk),

    FOREIGN KEY (customer_hk) REFERENCES hub_customer(customer_hk),
    FOREIGN KEY (product_hk) REFERENCES hub_product(product_hk)
);
```

## Satellite Tables

### Satellite Structure (Hub Satellite)
```sql
CREATE TABLE sat_customer (
    customer_hk BINARY(16) NOT NULL,         -- FK to Hub
    load_date TIMESTAMP NOT NULL,            -- Effective date
    load_end_date TIMESTAMP,                 -- End date (NULL for current)
    record_source VARCHAR(50) NOT NULL,
    hash_diff BINARY(16) NOT NULL,           -- Hash of all attributes

    -- Descriptive attributes
    customer_name VARCHAR(100),
    email VARCHAR(200),
    phone VARCHAR(20),
    address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(2),
    zip VARCHAR(10),

    PRIMARY KEY (customer_hk, load_date),
    FOREIGN KEY (customer_hk) REFERENCES hub_customer(customer_hk)
);
```

### Satellite Loading Pattern (Type 2)
```sql
-- Step 1: Calculate hash diff for change detection
WITH staging_with_hash AS (
    SELECT
        hc.customer_hk,
        s.customer_name,
        s.email,
        s.phone,
        s.address,
        s.city,
        s.state,
        s.zip,
        MD5(CONCAT_WS('||',
            COALESCE(s.customer_name, ''),
            COALESCE(s.email, ''),
            COALESCE(s.phone, ''),
            COALESCE(s.address, ''),
            COALESCE(s.city, ''),
            COALESCE(s.state, ''),
            COALESCE(s.zip, '')
        )) as hash_diff,
        CURRENT_TIMESTAMP() as load_date,
        'CRM' as record_source
    FROM staging_customers s
    JOIN hub_customer hc ON s.customer_id = hc.customer_id
),

-- Step 2: Close out changed records
changed_records AS (
    SELECT
        s.customer_hk,
        s.hash_diff
    FROM staging_with_hash s
    LEFT JOIN (
        SELECT customer_hk, hash_diff
        FROM sat_customer
        WHERE load_end_date IS NULL
    ) sat
        ON s.customer_hk = sat.customer_hk
    WHERE sat.hash_diff IS NULL  -- New customer
       OR sat.hash_diff != s.hash_diff  -- Changed customer
)

-- Close existing records
UPDATE sat_customer
SET load_end_date = CURRENT_TIMESTAMP()
WHERE customer_hk IN (SELECT customer_hk FROM changed_records)
  AND load_end_date IS NULL;

-- Step 3: Insert new records
INSERT INTO sat_customer
SELECT
    customer_hk,
    load_date,
    NULL as load_end_date,
    record_source,
    hash_diff,
    customer_name,
    email,
    phone,
    address,
    city,
    state,
    zip
FROM staging_with_hash s
WHERE EXISTS (
    SELECT 1 FROM changed_records c
    WHERE c.customer_hk = s.customer_hk
);
```

### Link Satellite
```sql
CREATE TABLE sat_order (
    order_link_hk BINARY(16) NOT NULL,
    load_date TIMESTAMP NOT NULL,
    load_end_date TIMESTAMP,
    record_source VARCHAR(50) NOT NULL,
    hash_diff BINARY(16) NOT NULL,

    -- Order attributes
    order_status VARCHAR(20),
    order_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    shipping_amount DECIMAL(10,2),
    discount_amount DECIMAL(10,2),

    PRIMARY KEY (order_link_hk, load_date),
    FOREIGN KEY (order_link_hk) REFERENCES link_order(order_link_hk)
);
```

### Multi-Active Satellite (Multiple Records per Effective Date)
```sql
CREATE TABLE sat_customer_phone (
    customer_hk BINARY(16) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,       -- Part of PK
    load_date TIMESTAMP NOT NULL,
    load_end_date TIMESTAMP,
    record_source VARCHAR(50) NOT NULL,
    hash_diff BINARY(16) NOT NULL,

    phone_type VARCHAR(20),                  -- Mobile, Home, Work
    is_primary BOOLEAN,

    PRIMARY KEY (customer_hk, phone_number, load_date),
    FOREIGN KEY (customer_hk) REFERENCES hub_customer(customer_hk)
);
```

## Point-in-Time (PIT) Tables

### PIT Structure
```sql
CREATE TABLE pit_customer (
    customer_hk BINARY(16) NOT NULL,
    snapshot_date DATE NOT NULL,

    -- Reference to latest satellite version as of snapshot_date
    sat_customer_hk BINARY(16),
    sat_customer_load_date TIMESTAMP,

    sat_customer_preferences_hk BINARY(16),
    sat_customer_preferences_load_date TIMESTAMP,

    PRIMARY KEY (customer_hk, snapshot_date)
);
```

### PIT Loading Logic
```sql
-- Create PIT table for efficient point-in-time queries
INSERT INTO pit_customer
WITH date_spine AS (
    -- Generate date range
    SELECT DATE '2020-01-01' + (ROW_NUMBER() OVER () - 1) as snapshot_date
    FROM TABLE(GENERATOR(ROWCOUNT => 1826))  -- 5 years of daily snapshots
),

customer_dates AS (
    SELECT DISTINCT customer_hk
    FROM hub_customer
    CROSS JOIN date_spine
    WHERE snapshot_date >= (
        SELECT MIN(load_date::DATE) FROM sat_customer
    )
),

latest_sat_customer AS (
    SELECT
        cd.customer_hk,
        cd.snapshot_date,
        MAX(sc.load_date) as sat_customer_load_date
    FROM customer_dates cd
    LEFT JOIN sat_customer sc
        ON cd.customer_hk = sc.customer_hk
        AND sc.load_date::DATE <= cd.snapshot_date
        AND (sc.load_end_date IS NULL OR sc.load_end_date::DATE > cd.snapshot_date)
    GROUP BY cd.customer_hk, cd.snapshot_date
)

SELECT
    lsc.customer_hk,
    lsc.snapshot_date,
    sc.customer_hk as sat_customer_hk,
    lsc.sat_customer_load_date
FROM latest_sat_customer lsc
LEFT JOIN sat_customer sc
    ON lsc.customer_hk = sc.customer_hk
    AND lsc.sat_customer_load_date = sc.load_date;
```

### Querying with PIT
```sql
-- Get customer data as of specific date
SELECT
    hc.customer_id,
    sc.customer_name,
    sc.email,
    sc.city,
    sc.state
FROM pit_customer pit
JOIN hub_customer hc ON pit.customer_hk = hc.customer_hk
JOIN sat_customer sc
    ON pit.sat_customer_hk = sc.customer_hk
    AND pit.sat_customer_load_date = sc.load_date
WHERE pit.snapshot_date = '2024-01-01';
```

## Bridge Tables

### Bridge Structure
```sql
CREATE TABLE bridge_order_customer (
    order_link_hk BINARY(16) NOT NULL,
    customer_hk BINARY(16) NOT NULL,
    effective_from TIMESTAMP NOT NULL,
    effective_to TIMESTAMP,

    PRIMARY KEY (order_link_hk, customer_hk, effective_from),
    FOREIGN KEY (order_link_hk) REFERENCES link_order(order_link_hk),
    FOREIGN KEY (customer_hk) REFERENCES hub_customer(customer_hk)
);
```

### Bridge Loading Logic
```sql
-- Simplify Link -> Hub relationships for queries
INSERT INTO bridge_order_customer
SELECT DISTINCT
    lo.order_link_hk,
    lo.customer_hk,
    lo.load_date as effective_from,
    NULL as effective_to
FROM link_order lo;
```

## Reference Tables

### Reference Hub Structure
```sql
CREATE TABLE ref_country_code (
    country_code_hk BINARY(16) PRIMARY KEY,
    country_code VARCHAR(3) NOT NULL,        -- ISO code
    load_date TIMESTAMP NOT NULL,
    record_source VARCHAR(50) NOT NULL,

    UNIQUE (country_code)
);

CREATE TABLE ref_sat_country (
    country_code_hk BINARY(16) NOT NULL,
    load_date TIMESTAMP NOT NULL,
    load_end_date TIMESTAMP,
    record_source VARCHAR(50) NOT NULL,

    country_name VARCHAR(100),
    region VARCHAR(50),
    currency_code VARCHAR(3),

    PRIMARY KEY (country_code_hk, load_date),
    FOREIGN KEY (country_code_hk) REFERENCES ref_country_code(country_code_hk)
);
```

## Hash Key Generation

### Standard Hash Key
```sql
-- MD5 hash (16 bytes)
SELECT MD5(CAST(customer_id AS VARCHAR)) as customer_hk
FROM staging;

-- SHA-256 hash (32 bytes, more secure)
SELECT SHA2(CAST(customer_id AS VARCHAR), 256) as customer_hk
FROM staging;
```

### Composite Hash Key
```sql
-- Concatenate with delimiter
SELECT MD5(CONCAT_WS('||',
    CAST(product_code AS VARCHAR),
    CAST(product_region AS VARCHAR)
)) as product_hk
FROM staging;
```

### Link Hash Key
```sql
-- Hash of all parent hash keys + business key
SELECT MD5(CONCAT_WS('||',
    customer_hk,
    product_hk,
    CAST(order_id AS VARCHAR)
)) as order_link_hk
FROM staging;
```

### Hash Diff (Change Detection)
```sql
-- Hash of all satellite attributes
SELECT MD5(CONCAT_WS('||',
    COALESCE(customer_name, ''),
    COALESCE(email, ''),
    COALESCE(phone, ''),
    COALESCE(address, ''),
    COALESCE(city, ''),
    COALESCE(state, ''),
    COALESCE(zip, '')
)) as hash_diff
FROM staging;

-- Important: COALESCE to handle NULLs consistently
```

## Data Vault Best Practices

### Naming Conventions
```
Hubs:      hub_<entity>           (hub_customer)
Links:     link_<entity>          (link_order)
Satellites: sat_<entity>          (sat_customer)
PIT:       pit_<entity>           (pit_customer)
Bridge:    bridge_<entity>        (bridge_order_customer)
Reference: ref_<entity>           (ref_country_code)
```

### Column Naming
```
Hash Keys:       <entity>_hk       (customer_hk)
Link Hash Keys:  <entity>_link_hk  (order_link_hk)
Business Keys:   <entity>_id       (customer_id)
Load Date:       load_date
End Date:        load_end_date
Record Source:   record_source
Hash Diff:       hash_diff
```

### Loading Sequence
```
1. Load Hubs (business keys)
2. Load Links (relationships)
3. Load Satellites (attributes)
4. Build PIT tables (optional, for query performance)
5. Build Bridge tables (optional, for query simplification)
```

### Parallel Loading
```sql
-- Hubs can be loaded in parallel
-- Links depend on Hubs (load after Hubs)
-- Satellites depend on Hubs/Links (load after Links)

-- Example dbt DAG:
hub_customer → link_order → sat_order
hub_product →  ↗
```

### Auditability
```
Every record includes:
- load_date: When record was loaded
- record_source: Source system identifier
- hash_diff: Change detection (Satellites)

Never delete records (soft deletes in Satellites)
Full history preserved automatically
```

## Querying Data Vault

### Current State Query
```sql
-- Get current customer data
SELECT
    hc.customer_id,
    sc.customer_name,
    sc.email,
    sc.city,
    sc.state
FROM hub_customer hc
JOIN sat_customer sc
    ON hc.customer_hk = sc.customer_hk
WHERE sc.load_end_date IS NULL;
```

### Historical Query (Point-in-Time)
```sql
-- Get customer data as of 2023-01-01
SELECT
    hc.customer_id,
    sc.customer_name,
    sc.email,
    sc.city,
    sc.state
FROM hub_customer hc
JOIN sat_customer sc
    ON hc.customer_hk = sc.customer_hk
WHERE sc.load_date <= '2023-01-01 23:59:59'
  AND (sc.load_end_date IS NULL OR sc.load_end_date > '2023-01-01 23:59:59');
```

### Join with Links
```sql
-- Get orders with customer and product details
SELECT
    hc.customer_id,
    sc.customer_name,
    hp.product_code,
    sp.product_name,
    lo.order_id,
    so.order_amount,
    so.order_status
FROM link_order lo
JOIN hub_customer hc ON lo.customer_hk = hc.customer_hk
JOIN sat_customer sc ON hc.customer_hk = sc.customer_hk AND sc.load_end_date IS NULL
JOIN hub_product hp ON lo.product_hk = hp.product_hk
JOIN sat_product sp ON hp.product_hk = sp.product_hk AND sp.load_end_date IS NULL
JOIN sat_order so ON lo.order_link_hk = so.order_link_hk AND so.load_end_date IS NULL;
```

## Business Vault

### Calculated Satellites
```sql
-- Derived attributes
CREATE TABLE sat_customer_metrics (
    customer_hk BINARY(16) NOT NULL,
    load_date TIMESTAMP NOT NULL,
    record_source VARCHAR(50) NOT NULL,

    lifetime_value DECIMAL(15,2),
    total_orders INTEGER,
    avg_order_value DECIMAL(10,2),
    customer_segment VARCHAR(20),
    risk_score DECIMAL(5,2),

    PRIMARY KEY (customer_hk, load_date),
    FOREIGN KEY (customer_hk) REFERENCES hub_customer(customer_hk)
);
```

### Computed Links
```sql
-- Inferred relationships
CREATE TABLE link_customer_product_affinity (
    customer_product_affinity_link_hk BINARY(16) PRIMARY KEY,
    customer_hk BINARY(16) NOT NULL,
    product_hk BINARY(16) NOT NULL,
    load_date TIMESTAMP NOT NULL,
    record_source VARCHAR(50) NOT NULL,

    affinity_score DECIMAL(5,4),

    FOREIGN KEY (customer_hk) REFERENCES hub_customer(customer_hk),
    FOREIGN KEY (product_hk) REFERENCES hub_product(product_hk)
);
```

## Advantages of Data Vault 2.0

**Pros:**
- ✅ Fully auditable
- ✅ Handles source system changes gracefully
- ✅ Parallel loading (Hubs/Links/Sats independent)
- ✅ Historical accuracy
- ✅ Scalable
- ✅ Insert-only (no updates)
- ✅ Supports real-time and batch

**Cons:**
- ❌ Complex to query (many joins)
- ❌ Not intuitive for business users
- ❌ Requires PIT/Bridge for performance
- ❌ More storage (denormalized)
- ❌ Steeper learning curve

## When to Use Data Vault

**Good Fit:**
- Multiple source systems
- Frequently changing source schemas
- Strict audit requirements
- Need full history
- Agile development (parallel teams)

**Not Ideal:**
- Single source system
- Simple dimensional model sufficient
- Business users query directly
- Storage constraints critical
