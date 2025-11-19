"""
Anomaly Detector - Detect unusual transactions
"""

import numpy as np
from typing import Dict
from sklearn.ensemble import IsolationForest


class AnomalyDetector:
    """Isolation Forest-based anomaly detection"""

    def __init__(self):
        self.model = None
        self.feature_names = []

    def train(self, X_train: np.ndarray, feature_names: list):
        """Train anomaly detector"""
        self.feature_names = feature_names

        self.model = IsolationForest(
            contamination=0.05,
            random_state=42,
            n_jobs=-1
        )

        self.model.fit(X_train)

    def score_transaction(self, features: Dict) -> float:
        """Score transaction for anomaly"""
        if self.model is None:
            return 0.5

        # Convert to array
        feature_array = np.array([[features.get(f, 0)
                                   for f in self.feature_names]])

        # Get anomaly score (-1 to 1)
        anomaly_score = self.model.decision_function(feature_array)[0]

        # Normalize to 0-1
        normalized = (anomaly_score + 1) / 2

        return min(max(normalized, 0.0), 1.0)
