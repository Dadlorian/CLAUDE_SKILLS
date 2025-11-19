# ML Pipeline Automation Template

## Purpose
Automate end-to-end machine learning workflows from data ingestion to model deployment, following industry best practices from companies like Uber (Michelangelo), Airbnb (Bighead), and Netflix (Metaflow).

## Prerequisites
- [ ] Training data available and accessible
- [ ] Compute resources defined (local, cloud, cluster)
- [ ] Success metrics and evaluation criteria established
- [ ] Model deployment target identified
- [ ] MLOps tools selected (MLflow, Kubeflow, Airflow, etc.)

## Configuration

Set these parameters before pipeline execution:

```python
pipeline_config = {
    # Data Configuration
    "data_source": "s3://bucket/data",  # or local path, database URI
    "data_format": "parquet",  # parquet, csv, tfrecord, etc.
    "train_split": 0.8,
    "val_split": 0.1,
    "test_split": 0.1,

    # Model Configuration
    "model_type": "transformer",  # or "resnet", "xgboost", etc.
    "model_config": {...},
    "pretrained_checkpoint": None,  # or path to checkpoint

    # Training Configuration
    "batch_size": 32,
    "learning_rate": 1e-4,
    "epochs": 10,
    "optimizer": "adamw",
    "mixed_precision": True,

    # Hyperparameter Search
    "hp_search_enabled": True,
    "hp_search_trials": 20,
    "hp_search_strategy": "bayesian",  # grid, random, bayesian

    # Monitoring & Logging
    "experiment_tracking": "mlflow",  # wandb, tensorboard, neptune
    "logging_steps": 100,
    "checkpoint_steps": 1000,
    "early_stopping_patience": 3,

    # Deployment
    "deployment_target": "sagemaker",  # kubernetes, local, torchserve
    "auto_deploy": False,
    "deploy_threshold": 0.05,  # Deploy if metric improves by 5%

    # Orchestration
    "orchestrator": "kubeflow",  # airflow, prefect, metaflow
    "parallel_workers": 4,
    "retry_policy": {"max_retries": 3, "backoff": "exponential"},
}
```

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ML Pipeline Overview                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Data Ingestion → Data Validation → Feature Engineering     │
│       ↓                                                      │
│  Data Splitting → Training → Evaluation → Model Validation  │
│       ↓                                                      │
│  Model Registry → Deployment → Monitoring                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Workflow

### Phase 1: Data Pipeline

**Objective**: Ingest, validate, and prepare data for training

#### 1.1 Data Ingestion

```python
from dataclasses import dataclass
from typing import Optional, List
import pandas as pd
from great_expectations.dataset import PandasDataset

@dataclass
class DataSource:
    """Configuration for data source."""
    source_uri: str
    format: str = "parquet"
    columns: Optional[List[str]] = None
    filters: Optional[dict] = None

def ingest_data(config: DataSource) -> pd.DataFrame:
    """
    Ingest data from source with validation.

    Args:
        config: Data source configuration

    Returns:
        Validated DataFrame

    Example:
        >>> config = DataSource("s3://bucket/data.parquet")
        >>> df = ingest_data(config)
    """
    # Load data based on format
    if config.format == "parquet":
        df = pd.read_parquet(config.source_uri, columns=config.columns)
    elif config.format == "csv":
        df = pd.read_csv(config.source_uri, usecols=config.columns)
    else:
        raise ValueError(f"Unsupported format: {config.format}")

    # Apply filters if specified
    if config.filters:
        for col, values in config.filters.items():
            df = df[df[col].isin(values)]

    # Log data statistics
    logger.info(f"Loaded {len(df)} rows with {len(df.columns)} columns")
    logger.info(f"Memory usage: {df.memory_usage(deep=True).sum() / 1e6:.2f} MB")

    return df
```

**Actions**:
- Connect to data source (S3, database, local filesystem)
- Load data with efficient I/O (chunking for large datasets)
- Log data statistics (rows, columns, memory usage)
- Handle data partitioning if needed

**Success indicators**:
- Data loaded successfully
- Expected number of rows within tolerance
- No critical columns missing

#### 1.2 Data Validation

```python
from great_expectations.core import ExpectationConfiguration

def validate_data(df: pd.DataFrame, validation_suite: str = "default") -> bool:
    """
    Validate data quality using Great Expectations.

    Args:
        df: Input DataFrame
        validation_suite: Name of validation suite to apply

    Returns:
        True if all validations pass

    Raises:
        DataValidationError: If critical validations fail
    """
    ge_df = PandasDataset(df)

    # Define expectations
    expectations = [
        # Completeness
        ge_df.expect_column_values_to_not_be_null("id", mostly=1.0),
        ge_df.expect_column_values_to_not_be_null("target", mostly=0.99),

        # Validity
        ge_df.expect_column_values_to_be_between("age", 0, 120),
        ge_df.expect_column_values_to_be_in_set("category", ["A", "B", "C"]),

        # Consistency
        ge_df.expect_column_values_to_be_unique("id"),

        # Schema
        ge_df.expect_table_columns_to_match_ordered_list([
            "id", "feature1", "feature2", "target"
        ]),
    ]

    # Run validation
    results = ge_df.validate(expectations)

    if not results["success"]:
        failed = [r for r in results["results"] if not r["success"]]
        logger.error(f"Data validation failed: {failed}")
        raise DataValidationError(failed)

    logger.info("Data validation passed ✓")
    return True
```

**Validation checks**:
- [ ] Schema validation (expected columns present)
- [ ] Data type validation
- [ ] Range validation (min/max values)
- [ ] Uniqueness constraints
- [ ] Missing value thresholds
- [ ] Distribution checks (detect data drift)
- [ ] Relationship validation (foreign keys, etc.)

**Validation Checkpoint**:
- [ ] All critical validations pass
- [ ] Warning-level issues documented
- [ ] Data quality metrics logged

#### 1.3 Feature Engineering

```python
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def create_feature_pipeline():
    """
    Create feature engineering pipeline.

    Returns:
        sklearn Pipeline for feature transformation
    """
    numeric_features = ["age", "income", "credit_score"]
    categorical_features = ["category", "region"]

    numeric_transformer = Pipeline([
        ("scaler", StandardScaler()),
    ])

    categorical_transformer = Pipeline([
        ("encoder", LabelEncoder()),
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ])

    return preprocessor

def engineer_features(df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
    """
    Apply feature engineering transformations.

    Args:
        df: Input DataFrame
        fit: Whether to fit the transformations (True for training data)

    Returns:
        Transformed DataFrame
    """
    # Create temporal features
    if "timestamp" in df.columns:
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
        df["day_of_week"] = pd.to_datetime(df["timestamp"]).dt.dayofweek
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    # Create interaction features
    if "feature1" in df.columns and "feature2" in df.columns:
        df["feature1_x_feature2"] = df["feature1"] * df["feature2"]

    # Apply transformations
    pipeline = create_feature_pipeline()
    if fit:
        transformed = pipeline.fit_transform(df)
    else:
        transformed = pipeline.transform(df)

    return transformed
```

**Actions**:
- Create temporal features (hour, day_of_week, etc.)
- Generate interaction features
- Apply domain-specific transformations
- Handle missing values (imputation strategy)
- Encode categorical variables
- Scale/normalize numerical features
- Create embeddings for high-cardinality categoricals

**Quality checks**:
- [ ] No data leakage (future information in features)
- [ ] Feature distributions reasonable
- [ ] No infinite or NaN values after transformation

#### 1.4 Data Splitting

```python
from sklearn.model_selection import train_test_split

def split_data(df: pd.DataFrame, config: dict):
    """
    Split data into train/val/test sets with stratification.

    Args:
        df: Input DataFrame
        config: Split configuration

    Returns:
        Tuple of (train, val, test) DataFrames
    """
    # First split: train+val vs test
    train_val, test = train_test_split(
        df,
        test_size=config["test_split"],
        stratify=df["target"] if "target" in df else None,
        random_state=42,
    )

    # Second split: train vs val
    val_size = config["val_split"] / (1 - config["test_split"])
    train, val = train_test_split(
        train_val,
        test_size=val_size,
        stratify=train_val["target"] if "target" in train_val else None,
        random_state=42,
    )

    logger.info(f"Split sizes - Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")

    # Verify stratification
    if "target" in df:
        logger.info(f"Train target dist: {train['target'].value_counts(normalize=True)}")
        logger.info(f"Val target dist: {val['target'].value_counts(normalize=True)}")
        logger.info(f"Test target dist: {test['target'].value_counts(normalize=True)}")

    return train, val, test
```

**Actions**:
- Perform stratified splitting (for classification)
- Temporal splitting (for time-series)
- Group-aware splitting (for grouped data)
- Version and save splits (for reproducibility)

---

### Phase 2: Model Training

**Objective**: Train model with hyperparameter optimization and experiment tracking

#### 2.1 Initialize Experiment Tracking

```python
import mlflow
from mlflow.tracking import MlflowClient

def setup_experiment(experiment_name: str):
    """
    Set up MLflow experiment tracking.

    Args:
        experiment_name: Name of the experiment
    """
    mlflow.set_experiment(experiment_name)
    mlflow.set_tracking_uri("http://mlflow-server:5000")

    # Log system information
    mlflow.log_param("python_version", sys.version)
    mlflow.log_param("pytorch_version", torch.__version__)
    mlflow.log_param("cuda_available", torch.cuda.is_available())

    return mlflow.active_run()
```

#### 2.2 Model Training Loop

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

def train_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: str,
    scaler: torch.cuda.amp.GradScaler,
) -> float:
    """
    Train for one epoch.

    Args:
        model: Model to train
        train_loader: Training data loader
        optimizer: Optimizer
        criterion: Loss function
        device: Device (cuda/cpu)
        scaler: GradScaler for mixed precision

    Returns:
        Average training loss
    """
    model.train()
    total_loss = 0

    pbar = tqdm(train_loader, desc="Training")
    for batch_idx, (data, target) in enumerate(pbar):
        data, target = data.to(device), target.to(device)

        optimizer.zero_grad()

        # Mixed precision training
        with torch.cuda.amp.autocast():
            output = model(data)
            loss = criterion(output, target)

        # Backward pass with gradient scaling
        scaler.scale(loss).backward()

        # Gradient clipping
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

        # Optimizer step
        scaler.step(optimizer)
        scaler.update()

        total_loss += loss.item()
        pbar.set_postfix({"loss": loss.item()})

        # Log metrics
        if batch_idx % 100 == 0:
            mlflow.log_metric("train_loss_step", loss.item(), step=batch_idx)

    return total_loss / len(train_loader)

def validate(model: nn.Module, val_loader: DataLoader, criterion: nn.Module, device: str):
    """
    Validate model.

    Returns:
        Dictionary of validation metrics
    """
    model.eval()
    total_loss = 0
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for data, target in val_loader:
            data, target = data.to(device), target.to(device)

            output = model(data)
            loss = criterion(output, target)

            total_loss += loss.item()
            all_preds.extend(output.argmax(dim=1).cpu().numpy())
            all_targets.extend(target.cpu().numpy())

    # Compute metrics
    from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

    metrics = {
        "val_loss": total_loss / len(val_loader),
        "accuracy": accuracy_score(all_targets, all_preds),
        "f1": f1_score(all_targets, all_preds, average="weighted"),
    }

    return metrics
```

#### 2.3 Hyperparameter Optimization

```python
import optuna
from optuna.integration import MLflowCallback

def objective(trial: optuna.Trial):
    """
    Optuna objective function for hyperparameter search.

    Args:
        trial: Optuna trial object

    Returns:
        Validation metric to optimize
    """
    # Suggest hyperparameters
    config = {
        "learning_rate": trial.suggest_float("lr", 1e-5, 1e-3, log=True),
        "batch_size": trial.suggest_categorical("batch_size", [16, 32, 64]),
        "hidden_size": trial.suggest_int("hidden_size", 256, 1024, step=256),
        "dropout": trial.suggest_float("dropout", 0.1, 0.5),
        "weight_decay": trial.suggest_float("weight_decay", 1e-6, 1e-3, log=True),
    }

    # Train model with suggested hyperparameters
    model = create_model(config)
    val_metric = train_model(model, config)

    return val_metric

def run_hyperparameter_search(n_trials: int = 20):
    """
    Run hyperparameter optimization.

    Args:
        n_trials: Number of trials to run

    Returns:
        Best hyperparameters
    """
    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(),
        pruner=optuna.pruners.MedianPruner(),
    )

    mlflow_callback = MLflowCallback(
        tracking_uri="http://mlflow-server:5000",
        metric_name="val_f1",
    )

    study.optimize(objective, n_trials=n_trials, callbacks=[mlflow_callback])

    logger.info(f"Best params: {study.best_params}")
    logger.info(f"Best value: {study.best_value}")

    return study.best_params
```

**Training Actions**:
- Initialize model with config
- Set up optimizer (AdamW, SGD with momentum, etc.)
- Configure learning rate scheduler (cosine, step, reduce on plateau)
- Enable mixed precision training (AMP)
- Implement gradient accumulation (if needed)
- Add gradient clipping
- Log metrics to experiment tracker

**Checkpointing**:
```python
def save_checkpoint(model, optimizer, epoch, best_metric, path):
    """Save training checkpoint."""
    checkpoint = {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "best_metric": best_metric,
    }
    torch.save(checkpoint, path)
    mlflow.log_artifact(path)
```

**Progress Checkpoint**:
- [ ] Training progressing (loss decreasing)
- [ ] Validation metrics improving
- [ ] No NaN or Inf in losses
- [ ] Gradient norms reasonable (not exploding)
- [ ] Checkpoints saved regularly

---

### Phase 3: Model Evaluation & Validation

**Objective**: Comprehensive model evaluation and validation before deployment

#### 3.1 Comprehensive Evaluation

```python
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

def evaluate_model(model, test_loader, device):
    """
    Comprehensive model evaluation.

    Returns:
        Dictionary of metrics and visualizations
    """
    model.eval()
    all_preds = []
    all_probs = []
    all_targets = []

    with torch.no_grad():
        for data, target in test_loader:
            data = data.to(device)
            output = model(data)
            probs = torch.softmax(output, dim=1)

            all_preds.extend(output.argmax(dim=1).cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
            all_targets.extend(target.numpy())

    # Classification report
    report = classification_report(all_targets, all_preds)
    logger.info(f"Classification Report:\n{report}")

    # Confusion matrix
    cm = confusion_matrix(all_targets, all_preds)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title("Confusion Matrix")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.savefig("confusion_matrix.png")
    mlflow.log_artifact("confusion_matrix.png")

    # ROC curve (for binary classification)
    if len(np.unique(all_targets)) == 2:
        from sklearn.metrics import roc_curve, auc
        fpr, tpr, _ = roc_curve(all_targets, np.array(all_probs)[:, 1])
        roc_auc = auc(fpr, tpr)

        plt.figure()
        plt.plot(fpr, tpr, label=f"ROC curve (AUC = {roc_auc:.2f})")
        plt.plot([0, 1], [0, 1], "k--")
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curve")
        plt.legend()
        plt.savefig("roc_curve.png")
        mlflow.log_artifact("roc_curve.png")

    return {
        "accuracy": accuracy_score(all_targets, all_preds),
        "precision": precision_score(all_targets, all_preds, average="weighted"),
        "recall": recall_score(all_targets, all_preds, average="weighted"),
        "f1": f1_score(all_targets, all_preds, average="weighted"),
    }
```

#### 3.2 Model Validation Gates

```python
def validate_model_for_deployment(metrics: dict, baseline_metrics: dict) -> bool:
    """
    Validate model meets deployment criteria.

    Args:
        metrics: Current model metrics
        baseline_metrics: Baseline/production model metrics

    Returns:
        True if model passes all validation gates
    """
    validation_results = {}

    # Gate 1: Minimum performance threshold
    validation_results["min_accuracy"] = metrics["accuracy"] >= 0.85

    # Gate 2: Improvement over baseline
    improvement = metrics["f1"] - baseline_metrics.get("f1", 0)
    validation_results["improves_baseline"] = improvement >= 0.02  # 2% improvement

    # Gate 3: No severe performance degradation on any class
    # (check per-class metrics here)

    # Gate 4: Inference latency acceptable
    validation_results["latency_ok"] = check_inference_latency(model) < 100  # ms

    # Gate 5: Model size acceptable
    model_size_mb = get_model_size(model)
    validation_results["size_ok"] = model_size_mb < 500  # MB

    all_passed = all(validation_results.values())

    logger.info(f"Validation results: {validation_results}")
    mlflow.log_params(validation_results)

    return all_passed
```

**Evaluation metrics**:
- [ ] Accuracy, Precision, Recall, F1
- [ ] ROC-AUC, PR-AUC (for classification)
- [ ] MAE, RMSE, R² (for regression)
- [ ] Per-class performance analysis
- [ ] Error analysis on failure cases
- [ ] Fairness metrics across demographic groups
- [ ] Calibration analysis (reliability diagrams)

**Model validation gates**:
- [ ] Performance exceeds minimum threshold
- [ ] Improves over baseline/production model
- [ ] No severe performance degradation on any segment
- [ ] Inference latency within acceptable range
- [ ] Model size within limits
- [ ] Passes bias and fairness tests
- [ ] Robust to adversarial examples (if applicable)

---

### Phase 4: Model Registry & Deployment

**Objective**: Register validated model and deploy to production

#### 4.1 Model Registration

```python
from mlflow.tracking import MlflowClient

def register_model(model_name: str, run_id: str, metrics: dict):
    """
    Register model in MLflow Model Registry.

    Args:
        model_name: Name for the registered model
        run_id: MLflow run ID
        metrics: Model metrics
    """
    client = MlflowClient()

    # Register model
    model_uri = f"runs:/{run_id}/model"
    model_version = mlflow.register_model(model_uri, model_name)

    # Add description
    client.update_model_version(
        name=model_name,
        version=model_version.version,
        description=f"Model trained on {datetime.now().isoformat()}\n"
                    f"Metrics: {metrics}",
    )

    # Transition to staging
    client.transition_model_version_stage(
        name=model_name,
        version=model_version.version,
        stage="Staging",
    )

    logger.info(f"Model registered: {model_name} v{model_version.version}")
    return model_version
```

#### 4.2 Deployment

```python
# Option 1: Deploy to Kubernetes
def deploy_to_kubernetes(model_version: str):
    """Deploy model to Kubernetes using Seldon Core."""
    deployment_yaml = f"""
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: {model_name}
spec:
  predictors:
  - name: default
    replicas: 3
    graph:
      name: classifier
      implementation: MLFLOW_SERVER
      modelUri: models:/{model_name}/{model_version}
    """
    # Apply deployment
    subprocess.run(["kubectl", "apply", "-f", "-"], input=deployment_yaml, text=True)

# Option 2: Deploy to SageMaker
def deploy_to_sagemaker(model_version: str):
    """Deploy model to AWS SageMaker."""
    import sagemaker
    from sagemaker.pytorch import PyTorchModel

    model = PyTorchModel(
        model_data=f"s3://bucket/models/{model_name}/{model_version}/model.tar.gz",
        role=sagemaker_role,
        framework_version="2.0",
        py_version="py310",
        entry_point="inference.py",
    )

    predictor = model.deploy(
        instance_type="ml.m5.xlarge",
        initial_instance_count=2,
    )

    return predictor
```

**Deployment Actions**:
- Package model with dependencies
- Create deployment configuration
- Deploy to target environment
- Set up health checks and readiness probes
- Configure autoscaling
- Implement A/B testing or canary deployment
- Set up rollback mechanism

---

### Phase 5: Monitoring & Maintenance

**Objective**: Monitor model performance and trigger retraining when needed

#### 5.1 Performance Monitoring

```python
from evidently.dashboard import Dashboard
from evidently.tabs import DataDriftTab, RegressionPerformanceTab

def monitor_model_performance():
    """Monitor model for drift and performance degradation."""
    # Collect production predictions
    production_data = load_recent_predictions()

    # Compare with reference data
    reference_data = load_training_data()

    # Create monitoring dashboard
    dashboard = Dashboard(tabs=[DataDriftTab(), RegressionPerformanceTab()])
    dashboard.calculate(reference_data, production_data)
    dashboard.save("monitoring_report.html")

    # Check for alerts
    drift_detected = check_data_drift(reference_data, production_data)
    performance_degraded = check_performance_degradation()

    if drift_detected or performance_degraded:
        trigger_retraining_pipeline()
```

#### 5.2 Automated Retraining

```python
def trigger_retraining_pipeline():
    """
    Trigger automated retraining pipeline.

    Conditions for retraining:
    - Data drift detected
    - Performance degradation > threshold
    - Scheduled retraining (weekly/monthly)
    - New labeled data available
    """
    logger.info("Triggering automated retraining pipeline")

    # Fetch latest data
    new_data = fetch_recent_data()

    # Run full pipeline
    pipeline = create_ml_pipeline()
    pipeline.run(data=new_data)

    # Notify stakeholders
    send_notification("Retraining pipeline triggered and completed")
```

**Monitoring metrics**:
- [ ] Prediction latency (p50, p95, p99)
- [ ] Throughput (requests per second)
- [ ] Error rate
- [ ] Model performance metrics (accuracy, etc.)
- [ ] Data drift (feature distribution changes)
- [ ] Prediction drift (output distribution changes)
- [ ] Resource usage (CPU, memory, GPU)

**Alerting triggers**:
- Performance degradation > 5%
- Data drift score > threshold
- Error rate spike
- Latency increase > 20%
- Resource exhaustion

---

## Success Criteria

The ML pipeline is considered successful when:

- [ ] **Data Quality**: All data validation checks pass
- [ ] **Model Performance**: Meets or exceeds target metrics
- [ ] **Reproducibility**: Pipeline can be re-run with identical results
- [ ] **Production Ready**: Model deployed and serving predictions
- [ ] **Monitored**: Dashboards and alerts operational
- [ ] **Documented**: Pipeline, model, and decisions documented
- [ ] **Tested**: Unit and integration tests passing
- [ ] **Automated**: Pipeline runs automatically on schedule or trigger

## Rollback Procedure

If the new model causes issues in production:

1. **Immediate Rollback**
   ```python
   # Transition previous version to Production
   client.transition_model_version_stage(
       name=model_name,
       version=previous_version,
       stage="Production",
   )
   ```

2. **Route traffic back to previous deployment**
   ```bash
   kubectl set image deployment/model-server model=model:v{previous_version}
   ```

3. **Verify rollback successful**
   - Check metrics return to baseline
   - Verify no errors in logs
   - Monitor for 1 hour

4. **Investigate failure**
   - Analyze logs and metrics
   - Reproduce issue in staging
   - Fix and re-deploy

## Post-Execution Checklist

- [ ] Clean up temporary files and intermediate data
- [ ] Archive experiment artifacts to long-term storage
- [ ] Update model documentation (model card)
- [ ] Update deployment documentation
- [ ] Notify stakeholders of deployment
- [ ] Schedule model review meeting
- [ ] Set up monitoring alerts
- [ ] Document lessons learned

## Best Practices Reference

### From Google's Rules of Machine Learning
- Rule #1: Don't be afraid to launch a product without machine learning
- Rule #4: Keep the first model simple and get the infrastructure right
- Rule #6: Be careful about dropped data when copying pipelines

### From Uber's Michelangelo
- Standardize feature computation across training and serving
- Use a centralized feature store
- Implement comprehensive monitoring from day one

### From Netflix's Metaflow
- Make pipelines reproducible
- Version everything (code, data, config, models)
- Design for failure and recovery

## Additional Resources

- **MLflow Documentation**: https://mlflow.org/docs/latest/index.html
- **Kubeflow Pipelines**: https://www.kubeflow.org/docs/components/pipelines/
- **Great Expectations**: https://docs.greatexpectations.io/
- **Evidently AI**: https://docs.evidentlyai.com/
- **PyTorch Lightning**: https://pytorch-lightning.readthedocs.io/
