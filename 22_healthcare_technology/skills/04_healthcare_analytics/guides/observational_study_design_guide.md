# Observational Study Design Guide

## Study Design Selection

### Cohort Study
**When to use**: Assess effect of exposure on outcome over time
**Example**: Compare cardiovascular outcomes for SGLT2i vs. DPP-4i in T2DM patients

### Case-Control Study
**When to use**: Investigate cause of rare outcome
**Example**: Identify risk factors for rare adverse drug reaction

### Cross-Sectional Study
**When to use**: Describe prevalence at a point in time
**Example**: Current diabetes treatment patterns

## Study Implementation Steps

### 1. Define Research Question
- Population of interest
- Exposure/intervention
- Outcome
- Time frame

### 2. Cohort Definition
```sql
-- Define exposed cohort
WITH exposed AS (
    SELECT DISTINCT patient_id, first_exposure_date AS index_date
    FROM drug_exposure
    WHERE drug_concept_id IN (SELECT concept_id FROM sglt2i_concepts)
        AND first_exposure_date BETWEEN '2020-01-01' AND '2022-12-31'
),
-- Define comparator cohort
comparator AS (
    SELECT DISTINCT patient_id, first_exposure_date AS index_date
    FROM drug_exposure
    WHERE drug_concept_id IN (SELECT concept_id FROM dpp4i_concepts)
        AND first_exposure_date BETWEEN '2020-01-01' AND '2022-12-31'
)
```

### 3. Apply Inclusion/Exclusion Criteria
```python
criteria = {
    'inclusion': [
        'age >= 18',
        'diabetes_diagnosis_before_index',
        'continuous_enrollment_pre_6mo',
        'continuous_enrollment_post_12mo'
    ],
    'exclusion': [
        'prior_exposure_either_drug',
        'pregnancy',
        'esrd',
        'hospice'
    ]
}
```

### 4. Matching/Balancing
- Propensity score matching
- Stratification
- Inverse probability weighting

### 5. Follow-Up & Outcome Assessment
- Define follow-up period
- Identify outcome events
- Censor at disenrollment or death

### 6. Statistical Analysis
- Survival analysis (Kaplan-Meier, Cox PH)
- Risk ratios, hazard ratios
- Confidence intervals

### 7. Sensitivity Analysis
- Vary definitions
- Different matching strategies
- Subgroup analyses

---

*Observational Study Design Guide*
