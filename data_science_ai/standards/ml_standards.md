# ML Standards Document

**Version:** 1.0
**Last Updated:** 2025-11-19
**Status:** Production Ready

---

## Table of Contents

1. [Code Style Guide](#code-style-guide)
2. [Documentation Standards](#documentation-standards)
3. [Model Card Templates](#model-card-templates)
4. [Data Sheet Templates](#data-sheet-templates)
5. [Experiment Tracking Standards](#experiment-tracking-standards)
6. [Naming Conventions](#naming-conventions)
7. [Repository Structure](#repository-structure)
8. [Security Best Practices](#security-best-practices)
9. [Privacy Considerations](#privacy-considerations)
10. [Ethics and Fairness Guidelines](#ethics-and-fairness-guidelines)
11. [Reproducibility Checklist](#reproducibility-checklist)

---

## Code Style Guide

### Python Code Standards

#### General Principles
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for code formatting
- Maximum line length: **88 characters** (use Black formatter)
- Use type hints for all function signatures
- Write docstrings for all public functions and classes

#### Formatting

```python
# Use Black for code formatting
# Configuration: pyproject.toml
[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311']

# Use isort for import organization
[tool.isort]
profile = "black"
line_length = 88
```

#### Type Hints

```python
from typing import List, Dict, Optional, Tuple, Union
import numpy as np
import pandas as pd

def train_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    hyperparameters: Dict[str, float],
    validation_split: float = 0.2,
) -> Tuple[np.ndarray, Dict[str, float]]:
    """Train a machine learning model.

    Args:
        X_train: Input features with shape (n_samples, n_features)
        y_train: Target values with shape (n_samples,)
        hyperparameters: Dictionary of hyperparameters
        validation_split: Fraction of data to use for validation

    Returns:
        Tuple of trained model weights and training metrics

    Raises:
        ValueError: If input shapes are incompatible
    """
    pass
```

#### Docstring Format (Google Style)

```python
def preprocess_data(
    df: pd.DataFrame,
    target_column: str,
    remove_missing: bool = True,
) -> Tuple[np.ndarray, np.ndarray]:
    """Preprocess raw data for model training.

    This function handles missing values, encodes categorical variables,
    and splits features from the target variable.

    Args:
        df: Input dataframe containing raw features and target
        target_column: Name of the target column
        remove_missing: Whether to drop rows with missing values

    Returns:
        Tuple containing:
            - X: Feature matrix of shape (n_samples, n_features)
            - y: Target vector of shape (n_samples,)

    Raises:
        KeyError: If target_column not found in dataframe
        ValueError: If dataframe is empty

    Examples:
        >>> df = pd.read_csv('data.csv')
        >>> X, y = preprocess_data(df, 'target')
        >>> print(X.shape)
        (1000, 15)
    """
    pass
```

#### Imports Organization

```python
# Standard library imports
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Third-party imports
import numpy as np
import pandas as pd
import scikit-learn as sklearn
from sklearn.model_selection import train_test_split

# Local application imports
from myml.preprocessing import normalize_features
from myml.models import NeuralNetwork
from myml.utils import setup_logging
```

#### Code Complexity Guidelines
- Functions: Keep under 50 lines of code
- Cyclomatic complexity: Maximum of 10
- Use early returns to reduce nesting
- Extract complex logic into helper functions

```python
# Bad: Multiple nested conditions
def validate_input(X, y, config):
    if X is not None:
        if y is not None:
            if config is not None:
                if X.shape[0] == y.shape[0]:
                    return True
    return False

# Good: Early returns and clear logic
def validate_input(X, y, config):
    """Validate input data and configuration."""
    if X is None or y is None or config is None:
        return False

    if X.shape[0] != y.shape[0]:
        return False

    return True
```

---

## Documentation Standards

### README Requirements

Every project must have a `README.md` in the root directory with:

```markdown
# Project Name

## Overview
Clear, concise description of what the project does.

## Problem Statement
What problem does this project solve?

## Solution
How does this project solve the problem?

## Key Features
- Feature 1
- Feature 2

## Installation

### Requirements
- Python >= 3.9
- Dependencies listed in requirements.txt

### Setup
```bash
git clone <repository-url>
cd <project-directory>
pip install -r requirements.txt
```

## Quick Start
```python
from myml.models import MyModel
model = MyModel()
model.train(X_train, y_train)
predictions = model.predict(X_test)
```

## Data
Description of datasets, sources, and preprocessing steps.

## Results
Summary of key results and metrics.

## Usage
Detailed usage instructions and examples.

## API Reference
Link to API documentation or inline reference.

## Contributing
Guidelines for contributing to the project.

## License
License information.

## References
Key papers, articles, or resources.
```

### Inline Code Comments

```python
# Use comments to explain WHY, not WHAT (code shows what it does)

# Good: Explains reasoning
# We use log transform to stabilize variance and handle outliers
# in highly skewed distributions (typical for e-commerce transaction amounts)
X_transformed = np.log1p(X)

# Bad: Redundant with code
# Take the log of X
X_transformed = np.log1p(X)
```

### Module and Class Documentation

```python
"""Feature preprocessing module for time-series data.

This module provides utilities for transforming and normalizing time-series
features including handling missing values, outlier detection, and seasonal
decomposition.

Typical usage example:
    from myml.preprocessing import TimeSeriesPreprocessor

    preprocessor = TimeSeriesPreprocessor()
    X_clean = preprocessor.fit_transform(X_raw)
"""

class TimeSeriesPreprocessor:
    """Preprocess time-series data for machine learning models.

    This class handles:
    - Missing value imputation using forward fill
    - Outlier detection and capping
    - Seasonal decomposition
    - Feature scaling to [0, 1]

    Attributes:
        method (str): Imputation method ('forward_fill' or 'interpolate')
        outlier_percentile (float): Percentile threshold for outlier detection
    """

    def __init__(self, method: str = 'forward_fill', outlier_percentile: float = 0.95):
        self.method = method
        self.outlier_percentile = outlier_percentile
```

---

## Model Card Templates

### Model Card Structure (Paper: [Mitchell et al., 2019](https://arxiv.org/abs/1810.03993))

Create `model_cards/model_name_model_card.md`:

```markdown
# Model Card: [Model Name]

## Overview
**Model Type:** [e.g., Neural Network, Random Forest, Gradient Boosting]
**Framework:** [e.g., TensorFlow, PyTorch, scikit-learn]
**Version:** 1.0
**Release Date:** YYYY-MM-DD

## Intended Use
### Primary Use Cases
- Use case 1
- Use case 2

### Intended Users
- Data scientists
- ML engineers
- Business stakeholders

### Not Recommended For
- Real-time inference with latency constraints < 100ms
- Production with < 95% uptime requirements
- Out-of-distribution data significantly different from training set

## Model Details
### Input Data
- Input shape: (batch_size, 28, 28, 3)
- Data type: float32 normalized to [0, 1]
- Preprocessing: Center cropping, normalization

### Output Data
- Output shape: (batch_size, 10)
- Output type: probability distribution over 10 classes
- Post-processing: argmax for class prediction

### Architecture
```
Input Layer (224x224x3)
  ↓
Conv Block 1 (32 filters, 3x3 kernel)
  ↓
Max Pool (2x2)
  ↓
Conv Block 2 (64 filters, 3x3 kernel)
  ↓
Max Pool (2x2)
  ↓
Dense Layer (128 units, ReLU)
  ↓
Dropout (0.5)
  ↓
Output Layer (10 units, Softmax)
```

### Parameters
- Total parameters: 2,248,706
- Trainable parameters: 2,248,706
- Model size: 8.6 MB

## Performance Characteristics
### Overall Performance
| Metric | Value | Data Split |
|--------|-------|-----------|
| Accuracy | 0.945 | Test set |
| Precision (weighted) | 0.943 | Test set |
| Recall (weighted) | 0.945 | Test set |
| F1-Score (weighted) | 0.944 | Test set |

### Per-Class Performance
| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| Class 0 | 0.92 | 0.94 | 0.93 | 500 |
| Class 1 | 0.96 | 0.95 | 0.96 | 510 |
| ... | ... | ... | ... | ... |

### Performance Variations
- **By gender:** 2% performance drop on underrepresented group
- **By age group:** Highest accuracy (0.96) for 25-45 age group
- **By geographic region:** 1-3% variation across regions

### Latency Characteristics
- Inference time (CPU): ~50ms per sample
- Inference time (GPU): ~5ms per sample
- Model loading time: ~2 seconds

## Training Data
### Data Source
- Name: ImageNet-1K subset
- Size: 50,000 images for training, 10,000 for validation
- Coverage: 10 object categories

### Data Characteristics
- Image resolution: 224x224 pixels
- Image format: RGB (3 channels)
- Class distribution: Relatively balanced (4,500-5,500 per class)

### Preprocessing
- Center crop to 224x224
- Normalize: subtract ImageNet mean, divide by std dev
- Data augmentation during training (random crops, flips)

### Limitations
- Limited to 10 object categories
- Trained on relatively high-quality images
- May perform poorly on low-resolution or artistic renderings

## Evaluation Data
### Test Set Composition
- Size: 10,000 images
- Class distribution: Balanced (1,000 per class)
- Temporal split: 80% training, 20% test (no temporal leakage)

### Evaluation Methodology
- Cross-validation: 5-fold stratified
- Hyperparameter tuning: Grid search with 50 configurations
- Threshold selection: Based on validation set F1-score

## Ethical Considerations
### Potential Harms
1. **Misclassification bias:** Model may misclassify objects from underrepresented categories, leading to incorrect decisions in downstream applications
2. **Perpetuation of training data bias:** If training data reflects historical biases, model will propagate them

### Fairness Evaluation
- Model performance varies by demographic groups
- Recommend stratified evaluation for specific use cases
- See fairness section below for mitigation strategies

### Recommendations
- Evaluate on diverse, representative test sets
- Implement monitoring for performance drift
- Document model limitations in deployment

## Limitations and Trade-offs
### Known Limitations
1. **Domain specificity:** Model trained on ImageNet; may not generalize to medical or satellite imagery
2. **Computational requirements:** Requires GPU for real-time performance
3. **Data size:** Requires large labeled datasets for effective fine-tuning

### Trade-offs
- **Accuracy vs. Speed:** Using smaller architecture reduces accuracy by 3% but improves latency by 10x
- **Robustness vs. Clean Accuracy:** Adversarial training reduces accuracy by 1% but increases robustness

## Maintenance and Monitoring
### Retraining Schedule
- Scheduled retraining: Quarterly
- Trigger-based retraining: If test accuracy drops > 2%
- Data drift detection: Monitor distribution shift of input features

### Performance Monitoring
- Log accuracy, precision, recall weekly
- Track feature distribution for data drift
- Monitor computational costs and latency

### Support and Issues
- Contact: ml-team@company.com
- Report issues to: ml-issues@company.com
- Expected response time: 24 hours

## Additional Resources
- [Model training code](../../src/train.py)
- [Evaluation results](../../results/evaluation_report.md)
- [Data documentation](../../data/DATA_SHEET.md)
```

---

## Data Sheet Templates

### Data Sheet Structure (Paper: [Gebru et al., 2021](https://arxiv.org/abs/1803.09010))

Create `data/DATASHEET.md`:

```markdown
# Data Sheet for Dataset: [Dataset Name]

## Motivation
### For What Purpose Was the Dataset Created?
The dataset was created to support research and development of [specific ML task]. It addresses the lack of [specific limitation in existing datasets].

### Who Created the Dataset?
- Organization: [Company/Institution Name]
- Funding source: [Funding agency or internal]
- Conflict of interest: [Describe any potential conflicts]

### Any Other Comments?
[Additional context about motivation]

## Composition
### What Do the Instances That Comprise the Dataset Represent?
Each instance represents [e.g., a transaction, a user interaction, an image of an object] with [number] features describing [what aspects].

### How Many Instances Are There in Total?
- Training set: 100,000 instances
- Validation set: 10,000 instances
- Test set: 10,000 instances
- **Total: 120,000 instances**

### Does the Dataset Contain All Possible Instances or Is It a Sample?
The dataset is a [sample/complete collection] of [describe population]. Sampling methodology: [describe if applicable].

### What Data Does Each Instance Consist Of?
Each instance contains:
- **age** (int): User age in years, range [18, 85]
- **gender** (categorical): {Male, Female, Non-binary, Prefer not to say}
- **income** (float): Annual income in USD
- **feature_vector** (array): 256-dimensional feature representation
- **label** (categorical): Binary classification target {0, 1}

### Is There a Label or Target Associated With Each Instance?
Yes, each instance has an associated label indicating [target variable description].

### Is Any Information Missing From Individual Instances?
- Missing values: 2.3% of dataset
- By feature:
  - income: 5% missing (MCAR)
  - education: 1% missing (MCAR)
- Handling: Imputed using [method], documented with indicator variable

### Are There Recommended Data Splits?
- **Training/Validation/Test:** 70/15/15 split
- **Stratification:** Stratified by [demographic characteristics]
- **Time-based split:** If temporal data, use date [YYYY-MM-DD] as split point
- **Group split:** If group-based, ensure groups not split across sets

### Are There Any Errors, Sources of Noise, or Redundancies?
- **Data quality issues:**
  - Duplicate records: 0.5% (detected and documented)
  - Outliers: 2% (documented in feature_quality.csv)
  - Format inconsistencies: None detected

- **Measurement error:**
  - Sensor accuracy: ±2% for continuous features
  - Labeling error rate: ~1% (estimated from inter-annotator agreement)

### Is the Dataset Self-Contained?
The dataset is self-contained and does not require external data for basic use. However, for [specific downstream task], users may want to augment with [specific external data sources].

### Any Confidentiality Issues?
Personal information has been de-identified:
- Names replaced with anonymized IDs
- Addresses removed
- Phone numbers removed
- Dates shifted by random offsets to prevent re-identification

Residual risks: De-identification assessed as [low/medium/high] for re-identification attack.

### Legal and Ethical Review?
- IRB approval: [IRB number or statement]
- Informed consent: [Yes/No and details]
- Data use agreements: [Yes/No and link to agreement]

## Collection Process
### How Was the Data Associated With Each Instance Acquired?
Data was collected through [method: surveys, sensors, web scraping, etc.] between [date range].

### If the Data is a Sample, What Was the Sampling Strategy?
Sampling method: [describe - e.g., stratified random sampling]
Sampling parameters: [describe stratification or sampling rate]

### Who Was Involved in the Data Collection Process?
- Data collectors: [describe team]
- Supervisors: [describe oversight]
- Annotators: [describe annotation team]

### Over What Time Frame Was the Data Collected?
- Collection period: [Start date] to [End date]
- Duration: [time period]
- Frequency: [continuous/daily/weekly/etc.]

### Were Any Ethical Review Processes Conducted?
- Institutional review: [Yes/No, provide board name]
- Informed consent: [Yes/No, describe process]
- Data protection impact assessment: [Yes/No, describe findings]

## Preprocessing/Cleaning/Labeling
### Was Any Preprocessing/Cleaning/Labeling of the Data Done?
Yes, the following preprocessing steps were applied:
1. Removal of [specific criteria]
2. Normalization to [range or distribution]
3. Imputation using [method]
4. Feature engineering: [describe]

### Is the Raw Data Available?
[Yes/No]. If yes: [location and instructions]. If no: [explain why and provide alternative].

### Is There Documentation of the Data Cleaning Process?
Yes, see [data_cleaning_report.md](data_cleaning_report.md) for detailed documentation including:
- Functions used
- Parameters selected
- Quality metrics before/after

### Who Did the Labeling?
- Annotators: [number and qualifications]
- Inter-annotator agreement: [Cohen's kappa or similar measure]
- Instructions: [link to annotation guidelines]
- Adjudication process: [describe consensus method]

## Uses
### Has the Dataset Been Used for Any Tasks?
Yes, the dataset has been used for:
1. [Task 1] - [number] publications
2. [Task 2] - [number] papers

### Is There a Repository That Links to Any or All Papers or Systems That Use the Dataset?
Yes: [link to repository or registry]

### What (Other) Tasks Could the Dataset Be Used For?
The dataset could be used for:
- [Potential task 1]: [relevance assessment]
- [Potential task 2]: [relevance assessment]

### Is There Anything About the Composition of the Dataset or the Way It Was Collected and Preprocessed That Might Impact Future Uses?
Yes:
- [Limited to specific domain/population]
- [Temporal effects: data from specific time period]
- [Measurement constraints: features collected under specific conditions]
- [Systematic bias documented in Limitations section]

### Are There Tasks for Which the Dataset Should Not Be Used?
Yes:
- **Not recommended for:** [specify domains/applications]
- **Reason:** [explain limitation or bias]
- **Potential harms:** [describe negative outcomes if used inappropriately]

## Distribution
### How Will the Dataset Be Distributed?
The dataset is distributed through [method: GitHub, Hugging Face, institutional repository, etc.]

### Will the Dataset Be Distributed Under a Copyright or Other Intellectual Property License? If so, Which?
License: [Specify - e.g., CC-BY-4.0, MIT, Apache 2.0]
Link: [Provide license URL]

### Have Any Third Parties Imposed IP-Based or Other Restrictions on the Data Associated With Your Instances?
[Describe any restrictions - None/Describe restrictions]

### Do Any Export Controls or Other Regulatory Restrictions Apply to the Dataset or Individual Instances?
[Describe regulatory compliance - None/Describe restrictions]

## Maintenance
### Who Is Responsible for the Dataset?
- Point of contact: [name and email]
- Organization: [company/institution]
- Role: [specific responsibility]

### How Can the Dataset Owner or Anyone Else Contact the Dataset Maintainers?
Contact information:
- Email: [address]
- Issue tracker: [GitHub issues/project page]
- Expected response time: [timeframe]

### Is There an Erratum?
[Yes/No]. If yes: [link to erratum document or issue tracker]

### Will the Dataset Be Updated?
Update schedule: [describe frequency and criteria]
Last update: [date]

### If the Dataset Becomes Obsolete, How Will It Be Deprecated?
Deprecation plan: [describe timeline and communication strategy]

### Will Older Versions of the Dataset Continue to Be Supported?
[Yes/No]. If yes: [describe version support policy]

### If Others Want to Extend/Augment/Build On/Contribute to the Dataset, Is There a Mechanism for Them to Do So?
Yes: [describe contribution process, link to CONTRIBUTING.md, outline review process]
```

---

## Experiment Tracking Standards

### MLflow Setup and Conventions

```python
"""Experiment tracking configuration and utilities."""

import mlflow
import json
from pathlib import Path
from typing import Dict, Any, Optional

def setup_experiment(experiment_name: str, tags: Optional[Dict[str, str]] = None) -> str:
    """Set up MLflow experiment with consistent naming and tracking.

    Args:
        experiment_name: Name of the experiment
        tags: Additional tags for the experiment

    Returns:
        Experiment ID
    """
    # Format: {project_name}/{task}/{date}_{experiment_name}
    formatted_name = f"nlp/sentiment/{experiment_name}"

    experiment_id = mlflow.create_experiment(
        formatted_name,
        tags=tags or {}
    )
    mlflow.set_experiment(formatted_name)
    return experiment_id

def log_training_run(
    model_name: str,
    hyperparameters: Dict[str, Any],
    metrics: Dict[str, float],
    artifacts_dir: Path,
) -> str:
    """Log a complete training run with all artifacts.

    Args:
        model_name: Name of the model
        hyperparameters: Hyperparameter dictionary
        metrics: Evaluation metrics dictionary
        artifacts_dir: Directory containing model artifacts

    Returns:
        Run ID
    """
    with mlflow.start_run() as run:
        # Log hyperparameters
        mlflow.log_params({
            "model_name": model_name,
            **{f"hp_{k}": v for k, v in hyperparameters.items()}
        })

        # Log metrics
        for metric_name, metric_value in metrics.items():
            mlflow.log_metric(metric_name, metric_value)

        # Log artifacts
        mlflow.log_artifacts(str(artifacts_dir), artifact_path="model")

        # Log configuration
        config = {
            "model": model_name,
            "hyperparameters": hyperparameters,
            "metrics": metrics,
        }
        mlflow.log_text(
            json.dumps(config, indent=2),
            artifact_file="config.json"
        )

        return run.info.run_id
```

### Experiment Tracking Best Practices

```
experiments/
├── {task}/
│   ├── {experiment_name}/
│   │   ├── params.yaml           # Hyperparameters
│   │   ├── metrics.json          # Final metrics
│   │   ├── config.yaml           # Full config
│   │   ├── logs/
│   │   │   ├── train.log
│   │   │   └── eval.log
│   │   ├── artifacts/
│   │   │   ├── model.pkl
│   │   │   ├── feature_importances.csv
│   │   │   └── confusion_matrix.png
│   │   ├── metadata/
│   │   │   ├── git_commit.txt
│   │   │   ├── environment.yml
│   │   │   └── timestamp.txt
│   │   └── results/
│   │       ├── train_metrics.csv
│   │       ├── val_metrics.csv
│   │       └── test_metrics.csv
```

### Experiment Documentation Template

```yaml
# experiments/nlp/sentiment_v2/experiment.yaml
experiment_name: "sentiment_v2"
description: |
  Second iteration of sentiment analysis model.
  Focuses on improving robustness to adversarial examples
  and reducing inference latency.

task: "sentiment_classification"
project: "nlp"
owner: "ml-team"
date_started: "2025-11-15"
date_completed: "2025-11-18"

objectives:
  - Improve validation accuracy to >95%
  - Reduce model size to <50MB
  - Achieve <100ms inference time on CPU

baseline:
  model_name: "sentiment_v1"
  accuracy: 0.92
  inference_time_ms: 150

changes_from_baseline:
  - Updated to BERT-base instead of DistilBERT
  - Added focal loss for hard example mining
  - Implemented knowledge distillation with DistilBERT

hyperparameters:
  learning_rate: 5e-5
  batch_size: 32
  num_epochs: 3
  warmup_ratio: 0.1
  weight_decay: 0.01
  dropout: 0.1

training_data:
  source: "internal_dataset"
  version: "v3"
  size: 50000
  split: {train: 0.7, val: 0.15, test: 0.15}
  preprocessing:
    - tokenize with BERT tokenizer
    - truncate to 128 tokens
    - pad sequences

results:
  train_loss: 0.15
  val_accuracy: 0.956
  test_accuracy: 0.954
  inference_time_ms: 85
  model_size_mb: 45

key_findings:
  - Focal loss improved performance on underrepresented classes
  - Knowledge distillation reduced model size without accuracy loss
  - Training on augmented data improved robustness

next_steps:
  - Evaluate on out-of-domain test sets
  - Implement adversarial attack evaluation
  - Profile memory usage for mobile deployment

artifacts:
  model_path: "artifacts/model.pt"
  metrics_path: "results/test_metrics.csv"
  confusion_matrix: "results/confusion_matrix.png"

code_reference:
  training_script: "src/train.py"
  config: "configs/sentiment_v2.yaml"
```

---

## Naming Conventions

### File and Directory Naming

```
projects/
├── {project_name}/                          # kebab-case
│   ├── README.md
│   ├── setup.py
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── src/
│   │   └── {package_name}/                  # snake_case
│   │       ├── __init__.py
│   │       ├── config.py
│   │       ├── models/
│   │       │   ├── __init__.py
│   │       │   ├── base_model.py            # snake_case
│   │       │   └── transformer_model.py
│   │       ├── preprocessing/
│   │       │   ├── __init__.py
│   │       │   └── text_processor.py        # descriptive, snake_case
│   │       └── utils/
│   │           ├── __init__.py
│   │           ├── metrics.py
│   │           └── plotting.py
│   ├── tests/
│   │   ├── test_models.py                   # test_{module}.py
│   │   ├── test_preprocessing.py
│   │   └── fixtures/
│   ├── data/
│   │   ├── raw/
│   │   ├── processed/
│   │   └── external/
│   ├── notebooks/
│   │   └── 01_exploratory_analysis.ipynb    # {number}_{description}.ipynb
│   ├── experiments/
│   │   └── {task}/{experiment_id}/
│   ├── models/
│   │   └── {model_name}_{version}.pkl
│   ├── configs/
│   │   ├── base.yaml
│   │   ├── train.yaml
│   │   └── {experiment_name}.yaml
│   ├── results/
│   │   └── {experiment_id}/
│   └── docs/
│       └── {topic}.md
```

### Variable and Function Naming

```python
# Constants: UPPER_SNAKE_CASE
MAX_SEQUENCE_LENGTH = 512
LEARNING_RATE = 5e-5
DEFAULT_BATCH_SIZE = 32

# Classes: PascalCase
class TextPreprocessor:
    pass

class SentimentAnalyzer:
    pass

# Functions and methods: snake_case
def preprocess_text(text: str) -> str:
    """Convert text to lowercase and remove punctuation."""
    pass

def calculate_metrics(predictions, targets):
    """Compute evaluation metrics."""
    pass

# Private methods: _leading_underscore
def _validate_input(data):
    """Internal validation not part of public API."""
    pass

# Protected methods: _leading_underscore (convention only)
def _preprocess_batch(batch):
    """Internal helper method."""
    pass

# Boolean variables: is_/has_/should_ prefix
is_training = True
has_labels = True
should_normalize = False

# Avoid single letters except in loops/comprehensions
# Bad
x = load_data()
y = train_model(x)

# Good
data = load_data()
model = train_model(data)

# Single letters OK in loops
for idx, item in enumerate(items):
    process(item)
```

### Model and Experiment Naming

```
Model naming pattern: {base_name}_{version}_{date}

Examples:
- bert_sentiment_v1_2025-11-15
- lstm_time_series_v2_2025-11-18
- transformer_nlp_v3.1_2025-11-19

Experiment naming pattern: {task}_{approach}_{identifier}

Examples:
- sentiment_focal_loss_exp_001
- time_series_ensemble_exp_002
- nlp_data_augmentation_exp_003

Version numbering: semantic versioning
- Major.Minor.Patch (e.g., 1.2.3)
- Major: Breaking changes or significant architecture redesign
- Minor: New features or improvements
- Patch: Bug fixes or minor adjustments
```

---

## Repository Structure

### Complete Project Template

```
ml-project/
├── README.md                       # Project overview and setup
├── LICENSE                         # MIT, Apache 2.0, etc.
├── .gitignore                      # Exclude data, models, large files
├── .env.example                    # Example environment variables
├── pyproject.toml                  # Project metadata and dependencies
├── setup.py                        # Installation script
├── requirements.txt                # Python dependencies (pinned versions)
├── Makefile                        # Common development commands
├── docker-compose.yml              # Local environment setup
│
├── src/
│   └── ml_project/                 # Main package
│       ├── __init__.py
│       ├── config.py               # Configuration management
│       ├── constants.py            # Project constants
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── base.py             # Abstract base model
│       │   ├── neural_network.py   # NN implementations
│       │   └── ensemble.py         # Ensemble methods
│       │
│       ├── preprocessing/
│       │   ├── __init__.py
│       │   ├── pipeline.py         # Preprocessing pipeline
│       │   ├── transformers.py     # Scikit-learn compatible transformers
│       │   └── validators.py       # Input validation
│       │
│       ├── features/
│       │   ├── __init__.py
│       │   ├── engineering.py      # Feature engineering
│       │   └── selection.py        # Feature selection methods
│       │
│       ├── evaluation/
│       │   ├── __init__.py
│       │   ├── metrics.py          # Evaluation metrics
│       │   └── plotting.py         # Visualization utilities
│       │
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── logging.py          # Logging configuration
│       │   ├── io.py               # File I/O utilities
│       │   └── data_loading.py     # Data loading utilities
│       │
│       └── __main__.py             # CLI entry point
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_models.py
│   ├── test_preprocessing.py
│   ├── test_evaluation.py
│   ├── integration/                # Integration tests
│   │   └── test_pipeline.py
│   └── fixtures/                   # Test data
│       └── sample_data.csv
│
├── notebooks/
│   ├── 00_template.ipynb           # Template notebook
│   ├── 01_exploratory_analysis.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_development.ipynb
│   └── README.md                   # Notebook guide
│
├── data/
│   ├── raw/                        # Original immutable data
│   │   └── .gitkeep
│   ├── processed/                  # Cleaned and preprocessed data
│   │   └── .gitkeep
│   ├── external/                   # External data sources
│   │   └── .gitkeep
│   ├── DATASHEET.md                # Data documentation
│   └── data_dictionary.csv         # Column descriptions
│
├── models/
│   ├── README.md                   # Models documentation
│   ├── model_cards/                # Model card documents
│   │   └── model_v1.md
│   └── .gitkeep
│
├── configs/
│   ├── base.yaml                   # Base configuration
│   ├── train.yaml                  # Training configuration
│   ├── evaluate.yaml               # Evaluation configuration
│   └── hyperparameters.yaml        # Hyperparameter templates
│
├── scripts/
│   ├── train.py                    # Training script
│   ├── evaluate.py                 # Evaluation script
│   ├── predict.py                  # Prediction script
│   └── data_preparation.py         # Data preparation script
│
├── experiments/
│   ├── exp_001/
│   │   ├── config.yaml
│   │   ├── params.yaml
│   │   ├── metrics.json
│   │   ├── artifacts/
│   │   │   └── model.pkl
│   │   └── logs/
│   │       ├── train.log
│   │       └── eval.log
│   └── README.md                   # Experiment tracking guide
│
├── results/
│   ├── plots/                      # Visualizations
│   │   └── .gitkeep
│   ├── reports/                    # Analysis reports
│   │   └── evaluation_report.md
│   └── metrics/                    # Metric results
│       └── .gitkeep
│
├── docs/
│   ├── index.md                    # Documentation home
│   ├── getting_started.md
│   ├── architecture.md
│   ├── api_reference.md
│   ├── CONTRIBUTING.md
│   ├── standards/
│   │   └── ml_standards.md         # This file
│   └── images/                     # Documentation images
│       └── .gitkeep
│
├── ci_cd/                          # CI/CD configuration
│   ├── .github/
│   │   └── workflows/
│   │       ├── tests.yml           # Test workflow
│   │       ├── linting.yml         # Linting workflow
│   │       └── release.yml         # Release workflow
│   └── pre_commit_config.yaml      # Pre-commit hooks
│
└── .dockerignore                    # Docker build ignore
```

### Gitignore Template

```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/

# Data and models (never commit raw data or large files)
data/raw/
data/processed/
models/*.pkl
models/*.h5
models/*.pt
*.csv
*.xlsx
*.json

# Notebooks
.ipynb_checkpoints/
*.ipynb_checkpoint

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
venv/
env/

# Experiment artifacts
experiments/*/artifacts/
experiments/*/logs/

# OS
.DS_Store
Thumbs.db

# Project-specific
*.log
.mlruns/
outputs/
```

---

## Security Best Practices

### Data Security

```python
"""Secure handling of sensitive data."""

from pathlib import Path
import hashlib
import secrets
from typing import Optional

def hash_sensitive_field(value: str, salt: Optional[str] = None) -> str:
    """Hash sensitive information for anonymization.

    Args:
        value: Sensitive value to hash
        salt: Optional salt for hashing (generate random if not provided)

    Returns:
        Hashed and salted value
    """
    if salt is None:
        salt = secrets.token_hex(16)

    salted = f"{salt}{value}".encode()
    return hashlib.sha256(salted).hexdigest()

def encrypt_dataframe(df, sensitive_columns, key_path: Path):
    """Encrypt sensitive columns in dataframe."""
    # Use cryptography library
    from cryptography.fernet import Fernet

    cipher = Fernet(Fernet.generate_key())

    for col in sensitive_columns:
        df[col] = df[col].apply(
            lambda x: cipher.encrypt(str(x).encode()).decode()
        )

    return df

def validate_data_integrity(data_path: Path, expected_hash: str) -> bool:
    """Verify data integrity using checksums.

    Args:
        data_path: Path to data file
        expected_hash: Expected SHA256 hash

    Returns:
        True if hashes match, False otherwise
    """
    sha256_hash = hashlib.sha256()
    with open(data_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest() == expected_hash
```

### Model Security

```python
"""Secure model versioning and deployment."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def create_model_manifest(
    model_path: Path,
    model_config: Dict[str, Any],
    code_version: str,
    data_version: str,
) -> Dict[str, Any]:
    """Create verifiable model manifest for deployment.

    Args:
        model_path: Path to model file
        model_config: Model configuration dictionary
        code_version: Git commit hash of training code
        data_version: Version/hash of training data

    Returns:
        Model manifest with security information
    """
    manifest = {
        "created": datetime.utcnow().isoformat(),
        "model_file": str(model_path),
        "code_version": code_version,
        "data_version": data_version,
        "configuration": model_config,
        "hash": hashlib.sha256(
            json.dumps(model_config, sort_keys=True).encode()
        ).hexdigest(),
    }

    return manifest

def verify_model_integrity(manifest: Dict[str, Any]) -> bool:
    """Verify that model hasn't been tampered with."""
    config_hash = hashlib.sha256(
        json.dumps(manifest["configuration"], sort_keys=True).encode()
    ).hexdigest()

    return config_hash == manifest["hash"]
```

### Access Control

```yaml
# Example RBAC configuration
access_control:
  roles:
    data_scientist:
      permissions:
        - read:data
        - read:models
        - write:experiments
        - write:notebooks
      denied_permissions:
        - delete:production_models
        - access:sensitive_data

    ml_engineer:
      permissions:
        - read:data
        - read:models
        - write:experiments
        - write:models
        - deploy:models
      denied_permissions:
        - delete:production_models

    admin:
      permissions:
        - "*"  # All permissions
```

### Audit Logging

```python
"""Audit logging for compliance and security."""

import logging
import json
from datetime import datetime
from functools import wraps

def audit_log(action: str):
    """Decorator to log user actions for audit trails."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "action": action,
                "function": func.__name__,
                "user": get_current_user(),  # Implement user tracking
                "args": str(args)[:500],  # Truncate sensitive args
                "status": "started",
            }

            logger = logging.getLogger("audit")
            logger.info(json.dumps(audit_entry))

            try:
                result = func(*args, **kwargs)
                audit_entry["status"] = "completed"
                logger.info(json.dumps(audit_entry))
                return result
            except Exception as e:
                audit_entry["status"] = "failed"
                audit_entry["error"] = str(e)
                logger.error(json.dumps(audit_entry))
                raise

        return wrapper
    return decorator
```

---

## Privacy Considerations

### Differential Privacy

```python
"""Differential privacy implementation for sensitive data."""

from typing import Tuple
import numpy as np

def add_laplace_noise(
    data: np.ndarray,
    epsilon: float,
    sensitivity: float,
) -> np.ndarray:
    """Add Laplace noise for differential privacy.

    Args:
        data: Input data array
        epsilon: Privacy budget (lower = more private, less accurate)
        sensitivity: Maximum change in query output for single record

    Returns:
        Data with added Laplace noise

    References:
        - Dwork & Roth (2014): The Algorithmic Foundations of Differential Privacy
    """
    scale = sensitivity / epsilon
    noise = np.random.laplace(loc=0, scale=scale, size=data.shape)
    return data + noise

def federated_learning_aggregate(
    client_updates: list,
    weights: np.ndarray = None,
) -> np.ndarray:
    """Aggregate model updates from multiple clients without sharing raw data.

    Args:
        client_updates: List of model weights from each client
        weights: Optional weights for weighted averaging

    Returns:
        Aggregated model weights

    Notes:
        This implements Federated Averaging (FedAvg) from McMahan et al. (2017)
    """
    if weights is None:
        weights = np.ones(len(client_updates)) / len(client_updates)

    aggregated = np.zeros_like(client_updates[0])

    for update, weight in zip(client_updates, weights):
        aggregated += weight * update

    return aggregated
```

### Data Minimization

```python
"""Strategies for minimizing data collection and retention."""

from datetime import datetime, timedelta
import pandas as pd

class DataMinimizationPolicy:
    """Implement data minimization and retention policies."""

    def __init__(self, retention_days: int = 90):
        """
        Args:
            retention_days: Days to retain data after collection
        """
        self.retention_days = retention_days

    def identify_expired_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identify records that exceed retention period.

        Args:
            df: Dataframe with 'created_date' column

        Returns:
            Dataframe of expired records to be deleted
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        expired = df[pd.to_datetime(df["created_date"]) < cutoff_date]
        return expired

    def anonymize_records(self, df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """Irreversibly anonymize specified columns."""
        df_anon = df.copy()

        for col in columns:
            df_anon[col] = df_anon[col].apply(
                lambda x: hashlib.sha256(str(x).encode()).hexdigest()
            )

        return df_anon
```

### Privacy Risk Assessment

```yaml
# Privacy Impact Assessment Template
assessment:
  project_name: "Recommendation System"
  assessor: "Privacy Team"
  assessment_date: "2025-11-19"

  data_inventory:
    personal_data:
      - user_ids
      - browsing_history
      - purchase_history
      - demographic_data: "Age, location (country-level)"

    sensitive_categories:
      - health_data: false
      - financial_data: true
      - biometric_data: false

    data_sources:
      - internal_events
      - third_party_apis
      - user_surveys

  processing_activities:
    - activity: "Model training"
      purpose: "Improve recommendations"
      legal_basis: "Legitimate interest"
      recipients: ["ML team", "Product team"]
      retention: "90 days"

    - activity: "Analytics"
      purpose: "Measure model performance"
      legal_basis: "Legitimate interest"
      recipients: ["Analytics team"]
      retention: "30 days"

  privacy_risks:
    - risk: "Re-identification via linkage with external data"
      severity: "Medium"
      mitigation: "Aggregate to country-level; differential privacy noise"

    - risk: "Model inversion attacks to recover training data"
      severity: "High"
      mitigation: "Limit model access; monitor for extraction attacks"

    - risk: "Membership inference attacks"
      severity: "Medium"
      mitigation: "Differential privacy; evaluate membership inference risk"

  safeguards:
    technical:
      - differential_privacy: true
      - encryption_in_transit: true
      - encryption_at_rest: true
      - access_controls: true

    organizational:
      - data_protection_training: true
      - privacy_by_design: true
      - vendor_assessment: true
```

---

## Ethics and Fairness Guidelines

### Fairness Assessment Framework

```python
"""Evaluate model fairness across demographic groups."""

import pandas as pd
import numpy as np
from typing import Dict, Tuple

class FairnessEvaluator:
    """Comprehensive fairness evaluation for classification models."""

    def __init__(self, protected_attributes: list):
        """
        Args:
            protected_attributes: List of column names for protected attributes
                                 (e.g., ['gender', 'race', 'age_group'])
        """
        self.protected_attributes = protected_attributes

    def calculate_disparate_impact(
        self,
        y_pred: np.ndarray,
        protected_attr: pd.Series,
        positive_label: int = 1,
    ) -> Dict[str, float]:
        """Calculate disparate impact ratio (4/5 rule).

        Args:
            y_pred: Model predictions
            protected_attr: Protected attribute values
            positive_label: Value representing positive prediction

        Returns:
            Dictionary with disparate impact ratios

        References:
            Feldman et al. (2015): Certifying and removing disparate impact
        """
        di_ratios = {}

        groups = protected_attr.unique()
        positive_rate = {}

        for group in groups:
            mask = protected_attr == group
            positive_rate[group] = (y_pred[mask] == positive_label).mean()

        # Calculate disparate impact (selection rate for disadvantaged group /
        # selection rate for advantaged group)
        min_group = min(positive_rate, key=positive_rate.get)
        max_group = max(positive_rate, key=positive_rate.get)

        di_ratios[f"{min_group}_vs_{max_group}"] = (
            positive_rate[min_group] / positive_rate[max_group]
        )

        return di_ratios

    def evaluate_equalized_odds(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        protected_attr: pd.Series,
    ) -> Dict[str, Dict[str, float]]:
        """Evaluate equalized odds fairness criterion.

        Equalized odds require that TPR and FPR are equal across groups.

        Args:
            y_true: Ground truth labels
            y_pred: Model predictions
            protected_attr: Protected attribute values

        Returns:
            Dictionary with TPR and FPR for each group

        References:
            Hardt et al. (2016): Equality of Opportunity in Supervised Learning
        """
        results = {}

        for group in protected_attr.unique():
            mask = protected_attr == group
            y_true_g = y_true[mask]
            y_pred_g = y_pred[mask]

            tp = ((y_pred_g == 1) & (y_true_g == 1)).sum()
            fp = ((y_pred_g == 1) & (y_true_g == 0)).sum()
            fn = ((y_pred_g == 0) & (y_true_g == 1)).sum()
            tn = ((y_pred_g == 0) & (y_true_g == 0)).sum()

            tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

            results[group] = {
                "tpr": tpr,
                "fpr": fpr,
            }

        return results

    def generate_fairness_report(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        df: pd.DataFrame,
    ) -> str:
        """Generate comprehensive fairness evaluation report."""
        report = "# Fairness Evaluation Report\n\n"

        for attr in self.protected_attributes:
            report += f"## {attr.upper()}\n\n"

            # Disparate impact
            di = self.calculate_disparate_impact(
                y_pred, df[attr].values
            )
            report += "### Disparate Impact\n"
            for ratio_name, ratio_value in di.items():
                status = "PASS" if ratio_value >= 0.8 else "FAIL"
                report += f"- {ratio_name}: {ratio_value:.3f} [{status}]\n"

            # Equalized odds
            eq_odds = self.evaluate_equalized_odds(
                y_true, y_pred, df[attr].values
            )
            report += "\n### Equalized Odds\n"
            for group, metrics in eq_odds.items():
                report += f"- {group}: TPR={metrics['tpr']:.3f}, "
                report += f"FPR={metrics['fpr']:.3f}\n"

        return report
```

### Ethical Review Checklist

```markdown
# Ethical Review Checklist for ML Projects

## Project Scope and Intent
- [ ] Clear statement of project purpose and intended use
- [ ] Identified stakeholders and impact assessment
- [ ] Documented assumptions and limitations
- [ ] Assessment of potential harms and benefits

## Data and Privacy
- [ ] Data sources documented and legally obtained
- [ ] Data collection methods ethical and transparent
- [ ] Personal data minimized and encrypted
- [ ] Privacy impact assessment completed
- [ ] User consent obtained where required
- [ ] Data retention policy defined and enforced
- [ ] Mechanism for data deletion/right to be forgotten

## Fairness and Bias
- [ ] Model evaluated for disparate impact across groups
- [ ] Identified demographic disparities and mitigation strategies
- [ ] Fairness metrics tracked alongside standard metrics
- [ ] Training data composition analyzed for representation
- [ ] Documented known limitations and biases

## Transparency and Explainability
- [ ] Model card created with all required sections
- [ ] Data sheet created documenting dataset
- [ ] Model decision-making process documented
- [ ] Explainability methods implemented (SHAP, LIME, etc.)
- [ ] Clear documentation on when/how model can be overridden

## Accountability and Governance
- [ ] Clear ownership and responsibility assignment
- [ ] Process for handling complaints and appeals
- [ ] Regular monitoring and evaluation scheduled
- [ ] Plan for model deprecation if necessary
- [ ] Audit trail logging implemented

## Human Oversight
- [ ] Human-in-the-loop decision processes for high-stakes decisions
- [ ] Clear escalation procedures for uncertain predictions
- [ ] Training provided for users and stakeholders
- [ ] Mechanism for providing feedback and contesting decisions

## Security
- [ ] Model and data access controls implemented
- [ ] Vulnerability assessments completed
- [ ] Adversarial robustness evaluated
- [ ] Secure deployment practices followed

## Compliance
- [ ] Legal requirements identified and addressed
- [ ] Regulatory compliance assessed (GDPR, CCPA, etc.)
- [ ] Licenses and attribution verified
- [ ] Terms of use compliant with regulations
```

---

## Reproducibility Checklist

### Complete Reproducibility Framework

```markdown
# Reproducibility Checklist

## Code Reproducibility

### Version Control
- [ ] All code in version control (Git)
- [ ] Repository README with clear setup instructions
- [ ] .gitignore properly configured
- [ ] Meaningful commit messages following conventional commits
- [ ] Git tags for model releases (e.g., v1.0.0)

### Environment
- [ ] requirements.txt with pinned versions
  ```
  pandas==1.3.5
  scikit-learn==1.0.2
  torch==1.10.0
  ```
- [ ] Python version specified (e.g., Python 3.9+)
- [ ] Docker image defined for environment reproducibility
- [ ] Dockerfile includes exact versions of system dependencies
- [ ] environment.yml for conda environments

### Code Structure
- [ ] Clear separation of concerns (data, models, utils)
- [ ] All magic numbers extracted to configuration files
- [ ] Comprehensive type hints
- [ ] Docstrings for all functions
- [ ] Tests for critical functions

## Data Reproducibility

### Data Documentation
- [ ] Dataset description (DATA_SHEET.md)
- [ ] Data source and collection method documented
- [ ] License and usage terms documented
- [ ] Data dictionary with column descriptions
- [ ] Known issues and limitations documented

### Data Versioning
- [ ] Data version tracked (in addition to code version)
- [ ] Checksums/hashes for critical datasets
- [ ] Clear procedure for updating datasets
- [ ] Old dataset versions archived
- [ ] Data transformations are deterministic and documented

### Data Reproducibility
```python
def load_and_preprocess_data(
    data_path: str,
    random_seed: int = 42,
    version: str = "v1.0"
) -> Tuple[np.ndarray, np.ndarray]:
    """Load and preprocess data with full reproducibility.

    Args:
        data_path: Path to raw data
        random_seed: Random seed for splits and augmentation
        version: Data version

    Returns:
        Preprocessed X, y arrays
    """
    # Set seeds for reproducibility
    np.random.seed(random_seed)

    # Document preprocessing
    print(f"Loading data from {data_path}")
    print(f"Using random seed: {random_seed}")
    print(f"Data version: {version}")

    # Load with version control
    df = pd.read_csv(data_path)

    # Deterministic preprocessing
    df = df.sort_values("id")  # Ensure consistent order

    return preprocess(df)
```

## Experiment Reproducibility

### Hyperparameter Documentation
- [ ] All hyperparameters in configuration file
  ```yaml
  model:
    name: "bert"
    hidden_size: 768
    num_layers: 12
    dropout: 0.1

  training:
    learning_rate: 5e-5
    batch_size: 32
    num_epochs: 3
    optimizer: "adam"
    seed: 42
  ```
- [ ] Default values documented
- [ ] Rationale for hyperparameter choices documented
- [ ] Grid search/hyperparameter tuning results saved

### Random Seed Management
```python
import random
import numpy as np
import torch

def set_seeds(seed: int = 42):
    """Set random seeds for reproducibility across all libraries."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

# Use in training script
set_seeds(42)
```

### Experiment Tracking
- [ ] All experiments tracked with MLflow/Weights & Biases
- [ ] Model artifacts saved with experiment ID
- [ ] Training logs saved
- [ ] Metrics CSV exported
- [ ] Configuration saved with experiment
  ```
  experiments/
  └── exp_001/
      ├── config.yaml          # Full configuration
      ├── metrics.json         # Final metrics
      ├── model.pkl            # Saved model
      ├── train.log            # Training log
      └── metadata.json        # Git commit, timestamp, etc.
  ```

### Reproducibility Report Template
```markdown
# Reproducibility Report

## Setup Instructions
```bash
# Clone and setup
git clone <repo> --branch v1.0.0
cd project
pip install -r requirements.txt

# Download data
wget https://data.example.com/dataset_v1.0.zip
unzip dataset_v1.0.zip -d data/raw/

# Run training
python scripts/train.py --config configs/base.yaml --seed 42
```

## Code Reproducibility
- **Repository:** https://github.com/org/project
- **Branch:** main
- **Commit:** abc123def456
- **Python Version:** 3.9.7
- **Framework Versions:**
  - PyTorch: 1.10.0
  - scikit-learn: 1.0.2

## Data Reproducibility
- **Dataset:** ImageNet-1K subset
- **Version:** v1.0
- **Size:** 50,000 images
- **Checksums:** [link to checksums.txt]
- **Preprocessing:** See data/preprocessing.py

## Experiment Setup
- **Random Seed:** 42
- **Device:** GPU (NVIDIA A100)
- **Training Time:** ~2 hours

## Results
- **Accuracy:** 0.945
- **F1-Score:** 0.944
- **Model File:** models/bert_sentiment_v1_2025-11-19.pkl

## Verification Steps
```python
# Verify data integrity
python scripts/verify_data.py --checksum data/checksums.txt

# Re-run training
python scripts/train.py --config configs/base.yaml --seed 42

# Verify predictions match (within floating point tolerance)
python scripts/verify_reproducibility.py --baseline results/baseline_predictions.csv
```

## Known Non-Determinism
- CUDA operations may have slight floating-point variations
- Expected difference in accuracy: < 0.001

## Deviations from Original
- [List any deviations and explanations]
```

## Documentation Reproducibility
- [ ] README with clear setup instructions
- [ ] Notebook walk-throughs of key analyses
- [ ] Code comments explaining non-obvious decisions
- [ ] Link to model card and data sheet
- [ ] Known limitations and assumptions documented

## Testing for Reproducibility
```python
# Unit test for deterministic behavior
def test_deterministic_preprocessing():
    """Verify that preprocessing is deterministic."""
    data = generate_test_data()

    result1 = preprocess_data(data, seed=42)
    result2 = preprocess_data(data, seed=42)

    np.testing.assert_array_equal(result1, result2)

# Integration test for reproducibility
def test_model_reproducibility():
    """Verify that training with same seed produces same model."""
    model1 = train_model(seed=42)
    model2 = train_model(seed=42)

    preds1 = model1.predict(X_test)
    preds2 = model2.predict(X_test)

    np.testing.assert_array_almost_equal(preds1, preds2, decimal=5)
```

## Final Checklist
- [ ] README provides clear, step-by-step reproduction instructions
- [ ] All code dependencies pinned to specific versions
- [ ] Random seeds set consistently throughout codebase
- [ ] Data versioning and checksums implemented
- [ ] Experiments tracked with full configuration
- [ ] Model artifacts saved with reproducibility metadata
- [ ] CI/CD pipeline tests reproducibility
- [ ] Documentation includes expected runtimes and compute requirements
- [ ] Known sources of non-determinism documented
- [ ] Instructions for verifying results provided
```

---

## References and Further Reading

### Key Papers
- Mitchell et al. (2019). "Model Cards for Model Reporting." https://arxiv.org/abs/1810.03993
- Gebru et al. (2021). "Datasheets for DataSets." https://arxiv.org/abs/1803.09010
- Hardt et al. (2016). "Equality of Opportunity in Supervised Learning." https://arxiv.org/abs/1610.02413
- Dwork & Roth (2014). "The Algorithmic Foundations of Differential Privacy."
- Feldman et al. (2015). "Certifying and removing disparate impact."

### Tools and Frameworks
- **Experiment Tracking:** MLflow, Weights & Biases, Neptune
- **Fairness:** Fairness Indicators, IBM AI Fairness 360, Aequitas
- **Interpretability:** SHAP, LIME, Captum
- **Data Versioning:** DVC, LakeFS
- **Model Versioning:** MLflow, Hugging Face Model Hub
- **Testing:** pytest, Great Expectations

### External Standards
- [Google AI Principles](https://ai.google/principles/)
- [Partnership on AI Guidelines](https://partnershiponai.org/)
- [NIST AI Risk Management Framework](https://ai.nist.gov/RMF)
- [EU AI Act](https://commission.europa.eu/law/european-union-artificial-intelligence-act)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-19 | Initial comprehensive standards document |

## Maintenance

**Owner:** ML Standards Committee
**Review Frequency:** Quarterly
**Last Reviewed:** 2025-11-19
**Next Review:** 2026-02-19
