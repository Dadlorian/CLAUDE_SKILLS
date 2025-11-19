-- HIPAA-Compliant Audit Log Database Schema
-- Designed for tamper-resistance and 6-year retention requirement

-- Main audit log table (append-only)
CREATE TABLE audit_logs (
    audit_id BIGSERIAL PRIMARY KEY,
    
    -- Required HIPAA elements
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    user_role VARCHAR(100),
    
    -- Action details
    action VARCHAR(50) NOT NULL,  -- VIEW, CREATE, UPDATE, DELETE, EXPORT, PRINT
    resource_type VARCHAR(100) NOT NULL,  -- PATIENT_RECORD, LAB_RESULT, MEDICATION, etc.
    resource_id VARCHAR(255),  -- Patient ID, Record ID, etc.
    
    -- Result
    status_code INTEGER,
    result VARCHAR(20) NOT NULL,  -- SUCCESS, FAILURE, DENIED
    error_message TEXT,
    
    -- Source information
    ip_address INET NOT NULL,
    workstation_id VARCHAR(255),
    user_agent TEXT,
    session_id VARCHAR(255),
    
    -- Request details (sanitized - no actual PHI)
    request_method VARCHAR(10),  -- GET, POST, PUT, DELETE
    request_path TEXT,
    query_parameters JSONB,  -- Sanitized parameters
    
    -- Performance
    duration_ms INTEGER,
    
    -- Integrity
    hash VARCHAR(64) NOT NULL,  -- SHA-256 hash for tamper detection
    previous_hash VARCHAR(64),  -- Chain to previous entry
    
    -- Metadata
    application VARCHAR(100),
    version VARCHAR(50),
    
    CONSTRAINT chk_result CHECK (result IN ('SUCCESS', 'FAILURE', 'DENIED')),
    CONSTRAINT chk_action CHECK (action IN ('VIEW', 'CREATE', 'UPDATE', 'DELETE', 
                                             'EXPORT', 'PRINT', 'LOGIN', 'LOGOUT', 
                                             'ACCESS_DENIED', 'CONFIGURATION_CHANGE'))
);

-- Indexes for performance (audit logs can grow very large)
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_result ON audit_logs(result);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- Separate table for PHI access (specific patient record access)
CREATE TABLE phi_access_log (
    access_id BIGSERIAL PRIMARY KEY,
    audit_id BIGINT REFERENCES audit_logs(audit_id),
    
    -- Patient identification
    patient_id VARCHAR(255) NOT NULL,
    patient_mrn VARCHAR(100),
    
    -- Specific PHI accessed
    phi_type VARCHAR(100),  -- DEMOGRAPHICS, DIAGNOSIS, MEDICATIONS, LAB_RESULTS, etc.
    phi_fields TEXT[],  -- Array of specific fields accessed
    
    -- Access justification
    access_reason VARCHAR(255),  -- TREATMENT, BILLING, RESEARCH, etc.
    access_context VARCHAR(255),  -- Additional context
    
    -- Break-glass access
    emergency_access BOOLEAN DEFAULT FALSE,
    emergency_justification TEXT,
    
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_phi_access_patient ON phi_access_log(patient_id);
CREATE INDEX idx_phi_access_timestamp ON phi_access_log(timestamp DESC);
CREATE INDEX idx_phi_access_emergency ON phi_access_log(emergency_access) WHERE emergency_access = TRUE;

-- Administrative actions log
CREATE TABLE admin_actions_log (
    action_id BIGSERIAL PRIMARY KEY,
    audit_id BIGINT REFERENCES audit_logs(audit_id),
    
    -- Admin action details
    admin_user_id VARCHAR(255) NOT NULL,
    action_type VARCHAR(100) NOT NULL,  -- PERMISSION_CHANGE, USER_CREATE, CONFIG_CHANGE, etc.
    target_user_id VARCHAR(255),  -- If action affects another user
    
    -- Changes made
    object_type VARCHAR(100),  -- USER, ROLE, POLICY, SYSTEM_CONFIG, etc.
    object_id VARCHAR(255),
    changes JSONB,  -- Before/after values
    
    -- Justification
    justification TEXT,
    approved_by VARCHAR(255),
    
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admin_actions_admin_user ON admin_actions_log(admin_user_id);
CREATE INDEX idx_admin_actions_target ON admin_actions_log(target_user_id);
CREATE INDEX idx_admin_actions_timestamp ON admin_actions_log(timestamp DESC);

-- Security incidents log
CREATE TABLE security_incidents (
    incident_id BIGSERIAL PRIMARY KEY,
    
    -- Incident classification
    incident_type VARCHAR(100) NOT NULL,  -- UNAUTHORIZED_ACCESS, BREACH, MALWARE, etc.
    severity VARCHAR(20) NOT NULL,  -- LOW, MEDIUM, HIGH, CRITICAL
    status VARCHAR(50) NOT NULL DEFAULT 'OPEN',  -- OPEN, INVESTIGATING, RESOLVED, CLOSED
    
    -- Discovery
    discovered_at TIMESTAMP WITH TIME ZONE NOT NULL,
    discovered_by VARCHAR(255) NOT NULL,
    detection_method VARCHAR(100),  -- AUDIT_REVIEW, AUTOMATED_ALERT, USER_REPORT, etc.
    
    -- Description
    description TEXT NOT NULL,
    affected_systems TEXT[],
    affected_users TEXT[],
    affected_patients TEXT[],
    
    -- PHI involved
    phi_involved BOOLEAN NOT NULL DEFAULT FALSE,
    phi_types TEXT[],
    estimated_records_affected INTEGER,
    
    -- Response
    response_actions TEXT[],
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    
    -- Breach assessment
    breach_assessment_completed BOOLEAN DEFAULT FALSE,
    breach_confirmed BOOLEAN,
    breach_notification_required BOOLEAN,
    notification_date TIMESTAMP WITH TIME ZONE,
    
    -- Root cause
    root_cause TEXT,
    corrective_actions TEXT[],
    
    -- Assignment
    assigned_to VARCHAR(255),
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_severity CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    CONSTRAINT chk_status CHECK (status IN ('OPEN', 'INVESTIGATING', 'RESOLVED', 'CLOSED'))
);

CREATE INDEX idx_security_incidents_status ON security_incidents(status);
CREATE INDEX idx_security_incidents_severity ON security_incidents(severity);
CREATE INDEX idx_security_incidents_discovered ON security_incidents(discovered_at DESC);

-- Audit log review tracking
CREATE TABLE audit_log_reviews (
    review_id BIGSERIAL PRIMARY KEY,
    
    -- Review details
    reviewed_by VARCHAR(255) NOT NULL,
    review_start_date DATE NOT NULL,
    review_end_date DATE NOT NULL,
    review_completed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Scope
    logs_reviewed_count INTEGER,
    
    -- Findings
    anomalies_found INTEGER DEFAULT 0,
    incidents_created INTEGER DEFAULT 0,
    notes TEXT,
    
    -- Follow-up
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_notes TEXT
);

CREATE INDEX idx_audit_reviews_date ON audit_log_reviews(review_completed_at DESC);

-- Tamper detection function
CREATE OR REPLACE FUNCTION verify_audit_chain()
RETURNS TABLE(audit_id BIGINT, is_valid BOOLEAN, error_message TEXT) AS $$
BEGIN
    RETURN QUERY
    WITH chain AS (
        SELECT 
            a1.audit_id,
            a1.hash,
            a1.previous_hash,
            LAG(a1.hash) OVER (ORDER BY a1.audit_id) as expected_previous_hash
        FROM audit_logs a1
    )
    SELECT 
        c.audit_id,
        CASE 
            WHEN c.audit_id = 1 THEN TRUE  -- First entry has no previous
            WHEN c.previous_hash = c.expected_previous_hash THEN TRUE
            ELSE FALSE
        END as is_valid,
        CASE
            WHEN c.audit_id = 1 THEN 'First entry'::TEXT
            WHEN c.previous_hash = c.expected_previous_hash THEN 'Valid'::TEXT
            ELSE 'Hash chain broken - possible tampering'::TEXT
        END as error_message
    FROM chain c
    WHERE c.previous_hash != c.expected_previous_hash OR c.audit_id = 1
    ORDER BY c.audit_id;
END;
$$ LANGUAGE plpgsql;

-- Prevent updates/deletes on audit logs (enforce append-only)
CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit logs are immutable. Modifications not allowed.';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_audit_update
    BEFORE UPDATE ON audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION prevent_audit_modification();

CREATE TRIGGER prevent_audit_delete
    BEFORE DELETE ON audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION prevent_audit_modification();

-- Partition by month for performance (PostgreSQL 10+)
-- This example shows quarterly partitioning, adjust as needed
CREATE TABLE audit_logs_2024_q1 PARTITION OF audit_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE audit_logs_2024_q2 PARTITION OF audit_logs
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- Add more partitions as needed

-- Retention policy enforcement (archive logs older than 6 years to archive table)
CREATE TABLE audit_logs_archive (
    LIKE audit_logs INCLUDING ALL
);

-- Grant appropriate permissions (principle of least privilege)
-- GRANT SELECT ON audit_logs TO audit_review_role;
-- GRANT INSERT ON audit_logs TO application_role;
-- REVOKE UPDATE, DELETE ON audit_logs FROM ALL;

-- Comments for documentation
COMMENT ON TABLE audit_logs IS 'HIPAA-compliant audit log. Append-only, tamper-resistant. Retains 6+ years per 45 CFR §164.316(b)(2)(i)';
COMMENT ON COLUMN audit_logs.hash IS 'SHA-256 hash of audit entry for integrity verification';
COMMENT ON COLUMN audit_logs.previous_hash IS 'Hash of previous entry creating tamper-evident chain';
