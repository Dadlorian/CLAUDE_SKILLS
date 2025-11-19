# Hyperparameter Tuning Guide

A comprehensive guide to hyperparameter optimization techniques, frameworks, and production workflows for machine learning models.

## Table of Contents

1. [Overview](#overview)
2. [Grid Search](#grid-search)
3. [Random Search](#random-search)
4. [Bayesian Optimization](#bayesian-optimization)
5. [Optuna Framework](#optuna-framework)
6. [Ray Tune for Distributed Tuning](#ray-tune-for-distributed-tuning)
7. [Learning Rate Finding](#learning-rate-finding)
8. [Neural Architecture Search](#neural-architecture-search)
9. [Early Stopping Strategies](#early-stopping-strategies)
10. [Trial Pruning](#trial-pruning)
11. [Multi-Objective Optimization](#multi-objective-optimization)
12. [Budget-Aware Tuning](#budget-aware-tuning)
13. [Production Workflows](#production-workflows)
14. [Best Practices](#best-practices)

---

## Overview

Hyperparameter tuning is the process of finding the optimal hyperparameter configuration for a machine learning model. Unlike model parameters (weights/biases) that are learned during training, hyperparameters are set before training begins.

### Key Concepts

- **Search Space**: The range of hyperparameter values to explore
- **Objective Function**: The metric to optimize (e.g., accuracy, F1 score)
- **Sampling Strategy**: How to select hyperparameter combinations
- **Stopping Criterion**: When to terminate the search

### Common Hyperparameters by Model Type

| Model Type | Hyperparameters |
|-----------|-----------------|
| Tree-based | max_depth, min_samples_split, learning_rate, n_estimators |
| SVM | C, kernel, gamma, degree |
| Neural Networks | learning_rate, batch_size, hidden_units, dropout |
| Boosting | learning_rate, n_estimators, subsample, colsample_bytree |

---

## Grid Search

Grid search exhaustively evaluates all combinations of specified hyperparameter values. While computationally expensive, it guarantees finding the best combination within the defined grid.

### When to Use

- Small search space (2-4 hyperparameters)
- Well-defined parameter ranges
- Computing resources are available
- Reproducibility is critical

### Example: Grid Search with Scikit-learn

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import pandas as pd

# Generate sample data
X, y = make_classification(n_samples=1000, n_features=20, n_classes=2, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define parameter grid
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [10, 20, 30, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['sqrt', 'log2']
}

# Initialize model
rf = RandomForestClassifier(random_state=42, n_jobs=-1)

# Perform grid search
grid_search = GridSearchCV(
    estimator=rf,
    param_grid=param_grid,
    cv=5,
    scoring='f1',
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train, y_train)

# Results
print(f"Best parameters: {grid_search.best_params_}")
print(f"Best cross-validation score: {grid_search.best_score_:.4f}")
print(f"Test set score: {grid_search.score(X_test, y_test):.4f}")

# Analyze results
results_df = pd.DataFrame(grid_search.cv_results_)
print("\nTop 5 parameter combinations:")
print(results_df[['param_n_estimators', 'param_max_depth', 'param_min_samples_split',
                   'mean_test_score', 'std_test_score']].nlargest(5, 'mean_test_score'))
```

### Grid Search Visualization

```python
import matplotlib.pyplot as plt
import numpy as np

# Visualize hyperparameter impact
results_df = pd.DataFrame(grid_search.cv_results_)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: n_estimators vs score
n_est_scores = results_df.groupby('param_n_estimators')['mean_test_score'].mean()
axes[0, 0].plot(n_est_scores.index, n_est_scores.values, marker='o')
axes[0, 0].set_xlabel('n_estimators')
axes[0, 0].set_ylabel('Mean Test Score')
axes[0, 0].set_title('Impact of n_estimators')
axes[0, 0].grid(True, alpha=0.3)

# Plot 2: max_depth vs score
max_depth_scores = results_df.groupby('param_max_depth')['mean_test_score'].mean()
axes[0, 1].plot(max_depth_scores.index, max_depth_scores.values, marker='s')
axes[0, 1].set_xlabel('max_depth')
axes[0, 1].set_ylabel('Mean Test Score')
axes[0, 1].set_title('Impact of max_depth')
axes[0, 1].grid(True, alpha=0.3)

# Plot 3: Heatmap of two parameters
pivot_data = results_df.pivot_table(
    values='mean_test_score',
    index='param_n_estimators',
    columns='param_max_depth'
)
im = axes[1, 0].imshow(pivot_data.values, cmap='viridis', aspect='auto')
axes[1, 0].set_xlabel('max_depth')
axes[1, 0].set_ylabel('n_estimators')
axes[1, 0].set_title('n_estimators vs max_depth')
plt.colorbar(im, ax=axes[1, 0])

# Plot 4: Parameter importance
results_df['mean_test_score'].hist(ax=axes[1, 1], bins=20, edgecolor='black')
axes[1, 1].set_xlabel('Mean Test Score')
axes[1, 1].set_ylabel('Frequency')
axes[1, 1].set_title('Distribution of Test Scores')

plt.tight_layout()
plt.savefig('grid_search_results.png', dpi=300)
plt.show()
```

---

## Random Search

Random search samples hyperparameter combinations randomly from the search space. It's more efficient than grid search, especially for high-dimensional spaces, and often performs comparably or better.

### When to Use

- Large search space with many hyperparameters
- Some parameters are more important than others
- Limited computational budget
- Exploring unknown search spaces

### Example: Random Search

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint, uniform

# Define parameter distributions
param_dist = {
    'n_estimators': randint(50, 300),
    'max_depth': [10, 20, 30, 40, 50, None],
    'min_samples_split': randint(2, 20),
    'min_samples_leaf': randint(1, 10),
    'max_features': ['sqrt', 'log2'],
    'bootstrap': [True, False]
}

# Random search
random_search = RandomizedSearchCV(
    estimator=rf,
    param_distributions=param_dist,
    n_iter=50,  # Number of parameter combinations to try
    cv=5,
    scoring='f1',
    n_jobs=-1,
    random_state=42,
    verbose=1
)

random_search.fit(X_train, y_train)

print(f"Best parameters: {random_search.best_params_}")
print(f"Best cross-validation score: {random_search.best_score_:.4f}")
print(f"Test set score: {random_search.score(X_test, y_test):.4f}")
```

### Random Search Efficiency Analysis

```python
# Compare grid search vs random search efficiency
import time

start_time = time.time()
random_search.fit(X_train, y_train)
random_time = time.time() - start_time

print(f"Random Search Time: {random_time:.2f}s")
print(f"Combinations Tested: {len(random_search.cv_results_['params'])}")
print(f"Average Time per Combination: {random_time / 50:.2f}s")

# Plot convergence
results_df = pd.DataFrame(random_search.cv_results_)
results_df['rank_test_score_cummin'] = results_df['rank_test_score'].cummin()

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(results_df.index, results_df['mean_test_score'], alpha=0.6, label='Individual Trial')
ax.plot(results_df.index, results_df['mean_test_score'].expanding().max(),
        label='Best Score So Far', linewidth=2)
ax.set_xlabel('Iteration')
ax.set_ylabel('Test Score')
ax.set_title('Random Search Convergence')
ax.legend()
ax.grid(True, alpha=0.3)
plt.savefig('random_search_convergence.png', dpi=300)
plt.show()
```

---

## Bayesian Optimization

Bayesian optimization builds a probabilistic model (surrogate) of the objective function and uses it to intelligently select which hyperparameters to evaluate next. It's more sample-efficient than grid or random search.

### How It Works

1. **Initialization**: Evaluate random parameter combinations
2. **Model Building**: Fit a Gaussian Process or other surrogate model
3. **Acquisition Function**: Calculate expected improvement for untested parameters
4. **Selection**: Evaluate parameters with highest expected improvement
5. **Update**: Retrain the model with new data
6. **Repeat**: Continue until convergence or budget exhausted

### Example: Bayesian Optimization with Scikit-Optimize

```python
from skopt import gp_minimize, space
from skopt.utils import use_named_args
from skopt.plots import plot_convergence, plot_evaluations
import numpy as np

# Define search space
search_space = [
    space.Integer(50, 300, name='n_estimators'),
    space.Integer(10, 50, name='max_depth'),
    space.Integer(2, 20, name='min_samples_split'),
    space.Integer(1, 10, name='min_samples_leaf'),
]

# Define objective function
@use_named_args(search_space)
def objective(**params):
    """Objective function to minimize (negative score)"""
    model = RandomForestClassifier(
        random_state=42,
        n_jobs=-1,
        **params
    )

    # Use cross-validation
    from sklearn.model_selection import cross_val_score
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1')

    # Return negative score (we want to maximize F1)
    return -scores.mean()

# Perform Bayesian optimization
result = gp_minimize(
    func=objective,
    dimensions=search_space,
    base_estimator='GP',  # Gaussian Process
    acq_func='EI',  # Expected Improvement
    n_calls=30,
    n_initial_points=10,
    random_state=42,
    verbose=1
)

print(f"Best parameters: {result.x}")
print(f"Best score: {-result.fun:.4f}")

# Visualize results
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
plot_convergence(result, ax=axes[0, 0])
plot_evaluations(result, axes=axes.ravel()[1:])
plt.tight_layout()
plt.savefig('bayesian_optimization_results.png', dpi=300)
plt.show()
```

### Acquisition Functions Explained

```python
"""
Common Acquisition Functions:

1. Expected Improvement (EI):
   - Balances exploration and exploitation
   - Default choice for many applications
   - Formula: E[max(0, f(x) - f_best))]

2. Probability of Improvement (PI):
   - Simpler than EI, focuses on finding better points
   - Can get stuck in local regions

3. Upper Confidence Bound (UCB):
   - Combines mean and uncertainty
   - Good for exploration-heavy tasks
   - Formula: mean(x) + kappa * std(x)

4. Thompson Sampling:
   - Probabilistic approach
   - Good balance of exploration/exploitation
"""

# Example with different acquisition functions
from skopt import gp_minimize

for acq_func in ['EI', 'PI', 'UCB']:
    result = gp_minimize(
        func=objective,
        dimensions=search_space,
        acq_func=acq_func,
        n_calls=30,
        n_initial_points=10,
        random_state=42
    )
    print(f"{acq_func}: Best score = {-result.fun:.4f}")
```

---

## Optuna Framework

Optuna is a modern hyperparameter optimization framework with advanced features like pruning, parallelization, and SQL-based storage.

### Why Optuna?

- **Efficient Sampling**: TPE (Tree-structured Parzen Estimator) sampler
- **Pruning**: Automatically stops unpromising trials
- **Parallelization**: Easy distributed tuning
- **Flexible**: Supports any objective function
- **Visualization**: Built-in dashboards and plots

### Basic Optuna Example

```python
import optuna
from optuna.trial import Trial
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

def objective(trial: Trial) -> float:
    """Define the objective function for Optuna"""

    # Suggest hyperparameters
    n_estimators = trial.suggest_int('n_estimators', 50, 300)
    max_depth = trial.suggest_int('max_depth', 10, 50)
    min_samples_split = trial.suggest_int('min_samples_split', 2, 20)
    min_samples_leaf = trial.suggest_int('min_samples_leaf', 1, 10)
    max_features = trial.suggest_categorical('max_features', ['sqrt', 'log2'])

    # Create model
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        max_features=max_features,
        random_state=42,
        n_jobs=-1
    )

    # Evaluate with cross-validation
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1')
    return scores.mean()

# Create a study
study = optuna.create_study(
    direction='maximize',  # Maximize F1 score
    sampler=optuna.samplers.TPESampler(seed=42)
)

# Optimize
study.optimize(objective, n_trials=50, show_progress_bar=True)

# Results
print(f"Best Trial: {study.best_trial.number}")
print(f"Best Score: {study.best_value:.4f}")
print(f"Best Parameters: {study.best_params}")
```

### Advanced Optuna Features

```python
import optuna
from optuna.pruners import MedianPruner
from optuna.trial import TrialState

def objective_with_pruning(trial: Trial) -> float:
    """Objective function with pruning support"""

    n_estimators = trial.suggest_int('n_estimators', 50, 300)
    max_depth = trial.suggest_int('max_depth', 10, 50)

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42,
        n_jobs=-1
    )

    # Incremental evaluation for pruning
    from sklearn.model_selection import StratifiedKFold
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    scores = []
    for fold, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train)):
        X_fold_train, X_fold_val = X_train[train_idx], X_train[val_idx]
        y_fold_train, y_fold_val = y_train[train_idx], y_train[val_idx]

        model.fit(X_fold_train, y_fold_train)
        score = model.score(X_fold_val, y_fold_val)
        scores.append(score)

        # Report intermediate value for pruning
        trial.report(np.mean(scores), fold)

        # Check if trial should be pruned
        if trial.should_prune():
            raise optuna.TrialPruned()

    return np.mean(scores)

# Create study with pruning
study = optuna.create_study(
    direction='maximize',
    sampler=optuna.samplers.TPESampler(seed=42),
    pruner=optuna.pruners.MedianPruner(n_warmup_steps=5)
)

study.optimize(objective_with_pruning, n_trials=50)

# Analyze optimization history
trials_df = study.trials_dataframe()
print("\nTop 10 trials:")
print(trials_df.nlargest(10, 'value')[['number', 'value', 'state']])
```

### Optuna Visualization Dashboard

```python
import optuna
from optuna.visualization import plot_param_importances, plot_optimization_history

# Generate visualization plots
fig1 = optuna.visualization.plot_optimization_history(study).show()
fig2 = optuna.visualization.plot_param_importances(study).show()
fig3 = optuna.visualization.plot_slice(study).show()
fig4 = optuna.visualization.plot_parallel_coordinates(study).show()

# Access plots programmatically
optimization_history = optuna.visualization.plot_optimization_history(study)
param_importances = optuna.visualization.plot_param_importances(study)

# Save as HTML
optimization_history.write_html('optimization_history.html')
param_importances.write_html('param_importances.html')
```

### Multi-Study Analysis

```python
# Store results in different studies for comparison
studies = {}

for sampler_name, sampler in {
    'TPE': optuna.samplers.TPESampler(seed=42),
    'CMA-ES': optuna.samplers.CmaEsSampler(seed=42),
    'Random': optuna.samplers.RandomSampler(seed=42)
}.items():
    study = optuna.create_study(
        direction='maximize',
        sampler=sampler,
        study_name=sampler_name
    )
    study.optimize(objective, n_trials=30, show_progress_bar=False)
    studies[sampler_name] = study

# Compare samplers
fig, ax = plt.subplots(figsize=(12, 6))

for sampler_name, study in studies.items():
    best_scores = [study.best_value]
    for trial in study.trials:
        best_scores.append(max(best_scores[-1], trial.value or -float('inf')))
    ax.plot(best_scores[1:], label=sampler_name, marker='o')

ax.set_xlabel('Trial Number')
ax.set_ylabel('Best Score So Far')
ax.set_title('Sampler Comparison')
ax.legend()
ax.grid(True, alpha=0.3)
plt.savefig('sampler_comparison.png', dpi=300)
plt.show()
```

---

## Ray Tune for Distributed Tuning

Ray Tune is a scalable hyperparameter tuning library that supports distributed training across multiple machines.

### When to Use Ray Tune

- Large-scale hyperparameter searches
- Distributed training needed
- Population-based training (PBT)
- Multi-GPU/multi-node setups

### Basic Ray Tune Example

```python
from ray import tune, air
from ray.tune import CLIReporter
from ray.air import session, Checkpoint
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
import numpy as np

def train_function(config):
    """Training function for Ray Tune"""

    # Create model with config parameters
    model = RandomForestClassifier(
        n_estimators=config['n_estimators'],
        max_depth=config['max_depth'],
        min_samples_split=config['min_samples_split'],
        min_samples_leaf=config['min_samples_leaf'],
        max_features=config['max_features'],
        random_state=42,
        n_jobs=-1
    )

    # Train and evaluate
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1')

    # Report back to Ray Tune
    session.report({"f1_score": scores.mean()})

# Define search space
search_space = {
    'n_estimators': tune.randint(50, 300),
    'max_depth': tune.randint(10, 50),
    'min_samples_split': tune.randint(2, 20),
    'min_samples_leaf': tune.randint(1, 10),
    'max_features': tune.choice(['sqrt', 'log2'])
}

# Configure tuner
tuner = tune.Tuner(
    train_function,
    param_space=search_space,
    tune_config=tune.TuneConfig(
        num_samples=50,  # Number of trials
        max_concurrent_trials=4,  # Parallel trials
        metric='f1_score',
        mode='max'
    ),
    run_config=air.RunConfig(
        name='rf_tuning',
        verbose=1
    )
)

# Run optimization
results = tuner.fit()

# Get best result
best_result = results.get_best_result(metric='f1_score', mode='max')
print(f"Best trial config: {best_result.config}")
print(f"Best F1 Score: {best_result.metrics['f1_score']:.4f}")
```

### Population-Based Training (PBT)

```python
from ray.tune import PopulationBasedTraining
from ray.tune.schedulers import PopulationBasedTrainingScheduler

def train_pbt_function(config):
    """Training function with learning rate scheduling for PBT"""

    model = RandomForestClassifier(
        n_estimators=config['n_estimators'],
        max_depth=config['max_depth'],
        random_state=42,
        n_jobs=-1
    )

    # Simulate iterative training
    for epoch in range(10):
        scores = cross_val_score(model, X_train, y_train, cv=3, scoring='f1')

        # Report metric for PBT to make decisions
        session.report({"f1_score": scores.mean(), "epoch": epoch})

# Configure PBT scheduler
pbt_scheduler = PopulationBasedTraining(
    time_attr='epoch',
    metric='f1_score',
    mode='max',
    perturbation_interval=2,  # Explore every 2 epochs
    hyperparam_mutations={
        'max_depth': [10, 20, 30, 40, 50],
        'n_estimators': [50, 100, 150, 200, 250]
    }
)

# Run with PBT
tuner = tune.Tuner(
    train_pbt_function,
    param_space={
        'n_estimators': tune.choice([50, 100, 150]),
        'max_depth': tune.choice([10, 20, 30])
    },
    tune_config=tune.TuneConfig(
        scheduler=pbt_scheduler,
        num_samples=8
    )
)

results = tuner.fit()
```

### Ray Tune with Checkpointing

```python
from pathlib import Path

def train_with_checkpoint(config):
    """Training with checkpoint support"""

    model = RandomForestClassifier(
        n_estimators=config['n_estimators'],
        max_depth=config['max_depth'],
        random_state=42
    )

    # Training loop
    for epoch in range(5):
        # Train
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)

        # Report metrics
        session.report({"accuracy": score, "epoch": epoch})

        # Checkpoint model
        if epoch % 2 == 0:
            checkpoint_dir = session.get_checkpoint_dir()
            checkpoint_path = Path(checkpoint_dir) / f"model_epoch_{epoch}.pkl"

            import pickle
            with open(checkpoint_path, 'wb') as f:
                pickle.dump(model, f)

            session.report({}, checkpoint=Checkpoint.from_directory(checkpoint_dir))

# Run with checkpointing
tuner = tune.Tuner(
    train_with_checkpoint,
    param_space={
        'n_estimators': tune.randint(50, 200),
        'max_depth': tune.randint(10, 40)
    },
    tune_config=tune.TuneConfig(num_samples=10)
)

results = tuner.fit()
```

---

## Learning Rate Finding

Learning rate is one of the most important hyperparameters for neural networks. LR finding helps identify the optimal learning rate range.

### Learning Rate Range Test

```python
import numpy as np
import torch
import torch.nn as nn
from torch.optim import SGD, Adam
import matplotlib.pyplot as plt

class SimpleNet(nn.Module):
    """Simple neural network for demonstration"""

    def __init__(self, input_size=20, hidden_size=128):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.sigmoid(self.fc3(x))
        return x

class LRFinder:
    """Learning Rate Finder"""

    def __init__(self, model, optimizer, criterion, device='cpu'):
        self.model = model
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device

        self.lrs = []
        self.losses = []

    def find(self, train_loader, start_lr=1e-4, end_lr=10, num_iters=100):
        """Find learning rate range"""

        n_steps = len(train_loader) * num_iters // (num_iters // 10)
        lr_schedule = np.logspace(np.log10(start_lr), np.log10(end_lr), n_steps)

        best_loss = None

        for batch_idx, (X, y) in enumerate(train_loader):
            X = X.to(self.device)
            y = y.to(self.device).float().unsqueeze(1)

            # Update learning rate
            lr = lr_schedule[batch_idx]
            for param_group in self.optimizer.param_groups:
                param_group['lr'] = lr

            # Forward pass
            outputs = self.model(X)
            loss = self.criterion(outputs, y)

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            self.lrs.append(lr)
            self.losses.append(loss.item())

            # Stop if loss diverges
            if best_loss is None:
                best_loss = loss.item()
            elif loss.item() > best_loss * 4:
                break
            elif loss.item() < best_loss:
                best_loss = loss.item()

        return self.lrs, self.losses

    def plot(self):
        """Plot learning rate vs loss"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(self.lrs, self.losses)
        ax.set_xscale('log')
        ax.set_xlabel('Learning Rate')
        ax.set_ylabel('Loss')
        ax.set_title('Learning Rate Finder')
        ax.grid(True, alpha=0.3)
        plt.savefig('lr_finder.png', dpi=300)
        plt.show()

# Prepare data
X_torch = torch.FloatTensor(X_train)
y_torch = torch.LongTensor(y_train)
from torch.utils.data import TensorDataset, DataLoader

dataset = TensorDataset(X_torch, y_torch)
train_loader = DataLoader(dataset, batch_size=32, shuffle=True)

# Find learning rate
model = SimpleNet().to('cpu')
optimizer = Adam(model.parameters(), lr=1e-4)
criterion = nn.BCELoss()

lr_finder = LRFinder(model, optimizer, criterion)
lrs, losses = lr_finder.find(train_loader)
lr_finder.plot()

# Find optimal LR (steepest descent)
optimal_idx = np.argmin(np.gradient(losses))
optimal_lr = lrs[optimal_idx]
print(f"Optimal Learning Rate: {optimal_lr:.2e}")
```

### Cyclic Learning Rate

```python
from torch.optim.lr_scheduler import CyclicLR

def train_with_cyclic_lr(model, train_loader, val_loader, epochs=50):
    """Train with cyclic learning rate"""

    optimizer = Adam(model.parameters(), lr=1e-3)
    criterion = nn.BCELoss()

    # Create cyclic LR scheduler
    scheduler = CyclicLR(
        optimizer,
        base_lr=1e-4,
        max_lr=1e-2,
        step_size_up=len(train_loader) * 5,
        cycle_momentum=False
    )

    train_losses = []
    val_losses = []

    for epoch in range(epochs):
        # Training
        model.train()
        epoch_loss = 0
        for X, y in train_loader:
            X = X.to('cpu')
            y = y.to('cpu').float().unsqueeze(1)

            optimizer.zero_grad()
            outputs = model(X)
            loss = criterion(outputs, y)
            loss.backward()
            optimizer.step()
            scheduler.step()

            epoch_loss += loss.item()

        train_losses.append(epoch_loss / len(train_loader))

        # Validation
        model.eval()
        with torch.no_grad():
            val_loss = 0
            for X, y in val_loader:
                X = X.to('cpu')
                y = y.to('cpu').float().unsqueeze(1)
                outputs = model(X)
                loss = criterion(outputs, y)
                val_loss += loss.item()

            val_losses.append(val_loss / len(val_loader))

        print(f"Epoch {epoch+1}/{epochs}, Train Loss: {train_losses[-1]:.4f}, "
              f"Val Loss: {val_losses[-1]:.4f}")

    return train_losses, val_losses

# Train with cyclic LR
train_losses, val_losses = train_with_cyclic_lr(model, train_loader, None, epochs=10)
```

---

## Neural Architecture Search

Neural Architecture Search (NAS) automatically designs neural network architectures.

### Simple Evolutionary NAS

```python
import random
from typing import List, Dict
import torch
import torch.nn as nn
from copy import deepcopy

class Architecture:
    """Represents a neural network architecture"""

    def __init__(self):
        self.layers = []
        self.hidden_units = []

    def add_layer(self, layer_type, **kwargs):
        self.layers.append({'type': layer_type, 'params': kwargs})

    def mutate(self):
        """Randomly mutate the architecture"""
        mutation_type = random.choice(['add', 'remove', 'modify'])

        if mutation_type == 'add' and len(self.layers) < 5:
            layer_type = random.choice(['dense', 'conv'])
            units = random.choice([32, 64, 128, 256])
            self.add_layer(layer_type, units=units)

        elif mutation_type == 'remove' and len(self.layers) > 1:
            self.layers.pop(random.randint(0, len(self.layers) - 1))

        elif mutation_type == 'modify' and self.layers:
            idx = random.randint(0, len(self.layers) - 1)
            self.layers[idx]['params']['units'] = random.choice([32, 64, 128, 256])

    def crossover(self, other: 'Architecture') -> 'Architecture':
        """Create child architecture from two parents"""
        child = Architecture()
        crossover_point = random.randint(1, max(len(self.layers), len(other.layers)))

        child.layers = self.layers[:crossover_point] + other.layers[crossover_point:]
        return child

class EvolutionaryNAS:
    """Evolutionary Neural Architecture Search"""

    def __init__(self, population_size=10, generations=20):
        self.population_size = population_size
        self.generations = generations
        self.population = []
        self.fitness_scores = []

    def initialize_population(self):
        """Initialize random population"""
        for _ in range(self.population_size):
            arch = Architecture()
            for _ in range(random.randint(2, 4)):
                arch.add_layer('dense', units=random.choice([64, 128, 256]))
            self.population.append(arch)

    def evaluate_fitness(self, arch: Architecture) -> float:
        """Evaluate architecture fitness (mock evaluation)"""
        # In practice, train the architecture and return validation accuracy
        # For now, use number of parameters as a proxy
        params = sum(arch.layers[i]['params'].get('units', 1) for i in range(len(arch.layers)))
        return params / 1000  # Normalize

    def evolve(self):
        """Run evolutionary algorithm"""
        self.initialize_population()

        for generation in range(self.generations):
            # Evaluate fitness
            self.fitness_scores = [self.evaluate_fitness(arch) for arch in self.population]

            # Select top architectures
            sorted_indices = sorted(range(len(self.fitness_scores)),
                                   key=lambda i: self.fitness_scores[i], reverse=True)
            elite = [self.population[i] for i in sorted_indices[:2]]

            # Create new population
            new_population = deepcopy(elite)

            while len(new_population) < self.population_size:
                if random.random() < 0.3:
                    # Mutation
                    parent = random.choice(elite)
                    child = deepcopy(parent)
                    child.mutate()
                    new_population.append(child)
                else:
                    # Crossover
                    parent1, parent2 = random.sample(elite, 2)
                    child = parent1.crossover(parent2)
                    new_population.append(child)

            self.population = new_population[:self.population_size]

            best_fitness = max(self.fitness_scores)
            print(f"Generation {generation+1}: Best Fitness = {best_fitness:.4f}")

        # Return best architecture
        best_idx = self.fitness_scores.index(max(self.fitness_scores))
        return self.population[best_idx]

# Run NAS
nas = EvolutionaryNAS(population_size=10, generations=5)
best_arch = nas.evolve()
print(f"\nBest Architecture Layers: {best_arch.layers}")
```

### Neural Architecture Search with Optuna

```python
import optuna
from optuna.trial import Trial

def objective_nas(trial: Trial) -> float:
    """NAS objective for Optuna"""

    # Suggest architecture
    n_layers = trial.suggest_int('n_layers', 2, 5)

    layers = []
    for i in range(n_layers):
        units = trial.suggest_int(f'layer_{i}_units', 32, 512, step=32)
        dropout = trial.suggest_float(f'layer_{i}_dropout', 0.0, 0.5, step=0.1)
        layers.append({'units': units, 'dropout': dropout})

    learning_rate = trial.suggest_float('learning_rate', 1e-4, 1e-2, log=True)
    batch_size = trial.suggest_categorical('batch_size', [16, 32, 64])

    # Build model
    model = nn.Sequential()
    input_size = 20

    for i, layer_config in enumerate(layers):
        model.add_module(f'layer_{i}', nn.Linear(input_size, layer_config['units']))
        model.add_module(f'relu_{i}', nn.ReLU())
        model.add_module(f'dropout_{i}', nn.Dropout(layer_config['dropout']))
        input_size = layer_config['units']

    model.add_module('output', nn.Linear(input_size, 1))
    model.add_module('sigmoid', nn.Sigmoid())

    # Train and evaluate (simplified)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.BCELoss()

    # Simple training loop
    X_torch = torch.FloatTensor(X_train)
    y_torch = torch.FloatTensor(y_train).unsqueeze(1)

    for epoch in range(5):
        optimizer.zero_grad()
        outputs = model(X_torch)
        loss = criterion(outputs, y_torch)
        loss.backward()
        optimizer.step()

    # Evaluate
    model.eval()
    with torch.no_grad():
        X_test_torch = torch.FloatTensor(X_test)
        y_test_torch = torch.FloatTensor(y_test).unsqueeze(1)
        outputs = model(X_test_torch)
        accuracy = (outputs.round() == y_test_torch).float().mean().item()

    return accuracy

# Create study for NAS
study = optuna.create_study(direction='maximize')
study.optimize(objective_nas, n_trials=20)

print(f"Best Architecture:")
for param, value in study.best_params.items():
    print(f"  {param}: {value}")
print(f"Best Accuracy: {study.best_value:.4f}")
```

---

## Early Stopping Strategies

Early stopping prevents overfitting by halting training when validation performance plateaus.

### Validation-Based Early Stopping

```python
class EarlyStopping:
    """Early stopping to prevent overfitting"""

    def __init__(self, patience=10, min_delta=0.0, restore_best_weights=True):
        """
        Args:
            patience: Number of checks with no improvement after which training stops
            min_delta: Minimum change to qualify as an improvement
            restore_best_weights: Whether to restore best weights
        """
        self.patience = patience
        self.min_delta = min_delta
        self.restore_best_weights = restore_best_weights

        self.best_score = None
        self.counter = 0
        self.best_epoch = 0
        self.best_weights = None

    def __call__(self, val_score, model):
        """Check if training should stop"""

        if self.best_score is None:
            self.best_score = val_score
            self.best_weights = deepcopy(model.state_dict())
        elif val_score > self.best_score + self.min_delta:
            self.best_score = val_score
            self.counter = 0
            self.best_weights = deepcopy(model.state_dict())
            return False  # Continue training
        else:
            self.counter += 1
            if self.counter >= self.patience:
                if self.restore_best_weights:
                    model.load_state_dict(self.best_weights)
                return True  # Stop training

        return False

def train_with_early_stopping(model, train_loader, val_loader, epochs=100, patience=10):
    """Train with early stopping"""

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.BCELoss()
    early_stop = EarlyStopping(patience=patience)

    train_losses = []
    val_losses = []

    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss = 0
        for X, y in train_loader:
            X = X.to('cpu')
            y = y.to('cpu').float().unsqueeze(1)

            optimizer.zero_grad()
            outputs = model(X)
            loss = criterion(outputs, y)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        train_loss /= len(train_loader)
        train_losses.append(train_loss)

        # Validation phase
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for X, y in val_loader:
                X = X.to('cpu')
                y = y.to('cpu').float().unsqueeze(1)
                outputs = model(X)
                loss = criterion(outputs, y)
                val_loss += loss.item()

        val_loss /= len(val_loader)
        val_losses.append(val_loss)

        print(f"Epoch {epoch+1}/{epochs}, Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

        # Check early stopping
        if early_stop(val_loss, model):
            print(f"Early stopping at epoch {epoch+1}")
            break

    return train_losses, val_losses

# Train with early stopping
from sklearn.model_selection import train_test_split

X_torch = torch.FloatTensor(X_train)
y_torch = torch.LongTensor(y_train)

X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(
    X_torch, y_torch, test_size=0.2, random_state=42
)

train_dataset = TensorDataset(X_train_split, y_train_split)
val_dataset = TensorDataset(X_val_split, y_val_split)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32)

model = SimpleNet()
train_losses, val_losses = train_with_early_stopping(model, train_loader, val_loader)
```

### Patience and Warmup

```python
class AdaptiveEarlyStopping(EarlyStopping):
    """Early stopping with adaptive patience"""

    def __init__(self, initial_patience=5, max_patience=20, warmup_epochs=5):
        super().__init__(patience=initial_patience)
        self.max_patience = max_patience
        self.warmup_epochs = warmup_epochs
        self.epochs_trained = 0

    def __call__(self, val_score, model):
        self.epochs_trained += 1

        # Warmup phase: don't stop too early
        if self.epochs_trained < self.warmup_epochs:
            return False

        # Increase patience if no improvement yet
        if self.counter == 0 and self.patience < self.max_patience:
            self.patience = min(self.patience + 1, self.max_patience)

        return super().__call__(val_score, model)
```

---

## Trial Pruning

Pruning stops unpromising trials early to save computational resources.

### Pruning with Optuna

```python
import optuna
from optuna.pruners import MedianPruner, PercentilePruner, SuccessiveHalvingPruner

def objective_with_pruning(trial: Trial) -> float:
    """Objective function that reports intermediate values for pruning"""

    n_estimators = trial.suggest_int('n_estimators', 50, 300)
    max_depth = trial.suggest_int('max_depth', 10, 50)

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42,
        n_jobs=-1
    )

    # Simulate iterative training with intermediate evaluations
    from sklearn.model_selection import StratifiedKFold
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    scores = []
    for fold, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train)):
        X_fold_train, X_fold_val = X_train[train_idx], X_train[val_idx]
        y_fold_train, y_fold_val = y_train[train_idx], y_train[val_idx]

        model.fit(X_fold_train, y_fold_train)
        score = model.score(X_fold_val, y_fold_val)
        scores.append(score)

        # Report intermediate value
        trial.report(np.mean(scores), fold)

        # Check if trial should be pruned
        if trial.should_prune():
            raise optuna.TrialPruned()

    return np.mean(scores)

# Different pruning strategies
pruners = {
    'MedianPruner': MedianPruner(n_warmup_steps=3),
    'PercentilePruner': PercentilePruner(percentile=50, n_warmup_steps=3),
    'SuccessiveHalvingPruner': SuccessiveHalvingPruner()
}

for pruner_name, pruner in pruners.items():
    study = optuna.create_study(
        direction='maximize',
        pruner=pruner,
        study_name=pruner_name
    )

    study.optimize(objective_with_pruning, n_trials=30, show_progress_bar=False)

    # Statistics
    complete = sum(1 for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE)
    pruned = sum(1 for t in study.trials if t.state == optuna.trial.TrialState.PRUNED)

    print(f"\n{pruner_name}:")
    print(f"  Best score: {study.best_value:.4f}")
    print(f"  Complete trials: {complete}")
    print(f"  Pruned trials: {pruned}")
```

### Successive Halving Pruning

```python
from optuna.pruners import SuccessiveHalvingPruner

def objective_successive_halving(trial: Trial) -> float:
    """Objective with multiple stages for successive halving"""

    config = {
        'learning_rate': trial.suggest_float('learning_rate', 1e-4, 1e-2, log=True),
        'batch_size': trial.suggest_categorical('batch_size', [16, 32, 64]),
        'hidden_units': trial.suggest_int('hidden_units', 32, 512, step=32)
    }

    # Simulate multi-stage training
    scores = []
    for stage in range(5):
        # Train for this stage
        score = np.random.random()  # In practice, actual training
        scores.append(score)

        # Report intermediate result
        trial.report(np.mean(scores), stage)

        # Prune if not promising
        if trial.should_prune():
            raise optuna.TrialPruned()

    return np.mean(scores)

study = optuna.create_study(
    direction='maximize',
    pruner=SuccessiveHalvingPruner(),
    sampler=optuna.samplers.TPESampler(seed=42)
)

study.optimize(objective_successive_halving, n_trials=30)
```

---

## Multi-Objective Optimization

Optimize multiple objectives simultaneously (e.g., accuracy and model size).

### Multi-Objective Optimization with Optuna

```python
import optuna
from optuna.trial import Trial

def multi_objective(trial: Trial) -> tuple:
    """Multi-objective function returning (accuracy, model_size)"""

    n_layers = trial.suggest_int('n_layers', 2, 5)
    layers = []
    total_params = 0

    for i in range(n_layers):
        units = trial.suggest_int(f'layer_{i}_units', 32, 512, step=32)
        dropout = trial.suggest_float(f'layer_{i}_dropout', 0.0, 0.5)
        layers.append({'units': units, 'dropout': dropout})

        # Estimate parameters
        if i == 0:
            total_params += 20 * units
        else:
            total_params += layers[i-1]['units'] * units

    # Create and train model
    model = nn.Sequential()
    input_size = 20

    for i, layer_config in enumerate(layers):
        model.add_module(f'layer_{i}', nn.Linear(input_size, layer_config['units']))
        model.add_module(f'relu_{i}', nn.ReLU())
        model.add_module(f'dropout_{i}', nn.Dropout(layer_config['dropout']))
        input_size = layer_config['units']

    model.add_module('output', nn.Linear(input_size, 1))

    # Train
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.BCEWithLogitsLoss()

    X_torch = torch.FloatTensor(X_train)
    y_torch = torch.FloatTensor(y_train).unsqueeze(1)

    for _ in range(5):
        optimizer.zero_grad()
        outputs = model(X_torch)
        loss = criterion(outputs, y_torch)
        loss.backward()
        optimizer.step()

    # Evaluate
    model.eval()
    with torch.no_grad():
        X_test_torch = torch.FloatTensor(X_test)
        y_test_torch = torch.FloatTensor(y_test).unsqueeze(1)
        outputs = model(X_test_torch)
        accuracy = (outputs.round() == y_test_torch).float().mean().item()

    # Normalize model size (smaller is better)
    model_size_penalty = total_params / 100000  # Normalize

    # Return both objectives
    return accuracy, -model_size_penalty  # Negative because we want to minimize size

# Create study with multiple objectives
sampler = optuna.samplers.NSGAIISampler()

study = optuna.create_study(
    directions=['maximize', 'maximize'],  # Maximize accuracy and minimize size
    sampler=sampler,
    study_name='pareto_optimization'
)

study.optimize(multi_objective, n_trials=30, show_progress_bar=True)

# Analyze Pareto front
trials_df = study.trials_dataframe()
print("\nPareto Front Trials:")
print(trials_df[['number', 'value_0', 'value_1']].tail(10))

# Visualize Pareto front
pareto_trials = study.get_pareto_front_trials()
accuracies = [t.values[0] for t in pareto_trials]
sizes = [-t.values[1] for t in pareto_trials]

plt.figure(figsize=(10, 6))
plt.scatter(sizes, accuracies, s=100, alpha=0.6)
plt.xlabel('Model Size (normalized)')
plt.ylabel('Accuracy')
plt.title('Pareto Front: Accuracy vs Model Size')
plt.grid(True, alpha=0.3)
plt.savefig('pareto_front.png', dpi=300)
plt.show()
```

### Constraint-Based Multi-Objective

```python
def constrained_objective(trial: Trial):
    """Multi-objective with constraints"""

    x = trial.suggest_float('x', -10, 10)
    y = trial.suggest_float('y', -10, 10)

    # Objectives
    obj1 = x ** 2 + y ** 2
    obj2 = (x - 2) ** 2 + (y - 2) ** 2

    # Constraint: x + y <= 5
    constraint = x + y - 5

    # Apply constraint as penalty
    if constraint > 0:
        obj1 += constraint * 100
        obj2 += constraint * 100

    return obj1, obj2

study = optuna.create_study(
    directions=['minimize', 'minimize'],
    sampler=optuna.samplers.NSGAIISampler()
)

study.optimize(constrained_objective, n_trials=100)
```

---

## Budget-Aware Tuning

Optimize hyperparameters while respecting computational/financial budgets.

### Time and Cost-Aware Tuning

```python
import time
from typing import Callable, Dict, Any

class BudgetAwareTuner:
    """Hyperparameter tuner that respects time and resource budgets"""

    def __init__(self,
                 objective: Callable,
                 budget_seconds: float = 3600,
                 max_trials: int = 100,
                 cost_per_trial: float = 1.0):
        """
        Args:
            objective: Function to optimize
            budget_seconds: Maximum time budget in seconds
            max_trials: Maximum number of trials
            cost_per_trial: Estimated cost per trial (for resource budgeting)
        """
        self.objective = objective
        self.budget_seconds = budget_seconds
        self.max_trials = max_trials
        self.cost_per_trial = cost_per_trial

        self.start_time = None
        self.trials_completed = 0
        self.total_cost = 0

    def remaining_budget(self) -> tuple:
        """Return (remaining_time_seconds, remaining_trials)"""
        elapsed = time.time() - self.start_time
        remaining_time = max(0, self.budget_seconds - elapsed)
        remaining_trials = max(0, self.max_trials - self.trials_completed)
        return remaining_time, remaining_trials

    def has_budget(self) -> bool:
        """Check if budget is available"""
        remaining_time, remaining_trials = self.remaining_budget()
        return remaining_time > 0 and remaining_trials > 0

    def run(self, param_suggestions: list) -> Dict[str, Any]:
        """Run optimization with budget constraints"""
        self.start_time = time.time()

        best_value = float('inf')
        best_params = None

        trial_number = 0
        while self.has_budget() and trial_number < len(param_suggestions):
            remaining_time, remaining_trials = self.remaining_budget()

            print(f"\nTrial {trial_number + 1}")
            print(f"  Remaining budget: {remaining_time:.1f}s, {remaining_trials} trials")

            # Time the trial
            trial_start = time.time()

            try:
                params = param_suggestions[trial_number]
                value = self.objective(params)

                trial_time = time.time() - trial_start

                if value < best_value:
                    best_value = value
                    best_params = params

                self.trials_completed += 1
                self.total_cost += self.cost_per_trial

                print(f"  Value: {value:.4f}, Time: {trial_time:.2f}s")
                print(f"  Best so far: {best_value:.4f}")

            except Exception as e:
                print(f"  Trial failed: {e}")

            trial_number += 1

        return {
            'best_params': best_params,
            'best_value': best_value,
            'trials_completed': self.trials_completed,
            'total_cost': self.total_cost,
            'total_time': time.time() - self.start_time
        }

# Example usage
def dummy_objective(params):
    """Dummy objective that takes time"""
    time.sleep(0.5)
    x = params['x']
    y = params['y']
    return (x - 3) ** 2 + (y - 2) ** 2

# Generate parameter suggestions
param_suggestions = [
    {'x': np.random.uniform(-10, 10), 'y': np.random.uniform(-10, 10)}
    for _ in range(50)
]

# Run with budget
tuner = BudgetAwareTuner(
    objective=dummy_objective,
    budget_seconds=10,  # 10 seconds
    max_trials=50,
    cost_per_trial=1.0
)

results = tuner.run(param_suggestions)
print("\n" + "="*50)
print("Final Results:")
print(f"Best parameters: {results['best_params']}")
print(f"Best value: {results['best_value']:.4f}")
print(f"Trials completed: {results['trials_completed']}")
print(f"Total time: {results['total_time']:.2f}s")
```

### Adaptive Sampling for Budget Constraints

```python
class AdaptiveBudgetTuner:
    """Adapts sampling strategy based on budget consumption"""

    def __init__(self, total_budget=3600):
        self.total_budget = total_budget
        self.spent = 0
        self.trial_times = []

    def estimate_remaining_trials(self) -> int:
        """Estimate how many trials can fit in remaining budget"""
        if not self.trial_times:
            return float('inf')

        avg_time = np.mean(self.trial_times[-10:])  # Last 10 trials
        remaining = self.total_budget - self.spent
        return max(1, int(remaining / avg_time))

    def should_stop(self) -> bool:
        """Determine if we should stop sampling"""
        remaining = self.total_budget - self.spent
        return remaining < np.mean(self.trial_times[-5:]) if self.trial_times else False

# Integration with Optuna
def objective_with_budget(trial: Trial):
    """Objective that checks budget status"""

    # If budget almost exhausted, reduce complexity
    remaining_trials = tuner.estimate_remaining_trials()

    if remaining_trials < 5:
        # Use simpler, faster models
        complexity = trial.suggest_categorical('complexity', ['low'])
    else:
        complexity = trial.suggest_categorical('complexity', ['low', 'medium', 'high'])

    # Rest of objective function...
    param = trial.suggest_float('param', 0, 1)
    return param ** 2
```

---

## Production Workflows

### Complete Training Pipeline with Hyperparameter Tuning

```python
import logging
from pathlib import Path
from datetime import datetime
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

class ProductionTuningPipeline:
    """Complete production-ready hyperparameter tuning pipeline"""

    def __init__(self,
                 project_name: str,
                 output_dir: str = './tuning_results',
                 n_trials: int = 50):
        """Initialize pipeline"""
        self.project_name = project_name
        self.output_dir = Path(output_dir)
        self.n_trials = n_trials

        # Setup logging
        self.setup_logging()

        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir = self.output_dir / 'models'
        self.models_dir.mkdir(exist_ok=True)

    def setup_logging(self):
        """Configure logging"""
        log_path = self.output_dir / f'tuning_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.project_name)

    def objective(self, trial: optuna.trial.Trial) -> float:
        """Objective function with comprehensive logging"""

        # Suggest hyperparameters
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 300),
            'max_depth': trial.suggest_int('max_depth', 10, 50),
            'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
            'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2']),
            'bootstrap': trial.suggest_categorical('bootstrap', [True, False])
        }

        # Create and train model
        model = RandomForestClassifier(**params, random_state=42, n_jobs=-1)

        # Cross-validation
        from sklearn.model_selection import cross_validate
        cv_results = cross_validate(
            model, X_train, y_train,
            cv=5,
            scoring=['f1', 'accuracy', 'precision', 'recall'],
            return_train_score=True
        )

        # Compute metrics
        f1_score = cv_results['test_f1'].mean()

        # Log trial information
        self.logger.info(f"Trial {trial.number}: F1={f1_score:.4f}, "
                        f"Params={params}")

        return f1_score

    def tune(self):
        """Run hyperparameter tuning"""
        self.logger.info(f"Starting hyperparameter tuning for {self.project_name}")
        self.logger.info(f"Number of trials: {self.n_trials}")

        study = optuna.create_study(
            direction='maximize',
            sampler=optuna.samplers.TPESampler(seed=42)
        )

        study.optimize(
            self.objective,
            n_trials=self.n_trials,
            show_progress_bar=True
        )

        self.logger.info(f"Tuning completed. Best trial: {study.best_trial.number}")
        self.logger.info(f"Best F1 score: {study.best_value:.4f}")
        self.logger.info(f"Best parameters: {study.best_params}")

        return study

    def train_final_model(self, study: optuna.study.Study):
        """Train final model with best parameters"""
        self.logger.info("Training final model with best parameters")

        model = RandomForestClassifier(
            **study.best_params,
            random_state=42,
            n_jobs=-1
        )

        model.fit(X_train, y_train)

        # Evaluate on test set
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)

        from sklearn.metrics import f1_score, accuracy_score, roc_auc_score

        metrics = {
            'f1_score': f1_score(y_test, y_pred),
            'accuracy': accuracy_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_pred_proba[:, 1])
        }

        self.logger.info(f"Test metrics: {metrics}")

        # Save model
        model_path = self.models_dir / 'best_model.joblib'
        joblib.dump(model, model_path)
        self.logger.info(f"Model saved to {model_path}")

        return model, metrics

    def save_results(self, study: optuna.study.Study, metrics: dict):
        """Save tuning results"""
        results = {
            'project': self.project_name,
            'timestamp': datetime.now().isoformat(),
            'best_trial': study.best_trial.number,
            'best_value': study.best_value,
            'best_params': study.best_params,
            'test_metrics': metrics,
            'n_trials': len(study.trials)
        }

        results_path = self.output_dir / 'results.json'
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)

        self.logger.info(f"Results saved to {results_path}")

        return results

# Usage
pipeline = ProductionTuningPipeline(
    project_name='rf_classifier_tuning',
    n_trials=50
)

study = pipeline.tune()
model, metrics = pipeline.train_final_model(study)
results = pipeline.save_results(study, metrics)
```

### Distributed Tuning with Ray

```python
from ray import tune, air
from ray.tune import Stopper
import time

class BudgetStopper(Stopper):
    """Custom stopper for budget constraints"""

    def __init__(self, budget_seconds=3600):
        self.budget_seconds = budget_seconds
        self.start_time = time.time()

    def __call__(self, trial_id, result):
        return time.time() - self.start_time > self.budget_seconds

    def stop_all(self):
        return time.time() - self.start_time > self.budget_seconds

def distributed_train_function(config):
    """Training function for distributed tuning"""

    model = RandomForestClassifier(
        n_estimators=config['n_estimators'],
        max_depth=config['max_depth'],
        random_state=42,
        n_jobs=-1
    )

    from sklearn.model_selection import cross_val_score
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1')

    session.report({"f1_score": scores.mean()})

# Configure distributed tuning
tuner = tune.Tuner(
    distributed_train_function,
    param_space={
        'n_estimators': tune.randint(50, 300),
        'max_depth': tune.randint(10, 50)
    },
    tune_config=tune.TuneConfig(
        num_samples=50,
        max_concurrent_trials=4,
        metric='f1_score',
        mode='max'
    ),
    run_config=air.RunConfig(
        name='distributed_tuning',
        stop=BudgetStopper(budget_seconds=3600),
        verbose=1
    )
)

# Run distributed tuning
results = tuner.fit()
best_result = results.get_best_result(metric='f1_score', mode='max')
```

---

## Best Practices

### 1. Search Space Design

```python
# DO: Define realistic ranges based on domain knowledge
good_space = {
    'learning_rate': [0.0001, 0.001, 0.01, 0.1],  # Log scale
    'batch_size': [16, 32, 64, 128],
    'hidden_units': [64, 128, 256, 512]
}

# DON'T: Define unrealistic ranges
bad_space = {
    'learning_rate': [0.00001, 1.0],  # Too broad
    'hidden_units': [1, 10000]  # Impractical
}
```

### 2. Objective Function Best Practices

```python
def objective_best_practices(trial: optuna.trial.Trial) -> float:
    """Objective function following best practices"""

    try:
        # 1. Clear parameter naming
        config = {
            'learning_rate': trial.suggest_float('lr', 1e-4, 1e-2, log=True),
            'batch_size': trial.suggest_categorical('bs', [16, 32, 64]),
        }

        # 2. Use cross-validation
        from sklearn.model_selection import cross_val_score
        scores = cross_val_score(
            estimator=model,
            X=X_train,
            y=y_train,
            cv=5,
            scoring='f1'
        )

        # 3. Return primary metric
        return scores.mean()

    except Exception as e:
        # 4. Handle errors gracefully
        logging.error(f"Trial failed: {e}")
        return float('-inf')  # Penalty for failed trials
```

### 3. Reproducibility

```python
# Set random seeds for reproducibility
import numpy as np
import random
import torch
import optuna

SEED = 42

np.random.seed(SEED)
random.seed(SEED)
torch.manual_seed(SEED)

# Use deterministic sampler
sampler = optuna.samplers.TPESampler(seed=SEED)
study = optuna.create_study(sampler=sampler)
```

### 4. Monitoring and Logging

```python
# Log comprehensive trial information
def objective_with_logging(trial):
    # Log start
    logger.info(f"Starting trial {trial.number}")

    start_time = time.time()

    try:
        # Run trial
        value = compute_objective(trial)

        elapsed = time.time() - start_time

        # Log results
        logger.info(f"Trial {trial.number} completed in {elapsed:.2f}s")
        logger.info(f"  Value: {value:.4f}")
        logger.info(f"  Params: {trial.params}")

        return value

    except Exception as e:
        logger.error(f"Trial {trial.number} failed: {e}", exc_info=True)
        return float('-inf')
```

### 5. Checkpoint and Resume

```python
# Save study progress regularly
def save_study(study, path):
    """Persist study to database"""
    import sqlite3

    connection_string = f'sqlite:///{path}/tuning_study.db'
    # Recreate study with persistent storage
    return optuna.create_study(
        storage=connection_string,
        study_name='my_study',
        load_if_exists=True
    )

# Resume tuning
study = save_study(study, './results')
study.optimize(objective, n_trials=50)  # Resume from saved state
```

### 6. Hyperparameter Importance Analysis

```python
def analyze_importance(study):
    """Analyze hyperparameter importance"""

    # Get importance using permutation method
    importances = optuna.importance.get_param_importances(study)

    # Visualize
    fig = optuna.visualization.plot_param_importances(study).show()

    # Print summary
    print("\nHyperparameter Importance:")
    for param, importance in sorted(importances.items(),
                                   key=lambda x: x[1],
                                   reverse=True):
        print(f"  {param}: {importance:.4f}")

    return importances
```

### 7. Validation Strategy

```python
# Always use validation set separate from test set
from sklearn.model_selection import train_test_split

# Split: 60% train, 20% validation, 20% test
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.4, random_state=42
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42
)

# Tune on train+val, evaluate on test
# (Cross-validation within train set during tuning)
```

---

## Summary

Key takeaways for effective hyperparameter tuning:

1. **Start simple**: Grid search or random search for initial exploration
2. **Use intelligent samplers**: Bayesian optimization, TPE for efficiency
3. **Leverage frameworks**: Optuna for flexibility, Ray Tune for scale
4. **Prune aggressively**: Stop unpromising trials early
5. **Respect constraints**: Budget time, computational resources
6. **Validate thoroughly**: Separate train/validation/test sets
7. **Monitor everything**: Log trials, track metrics, analyze importance
8. **Parallelize**: Use distributed tuning for large search spaces
9. **Reproduce results**: Use seeds, persistent storage, version control
10. **Iterate strategically**: Start broad, refine based on results

---

## References

- Optuna Documentation: https://optuna.readthedocs.io/
- Ray Tune: https://docs.ray.io/en/latest/tune/
- scikit-optimize: https://scikit-optimize.github.io/
- "Practical Bayesian Optimization of Machine Learning Algorithms" (Snoek et al., 2012)
