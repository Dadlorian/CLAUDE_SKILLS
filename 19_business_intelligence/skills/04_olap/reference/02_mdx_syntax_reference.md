# MDX Syntax Reference

## Overview

MDX (Multidimensional Expressions) is the standard query language for OLAP cubes, providing powerful capabilities for multidimensional analysis.

## Basic Query Structure

```mdx
SELECT
  [columns] ON COLUMNS,
  [rows] ON ROWS
FROM [Cube]
WHERE [slicer]
```

## Axes

### Axis Specifications
```mdx
ON COLUMNS (Axis 0)
ON ROWS (Axis 1)
ON PAGES (Axis 2)
ON SECTIONS (Axis 3)
ON CHAPTERS (Axis 4)
```

### Alternative Syntax
```mdx
ON AXIS(0)  -- Same as ON COLUMNS
ON AXIS(1)  -- Same as ON ROWS
```

## Member References

### Fully Qualified
```mdx
[Dimension].[Hierarchy].[Level].[Member]
[Date].[Calendar].[Year].[2024]
```

### Shorthand
```mdx
[Date].[Calendar].[2024]  -- When level is implicit
[Date].[2024]              -- When hierarchy is implicit
```

### Member Properties
```mdx
[Product].[Category].[Electronics].Properties("Description")
[Customer].[Customer].[John Smith].MEMBER_CAPTION
```

## Sets

### Explicit Sets
```mdx
{[2023], [2024]}
{[Product].[Category].[Electronics], [Product].[Category].[Clothing]}
```

### Empty Set
```mdx
{}
```

### Set Functions

#### MEMBERS
```mdx
[Date].[Year].MEMBERS
-- Returns all year members
```

#### CHILDREN
```mdx
[Product].[Category].[Electronics].CHILDREN
-- Returns subcategories under Electronics
```

#### DESCENDANTS
```mdx
DESCENDANTS(
  [Geography].[Country].[USA],
  [Geography].[City],
  SELF
)
```

#### FILTER
```mdx
FILTER(
  [Product].[Product].MEMBERS,
  [Measures].[Sales Amount] > 100000
)
```

#### TOPCOUNT / BOTTOMCOUNT
```mdx
TOPCOUNT(
  [Product].[Product].MEMBERS,
  10,
  [Measures].[Sales Amount]
)
```

#### ORDER
```mdx
ORDER(
  [Customer].[Customer].MEMBERS,
  [Measures].[Sales Amount],
  BDESC  -- Breaking hierarchy, descending
)
```

#### CROSSJOIN
```mdx
CROSSJOIN(
  [Date].[Year].MEMBERS,
  [Product].[Category].MEMBERS
)
```

#### UNION
```mdx
UNION(
  {[Date].[2023]},
  {[Date].[2024]}
)
```

#### EXCEPT
```mdx
EXCEPT(
  [Product].[Category].MEMBERS,
  {[Product].[Category].[Unknown]}
)
```

## Tuples

### Single Tuple
```mdx
([Date].[2024], [Product].[Electronics], [Measures].[Sales Amount])
```

### Tuple in Query
```mdx
SELECT
  [Measures].[Sales Amount] ON COLUMNS,
  [Product].[Category].MEMBERS ON ROWS
FROM [Sales]
WHERE ([Date].[2024], [Geography].[USA])
```

## Calculated Members

### Basic Syntax
```mdx
WITH MEMBER [Measures].[Profit]
AS [Measures].[Sales Amount] - [Measures].[Cost]

SELECT
  {[Measures].[Sales Amount], [Measures].[Cost], [Measures].[Profit]} ON COLUMNS,
  [Product].[Category].MEMBERS ON ROWS
FROM [Sales]
```

### Format String
```mdx
WITH MEMBER [Measures].[Profit Margin]
AS ([Measures].[Profit] / [Measures].[Sales Amount]) * 100,
FORMAT_STRING = "0.00%"
```

### Solve Order
```mdx
WITH MEMBER [Measures].[Calc1] AS expression1, SOLVE_ORDER = 1
    MEMBER [Measures].[Calc2] AS expression2, SOLVE_ORDER = 2
```

## Named Sets

```mdx
WITH SET [Top10Products] AS
  TOPCOUNT(
    [Product].[Product].MEMBERS,
    10,
    [Measures].[Sales Amount]
  )

SELECT
  [Measures].[Sales Amount] ON COLUMNS,
  [Top10Products] ON ROWS
FROM [Sales]
```

## Time Intelligence Functions

### ParallelPeriod
```mdx
-- Prior year same period
PARALLELPERIOD(
  [Date].[Calendar].[Year],
  1,
  [Date].[Calendar].CURRENTMEMBER
)
```

### PeriodsToDate
```mdx
-- Year to date
PERIODSTODATE(
  [Date].[Calendar].[Year],
  [Date].[Calendar].CURRENTMEMBER
)
```

### LastPeriods
```mdx
-- Last 12 months
LASTPERIODS(
  12,
  [Date].[Calendar].CURRENTMEMBER
)
```

### OpeningPeriod / ClosingPeriod
```mdx
-- First month of year
OPENINGPERIOD([Date].[Month], [Date].[Year].[2024])

-- Last month of year
CLOSINGPERIOD([Date].[Month], [Date].[Year].[2024])
```

## Aggregate Functions

### SUM
```mdx
SUM(
  [Date].[Calendar].[2024].CHILDREN,
  [Measures].[Sales Amount]
)
```

### AVG
```mdx
AVG(
  [Product].[Category].MEMBERS,
  [Measures].[Unit Price]
)
```

### COUNT
```mdx
COUNT([Product].[Product].MEMBERS)
COUNT([Customer].[Customer].MEMBERS, EXCLUDEEMPTY)
```

### MIN / MAX
```mdx
MIN([Measures].[Unit Price])
MAX([Measures].[Sales Amount])
```

### AGGREGATE
```mdx
-- Smart aggregation based on measure type
AGGREGATE(
  [Date].[Calendar].[2024].CHILDREN,
  [Measures].[Balance]
)
```

## Conditional Logic

### IIF
```mdx
IIF(
  [Measures].[Sales Amount] > 100000,
  "High",
  "Low"
)
```

### CASE
```mdx
CASE
  WHEN [Measures].[Sales Amount] > 1000000 THEN "Premium"
  WHEN [Measures].[Sales Amount] > 100000 THEN "Standard"
  ELSE "Basic"
END
```

## Comparison Operators

```mdx
=   -- Equal
<>  -- Not equal
>   -- Greater than
<   -- Less than
>=  -- Greater than or equal
<=  -- Less than or equal
```

## Logical Operators

```mdx
AND
OR
NOT
XOR
```

## String Functions

### Concatenation
```mdx
[Customer].[FirstName] + " " + [Customer].[LastName]
```

### Substring
```mdx
LEFT([Product].[ProductName], 10)
RIGHT([Customer].[PostalCode], 4)
MID([Product].[SKU], 3, 5)
```

## Numeric Functions

```mdx
ROUND([Measures].[Unit Price], 2)
FLOOR([Measures].[Quantity] / 12)
CEILING([Measures].[Shipping Weight])
ABS([Measures].[Variance])
```

## Current Member

```mdx
[Date].[Calendar].CURRENTMEMBER
[Product].[Category].CURRENTMEMBER.MEMBER_CAPTION
```

## Hierarchy Navigation

### Parent
```mdx
[Product].[Category].[Electronics].[Laptops].PARENT
-- Returns [Electronics]
```

### Ancestor
```mdx
ANCESTOR(
  [Geography].[City].[Seattle],
  [Geography].[Country]
)
```

### Lead / Lag
```mdx
[Date].[Calendar].CURRENTMEMBER.LAG(1)  -- Prior period
[Date].[Calendar].CURRENTMEMBER.LEAD(1) -- Next period
```

## Scope Statements

```mdx
SCOPE([Date].[Calendar].[2024]);
  THIS = [Measures].[Budget] * 1.1;
END SCOPE;
```

## Comments

```mdx
-- Single line comment

/* Multi-line
   comment */
```

## Best Practices

1. **Use fully qualified names** for clarity
2. **Leverage named sets** for reusable logic
3. **Optimize set operations** (filter early, minimize cross joins)
4. **Use appropriate aggregation functions** for measure types
5. **Consider solve order** for calculated members
6. **Add comments** for complex logic
7. **Test performance** with production data volumes
8. **Use NONEMPTY** to reduce result size

## Common Patterns

### Year-over-Year Growth
```mdx
WITH MEMBER [Measures].[YoY Growth %] AS
  (
    ([Measures].[Sales Amount], [Date].[Calendar].CURRENTMEMBER) -
    ([Measures].[Sales Amount], PARALLELPERIOD([Date].[Calendar].[Year], 1))
  ) /
  ([Measures].[Sales Amount], PARALLELPERIOD([Date].[Calendar].[Year], 1)) * 100,
  FORMAT_STRING = "0.00%"
```

### Moving Average
```mdx
WITH MEMBER [Measures].[3 Month Avg] AS
  AVG(
    LASTPERIODS(3, [Date].[Calendar].CURRENTMEMBER),
    [Measures].[Sales Amount]
  )
```

### Contribution Percentage
```mdx
WITH MEMBER [Measures].[% of Total] AS
  [Measures].[Sales Amount] /
  ([Measures].[Sales Amount], [Product].[Category].[All]),
  FORMAT_STRING = "0.00%"
```
