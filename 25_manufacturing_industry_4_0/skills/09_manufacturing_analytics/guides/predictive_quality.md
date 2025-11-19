# Predictive Quality Implementation Guide

## Executive Summary

This guide provides a comprehensive roadmap for implementing predictive quality analytics in manufacturing operations. Predictive quality uses machine learning to identify potential quality issues before they occur, enabling proactive corrective actions.

### Expected Benefits
- 30-50% reduction in scrap and rework
- 5-15 percentage point improvement in first pass yield
- 40-60% reduction in customer returns
- 20-30% reduction in cost of quality

### Implementation Timeline
- **Phase 1** (Months 1-2): Discovery and planning
- **Phase 2** (Months 2-4): Data preparation and model development
- **Phase 3** (Months 4-6): Validation and refinement
- **Phase 4** (Months 6-12): Deployment and optimization

---

## Phase 1: Discovery and Planning

### Step 1.1: Problem Definition

**Identify Quality Challenges**:
- What are the top defect types?
- What is the current FPY (first pass yield)?
- What is the cost of poor quality (COPQ)?
- Where are the biggest opportunities?

**Data-Driven Assessment**:
```python
# Analyze defect distribution
import pandas as pd
import numpy as np

# Load defect data
defects = pd.read_csv('historical_defects.csv')

# Top defect types
print("Defect Type Distribution:")
print(defects['defect_type'].value_counts())
print("\nDefect Type by Cost:")
print((defects.groupby('defect_type')['cost'].sum()).sort_values(ascending=False))

# FPY calculation
total_units = defects.shape[0]
good_units = defects[defects['defect_type'].isna()].shape[0]
fpy = (good_units / total_units) * 100
print(f"\nCurrent FPY: {fpy:.1f}%")
```

**Define Success Criteria**:
- Target FPY improvement (e.g., 92% → 97%)
- Acceptable detection latency (e.g., < 5 minutes after defect occurs)
- Model accuracy targets (e.g., 95% precision, 90% recall)
- ROI timeline and investment limits

### Step 1.2: Feasibility Assessment

**Data Availability**:
- What quality data is available? (test results, images, measurements)
- What process parameters are measured?
- What is the data retention period?
- Data quality: completeness, accuracy, consistency

**Technical Resources**:
- Data infrastructure capacity
- Analytics team skills and capacity
- Computing resources (GPU, storage)
- Integration capabilities with existing systems

**Process Knowledge**:
- Are failure modes well understood?
- What causes each defect type?
- What lead indicators exist?
- Are there known relationships to parameters?

### Step 1.3: Business Case Development

**ROI Calculation**:
```python
# Calculate potential savings
current_fpy = 0.92  # 92%
target_fpy = 0.97   # 97%

units_per_year = 1_000_000
gross_margin = 0.40
scrap_rate_current = 1 - current_fpy
scrap_rate_target = 1 - target_fpy

# Calculate savings
scrap_units_avoided = units_per_year * (scrap_rate_current - scrap_rate_target)
revenue_saved = scrap_units_avoided * (units_per_year / current_fpy) * gross_margin

# Implementation costs
development_cost = 100_000
infrastructure_cost = 50_000
training_cost = 20_000
annual_maintenance = 30_000

# Calculate ROI
year_1_roi = (revenue_saved - annual_maintenance - development_cost - infrastructure_cost - training_cost) / (development_cost + infrastructure_cost + training_cost)

print(f"Scrap Units Avoided: {scrap_units_avoided:,}")
print(f"Annual Revenue Saved: ${revenue_saved:,.0f}")
print(f"Year 1 ROI: {year_1_roi*100:.1f}%")
```

**Stakeholder Buy-In**:
- Present business case to leadership
- Align with strategic objectives
- Address concerns and risks
- Secure budget and resources

### Step 1.4: Project Planning

**Team Structure**:
- Project sponsor (executive)
- Project manager (coordination)
- Quality engineer (domain expertise)
- Data scientist (model development)
- Data engineer (infrastructure)
- Operations representative (integration)

**Timeline and Milestones**:
- Month 1: Data preparation (50%)
- Month 2: Feature engineering and model training
- Month 3: Model validation and testing
- Month 4-5: Pilot deployment (single line)
- Month 6-12: Full deployment and optimization

**Risk Management**:
- Model accuracy insufficient for deployment
- Data quality issues preventing training
- Change management and operator resistance
- Integration challenges with existing systems

---

## Phase 2: Data Preparation and Model Development

### Step 2.1: Data Collection and Integration

**Quality Data Sources**:
```python
# Integrate multiple data sources
import pandas as pd
from datetime import datetime, timedelta

# Load quality inspection data
quality_data = pd.read_csv('quality_inspections.csv', parse_dates=['timestamp'])

# Load process parameters
process_data = pd.read_csv('process_parameters.csv', parse_dates=['timestamp'])

# Load environmental data
environment_data = pd.read_csv('environmental.csv', parse_dates=['timestamp'])

# Merge data on timestamp (closest match within 5 minutes)
merged_data = pd.merge_asof(
    quality_data.sort_values('timestamp'),
    process_data.sort_values('timestamp'),
    on='timestamp',
    tolerance=pd.Timedelta('5min'),
    direction='nearest'
)

merged_data = pd.merge_asof(
    merged_data,
    environment_data.sort_values('timestamp'),
    on='timestamp',
    tolerance=pd.Timedelta('5min'),
    direction='nearest'
)

print(f"Merged dataset shape: {merged_data.shape}")
print(f"Date range: {merged_data['timestamp'].min()} to {merged_data['timestamp'].max()}")
```

**Required Data**:
1. **Quality Outcomes**:
   - Binary: Pass/Fail
   - Multi-class: Defect type
   - Continuous: Dimension measurement
   - Image data: Product appearance

2. **Process Parameters**:
   - Temperature, pressure, flow rate
   - Equipment settings and configurations
   - Production rate and cycle time
   - Material lot and supplier

3. **Equipment Condition**:
   - Equipment age and maintenance history
   - Vibration and acoustic signals
   - Power consumption
   - Current conditions and stress

4. **Contextual Data**:
   - Time of day (circadian patterns)
   - Shift and operator information
   - Raw material batch/lot
   - Environmental conditions

### Step 2.2: Data Cleaning and Preprocessing

**Handle Missing Values**:
```python
import pandas as pd
import numpy as np

# Identify missing data
print("Missing values:")
print(merged_data.isnull().sum())

# Strategy 1: Remove rows with missing critical features
merged_data = merged_data.dropna(subset=['product_id', 'quality_result'])

# Strategy 2: Forward fill for time-series data
merged_data['temperature'] = merged_data['temperature'].fillna(method='ffill')

# Strategy 3: Mean imputation for non-critical features
merged_data['humidity'] = merged_data['humidity'].fillna(merged_data['humidity'].mean())

# Strategy 4: Flag missing values as a separate category
merged_data['material_supplier'].fillna('Unknown', inplace=True)

print(f"Rows after cleaning: {merged_data.shape[0]}")
```

**Handle Outliers**:
```python
# Identify outliers using IQR method
def remove_outliers(df, columns, iqr_multiplier=1.5):
    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - iqr_multiplier * IQR
        upper_bound = Q3 + iqr_multiplier * IQR

        # Flag outliers
        df[f'{col}_outlier'] = (df[col] < lower_bound) | (df[col] > upper_bound)

        # Option 1: Remove outliers
        # df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]

        # Option 2: Cap at bounds
        df[col] = df[col].clip(lower_bound, upper_bound)

    return df

# Apply to numeric columns
numeric_cols = merged_data.select_dtypes(include=[np.number]).columns
merged_data = remove_outliers(merged_data, numeric_cols)
```

**Handle Imbalanced Data**:
```python
# Check class distribution
print("Quality outcome distribution:")
print(merged_data['quality_result'].value_counts(normalize=True))

# For imbalanced data, use techniques like:
# 1. Stratified sampling
from sklearn.model_selection import train_test_split

train, test = train_test_split(
    merged_data,
    test_size=0.2,
    stratify=merged_data['quality_result'],
    random_state=42
)

# 2. Oversampling minority class
from imblearn.over_sampling import SMOTE

# Will be used during model training
# smote = SMOTE(sampling_strategy='auto')
# X_resampled, y_resampled = smote.fit_resample(X, y)
```

### Step 2.3: Feature Engineering

**Create Meaningful Features**:
```python
import pandas as pd
import numpy as np

# 1. Time-based features
merged_data['hour'] = merged_data['timestamp'].dt.hour
merged_data['day_of_week'] = merged_data['timestamp'].dt.dayofweek
merged_data['month'] = merged_data['timestamp'].dt.month
merged_data['is_shift_start'] = merged_data['hour'].isin([6, 14, 22]).astype(int)

# 2. Lag features (previous observations)
merged_data['prev_temp'] = merged_data['temperature'].shift(1)
merged_data['prev_pressure'] = merged_data['pressure'].shift(1)

# 3. Rolling statistics (moving averages)
merged_data['temp_rolling_mean_5'] = merged_data['temperature'].rolling(5).mean()
merged_data['temp_rolling_std_5'] = merged_data['temperature'].rolling(5).std()

# 4. Rate of change features
merged_data['temp_rate_of_change'] = merged_data['temperature'].diff()
merged_data['pressure_acceleration'] = merged_data['pressure'].diff().diff()

# 5. Interaction features
merged_data['temp_pressure_interaction'] = (
    merged_data['temperature'] * merged_data['pressure']
)

# 6. Domain-specific features (based on process knowledge)
# Example: Deviation from optimal range
optimal_temp = 95
merged_data['temp_deviation'] = np.abs(merged_data['temperature'] - optimal_temp)

# Categorical encoding
merged_data['equipment_age_category'] = pd.cut(
    merged_data['equipment_age_days'],
    bins=[0, 365, 730, 1825, np.inf],
    labels=['new', 'standard', 'aging', 'old']
)

print(f"Features after engineering: {merged_data.shape[1]}")
print(f"Feature names: {merged_data.columns.tolist()}")
```

**Feature Selection**:
```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Prepare data
X = merged_data.drop(['timestamp', 'quality_result'], axis=1)
y = merged_data['quality_result']

# Handle categorical variables
X_encoded = pd.get_dummies(X, drop_first=True)

# Feature importance using Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_encoded, y)

# Get feature importance
feature_importance = pd.DataFrame({
    'feature': X_encoded.columns,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

print("Top 20 Most Important Features:")
print(feature_importance.head(20))

# Select top features (e.g., 80% of cumulative importance)
cumsum = feature_importance['importance'].cumsum()
num_features = (cumsum <= cumsum.iloc[-1] * 0.8).sum()
top_features = feature_importance.head(num_features)['feature'].tolist()

print(f"\nSelected {len(top_features)} features out of {len(X_encoded.columns)}")
```

### Step 2.4: Model Development

**Split Data**:
```python
from sklearn.model_selection import train_test_split

X_train, X_temp, y_train, y_temp = train_test_split(
    X_final, y, test_size=0.3, stratify=y, random_state=42
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42
)

print(f"Training set: {X_train.shape}")
print(f"Validation set: {X_val.shape}")
print(f"Test set: {X_test.shape}")
```

**Train Multiple Models**:
```python
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
import numpy as np

models = {
    'Logistic Regression': LogisticRegression(max_iter=1000),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
}

results = {}

for name, model in models.items():
    # Train
    model.fit(X_train, y_train)

    # Predict
    y_pred_train = model.predict(X_train)
    y_pred_val = model.predict(X_val)
    y_pred_test = model.predict(X_test)

    # Get probabilities for threshold tuning
    y_pred_proba_val = model.predict_proba(X_val)[:, 1]
    y_pred_proba_test = model.predict_proba(X_test)[:, 1]

    # Evaluate
    results[name] = {
        'train_f1': f1_score(y_train, y_pred_train),
        'val_f1': f1_score(y_val, y_pred_val),
        'test_f1': f1_score(y_test, y_pred_test),
        'test_precision': precision_score(y_test, y_pred_test),
        'test_recall': recall_score(y_test, y_pred_test),
        'test_auc': roc_auc_score(y_test, y_pred_proba_test),
        'model': model,
        'proba_val': y_pred_proba_val,
        'proba_test': y_pred_proba_test
    }

# Compare models
results_df = pd.DataFrame({
    'Train F1': [results[m]['train_f1'] for m in results],
    'Val F1': [results[m]['val_f1'] for m in results],
    'Test F1': [results[m]['test_f1'] for m in results],
    'Precision': [results[m]['test_precision'] for m in results],
    'Recall': [results[m]['test_recall'] for m in results],
    'AUC-ROC': [results[m]['test_auc'] for m in results]
}, index=results.keys())

print("Model Comparison:")
print(results_df)
```

**Hyperparameter Tuning**:
```python
from sklearn.model_selection import GridSearchCV

# Define parameter grid
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15],
    'min_samples_split': [5, 10, 20],
    'min_samples_leaf': [2, 4, 8]
}

# Grid search
gb_model = GradientBoostingClassifier(random_state=42)
grid_search = GridSearchCV(
    gb_model,
    param_grid,
    cv=5,
    scoring='f1',
    n_jobs=-1
)

grid_search.fit(X_train, y_train)

print(f"Best parameters: {grid_search.best_params_}")
print(f"Best CV F1 score: {grid_search.best_score_:.4f}")

# Use best model
best_model = grid_search.best_estimator_
```

---

## Phase 3: Validation and Refinement

### Step 3.1: Threshold Tuning

**Optimize Decision Threshold**:
```python
# Default threshold is 0.5
# For imbalanced data or different business needs, optimize

from sklearn.metrics import precision_recall_curve
import matplotlib.pyplot as plt

# Get probability predictions
y_proba = best_model.predict_proba(X_val)[:, 1]

# Calculate precision-recall curve
precision, recall, thresholds = precision_recall_curve(y_val, y_proba)

# Find optimal threshold based on business criteria
# Example: Maximize F1 score
f1_scores = 2 * (precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-10)
optimal_idx = np.argmax(f1_scores)
optimal_threshold = thresholds[optimal_idx]

print(f"Optimal threshold: {optimal_threshold:.3f}")
print(f"At this threshold:")
print(f"  Precision: {precision[optimal_idx]:.3f}")
print(f"  Recall: {recall[optimal_idx]:.3f}")
print(f"  F1 Score: {f1_scores[optimal_idx]:.3f}")

# Plot PR curve
plt.figure(figsize=(10, 6))
plt.plot(recall, precision)
plt.axvline(x=recall[optimal_idx], color='r', linestyle='--', label=f'Optimal threshold: {optimal_threshold:.3f}')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.legend()
plt.grid(True)
plt.show()
```

### Step 3.2: Pilot Testing

**Select Pilot Production Line**:
- Represents 10-30% of total production
- Full data collection capability
- Cooperative operations team
- Measurable baseline

**Deployment Steps**:
1. Install real-time model serving
2. Generate daily predictions
3. Validate predictions against outcomes
4. Refine thresholds based on results
5. Train operators on new information

**Success Metrics** (first 4 weeks):
- Model accuracy on new data
- Alert response time
- Corrective action effectiveness
- Data collection completeness

---

## Phase 4: Deployment and Optimization

### Step 4.1: Production Deployment

**Model Serving**:
```python
# Save trained model
import joblib

joblib.dump(best_model, 'quality_model.pkl')

# Create prediction service
class QualityPredictor:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)
        self.threshold = 0.45  # Optimized threshold

    def predict(self, data):
        """
        data: dict with feature values
        returns: {'defect_risk': float, 'alert': bool, 'recommendation': str}
        """
        # Prepare features
        X = np.array([data[f] for f in self.feature_names]).reshape(1, -1)

        # Get prediction
        probability = self.model.predict_proba(X)[0, 1]
        alert = probability > self.threshold

        # Generate recommendation
        if alert:
            recommendation = self._get_recommendation(data)
        else:
            recommendation = "No action needed"

        return {
            'defect_risk': float(probability),
            'alert': bool(alert),
            'confidence': float(max(self.model.predict_proba(X)[0])),
            'recommendation': recommendation
        }

    def _get_recommendation(self, data):
        # Based on feature values, suggest corrective actions
        if data['temperature'] > 100:
            return "Reduce temperature immediately"
        elif data['pressure'] > 200:
            return "Check pressure regulation"
        else:
            return "Review process parameters"

# Deploy service
predictor = QualityPredictor('quality_model.pkl')
```

**Integration with Production Systems**:
- API for MES integration
- Real-time data pipelines
- Alert notification system
- Dashboard visualization
- Data logging and audit trail

### Step 4.2: Monitoring and Maintenance

**Model Performance Monitoring**:
```python
# Track model performance over time
def monitor_model_performance(y_actual, y_pred, y_proba, dates):
    """
    Monitor model performance metrics over time
    """
    daily_results = []

    for date in dates.unique():
        mask = dates == date
        daily_results.append({
            'date': date,
            'accuracy': accuracy_score(y_actual[mask], y_pred[mask]),
            'precision': precision_score(y_actual[mask], y_pred[mask]),
            'recall': recall_score(y_actual[mask], y_pred[mask]),
            'f1': f1_score(y_actual[mask], y_pred[mask]),
            'auc': roc_auc_score(y_actual[mask], y_proba[mask])
        })

    return pd.DataFrame(daily_results)

# Alert if performance degrades
def check_performance_drift(current_metrics, baseline_metrics, threshold=0.05):
    """
    Check if current metrics have drifted from baseline
    """
    drifts = []
    for metric in ['accuracy', 'precision', 'recall', 'f1']:
        drift = abs(current_metrics[metric] - baseline_metrics[metric])
        if drift > threshold:
            drifts.append(f"{metric}: {drift:.3f}")

    if drifts:
        print(f"Performance drift detected: {', '.join(drifts)}")
        print("Action: Schedule model retraining")
        return True
    return False
```

**Retraining Schedule**:
- Monthly: Review performance and retrain if drift detected
- Quarterly: Full model validation and hyperparameter review
- Annually: Major model updates and architecture review

---

## Implementation Checklist

**Phase 1: Discovery and Planning**
- [ ] Define quality problem and success criteria
- [ ] Assess data availability and quality
- [ ] Develop ROI business case
- [ ] Secure budget and stakeholder buy-in
- [ ] Establish project team and timeline

**Phase 2: Data Preparation and Model Development**
- [ ] Collect and integrate quality data
- [ ] Clean and preprocess data
- [ ] Engineer relevant features
- [ ] Select top features
- [ ] Train and compare models
- [ ] Tune hyperparameters
- [ ] Document model specifications

**Phase 3: Validation and Refinement**
- [ ] Tune decision thresholds
- [ ] Design pilot deployment
- [ ] Test on pilot line
- [ ] Validate predictions
- [ ] Refine based on feedback

**Phase 4: Deployment and Optimization**
- [ ] Deploy production model
- [ ] Integrate with MES/systems
- [ ] Train operators
- [ ] Set up monitoring and alerts
- [ ] Establish retraining schedule
- [ ] Measure and report ROI
- [ ] Plan continuous improvement

