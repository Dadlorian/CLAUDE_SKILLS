# Feature Engineering Guide: Production-Ready Techniques

A comprehensive guide to feature engineering techniques used by Kaggle grandmasters and production ML systems. This guide covers numerical transformations, categorical encoding, temporal features, text extraction, selection methods, and automated approaches.

**Table of Contents**
- [1. Numerical Feature Transformations](#1-numerical-feature-transformations)
- [2. Categorical Encoding Strategies](#2-categorical-encoding-strategies)
- [3. Temporal Feature Engineering](#3-temporal-feature-engineering)
- [4. Text Feature Extraction](#4-text-feature-extraction)
- [5. Feature Selection Methods](#5-feature-selection-methods)
- [6. Feature Importance Analysis](#6-feature-importance-analysis)
- [7. Automated Feature Engineering](#7-automated-feature-engineering)
- [8. Feature Stores](#8-feature-stores)
- [9. Best Practices](#9-best-practices)

---

## 1. Numerical Feature Transformations

### 1.1 Scaling and Normalization

Scale features to prevent large-magnitude features from dominating learning algorithms.

**StandardScaler (Z-score normalization)**
```python
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd

# Create sample data
X = pd.DataFrame({
    'age': [25, 45, 35, 50, 28],
    'income': [50000, 120000, 85000, 150000, 62000],
    'score': [0.7, 0.9, 0.65, 0.95, 0.72]
})

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# For production: save the scaler
import pickle
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

# In serving: transform with saved scaler
X_new_scaled = scaler.transform(X_new)
```

**RobustScaler (resistant to outliers)**
```python
from sklearn.preprocessing import RobustScaler

# Use for data with outliers
robust_scaler = RobustScaler()
X_robust = robust_scaler.fit_transform(X)

# IQR-based scaling: uses median and quartiles instead of mean/std
# Formula: (x - median) / IQR
```

**MinMaxScaler (bounded to [0,1])**
```python
from sklearn.preprocessing import MinMaxScaler

# Useful when you need bounded features (e.g., neural networks)
minmax_scaler = MinMaxScaler(feature_range=(0, 1))
X_minmax = minmax_scaler.fit_transform(X)
```

**PowerTransformer (Yeo-Johnson)**
```python
from sklearn.preprocessing import PowerTransformer

# Makes data more Gaussian-like, improves linear model performance
pt = PowerTransformer(method='yeo-johnson')
X_transformed = pt.fit_transform(X)

# Also supports 'box-cox' for positive-only data
```

### 1.2 Handling Skewness

**Log Transform**
```python
import numpy as np

# For right-skewed data (house prices, income)
X['log_income'] = np.log1p(X['income'])  # log1p handles zeros

# Box-Cox Transform (automatic optimal lambda)
from scipy.stats import boxcox
X['income_boxcox'], lambda_param = boxcox(X['income'] + 1)
```

**Polynomial Features**
```python
from sklearn.preprocessing import PolynomialFeatures

# Create interaction terms and polynomial features
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X[['age', 'income']])

# Useful for capturing non-linear relationships
# Warning: can cause high dimensionality (p features -> p*(p+3)/2 features)
```

### 1.3 Binning and Discretization

```python
# Equal-width binning
X['age_bin_width'] = pd.cut(X['age'], bins=5)

# Equal-frequency binning (quantiles)
X['age_bin_freq'] = pd.qcut(X['age'], q=5)

# Custom bins
bins = [0, 30, 50, 100]
labels = ['young', 'middle', 'senior']
X['age_category'] = pd.cut(X['age'], bins=bins, labels=labels)

# KMeans binning (optimal for tree models)
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=5, random_state=42)
X['age_kmeans'] = kmeans.fit_predict(X[['age']])
```

### 1.4 Mathematical Transformations

```python
# Reciprocal transformation
X['reciprocal_value'] = 1 / (X['value'] + 1)  # +1 to avoid division by zero

# Square root
X['sqrt_value'] = np.sqrt(X['value'])

# Exponential
X['exp_value'] = np.exp(X['value'])

# Sigmoid (bounds to 0-1)
X['sigmoid_value'] = 1 / (1 + np.exp(-X['value']))

# Log-ratio (for compositional data)
X['log_ratio'] = np.log(X['feature_a'] / (X['feature_b'] + 1e-10))
```

---

## 2. Categorical Encoding Strategies

### 2.1 One-Hot Encoding

Best for tree models and when categories are unordered.

```python
# Simple one-hot encoding
X_encoded = pd.get_dummies(X, columns=['country', 'product_category'])

# Sklearn approach (better for pipelines)
from sklearn.preprocessing import OneHotEncoder

ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
X_encoded = ohe.fit_transform(X[['country', 'category']])

# Production tip: specify categories explicitly
categories = [['US', 'UK', 'CA', 'AU'], ['A', 'B', 'C']]
ohe = OneHotEncoder(categories=categories, handle_unknown='ignore')
```

### 2.2 Label Encoding

For ordinal categories or when you need dense features.

```python
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
X['education_encoded'] = le.fit_transform(X['education'])
# maps: ['high_school', 'bachelor', 'master', 'phd'] -> [0, 1, 2, 3]
```

### 2.3 Target Encoding (Mean Encoding)

Powerful technique that uses target variable information.

```python
# Simple implementation
target_encoding = X.groupby('city')['target'].agg(['mean', 'count']).reset_index()
target_encoding.columns = ['city', 'city_target_mean', 'city_count']

X = X.merge(target_encoding, on='city', how='left')

# Production-grade: with smoothing (regularization)
def target_encode(X, column, target, smoothing=1.0):
    """
    Target encoding with smoothing to prevent overfitting.

    smoothing: higher values = more regularization toward global mean
    """
    global_mean = target.mean()

    stats = X.groupby(column)[target.name].agg(['count', 'mean'])
    stats['smoothed_mean'] = (
        stats['count'] * stats['mean'] + smoothing * global_mean
    ) / (stats['count'] + smoothing)

    return X[column].map(stats['smoothed_mean'])

X['city_target_encoded'] = target_encode(X, 'city', X['target'], smoothing=20)
```

### 2.4 Frequency Encoding

```python
# Count occurrences of each category
freq_encoding = X['category'].value_counts()
X['category_freq'] = X['category'].map(freq_encoding)

# Log-frequency for better distribution
X['category_log_freq'] = np.log1p(X['category'].map(freq_encoding))
```

### 2.5 Embeddings for High-Cardinality Categories

For categories with hundreds/thousands of unique values:

```python
# Using entity embeddings (from neural networks)
import tensorflow as tf
from tensorflow.keras.layers import Embedding, Dense, Input, Flatten, Concatenate
from tensorflow.keras.models import Model

# Create embeddings for city (500 categories)
city_input = Input(shape=(1,), name='city')
city_embedding = Embedding(input_dim=500, output_dim=10)(city_input)
city_flat = Flatten()(city_embedding)

# Combine with other features
other_input = Input(shape=(num_other_features,), name='other')
merged = Concatenate()([city_flat, other_input])

output = Dense(1)(merged)
model = Model(inputs=[city_input, other_input], outputs=output)

# Use embedding layer output as features
encoder = Model(inputs=[city_input, other_input], outputs=city_flat)
embeddings = encoder.predict([X['city_encoded'], X[other_features]])
```

### 2.6 Binary Features

```python
# Direct binary encoding
X['is_premium'] = (X['subscription_level'] == 'premium').astype(int)
X['is_weekend'] = X['day_of_week'].isin([5, 6]).astype(int)

# Multiple binary flags from single category
X['country_us'] = (X['country'] == 'US').astype(int)
X['country_uk'] = (X['country'] == 'UK').astype(int)
X['country_other'] = (~X['country'].isin(['US', 'UK'])).astype(int)
```

---

## 3. Temporal Feature Engineering

### 3.1 Date/Time Extraction

```python
# Convert to datetime
X['date'] = pd.to_datetime(X['date'])

# Extract components
X['year'] = X['date'].dt.year
X['month'] = X['date'].dt.month
X['day'] = X['date'].dt.day
X['dayofweek'] = X['date'].dt.dayofweek  # 0=Monday, 6=Sunday
X['quarter'] = X['date'].dt.quarter
X['dayofyear'] = X['date'].dt.dayofyear
X['weekofyear'] = X['date'].dt.isocalendar().week
X['is_weekend'] = X['date'].dt.dayofweek >= 5

# Cyclical encoding for month (circular nature)
X['month_sin'] = np.sin(2 * np.pi * X['month'] / 12)
X['month_cos'] = np.cos(2 * np.pi * X['month'] / 12)

X['dayofweek_sin'] = np.sin(2 * np.pi * X['dayofweek'] / 7)
X['dayofweek_cos'] = np.cos(2 * np.pi * X['dayofweek'] / 7)
```

### 3.2 Time-Based Features

```python
# Days since reference date
reference_date = pd.Timestamp('2024-01-01')
X['days_since_ref'] = (X['date'] - reference_date).dt.days

# Tenure/Age of account
X['days_since_signup'] = (X['current_date'] - X['signup_date']).dt.days
X['years_tenure'] = X['days_since_signup'] / 365.25

# Time until event
X['days_until_expiry'] = (X['expiry_date'] - X['current_date']).dt.days

# Season (Northern hemisphere)
def get_season(month):
    if month in [12, 1, 2]:
        return 'winter'
    elif month in [3, 4, 5]:
        return 'spring'
    elif month in [6, 7, 8]:
        return 'summer'
    else:
        return 'fall'

X['season'] = X['month'].apply(get_season)
```

### 3.3 Lag Features (Time Series)

```python
# Sort by time first
X = X.sort_values('date').reset_index(drop=True)

# Lag features (previous values)
for lag in [1, 7, 30]:
    X[f'sales_lag_{lag}'] = X['sales'].shift(lag)

# Rolling statistics
X['sales_rolling_mean_7'] = X['sales'].rolling(window=7, min_periods=1).mean()
X['sales_rolling_std_7'] = X['sales'].rolling(window=7, min_periods=1).std()
X['sales_rolling_max_30'] = X['sales'].rolling(window=30, min_periods=1).max()

# Expanding statistics (all history up to current)
X['sales_expanding_mean'] = X['sales'].expanding(min_periods=1).mean()
X['sales_expanding_max'] = X['sales'].expanding(min_periods=1).max()
```

### 3.4 Grouped Time Features

```python
# Group by entity then calculate time features
X = X.sort_values(['user_id', 'date']).reset_index(drop=True)

# Time since last event for each user
X['days_since_last_purchase'] = X.groupby('user_id')['date'].diff().dt.days

# Event count in rolling window
X['purchases_7d'] = X.groupby('user_id')['date'].rolling('7D').count().reset_index(drop=True)

# Time between events
X['purchase_interval_days'] = X.groupby('user_id')['date'].diff().dt.days
```

---

## 4. Text Feature Extraction

### 4.1 Basic Text Features

```python
import pandas as pd
import numpy as np

X['text_length'] = X['text'].str.len()
X['word_count'] = X['text'].str.split().str.len()
X['avg_word_length'] = X['text_length'] / X['word_count']
X['unique_word_count'] = X['text'].apply(lambda x: len(set(x.split())))
X['punctuation_count'] = X['text'].str.count(r'[!?.,;:\-]')
```

### 4.2 TF-IDF Features

```python
from sklearn.feature_extraction.text import TfidfVectorizer

# Create TF-IDF vectors
tfidf = TfidfVectorizer(
    max_features=100,
    min_df=2,
    max_df=0.8,
    ngram_range=(1, 2),  # unigrams and bigrams
    stop_words='english'
)

X_tfidf = tfidf.fit_transform(X['text'])

# Convert to dense for models that need it
X_tfidf_dense = X_tfidf.toarray()

# Get feature names for interpretability
feature_names = tfidf.get_feature_names_out()
```

### 4.3 Word2Vec Embeddings

```python
from gensim.models import Word2Vec
import numpy as np

# Train Word2Vec
sentences = X['text'].str.split()
model = Word2Vec(
    sentences=sentences,
    vector_size=100,
    window=5,
    min_count=2,
    workers=4
)

# Create document embeddings (average of word vectors)
def get_document_embedding(text, model, vector_size=100):
    words = text.split()
    embeddings = [model.wv[w] for w in words if w in model.wv]

    if not embeddings:
        return np.zeros(vector_size)

    return np.mean(embeddings, axis=0)

X_embeddings = np.array([
    get_document_embedding(text, model)
    for text in X['text']
])
```

### 4.4 Pre-trained Language Models

```python
from transformers import AutoTokenizer, AutoModel
import torch

# Load BERT embeddings
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased", output_hidden_states=True)

def get_bert_embeddings(texts, model, tokenizer, layer=-2):
    """
    Extract BERT embeddings. Layer -2 is often better than last layer.
    """
    embeddings = []

    for text in texts:
        inputs = tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True)

        with torch.no_grad():
            outputs = model(inputs)
            hidden_states = outputs[2]  # All hidden states

        # Use second-to-last layer, average pooling
        embedding = hidden_states[layer][0].mean(dim=0).numpy()
        embeddings.append(embedding)

    return np.array(embeddings)

X_bert_embeddings = get_bert_embeddings(X['text'].values, model, tokenizer)
```

### 4.5 NLP Features

```python
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize

# Sentiment analysis
sia = SentimentIntensityAnalyzer()
X['sentiment_score'] = X['text'].apply(lambda x: sia.polarity_scores(x)['compound'])

# Sentence count
X['sentence_count'] = X['text'].apply(lambda x: len(sent_tokenize(x)))

# Named Entity Recognition
from transformers import pipeline
ner = pipeline("ner", model="dbmdz/bert-base-cased-finetuned-conll03-english")

def count_entities(text):
    entities = ner(text[:512])  # Limit to 512 chars
    return len(entities)

X['entity_count'] = X['text'].apply(count_entities)
```

---

## 5. Feature Selection Methods

### 5.1 Univariate Statistical Methods

```python
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
import pandas as pd

# Select K best features using f-statistic (classification)
selector = SelectKBest(score_func=f_classif, k=20)
X_selected = selector.fit_transform(X, y)

# Get selected feature names
selected_features = X.columns[selector.get_support()].tolist()

# Mutual information (doesn't assume linear relationship)
selector_mi = SelectKBest(score_func=mutual_info_classif, k=20)
X_selected_mi = selector_mi.fit_transform(X, y)

# Feature scores for interpretation
scores = pd.DataFrame({
    'feature': X.columns,
    'f_score': selector.scores_,
    'mi_score': selector_mi.scores_
}).sort_values('f_score', ascending=False)
```

### 5.2 RFE (Recursive Feature Elimination)

```python
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier

# RFE with Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rfe = RFE(estimator=rf, n_features_to_select=20, step=1)
X_rfe = rfe.fit_transform(X, y)

selected_rfe = X.columns[rfe.support_].tolist()

# RFECV: cross-validated feature selection
from sklearn.feature_selection import RFECV

rfecv = RFECV(estimator=rf, step=1, cv=5, scoring='roc_auc')
X_rfecv = rfecv.fit_transform(X, y)

print(f"Optimal number of features: {rfecv.n_features_}")
```

### 5.3 Feature Importance from Models

```python
from sklearn.ensemble import GradientBoostingClassifier
import pandas as pd

# Train model
gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
gb.fit(X, y)

# Extract importances
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': gb.feature_importances_
}).sort_values('importance', ascending=False)

# Select top features
top_features = feature_importance.head(20)['feature'].tolist()
```

### 5.4 Permutation Feature Importance

Model-agnostic method that's more reliable than built-in importances:

```python
from sklearn.inspection import permutation_importance
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Calculate permutation importance
perm_importance = permutation_importance(
    model, X, y, n_repeats=10, random_state=42, n_jobs=-1
)

importance_df = pd.DataFrame({
    'feature': X.columns,
    'importance': perm_importance.importances_mean,
    'std': perm_importance.importances_std
}).sort_values('importance', ascending=False)
```

### 5.5 SHAP for Feature Importance

```python
import shap
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Create SHAP explainer
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

# Feature importance (mean absolute SHAP values)
feature_importance_shap = pd.DataFrame({
    'feature': X.columns,
    'importance': np.abs(shap_values).mean(axis=0)
}).sort_values('importance', ascending=False)

# Visualizations
shap.summary_plot(shap_values, X, plot_type="bar")
shap.summary_plot(shap_values, X)
```

### 5.6 Multicollinearity Analysis

```python
import numpy as np
import pandas as pd

# Calculate correlation matrix
corr_matrix = X.corr()

# Variance Inflation Factor (VIF)
from statsmodels.stats.outliers_influence import variance_inflation_factor

vif_data = pd.DataFrame()
vif_data["feature"] = X.columns
vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
vif_data = vif_data.sort_values('VIF', ascending=False)

# Remove features with VIF > 10 (indicates multicollinearity)
high_vif_features = vif_data[vif_data['VIF'] > 10]['feature'].tolist()
X_low_vif = X.drop(columns=high_vif_features)
```

---

## 6. Feature Importance Analysis

### 6.1 SHAP Deep Dive

```python
import shap
from sklearn.ensemble import GradientBoostingClassifier
import matplotlib.pyplot as plt

# Train model
model = GradientBoostingClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Create SHAP explainer
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Summary plot (feature importance)
shap.summary_plot(shap_values, X_test, plot_type="bar")
plt.title("Feature Importance (Mean |SHAP|)")
plt.show()

# Summary plot with value distribution
shap.summary_plot(shap_values, X_test)
plt.title("SHAP Values Distribution")
plt.show()

# Force plot for single prediction
shap.force_plot(explainer.expected_value, shap_values[0], X_test.iloc[0])

# Dependence plot for feature interaction
shap.dependence_plot("age", shap_values, X_test)
```

### 6.2 Feature Interaction Analysis

```python
import shap
import pandas as pd

# H-statistic for detecting interactions
def calculate_interaction_strength(shap_values, features_df):
    """
    Simple interaction strength based on SHAP value variance.
    Higher variance = stronger interaction with other features.
    """
    interaction_strength = []

    for i in range(shap_values.shape[1]):
        # Variance across samples for each feature
        var = np.var(shap_values[:, i])
        interaction_strength.append({
            'feature': features_df.columns[i],
            'interaction_strength': var
        })

    return pd.DataFrame(interaction_strength).sort_values('interaction_strength', ascending=False)

interactions = calculate_interaction_strength(shap_values, X_test)
```

### 6.3 Partial Dependence Plots

```python
from sklearn.inspection import plot_partial_dependence
import matplotlib.pyplot as plt

# Partial dependence for single feature
plot_partial_dependence(model, X_train, features=[0], feature_names=X_train.columns)
plt.show()

# 2D partial dependence for interactions
plot_partial_dependence(model, X_train, features=[(0, 1)], feature_names=X_train.columns)
plt.show()
```

---

## 7. Automated Feature Engineering

### 7.1 Featuretools

```python
import featuretools as ft
import pandas as pd

# Create entityset (relationship database)
es = ft.EntitySet(id="customer_data")

# Add entities
es.add_dataframe(
    dataframe_name="transactions",
    dataframe=transactions_df,
    index="transaction_id"
)

es.add_dataframe(
    dataframe_name="customers",
    dataframe=customers_df,
    index="customer_id"
)

# Define relationship
es.add_relationship(
    ft.Relationship(
        parent_entity_id="customers",
        child_entity_id="transactions",
        parent_column_name="customer_id",
        child_column_name="customer_id"
    )
)

# Generate features (Deep Feature Synthesis)
feature_matrix, feature_defs = ft.dfs(
    entityset=es,
    target_entity="customers",
    trans_primitives=["sum", "mean", "count", "max", "min", "std"],
    agg_primitives=["sum", "mean", "count", "max", "min", "std"],
    max_depth=2,
    verbose=1
)

print(f"Generated {len(feature_matrix.columns)} features")
print(feature_matrix.head())
```

### 7.2 TSFRESH (Time Series Features)

```python
from tsfresh import extract_features
from tsfresh.feature_extraction import ComprehensiveFeatureExtractionSettings
import pandas as pd

# Prepare data in tsfresh format: id, time, value
ts_data = pd.DataFrame({
    'id': [1]*100 + [2]*100,  # time series id
    'time': list(range(100)) * 2,
    'value': np.random.randn(200)
})

# Extract features
settings = ComprehensiveFeatureExtractionSettings()
ts_features = extract_features(
    ts_data,
    column_id='id',
    column_sort='time',
    default_fc_parameters=settings,
    n_jobs=4
)

print(f"Extracted {ts_features.shape[1]} time series features")
print(ts_features.head())
```

### 7.3 Auto-sklearn for Feature Engineering

```python
import autosklearn.classification

# Auto-sklearn automatically performs feature engineering
automl = autosklearn.classification.AutoSklearnClassifier(
    time_left_for_this_task=3600,
    per_run_time_limit=120,
    ensemble_memory_limit=4096,
    include_preprocessors=['no_preprocessing', 'select_percentile_classification_regression'],
    include_feature_preprocessors=['no_preprocessing', 'polynomial'],
    n_jobs=4
)

automl.fit(X_train, y_train)
predictions = automl.predict(X_test)

# Access generated features
print(automl.show_models())
```

---

## 8. Feature Stores

Production-grade feature management for ML pipelines.

### 8.1 Feast (Feature Store)

```yaml
# registry.yaml - Feast configuration
project: credit_scoring
registry: s3://my-bucket/registry.db
provider: aws
online_store:
  type: dynamodb
  table_name: credit_features
offline_store:
  type: s3
  path_prefix: s3://my-bucket/offline
```

```python
# features.py
from feast import Feature, FeatureView, Entity, FeatureStore
from feast.data_sources import ParquetSource
from datetime import timedelta

# Define entity
customer = Entity(
    name="customer_id",
    description="Unique customer identifier"
)

# Define feature view
transactions_source = ParquetSource(
    path="s3://my-bucket/transactions.parquet"
)

transaction_features = FeatureView(
    name="transaction_stats",
    entities=[customer],
    features=[
        Feature(name="total_transactions", dtype=ValueType.INT64),
        Feature(name="avg_transaction_amount", dtype=ValueType.DOUBLE),
        Feature(name="last_transaction_date", dtype=ValueType.STRING),
    ],
    source=transactions_source,
    ttl=timedelta(days=1)
)

# In application code
store = FeatureStore()

# Get features for serving
feature_dict = store.get_online_features(
    features=[
        "transaction_stats:total_transactions",
        "transaction_stats:avg_transaction_amount"
    ],
    entity_rows=[
        {"customer_id": 12345}
    ]
).to_dict()
```

### 8.2 Building a Simple Feature Store

```python
import pandas as pd
from typing import Dict, List
import json
from datetime import datetime

class SimpleFeatureStore:
    """Minimal feature store implementation for production."""

    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.metadata = {}

    def register_feature_group(
        self,
        name: str,
        df: pd.DataFrame,
        entity_id: str,
        ttl_days: int = 1
    ):
        """Register a feature group."""
        path = f"{self.storage_path}/{name}.parquet"
        df.to_parquet(path)

        self.metadata[name] = {
            'path': path,
            'entity_id': entity_id,
            'ttl_days': ttl_days,
            'registered_at': datetime.now().isoformat(),
            'features': df.columns.tolist()
        }

        # Save metadata
        with open(f"{self.storage_path}/metadata.json", 'w') as f:
            json.dump(self.metadata, f)

    def get_features(
        self,
        feature_group: str,
        entity_ids: List[int]
    ) -> pd.DataFrame:
        """Retrieve features."""
        df = pd.read_parquet(self.metadata[feature_group]['path'])
        entity_id = self.metadata[feature_group]['entity_id']
        return df[df[entity_id].isin(entity_ids)]

    def get_batch_features(self, requests: Dict[str, List[int]]) -> pd.DataFrame:
        """Get multiple feature groups joined by entity."""
        result = None

        for feature_group, entity_ids in requests.items():
            features = self.get_features(feature_group, entity_ids)

            if result is None:
                result = features
            else:
                result = result.merge(features, on='entity_id', how='left')

        return result

# Usage
fs = SimpleFeatureStore('/data/feature_store')

# Register features
fs.register_feature_group('customer_stats', customer_features, entity_id='customer_id')
fs.register_feature_group('transaction_stats', transaction_features, entity_id='customer_id')

# Get features
features = fs.get_batch_features({
    'customer_stats': [123, 456, 789],
    'transaction_stats': [123, 456, 789]
})
```

---

## 9. Best Practices

### 9.1 Production-Grade Feature Engineering Pipeline

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer, Pipeline
from sklearn.preprocessing import OneHotEncoder
import joblib

class ProductionFeaturePipeline:
    """
    Production-ready feature engineering pipeline.
    Separates fit and transform for proper train/test handling.
    """

    def __init__(self):
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(handle_unknown='ignore')
        self.is_fitted = False
        self.numeric_features = []
        self.categorical_features = []

    def fit(self, X: pd.DataFrame, y: pd.Series = None) -> 'ProductionFeaturePipeline':
        """Fit the pipeline on training data."""

        # Identify feature types
        self.numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()

        # Fit transformers on numeric features
        if self.numeric_features:
            self.scaler.fit(X[self.numeric_features])

        # Fit encoder on categorical features
        if self.categorical_features:
            self.encoder.fit(X[self.categorical_features])

        self.is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Transform data using fitted pipeline."""

        if not self.is_fitted:
            raise ValueError("Pipeline must be fitted before transform")

        transformed_features = []

        # Transform numeric features
        if self.numeric_features:
            numeric_transformed = self.scaler.transform(X[self.numeric_features])
            transformed_features.append(numeric_transformed)

        # Transform categorical features
        if self.categorical_features:
            categorical_transformed = self.encoder.transform(X[self.categorical_features]).toarray()
            transformed_features.append(categorical_transformed)

        # Concatenate all features
        return np.hstack(transformed_features)

    def save(self, path: str):
        """Save pipeline for production."""
        joblib.dump(self, path)

    @staticmethod
    def load(path: str) -> 'ProductionFeaturePipeline':
        """Load saved pipeline."""
        return joblib.load(path)

# Usage
pipeline = ProductionFeaturePipeline()
pipeline.fit(X_train, y_train)

# Save for production
pipeline.save('feature_pipeline.pkl')

# In production
pipeline = ProductionFeaturePipeline.load('feature_pipeline.pkl')
X_transformed = pipeline.transform(X_new)
```

### 9.2 Feature Engineering Checklist

- **Exploratory Data Analysis (EDA)**
  - Check distributions, outliers, missing values
  - Analyze correlations and relationships
  - Understand domain constraints and business logic

- **Feature Creation**
  - Use domain knowledge (most important!)
  - Create interactions for non-linear relationships
  - Test polynomial and other transformations
  - Avoid data leakage (target information in features)

- **Handling Missing Values**
  ```python
  # Strategy 1: Remove rows
  X = X.dropna()

  # Strategy 2: Fill with statistics
  X['age'].fillna(X['age'].median(), inplace=True)

  # Strategy 3: Fill with model
  from sklearn.impute import SimpleImputer
  imputer = SimpleImputer(strategy='mean')
  X_imputed = imputer.fit_transform(X)

  # Strategy 4: Create missing indicator
  X['age_missing'] = X['age'].isna().astype(int)
  ```

- **Scaling & Normalization**
  - Use StandardScaler for linear models
  - Use MinMaxScaler for neural networks
  - Use RobustScaler for data with outliers
  - NEVER fit on test set

- **Dimensionality Reduction**
  - Use PCA when you have too many features
  - Use feature selection before PCA
  - Monitor explained variance

- **Validation Strategy**
  - Use cross-validation to estimate feature importance
  - Validate on holdout test set
  - Check for temporal leakage in time series

### 9.3 Avoiding Data Leakage

```python
# WRONG: Feature computed using target information
X['high_value_customer'] = y  # Leakage!

# WRONG: Feature computed on full dataset before split
X_scaled = scaler.fit_transform(X)
X_train, X_test = train_test_split(X_scaled)  # Leakage!

# CORRECT: Fit on train, transform all
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

X_train, X_test = train_test_split(X, test_size=0.2)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# WRONG: Time series - using future information
df = df.sort_values('date')
df['future_price'] = df['price'].shift(-1)  # Leakage!

# CORRECT: Use only past information
df = df.sort_values('date')
df['past_7d_price_mean'] = df['price'].rolling(7).mean().shift(1)
```

### 9.4 Feature Engineering Best Practices from Kaggle Grandmasters

1. **Start Simple**
   - Establish baseline with simple features
   - Gradually add complexity
   - Measure improvement for each feature

2. **Domain Expertise is King**
   - Understand the problem deeply
   - Create features that make business sense
   - Talk to domain experts

3. **Iterative Approach**
   - Create hypothesis about important features
   - Engineer features
   - Test on validation set
   - Iterate based on results

4. **Feature Interactions**
   - Don't just add individual features
   - Create interactions for complex relationships
   - Use trees to discover important interactions

5. **Regularization**
   - More features = more overfitting risk
   - Use L1/L2 regularization
   - Use feature selection

6. **Documentation**
   - Document what each feature represents
   - Note creation date and method
   - Track feature performance over time

```python
# Feature documentation example
feature_documentation = {
    'age_normalized': {
        'description': 'Normalized age (0-1 range)',
        'source': 'age column',
        'method': 'MinMaxScaler',
        'created_date': '2024-01-15',
        'importance_rank': 3,
        'correlation_with_target': 0.45
    },
    'income_log': {
        'description': 'Log-transformed income',
        'source': 'income column',
        'method': 'log1p transformation',
        'created_date': '2024-01-15',
        'importance_rank': 1,
        'correlation_with_target': 0.62
    }
}

import json
with open('feature_documentation.json', 'w') as f:
    json.dump(feature_documentation, f, indent=2)
```

### 9.5 Feature Engineering for Different Model Types

**Linear Models (Regression, Logistic Regression)**
- Polynomial features for non-linearity
- Scale features (StandardScaler)
- Handle multicollinearity (VIF analysis)
- Create explicit interaction terms

```python
from sklearn.preprocessing import PolynomialFeatures

poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
```

**Tree-based Models (Random Forest, XGBoost)**
- Don't need scaling
- Automatically discover interactions
- Can handle categorical features directly
- Benefit from domain-specific features
- Feature importance is reliable

```python
# Trees handle categorical directly
from xgboost import XGBClassifier

model = XGBClassifier(
    tree_method='gpu_hist',
    enable_categorical=True
)
model.fit(X, y)
```

**Neural Networks**
- Scale features (0-1 or -1 to 1)
- Embedding layers for categorical
- Can learn interactions automatically
- Benefit from normalized features

```python
# Feature preparation for neural networks
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler(feature_range=(0, 1))
X_scaled = scaler.fit_transform(X)

# Embeddings for categorical
embedding = tf.keras.layers.Embedding(
    input_dim=num_categories,
    output_dim=8
)
```

---

## Quick Reference: Feature Engineering Workflow

```python
# 1. Load and explore
import pandas as pd
df = pd.read_csv('data.csv')
print(df.info())
print(df.describe())

# 2. Handle missing values
df = df.dropna()  # or impute

# 3. Create features
df['log_income'] = np.log1p(df['income'])
df['age_squared'] = df['age'] ** 2
df['income_age_interaction'] = df['income'] * df['age']

# 4. Encode categorical
df = pd.get_dummies(df, columns=['category'])

# 5. Scale numerical
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaled_features = scaler.fit_transform(df[numeric_cols])

# 6. Select features
from sklearn.feature_selection import SelectKBest, f_classif
selector = SelectKBest(f_classif, k=20)
X_selected = selector.fit_transform(X, y)

# 7. Train and evaluate
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X_selected, y, cv=5)

# 8. Save pipeline
import joblib
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('selector', SelectKBest(f_classif, k=20)),
    ('model', RandomForestClassifier())
])
joblib.dump(pipeline, 'pipeline.pkl')
```

---

## Further Resources

- **Kaggle**: https://www.kaggle.com/learn/feature-engineering
- **Featuretools**: https://www.featuretools.com/
- **Feast**: https://feast.dev/
- **SHAP**: https://shap.readthedocs.io/
- **Auto-sklearn**: https://automl.github.io/auto-sklearn/
- **Papers**: "A Few Useful Things to Know about Machine Learning" - Domingos, P.

---

**Last Updated**: 2024-11-19
**Production-Ready**: Yes
**Tested With**: Python 3.8+, scikit-learn, pandas, numpy
