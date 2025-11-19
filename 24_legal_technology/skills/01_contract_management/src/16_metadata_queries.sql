-- Metadata Extraction and Query Examples
-- Extract and query contract metadata

-- Query 1: Extract all contract metadata
SELECT 
    c.id,
    c.reference_number,
    c.title,
    c.contract_type,
    c.status,
    c.effective_date,
    c.expiration_date,
    c.contract_value,
    c.currency,
    c.payment_terms,
    p1.legal_name as primary_party,
    p2.legal_name as counterparty,
    jsonb_pretty(c.metadata) as full_metadata
FROM contracts c
LEFT JOIN parties p1 ON c.primary_party_id = p1.id
LEFT JOIN parties p2 ON c.counterparty_id = p2.id
WHERE c.status = 'Active'
ORDER BY c.created_at DESC;

-- Query 2: Extract specific metadata fields
SELECT 
    c.reference_number,
    c.title,
    c.metadata->>'parties' as parties,
    c.metadata->>'dates' as dates,
    c.metadata->>'financial_terms' as financial_terms,
    c.metadata->>'slas' as slas,
    c.metadata->>'risk_factors' as risk_factors
FROM contracts c
WHERE c.metadata IS NOT NULL;

-- Query 3: Search contracts by party name
SELECT 
    c.reference_number,
    c.title,
    p.legal_name,
    p.party_type,
    c.contract_value,
    c.effective_date,
    c.expiration_date
FROM contracts c
LEFT JOIN parties p ON c.primary_party_id = p.id OR c.counterparty_id = p.id
WHERE p.legal_name ILIKE '%Acme%'
ORDER BY c.effective_date DESC;

-- Query 4: Extract financial metadata
SELECT 
    c.reference_number,
    c.title,
    c.contract_value,
    c.currency,
    c.payment_terms,
    c.metadata->'financial'->>'escalation_rate' as escalation_rate,
    c.metadata->'financial'->>'renewal_value' as renewal_value,
    c.effective_date,
    c.expiration_date
FROM contracts c
WHERE c.contract_value IS NOT NULL
ORDER BY c.contract_value DESC;

-- Query 5: Extract and analyze SLA metadata
SELECT 
    c.reference_number,
    c.title,
    jsonb_array_elements(c.metadata->'slas') as sla_specification,
    c.metadata->>'uptime_requirement' as uptime_requirement,
    c.metadata->>'response_time_sla' as response_time,
    c.metadata->>'resolution_time_sla' as resolution_time
FROM contracts c
WHERE c.metadata->'slas' IS NOT NULL
AND jsonb_array_length(c.metadata->'slas') > 0;

-- Query 6: Get metadata for expiring contracts
SELECT 
    c.reference_number,
    c.title,
    c.expiration_date,
    EXTRACT(DAY FROM c.expiration_date - CURRENT_DATE) as days_until_expiration,
    p.legal_name as counterparty,
    p.contact_email,
    p.contact_phone,
    c.contract_value,
    c.metadata->>'renewal_terms' as renewal_terms
FROM contracts c
LEFT JOIN parties p ON c.counterparty_id = p.id
WHERE c.expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '90 days'
AND c.status != 'Expired'
ORDER BY c.expiration_date ASC;

-- Query 7: Extract compliance metadata
SELECT 
    c.reference_number,
    c.title,
    c.metadata->>'compliance_requirements' as compliance_requirements,
    c.metadata->>'data_protection' as data_protection,
    c.metadata->>'insurance_requirements' as insurance_requirements,
    c.metadata->>'regulatory_scope' as regulatory_scope
FROM contracts c
WHERE c.metadata->>'compliance_requirements' IS NOT NULL;

-- Query 8: Text search across metadata
SELECT 
    c.reference_number,
    c.title,
    c.contract_type,
    c.metadata,
    ts_rank(c.full_text_search, plainto_tsquery('english', 'liability')) as rank
FROM contracts c
WHERE c.full_text_search @@ plainto_tsquery('english', 'liability')
ORDER BY rank DESC;

-- Query 9: Aggregate metadata by contract type
SELECT 
    c.contract_type,
    COUNT(*) as contract_count,
    AVG(c.contract_value) as avg_value,
    MIN(c.contract_value) as min_value,
    MAX(c.contract_value) as max_value,
    AVG(c.risk_score) as avg_risk_score
FROM contracts c
WHERE c.status = 'Active'
GROUP BY c.contract_type
ORDER BY contract_count DESC;

-- Query 10: Extract and count defined terms
SELECT 
    c.reference_number,
    c.title,
    jsonb_object_keys(c.metadata->'defined_terms') as defined_term,
    c.metadata->'defined_terms'->jsonb_object_keys(c.metadata->'defined_terms') as definition
FROM contracts c
WHERE c.metadata->'defined_terms' IS NOT NULL;
