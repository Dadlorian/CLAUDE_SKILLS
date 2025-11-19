# Blue-Green Deployments with Kubernetes

## Overview
This guide demonstrates how to implement blue-green deployments on Kubernetes, providing instant rollback capabilities and zero-downtime deployments.

---

## What is Blue-Green Deployment?

Blue-green deployment maintains two identical production environments:
- **Blue**: Currently serving production traffic
- **Green**: New version, ready to receive traffic

Traffic switches atomically from blue to green, enabling instant rollback if issues arise.

---

## Architecture

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │    Service      │
                    │ (label selector)│
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
        ┌───────▼────────┐       ┌───────▼────────┐
        │  Blue Deploy   │       │ Green Deploy   │
        │  version: v1   │       │  version: v2   │
        │  (active)      │       │  (standby)     │
        └────────────────┘       └────────────────┘
```

---

## Method 1: Label-Based Service Switching

### Initial Blue Deployment

```yaml
# blue-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-blue
  namespace: production
  labels:
    app: myapp
    version: blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: myapp
        image: myapp:v1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: VERSION
          value: "v1.0.0"
        - name: COLOR
          value: "blue"
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: myapp
  namespace: production
spec:
  selector:
    app: myapp
    version: blue    # Points to blue deployment
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

### Deploy Blue Environment

```bash
# Create namespace
kubectl create namespace production

# Deploy blue version
kubectl apply -f blue-deployment.yaml

# Verify deployment
kubectl get deployments -n production
kubectl get pods -n production -l version=blue
kubectl get service myapp -n production

# Test the service
kubectl port-forward -n production svc/myapp 8080:80
curl http://localhost:8080
```

---

### Deploy Green Environment

```yaml
# green-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-green
  namespace: production
  labels:
    app: myapp
    version: green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: myapp
        image: myapp:v2.0.0    # New version
        ports:
        - containerPort: 8080
        env:
        - name: VERSION
          value: "v2.0.0"
        - name: COLOR
          value: "green"
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Deploy and Test Green

```bash
# Deploy green version (no traffic yet)
kubectl apply -f green-deployment.yaml

# Verify green pods are running
kubectl get pods -n production -l version=green

# Create temporary service to test green
kubectl expose deployment myapp-green \
  --name=myapp-green-test \
  --port=80 \
  --target-port=8080 \
  -n production

# Test green environment
kubectl port-forward -n production svc/myapp-green-test 8081:80
curl http://localhost:8081

# Run smoke tests
./run-smoke-tests.sh http://localhost:8081

# Clean up test service
kubectl delete service myapp-green-test -n production
```

---

### Switch Traffic to Green

```bash
# Method 1: Patch service
kubectl patch service myapp -n production \
  -p '{"spec":{"selector":{"version":"green"}}}'

# Method 2: Apply updated service
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: myapp
  namespace: production
spec:
  selector:
    app: myapp
    version: green    # Changed from blue to green
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
EOF

# Verify traffic switch
kubectl describe service myapp -n production

# Test the service (should now show v2.0.0)
curl http://<EXTERNAL-IP>
```

---

### Rollback to Blue

```bash
# If issues detected, instantly rollback
kubectl patch service myapp -n production \
  -p '{"spec":{"selector":{"version":"blue"}}}'

# Verify rollback
kubectl describe service myapp -n production
```

---

### Cleanup Old Deployment

```bash
# After green is stable, remove blue
kubectl delete deployment myapp-blue -n production

# Rename green to blue for next cycle
kubectl patch deployment myapp-green -n production \
  -p '{"metadata":{"name":"myapp-blue"},"spec":{"selector":{"matchLabels":{"version":"blue"}},"template":{"metadata":{"labels":{"version":"blue"}}}}}'
```

---

## Method 2: Using Ingress Controller

### Setup with Nginx Ingress

```yaml
# deployments.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-blue
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: myapp
        image: myapp:v1.0.0
        ports:
        - containerPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-green
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: myapp
        image: myapp:v2.0.0
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-blue
  namespace: production
spec:
  selector:
    app: myapp
    version: blue
  ports:
  - port: 80
    targetPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-green
  namespace: production
spec:
  selector:
    app: myapp
    version: green
  ports:
  - port: 80
    targetPort: 8080
```

### Ingress Configuration

```yaml
# ingress-blue.yaml (active)
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp-blue    # Points to blue
            port:
              number: 80
```

### Switch to Green

```yaml
# ingress-green.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp-green    # Changed to green
            port:
              number: 80
```

```bash
# Switch traffic
kubectl apply -f ingress-green.yaml

# Verify
kubectl get ingress myapp -n production -o yaml
```

---

## Method 3: Using Istio Virtual Service

### Istio Setup

```yaml
# istio-deployments.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-blue
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
      annotations:
        sidecar.istio.io/inject: "true"
    spec:
      containers:
      - name: myapp
        image: myapp:v1.0.0
        ports:
        - containerPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-green
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
      annotations:
        sidecar.istio.io/inject: "true"
    spec:
      containers:
      - name: myapp
        image: myapp:v2.0.0
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: myapp
  namespace: production
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8080
```

### Istio Gateway and VirtualService

```yaml
# istio-gateway.yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: myapp-gateway
  namespace: production
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - myapp.example.com
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: myapp-tls
    hosts:
    - myapp.example.com
---
# Virtual Service - Blue active
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
  namespace: production
spec:
  hosts:
  - myapp.example.com
  gateways:
  - myapp-gateway
  http:
  - match:
    - uri:
        prefix: /
    route:
    - destination:
        host: myapp
        subset: blue
      weight: 100
---
# Destination Rules
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: myapp
  namespace: production
spec:
  host: myapp
  subsets:
  - name: blue
    labels:
      version: blue
  - name: green
    labels:
      version: green
```

### Switch to Green with Istio

```yaml
# istio-virtualservice-green.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
  namespace: production
spec:
  hosts:
  - myapp.example.com
  gateways:
  - myapp-gateway
  http:
  - match:
    - uri:
        prefix: /
    route:
    - destination:
        host: myapp
        subset: green    # Switch to green
      weight: 100
```

```bash
# Switch traffic
kubectl apply -f istio-virtualservice-green.yaml

# Verify
kubectl get virtualservice myapp -n production -o yaml
```

---

## Method 4: Automated with Argo Rollouts

### Install Argo Rollouts

```bash
kubectl create namespace argo-rollouts

kubectl apply -n argo-rollouts -f \
  https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# Install kubectl plugin
curl -LO https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-linux-amd64
chmod +x kubectl-argo-rollouts-linux-amd64
sudo mv kubectl-argo-rollouts-linux-amd64 /usr/local/bin/kubectl-argo-rollouts
```

### Rollout Configuration

```yaml
# argo-rollout.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:v1.0.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
  # Blue-Green Strategy
  strategy:
    blueGreen:
      # Service for active version
      activeService: myapp-active
      # Service for preview version
      previewService: myapp-preview
      # Automatically promote after 5 minutes
      autoPromotionEnabled: false
      # Manual promotion required
      scaleDownDelaySeconds: 30
      # Time to keep old version
      scaleDownDelayRevisionLimit: 2
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-active
  namespace: production
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-preview
  namespace: production
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8080
```

### Deploy and Promote

```bash
# Initial deployment
kubectl apply -f argo-rollout.yaml

# Update image to new version
kubectl argo rollouts set image myapp \
  myapp=myapp:v2.0.0 \
  -n production

# Watch rollout status
kubectl argo rollouts get rollout myapp -n production --watch

# Check preview service
kubectl port-forward -n production svc/myapp-preview 8081:80
curl http://localhost:8081

# Promote to production (manual)
kubectl argo rollouts promote myapp -n production

# Verify active service
kubectl port-forward -n production svc/myapp-active 8080:80
curl http://localhost:8080
```

### Automated Promotion with Analysis

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:v1.0.0
        ports:
        - containerPort: 8080
  strategy:
    blueGreen:
      activeService: myapp-active
      previewService: myapp-preview
      autoPromotionEnabled: false
      # Pre-promotion analysis
      prePromotionAnalysis:
        templates:
        - templateName: smoke-tests
        - templateName: performance-tests
        args:
        - name: service-name
          value: myapp-preview
      # Post-promotion analysis
      postPromotionAnalysis:
        templates:
        - templateName: monitoring
        args:
        - name: service-name
          value: myapp-active
---
# Analysis Template - Smoke Tests
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: smoke-tests
  namespace: production
spec:
  args:
  - name: service-name
  metrics:
  - name: smoke-test
    provider:
      job:
        spec:
          template:
            spec:
              containers:
              - name: smoke-test
                image: curlimages/curl:latest
                command:
                - /bin/sh
                - -c
                - |
                  curl -f http://{{args.service-name}}/health && \
                  curl -f http://{{args.service-name}}/api/status
              restartPolicy: Never
          backoffLimit: 1
---
# Analysis Template - Performance
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: performance-tests
  namespace: production
spec:
  args:
  - name: service-name
  metrics:
  - name: response-time
    provider:
      prometheus:
        address: http://prometheus.monitoring:9090
        query: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket{
              service="{{args.service-name}}"
            }[5m])) by (le)
          )
    successCondition: result < 0.5
    interval: 30s
    count: 5
```

---

## Automation Scripts

### Bash Script for Blue-Green Switch

```bash
#!/bin/bash
# blue-green-switch.sh

set -e

NAMESPACE=${1:-production}
APP_NAME=${2:-myapp}
NEW_VERSION=${3:-green}

echo "Starting blue-green deployment for $APP_NAME in $NAMESPACE"

# Current active version
CURRENT_VERSION=$(kubectl get service $APP_NAME -n $NAMESPACE \
  -o jsonpath='{.spec.selector.version}')

echo "Current version: $CURRENT_VERSION"
echo "New version: $NEW_VERSION"

# Verify new deployment is ready
echo "Checking new deployment readiness..."
kubectl wait --for=condition=available \
  --timeout=300s \
  deployment/${APP_NAME}-${NEW_VERSION} \
  -n $NAMESPACE

# Get ready replicas
READY_REPLICAS=$(kubectl get deployment ${APP_NAME}-${NEW_VERSION} \
  -n $NAMESPACE \
  -o jsonpath='{.status.readyReplicas}')

echo "Ready replicas: $READY_REPLICAS"

if [ "$READY_REPLICAS" -lt 1 ]; then
  echo "ERROR: New deployment not ready"
  exit 1
fi

# Run smoke tests
echo "Running smoke tests..."
kubectl run smoke-test-$RANDOM \
  --image=curlimages/curl \
  --rm -i --restart=Never \
  -n $NAMESPACE \
  -- curl -f http://${APP_NAME}-${NEW_VERSION}/health

if [ $? -ne 0 ]; then
  echo "ERROR: Smoke tests failed"
  exit 1
fi

echo "Smoke tests passed"

# Switch traffic
echo "Switching traffic to $NEW_VERSION..."
kubectl patch service $APP_NAME -n $NAMESPACE \
  -p "{\"spec\":{\"selector\":{\"version\":\"$NEW_VERSION\"}}}"

echo "Traffic switched successfully"

# Wait and verify
sleep 10

echo "Verifying new version is serving traffic..."
NEW_ACTIVE_VERSION=$(kubectl get service $APP_NAME -n $NAMESPACE \
  -o jsonpath='{.spec.selector.version}')

if [ "$NEW_ACTIVE_VERSION" != "$NEW_VERSION" ]; then
  echo "ERROR: Traffic switch verification failed"
  exit 1
fi

echo "Blue-green deployment completed successfully"
echo "Active version: $NEW_ACTIVE_VERSION"
echo "Previous version ($CURRENT_VERSION) is still running and can be used for rollback"
```

### Rollback Script

```bash
#!/bin/bash
# rollback.sh

set -e

NAMESPACE=${1:-production}
APP_NAME=${2:-myapp}

echo "Rolling back $APP_NAME in $NAMESPACE"

# Get current version
CURRENT_VERSION=$(kubectl get service $APP_NAME -n $NAMESPACE \
  -o jsonpath='{.spec.selector.version}')

# Determine previous version
if [ "$CURRENT_VERSION" == "blue" ]; then
  PREVIOUS_VERSION="green"
else
  PREVIOUS_VERSION="blue"
fi

echo "Current version: $CURRENT_VERSION"
echo "Rolling back to: $PREVIOUS_VERSION"

# Verify previous deployment exists and is ready
if ! kubectl get deployment ${APP_NAME}-${PREVIOUS_VERSION} -n $NAMESPACE &> /dev/null; then
  echo "ERROR: Previous deployment not found"
  exit 1
fi

# Switch back
echo "Switching traffic to $PREVIOUS_VERSION..."
kubectl patch service $APP_NAME -n $NAMESPACE \
  -p "{\"spec\":{\"selector\":{\"version\":\"$PREVIOUS_VERSION\"}}}"

echo "Rollback completed"
echo "Active version: $PREVIOUS_VERSION"
```

---

## Monitoring and Validation

### Health Check Script

```python
#!/usr/bin/env python3
# health-check.py

import requests
import time
import sys

def check_health(url, expected_version, timeout=300):
    """Check if service is healthy and serving correct version"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=5)

            if response.status_code == 200:
                data = response.json()

                if data.get('version') == expected_version:
                    print(f"✓ Service healthy, version: {expected_version}")
                    return True
                else:
                    print(f"✗ Version mismatch: {data.get('version')} != {expected_version}")

        except Exception as e:
            print(f"Health check failed: {e}")

        time.sleep(5)

    print("Health check timeout")
    return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: health-check.py <url> <expected_version>")
        sys.exit(1)

    url = sys.argv[1]
    version = sys.argv[2]

    if check_health(url, version):
        sys.exit(0)
    else:
        sys.exit(1)
```

### Prometheus Queries for Validation

```promql
# Request success rate per version
sum(rate(http_requests_total{status=~"2.."}[5m])) by (version)
/
sum(rate(http_requests_total[5m])) by (version)

# Response time per version
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, version)
)

# Error rate comparison
sum(rate(http_requests_total{status=~"5.."}[5m])) by (version)
```

---

## Best Practices

### 1. Database Compatibility
```sql
-- Ensure schema is backward compatible

-- BAD: Breaking change
ALTER TABLE users DROP COLUMN legacy_field;

-- GOOD: Expand-contract pattern
-- Deploy green with code that doesn't use legacy_field
-- Later, drop column in separate migration
```

### 2. Pre-Production Validation
```bash
# Comprehensive testing before switch
./run-smoke-tests.sh
./run-integration-tests.sh
./run-performance-tests.sh
./verify-database-migrations.sh
```

### 3. Gradual Traffic Shifting (Hybrid)
```yaml
# Use weighted routing for safer rollout
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  http:
  - route:
    - destination:
        host: myapp
        subset: blue
      weight: 90
    - destination:
        host: myapp
        subset: green
      weight: 10
```

### 4. Resource Management
```yaml
# Ensure both environments can run simultaneously
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi

# Use node affinity to spread across nodes
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchLabels:
            app: myapp
        topologyKey: kubernetes.io/hostname
```

---

## Troubleshooting

### Issue: Service not switching
```bash
# Check service selector
kubectl get service myapp -n production -o yaml | grep -A 5 selector

# Check pod labels
kubectl get pods -n production --show-labels

# Verify endpoints
kubectl get endpoints myapp -n production
```

### Issue: Both versions receiving traffic
```bash
# Check for multiple services
kubectl get services -n production -l app=myapp

# Check ingress/virtual service configuration
kubectl get ingress -n production
kubectl get virtualservice -n production
```

### Issue: New version not ready
```bash
# Check pod status
kubectl get pods -n production -l version=green

# Check events
kubectl get events -n production --sort-by='.lastTimestamp'

# Check logs
kubectl logs -n production -l version=green --tail=100
```

---

## Summary

Blue-green deployments on Kubernetes provide:
- Zero-downtime deployments
- Instant rollback capability
- Full production testing before switch
- Clear rollback path

Choose the method that fits your infrastructure:
- **Label switching**: Simple, works everywhere
- **Ingress**: Good for HTTP/HTTPS traffic
- **Istio**: Advanced traffic management
- **Argo Rollouts**: Automated with analysis

---

## Resources

- Kubernetes Services: https://kubernetes.io/docs/concepts/services-networking/service/
- Argo Rollouts: https://argoproj.github.io/argo-rollouts/
- Istio Traffic Management: https://istio.io/latest/docs/concepts/traffic-management/
- Martin Fowler - Blue-Green: https://martinfowler.com/bliki/BlueGreenDeployment.html
