-- Financial Analysis Queries
-- Analyze financial terms, spending, and contract values

-- Query 1: Total contract value and commitment
SELECT 
    SUM(c.contract_value) as total_contract_value,
    COUNT(*) as total_contracts,
    AVG(c.contract_value) as avg_contract_value,
    MIN(c.contract_value) as min_contract_value,
    MAX(c.contract_value) as max_contract_value,
    c.currency
FROM contracts c
WHERE c.status IN ('Active', 'Executed')
AND c.contract_value IS NOT NULL
GROUP BY c.currency;

-- Query 2: Spending by vendor
SELECT 
    p.legal_name as vendor,
    p.party_type,
    COUNT(c.id) as contract_count,
    SUM(c.contract_value) as total_spend,
    AVG(c.contract_value) as avg_contract_value,
    MAX(c.contract_value) as largest_contract,
    COUNT(DISTINCT c.contract_type) as contract_types,
    ROUND(SUM(c.contract_value) * 100.0 / (SELECT SUM(contract_value) FROM contracts WHERE status IN ('Active', 'Executed')), 2) as percent_of_total
FROM contracts c
LEFT JOIN parties p ON c.counterparty_id = p.id
WHERE c.status IN ('Active', 'Executed')
AND c.contract_value IS NOT NULL
GROUP BY p.id, p.legal_name, p.party_type
ORDER BY total_spend DESC;

-- Query 3: Payment terms analysis
SELECT 
    c.payment_terms,
    COUNT(*) as contract_count,
    AVG(c.contract_value) as avg_contract_value,
    SUM(c.contract_value) as total_value,
    ROUND((COUNT(*) * 100.0) / (SELECT COUNT(*) FROM contracts WHERE status IN ('Active', 'Executed')), 2) as percent_of_contracts
FROM contracts c
WHERE c.status IN ('Active', 'Executed')
AND c.payment_terms IS NOT NULL
GROUP BY c.payment_terms
ORDER BY contract_count DESC;

-- Query 4: Contract expiration and renewal revenue impact
SELECT 
    DATE_TRUNC('quarter', c.expiration_date)::DATE as quarter,
    COUNT(*) as expiring_contracts,
    SUM(c.contract_value) as revenue_at_risk,
    ROUND(SUM(c.contract_value) * 100.0 / (SELECT SUM(contract_value) FROM contracts WHERE status = 'Active'), 2) as percent_of_active_revenue,
    COUNT(DISTINCT c.contract_type) as contract_types
FROM contracts c
WHERE c.expiration_date >= CURRENT_DATE
AND c.status IN ('Active', 'Executed')
GROUP BY DATE_TRUNC('quarter', c.expiration_date)
ORDER BY quarter ASC;

-- Query 5: Cost escalation analysis
SELECT 
    c.reference_number,
    c.title,
    p.legal_name as vendor,
    c.contract_value as initial_value,
    c.metadata->>'escalation_rate' as escalation_rate,
    c.effective_date,
    c.expiration_date,
    ROUND(c.contract_value * (1 + CAST(c.metadata->>'escalation_rate' AS DECIMAL))^(EXTRACT(YEAR FROM c.expiration_date) - EXTRACT(YEAR FROM c.effective_date)), 2) as projected_final_value,
    ROUND(CAST(c.metadata->>'escalation_rate' AS DECIMAL) * c.contract_value * (EXTRACT(YEAR FROM c.expiration_date) - EXTRACT(YEAR FROM c.effective_date)), 2) as total_escalation_impact
FROM contracts c
LEFT JOIN parties p ON c.counterparty_id = p.id
WHERE c.metadata->>'escalation_rate' IS NOT NULL
AND c.contract_value IS NOT NULL
ORDER BY CAST(c.metadata->>'escalation_rate' AS DECIMAL) DESC;

-- Query 6: Multi-year financial commitment
SELECT 
    c.contract_type,
    COUNT(*) as contracts,
    SUM(c.contract_value) as total_value,
    AVG(EXTRACT(DAY FROM c.expiration_date - c.effective_date) / 365.25) as avg_duration_years,
    ROUND(SUM(c.contract_value) / NULLIF(AVG(EXTRACT(DAY FROM c.expiration_date - c.effective_date) / 365.25), 0), 2) as annual_value,
    MIN(c.effective_date) as earliest_effective_date,
    MAX(c.expiration_date) as latest_expiration_date
FROM contracts c
WHERE c.status IN ('Active', 'Executed')
AND c.contract_value IS NOT NULL
AND c.effective_date IS NOT NULL
AND c.expiration_date IS NOT NULL
GROUP BY c.contract_type
ORDER BY total_value DESC;

-- Query 7: Currency exposure
SELECT 
    c.currency,
    COUNT(*) as contract_count,
    SUM(c.contract_value) as total_value,
    ROUND(SUM(c.contract_value) * 100.0 / (SELECT SUM(contract_value) FROM contracts WHERE status IN ('Active', 'Executed')), 2) as percent_of_portfolio
FROM contracts c
WHERE c.status IN ('Active', 'Executed')
AND c.currency IS NOT NULL
GROUP BY c.currency
ORDER BY total_value DESC;

-- Query 8: Top vendors by category
WITH vendor_summary AS (
    SELECT 
        p.legal_name as vendor,
        c.contract_type,
        SUM(c.contract_value) as category_spend,
        COUNT(*) as contract_count,
        ROW_NUMBER() OVER (PARTITION BY c.contract_type ORDER BY SUM(c.contract_value) DESC) as rank
    FROM contracts c
    LEFT JOIN parties p ON c.counterparty_id = p.id
    WHERE c.status IN ('Active', 'Executed')
    AND c.contract_value IS NOT NULL
    GROUP BY p.id, p.legal_name, c.contract_type
)
SELECT 
    vendor,
    contract_type,
    category_spend,
    contract_count,
    rank
FROM vendor_summary
WHERE rank <= 3
ORDER BY contract_type, rank;

-- Query 9: Financial metrics dashboard
SELECT 
    'Total Active Revenue' as metric,
    CAST(SUM(contract_value) AS VARCHAR) as value,
    'USD' as unit
FROM contracts
WHERE status IN ('Active', 'Executed')
UNION ALL
SELECT 
    'Average Contract Value',
    CAST(ROUND(AVG(contract_value), 2) AS VARCHAR),
    'USD'
FROM contracts
WHERE status IN ('Active', 'Executed')
UNION ALL
SELECT 
    'Total Contracts',
    CAST(COUNT(*) AS VARCHAR),
    'Count'
FROM contracts
WHERE status IN ('Active', 'Executed')
UNION ALL
SELECT 
    'Contracts Expiring Next 90 Days',
    CAST(COUNT(*) AS VARCHAR),
    'Count'
FROM contracts
WHERE expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '90 days'
AND status != 'Expired';

-- Query 10: Spend variance from budget
SELECT 
    DATE_TRUNC('month', c.created_at)::DATE as month,
    c.contract_type,
    SUM(c.contract_value) as actual_spend,
    COUNT(*) as contract_count
FROM contracts c
WHERE c.status IN ('Active', 'Executed')
AND c.created_at >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', c.created_at), c.contract_type
ORDER BY month DESC, actual_spend DESC;
