# Population Health Metrics Reference

## Overview

Population health analytics focuses on measuring and improving health outcomes for defined patient populations, emphasizing prevention, care coordination, and value-based care delivery.

## Core Population Health Concepts

### Triple Aim

**Goals:**
1. **Better Care**: Improve patient experience and quality
2. **Better Health**: Improve population health outcomes
3. **Lower Cost**: Reduce per capita healthcare costs

**Quadruple Aim**: Adds provider/team well-being

### Population Segmentation

**Purpose**: Group patients by similar characteristics for targeted interventions

**Segmentation Dimensions:**
- Risk level (high, medium, low)
- Chronic conditions (diabetes, CHF, COPD, etc.)
- Utilization patterns (high ED use, frequent inpatient)
- Social determinants of health (SDOH)
- Care management needs

## Population Health Metrics Categories

### Access Metrics

#### Primary Care Access

**Primary Care Visits per 1000 Members**
```
Numerator: Total primary care visits (CPT 99201-99215)
Denominator: Total members × (days in period / 365)
Target: 3000-4000 visits per 1000 member-years
```

**PCP Panel Size**
```
Numerator: Total attributed members
Denominator: Number of PCPs
Target: 1500-2500 patients per PCP
```

**Third Next Available Appointment**
```
Metric: Days until 3rd next available appointment slot
Data Source: Practice management system
Target: ≤7 days for routine visits
```

#### Specialist Access

**Referral Completion Rate**
```
Numerator: Referrals with completed specialist visit
Denominator: All referrals placed
Target: >85%
```

**Time to Specialist Appointment**
```
Metric: Days from referral to specialist visit
Target: ≤14 days for urgent, ≤30 days for routine
```

### Utilization Metrics

#### Inpatient Utilization

**Inpatient Admits per 1000**
```sql
SELECT
    COUNT(DISTINCT encounter_key) AS admits,
    COUNT(DISTINCT patient_key) AS total_patients,
    ROUND(1000.0 * COUNT(DISTINCT encounter_key) / COUNT(DISTINCT patient_key), 2) AS admits_per_1000
FROM fact_encounter
WHERE encounter_type = 'Inpatient'
    AND admission_date_key BETWEEN 20230101 AND 20231231;
```

**Benchmark**: 50-100 admits per 1000 (varies by population age/acuity)

**Inpatient Days per 1000**
```
Numerator: Total inpatient days (sum of length of stay)
Denominator: Total members
Multiplier: 1000
Target: 200-400 days per 1000 member-years
```

**Average Length of Stay (ALOS)**
```
Numerator: Total inpatient days
Denominator: Total inpatient discharges
Target: 4.5-5.5 days (varies by case mix)
```

**Case Mix Index (CMI)**
```
Numerator: Sum of all DRG weights
Denominator: Total discharges
Purpose: Adjust for patient acuity/complexity
```

#### Emergency Department Utilization

**ED Visits per 1000**
```
Numerator: Total ED visits
Denominator: Total members
Multiplier: 1000
Target: 300-500 visits per 1000 member-years
```

**Avoidable ED Visit Rate**
```
Numerator: ED visits for non-urgent conditions (NYU ED algorithm)
Denominator: Total ED visits
Target: <30%
```

**ED Admits Rate**
```
Numerator: ED visits resulting in inpatient admission
Denominator: Total ED visits
Benchmark: 12-18%
```

#### Outpatient & Ancillary Utilization

**Outpatient Visits per 1000**
- Primary care visits
- Specialist visits
- Mental health visits

**Imaging per 1000**
- CT scans
- MRIs
- X-rays

**Lab Tests per Member**
```
Numerator: Total lab tests
Denominator: Total members
Target: Varies by population
```

### Quality & Outcomes Metrics

#### Chronic Disease Management

**Diabetes Quality Composite**
```
Components:
- HbA1c <8%: 60%
- BP <140/90: 70%
- Eye exam: 65%
- Nephropathy screening: 80%
- Statin therapy: 75%

Composite Score: Average of all components
Target: >70%
```

**Heart Failure Readmission Rate**
```
Numerator: CHF patients readmitted within 30 days
Denominator: CHF discharges
Target: <20%
```

**COPD Exacerbation Rate**
```
Numerator: COPD patients with ED visit or hospitalization for exacerbation
Denominator: Total COPD patients
Target: <15 per 100 patients
```

**Hypertension Control Rate**
```
Numerator: HTN patients with most recent BP <140/90
Denominator: HTN patients with BP measured
Target: >70%
```

#### Preventive Care

**Cancer Screening Rates**
```
Breast Cancer (Women 50-74): Mammogram in past 2 years
  Target: >75%

Colorectal Cancer (50-75): Appropriate screening
  Target: >70%

Cervical Cancer (Women 21-64): Pap test per guidelines
  Target: >80%

Lung Cancer (High-risk 50-80): LDCT if indicated
  Target: >15% of eligible
```

**Immunization Rates**
```
Influenza (Age 65+): Annual flu shot
  Target: >70%

Pneumococcal (Age 65+): PCV13 and PPSV23 per CDC
  Target: >70%

Shingles (Age 50+): Shingrix 2-dose series
  Target: >50%
```

**Well-Child Visits**
```
Age 0-15 months: 6+ visits
Age 3-6 years: 1+ visit per year
Age 12-21 years: 1+ visit per year
Target: >80%
```

#### Patient Safety & Experience

**Hospital-Acquired Conditions**
```
- Central line-associated BSI (CLABSI)
- Catheter-associated UTI (CAUTI)
- Surgical site infections (SSI)
- Pressure ulcers
- Falls with injury

Target: <1% of admissions
```

**Patient Experience (CAHPS)**
```
- Overall rating of care: Mean score 0-10
- Doctor communication: % top box
- Care coordination: % top box
- Access to care: % top box

Target: ≥75th percentile nationally
```

### Care Management Metrics

#### Care Gap Closure

**Open Care Gaps per Patient**
```sql
WITH care_gaps AS (
    SELECT
        patient_key,
        SUM(CASE WHEN hba1c_due = 1 THEN 1 ELSE 0 END) AS hba1c_gap,
        SUM(CASE WHEN mammogram_due = 1 THEN 1 ELSE 0 END) AS mammogram_gap,
        SUM(CASE WHEN colonoscopy_due = 1 THEN 1 ELSE 0 END) AS colonoscopy_gap,
        SUM(CASE WHEN eye_exam_due = 1 THEN 1 ELSE 0 END) AS eye_exam_gap
    FROM patient_quality_metrics
    GROUP BY patient_key
)
SELECT
    AVG(hba1c_gap + mammogram_gap + colonoscopy_gap + eye_exam_gap) AS avg_gaps_per_patient
FROM care_gaps;
```

**Care Gap Closure Rate**
```
Numerator: Care gaps closed during period
Denominator: Total care gaps at period start
Target: >40% per quarter
```

#### Care Coordinator Productivity

**Patients Enrolled in Care Management**
```
Numerator: Patients actively receiving care management
Denominator: Eligible high-risk patients
Target: >80% of eligible
```

**Care Coordinator Caseload**
```
Metric: Average patients per care coordinator
Target: 50-150 depending on acuity
```

**Outreach Attempts per Patient**
```
Numerator: Total outreach contacts (calls, visits, messages)
Denominator: Enrolled patients
Target: 2+ contacts per month for high-risk
```

**Care Plan Completion Rate**
```
Numerator: Patients with documented, current care plan
Denominator: Enrolled patients
Target: >95%
```

### Cost & Financial Metrics

#### Total Cost of Care (TCOC)

**Per Member Per Month (PMPM)**
```
Numerator: Total allowed costs for all services
Denominator: Member months
Example: $450 PMPM for commercial population
```

**Cost Categories:**
- Inpatient: 30-40% of TCOC
- Outpatient: 25-35%
- Professional: 20-30%
- Pharmacy: 15-25%
- Other: 5-10%

**Medical Loss Ratio (MLR)**
```
Numerator: Total medical expenses + quality improvement
Denominator: Premium revenue
Regulatory Minimum: 80% (individual/small group), 85% (large group)
```

#### Trend Analysis

**Medical Cost Trend**
```
Formula: ((Current Year PMPM / Prior Year PMPM) - 1) × 100
Industry Average: 5-7% annual increase
```

**Risk-Adjusted PMPM**
```
Numerator: Total costs × (Population Average RAF / Member RAF)
Denominator: Member months
Purpose: Compare costs across different population acuities
```

#### High-Cost Patients

**Percent of Spend in Top 5%**
```
Numerator: Total costs for top 5% costliest patients
Denominator: Total costs for all patients
Typical: 50-60% of total spend
```

**Catastrophic Cases**
```
Threshold: Patients exceeding $100k+ annual costs
Percentage: 0.5-2% of population
Monitoring: Monthly case review, care coordination
```

### Risk Stratification Metrics

#### Risk Score Distribution

**HCC Risk Score**
```sql
SELECT
    CASE
        WHEN risk_score < 0.5 THEN 'Very Low'
        WHEN risk_score BETWEEN 0.5 AND 1.0 THEN 'Low'
        WHEN risk_score BETWEEN 1.0 AND 2.0 THEN 'Medium'
        WHEN risk_score BETWEEN 2.0 AND 3.0 THEN 'High'
        WHEN risk_score > 3.0 THEN 'Very High'
    END AS risk_category,
    COUNT(*) AS patient_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM patient_risk_scores
GROUP BY risk_category;
```

**Risk Stratification Model Performance**
```
- Positive Predictive Value (PPV): High-risk patients with events
- Sensitivity: Percent of events captured in high-risk group
- Specificity: Percent of non-events in low-risk group
- AUC-ROC: 0.70+ indicates good discrimination
```

#### Patient Complexity

**Multiple Chronic Conditions**
```
Distribution:
- 0 conditions: 40-50%
- 1-2 conditions: 30-40%
- 3-5 conditions: 15-20%
- 6+ conditions: 5-10%
```

**Polypharmacy Rate**
```
Numerator: Patients on 5+ medications
Denominator: Total patients
Concern: Medication interactions, adherence challenges
```

### Social Determinants of Health (SDOH)

#### SDOH Data Elements

**Economic Stability**
- Employment status
- Income level / Federal poverty level (FPL)
- Food insecurity
- Housing instability

**Education Access**
- Literacy level
- Educational attainment

**Healthcare Access**
- Insurance status
- Transportation barriers
- Access to primary care

**Neighborhood & Built Environment**
- ZIP code / census tract
- Area Deprivation Index (ADI)
- Crime rate
- Environmental quality

**Social & Community Context**
- Social isolation
- Community engagement

#### SDOH Metrics

**Food Insecurity Screening Rate**
```
Numerator: Patients screened for food insecurity
Denominator: All patients
Target: >80% annually
```

**Housing Instability Prevalence**
```
Numerator: Patients reporting housing instability
Denominator: Patients screened
Benchmark: 5-15% in general population
```

**Area Deprivation Index (ADI)**
```
Scale: 1-100 (higher = more disadvantaged)
Use: Segment populations, target resources
Data Source: Neighborhood Atlas
```

**Transportation Barrier Rate**
```
Numerator: Patients reporting transportation as barrier to care
Denominator: Patients screened
Action: Connect to transportation assistance programs
```

## Advanced Population Health Analytics

### Predictive Risk Models

**30-Day Readmission Risk**
```
Features:
- Prior hospitalizations
- Comorbidities (Charlson, Elixhauser)
- Medications
- Lab values
- Demographics
- SDOH factors

Model: Logistic regression, gradient boosting
Target AUC: >0.70
Intervention: Care transitions program for high-risk
```

**Future High-Cost Prediction**
```
Outcome: Top 10% costs in next 12 months
Features:
- Historical costs
- Chronic conditions
- Pharmacy utilization
- ED utilization
- Risk scores

Purpose: Proactive care management enrollment
```

**Disease Progression Models**
```
Examples:
- CKD progression to ESRD
- Pre-diabetes to diabetes
- Stable angina to ACS

Use: Early intervention, resource planning
```

### Patient Attribution

**Attribution Methods:**

1. **Plurality**: Provider with most visits
2. **Majority**: Provider with >50% of visits
3. **Prospective**: Based on prior year utilization
4. **Roster-based**: Patient selection of PCP
5. **Claims-based**: Algorithm using E&M visits

**Attribution Window**: Typically 12-24 months

**Attribution Example:**
```sql
WITH patient_visits AS (
    SELECT
        patient_key,
        provider_key,
        COUNT(*) AS visit_count,
        RANK() OVER (PARTITION BY patient_key ORDER BY COUNT(*) DESC) AS provider_rank
    FROM fact_encounter
    WHERE encounter_type IN ('Office Visit', 'Telehealth')
        AND encounter_date BETWEEN '2022-01-01' AND '2023-12-31'
    GROUP BY patient_key, provider_key
)
SELECT
    patient_key,
    provider_key AS attributed_provider
FROM patient_visits
WHERE provider_rank = 1;  -- Plurality attribution
```

### Cohort Analysis

**Diabetes Cohort Year-over-Year Comparison**
```sql
SELECT
    year,
    COUNT(DISTINCT patient_key) AS cohort_size,
    AVG(hba1c_last_value) AS avg_hba1c,
    SUM(CASE WHEN hba1c_last_value > 9 THEN 1 ELSE 0 END) AS poor_control_count,
    AVG(total_cost_pmpm) AS avg_pmpm,
    AVG(ip_admits) AS avg_admits
FROM diabetes_annual_cohort
GROUP BY year
ORDER BY year;
```

### Longitudinal Analysis

**Patient Journey Mapping**
```
Identify common care pathways:
1. Diagnosis event
2. Initial treatment
3. Follow-up visits
4. Complications
5. Intensification
6. Outcomes (control vs. progression)

Analyze time between events, treatment variations
```

**Time to Treatment**
```
Numerator: Days from diagnosis to first treatment
Denominator: Newly diagnosed patients
Stratify by: Demographics, severity, insurance
```

## Population Health Dashboards

### Executive Dashboard Components

**KPI Summary:**
- Total attributed population
- Overall quality score (composite)
- Total cost PMPM
- Medical cost trend
- Hospital admissions per 1000
- ED visits per 1000
- Star rating (if applicable)

**Trends:**
- Quality measure performance over time
- Cost trend graphs
- Utilization trends

**Benchmarks:**
- Comparison to national/regional benchmarks
- Peer group comparisons

### Operational Dashboard

**Care Gap Management:**
- Open gaps by measure
- Gaps closed this month
- Patients with multiple gaps
- Actionable patient lists

**High-Risk Patient Panel:**
- Risk score distribution
- High-risk patients needing outreach
- Care management enrollment status
- Recent ED/IP utilization

**Provider Performance:**
- Quality measures by provider
- Panel size
- Utilization patterns
- Cost efficiency

### Patient-Level View

**Individual Patient Summary:**
- Demographics
- Chronic conditions
- Risk score
- Recent utilization
- Open care gaps
- Assigned care coordinator
- Upcoming appointments

## Population Health Benchmarks

### Industry Benchmarks by Payer

**Medicare:**
- IP admits per 1000: 250-400
- IP days per 1000: 1200-2000
- ED visits per 1000: 500-800
- ALOS: 5.0-6.5 days

**Commercial (under 65):**
- IP admits per 1000: 50-100
- IP days per 1000: 200-400
- ED visits per 1000: 300-500
- ALOS: 4.0-5.0 days

**Medicaid:**
- IP admits per 1000: 80-150
- IP days per 1000: 300-600
- ED visits per 1000: 600-1200
- ALOS: 4.5-6.0 days

### Quality Benchmarks

**NCQA Health Plan Ratings:**
- 5 Stars: 90th percentile
- 4 Stars: 75th percentile
- 3 Stars: 50th percentile
- 2 Stars: 25th percentile
- 1 Star: <25th percentile

**Diabetes Care Composite (Commercial):**
- Top 10%: >80%
- Average: 60-70%
- Below Average: <50%

## Population Health Interventions

### High-Value Interventions

**Transition of Care Programs**
- Post-discharge calls within 48 hours
- Medication reconciliation
- Follow-up appointment scheduling
- Home health coordination
- Target: 30% reduction in 30-day readmissions

**Chronic Disease Management**
- Self-management education
- Regular monitoring (home BP, glucose)
- Medication adherence programs
- Care coordinator touchpoints
- Target: 10-15% improvement in quality measures

**Preventive Outreach**
- Automated reminders for screenings
- Population health campaigns
- Community health events
- Patient navigation
- Target: 20% increase in screening rates

**Complex Care Management**
- Multidisciplinary care teams
- Individualized care plans
- Frequent touchpoints (weekly+)
- Social services integration
- Target: 20-30% cost reduction for enrolled

### Intervention Tracking

**Intervention Effectiveness:**
```sql
SELECT
    intervention_type,
    COUNT(DISTINCT patient_key) AS enrolled,
    AVG(pre_intervention_cost_pmpm) AS baseline_cost,
    AVG(post_intervention_cost_pmpm) AS follow_up_cost,
    AVG(post_intervention_cost_pmpm - pre_intervention_cost_pmpm) AS cost_change,
    AVG(pre_intervention_quality_score) AS baseline_quality,
    AVG(post_intervention_quality_score) AS follow_up_quality
FROM intervention_cohort_analysis
GROUP BY intervention_type;
```

---

*Population Health Metrics Reference - Comprehensive framework for measuring and improving health outcomes across defined patient populations.*
