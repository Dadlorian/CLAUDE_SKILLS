-- Date Dimension Table
-- Comprehensive date dimension with calendar and fiscal hierarchies

CREATE TABLE DimDate (
    DateKey INT PRIMARY KEY,
    Date DATE NOT NULL UNIQUE,
    
    -- Calendar attributes
    DayOfWeek INT,
    DayOfWeekName VARCHAR(10),
    DayOfMonth INT,
    DayOfYear INT,
    WeekOfYear INT,
    WeekOfMonth INT,
    MonthNumber INT,
    MonthName VARCHAR(10),
    MonthNameShort VARCHAR(3),
    Quarter INT,
    QuarterName VARCHAR(2),
    Year INT,
    
    -- Fiscal attributes (July 1 - June 30)
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
    
    -- Business day flags
    IsWeekend BIT,
    IsHoliday BIT,
    HolidayName VARCHAR(100),
    IsBusinessDay AS (CASE WHEN IsWeekend = 0 AND IsHoliday = 0 THEN 1 ELSE 0 END),
    
    -- Formatted strings
    YearMonth INT,
    YearQuarter INT,
    DateFormatted AS (FORMAT(Date, 'MMM dd, yyyy')),
    MonthYear AS (FORMAT(Date, 'MMM yyyy')),
    QuarterYear AS ('Q' + CAST(Quarter AS VARCHAR) + ' ' + CAST(Year AS VARCHAR))
);

-- Populate date dimension
DECLARE @StartDate DATE = '2020-01-01';
DECLARE @EndDate DATE = '2030-12-31';
DECLARE @CurrentDate DATE = @StartDate;
DECLARE @FiscalYearStartMonth INT = 7; -- July

WHILE @CurrentDate <= @EndDate
BEGIN
    INSERT INTO DimDate (
        DateKey,
        Date,
        DayOfWeek,
        DayOfWeekName,
        DayOfMonth,
        DayOfYear,
        WeekOfYear,
        WeekOfMonth,
        MonthNumber,
        MonthName,
        MonthNameShort,
        Quarter,
        QuarterName,
        Year,
        FiscalYear,
        FiscalQuarter,
        FiscalMonth,
        FiscalWeek,
        ISOWeek,
        ISOYear,
        ISOYearWeek,
        IsCurrentDay,
        IsCurrentWeek,
        IsCurrentMonth,
        IsCurrentQuarter,
        IsCurrentYear,
        IsWeekend,
        IsHoliday,
        YearMonth,
        YearQuarter
    )
    VALUES (
        CONVERT(INT, FORMAT(@CurrentDate, 'yyyyMMdd')),
        @CurrentDate,
        DATEPART(WEEKDAY, @CurrentDate),
        DATENAME(WEEKDAY, @CurrentDate),
        DAY(@CurrentDate),
        DATEPART(DAYOFYEAR, @CurrentDate),
        DATEPART(WEEK, @CurrentDate),
        DATEDIFF(WEEK, DATEADD(MONTH, DATEDIFF(MONTH, 0, @CurrentDate), 0), @CurrentDate) + 1,
        MONTH(@CurrentDate),
        DATENAME(MONTH, @CurrentDate),
        FORMAT(@CurrentDate, 'MMM'),
        DATEPART(QUARTER, @CurrentDate),
        'Q' + CAST(DATEPART(QUARTER, @CurrentDate) AS VARCHAR(1)),
        YEAR(@CurrentDate),
        -- Fiscal year
        CASE WHEN MONTH(@CurrentDate) >= @FiscalYearStartMonth 
             THEN YEAR(@CurrentDate) + 1
             ELSE YEAR(@CurrentDate) END,
        -- Fiscal quarter
        CASE 
            WHEN MONTH(@CurrentDate) >= @FiscalYearStartMonth 
            THEN ((MONTH(@CurrentDate) - @FiscalYearStartMonth) / 3) + 1
            ELSE ((MONTH(@CurrentDate) + (12 - @FiscalYearStartMonth)) / 3) + 1
        END,
        -- Fiscal month
        CASE 
            WHEN MONTH(@CurrentDate) >= @FiscalYearStartMonth 
            THEN MONTH(@CurrentDate) - @FiscalYearStartMonth + 1
            ELSE MONTH(@CurrentDate) + (12 - @FiscalYearStartMonth) + 1
        END,
        NULL, -- FiscalWeek - calculate separately if needed
        DATEPART(ISO_WEEK, @CurrentDate),
        YEAR(DATEADD(DAY, 26 - DATEPART(ISO_WEEK, @CurrentDate), @CurrentDate)),
        YEAR(DATEADD(DAY, 26 - DATEPART(ISO_WEEK, @CurrentDate), @CurrentDate)) * 100 + DATEPART(ISO_WEEK, @CurrentDate),
        CASE WHEN @CurrentDate = CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END,
        CASE WHEN DATEPART(WEEK, @CurrentDate) = DATEPART(WEEK, GETDATE()) 
                  AND YEAR(@CurrentDate) = YEAR(GETDATE()) THEN 1 ELSE 0 END,
        CASE WHEN MONTH(@CurrentDate) = MONTH(GETDATE()) 
                  AND YEAR(@CurrentDate) = YEAR(GETDATE()) THEN 1 ELSE 0 END,
        CASE WHEN DATEPART(QUARTER, @CurrentDate) = DATEPART(QUARTER, GETDATE()) 
                  AND YEAR(@CurrentDate) = YEAR(GETDATE()) THEN 1 ELSE 0 END,
        CASE WHEN YEAR(@CurrentDate) = YEAR(GETDATE()) THEN 1 ELSE 0 END,
        CASE WHEN DATEPART(WEEKDAY, @CurrentDate) IN (1, 7) THEN 1 ELSE 0 END,
        0, -- IsHoliday - update separately
        YEAR(@CurrentDate) * 100 + MONTH(@CurrentDate),
        YEAR(@CurrentDate) * 10 + DATEPART(QUARTER, @CurrentDate)
    );
    
    SET @CurrentDate = DATEADD(DAY, 1, @CurrentDate);
END;

-- Update holidays (example for US holidays)
UPDATE DimDate
SET IsHoliday = 1,
    HolidayName = 'New Year''s Day'
WHERE MonthNumber = 1 AND DayOfMonth = 1;

UPDATE DimDate
SET IsHoliday = 1,
    HolidayName = 'Independence Day'
WHERE MonthNumber = 7 AND DayOfMonth = 4;

UPDATE DimDate
SET IsHoliday = 1,
    HolidayName = 'Christmas Day'
WHERE MonthNumber = 12 AND DayOfMonth = 25;

-- Create indexes
CREATE INDEX IX_DimDate_Year ON DimDate(Year);
CREATE INDEX IX_DimDate_YearMonth ON DimDate(YearMonth);
CREATE INDEX IX_DimDate_FiscalYear ON DimDate(FiscalYear);
