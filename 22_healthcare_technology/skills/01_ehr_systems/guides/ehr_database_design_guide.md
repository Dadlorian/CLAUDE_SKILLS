# EHR Database Design Guide

## Overview

Comprehensive guide for designing relational databases for Electronic Health Record systems with focus on performance, scalability, and compliance.

## Design Principles

### 1. Data Normalization
- Use 3NF (Third Normal Form) for clinical data
- Denormalize strategically for reporting tables
- Maintain referential integrity with foreign keys

### 2. Audit Trail Requirements
- Track all data changes (who, what, when)
- Immutable audit logs
- Separate audit database for security

### 3. Performance Optimization
- Strategic indexing on frequently queried columns
- Partitioning large tables by date
- Read replicas for reporting workloads

## Core Table Schemas

### Patient Table
```sql
CREATE TABLE patient (
    patient_id BIGSERIAL PRIMARY KEY,
    medical_record_number VARCHAR(50) UNIQUE NOT NULL,
    ssn_encrypted BYTEA,

    -- Name
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,

    -- Demographics
    date_of_birth DATE NOT NULL,
    gender_code VARCHAR(10),
    race_code VARCHAR(20),
    ethnicity_code VARCHAR(20),

    -- Status
    active_status BOOLEAN DEFAULT TRUE,
    deceased_indicator BOOLEAN DEFAULT FALSE,
    date_of_death DATE,

    -- Audit
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id BIGINT,
    modified_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by_user_id BIGINT,

    -- Indexes
    CONSTRAINT fk_created_by FOREIGN KEY (created_by_user_id) REFERENCES app_user(user_id),
    CONSTRAINT fk_modified_by FOREIGN KEY (modified_by_user_id) REFERENCES app_user(user_id)
);

CREATE INDEX idx_patient_mrn ON patient(medical_record_number);
CREATE INDEX idx_patient_last_name ON patient(last_name);
CREATE INDEX idx_patient_dob ON patient(date_of_birth);
CREATE INDEX idx_patient_active ON patient(active_status) WHERE active_status = TRUE;
```

### Encounter Table (with Partitioning)
```sql
CREATE TABLE encounter (
    encounter_id BIGSERIAL,
    patient_id BIGINT NOT NULL,
    visit_number VARCHAR(50) UNIQUE NOT NULL,

    -- Classification
    encounter_class_code VARCHAR(20) NOT NULL,
    encounter_type_code VARCHAR(50),
    encounter_status_code VARCHAR(20) NOT NULL,

    -- Timing
    registration_timestamp TIMESTAMP,
    admission_timestamp TIMESTAMP,
    discharge_timestamp TIMESTAMP,

    -- Care Team
    attending_provider_id BIGINT,
    facility_id BIGINT,

    -- Audit
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (encounter_id, admission_timestamp),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (attending_provider_id) REFERENCES practitioner(provider_id)
) PARTITION BY RANGE (admission_timestamp);

-- Create yearly partitions
CREATE TABLE encounter_2023 PARTITION OF encounter
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE encounter_2024 PARTITION OF encounter
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- Indexes on partitions
CREATE INDEX idx_encounter_2024_patient ON encounter_2024(patient_id);
CREATE INDEX idx_encounter_2024_status ON encounter_2024(encounter_status_code);
```

## Best Practices

### Encryption
```sql
-- Enable pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive data
INSERT INTO patient (ssn_encrypted)
VALUES (pgp_sym_encrypt('123-45-6789', current_setting('app.encryption_key')));

-- Decrypt when needed
SELECT pgp_sym_decrypt(ssn_encrypted, current_setting('app.encryption_key'))
FROM patient WHERE patient_id = 12345;
```

### Audit Trigger
```sql
CREATE OR REPLACE FUNCTION audit_patient_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'UPDATE') THEN
        INSERT INTO patient_audit (
            patient_id,
            field_name,
            old_value,
            new_value,
            changed_by,
            changed_timestamp
        )
        SELECT
            NEW.patient_id,
            column_name,
            to_json(OLD),
            to_json(NEW),
            current_user,
            CURRENT_TIMESTAMP
        FROM information_schema.columns
        WHERE table_name = 'patient'
          AND to_json(OLD) IS DISTINCT FROM to_json(NEW);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER patient_audit_trigger
AFTER UPDATE ON patient
FOR EACH ROW
EXECUTE FUNCTION audit_patient_changes();
```

## Performance Tuning

### Query Optimization
```sql
-- Use EXPLAIN ANALYZE
EXPLAIN ANALYZE
SELECT p.*, e.*
FROM patient p
JOIN encounter e ON p.patient_id = e.patient_id
WHERE p.last_name = 'Smith'
  AND e.admission_timestamp >= '2024-01-01';

-- Create covering index
CREATE INDEX idx_patient_name_id ON patient(last_name, patient_id);

-- Materialized view for complex reports
CREATE MATERIALIZED VIEW patient_encounter_summary AS
SELECT
    p.patient_id,
    p.medical_record_number,
    COUNT(e.encounter_id) as total_encounters,
    MAX(e.admission_timestamp) as last_visit
FROM patient p
LEFT JOIN encounter e ON p.patient_id = e.patient_id
GROUP BY p.patient_id, p.medical_record_number;

-- Refresh materialized view
REFRESH MATERIALIZED VIEW CONCURRENTLY patient_encounter_summary;
```

## References
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Clinical Data Models: See clinical_data_models.md reference

---

**Document Version**: 1.0
**Last Updated**: November 2024
