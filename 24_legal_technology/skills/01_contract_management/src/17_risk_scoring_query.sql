-- Risk Scoring Queries
-- Calculate and analyze contract risk scores

-- Query 1: Get all contracts with risk scores
SELECT 
    c.id,
    c.reference_number,
    c.title,
    c.contract_type,
    c.risk_score,
    c.risk_level,
    CASE 
        WHEN c.risk_score < 2 THEN 'GREEN'
        WHEN c.risk_score < 3 THEN 'YELLOW'
        WHEN c.risk_score < 4 THEN 'ORANGE'
        ELSE 'RED'
    END as risk_color,
    p.legal_name as counterparty,
    c.created_at
FROM contracts c
LEFT JOIN parties p ON c.counterparty_id = p.id
ORDER BY c.risk_score DESC;

-- Query 2: Get high-risk contracts requiring attention
SELECT 
    c.reference_number,
    c.title,
    c.contract_type,
    c.risk_score,
    c.risk_level,
    p.legal_name as counterparty,
    c.effective_date,
    c.expiration_date,
    CASE 
        WHEN c.risk_score >= 4 THEN 'Immediate Review Required'
        WHEN c.risk_score >= 3.5 THEN 'Executive Review Required'
        ELSE 'Monitoring Required'
    END as action_required
FROM contracts c
LEFT JOIN parties p ON c.counterparty_id = p.id
WHERE c.risk_score >= 3
ORDER BY c.risk_score DESC;

-- Query 3: Risk analysis by contract type
SELECT 
    c.contract_type,
    COUNT(*) as total_contracts,
    AVG(c.risk_score) as avg_risk_score,
    MAX(c.risk_score) as max_risk_score,
    MIN(c.risk_score) as min_risk_score,
    SUM(CASE WHEN c.risk_level = 'Critical' THEN 1 ELSE 0 END) as critical_count,
    SUM(CASE WHEN c.risk_level = 'High' THEN 1 ELSE 0 END) as high_count,
    SUM(CASE WHEN c.risk_level = 'Moderate' THEN 1 ELSE 0 END) as moderate_count,
    SUM(CASE WHEN c.risk_level = 'Low' THEN 1 ELSE 0 END) as low_count
FROM contracts c
WHERE c.status != 'Expired'
GROUP BY c.contract_type
ORDER BY avg_risk_score DESC;

-- Query 4: Get clause-level risk factors
SELECT 
    c.reference_number,
    c.title,
    cl.clause_type,
    cl.title as clause_title,
    cl.risk_score as clause_risk_score,
    c.risk_score as contract_risk_score,
    ROUND(((cl.risk_score / NULLIF(c.risk_score, 0)) * 100), 2) as clause_contribution_percent
FROM contracts c
JOIN clauses cl ON c.id = cl.contract_id
WHERE cl.risk_score > 0
ORDER BY cl.risk_score DESC;

-- Query 5: Identify risk trends over time
SELECT 
    DATE_TRUNC('month', c.created_at)::DATE as month,
    c.contract_type,
    COUNT(*) as contracts_created,
    AVG(c.risk_score) as avg_risk_score,
    MAX(c.risk_score) as max_risk_score,
    SUM(CASE WHEN c.risk_level = 'Critical' THEN 1 ELSE 0 END) as critical_new_contracts
FROM contracts c
WHERE c.created_at >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', c.created_at), c.contract_type
ORDER BY month DESC, avg_risk_score DESC;

-- Query 6: Risk by party and contract type
SELECT 
    p.legal_name as counterparty,
    c.contract_type,
    COUNT(*) as contract_count,
    AVG(c.risk_score) as avg_risk_score,
    MAX(c.risk_score) as highest_risk,
    SUM(CASE WHEN c.risk_level IN ('High', 'Critical') THEN 1 ELSE 0 END) as high_risk_contracts
FROM contracts c
LEFT JOIN parties p ON c.counterparty_id = p.id
WHERE c.status != 'Expired'
GROUP BY p.legal_name, c.contract_type
HAVING AVG(c.risk_score) > 2.5
ORDER BY avg_risk_score DESC;

-- Query 7: Risk vs Contract Value analysis
SELECT 
    c.reference_number,
    c.title,
    c.contract_value,
    c.risk_score,
    CASE 
        WHEN c.contract_value > 1000000 AND c.risk_score > 3 THEN 'HIGH VALUE + HIGH RISK'
        WHEN c.contract_value > 1000000 THEN 'HIGH VALUE'
        WHEN c.risk_score > 3 THEN 'HIGH RISK'
        ELSE 'STANDARD'
    END as priority_classification,
    ROUND((c.contract_value * (c.risk_score / 5)), 2) as risk_weighted_value
FROM contracts c
WHERE c.status = 'Active'
ORDER BY risk_weighted_value DESC;

-- Query 8: Risk scorecard
SELECT 
    CURRENT_DATE as report_date,
    COUNT(*) as total_active_contracts,
    ROUND(AVG(c.risk_score), 2) as portfolio_avg_risk,
    MAX(c.risk_score) as max_risk_score,
    SUM(CASE WHEN c.risk_level = 'Critical' THEN 1 ELSE 0 END) as critical_count,
    SUM(CASE WHEN c.risk_level = 'High' THEN 1 ELSE 0 END) as high_count,
    SUM(CASE WHEN c.risk_level = 'Moderate' THEN 1 ELSE 0 END) as moderate_count,
    SUM(CASE WHEN c.risk_level = 'Low' THEN 1 ELSE 0 END) as low_count,
    ROUND((SUM(CASE WHEN c.risk_level = 'Critical' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as critical_percentage
FROM contracts c
WHERE c.status IN ('Active', 'Executed');

-- Query 9: Pending approvals with risk
SELECT 
    c.reference_number,
    c.title,
    c.risk_score,
    c.risk_level,
    a.approver_role,
    a.approval_status,
    DATEDIFF(day, a.created_at, CURRENT_DATE) as days_pending
FROM contracts c
JOIN approvals a ON c.id = a.contract_id
WHERE a.approval_status = 'Pending'
AND c.risk_score > 2
ORDER BY DATEDIFF(day, a.created_at, CURRENT_DATE) DESC;

-- Query 10: Risk mitigation recommendations
SELECT 
    c.reference_number,
    c.title,
    c.risk_score,
    string_agg(DISTINCT cl.clause_type, ', ') as high_risk_clause_types,
    CASE 
        WHEN c.risk_score >= 4 AND c.contract_value > 500000 THEN 'Request legal review and renegotiation'
        WHEN c.risk_score >= 3.5 THEN 'Review high-risk clauses'
        WHEN c.risk_score >= 3 THEN 'Monitor and document risks'
        ELSE 'Standard monitoring'
    END as recommended_action
FROM contracts c
LEFT JOIN clauses cl ON c.id = cl.contract_id AND cl.risk_score > 2
WHERE c.status IN ('Active', 'In Negotiation')
GROUP BY c.id, c.reference_number, c.title, c.risk_score, c.contract_value
ORDER BY c.risk_score DESC;
