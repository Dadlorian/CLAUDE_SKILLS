"""Sepsis Early Warning System using Machine Learning"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime, timedelta

class SepsisEarlyWarning:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=200, max_depth=10, class_weight='balanced')
        self.feature_window_hours = 6

    def extract_time_series_features(self, vitals_df):
        """Extract statistical features from time-series vitals"""
        features = {}
        for vital in ['heart_rate', 'respiratory_rate', 'temperature', 'map', 'spo2']:
            if vital in vitals_df.columns:
                features[f'{vital}_current'] = vitals_df[vital].iloc[-1]
                features[f'{vital}_mean_6h'] = vitals_df[vital].tail(6).mean()
                features[f'{vital}_max_6h'] = vitals_df[vital].tail(6).max()
                features[f'{vital}_trend'] = self.calculate_trend(vitals_df[vital].tail(6))
        return features

    def calculate_trend(self, series):
        """Calculate trend (slope) of vital sign"""
        if len(series) < 2:
            return 0
        x = np.arange(len(series))
        return np.polyfit(x, series, 1)[0]

    def calculate_sofa_score(self, patient_data):
        """Calculate Sequential Organ Failure Assessment score"""
        score = 0
        # Respiration: PaO2/FiO2
        if patient_data.get('pao2_fio2', 400) < 100: score += 4
        elif patient_data.get('pao2_fio2', 400) < 200: score += 3
        # Coagulation: Platelets
        if patient_data.get('platelets', 150) < 20: score += 4
        elif patient_data.get('platelets', 150) < 50: score += 3
        # Add more SOFA components...
        return score

    def predict_sepsis_risk(self, patient_id, current_data):
        """Predict sepsis risk for a patient"""
        features = {
            **self.extract_time_series_features(current_data['vitals']),
            'sofa_score': self.calculate_sofa_score(current_data['labs']),
            'lactate': current_data['labs'].get('lactate', 1.0),
            'wbc_count': current_data['labs'].get('wbc', 10),
            'age': current_data['demographics']['age'],
            'on_vasopressors': int(current_data.get('on_vasopressors', False))
        }
        risk = self.model.predict_proba([list(features.values())])[0][1]
        return {'patient_id': patient_id, 'sepsis_risk': risk,
                'alert_level': 'CRITICAL' if risk > 0.70 else 'WARNING' if risk > 0.40 else 'NORMAL'}
