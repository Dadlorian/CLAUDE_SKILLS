"""
Machine Learning Fraud Model - XGBoost-based fraud classifier
"""

import xgboost as xgb
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple


class MLFraudModel:
    """XGBoost-based fraud detection model"""

    def __init__(self, model_path: str = None):
        self.model = None
        self.feature_names = []
        self.scaler = StandardScaler()

        if model_path:
            self.load_model(model_path)

    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              feature_names: List[str]):
        """Train XGBoost model"""
        self.feature_names = feature_names

        # Create model
        self.model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=7,
            learning_rate=0.1,
            subsample=0.8,
            scale_pos_weight=10,  # Handle class imbalance
            random_state=42,
            n_jobs=-1
        )

        # Train
        self.model.fit(X_train, y_train)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get fraud probability"""
        if self.model is None:
            raise ValueError("Model not trained or loaded")

        return self.model.predict_proba(X)

    def score_transaction(self, features: Dict) -> float:
        """Score single transaction"""
        # Convert to array
        feature_array = np.array([[features.get(f, 0)
                                   for f in self.feature_names]])

        # Predict
        proba = self.predict_proba(feature_array)

        return proba[0][1]

    def get_feature_importance(self) -> Dict:
        """Get feature importance scores"""
        importances = self.model.feature_importances_

        return {
            name: float(importance)
            for name, importance in zip(self.feature_names, importances)
        }

    def save_model(self, path: str):
        """Save model to disk"""
        self.model.save_model(path)

    def load_model(self, path: str):
        """Load model from disk"""
        self.model = xgb.XGBClassifier()
        self.model.load_model(path)
