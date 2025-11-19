# Predictive Maintenance Implementation Guide

## Step-by-Step Guide for Deploying PDM Systems

---

## 1. Assessment and Planning Phase

### 1.1 Equipment Criticality Analysis

**Step 1: Identify Critical Equipment**

Create a list of all equipment with the following attributes:

```
Equipment ID: PUMP-001
Name: Primary Process Pump
Type: Centrifugal pump, 50 GPM, 100 psi
Age: 5 years
Historical failures: 3 failures in 5 years (bearing, seal, impeller wear)
Failure cost estimate: $15,000 (parts + labor + downtime)
Production impact: Critical (line stops if pump fails)
Mean Time Between Failures (MTBF): ~20 months
```

**Criticality Scoring (0-100):**

```
Criticality_Score = (20 × Failure_Cost_Impact)
                   + (30 × Failure_Frequency)
                   + (30 × Production_Consequence)
                   + (20 × Safety_Risk)

Scoring guidance:
- Failure_Cost_Impact: 1-5 (1=<$1K, 5=>$50K)
- Failure_Frequency: 1-5 (1=rare, 5=monthly)
- Production_Consequence: 1-5 (1=none, 5=complete stop)
- Safety_Risk: 1-5 (1=none, 5=critical risk)

Interpretation:
- Score > 70: HIGH priority for PDM
- Score 40-70: MEDIUM priority
- Score < 40: LOW priority (run-to-failure acceptable)
```

**Recommended PDM Budget Allocation by Criticality:**

```
HIGH (> 70 points):
├─ PDM investment: $5K-$20K per equipment
├─ Continuous or frequent (weekly) monitoring
├─ Multiple sensor types (vibration, temperature, pressure)
├─ Real-time alert system
└─ Example: Centrifugal compressor, critical pump

MEDIUM (40-70 points):
├─ PDM investment: $1K-$5K per equipment
├─ Monthly or quarterly monitoring
├─ Single primary sensor (vibration or temperature)
├─ Alert system with less-frequent checks
└─ Example: Secondary pump, medium motor

LOW (< 40 points):
├─ Minimal monitoring ($0-$500)
├─ Visual inspection, operator observation
├─ Manual checks or run-to-failure
└─ Example: Small fan, low-load bearing
```

### 1.2 Failure History Analysis

**Data Collection:**

```
For each equipment, gather:
1. Maintenance records (last 3-5 years)
2. Failure event reports
3. Operating hours / production throughput
4. Environmental conditions
5. Load profile variations
6. Previous repairs and replacements

Create timeline:
┌─────────────┬──────────────┬─────────────┬──────────────┐
│ Date        │ Event Type   │ Description │ Time to Next │
├─────────────┼──────────────┼─────────────┼──────────────┤
│ 2020-01-15  │ Bearing wear │ Noise       │ 30 days      │
│ 2020-02-14  │ Bearing fail │ Outer race  │ 18 months    │
│ 2021-08-10  │ Impeller     │ Cavitation  │ 6 months     │
│ 2021-12-15  │ Seal failure │ Leakage    │ 24 months    │
│ 2023-12-XX  │ ?            │ Predicted   │ ?            │
└─────────────┴──────────────┴─────────────┴──────────────┘

Calculate:
- Mean Time Between Failures (MTBF) = Total operating hours / Number of failures
- Coefficient of Variation = StdDev(TTF) / Mean(TTF)
  * Low variation (CV < 0.5): Degradation-based, good for PDM
  * High variation (CV > 1.5): Random failures, less predictable
```

### 1.3 Data Infrastructure Assessment

**Current Systems Audit:**

```
Question                          Status      Gap Analysis
─────────────────────────────────────────────────────────
SCADA/PLC data available?         Yes/No      What parameters collected?
Database/historian system?        Yes/No      Time-series capability?
Data retention policy?            Yes/No      How long stored?
Network connectivity?             Yes/No      WiFi, Ethernet, cellular?
Edge computing capability?        Yes/No      Real-time processing possible?
Cloud connectivity?               Yes/No      Data sync to cloud systems?
Data security/encryption?         Yes/No      Compliance requirements?
Staff IT expertise?               Yes/No      Training needed?
Budget for infrastructure?        $XXK        Sufficient for PDM needs?
```

**Typical PDM Infrastructure Requirements:**

```
Equipment sensor → MQTT gateway → Time-series database → ML pipeline
                                        ↓
                              Alert/Dashboard system
                                        ↓
                            Maintenance management system
                                        ↓
                              Equipment work order
```

### 1.4 Skill and Resource Assessment

**Team Composition for PDM Implementation:**

```
Role                    FTE     Skills Required
────────────────────────────────────────────────────────────────
Project Manager         0.5     Project planning, stakeholder mgmt
Data Engineer           1.0     Data pipelines, databases, Python
ML/Data Scientist       1.0     Machine learning, statistics, Python
Domain Expert           0.5     Equipment knowledge, failure modes
Maintenance Tech        0.5     Equipment operation, troubleshooting
IT/Infrastructure       0.5     Cloud, networking, deployment
Total                   4.0     (Year 1; Year 2 can reduce to 2.0 FTE)

Training needed:
├─ ML engineers: Equipment operation, condition monitoring
├─ Maintenance staff: ML concepts, alert interpretation
├─ Operations: New alerting procedures, integration with CMMS
└─ Management: PDM ROI metrics, continuous improvement
```

---

## 2. Data Collection and Preparation

### 2.1 Sensor Selection and Installation

**Vibration Sensors:**

```
Equipment Type          Sensor Type           Bandwidth    Cost Range
──────────────────────────────────────────────────────────────────────
Centrifugal pump        ICP Accelerometer     0-10 kHz     $200-600
Motor bearing           ICP Accelerometer     0-20 kHz     $400-800
Gearbox                 Shear IEPE            0-40 kHz     $800-2000
Compressor              Velocity transducer   0-5 kHz      $300-700
Fan                     MEMS accelerometer    0-5 kHz      $50-200

Mounting recommendations:
├─ Magnetic mount (temporary, non-invasive)
├─ Threaded stud mount (permanent, best signal)
├─ Adhesive mount (surface-mounted, medium quality)
└─ Do NOT use handheld probes for continuous monitoring
```

**Temperature Sensors:**

```
Type                Range           Accuracy    Cost        Application
───────────────────────────────────────────────────────────────────────
Thermocouple K      -50 to 1250°C   ±2°C        $10-50      Surface monitoring
RTD Pt100           -50 to 200°C    ±0.5°C      $20-100     Embedded in bearing
Wireless RTD        -20 to 200°C    ±1°C        $100-500    Remote monitoring
IR thermometer      -20 to 1500°C   ±2% reading $100-500    Spot checks
IR camera           -20 to 1500°C   ±2% reading $5K-30K     Thermal imaging

Typical installation:
├─ Bearing housing: RTD or thermocouple in contact
├─ Motor winding: Embedded RTD in coil
├─ Gearbox: Immersion thermostat in oil
├─ Verify: Compare with baseline (healthy equipment reference)
```

**Pressure and Acoustic Sensors:**

```
Pressure transducers:
├─ Pump discharge: 0-200 psi range, ±0.5% accuracy
├─ Compressor: 0-300 psi range, ±0.5% accuracy
├─ Filter pressure drop: 0-50 psi range, ±2% accuracy

Acoustic/ultrasonic:
├─ Bearing friction: 20-40 kHz ultrasonic, detects early friction
├─ Cavitation: Broadband noise 20-100 kHz
├─ Bearing defects: 10-20 kHz envelope analysis
```

### 2.2 Data Collection Frequency and Storage

**Sampling Strategy:**

```
Equipment Criticality    Collection Method    Frequency       Storage
──────────────────────────────────────────────────────────────────────
HIGH (Critical)         Continuous or auto   Every 1-4 hours Full waveform (10 MB/week)
                        data acquisition

MEDIUM (Important)      Automated periodic   Daily or weekly Decimated/features only (1 MB/month)
                        collection task

LOW (Routine)           Manual inspection    Weekly/monthly  Summary statistics only
                        or visual

Data retention:
├─ Raw waveforms: 3 months (space-intensive)
├─ Computed features: 3 years (trends, model training)
├─ Alarms/anomalies: 5+ years (audit trail, learning)
└─ Equipment info: Indefinite (reference and root cause analysis)

Storage system recommendation:
├─ Time-series database: InfluxDB, TimescaleDB, or cloud equivalent
├─ Cloud storage: AWS S3, Azure Blob for long-term archiving
├─ Backup: Daily backups, 30-day retention minimum
└─ Access control: Role-based (operators see their equipment only)
```

### 2.3 Data Quality and Validation

**Data Cleaning Pipeline:**

```
Raw sensor data
    ↓
1. Detect spikes (>5σ deviation)
   └─ Remove or flag as anomaly
    ↓
2. Handle missing values (sensor failure, transmission loss)
   └─ Interpolate (< 1 hour gap), flag as incomplete (> 1 hour)
    ↓
3. Synchronization (ensure all sensors timestamped correctly)
   └─ Re-align if clock drift detected
    ↓
4. Unit conversion (convert to standard units)
   └─ mm/s for vibration, °C for temperature, etc.
    ↓
5. Calibration verification (compare to baseline)
   └─ Alert if sensor drift suspected
    ↓
6. Validate against operational parameters
   └─ Check if measurements reasonable for current speed/load
    ↓
Clean data ready for feature extraction
```

**Data Quality Metrics:**

```
Completeness:   % of expected data points received
                Target: > 95%

Consistency:    Measurements within expected range for operating condition
                Target: 99%+ within ±20% of baseline

Timeliness:     Data latency from sensor to analysis
                Target: < 1 hour for alerts

Accuracy:       Calibration verification (annual or quarterly)
                Target: < 5% error vs. calibration standard
```

---

## 3. Feature Engineering and Model Development

### 3.1 Feature Extraction from Raw Data

**Time-Domain Features (Statistically Simple):**

```python
# For vibration acceleration signal x(t)

def extract_time_domain_features(signal):
    features = {}

    # Basic statistics
    features['rms'] = np.sqrt(np.mean(signal**2))
    features['peak'] = np.max(np.abs(signal))
    features['peak_to_peak'] = np.max(signal) - np.min(signal)

    # Distribution properties
    features['mean'] = np.mean(signal)
    features['std'] = np.std(signal)
    features['skewness'] = scipy.stats.skew(signal)
    features['kurtosis'] = scipy.stats.kurtosis(signal)

    # Impulse indicators
    features['crest_factor'] = features['peak'] / features['rms']
    features['margin'] = (features['peak'] - features['rms']) / features['rms']

    # Energy indicators
    features['energy'] = np.sum(signal**2)
    features['variance'] = features['std']**2

    return features
```

**Frequency-Domain Features (Spectral Content):**

```python
def extract_frequency_features(signal, fs, fault_frequencies=None):
    features = {}

    # FFT analysis
    fft_magnitude = np.abs(np.fft.fft(signal))
    freqs = np.fft.fftfreq(len(signal), 1/fs)

    # Spectral features
    features['spectral_centroid'] = np.sum(freqs * fft_magnitude) / np.sum(fft_magnitude)
    features['spectral_energy'] = np.sum(fft_magnitude**2)
    features['spectral_entropy'] = entropy(fft_magnitude / np.sum(fft_magnitude))

    # Bearing fault frequencies
    if fault_frequencies:
        for fault_name, fault_freq in fault_frequencies.items():
            # Energy around fault frequency (±5%)
            freq_band = np.abs(freqs - fault_freq) / fault_freq < 0.05
            features[f'{fault_name}_energy'] = np.sum(fft_magnitude[freq_band]**2)

    # High-frequency content (> 5 kHz)
    high_freq_band = freqs > 5000
    features['high_freq_energy'] = np.sum(fft_magnitude[high_freq_band]**2)

    return features
```

**Envelope Analysis Features (Demodulation):**

```python
def extract_envelope_features(signal, fs, freq_band=(5000, 40000)):
    """Envelope analysis for bearing fault detection"""

    # 1. Bandpass filter
    sos = scipy.signal.butter(4, freq_band, btype='band', fs=fs, output='sos')
    filtered = scipy.signal.sosfilt(sos, signal)

    # 2. Analytical signal (Hilbert transform)
    analytic_signal = scipy.signal.hilbert(filtered)

    # 3. Envelope (magnitude of analytic signal)
    envelope = np.abs(analytic_signal)

    # 4. Demodulation (low-pass filter of envelope)
    sos_lp = scipy.signal.butter(2, 500, btype='low', fs=fs, output='sos')
    demod_signal = scipy.signal.sosfilt(sos_lp, envelope)

    # 5. Extract features from demodulated signal
    features = extract_time_domain_features(demod_signal)

    # 6. FFT of demodulated signal (look for bearing fault frequencies)
    fft_demod = np.abs(np.fft.fft(demod_signal))
    freqs_demod = np.fft.fftfreq(len(demod_signal), 1/fs)
    features['demod_spectral_energy'] = np.sum(fft_demod**2)

    return features
```

### 3.2 Health Indicator Construction

**Single Health Indicator from Multiple Features:**

```python
# Method 1: Weighted sum of normalized features

def create_health_indicator_weighted(features_dict, weights_dict,
                                   baseline_healthy, baseline_critical):
    """
    Combine multiple features into single health indicator (0-1 scale)

    Args:
        features_dict: {feature_name: value}
        weights_dict: {feature_name: weight}
        baseline_healthy: Feature values at healthy state
        baseline_critical: Feature values at failure state

    Returns:
        health_indicator (0=healthy, 1=failure)
    """

    health_components = {}

    for feature_name, weight in weights_dict.items():
        if feature_name not in features_dict:
            continue

        feature_value = features_dict[feature_name]
        healthy_val = baseline_healthy[feature_name]
        critical_val = baseline_critical[feature_name]

        # Normalize to 0-1 range
        if critical_val != healthy_val:
            normalized = (feature_value - healthy_val) / (critical_val - healthy_val)
            normalized = np.clip(normalized, 0, 1)  # Constrain to 0-1
        else:
            normalized = 0

        health_components[feature_name] = normalized * weight

    # Weighted sum
    health_indicator = sum(health_components.values()) / sum(weights_dict.values())

    return health_indicator

# Example usage
weights = {
    'rms': 0.25,
    'crest_factor': 0.25,
    'high_freq_energy': 0.25,
    'kurtosis': 0.25
}

baseline_healthy = {
    'rms': 2.0,
    'crest_factor': 3.0,
    'high_freq_energy': 100,
    'kurtosis': 3.0
}

baseline_critical = {
    'rms': 20.0,
    'crest_factor': 15.0,
    'high_freq_energy': 10000,
    'kurtosis': 20.0
}

current_features = {
    'rms': 5.0,
    'crest_factor': 5.5,
    'high_freq_energy': 1000,
    'kurtosis': 5.5
}

HI = create_health_indicator_weighted(current_features, weights,
                                      baseline_healthy, baseline_critical)
# HI = 0.35 (equipment in early degradation, 35% toward failure)
```

**Method 2: Principal Component Analysis (PCA)**

```python
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

def create_health_indicator_pca(features_dict_list, baseline_features_list):
    """
    Use first PCA component as health indicator

    Features that vary together with degradation → high loading on PC1
    """

    # Standardize features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features_dict_list)

    # PCA (keep first component)
    pca = PCA(n_components=1)
    health_indicator = pca.fit_transform(features_scaled)

    # Normalize to 0-1 (0=healthy baseline, 1=failure)
    HI_normalized = (health_indicator - health_indicator.min()) / \
                    (health_indicator.max() - health_indicator.min())

    return HI_normalized

# Usage with historical data
HI_trends = []
for timestep in measurement_history:
    features = extract_all_features(timestep.vibration_data, timestep.temperature)
    HI = create_health_indicator_pca([features], baseline_features)
    HI_trends.append(HI)

# Plot trend to visualize degradation progression
```

### 3.3 Machine Learning Model Training

**Random Forest for Fault Classification:**

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import confusion_matrix, roc_auc_score, roc_curve

# Prepare training data
# X: features extracted from historical vibration/temperature data
# y: labels (0=healthy, 1=early_fault, 2=advanced_fault, 3=critical)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train random forest
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=4,
    max_features='sqrt',
    class_weight='balanced',  # Handle imbalanced classes
    random_state=42,
    n_jobs=-1  # Parallel processing
)

rf_model.fit(X_train, y_train)

# Evaluate
train_score = rf_model.score(X_train, y_train)
test_score = rf_model.score(X_test, y_test)
print(f"Train accuracy: {train_score:.3f}, Test accuracy: {test_score:.3f}")

# Feature importance (what features matter most?)
importances = rf_model.feature_importances_
feature_names = [...list of feature names...]
for fname, importance in zip(feature_names, importances):
    print(f"{fname}: {importance:.4f}")

# Cross-validation (more robust estimate)
cv_scores = cross_val_score(rf_model, X, y, cv=5)
print(f"CV scores: {cv_scores}, mean: {cv_scores.mean():.3f}, std: {cv_scores.std():.3f}")

# Save model
import joblib
joblib.dump(rf_model, 'fault_classification_model.pkl')
```

**XGBoost for RUL Regression:**

```python
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Prepare data: X = features, y = remaining days until failure
# Sequence-based: Each training sample is 30 days of features → RUL label

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train XGBoost
xgb_model = XGBRegressor(
    n_estimators=300,
    max_depth=7,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective='reg:squarederror',
    eval_metric='rmse',
    random_state=42
)

# Train with early stopping (prevent overfitting)
xgb_model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    early_stopping_rounds=20,
    verbose=False
)

# Evaluate RUL predictions
y_pred = xgb_model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"MAE: {mae:.1f} days, RMSE: {rmse:.1f} days, R²: {r2:.3f}")

# Prediction on new data
new_features = extract_features(current_vibration_data)
predicted_rul = xgb_model.predict([new_features])[0]
print(f"Estimated RUL: {predicted_rul:.0f} days")

# Save model
xgb_model.save_model('rul_prediction_model.json')
```

---

## 4. Deployment and Integration

### 4.1 Production Inference Pipeline

**Real-Time Scoring Architecture:**

```
Equipment Sensor
    ↓
Data Collection (MQTT/local)
    ↓
Feature Extraction (Python service)
    ↓
Model Inference (trained ML models)
    ↓
Alert Generation (if anomaly/fault detected)
    ↓
Dashboard Visualization
    ↓
Maintenance Management System (work order generation)
```

**Example Python Inference Service:**

```python
import pickle
import numpy as np
from datetime import datetime, timedelta

class PDMInferenceEngine:
    def __init__(self, model_paths):
        self.rf_classifier = pickle.load(open(model_paths['classifier'], 'rb'))
        self.xgb_regressor = pickle.load(open(model_paths['regressor'], 'rb'))
        self.scaler = pickle.load(open(model_paths['scaler'], 'rb'))

    def score_equipment(self, sensor_data):
        """
        Input: Recent sensor readings (vibration, temperature, pressure)
        Output: Fault class + RUL prediction + Confidence
        """

        # Feature extraction
        features = self.extract_features(sensor_data)
        features_scaled = self.scaler.transform([features])

        # Fault classification
        fault_proba = self.rf_classifier.predict_proba(features_scaled)[0]
        fault_class = np.argmax(fault_proba)
        fault_confidence = fault_proba[fault_class]

        # RUL prediction
        predicted_rul_days = self.xgb_regressor.predict(features_scaled)[0]
        predicted_maintenance_date = datetime.now() + timedelta(days=predicted_rul_days)

        # Alert generation
        alert = self.generate_alert(fault_class, fault_proba, predicted_rul_days)

        return {
            'timestamp': datetime.now(),
            'fault_class': fault_class,
            'fault_confidence': fault_confidence,
            'rul_days': predicted_rul_days,
            'maintenance_date': predicted_maintenance_date,
            'alert': alert
        }

    def generate_alert(self, fault_class, fault_proba, rul_days):
        """
        Classify alert severity and generate actionable message
        """

        fault_names = ['healthy', 'early_fault', 'advanced_fault', 'critical']

        if fault_class == 3 or rul_days < 7:  # Critical
            return {
                'severity': 'CRITICAL',
                'message': f'CRITICAL: Failure imminent in {rul_days:.1f} days',
                'recommended_action': 'Schedule emergency maintenance immediately',
                'escalate_to': ['maintenance_manager', 'plant_manager']
            }
        elif fault_class == 2 or rul_days < 30:  # Advanced fault
            return {
                'severity': 'ALERT',
                'message': f'ALERT: Advanced degradation detected, RUL={rul_days:.0f} days',
                'recommended_action': 'Schedule maintenance within 1-2 weeks',
                'escalate_to': ['maintenance_supervisor']
            }
        elif fault_class == 1:  # Early fault
            return {
                'severity': 'WARNING',
                'message': f'WARNING: Early signs of degradation detected',
                'recommended_action': 'Increase monitoring frequency',
                'escalate_to': ['maintenance_technician']
            }
        else:
            return {
                'severity': 'INFO',
                'message': 'Equipment healthy',
                'recommended_action': 'Continue routine monitoring',
                'escalate_to': []
            }

    def extract_features(self, sensor_data):
        """Extract features from raw sensor data"""
        # [Implementation from Section 3.1]
        pass
```

### 4.2 Integration with Maintenance Management System (CMMS)

**Automatic Work Order Generation:**

```python
class CMSSIntegration:
    def __init__(self, cmms_api_endpoint):
        self.api_endpoint = cmms_api_endpoint

    def create_work_order(self, equipment_id, pdm_result):
        """
        Create maintenance work order based on PDM prediction
        """

        if pdm_result['alert']['severity'] not in ['ALERT', 'CRITICAL']:
            return None  # No action needed

        # Determine priority and due date
        if pdm_result['alert']['severity'] == 'CRITICAL':
            priority = 'URGENT'
            due_date = (datetime.now() + timedelta(days=1)).date()
        else:  # ALERT
            priority = 'HIGH'
            due_date = pdm_result['maintenance_date'].date()

        # Determine work type based on fault
        fault_class = pdm_result['fault_class']
        if fault_class == 3:  # Critical
            work_description = "Emergency bearing replacement - imminent failure"
            estimated_hours = 8
        elif fault_class == 2:  # Advanced fault
            work_description = "Bearing inspection and replacement if needed"
            estimated_hours = 6
        else:  # Early fault
            work_description = "Bearing condition assessment and monitoring increase"
            estimated_hours = 2

        work_order = {
            'equipment_id': equipment_id,
            'work_type': 'MAINTENANCE',
            'priority': priority,
            'description': work_description,
            'due_date': due_date.isoformat(),
            'estimated_hours': estimated_hours,
            'source': 'PDM_SYSTEM',
            'confidence': f"{pdm_result['fault_confidence']:.1%}",
            'rul_days': f"{pdm_result['rul_days']:.0f}"
        }

        # Submit to CMMS API
        response = requests.post(
            f"{self.api_endpoint}/work_orders",
            json=work_order,
            headers={'Authorization': f'Bearer {self.api_token}'}
        )

        if response.status_code == 201:
            wo_id = response.json()['id']
            print(f"Work order {wo_id} created for {equipment_id}")
            return wo_id
        else:
            print(f"Error creating work order: {response.text}")
            return None
```

### 4.3 Dashboard and Visualization

**Key Metrics Dashboard:**

```html
<!-- Example dashboard showing PDM metrics -->

Equipment Health Dashboard
═════════════════════════════════════════════════════════════

PUMP-001 | Centrifugal Pump | Status: ⚠️ ALERT
─────────────────────────────────────────────────────────────
Fault Class: Early Degradation (85% confidence)
RUL Prediction: 28 days (maintenance recommended within 4 weeks)

Trend Chart (30 days):
Health Indicator → 0.45 (0=healthy, 1=failure)
 ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁ (trending downward, accelerating)

Sensor Status:
├─ Vibration RMS: 8.5 mm/s (↑ +15% vs. baseline)
├─ Temperature: 72°C (↑ +8°C vs. baseline)
├─ Bearing Fault Freq: Present (BPFO harmonics detected)
└─ Data Quality: 99% (healthy)

Recommendations:
1. Schedule bearing replacement: 2025-01-15 (target date)
2. Increase vibration monitoring to daily
3. Plan for 6-8 hour maintenance window
4. Order replacement bearing (part# BR-2050X)

Historical Performance:
Last failure: 2023-12-15 (bearing outer race spall)
MTBF: 18 months (current trend: extended to 24+ months)
Maintenance cost saved: $8,500 (predictive vs. emergency repair)
```

---

## 5. Monitoring and Continuous Improvement

### 5.1 Performance Monitoring Framework

**Model Performance Tracking:**

```python
class ModelPerformanceMonitor:
    def __init__(self, model_id):
        self.model_id = model_id
        self.predictions = []
        self.actuals = []

    def log_prediction(self, equipment_id, predicted_rul_days, fault_class):
        """Log each prediction"""
        self.predictions.append({
            'timestamp': datetime.now(),
            'equipment_id': equipment_id,
            'predicted_rul_days': predicted_rul_days,
            'fault_class': fault_class
        })

    def log_actual(self, equipment_id, actual_failure_date):
        """Log actual failure for comparison"""
        # Find corresponding prediction
        pred = next(p for p in self.predictions
                   if p['equipment_id'] == equipment_id)

        predicted_date = datetime.now() + timedelta(days=pred['predicted_rul_days'])
        actual_date = actual_failure_date
        error_days = (actual_date - predicted_date).days
        error_percent = error_days / (actual_date - datetime.now()).days * 100

        self.actuals.append({
            'equipment_id': equipment_id,
            'predicted_date': predicted_date,
            'actual_date': actual_date,
            'error_days': error_days,
            'error_percent': error_percent
        })

    def generate_performance_report(self):
        """Monthly model performance report"""
        if not self.actuals:
            return "No failures recorded yet for evaluation"

        errors = [a['error_days'] for a in self.actuals]
        mae = np.mean(np.abs(errors))
        rmse = np.sqrt(np.mean(np.array(errors)**2))

        report = f"""
        MODEL PERFORMANCE REPORT - {self.model_id}
        ════════════════════════════════════════

        Evaluation period: {min(a['actual_date'] for a in self.actuals)}
                           to {max(a['actual_date'] for a in self.actuals)}

        Total failures analyzed: {len(self.actuals)}
        Mean Absolute Error (MAE): {mae:.1f} days
        Root Mean Square Error (RMSE): {rmse:.1f} days

        Over-predictions (conservative): {sum(1 for e in errors if e > 0)} ({sum(1 for e in errors if e > 0)/len(errors)*100:.0f}%)
        Under-predictions (risky): {sum(1 for e in errors if e < 0)} ({sum(1 for e in errors if e < 0)/len(errors)*100:.0f}%)

        Accuracy (within ±7 days): {sum(1 for e in errors if abs(e) <= 7)/len(errors)*100:.0f}%

        Recommendation: {'RETRAIN MODEL' if rmse > 15 else 'Model performing well, standard monitoring'}
        """

        return report
```

### 5.2 Data Drift Detection

**Monitoring Feature Distribution Changes:**

```python
from scipy.stats import ks_2samp

class DataDriftDetector:
    def __init__(self, baseline_features):
        self.baseline_features = baseline_features
        self.drift_log = []

    def detect_drift(self, current_features, threshold=0.05):
        """
        Compare current feature distribution to baseline using KS test
        """

        drifts_detected = {}

        for feature_name in self.baseline_features.keys():
            baseline_dist = self.baseline_features[feature_name]
            current_dist = current_features[feature_name]

            # Kolmogorov-Smirnov test
            ks_stat, p_value = ks_2samp(baseline_dist, current_dist)

            if p_value < threshold:
                drifts_detected[feature_name] = {
                    'ks_statistic': ks_stat,
                    'p_value': p_value,
                    'baseline_mean': np.mean(baseline_dist),
                    'current_mean': np.mean(current_dist),
                    'shift_percent': (np.mean(current_dist) - np.mean(baseline_dist)) / np.mean(baseline_dist) * 100
                }

        self.drift_log.append({
            'timestamp': datetime.now(),
            'drifts': drifts_detected
        })

        if drifts_detected:
            print(f"⚠️  DATA DRIFT DETECTED in {len(drifts_detected)} features:")
            for fname, drift_info in drifts_detected.items():
                print(f"  {fname}: {drift_info['shift_percent']:+.1f}% shift (p={drift_info['p_value']:.4f})")

            return True, drifts_detected
        else:
            return False, {}
```

### 5.3 Retraining Schedule and Triggers

**When to Retrain Models:**

```
SCHEDULE-BASED RETRAINING:
├─ Frequency: Quarterly (every 3 months minimum)
├─ Includes: All new failure data collected since last training
├─ Process: 1-week cycle (new model evaluation, testing, deployment)
└─ Timing: During low-production periods if possible

TRIGGER-BASED RETRAINING:
├─ Data drift detected (p < 0.05 in KS test)
├─ Model accuracy < 80% on recent predictions
├─ Equipment operating outside historical parameter range
├─ >20% new equipment added to fleet (different manufacturers)
└─ Major process changes (speed, load, environment)

PRIORITY-BASED RETRAINING:
├─ High priority: Critical equipment models (impact on uptime)
├─ Medium: Standard equipment (production efficiency)
├─ Low: Non-critical equipment (run-to-failure acceptable)
```

---

## 6. Troubleshooting and Optimization

### 6.1 Common Issues and Solutions

**Issue 1: High False Positive Rate**

```
Problem: Too many alerts for healthy equipment
Root causes:
├─ Thresholds too conservative (too sensitive)
├─ Feature noise too high (need better filtering)
├─ Normal variation in baseline (different load conditions)
└─ Equipment operating outside historical range

Solutions:
├─ Increase alert thresholds (raise to 85th percentile of healthy data)
├─ Add data preprocessing filter (moving average, wavelet denoising)
├─ Create separate models for different operating modes
├─ Collect more baseline data (expand reference)
└─ Manual threshold tuning based on maintenance feedback

Metric: False positive rate should be < 5% after tuning
```

**Issue 2: High False Negative Rate**

```
Problem: Equipment fails despite no warning
Root causes:
├─ Thresholds too conservative (not sensitive enough)
├─ Model underfitting (not capturing failure patterns)
├─ Sensor failure or data quality issues
├─ Failure modes not in training data
└─ Different failure progression than historical

Solutions:
├─ Decrease alert thresholds (lower to 70th percentile)
├─ Add more training data (more failure examples)
├─ Improve feature engineering (better failure indicators)
├─ Root cause analysis of missed failures
├─ Augment training data with similar equipment types
└─ Implement ensemble methods (multiple models voted together)

Target: False negative rate < 5% (fewer surprises)
```

**Issue 3: Slow Model Inference**

```
Problem: RUL prediction takes > 1 minute (too slow for real-time)
Causes:
├─ Complex deep learning model (LSTM, ensemble of 10+ tree models)
├─ Feature extraction computationally expensive
├─ Inefficient data loading or API calls
└─ Single-threaded implementation

Solutions:
├─ Model compression (distillation, pruning, quantization)
├─ Feature caching (pre-compute features incrementally)
├─ Batch processing (predict multiple equipment simultaneously)
├─ Parallel processing (multi-threaded feature extraction)
└─ Simplified model (Random Forest instead of LSTM for similar accuracy)

Target: < 1 second per prediction for real-time system
```

### 6.2 Model Optimization Techniques

**Feature Selection (Reduce dimensionality):**

```python
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif

# Identify most important features
selector = SelectKBest(f_classif, k=10)  # Keep top 10 features
X_selected = selector.fit_transform(X, y)

# Get selected feature names
selected_features = [X.columns[i] for i in selector.get_support(indices=True)]
print(f"Selected features: {selected_features}")

# Retrain model with fewer features → faster inference
model = RandomForestClassifier(n_estimators=50, max_depth=10)  # Simpler too
model.fit(X_selected, y)
```

**Hyperparameter Optimization:**

```python
from sklearn.model_selection import GridSearchCV

# Grid of hyperparameters to try
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15],
    'min_samples_split': [5, 10, 20],
    'min_samples_leaf': [2, 4, 8]
}

# Grid search with cross-validation
grid_search = GridSearchCV(
    RandomForestClassifier(),
    param_grid,
    cv=5,  # 5-fold cross-validation
    scoring='f1_weighted',
    n_jobs=-1  # Parallel processing
)

grid_search.fit(X, y)

best_params = grid_search.best_params_
print(f"Best parameters: {best_params}")
print(f"Best CV score: {grid_search.best_score_:.3f}")

# Retrain with best parameters
best_model = grid_search.best_estimator_
```

---

## 7. Success Metrics and ROI

### 7.1 Key Performance Indicators

**Tracking PDM Implementation Success:**

```
RELIABILITY METRICS:
├─ Mean Time Between Failures (MTBF): Target +50%
├─ Unplanned downtime: Target -70%
├─ Equipment availability: Target >95%
└─ Failure prediction accuracy: Target >85%

MAINTENANCE EFFICIENCY:
├─ Maintenance cost/year: Target -25%
├─ Preventive/corrective ratio: Target 80/20 (from 20/80)
├─ Maintenance labor utilization: Target >80% productive
└─ Work order lead time: Target +2 weeks (time to plan)

OPERATIONAL IMPACT:
├─ Production loss from equipment failure: Target -50%
├─ Quality defects from equipment: Target -20%
├─ Safety incidents: Target -40%
└─ Overall Equipment Effectiveness (OEE): Target +10 points

FINANCIAL:
├─ ROI on PDM investment: Target >30% annually
├─ Payback period: Target 18-24 months
├─ Emergency repair costs avoided: Track and monetize
└─ Production revenue protected: Calculate prevented downtime costs
```

### 7.2 ROI Calculation Example

```
PDM INVESTMENT COSTS (Year 1):
├─ Sensors & installation: $15,000
├─ Software/cloud platform: $20,000
├─ Infrastructure (database, network): $10,000
├─ ML development & deployment: $40,000
├─ Training & change management: $5,000
└─ Total Year 1: $90,000

OPERATIONAL COSTS (Annual):
├─ Monitoring & analysis (0.5 FTE): $30,000
├─ Cloud/database subscription: $5,000
├─ Sensor maintenance & calibration: $2,000
└─ Total Annual: $37,000

BENEFITS FROM PDM:
├─ Reduced maintenance costs: $25,000/year (20% savings on $125K budget)
├─ Avoided emergency repairs: $50,000/year (2 prevented catastrophic failures)
├─ Production saved (downtime): $80,000/year (40 hours × $2K/hour)
├─ Extended equipment life: $15,000/year (defer replacement capital)
└─ Total Year 1 Benefits: $170,000

ROI = (Benefits - Costs) / Investment × 100%
    = (170K - 90K - 37K) / 90K × 100%
    = 43K / 90K × 100%
    = 48% ROI in Year 1

Payback period = 90K / (170K - 37K) × 12 months = 7 months

Year 2+ Benefit = $170K/year - $37K/year = $133K/year net benefit
```

---

## References and Resources

- Mobley, R.K., "Predictive Maintenance"
- ISO 13373 series: Condition Monitoring Standards
- Python libraries: Scikit-learn, XGBoost, TensorFlow, NumPy
- Time-series databases: InfluxDB, TimescaleDB
- Cloud platforms: AWS SageMaker, Azure ML, Google Cloud AI
