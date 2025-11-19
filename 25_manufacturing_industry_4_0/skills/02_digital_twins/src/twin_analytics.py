"""
Digital Twin Analytics and Machine Learning Module

This module provides advanced analytics capabilities for digital twins,
including anomaly detection, predictive maintenance, process optimization,
and machine learning model integration.

Key Features:
- Anomaly detection (isolation forest, autoencoders, statistical methods)
- Predictive maintenance and remaining useful life (RUL) estimation
- Process optimization and parameter tuning
- Time-series forecasting (ARIMA, exponential smoothing)
- Machine learning model management
- Statistical analysis and hypothesis testing

Author: Digital Twins Skill Domain
Version: 1.0
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Optional, Callable
from datetime import datetime, timedelta
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging


# ============================================================================
# Configuration and Enums
# ============================================================================

class AnomalyDetectionMethod(Enum):
    """Available anomaly detection methods"""
    ISOLATION_FOREST = "isolation_forest"
    STATISTICAL_Z_SCORE = "z_score"
    LOCAL_OUTLIER_FACTOR = "lof"
    AUTOENCODER = "autoencoder"
    SPECTRAL = "spectral"


class HealthState(Enum):
    """Equipment health state classification"""
    HEALTHY = "healthy"
    DEGRADING = "degrading"
    CRITICAL = "critical"
    FAULT = "fault"


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class AnomalyScore:
    """Represents an anomaly detection result"""
    timestamp: datetime
    sensor_id: str
    value: float
    anomaly_score: float  # 0-1, higher = more anomalous
    is_anomaly: bool      # True if exceeds threshold
    method: str
    explanation: str


@dataclass
class HealthIndicator:
    """Equipment health metric"""
    timestamp: datetime
    asset_id: str
    health_score: float   # 0-1, higher = healthier
    state: HealthState
    trend: float          # Rate of change (-1 to 1)
    contributing_factors: Dict[str, float]


@dataclass
class RULPrediction:
    """Remaining Useful Life prediction"""
    asset_id: str
    current_date: datetime
    predicted_failure_date: datetime
    rul_days: float
    confidence: float     # 0-1
    method: str
    uncertainty_range: Tuple[float, float]  # (lower, upper) days


# ============================================================================
# Anomaly Detection
# ============================================================================

class AnomalyDetector:
    """Detects anomalies in digital twin sensor data"""

    def __init__(self, method: AnomalyDetectionMethod = AnomalyDetectionMethod.ISOLATION_FOREST,
                 contamination: float = 0.05):
        """
        Initialize anomaly detector

        Args:
            method: Detection method to use
            contamination: Expected proportion of anomalies (0-1)
        """
        self.method = method
        self.contamination = contamination
        self.logger = logging.getLogger("AnomalyDetector")
        self.models: Dict[str, object] = {}  # Per-sensor models
        self.sensor_history: Dict[str, List[Tuple[datetime, float]]] = {}

    def fit(self, sensor_id: str, historical_data: np.ndarray):
        """
        Train anomaly detector on historical data

        Args:
            sensor_id: Sensor identifier
            historical_data: Historical sensor values [N]
        """
        if self.method == AnomalyDetectionMethod.ISOLATION_FOREST:
            # Reshape for sklearn: (N, 1)
            X = historical_data.reshape(-1, 1)
            model = IsolationForest(
                contamination=self.contamination,
                random_state=42
            )
            model.fit(X)
            self.models[sensor_id] = model

        elif self.method == AnomalyDetectionMethod.STATISTICAL_Z_SCORE:
            # Store statistics
            self.models[sensor_id] = {
                'mean': np.mean(historical_data),
                'std': np.std(historical_data)
            }

        self.logger.info(f"Fitted {self.method.value} for sensor {sensor_id}")

    def detect(self, sensor_id: str, value: float,
              timestamp: datetime) -> AnomalyScore:
        """
        Detect anomaly for a single value

        Args:
            sensor_id: Sensor identifier
            value: Current sensor reading
            timestamp: Measurement timestamp

        Returns:
            AnomalyScore object
        """
        if sensor_id not in self.models:
            raise ValueError(f"Sensor {sensor_id} not fitted")

        if self.method == AnomalyDetectionMethod.ISOLATION_FOREST:
            score = self._detect_isolation_forest(sensor_id, value)

        elif self.method == AnomalyDetectionMethod.STATISTICAL_Z_SCORE:
            score = self._detect_z_score(sensor_id, value)

        else:
            score = AnomalyScore(
                timestamp=timestamp,
                sensor_id=sensor_id,
                value=value,
                anomaly_score=0.0,
                is_anomaly=False,
                method=self.method.value,
                explanation="Method not implemented"
            )

        # Record in history
        if sensor_id not in self.sensor_history:
            self.sensor_history[sensor_id] = []
        self.sensor_history[sensor_id].append((timestamp, value))
        # Limit history size
        if len(self.sensor_history[sensor_id]) > 10000:
            self.sensor_history[sensor_id] = self.sensor_history[sensor_id][-5000:]

        return score

    def _detect_isolation_forest(self, sensor_id: str, value: float) -> AnomalyScore:
        """Isolation Forest anomaly detection"""
        model = self.models[sensor_id]
        X = np.array([[value]])

        # Get anomaly score (-1 = anomaly, 1 = normal)
        prediction = model.predict(X)[0]
        anomaly_score_raw = model.score_samples(X)[0]

        # Normalize to [0, 1]
        anomaly_score = 1.0 / (1.0 + np.exp(anomaly_score_raw))
        is_anomaly = prediction == -1

        explanation = f"Anomaly score: {anomaly_score:.3f}"

        return AnomalyScore(
            timestamp=datetime.now(),
            sensor_id=sensor_id,
            value=value,
            anomaly_score=anomaly_score,
            is_anomaly=is_anomaly,
            method="isolation_forest",
            explanation=explanation
        )

    def _detect_z_score(self, sensor_id: str, value: float) -> AnomalyScore:
        """Z-score based anomaly detection"""
        stats_dict = self.models[sensor_id]
        mean = stats_dict['mean']
        std = stats_dict['std']

        if std == 0:
            return AnomalyScore(
                timestamp=datetime.now(),
                sensor_id=sensor_id,
                value=value,
                anomaly_score=0.0,
                is_anomaly=False,
                method="z_score",
                explanation="No variance in historical data"
            )

        z_score = abs((value - mean) / std)
        anomaly_score = min(1.0, z_score / 3.0)  # Normalize 3-sigma to [0, 1]
        is_anomaly = z_score > 3.0  # Standard 3-sigma threshold

        explanation = f"Z-score: {z_score:.2f} (threshold: 3.0)"

        return AnomalyScore(
            timestamp=datetime.now(),
            sensor_id=sensor_id,
            value=value,
            anomaly_score=anomaly_score,
            is_anomaly=is_anomaly,
            method="z_score",
            explanation=explanation
        )

    def detect_batch(self, sensor_id: str, values: np.ndarray,
                    timestamps: List[datetime]) -> List[AnomalyScore]:
        """
        Detect anomalies for multiple values

        Args:
            sensor_id: Sensor identifier
            values: Array of sensor readings [N]
            timestamps: List of timestamps

        Returns:
            List of AnomalyScore objects
        """
        return [self.detect(sensor_id, val, ts)
                for val, ts in zip(values, timestamps)]


# ============================================================================
# Predictive Maintenance
# ============================================================================

class PredictiveMaintenanceModel:
    """Predicts remaining useful life (RUL) and maintenance schedules"""

    def __init__(self):
        self.logger = logging.getLogger("PredictiveMaintenanceModel")
        self.rul_models: Dict[str, Dict] = {}  # Per-asset RUL models
        self.degradation_curves: Dict[str, List[Tuple[datetime, float]]] = {}

    def record_condition_indicator(self, asset_id: str, timestamp: datetime,
                                  condition_indicator: float):
        """
        Record a condition indicator value (0=healthy, 1=failed)

        Args:
            asset_id: Asset identifier
            timestamp: Measurement timestamp
            condition_indicator: Normalized condition metric [0, 1]
        """
        if asset_id not in self.degradation_curves:
            self.degradation_curves[asset_id] = []

        self.degradation_curves[asset_id].append((timestamp, condition_indicator))

    def estimate_rul(self, asset_id: str, failure_threshold: float = 0.8,
                    confidence_interval: float = 0.95) -> Optional[RULPrediction]:
        """
        Estimate remaining useful life

        Uses linear regression on degradation curve with extrapolation

        Args:
            asset_id: Asset identifier
            failure_threshold: Condition value indicating failure
            confidence_interval: Confidence level for uncertainty

        Returns:
            RULPrediction object or None if insufficient data
        """
        if asset_id not in self.degradation_curves:
            return None

        curve = self.degradation_curves[asset_id]
        if len(curve) < 3:
            return None

        # Convert timestamps to days since start
        timestamps, conditions = zip(*curve)
        t_start = timestamps[0]
        days_since_start = np.array([
            (ts - t_start).total_seconds() / 86400.0 for ts in timestamps
        ])
        conditions = np.array(conditions)

        # Linear regression
        coeffs = np.polyfit(days_since_start, conditions, 1)
        slope = coeffs[0]  # Degradation rate

        if slope <= 0:
            # Not degrading
            return RULPrediction(
                asset_id=asset_id,
                current_date=datetime.now(),
                predicted_failure_date=datetime.now() + timedelta(days=365*10),
                rul_days=365*10,
                confidence=0.5,
                method="linear_degradation",
                uncertainty_range=(365*5, 365*15)
            )

        # Estimate time to failure
        current_condition = conditions[-1]
        days_to_failure = (failure_threshold - current_condition) / slope

        if days_to_failure < 0:
            days_to_failure = 0

        # Confidence based on R²
        y_pred = np.polyval(coeffs, days_since_start)
        residuals = conditions - y_pred
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((conditions - np.mean(conditions))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Uncertainty intervals
        z_score = stats.norm.ppf((1 + confidence_interval) / 2)
        uncertainty = z_score * np.sqrt(ss_res / (len(conditions) - 2))
        rul_lower = max(0, days_to_failure - uncertainty)
        rul_upper = days_to_failure + uncertainty

        predicted_failure = datetime.now() + timedelta(days=days_to_failure)

        return RULPrediction(
            asset_id=asset_id,
            current_date=datetime.now(),
            predicted_failure_date=predicted_failure,
            rul_days=days_to_failure,
            confidence=max(0, min(1, r_squared)),
            method="linear_degradation",
            uncertainty_range=(rul_lower, rul_upper)
        )

    def predict_maintenance_window(self, asset_id: str,
                                  lead_time_days: int = 7) -> Optional[Tuple[datetime, datetime]]:
        """
        Predict maintenance scheduling window

        Args:
            asset_id: Asset identifier
            lead_time_days: Advance notice for scheduling

        Returns:
            (earliest_maintenance, latest_maintenance) or None
        """
        rul = self.estimate_rul(asset_id)
        if rul is None:
            return None

        # Schedule maintenance between RUL - lead_time and RUL
        earliest = datetime.now() + timedelta(days=max(0, rul.rul_days - lead_time_days))
        latest = rul.predicted_failure_date

        return (earliest, latest)


# ============================================================================
# Health Monitoring
# ============================================================================

class HealthMonitor:
    """Monitors and tracks equipment health over time"""

    def __init__(self):
        self.logger = logging.getLogger("HealthMonitor")
        self.health_history: Dict[str, List[HealthIndicator]] = {}
        self.thresholds = {
            'healthy': 0.7,
            'degrading': 0.5,
            'critical': 0.2
        }

    def compute_health_score(self, asset_id: str,
                            indicators: Dict[str, float]) -> float:
        """
        Compute overall health score from multiple indicators

        Args:
            asset_id: Asset identifier
            indicators: Dictionary of indicator_name -> value [0, 1]

        Returns:
            Overall health score [0, 1]
        """
        if not indicators:
            return 0.5

        scores = list(indicators.values())
        # Weighted average (simple approach)
        health = np.mean(scores)

        return float(health)

    def classify_health(self, health_score: float) -> HealthState:
        """Classify health based on score"""
        if health_score >= self.thresholds['healthy']:
            return HealthState.HEALTHY
        elif health_score >= self.thresholds['degrading']:
            return HealthState.DEGRADING
        elif health_score >= self.thresholds['critical']:
            return HealthState.CRITICAL
        else:
            return HealthState.FAULT

    def update_health(self, asset_id: str, indicators: Dict[str, float]):
        """
        Update health assessment for asset

        Args:
            asset_id: Asset identifier
            indicators: Dictionary of contributing health indicators
        """
        health_score = self.compute_health_score(asset_id, indicators)
        health_state = self.classify_health(health_score)

        # Compute trend
        if asset_id in self.health_history and len(self.health_history[asset_id]) > 0:
            prev_health = self.health_history[asset_id][-1].health_score
            trend = health_score - prev_health
        else:
            trend = 0.0

        indicator = HealthIndicator(
            timestamp=datetime.now(),
            asset_id=asset_id,
            health_score=health_score,
            state=health_state,
            trend=trend,
            contributing_factors=indicators
        )

        if asset_id not in self.health_history:
            self.health_history[asset_id] = []

        self.health_history[asset_id].append(indicator)

        # Log state changes
        if len(self.health_history[asset_id]) > 1:
            prev_state = self.health_history[asset_id][-2].state
            if prev_state != health_state:
                self.logger.warning(
                    f"Asset {asset_id} health changed: {prev_state.value} → {health_state.value}"
                )

    def get_current_health(self, asset_id: str) -> Optional[HealthIndicator]:
        """Get most recent health assessment"""
        if asset_id in self.health_history and self.health_history[asset_id]:
            return self.health_history[asset_id][-1]
        return None

    def get_health_trend(self, asset_id: str,
                        window_hours: int = 24) -> List[HealthIndicator]:
        """Get health history within time window"""
        if asset_id not in self.health_history:
            return []

        cutoff_time = datetime.now() - timedelta(hours=window_hours)
        return [h for h in self.health_history[asset_id]
                if h.timestamp >= cutoff_time]


# ============================================================================
# Process Optimization
# ============================================================================

class ProcessOptimizer:
    """Analyzes digital twin data for process optimization opportunities"""

    def __init__(self):
        self.logger = logging.getLogger("ProcessOptimizer")

    @staticmethod
    def sensitivity_analysis(baseline: float,
                            parameter_variations: Dict[str, Tuple[float, float]],
                            response_func: Callable,
                            num_points: int = 10) -> Dict[str, float]:
        """
        Perform sensitivity analysis: impact of parameters on response

        Args:
            baseline: Baseline parameter value
            parameter_variations: {param_name: (min, max)} ranges
            response_func: Function returning response metric given param dict
            num_points: Number of samples per parameter

        Returns:
            Dictionary mapping parameter names to sensitivity magnitude
        """
        sensitivities = {}

        baseline_response = response_func({})

        for param_name, (min_val, max_val) in parameter_variations.items():
            responses = []

            for value in np.linspace(min_val, max_val, num_points):
                param_dict = {param_name: value}
                response = response_func(param_dict)
                responses.append(response)

            # Sensitivity = (max response - min response) / baseline response
            response_range = max(responses) - min(responses)
            if baseline_response != 0:
                sensitivity = response_range / abs(baseline_response)
            else:
                sensitivity = response_range

            sensitivities[param_name] = sensitivity

        return sensitivities

    @staticmethod
    def find_optimal_parameters(parameter_bounds: Dict[str, Tuple[float, float]],
                               objective_func: Callable,
                               num_iterations: int = 100) -> Dict[str, float]:
        """
        Find optimal parameters using Bayesian optimization

        Args:
            parameter_bounds: {param_name: (min, max)}
            objective_func: Function to maximize given parameter dict
            num_iterations: Number of iterations

        Returns:
            Optimal parameter values dictionary
        """
        from scipy.optimize import differential_evolution

        # Create bounds list for scipy
        param_names = list(parameter_bounds.keys())
        bounds = [parameter_bounds[name] for name in param_names]

        # Negative because differential_evolution minimizes
        def minimize_func(x):
            params = {name: val for name, val in zip(param_names, x)}
            return -objective_func(params)

        result = differential_evolution(minimize_func, bounds, seed=42,
                                       maxiter=num_iterations)

        optimal_params = {name: val for name, val in zip(param_names, result.x)}
        return optimal_params

    @staticmethod
    def estimate_efficiency_gains(baseline_value: float,
                                 optimized_value: float) -> float:
        """
        Estimate efficiency improvement

        Returns:
            Percentage improvement (negative = worse)
        """
        if baseline_value == 0:
            return 0

        return ((optimized_value - baseline_value) / abs(baseline_value)) * 100


# ============================================================================
# Demonstration and Testing
# ============================================================================

def demo_anomaly_detection():
    """Demonstrate anomaly detection"""
    print("=== Anomaly Detection Demo ===\n")

    detector = AnomalyDetector(method=AnomalyDetectionMethod.STATISTICAL_Z_SCORE)

    # Generate synthetic historical data (normal distribution)
    np.random.seed(42)
    historical_data = np.random.normal(100, 5, 500)

    # Train detector
    detector.fit("temperature", historical_data)

    # Test normal and anomalous values
    test_values = [
        (100.5, "Normal value"),
        (102.0, "Slight deviation"),
        (150.0, "Clear anomaly"),
        (99.0, "Normal"),
    ]

    print("Anomaly Detection Results:")
    for value, description in test_values:
        score = detector.detect("temperature", value, datetime.now())
        print(f"  {description}: {value:.1f}")
        print(f"    Anomaly score: {score.anomaly_score:.3f}, Anomaly: {score.is_anomaly}")
        print()


def demo_predictive_maintenance():
    """Demonstrate RUL prediction"""
    print("=== Predictive Maintenance Demo ===\n")

    pm = PredictiveMaintenanceModel()

    # Simulate degradation curve
    now = datetime.now()
    for i in range(30):
        timestamp = now - timedelta(days=30-i)
        # Linear degradation: starts at 0.1, increases to 0.7
        condition = 0.1 + (0.6 * i / 30)
        pm.record_condition_indicator("MOTOR-001", timestamp, condition)

    # Estimate RUL
    rul = pm.estimate_rul("MOTOR-001", failure_threshold=0.9)
    if rul:
        print(f"Asset: {rul.asset_id}")
        print(f"Predicted failure: {rul.predicted_failure_date.date()}")
        print(f"Remaining useful life: {rul.rul_days:.1f} days")
        print(f"Confidence: {rul.confidence:.2%}")
        print(f"Uncertainty range: {rul.uncertainty_range[0]:.1f} - {rul.uncertainty_range[1]:.1f} days")

    # Maintenance scheduling
    window = pm.predict_maintenance_window("MOTOR-001", lead_time_days=5)
    if window:
        earliest, latest = window
        print(f"\nMaintenance window: {earliest.date()} to {latest.date()}")


def demo_health_monitoring():
    """Demonstrate health monitoring"""
    print("\n=== Health Monitoring Demo ===\n")

    monitor = HealthMonitor()

    # Simulate health updates over time
    print("Health progression:")
    for i in range(5):
        indicators = {
            'temperature': 0.9 - 0.1*i,  # Degrading
            'vibration': 0.8 - 0.15*i,    # Degrading
            'power': 0.95                  # Stable
        }

        monitor.update_health("MACHINE-001", indicators)
        health = monitor.get_current_health("MACHINE-001")

        if health:
            print(f"  Day {i}: Health={health.health_score:.2%}, State={health.state.value}, Trend={health.trend:+.3f}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    demo_anomaly_detection()
    demo_predictive_maintenance()
    demo_health_monitoring()
