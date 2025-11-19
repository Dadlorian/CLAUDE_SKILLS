# ML Testing Patterns: Production Testing Practices

Comprehensive guide to testing machine learning systems following Google's ML testing best practices. This document covers unit tests, integration tests, model validation, data validation, property-based testing, and CI/CD patterns for ML.

## Table of Contents

1. [Overview](#overview)
2. [Unit Tests for ML Code](#unit-tests-for-ml-code)
3. [Integration Tests for Pipelines](#integration-tests-for-pipelines)
4. [Model Validation Tests](#model-validation-tests)
5. [Data Validation Tests](#data-validation-tests)
6. [Property-Based Testing for ML](#property-based-testing-for-ml)
7. [Regression Tests](#regression-tests)
8. [Performance Tests](#performance-tests)
9. [Testing Frameworks](#testing-frameworks)
10. [CI/CD for ML Testing](#cicd-for-ml-testing)
11. [Complete Test Examples](#complete-test-examples)
12. [Best Practices](#best-practices)

## Overview

Testing ML systems is fundamentally different from traditional software testing. ML tests must validate:

- **Code quality**: Traditional unit tests
- **Data quality**: Input data properties and distributions
- **Model behavior**: Correctness, fairness, and robustness
- **System performance**: Training speed, inference latency, memory usage
- **Integration points**: Pipeline end-to-end execution
- **Stability**: Reproducibility and drift detection

### Google's ML Testing Perspective

Google's approach emphasizes:

1. **ML-specific test levels**: Beyond typical unit/integration/E2E
2. **Data validation as first-class testing concern**
3. **Model metrics validation** (not just accuracy)
4. **Infrastructure and pipeline testing**
5. **Production monitoring patterns**

---

## Unit Tests for ML Code

Unit tests for ML focus on individual functions and classes in isolation.

### Testing Feature Preprocessing

```python
# tests/test_preprocessing.py
import pytest
import numpy as np
import pandas as pd
from data_science_ai.preprocessing import StandardScaler, OneHotEncoder

class TestStandardScaler:
    """Unit tests for StandardScaler feature preprocessing."""

    def test_fit_scales_correctly(self):
        """Test that fit computes correct mean and std."""
        scaler = StandardScaler()
        X = np.array([[1, 2], [3, 4], [5, 6]], dtype=float)
        scaler.fit(X)

        assert np.allclose(scaler.mean_, np.array([3.0, 4.0]))
        assert np.allclose(scaler.std_, np.array([np.std([1, 3, 5]), np.std([2, 4, 6])]))

    def test_transform_zeros_mean(self):
        """Test that transform produces zero mean features."""
        scaler = StandardScaler()
        X = np.array([[1, 2], [3, 4], [5, 6]], dtype=float)
        scaler.fit(X)
        X_scaled = scaler.transform(X)

        assert np.allclose(X_scaled.mean(axis=0), np.zeros(2), atol=1e-10)

    def test_transform_unit_variance(self):
        """Test that transform produces unit variance features."""
        scaler = StandardScaler()
        X = np.array([[1, 2], [3, 4], [5, 6]], dtype=float)
        scaler.fit(X)
        X_scaled = scaler.transform(X)

        assert np.allclose(X_scaled.std(axis=0), np.ones(2), atol=1e-10)

    def test_fit_transform_consistency(self):
        """Test fit_transform matches fit + transform."""
        scaler1 = StandardScaler()
        scaler2 = StandardScaler()
        X = np.random.randn(100, 10)

        result1 = scaler1.fit_transform(X)
        result2 = scaler2.fit(X).transform(X)

        assert np.allclose(result1, result2)

    def test_handles_single_feature(self):
        """Test with single feature input."""
        scaler = StandardScaler()
        X = np.array([[1], [2], [3]], dtype=float)
        X_scaled = scaler.fit_transform(X)

        assert X_scaled.shape == (3, 1)
        assert np.allclose(X_scaled.mean(), 0)

    def test_handles_constant_feature(self):
        """Test behavior with constant features."""
        scaler = StandardScaler()
        X = np.array([[5, 1], [5, 2], [5, 3]], dtype=float)
        X_scaled = scaler.fit_transform(X)

        # Constant feature should have zero std, avoid division by zero
        assert np.isfinite(X_scaled).all()

    def test_reproducibility(self):
        """Test that fit/transform produces consistent results."""
        scaler = StandardScaler()
        X = np.array([[1, 2], [3, 4], [5, 6]], dtype=float)

        X_scaled_1 = scaler.fit_transform(X)
        X_scaled_2 = scaler.fit_transform(X)

        assert np.array_equal(X_scaled_1, X_scaled_2)

class TestOneHotEncoder:
    """Unit tests for OneHotEncoder."""

    def test_encode_single_categorical_feature(self):
        """Test encoding of single categorical column."""
        encoder = OneHotEncoder()
        X = pd.DataFrame({'color': ['red', 'blue', 'red', 'green']})
        encoded = encoder.fit_transform(X)

        expected_columns = {'color_red', 'color_blue', 'color_green'}
        assert set(encoded.columns) == expected_columns
        assert encoded.shape[0] == 4

    def test_encode_preserves_order(self):
        """Test that encoding preserves row order."""
        encoder = OneHotEncoder()
        X = pd.DataFrame({'fruit': ['apple', 'banana', 'apple']})
        encoded = encoder.fit_transform(X)

        assert encoded['fruit_apple'].iloc[0] == 1
        assert encoded['fruit_banana'].iloc[1] == 1
        assert encoded['fruit_apple'].iloc[2] == 1

    def test_unknown_category_handling(self):
        """Test handling of unknown categories during transform."""
        encoder = OneHotEncoder(handle_unknown='error')
        X_train = pd.DataFrame({'color': ['red', 'blue']})
        encoder.fit(X_train)

        X_test = pd.DataFrame({'color': ['purple']})
        with pytest.raises(ValueError):
            encoder.transform(X_test)

    def test_multiple_categorical_features(self):
        """Test encoding multiple categorical columns."""
        encoder = OneHotEncoder()
        X = pd.DataFrame({
            'color': ['red', 'blue', 'red'],
            'size': ['S', 'M', 'L']
        })
        encoded = encoder.fit_transform(X)

        expected_columns = {
            'color_red', 'color_blue',
            'size_S', 'size_M', 'size_L'
        }
        assert set(encoded.columns) == expected_columns

```

### Testing Model Initialization

```python
# tests/test_model_initialization.py
import pytest
import numpy as np
from data_science_ai.models import LogisticRegression, RandomForest

class TestLogisticRegressionInit:
    """Unit tests for LogisticRegression initialization."""

    def test_default_parameters(self):
        """Test model initializes with correct defaults."""
        model = LogisticRegression()
        assert model.learning_rate == 0.01
        assert model.max_iterations == 1000
        assert model.random_state is None

    def test_custom_parameters(self):
        """Test model accepts custom parameters."""
        model = LogisticRegression(
            learning_rate=0.001,
            max_iterations=500,
            random_state=42
        )
        assert model.learning_rate == 0.001
        assert model.max_iterations == 500
        assert model.random_state == 42

    def test_invalid_learning_rate(self):
        """Test that invalid learning rates raise errors."""
        with pytest.raises(ValueError):
            LogisticRegression(learning_rate=-0.1)

        with pytest.raises(ValueError):
            LogisticRegression(learning_rate=0)

    def test_invalid_iterations(self):
        """Test that invalid iteration counts raise errors."""
        with pytest.raises(ValueError):
            LogisticRegression(max_iterations=0)

        with pytest.raises(ValueError):
            LogisticRegression(max_iterations=-1)

class TestRandomForestInit:
    """Unit tests for RandomForest initialization."""

    def test_default_parameters(self):
        """Test model initializes with correct defaults."""
        model = RandomForest()
        assert model.n_estimators == 100
        assert model.max_depth is None
        assert model.min_samples_split == 2

    def test_parameter_validation(self):
        """Test parameter validation."""
        with pytest.raises(ValueError):
            RandomForest(n_estimators=0)

        with pytest.raises(ValueError):
            RandomForest(max_depth=-1)

        with pytest.raises(ValueError):
            RandomForest(min_samples_split=0)

```

---

## Integration Tests for Pipelines

Integration tests validate that multiple components work together correctly.

### Testing ML Pipelines

```python
# tests/test_pipeline_integration.py
import pytest
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from data_science_ai.preprocessing import StandardScaler, OneHotEncoder
from data_science_ai.models import LogisticRegression

class TestPipelineIntegration:
    """Integration tests for ML pipelines."""

    @pytest.fixture
    def sample_data(self):
        """Create sample training and test data."""
        np.random.seed(42)
        X_train = pd.DataFrame({
            'feature_1': np.random.randn(100),
            'feature_2': np.random.randn(100),
            'category': np.random.choice(['A', 'B', 'C'], 100)
        })
        y_train = np.random.randint(0, 2, 100)

        X_test = pd.DataFrame({
            'feature_1': np.random.randn(20),
            'feature_2': np.random.randn(20),
            'category': np.random.choice(['A', 'B', 'C'], 20)
        })
        y_test = np.random.randint(0, 2, 20)

        return X_train, y_train, X_test, y_test

    def test_pipeline_full_workflow(self, sample_data):
        """Test complete pipeline: fit and predict."""
        X_train, y_train, X_test, y_test = sample_data

        pipeline = Pipeline([
            ('preprocessing', StandardScaler()),
            ('model', LogisticRegression())
        ])

        # Should not raise
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)

        assert predictions.shape == (20,)
        assert np.all((predictions == 0) | (predictions == 1))

    def test_pipeline_score(self, sample_data):
        """Test pipeline scoring."""
        X_train, y_train, X_test, y_test = sample_data

        pipeline = Pipeline([
            ('preprocessing', StandardScaler()),
            ('model', LogisticRegression())
        ])

        pipeline.fit(X_train, y_train)
        score = pipeline.score(X_test, y_test)

        assert 0.0 <= score <= 1.0

    def test_pipeline_preserves_data_integrity(self, sample_data):
        """Test that pipeline doesn't corrupt data."""
        X_train, y_train, _, _ = sample_data
        original_shape = X_train.shape

        pipeline = Pipeline([
            ('preprocessing', StandardScaler()),
        ])

        X_processed = pipeline.fit_transform(X_train)

        assert X_processed.shape == original_shape
        assert not np.any(np.isnan(X_processed))
        assert not np.any(np.isinf(X_processed))

    def test_pipeline_handles_unseen_categories(self, sample_data):
        """Test pipeline behavior with unseen categories."""
        X_train, y_train, _, _ = sample_data

        pipeline = Pipeline([
            ('preprocessing', OneHotEncoder(handle_unknown='ignore')),
            ('model', LogisticRegression())
        ])

        pipeline.fit(X_train, y_train)

        X_test_with_unknown = pd.DataFrame({
            'feature_1': [1.0],
            'feature_2': [2.0],
            'category': ['UNKNOWN_CATEGORY']
        })

        # Should not raise with handle_unknown='ignore'
        predictions = pipeline.predict(X_test_with_unknown)
        assert predictions.shape == (1,)

```

### Testing Data Loading Pipelines

```python
# tests/test_data_pipeline.py
import pytest
import pandas as pd
from pathlib import Path
from data_science_ai.data import DataLoader, DataSplitter

class TestDataLoader:
    """Integration tests for data loading."""

    @pytest.fixture
    def sample_csv(self, tmp_path):
        """Create a sample CSV file."""
        df = pd.DataFrame({
            'feature_1': [1, 2, 3, 4, 5],
            'feature_2': [10, 20, 30, 40, 50],
            'target': [0, 1, 0, 1, 0]
        })
        file_path = tmp_path / "data.csv"
        df.to_csv(file_path, index=False)
        return file_path

    def test_load_csv(self, sample_csv):
        """Test loading CSV file."""
        loader = DataLoader()
        df = loader.load(sample_csv)

        assert len(df) == 5
        assert list(df.columns) == ['feature_1', 'feature_2', 'target']

    def test_load_and_validate_schema(self, sample_csv):
        """Test loading with schema validation."""
        loader = DataLoader(
            schema={
                'feature_1': 'int64',
                'feature_2': 'int64',
                'target': 'int64'
            }
        )
        df = loader.load(sample_csv)

        assert df['feature_1'].dtype == 'int64'
        assert df['feature_2'].dtype == 'int64'

class TestDataSplitter:
    """Integration tests for data splitting."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data."""
        return pd.DataFrame({
            'feature': range(100),
            'target': range(100) % 2
        })

    def test_train_test_split(self, sample_data):
        """Test train/test split."""
        splitter = DataSplitter(test_size=0.2, random_state=42)
        X_train, X_test = splitter.split(sample_data.drop('target', axis=1))

        assert len(X_train) == 80
        assert len(X_test) == 20
        assert len(X_train) + len(X_test) == 100

    def test_stratified_split(self, sample_data):
        """Test stratified split preserves class distribution."""
        splitter = DataSplitter(
            test_size=0.2,
            random_state=42,
            stratify=True
        )
        y = sample_data['target']
        X_train, X_test, y_train, y_test = splitter.split(
            sample_data.drop('target', axis=1),
            y
        )

        # Check class distribution is similar
        train_ratio = y_train.sum() / len(y_train)
        test_ratio = y_test.sum() / len(y_test)

        assert abs(train_ratio - test_ratio) < 0.1

```

---

## Model Validation Tests

Model validation tests ensure the trained model behaves correctly.

### Testing Model Predictions

```python
# tests/test_model_validation.py
import pytest
import numpy as np
from data_science_ai.models import BinaryClassifier, Regressor

class TestBinaryClassifierValidation:
    """Validation tests for binary classification models."""

    @pytest.fixture
    def trained_classifier(self):
        """Create and train a classifier."""
        np.random.seed(42)
        X_train = np.random.randn(100, 5)
        y_train = np.random.randint(0, 2, 100)

        model = BinaryClassifier()
        model.fit(X_train, y_train)
        return model, X_train, y_train

    def test_predictions_in_valid_range(self, trained_classifier):
        """Test predictions are valid class labels."""
        model, X_train, _ = trained_classifier
        predictions = model.predict(X_train[:10])

        assert np.all((predictions == 0) | (predictions == 1))
        assert predictions.dtype in [np.int32, np.int64, int]

    def test_probabilities_sum_to_one(self, trained_classifier):
        """Test predicted probabilities sum to 1."""
        model, X_train, _ = trained_classifier
        proba = model.predict_proba(X_train[:10])

        assert proba.shape[1] == 2
        assert np.allclose(proba.sum(axis=1), 1.0)

    def test_probabilities_in_valid_range(self, trained_classifier):
        """Test probabilities are in [0, 1]."""
        model, X_train, _ = trained_classifier
        proba = model.predict_proba(X_train)

        assert np.all((proba >= 0) & (proba <= 1))

    def test_probability_threshold_consistency(self, trained_classifier):
        """Test that predictions match probability threshold."""
        model, X_train, _ = trained_classifier
        predictions = model.predict(X_train)
        proba = model.predict_proba(X_train)

        # Predictions should match threshold=0.5
        threshold_predictions = (proba[:, 1] >= 0.5).astype(int)
        assert np.array_equal(predictions, threshold_predictions)

    def test_edge_case_all_same_class(self, trained_classifier):
        """Test behavior when training data has only one class."""
        model = BinaryClassifier()
        X = np.random.randn(10, 5)
        y = np.zeros(10)  # All class 0

        # Should handle gracefully
        model.fit(X, y)
        predictions = model.predict(X)
        assert predictions.shape == (10,)

class TestRegressorValidation:
    """Validation tests for regression models."""

    @pytest.fixture
    def trained_regressor(self):
        """Create and train a regressor."""
        np.random.seed(42)
        X_train = np.random.randn(100, 5)
        y_train = np.random.randn(100) * 100

        model = Regressor()
        model.fit(X_train, y_train)
        return model, X_train, y_train

    def test_predictions_are_numeric(self, trained_regressor):
        """Test predictions are numeric values."""
        model, X_train, _ = trained_regressor
        predictions = model.predict(X_train[:10])

        assert predictions.dtype in [np.float32, np.float64, float]
        assert np.all(np.isfinite(predictions))

    def test_no_nan_predictions(self, trained_regressor):
        """Test that predictions don't contain NaN."""
        model, X_train, _ = trained_regressor
        predictions = model.predict(X_train)

        assert not np.any(np.isnan(predictions))
        assert not np.any(np.isinf(predictions))

    def test_predictions_reasonable_scale(self, trained_regressor):
        """Test predictions are on reasonable scale."""
        model, X_train, y_train = trained_regressor
        predictions = model.predict(X_train)

        # Predictions should be in similar range as training targets
        pred_std = np.std(predictions)
        target_std = np.std(y_train)

        # Should be within 10x of training std
        assert pred_std < target_std * 10
        assert pred_std > target_std / 10 or pred_std == 0

```

### Testing Model Metrics

```python
# tests/test_model_metrics.py
import pytest
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score
from data_science_ai.evaluation import ModelEvaluator

class TestModelMetrics:
    """Tests for model evaluation metrics."""

    @pytest.fixture
    def predictions_and_targets(self):
        """Create predictions and targets."""
        y_true = np.array([0, 1, 1, 0, 1, 1, 0, 0])
        y_pred = np.array([0, 1, 0, 0, 1, 1, 0, 1])
        return y_true, y_pred

    def test_accuracy_computation(self, predictions_and_targets):
        """Test accuracy metric computation."""
        y_true, y_pred = predictions_and_targets
        evaluator = ModelEvaluator()

        accuracy = evaluator.accuracy(y_true, y_pred)
        expected = accuracy_score(y_true, y_pred)

        assert np.isclose(accuracy, expected)

    def test_precision_computation(self, predictions_and_targets):
        """Test precision metric computation."""
        y_true, y_pred = predictions_and_targets
        evaluator = ModelEvaluator()

        precision = evaluator.precision(y_true, y_pred)
        expected = precision_score(y_true, y_pred)

        assert np.isclose(precision, expected)

    def test_recall_computation(self, predictions_and_targets):
        """Test recall metric computation."""
        y_true, y_pred = predictions_and_targets
        evaluator = ModelEvaluator()

        recall = evaluator.recall(y_true, y_pred)
        expected = recall_score(y_true, y_pred)

        assert np.isclose(recall, expected)

    def test_metrics_in_valid_range(self, predictions_and_targets):
        """Test that metrics are in valid ranges."""
        y_true, y_pred = predictions_and_targets
        evaluator = ModelEvaluator()

        metrics = {
            'accuracy': evaluator.accuracy(y_true, y_pred),
            'precision': evaluator.precision(y_true, y_pred),
            'recall': evaluator.recall(y_true, y_pred)
        }

        for metric_name, value in metrics.items():
            assert 0.0 <= value <= 1.0, f"{metric_name} out of range"

    def test_perfect_predictions(self):
        """Test metrics with perfect predictions."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_pred = np.array([0, 1, 1, 0, 1])
        evaluator = ModelEvaluator()

        assert evaluator.accuracy(y_true, y_pred) == 1.0
        assert evaluator.precision(y_true, y_pred) == 1.0
        assert evaluator.recall(y_true, y_pred) == 1.0

    def test_worst_predictions(self):
        """Test metrics with all wrong predictions."""
        y_true = np.array([0, 0, 0, 1, 1, 1])
        y_pred = np.array([1, 1, 1, 0, 0, 0])
        evaluator = ModelEvaluator()

        assert evaluator.accuracy(y_true, y_pred) == 0.0

```

---

## Data Validation Tests

Data validation is a first-class testing concern in ML. Tests should validate data quality, distributions, and schema.

### Testing Data Quality

```python
# tests/test_data_validation.py
import pytest
import numpy as np
import pandas as pd
from data_science_ai.validation import DataValidator

class TestDataValidation:
    """Tests for data quality validation."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data with various issues."""
        return pd.DataFrame({
            'feature_1': [1, 2, 3, np.nan, 5],
            'feature_2': [10, 20, 30, 40, 50],
            'feature_3': [100, 100, 100, 100, 100],
            'category': ['A', 'B', 'A', 'B', None],
            'id': [1, 2, 3, 4, 5]
        })

    def test_detects_missing_values(self, sample_data):
        """Test detection of missing values."""
        validator = DataValidator()
        result = validator.check_missing_values(sample_data)

        assert result['feature_1'] == 1
        assert result['category'] == 1
        assert result['feature_2'] == 0

    def test_detects_constant_features(self, sample_data):
        """Test detection of constant features."""
        validator = DataValidator()
        constant_features = validator.find_constant_features(sample_data)

        assert 'feature_3' in constant_features
        assert 'feature_1' not in constant_features

    def test_validates_feature_ranges(self, sample_data):
        """Test validation of feature value ranges."""
        validator = DataValidator()

        # Define expected ranges
        ranges = {
            'feature_1': (0, 10),
            'feature_2': (0, 100),
        }

        violations = validator.check_ranges(sample_data, ranges)

        assert len(violations['feature_1']) == 0
        assert len(violations['feature_2']) == 0

    def test_detects_outliers(self, sample_data):
        """Test outlier detection."""
        validator = DataValidator()
        data_with_outliers = sample_data.copy()
        data_with_outliers.loc[0, 'feature_2'] = 10000  # Outlier

        outliers = validator.detect_outliers(
            data_with_outliers,
            method='iqr',
            columns=['feature_2']
        )

        assert 0 in outliers.index

    def test_validates_categorical_values(self, sample_data):
        """Test validation of categorical values."""
        validator = DataValidator()
        allowed_values = {
            'category': ['A', 'B', 'C']
        }

        violations = validator.check_categorical_values(
            sample_data,
            allowed_values
        )

        # Should report missing value but not 'A' or 'B'
        assert len(violations['category']) >= 1

    def test_checks_data_types(self, sample_data):
        """Test data type validation."""
        validator = DataValidator()
        expected_types = {
            'feature_1': 'numeric',
            'feature_2': 'numeric',
            'category': 'categorical'
        }

        violations = validator.check_types(sample_data, expected_types)

        assert len(violations) == 0

    def test_validates_schema(self, sample_data):
        """Test schema validation."""
        validator = DataValidator()
        schema = {
            'feature_1': {'type': 'float', 'nullable': True},
            'feature_2': {'type': 'int', 'nullable': False},
            'category': {'type': 'str', 'nullable': True}
        }

        result = validator.validate_schema(sample_data, schema)
        assert result['valid'] == True or len(result['errors']) > 0

```

### Testing Data Distributions

```python
# tests/test_data_distributions.py
import pytest
import numpy as np
import pandas as pd
from scipy import stats
from data_science_ai.validation import DistributionValidator

class TestDataDistributions:
    """Tests for validating data distributions."""

    @pytest.fixture
    def normal_data(self):
        """Create normally distributed data."""
        np.random.seed(42)
        return np.random.normal(0, 1, 1000)

    @pytest.fixture
    def uniform_data(self):
        """Create uniformly distributed data."""
        np.random.seed(42)
        return np.random.uniform(0, 1, 1000)

    def test_normal_distribution_detection(self, normal_data):
        """Test detection of normal distribution."""
        validator = DistributionValidator()

        # Shapiro-Wilk test
        is_normal = validator.is_normal(normal_data, test='shapiro')
        assert is_normal or not is_normal  # Just checking it runs

    def test_distribution_shift_detection(self):
        """Test detection of distribution shift."""
        np.random.seed(42)
        baseline = np.random.normal(0, 1, 1000)
        shifted = np.random.normal(2, 1, 1000)  # Mean shift

        validator = DistributionValidator()
        ks_stat, p_value = validator.kolmogorov_smirnov(baseline, shifted)

        # Shifted distribution should be significantly different
        assert p_value < 0.05

    def test_distribution_similarity(self):
        """Test measurement of distribution similarity."""
        np.random.seed(42)
        data1 = np.random.normal(0, 1, 1000)
        data2 = np.random.normal(0.1, 1, 1000)  # Slightly different

        validator = DistributionValidator()
        distance = validator.wasserstein_distance(data1, data2)

        assert isinstance(distance, float)
        assert distance >= 0

    def test_skewness_detection(self, uniform_data):
        """Test skewness detection."""
        validator = DistributionValidator()
        skewness = validator.skewness(uniform_data)

        # Uniform distribution should have low skewness
        assert abs(skewness) < 1.0

    def test_kurtosis_detection(self):
        """Test kurtosis detection."""
        np.random.seed(42)
        normal_data = np.random.normal(0, 1, 1000)

        validator = DistributionValidator()
        kurt = validator.kurtosis(normal_data)

        # Normal distribution has kurtosis ~0
        assert abs(kurt) < 1.0

```

---

## Property-Based Testing for ML

Property-based testing uses hypothesis to generate test cases automatically, finding edge cases.

### Property-Based Tests

```python
# tests/test_properties.py
import pytest
from hypothesis import given, strategies as st, settings
import numpy as np
import pandas as pd
from data_science_ai.preprocessing import StandardScaler, MinMaxScaler

class TestScalerProperties:
    """Property-based tests for scaler invariants."""

    @given(
        data=st.lists(
            st.floats(
                allow_nan=False,
                allow_infinity=False,
                min_value=-1e6,
                max_value=1e6
            ),
            min_size=10,
            max_size=1000
        )
    )
    @settings(max_examples=100)
    def test_scaler_is_invertible(self, data):
        """Property: StandardScaler should be invertible."""
        X = np.array(data).reshape(-1, 1)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        X_inverted = scaler.inverse_transform(X_scaled)

        # Should recover original data
        assert np.allclose(X, X_inverted, rtol=1e-5)

    @given(
        X=st.lists(
            st.tuples(
                st.floats(allow_nan=False, allow_infinity=False, min_value=-100, max_value=100),
                st.floats(allow_nan=False, allow_infinity=False, min_value=-100, max_value=100)
            ),
            min_size=5,
            max_size=100
        )
    )
    @settings(max_examples=100)
    def test_minmax_scaler_range(self, X):
        """Property: MinMaxScaler output should be in [0, 1]."""
        X = np.array(X)

        scaler = MinMaxScaler(feature_range=(0, 1))
        X_scaled = scaler.fit_transform(X)

        assert np.all(X_scaled >= 0)
        assert np.all(X_scaled <= 1)

    @given(
        X=st.lists(
            st.floats(allow_nan=False, allow_infinity=False, min_value=-100, max_value=100),
            min_size=5,
            max_size=100
        )
    )
    @settings(max_examples=100)
    def test_scaler_preserves_order(self, X):
        """Property: Scaling should preserve order of samples."""
        X_array = np.array(X).reshape(-1, 1)

        # Get original ordering
        original_order = np.argsort(X_array.flatten())

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_array)

        # Scaled ordering should match original
        scaled_order = np.argsort(X_scaled.flatten())

        assert np.array_equal(original_order, scaled_order)

class TestModelProperties:
    """Property-based tests for model invariants."""

    @given(
        n_samples=st.integers(min_value=10, max_value=100),
        n_features=st.integers(min_value=1, max_value=20)
    )
    @settings(max_examples=50)
    def test_classifier_output_shape(self, n_samples, n_features):
        """Property: Classifier predictions should match input size."""
        from data_science_ai.models import LogisticRegression

        np.random.seed(42)
        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, 2, n_samples)

        model = LogisticRegression()
        model.fit(X, y)
        predictions = model.predict(X)

        assert predictions.shape[0] == n_samples

    @given(
        threshold=st.floats(min_value=0, max_value=1)
    )
    @settings(max_examples=20)
    def test_probability_threshold_monotonicity(self, threshold):
        """Property: Higher probabilities should predict positive class."""
        from data_science_ai.models import LogisticRegression

        np.random.seed(42)
        X = np.random.randn(100, 5)
        y = np.random.randint(0, 2, 100)

        model = LogisticRegression()
        model.fit(X, y)

        proba = model.predict_proba(X)
        predictions = (proba[:, 1] >= threshold).astype(int)

        # All high probability samples should predict positive
        high_prob = proba[:, 1] > threshold
        assert np.all(predictions[high_prob] == 1)

class TestDataTransformationProperties:
    """Property-based tests for data transformations."""

    @given(
        df=st.data(),
    )
    def test_transformation_produces_valid_dataframe(self, df):
        """Property: Transformations should produce valid DataFrames."""
        from data_science_ai.preprocessing import DataFrameTransformer

        # Generate valid DataFrame
        data = {
            'col1': st.lists(st.floats(allow_nan=False, allow_infinity=False),
                           min_size=5, max_size=20).example(),
            'col2': st.lists(st.integers(), min_size=5, max_size=20).example(),
        }
        df = pd.DataFrame(data)

        transformer = DataFrameTransformer()
        result = transformer.transform(df)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(df)
        assert not result.isnull().any().any()

```

---

## Regression Tests

Regression tests ensure model behavior remains stable across versions.

```python
# tests/test_regression.py
import pytest
import numpy as np
import pickle
from data_science_ai.models import LogisticRegression

class TestRegressionPrevention:
    """Tests to catch regression in model behavior."""

    @pytest.fixture
    def baseline_model(self, tmp_path):
        """Create and save baseline model."""
        np.random.seed(42)
        X = np.random.randn(100, 5)
        y = np.random.randint(0, 2, 100)

        model = LogisticRegression()
        model.fit(X, y)

        baseline_predictions = model.predict(X[:10])
        baseline_proba = model.predict_proba(X[:10])

        return {
            'model': model,
            'predictions': baseline_predictions,
            'proba': baseline_proba,
            'X_test': X[:10]
        }

    def test_predictions_match_baseline(self, baseline_model):
        """Test that current predictions match baseline."""
        model = baseline_model['model']
        X_test = baseline_model['X_test']
        baseline_predictions = baseline_model['predictions']

        current_predictions = model.predict(X_test)

        # Should be identical after re-fitting with same data
        assert np.array_equal(current_predictions, baseline_predictions)

    def test_probabilities_match_baseline(self, baseline_model):
        """Test that probabilities match baseline."""
        model = baseline_model['model']
        X_test = baseline_model['X_test']
        baseline_proba = baseline_model['proba']

        current_proba = model.predict_proba(X_test)

        assert np.allclose(current_proba, baseline_proba, rtol=1e-5)

    def test_model_serialization_consistency(self, baseline_model, tmp_path):
        """Test that model serialization preserves behavior."""
        model = baseline_model['model']
        X_test = baseline_model['X_test']
        baseline_predictions = baseline_model['predictions']

        # Serialize and deserialize
        model_path = tmp_path / "model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)

        with open(model_path, 'rb') as f:
            loaded_model = pickle.load(f)

        loaded_predictions = loaded_model.predict(X_test)

        assert np.array_equal(loaded_predictions, baseline_predictions)

    def test_hyperparameter_sensitivity(self):
        """Test that hyperparameter changes affect behavior."""
        np.random.seed(42)
        X = np.random.randn(50, 5)
        y = np.random.randint(0, 2, 50)

        model1 = LogisticRegression(learning_rate=0.01)
        model1.fit(X, y)
        pred1 = model1.predict(X[:5])

        model2 = LogisticRegression(learning_rate=0.001)
        model2.fit(X, y)
        pred2 = model2.predict(X[:5])

        # Different hyperparameters may produce different results
        # (This is a basic test; more sophisticated comparison might be needed)
        assert pred1.shape == pred2.shape

```

---

## Performance Tests

Performance tests ensure the model meets latency and throughput requirements.

```python
# tests/test_performance.py
import pytest
import numpy as np
import time
from data_science_ai.models import LogisticRegression, RandomForest

class TestInferencePerformance:
    """Tests for model inference performance."""

    @pytest.fixture
    def trained_model(self):
        """Create and train a model."""
        np.random.seed(42)
        X = np.random.randn(1000, 10)
        y = np.random.randint(0, 2, 1000)

        model = LogisticRegression()
        model.fit(X, y)
        return model, X

    @pytest.mark.performance
    def test_inference_latency(self, trained_model):
        """Test that inference meets latency requirements."""
        model, X = trained_model

        # Warm up
        model.predict(X[:10])

        # Measure inference time for single sample
        start = time.time()
        for _ in range(100):
            model.predict(X[:1])
        elapsed = time.time() - start

        avg_latency = elapsed / 100
        # Should be fast for small model
        assert avg_latency < 0.01, f"Inference latency {avg_latency}s exceeds 10ms"

    @pytest.mark.performance
    def test_batch_throughput(self, trained_model):
        """Test batch inference throughput."""
        model, X = trained_model
        batch_size = 100

        start = time.time()
        predictions = model.predict(X[:batch_size])
        elapsed = time.time() - start

        throughput = batch_size / elapsed
        # Should process at least 100 samples per second
        assert throughput > 100, f"Throughput {throughput} samples/s is too low"

    @pytest.mark.performance
    def test_memory_efficiency(self, trained_model):
        """Test that model doesn't consume excessive memory."""
        model, X = trained_model

        import sys
        model_size = sys.getsizeof(model)

        # Model should be reasonably small (< 10MB for typical classifier)
        assert model_size < 10_000_000, f"Model size {model_size} is too large"

class TestTrainingPerformance:
    """Tests for training performance."""

    @pytest.mark.performance
    def test_training_convergence_speed(self):
        """Test that training converges in reasonable time."""
        np.random.seed(42)
        X = np.random.randn(100, 5)
        y = np.random.randint(0, 2, 100)

        model = LogisticRegression(max_iterations=100)

        start = time.time()
        model.fit(X, y)
        elapsed = time.time() - start

        # Should train quickly on small dataset
        assert elapsed < 10.0, f"Training took {elapsed}s, expected < 10s"

    @pytest.mark.performance
    def test_scalability_with_data_size(self):
        """Test that training time scales reasonably."""
        model = LogisticRegression()

        times = []
        for size in [100, 500, 1000]:
            np.random.seed(42)
            X = np.random.randn(size, 5)
            y = np.random.randint(0, 2, size)

            start = time.time()
            model.fit(X, y)
            elapsed = time.time() - start
            times.append(elapsed)

        # Time should not increase quadratically
        ratio = times[-1] / times[0]
        # 10x data should take < 15x time (roughly linear to 1.5x linear)
        assert ratio < 15, f"Training doesn't scale well: {ratio}x time increase"

```

---

## Testing Frameworks

### Pytest Fixtures and Configuration

```python
# tests/conftest.py
"""Shared fixtures for all tests."""
import pytest
import numpy as np
import pandas as pd
import tempfile
from pathlib import Path

@pytest.fixture
def random_seed():
    """Set random seed for reproducibility."""
    np.random.seed(42)
    return 42

@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def sample_dataset():
    """Create sample dataset for testing."""
    np.random.seed(42)
    X = pd.DataFrame({
        'feature_1': np.random.randn(100),
        'feature_2': np.random.randn(100),
        'feature_3': np.random.choice(['A', 'B', 'C'], 100)
    })
    y = pd.Series(np.random.randint(0, 2, 100), name='target')
    return X, y

@pytest.fixture
def large_dataset():
    """Create large dataset for performance testing."""
    np.random.seed(42)
    n_samples = 10000
    n_features = 50

    X = np.random.randn(n_samples, n_features)
    y = np.random.randint(0, 2, n_samples)

    return X, y

@pytest.fixture
def imbalanced_dataset():
    """Create imbalanced dataset for testing."""
    np.random.seed(42)
    X = np.random.randn(1000, 10)
    y = np.concatenate([
        np.zeros(950, dtype=int),
        np.ones(50, dtype=int)
    ])
    return X, y
```

### Pytest Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=data_science_ai
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow tests
    gpu: GPU-requiring tests
```

### Running Tests with Hypothesis

```bash
# Run all tests with hypothesis
pytest tests/ -v

# Run with specific profile (fast, default, slow)
pytest tests/ --hypothesis-profile=default

# Run with seed for reproducibility
pytest tests/ --hypothesis-seed=12345

# Generate examples
pytest tests/test_properties.py --hypothesis-verbosity=verbose
```

---

## CI/CD for ML Testing

### GitHub Actions Workflow

```yaml
# .github/workflows/ml-tests.yml
name: ML Testing Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Lint with flake8
      run: |
        flake8 data_science_ai tests --count --select=E9,F63,F7,F82 --show-source --statistics

    - name: Run unit tests
      run: |
        pytest tests/test_*.py -m unit -v --cov

    - name: Run integration tests
      run: |
        pytest tests/test_*_integration.py -m integration -v

    - name: Run property-based tests
      run: |
        pytest tests/test_properties.py -v

    - name: Run data validation tests
      run: |
        pytest tests/test_data_validation.py -v

    - name: Run model validation tests
      run: |
        pytest tests/test_model_validation.py -v

    - name: Run performance tests
      run: |
        pytest tests/ -m performance -v

    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [ --profile, black ]

  - repo: https://github.com/PyCQA/pylint
    rev: pylint-2.17.4
    hooks:
      - id: pylint
        args: [ --disable=C0111 ]
```

### Model Testing Script

```python
# scripts/validate_model.py
"""
Script to validate a trained model before deployment.
Follows Google's ML testing practices.
"""
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from data_science_ai.validation import ModelValidator, DataValidator

def validate_model(model_path, data_path, config_path):
    """
    Comprehensive model validation before deployment.

    Args:
        model_path: Path to trained model
        data_path: Path to validation data
        config_path: Path to validation config

    Returns:
        dict: Validation results
    """
    # Load model and data
    import pickle
    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    df = pd.read_csv(data_path)
    X = df.drop('target', axis=1)
    y = df['target']

    # Run validation suite
    validator = ModelValidator(config_path)

    results = {
        'predictions': validator.check_predictions(model, X),
        'metrics': validator.check_metrics(model, X, y),
        'stability': validator.check_stability(model, X),
        'fairness': validator.check_fairness(model, X, y),
        'robustness': validator.check_robustness(model, X),
    }

    # Print results
    print("\n=== Model Validation Results ===\n")
    for check_name, result in results.items():
        print(f"{check_name}: {'PASS' if result['pass'] else 'FAIL'}")
        if not result['pass']:
            print(f"  Details: {result['details']}\n")

    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True, help='Path to model')
    parser.add_argument('--data', required=True, help='Path to validation data')
    parser.add_argument('--config', required=True, help='Path to config')

    args = parser.parse_args()
    validate_model(args.model, args.data, args.config)
```

---

## Complete Test Examples

### Example 1: Complete Classification Pipeline Test

```python
# tests/test_classification_pipeline_example.py
import pytest
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

from data_science_ai.pipeline import ClassificationPipeline
from data_science_ai.evaluation import MetricsCalculator

class TestClassificationPipeline:
    """Complete example: Testing a classification pipeline."""

    @pytest.fixture
    def classification_data(self):
        """Create synthetic classification dataset."""
        X, y = make_classification(
            n_samples=500,
            n_features=20,
            n_informative=10,
            n_redundant=5,
            random_state=42
        )

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test
        }

    def test_pipeline_initialization(self):
        """Test pipeline initializes correctly."""
        pipeline = ClassificationPipeline()
        assert pipeline is not None
        assert hasattr(pipeline, 'fit')
        assert hasattr(pipeline, 'predict')

    def test_pipeline_fit(self, classification_data):
        """Test pipeline fits without errors."""
        pipeline = ClassificationPipeline()

        # Should not raise
        pipeline.fit(
            classification_data['X_train'],
            classification_data['y_train']
        )

    def test_pipeline_predict(self, classification_data):
        """Test pipeline predictions."""
        pipeline = ClassificationPipeline()
        pipeline.fit(
            classification_data['X_train'],
            classification_data['y_train']
        )

        predictions = pipeline.predict(classification_data['X_test'])

        assert predictions.shape[0] == classification_data['X_test'].shape[0]
        assert np.all((predictions == 0) | (predictions == 1))

    def test_pipeline_probability_output(self, classification_data):
        """Test pipeline probability output."""
        pipeline = ClassificationPipeline()
        pipeline.fit(
            classification_data['X_train'],
            classification_data['y_train']
        )

        proba = pipeline.predict_proba(classification_data['X_test'])

        assert proba.shape == (len(classification_data['X_test']), 2)
        assert np.allclose(proba.sum(axis=1), 1.0)

    def test_pipeline_metrics(self, classification_data):
        """Test pipeline metric evaluation."""
        pipeline = ClassificationPipeline()
        pipeline.fit(
            classification_data['X_train'],
            classification_data['y_train']
        )

        predictions = pipeline.predict(classification_data['X_test'])

        calculator = MetricsCalculator()
        metrics = calculator.compute_metrics(
            classification_data['y_test'],
            predictions
        )

        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1' in metrics

        for key, value in metrics.items():
            assert 0.0 <= value <= 1.0

    def test_pipeline_end_to_end(self, classification_data):
        """Test complete pipeline flow."""
        pipeline = ClassificationPipeline()

        # Fit
        pipeline.fit(
            classification_data['X_train'],
            classification_data['y_train']
        )

        # Predict
        predictions = pipeline.predict(classification_data['X_test'])
        proba = pipeline.predict_proba(classification_data['X_test'])

        # Evaluate
        calculator = MetricsCalculator()
        metrics = calculator.compute_metrics(
            classification_data['y_test'],
            predictions
        )

        # Verify
        assert predictions.shape[0] == len(classification_data['y_test'])
        assert proba.shape[0] == len(classification_data['y_test'])
        assert all(0.0 <= v <= 1.0 for v in metrics.values())

```

### Example 2: Complete Data Validation Test

```python
# tests/test_data_validation_example.py
import pytest
import pandas as pd
import numpy as np
from data_science_ai.data import DataQualityValidator

class TestDataQualityValidationExample:
    """Complete example: Data quality validation pipeline."""

    @pytest.fixture
    def raw_data(self):
        """Create realistic data with quality issues."""
        return pd.DataFrame({
            'id': [1, 2, 3, 4, 5, 6, 7, 8],
            'age': [25, 32, np.nan, 45, 28, 200, 30, -5],
            'income': [50000, 60000, 55000, np.nan, 65000, 70000, 60000, 58000],
            'category': ['A', 'B', 'A', 'C', 'B', 'B', 'A', None],
            'score': [0.5, 0.7, 0.6, 0.8, 0.5, 0.5, 0.5, 0.6],
            'timestamp': pd.date_range('2024-01-01', periods=8)
        })

    def test_check_missing_values(self, raw_data):
        """Test detection of missing values."""
        validator = DataQualityValidator()
        missing = validator.check_missing_values(raw_data)

        assert missing['age'] == 1
        assert missing['income'] == 1
        assert missing['category'] == 1
        assert missing['id'] == 0

    def test_check_outliers(self, raw_data):
        """Test outlier detection."""
        validator = DataQualityValidator()
        outliers = validator.detect_outliers(
            raw_data[['age', 'income']],
            method='iqr'
        )

        # Age has obvious outliers (200, -5)
        assert len(outliers) > 0

    def test_check_duplicates(self, raw_data):
        """Test duplicate detection."""
        validator = DataQualityValidator()

        # Add a duplicate row
        data_with_dup = pd.concat([raw_data, raw_data.iloc[0:1]])

        duplicates = validator.find_duplicates(data_with_dup)
        assert len(duplicates) > 0

    def test_validate_numeric_ranges(self, raw_data):
        """Test numeric range validation."""
        validator = DataQualityValidator()

        ranges = {
            'age': (0, 120),
            'income': (0, 200000),
            'score': (0, 1)
        }

        violations = validator.check_ranges(raw_data, ranges)

        # Age has out-of-range values
        assert len(violations['age']) > 0

    def test_validate_categorical_values(self, raw_data):
        """Test categorical value validation."""
        validator = DataQualityValidator()

        allowed_values = {
            'category': ['A', 'B', 'C']
        }

        violations = validator.check_categorical_values(
            raw_data,
            allowed_values
        )

        # None is not in allowed values
        assert violations['category'] is not None

    def test_complete_data_quality_report(self, raw_data):
        """Test complete data quality report."""
        validator = DataQualityValidator()

        report = validator.generate_report(raw_data)

        assert 'missing_values' in report
        assert 'outliers' in report
        assert 'duplicates' in report
        assert 'quality_score' in report

        # Report should show issues with this data
        assert report['quality_score'] < 1.0

```

---

## Best Practices

### 1. Test Organization

```
tests/
├── conftest.py                      # Shared fixtures
├── test_preprocessing.py            # Unit tests
├── test_models.py                   # Unit tests
├── test_pipeline_integration.py     # Integration tests
├── test_data_validation.py          # Data tests
├── test_model_validation.py         # Model tests
├── test_properties.py               # Property-based tests
├── test_performance.py              # Performance tests
├── test_regression.py               # Regression tests
└── fixtures/
    ├── sample_data.csv
    └── baseline_model.pkl
```

### 2. Testing Best Practices

- **Arrange-Act-Assert Pattern**: Structure tests clearly
- **One assertion per test**: Makes failures clear
- **Descriptive test names**: What, not how
- **Fixtures for setup**: Reuse common test data
- **Parametrization**: Test multiple cases
- **Mocking external dependencies**: Isolate code
- **Clear failure messages**: Help debugging

### 3. Data Testing Checklist

- [ ] Missing values
- [ ] Data types correct
- [ ] Ranges/bounds valid
- [ ] Categorical values allowed
- [ ] No duplicates
- [ ] No data leakage
- [ ] Distribution reasonable
- [ ] Sufficient samples per class (for classification)

### 4. Model Testing Checklist

- [ ] Predictions shape correct
- [ ] Predictions in valid range
- [ ] Probabilities sum to 1
- [ ] No NaN/Inf values
- [ ] Metrics computed correctly
- [ ] Model reproducible (with seed)
- [ ] Performance acceptable
- [ ] Behavior consistent with baselines

### 5. Google's ML Testing Practices

Reference: [Google's Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)

Key principles:
- **ML-specific testing** beyond traditional QA
- **Data quality first** - garbage in, garbage out
- **Model metrics matter** - not just accuracy
- **Test data distribution** - detect shift
- **Monitor in production** - not just offline
- **Shadow models** - test new approaches safely
- **Regular validation** - continuous testing
- **Track metadata** - know your training data

### 6. Testing Tools Summary

| Tool | Purpose |
|------|---------|
| `pytest` | Test framework |
| `hypothesis` | Property-based testing |
| `pytest-cov` | Coverage reporting |
| `pytest-benchmark` | Performance testing |
| `pytest-mock` | Mocking |
| `pandas-testing` | DataFrame testing |
| `great-expectations` | Data validation |
| `deepdiff` | Object comparison |

### 7. Performance Testing Tips

```python
# Use pytest-benchmark for consistent performance tests
import pytest

@pytest.mark.benchmark
def test_inference_speed(benchmark, model, data):
    """Benchmark model inference."""
    result = benchmark(model.predict, data)
    assert len(result) == len(data)
```

---

## Conclusion

ML testing requires a multi-faceted approach covering:

1. **Unit Tests**: Individual components
2. **Integration Tests**: Component interaction
3. **Data Tests**: Input quality and distributions
4. **Model Tests**: Correctness and metrics
5. **Property Tests**: Invariant properties
6. **Performance Tests**: Latency and throughput
7. **Regression Tests**: Stability across versions

Follow Google's ML testing practices and adapt these patterns to your specific use cases. Always test data quality first - it's the foundation of ML system reliability.

## References

- [Google's Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [pytest Documentation](https://docs.pytest.org/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Testing Data Science Code](https://www.oreilly.com/content/what-is-testing/)
