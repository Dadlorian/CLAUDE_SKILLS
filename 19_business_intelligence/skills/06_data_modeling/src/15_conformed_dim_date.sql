-- CONFORMED DATE DIMENSION (Complete)
-- Pre-populated for 10 years, used by all fact tables
INSERT INTO DIM_DATE (date_key, date, day_name, month_name, quarter_number, year)
SELECT 
    TO_CHAR(d, 'YYYYMMDD')::INTEGER,
    d::DATE,
    TO_CHAR(d, 'Day'),
    TO_CHAR(d, 'Month'),
    EXTRACT(QUARTER FROM d),
    EXTRACT(YEAR FROM d)
FROM generate_series('2020-01-01'::DATE, '2029-12-31'::DATE, '1 day') d;
