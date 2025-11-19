# AI/ML Clinical Models Reference

## Overview
Machine learning and artificial intelligence models for clinical prediction, diagnosis, and decision support. Focus on production-grade, validated models with regulatory considerations.

## Model Categories

### 1. Early Warning Systems

#### Sepsis Prediction Models

**Traditional Scores**:
- **SIRS** (Sensitivity ~85%, Specificity ~50%)
- **qSOFA** (Sensitivity ~60%, Specificity ~70%)
- **MEWS** (Modified Early Warning Score)
- **NEWS** (National Early Warning Score)

**ML-Based Models**:

**TREWS (Targeted Real-time Early Warning System)**:
- **Algorithm**: XGBoost ensemble
- **Features**: 66 clinical variables (vitals, labs, demographics)
- **Performance**: AUROC 0.83, 3-hour advance warning
- **Deployment**: Real-time streaming from EHR
- **Reference**: Henry et al., Science Translational Medicine, 2015

**Epic Sepsis Model**:
- **Algorithm**: Proprietary ML
- **Features**: Vital signs, labs, demographics, medications
- **Performance**: Variable (AUROC 0.63-0.83 depending on validation study)
- **Concerns**: Black-box, external validation issues
- **Controversy**: Wong et al. (2021) critique

**InSight (Dascena)**:
- **Algorithm**: Machine learning ensemble
- **Features**: EMR data, vital signs, labs
- **Performance**: AUROC 0.85-0.92 (varies by setting)
- **FDA Status**: 510(k) cleared

**Implementation Pattern**:
```python
class SepsisMLModel:
    def __init__(self):
        self.model = load_xgboost_model('sepsis_v3.pkl')
        self.feature_extractor = SepsisFeatureExtractor()
        self.update_frequency = 3600  # Re-score hourly

    def predict(self, patient_id, timestamp):
        """Generate sepsis risk score"""
        # Extract features from EHR
        features = self.feature_extractor.extract(
            patient_id,
            lookback_hours=24,
            timestamp=timestamp
        )

        # Feature validation
        if not self.validate_features(features):
            return {'error': 'Insufficient data', 'score': None}

        # Prediction
        probability = self.model.predict_proba(features)[1]

        # Risk stratification
        risk_tier = self.stratify_risk(probability)

        return {
            'probability': probability,
            'risk_tier': risk_tier,  # LOW, MODERATE, HIGH, CRITICAL
            'features_used': features.to_dict(),
            'shap_values': self.explain(features),
            'model_version': 'v3.2',
            'timestamp': timestamp
        }

    def stratify_risk(self, prob):
        if prob < 0.05: return 'LOW'
        elif prob < 0.15: return 'MODERATE'
        elif prob < 0.30: return 'HIGH'
        else: return 'CRITICAL'
```

#### Deterioration Detection

**MEWS (Modified Early Warning Score)**:
```python
def calculate_mews(vitals):
    score = 0

    # Respiratory rate
    if vitals.rr < 9: score += 2
    elif vitals.rr <= 14: score += 0
    elif vitals.rr <= 20: score += 1
    elif vitals.rr <= 29: score += 2
    else: score += 3

    # Heart rate
    if vitals.hr < 40: score += 2
    elif vitals.hr <= 50: score += 1
    elif vitals.hr <= 100: score += 0
    elif vitals.hr <= 110: score += 1
    elif vitals.hr <= 129: score += 2
    else: score += 3

    # Systolic BP
    if vitals.sbp < 70: score += 3
    elif vitals.sbp <= 80: score += 2
    elif vitals.sbp <= 100: score += 1
    elif vitals.sbp <= 199: score += 0
    else: score += 2

    # Temperature
    if vitals.temp < 35: score += 2
    elif vitals.temp <= 38.4: score += 0
    else: score += 2

    # AVPU (Alert, Voice, Pain, Unresponsive)
    if vitals.avpu == 'Alert': score += 0
    elif vitals.avpu in ['Voice', 'Pain']: score += 2
    else: score += 3

    return {
        'score': score,
        'action': get_mews_action(score)
    }

def get_mews_action(score):
    if score >= 5:
        return 'URGENT: Alert physician immediately, consider ICU'
    elif score >= 3:
        return 'Increase monitoring frequency, notify physician'
    else:
        return 'Continue routine monitoring'
```

### 2. Readmission Prediction

#### LACE Index

**Components**:
- **L**ength of stay
- **A**cute admission (vs planned)
- **C**omorbidities (Charlson index)
- **E**D visits in past 6 months

```python
def calculate_lace(admission):
    score = 0

    # Length of stay
    if admission.los < 1: score += 0
    elif admission.los == 1: score += 1
    elif admission.los == 2: score += 2
    elif admission.los == 3: score += 3
    elif admission.los <= 6: score += 4
    elif admission.los <= 13: score += 5
    else: score += 7

    # Acute admission
    if admission.type == 'EMERGENT':
        score += 3

    # Comorbidities (Charlson)
    charlson = calculate_charlson(admission.patient)
    if charlson >= 4: score += 5
    elif charlson >= 1: score += charlson

    # ED visits (past 6 months)
    ed_visits = count_ed_visits(admission.patient, days=180)
    if ed_visits >= 4: score += 4
    elif ed_visits >= 1: score += ed_visits

    return {
        'score': score,
        'readmission_risk': get_lace_risk(score)
    }

def get_lace_risk(score):
    if score >= 10: return 'HIGH (12% 30-day readmission)'
    elif score >= 5: return 'MODERATE (6% 30-day readmission)'
    else: return 'LOW (3% 30-day readmission)'
```

#### ML Readmission Models

**Deep Learning Approach**:
```python
import torch
import torch.nn as nn

class ReadmissionLSTM(nn.Module):
    """LSTM model for readmission prediction using temporal EHR data"""

    def __init__(self, input_dim, hidden_dim, num_layers):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x: (batch, seq_len, features)
        _, (hidden, _) = self.lstm(x)
        out = self.fc(hidden[-1])
        return self.sigmoid(out)

class ReadmissionPredictor:
    def __init__(self):
        self.model = torch.load('readmission_lstm.pt')
        self.feature_names = [
            'age', 'num_diagnoses', 'num_medications',
            'prior_admissions', 'charlson_score',
            # Vitals time series
            'hr_mean', 'hr_std', 'sbp_mean', 'sbp_std',
            # Labs
            'hemoglobin', 'sodium', 'creatinine', 'glucose'
        ]

    def predict(self, patient_id):
        # Extract temporal features
        features = self.extract_temporal_features(patient_id)

        # Model inference
        with torch.no_grad():
            prob = self.model(features).item()

        return {
            'readmission_probability': prob,
            'risk_category': self.categorize_risk(prob),
            'interventions': self.recommend_interventions(prob, patient_id)
        }

    def recommend_interventions(self, prob, patient_id):
        if prob > 0.3:
            return [
                'Discharge planning conference',
                'Post-discharge phone call at 48 hours',
                'Home health referral',
                'Medication reconciliation',
                'Primary care appointment within 7 days'
            ]
        elif prob > 0.15:
            return [
                'Medication reconciliation',
                'Primary care appointment within 14 days'
            ]
        else:
            return ['Standard discharge instructions']
```

### 3. Diagnostic Support

#### Skin Lesion Classification (Dermatology)

**Architecture**: CNN (ResNet, Inception, EfficientNet)
**Task**: Classify skin lesions (melanoma, basal cell, etc.)
**Performance**: Matches dermatologist accuracy (AUROC ~0.95)

```python
import tensorflow as tf

class SkinLesionClassifier:
    def __init__(self):
        self.model = tf.keras.models.load_model('efficientnet_skin.h5')
        self.classes = ['Melanoma', 'Basal Cell Carcinoma',
                       'Squamous Cell Carcinoma', 'Actinic Keratosis',
                       'Benign Keratosis', 'Nevus', 'Dermatofibroma']

    def predict(self, image_path):
        # Preprocess
        img = tf.keras.preprocessing.image.load_img(
            image_path, target_size=(224, 224)
        )
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)
        img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)

        # Predict
        predictions = self.model.predict(img_array)[0]

        # Format results
        results = [
            {'diagnosis': cls, 'probability': float(prob)}
            for cls, prob in zip(self.classes, predictions)
        ]
        results.sort(key=lambda x: x['probability'], reverse=True)

        # Clinical decision support
        top_diagnosis = results[0]
        if top_diagnosis['diagnosis'] == 'Melanoma' and top_diagnosis['probability'] > 0.7:
            recommendation = 'URGENT: Dermatology referral for biopsy'
        elif top_diagnosis['probability'] > 0.8:
            recommendation = f'Likely {top_diagnosis["diagnosis"]} - Consider biopsy'
        else:
            recommendation = 'Uncertain diagnosis - Dermatology referral recommended'

        return {
            'predictions': results,
            'recommendation': recommendation,
            'confidence': top_diagnosis['probability']
        }
```

#### Diabetic Retinopathy Detection

**Task**: Screen fundus photos for diabetic retinopathy
**FDA Clearance**: IDx-DR (first autonomous AI diagnostic)

```python
class DiabeticRetinopathyDetector:
    def __init__(self):
        self.model = load_model('dr_detection.h5')
        self.severity_classes = [
            'No DR',
            'Mild',
            'Moderate',
            'Severe',
            'Proliferative DR'
        ]

    def predict(self, fundus_image_paths):
        """Takes left and right eye fundus photos"""
        results = {}

        for eye, path in fundus_image_paths.items():
            img = self.preprocess(path)
            pred = self.model.predict(img)

            severity = self.severity_classes[np.argmax(pred)]
            confidence = float(np.max(pred))

            results[eye] = {
                'severity': severity,
                'confidence': confidence,
                'referral_needed': severity in ['Severe', 'Proliferative DR']
            }

        # Clinical recommendation
        max_severity = max(results.values(), key=lambda x: self.severity_classes.index(x['severity']))
        if max_severity['referral_needed']:
            recommendation = 'URGENT: Ophthalmology referral within 1 week'
        elif max_severity['severity'] == 'Moderate':
            recommendation = 'Ophthalmology referral within 1-3 months'
        else:
            recommendation = 'Rescreen in 12 months'

        return {
            'results': results,
            'recommendation': recommendation
        }
```

### 4. AKI (Acute Kidney Injury) Prediction

**DeepAKI Model**:
```python
class AKIPredictionModel:
    def __init__(self):
        self.model = load_model('deep_aki.pkl')
        self.kdigo_thresholds = {
            'stage_1': 0.3,  # Cr increase ≥ 0.3 mg/dL
            'stage_2': 2.0,  # 2x baseline Cr
            'stage_3': 3.0   # 3x baseline Cr
        }

    def predict(self, patient_id):
        # Extract features
        features = {
            'baseline_cr': get_baseline_creatinine(patient_id),
            'current_cr': get_latest_creatinine(patient_id),
            'cr_trend': calculate_cr_trend(patient_id, hours=48),
            'urine_output': get_urine_output(patient_id, hours=24),
            'nephrotoxic_drugs': count_nephrotoxic_meds(patient_id),
            'hypotension_episodes': count_hypotension(patient_id, hours=24),
            'sepsis': has_sepsis(patient_id),
            'contrast_exposure': recent_contrast(patient_id, hours=72),
            'age': get_age(patient_id),
            'comorbidities': get_aki_risk_factors(patient_id)
        }

        # Predict AKI risk in next 48 hours
        risk_48h = self.model.predict_proba([features])[1]

        # Check current KDIGO stage
        kdigo_stage = self.assess_kdigo(features)

        # Generate recommendations
        recommendations = self.generate_recommendations(features, risk_48h, kdigo_stage)

        return {
            'aki_risk_48h': risk_48h,
            'current_kdigo_stage': kdigo_stage,
            'recommendations': recommendations
        }

    def generate_recommendations(self, features, risk, kdigo_stage):
        recs = []

        if kdigo_stage or risk > 0.3:
            recs.append('Avoid nephrotoxic agents (NSAIDs, aminoglycosides, contrast)')
            recs.append('Ensure adequate hydration')
            recs.append('Monitor creatinine daily')

        if features['nephrotoxic_drugs'] > 0:
            recs.append('Review and discontinue nephrotoxic medications if possible')

        if risk > 0.5:
            recs.append('Consider nephrology consultation')
            recs.append('Adjust medication doses for renal function')

        return recs
```

## Model Deployment Architecture

### Real-Time Inference Pipeline

```python
class ClinicalMLPipeline:
    def __init__(self):
        self.models = {
            'sepsis': SepsisMLModel(),
            'aki': AKIPredictionModel(),
            'readmission': ReadmissionPredictor()
        }
        self.fhir_client = FHIRClient()
        self.alert_service = AlertService()

    async def run_periodic_screening(self):
        """Run ML models on all active patients hourly"""
        patients = get_active_patients()

        for patient in patients:
            # Run models in parallel
            results = await asyncio.gather(
                self.models['sepsis'].predict(patient.id),
                self.models['aki'].predict(patient.id)
            )

            # Generate alerts if needed
            for result in results:
                if result['risk_tier'] in ['HIGH', 'CRITICAL']:
                    self.alert_service.send(
                        patient_id=patient.id,
                        alert_type=result['model_type'],
                        severity=result['risk_tier'],
                        details=result
                    )

    def real_time_event_handler(self, event):
        """Trigger model on specific clinical events"""
        if event.type == 'LAB_RESULT':
            # New creatinine → run AKI model
            if event.lab_code == '2160-0':  # LOINC for creatinine
                result = self.models['aki'].predict(event.patient_id)
                if result['kdigo_stage']:
                    self.alert_service.send_critical(event.patient_id, result)

        elif event.type == 'VITAL_SIGN':
            # Abnormal vitals → run sepsis model
            if self.is_abnormal_vitals(event):
                result = self.models['sepsis'].predict(event.patient_id)
                if result['risk_tier'] in ['HIGH', 'CRITICAL']:
                    self.alert_service.send(event.patient_id, result)
```

## Model Explainability

### SHAP (SHapley Additive exPlanations)

```python
import shap

class ExplainableModel:
    def __init__(self, model):
        self.model = model
        self.explainer = shap.TreeExplainer(model)

    def predict_with_explanation(self, features):
        # Prediction
        prob = self.model.predict_proba([features])[1]

        # SHAP values
        shap_values = self.explainer.shap_values(features)

        # Format for clinical display
        feature_contributions = [
            {
                'feature': name,
                'value': val,
                'contribution': shap_val,
                'direction': 'increases' if shap_val > 0 else 'decreases'
            }
            for name, val, shap_val in zip(
                self.feature_names, features, shap_values[1]
            )
        ]

        # Sort by absolute contribution
        feature_contributions.sort(
            key=lambda x: abs(x['contribution']),
            reverse=True
        )

        return {
            'probability': prob,
            'top_contributors': feature_contributions[:5],
            'explanation_text': self.generate_text(feature_contributions[:3])
        }

    def generate_text(self, top_features):
        """Generate human-readable explanation"""
        text = "Risk is elevated due to: "
        reasons = [
            f"{f['feature']} ({f['value']})"
            for f in top_features if f['contribution'] > 0
        ]
        return text + ", ".join(reasons)
```

## Regulatory Considerations

### FDA Software as Medical Device (SaMD)

**Risk Categories**:
- **Class I**: Low risk (e.g., patient education)
- **Class II**: Moderate risk (e.g., sepsis prediction) - Requires 510(k)
- **Class III**: High risk (e.g., autonomous diagnosis) - Requires PMA

**CDS Software Exemptions** (21st Century Cures Act):
- Clinical decision support tools
- Not autonomous (requires clinician review)
- Evidence-based
- Transparent basis for recommendations

### Performance Monitoring

```python
class ModelMonitoring:
    def __init__(self):
        self.performance_log = PerformanceDatabase()

    def log_prediction(self, prediction_id, inputs, output):
        """Log all predictions for monitoring"""
        self.performance_log.insert({
            'prediction_id': prediction_id,
            'timestamp': datetime.now(),
            'model_version': output['model_version'],
            'inputs': inputs,
            'prediction': output['probability'],
            'features_used': output['features_used']
        })

    def log_outcome(self, prediction_id, actual_outcome):
        """Log actual clinical outcome"""
        self.performance_log.update(prediction_id, {
            'actual_outcome': actual_outcome,
            'outcome_timestamp': datetime.now()
        })

    def calculate_metrics(self, start_date, end_date):
        """Calculate model performance metrics"""
        data = self.performance_log.query(start_date, end_date)

        predictions = [d['prediction'] for d in data]
        actuals = [d['actual_outcome'] for d in data]

        return {
            'auroc': roc_auc_score(actuals, predictions),
            'sensitivity': sensitivity_at_threshold(actuals, predictions, 0.5),
            'specificity': specificity_at_threshold(actuals, predictions, 0.5),
            'ppv': ppv(actuals, predictions, 0.5),
            'npv': npv(actuals, predictions, 0.5),
            'calibration': calibration_plot(actuals, predictions)
        }

    def detect_model_drift(self):
        """Monitor for degradation in model performance"""
        recent = self.calculate_metrics(days_ago=30, days_ago=0)
        baseline = self.calculate_metrics(days_ago=180, days_ago=30)

        if recent['auroc'] < baseline['auroc'] - 0.05:
            alert_ops_team('Model performance degradation detected')
            return True

        return False
```

## Resources
- FDA guidance on Clinical Decision Support Software
- HL7 FHIR Clinical Reasoning Module
- TRIPOD Statement (Transparent Reporting of prediction models)
- CONSORT-AI Extension (Clinical trial reporting)
- Henry et al. TREWS paper (Science Translational Medicine)
