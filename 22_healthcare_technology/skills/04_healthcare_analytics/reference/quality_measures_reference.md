# Quality Measures Reference (HEDIS, MIPS, eCQM)

## Overview

Healthcare quality measures are standardized metrics used to assess the quality of care delivered by healthcare providers and systems. Key measure sets include HEDIS (health plan quality), MIPS (physician payment), and eCQM (electronic clinical quality measures).

## HEDIS (Healthcare Effectiveness Data and Information Set)

### Overview

**Purpose**: Standardized performance measures for health plans
**Managed by**: NCQA (National Committee for Quality Assurance)
**Domains**: Effectiveness of Care, Access/Availability, Experience of Care, Utilization, Health Plan Descriptive Information

### Measure Calculation Methodology

**Administrative Data**: Claims and enrollment data
**Hybrid Method**: Administrative data + medical record review
**Survey Data**: CAHPS (Consumer Assessment of Healthcare Providers and Systems)

### Key HEDIS Measures

#### Comprehensive Diabetes Care (CDC)

**Eligible Population**:
- Age 18-75 with diabetes (Type 1 or Type 2)
- Continuous enrollment during measurement year

**Components**:

1. **HbA1c Testing**
```
Numerator: At least one HbA1c test during the measurement year
Denominator: All eligible diabetic patients
Target: >90%
```

2. **HbA1c Control (<8%)**
```
Numerator: Most recent HbA1c <8% (or <64 mmol/mol)
Denominator: All eligible with HbA1c result
Target: >50%
```

3. **HbA1c Poor Control (>9%)**
```
Numerator: Most recent HbA1c >9% (or >75 mmol/mol)
Denominator: All eligible with HbA1c result
Target: <35% (lower is better)
```

4. **Eye Exam**
```
Numerator: Retinal or dilated eye exam during measurement year or prior year
Denominator: All eligible diabetic patients
Target: >60%
```

5. **Medical Attention for Nephropathy**
```
Numerator: Evidence of nephropathy (urine protein test, ACE/ARB, visit with nephrologist)
Denominator: All eligible diabetic patients
Target: >90%
```

6. **BP Control (<140/90)**
```
Numerator: Most recent BP <140/90 mmHg
Denominator: All eligible diabetic patients
Target: >70%
```

**SQL Example:**
```sql
-- HbA1c Testing Rate
WITH diabetic_population AS (
    SELECT DISTINCT patient_key
    FROM fact_diagnosis
    WHERE diagnosis_code LIKE 'E08%'
       OR diagnosis_code LIKE 'E09%'
       OR diagnosis_code LIKE 'E10%'
       OR diagnosis_code LIKE 'E11%'
       OR diagnosis_code LIKE 'E13%'
       AND diagnosis_date BETWEEN '2023-01-01' AND '2023-12-31'
),
hba1c_tests AS (
    SELECT DISTINCT patient_key
    FROM fact_lab_result
    WHERE lab_test_code = '4548-4'  -- LOINC for HbA1c
       AND result_date BETWEEN '2023-01-01' AND '2023-12-31'
)
SELECT
    COUNT(DISTINCT dp.patient_key) AS denominator,
    COUNT(DISTINCT ht.patient_key) AS numerator,
    ROUND(100.0 * COUNT(DISTINCT ht.patient_key) / COUNT(DISTINCT dp.patient_key), 2) AS rate
FROM diabetic_population dp
LEFT JOIN hba1c_tests ht ON dp.patient_key = ht.patient_key;
```

#### Controlling High Blood Pressure (CBP)

**Eligible Population**:
- Age 18-85 with diagnosis of hypertension
- Continuous enrollment

**Numerator**: Most recent BP <140/90 mmHg during measurement year

**Exclusions**:
- End-stage renal disease
- Pregnancy
- Hospice care

**Stratification**: Age groups, comorbidities

#### Breast Cancer Screening (BCS)

**Eligible Population**:
- Women age 50-74
- Continuous enrollment

**Numerator**: Mammogram during measurement year or year prior

**Value Sets**:
- CPT: 77065, 77066, 77067
- HCPCS: G0202, G0204, G0206
- ICD-10-PCS: BH00ZZZ, BH01ZZZ

#### Colorectal Cancer Screening (COL)

**Eligible Population**:
- Age 50-75
- Continuous enrollment

**Numerator**: One of the following:
- Fecal occult blood test (FOBT) during measurement year
- Flexible sigmoidoscopy during measurement year or 4 years prior
- Colonoscopy during measurement year or 9 years prior
- CT colonography during measurement year or 4 years prior
- FIT-DNA test during measurement year or 2 years prior

**Exclusions**:
- Colorectal cancer
- Total colectomy

#### Childhood Immunization Status (CIS)

**Eligible Population**:
- Children who turn 2 years old during measurement year
- Continuous enrollment

**Combination Measures**:
1. DTaP (4 doses)
2. IPV (3 doses)
3. MMR (1 dose)
4. HiB (3 doses)
5. Hepatitis B (3 doses)
6. VZV (1 dose)
7. Pneumococcal conjugate (4 doses)
8. Hepatitis A (1 dose)
9. Rotavirus (2-3 doses)
10. Influenza (2 doses)

**Combination Rates**: Various combinations (e.g., Combo 3, Combo 10)

### HEDIS Star Ratings

**Purpose**: Medicare Advantage and Part D plan quality ratings (1-5 stars)

**Domains**:
1. Staying Healthy: Screenings, Tests, Vaccines
2. Managing Chronic Conditions: Diabetes, Heart Disease
3. Member Experience: CAHPS survey results
4. Member Complaints and Changes in Plan Performance
5. Health Plan Customer Service

**Star Calculation**:
- Measures scored 1-5 stars based on percentile performance
- Domain scores averaged
- Overall score: weighted average of domains
- Cut points revised annually based on national distribution

**High-Value Measures**: Weighted more heavily (e.g., CBP, CDC)

### HEDIS Data Collection

#### Administrative Method

```python
# Pseudocode for HEDIS CDC - HbA1c Testing
def calculate_cdc_hba1c_admin(measurement_year):
    # Step 1: Identify diabetic population
    diabetic_population = get_diabetic_patients(
        measurement_year=measurement_year,
        continuous_enrollment=True,
        age_range=(18, 75)
    )

    # Step 2: Exclude patients
    excluded = exclude_patients(
        diabetic_population,
        exclusions=['hospice', 'palliative_care', 'deceased']
    )

    denominator = len(diabetic_population) - len(excluded)

    # Step 3: Identify numerator (HbA1c test)
    numerator = count_patients_with_test(
        population=diabetic_population - excluded,
        loinc_codes=['4548-4', '17856-6', '41995-2'],
        date_range=(f'{measurement_year}-01-01', f'{measurement_year}-12-31')
    )

    # Step 4: Calculate rate
    rate = (numerator / denominator) * 100
    return {
        'denominator': denominator,
        'numerator': numerator,
        'rate': rate
    }
```

#### Hybrid Method

```
1. Run administrative spec (claims/encounter data)
2. Sample records for medical record review
3. Calculate oversample rate (account for exclusions)
4. Abstract medical records
5. Apply weighted hybrid rate calculation
6. Report final measure rate
```

**Sample Size**: Based on NCQA specifications (typically 411 records)

## MIPS (Merit-based Incentive Payment System)

### Overview

**Purpose**: Medicare physician quality payment program
**Applies to**: Eligible clinicians (physicians, NPs, PAs, etc.)
**Enacted**: MACRA (Medicare Access and CHIP Reauthorization Act) 2015

### MIPS Performance Categories

1. **Quality (30-45%)**: Clinical quality measures
2. **Cost (0-30%)**: Cost/resource use (calculated by CMS)
3. **Improvement Activities (15%)**: Practice improvement activities
4. **Promoting Interoperability (25%)**: Meaningful use of EHR

**Total Score**: 0-100 points, determines payment adjustment (+/- up to 9%)

### MIPS Quality Measures

**Requirements**:
- Report 6 quality measures (including 1 outcome measure)
- Or, report all measures in specialty measure set
- Meet data completeness threshold (70% of eligible cases)

**Reporting Methods**:
- Claims
- Registry
- EHR
- QCDR (Qualified Clinical Data Registry)
- CMS Web Interface (for groups)

**Measure Selection Strategy**:
- Choose topped-out measures cautiously (3-point cap)
- Select high-performing measures
- Include bonus measures (high priority, outcome)

#### Example MIPS Quality Measures

**Diabetes: HbA1c Poor Control (>9%)**
- Measure ID: 001
- NQF: 0059
- Type: Intermediate Outcome
- Inverse Measure: Lower is better

**Denominator**: Patients age 18-75 with diabetes
**Numerator**: Patients with most recent HbA1c >9%
**Exclusion**: Patients with diabetes during pregnancy

**Coronary Artery Disease: Beta-Blocker Therapy**
- Measure ID: 007
- Type: Process

**Denominator**: Patients with CAD and prior MI
**Numerator**: Patients prescribed beta-blocker therapy
**Exception**: Medical reason for not prescribing

### MIPS Improvement Activities

**Requirements**: Attest to 1-4 activities depending on category weight

**Categories**:
- Achieving Health Equity
- Behavioral and Mental Health
- Beneficiary Engagement
- Care Coordination
- Emergency Response and Preparedness
- Patient Safety and Practice Assessment
- Expanded Practice Access
- Population Management

**Example Activities**:
- Implement Depression Screening (medium weight, 10 points)
- Implement PCMH Recognition (high weight, 20 points)
- Use CDC Training to Improve Antibiotic Prescribing (medium, 10 points)

### MIPS Promoting Interoperability

**Objectives**:
1. **e-Prescribing**: Generate and transmit e-prescriptions (10 points)
2. **Health Information Exchange**: Send/receive electronic health info (40 points)
3. **Provider to Patient Exchange**: Give patients electronic access (40 points)
4. **Public Health and Clinical Data Exchange**: Submit to registries (10 points)

**Bonus Points**:
- Query PDMP (5 points)
- Verify Opioid Treatment Agreement (10 points)

### MIPS Scoring Example

```
Provider X MIPS Score (2023):

Quality: 85 points × 40% weight = 34.0
Cost: 70 points × 30% weight = 21.0
Improvement Activities: 100 points × 15% weight = 15.0
Promoting Interoperability: 90 points × 15% weight = 13.5

Total MIPS Score: 83.5 points

Performance Threshold: 75 points
Additional Performance Threshold: 89 points

Payment Adjustment: +3.5% (above threshold, scaled adjustment)
```

## eCQM (Electronic Clinical Quality Measures)

### Overview

**Purpose**: Clinical quality measures calculated from EHR data
**Format**: Standards-based, computable specifications
**Used in**: Hospital IQR, Promoting Interoperability, various CMS programs

### eCQM Structure

**QDM (Quality Data Model)**: Conceptual framework for quality data

**CQL (Clinical Quality Language)**: Human-readable, machine-executable logic

**FHIR-based eCQMs**: Emerging standard using FHIR resources

### eCQM Components

```
Initial Population (IP)
    ↓
Denominator (DENOM)
    ↓ (minus)
Denominator Exclusions (DENEX)
    ↓ (minus)
Denominator Exceptions (DENEXCEP)
    ↓
Eligible Population for Numerator
    ↓
Numerator (NUMER)
    ↓ (minus)
Numerator Exclusions (NUMEX)
    ↓
Performance Met Population

Rate = NUMER / (DENOM - DENEX - DENEXCEP)
```

### Example eCQM: CMS122v11 - Diabetes: HbA1c Poor Control

**CQL Logic (Simplified):**

```cql
library CMS122 version '11.0.000'

using QDM version '5.6'

// Value sets
valueset "Diabetes": '2.16.840.1.113883.3.464.1003.103.12.1001'
valueset "HbA1c Laboratory Test": '2.16.840.1.113883.3.464.1003.198.12.1013'

// Parameters
parameter "Measurement Period" Interval<DateTime>

// Initial Population
define "Initial Population":
  AgeInYearsAt(start of "Measurement Period") >= 18
    and AgeInYearsAt(start of "Measurement Period") < 75
    and exists "Qualifying Encounters"
    and exists "Diabetes Diagnosis"

// Denominator
define "Denominator":
  "Initial Population"

// Denominator Exclusions
define "Denominator Exclusions":
  "Has Hospice Care"
    or "Has Palliative Care"
    or "Advanced Illness and Frailty"

// Numerator
define "Numerator":
  "Has Most Recent HbA1c Greater Than 9"

// Supporting definitions
define "Diabetes Diagnosis":
  [Diagnosis: "Diabetes"] D
    where D.prevalencePeriod overlaps "Measurement Period"

define "Has Most Recent HbA1c Greater Than 9":
  "Most Recent HbA1c" >= 9 '%'

define "Most Recent HbA1c":
  Last(
    [Laboratory Test, Performed: "HbA1c Laboratory Test"] HbA1c
      where HbA1c.result is not null
        and HbA1c.relevantDatetime during "Measurement Period"
      sort by relevantDatetime
  ).result as Quantity
```

### eCQM Value Sets

**OID (Object Identifier)**: Unique identifier for value sets
**Managed by**: VSAC (Value Set Authority Center)

**Example Value Sets:**
- 2.16.840.1.113883.3.464.1003.103.12.1001: Diabetes
- 2.16.840.1.113883.3.464.1003.198.12.1013: HbA1c Laboratory Test
- 2.16.840.1.113883.3.464.1003.101.12.1001: Office Visit

**VSAC Access**: Requires UMLS account

### eCQM Implementation Patterns

#### Data Element Extraction

```sql
-- Extract diabetes diagnoses for eCQM
SELECT
    p.patient_key,
    d.diagnosis_code,
    d.diagnosis_date,
    d.diagnosis_description
FROM dim_patient p
JOIN fact_diagnosis d ON p.patient_key = d.patient_key
WHERE d.diagnosis_code IN (
    -- ICD-10 codes from "Diabetes" value set
    SELECT code FROM ecqm_valueset_codes
    WHERE valueset_oid = '2.16.840.1.113883.3.464.1003.103.12.1001'
        AND code_system = 'ICD10CM'
)
    AND d.diagnosis_date BETWEEN '2023-01-01' AND '2023-12-31';
```

#### eCQM Calculation Engine

```python
class ECQMEngine:
    def __init__(self, measure_id, measurement_period):
        self.measure_id = measure_id
        self.measurement_period = measurement_period
        self.cql_library = load_cql_library(measure_id)

    def calculate_measure(self, patient_id):
        # Build patient context
        context = self.build_patient_context(patient_id)

        # Evaluate CQL expressions
        ip = self.cql_library.evaluate('Initial Population', context)
        denom = self.cql_library.evaluate('Denominator', context)
        denex = self.cql_library.evaluate('Denominator Exclusions', context)
        denexcep = self.cql_library.evaluate('Denominator Exceptions', context)
        numer = self.cql_library.evaluate('Numerator', context)

        # Determine patient population membership
        return {
            'patient_id': patient_id,
            'initial_population': ip,
            'denominator': denom,
            'denominator_exclusions': denex,
            'denominator_exceptions': denexcep,
            'numerator': numer,
            'performance_met': numer and denom and not denex and not denexcep
        }

    def calculate_population_rate(self, patient_ids):
        results = [self.calculate_measure(pid) for pid in patient_ids]

        denom_count = sum(1 for r in results if r['denominator'] and not r['denominator_exclusions'])
        numer_count = sum(1 for r in results if r['numerator'])

        return {
            'measure_id': self.measure_id,
            'denominator': denom_count,
            'numerator': numer_count,
            'rate': (numer_count / denom_count * 100) if denom_count > 0 else 0,
            'measurement_period': self.measurement_period
        }
```

### Common eCQMs

**Hospital Inpatient Quality Reporting (IQR):**
- ED-2: Admit Decision Time to ED Departure
- SEP-1: Severe Sepsis and Septic Shock: Management Bundle
- PC-01: Elective Delivery (avoid early elective deliveries)
- VTE-1: Venous Thromboembolism Prophylaxis

**Eligible Hospital/CAH eCQMs:**
- CMS2v12: Preventive Care and Screening: BMI and Follow-Up
- CMS68v12: Documentation of Current Medications
- CMS69v11: Preventive Care and Screening: BMI and Nutrition Counseling
- CMS50v11: Closing the Referral Loop

## Quality Measure Reporting Formats

### QRDA (Quality Reporting Document Architecture)

**QRDA Category I**: Patient-level data
- One document per patient
- Contains patient demographics and relevant data elements
- Used for registry reporting, provider-level reporting

**QRDA Category III**: Aggregate summary data
- Population-level results
- Aggregate counts (numerator, denominator, exclusions)
- Used for program reporting to CMS

**Example QRDA I (Simplified XML):**
```xml
<ClinicalDocument>
  <recordTarget>
    <patientRole>
      <id extension="1234567" root="2.16.840.1.113883.3.xxx"/>
      <patient>
        <birthTime value="19650315"/>
        <administrativeGenderCode code="M" codeSystem="2.16.840.1.113883.5.1"/>
      </patient>
    </patientRole>
  </recordTarget>

  <entry>
    <observation classCode="OBS" moodCode="EVN">
      <code code="4548-4" codeSystem="2.16.840.1.113883.6.1"
            displayName="Hemoglobin A1c"/>
      <value xsi:type="PQ" value="7.2" unit="%"/>
      <effectiveTime value="20230615"/>
    </observation>
  </entry>
</ClinicalDocument>
```

### Flat File Formats

**Medicare Part C/D Reporting**: Fixed-width, CSV formats
**Registry Reporting**: Custom formats per registry

## Quality Measure Stratification

### Risk Adjustment

**Purpose**: Account for patient complexity when comparing performance

**Methods**:
- Direct standardization
- Indirect standardization
- Hierarchical modeling

**CMS HCC (Hierarchical Condition Categories):**
- Risk score based on demographics and diagnoses
- Used for cost and utilization benchmarking
- Not typically used for clinical quality measures

### Demographic Stratification

**Common Strata**:
- Age groups
- Gender
- Race/ethnicity
- Geographic region
- Payer type (Medicare, Medicaid, Commercial)

**Health Equity Analysis**: Compare performance across racial/ethnic groups to identify disparities

## Quality Improvement Workflow

```
1. Measure Selection
   ↓
2. Baseline Measurement
   ↓
3. Gap Analysis (identify underperforming areas)
   ↓
4. Intervention Design
   ↓
5. Implementation
   ↓
6. Monitoring & Feedback
   ↓
7. Re-measurement
   ↓
8. Continuous Improvement
```

### Quality Dashboard Components

**Executive View:**
- Overall quality score/star rating
- Trend over time
- Comparison to benchmarks

**Operational View:**
- Measure-specific rates
- Drill-down by provider, location, payer
- Care gap lists

**Patient-Level View:**
- Individual care gaps
- Due dates for screenings/tests
- Integration with EHR workflows

## Quality Measure Tools & Vendors

### Quality Measure Engines
- **Medisolv Quality Measure Calculator**: Hybrid HEDIS, eCQM engine
- **Philips Wellcentive**: Population health platform with quality measures
- **Health Catalyst**: Data warehouse with quality measure analytics
- **Epic Healthy Planet**: EHR-integrated population health tool

### Quality Reporting Solutions
- **Mathematica Chronic Condition Warehouse**: CMS data repository
- **Inovalon**: Cloud-based quality and risk adjustment
- **Cedar Gate**: Medicare Advantage quality analytics
- **Arcadia Analytics**: Population health and quality platform

---

*Quality Measures Reference - Standards for measuring and improving healthcare quality across health plans, providers, and hospitals.*
