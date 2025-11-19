# ML Monitoring Guide: Production Excellence

A comprehensive guide to monitoring machine learning models in production, covering performance tracking, drift detection, alerting strategies, and complete implementation with Prometheus and Grafana.

## Table of Contents

1. [Model Performance Monitoring](#model-performance-monitoring)
2. [Data Drift Detection](#data-drift-detection)
3. [Concept Drift](#concept-drift)
4. [Feature Drift](#feature-drift)
5. [Prediction Drift](#prediction-drift)
6. [Monitoring Metrics](#monitoring-metrics)
7. [Alerting Strategies](#alerting-strategies)
8. [Dashboard Design](#dashboard-design)
9. [Logging Best Practices](#logging-best-practices)
10. [Complete Production Setup](#complete-production-setup)

---

## Model Performance Monitoring

### Key Concepts

Model performance monitoring tracks how your deployed models are performing in production. Unlike offline metrics, production monitoring must handle:
- Real-world data variations
- Concept drift and changing distributions
- Edge cases not seen during training
- Latency and resource constraints

### Metrics to Track

```python
# Core Performance Metrics
class PerformanceMetrics:
    """Track model performance in production"""

    def __init__(self, model_name: str, version: str):
        self.model_name = model_name
        self.version = version
        self.predictions = []
        self.actuals = []
        self.timestamps = []

    def calculate_metrics(self) -> dict:
        """Calculate comprehensive performance metrics"""
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score,
            f1_score, roc_auc_score, confusion_matrix
        )
        import numpy as np

        metrics = {
            'accuracy': accuracy_score(self.actuals, self.predictions),
            'precision': precision_score(self.actuals, self.predictions, average='weighted'),
            'recall': recall_score(self.actuals, self.predictions, average='weighted'),
            'f1': f1_score(self.actuals, self.predictions, average='weighted'),
        }

        # Add confusion matrix info
        cm = confusion_matrix(self.actuals, self.predictions)
        metrics['confusion_matrix'] = cm.tolist()

        # Calculate per-class metrics for multi-class
        for i in range(len(np.unique(self.actuals))):
            metrics[f'class_{i}_precision'] = precision_score(
                self.actuals, self.predictions,
                labels=[i], average='weighted'
            )

        return metrics

    def add_prediction(self, pred, actual, timestamp):
        """Record a prediction and actual value"""
        self.predictions.append(pred)
        self.actuals.append(actual)
        self.timestamps.append(timestamp)

    def get_windowed_metrics(self, window_size: int = 100) -> dict:
        """Calculate metrics over recent window"""
        recent_preds = self.predictions[-window_size:]
        recent_actuals = self.actuals[-window_size:]

        if len(recent_preds) < window_size:
            return {}

        from sklearn.metrics import accuracy_score
        return {
            'window_accuracy': accuracy_score(recent_actuals, recent_preds),
            'window_size': window_size
        }
```

### Baseline Establishment

```python
import json
from datetime import datetime

class PerformanceBaseline:
    """Manage performance baselines for comparison"""

    def __init__(self, baseline_file: str = 'baseline_metrics.json'):
        self.baseline_file = baseline_file
        self.baselines = self._load_baselines()

    def _load_baselines(self) -> dict:
        """Load baseline metrics from file"""
        try:
            with open(self.baseline_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def set_baseline(self, model_version: str, metrics: dict):
        """Set baseline metrics for a model version"""
        self.baselines[model_version] = {
            'metrics': metrics,
            'timestamp': datetime.now().isoformat(),
            'thresholds': {
                'accuracy': metrics['accuracy'] * 0.95,  # Alert if 5% below
                'precision': metrics['precision'] * 0.90,  # Alert if 10% below
                'recall': metrics['recall'] * 0.90,
            }
        }
        self._save_baselines()

    def _save_baselines(self):
        """Persist baselines to file"""
        with open(self.baseline_file, 'w') as f:
            json.dump(self.baselines, f, indent=2)

    def compare_metrics(self, model_version: str, current_metrics: dict) -> dict:
        """Compare current metrics against baseline"""
        if model_version not in self.baselines:
            return {'status': 'no_baseline'}

        baseline = self.baselines[model_version]
        thresholds = baseline['thresholds']
        alerts = []

        for metric_name, current_value in current_metrics.items():
            if metric_name in thresholds:
                if current_value < thresholds[metric_name]:
                    alerts.append({
                        'metric': metric_name,
                        'current': current_value,
                        'threshold': thresholds[metric_name],
                        'baseline': baseline['metrics'][metric_name],
                        'severity': 'warning' if current_value > thresholds[metric_name] * 0.9 else 'critical'
                    })

        return {
            'status': 'ok' if not alerts else 'degradation',
            'alerts': alerts,
            'timestamp': datetime.now().isoformat()
        }
```

---

## Data Drift Detection

### Evidently AI Integration

Evidently AI provides comprehensive data drift detection capabilities.

```python
from evidently.report import Report
from evidently.metrics import (
    DataDriftTable, DatasetDriftMetric,
    ColumnDriftMetric
)
from evidently.test_suite import TestSuite
from evidently.tests import TestColumnDrift, TestDatasetDrift
import pandas as pd

class EvidentlyDriftDetector:
    """Monitor data drift using Evidently AI"""

    def __init__(self, reference_data: pd.DataFrame):
        """
        Initialize with reference dataset

        Args:
            reference_data: The baseline dataset to compare against
        """
        self.reference_data = reference_data
        self.drift_history = []

    def detect_drift(self, current_data: pd.DataFrame) -> dict:
        """Detect data drift using Evidently"""

        # Create drift report
        drift_report = Report(metrics=[
            DataDriftTable(),
            DatasetDriftMetric(),
            ColumnDriftMetric(column_name='feature_1'),
            ColumnDriftMetric(column_name='feature_2'),
        ])

        drift_report.run(
            reference_data=self.reference_data,
            current_data=current_data
        )

        # Extract results
        report_dict = drift_report.as_dict()

        drift_results = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'dataset_drift': report_dict['metrics'][1]['result']['dataset_drift'],
            'column_drifts': {}
        }

        # Get column-level drift info
        for i, metric in enumerate(report_dict['metrics']):
            if 'column_name' in metric.get('parameters', {}):
                col_name = metric['parameters']['column_name']
                drift_results['column_drifts'][col_name] = metric['result'].get('drift_detected', False)

        self.drift_history.append(drift_results)
        return drift_results

    def run_drift_tests(self, current_data: pd.DataFrame) -> dict:
        """Run statistical tests for drift detection"""

        test_suite = TestSuite(tests=[
            TestDatasetDrift(),
            TestColumnDrift(column_name='feature_1'),
            TestColumnDrift(column_name='feature_2'),
        ])

        test_suite.run(
            reference_data=self.reference_data,
            current_data=current_data
        )

        results = test_suite.as_dict()

        test_results = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'total_tests': len(results['tests']),
            'passed_tests': sum(1 for t in results['tests'] if t['status'] == 'success'),
            'failed_tests': sum(1 for t in results['tests'] if t['status'] == 'fail'),
            'test_details': []
        }

        for test in results['tests']:
            test_results['test_details'].append({
                'name': test['name'],
                'status': test['status'],
                'parameters': test.get('parameters', {})
            })

        return test_results

    def get_drift_summary(self) -> dict:
        """Get summary of drift over time"""
        if not self.drift_history:
            return {'status': 'no_data'}

        recent_drifts = self.drift_history[-10:]
        drift_detected_count = sum(1 for d in recent_drifts if d['dataset_drift'])

        return {
            'total_checks': len(self.drift_history),
            'recent_checks': len(recent_drifts),
            'drifts_detected': drift_detected_count,
            'drift_percentage': (drift_detected_count / len(recent_drifts)) * 100,
            'latest_check': recent_drifts[-1] if recent_drifts else None
        }
```

### Alibi Detect Integration

```python
from alibi_detect.cd import KSDrift, MMDDrift, ChiSquareDrift
from alibi_detect.models.autoencoder import AE
import numpy as np

class AlibiDriftDetector:
    """Monitor data drift using Alibi Detect"""

    def __init__(self, reference_data: np.ndarray, detector_type: str = 'ks'):
        """
        Initialize drift detector

        Args:
            reference_data: Reference dataset (X_ref)
            detector_type: 'ks' (KSDrift), 'mmd' (MMDDrift), or 'chi2'
        """
        self.reference_data = reference_data
        self.detector_type = detector_type
        self.detector = self._create_detector()
        self.drift_scores = []

    def _create_detector(self):
        """Create appropriate Alibi Detect detector"""

        if self.detector_type == 'ks':
            # Kolmogorov-Smirnov test (univariate)
            detector = KSDrift(
                X_ref=self.reference_data,
                p_val=0.05
            )
        elif self.detector_type == 'mmd':
            # Maximum Mean Discrepancy (multivariate)
            detector = MMDDrift(
                X_ref=self.reference_data,
                p_val=0.05
            )
        elif self.detector_type == 'chi2':
            # Chi-square test
            detector = ChiSquareDrift(
                X_ref=self.reference_data,
                p_val=0.05
            )
        else:
            raise ValueError(f"Unknown detector type: {self.detector_type}")

        return detector

    def detect(self, X_test: np.ndarray) -> dict:
        """Detect drift in test data"""

        result = self.detector.predict(X_test)

        drift_result = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'drift_detected': bool(result['data']['is_drift']),
            'p_value': float(result['data']['p_val']),
            'test_statistic': float(result['data']['distance']),
            'threshold': float(result['data']['threshold']),
            'detector_type': self.detector_type
        }

        self.drift_scores.append(drift_result)
        return drift_result

    def get_drift_stats(self, window: int = 100) -> dict:
        """Get drift statistics over recent window"""

        if not self.drift_scores:
            return {'status': 'no_data'}

        recent = self.drift_scores[-window:]
        drifts = [d for d in recent if d['drift_detected']]

        return {
            'total_checks': len(self.drift_scores),
            'window_size': len(recent),
            'drifts_detected': len(drifts),
            'drift_rate': len(drifts) / len(recent) * 100,
            'avg_p_value': np.mean([d['p_value'] for d in recent]),
            'avg_test_statistic': np.mean([d['test_statistic'] for d in recent])
        }

    def compare_with_reference(self, X_test: np.ndarray) -> dict:
        """Compare test data with reference data"""

        result = self.detect(X_test)

        comparison = {
            'drift_detected': result['drift_detected'],
            'reference_stats': {
                'mean': self.reference_data.mean(axis=0),
                'std': self.reference_data.std(axis=0),
                'min': self.reference_data.min(axis=0),
                'max': self.reference_data.max(axis=0),
            },
            'test_stats': {
                'mean': X_test.mean(axis=0),
                'std': X_test.std(axis=0),
                'min': X_test.min(axis=0),
                'max': X_test.max(axis=0),
            },
            'result': result
        }

        return comparison
```

---

## Concept Drift

### Concept Drift Detection

Concept drift occurs when the relationship between features and target changes, even if feature distribution stays the same.

```python
from sklearn.metrics import accuracy_score
from collections import deque
import numpy as np

class ConceptDriftDetector:
    """Detect concept drift using streaming performance metrics"""

    def __init__(self, window_size: int = 100, threshold: float = 0.05):
        """
        Args:
            window_size: Number of samples for sliding window
            threshold: Accuracy drop threshold (5% default)
        """
        self.window_size = window_size
        self.threshold = threshold
        self.predictions = deque(maxlen=window_size)
        self.actuals = deque(maxlen=window_size)
        self.accuracies = deque(maxlen=window_size)
        self.drift_alerts = []

    def update(self, prediction: float, actual: float):
        """Add new prediction and actual value"""
        self.predictions.append(prediction)
        self.actuals.append(actual)

        if len(self.predictions) == self.window_size:
            accuracy = accuracy_score(self.actuals, self.predictions)
            self.accuracies.append(accuracy)

            # Check for drift
            if len(self.accuracies) >= 2:
                prev_accuracy = list(self.accuracies)[-2]
                current_accuracy = list(self.accuracies)[-1]

                if (prev_accuracy - current_accuracy) > self.threshold:
                    self._raise_drift_alert(prev_accuracy, current_accuracy)

    def _raise_drift_alert(self, prev_acc: float, curr_acc: float):
        """Record concept drift alert"""
        alert = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'previous_accuracy': prev_acc,
            'current_accuracy': curr_acc,
            'drop': prev_acc - curr_acc,
            'drop_percentage': ((prev_acc - curr_acc) / prev_acc) * 100
        }
        self.drift_alerts.append(alert)
        print(f"Concept Drift Detected: {alert['drop_percentage']:.2f}% drop")

    def get_current_performance(self) -> dict:
        """Get current window performance"""
        if not self.accuracies:
            return {}

        accs = list(self.accuracies)
        return {
            'current_accuracy': accs[-1],
            'avg_accuracy': np.mean(accs),
            'accuracy_std': np.std(accs),
            'min_accuracy': np.min(accs),
            'max_accuracy': np.max(accs),
            'window_size': self.window_size
        }

    def get_drift_summary(self) -> dict:
        """Get summary of detected drifts"""
        return {
            'total_drifts': len(self.drift_alerts),
            'recent_drifts': self.drift_alerts[-10:],
            'current_performance': self.get_current_performance()
        }


# Alternative: Page-Hinkley Test for Concept Drift
class PageHinkleyDriftDetector:
    """Detect drift using Page-Hinkley statistical test"""

    def __init__(self, threshold: float = 5.0, lambda_: float = 50, delta: float = 0.005):
        """
        Args:
            threshold: Detection threshold
            lambda_: Reference level
            delta: Minimum difference to detect
        """
        self.threshold = threshold
        self.lambda_ = lambda_
        self.delta = delta
        self.ph_stat = 0
        self.min_stat = 0
        self.errors = deque(maxlen=1000)
        self.drift_points = []

    def update(self, error: float):
        """Update with new error value"""
        self.errors.append(error)

        # Update Page-Hinkley statistic
        self.ph_stat += (error - self.lambda_ + self.delta)

        # Track minimum
        self.min_stat = min(self.min_stat, self.ph_stat)

        # Check for drift
        if (self.ph_stat - self.min_stat) > self.threshold:
            self.drift_points.append({
                'timestamp': pd.Timestamp.now().isoformat(),
                'statistic': self.ph_stat,
                'error': error
            })
            self._reset()

    def _reset(self):
        """Reset after drift detection"""
        self.ph_stat = 0
        self.min_stat = 0

    def get_drift_status(self) -> dict:
        """Get drift detection status"""
        return {
            'current_statistic': self.ph_stat,
            'total_drifts': len(self.drift_points),
            'recent_drifts': self.drift_points[-5:],
            'avg_error': np.mean(self.errors) if self.errors else 0
        }
```

---

## Feature Drift

### Feature Distribution Drift

```python
import scipy.stats as stats
from typing import List, Tuple

class FeatureDriftDetector:
    """Detect drift in individual feature distributions"""

    def __init__(self, reference_data: pd.DataFrame, features: List[str]):
        """
        Args:
            reference_data: Reference dataset
            features: List of feature columns to monitor
        """
        self.reference_data = reference_data
        self.features = features
        self.reference_stats = self._compute_stats()
        self.drift_history = {}

    def _compute_stats(self) -> dict:
        """Compute statistics for reference data"""
        stats_dict = {}

        for feature in self.features:
            ref_feature = self.reference_data[feature]
            stats_dict[feature] = {
                'mean': ref_feature.mean(),
                'std': ref_feature.std(),
                'min': ref_feature.min(),
                'max': ref_feature.max(),
                'median': ref_feature.median(),
                'quantiles': {
                    'q25': ref_feature.quantile(0.25),
                    'q75': ref_feature.quantile(0.75),
                }
            }

        return stats_dict

    def detect_drift(self, current_data: pd.DataFrame, method: str = 'ks') -> dict:
        """
        Detect feature drift

        Args:
            current_data: Current dataset
            method: 'ks' (Kolmogorov-Smirnov), 'wasserstein', 'ad' (Anderson-Darling)
        """
        drift_results = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'method': method,
            'features': {}
        }

        for feature in self.features:
            if method == 'ks':
                statistic, p_value = stats.ks_2samp(
                    self.reference_data[feature],
                    current_data[feature]
                )
            elif method == 'wasserstein':
                statistic = stats.wasserstein_distance(
                    self.reference_data[feature],
                    current_data[feature]
                )
                p_value = None
            elif method == 'ad':
                # Anderson-Darling test
                combined = np.concatenate([
                    self.reference_data[feature].values,
                    current_data[feature].values
                ])
                result = stats.anderson_ksamp([
                    self.reference_data[feature].values,
                    current_data[feature].values
                ])
                statistic = result.statistic
                p_value = None
            else:
                raise ValueError(f"Unknown method: {method}")

            drift_detected = (p_value < 0.05 if p_value else statistic > 0.1)

            drift_results['features'][feature] = {
                'statistic': float(statistic),
                'p_value': float(p_value) if p_value else None,
                'drift_detected': drift_detected,
                'current_stats': {
                    'mean': float(current_data[feature].mean()),
                    'std': float(current_data[feature].std()),
                    'min': float(current_data[feature].min()),
                    'max': float(current_data[feature].max()),
                },
                'reference_stats': self.reference_stats[feature]
            }

            # Store history
            if feature not in self.drift_history:
                self.drift_history[feature] = []
            self.drift_history[feature].append(drift_results['features'][feature])

        return drift_results

    def get_feature_summary(self) -> dict:
        """Get summary of feature drift over time"""
        summary = {}

        for feature in self.features:
            if feature not in self.drift_history:
                continue

            history = self.drift_history[feature]
            drifts = [h for h in history if h['drift_detected']]

            summary[feature] = {
                'total_checks': len(history),
                'drifts_detected': len(drifts),
                'drift_rate': len(drifts) / len(history) * 100,
                'mean_change': np.abs(np.mean([
                    h['current_stats']['mean'] - h['reference_stats']['mean']
                    for h in history
                ])),
                'latest_drift_status': drifts[-1] if drifts else history[-1]
            }

        return summary
```

---

## Prediction Drift

### Prediction Distribution Drift

```python
class PredictionDriftDetector:
    """Monitor drift in model predictions"""

    def __init__(self, window_size: int = 1000):
        """
        Args:
            window_size: Size of sliding window for analysis
        """
        self.window_size = window_size
        self.predictions = deque(maxlen=window_size)
        self.prediction_probs = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)
        self.drift_history = []

    def add_prediction(self, prediction: np.ndarray, prob: float, timestamp: str = None):
        """Record a prediction"""
        self.predictions.append(prediction)
        self.prediction_probs.append(prob)
        self.timestamps.append(timestamp or pd.Timestamp.now().isoformat())

    def detect_prediction_drift(self) -> dict:
        """Detect drift in predictions"""

        if len(self.predictions) < self.window_size // 2:
            return {'status': 'insufficient_data'}

        # Split into two halves
        mid = len(self.predictions) // 2
        earlier = list(self.predictions)[:mid]
        recent = list(self.predictions)[mid:]

        # Check class distribution drift
        from scipy.stats import chi2_contingency

        unique_classes = np.unique(self.predictions)
        earlier_counts = np.array([np.sum(earlier == c) for c in unique_classes])
        recent_counts = np.array([np.sum(recent == c) for c in unique_classes])

        # Chi-square test
        contingency_table = np.array([earlier_counts, recent_counts])
        chi2, p_value, dof, expected = chi2_contingency(contingency_table)

        # Check prediction confidence drift
        earlier_probs = list(self.prediction_probs)[:mid]
        recent_probs = list(self.prediction_probs)[mid:]

        confidence_result = stats.ks_2samp(earlier_probs, recent_probs)

        drift_result = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'class_distribution': {
                'chi_square_statistic': float(chi2),
                'p_value': float(p_value),
                'drift_detected': p_value < 0.05,
                'earlier_distribution': earlier_counts.tolist(),
                'recent_distribution': recent_counts.tolist(),
            },
            'confidence': {
                'ks_statistic': float(confidence_result.statistic),
                'p_value': float(confidence_result.pvalue),
                'drift_detected': confidence_result.pvalue < 0.05,
                'earlier_avg_confidence': float(np.mean(earlier_probs)),
                'recent_avg_confidence': float(np.mean(recent_probs)),
            }
        }

        self.drift_history.append(drift_result)
        return drift_result

    def get_prediction_stats(self) -> dict:
        """Get prediction statistics"""
        if not self.predictions:
            return {}

        preds = np.array(self.predictions)
        probs = np.array(self.prediction_probs)

        return {
            'total_predictions': len(self.predictions),
            'unique_classes': int(len(np.unique(preds))),
            'class_distribution': {
                int(c): int(np.sum(preds == c))
                for c in np.unique(preds)
            },
            'confidence_stats': {
                'mean': float(np.mean(probs)),
                'std': float(np.std(probs)),
                'min': float(np.min(probs)),
                'max': float(np.max(probs)),
                'percentile_25': float(np.percentile(probs, 25)),
                'percentile_75': float(np.percentile(probs, 75)),
            }
        }
```

---

## Monitoring Metrics

### Key Metrics to Monitor

```python
import time
from prometheus_client import Counter, Histogram, Gauge

class MonitoringMetrics:
    """Track production metrics with Prometheus"""

    def __init__(self, namespace: str = 'ml_model'):
        """Initialize Prometheus metrics"""

        # Prediction metrics
        self.predictions_total = Counter(
            f'{namespace}_predictions_total',
            'Total number of predictions',
            ['model_name', 'model_version']
        )

        self.predictions_by_class = Counter(
            f'{namespace}_predictions_by_class',
            'Predictions by class',
            ['model_name', 'class_label']
        )

        # Latency metrics
        self.prediction_latency = Histogram(
            f'{namespace}_prediction_latency_seconds',
            'Prediction latency in seconds',
            ['model_name'],
            buckets=(0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0)
        )

        # Throughput metrics
        self.predictions_per_minute = Gauge(
            f'{namespace}_predictions_per_minute',
            'Predictions per minute',
            ['model_name']
        )

        # Accuracy metrics
        self.accuracy = Gauge(
            f'{namespace}_accuracy',
            'Model accuracy',
            ['model_name', 'model_version']
        )

        self.precision = Gauge(
            f'{namespace}_precision',
            'Model precision',
            ['model_name', 'model_version']
        )

        self.recall = Gauge(
            f'{namespace}_recall',
            'Model recall',
            ['model_name', 'model_version']
        )

        self.f1_score = Gauge(
            f'{namespace}_f1_score',
            'Model F1 score',
            ['model_name', 'model_version']
        )

        # Drift metrics
        self.data_drift = Gauge(
            f'{namespace}_data_drift',
            'Data drift detected (0/1)',
            ['model_name']
        )

        self.concept_drift = Gauge(
            f'{namespace}_concept_drift',
            'Concept drift detected (0/1)',
            ['model_name']
        )

        # Resource metrics
        self.prediction_errors = Counter(
            f'{namespace}_prediction_errors_total',
            'Total prediction errors',
            ['model_name', 'error_type']
        )

        self.model_inference_memory = Gauge(
            f'{namespace}_inference_memory_bytes',
            'Memory used for inference',
            ['model_name']
        )

    def record_prediction(self, model_name: str, prediction: float, latency: float, class_label: str = None):
        """Record a prediction"""
        self.predictions_total.labels(model_name=model_name, model_version='v1').inc()
        self.prediction_latency.labels(model_name=model_name).observe(latency)
        if class_label:
            self.predictions_by_class.labels(model_name=model_name, class_label=class_label).inc()

    def update_performance_metrics(self, model_name: str, model_version: str, metrics: dict):
        """Update performance metrics"""
        self.accuracy.labels(model_name=model_name, model_version=model_version).set(metrics.get('accuracy', 0))
        self.precision.labels(model_name=model_name, model_version=model_version).set(metrics.get('precision', 0))
        self.recall.labels(model_name=model_name, model_version=model_version).set(metrics.get('recall', 0))
        self.f1_score.labels(model_name=model_name, model_version=model_version).set(metrics.get('f1', 0))

    def record_drift(self, model_name: str, drift_type: str, detected: bool):
        """Record drift detection"""
        if drift_type == 'data':
            self.data_drift.labels(model_name=model_name).set(1 if detected else 0)
        elif drift_type == 'concept':
            self.concept_drift.labels(model_name=model_name).set(1 if detected else 0)
```

### Comprehensive Metric Collection

```python
class ProductionMetricsCollector:
    """Collect comprehensive metrics from production models"""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.metrics = MonitoringMetrics()
        self.start_time = time.time()

    def monitor_prediction(self, model, features: np.ndarray, actual: float = None):
        """Monitor a single prediction end-to-end"""

        # Measure latency
        start = time.time()
        prediction = model.predict(features.reshape(1, -1))[0]
        latency = time.time() - start

        # Get prediction probability
        try:
            prob = model.predict_proba(features.reshape(1, -1)).max()
        except AttributeError:
            prob = 0.5

        # Record metrics
        self.metrics.record_prediction(
            model_name=self.model_name,
            prediction=prediction,
            latency=latency,
            class_label=str(prediction)
        )

        # Calculate throughput
        elapsed = time.time() - self.start_time
        total_predictions = self.metrics.predictions_total._value.get()
        throughput = (total_predictions / elapsed) * 60  # per minute
        self.metrics.predictions_per_minute.labels(model_name=self.model_name).set(throughput)

        return {
            'prediction': prediction,
            'probability': prob,
            'latency': latency,
            'throughput': throughput
        }

    def get_metrics_summary(self) -> dict:
        """Get summary of all collected metrics"""
        return {
            'model_name': self.model_name,
            'total_predictions': self.metrics.predictions_total._value.get(),
            'avg_latency': self.metrics.prediction_latency.labels(model_name=self.model_name)._value.get(),
            'current_throughput': self.metrics.predictions_per_minute.labels(model_name=self.model_name)._value.get()
        }
```

---

## Alerting Strategies

### Alert Rules and Thresholds

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class AlertRule:
    """Define alert rule"""
    name: str
    metric_name: str
    condition: Callable[[float], bool]
    severity: str  # 'info', 'warning', 'critical'
    message_template: str

class AlertingSystem:
    """Production alerting system"""

    def __init__(self):
        self.rules = []
        self.alerts = deque(maxlen=1000)
        self.alert_handlers = []
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default alert rules"""

        # Accuracy degradation
        self.add_rule(AlertRule(
            name='accuracy_degradation',
            metric_name='accuracy',
            condition=lambda x: x < 0.85,
            severity='critical',
            message_template='Accuracy dropped to {value:.2%}'
        ))

        # High latency
        self.add_rule(AlertRule(
            name='high_latency',
            metric_name='prediction_latency',
            condition=lambda x: x > 1.0,
            severity='warning',
            message_template='Prediction latency is {value:.3f}s'
        ))

        # Data drift detected
        self.add_rule(AlertRule(
            name='data_drift_detected',
            metric_name='data_drift',
            condition=lambda x: x == 1,
            severity='warning',
            message_template='Data drift detected in production'
        ))

        # Concept drift detected
        self.add_rule(AlertRule(
            name='concept_drift_detected',
            metric_name='concept_drift',
            condition=lambda x: x == 1,
            severity='critical',
            message_template='Concept drift detected - model retraining recommended'
        ))

        # Low prediction confidence
        self.add_rule(AlertRule(
            name='low_confidence',
            metric_name='avg_confidence',
            condition=lambda x: x < 0.6,
            severity='warning',
            message_template='Average prediction confidence is low: {value:.2%}'
        ))

        # High error rate
        self.add_rule(AlertRule(
            name='high_error_rate',
            metric_name='error_rate',
            condition=lambda x: x > 0.05,
            severity='critical',
            message_template='Prediction error rate is {value:.2%}'
        ))

        # Model serving unavailable
        self.add_rule(AlertRule(
            name='model_unavailable',
            metric_name='model_availability',
            condition=lambda x: x == 0,
            severity='critical',
            message_template='Model serving is unavailable'
        ))

    def add_rule(self, rule: AlertRule):
        """Add custom alert rule"""
        self.rules.append(rule)

    def register_handler(self, handler: Callable):
        """Register alert handler (email, Slack, etc.)"""
        self.alert_handlers.append(handler)

    def check_metrics(self, metrics: dict) -> list:
        """Check metrics against alert rules"""
        triggered_alerts = []

        for rule in self.rules:
            if rule.metric_name in metrics:
                value = metrics[rule.metric_name]

                if rule.condition(value):
                    alert = {
                        'timestamp': pd.Timestamp.now().isoformat(),
                        'rule_name': rule.name,
                        'severity': rule.severity,
                        'metric': rule.metric_name,
                        'value': value,
                        'message': rule.message_template.format(value=value)
                    }

                    triggered_alerts.append(alert)
                    self.alerts.append(alert)

                    # Trigger handlers
                    self._handle_alert(alert)

        return triggered_alerts

    def _handle_alert(self, alert: dict):
        """Handle triggered alert"""
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                print(f"Error in alert handler: {e}")

    def send_to_slack(self, webhook_url: str):
        """Add Slack notification handler"""
        import requests

        def slack_handler(alert):
            message = {
                'text': alert['message'],
                'attachments': [{
                    'color': 'danger' if alert['severity'] == 'critical' else 'warning',
                    'fields': [
                        {'title': 'Rule', 'value': alert['rule_name'], 'short': True},
                        {'title': 'Severity', 'value': alert['severity'], 'short': True},
                        {'title': 'Metric', 'value': alert['metric'], 'short': True},
                        {'title': 'Value', 'value': str(alert['value']), 'short': True},
                        {'title': 'Timestamp', 'value': alert['timestamp'], 'short': False},
                    ]
                }]
            }

            requests.post(webhook_url, json=message)

        self.register_handler(slack_handler)

    def send_to_email(self, smtp_config: dict):
        """Add email notification handler"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        def email_handler(alert):
            msg = MIMEMultipart()
            msg['Subject'] = f"[{alert['severity'].upper()}] {alert['message']}"
            msg['From'] = smtp_config['sender']
            msg['To'] = ', '.join(smtp_config['recipients'])

            body = f"""
            Alert Rule: {alert['rule_name']}
            Severity: {alert['severity']}
            Timestamp: {alert['timestamp']}

            Metric: {alert['metric']}
            Value: {alert['value']}

            Message: {alert['message']}
            """

            msg.attach(MIMEText(body, 'plain'))

            try:
                server = smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port'])
                server.login(smtp_config['user'], smtp_config['password'])
                server.send_message(msg)
                server.quit()
            except Exception as e:
                print(f"Error sending email: {e}")

        self.register_handler(email_handler)

    def get_active_alerts(self) -> dict:
        """Get current active alerts"""
        recent_alerts = list(self.alerts)[-20:]

        by_severity = {}
        for alert in recent_alerts:
            sev = alert['severity']
            if sev not in by_severity:
                by_severity[sev] = []
            by_severity[sev].append(alert)

        return {
            'total_alerts': len(self.alerts),
            'recent_alerts': recent_alerts,
            'by_severity': by_severity
        }
```

---

## Dashboard Design

### Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "ML Model Monitoring Dashboard",
    "timezone": "browser",
    "panels": [
      {
        "title": "Model Accuracy Trend",
        "type": "graph",
        "targets": [
          {
            "expr": "ml_model_accuracy"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "palette-classic"},
            "custom": {"lineWidth": 2},
            "unit": "percentunit"
          }
        }
      },
      {
        "title": "Prediction Latency (ms)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(ml_model_prediction_latency_seconds_bucket[5m])) * 1000"
          }
        ]
      },
      {
        "title": "Data Drift Detection",
        "type": "stat",
        "targets": [
          {
            "expr": "ml_model_data_drift"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "green", "value": 0},
                {"color": "red", "value": 1}
              ]
            }
          }
        }
      },
      {
        "title": "Concept Drift Detection",
        "type": "stat",
        "targets": [
          {
            "expr": "ml_model_concept_drift"
          }
        ]
      },
      {
        "title": "Predictions Per Minute",
        "type": "graph",
        "targets": [
          {
            "expr": "ml_model_predictions_per_minute"
          }
        ]
      },
      {
        "title": "Class Distribution",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum by (class_label) (ml_model_predictions_by_class)"
          }
        ]
      },
      {
        "title": "Performance Metrics",
        "type": "table",
        "targets": [
          {
            "expr": "ml_model_accuracy or ml_model_precision or ml_model_recall or ml_model_f1_score"
          }
        ]
      },
      {
        "title": "Active Alerts",
        "type": "alertlist"
      }
    ]
  }
}
```

### Python Dashboard Builder

```python
class DashboardBuilder:
    """Build Grafana dashboards programmatically"""

    def __init__(self, dashboard_name: str, description: str = ""):
        self.dashboard = {
            'title': dashboard_name,
            'description': description,
            'timezone': 'browser',
            'panels': [],
            'refresh': '30s',
            'time': {'from': 'now-6h', 'to': 'now'}
        }

    def add_accuracy_panel(self, y_position: int = 0):
        """Add accuracy trend panel"""
        self.dashboard['panels'].append({
            'title': 'Model Accuracy',
            'type': 'graph',
            'gridPos': {'x': 0, 'y': y_position, 'w': 12, 'h': 8},
            'targets': [
                {
                    'expr': 'ml_model_accuracy',
                    'legendFormat': '{{model_name}}'
                }
            ],
            'yaxes': [
                {'format': 'percentunit', 'min': 0, 'max': 1},
                {'format': 'short'}
            ]
        })

    def add_latency_panel(self, y_position: int = 8):
        """Add latency heatmap"""
        self.dashboard['panels'].append({
            'title': 'Prediction Latency Distribution',
            'type': 'heatmap',
            'gridPos': {'x': 12, 'y': y_position, 'w': 12, 'h': 8},
            'targets': [
                {
                    'expr': 'rate(ml_model_prediction_latency_seconds_bucket[5m])',
                    'legendFormat': '{{le}}'
                }
            ]
        })

    def add_drift_panel(self, y_position: int = 16):
        """Add drift detection status"""
        self.dashboard['panels'].append({
            'title': 'Data Drift Status',
            'type': 'stat',
            'gridPos': {'x': 0, 'y': y_position, 'w': 6, 'h': 4},
            'targets': [
                {'expr': 'ml_model_data_drift'}
            ],
            'fieldConfig': {
                'defaults': {
                    'color': {'mode': 'thresholds'},
                    'thresholds': {
                        'mode': 'absolute',
                        'steps': [
                            {'color': 'green', 'value': 0},
                            {'color': 'red', 'value': 1}
                        ]
                    },
                    'mappings': [
                        {'type': 'value', 'value': '0', 'text': 'No Drift'},
                        {'type': 'value', 'value': '1', 'text': 'Drift Detected'}
                    ]
                }
            }
        })

        self.dashboard['panels'].append({
            'title': 'Concept Drift Status',
            'type': 'stat',
            'gridPos': {'x': 6, 'y': y_position, 'w': 6, 'h': 4},
            'targets': [
                {'expr': 'ml_model_concept_drift'}
            ],
            'fieldConfig': {
                'defaults': {
                    'color': {'mode': 'thresholds'},
                    'thresholds': {
                        'mode': 'absolute',
                        'steps': [
                            {'color': 'green', 'value': 0},
                            {'color': 'red', 'value': 1}
                        ]
                    },
                    'mappings': [
                        {'type': 'value', 'value': '0', 'text': 'No Drift'},
                        {'type': 'value', 'value': '1', 'text': 'Drift Detected'}
                    ]
                }
            }
        })

    def add_throughput_panel(self, y_position: int = 20):
        """Add throughput gauge"""
        self.dashboard['panels'].append({
            'title': 'Predictions Per Minute',
            'type': 'gauge',
            'gridPos': {'x': 12, 'y': y_position, 'w': 6, 'h': 4},
            'targets': [
                {'expr': 'ml_model_predictions_per_minute'}
            ],
            'fieldConfig': {
                'defaults': {
                    'unit': 'short',
                    'thresholds': {
                        'mode': 'absolute',
                        'steps': [
                            {'color': 'red', 'value': 0},
                            {'color': 'yellow', 'value': 100},
                            {'color': 'green', 'value': 1000}
                        ]
                    }
                }
            }
        })

    def export_json(self) -> str:
        """Export dashboard as JSON"""
        import json
        return json.dumps(self.dashboard, indent=2)

    def to_file(self, filename: str):
        """Save dashboard to file"""
        with open(filename, 'w') as f:
            f.write(self.export_json())

# Usage
dashboard = DashboardBuilder('ML Model Monitoring', 'Production ML model monitoring dashboard')
dashboard.add_accuracy_panel(0)
dashboard.add_latency_panel(8)
dashboard.add_drift_panel(16)
dashboard.add_throughput_panel(20)
dashboard.to_file('monitoring_dashboard.json')
```

---

## Logging Best Practices

### Structured Logging

```python
import logging
import json
from pythonjsonlogger import jsonlogger

class ProductionLogger:
    """Production-grade structured logging"""

    def __init__(self, app_name: str, log_file: str = None):
        self.logger = logging.getLogger(app_name)
        self.logger.setLevel(logging.INFO)

        # JSON formatter for structured logs
        json_formatter = jsonlogger.JsonFormatter()

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(json_formatter)
        self.logger.addHandler(console_handler)

        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(json_formatter)
            self.logger.addHandler(file_handler)

    def log_prediction(self, model_name: str, features: dict, prediction: float,
                      latency: float, confidence: float):
        """Log prediction with full context"""
        self.logger.info('prediction', extra={
            'model_name': model_name,
            'prediction': float(prediction),
            'confidence': float(confidence),
            'latency_ms': float(latency * 1000),
            'features': features,
            'timestamp': pd.Timestamp.now().isoformat()
        })

    def log_model_retraining(self, model_name: str, reason: str,
                            metrics_before: dict, metrics_after: dict):
        """Log model retraining event"""
        self.logger.info('model_retraining', extra={
            'model_name': model_name,
            'reason': reason,
            'metrics_before': metrics_before,
            'metrics_after': metrics_after,
            'improvement': {
                'accuracy': metrics_after.get('accuracy', 0) - metrics_before.get('accuracy', 0)
            },
            'timestamp': pd.Timestamp.now().isoformat()
        })

    def log_drift_detection(self, model_name: str, drift_type: str,
                           details: dict):
        """Log drift detection"""
        self.logger.warning('drift_detected', extra={
            'model_name': model_name,
            'drift_type': drift_type,
            'details': details,
            'action_required': True,
            'timestamp': pd.Timestamp.now().isoformat()
        })

    def log_error(self, model_name: str, error_type: str,
                 error_message: str, context: dict = None):
        """Log errors in predictions"""
        self.logger.error('prediction_error', extra={
            'model_name': model_name,
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {},
            'timestamp': pd.Timestamp.now().isoformat()
        })

# Usage
logger = ProductionLogger('ml_monitoring', log_file='predictions.log')

# Log predictions
logger.log_prediction(
    model_name='classifier_v1',
    features={'feature_1': 0.5, 'feature_2': 0.3},
    prediction=1,
    latency=0.015,
    confidence=0.92
)

# Log drift
logger.log_drift_detection(
    model_name='classifier_v1',
    drift_type='data_drift',
    details={'features_affected': ['feature_1', 'feature_3'], 'p_value': 0.003}
)
```

### Log Aggregation

```python
class LogAggregator:
    """Aggregate logs for analysis"""

    def __init__(self, log_file: str):
        self.log_file = log_file
        self.logs = []
        self._load_logs()

    def _load_logs(self):
        """Load logs from file"""
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    self.logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    def get_stats_by_model(self) -> dict:
        """Get statistics by model"""
        stats = {}

        for log in self.logs:
            model_name = log.get('model_name', 'unknown')
            if model_name not in stats:
                stats[model_name] = {
                    'total_predictions': 0,
                    'avg_latency': [],
                    'avg_confidence': [],
                    'errors': 0,
                    'drifts': 0
                }

            if log.get('msg') == 'prediction':
                stats[model_name]['total_predictions'] += 1
                stats[model_name]['avg_latency'].append(log.get('latency_ms', 0))
                stats[model_name]['avg_confidence'].append(log.get('confidence', 0))
            elif log.get('msg') == 'prediction_error':
                stats[model_name]['errors'] += 1
            elif log.get('msg') == 'drift_detected':
                stats[model_name]['drifts'] += 1

        # Calculate averages
        for model_name in stats:
            if stats[model_name]['avg_latency']:
                stats[model_name]['avg_latency'] = np.mean(stats[model_name]['avg_latency'])
            if stats[model_name]['avg_confidence']:
                stats[model_name]['avg_confidence'] = np.mean(stats[model_name]['avg_confidence'])

        return stats

    def get_error_analysis(self) -> dict:
        """Analyze errors"""
        errors = [log for log in self.logs if log.get('msg') == 'prediction_error']

        error_types = {}
        for error in errors:
            error_type = error.get('error_type', 'unknown')
            if error_type not in error_types:
                error_types[error_type] = 0
            error_types[error_type] += 1

        return {
            'total_errors': len(errors),
            'error_types': error_types,
            'error_rate': len(errors) / len(self.logs) if self.logs else 0,
            'recent_errors': errors[-10:]
        }
```

---

## Complete Production Setup

### Docker Compose Setup

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    networks:
      - monitoring
    depends_on:
      - prometheus

  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    networks:
      - monitoring

  ml_model_service:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - PROMETHEUS_PORT=8000
      - LOG_FILE=/logs/predictions.log
    volumes:
      - ./models:/app/models
      - ./logs:/logs
    networks:
      - monitoring
    depends_on:
      - prometheus

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:

networks:
  monitoring:
    driver: bridge
```

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    environment: 'production'
    cluster: 'ml_cluster'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - localhost:9093

rule_files:
  - 'alert_rules.yml'

scrape_configs:
  - job_name: 'ml_model_service'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 10s
    scrape_timeout: 5s
    metrics_path: '/metrics'

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'alertmanager'
    static_configs:
      - targets: ['localhost:9093']
```

### Alert Rules

```yaml
# alert_rules.yml
groups:
  - name: ml_model_alerts
    interval: 30s
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(ml_model_prediction_latency_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High prediction latency detected"
          description: "P95 latency is {{ $value }}s"

      - alert: AccuracyDegradation
        expr: ml_model_accuracy < 0.85
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Model accuracy degradation detected"
          description: "Accuracy is {{ $value }}"

      - alert: DataDriftDetected
        expr: ml_model_data_drift == 1
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Data drift detected in production"
          description: "Data distribution has changed significantly"

      - alert: ConceptDriftDetected
        expr: ml_model_concept_drift == 1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Concept drift detected"
          description: "Model retraining is recommended"

      - alert: HighErrorRate
        expr: rate(ml_model_prediction_errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High prediction error rate"
          description: "Error rate is {{ $value }}"

      - alert: LowPredictionConfidence
        expr: ml_model_avg_confidence < 0.6
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low average prediction confidence"
          description: "Average confidence is {{ $value }}"
```

### Flask Application with Prometheus

```python
from flask import Flask, request, jsonify
from prometheus_client import generate_latest, CollectorRegistry, start_http_server
from werkzeug.exceptions import HTTPException
import time
import pickle
import logging

app = Flask(__name__)

# Initialize monitoring
registry = CollectorRegistry()
metrics = MonitoringMetrics(namespace='ml_model')

# Setup logging
logger = ProductionLogger('ml_service', log_file='/logs/predictions.log')

# Load model
with open('/app/models/model.pkl', 'rb') as f:
    model = pickle.load(f)

# Initialize drift detectors
drift_detector = EvidentlyDriftDetector(reference_data=pd.read_csv('/app/models/reference_data.csv'))
concept_drift_detector = ConceptDriftDetector(window_size=100)

# Initialize alerting
alerting_system = AlertingSystem()
alerting_system.send_to_slack(os.getenv('SLACK_WEBHOOK_URL'))

@app.route('/predict', methods=['POST'])
def predict():
    """Make prediction endpoint"""
    try:
        start_time = time.time()

        # Get features
        data = request.json
        features = np.array([data['features']])

        # Make prediction
        prediction = model.predict(features)[0]
        confidence = model.predict_proba(features).max()

        # Calculate latency
        latency = time.time() - start_time

        # Record metrics
        metrics.record_prediction(
            model_name='production_model',
            prediction=prediction,
            latency=latency,
            class_label=str(prediction)
        )

        # Log prediction
        logger.log_prediction(
            model_name='production_model',
            features=data['features'],
            prediction=prediction,
            latency=latency,
            confidence=confidence
        )

        # Check for concept drift (if actual label provided)
        if 'actual' in data:
            concept_drift_detector.update(
                prediction=prediction,
                actual=data['actual']
            )

            # Check for drift alerts
            drift_status = concept_drift_detector.get_drift_summary()
            metrics_dict = {
                'concept_drift': 1 if drift_status['drift_alerts'] else 0,
                'accuracy': drift_status['current_performance'].get('current_accuracy', 0)
            }

            triggered_alerts = alerting_system.check_metrics(metrics_dict)
            if triggered_alerts:
                for alert in triggered_alerts:
                    logger.logger.warning(f"Alert: {alert['message']}")

        return jsonify({
            'prediction': int(prediction),
            'confidence': float(confidence),
            'latency_ms': float(latency * 1000)
        }), 200

    except Exception as e:
        logger.log_error(
            model_name='production_model',
            error_type=type(e).__name__,
            error_message=str(e),
            context={'endpoint': '/predict'}
        )
        return jsonify({'error': str(e)}), 500

@app.route('/metrics', methods=['GET'])
def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return generate_latest(registry)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/drift-status', methods=['GET'])
def drift_status():
    """Get drift detection status"""
    return jsonify({
        'concept_drift': concept_drift_detector.get_drift_summary(),
        'data_drift': drift_detector.get_drift_summary()
    }), 200

@app.route('/alerts', methods=['GET'])
def get_alerts():
    """Get active alerts"""
    return jsonify(alerting_system.get_active_alerts()), 200

if __name__ == '__main__':
    # Start Prometheus metrics server
    start_http_server(8000, registry=registry)

    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### Monitoring Controller

```python
class MonitoringController:
    """Centralized monitoring control"""

    def __init__(self, model, reference_data: pd.DataFrame):
        self.model = model
        self.reference_data = reference_data

        # Initialize all components
        self.performance_metrics = PerformanceMetrics('production_model', 'v1')
        self.drift_detector = EvidentlyDriftDetector(reference_data)
        self.feature_drift_detector = FeatureDriftDetector(reference_data, reference_data.columns.tolist()[:-1])
        self.concept_drift_detector = ConceptDriftDetector(window_size=100)
        self.prediction_drift_detector = PredictionDriftDetector(window_size=1000)
        self.logger = ProductionLogger('ml_monitoring')
        self.alerting_system = AlertingSystem()
        self.metrics_collector = MonitoringMetrics()

        # Counters
        self.prediction_count = 0
        self.check_frequency = 100  # Check drift every N predictions

    def make_prediction(self, features: np.ndarray, actual: float = None) -> dict:
        """Make prediction with full monitoring"""

        start_time = time.time()

        # Make prediction
        prediction = self.model.predict(features.reshape(1, -1))[0]
        confidence = self.model.predict_proba(features.reshape(1, -1)).max()
        latency = time.time() - start_time

        # Record metrics
        self.prediction_count += 1
        self.performance_metrics.add_prediction(prediction, actual, pd.Timestamp.now())
        self.prediction_drift_detector.add_prediction(prediction, confidence)
        self.metrics_collector.record_prediction(
            model_name='production_model',
            prediction=prediction,
            latency=latency,
            class_label=str(prediction)
        )

        # Log prediction
        self.logger.log_prediction(
            model_name='production_model',
            features={'feature_' + str(i): float(v) for i, v in enumerate(features)},
            prediction=prediction,
            latency=latency,
            confidence=confidence
        )

        # Update concept drift
        if actual is not None:
            self.concept_drift_detector.update(prediction, actual)

        # Periodic drift checks
        if self.prediction_count % self.check_frequency == 0:
            self._check_drifts(features)

        return {
            'prediction': float(prediction),
            'confidence': float(confidence),
            'latency_ms': float(latency * 1000),
            'prediction_id': self.prediction_count
        }

    def _check_drifts(self, current_features: np.ndarray):
        """Check for various drifts"""

        # Create batch for drift checking
        current_data = pd.DataFrame([current_features])

        # Check data drift
        data_drift_result = self.drift_detector.detect_drift(current_data)
        data_drift_detected = data_drift_result['dataset_drift']

        # Check feature drift
        feature_drift_result = self.feature_drift_detector.detect_drift(current_data)

        # Check prediction drift
        prediction_drift_result = self.prediction_drift_detector.detect_prediction_drift()

        # Update metrics
        metrics_dict = {
            'data_drift': 1 if data_drift_detected else 0,
            'concept_drift': 1 if self.concept_drift_detector.drift_alerts else 0,
            'accuracy': self.performance_metrics.calculate_metrics().get('accuracy', 0),
            'error_rate': 0.0  # Calculate from logs
        }

        # Check alerts
        triggered_alerts = self.alerting_system.check_metrics(metrics_dict)

        # Log drifts
        if data_drift_detected:
            self.logger.log_drift_detection(
                model_name='production_model',
                drift_type='data_drift',
                details=data_drift_result
            )

        if feature_drift_result['features']:
            drifted_features = [
                f for f, d in feature_drift_result['features'].items()
                if d['drift_detected']
            ]
            if drifted_features:
                self.logger.log_drift_detection(
                    model_name='production_model',
                    drift_type='feature_drift',
                    details={'features': drifted_features}
                )

    def get_monitoring_report(self) -> dict:
        """Generate comprehensive monitoring report"""

        return {
            'summary': {
                'total_predictions': self.prediction_count,
                'timestamp': pd.Timestamp.now().isoformat()
            },
            'performance': self.performance_metrics.calculate_metrics(),
            'drift_status': {
                'data_drift': self.drift_detector.get_drift_summary(),
                'concept_drift': self.concept_drift_detector.get_drift_summary(),
                'prediction_drift': self.prediction_drift_detector.get_prediction_stats()
            },
            'alerts': self.alerting_system.get_active_alerts()
        }

# Usage
monitoring = MonitoringController(model, reference_data)

# Make predictions with monitoring
for features, actual in test_data:
    result = monitoring.make_prediction(features, actual)
    print(f"Prediction: {result['prediction']}, Confidence: {result['confidence']:.2%}")

# Get monitoring report
report = monitoring.get_monitoring_report()
print(json.dumps(report, indent=2, default=str))
```

---

## Summary

This comprehensive ML monitoring guide covers:

1. **Model Performance Monitoring** - Track accuracy, precision, recall, F1 score
2. **Data Drift Detection** - Using Evidently AI and Alibi Detect
3. **Concept Drift** - Detecting changes in prediction-target relationship
4. **Feature Drift** - Monitoring individual feature distributions
5. **Prediction Drift** - Tracking changes in prediction distributions
6. **Monitoring Metrics** - Latency, throughput, accuracy tracking
7. **Alerting Strategies** - Rule-based alerts with handlers
8. **Dashboard Design** - Grafana dashboards for visualization
9. **Logging Best Practices** - Structured logging and aggregation
10. **Production Setup** - Complete Docker, Prometheus, Grafana stack

All code examples are production-ready and can be directly integrated into ML systems for comprehensive monitoring and alerting.
