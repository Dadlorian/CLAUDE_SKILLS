# Conformed Dimensions Implementation Guide

## Purpose
Conformed dimensions enable enterprise integration by sharing dimensions across multiple fact tables with consistent structure, keys, and values.

## Key Concepts

### What is Conformance?
- Same dimension structure across all uses
- Identical keys for same business entities
- Consistent attribute names and values
- Single source of truth

### Why Conform?
- Drill-across queries work
- Consistent enterprise metrics
- Single dimension ETL process
- Reduced development effort
- User trust in data

## Implementation Steps

### Step 1: Identify Candidates
Priority dimensions:
- DIM_DATE (universal)
- DIM_CUSTOMER
- DIM_PRODUCT  
- DIM_GEOGRAPHY
- DIM_EMPLOYEE

### Step 2: Define Standard
- Assign dimension owner/steward
- Define structure and attributes
- Establish naming conventions
- Document business rules
- Set update SLA

### Step 3: Build Master
- Single ETL process
- Integrate multiple sources
- Apply business rules
- Generate surrogate keys consistently

### Step 4: Enforce Usage
- All data marts use same physical table
- No local, modified versions
- Change control process
- Impact analysis for changes

## Bus Matrix
Document conformity:
```
            | DATE | CUSTOMER | PRODUCT | STORE
Sales       |  X   |    X     |    X    |   X
Inventory   |  X   |          |    X    |   X
Service     |  X   |    X     |         |
Returns     |  X   |    X     |    X    |   X
```

## Common Challenges

### Different Sources
**Challenge**: Customer in CRM, ERP, Web
**Solution**: Master data management (MDM) to match and merge

### Different Granularity  
**Challenge**: Sales by store, inventory by warehouse
**Solution**: Common parent in hierarchy or bridge tables

### Different Attributes
**Challenge**: Sales needs demographics, Finance doesn't
**Solution**: Core conformed + optional extensions

## Success Metrics
- % data marts using conformed dimensions
- Drill-across query count
- Dimension update SLA compliance
- Data quality scores

