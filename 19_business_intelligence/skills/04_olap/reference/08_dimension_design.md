# Dimension Design Best Practices

## Overview

Comprehensive guide to designing effective dimensions for OLAP cubes, covering modeling approaches, optimization techniques, and common patterns.

## Dimension Types

### Conformed Dimensions
Shared across multiple fact tables:

```
DimCustomer (Conformed):
├── Used by FactSales
├── Used by FactReturns
├── Used by FactServiceCalls
└── Used by FactWebsite Visits

Benefits:
- Consistent reporting across facts
- Single source of truth
- Easier maintenance
- Cross-fact analysis
```

### Degenerate Dimensions
Dimension stored in fact table (no separate dimension table):

```
FactOrders:
- OrderID (Degenerate Dimension)
- OrderLineNumber (Degenerate Dimension)
- ProductKey (FK to DimProduct)
- CustomerKey (FK to DimCustomer)
- OrderDate (FK to DimDate)
- Quantity
- Amount

Usage:
- Transaction identifiers
- Order numbers, invoice numbers
- No descriptive attributes
- Minimal storage overhead
```

### Junk Dimensions
Grouping of low-cardinality flags and indicators:

```
Instead of:
FactSales with individual flags:
- IsPromotional (Y/N)
- PaymentType (Cash/Credit/Other)
- IsFirstPurchase (Y/N)
- ShipMethod (Ground/Air/Express)

Create DimSalesAttributes (Junk):
SalesAttributeKey | IsPromotional | PaymentType | IsFirstPurchase | ShipMethod
1                 | Y             | Cash        | Y               | Ground
2                 | Y             | Cash        | Y               | Air
3                 | Y             | Cash        | N               | Ground
...

Benefits:
- Reduces fact table width
- Improves query performance
- Easier to analyze combinations
```

### Role-Playing Dimensions
Single dimension used multiple times with different meanings:

```
DimDate (single physical table):
Used as:
- Order Date
- Ship Date
- Delivery Date
- Payment Date

Implementation:
- Create database views
- Create cube dimension roles
- Or use single dimension with role context
```

### Outrigger Dimensions
Dimension normalized to another dimension:

```
DimCustomer:
- CustomerKey (PK)
- CustomerName
- GeographyKey (FK to DimGeography)

DimGeography (Outrigger):
- GeographyKey (PK)
- City
- State
- Country
- Region

Considerations:
- More normalized design
- Additional join in queries
- Use for large, reusable attributes
```

## Slowly Changing Dimensions (SCD)

### Type 0: Fixed
Dimension values never change:

```
DimDate:
- DateKey: 20240115
- Date: 2024-01-15
- Year: 2024
- Month: January

These values are immutable
```

### Type 1: Overwrite
Latest values overwrite, no history:

```
Before:
CustomerKey | CustomerName | City       | CurrentFlag
1           | John Smith   | Seattle    | Y

After (customer moves):
CustomerKey | CustomerName | City       | CurrentFlag
1           | John Smith   | San Diego  | Y

Result:
- All historical facts show new city
- No history of previous values
- Simplest approach
- Use when history not needed
```

### Type 2: Add New Row
Full history with multiple rows:

```
Before:
CustomerKey | CustomerID | City    | StartDate  | EndDate    | IsCurrent
1           | C001       | Seattle | 2020-01-01 | 9999-12-31 | Yes

After (customer moves):
CustomerKey | CustomerID | City      | StartDate  | EndDate    | IsCurrent
1           | C001       | Seattle   | 2020-01-01 | 2024-01-14 | No
2           | C001       | San Diego | 2024-01-15 | 9999-12-31 | Yes

Query Patterns:
-- Current value only
WHERE IsCurrent = 'Yes'

-- Historical (point-in-time)
WHERE OrderDate BETWEEN StartDate AND EndDate

-- All history
No filter needed

Benefits:
- Complete history
- Point-in-time accuracy
- Most common for critical attributes
```

### Type 3: Add New Column
Limited history with additional columns:

```
CustomerKey | CustomerName | CurrentCity | PreviousCity | ChangeDate
1           | John Smith   | San Diego   | Seattle      | 2024-01-15

Limitations:
- Only one previous value
- Limited history depth
- Use for specific requirements only
```

### Type 4: Historical Table
Separate table for historical values:

```
DimCustomer (Current):
CustomerKey | CustomerID | City      | IsCurrent
1           | C001       | San Diego | Yes

DimCustomerHistory:
HistoryKey | CustomerID | City    | StartDate  | EndDate
1          | C001       | Seattle | 2020-01-01 | 2024-01-14
2          | C001       | San Diego | 2024-01-15 | 9999-12-31

Usage:
- Separate history tracking
- Keep current dimension small
- Complex queries for history
```

### Type 6: Hybrid (1+2+3)
Combination approach:

```
CustomerKey | CustomerID | CurrentCity | PreviousCity | HistoricalCity | StartDate  | EndDate    | IsCurrent
1           | C001       | Seattle     | NULL         | NULL           | 2020-01-01 | 2022-12-31 | No
2           | C001       | Portland    | Seattle      | Seattle        | 2023-01-01 | 2024-01-14 | No
3           | C001       | San Diego   | Portland     | Seattle        | 2024-01-15 | 9999-12-31 | Yes

Features:
- Current value in all rows (Type 1)
- Historical rows (Type 2)
- Previous value column (Type 3)
```

## Dimension Attributes

### Types of Attributes

#### Key Attribute
Unique identifier:
```xml
<Attribute>
  <ID>CustomerKey</ID>
  <Name>Customer Key</Name>
  <Type>KeyAttribute</Type>
  <Usage>Key</Usage>
  <KeyColumns>
    <KeyColumn>
      <Source>CustomerKey</Source>
    </KeyColumn>
  </KeyColumns>
</Attribute>
```

#### Member Name
Display attribute:
```xml
<Attribute>
  <ID>CustomerName</ID>
  <Name>Customer Name</Name>
  <NameColumn>
    <Source>CustomerName</Source>
  </NameColumn>
</Attribute>
```

#### Member Properties
Additional descriptive attributes:
```
Customer attributes:
- Email (Property)
- Phone (Property)
- Segment (Hierarchy level)
- Credit Limit (Property)
- Registration Date (Property)

Usage:
- Filtering
- Display in reports
- Drill-through details
```

### Attribute Relationships

```xml
<Dimension>
  <Attributes>
    <Attribute>
      <ID>City</ID>
      <AttributeRelationships>
        <AttributeRelationship>
          <AttributeID>State</AttributeID>
          <RelationshipType>Rigid</RelationshipType>
        </AttributeRelationship>
      </AttributeRelationships>
    </Attribute>
    <Attribute>
      <ID>State</ID>
      <AttributeRelationships>
        <AttributeRelationship>
          <AttributeID>Country</AttributeID>
          <RelationshipType>Rigid</RelationshipType>
        </AttributeRelationship>
      </AttributeRelationships>
    </Attribute>
  </Attributes>
</Dimension>
```

Benefits:
- Query performance optimization
- Aggregation design
- Better compression
- Reduced storage

## Special Dimension Patterns

### Date/Time Dimension

```sql
CREATE TABLE DimDate (
    DateKey INT PRIMARY KEY,
    Date DATE NOT NULL,
    DayOfWeek VARCHAR(10),
    DayOfMonth INT,
    DayOfYear INT,
    WeekOfYear INT,
    MonthName VARCHAR(10),
    MonthNumber INT,
    Quarter INT,
    Year INT,
    IsWeekend BIT,
    IsHoliday BIT,
    HolidayName VARCHAR(50),
    FiscalYear INT,
    FiscalQuarter INT,
    FiscalMonth INT,
    -- ISO 8601 fields
    ISOWeek INT,
    ISOYear INT,
    -- Relative periods
    IsCurrentDay BIT,
    IsCurrentWeek BIT,
    IsCurrentMonth BIT,
    IsCurrentQuarter BIT,
    IsCurrentYear BIT,
    -- Computed attributes
    YearMonth VARCHAR(7), -- '2024-01'
    YearQuarter VARCHAR(7), -- '2024-Q1'
    MonthYear VARCHAR(8), -- 'Jan 2024'
    -- Business day flags
    IsBusinessDay BIT,
    BusinessDayOfMonth INT,
    BusinessDayOfYear INT
);
```

### Geography Dimension

```sql
CREATE TABLE DimGeography (
    GeographyKey INT PRIMARY KEY,
    PostalCode VARCHAR(10),
    City VARCHAR(100),
    StateProvince VARCHAR(100),
    StateProvinceCode VARCHAR(10),
    Country VARCHAR(100),
    CountryCode VARCHAR(3),
    Region VARCHAR(50),
    Continent VARCHAR(50),
    -- Coordinates
    Latitude DECIMAL(9,6),
    Longitude DECIMAL(9,6),
    -- Aggregation helpers
    CityState AS (City + ', ' + StateProvinceCode),
    FullLocation AS (City + ', ' + StateProvinceCode + ', ' + Country)
);
```

### Product Dimension

```sql
CREATE TABLE DimProduct (
    ProductKey INT PRIMARY KEY,
    ProductID VARCHAR(50) UNIQUE NOT NULL,
    ProductName VARCHAR(200),
    SKU VARCHAR(50),
    -- Hierarchies
    Division VARCHAR(50),
    Category VARCHAR(100),
    Subcategory VARCHAR(100),
    Brand VARCHAR(100),
    ProductLine VARCHAR(100),
    -- Attributes
    Color VARCHAR(50),
    Size VARCHAR(20),
    Weight DECIMAL(10,2),
    UnitOfMeasure VARCHAR(20),
    -- Pricing
    StandardCost DECIMAL(10,2),
    ListPrice DECIMAL(10,2),
    -- Status
    Status VARCHAR(20), -- Active, Discontinued, etc.
    IntroducedDate DATE,
    DiscontinuedDate DATE,
    -- SCD Type 2 fields
    StartDate DATE,
    EndDate DATE,
    IsCurrent BIT
);
```

### Customer Dimension

```sql
CREATE TABLE DimCustomer (
    CustomerKey INT PRIMARY KEY,
    CustomerID VARCHAR(50) UNIQUE NOT NULL,
    -- Demographics
    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    FullName AS (FirstName + ' ' + LastName),
    Gender VARCHAR(1),
    BirthDate DATE,
    MaritalStatus VARCHAR(1),
    -- Contact
    Email VARCHAR(200),
    Phone VARCHAR(20),
    -- Segmentation
    CustomerSegment VARCHAR(50),
    CustomerType VARCHAR(50), -- Individual, Business
    AnnualIncome DECIMAL(15,2),
    CreditRating VARCHAR(10),
    -- Geography
    GeographyKey INT,
    -- Status
    AccountOpenDate DATE,
    AccountCloseDate DATE,
    CustomerStatus VARCHAR(20),
    -- SCD Type 2
    StartDate DATE,
    EndDate DATE,
    IsCurrent BIT,
    -- Derived attributes
    Age AS (DATEDIFF(YEAR, BirthDate, GETDATE())),
    AgeGroup AS (
        CASE
            WHEN DATEDIFF(YEAR, BirthDate, GETDATE()) < 18 THEN 'Under 18'
            WHEN DATEDIFF(YEAR, BirthDate, GETDATE()) < 35 THEN '18-34'
            WHEN DATEDIFF(YEAR, BirthDate, GETDATE()) < 50 THEN '35-49'
            WHEN DATEDIFF(YEAR, BirthDate, GETDATE()) < 65 THEN '50-64'
            ELSE '65+'
        END
    )
);
```

## Unknown Member Handling

### Default Unknown Records

```sql
-- Insert unknown member for each dimension
INSERT INTO DimProduct (ProductKey, ProductID, ProductName, IsCurrent)
VALUES (-1, 'UNKNOWN', 'Unknown Product', 1);

INSERT INTO DimCustomer (CustomerKey, CustomerID, FullName, IsCurrent)
VALUES (-1, 'UNKNOWN', 'Unknown Customer', 1);

INSERT INTO DimDate (DateKey, Date, Year, MonthNumber)
VALUES (00000000, '1900-01-01', 1900, 1);

-- Use in fact table for missing references
INSERT INTO FactSales (ProductKey, CustomerKey, DateKey, Amount)
VALUES (
    ISNULL(ProductKey, -1),
    ISNULL(CustomerKey, -1),
    ISNULL(DateKey, 00000000),
    Amount
);
```

### SSAS Configuration

```xml
<Dimension>
  <ID>Product</ID>
  <UnknownMember>Visible</UnknownMember>
  <UnknownMemberName>Unknown Product</UnknownMemberName>
</Dimension>
```

## Dimension Design Best Practices

### 1. Naming Conventions
```
✓ Clear, business-friendly names
✓ Consistent prefixes (Dim, Fact)
✓ Avoid abbreviations
✓ Use full words

Examples:
✓ DimCustomer, DimProduct, DimDate
✗ DimCust, DimProd, DimDt
✓ CustomerName, ProductCategory
✗ CustNm, ProdCat
```

### 2. Grain Selection
```
Choose appropriate detail level:

Too Fine:
- Every product variation (color, size) as separate dimension
- Millions of members
- Poor performance

Too Coarse:
- Only product category
- Loss of analytical capability
- Limited insights

Appropriate:
- Product dimension with hierarchy (Category → Subcategory → Product)
- Supports drill-down
- Manageable member count
```

### 3. Cardinality Management
```
Dimension Size Guidelines:
- Low: < 1,000 members (Category, Region)
- Medium: 1,000 - 100,000 (Product, Store)
- High: 100,000 - 1,000,000 (Customer)
- Very High: > 1,000,000 (Transaction ID - consider degenerate)

Performance Impact:
- Low: Minimal
- Medium: Carefully design hierarchies
- High: Consider partitioning, optimize indexes
- Very High: Re-evaluate design, consider degenerate dimension
```

### 4. Surrogate Keys
```
Always use surrogate keys:

✓ Benefits:
- Enables SCD Type 2
- Smaller, faster joins
- Handles source system changes
- Supports data integration from multiple sources

✗ Natural Keys:
- Can change over time
- May be large (composite keys)
- Source system dependent
```

### 5. Dimension Width
```
Optimal attribute count:
- 5-15 attributes: Good
- 15-30 attributes: Acceptable
- 30+ attributes: Consider splitting

If too many attributes:
- Create subdimensions (outriggers)
- Evaluate if all are needed
- Consider junk dimension for flags
```

## Performance Optimization

### Indexing Strategy

```sql
-- Primary key (clustered)
ALTER TABLE DimProduct
ADD CONSTRAINT PK_Product PRIMARY KEY CLUSTERED (ProductKey);

-- Natural key (non-clustered)
CREATE UNIQUE NONCLUSTERED INDEX IX_Product_ProductID
ON DimProduct(ProductID);

-- Frequently filtered attributes
CREATE NONCLUSTERED INDEX IX_Product_Category
ON DimProduct(Category);

-- Covering index for common queries
CREATE NONCLUSTERED INDEX IX_Product_Category_Brand
ON DimProduct(Category, Brand)
INCLUDE (ProductName, ListPrice);

-- SCD Type 2 support
CREATE NONCLUSTERED INDEX IX_Product_ID_Current
ON DimProduct(ProductID, IsCurrent)
INCLUDE (ProductKey);
```

### Partitioning Large Dimensions

```sql
-- Partition very large customer dimension
CREATE PARTITION SCHEME PS_Customer
AS PARTITION PF_CustomerSegment
TO ([PRIMARY], [PRIMARY], [PRIMARY]);

CREATE PARTITION FUNCTION PF_CustomerSegment (VARCHAR(50))
AS RANGE LEFT FOR VALUES ('Premium', 'Standard');

-- Apply to table
CREATE TABLE DimCustomer (
    CustomerKey INT,
    CustomerSegment VARCHAR(50),
    ...
) ON PS_Customer(CustomerSegment);
```

## Testing and Validation

### Data Quality Checks

```sql
-- Check for NULL values in required fields
SELECT COUNT(*)
FROM DimProduct
WHERE ProductName IS NULL OR Category IS NULL;

-- Verify SCD Type 2 logic
SELECT ProductID, COUNT(*)
FROM DimProduct
GROUP BY ProductID
HAVING COUNT(*) > 1 AND SUM(CAST(IsCurrent AS INT)) != 1;

-- Check for orphaned records (no current record)
SELECT ProductID
FROM DimProduct
GROUP BY ProductID
HAVING SUM(CAST(IsCurrent AS INT)) = 0;

-- Validate date ranges
SELECT *
FROM DimProduct
WHERE StartDate > EndDate
   OR (IsCurrent = 1 AND EndDate != '9999-12-31');

-- Check for duplicate keys
SELECT ProductKey, COUNT(*)
FROM DimProduct
GROUP BY ProductKey
HAVING COUNT(*) > 1;
```
