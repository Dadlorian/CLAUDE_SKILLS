# Kimball Dimensional Modeling Methodology Guide

Step-by-step guide to implementing Ralph Kimball's dimensional modeling methodology for data warehouse design.

## Overview

The Kimball methodology is a bottom-up approach to data warehousing that emphasizes:
- Business process focus
- Dimensional modeling (star schemas)
- Conformed dimensions
- Incremental, iterative development
- Business user accessibility

## The Kimball Four-Step Design Process

### Step 1: Select the Business Process

**Goal**: Choose a single business process to model

**How To**:

1. **Identify Candidate Business Processes**
   ```
   Common business processes:
   - Sales transactions
   - Order fulfillment
   - Customer service interactions
   - Inventory management
   - Financial accounting
   - Marketing campaigns
   - Manufacturing operations
   ```

2. **Prioritize Based on Criteria**
   ```
   Evaluation criteria:
   ✓ Business impact and value
   ✓ Data availability and quality
   ✓ Feasibility (complexity, timeline)
   ✓ Stakeholder support
   ✓ Foundation for future processes
   ```

3. **Document the Selected Process**
   ```
   Business Process: Sales Transactions

   Description: Capture every product sale transaction
   at the point of sale, including what was sold, to whom,
   when, where, by whom, and for how much.

   Business Value: Enable sales analysis by product,
   customer, time, and location. Support revenue forecasting
   and commission calculations.

   Scope: All retail and online sales transactions
   Frequency: Real-time to daily batch
   Stakeholders: Sales, Marketing, Finance teams
   ```

**Example Output**: Business Process Definition Document

---

### Step 2: Declare the Grain

**Goal**: Define the level of detail for each fact table row

**How To**:

1. **Ask the Grain Question**
   ```
   "What does a single fact table row represent?"

   Examples:
   ✓ "One row per product sold on a transaction"
   ✓ "One row per account per day"
   ✓ "One row per manufacturing job completion"
   ```

2. **Choose Grain Type**
   ```
   Transaction Grain:
   - One row per business event
   - Example: Each individual sale line item
   - Most atomic level of detail

   Periodic Snapshot Grain:
   - One row per entity per time period
   - Example: Account balance at end of each day
   - Regular time intervals

   Accumulating Snapshot Grain:
   - One row per process instance (updated over time)
   - Example: Order lifecycle from placement to delivery
   - Tracks milestones in a process
   ```

3. **Declare Grain Formally**
   ```
   Grain Statement: "One row per product line item
   on a sales transaction"

   Characteristics:
   - Most atomic level: YES
   - Matches source system: YES
   - Supports all analysis requirements: YES
   - Performance acceptable: YES
   ```

4. **Validate Grain**
   ```
   Test questions:
   ✓ Can we answer all required business questions?
   ✓ Is this the lowest level of detail available?
   ✓ Will this support future requirements?
   ✓ Can we aggregate up from this grain?
   ```

**Example Output**: Grain Definition Statement

---

### Step 3: Identify the Dimensions

**Goal**: Determine the "who, what, where, when, why, and how" context for the business process

**How To**:

1. **Brainstorm All Context Questions**
   ```
   For Sales Transaction process:

   WHEN did it happen?
   → Date, Time dimensions

   WHAT was sold?
   → Product dimension

   WHO bought it?
   → Customer dimension

   WHERE did it happen?
   → Store/Location dimension

   HOW was it sold?
   → Promotion dimension, Payment Method dimension

   WHO sold it?
   → Employee/Salesperson dimension
   ```

2. **Define Each Dimension**
   ```sql
   -- Date Dimension
   CREATE TABLE dim_date (
       date_key INTEGER PRIMARY KEY,
       date DATE,
       day_of_week VARCHAR(10),
       day_of_month INTEGER,
       day_of_year INTEGER,
       week_of_year INTEGER,
       month_name VARCHAR(10),
       month_number INTEGER,
       quarter INTEGER,
       year INTEGER,
       is_weekend BOOLEAN,
       is_holiday BOOLEAN,
       holiday_name VARCHAR(50),
       fiscal_year INTEGER,
       fiscal_quarter INTEGER,
       fiscal_month INTEGER
   );

   -- Product Dimension
   CREATE TABLE dim_product (
       product_key INTEGER PRIMARY KEY,
       product_id VARCHAR(50),          -- Natural key
       product_name VARCHAR(200),
       product_description TEXT,
       brand VARCHAR(100),
       category VARCHAR(100),
       subcategory VARCHAR(100),
       department VARCHAR(100),
       package_type VARCHAR(50),
       package_size VARCHAR(50),
       unit_of_measure VARCHAR(20),
       unit_cost DECIMAL(10,2),
       unit_price DECIMAL(10,2),
       effective_date DATE,             -- For SCD Type 2
       end_date DATE,
       is_current BOOLEAN
   );

   -- Customer Dimension
   CREATE TABLE dim_customer (
       customer_key INTEGER PRIMARY KEY,
       customer_id VARCHAR(50),
       customer_name VARCHAR(200),
       customer_type VARCHAR(50),       -- Retail, Wholesale, etc.
       email VARCHAR(200),
       phone VARCHAR(20),
       address VARCHAR(200),
       city VARCHAR(100),
       state VARCHAR(2),
       zip VARCHAR(10),
       country VARCHAR(50),
       region VARCHAR(50),
       customer_since_date DATE,
       customer_segment VARCHAR(50),     -- VIP, Regular, New
       effective_date DATE,
       end_date DATE,
       is_current BOOLEAN
   );

   -- Store Dimension
   CREATE TABLE dim_store (
       store_key INTEGER PRIMARY KEY,
       store_id VARCHAR(50),
       store_name VARCHAR(200),
       store_type VARCHAR(50),          -- Flagship, Regular, Outlet
       store_size_sqft INTEGER,
       manager_name VARCHAR(200),
       address VARCHAR(200),
       city VARCHAR(100),
       state VARCHAR(2),
       zip VARCHAR(10),
       region VARCHAR(50),
       district VARCHAR(50),
       opened_date DATE,
       effective_date DATE,
       end_date DATE,
       is_current BOOLEAN
   );
   ```

3. **Identify Dimension Attributes**
   ```
   Guidelines:
   - Include ALL descriptive text
   - Add derived attributes (age from birth_date)
   - Include hierarchies (Category → Subcategory → Product)
   - Add analytics-friendly flags (is_active, is_premium)
   - Include slowly changing attributes
   ```

4. **Plan for Slowly Changing Dimensions**
   ```
   For each dimension, categorize attributes:

   Type 1 (Overwrite): Corrections, non-historical
   - Email address corrections
   - Phone number updates

   Type 2 (Add Row): Historical tracking needed
   - Customer address changes
   - Product category changes
   - Store manager changes

   Type 0 (Never Change): Immutable attributes
   - Birth date
   - Account opening date
   - Original credit score
   ```

**Example Output**: Dimension DDL and attribute catalog

---

### Step 4: Identify the Facts

**Goal**: Determine the numeric measurements for the business process

**How To**:

1. **Identify Candidate Facts**
   ```
   Ask: "What are we measuring in this business process?"

   For Sales Transaction:
   - quantity_sold
   - unit_price
   - extended_price (quantity × unit_price)
   - discount_amount
   - discount_percent
   - tax_amount
   - shipping_amount
   - total_amount
   - cost_amount
   - profit_amount (total_amount - cost_amount)
   ```

2. **Classify Fact Types**
   ```
   Additive (can sum across all dimensions):
   ✓ quantity_sold
   ✓ extended_price
   ✓ discount_amount
   ✓ total_amount
   ✓ profit_amount

   Semi-Additive (can sum across some dimensions):
   ⚠ account_balance (additive across accounts, not time)
   ⚠ inventory_level (additive across products, not time)

   Non-Additive (cannot sum):
   ✗ unit_price
   ✗ discount_percent
   ✗ profit_margin_percent

   Note: Store non-additive facts for filtering/grouping,
   not aggregation
   ```

3. **Design the Fact Table**
   ```sql
   CREATE TABLE fct_sales (
       -- Dimension Foreign Keys
       date_key INTEGER NOT NULL,
       time_key INTEGER,
       product_key INTEGER NOT NULL,
       customer_key INTEGER NOT NULL,
       store_key INTEGER NOT NULL,
       promotion_key INTEGER,
       payment_method_key INTEGER,
       employee_key INTEGER,

       -- Degenerate Dimensions (no dimension table)
       transaction_number VARCHAR(50),
       line_number INTEGER,

       -- Facts (Measurements)
       quantity_sold DECIMAL(10,2),
       unit_price DECIMAL(10,2),
       extended_price DECIMAL(10,2),
       discount_amount DECIMAL(10,2),
       tax_amount DECIMAL(10,2),
       shipping_amount DECIMAL(10,2),
       total_amount DECIMAL(10,2),
       cost_amount DECIMAL(10,2),
       profit_amount DECIMAL(10,2),

       -- Audit columns
       etl_insert_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       etl_update_datetime TIMESTAMP,

       -- Foreign key constraints
       FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
       FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
       FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
       FOREIGN KEY (store_key) REFERENCES dim_store(store_key)
   );
   ```

4. **Consider Fact Table Types**
   ```
   Transaction Fact Table:
   - One row per transaction line item
   - Grain: Individual events
   - Use: Detailed analysis

   Periodic Snapshot Fact Table:
   - One row per period (daily/monthly)
   - Grain: Regular time intervals
   - Use: Trend analysis, forecasting

   Accumulating Snapshot Fact Table:
   - One row per process instance
   - Multiple date dimensions (milestones)
   - Rows updated as process progresses
   - Use: Pipeline analysis, cycle time
   ```

**Example Output**: Fact table DDL and fact catalog

---

## Kimball Design Best Practices

### Conformed Dimensions

**Definition**: Dimensions shared across fact tables with identical structure and content

**Implementation**:
```sql
-- Master conformed dimension
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    date DATE,
    -- Standard attributes used everywhere
    day_of_week VARCHAR(10),
    month_name VARCHAR(10),
    quarter INTEGER,
    year INTEGER,
    is_holiday BOOLEAN
);

-- Used by multiple fact tables
CREATE TABLE fct_sales (..., date_key INTEGER, ...);
CREATE TABLE fct_inventory (..., date_key INTEGER, ...);
CREATE TABLE fct_shipments (..., date_key INTEGER, ...);

-- All reference same dim_date table
-- Enables "drill across" queries
```

**Benefits**:
- Consistent reporting across business processes
- Single source of truth
- Enables cross-process analysis
- Simplifies maintenance

### Bus Matrix

**Purpose**: Plan conformed dimensions across enterprise

| Business Process | Date | Product | Customer | Store | Employee | Promotion |
|-----------------|------|---------|----------|-------|----------|-----------|
| Sales           | ✓    | ✓       | ✓        | ✓     | ✓        | ✓         |
| Inventory       | ✓    | ✓       |          | ✓     |          |           |
| Purchases       | ✓    | ✓       | Vendor   | ✓     |          |           |
| Returns         | ✓    | ✓       | ✓        | ✓     | ✓        |           |

**How to Create**:
1. List all business processes (rows)
2. List all dimensions (columns)
3. Mark which dimensions apply to each process
4. Identify conformed dimensions (used by multiple processes)

### Kimball Lifecycle Roadmap

**Phase 1: Project Planning (2-4 weeks)**
- Define project scope
- Identify stakeholders
- Establish success criteria
- Create project plan

**Phase 2: Business Requirements (2-4 weeks)**
- Conduct stakeholder interviews
- Document business processes
- Identify key metrics and KPIs
- Prioritize requirements

**Phase 3: Dimensional Modeling (2-4 weeks)**
- Apply four-step design process
- Design star schemas
- Plan for SCDs
- Document data models

**Phase 4: Physical Design (2-3 weeks)**
- Choose target platform
- Optimize for performance (partitioning, indexing)
- Plan capacity and scalability
- Define naming standards

**Phase 5: ETL Design & Development (4-8 weeks)**
- Design ETL architecture
- Build source-to-staging processes
- Implement dimension loading (SCD logic)
- Develop fact table loading
- Create audit and error handling

**Phase 6: BI Application Development (2-4 weeks)**
- Build standard reports
- Create ad-hoc analysis templates
- Develop dashboards
- Enable self-service access

**Phase 7: Deployment & Support (Ongoing)**
- User training
- Production deployment
- Monitor performance
- Gather feedback
- Plan next iteration

## Common Patterns

### Factless Fact Tables

**Use Case**: Record events without measurements

```sql
-- Student course enrollment (event occurs, but no measures)
CREATE TABLE fct_course_enrollment (
    date_key INTEGER,
    student_key INTEGER,
    course_key INTEGER,
    instructor_key INTEGER,
    enrollment_id VARCHAR(50),  -- Degenerate dimension

    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (student_key) REFERENCES dim_student(student_key),
    FOREIGN KEY (course_key) REFERENCES dim_course(course_key),
    FOREIGN KEY (instructor_key) REFERENCES dim_instructor(instructor_key)
);

-- Analysis: COUNT(*) for number of enrollments
SELECT
    c.course_name,
    i.instructor_name,
    COUNT(*) as enrollment_count
FROM fct_course_enrollment f
JOIN dim_course c ON f.course_key = c.course_key
JOIN dim_instructor i ON f.instructor_key = i.instructor_key
GROUP BY c.course_name, i.instructor_name;
```

### Junk Dimensions

**Use Case**: Consolidate miscellaneous flags and indicators

```sql
-- Instead of 5 separate dimensions for flags
CREATE TABLE dim_transaction_flags (
    transaction_flags_key INTEGER PRIMARY KEY,
    is_gift_wrapped BOOLEAN,
    is_express_shipping BOOLEAN,
    is_international BOOLEAN,
    payment_type VARCHAR(20),
    order_source VARCHAR(20)
);

-- Pre-populate all combinations
INSERT INTO dim_transaction_flags VALUES
(1, FALSE, FALSE, FALSE, 'Credit Card', 'Web'),
(2, TRUE, FALSE, FALSE, 'Credit Card', 'Web'),
(3, FALSE, TRUE, FALSE, 'Credit Card', 'Web'),
-- ... all valid combinations

-- Fact table references junk dimension
CREATE TABLE fct_orders (
    date_key INTEGER,
    customer_key INTEGER,
    product_key INTEGER,
    transaction_flags_key INTEGER,  -- Single FK
    order_amount DECIMAL(10,2)
);
```

### Role-Playing Dimensions

**Use Case**: Same dimension used multiple times with different roles

```sql
-- Single date dimension
CREATE TABLE dim_date (...);

-- Fact table with multiple date roles
CREATE TABLE fct_orders (
    order_date_key INTEGER,      -- Date order placed
    payment_date_key INTEGER,    -- Date payment received
    ship_date_key INTEGER,       -- Date order shipped
    delivery_date_key INTEGER,   -- Date delivered

    -- All reference same dim_date
    FOREIGN KEY (order_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (payment_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (ship_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (delivery_date_key) REFERENCES dim_date(date_key)
);

-- Query using aliases
SELECT
    order_date.year as order_year,
    ship_date.year as ship_year,
    COUNT(*) as order_count
FROM fct_orders f
JOIN dim_date order_date ON f.order_date_key = order_date.date_key
JOIN dim_date ship_date ON f.ship_date_key = ship_date.date_key
GROUP BY order_date.year, ship_date.year;
```

## Checklist

### Design Phase
- [ ] Business process selected and documented
- [ ] Grain clearly defined and validated
- [ ] All dimensions identified
- [ ] Dimension attributes cataloged
- [ ] SCD types assigned to attributes
- [ ] All facts identified and classified
- [ ] Fact table grain matches dimension grain
- [ ] Conformed dimensions planned
- [ ] Bus matrix created
- [ ] Data model documented and reviewed

### Implementation Phase
- [ ] DDL created for all tables
- [ ] Surrogate keys implemented
- [ ] SCD Type 2 logic implemented
- [ ] ETL processes built
- [ ] Data quality checks in place
- [ ] Initial data loaded
- [ ] Performance optimized (indexes, partitions)
- [ ] Sample queries tested
- [ ] Documentation complete
- [ ] User training conducted

### Post-Deployment
- [ ] Monitor query performance
- [ ] Gather user feedback
- [ ] Track data quality metrics
- [ ] Plan next business process
- [ ] Identify new conformed dimensions
- [ ] Optimize based on usage patterns
