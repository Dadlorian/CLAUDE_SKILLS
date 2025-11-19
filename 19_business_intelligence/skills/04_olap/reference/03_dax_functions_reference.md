# DAX Functions Reference

## Overview

DAX (Data Analysis Expressions) is the formula language for Power BI, Analysis Services Tabular, and Power Pivot, optimized for tabular data models.

## Function Categories

### 1. Aggregation Functions

#### Basic Aggregations
```dax
SUM(Sales[Amount])
AVERAGE(Sales[Quantity])
MIN(Sales[OrderDate])
MAX(Sales[OrderDate])
COUNT(Sales[OrderID])
COUNTA(Sales[CustomerName])  -- Counts non-blank values
COUNTROWS(Sales)
DISTINCTCOUNT(Sales[CustomerID])
```

#### Statistical Aggregations
```dax
MEDIAN(Sales[Amount])
PERCENTILE.INC(Sales[Amount], 0.75)
PERCENTILE.EXC(Sales[Amount], 0.75)
STDEV.P(Sales[Amount])  -- Population
STDEV.S(Sales[Amount])  -- Sample
VAR.P(Sales[Amount])
VAR.S(Sales[Amount])
```

#### Smart Aggregations
```dax
-- Respects filters and relationships
SUMX(Sales, Sales[Quantity] * Sales[UnitPrice])
AVERAGEX(Sales, Sales[Amount] / Sales[Quantity])
MINX(Sales, Sales[Discount])
MAXX(Sales, Sales[TotalAmount])
```

### 2. Filter Functions

#### FILTER
```dax
FILTER(
    Sales,
    Sales[Amount] > 1000
)

-- Multiple conditions
FILTER(
    Sales,
    Sales[Amount] > 1000 &&
    Sales[Region] = "West"
)
```

#### CALCULATE
```dax
-- Most important DAX function
CALCULATE(
    SUM(Sales[Amount]),
    Sales[Region] = "West",
    Sales[Year] = 2024
)

-- With filter functions
CALCULATE(
    SUM(Sales[Amount]),
    FILTER(Sales, Sales[Amount] > 1000)
)
```

#### ALL
```dax
ALL(Sales)              -- Removes all filters from Sales table
ALL(Sales[Region])      -- Removes filters from Region column
ALLEXCEPT(Sales, Sales[Year])  -- Remove all except Year filter
ALLSELECTED(Sales)      -- Removes filters except visual/page/report filters
```

#### KEEPFILTERS
```dax
CALCULATE(
    SUM(Sales[Amount]),
    KEEPFILTERS(Sales[Region] = "West")
)
```

#### REMOVEFILTERS
```dax
CALCULATE(
    SUM(Sales[Amount]),
    REMOVEFILTERS(Sales[Region])
)
```

#### VALUES & DISTINCT
```dax
VALUES(Sales[Region])    -- Distinct values respecting filters
DISTINCT(Sales[Region])  -- Distinct values, may differ with blanks
```

#### RELATED & RELATEDTABLE
```dax
-- In Sales table, get Product category
RELATED(Products[Category])

-- In Products table, count related sales
COUNTROWS(RELATEDTABLE(Sales))
```

### 3. Time Intelligence

#### Year-to-Date
```dax
Total YTD =
TOTALYTD(
    SUM(Sales[Amount]),
    'Date'[Date]
)

-- With fiscal year
Total Fiscal YTD =
TOTALYTD(
    SUM(Sales[Amount]),
    'Date'[Date],
    "6/30"  -- Fiscal year ends June 30
)
```

#### Quarter/Month-to-Date
```dax
Total QTD = TOTALQTD(SUM(Sales[Amount]), 'Date'[Date])
Total MTD = TOTALMTD(SUM(Sales[Amount]), 'Date'[Date])
```

#### Prior Period Comparisons
```dax
Sales PY =
CALCULATE(
    SUM(Sales[Amount]),
    SAMEPERIODLASTYEAR('Date'[Date])
)

Sales LM =
CALCULATE(
    SUM(Sales[Amount]),
    PREVIOUSMONTH('Date'[Date])
)

Sales LQ =
CALCULATE(
    SUM(Sales[Amount]),
    PREVIOUSQUARTER('Date'[Date])
)

Sales LY =
CALCULATE(
    SUM(Sales[Amount]),
    PREVIOUSYEAR('Date'[Date])
)
```

#### Date Ranges
```dax
-- Last 30 days
Last 30 Days =
CALCULATE(
    SUM(Sales[Amount]),
    DATESINPERIOD(
        'Date'[Date],
        MAX('Date'[Date]),
        -30,
        DAY
    )
)

-- Date range
Custom Period =
CALCULATE(
    SUM(Sales[Amount]),
    DATESBETWEEN(
        'Date'[Date],
        DATE(2024, 1, 1),
        DATE(2024, 12, 31)
    )
)
```

#### Period Over Period
```dax
Sales vs PY =
VAR CurrentSales = SUM(Sales[Amount])
VAR PriorYearSales =
    CALCULATE(
        SUM(Sales[Amount]),
        SAMEPERIODLASTYEAR('Date'[Date])
    )
RETURN
    CurrentSales - PriorYearSales

Sales Growth % =
DIVIDE(
    [Sales vs PY],
    CALCULATE(SUM(Sales[Amount]), SAMEPERIODLASTYEAR('Date'[Date])),
    0
)
```

#### Rolling Averages
```dax
3 Month Rolling Avg =
AVERAGEX(
    DATESINPERIOD(
        'Date'[Date],
        LASTDATE('Date'[Date]),
        -3,
        MONTH
    ),
    CALCULATE(SUM(Sales[Amount]))
)
```

### 4. Logical Functions

```dax
-- IF
Discount Category =
IF(
    Sales[Discount] > 0.2,
    "High",
    "Standard"
)

-- Nested IF
Price Band =
IF(
    Sales[UnitPrice] >= 100,
    "Premium",
    IF(
        Sales[UnitPrice] >= 50,
        "Standard",
        "Budget"
    )
)

-- SWITCH (better than nested IF)
Price Category =
SWITCH(
    TRUE(),
    Sales[UnitPrice] >= 100, "Premium",
    Sales[UnitPrice] >= 50, "Standard",
    Sales[UnitPrice] >= 20, "Budget",
    "Economy"
)

-- AND / OR
High Value Sale =
IF(
    AND(Sales[Amount] > 1000, Sales[Quantity] > 10),
    "Yes",
    "No"
)

Special Deal =
IF(
    OR(Sales[Discount] > 0.3, Sales[Amount] > 5000),
    "Yes",
    "No"
)

-- NOT
Not Returned =
IF(NOT(Sales[IsReturned]), Sales[Amount], 0)
```

### 5. Text Functions

```dax
-- Concatenation
Full Name = Customers[FirstName] & " " & Customers[LastName]
Full Name = CONCATENATE(Customers[FirstName], Customers[LastName])

-- Format
Formatted Date = FORMAT('Date'[Date], "MMM DD, YYYY")
Formatted Amount = FORMAT(Sales[Amount], "$#,##0.00")

-- Substring
LEFT(Products[SKU], 3)
RIGHT(Products[SKU], 4)
MID(Products[SKU], 4, 6)

-- Case conversion
UPPER(Customers[Email])
LOWER(Customers[Email])
PROPER(Customers[Name])

-- Trimming
TRIM(Customers[Name])

-- Length
LEN(Products[Description])

-- Find and replace
FIND("@", Customers[Email])
SUBSTITUTE(Products[Name], "Old", "New")
```

### 6. Mathematical Functions

```dax
-- Rounding
ROUND(Sales[Amount], 2)
ROUNDUP(Sales[Amount], 0)
ROUNDDOWN(Sales[Amount], 0)
MROUND(Sales[Amount], 5)  -- Round to nearest 5
FLOOR(Sales[Amount], 10)
CEILING(Sales[Amount], 10)

-- Other math
ABS(Sales[Variance])
SQRT(Sales[Area])
POWER(Sales[Base], 2)
EXP(Sales[Rate])
LN(Sales[Value])
LOG(Sales[Value], 10)
SIGN(Sales[Change])
MOD(Sales[Quantity], 12)
QUOTIENT(Sales[Quantity], 12)

-- Division with error handling
Safe Division = DIVIDE(Sales[Profit], Sales[Revenue], 0)
```

### 7. Information Functions

```dax
-- Testing
ISBLANK(Sales[Discount])
ISEMPTY(FILTER(Sales, Sales[Amount] > 10000))
ISERROR(DIVIDE(Sales[Profit], Sales[Revenue]))
ISNUMBER(Sales[Amount])
ISTEXT(Sales[Description])

-- Blank handling
COALESCE(Sales[Discount], 0)
BLANK()
```

### 8. Iterator Functions

```dax
-- SUMX
Total Revenue =
SUMX(
    Sales,
    Sales[Quantity] * Sales[UnitPrice]
)

-- AVERAGEX
Avg Order Value =
AVERAGEX(
    VALUES(Sales[OrderID]),
    CALCULATE(SUM(Sales[Amount]))
)

-- RANKX
Product Rank =
RANKX(
    ALL(Products[ProductName]),
    CALCULATE(SUM(Sales[Amount])),
    ,
    DESC,
    DENSE
)

-- CONCATENATEX
Product List =
CONCATENATEX(
    VALUES(Products[ProductName]),
    Products[ProductName],
    ", ",
    Products[ProductName],
    ASC
)
```

### 9. Table Functions

```dax
-- SELECTCOLUMNS
SELECTCOLUMNS(
    Sales,
    "Order ID", Sales[OrderID],
    "Total", Sales[Amount]
)

-- ADDCOLUMNS
ADDCOLUMNS(
    Products,
    "Total Sales", CALCULATE(SUM(Sales[Amount]))
)

-- SUMMARIZE
SUMMARIZE(
    Sales,
    Products[Category],
    "Total Sales", SUM(Sales[Amount]),
    "Avg Price", AVERAGE(Sales[UnitPrice])
)

-- CROSSJOIN
CROSSJOIN(
    VALUES(Products[Category]),
    VALUES('Date'[Year])
)

-- UNION
UNION(
    SELECTCOLUMNS(Table1, "ID", [ID]),
    SELECTCOLUMNS(Table2, "ID", [ID])
)

-- EXCEPT
EXCEPT(
    VALUES(Products[ProductID]),
    FILTER(Sales, Sales[IsReturned] = TRUE)
)
```

### 10. Statistical Functions

```dax
-- Ranking
Percentile 90 = PERCENTILE.INC(Sales[Amount], 0.9)

-- Distribution
Product Sales Rank =
RANKX(
    ALL(Products),
    [Total Sales],
    ,
    DESC
)

-- Correlation
CORREL(Sales[Quantity], Sales[Discount])

-- Beta distribution
BETA.DIST(0.4, 2, 5, TRUE)
```

## Variables

```dax
Profit Margin =
VAR TotalRevenue = SUM(Sales[Amount])
VAR TotalCost = SUM(Sales[Cost])
VAR Profit = TotalRevenue - TotalCost
RETURN
    DIVIDE(Profit, TotalRevenue, 0)
```

## Row Context vs Filter Context

### Row Context
Created by calculated columns and iterator functions:
```dax
-- Calculated Column
Sales[Total] = Sales[Quantity] * Sales[UnitPrice]
```

### Filter Context
Created by visuals, slicers, and CALCULATE:
```dax
-- Measure
Total Sales = SUM(Sales[Amount])  -- Respects filters
```

### Context Transition
```dax
-- Iterator creates row context, CALCULATE transitions to filter context
Avg Order Value =
AVERAGEX(
    VALUES(Sales[OrderID]),
    CALCULATE(SUM(Sales[Amount]))  -- Context transition
)
```

## Best Practices

1. **Use Variables**: Improve performance and readability
2. **Use DIVIDE**: Handles division by zero
3. **Avoid Calculated Columns**: Use measures when possible
4. **Use ISBLANK**: Instead of = BLANK()
5. **Filter Early**: Apply filters before expensive operations
6. **Use SELECTEDVALUE**: For single-value contexts
7. **Avoid Bidirectional Filters**: Use when necessary only
8. **Document Complex Measures**: Use comments

## Common Patterns

### % of Total
```dax
% of Total =
DIVIDE(
    SUM(Sales[Amount]),
    CALCULATE(
        SUM(Sales[Amount]),
        ALL(Products)
    ),
    0
)
```

### Running Total
```dax
Running Total =
CALCULATE(
    SUM(Sales[Amount]),
    FILTER(
        ALL('Date'[Date]),
        'Date'[Date] <= MAX('Date'[Date])
    )
)
```

### Same Period Last Year
```dax
Sales SPLY =
CALCULATE(
    [Total Sales],
    SAMEPERIODLASTYEAR('Date'[Date])
)
```
