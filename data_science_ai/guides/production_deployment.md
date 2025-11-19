# Production Deployment Guide for ML & Data Science Models

A comprehensive guide to deploying machine learning models in production environments with production-grade infrastructure patterns, containerization strategies, and operational best practices.

---

## Table of Contents

1. [Model Serving Options](#model-serving-options)
2. [Containerization with Docker](#containerization-with-docker)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [API Design for ML Services](#api-design-for-ml-services)
5. [Load Balancing and Autoscaling](#load-balancing-and-autoscaling)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [A/B Testing](#ab-testing)
8. [Canary Deployments](#canary-deployments)
9. [Complete Deployment Examples](#complete-deployment-examples)
10. [Best Practices](#best-practices)

---

## Model Serving Options

### Overview

Model serving frameworks handle the complexities of production ML inference, including model loading, batching, versioning, and scaling.

### 1. TorchServe

**Description:** Official model serving framework for PyTorch models.

**Pros:**
- Native PyTorch integration
- Built-in model versioning
- Excellent batch processing
- Multi-worker support

**Cons:**
- PyTorch-only
- Steeper learning curve
- Java-based (slower startup)

**Configuration Example:**

```yaml
# torchserve_config.properties
inference_address=http://0.0.0.0:8080
management_address=http://0.0.0.0:8081
metrics_address=http://0.0.0.0:8082
ncs=true
number_of_gpu=1
batch_size=32
max_batch_delay=10
models=resnet18=resnet18.mar,bert=bert.mar
default_response_timeout=120
unregister_model_timeout=120
```

**Model Handler Example:**

```python
# model_handler.py
import torch
import torch.nn.functional as F
from ts.torch_handler.base_handler import BaseHandler

class ModelHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def initialize(self, context):
        properties = context.system_properties
        model_dir = properties.get("model_dir")
        self.model = torch.jit.load(f"{model_dir}/model.pt")
        self.model.to(self.device)
        self.model.eval()

    def preprocess(self, data):
        images = []
        for req in data:
            image = req.get("data") or req.get("body")
            image = torch.tensor(image, dtype=torch.float32)
            images.append(image)
        return torch.stack(images)

    def inference(self, data):
        with torch.no_grad():
            predictions = self.model(data)
        return predictions

    def postprocess(self, inference_output):
        predictions = F.softmax(inference_output, dim=1)
        return predictions.tolist()
```

**Deployment:**

```bash
# Archive model
torch-model-archiver \
  --model-name resnet18 \
  --version 1.0 \
  --model-file model.py \
  --serialized-file model.pt \
  --handler model_handler.py \
  --export-path model_store

# Start TorchServe
torchserve --start --model-store model_store --models resnet18=resnet18.mar
```

### 2. TensorFlow Serving

**Description:** Flexible, high-performance ML serving system from Google.

**Pros:**
- Excellent for TensorFlow/Keras
- Multi-model serving
- Batching and request optimization
- Production-hardened at Google scale

**Cons:**
- TensorFlow-specific
- Complex configuration
- Higher memory footprint

**Configuration Example:**

```proto
# models.config
model_config_list {
  config {
    name: "model_name"
    base_path: "/models/model_name"
    model_platform: "tensorflow"
    model_version_policy {
      all {}
    }
  }
}
```

**Docker Deployment:**

```dockerfile
FROM tensorflow/serving:latest-gpu

COPY models /models
COPY models.config /models/models.config

ENV MODEL_NAME=model_name
EXPOSE 8500 8501

ENTRYPOINT ["tensorflow_model_server"]
CMD ["--port=8500", \
     "--rest_api_port=8501", \
     "--model_config_file=/models/models.config", \
     "--file_system_poll_wait_seconds=30"]
```

**Client Example:**

```python
# client.py
import requests
import json

def predict(instance):
    server_url = "http://localhost:8501/v1/models/model_name:predict"

    request_data = {
        "instances": [instance]
    }

    response = requests.post(server_url, json=request_data)
    return response.json()

# Usage
prediction = predict([[1.0, 2.0, 3.0]])
print(prediction)
```

### 3. Triton Inference Server

**Description:** Multi-framework inference server optimized for GPU acceleration.

**Pros:**
- Multi-framework support (TF, PyTorch, ONNX, etc.)
- Advanced batching strategies
- Ensemble model support
- Exceptional performance

**Cons:**
- Steep learning curve
- Complex model configuration

**Configuration Example:**

```
models/
├── model1/
│   ├── config.pbtxt
│   └── 1/
│       └── model.pt
└── model2/
    ├── config.pbtxt
    └── 1/
        └── model.onnx
```

```proto
# config.pbtxt
name: "pytorch_model"
platform: "pytorch_libtorch"
max_batch_size: 128
input [
  {
    name: "input__0"
    data_type: TYPE_FP32
    dims: [ 3, 224, 224 ]
  }
]
output [
  {
    name: "output__0"
    data_type: TYPE_FP32
    dims: [ 1000 ]
  }
]
instance_group [
  {
    kind: KIND_GPU
    gpus: [ 0 ]
    count: 2
  }
]
```

**Docker Deployment:**

```dockerfile
FROM nvcr.io/nvidia/tritonserver:latest

COPY models /models

ENTRYPOINT ["tritonserver", "--model-repository=/models"]
```

### 4. BentoML

**Description:** Python-first framework for model serving with built-in REST/gRPC APIs.

**Pros:**
- Pythonic and easy to use
- Multi-framework support
- Built-in model management
- Great for data scientists

**Cons:**
- Emerging ecosystem
- Smaller community than alternatives
- Can be slower than specialized servers

**Example:**

```python
# service.py
import bentoml
import numpy as np
from transformers import pipeline

# Load and tag model
classifier = pipeline("sentiment-analysis")
bentoml.transformers.save_model("sentiment_classifier", classifier)

# Create service
@bentoml.service
class SentimentAnalysisService:
    model_ref = bentoml.models.get("sentiment_classifier:latest")

    def __init__(self):
        self.model = bentoml.transformers.load_model(self.model_ref)

    @bentoml.api
    def predict(self, text: str) -> dict:
        result = self.model(text)
        return {"sentiment": result[0]["label"], "score": result[0]["score"]}

# Async endpoint for high throughput
@bentoml.service
class AsyncSentimentService:
    @bentoml.api(batchable=True)
    async def batch_predict(self, texts: list[str]) -> list[dict]:
        results = []
        for text in texts:
            result = classifier(text)
            results.append(result[0])
        return results
```

**Deployment:**

```bash
# Build Bento
bentoml build

# Deploy locally
bentoml serve sentiment_classifier_service:latest --port 8000

# Deploy to container
bentoml containerize sentiment_classifier_service:latest
docker run -p 8000:8000 sentiment_classifier_service:latest
```

### Comparison Table

| Feature | TorchServe | TF Serving | Triton | BentoML |
|---------|-----------|-----------|--------|---------|
| Framework Support | PyTorch | TensorFlow | Multi | Multi |
| Learning Curve | Medium | Hard | Hard | Easy |
| Performance | Good | Very Good | Excellent | Good |
| Batching | Native | Excellent | Advanced | Native |
| Model Versioning | Yes | Yes | Limited | Yes |
| REST/gRPC | Yes/No | Yes/Yes | Yes/Yes | Yes/Yes |
| Production Ready | Yes | Yes | Yes | Emerging |

---

## Containerization with Docker

### Production Docker Strategy

Build optimized, secure, and minimal images for production deployments.

### Multi-Stage Build

```dockerfile
# Dockerfile (Production-Grade)

# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create wheels for all dependencies
RUN pip install --wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install wheels
RUN pip install --no-cache /wheels/*

# Create non-root user
RUN useradd -m -u 1000 mluser

# Copy application
COPY --chown=mluser:mluser . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Switch to non-root user
USER mluser

EXPOSE 8000

# Use exec form to ensure proper signal handling
ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### GPU-Optimized Dockerfile

```dockerfile
# Dockerfile.gpu

# NVIDIA CUDA base image
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

WORKDIR /app

# Install Python and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3.10-dev \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch with CUDA support
RUN pip install --no-cache-dir \
    torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cu121

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 mluser
RUN chown -R mluser:mluser /app
USER mluser

EXPOSE 8000
HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

CMD ["python3", "-m", "uvicorn", "app:app", "--host", "0.0.0.0"]
```

### Docker Compose for Local Development

```yaml
# docker-compose.yml
version: '3.9'

services:
  model_server:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - MODEL_PATH=/models
      - LOG_LEVEL=INFO
      - WORKERS=4
    volumes:
      - ./models:/models
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  prometheus_data:
  grafana_data:
```

### Security Best Practices

```dockerfile
# Secure Dockerfile checklist

# 1. Use slim/alpine base images
FROM python:3.10-slim

# 2. Run as non-root user
RUN useradd -m -u 1000 mluser
USER mluser

# 3. Remove unnecessary files
RUN rm -rf /usr/share/doc/* /usr/share/man/*

# 4. Use COPY instead of ADD (more predictable)
COPY app/ /app/

# 5. Multi-stage builds to reduce image size
# (see multi-stage example above)

# 6. Use specific version tags
RUN pip install torch==2.0.0 torchvision==0.15.0

# 7. Scan for vulnerabilities
# docker scan myimage:latest
# or use Trivy: trivy image myimage:latest
```

---

## Kubernetes Deployment

### Production Kubernetes Architecture

Deploy ML models with high availability, auto-scaling, and service mesh integration.

### Basic Model Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-server
  namespace: production
  labels:
    app: ml-model-server
    version: v1.0.0
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: ml-model-server
  template:
    metadata:
      labels:
        app: ml-model-server
        version: v1.0.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      # Pod disruption budget for high availability
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - ml-model-server
              topologyKey: kubernetes.io/hostname

      # Service account with minimal permissions
      serviceAccountName: ml-model-server

      # Init containers for setup
      initContainers:
      - name: model-download
        image: gcr.io/cloud-builders/gsutil
        command: ['bash', '-c']
        args:
        - |
          gsutil -m cp -r gs://model-bucket/model-v1.0/* /models/
        volumeMounts:
        - name: models
          mountPath: /models

      containers:
      - name: model-server
        image: myregistry.azurecr.io/ml-model-server:1.0.0
        imagePullPolicy: IfNotPresent

        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        - name: metrics
          containerPort: 8001
          protocol: TCP

        env:
        - name: MODEL_PATH
          value: "/models"
        - name: WORKERS
          value: "4"
        - name: LOG_LEVEL
          value: "INFO"
        - name: PYTHONUNBUFFERED
          value: "1"

        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
            ephemeral-storage: "5Gi"
          limits:
            cpu: "2000m"
            memory: "4Gi"
            ephemeral-storage: "10Gi"

        # Liveness probe
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        # Readiness probe
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2

        # Startup probe for slow-starting apps
        startupProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 0
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 30

        # Graceful shutdown
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]

        volumeMounts:
        - name: models
          mountPath: /models
          readOnly: true
        - name: logs
          mountPath: /var/log/app
        - name: cache
          mountPath: /tmp/cache

        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL

      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: model-storage
      - name: logs
        emptyDir: {}
      - name: cache
        emptyDir: {}

      # Pod disruption budget
      terminationGracePeriodSeconds: 30

      # Pull secrets for private registry
      imagePullSecrets:
      - name: acr-credentials

---
# Service
apiVersion: v1
kind: Service
metadata:
  name: ml-model-server
  namespace: production
spec:
  type: ClusterIP
  selector:
    app: ml-model-server
  ports:
  - name: http
    port: 8000
    targetPort: 8000
    protocol: TCP
  - name: metrics
    port: 8001
    targetPort: 8001
    protocol: TCP

---
# HorizontalPodAutoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-model-server-hpa
  namespace: production
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max

---
# ServiceMonitor for Prometheus
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: ml-model-server
  namespace: production
spec:
  selector:
    matchLabels:
      app: ml-model-server
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### Persistent Volume for Model Storage

```yaml
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: model-storage
  namespace: production
spec:
  accessModes:
    - ReadOnlyMany
  resources:
    requests:
      storage: 50Gi
  storageClassName: fast-ssd

---
# Kubernetes ConfigMap for configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: ml-model-config
  namespace: production
data:
  config.yaml: |
    model:
      name: resnet50
      version: 1.0.0
      batch_size: 32
      max_batch_delay: 10
    server:
      workers: 4
      timeout: 120
    monitoring:
      enabled: true
      metrics_port: 8001

---
# Kubernetes Secret for credentials
apiVersion: v1
kind: Secret
metadata:
  name: ml-model-secrets
  namespace: production
type: Opaque
stringData:
  api_key: "your-api-key-here"
  db_connection: "postgresql://user:pass@host/db"
```

### RBAC for Service Account

```yaml
# rbac.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ml-model-server
  namespace: production

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ml-model-server
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: ml-model-server
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: ml-model-server
subjects:
- kind: ServiceAccount
  name: ml-model-server
  namespace: production
```

---

## API Design for ML Services

### REST API Best Practices

```python
# app.py - FastAPI Implementation
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import numpy as np
import logging
from enum import Enum
import time
from datetime import datetime

app = FastAPI(
    title="ML Model Server",
    description="Production-grade ML model serving API",
    version="1.0.0"
)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class PredictionInput(BaseModel):
    """Input schema for predictions"""
    features: List[float] = Field(..., min_items=1, max_items=1000, description="Input features")
    model_version: str = Field(default="latest", description="Model version to use")
    request_id: Optional[str] = Field(None, description="Unique request identifier")

    @validator('features')
    def validate_features(cls, v):
        if any(not isinstance(x, (int, float)) for x in v):
            raise ValueError("All features must be numeric")
        return v

class PredictionOutput(BaseModel):
    """Output schema for predictions"""
    prediction: float
    confidence: float = Field(..., ge=0.0, le=1.0)
    model_version: str
    processing_time_ms: float
    request_id: Optional[str]

class BatchPredictionInput(BaseModel):
    """Batch prediction input"""
    instances: List[List[float]] = Field(..., max_items=1000)
    model_version: str = Field(default="latest")

class HealthStatus(BaseModel):
    """Health check status"""
    status: str
    timestamp: datetime
    model_loaded: bool
    version: str
    uptime_seconds: float

# Global state
model_state = {
    "model": None,
    "version": "1.0.0",
    "loaded": False,
    "start_time": time.time()
}

# Endpoints

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    logger.info("Loading ML model...")
    # model_state["model"] = load_model()
    model_state["loaded"] = True
    logger.info(f"Model loaded successfully: {model_state['version']}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down model server...")
    if model_state["model"]:
        # Cleanup code
        pass

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Comprehensive health check endpoint"""
    return HealthStatus(
        status="healthy" if model_state["loaded"] else "degraded",
        timestamp=datetime.utcnow(),
        model_loaded=model_state["loaded"],
        version=model_state["version"],
        uptime_seconds=time.time() - model_state["start_time"]
    )

@app.get("/health/live")
async def liveness_probe():
    """Kubernetes liveness probe"""
    if not model_state["loaded"]:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness_probe():
    """Kubernetes readiness probe"""
    if not model_state["loaded"]:
        raise HTTPException(status_code=503, detail="Not ready")
    return {"status": "ready"}

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    """
    Single prediction endpoint

    Args:
        input_data: Input features and configuration

    Returns:
        Prediction with confidence score
    """
    start_time = time.time()

    try:
        if not model_state["loaded"]:
            raise HTTPException(status_code=503, detail="Model not available")

        # Validate input
        if len(input_data.features) == 0:
            raise HTTPException(status_code=400, detail="Empty features")

        # Preprocess
        features = np.array(input_data.features).reshape(1, -1)

        # Inference (mock)
        prediction = float(np.mean(features))
        confidence = 0.95

        processing_time = (time.time() - start_time) * 1000

        logger.info(f"Prediction request processed in {processing_time:.2f}ms")

        return PredictionOutput(
            prediction=prediction,
            confidence=confidence,
            model_version=input_data.model_version,
            processing_time_ms=processing_time,
            request_id=input_data.request_id
        )

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/batch")
async def batch_predict(input_data: BatchPredictionInput, background_tasks: BackgroundTasks):
    """
    Batch prediction endpoint

    Args:
        input_data: Multiple instances for prediction
        background_tasks: FastAPI background task handler

    Returns:
        List of predictions
    """
    start_time = time.time()

    try:
        if len(input_data.instances) == 0:
            raise HTTPException(status_code=400, detail="Empty batch")

        if len(input_data.instances) > 1000:
            raise HTTPException(status_code=400, detail="Batch size exceeds limit")

        # Process batch
        features = np.array(input_data.instances)
        predictions = np.mean(features, axis=1).tolist()

        processing_time = (time.time() - start_time) * 1000

        # Log batch statistics in background
        background_tasks.add_task(
            logger.info,
            f"Batch prediction: {len(input_data.instances)} instances in {processing_time:.2f}ms"
        )

        return {
            "predictions": predictions,
            "count": len(predictions),
            "processing_time_ms": processing_time,
            "model_version": input_data.model_version
        }

    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """List available models and versions"""
    return {
        "models": [
            {
                "name": "resnet50",
                "versions": ["1.0.0", "1.1.0"],
                "current": "1.0.0"
            }
        ]
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return """
    # HELP predictions_total Total number of predictions
    # TYPE predictions_total counter
    predictions_total 1000

    # HELP prediction_duration_seconds Prediction processing time
    # TYPE prediction_duration_seconds histogram
    prediction_duration_seconds_bucket{le="0.1"} 900
    prediction_duration_seconds_bucket{le="0.5"} 990
    prediction_duration_seconds_bucket{le="1.0"} 1000
    """

@app.post("/explain")
async def explain(input_data: PredictionInput):
    """Model explainability endpoint (LIME, SHAP)"""
    return {
        "request_id": input_data.request_id,
        "explanation": "Feature importance scores",
        "feature_importance": {f"feature_{i}": score for i, score in enumerate([0.3, 0.2, 0.5])}
    }

# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return {"detail": str(exc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)
```

### gRPC Service Definition

```protobuf
// service.proto
syntax = "proto3";

package ml_service;

service PredictionService {
  rpc Predict (PredictionRequest) returns (PredictionResponse);
  rpc BatchPredict (BatchPredictionRequest) returns (BatchPredictionResponse);
  rpc GetHealth (HealthRequest) returns (HealthResponse);
}

message PredictionRequest {
  repeated float features = 1;
  string model_version = 2;
  string request_id = 3;
}

message PredictionResponse {
  float prediction = 1;
  float confidence = 2;
  string model_version = 3;
  float processing_time_ms = 4;
  string request_id = 5;
}

message BatchPredictionRequest {
  repeated Instance instances = 1;
  string model_version = 2;
}

message Instance {
  repeated float features = 1;
}

message BatchPredictionResponse {
  repeated float predictions = 1;
  float processing_time_ms = 2;
  int32 count = 3;
}

message HealthRequest {}

message HealthResponse {
  string status = 1;
  bool model_loaded = 2;
  string version = 3;
}
```

---

## Load Balancing and Autoscaling

### Kubernetes HPA with Custom Metrics

```yaml
# hpa-custom-metrics.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-model-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-model-server
  minReplicas: 3
  maxReplicas: 50
  metrics:
  # CPU scaling
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

  # Memory scaling
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

  # Custom metric: request latency
  - type: Pods
    pods:
      metric:
        name: http_request_duration_seconds
      target:
        type: AverageValue
        averageValue: "100m"  # 100 milliseconds

  # Custom metric: request rate
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"

  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 1
        periodSeconds: 120
      selectPolicy: Min

    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
```

### Load Balancing with Istio

```yaml
# istio-lb.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ml-model-vs
  namespace: production
spec:
  hosts:
  - ml-model-server
  http:
  - match:
    - uri:
        prefix: "/predict"
    route:
    - destination:
        host: ml-model-server
        port:
          number: 8000
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s

---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: ml-model-dr
  namespace: production
spec:
  host: ml-model-server
  trafficPolicy:
    connectionPool:
      http:
        http1MaxPendingRequests: 1024
        maxRequestsPerConnection: 100
      tcp:
        maxConnections: 1000
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

### nginx Ingress with Load Balancing

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ml-model-ingress
  namespace: production
  annotations:
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/limit-rps: "100"
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "600"
    nginx.ingress.kubernetes.io/enable-cors: "true"
spec:
  ingressClassName: nginx
  rules:
  - host: ml-api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ml-model-server
            port:
              number: 8000
  tls:
  - hosts:
    - ml-api.example.com
    secretName: ml-api-tls
```

---

## Monitoring and Logging

### Prometheus Metrics Collection

```python
# metrics.py - Prometheus instrumentation
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
from functools import wraps

# Counters
predictions_total = Counter(
    'ml_predictions_total',
    'Total number of predictions',
    ['model_version', 'status']
)

errors_total = Counter(
    'ml_errors_total',
    'Total number of errors',
    ['error_type']
)

# Histograms
prediction_duration = Histogram(
    'ml_prediction_duration_seconds',
    'Prediction processing time',
    ['model_version'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0)
)

batch_size = Histogram(
    'ml_batch_size',
    'Batch prediction size',
    buckets=(1, 10, 50, 100, 500, 1000)
)

# Gauges
active_requests = Gauge(
    'ml_active_requests',
    'Currently active requests'
)

model_load_time = Gauge(
    'ml_model_load_time_seconds',
    'Time to load model',
    ['model_name']
)

# Decorator for automatic metrics
def record_metrics(model_version="1.0.0"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            active_requests.inc()
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                predictions_total.labels(
                    model_version=model_version,
                    status="success"
                ).inc()
                return result
            except Exception as e:
                errors_total.labels(error_type=type(e).__name__).inc()
                predictions_total.labels(
                    model_version=model_version,
                    status="error"
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                prediction_duration.labels(model_version=model_version).observe(duration)
                active_requests.dec()

        return wrapper
    return decorator
```

### ELK Stack Configuration

```yaml
# elasticsearch.yaml
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: ml-logs
  namespace: production
spec:
  version: 8.5.0
  nodeSets:
  - name: default
    count: 3
    config:
      node.store.allow_mmap: false
    podTemplate:
      spec:
        containers:
        - name: elasticsearch
          resources:
            requests:
              memory: "2Gi"
              cpu: "500m"
            limits:
              memory: "4Gi"
              cpu: "1000m"

---
apiVersion: kibana.k8s.elastic.co/v1
kind: Kibana
metadata:
  name: ml-kibana
  namespace: production
spec:
  version: 8.5.0
  count: 1
  elasticsearchRef:
    name: ml-logs

---
apiVersion: beat.k8s.elastic.co/v1beta1
kind: Filebeat
metadata:
  name: ml-filebeat
  namespace: production
spec:
  version: 8.5.0
  deployment:
    replicas: 1
  elasticsearchRef:
    name: ml-logs
  config:
    filebeat.inputs:
    - type: container
      paths:
      - '/var/log/containers/*-ml-model-server-*.log'
      processors:
      - add_kubernetes_metadata: ~
```

### Structured Logging

```python
# logging_config.py
import json
import logging
from pythonjsonlogger import jsonlogger
import sys
from datetime import datetime

class JSONFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(JSONFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['process_id'] = record.process
        log_record['thread_id'] = record.thread

# Configure structured logging
def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # JSON handler for stdout
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(json_handler)

    return root_logger

logger = setup_logging()

# Usage examples
logger.info("Model loaded", extra={
    "model_name": "resnet50",
    "model_version": "1.0.0",
    "load_time_ms": 1234
})

logger.warning("High memory usage", extra={
    "memory_mb": 3500,
    "limit_mb": 4000,
    "percentage": 87.5
})
```

### Alerting Rules

```yaml
# prometheus-rules.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-rules
  namespace: production
data:
  ml-alerts.yml: |
    groups:
    - name: ml_model_alerts
      interval: 30s
      rules:
      - alert: HighPredictionLatency
        expr: histogram_quantile(0.95, ml_prediction_duration_seconds) > 1
        for: 5m
        annotations:
          summary: "High prediction latency detected"
          description: "P95 latency is {{ $value }}s"

      - alert: HighErrorRate
        expr: rate(ml_errors_total[5m]) > 0.01
        for: 2m
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"

      - alert: ModelNotReady
        expr: ml_model_ready == 0
        for: 1m
        annotations:
          summary: "Model not ready"
          description: "Model has been unavailable for 1 minute"

      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes{pod=~"ml-model-server.*"} > 3.5e9
        for: 5m
        annotations:
          summary: "High memory usage"
          description: "Pod using {{ $value | humanize }}B"
```

---

## A/B Testing

### A/B Testing Framework

```python
# ab_testing.py
import random
from typing import Tuple, Dict, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import json

class ModelVariant(Enum):
    CONTROL = "control"
    VARIANT_A = "variant_a"
    VARIANT_B = "variant_b"

@dataclass
class Experiment:
    experiment_id: str
    name: str
    start_time: datetime
    control_model: str
    treatment_models: Dict[str, str]
    traffic_split: Dict[ModelVariant, float]  # e.g., {control: 0.5, variant_a: 0.3, variant_b: 0.2}
    metrics: Dict[str, float]

class ABTestingFramework:
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.results_cache = []

    def create_experiment(
        self,
        experiment_id: str,
        name: str,
        control_model: str,
        treatment_models: Dict[str, str],
        traffic_split: Dict[str, float]
    ) -> Experiment:
        """Create a new A/B test experiment"""
        traffic_split_enum = {
            ModelVariant[k.upper()]: v
            for k, v in traffic_split.items()
        }

        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            start_time=datetime.utcnow(),
            control_model=control_model,
            treatment_models=treatment_models,
            traffic_split=traffic_split_enum,
            metrics={}
        )

        self.experiments[experiment_id] = experiment
        return experiment

    def assign_variant(self, experiment_id: str, user_id: str) -> ModelVariant:
        """Assign user to a variant (consistent hashing)"""
        experiment = self.experiments[experiment_id]

        # Use user_id for consistent assignment
        hash_value = hash(f"{experiment_id}:{user_id}") % 100

        cumulative = 0
        for variant, traffic in experiment.traffic_split.items():
            cumulative += traffic * 100
            if hash_value < cumulative:
                return variant

        return ModelVariant.CONTROL

    def record_metric(
        self,
        experiment_id: str,
        user_id: str,
        variant: ModelVariant,
        metric_name: str,
        metric_value: float
    ):
        """Record a metric for analysis"""
        self.results_cache.append({
            "experiment_id": experiment_id,
            "user_id": user_id,
            "variant": variant.value,
            "metric": metric_name,
            "value": metric_value,
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_statistics(self, experiment_id: str, metric_name: str) -> Dict[str, Any]:
        """Calculate statistical summary of results"""
        import numpy as np
        from scipy import stats

        results = [r for r in self.results_cache
                  if r["experiment_id"] == experiment_id
                  and r["metric"] == metric_name]

        if not results:
            return {}

        # Group by variant
        grouped = {}
        for result in results:
            variant = result["variant"]
            if variant not in grouped:
                grouped[variant] = []
            grouped[variant].append(result["value"])

        # Calculate statistics
        stats_result = {}
        for variant, values in grouped.items():
            values = np.array(values)
            stats_result[variant] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "median": float(np.median(values)),
                "count": len(values),
                "min": float(np.min(values)),
                "max": float(np.max(values))
            }

        # T-test for significance
        if len(grouped) >= 2:
            variants = list(grouped.keys())
            control_values = np.array(grouped[variants[0]])
            treatment_values = np.array(grouped[variants[1]])

            t_stat, p_value = stats.ttest_ind(control_values, treatment_values)
            stats_result["statistical_test"] = {
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "significant": p_value < 0.05
            }

        return stats_result

# FastAPI integration
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
ab_testing = ABTestingFramework()

class PredictionRequestAB(BaseModel):
    user_id: str
    experiment_id: str
    features: list
    metric_feedback: dict = {}

@app.post("/predict/ab")
async def predict_with_ab_test(request: PredictionRequestAB):
    """Prediction endpoint with A/B testing"""

    # Assign variant
    variant = ab_testing.assign_variant(
        request.experiment_id,
        request.user_id
    )

    # Select model based on variant
    experiment = ab_testing.experiments[request.experiment_id]
    if variant == ModelVariant.CONTROL:
        model_to_use = experiment.control_model
    else:
        model_name = list(experiment.treatment_models.keys())[
            list(ModelVariant).index(variant) - 1
        ]
        model_to_use = experiment.treatment_models[model_name]

    # Make prediction with selected model
    prediction = {"value": 0.5, "model": model_to_use}

    # Record metrics if provided
    for metric_name, metric_value in request.metric_feedback.items():
        ab_testing.record_metric(
            request.experiment_id,
            request.user_id,
            variant,
            metric_name,
            metric_value
        )

    return {
        "prediction": prediction,
        "variant": variant.value,
        "experiment_id": request.experiment_id
    }

@app.get("/experiments/{experiment_id}/results")
async def get_experiment_results(experiment_id: str, metric: str):
    """Retrieve experiment results and statistical analysis"""
    stats = ab_testing.get_statistics(experiment_id, metric)
    return stats
```

---

## Canary Deployments

### Canary Deployment with Flagger

```yaml
# flagger-canary.yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: ml-model-canary
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-model-server

  progressDeadlineSeconds: 300

  service:
    port: 8000

  analysis:
    # Interval between canary checks
    interval: 1m
    # Number of successful checks before promoting
    threshold: 5
    # Maximum weight for canary replica
    maxWeight: 50
    # Step weight increase
    stepWeight: 10

    metrics:
    # HTTP success rate
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m

    # P95 latency
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m

    # Error rate threshold
    - name: error-rate
      thresholdRange:
        max: 1
      interval: 1m

  skipAnalysis: false

---
# VirtualService for traffic routing
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ml-model-canary
  namespace: production
spec:
  hosts:
  - ml-model-server
  http:
  - match:
    - uri:
        prefix: "/predict"
    route:
    - destination:
        host: ml-model-server-primary
        port:
          number: 8000
      weight: 90
    - destination:
        host: ml-model-server-canary
        port:
          number: 8000
      weight: 10
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s
```

### Manual Canary Deployment Strategy

```yaml
# canary-manual.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-server-v1
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-model-server
      version: v1
  template:
    metadata:
      labels:
        app: ml-model-server
        version: v1
    spec:
      containers:
      - name: model-server
        image: myregistry.azurecr.io/ml-model-server:1.0.0
        ports:
        - containerPort: 8000

---
# Canary deployment (new version)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-server-v2-canary
  namespace: production
spec:
  replicas: 1  # Start with 1 replica
  selector:
    matchLabels:
      app: ml-model-server
      version: v2
      track: canary
  template:
    metadata:
      labels:
        app: ml-model-server
        version: v2
        track: canary
    spec:
      containers:
      - name: model-server
        image: myregistry.azurecr.io/ml-model-server:2.0.0
        ports:
        - containerPort: 8000

---
# VirtualService routing traffic
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ml-model-canary-route
  namespace: production
spec:
  hosts:
  - ml-model-server
  http:
  - match:
    - headers:
        user-id:
          regex: "^(canary-user-.*)$"
    route:
    - destination:
        host: ml-model-server
        subset: v2-canary
      port:
        number: 8000
    weight: 5
  - route:
    - destination:
        host: ml-model-server
        subset: v1
      port:
        number: 8000
      weight: 95

---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: ml-model-canary-dr
  namespace: production
spec:
  host: ml-model-server
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2-canary
    labels:
      version: v2
      track: canary
```

---

## Complete Deployment Examples

### End-to-End Production Deployment Example

```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: production

commonLabels:
  app: ml-model-server
  environment: production

replicas:
- name: ml-model-server
  count: 3

resources:
- deployment.yaml
- service.yaml
- ingress.yaml
- hpa.yaml
- configmap.yaml
- secret.yaml
- serviceaccount.yaml
- rbac.yaml
- pvc.yaml

images:
- name: myregistry.azurecr.io/ml-model-server
  newTag: "1.0.0"

patches:
- target:
    kind: Deployment
    name: ml-model-server
  patch: |-
    - op: replace
      path: /spec/template/spec/containers/0/resources/limits/memory
      value: 4Gi
```

### Complete Docker Compose Stack

```yaml
# docker-compose-prod.yaml
version: '3.9'

services:
  ml-model-server:
    build:
      context: .
      dockerfile: Dockerfile
      cache_from:
      - ml-model-server:latest
    image: ml-model-server:1.0.0
    container_name: ml-model-server
    restart: unless-stopped
    ports:
      - "8000:8000"
      - "8001:8001"  # Metrics
    environment:
      - MODEL_PATH=/models
      - LOG_LEVEL=INFO
      - WORKERS=4
      - ENABLE_METRICS=true
    volumes:
      - model_storage:/models:ro
      - ./logs:/var/log/app
      - ./config/app.yaml:/app/config.yaml:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - ml-network
    depends_on:
      - prometheus
      - elasticsearch
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./alerts.yml:/etc/prometheus/alerts.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
    networks:
      - ml-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=redis-datasource
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
    networks:
      - ml-network
    depends_on:
      - prometheus

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    container_name: elasticsearch
    restart: unless-stopped
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - xpack.watcher.enabled=true
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    networks:
      - ml-network
    healthcheck:
      test: curl -s http://localhost:9200 >/dev/null || exit 1
      interval: 30s
      timeout: 10s
      retries: 5

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    container_name: kibana
    restart: unless-stopped
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    networks:
      - ml-network
    depends_on:
      - elasticsearch

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.5.0
    container_name: filebeat
    restart: unless-stopped
    user: root
    volumes:
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    command: filebeat -e -strict.perms=false
    networks:
      - ml-network
    depends_on:
      - elasticsearch

volumes:
  model_storage:
  prometheus_data:
  grafana_data:
  elasticsearch_data:

networks:
  ml-network:
    driver: bridge
```

---

## Best Practices

### 1. Model Versioning and Reproducibility

```python
# model_registry.py
from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime
import json
import hashlib

@dataclass
class ModelMetadata:
    name: str
    version: str
    framework: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    metrics: Dict[str, float]
    training_date: datetime
    created_by: str
    git_commit: str
    training_dataset_hash: str
    dependencies: Dict[str, str]

class ModelRegistry:
    """Centralized model versioning and metadata management"""

    def register_model(
        self,
        model_path: str,
        metadata: ModelMetadata
    ):
        """Register a new model version"""
        # Save metadata to JSON
        metadata_dict = {
            "name": metadata.name,
            "version": metadata.version,
            "framework": metadata.framework,
            "input_schema": metadata.input_schema,
            "output_schema": metadata.output_schema,
            "metrics": metadata.metrics,
            "training_date": metadata.training_date.isoformat(),
            "created_by": metadata.created_by,
            "git_commit": metadata.git_commit,
            "training_dataset_hash": metadata.training_dataset_hash,
            "dependencies": metadata.dependencies
        }

        with open(f"{model_path}/metadata.json", "w") as f:
            json.dump(metadata_dict, f, indent=2)

# Example usage
registry = ModelRegistry()
registry.register_model(
    "/models/resnet50/v1.0.0",
    ModelMetadata(
        name="resnet50",
        version="1.0.0",
        framework="pytorch",
        input_schema={"images": "tensor[batch, 3, 224, 224]"},
        output_schema={"predictions": "tensor[batch, 1000]"},
        metrics={"accuracy": 0.92, "f1_score": 0.91},
        training_date=datetime.utcnow(),
        created_by="data-science-team",
        git_commit="abc123def456",
        training_dataset_hash="sha256:xyz789",
        dependencies={"torch": "2.0.0", "torchvision": "0.15.0"}
    )
)
```

### 2. Request Validation and Error Handling

```python
# validation.py
from pydantic import BaseModel, validator, Field
from typing import List, Optional
from enum import Enum

class ModelType(str, Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"

class PredictionRequest(BaseModel):
    """Validated prediction request"""

    features: List[float] = Field(..., min_items=1, max_items=1000)
    model_version: str = Field(default="latest", regex="^[a-z0-9.]+$")
    model_type: ModelType = Field(default=ModelType.CLASSIFICATION)
    request_id: Optional[str] = Field(None, regex="^[a-z0-9-]+$")
    timeout_ms: int = Field(default=5000, ge=100, le=60000)

    @validator('features')
    def validate_features_numeric(cls, v):
        if not all(isinstance(x, (int, float)) for x in v):
            raise ValueError("All features must be numeric")
        if any(float('inf') in [x] or float('nan') in [x] for x in v):
            raise ValueError("Features cannot contain infinity or NaN")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "features": [0.1, 0.2, 0.3],
                "model_version": "1.0.0",
                "request_id": "req-123-456"
            }
        }
```

### 3. Caching Strategy

```python
# caching.py
from functools import lru_cache
import hashlib
import json
from typing import Tuple

class ModelCache:
    """LRU cache for model predictions with hash-based keys"""

    def __init__(self, max_size: int = 10000):
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    @staticmethod
    def _hash_features(features: list) -> str:
        """Create deterministic hash of features"""
        features_str = json.dumps(features, sort_keys=True)
        return hashlib.sha256(features_str.encode()).hexdigest()

    def get(self, features: list, model_version: str) -> Optional[dict]:
        """Retrieve cached prediction"""
        key = f"{model_version}:{self._hash_features(features)}"

        if key in self.cache:
            self.hits += 1
            return self.cache[key]

        self.misses += 1
        return None

    def set(self, features: list, model_version: str, prediction: dict):
        """Store prediction in cache"""
        key = f"{model_version}:{self._hash_features(features)}"

        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            self.cache.pop(next(iter(self.cache)))

        self.cache[key] = prediction

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
```

### 4. Security Best Practices

```python
# security.py
from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.security import APIKeyHeader
from typing import Optional
import secrets
import jwt
from datetime import datetime, timedelta

api_key_header = APIKeyHeader(name="X-API-Key")

class APIKeyValidator:
    """Validate API keys for secure model access"""

    def __init__(self, api_keys: dict):
        self.api_keys = api_keys  # {"key": "user-id"}

    async def validate_api_key(self, api_key: str = Depends(api_key_header)) -> str:
        """Validate API key and return user ID"""
        if api_key not in self.api_keys:
            raise HTTPException(status_code=403, detail="Invalid API key")
        return self.api_keys[api_key]

class JWTTokenValidator:
    """JWT token validation for API access"""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def create_token(self, user_id: str, expires_in_hours: int = 24) -> str:
        """Create JWT token"""
        payload = {
            "sub": user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=expires_in_hours)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def validate_token(self, token: str) -> str:
        """Validate JWT token and return user ID"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

# Rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter

@app.post("/predict")
@limiter.limit("100/minute")
async def predict_with_rate_limit(request, api_key: str = Depends(api_key_header)):
    """Rate-limited prediction endpoint"""
    # Validate API key and process prediction
    pass
```

### 5. Testing Strategy for ML Models

```python
# test_model.py
import pytest
from unittest.mock import patch
import numpy as np

class TestModelServer:
    """Comprehensive tests for ML model server"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "timestamp" in data

    def test_prediction_valid_input(self, client):
        """Test prediction with valid input"""
        response = client.post("/predict", json={
            "features": [0.1, 0.2, 0.3],
            "model_version": "1.0.0"
        })
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data
        assert 0 <= data["confidence"] <= 1

    def test_prediction_invalid_input(self, client):
        """Test prediction with invalid input"""
        response = client.post("/predict", json={
            "features": [],
            "model_version": "1.0.0"
        })
        assert response.status_code == 400

    def test_batch_prediction(self, client):
        """Test batch prediction"""
        response = client.post("/predict/batch", json={
            "instances": [[0.1, 0.2], [0.3, 0.4]],
            "model_version": "1.0.0"
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["predictions"]) == 2

    def test_batch_size_limit(self, client):
        """Test batch size limits"""
        large_batch = [[float(i)] * 10 for i in range(1001)]
        response = client.post("/predict/batch", json={
            "instances": large_batch,
            "model_version": "1.0.0"
        })
        assert response.status_code == 400

    def test_model_versioning(self, client):
        """Test different model versions"""
        versions = ["1.0.0", "1.1.0", "2.0.0"]
        for version in versions:
            response = client.post("/predict", json={
                "features": [0.1, 0.2],
                "model_version": version
            })
            assert response.status_code == 200
            assert response.json()["model_version"] == version

    @patch('model_loader.load_model')
    def test_model_failure_handling(self, mock_load, client):
        """Test graceful handling of model loading failure"""
        mock_load.side_effect = Exception("Model load failed")
        response = client.get("/health")
        assert response.status_code in [200, 503]

# Performance tests
import time

def test_prediction_latency():
    """Test prediction latency SLA"""
    import timeit

    def predict():
        # Your prediction logic
        return np.random.rand()

    latencies = [timeit.timeit(predict, number=1) for _ in range(100)]

    assert np.percentile(latencies, 50) < 0.1, "P50 latency SLA violated"
    assert np.percentile(latencies, 95) < 0.5, "P95 latency SLA violated"
    assert np.percentile(latencies, 99) < 1.0, "P99 latency SLA violated"
```

### 6. Compliance and Governance

```yaml
# compliance.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ml-governance-policy
  namespace: production
data:
  governance-policy.yaml: |
    # Model Governance Policy

    model_approval:
      required_tests:
        - unit_tests
        - integration_tests
        - performance_benchmarks
        - security_scan
        - data_validation
        - bias_testing

      required_documentation:
        - model_card
        - training_data_documentation
        - performance_metrics
        - limitations_and_biases
        - monitoring_plan

    deployment_requirements:
      minimum_accuracy: 0.90
      maximum_latency_ms: 500
      minimum_uptime: 0.99
      data_retention_days: 30
      model_versioning: true
      canary_deployment: true

    monitoring_requirements:
      data_drift_monitoring: enabled
      model_performance_monitoring: enabled
      alert_threshold: 0.05
      audit_logging: enabled

    compliance:
      gdpr: true
      data_anonymization: required
      model_explainability: required
      fairness_assessment: required
```

---

## Deployment Checklist

- [ ] Model archived and versioned
- [ ] Docker image built and scanned for vulnerabilities
- [ ] Kubernetes manifests validated with `kubeval`
- [ ] Health check endpoints implemented
- [ ] Metrics and logging configured
- [ ] Load testing completed
- [ ] Canary deployment strategy defined
- [ ] Monitoring and alerting set up
- [ ] Backup and disaster recovery plan
- [ ] API documentation generated
- [ ] Security audit completed
- [ ] Runbook created for common issues
- [ ] On-call escalation defined

---

## Summary

This production deployment guide provides a comprehensive approach to deploying machine learning models in enterprise environments. Key takeaways:

1. **Model Serving**: Choose the right framework based on your model type and performance requirements
2. **Containerization**: Use multi-stage Docker builds for minimal, secure images
3. **Orchestration**: Leverage Kubernetes for scalability and reliability
4. **Observability**: Implement comprehensive monitoring, logging, and alerting
5. **Reliability Patterns**: Use canary deployments and A/B testing for safe rollouts
6. **Security**: Implement API keys, rate limiting, and secure configurations
7. **Testing**: Comprehensive testing including performance and load testing
8. **Governance**: Model versioning, approval workflows, and compliance tracking

For production deployments, always test thoroughly, monitor continuously, and maintain clear rollback procedures.
