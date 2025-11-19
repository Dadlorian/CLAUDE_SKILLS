# Tableau Calculations Reference

## Calculation Types Overview

### Basic Calculations
Simple expressions using fields, operators, and functions
```tableau
// Revenue per unit
[Revenue] / [Quantity]

// Profit margin percentage
([Revenue] - [Cost]) / [Revenue]

// Full name concatenation
[First Name] + " " + [Last Name]
```

### Table Calculations
Computations based on visible table data
```tableau
// Running total
RUNNING_SUM(SUM([Sales]))

// Percent of total
SUM([Sales]) / TOTAL(SUM([Sales]))

// Rank
RANK(SUM([Sales]))

// Moving average (3 periods)
WINDOW_AVG(SUM([Sales]), -2, 0)

// Year over year growth
(ZN(SUM([Sales])) - LOOKUP(ZN(SUM([Sales])), -12)) /
ABS(LOOKUP(ZN(SUM([Sales])), -12))
```

### Level of Detail (LOD) Expressions

#### FIXED - Independent of view dimensions
```tableau
// Customer lifetime value (total per customer)
{ FIXED [Customer ID] : SUM([Revenue]) }

// Average order value per customer
{ FIXED [Customer ID] : SUM([Sales]) / COUNTD([Order ID]) }

// First purchase date per customer
{ FIXED [Customer ID] : MIN([Order Date]) }
```

#### INCLUDE - Adds dimensions to view level
```tableau
// Average sales per state (when state not in view)
{ INCLUDE [State] : AVG([Sales]) }

// Total by category even if category in filter
{ INCLUDE [Category] : SUM([Sales]) }
```

#### EXCLUDE - Removes dimensions from view level
```tableau
// Overall average independent of row dimensions
{ EXCLUDE [Product] : AVG([Sales]) }

// Percentage of category total
SUM([Sales]) / { EXCLUDE [Product] : SUM([Sales]) }
```

### LOD Best Practices
1. **Performance**: FIXED is fastest, INCLUDE second, nested LODs slowest
2. **Aggregation**: LOD expressions must be wrapped in aggregation
3. **Filters**: Context filters apply before FIXED, normal filters after
4. **Nested LODs**: Avoid deeply nested expressions when possible

## Common Calculation Patterns

### Date Calculations
```tableau
// Fiscal year (starts July 1)
IF MONTH([Date]) >= 7
THEN YEAR([Date]) + 1
ELSE YEAR([Date])
END

// Days between dates
DATEDIFF('day', [Start Date], [End Date])

// Last day of month
DATEADD('day', -1, DATEADD('month', 1, DATETRUNC('month', [Date])))

// Week number in year
DATEPART('week', [Date])

// Same period last year
DATEADD('year', -1, [Date])
```

### Conditional Logic
```tableau
// Multiple conditions
CASE [Region]
  WHEN 'East' THEN 'Eastern Seaboard'
  WHEN 'West' THEN 'Western States'
  ELSE 'Other'
END

// IF-THEN-ELSEIF
IF [Sales] > 10000 THEN 'High'
ELSEIF [Sales] > 5000 THEN 'Medium'
ELSE 'Low'
END

// Nested IF with null handling
IF ISNULL([Discount]) THEN 0
ELSE [Sales] * [Discount]
END
```

### String Manipulations
```tableau
// Extract domain from email
SPLIT([Email], '@', 2)

// Remove whitespace
TRIM([Name])

// Replace text
REPLACE([Phone], '-', '')

// Left padding with zeros
RIGHT('00000' + STR([ID]), 5)

// Contains check (case insensitive)
CONTAINS(LOWER([Description]), 'urgent')
```

### Aggregation Functions
```tableau
// Distinct count
COUNTD([Customer ID])

// Conditional sum
SUM(IF [Category] = 'Electronics' THEN [Sales] END)

// Median using table calc
WINDOW_PERCENTILE(AVG([Sales]), 0.5)

// Weighted average
SUM([Sales] * [Quantity]) / SUM([Quantity])

// Mode (most frequent value) - approximate
ATTR(
  IF WINDOW_RANK(COUNTD([Product ID])) = 1
  THEN [Product ID]
  END
)
```

### Cohort Analysis
```tableau
// Cohort (first purchase month)
{ FIXED [Customer ID] :
  DATETRUNC('month', MIN([Order Date])) }

// Months since first purchase
DATEDIFF('month', [Cohort], [Order Date])

// Customer acquisition month
DATETRUNC('month', { FIXED [Customer ID] : MIN([Order Date]) })

// Cohort retention rate
COUNTD([Customer ID]) /
COUNTD(IF [Months Since First Purchase] = 0
       THEN [Customer ID] END)
```

### Statistical Calculations
```tableau
// Standard deviation
STDEV([Sales])

// Variance
VAR([Sales])

// Correlation
CORR([Sales], [Profit])

// Z-score
([Sales] - WINDOW_AVG(AVG([Sales]))) /
WINDOW_STDEV(AVG([Sales]))

// Percentile rank
RANK_PERCENTILE(SUM([Sales]))
```

## Advanced Patterns

### Parent-Child Hierarchies
```tableau
// Recursive hierarchy flattening (requires self-join)
// Level 1
{ FIXED [Employee ID] : MIN([Manager ID]) }

// Full path (requires table calc or prep work)
// Best done in data preparation layer
```

### Dynamic Threshold
```tableau
// Parameter-based filtering
IF [Sales] > [Sales Threshold Parameter]
THEN "Above"
ELSE "Below"
END

// Top N with parameter
IF RANK(SUM([Sales])) <= [Top N Parameter]
THEN [Product Name]
ELSE "Other"
END
```

### Complex Period Comparisons
```tableau
// Same week last year (accounting for week shift)
DATEADD('day',
  DATEDIFF('day',
    DATE(DATEPART('year', [Date])-1 & "-01-01"),
    DATETRUNC('week', [Date])
  ),
  DATE(DATEPART('year', [Date]) & "-01-01")
)

// Rolling 12-month calculation
IF [Date] >= DATEADD('month', -12, TODAY())
   AND [Date] < TODAY()
THEN [Sales]
END
```

### Progressive Calculations
```tableau
// Contribution to total (with running sum)
RUNNING_SUM(SUM([Sales])) / TOTAL(SUM([Sales]))

// Pareto analysis (80/20)
IF RUNNING_SUM(SUM([Sales])) <= 0.8 * TOTAL(SUM([Sales]))
THEN "Top 80%"
ELSE "Bottom 20%"
END
```

## Performance Optimization Tips

### 1. Calculation Efficiency
```tableau
// SLOW: Multiple LODs
{ FIXED [Customer] : SUM([Sales]) } /
{ FIXED : SUM([Sales]) }

// FAST: Single LOD with division outside
{ FIXED [Customer] : SUM([Sales]) } /
TOTAL(SUM([Sales]))
```

### 2. Use ATTR for Single Values
```tableau
// When dimension guaranteed single value in context
ATTR([Customer Name])  // Better than MIN([Customer Name])
```

### 3. Avoid String Comparisons in Aggregations
```tableau
// SLOW
SUM(IF [Category] = "Electronics" THEN [Sales] END)

// FAST: Use boolean field created in data source
SUM([Sales (Electronics)])
```

### 4. Pre-Aggregate in Data Source
```tableau
// Instead of complex LOD, create in data source:
// SELECT customer_id, SUM(sales) as total_sales
// GROUP BY customer_id

// Then simply use:
SUM([Total Sales])
```

## Function Categories

### Numeric Functions
- `ABS()`, `ROUND()`, `CEILING()`, `FLOOR()`
- `POWER()`, `SQUARE()`, `SQRT()`
- `EXP()`, `LN()`, `LOG()`
- `DIV()` - Integer division
- `ZN()` - Zero if null

### String Functions
- `LEFT()`, `RIGHT()`, `MID()`
- `FIND()`, `CONTAINS()`, `STARTSWITH()`, `ENDSWITH()`
- `UPPER()`, `LOWER()`, `PROPER()`
- `LTRIM()`, `RTRIM()`, `TRIM()`
- `SPLIT()`, `REPLACE()`
- `LEN()`, `SPACE()`

### Date Functions
- `DATEADD()`, `DATEDIFF()`, `DATEPART()`, `DATENAME()`
- `DATETRUNC()`, `DATEPARSE()`
- `YEAR()`, `MONTH()`, `DAY()`, `QUARTER()`
- `WEEK()`, `WEEKDAY()`
- `NOW()`, `TODAY()`
- `ISDATE()`

### Type Conversion
- `STR()` - To string
- `INT()`, `FLOAT()` - To number
- `DATE()`, `DATETIME()` - To date
- `BOOL()` - To boolean

### Logical Functions
- `IF`, `CASE`, `IIF()`
- `AND`, `OR`, `NOT`
- `ISNULL()`, `IFNULL()`, `ZN()`
- `ISDATE()`, `ISNULL()`

### Aggregate Functions
- `SUM()`, `AVG()`, `MIN()`, `MAX()`
- `COUNT()`, `COUNTD()`
- `MEDIAN()`, `PERCENTILE()`
- `STDEV()`, `STDEVP()`, `VAR()`, `VARP()`
- `ATTR()` - Attribute (single value or *)

### Table Calculation Functions
- `RUNNING_SUM()`, `RUNNING_AVG()`, `RUNNING_MIN()`, `RUNNING_MAX()`
- `WINDOW_SUM()`, `WINDOW_AVG()`, `WINDOW_MIN()`, `WINDOW_MAX()`
- `LOOKUP()`, `PREVIOUS_VALUE()`
- `RANK()`, `RANK_DENSE()`, `RANK_UNIQUE()`, `RANK_PERCENTILE()`
- `FIRST()`, `LAST()`, `INDEX()`, `SIZE()`
- `TOTAL()` - Aggregate over entire partition

## Common Errors & Solutions

### Error: "Cannot mix aggregate and non-aggregate"
```tableau
// WRONG
[Sales] / SUM([Quantity])

// CORRECT
SUM([Sales]) / SUM([Quantity])
// OR
[Sales] / { FIXED : SUM([Quantity]) }
```

### Error: "Cannot use LOD expression in another LOD"
```tableau
// WRONG
{ FIXED [Customer] :
  { FIXED [Order] : SUM([Sales]) } }

// CORRECT: Flatten to single LOD
{ FIXED [Customer], [Order] : SUM([Sales]) }
```

### Error: "Null values in calculation"
```tableau
// Add null handling
IFNULL([Value], 0)
// OR
ZN([Value])  // Zero if null
```

### Unexpected Filtering Behavior
```tableau
// Use context filters for LOD base
// Right-click dimension -> Add to Context

// Or use FIXED LOD to ignore filters
{ FIXED [Dimension] : SUM([Measure]) }
```

## Quick Reference Card

| Need | Use |
|------|-----|
| Running total | `RUNNING_SUM(SUM([Measure]))` |
| % of total | `SUM([Measure]) / TOTAL(SUM([Measure]))` |
| Rank | `RANK(SUM([Measure]))` |
| Moving average | `WINDOW_AVG(SUM([Measure]), -2, 0)` |
| Customer LTV | `{ FIXED [Customer] : SUM([Revenue]) }` |
| Previous value | `LOOKUP(SUM([Measure]), -1)` |
| Growth % | `(ZN(SUM([Sales])) - LOOKUP(ZN(SUM([Sales])), -1)) / ABS(LOOKUP(ZN(SUM([Sales])), -1))` |
| Year over year | Same as growth % with appropriate offset |
| Null to zero | `ZN([Field])` or `IFNULL([Field], 0)` |
| Conditional count | `COUNTD(IF [Condition] THEN [ID] END)` |

## Resources
- Tableau Calculation Language: https://help.tableau.com/current/pro/desktop/en-us/functions.htm
- LOD Expressions: https://help.tableau.com/current/pro/desktop/en-us/calculations_calculatedfields_lod.htm
- Table Calculations: https://help.tableau.com/current/pro/desktop/en-us/calculations_tablecalculations.htm
