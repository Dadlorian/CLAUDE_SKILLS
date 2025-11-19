# Risk Stratification Reference

## Overview

Risk stratification categorizes patients by their predicted healthcare needs, costs, and adverse event risks to enable targeted interventions and resource allocation in value-based care.

## HCC (Hierarchical Condition Category) Model

### Overview

**Purpose**: Medicare Advantage risk adjustment for capitation payments
**Managed by**: CMS (Centers for Medicare & Medicaid Services)
**Model Version**: V24 (current), V28 (implemented 2024)

### HCC Basics

**Risk Adjustment Factor (RAF) Score:**
```
RAF Score = Demographic Factors + Disease Burden (HCCs) + Interactions

Avg RAF = 1.0 (national average)
RAF > 1.0 = Higher cost/sicker than average
RAF < 1.0 = Lower cost/healthier than average

Example:
- Healthy 65-year-old: RAF ~ 0.30-0.40
- 75-year-old with diabetes + CHF: RAF ~ 2.5-3.5
```

**Payment Calculation:**
```
Monthly Payment = Base Rate × RAF Score

Example:
Base Rate = $850 PMPM
Patient RAF = 2.5
Payment = $850 × 2.5 = $2,125 PMPM
```

### HCC Categories (V24 Model)

**79 HCC Categories organized hierarchically:**

```
Example HCC Hierarchy - Diabetes:
HCC 19: Diabetes with Acute Complications (highest)
HCC 18: Diabetes with Chronic Complications
HCC 17: Diabetes with Ophthalmic or Unspecified Complications
HCC 18: Diabetes without Complication (lowest)

Rule: Patient assigned to HIGHEST HCC in hierarchy
```

**High-Value HCCs (Large RAF Weights):**

| HCC | Description | RAF Weight (V24) |
|-----|-------------|------------------|
| HCC 8 | Metastatic Cancer | 2.659 |
| HCC 9 | Lung Cancer | 1.323 |
| HCC 10 | Lymphoma, Other Cancers | 1.093 |
| HCC 17 | Diabetes with Acute Complications | 0.318 |
| HCC 18 | Diabetes with Chronic Complications | 0.318 |
| HCC 85 | CHF | 0.323 |
| HCC 96 | Specified Heart Arrhythmias | 0.307 |
| HCC 108 | COPD | 0.328 |
| HCC 111 | Aspiration and Bacterial Pneumonia | 0.697 |

### HCC Calculation

**Step 1: Identify Qualifying Diagnoses**
```sql
-- Extract HCC-eligible diagnoses from past 12 months
SELECT DISTINCT
    p.patient_key,
    d.diagnosis_code,
    h.hcc_category,
    h.hcc_description,
    h.coefficient AS hcc_weight
FROM dim_patient p
JOIN fact_diagnosis d ON p.patient_key = d.patient_key
JOIN ref_icd10_to_hcc_mapping h ON d.diagnosis_code = h.icd10_code
WHERE d.diagnosis_date BETWEEN '2023-01-01' AND '2023-12-31'
    AND d.encounter_type IN ('Inpatient', 'Outpatient')  -- Exclude labs-only
    AND p.medicare_advantage = 1;
```

**Step 2: Apply Hierarchy Rules**
```python
def apply_hcc_hierarchies(patient_hccs):
    """Apply HCC hierarchical rules"""

    hierarchy_rules = {
        # Diabetes hierarchy
        19: [17, 18, 19],  # HCC 19 overrides 17, 18, 19
        18: [17, 18],      # HCC 18 overrides 17, 18
        17: [17],          # HCC 17 overrides itself only

        # CHF hierarchy
        85: [85, 86, 87],

        # COPD hierarchy
        108: [108, 109, 110, 111, 112]
    }

    final_hccs = set(patient_hccs)

    for superior_hcc, subordinate_hccs in hierarchy_rules.items():
        if superior_hcc in patient_hccs:
            # Remove all subordinate HCCs
            for subordinate in subordinate_hccs:
                if subordinate != superior_hcc:
                    final_hccs.discard(subordinate)

    return final_hccs
```

**Step 3: Calculate RAF Score**
```python
def calculate_raf_score(patient_id, year):
    """Calculate CMS-HCC RAF score"""

    patient = get_patient_demographics(patient_id)

    # Demographic factors
    age = year - patient['year_of_birth']
    gender = patient['gender']
    medicaid = patient['dual_eligible']  # Medicare + Medicaid
    disabled = patient['disabled_status']
    institutional = patient['institutional_status']

    # Get demographic coefficient
    demo_coefficient = get_demographic_coefficient(age, gender, medicaid, disabled, institutional)

    # Get HCCs from diagnoses
    patient_hccs = get_patient_hccs(patient_id, year)
    final_hccs = apply_hcc_hierarchies(patient_hccs)

    # Sum HCC coefficients
    hcc_coefficient = sum(get_hcc_coefficient(hcc) for hcc in final_hccs)

    # Disease interactions
    interaction_coefficient = calculate_disease_interactions(final_hccs, demo_coefficient)

    # Total RAF
    raf_score = demo_coefficient + hcc_coefficient + interaction_coefficient

    return {
        'patient_id': patient_id,
        'raf_score': round(raf_score, 3),
        'demographic_component': demo_coefficient,
        'disease_component': hcc_coefficient,
        'interaction_component': interaction_coefficient,
        'hccs': list(final_hccs)
    }
```

**Step 4: Disease Interactions**
```python
# Example interactions (partial list)
disease_interactions = {
    'CHF_COPD': {
        'hccs': [85, 108],
        'coefficient': 0.141
    },
    'CHF_Diabetes': {
        'hccs': [85, 17, 18, 19],
        'coefficient': 0.154
    },
    'COPD_Diabetes': {
        'hccs': [108, 17, 18, 19],
        'coefficient': 0.190
    },
    'Diabetes_CHF_COPD': {
        'hccs': [17, 18, 19, 85, 108],
        'coefficient': 0.398
    }
}
```

### HCC Coding Best Practices

**Annual Diagnosis Documentation:**
```
- HCCs must be documented ANNUALLY
- Diagnosis must be documented in face-to-face encounter
- Documentation must support diagnosis
- Specificity matters (code to highest specificity)
```

**Example:**
```
❌ E11.9 - Type 2 diabetes without complications (HCC 19)
   RAF Weight: 0.104

✓ E11.22 - Type 2 diabetes with diabetic chronic kidney disease (HCC 18)
   RAF Weight: 0.318

Result: 3x higher RAF by coding to specificity
```

**Suspected vs. Confirmed:**
```
Inpatient: "Suspected" diagnoses acceptable
Outpatient: Only CONFIRMED diagnoses count for HCC
```

## Risk Stratification Models

### Johns Hopkins ACG (Adjusted Clinical Groups)

**Overview:**
- Comprehensive risk adjustment system
- Uses diagnoses, pharmacy, demographics
- Produces resource utilization bands (RUBs)

**Risk Categories:**
```
RUB 0: Non-users (no healthcare utilization)
RUB 1: Healthy users (low utilization)
RUB 2: Low morbidity
RUB 3: Moderate morbidity
RUB 4: High morbidity
RUB 5: Very high morbidity
```

**ACG Categories:**
- 93 mutually exclusive categories
- Based on persistency, severity, etiology

### 3M Clinical Risk Groups (CRGs)

**Overview:**
- Episode-based risk grouping
- Severity levels within conditions
- Predictive of future costs

**CRG Status Levels:**
```
1. Healthy (no significant chronic conditions)
2. History of significant acute illness
3. Single minor chronic condition
4. Minor chronic conditions in multiple systems
5. Single dominant chronic condition
6. Significant chronic conditions in multiple systems
7. Dominant chronic in 3+ systems
8. Dominant and metastatic malignancies
9. Catastrophic conditions
```

### MEG (Episode Treatment Groups)

**Overview:**
- Groups services into clinical episodes
- Analyzes cost and quality per episode
- Identifies variation and opportunities

**Example Episodes:**
```
- Hip replacement (all related services)
- Diabetes management (annual)
- Pneumonia episode (acute)
- Maternity care (full episode)
```

## Custom Risk Stratification

### Multidimensional Risk Model

```python
class PopulationRiskStratification:
    def __init__(self):
        self.clinical_weight = 0.35
        self.utilization_weight = 0.30
        self.psychosocial_weight = 0.20
        self.cost_weight = 0.15

    def calculate_clinical_risk(self, patient_id):
        """Clinical complexity score"""

        # Chronic condition count
        chronic_conditions = get_chronic_conditions(patient_id)
        condition_count = len(chronic_conditions)

        # HCC RAF score
        raf_score = get_hcc_raf_score(patient_id)

        # Comorbidity indices
        charlson_score = calculate_charlson_index(patient_id)
        elixhauser_score = calculate_elixhauser_index(patient_id)

        # Medications
        medication_count = get_active_medication_count(patient_id)
        high_risk_meds = get_high_risk_medication_count(patient_id)

        # Normalize to 0-1 scale
        clinical_risk = (
            min(condition_count / 10, 1.0) * 0.25 +
            min(raf_score / 3.0, 1.0) * 0.30 +
            min(charlson_score / 10, 1.0) * 0.20 +
            min(medication_count / 15, 1.0) * 0.15 +
            min(high_risk_meds / 5, 1.0) * 0.10
        )

        return clinical_risk

    def calculate_utilization_risk(self, patient_id):
        """Healthcare utilization patterns"""

        # Last 12 months utilization
        ed_visits = count_ed_visits(patient_id, months=12)
        ip_admits = count_inpatient_admits(patient_id, months=12)
        readmissions = count_30day_readmissions(patient_id, months=12)

        # Primary care engagement
        pcp_visits = count_pcp_visits(patient_id, months=12)

        # No-show rate
        noshow_rate = calculate_noshow_rate(patient_id, months=12)

        # Normalize
        utilization_risk = (
            min(ed_visits / 6, 1.0) * 0.30 +
            min(ip_admits / 3, 1.0) * 0.35 +
            min(readmissions / 2, 1.0) * 0.20 +
            (1.0 - min(pcp_visits / 4, 1.0)) * 0.10 +  # Inverse - fewer PCP visits = higher risk
            noshow_rate * 0.05
        )

        return utilization_risk

    def calculate_psychosocial_risk(self, patient_id):
        """Social determinants and behavioral health"""

        factors = get_sdoh_factors(patient_id)

        risk_score = 0.0

        # Social determinants
        if factors.get('lives_alone') and get_patient_age(patient_id) > 75:
            risk_score += 0.15
        if factors.get('transportation_barriers'):
            risk_score += 0.15
        if factors.get('food_insecurity'):
            risk_score += 0.20
        if factors.get('housing_unstable'):
            risk_score += 0.20

        # Behavioral health
        if has_condition(patient_id, 'Depression'):
            risk_score += 0.10
        if has_condition(patient_id, 'Anxiety'):
            risk_score += 0.05
        if has_condition(patient_id, 'Substance_Abuse'):
            risk_score += 0.15

        # Area deprivation
        adi = get_area_deprivation_index(patient_id)
        if adi > 80:  # High deprivation
            risk_score += 0.10

        return min(risk_score, 1.0)

    def calculate_cost_risk(self, patient_id):
        """Historical and predicted costs"""

        # Trailing 12-month costs
        actual_cost_12mo = get_total_cost(patient_id, months=12)

        # Predicted next-year cost
        predicted_cost = predict_next_year_cost(patient_id)

        # Normalize (assume $50k+ is very high)
        cost_risk = min(predicted_cost / 50000, 1.0)

        return cost_risk

    def stratify_patient(self, patient_id):
        """Comprehensive risk stratification"""

        clinical = self.calculate_clinical_risk(patient_id)
        utilization = self.calculate_utilization_risk(patient_id)
        psychosocial = self.calculate_psychosocial_risk(patient_id)
        cost = self.calculate_cost_risk(patient_id)

        # Weighted composite score
        composite_score = (
            clinical * self.clinical_weight +
            utilization * self.utilization_weight +
            psychosocial * self.psychosocial_weight +
            cost * self.cost_weight
        )

        # Assign tier
        if composite_score >= 0.70:
            tier = 'High'
            intervention = 'Intensive Care Management'
            care_coordinator_ratio = 50  # 1 coordinator per 50 patients
        elif composite_score >= 0.40:
            tier = 'Medium'
            intervention = 'Care Coordination'
            care_coordinator_ratio = 150
        elif composite_score >= 0.20:
            tier = 'Low'
            intervention = 'Self-Management Support'
            care_coordinator_ratio = None
        else:
            tier = 'Healthy'
            intervention = 'Prevention & Wellness'
            care_coordinator_ratio = None

        return {
            'patient_id': patient_id,
            'composite_score': round(composite_score, 3),
            'risk_tier': tier,
            'recommended_intervention': intervention,
            'care_coordinator_ratio': care_coordinator_ratio,
            'component_scores': {
                'clinical': round(clinical, 3),
                'utilization': round(utilization, 3),
                'psychosocial': round(psychosocial, 3),
                'cost': round(cost, 3)
            }
        }
```

### Predictive Risk Models

**Future High-Cost Prediction:**
```python
from sklearn.ensemble import GradientBoostingRegressor

def train_cost_prediction_model():
    """Train model to predict next-year costs"""

    # Features
    features = [
        # Historical costs
        'cost_total_12mo', 'cost_ip_12mo', 'cost_ed_12mo',
        'cost_pharma_12mo', 'cost_outpatient_12mo',

        # Utilization
        'ed_visits_12mo', 'ip_admits_12mo', 'readmits_30d',

        # Clinical
        'age', 'chronic_condition_count', 'charlson_score',
        'raf_score', 'medication_count',

        # Specific conditions (binary)
        'has_chf', 'has_copd', 'has_diabetes', 'has_ckd',
        'has_cancer', 'has_depression',

        # SDOH
        'area_deprivation_index', 'lives_alone',
        'transportation_barriers'
    ]

    # Target: Next year total cost
    target = 'cost_next_year'

    # Train
    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=6,
        random_state=42
    )

    model.fit(X_train[features], y_train[target])

    return model

# Identify future high-cost patients
def identify_future_high_cost(threshold_pmpm=5000):
    """Identify patients predicted to be high-cost next year"""

    all_patients = get_active_patients()
    predictions = []

    for patient_id in all_patients:
        features = extract_patient_features(patient_id)
        predicted_annual_cost = cost_model.predict([features])[0]
        predicted_pmpm = predicted_annual_cost / 12

        if predicted_pmpm >= threshold_pmpm:
            predictions.append({
                'patient_id': patient_id,
                'predicted_annual_cost': predicted_annual_cost,
                'predicted_pmpm': predicted_pmpm,
                'current_12mo_cost': features['cost_total_12mo'],
                'cost_increase_pct': (
                    (predicted_annual_cost - features['cost_total_12mo']) /
                    features['cost_total_12mo'] * 100
                )
            })

    return pd.DataFrame(predictions).sort_values('predicted_annual_cost', ascending=False)
```

## Risk Stratification Reporting

### Population Distribution

```sql
-- Risk tier distribution
SELECT
    risk_tier,
    COUNT(*) AS patient_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_population,
    SUM(total_cost_12mo) AS total_cost,
    AVG(total_cost_12mo) AS avg_cost_pmpm,
    AVG(composite_risk_score) AS avg_risk_score
FROM patient_risk_stratification
GROUP BY risk_tier
ORDER BY
    CASE risk_tier
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
        WHEN 'Healthy' THEN 4
    END;
```

### Risk Migration Analysis

```sql
-- Track patients moving between risk tiers
WITH current_risk AS (
    SELECT patient_key, risk_tier AS current_tier
    FROM patient_risk_stratification
    WHERE score_date = '2024-01-01'
),
prior_risk AS (
    SELECT patient_key, risk_tier AS prior_tier
    FROM patient_risk_stratification
    WHERE score_date = '2023-01-01'
)
SELECT
    pr.prior_tier,
    cr.current_tier,
    COUNT(*) AS patient_count
FROM current_risk cr
JOIN prior_risk pr ON cr.patient_key = pr.patient_key
GROUP BY pr.prior_tier, cr.current_tier
ORDER BY pr.prior_tier, cr.current_tier;
```

---

*Risk Stratification Reference - Methods for categorizing patients by predicted healthcare needs and costs to enable targeted interventions.*
