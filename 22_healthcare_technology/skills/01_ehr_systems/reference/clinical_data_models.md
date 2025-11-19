# Clinical Data Models for EHR Systems

## Overview

This reference documents common data models, database schemas, and entity relationships used in Electronic Health Record (EHR) systems. Understanding these models is essential for building, integrating, or customizing EHR platforms.

## Core Entity Relationship Model

### High-Level ERD
```
Patient (1) ----< (M) Encounter
                      |
                      |----< (M) Order
                      |         |
                      |         |----< (M) Medication_Administration
                      |         |----< (M) Lab_Result
                      |         |----< (M) Radiology_Study
                      |
                      |----< (M) Clinical_Note
                      |----< (M) Vital_Signs
                      |----< (M) Diagnosis

Patient (1) ----< (M) Allergy
Patient (1) ----< (M) Problem_List
Patient (1) ----< (M) Immunization
Patient (1) ----< (M) Insurance_Coverage

Practitioner (1) ----< (M) Encounter (as attending)
Practitioner (1) ----< (M) Order (as ordering provider)
Practitioner (1) ----< (M) Clinical_Note (as author)
```

## Patient Domain

### Patient Table
Core demographic and identification information.

```sql
CREATE TABLE patient (
    patient_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    medical_record_number VARCHAR(50) UNIQUE NOT NULL,
    ssn VARCHAR(11) ENCRYPTED,

    -- Name components
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    suffix VARCHAR(20),
    prefix VARCHAR(20),
    maiden_name VARCHAR(100),

    -- Demographics
    date_of_birth DATE NOT NULL,
    date_of_death DATE,
    gender_code VARCHAR(10),
    sex_at_birth VARCHAR(10),
    marital_status_code VARCHAR(10),

    -- Race and Ethnicity (multiple allowed)
    race_code VARCHAR(20),
    ethnicity_code VARCHAR(20),

    -- Language and Communication
    primary_language_code VARCHAR(10),
    interpreter_required BOOLEAN DEFAULT FALSE,

    -- VIP and Security
    vip_indicator BOOLEAN DEFAULT FALSE,
    restricted_access BOOLEAN DEFAULT FALSE,

    -- Administrative
    active_status BOOLEAN DEFAULT TRUE,
    deceased_indicator BOOLEAN DEFAULT FALSE,

    -- Audit fields
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    modified_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    modified_by VARCHAR(100),

    INDEX idx_mrn (medical_record_number),
    INDEX idx_last_name (last_name),
    INDEX idx_dob (date_of_birth),
    INDEX idx_ssn (ssn)
);
```

### Patient_Identifier Table
Multiple identification numbers per patient.

```sql
CREATE TABLE patient_identifier (
    identifier_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    patient_id BIGINT NOT NULL,
    identifier_type_code VARCHAR(20) NOT NULL, -- MRN, SSN, DL, etc.
    identifier_value VARCHAR(100) NOT NULL,
    assigning_authority VARCHAR(100),
    effective_date DATE,
    expiration_date DATE,
    active_indicator BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    UNIQUE KEY uk_patient_identifier (patient_id, identifier_type_code, assigning_authority),
    INDEX idx_identifier_value (identifier_value)
);
```

### Patient_Address Table
Multiple addresses per patient (home, work, temporary).

```sql
CREATE TABLE patient_address (
    address_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    patient_id BIGINT NOT NULL,
    address_type_code VARCHAR(10), -- HOME, WORK, TEMP
    use_code VARCHAR(10), -- PRIMARY, SECONDARY

    -- Address components
    street_line_1 VARCHAR(200),
    street_line_2 VARCHAR(200),
    city VARCHAR(100),
    county VARCHAR(100),
    state_code VARCHAR(10),
    postal_code VARCHAR(20),
    country_code VARCHAR(10),

    -- Geolocation
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- Validity
    effective_date DATE,
    expiration_date DATE,
    active_indicator BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    INDEX idx_patient (patient_id),
    INDEX idx_postal_code (postal_code)
);
```

### Patient_Contact Table
Phone numbers, email addresses.

```sql
CREATE TABLE patient_contact (
    contact_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    patient_id BIGINT NOT NULL,
    contact_type_code VARCHAR(20), -- PHONE, EMAIL, FAX
    contact_use_code VARCHAR(20), -- HOME, WORK, MOBILE
    contact_value VARCHAR(200) NOT NULL,
    priority_rank INT,
    preferred_indicator BOOLEAN DEFAULT FALSE,
    active_indicator BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    INDEX idx_patient (patient_id)
);
```

### Patient_Relationship Table
Emergency contacts, next of kin, guarantor.

```sql
CREATE TABLE patient_relationship (
    relationship_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    patient_id BIGINT NOT NULL,
    relationship_type_code VARCHAR(20), -- EMERGENCY, NOK, GUARANTOR, SPOUSE

    -- Related person information
    related_person_name VARCHAR(200),
    related_person_phone VARCHAR(50),
    related_person_address_line VARCHAR(200),
    related_person_city VARCHAR(100),
    related_person_state VARCHAR(10),
    related_person_postal_code VARCHAR(20),

    priority_rank INT,
    effective_date DATE,
    expiration_date DATE,
    active_indicator BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    INDEX idx_patient (patient_id)
);
```

## Encounter Domain

### Encounter Table
Patient visits, admissions, episodes of care.

```sql
CREATE TABLE encounter (
    encounter_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    patient_id BIGINT NOT NULL,
    visit_number VARCHAR(50) UNIQUE NOT NULL,
    account_number VARCHAR(50),

    -- Encounter Classification
    encounter_class_code VARCHAR(20) NOT NULL, -- INPATIENT, OUTPATIENT, EMERGENCY, OBSERVATION
    encounter_type_code VARCHAR(50),
    encounter_status_code VARCHAR(20) NOT NULL, -- PLANNED, ARRIVED, IN_PROGRESS, FINISHED, CANCELLED

    -- Timing
    registration_datetime TIMESTAMP,
    arrival_datetime TIMESTAMP,
    admission_datetime TIMESTAMP,
    discharge_datetime TIMESTAMP,
    expected_discharge_datetime TIMESTAMP,

    -- Clinical Details
    admission_source_code VARCHAR(20), -- ER, TRANSFER, REFERRAL, etc.
    admission_type_code VARCHAR(20), -- EMERGENCY, URGENT, ELECTIVE
    chief_complaint TEXT,

    -- Care Team
    attending_provider_id BIGINT,
    admitting_provider_id BIGINT,
    referring_provider_id BIGINT,
    primary_care_provider_id BIGINT,

    -- Location
    facility_id BIGINT,
    department_id BIGINT,
    room_number VARCHAR(20),
    bed_number VARCHAR(20),

    -- Discharge Information
    discharge_disposition_code VARCHAR(20), -- HOME, SNF, EXPIRED, AMA, etc.
    discharge_location VARCHAR(200),

    -- Financial
    financial_class_code VARCHAR(20),

    -- Audit
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    modified_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    modified_by VARCHAR(100),

    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (attending_provider_id) REFERENCES practitioner(provider_id),
    INDEX idx_patient (patient_id),
    INDEX idx_visit_number (visit_number),
    INDEX idx_admission_datetime (admission_datetime),
    INDEX idx_encounter_status (encounter_status_code)
);
```

### Encounter_Diagnosis Table
Diagnoses associated with encounters.

```sql
CREATE TABLE encounter_diagnosis (
    diagnosis_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    encounter_id BIGINT NOT NULL,

    -- Diagnosis Coding
    diagnosis_code VARCHAR(20) NOT NULL,
    diagnosis_code_system VARCHAR(50) NOT NULL, -- ICD10CM, SNOMED
    diagnosis_description TEXT,

    -- Diagnosis Classification
    diagnosis_type_code VARCHAR(20), -- ADMITTING, PRINCIPAL, SECONDARY, FINAL
    diagnosis_rank INT,
    present_on_admission_indicator VARCHAR(1), -- Y, N, U, W

    -- Clinical Details
    onset_datetime TIMESTAMP,
    resolution_datetime TIMESTAMP,

    -- Audit
    documented_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    documented_by VARCHAR(100),

    FOREIGN KEY (encounter_id) REFERENCES encounter(encounter_id),
    INDEX idx_encounter (encounter_id),
    INDEX idx_diagnosis_code (diagnosis_code)
);
```

## Order Domain

### Order_Catalog Table
Orderable items catalog.

```sql
CREATE TABLE order_catalog (
    catalog_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    catalog_type_code VARCHAR(20) NOT NULL, -- MEDICATION, LAB, RADIOLOGY, PROCEDURE

    -- Identification
    mnemonic VARCHAR(100) UNIQUE NOT NULL,
    synonym VARCHAR(200),
    display_name VARCHAR(500) NOT NULL,

    -- Standard Codes
    rxnorm_code VARCHAR(50), -- For medications
    loinc_code VARCHAR(50), -- For labs
    cpt_code VARCHAR(20), -- For procedures
    snomed_code VARCHAR(50), -- For clinical concepts

    -- Clinical Details
    description TEXT,
    clinical_indications TEXT,
    contraindications TEXT,

    -- Order Defaults
    default_dose VARCHAR(100),
    default_route_code VARCHAR(20),
    default_frequency_code VARCHAR(20),
    default_duration VARCHAR(50),
    default_priority_code VARCHAR(20),

    -- Status
    active_indicator BOOLEAN DEFAULT TRUE,
    orderable_indicator BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (catalog_id) REFERENCES order_catalog(catalog_id),
    INDEX idx_mnemonic (mnemonic),
    INDEX idx_catalog_type (catalog_type_code)
);
```

### Clinical_Order Table
All clinical orders (medications, labs, imaging, procedures).

```sql
CREATE TABLE clinical_order (
    order_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    patient_id BIGINT NOT NULL,
    encounter_id BIGINT,
    catalog_id BIGINT NOT NULL,

    -- Order Identification
    order_number VARCHAR(50) UNIQUE NOT NULL,
    order_type_code VARCHAR(20) NOT NULL, -- MEDICATION, LAB, RADIOLOGY, PROCEDURE
    order_class_code VARCHAR(20), -- INPATIENT, OUTPATIENT, STAT

    -- Order Details
    order_mnemonic VARCHAR(200),
    order_description TEXT,
    order_status_code VARCHAR(20) NOT NULL, -- ORDERED, ACTIVE, COMPLETED, DISCONTINUED, CANCELLED

    -- Timing
    ordered_datetime TIMESTAMP NOT NULL,
    start_datetime TIMESTAMP,
    stop_datetime TIMESTAMP,
    completed_datetime TIMESTAMP,

    -- Priority
    priority_code VARCHAR(20), -- ROUTINE, URGENT, STAT, ASAP

    -- Ordering Provider
    ordering_provider_id BIGINT NOT NULL,
    ordering_department_id BIGINT,

    -- Clinical Context
    order_reason_code VARCHAR(50),
    order_reason_text TEXT,
    clinical_indication TEXT,

    -- Order Instructions
    order_comments TEXT,
    special_instructions TEXT,

    -- Discontinuation
    discontinued_datetime TIMESTAMP,
    discontinued_by VARCHAR(100),
    discontinue_reason TEXT,

    -- Audit
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    modified_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    modified_by VARCHAR(100),
    signed_datetime TIMESTAMP,
    signed_by VARCHAR(100),

    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (encounter_id) REFERENCES encounter(encounter_id),
    FOREIGN KEY (catalog_id) REFERENCES order_catalog(catalog_id),
    FOREIGN KEY (ordering_provider_id) REFERENCES practitioner(provider_id),
    INDEX idx_patient (patient_id),
    INDEX idx_encounter (encounter_id),
    INDEX idx_order_status (order_status_code),
    INDEX idx_ordered_datetime (ordered_datetime)
);
```

### Medication_Order_Detail Table
Medication-specific order details.

```sql
CREATE TABLE medication_order_detail (
    med_order_detail_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,

    -- Medication Identification
    medication_name VARCHAR(500),
    generic_name VARCHAR(500),
    rxnorm_code VARCHAR(50),
    ndc_code VARCHAR(20),

    -- Dosing
    dose_quantity DECIMAL(18, 6),
    dose_unit_code VARCHAR(50),
    dose_form_code VARCHAR(50), -- TABLET, CAPSULE, INJECTION, etc.

    -- Route and Frequency
    route_code VARCHAR(50), -- PO, IV, IM, SC, etc.
    frequency_code VARCHAR(50), -- BID, TID, QID, Q4H, etc.
    frequency_description VARCHAR(200),

    -- Duration and Quantity
    duration_quantity INT,
    duration_unit_code VARCHAR(20), -- DAYS, WEEKS, MONTHS

    -- Administration Instructions
    administration_instructions TEXT,
    prn_indicator BOOLEAN DEFAULT FALSE,
    prn_reason TEXT,

    -- Dispensing
    dispense_quantity DECIMAL(18, 2),
    dispense_unit_code VARCHAR(50),
    refills_authorized INT DEFAULT 0,
    substitution_allowed BOOLEAN DEFAULT TRUE,

    -- E-Prescribing
    eprescribe_sent_datetime TIMESTAMP,
    eprescribe_status_code VARCHAR(20),
    pharmacy_name VARCHAR(200),
    pharmacy_ncpdp_id VARCHAR(20),

    FOREIGN KEY (order_id) REFERENCES clinical_order(order_id),
    INDEX idx_order (order_id),
    INDEX idx_rxnorm (rxnorm_code)
);
```

### Medication_Administration Table
Record of medication administrations.

```sql
CREATE TABLE medication_administration (
    admin_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    patient_id BIGINT NOT NULL,
    encounter_id BIGINT,

    -- Administration Details
    scheduled_datetime TIMESTAMP NOT NULL,
    administered_datetime TIMESTAMP,
    admin_status_code VARCHAR(20), -- GIVEN, NOT_GIVEN, HELD, REFUSED

    -- Administered Medication
    medication_name VARCHAR(500),
    administered_dose DECIMAL(18, 6),
    dose_unit_code VARCHAR(50),
    route_code VARCHAR(50),

    -- Administration Site
    site_code VARCHAR(50),
    site_description VARCHAR(200),

    -- Administering Staff
    administered_by BIGINT,
    witness_id BIGINT,

    -- Reasons for Non-Administration
    not_given_reason_code VARCHAR(50),
    not_given_reason_text TEXT,

    -- Documentation
    administration_notes TEXT,

    -- Audit
    documented_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    documented_by VARCHAR(100),

    FOREIGN KEY (order_id) REFERENCES clinical_order(order_id),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (encounter_id) REFERENCES encounter(encounter_id),
    FOREIGN KEY (administered_by) REFERENCES practitioner(provider_id),
    INDEX idx_order (order_id),
    INDEX idx_patient (patient_id),
    INDEX idx_scheduled_datetime (scheduled_datetime)
);
```

## Clinical Documentation Domain

### Clinical_Note Table
All clinical documentation (progress notes, H&P, discharge summaries, etc.).

```sql
CREATE TABLE clinical_note (
    note_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    patient_id BIGINT NOT NULL,
    encounter_id BIGINT,

    -- Note Classification
    note_type_code VARCHAR(50) NOT NULL, -- PROGRESS, HP, DISCHARGE, CONSULT, OP, PROCEDURE
    note_title VARCHAR(500),
    service_line_code VARCHAR(50),

    -- Note Content
    note_text TEXT NOT NULL,
    note_text_encrypted BLOB, -- For highly sensitive notes

    -- Structured Components (Optional)
    chief_complaint TEXT,
    history_present_illness TEXT,
    review_of_systems TEXT,
    past_medical_history TEXT,
    physical_exam TEXT,
    assessment_plan TEXT,

    -- Author Information
    author_provider_id BIGINT NOT NULL,
    author_service_code VARCHAR(50),

    -- Timing
    service_datetime TIMESTAMP NOT NULL,
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Status
    note_status_code VARCHAR(20) NOT NULL, -- DRAFT, PRELIMINARY, FINAL, AMENDED, SIGNED
    signed_datetime TIMESTAMP,
    signed_by BIGINT,
    cosigned_datetime TIMESTAMP,
    cosigned_by BIGINT,

    -- Addenda and Amendments
    addendum_to_note_id BIGINT,
    amendment_to_note_id BIGINT,
    amendment_reason TEXT,

    -- Security
    confidential_indicator BOOLEAN DEFAULT FALSE,
    restricted_access BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (encounter_id) REFERENCES encounter(encounter_id),
    FOREIGN KEY (author_provider_id) REFERENCES practitioner(provider_id),
    FOREIGN KEY (signed_by) REFERENCES practitioner(provider_id),
    INDEX idx_patient (patient_id),
    INDEX idx_encounter (encounter_id),
    INDEX idx_service_datetime (service_datetime),
    INDEX idx_note_type (note_type_code),
    INDEX idx_note_status (note_status_code)
);
```

### Note_Template Table
Clinical documentation templates.

```sql
CREATE TABLE note_template (
    template_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    template_name VARCHAR(200) NOT NULL,
    template_type_code VARCHAR(50),
    specialty_code VARCHAR(50),

    -- Template Content
    template_text TEXT,
    template_structure JSON, -- Structured template definition

    -- Metadata
    description TEXT,
    use_instructions TEXT,

    -- Availability
    active_indicator BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(100),
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_template_type (template_type_code),
    INDEX idx_specialty (specialty_code)
);
```

## Results Domain

### Lab_Result Table
Laboratory test results.

```sql
CREATE TABLE lab_result (
    result_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    patient_id BIGINT NOT NULL,
    encounter_id BIGINT,

    -- Test Identification
    test_code VARCHAR(50) NOT NULL, -- LOINC preferred
    test_name VARCHAR(500) NOT NULL,
    test_category_code VARCHAR(50), -- CHEMISTRY, HEMATOLOGY, MICROBIOLOGY, etc.

    -- Result Value
    result_value VARCHAR(4000),
    result_value_numeric DECIMAL(18, 6),
    result_units VARCHAR(50),
    result_type_code VARCHAR(20), -- NUMERIC, TEXT, CODED

    -- Reference Range
    reference_range_low DECIMAL(18, 6),
    reference_range_high DECIMAL(18, 6),
    reference_range_text VARCHAR(500),

    -- Interpretation
    abnormal_flag_code VARCHAR(20), -- NORMAL, HIGH, LOW, CRITICAL_HIGH, CRITICAL_LOW
    result_status_code VARCHAR(20), -- PRELIMINARY, FINAL, CORRECTED, CANCELLED

    -- Timing
    specimen_collected_datetime TIMESTAMP,
    result_datetime TIMESTAMP NOT NULL,
    result_verified_datetime TIMESTAMP,

    -- Performing Lab
    performing_lab_id BIGINT,
    performing_technologist VARCHAR(200),

    -- Clinical Context
    result_comments TEXT,
    clinical_significance TEXT,

    -- Audit
    entered_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    entered_by VARCHAR(100),
    verified_by BIGINT,

    FOREIGN KEY (order_id) REFERENCES clinical_order(order_id),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (encounter_id) REFERENCES encounter(encounter_id),
    INDEX idx_order (order_id),
    INDEX idx_patient (patient_id),
    INDEX idx_result_datetime (result_datetime),
    INDEX idx_test_code (test_code)
);
```

## Problem List and Conditions

### Problem_List Table
Ongoing patient problems and diagnoses.

```sql
CREATE TABLE problem_list (
    problem_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    patient_id BIGINT NOT NULL,

    -- Problem Coding
    problem_code VARCHAR(50), -- ICD-10, SNOMED
    problem_code_system VARCHAR(50),
    problem_description TEXT NOT NULL,

    -- Classification
    problem_type_code VARCHAR(20), -- DIAGNOSIS, SYMPTOM, FINDING
    problem_status_code VARCHAR(20), -- ACTIVE, RESOLVED, INACTIVE
    clinical_status_code VARCHAR(20), -- ACTIVE, RECURRENCE, RELAPSE, INACTIVE, REMISSION, RESOLVED
    verification_status_code VARCHAR(20), -- CONFIRMED, PROVISIONAL, DIFFERENTIAL, REFUTED

    -- Severity
    severity_code VARCHAR(20), -- MILD, MODERATE, SEVERE

    -- Timing
    onset_date DATE,
    onset_age INT,
    resolution_date DATE,
    recorded_date DATE NOT NULL,

    -- Clinical Context
    recorded_by BIGINT,
    encounter_id BIGINT, -- Encounter where problem identified

    -- Problem Ranking
    chronic_indicator BOOLEAN,
    primary_problem_indicator BOOLEAN,

    -- Notes
    clinical_notes TEXT,

    -- Audit
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (recorded_by) REFERENCES practitioner(provider_id),
    INDEX idx_patient (patient_id),
    INDEX idx_problem_status (problem_status_code),
    INDEX idx_problem_code (problem_code)
);
```

## Allergy and Adverse Reactions

### Allergy Table
Patient allergies and intolerances.

```sql
CREATE TABLE allergy (
    allergy_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    patient_id BIGINT NOT NULL,

    -- Allergen
    allergen_type_code VARCHAR(20), -- DRUG, FOOD, ENVIRONMENTAL
    allergen_code VARCHAR(50), -- RxNorm for drugs
    allergen_name VARCHAR(500) NOT NULL,
    allergen_class VARCHAR(200), -- Drug class (e.g., Penicillins)

    -- Status
    allergy_status_code VARCHAR(20), -- ACTIVE, INACTIVE, RESOLVED
    verification_status_code VARCHAR(20), -- CONFIRMED, UNCONFIRMED, REFUTED

    -- Severity
    severity_code VARCHAR(20), -- MILD, MODERATE, SEVERE
    criticality_code VARCHAR(20), -- LOW, HIGH, UNABLE_TO_ASSESS

    -- Reactions
    reaction_codes JSON, -- Array of SNOMED reaction codes
    reaction_description TEXT,

    -- Timing
    onset_date DATE,
    recorded_date DATE NOT NULL,
    recorded_by BIGINT,

    -- Clinical Notes
    clinical_notes TEXT,

    -- Audit
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (recorded_by) REFERENCES practitioner(provider_id),
    INDEX idx_patient (patient_id),
    INDEX idx_allergen_type (allergen_type_code),
    INDEX idx_allergy_status (allergy_status_code)
);
```

## Vital Signs

### Vital_Signs Table
Patient vital signs measurements.

```sql
CREATE TABLE vital_signs (
    vital_sign_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    patient_id BIGINT NOT NULL,
    encounter_id BIGINT,

    -- Timing
    measurement_datetime TIMESTAMP NOT NULL,

    -- Blood Pressure
    systolic_bp INT,
    diastolic_bp INT,
    bp_position_code VARCHAR(20), -- SITTING, STANDING, LYING
    bp_site_code VARCHAR(20), -- LEFT_ARM, RIGHT_ARM, LEFT_LEG, RIGHT_LEG

    -- Vital Signs
    heart_rate INT, -- beats per minute
    respiratory_rate INT, -- breaths per minute
    temperature DECIMAL(5, 2), -- in Fahrenheit or Celsius
    temperature_unit_code VARCHAR(1), -- F or C
    temperature_route_code VARCHAR(20), -- ORAL, RECTAL, AXILLARY, TYMPANIC

    -- Oxygen
    oxygen_saturation INT, -- SpO2 percentage
    oxygen_flow_rate DECIMAL(5, 2), -- liters per minute
    oxygen_delivery_code VARCHAR(50), -- ROOM_AIR, NASAL_CANNULA, MASK, etc.

    -- Other Measurements
    weight DECIMAL(7, 2),
    weight_unit_code VARCHAR(10), -- KG, LB
    height DECIMAL(7, 2),
    height_unit_code VARCHAR(10), -- CM, IN
    bmi DECIMAL(5, 2), -- Calculated

    -- Pain Assessment
    pain_score INT, -- 0-10 scale
    pain_location TEXT,

    -- Documentation
    measured_by BIGINT,
    documented_by BIGINT,
    documented_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Notes
    vital_signs_notes TEXT,

    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (encounter_id) REFERENCES encounter(encounter_id),
    FOREIGN KEY (measured_by) REFERENCES practitioner(provider_id),
    INDEX idx_patient (patient_id),
    INDEX idx_encounter (encounter_id),
    INDEX idx_measurement_datetime (measurement_datetime)
);
```

## Immunization Domain

### Immunization Table
Vaccination records.

```sql
CREATE TABLE immunization (
    immunization_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    patient_id BIGINT NOT NULL,
    encounter_id BIGINT,

    -- Vaccine Information
    vaccine_code VARCHAR(50) NOT NULL, -- CVX code
    vaccine_name VARCHAR(500) NOT NULL,
    vaccine_group_code VARCHAR(50), -- e.g., Influenza, COVID-19

    -- Administration Details
    administration_datetime TIMESTAMP NOT NULL,
    dose_number INT,
    doses_in_series INT,

    -- Route and Site
    route_code VARCHAR(50),
    site_code VARCHAR(50),
    site_description VARCHAR(200),

    -- Lot Information
    lot_number VARCHAR(50),
    manufacturer_name VARCHAR(200),
    expiration_date DATE,

    -- Dose Quantity
    dose_quantity DECIMAL(10, 3),
    dose_unit_code VARCHAR(20),

    -- Provider Information
    administering_provider_id BIGINT,
    ordering_provider_id BIGINT,

    -- Status
    immunization_status_code VARCHAR(20), -- COMPLETED, NOT_DONE
    not_given_reason TEXT,

    -- Information Source
    information_source_code VARCHAR(20), -- RECORD, HISTORICAL, REPORTED

    -- Documentation
    administration_notes TEXT,

    -- Registry Reporting
    reported_to_registry BOOLEAN DEFAULT FALSE,
    registry_report_datetime TIMESTAMP,

    -- Audit
    documented_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    documented_by VARCHAR(100),

    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (encounter_id) REFERENCES encounter(encounter_id),
    FOREIGN KEY (administering_provider_id) REFERENCES practitioner(provider_id),
    INDEX idx_patient (patient_id),
    INDEX idx_vaccine_code (vaccine_code),
    INDEX idx_administration_datetime (administration_datetime)
);
```

## Insurance and Financial

### Insurance_Coverage Table
Patient insurance information.

```sql
CREATE TABLE insurance_coverage (
    coverage_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    patient_id BIGINT NOT NULL,

    -- Coverage Priority
    coverage_priority INT, -- 1=Primary, 2=Secondary, etc.

    -- Payer Information
    payer_id VARCHAR(50),
    payer_name VARCHAR(200) NOT NULL,
    plan_name VARCHAR(200),
    plan_type_code VARCHAR(50), -- COMMERCIAL, MEDICARE, MEDICAID, etc.

    -- Policy Information
    policy_number VARCHAR(100),
    group_number VARCHAR(100),

    -- Subscriber Information
    subscriber_id VARCHAR(100),
    subscriber_name VARCHAR(200),
    relationship_to_subscriber_code VARCHAR(20), -- SELF, SPOUSE, CHILD, OTHER

    -- Coverage Period
    effective_date DATE NOT NULL,
    termination_date DATE,

    -- Verification
    last_verified_date DATE,
    verified_by VARCHAR(100),
    verification_status_code VARCHAR(20),

    -- Authorization
    authorization_required BOOLEAN DEFAULT FALSE,
    preauth_number VARCHAR(100),

    -- Status
    active_indicator BOOLEAN DEFAULT TRUE,

    -- Audit
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    INDEX idx_patient (patient_id),
    INDEX idx_policy_number (policy_number),
    INDEX idx_coverage_priority (patient_id, coverage_priority)
);
```

## Practitioner and Staff

### Practitioner Table
Healthcare providers and staff.

```sql
CREATE TABLE practitioner (
    provider_id BIGINT PRIMARY KEY AUTO_INCREMENT,

    -- Identification
    npi VARCHAR(10) UNIQUE, -- National Provider Identifier
    employee_id VARCHAR(50),

    -- Name
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    suffix VARCHAR(20),
    prefix VARCHAR(20),
    credentials VARCHAR(200), -- MD, DO, RN, etc.

    -- Demographics
    date_of_birth DATE,
    gender_code VARCHAR(10),

    -- Contact
    work_phone VARCHAR(50),
    mobile_phone VARCHAR(50),
    work_email VARCHAR(200),

    -- Professional Information
    primary_specialty_code VARCHAR(50),
    provider_type_code VARCHAR(50), -- PHYSICIAN, NP, PA, RN, etc.

    -- Credentials and Licenses
    license_number VARCHAR(100),
    license_state VARCHAR(10),
    license_expiration_date DATE,
    dea_number VARCHAR(50) ENCRYPTED,
    dea_expiration_date DATE,

    -- Status
    active_status BOOLEAN DEFAULT TRUE,

    -- Audit
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_npi (npi),
    INDEX idx_last_name (last_name),
    INDEX idx_specialty (primary_specialty_code)
);
```

## Organization and Location

### Facility Table
Healthcare facilities and locations.

```sql
CREATE TABLE facility (
    facility_id BIGINT PRIMARY KEY AUTO_INCREMENT,

    -- Identification
    facility_name VARCHAR(200) NOT NULL,
    facility_code VARCHAR(50) UNIQUE,
    npi VARCHAR(10), -- Facility NPI

    -- Facility Type
    facility_type_code VARCHAR(50), -- HOSPITAL, CLINIC, SNF, etc.

    -- Address
    street_line_1 VARCHAR(200),
    street_line_2 VARCHAR(200),
    city VARCHAR(100),
    state_code VARCHAR(10),
    postal_code VARCHAR(20),
    country_code VARCHAR(10),

    -- Contact
    main_phone VARCHAR(50),
    fax_number VARCHAR(50),

    -- Hierarchy
    parent_facility_id BIGINT,

    -- Status
    active_indicator BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (parent_facility_id) REFERENCES facility(facility_id),
    INDEX idx_facility_code (facility_code),
    INDEX idx_facility_type (facility_type_code)
);
```

## Best Practices for Data Modeling

### 1. Normalization
- Use appropriate normalization (typically 3NF for clinical data)
- Avoid over-normalization that impacts performance
- Denormalize strategically for read-heavy operations

### 2. Indexing Strategy
```sql
-- Composite indexes for common queries
CREATE INDEX idx_patient_encounter ON clinical_order(patient_id, encounter_id);
CREATE INDEX idx_patient_datetime ON lab_result(patient_id, result_datetime);

-- Covering indexes for frequent reports
CREATE INDEX idx_encounter_summary ON encounter(patient_id, encounter_class_code, admission_datetime)
    INCLUDE (discharge_datetime, attending_provider_id);
```

### 3. Audit Trails
All clinical tables should include:
- `created_datetime`
- `created_by`
- `modified_datetime`
- `modified_by`

### 4. Soft Deletes
Use `active_indicator` or `deleted_indicator` rather than hard deletes:
```sql
-- Instead of DELETE FROM patient WHERE patient_id = 123;
UPDATE patient SET active_status = FALSE, modified_datetime = CURRENT_TIMESTAMP WHERE patient_id = 123;
```

### 5. Code Value Management
Create reference tables for all coded fields:
```sql
CREATE TABLE code_value (
    code_value_id INT PRIMARY KEY AUTO_INCREMENT,
    code_set VARCHAR(100) NOT NULL, -- e.g., GENDER, MARITAL_STATUS
    code VARCHAR(50) NOT NULL,
    display VARCHAR(200) NOT NULL,
    description TEXT,
    active_indicator BOOLEAN DEFAULT TRUE,
    UNIQUE KEY uk_code (code_set, code)
);
```

### 6. Data Types
- Use appropriate precision for DECIMAL fields
- Use DATE for dates without time
- Use TIMESTAMP for date/time with timezone awareness
- Use TEXT for large text fields, VARCHAR for limited text
- Encrypt sensitive data (SSN, DEA numbers) at rest

### 7. Referential Integrity
- Always use foreign keys for relationships
- Use CASCADE or RESTRICT appropriately
- Consider application-level checks for complex constraints

## References

- **HL7 FHIR Data Models**: http://hl7.org/fhir/R4/
- **OHDSI Common Data Model**: https://ohdsi.github.io/CommonDataModel/
- **OMOP Common Data Model**: Observational Medical Outcomes Partnership
- **Clinical Data Interchange Standards Consortium (CDISC)**: https://www.cdisc.org/

---

**Document Version**: 1.0
**Last Updated**: November 2024
**Author**: Healthcare Technology Team
**Classification**: Public - Educational Use
