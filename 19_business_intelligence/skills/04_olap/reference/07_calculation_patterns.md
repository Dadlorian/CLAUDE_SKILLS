# Calculation Patterns in OLAP

## Overview

Standard calculation patterns for implementing common analytical requirements in OLAP cubes using both MDX and DAX.

## Time Intelligence Calculations

### Year-to-Date (YTD)

#### MDX
```mdx
WITH MEMBER [Measures].[Sales YTD] AS
    AGGREGATE(
        PERIODSTODATE(
            [Date].[Calendar].[Year],
            [Date].[Calendar].CURRENTMEMBER
        ),
        [Measures].[Sales Amount]
    )
```

#### DAX
```dax
Sales YTD =
TOTALYTD(
    SUM(Sales[Amount]),
    'Date'[Date],
    "12/31"  -- Calendar year end
)

// Fiscal YTD
Sales Fiscal YTD =
TOTALYTD(
    SUM(Sales[Amount]),
    'Date'[Date],
    "6/30"  -- Fiscal year ends June 30
)
```

### Quarter-to-Date (QTD) and Month-to-Date (MTD)

#### MDX
```mdx
WITH MEMBER [Measures].[Sales QTD] AS
    AGGREGATE(
        PERIODSTODATE(
            [Date].[Calendar].[Quarter],
            [Date].[Calendar].CURRENTMEMBER
        ),
        [Measures].[Sales Amount]
    )

MEMBER [Measures].[Sales MTD] AS
    AGGREGATE(
        PERIODSTODATE(
            [Date].[Calendar].[Month],
            [Date].[Calendar].CURRENTMEMBER
        ),
        [Measures].[Sales Amount]
    )
```

#### DAX
```dax
Sales QTD = TOTALQTD(SUM(Sales[Amount]), 'Date'[Date])
Sales MTD = TOTALMTD(SUM(Sales[Amount]), 'Date'[Date])
```

### Prior Period Comparisons

#### MDX - Year-over-Year
```mdx
WITH MEMBER [Measures].[Sales LY] AS
    (
        PARALLELPERIOD(
            [Date].[Calendar].[Year],
            1,
            [Date].[Calendar].CURRENTMEMBER
        ),
        [Measures].[Sales Amount]
    )

MEMBER [Measures].[YoY Change] AS
    [Measures].[Sales Amount] - [Measures].[Sales LY]

MEMBER [Measures].[YoY % Change] AS
    IIF(
        [Measures].[Sales LY] = 0,
        NULL,
        ([Measures].[Sales Amount] - [Measures].[Sales LY]) /
        [Measures].[Sales LY]
    ),
    FORMAT_STRING = "Percent"
```

#### DAX - Multiple Prior Periods
```dax
Sales LY =
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

// Generic Prior Period
Sales Prior Period =
VAR PriorPeriod =
    DATEADD('Date'[Date], -1, YEAR)
RETURN
    CALCULATE(SUM(Sales[Amount]), PriorPeriod)

// YoY Growth %
YoY Growth % =
VAR CurrentPeriod = SUM(Sales[Amount])
VAR PriorYear = [Sales LY]
RETURN
    DIVIDE(CurrentPeriod - PriorYear, PriorYear, 0)
```

### Rolling/Moving Averages

#### MDX
```mdx
WITH MEMBER [Measures].[3 Month Rolling Avg] AS
    AVG(
        LASTPERIODS(
            3,
            [Date].[Calendar].CURRENTMEMBER
        ),
        [Measures].[Sales Amount]
    )

MEMBER [Measures].[12 Month Rolling Avg] AS
    AVG(
        LASTPERIODS(12, [Date].[Calendar].CURRENTMEMBER),
        [Measures].[Sales Amount]
    )
```

#### DAX
```dax
3 Month Rolling Avg =
AVERAGEX(
    DATESINPERIOD(
        'Date'[Date],
        LASTDATE('Date'[Date]),
        -3,
        MONTH
    ),
    [Sales Amount]
)

// Alternative with window functions
Rolling 12 Month Avg =
VAR LastDate = MAX('Date'[Date])
VAR Last12Months =
    DATESINPERIOD('Date'[Date], LastDate, -12, MONTH)
RETURN
    CALCULATE(
        AVERAGE(Sales[Amount]),
        Last12Months
    )
```

### Cumulative Totals (Running Total)

#### MDX
```mdx
WITH MEMBER [Measures].[Running Total] AS
    SUM(
        PERIODSTODATE(
            [Date].[Calendar].[Year],
            [Date].[Calendar].CURRENTMEMBER
        ),
        [Measures].[Sales Amount]
    )
```

#### DAX
```dax
Running Total =
CALCULATE(
    SUM(Sales[Amount]),
    FILTER(
        ALL('Date'),
        'Date'[Date] <= MAX('Date'[Date])
    )
)

// Within year
Running Total YTD =
VAR MaxDate = MAX('Date'[Date])
VAR MaxYear = YEAR(MaxDate)
RETURN
    CALCULATE(
        SUM(Sales[Amount]),
        FILTER(
            ALL('Date'),
            'Date'[Date] <= MaxDate &&
            YEAR('Date'[Date]) = MaxYear
        )
    )
```

## Contribution Analysis

### Percentage of Parent

#### MDX
```mdx
WITH MEMBER [Measures].[% of Category] AS
    [Measures].[Sales Amount] /
    (
        [Product].[Category].CURRENTMEMBER,
        [Measures].[Sales Amount]
    ),
    FORMAT_STRING = "Percent"

MEMBER [Measures].[% of Total] AS
    [Measures].[Sales Amount] /
    (
        [Product].[Category].[All],
        [Measures].[Sales Amount]
    ),
    FORMAT_STRING = "Percent"
```

#### DAX
```dax
% of Category =
VAR CurrentSales = SUM(Sales[Amount])
VAR CategorySales =
    CALCULATE(
        SUM(Sales[Amount]),
        ALLEXCEPT(Products, Products[Category])
    )
RETURN
    DIVIDE(CurrentSales, CategorySales, 0)

% of Total =
VAR CurrentSales = SUM(Sales[Amount])
VAR TotalSales = CALCULATE(SUM(Sales[Amount]), ALL(Products))
RETURN
    DIVIDE(CurrentSales, TotalSales, 0)

% of Parent (Generic) =
DIVIDE(
    SUM(Sales[Amount]),
    CALCULATE(
        SUM(Sales[Amount]),
        ALLSELECTED()
    ),
    0
)
```

### Percentage of Grand Total

#### DAX
```dax
% of Grand Total =
DIVIDE(
    SUM(Sales[Amount]),
    CALCULATE(
        SUM(Sales[Amount]),
        ALL(Sales)
    ),
    0
)

// Respecting certain filters
% of Visual Total =
DIVIDE(
    SUM(Sales[Amount]),
    CALCULATE(
        SUM(Sales[Amount]),
        ALLSELECTED(Sales)
    ),
    0
)
```

## Ranking and Top N

### Ranking

#### MDX
```mdx
WITH MEMBER [Measures].[Product Rank] AS
    RANK(
        [Product].[Product].CURRENTMEMBER,
        [Product].[Product].MEMBERS,
        [Measures].[Sales Amount]
    )

-- Dense ranking (no gaps)
MEMBER [Measures].[Dense Rank] AS
    RANK(
        [Product].[Product].CURRENTMEMBER,
        ORDER(
            [Product].[Product].MEMBERS,
            [Measures].[Sales Amount],
            BDESC
        ),
        [Measures].[Sales Amount]
    )
```

#### DAX
```dax
Product Rank =
RANKX(
    ALL(Products[ProductName]),
    [Sales Amount],
    ,
    DESC,
    Dense
)

// Within category
Rank in Category =
RANKX(
    ALLEXCEPT(Products, Products[Category]),
    [Sales Amount],
    ,
    DESC,
    Dense
)

// Percentile Rank
Percentile Rank =
VAR CurrentRank = [Product Rank]
VAR TotalProducts = COUNTROWS(ALL(Products))
RETURN
    DIVIDE(CurrentRank, TotalProducts, 0)
```

### Top N Selection

#### MDX
```mdx
WITH SET [Top 10 Products] AS
    TOPCOUNT(
        [Product].[Product].MEMBERS,
        10,
        [Measures].[Sales Amount]
    )

-- Top N with Others
SET [Top 5 with Others] AS
    TOPCOUNT([Product].[Product].MEMBERS, 5, [Measures].[Sales Amount])
    +
    {[Product].[Product].[All].[Other]}

-- Dynamic Top N
MEMBER [Measures].[Top N Count] AS 10
SET [Top N Products] AS
    TOPCOUNT(
        [Product].[Product].MEMBERS,
        [Measures].[Top N Count],
        [Measures].[Sales Amount]
    )
```

#### DAX
```dax
Sales Top 10 Products =
VAR Top10 =
    TOPN(
        10,
        ALL(Products[ProductName]),
        [Sales Amount],
        DESC
    )
RETURN
    CALCULATE(
        SUM(Sales[Amount]),
        KEEPFILTERS(Top10)
    )

// Dynamic Top N with parameter
Top N Sales =
VAR N = SELECTEDVALUE('Top N'[Value], 10)
VAR TopN =
    TOPN(
        N,
        ALL(Products[ProductName]),
        [Sales Amount],
        DESC
    )
RETURN
    CALCULATE(SUM(Sales[Amount]), TopN)

// Is in Top N (for filtering)
Is Top 10 Product =
VAR CurrentProduct = SELECTEDVALUE(Products[ProductName])
VAR Top10 =
    TOPN(10, ALL(Products[ProductName]), [Sales Amount], DESC)
RETURN
    CurrentProduct IN Top10
```

## Statistical Calculations

### Averages and Variance

#### MDX
```mdx
WITH MEMBER [Measures].[Avg Sales] AS
    AVG(
        [Product].[Product].MEMBERS,
        [Measures].[Sales Amount]
    )

MEMBER [Measures].[Variance from Avg] AS
    [Measures].[Sales Amount] - [Measures].[Avg Sales]

MEMBER [Measures].[% Variance from Avg] AS
    ([Measures].[Sales Amount] - [Measures].[Avg Sales]) /
    [Measures].[Avg Sales],
    FORMAT_STRING = "Percent"
```

#### DAX
```dax
Average Sales =
AVERAGEX(
    ALL(Products[ProductName]),
    [Sales Amount]
)

Variance from Average =
[Sales Amount] - [Average Sales]

Standard Deviation =
STDEVX.P(
    ALL(Products[ProductName]),
    [Sales Amount]
)

Z-Score =
VAR Avg = [Average Sales]
VAR StdDev = [Standard Deviation]
RETURN
    DIVIDE([Sales Amount] - Avg, StdDev, 0)
```

### Weighted Averages

#### DAX
```dax
Weighted Avg Price =
SUMX(
    Sales,
    Sales[Quantity] * Sales[UnitPrice]
) /
SUM(Sales[Quantity])

// Alternative
Weighted Avg =
DIVIDE(
    SUMX(Sales, Sales[Quantity] * Sales[UnitPrice]),
    SUM(Sales[Quantity]),
    0
)
```

## ABC Analysis (Pareto)

#### DAX
```dax
// Cumulative % of Total
Cumulative % =
VAR CurrentAmount = SUM(Sales[Amount])
VAR CurrentProduct = SELECTEDVALUE(Products[ProductName])
VAR ProductsRanked =
    ADDCOLUMNS(
        ALL(Products[ProductName]),
        "@Sales", [Sales Amount]
    )
VAR ProductsOrdered =
    FILTER(
        ProductsRanked,
        [@Sales] >= CurrentAmount
    )
VAR CumulativeAmount =
    SUMX(ProductsOrdered, [@Sales])
VAR TotalAmount =
    CALCULATE(SUM(Sales[Amount]), ALL(Products))
RETURN
    DIVIDE(CumulativeAmount, TotalAmount, 0)

// ABC Classification
ABC Class =
VAR CumPct = [Cumulative %]
RETURN
    SWITCH(
        TRUE(),
        CumPct <= 0.80, "A",
        CumPct <= 0.95, "B",
        "C"
    )
```

## Same Store Sales

#### DAX
```dax
Same Store Sales =
VAR CurrentStores =
    VALUES(Stores[StoreID])
VAR PriorYearDate =
    DATEADD('Date'[Date], -1, YEAR)
VAR StoresOpenPriorYear =
    CALCULATETABLE(
        VALUES(Stores[StoreID]),
        PriorYearDate,
        Stores[OpenDate] <= MAX('Date'[Date])
    )
VAR SameStores =
    INTERSECT(CurrentStores, StoresOpenPriorYear)
RETURN
    CALCULATE(
        SUM(Sales[Amount]),
        KEEPFILTERS(SameStores)
    )

Same Store Sales Growth % =
VAR CurrentSSS = [Same Store Sales]
VAR PriorYearSSS =
    CALCULATE(
        [Same Store Sales],
        SAMEPERIODLASTYEAR('Date'[Date])
    )
RETURN
    DIVIDE(CurrentSSS - PriorYearSSS, PriorYearSSS, 0)
```

## Budget Variance Analysis

#### DAX
```dax
Budget Variance =
[Actual Sales] - [Budget Sales]

Budget Variance % =
DIVIDE(
    [Budget Variance],
    [Budget Sales],
    0
)

// Favorable/Unfavorable
Variance Status =
VAR Variance = [Budget Variance]
RETURN
    SWITCH(
        TRUE(),
        Variance > 0, "Favorable",
        Variance < 0, "Unfavorable",
        "On Target"
    )

// Traffic light indicator
Variance Indicator =
VAR VariancePct = [Budget Variance %]
RETURN
    SWITCH(
        TRUE(),
        VariancePct >= 0.05, "🟢",
        VariancePct <= -0.05, "🔴",
        "🟡"
    )
```

## Customer Cohort Analysis

#### DAX
```dax
// First purchase date
Customer First Purchase =
MINX(
    RELATEDTABLE(Sales),
    Sales[OrderDate]
)

// Cohort (month of first purchase)
Customer Cohort =
FORMAT([Customer First Purchase], "YYYY-MM")

// Months since first purchase
Months Since First Purchase =
DATEDIFF(
    [Customer First Purchase],
    MAX('Date'[Date]),
    MONTH
)

// Cohort retention
Cohort Retention =
VAR CohortCustomers =
    CALCULATE(
        DISTINCTCOUNT(Sales[CustomerID]),
        ALLEXCEPT(Customers, Customers[Customer Cohort])
    )
VAR ActiveCustomers =
    DISTINCTCOUNT(Sales[CustomerID])
RETURN
    DIVIDE(ActiveCustomers, CohortCustomers, 0)
```

## Best Practices

### 1. Performance Optimization
```dax
// ✓ Good - Filter early
Optimized Calc =
VAR FilteredData =
    FILTER(Sales, Sales[Amount] > 1000)
RETURN
    SUMX(FilteredData, Sales[Amount] * Sales[Quantity])

// ✗ Poor - Calculate then filter
Slow Calc =
SUMX(
    FILTER(Sales, Sales[Amount] > 1000),
    Sales[Amount] * Sales[Quantity]
)
```

### 2. Use Variables
```dax
// ✓ Good - Calculate once
Efficient =
VAR CurrentSales = SUM(Sales[Amount])
VAR PriorSales = [Sales LY]
VAR Variance = CurrentSales - PriorSales
RETURN
    DIVIDE(Variance, PriorSales, 0)

// ✗ Poor - Recalculate multiple times
Inefficient =
DIVIDE(
    SUM(Sales[Amount]) - [Sales LY],
    [Sales LY],
    0
)
```

### 3. Error Handling
```dax
// Always handle division by zero
Safe Division = DIVIDE([Numerator], [Denominator], 0)

// Handle blank values
Safe Calc =
VAR Value = [Some Measure]
RETURN
    IF(ISBLANK(Value), 0, Value)
```

### 4. Format Strings
```mdx
WITH MEMBER [Measures].[Profit %] AS
    [Measures].[Profit] / [Measures].[Sales],
    FORMAT_STRING = "Percent"

MEMBER [Measures].[Sales Amount] AS
    ...,
    FORMAT_STRING = "$#,##0.00"
```

### 5. Documentation
```dax
// Document complex calculations
YoY Growth % =
-- Calculates year-over-year growth percentage
-- Returns BLANK if no prior year data exists
VAR CurrentYear = SUM(Sales[Amount])
VAR PriorYear = [Sales LY]
RETURN
    IF(
        ISBLANK(PriorYear),
        BLANK(),
        DIVIDE(CurrentYear - PriorYear, PriorYear, 0)
    )
```
