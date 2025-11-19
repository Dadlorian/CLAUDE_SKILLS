# Qlik Sense Expressions Reference

## Set Analysis Fundamentals

### Basic Syntax
```qlik
Sum({<Field1={'Value1'}, Field2={'Value2'}>} Sales)
```

### Set Analysis Structure
```
{[Set Identifier] [Set Modifiers]}
```

**Set Identifiers:**
- `$` - Current selection
- `1` - All records (ignores selection)
- `0` - Empty set
- `$1` - Default bookmark
- `BM01` - Specific bookmark

### Common Set Analysis Patterns

#### Ignore All Selections
```qlik
// Total sales ignoring all filters
Sum({1} Sales)

// Count of all customers regardless of selection
Count({1} DISTINCT CustomerID)
```

#### Ignore Specific Fields
```qlik
// Ignore Year selection, keep all others
Sum({<Year=>} Sales)

// Ignore multiple fields
Sum({<Year=, Region=, Product=>} Sales)
```

#### Set Specific Values
```qlik
// Sales for specific year
Sum({<Year={2024}>} Sales)

// Multiple values
Sum({<Year={2023, 2024}>} Sales)

// Range
Sum({<Year={">=$(=Year(Today())-5)"}>} Sales)
```

#### Previous Year
```qlik
// Prior year sales
Sum({<Year={$(=Max(Year)-1)}>} Sales)

// Prior year with same month
Sum({<
  Year={$(=Max(Year)-1)},
  Month={$(=Max(Month))}
>} Sales)
```

#### Year to Date
```qlik
// YTD current year
Sum({<
  Year={$(=Max(Year))},
  MonthNum={"<=$(=Max(MonthNum))"}
>} Sales)

// YTD prior year
Sum({<
  Year={$(=Max(Year)-1)},
  MonthNum={"<=$(=Max(MonthNum))"}
>} Sales)
```

#### Advanced Set Operations

**Set Union (OR)**
```qlik
// Sales in East OR West region
Sum({<Region={'East','West'}>} Sales)
```

**Set Intersection (AND)**
```qlik
// High value customers in East region
Sum({<
  CustomerID=P({<Region={'East'}>} DISTINCT CustomerID) *
  CustomerID=P({<Sales={">10000"}>} DISTINCT CustomerID)
>} Sales)
```

**Set Difference (Exclusion)**
```qlik
// All except cancelled orders
Sum({<Status-={'Cancelled'}>} Sales)

// Customers who bought Product A but not Product B
Count({<
  CustomerID=P({<Product={'A'}>} DISTINCT CustomerID) -
  CustomerID=P({<Product={'B'}>} DISTINCT CustomerID)
>} DISTINCT CustomerID)
```

**Element Functions (P, E)**
```qlik
// P() - Possible values given selections
Sum({<Product=P({<Region={'East'}>} Product)>} Sales)

// E() - Excluded values
Sum({<Product=E({<Region={'East'}>} Product)>} Sales)
```

## Aggregation Functions

### Basic Aggregations
```qlik
// Sum
Sum(Sales)
Sum(DISTINCT Sales)  // Distinct values only

// Count
Count(OrderID)
Count(DISTINCT CustomerID)

// Average
Avg(Sales)
Avg(DISTINCT Sales)

// Min/Max
Min(Date)
Max(Sales)

// Standard Deviation
Stdev(Sales)
StdevPop(Sales)  // Population

// Median
Median(Sales)

// Mode (most frequent)
Mode(ProductID)

// Fractile (percentile)
Fractile(Sales, 0.95)  // 95th percentile
```

### Conditional Aggregations
```qlik
// Sum with condition
Sum(If(Region='East', Sales, 0))

// Alternative using set analysis
Sum({<Region={'East'}>} Sales)

// Count with multiple conditions
Count(
  If(
    Status='Complete' and Year=2024,
    OrderID
  )
)

// Distinct count with condition
Count(DISTINCT If(Sales > 1000, CustomerID))
```

### String Aggregations
```qlik
// Concatenate
Concat(ProductName, ', ')
Concat(DISTINCT ProductName, ', ', ProductName)

// First/Last sorted
FirstSortedValue(ProductName, -Sales)  // Product with max sales
FirstSortedValue(Date, -Date)  // Most recent date

// Max/Min string
MaxString(CustomerName)
MinString(CustomerName)
```

## Date and Time Functions

### Date Arithmetic
```qlik
// Add/subtract days
Date + 7
AddMonths(Date, 3)
AddYears(Date, 1)

// Date difference
Date2 - Date1  // Days between
Age(EndDate, StartDate)  // Years, fractional

// Month/Year difference
MonthsDiff(Date1, Date2)
YearsDiff(Date1, Date2)
```

### Date Extraction
```qlik
// Components
Year(Date)
Month(Date)
Day(Date)
Week(Date)
Weekday(Date)
Quarter(Date)
Hour(Time)
Minute(Time)
Second(Time)

// Names
MonthName(Date)  // Jan 2024
WeekName(Date)   // 2024/01

// Start/End of period
MonthStart(Date)
MonthEnd(Date)
YearStart(Date)
YearEnd(Date)
QuarterStart(Date)
QuarterEnd(Date)
```

### Date Formatting
```qlik
// Date formatting
Date(OrderDate, 'YYYY-MM-DD')
Date#(StringDate, 'MM/DD/YYYY')  // Parse string to date

// Timestamp
Timestamp(DateTime, 'YYYY-MM-DD hh:mm:ss')
```

### Relative Dates
```qlik
// Today and now
Today()
Now()

// Relative
Today() - 7  // 7 days ago
AddMonths(Today(), -3)  // 3 months ago
YearStart(Today())  // Start of current year

// In set analysis
Sum({<Date={">=$(=YearStart(Today()))"}>} Sales)
```

## String Functions

### String Manipulation
```qlik
// Concatenation
FirstName & ' ' & LastName
'Customer: ' & CustomerID

// Substring
Left(String, 5)
Right(String, 3)
Mid(String, 2, 4)  // From position 2, length 4

// Find and replace
Index(String, 'search')  // Position of substring
SubField(Email, '@', 2)  // Split by delimiter
Replace(Phone, '-', '')  // Replace all occurrences

// Trim and clean
Trim(String)
LTrim(String)
RTrim(String)
Lower(String)
Upper(String)
Capitalize(String)  // First letter uppercase

// Length
Len(String)
```

### Pattern Matching
```qlik
// Wildcard match
If(WildMatch(ProductName, '*Phone*'), 'Mobile', 'Other')
If(WildMatch(Status, 'Complete*', 'Shipped*'), 'Done', 'Pending')

// Substring match
If(Index(Description, 'urgent') > 0, 'Priority', 'Normal')

// Multiple patterns
Match(Status, 'Complete', 'Shipped', 'Delivered')  // Returns position if found
```

### String Formatting
```qlik
// Number formatting
Num(Value, '#,##0.00')
Num(Percentage, '0.0%')
Money(Amount, '$ #,##0.00')

// Text formatting
Text(Value)  // Force to text
PurgeChar(String, '0123456789')  // Remove digits
KeepChar(String, '0123456789')  // Keep only digits
```

## Conditional Logic

### If Statements
```qlik
// Simple if
If(Sales > 1000, 'High', 'Low')

// Nested if
If(Sales > 10000, 'Very High',
  If(Sales > 5000, 'High',
    If(Sales > 1000, 'Medium', 'Low')
  )
)

// If with multiple conditions
If(Region='East' and Sales > 1000, 'Target', 'Other')
```

### Pick and Match
```qlik
// Pick by index (1-based)
Pick(Status, 'New', 'Processing', 'Complete', 'Cancelled')

// Match returns index
Match(Region, 'East', 'West', 'North', 'South')

// Combined
Pick(
  Match(Month(Date), 1,2,3, 4,5,6, 7,8,9, 10,11,12),
  'Q1', 'Q1', 'Q1',
  'Q2', 'Q2', 'Q2',
  'Q3', 'Q3', 'Q3',
  'Q4', 'Q4', 'Q4'
)
```

### Class Function
```qlik
// Binning
Class(Sales, 1000)  // 0-1000, 1000-2000, etc.
Class(Sales, 1000, 'Sales: ', 'k')  // Sales: 0-1k, Sales: 1-2k

// Custom intervals
If(Sales <= 100, '0-100',
  If(Sales <= 500, '101-500',
    If(Sales <= 1000, '501-1000', '1000+')
  )
)
```

## Inter-Record Functions

### Previous/Next Value
```qlik
// Previous value in sort order
Previous(Sum(Sales))

// Peek (look at previous row during load)
// Used in script only
Peek('Sales', -1)  // Previous row
Peek('Sales', 0)   // Current row
Peek('Sales', Row() - 1)  // Explicit row reference
```

### Above/Below (in Pivot Tables)
```qlik
// Above current cell
Above(Sum(Sales))
Above(Sum(Sales), 2)  // 2 rows above

// Total of column above
RangeSum(Above(Sum(Sales), 0, RowNo()))

// Column total
Column(1)  // First column value
```

## Range Functions

### Range Aggregations
```qlik
// Sum of arguments
RangeSum(Value1, Value2, Value3)
RangeSum(Above(Sum(Sales), 0, 3))  // Sum of current + 2 above

// Average of range
RangeAvg(Q1Sales, Q2Sales, Q3Sales, Q4Sales)

// Count non-null values
RangeCount(Value1, Value2, Value3)

// Min/Max of range
RangeMin(Sales, Cost, Profit)
RangeMax(Jan, Feb, Mar, Apr)

// Statistical
RangeStdev(Value1, Value2, Value3)
```

## Advanced Patterns

### Running Totals
```qlik
// Using RangeSum and Above
RangeSum(Above(Sum(Sales), 0, RowNo()))

// Alternative with total
Sum(Sales) / Sum(TOTAL Sales)  // Percent of total
```

### Ranking
```qlik
// Rank in current context
Rank(Sum(Sales))

// Dense rank (no gaps)
Rank(Sum(Sales), 1)

// Rank over total
Rank(TOTAL Sum(Sales))

// Top N
If(Rank(Sum(Sales)) <= 10, ProductName, 'Others')
```

### Moving Averages
```qlik
// 3-month moving average
RangeAvg(Above(Sum(Sales), 0, 3))

// Weighted moving average
RangeSum(
  Above(Sum(Sales), 0) * 3,
  Above(Sum(Sales), 1) * 2,
  Above(Sum(Sales), 2) * 1
) / 6
```

### Variance and Growth
```qlik
// Variance from previous
Sum(Sales) - Above(Sum(Sales))

// Percent change
(Sum(Sales) - Above(Sum(Sales))) / Above(Sum(Sales))

// Year over year growth
(Sum(Sales) - Sum({<Year={$(=Max(Year)-1)}>} Sales))
/ Sum({<Year={$(=Max(Year)-1)}>} Sales)
```

### Pareto Analysis
```qlik
// Running total percentage
RangeSum(Above(Sum(Sales), 0, RowNo()))
/ Sum(TOTAL Sales)

// ABC classification
If(
  RangeSum(Above(Sum(Sales), 0, RowNo())) / Sum(TOTAL Sales) <= 0.7,
  'A',
  If(
    RangeSum(Above(Sum(Sales), 0, RowNo())) / Sum(TOTAL Sales) <= 0.9,
    'B',
    'C'
  )
)
```

## Variables and Dollar Sign Expansion

### Variable Expansion
```qlik
// Variable definition (in script or variable editor)
LET vCurrentYear = Year(Today());
LET vPriorYear = $(vCurrentYear) - 1;

// Using in expression
Sum({<Year={$(vCurrentYear)}>} Sales)

// Complex variable
LET vYoYGrowth = (Sum(Sales) - Sum({<Year={$(vPriorYear)}>} Sales))
                 / Sum({<Year={$(vPriorYear)}>} Sales);
```

### Expression Variables
```qlik
// Variable with parameters
// Variable: vTopN
// Definition: Sum({<$(=$1)={$(=$2)}>} $(=$3))

// Usage
$(vTopN('Region', 'East', 'Sales'))
// Expands to: Sum({<Region={'East'}>} Sales)
```

## Alt Function (Alternative Values)

```qlik
// Use alternative if first is null
Alt(PrimaryValue, SecondaryValue, 0)

// Coalesce-like behavior
Alt(DiscountRate, DefaultRate, 0.05)

// With aggregations
Alt(Sum(Sales), 0)  // Return 0 if no sales
```

## Performance Optimization Tips

### 1. Use Set Analysis Over If
```qlik
// SLOW
Sum(If(Region='East', Sales))

// FAST
Sum({<Region={'East'}>} Sales)
```

### 2. Avoid Aggr When Possible
```qlik
// SLOW: Aggr creates temporary table
Sum(Aggr(Sum(Sales), Customer, Product))

// FAST: Direct aggregation when possible
Sum(Sales)
```

### 3. Pre-Calculate in Script
```qlik
// Instead of complex expression in chart
// Do in load script:
// OrderValue: Quantity * Price

// Then simply:
Sum(OrderValue)
```

### 4. Use TOTAL Wisely
```qlik
// Calculate once with TOTAL
Sum(Sales) / Sum(TOTAL Sales)

// Instead of recalculating denominator
Sum(Sales) / Sum({1} Sales)
```

## Common Pitfalls and Solutions

### NULL Handling
```qlik
// Problem: Null breaks calculation
Sum(Sales) / Sum(Orders)  // Returns null if Orders = 0

// Solution: Use Div or If
Div(Sum(Sales), Sum(Orders))  // Returns null safely
If(Sum(Orders) > 0, Sum(Sales) / Sum(Orders), 0)
Alt(Sum(Sales) / Sum(Orders), 0)
```

### Set Analysis with Dollar Expansion
```qlik
// WRONG: Missing quotes
Sum({<Year={$(=Max(Year))}>} Sales)  // Error

// CORRECT: Dollar expansion result should be quoted
Sum({<Year={"$(=Max(Year))"}>} Sales)
```

### Aggregation Scope
```qlik
// WRONG: Can't aggregate aggregation
Sum(Sum(Sales))  // Error

// CORRECT: Use TOTAL or Aggr
Sum(TOTAL Sales)
Sum(Aggr(Sum(Sales), Customer))
```

## Quick Reference Table

| Function Type | Examples |
|--------------|----------|
| Set Analysis | `{<Year={2024}>}`, `{1}`, `{<Field=>}` |
| Aggregation | `Sum()`, `Count()`, `Avg()`, `Max()` |
| Conditional | `If()`, `Pick()`, `Match()`, `Alt()` |
| String | `Left()`, `Mid()`, `Index()`, `SubField()` |
| Date | `Date()`, `Year()`, `AddMonths()`, `MonthName()` |
| Inter-Record | `Above()`, `Below()`, `Previous()`, `Peek()` |
| Range | `RangeSum()`, `RangeAvg()`, `RangeMin()` |
| Ranking | `Rank()`, `Rank(TOTAL)` |

## Resources
- Qlik Functions Reference: https://help.qlik.com/en-US/sense/November2023/Subsystems/Hub/Content/Sense_Hub/Scripting/functions.htm
- Set Analysis Guide: https://help.qlik.com/en-US/sense/November2023/Subsystems/Hub/Content/Sense_Hub/ChartFunctions/SetAnalysis/set-analysis.htm
