# Model Evaluation Guide

A comprehensive guide to evaluating machine learning models with practical code examples, statistical rigor, and best practices.

## Table of Contents

1. [Classification Metrics](#classification-metrics)
2. [Regression Metrics](#regression-metrics)
3. [Cross-Validation Strategies](#cross-validation-strategies)
4. [Statistical Significance Testing](#statistical-significance-testing)
5. [Confidence Intervals](#confidence-intervals)
6. [Calibration Analysis](#calibration-analysis)
7. [Fairness Metrics](#fairness-metrics)
8. [Error Analysis Techniques](#error-analysis-techniques)
9. [Best Practices](#best-practices)
10. [Complete Evaluation Pipeline](#complete-evaluation-pipeline)

---

## Classification Metrics

Classification metrics evaluate how well a model predicts discrete categories. Each metric captures different aspects of performance.

### Fundamental Concepts

- **True Positive (TP)**: Correctly predicted positive samples
- **True Negative (TN)**: Correctly predicted negative samples
- **False Positive (FP)**: Negative samples incorrectly predicted as positive
- **False Negative (FN)**: Positive samples incorrectly predicted as negative

### 1. Accuracy

Proportion of correct predictions among all samples.

**Formula**: `Accuracy = (TP + TN) / (TP + TN + FP + FN)`

**Limitations**:
- Misleading with imbalanced datasets
- Treats all errors equally

**Code Example:**

```python
from sklearn.metrics import accuracy_score
import numpy as np

# Sample predictions and true labels
y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 1])
y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0, 1, 1])

accuracy = accuracy_score(y_true, y_pred)
print(f"Accuracy: {accuracy:.4f}")  # Output: 0.8000

# Manual calculation
tp = np.sum((y_pred == 1) & (y_true == 1))
tn = np.sum((y_pred == 0) & (y_true == 0))
total = len(y_true)
manual_accuracy = (tp + tn) / total
print(f"Manual Accuracy: {manual_accuracy:.4f}")
```

### 2. Precision

Proportion of positive predictions that were correct.

**Formula**: `Precision = TP / (TP + FP)`

**When to use**: When false positives are costly (spam detection, medical screening)

**Code Example:**

```python
from sklearn.metrics import precision_score, precision_recall_curve
import matplotlib.pyplot as plt

precision = precision_score(y_true, y_pred)
print(f"Precision: {precision:.4f}")

# For probability predictions
y_pred_proba = np.array([0.9, 0.1, 0.8, 0.3, 0.2, 0.75, 0.6, 0.1, 0.85, 0.95])

# Get precision at different thresholds
precisions, recalls, thresholds = precision_recall_curve(y_true, y_pred_proba)

plt.figure(figsize=(10, 6))
plt.plot(recalls, precisions, marker='o', linewidth=2)
plt.xlabel('Recall', fontsize=12)
plt.ylabel('Precision', fontsize=12)
plt.title('Precision-Recall Curve', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.show()
```

### 3. Recall (Sensitivity)

Proportion of actual positive samples that were correctly identified.

**Formula**: `Recall = TP / (TP + FN)`

**When to use**: When false negatives are costly (disease detection, fraud)

**Code Example:**

```python
from sklearn.metrics import recall_score

recall = recall_score(y_true, y_pred)
print(f"Recall: {recall:.4f}")

# Calculate sensitivity and specificity
tp = np.sum((y_pred == 1) & (y_true == 1))
tn = np.sum((y_pred == 0) & (y_true == 0))
fp = np.sum((y_pred == 1) & (y_true == 0))
fn = np.sum((y_pred == 0) & (y_true == 1))

sensitivity = tp / (tp + fn)  # Same as recall
specificity = tn / (tn + fp)

print(f"Sensitivity: {sensitivity:.4f}")
print(f"Specificity: {specificity:.4f}")
```

### 4. F1 Score

Harmonic mean of precision and recall. Balances both metrics.

**Formula**: `F1 = 2 × (Precision × Recall) / (Precision + Recall)`

**Use cases**: Imbalanced datasets where both precision and recall matter

**Code Example:**

```python
from sklearn.metrics import f1_score, classification_report

f1 = f1_score(y_true, y_pred)
print(f"F1 Score: {f1:.4f}")

# Weighted F1 for multi-class problems
f1_weighted = f1_score(y_true, y_pred, average='weighted')
print(f"F1 Score (weighted): {f1_weighted:.4f}")

# Comprehensive classification report
print("\nClassification Report:")
print(classification_report(y_true, y_pred))
```

### 5. ROC-AUC (Receiver Operating Characteristic - Area Under Curve)

Measures trade-off between true positive rate (TPR) and false positive rate (FPR) across all classification thresholds.

**Interpretation**:
- AUC = 1.0: Perfect classifier
- AUC = 0.5: Random classifier
- AUC < 0.5: Worse than random

**Code Example:**

```python
from sklearn.metrics import roc_curve, auc, roc_auc_score
import matplotlib.pyplot as plt

# Calculate ROC curve
fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
roc_auc = auc(fpr, tpr)

# Alternatively
roc_auc_score_val = roc_auc_score(y_true, y_pred_proba)
print(f"ROC-AUC: {roc_auc_score_val:.4f}")

# Plot ROC curve
plt.figure(figsize=(10, 8))
plt.plot(fpr, tpr, color='darkorange', lw=2,
         label=f'ROC Curve (AUC = {roc_auc:.3f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--',
         label='Random Classifier (AUC = 0.5)')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate', fontsize=12)
plt.ylabel('True Positive Rate', fontsize=12)
plt.title('ROC Curve', fontsize=14, fontweight='bold')
plt.legend(loc="lower right", fontsize=11)
plt.grid(True, alpha=0.3)
plt.show()

# Find optimal threshold
optimal_idx = np.argmax(tpr - fpr)
optimal_threshold = thresholds[optimal_idx]
print(f"Optimal Threshold: {optimal_threshold:.4f}")
```

### 6. PR-AUC (Precision-Recall Area Under Curve)

More informative than ROC-AUC for imbalanced datasets.

**Advantages over ROC-AUC**:
- Not influenced by true negatives
- Better for imbalanced data
- Directly related to decision threshold

**Code Example:**

```python
from sklearn.metrics import precision_recall_curve, auc

# Calculate PR curve
precisions, recalls, thresholds = precision_recall_curve(y_true, y_pred_proba)
pr_auc = auc(recalls, precisions)

print(f"PR-AUC: {pr_auc:.4f}")

# Plot PR curve
plt.figure(figsize=(10, 8))
plt.plot(recalls, precisions, color='blue', lw=2,
         label=f'PR Curve (AUC = {pr_auc:.3f})')
plt.xlabel('Recall', fontsize=12)
plt.ylabel('Precision', fontsize=12)
plt.title('Precision-Recall Curve', fontsize=14, fontweight='bold')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.legend(loc="lower left", fontsize=11)
plt.grid(True, alpha=0.3)
plt.show()
```

### Classification Metrics Summary

```python
def evaluate_classification(y_true, y_pred, y_pred_proba):
    """Comprehensive classification evaluation."""
    from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                                f1_score, roc_auc_score, precision_recall_curve, auc)

    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_true, y_pred_proba),
    }

    # PR-AUC
    precisions, recalls, _ = precision_recall_curve(y_true, y_pred_proba)
    metrics['pr_auc'] = auc(recalls, precisions)

    return metrics

# Usage
metrics = evaluate_classification(y_true, y_pred, y_pred_proba)
for metric, value in metrics.items():
    print(f"{metric}: {value:.4f}")
```

---

## Regression Metrics

Regression metrics evaluate how well a model predicts continuous values.

### 1. Mean Absolute Error (MAE)

Average absolute difference between predictions and actual values.

**Formula**: `MAE = (1/n) × Σ|y_i - ŷ_i|`

**Advantages**:
- Same units as target variable
- Robust to outliers

**Code Example:**

```python
from sklearn.metrics import mean_absolute_error
import numpy as np

y_true = np.array([3.0, -0.5, 2.0, 7.0, 4.5])
y_pred = np.array([2.5, 0.0, 2.0, 8.0, 4.0])

mae = mean_absolute_error(y_true, y_pred)
print(f"MAE: {mae:.4f}")

# Manual calculation
manual_mae = np.mean(np.abs(y_true - y_pred))
print(f"Manual MAE: {manual_mae:.4f}")
```

### 2. Mean Squared Error (MSE)

Average squared difference between predictions and actual values.

**Formula**: `MSE = (1/n) × Σ(y_i - ŷ_i)²`

**Advantages**:
- Penalizes larger errors more
- Differentiable (good for optimization)

**Disadvantages**:
- Not in same units as target (squared)
- Sensitive to outliers

**Code Example:**

```python
from sklearn.metrics import mean_squared_error

mse = mean_squared_error(y_true, y_pred)
print(f"MSE: {mse:.4f}")

# Manual calculation
manual_mse = np.mean((y_true - y_pred) ** 2)
print(f"Manual MSE: {manual_mse:.4f}")

# Visualize residuals
residuals = y_true - y_pred
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.scatter(y_pred, residuals, alpha=0.6)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted Values', fontsize=11)
plt.ylabel('Residuals', fontsize=11)
plt.title('Residual Plot', fontsize=12, fontweight='bold')
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.hist(residuals, bins=10, alpha=0.7, edgecolor='black')
plt.xlabel('Residuals', fontsize=11)
plt.ylabel('Frequency', fontsize=11)
plt.title('Distribution of Residuals', fontsize=12, fontweight='bold')
plt.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.show()
```

### 3. Root Mean Squared Error (RMSE)

Square root of MSE, returning to original units.

**Formula**: `RMSE = √MSE`

**Use**: When you want MSE's sensitivity to outliers but in original units

**Code Example:**

```python
from sklearn.metrics import mean_squared_error
import numpy as np

rmse = np.sqrt(mean_squared_error(y_true, y_pred))
print(f"RMSE: {rmse:.4f}")

# Relationship between metrics
mse = mean_squared_error(y_true, y_pred)
mae = mean_absolute_error(y_true, y_pred)

print(f"MSE: {mse:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"MAE: {mae:.4f}")
print(f"RMSE/MAE Ratio: {rmse/mae:.4f}")  # >1 indicates presence of outliers
```

### 4. R² Score (Coefficient of Determination)

Proportion of variance in target variable explained by the model.

**Formula**: `R² = 1 - (SS_res / SS_tot)` where:
- SS_res = Σ(y_i - ŷ_i)²
- SS_tot = Σ(y_i - ȳ)²

**Interpretation**:
- R² = 1.0: Perfect fit
- R² = 0.0: Model performs as well as predicting mean
- R² < 0.0: Worse than predicting mean

**Code Example:**

```python
from sklearn.metrics import r2_score

r2 = r2_score(y_true, y_pred)
print(f"R² Score: {r2:.4f}")

# Visualize prediction quality
plt.figure(figsize=(10, 6))
plt.scatter(y_true, y_pred, alpha=0.6, s=100)
min_val = min(y_true.min(), y_pred.min())
max_val = max(y_true.max(), y_pred.max())
plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')
plt.xlabel('True Values', fontsize=12)
plt.ylabel('Predicted Values', fontsize=12)
plt.title(f'Prediction Quality (R² = {r2:.4f})', fontsize=14, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.axis('equal')
plt.show()
```

### Regression Metrics Summary

```python
def evaluate_regression(y_true, y_pred):
    """Comprehensive regression evaluation."""
    from sklearn.metrics import (mean_absolute_error, mean_squared_error,
                                r2_score, mean_absolute_percentage_error)

    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    metrics = {
        'mae': mae,
        'mse': mse,
        'rmse': rmse,
        'r2': r2,
        'mape': mean_absolute_percentage_error(y_true, y_pred),
    }

    return metrics

# Usage
reg_metrics = evaluate_regression(y_true, y_pred)
for metric, value in reg_metrics.items():
    print(f"{metric}: {value:.4f}")
```

---

## Cross-Validation Strategies

Cross-validation estimates model performance on unseen data and provides confidence in results.

### 1. K-Fold Cross-Validation

Splits data into k subsets, training on k-1 and testing on 1.

**Advantages**:
- Uses all data for training and testing
- Reduces variance in performance estimates

**Code Example:**

```python
from sklearn.model_selection import cross_val_score, cross_validate, KFold
from sklearn.ensemble import RandomForestRegressor
import numpy as np

# Sample data
X = np.random.rand(100, 10)
y = np.random.rand(100)

model = RandomForestRegressor(n_estimators=100, random_state=42)

# Simple cross-validation
kfold = KFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=kfold, scoring='r2')

print(f"CV Scores: {scores}")
print(f"Mean CV Score: {scores.mean():.4f}")
print(f"Std CV Score: {scores.std():.4f}")

# Multiple metrics
scoring = {
    'r2': 'r2',
    'mae': 'neg_mean_absolute_error',
    'rmse': 'neg_root_mean_squared_error'
}

cv_results = cross_validate(model, X, y, cv=kfold, scoring=scoring)

for metric in scoring:
    scores = -cv_results[f'test_{metric}']
    print(f"{metric.upper()}: {scores.mean():.4f} (+/- {scores.std():.4f})")
```

### 2. Stratified K-Fold (Classification)

Maintains class distribution in each fold for imbalanced data.

**Code Example:**

```python
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier

y_class = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 1] * 10)
X_class = np.random.rand(100, 10)

model = RandomForestClassifier(n_estimators=100, random_state=42)

skfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X_class, y_class, cv=skfold, scoring='roc_auc')

print(f"Stratified CV Scores: {scores}")
print(f"Mean: {scores.mean():.4f} (+/- {scores.std():.4f})")

# Verify class distribution in each fold
for fold, (train_idx, test_idx) in enumerate(skfold.split(X_class, y_class)):
    train_positive_ratio = y_class[train_idx].mean()
    test_positive_ratio = y_class[test_idx].mean()
    print(f"Fold {fold}: Train pos ratio: {train_positive_ratio:.2%}, "
          f"Test pos ratio: {test_positive_ratio:.2%}")
```

### 3. Leave-One-Out Cross-Validation (LOOCV)

Each sample is used once as test set.

**Use cases**: Small datasets, when maximum data utilization needed

**Code Example:**

```python
from sklearn.model_selection import LeaveOneOut, cross_val_score

loo = LeaveOneOut()
# Warning: LOOCV is slow for large datasets
# Typically used with n < 1000

if len(X) < 100:  # Only for small datasets
    scores = cross_val_score(model, X, y, cv=loo, scoring='r2')
    print(f"LOOCV Score: {scores.mean():.4f}")
else:
    print("LOOCV recommended only for small datasets (n < 100)")
```

### 4. Time Series Cross-Validation

Respects temporal ordering for time series data.

**Code Example:**

```python
from sklearn.model_selection import TimeSeriesSplit
import numpy as np

# Time series data
X_ts = np.random.rand(200, 5)
y_ts = np.random.rand(200)

tscv = TimeSeriesSplit(n_splits=5)

plt.figure(figsize=(12, 6))

for fold, (train_idx, test_idx) in enumerate(tscv.split(X_ts)):
    plt.barh(fold, len(train_idx), left=0, height=0.5, label='Train' if fold == 0 else '')
    plt.barh(fold, len(test_idx), left=len(train_idx), height=0.5,
             label='Test' if fold == 0 else '', color='orange')

plt.xlabel('Data Points', fontsize=12)
plt.ylabel('Fold', fontsize=12)
plt.title('Time Series Cross-Validation Splits', fontsize=14, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.show()

# Evaluate with time series CV
scores = cross_val_score(model, X_ts, y_ts, cv=tscv, scoring='r2')
print(f"Time Series CV Scores: {scores.mean():.4f} (+/- {scores.std():.4f})")
```

---

## Statistical Significance Testing

Determine if performance differences are statistically significant or due to chance.

### 1. Paired t-test

Compare two models on same data using CV results.

**Code Example:**

```python
from scipy import stats
from sklearn.model_selection import cross_val_score, KFold
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

kfold = KFold(n_splits=5, shuffle=True, random_state=42)

model1 = RandomForestRegressor(random_state=42)
model2 = GradientBoostingRegressor(random_state=42)

scores1 = cross_val_score(model1, X, y, cv=kfold, scoring='r2')
scores2 = cross_val_score(model2, X, y, cv=kfold, scoring='r2')

# Paired t-test
t_stat, p_value = stats.ttest_rel(scores1, scores2)

print(f"Model 1 Mean CV Score: {scores1.mean():.4f}")
print(f"Model 2 Mean CV Score: {scores2.mean():.4f}")
print(f"t-statistic: {t_stat:.4f}")
print(f"p-value: {p_value:.4f}")

if p_value < 0.05:
    print("Difference is statistically significant (p < 0.05)")
else:
    print("Difference is NOT statistically significant (p >= 0.05)")
```

### 2. McNemar's Test (Classification)

Tests if two classifiers have significantly different error rates.

**Code Example:**

```python
from statsmodels.stats.contingency_tables import mcnemar

# Predictions from two models
y_pred1 = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 1] * 10)
y_pred2 = np.array([1, 0, 1, 0, 0, 1, 1, 0, 1, 1] * 10)
y_true_class = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 1] * 10)

# Create contingency table
# a: Model1 correct, Model2 incorrect
# b: Model1 incorrect, Model2 correct
# c: Both correct
# d: Both incorrect

model1_correct = (y_pred1 == y_true_class)
model2_correct = (y_pred2 == y_true_class)

table = np.array([
    [np.sum(model1_correct & model2_correct),  # Both correct
     np.sum(model1_correct & ~model2_correct)],  # M1 correct, M2 wrong
    [np.sum(~model1_correct & model2_correct),  # M1 wrong, M2 correct
     np.sum(~model1_correct & ~model2_correct)]  # Both wrong
])

result = mcnemar(table)
print(f"McNemar Test Statistic: {result.statistic:.4f}")
print(f"p-value: {result.pvalue:.4f}")

if result.pvalue < 0.05:
    print("Classifiers have significantly different error rates")
```

### 3. Bootstrap Test

Resampling-based test for comparing model performance.

**Code Example:**

```python
from sklearn.utils import resample

def bootstrap_compare(y_true, y_pred1, y_pred2, metric_func, n_iterations=1000):
    """Compare two models using bootstrap resampling."""
    differences = []

    for _ in range(n_iterations):
        # Resample
        indices = resample(range(len(y_true)), n_samples=len(y_true),
                          replace=True, random_state=None)

        score1 = metric_func(y_true[indices], y_pred1[indices])
        score2 = metric_func(y_true[indices], y_pred2[indices])

        differences.append(score1 - score2)

    differences = np.array(differences)

    # Two-sided p-value
    p_value = np.mean(np.abs(differences) >= np.abs(differences.mean()))

    return {
        'mean_diff': differences.mean(),
        'ci_lower': np.percentile(differences, 2.5),
        'ci_upper': np.percentile(differences, 97.5),
        'p_value': p_value
    }

# Usage
from sklearn.metrics import r2_score
results = bootstrap_compare(y_true, y_pred1, y_pred2, r2_score)

print(f"Mean Difference: {results['mean_diff']:.4f}")
print(f"95% CI: [{results['ci_lower']:.4f}, {results['ci_upper']:.4f}]")
print(f"p-value: {results['p_value']:.4f}")
```

---

## Confidence Intervals

Quantify uncertainty in performance estimates.

### 1. Parametric Confidence Intervals

Based on normal distribution assumptions.

**Code Example:**

```python
from scipy import stats
import numpy as np

def parametric_ci(scores, confidence=0.95):
    """Calculate parametric confidence interval."""
    n = len(scores)
    mean = scores.mean()
    std = scores.std()

    # Standard error
    se = std / np.sqrt(n)

    # Critical value
    alpha = 1 - confidence
    t_critical = stats.t.ppf(1 - alpha/2, df=n-1)

    ci_lower = mean - t_critical * se
    ci_upper = mean + t_critical * se

    return mean, ci_lower, ci_upper, se

# Usage with CV scores
kfold = KFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=kfold, scoring='r2')

mean, ci_lower, ci_upper, se = parametric_ci(scores)

print(f"Mean Score: {mean:.4f}")
print(f"95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
print(f"Standard Error: {se:.4f}")
```

### 2. Bootstrap Confidence Intervals

Non-parametric approach using resampling.

**Code Example:**

```python
def bootstrap_ci(y_true, y_pred, metric_func, n_bootstrap=1000, confidence=0.95):
    """Calculate bootstrap confidence interval."""
    bootstrap_scores = []

    for _ in range(n_bootstrap):
        indices = resample(range(len(y_true)), n_samples=len(y_true),
                          replace=True, random_state=None)
        score = metric_func(y_true[indices], y_pred[indices])
        bootstrap_scores.append(score)

    bootstrap_scores = np.array(bootstrap_scores)

    alpha = 1 - confidence
    ci_lower = np.percentile(bootstrap_scores, 100 * alpha/2)
    ci_upper = np.percentile(bootstrap_scores, 100 * (1 - alpha/2))

    return {
        'mean': bootstrap_scores.mean(),
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'std': bootstrap_scores.std(),
        'samples': bootstrap_scores
    }

# Usage
from sklearn.metrics import r2_score
ci_results = bootstrap_ci(y_true, y_pred, r2_score)

print(f"Bootstrap Mean: {ci_results['mean']:.4f}")
print(f"95% CI: [{ci_results['ci_lower']:.4f}, {ci_results['ci_upper']:.4f}]")

# Visualize bootstrap distribution
plt.figure(figsize=(10, 6))
plt.hist(ci_results['samples'], bins=50, alpha=0.7, edgecolor='black')
plt.axvline(ci_results['mean'], color='r', linestyle='--', linewidth=2, label='Mean')
plt.axvline(ci_results['ci_lower'], color='g', linestyle='--', linewidth=2, label='95% CI')
plt.axvline(ci_results['ci_upper'], color='g', linestyle='--', linewidth=2)
plt.xlabel('R² Score', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.title('Bootstrap Distribution of R² Score', fontsize=14, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3, axis='y')
plt.show()
```

---

## Calibration Analysis

Ensures predicted probabilities match actual frequencies.

### 1. Calibration Curve

Plots predicted probability vs true frequency.

**Code Example:**

```python
from sklearn.calibration import calibration_curve, CalibratedClassifierCV
import matplotlib.pyplot as plt

# Calculate calibration curve
prob_true, prob_pred = calibration_curve(y_true, y_pred_proba,
                                         n_bins=10, strategy='uniform')

# Plot calibration curve
plt.figure(figsize=(10, 8))
plt.plot(prob_pred, prob_true, marker='o', linewidth=2, markersize=8,
         label='Model')
plt.plot([0, 1], [0, 1], linestyle='--', color='gray', linewidth=2,
         label='Perfectly Calibrated')
plt.xlabel('Predicted Probability', fontsize=12)
plt.ylabel('True Frequency', fontsize=12)
plt.title('Calibration Curve', fontsize=14, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.show()

# Calculate Brier Score (measure of calibration error)
from sklearn.metrics import brier_score_loss

brier = brier_score_loss(y_true, y_pred_proba)
print(f"Brier Score: {brier:.4f}")  # Closer to 0 is better
```

### 2. Calibration via Temperature Scaling

Adjust predicted probabilities for better calibration.

**Code Example:**

```python
def temperature_scaling(y_true, y_pred_proba, learning_rate=0.01,
                       n_iterations=100):
    """Apply temperature scaling to calibrate probabilities."""
    from scipy.special import softmax
    from scipy.optimize import minimize

    def nll_loss(temperature):
        """Negative log-likelihood."""
        scaled_probs = 1 / (1 + np.exp(-y_pred_proba / temperature))
        return -np.mean(y_true * np.log(scaled_probs + 1e-15) +
                       (1 - y_true) * np.log(1 - scaled_probs + 1e-15))

    # Find optimal temperature
    result = minimize(nll_loss, x0=[1.0], bounds=[(0.1, 10.0)])
    optimal_temp = result.x[0]

    # Apply scaling
    calibrated_proba = 1 / (1 + np.exp(-y_pred_proba / optimal_temp))

    return calibrated_proba, optimal_temp

# Usage
calibrated_proba, temp = temperature_scaling(y_true, y_pred_proba)

print(f"Optimal Temperature: {temp:.4f}")
print(f"Original Brier Score: {brier_score_loss(y_true, y_pred_proba):.4f}")
print(f"Calibrated Brier Score: {brier_score_loss(y_true, calibrated_proba):.4f}")
```

### 3. Expected Calibration Error (ECE)

Quantifies calibration error across probability bins.

**Code Example:**

```python
def expected_calibration_error(y_true, y_pred_proba, n_bins=10):
    """Calculate Expected Calibration Error."""
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    ece = 0
    bin_accs = []
    bin_confs = []
    bin_counts = []

    for i in range(n_bins):
        mask = (y_pred_proba >= bin_edges[i]) & (y_pred_proba < bin_edges[i+1])

        if mask.sum() > 0:
            bin_accuracy = y_true[mask].mean()
            bin_confidence = y_pred_proba[mask].mean()
            bin_count = mask.sum()

            ece += np.abs(bin_accuracy - bin_confidence) * (bin_count / len(y_true))

            bin_accs.append(bin_accuracy)
            bin_confs.append(bin_confidence)
            bin_counts.append(bin_count)

    return ece, bin_centers, bin_accs, bin_confs, bin_counts

# Usage
ece, bin_centers, accuracies, confidences, counts = expected_calibration_error(
    y_true, y_pred_proba
)

print(f"Expected Calibration Error: {ece:.4f}")

# Visualize
plt.figure(figsize=(10, 6))
plt.bar(bin_centers, np.abs(np.array(accuracies) - np.array(confidences)),
        width=0.08, alpha=0.7, edgecolor='black')
plt.xlabel('Confidence', fontsize=12)
plt.ylabel('Calibration Error', fontsize=12)
plt.title(f'Expected Calibration Error (ECE = {ece:.4f})',
         fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3, axis='y')
plt.show()
```

---

## Fairness Metrics

Ensure model predictions are fair across demographic groups.

### 1. Demographic Parity

Equal prediction rates across groups.

**Formula**: `P(ŷ=1|A=a) = P(ŷ=1|A=a')` for all demographic attributes A

**Code Example:**

```python
def demographic_parity(y_pred, protected_attr, positive_label=1):
    """Check demographic parity."""
    groups = np.unique(protected_attr)
    predictions_by_group = {}

    for group in groups:
        mask = protected_attr == group
        pos_rate = (y_pred[mask] == positive_label).mean()
        predictions_by_group[group] = pos_rate

    disparity = max(predictions_by_group.values()) - min(predictions_by_group.values())

    return predictions_by_group, disparity

# Example: Check fairness across genders
gender = np.random.choice(['M', 'F'], size=len(y_pred))
pred_rates, disparity = demographic_parity(y_pred, gender)

print("Positive Prediction Rate by Gender:")
for group, rate in pred_rates.items():
    print(f"  {group}: {rate:.4f}")
print(f"Disparity: {disparity:.4f}")

# Visualization
plt.figure(figsize=(8, 6))
groups = list(pred_rates.keys())
rates = list(pred_rates.values())
plt.bar(groups, rates, alpha=0.7, edgecolor='black')
plt.ylabel('Positive Prediction Rate', fontsize=12)
plt.title('Demographic Parity Check', fontsize=14, fontweight='bold')
plt.ylim([0, 1])
plt.grid(True, alpha=0.3, axis='y')
plt.show()
```

### 2. Equalized Odds

Equal TPR and FPR across groups.

**Code Example:**

```python
def equalized_odds(y_true, y_pred, protected_attr):
    """Check equalized odds."""
    groups = np.unique(protected_attr)
    metrics_by_group = {}

    for group in groups:
        mask = protected_attr == group
        y_true_group = y_true[mask]
        y_pred_group = y_pred[mask]

        tp = np.sum((y_pred_group == 1) & (y_true_group == 1))
        fp = np.sum((y_pred_group == 1) & (y_true_group == 0))
        fn = np.sum((y_pred_group == 0) & (y_true_group == 1))
        tn = np.sum((y_pred_group == 0) & (y_true_group == 0))

        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

        metrics_by_group[group] = {'TPR': tpr, 'FPR': fpr}

    return metrics_by_group

# Usage
race = np.random.choice(['A', 'B'], size=len(y_pred))
fairness_metrics = equalized_odds(y_true, y_pred, race)

print("Equalized Odds by Race:")
for group, metrics in fairness_metrics.items():
    print(f"  {group}: TPR={metrics['TPR']:.4f}, FPR={metrics['FPR']:.4f}")

# Visualization
groups = list(fairness_metrics.keys())
tprs = [fairness_metrics[g]['TPR'] for g in groups]
fprs = [fairness_metrics[g]['FPR'] for g in groups]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.bar(groups, tprs, alpha=0.7, edgecolor='black', color='blue')
ax1.set_ylabel('True Positive Rate', fontsize=11)
ax1.set_title('TPR by Race', fontsize=12, fontweight='bold')
ax1.set_ylim([0, 1])
ax1.grid(True, alpha=0.3, axis='y')

ax2.bar(groups, fprs, alpha=0.7, edgecolor='black', color='red')
ax2.set_ylabel('False Positive Rate', fontsize=11)
ax2.set_title('FPR by Race', fontsize=12, fontweight='bold')
ax2.set_ylim([0, 1])
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.show()
```

### 3. Disparate Impact Ratio

Ratio of positive prediction rates between groups.

**Code Example:**

```python
def disparate_impact_ratio(y_pred, protected_attr, positive_label=1,
                          reference_group=None):
    """Calculate disparate impact ratio."""
    groups = np.unique(protected_attr)
    pos_rates = {}

    for group in groups:
        mask = protected_attr == group
        pos_rate = (y_pred[mask] == positive_label).mean()
        pos_rates[group] = pos_rate

    if reference_group is None:
        reference_group = groups[0]

    di_ratios = {}
    for group in groups:
        if group != reference_group:
            ratio = pos_rates[group] / pos_rates[reference_group]
            di_ratios[group] = ratio

    return pos_rates, di_ratios

# Usage
pos_rates, di_ratios = disparate_impact_ratio(y_pred, gender)

print("Disparate Impact Analysis:")
print(f"Positive prediction rates: {pos_rates}")
print(f"Disparate Impact Ratios (vs {list(pos_rates.keys())[0]}):")
for group, ratio in di_ratios.items():
    status = "PASS" if 0.8 <= ratio <= 1.25 else "FAIL"
    print(f"  {group}: {ratio:.4f} [{status}]")
```

---

## Error Analysis Techniques

Understand and improve model performance through systematic error analysis.

### 1. Confusion Matrix Analysis

Detailed breakdown of prediction errors.

**Code Example:**

```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

cm = confusion_matrix(y_true, y_pred)

# Detailed analysis
tn, fp, fn, tp = cm.ravel()

print(f"True Negatives: {tn}")
print(f"False Positives: {fp}")
print(f"False Negatives: {fn}")
print(f"True Positives: {tp}")

# Normalized confusion matrix
cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

# Visualize
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Absolute counts
disp = ConfusionMatrixDisplay(cm, display_labels=['Negative', 'Positive'])
disp.plot(ax=axes[0], cmap='Blues', values_format='d')
axes[0].set_title('Confusion Matrix (Counts)', fontsize=12, fontweight='bold')

# Normalized
disp_norm = ConfusionMatrixDisplay(cm_normalized, display_labels=['Negative', 'Positive'])
disp_norm.plot(ax=axes[1], cmap='Blues', values_format='.2f')
axes[1].set_title('Confusion Matrix (Normalized)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.show()
```

### 2. Error Categorization

Categorize errors to understand their source.

**Code Example:**

```python
def categorize_errors(y_true, y_pred, y_pred_proba, threshold=0.5):
    """Categorize prediction errors."""
    errors = {}

    # True positives with high confidence
    high_conf_tp = (y_pred == 1) & (y_true == 1) & (y_pred_proba >= 0.8)
    errors['High Confidence TP'] = high_conf_tp.sum()

    # False positives with high confidence
    high_conf_fp = (y_pred == 1) & (y_true == 0) & (y_pred_proba >= 0.8)
    errors['High Confidence FP'] = high_conf_fp.sum()

    # False negatives with low confidence
    low_conf_fn = (y_pred == 0) & (y_true == 1) & (y_pred_proba < 0.2)
    errors['Low Confidence FN'] = low_conf_fn.sum()

    # Borderline errors (close to threshold)
    borderline_fp = (y_pred == 1) & (y_true == 0) & \
                    (y_pred_proba >= (threshold - 0.1)) & (y_pred_proba < (threshold + 0.1))
    errors['Borderline FP'] = borderline_fp.sum()

    borderline_fn = (y_pred == 0) & (y_true == 1) & \
                    (y_pred_proba >= (threshold - 0.1)) & (y_pred_proba < (threshold + 0.1))
    errors['Borderline FN'] = borderline_fn.sum()

    return errors

# Usage
error_categories = categorize_errors(y_true, y_pred, y_pred_proba)

print("Error Categorization:")
for category, count in error_categories.items():
    print(f"  {category}: {count}")
```

### 3. Residual Analysis (Regression)

Analyze prediction errors for patterns.

**Code Example:**

```python
def residual_analysis(y_true, y_pred, X=None, feature_names=None):
    """Comprehensive residual analysis."""
    residuals = y_true - y_pred

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Residuals vs Predictions
    axes[0, 0].scatter(y_pred, residuals, alpha=0.6)
    axes[0, 0].axhline(y=0, color='r', linestyle='--')
    axes[0, 0].set_xlabel('Predicted Values', fontsize=11)
    axes[0, 0].set_ylabel('Residuals', fontsize=11)
    axes[0, 0].set_title('Residuals vs Predictions', fontsize=12, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)

    # Q-Q plot
    stats.probplot(residuals, dist="norm", plot=axes[0, 1])
    axes[0, 1].set_title('Q-Q Plot', fontsize=12, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)

    # Histogram of residuals
    axes[1, 0].hist(residuals, bins=20, alpha=0.7, edgecolor='black')
    axes[1, 0].set_xlabel('Residuals', fontsize=11)
    axes[1, 0].set_ylabel('Frequency', fontsize=11)
    axes[1, 0].set_title('Distribution of Residuals', fontsize=12, fontweight='bold')
    axes[1, 0].axvline(x=0, color='r', linestyle='--')
    axes[1, 0].grid(True, alpha=0.3, axis='y')

    # Scale-location plot
    standardized_residuals = (residuals - residuals.mean()) / residuals.std()
    axes[1, 1].scatter(y_pred, np.sqrt(np.abs(standardized_residuals)), alpha=0.6)
    axes[1, 1].set_xlabel('Predicted Values', fontsize=11)
    axes[1, 1].set_ylabel('√|Standardized Residuals|', fontsize=11)
    axes[1, 1].set_title('Scale-Location Plot', fontsize=12, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    # Statistical tests
    _, normality_p = stats.shapiro(residuals[:min(5000, len(residuals))])
    print(f"Normality Test p-value: {normality_p:.4f}")
    print(f"  {'PASS' if normality_p > 0.05 else 'FAIL'}: Residuals are {'normal' if normality_p > 0.05 else 'NOT normal'}")

# Usage
residual_analysis(y_true, y_pred)
```

---

## Best Practices

### 1. Metric Selection Guidelines

| Scenario | Primary Metric | Secondary Metrics |
|----------|---|---|
| Balanced Classification | F1, Accuracy | Precision, Recall |
| Imbalanced Classification | F1, PR-AUC | Recall, Precision |
| Medical Diagnosis | Recall | Precision, Specificity |
| Spam Detection | Precision | Recall, ROC-AUC |
| Regression | RMSE or MAE | R², MAPE |
| Time Series | RMSE + MAE | MAPE, R² |

### 2. Evaluation Workflow

```python
def comprehensive_model_evaluation(model, X_train, X_test, y_train, y_test,
                                  task='classification', model_name='Model'):
    """Complete evaluation workflow."""
    import time
    from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                                f1_score, roc_auc_score, mean_squared_error, r2_score)

    print(f"\n{'='*60}")
    print(f"MODEL EVALUATION: {model_name}")
    print(f"{'='*60}\n")

    # Train time
    start = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start
    print(f"Training Time: {train_time:.4f}s")

    # Inference time
    start = time.time()
    predictions = model.predict(X_test)
    inference_time = time.time() - start
    print(f"Inference Time: {inference_time:.6f}s")

    if task == 'classification':
        # Classification metrics
        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions, zero_division=0)
        recall = recall_score(y_test, predictions, zero_division=0)
        f1 = f1_score(y_test, predictions, zero_division=0)

        print(f"\nClassification Metrics:")
        print(f"  Accuracy:  {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  F1 Score:  {f1:.4f}")

        # Probability-based metrics
        if hasattr(model, 'predict_proba'):
            y_proba = model.predict_proba(X_test)[:, 1]
            roc_auc = roc_auc_score(y_test, y_proba)
            print(f"  ROC-AUC:   {roc_auc:.4f}")

            # Confidence interval
            scores = cross_val_score(model, X_test, y_test, cv=5, scoring='roc_auc')
            print(f"  ROC-AUC CI: [{scores.mean() - 1.96*scores.std():.4f}, "
                  f"{scores.mean() + 1.96*scores.std():.4f}]")

    else:  # Regression
        mse = mean_squared_error(y_test, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)

        print(f"\nRegression Metrics:")
        print(f"  MSE:  {mse:.4f}")
        print(f"  RMSE: {rmse:.4f}")
        print(f"  MAE:  {mae:.4f}")
        print(f"  R²:   {r2:.4f}")

    print(f"\n{'='*60}\n")

# Usage
comprehensive_model_evaluation(model, X_train, X_test, y_train, y_test,
                              task='classification', model_name='Random Forest')
```

### 3. Common Pitfalls to Avoid

**1. Data Leakage**
```python
# WRONG: Scaling before split
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y)

# CORRECT: Scale after split
X_train, X_test, y_train, y_test = train_test_split(X, y)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

**2. Using Test Set for Hyperparameter Tuning**
```python
# WRONG
for param in param_grid:
    model.set_params(**param)
    model.fit(X_train, y_train)
    score = evaluate(X_test, y_test)  # Tuning on test set!

# CORRECT
X_train_split, X_val, y_train_split, y_val = train_test_split(X_train, y_train)
for param in param_grid:
    model.set_params(**param)
    model.fit(X_train_split, y_train_split)
    score = evaluate(X_val, y_val)  # Tune on validation set
```

**3. Metric-Data Mismatch**
```python
# WRONG: Using accuracy for imbalanced data
y_imbalanced = np.array([1]*95 + [0]*5)  # 95% positive class
accuracy = accuracy_score(y_imbalanced, y_pred)  # Misleading!

# CORRECT
f1 = f1_score(y_imbalanced, y_pred)
pr_auc = auc(recalls, precisions)
```

### 4. Reproducibility Best Practices

```python
import random
import numpy as np
from sklearn.model_selection import train_test_split

def set_seed(seed=42):
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    # For TensorFlow/PyTorch if used:
    # tf.random.set_seed(seed)
    # torch.manual_seed(seed)

# Usage
set_seed(42)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
model = RandomForestClassifier(random_state=42)
```

---

## Complete Evaluation Pipeline

Comprehensive example combining all techniques:

```python
class ModelEvaluator:
    """Complete model evaluation pipeline."""

    def __init__(self, model, X_train, X_test, y_train, y_test, task='classification'):
        self.model = model
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.task = task
        self.results = {}

    def train_and_predict(self):
        """Train model and generate predictions."""
        self.model.fit(self.X_train, self.y_train)
        self.y_pred = self.model.predict(self.X_test)

        if hasattr(self.model, 'predict_proba'):
            self.y_pred_proba = self.model.predict_proba(self.X_test)[:, 1]

        return self

    def evaluate_classification(self):
        """Evaluate classification model."""
        from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                                    f1_score, roc_auc_score, precision_recall_curve, auc)

        self.results['accuracy'] = accuracy_score(self.y_test, self.y_pred)
        self.results['precision'] = precision_score(self.y_test, self.y_pred, zero_division=0)
        self.results['recall'] = recall_score(self.y_test, self.y_pred, zero_division=0)
        self.results['f1'] = f1_score(self.y_test, self.y_pred, zero_division=0)

        if hasattr(self, 'y_pred_proba'):
            self.results['roc_auc'] = roc_auc_score(self.y_test, self.y_pred_proba)
            precisions, recalls, _ = precision_recall_curve(self.y_test, self.y_pred_proba)
            self.results['pr_auc'] = auc(recalls, precisions)

        return self

    def evaluate_regression(self):
        """Evaluate regression model."""
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

        self.results['mae'] = mean_absolute_error(self.y_test, self.y_pred)
        self.results['mse'] = mean_squared_error(self.y_test, self.y_pred)
        self.results['rmse'] = np.sqrt(self.results['mse'])
        self.results['r2'] = r2_score(self.y_test, self.y_pred)

        return self

    def cross_validate(self, cv=5):
        """Perform cross-validation."""
        from sklearn.model_selection import cross_val_score

        if self.task == 'classification':
            scoring = 'roc_auc'
        else:
            scoring = 'r2'

        cv_scores = cross_val_score(self.model, self.X_train, self.y_train,
                                   cv=cv, scoring=scoring)

        self.results[f'cv_{scoring}_mean'] = cv_scores.mean()
        self.results[f'cv_{scoring}_std'] = cv_scores.std()

        return self

    def print_results(self):
        """Print evaluation results."""
        print("\nEvaluation Results:")
        print("=" * 50)
        for metric, value in self.results.items():
            if isinstance(value, float):
                print(f"{metric:.<40} {value:.4f}")
        print("=" * 50)

        return self

# Usage
evaluator = ModelEvaluator(model, X_train, X_test, y_train, y_test,
                          task='classification')
evaluator.train_and_predict()
evaluator.evaluate_classification()
evaluator.cross_validate(cv=5)
evaluator.print_results()
```

---

## References and Further Reading

- Scikit-learn Documentation: https://scikit-learn.org
- ROC and AUC: https://en.wikipedia.org/wiki/Receiver_operating_characteristic
- Calibration: Niculescu-Mizil & Caruana (2005)
- Fairness in ML: Mitchell et al. (2019)
- Cross-Validation: Arlot & Celisse (2010)

---

**Last Updated:** November 2024
**Author:** Data Science & AI Team
**Version:** 1.0
