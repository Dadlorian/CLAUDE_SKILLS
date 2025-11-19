# Conformed Dimensions Reference

## Overview

Conformed dimensions are dimensions that are shared across multiple fact tables or data marts with consistent structure, content, and meaning. They are the foundation of enterprise dimensional architecture and enable integrated analytics across business processes.

**Kimball's Definition**: "A conformed dimension is a dimension that means the same thing with every possible fact table to which it can be joined."

---

## Why Conformed Dimensions Matter

### Benefits

1. **Integrated Analytics**: Drill across different business processes
2. **Consistency**: Same attributes, same values across the enterprise
3. **Reusability**: Build once, use many times
4. **Single Version of Truth**: One authoritative source for dimension data
5. **Simplified ETL**: Centralized dimension management
6. **User Trust**: Consistent metrics across reports
7. **Reduced Development Time**: Shared dimensions accelerate new marts

### Without Conformed Dimensions (Anti-Pattern)
```
Sales Data Mart:
  - FACT_SALES → DIM_CUSTOMER (customer_id, name, region)

Service Data Mart:
  - FACT_SERVICE_CALL → DIM_CUSTOMER (cust_num, cust_name, territory)

Finance Data Mart:
  - FACT_PAYMENT → DIM_CLIENT (client_id, client_name, zone)

Problems:
- Different keys (customer_id vs cust_num vs client_id)
- Different names for same customer
- Cannot integrate: "Total sales + service costs per customer"
- Conflicting metrics: "How many customers do we have?"
```

### With Conformed Dimensions
```
Enterprise Customer Dimension:
  DIM_CUSTOMER (shared across all data marts)
  - customer_key (surrogate, consistent)
  - customer_id (standardized business key)
  - customer_name (standardized)
  - customer_region (standardized)

All Data Marts:
  FACT_SALES → DIM_CUSTOMER
  FACT_SERVICE_CALL → DIM_CUSTOMER
  FACT_PAYMENT → DIM_CUSTOMER

Benefits:
✓ Same customer keys across all facts
✓ Integrated reporting
✓ Drill across queries
✓ Consistent metrics
```

---

## Types of Conformed Dimensions

### 1. Exact Conformed Dimensions

**Definition**: Identical structure, content, and meaning across all uses.

**Example**: DIM_DATE
```sql
-- Exactly the same dimension used everywhere
CREATE TABLE DIM_DATE (
    date_key INTEGER PRIMARY KEY,
    date DATE,
    day_name VARCHAR(10),
    month_name VARCHAR(10),
    quarter_name VARCHAR(2),
    year INTEGER,
    fiscal_year INTEGER,
    is_holiday CHAR(1)
);

-- Used by all fact tables
FACT_SALES.order_date_key → DIM_DATE.date_key
FACT_INVENTORY.snapshot_date_key → DIM_DATE.date_key
FACT_SHIPMENT.ship_date_key → DIM_DATE.date_key
FACT_PAYMENT.payment_date_key → DIM_DATE.date_key
```

**Requirements**:
- Identical columns across all uses
- Same keys, same values
- Same business definitions
- Centrally managed

---

### 2. Conformed Subset (Drill-Down)

**Definition**: Smaller dimension is a subset of larger dimension. Larger dimension adds additional attributes.

**Example**: Product Dimension
```sql
-- Base conformed dimension (used by most data marts)
DIM_PRODUCT
- product_key
- product_id
- product_name
- category
- brand

-- Extended dimension (used by specific data mart with additional needs)
DIM_PRODUCT_EXTENDED
- product_key (same keys as DIM_PRODUCT)
- product_id
- product_name
- category
- brand
-- Additional attributes for detailed analysis
- detailed_description
- ingredients
- nutritional_facts
- supplier_details
- manufacturing_location
```

**Rule**: The subset must be exactly the same across all uses. Extensions can vary.

---

### 3. Conformed Rollup (Drill-Up)

**Definition**: Higher-level aggregation of a detailed dimension. Summary dimension is aggregated from detailed dimension.

**Example**: Geography Hierarchy
```sql
-- Detailed conformed dimension
DIM_STORE
- store_key
- store_id
- store_name
- city
- state
- region
- district

-- Rolled-up conformed dimension
DIM_DISTRICT (aggregation of stores)
- district_key
- district_id
- district_name
- region

Relationship:
Multiple stores → One district
DIM_STORE.district_key → DIM_DISTRICT.district_key
```

**Use Cases**:
- Some facts at store level (FACT_SALES)
- Some facts at district level (FACT_DISTRICT_BUDGET)
- Can drill across if district is conformed

---

### 4. Conformed Attributes

**Definition**: Not the entire dimension, but specific attributes that are standardized across dimensions.

**Example**: Geographic Attributes
```sql
-- Customer dimension with conformed geographic attributes
DIM_CUSTOMER
- customer_key
- customer_name
- state_code (conformed)
- state_name (conformed)
- region_code (conformed)
- region_name (conformed)

-- Store dimension with same conformed geographic attributes
DIM_STORE
- store_key
- store_name
- state_code (conformed - same values as DIM_CUSTOMER)
- state_name (conformed - same values as DIM_CUSTOMER)
- region_code (conformed - same values as DIM_CUSTOMER)
- region_name (conformed - same values as DIM_CUSTOMER)
```

**Benefit**: Can aggregate across different dimensions by conformed attributes
```sql
-- Sales by state (combining customer and store geographies)
SELECT
    c.state_name,  -- Conformed attribute
    SUM(f.amount) as total_sales
FROM FACT_SALES f
JOIN DIM_CUSTOMER c ON f.customer_key = c.customer_key
GROUP BY c.state_name

UNION ALL

SELECT
    s.state_name,  -- Same conformed values
    SUM(f.amount) as total_sales
FROM FACT_INVENTORY f
JOIN DIM_STORE s ON f.store_key = s.store_key
GROUP BY s.state_name;
```

---

## Dimension Bus Matrix

### Definition
A grid that documents which conformed dimensions are used by which fact tables across the enterprise.

### Example Bus Matrix
```
                           | DIM_DATE | DIM_CUSTOMER | DIM_PRODUCT | DIM_STORE | DIM_EMPLOYEE
---------------------------|----------|--------------|-------------|-----------|-------------
FACT_SALES                 |    X     |      X       |      X      |     X     |      X
FACT_INVENTORY             |    X     |              |      X      |     X     |
FACT_SHIPMENT              |    X     |      X       |      X      |     X     |
FACT_RETURNS               |    X     |      X       |      X      |     X     |
FACT_CUSTOMER_SERVICE      |    X     |      X       |             |           |      X
FACT_EMPLOYEE_PERFORMANCE  |    X     |              |             |     X     |      X
FACT_STORE_TRAFFIC         |    X     |              |             |     X     |
```

### Purpose
- **Planning Tool**: Identifies which dimensions to conform first (most shared)
- **Design Guide**: Shows relationships between processes
- **Documentation**: Visualizes enterprise architecture
- **Impact Analysis**: Shows which facts are affected by dimension changes
- **Priority Setting**: Most-used dimensions are highest priority

### Reading the Matrix
- **Rows**: Business processes (fact tables)
- **Columns**: Conformed dimensions
- **X**: Dimension is used by this fact table
- **Dense column**: Dimension shared across many processes (high conformity value)

---

## Implementing Conformed Dimensions

### Approach 1: Enterprise Dimension (Inmon-style)

**Structure**:
```
Master Data Management System
    ↓
Enterprise Customer Dimension (3NF)
    ↓
Dimensional Customer (denormalized for data marts)
    ↓
All Data Marts use same dimension
```

**Process**:
1. Centralized master data management
2. Single source of truth
3. ETL process produces conformed dimension
4. Data marts reference shared dimension
5. Updates propagated from master

**Example**:
```sql
-- Master data layer (3NF)
MASTER.CUSTOMER
MASTER.CUSTOMER_ADDRESS
MASTER.CUSTOMER_CONTACT

-- ETL to conformed dimension
DIM_CUSTOMER (denormalized, shared by all marts)
- customer_key (surrogate)
- customer_id (from MASTER.CUSTOMER)
- customer_name
- primary_address (from MASTER.CUSTOMER_ADDRESS)
- primary_phone (from MASTER.CUSTOMER_CONTACT)

-- All data marts reference
DATAMART_SALES.FACT_SALES → DIM_CUSTOMER
DATAMART_SERVICE.FACT_SERVICE → DIM_CUSTOMER
DATAMART_FINANCE.FACT_PAYMENT → DIM_CUSTOMER
```

---

### Approach 2: Kimball Bus Architecture

**Structure**:
```
Conformed Dimension Owners (designated teams)
    ↓
Published Conformed Dimensions
    ↓
Data Marts built using conformed dimensions
```

**Process**:
1. Identify enterprise dimensions in bus matrix
2. Assign dimension owner/steward
3. Define standard structure and content
4. Publish dimension for reuse
5. Enforce conformity in all new data marts

**Governance**:
- Dimension steward approves changes
- Change control process for structure
- SLA for dimension updates
- Documentation and metadata

---

### Approach 3: Federated (Decentralized with Standards)

**Structure**:
```
Conformed Dimension Standards (centrally defined)
    ↓
Each data mart implements to standard
    ↓
Integration layer harmonizes views
```

**Process**:
1. Central team defines standards (structure, values, rules)
2. Data mart teams implement to standards
3. Periodic audits for compliance
4. Integration layer provides unified view

---

## Conformed Dimension Challenges

### Challenge 1: Different Source Systems

**Problem**: Customer data from CRM, ERP, and Web - different formats and values

**Solution**: Master Data Management (MDM)
```sql
-- Staging: Raw data from multiple sources
STAGING.CUSTOMER_CRM
STAGING.CUSTOMER_ERP
STAGING.CUSTOMER_WEB

-- Integration: Match and merge
INTEGRATION.CUSTOMER_MASTER
- master_customer_id (assigned)
- source_system
- source_customer_id
- customer_name (standardized)
- matching_confidence_score

-- Conformed dimension: Single view
DIM_CUSTOMER
- customer_key (surrogate)
- master_customer_id
- customer_name (best from sources)
- data_quality_score
```

---

### Challenge 2: Different Granularity

**Problem**: Sales data by store, inventory data by warehouse (different grain)

**Solution**: Hierarchy rollup or bridge tables
```sql
-- Detailed dimension
DIM_LOCATION
- location_key
- location_id
- location_name
- location_type (Store, Warehouse, Distribution Center)
- parent_location_key (hierarchy)

-- Facts reference at their natural grain
FACT_SALES → DIM_LOCATION (store level)
FACT_INVENTORY → DIM_LOCATION (warehouse level)

-- Can roll up to common level for comparison
SELECT location_type, SUM(amount)
FROM FACT_SALES f
JOIN DIM_LOCATION l ON f.location_key = l.location_key
GROUP BY location_type;
```

---

### Challenge 3: Different Update Frequencies

**Problem**: Customer dimension updated daily (sales), weekly (finance)

**Solution**: Most frequent update wins
```sql
-- Conformed dimension updated daily (most frequent need)
-- Finance data mart gets daily updates even though only needs weekly
-- Alternative: Snapshot dimension at weekly intervals for finance
```

---

### Challenge 4: Different Attribute Requirements

**Problem**: Sales needs customer demographics, Finance only needs basic info

**Solution**: Conformed core + Extensions
```sql
-- Core conformed dimension (required by all)
DIM_CUSTOMER
- customer_key
- customer_id
- customer_name
- customer_type

-- Extended for specific needs
DIM_CUSTOMER_EXTENDED
- customer_key (same as core)
- detailed_demographics
- detailed_preferences
- detailed_behavior_scores
```

---

## Drill-Across Queries

### Definition
Querying multiple fact tables using conformed dimensions to integrate metrics.

### Example: Sales and Inventory by Product
```sql
-- Separate queries using conformed DIM_PRODUCT
WITH sales AS (
    SELECT
        p.product_category,
        SUM(s.sales_amount) as total_sales,
        SUM(s.quantity) as units_sold
    FROM FACT_SALES s
    JOIN DIM_PRODUCT p ON s.product_key = p.product_key
    JOIN DIM_DATE d ON s.date_key = d.date_key
    WHERE d.year = 2024 AND d.month = 6
    GROUP BY p.product_category
),
inventory AS (
    SELECT
        p.product_category,
        AVG(i.ending_quantity) as avg_inventory
    FROM FACT_INVENTORY_DAILY i
    JOIN DIM_PRODUCT p ON i.product_key = p.product_key
    JOIN DIM_DATE d ON i.date_key = d.date_key
    WHERE d.year = 2024 AND d.month = 6
    GROUP BY p.product_category
)
SELECT
    s.product_category,
    s.total_sales,
    s.units_sold,
    i.avg_inventory,
    s.total_sales / NULLIF(i.avg_inventory, 0) as inventory_turnover
FROM sales s
JOIN inventory i ON s.product_category = i.product_category;
```

**Key Point**: This only works because DIM_PRODUCT is conformed (same keys, same categories)

---

## Conformed Dimension Governance

### Roles and Responsibilities

**Dimension Owner/Steward**:
- Defines dimension structure
- Approves attribute additions
- Manages dimension values
- Enforces data quality
- Documents business rules
- Coordinates changes

**Data Governance Committee**:
- Approves new conformed dimensions
- Resolves conflicts between business units
- Sets conformity standards
- Prioritizes dimension development

**Data Mart Teams**:
- Use conformed dimensions as published
- Request new attributes through steward
- Report data quality issues
- Comply with conformity standards

---

### Change Control Process

**Adding New Attributes**:
1. Request submitted to dimension steward
2. Impact analysis (which data marts affected?)
3. Business case (why needed?)
4. Approval by governance committee
5. Implementation in test environment
6. Communication to all consumers
7. Coordinated deployment

**Changing Existing Attributes**:
1. Higher scrutiny (affects existing reports)
2. Impact analysis required
3. Backward compatibility assessment
4. Migration plan for existing data
5. Testing by all consuming systems
6. Coordinated deployment with rollback plan

---

## Conformed Dimension Quality

### Quality Dimensions

1. **Completeness**: All required attributes populated
2. **Accuracy**: Values match source systems
3. **Consistency**: Same meaning across all uses
4. **Timeliness**: Updated per SLA
5. **Uniqueness**: No duplicate business keys
6. **Validity**: Values within expected domains

### Quality Monitoring
```sql
-- Data quality checks for conformed dimension
DIM_CUSTOMER_QUALITY
- date_key
- total_records
- null_customer_name_count
- null_address_count
- duplicate_customer_id_count
- invalid_state_code_count
- orphaned_records_in_facts_count
- completeness_percentage
- quality_score
```

---

## Best Practices

### Design
1. **Identify Early**: Use bus matrix in planning phase
2. **Start with Highest Impact**: Conform most-shared dimensions first (date, customer, product)
3. **Design for Reuse**: Think enterprise-wide, not single data mart
4. **Include Metadata**: Document source systems, business rules, refresh schedule
5. **Plan for Growth**: Design for attributes that may be added later

### Implementation
1. **Centralize ETL**: One ETL process creates conformed dimension
2. **Single Physical Table**: Not copies in each data mart
3. **Consistent Naming**: Same table name across enterprise
4. **Version Control**: Track dimension structure changes
5. **Audit Trail**: Who, when, why for all changes

### Governance
1. **Assign Ownership**: Every conformed dimension has steward
2. **Document Standards**: Structure, naming, values, rules
3. **Change Control**: Formal process for modifications
4. **SLA**: Define update frequency and availability
5. **Quality Metrics**: Monitor and report dimension quality

### Usage
1. **Enforce Conformity**: Don't allow non-conformed versions
2. **Educate Users**: Train on conformed dimensions and benefits
3. **Track Lineage**: Document which facts use which dimensions
4. **Communicate Changes**: Notify all consumers of updates
5. **Measure Value**: Track drill-across query usage

---

## Conformed Dimension Checklist

### Is this dimension conformed?
- [ ] Same surrogate keys across all fact tables?
- [ ] Same business keys across all uses?
- [ ] Same attribute names and meanings?
- [ ] Same attribute values (no conflicts)?
- [ ] Centrally managed (single source)?
- [ ] Documented in bus matrix?
- [ ] Change control process in place?
- [ ] Dimension steward assigned?
- [ ] Update SLA defined?
- [ ] Quality metrics monitored?

### For New Data Mart
- [ ] Reviewed bus matrix for applicable dimensions?
- [ ] Using existing conformed dimensions where applicable?
- [ ] Requested new attributes through proper channels?
- [ ] Not creating non-conformed versions of existing dimensions?
- [ ] Documented new dimension needs for future conformity?

---

## Common Conformed Dimensions

### Universal (Nearly Every Enterprise)

**DIM_DATE**:
- Most critical conformed dimension
- Used by all fact tables
- Same structure across all data marts
- Include both calendar and fiscal calendars

**DIM_CUSTOMER**:
- High-value conformity
- Integrates sales, service, finance
- Often requires MDM
- May have multiple roles (bill-to, ship-to)

**DIM_PRODUCT**:
- Core business dimension
- Shared across operations
- Include complete hierarchy
- Version history important (Type 2)

### Industry-Specific

**Retail**: DIM_STORE, DIM_PROMOTION, DIM_EMPLOYEE
**Banking**: DIM_ACCOUNT, DIM_BRANCH, DIM_ACCOUNT_TYPE
**Healthcare**: DIM_PATIENT, DIM_PROVIDER, DIM_DIAGNOSIS
**Telecom**: DIM_SUBSCRIBER, DIM_PLAN, DIM_DEVICE
**Manufacturing**: DIM_PLANT, DIM_PART, DIM_SUPPLIER

---

## Success Metrics

### Adoption
- Percentage of data marts using conformed dimensions
- Number of drill-across queries executed
- User satisfaction with integrated reporting

### Quality
- Dimension completeness percentage
- Data quality score trends
- Number of data quality issues reported

### Efficiency
- Time to develop new data mart (should decrease)
- ETL development effort (should decrease)
- User training time (should decrease)

### Business Value
- Number of integrated reports/dashboards
- Business decisions enabled by drill-across
- Consistency of enterprise metrics
