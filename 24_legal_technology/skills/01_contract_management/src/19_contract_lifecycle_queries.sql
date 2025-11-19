-- Contract Lifecycle Queries
-- Track contracts through their lifecycle stages

-- Query 1: Contracts by lifecycle stage
SELECT 
    c.status,
    COUNT(*) as contract_count,
    SUM(c.contract_value) as total_value,
    AVG(c.contract_value) as avg_value,
    ROUND((COUNT(*) * 100.0) / (SELECT COUNT(*) FROM contracts), 2) as percent_of_total
FROM contracts c
GROUP BY c.status
ORDER BY contract_count DESC;

-- Query 2: Contract creation and execution pipeline
SELECT 
    DATE_TRUNC('month', c.created_at)::DATE as month,
    COUNT(*) as contracts_created,
    SUM(CASE WHEN c.status = 'Draft' THEN 1 ELSE 0 END) as still_in_draft,
    SUM(CASE WHEN c.status = 'In Negotiation' THEN 1 ELSE 0 END) as in_negotiation,
    SUM(CASE WHEN c.status IN ('Executed', 'Active') THEN 1 ELSE 0 END) as executed_active,
    ROUND(AVG(EXTRACT(DAY FROM c.execution_date - c.created_at)), 2) as avg_days_to_execution
FROM contracts c
WHERE c.created_at >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', c.created_at)
ORDER BY month DESC;

-- Query 3: Contracts by age
SELECT 
    CASE 
        WHEN EXTRACT(DAY FROM CURRENT_DATE - c.effective_date) < 30 THEN 'New (0-30 days)'
        WHEN EXTRACT(DAY FROM CURRENT_DATE - c.effective_date) < 90 THEN 'Recent (30-90 days)'
        WHEN EXTRACT(DAY FROM CURRENT_DATE - c.effective_date) < 365 THEN 'Current (3-12 months)'
        WHEN EXTRACT(DAY FROM CURRENT_DATE - c.effective_date) < 730 THEN '1-2 years'
        ELSE 'Long-term (2+ years)'
    END as contract_age_category,
    COUNT(*) as contract_count,
    AVG(EXTRACT(DAY FROM CURRENT_DATE - c.effective_date)) as avg_days_active,
    SUM(c.contract_value) as total_value
FROM contracts c
WHERE c.status IN ('Active', 'Executed')
GROUP BY contract_age_category
ORDER BY contract_count DESC;

-- Query 4: Renewal candidates (60-180 days out)
SELECT 
    c.reference_number,
    c.title,
    c.contract_type,
    p.legal_name as counterparty,
    c.expiration_date,
    EXTRACT(DAY FROM c.expiration_date - CURRENT_DATE) as days_until_expiration,
    c.contract_value,
    c.metadata->>'renewal_terms' as renewal_terms,
    CASE 
        WHEN EXTRACT(DAY FROM c.expiration_date - CURRENT_DATE) < 30 THEN 'URGENT'
        WHEN EXTRACT(DAY FROM c.expiration_date - CURRENT_DATE) < 60 THEN 'HIGH'
        ELSE 'MEDIUM'
    END as priority
FROM contracts c
LEFT JOIN parties p ON c.counterparty_id = p.id
WHERE c.expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '180 days'
AND c.status != 'Expired'
ORDER BY c.expiration_date ASC;

-- Query 5: Recently executed contracts
SELECT 
    c.reference_number,
    c.title,
    c.contract_type,
    p.legal_name as counterparty,
    c.execution_date,
    EXTRACT(DAY FROM CURRENT_DATE - c.execution_date) as days_since_execution,
    c.effective_date,
    c.expiration_date,
    c.contract_value,
    c.status
FROM contracts c
LEFT JOIN parties p ON c.counterparty_id = p.id
WHERE c.execution_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY c.execution_date DESC;

-- Query 6: Contract approval workflow status
SELECT 
    c.reference_number,
    c.title,
    c.status,
    COUNT(a.id) as total_approval_steps,
    SUM(CASE WHEN a.approval_status = 'Approved' THEN 1 ELSE 0 END) as completed_approvals,
    SUM(CASE WHEN a.approval_status = 'Pending' THEN 1 ELSE 0 END) as pending_approvals,
    SUM(CASE WHEN a.approval_status = 'Rejected' THEN 1 ELSE 0 END) as rejected_approvals,
    MAX(a.created_at) as last_approval_activity,
    DATEDIFF(day, MAX(a.created_at), CURRENT_DATE) as days_in_current_step
FROM contracts c
LEFT JOIN approvals a ON c.id = a.contract_id
WHERE c.status IN ('Draft', 'In Negotiation')
GROUP BY c.id, c.reference_number, c.title, c.status
ORDER BY days_in_current_step DESC;

-- Query 7: Expired and terminated contracts
SELECT 
    c.reference_number,
    c.title,
    c.contract_type,
    p.legal_name as counterparty,
    c.expiration_date,
    EXTRACT(DAY FROM CURRENT_DATE - c.expiration_date) as days_since_expiration,
    c.status,
    c.contract_value,
    c.metadata->>'renewal_decision' as renewal_decision
FROM contracts c
LEFT JOIN parties p ON c.counterparty_id = p.id
WHERE c.status IN ('Expired', 'Terminated')
ORDER BY c.expiration_date DESC;

-- Query 8: Contract amendments and versions
SELECT 
    c.reference_number,
    c.title,
    COUNT(DISTINCT d.version) as total_versions,
    MAX(d.uploaded_at) as latest_version_date,
    c.status,
    COUNT(DISTINCT a.id) as amendment_count,
    c.metadata->>'amendment_history' as amendments
FROM contracts c
LEFT JOIN documents d ON c.id = d.contract_id
LEFT JOIN approvals a ON c.id = a.contract_id AND a.approval_status = 'Approved'
GROUP BY c.id, c.reference_number, c.title, c.status, c.metadata
ORDER BY total_versions DESC;

-- Query 9: Performance tracking by contract
SELECT 
    c.reference_number,
    c.title,
    c.status,
    c.contract_value,
    CASE 
        WHEN c.status = 'Draft' THEN 'Pre-Execution'
        WHEN c.status = 'In Negotiation' THEN 'Negotiation'
        WHEN c.status IN ('Executed', 'Active') THEN 'Active'
        WHEN c.status = 'Renewed' THEN 'Renewed'
        ELSE 'Closed'
    END as lifecycle_stage,
    ROUND(EXTRACT(DAY FROM CURRENT_DATE - c.created_at) / 365.25, 2) as years_since_creation,
    c.metadata->>'performance_score' as performance_score,
    c.metadata->>'satisfaction_rating' as satisfaction_rating
FROM contracts c
ORDER BY c.created_at DESC;

-- Query 10: Contract status transition history
WITH contract_history AS (
    SELECT 
        c.id,
        c.reference_number,
        c.title,
        c.status as current_status,
        al.action as last_action,
        al.timestamp as last_change_date,
        LAG(al.action) OVER (PARTITION BY al.contract_id ORDER BY al.timestamp) as previous_status
    FROM contracts c
    LEFT JOIN audit_log al ON c.id = al.contract_id
)
SELECT 
    reference_number,
    title,
    current_status,
    previous_status,
    last_action,
    last_change_date,
    EXTRACT(DAY FROM CURRENT_DATE - last_change_date) as days_in_current_status
FROM contract_history
WHERE last_change_date IS NOT NULL
ORDER BY reference_number, last_change_date DESC;
