# Implementing Canary Deployments with Flagger

## Overview
This guide walks through implementing canary deployments on Kubernetes using Flagger, an open-source progressive delivery tool that automates canary analysis and promotion.

---

## Prerequisites

- Kubernetes cluster (1.19+)
- kubectl configured
- Istio, Linkerd, or App Mesh (service mesh) installed
- Prometheus for metrics (recommended)
- Helm 3.x

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Load Balancer                        │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Istio VirtualService                    │
│                   (Traffic Routing)                      │
└─────────────────────────────────────────────────────────┘
                    │              │
         ┌──────────┴───────┐     │
         │                  │     │
         ▼                  ▼     ▼
┌────────────────┐   ┌────────────────┐
│  Primary       │   │  Canary        │
│  (Stable)      │   │  (New Version) │
│  90% traffic   │   │  10% traffic   │
└────────────────┘   └────────────────┘
         │                  │
         └──────────┬───────┘
                    ▼
            ┌──────────────┐
            │  Prometheus  │
            │  (Metrics)   │
            └──────────────┘
                    │
                    ▼
            ┌──────────────┐
            │   Flagger    │
            │  (Analysis)  │
            └──────────────┘
```

---

## Step 1: Install Flagger

### Install with Helm

```bash
# Add Flagger Helm repository
helm repo add flagger https://flagger.app

# Install Flagger with Istio integration
kubectl create namespace flagger-system

helm upgrade -i flagger flagger/flagger \
  --namespace=flagger-system \
  --set crd.create=true \
  --set meshProvider=istio \
  --set metricsServer=http://prometheus.istio-system:9090

# Install Flagger Grafana dashboards (optional)
helm upgrade -i flagger-grafana flagger/grafana \
  --namespace=flagger-system \
  --set url=http://prometheus.istio-system:9090
```

### Verify Installation

```bash
# Check Flagger pods
kubectl get pods -n flagger-system

# Expected output:
# NAME                        READY   STATUS    RESTARTS   AGE
# flagger-6c7f9d4d4d-8xz2q   1/1     Running   0          1m
```

### Install Load Tester (for automated testing)

```bash
helm upgrade -i flagger-loadtester flagger/loadtester \
  --namespace=test \
  --set cmd.timeout=1h
```

---

## Step 2: Prepare Your Application

### Sample Application Deployment

```yaml
# app-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: podinfo
  namespace: test
  labels:
    app: podinfo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: podinfo
  template:
    metadata:
      labels:
        app: podinfo
    spec:
      containers:
      - name: podinfo
        image: ghcr.io/stefanprodan/podinfo:6.0.0
        ports:
        - name: http
          containerPort: 9898
          protocol: TCP
        command:
          - ./podinfo
          - --port=9898
        env:
        - name: PODINFO_UI_COLOR
          value: "#34577c"
        resources:
          limits:
            cpu: 1000m
            memory: 512Mi
          requests:
            cpu: 100m
            memory: 64Mi
        livenessProbe:
          httpGet:
            path: /healthz
            port: 9898
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /readyz
            port: 9898
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: podinfo
  namespace: test
spec:
  type: ClusterIP
  selector:
    app: podinfo
  ports:
  - name: http
    port: 9898
    targetPort: http
    protocol: TCP
```

### Apply the Deployment

```bash
kubectl create namespace test
kubectl apply -f app-deployment.yaml
```

---

## Step 3: Create Canary Resource

### Basic Canary Configuration

```yaml
# canary.yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: podinfo
  namespace: test
spec:
  # Deployment reference
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: podinfo

  # HPA reference (optional)
  autoscalerRef:
    apiVersion: autoscaling/v2
    kind: HorizontalPodAutoscaler
    name: podinfo

  # Service reference
  service:
    port: 9898
    targetPort: 9898
    # Istio traffic policy
    gateways:
    - public-gateway.istio-system.svc.cluster.local
    hosts:
    - podinfo.example.com
    trafficPolicy:
      tls:
        mode: DISABLE

  # Canary analysis configuration
  analysis:
    # Schedule interval (default 60s)
    interval: 30s
    # Max number of failed metric checks before rollback
    threshold: 5
    # Max traffic percentage routed to canary (default 50)
    maxWeight: 50
    # Canary increment step (default 5)
    stepWeight: 10
    # Promotion validation (checks before promoting)
    iterations: 10

    # Metrics for analysis
    metrics:
    - name: request-success-rate
      # Minimum success rate (percentage)
      thresholdRange:
        min: 99
      interval: 1m

    - name: request-duration
      # Maximum request duration (milliseconds)
      thresholdRange:
        max: 500
      interval: 1m

    # Webhooks for testing (optional)
    webhooks:
      - name: load-test
        url: http://flagger-loadtester.test/
        timeout: 5s
        metadata:
          type: cmd
          cmd: "hey -z 1m -q 10 -c 2 http://podinfo-canary.test:9898/"
```

### Apply Canary Configuration

```bash
kubectl apply -f canary.yaml
```

### Verify Canary Setup

```bash
# Check canary status
kubectl get canary -n test

# Detailed status
kubectl describe canary podinfo -n test

# Watch canary events
kubectl get events -n test --watch --field-selector involvedObject.name=podinfo
```

---

## Step 4: Configure Metrics

### Prometheus Metrics Templates

```yaml
# metrics.yaml
apiVersion: flagger.app/v1beta1
kind: MetricTemplate
metadata:
  name: request-success-rate
  namespace: test
spec:
  provider:
    type: prometheus
    address: http://prometheus.istio-system:9090
  query: |
    sum(
      rate(
        istio_requests_total{
          reporter="destination",
          destination_workload_namespace="{{ namespace }}",
          destination_workload=~"{{ target }}",
          response_code!~"5.*"
        }[{{ interval }}]
      )
    )
    /
    sum(
      rate(
        istio_requests_total{
          reporter="destination",
          destination_workload_namespace="{{ namespace }}",
          destination_workload=~"{{ target }}"
        }[{{ interval }}]
      )
    ) * 100
---
apiVersion: flagger.app/v1beta1
kind: MetricTemplate
metadata:
  name: request-duration
  namespace: test
spec:
  provider:
    type: prometheus
    address: http://prometheus.istio-system:9090
  query: |
    histogram_quantile(0.99,
      sum(
        rate(
          istio_request_duration_milliseconds_bucket{
            reporter="destination",
            destination_workload_namespace="{{ namespace }}",
            destination_workload=~"{{ target }}"
          }[{{ interval }}]
        )
      ) by (le)
    )
---
apiVersion: flagger.app/v1beta1
kind: MetricTemplate
metadata:
  name: error-rate
  namespace: test
spec:
  provider:
    type: prometheus
    address: http://prometheus.istio-system:9090
  query: |
    sum(
      rate(
        istio_requests_total{
          reporter="destination",
          destination_workload_namespace="{{ namespace }}",
          destination_workload=~"{{ target }}",
          response_code=~"5.*"
        }[{{ interval }}]
      )
    )
    /
    sum(
      rate(
        istio_requests_total{
          reporter="destination",
          destination_workload_namespace="{{ namespace }}",
          destination_workload=~"{{ target }}"
        }[{{ interval }}]
      )
    ) * 100
```

### Custom Metrics

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: podinfo
  namespace: test
spec:
  # ... other config ...
  analysis:
    metrics:
    # Built-in Istio metrics
    - name: request-success-rate
      templateRef:
        name: request-success-rate
        namespace: test
      thresholdRange:
        min: 99
      interval: 1m

    # Custom business metric
    - name: conversion-rate
      templateRef:
        name: conversion-rate
        namespace: test
      thresholdRange:
        min: 95
      interval: 2m

    # Custom application metric
    - name: cache-hit-rate
      templateRef:
        name: cache-hit-rate
        namespace: test
      thresholdRange:
        min: 80
      interval: 1m
```

---

## Step 5: Trigger Canary Deployment

### Update Container Image

```bash
# Update deployment with new image version
kubectl -n test set image deployment/podinfo \
  podinfo=ghcr.io/stefanprodan/podinfo:6.1.0

# Or update the YAML and apply
kubectl apply -f app-deployment.yaml
```

### Monitor Canary Progress

```bash
# Watch canary status
kubectl get canary podinfo -n test --watch

# Watch events
kubectl get events -n test --watch \
  --field-selector involvedObject.name=podinfo

# Check traffic weights
kubectl get virtualservice podinfo -n test -o yaml

# Check pods
kubectl get pods -n test -l app=podinfo
```

### Canary Progression States

```
Initializing → Waiting → Progressing → Promoting → Finalizing → Succeeded
                   ↓
              (If metrics fail)
                   ↓
              Rollback
```

---

## Step 6: Automated Testing with Webhooks

### Load Test Webhook

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: podinfo
  namespace: test
spec:
  # ... other config ...
  analysis:
    webhooks:
    # Load testing
    - name: load-test
      type: pre-rollout
      url: http://flagger-loadtester.test/
      timeout: 15s
      metadata:
        type: cmd
        cmd: "hey -z 2m -q 10 -c 2 http://podinfo-canary.test:9898/"

    # Smoke tests
    - name: smoke-test
      type: pre-rollout
      url: http://flagger-loadtester.test/
      timeout: 30s
      metadata:
        type: bash
        cmd: |
          curl -s http://podinfo-canary.test:9898/healthz | grep OK

    # Integration tests
    - name: integration-test
      type: pre-rollout
      url: http://flagger-loadtester.test/
      timeout: 60s
      metadata:
        type: bash
        cmd: |
          ./run-integration-tests.sh http://podinfo-canary.test:9898
```

### Custom Webhook Server

```python
# webhook-server.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/validate', methods=['POST'])
def validate_canary():
    """Custom validation logic"""
    payload = request.json

    canary_url = payload.get('canary_url')
    namespace = payload.get('namespace')
    name = payload.get('name')

    try:
        # Run custom validation
        response = requests.get(f"{canary_url}/api/info", timeout=5)

        if response.status_code == 200:
            data = response.json()

            # Custom business logic validation
            if data.get('version') and data.get('status') == 'healthy':
                return jsonify({'approved': True})

        return jsonify({'approved': False, 'reason': 'Validation failed'})

    except Exception as e:
        return jsonify({'approved': False, 'reason': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

---

## Step 7: Advanced Canary Configurations

### A/B Testing Configuration

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: podinfo
  namespace: test
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: podinfo
  service:
    port: 9898
  analysis:
    interval: 1m
    threshold: 10
    iterations: 10
    # A/B testing: route users based on headers
    match:
      - headers:
          user-agent:
            regex: ".*Mobile.*"
      - headers:
          x-canary:
            exact: "insider"
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
```

### Blue-Green with Canary Analysis

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: podinfo
  namespace: test
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: podinfo
  service:
    port: 9898
  analysis:
    interval: 1m
    threshold: 10
    # Blue-Green: no traffic shifting, just analysis
    iterations: 10
    # Skip traffic shifting (blue-green mode)
    maxWeight: 0
    # Run analysis on canary
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    # Send test traffic to canary
    webhooks:
    - name: load-test
      url: http://flagger-loadtester.test/
      metadata:
        cmd: "hey -z 1m -q 10 -c 2 http://podinfo-canary.test:9898/"
```

### Canary with Session Affinity

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: podinfo
  namespace: test
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: podinfo
  service:
    port: 9898
    # Istio traffic policy for session affinity
    trafficPolicy:
      loadBalancer:
        consistentHash:
          httpCookie:
            name: "user-session"
            ttl: 3600s
  analysis:
    interval: 30s
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
```

---

## Step 8: Monitoring and Alerting

### Prometheus Alerts

```yaml
# prometheus-alerts.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-alerts
  namespace: monitoring
data:
  canary-alerts.yaml: |
    groups:
    - name: canary
      interval: 30s
      rules:
      - alert: CanaryRollbackDetected
        expr: flagger_canary_status{phase="Failed"} > 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Canary deployment failed"
          description: "Canary {{ $labels.name }} in namespace {{ $labels.namespace }} was rolled back"

      - alert: CanaryStuck
        expr: |
          (
            flagger_canary_status{phase="Progressing"} > 0
            and
            time() - flagger_canary_last_transition_time > 1800
          )
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Canary deployment stuck"
          description: "Canary {{ $labels.name }} has been progressing for >30 minutes"

      - alert: CanaryHighErrorRate
        expr: |
          rate(istio_requests_total{
            destination_workload=~".*-canary",
            response_code=~"5.."
          }[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate in canary"
          description: "Canary workload has >5% error rate"
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Flagger Canary Deployments",
    "panels": [
      {
        "title": "Canary Success Rate",
        "targets": [
          {
            "expr": "sum(rate(istio_requests_total{destination_workload=~\".*-canary\",response_code!~\"5.*\"}[1m])) / sum(rate(istio_requests_total{destination_workload=~\".*-canary\"}[1m])) * 100"
          }
        ]
      },
      {
        "title": "Traffic Weight",
        "targets": [
          {
            "expr": "flagger_canary_weight"
          }
        ]
      },
      {
        "title": "Canary Duration",
        "targets": [
          {
            "expr": "flagger_canary_duration_seconds"
          }
        ]
      }
    ]
  }
}
```

---

## Step 9: Rollback Scenarios

### Manual Rollback

```bash
# Suspend canary analysis
kubectl -n test patch canary/podinfo --type=merge \
  -p '{"spec":{"skipAnalysis":true}}'

# Rollback to previous version
kubectl -n test set image deployment/podinfo \
  podinfo=ghcr.io/stefanprodan/podinfo:6.0.0

# Resume canary analysis
kubectl -n test patch canary/podinfo --type=merge \
  -p '{"spec":{"skipAnalysis":false}}'
```

### Automated Rollback (Metric Threshold)

Flagger automatically rolls back if:
- Metrics exceed thresholds
- Analysis fails `threshold` consecutive times
- Webhooks return failure

```bash
# Check rollback events
kubectl get events -n test \
  --field-selector reason=Synced,involvedObject.name=podinfo \
  --sort-by='.lastTimestamp'
```

---

## Step 10: Best Practices

### 1. Start Conservative

```yaml
analysis:
  interval: 1m          # Start with longer intervals
  threshold: 10         # Higher threshold = more tolerant
  maxWeight: 30         # Lower max weight = safer
  stepWeight: 5         # Smaller steps = slower rollout
  iterations: 20        # More iterations = more validation
```

### 2. Comprehensive Metrics

```yaml
metrics:
  # Performance
  - name: request-success-rate
    thresholdRange:
      min: 99
  - name: request-duration
    thresholdRange:
      max: 500

  # Business metrics
  - name: conversion-rate
    thresholdRange:
      min: 95

  # Infrastructure
  - name: cpu-usage
    thresholdRange:
      max: 80
```

### 3. Progressive Rollout Schedule

```
Traffic Distribution Timeline:
0min:  Primary: 100%, Canary: 0%   (Deploy)
2min:  Primary: 90%,  Canary: 10%  (Initial traffic)
4min:  Primary: 80%,  Canary: 20%  (Increase if healthy)
6min:  Primary: 70%,  Canary: 30%
8min:  Primary: 60%,  Canary: 40%
10min: Primary: 50%,  Canary: 50%
12min: Primary: 0%,   Canary: 100% (Promote if all checks pass)
```

### 4. Testing Strategy

```yaml
webhooks:
  # Pre-rollout: Before any traffic shift
  - name: smoke-test
    type: pre-rollout

  # Rollout: During traffic shifting
  - name: load-test
    type: rollout

  # Post-rollout: After promotion
  - name: acceptance-test
    type: post-rollout

  # Confirm promotion
  - name: confirm-promotion
    type: confirm-promotion
```

---

## Troubleshooting

### Common Issues

**Issue 1: Canary stuck in "Initializing"**
```bash
# Check Flagger logs
kubectl logs -n flagger-system deploy/flagger

# Check service mesh installation
kubectl get pods -n istio-system

# Verify Prometheus connectivity
kubectl run -it --rm debug --image=curlimages/curl \
  --restart=Never -- \
  curl http://prometheus.istio-system:9090/-/healthy
```

**Issue 2: Metrics not working**
```bash
# Test Prometheus query manually
kubectl port-forward -n istio-system svc/prometheus 9090:9090

# Access http://localhost:9090 and run query:
sum(rate(istio_requests_total{destination_workload="podinfo"}[1m]))
```

**Issue 3: Canary failing immediately**
```bash
# Check metric templates
kubectl get metrictemplates -n test

# Check canary analysis details
kubectl describe canary podinfo -n test

# Review recent events
kubectl get events -n test --sort-by='.lastTimestamp'
```

---

## Summary

You've successfully implemented canary deployments with Flagger! Key takeaways:

1. **Automated Progressive Delivery**: Flagger automates traffic shifting
2. **Metric-Based Decisions**: Uses real metrics for promotion/rollback
3. **Safety**: Automatic rollback on failures
4. **Flexibility**: Supports A/B testing, blue-green, and more
5. **Observable**: Integrated with Prometheus and Grafana

---

## Next Steps

- Implement canary deployments for your applications
- Set up custom metrics for business logic
- Configure webhooks for automated testing
- Create Grafana dashboards for monitoring
- Establish rollback procedures
- Document canary configurations

---

## Additional Resources

- Flagger Documentation: https://docs.flagger.app/
- Flagger GitHub: https://github.com/fluxcd/flagger
- Progressive Delivery: https://flagger.app/intro/
- Istio Traffic Management: https://istio.io/latest/docs/concepts/traffic-management/
