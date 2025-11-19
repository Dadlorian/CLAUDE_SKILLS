-- Medical Device Software Database Schema
-- Supports IEC 62304 compliance and post-market surveillance

CREATE TABLE devices (
    device_id VARCHAR(50) PRIMARY KEY,
    device_name VARCHAR(255) NOT NULL,
    software_version VARCHAR(20) NOT NULL,
    serial_number VARCHAR(50),
    manufactured_date DATE,
    customer_id VARCHAR(50),
    installation_date DATE,
    audit_trail_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Requirement: REQ-GLU-003 (Log all measurements)
-- Risk Control: RC-001 (Data integrity)
CREATE TABLE glucose_measurements (
    measurement_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    device_id VARCHAR(50) NOT NULL,
    patient_id VARCHAR(50) NOT NULL,
    glucose_value DECIMAL(5,1),
    measurement_timestamp TIMESTAMP,
    sensor_status VARCHAR(50),
    -- Audit trail per 21 CFR Part 11
    recorded_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recorded_by VARCHAR(50),
    FOREIGN KEY (device_id) REFERENCES devices(device_id),
    CHECK (glucose_value BETWEEN 0 AND 600)
);

-- Requirement: REQ-SAFE-002 (Traceability of all changes)
CREATE TABLE software_versions (
    version_id VARCHAR(20) PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL,
    version_number VARCHAR(20),
    release_date DATE,
    major_changes TEXT,
    verification_status VARCHAR(50),
    validation_status VARCHAR(50),
    approved_by VARCHAR(50),
    approval_date DATE,
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

-- Post-market surveillance requirement
-- Requirement: REQ-POST-001 (Track all complaints)
CREATE TABLE complaints (
    complaint_id VARCHAR(50) PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL,
    complaint_date DATE,
    severity VARCHAR(50),
    description TEXT,
    patient_outcome VARCHAR(255),
    investigation_status VARCHAR(50),
    root_cause TEXT,
    corrective_action TEXT,
    mdr_reported BOOLEAN,
    investigation_date DATE,
    FOREIGN KEY (device_id) REFERENCES devices(device_id),
    INDEX idx_complaint_date (complaint_date),
    INDEX idx_severity (severity)
);

-- Risk management traceability
-- Requirement: REQ-RISK-001 (Link hazards to tests)
CREATE TABLE risk_controls (
    control_id VARCHAR(50) PRIMARY KEY,
    hazard_id VARCHAR(50),
    description TEXT,
    verification_method VARCHAR(255),
    test_case_id VARCHAR(50),
    verification_date DATE,
    verified_by VARCHAR(50),
    residual_risk_score INT
);

-- Audit trail for all system activities
-- Requirement: 21 CFR Part 11 (Electronic records)
CREATE TABLE audit_log (
    log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    device_id VARCHAR(50),
    user_id VARCHAR(50),
    action VARCHAR(100),
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    session_id VARCHAR(100),
    INDEX idx_device_timestamp (device_id, timestamp),
    INDEX idx_user_timestamp (user_id, timestamp)
);

-- View for trend analysis
CREATE VIEW complaint_trends AS
SELECT 
    DATE_FORMAT(complaint_date, '%Y-%m') as month,
    severity,
    COUNT(*) as count
FROM complaints
GROUP BY month, severity
ORDER BY month DESC;

-- Verify FDA compliance
-- Check: All measurements have proper audit trail
SELECT COUNT(*) as measurements_without_audit
FROM glucose_measurements
WHERE recorded_timestamp IS NULL;

-- Verify: All complaints investigated
SELECT COUNT(*) as uninvestigated_complaints
FROM complaints
WHERE investigation_status != 'Closed';
