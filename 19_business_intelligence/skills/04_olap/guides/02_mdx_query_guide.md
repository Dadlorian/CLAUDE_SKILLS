# MDX Query Writing: Practical Guide

## Introduction

Step-by-step guide to writing effective MDX queries for OLAP cubes.

## Basic Query Structure

### Simple Query
```mdx
SELECT
  [Measures].[Sales Amount] ON COLUMNS,
  [Product].[Category].MEMBERS ON ROWS
FROM [Sales]
```

### Multi-Axis Query
```mdx
SELECT
  [Measures].[Sales Amount] ON COLUMNS,
  [Product].[Category].MEMBERS ON ROWS,
  [Date].[Calendar].[Year].MEMBERS ON PAGES
FROM [Sales]
```

## Filtering with WHERE Clause

### Single Filter
```mdx
SELECT
  [Measures].[Sales Amount] ON COLUMNS,
  [Product].[Category].MEMBERS ON ROWS
FROM [Sales]
WHERE [Date].[Calendar].[2024]
```

### Multiple Filters (Tuple)
```mdx
SELECT
  [Measures].[Sales Amount] ON COLUMNS,
  [Product].[Category].MEMBERS ON ROWS
FROM [Sales]
WHERE ([Date].[Calendar].[2024], [Geography].[Country].[USA])
```

## Common Query Patterns

### Top N Products
```mdx
SELECT
  [Measures].[Sales Amount] ON COLUMNS,
  TOPCOUNT(
    [Product].[Product].MEMBERS,
    10,
    [Measures].[Sales Amount]
  ) ON ROWS
FROM [Sales]
```

### Year-over-Year Comparison
```mdx
WITH MEMBER [Measures].[Sales LY] AS
  (
    PARALLELPERIOD([Date].[Calendar].[Year], 1),
    [Measures].[Sales Amount]
  )

MEMBER [Measures].[YoY Growth] AS
  [Measures].[Sales Amount] - [Measures].[Sales LY]

SELECT
  {
    [Measures].[Sales Amount],
    [Measures].[Sales LY],
    [Measures].[YoY Growth]
  } ON COLUMNS,
  [Date].[Calendar].[Month].MEMBERS ON ROWS
FROM [Sales]
WHERE [Date].[Calendar].[2024]
```

### Period-to-Date
```mdx
WITH MEMBER [Measures].[YTD Sales] AS
  AGGREGATE(
    PERIODSTODATE(
      [Date].[Calendar].[Year],
      [Date].[Calendar].CURRENTMEMBER
    ),
    [Measures].[Sales Amount]
  )

SELECT
  {[Measures].[Sales Amount], [Measures].[YTD Sales]} ON COLUMNS,
  [Date].[Calendar].[Month].MEMBERS ON ROWS
FROM [Sales]
WHERE [Date].[Calendar].[2024]
```

## Advanced Techniques

### NONEMPTY for Performance
```mdx
SELECT
  [Measures].[Sales Amount] ON COLUMNS,
  NONEMPTY(
    [Product].[Product].MEMBERS,
    [Measures].[Sales Amount]
  ) ON ROWS
FROM [Sales]
```

### Recursive Hierarchy Navigation
```mdx
WITH SET [AllDescendants] AS
  DESCENDANTS(
    [Employee].[Org].[CEO],
    [Employee].[Org].[Employee],
    SELF_AND_AFTER
  )

SELECT
  [Measures].[Sales Amount] ON COLUMNS,
  [AllDescendants] ON ROWS
FROM [Sales]
```

### Dynamic Sets
```mdx
WITH SET [DynamicSet] AS
  IIF(
    [Measures].[Sales Amount] > 100000,
    TOPCOUNT([Product].MEMBERS, 20, [Measures].[Sales Amount]),
    TOPCOUNT([Product].MEMBERS, 10, [Measures].[Sales Amount])
  )

SELECT
  [Measures].[Sales Amount] ON COLUMNS,
  [DynamicSet] ON ROWS
FROM [Sales]
```

## Best Practices

1. **Use NONEMPTY** to reduce result sets
2. **Filter early** with WHERE clause or subselects
3. **Leverage calculated members** for reusability
4. **Use named sets** for complex sets
5. **Avoid large crossjoins**
6. **Test with production data volumes**

## Common Patterns Library

### Contribution Percentage
```mdx
WITH MEMBER [Measures].[% of Total] AS
  [Measures].[Sales Amount] /
  ([Measures].[Sales Amount], [Product].[Category].[All]),
  FORMAT_STRING = "Percent"
```

### Ranking
```mdx
WITH MEMBER [Measures].[Rank] AS
  RANK(
    [Product].[Product].CURRENTMEMBER,
    ORDER([Product].[Product].MEMBERS, [Measures].[Sales Amount], BDESC)
  )
```

### Moving Average
```mdx
WITH MEMBER [Measures].[3 Month Avg] AS
  AVG(
    LASTPERIODS(3, [Date].[Calendar].CURRENTMEMBER),
    [Measures].[Sales Amount]
  )
```
