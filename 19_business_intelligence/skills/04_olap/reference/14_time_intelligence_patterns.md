# Time Intelligence Patterns in OLAP

## Overview

Comprehensive patterns for implementing time-based calculations in OLAP cubes, covering period-over-period comparisons, running totals, and complex time analysis.

## Date Dimension Requirements

### Complete Date Table

```sql
CREATE TABLE DimDate (
    DateKey INT PRIMARY KEY,
    Date DATE NOT NULL UNIQUE,

    -- Calendar hierarchy
    DayOfWeek INT,
    DayOfWeekName VARCHAR(10),
    DayOfMonth INT,
    DayOfYear INT,
    WeekOfYear INT,
    MonthNumber INT,
    MonthName VARCHAR(10),
    MonthNameShort VARCHAR(3),
    Quarter INT,
    QuarterName VARCHAR(2),
    Year INT,
    YearMonth INT,
    YearQuarter INT,

    -- Fiscal hierarchy
    FiscalYear INT,
    FiscalQuarter INT,
    FiscalMonth INT,
    FiscalWeek INT,
    FiscalDayOfYear INT,

    -- ISO 8601
    ISOWeek INT,
    ISOYear INT,
    ISOYearWeek INT,

    -- Relative periods
    IsCurrentDay BIT,
    IsCurrentWeek BIT,
    IsCurrentMonth BIT,
    IsCurrentQuarter BIT,
    IsCurrentYear BIT,

    IsLastDay BIT,
    IsLastWeek BIT,
    IsLastMonth BIT,
    IsLastQuarter BIT,
    IsLastYear BIT,

    -- Business day flags
    IsWeekend BIT,
    IsHoliday BIT,
    HolidayName VARCHAR(100),
    IsBusinessDay AS (CASE WHEN IsWeekend = 0 AND IsHoliday = 0 THEN 1 ELSE 0 END),

    -- Offsets
    PriorDayKey INT,
    PriorWeekKey INT,
    PriorMonthKey INT,
    PriorQuarterKey INT,
    PriorYearKey INT,

    -- Formatted strings
    DateFormatted AS (FORMAT(Date, 'MMM dd, yyyy')),
    MonthYear AS (FORMAT(Date, 'MMM yyyy')),
    QuarterYear AS ('Q' + CAST(Quarter AS VARCHAR) + ' ' + CAST(Year AS VARCHAR))
);

-- Populate date dimension (2020-2030)
DECLARE @StartDate DATE = '2020-01-01';
DECLARE @EndDate DATE = '2030-12-31';
DECLARE @FiscalYearEnd VARCHAR(5) = '06-30'; -- June 30 fiscal year end

WHILE @StartDate <= @EndDate
BEGIN
    INSERT INTO DimDate (DateKey, Date, /* other fields */)
    VALUES (
        CONVERT(INT, FORMAT(@StartDate, 'yyyyMMdd')),
        @StartDate,
        -- Calculate other fields...
    );

    SET @StartDate = DATEADD(DAY, 1, @StartDate);
END;
```

## Year-to-Date (YTD) Patterns

### MDX YTD

```mdx
-- Calendar YTD
WITH MEMBER [Measures].[Sales YTD] AS
    AGGREGATE(
        PERIODSTODATE(
            [Date].[Calendar].[Year],
            [Date].[Calendar].CURRENTMEMBER
        ),
        [Measures].[Sales Amount]
    )

SELECT
    {[Measures].[Sales Amount], [Measures].[Sales YTD]} ON COLUMNS,
    [Date].[Calendar].[Month].MEMBERS ON ROWS
FROM [Sales]
WHERE [Date].[Calendar].[2024]
```

### DAX YTD

```dax
// Calendar YTD
Sales YTD =
TOTALYTD(
    SUM(Sales[Amount]),
    'Date'[Date]
)

// Fiscal YTD (July 1 - June 30)
Sales Fiscal YTD =
TOTALYTD(
    SUM(Sales[Amount]),
    'Date'[Date],
    "6/30"  -- Fiscal year ends June 30
)

// YTD with specific filter
Sales YTD Electronics =
CALCULATE(
    [Sales YTD],
    Products[Category] = "Electronics"
)
```

### Custom YTD Logic

```dax
// YTD with custom start month
Sales Custom YTD =
VAR CurrentDate = MAX('Date'[Date])
VAR CurrentYear = YEAR(CurrentDate)
VAR YTDStart = DATE(CurrentYear, 4, 1) -- April 1
VAR YTDEnd = CurrentDate
RETURN
    CALCULATE(
        SUM(Sales[Amount]),
        DATESBETWEEN(
            'Date'[Date],
            YTDStart,
            YTDEnd
        )
    )
```

## Quarter-to-Date and Month-to-Date

### MDX QTD/MTD

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

MEMBER [Measures].[Sales WTD] AS
    AGGREGATE(
        LASTPERIODS(
            WEEKDAY([Date].[Calendar].CURRENTMEMBER.Name),
            [Date].[Calendar].CURRENTMEMBER
        ),
        [Measures].[Sales Amount]
    )
```

### DAX QTD/MTD

```dax
// Quarter-to-Date
Sales QTD = TOTALQTD(SUM(Sales[Amount]), 'Date'[Date])

// Month-to-Date
Sales MTD = TOTALMTD(SUM(Sales[Amount]), 'Date'[Date])

// Week-to-Date (Monday start)
Sales WTD =
VAR LastDate = MAX('Date'[Date])
VAR WeekStart = LastDate - WEEKDAY(LastDate, 2) + 1
RETURN
    CALCULATE(
        SUM(Sales[Amount]),
        DATESBETWEEN('Date'[Date], WeekStart, LastDate)
    )
```

## Prior Period Comparisons

### Year-over-Year (YoY)

```mdx
-- MDX YoY
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
    [Measures].[Sales Amount] - [Measures].[Sales LY],
    FORMAT_STRING = "Currency"

MEMBER [Measures].[YoY % Change] AS
    IIF(
        [Measures].[Sales LY] = 0,
        NULL,
        ([Measures].[Sales Amount] - [Measures].[Sales LY]) /
        [Measures].[Sales LY]
    ),
    FORMAT_STRING = "Percent"

MEMBER [Measures].[YoY Index] AS
    IIF(
        [Measures].[Sales LY] = 0,
        NULL,
        [Measures].[Sales Amount] / [Measures].[Sales LY] * 100
    ),
    FORMAT_STRING = "0.0"
```

```dax
// DAX YoY
Sales LY =
CALCULATE(
    SUM(Sales[Amount]),
    SAMEPERIODLASTYEAR('Date'[Date])
)

YoY Change = [Sales Amount] - [Sales LY]

YoY % Change =
DIVIDE([YoY Change], [Sales LY], 0)

YoY Growth % =
VAR CurrentYear = SUM(Sales[Amount])
VAR PriorYear = [Sales LY]
RETURN
    DIVIDE(CurrentYear - PriorYear, PriorYear, 0)
```

### Month-over-Month and Quarter-over-Quarter

```mdx
-- MDX MoM/QoQ
WITH MEMBER [Measures].[Sales LM] AS
    (
        PARALLELPERIOD(
            [Date].[Calendar].[Month],
            1,
            [Date].[Calendar].CURRENTMEMBER
        ),
        [Measures].[Sales Amount]
    )

MEMBER [Measures].[Sales LQ] AS
    (
        PARALLELPERIOD(
            [Date].[Calendar].[Quarter],
            1,
            [Date].[Calendar].CURRENTMEMBER
        ),
        [Measures].[Sales Amount]
    )

MEMBER [Measures].[MoM % Change] AS
    ([Measures].[Sales Amount] - [Measures].[Sales LM]) /
    [Measures].[Sales LM],
    FORMAT_STRING = "Percent"
```

```dax
// DAX MoM/QoQ
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

MoM % Change = DIVIDE([Sales Amount] - [Sales LM], [Sales LM], 0)
QoQ % Change = DIVIDE([Sales Amount] - [Sales LQ], [Sales LQ], 0)

// Generic prior period
Sales Prior Period =
VAR PeriodOffset = -1
VAR PeriodType = YEAR  -- or QUARTER, MONTH
RETURN
    CALCULATE(
        SUM(Sales[Amount]),
        DATEADD('Date'[Date], PeriodOffset, PeriodType)
    )
```

## Rolling/Moving Calculations

### Rolling Averages

```mdx
-- MDX Rolling Averages
WITH MEMBER [Measures].[3 Month Rolling Avg] AS
    AVG(
        LASTPERIODS(3, [Date].[Calendar].CURRENTMEMBER),
        [Measures].[Sales Amount]
    )

MEMBER [Measures].[12 Month Rolling Avg] AS
    AVG(
        LASTPERIODS(12, [Date].[Calendar].CURRENTMEMBER),
        [Measures].[Sales Amount]
    )

MEMBER [Measures].[Rolling Avg Last 90 Days] AS
    AVG(
        LASTPERIODS(90, [Date].[Date].CURRENTMEMBER),
        [Measures].[Sales Amount]
    )
```

```dax
// DAX Rolling Averages
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

12 Month Rolling Avg =
VAR Last12Months =
    DATESINPERIOD(
        'Date'[Date],
        MAX('Date'[Date]),
        -12,
        MONTH
    )
RETURN
    CALCULATE(
        AVERAGE(Sales[Amount]),
        Last12Months
    )

// Trailing 90 days
Trailing 90 Day Avg =
VAR Last90Days =
    DATESINPERIOD(
        'Date'[Date],
        MAX('Date'[Date]),
        -90,
        DAY
    )
RETURN
    CALCULATE(
        AVERAGE(Sales[DailyTotal]),
        Last90Days
    )
```

### Rolling Sum

```dax
// Rolling 12 month sum
Rolling 12M Sales =
CALCULATE(
    SUM(Sales[Amount]),
    DATESINPERIOD(
        'Date'[Date],
        LASTDATE('Date'[Date]),
        -12,
        MONTH
    )
)

// Rolling quarter sum
Rolling Quarter =
CALCULATE(
    SUM(Sales[Amount]),
    DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -3, MONTH)
)
```

## Running Totals (Cumulative)

### MDX Running Total

```mdx
-- Running total (YTD approach)
WITH MEMBER [Measures].[Running Total] AS
    SUM(
        PERIODSTODATE(
            [Date].[Calendar].[Year],
            [Date].[Calendar].CURRENTMEMBER
        ),
        [Measures].[Sales Amount]
    )

-- All-time running total
MEMBER [Measures].[All Time Running Total] AS
    SUM(
        [Date].[Calendar].[Date].MEMBERS.ITEM(0) :
        [Date].[Calendar].CURRENTMEMBER,
        [Measures].[Sales Amount]
    )
```

### DAX Running Total

```dax
// Running total (all time)
Running Total =
CALCULATE(
    SUM(Sales[Amount]),
    FILTER(
        ALL('Date'),
        'Date'[Date] <= MAX('Date'[Date])
    )
)

// Running total within year
Running Total YTD =
VAR MaxDate = MAX('Date'[Date])
VAR CurrentYear = YEAR(MaxDate)
RETURN
    CALCULATE(
        SUM(Sales[Amount]),
        FILTER(
            ALL('Date'),
            'Date'[Date] <= MaxDate &&
            YEAR('Date'[Date]) = CurrentYear
        )
    )

// Running total by category
Running Total by Category =
CALCULATE(
    SUM(Sales[Amount]),
    FILTER(
        ALLEXCEPT('Date', Products[Category]),
        'Date'[Date] <= MAX('Date'[Date])
    )
)
```

## Period Comparison Patterns

### Same Period Last Year (SPLY)

```dax
// SPLY for any time period
Sales SPLY =
CALCULATE(
    [Sales Amount],
    SAMEPERIODLASTYEAR('Date'[Date])
)

// YTD vs SPLY YTD
Sales YTD vs LY YTD =
VAR CurrentYTD = [Sales YTD]
VAR LastYearYTD =
    CALCULATE(
        [Sales YTD],
        SAMEPERIODLASTYEAR('Date'[Date])
    )
RETURN
    CurrentYTD - LastYearYTD

// YTD Growth % vs LY
YTD Growth % vs LY =
VAR CurrentYTD = [Sales YTD]
VAR LastYearYTD =
    CALCULATE(
        [Sales YTD],
        SAMEPERIODLASTYEAR('Date'[Date])
    )
RETURN
    DIVIDE(CurrentYTD - LastYearYTD, LastYearYTD, 0)
```

### Complete Period Comparison

```dax
// Prior complete month (not MTD)
Sales Prior Complete Month =
VAR LastCompleteMonth =
    EOMONTH(MAX('Date'[Date]), -1)
VAR MonthStart =
    DATE(YEAR(LastCompleteMonth), MONTH(LastCompleteMonth), 1)
RETURN
    CALCULATE(
        SUM(Sales[Amount]),
        DATESBETWEEN('Date'[Date], MonthStart, LastCompleteMonth)
    )

// Prior complete quarter
Sales Prior Complete Quarter =
VAR CurrentQuarter = QUARTER(MAX('Date'[Date]))
VAR CurrentYear = YEAR(MAX('Date'[Date]))
VAR PriorQuarter = IF(CurrentQuarter = 1, 4, CurrentQuarter - 1)
VAR PriorYear = IF(CurrentQuarter = 1, CurrentYear - 1, CurrentYear)
VAR QuarterStart = DATE(PriorYear, (PriorQuarter - 1) * 3 + 1, 1)
VAR QuarterEnd = EOMONTH(QuarterStart, 2)
RETURN
    CALCULATE(
        SUM(Sales[Amount]),
        DATESBETWEEN('Date'[Date], QuarterStart, QuarterEnd)
    )
```

## Advanced Time Intelligence

### Fiscal Calendar Support

```dax
// Fiscal YTD (custom fiscal year)
Sales Fiscal YTD =
VAR FiscalYearStartMonth = 7  -- July
VAR CurrentDate = MAX('Date'[Date])
VAR CurrentFiscalYear = 'Date'[FiscalYear]
VAR FiscalYearStart = DATE(
    IF(MONTH(CurrentDate) < FiscalYearStartMonth,
       YEAR(CurrentDate) - 1,
       YEAR(CurrentDate)
    ),
    FiscalYearStartMonth,
    1
)
RETURN
    CALCULATE(
        SUM(Sales[Amount]),
        DATESBETWEEN('Date'[Date], FiscalYearStart, CurrentDate)
    )

// Fiscal Period comparison
Sales Same Fiscal Period LY =
VAR CurrentFiscalPeriod = MAX('Date'[FiscalPeriod])
VAR PriorFiscalYear = MAX('Date'[FiscalYear]) - 1
RETURN
    CALCULATE(
        SUM(Sales[Amount]),
        'Date'[FiscalPeriod] = CurrentFiscalPeriod,
        'Date'[FiscalYear] = PriorFiscalYear
    )
```

### Weekly Patterns (ISO 8601)

```dax
// Week-over-week
Sales WoW =
VAR CurrentWeek = MAX('Date'[ISOWeek])
VAR CurrentYear = MAX('Date'[ISOYear])
VAR PriorWeek = IF(CurrentWeek = 1, 52, CurrentWeek - 1)
VAR PriorYear = IF(CurrentWeek = 1, CurrentYear - 1, CurrentYear)
RETURN
    CALCULATE(
        SUM(Sales[Amount]),
        'Date'[ISOWeek] = PriorWeek,
        'Date'[ISOYear] = PriorYear
    )

// Same week last year
Sales SWLY =
VAR CurrentWeek = MAX('Date'[ISOWeek])
VAR PriorYear = MAX('Date'[ISOYear]) - 1
RETURN
    CALCULATE(
        SUM(Sales[Amount]),
        'Date'[ISOWeek] = CurrentWeek,
        'Date'[ISOYear] = PriorYear
    )
```

### Business Days Calculations

```dax
// Sales per business day
Sales per Business Day =
VAR TotalSales = SUM(Sales[Amount])
VAR BusinessDays =
    CALCULATE(
        COUNTROWS('Date'),
        'Date'[IsBusinessDay] = TRUE
    )
RETURN
    DIVIDE(TotalSales, BusinessDays, 0)

// MTD business days vs same period LY
MTD Business Days vs LY =
VAR CurrentMTD = [Sales MTD]
VAR CurrentBusinessDays =
    CALCULATE(
        COUNTROWS('Date'),
        'Date'[IsBusinessDay] = TRUE,
        DATESMTD('Date'[Date])
    )
VAR LastYearSameBizDays =
    VAR LYStart = EDATE(DATE(YEAR(MIN('Date'[Date])) - 1, MONTH(MIN('Date'[Date])), 1), 0)
    VAR LYEnd = DATEADD(LYStart, CurrentBusinessDays - 1, DAY)
    RETURN
        CALCULATE(
            SUM(Sales[Amount]),
            DATESBETWEEN('Date'[Date], LYStart, LYEnd)
        )
RETURN
    CurrentMTD - LastYearSameBizDays
```

## Best Practices

### 1. Date Table Design
```
✓ Continuous date range (no gaps)
✓ Include all relevant hierarchies
✓ Mark as date table
✓ Pre-calculate common offsets
✓ Include fiscal calendars if needed
✓ Add business day logic
```

### 2. Calculation Performance
```
✓ Use built-in time intelligence functions when possible
✓ Leverage date table relationships
✓ Minimize use of FILTER on large tables
✓ Use variables to avoid recalculation
✓ Consider materialized columns for complex logic
```

### 3. User Experience
```
✓ Consistent naming conventions
✓ Appropriate format strings
✓ Handle edge cases (no prior period data)
✓ Document calculation logic
✓ Provide tooltips/descriptions
```

### 4. Testing
```
✓ Test boundary conditions (year-end, quarter-end)
✓ Validate leap years
✓ Test fiscal year transitions
✓ Verify with known totals
✓ Test with incomplete periods
```
