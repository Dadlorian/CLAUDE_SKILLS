"""
Model Training - Train fraud detection models
"""

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from typing import Tuple
import numpy as np


class ModelTrainer:
    """Train fraud detection models"""

    @staticmethod
    def prepare_data(X: np.ndarray, y: np.ndarray) -> Tuple:
        """Prepare data for training"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            stratify=y,
            random_state=42
        )

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        return X_train_scaled, X_test_scaled, y_train, y_test, scaler

    @staticmethod
    def train_model(X_train: np.ndarray, y_train: np.ndarray) -> xgb.XGBClassifier:
        """Train XGBoost model"""
        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=7,
            learning_rate=0.1,
            subsample=0.8,
            scale_pos_weight=10,
            random_state=42
        )

        model.fit(X_train, y_train)

        return model

    @staticmethod
    def evaluate_model(model, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Evaluate model performance"""
        from sklearn.metrics import roc_auc_score, f1_score, precision_recall_curve

        y_pred_proba = model.predict_proba(X_test)[:, 1]
        y_pred = (y_pred_proba > 0.5).astype(int)

        return {
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'f1': f1_score(y_test, y_pred),
            'precision': precision_recall_curve(y_test, y_pred_proba)
        }
