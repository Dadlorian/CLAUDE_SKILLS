# Real-World Evidence Reference

## Overview

Real-World Evidence (RWE) is clinical evidence derived from analysis of Real-World Data (RWD) collected outside of traditional randomized controlled trials, used to support regulatory decisions, comparative effectiveness research, and value-based care.

## Real-World Data Sources

### Electronic Health Records (EHR)
- Demographics, diagnoses, procedures
- Laboratory results, vital signs
- Medications (prescribed and administered)
- Clinical notes (requires NLP)
- Treatment pathways
- **Advantages**: Rich clinical detail, longitudinal data
- **Limitations**: Data quality variation, missing data, limited to health system

### Claims Data
- Medical claims (professional, institutional)
- Pharmacy claims
- Enrollment/eligibility data
- **Advantages**: Large populations, complete utilization, standardized codes
- **Limitations**: Lack of clinical detail (no labs, vitals), billing-driven coding

### Registries
- Disease-specific registries (cancer, cardiovascular)
- Product registries (devices, biologics)
- Patient registries
- **Advantages**: Highly standardized, disease-specific detail
- **Limitations**: Limited scope, resource-intensive

### Patient-Generated Health Data
- Wearables (Fitbit, Apple Watch)
- Patient-reported outcomes (PROs)
- Mobile health apps
- **Advantages**: Patient perspective, continuous monitoring
- **Limitations**: Data quality, compliance, standardization

### Genomic and Biomarker Data
- Next-generation sequencing
- Biomarker panels
- Pharmacogenomics
- **Advantages**: Precision medicine insights
- **Limitations**: Cost, accessibility, interpretation complexity

## RWE Study Designs

### Cohort Studies

**Prospective Cohort:**
```
Exposure → Follow Over Time → Outcome
Example: Follow diabetics on SGLT2 inhibitors vs. DPP-4 inhibitors for cardiovascular events
```

**Retrospective Cohort:**
```
Historical Data → Define Cohorts → Analyze Outcomes
Example: Compare outcomes for COVID-19 patients treated with vs. without remdesivir using EHR data
```

**Example Implementation:**
```python
def create_treatment_cohorts(drug_of_interest, comparator_drug):
    """Create matched treatment cohorts"""

    # Define index date (first prescription)
    treatment_group = identify_new_users(
        drug=drug_of_interest,
        index_date_range=('2020-01-01', '2023-12-31')
    )

    comparator_group = identify_new_users(
        drug=comparator_drug,
        index_date_range=('2020-01-01', '2023-12-31')
    )

    # Apply inclusion/exclusion criteria
    treatment_group = apply_criteria(treatment_group, {
        'min_age': 18,
        'continuous_enrollment_pre': 180,  # 6 months pre-index
        'continuous_enrollment_post': 365,  # 12 months post-index
        'no_prior_treatment': [drug_of_interest, comparator_drug]
    })

    comparator_group = apply_criteria(comparator_group, {
        'min_age': 18,
        'continuous_enrollment_pre': 180,
        'continuous_enrollment_post': 365,
        'no_prior_treatment': [drug_of_interest, comparator_drug]
    })

    # Propensity score matching
    matched_cohorts = propensity_score_matching(
        treatment=treatment_group,
        comparator=comparator_group,
        covariates=[
            'age', 'gender', 'comorbidity_score',
            'prior_hospitalizations', 'baseline_hba1c'
        ],
        caliper=0.1
    )

    return matched_cohorts
```

### Case-Control Studies

```
Identify Cases (with outcome) ← Match Controls (without outcome) → Compare Exposures
```

**Example**: Identify hospitalized COVID-19 patients (cases) vs. matched controls, compare prior flu vaccination rates

```python
def conduct_case_control_study(outcome_condition, matching_ratio=4):
    """Case-control study design"""

    # Identify cases
    cases = identify_patients_with_condition(outcome_condition)

    # Find matched controls
    controls = []
    for case in cases:
        matched_controls = find_matched_controls(
            case_id=case['patient_id'],
            matching_criteria={
                'age': case['age'] ± 5,  # Within 5 years
                'gender': case['gender'],
                'index_date': case['diagnosis_date'],
                'no_outcome': outcome_condition
            },
            n_controls=matching_ratio
        )
        controls.extend(matched_controls)

    # Compare exposures
    exposure_analysis = compare_exposures(
        cases=cases,
        controls=controls,
        exposures_of_interest=[
            'prior_flu_vaccine',
            'chronic_conditions',
            'medications'
        ]
    )

    return exposure_analysis
```

### Cross-Sectional Studies

**Design**: Snapshot at single point in time

**Example**: Prevalence of diabetes and treatment patterns as of 2023-12-31

```sql
-- Cross-sectional prevalence study
SELECT
    age_group,
    gender,
    COUNT(*) AS total_patients,
    SUM(CASE WHEN has_diabetes = 1 THEN 1 ELSE 0 END) AS diabetes_patients,
    ROUND(100.0 * SUM(CASE WHEN has_diabetes = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS diabetes_prevalence_pct,
    SUM(CASE WHEN has_diabetes = 1 AND on_metformin = 1 THEN 1 ELSE 0 END) AS on_metformin,
    SUM(CASE WHEN has_diabetes = 1 AND on_insulin = 1 THEN 1 ELSE 0 END) AS on_insulin
FROM patient_snapshot_20231231
GROUP BY age_group, gender;
```

### Comparative Effectiveness Research (CER)

**Purpose**: Compare real-world effectiveness of treatment alternatives

**Example**: SGLT2 inhibitors vs. GLP-1 agonists for cardiovascular outcomes in Type 2 diabetes

```python
def comparative_effectiveness_analysis(treatment_a, treatment_b, outcome):
    """Compare effectiveness of two treatments"""

    # Create matched cohorts
    cohort_a = create_treatment_cohort(treatment_a)
    cohort_b = create_treatment_cohort(treatment_b)

    # Propensity score matching or inverse probability weighting
    matched = propensity_score_matching(cohort_a, cohort_b)

    # Follow-up analysis
    results_a = measure_outcome(matched['treatment_a'], outcome)
    results_b = measure_outcome(matched['treatment_b'], outcome)

    # Calculate effect sizes
    relative_risk = results_a['event_rate'] / results_b['event_rate']
    risk_difference = results_a['event_rate'] - results_b['event_rate']
    nnt = 1 / abs(risk_difference) if risk_difference != 0 else float('inf')

    # Survival analysis
    survival_comparison = kaplan_meier_analysis(
        cohort_a=matched['treatment_a'],
        cohort_b=matched['treatment_b'],
        outcome=outcome,
        follow_up_years=3
    )

    return {
        'treatment_a': treatment_a,
        'treatment_b': treatment_b,
        'outcome': outcome,
        'relative_risk': relative_risk,
        'risk_difference': risk_difference,
        'number_needed_to_treat': nnt,
        'survival_curves': survival_comparison
    }
```

## Statistical Methods for RWE

### Propensity Score Methods

**Purpose**: Reduce confounding in observational studies by balancing treatment groups

**Propensity Score**: Probability of receiving treatment given observed covariates

```python
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors

def calculate_propensity_scores(data, treatment_var, covariates):
    """Calculate propensity scores using logistic regression"""

    X = data[covariates]
    y = data[treatment_var]

    # Fit logistic regression
    ps_model = LogisticRegression(max_iter=1000)
    ps_model.fit(X, y)

    # Predict propensity scores
    propensity_scores = ps_model.predict_proba(X)[:, 1]

    data['propensity_score'] = propensity_scores
    return data

def propensity_score_matching(treatment_group, control_group, caliper=0.1):
    """1:1 nearest neighbor matching with caliper"""

    # Calculate propensity scores
    treatment_ps = treatment_group['propensity_score'].values.reshape(-1, 1)
    control_ps = control_group['propensity_score'].values.reshape(-1, 1)

    # Nearest neighbor matching
    nn = NearestNeighbors(n_neighbors=1, metric='euclidean')
    nn.fit(control_ps)
    distances, indices = nn.kneighbors(treatment_ps)

    # Apply caliper (exclude matches beyond caliper distance)
    matched_pairs = []
    for i, (distance, control_idx) in enumerate(zip(distances, indices)):
        if distance[0] <= caliper:
            matched_pairs.append({
                'treatment_id': treatment_group.iloc[i]['patient_id'],
                'control_id': control_group.iloc[control_idx[0]]['patient_id'],
                'distance': distance[0]
            })

    return pd.DataFrame(matched_pairs)
```

**Propensity Score Methods:**
1. **Matching**: Pair treated and control subjects with similar PS
2. **Stratification**: Stratify by PS quintiles and analyze within strata
3. **IPTW (Inverse Probability of Treatment Weighting)**: Weight subjects by inverse of PS
4. **Covariate Adjustment**: Include PS as covariate in regression

### Survival Analysis

```python
from lifelines import KaplanMeierFitter, CoxPHFitter
import matplotlib.pyplot as plt

def kaplan_meier_analysis(cohort_a, cohort_b, outcome_event, follow_up_col):
    """Kaplan-Meier survival analysis"""

    kmf = KaplanMeierFitter()

    # Fit for treatment A
    kmf.fit(
        durations=cohort_a[follow_up_col],
        event_observed=cohort_a[outcome_event],
        label='Treatment A'
    )
    kmf.plot()

    # Fit for treatment B
    kmf.fit(
        durations=cohort_b[follow_up_col],
        event_observed=cohort_b[outcome_event],
        label='Treatment B'
    )
    kmf.plot()

    plt.xlabel('Time (days)')
    plt.ylabel('Survival Probability')
    plt.title('Kaplan-Meier Survival Curves')
    plt.legend()
    plt.show()

    # Log-rank test for difference
    from lifelines.statistics import logrank_test
    results = logrank_test(
        cohort_a[follow_up_col], cohort_b[follow_up_col],
        cohort_a[outcome_event], cohort_b[outcome_event]
    )

    return results

def cox_proportional_hazards(data, duration_col, event_col, covariates):
    """Cox proportional hazards regression"""

    cph = CoxPHFitter()
    cph.fit(data[[duration_col, event_col] + covariates],
            duration_col=duration_col,
            event_col=event_col)

    cph.print_summary()

    # Hazard ratios
    hazard_ratios = cph.hazard_ratios_
    return cph, hazard_ratios
```

### Difference-in-Differences (DiD)

**Purpose**: Assess causal effect of intervention using before/after comparisons

```python
def difference_in_differences(intervention_group, control_group, outcome, pre_period, post_period):
    """DiD analysis for policy/intervention evaluation"""

    # Intervention group: before and after
    int_pre = intervention_group[intervention_group['period'] == pre_period][outcome].mean()
    int_post = intervention_group[intervention_group['period'] == post_period][outcome].mean()
    int_change = int_post - int_pre

    # Control group: before and after
    ctrl_pre = control_group[control_group['period'] == pre_period][outcome].mean()
    ctrl_post = control_group[control_group['period'] == post_period][outcome].mean()
    ctrl_change = ctrl_post - ctrl_pre

    # DiD estimate
    did_estimate = int_change - ctrl_change

    return {
        'intervention_pre': int_pre,
        'intervention_post': int_post,
        'intervention_change': int_change,
        'control_pre': ctrl_pre,
        'control_post': ctrl_post,
        'control_change': ctrl_change,
        'did_estimate': did_estimate,
        'interpretation': f"Intervention effect: {did_estimate:.2f} (accounting for secular trends)"
    }
```

### Interrupted Time Series

```python
import statsmodels.api as sm

def interrupted_time_series(data, intervention_date, outcome):
    """Interrupted time series analysis"""

    # Create time variable
    data['time'] = range(len(data))

    # Create intervention indicator
    data['intervention'] = (data['date'] >= intervention_date).astype(int)

    # Time since intervention
    data['time_since_intervention'] = data.apply(
        lambda row: row['time'] - data[data['date'] == intervention_date].index[0]
        if row['intervention'] == 1 else 0,
        axis=1
    )

    # Regression model
    X = data[['time', 'intervention', 'time_since_intervention']]
    X = sm.add_constant(X)
    y = data[outcome]

    model = sm.OLS(y, X).fit()
    print(model.summary())

    # Interpret coefficients
    interpretation = {
        'baseline_trend': model.params['time'],
        'immediate_effect': model.params['intervention'],
        'change_in_trend': model.params['time_since_intervention']
    }

    return model, interpretation
```

## RWE Study Examples

### Example 1: Drug Safety Surveillance

```python
def drug_safety_surveillance(drug_of_interest, adverse_event, comparison_period='pre_post'):
    """Monitor adverse events associated with drug"""

    # Identify exposed cohort
    exposed = identify_patients_on_drug(drug_of_interest)

    if comparison_period == 'pre_post':
        # Compare rates before and during exposure
        pre_exposure_ae_rate = calculate_ae_rate(
            cohort=exposed,
            period='pre_exposure',
            adverse_event=adverse_event
        )

        during_exposure_ae_rate = calculate_ae_rate(
            cohort=exposed,
            period='during_exposure',
            adverse_event=adverse_event
        )

        relative_risk = during_exposure_ae_rate / pre_exposure_ae_rate

    else:  # Compare to unexposed
        unexposed = create_matched_unexposed_cohort(exposed)

        exposed_ae_rate = calculate_ae_rate(
            cohort=exposed,
            period='during_exposure',
            adverse_event=adverse_event
        )

        unexposed_ae_rate = calculate_ae_rate(
            cohort=unexposed,
            period='same_timeframe',
            adverse_event=adverse_event
        )

        relative_risk = exposed_ae_rate / unexposed_ae_rate

    # Signal detection
    signal = relative_risk > 2.0 and is_statistically_significant(exposed_ae_rate, unexposed_ae_rate)

    return {
        'drug': drug_of_interest,
        'adverse_event': adverse_event,
        'exposed_ae_rate': exposed_ae_rate,
        'comparison_ae_rate': unexposed_ae_rate,
        'relative_risk': relative_risk,
        'safety_signal': signal
    }
```

### Example 2: Treatment Pathway Analysis

```python
def analyze_treatment_pathways(condition, start_date, end_date):
    """Analyze real-world treatment sequences"""

    # Identify patients with condition
    cohort = identify_patients_with_condition(condition, start_date, end_date)

    # Extract treatment sequences
    pathways = []
    for patient_id in cohort:
        treatments = get_treatment_sequence(
            patient_id=patient_id,
            condition=condition,
            start_date=start_date,
            end_date=end_date
        )

        pathways.append({
            'patient_id': patient_id,
            'pathway': ' → '.join(treatments),
            'pathway_length': len(treatments),
            'outcome': get_patient_outcome(patient_id, condition)
        })

    df = pd.DataFrame(pathways)

    # Most common pathways
    pathway_frequency = df['pathway'].value_counts()

    # Pathways with best outcomes
    pathway_outcomes = df.groupby('pathway')['outcome'].mean()

    return {
        'total_patients': len(cohort),
        'unique_pathways': len(pathway_frequency),
        'most_common_pathways': pathway_frequency.head(10),
        'best_outcome_pathways': pathway_outcomes.nlargest(10)
    }
```

### Example 3: Medication Adherence Impact

```python
def adherence_outcomes_analysis(medication, outcome, follow_up_years=2):
    """Assess impact of medication adherence on outcomes"""

    # Identify patients on medication
    cohort = identify_patients_on_medication(medication)

    # Calculate adherence (PDC - Proportion of Days Covered)
    for patient_id in cohort:
        pdc = calculate_pdc(patient_id, medication, days=365)
        cohort[cohort['patient_id'] == patient_id]['pdc'] = pdc

    # Categorize adherence
    cohort['adherence_category'] = pd.cut(
        cohort['pdc'],
        bins=[0, 0.40, 0.80, 1.0],
        labels=['Poor (<40%)', 'Moderate (40-80%)', 'Good (≥80%)']
    )

    # Measure outcomes by adherence category
    outcomes_by_adherence = cohort.groupby('adherence_category').agg({
        outcome: 'mean',
        'hospitalizations': 'sum',
        'total_cost': 'mean',
        'patient_id': 'count'
    }).rename(columns={'patient_id': 'n_patients'})

    # Dose-response relationship
    from scipy.stats import spearmanr
    correlation, pvalue = spearmanr(cohort['pdc'], cohort[outcome])

    return {
        'medication': medication,
        'outcome': outcome,
        'outcomes_by_adherence': outcomes_by_adherence,
        'dose_response_correlation': correlation,
        'pvalue': pvalue
    }
```

## Data Quality Considerations

### Common Data Quality Issues

```python
def assess_rwd_quality(dataset):
    """Assess real-world data quality"""

    quality_metrics = {}

    # Completeness
    quality_metrics['completeness'] = {
        field: (1 - dataset[field].isna().mean()) * 100
        for field in dataset.columns
    }

    # Timeliness (data lag)
    quality_metrics['data_lag_days'] = (
        pd.Timestamp.now() - dataset['last_updated'].max()
    ).days

    # Consistency (logical checks)
    quality_metrics['consistency_issues'] = {
        'death_before_birth': (
            dataset['death_date'] < dataset['birth_date']
        ).sum(),
        'discharge_before_admission': (
            dataset['discharge_date'] < dataset['admission_date']
        ).sum(),
        'age_negative': (dataset['age'] < 0).sum()
    }

    # Plausibility (value ranges)
    quality_metrics['implausible_values'] = {
        'systolic_bp_out_of_range': (
            (dataset['systolic_bp'] < 50) | (dataset['systolic_bp'] > 300)
        ).sum(),
        'heart_rate_out_of_range': (
            (dataset['heart_rate'] < 20) | (dataset['heart_rate'] > 300)
        ).sum()
    }

    # Uniqueness (duplicate records)
    quality_metrics['duplicate_patients'] = (
        dataset.duplicated(subset=['patient_id']).sum()
    )

    return quality_metrics
```

## Regulatory Considerations

### FDA Real-World Evidence Framework

**Use Cases:**
1. Post-market safety surveillance
2. New indications for approved drugs
3. Satisfying post-approval study requirements
4. Supporting regulatory decisions

**Data Standards:**
- CDISC (Clinical Data Interchange Standards Consortium)
- Sentinel Common Data Model
- FDA's Adverse Event Reporting System (FAERS)

### EMA (European Medicines Agency)

- Similar focus on RWE for regulatory decisions
- Emphasis on data quality and transparency

---

*Real-World Evidence Reference - Methodologies for generating clinical evidence from real-world healthcare data to support research and regulatory decisions.*
