# Data Vault 2.0 Components Reference

## Overview

Data Vault 2.0 is an insert-only modeling methodology designed for enterprise data warehouses. It emphasizes auditability, scalability, and flexibility through three core component types: Hubs, Links, and Satellites.

**Key Principles**:
- Insert-only (no updates or deletes in raw vault)
- Complete audit trail
- Source-system aligned
- Parallel loading capability
- Business key-centric design

---

## Core Components

### Hub Tables

**Definition**: Store unique business keys and their first appearance metadata.

**Purpose**:
- Represent core business entities
- One hub per business concept
- Track when business key first appeared
- Enable integration across source systems

**Structure**:
```
HUB_CUSTOMER
- customer_hash_key (PK, hash of business key)
- customer_id (business key)
- load_date (when first seen)
- record_source (which source system)
```

**Detailed Example**:
```sql
CREATE TABLE HUB_CUSTOMER (
    customer_hash_key CHAR(32) PRIMARY KEY,  -- MD5/SHA-256 hash
    customer_id VARCHAR(50) NOT NULL,         -- Natural business key
    load_date TIMESTAMP NOT NULL,             -- First load time
    record_source VARCHAR(50) NOT NULL,       -- Source system identifier
    UNIQUE (customer_id)
);

-- Example data:
customer_hash_key                  | customer_id | load_date           | record_source
A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6  | CUST-12345  | 2024-01-15 10:30:00 | CRM_SYSTEM
```

**Business Key Characteristics**:
- Unique identifier in source system
- Immutable (never changes)
- Meaningful to business (not surrogate)
- May be composite (multi-column)

**Hub Naming Convention**:
- Prefix: `HUB_`
- Singular noun: `HUB_CUSTOMER`, `HUB_PRODUCT`, `HUB_ACCOUNT`

**Hub Rules**:
1. Only business keys and metadata (no descriptive attributes)
2. One row per unique business key (forever)
3. Never updated or deleted
4. Load_date is the first time key was seen
5. Record_source identifies originating system

**Composite Business Keys**:
```sql
HUB_ORDER_LINE
- order_line_hash_key (PK, hash of order_id + line_number)
- order_id (part of composite business key)
- line_number (part of composite business key)
- load_date
- record_source
```

---

### Link Tables

**Definition**: Represent relationships (associations) between Hubs.

**Purpose**:
- Connect business entities
- Track relationships over time
- Handle many-to-many relationships
- Support complex multi-way relationships

**Structure**:
```
LINK_CUSTOMER_PRODUCT
- customer_product_hash_key (PK, hash of relationship)
- customer_hash_key (FK to HUB_CUSTOMER)
- product_hash_key (FK to HUB_PRODUCT)
- load_date
- record_source
```

**Detailed Example**:
```sql
CREATE TABLE LINK_ORDER (
    order_hash_key CHAR(32) PRIMARY KEY,
    customer_hash_key CHAR(32) NOT NULL,
    product_hash_key CHAR(32) NOT NULL,
    store_hash_key CHAR(32) NOT NULL,
    load_date TIMESTAMP NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    FOREIGN KEY (customer_hash_key) REFERENCES HUB_CUSTOMER(customer_hash_key),
    FOREIGN KEY (product_hash_key) REFERENCES HUB_PRODUCT(product_hash_key),
    FOREIGN KEY (store_hash_key) REFERENCES HUB_STORE(store_hash_key)
);

-- Example data:
order_hash_key                     | customer_hash_key              | product_hash_key               | store_hash_key                 | load_date           | record_source
X1Y2Z3A4B5C6D7E8F9G0H1I2J3K4L5M6  | A1B2C3...                      | P1Q2R3...                      | S1T2U3...                      | 2024-06-15 14:22:00 | POS_SYSTEM
```

**Link Types**:

1. **Simple Link (Two Hubs)**:
```
LINK_CUSTOMER_ADDRESS
- customer_address_hash_key
- customer_hash_key
- address_hash_key
- load_date
- record_source
```

2. **Multi-Way Link (Three+ Hubs)**:
```
LINK_ORDER (Customer purchases Product at Store)
- order_hash_key
- customer_hash_key
- product_hash_key
- store_hash_key
- date_hash_key
- load_date
- record_source
```

3. **Hierarchical Link (Hub to itself)**:
```
LINK_EMPLOYEE_HIERARCHY
- employee_hierarchy_hash_key
- employee_hash_key (employee)
- manager_hash_key (also points to HUB_EMPLOYEE)
- load_date
- record_source
```

**Link Naming Convention**:
- Prefix: `LINK_`
- Hub names in relationship: `LINK_CUSTOMER_PRODUCT`
- Or business process: `LINK_ORDER`, `LINK_SHIPMENT`

**Link Rules**:
1. Contains only hub foreign keys and metadata
2. No descriptive attributes (those go in satellites)
3. Can connect 2 or more hubs
4. Never links to other links (links connect hubs only)
5. Insert-only (same relationship can appear multiple times from different sources)

**Degenerate Data in Links**:
Some implementations allow degenerate keys (transaction IDs) in links:
```
LINK_ORDER
- order_hash_key
- customer_hash_key
- product_hash_key
- order_number (degenerate - unique transaction identifier)
- load_date
- record_source
```

---

### Satellite Tables

**Definition**: Store descriptive attributes and track all changes over time.

**Purpose**:
- Contain descriptive data
- Track complete change history
- Separate volatile from stable attributes
- Enable point-in-time accuracy

**Structure**:
```
SAT_CUSTOMER
- customer_hash_key (PK, FK to HUB_CUSTOMER)
- load_date (PK, part of composite key)
- load_end_date (when this version was superseded)
- customer_name
- email
- phone
- address
- hash_diff (hash of all attributes for change detection)
- record_source
```

**Detailed Example**:
```sql
CREATE TABLE SAT_CUSTOMER (
    customer_hash_key CHAR(32) NOT NULL,
    load_date TIMESTAMP NOT NULL,
    load_end_date TIMESTAMP,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    city VARCHAR(50),
    state VARCHAR(2),
    zip VARCHAR(10),
    hash_diff CHAR(32) NOT NULL,  -- Hash of all payload columns
    record_source VARCHAR(50),
    PRIMARY KEY (customer_hash_key, load_date),
    FOREIGN KEY (customer_hash_key) REFERENCES HUB_CUSTOMER(customer_hash_key)
);

-- Example data (showing changes over time):
customer_hash_key  | load_date           | load_end_date       | customer_name | email           | hash_diff     | record_source
A1B2C3...          | 2024-01-15 10:30:00 | 2024-06-01 09:00:00 | John Smith    | john@old.com    | H1A2S3H4...   | CRM_SYSTEM
A1B2C3...          | 2024-06-01 09:00:00 | NULL                | John Smith    | john@new.com    | H5B6S7H8...   | CRM_SYSTEM
```

**Satellite Types**:

1. **Hub Satellite**: Describes hub attributes
```
SAT_PRODUCT
- product_hash_key (FK to HUB_PRODUCT)
- load_date
- product_name
- description
- category
- unit_price
- hash_diff
- record_source
```

2. **Link Satellite**: Describes relationship attributes
```
SAT_ORDER (describes LINK_ORDER)
- order_hash_key (FK to LINK_ORDER)
- load_date
- order_date
- order_status
- total_amount
- payment_method
- hash_diff
- record_source
```

3. **Multi-Source Satellite**: Same hub, different sources
```
SAT_CUSTOMER_CRM (from CRM system)
- customer_hash_key
- load_date
- crm_segment
- loyalty_status
- hash_diff
- record_source ('CRM_SYSTEM')

SAT_CUSTOMER_WEB (from Web system)
- customer_hash_key
- load_date
- web_preferences
- last_login_date
- hash_diff
- record_source ('WEB_SYSTEM')
```

4. **Effectivity Satellite**: Temporal validity (when relationship was active)
```
SAT_CUSTOMER_ADDRESS_EFFECTIVITY
- customer_address_hash_key (FK to LINK_CUSTOMER_ADDRESS)
- load_date
- effective_from_date
- effective_to_date
- hash_diff
- record_source
```

**Satellite Naming Convention**:
- Prefix: `SAT_`
- Hub/Link name: `SAT_CUSTOMER`, `SAT_ORDER`
- Optional suffix for source: `SAT_CUSTOMER_CRM`, `SAT_CUSTOMER_WEB`

**Satellite Rules**:
1. Must have at least one descriptive attribute
2. Hash diff for change detection (hash of all payload)
3. Load_date + hash_key form composite primary key
4. Load_end_date for end-dating (optional, can be calculated)
5. Insert-only (new row for each change)
6. NULL load_end_date indicates current record

**Hash Diff Calculation**:
```sql
-- Hash of all payload attributes for change detection
MD5(CONCAT(
    COALESCE(customer_name, ''),
    COALESCE(email, ''),
    COALESCE(phone, ''),
    COALESCE(address, '')
))
```

**Change Detection**:
```sql
-- Only insert if hash_diff is different from current record
INSERT INTO SAT_CUSTOMER
SELECT
    customer_hash_key,
    CURRENT_TIMESTAMP as load_date,
    NULL as load_end_date,
    customer_name,
    email,
    phone,
    hash_diff,
    record_source
FROM staging.customers s
WHERE NOT EXISTS (
    SELECT 1 FROM SAT_CUSTOMER sat
    WHERE sat.customer_hash_key = s.customer_hash_key
      AND sat.load_end_date IS NULL
      AND sat.hash_diff = s.hash_diff
);
```

---

## Advanced Components

### Point-in-Time (PIT) Tables

**Definition**: Performance optimization structure for time-variant queries.

**Purpose**:
- Fast lookup of dimension state at any point in time
- Pre-join satellites for query performance
- Snapshot of satellite keys at regular intervals

**Structure**:
```
PIT_CUSTOMER (daily snapshots)
- customer_hash_key (PK)
- snapshot_date (PK)
- sat_customer_hash_key (which SAT_CUSTOMER row was active)
- sat_customer_load_date (load_date of active SAT_CUSTOMER row)
- sat_customer_crm_hash_key
- sat_customer_crm_load_date
- sat_customer_web_hash_key
- sat_customer_web_load_date
```

**Example**:
```sql
CREATE TABLE PIT_CUSTOMER_DAILY (
    customer_hash_key CHAR(32) NOT NULL,
    snapshot_date DATE NOT NULL,
    sat_customer_hash_key CHAR(32),
    sat_customer_load_date TIMESTAMP,
    sat_customer_crm_hash_key CHAR(32),
    sat_customer_crm_load_date TIMESTAMP,
    PRIMARY KEY (customer_hash_key, snapshot_date)
);

-- Usage: Get customer attributes as of specific date
SELECT
    h.customer_id,
    sc.customer_name,
    sc.email,
    scrm.loyalty_status
FROM PIT_CUSTOMER_DAILY pit
JOIN HUB_CUSTOMER h ON pit.customer_hash_key = h.customer_hash_key
JOIN SAT_CUSTOMER sc ON pit.sat_customer_hash_key = sc.customer_hash_key
    AND pit.sat_customer_load_date = sc.load_date
JOIN SAT_CUSTOMER_CRM scrm ON pit.sat_customer_crm_hash_key = scrm.customer_hash_key
    AND pit.sat_customer_crm_load_date = scrm.load_date
WHERE pit.snapshot_date = '2024-06-15';
```

**Benefits**:
- Dramatically improves query performance for time-variant queries
- Pre-calculated joins
- Regular snapshot intervals (daily, weekly, monthly)

---

### Bridge Tables

**Definition**: Dimensional representation of Data Vault structures for reporting.

**Purpose**:
- Convert Data Vault to dimensional model
- Provide flattened, denormalized views
- Optimize for BI tool consumption

**Structure**:
```
BRIDGE_CUSTOMER (dimensional view of customer)
- customer_key (surrogate key for BI tools)
- customer_hash_key (link to hub)
- customer_id (business key)
- customer_name
- email
- phone
- address
- crm_segment
- loyalty_status
- web_preferences
- effective_date
- expiration_date
- current_flag
```

**Example**:
```sql
CREATE VIEW BRIDGE_CUSTOMER AS
SELECT
    ROW_NUMBER() OVER (ORDER BY h.customer_hash_key, sc.load_date) as customer_key,
    h.customer_hash_key,
    h.customer_id,
    sc.customer_name,
    sc.email,
    sc.phone,
    scrm.loyalty_status,
    sc.load_date as effective_date,
    COALESCE(sc.load_end_date, '9999-12-31') as expiration_date,
    CASE WHEN sc.load_end_date IS NULL THEN 'Y' ELSE 'N' END as current_flag
FROM HUB_CUSTOMER h
JOIN SAT_CUSTOMER sc ON h.customer_hash_key = sc.customer_hash_key
LEFT JOIN SAT_CUSTOMER_CRM scrm ON h.customer_hash_key = scrm.customer_hash_key
    AND sc.load_date BETWEEN scrm.load_date AND COALESCE(scrm.load_end_date, '9999-12-31');
```

---

## Raw Vault vs Business Vault

### Raw Vault
**Characteristics**:
- Source-system aligned
- No business rules applied
- Insert-only
- Complete audit trail
- Hubs, Links, Satellites only

**Purpose**:
- Legal record of source data
- Audit and compliance
- Single version of truth
- Source for recreating business vault

### Business Vault
**Characteristics**:
- Business rules applied
- Calculated fields
- Derived data
- Soft business rules
- Hash keys match raw vault

**Components**:

1. **Computed Satellites**: Calculated attributes
```
SAT_CUSTOMER_COMPUTED
- customer_hash_key
- load_date
- customer_age (calculated from birth_date)
- customer_tenure_days (calculated from signup_date)
- customer_lifetime_value (aggregated from facts)
- hash_diff
- record_source ('BUSINESS_VAULT')
```

2. **Reference Tables**: Business reference data
```
REF_PRODUCT_CATEGORY_HIERARCHY
- category_code (PK)
- category_name
- parent_category_code
- category_level
- effective_date
- expiration_date
```

3. **Business Links**: Derived relationships
```
LINK_CUSTOMER_HIERARCHY (computed from addresses, phone numbers)
- customer_hierarchy_hash_key
- parent_customer_hash_key
- child_customer_hash_key
- relationship_type
- confidence_score
- load_date
- record_source ('BUSINESS_VAULT')
```

---

## Hash Keys

### Purpose
- Fast joins (fixed length)
- Parallel loading (distribute by hash)
- Change detection (hash diff)
- Multi-source integration

### Hash Key Standards
```sql
-- MD5 (32 characters, fast, sufficient for most cases)
MD5(CONCAT(COALESCE(business_key_column1, ''), '|',
           COALESCE(business_key_column2, '')))

-- SHA-256 (64 characters, more collision-resistant)
SHA2(CONCAT(COALESCE(business_key_column1, ''), '|',
            COALESCE(business_key_column2, '')), 256)
```

### Hash Key Components
1. **Hub Hash Key**: Hash of business key only
2. **Link Hash Key**: Hash of all hub hash keys in relationship
3. **Hash Diff**: Hash of all satellite payload columns

**Example**:
```sql
-- Hub hash key
customer_hash_key = MD5(customer_id)

-- Link hash key (deterministic order)
order_hash_key = MD5(CONCAT(customer_hash_key, '|', product_hash_key))

-- Hash diff (all payload columns)
hash_diff = MD5(CONCAT(
    COALESCE(customer_name, ''), '|',
    COALESCE(email, ''), '|',
    COALESCE(phone, ''), '|',
    COALESCE(address, '')
))
```

---

## Loading Patterns

### Parallel Loading
Each source system can load independently in parallel:
```
Source A → HUB_CUSTOMER, SAT_CUSTOMER_SOURCE_A
Source B → HUB_CUSTOMER, SAT_CUSTOMER_SOURCE_B
Source C → HUB_CUSTOMER, SAT_CUSTOMER_SOURCE_C
```

Same business key from different sources gets same hash key → merges in Hub.

### Insert-Only Pattern
```sql
-- Always insert, never update
INSERT INTO HUB_CUSTOMER
SELECT customer_hash_key, customer_id, CURRENT_TIMESTAMP, 'CRM'
FROM staging.customers
WHERE customer_hash_key NOT IN (SELECT customer_hash_key FROM HUB_CUSTOMER);

INSERT INTO SAT_CUSTOMER
SELECT customer_hash_key, CURRENT_TIMESTAMP, NULL, customer_name, email, hash_diff, 'CRM'
FROM staging.customers
WHERE hash_diff NOT IN (
    SELECT hash_diff FROM SAT_CUSTOMER
    WHERE customer_hash_key = staging.customers.customer_hash_key
      AND load_end_date IS NULL
);
```

---

## Best Practices

1. **Always use hash keys** for joins and relationships
2. **Include hash_diff** in all satellites for change detection
3. **Never delete** from raw vault (archive if needed)
4. **Separate raw and business vault** clearly
5. **Use PIT and Bridge tables** for query performance
6. **Partition satellites** by load_date for large volumes
7. **Index hash keys** and load_date columns
8. **Document record_source** values consistently
9. **Version control** Data Vault design and ETL
10. **Generate code** where possible (many DV tools available)

## Common Patterns

| Pattern | Use Case | Structure |
|---------|----------|-----------|
| Hub | Core business entity | Business key + metadata |
| Link | Relationship/transaction | Hub FKs + metadata |
| Satellite | Descriptive attributes | Hub/Link FK + attributes + history |
| PIT | Query performance | Snapshot of satellite keys |
| Bridge | Dimensional view | Flattened for BI tools |
| Effectivity Satellite | Temporal validity | Effective from/to dates |
| Multi-source Satellite | Different sources | Separate satellite per source |
| Computed Satellite | Business rules | Calculated fields |
