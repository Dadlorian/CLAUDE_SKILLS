# Power BI Data Modeling Guide

## Semantic Model Design

### Star Schema Implementation

Create dimension and fact tables:

```powerquery
// DimDate table
let
    StartDate = #date(2020, 1, 1),
    EndDate = #date(2030, 12, 31),
    NumberOfDays = Duration.Days(EndDate - StartDate) + 1,
    Dates = List.Dates(StartDate, NumberOfDays, #duration(1,0,0,0)),
    TableFromList = Table.FromList(Dates, Splitter.SplitterByNothing()),
    ChangedType = Table.RenameColumns(TableFromList,{{"Column1", "Date"}}),
    InsertYear = Table.AddColumn(ChangedType, "Year", each Date.Year([Date])),
    InsertQuarter = Table.AddColumn(InsertYear, "Quarter", each Date.QuarterOfYear([Date])),
    InsertMonth = Table.AddColumn(InsertQuarter, "Month", each Date.Month([Date])),
    InsertMonthName = Table.AddColumn(InsertMonth, "MonthName", each Date.MonthName([Date])),
    InsertDay = Table.AddColumn(InsertMonthName, "Day", each Date.Day([Date])),
    InsertDayOfWeek = Table.AddColumn(InsertDay, "DayOfWeek", each Date.DayOfWeekName([Date]))
in
    InsertDayOfWeek
```

### Relationships

Configure relationships:
- One-to-Many from dimension to fact
- Single direction (default)
- Ensure referential integrity

### Hierarchies

```dax
// Create hierarchy in Date table
Calendar Hierarchy:
- Year
- Quarter
- Month
- Date

// Create hierarchy in Product table
Product Hierarchy:
- Category
- Subcategory
- Product
```

## DAX Measures

### Base Measures
```dax
Total Sales = SUM(Sales[Amount])
Total Cost = SUM(Sales[Cost])
Total Profit = [Total Sales] - [Total Cost]
Profit Margin = DIVIDE([Total Profit], [Total Sales], 0)
```

### Time Intelligence
```dax
Sales YTD = TOTALYTD([Total Sales], 'Date'[Date])
Sales LY = CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
YoY Growth = DIVIDE([Total Sales] - [Sales LY], [Sales LY], 0)
```

## Row-Level Security

```dax
// Create security role
[Region] = USERPRINCIPALNAME()

// Or dynamic security
VAR UserEmail = USERPRINCIPALNAME()
VAR UserRegions =
    CALCULATETABLE(
        VALUES(UserSecurity[Region]),
        UserSecurity[Email] = UserEmail
    )
RETURN
    [Region] IN UserRegions
```

## Performance Optimization

### 1. Data Model
- Use star schema
- Remove unnecessary columns
- Use appropriate data types
- Create date table
- Define relationships properly

### 2. DAX Optimization
- Use variables
- Avoid calculated columns
- Use DIVIDE function
- Filter early
- Avoid iterators when possible

### 3. Visuals
- Limit number of visuals per page
- Use slicers efficiently
- Avoid custom visuals if possible
- Consider aggregation tables

## Best Practices

1. **Model Design**
   - Star schema over snowflake
   - Conformed dimensions
   - Surrogate keys
   - Date table mandatory

2. **DAX**
   - Document complex measures
   - Use measure groups/folders
   - Consistent naming
   - Format strings

3. **Performance**
   - Incremental refresh for large datasets
   - Aggregations for detail tables
   - DirectQuery when needed
   - Composite models strategically
