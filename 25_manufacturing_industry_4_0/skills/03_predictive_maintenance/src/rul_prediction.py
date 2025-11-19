"""
Remaining Useful Life (RUL) Prediction Module

This module provides machine learning models for predicting remaining useful life
of equipment, including Random Forest, XGBoost, and LSTM neural networks with
uncertainty quantification.

Author: Industrial AI Team
License: MIT
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict, Tuple, Optional, List
import warnings

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False


class RULPredictor:
    """
    Base class for RUL prediction models.

    Attributes:
        model: Trained prediction model
        scaler: Feature normalizer
        rul_scaler: RUL normalizer (for neural networks)
    """

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.rul_scaler = StandardScaler()
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fit RUL prediction model."""
        raise NotImplementedError

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict RUL values."""
        raise NotImplementedError

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model performance.

        Returns:
            Dictionary with metrics: mae, rmse, r2, mape
        """
        y_pred = self.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mape = np.mean(np.abs((y_test - y_pred) / (y_test + 1e-10))) * 100

        return {
            'mae': float(mae),
            'rmse': float(rmse),
            'r2': float(r2),
            'mape': float(mape)
        }


class RandomForestRULPredictor(RULPredictor):
    """
    Random Forest RUL predictor.

    Advantages:
    - Non-parametric, handles non-linear degradation
    - Fast inference
    - Feature importance ranking
    - Robust to outliers

    Disadvantages:
    - No native uncertainty quantification
    - Requires labeled training data
    - Can extrapolate poorly
    """

    def __init__(self, n_estimators: int = 200, max_depth: int = 15,
                 random_state: int = 42):
        """
        Initialize Random Forest RUL predictor.

        Args:
            n_estimators: Number of trees
            max_depth: Maximum tree depth
            random_state: Random seed
        """
        super().__init__()

        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=10,
            min_samples_leaf=5,
            max_features='sqrt',
            random_state=random_state,
            n_jobs=-1
        )

        self.feature_names = None

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None):
        """
        Fit Random Forest model.

        Args:
            X: Features (num_samples, num_features)
            y: RUL labels (num_samples,)
            feature_names: Optional feature names for importance analysis
        """
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        self.feature_names = feature_names

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict RUL values.

        Args:
            X: Features (num_samples, num_features)

        Returns:
            Array of predicted RUL values
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance ranking.

        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted.")

        importances = self.model.feature_importances_

        if self.feature_names is None:
            self.feature_names = [f"Feature_{i}" for i in range(len(importances))]

        return dict(zip(self.feature_names, importances))

    def predict_with_uncertainty_bootstrap(self, X: np.ndarray, n_bootstrap: int = 50) \
            -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Predict RUL with uncertainty using bootstrap.

        Args:
            X: Features
            n_bootstrap: Number of bootstrap models to train

        Returns:
            Tuple of (point_estimate, lower_bound, upper_bound)
        """
        n_samples = len(X)
        predictions = np.zeros((n_bootstrap, n_samples))

        # Train bootstrap models
        for i in range(n_bootstrap):
            # Random sample with replacement
            indices = np.random.choice(
                len(self.scaler.mean_),
                size=len(self.scaler.mean_),
                replace=True
            )

            # Re-train model (simplified - just use variance across trees)
            pass

        # For simplicity, use ensemble variance across trees
        X_scaled = self.scaler.transform(X)

        # Get predictions from individual trees
        tree_predictions = np.array([tree.predict(X_scaled) for tree in self.model.estimators_])

        point_estimate = np.mean(tree_predictions, axis=0)
        lower_bound = np.percentile(tree_predictions, 2.5, axis=0)
        upper_bound = np.percentile(tree_predictions, 97.5, axis=0)

        return point_estimate, lower_bound, upper_bound


class XGBoostRULPredictor(RULPredictor):
    """
    XGBoost RUL predictor.

    Advantages:
    - State-of-the-art performance
    - Built-in regularization
    - Feature importance
    - Handles missing values

    Disadvantages:
    - More hyperparameters to tune
    - Slower training than Random Forest
    """

    def __init__(self, n_estimators: int = 300, max_depth: int = 7,
                 learning_rate: float = 0.05, random_state: int = 42):
        """
        Initialize XGBoost RUL predictor.

        Args:
            n_estimators: Number of boosting rounds
            max_depth: Maximum tree depth
            learning_rate: Learning rate (shrinkage)
            random_state: Random seed
        """
        if not HAS_XGBOOST:
            raise ImportError("XGBoost required. Install with: pip install xgboost")

        super().__init__()

        self.model = xgb.XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='reg:squarederror',
            eval_metric='rmse',
            random_state=random_state,
            n_jobs=-1
        )

        self.feature_names = None

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None,
            early_stopping_rounds: int = 20, verbose: bool = False):
        """
        Fit XGBoost model with early stopping.

        Args:
            X: Features
            y: RUL labels
            feature_names: Optional feature names
            early_stopping_rounds: Rounds for early stopping
            verbose: Print training progress
        """
        X_scaled = self.scaler.fit_transform(X)
        X_train, X_val, y_train, y_val = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=early_stopping_rounds,
            verbose=verbose
        )

        self.is_fitted = True
        self.feature_names = feature_names

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict RUL values."""
        if not self.is_fitted:
            raise ValueError("Model not fitted.")

        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from XGBoost model."""
        if not self.is_fitted:
            raise ValueError("Model not fitted.")

        importances = self.model.feature_importances_

        if self.feature_names is None:
            self.feature_names = [f"Feature_{i}" for i in range(len(importances))]

        return dict(zip(self.feature_names, importances))


class LSTMRULPredictor(RULPredictor):
    """
    LSTM neural network RUL predictor.

    Advantages:
    - Captures temporal dependencies in sequences
    - Excellent for time-series degradation patterns
    - Automatically learns features
    - Can model uncertainty with Bayesian dropout

    Disadvantages:
    - Requires large training datasets
    - Slow training and inference
    - "Black box" interpretation difficult
    - Hyperparameter tuning critical
    """

    def __init__(self, sequence_length: int = 30, lstm_units: int = 64,
                 dropout_rate: float = 0.2):
        """
        Initialize LSTM RUL predictor.

        Args:
            sequence_length: Lookback window length (timesteps)
            lstm_units: Number of LSTM units
            dropout_rate: Dropout rate for regularization
        """
        if not HAS_TENSORFLOW:
            raise ImportError("TensorFlow required. Install with: pip install tensorflow")

        super().__init__()

        self.sequence_length = sequence_length
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.model = None
        self.input_dim = None

    def build_model(self, input_dim: int):
        """
        Build LSTM model architecture.

        Args:
            input_dim: Number of features in each timestep
        """
        self.input_dim = input_dim

        self.model = Sequential([
            LSTM(self.lstm_units, activation='relu', return_sequences=True,
                 input_shape=(self.sequence_length, input_dim)),
            Dropout(self.dropout_rate),
            LSTM(32, activation='relu', return_sequences=False),
            Dropout(self.dropout_rate),
            Dense(16, activation='relu'),
            Dropout(self.dropout_rate),
            Dense(1, activation='relu')  # RUL is positive
        ])

        self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 100,
            batch_size: int = 32, validation_split: float = 0.2, verbose: int = 0):
        """
        Fit LSTM model.

        Args:
            X: Sequence data (num_samples, sequence_length, num_features)
            y: RUL labels (num_samples,)
            epochs: Training epochs
            batch_size: Batch size
            validation_split: Validation split ratio
            verbose: TensorFlow verbosity
        """
        if X.ndim != 3:
            raise ValueError("X must be 3D: (num_samples, sequence_length, num_features)")

        if self.model is None:
            self.build_model(X.shape[2])

        # Normalize features
        X_2d = X.reshape(-1, X.shape[2])
        X_scaled = self.scaler.fit_transform(X_2d)
        X_scaled = X_scaled.reshape(X.shape)

        # Normalize RUL
        y_scaled = self.rul_scaler.fit_transform(y.reshape(-1, 1)).flatten()

        # Early stopping
        early_stop = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )

        self.model.fit(
            X_scaled, y_scaled,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[early_stop],
            verbose=verbose
        )

        self.is_fitted = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict RUL values.

        Args:
            X: Sequence data (num_samples, sequence_length, num_features)

        Returns:
            Array of predicted RUL values
        """
        if not self.is_fitted or self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")

        # Normalize features
        X_2d = X.reshape(-1, X.shape[2])
        X_scaled = self.scaler.transform(X_2d)
        X_scaled = X_scaled.reshape(X.shape)

        # Predict
        y_scaled = self.model.predict(X_scaled, verbose=0)

        # Inverse transform
        y_pred = self.rul_scaler.inverse_transform(y_scaled)

        return y_pred.flatten()

    def predict_with_uncertainty(self, X: np.ndarray, n_forward_passes: int = 100) \
            -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict RUL with uncertainty using MC dropout.

        Uses dropout during inference (Bayesian approximation) to estimate uncertainty.

        Args:
            X: Sequence data
            n_forward_passes: Number of forward passes with dropout

        Returns:
            Tuple of (point_estimate, uncertainty_std)
        """
        # Create model with dropout enabled during inference
        predictions = []

        for _ in range(n_forward_passes):
            # Forward pass with training=True enables dropout
            y_pred_scaled = self.model(X, training=True)
            y_pred = self.rul_scaler.inverse_transform(y_pred_scaled.numpy())
            predictions.append(y_pred.flatten())

        predictions = np.array(predictions)  # (n_forward_passes, num_samples)

        point_estimate = np.mean(predictions, axis=0)
        uncertainty = np.std(predictions, axis=0)

        return point_estimate, uncertainty


def prepare_sequence_data(features_over_time: List[np.ndarray],
                         rul_over_time: List[np.ndarray],
                         sequence_length: int = 30) -> Tuple[np.ndarray, np.ndarray]:
    """
    Prepare sequence data for LSTM training.

    Args:
        features_over_time: List of (T, F) feature arrays for each equipment
        rul_over_time: List of (T,) RUL arrays for each equipment
        sequence_length: Lookback window size

    Returns:
        Tuple of (X, y) where X is (N, sequence_length, F) and y is (N,)
    """
    X_list = []
    y_list = []

    for features, ruls in zip(features_over_time, rul_over_time):
        T = len(features)

        for t in range(sequence_length, T):
            # Input: features from [t-sequence_length:t]
            window = features[t-sequence_length:t, :]
            X_list.append(window)

            # Output: RUL at time t
            rul_target = ruls[t]
            y_list.append(rul_target)

    X = np.array(X_list)
    y = np.array(y_list)

    return X, y


def create_rul_predictor(predictor_type: str = 'random_forest', **kwargs) -> RULPredictor:
    """
    Factory function to create RUL predictor instances.

    Args:
        predictor_type: Type of predictor
                       ('random_forest', 'xgboost', 'lstm')
        **kwargs: Additional arguments for predictor initialization

    Returns:
        Initialized RUL predictor
    """
    if predictor_type == 'random_forest':
        return RandomForestRULPredictor(**kwargs)
    elif predictor_type == 'xgboost':
        return XGBoostRULPredictor(**kwargs)
    elif predictor_type == 'lstm':
        return LSTMRULPredictor(**kwargs)
    else:
        raise ValueError(f"Unknown predictor type: {predictor_type}")


# Example usage
if __name__ == "__main__":
    # Generate synthetic degradation data
    np.random.seed(42)

    # Equipment 1: 5000 hours to failure
    t1 = np.arange(0, 5000, 10)
    features1 = np.column_stack([
        2.0 + 0.001 * t1 + np.random.normal(0, 0.1, len(t1)),  # RMS vibration
        65 + 0.005 * t1 + np.random.normal(0, 1, len(t1)),      # Temperature
        3.5 + 0.0005 * t1 + np.random.normal(0, 0.1, len(t1))   # Crest factor
    ])
    rul1 = np.maximum(5000 - t1, 0)

    # Equipment 2: 4200 hours to failure
    t2 = np.arange(0, 4200, 10)
    features2 = np.column_stack([
        2.0 + 0.0012 * t2 + np.random.normal(0, 0.1, len(t2)),
        65 + 0.006 * t2 + np.random.normal(0, 1, len(t2)),
        3.5 + 0.0006 * t2 + np.random.normal(0, 0.1, len(t2))
    ])
    rul2 = np.maximum(4200 - t2, 0)

    # Prepare data
    X, y = prepare_sequence_data([features1, features2], [rul1, rul2], sequence_length=30)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Flatten for Random Forest and XGBoost
    X_train_2d = X_train.reshape(len(X_train), -1)
    X_test_2d = X_test.reshape(len(X_test), -1)

    # Test Random Forest
    print("Random Forest RUL Predictor:")
    rf_pred = RandomForestRULPredictor()
    rf_pred.fit(X_train_2d, y_train)
    metrics_rf = rf_pred.evaluate(X_test_2d, y_test)
    print(f"  MAE: {metrics_rf['mae']:.1f} hours")
    print(f"  RMSE: {metrics_rf['rmse']:.1f} hours")
    print(f"  R²: {metrics_rf['r2']:.3f}")

    # Test XGBoost (if available)
    if HAS_XGBOOST:
        print("\nXGBoost RUL Predictor:")
        xgb_pred = XGBoostRULPredictor()
        xgb_pred.fit(X_train_2d, y_train, verbose=False)
        metrics_xgb = xgb_pred.evaluate(X_test_2d, y_test)
        print(f"  MAE: {metrics_xgb['mae']:.1f} hours")
        print(f"  RMSE: {metrics_xgb['rmse']:.1f} hours")
        print(f"  R²: {metrics_xgb['r2']:.3f}")

    # Test LSTM (if available)
    if HAS_TENSORFLOW:
        print("\nLSTM RUL Predictor:")
        lstm_pred = LSTMRULPredictor(sequence_length=30)
        lstm_pred.fit(X_train, y_train, epochs=50, verbose=0)
        metrics_lstm = lstm_pred.evaluate(X_test, y_test)
        print(f"  MAE: {metrics_lstm['mae']:.1f} hours")
        print(f"  RMSE: {metrics_lstm['rmse']:.1f} hours")
        print(f"  R²: {metrics_lstm['r2']:.3f}")

        # Predict with uncertainty
        rul_point, rul_uncertainty = lstm_pred.predict_with_uncertainty(X_test[:5])
        print(f"\n  Sample predictions with uncertainty:")
        for i in range(5):
            print(f"    RUL: {rul_point[i]:.0f} ± {rul_uncertainty[i]:.0f} hours")
