# Power BI Optimization Guide

## Data Model Optimization

### Star Schema Design
```
Fact Table (Sales):
- SalesID (PK)
- DateKey (FK) → Date
- ProductKey (FK) → Product
- CustomerKey (FK) → Customer
- Quantity
- Amount

Dimension Tables:
- Date (DateKey, Date, Month, Quarter, Year)
- Product (ProductKey, Name, Category, Price)
- Customer (CustomerKey, Name, Segment, Region)

✓ Benefits:
- Fast queries
- Clear relationships
- Easy to understand
- Optimal for DAX
```

### Reduce Model Size
```powerquery
// Remove unnecessary columns in Power Query
Source = Sql.Database("server", "database"),
SelectNeeded = Table.SelectColumns(Source, {
    "OrderID", "OrderDate", "CustomerID", "Amount"
}),

// Use smallest data types
ChangeTypes = Table.TransformColumnTypes(SelectNeeded, {
    {"OrderID", Int64.Type},        // Instead of text
    {"OrderDate", type date},       // Not datetime
    {"Amount", type number}         // Not decimal
}),

// Remove duplicates
RemoveDups = Table.Distinct(ChangeTypes, {"OrderID"})
```

### Disable Auto Date/Time
```
File → Options → Data Load
☐ Auto date/time (uncheck)

Why:
- Creates hidden calculated tables
- 12 columns per date column
- Significantly increases model size
- Create explicit Date table instead
```

## DAX Optimization

### Use Variables
```dax
// SLOW: Repeats calculation
Sales vs Target =
DIVIDE(
    SUM(Sales[Amount]),
    SUM(Target[Amount])
) - 1

// FAST: Calculate once with VAR
Sales vs Target Optimized =
VAR CurrentSales = SUM(Sales[Amount])
VAR TargetAmount = SUM(Target[Amount])
VAR Variance = DIVIDE(CurrentSales, TargetAmount) - 1
RETURN Variance
```

### Avoid Calculated Columns for Aggregates
```dax
// SLOW: Calculated column (stored in model)
Sales[TotalAmount] = Sales[Quantity] * Sales[UnitPrice]
Measure: Total = SUM(Sales[TotalAmount])

// FAST: Calculate in measure
Total Sales =
SUMX(Sales, Sales[Quantity] * Sales[UnitPrice])

// BETTER: Calculate in Power Query
= Table.AddColumn(Source, "TotalAmount",
    each [Quantity] * [UnitPrice], type number)
```

### Optimize CALCULATE
```dax
// SLOW: Multiple CALCULATE calls
Result =
VAR A = CALCULATE(SUM(Sales[Amount]), Filter1)
VAR B = CALCULATE(SUM(Sales[Amount]), Filter2)
RETURN A + B

// FAST: Single CALCULATE with OR
Result Optimized =
CALCULATE(
    SUM(Sales[Amount]),
    Filter1 || Filter2
)

// Use KEEPFILTERS for additive filters
Sales with Filter =
CALCULATE(
    SUM(Sales[Amount]),
    KEEPFILTERS(Product[Category] = "Electronics")
)
```

## Power Query Optimization

### Query Folding
```powerquery
// Operations that fold to database:
Source = Sql.Database("server", "db"),
Filter = Table.SelectRows(Source,
    each [OrderDate] >= #date(2024,1,1)),
Select = Table.SelectColumns(Filter,
    {"OrderID", "Amount", "CustomerID"}),
Group = Table.Group(Select, {"CustomerID"},
    {{"Total", each List.Sum([Amount])}})

// Check folding: Right-click step → View Native Query
// If grayed out, folding broke at previous step

// Common folding breaks:
❌ Table.AddColumn with complex functions
❌ Merging with non-database tables
❌ Text.Upper, Text.Proper (use database functions)

// Push to source when possible:
= Sql.Database("server", "db", [Query="
    SELECT
        CustomerID,
        SUM(Amount) as Total
    FROM Orders
    WHERE OrderDate >= '2024-01-01'
    GROUP BY CustomerID
"])
```

### Incremental Refresh
```powerquery
// 1. Create RangeStart and RangeEnd parameters
// Parameter: RangeStart (Date/Time)
// Parameter: RangeEnd (Date/Time)

// 2. Filter using parameters
Source = Sql.Database("server", "database"),
FilteredRows = Table.SelectRows(Source,
    each [OrderDate] >= RangeStart
     and [OrderDate] < RangeEnd)

// 3. Configure incremental refresh policy
// Table → Incremental refresh settings
Archive data starting: 5 years before refresh date
Incrementally refresh: 7 days before refresh date
Detect data changes: [OrderDate] column

// Result:
// - Historical data (>7 days): Stored, not refreshed
// - Recent data (7 days): Refreshed each time
// - Full refresh only when needed
```

## Aggregations

### Configure Aggregation Tables
```dax
// Detail table: Sales (10M rows)
// Agg table: Sales_Monthly (100K rows)

// Create aggregation table
Sales_Monthly =
SUMMARIZECOLUMNS(
    'Date'[Year],
    'Date'[Month],
    'Product'[Category],
    "Total_Sales", SUM(Sales[Amount]),
    "Total_Quantity", SUM(Sales[Quantity]),
    "Order_Count", COUNTROWS(Sales)
)

// Configure in model (Manage Aggregations):
// Sales_Monthly.Year → Sales.OrderDate (Year)
// Sales_Monthly.Month → Sales.OrderDate (Month)
// Sales_Monthly.Category → Product.Category
// Sales_Monthly.Total_Sales → SUM(Sales.Amount)

// Power BI automatically uses agg when possible
```

### When Aggregations Help
```
✓ Use aggregations when:
- Detail table > 1M rows
- Queries often at higher grain (monthly vs daily)
- DirectQuery performance is slow
- Users rarely drill to detail

Example:
Detail: 10M rows (daily transactions)
Monthly agg: 36K rows (3 years × 12 months × 100 products)
Performance: 100x faster for monthly queries
```

## DirectQuery Optimization

### Reduce Visuals Per Page
```
DirectQuery = Every visual = Database query

✓ Recommended:
- 3-5 visuals per report page
- Use slicers sparingly (each adds query)
- Group related metrics in same visual

❌ Avoid:
- 10+ visuals on one page
- Separate card for each KPI
- Multiple instances of same data
```

### Composite Model Pattern
```
Storage Modes:
├─ Import: Dimension tables (small, static)
│   └─ Product, Customer, Date
├─ DirectQuery: Fact tables (large, real-time)
│   └─ Sales, Inventory
└─ Dual: Can be either (Power BI chooses)
    └─ Time dimensions

Benefits:
- Real-time data from DirectQuery
- Fast dimension filtering from Import
- Aggregations stored in Import mode
```

### Query Reduction
```
File → Options → Query reduction

☑ Reduce number of queries sent by:
  ☑ Applying slicer filters only after Analyze button
  ☑ Applying filter pane changes only after Apply button

// Batches queries instead of each interaction
// Critical for DirectQuery performance
```

## Report Performance

### Performance Analyzer
```
View → Performance Analyzer → Start Recording

Metrics shown:
1. DAX query: Time to execute measure logic
2. Visual display: Time to render
3. Other: Overhead

Optimization based on results:
- High DAX query: Optimize measures, use aggregations
- High visual display: Simplify visual, reduce data points
- High other: Too many visuals, reduce complexity

// Export results for analysis
Performance Analyzer → Export
```

### Visual-Specific Optimization
```
Matrix:
- Limit to 1,000 rows
- Avoid many nested levels
- Use "Show items with no data" sparingly

Table:
- Limit rows (use Top N)
- Avoid too many columns
- Sort by measure, not dimension

Line Chart:
- Limit to 3-5 series
- Aggregate to appropriate grain
- Use markers only if <50 points

Map:
- Use filled maps for regions
- Limit to 1,000 locations
- Use clustering for many points
```

## Refresh Optimization

### Parallel Partition Refresh
```powerquery
// Split large tables into partitions
// Sales_2022, Sales_2023, Sales_2024

// Benefits:
- Parallel refresh (faster)
- Refresh only changed partition
- Easier to manage

// Implementation:
// 1. Create partitions via XMLA endpoint
// 2. Refresh specific partitions via API
POST /datasets/{id}/refreshes
{
  "type": "Full",
  "objects": [
    {"table": "Sales_2024"}
  ]
}
```

### Scheduled Refresh Strategy
```
Real-time Dashboard:
- DirectQuery or Live Connection
- No refresh needed

Daily Operational:
- Refresh: Every 3 hours (8 times/day)
- Incremental refresh enabled

Weekly Reports:
- Refresh: Monday 6 AM
- Full refresh only

Executive Monthly:
- Refresh: 1st of month, 8 AM
- Full refresh
```

## Relationship Optimization

### Bidirectional Filtering (Use Carefully)
```
// Many-to-many scenarios only
Sales <-→ Bridge <-→ Product

⚠ Risks:
- Ambiguous filter paths
- Performance degradation
- Unexpected results

✓ Better: Resolve at data source
```

### Inactive Relationships
```dax
// Use USERELATIONSHIP for role-playing dimensions
Sales by Order Date =
CALCULATE(
    SUM(Sales[Amount]),
    USERELATIONSHIP(Sales[OrderDate], 'Date'[Date])
)

Sales by Ship Date =
CALCULATE(
    SUM(Sales[Amount]),
    USERELATIONSHIP(Sales[ShipDate], 'Date'[Date])
)

// Only one relationship can be active
```

## Visual Design Performance

### Reduce Visual Queries
```
// Use bookmarks for view switching
// Instead of multiple hidden visuals

Create bookmarks:
1. Summary View (simple visuals)
2. Detail View (complex analysis)
3. Trend View (time series)

// User clicks button → Change bookmark
// Visuals not in bookmark don't query
```

### Conditional Formatting Performance
```dax
// SLOW: Complex conditional format on every cell
Color =
SWITCH(TRUE(),
    [Sales] > CALCULATE([Sales], ALL(Product)), "Green",
    [Sales] < CALCULATE([Sales], ALL(Product)) * 0.5, "Red",
    "Yellow"
)

// FAST: Pre-calculate categories
Sales Category =
VAR AvgSales = CALCULATE(AVERAGE(Sales[Amount]), ALL(Product))
VAR CurrentSales = SUM(Sales[Amount])
RETURN
    IF(CurrentSales > AvgSales, "High", "Low")

// Apply simple conditional format on category
```

## Deployment Pipelines

### Dev → Test → Prod
```
Workspace Development:
├─ Frequent changes
├─ Sample data
└─ Individual testing

Workspace Test:
├─ Full data
├─ User acceptance testing
└─ Performance validation

Workspace Production:
├─ Published to app
├─ Permissions configured
└─ Scheduled refreshes

// Power BI Pipelines (Premium)
Dev → Deploy → Test → Deploy → Prod
// Handles parameters, data sources
```

## Capacity Management (Premium)

### Monitor Metrics
```
Metrics to watch:
- CPU %: Keep < 80%
- Memory %: Keep < 80%
- Query duration: < 30 seconds
- Refresh duration: Varies by dataset size

// Capacity Metrics App
Download from AppSource
Install in Admin workspace
Monitor daily
```

### Autoscale
```
// Premium Gen2 feature
When CPU > 100% for 24 hours:
→ Add 1 v-core for 24 hours
→ Billed hourly

Max autoscale: 2x base capacity
```

## Best Practices Checklist

### Before Publishing
- [ ] Model < 1 GB (or use Premium)
- [ ] Removed unused columns
- [ ] Optimal data types
- [ ] Star schema implemented
- [ ] Relationships optimized
- [ ] DAX measures use variables
- [ ] Aggregations configured (if needed)
- [ ] Incremental refresh set up (large datasets)
- [ ] Performance Analyzer results acceptable
- [ ] Report loads < 5 seconds
- [ ] Documented complex measures

### Monthly Maintenance
- [ ] Review Capacity Metrics
- [ ] Check refresh failures
- [ ] Analyze usage patterns
- [ ] Remove stale content
- [ ] Update documentation
- [ ] Test restore procedure

## Troubleshooting Guide

### Slow Refresh
```
Diagnosis:
1. Check Refresh History for failure patterns
2. Review Power Query steps (folding breaks?)
3. Monitor network during refresh
4. Check source database performance

Solutions:
- Enable incremental refresh
- Partition large tables
- Push transformations to source
- Use dataflows for shared prep
- Consider Premium for parallel refresh
```

### Memory Errors
```
Error: "The operation has been cancelled because there is not enough memory"

Solutions:
1. Reduce model size
   - Remove unused columns
   - Optimize data types
   - Use incremental refresh

2. Upgrade capacity (Premium)
   - More memory available
   - Larger dataset support

3. Use DirectQuery/Composite
   - Don't import large tables
   - Use aggregations
```

### Slow Visual Performance
```
Diagnosis:
1. Run Performance Analyzer
2. Identify slow visuals
3. Check DAX query time

Solutions:
- Simplify measures (use variables)
- Reduce data points in visual
- Use aggregations
- Switch to DirectQuery for detail
- Implement Top N filtering
```

## Resources
- DAX Patterns: https://www.daxpatterns.com/
- Power BI Best Practices: https://docs.microsoft.com/power-bi/guidance/
- SQLBI: https://www.sqlbi.com/
- Guy in a Cube: https://www.youtube.com/c/GuyinaCube
