# Grain Declaration Patterns Reference

## Overview

The grain of a fact table is the most fundamental design decision in dimensional modeling. The grain defines what a single row in the fact table represents. All facts and all dimension foreign keys must be consistent with the declared grain.

**Kimball's Principle**: "The grain must be declared before the design can proceed."

---

## Why Grain Matters

### Consequences of Grain Declaration

1. **Determines Detail Level**: How much detail is captured
2. **Affects Storage**: Lower grain = more rows
3. **Enables Flexibility**: Atomic grain supports any aggregation
4. **Guides Dimension Selection**: Dimensions must make sense at the grain
5. **Defines Fact Selection**: Facts must be measurable at the grain
6. **Impacts Performance**: More atomic = more rows but more flexible

---

## Grain Statement Template

### Format
"One row per [business entity] per [time period/event]"

### Examples
- "One row per sales transaction line item"
- "One row per account per day"
- "One row per order (updated as order progresses)"
- "One row per student-course enrollment per semester"

---

## Atomic Grain Pattern

### Definition
The lowest level of detail captured by the source system. Cannot be subdivided further.

### Characteristics
- Most detailed possible
- Most flexible for unforeseen queries
- Largest row counts
- Best practice default

### Example: Retail Sales
```
Grain: "One row per product per sales transaction line item"

FACT_SALES_TRANSACTION
- sales_transaction_key (PK)
- date_key (transaction date)
- time_key (transaction time)
- store_key
- product_key
- customer_key
- cashier_key
- register_key
- promotion_key
- transaction_number (degenerate dimension)
- line_number (degenerate dimension)
- quantity DECIMAL(10,2)
- unit_price DECIMAL(10,2)
- extended_price DECIMAL(12,2)
- discount_amount DECIMAL(10,2)
- tax_amount DECIMAL(10,2)
```

### Grain Validation Questions
1. **Can this be subdivided?** No - this is the line item level
2. **Do all facts make sense?** Yes - quantity, price, etc. are all line-item level
3. **Do all dimensions make sense?** Yes - each dimension applies to a line item
4. **Are there mixed grains?** No - everything is line-item level

### Benefits
- Supports any aggregation (daily, monthly, yearly, by any dimension)
- Answers unforeseen questions
- Single version of truth
- Future-proof

### Trade-offs
- Largest storage requirements
- Most rows to process
- May need aggregate tables for performance

---

## Aggregated Grain Pattern

### Definition
Pre-aggregated to a higher level than atomic. Summarizes detail for performance.

### When to Use
- Performance optimization (supplement atomic, not replace)
- Known query patterns
- Storage constraints (historical systems)
- Report-specific requirements

### Example: Daily Sales by Product
```
Grain: "One row per product per day per store"

FACT_SALES_DAILY
- sales_daily_key (PK)
- date_key
- store_key
- product_key
- transaction_count INTEGER
- total_quantity DECIMAL(12,2)
- total_sales_amount DECIMAL(15,2)
- total_cost_amount DECIMAL(15,2)
- total_profit_amount DECIMAL(15,2)
- average_unit_price DECIMAL(10,2)
- unique_customer_count INTEGER
```

### Grain Validation
1. **Can this be subdivided?** Yes - back to transaction level
2. **Is atomic grain also available?** Should be (aggregates supplement, not replace)
3. **Which queries does this optimize?** Daily sales trends, product performance
4. **Can this be recreated from atomic?** Yes - always derivable

### Best Practices
- Always maintain atomic grain
- Aggregates derived from atomic
- Document what queries each aggregate serves
- Name tables to indicate grain: FACT_SALES_DAILY, FACT_SALES_MONTHLY

---

## Time-Based Grain Patterns

### Transaction Grain (Event-Level)
```
Grain: "One row per [event]"

Examples:
- One row per ATM withdrawal
- One row per web page click
- One row per phone call
- One row per manufacturing defect
```

**Characteristics**:
- Unpredictable row counts (driven by events)
- Irregular timing
- Sparse (not all dimension combinations)
- Fine-grained time dimension (date + time)

**Example**:
```sql
FACT_WEBSITE_CLICKSTREAM
- clickstream_key
- date_key
- time_key (second-level precision)
- session_key
- page_key
- visitor_key
- referrer_key
- click_timestamp TIMESTAMP
- page_load_time_ms INTEGER
- scroll_depth_percentage INTEGER
```

---

### Periodic Snapshot Grain
```
Grain: "One row per [entity] per [regular time period]"

Examples:
- One row per account per day
- One row per product per week
- One row per warehouse location per month
```

**Characteristics**:
- Predictable row counts
- Regular intervals (daily, weekly, monthly)
- Dense (rows exist for all periods)
- Semi-additive measures (balances)

**Example**:
```sql
FACT_INVENTORY_DAILY
- inventory_daily_key
- date_key (every day)
- product_key (every product)
- warehouse_key (every warehouse)
- beginning_quantity INTEGER
- ending_quantity INTEGER
- units_received INTEGER
- units_shipped INTEGER
- units_adjusted INTEGER
- average_quantity DECIMAL(10,2)
```

**Grain Statement**: "One row per product per warehouse per day"

**Validation**:
- Does every product × warehouse × day combination have a row? Should (dense)
- Are quantities measurable at this grain? Yes
- Can we aggregate to weekly or monthly? Yes

---

### Accumulating Snapshot Grain
```
Grain: "One row per [process instance]"

Examples:
- One row per order (updated as order progresses)
- One row per insurance claim
- One row per student enrollment
- One row per loan application
```

**Characteristics**:
- One row per business process instance
- Rows updated as process progresses
- Multiple date foreign keys (milestones)
- Relatively small row counts
- Tracks lag between milestones

**Example**:
```sql
FACT_ORDER_FULFILLMENT
- order_fulfillment_key
- order_date_key (milestone 1)
- payment_date_key (milestone 2)
- fulfillment_date_key (milestone 3)
- ship_date_key (milestone 4)
- delivery_date_key (milestone 5)
- customer_key
- product_key
- order_number (degenerate)
- order_amount DECIMAL(12,2)
- days_to_ship INTEGER (lag calculation)
- days_to_deliver INTEGER (lag calculation)
- current_status VARCHAR(20)
```

**Grain Statement**: "One row per order, updated as order moves through fulfillment process"

**Unique Aspect**: Rows are UPDATED (exception to insert-only rule)

---

## Multi-Dimensional Grain Patterns

### Product × Customer × Time
```
Grain: "One row per customer per product per month"

FACT_CUSTOMER_PRODUCT_MONTHLY
- customer_product_month_key
- month_key
- customer_key
- product_key
- purchase_count INTEGER
- total_quantity DECIMAL(12,2)
- total_amount DECIMAL(15,2)
- first_purchase_date_key
- last_purchase_date_key
```

**Use Case**: Customer product affinity analysis, RFM segmentation

---

### Geography × Time
```
Grain: "One row per store per day"

FACT_STORE_TRAFFIC_DAILY
- store_traffic_daily_key
- date_key
- store_key
- visitor_count INTEGER
- transaction_count INTEGER
- average_transaction_value DECIMAL(10,2)
- conversion_rate DECIMAL(5,4)
```

**Use Case**: Store performance, traffic patterns

---

## Grain Consistency Rules

### Rule 1: All Facts Must Match Grain

**Correct**:
```sql
-- Grain: One row per sales transaction line item
FACT_SALES_TRANSACTION
- quantity (line item level ✓)
- line_amount (line item level ✓)
- unit_price (line item level ✓)
```

**Incorrect**:
```sql
-- Grain: One row per sales transaction line item
FACT_SALES_TRANSACTION
- quantity (line item level ✓)
- line_amount (line item level ✓)
- order_total (ORDER level ✗) -- WRONG GRAIN!
- customer_lifetime_value (CUSTOMER level ✗) -- WRONG GRAIN!
```

**Solution**: Create separate fact tables
```sql
-- Line item grain
FACT_SALES_LINE_ITEM
- quantity
- line_amount

-- Order grain
FACT_SALES_ORDER
- order_total
- order_item_count

-- Customer grain
FACT_CUSTOMER_METRICS
- customer_lifetime_value
- customer_order_count
```

---

### Rule 2: All Dimensions Must Match Grain

**Correct**:
```sql
-- Grain: One row per product per day
FACT_INVENTORY_DAILY
- date_key ✓
- product_key ✓
- warehouse_key ✓
```

**Incorrect**:
```sql
-- Grain: One row per product per day
FACT_INVENTORY_DAILY
- date_key ✓
- product_key ✓
- warehouse_key ✓
- employee_key ✗  -- Which employee? Not meaningful at daily product grain
```

**Question to Ask**: "Does this dimension make sense at this grain?"

---

### Rule 3: Grain Determines Dimensionality

**Example: Customer Orders**

**Option 1 - Order Header Grain**:
```
Grain: "One row per order"
Dimensions: customer, order_date, shipping_address
Cannot include: product (orders have multiple products)
```

**Option 2 - Order Line Grain**:
```
Grain: "One row per order line item"
Dimensions: customer, order_date, product, shipping_address
Can include: product (each line has one product)
```

**Option 3 - Both** (common solution):
```
FACT_ORDER_HEADER (order grain)
- order-level facts and dimensions

FACT_ORDER_LINE (line item grain)
- line-level facts and dimensions
```

---

## Grain Declaration Process

### Step 1: Identify Business Process
"What business process are we measuring?"
- Sales transactions
- Customer interactions
- Inventory movements
- Financial payments

### Step 2: Determine Atomic Level
"What is the lowest level of detail available?"
- Individual line item
- Individual event
- Daily snapshot
- Individual process instance

### Step 3: Declare Grain Explicitly
"One row represents..."
- One sales transaction line item
- One account per day
- One order (lifecycle)

### Step 4: Validate Against Four Questions

1. **What does one row represent?**
   - Clear, unambiguous statement

2. **Can it be subdivided?**
   - If yes, consider more atomic grain
   - If no, this is atomic

3. **Do all facts make sense at this grain?**
   - Every measure must be meaningful and measurable

4. **Do all dimensions make sense at this grain?**
   - Every dimension must have exactly one value per row

### Step 5: Document Grain
Include in:
- Data model documentation
- Table definitions
- ETL specifications
- Business glossary

---

## Common Grain Mistakes

### Mistake 1: Implicit Grain
❌ "This is a sales fact table"
✓ "One row per sales transaction line item"

### Mistake 2: Mixed Grain
❌ Storing both line-level and order-level facts in same table

### Mistake 3: Changing Grain
❌ Starting with daily grain, later adding transaction detail to same table

### Mistake 4: Grain Too Coarse
❌ Monthly summary when daily or transaction detail is available
(Cannot drill down or answer detailed questions)

### Mistake 5: Grain Too Fine
❌ Real-time millisecond grain when second or minute grain sufficient
(Unnecessary storage and complexity)

---

## Grain Examples by Industry

### Retail
- **Transaction**: One row per product per transaction line item
- **Daily Store**: One row per store per day
- **Monthly Customer**: One row per customer per month

### Banking
- **Transaction**: One row per account transaction
- **Daily Balance**: One row per account per day
- **Monthly Statement**: One row per account per month

### Telecommunications
- **Call Detail**: One row per phone call
- **Daily Usage**: One row per customer per day
- **Monthly Billing**: One row per customer per month

### Healthcare
- **Encounter**: One row per patient visit
- **Procedure**: One row per procedure performed
- **Daily Census**: One row per facility per day

### Manufacturing
- **Production**: One row per production run
- **Defect**: One row per defect occurrence
- **Daily Output**: One row per production line per day

### Web Analytics
- **Clickstream**: One row per page view
- **Session**: One row per user session
- **Daily Visitor**: One row per visitor per day

---

## Grain Documentation Template

### Template
```
Fact Table: FACT_[NAME]
Grain: One row per [entity] per [time/event]

Grain Validation:
- Can this be subdivided? [Yes/No]
- Atomic level? [Yes/No]
- All facts measurable at this grain? [Yes/No]
- All dimensions meaningful at this grain? [Yes/No]

Row Count Estimate: [Number] rows per [time period]
Expected Growth: [Rate]

Facts (all must match grain):
- [fact_name]: [description]
- [fact_name]: [description]

Dimensions (all must match grain):
- [dimension_name]: [description]
- [dimension_name]: [description]

Related Fact Tables (different grains):
- [related_fact]: [grain]

Example Row:
[Concrete example of what one row represents]
```

### Example Documentation
```
Fact Table: FACT_SALES_TRANSACTION
Grain: One row per product per sales transaction line item

Grain Validation:
- Can this be subdivided? No - this is the atomic level
- Atomic level? Yes
- All facts measurable at this grain? Yes
- All dimensions meaningful at this grain? Yes

Row Count Estimate: 1,000,000 rows per day (average)
Expected Growth: 10% year-over-year

Facts (all must match grain):
- quantity: Number of units purchased in this line item
- unit_price: Price per unit for this line item
- extended_price: quantity × unit_price
- discount_amount: Discount applied to this line item
- tax_amount: Tax for this line item

Dimensions (all must match grain):
- date: Date of transaction
- time: Time of transaction
- store: Store where transaction occurred
- product: Product sold in this line item
- customer: Customer who made purchase
- cashier: Employee who processed transaction
- promotion: Promotion applied to this line item

Related Fact Tables (different grains):
- FACT_SALES_DAILY: One row per product per store per day
- FACT_SALES_MONTHLY: One row per product per month

Example Row:
"Customer C12345 purchased 2 units of Product P789 at Store S456
on 2024-06-15 at 14:35:22 for $19.99 each (total $39.98)"
```

---

## Best Practices

1. **Always declare grain explicitly** before designing the fact table
2. **Default to atomic grain** unless there's a compelling reason not to
3. **One grain per fact table** - never mix grains
4. **Document grain clearly** in all specifications
5. **Validate all facts and dimensions** against the grain
6. **Create aggregate tables separately** for performance
7. **Test grain with concrete examples** - "what does one row represent?"
8. **Consider future requirements** - atomic grain is more flexible
9. **Review grain with business users** - ensure they understand
10. **Maintain grain consistently** - never change grain of existing table

## Grain Decision Matrix

| Consideration | Atomic Grain | Aggregated Grain |
|---------------|--------------|------------------|
| Flexibility | Highest | Limited |
| Storage | Highest | Lower |
| Query Performance | May need optimization | Faster |
| Future-Proofing | Best | Limited |
| Detail Available | Maximum | Summary only |
| ETL Complexity | Simpler | More complex |
| Default Choice | ✓ Recommended | Special cases only |
