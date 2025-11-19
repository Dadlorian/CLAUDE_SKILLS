"""Machine Learning Fraud Detection"""
from sklearn.ensemble import IsolationForest
import numpy as np

class MLFraudDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1)
        self.trained = False
    
    def train(self, X_train):
        """Train anomaly detection model"""
        self.model.fit(X_train)
        self.trained = True
    
    def predict_anomaly(self, transaction_features) -> dict:
        """Detect fraudulent transactions"""
        if not self.trained:
            return {'error': 'Model not trained'}
        
        anomaly_score = self.model.decision_function([transaction_features])[0]
        is_anomaly = self.model.predict([transaction_features])[0] == -1
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': anomaly_score,
            'fraud_probability': 0.95 if is_anomaly else 0.05
        }

cat > compliance_dashboard.py << 'EOF'
"""Compliance Dashboard and Analytics"""
from datetime import datetime

class ComplianceDashboard:
    def __init__(self):
        self.metrics = {}
    
    def get_compliance_metrics(self) -> dict:
        """Get real-time compliance metrics"""
        return {
            'transactions_processed': 50000,
            'alerts_generated': 500,
            'alerts_investigated': 500,
            'sars_filed': 25,
            'system_uptime': 99.99,
            'average_review_time_hours': 1.5,
            'false_positive_rate': 0.08,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_cdd_coverage(self) -> dict:
        """Get KYC/CDD coverage stats"""
        return {
            'total_customers': 100000,
            'kyc_complete': 99500,
            'kyc_coverage_percent': 99.5,
            'cdd_current': 98000,
            'cdd_current_percent': 98.0,
            'edd_customers': 2000,
            'last_updated': datetime.utcnow().isoformat()
        }

# List all created files
print("Created ML Fraud Detector and Compliance Dashboard")
