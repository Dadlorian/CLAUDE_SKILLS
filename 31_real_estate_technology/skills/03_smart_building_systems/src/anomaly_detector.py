"""Anomaly Detection for Predictive Maintenance"""
import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np

class EquipmentAnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        
    def train(self, historical_data):
        """Train on normal operating data"""
        features = self.extract_features(historical_data)
        self.model.fit(features)
        
    def extract_features(self, df):
        """Extract relevant features"""
        features = df[['supply_temp', 'return_temp', 'power_consumption']].copy()
        features['temp_diff'] = features['supply_temp'] - features['return_temp']
        features['efficiency'] = features['power_consumption'] / (features['temp_diff'] + 1)
        return features[['supply_temp', 'return_temp', 'temp_diff', 'efficiency']]
        
    def detect_anomalies(self, current_data):
        """Detect if current operation is anomalous"""
        features = self.extract_features(current_data)
        predictions = self.model.predict(features)
        anomaly_scores = self.model.score_samples(features)
        
        anomalies = current_data[predictions == -1].copy()
        anomalies['anomaly_score'] = anomaly_scores[predictions == -1]
        
        return anomalies
        
    def predict_failure(self, equipment_id, data):
        """Predict if equipment likely to fail"""
        anomalies = self.detect_anomalies(data)
        
        if len(anomalies) > 5:
            return {
                'failure_likely': True,
                'confidence': 0.8,
                'recommended_action': 'Schedule maintenance inspection'
            }
        return {'failure_likely': False}

# Example usage
detector = EquipmentAnomalyDetector()

# Training data (normal operation)
historical = pd.DataFrame({
    'supply_temp': np.random.normal(55, 2, 1000),
    'return_temp': np.random.normal(72, 2, 1000),
    'power_consumption': np.random.normal(10, 1, 1000)
})
detector.train(historical)

# Test data (with anomaly)
test = pd.DataFrame({
    'supply_temp': [55, 55, 60],  # Anomalous high supply temp
    'return_temp': [72, 72, 72],
    'power_consumption': [10, 10, 15]  # High power
})

anomalies = detector.detect_anomalies(test)
print(f"Found {len(anomalies)} anomalies")
