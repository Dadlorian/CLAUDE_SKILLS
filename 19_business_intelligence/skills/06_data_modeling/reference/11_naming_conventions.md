# Naming Conventions Reference

## Overview

Consistent naming conventions are critical for maintainability, usability, and team productivity. Good names are self-documenting and reduce ambiguity.

**Principles**:
- **Clarity**: Names should be obvious and unambiguous
- **Consistency**: Same pattern across all objects
- **Business-Friendly**: Use terms business users understand
- **Descriptive**: Avoid cryptic abbreviations
- **Standardized**: Follow organization-wide standards

---

## Table Naming

### Dimension Tables

**Pattern**: `DIM_<ENTITY_NAME>`

**Examples**:
```
DIM_CUSTOMER
DIM_PRODUCT
DIM_DATE
DIM_TIME
DIM_EMPLOYEE
DIM_STORE
DIM_ACCOUNT
DIM_PROMOTION
```

**Rules**:
- Always use `DIM_` prefix
- Singular noun (not plural): `DIM_CUSTOMER` not `DIM_CUSTOMERS`
- Descriptive business term: `DIM_CUSTOMER` not `DIM_CUST`
- No abbreviations unless universally understood: `DIM_SKU` acceptable

**Special Cases**:
```
DIM_DATE (not DIM_TIME or DIM_CALENDAR)
DIM_TIME (for intraday time)
DIM_GEOGRAPHY (or DIM_LOCATION if geographic)
```

---

### Fact Tables

**Pattern**: `FACT_<BUSINESS_PROCESS>`

**Examples**:
```
FACT_SALES
FACT_SALES_TRANSACTION
FACT_ORDER
FACT_INVENTORY
FACT_SHIPMENT
FACT_PAYMENT
FACT_ACCOUNT_BALANCE
FACT_CUSTOMER_ACTIVITY
```

**Rules**:
- Always use `FACT_` prefix
- Business process name (what it measures)
- Singular or plural based on convention
- Include grain indicator for aggregates:
  - `FACT_SALES_TRANSACTION` (atomic)
  - `FACT_SALES_DAILY` (daily aggregate)
  - `FACT_SALES_MONTHLY` (monthly aggregate)

**Grain Suffixes**:
```
FACT_SALES_TRANSACTION (or FACT_SALES_LINE_ITEM)
FACT_SALES_ORDER
FACT_SALES_DAILY
FACT_SALES_WEEKLY
FACT_SALES_MONTHLY
FACT_SALES_YEARLY
```

---

### Bridge Tables

**Pattern**: `BRIDGE_<ENTITIES>`

**Examples**:
```
BRIDGE_ACCOUNT_CUSTOMER (many accounts to many customers)
BRIDGE_PRODUCT_PROMOTION (many products to many promotions)
BRIDGE_EMPLOYEE_HIERARCHY (self-referencing hierarchy)
```

**Alternative for Dimensional Views**:
```
BRIDGE_CUSTOMER (dimensional view of Data Vault customer)
BRIDGE_PRODUCT (dimensional view of Data Vault product)
```

---

### Data Vault Tables

**Hub Pattern**: `HUB_<ENTITY>`
```
HUB_CUSTOMER
HUB_PRODUCT
HUB_ORDER
HUB_ACCOUNT
```

**Link Pattern**: `LINK_<ENTITIES>` or `LINK_<BUSINESS_PROCESS>`
```
LINK_CUSTOMER_ACCOUNT
LINK_ORDER (connects customer, product, store)
LINK_EMPLOYEE_HIERARCHY
```

**Satellite Pattern**: `SAT_<HUB/LINK>_<SOURCE>` (optional source suffix)
```
SAT_CUSTOMER
SAT_CUSTOMER_CRM
SAT_CUSTOMER_WEB
SAT_ORDER
SAT_ORDER_SHIPPING
```

**Point-in-Time**: `PIT_<ENTITY>_<FREQUENCY>`
```
PIT_CUSTOMER_DAILY
PIT_PRODUCT_MONTHLY
```

---

### Staging Tables

**Pattern**: `STG_<SOURCE>_<ENTITY>`

**Examples**:
```
STG_CRM_CUSTOMER
STG_ERP_ORDER
STG_WEB_CLICKSTREAM
STG_POS_TRANSACTION
```

**Rules**:
- `STG_` prefix indicates staging/temporary
- Include source system identifier
- Match source table name when possible
- Temporary tables, can be truncated

---

### Reference/Lookup Tables

**Pattern**: `REF_<CATEGORY>` or `LKP_<CATEGORY>`

**Examples**:
```
REF_COUNTRY
REF_STATE
REF_CURRENCY
REF_HOLIDAY
REF_PRODUCT_CATEGORY
LKP_STATUS_CODE
LKP_PAYMENT_METHOD
```

---

### Aggregate/Summary Tables

**Pattern**: `AGG_<FACT>_<GRAIN>` or include grain in fact name

**Examples**:
```
AGG_SALES_DAILY
AGG_SALES_MONTHLY
AGG_CUSTOMER_MONTHLY
FACT_SALES_DAILY (alternative: include in FACT prefix)
```

---

## Column Naming

### Primary Keys

**Pattern**: `<table_name>_key` (singular, surrogate)

**Examples**:
```sql
DIM_CUSTOMER
- customer_key (PRIMARY KEY, surrogate)

DIM_PRODUCT
- product_key (PRIMARY KEY, surrogate)

FACT_SALES
- sales_key (PRIMARY KEY, surrogate)
```

**Rules**:
- Singular: `customer_key` not `customers_key`
- Suffix: `_key` for surrogate keys
- Integer datatype
- Auto-increment or sequence-generated

---

### Foreign Keys

**Pattern**: `<dimension_name>_key` (matches dimension PK)

**Examples**:
```sql
FACT_SALES
- date_key (FK to DIM_DATE.date_key)
- customer_key (FK to DIM_CUSTOMER.customer_key)
- product_key (FK to DIM_PRODUCT.product_key)
- store_key (FK to DIM_STORE.store_key)
```

**Rules**:
- Match the target dimension's primary key name exactly
- Enables clear join relationships
- Same datatype as target primary key

**Role-Playing Dimensions**:
```sql
FACT_ORDER
- order_date_key (FK to DIM_DATE.date_key)
- ship_date_key (FK to DIM_DATE.date_key)
- delivery_date_key (FK to DIM_DATE.date_key)
```

---

### Natural/Business Keys

**Pattern**: `<entity>_id` or `<entity>_number` or `<entity>_code`

**Examples**:
```sql
DIM_CUSTOMER
- customer_key (surrogate PK)
- customer_id (natural business key)
- customer_number (alternative)

DIM_PRODUCT
- product_key (surrogate PK)
- product_id (natural business key)
- sku (specific product identifier)
- upc (barcode)

DIM_STATE
- state_key (surrogate PK)
- state_code (natural key: "CA", "NY")
- state_abbreviation (alternative)
```

**Suffixes**:
- `_id`: Unique identifier
- `_number`: Sequential or formatted number
- `_code`: Short code/abbreviation
- `_name`: Full descriptive name

---

### Descriptive Attributes

**Pattern**: `<entity>_<attribute>` or `<attribute>` (if context clear)

**Examples**:
```sql
DIM_CUSTOMER
- customer_name
- customer_type
- customer_segment
- email_address (or just "email")
- phone_number (or just "phone")
- street_address (or just "address")
- city
- state
- zip_code (or "postal_code")
```

**Clarity Through Context**:
```sql
-- In DIM_CUSTOMER, "name" is clear (customer_name)
DIM_CUSTOMER
- customer_name (or just "name" if unambiguous)

-- In FACT_SALES, be explicit
FACT_SALES
- sales_amount (not just "amount")
- quantity (context makes it clear)
```

---

### Fact Measures

**Pattern**: `<measure_name>` with suffix indicating type

**Suffixes**:
- `_amount`: Monetary value
- `_quantity`: Numeric count of items
- `_count`: Number of occurrences
- `_rate`: Percentage or ratio
- `_flag`: Boolean/binary indicator

**Examples**:
```sql
FACT_SALES
- sales_amount
- discount_amount
- tax_amount
- total_amount
- quantity (quantity of items)
- transaction_count
- profit_amount
- margin_rate

FACT_ACCOUNT_BALANCE
- beginning_balance
- ending_balance
- deposit_amount
- withdrawal_amount
- transaction_count
- average_balance
```

---

### Dates and Times

**Pattern**: `<event>_date`, `<event>_time`, `<event>_timestamp`, `<event>_date_key`

**Examples**:
```sql
-- Dimension tables
DIM_CUSTOMER
- birth_date
- signup_date
- effective_date (SCD Type 2)
- expiration_date (SCD Type 2)
- created_date (audit)
- modified_date (audit)

-- Fact tables (use keys for dimensional dates)
FACT_ORDER
- order_date_key (FK to DIM_DATE)
- ship_date_key (FK to DIM_DATE)
- order_timestamp (actual timestamp, if needed)

-- Accumulating snapshot facts
FACT_ORDER_FULFILLMENT
- order_date_key
- payment_date_key
- ship_date_key
- delivery_date_key
```

**Date vs Timestamp vs Key**:
- `_date`: DATE datatype (2024-06-15)
- `_timestamp`: TIMESTAMP datatype (2024-06-15 14:35:22)
- `_date_key`: Integer FK to DIM_DATE (20240615)
- `_time_key`: Integer FK to DIM_TIME (143522)

---

### Boolean/Flag Columns

**Pattern**: `is_<condition>` or `<attribute>_flag`

**Examples**:
```sql
DIM_CUSTOMER
- is_active (BOOLEAN or CHAR(1))
- is_deleted (BOOLEAN or CHAR(1))
- current_flag (SCD Type 2 indicator)

DIM_PRODUCT
- is_discontinued
- is_promotional
- is_seasonal

DIM_DATE
- is_holiday
- is_weekday
- is_weekend
- is_business_day
- is_last_day_of_month
```

**Values**:
- BOOLEAN: TRUE/FALSE (if supported)
- CHAR(1): 'Y'/'N' or '1'/'0'
- INTEGER: 1/0

---

### Audit Columns

**Standard Audit Columns**:
```sql
-- Every table should have
- created_date TIMESTAMP
- created_by VARCHAR(50)
- modified_date TIMESTAMP
- modified_by VARCHAR(50)
- source_system VARCHAR(50)
- etl_batch_id BIGINT
```

**Data Vault Audit Columns**:
```sql
-- Hubs
- load_date TIMESTAMP
- record_source VARCHAR(50)

-- Satellites
- load_date TIMESTAMP (part of PK)
- load_end_date TIMESTAMP
- hash_diff CHAR(32)
- record_source VARCHAR(50)
```

---

### SCD Type 2 Columns

**Standard Set**:
```sql
- effective_date DATE (or effective_timestamp)
- expiration_date DATE (or expiration_timestamp)
- current_flag CHAR(1) ('Y'/'N')
- version_number INTEGER
```

**Alternative Names**:
```
- valid_from / valid_to
- start_date / end_date
- effective_from / effective_to
- is_current / current_indicator
- row_version / version_id
```

---

## Naming Anti-Patterns to Avoid

### 1. Cryptic Abbreviations
```
❌ cst_k, prd_nm, addr_ln_1
✓ customer_key, product_name, address_line_1
```

### 2. Inconsistent Prefixes
```
❌ Customer, DIM_Product, tblStore, d_Employee
✓ DIM_CUSTOMER, DIM_PRODUCT, DIM_STORE, DIM_EMPLOYEE
```

### 3. Plural Table Names (when using singular convention)
```
❌ DIM_CUSTOMERS, DIM_PRODUCTS
✓ DIM_CUSTOMER, DIM_PRODUCT
```

### 4. Reserved Words
```
❌ order, user, date, table, column
✓ sales_order, dim_user, dim_date (with prefix)
```

### 5. Same Name for Different Meanings
```
❌ DIM_CUSTOMER.id (natural key)
    FACT_SALES.id (surrogate key)
✓ DIM_CUSTOMER.customer_id (natural key)
    FACT_SALES.sales_key (surrogate key)
```

### 6. Hungarian Notation
```
❌ intCustomerKey, varCustomerName, dtCreatedDate
✓ customer_key, customer_name, created_date
```

### 7. Meaningless Names
```
❌ field1, field2, col_a, temp_data
✓ customer_name, order_amount, staging_data
```

---

## Case Conventions

### Options

**snake_case** (Recommended for databases):
```
customer_key
product_name
sales_amount
order_date
```

**PascalCase**:
```
CustomerKey
ProductName
SalesAmount
OrderDate
```

**camelCase**:
```
customerKey
productName
salesAmount
orderDate
```

**SCREAMING_SNAKE_CASE**:
```
CUSTOMER_KEY
PRODUCT_NAME
SALES_AMOUNT
ORDER_DATE
```

### Recommendation
Use **snake_case** for database objects:
- Case-insensitive in most databases
- Readable and scannable
- Standard in SQL community
- Works well with underscores as separators

---

## Full Example

### Dimensional Model
```sql
-- Date dimension (conformed)
CREATE TABLE DIM_DATE (
    date_key INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    day_of_week INTEGER,
    day_name VARCHAR(10),
    month_number INTEGER,
    month_name VARCHAR(10),
    quarter_number INTEGER,
    year INTEGER,
    fiscal_year INTEGER,
    is_holiday CHAR(1),
    is_weekday CHAR(1),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customer dimension (Type 2 SCD)
CREATE TABLE DIM_CUSTOMER (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(100),
    customer_type VARCHAR(20),
    customer_segment VARCHAR(30),
    email_address VARCHAR(100),
    phone_number VARCHAR(20),
    street_address VARCHAR(200),
    city VARCHAR(50),
    state_code CHAR(2),
    zip_code VARCHAR(10),
    effective_date DATE NOT NULL,
    expiration_date DATE NOT NULL DEFAULT '9999-12-31',
    current_flag CHAR(1) NOT NULL DEFAULT 'Y',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP,
    source_system VARCHAR(50)
);

-- Product dimension
CREATE TABLE DIM_PRODUCT (
    product_key INTEGER PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    sku VARCHAR(50),
    product_name VARCHAR(200),
    product_description TEXT,
    brand_name VARCHAR(100),
    category_name VARCHAR(100),
    subcategory_name VARCHAR(100),
    department_name VARCHAR(100),
    unit_price DECIMAL(10,2),
    is_active CHAR(1),
    is_discontinued CHAR(1),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP,
    source_system VARCHAR(50)
);

-- Sales fact table (transaction grain)
CREATE TABLE FACT_SALES_TRANSACTION (
    sales_transaction_key BIGINT PRIMARY KEY,
    date_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    store_key INTEGER NOT NULL,
    promotion_key INTEGER NOT NULL,
    transaction_number VARCHAR(20) NOT NULL,
    line_number INTEGER NOT NULL,
    quantity DECIMAL(10,2),
    unit_price DECIMAL(10,2),
    extended_price DECIMAL(12,2),
    discount_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    total_amount DECIMAL(12,2),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_system VARCHAR(50),
    FOREIGN KEY (date_key) REFERENCES DIM_DATE(date_key),
    FOREIGN KEY (customer_key) REFERENCES DIM_CUSTOMER(customer_key),
    FOREIGN KEY (product_key) REFERENCES DIM_PRODUCT(product_key)
);
```

---

## Documentation Standards

### Table Documentation
```
Table: DIM_CUSTOMER
Purpose: Customer dimension supporting sales, service, and finance processes
Grain: One row per customer per version (SCD Type 2)
Source: CRM system (primary), ERP system (supplemental)
Update Frequency: Daily at 2 AM
Owner: Customer Analytics Team
```

### Column Documentation
```
Column: customer_segment
Description: Customer segmentation based on lifetime value and recency
Values: Platinum, Gold, Silver, Bronze
Business Rule: Recalculated monthly based on RFM analysis
Source: Derived in ETL from transaction history
```

---

## Naming Convention Checklist

### Tables
- [ ] Consistent prefix (DIM_, FACT_, etc.)?
- [ ] Descriptive business name?
- [ ] Singular vs plural consistent with standard?
- [ ] No reserved words?
- [ ] No cryptic abbreviations?

### Columns
- [ ] Primary key ends with _key?
- [ ] Foreign keys match target table's PK name?
- [ ] Natural keys end with _id, _number, or _code?
- [ ] Flags use is_ prefix or _flag suffix?
- [ ] Dates use _date, _time, or _timestamp suffix?
- [ ] Amounts use _amount suffix?
- [ ] Counts use _count suffix?

### General
- [ ] Consistent case convention (snake_case recommended)?
- [ ] Business-friendly terms?
- [ ] Self-documenting names?
- [ ] Unambiguous meanings?
- [ ] Documented in data dictionary?

---

## Quick Reference

| Object Type | Pattern | Example |
|-------------|---------|---------|
| Dimension | DIM_<entity> | DIM_CUSTOMER |
| Fact | FACT_<process> | FACT_SALES |
| Bridge | BRIDGE_<entities> | BRIDGE_ACCOUNT_CUSTOMER |
| Hub | HUB_<entity> | HUB_CUSTOMER |
| Link | LINK_<entities> | LINK_CUSTOMER_ACCOUNT |
| Satellite | SAT_<hub> | SAT_CUSTOMER |
| Staging | STG_<source>_<entity> | STG_CRM_CUSTOMER |
| Reference | REF_<category> | REF_COUNTRY |
| PK | <table>_key | customer_key |
| FK | <dimension>_key | customer_key |
| Natural Key | <entity>_id | customer_id |
| Date | <event>_date | order_date |
| Timestamp | <event>_timestamp | order_timestamp |
| Date Key | <event>_date_key | order_date_key |
| Amount | <measure>_amount | sales_amount |
| Count | <measure>_count | transaction_count |
| Flag | is_<condition> | is_active |
| Audit | created_date, modified_date | created_date |
