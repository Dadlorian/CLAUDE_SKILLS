-- Matter Profitability Analysis Queries
-- Analyzes matter costs, revenue, and profitability by various dimensions

-- Query 1: Matter profitability summary
SELECT
    m.matter_id,
    m.matter_name,
    m.client_id,
    c.client_name,
    m.matter_type,
    m.practice_area,
    m.status,
    DATE_TRUNC(m.matter_open_date, MONTH) as open_month,
    COALESCE(DATE_TRUNC(m.matter_close_date, MONTH), 'Open') as close_month,
    ROUND(SUM(t.hours * lr.hourly_rate), 2) as labor_cost,
    ROUND(SUM(d.disbursement_amount), 2) as total_disbursements,
    ROUND(SUM(t.hours * lr.hourly_rate) + COALESCE(SUM(d.disbursement_amount), 0), 2) as total_cost,
    ROUND(m.billed_amount, 2) as revenue,
    ROUND(m.billed_amount - (SUM(t.hours * lr.hourly_rate) + COALESCE(SUM(d.disbursement_amount), 0)), 2) as gross_profit,
    ROUND((m.billed_amount - (SUM(t.hours * lr.hourly_rate) + COALESCE(SUM(d.disbursement_amount), 0))) / m.billed_amount * 100, 1) as profit_margin_pct,
    ROUND(m.billed_amount / (SUM(t.hours * lr.hourly_rate) + COALESCE(SUM(d.disbursement_amount), 0)), 2) as profit_multiple,
    m.outcome
FROM matters m
JOIN clients c ON m.client_id = c.client_id
LEFT JOIN timekeeping t ON m.matter_id = t.matter_id
LEFT JOIN lawyer_rates lr ON t.lawyer_id = lr.lawyer_id
    AND t.time_entry_date BETWEEN lr.rate_effective_date
    AND COALESCE(lr.rate_end_date, CURDATE())
LEFT JOIN disbursements d ON m.matter_id = d.matter_id
GROUP BY m.matter_id, m.matter_name, m.client_id, c.client_name, m.matter_type,
    m.practice_area, m.status, m.matter_open_date, m.matter_close_date,
    m.billed_amount, m.outcome
HAVING m.billed_amount > 0
ORDER BY gross_profit DESC;

-- Query 2: Profitability by practice area
SELECT
    m.practice_area,
    COUNT(DISTINCT m.matter_id) as num_matters,
    ROUND(AVG(m.billed_amount), 2) as avg_matter_revenue,
    ROUND(SUM(m.billed_amount), 2) as total_revenue,
    ROUND(SUM(m.billed_amount) - SUM(COALESCE(
        (SELECT SUM(t2.hours * lr2.hourly_rate)
         FROM timekeeping t2
         JOIN lawyer_rates lr2 ON t2.lawyer_id = lr2.lawyer_id
             AND t2.time_entry_date BETWEEN lr2.rate_effective_date
             AND COALESCE(lr2.rate_end_date, CURDATE())
         WHERE t2.matter_id = m.matter_id), 0
    ) + COALESCE(
        (SELECT SUM(d2.disbursement_amount)
         FROM disbursements d2
         WHERE d2.matter_id = m.matter_id), 0
    )), 2) as total_profit,
    ROUND((SUM(m.billed_amount) - SUM(COALESCE(
        (SELECT SUM(t2.hours * lr2.hourly_rate)
         FROM timekeeping t2
         JOIN lawyer_rates lr2 ON t2.lawyer_id = lr2.lawyer_id
             AND t2.time_entry_date BETWEEN lr2.rate_effective_date
             AND COALESCE(lr2.rate_end_date, CURDATE())
         WHERE t2.matter_id = m.matter_id), 0
    ) + COALESCE(
        (SELECT SUM(d2.disbursement_amount)
         FROM disbursements d2
         WHERE d2.matter_id = m.matter_id), 0
    ))) / SUM(m.billed_amount) * 100, 1) as profit_margin_pct
FROM matters m
WHERE m.status IN ('Closed', 'Settled')
    AND m.matter_close_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
GROUP BY m.practice_area
ORDER BY total_profit DESC;

-- Query 3: Profitability by matter type and outcome
SELECT
    m.matter_type,
    m.outcome,
    COUNT(DISTINCT m.matter_id) as num_matters,
    ROUND(AVG(m.billed_amount), 2) as avg_revenue,
    ROUND(AVG(DATEDIFF(m.matter_close_date, m.matter_open_date)) / 30, 1) as avg_duration_months,
    ROUND(SUM(m.billed_amount), 2) as total_revenue,
    ROUND(SUM(m.billed_amount) / COUNT(DISTINCT m.matter_id) -
        (SELECT AVG(cost)
         FROM (SELECT m2.matter_id,
               SUM(t2.hours * lr2.hourly_rate) + COALESCE(SUM(d2.disbursement_amount), 0) as cost
               FROM matters m2
               LEFT JOIN timekeeping t2 ON m2.matter_id = t2.matter_id
               LEFT JOIN lawyer_rates lr2 ON t2.lawyer_id = lr2.lawyer_id
                   AND t2.time_entry_date BETWEEN lr2.rate_effective_date
                   AND COALESCE(lr2.rate_end_date, CURDATE())
               LEFT JOIN disbursements d2 ON m2.matter_id = d2.matter_id
               WHERE m2.matter_type = m.matter_type
               GROUP BY m2.matter_id) costs), 2) as avg_profit
FROM matters m
WHERE m.status IN ('Closed', 'Settled')
    AND m.matter_close_date >= DATE_SUB(CURDATE(), INTERVAL 24 MONTH)
GROUP BY m.matter_type, m.outcome
ORDER BY total_revenue DESC;

-- Query 4: Cost breakdown by matter
SELECT
    m.matter_id,
    m.matter_name,
    ROUND(SUM(CASE WHEN t.lawyer_id IS NOT NULL THEN t.hours * lr.hourly_rate ELSE 0 END), 2) as labor_cost,
    ROUND(SUM(CASE WHEN d.disbursement_type = 'Expert Witness' THEN d.disbursement_amount ELSE 0 END), 2) as expert_cost,
    ROUND(SUM(CASE WHEN d.disbursement_type = 'Court Reporter' THEN d.disbursement_amount ELSE 0 END), 2) as court_reporter_cost,
    ROUND(SUM(CASE WHEN d.disbursement_type = 'Document Review' THEN d.disbursement_amount ELSE 0 END), 2) as doc_review_cost,
    ROUND(SUM(CASE WHEN d.disbursement_type = 'Travel' THEN d.disbursement_amount ELSE 0 END), 2) as travel_cost,
    ROUND(SUM(CASE WHEN d.disbursement_type NOT IN ('Expert Witness', 'Court Reporter', 'Document Review', 'Travel')
                   THEN d.disbursement_amount ELSE 0 END), 2) as other_cost,
    ROUND(SUM(CASE WHEN t.lawyer_id IS NOT NULL THEN t.hours * lr.hourly_rate ELSE 0 END)
        + COALESCE(SUM(d.disbursement_amount), 0), 2) as total_cost,
    ROUND(SUM(CASE WHEN t.lawyer_id IS NOT NULL THEN t.hours * lr.hourly_rate ELSE 0 END) / NULLIF(SUM(CASE WHEN t.lawyer_id IS NOT NULL THEN t.hours * lr.hourly_rate ELSE 0 END)
        + COALESCE(SUM(d.disbursement_amount), 0), 0) * 100, 1) as labor_pct_of_cost
FROM matters m
LEFT JOIN timekeeping t ON m.matter_id = t.matter_id
LEFT JOIN lawyer_rates lr ON t.lawyer_id = lr.lawyer_id
    AND t.time_entry_date BETWEEN lr.rate_effective_date
    AND COALESCE(lr.rate_end_date, CURDATE())
LEFT JOIN disbursements d ON m.matter_id = d.matter_id
WHERE m.matter_close_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
GROUP BY m.matter_id, m.matter_name
ORDER BY total_cost DESC;

-- Query 5: High-value vs low-value matters analysis
WITH matter_values AS (
    SELECT
        m.matter_id,
        m.billed_amount,
        SUM(t.hours * lr.hourly_rate) + COALESCE(SUM(d.disbursement_amount), 0) as cost,
        m.billed_amount - (SUM(t.hours * lr.hourly_rate) + COALESCE(SUM(d.disbursement_amount), 0)) as profit
    FROM matters m
    LEFT JOIN timekeeping t ON m.matter_id = t.matter_id
    LEFT JOIN lawyer_rates lr ON t.lawyer_id = lr.lawyer_id
    LEFT JOIN disbursements d ON m.matter_id = d.matter_id
    WHERE m.status IN ('Closed', 'Settled')
    GROUP BY m.matter_id, m.billed_amount
)
SELECT
    CASE WHEN billed_amount > (SELECT PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY billed_amount) FROM matter_values) THEN 'High Value'
         WHEN billed_amount < (SELECT PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY billed_amount) FROM matter_values) THEN 'Low Value'
         ELSE 'Mid Value'
    END as value_category,
    COUNT(*) as num_matters,
    ROUND(AVG(cost), 2) as avg_cost,
    ROUND(AVG(billed_amount), 2) as avg_revenue,
    ROUND(AVG(profit), 2) as avg_profit,
    ROUND(AVG(profit) / NULLIF(AVG(billed_amount), 0) * 100, 1) as avg_margin_pct,
    ROUND(SUM(profit), 2) as total_profit
FROM matter_values
GROUP BY value_category
ORDER BY total_profit DESC;

-- Query 6: Profitability trend over time
SELECT
    DATE_TRUNC(m.matter_close_date, MONTH) as month,
    COUNT(DISTINCT m.matter_id) as matters_closed,
    ROUND(SUM(m.billed_amount), 2) as monthly_revenue,
    ROUND(SUM(m.billed_amount) - (
        SELECT SUM(cost)
        FROM (SELECT m2.matter_id,
                     SUM(t2.hours * lr2.hourly_rate) + COALESCE(SUM(d2.disbursement_amount), 0) as cost
              FROM matters m2
              LEFT JOIN timekeeping t2 ON m2.matter_id = t2.matter_id
              LEFT JOIN lawyer_rates lr2 ON t2.lawyer_id = lr2.lawyer_id
              LEFT JOIN disbursements d2 ON m2.matter_id = d2.matter_id
              WHERE DATE_TRUNC(m2.matter_close_date, MONTH) = DATE_TRUNC(m.matter_close_date, MONTH)
              GROUP BY m2.matter_id) costs
    ), 2) as monthly_profit,
    ROUND((SUM(m.billed_amount) - (
        SELECT SUM(cost)
        FROM (SELECT m2.matter_id,
                     SUM(t2.hours * lr2.hourly_rate) + COALESCE(SUM(d2.disbursement_amount), 0) as cost
              FROM matters m2
              LEFT JOIN timekeeping t2 ON m2.matter_id = t2.matter_id
              LEFT JOIN lawyer_rates lr2 ON t2.lawyer_id = lr2.lawyer_id
              LEFT JOIN disbursements d2 ON m2.matter_id = d2.matter_id
              WHERE DATE_TRUNC(m2.matter_close_date, MONTH) = DATE_TRUNC(m.matter_close_date, MONTH)
              GROUP BY m2.matter_id) costs
    )) / SUM(m.billed_amount) * 100, 1) as profit_margin_pct
FROM matters m
WHERE m.status IN ('Closed', 'Settled')
    AND m.matter_close_date >= DATE_SUB(CURDATE(), INTERVAL 24 MONTH)
GROUP BY month
ORDER BY month DESC;
