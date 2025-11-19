# Risk Scoring Implementation Guide

## Risk Scoring Model Framework

```
CUSTOMER RISK SCORE =
    (Customer_Risk × 0.25) +
    (Geographic_Risk × 0.20) +
    (Industry_Risk × 0.15) +
    (Transaction_Risk × 0.20) +
    (Behavioral_Risk × 0.10) +
    (Regulatory_Risk × 0.10)

Result: 0-100 scale
├─ 0-25: Low Risk (CDD baseline)
├─ 25-50: Medium Risk (Enhanced CDD)
├─ 50-75: High Risk (EDD required)
└─ 75-100: Very High Risk (Senior review/decline)
```

## Feature Engineering

```
CUSTOMER ATTRIBUTES:
├─ Type: Individual, Business, Trust, etc.
├─ Size: Revenue, AUM, transaction volume
├─ Age: How long with institution
├─ Ownership: Direct, complex structure
├─ Public Status: PEP, director, etc.
├─ Regulatory Status: Previous violations

GEOGRAPHIC FACTORS:
├─ Customer Location Risk Score
├─ Beneficial Owner Location Risk
├─ Counterparty Location Risk
├─ Transaction Destination Risk
├─ FATF Gray List Status
└─ Sanction Jurisdiction Exposure

INDUSTRY FACTORS:
├─ Industry Classification Risk
├─ Cash Intensity Score
├─ ML Vulnerability Assessment
├─ Regulatory Oversight Level
├─ Business Stability Score
└─ International Trade Exposure

TRANSACTION PROFILE:
├─ Average Monthly Volume
├─ Transaction Volatility (std dev)
├─ Geographic Concentration
├─ Counterparty Diversity
├─ Payment Method Mix
└─ Cross-Border Percentage

BEHAVIORAL PATTERNS:
├─ Consistency with Profile
├─ Deviation from Historical
├─ Seasonal Patterns
├─ Growth Rate
├─ Payment Timing
└─ Communication Responsiveness

REGULATORY RED FLAGS:
├─ SAR Historical Rate
├─ Complaint History
├─ Examination Findings
├─ Adverse Media Matches
├─ Regulatory Violations
└─ Sanctioned List Proximity
```

## Model Development

**Step 1: Data Preparation**
```python
import pandas as pd
import numpy as np

# Load training data (historical customers with known risk)
df = pd.read_csv('customer_data.csv')

# Feature engineering
df['geographic_risk'] = df['customer_country'].map(country_risk_scores)
df['industry_risk'] = df['industry'].map(industry_risk_scores)
df['customer_size_risk'] = pd.qcut(df['annual_revenue'], 5, labels=[1,2,3,4,5])
df['transaction_volatility'] = df.groupby('customer_id')['amount'].transform('std')
df['customer_tenure_days'] = (datetime.now() - df['account_open_date']).dt.days

# Remove outliers and missing values
df = df.dropna(subset=['risk_label'])
df = df[(df['amount'] > 0) & (df['amount'] < df['amount'].quantile(0.99))]
```

**Step 2: Model Selection**
```python
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

# Prepare features and labels
X = df[feature_columns]
y = df['risk_label']  # 0=Low, 1=Medium, 2=High, 3=VeryHigh

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train model
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    objective='multi:softprob',
    num_class=4
)
model.fit(X_scaled, y)

# Feature importance analysis
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
```

**Step 3: Model Validation**
```python
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix, classification_report

# Cross-validation
cv_scores = cross_val_score(model, X_scaled, y, cv=5)
print(f"CV Score: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")

# Test set evaluation
y_pred = model.predict(X_test_scaled)
print(classification_report(y_test, y_pred))

# ROC curve analysis (for binary case)
fpr, tpr, thresholds = roc_curve(y_test, model.predict_proba(X_test_scaled)[:, 1])
auc = auc(fpr, tpr)
print(f"AUC: {auc:.3f}")
```

## Risk Score Application

**Real-Time Scoring:**
```python
def calculate_customer_risk_score(customer_data):
    """
    Calculate risk score for customer
    Returns: risk_score (0-100), risk_category, key_factors
    """

    # Extract features
    features = extract_features(customer_data)

    # Normalize features
    X = scaler.transform([features])

    # Predict risk class
    risk_probability = model.predict_proba(X)[0]
    risk_score = np.argmax(risk_probability) * 33.33

    # Get feature contribution (SHAP values)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    # Determine category
    if risk_score < 25:
        category = "LOW"
        cdd_level = "BASIC"
    elif risk_score < 50:
        category = "MEDIUM"
        cdd_level = "ENHANCED"
    elif risk_score < 75:
        category = "HIGH"
        cdd_level = "ENHANCED_DUE_DILIGENCE"
    else:
        category = "VERY_HIGH"
        cdd_level = "SENIOR_REVIEW"

    return {
        'risk_score': risk_score,
        'category': category,
        'cdd_level': cdd_level,
        'key_factors': get_top_factors(shap_values),
        'confidence': risk_probability.max()
    }
```

## Monitoring and Recalibration

**Monitoring Procedures:**
- Monthly: Review model performance
- Quarterly: Check for data drift
- Semi-annually: Accuracy assessment
- Annually: Full model retraining

**Recalibration Triggers:**
- Accuracy drops below 85%
- False positive rate exceeds 15%
- False negative rate exceeds 2%
- New risk types emerge
- Regulatory changes

## Risk Score Output

```
RISK ASSESSMENT REPORT:

Customer: John Doe
Account: ACC-123456
Assessment Date: 2024-01-15

RISK SCORE: 42 (MEDIUM RISK)

Components:
├─ Customer Attributes: 35 (25%)
├─ Geographic Risk: 45 (20%)
├─ Industry Risk: 40 (15%)
├─ Transaction Risk: 50 (20%)
├─ Behavioral Risk: 30 (10%)
└─ Regulatory Risk: 25 (10%)

CDD REQUIREMENTS: Enhanced Due Diligence

Key Risk Factors:
1. Geographic: UK (medium-risk jurisdiction)
2. Industry: Trade/Import-Export (elevated risk)
3. Transaction: Volatility above baseline
4. Geographic concentration: Eastern Europe (25%)

Recommended Actions:
- Obtain source of funds documentation
- Verify beneficial ownership
- Quarterly risk reassessment
- Enhanced transaction monitoring

Next Review Date: 2024-04-15
Recommended Action: PROCEED with Enhanced CDD
```

## Performance Metrics

| Metric | Target | Frequency |
|--------|--------|-----------|
| Model Accuracy | > 85% | Quarterly |
| Precision (High Risk) | > 90% | Monthly |
| Recall (High Risk) | > 80% | Monthly |
| False Positive Rate | < 10% | Monthly |
| False Negative Rate | < 2% | Monthly |
| AUC Score | > 0.85 | Quarterly |

## Best Practices

1. **Regular Retraining** - Retrain model annually or on data drift
2. **Explainability** - Understand why model scores customers
3. **Validation** - Test on holdout set, cross-validation
4. **Feature Engineering** - Domain expertise in feature selection
5. **Monitoring** - Track model performance in production
6. **Human Review** - High-risk scores require analyst verification
7. **Documentation** - Document model rationale and assumptions
8. **Testing** - Test on known high/low risk scenarios
9. **Regulatory Alignment** - Ensure compliance with FATF guidance
10. **Continuous Improvement** - Update model as regulations change

## Regulatory Considerations

- **FATF Guidance**: Risk-based approach to AML/CFT
- **Fair Lending**: Ensure risk score doesn't discriminate
- **Transparency**: Document scoring methodology
- **Data Quality**: Accurate input data essential
- **Testing**: Regular accuracy validation
- **Override Procedures**: Clear procedures for exceptions
