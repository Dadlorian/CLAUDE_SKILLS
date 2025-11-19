# Risk Stratification Implementation Guide

## Implementation Overview

Risk stratification assigns patients to risk tiers based on predicted healthcare needs, enabling targeted interventions and resource allocation.

## Step 1: Define Risk Model

### Select Risk Dimensions
```python
risk_dimensions = {
    'clinical_risk': {
        'weight': 0.35,
        'components': ['chronic_conditions', 'hcc_score', 'comorbidities']
    },
    'utilization_risk': {
        'weight': 0.30,
        'components': ['ed_visits', 'hospitalizations', 'readmissions']
    },
    'cost_risk': {
        'weight': 0.20,
        'components': ['historical_cost', 'predicted_cost']
    },
    'psychosocial_risk': {
        'weight': 0.15,
        'components': ['sdoh_factors', 'behavioral_health', 'adherence']
    }
}
```

### Define Risk Tiers
```
High Risk (Score ≥ 0.70):
- Intensive care management
- 1 coordinator per 50 patients
- Monthly+ touchpoints

Medium Risk (Score 0.40-0.70):
- Care coordination
- 1 coordinator per 150 patients
- Quarterly touchpoints

Low Risk (Score 0.20-0.40):
- Self-management support
- Educational materials
- Annual wellness visit

Healthy (Score < 0.20):
- Prevention & wellness
- Preventive screenings
- Health promotion
```

## Step 2: Data Collection

### Required Data Elements
- Demographics
- Diagnoses (past 12-24 months)
- Procedures
- Medications
- Labs/vitals
- Utilization history
- SDOH assessments

## Step 3: Score Calculation

See code examples for full implementation.

## Step 4: Intervention Assignment

```python
def assign_intervention(patient_id, risk_score, risk_tier):
    """Assign appropriate intervention"""

    interventions = {
        'High': [
            'Enroll in complex care management',
            'Assign dedicated care coordinator',
            'Monthly care coordinator calls',
            'Home health assessment',
            'Medication reconciliation',
            'Advance care planning'
        ],
        'Medium': [
            'Enroll in care coordination',
            'Quarterly check-ins',
            'Care gap closure outreach',
            'Self-management education'
        ],
        'Low': [
            'Preventive care reminders',
            'Health coaching available',
            'Online resources'
        ]
    }

    return interventions.get(risk_tier, [])
```

## Step 5: Monitoring & Reporting

### Risk Distribution Report
```sql
SELECT
    risk_tier,
    COUNT(*) AS patient_count,
    AVG(risk_score) AS avg_score,
    SUM(total_cost_12mo) AS total_cost
FROM patient_risk_stratification
GROUP BY risk_tier;
```

### Intervention Tracking
- Enrollment rates by tier
- Outreach completion
- Care plan adherence
- Outcome metrics

---

*Risk Stratification Implementation Guide*
