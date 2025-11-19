# Star Schema Design Process Guide

## Star Schema Overview

Central fact table surrounded by denormalized dimension tables, forming a star pattern.

## Step-by-Step Design

### Step 1: Select Business Process
Identify what you're measuring (not department).

Examples:
- ✓ Sales transactions
- ✓ Order fulfillment
- ✗ Marketing department (too broad)

### Step 2: Declare Grain
"One row per..."

Example: "One row per product per sales transaction line item"

Validate:
- Can it be subdivided? (If yes, consider more atomic)
- Are all facts meaningful at this grain?
- Are all dimensions meaningful?

### Step 3: Identify Dimensions
Who, what, where, when, why, how.

Example for Sales:
- When: Date, Time
- Who: Customer, Cashier
- What: Product, Promotion
- Where: Store
- How: Payment Method

### Step 4: Identify Facts
Numeric measurements at the grain.

Example:
- quantity (additive)
- unit_price
- extended_price
- discount_amount
- tax_amount

### Step 5: Design Physical Model

**Fact Table**:
```sql
FACT_SALES
- sales_key (PK)
- date_key (FK)
- time_key (FK)
- customer_key (FK)
- product_key (FK)
- store_key (FK)
- transaction_number (degenerate)
- quantity
- amount
```

**Dimension Tables** (denormalized):
```sql
DIM_PRODUCT
- product_key (PK)
- product_id
- product_name
- subcategory
- category
- department (hierarchy levels in one table)
```

## Star Schema Characteristics

- Denormalized dimensions (not snowflaked)
- Surrogate keys
- Unknown members (key = 0)
- Fact table narrow (FKs + facts only)
- Dimensions wide (many attributes OK)

## Benefits

- Simple, intuitive structure
- Fast query performance
- Easy for BI tools
- Predictable join paths
- Business-friendly

## Common Mistakes to Avoid

- Snowflaking (normalizing dimensions)
- Mixed grains in fact
- NULL foreign keys
- Dimension attributes in fact
- Smart keys

