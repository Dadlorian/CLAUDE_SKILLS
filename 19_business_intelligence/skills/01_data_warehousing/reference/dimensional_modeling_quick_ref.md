# Dimensional Modeling Quick Reference

Fast lookup guide for dimensional modeling concepts, patterns, and best practices following Kimball methodology.

## Core Concepts

### Fact Tables
**Purpose**: Store measurements, metrics, and foreign keys to dimensions

**Characteristics**:
- Grain: Level of detail (e.g., one row per order line item)
- Measures/Facts: Numeric, additive values
- Foreign Keys: References to dimension tables
- Typically 80-90% of data warehouse data volume

**Types**:
1. **Transaction Facts**: One row per business event
2. **Periodic Snapshot Facts**: One row per time period
3. **Accumulating Snapshot Facts**: One row per process lifecycle

### Dimension Tables
**Purpose**: Provide descriptive context for facts

**Characteristics**:
- Denormalized, wide tables
- Textual descriptions and attributes
- Relatively small compared to facts
- Slowly changing over time

**Types**:
1. **Conformed Dimensions**: Shared across fact tables
2. **Role-Playing Dimensions**: Same dimension used multiple ways
3. **Junk Dimensions**: Collection of miscellaneous flags
4. **Degenerate Dimensions**: Dimension key in fact table (no dimension table)

## Schema Patterns

### Star Schema
```
         [Date Dim]
              |
         [Product Dim] --- [Sales Fact] --- [Customer Dim]
              |                |
         [Store Dim]      [Promotion Dim]
```

**Characteristics**:
- Fact table in center
- Dimension tables radiate outward
- Dimension tables denormalized
- Simple, fast queries
- Most common pattern

**Benefits**:
- Easy to understand
- Fast query performance
- Simple to navigate
- Optimal for BI tools

### Snowflake Schema
```
         [Date Dim]
              |
    [Product Dim] --- [Category Dim]
         |
    [Sales Fact] --- [Customer Dim] --- [City Dim] --- [Country Dim]
         |
    [Store Dim]
```

**Characteristics**:
- Normalized dimension tables
- Reduces data redundancy
- More complex queries
- More tables to join

**When to Use**:
- Storage optimization critical (rare in modern warehouses)
- Dimension update patterns favor normalization
- Complex hierarchies need separate tables

### Constellation Schema (Galaxy Schema)
```
[Date Dim] ---+--- [Sales Fact]
              |
[Product Dim]-+--- [Inventory Fact]
              |
[Store Dim] --+--- [Promotion Fact]
```

**Characteristics**:
- Multiple fact tables
- Shared dimensions (conformed)
- Enterprise-scale data warehouse
- Most complex pattern

**Benefits**:
- Supports multiple business processes
- Conformed dimensions enable cross-process analysis
- Scalable architecture

## Fact Table Types

### Transaction Facts

**Grain**: One row per transaction event

```sql
CREATE TABLE sales_transaction_fact (
    -- Keys
    date_key INTEGER,
    product_key INTEGER,
    customer_key INTEGER,
    store_key INTEGER,

    -- Degenerate dimensions
    order_number VARCHAR(20),
    line_number INTEGER,

    -- Facts
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    cost_amount DECIMAL(10,2)
);
```

**Characteristics**:
- Captures individual events
- Sparse (not all dimension combinations exist)
- Additive facts
- Most detailed grain

**Examples**:
- Sales transactions
- Website clickstreams
- ATM withdrawals
- Phone calls

### Periodic Snapshot Facts

**Grain**: One row per time period (e.g., daily, monthly)

```sql
CREATE TABLE account_monthly_snapshot_fact (
    -- Keys
    month_key INTEGER,
    account_key INTEGER,
    customer_key INTEGER,
    product_key INTEGER,

    -- Facts (semi-additive across time)
    beginning_balance DECIMAL(15,2),
    ending_balance DECIMAL(15,2),
    average_balance DECIMAL(15,2),

    -- Facts (additive)
    total_deposits DECIMAL(15,2),
    total_withdrawals DECIMAL(15,2),
    transaction_count INTEGER
);
```

**Characteristics**:
- Regular time intervals
- Dense (row for each entity/period)
- Mix of additive and semi-additive facts
- Supports trend analysis

**Examples**:
- Monthly account balances
- Daily inventory levels
- Weekly sales forecasts
- Quarterly financial statements

### Accumulating Snapshot Facts

**Grain**: One row per process instance (updated as process progresses)

```sql
CREATE TABLE order_fulfillment_fact (
    -- Keys
    order_key INTEGER,
    customer_key INTEGER,
    product_key INTEGER,

    -- Multiple date dimensions (milestones)
    order_date_key INTEGER,
    payment_date_key INTEGER,
    shipment_date_key INTEGER,
    delivery_date_key INTEGER,

    -- Lag facts (days between milestones)
    days_to_payment INTEGER,
    days_to_shipment INTEGER,
    days_to_delivery INTEGER,

    -- Standard facts
    order_amount DECIMAL(10,2),
    shipping_cost DECIMAL(10,2)
);
```

**Characteristics**:
- One row per process lifecycle
- Multiple date dimensions (milestones)
- Rows updated as process progresses
- Lag calculations between milestones

**Examples**:
- Order fulfillment pipeline
- Student enrollment lifecycle
- Insurance claim processing
- Loan origination to closing

## Dimension Patterns

### Conformed Dimensions

**Definition**: Dimension shared across multiple fact tables with identical meaning

```sql
-- Shared date dimension
CREATE TABLE date_dim (
    date_key INTEGER PRIMARY KEY,
    date DATE,
    day_of_week VARCHAR(10),
    day_of_month INTEGER,
    month_name VARCHAR(10),
    quarter INTEGER,
    year INTEGER,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);

-- Used by multiple facts
-- sales_fact.date_key -> date_dim.date_key
-- inventory_fact.date_key -> date_dim.date_key
-- returns_fact.date_key -> date_dim.date_key
```

**Benefits**:
- Consistency across business processes
- Enables drill-across queries
- Single dimension maintenance
- Master data management

### Role-Playing Dimensions

**Definition**: Same dimension used multiple times with different roles

```sql
-- Single date dimension
CREATE TABLE date_dim (...);

-- Fact table with multiple date roles
CREATE TABLE orders_fact (
    order_date_key INTEGER,      -- Role: Order Date
    payment_date_key INTEGER,    -- Role: Payment Date
    ship_date_key INTEGER,       -- Role: Ship Date
    delivery_date_key INTEGER,   -- Role: Delivery Date

    -- All reference same date_dim
    FOREIGN KEY (order_date_key) REFERENCES date_dim(date_key),
    FOREIGN KEY (payment_date_key) REFERENCES date_dim(date_key),
    FOREIGN KEY (ship_date_key) REFERENCES date_dim(date_key),
    FOREIGN KEY (delivery_date_key) REFERENCES date_dim(date_key)
);
```

**Common Examples**:
- Date (order date, ship date, delivery date)
- Location (ship from, ship to)
- Employee (sales rep, account manager)

### Junk Dimensions

**Definition**: Collection of miscellaneous flags and indicators

```sql
CREATE TABLE order_flags_dim (
    flags_key INTEGER PRIMARY KEY,

    -- Indicator flags
    is_express_shipping BOOLEAN,
    is_gift_wrapped BOOLEAN,
    is_international BOOLEAN,
    requires_signature BOOLEAN,
    is_insured BOOLEAN,
    payment_method VARCHAR(20),
    order_source VARCHAR(20)
);

-- Fact table
CREATE TABLE orders_fact (
    order_key INTEGER,
    date_key INTEGER,
    customer_key INTEGER,
    order_flags_key INTEGER,  -- Reference to junk dimension

    order_amount DECIMAL(10,2)
);
```

**When to Use**:
- Many low-cardinality attributes
- Flags/indicators that don't fit other dimensions
- Avoid proliferation of foreign keys in fact

**Benefits**:
- Reduces fact table width
- Groups related indicators
- Easier to query combinations

### Degenerate Dimensions

**Definition**: Dimension key stored in fact table without corresponding dimension table

```sql
CREATE TABLE sales_fact (
    date_key INTEGER,
    product_key INTEGER,
    customer_key INTEGER,

    -- Degenerate dimensions (no dimension table)
    order_number VARCHAR(20),
    line_item_number INTEGER,
    invoice_number VARCHAR(20),

    quantity INTEGER,
    amount DECIMAL(10,2)
);
```

**Characteristics**:
- Operational IDs (order number, invoice number)
- No descriptive attributes
- Used for drill-back to source system
- Common in transaction fact tables

### Bridge Tables (Multi-Valued Dimensions)

**Definition**: Handles many-to-many relationships

```sql
-- Customer dimension
CREATE TABLE customer_dim (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR(20),
    customer_name VARCHAR(100)
);

-- Product category dimension
CREATE TABLE category_dim (
    category_key INTEGER PRIMARY KEY,
    category_name VARCHAR(50)
);

-- Bridge table (customer can have multiple interests)
CREATE TABLE customer_category_bridge (
    customer_key INTEGER,
    category_key INTEGER,
    weighting_factor DECIMAL(5,4),  -- Allocate facts proportionally
    PRIMARY KEY (customer_key, category_key)
);

-- Fact table
CREATE TABLE sales_fact (
    date_key INTEGER,
    product_key INTEGER,
    customer_key INTEGER,  -- Join through bridge to categories
    amount DECIMAL(10,2)
);
```

**Use Cases**:
- Customer interests/preferences
- Product categories (multiple per product)
- Employee skills
- Doctor diagnoses per patient visit

## Slowly Changing Dimensions (SCD)

### Type 0: Retain Original

**Strategy**: Never change, retain original value

```sql
CREATE TABLE customer_dim (
    customer_key INTEGER,
    customer_id VARCHAR(20),
    original_credit_score INTEGER,  -- Never changes
    ...
);
```

**Use When**: Historical value must never change

### Type 1: Overwrite

**Strategy**: Overwrite with new value, no history

```sql
-- Before update
customer_key | customer_id | email
1           | C001        | old@email.com

-- After update (no history)
customer_key | customer_id | email
1           | C001        | new@email.com
```

**Use When**:
- Corrections to data errors
- No historical value needed
- Low storage priority

### Type 2: Add New Row

**Strategy**: Insert new row, preserve history

```sql
CREATE TABLE customer_dim (
    customer_key INTEGER PRIMARY KEY,      -- Surrogate key
    customer_id VARCHAR(20),               -- Natural key
    customer_name VARCHAR(100),
    address VARCHAR(200),
    city VARCHAR(50),

    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN
);

-- History example
customer_key | customer_id | city        | effective_date | end_date   | is_current
1           | C001        | New York    | 2020-01-01    | 2023-06-30 | false
2           | C001        | Los Angeles | 2023-07-01    | 9999-12-31 | true
```

**Use When**:
- Need full historical tracking
- Analyze behavior before/after changes
- Most common SCD type

### Type 3: Add New Column

**Strategy**: Add column for previous value

```sql
CREATE TABLE customer_dim (
    customer_key INTEGER,
    customer_id VARCHAR(20),
    current_city VARCHAR(50),
    previous_city VARCHAR(50),
    city_change_date DATE
);

-- Example
customer_key | customer_id | current_city | previous_city | city_change_date
1           | C001        | Los Angeles  | New York      | 2023-07-01
```

**Use When**:
- Need only previous value
- Limited history requirements
- Simple before/after analysis

### Type 6: Hybrid (1+2+3)

**Strategy**: Combine Type 1, 2, and 3 techniques

```sql
CREATE TABLE customer_dim (
    customer_key INTEGER,
    customer_id VARCHAR(20),

    -- Type 1: Always current
    current_email VARCHAR(100),

    -- Type 2: Full history
    address VARCHAR(200),
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN,

    -- Type 3: Previous value
    previous_address VARCHAR(200)
);
```

## Naming Conventions

### Table Names
- **Facts**: `<process>_fact` (e.g., `sales_fact`, `order_fulfillment_fact`)
- **Dimensions**: `<entity>_dim` (e.g., `customer_dim`, `product_dim`)

### Column Names
- **Surrogate Keys**: `<table>_key` (e.g., `customer_key`, `product_key`)
- **Natural Keys**: `<entity>_id` (e.g., `customer_id`, `product_id`)
- **Dates**: `<event>_date_key` or `<event>_date` (e.g., `order_date_key`)

### Special Columns
- `effective_date`, `end_date`: SCD Type 2 tracking
- `is_current`: Current row indicator
- `created_datetime`: Audit timestamp
- `updated_datetime`: Last update timestamp

## Grain Declaration

**Definition**: The most atomic level of detail captured in fact table

### Grain Examples

**Sales Fact**:
- One row per individual product sold on a transaction
- Grain: Transaction line item

**Website Clickstream Fact**:
- One row per page view
- Grain: Page view event

**Account Snapshot Fact**:
- One row per account per day
- Grain: Account-day

**Grain Rules**:
1. Declare grain before designing fact table
2. All facts must conform to same grain
3. Never mix grains in single fact table
4. Grain determines which dimensions are possible

## Best Practices

### Design Process (Kimball 4-Step Method)
1. **Select Business Process**: Sales, inventory, etc.
2. **Declare Grain**: Most atomic level of detail
3. **Identify Dimensions**: Who, what, where, when, why, how
4. **Identify Facts**: Numeric measurements at grain level

### Dimension Design
1. Denormalize dimensions (include descriptive attributes)
2. Use surrogate keys for all dimensions
3. Include audit columns (created_date, updated_date)
4. Implement appropriate SCD type for each attribute
5. Create conformed dimensions for enterprise consistency

### Fact Design
1. Store facts at most atomic grain possible
2. Use foreign keys to dimensions (never descriptive attributes)
3. Include all relevant dimensions
4. Use degenerate dimensions for operational IDs
5. Choose appropriate fact table type (transaction, snapshot, accumulating)

### Performance
1. Partition large fact tables (usually by date)
2. Cluster/sort on frequently filtered columns
3. Create aggregate fact tables for common summaries
4. Index dimension tables appropriately
5. Consider materialized views for complex queries

### Common Pitfalls to Avoid
1. ❌ Mixing grains in single fact table
2. ❌ Storing descriptive attributes in fact tables
3. ❌ Normalizing dimension tables (snowflaking without reason)
4. ❌ Using natural keys instead of surrogate keys
5. ❌ Not implementing SCD for changing attributes
6. ❌ Creating too many dimensions (dimension explosion)
7. ❌ Not declaring conformed dimensions
8. ❌ Storing derived values instead of calculating at query time
