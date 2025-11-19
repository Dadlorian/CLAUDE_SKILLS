# Machine Learning for Remaining Useful Life (RUL) Prediction Guide

## Complete Guide to Building RUL Prediction Models

---

## 1. RUL Prediction Fundamentals

### 1.1 RUL Definition and Scope

**Remaining Useful Life (RUL)**: The time remaining before an asset requires corrective maintenance or replacement.

**RUL Scope:**
```
Current Time (t_now) ────── Predicted RUL ────── Failure Time (t_failure)
                  │◄─────── RUL prediction ─────►│
                  │                              │
                  Current Health State    End-of-Life Threshold
                           0%                   100%

RUL = t_failure - t_now

Uncertainty: RUL estimate ± confidence interval (e.g., 28 ± 7 days)
```

### 1.2 RUL Prediction Approaches

**Run-to-Failure Approach (Supervised Learning):**

```
Equipment 1: Operating hours [0, 1000, 2000, ..., 5000] → Failure
              Features at each timestep
              Labels: RUL = [5000, 4000, 3000, ..., 0]

Equipment 2: Operating hours [0, 1000, 2000, ..., 4200] → Failure
              Features at each timestep
              Labels: RUL = [4200, 3200, 2200, ..., 0]

Model learns: Features → RUL (regression)
```

**Advantages:**
- Realistic failure data
- Direct mapping from current state to RUL
- Handles non-linear degradation

**Disadvantages:**
- Expensive (must run equipment to failure)
- Limited number of failure examples
- Variability between identical equipment

### 1.3 Health Indicator Development

**Health Indicator (HI):** Single metric (0-1 scale) representing equipment degradation state.

**Properties:**
- Monotonically increasing (degradation always progresses)
- 0 at system start (healthy)
- 1 at system failure
- Smooth (minimum noise)
- Normalized (comparable across equipment)

**Construction Methods:**

**Method 1: Statistical Combination**

```python
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def construct_health_indicator_statistical(features_over_time):
    """
    Combine multiple features into single HI using exponential weighting
    """

    # Example: Combine RMS vibration and temperature
    rms_vibration = features_over_time['rms']
    temperature = features_over_time['temperature']

    # Normalize to 0-1 scale
    rms_normalized = (rms_vibration - rms_vibration.min()) / (rms_vibration.max() - rms_vibration.min())
    temp_normalized = (temperature - temperature.min()) / (temperature.max() - temperature.min())

    # Weighted combination
    health_indicator = 0.6 * rms_normalized + 0.4 * temp_normalized

    # Smooth with moving average (reduce noise)
    window = 10
    health_indicator_smooth = np.convolve(health_indicator, np.ones(window)/window, mode='same')

    return health_indicator_smooth
```

**Method 2: PCA-Based Combination**

```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def construct_health_indicator_pca(features_over_time):
    """
    Use first PCA component as health indicator
    - Captures variance explained by degradation
    - Automatically weights features
    """

    # Stack features as matrix (time × features)
    feature_names = ['rms', 'crest_factor', 'kurtosis', 'temperature', 'pressure']
    X = np.column_stack([features_over_time[fname] for fname in feature_names])

    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # PCA: keep first component
    pca = PCA(n_components=1)
    health_indicator = pca.fit_transform(X_scaled).flatten()

    # Normalize to 0-1
    health_indicator = (health_indicator - health_indicator.min()) / (health_indicator.max() - health_indicator.min())

    print(f"PCA variance explained: {pca.explained_variance_ratio_[0]:.1%}")
    print(f"PCA loadings: {dict(zip(feature_names, pca.components_[0]))}")

    return health_indicator
```

**Method 3: Wiener Process (Stochastic Model)**

```
Assumption: Degradation follows Wiener process
HI_t = α×t + β×W_t

Where:
- α: Deterministic degradation rate
- W_t: Brownian motion (random fluctuations)
- β: Noise level

RUL = (1 - HI_current) / α (approximately)

Advantage: Handles stochasticity explicitly
Disadvantage: Assumes linear + Brownian motion (may be oversimplified)
```

---

## 2. Data Preparation for RUL Prediction

### 2.1 Training Dataset Construction

**Run-to-Failure Approach:**

```python
def prepare_rul_training_data(equipment_data_list, sequence_length=30):
    """
    Prepare training data for RUL prediction models

    Args:
        equipment_data_list: List of dicts, each containing:
            - 'features': (T, num_features) array of sensor readings
            - 'failure_time': time of failure
        sequence_length: Lookback window (e.g., 30 days of history)

    Returns:
        X: (num_samples, sequence_length, num_features) training features
        y: (num_samples,) remaining useful life labels
    """

    X = []
    y = []

    for equipment in equipment_data_list:
        features = equipment['features']  # (T, F) array
        failure_time = equipment['failure_time']  # timestep of failure
        total_life = failure_time

        # Create sliding windows
        for t in range(sequence_length, failure_time):
            # Input: features from [t-sequence_length:t]
            window = features[t-sequence_length:t, :]
            X.append(window)

            # Output: RUL at time t
            remaining_time = failure_time - t
            y.append(remaining_time)

    X = np.array(X)  # (N, 30, F)
    y = np.array(y)  # (N,)

    return X, y

# Example usage
X_train, y_train = prepare_rul_training_data([
    {'features': equipment1_features, 'failure_time': 5000},
    {'features': equipment2_features, 'failure_time': 4200},
    {'features': equipment3_features, 'failure_time': 5200}
], sequence_length=30)

print(f"Training set shape: {X_train.shape}")  # (N, 30, num_features)
print(f"RUL labels shape: {y_train.shape}")    # (N,)
print(f"RUL range: {y_train.min():.0f} to {y_train.max():.0f} days")
```

### 2.2 Handling Censored Data

**Censored Data:** Equipment still operating (RUL unknown, equipment hasn't failed yet)

**Approach 1: Exclude (Conservative)**

```python
def filter_uncensored_data(training_data):
    """
    Keep only run-to-failure examples (exclude actively operating equipment)
    """

    uncensored = []
    for equipment in training_data:
        if equipment['is_failed']:  # Only include failed equipment
            uncensored.append(equipment)

    return uncensored

# Disadvantage: Loses information from operating equipment
# Advantage: Simpler, unbiased RUL estimates
```

**Approach 2: Survival Analysis (Advanced)**

```python
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.ensemble import RandomSurvivalForest

# Censored data: (status, time, features)
# status: 1 if failed, 0 if censored (still operating)
# time: failure time (if failed) or monitoring time (if censored)

# Define structured array for survival analysis
y_surv = np.array([(equipment['is_failed'], equipment['time'])
                    for equipment in training_data],
                   dtype=[('status', '?'), ('time', '<f8')])

# Train Cox Proportional Hazards model
model = CoxPHSurvivalAnalysis()
model.fit(X_train, y_surv)

# Predict survival probability at time t
survival_prob = model.predict_survival_function(X_test, return_array=True)

# Estimate RUL (median survival time)
rul = np.median(survival_prob)
```

**Advantage:** Uses information from operating equipment, more data
**Disadvantage:** Requires specialized libraries, assumes proportional hazards

### 2.3 Handling Data Imbalance

**Problem:** Most data from healthy phase, few failures

```
Health state distribution:
- Healthy (0-20% of life): 60% of data
- Early degradation (20-50%): 25% of data
- Advanced degradation (50-80%): 12% of data
- Critical (80-100%): 3% of data

Result: Model trained mostly on healthy data, poor at detecting failure
```

**Solution 1: Stratified Sampling**

```python
from sklearn.model_selection import train_test_split

# Divide data into degradation phases
healthy_indices = np.where(y_train < 0.2 * max_rul)[0]
degraded_indices = np.where(y_train >= 0.2 * max_rul)[0]

# Sample to balance
sample_size_healthy = len(degraded_indices) * 2
sample_indices_healthy = np.random.choice(healthy_indices, sample_size_healthy, replace=False)

# Balanced training set
balanced_indices = np.concatenate([sample_indices_healthy, degraded_indices])
X_balanced = X_train[balanced_indices]
y_balanced = y_train[balanced_indices]
```

**Solution 2: Weighted Loss Function**

```python
# Increase weight for critical RUL samples
sample_weights = np.ones_like(y_train)
critical_threshold = 0.2 * max_rul
sample_weights[y_train < critical_threshold] = 5.0  # 5× weight for critical

# Use in model training
model.fit(X_train, y_train, sample_weight=sample_weights)
```

**Solution 3: Cost-Sensitive Learning**

```
Define custom loss that penalizes errors at critical RUL more:

Loss = Σ |y_pred - y_true| × cost_weight(y_true)

Where:
- cost_weight(RUL < 7 days) = 100 (very expensive to miss critical failures)
- cost_weight(RUL 7-30 days) = 10 (important to catch degradation)
- cost_weight(RUL > 30 days) = 1 (lower penalty for early prediction)
```

---

## 3. RUL Prediction Models

### 3.1 Baseline Models (Simple)

**Linear Regression:**

```python
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Simple model: RUL = a × health_indicator + b

# Prepare data
hi_values = features_over_time['health_indicator'].reshape(-1, 1)  # (T, 1)
rul_values = np.arange(len(hi_values))[::-1]  # RUL decreases from T to 0

# Train
model = LinearRegression()
model.fit(hi_values, rul_values)

# Evaluate
rul_pred = model.predict(hi_values)
rmse = np.sqrt(np.mean((rul_pred - rul_values)**2))
mae = np.mean(np.abs(rul_pred - rul_values))

print(f"RMSE: {rmse:.1f} days, MAE: {mae:.1f} days")

# Visualization
plt.figure(figsize=(10, 6))
plt.plot(rul_values, label='True RUL')
plt.plot(rul_pred, label='Predicted RUL')
plt.xlabel('Time')
plt.ylabel('RUL (days)')
plt.legend()
plt.show()
```

**Polynomial Regression:**

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline

# Model: RUL = a0 + a1×HI + a2×HI² + a3×HI³
# Higher-order captures non-linear degradation

model = Pipeline([
    ('poly_features', PolynomialFeatures(degree=3)),
    ('linear_regression', LinearRegression())
])

model.fit(hi_values, rul_values)
rul_pred = model.predict(hi_values)
rmse = np.sqrt(np.mean((rul_pred - rul_values)**2))

# Interpretation:
# Polynomial degree trade-off:
# - Degree 1: Underfitting (assumes linear)
# - Degree 2-3: Good fit for most equipment
# - Degree 4+: Overfitting (noise learning)
```

### 3.2 Random Forest for RUL Regression

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

# Prepare data (same as earlier)
# X: features matrix (N, F)
# y: RUL labels (N,)

# Train Random Forest
rf_model = RandomForestRegressor(
    n_estimators=200,
    max_depth=20,
    min_samples_split=10,
    min_samples_leaf=5,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)

# Evaluate on test set
y_pred = rf_model.predict(X_test)
mae = np.mean(np.abs(y_pred - y_test))
rmse = np.sqrt(np.mean((y_pred - y_test)**2))
r2 = rf_model.score(X_test, y_test)

print(f"RF Model Performance:")
print(f"  MAE: {mae:.1f} days")
print(f"  RMSE: {rmse:.1f} days")
print(f"  R²: {r2:.3f}")

# Cross-validation (more robust estimate)
cv_scores = cross_val_score(rf_model, X, y, cv=5, scoring='neg_mean_absolute_error')
print(f"  CV MAE: {-cv_scores.mean():.1f} ± {cv_scores.std():.1f} days")

# Feature importance (which sensors matter most?)
importances = rf_model.feature_importances_
feature_names = ['vibration_rms', 'temperature', 'crest_factor', 'kurtosis', 'pressure']
for name, importance in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True):
    print(f"  {name}: {importance:.4f}")

# Advantages:
# ✓ Non-parametric (no assumptions about degradation curve shape)
# ✓ Handles non-linear relationships
# ✓ Robust to outliers
# ✓ Feature importance ranking
# ✓ Fast inference (milliseconds)

# Disadvantages:
# ✗ Requires labeled training data
# ✗ Can extrapolate poorly (predicts ~max_rul for very healthy equipment)
# ✗ No uncertainty quantification (without modifications)
```

### 3.3 Gradient Boosting (XGBoost) for RUL

```python
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Prepare data (same as earlier)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train XGBoost
xgb_model = xgb.XGBRegressor(
    n_estimators=300,
    max_depth=7,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective='reg:squarederror',
    eval_metric='rmse',
    early_stopping_rounds=20,
    random_state=42
)

# Train with early stopping
xgb_model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False
)

# Evaluate
y_pred = xgb_model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"XGBoost Model:")
print(f"  MAE: {mae:.1f} days")
print(f"  RMSE: {rmse:.1f} days")

# Advantages:
# ✓ State-of-the-art performance (often beats Random Forest)
# ✓ Built-in regularization (prevents overfitting)
# ✓ Handles missing values naturally
# ✓ Fast training and inference
# ✓ Feature importance ranking
# ✓ Built-in cross-validation

# Disadvantages:
# ✗ More hyperparameters to tune
# ✗ Computational cost (training slower than Random Forest)
# ✗ Still no native uncertainty quantification
```

### 3.4 LSTM Neural Network for RUL (Deep Learning)

```python
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# Prepare sequence data
# X_train shape: (num_samples, sequence_length, num_features)
# y_train shape: (num_samples,) - RUL label

# Normalize features for neural networks
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train.reshape(-1, X_train.shape[-1])).reshape(X_train.shape)
X_test_scaled = scaler.transform(X_test.reshape(-1, X_test.shape[-1])).reshape(X_test.shape)

# Normalize targets
rul_scaler = StandardScaler()
y_train_scaled = rul_scaler.fit_transform(y_train.reshape(-1, 1)).flatten()
y_test_scaled = rul_scaler.transform(y_test.reshape(-1, 1)).flatten()

# Build LSTM model
model = Sequential([
    LSTM(64, activation='relu', return_sequences=True, input_shape=(sequence_length, num_features)),
    Dropout(0.2),
    LSTM(32, activation='relu', return_sequences=False),
    Dropout(0.2),
    Dense(16, activation='relu'),
    Dense(1, activation='relu')  # RUL is always positive
])

# Compile
model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='mean_squared_error',
    metrics=['mae']
)

# Train with early stopping
early_stop = keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=20,
    restore_best_weights=True
)

history = model.fit(
    X_train_scaled, y_train_scaled,
    validation_data=(X_test_scaled, y_test_scaled),
    epochs=200,
    batch_size=32,
    callbacks=[early_stop],
    verbose=1
)

# Evaluate
y_pred_scaled = model.predict(X_test_scaled)
y_pred = rul_scaler.inverse_transform(y_pred_scaled)  # Rescale to original units
mae = np.mean(np.abs(y_pred.flatten() - y_test))
rmse = np.sqrt(np.mean((y_pred.flatten() - y_test)**2))

print(f"LSTM Model Performance:")
print(f"  MAE: {mae:.1f} days")
print(f"  RMSE: {rmse:.1f} days")

# Advantages:
# ✓ Captures temporal dependencies in sequences
# ✓ Excellent for time-series degradation patterns
# ✓ Automatically learns relevant features
# ✓ Can use variable-length sequences

# Disadvantages:
# ✗ Requires large amounts of training data (100+ failure examples)
# ✗ Slow training (minutes to hours)
# ✗ "Black box" - difficult to interpret
# ✗ Hyperparameter tuning critical
# ✗ Slow inference (seconds per prediction)
```

---

## 4. Uncertainty Quantification in RUL

### 4.1 Prediction Intervals (Regression)

**Bootstrap Method (Non-parametric):**

```python
def predict_rul_with_uncertainty_bootstrap(model, X_test, n_bootstrap=100):
    """
    Generate confidence intervals using bootstrap resampling
    """

    n_samples = len(X_test)
    predictions = np.zeros((n_bootstrap, n_samples))

    for i in range(n_bootstrap):
        # Bootstrap sample from training data
        indices = np.random.choice(len(X_train), size=len(X_train), replace=True)
        X_boot = X_train[indices]
        y_boot = y_train[indices]

        # Train model on bootstrap sample
        model_boot = clone(model)
        model_boot.fit(X_boot, y_boot)

        # Predict
        predictions[i] = model_boot.predict(X_test)

    # Calculate percentiles
    rul_point_estimate = predictions.mean(axis=0)
    rul_lower = np.percentile(predictions, 2.5, axis=0)  # 95% CI lower
    rul_upper = np.percentile(predictions, 97.5, axis=0)  # 95% CI upper

    return rul_point_estimate, rul_lower, rul_upper
```

**Quantile Regression:**

```python
from sklearn.ensemble import GradientBoostingRegressor

# Train three separate models for different quantiles
quantiles = [0.05, 0.50, 0.95]  # 5%, 50% (median), 95% quantiles

models_quantile = {}
for q in quantiles:
    model = GradientBoostingRegressor(
        loss='quantile',
        alpha=q,
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05
    )
    model.fit(X_train, y_train)
    models_quantile[q] = model

# Predict with uncertainty
rul_lower = models_quantile[0.05].predict(X_test)     # 5th percentile
rul_estimate = models_quantile[0.50].predict(X_test)  # Median
rul_upper = models_quantile[0.95].predict(X_test)     # 95th percentile

# Interpretation: 90% confidence interval = [rul_lower, rul_upper]
```

### 4.2 Bayesian Uncertainty (Deep Learning)

```python
# Bayesian LSTM using dropout as approximation to Bayesian inference
# (Dropout as a Bayesian approximation - Gal & Ghahramani)

class BayesianLSTM(keras.Model):
    def __init__(self, sequence_length, num_features):
        super().__init__()
        self.lstm1 = LSTM(64, return_sequences=True)
        self.dropout1 = Dropout(0.2)  # Dropout during inference too
        self.lstm2 = LSTM(32)
        self.dropout2 = Dropout(0.2)
        self.dense = Dense(16, activation='relu')
        self.dropout3 = Dropout(0.2)
        self.output_layer = Dense(1, activation='relu')

    def call(self, x, training=True):
        x = self.lstm1(x, training=training)
        x = self.dropout1(x, training=training)  # Note: training=training
        x = self.lstm2(x, training=training)
        x = self.dropout2(x, training=training)
        x = self.dense(x)
        x = self.dropout3(x, training=training)
        return self.output_layer(x)

# Prediction with uncertainty
model = BayesianLSTM(sequence_length, num_features)

n_forward_passes = 100
predictions = []

for _ in range(n_forward_passes):
    pred = model(X_test, training=True)  # Dropout active even during inference
    predictions.append(pred.numpy())

predictions = np.array(predictions)  # (100, num_samples, 1)

rul_estimate = np.mean(predictions, axis=0).flatten()
rul_uncertainty = np.std(predictions, axis=0).flatten()

# 95% Credible Interval
rul_lower = rul_estimate - 1.96 * rul_uncertainty
rul_upper = rul_estimate + 1.96 * rul_uncertainty
```

---

## 5. Model Validation and Evaluation

### 5.1 Time-Series Cross-Validation

```python
from sklearn.model_selection import TimeSeriesSplit

# Standard k-fold CV: BAD for time-series
# Creates look-ahead bias (training on future data)

# Time-series CV: GOOD
# Respects temporal ordering

tscv = TimeSeriesSplit(n_splits=5)

for train_idx, test_idx in tscv.split(X):
    X_train_fold, X_test_fold = X[train_idx], X[test_idx]
    y_train_fold, y_test_fold = y[train_idx], y[test_idx]

    model = RandomForestRegressor(n_estimators=100)
    model.fit(X_train_fold, y_train_fold)

    mae = mean_absolute_error(y_test_fold, model.predict(X_test_fold))
    print(f"Fold MAE: {mae:.1f} days")

# This ensures model trained only on past data, tested on future
```

### 5.2 Error Metrics Interpretation

```
MAE (Mean Absolute Error):
├─ Definition: Average |predicted_rul - actual_rul|
├─ Unit: Days
├─ Interpretation: On average, prediction off by X days
├─ Good if: < 10% of typical equipment life
└─ Example: Equipment life 5 years → MAE < 183 days

RMSE (Root Mean Squared Error):
├─ Definition: sqrt(mean((predicted_rul - actual_rul)²))
├─ Penalizes large errors more than MAE
├─ Good if: RMSE < 1.3 × MAE (indicates few large errors)
└─ Example: If MAE=10 days, RMSE should be < 13 days

MAPE (Mean Absolute Percentage Error):
├─ Definition: mean(|predicted_rul - actual_rul| / actual_rul) × 100%
├─ Unit: Percent
├─ Good if: < 15%
├─ Advantage: Scale-independent
└─ Example: Same model applied to different equipment types

R² (Coefficient of Determination):
├─ Definition: 1 - (SS_res / SS_tot)
├─ Range: [0, 1] (1 is perfect)
├─ Good if: > 0.8
└─ Interpretation: Model explains X% of RUL variance
```

### 5.3 Over-prediction vs. Under-prediction Trade-off

```
Over-prediction (predict more RUL than actual):
├─ Risk: Equipment fails before predicted maintenance
├─ Cost: Emergency repair costs
├─ Safety impact: Equipment failure risk
├─ Acceptable?: No, for critical safety equipment

Under-prediction (predict less RUL than actual):
├─ Risk: Unnecessary maintenance on healthy equipment
├─ Cost: Wasted maintenance labor and parts
├─ Safety impact: Reduces failure risk (conservative)
├─ Acceptable?: Yes, but increases maintenance costs

Solution: Asymmetric loss function

Loss = Σ w_over × (pred_over - actual)² + w_under × (actual - pred_under)²

Typical: w_over = 5 to 10 (penalize over-prediction heavily)
         w_under = 1

Result: Model biased toward under-prediction (conservative)
```

---

## 6. Production RUL Deployment

### 6.1 Real-Time RUL Scoring

```python
class RULPredictionEngine:
    def __init__(self, model_path, scaler_path):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.feature_window = deque(maxlen=30)  # 30-day lookback

    def update_sensor_reading(self, timestamp, vibration_rms, temperature, pressure):
        """Add new sensor reading to feature buffer"""

        features = {
            'timestamp': timestamp,
            'vibration_rms': vibration_rms,
            'temperature': temperature,
            'pressure': pressure
        }

        self.feature_window.append(features)

    def predict_rul(self):
        """Compute RUL based on current sensor history"""

        if len(self.feature_window) < 30:
            return None  # Insufficient data

        # Convert feature window to array
        feature_array = np.array([
            [f['vibration_rms'], f['temperature'], f['pressure']]
            for f in self.feature_window
        ])

        # Reshape for model (1, 30, 3)
        X = feature_array.reshape(1, 30, 3)

        # Scale features
        X_scaled = self.scaler.transform(X.reshape(-1, 3)).reshape(X.shape)

        # Predict RUL
        rul_days = self.model.predict(X_scaled, verbose=0)[0][0]

        return {
            'rul_days': float(rul_days),
            'maintenance_date': (datetime.now() + timedelta(days=rul_days)).date(),
            'timestamp': datetime.now()
        }

# Usage
engine = RULPredictionEngine('models/rul_model.h5', 'models/scaler.pkl')

# Simulate sensor readings
for day in range(60):
    vibration = 2.0 + day * 0.01 + np.random.normal(0, 0.2)
    temperature = 65 + day * 0.1 + np.random.normal(0, 2)
    pressure = 50 + np.random.normal(0, 1)

    engine.update_sensor_reading(datetime.now(), vibration, temperature, pressure)

    if day % 10 == 0:
        rul_pred = engine.predict_rul()
        if rul_pred:
            print(f"Day {day}: RUL = {rul_pred['rul_days']:.0f} days")
```

### 6.2 Alert Generation from RUL

```python
def generate_rul_alert(rul_prediction):
    """Convert RUL prediction to alert with maintenance recommendation"""

    rul_days = rul_prediction['rul_days']

    # Alert levels
    if rul_days < 3:
        alert = {
            'level': 'CRITICAL',
            'color': 'red',
            'message': f'CRITICAL: Equipment failure in {rul_days:.0f} days',
            'action': 'EMERGENCY MAINTENANCE',
            'escalate': True
        }
    elif rul_days < 7:
        alert = {
            'level': 'SEVERE',
            'color': 'orange',
            'message': f'SEVERE: Schedule maintenance in {rul_days:.0f} days',
            'action': 'Immediate scheduling required',
            'escalate': True
        }
    elif rul_days < 30:
        alert = {
            'level': 'ALERT',
            'color': 'yellow',
            'message': f'ALERT: Plan maintenance in {rul_days:.0f} days',
            'action': 'Schedule within 2 weeks',
            'escalate': False
        }
    else:
        alert = {
            'level': 'INFO',
            'color': 'green',
            'message': f'Equipment healthy, RUL: {rul_days:.0f} days',
            'action': 'Continue monitoring',
            'escalate': False
        }

    return alert
```

---

## References

- Saxena, A., & Goebel, K., "Prognostics and Health Management"
- Kendall, A., & Gal, Y., "What Uncertainties Do We Need in Bayesian Deep Learning"
- XGBoost documentation: https://xgboost.readthedocs.io
- TensorFlow/Keras documentation: https://tensorflow.org
