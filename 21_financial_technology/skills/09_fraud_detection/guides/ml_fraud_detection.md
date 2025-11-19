# Machine Learning Fraud Detection Guide

## Model Selection Strategy

### Phase 1: Baseline Models
```
Start with simple models to establish baseline:

1. Logistic Regression
   - Fast training & inference
   - Interpretable coefficients
   - Handles linear relationships
   - Good for baseline comparison

2. Random Forest
   - Non-linear relationships
   - Feature importance ranking
   - Less prone to overfitting
   - Fast prediction
```

### Phase 2: Advanced Models
```
Upgrade to production-grade models:

1. XGBoost (Recommended)
   - Superior performance
   - Gradient boosting advantages
   - Fast training & prediction
   - Handles missing values
   - Feature interaction detection

2. LightGBM
   - Even faster than XGBoost
   - Lower memory usage
   - Better for large datasets
   - Similar performance

3. Neural Networks
   - Complex non-linear patterns
   - Deep learning advantages
   - Higher training cost
   - Good for rich feature sets
```

## Data Preparation

### Feature Engineering
```
Create meaningful features from raw data:

Transaction Level:
- Amount (raw, log-transformed)
- Amount deviation from baseline
- Time since account creation
- Transaction count (daily, hourly)
- Time between transactions

Customer Level:
- Account age
- Typical transaction amount
- Transaction volatility
- Account velocity
- Refund rate
- Chargeback history

Device Level:
- Device age
- Device fraud history
- Devices per customer
- Device location consistency

Network Level:
- Customers per device
- Cards per customer
- Shared attributes
- Graph clustering
- Ring membership
```

### Feature Scaling
```
Normalize features to similar ranges:

StandardScaler:
- Mean = 0, Std = 1
- Use for: Linear models, neural networks
- Code: (X - mean) / std

MinMaxScaler:
- Range: [0, 1]
- Use for: Tree-based (not needed), neural networks
- Code: (X - min) / (max - min)

RobustScaler:
- Resistant to outliers
- Use for: Outlier-heavy features
- Code: (X - median) / IQR
```

### Handling Missing Values
```
Strategy by Data Type:

Numerical:
- Mean/median imputation
- Forward fill (time series)
- Remove if > 50% missing
- Model-based imputation

Categorical:
- Mode imputation
- Create 'Unknown' category
- Remove if > 50% missing

Code Example:
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy='median')
X_imputed = imputer.fit_transform(X)
```

### Class Imbalance Handling
```
Fraud is typically 0.1-1% of transactions:

1. Oversampling (SMOTE)
```python
from imblearn.over_sampling import SMOTE
smote = SMOTE(sampling_strategy=0.3)
X_resampled, y_resampled = smote.fit_resample(X, y)
```

2. Undersampling
```python
from imblearn.under_sampling import RandomUnderSampler
undersampler = RandomUnderSampler(sampling_strategy=0.3)
X_resampled, y_resampled = undersampler.fit_resample(X, y)
```

3. Cost-Sensitive Learning
```python
# Increase weight of fraud class
class_weights = {0: 1, 1: 100}
model.fit(X, y, sample_weight=class_weights)
```

## Training Pipeline

### Train/Test Split Strategy
```
Time-Based Split (Prevent Leakage):
Train: Jan 1 - Aug 31
Test: Sep 1 - Sep 30

Never shuffle! Fraud patterns change over time.

Validation:
Train: Jan 1 - Jul 31
Validation: Aug 1 - Aug 31
Test: Sep 1 - Sep 30
```

### Cross-Validation
```python
from sklearn.model_selection import StratifiedKFold

skf = StratifiedKFold(n_splits=5, shuffle=False)
for train_idx, val_idx in skf.split(X, y):
    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]
    # Train model
    # Evaluate on validation
```

### Hyperparameter Tuning

**Grid Search**
```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [5, 10, 15],
    'learning_rate': [0.01, 0.1, 0.3]
}

grid_search = GridSearchCV(
    XGBClassifier(),
    param_grid,
    cv=5,
    scoring='roc_auc'
)
grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_
```

**Random Search**
```python
from sklearn.model_selection import RandomizedSearchCV

param_dist = {
    'n_estimators': [50, 100, 200, 300],
    'max_depth': [3, 5, 7, 10, 15],
    'learning_rate': [0.001, 0.01, 0.1, 0.3]
}

random_search = RandomizedSearchCV(
    XGBClassifier(),
    param_dist,
    n_iter=20,
    cv=5,
    scoring='roc_auc'
)
random_search.fit(X_train, y_train)
```

## Model Evaluation

### Classification Metrics
```
Confusion Matrix Interpretation:
                 Predicted Fraud    Predicted Legit
Actual Fraud     TP                 FN
Actual Legit     FP                 TN

Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1 = 2 * (Precision * Recall) / (Precision + Recall)
Specificity = TN / (TN + FP)
```

### ROC-AUC Evaluation
```python
from sklearn.metrics import roc_curve, auc

fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)

# Interpretation:
# 0.5 = Random classifier
# 0.7-0.8 = Good
# 0.8-0.9 = Very good
# > 0.9 = Excellent
```

### PR-AUC Evaluation
```python
from sklearn.metrics import precision_recall_curve, auc

precision, recall, thresholds = precision_recall_curve(y_test, y_pred_proba)
pr_auc = auc(recall, precision)

# Better metric for imbalanced data
# Similar interpretation to ROC-AUC
```

### Threshold Optimization
```python
# Find threshold maximizing F1
thresholds = np.linspace(0, 1, 100)
f1_scores = []

for threshold in thresholds:
    predictions = (y_pred_proba >= threshold).astype(int)
    f1 = f1_score(y_test, predictions)
    f1_scores.append(f1)

best_threshold = thresholds[np.argmax(f1_scores)]
optimal_predictions = (y_pred_proba >= best_threshold).astype(int)
```

## Feature Importance Analysis

### Tree-Based Feature Importance
```python
# Get feature importance from trained model
importances = model.feature_importances_

# Sort and visualize
indices = np.argsort(importances)[::-1]
for i in range(10):
    print(f"{i+1}. {feature_names[indices[i]]}: {importances[indices[i]]:.4f}")

# Visualize
plt.barh(range(len(indices[:10])), importances[indices[:10]])
plt.xlabel('Importance')
plt.show()
```

### SHAP Values (Advanced)
```python
import shap

# Create explainer
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Summary plot
shap.summary_plot(shap_values, X_test)

# Force plot for single instance
shap.force_plot(explainer.expected_value, shap_values[0], X_test[0])
```

### Permutation Importance
```python
from sklearn.inspection import permutation_importance

result = permutation_importance(
    model, X_test, y_test,
    n_repeats=10,
    random_state=42
)

importances = result.importances_mean
indices = np.argsort(importances)[::-1]
```

## Model Monitoring & Retraining

### Performance Monitoring
```
Daily Monitoring:
- Fraud detection rate
- False positive rate
- Model precision/recall
- Score distribution

Weekly Monitoring:
- Performance trend
- Feature distribution drift
- Model calibration
- Comparative analysis

Monthly Review:
- Overall performance
- Model improvements needed
- Retraining triggers
- Threshold adjustments
```

### Drift Detection
```python
# Monitor feature distributions
from scipy.stats import ks_2samp

for feature in X_test.columns:
    stat, p_value = ks_2samp(X_train[feature], X_test[feature])
    if p_value < 0.05:
        print(f"Feature {feature} has drifted!")

# Trigger retraining if multiple features drift
if drifted_features > 5:
    retrain_model()
```

### Automated Retraining
```
Schedule:
- Daily: Monitor performance
- Weekly: Check for drift
- Monthly: Retrain if needed
- Quarterly: Full evaluation

Trigger Retraining If:
- Detection rate drops > 5%
- False positive rate increases > 50%
- Feature drift detected
- New fraud patterns identified
- Performance below target

Process:
1. Collect new labeled data
2. Feature engineering
3. Model training
4. Validation testing
5. A/B testing in production
6. Gradual rollout
7. Performance monitoring
```

## Production Deployment

### Model Serialization
```python
import joblib

# Save model
joblib.dump(model, 'fraud_model.pkl')

# Load model
model = joblib.load('fraud_model.pkl')

# ONNX format for cross-platform
import skl2onnx
initial_type = [('float_input', FloatTensorType([None, 30]))]
onnx_model = convert_sklearn(model, initial_types=initial_type)
with open('model.onnx', 'wb') as f:
    f.write(onnx_model.SerializeToString())
```

### Real-Time Scoring API
```python
from flask import Flask, request
import numpy as np

app = Flask(__name__)
model = joblib.load('fraud_model.pkl')

@app.route('/score', methods=['POST'])
def score():
    data = request.json
    features = np.array([data['features']])
    prediction = model.predict_proba(features)[0][1]
    return {'fraud_score': float(prediction)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Batch Scoring
```python
def batch_score_transactions(transactions_df, model):
    features = transactions_df[feature_columns]
    scores = model.predict_proba(features)[:, 1]
    return pd.DataFrame({
        'transaction_id': transactions_df['id'],
        'fraud_score': scores
    })

# Daily batch job
daily_transactions = get_daily_transactions()
scores = batch_score_transactions(daily_transactions, model)
save_to_database(scores)
```

## Model Explainability

### Feature Contribution Explanation
```python
def explain_prediction(model, instance, feature_names):
    # Get model prediction
    prediction = model.predict(instance)[0]

    # Get feature importance
    importance = model.feature_importances_

    # Calculate contribution
    contributions = instance[0] * importance

    # Sort by absolute contribution
    idx = np.argsort(np.abs(contributions))[::-1]

    print(f"Fraud Score: {prediction:.2%}")
    print("Top Contributing Features:")
    for i in range(5):
        feat_name = feature_names[idx[i]]
        feat_value = instance[0][idx[i]]
        contribution = contributions[idx[i]]
        print(f"  {feat_name}: {feat_value:.2f} ({contribution:.4f})")
```

### Decision Explanation for High-Risk Cases
```
Transaction: 12345
Fraud Score: 0.85 (HIGH RISK)

Top Factors:
1. Transaction Velocity: +0.25
   - 5 transactions in 1 hour (unusual)

2. Device New: +0.20
   - Device not previously used

3. High Amount: +0.15
   - $2,000 vs typical $150

4. Unusual Time: +0.10
   - 2:30 AM (typical: 2 PM)

5. Merchant Risk: +0.05
   - High-risk category (crypto)

Recommendation: Require additional verification
```

## Common Issues & Solutions

### Issue 1: Model Performance Degradation
**Cause**: Fraud patterns evolve, model becomes stale
**Solution**: Implement automated retraining pipeline

### Issue 2: High False Positive Rate
**Cause**: Threshold too aggressive or class imbalance
**Solution**: Adjust threshold, improve features, handle imbalance

### Issue 3: Feature Leakage
**Cause**: Training on data not available at prediction time
**Solution**: Review feature selection, ensure temporal consistency

### Issue 4: Overfitting
**Cause**: Model too complex for data or training too long
**Solution**: Regularization, early stopping, cross-validation

### Issue 5: Poor Calibration
**Cause**: Model probabilities don't match actual fraud rates
**Solution**: Probability calibration, isotonic regression

## Best Practices Summary

1. **Start Simple**: Baseline model before complexity
2. **Feature Engineering**: Most important for performance
3. **Data Quality**: Good data beats complex models
4. **Testing**: Comprehensive before production
5. **Monitoring**: Continuous performance tracking
6. **Feedback Loop**: Use investigation outcomes
7. **Documentation**: Record all decisions & changes
8. **Ethics**: Monitor for bias & fairness
