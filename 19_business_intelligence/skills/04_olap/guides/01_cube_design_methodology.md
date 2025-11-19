# Cube Design Methodology: Step-by-Step Guide

## Overview

A systematic approach to designing OLAP cubes from requirements gathering through deployment.

## Phase 1: Requirements Gathering

### Step 1: Identify Business Questions

Document the analytical questions users need to answer:

```
Sales Analysis Questions:
1. What are our sales by product, region, and time period?
2. How do current sales compare to last year?
3. Which products are top performers?
4. What is our sales trend over time?
5. Which customers are most valuable?
6. What is our profit margin by product category?

Inventory Questions:
1. What is current inventory level by product and warehouse?
2. How many days of supply do we have?
3. What items are understocked or overstocked?

Budget Analysis:
1. What is actual vs. budget variance by department?
2. What is our forecast accuracy?
```

### Step 2: Identify Required Measures

```
Sales Measures:
- Sales Amount (Sum)
- Sales Quantity (Sum)
- Unit Price (Non-additive, use weighted average)
- Profit Amount (Sum)
- Profit Margin % (Calculated)
- Cost Amount (Sum)
- Order Count (Count distinct)
- Customer Count (Distinct count)

Inventory Measures:
- Inventory Level (Semi-additive: LastNonEmpty)
- Inventory Value (Semi-additive: LastNonEmpty)
- Reorder Point (Non-additive)
- Days on Hand (Calculated)

Budget Measures:
- Budget Amount (Sum)
- Forecast Amount (Sum)
- Variance (Calculated: Actual - Budget)
- Variance % (Calculated)
```

### Step 3: Identify Dimensions

```
Required Dimensions:
1. Date/Time
   - Calendar hierarchy: Year > Quarter > Month > Day
   - Fiscal hierarchy: Fiscal Year > Fiscal Quarter > Fiscal Month
   - Week hierarchy: Year > Week > Day

2. Product
   - Category > Subcategory > Product
   - Brand hierarchy
   - Supplier hierarchy

3. Customer
   - Customer Segment > Customer
   - Geographic hierarchy (through reference)
   - Customer Type (B2B, B2C)

4. Geography
   - Region > Country > State > City

5. Sales Channel
   - Channel Type > Channel > Store

6. Employee (for sales attribution)
   - Department > Manager > Sales Rep
```

### Step 4: Define Grain

```
Sales Fact Table Grain:
"One row per product per order line item"

Detail Level:
- OrderID: 123456
- OrderLineNumber: 1
- ProductID: P789
- Quantity: 5
- UnitPrice: $29.99
- Amount: $149.95

This grain allows:
✓ Product-level analysis
✓ Order-level analysis
✓ Customer purchasing patterns
✓ Time-series analysis
```

## Phase 2: Dimensional Modeling

### Step 1: Design Star Schema

```sql
-- Fact Table
CREATE TABLE FactSales (
    -- Keys
    DateKey INT NOT NULL,
    ProductKey INT NOT NULL,
    CustomerKey INT NOT NULL,
    EmployeeKey INT NOT NULL,
    ChannelKey INT NOT NULL,

    -- Degenerate dimensions
    OrderID VARCHAR(20) NOT NULL,
    OrderLineNumber INT NOT NULL,

    -- Measures
    SalesAmount DECIMAL(18,2) NOT NULL,
    SalesQuantity INT NOT NULL,
    UnitPrice DECIMAL(18,2) NOT NULL,
    CostAmount DECIMAL(18,2) NOT NULL,
    DiscountAmount DECIMAL(18,2) NULL,

    -- Audit
    LoadDate DATETIME NOT NULL DEFAULT GETDATE(),

    -- Constraints
    CONSTRAINT PK_FactSales PRIMARY KEY CLUSTERED (DateKey, OrderID, OrderLineNumber),
    CONSTRAINT FK_FactSales_Date FOREIGN KEY (DateKey) REFERENCES DimDate(DateKey),
    CONSTRAINT FK_FactSales_Product FOREIGN KEY (ProductKey) REFERENCES DimProduct(ProductKey),
    CONSTRAINT FK_FactSales_Customer FOREIGN KEY (CustomerKey) REFERENCES DimCustomer(CustomerKey),
    CONSTRAINT FK_FactSales_Employee FOREIGN KEY (EmployeeKey) REFERENCES DimEmployee(EmployeeKey),
    CONSTRAINT FK_FactSales_Channel FOREIGN KEY (ChannelKey) REFERENCES DimChannel(ChannelKey)
);

-- Dimension Tables
CREATE TABLE DimProduct (
    ProductKey INT PRIMARY KEY IDENTITY(1,1),
    ProductID VARCHAR(50) UNIQUE NOT NULL,
    ProductName VARCHAR(200) NOT NULL,
    Category VARCHAR(100) NOT NULL,
    Subcategory VARCHAR(100) NOT NULL,
    Brand VARCHAR(100) NOT NULL,
    UnitOfMeasure VARCHAR(20),
    StandardCost DECIMAL(18,2),
    ListPrice DECIMAL(18,2),
    -- SCD Type 2
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    IsCurrent BIT NOT NULL
);
```

### Step 2: Design Hierarchies

```
Product Dimension Hierarchies:

1. Category Hierarchy:
   All Products
   └── Category (10 members)
       └── Subcategory (50 members)
           └── Product (1,000 members)

2. Brand Hierarchy:
   All Products
   └── Brand (25 members)
       └── Product (1,000 members)

Attribute Relationships:
Product → Subcategory (Many:One, Rigid)
Subcategory → Category (Many:One, Rigid)
Product → Brand (Many:One, Flexible)
```

### Step 3: Implement SCD Strategy

```sql
-- SCD Type 2 for Product dimension
-- Track price changes over time

-- Initial product
INSERT INTO DimProduct (
    ProductID, ProductName, Category, Subcategory,
    Brand, StandardCost, ListPrice,
    StartDate, EndDate, IsCurrent
)
VALUES (
    'PROD001', 'Laptop Pro 15', 'Computers', 'Laptops',
    'TechBrand', 800.00, 1299.99,
    '2024-01-01', '9999-12-31', 1
);

-- Price change - add new row, update old
-- Step 1: Close current record
UPDATE DimProduct
SET EndDate = '2024-06-30', IsCurrent = 0
WHERE ProductID = 'PROD001' AND IsCurrent = 1;

-- Step 2: Insert new record
INSERT INTO DimProduct (
    ProductID, ProductName, Category, Subcategory,
    Brand, StandardCost, ListPrice,
    StartDate, EndDate, IsCurrent
)
VALUES (
    'PROD001', 'Laptop Pro 15', 'Computers', 'Laptops',
    'TechBrand', 750.00, 1199.99,  -- New prices
    '2024-07-01', '9999-12-31', 1
);
```

## Phase 3: Cube Definition

### Step 1: Create SSAS Project

```powershell
# Create new SSAS Multidimensional project
# In Visual Studio:
# File > New > Project > Analysis Services Multidimensional Project
```

### Step 2: Define Data Source

```xml
<DataSource xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <ID>SalesDB</ID>
  <Name>Sales Database</Name>
  <ConnectionString>
    Provider=SQLNCLI11;
    Data Source=SQLServer;
    Integrated Security=SSPI;
    Initial Catalog=SalesDW
  </ConnectionString>
  <ImpersonationInfo>
    <ImpersonationMode>ImpersonateServiceAccount</ImpersonationMode>
  </ImpersonationInfo>
</DataSource>
```

### Step 3: Create Data Source View

```xml
<DataSourceView>
  <ID>SalesDSV</ID>
  <Name>Sales Data Source View</Name>
  <Tables>
    <TableDef>
      <TableID>dbo_FactSales</TableID>
      <SourceID>SalesDB</SourceID>
    </TableDef>
    <TableDef>
      <TableID>dbo_DimDate</TableID>
    </TableDef>
    <TableDef>
      <TableID>dbo_DimProduct</TableID>
    </TableDef>
    <!-- Additional tables -->
  </Tables>
  <Relationships>
    <Relationship>
      <ParentTableID>dbo_DimProduct</ParentTableID>
      <ParentColumnID>ProductKey</ParentColumnID>
      <ChildTableID>dbo_FactSales</ChildTableID>
      <ChildColumnID>ProductKey</ChildColumnID>
    </Relationship>
    <!-- Additional relationships -->
  </Relationships>
</DataSourceView>
```

### Step 4: Build Dimensions

```csharp
// Create Date dimension
var dateDim = new Dimension
{
    ID = "Date",
    Name = "Date",
    Source = new DataSourceViewBinding { DataSourceViewID = "SalesDSV" },
    Type = DimensionType.Time
};

// Add attributes
var dateKeyAttr = new DimensionAttribute
{
    ID = "Date",
    Name = "Date",
    Usage = AttributeUsage.Key,
    Type = AttributeType.Days,
    KeyColumns = { new DataItem { Source = new ColumnBinding { TableID = "DimDate", ColumnID = "DateKey" } } },
    NameColumn = new DataItem { Source = new ColumnBinding { TableID = "DimDate", ColumnID = "Date" } }
};

dateDim.Attributes.Add(dateKeyAttr);

// Add Year attribute
var yearAttr = new DimensionAttribute
{
    ID = "Year",
    Name = "Year",
    KeyColumns = { new DataItem { Source = new ColumnBinding { TableID = "DimDate", ColumnID = "Year" } } }
};

dateDim.Attributes.Add(yearAttr);

// Create hierarchy
var calendarHierarchy = new Hierarchy
{
    ID = "Calendar",
    Name = "Calendar",
    AllMemberName = "All Years"
};

calendarHierarchy.Levels.Add(new Level { SourceAttributeID = "Year", Name = "Year" });
calendarHierarchy.Levels.Add(new Level { SourceAttributeID = "Quarter", Name = "Quarter" });
calendarHierarchy.Levels.Add(new Level { SourceAttributeID = "Month", Name = "Month" });
calendarHierarchy.Levels.Add(new Level { SourceAttributeID = "Date", Name = "Date" });

dateDim.Hierarchies.Add(calendarHierarchy);
```

### Step 5: Define Measure Groups

```xml
<MeasureGroup>
  <ID>Sales</ID>
  <Name>Sales</Name>
  <Measures>
    <Measure>
      <ID>SalesAmount</ID>
      <Name>Sales Amount</Name>
      <AggregateFunction>Sum</AggregateFunction>
      <FormatString>Currency</FormatString>
      <Source>
        <Source xsi:type="ColumnBinding">
          <TableID>dbo_FactSales</TableID>
          <ColumnID>SalesAmount</ColumnID>
        </Source>
      </Source>
    </Measure>
    <Measure>
      <ID>SalesQuantity</ID>
      <Name>Sales Quantity</Name>
      <AggregateFunction>Sum</AggregateFunction>
      <FormatString>#,##0</FormatString>
    </Measure>
    <!-- Additional measures -->
  </Measures>
  <StorageMode>Molap</StorageMode>
  <ProcessingPriority>0</ProcessingPriority>
</MeasureGroup>
```

### Step 6: Add Calculated Measures

```mdx
CREATE MEMBER CURRENTCUBE.[Measures].[Profit]
AS [Measures].[Sales Amount] - [Measures].[Cost Amount],
FORMAT_STRING = "Currency",
VISIBLE = 1;

CREATE MEMBER CURRENTCUBE.[Measures].[Profit Margin %]
AS
  IIF(
    [Measures].[Sales Amount] = 0,
    NULL,
    ([Measures].[Profit] / [Measures].[Sales Amount])
  ),
FORMAT_STRING = "Percent",
VISIBLE = 1;

CREATE MEMBER CURRENTCUBE.[Measures].[Sales YoY %]
AS
  IIF(
    ([Measures].[Sales Amount], PARALLELPERIOD([Date].[Calendar].[Year], 1)) = 0,
    NULL,
    (
      ([Measures].[Sales Amount] - ([Measures].[Sales Amount], PARALLELPERIOD([Date].[Calendar].[Year], 1))) /
      ([Measures].[Sales Amount], PARALLELPERIOD([Date].[Calendar].[Year], 1))
    )
  ),
FORMAT_STRING = "Percent",
VISIBLE = 1;
```

## Phase 4: Optimization

### Step 1: Define Attribute Relationships

```xml
<Dimension>
  <Attributes>
    <Attribute>
      <ID>Product</ID>
      <AttributeRelationships>
        <AttributeRelationship>
          <AttributeID>Subcategory</AttributeID>
          <RelationshipType>Rigid</RelationshipType>
        </AttributeRelationship>
        <AttributeRelationship>
          <AttributeID>Brand</AttributeID>
          <RelationshipType>Flexible</RelationshipType>
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
  </Attributes>
</Dimension>
```

### Step 2: Design Aggregations

```powershell
# Using Aggregation Design Wizard
# Or programmatically:

$server = New-Object Microsoft.AnalysisServices.Server
$server.Connect("localhost")

$db = $server.Databases["SalesCube"]
$cube = $db.Cubes["Sales"]
$mg = $cube.MeasureGroups["Sales"]

# Create aggregation design
$aggDesign = $mg.AggregationDesigns.Add("SalesAggregation", "Sales Aggregation Design")

# Design with 30% performance gain target
$aggDesign.DesignAggregations(
    0,      # Use storage limit = false
    30,     # 30% performance improvement target
    $null   # Use current query patterns
)

$aggDesign.Update()
$server.Disconnect()

Write-Host "Aggregation design complete"
```

### Step 3: Implement Partitioning

```powershell
# Create monthly partitions
$server = New-Object Microsoft.AnalysisServices.Server
$server.Connect("localhost")

$db = $server.Databases["SalesCube"]
$cube = $db.Cubes["Sales"]
$mg = $cube.MeasureGroups["Sales"]

# Remove default partition
if ($mg.Partitions.Count -gt 0) {
    $mg.Partitions[0].Drop()
}

# Create partition for each month in 2024
for ($month = 1; $month -le 12; $month++) {
    $monthName = (Get-Culture).DateTimeFormat.GetMonthName($month)
    $partitionName = "Sales_2024_" + $month.ToString("00")

    $partition = New-Object Microsoft.AnalysisServices.Partition
    $partition.Name = $partitionName
    $partition.ID = $partitionName
    $partition.StorageMode = [Microsoft.AnalysisServices.StorageMode]::Molap

    $queryBinding = New-Object Microsoft.AnalysisServices.QueryBinding
    $queryBinding.DataSourceID = "SalesDB"
    $queryBinding.QueryDefinition = @"
        SELECT *
        FROM FactSales
        WHERE DateKey >= 2024$(${month}.ToString('00'))01
          AND DateKey < 2024$(if ($month -eq 12) { '2025' + '01' } else { '2024' + ($month + 1).ToString('00') })01
"@

    $partition.Source = $queryBinding
    $partition.AggregationDesignID = "SalesAggregation"

    $mg.Partitions.Add($partition)
    $partition.Update()

    Write-Host "Created partition: $partitionName"
}

$server.Disconnect()
```

## Phase 5: Security

### Step 1: Define Roles

```xml
<Role>
  <ID>SalesManagers</ID>
  <Name>Sales Managers</Name>
  <Members>
    <Member>
      <Name>DOMAIN\SalesManagers</Name>
    </Member>
  </Members>
  <Permissions>
    <DatabasePermission>
      <DatabaseID>SalesCube</DatabaseID>
      <Read>Allowed</Read>
    </DatabasePermission>
  </Permissions>
</Role>
```

### Step 2: Implement Dimension Security

```xml
<Role>
  <ID>RegionalManagers</ID>
  <Name>Regional Sales Managers</Name>
  <DimensionPermissions>
    <DimensionPermission>
      <CubeDimensionID>Geography</CubeDimensionID>
      <Read>Allowed</Read>
      <AttributePermissions>
        <AttributePermission>
          <AttributeID>Region</AttributeID>
          <AllowedSet>
            <![CDATA[
              STRTOMEMBER(
                "[Geography].[Region].[" +
                USERNAME() + "]"
              )
            ]]>
          </AllowedSet>
        </AttributePermission>
      </AttributePermissions>
    </DimensionPermission>
  </DimensionPermissions>
</Role>
```

## Phase 6: Testing and Deployment

### Step 1: Unit Testing

```mdx
-- Test basic measures
SELECT
    [Measures].[Sales Amount],
    [Measures].[Sales Quantity],
    [Measures].[Profit]
ON COLUMNS
FROM [Sales];

-- Test calculations
WITH MEMBER [Measures].[Test Profit Margin] AS
    [Measures].[Profit] / [Measures].[Sales Amount],
    FORMAT_STRING = "Percent"

SELECT
    {[Measures].[Profit Margin %], [Measures].[Test Profit Margin]} ON COLUMNS,
    [Product].[Category].MEMBERS ON ROWS
FROM [Sales];

-- Test time intelligence
SELECT
    {
        [Measures].[Sales Amount],
        [Measures].[Sales LY],
        [Measures].[Sales YoY %]
    } ON COLUMNS,
    [Date].[Calendar].[Month].MEMBERS ON ROWS
FROM [Sales]
WHERE [Date].[Calendar].[2024];
```

### Step 2: Performance Testing

```powershell
# Load test script
$queries = @(
    "SELECT [Measures].[Sales Amount] ON 0 FROM [Sales]",
    "SELECT [Product].[Category].MEMBERS ON 0 FROM [Sales]",
    # ... more queries
)

$results = @()

foreach ($query in $queries) {
    $startTime = Get-Date

    $server.ExecuteCaptureLog($query, $true)

    $duration = (Get-Date) - $startTime

    $results += @{
        Query = $query.Substring(0, [Math]::Min(50, $query.Length))
        Duration = $duration.TotalMilliseconds
    }
}

$results | Format-Table -Auto
```

### Step 3: Deploy to Production

See [Deployment Strategies](./13_deployment_strategies.md) for detailed deployment procedures.

## Best Practices Checklist

```
Requirements Phase:
□ Business questions documented
□ Stakeholders identified and interviewed
□ Key metrics defined
□ Data sources identified
□ Access requirements documented

Design Phase:
□ Star schema designed
□ Grain clearly defined
□ Dimensions identified
□ Hierarchies defined
□ SCD strategy chosen
□ Conformed dimensions identified

Implementation Phase:
□ Dimensions created with proper attributes
□ Hierarchies implemented
□ Attribute relationships defined
□ Measures defined with correct aggregation
□ Calculated measures created
□ Security roles defined

Optimization Phase:
□ Aggregations designed
□ Partitioning implemented
□ Indexes created on fact tables
□ Processing strategy defined
□ Performance tested

Deployment Phase:
□ Deployment script created
□ Testing completed
□ Documentation written
□ Training provided
□ Go-live plan executed
```
