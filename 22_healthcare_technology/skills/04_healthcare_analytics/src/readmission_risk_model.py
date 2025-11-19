"""
30-Day Hospital Readmission Risk Prediction Model
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, classification_report
import joblib

class ReadmissionRiskModel:
    def __init__(self):
        self.model = None
        self.features = []

    def prepare_features(self, encounters_df):
        """Extract features for readmission prediction"""

        features = pd.DataFrame()

        # Demographics
        features['age'] = encounters_df['age']
        features['gender_male'] = (encounters_df['gender'] == 'M').astype(int)

        # Clinical complexity
        features['charlson_score'] = encounters_df['charlson_comorbidity_index']
        features['chronic_condition_count'] = encounters_df['chronic_conditions'].apply(len)
        features['medication_count'] = encounters_df['active_medications'].apply(len)

        # Index admission characteristics
        features['length_of_stay'] = encounters_df['length_of_stay']
        features['icu_admission'] = encounters_df['icu_admission'].astype(int)
        features['emergency_admission'] = (encounters_df['admission_type'] == 'Emergency').astype(int)

        # Specific conditions (binary flags)
        features['has_chf'] = encounters_df['diagnoses'].apply(lambda x: 'CHF' in x).astype(int)
        features['has_copd'] = encounters_df['diagnoses'].apply(lambda x: 'COPD' in x).astype(int)
        features['has_diabetes'] = encounters_df['diagnoses'].apply(lambda x: 'Diabetes' in x).astype(int)

        # Utilization history
        features['prior_admits_6mo'] = encounters_df['prior_admits_6mo']
        features['ed_visits_6mo'] = encounters_df['ed_visits_6mo']

        # Labs at discharge
        features['hemoglobin_discharge'] = encounters_df['discharge_hemoglobin']
        features['creatinine_discharge'] = encounters_df['discharge_creatinine']
        features['sodium_discharge'] = encounters_df['discharge_sodium']

        # Social determinants
        features['lives_alone'] = encounters_df['lives_alone'].astype(int)
        features['transportation_barriers'] = encounters_df['transportation_barriers'].astype(int)

        # Handle missing values
        features = features.fillna(features.median())

        self.features = features.columns.tolist()

        return features

    def train(self, X_train, y_train):
        """Train readmission risk model"""

        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )

        self.model.fit(X_train, y_train)

    def evaluate(self, X_test, y_test):
        """Evaluate model performance"""

        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        y_pred = self.model.predict(X_test)

        auc = roc_auc_score(y_test, y_pred_proba)
        print(f"AUC-ROC: {auc:.3f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))

        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.features,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        print("\nTop 10 Features:")
        print(feature_importance.head(10))

        return auc

    def predict_risk(self, patient_features):
        """Predict readmission risk for a patient"""

        risk_prob = self.model.predict_proba(patient_features)[0][1]

        risk_tier = 'High' if risk_prob > 0.40 else 'Medium' if risk_prob > 0.20 else 'Low'

        return {
            'risk_probability': risk_prob,
            'risk_tier': risk_tier,
            'recommended_interventions': self.get_interventions(risk_tier)
        }

    def get_interventions(self, risk_tier):
        """Get recommended interventions based on risk"""

        interventions = {
            'High': [
                'Enroll in care transitions program',
                'Home health nurse visit within 48 hours',
                'Medication reconciliation',
                'PCP follow-up within 7 days',
                'Daily monitoring calls'
            ],
            'Medium': [
                'Phone call within 48 hours',
                'PCP follow-up within 14 days',
                'Medication education'
            ],
            'Low': [
                'Standard discharge instructions',
                'PCP follow-up as scheduled'
            ]
        }

        return interventions.get(risk_tier, [])

    def save_model(self, filepath):
        """Save trained model"""
        joblib.dump({
            'model': self.model,
            'features': self.features
        }, filepath)

    def load_model(self, filepath):
        """Load trained model"""
        saved = joblib.load(filepath)
        self.model = saved['model']
        self.features = saved['features']

if __name__ == "__main__":
    # Load data
    discharges = pd.read_csv('hospital_discharges.csv')

    # Initialize model
    readmission_model = ReadmissionRiskModel()

    # Prepare features
    X = readmission_model.prepare_features(discharges)
    y = discharges['readmitted_30d']

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train
    readmission_model.train(X_train, y_train)

    # Evaluate
    readmission_model.evaluate(X_test, y_test)

    # Save model
    readmission_model.save_model('readmission_model.pkl')

    print("\nModel training complete!")
