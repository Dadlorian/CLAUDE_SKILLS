# ML Project Scaffolding Template

## Purpose
Generate production-ready ML project structures with best practices baked in. Follows patterns from PyTorch Lightning, HuggingFace Transformers, and leading ML engineering teams.

## When to Use

- Starting a new ML/DL project from scratch
- Setting up computer vision, NLP, or tabular ML projects
- Creating reusable ML components
- Building research code that needs to scale to production
- Implementing models from research papers

## Prerequisites

- [ ] Project requirements defined (task type, data, constraints)
- [ ] Framework chosen (PyTorch, TensorFlow, JAX, scikit-learn)
- [ ] Python environment ready (Python 3.8+)
- [ ] Basic project info (name, description, license)

## Configuration

```python
project_config = {
    # Project Info
    "project_name": "my_ml_project",
    "description": "Brief project description",
    "author": "Your Name",
    "python_version": "3.10",

    # ML Framework
    "framework": "pytorch",  # pytorch, tensorflow, jax, sklearn

    # Project Type
    "project_type": "image_classification",  # Options:
    # - image_classification, object_detection, segmentation
    # - text_classification, ner, question_answering, llm_finetuning
    # - tabular_classification, tabular_regression
    # - time_series, reinforcement_learning

    # Tools & Libraries
    "use_lightning": True,  # PyTorch Lightning for boilerplate reduction
    "use_hydra": True,  # Hydra for configuration management
    "use_wandb": True,  # Weights & Biases for experiment tracking
    "use_dvc": False,  # DVC for data versioning

    # Code Quality
    "use_pre_commit": True,  # Pre-commit hooks
    "use_black": True,  # Code formatting
    "use_ruff": True,  # Fast linting
    "use_mypy": True,  # Type checking

    # Testing
    "use_pytest": True,
    "use_coverage": True,

    # CI/CD
    "ci_provider": "github_actions",  # github_actions, gitlab_ci, circle_ci

    # Documentation
    "use_mkdocs": True,  # Documentation with MkDocs
}
```

## Project Structure

```
my_ml_project/
├── README.md                   # Project overview and setup
├── setup.py                    # Package installation
├── requirements.txt            # Python dependencies
├── environment.yml             # Conda environment (optional)
├── .gitignore                  # Git ignore rules
├── .pre-commit-config.yaml     # Pre-commit hooks
├── pyproject.toml              # Project metadata & tool configs
│
├── configs/                    # Hydra configuration files
│   ├── config.yaml            # Main config
│   ├── model/
│   │   ├── resnet50.yaml
│   │   └── efficientnet.yaml
│   ├── data/
│   │   └── imagenet.yaml
│   └── trainer/
│       └── default.yaml
│
├── data/                       # Data directory (gitignored)
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── notebooks/                  # Jupyter notebooks
│   ├── 01_eda.ipynb
│   ├── 02_baseline.ipynb
│   └── 03_analysis.ipynb
│
├── src/                        # Source code
│   └── {project_name}/
│       ├── __init__.py
│       ├── data/               # Data loading and processing
│       │   ├── __init__.py
│       │   ├── dataset.py
│       │   ├── datamodule.py  # PyTorch Lightning DataModule
│       │   └── transforms.py
│       ├── models/             # Model definitions
│       │   ├── __init__.py
│       │   ├── model.py
│       │   ├── components.py  # Reusable components
│       │   └── pretrained.py
│       ├── training/           # Training logic
│       │   ├── __init__.py
│       │   ├── trainer.py
│       │   ├── callbacks.py
│       │   └── losses.py
│       ├── evaluation/         # Evaluation and metrics
│       │   ├── __init__.py
│       │   ├── metrics.py
│       │   └── evaluator.py
│       └── utils/              # Utility functions
│           ├── __init__.py
│           ├── config.py
│           ├── logging.py
│           └── visualization.py
│
├── scripts/                    # Executable scripts
│   ├── train.py               # Training script
│   ├── evaluate.py            # Evaluation script
│   ├── predict.py             # Inference script
│   └── download_data.py       # Data download script
│
├── tests/                      # Unit and integration tests
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_data.py
│   ├── test_models.py
│   └── test_training.py
│
├── experiments/                # Experiment outputs (gitignored)
│   ├── runs/
│   ├── checkpoints/
│   └── logs/
│
├── docs/                       # Documentation
│   ├── index.md
│   ├── quickstart.md
│   └── api/
│
├── docker/                     # Docker configurations
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── .github/                    # GitHub specific
    └── workflows/
        ├── ci.yml             # CI pipeline
        └── deploy.yml         # Deployment pipeline
```

## Generation Workflow

### Step 1: Initialize Project Structure

```bash
# Create project directory
mkdir my_ml_project && cd my_ml_project

# Initialize git
git init
git branch -M main

# Create directory structure
mkdir -p src/{project_name}/{data,models,training,evaluation,utils}
mkdir -p configs/{model,data,trainer}
mkdir -p {scripts,tests,notebooks,experiments,docs,docker}
mkdir -p data/{raw,processed,external}
```

### Step 2: Generate Core Files

#### README.md

```markdown
# {Project Name}

{Project Description}

## Features

- ✅ Production-ready ML project structure
- ✅ PyTorch Lightning for clean training code
- ✅ Hydra for powerful configuration management
- ✅ Comprehensive testing with pytest
- ✅ Experiment tracking with Weights & Biases
- ✅ Type hints and docstrings throughout
- ✅ Pre-commit hooks for code quality
- ✅ Docker support for reproducibility

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/username/{project_name}.git
cd {project_name}

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -e .
```

### Training

```bash
# Train with default config
python scripts/train.py

# Train with custom config
python scripts/train.py model=efficientnet data.batch_size=64

# Override multiple params
python scripts/train.py model=resnet50 trainer.max_epochs=100 data.batch_size=32
```

### Evaluation

```bash
python scripts/evaluate.py checkpoint_path=experiments/runs/best_model.ckpt
```

### Inference

```bash
python scripts/predict.py --image path/to/image.jpg --checkpoint best_model.ckpt
```

## Project Structure

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed documentation.

## Configuration

All configuration is managed through Hydra. See `configs/` directory.

## Development

### Running Tests

```bash
pytest tests/
pytest tests/ --cov=src  # With coverage
```

### Code Quality

```bash
# Format code
black src/ tests/ scripts/

# Lint
ruff src/ tests/ scripts/

# Type check
mypy src/
```

## Citation

If you use this project, please cite:

```bibtex
@software{project_name,
  author = {Author Name},
  title = {Project Name},
  year = {2025},
  url = {https://github.com/username/project_name}
}
```

## License

MIT License - see [LICENSE](LICENSE)
```

#### setup.py

```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="{project_name}",
    version="0.1.0",
    author="{author}",
    author_email="{author_email}",
    description="{description}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/{username}/{project_name}",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "ruff>=0.1",
            "mypy>=1.0",
            "pre-commit>=3.0",
        ],
        "docs": [
            "mkdocs>=1.4",
            "mkdocs-material>=9.0",
            "mkdocstrings[python]>=0.20",
        ],
    },
)
```

#### requirements.txt

```
# Core ML Framework
torch>=2.0.0
torchvision>=0.15.0
pytorch-lightning>=2.0.0

# Data Processing
numpy>=1.24.0
pandas>=2.0.0
pillow>=9.0.0
albumentations>=1.3.0  # For image augmentation

# Configuration & Logging
hydra-core>=1.3.0
wandb>=0.15.0
python-dotenv>=1.0.0

# Utilities
tqdm>=4.65.0
rich>=13.0.0  # Beautiful terminal output

# Evaluation
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0

# Optional but recommended
# tensorboard>=2.13.0
# optuna>=3.0.0  # For hyperparameter optimization
```

### Step 3: Generate Data Module

#### src/{project_name}/data/dataset.py

```python
"""
Dataset implementation.

Following PyTorch best practices for custom datasets.
"""

from pathlib import Path
from typing import Optional, Callable, Tuple, List
import torch
from torch.utils.data import Dataset
from PIL import Image
import pandas as pd


class CustomDataset(Dataset):
    """
    Custom dataset for {project_type}.

    Args:
        data_dir: Path to data directory
        split: Dataset split (train, val, test)
        transform: Optional transform to apply to images
        target_transform: Optional transform to apply to targets

    Example:
        >>> dataset = CustomDataset("data/processed", split="train")
        >>> image, label = dataset[0]
        >>> print(f"Image shape: {image.shape}, Label: {label}")
    """

    def __init__(
        self,
        data_dir: str,
        split: str = "train",
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
    ):
        super().__init__()
        self.data_dir = Path(data_dir)
        self.split = split
        self.transform = transform
        self.target_transform = target_transform

        # Load annotations
        self.samples = self._load_annotations()

    def _load_annotations(self) -> List[Tuple[Path, int]]:
        """
        Load dataset annotations.

        Returns:
            List of (image_path, label) tuples
        """
        # Example: Load from CSV
        annotations_file = self.data_dir / f"{self.split}.csv"
        df = pd.read_csv(annotations_file)

        samples = []
        for _, row in df.iterrows():
            image_path = self.data_dir / row["image_path"]
            label = row["label"]
            samples.append((image_path, label))

        return samples

    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        """
        Get dataset item.

        Args:
            idx: Index

        Returns:
            Tuple of (image, label)
        """
        image_path, label = self.samples[idx]

        # Load image
        image = Image.open(image_path).convert("RGB")

        # Apply transforms
        if self.transform:
            image = self.transform(image)

        if self.target_transform:
            label = self.target_transform(label)

        return image, label


class TextDataset(Dataset):
    """Dataset for text classification tasks."""

    def __init__(
        self,
        data_path: str,
        tokenizer: Callable,
        max_length: int = 512,
        split: str = "train",
    ):
        super().__init__()
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Load data
        df = pd.read_csv(data_path)
        self.texts = df["text"].tolist()
        self.labels = df["label"].tolist()

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int):
        text = self.texts[idx]
        label = self.labels[idx]

        # Tokenize
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "label": torch.tensor(label, dtype=torch.long),
        }
```

#### src/{project_name}/data/datamodule.py

```python
"""
PyTorch Lightning DataModule.

Handles all data loading, preprocessing, and splitting logic.
"""

from typing import Optional
import pytorch_lightning as pl
from torch.utils.data import DataLoader, random_split
from torchvision import transforms

from .dataset import CustomDataset


class CustomDataModule(pl.LightningDataModule):
    """
    DataModule for {project_name}.

    Args:
        data_dir: Path to data directory
        batch_size: Batch size for training
        num_workers: Number of data loading workers
        val_split: Validation split ratio
        image_size: Size to resize images to

    Example:
        >>> dm = CustomDataModule("data/processed", batch_size=32)
        >>> dm.setup()
        >>> train_loader = dm.train_dataloader()
    """

    def __init__(
        self,
        data_dir: str = "data/processed",
        batch_size: int = 32,
        num_workers: int = 4,
        val_split: float = 0.2,
        image_size: int = 224,
    ):
        super().__init__()
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.val_split = val_split
        self.image_size = image_size

        # Will be set in setup()
        self.train_dataset = None
        self.val_dataset = None
        self.test_dataset = None

    def prepare_data(self):
        """
        Download and prepare data (called once, on 1 GPU/CPU).

        Use this for downloading, tokenizing, etc.
        Do not assign state here (self.x = y).
        """
        # Example: Download dataset if not exists
        # download_dataset(self.data_dir)
        pass

    def setup(self, stage: Optional[str] = None):
        """
        Setup datasets (called on every GPU in distributed training).

        Args:
            stage: Current stage (fit, validate, test, predict)
        """
        # Define transforms
        train_transform = transforms.Compose([
            transforms.Resize((self.image_size, self.image_size)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ])

        val_transform = transforms.Compose([
            transforms.Resize((self.image_size, self.image_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ])

        # Setup for training
        if stage == "fit" or stage is None:
            self.train_dataset = CustomDataset(
                self.data_dir,
                split="train",
                transform=train_transform,
            )

            self.val_dataset = CustomDataset(
                self.data_dir,
                split="val",
                transform=val_transform,
            )

        # Setup for testing
        if stage == "test" or stage is None:
            self.test_dataset = CustomDataset(
                self.data_dir,
                split="test",
                transform=val_transform,
            )

    def train_dataloader(self) -> DataLoader:
        """Return training dataloader."""
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            shuffle=True,
            pin_memory=True,
            persistent_workers=True if self.num_workers > 0 else False,
        )

    def val_dataloader(self) -> DataLoader:
        """Return validation dataloader."""
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            shuffle=False,
            pin_memory=True,
            persistent_workers=True if self.num_workers > 0 else False,
        )

    def test_dataloader(self) -> DataLoader:
        """Return test dataloader."""
        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            shuffle=False,
            pin_memory=True,
        )
```

### Step 4: Generate Model Code

#### src/{project_name}/models/model.py

```python
"""
Model definition.

Implements the main model architecture following PyTorch best practices.
"""

import torch
import torch.nn as nn
import pytorch_lightning as pl
from torchmetrics import Accuracy, F1Score
from typing import Dict, Any, Optional


class LitModel(pl.LightningModule):
    """
    PyTorch Lightning model for {project_type}.

    Args:
        num_classes: Number of output classes
        learning_rate: Learning rate for optimizer
        backbone: Backbone architecture (resnet50, efficientnet_b0, etc.)
        pretrained: Whether to use pretrained weights

    Example:
        >>> model = LitModel(num_classes=10, backbone="resnet50")
        >>> output = model(torch.randn(1, 3, 224, 224))
        >>> print(output.shape)  # (1, 10)
    """

    def __init__(
        self,
        num_classes: int = 10,
        learning_rate: float = 1e-3,
        backbone: str = "resnet50",
        pretrained: bool = True,
    ):
        super().__init__()
        self.save_hyperparameters()

        self.num_classes = num_classes
        self.learning_rate = learning_rate

        # Build model
        self.model = self._build_model(backbone, pretrained)

        # Loss function
        self.criterion = nn.CrossEntropyLoss()

        # Metrics
        self.train_acc = Accuracy(task="multiclass", num_classes=num_classes)
        self.val_acc = Accuracy(task="multiclass", num_classes=num_classes)
        self.val_f1 = F1Score(task="multiclass", num_classes=num_classes)

    def _build_model(self, backbone: str, pretrained: bool) -> nn.Module:
        """
        Build model architecture.

        Args:
            backbone: Backbone name
            pretrained: Use pretrained weights

        Returns:
            Model
        """
        if backbone == "resnet50":
            from torchvision.models import resnet50, ResNet50_Weights
            weights = ResNet50_Weights.DEFAULT if pretrained else None
            model = resnet50(weights=weights)
            model.fc = nn.Linear(model.fc.in_features, self.num_classes)

        elif backbone == "efficientnet_b0":
            from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
            weights = EfficientNet_B0_Weights.DEFAULT if pretrained else None
            model = efficientnet_b0(weights=weights)
            model.classifier[1] = nn.Linear(
                model.classifier[1].in_features,
                self.num_classes,
            )

        else:
            raise ValueError(f"Unknown backbone: {backbone}")

        return model

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input tensor (B, C, H, W)

        Returns:
            Logits (B, num_classes)
        """
        return self.model(x)

    def training_step(self, batch, batch_idx):
        """Training step."""
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)

        # Metrics
        preds = torch.argmax(logits, dim=1)
        self.train_acc(preds, y)

        # Logging
        self.log("train/loss", loss, on_step=True, on_epoch=True, prog_bar=True)
        self.log("train/acc", self.train_acc, on_step=False, on_epoch=True, prog_bar=True)

        return loss

    def validation_step(self, batch, batch_idx):
        """Validation step."""
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)

        # Metrics
        preds = torch.argmax(logits, dim=1)
        self.val_acc(preds, y)
        self.val_f1(preds, y)

        # Logging
        self.log("val/loss", loss, on_step=False, on_epoch=True, prog_bar=True)
        self.log("val/acc", self.val_acc, on_step=False, on_epoch=True, prog_bar=True)
        self.log("val/f1", self.val_f1, on_step=False, on_epoch=True)

    def configure_optimizers(self):
        """Configure optimizers and learning rate schedulers."""
        optimizer = torch.optim.AdamW(
            self.parameters(),
            lr=self.learning_rate,
            weight_decay=1e-4,
        )

        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=self.trainer.max_epochs,
            eta_min=1e-6,
        )

        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "interval": "epoch",
            },
        }
```

### Step 5: Generate Training Script

#### scripts/train.py

```python
"""
Training script.

Example usage:
    python scripts/train.py
    python scripts/train.py model=resnet50 data.batch_size=64
    python scripts/train.py trainer.max_epochs=100
"""

import hydra
from omegaconf import DictConfig, OmegaConf
import pytorch_lightning as pl
from pytorch_lightning.callbacks import (
    ModelCheckpoint,
    EarlyStopping,
    LearningRateMonitor,
    RichProgressBar,
)
from pytorch_lightning.loggers import WandbLogger

from {project_name}.data.datamodule import CustomDataModule
from {project_name}.models.model import LitModel


@hydra.main(version_base=None, config_path="../configs", config_name="config")
def train(cfg: DictConfig):
    """
    Train model with Hydra configuration.

    Args:
        cfg: Hydra configuration
    """
    # Print config
    print(OmegaConf.to_yaml(cfg))

    # Set seed
    pl.seed_everything(cfg.seed, workers=True)

    # Initialize DataModule
    datamodule = CustomDataModule(
        data_dir=cfg.data.data_dir,
        batch_size=cfg.data.batch_size,
        num_workers=cfg.data.num_workers,
        image_size=cfg.data.image_size,
    )

    # Initialize Model
    model = LitModel(
        num_classes=cfg.model.num_classes,
        learning_rate=cfg.model.learning_rate,
        backbone=cfg.model.backbone,
        pretrained=cfg.model.pretrained,
    )

    # Callbacks
    callbacks = [
        ModelCheckpoint(
            dirpath=cfg.trainer.checkpoint_dir,
            filename="{epoch:02d}-{val_acc:.4f}",
            monitor="val/acc",
            mode="max",
            save_top_k=3,
            save_last=True,
        ),
        EarlyStopping(
            monitor="val/acc",
            mode="max",
            patience=cfg.trainer.early_stopping_patience,
            verbose=True,
        ),
        LearningRateMonitor(logging_interval="epoch"),
        RichProgressBar(),
    ]

    # Logger
    logger = WandbLogger(
        project=cfg.project_name,
        name=cfg.experiment_name,
        save_dir=cfg.trainer.log_dir,
    ) if cfg.use_wandb else None

    # Trainer
    trainer = pl.Trainer(
        max_epochs=cfg.trainer.max_epochs,
        accelerator=cfg.trainer.accelerator,
        devices=cfg.trainer.devices,
        precision=cfg.trainer.precision,
        callbacks=callbacks,
        logger=logger,
        deterministic=True,
        gradient_clip_val=cfg.trainer.gradient_clip_val,
    )

    # Train
    trainer.fit(model, datamodule=datamodule)

    # Test best model
    trainer.test(model, datamodule=datamodule, ckpt_path="best")


if __name__ == "__main__":
    train()
```

### Step 6: Generate Configuration Files

#### configs/config.yaml

```yaml
# Main configuration file

defaults:
  - model: resnet50
  - data: default
  - trainer: default
  - _self_

# Project info
project_name: {project_name}
experiment_name: baseline

# Random seed for reproducibility
seed: 42

# Experiment tracking
use_wandb: true
```

#### configs/model/resnet50.yaml

```yaml
# ResNet50 model configuration

num_classes: 10
backbone: resnet50
pretrained: true
learning_rate: 1e-3
```

#### configs/data/default.yaml

```yaml
# Data configuration

data_dir: data/processed
batch_size: 32
num_workers: 4
image_size: 224
val_split: 0.2
```

#### configs/trainer/default.yaml

```yaml
# Trainer configuration

max_epochs: 100
accelerator: auto  # auto, cpu, gpu, tpu
devices: 1
precision: 16-mixed  # 32, 16-mixed, bf16-mixed

# Checkpointing
checkpoint_dir: experiments/checkpoints
log_dir: experiments/logs

# Training settings
gradient_clip_val: 1.0
early_stopping_patience: 10
```

### Step 7: Generate Tests

#### tests/conftest.py

```python
"""Pytest configuration and fixtures."""

import pytest
import torch


@pytest.fixture
def sample_batch():
    """Sample batch for testing."""
    batch_size = 4
    images = torch.randn(batch_size, 3, 224, 224)
    labels = torch.randint(0, 10, (batch_size,))
    return images, labels


@pytest.fixture
def mock_datamodule():
    """Mock datamodule for testing."""
    from {project_name}.data.datamodule import CustomDataModule
    return CustomDataModule(data_dir="data/processed", batch_size=4)
```

#### tests/test_model.py

```python
"""Tests for model."""

import torch
import pytest
from {project_name}.models.model import LitModel


def test_model_forward(sample_batch):
    """Test model forward pass."""
    model = LitModel(num_classes=10)
    images, _ = sample_batch

    output = model(images)

    assert output.shape == (4, 10)
    assert not torch.isnan(output).any()
    assert not torch.isinf(output).any()


def test_model_training_step(sample_batch):
    """Test training step."""
    model = LitModel(num_classes=10)
    images, labels = sample_batch

    loss = model.training_step((images, labels), batch_idx=0)

    assert loss.item() > 0
    assert not torch.isnan(loss)


def test_model_save_load(tmp_path):
    """Test model checkpoint save/load."""
    model = LitModel(num_classes=10)

    # Save
    checkpoint_path = tmp_path / "model.ckpt"
    torch.save(model.state_dict(), checkpoint_path)

    # Load
    loaded_model = LitModel(num_classes=10)
    loaded_model.load_state_dict(torch.load(checkpoint_path))

    # Compare
    for p1, p2 in zip(model.parameters(), loaded_model.parameters()):
        assert torch.allclose(p1, p2)
```

### Step 8: Generate CI/CD Pipeline

#### .github/workflows/ci.yml

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"

    - name: Lint with ruff
      run: ruff check src/ tests/

    - name: Format check with black
      run: black --check src/ tests/

    - name: Type check with mypy
      run: mypy src/

    - name: Test with pytest
      run: pytest tests/ --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Success Criteria

Project scaffold is complete when:

- [ ] **Structure**: All directories and files created
- [ ] **Dependencies**: Requirements file complete and installable
- [ ] **Code**: Core modules implemented with docstrings and type hints
- [ ] **Configuration**: Hydra configs working
- [ ] **Tests**: Basic tests passing
- [ ] **CI/CD**: Pipeline configured and passing
- [ ] **Documentation**: README complete with examples
- [ ] **Quality**: Pre-commit hooks configured

## Post-Scaffold Checklist

- [ ] Update README with project-specific details
- [ ] Add LICENSE file
- [ ] Configure pre-commit hooks (`pre-commit install`)
- [ ] Set up experiment tracking (W&B account, etc.)
- [ ] Add data download script if needed
- [ ] Update model architecture for specific task
- [ ] Configure CI/CD secrets
- [ ] Create initial git commit
- [ ] Push to remote repository

## Best Practices

### From PyTorch Lightning
- Use DataModules for data handling
- Leverage built-in callbacks
- Log metrics consistently
- Use mixed precision training

### From HuggingFace
- Clear model interfaces
- Comprehensive docstrings
- Type hints throughout
- Extensive testing

### From Google Research
- Reproducible experiments (seed everything)
- Configuration management (Hydra)
- Experiment tracking (W&B)
- Code quality tools (black, ruff, mypy)

## Customization Guide

**For Computer Vision:**
- Use torchvision models and transforms
- Add albumentations for advanced augmentation
- Consider timm for more model options

**For NLP:**
- Use HuggingFace transformers
- Add tokenizers and datasets libraries
- Consider Flash Attention for efficiency

**For Tabular:**
- Use scikit-learn or XGBoost
- Add feature engineering utilities
- Consider RAPIDS for GPU acceleration

**For Reinforcement Learning:**
- Use stable-baselines3 or CleanRL
- Add environment wrappers
- Implement replay buffers
