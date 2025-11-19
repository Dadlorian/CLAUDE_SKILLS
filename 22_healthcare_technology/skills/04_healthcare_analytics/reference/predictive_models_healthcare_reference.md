# Predictive Models in Healthcare Reference

## Overview

Predictive analytics in healthcare uses statistical and machine learning techniques to forecast clinical events, patient outcomes, and resource utilization, enabling proactive interventions and optimized care delivery.

## Common Predictive Healthcare Models

### Hospital Readmission Prediction

#### 30-Day All-Cause Readmission

**Clinical Problem**: 15-20% of Medicare patients readmitted within 30 days
**Financial Impact**: CMS Hospital Readmissions Reduction Program (HRRP) penalties

**Prediction Target**: Binary classification (readmitted vs. not readmitted within 30 days)

**Feature Categories:**

1. **Demographics**
   - Age
   - Gender
   - Race/ethnicity
   - Marital status
   - Insurance type

2. **Clinical History**
   - Number of prior admissions (past 6/12 months)
   - Comorbidity count
   - Charlson Comorbidity Index
   - Elixhauser Comorbidity Index
   - HCC risk score
   - Specific chronic conditions (CHF, COPD, diabetes, CKD)

3. **Index Admission**
   - Length of stay
   - ICU admission
   - Primary diagnosis (DRG, ICD-10)
   - Discharge disposition
   - Number of procedures
   - Emergency admission vs. elective

4. **Medications**
   - Polypharmacy (5+ medications)
   - High-risk medications
   - New medication starts
   - Medication changes during admission

5. **Labs & Vitals (at discharge)**
   - Hemoglobin
   - Sodium, potassium
   - Creatinine, eGFR
   - BNP (for CHF)
   - Blood pressure
   - Weight change

6. **Utilization History**
   - ED visits (past 6 months)
   - No-show rate to appointments
   - PCP visit frequency
   - Specialist visit count

7. **Social Determinants**
   - Distance from hospital
   - Area Deprivation Index
   - Living alone
   - Homelessness
   - Transportation barriers

**Model Development Example:**

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, classification_report
from imblearn.over_sampling import SMOTE

# Load data
df = load_discharge_data()

# Feature engineering
features = [
    'age', 'gender', 'charlson_score', 'length_of_stay',
    'prior_admits_6mo', 'prior_admits_12mo', 'icu_admission',
    'emergency_admit', 'num_medications', 'hemoglobin_discharge',
    'sodium_discharge', 'creatinine_discharge', 'chf_flag',
    'copd_flag', 'diabetes_flag', 'ckd_flag', 'ed_visits_6mo',
    'area_deprivation_index', 'lives_alone'
]

X = df[features]
y = df['readmitted_30d']

# Handle missing values
X = X.fillna(X.median())

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Handle class imbalance
smote = SMOTE(random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

# Train model
model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42
)
model.fit(X_train_balanced, y_train_balanced)

# Evaluate
y_pred_proba = model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, y_pred_proba)
print(f"AUC-ROC: {auc:.3f}")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
```

**Model Performance Targets:**
- AUC-ROC: 0.70-0.80
- Sensitivity: 60-70% (capture true readmissions)
- Specificity: 65-75%
- PPV: 25-35% (prevalence ~15-20%)

**Clinical Deployment:**
```python
# Real-time scoring at discharge
def score_readmission_risk(patient_id):
    features = extract_patient_features(patient_id)
    risk_score = model.predict_proba(features)[0][1]

    if risk_score > 0.40:  # High risk threshold
        trigger_care_transitions_program(patient_id)
        schedule_follow_up_call(patient_id, within_days=2)
        alert_care_coordinator(patient_id, risk_score)

    return {
        'patient_id': patient_id,
        'risk_score': risk_score,
        'risk_category': 'High' if risk_score > 0.40 else 'Medium' if risk_score > 0.20 else 'Low',
        'recommended_interventions': get_interventions(risk_score)
    }
```

### Sepsis Prediction

#### Early Warning System

**Clinical Problem**: Sepsis mortality increases 7.6% per hour without treatment
**Goal**: Predict sepsis 4-6 hours before clinical recognition

**Prediction Window**: Rolling 4-hour prediction
**Update Frequency**: Every hour (or real-time with streaming vitals)

**Features:**

1. **Vital Signs (trending)**
   - Heart rate (current, mean, max, std over 6h)
   - Respiratory rate (current, trend)
   - Temperature (current, max)
   - Blood pressure (systolic, diastolic, MAP)
   - SpO2 (current, min)
   - Glasgow Coma Scale

2. **Laboratory Values**
   - WBC count, differential
   - Lactate level
   - Creatinine, BUN
   - Bilirubin
   - Platelet count
   - INR, PTT
   - Procalcitonin (if available)

3. **Clinical Context**
   - Age
   - Admission source (ED, transfer, etc.)
   - Primary diagnosis
   - ICU status
   - Mechanical ventilation
   - Vasopressor use
   - Recent surgery
   - Immunocompromised status

4. **Derived Features**
   - SOFA score components
   - qSOFA score
   - SIRS criteria count
   - NEWS2 score
   - Shock index (HR / SBP)

**Model Architecture:**

```python
from sklearn.ensemble import RandomForestClassifier
import numpy as np

class SepsisEarlyWarning:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=20,
            class_weight='balanced'
        )
        self.feature_window = 6  # hours of data

    def extract_time_series_features(self, patient_vitals_df):
        """Extract statistical features from time-series vitals"""
        features = {}

        for vital in ['heart_rate', 'respiratory_rate', 'temperature', 'map']:
            recent = patient_vitals_df[vital].tail(6)  # Last 6 hours

            features[f'{vital}_current'] = recent.iloc[-1]
            features[f'{vital}_mean'] = recent.mean()
            features[f'{vital}_max'] = recent.max()
            features[f'{vital}_min'] = recent.min()
            features[f'{vital}_std'] = recent.std()
            features[f'{vital}_trend'] = np.polyfit(range(len(recent)), recent, 1)[0]

        return features

    def calculate_sofa_score(self, patient_data):
        """Calculate Sequential Organ Failure Assessment score"""
        score = 0

        # Respiration (PaO2/FiO2)
        if patient_data['pao2_fio2'] < 100:
            score += 4
        elif patient_data['pao2_fio2'] < 200:
            score += 3
        elif patient_data['pao2_fio2'] < 300:
            score += 2
        elif patient_data['pao2_fio2'] < 400:
            score += 1

        # Coagulation (platelets)
        if patient_data['platelets'] < 20:
            score += 4
        elif patient_data['platelets'] < 50:
            score += 3
        elif patient_data['platelets'] < 100:
            score += 2
        elif patient_data['platelets'] < 150:
            score += 1

        # Liver (bilirubin)
        if patient_data['bilirubin'] >= 12.0:
            score += 4
        elif patient_data['bilirubin'] >= 6.0:
            score += 3
        elif patient_data['bilirubin'] >= 2.0:
            score += 2
        elif patient_data['bilirubin'] >= 1.2:
            score += 1

        # Cardiovascular (MAP or vasopressors)
        if patient_data['on_vasopressors']:
            score += 3 + patient_data['vasopressor_dose_category']
        elif patient_data['map'] < 70:
            score += 1

        # CNS (Glasgow Coma Scale)
        if patient_data['gcs'] < 6:
            score += 4
        elif patient_data['gcs'] < 10:
            score += 3
        elif patient_data['gcs'] < 13:
            score += 2
        elif patient_data['gcs'] < 15:
            score += 1

        # Renal (creatinine or urine output)
        if patient_data['creatinine'] >= 5.0:
            score += 4
        elif patient_data['creatinine'] >= 3.5:
            score += 3
        elif patient_data['creatinine'] >= 2.0:
            score += 2
        elif patient_data['creatinine'] >= 1.2:
            score += 1

        return score

    def predict_sepsis_risk(self, patient_id):
        """Predict sepsis risk for a patient"""
        # Get recent data
        vitals = get_patient_vitals(patient_id, hours=6)
        labs = get_patient_labs(patient_id, hours=24)
        clinical = get_patient_clinical_data(patient_id)

        # Extract features
        features = {}
        features.update(self.extract_time_series_features(vitals))
        features.update(labs)
        features.update(clinical)
        features['sofa_score'] = self.calculate_sofa_score(features)

        # Predict
        X = pd.DataFrame([features])
        risk_prob = self.model.predict_proba(X)[0][1]

        return {
            'patient_id': patient_id,
            'sepsis_risk': risk_prob,
            'alert_level': 'CRITICAL' if risk_prob > 0.70 else 'WARNING' if risk_prob > 0.40 else 'NORMAL',
            'sofa_score': features['sofa_score'],
            'recommended_action': self.get_recommendations(risk_prob, features)
        }

    def get_recommendations(self, risk, features):
        """Get clinical recommendations based on risk"""
        if risk > 0.70:
            return [
                'Immediate physician evaluation',
                'Order blood cultures × 2',
                'Consider broad-spectrum antibiotics',
                'Check lactate level',
                'Consider ICU transfer'
            ]
        elif risk > 0.40:
            return [
                'Increased monitoring frequency',
                'Recheck vital signs in 1 hour',
                'Consider repeat labs',
                'Notify attending physician'
            ]
        else:
            return ['Continue standard monitoring']
```

**Performance Expectations:**
- AUC: 0.75-0.85
- Alert 4-6 hours before clinical diagnosis
- False positive rate: <10% (minimize alert fatigue)

### Patient Deterioration (Rapid Response)

#### Modified Early Warning Score (MEWS) + ML

**Traditional MEWS:**
```python
def calculate_mews(vitals):
    score = 0

    # Systolic BP
    bp_score = {
        (0, 70): 3, (71, 80): 2, (81, 100): 1,
        (101, 199): 0, (200, 999): 2
    }

    # Heart Rate
    hr_score = {
        (0, 40): 2, (41, 50): 1, (51, 100): 0,
        (101, 110): 1, (111, 129): 2, (130, 999): 3
    }

    # Respiratory Rate
    rr_score = {
        (0, 9): 2, (9, 15): 0, (15, 20): 1,
        (21, 29): 2, (30, 999): 3
    }

    # Temperature (°C)
    temp_score = {
        (0, 35): 2, (35, 38.5): 0, (38.5, 999): 2
    }

    # AVPU (Alert, Voice, Pain, Unresponsive)
    consciousness_score = {'A': 0, 'V': 1, 'P': 2, 'U': 3}

    # Calculate
    score += get_score_from_ranges(vitals['sbp'], bp_score)
    score += get_score_from_ranges(vitals['hr'], hr_score)
    score += get_score_from_ranges(vitals['rr'], rr_score)
    score += get_score_from_ranges(vitals['temp'], temp_score)
    score += consciousness_score.get(vitals['avpu'], 0)

    return score

# MEWS ≥ 5: Trigger rapid response team
```

**Enhanced ML Model:**
Combines MEWS with additional predictors:
- Trend in vital signs (worsening)
- Lab values (lactate, WBC, creatinine)
- Nursing assessments (pain, mobility)
- Prior rapid response calls

**Target**: Predict deterioration 2-4 hours before traditional score triggers

### Length of Stay (LOS) Prediction

#### Inpatient LOS Forecasting

**Use Cases:**
- Bed capacity planning
- Discharge planning
- Resource allocation

**Model Type**: Regression (predict days) or classification (short/medium/long stay)

**Features:**
```python
features = {
    # Demographics
    'age': 65,
    'gender': 'M',

    # Clinical
    'primary_diagnosis_drg': 291,  # Heart failure
    'comorbidity_count': 5,
    'charlson_score': 6,
    'admission_source': 'Emergency',
    'admission_type': 'Emergency',

    # Vitals at admission
    'admission_heart_rate': 105,
    'admission_sbp': 145,
    'admission_respiratory_rate': 22,
    'admission_spo2': 94,

    # Labs at admission
    'admission_hemoglobin': 10.2,
    'admission_creatinine': 1.8,
    'admission_sodium': 133,
    'admission_bun': 42,

    # Historical
    'prior_admits_6mo': 2,
    'prior_los_avg': 4.5,

    # Early hospital course
    'icu_within_24h': True,
    'consultant_count_24h': 2
}
```

**Model:**
```python
from sklearn.ensemble import RandomForestRegressor

def predict_length_of_stay(admission_data):
    model = RandomForestRegressor(n_estimators=100, max_depth=8)

    # Train on historical data
    model.fit(X_train, y_train_los)

    # Predict
    predicted_los = model.predict([admission_data])[0]

    # Provide prediction intervals
    predictions_ensemble = [tree.predict([admission_data])[0]
                           for tree in model.estimators_]

    return {
        'predicted_los_days': round(predicted_los, 1),
        'los_lower_bound': np.percentile(predictions_ensemble, 10),
        'los_upper_bound': np.percentile(predictions_ensemble, 90),
        'confidence': 'High' if np.std(predictions_ensemble) < 1.0 else 'Medium'
    }
```

**Performance:**
- RMSE: < 1.5 days
- R²: 0.40-0.60 (LOS has high variability)

### No-Show Prediction

#### Appointment No-Show Model

**Problem**: 15-30% no-show rate reduces capacity and revenue

**Features:**
1. **Patient History**
   - Prior no-show rate
   - Prior late cancellation rate
   - Total appointment history
   - Days since last visit

2. **Appointment Characteristics**
   - Time of day
   - Day of week
   - Lead time (days from scheduling to appointment)
   - Appointment type (new vs. follow-up)
   - Department/specialty

3. **Demographics**
   - Age
   - Insurance type
   - ZIP code / distance from clinic

4. **SDOH**
   - Transportation barriers
   - Language barriers
   - Area Deprivation Index

5. **Clinical**
   - Chronic condition count
   - Recent hospitalization
   - Active prescriptions

**Model:**
```python
from xgboost import XGBClassifier

class NoShowPredictor:
    def __init__(self):
        self.model = XGBClassifier(
            max_depth=6,
            n_estimators=150,
            learning_rate=0.1,
            scale_pos_weight=2  # Handle class imbalance
        )

    def predict_no_show(self, appointment_id):
        features = extract_appointment_features(appointment_id)

        no_show_prob = self.model.predict_proba([features])[0][1]

        # Intervention logic
        if no_show_prob > 0.50:  # High risk
            send_reminder_sms(appointment_id, timing='1_day_before')
            send_reminder_call(appointment_id, timing='1_day_before')
            offer_transportation_assistance(appointment_id)
        elif no_show_prob > 0.30:  # Medium risk
            send_reminder_sms(appointment_id, timing='2_days_before')
            send_reminder_email(appointment_id)

        return {
            'appointment_id': appointment_id,
            'no_show_probability': no_show_prob,
            'risk_category': 'High' if no_show_prob > 0.50 else 'Medium' if no_show_prob > 0.30 else 'Low',
            'intervention_triggered': no_show_prob > 0.30
        }
```

**Impact:**
- 20-30% reduction in no-shows with targeted interventions
- Precision > 60% for high-risk predictions
- Enable overbooking strategies

### Chronic Disease Progression

#### Diabetes Progression to Complications

**Outcomes to Predict:**
- Diabetic retinopathy onset (1-3 years)
- Diabetic nephropathy (CKD stage progression)
- Cardiovascular events
- Diabetic foot ulcers

**Longitudinal Features:**
```python
# Time-varying covariates
longitudinal_features = {
    'hba1c_trajectory': [7.2, 7.8, 8.1, 8.5, 9.2],  # Worsening
    'bp_control_history': [True, True, False, False, False],
    'medication_adherence_pdc': [0.85, 0.75, 0.65, 0.60, 0.55],  # Declining
    'bmi_trajectory': [28, 29, 31, 32, 34],  # Increasing
    'ldl_trajectory': [105, 110, 125, 130, 135]
}

# Use survival analysis or recurrent neural networks
from lifelines import CoxPHFitter

# Cox proportional hazards model
cph = CoxPHFitter()
cph.fit(df, duration_col='time_to_complication', event_col='complication_occurred')

# Predict risk at different time points
risk_1year = cph.predict_survival_function(patient_data, times=[1.0])
risk_3year = cph.predict_survival_function(patient_data, times=[3.0])
```

### CKD Progression to ESRD

**Stages:**
- CKD 3a (eGFR 45-59)
- CKD 3b (eGFR 30-44)
- CKD 4 (eGFR 15-29)
- CKD 5 / ESRD (eGFR <15 or dialysis)

**Prediction Goal**: Time to dialysis initiation

**Key Predictors:**
- Current eGFR and rate of decline
- Proteinuria level (ACR)
- Diabetes status
- Hypertension control
- Cardiovascular disease
- Age, BMI

**Kidney Failure Risk Equation (KFRE):**
```python
import numpy as np

def calculate_kfre_4var(age, sex, egfr, acr):
    """
    4-variable KFRE: Predicts 2 and 5-year risk of ESRD
    Variables: Age, sex, eGFR, ACR
    """
    # Log transformation
    log_acr = np.log(acr) if acr > 0 else 0

    # Coefficient calculation
    score = (
        -0.2201 * (age / 10 - 7.036) +
        0.2467 * (1 if sex == 'M' else 0 - 0.5642) +
        -0.5567 * (egfr / 5 - 7.222) +
        0.4510 * (log_acr - 5.137)
    )

    # 2-year risk
    risk_2y = 1 - 0.9832 ** np.exp(score)

    # 5-year risk
    risk_5y = 1 - 0.9365 ** np.exp(score)

    return {
        'kfre_score': score,
        'esrd_risk_2year': risk_2y,
        'esrd_risk_5year': risk_5y,
        'recommendation': 'Refer to nephrology' if risk_2y > 0.10 else 'Continue monitoring'
    }
```

## Model Development Best Practices

### Data Preparation

**Handling Missing Data:**
```python
# Imputation strategies
from sklearn.impute import SimpleImputer, KNNImputer

# Median for continuous
imputer_median = SimpleImputer(strategy='median')

# Mode for categorical
imputer_mode = SimpleImputer(strategy='most_frequent')

# KNN for complex patterns
imputer_knn = KNNImputer(n_neighbors=5)

# Flag missing values as informative
df['lab_missing'] = df['creatinine'].isna().astype(int)
```

**Class Imbalance:**
```python
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.combine import SMOTETomek

# SMOTE for oversampling minority class
smote = SMOTE(sampling_strategy=0.5)
X_resampled, y_resampled = smote.fit_resample(X, y)

# Combined approach
smote_tomek = SMOTETomek(sampling_strategy=0.5)
```

**Feature Engineering:**
```python
# Interaction terms
df['age_x_charlson'] = df['age'] * df['charlson_score']

# Polynomial features
df['hr_squared'] = df['heart_rate'] ** 2

# Binning
df['age_group'] = pd.cut(df['age'], bins=[0, 50, 65, 80, 120],
                          labels=['<50', '50-65', '65-80', '80+'])

# Temporal features
df['weekend_admit'] = df['admission_date'].dt.dayofweek >= 5
df['hour_of_day'] = df['admission_datetime'].dt.hour
df['month'] = df['admission_date'].dt.month

# Domain-specific scores
df['shock_index'] = df['heart_rate'] / df['systolic_bp']
df['anion_gap'] = df['sodium'] - (df['chloride'] + df['bicarbonate'])
```

### Model Selection

**Algorithm Comparison:**
```python
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier

models = {
    'Logistic Regression': LogisticRegression(max_iter=1000),
    'Random Forest': RandomForestClassifier(n_estimators=100),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100),
    'XGBoost': XGBClassifier(n_estimators=100),
    'Neural Network': MLPClassifier(hidden_layers=(100, 50))
}

for name, model in models.items():
    model.fit(X_train, y_train)
    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    print(f"{name}: AUC = {auc:.3f}")
```

### Model Validation

**Cross-Validation:**
```python
from sklearn.model_selection import cross_val_score, StratifiedKFold

# Stratified K-Fold for imbalanced data
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

cv_scores = cross_val_score(model, X, y, cv=skf, scoring='roc_auc')
print(f"Cross-validated AUC: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
```

**Temporal Validation:**
```python
# Train on 2020-2021, validate on 2022, test on 2023
train = df[df['year'].isin([2020, 2021])]
valid = df[df['year'] == 2022]
test = df[df['year'] == 2023]

# Ensures model generalizes to future data
```

### Model Interpretability

**SHAP Values:**
```python
import shap

# Create explainer
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Summary plot
shap.summary_plot(shap_values, X_test, feature_names=features)

# Individual prediction explanation
shap.force_plot(explainer.expected_value, shap_values[0], X_test.iloc[0])

# Waterfall plot for specific patient
shap.waterfall_plot(shap.Explanation(
    values=shap_values[0],
    base_values=explainer.expected_value,
    data=X_test.iloc[0],
    feature_names=features
))
```

**Feature Importance:**
```python
# For tree-based models
importances = pd.DataFrame({
    'feature': features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

# Permutation importance (model-agnostic)
from sklearn.inspection import permutation_importance

perm_importance = permutation_importance(model, X_test, y_test, n_repeats=10)
```

### Model Monitoring

**Performance Drift Detection:**
```python
def monitor_model_performance(model, new_data, threshold_auc=0.70):
    """Monitor model performance over time"""
    monthly_performance = []

    for month in new_data['month'].unique():
        month_data = new_data[new_data['month'] == month]

        if len(month_data) > 100:
            y_true = month_data['outcome']
            y_pred = model.predict_proba(month_data[features])[:, 1]

            auc = roc_auc_score(y_true, y_pred)
            monthly_performance.append({
                'month': month,
                'auc': auc,
                'alert': auc < threshold_auc,
                'sample_size': len(month_data)
            })

    return pd.DataFrame(monthly_performance)

# Check for concept drift
# If AUC drops significantly, retrain model
```

**Feature Drift:**
```python
from scipy.stats import ks_2samp

def detect_feature_drift(train_data, new_data, features):
    """Detect distribution changes in features"""
    drift_results = []

    for feature in features:
        # Kolmogorov-Smirnov test
        statistic, pvalue = ks_2samp(
            train_data[feature].dropna(),
            new_data[feature].dropna()
        )

        drift_results.append({
            'feature': feature,
            'ks_statistic': statistic,
            'p_value': pvalue,
            'significant_drift': pvalue < 0.05
        })

    return pd.DataFrame(drift_results)
```

## Model Deployment Patterns

### Batch Scoring
```python
# Nightly batch process
def batch_score_readmission_risk():
    """Score all patients discharged today"""
    discharges_today = get_todays_discharges()

    results = []
    for patient_id in discharges_today:
        score = score_readmission_risk(patient_id)
        results.append(score)

        # Persist to database
        save_risk_score(patient_id, score, model_version='v2.1')

    return results
```

### Real-Time Scoring
```python
# API endpoint for real-time scoring
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/predict/sepsis', methods=['POST'])
def predict_sepsis():
    patient_data = request.json

    # Extract features
    features = extract_features(patient_data)

    # Score
    prediction = sepsis_model.predict_proba([features])[0][1]

    return jsonify({
        'patient_id': patient_data['patient_id'],
        'sepsis_risk': float(prediction),
        'timestamp': datetime.now().isoformat(),
        'model_version': 'v1.3'
    })
```

### Integration with EHR
```python
# Best Practice Advisor (BPA) in Epic
def trigger_ehr_alert(patient_id, risk_score, alert_type):
    """Send alert to EHR system"""
    if alert_type == 'sepsis' and risk_score > 0.70:
        create_ehr_alert(
            patient_id=patient_id,
            alert_title='Sepsis Risk Alert',
            alert_message=f'High sepsis risk detected: {risk_score:.1%}',
            severity='High',
            recipients=['Attending', 'Nurse'],
            suggested_orders=['Blood cultures', 'Lactate level', 'Broad-spectrum antibiotics']
        )
```

---

*Predictive Models in Healthcare Reference - Machine learning techniques for forecasting clinical events and enabling proactive care delivery.*
