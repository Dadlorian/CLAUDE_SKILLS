-- Consent Management Database Schema
-- GDPR-compliant consent tracking and audit

-- Consent Records Table
CREATE TABLE consent_records (
    consent_id VARCHAR(64) PRIMARY KEY,
    user_id_hash VARCHAR(64) NOT NULL,
    consent_type VARCHAR(50) NOT NULL,
    granted BOOLEAN NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    ip_address_hash VARCHAR(64),
    user_agent TEXT,
    consent_version VARCHAR(10),
    consent_duration_days INT,
    expiration_date TIMESTAMP,
    verification_code VARCHAR(32),
    legal_basis VARCHAR(100),
    source_channel VARCHAR(50),
    explicit_confirmation BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id_hash),
    INDEX idx_consent_type (consent_type),
    INDEX idx_timestamp (timestamp),
    INDEX idx_expiration (expiration_date),
    UNIQUE KEY unique_verification (verification_code)
);

-- Consent Withdrawal Table
CREATE TABLE consent_withdrawals (
    withdrawal_id VARCHAR(64) PRIMARY KEY,
    consent_id VARCHAR(64) NOT NULL,
    user_id_hash VARCHAR(64) NOT NULL,
    withdrawal_date TIMESTAMP NOT NULL,
    withdrawal_method VARCHAR(50),
    reason TEXT,
    effective_date TIMESTAMP,
    processed_by VARCHAR(100),
    status VARCHAR(20) DEFAULT 'processed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consent_id) REFERENCES consent_records(consent_id),
    INDEX idx_user_id (user_id_hash),
    INDEX idx_withdrawal_date (withdrawal_date)
);

-- Data Subject Rights Requests Table
CREATE TABLE data_subject_requests (
    request_id VARCHAR(64) PRIMARY KEY,
    request_type VARCHAR(50) NOT NULL,  -- access, deletion, rectification, portability, objection
    subject_id_hash VARCHAR(64) NOT NULL,
    requested_date TIMESTAMP NOT NULL,
    received_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'received',
    priority_level VARCHAR(20),
    data_categories_requested TEXT,
    due_date TIMESTAMP,
    completion_date TIMESTAMP,
    response_format VARCHAR(50),
    processed_by VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_subject_id (subject_id_hash),
    INDEX idx_request_type (request_type),
    INDEX idx_status (status),
    INDEX idx_due_date (due_date)
);

-- Data Processing Activities Table
CREATE TABLE processing_activities (
    activity_id VARCHAR(64) PRIMARY KEY,
    activity_name VARCHAR(255) NOT NULL,
    purpose TEXT NOT NULL,
    legal_basis VARCHAR(100),
    data_categories TEXT,
    data_subjects TEXT,
    recipients TEXT,
    retention_period_days INT,
    retention_basis VARCHAR(255),
    special_category_data BOOLEAN DEFAULT FALSE,
    automated_decision_making BOOLEAN DEFAULT FALSE,
    created_date TIMESTAMP,
    last_updated TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    dpia_required BOOLEAN DEFAULT FALSE,
    dpia_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_activity_name (activity_name),
    INDEX idx_legal_basis (legal_basis),
    INDEX idx_status (status)
);

-- Breach Registry Table
CREATE TABLE breach_registry (
    breach_id VARCHAR(64) PRIMARY KEY,
    breach_date TIMESTAMP NOT NULL,
    discovery_date TIMESTAMP,
    notification_date TIMESTAMP,
    data_categories TEXT,
    affected_individuals INT,
    severity_level VARCHAR(20),
    risk_score DECIMAL(3, 1),
    breach_description TEXT,
    mitigation_measures TEXT,
    authority_notified BOOLEAN DEFAULT FALSE,
    authority_notification_date TIMESTAMP,
    individuals_notified BOOLEAN DEFAULT FALSE,
    notification_method VARCHAR(100),
    investigation_status VARCHAR(20),
    root_cause TEXT,
    resolution_date TIMESTAMP,
    lessons_learned TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_breach_date (breach_date),
    INDEX idx_discovery_date (discovery_date),
    INDEX idx_severity (severity_level)
);

-- Audit Trail Table
CREATE TABLE audit_trail (
    event_id VARCHAR(64) PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    user_id_hash VARCHAR(64),
    resource_id VARCHAR(100),
    action VARCHAR(100),
    description TEXT,
    data_elements_affected TEXT,
    ip_address_hash VARCHAR(64),
    user_agent TEXT,
    previous_hash VARCHAR(64),
    entry_hash VARCHAR(64),
    status VARCHAR(20) DEFAULT 'recorded',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp),
    INDEX idx_event_type (event_type),
    INDEX idx_user_id (user_id_hash),
    INDEX idx_resource_id (resource_id),
    UNIQUE KEY unique_entry_hash (entry_hash)
);

-- Vendor Agreements Table
CREATE TABLE vendor_agreements (
    dpa_id VARCHAR(64) PRIMARY KEY,
    vendor_name VARCHAR(255) NOT NULL,
    processing_purpose TEXT,
    data_categories TEXT,
    data_subjects TEXT,
    signing_date TIMESTAMP,
    effective_date TIMESTAMP,
    termination_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    sub_processors TEXT,
    audit_rights_included BOOLEAN DEFAULT TRUE,
    last_audit_date TIMESTAMP,
    next_audit_date TIMESTAMP,
    compliance_status VARCHAR(20) DEFAULT 'compliant',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_vendor_name (vendor_name),
    INDEX idx_status (status),
    INDEX idx_next_audit (next_audit_date)
);

-- Training Records Table
CREATE TABLE training_records (
    training_id VARCHAR(64) PRIMARY KEY,
    employee_id VARCHAR(64) NOT NULL,
    training_type VARCHAR(100),
    training_name VARCHAR(255),
    completion_date TIMESTAMP,
    score INT,
    passed BOOLEAN,
    certificate_issued BOOLEAN DEFAULT FALSE,
    renewal_date TIMESTAMP,
    duration_minutes INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_employee_id (employee_id),
    INDEX idx_completion_date (completion_date),
    INDEX idx_renewal_date (renewal_date)
);

-- Compliance Reporting Table
CREATE TABLE compliance_reports (
    report_id VARCHAR(64) PRIMARY KEY,
    report_type VARCHAR(100),  -- annual, quarterly, incident, audit
    report_name VARCHAR(255),
    generated_date TIMESTAMP,
    reporting_period_start DATE,
    reporting_period_end DATE,
    content TEXT,
    file_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'draft',
    approver_name VARCHAR(100),
    approval_date TIMESTAMP,
    distributed_to TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_report_type (report_type),
    INDEX idx_generated_date (generated_date),
    INDEX idx_status (status)
);

-- Regulatory Change Log Table
CREATE TABLE regulatory_changes (
    change_id VARCHAR(64) PRIMARY KEY,
    regulation_name VARCHAR(255),
    jurisdiction VARCHAR(100),
    change_type VARCHAR(50),
    effective_date DATE,
    description TEXT,
    impact_assessment TEXT,
    action_items TEXT,
    status VARCHAR(20) DEFAULT 'identified',
    implementation_deadline DATE,
    created_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_jurisdiction (jurisdiction),
    INDEX idx_effective_date (effective_date),
    INDEX idx_implementation_deadline (implementation_deadline)
);

-- Useful Views

-- Active Consent View
CREATE VIEW active_consents AS
SELECT cr.*, 'active' as consent_status
FROM consent_records cr
LEFT JOIN consent_withdrawals cw ON cr.consent_id = cw.consent_id
WHERE cw.withdrawal_id IS NULL
AND cr.expiration_date > CURRENT_TIMESTAMP;

-- Overdue Data Subject Requests
CREATE VIEW overdue_requests AS
SELECT *
FROM data_subject_requests
WHERE status NOT IN ('completed', 'rejected')
AND due_date < CURRENT_TIMESTAMP;

-- Compliance Dashboard Summary
CREATE VIEW compliance_summary AS
SELECT
    'Total Active Consents' as metric,
    COUNT(*) as value
FROM active_consents
UNION ALL
SELECT
    'Pending Data Subject Requests',
    COUNT(*)
FROM data_subject_requests
WHERE status NOT IN ('completed', 'rejected')
UNION ALL
SELECT
    'Overdue Training Completions',
    COUNT(*)
FROM training_records
WHERE renewal_date < CURRENT_TIMESTAMP
UNION ALL
SELECT
    'Unresolved Breaches',
    COUNT(*)
FROM breach_registry
WHERE resolution_date IS NULL;

-- Audit Trail Integrity Check
CREATE VIEW audit_trail_integrity AS
SELECT
    event_id,
    timestamp,
    event_type,
    CASE
        WHEN entry_hash IS NOT NULL THEN 'verified'
        ELSE 'unverified'
    END as integrity_status
FROM audit_trail;

-- Useful Queries

-- Consent Expiration Alert (30-day window)
-- SELECT * FROM consent_records
-- WHERE expiration_date BETWEEN CURRENT_TIMESTAMP AND DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 30 DAY)
-- ORDER BY expiration_date;

-- Data Retention Compliance Check
-- SELECT DISTINCT
--     pa.activity_id,
--     pa.activity_name,
--     pa.retention_period_days,
--     COUNT(DISTINCT dsr.subject_id_hash) as active_records
-- FROM processing_activities pa
-- LEFT JOIN data_subject_requests dsr ON pa.activity_id = dsr.request_id
-- WHERE pa.retention_period_days > 730;  -- Flag if > 2 years

-- Vendor Compliance Status
-- SELECT
--     dpa_id,
--     vendor_name,
--     status,
--     compliance_status,
--     DATEDIFF(next_audit_date, CURRENT_DATE) as days_to_next_audit
-- FROM vendor_agreements
-- WHERE status = 'active'
-- ORDER BY next_audit_date;

-- PII Data Access Audit
-- SELECT
--     event_id,
--     timestamp,
--     user_id_hash,
--     resource_id,
--     data_elements_affected,
--     ip_address_hash
-- FROM audit_trail
-- WHERE event_type = 'data_access'
-- AND data_elements_affected LIKE '%PII%'
-- AND timestamp > DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 30 DAY);
