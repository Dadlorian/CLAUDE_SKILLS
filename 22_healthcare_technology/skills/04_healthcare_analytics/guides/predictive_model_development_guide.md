# Predictive Model Development Guide

## Model Development Lifecycle

### 1. Problem Definition
- Define prediction target (outcome)
- Determine prediction window (e.g., 30-day readmission)
- Specify use case and intervention

### 2. Data Preparation
```python
# Feature extraction
features = extract_features(
    population='inpatient_discharges',
    lookback_period='6_months',
    feature_categories=[
        'demographics',
        'diagnoses',
        'procedures',
        'medications',
        'labs',
        'vitals',
        'utilization_history'
    ]
)

# Handle missing data
features = impute_missing(features, strategy='median')

# Create target variable
target = define_outcome(
    event='readmission',
    time_window=30,  # days
    population=features.index
)
```

### 3. Train/Validation/Test Split
```python
# Temporal split (recommended for healthcare)
train = data[data['year'].isin([2020, 2021])]
validation = data[data['year'] == 2022]
test = data[data['year'] == 2023]
```

### 4. Model Training
```python
from sklearn.ensemble import GradientBoostingClassifier

model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5
)

model.fit(X_train, y_train)
```

### 5. Model Evaluation
```python
from sklearn.metrics import roc_auc_score, classification_report

# AUC-ROC
auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])

# Precision, Recall, F1
print(classification_report(y_test, model.predict(X_test)))

# Calibration
from sklearn.calibration import calibration_curve
prob_true, prob_pred = calibration_curve(y_test, y_pred_proba, n_bins=10)
```

### 6. Model Interpretation
```python
import shap

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)
shap.summary_plot(shap_values, X_test)
```

### 7. Model Deployment
- Batch scoring: Nightly runs
- Real-time scoring: API endpoint
- EHR integration: BPA/alerts

### 8. Monitoring
- Track model performance over time
- Detect concept drift
- Retrain schedule (quarterly/annually)

## Best Practices

1. **Clinical Validation**: Engage clinicians throughout
2. **Interpretability**: Use explainable models for high-stakes decisions
3. **Fairness**: Assess bias across demographics
4. **Temporal Validation**: Use future data for testing
5. **Prospective Validation**: Pilot before full deployment

---

*Predictive Model Development Guide*
