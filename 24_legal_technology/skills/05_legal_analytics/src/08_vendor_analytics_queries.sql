-- Vendor Performance Analytics Queries
-- Comprehensive analysis of vendor performance, quality, and cost

-- Query 1: Vendor scorecard with weighted metrics
WITH vendor_metrics AS (
    SELECT
        v.vendor_id,
        v.vendor_name,
        COUNT(DISTINCT i.invoice_id) as num_invoices,
        ROUND(SUM(i.amount_paid), 2) as total_spend,
        ROUND(AVG(i.realization_rate), 2) as avg_realization,
        ROUND(AVG(i.quality_score), 2) as avg_quality,
        ROUND(SUM(CASE WHEN d.completion_date <= d.due_date THEN 1 ELSE 0 END)
            / COUNT(DISTINCT d.deliverable_id) * 100, 1) as on_time_delivery_pct,
        ROUND(AVG(i.billing_accuracy), 2) as billing_accuracy_pct,
        DATE_TRUNC(MAX(i.invoice_date), MONTH) as last_invoice_month
    FROM vendors v
    LEFT JOIN invoices i ON v.vendor_id = i.vendor_id
    LEFT JOIN deliverables d ON v.vendor_id = d.vendor_id
    WHERE i.invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
    GROUP BY v.vendor_id, v.vendor_name
)
SELECT
    vendor_id,
    vendor_name,
    num_invoices,
    total_spend,
    avg_realization,
    avg_quality,
    on_time_delivery_pct,
    billing_accuracy_pct,
    ROUND(
        (1 - (total_spend / (SELECT SUM(total_spend) FROM vendor_metrics))) * 0.25 +
        (avg_quality / 5) * 0.35 +
        (on_time_delivery_pct / 100) * 0.20 +
        (billing_accuracy_pct / 100) * 0.10 +
        (avg_realization / 100) * 0.10,
        2
    ) as performance_score,
    CASE
        WHEN ROUND(
            (1 - (total_spend / (SELECT SUM(total_spend) FROM vendor_metrics))) * 0.25 +
            (avg_quality / 5) * 0.35 +
            (on_time_delivery_pct / 100) * 0.20 +
            (billing_accuracy_pct / 100) * 0.10 +
            (avg_realization / 100) * 0.10,
            2
        ) >= 0.80 THEN 'Excellent'
        WHEN ROUND(
            (1 - (total_spend / (SELECT SUM(total_spend) FROM vendor_metrics))) * 0.25 +
            (avg_quality / 5) * 0.35 +
            (on_time_delivery_pct / 100) * 0.20 +
            (billing_accuracy_pct / 100) * 0.10 +
            (avg_realization / 100) * 0.10,
            2
        ) >= 0.60 THEN 'Good'
        WHEN ROUND(
            (1 - (total_spend / (SELECT SUM(total_spend) FROM vendor_metrics))) * 0.25 +
            (avg_quality / 5) * 0.35 +
            (on_time_delivery_pct / 100) * 0.20 +
            (billing_accuracy_pct / 100) * 0.10 +
            (avg_realization / 100) * 0.10,
            2
        ) >= 0.40 THEN 'Acceptable'
        ELSE 'Poor'
    END as rating,
    last_invoice_month
FROM vendor_metrics
ORDER BY performance_score DESC;

-- Query 2: Vendor spend concentration analysis
WITH vendor_spend AS (
    SELECT
        v.vendor_id,
        v.vendor_name,
        SUM(i.amount_paid) as annual_spend
    FROM vendors v
    JOIN invoices i ON v.vendor_id = i.vendor_id
    WHERE i.invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
    GROUP BY v.vendor_id, v.vendor_name
)
SELECT
    vendor_name,
    annual_spend,
    (SELECT SUM(annual_spend) FROM vendor_spend) as total_spend,
    ROUND(annual_spend / (SELECT SUM(annual_spend) FROM vendor_spend) * 100, 2) as pct_of_total,
    SUM(annual_spend) OVER (ORDER BY annual_spend DESC) as cumulative_spend,
    ROUND(SUM(annual_spend) OVER (ORDER BY annual_spend DESC) / (SELECT SUM(annual_spend) FROM vendor_spend) * 100, 2) as cumulative_pct
FROM vendor_spend
ORDER BY annual_spend DESC;

-- Query 3: Vendor rate analysis - are we getting competitive rates?
WITH vendor_rates AS (
    SELECT
        v.vendor_id,
        v.vendor_name,
        i.rate_type,
        i.hourly_rate,
        COUNT(*) as num_invoices,
        ROUND(AVG(i.hourly_rate), 2) as avg_rate
    FROM vendors v
    JOIN invoices i ON v.vendor_id = i.vendor_id
    WHERE i.invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
    GROUP BY v.vendor_id, v.vendor_name, i.rate_type, i.hourly_rate
),
market_rates AS (
    SELECT
        rate_type,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY market_rate) as q1_rate,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY market_rate) as median_rate,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY market_rate) as q3_rate
    FROM market_benchmarks
    WHERE benchmark_date = CURRENT_DATE()
    GROUP BY rate_type
)
SELECT
    vr.vendor_name,
    vr.rate_type,
    vr.avg_rate,
    mr.median_rate,
    ROUND(vr.avg_rate - mr.median_rate, 2) as variance_from_median,
    ROUND((vr.avg_rate - mr.median_rate) / mr.median_rate * 100, 2) as pct_variance,
    CASE
        WHEN vr.avg_rate < mr.q1_rate THEN 'Below Market (Good)'
        WHEN vr.avg_rate BETWEEN mr.q1_rate AND mr.median_rate THEN 'Below Median (Good)'
        WHEN vr.avg_rate BETWEEN mr.median_rate AND mr.q3_rate THEN 'At Market (Fair)'
        ELSE 'Above Market (Expensive)'
    END as rate_position,
    vr.num_invoices
FROM vendor_rates vr
JOIN market_rates mr ON vr.rate_type = mr.rate_type
ORDER BY vr.vendor_name, vr.rate_type;

-- Query 4: Vendor performance trend
SELECT
    DATE_TRUNC(i.invoice_date, MONTH) as month,
    v.vendor_name,
    COUNT(DISTINCT i.invoice_id) as num_invoices,
    ROUND(AVG(i.quality_score), 2) as avg_quality,
    ROUND(AVG(i.realization_rate), 2) as avg_realization,
    ROUND(SUM(i.amount_paid), 2) as monthly_spend,
    ROUND(AVG(DATEDIFF(d.completion_date, d.due_date)), 1) as avg_days_late
FROM vendors v
LEFT JOIN invoices i ON v.vendor_id = i.vendor_id
LEFT JOIN deliverables d ON v.vendor_id = d.vendor_id
WHERE i.invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
GROUP BY month, v.vendor_name
ORDER BY v.vendor_name, month DESC;

-- Query 5: Vendor by matter type - specialization analysis
SELECT
    v.vendor_name,
    m.matter_type,
    COUNT(DISTINCT m.matter_id) as num_matters,
    ROUND(SUM(i.amount_paid), 2) as total_spend,
    ROUND(AVG(i.quality_score), 2) as avg_quality,
    ROUND(AVG(i.realization_rate), 2) as avg_realization,
    ROUND(SUM(i.amount_paid) / COUNT(DISTINCT m.matter_id), 2) as cost_per_matter,
    COUNT(DISTINCT m.matter_id) / (SELECT COUNT(DISTINCT matter_id) FROM matters WHERE DATE_TRUNC(matter_open_date, MONTH) >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)) * 100 as pct_of_all_matters
FROM vendors v
JOIN invoices i ON v.vendor_id = i.vendor_id
JOIN matters m ON i.matter_id = m.matter_id
WHERE i.invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
GROUP BY v.vendor_name, m.matter_type
HAVING COUNT(DISTINCT m.matter_id) >= 3
ORDER BY v.vendor_name, total_spend DESC;

-- Query 6: Vendor consolidation opportunity analysis
SELECT
    v.vendor_name,
    v.vendor_status,
    COUNT(DISTINCT i.invoice_id) as annual_invoices,
    ROUND(SUM(i.amount_paid), 2) as annual_spend,
    ROUND(SUM(i.amount_paid) / COUNT(DISTINCT i.invoice_id), 2) as avg_invoice_size,
    ROUND(AVG(i.quality_score), 2) as avg_quality,
    CASE
        WHEN COUNT(DISTINCT i.invoice_id) < 5 AND SUM(i.amount_paid) < 50000 THEN 'Low Activity - Consolidation Candidate'
        WHEN ROUND(AVG(i.quality_score), 2) < 3.5 THEN 'Low Quality - Replacement Candidate'
        WHEN ROUND(AVG(i.quality_score), 2) > 4.3 AND SUM(i.amount_paid) > 100000 THEN 'Strategic Partner - Expand'
        ELSE 'Core Vendor'
    END as recommendation
FROM vendors v
LEFT JOIN invoices i ON v.vendor_id = i.vendor_id
WHERE i.invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
    AND v.vendor_status = 'Active'
GROUP BY v.vendor_id, v.vendor_name, v.vendor_status
ORDER BY annual_spend DESC;

-- Query 7: Cost reduction opportunity analysis
WITH vendor_analysis AS (
    SELECT
        v.vendor_id,
        v.vendor_name,
        SUM(i.amount_paid) as current_spend,
        ROUND(AVG(i.hourly_rate), 2) as current_rate,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY mb.market_rate) as market_median,
        ROUND((SUM(i.amount_paid) - (SUM(i.amount_paid) / AVG(i.hourly_rate)) *
            PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY mb.market_rate)) / SUM(i.amount_paid) * 100, 2) as potential_savings_pct,
        ROUND(SUM(i.amount_paid) - (SUM(i.amount_paid) / AVG(i.hourly_rate)) *
            PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY mb.market_rate), 2) as potential_savings_dollars
    FROM vendors v
    JOIN invoices i ON v.vendor_id = i.vendor_id
    LEFT JOIN market_benchmarks mb ON i.rate_type = mb.rate_type
    WHERE i.invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        AND mb.benchmark_date = CURRENT_DATE()
    GROUP BY v.vendor_id, v.vendor_name
)
SELECT
    vendor_name,
    ROUND(current_spend, 2) as current_annual_spend,
    ROUND(current_rate, 2) as current_avg_rate,
    ROUND(market_median, 2) as market_median_rate,
    potential_savings_pct,
    potential_savings_dollars,
    CASE
        WHEN potential_savings_pct > 15 THEN 'High - Negotiate Immediately'
        WHEN potential_savings_pct > 10 THEN 'Medium - Schedule Negotiation'
        WHEN potential_savings_pct > 5 THEN 'Low - Monitor'
        ELSE 'Competitive'
    END as negotiation_priority
FROM vendor_analysis
WHERE potential_savings_pct > 0
ORDER BY potential_savings_dollars DESC;

-- Query 8: Vendor diversity analysis
SELECT
    CASE
        WHEN vendor_type = 'Law Firm' THEN 'Law Firms'
        WHEN vendor_type = 'Consulting' THEN 'Consultants'
        WHEN vendor_type = 'Individual' THEN 'Individual Practitioners'
        WHEN vendor_type = 'Specialty Service' THEN 'Specialty Services'
        ELSE vendor_type
    END as vendor_category,
    COUNT(DISTINCT vendor_id) as num_vendors,
    ROUND(SUM(annual_spend), 2) as total_spend,
    ROUND(SUM(annual_spend) / (SELECT SUM(annual_spend) FROM (
        SELECT SUM(amount_paid) as annual_spend
        FROM invoices
        WHERE invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
    )) * 100, 2) as pct_of_total,
    ROUND(AVG(annual_spend), 2) as avg_vendor_spend
FROM (
    SELECT
        v.vendor_id,
        v.vendor_type,
        SUM(i.amount_paid) as annual_spend
    FROM vendors v
    JOIN invoices i ON v.vendor_id = i.vendor_id
    WHERE i.invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
    GROUP BY v.vendor_id, v.vendor_type
) vendor_data
GROUP BY vendor_category
ORDER BY total_spend DESC;
