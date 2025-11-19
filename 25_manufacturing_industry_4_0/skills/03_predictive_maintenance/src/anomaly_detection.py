"""
Anomaly Detection Module for Predictive Maintenance

This module provides multiple anomaly detection algorithms for equipment
condition monitoring, including Isolation Forest, Local Outlier Factor,
and autoencoder-based detection.

Author: Industrial AI Team
License: MIT
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from typing import Dict, Tuple, List, Optional
import warnings


class IsolationForestDetector:
    """
    Isolation Forest-based anomaly detector.

    Anomalies are isolated by randomly selecting features and split values.
    Anomalies require fewer splits to isolate than normal points.

    Attributes:
        model: Fitted IsolationForest model
        scaler: StandardScaler for feature normalization
        threshold: Anomaly score threshold (-1 to 1 scale)
    """

    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        """
        Initialize IsolationForestDetector.

        Args:
            contamination: Expected proportion of anomalies (0.01-0.1 typical)
            random_state: Random seed for reproducibility
        """
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.threshold = 0.0
        self.is_fitted = False

    def fit(self, X: np.ndarray):
        """
        Fit anomaly detection model on normal (healthy) data.

        Args:
            X: Training data (num_samples, num_features), assumed to be normal data
        """
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_fitted = True

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect anomalies in new data.

        Args:
            X: Data to check (num_samples, num_features)

        Returns:
            Tuple of:
            - predictions: Array of -1 (anomaly) or 1 (normal)
            - scores: Anomaly scores (-1 to 1, lower = more anomalous)
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)  # -1 (anomaly), 1 (normal)
        scores = self.model.score_samples(X_scaled)  # Higher is more normal

        return predictions, scores

    def get_anomaly_probability(self, X: np.ndarray) -> np.ndarray:
        """
        Get probability (0-1) that each sample is anomalous.

        Args:
            X: Data to check

        Returns:
            Array of anomaly probabilities (0=definitely normal, 1=definitely anomaly)
        """
        _, scores = self.predict(X)

        # Convert scores to probability
        # Scores typically range from -1 (anomalous) to 0.1 (normal)
        # Map to 0-1 range
        prob = 1.0 / (1.0 + np.exp(scores))  # Sigmoid transformation

        return prob


class LocalOutlierFactorDetector:
    """
    Local Outlier Factor (LOF) anomaly detector.

    LOF compares local density of points. Anomalies are in sparse regions.
    Effective for both global and local anomalies.

    Attributes:
        model: Fitted LocalOutlierFactor model
        scaler: StandardScaler for normalization
    """

    def __init__(self, n_neighbors: int = 20, contamination: float = 0.05):
        """
        Initialize LocalOutlierFactorDetector.

        Args:
            n_neighbors: Number of neighbors for local density calculation
            contamination: Expected anomaly proportion
        """
        self.model = LocalOutlierFactor(
            n_neighbors=n_neighbors,
            contamination=contamination,
            novelty=True  # Enable detection on new data
        )
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit(self, X: np.ndarray):
        """
        Fit LOF model on normal data.

        Args:
            X: Training data (assumed to be normal)
        """
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_fitted = True

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect anomalies.

        Args:
            X: Data to check

        Returns:
            Tuple of:
            - predictions: Array of -1 (anomaly) or 1 (normal)
            - lof_scores: LOF scores (>1 indicates anomaly)
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted.")

        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        lof_scores = self.model.negative_outlier_factor_  # More negative = more anomalous

        return predictions, -lof_scores  # Negate for intuitive interpretation (>1 = anomaly)


class OneClassSVMDetector:
    """
    One-Class SVM anomaly detector.

    Learns boundary around normal data. Points outside boundary are anomalies.
    Effective for high-dimensional data and complex decision boundaries.
    """

    def __init__(self, kernel: str = 'rbf', nu: float = 0.05, gamma: str = 'auto'):
        """
        Initialize OneClassSVMDetector.

        Args:
            kernel: Kernel type ('rbf', 'linear', 'poly')
            nu: Upper bound on anomaly fraction (0.01-0.1)
            gamma: Kernel coefficient ('auto' or float)
        """
        self.model = OneClassSVM(kernel=kernel, nu=nu, gamma=gamma)
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit(self, X: np.ndarray):
        """Fit One-Class SVM on normal data."""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_fitted = True

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect anomalies.

        Args:
            X: Data to check

        Returns:
            Tuple of:
            - predictions: -1 (anomaly) or 1 (normal)
            - distances: Distance from decision boundary (negative = anomaly)
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted.")

        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        distances = self.model.decision_function(X_scaled)

        return predictions, distances


class AutoencoderDetector:
    """
    Autoencoder-based anomaly detector using reconstruction error.

    Autoencoders learn to reconstruct normal data. High reconstruction error
    indicates anomalous data.
    """

    def __init__(self, encoding_dim: int = 10, contamination: float = 0.05):
        """
        Initialize AutoencoderDetector.

        Args:
            encoding_dim: Dimension of bottleneck layer
            contamination: Expected anomaly proportion (for threshold setting)
        """
        self.encoding_dim = encoding_dim
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.reconstruction_errors = None
        self.threshold = None
        self.is_fitted = False

        # Try to import TensorFlow
        try:
            import tensorflow as tf
            from tensorflow import keras
            self.tf = tf
            self.keras = keras
            self.has_tf = True
        except ImportError:
            warnings.warn("TensorFlow not installed. Autoencoder functionality unavailable.")
            self.has_tf = False

    def fit(self, X: np.ndarray, epochs: int = 50, batch_size: int = 32, verbose: int = 0):
        """
        Fit autoencoder on normal data.

        Args:
            X: Training data (num_samples, num_features)
            epochs: Training epochs
            batch_size: Batch size for training
            verbose: TensorFlow verbosity level
        """
        if not self.has_tf:
            raise RuntimeError("TensorFlow required for autoencoder.")

        X_scaled = self.scaler.fit_transform(X)

        # Build autoencoder
        input_dim = X.shape[1]

        encoder = self.keras.Sequential([
            self.keras.layers.Dense(64, activation='relu', input_dim=input_dim),
            self.keras.layers.Dense(32, activation='relu'),
            self.keras.layers.Dense(self.encoding_dim, activation='relu')
        ])

        decoder = self.keras.Sequential([
            self.keras.layers.Dense(32, activation='relu', input_dim=self.encoding_dim),
            self.keras.layers.Dense(64, activation='relu'),
            self.keras.layers.Dense(input_dim, activation='linear')
        ])

        autoencoder = self.keras.Sequential([encoder, decoder])
        autoencoder.compile(optimizer='adam', loss='mse')

        # Train
        autoencoder.fit(
            X_scaled, X_scaled,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.1,
            verbose=verbose
        )

        # Calculate reconstruction error on training data
        X_pred = autoencoder.predict(X_scaled, verbose=0)
        self.reconstruction_errors = np.mean(np.power(X_scaled - X_pred, 2), axis=1)

        # Set threshold (95th percentile of training errors)
        self.threshold = np.percentile(self.reconstruction_errors, 100 * (1 - self.contamination))

        self.autoencoder = autoencoder
        self.is_fitted = True

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect anomalies based on reconstruction error.

        Args:
            X: Data to check

        Returns:
            Tuple of:
            - predictions: -1 (anomaly) or 1 (normal)
            - reconstruction_errors: Reconstruction error for each sample
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted.")

        X_scaled = self.scaler.transform(X)
        X_pred = self.autoencoder.predict(X_scaled, verbose=0)

        errors = np.mean(np.power(X_scaled - X_pred, 2), axis=1)
        predictions = np.where(errors > self.threshold, -1, 1)

        return predictions, errors


class EnsembleAnomalyDetector:
    """
    Ensemble anomaly detector combining multiple algorithms.

    Uses voting mechanism for robust anomaly detection.
    """

    def __init__(self, algorithms: Optional[List[str]] = None):
        """
        Initialize ensemble detector.

        Args:
            algorithms: List of algorithms to include
                       ('isolation_forest', 'lof', 'one_class_svm')
                       Default: all three
        """
        if algorithms is None:
            algorithms = ['isolation_forest', 'lof', 'one_class_svm']

        self.algorithms = algorithms
        self.detectors = {}

        if 'isolation_forest' in algorithms:
            self.detectors['isolation_forest'] = IsolationForestDetector()

        if 'lof' in algorithms:
            self.detectors['lof'] = LocalOutlierFactorDetector()

        if 'one_class_svm' in algorithms:
            self.detectors['one_class_svm'] = OneClassSVMDetector()

    def fit(self, X: np.ndarray):
        """
        Fit all detectors on normal data.

        Args:
            X: Training data
        """
        for detector in self.detectors.values():
            detector.fit(X)

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """
        Ensemble anomaly detection.

        Args:
            X: Data to check

        Returns:
            Tuple of:
            - ensemble_predictions: -1 (anomaly) or 1 (normal) by voting
            - anomaly_scores: Confidence scores (0-1)
            - individual_results: Results from each detector
        """
        individual_results = {}
        votes = np.zeros(len(X))
        scores = np.zeros(len(X))

        for name, detector in self.detectors.items():
            preds, scores_algo = detector.predict(X)
            individual_results[name] = {'predictions': preds, 'scores': scores_algo}

            # Vote (-1 for anomaly)
            votes += (preds == -1).astype(int)
            scores += 1.0 / (1.0 + np.exp(scores_algo))  # Normalize to 0-1

        # Ensemble prediction (majority vote)
        num_detectors = len(self.detectors)
        votes_normalized = votes / num_detectors
        anomaly_scores = scores / num_detectors

        # Threshold: >50% of detectors agree it's anomaly
        ensemble_predictions = np.where(votes_normalized > 0.5, -1, 1)

        return ensemble_predictions, anomaly_scores, individual_results


class StatisticalAnomalyDetector:
    """
    Statistical anomaly detector using Z-score and control limits.

    Simple but effective for univariate monitoring.
    """

    def __init__(self, z_threshold: float = 3.0):
        """
        Initialize statistical detector.

        Args:
            z_threshold: Z-score threshold for anomaly (3.0 = 99.7% confidence)
        """
        self.z_threshold = z_threshold
        self.mean = None
        self.std = None

    def fit(self, X: np.ndarray):
        """
        Fit on normal data (calculate mean and std).

        Args:
            X: 1D or 2D array of normal data
        """
        self.mean = np.mean(X, axis=0)
        self.std = np.std(X, axis=0)

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect anomalies using Z-score.

        Args:
            X: Data to check

        Returns:
            Tuple of:
            - predictions: -1 (anomaly) or 1 (normal)
            - z_scores: Absolute Z-scores
        """
        if self.mean is None or self.std is None:
            raise ValueError("Model not fitted.")

        z_scores = np.abs((X - self.mean) / (self.std + 1e-10))

        if len(z_scores.shape) > 1:
            z_scores = np.max(z_scores, axis=1)  # Use max Z-score across features

        predictions = np.where(z_scores > self.z_threshold, -1, 1)

        return predictions, z_scores


def create_anomaly_detector(detector_type: str = 'ensemble', **kwargs) -> object:
    """
    Factory function to create anomaly detector instances.

    Args:
        detector_type: Type of detector to create
                      ('isolation_forest', 'lof', 'one_class_svm', 'ensemble', 'statistical')
        **kwargs: Additional arguments for detector initialization

    Returns:
        Initialized anomaly detector
    """
    if detector_type == 'isolation_forest':
        return IsolationForestDetector(**kwargs)
    elif detector_type == 'lof':
        return LocalOutlierFactorDetector(**kwargs)
    elif detector_type == 'one_class_svm':
        return OneClassSVMDetector(**kwargs)
    elif detector_type == 'ensemble':
        return EnsembleAnomalyDetector(**kwargs)
    elif detector_type == 'statistical':
        return StatisticalAnomalyDetector(**kwargs)
    else:
        raise ValueError(f"Unknown detector type: {detector_type}")


# Example usage
if __name__ == "__main__":
    # Generate synthetic normal data and anomalies
    np.random.seed(42)

    # Normal data
    X_normal = np.random.normal(loc=0, scale=1, size=(100, 5))

    # Anomalies
    X_anomalies = np.random.normal(loc=3, scale=1, size=(10, 5))

    X_train = X_normal
    X_test = np.vstack([X_normal[:20], X_anomalies])
    y_test = np.array([1]*20 + [-1]*10)

    # Test Isolation Forest
    print("Isolation Forest Detector:")
    detector_if = IsolationForestDetector(contamination=0.1)
    detector_if.fit(X_train)
    preds_if, scores_if = detector_if.predict(X_test)
    accuracy_if = np.mean(preds_if == y_test)
    print(f"  Accuracy: {accuracy_if:.2%}")

    # Test LOF
    print("\nLocal Outlier Factor Detector:")
    detector_lof = LocalOutlierFactorDetector(contamination=0.1)
    detector_lof.fit(X_train)
    preds_lof, scores_lof = detector_lof.predict(X_test)
    accuracy_lof = np.mean(preds_lof == y_test)
    print(f"  Accuracy: {accuracy_lof:.2%}")

    # Test Ensemble
    print("\nEnsemble Anomaly Detector:")
    detector_ens = EnsembleAnomalyDetector()
    detector_ens.fit(X_train)
    preds_ens, scores_ens, individual = detector_ens.predict(X_test)
    accuracy_ens = np.mean(preds_ens == y_test)
    print(f"  Accuracy: {accuracy_ens:.2%}")

    # Test Statistical
    print("\nStatistical Detector:")
    detector_stat = StatisticalAnomalyDetector(z_threshold=3.0)
    detector_stat.fit(X_train)
    preds_stat, z_scores = detector_stat.predict(X_test)
    accuracy_stat = np.mean(preds_stat == y_test)
    print(f"  Accuracy: {accuracy_stat:.2%}")
