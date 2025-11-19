# Dimensional Modeling Patterns Reference

## Star Schema Pattern

### Definition
A star schema consists of a central fact table surrounded by dimension tables. The fact table contains foreign keys to dimension tables and numeric measures. Dimension tables are denormalized and contain descriptive attributes.

### Structure
```
           DIM_DATE
               |
               |
DIM_PRODUCT - FACT_SALES - DIM_CUSTOMER
               |
               |
           DIM_STORE
```

### Characteristics
- **Fact Table**: Narrow and deep (many rows, fewer columns)
- **Dimension Tables**: Wide and shallow (fewer rows, many columns)
- **Denormalized**: Dimensions contain hierarchies in single tables
- **Surrogate Keys**: Technical keys for joins
- **Natural Keys**: Business keys preserved in dimensions

### Benefits
- Simple, intuitive structure
- Optimal query performance
- Easy for BI tools to navigate
- Predictable join patterns
- Minimal join complexity

### Use Cases
- Standard reporting and analytics
- OLAP cube sources
- Self-service BI
- Performance-critical applications

---

## Snowflake Schema Pattern

### Definition
A snowflake schema normalizes dimension tables into multiple related tables, creating a snowflake-like structure around the fact table.

### Structure
```
DIM_PRODUCT_CATEGORY
        |
DIM_PRODUCT_SUBCATEGORY
        |
    DIM_PRODUCT - FACT_SALES - DIM_CUSTOMER - DIM_CUSTOMER_SEGMENT
```

### Characteristics
- Normalized dimension tables
- Reduced data redundancy
- More complex join paths
- Smaller dimension table sizes
- Hierarchies in separate tables

### Benefits
- Reduced storage for large dimensions
- Easier maintenance of hierarchies
- Clear hierarchy structure
- Reusable dimension components

### Drawbacks
- Increased query complexity
- More joins required
- Slower query performance
- Harder for business users to understand
- More complex ETL

### Use Cases
- Large dimensions with significant redundancy
- Dimensions with frequently changing hierarchies
- Storage-constrained environments
- Data that naturally separates into components

---

## Constellation Schema Pattern (Galaxy Schema)

### Definition
Multiple fact tables sharing dimension tables in a unified dimensional model. Represents an enterprise dimensional warehouse.

### Structure
```
                DIM_DATE
                /      \
               /        \
        FACT_SALES    FACT_INVENTORY
           |  \        /  |
           |   \      /   |
    DIM_PRODUCT  DIM_STORE
```

### Characteristics
- Multiple fact tables (different business processes)
- Shared conformed dimensions
- Consistent dimension definitions
- Enterprise data warehouse structure
- Drill-across capability

### Benefits
- Enterprise-wide consistency
- Shared dimension management
- Cross-process analysis
- Single version of truth
- Reduced dimension redundancy

### Implementation
- Conformed dimensions managed centrally
- Bus matrix defines conformity
- Consistent grain across uses
- Synchronized dimension updates

### Use Cases
- Enterprise data warehouses
- Cross-functional analytics
- Integrated business intelligence
- Multi-process reporting

---

## Fact Constellation Patterns

### Transaction Fact Pattern
**Grain**: One row per transaction event
**Example**: Sales transactions, web clicks, ATM withdrawals

```
FACT_SALES_TRANSACTION
- sales_key (PK)
- date_key (FK)
- product_key (FK)
- customer_key (FK)
- store_key (FK)
- transaction_number (DD - degenerate dimension)
- quantity
- unit_price
- discount_amount
- extended_amount
- tax_amount
```

**Characteristics**:
- Highest granularity
- Large row counts
- Sparse (not all dimension combinations exist)
- Additive measures
- Time-stamped events

---

### Periodic Snapshot Fact Pattern
**Grain**: One row per period (day, week, month)
**Example**: Daily account balances, monthly inventory levels

```
FACT_ACCOUNT_BALANCE_DAILY
- balance_key (PK)
- date_key (FK)
- account_key (FK)
- branch_key (FK)
- beginning_balance
- ending_balance
- average_daily_balance
- transaction_count
```

**Characteristics**:
- Regular time intervals
- Dense (rows exist for all periods)
- Semi-additive measures (balances)
- Snapshot of state at point in time
- Predictable row growth

---

### Accumulating Snapshot Fact Pattern
**Grain**: One row per process instance (updated as process progresses)
**Example**: Order fulfillment, claim processing, student enrollment

```
FACT_ORDER_FULFILLMENT
- order_key (PK)
- order_date_key (FK)
- payment_date_key (FK)
- ship_date_key (FK)
- delivery_date_key (FK)
- customer_key (FK)
- product_key (FK)
- order_number (DD)
- days_to_payment
- days_to_ship
- days_to_deliver
- order_amount
- ship_cost
```

**Characteristics**:
- Multiple date foreign keys (milestones)
- Rows are updated (not just inserted)
- Lag measures (days between milestones)
- Semi-additive measures
- Relatively small row counts

---

### Factless Fact Pattern
**Grain**: One row per event with no numeric measures
**Example**: Student course attendance, promotion coverage, eligibility

**Type 1: Event Tracking**
```
FACT_STUDENT_ATTENDANCE
- attendance_key (PK)
- date_key (FK)
- student_key (FK)
- course_key (FK)
- instructor_key (FK)
- classroom_key (FK)
```

**Type 2: Coverage/Eligibility**
```
FACT_PROMOTION_COVERAGE
- coverage_key (PK)
- promotion_key (FK)
- product_key (FK)
- store_key (FK)
- start_date_key (FK)
- end_date_key (FK)
```

**Characteristics**:
- No numeric facts (or dummy fact like "1")
- Captures events or relationships
- Count queries (COUNT(*))
- Often used for conditions or eligibility

---

## Dimension Patterns

### Conformed Dimension Pattern
Dimensions shared across multiple fact tables with identical structure, content, and meaning.

**Example**: DIM_DATE used by all fact tables
```
DIM_DATE (shared across enterprise)
- date_key (PK)
- calendar_date
- day_of_week
- month_name
- quarter_name
- fiscal_year
- is_holiday
- is_weekday
```

**Requirements**:
- Identical attribute names and meanings
- Synchronized values across all uses
- Managed by single authoritative source
- Same grain and granularity
- Consistent business definitions

---

### Role-Playing Dimension Pattern
A single dimension table used multiple times in a fact table with different meanings.

**Example**: DIM_DATE as Order Date, Ship Date, Delivery Date
```
FACT_SALES
- order_date_key (FK to DIM_DATE)
- ship_date_key (FK to DIM_DATE)
- delivery_date_key (FK to DIM_DATE)
```

**Implementation**:
- Database views with role-specific names
- BI tool aliases for clarity
- Single physical dimension table
- Multiple logical dimension views

---

### Junk Dimension Pattern
Consolidation of low-cardinality flags and indicators into a single dimension.

**Instead of**: Multiple flag columns in fact table
**Use**: Single foreign key to junk dimension

```
DIM_TRANSACTION_INDICATORS
- indicator_key (PK)
- payment_type_code
- payment_type_desc
- shipping_method_code
- shipping_method_desc
- gift_wrap_flag
- express_flag
- international_flag
```

**Benefits**:
- Reduces fact table width
- Eliminates nulls in fact table
- Groups related indicators
- Pre-generates all combinations or adds as encountered

---

### Mini-Dimension Pattern
Rapidly changing attributes separated from main dimension to avoid dimension growth.

**Example**: Customer demographics that change frequently
```
DIM_CUSTOMER (stable attributes)
- customer_key (PK)
- customer_id
- customer_name
- signup_date

DIM_CUSTOMER_DEMOGRAPHICS (rapidly changing)
- demographics_key (PK)
- age_range
- income_band
- credit_score_band
- household_size_range

FACT_SALES
- customer_key (FK)
- demographics_key (FK)
```

**Use Cases**:
- Rapidly changing attributes (demographics, scores)
- Large dimensions with frequent updates
- Avoiding SCD Type 2 explosion

---

### Outrigger Dimension Pattern
Normalized attribute from dimension into separate table (controlled snowflaking).

**Example**: State/Country information from Customer dimension
```
DIM_CUSTOMER
- customer_key (PK)
- customer_name
- address
- city
- state_key (FK to DIM_STATE)

DIM_STATE (outrigger)
- state_key (PK)
- state_code
- state_name
- region
- country_key (FK to DIM_COUNTRY)
```

**Use Cases**:
- Attributes with own natural hierarchy
- Frequently changing reference data
- Reusable across multiple dimensions
- Large, stable reference datasets

---

## Bridge Table Patterns

### Multivalued Dimension Bridge
Handles many-to-many relationships between facts and dimensions.

**Example**: Account with multiple customers
```
DIM_CUSTOMER
- customer_key (PK)

BRIDGE_ACCOUNT_CUSTOMER
- account_key (FK)
- customer_key (FK)
- allocation_percentage
- primary_customer_flag
- weighting_factor

FACT_ACCOUNT_BALANCE
- account_key (FK)
```

**Weighting Factor**: Prevents double-counting
- If 2 customers on account: weighting_factor = 0.5
- If 3 customers: weighting_factor = 0.333

---

### Ragged Hierarchy Bridge
Handles variable-depth hierarchies.

**Example**: Organizational hierarchy with varying levels
```
DIM_EMPLOYEE
- employee_key (PK)
- employee_name

BRIDGE_EMPLOYEE_HIERARCHY
- employee_key (FK)
- manager_key (FK)
- hierarchy_level
- top_flag
- bottom_flag
```

---

## Grain Patterns

### Atomic Grain
Lowest level of detail available from source systems.

**Benefits**:
- Maximum flexibility for queries
- Supports unforeseen aggregations
- Single version of truth
- Future-proof design

**Example**: Individual line items rather than order totals

---

### Multiple Grains (Anti-Pattern)
Different grain levels in same fact table.

**Problem**: Mixing line-item and order-level facts
```
❌ FACT_SALES (WRONG - MIXED GRAIN)
- line_item_amount
- order_total_amount (different grain!)
```

**Solution**: Separate fact tables
```
✓ FACT_SALES_LINE_ITEM (line grain)
✓ FACT_SALES_ORDER (order grain)
```

---

## Best Practices

1. **Start with Star Schema**: Default pattern for most use cases
2. **Use Surrogate Keys**: Always use surrogate keys for dimensions
3. **Denormalize Dimensions**: Keep dimensions flat (star) unless compelling reason
4. **Atomic Grain**: Build fact tables at most atomic grain possible
5. **Conformed Dimensions**: Share dimensions across fact tables
6. **Role-Playing**: Reuse dimensions with different roles
7. **Junk Dimensions**: Consolidate flags and indicators
8. **Bridge Tables**: Handle many-to-many relationships properly
9. **Consistent Naming**: Follow naming conventions across all tables
10. **Document Grain**: Explicitly state and maintain fact table grain

## Quick Reference

| Pattern | Use When | Avoid When |
|---------|----------|------------|
| Star Schema | Standard reporting, performance critical | None (default pattern) |
| Snowflake | Large dimensions, storage constraints | Performance is priority |
| Constellation | Enterprise warehouse, multiple processes | Single business process |
| Transaction Fact | Event-level detail needed | Only summaries required |
| Periodic Snapshot | Regular interval reporting | Event-level analysis needed |
| Accumulating Snapshot | Process/pipeline tracking | Simple event tracking |
| Factless Fact | Event occurrence, eligibility | Numeric measurements exist |
| Junk Dimension | Many low-cardinality flags | High-cardinality attributes |
| Mini-Dimension | Rapidly changing attributes | Stable dimensions |
| Bridge Table | Many-to-many relationships | Simple one-to-many |
