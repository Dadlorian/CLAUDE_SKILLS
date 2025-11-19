# Model Serving Guide

A comprehensive guide to deploying and serving machine learning models in production environments with performance optimization, reliability, and scalability patterns.

## Table of Contents

1. [REST API Design for ML](#rest-api-design-for-ml)
2. [gRPC for High-Performance Serving](#grpc-for-high-performance-serving)
3. [Batch Inference Patterns](#batch-inference-patterns)
4. [Real-Time Inference](#real-time-inference)
5. [Streaming Inference](#streaming-inference)
6. [Model Versioning in Production](#model-versioning-in-production)
7. [Request Batching](#request-batching)
8. [Caching Strategies](#caching-strategies)
9. [Performance Optimization](#performance-optimization)
10. [Complete Implementation Examples](#complete-implementation-examples)

---

## REST API Design for ML

### Principles

- **Standardized Endpoints**: `/predict`, `/batch_predict`, `/health`, `/metrics`
- **Stateless Design**: Each request is independent
- **Scalable Architecture**: Horizontal scaling through load balancing
- **Clear Error Handling**: Comprehensive HTTP status codes
- **Request/Response Contracts**: Strict validation and schemas

### Core Endpoints

```
POST /api/v1/predict          - Single prediction
POST /api/v1/batch_predict    - Batch predictions
GET  /api/v1/health           - Health check
GET  /api/v1/metrics          - Prometheus metrics
GET  /api/v1/model/info       - Model metadata
POST /api/v1/model/reload     - Reload model
```

### Request/Response Format

**Single Prediction Request:**
```json
{
  "input_data": [
    {"feature1": 0.5, "feature2": 1.2, "feature3": "category_a"},
    {"feature1": 0.3, "feature2": 2.1, "feature3": "category_b"}
  ],
  "model_version": "v1.2.3",
  "return_explanation": true
}
```

**Response:**
```json
{
  "predictions": [0.95, 0.42],
  "probabilities": [[0.95, 0.05], [0.42, 0.58]],
  "model_version": "v1.2.3",
  "inference_time_ms": 15.3,
  "explanation": [
    {"feature": "feature1", "importance": 0.7},
    {"feature": "feature2", "importance": 0.3}
  ]
}
```

### HTTP Status Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | OK | Successful prediction |
| 400 | Bad Request | Invalid input data |
| 422 | Unprocessable Entity | Schema validation failed |
| 503 | Service Unavailable | Model loading failed |
| 504 | Gateway Timeout | Inference exceeded timeout |

---

## gRPC for High-Performance Serving

### Why gRPC?

- **Binary Protocol**: More efficient than JSON (3-10x faster)
- **Multiplexing**: Multiple concurrent requests on single connection
- **Streaming**: Bidirectional streaming support
- **Low Latency**: Optimized for high-throughput, low-latency scenarios
- **Language Agnostic**: Works across multiple languages

### Protocol Buffer Definition

```protobuf
syntax = "proto3";

package ml_serving;

service PredictionService {
  rpc Predict(PredictRequest) returns (PredictResponse) {}
  rpc BatchPredict(BatchPredictRequest) returns (BatchPredictResponse) {}
  rpc StreamPredict(stream PredictRequest) returns (stream PredictResponse) {}
  rpc GetModelInfo(Empty) returns (ModelInfo) {}
}

message Features {
  map<string, float> numeric_features = 1;
  map<string, string> categorical_features = 2;
}

message PredictRequest {
  Features input = 1;
  string model_version = 2;
  bool return_probabilities = 3;
}

message PredictResponse {
  float prediction = 1;
  repeated float probabilities = 2;
  int64 inference_time_ms = 3;
  string model_version = 4;
}

message BatchPredictRequest {
  repeated Features inputs = 1;
  string model_version = 2;
}

message BatchPredictResponse {
  repeated float predictions = 1;
  int64 total_inference_time_ms = 2;
}

message ModelInfo {
  string version = 1;
  int64 load_timestamp = 2;
  map<string, string> metadata = 3;
}

message Empty {}
```

### gRPC Server Implementation (Python)

```python
import grpc
from concurrent import futures
import ml_serving_pb2
import ml_serving_pb2_grpc
import logging

class PredictionServicer(ml_serving_pb2_grpc.PredictionServiceServicer):
    def __init__(self, model, model_version="v1.0"):
        self.model = model
        self.model_version = model_version
        self.logger = logging.getLogger(__name__)

    def Predict(self, request, context):
        try:
            # Convert protobuf to numpy array
            features = self._parse_features(request.input)

            # Inference
            prediction = self.model.predict(features)

            # Return response
            return ml_serving_pb2.PredictResponse(
                prediction=float(prediction),
                model_version=self.model_version
            )
        except Exception as e:
            self.logger.error(f"Prediction error: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return ml_serving_pb2.PredictResponse()

    def BatchPredict(self, request, context):
        try:
            batch_features = [
                self._parse_features(features)
                for features in request.inputs
            ]

            predictions = self.model.predict_batch(batch_features)

            return ml_serving_pb2.BatchPredictResponse(
                predictions=predictions.tolist()
            )
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return ml_serving_pb2.BatchPredictResponse()

    def StreamPredict(self, request_iterator, context):
        for request in request_iterator:
            features = self._parse_features(request.input)
            prediction = self.model.predict(features)

            yield ml_serving_pb2.PredictResponse(
                prediction=float(prediction),
                model_version=self.model_version
            )

    def GetModelInfo(self, request, context):
        return ml_serving_pb2.ModelInfo(
            version=self.model_version,
            metadata={"model_type": "gradient_boosting"}
        )

    def _parse_features(self, features):
        # Convert protobuf features to numpy array
        numeric = dict(features.numeric_features)
        return numeric

def serve(model, port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ml_serving_pb2_grpc.add_PredictionServiceServicer_to_server(
        PredictionServicer(model), server
    )
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"gRPC server started on port {port}")
    server.wait_for_termination()

if __name__ == "__main__":
    # Load model
    import joblib
    model = joblib.load("model.pkl")
    serve(model)
```

---

## Batch Inference Patterns

### Offline Batch Processing

**Use Case**: Daily predictions on historical data, report generation

```python
import pandas as pd
import numpy as np
from typing import List, Tuple
import logging

class BatchInferenceEngine:
    def __init__(self, model, batch_size=1000, workers=4):
        self.model = model
        self.batch_size = batch_size
        self.workers = workers
        self.logger = logging.getLogger(__name__)

    def process_file(self, input_path: str, output_path: str):
        """Process large CSV file in batches"""
        chunks = pd.read_csv(input_path, chunksize=self.batch_size)
        results = []

        for i, chunk in enumerate(chunks):
            self.logger.info(f"Processing batch {i+1}")

            # Extract features
            X = chunk.drop('target', axis=1)

            # Batch inference
            batch_predictions = self.model.predict(X)

            # Store results
            chunk['prediction'] = batch_predictions
            results.append(chunk)

        # Write results
        output_df = pd.concat(results, ignore_index=True)
        output_df.to_csv(output_path, index=False)
        self.logger.info(f"Batch inference complete. Results saved to {output_path}")

    def process_generator(self, data_generator, callback=None):
        """Process data from generator with callback"""
        batch = []
        indices = []

        for idx, sample in enumerate(data_generator):
            batch.append(sample)
            indices.append(idx)

            if len(batch) == self.batch_size:
                predictions = self.model.predict(np.array(batch))

                if callback:
                    callback(indices, predictions)

                batch = []
                indices = []

        # Process remaining
        if batch:
            predictions = self.model.predict(np.array(batch))
            if callback:
                callback(indices, predictions)
```

### Streaming Batch Processing

```python
from queue import Queue
from threading import Thread
import time

class StreamingBatchProcessor:
    def __init__(self, model, batch_size=100, timeout=5.0):
        self.model = model
        self.batch_size = batch_size
        self.timeout = timeout
        self.queue = Queue()
        self.futures = []

    def submit_request(self, request_id, features):
        """Submit single request"""
        future = {
            'id': request_id,
            'features': features,
            'timestamp': time.time(),
            'result': None,
            'ready': False
        }
        self.queue.put(future)
        self.futures.append(future)
        return request_id

    def get_result(self, request_id, timeout=None):
        """Get result with timeout"""
        start = time.time()
        timeout = timeout or self.timeout

        while time.time() - start < timeout:
            for future in self.futures:
                if future['id'] == request_id and future['ready']:
                    return future['result']
            time.sleep(0.01)

        raise TimeoutError(f"Request {request_id} timeout")

    def worker(self):
        """Background worker for batch processing"""
        batch = []
        batch_futures = []
        last_process_time = time.time()

        while True:
            try:
                # Try to fill batch
                while len(batch) < self.batch_size:
                    timeout = max(0.1, self.timeout - (time.time() - last_process_time))
                    future = self.queue.get(timeout=timeout)
                    batch.append(future['features'])
                    batch_futures.append(future)

                # Process batch
                predictions = self.model.predict(np.array(batch))

                for future, pred in zip(batch_futures, predictions):
                    future['result'] = pred
                    future['ready'] = True

                batch = []
                batch_futures = []
                last_process_time = time.time()

            except:
                # Timeout: process partial batch
                if batch and (time.time() - last_process_time) > self.timeout:
                    predictions = self.model.predict(np.array(batch))

                    for future, pred in zip(batch_futures, predictions):
                        future['result'] = pred
                        future['ready'] = True

                    batch = []
                    batch_futures = []
                    last_process_time = time.time()
```

---

## Real-Time Inference

### Low-Latency Single Prediction

```python
import asyncio
from typing import Dict, Any
import time

class RealtimePredictor:
    def __init__(self, model, max_latency_ms=100):
        self.model = model
        self.max_latency_ms = max_latency_ms

    async def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Predict with latency tracking"""
        start = time.time()

        try:
            # Convert to model input
            X = self._prepare_input(features)

            # Run inference
            prediction = self.model.predict(X)

            latency_ms = (time.time() - start) * 1000

            if latency_ms > self.max_latency_ms:
                print(f"Warning: Latency {latency_ms:.2f}ms exceeds {self.max_latency_ms}ms")

            return {
                'prediction': float(prediction),
                'latency_ms': latency_ms,
                'timestamp': time.time()
            }

        except Exception as e:
            return {
                'error': str(e),
                'latency_ms': (time.time() - start) * 1000
            }

    def _prepare_input(self, features):
        # Feature engineering
        return np.array([[features.get(f, 0.0) for f in self.model.feature_names_]])
```

---

## Streaming Inference

### Continuous Stream Processing

```python
from kafka import KafkaConsumer, KafkaProducer
import json
import time

class StreamingInferenceService:
    def __init__(self, model, kafka_brokers, input_topic, output_topic):
        self.model = model

        self.consumer = KafkaConsumer(
            input_topic,
            bootstrap_servers=kafka_brokers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='inference_service'
        )

        self.producer = KafkaProducer(
            bootstrap_servers=kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        self.output_topic = output_topic

    def process_stream(self):
        """Process continuous stream"""
        for message in self.consumer:
            try:
                # Parse input
                request = message.value
                request_id = request['id']
                features = request['features']

                # Inference
                start = time.time()
                prediction = self.model.predict([list(features.values())])
                latency = (time.time() - start) * 1000

                # Send result
                result = {
                    'request_id': request_id,
                    'prediction': float(prediction[0]),
                    'timestamp': time.time(),
                    'latency_ms': latency
                }

                self.producer.send(self.output_topic, result)

            except Exception as e:
                print(f"Stream processing error: {e}")
```

### Time-Window Aggregation

```python
from collections import deque
import threading

class TimeWindowAggregator:
    def __init__(self, model, window_size_seconds=5, step_size_seconds=1):
        self.model = model
        self.window_size = window_size_seconds
        self.step_size = step_size_seconds
        self.buffer = deque()
        self.lock = threading.Lock()

    def add_sample(self, timestamp, features):
        """Add sample to buffer"""
        with self.lock:
            self.buffer.append((timestamp, features))

    def get_windowed_predictions(self):
        """Get predictions for current window"""
        with self.lock:
            now = time.time()
            cutoff = now - self.window_size

            # Keep only recent samples
            valid_samples = [
                features for ts, features in self.buffer
                if ts > cutoff
            ]

            if not valid_samples:
                return None

            # Batch predict
            X = np.array(valid_samples)
            predictions = self.model.predict(X)

            return {
                'window_start': cutoff,
                'window_end': now,
                'count': len(predictions),
                'predictions': predictions.tolist(),
                'mean_prediction': float(np.mean(predictions)),
                'std_prediction': float(np.std(predictions))
            }
```

---

## Model Versioning in Production

### Version Management System

```python
import json
import os
from datetime import datetime
from pathlib import Path
import hashlib

class ModelVersionManager:
    def __init__(self, model_dir="models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.metadata_file = self.model_dir / "versions.json"

    def register_model(self, model, version: str, metadata: dict = None):
        """Register new model version"""
        version_dir = self.model_dir / version
        version_dir.mkdir(exist_ok=True)

        # Save model
        model_path = version_dir / "model.pkl"
        import joblib
        joblib.dump(model, model_path)

        # Calculate checksum
        checksum = self._calculate_checksum(model_path)

        # Save metadata
        version_info = {
            'version': version,
            'timestamp': datetime.utcnow().isoformat(),
            'checksum': checksum,
            'status': 'inactive',
            'metrics': metadata or {}
        }

        self._update_versions_file(version_info)
        return version_info

    def activate_version(self, version: str):
        """Activate specific model version"""
        versions = self._load_versions()

        # Deactivate current active version
        for v in versions:
            if v['status'] == 'active':
                v['status'] = 'inactive'

        # Activate new version
        for v in versions:
            if v['version'] == version:
                v['status'] = 'active'
                v['activated_at'] = datetime.utcnow().isoformat()

        self._save_versions(versions)

    def get_active_model(self):
        """Load active model version"""
        versions = self._load_versions()

        for v in versions:
            if v['status'] == 'active':
                model_path = self.model_dir / v['version'] / "model.pkl"
                import joblib
                return joblib.load(model_path), v

        raise ValueError("No active model version found")

    def rollback(self, version: str):
        """Rollback to previous version"""
        self.activate_version(version)

    def list_versions(self):
        """List all registered versions"""
        return self._load_versions()

    def _calculate_checksum(self, path):
        """Calculate file checksum"""
        sha256 = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _load_versions(self):
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                return json.load(f)
        return []

    def _save_versions(self, versions):
        with open(self.metadata_file, 'w') as f:
            json.dump(versions, f, indent=2)

    def _update_versions_file(self, version_info):
        versions = self._load_versions()
        versions.append(version_info)
        self._save_versions(versions)


# Usage Example
version_manager = ModelVersionManager()

# Register new model
version_manager.register_model(
    model=trained_model,
    version="v1.2.3",
    metadata={
        'accuracy': 0.95,
        'f1_score': 0.92,
        'training_date': '2024-01-15'
    }
)

# Activate it
version_manager.activate_version("v1.2.3")

# Later, load active model
active_model, version_info = version_manager.get_active_model()
```

---

## Request Batching

### Dynamic Batch Accumulator

```python
import threading
import queue
from typing import List, Tuple
import numpy as np
import time

class DynamicBatcher:
    def __init__(self, model, batch_size=32, wait_time_ms=50):
        self.model = model
        self.batch_size = batch_size
        self.wait_time_ms = wait_time_ms / 1000  # Convert to seconds

        self.input_queue = queue.Queue()
        self.output_dict = {}
        self.output_lock = threading.Lock()

        self.worker_thread = threading.Thread(target=self._batch_worker, daemon=True)
        self.worker_thread.start()

    def predict(self, request_id: str, features: np.ndarray) -> float:
        """Submit request and wait for prediction"""
        # Submit to queue
        self.input_queue.put((request_id, features))

        # Wait for result
        timeout = (self.batch_size * self.wait_time_ms) + 1.0
        start = time.time()

        while time.time() - start < timeout:
            with self.output_lock:
                if request_id in self.output_dict:
                    return self.output_dict.pop(request_id)

            time.sleep(0.001)

        raise TimeoutError(f"Request {request_id} timeout")

    def _batch_worker(self):
        """Background worker that accumulates and processes batches"""
        batch_ids = []
        batch_features = []
        last_process_time = time.time()

        while True:
            try:
                # Try to get next item with timeout
                timeout = max(0.001, self.wait_time_ms - (time.time() - last_process_time))
                request_id, features = self.input_queue.get(timeout=timeout)

                batch_ids.append(request_id)
                batch_features.append(features)

                # Process when batch is full
                if len(batch_ids) >= self.batch_size:
                    self._process_batch(batch_ids, batch_features)
                    batch_ids = []
                    batch_features = []
                    last_process_time = time.time()

            except queue.Empty:
                # Timeout: process partial batch if available
                if batch_ids and (time.time() - last_process_time) >= self.wait_time_ms:
                    self._process_batch(batch_ids, batch_features)
                    batch_ids = []
                    batch_features = []
                    last_process_time = time.time()

    def _process_batch(self, ids: List[str], features: List[np.ndarray]):
        """Process accumulated batch"""
        X = np.array(features)
        predictions = self.model.predict(X)

        with self.output_lock:
            for request_id, pred in zip(ids, predictions):
                self.output_dict[request_id] = float(pred)
```

---

## Caching Strategies

### Multi-Level Cache

```python
import hashlib
import json
from functools import lru_cache
import redis
import pickle
from typing import Any, Dict

class MultiLevelCache:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.memory_cache = {}
        self.memory_cache_size = 10000

        # Redis cache
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=False
        )

        self.cache_ttl = 3600  # 1 hour

    def get_or_predict(self, model, features: Dict) -> Any:
        """Get cached prediction or compute"""
        cache_key = self._hash_features(features)

        # Level 1: Memory cache
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]['prediction']

        # Level 2: Redis cache
        cached = self.redis_client.get(cache_key)
        if cached:
            prediction = pickle.loads(cached)
            self.memory_cache[cache_key] = {
                'prediction': prediction,
                'source': 'redis'
            }
            return prediction

        # Level 3: Compute
        X = self._prepare_features(features)
        prediction = model.predict(X)[0]

        # Store in caches
        self._store_in_cache(cache_key, prediction)

        return prediction

    def _hash_features(self, features: Dict) -> str:
        """Generate cache key"""
        feature_str = json.dumps(features, sort_keys=True)
        return hashlib.sha256(feature_str.encode()).hexdigest()

    def _prepare_features(self, features):
        import numpy as np
        return np.array([[v for v in features.values()]])

    def _store_in_cache(self, key: str, prediction: Any):
        """Store in both levels"""
        # Memory cache
        if len(self.memory_cache) < self.memory_cache_size:
            self.memory_cache[key] = {
                'prediction': prediction,
                'source': 'memory'
            }

        # Redis cache
        self.redis_client.setex(
            key,
            self.cache_ttl,
            pickle.dumps(prediction)
        )


# Feature-based caching
class FeatureBatchCache:
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = ttl_seconds

    def invalidate_if_feature_changed(self, feature_name: str):
        """Invalidate cache when feature changes"""
        self.cache = {
            k: v for k, v in self.cache.items()
            if feature_name not in k
        }

    def cache_batch_predictions(self, feature_hash: str, predictions: List):
        """Cache batch predictions"""
        self.cache[feature_hash] = {
            'predictions': predictions,
            'timestamp': time.time()
        }

    def get_cached_batch(self, feature_hash: str):
        """Retrieve cached batch"""
        if feature_hash in self.cache:
            entry = self.cache[feature_hash]
            if (time.time() - entry['timestamp']) < self.ttl:
                return entry['predictions']
            else:
                del self.cache[feature_hash]
        return None
```

---

## Performance Optimization

### Model Optimization Techniques

```python
import numpy as np
from typing import Callable
import time

class ModelOptimizer:
    """Various model optimization techniques"""

    @staticmethod
    def quantize_model(model, data_sample, bits=8):
        """Quantize model to lower precision"""
        # Get model weights
        import joblib

        # Find min/max
        weights = model.get_weights() if hasattr(model, 'get_weights') else None

        # Simple linear quantization
        quantized = {}
        for name, weight in weights.items():
            min_val = np.min(weight)
            max_val = np.max(weight)

            # Quantize to 8-bit
            scale = (max_val - min_val) / (2 ** bits - 1)
            quantized[name] = {
                'data': ((weight - min_val) / scale).astype(np.uint8),
                'scale': scale,
                'min': min_val
            }

        return quantized

    @staticmethod
    def profile_inference(model, data: np.ndarray, iterations=100):
        """Profile model inference performance"""
        times = []

        for _ in range(iterations):
            start = time.time()
            _ = model.predict(data)
            times.append((time.time() - start) * 1000)

        return {
            'mean_ms': np.mean(times),
            'median_ms': np.median(times),
            'p95_ms': np.percentile(times, 95),
            'p99_ms': np.percentile(times, 99),
            'min_ms': np.min(times),
            'max_ms': np.max(times)
        }

    @staticmethod
    def optimize_batch_size(model, data: np.ndarray, max_batch=512):
        """Find optimal batch size"""
        results = {}

        for batch_size in [1, 4, 8, 16, 32, 64, 128, 256, 512]:
            if batch_size > len(data):
                break

            start = time.time()
            _ = model.predict(data[:batch_size])
            latency = (time.time() - start) * 1000

            throughput = batch_size / (latency / 1000)
            results[batch_size] = {
                'latency_ms': latency,
                'throughput_samples_per_sec': throughput
            }

        # Find optimal
        optimal_batch = max(results.items(),
                          key=lambda x: x[1]['throughput_samples_per_sec'])

        return results, optimal_batch[0]


# GPU-aware inference
class GPUInferenceOptimizer:
    def __init__(self, model, device='cuda:0'):
        self.model = model
        self.device = device

    def batch_to_device(self, batch, device):
        """Move batch to device"""
        import torch
        if isinstance(batch, torch.Tensor):
            return batch.to(device)
        elif isinstance(batch, dict):
            return {k: self._to_device(v, device) for k, v in batch.items()}
        else:
            return batch

    def optimize_memory(self):
        """Optimize GPU memory usage"""
        import torch
        torch.cuda.empty_cache()

        # Set to eval mode
        if hasattr(self.model, 'eval'):
            self.model.eval()

        # Disable gradients
        import torch.no_grad
        return torch.no_grad()
```

---

## Complete Implementation Examples

### Example 1: Production FastAPI Service

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, validator
from typing import List, Optional
import numpy as np
import joblib
import logging
from datetime import datetime
import asyncio
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for validation
class PredictionRequest(BaseModel):
    features: dict
    model_version: Optional[str] = None
    request_id: Optional[str] = None

    @validator('features')
    def features_not_empty(cls, v):
        if not v:
            raise ValueError('features cannot be empty')
        return v

class BatchPredictionRequest(BaseModel):
    instances: List[dict]
    model_version: Optional[str] = None

class PredictionResponse(BaseModel):
    request_id: str
    prediction: float
    probability: Optional[List[float]] = None
    model_version: str
    inference_time_ms: float
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    model_version: str
    uptime_seconds: float

# Initialize FastAPI app
app = FastAPI(title="ML Model Server", version="1.0.0")

# Global state
class ModelServer:
    def __init__(self):
        self.model = None
        self.model_version = "v1.0.0"
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0

    async def load_model(self):
        """Load model from disk"""
        try:
            self.model = joblib.load("model.pkl")
            logger.info(f"Model loaded: {self.model_version}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

server = ModelServer()

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    await server.load_model()
    logger.info("Server started")

@app.on_event("shutdown")
async def shutdown():
    logger.info(f"Server shutting down. Total requests: {server.request_count}")

# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - server.start_time
    return HealthResponse(
        status="healthy",
        model_version=server.model_version,
        uptime_seconds=uptime
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Single prediction endpoint"""
    server.request_count += 1

    try:
        start = time.time()

        # Prepare features
        feature_array = np.array([[request.features.get(f, 0.0)
                                   for f in sorted(request.features.keys())]])

        # Run inference
        prediction = server.model.predict(feature_array)[0]

        # Get probability if available
        probability = None
        if hasattr(server.model, 'predict_proba'):
            probability = server.model.predict_proba(feature_array)[0].tolist()

        latency_ms = (time.time() - start) * 1000

        return PredictionResponse(
            request_id=request.request_id or str(server.request_count),
            prediction=float(prediction),
            probability=probability,
            model_version=server.model_version,
            inference_time_ms=latency_ms,
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        server.error_count += 1
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch_predict")
async def batch_predict(request: BatchPredictionRequest):
    """Batch prediction endpoint"""
    server.request_count += 1

    try:
        start = time.time()

        # Prepare features
        X = np.array([
            [inst.get(f, 0.0) for f in sorted(inst.keys())]
            for inst in request.instances
        ])

        # Batch inference
        predictions = server.model.predict(X)

        latency_ms = (time.time() - start) * 1000

        return {
            "predictions": predictions.tolist(),
            "count": len(predictions),
            "model_version": server.model_version,
            "inference_time_ms": latency_ms,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        server.error_count += 1
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """Prometheus-style metrics"""
    uptime = time.time() - server.start_time

    return {
        "requests_total": server.request_count,
        "errors_total": server.error_count,
        "uptime_seconds": uptime,
        "error_rate": server.error_count / max(server.request_count, 1)
    }

# Run with: uvicorn module_name:app --host 0.0.0.0 --port 8000 --workers 4
```

### Example 2: Complete gRPC Service with Load Balancing

```python
# model_serving_pb2.py already defined above

import grpc
from concurrent import futures
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedPredictionServicer(ml_serving_pb2_grpc.PredictionServiceServicer):
    def __init__(self, model, model_version="v1.0", enable_batching=True):
        self.model = model
        self.model_version = model_version
        self.enable_batching = enable_batching

        if enable_batching:
            self.batcher = DynamicBatcher(self.model, batch_size=32)

    def Predict(self, request, context):
        try:
            # Parse features
            features = dict(request.input.numeric_features)

            if self.enable_batching:
                # Use dynamic batcher
                import uuid
                request_id = str(uuid.uuid4())
                features_array = np.array([list(features.values())])
                prediction = self.batcher.predict(request_id, features_array[0])
            else:
                # Direct inference
                features_array = np.array([list(features.values())])
                prediction = self.model.predict(features_array)[0]

            return ml_serving_pb2.PredictResponse(
                prediction=float(prediction),
                model_version=self.model_version
            )
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return ml_serving_pb2.PredictResponse()

    def BatchPredict(self, request, context):
        try:
            features_list = [
                np.array(list(f.numeric_features.values()))
                for f in request.inputs
            ]
            X = np.array(features_list)
            predictions = self.model.predict(X)

            return ml_serving_pb2.BatchPredictResponse(
                predictions=predictions.tolist()
            )
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return ml_serving_pb2.BatchPredictResponse()

def serve_with_load_balancing(models_dict, port=50051):
    """Serve with multiple replicas for load balancing"""
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=20),
        options=[
            ('grpc.max_send_message_length', 100 * 1024 * 1024),
            ('grpc.max_receive_message_length', 100 * 1024 * 1024),
        ]
    )

    # Add servicer
    servicer = OptimizedPredictionServicer(
        models_dict['primary'],
        enable_batching=True
    )

    ml_serving_pb2_grpc.add_PredictionServiceServicer_to_server(
        servicer, server
    )

    server.add_insecure_port(f'[::]:{port}')
    server.start()

    logger.info(f"gRPC server started on port {port}")
    server.wait_for_termination()

# Client example
class PredictionClient:
    def __init__(self, server_address='localhost:50051'):
        self.channel = grpc.aio.secure_channel(server_address)
        self.stub = ml_serving_pb2_grpc.PredictionServiceStub(self.channel)

    async def predict(self, features: dict):
        request = ml_serving_pb2.PredictRequest(
            input=ml_serving_pb2.Features(
                numeric_features=features
            )
        )
        response = await self.stub.Predict(request)
        return response.prediction

    async def batch_predict(self, batch):
        requests = [
            ml_serving_pb2.Features(numeric_features=f)
            for f in batch
        ]
        request = ml_serving_pb2.BatchPredictRequest(inputs=requests)
        response = await self.stub.BatchPredict(request)
        return response.predictions
```

### Example 3: Kubernetes Deployment Configuration

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-server
  labels:
    app: ml-model-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-model-server
  template:
    metadata:
      labels:
        app: ml-model-server
    spec:
      containers:
      - name: ml-server
        image: ml-model-server:latest
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 50051
          name: grpc
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
            nvidia.com/gpu: "1"
          limits:
            memory: "1Gi"
            cpu: "1000m"
            nvidia.com/gpu: "1"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        env:
        - name: MODEL_VERSION
          value: "v1.2.3"
        - name: BATCH_SIZE
          value: "32"
        - name: CACHE_ENABLED
          value: "true"

---
apiVersion: v1
kind: Service
metadata:
  name: ml-model-server
spec:
  selector:
    app: ml-model-server
  ports:
  - port: 8000
    targetPort: 8000
    name: http
  - port: 50051
    targetPort: 50051
    name: grpc
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-model-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-model-server
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Best Practices Summary

### Architecture

| Pattern | Recommended | Rationale |
|---------|-------------|-----------|
| REST API | Microservices, Low-frequency queries | Standard, easy debugging |
| gRPC | High-frequency, Low-latency needs | 3-10x performance improvement |
| Batch Processing | Offline jobs, Reports | High throughput |
| Streaming | Real-time events, Continuous data | Low latency, Event-driven |

### Optimization Checklist

- [ ] Use dynamic batching for 50% latency reduction
- [ ] Implement multi-level caching (memory + Redis)
- [ ] Profile inference latency at various batch sizes
- [ ] Monitor model serving metrics (p95, p99 latencies)
- [ ] Version all models with checksums
- [ ] Set up health checks and readiness probes
- [ ] Use GPU acceleration for heavy compute
- [ ] Implement request timeouts
- [ ] Enable async processing where possible
- [ ] Set up automated rollback on errors

### Deployment Checklist

- [ ] Containerize model service
- [ ] Define resource requests/limits
- [ ] Implement liveness/readiness probes
- [ ] Set up monitoring and alerting
- [ ] Use horizontal pod autoscaling
- [ ] Implement graceful shutdown
- [ ] Use load balancing for multiple replicas
- [ ] Version control models with metadata
- [ ] Document API contracts
- [ ] Test performance under load

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [gRPC Python Guide](https://grpc.io/docs/languages/python/)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)
- [Redis for Caching](https://redis.io/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/)
- [NVIDIA TensorRT](https://docs.nvidia.com/deeplearning/tensorrt/)
