-- Compliance Reporting Queries
-- Monitor contract compliance and regulatory requirements

-- Query 1: Compliance status overview
SELECT 
    c.reference_number,
    c.title,
    c.contract_type,
    p.legal_name as counterparty,
    c.metadata->>'compliance_requirements' as compliance_requirements,
    c.metadata->>'regulatory_scope' as regulatory_scope,
    c.metadata->>'compliance_status' as compliance_status,
    c.effective_date,
    c.expiration_date
FROM contracts c
LEFT JOIN parties p ON c.counterparty_id = p.id
WHERE c.metadata->>'compliance_requirements' IS NOT NULL
ORDER BY c.reference_number;

-- Query 2: Insurance and coverage verification
SELECT 
    c.reference_number,
    c.title,
    p.legal_name as counterparty,
    c.metadata->>'insurance_requirements' as required_insurance,
    c.metadata->>'insurance_verified' as insurance_verified,
    c.metadata->>'insurance_verification_date' as verification_date,
    c.metadata->>'insurance_expiration' as insurance_expiration,
    CASE 
        WHEN c.metadata->>'insurance_verified' = 'true' THEN 'Compliant'
        ELSE 'Not Verified'
    END as insurance_status
FROM contracts c
LEFT JOIN parties p ON c.counterparty_id = p.id
WHERE c.metadata->>'insurance_requirements' IS NOT NULL
ORDER BY c.reference_number;

-- Query 3: Data protection and privacy compliance
SELECT 
    c.reference_number,
    c.title,
    c.contract_type,
    p.legal_name as counterparty,
    c.metadata->>'data_protection_standard' as data_protection_standard,
    c.metadata->>'gdpr_compliant' as gdpr_compliant,
    c.metadata->>'ccpa_compliant' as ccpa_compliant,
    c.metadata->>'data_residency' as data_residency,
    c.metadata->>'encryption_required' as encryption_required,
    c.status
FROM contracts c
LEFT JOIN parties p ON c.counterparty_id = p.id
WHERE c.metadata->>'data_protection_standard' IS NOT NULL
ORDER BY c.reference_number;

-- Query 4: Regulatory scope and jurisdiction
SELECT 
    c.reference_number,
    c.title,
    c.metadata->>'governing_law' as governing_law,
    c.metadata->>'jurisdiction' as jurisdiction,
    c.metadata->>'regulatory_scope' as regulatory_scope,
    jsonb_array_elements(c.metadata->'regulatory_requirements') as regulatory_requirement,
    c.status
FROM contracts c
WHERE c.metadata->'regulatory_requirements' IS NOT NULL
AND jsonb_array_length(c.metadata->'regulatory_requirements') > 0;

-- Query 5: Compliance audit trail
SELECT 
    c.reference_number,
    c.title,
    al.action as compliance_action,
    al.timestamp as action_date,
    al.changes as changes,
    EXTRACT(DAY FROM CURRENT_DATE - al.timestamp) as days_since_action
FROM contracts c
JOIN audit_log al ON c.id = al.contract_id
WHERE al.action IN ('Compliance Review', 'Insurance Verified', 'Audit Completed')
OR al.changes::TEXT LIKE '%compliance%'
ORDER BY al.timestamp DESC;

-- Query 6: Compliance requirements checklist
SELECT 
    c.reference_number,
    c.title,
    c.contract_type,
    COUNT(*) as total_requirements,
    SUM(CASE WHEN al.action = 'Compliance Verified' THEN 1 ELSE 0 END) as verified_requirements,
    ROUND((SUM(CASE WHEN al.action = 'Compliance Verified' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as percent_complete
FROM contracts c
LEFT JOIN audit_log al ON c.id = al.contract_id
WHERE c.metadata->>'compliance_requirements' IS NOT NULL
GROUP BY c.id, c.reference_number, c.title, c.contract_type
ORDER BY percent_complete ASC;

-- Query 7: Non-compliant contracts
SELECT 
    c.reference_number,
    c.title,
    c.contract_type,
    p.legal_name as counterparty,
    c.metadata->>'compliance_issues' as compliance_issues,
    c.metadata->>'remediation_required' as remediation_required,
    c.metadata->>'remediation_deadline' as remediation_deadline,
    c.status
FROM contracts c
LEFT JOIN parties p ON c.counterparty_id = p.id
WHERE c.metadata->>'compliance_status' = 'Non-Compliant'
OR c.metadata->>'remediation_required' = 'true'
ORDER BY CAST(c.metadata->>'remediation_deadline' AS DATE) ASC;

-- Query 8: Compliance metrics dashboard
SELECT 
    'Total Contracts with Compliance Requirements' as metric,
    COUNT(*)::VARCHAR as value
FROM contracts
WHERE metadata->>'compliance_requirements' IS NOT NULL
UNION ALL
SELECT 
    'Contracts with Verified Insurance',
    COUNT(*)::VARCHAR
FROM contracts
WHERE metadata->>'insurance_verified' = 'true'
UNION ALL
SELECT 
    'GDPR Compliant Contracts',
    COUNT(*)::VARCHAR
FROM contracts
WHERE metadata->>'gdpr_compliant' = 'true'
UNION ALL
SELECT 
    'Non-Compliant Requiring Remediation',
    COUNT(*)::VARCHAR
FROM contracts
WHERE metadata->>'remediation_required' = 'true';

-- Query 9: Upcoming compliance deadlines
SELECT 
    c.reference_number,
    c.title,
    c.contract_type,
    p.legal_name as counterparty,
    CAST(c.metadata->>'next_compliance_review' AS DATE) as next_review_date,
    CAST(c.metadata->>'insurance_renewal_date' AS DATE) as insurance_renewal_date,
    CAST(c.metadata->>'compliance_certification_expiry' AS DATE) as certification_expiry,
    LEAST(
        CAST(c.metadata->>'next_compliance_review' AS DATE),
        CAST(c.metadata->>'insurance_renewal_date' AS DATE),
        CAST(c.metadata->>'compliance_certification_expiry' AS DATE)
    ) as earliest_deadline,
    EXTRACT(DAY FROM LEAST(
        CAST(c.metadata->>'next_compliance_review' AS DATE),
        CAST(c.metadata->>'insurance_renewal_date' AS DATE),
        CAST(c.metadata->>'compliance_certification_expiry' AS DATE)
    ) - CURRENT_DATE) as days_until_deadline
FROM contracts c
LEFT JOIN parties p ON c.counterparty_id = p.id
WHERE c.status IN ('Active', 'Executed')
ORDER BY earliest_deadline ASC;

-- Query 10: Compliance by contract type
SELECT 
    c.contract_type,
    COUNT(*) as total_contracts,
    SUM(CASE WHEN c.metadata->>'compliance_status' = 'Compliant' THEN 1 ELSE 0 END) as compliant_contracts,
    SUM(CASE WHEN c.metadata->>'compliance_status' = 'Non-Compliant' THEN 1 ELSE 0 END) as non_compliant_contracts,
    SUM(CASE WHEN c.metadata->>'compliance_status' IS NULL THEN 1 ELSE 0 END) as unreviewed_contracts,
    ROUND((SUM(CASE WHEN c.metadata->>'compliance_status' = 'Compliant' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as compliance_rate
FROM contracts c
WHERE c.status IN ('Active', 'Executed')
GROUP BY c.contract_type
ORDER BY compliance_rate DESC;
