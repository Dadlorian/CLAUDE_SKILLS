# Power BI DAX Reference Guide

## DAX Fundamentals

### Calculated Columns vs Measures

**Calculated Columns** - Computed row-by-row, stored in model
```dax
// Calculated Column (in table)
Full Name = Customers[FirstName] & " " & Customers[LastName]

// Profit Margin
Profit Margin = DIVIDE(Sales[Revenue] - Sales[Cost], Sales[Revenue])

// Age Group
Age Group =
SWITCH(
    TRUE(),
    Customers[Age] < 18, "Under 18",
    Customers[Age] < 35, "18-34",
    Customers[Age] < 55, "35-54",
    "55+"
)
```

**Measures** - Computed dynamically based on filter context
```dax
// Total Sales
Total Sales = SUM(Sales[Amount])

// Average Order Value
Average Order Value =
DIVIDE(
    SUM(Sales[Amount]),
    DISTINCTCOUNT(Sales[OrderID])
)

// Active Customers
Active Customers =
CALCULATE(
    DISTINCTCOUNT(Sales[CustomerID]),
    Sales[Date] >= TODAY() - 90
)
```

### When to Use Each
- **Calculated Column**: Static values, row-level logic, used in slicers/filters
- **Measure**: Aggregations, dynamic calculations, better performance for aggregates

## Core DAX Functions

### Aggregation Functions
```dax
// Basic aggregations
Total Sales = SUM(Sales[Amount])
Average Sales = AVERAGE(Sales[Amount])
Min Sales = MIN(Sales[Amount])
Max Sales = MAX(Sales[Amount])

// Count variations
Row Count = COUNT(Sales[OrderID])
Distinct Customers = DISTINCTCOUNT(Sales[CustomerID])
Count Non-Blank = COUNTA(Sales[ProductID])
Count Rows = COUNTROWS(Sales)
Count Blank = COUNTBLANK(Sales[DiscountCode])

// Statistical
Std Dev = STDEV.P(Sales[Amount])
Variance = VAR.P(Sales[Amount])
Median Sales = MEDIAN(Sales[Amount])
```

### Iterator Functions (X-Functions)
```dax
// SUMX - Row-by-row calculation then sum
Total Revenue =
SUMX(
    Sales,
    Sales[Quantity] * Sales[UnitPrice]
)

// AVERAGEX - Calculate then average
Avg Order Value =
AVERAGEX(
    VALUES(Sales[OrderID]),
    CALCULATE(SUM(Sales[Amount]))
)

// RANKX - Ranking
Product Rank =
RANKX(
    ALL(Products[ProductName]),
    [Total Sales],
    ,
    DESC,
    DENSE
)

// CONCATENATEX - String aggregation
Product List =
CONCATENATEX(
    Products,
    Products[ProductName],
    ", ",
    Products[ProductName],
    ASC
)

// MINX, MAXX - Min/Max of expression
Longest Deal Cycle =
MAXX(
    Sales,
    DATEDIFF(Sales[CreatedDate], Sales[ClosedDate], DAY)
)
```

### CALCULATE - The Most Important Function
```dax
// Basic CALCULATE - Modify filter context
Sales Last Year =
CALCULATE(
    SUM(Sales[Amount]),
    SAMEPERIODLASTYEAR('Date'[Date])
)

// Multiple filters
High Value Sales =
CALCULATE(
    SUM(Sales[Amount]),
    Sales[Amount] > 1000,
    Products[Category] = "Electronics"
)

// Remove filters
Total Sales All Regions =
CALCULATE(
    SUM(Sales[Amount]),
    ALL(Regions)
)

// Replace filter context
Sales for This Product =
CALCULATE(
    SUM(Sales[Amount]),
    ALL(Products),
    Products[ProductID] = EARLIER(Products[ProductID])
)

// Using FILTER
Sales of Big Customers =
CALCULATE(
    SUM(Sales[Amount]),
    FILTER(
        Customers,
        [Total Sales] > 10000
    )
)
```

## Filter Functions

### ALL Family
```dax
// Remove all filters from table
Total Sales (All) = CALCULATE(SUM(Sales[Amount]), ALL(Sales))

// Remove filters from specific columns
Sales All Products = CALCULATE(SUM(Sales[Amount]), ALL(Products[Category]))

// Remove only selected columns, keep others
Sales All Except Region =
CALCULATE(
    SUM(Sales[Amount]),
    ALLEXCEPT(Sales, Sales[Region])
)

// All selected (used with slicers)
Selected Products =
CALCULATE(
    DISTINCTCOUNT(Sales[ProductID]),
    ALLSELECTED(Products)
)
```

### FILTER Function
```dax
// Dynamic filtering
Sales of Premium Customers =
CALCULATE(
    SUM(Sales[Amount]),
    FILTER(
        Customers,
        Customers[Tier] = "Premium"
    )
)

// Complex filter logic
Recent High Value Sales =
CALCULATE(
    SUM(Sales[Amount]),
    FILTER(
        Sales,
        Sales[Date] >= TODAY() - 30 &&
        Sales[Amount] > 1000
    )
)

// Filtered table in variable
VAR HighValueOrders =
    FILTER(
        Sales,
        Sales[Amount] > 5000
    )
RETURN
    COUNTROWS(HighValueOrders)
```

### KEEPFILTERS
```dax
// Add to existing filter instead of replacing
Sales Tech Products =
CALCULATE(
    SUM(Sales[Amount]),
    KEEPFILTERS(Products[Category] = "Technology")
)
```

### REMOVEFILTERS
```dax
// Modern alternative to ALL
Sales No Date Filter =
CALCULATE(
    SUM(Sales[Amount]),
    REMOVEFILTERS('Date')
)
```

## Time Intelligence Functions

### Year-to-Date Calculations
```dax
// Sales YTD
Sales YTD =
CALCULATE(
    SUM(Sales[Amount]),
    DATESYTD('Date'[Date])
)

// Quarter-to-Date
Sales QTD =
CALCULATE(
    SUM(Sales[Amount]),
    DATESQTD('Date'[Date])
)

// Month-to-Date
Sales MTD =
CALCULATE(
    SUM(Sales[Amount]),
    DATESMTD('Date'[Date])
)
```

### Period-over-Period Comparisons
```dax
// Prior Year
Sales PY =
CALCULATE(
    SUM(Sales[Amount]),
    SAMEPERIODLASTYEAR('Date'[Date])
)

// Year-over-Year Growth
YoY Growth =
VAR CurrentYear = SUM(Sales[Amount])
VAR PriorYear = CALCULATE(SUM(Sales[Amount]), SAMEPERIODLASTYEAR('Date'[Date]))
RETURN
    DIVIDE(CurrentYear - PriorYear, PriorYear)

// Prior Month
Sales Prior Month =
CALCULATE(
    SUM(Sales[Amount]),
    DATEADD('Date'[Date], -1, MONTH)
)

// Month-over-Month
MoM Growth =
VAR CurrentMonth = SUM(Sales[Amount])
VAR PriorMonth = CALCULATE(SUM(Sales[Amount]), DATEADD('Date'[Date], -1, MONTH))
RETURN
    DIVIDE(CurrentMonth - PriorMonth, PriorMonth)
```

### Rolling Periods
```dax
// Last 12 Months
Sales L12M =
CALCULATE(
    SUM(Sales[Amount]),
    DATESINPERIOD(
        'Date'[Date],
        LASTDATE('Date'[Date]),
        -12,
        MONTH
    )
)

// Rolling 7 Days
Sales L7D =
CALCULATE(
    SUM(Sales[Amount]),
    DATESINPERIOD(
        'Date'[Date],
        MAX('Date'[Date]),
        -7,
        DAY
    )
)

// Last Complete Month
Sales Last Month =
CALCULATE(
    SUM(Sales[Amount]),
    DATESMTD(DATEADD('Date'[Date], -1, MONTH))
)
```

### Custom Time Periods
```dax
// Fiscal Year (July 1 start)
Sales Fiscal YTD =
CALCULATE(
    SUM(Sales[Amount]),
    DATESYTD('Date'[Date], "6/30")
)

// Last N Days (dynamic)
Sales Last N Days =
VAR DaysBack = [Days Parameter Value]
RETURN
    CALCULATE(
        SUM(Sales[Amount]),
        FILTER(
            ALL('Date'),
            'Date'[Date] > MAX('Date'[Date]) - DaysBack &&
            'Date'[Date] <= MAX('Date'[Date])
        )
    )
```

## Advanced Patterns

### Variables (VAR)
```dax
// Using variables for clarity and performance
Customer Lifetime Value =
VAR TotalRevenue = SUM(Sales[Amount])
VAR TotalCost = SUM(Sales[Cost])
VAR CustomerCount = DISTINCTCOUNT(Sales[CustomerID])
VAR AvgLifetime = 36 // months
RETURN
    DIVIDE((TotalRevenue - TotalCost) * AvgLifetime, CustomerCount)

// Complex calculation with multiple vars
Cohort Retention =
VAR CohortDate = MIN(Customers[FirstPurchaseDate])
VAR MonthsAgo = DATEDIFF(CohortDate, TODAY(), MONTH)
VAR InitialCustomers =
    CALCULATE(
        DISTINCTCOUNT(Sales[CustomerID]),
        Sales[Date] = CohortDate
    )
VAR CurrentCustomers =
    CALCULATE(
        DISTINCTCOUNT(Sales[CustomerID]),
        Sales[Date] >= TODAY() - 30
    )
RETURN
    DIVIDE(CurrentCustomers, InitialCustomers)
```

### EARLIER Function (Row Context)
```dax
// Rank within category
Product Rank in Category =
RANKX(
    FILTER(
        Products,
        Products[Category] = EARLIER(Products[Category])
    ),
    Products[TotalSales],
    ,
    DESC
)

// Count of products above this price
Products Above This Price =
COUNTROWS(
    FILTER(
        Products,
        Products[Price] > EARLIER(Products[Price])
    )
)
```

### SWITCH and TRUE()
```dax
// Multiple conditions
Sales Tier =
SWITCH(
    TRUE(),
    [Total Sales] >= 100000, "Platinum",
    [Total Sales] >= 50000, "Gold",
    [Total Sales] >= 10000, "Silver",
    "Bronze"
)

// Complex business logic
Discount Rate =
SWITCH(
    TRUE(),
    AND([Total Sales] > 50000, [Region] = "West"), 0.15,
    AND([Total Sales] > 30000, [Region] = "East"), 0.12,
    [Total Sales] > 10000, 0.10,
    0.05
)
```

### Dynamic Segmentation
```dax
// ABC Analysis
ABC Classification =
VAR CurrentProductSales = [Total Sales]
VAR RunningTotal =
    CALCULATE(
        [Total Sales],
        FILTER(
            ALL(Products),
            [Total Sales] >= CurrentProductSales
        )
    )
VAR TotalSales = CALCULATE([Total Sales], ALL(Products))
VAR Percentage = DIVIDE(RunningTotal, TotalSales)
RETURN
    SWITCH(
        TRUE(),
        Percentage <= 0.7, "A",
        Percentage <= 0.9, "B",
        "C"
    )
```

### Parent-Child Hierarchies
```dax
// Path function (for org charts, etc.)
Manager Path =
PATH(Employees[EmployeeID], Employees[ManagerID])

// Level in hierarchy
Org Level =
PATHLENGTH(Employees[ManagerPath])

// Parent name
Manager Name =
LOOKUPVALUE(
    Employees[FullName],
    Employees[EmployeeID],
    PATHITEM(Employees[ManagerPath], 2)
)
```

## Performance Optimization

### Use Variables
```dax
// SLOW: Calculation repeated
Measure =
DIVIDE(
    CALCULATE(SUM(Sales[Amount]), Region[Name] = "West"),
    CALCULATE(SUM(Sales[Amount]), ALL(Region))
)

// FAST: Calculate once, use twice
Measure Optimized =
VAR WestSales = CALCULATE(SUM(Sales[Amount]), Region[Name] = "West")
VAR AllSales = CALCULATE(SUM(Sales[Amount]), ALL(Region))
RETURN DIVIDE(WestSales, AllSales)
```

### Avoid Calculated Columns for Aggregates
```dax
// SLOW: Calculated column
// Sales[TotalAmount] = Sales[Quantity] * Sales[Price]
// Measure: SUM(Sales[TotalAmount])

// FAST: Calculate in measure
Total Sales = SUMX(Sales, Sales[Quantity] * Sales[Price])
```

### Use COUNTROWS Instead of COUNT
```dax
// SLOWER
Order Count = COUNT(Sales[OrderID])

// FASTER
Order Count = COUNTROWS(Sales)
```

### Minimize Iterator Usage
```dax
// SLOW: Nested iterators
Measure =
SUMX(
    Products,
    AVERAGEX(
        RELATEDTABLE(Sales),
        Sales[Amount]
    )
)

// Better: Simplify logic if possible
```

## Common Patterns

### Top N with Others
```dax
Top N Products =
VAR TopNValue = [Top N Parameter]
VAR ProductRank = RANKX(ALL(Products[Name]), [Total Sales],, DESC)
RETURN
    IF(ProductRank <= TopNValue, Products[Name], "Other")
```

### Running Total
```dax
Running Total =
CALCULATE(
    [Total Sales],
    FILTER(
        ALLSELECTED('Date'),
        'Date'[Date] <= MAX('Date'[Date])
    )
)
```

### Percent of Total
```dax
% of Total =
DIVIDE(
    [Total Sales],
    CALCULATE([Total Sales], ALL(Products))
)

% of Parent =
DIVIDE(
    [Total Sales],
    CALCULATE([Total Sales], ALLEXCEPT(Products, Products[Category]))
)
```

### Cohort Analysis
```dax
// Cohort month
Cohort Month =
CALCULATE(
    MIN('Date'[YearMonth]),
    ALLEXCEPT(Sales, Sales[CustomerID])
)

// Months from cohort
Months from Cohort =
DATEDIFF([Cohort Month], MAX('Date'[YearMonth]), MONTH)

// Cohort size
Cohort Size =
CALCULATE(
    DISTINCTCOUNT(Sales[CustomerID]),
    FILTER(
        ALLSELECTED('Date'),
        'Date'[YearMonth] = [Cohort Month]
    )
)

// Retention rate
Retention Rate =
DIVIDE(
    DISTINCTCOUNT(Sales[CustomerID]),
    [Cohort Size]
)
```

## Error Handling

### DIVIDE Function
```dax
// Handles divide by zero
Profit Margin = DIVIDE([Profit], [Revenue], 0)

// Custom error value
Ratio = DIVIDE([Numerator], [Denominator], BLANK())
```

### IFERROR
```dax
Safe Calculation =
IFERROR(
    [Risky Calculation],
    BLANK()
)
```

### ISBLANK and Handling
```dax
Sales or Zero =
IF(
    ISBLANK([Total Sales]),
    0,
    [Total Sales]
)
```

## DAX Studio Queries

### Basic Query
```dax
EVALUATE
    TOPN(
        10,
        SUMMARIZE(
            Sales,
            Products[Name],
            "Total Sales", SUM(Sales[Amount])
        ),
        [Total Sales],
        DESC
    )
```

### With Variables
```dax
EVALUATE
VAR TopProducts =
    TOPN(
        100,
        SUMMARIZE(Sales, Products[Name]),
        SUM(Sales[Amount]),
        DESC
    )
RETURN
    ADDCOLUMNS(
        TopProducts,
        "Revenue", SUM(Sales[Amount]),
        "Profit", SUM(Sales[Profit])
    )
```

## Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| Circular dependency | Measure references itself | Check calculation chain |
| Cannot convert to type | Type mismatch | Use conversion functions |
| Column not found | Wrong table reference | Verify table and column names |
| Too many arguments | Extra commas or params | Check function syntax |
| The value for column cannot be determined | Context issue | Add CALCULATE or check relationships |
| A table of multiple values was supplied | EARLIER or filter needed | Use EARLIER or proper FILTER |

## Quick Reference

| Need | DAX Pattern |
|------|------------|
| Simple total | `SUM(Table[Column])` |
| Distinct count | `DISTINCTCOUNT(Table[Column])` |
| Year-to-date | `TOTALYTD(SUM(Table[Column]), 'Date'[Date])` |
| Prior year | `CALCULATE([Measure], SAMEPERIODLASTYEAR('Date'[Date]))` |
| Rolling 12 months | `CALCULATE([Measure], DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -12, MONTH))` |
| Percentage of total | `DIVIDE([Measure], CALCULATE([Measure], ALL(Table)))` |
| Ranking | `RANKX(ALL(Table[Column]), [Measure],, DESC)` |
| Filter removal | `CALCULATE([Measure], ALL(Table))` |
| Multiple filters | `CALCULATE([Measure], Table[Col1] = "Value", Table[Col2] > 100)` |

## Resources
- DAX Function Reference: https://dax.guide/
- SQLBI DAX Patterns: https://www.daxpatterns.com/
- DAX Formatter: https://www.daxformatter.com/
