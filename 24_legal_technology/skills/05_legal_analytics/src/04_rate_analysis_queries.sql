-- Rate Analysis SQL Queries
-- Analyzes billing rates, rate trends, and rate comparisons

-- Query 1: Average rates by experience level and practice area
SELECT
    practice_area,
    experience_level,
    COUNT(DISTINCT lawyer_id) as num_lawyers,
    ROUND(AVG(hourly_rate), 2) as avg_rate,
    ROUND(MIN(hourly_rate), 2) as min_rate,
    ROUND(MAX(hourly_rate), 2) as max_rate,
    ROUND(STDDEV(hourly_rate), 2) as rate_stddev,
    ROUND(AVG(realization_rate), 1) as avg_realization_pct
FROM lawyer_rates
WHERE active = 1
    AND rate_effective_date <= CURDATE()
    AND (rate_end_date IS NULL OR rate_end_date > CURDATE())
GROUP BY practice_area, experience_level
ORDER BY practice_area, experience_level;

-- Query 2: Rate history and trends
SELECT
    DATE_TRUNC(rate_effective_date, MONTH) as month,
    experience_level,
    ROUND(AVG(hourly_rate), 2) as avg_rate,
    ROUND(AVG(hourly_rate) - LAG(AVG(hourly_rate)) OVER (
        PARTITION BY experience_level
        ORDER BY DATE_TRUNC(rate_effective_date, MONTH)
    ), 2) as month_over_month_change,
    ROUND((AVG(hourly_rate) - LAG(AVG(hourly_rate)) OVER (
        PARTITION BY experience_level
        ORDER BY DATE_TRUNC(rate_effective_date, MONTH)
    )) / LAG(AVG(hourly_rate)) OVER (
        PARTITION BY experience_level
        ORDER BY DATE_TRUNC(rate_effective_date, MONTH)
    ) * 100, 2) as pct_change
FROM lawyer_rates
WHERE rate_effective_date >= DATE_SUB(CURDATE(), INTERVAL 24 MONTH)
GROUP BY month, experience_level
ORDER BY month DESC, experience_level;

-- Query 3: Blended rate analysis by matter
SELECT
    m.matter_id,
    m.matter_name,
    m.client_id,
    c.client_name,
    SUM(t.hours) as total_hours,
    ROUND(SUM(t.hours * lr.hourly_rate) / SUM(t.hours), 2) as blended_rate,
    ROUND(AVG(lr.hourly_rate), 2) as avg_staff_rate,
    ROUND(MAX(lr.hourly_rate), 2) as max_staff_rate,
    ROUND(MIN(lr.hourly_rate), 2) as min_staff_rate,
    ROUND(SUM(t.hours * lr.hourly_rate), 2) as total_billed,
    m.matter_type,
    m.practice_area
FROM matters m
JOIN timekeeping t ON m.matter_id = t.matter_id
JOIN lawyer_rates lr ON t.lawyer_id = lr.lawyer_id
    AND t.time_entry_date BETWEEN lr.rate_effective_date
    AND COALESCE(lr.rate_end_date, CURDATE())
JOIN clients c ON m.client_id = c.client_id
WHERE DATE_TRUNC(t.time_entry_date, MONTH) = DATE_TRUNC(CURDATE(), MONTH)
GROUP BY m.matter_id, m.matter_name, m.client_id, c.client_name, m.matter_type, m.practice_area
ORDER BY total_billed DESC;

-- Query 4: Rate variance analysis
WITH rate_benchmarks AS (
    SELECT
        experience_level,
        practice_area,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY hourly_rate) as q1_rate,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY hourly_rate) as median_rate,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY hourly_rate) as q3_rate
    FROM lawyer_rates
    WHERE active = 1
    GROUP BY experience_level, practice_area
)
SELECT
    lr.lawyer_id,
    lr.lawyer_name,
    lr.experience_level,
    lr.practice_area,
    lr.hourly_rate,
    rb.median_rate,
    ROUND(lr.hourly_rate - rb.median_rate, 2) as variance_from_median,
    ROUND((lr.hourly_rate - rb.median_rate) / rb.median_rate * 100, 2) as pct_variance,
    CASE
        WHEN lr.hourly_rate < rb.q1_rate THEN 'Below Q1 - LOW'
        WHEN lr.hourly_rate BETWEEN rb.q1_rate AND rb.median_rate THEN 'Q1-Median - BELOW MARKET'
        WHEN lr.hourly_rate BETWEEN rb.median_rate AND rb.q3_rate THEN 'Median-Q3 - AT MARKET'
        ELSE 'Above Q3 - PREMIUM'
    END as rate_position
FROM lawyer_rates lr
JOIN rate_benchmarks rb ON lr.experience_level = rb.experience_level
    AND lr.practice_area = rb.practice_area
WHERE lr.active = 1
ORDER BY lr.practice_area, lr.experience_level, variance_from_median DESC;

-- Query 5: Realization rate by vendor/firm
SELECT
    v.vendor_id,
    v.vendor_name,
    v.vendor_type,
    COUNT(DISTINCT i.invoice_id) as num_invoices,
    ROUND(SUM(i.original_billed_amount), 2) as total_billed,
    ROUND(SUM(i.amount_paid), 2) as total_collected,
    ROUND(SUM(i.amount_paid) / SUM(i.original_billed_amount) * 100, 2) as realization_rate,
    ROUND(AVG(i.hourly_rate), 2) as avg_hourly_rate,
    AVG(i.hours_billed) as avg_hours_per_invoice,
    ROUND(SUM(i.adjustment_amount), 2) as total_adjustments
FROM vendors v
JOIN invoices i ON v.vendor_id = i.vendor_id
WHERE DATE_TRUNC(i.invoice_date, MONTH) >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
GROUP BY v.vendor_id, v.vendor_name, v.vendor_type
HAVING COUNT(DISTINCT i.invoice_id) >= 10
ORDER BY realization_rate DESC, total_billed DESC;

-- Query 6: Rate comparison - your rates vs market
SELECT
    'Your Organization' as organization,
    lr.experience_level,
    lr.practice_area,
    ROUND(AVG(lr.hourly_rate), 2) as avg_rate,
    'Your Rates' as rate_type
FROM lawyer_rates lr
WHERE lr.active = 1
GROUP BY lr.experience_level, lr.practice_area

UNION ALL

SELECT
    'Market Median' as organization,
    mb.experience_level,
    mb.practice_area,
    mb.median_market_rate,
    'Benchmark' as rate_type
FROM market_benchmarks mb
WHERE benchmark_date = (SELECT MAX(benchmark_date) FROM market_benchmarks)

ORDER BY experience_level, practice_area, organization;

-- Query 7: Cost efficiency - cost per deliverable by vendor
SELECT
    v.vendor_name,
    COUNT(DISTINCT d.deliverable_id) as total_deliverables,
    COUNT(DISTINCT d.matter_id) as matters_handled,
    ROUND(SUM(c.cost_amount) / COUNT(DISTINCT d.deliverable_id), 2) as cost_per_deliverable,
    ROUND(SUM(c.cost_amount), 2) as total_cost,
    ROUND(AVG(DATEDIFF(d.completion_date, d.due_date)), 1) as avg_days_variance,
    ROUND(AVG(d.quality_score), 2) as avg_quality_score,
    ROUND(SUM(CASE WHEN d.completion_date <= d.due_date THEN 1 ELSE 0 END)
        / COUNT(DISTINCT d.deliverable_id) * 100, 1) as on_time_pct
FROM vendors v
JOIN deliverables d ON v.vendor_id = d.vendor_id
JOIN vendor_costs c ON d.deliverable_id = c.deliverable_id
WHERE d.completion_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
GROUP BY v.vendor_name
ORDER BY cost_per_deliverable ASC;

-- Query 8: Rate increase impact analysis
WITH current_rates AS (
    SELECT
        lawyer_id,
        experience_level,
        hourly_rate,
        LAG(hourly_rate) OVER (PARTITION BY lawyer_id ORDER BY rate_effective_date) as previous_rate
    FROM lawyer_rates
    WHERE active = 1
    ORDER BY lawyer_id, rate_effective_date
)
SELECT
    experience_level,
    COUNT(DISTINCT lawyer_id) as num_lawyers,
    ROUND(AVG(hourly_rate - COALESCE(previous_rate, hourly_rate)), 2) as avg_increase,
    ROUND(AVG((hourly_rate - COALESCE(previous_rate, hourly_rate))
        / COALESCE(previous_rate, hourly_rate) * 100), 2) as avg_pct_increase,
    ROUND(MIN(hourly_rate - COALESCE(previous_rate, hourly_rate)), 2) as min_increase,
    ROUND(MAX(hourly_rate - COALESCE(previous_rate, hourly_rate)), 2) as max_increase
FROM current_rates
WHERE previous_rate IS NOT NULL
GROUP BY experience_level
ORDER BY experience_level;

-- Query 9: Discounted rate analysis
SELECT
    discount_type,
    COUNT(DISTINCT matter_id) as matters_using_discount,
    ROUND(AVG(discount_percentage), 2) as avg_discount_pct,
    ROUND(SUM(standard_rate * hours - discounted_amount), 2) as total_discount_value,
    ROUND(SUM(discounted_amount), 2) as total_revenue,
    ROUND(SUM(standard_rate * hours), 2) as revenue_at_standard_rate
FROM billing_discounts
WHERE discount_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
GROUP BY discount_type
ORDER BY total_discount_value DESC;

-- Query 10: Rate setting recommendations
WITH historical_data AS (
    SELECT
        experience_level,
        practice_area,
        AVG(hourly_rate) as current_avg_rate,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY hourly_rate) as market_75th,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY hourly_rate) as market_median,
        STDDEV(hourly_rate) as market_stddev
    FROM (
        SELECT hourly_rate, experience_level, practice_area
        FROM lawyer_rates WHERE active = 1
        UNION ALL
        SELECT market_rate, exp_level, practice_area
        FROM market_benchmarks WHERE benchmark_date = CURRENT_DATE()
    )
    GROUP BY experience_level, practice_area
)
SELECT
    experience_level,
    practice_area,
    ROUND(current_avg_rate, 2) as current_rate,
    ROUND(market_median, 2) as market_median,
    ROUND(market_75th, 2) as market_75th_percentile,
    ROUND(current_avg_rate - market_median, 2) as variance_from_median,
    CASE
        WHEN current_avg_rate < market_median * 0.95 THEN 'INCREASE - Below market'
        WHEN current_avg_rate BETWEEN market_median * 0.95 AND market_median * 1.05 THEN 'MAINTAIN - At market'
        ELSE 'MONITOR - Above market'
    END as recommendation
FROM historical_data
ORDER BY experience_level, practice_area;
