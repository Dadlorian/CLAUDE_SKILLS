# Clinical Data Warehouse Reference

## Overview

A Clinical Data Warehouse (CDW) is an enterprise-level repository that integrates clinical, financial, and operational data from multiple source systems to enable comprehensive analytics, reporting, and decision support.

## Architecture Patterns

### Traditional Enterprise Data Warehouse (EDW)

```
Source Systems → Staging → Integration (ODS) → EDW → Data Marts → Analytics
```

**Layers:**
1. **Staging Layer**: Raw extracts from source systems, minimal transformation
2. **Integration Layer (ODS)**: Operational Data Store for near-real-time reporting
3. **Enterprise Data Warehouse**: Conformed dimensions and facts, historical data
4. **Data Mart Layer**: Department-specific or use-case focused aggregations
5. **Semantic Layer**: Business definitions, calculated metrics, security

### Modern Cloud Data Warehouse

```
EHR/Sources → Event Streaming → Data Lake (Raw) → Data Warehouse (Curated) → Analytics
                                        ↓
                                  ML/AI Platform
```

**Components:**
- **Bronze Layer**: Raw, immutable data from sources
- **Silver Layer**: Cleaned, validated, conformed data
- **Gold Layer**: Business-level aggregates and curated datasets
- **Feature Store**: ML features for predictive models

## Core Design Principles

### 1. Dimensional Modeling (Kimball)

**Star Schema**: Facts surrounded by dimensions
- **Fact Tables**: Measurable events (encounters, lab results, medications)
- **Dimension Tables**: Descriptive attributes (patient, provider, location, time)

**Snowflake Schema**: Normalized dimensions (less common in healthcare)

### 2. Data Vault (Scalable, Auditable)

**Components:**
- **Hubs**: Unique business keys (patient, provider, location)
- **Links**: Relationships between hubs (patient-provider-encounter)
- **Satellites**: Descriptive attributes with history

**Benefits**: Audit trail, parallel loading, business key stability

### 3. Anchor Modeling (Temporal)

Extreme 6NF for temporal and evolving schemas.

## Key Clinical Dimensions

### Patient Dimension (DIM_PATIENT)

```sql
CREATE TABLE dim_patient (
    patient_key BIGINT PRIMARY KEY,          -- Surrogate key
    mrn VARCHAR(50),                          -- Medical record number
    enterprise_mrn VARCHAR(50),               -- Enterprise-wide MRN
    ssn_hash VARCHAR(64),                     -- Hashed SSN for matching
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    date_of_death DATE,
    gender_code VARCHAR(10),
    race_code VARCHAR(50),
    ethnicity_code VARCHAR(50),
    preferred_language VARCHAR(50),
    marital_status_code VARCHAR(20),
    religion_code VARCHAR(50),
    primary_care_provider_key BIGINT,
    patient_status VARCHAR(20),               -- Active, Deceased, Inactive
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    effective_start_date DATE,
    effective_end_date DATE,
    current_flag BOOLEAN,
    source_system VARCHAR(50)
);
```

**SCD Type 2**: Track historical changes (name, address, PCP)

### Provider Dimension (DIM_PROVIDER)

```sql
CREATE TABLE dim_provider (
    provider_key BIGINT PRIMARY KEY,
    npi VARCHAR(10),                          -- National Provider Identifier
    provider_id VARCHAR(50),                  -- Internal ID
    provider_name VARCHAR(200),
    provider_type VARCHAR(100),               -- Physician, NP, PA, RN
    specialty VARCHAR(100),
    sub_specialty VARCHAR(100),
    department_key BIGINT,
    location_key BIGINT,
    taxonomy_code VARCHAR(20),
    license_number VARCHAR(50),
    license_state VARCHAR(2),
    dea_number VARCHAR(20),
    provider_status VARCHAR(20),              -- Active, Inactive, Terminated
    effective_start_date DATE,
    effective_end_date DATE,
    current_flag BOOLEAN
);
```

### Location Dimension (DIM_LOCATION)

```sql
CREATE TABLE dim_location (
    location_key BIGINT PRIMARY KEY,
    location_id VARCHAR(50),
    location_name VARCHAR(200),
    location_type VARCHAR(50),                -- Hospital, Clinic, ED, OR
    address_line1 VARCHAR(200),
    address_line2 VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    county VARCHAR(100),
    fips_code VARCHAR(10),                    -- For SDOH analytics
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    facility_id VARCHAR(50),
    hospital_key BIGINT,
    service_line VARCHAR(100),
    cost_center VARCHAR(50),
    revenue_department VARCHAR(100)
);
```

### Time Dimension (DIM_DATE)

```sql
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,                 -- YYYYMMDD format
    full_date DATE,
    day_of_week INT,
    day_name VARCHAR(10),
    day_of_month INT,
    day_of_year INT,
    week_of_year INT,
    month_number INT,
    month_name VARCHAR(10),
    quarter INT,
    year INT,
    fiscal_year INT,
    fiscal_quarter INT,
    fiscal_month INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    holiday_name VARCHAR(100),
    is_business_day BOOLEAN,
    season VARCHAR(20)                        -- For seasonal analytics
);
```

## Core Clinical Facts

### Encounter Fact (FACT_ENCOUNTER)

```sql
CREATE TABLE fact_encounter (
    encounter_key BIGINT PRIMARY KEY,
    encounter_id VARCHAR(50),
    patient_key BIGINT,
    provider_key BIGINT,
    location_key BIGINT,
    admission_date_key INT,
    discharge_date_key INT,
    admission_datetime TIMESTAMP,
    discharge_datetime TIMESTAMP,
    encounter_type VARCHAR(50),               -- Inpatient, Outpatient, ED, etc.
    encounter_class VARCHAR(50),
    admission_source VARCHAR(50),
    discharge_disposition VARCHAR(50),
    financial_class VARCHAR(50),
    primary_payer_key BIGINT,
    drg_code VARCHAR(10),                     -- Diagnosis Related Group
    apr_drg_code VARCHAR(10),
    severity_of_illness VARCHAR(20),
    risk_of_mortality VARCHAR(20),
    length_of_stay DECIMAL(10,2),
    total_charges DECIMAL(15,2),
    total_payments DECIMAL(15,2),
    readmission_flag BOOLEAN,
    readmission_within_30_days BOOLEAN,
    hospital_acquired_condition_flag BOOLEAN,
    patient_safety_event_flag BOOLEAN
);
```

### Diagnosis Fact (FACT_DIAGNOSIS)

```sql
CREATE TABLE fact_diagnosis (
    diagnosis_key BIGINT PRIMARY KEY,
    encounter_key BIGINT,
    patient_key BIGINT,
    provider_key BIGINT,
    diagnosis_date_key INT,
    diagnosis_datetime TIMESTAMP,
    diagnosis_code VARCHAR(20),               -- ICD-10-CM
    diagnosis_code_system VARCHAR(20),        -- ICD-10, SNOMED
    diagnosis_description TEXT,
    diagnosis_type VARCHAR(50),               -- Admitting, Primary, Secondary
    diagnosis_sequence INT,
    present_on_admission VARCHAR(1),          -- Y/N/U/W
    chronic_condition_flag BOOLEAN,
    hcc_code VARCHAR(10),                     -- Hierarchical Condition Category
    hcc_weight DECIMAL(10,4),
    clinical_classification VARCHAR(100),      -- CCS category
    body_system VARCHAR(100)
);
```

### Procedure Fact (FACT_PROCEDURE)

```sql
CREATE TABLE fact_procedure (
    procedure_key BIGINT PRIMARY KEY,
    encounter_key BIGINT,
    patient_key BIGINT,
    provider_key BIGINT,
    procedure_date_key INT,
    procedure_datetime TIMESTAMP,
    procedure_code VARCHAR(20),               -- CPT, ICD-10-PCS
    procedure_code_system VARCHAR(20),
    procedure_description TEXT,
    procedure_type VARCHAR(50),
    procedure_sequence INT,
    modifier_1 VARCHAR(10),
    modifier_2 VARCHAR(10),
    modifier_3 VARCHAR(10),
    modifier_4 VARCHAR(10),
    quantity INT,
    units DECIMAL(10,2),
    charges DECIMAL(15,2),
    allowed_amount DECIMAL(15,2),
    paid_amount DECIMAL(15,2),
    location_key BIGINT
);
```

### Medication Fact (FACT_MEDICATION)

```sql
CREATE TABLE fact_medication (
    medication_key BIGINT PRIMARY KEY,
    encounter_key BIGINT,
    patient_key BIGINT,
    provider_key BIGINT,
    order_date_key INT,
    administration_date_key INT,
    medication_code VARCHAR(20),              -- NDC, RxNorm
    medication_name VARCHAR(500),
    generic_name VARCHAR(500),
    therapeutic_class VARCHAR(200),
    pharmacologic_class VARCHAR(200),
    route VARCHAR(50),
    dose DECIMAL(10,2),
    dose_unit VARCHAR(50),
    frequency VARCHAR(50),
    duration INT,
    duration_unit VARCHAR(20),
    quantity DECIMAL(10,2),
    refills INT,
    medication_status VARCHAR(50),            -- Ordered, Administered, Discontinued
    formulary_status VARCHAR(50),
    high_risk_flag BOOLEAN,                   -- High-risk medications
    opioid_flag BOOLEAN,
    antibiotic_flag BOOLEAN
);
```

### Laboratory Fact (FACT_LAB_RESULT)

```sql
CREATE TABLE fact_lab_result (
    lab_result_key BIGINT PRIMARY KEY,
    encounter_key BIGINT,
    patient_key BIGINT,
    provider_key BIGINT,
    collection_date_key INT,
    result_date_key INT,
    collection_datetime TIMESTAMP,
    result_datetime TIMESTAMP,
    lab_test_code VARCHAR(20),                -- LOINC
    lab_test_name VARCHAR(500),
    result_value VARCHAR(500),
    result_numeric DECIMAL(18,6),
    result_unit VARCHAR(50),
    reference_range_low DECIMAL(18,6),
    reference_range_high DECIMAL(18,6),
    abnormal_flag VARCHAR(10),                -- H, L, N, A
    critical_flag BOOLEAN,
    result_status VARCHAR(50),                -- Final, Preliminary, Corrected
    performing_lab VARCHAR(200),
    specimen_type VARCHAR(100),
    test_category VARCHAR(100)                -- Chemistry, Hematology, etc.
);
```

### Vital Signs Fact (FACT_VITALS)

```sql
CREATE TABLE fact_vitals (
    vitals_key BIGINT PRIMARY KEY,
    encounter_key BIGINT,
    patient_key BIGINT,
    measurement_date_key INT,
    measurement_datetime TIMESTAMP,
    vital_sign_type VARCHAR(50),              -- BP, Temp, HR, RR, SpO2, etc.
    vital_value DECIMAL(10,2),
    vital_unit VARCHAR(50),
    systolic_bp DECIMAL(10,2),
    diastolic_bp DECIMAL(10,2),
    temperature DECIMAL(10,2),
    temperature_unit VARCHAR(1),              -- F, C
    heart_rate DECIMAL(10,2),
    respiratory_rate DECIMAL(10,2),
    oxygen_saturation DECIMAL(10,2),
    weight_kg DECIMAL(10,2),
    height_cm DECIMAL(10,2),
    bmi DECIMAL(10,2),
    pain_scale INT,
    location_key BIGINT
);
```

## Master Data Management

### Patient Matching & MPI (Master Patient Index)

**Deterministic Matching:**
```sql
-- Exact match on SSN and DOB
SELECT * FROM patient_source
WHERE ssn = @ssn AND date_of_birth = @dob;

-- Match on Name + DOB
WHERE SOUNDEX(last_name) = SOUNDEX(@last_name)
  AND first_name = @first_name
  AND date_of_birth = @dob;
```

**Probabilistic Matching:**
- Jaro-Winkler distance for name similarity
- Levenshtein distance for addresses
- Weighted scoring across multiple attributes
- Machine learning-based matching (dedupe library)

**MDM Platforms:**
- IBM InfoSphere MDM
- Oracle Healthcare Master Person Index
- Verato Universal Identity
- NextGate Enterprise Master Patient Index

### Provider Master File

**NPI Validation:**
```python
# Validate NPI checksum (Luhn algorithm)
def validate_npi(npi):
    if len(npi) != 10:
        return False

    digits = [int(d) for d in npi]
    checksum = sum(digits[i] if i % 2 == 0 else (digits[i] * 2) // 10 + (digits[i] * 2) % 10
                   for i in range(9))
    return (checksum + digits[9]) % 10 == 0
```

**Provider Deduplication:**
- Match on NPI (primary)
- State license number + state
- DEA number
- Name + taxonomy + location

## Data Quality Framework

### Critical Data Quality Rules

**Patient Data:**
- MRN must be unique per facility
- Date of birth must be <= current date
- Date of death must be >= date of birth
- Gender must be in value set (M, F, U, O)
- SSN must be 9 digits (if present)

**Encounter Data:**
- Admission date <= discharge date
- Discharge disposition required for closed encounters
- Primary diagnosis required for inpatient encounters
- Financial class required

**Clinical Data:**
- Lab result date >= collection date
- Medication end date >= start date
- Vitals within reasonable ranges (HR: 20-300, BP: 40-300, etc.)

### Data Quality Metrics

```sql
-- Completeness
SELECT
    'Patient SSN' AS metric,
    COUNT(*) AS total_records,
    COUNT(ssn) AS populated,
    ROUND(100.0 * COUNT(ssn) / COUNT(*), 2) AS completeness_pct
FROM dim_patient;

-- Timeliness
SELECT
    'Encounter Load Lag' AS metric,
    AVG(DATEDIFF(hour, discharge_datetime, etl_load_datetime)) AS avg_lag_hours,
    MAX(DATEDIFF(hour, discharge_datetime, etl_load_datetime)) AS max_lag_hours
FROM fact_encounter
WHERE discharge_datetime >= DATEADD(day, -30, GETDATE());

-- Accuracy (conformance to value sets)
SELECT
    'Invalid Gender Codes' AS metric,
    COUNT(*) AS invalid_count
FROM dim_patient
WHERE gender_code NOT IN ('M', 'F', 'U', 'O');
```

## Performance Optimization

### Partitioning Strategies

**Date-based Partitioning (Most Common):**
```sql
-- Partition fact tables by month
CREATE TABLE fact_encounter (
    ...
)
PARTITION BY RANGE (admission_date_key) (
    PARTITION p202301 VALUES LESS THAN (20230201),
    PARTITION p202302 VALUES LESS THAN (20230301),
    PARTITION p202303 VALUES LESS THAN (20230401),
    ...
);
```

**Benefits:**
- Faster queries with partition pruning
- Easier archival and purging
- Parallel processing of partitions

### Indexing Best Practices

```sql
-- Clustered index on primary key (default)
CREATE CLUSTERED INDEX idx_encounter_pk ON fact_encounter(encounter_key);

-- Non-clustered indexes on common query patterns
CREATE INDEX idx_encounter_patient ON fact_encounter(patient_key, admission_date_key);
CREATE INDEX idx_encounter_date ON fact_encounter(admission_date_key);
CREATE INDEX idx_encounter_provider ON fact_encounter(provider_key);

-- Covering index for common query
CREATE INDEX idx_encounter_coverage
ON fact_encounter(patient_key, admission_date_key)
INCLUDE (encounter_type, drg_code, length_of_stay);

-- Filtered index for active records
CREATE INDEX idx_encounter_recent
ON fact_encounter(admission_date_key)
WHERE admission_date_key >= 20200101;
```

### Aggregate Tables

```sql
-- Pre-aggregated monthly patient summaries
CREATE TABLE agg_patient_monthly (
    patient_key BIGINT,
    year_month INT,
    encounter_count INT,
    ed_visit_count INT,
    inpatient_admission_count INT,
    total_charges DECIMAL(15,2),
    primary_care_visit_count INT,
    specialist_visit_count INT,
    unique_providers INT,
    chronic_condition_count INT
);

-- Update monthly via scheduled job
```

## ETL Patterns

### Incremental Loading

```sql
-- Extract delta records based on modified date
SELECT *
FROM source_system.encounters
WHERE last_modified_date > (
    SELECT MAX(source_last_modified_date)
    FROM staging.encounters
)
OR encounter_id IN (
    SELECT encounter_id
    FROM staging.encounters_to_reprocess
);
```

### CDC (Change Data Capture)

**Database-level CDC:**
```sql
-- Enable CDC on source table (SQL Server)
EXEC sys.sp_cdc_enable_table
    @source_schema = 'dbo',
    @source_name = 'encounters',
    @role_name = NULL;

-- Query CDC changes
SELECT *
FROM cdc.dbo_encounters_CT
WHERE __$operation IN (2, 4)  -- Insert, Update
  AND __$start_lsn >= @last_processed_lsn;
```

**Log-based CDC (Debezium, GoldenGate):**
- Near real-time replication
- Minimal impact on source systems
- Supports schema evolution

### SCD Type 2 Implementation

```sql
-- Update existing record (expire old version)
UPDATE dim_patient
SET effective_end_date = CURRENT_DATE - 1,
    current_flag = FALSE
WHERE patient_key = @patient_key
  AND current_flag = TRUE;

-- Insert new record (new version)
INSERT INTO dim_patient (
    patient_key, mrn, first_name, last_name,
    effective_start_date, effective_end_date, current_flag
)
VALUES (
    @patient_key, @mrn, @new_first_name, @new_last_name,
    CURRENT_DATE, '9999-12-31', TRUE
);
```

## Reference Architectures

### On-Premises EDW

```
Source Systems (EHR, Labs, etc.)
    ↓ (HL7, Files, DB Links)
ETL Server (Informatica, SSIS)
    ↓
Staging Database (SQL Server)
    ↓
Enterprise Data Warehouse (SQL Server, Oracle)
    ↓
OLAP Cubes (SSAS, Essbase)
    ↓
BI Tools (Tableau, SSRS)
```

### Cloud-Native Architecture

```
Source Systems
    ↓ (APIs, Streaming)
Event Hub / Kafka
    ↓
Data Lake (S3, ADLS) - Bronze Layer
    ↓ (Apache Spark, dbt)
Data Warehouse (Snowflake, Redshift) - Silver/Gold Layers
    ↓
BI (Tableau, Power BI) + ML (SageMaker, Databricks)
```

### Hybrid Architecture

```
On-Prem EHR (Epic, Cerner)
    ↓ (VPN/Direct Connect)
Cloud Data Integration (AWS DMS, Azure Data Factory)
    ↓
Cloud Data Warehouse (Snowflake, BigQuery)
    ↓
Analytics & ML (Cloud-native tools)
```

## Metadata Management

### Business Glossary

- **Encounter**: A documented interaction between a patient and healthcare provider
- **Readmission**: Inpatient admission within 30 days of prior discharge
- **Primary Care Visit**: E&M visit with PCP (CPT 99201-99215)
- **Chronic Condition**: Condition lasting >= 12 months per CMS definition

### Data Lineage

```
Source: Epic.dbo.PAT_ENC
    ↓ (SSIS Package: Extract_Encounters)
Staging: STG.Epic_Encounters
    ↓ (SSIS Package: Transform_Encounters)
EDW: dim_encounter, fact_encounter
    ↓ (dbt model: monthly_patient_summary)
Data Mart: mart.patient_monthly_summary
    ↓ (Tableau Extract)
Report: Patient Utilization Dashboard
```

**Tools:**
- Informatica Enterprise Data Catalog
- Collibra Data Governance
- Alation Data Catalog
- Apache Atlas (open-source)

## Regulatory Compliance

### HIPAA Requirements

- **Minimum Necessary**: Only provide access to data required for job function
- **Audit Controls**: Log all access to PHI
- **Data Integrity**: Protect data from improper alteration or destruction
- **Transmission Security**: Encrypt data in transit

### De-identification Methods

**Safe Harbor Method:**
- Remove 18 HIPAA identifiers
- No actual knowledge that residual information can identify individual

**Expert Determination:**
- Statistical and scientific principles
- Very small risk of re-identification

**Limited Data Set:**
- Remove 16 identifiers (keep dates, geographic data)
- Requires data use agreement

## Key Vendors & Tools

### Data Warehouse Platforms
- **Snowflake**: Cloud-native, separate compute/storage, HIPAA-compliant
- **Google BigQuery**: Serverless, ML integration, FHIR analytics
- **AWS Redshift**: Columnar, tight AWS integration, Spectrum for S3
- **Azure Synapse**: Integrated analytics, serverless + dedicated pools
- **Teradata**: Traditional EDW, healthcare-specific accelerators

### Healthcare ETL
- **Health Catalyst Data Operating System (DOS)**: Healthcare-specific EDW
- **Informatica**: Enterprise-grade ETL, healthcare templates
- **Talend**: Open-source + enterprise, cloud-native
- **Apache NiFi**: Data flow automation, healthcare processors

---

*Clinical Data Warehouse Reference - Foundation for healthcare analytics and population health management.*
