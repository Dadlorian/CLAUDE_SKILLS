# Building a Production Recommendation Engine

This guide walks through building a complete recommendation system from scratch, covering data pipeline, model training, serving infrastructure, and A/B testing.

## Architecture Overview

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  User Activity  │─────>│   Data Pipeline  │─────>│  Feature Store  │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                                              │
                                                              ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Recommendation │<─────│   Model Serving  │<─────│  Trained Models │
│      API        │      │   Infrastructure │      └─────────────────┘
└─────────────────┘      └──────────────────┘
        │
        ▼
┌─────────────────┐
│   A/B Testing   │
│   & Analytics   │
└─────────────────┘
```

## Phase 1: Data Collection & Pipeline

### 1.1 Event Tracking

Track user interactions in real-time:

```python
# event_tracker.py
import json
import time
from kafka import KafkaProducer

class EventTracker:
    def __init__(self, kafka_servers):
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def track_view(self, user_id, item_id, duration_seconds, context):
        """Track content view event"""
        event = {
            'event_type': 'view',
            'user_id': user_id,
            'item_id': item_id,
            'duration': duration_seconds,
            'timestamp': int(time.time()),
            'device': context.get('device'),
            'location': context.get('location'),
            'time_of_day': context.get('time_of_day')
        }
        self.producer.send('user-events', event)

    def track_rating(self, user_id, item_id, rating):
        """Track explicit rating"""
        event = {
            'event_type': 'rating',
            'user_id': user_id,
            'item_id': item_id,
            'rating': rating,
            'timestamp': int(time.time())
        }
        self.producer.send('user-events', event)

    def track_search(self, user_id, query, results_clicked):
        """Track search behavior"""
        event = {
            'event_type': 'search',
            'user_id': user_id,
            'query': query,
            'results_clicked': results_clicked,
            'timestamp': int(time.time())
        }
        self.producer.send('user-events', event)
```

### 1.2 Feature Engineering

Transform raw events into features for ML:

```python
# feature_engineering.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class FeatureEngineer:
    def __init__(self):
        self.lookback_days = 30

    def compute_user_features(self, user_events):
        """Compute user behavioral features"""

        features = {}

        # Viewing history features
        features['total_views'] = len(user_events)
        features['unique_items_viewed'] = user_events['item_id'].nunique()
        features['avg_view_duration'] = user_events['duration'].mean()

        # Genre preferences
        genre_counts = user_events.groupby('genre').size()
        top_genres = genre_counts.nlargest(3)
        features['top_genre_1'] = top_genres.index[0] if len(top_genres) > 0 else None
        features['top_genre_2'] = top_genres.index[1] if len(top_genres) > 1 else None
        features['top_genre_3'] = top_genres.index[2] if len(top_genres) > 2 else None

        # Temporal patterns
        user_events['hour'] = pd.to_datetime(user_events['timestamp'], unit='s').dt.hour
        features['preferred_viewing_hour'] = user_events['hour'].mode()[0]

        # Device preferences
        device_counts = user_events['device'].value_counts()
        features['primary_device'] = device_counts.index[0] if len(device_counts) > 0 else None

        # Engagement metrics
        features['completion_rate'] = (
            user_events[user_events['duration'] > 300].shape[0] / len(user_events)
        )

        # Recency
        latest_view = user_events['timestamp'].max()
        features['days_since_last_view'] = (
            datetime.now() - datetime.fromtimestamp(latest_view)
        ).days

        return features

    def compute_item_features(self, item_metadata, interaction_stats):
        """Compute item features"""

        features = {}

        # Metadata features
        features['genre'] = item_metadata['genre']
        features['release_year'] = item_metadata['release_year']
        features['duration_minutes'] = item_metadata['duration_minutes']
        features['language'] = item_metadata['language']
        features['maturity_rating'] = item_metadata['maturity_rating']

        # Popularity features
        features['total_views'] = interaction_stats.get('view_count', 0)
        features['unique_viewers'] = interaction_stats.get('unique_viewers', 0)
        features['avg_rating'] = interaction_stats.get('avg_rating', 0)
        features['rating_count'] = interaction_stats.get('rating_count', 0)

        # Temporal features
        features['days_since_release'] = (
            datetime.now() - datetime.fromisoformat(item_metadata['release_date'])
        ).days

        # Engagement features
        features['avg_completion_rate'] = interaction_stats.get('completion_rate', 0)
        features['share_count'] = interaction_stats.get('shares', 0)

        return features

    def create_user_item_pairs(self, user_id, candidate_items, user_features, item_features_dict):
        """Create feature vectors for user-item pairs"""

        pairs = []

        for item_id in candidate_items:
            item_features = item_features_dict.get(item_id, {})

            # Combine user and item features
            pair_features = {
                **user_features,
                **item_features,
                'user_id': user_id,
                'item_id': item_id
            }

            # Cross features
            pair_features['genre_match'] = (
                item_features.get('genre') == user_features.get('top_genre_1')
            )
            pair_features['device_compatibility'] = self.check_device_compatibility(
                user_features.get('primary_device'),
                item_features.get('supported_devices')
            )

            pairs.append(pair_features)

        return pairs

    def check_device_compatibility(self, user_device, supported_devices):
        """Check if item is compatible with user's device"""
        if not user_device or not supported_devices:
            return True
        return user_device in supported_devices
```

## Phase 2: Model Training

### 2.1 Collaborative Filtering with ALS

```python
# collaborative_filtering.py
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator

class CollaborativeFilteringModel:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("RecommendationSystem") \
            .getOrCreate()

        self.model = None

    def train(self, interactions_df, rank=50, max_iter=10, reg_param=0.1):
        """Train ALS model on user-item interactions"""

        # Convert to Spark DataFrame
        spark_df = self.spark.createDataFrame(interactions_df)

        # Split data
        train, test = spark_df.randomSplit([0.8, 0.2], seed=42)

        # Build ALS model
        als = ALS(
            rank=rank,
            maxIter=max_iter,
            regParam=reg_param,
            userCol="user_id",
            itemCol="item_id",
            ratingCol="rating",
            coldStartStrategy="drop",
            implicitPrefs=False
        )

        # Train
        self.model = als.fit(train)

        # Evaluate
        predictions = self.model.transform(test)
        evaluator = RegressionEvaluator(
            metricName="rmse",
            labelCol="rating",
            predictionCol="prediction"
        )
        rmse = evaluator.evaluate(predictions)

        print(f"Root-mean-square error = {rmse}")

        return rmse

    def recommend_for_user(self, user_id, n=10):
        """Generate top N recommendations for a user"""

        user_df = self.spark.createDataFrame([(user_id,)], ["user_id"])
        recommendations = self.model.recommendForUserSubset(user_df, n)

        # Extract item IDs and scores
        recs = recommendations.collect()[0].recommendations
        return [(rec.item_id, rec.rating) for rec in recs]

    def recommend_for_all_users(self, n=10):
        """Generate recommendations for all users (batch)"""

        user_recs = self.model.recommendForAllUsers(n)
        return user_recs

    def get_item_factors(self):
        """Get learned item embeddings"""
        return self.model.itemFactors

    def get_user_factors(self):
        """Get learned user embeddings"""
        return self.model.userFactors
```

### 2.2 Deep Learning Model (Two-Tower)

```python
# two_tower_model.py
import tensorflow as tf
import tensorflow_recommenders as tfrs
import numpy as np

class TwoTowerRecommender(tfrs.Model):
    def __init__(self, user_vocab, item_vocab, embedding_dim=128):
        super().__init__()

        # User tower
        self.user_model = tf.keras.Sequential([
            tf.keras.layers.StringLookup(
                vocabulary=user_vocab, mask_token=None
            ),
            tf.keras.layers.Embedding(len(user_vocab) + 1, embedding_dim),
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(embedding_dim)
        ])

        # Item tower
        self.item_model = tf.keras.Sequential([
            tf.keras.layers.StringLookup(
                vocabulary=item_vocab, mask_token=None
            ),
            tf.keras.layers.Embedding(len(item_vocab) + 1, embedding_dim),
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(embedding_dim)
        ])

        # Task
        self.task = tfrs.tasks.Retrieval(
            metrics=tfrs.metrics.FactorizedTopK(
                candidates=item_vocab
            )
        )

    def compute_loss(self, features, training=False):
        user_embeddings = self.user_model(features["user_id"])
        item_embeddings = self.item_model(features["item_id"])

        return self.task(user_embeddings, item_embeddings)

    def call(self, features):
        user_embeddings = self.user_model(features["user_id"])
        item_embeddings = self.item_model(features["item_id"])

        return {
            "user_embeddings": user_embeddings,
            "item_embeddings": item_embeddings
        }

def train_two_tower_model(train_dataset, test_dataset, user_vocab, item_vocab, epochs=10):
    """Train two-tower model"""

    model = TwoTowerRecommender(user_vocab, item_vocab, embedding_dim=128)

    model.compile(optimizer=tf.keras.optimizers.Adagrad(learning_rate=0.1))

    # Train
    history = model.fit(
        train_dataset.batch(2048),
        validation_data=test_dataset.batch(2048),
        epochs=epochs
    )

    return model, history
```

## Phase 3: Model Serving Infrastructure

### 3.1 Real-Time Serving with Redis + FastAPI

```python
# serving.py
from fastapi import FastAPI, HTTPException
import redis
import numpy as np
import pickle
from typing import List, Dict

app = FastAPI()

# Redis for caching
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=False)

# Load model embeddings
user_embeddings = load_user_embeddings()
item_embeddings = load_item_embeddings()

@app.get("/recommendations/{user_id}")
async def get_recommendations(
    user_id: str,
    n: int = 20,
    context: Dict = None
):
    """Get real-time recommendations for user"""

    # Check cache first
    cache_key = f"recs:{user_id}:{n}"
    cached = redis_client.get(cache_key)

    if cached:
        return pickle.loads(cached)

    # Get user embedding
    user_embedding = user_embeddings.get(user_id)
    if user_embedding is None:
        # Cold start - use default/popularity
        return await get_cold_start_recommendations(n)

    # Compute similarities with all items
    similarities = compute_similarities(user_embedding, item_embeddings)

    # Get top N
    top_indices = np.argsort(similarities)[-n:][::-1]
    recommendations = [
        {
            "item_id": item_ids[idx],
            "score": float(similarities[idx]),
            "metadata": get_item_metadata(item_ids[idx])
        }
        for idx in top_indices
    ]

    # Apply business rules
    recommendations = apply_business_rules(recommendations, user_id, context)

    # Cache for 1 hour
    redis_client.setex(cache_key, 3600, pickle.dumps(recommendations))

    return {
        "user_id": user_id,
        "recommendations": recommendations,
        "algorithm": "two_tower",
        "cached": False
    }

def compute_similarities(user_embedding, item_embeddings):
    """Compute cosine similarity between user and all items"""

    # Normalize embeddings
    user_norm = user_embedding / np.linalg.norm(user_embedding)
    item_norms = item_embeddings / np.linalg.norm(item_embeddings, axis=1, keepdims=True)

    # Dot product
    similarities = np.dot(item_norms, user_norm)

    return similarities

def apply_business_rules(recommendations, user_id, context):
    """Apply filtering and ranking rules"""

    # Filter out already watched
    watched_items = get_user_watch_history(user_id)
    recommendations = [r for r in recommendations if r['item_id'] not in watched_items]

    # Filter by maturity rating
    user_profile = get_user_profile(user_id)
    max_rating = user_profile.get('max_maturity_rating', 'R')
    recommendations = [
        r for r in recommendations
        if is_rating_appropriate(r['metadata']['rating'], max_rating)
    ]

    # Boost new releases
    for rec in recommendations:
        if rec['metadata']['days_since_release'] < 7:
            rec['score'] *= 1.2

    # Re-sort by adjusted score
    recommendations.sort(key=lambda x: x['score'], reverse=True)

    return recommendations
```

### 3.2 Approximate Nearest Neighbors (ANN) for Scale

```python
# ann_serving.py
import faiss
import numpy as np

class FAISSRecommender:
    def __init__(self, item_embeddings, item_ids):
        self.item_ids = item_ids
        self.embedding_dim = item_embeddings.shape[1]

        # Build FAISS index
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(item_embeddings)
        self.index.add(item_embeddings.astype('float32'))

        print(f"Built FAISS index with {self.index.ntotal} items")

    def recommend(self, user_embedding, k=20):
        """Find k nearest items to user"""

        # Normalize user embedding
        user_embedding = user_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(user_embedding)

        # Search
        scores, indices = self.index.search(user_embedding, k)

        # Map to item IDs
        recommendations = [
            {
                "item_id": self.item_ids[idx],
                "score": float(scores[0][i])
            }
            for i, idx in enumerate(indices[0])
        ]

        return recommendations

    def batch_recommend(self, user_embeddings, k=20):
        """Batch recommendation for multiple users"""

        # Normalize
        faiss.normalize_L2(user_embeddings)

        # Search
        scores, indices = self.index.search(user_embeddings, k)

        return scores, indices
```

## Phase 4: A/B Testing Framework

### 4.1 Experiment Management

```python
# ab_testing.py
import hashlib

class ExperimentManager:
    def __init__(self, config):
        self.experiments = config['experiments']

    def get_variant(self, user_id, experiment_id):
        """Assign user to experiment variant"""

        experiment = self.experiments.get(experiment_id)
        if not experiment or not experiment['active']:
            return 'control'

        # Consistent hashing for stable assignment
        hash_input = f"{user_id}:{experiment_id}:{experiment['salt']}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = hash_value % 100

        # Assign based on traffic allocation
        cumulative = 0
        for variant_name, traffic_percent in experiment['variants'].items():
            cumulative += traffic_percent
            if bucket < cumulative:
                return variant_name

        return 'control'

    def get_recommendations_with_experiment(self, user_id, experiment_id, n=20):
        """Get recommendations for experiment variant"""

        variant = self.get_variant(user_id, experiment_id)

        # Route to appropriate algorithm
        if variant == 'control':
            recs = self.collaborative_filtering(user_id, n)
        elif variant == 'two_tower':
            recs = self.two_tower_model(user_id, n)
        elif variant == 'hybrid':
            recs = self.hybrid_approach(user_id, n)
        else:
            recs = self.collaborative_filtering(user_id, n)

        # Log for analysis
        self.log_impression({
            'user_id': user_id,
            'experiment_id': experiment_id,
            'variant': variant,
            'recommendations': [r['item_id'] for r in recs],
            'timestamp': time.time()
        })

        return recs, variant
```

### 4.2 Metrics Collection

```python
# metrics.py
from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class ExperimentMetrics:
    variant: str
    impressions: int
    clicks: int
    conversions: int
    total_watch_time: float
    unique_users: int

    @property
    def ctr(self):
        return self.clicks / self.impressions if self.impressions > 0 else 0

    @property
    def conversion_rate(self):
        return self.conversions / self.clicks if self.clicks > 0 else 0

    @property
    def avg_watch_time(self):
        return self.total_watch_time / self.conversions if self.conversions > 0 else 0

def calculate_statistical_significance(control_metrics, variant_metrics, alpha=0.05):
    """Perform two-proportion z-test for CTR"""

    p1 = control_metrics.ctr
    p2 = variant_metrics.ctr

    n1 = control_metrics.impressions
    n2 = variant_metrics.impressions

    # Pooled proportion
    p_pool = (control_metrics.clicks + variant_metrics.clicks) / (n1 + n2)

    # Standard error
    se = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))

    # Z-score
    z = (p2 - p1) / se

    # P-value (two-tailed)
    from scipy import stats
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    is_significant = p_value < alpha

    return {
        'z_score': z,
        'p_value': p_value,
        'is_significant': is_significant,
        'lift': (p2 - p1) / p1 if p1 > 0 else 0
    }
```

## Phase 5: Monitoring & Optimization

### 5.1 Model Performance Monitoring

```python
# monitoring.py
from prometheus_client import Counter, Histogram, Gauge

# Metrics
recommendation_requests = Counter(
    'recommendation_requests_total',
    'Total recommendation requests',
    ['variant', 'status']
)

recommendation_latency = Histogram(
    'recommendation_latency_seconds',
    'Recommendation latency',
    ['variant']
)

cache_hit_rate = Gauge(
    'cache_hit_rate',
    'Cache hit rate'
)

model_quality_score = Gauge(
    'model_quality_score',
    'Model quality metric',
    ['metric_type']
)

def monitor_recommendation_request(variant, latency, status):
    """Record recommendation request metrics"""
    recommendation_requests.labels(variant=variant, status=status).inc()
    recommendation_latency.labels(variant=variant).observe(latency)
```

## Best Practices

1. **Start simple**: Begin with collaborative filtering, add complexity as needed
2. **Measure everything**: Instrument code for comprehensive metrics
3. **A/B test changes**: Never deploy algorithm changes without testing
4. **Handle cold start**: Have fallbacks for new users/items
5. **Cache aggressively**: Use Redis/Memcached for hot recommendations
6. **Use ANN for scale**: FAISS/Annoy for sub-millisecond retrieval
7. **Diversify results**: Avoid filter bubbles with diversity constraints
8. **Monitor quality**: Track offline and online metrics continuously
9. **Retrain regularly**: Update models with fresh data (daily/weekly)
10. **Plan for scale**: Design for 10x current traffic from day one

## Performance Targets

- **Latency**: p50 < 50ms, p95 < 100ms, p99 < 200ms
- **Cache hit rate**: > 70% for popular users
- **CTR improvement**: > 10% vs baseline
- **Model refresh**: Daily for fast-moving content
- **Availability**: 99.95% uptime
