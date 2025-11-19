/*
 * Comprehensive EHR Database Schema
 * Production-grade schema for patient demographics, encounters, and clinical data
 * Database: PostgreSQL 14+
 */

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- PATIENT DOMAIN
-- ============================================================================

CREATE TABLE patient (
    patient_id BIGSERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    medical_record_number VARCHAR(50) UNIQUE NOT NULL,

    -- Name
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    suffix VARCHAR(20),
    prefix VARCHAR(20),

    -- Demographics
    date_of_birth DATE NOT NULL,
    gender_code VARCHAR(10),
    sex_at_birth VARCHAR(10),
    marital_status_code VARCHAR(10),
    race_code VARCHAR(20),
    ethnicity_code VARCHAR(20),

    -- Sensitive data (encrypted)
    ssn_encrypted BYTEA,

    -- Status flags
    active_status BOOLEAN DEFAULT TRUE NOT NULL,
    deceased_indicator BOOLEAN DEFAULT FALSE,
    date_of_death DATE,
    vip_indicator BOOLEAN DEFAULT FALSE,
    restricted_access BOOLEAN DEFAULT FALSE,

    -- Communication
    primary_language_code VARCHAR(10),
    interpreter_required BOOLEAN DEFAULT FALSE,

    -- Audit fields
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_user_id BIGINT,
    modified_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    modified_by_user_id BIGINT,

    CONSTRAINT chk_dob_valid CHECK (date_of_birth <= CURRENT_DATE),
    CONSTRAINT chk_death_after_birth CHECK (date_of_death IS NULL OR date_of_death >= date_of_birth)
);

-- Indexes for patient table
CREATE INDEX idx_patient_mrn ON patient(medical_record_number);
CREATE INDEX idx_patient_last_name ON patient(last_name);
CREATE INDEX idx_patient_first_name ON patient(first_name);
CREATE INDEX idx_patient_dob ON patient(date_of_birth);
CREATE INDEX idx_patient_active ON patient(active_status) WHERE active_status = TRUE;
CREATE INDEX idx_patient_created ON patient(created_timestamp);

-- Patient identifiers (multiple IDs per patient)
CREATE TABLE patient_identifier (
    identifier_id BIGSERIAL PRIMARY KEY,
    patient_id BIGINT NOT NULL REFERENCES patient(patient_id),
    identifier_type_code VARCHAR(20) NOT NULL,
    identifier_value VARCHAR(100) NOT NULL,
    assigning_authority VARCHAR(100),
    effective_date DATE,
    expiration_date DATE,
    active_indicator BOOLEAN DEFAULT TRUE,

    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (patient_id, identifier_type_code, assigning_authority)
);

CREATE INDEX idx_patient_identifier_value ON patient_identifier(identifier_value);
CREATE INDEX idx_patient_identifier_patient ON patient_identifier(patient_id);

-- Patient addresses
CREATE TABLE patient_address (
    address_id BIGSERIAL PRIMARY KEY,
    patient_id BIGINT NOT NULL REFERENCES patient(patient_id),
    address_type_code VARCHAR(10),
    use_code VARCHAR(10),

    street_line_1 VARCHAR(200),
    street_line_2 VARCHAR(200),
    city VARCHAR(100),
    county VARCHAR(100),
    state_code VARCHAR(10),
    postal_code VARCHAR(20),
    country_code VARCHAR(10),

    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    effective_date DATE,
    expiration_date DATE,
    active_indicator BOOLEAN DEFAULT TRUE,

    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patient_address_patient ON patient_address(patient_id);
CREATE INDEX idx_patient_address_postal ON patient_address(postal_code);

-- ============================================================================
-- ENCOUNTER DOMAIN
-- ============================================================================

CREATE TABLE encounter (
    encounter_id BIGSERIAL NOT NULL,
    patient_id BIGINT NOT NULL REFERENCES patient(patient_id),
    visit_number VARCHAR(50) UNIQUE NOT NULL,
    account_number VARCHAR(50),

    -- Classification
    encounter_class_code VARCHAR(20) NOT NULL,
    encounter_type_code VARCHAR(50),
    encounter_status_code VARCHAR(20) NOT NULL,

    -- Timing
    registration_timestamp TIMESTAMP,
    admission_timestamp TIMESTAMP NOT NULL,
    discharge_timestamp TIMESTAMP,

    -- Care team
    attending_provider_id BIGINT,
    admitting_provider_id BIGINT,
    referring_provider_id BIGINT,

    -- Location
    facility_id BIGINT,
    department_id BIGINT,
    room_number VARCHAR(20),
    bed_number VARCHAR(20),

    -- Discharge
    discharge_disposition_code VARCHAR(20),

    -- Audit
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_user_id BIGINT,
    modified_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    PRIMARY KEY (encounter_id, admission_timestamp),
    CONSTRAINT chk_discharge_after_admission CHECK (
        discharge_timestamp IS NULL OR discharge_timestamp >= admission_timestamp
    )
) PARTITION BY RANGE (admission_timestamp);

-- Create partitions for encounters (yearly)
CREATE TABLE encounter_2023 PARTITION OF encounter
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE encounter_2024 PARTITION OF encounter
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE encounter_2025 PARTITION OF encounter
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Indexes on encounter partitions
CREATE INDEX idx_encounter_2024_patient ON encounter_2024(patient_id);
CREATE INDEX idx_encounter_2024_status ON encounter_2024(encounter_status_code);
CREATE INDEX idx_encounter_2024_visit ON encounter_2024(visit_number);

-- ============================================================================
-- ALLERGY DOMAIN
-- ============================================================================

CREATE TABLE allergy (
    allergy_id BIGSERIAL PRIMARY KEY,
    patient_id BIGINT NOT NULL REFERENCES patient(patient_id),

    allergen_type_code VARCHAR(20),
    allergen_code VARCHAR(50),
    allergen_name VARCHAR(500) NOT NULL,
    allergen_class VARCHAR(200),

    allergy_status_code VARCHAR(20) NOT NULL,
    verification_status_code VARCHAR(20),

    severity_code VARCHAR(20),
    criticality_code VARCHAR(20),

    reaction_description TEXT,

    onset_date DATE,
    recorded_date DATE NOT NULL,
    recorded_by BIGINT,

    clinical_notes TEXT,

    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    modified_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT chk_recorded_after_onset CHECK (
        onset_date IS NULL OR recorded_date >= onset_date
    )
);

CREATE INDEX idx_allergy_patient ON allergy(patient_id);
CREATE INDEX idx_allergy_status ON allergy(allergy_status_code);

-- ============================================================================
-- MEDICATION DOMAIN
-- ============================================================================

CREATE TABLE medication_order (
    order_id BIGSERIAL PRIMARY KEY,
    patient_id BIGINT NOT NULL REFERENCES patient(patient_id),
    encounter_id BIGINT,

    order_number VARCHAR(50) UNIQUE NOT NULL,
    order_status_code VARCHAR(20) NOT NULL,

    medication_name VARCHAR(500) NOT NULL,
    generic_name VARCHAR(500),
    rxnorm_code VARCHAR(50),

    dose_quantity DECIMAL(18, 6),
    dose_unit_code VARCHAR(50),
    route_code VARCHAR(50),
    frequency_code VARCHAR(50),

    prn_indicator BOOLEAN DEFAULT FALSE,
    prn_reason TEXT,

    start_datetime TIMESTAMP NOT NULL,
    stop_datetime TIMESTAMP,

    ordering_provider_id BIGINT NOT NULL,
    ordered_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    clinical_indication TEXT,

    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    modified_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_medication_order_patient ON medication_order(patient_id);
CREATE INDEX idx_medication_order_status ON medication_order(order_status_code);
CREATE INDEX idx_medication_order_rxnorm ON medication_order(rxnorm_code);

-- ============================================================================
-- CLINICAL OBSERVATION DOMAIN
-- ============================================================================

CREATE TABLE clinical_observation (
    observation_id BIGSERIAL PRIMARY KEY,
    patient_id BIGINT NOT NULL REFERENCES patient(patient_id),
    encounter_id BIGINT,
    order_id BIGINT,

    observation_code VARCHAR(50) NOT NULL,
    observation_name VARCHAR(500) NOT NULL,
    observation_category_code VARCHAR(50),

    result_value_numeric DECIMAL(18, 6),
    result_value_text VARCHAR(4000),
    result_units VARCHAR(50),

    reference_range_low DECIMAL(18, 6),
    reference_range_high DECIMAL(18, 6),
    reference_range_text VARCHAR(500),

    abnormal_flag_code VARCHAR(20),
    observation_status_code VARCHAR(20) NOT NULL,

    observation_datetime TIMESTAMP NOT NULL,
    result_verified_datetime TIMESTAMP,

    performing_provider_id BIGINT,

    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_observation_patient ON clinical_observation(patient_id);
CREATE INDEX idx_observation_datetime ON clinical_observation(observation_datetime DESC);
CREATE INDEX idx_observation_code ON clinical_observation(observation_code);

-- ============================================================================
-- AUDIT TRAIL
-- ============================================================================

CREATE TABLE audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id BIGINT NOT NULL,
    action_type VARCHAR(20) NOT NULL,  -- INSERT, UPDATE, DELETE, ACCESS

    user_id BIGINT,
    username VARCHAR(100),
    ip_address INET,

    old_values JSONB,
    new_values JSONB,

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_audit_log_table ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);

-- ============================================================================
-- AUDIT TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_log (table_name, record_id, action_type, old_values, timestamp)
        VALUES (TG_TABLE_NAME, OLD.patient_id, 'DELETE', row_to_json(OLD), CURRENT_TIMESTAMP);
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit_log (table_name, record_id, action_type, old_values, new_values, timestamp)
        VALUES (TG_TABLE_NAME, NEW.patient_id, 'UPDATE', row_to_json(OLD), row_to_json(NEW), CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_log (table_name, record_id, action_type, new_values, timestamp)
        VALUES (TG_TABLE_NAME, NEW.patient_id, 'INSERT', row_to_json(NEW), CURRENT_TIMESTAMP);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers
CREATE TRIGGER patient_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON patient
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER allergy_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON allergy
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

-- Insert sample patient
INSERT INTO patient (
    medical_record_number,
    first_name,
    middle_name,
    last_name,
    date_of_birth,
    gender_code,
    sex_at_birth,
    ssn_encrypted
) VALUES (
    'MRN123456',
    'John',
    'Robert',
    'Doe',
    '1980-01-15',
    'M',
    'M',
    pgp_sym_encrypt('123-45-6789', 'encryption_key_here')
);

COMMIT;
