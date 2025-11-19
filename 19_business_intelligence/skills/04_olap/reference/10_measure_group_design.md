# Measure Group Design

## Overview

Measure groups organize related measures and define their relationship to dimensions, serving as the foundation for fact table representation in OLAP cubes.

## Measure Group Fundamentals

### Definition
A measure group represents a fact table and contains:
- **Measures**: Numeric values to analyze
- **Dimension Relationships**: How dimensions relate to this fact
- **Partitions**: Data storage segments
- **Aggregations**: Pre-computed summaries

### Structure
```
Measure Group: Sales
├── Measures
│   ├── Sales Amount (Sum)
│   ├── Sales Quantity (Sum)
│   ├── Unit Price (Average)
│   └── Order Count (Count)
├── Dimensions
│   ├── Date (Regular)
│   ├── Product (Regular)
│   ├── Customer (Regular)
│   └── Geography (Referenced)
├── Partitions
│   ├── Sales_2024_01
│   ├── Sales_2024_02
│   └── Sales_2024_03
└── Aggregations
    └── SalesAggregation
```

## Measure Types and Aggregation Functions

### Additive Measures
Sum across all dimensions:

```xml
<Measure>
  <ID>SalesAmount</ID>
  <Name>Sales Amount</Name>
  <AggregateFunction>Sum</AggregateFunction>
  <FormatString>Currency</FormatString>
  <Source>
    <Source xsi:type="ColumnBinding">
      <TableID>FactSales</TableID>
      <ColumnID>SalesAmount</ColumnID>
    </Source>
  </Source>
</Measure>
```

Examples:
- Sales Amount
- Quantity Sold
- Cost
- Profit
- Order Count

### Semi-Additive Measures
Sum across some dimensions, but not all (typically not time):

```xml
<Measure>
  <ID>AccountBalance</ID>
  <Name>Account Balance</Name>
  <AggregateFunction>LastNonEmpty</AggregateFunction>
  <Source>
    <Source xsi:type="ColumnBinding">
      <TableID>FactAccount</TableID>
      <ColumnID>Balance</ColumnID>
    </Source>
  </Source>
</Measure>
```

Semi-additive functions:
- **FirstChild**: First time period value
- **LastChild**: Last time period value
- **FirstNonEmpty**: First non-null time period
- **LastNonEmpty**: Last non-null time period (most common)
- **AverageOfChildren**: Average across time
- **ByAccount**: Uses account type (debit/credit)

Examples:
- Account Balance (LastNonEmpty)
- Inventory Level (LastNonEmpty)
- Head Count (LastNonEmpty)
- Stock Price (LastNonEmpty)

### Non-Additive Measures
Cannot be summed:

```xml
<Measure>
  <ID>UnitPrice</ID>
  <Name>Unit Price</Name>
  <AggregateFunction>None</AggregateFunction>
  <Source>
    <Source xsi:type="ColumnBinding">
      <TableID>FactSales</TableID>
      <ColumnID>UnitPrice</ColumnID>
    </Source>
  </Source>
</Measure>
```

Handle with calculated measures:
```dax
Weighted Avg Price =
DIVIDE(
    SUM(Sales[Amount]),
    SUM(Sales[Quantity]),
    0
)

Profit Margin % =
DIVIDE(
    SUM(Sales[Profit]),
    SUM(Sales[Revenue]),
    0
)
```

Examples:
- Ratios
- Percentages
- Rates
- Prices (unit prices)

### Distinct Count Measures
Count unique values:

```xml
<Measure>
  <ID>CustomerCount</ID>
  <Name>Customer Count</Name>
  <AggregateFunction>DistinctCount</AggregateFunction>
  <Source>
    <Source xsi:type="ColumnBinding">
      <TableID>FactSales</TableID>
      <ColumnID>CustomerID</ColumnID>
    </Source>
  </Source>
</Measure>
```

Special considerations:
- Separate measure group recommended
- Performance impact
- Cannot be pre-aggregated
- Uses more memory

## Dimension Relationships

### Regular Relationship
Direct foreign key:

```xml
<Dimension>
  <CubeDimensionID>Date</CubeDimensionID>
  <RelationshipType>Regular</RelationshipType>
  <Attributes>
    <Attribute>
      <AttributeID>Date</AttributeID>
      <KeyColumns>
        <KeyColumn>
          <Source xsi:type="ColumnBinding">
            <TableID>FactSales</TableID>
            <ColumnID>DateKey</ColumnID>
          </Source>
        </KeyColumn>
      </KeyColumns>
    </Attribute>
  </Attributes>
</Dimension>
```

Example:
```
FactSales.DateKey → DimDate.DateKey (FK)
```

### Referenced Relationship
Indirect through another dimension:

```xml
<Dimension>
  <CubeDimensionID>Geography</CubeDimensionID>
  <RelationshipType>Referenced</RelationshipType>
  <IntermediateCubeDimensionID>Customer</IntermediateCubeDimensionID>
  <IntermediateGranularityAttributeID>CustomerKey</IntermediateGranularityAttributeID>
  <Materialized>true</Materialized>
</Dimension>
```

Example:
```
FactSales → DimCustomer → DimGeography
FactSales.CustomerKey → DimCustomer.CustomerKey
DimCustomer.GeographyKey → DimGeography.GeographyKey
```

Benefits of materialization:
- Faster queries (pre-joined)
- More storage
- Longer processing time

### Many-to-Many Relationship
Multiple relationships through bridge table:

```xml
<Dimension>
  <CubeDimensionID>Account</CubeDimensionID>
  <RelationshipType>ManyToMany</RelationshipType>
  <IntermediateMeasureGroupID>AccountSalesBridge</IntermediateMeasureGroupID>
</Dimension>
```

Example:
```
Sales can have multiple accounts
Accounts can have multiple sales
Bridge: FactAccountSales (SalesKey, AccountKey)
```

### Data Mining Relationship
Based on data mining model:

```xml
<Dimension>
  <CubeDimensionID>CustomerSegment</CubeDimensionID>
  <RelationshipType>DataMining</RelationshipType>
  <DataMiningModelID>CustomerClustering</DataMiningModelID>
</Dimension>
```

### No Relationship
Dimension not related to this measure group:

```xml
<Dimension>
  <CubeDimensionID>Product</CubeDimensionID>
  <RelationshipType>NoRelationship</RelationshipType>
</Dimension>
```

Result: Measure repeats same value across all members

## Multiple Measure Groups

### Design Patterns

#### Pattern 1: Multiple Fact Tables at Same Grain
```
Measure Group: Sales (Order line level)
- Sales Amount
- Quantity
- Product, Customer, Date

Measure Group: Returns (Return line level)
- Return Amount
- Return Quantity
- Product, Customer, Date

Measure Group: Costs (Order line level)
- Product Cost
- Shipping Cost
- Product, Date

Shared dimensions:
- DimDate (conformed)
- DimProduct (conformed)
- DimCustomer (conformed)
```

#### Pattern 2: Different Grains
```
Measure Group: Sales (Transaction level - daily)
- Sales Amount
- Dimensions: Date (day), Product, Customer

Measure Group: Budget (Monthly level)
- Budget Amount
- Dimensions: Date (month), Product Category

Measure Group: Forecast (Quarterly level)
- Forecast Amount
- Dimensions: Date (quarter), Product Category

Query Behavior:
- Different granularities display at their level
- No automatic interpolation
```

#### Pattern 3: Snapshot Facts
```
Measure Group: Sales (Transactional)
- Sales Amount (Additive)
- Date, Product, Customer

Measure Group: Inventory (Snapshot)
- Inventory Level (Semi-additive: LastNonEmpty)
- Date, Product, Warehouse

Measure Group: Account Balance (Snapshot)
- Balance (Semi-additive: LastNonEmpty)
- Date, Account, Customer
```

## Distinct Count Optimization

### Separate Measure Group
```
Measure Group: Sales
- Sales Amount
- Quantity
- Cost
(Regular measures)

Measure Group: Sales Distinct Counts
- Customer Count (DistinctCount on CustomerID)
- Product Count (DistinctCount on ProductID)
- Order Count (DistinctCount on OrderID)

Benefits:
- Isolates performance impact
- Separate processing
- Optimized aggregations
```

### Partition Strategy
```xml
<MeasureGroup>
  <ID>SalesDistinctCount</ID>
  <AggregationPrefix>DistCount</AggregationPrefix>
  <Partitions>
    <!-- More aggressive partitioning -->
    <Partition>
      <ID>DC_2024_01_Week1</ID>
      <StorageMode>Molap</StorageMode>
      <!-- Weekly partitions for better performance -->
    </Partition>
  </Partitions>
</MeasureGroup>
```

## Measure Group Properties

### Storage Mode
```xml
<MeasureGroup>
  <ID>Sales</ID>
  <StorageMode>Molap</StorageMode>
  <!-- or Rolap, Holap, InMemory -->
</MeasureGroup>
```

### Processing Priority
```xml
<MeasureGroup>
  <ID>Sales</ID>
  <ProcessingPriority>10</ProcessingPriority>
  <!-- Higher = processed first -->
</MeasureGroup>
```

### Ignore Unrelated Dimensions
```xml
<MeasureGroup>
  <ID>Sales</ID>
  <IgnoreUnrelatedDimensions>false</IgnoreUnrelatedDimensions>
  <!-- true = repeat value, false = NULL -->
</MeasureGroup>
```

### Processing Mode
```xml
<MeasureGroup>
  <ID>Sales</ID>
  <ProcessingMode>Regular</ProcessingMode>
  <!-- Regular or LazyOptimization -->
</MeasureGroup>
```

## Calculated Measures in Measure Groups

### MDX Calculated Measures
```mdx
WITH MEMBER [Measures].[Profit] AS
    [Measures].[Sales Amount] - [Measures].[Cost],
    FORMAT_STRING = "Currency",
    VISIBLE = 1

MEMBER [Measures].[Profit Margin %] AS
    IIF(
        [Measures].[Sales Amount] = 0,
        NULL,
        [Measures].[Profit] / [Measures].[Sales Amount]
    ),
    FORMAT_STRING = "Percent",
    VISIBLE = 1
```

### Scope Assignments
```mdx
-- Allocate budget down to products
SCOPE([Measures].[Budget]);
    SCOPE([Product].[Product].MEMBERS);
        THIS = [Measures].[Budget] /
               COUNT([Product].[Product].CURRENTMEMBER.SIBLINGS);
    END SCOPE;
END SCOPE;
```

## DAX Measures (Tabular Models)

### Explicit Measures
```dax
Sales Amount = SUM(Sales[Amount])

Profit = SUM(Sales[Amount]) - SUM(Sales[Cost])

Profit Margin % =
DIVIDE([Profit], [Sales Amount], 0)

YoY Growth % =
VAR CurrentYear = [Sales Amount]
VAR PriorYear = CALCULATE([Sales Amount], SAMEPERIODLASTYEAR('Date'[Date]))
RETURN
    DIVIDE(CurrentYear - PriorYear, PriorYear, 0)
```

### Implicit Measures
```dax
-- Power BI creates automatically from aggregations
-- Sum of Amount, Count of Orders, etc.
-- Visible in Fields list but not in model
```

## Measure Group Best Practices

### 1. Grain Definition
```
✓ Clearly document grain
Example: "Order Line Level - One row per product per order"

✓ Ensure all measures match grain
- Sales Amount ✓ (order line level)
- Quantity ✓ (order line level)
- Order Total ✗ (order level - use calculated measure)

✓ Create separate measure groups for different grains
```

### 2. Measure Naming
```
✓ Descriptive, business-friendly names
✓ Include units/context where needed
✓ Consistent across measure groups

Examples:
✓ Sales Amount
✓ Sales Quantity
✓ Average Unit Price
✓ Customer Count (Distinct)

✗ Amt
✗ Qty
✗ Sum_Sales
```

### 3. Aggregation Function Selection
```
Choose appropriate function:
- Sales, Revenue, Cost → Sum
- Inventory, Balance → LastNonEmpty
- Ratios, Percentages → None (use calculated)
- Unique counts → DistinctCount
- Prices → None (use weighted average calc)
```

### 4. Format Strings
```xml
<Measure>
  <FormatString>Currency</FormatString>
  <!-- or "Percent", "#,##0", "#,##0.00", etc. -->
</Measure>
```

### 5. Performance Optimization
```
- Separate distinct count measures
- Use appropriate storage mode
- Design efficient aggregations
- Partition large measure groups
- Monitor processing times
- Index fact table columns
```

### 6. Documentation
```
Document each measure group:
- Business purpose
- Data source (fact table)
- Grain definition
- Refresh frequency
- Related measure groups
- Special considerations
```

## Testing and Validation

### Data Quality Checks
```sql
-- Verify measure totals
SELECT
    SUM(SalesAmount) as TotalSales,
    SUM(Quantity) as TotalQuantity,
    COUNT(DISTINCT CustomerID) as UniqueCustomers
FROM FactSales;

-- Check for NULLs in measures
SELECT COUNT(*)
FROM FactSales
WHERE SalesAmount IS NULL OR Quantity IS NULL;

-- Validate dimension relationships
SELECT COUNT(*)
FROM FactSales f
LEFT JOIN DimProduct p ON f.ProductKey = p.ProductKey
WHERE p.ProductKey IS NULL;
```

### MDX Validation Queries
```mdx
-- Verify measure totals match source
SELECT
    [Measures].[Sales Amount],
    [Measures].[Sales Quantity]
ON COLUMNS
FROM [Sales];

-- Check distinct count accuracy
WITH MEMBER [Measures].[Test Customer Count] AS
    COUNT(
        NONEMPTY(
            [Customer].[Customer].MEMBERS,
            [Measures].[Sales Amount]
        )
    )
SELECT
    [Measures].[Customer Count],
    [Measures].[Test Customer Count]
ON COLUMNS
FROM [Sales];
```

### Performance Testing
```
Test scenarios:
□ Simple aggregation query (< 1 second)
□ Complex calculation (< 3 seconds)
□ Large dataset scan (< 10 seconds)
□ Distinct count query (< 5 seconds)
□ Many-to-many query (< 5 seconds)
□ Cross measure group query (< 3 seconds)
```

## Common Issues and Solutions

### Issue: Incorrect Totals
```
Problem: Totals don't match source data
Solutions:
1. Verify aggregation function
2. Check for duplicate records
3. Validate dimension relationships
4. Review calculated measure logic
5. Check for filtering in partitions
```

### Issue: Slow Distinct Count
```
Problem: Distinct count queries very slow
Solutions:
1. Create separate measure group
2. More aggressive partitioning
3. Ensure proper indexing
4. Consider approximation alternatives
5. Review user requirements (really needed?)
```

### Issue: Many-to-Many Performance
```
Problem: Queries with M:M relationships slow
Solutions:
1. Materialize intermediate results
2. Optimize bridge table
3. Create aggregations
4. Consider alternative design
5. Limit scope of M:M relationship
```
