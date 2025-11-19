-- Clinical Data Mart Schema for Analytics
-- Star schema optimized for clinical quality and population health queries

-- Date Dimension
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    day_of_week INT,
    day_name VARCHAR(10),
    month_number INT,
    month_name VARCHAR(10),
    quarter INT,
    year INT,
    fiscal_year INT,
    fiscal_quarter INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    holiday_name VARCHAR(100)
);

-- Patient Dimension (SCD Type 2)
CREATE TABLE dim_patient (
    patient_key BIGINT PRIMARY KEY,
    mrn VARCHAR(50),
    enterprise_mrn VARCHAR(50),
    date_of_birth DATE,
    age_current INT,
    gender_code VARCHAR(10),
    race_code VARCHAR(50),
    ethnicity_code VARCHAR(50),
    primary_language VARCHAR(50),
    marital_status VARCHAR(20),
    zip_code VARCHAR(10),
    county VARCHAR(100),
    state VARCHAR(2),
    -- SCD Type 2 fields
    effective_start_date DATE,
    effective_end_date DATE,
    current_flag BOOLEAN,
    version INT,
    -- Audit
    created_timestamp TIMESTAMP,
    updated_timestamp TIMESTAMP
);

-- Provider Dimension
CREATE TABLE dim_provider (
    provider_key BIGINT PRIMARY KEY,
    npi VARCHAR(10),
    provider_name VARCHAR(200),
    specialty VARCHAR(100),
    sub_specialty VARCHAR(100),
    department VARCHAR(100),
    primary_location_key BIGINT,
    provider_type VARCHAR(50),
    provider_status VARCHAR(20),
    effective_start_date DATE,
    effective_end_date DATE,
    current_flag BOOLEAN
);

-- Location Dimension
CREATE TABLE dim_location (
    location_key BIGINT PRIMARY KEY,
    location_name VARCHAR(200),
    location_type VARCHAR(50),
    address VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    facility_key BIGINT,
    service_line VARCHAR(100)
);

-- Encounter Fact
CREATE TABLE fact_encounter (
    encounter_key BIGINT PRIMARY KEY,
    encounter_id VARCHAR(50),
    patient_key BIGINT,
    provider_key BIGINT,
    location_key BIGINT,
    admission_date_key INT,
    discharge_date_key INT,
    encounter_type VARCHAR(50),
    encounter_class VARCHAR(50),
    admission_source VARCHAR(50),
    discharge_disposition VARCHAR(50),
    length_of_stay DECIMAL(10,2),
    drg_code VARCHAR(10),
    severity_of_illness VARCHAR(20),
    risk_of_mortality VARCHAR(20),
    total_charges DECIMAL(15,2),
    total_payments DECIMAL(15,2),
    readmission_30d_flag BOOLEAN,
    -- Foreign Keys
    FOREIGN KEY (patient_key) REFERENCES dim_patient(patient_key),
    FOREIGN KEY (provider_key) REFERENCES dim_provider(provider_key),
    FOREIGN KEY (location_key) REFERENCES dim_location(location_key),
    FOREIGN KEY (admission_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (discharge_date_key) REFERENCES dim_date(date_key)
);

-- Diagnosis Fact
CREATE TABLE fact_diagnosis (
    diagnosis_key BIGINT PRIMARY KEY,
    encounter_key BIGINT,
    patient_key BIGINT,
    diagnosis_date_key INT,
    diagnosis_code VARCHAR(20),
    diagnosis_description TEXT,
    diagnosis_type VARCHAR(50),
    diagnosis_sequence INT,
    chronic_flag BOOLEAN,
    hcc_code VARCHAR(10),
    hcc_weight DECIMAL(10,4),
    FOREIGN KEY (encounter_key) REFERENCES fact_encounter(encounter_key),
    FOREIGN KEY (patient_key) REFERENCES dim_patient(patient_key)
);

-- Lab Result Fact
CREATE TABLE fact_lab_result (
    lab_result_key BIGINT PRIMARY KEY,
    encounter_key BIGINT,
    patient_key BIGINT,
    collection_date_key INT,
    result_date_key INT,
    lab_test_code VARCHAR(20),
    lab_test_name VARCHAR(500),
    result_value VARCHAR(500),
    result_numeric DECIMAL(18,6),
    result_unit VARCHAR(50),
    reference_range_low DECIMAL(18,6),
    reference_range_high DECIMAL(18,6),
    abnormal_flag VARCHAR(10),
    critical_flag BOOLEAN,
    FOREIGN KEY (encounter_key) REFERENCES fact_encounter(encounter_key),
    FOREIGN KEY (patient_key) REFERENCES dim_patient(patient_key)
);

-- Indexes for performance
CREATE INDEX idx_fact_enc_patient ON fact_encounter(patient_key);
CREATE INDEX idx_fact_enc_date ON fact_encounter(admission_date_key);
CREATE INDEX idx_fact_diag_patient ON fact_diagnosis(patient_key);
CREATE INDEX idx_fact_diag_code ON fact_diagnosis(diagnosis_code);
CREATE INDEX idx_fact_lab_patient ON fact_lab_result(patient_key);
CREATE INDEX idx_fact_lab_code ON fact_lab_result(lab_test_code);
