# Model Analysis & Optimization Template

## Purpose
Comprehensively analyze ML model performance, debug issues, explain predictions, and optimize models for production deployment. Follows best practices from Google's ML Testing, Meta's Responsible AI, and industry-leading model debugging techniques.

## When to Use

- Model underperforming on validation/test data
- Need to understand model predictions and behavior
- Debugging training issues (loss not decreasing, NaN values, etc.)
- Optimizing inference speed or memory usage
- Preparing model for production deployment
- Explaining model decisions for stakeholders
- Auditing model for bias and fairness

## Prerequisites

- [ ] Trained model checkpoint available
- [ ] Access to training, validation, and test datasets
- [ ] Training logs and metrics
- [ ] Model architecture definition
- [ ] Expected performance baselines

## Analysis Framework

### Phase 1: Initial Health Check

**Objective**: Quickly identify obvious issues and verify model basics

#### 1.1 Model Inspection

```python
import torch
import torch.nn as nn
from typing import Dict, Any
import numpy as np

def inspect_model(model: nn.Module) -> Dict[str, Any]:
    """
    Perform basic model health checks.

    Args:
        model: PyTorch model to inspect

    Returns:
        Dictionary of inspection results
    """
    results = {}

    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    results["total_parameters"] = total_params
    results["trainable_parameters"] = trainable_params
    results["parameter_size_mb"] = total_params * 4 / (1024 ** 2)  # Assuming float32

    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    print(f"Model size: {results['parameter_size_mb']:.2f} MB")

    # Check for frozen layers
    frozen_layers = []
    for name, param in model.named_parameters():
        if not param.requires_grad:
            frozen_layers.append(name)

    results["frozen_layers"] = frozen_layers
    if frozen_layers:
        print(f"⚠️  Found {len(frozen_layers)} frozen layers")

    # Check parameter initialization
    zero_params = []
    for name, param in model.named_parameters():
        if torch.all(param == 0):
            zero_params.append(name)

    results["zero_initialized"] = zero_params
    if zero_params:
        print(f"⚠️  Warning: {len(zero_params)} layers are zero-initialized: {zero_params}")

    # Check for NaN or Inf
    nan_params = []
    for name, param in model.named_parameters():
        if torch.isnan(param).any() or torch.isinf(param).any():
            nan_params.append(name)

    results["nan_or_inf_params"] = nan_params
    if nan_params:
        print(f"❌ Critical: NaN or Inf detected in: {nan_params}")

    return results
```

**Check List**:
- [ ] Model loads successfully
- [ ] Parameter count reasonable for task
- [ ] No NaN or Inf values in parameters
- [ ] Expected layers are trainable
- [ ] Model size appropriate for deployment target

#### 1.2 Training Metrics Analysis

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_training_metrics(metrics_file: str):
    """
    Analyze training history for issues.

    Args:
        metrics_file: Path to CSV file with training metrics
    """
    df = pd.read_csv(metrics_file)

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))

    # Plot 1: Loss curves
    ax = axes[0, 0]
    ax.plot(df["epoch"], df["train_loss"], label="Train Loss", linewidth=2)
    ax.plot(df["epoch"], df["val_loss"], label="Val Loss", linewidth=2)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title("Training and Validation Loss")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Identify issues
    if df["train_loss"].iloc[-1] > df["train_loss"].iloc[0]:
        print("⚠️  Training loss not decreasing!")

    if df["val_loss"].iloc[-5:].mean() > df["val_loss"].iloc[:5].mean():
        print("⚠️  Validation loss increased over time - possible overfitting")

    train_val_gap = df["val_loss"].iloc[-1] - df["train_loss"].iloc[-1]
    if train_val_gap > 0.5:
        print(f"⚠️  Large train-val gap ({train_val_gap:.3f}) - likely overfitting")

    # Plot 2: Learning rate
    if "learning_rate" in df.columns:
        ax = axes[0, 1]
        ax.plot(df["epoch"], df["learning_rate"])
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Learning Rate")
        ax.set_title("Learning Rate Schedule")
        ax.set_yscale("log")
        ax.grid(True, alpha=0.3)

    # Plot 3: Gradient norms
    if "grad_norm" in df.columns:
        ax = axes[1, 0]
        ax.plot(df["epoch"], df["grad_norm"])
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Gradient Norm")
        ax.set_title("Gradient Norm Over Time")
        ax.grid(True, alpha=0.3)

        if df["grad_norm"].max() > 100:
            print("⚠️  Very large gradient norms detected - consider gradient clipping")

    # Plot 4: Metrics (accuracy, F1, etc.)
    ax = axes[1, 1]
    metric_cols = [col for col in df.columns if col.startswith("val_") and col != "val_loss"]
    for col in metric_cols:
        ax.plot(df["epoch"], df[col], label=col, linewidth=2)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Metric Value")
    ax.set_title("Validation Metrics")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("training_analysis.png", dpi=300, bbox_inches="tight")
    print("📊 Training analysis saved to training_analysis.png")
```

**Diagnose Issues**:
- [ ] Training loss decreasing consistently
- [ ] Validation loss following train loss (not diverging)
- [ ] No sudden spikes in loss
- [ ] Learning rate schedule appropriate
- [ ] Gradient norms stable (no explosion/vanishing)

---

### Phase 2: Performance Deep Dive

**Objective**: Understand where and why the model fails

#### 2.1 Comprehensive Error Analysis

```python
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_curve,
    auc,
    precision_recall_curve,
)
import numpy as np

def comprehensive_evaluation(
    model: nn.Module,
    test_loader,
    device: str,
    class_names: list,
):
    """
    Perform comprehensive model evaluation.

    Args:
        model: Model to evaluate
        test_loader: Test data loader
        device: Device (cuda/cpu)
        class_names: List of class names

    Returns:
        Dictionary of results and visualizations
    """
    model.eval()

    all_preds = []
    all_probs = []
    all_targets = []
    all_features = []  # For embedding analysis

    with torch.no_grad():
        for batch in test_loader:
            if len(batch) == 2:
                data, target = batch
            else:
                data, target = batch["input"], batch["target"]

            data = data.to(device)
            output = model(data)

            probs = torch.softmax(output, dim=1)
            preds = output.argmax(dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
            all_targets.extend(target.numpy())

    all_preds = np.array(all_preds)
    all_probs = np.array(all_probs)
    all_targets = np.array(all_targets)

    # 1. Classification Report
    print("=" * 80)
    print("CLASSIFICATION REPORT")
    print("=" * 80)
    report = classification_report(
        all_targets,
        all_preds,
        target_names=class_names,
        digits=4,
    )
    print(report)

    # 2. Confusion Matrix
    cm = confusion_matrix(all_targets, all_preds)
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
    )
    plt.title("Confusion Matrix")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()
    plt.savefig("confusion_matrix.png", dpi=300, bbox_inches="tight")

    # Analyze confusion matrix
    print("\n" + "=" * 80)
    print("CONFUSION MATRIX ANALYSIS")
    print("=" * 80)

    # Find most confused pairs
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
    np.fill_diagonal(cm_norm, 0)  # Ignore diagonal

    most_confused = []
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            if i != j and cm_norm[i, j] > 0.1:  # >10% confusion rate
                most_confused.append((class_names[i], class_names[j], cm_norm[i, j]))

    most_confused.sort(key=lambda x: x[2], reverse=True)

    if most_confused:
        print("Most confused class pairs (>10% confusion rate):")
        for true_class, pred_class, rate in most_confused[:10]:
            print(f"  {true_class} → {pred_class}: {rate:.1%}")
    else:
        print("✓ No significant class confusion detected")

    # 3. ROC Curves (for binary or multiclass)
    n_classes = len(class_names)

    if n_classes == 2:
        # Binary classification
        fpr, tpr, _ = roc_curve(all_targets, all_probs[:, 1])
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, linewidth=2, label=f"ROC (AUC = {roc_auc:.3f})")
        plt.plot([0, 1], [0, 1], "k--", linewidth=1)
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curve")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig("roc_curve.png", dpi=300, bbox_inches="tight")

    else:
        # Multiclass - one ROC per class
        fig, ax = plt.subplots(figsize=(10, 8))

        for i, class_name in enumerate(class_names):
            y_true_binary = (all_targets == i).astype(int)
            y_score = all_probs[:, i]

            fpr, tpr, _ = roc_curve(y_true_binary, y_score)
            roc_auc = auc(fpr, tpr)

            ax.plot(fpr, tpr, linewidth=2, label=f"{class_name} (AUC = {roc_auc:.3f})")

        ax.plot([0, 1], [0, 1], "k--", linewidth=1)
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.set_title("ROC Curves (One-vs-Rest)")
        ax.legend(loc="lower right")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig("roc_curves_multiclass.png", dpi=300, bbox_inches="tight")

    # 4. Calibration Analysis
    analyze_calibration(all_targets, all_probs, class_names)

    # 5. Error Analysis by Confidence
    analyze_errors_by_confidence(all_targets, all_preds, all_probs)

    return {
        "predictions": all_preds,
        "probabilities": all_probs,
        "targets": all_targets,
    }


def analyze_calibration(y_true, y_prob, class_names):
    """
    Analyze model calibration (are predicted probabilities accurate?).
    """
    from sklearn.calibration import calibration_curve

    print("\n" + "=" * 80)
    print("CALIBRATION ANALYSIS")
    print("=" * 80)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Reliability diagram
    ax = axes[0]
    for i, class_name in enumerate(class_names):
        y_true_binary = (y_true == i).astype(int)
        y_score = y_prob[:, i]

        fraction_of_positives, mean_predicted_value = calibration_curve(
            y_true_binary, y_score, n_bins=10, strategy="uniform"
        )

        ax.plot(
            mean_predicted_value,
            fraction_of_positives,
            marker="o",
            linewidth=2,
            label=class_name,
        )

    ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Perfect calibration")
    ax.set_xlabel("Mean Predicted Probability")
    ax.set_ylabel("Fraction of Positives")
    ax.set_title("Reliability Diagram")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Confidence histogram
    ax = axes[1]
    max_probs = y_prob.max(axis=1)
    ax.hist(max_probs, bins=20, edgecolor="black")
    ax.set_xlabel("Confidence (Max Probability)")
    ax.set_ylabel("Count")
    ax.set_title("Prediction Confidence Distribution")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("calibration_analysis.png", dpi=300, bbox_inches="tight")

    # Calculate expected calibration error (ECE)
    ece = calculate_ece(y_true, y_prob)
    print(f"Expected Calibration Error (ECE): {ece:.4f}")
    if ece > 0.1:
        print("⚠️  Model is poorly calibrated - consider temperature scaling")


def calculate_ece(y_true, y_prob, n_bins=10):
    """Calculate Expected Calibration Error."""
    confidences = y_prob.max(axis=1)
    predictions = y_prob.argmax(axis=1)
    accuracies = predictions == y_true

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]

        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = in_bin.mean()

        if prop_in_bin > 0:
            accuracy_in_bin = accuracies[in_bin].mean()
            avg_confidence_in_bin = confidences[in_bin].mean()
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

    return ece


def analyze_errors_by_confidence(y_true, y_pred, y_prob):
    """
    Analyze where model makes errors based on confidence.
    """
    print("\n" + "=" * 80)
    print("ERROR ANALYSIS BY CONFIDENCE")
    print("=" * 80)

    confidences = y_prob.max(axis=1)
    correct = y_pred == y_true

    # Split into confidence buckets
    high_conf_mask = confidences > 0.9
    med_conf_mask = (confidences > 0.5) & (confidences <= 0.9)
    low_conf_mask = confidences <= 0.5

    print(f"\nHigh confidence (>0.9): {high_conf_mask.sum()} samples")
    print(f"  Accuracy: {correct[high_conf_mask].mean():.4f}")
    print(f"  Error rate: {(1 - correct[high_conf_mask].mean()):.4f}")

    print(f"\nMedium confidence (0.5-0.9): {med_conf_mask.sum()} samples")
    print(f"  Accuracy: {correct[med_conf_mask].mean():.4f}")

    print(f"\nLow confidence (<0.5): {low_conf_mask.sum()} samples")
    if low_conf_mask.sum() > 0:
        print(f"  Accuracy: {correct[low_conf_mask].mean():.4f}")
        print(f"⚠️  Model is uncertain on {low_conf_mask.sum()} samples - review these")
```

#### 2.2 Feature Importance & Explainability

```python
import shap
from captum.attr import IntegratedGradients, LayerGradCam

def explain_predictions(model, test_loader, device, method="shap"):
    """
    Generate explanations for model predictions.

    Args:
        model: Model to explain
        test_loader: Test data
        device: Device
        method: Explanation method (shap, integrated_gradients, gradcam)
    """
    model.eval()

    # Get sample batch
    sample_batch = next(iter(test_loader))
    if len(sample_batch) == 2:
        inputs, targets = sample_batch
    else:
        inputs, targets = sample_batch["input"], sample_batch["target"]

    inputs = inputs[:8].to(device)  # Analyze first 8 samples
    targets = targets[:8]

    if method == "shap":
        # SHAP explanations
        background = inputs[:4]
        test_samples = inputs[4:8]

        explainer = shap.DeepExplainer(model, background)
        shap_values = explainer.shap_values(test_samples)

        # Visualize
        shap.image_plot(shap_values, test_samples.cpu().numpy())

    elif method == "integrated_gradients":
        # Integrated Gradients
        ig = IntegratedGradients(model)

        attributions = ig.attribute(
            inputs,
            target=targets.to(device),
            n_steps=50,
        )

        # Visualize attributions
        visualize_attributions(inputs, attributions)

    elif method == "gradcam":
        # Grad-CAM (for CNNs)
        layer = model.layer4  # Adjust based on your model
        gradcam = LayerGradCam(model, layer)

        attributions = gradcam.attribute(
            inputs,
            target=targets.to(device),
        )

        visualize_gradcam(inputs, attributions)


def analyze_feature_importance_tabular(model, X_test, feature_names):
    """
    Analyze feature importance for tabular data using SHAP.

    Args:
        model: Trained model
        X_test: Test features
        feature_names: Names of features
    """
    # SHAP TreeExplainer (for tree-based models)
    # or KernelExplainer (model-agnostic)

    explainer = shap.Explainer(model)
    shap_values = explainer(X_test)

    # Summary plot
    shap.summary_plot(shap_values, X_test, feature_names=feature_names)

    # Feature importance
    shap.summary_plot(shap_values, X_test, plot_type="bar", feature_names=feature_names)

    # Dependence plots for top features
    top_features = np.abs(shap_values.values).mean(0).argsort()[-5:][::-1]

    for idx in top_features:
        shap.dependence_plot(idx, shap_values.values, X_test, feature_names=feature_names)

    print("\nTop 10 Most Important Features:")
    feature_importance = np.abs(shap_values.values).mean(0)
    top_10_idx = feature_importance.argsort()[-10:][::-1]

    for rank, idx in enumerate(top_10_idx, 1):
        print(f"{rank}. {feature_names[idx]}: {feature_importance[idx]:.4f}")
```

#### 2.3 Slice-Based Analysis

```python
def analyze_performance_by_slice(
    predictions,
    targets,
    metadata,
    slice_feature: str,
):
    """
    Analyze model performance across different data slices.

    Args:
        predictions: Model predictions
        targets: Ground truth labels
        metadata: DataFrame with metadata for each sample
        slice_feature: Feature to slice by (e.g., 'age_group', 'gender')
    """
    from sklearn.metrics import accuracy_score, f1_score

    print(f"\n{'=' * 80}")
    print(f"PERFORMANCE ANALYSIS BY {slice_feature.upper()}")
    print(f"{'=' * 80}\n")

    unique_values = metadata[slice_feature].unique()

    results = []
    for value in unique_values:
        mask = metadata[slice_feature] == value
        slice_preds = predictions[mask]
        slice_targets = targets[mask]

        if len(slice_preds) == 0:
            continue

        accuracy = accuracy_score(slice_targets, slice_preds)
        f1 = f1_score(slice_targets, slice_preds, average="weighted")

        results.append({
            "slice": value,
            "count": len(slice_preds),
            "accuracy": accuracy,
            "f1": f1,
        })

        print(f"{value}:")
        print(f"  Samples: {len(slice_preds)}")
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  F1 Score: {f1:.4f}")
        print()

    # Identify worst performing slices
    results_df = pd.DataFrame(results)
    worst_slices = results_df.nsmallest(3, "accuracy")

    print("⚠️  Worst performing slices:")
    print(worst_slices.to_string(index=False))

    # Check for significant performance gaps
    max_acc = results_df["accuracy"].max()
    min_acc = results_df["accuracy"].min()
    gap = max_acc - min_acc

    if gap > 0.1:
        print(f"\n⚠️  Large performance gap detected: {gap:.2%}")
        print("    Consider collecting more data for underperforming slices")
        print("    or using techniques like class reweighting")

    # Visualize
    plt.figure(figsize=(12, 6))
    x = range(len(results_df))
    plt.bar(x, results_df["accuracy"], alpha=0.7, label="Accuracy")
    plt.bar(x, results_df["f1"], alpha=0.7, label="F1 Score")
    plt.xticks(x, results_df["slice"], rotation=45, ha="right")
    plt.ylabel("Score")
    plt.title(f"Performance by {slice_feature}")
    plt.legend()
    plt.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(f"performance_by_{slice_feature}.png", dpi=300, bbox_inches="tight")
```

---

### Phase 3: Inference Optimization

**Objective**: Optimize model for fast, efficient inference

#### 3.1 Latency Profiling

```python
import time
from torch.profiler import profile, ProfilerActivity

def profile_inference(model, sample_input, device, warmup_runs=10, test_runs=100):
    """
    Profile model inference latency.

    Args:
        model: Model to profile
        sample_input: Sample input tensor
        device: Device (cuda/cpu)
        warmup_runs: Number of warmup iterations
        test_runs: Number of test iterations

    Returns:
        Dictionary with latency statistics
    """
    model.eval()
    sample_input = sample_input.to(device)

    # Warmup
    with torch.no_grad():
        for _ in range(warmup_runs):
            _ = model(sample_input)

    # Measure latency
    latencies = []

    with torch.no_grad():
        for _ in range(test_runs):
            if device == "cuda":
                torch.cuda.synchronize()

            start = time.perf_counter()
            _ = model(sample_input)

            if device == "cuda":
                torch.cuda.synchronize()

            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # Convert to ms

    latencies = np.array(latencies)

    results = {
        "mean_ms": latencies.mean(),
        "std_ms": latencies.std(),
        "p50_ms": np.percentile(latencies, 50),
        "p95_ms": np.percentile(latencies, 95),
        "p99_ms": np.percentile(latencies, 99),
        "min_ms": latencies.min(),
        "max_ms": latencies.max(),
    }

    print("\n" + "=" * 80)
    print("INFERENCE LATENCY PROFILE")
    print("=" * 80)
    print(f"Mean: {results['mean_ms']:.2f} ms")
    print(f"Std:  {results['std_ms']:.2f} ms")
    print(f"P50:  {results['p50_ms']:.2f} ms")
    print(f"P95:  {results['p95_ms']:.2f} ms")
    print(f"P99:  {results['p99_ms']:.2f} ms")

    # Throughput
    batch_size = sample_input.shape[0]
    throughput = (batch_size * 1000) / results["mean_ms"]
    print(f"\nThroughput: {throughput:.1f} samples/sec")

    return results


def detailed_profiling(model, sample_input, device):
    """
    Detailed profiling with PyTorch Profiler.
    """
    with profile(
        activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
        record_shapes=True,
        profile_memory=True,
        with_stack=True,
    ) as prof:
        with torch.no_grad():
            _ = model(sample_input.to(device))

    # Print results
    print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=20))

    # Export trace
    prof.export_chrome_trace("model_trace.json")
    print("\n📊 Detailed trace saved to model_trace.json")
    print("   View at chrome://tracing")
```

#### 3.2 Memory Analysis

```python
def analyze_memory_usage(model, sample_input, device):
    """
    Analyze memory usage during inference.

    Args:
        model: Model to analyze
        sample_input: Sample input
        device: Device (cuda/cpu)

    Returns:
        Memory statistics
    """
    if device != "cuda":
        print("⚠️  Memory analysis only available for CUDA")
        return

    model.eval()
    sample_input = sample_input.to(device)

    torch.cuda.reset_peak_memory_stats()
    torch.cuda.empty_cache()

    # Measure memory
    mem_before = torch.cuda.memory_allocated() / (1024 ** 2)  # MB

    with torch.no_grad():
        output = model(sample_input)

    mem_after = torch.cuda.memory_allocated() / (1024 ** 2)
    mem_peak = torch.cuda.max_memory_allocated() / (1024 ** 2)

    print("\n" + "=" * 80)
    print("MEMORY USAGE ANALYSIS")
    print("=" * 80)
    print(f"Memory before: {mem_before:.2f} MB")
    print(f"Memory after:  {mem_after:.2f} MB")
    print(f"Peak memory:   {mem_peak:.2f} MB")
    print(f"Memory delta:  {mem_after - mem_before:.2f} MB")

    # Model parameter memory
    param_memory = sum(p.numel() * p.element_size() for p in model.parameters()) / (1024 ** 2)
    print(f"\nModel parameters: {param_memory:.2f} MB")

    # Activation memory
    activation_memory = mem_peak - param_memory
    print(f"Activations (estimated): {activation_memory:.2f} MB")

    return {
        "param_memory_mb": param_memory,
        "activation_memory_mb": activation_memory,
        "peak_memory_mb": mem_peak,
    }
```

#### 3.3 Optimization Recommendations

```python
def recommend_optimizations(
    model,
    latency_results,
    memory_results,
    target_latency_ms=100,
    target_memory_mb=500,
):
    """
    Recommend optimizations based on profiling results.

    Args:
        model: Model
        latency_results: Latency profiling results
        memory_results: Memory profiling results
        target_latency_ms: Target latency (ms)
        target_memory_mb: Target memory (MB)

    Returns:
        List of recommended optimizations
    """
    recommendations = []

    print("\n" + "=" * 80)
    print("OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)

    # Latency optimizations
    current_latency = latency_results["p95_ms"]
    if current_latency > target_latency_ms:
        speedup_needed = current_latency / target_latency_ms

        print(f"\n⚠️  Latency ({current_latency:.1f}ms) exceeds target ({target_latency_ms}ms)")
        print(f"    Need {speedup_needed:.1f}x speedup\n")

        recommendations.append({
            "priority": "HIGH",
            "optimization": "Quantization (INT8)",
            "expected_speedup": "2-4x",
            "complexity": "Low",
            "code": "Use torch.quantization or ONNX Runtime",
        })

        recommendations.append({
            "priority": "HIGH",
            "optimization": "ONNX + TensorRT",
            "expected_speedup": "2-5x",
            "complexity": "Medium",
            "code": "Convert to ONNX, optimize with TensorRT",
        })

        if speedup_needed > 3:
            recommendations.append({
                "priority": "CRITICAL",
                "optimization": "Model architecture changes",
                "expected_speedup": "Varies",
                "complexity": "High",
                "code": "Consider MobileNet, EfficientNet, DistilBERT, etc.",
            })

    # Memory optimizations
    current_memory = memory_results.get("peak_memory_mb", 0)
    if current_memory > target_memory_mb:
        print(f"\n⚠️  Memory ({current_memory:.1f}MB) exceeds target ({target_memory_mb}MB)\n")

        recommendations.append({
            "priority": "HIGH",
            "optimization": "Quantization",
            "memory_reduction": "4x (FP32 -> INT8)",
            "complexity": "Low",
        })

        recommendations.append({
            "priority": "MEDIUM",
            "optimization": "Pruning",
            "memory_reduction": "2-5x (depends on sparsity)",
            "complexity": "Medium",
        })

    # General recommendations
    recommendations.append({
        "priority": "LOW",
        "optimization": "torch.compile (PyTorch 2.0+)",
        "expected_speedup": "1.2-2x",
        "complexity": "Very Low",
        "code": "model = torch.compile(model)",
    })

    recommendations.append({
        "priority": "MEDIUM",
        "optimization": "Batching",
        "expected_speedup": "Varies with batch size",
        "complexity": "Low",
        "code": "Increase batch size for throughput",
    })

    # Print recommendations
    for rec in sorted(recommendations, key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}[rec["priority"]]):
        print(f"\n[{rec['priority']}] {rec['optimization']}")
        for key, value in rec.items():
            if key != "priority" and key != "optimization":
                print(f"  {key}: {value}")

    return recommendations
```

---

## Success Criteria

Analysis is complete when:

- [ ] **Health Check**: Model loads and basic checks pass
- [ ] **Performance**: Metrics calculated and compared to baselines
- [ ] **Errors**: Error patterns identified and documented
- [ ] **Explanations**: Model predictions explainable
- [ ] **Slices**: Performance analyzed across data segments
- [ ] **Optimization**: Profiling complete, optimizations recommended
- [ ] **Documentation**: Findings documented with visualizations

## Output Format

Present findings in this structure:

### Executive Summary
- 2-3 sentence overview
- Key metrics vs baselines
- Critical issues (if any)

### Detailed Analysis

#### Performance Metrics
- Overall metrics table
- Comparison to baseline
- Statistical significance tests

#### Error Analysis
- Confusion matrix highlights
- Most confused class pairs
- Error patterns

#### Model Behavior
- Calibration assessment
- Confidence analysis
- Feature importance (top 10)

#### Performance by Segment
- Slice-based analysis results
- Worst performing segments
- Fairness assessment

#### Optimization Opportunities
- Latency profiling results
- Memory usage analysis
- Recommended optimizations (prioritized)

### Action Items
1. High priority fixes
2. Medium priority improvements
3. Low priority enhancements

## Best Practices Reference

### From Google's ML Testing
- Test training/serving skew
- Test for NaN and Inf values
- Validate on multiple slices
- Check model calibration

### From Meta's Responsible AI
- Analyze fairness across demographics
- Provide model explanations
- Document limitations
- Test for adversarial robustness

### Industry Standards
- SHAP for feature importance
- Calibration curves for probability quality
- Slice-based analysis for fairness
- Profiling for optimization

## Troubleshooting Common Issues

**Issue: Model not learning (flat loss)**
- Check data loading (are labels correct?)
- Verify loss computation
- Check learning rate (try LR finder)
- Simplify model to rule out architecture issues

**Issue: Training loss good, val loss bad (overfitting)**
- Add regularization (dropout, weight decay)
- More training data or data augmentation
- Reduce model capacity
- Early stopping

**Issue: Both losses high (underfitting)**
- Increase model capacity
- Train longer
- Reduce regularization
- Check for bugs in model implementation

**Issue: NaN loss during training**
- Gradient explosion - add gradient clipping
- Learning rate too high - reduce LR
- Check for division by zero in loss
- Use mixed precision carefully

**Issue: Slow inference**
- Quantize model (INT8)
- Convert to ONNX/TensorRT
- Use torch.compile
- Batch requests
- Profile and optimize bottlenecks
