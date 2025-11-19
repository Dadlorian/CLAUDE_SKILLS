# OMOP CDM Implementation Guide

## Implementation Overview

The OMOP Common Data Model implementation transforms healthcare data from source systems into a standardized research-ready format for observational studies.

## Phase 1: Planning

### Requirements Definition
- Define research use cases
- Identify data sources (EHR, claims, labs, pharmacy)
- Determine OMOP CDM version (recommend latest: v5.4)
- Select vocabulary version
- Plan infrastructure (database platform, storage)

### Team Structure
- Clinical SME (vocabulary mapping, validation)
- Data Engineer (ETL development)
- Database Administrator
- Analyst/Researcher (validation, use case testing)

## Phase 2: Environment Setup

### Database Setup

**PostgreSQL (Recommended for OMOP):**
```sql
-- Create OMOP schema
CREATE SCHEMA omop_cdm;
CREATE SCHEMA omop_vocab;
CREATE SCHEMA omop_results;

-- Create tables using OHDSI DDL scripts
-- Download from: https://github.com/OHDSI/CommonDataModel
\i OMOPCDM_postgresql_5.4_ddl.sql
\i OMOPCDM_postgresql_5.4_primary_keys.sql
\i OMOPCDM_postgresql_5.4_indices.sql
\i OMOPCDM_postgresql_5.4_constraints.sql
```

### Vocabulary Installation

1. Download vocabularies from Athena: https://athena.ohdsi.org
2. Select vocabularies: SNOMED, RxNorm, LOINC, ICD10CM, CPT4, etc.
3. Load vocabulary files:

```bash
# Load vocabulary CSV files
psql -d omop_db -c "\copy omop_vocab.concept FROM 'CONCEPT.csv' CSV HEADER"
psql -d omop_db -c "\copy omop_vocab.concept_relationship FROM 'CONCEPT_RELATIONSHIP.csv' CSV HEADER"
psql -d omop_db -c "\copy omop_vocab.concept_ancestor FROM 'CONCEPT_ANCESTOR.csv' CSV HEADER"
psql -d omop_db -c "\copy omop_vocab.vocabulary FROM 'VOCABULARY.csv' CSV HEADER"
```

## Phase 3: Mapping & ETL

### Vocabulary Mapping

**Map ICD-10 to SNOMED:**
```sql
SELECT
    c_source.concept_id AS source_concept_id,
    c_source.concept_code AS icd10_code,
    c_source.concept_name AS icd10_name,
    c_standard.concept_id AS standard_concept_id,
    c_standard.concept_code AS snomed_code,
    c_standard.concept_name AS snomed_name
FROM concept c_source
JOIN concept_relationship cr
    ON c_source.concept_id = cr.concept_id_1
    AND cr.relationship_id = 'Maps to'
JOIN concept c_standard
    ON cr.concept_id_2 = c_standard.concept_id
WHERE c_source.vocabulary_id = 'ICD10CM'
    AND c_source.concept_code = 'E11.9'
    AND c_standard.standard_concept = 'S';
```

**Create Local Mapping Tables:**
```sql
CREATE TABLE source_to_concept_map_custom (
    source_code VARCHAR(50),
    source_vocabulary_id VARCHAR(20),
    source_concept_id INT,
    target_concept_id INT,
    target_vocabulary_id VARCHAR(20),
    valid_start_date DATE,
    valid_end_date DATE,
    mapping_type VARCHAR(20)
);
```

### ETL to OMOP

See reference files and code examples for detailed ETL implementations.

## Phase 4: Quality Assurance

### Run ACHILLES

```r
library(Achilles)

connectionDetails <- createConnectionDetails(
    dbms = "postgresql",
    server = "localhost/omop_db",
    user = "omop_user",
    password = Sys.getenv("OMOP_PASSWORD")
)

achilles(
    connectionDetails = connectionDetails,
    cdmDatabaseSchema = "omop_cdm",
    vocabDatabaseSchema = "omop_vocab",
    resultsDatabaseSchema = "omop_results",
    sourceName = "My Health System OMOP",
    cdmVersion = "5.4",
    runHeel = TRUE
)
```

### Data Quality Dashboard

Deploy OHDSI Data Quality Dashboard to visualize ACHILLES results.

## Phase 5: Validation

### Cohort Definition Testing
- Define test cohorts in ATLAS
- Validate against known patient lists
- Chart review for sample

### Compare to Source
- Row counts
- Patient counts
- Key metrics (encounters, diagnoses, medications)

## Best Practices

1. **Preserve Source Data**: Always populate *_source_value fields
2. **Standard Concepts Only**: Use only standard concepts in *_concept_id fields
3. **Visit Linkage**: Link all events to visit_occurrence when possible
4. **Temporal Consistency**: Ensure dates fall within observation periods
5. **Documentation**: Document all mapping decisions and custom concepts

---

*OMOP CDM Implementation Guide*
