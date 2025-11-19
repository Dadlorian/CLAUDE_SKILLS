# Hierarchy Implementation Guide

## Creating User Hierarchies

### In SSAS Multidimensional

1. **Define Attributes**
```xml
<Dimension>
  <Attributes>
    <Attribute>
      <ID>Category</ID>
      <Name>Category</Name>
    </Attribute>
    <Attribute>
      <ID>Subcategory</ID>
      <Name>Subcategory</Name>
    </Attribute>
    <Attribute>
      <ID>Product</ID>
      <Name>Product</Name>
      <Usage>Key</Usage>
    </Attribute>
  </Attributes>
</Dimension>
```

2. **Create Hierarchy**
```xml
<Hierarchy>
  <ID>ProductHierarchy</ID>
  <Name>Product Hierarchy</Name>
  <AllMemberName>All Products</AllMemberName>
  <Levels>
    <Level>
      <ID>Category</ID>
      <Name>Category</Name>
      <SourceAttributeID>Category</SourceAttributeID>
    </Level>
    <Level>
      <ID>Subcategory</ID>
      <Name>Subcategory</Name>
      <SourceAttributeID>Subcategory</SourceAttributeID>
    </Level>
    <Level>
      <ID>Product</ID>
      <Name>Product</Name>
      <SourceAttributeID>Product</SourceAttributeID>
    </Level>
  </Levels>
</Hierarchy>
```

3. **Define Attribute Relationships**
```xml
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
      <RelationshipType>Rigid</RelationshipType>
    </AttributeRelationship>
  </AttributeRelationships>
</Attribute>
```

### In Power BI

1. Select columns in proper order
2. Right-click → Create Hierarchy
3. Drag remaining levels into hierarchy

```
Product Hierarchy:
├── Category
├── Subcategory
└── Product Name
```

## Parent-Child Hierarchies

### SQL Table Structure
```sql
CREATE TABLE Employee (
    EmployeeID INT PRIMARY KEY,
    EmployeeName VARCHAR(100),
    ManagerID INT,
    FOREIGN KEY (ManagerID) REFERENCES Employee(EmployeeID)
)
```

### DAX Implementation
```dax
// Create PATH
Employee Path = PATH(Employee[EmployeeID], Employee[ManagerID])

// Calculate level
Employee Level = PATHLENGTH([Employee Path])

// Get manager name
Manager =
LOOKUPVALUE(
    Employee[EmployeeName],
    Employee[EmployeeID],
    PATHITEM([Employee Path], [Employee Level] - 1)
)

// Aggregate down hierarchy
Total for Branch =
CALCULATE(
    SUM(Sales[Amount]),
    FILTER(
        ALL(Employee),
        PATHCONTAINS([Employee Path], Employee[EmployeeID])
    )
)
```

## Ragged Hierarchies

### Hide Empty Levels
```mdx
WITH MEMBER [Geography].[Org].[(All)].[MEMBER_CAPTION] AS
    IIF(
        IsLeaf([Geography].[Org].CurrentMember),
        [Geography].[Org].CurrentMember.Name,
        NULL
    )
```

### Power BI Approach
Use parent-child hierarchy with PATH functions

## Best Practices

1. **Logical Structure**
   - Natural business groupings
   - Clear parent-child relationships
   - 3-6 levels ideal

2. **Performance**
   - Define attribute relationships
   - Use rigid when appropriate
   - Index underlying columns

3. **User Experience**
   - Clear, business-friendly names
   - Consistent naming
   - Appropriate ALL member name

4. **Testing**
   - Verify all members appear
   - Test drill-down/up
   - Validate aggregations
   - Check for orphans
