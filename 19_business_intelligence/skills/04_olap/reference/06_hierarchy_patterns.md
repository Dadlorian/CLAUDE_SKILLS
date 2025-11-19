# Hierarchy Patterns in OLAP

## Overview

Hierarchies organize dimension members into logical parent-child relationships, enabling drill-down analysis and aggregation at multiple levels.

## Hierarchy Types

### 1. Balanced Hierarchies
All branches have the same depth, no missing levels:

```
Geography (Balanced):
All
└── Country
    └── State/Province
        └── City
            └── Postal Code

Example Path:
All → USA → California → San Francisco → 94102

Characteristics:
- Every leaf is at same level (depth = 4)
- No missing levels
- Most common type
- Easiest to query and aggregate
```

### 2. Unbalanced (Ragged) Hierarchies
Branches have different depths:

```
Organization (Ragged):
CEO
├── VP Sales (Level 2)
│   ├── Director East (Level 3)
│   │   └── Manager NYC (Level 4)
│   └── Manager West (Level 3) ← Different depth!
└── VP Operations (Level 2)
    └── Manager Production (Level 3)

Characteristics:
- Varying depths
- Some branches shorter than others
- Requires special handling
- Common in org charts, account hierarchies
```

#### Ragged Hierarchy Handling
```mdx
-- Hide unused levels
WITH MEMBER [Employee].[Org].[Level 04].[MEMBER_CAPTION]
AS IIF(
    IsLeaf([Employee].[Org].CurrentMember),
    [Employee].[Org].CurrentMember.Name,
    NULL
)

-- Skip empty levels in visualization
```

### 3. Parent-Child Hierarchies
Self-referencing relationships with unlimited levels:

```
Employee Table:
EmployeeID | Name        | ManagerID
1          | CEO         | NULL
2          | VP Sales    | 1
3          | Director    | 2
4          | Manager A   | 3
5          | Manager B   | 3
6          | Rep 1       | 4
7          | Rep 2       | 4

Resulting Hierarchy:
CEO (1)
└── VP Sales (2)
    └── Director (3)
        ├── Manager A (4)
        │   ├── Rep 1 (6)
        │   └── Rep 2 (7)
        └── Manager B (5)

Characteristics:
- Variable depth (not fixed)
- Defined by data, not metadata
- Flexible structure
- Complex aggregation
```

#### Parent-Child Configuration (SSAS)
```xml
<Dimension>
  <ID>Employee</ID>
  <Attributes>
    <Attribute>
      <ID>Employee</ID>
      <Type>Parent</Type>
      <Usage>Parent</Usage>
    </Attribute>
  </Attributes>
</Dimension>
```

### 4. Many-to-Many Hierarchies
Members can belong to multiple parents:

```
Product-to-Category (Many-to-Many):
Product "Smartphone X":
├── Electronics
├── Mobile Devices
└── Business Equipment

Account Balance:
Account 12345:
├── Personal Accounts
├── Premium Tier
└── Online Banking Users

Characteristics:
- Single member in multiple paths
- Requires bridge table
- Complex aggregation logic
- Avoid double-counting
```

## Standard Hierarchy Patterns

### Time Hierarchy
```
Calendar:
All Years
└── Year (2024)
    └── Quarter (Q1)
        └── Month (January)
            └── Day (2024-01-15)

Fiscal:
All Fiscal Years
└── Fiscal Year (FY2024)
    └── Fiscal Quarter (FQ1)
        └── Fiscal Period (Period 1)
            └── Date (2024-07-15)

Week-based:
All Years
└── Year (2024)
    └── Week (Week 3)
        └── Day (2024-01-15)

ISO 8601:
└── Year (2024)
    └── ISO Week (Week 03)
        └── Weekday (Monday)
```

### Geography Hierarchy
```
Corporate:
All
└── Region (Americas)
    └── Country (USA)
        └── State (California)
            └── City (San Francisco)
                └── Store (Store #123)

Sales Territory:
All Territories
└── Territory Group (West)
    └── Territory (Pacific)
        └── Sales District (SF Bay Area)
            └── Sales Rep (John Smith)
```

### Product Hierarchy
```
Standard:
All Products
└── Division (Consumer Electronics)
    └── Category (Computers)
        └── Subcategory (Laptops)
            └── Product (Model X1000)
                └── SKU (X1000-BLK-256GB)

Alternate:
All Products
└── Brand (TechCorp)
    └── Product Line (Pro Series)
        └── Product Family (Ultrabooks)
            └── Product (Model X1000)
```

### Customer Hierarchy
```
B2C:
All Customers
└── Segment (Premium)
    └── Region (West)
        └── State (California)
            └── City (Los Angeles)
                └── Customer (Customer #12345)

B2B:
All Accounts
└── Industry (Technology)
    └── Account Type (Enterprise)
        └── Parent Account (TechCorp Global)
            └── Account (TechCorp USA)
                └── Business Unit (Engineering Dept)
```

## Attribute Relationships

### Natural Hierarchy
Define relationships to optimize queries:

```
Product Dimension:
Product (Detail)
    ↑ Member of
Subcategory
    ↑ Member of
Category
    ↑ Member of
Division

Attribute Relationships:
Product → Subcategory (Many:One)
Subcategory → Category (Many:One)
Category → Division (Many:One)

Benefits:
- Faster aggregation
- Smaller indexes
- Better compression
- Query optimization
```

### SSAS Configuration
```xml
<Dimension>
  <ID>Product</ID>
  <Attributes>
    <Attribute>
      <ID>Product</ID>
      <AttributeRelationships>
        <AttributeRelationship>
          <AttributeID>Subcategory</AttributeID>
          <RelationshipType>Rigid</RelationshipType>
        </AttributeRelationship>
      </AttributeRelationships>
    </Attribute>
    <Attribute>
      <ID>Subcategory</ID>
      <AttributeRelationships>
        <AttributeRelationship>
          <AttributeID>Category</AttributeID>
          <RelationshipType>Flexible</RelationshipType>
        </AttributeRelationship>
      </AttributeRelationships>
    </Attribute>
  </Attributes>
</Dimension>
```

### Relationship Types

#### Rigid
Member never moves to different parent:
```
Example: Month → Year
- January 2024 will ALWAYS be in 2024
- Never changes
- Better performance
```

#### Flexible
Member might move to different parent:
```
Example: Employee → Department
- Employee might transfer departments
- Can change over time
- Requires full process on change
```

## User Hierarchies vs Attribute Hierarchies

### Attribute Hierarchy
Single level, auto-created for each attribute:

```
[Product].[Category]
├── All
└── Members
    ├── Electronics
    ├── Clothing
    └── Home & Garden

Usage: Direct attribute access
```

### User Hierarchy
Multi-level, manually defined:

```
[Product].[Product Hierarchy]
└── All Products
    └── Category
        └── Subcategory
            └── Product

Usage: Drill-down navigation
```

## Advanced Hierarchy Patterns

### Role-Playing Dimensions
Same dimension used multiple times:

```
Date Dimension (single physical):
├── Order Date Hierarchy
├── Ship Date Hierarchy
├── Delivery Date Hierarchy
└── Return Date Hierarchy

MDX Reference:
[Order Date].[Calendar].[2024]
[Ship Date].[Calendar].[2024]
```

### Slowly Changing Dimensions

#### Type 2 SCD with Time Hierarchy
```
Customer Dimension:
CustomerKey | CustomerID | Segment  | StartDate  | EndDate    | IsCurrent
1           | C001       | Standard | 2022-01-01 | 2023-12-31 | No
2           | C001       | Premium  | 2024-01-01 | 9999-12-31 | Yes

Query Considerations:
- As-was reporting: Use historical records
- As-is reporting: Use current records only
- Point-in-time: Filter by date range
```

### Alternate Hierarchies
Multiple navigation paths for same dimension:

```
Product Dimension:

Hierarchy 1 (Category):
All → Category → Subcategory → Product

Hierarchy 2 (Brand):
All → Brand → Product Line → Product

Hierarchy 3 (Price):
All → Price Range → Product

Usage:
- Different analysis perspectives
- User preference
- Different business questions
```

## DAX Hierarchy Patterns (Power BI)

### Path Functions
```dax
// Create parent-child hierarchy
Employee Path =
PATH(Employee[EmployeeID], Employee[ManagerID])

// Get level in hierarchy
Employee Level =
PATHLENGTH(Employee[Employee Path])

// Get specific ancestor
Employee Manager =
LOOKUPVALUE(
    Employee[Name],
    Employee[EmployeeID],
    PATHITEM(Employee[Employee Path], 2)
)

// Aggregate up hierarchy
Total for Branch =
CALCULATE(
    SUM(Sales[Amount]),
    FILTER(
        ALL(Employee),
        PATHCONTAINS(Employee[Employee Path], Employee[EmployeeID])
    )
)
```

## Hierarchy Design Best Practices

### 1. Logical Structure
```
Good Hierarchy:
- Natural business grouping
- Clear parent-child relationships
- Meaningful drill paths
- Consistent depth (when possible)

Poor Hierarchy:
- Arbitrary groupings
- Confusing relationships
- Illogical drill paths
- Inconsistent structure
```

### 2. Naming Conventions
```
User-Friendly Names:
✓ Product → Category → Subcategory → Product Name
✗ Prod → Cat → SubCat → ProdNm

Consistent Across Hierarchies:
✓ All Years → Year → Quarter → Month
✓ All Customers → Segment → Region → Customer
✗ All → Year → Qtr → Month (inconsistent)
```

### 3. Hierarchy Depth
```
Optimal Depth: 3-6 levels
- Too shallow (1-2): Limited analysis
- Too deep (7+): User confusion

Example (Good):
Geography: Region → Country → State → City (4 levels)

Example (Too Deep):
Org: Division → Group → Dept → Team → SubTeam → Unit → Employee (7 levels)
Consider: Dept → Team → Employee (3 levels)
```

### 4. Cardinality at Each Level
```
Balanced Cardinality:
Region: 4 members
└── Country: 20 members (5 per region)
    └── State: 100 members (5 per country)
        └── City: 1,000 members (10 per state)

Poor Design:
Level 1: 2 members (too few)
└── Level 2: 10,000 members (too many)
    └── Level 3: 10,001 members (barely different)
```

### 5. All Member Configuration
```
Include "All" Level:
✓ Enables grand totals
✓ Clear starting point
✓ Consistent navigation

Skip "All" Level:
✓ When totals don't make sense
✓ Distinct/Count measures
✓ Special analytical contexts
```

## Performance Considerations

### Hierarchy Optimization
```
Attribute Relationships:
- Define all relationships
- Use rigid when appropriate
- Enables aggregation design
- Improves query performance

Index Strategy:
- Index all hierarchy attributes
- Consider composite indexes
- Monitor usage patterns
```

### Query Performance
```
Efficient:
[Product].[Category].[Electronics]
- Direct attribute access
- Uses indexes

Less Efficient:
FILTER([Product].[Product].Members,
       [Product].[Category] = "Electronics")
- Scans all products
- Slower than direct access
```

## Testing Hierarchies

### Validation Checklist
```
□ All members appear in correct place
□ No orphaned members
□ Aggregations sum correctly
□ Drill-down works at all levels
□ Performance acceptable at all levels
□ Unknown members handled properly
□ Slowly changing dimensions tested
□ Edge cases validated
□ User feedback incorporated
```

### Common Issues
```
Orphaned Members:
- Member with no parent
- Fix: Add default/unknown parent

Incorrect Aggregation:
- Double counting
- Fix: Check many-to-many relationships

Performance Problems:
- Slow drill-down
- Fix: Add aggregations, check indexes

Missing Relationships:
- Attribute relationships not defined
- Fix: Add relationship definitions
```
