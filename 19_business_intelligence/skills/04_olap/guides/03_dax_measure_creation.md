# DAX Measure Creation: Practical Guide

## Introduction

Comprehensive guide to creating effective DAX measures for Power BI and Tabular models.

## Basic Measures

### Simple Aggregations
```dax
Sales Amount = SUM(Sales[Amount])
Total Quantity = SUM(Sales[Quantity])
Average Price = AVERAGE(Sales[UnitPrice])
Customer Count = DISTINCTCOUNT(Sales[CustomerID])
```

### Calculated Measures
```dax
Profit = SUM(Sales[Amount]) - SUM(Sales[Cost])

Profit Margin % =
DIVIDE(
    [Profit],
    [Sales Amount],
    0
)
```

## Time Intelligence

### Year-to-Date
```dax
Sales YTD =
TOTALYTD(
    SUM(Sales[Amount]),
    'Date'[Date]
)

// Fiscal YTD
Sales Fiscal YTD =
TOTALYTD(
    SUM(Sales[Amount]),
    'Date'[Date],
    "6/30"
)
```

### Prior Period Comparisons
```dax
Sales LY =
CALCULATE(
    SUM(Sales[Amount]),
    SAMEPERIODLASTYEAR('Date'[Date])
)

YoY Growth % =
VAR CurrentPeriod = [Sales Amount]
VAR PriorPeriod = [Sales LY]
RETURN
    DIVIDE(CurrentPeriod - PriorPeriod, PriorPeriod, 0)
```

### Moving Calculations
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
```

## Advanced Patterns

### Context Transition
```dax
Avg Sales per Customer =
AVERAGEX(
    VALUES(Customer[CustomerID]),
    CALCULATE(SUM(Sales[Amount]))
)
```

### Variables for Performance
```dax
Complex Calculation =
VAR Revenue = SUM(Sales[Amount])
VAR Cost = SUM(Sales[Cost])
VAR Quantity = SUM(Sales[Quantity])
VAR Profit = Revenue - Cost
VAR Margin = DIVIDE(Profit, Revenue, 0)
RETURN
    IF(Quantity > 100, Margin * 1.1, Margin)
```

### SWITCH for Multiple Conditions
```dax
Performance Category =
SWITCH(
    TRUE(),
    [Sales Amount] > 1000000, "Excellent",
    [Sales Amount] > 500000, "Good",
    [Sales Amount] > 100000, "Average",
    "Below Average"
)
```

## Common Business Calculations

### Same Store Sales
```dax
Same Store Sales =
VAR CurrentStores = VALUES(Store[StoreID])
VAR PriorYearStores =
    CALCULATETABLE(
        VALUES(Store[StoreID]),
        DATEADD('Date'[Date], -1, YEAR)
    )
VAR SameStores = INTERSECT(CurrentStores, PriorYearStores)
RETURN
    CALCULATE(
        SUM(Sales[Amount]),
        KEEPFILTERS(SameStores)
    )
```

### ABC Classification
```dax
ABC Class =
VAR CumulativePct = [Cumulative % of Total]
RETURN
    SWITCH(
        TRUE(),
        CumulativePct <= 0.80, "A",
        CumulativePct <= 0.95, "B",
        "C"
    )
```

### Running Total
```dax
Running Total =
CALCULATE(
    SUM(Sales[Amount]),
    FILTER(
        ALL('Date'),
        'Date'[Date] <= MAX('Date'[Date])
    )
)
```

## Best Practices

1. **Use Variables** for complex calculations
2. **Use DIVIDE** instead of division operator
3. **Avoid Calculated Columns** when measures suffice
4. **Format measures** with appropriate strings
5. **Document complex logic** with comments
6. **Test with edge cases** (blanks, zeros, nulls)
7. **Optimize performance** with early filtering

## Measure Documentation Template

```dax
// Measure Name: YoY Growth %
// Purpose: Calculate year-over-year growth percentage
// Dependencies: Sales Amount, Date table
// Business Logic: (Current Year - Prior Year) / Prior Year
// Author: Data Team
// Date: 2024-01-15
// Last Modified: 2024-01-15

YoY Growth % =
VAR CurrentYear = [Sales Amount]
VAR PriorYear = [Sales LY]
RETURN
    IF(
        ISBLANK(PriorYear),
        BLANK(),
        DIVIDE(CurrentYear - PriorYear, PriorYear, 0)
    )
```
