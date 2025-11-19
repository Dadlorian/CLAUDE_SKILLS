-- Snowflake Healthcare Analytics Queries
-- Optimized for Snowflake data warehouse

-- Query 1: Population Health Summary
SELECT
    COUNT(DISTINCT patient_key) AS total_population,
    AVG(age) AS avg_age,
    COUNT(DISTINCT CASE WHEN has_diabetes THEN patient_key END) AS diabetic_patients,
    COUNT(DISTINCT CASE WHEN has_hypertension THEN patient_key END) AS hypertensive_patients,
    AVG(hcc_raf_score) AS avg_risk_score,
    SUM(total_cost_12mo) AS total_cost,
    AVG(total_cost_12mo) / 12 AS avg_pmpm
FROM analytics.patient_summary
WHERE measurement_date = CURRENT_DATE;

-- Query 2: Monthly Quality Measure Trends
WITH monthly_quality AS (
    SELECT
        DATE_TRUNC('month', measurement_date) AS month,
        measure_id,
        measure_name,
        SUM(numerator) AS numerator,
        SUM(denominator) AS denominator,
        DIV0(SUM(numerator), SUM(denominator)) * 100 AS rate
    FROM analytics.quality_measures
    WHERE measurement_date >= DATEADD('month', -12, CURRENT_DATE)
    GROUP BY 1, 2, 3
)
SELECT
    month,
    measure_name,
    rate,
    LAG(rate) OVER (PARTITION BY measure_id ORDER BY month) AS prior_month_rate,
    rate - LAG(rate) OVER (PARTITION BY measure_id ORDER BY month) AS rate_change
FROM monthly_quality
ORDER BY measure_id, month;

-- Query 3: High-Risk Patient Identification
SELECT
    p.patient_key,
    p.mrn,
    p.patient_name,
    p.age,
    p.chronic_condition_count,
    p.hcc_raf_score,
    u.ed_visits_12mo,
    u.ip_admits_12mo,
    c.total_cost_12mo,
    rs.risk_score,
    rs.risk_tier
FROM analytics.dim_patient p
JOIN analytics.patient_utilization u ON p.patient_key = u.patient_key
JOIN analytics.patient_cost c ON p.patient_key = c.patient_key
JOIN analytics.patient_risk_stratification rs ON p.patient_key = rs.patient_key
WHERE rs.risk_tier = 'High'
    AND p.current_flag = TRUE
ORDER BY rs.risk_score DESC
LIMIT 1000;

-- Query 4: Provider Performance Dashboard
SELECT
    prov.provider_key,
    prov.provider_name,
    prov.specialty,
    COUNT(DISTINCT e.patient_key) AS panel_size,
    AVG(p.hcc_raf_score) AS avg_panel_risk,
    COUNT(DISTINCT e.encounter_key) AS total_encounters,
    AVG(CASE WHEN e.encounter_type = 'Inpatient' THEN e.length_of_stay END) AS avg_los,
    SUM(CASE WHEN e.readmission_30d_flag THEN 1 ELSE 0 END)::FLOAT /
        NULLIF(COUNT(CASE WHEN e.encounter_type = 'Inpatient' THEN 1 END), 0) * 100 AS readmission_rate,
    q.composite_quality_score
FROM analytics.dim_provider prov
JOIN analytics.fact_encounter e ON prov.provider_key = e.provider_key
JOIN analytics.dim_patient p ON e.patient_key = p.patient_key
LEFT JOIN analytics.provider_quality q ON prov.provider_key = q.provider_key
WHERE e.admission_date >= DATEADD('year', -1, CURRENT_DATE)
    AND prov.current_flag = TRUE
GROUP BY prov.provider_key, prov.provider_name, prov.specialty, q.composite_quality_score;

-- Query 5: Care Gap Closure Tracking
SELECT
    cg.gap_type,
    cg.measure_id,
    COUNT(DISTINCT cg.patient_key) AS patients_with_gap,
    COUNT(DISTINCT CASE WHEN cg.gap_closed_date IS NOT NULL THEN cg.patient_key END) AS gaps_closed,
    DIV0(COUNT(DISTINCT CASE WHEN cg.gap_closed_date IS NOT NULL THEN cg.patient_key END),
         COUNT(DISTINCT cg.patient_key)) * 100 AS closure_rate,
    AVG(DATEDIFF('day', cg.gap_identified_date, cg.gap_closed_date)) AS avg_days_to_close
FROM analytics.care_gaps cg
WHERE cg.gap_identified_date >= DATEADD('year', -1, CURRENT_DATE)
GROUP BY cg.gap_type, cg.measure_id
ORDER BY closure_rate DESC;

-- Query 6: Utilization Trends by Risk Tier
SELECT
    DATE_TRUNC('month', e.admission_date) AS month,
    rs.risk_tier,
    COUNT(DISTINCT e.encounter_key) AS encounters,
    SUM(CASE WHEN e.encounter_type = 'Inpatient' THEN 1 ELSE 0 END) AS ip_admits,
    SUM(CASE WHEN e.encounter_type = 'ED' THEN 1 ELSE 0 END) AS ed_visits,
    AVG(e.total_charges) AS avg_charges
FROM analytics.fact_encounter e
JOIN analytics.patient_risk_stratification rs ON e.patient_key = rs.patient_key
WHERE e.admission_date >= DATEADD('month', -12, CURRENT_DATE)
GROUP BY 1, 2
ORDER BY 1, 2;
