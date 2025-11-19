-- Benchmarking Analysis Queries
-- Compare legal department performance against industry standards

-- Query 1: Internal benchmarking - compare across departments
SELECT
    department,
    COUNT(DISTINCT lawyer_id) as num_lawyers,
    ROUND(SUM(billable_hours), 2) as total_billable_hours,
    ROUND(AVG(billable_hours), 2) as avg_billable_hours_per_person,
    ROUND(SUM(billable_hours) / COUNT(DISTINCT lawyer_id) / (250 * 8) * 100, 1) as utilization_rate_pct,
    ROUND(SUM(billable_hours * hourly_rate), 2) as total_revenue,
    ROUND(AVG(quality_score), 2) as avg_quality_score,
    ROUND(SUM(CASE WHEN on_time_delivery THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as on_time_delivery_pct,
    ROUND(SUM(matters_handled), 0) / COUNT(DISTINCT lawyer_id) as matters_per_person
FROM (
    SELECT
        l.department,
        l.lawyer_id,
        SUM(t.billable_hours) as billable_hours,
        AVG(lr.hourly_rate) as hourly_rate,
        AVG(m.quality_score) as quality_score,
        COUNT(DISTINCT m.matter_id) as matters_handled,
        AVG(CASE WHEN d.completion_date <= d.due_date THEN 1 ELSE 0 END) as on_time_delivery
    FROM lawyers l
    LEFT JOIN timekeeping t ON l.lawyer_id = t.lawyer_id
    LEFT JOIN lawyer_rates lr ON l.lawyer_id = lr.lawyer_id
    LEFT JOIN matters m ON t.matter_id = m.matter_id
    LEFT JOIN deliverables d ON l.lawyer_id = d.assigned_lawyer_id
    WHERE t.time_entry_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
    GROUP BY l.lawyer_id, l.department
) lawyer_data
GROUP BY department
ORDER BY total_revenue DESC;

-- Query 2: Comparing your metrics to market benchmarks
WITH your_org_metrics AS (
    SELECT
        'Your Organization' as organization,
        ROUND(SUM(billed_amount) / COUNT(DISTINCT lawyer_id), 2) as revenue_per_lawyer,
        ROUND(SUM(billable_hours) / COUNT(DISTINCT lawyer_id) / (250 * 8) * 100, 1) as utilization_rate_pct,
        ROUND(SUM(billed_amount) / SUM(cost), 2) as profit_multiple,
        ROUND(AVG(quality_score), 2) as avg_quality,
        ROUND(SUM(CASE WHEN realization_rate > 0.95 THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as high_realization_pct
    FROM (
        SELECT
            m.matter_id,
            m.billed_amount,
            l.lawyer_id,
            SUM(t.billable_hours) as billable_hours,
            SUM(c.cost) as cost,
            m.quality_score,
            m.realization_rate
        FROM matters m
        JOIN timekeeping t ON m.matter_id = t.matter_id
        JOIN lawyers l ON t.lawyer_id = l.lawyer_id
        LEFT JOIN costs c ON m.matter_id = c.matter_id
        WHERE m.close_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY m.matter_id, l.lawyer_id
    ) your_data
)
SELECT
    'Your Organization' as organization,
    (SELECT revenue_per_lawyer FROM your_org_metrics) as revenue_per_lawyer,
    (SELECT utilization_rate_pct FROM your_org_metrics) as utilization_pct,
    (SELECT profit_multiple FROM your_org_metrics) as profit_multiple,
    (SELECT avg_quality FROM your_org_metrics) as avg_quality,
    (SELECT high_realization_pct FROM your_org_metrics) as high_realization_pct

UNION ALL

SELECT
    'Industry Median (Fortune 500)',
    2500000,
    78.5,
    1.8,
    4.1,
    92.0

UNION ALL

SELECT
    'Top Quartile',
    3200000,
    85.0,
    2.2,
    4.5,
    96.0;

-- Query 3: Rate benchmarking across experience levels
WITH your_rates AS (
    SELECT
        experience_level,
        ROUND(AVG(hourly_rate), 2) as your_rate,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY hourly_rate) as your_q1,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY hourly_rate) as your_median,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY hourly_rate) as your_q3
    FROM lawyer_rates
    WHERE active = 1
    GROUP BY experience_level
)
SELECT
    yr.experience_level,
    yr.your_rate,
    mb.market_q1_rate,
    mb.market_median_rate,
    mb.market_q3_rate,
    ROUND(yr.your_rate - mb.market_median_rate, 2) as variance_from_median,
    ROUND((yr.your_rate - mb.market_median_rate) / mb.market_median_rate * 100, 2) as pct_variance,
    CASE
        WHEN yr.your_rate < mb.market_q1_rate THEN 'Below Market - Competitive Advantage'
        WHEN yr.your_rate BETWEEN mb.market_q1_rate AND mb.market_median_rate THEN 'Below Market - Good Position'
        WHEN yr.your_rate BETWEEN mb.market_median_rate AND mb.market_q3_rate THEN 'At Market - Fair Position'
        ELSE 'Above Market - Reconsider'
    END as assessment
FROM your_rates yr
JOIN market_benchmarks mb ON yr.experience_level = mb.experience_level
WHERE mb.benchmark_date = (SELECT MAX(benchmark_date) FROM market_benchmarks)
ORDER BY yr.experience_level;

-- Query 4: Practice area benchmarking
SELECT
    m.practice_area,
    COUNT(DISTINCT m.matter_id) as num_matters,
    ROUND(SUM(m.billed_amount), 2) as total_revenue,
    ROUND(AVG(m.billed_amount), 2) as avg_matter_value,
    ROUND(SUM(c.cost), 2) as total_cost,
    ROUND(AVG(m.quality_score), 2) as avg_quality,
    ROUND(AVG(DATEDIFF(m.close_date, m.open_date) / 30), 1) as avg_duration_months,
    ROUND(SUM(m.billed_amount) / SUM(c.cost), 2) as profit_multiple,
    CASE
        WHEN ROUND(AVG(m.quality_score), 2) > 4.2 AND ROUND(SUM(m.billed_amount) / SUM(c.cost), 2) > 2.0
            THEN 'Excellent'
        WHEN ROUND(AVG(m.quality_score), 2) > 4.0 AND ROUND(SUM(m.billed_amount) / SUM(c.cost), 2) > 1.8
            THEN 'Good'
        WHEN ROUND(AVG(m.quality_score), 2) >= 3.8 AND ROUND(SUM(m.billed_amount) / SUM(c.cost), 2) >= 1.5
            THEN 'Acceptable'
        ELSE 'Needs Improvement'
    END as performance_rating
FROM matters m
LEFT JOIN costs c ON m.matter_id = c.matter_id
WHERE m.close_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
GROUP BY m.practice_area
ORDER BY total_revenue DESC;

-- Query 5: Client satisfaction benchmarking
SELECT
    c.client_name,
    c.industry,
    COUNT(DISTINCT m.matter_id) as num_matters,
    ROUND(AVG(m.satisfaction_score), 2) as avg_satisfaction,
    ROUND(AVG(m.nps_score), 1) as avg_nps,
    CASE
        WHEN ROUND(AVG(m.nps_score), 1) > 70 THEN 'Promoters'
        WHEN ROUND(AVG(m.nps_score), 1) >= 50 THEN 'Passives'
        ELSE 'Detractors'
    END as nps_category,
    CASE
        WHEN ROUND(AVG(m.satisfaction_score), 2) > 4.5 AND ROUND(AVG(m.nps_score), 1) > 70 THEN 'Excellent'
        WHEN ROUND(AVG(m.satisfaction_score), 2) > 4.0 AND ROUND(AVG(m.nps_score), 1) > 50 THEN 'Good'
        WHEN ROUND(AVG(m.satisfaction_score), 2) >= 3.5 THEN 'Acceptable'
        ELSE 'At Risk'
    END as client_relationship_health
FROM clients c
JOIN matters m ON c.client_id = m.client_id
WHERE m.close_date >= DATE_SUB(CURDATE(), INTERVAL 24 MONTH)
GROUP BY c.client_id, c.client_name, c.industry
HAVING COUNT(DISTINCT m.matter_id) >= 2
ORDER BY avg_satisfaction DESC;

-- Query 6: Cost efficiency benchmarking
SELECT
    m.matter_type,
    m.practice_area,
    COUNT(DISTINCT m.matter_id) as num_matters,
    ROUND(AVG(c.cost), 2) as avg_cost_per_matter,
    ROUND(AVG(DATEDIFF(m.close_date, m.open_date)), 0) as avg_duration_days,
    ROUND(AVG(c.cost) / NULLIF(AVG(DATEDIFF(m.close_date, m.open_date)), 0), 2) as cost_per_day,
    ROUND(AVG(m.billed_amount) / NULLIF(AVG(c.cost), 0), 2) as efficiency_ratio,
    CASE
        WHEN ROUND(AVG(m.billed_amount) / NULLIF(AVG(c.cost), 0), 2) > 2.5 THEN 'Highly Efficient'
        WHEN ROUND(AVG(m.billed_amount) / NULLIF(AVG(c.cost), 0), 2) > 2.0 THEN 'Efficient'
        WHEN ROUND(AVG(m.billed_amount) / NULLIF(AVG(c.cost), 0), 2) > 1.5 THEN 'Acceptable'
        ELSE 'Below Target - Improvement Needed'
    END as efficiency_assessment
FROM matters m
LEFT JOIN costs c ON m.matter_id = c.matter_id
WHERE m.close_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
GROUP BY m.matter_type, m.practice_area
ORDER BY efficiency_ratio DESC;

-- Query 7: Benchmarking - Best practices identification
SELECT
    'Fastest Case Resolution' as benchmark_category,
    m.practice_area,
    m.matter_type,
    ROUND(AVG(DATEDIFF(m.close_date, m.open_date) / 30), 1) as duration_months,
    ROUND(AVG(m.quality_score), 2) as avg_quality,
    ROUND(AVG(m.billed_amount) / NULLIF(AVG(c.cost), 0), 2) as profit_multiple,
    'Focus on quick case disposition without compromising quality' as lesson
FROM matters m
LEFT JOIN costs c ON m.matter_id = c.matter_id
WHERE m.close_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
GROUP BY m.practice_area, m.matter_type
HAVING ROUND(AVG(DATEDIFF(m.close_date, m.open_date) / 30), 1) < 12
ORDER BY duration_months ASC
LIMIT 10;
