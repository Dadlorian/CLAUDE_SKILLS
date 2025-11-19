# Normalization Rules Reference

## Database Normalization Overview

Normalization is the process of organizing data to reduce redundancy and improve data integrity. It involves decomposing tables into smaller, well-structured tables and defining relationships between them.

**Purpose**:
- Eliminate redundant data
- Ensure data dependencies make sense
- Reduce storage requirements
- Improve data integrity
- Simplify maintenance and updates

---

## Normal Forms

### Unnormalized Form (UNF)

**Definition**: Data contains repeating groups or arrays within rows.

**Example**:
```
ORDER_TABLE (Unnormalized)
OrderID | CustomerName | Products
--------|--------------|------------------------------------------
1001    | John Smith   | Product1, Product2, Product3
1002    | Jane Doe     | Product2, Product4
```

**Problems**:
- Cannot easily query individual products
- Difficult to update product information
- No atomic values

---

### First Normal Form (1NF)

**Definition**:
- All attributes contain only atomic (indivisible) values
- Each column contains values of a single type
- Each column has a unique name
- The order of rows and columns doesn't matter

**Rules**:
1. Eliminate repeating groups
2. Create separate row for each set of related data
3. Identify each row with unique primary key

**Example - Converting to 1NF**:

**Before (UNF)**:
```
ORDER
OrderID | CustomerName | Products
1001    | John Smith   | Product1, Product2, Product3
```

**After (1NF)**:
```
ORDER
OrderID | CustomerName | Product
1001    | John Smith   | Product1
1001    | John Smith   | Product2
1001    | John Smith   | Product3
```

**Verification**:
- ✓ All values are atomic
- ✓ No repeating groups
- ✓ Each row is unique (OrderID + Product forms composite key)

---

### Second Normal Form (2NF)

**Definition**:
- Must be in 1NF
- All non-key attributes are fully functionally dependent on the entire primary key
- No partial dependencies (relevant only for composite keys)

**Partial Dependency**: When non-key attribute depends on part of composite key, not the whole key.

**Example - Converting to 2NF**:

**Before (1NF with partial dependencies)**:
```
ORDER_LINE (PK: OrderID + ProductID)
OrderID | ProductID | Quantity | CustomerName | CustomerEmail | ProductName | ProductPrice
1001    | P01       | 2        | John Smith   | john@email    | Widget      | 10.00
1001    | P02       | 1        | John Smith   | john@email    | Gadget      | 25.00
1002    | P01       | 3        | Jane Doe     | jane@email    | Widget      | 10.00
```

**Problems**:
- CustomerName depends only on OrderID (partial dependency)
- ProductName depends only on ProductID (partial dependency)

**After (2NF)**:
```
ORDER
OrderID | CustomerName | CustomerEmail
1001    | John Smith   | john@email
1002    | Jane Doe     | jane@email

PRODUCT
ProductID | ProductName | ProductPrice
P01       | Widget      | 10.00
P02       | Gadget      | 25.00

ORDER_LINE
OrderID | ProductID | Quantity
1001    | P01       | 2
1001    | P02       | 1
1002    | P01       | 3
```

**Verification**:
- ✓ All tables are in 1NF
- ✓ No partial dependencies
- ✓ Non-key attributes depend on entire primary key

---

### Third Normal Form (3NF)

**Definition**:
- Must be in 2NF
- No transitive dependencies
- All attributes are directly dependent on the primary key only

**Transitive Dependency**: When non-key attribute depends on another non-key attribute.
- A → B and B → C, therefore A → C (transitive)

**Example - Converting to 3NF**:

**Before (2NF with transitive dependencies)**:
```
EMPLOYEE
EmployeeID | EmployeeName | DepartmentID | DepartmentName | DepartmentManager
E001       | John Smith   | D01          | Sales          | Sarah Jones
E002       | Jane Doe     | D01          | Sales          | Sarah Jones
E003       | Bob Wilson   | D02          | IT             | Mike Davis
```

**Problem**:
- DepartmentName depends on DepartmentID (not directly on EmployeeID)
- DepartmentManager depends on DepartmentID (transitive dependency)

**After (3NF)**:
```
EMPLOYEE
EmployeeID | EmployeeName | DepartmentID
E001       | John Smith   | D01
E002       | Jane Doe     | D01
E003       | Bob Wilson   | D02

DEPARTMENT
DepartmentID | DepartmentName | DepartmentManager
D01          | Sales          | Sarah Jones
D02          | IT             | Mike Davis
```

**Verification**:
- ✓ All tables are in 2NF
- ✓ No transitive dependencies
- ✓ All non-key attributes depend directly on primary key

---

### Boyce-Codd Normal Form (BCNF)

**Definition**:
- Stricter version of 3NF
- For every functional dependency X → Y, X must be a superkey
- Handles anomalies not addressed by 3NF (rare cases)

**Example**:
```
STUDENT_ADVISOR (Student can have multiple majors, each major has one advisor)
StudentID | Major          | Advisor
S001      | Computer Sci   | Dr. Smith
S001      | Mathematics    | Dr. Jones
S002      | Computer Sci   | Dr. Smith
```

**Functional Dependencies**:
- StudentID + Major → Advisor (candidate key)
- Advisor → Major (violation: Advisor is not a superkey)

**Problem**: Dr. Smith always advises Computer Science, but this isn't enforced.

**After (BCNF)**:
```
ADVISOR_MAJOR
Advisor    | Major
Dr. Smith  | Computer Sci
Dr. Jones  | Mathematics

STUDENT_ADVISOR
StudentID | Advisor
S001      | Dr. Smith
S001      | Dr. Jones
S002      | Dr. Smith
```

---

### Fourth Normal Form (4NF)

**Definition**:
- Must be in BCNF
- No multi-valued dependencies
- Handles independent many-to-many relationships

**Multi-valued Dependency**: One attribute determines multiple independent sets of values.

**Example**:

**Before (BCNF but has multi-valued dependency)**:
```
EMPLOYEE_SKILL_LANGUAGE
EmployeeID | Skill      | Language
E001       | Java       | English
E001       | Java       | Spanish
E001       | Python     | English
E001       | Python     | Spanish
```

**Problem**: Skills and Languages are independent (all combinations repeated).

**After (4NF)**:
```
EMPLOYEE_SKILL
EmployeeID | Skill
E001       | Java
E001       | Python

EMPLOYEE_LANGUAGE
EmployeeID | Language
E001       | English
E001       | Spanish
```

---

### Fifth Normal Form (5NF)

**Definition**:
- Must be in 4NF
- No join dependencies
- Cannot be decomposed without loss of information

**Example**: Complex three-way relationship where all three attributes are needed.

```
SUPPLIER_PART_PROJECT (supplier supplies part for project)
```

Only decompose if the join can be reconstructed without creating spurious tuples.

---

## Normalization for Data Warehousing

### Inmon Approach (3NF in EDW)

**EDW (Enterprise Data Warehouse)**:
- Normalize to 3NF
- Subject-oriented organization
- Atomic data storage
- Single version of truth

**Example - Customer Subject Area (3NF)**:
```
CUSTOMER
customer_key | customer_id | customer_name | customer_type_key

CUSTOMER_TYPE
customer_type_key | customer_type_code | customer_type_desc

CUSTOMER_ADDRESS
address_key | customer_key | address_type_key | street | city | state | zip

ADDRESS_TYPE
address_type_key | address_type_code | address_type_desc

CUSTOMER_PHONE
phone_key | customer_key | phone_type_key | phone_number

PHONE_TYPE
phone_type_key | phone_type_code | phone_type_desc
```

**Benefits**:
- Data integrity
- No redundancy
- Easy to maintain
- Supports complex relationships

**Drawbacks**:
- Complex queries (many joins)
- Slower query performance
- Difficult for business users

---

### Kimball Approach (Denormalization)

**Dimensional Model**:
- Denormalize dimensions (2NF or 1NF)
- Optimize for query performance
- Business user accessibility

**Example - Customer Dimension (Denormalized)**:
```
DIM_CUSTOMER
customer_key (PK, surrogate)
customer_id (natural key)
customer_name
customer_type_code
customer_type_desc
primary_address_street
primary_address_city
primary_address_state
primary_address_zip
primary_phone_number
secondary_phone_number
credit_score_band
income_range
customer_segment
region
district
territory
effective_date
expiration_date
current_flag
```

**Trade-offs**:
- More storage (redundancy)
- Faster queries (fewer joins)
- Simpler for users
- More complex ETL (manage redundancy)

---

## Denormalization Patterns for BI

### When to Denormalize

1. **Dimension Tables**: Almost always denormalize
   - Include hierarchies in single table
   - Duplicate reference data
   - Optimize for query performance

2. **Fact Tables**: Keep normalized foreign keys
   - Never denormalize dimension attributes into facts
   - Use surrogate keys
   - Keep fact tables narrow

3. **Aggregate Tables**: Pre-calculate and store
   - Summarized facts at higher grains
   - Redundant but improves performance

---

### Controlled Denormalization

**Technique 1: Flatten Hierarchies**
```
Instead of:
  PRODUCT → SUBCATEGORY → CATEGORY → DEPARTMENT

Use:
  DIM_PRODUCT (includes all hierarchy levels)
  - product_key
  - product_name
  - subcategory_name
  - category_name
  - department_name
```

**Technique 2: Duplicate Reference Data**
```
Instead of:
  CUSTOMER → STATE → REGION → COUNTRY

Use:
  DIM_CUSTOMER (includes all geographic attributes)
  - customer_key
  - state_code
  - state_name
  - region_code
  - region_name
  - country_code
  - country_name
```

**Technique 3: Outrigger (Selective Normalization)**
```
When reference data is large and reusable:
  DIM_CUSTOMER
  - customer_key
  - state_key (FK to DIM_STATE)

  DIM_STATE (outrigger)
  - state_key
  - state_code
  - state_name
  - region
  - country
```

---

## Normalization Decision Matrix

| Context | Normal Form | Rationale |
|---------|-------------|-----------|
| OLTP Database | 3NF | Data integrity, update efficiency |
| Inmon EDW | 3NF | Enterprise integration, single version of truth |
| Kimball Dimensions | Denormalized | Query performance, user accessibility |
| Kimball Facts | 2NF (foreign keys) | Narrow tables, referential integrity |
| Data Vault Hubs | BCNF | Business keys only |
| Data Vault Satellites | 3NF | Descriptive attributes |
| Staging Area | 1NF or UNF | Source-aligned, minimal transformation |
| Aggregate Tables | Denormalized | Pre-calculated, query optimization |

---

## Functional Dependency Rules

### Definition
Functional dependency (A → B) means attribute A uniquely determines attribute B.

### Types

1. **Full Functional Dependency**:
   - Non-key attribute depends on entire composite key
   - Required for 2NF

2. **Partial Functional Dependency**:
   - Non-key attribute depends on part of composite key
   - Violation of 2NF

3. **Transitive Functional Dependency**:
   - Non-key attribute depends on another non-key attribute
   - Violation of 3NF

### Armstrong's Axioms

1. **Reflexivity**: If B ⊆ A, then A → B
2. **Augmentation**: If A → B, then AC → BC
3. **Transitivity**: If A → B and B → C, then A → C

---

## Practical Guidelines

### For OLTP Systems
1. Normalize to at least 3NF
2. Consider BCNF for critical tables
3. Denormalize only for proven performance issues
4. Document any denormalization decisions
5. Maintain data integrity with constraints

### For Data Warehouses (Inmon)
1. EDW in 3NF
2. Subject-oriented organization
3. Atomic grain
4. Complete audit trail
5. Dependent data marts can denormalize

### For Data Warehouses (Kimball)
1. Dimensions: Denormalized (star schema)
2. Facts: Normalized foreign keys, additive measures
3. No snowflaking unless necessary
4. Conformed dimensions enforce consistency
5. ETL handles redundancy management

### For Data Vault
1. Hubs: BCNF (business keys only)
2. Links: BCNF (foreign keys only)
3. Satellites: 3NF (descriptive data)
4. No redundancy in raw vault
5. Business vault can calculate/denormalize

---

## Common Mistakes

1. **Over-normalization in DW Dimensions**
   - ❌ Snowflaking dimensions excessively
   - ✓ Keep star schema for performance

2. **Under-normalization in OLTP**
   - ❌ Storing redundant data for convenience
   - ✓ Normalize to 3NF, denormalize with proof

3. **Denormalizing Fact Tables**
   - ❌ Adding dimension attributes to facts
   - ✓ Keep facts narrow with foreign keys only

4. **Ignoring Update Anomalies**
   - ❌ Accepting redundancy without update strategy
   - ✓ Plan for maintaining consistency

5. **Premature Optimization**
   - ❌ Denormalizing before measuring performance
   - ✓ Normalize first, denormalize based on evidence

---

## Quick Reference: Normalization Checklist

**1NF**:
- [ ] All attributes are atomic
- [ ] No repeating groups
- [ ] Each row is unique
- [ ] Primary key defined

**2NF**:
- [ ] Table is in 1NF
- [ ] No partial dependencies
- [ ] Non-key attributes depend on entire primary key

**3NF**:
- [ ] Table is in 2NF
- [ ] No transitive dependencies
- [ ] Non-key attributes depend only on primary key

**BCNF**:
- [ ] Table is in 3NF
- [ ] Every determinant is a candidate key
- [ ] No functional dependencies violate key structure

**4NF**:
- [ ] Table is in BCNF
- [ ] No multi-valued dependencies
- [ ] Independent many-to-many relationships separated

**5NF**:
- [ ] Table is in 4NF
- [ ] No join dependencies
- [ ] Cannot be decomposed without information loss
