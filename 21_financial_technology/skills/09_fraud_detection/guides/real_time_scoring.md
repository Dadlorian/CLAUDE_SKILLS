# Real-Time Fraud Scoring Guide

## Architecture for Real-Time Scoring

### System Components
```
Transaction
    ↓
Feature Store (Retrieve cached features)
    ↓
Rules Engine (10-20ms)
    ↓
ML Model Server (30-50ms)
    ↓
Score Aggregation (5ms)
    ↓
Decision Logic (5ms)
    ↓
Response (Block/Verify/Allow)

Target Total: < 100ms (P99)
```

## Feature Store Design

### Feature Categories

**Real-Time Features** (< 1 second latency)
```
- Current transaction details
- Current velocity counts
- Recent device activity
- Recent user activity
- Real-time network updates
```

**Cached Features** (Updated hourly/daily)
```
- Customer baseline statistics
- Device reputation
- Device history
- Card history
- Network graph
```

**Pre-Computed Features** (Batch, updated daily)
```
- RFM analysis
- Customer risk profile
- Device risk scoring
- Merchant risk scoring
```

### Feature Store Implementation
```python
import redis

class FeatureStore:
    def __init__(self, redis_client):
        self.redis = redis_client

    def get_customer_features(self, customer_id):
        # Try cache first
        cached = self.redis.get(f"customer:{customer_id}")
        if cached:
            return json.loads(cached)

        # Fetch from database if not cached
        features = self.fetch_from_db(customer_id)

        # Cache for 1 hour
        self.redis.setex(
            f"customer:{customer_id}",
            3600,
            json.dumps(features)
        )

        return features

    def get_velocity_features(self, customer_id):
        # Real-time calculation
        count_1h = self.redis.incr(f"velocity_1h:{customer_id}")
        count_1d = self.redis.incr(f"velocity_1d:{customer_id}")

        # Set expiration
        self.redis.expire(f"velocity_1h:{customer_id}", 3600)
        self.redis.expire(f"velocity_1d:{customer_id}", 86400)

        return {'count_1h': count_1h, 'count_1d': count_1d}
```

## Real-Time Scoring API

### FastAPI Implementation
```python
from fastapi import FastAPI
import joblib
import numpy as np
from typing import Dict

app = FastAPI()

# Load model at startup
model = joblib.load('fraud_model.pkl')
feature_store = FeatureStore(redis_client)

@app.post('/score')
async def score_transaction(transaction: Dict):
    """
    Score transaction for fraud risk
    """
    # 1. Extract transaction info
    customer_id = transaction['customer_id']
    amount = transaction['amount']
    merchant = transaction['merchant']

    # 2. Get features (target: 20ms)
    with timer() as t:
        features = extract_features(
            transaction,
            feature_store
        )
    logging.info(f"Feature extraction: {t.elapsed}ms")

    # 3. Run through rules (target: 15ms)
    with timer() as t:
        rules_score = rules_engine.score(features)
    logging.info(f"Rules scoring: {t.elapsed}ms")

    # 4. ML model scoring (target: 40ms)
    with timer() as t:
        features_array = np.array([features])
        ml_score = model.predict_proba(features_array)[0][1]
    logging.info(f"ML scoring: {t.elapsed}ms")

    # 5. Behavioral scoring (target: 15ms)
    with timer() as t:
        behavioral_score = behavioral_analyzer.score(customer_id, features)
    logging.info(f"Behavioral scoring: {t.elapsed}ms")

    # 6. Combine scores (target: 5ms)
    with timer() as t:
        final_score = combine_scores(
            rules_score=rules_score,
            ml_score=ml_score,
            behavioral_score=behavioral_score,
            weights={
                'rules': 0.25,
                'ml': 0.35,
                'behavioral': 0.25,
                'network': 0.15
            }
        )
    logging.info(f"Score combination: {t.elapsed}ms")

    # 7. Determine action (target: 5ms)
    action = determine_action(final_score)

    # 8. Log transaction (async, non-blocking)
    log_transaction_async(transaction, final_score, action)

    return {
        'transaction_id': transaction['id'],
        'fraud_score': final_score,
        'action': action,
        'timestamp': datetime.now().isoformat()
    }

# Async logging to avoid latency impact
async def log_transaction_async(transaction, score, action):
    # Queue for async processing
    logging_queue.put((transaction, score, action))
```

## Model Serving

### In-Memory Model Loading
```python
import joblib
from threading import Lock

class ModelServer:
    def __init__(self):
        self.model = None
        self.lock = Lock()
        self.load_model()

    def load_model(self):
        """Load model once at startup"""
        with self.lock:
            self.model = joblib.load('fraud_model.pkl')
            self.feature_names = self.model.feature_names_
            logging.info("Model loaded into memory")

    def predict(self, features_dict):
        """
        Quick prediction with loaded model
        """
        # Convert dict to feature array
        features_array = np.array([
            [features_dict[f] for f in self.feature_names]
        ])

        # Predict
        prediction = self.model.predict_proba(features_array)[0][1]

        return prediction

    def update_model(self, new_model_path):
        """Update model without downtime"""
        with self.lock:
            # Load new model in background
            new_model = joblib.load(new_model_path)

            # Atomic swap
            self.model = new_model
            logging.info("Model updated successfully")
```

### Batch Prediction for Async Cases
```python
from concurrent.futures import ThreadPoolExecutor

class BatchScorer:
    def __init__(self, batch_size=1000):
        self.batch_size = batch_size
        self.queue = []
        self.executor = ThreadPoolExecutor(max_workers=4)

    def score_async(self, transaction):
        """Queue transaction for batch scoring"""
        self.queue.append(transaction)

        if len(self.queue) >= self.batch_size:
            self.process_batch()

        return {'status': 'queued'}

    def process_batch(self):
        """Process batch of queued transactions"""
        if not self.queue:
            return

        batch = self.queue[:self.batch_size]
        self.queue = self.queue[self.batch_size:]

        # Submit for background processing
        self.executor.submit(self._score_batch, batch)

    def _score_batch(self, batch):
        """Actually score the batch"""
        scores = model.predict_proba(batch)
        # Store results in database
        for transaction, score in zip(batch, scores):
            store_score(transaction['id'], score)
```

## Optimization Techniques

### Score Caching
```python
import hashlib
from functools import lru_cache

class ScoreCache:
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = ttl_seconds
        self.timestamps = {}

    def get_cached_score(self, feature_hash):
        """Get score if cached and valid"""
        if feature_hash in self.cache:
            age = time.time() - self.timestamps[feature_hash]
            if age < self.ttl:
                return self.cache[feature_hash]
            else:
                # Expired
                del self.cache[feature_hash]
                del self.timestamps[feature_hash]

        return None

    def cache_score(self, features, score):
        """Cache calculated score"""
        feature_hash = hashlib.md5(
            json.dumps(features, sort_keys=True).encode()
        ).hexdigest()

        self.cache[feature_hash] = score
        self.timestamps[feature_hash] = time.time()

        return feature_hash

    def get_or_score(self, features, score_fn):
        """Unified get or score logic"""
        feature_hash = hashlib.md5(
            json.dumps(features, sort_keys=True).encode()
        ).hexdigest()

        # Try cache
        cached = self.get_cached_score(feature_hash)
        if cached is not None:
            return cached

        # Compute
        score = score_fn(features)

        # Cache
        self.cache_score(features, score)

        return score
```

### Query Optimization
```python
# Use indexes on frequently queried columns
# Index on: customer_id, timestamp, device_id

# Batch retrieve operations
def get_multiple_features(customer_ids):
    """Retrieve features for multiple customers at once"""
    # Use Redis pipeline for atomic retrieval
    pipe = redis.pipeline()
    for cid in customer_ids:
        pipe.get(f"customer:{cid}")

    results = pipe.execute()
    return [json.loads(r) for r in results if r]

# Denormalize data for fast access
# Keep precomputed stats (mean, std dev) in cache
# Update once per day, not per transaction
```

### Model Compression
```python
# Use ONNX format for faster inference
import onnxruntime as ort

def create_onnx_session():
    sess = ort.InferenceSession('model.onnx')
    return sess

def score_with_onnx(session, features):
    # ONNX is ~2x faster than sklearn
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    result = session.run(
        [output_name],
        {input_name: features.astype('float32')}
    )

    return result[0][0][1]  # Fraud probability
```

## Monitoring Real-Time Performance

### Latency Tracking
```python
import time
from collections import defaultdict

class LatencyMonitor:
    def __init__(self):
        self.latencies = defaultdict(list)

    def record(self, component, latency_ms):
        self.latencies[component].append(latency_ms)

    def get_percentiles(self):
        """Get P50, P95, P99 latencies"""
        results = {}
        for component, latencies in self.latencies.items():
            sorted_latencies = sorted(latencies)
            n = len(sorted_latencies)

            results[component] = {
                'p50': sorted_latencies[int(n * 0.5)],
                'p95': sorted_latencies[int(n * 0.95)],
                'p99': sorted_latencies[int(n * 0.99)],
                'avg': np.mean(latencies)
            }

        return results

# Usage in scoring
monitor = LatencyMonitor()

start = time.time()
features = extract_features(transaction)
monitor.record('features', (time.time() - start) * 1000)

start = time.time()
score = model.predict(features)
monitor.record('model', (time.time() - start) * 1000)

# Print stats every minute
every_minute = schedule_periodic(lambda: print(monitor.get_percentiles()), 60)
```

### Throughput Monitoring
```python
import threading

class ThroughputMonitor:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()
        self.start_time = time.time()

    def record(self):
        with self.lock:
            self.count += 1

    def get_tps(self):
        with self.lock:
            elapsed = time.time() - self.start_time
            return self.count / elapsed if elapsed > 0 else 0

    def reset(self):
        with self.lock:
            self.count = 0
            self.start_time = time.time()

# Usage
monitor = ThroughputMonitor()

@app.post('/score')
async def score(transaction):
    # ... scoring logic ...
    monitor.record()
    return result
```

## Handling Failures & Fallbacks

### Graceful Degradation
```python
def score_transaction_with_fallback(transaction):
    try:
        # Try full scoring
        return full_scoring(transaction)
    except TimeoutError:
        # Fall back to rules only
        return rules_only_scoring(transaction)
    except ModelError:
        # Fall back to basic checks
        return basic_checks(transaction)
    except:
        # Last resort: allow transaction
        return 0.1  # Low fraud score

def full_scoring(transaction):
    """Complete ML + rules + behavioral scoring"""
    # ... full logic ...

def rules_only_scoring(transaction):
    """Just rules, no ML"""
    return rules_engine.score(transaction)

def basic_checks(transaction):
    """Minimal checks"""
    if transaction['amount'] > 10000:
        return 0.7
    return 0.2
```

### Circuit Breaker Pattern
```python
from datetime import datetime, timedelta

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout_seconds=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout_seconds
        self.failures = 0
        self.last_failure = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    def call(self, fn, *args, **kwargs):
        if self.state == 'OPEN':
            if self.is_timeout_expired():
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = fn(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e

    def on_success(self):
        self.failures = 0
        self.state = 'CLOSED'

    def on_failure(self):
        self.failures += 1
        self.last_failure = datetime.now()

        if self.failures >= self.failure_threshold:
            self.state = 'OPEN'

    def is_timeout_expired(self):
        return (
            datetime.now() - self.last_failure
        ).total_seconds() > self.timeout

# Usage
breaker = CircuitBreaker()

try:
    score = breaker.call(model.predict, features)
except:
    score = fallback_score()
```

## Best Practices

1. **Latency Budget**
   - Features: 20ms
   - Rules: 15ms
   - Model: 40ms
   - Decision: 5ms
   - Logging: Async

2. **Caching Strategy**
   - Customer data: 1 hour
   - Velocity: Real-time
   - Model: In-memory
   - Results: 5 minutes

3. **Fallbacks**
   - Service down: Use rules
   - Model error: Use rules
   - Timeout: Allow transaction
   - Complete failure: Whitelist

4. **Monitoring**
   - P99 latency alert: > 150ms
   - Throughput alert: < 8000 TPS
   - Error rate alert: > 1%
   - Model staleness: > 30 days

5. **Performance Testing**
   - Load testing: 20,000 TPS
   - Latency: P99 < 100ms
   - Failover: < 1 second
   - Recovery: Automatic
