# OMOP Common Data Model Reference

## Overview

The Observational Medical Outcomes Partnership (OMOP) Common Data Model (CDM) is a standardized data model developed by OHDSI (Observational Health Data Sciences and Informatics) to enable collaborative research across disparate observational databases.

## Core Principles

### Standardization Benefits

1. **Vocabulary Harmonization**: Convert local codes to standard concepts
2. **Reproducible Research**: Same analysis can run across multiple sites
3. **Network Studies**: Multi-institutional collaborative research
4. **Tool Ecosystem**: ATLAS, ACHILLES, and other OHDSI tools
5. **Evidence Generation**: Observational studies, safety surveillance

### Design Philosophy

- **Person-centric**: Patient as the unit of observation
- **Visit-centric**: Events occur within visit context
- **Concept-based**: Standardized vocabularies for interoperability
- **Temporal**: Precise dating of clinical events
- **Source preservation**: Retain source codes alongside standard concepts

## OMOP CDM v5.4 Schema

### Clinical Data Tables

#### PERSON
```sql
CREATE TABLE person (
    person_id BIGINT PRIMARY KEY,
    gender_concept_id INTEGER,              -- Standard concept from CONCEPT table
    year_of_birth INTEGER,
    month_of_birth INTEGER,
    day_of_birth INTEGER,
    birth_datetime TIMESTAMP,
    race_concept_id INTEGER,
    ethnicity_concept_id INTEGER,
    location_id INTEGER,
    provider_id INTEGER,
    care_site_id INTEGER,
    person_source_value VARCHAR(50),        -- Original person ID from source
    gender_source_value VARCHAR(50),
    gender_source_concept_id INTEGER,
    race_source_value VARCHAR(50),
    race_source_concept_id INTEGER,
    ethnicity_source_value VARCHAR(50),
    ethnicity_source_concept_id INTEGER
);
```

**Key Concepts:**
- `person_id`: Unique identifier for the person (de-identified)
- `*_concept_id`: Standard concepts (e.g., 8507 for Male, 8532 for Female)
- `*_source_value`: Original value from source system
- `*_source_concept_id`: If source value maps to a concept

#### OBSERVATION_PERIOD
```sql
CREATE TABLE observation_period (
    observation_period_id BIGINT PRIMARY KEY,
    person_id BIGINT,
    observation_period_start_date DATE,
    observation_period_end_date DATE,
    period_type_concept_id INTEGER          -- How period was determined
);
```

**Purpose**: Define time periods when patient data is observable (enrollment, coverage)

#### VISIT_OCCURRENCE
```sql
CREATE TABLE visit_occurrence (
    visit_occurrence_id BIGINT PRIMARY KEY,
    person_id BIGINT,
    visit_concept_id INTEGER,               -- 9201: Inpatient, 9202: Outpatient, 9203: ED
    visit_start_date DATE,
    visit_start_datetime TIMESTAMP,
    visit_end_date DATE,
    visit_end_datetime TIMESTAMP,
    visit_type_concept_id INTEGER,          -- How visit was recorded (EHR, Claims)
    provider_id INTEGER,
    care_site_id INTEGER,
    visit_source_value VARCHAR(50),
    visit_source_concept_id INTEGER,
    admitted_from_concept_id INTEGER,       -- Admission source
    admitted_from_source_value VARCHAR(50),
    discharged_to_concept_id INTEGER,       -- Discharge disposition
    discharged_to_source_value VARCHAR(50),
    preceding_visit_occurrence_id BIGINT    -- Link to prior visit
);
```

#### CONDITION_OCCURRENCE
```sql
CREATE TABLE condition_occurrence (
    condition_occurrence_id BIGINT PRIMARY KEY,
    person_id BIGINT,
    condition_concept_id INTEGER,           -- Standard SNOMED concept
    condition_start_date DATE,
    condition_start_datetime TIMESTAMP,
    condition_end_date DATE,
    condition_end_datetime TIMESTAMP,
    condition_type_concept_id INTEGER,      -- EHR diagnosis, billing code, etc.
    condition_status_concept_id INTEGER,    -- Primary, secondary, etc.
    stop_reason VARCHAR(20),
    provider_id INTEGER,
    visit_occurrence_id BIGINT,
    visit_detail_id BIGINT,
    condition_source_value VARCHAR(50),     -- Original ICD-10 code
    condition_source_concept_id INTEGER,    -- ICD-10 concept
    condition_status_source_value VARCHAR(50)
);
```

**Example Mapping:**
- Source: ICD-10 code "E11.9" (Type 2 diabetes without complications)
- Standard: SNOMED concept 44054006 (Diabetes mellitus type 2)

#### DRUG_EXPOSURE
```sql
CREATE TABLE drug_exposure (
    drug_exposure_id BIGINT PRIMARY KEY,
    person_id BIGINT,
    drug_concept_id INTEGER,                -- Standard RxNorm Ingredient
    drug_exposure_start_date DATE,
    drug_exposure_start_datetime TIMESTAMP,
    drug_exposure_end_date DATE,
    drug_exposure_end_datetime TIMESTAMP,
    verbatim_end_date DATE,
    drug_type_concept_id INTEGER,           -- Prescription, dispensing, administration
    stop_reason VARCHAR(20),
    refills INTEGER,
    quantity NUMERIC,
    days_supply INTEGER,
    sig TEXT,                                -- Prescription instructions
    route_concept_id INTEGER,
    lot_number VARCHAR(50),
    provider_id INTEGER,
    visit_occurrence_id BIGINT,
    visit_detail_id BIGINT,
    drug_source_value VARCHAR(50),          -- NDC code
    drug_source_concept_id INTEGER,
    route_source_value VARCHAR(50),
    dose_unit_source_value VARCHAR(50)
);
```

**RxNorm Hierarchy:**
- Ingredient (standard): "Metformin"
- Clinical Drug: "Metformin 500 MG Oral Tablet"
- Branded Drug: "Glucophage 500 MG Oral Tablet"

#### PROCEDURE_OCCURRENCE
```sql
CREATE TABLE procedure_occurrence (
    procedure_occurrence_id BIGINT PRIMARY KEY,
    person_id BIGINT,
    procedure_concept_id INTEGER,           -- Standard SNOMED procedure
    procedure_date DATE,
    procedure_datetime TIMESTAMP,
    procedure_end_date DATE,
    procedure_end_datetime TIMESTAMP,
    procedure_type_concept_id INTEGER,      -- Primary procedure, billing, etc.
    modifier_concept_id INTEGER,
    quantity INTEGER,
    provider_id INTEGER,
    visit_occurrence_id BIGINT,
    visit_detail_id BIGINT,
    procedure_source_value VARCHAR(50),     -- CPT, ICD-10-PCS code
    procedure_source_concept_id INTEGER,
    modifier_source_value VARCHAR(50)
);
```

#### MEASUREMENT
```sql
CREATE TABLE measurement (
    measurement_id BIGINT PRIMARY KEY,
    person_id BIGINT,
    measurement_concept_id INTEGER,         -- Standard LOINC concept
    measurement_date DATE,
    measurement_datetime TIMESTAMP,
    measurement_time VARCHAR(10),
    measurement_type_concept_id INTEGER,    -- Lab, vital sign, etc.
    operator_concept_id INTEGER,            -- =, <, >, etc.
    value_as_number NUMERIC,
    value_as_concept_id INTEGER,            -- For categorical results
    unit_concept_id INTEGER,                -- Standard unit (mg/dL, mmol/L)
    range_low NUMERIC,
    range_high NUMERIC,
    provider_id INTEGER,
    visit_occurrence_id BIGINT,
    visit_detail_id BIGINT,
    measurement_source_value VARCHAR(50),   -- Original LOINC code
    measurement_source_concept_id INTEGER,
    unit_source_value VARCHAR(50),
    unit_source_concept_id INTEGER,
    value_source_value VARCHAR(50),
    measurement_event_id BIGINT,
    meas_event_field_concept_id INTEGER
);
```

**Common LOINC Concepts:**
- 2345-7: Glucose [Mass/volume] in Serum or Plasma
- 4548-4: Hemoglobin A1c/Hemoglobin.total in Blood
- 2160-0: Creatinine [Mass/volume] in Serum or Plasma

#### OBSERVATION
```sql
CREATE TABLE observation (
    observation_id BIGINT PRIMARY KEY,
    person_id BIGINT,
    observation_concept_id INTEGER,
    observation_date DATE,
    observation_datetime TIMESTAMP,
    observation_type_concept_id INTEGER,
    value_as_number NUMERIC,
    value_as_string VARCHAR(60),
    value_as_concept_id INTEGER,
    qualifier_concept_id INTEGER,
    unit_concept_id INTEGER,
    provider_id INTEGER,
    visit_occurrence_id BIGINT,
    visit_detail_id BIGINT,
    observation_source_value VARCHAR(50),
    observation_source_concept_id INTEGER,
    unit_source_value VARCHAR(50),
    qualifier_source_value VARCHAR(50),
    value_source_value VARCHAR(50),
    observation_event_id BIGINT,
    obs_event_field_concept_id INTEGER
);
```

**Use Cases:**
- Social history (smoking status, alcohol use)
- Family history
- Patient-reported outcomes
- Observations not fitting other domains

#### DEATH
```sql
CREATE TABLE death (
    person_id BIGINT PRIMARY KEY,
    death_date DATE,
    death_datetime TIMESTAMP,
    death_type_concept_id INTEGER,          -- Source of death information
    cause_concept_id INTEGER,               -- Primary cause of death
    cause_source_value VARCHAR(50),
    cause_source_concept_id INTEGER
);
```

### Health System Tables

#### LOCATION
```sql
CREATE TABLE location (
    location_id BIGINT PRIMARY KEY,
    address_1 VARCHAR(50),
    address_2 VARCHAR(50),
    city VARCHAR(50),
    state VARCHAR(2),
    zip VARCHAR(9),
    county VARCHAR(20),
    location_source_value VARCHAR(50),
    country_concept_id INTEGER,
    country_source_value VARCHAR(80),
    latitude NUMERIC,
    longitude NUMERIC
);
```

#### CARE_SITE
```sql
CREATE TABLE care_site (
    care_site_id BIGINT PRIMARY KEY,
    care_site_name VARCHAR(255),
    place_of_service_concept_id INTEGER,
    location_id INTEGER,
    care_site_source_value VARCHAR(50),
    place_of_service_source_value VARCHAR(50)
);
```

#### PROVIDER
```sql
CREATE TABLE provider (
    provider_id BIGINT PRIMARY KEY,
    provider_name VARCHAR(255),
    npi VARCHAR(20),
    dea VARCHAR(20),
    specialty_concept_id INTEGER,
    care_site_id INTEGER,
    year_of_birth INTEGER,
    gender_concept_id INTEGER,
    provider_source_value VARCHAR(50),
    specialty_source_value VARCHAR(50),
    specialty_source_concept_id INTEGER,
    gender_source_value VARCHAR(50),
    gender_source_concept_id INTEGER
);
```

### Vocabulary Tables

#### CONCEPT
```sql
CREATE TABLE concept (
    concept_id INTEGER PRIMARY KEY,
    concept_name VARCHAR(255),
    domain_id VARCHAR(20),                  -- Condition, Drug, Procedure, etc.
    vocabulary_id VARCHAR(20),              -- SNOMED, RxNorm, LOINC, etc.
    concept_class_id VARCHAR(20),
    standard_concept VARCHAR(1),            -- 'S' for standard, 'C' for classification
    concept_code VARCHAR(50),               -- Original code in vocabulary
    valid_start_date DATE,
    valid_end_date DATE,
    invalid_reason VARCHAR(1)               -- 'D' deprecated, 'U' updated
);
```

**Example:**
```
concept_id: 201826
concept_name: Type 2 diabetes mellitus
domain_id: Condition
vocabulary_id: SNOMED
concept_class_id: Clinical Finding
standard_concept: S
concept_code: 44054006
```

#### CONCEPT_RELATIONSHIP
```sql
CREATE TABLE concept_relationship (
    concept_id_1 INTEGER,
    concept_id_2 INTEGER,
    relationship_id VARCHAR(20),            -- Maps to, Is a, Subsumes, etc.
    valid_start_date DATE,
    valid_end_date DATE,
    invalid_reason VARCHAR(1),
    PRIMARY KEY (concept_id_1, concept_id_2, relationship_id)
);
```

**Common Relationships:**
- "Maps to": Source concept → Standard concept
- "Is a": Hierarchical (child → parent)
- "Subsumes": Hierarchical (parent → child)
- "RxNorm has ing": Drug → Ingredient

#### CONCEPT_ANCESTOR
```sql
CREATE TABLE concept_ancestor (
    ancestor_concept_id INTEGER,
    descendant_concept_id INTEGER,
    min_levels_of_separation INTEGER,
    max_levels_of_separation INTEGER,
    PRIMARY KEY (ancestor_concept_id, descendant_concept_id)
);
```

**Use**: Efficient hierarchical queries (all descendants of "Diabetes mellitus")

#### VOCABULARY
```sql
CREATE TABLE vocabulary (
    vocabulary_id VARCHAR(20) PRIMARY KEY,
    vocabulary_name VARCHAR(255),
    vocabulary_reference VARCHAR(255),
    vocabulary_version VARCHAR(255),
    vocabulary_concept_id INTEGER
);
```

**Standard Vocabularies:**
- SNOMED: Clinical conditions, procedures, findings
- RxNorm: Medications (US-centric)
- LOINC: Laboratory and clinical observations
- CPT4: Procedures (US billing)
- ICD10CM: Diagnoses (US)
- ICD10PCS: Procedures (US inpatient)

## OMOP Vocabulary Mapping

### Source to Standard Concept Mapping

```sql
-- Find standard concept for ICD-10 code E11.9
SELECT
    c1.concept_id AS source_concept_id,
    c1.concept_code AS source_code,
    c1.concept_name AS source_name,
    c2.concept_id AS standard_concept_id,
    c2.concept_code AS standard_code,
    c2.concept_name AS standard_name
FROM concept c1
JOIN concept_relationship cr
    ON c1.concept_id = cr.concept_id_1
    AND cr.relationship_id = 'Maps to'
JOIN concept c2
    ON cr.concept_id_2 = c2.concept_id
WHERE c1.vocabulary_id = 'ICD10CM'
    AND c1.concept_code = 'E11.9'
    AND c2.standard_concept = 'S';
```

**Result:**
```
source_concept_id: 45571916
source_code: E11.9
source_name: Type 2 diabetes mellitus without complications
standard_concept_id: 201826
standard_code: 44054006
standard_name: Type 2 diabetes mellitus
```

### Hierarchical Queries

```sql
-- Find all descendants of "Diabetes mellitus" (concept_id 201820)
SELECT
    c.concept_id,
    c.concept_name,
    ca.min_levels_of_separation
FROM concept_ancestor ca
JOIN concept c ON ca.descendant_concept_id = c.concept_id
WHERE ca.ancestor_concept_id = 201820
    AND c.standard_concept = 'S'
ORDER BY ca.min_levels_of_separation, c.concept_name;
```

### Drug Ingredient Rollup

```sql
-- Find all medications containing Metformin (concept_id 1503297)
SELECT DISTINCT
    c.concept_id,
    c.concept_name,
    c.concept_class_id
FROM concept c
JOIN concept_ancestor ca ON c.concept_id = ca.descendant_concept_id
WHERE ca.ancestor_concept_id = 1503297  -- Metformin ingredient
    AND c.standard_concept = 'S'
    AND c.concept_class_id IN ('Clinical Drug', 'Branded Drug');
```

## ETL to OMOP CDM

### General ETL Approach

```
1. Extract: Pull data from source system (EHR, claims)
2. Staging: Load raw data into staging tables
3. Vocabulary Mapping: Map source codes to standard concepts
4. Transform: Convert to OMOP CDM structure
5. Load: Insert into OMOP CDM tables
6. Validate: Run data quality checks (ACHILLES)
```

### Example: ICD-10 to OMOP Condition

```python
# Pseudocode for ETL
def etl_conditions(source_diagnoses):
    for diagnosis in source_diagnoses:
        # Map ICD-10 to standard SNOMED concept
        standard_concept = map_to_standard(
            diagnosis.icd10_code,
            'ICD10CM'
        )

        # Insert into CONDITION_OCCURRENCE
        insert_condition_occurrence(
            person_id=get_person_id(diagnosis.patient_mrn),
            condition_concept_id=standard_concept.concept_id,
            condition_start_date=diagnosis.diagnosis_date,
            condition_type_concept_id=32020,  # EHR diagnosis
            visit_occurrence_id=get_visit_id(diagnosis.encounter_id),
            condition_source_value=diagnosis.icd10_code,
            condition_source_concept_id=standard_concept.source_concept_id
        )
```

### ETL Best Practices

1. **Preserve Source Values**: Always populate `*_source_value` and `*_source_concept_id`
2. **Type Concepts**: Use appropriate `*_type_concept_id` to indicate data provenance
3. **Visit Linkage**: Link all events to `visit_occurrence_id` when possible
4. **Standard Concepts Only**: `*_concept_id` fields must reference standard concepts
5. **Temporal Consistency**: Ensure event dates fall within observation periods
6. **Vocabularies**: Keep vocabularies updated (OHDSI releases quarterly)

## OHDSI Tools Ecosystem

### ATLAS

Web-based cohort definition and analysis tool.

**Key Features:**
- Cohort Definition: Visual cohort builder
- Characterization: Describe cohort demographics, conditions, drugs
- Cohort Pathways: Visualize treatment sequences
- Incidence Rates: Calculate disease incidence
- Population-Level Estimation: Comparative effectiveness
- Patient-Level Prediction: Build predictive models

**Cohort Definition Example:**
```json
{
  "ConceptSets": [
    {
      "id": 0,
      "name": "Type 2 Diabetes",
      "expression": {
        "items": [
          {
            "concept": {
              "CONCEPT_ID": 201826,
              "CONCEPT_NAME": "Type 2 diabetes mellitus"
            },
            "includeDescendants": true
          }
        ]
      }
    }
  ],
  "PrimaryCriteria": {
    "CriteriaList": [
      {
        "ConditionOccurrence": {
          "CodesetId": 0
        }
      }
    ]
  }
}
```

### ACHILLES

Automated Characterization of Health Information at Large-scale Longitudinal Evidence Systems.

**Purpose**: Data quality assessment and database profiling

**Analyses:**
- Data density (records over time)
- Vocabulary distribution
- Completeness metrics
- Temporal coherence checks
- Orphaned records detection

**Run ACHILLES:**
```r
library(Achilles)

connectionDetails <- createConnectionDetails(
  dbms = "postgresql",
  server = "localhost/omop",
  user = "omop_user",
  password = "password"
)

achilles(
  connectionDetails = connectionDetails,
  cdmDatabaseSchema = "omop_cdm",
  resultsDatabaseSchema = "omop_results",
  sourceName = "My Healthcare System",
  cdmVersion = "5.4"
)
```

### Data Quality Dashboard

Visual representation of ACHILLES results.

**Metrics:**
- Conformance: Data adheres to OMOP CDM structure
- Completeness: Required fields populated
- Plausibility: Values within expected ranges
- Temporal: Dates logically consistent

### SQLRender

Translates SQL across different database platforms.

```r
library(SqlRender)

sql <- "SELECT TOP 100 * FROM @cdm_database.person;"

renderedSql <- render(
  sql,
  cdm_database = "omop_cdm"
)

translatedSql <- translate(
  renderedSql,
  targetDialect = "postgresql"  # or oracle, redshift, etc.
)
```

### DatabaseConnector

R package for connecting to various database platforms.

```r
library(DatabaseConnector)

connection <- connect(connectionDetails)

querySql(
  connection,
  "SELECT COUNT(*) FROM omop_cdm.person;"
)

disconnect(connection)
```

## Common Cohort Definitions

### Type 2 Diabetes Cohort

```sql
-- Patients with Type 2 Diabetes diagnosis
SELECT DISTINCT p.person_id
FROM person p
JOIN condition_occurrence co ON p.person_id = co.person_id
JOIN concept_ancestor ca ON co.condition_concept_id = ca.descendant_concept_id
WHERE ca.ancestor_concept_id = 201826  -- Type 2 diabetes mellitus
    AND co.condition_start_date >= '2020-01-01';
```

### Patients on Metformin

```sql
-- Patients with Metformin exposure in 2023
SELECT DISTINCT p.person_id
FROM person p
JOIN drug_exposure de ON p.person_id = de.person_id
JOIN concept_ancestor ca ON de.drug_concept_id = ca.descendant_concept_id
WHERE ca.ancestor_concept_id = 1503297  -- Metformin ingredient
    AND de.drug_exposure_start_date BETWEEN '2023-01-01' AND '2023-12-31';
```

### Hospitalized COVID-19 Patients

```sql
-- COVID-19 patients with inpatient admission
SELECT DISTINCT p.person_id, v.visit_start_date
FROM person p
JOIN condition_occurrence co ON p.person_id = co.person_id
JOIN visit_occurrence v ON co.visit_occurrence_id = v.visit_occurrence_id
JOIN concept_ancestor ca ON co.condition_concept_id = ca.descendant_concept_id
WHERE ca.ancestor_concept_id = 37311061  -- Disease caused by 2019-nCoV
    AND v.visit_concept_id = 9201  -- Inpatient visit
    AND v.visit_start_date >= '2020-03-01';
```

## Phenotype Algorithms

### Diabetes with Complications Phenotype

```sql
-- T2DM patients with diabetic kidney disease
SELECT DISTINCT
    p.person_id,
    MIN(co1.condition_start_date) AS t2dm_index_date,
    MIN(co2.condition_start_date) AS ckd_date
FROM person p
-- Type 2 Diabetes
JOIN condition_occurrence co1 ON p.person_id = co1.person_id
JOIN concept_ancestor ca1 ON co1.condition_concept_id = ca1.descendant_concept_id
    AND ca1.ancestor_concept_id = 201826
-- Chronic Kidney Disease
JOIN condition_occurrence co2 ON p.person_id = co2.person_id
JOIN concept_ancestor ca2 ON co2.condition_concept_id = ca2.descendant_concept_id
    AND ca2.ancestor_concept_id = 46271022  -- Chronic kidney disease
WHERE co2.condition_start_date >= co1.condition_start_date
GROUP BY p.person_id
HAVING COUNT(DISTINCT co1.condition_occurrence_id) >= 2
    AND COUNT(DISTINCT co2.condition_occurrence_id) >= 1;
```

### Acute Myocardial Infarction (AMI)

```sql
-- AMI phenotype: inpatient with AMI diagnosis in primary position
SELECT DISTINCT
    p.person_id,
    v.visit_occurrence_id,
    v.visit_start_date AS ami_date
FROM person p
JOIN visit_occurrence v ON p.person_id = v.person_id
JOIN condition_occurrence co ON v.visit_occurrence_id = co.visit_occurrence_id
JOIN concept_ancestor ca ON co.condition_concept_id = ca.descendant_concept_id
WHERE ca.ancestor_concept_id = 4329847  -- Myocardial infarction
    AND v.visit_concept_id = 9201  -- Inpatient
    AND co.condition_type_concept_id IN (32020, 32840);  -- Primary diagnosis
```

## OMOP Performance Optimization

### Indexing Strategy

```sql
-- Primary keys (created automatically)
-- Foreign keys for joining
CREATE INDEX idx_condition_person ON condition_occurrence(person_id);
CREATE INDEX idx_condition_concept ON condition_occurrence(condition_concept_id);
CREATE INDEX idx_condition_visit ON condition_occurrence(visit_occurrence_id);
CREATE INDEX idx_condition_date ON condition_occurrence(condition_start_date);

-- Similar indexes for all event tables
CREATE INDEX idx_drug_person ON drug_exposure(person_id);
CREATE INDEX idx_drug_concept ON drug_exposure(drug_concept_id);
CREATE INDEX idx_procedure_person ON procedure_occurrence(person_id);
CREATE INDEX idx_measurement_person ON measurement(person_id);

-- Concept_ancestor is heavily queried
CREATE INDEX idx_concept_ancestor_ancestor ON concept_ancestor(ancestor_concept_id);
CREATE INDEX idx_concept_ancestor_descendant ON concept_ancestor(descendant_concept_id);
```

### Partitioning

```sql
-- Partition large tables by date
CREATE TABLE condition_occurrence_partitioned (
    LIKE condition_occurrence
)
PARTITION BY RANGE (condition_start_date);

CREATE TABLE condition_occurrence_2020
    PARTITION OF condition_occurrence_partitioned
    FOR VALUES FROM ('2020-01-01') TO ('2021-01-01');

CREATE TABLE condition_occurrence_2021
    PARTITION OF condition_occurrence_partitioned
    FOR VALUES FROM ('2021-01-01') TO ('2022-01-01');
```

## OMOP CDM Extensions

### Custom Concepts

For institution-specific concepts not in standard vocabularies:

```sql
-- Insert custom concepts (concept_id >= 2000000000)
INSERT INTO concept (
    concept_id, concept_name, domain_id, vocabulary_id,
    concept_class_id, standard_concept, concept_code,
    valid_start_date, valid_end_date
) VALUES (
    2000000001,
    'Custom Risk Score',
    'Observation',
    'Local',
    'Clinical Observation',
    'S',
    'RISK_001',
    '2024-01-01',
    '2099-12-31'
);
```

### OMOP Oncology Extension

Specialized tables for cancer research:
- EPISODE: Cancer diagnosis episodes
- EPISODE_EVENT: Events associated with episodes
- Extended MEASUREMENT: Biomarkers, genomic tests

---

*OMOP CDM Reference - Standardized data model enabling multi-site observational research and evidence generation.*
