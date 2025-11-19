-- Date Dimension Generator Script
-- Platform-agnostic date dimension population
-- Description: Comprehensive date dimension with calendar and fiscal attributes

-- ============================================
-- SNOWFLAKE VERSION
-- ============================================

-- Create and populate date dimension for Snowflake
CREATE OR REPLACE TABLE DIM.DIM_DATE AS
WITH date_range AS (
    SELECT
        DATEADD(day, SEQ4(), '2020-01-01')::DATE AS date_value
    FROM TABLE(GENERATOR(ROWCOUNT => 3653))  -- 10 years of dates
),

date_attributes AS (
    SELECT
        date_value,

        -- Date Key (YYYYMMDD format)
        TO_NUMBER(TO_CHAR(date_value, 'YYYYMMDD')) AS date_key,

        -- Day attributes
        DAYOFWEEK(date_value) AS day_of_week_num,
        DAYNAME(date_value) AS day_name,
        LEFT(DAYNAME(date_value), 3) AS day_name_short,
        DAYOFMONTH(date_value) AS day_of_month,
        DAYOFYEAR(date_value) AS day_of_year,

        -- Week attributes
        WEEKOFYEAR(date_value) AS week_of_year,
        DATE_TRUNC('week', date_value)::DATE AS week_start_date,
        DATEADD(day, 6, DATE_TRUNC('week', date_value))::DATE AS week_end_date,

        -- Month attributes
        MONTH(date_value) AS month_number,
        MONTHNAME(date_value) AS month_name,
        LEFT(MONTHNAME(date_value), 3) AS month_name_short,
        DATE_TRUNC('month', date_value)::DATE AS month_start_date,
        LAST_DAY(date_value)::DATE AS month_end_date,
        DAYOFMONTH(LAST_DAY(date_value)) AS days_in_month,

        -- Quarter attributes
        QUARTER(date_value) AS quarter_number,
        'Q' || QUARTER(date_value) AS quarter_name,
        TO_CHAR(date_value, 'YYYY') || '-Q' || QUARTER(date_value) AS year_quarter,
        DATE_TRUNC('quarter', date_value)::DATE AS quarter_start_date,
        LAST_DAY(DATEADD(month, 2, DATE_TRUNC('quarter', date_value)))::DATE AS quarter_end_date,

        -- Year attributes
        YEAR(date_value) AS year,

        -- Fiscal calendar (assuming fiscal year starts July 1st)
        CASE
            WHEN MONTH(date_value) >= 7 THEN YEAR(date_value) + 1
            ELSE YEAR(date_value)
        END AS fiscal_year,

        CASE
            WHEN MONTH(date_value) IN (7, 8, 9) THEN 1
            WHEN MONTH(date_value) IN (10, 11, 12) THEN 2
            WHEN MONTH(date_value) IN (1, 2, 3) THEN 3
            WHEN MONTH(date_value) IN (4, 5, 6) THEN 4
        END AS fiscal_quarter,

        CASE
            WHEN MONTH(date_value) >= 7 THEN MONTH(date_value) - 6
            ELSE MONTH(date_value) + 6
        END AS fiscal_month,

        -- Flags
        CASE WHEN DAYOFWEEK(date_value) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend,
        CASE WHEN DAYOFWEEK(date_value) = 0 THEN TRUE ELSE FALSE END AS is_sunday,
        CASE WHEN DAYOFWEEK(date_value) = 6 THEN TRUE ELSE FALSE END AS is_saturday,
        CASE WHEN DAYOFWEEK(date_value) BETWEEN 1 AND 5 THEN TRUE ELSE FALSE END AS is_weekday,

        -- Special dates (US holidays - extend as needed)
        CASE
            -- New Year's Day
            WHEN MONTH(date_value) = 1 AND DAY(date_value) = 1 THEN TRUE
            -- Independence Day
            WHEN MONTH(date_value) = 7 AND DAY(date_value) = 4 THEN TRUE
            -- Christmas
            WHEN MONTH(date_value) = 12 AND DAY(date_value) = 25 THEN TRUE
            ELSE FALSE
        END AS is_holiday,

        CASE
            WHEN MONTH(date_value) = 1 AND DAY(date_value) = 1 THEN 'New Year''s Day'
            WHEN MONTH(date_value) = 7 AND DAY(date_value) = 4 THEN 'Independence Day'
            WHEN MONTH(date_value) = 12 AND DAY(date_value) = 25 THEN 'Christmas Day'
            ELSE NULL
        END AS holiday_name,

        -- Relative date attributes
        CASE WHEN date_value = CURRENT_DATE() THEN TRUE ELSE FALSE END AS is_current_day,
        CASE WHEN date_value = CURRENT_DATE() - 1 THEN TRUE ELSE FALSE END AS is_yesterday,
        CASE WHEN date_value = CURRENT_DATE() + 1 THEN TRUE ELSE FALSE END AS is_tomorrow,

        -- Current period flags
        CASE WHEN DATE_TRUNC('week', date_value) = DATE_TRUNC('week', CURRENT_DATE())
             THEN TRUE ELSE FALSE END AS is_current_week,
        CASE WHEN DATE_TRUNC('month', date_value) = DATE_TRUNC('month', CURRENT_DATE())
             THEN TRUE ELSE FALSE END AS is_current_month,
        CASE WHEN DATE_TRUNC('quarter', date_value) = DATE_TRUNC('quarter', CURRENT_DATE())
             THEN TRUE ELSE FALSE END AS is_current_quarter,
        CASE WHEN YEAR(date_value) = YEAR(CURRENT_DATE())
             THEN TRUE ELSE FALSE END AS is_current_year,

        -- Business day calculation (excluding weekends)
        ROW_NUMBER() OVER (
            PARTITION BY YEAR(date_value), MONTH(date_value)
            ORDER BY date_value
        ) FILTER (WHERE DAYOFWEEK(date_value) BETWEEN 1 AND 5) AS business_day_of_month,

        -- Metadata
        CURRENT_TIMESTAMP() AS created_at,
        CURRENT_TIMESTAMP() AS updated_at

    FROM date_range
)

SELECT
    date_key,
    date_value,
    day_of_week_num,
    day_name,
    day_name_short,
    day_of_month,
    day_of_year,
    week_of_year,
    week_start_date,
    week_end_date,
    month_number,
    month_name,
    month_name_short,
    month_start_date,
    month_end_date,
    days_in_month,
    quarter_number,
    quarter_name,
    year_quarter,
    quarter_start_date,
    quarter_end_date,
    year,
    fiscal_year,
    fiscal_quarter,
    fiscal_month,
    is_weekend,
    is_sunday,
    is_saturday,
    is_weekday,
    is_holiday,
    holiday_name,
    is_current_day,
    is_yesterday,
    is_tomorrow,
    is_current_week,
    is_current_month,
    is_current_quarter,
    is_current_year,
    business_day_of_month,
    created_at,
    updated_at
FROM date_attributes
ORDER BY date_value;

-- ============================================
-- BIGQUERY VERSION
-- ============================================

CREATE OR REPLACE TABLE `project.dwh.dim_date` AS
WITH date_range AS (
    SELECT date_value
    FROM UNNEST(
        GENERATE_DATE_ARRAY('2020-01-01', '2029-12-31', INTERVAL 1 DAY)
    ) AS date_value
),

date_attributes AS (
    SELECT
        date_value,

        -- Date Key (YYYYMMDD format)
        CAST(FORMAT_DATE('%Y%m%d', date_value) AS INT64) AS date_key,

        -- Day attributes
        EXTRACT(DAYOFWEEK FROM date_value) AS day_of_week_num,
        FORMAT_DATE('%A', date_value) AS day_name,
        FORMAT_DATE('%a', date_value) AS day_name_short,
        EXTRACT(DAY FROM date_value) AS day_of_month,
        EXTRACT(DAYOFYEAR FROM date_value) AS day_of_year,

        -- Week attributes
        EXTRACT(WEEK FROM date_value) AS week_of_year,
        DATE_TRUNC(date_value, WEEK(SUNDAY)) AS week_start_date,
        DATE_ADD(DATE_TRUNC(date_value, WEEK(SUNDAY)), INTERVAL 6 DAY) AS week_end_date,

        -- Month attributes
        EXTRACT(MONTH FROM date_value) AS month_number,
        FORMAT_DATE('%B', date_value) AS month_name,
        FORMAT_DATE('%b', date_value) AS month_name_short,
        DATE_TRUNC(date_value, MONTH) AS month_start_date,
        LAST_DAY(date_value, MONTH) AS month_end_date,
        EXTRACT(DAY FROM LAST_DAY(date_value, MONTH)) AS days_in_month,

        -- Quarter attributes
        EXTRACT(QUARTER FROM date_value) AS quarter_number,
        'Q' || CAST(EXTRACT(QUARTER FROM date_value) AS STRING) AS quarter_name,
        CAST(EXTRACT(YEAR FROM date_value) AS STRING) || '-Q' ||
            CAST(EXTRACT(QUARTER FROM date_value) AS STRING) AS year_quarter,
        DATE_TRUNC(date_value, QUARTER) AS quarter_start_date,
        LAST_DAY(date_value, QUARTER) AS quarter_end_date,

        -- Year attributes
        EXTRACT(YEAR FROM date_value) AS year,

        -- Fiscal calendar (assuming fiscal year starts July 1st)
        CASE
            WHEN EXTRACT(MONTH FROM date_value) >= 7
            THEN EXTRACT(YEAR FROM date_value) + 1
            ELSE EXTRACT(YEAR FROM date_value)
        END AS fiscal_year,

        CASE
            WHEN EXTRACT(MONTH FROM date_value) IN (7, 8, 9) THEN 1
            WHEN EXTRACT(MONTH FROM date_value) IN (10, 11, 12) THEN 2
            WHEN EXTRACT(MONTH FROM date_value) IN (1, 2, 3) THEN 3
            WHEN EXTRACT(MONTH FROM date_value) IN (4, 5, 6) THEN 4
        END AS fiscal_quarter,

        CASE
            WHEN EXTRACT(MONTH FROM date_value) >= 7
            THEN EXTRACT(MONTH FROM date_value) - 6
            ELSE EXTRACT(MONTH FROM date_value) + 6
        END AS fiscal_month,

        -- Flags
        CASE WHEN EXTRACT(DAYOFWEEK FROM date_value) IN (1, 7) THEN TRUE ELSE FALSE END AS is_weekend,
        CASE WHEN EXTRACT(DAYOFWEEK FROM date_value) = 1 THEN TRUE ELSE FALSE END AS is_sunday,
        CASE WHEN EXTRACT(DAYOFWEEK FROM date_value) = 7 THEN TRUE ELSE FALSE END AS is_saturday,
        CASE WHEN EXTRACT(DAYOFWEEK FROM date_value) BETWEEN 2 AND 6 THEN TRUE ELSE FALSE END AS is_weekday,

        -- Holidays (US)
        CASE
            WHEN EXTRACT(MONTH FROM date_value) = 1 AND EXTRACT(DAY FROM date_value) = 1 THEN TRUE
            WHEN EXTRACT(MONTH FROM date_value) = 7 AND EXTRACT(DAY FROM date_value) = 4 THEN TRUE
            WHEN EXTRACT(MONTH FROM date_value) = 12 AND EXTRACT(DAY FROM date_value) = 25 THEN TRUE
            ELSE FALSE
        END AS is_holiday,

        CASE
            WHEN EXTRACT(MONTH FROM date_value) = 1 AND EXTRACT(DAY FROM date_value) = 1 THEN 'New Year''s Day'
            WHEN EXTRACT(MONTH FROM date_value) = 7 AND EXTRACT(DAY FROM date_value) = 4 THEN 'Independence Day'
            WHEN EXTRACT(MONTH FROM date_value) = 12 AND EXTRACT(DAY FROM date_value) = 25 THEN 'Christmas Day'
            ELSE NULL
        END AS holiday_name,

        -- Current period flags
        date_value = CURRENT_DATE() AS is_current_day,
        date_value = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY) AS is_yesterday,
        date_value = DATE_ADD(CURRENT_DATE(), INTERVAL 1 DAY) AS is_tomorrow,
        DATE_TRUNC(date_value, WEEK) = DATE_TRUNC(CURRENT_DATE(), WEEK) AS is_current_week,
        DATE_TRUNC(date_value, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH) AS is_current_month,
        DATE_TRUNC(date_value, QUARTER) = DATE_TRUNC(CURRENT_DATE(), QUARTER) AS is_current_quarter,
        EXTRACT(YEAR FROM date_value) = EXTRACT(YEAR FROM CURRENT_DATE()) AS is_current_year,

        -- Metadata
        CURRENT_TIMESTAMP() AS created_at,
        CURRENT_TIMESTAMP() AS updated_at

    FROM date_range
)

SELECT * FROM date_attributes
ORDER BY date_value;

-- ============================================
-- REDSHIFT VERSION
-- ============================================

CREATE TABLE dim_date AS
WITH RECURSIVE date_range AS (
    SELECT '2020-01-01'::DATE AS date_value
    UNION ALL
    SELECT date_value + 1
    FROM date_range
    WHERE date_value < '2029-12-31'::DATE
),

date_attributes AS (
    SELECT
        date_value,

        -- Date Key
        TO_NUMBER(TO_CHAR(date_value, 'YYYYMMDD'), '99999999') AS date_key,

        -- Day attributes
        EXTRACT(dow FROM date_value) AS day_of_week_num,
        TO_CHAR(date_value, 'Day') AS day_name,
        TO_CHAR(date_value, 'Dy') AS day_name_short,
        EXTRACT(day FROM date_value) AS day_of_month,
        EXTRACT(doy FROM date_value) AS day_of_year,

        -- Week attributes
        EXTRACT(week FROM date_value) AS week_of_year,
        DATE_TRUNC('week', date_value)::DATE AS week_start_date,
        DATE_TRUNC('week', date_value)::DATE + 6 AS week_end_date,

        -- Month attributes
        EXTRACT(month FROM date_value) AS month_number,
        TO_CHAR(date_value, 'Month') AS month_name,
        TO_CHAR(date_value, 'Mon') AS month_name_short,
        DATE_TRUNC('month', date_value)::DATE AS month_start_date,
        LAST_DAY(date_value)::DATE AS month_end_date,
        EXTRACT(day FROM LAST_DAY(date_value)) AS days_in_month,

        -- Quarter attributes
        EXTRACT(quarter FROM date_value) AS quarter_number,
        'Q' || EXTRACT(quarter FROM date_value) AS quarter_name,

        -- Year attributes
        EXTRACT(year FROM date_value) AS year,

        -- Fiscal year (July 1st start)
        CASE
            WHEN EXTRACT(month FROM date_value) >= 7
            THEN EXTRACT(year FROM date_value) + 1
            ELSE EXTRACT(year FROM date_value)
        END AS fiscal_year,

        -- Flags
        CASE WHEN EXTRACT(dow FROM date_value) IN (0, 6) THEN 1 ELSE 0 END AS is_weekend,
        CASE WHEN EXTRACT(dow FROM date_value) BETWEEN 1 AND 5 THEN 1 ELSE 0 END AS is_weekday,

        GETDATE() AS created_at,
        GETDATE() AS updated_at

    FROM date_range
)

SELECT * FROM date_attributes
ORDER BY date_value;

-- ============================================
-- POSTGRES VERSION
-- ============================================

CREATE TABLE dim_date AS
WITH date_range AS (
    SELECT generate_series(
        '2020-01-01'::DATE,
        '2029-12-31'::DATE,
        '1 day'::INTERVAL
    )::DATE AS date_value
),

date_attributes AS (
    SELECT
        date_value,

        -- Date Key
        TO_CHAR(date_value, 'YYYYMMDD')::INTEGER AS date_key,

        -- Day attributes
        EXTRACT(dow FROM date_value)::INTEGER AS day_of_week_num,
        TO_CHAR(date_value, 'Day') AS day_name,
        TO_CHAR(date_value, 'Dy') AS day_name_short,
        EXTRACT(day FROM date_value)::INTEGER AS day_of_month,
        EXTRACT(doy FROM date_value)::INTEGER AS day_of_year,

        -- Week attributes
        EXTRACT(week FROM date_value)::INTEGER AS week_of_year,
        DATE_TRUNC('week', date_value)::DATE AS week_start_date,
        (DATE_TRUNC('week', date_value) + INTERVAL '6 days')::DATE AS week_end_date,

        -- Month attributes
        EXTRACT(month FROM date_value)::INTEGER AS month_number,
        TO_CHAR(date_value, 'Month') AS month_name,
        TO_CHAR(date_value, 'Mon') AS month_name_short,
        DATE_TRUNC('month', date_value)::DATE AS month_start_date,
        (DATE_TRUNC('month', date_value) + INTERVAL '1 month - 1 day')::DATE AS month_end_date,

        -- Quarter attributes
        EXTRACT(quarter FROM date_value)::INTEGER AS quarter_number,
        'Q' || EXTRACT(quarter FROM date_value)::TEXT AS quarter_name,
        DATE_TRUNC('quarter', date_value)::DATE AS quarter_start_date,
        (DATE_TRUNC('quarter', date_value) + INTERVAL '3 months - 1 day')::DATE AS quarter_end_date,

        -- Year attributes
        EXTRACT(year FROM date_value)::INTEGER AS year,

        -- Flags
        CASE WHEN EXTRACT(dow FROM date_value) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend,
        CASE WHEN EXTRACT(dow FROM date_value) BETWEEN 1 AND 5 THEN TRUE ELSE FALSE END AS is_weekday,

        CURRENT_TIMESTAMP AS created_at,
        CURRENT_TIMESTAMP AS updated_at

    FROM date_range
)

SELECT * FROM date_attributes
ORDER BY date_value;
