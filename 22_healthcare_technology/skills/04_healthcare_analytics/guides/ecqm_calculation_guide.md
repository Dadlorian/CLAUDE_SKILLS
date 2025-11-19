# eCQM Calculation Guide

## eCQM Overview

Electronic Clinical Quality Measures (eCQMs) are quality measures calculated directly from structured EHR data using standard specifications.

## eCQM Components

### Population Criteria

1. **Initial Population (IP)**: All patients/encounters eligible for measure
2. **Denominator (DENOM)**: Subset of IP meeting specific criteria
3. **Denominator Exclusions (DENEX)**: Remove from denominator (e.g., hospice)
4. **Denominator Exceptions (DENEXCEP)**: Clinically appropriate reasons for not meeting measure
5. **Numerator (NUMER)**: Patients/encounters meeting quality action
6. **Numerator Exclusions (NUMEX)**: Remove from numerator (rarely used)

### Rate Calculation

```
Performance Rate = NUMER / (DENOM - DENEX - DENEXCEP)
```

## Implementing eCQM Logic

### CQL (Clinical Quality Language)

```cql
library CMS122 version '11.0.000'
using QDM version '5.6'

valueset "Diabetes": '2.16.840.1.113883.3.464.1003.103.12.1001'
valueset "HbA1c Laboratory Test": '2.16.840.1.113883.3.464.1003.198.12.1013'

parameter "Measurement Period" Interval<DateTime>

define "Initial Population":
  AgeInYearsAt(start of "Measurement Period") >= 18
    and AgeInYearsAt(start of "Measurement Period") < 75
    and exists "Qualifying Encounters"
    and exists "Diabetes Diagnosis"

define "Denominator":
  "Initial Population"

define "Denominator Exclusions":
  "Has Hospice Care"

define "Numerator":
  "Has Most Recent HbA1c Greater Than 9"

define "Has Most Recent HbA1c Greater Than 9":
  "Most Recent HbA1c" >= 9 '%'
```

### SQL Implementation

```sql
-- CMS122: Diabetes HbA1c Poor Control
WITH initial_population AS (
    SELECT DISTINCT p.patient_key
    FROM dim_patient p
    WHERE p.age_at_year_end BETWEEN 18 AND 75
        AND EXISTS (
            SELECT 1 FROM fact_diagnosis d
            WHERE d.patient_key = p.patient_key
                AND d.diagnosis_code IN (SELECT code FROM valueset_diabetes)
                AND d.diagnosis_date BETWEEN '2023-01-01' AND '2023-12-31'
        )
),
denominator AS (
    SELECT patient_key FROM initial_population
    WHERE NOT EXISTS (
        -- Exclude hospice patients
        SELECT 1 FROM fact_encounter e
        WHERE e.patient_key = initial_population.patient_key
            AND e.hospice_flag = TRUE
    )
),
numerator AS (
    SELECT d.patient_key
    FROM denominator d
    JOIN LATERAL (
        SELECT result_numeric
        FROM fact_lab_result l
        WHERE l.patient_key = d.patient_key
            AND l.lab_test_code = '4548-4'  -- HbA1c LOINC
            AND l.result_date BETWEEN '2023-01-01' AND '2023-12-31'
        ORDER BY l.result_date DESC
        LIMIT 1
    ) latest_hba1c ON TRUE
    WHERE latest_hba1c.result_numeric > 9.0
)
SELECT
    (SELECT COUNT(*) FROM denominator) AS denominator_count,
    (SELECT COUNT(*) FROM numerator) AS numerator_count,
    ROUND(100.0 * (SELECT COUNT(*) FROM numerator) / (SELECT COUNT(*) FROM denominator), 2) AS performance_rate;
```

## eCQM Calculation Engine

See code examples for full implementation.

## Validation & Reporting

### Measure Validation
1. Test on known cohorts
2. Chart review sample (10-20 patients)
3. Compare to prior year results
4. Validate edge cases

### QRDA Reporting
- Generate QRDA Category I (patient-level)
- Generate QRDA Category III (aggregate)
- Submit to quality programs

---

*eCQM Calculation Guide*
