# Machine Learning Fundamentals Reference Guide

A comprehensive reference for machine learning algorithms, techniques, and best practices for production environments.

## Table of Contents

1. [Supervised Learning Algorithms](#supervised-learning-algorithms)
2. [Unsupervised Learning Algorithms](#unsupervised-learning-algorithms)
3. [Model Selection and Evaluation](#model-selection-and-evaluation)
4. [Bias-Variance Tradeoff](#bias-variance-tradeoff)
5. [Regularization Techniques](#regularization-techniques)
6. [Ensemble Methods](#ensemble-methods)
7. [Algorithm Selection Guide](#algorithm-selection-guide)
8. [Best Practices](#best-practices)

---

## Supervised Learning Algorithms

Supervised learning algorithms learn from labeled data to make predictions on unseen data.

### 1. Linear Regression

**Overview**: Predicts continuous values by fitting a linear relationship between features and target.

**Key Concepts**:
- Minimizes Mean Squared Error (MSE)
- Assumes linear relationship between features and target
- Sensitive to outliers
- Interpretable coefficients

**When to Use**:
- Continuous target variable
- Linear relationships in data
- Interpretability is important
- Quick baseline model needed

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Example with house price prediction
X = np.random.randn(1000, 5)
y = 2*X[:, 0] + 3*X[:, 1] - X[:, 2] + np.random.randn(1000) * 0.1

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Standardize features (important for interpretation)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model
model = LinearRegression()
model.fit(X_train_scaled, y_train)

# Make predictions
y_pred = model.predict(X_test_scaled)

# Evaluate
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mse)

print(f"RMSE: {rmse:.4f}")
print(f"R² Score: {r2:.4f}")
print(f"Coefficients: {model.coef_}")
print(f"Intercept: {model.intercept_}")
```

**Production Considerations**:
- Always scale features before fitting
- Check assumptions: linearity, homoscedasticity, normality of residuals
- Use regularization for high-dimensional data
- Monitor for multicollinearity

---

### 2. Logistic Regression

**Overview**: Binary or multiclass classification using a sigmoid function to model probability.

**Key Concepts**:
- Outputs probability scores between 0 and 1
- Uses maximum likelihood estimation
- Interpretable decision boundaries
- Scalable to large datasets

**When to Use**:
- Binary or multiclass classification
- Need probability estimates
- Interpretability critical
- Linear decision boundaries sufficient

```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, roc_curve
)
import matplotlib.pyplot as plt

# Generate binary classification data
from sklearn.datasets import make_classification

X, y = make_classification(
    n_samples=1000, n_features=20, n_informative=10,
    n_redundant=5, random_state=42
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Standardize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model with L2 regularization
model = LogisticRegression(
    C=1.0,  # Inverse regularization strength
    max_iter=1000,
    solver='lbfgs',
    random_state=42
)
model.fit(X_train_scaled, y_train)

# Predictions and probabilities
y_pred = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

# Evaluation
print(classification_report(y_test, y_pred))
print(f"AUC-ROC: {roc_auc_score(y_test, y_pred_proba):.4f}")
print(f"Confusion Matrix:\n{confusion_matrix(y_test, y_pred)}")

# Feature importance (coefficients)
feature_importance = pd.DataFrame({
    'feature': range(X.shape[1]),
    'coefficient': model.coef_[0]
}).sort_values('coefficient', key=abs, ascending=False)
print(feature_importance.head(10))
```

**Production Considerations**:
- Set appropriate decision threshold for business requirements
- Use probability predictions for ranking
- Monitor for class imbalance (use class_weight parameter)
- Calibrate probabilities if needed

---

### 3. Decision Trees

**Overview**: Non-parametric model that recursively splits features to minimize impurity.

**Key Concepts**:
- Builds tree structure with binary splits
- Measures split quality using Gini impurity or entropy
- Can capture non-linear relationships
- Prone to overfitting without pruning

**When to Use**:
- Non-linear relationships
- Feature interactions important
- Need interpretable white-box model
- Mixed data types (with preprocessing)

```python
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Train decision tree with depth control
model = DecisionTreeClassifier(
    max_depth=5,  # Control complexity
    min_samples_split=20,  # Prevent small splits
    min_samples_leaf=10,  # Ensure minimum samples per leaf
    criterion='gini',  # or 'entropy'
    random_state=42
)
model.fit(X_train_scaled, y_train)

# Predictions
y_pred = model.predict(X_test_scaled)

# Evaluation
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall: {recall_score(y_test, y_pred):.4f}")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': range(X.shape[1]),
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print(feature_importance.head(10))

# Visualize tree (for small trees only)
# tree.plot_tree(model, max_depth=2, feature_names=[f'Feature {i}' for i in range(X.shape[1])])
```

**Production Considerations**:
- Control tree depth to prevent overfitting
- Use pruning techniques
- Requires data scaling is NOT needed (tree-based)
- Monitor feature importance for model explainability
- Sensitive to data imbalance

---

### 4. Random Forests

**Overview**: Ensemble of decision trees that aggregates predictions for improved generalization.

**Key Concepts**:
- Bootstrap aggregating (bagging)
- Random feature selection at each split
- Reduces variance through ensemble averaging
- Feature importances from aggregate splits

**When to Use**:
- Strong non-linear patterns
- Large datasets
- Want to reduce overfitting from single trees
- Need feature importance rankings

```python
from sklearn.ensemble import RandomForestClassifier

# Production-ready random forest
model = RandomForestClassifier(
    n_estimators=100,  # Number of trees
    max_depth=10,  # Control complexity
    min_samples_split=20,
    min_samples_leaf=10,
    max_features='sqrt',  # Random feature selection
    n_jobs=-1,  # Use all cores
    random_state=42,
    class_weight='balanced',  # Handle imbalance
    oob_score=True  # Out-of-bag score
)
model.fit(X_train, y_train)

# Predictions with probabilities
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

# Evaluation
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"AUC-ROC: {roc_auc_score(y_test, y_pred_proba):.4f}")
print(f"OOB Score: {model.oob_score_:.4f}")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': range(X.shape[1]),
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print(feature_importance.head(10))

# Get predictions from individual trees
tree_predictions = np.array([
    tree.predict_proba(X_test)[:, 1] for tree in model.estimators_
]).T
tree_stds = np.std(tree_predictions, axis=1)  # Uncertainty estimates
```

**Production Considerations**:
- Hyperparameter tuning critical (depth, samples_split, samples_leaf)
- Monitor OOB score for early overfitting detection
- Can provide uncertainty estimates from tree variance
- Feature importance helps with debugging and monitoring
- Scales well to large datasets

---

### 5. Gradient Boosting

**Overview**: Sequentially builds trees where each corrects residuals of previous trees.

**Key Concepts**:
- Sequential tree construction
- Learns from residuals (errors) of previous models
- Controls learning rate for regularization
- Often achieves state-of-the-art performance

**When to Use**:
- Need maximum predictive accuracy
- Complex non-linear relationships
- Have time for hyperparameter tuning
- Production systems can handle longer inference time

```python
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV

# Production gradient boosting model
model = GradientBoostingClassifier(
    n_estimators=200,  # Number of boosting rounds
    learning_rate=0.1,  # Shrinkage parameter
    max_depth=5,  # Depth of each tree
    min_samples_split=20,
    min_samples_leaf=10,
    subsample=0.8,  # Stochastic gradient boosting
    random_state=42,
    validation_fraction=0.1,  # Use for early stopping
    n_iter_no_change=10  # Early stopping
)
model.fit(X_train_scaled, y_train, verbose=0)

# Predictions
y_pred = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

# Evaluation
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"AUC-ROC: {roc_auc_score(y_test, y_pred_proba):.4f}")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': range(X.shape[1]),
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print(feature_importance.head(10))

# Training history (loss vs iteration)
train_scores = model.train_score_
print(f"Number of iterations: {len(train_scores)}")
print(f"Final training score: {train_scores[-1]:.4f}")

# Hyperparameter tuning example
param_grid = {
    'learning_rate': [0.01, 0.1, 0.5],
    'max_depth': [3, 5, 7],
    'n_estimators': [100, 200]
}

# Grid search (can be time-consuming)
# grid_search = GridSearchCV(
#     GradientBoostingClassifier(random_state=42),
#     param_grid,
#     cv=5,
#     n_jobs=-1
# )
# grid_search.fit(X_train_scaled, y_train)
# print(f"Best params: {grid_search.best_params_}")
```

**Production Considerations**:
- Prone to overfitting; use early stopping
- Hyperparameter tuning is critical
- Learning rate and max_depth are most important
- Use subsample for stochastic boosting (variance reduction)
- Monitor validation loss for early stopping
- Computationally more expensive than random forests

---

### 6. Support Vector Machines (SVM)

**Overview**: Finds optimal hyperplane to maximize margin between classes.

**Key Concepts**:
- Margin maximization
- Kernel tricks for non-linear decision boundaries
- Support vectors determine decision boundary
- Sensitive to feature scaling

**When to Use**:
- High-dimensional data
- Binary or multiclass classification
- Need clear margin interpretation
- Kernel tricks for non-linearity

```python
from sklearn.svm import SVC, SVR
from sklearn.metrics import f1_score

# SVM for classification
model = SVC(
    kernel='rbf',  # 'linear', 'poly', 'rbf', 'sigmoid'
    C=1.0,  # Regularization parameter
    gamma='scale',  # Kernel coefficient
    probability=True,  # Enable probability estimates
    random_state=42
)
model.fit(X_train_scaled, y_train)

# Predictions
y_pred = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

# Evaluation
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"F1-Score: {f1_score(y_test, y_pred):.4f}")
print(f"Number of support vectors: {len(model.support_vectors_)}")

# SVM Regression example
from sklearn.datasets import make_regression

X_reg, y_reg = make_regression(n_samples=500, n_features=10, random_state=42)
X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
    X_reg, y_reg, test_size=0.2, random_state=42
)

scaler_reg = StandardScaler()
X_train_reg_scaled = scaler_reg.fit_transform(X_train_reg)
X_test_reg_scaled = scaler_reg.transform(X_test_reg)

svm_reg = SVR(kernel='rbf', C=1.0, gamma='scale')
svm_reg.fit(X_train_reg_scaled, y_train_reg)

y_pred_reg = svm_reg.predict(X_test_reg_scaled)
rmse = np.sqrt(mean_squared_error(y_test_reg, y_pred_reg))
print(f"SVM Regression RMSE: {rmse:.4f}")
```

**Production Considerations**:
- MUST scale features before fitting
- Kernel selection affects performance significantly
- C and gamma are critical hyperparameters
- Slow on very large datasets
- Memory-intensive with many support vectors
- Good for smaller to medium-sized datasets

---

## Unsupervised Learning Algorithms

Unsupervised learning discovers patterns in unlabeled data without target variable.

### 1. K-Means Clustering

**Overview**: Partitions data into k clusters by minimizing within-cluster variance.

**Key Concepts**:
- Iterative centroid-based clustering
- Random initialization affects results
- Requires specifying k in advance
- Fast and scalable

**When to Use**:
- Customer segmentation
- Data exploration
- Quick clustering baseline
- Spherical cluster shapes

```python
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
import matplotlib.pyplot as plt

# Generate clustering data
from sklearn.datasets import make_blobs

X_cluster, _ = make_blobs(n_samples=500, n_features=5, centers=4, random_state=42)

# Standardize features
scaler = StandardScaler()
X_cluster_scaled = scaler.fit_transform(X_cluster)

# Find optimal k using elbow method
inertias = []
silhouette_scores = []
k_range = range(2, 11)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_cluster_scaled)
    inertias.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X_cluster_scaled, kmeans.labels_))

# Plot elbow curve
# plt.figure(figsize=(12, 4))
# plt.subplot(1, 2, 1)
# plt.plot(k_range, inertias, 'bo-')
# plt.xlabel('Number of Clusters')
# plt.ylabel('Inertia')
# plt.title('Elbow Method')
#
# plt.subplot(1, 2, 2)
# plt.plot(k_range, silhouette_scores, 'ro-')
# plt.xlabel('Number of Clusters')
# plt.ylabel('Silhouette Score')
# plt.title('Silhouette Analysis')
# plt.tight_layout()

# Fit final model
optimal_k = 4
model = KMeans(
    n_clusters=optimal_k,
    init='k-means++',  # Smart initialization
    max_iter=300,
    random_state=42,
    n_init=10
)
labels = model.fit_predict(X_cluster_scaled)

# Evaluation metrics
silhouette = silhouette_score(X_cluster_scaled, labels)
davies_bouldin = davies_bouldin_score(X_cluster_scaled, labels)
inertia = model.inertia_

print(f"Silhouette Score: {silhouette:.4f}")  # Higher is better, range [-1, 1]
print(f"Davies-Bouldin Index: {davies_bouldin:.4f}")  # Lower is better
print(f"Inertia: {inertia:.4f}")
print(f"Cluster sizes: {pd.Series(labels).value_counts().sort_index().to_dict()}")

# Add cluster labels to data
cluster_df = pd.DataFrame(X_cluster, columns=[f'Feature_{i}' for i in range(5)])
cluster_df['Cluster'] = labels
```

**Production Considerations**:
- Use k-means++ initialization
- Scale features before clustering
- Run multiple times with different initializations
- Use silhouette score or Davies-Bouldin index to validate
- Sensitive to outliers
- Assumes spherical clusters

---

### 2. Hierarchical Clustering

**Overview**: Creates dendrograms by iteratively merging or splitting clusters.

**Key Concepts**:
- Agglomerative (bottom-up) or divisive (top-down)
- Linkage methods: single, complete, average, Ward
- Produces dendrogram for visualization
- No need to specify cluster count upfront

**When to Use**:
- Hierarchical data structure important
- Need dendrogram visualization
- Flexibility in choosing cut-off distance
- Smaller datasets (computational cost)

```python
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage

# Hierarchical clustering with different linkage methods
linkage_methods = ['ward', 'complete', 'average', 'single']
linkage_matrices = {}

for method in linkage_methods:
    linkage_matrix = linkage(X_cluster_scaled, method=method)
    linkage_matrices[method] = linkage_matrix

# Use Ward linkage (usually best)
model = AgglomerativeClustering(
    n_clusters=4,
    linkage='ward'
)
labels = model.fit_predict(X_cluster_scaled)

# Evaluation
silhouette = silhouette_score(X_cluster_scaled, labels)
davies_bouldin = davies_bouldin_score(X_cluster_scaled, labels)

print(f"Silhouette Score: {silhouette:.4f}")
print(f"Davies-Bouldin Index: {davies_bouldin:.4f}")

# Dendrogram visualization (for small datasets)
# plt.figure(figsize=(15, 5))
# for idx, (method, linkage_matrix) in enumerate(linkage_matrices.items(), 1):
#     plt.subplot(1, len(linkage_methods), idx)
#     dendrogram(linkage_matrix)
#     plt.title(f'{method.capitalize()} Linkage')
#     plt.xlabel('Sample Index')
#     plt.ylabel('Distance')
# plt.tight_layout()
```

**Production Considerations**:
- Ward linkage generally performs best
- Dendrogram useful for exploratory analysis
- Computationally expensive for large datasets O(n²)
- Good for understanding hierarchical relationships
- Sensitive to scaling

---

### 3. DBSCAN (Density-Based Spatial Clustering)

**Overview**: Clusters data based on density, can identify outliers.

**Key Concepts**:
- Epsilon and min_samples define neighborhood
- Identifies core points, border points, noise
- Non-parametric (no need to specify cluster count)
- Finds arbitrary-shaped clusters

**When to Use**:
- Outlier detection
- Non-spherical cluster shapes
- Unknown number of clusters
- Need noise point identification

```python
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

# Find optimal epsilon using k-distance graph
neighbors = NearestNeighbors(n_neighbors=5)
neighbors_fit = neighbors.fit(X_cluster_scaled)
distances, indices = neighbors_fit.kneighbors(X_cluster_scaled)
distances = np.sort(distances[:, -1], axis=0)

# Plot k-distance graph to find elbow
# plt.figure(figsize=(10, 6))
# plt.plot(distances)
# plt.ylabel('5-th Nearest Neighbor Distance')
# plt.xlabel('Data Points sorted by distance')
# plt.axhline(y=0.5, color='r', linestyle='--')
# plt.title('K-distance Graph for Epsilon Selection')
# plt.show()

# DBSCAN clustering
model = DBSCAN(
    eps=0.5,  # Maximum distance between neighbors
    min_samples=5  # Minimum samples in neighborhood
)
labels = model.fit_predict(X_cluster_scaled)

# Count clusters and noise points
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
n_noise = list(labels).count(-1)

print(f"Number of clusters: {n_clusters}")
print(f"Number of noise points: {n_noise}")
print(f"Silhouette Score: {silhouette_score(X_cluster_scaled, labels[labels != -1]):.4f}")

# Cluster composition
cluster_df = pd.DataFrame(X_cluster_scaled)
cluster_df['Cluster'] = labels
cluster_df['IsNoise'] = labels == -1
print(f"\nCluster distribution:\n{cluster_df['Cluster'].value_counts()}")
```

**Production Considerations**:
- Epsilon and min_samples are critical parameters
- Use k-distance graph to find epsilon
- Noise points can be valuable for anomaly detection
- Computationally efficient O(n log n) with spatial indexing
- Not affected by feature scaling as much as distance-based methods
- Good for non-spherical clusters and outlier detection

---

### 4. PCA (Principal Component Analysis)

**Overview**: Dimensionality reduction by finding principal components of maximum variance.

**Key Concepts**:
- Orthogonal linear transformation
- Preserves variance information
- Reduces to uncorrelated features
- Foundation for many techniques

**When to Use**:
- High-dimensional data
- Feature visualization
- Noise reduction
- Curse of dimensionality

```python
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Generate high-dimensional data
from sklearn.datasets import load_iris

iris = load_iris()
X_iris = iris.data
y_iris = iris.target

# Scale features
scaler = StandardScaler()
X_iris_scaled = scaler.fit_transform(X_iris)

# Analyze variance explained
pca_full = PCA()
pca_full.fit(X_iris_scaled)

cumulative_variance = np.cumsum(pca_full.explained_variance_ratio_)
print("Explained variance by component:")
for i, var in enumerate(pca_full.explained_variance_ratio_):
    print(f"  PC{i+1}: {var:.4f} ({cumulative_variance[i]:.4f} cumulative)")

# Reduce to 2 components for visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_iris_scaled)

print(f"\nTotal variance explained: {pca.explained_variance_ratio_.sum():.4f}")
print(f"Components shape: {pca.components_.shape}")

# Visualization
# plt.figure(figsize=(10, 6))
# scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y_iris, cmap='viridis')
# plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%})')
# plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%})')
# plt.title('PCA: Iris Dataset')
# plt.colorbar(scatter)
# plt.show()

# Scree plot
# plt.figure(figsize=(10, 6))
# plt.plot(range(1, len(cumulative_variance) + 1), cumulative_variance, 'bo-')
# plt.axhline(y=0.95, color='r', linestyle='--', label='95% Threshold')
# plt.xlabel('Number of Components')
# plt.ylabel('Cumulative Explained Variance')
# plt.legend()
# plt.title('Scree Plot')
# plt.show()

# Feature contributions to principal components
component_df = pd.DataFrame(
    pca.components_.T,
    columns=[f'PC{i+1}' for i in range(pca.n_components_)],
    index=iris.feature_names
)
print("\nFeature contributions to principal components:")
print(component_df)
```

**Production Considerations**:
- Always scale features before PCA
- Choose components to capture 95%+ variance
- Components are not interpretable
- Good for visualization and preprocessing
- Sensitive to outliers
- Useful as preprocessing step for other algorithms

---

### 5. t-SNE (t-Distributed Stochastic Neighbor Embedding)

**Overview**: Non-linear dimensionality reduction preserving local neighborhood structure.

**Key Concepts**:
- Converts distances to probabilities
- Focuses on local structure
- Good for visualization only
- Stochastic (different runs may differ)

**When to Use**:
- Data visualization (2D/3D)
- Exploratory analysis
- NOT for downstream modeling
- Understanding cluster structure

```python
from sklearn.manifold import TSNE

# t-SNE is computationally expensive
# Use on sample of data for exploration
sample_size = min(1000, X_cluster_scaled.shape[0])
sample_idx = np.random.choice(X_cluster_scaled.shape[0], sample_size, replace=False)
X_sample = X_cluster_scaled[sample_idx]

# t-SNE reduction
tsne = TSNE(
    n_components=2,
    perplexity=30,  # Balance local vs global structure
    learning_rate=200,
    n_iter=1000,
    random_state=42,
    n_jobs=-1
)
X_tsne = tsne.fit_transform(X_sample)

print(f"t-SNE output shape: {X_tsne.shape}")

# Visualization
# plt.figure(figsize=(10, 8))
# scatter = plt.scatter(X_tsne[:, 0], X_tsne[:, 1], c=labels[sample_idx], cmap='viridis', alpha=0.6)
# plt.xlabel('t-SNE 1')
# plt.ylabel('t-SNE 2')
# plt.title('t-SNE Visualization')
# plt.colorbar(scatter)
# plt.show()
```

**Production Considerations**:
- NOT for feature engineering or preprocessing
- For visualization only
- Sensitive to perplexity parameter
- Non-deterministic (use random_state for reproducibility)
- Computationally expensive
- Best with 1000-5000 samples
- Results can be misleading if misinterpreted

---

### 6. UMAP (Uniform Manifold Approximation and Projection)

**Overview**: Modern dimensionality reduction preserving both local and global structure.

**Key Concepts**:
- Topological data analysis
- Better preservation of global structure than t-SNE
- Can be used for preprocessing
- Faster than t-SNE

**When to Use**:
- Better visualization than t-SNE
- Both local and global structure important
- Large datasets
- Can use output for downstream modeling

```python
# UMAP requires separate installation: pip install umap-learn
try:
    import umap

    # UMAP reduction
    umap_model = umap.UMAP(
        n_components=2,
        n_neighbors=15,  # Local neighborhood size
        min_dist=0.1,  # Minimum distance between points
        metric='euclidean',
        random_state=42
    )
    X_umap = umap_model.fit_transform(X_cluster_scaled)

    print(f"UMAP output shape: {X_umap.shape}")

    # Visualization
    # plt.figure(figsize=(10, 8))
    # scatter = plt.scatter(X_umap[:, 0], X_umap[:, 1], c=labels, cmap='viridis', alpha=0.6)
    # plt.xlabel('UMAP 1')
    # plt.ylabel('UMAP 2')
    # plt.title('UMAP Visualization')
    # plt.colorbar(scatter)
    # plt.show()

except ImportError:
    print("UMAP not installed. Install with: pip install umap-learn")
```

**Production Considerations**:
- Faster than t-SNE, suitable for larger datasets
- Better global structure preservation
- Can use output for preprocessing
- n_neighbors affects local vs global balance
- Faster inference on new data
- Generally superior to t-SNE for many tasks

---

## Model Selection and Evaluation

### Cross-Validation

**Overview**: Robust evaluation technique that uses multiple train-test splits.

```python
from sklearn.model_selection import (
    cross_val_score, cross_validate, KFold, StratifiedKFold,
    TimeSeriesSplit
)

# Stratified K-Fold for imbalanced classification
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# K-Fold for regression
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# Time Series Split for temporal data
ts_split = TimeSeriesSplit(n_splits=5)

# Simple cross-validation score
model = LogisticRegression(random_state=42)
scores = cross_val_score(
    model, X_train_scaled, y_train,
    cv=StratifiedKFold(n_splits=5, random_state=42),
    scoring='roc_auc',
    n_jobs=-1
)
print(f"CV Scores: {scores}")
print(f"Mean CV Score: {scores.mean():.4f} (+/- {scores.std():.4f})")

# Detailed cross-validation with multiple metrics
metrics = {
    'accuracy': 'accuracy',
    'precision': 'precision',
    'recall': 'recall',
    'f1': 'f1',
    'roc_auc': 'roc_auc'
}

cv_results = cross_validate(
    model, X_train_scaled, y_train,
    cv=StratifiedKFold(n_splits=5, random_state=42),
    scoring=metrics,
    n_jobs=-1
)

results_df = pd.DataFrame({
    metric: cv_results[f'test_{metric}']
    for metric in metrics.keys()
})
print("\nCross-validation results:")
print(results_df.describe())
```

**Best Practices**:
- Use StratifiedKFold for classification (maintains class distribution)
- Use TimeSeriesSplit for temporal data
- Typically 5-10 folds
- Report mean and standard deviation

---

### Classification Metrics

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, pr_auc_score, confusion_matrix, classification_report,
    precision_recall_curve, roc_curve
)

# Binary classification metrics
y_pred = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred_proba)

print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-Score:  {f1:.4f}")
print(f"ROC-AUC:   {roc_auc:.4f}")

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:\n{cm}")
print(f"TN: {cm[0,0]}, FP: {cm[0,1]}")
print(f"FN: {cm[1,0]}, TP: {cm[1,1]}")

# Classification report (macro, micro, weighted averages for multiclass)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Negative', 'Positive']))

# Threshold optimization
precision_vals, recall_vals, thresholds = precision_recall_curve(y_test, y_pred_proba)
f1_scores_threshold = 2 * (precision_vals * recall_vals) / (precision_vals + recall_vals + 1e-10)
optimal_threshold = thresholds[np.argmax(f1_scores_threshold)]
print(f"\nOptimal threshold (F1): {optimal_threshold:.4f}")
```

**Metric Interpretation**:
- **Accuracy**: Overall correctness (avoid for imbalanced data)
- **Precision**: TP / (TP + FP) - False positive cost high
- **Recall**: TP / (TP + FN) - False negative cost high
- **F1-Score**: Harmonic mean of precision and recall
- **ROC-AUC**: Threshold-invariant metric, good for imbalanced data
- **PR-AUC**: Better than ROC-AUC for highly imbalanced data

---

### Regression Metrics

```python
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, mean_absolute_percentage_error,
    r2_score, median_absolute_error
)

# Regression metrics
y_pred_reg = model.predict(X_test)

mse = mean_squared_error(y_test_reg, y_pred_reg)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test_reg, y_pred_reg)
mape = mean_absolute_percentage_error(y_test_reg, y_pred_reg)
r2 = r2_score(y_test_reg, y_pred_reg)
median_ae = median_absolute_error(y_test_reg, y_pred_reg)

print(f"MSE:  {mse:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"MAE:  {mae:.4f}")
print(f"MAPE: {mape:.4f}")
print(f"R²:   {r2:.4f}")
print(f"Median AE: {median_ae:.4f}")

# Residual analysis
residuals = y_test_reg - y_pred_reg
print(f"\nResiduals Mean: {residuals.mean():.4f}")
print(f"Residuals Std: {residuals.std():.4f}")
```

**Metric Interpretation**:
- **MSE/RMSE**: Penalizes large errors (sensitive to outliers)
- **MAE**: Robust to outliers
- **MAPE**: Scale-independent percentage error
- **R²**: Proportion of variance explained (0-1 for good fit)
- **Median AE**: Robust alternative to MSE

---

## Bias-Variance Tradeoff

### Understanding the Tradeoff

**Bias**: Error from overly simplistic model assumptions (underfitting)
**Variance**: Error from excessive sensitivity to training data fluctuations (overfitting)

```python
from sklearn.model_selection import learning_curve
import matplotlib.pyplot as plt

# Learning curves to visualize bias-variance tradeoff
def plot_learning_curve(model, X, y, cv=5, title="Learning Curve"):
    train_sizes, train_scores, val_scores = learning_curve(
        model, X, y,
        cv=cv,
        train_sizes=np.linspace(0.1, 1.0, 10),
        n_jobs=-1,
        scoring='accuracy'
    )

    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    val_std = np.std(val_scores, axis=1)

    # plt.figure(figsize=(10, 6))
    # plt.plot(train_sizes, train_mean, label='Training score', color='blue', marker='o')
    # plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.2, color='blue')
    # plt.plot(train_sizes, val_mean, label='Validation score', color='red', marker='o')
    # plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.2, color='red')
    # plt.xlabel('Training Set Size')
    # plt.ylabel('Score')
    # plt.title(title)
    # plt.legend()
    # plt.grid()
    # plt.show()

    return train_mean, val_mean

# Test different model complexities
models = {
    'High Bias': DecisionTreeClassifier(max_depth=2, random_state=42),
    'Balanced': DecisionTreeClassifier(max_depth=5, random_state=42),
    'High Variance': DecisionTreeClassifier(max_depth=15, random_state=42),
}

# for name, model in models.items():
#     plot_learning_curve(model, X_train_scaled, y_train, title=f'{name}')
```

**Addressing High Bias (Underfitting)**:
- Increase model complexity
- Add more features
- Reduce regularization
- Train longer

**Addressing High Variance (Overfitting)**:
- Reduce model complexity
- Get more training data
- Increase regularization
- Use ensemble methods
- Feature selection

---

## Regularization Techniques

### L1 Regularization (Lasso)

```python
from sklearn.linear_model import Lasso, LassoCV

# L1 penalty: sum of absolute values of coefficients
# Tends to produce sparse solutions (feature selection)

# Cross-validated Lasso
lasso_cv = LassoCV(
    cv=5,
    random_state=42,
    n_jobs=-1
)
lasso_cv.fit(X_train_scaled, y_train)

print(f"Optimal alpha: {lasso_cv.alpha_:.4f}")
print(f"Non-zero coefficients: {(lasso_cv.coef_ != 0).sum()}")
print(f"Number of features: {len(lasso_cv.coef_)}")

# Manual Lasso with specific alpha
lasso = Lasso(alpha=0.01, random_state=42)
lasso.fit(X_train_scaled, y_train)

# Feature selection from Lasso
selected_features = np.where(lasso.coef_ != 0)[0]
print(f"Selected features: {selected_features}")
```

### L2 Regularization (Ridge)

```python
from sklearn.linear_model import Ridge, RidgeCV

# L2 penalty: sum of squared coefficients
# Distributes weight evenly across correlated features

ridge_cv = RidgeCV(
    alphas=np.logspace(-2, 2, 100),
    cv=5
)
ridge_cv.fit(X_train_scaled, y_train)

print(f"Optimal alpha: {ridge_cv.alpha_:.4f}")

ridge = Ridge(alpha=ridge_cv.alpha_)
ridge.fit(X_train_scaled, y_train)

# All features are used (but with reduced coefficients)
print(f"Coefficient magnitudes: {np.abs(ridge.coef_).mean():.4f}")
```

### Elastic Net (L1 + L2)

```python
from sklearn.linear_model import ElasticNetCV

# Combines L1 and L2 penalties
# l1_ratio: 0=Ridge, 1=Lasso

elastic_net_cv = ElasticNetCV(
    cv=5,
    l1_ratio=[0.1, 0.5, 0.9, 0.99],
    random_state=42,
    n_jobs=-1
)
elastic_net_cv.fit(X_train_scaled, y_train)

print(f"Optimal alpha: {elastic_net_cv.alpha_:.4f}")
print(f"Optimal l1_ratio: {elastic_net_cv.l1_ratio_:.4f}")
print(f"Non-zero coefficients: {(elastic_net_cv.coef_ != 0).sum()}")
```

**Regularization Summary**:
- **L1 (Lasso)**: Feature selection, sparse solutions
- **L2 (Ridge)**: Coefficient shrinkage, correlated features
- **Elastic Net**: Balance between L1 and L2, most flexible

---

## Ensemble Methods

### Voting Classifier

```python
from sklearn.ensemble import VotingClassifier

# Combine multiple algorithms
ensemble = VotingClassifier(
    estimators=[
        ('lr', LogisticRegression(random_state=42)),
        ('rf', RandomForestClassifier(n_estimators=100, random_state=42)),
        ('svm', SVC(probability=True, random_state=42))
    ],
    voting='soft'  # 'soft' uses probability, 'hard' uses majority vote
)

ensemble.fit(X_train_scaled, y_train)
y_pred_ensemble = ensemble.predict(X_test_scaled)

print(f"Voting Ensemble Accuracy: {accuracy_score(y_test, y_pred_ensemble):.4f}")
```

### Stacking

```python
from sklearn.ensemble import StackingClassifier

# Meta-learner trained on base learner predictions
base_learners = [
    ('lr', LogisticRegression(random_state=42)),
    ('rf', RandomForestClassifier(n_estimators=100, random_state=42))
]

stacker = StackingClassifier(
    estimators=base_learners,
    final_estimator=LogisticRegression(random_state=42),
    cv=5
)

stacker.fit(X_train_scaled, y_train)
y_pred_stacked = stacker.predict(X_test_scaled)

print(f"Stacking Ensemble Accuracy: {accuracy_score(y_test, y_pred_stacked):.4f}")
```

---

## Algorithm Selection Guide

### Classification Tasks

| Problem | Recommended Algorithms | Why |
|---------|----------------------|-----|
| **Quick Baseline** | Logistic Regression | Fast, interpretable, good starting point |
| **Binary Classification** | Logistic Regression, SVM, Random Forest | Proven, interpretable, scalable |
| **Multiclass** | Random Forest, Gradient Boosting, Neural Networks | Handle multiclass well |
| **Imbalanced Data** | Random Forest (class_weight), Gradient Boosting | Can handle imbalance naturally |
| **Feature Importance** | Random Forest, Gradient Boosting | Built-in feature importance |
| **High Dimensionality** | Logistic Regression, SVM | Scale better than tree-based |
| **Need Probabilities** | Logistic Regression, Gradient Boosting | Output calibrated probabilities |
| **Non-linear Boundaries** | Random Forest, SVM (RBF), Gradient Boosting | Capture non-linearity |
| **Interpretability Critical** | Logistic Regression, Decision Trees | White-box models |
| **Production Speed Critical** | Logistic Regression, Tree models | Fast inference |

### Regression Tasks

| Problem | Recommended Algorithms | Why |
|---------|----------------------|-----|
| **Quick Baseline** | Linear Regression | Fast, interpretable |
| **Linear Relationships** | Linear Regression, Ridge, Lasso | Appropriate assumption |
| **Non-linear** | Random Forest, Gradient Boosting | Captures non-linearity |
| **High Dimensionality** | Ridge, Lasso, Elastic Net | Handle multicollinearity |
| **Need Feature Selection** | Lasso, Elastic Net | Automatic selection |
| **Outliers Present** | Random Forest, Gradient Boosting | Robust to outliers |
| **Feature Interactions** | Random Forest, Gradient Boosting | Capture interactions |
| **Maximum Accuracy** | Gradient Boosting, Neural Networks | State-of-the-art performance |

### Clustering Tasks

| Problem | Recommended Algorithm | Why |
|---------|----------------------|-----|
| **Quick Exploration** | K-Means | Fast, simple, scalable |
| **Unknown Cluster Count** | DBSCAN, Hierarchical | Don't need to specify k |
| **Outlier Detection** | DBSCAN | Identifies noise points |
| **Spherical Clusters** | K-Means | Assumes spherical shapes |
| **Arbitrary Shapes** | DBSCAN, Hierarchical | Flexible cluster shapes |
| **Hierarchical Structure** | Hierarchical Clustering | Dendrogram interpretation |
| **Large Datasets** | K-Means | O(n) complexity |
| **Need Dendrogram** | Hierarchical Clustering | Visual structure |
| **Visualization** | UMAP, t-SNE | Better 2D/3D representations |

---

## Best Practices

### Data Preprocessing

```python
# 1. Handling Missing Values
from sklearn.impute import SimpleImputer, KNNImputer

# Simple imputation
imputer = SimpleImputer(strategy='mean')  # 'mean', 'median', 'most_frequent'
X_imputed = imputer.fit_transform(X)

# KNN imputation (better for multivariate missing data)
knn_imputer = KNNImputer(n_neighbors=5)
X_imputed = knn_imputer.fit_transform(X)

# 2. Feature Scaling
# For distance-based and regularized models: standardization or normalization

# Standardization (mean=0, std=1)
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Min-Max Normalization (range [0, 1])
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# 3. Categorical Features
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

# One-hot encoding for nominal features
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
X_encoded = encoder.fit_transform(X_cat)

# Label encoding for ordinal features
label_encoder = LabelEncoder()
X_encoded = label_encoder.fit_transform(X_cat)

# 4. Outlier Detection
from sklearn.preprocessing import RobustScaler
from sklearn.covariance import EllipticEnvelope

# Robust scaling (resistant to outliers)
robust_scaler = RobustScaler()
X_scaled = robust_scaler.fit_transform(X)

# Outlier detection
outlier_detector = EllipticEnvelope(contamination=0.05, random_state=42)
outlier_labels = outlier_detector.fit_predict(X)
X_clean = X[outlier_labels != -1]

# 5. Feature Engineering
# Create polynomial features
from sklearn.preprocessing import PolynomialFeatures

poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)

# Create interaction features manually
X_interact = np.c_[X, X[:, 0] * X[:, 1]]
```

### Model Training Pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV

# Complete pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', RandomForestClassifier(random_state=42))
])

# Hyperparameter tuning
param_grid = {
    'model__n_estimators': [100, 200],
    'model__max_depth': [5, 10, 15],
    'model__min_samples_split': [10, 20]
}

grid_search = GridSearchCV(
    pipeline,
    param_grid,
    cv=5,
    n_jobs=-1,
    verbose=1,
    scoring='f1'
)

grid_search.fit(X_train, y_train)

print(f"Best parameters: {grid_search.best_params_}")
print(f"Best CV score: {grid_search.best_score_:.4f}")

# Use best model
best_model = grid_search.best_estimator_
y_pred = best_model.predict(X_test)
```

### Monitoring and Validation

```python
# 1. Train-Validation-Test Split
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.3, random_state=42
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42
)

# 2. Model Checkpointing
import joblib

# Save best model
joblib.dump(best_model, 'best_model.pkl')

# Load model
loaded_model = joblib.load('best_model.pkl')

# 3. Track Metrics Over Time
metrics_history = {
    'train_loss': [],
    'val_loss': [],
    'train_accuracy': [],
    'val_accuracy': []
}

# 4. Production Deployment Checklist
"""
- Input validation (type, range, null checks)
- Output validation (range, NaN checks)
- Monitoring for data drift
- Model performance tracking
- Logging and alerting
- Version control for models
- A/B testing framework
- Rollback procedures
"""
```

### Common Pitfalls

```python
# 1. Data Leakage Prevention
# WRONG: Fit scaler on entire dataset before split
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # Data leakage!
X_train, X_test = train_test_split(X_scaled, ...)

# RIGHT: Fit scaler only on training data
X_train, X_test, y_train, y_test = train_test_split(X, y, ...)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # Fit on training only
X_test_scaled = scaler.transform(X_test)  # Transform test with training params

# 2. Proper Cross-Validation
# WRONG: Multiple train-test splits
scores = []
for i in range(10):
    X_train, X_test, y_train, y_test = train_test_split(X, y, ...)
    scores.append(model.fit(X_train, y_train).score(X_test, y_test))

# RIGHT: Use proper cross-validation
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=10)

# 3. Hyperparameter Tuning
# WRONG: Use test set for hyperparameter selection
best_accuracy = 0
for depth in range(1, 20):
    model = DecisionTreeClassifier(max_depth=depth)
    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)  # Tuning on test set!
    if acc > best_accuracy:
        best_accuracy = acc

# RIGHT: Use cross-validation or validation set
from sklearn.model_selection import GridSearchCV
grid_search = GridSearchCV(
    DecisionTreeClassifier(),
    {'max_depth': range(1, 20)},
    cv=5
)
grid_search.fit(X_train, y_train)
final_score = grid_search.score(X_test, y_test)

# 4. Class Imbalance
# WRONG: Ignore imbalanced classes
model = RandomForestClassifier()
model.fit(X_train, y_train)

# RIGHT: Use class weights or resampling
model = RandomForestClassifier(class_weight='balanced')
model.fit(X_train, y_train)

# Or use SMOTE for oversampling
from imblearn.over_sampling import SMOTE
smote = SMOTE(random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

# 5. Feature Scaling
# WRONG: Don't scale features for tree-based models
model = RandomForestClassifier()
model.fit(X_train_scaled, y_train)  # Unnecessary

# RIGHT: Only scale for distance-based and regularized models
# Tree-based: No scaling needed
# Distance-based (KNN, SVM, K-Means): Scale required
# Regularized (Ridge, Lasso, Logistic): Scale required
```

### Hyperparameter Tuning Strategy

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import uniform, randint

# Hyperparameter search strategies
# Strategy 1: Grid Search (exhaustive)
# Best for: Small parameter space, final tuning

# Strategy 2: Random Search (stochastic)
# Best for: Large parameter space, initial exploration

param_dist = {
    'n_estimators': randint(50, 300),
    'max_depth': [5, 10, 15, 20, None],
    'min_samples_split': randint(2, 20),
    'min_samples_leaf': randint(1, 10),
    'max_features': ['sqrt', 'log2'],
    'subsample': uniform(0.7, 0.3)
}

random_search = RandomizedSearchCV(
    RandomForestClassifier(random_state=42),
    param_dist,
    n_iter=20,  # Number of parameter settings sampled
    cv=5,
    n_jobs=-1,
    random_state=42,
    verbose=1
)
random_search.fit(X_train, y_train)

# Strategy 3: Bayesian Optimization
# Best for: Expensive models, limited budget
# Requires: pip install optuna or scikit-optimize
```

### Production Deployment Best Practices

```python
# 1. Model Versioning
import hashlib
import json

model_metadata = {
    'version': '1.0.0',
    'created_date': '2024-01-15',
    'training_data_hash': hashlib.md5(str(X_train.shape).encode()).hexdigest(),
    'hyperparameters': {
        'n_estimators': 100,
        'max_depth': 10
    },
    'performance': {
        'train_accuracy': 0.95,
        'val_accuracy': 0.92,
        'test_accuracy': 0.91
    },
    'feature_names': ['feature_1', 'feature_2'],
    'classes': ['negative', 'positive']
}

with open('model_metadata.json', 'w') as f:
    json.dump(model_metadata, f)

# 2. Input Validation
def validate_input(X_new):
    """Validate input before prediction"""
    required_features = 20
    if X_new.shape[1] != required_features:
        raise ValueError(f"Expected {required_features} features, got {X_new.shape[1]}")
    if np.any(np.isnan(X_new)):
        raise ValueError("Input contains NaN values")
    if np.any(np.isinf(X_new)):
        raise ValueError("Input contains infinite values")
    return True

# 3. Prediction with Error Handling
def make_prediction(X_new):
    """Make prediction with error handling"""
    try:
        validate_input(X_new)
        prediction = model.predict(X_new)
        probability = model.predict_proba(X_new)
        return {
            'success': True,
            'prediction': prediction,
            'probability': probability,
            'confidence': np.max(probability)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# 4. Model Monitoring
def log_prediction(features, prediction, probability, timestamp):
    """Log predictions for monitoring"""
    log_entry = {
        'timestamp': timestamp,
        'features_hash': hashlib.md5(str(features).encode()).hexdigest(),
        'prediction': prediction,
        'probability': probability
    }
    # Write to monitoring system
    return log_entry
```

---

## Quick Reference Summary

### Model Selection by Dataset Size

| Dataset Size | Recommended Models |
|--------------|-------------------|
| <100 samples | SVM, Logistic Regression |
| 100-10K | Logistic Regression, Random Forest, SVM |
| 10K-100K | Random Forest, Gradient Boosting |
| >100K | Logistic Regression (linear), SGDClassifier, Large-scale GB |

### Computational Complexity

| Algorithm | Training | Prediction | Space |
|-----------|----------|-----------|-------|
| Linear Regression | O(n·p²) | O(p) | O(p) |
| Logistic Regression | O(n·p) | O(p) | O(p) |
| Decision Tree | O(n·p·log n) | O(log n) | O(n) |
| Random Forest | O(k·n·p·log n) | O(k·log n) | O(k·n) |
| SVM | O(n²·p) | O(p) | O(n) |
| K-Means | O(k·n·p·i) | O(p) | O(n) |
| PCA | O(min(n,p)·p²) | O(p) | O(p) |

### Feature Scaling Requirements

| Algorithm | Scaling Needed? |
|-----------|-----------------|
| Linear/Logistic Regression | Yes |
| SVM | Yes |
| K-Nearest Neighbors | Yes |
| K-Means | Yes |
| Decision Trees | No |
| Random Forest | No |
| Gradient Boosting | No |
| PCA | Yes |

---

## Additional Resources

### Debugging Models

```python
# When model is underperforming:

# 1. Check data quality
print(f"Missing values: {X.isnull().sum().sum()}")
print(f"Duplicates: {X.duplicated().sum()}")
print(f"Feature ranges: {X.describe()}")

# 2. Check class balance
print(f"Class distribution: {pd.Series(y).value_counts()}")

# 3. Check for data leakage
# Ensure no information from test set used in training

# 4. Visualize feature distributions
# import matplotlib.pyplot as plt
# plt.figure(figsize=(15, 5))
# for i in range(min(5, X.shape[1])):
#     plt.subplot(1, 5, i+1)
#     plt.hist(X[:, i], bins=30)
#     plt.title(f'Feature {i}')
# plt.tight_layout()
# plt.show()

# 5. Check feature correlations
# corr_matrix = pd.DataFrame(X).corr()
# plt.figure(figsize=(10, 8))
# plt.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
# plt.colorbar()
# plt.title('Feature Correlation Matrix')
# plt.show()
```

---

**Last Updated**: 2024
**Version**: 1.0
