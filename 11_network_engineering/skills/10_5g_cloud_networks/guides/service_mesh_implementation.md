# Service Mesh Implementation Guide

## Service Mesh Selection & Planning

### Comparison Matrix

```
Metric              | Istio        | Linkerd       | Consul
Performance         | Moderate     | High          | Moderate
Complexity          | High         | Low           | Moderate
Resource Usage      | High         | Low           | Medium
Learning Curve      | Steep        | Shallow       | Moderate
Multi-cluster       | Yes          | Yes           | Yes
```

### Implementation Decision

**Choose Istio for:** Complex routing, multi-protocol, advanced observability
**Choose Linkerd for:** Lightweight, fast deployment, Kubernetes-native
**Choose Consul for:** Multi-cloud, complex policies, service discovery

## Step 1: Istio Installation

### Prerequisites

```bash
# Check Kubernetes version
kubectl version --short

# Check available resources
kubectl top nodes
kubectl top pods -A

# Verify metrics server
kubectl get deployment metrics-server -n kube-system
```

### Install Istio

```bash
# Download Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-1.16.0

# Add istioctl to PATH
export PATH=$PWD/bin:$PATH

# Install Istio with default profile
istioctl install --set profile=demo -y

# Verify installation
kubectl get pods -n istio-system
kubectl get crd | grep istio

# Enable sidecar injection
kubectl label namespace default istio-injection=enabled
```

## Step 2: Configure Kubernetes Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    istio-injection: enabled
    monitoring: "true"
```

## Step 3: Deploy Sample Application

### Application Deployment

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: production
  labels:
    app: api
spec:
  ports:
  - port: 8080
    name: http
  selector:
    app: api
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
      version: v1
  template:
    metadata:
      labels:
        app: api
        version: v1
    spec:
      containers:
      - name: api
        image: myapp/api:v1
        ports:
        - containerPort: 8080
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-v2
  namespace: production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
      version: v2
  template:
    metadata:
      labels:
        app: api
        version: v2
    spec:
      containers:
      - name: api
        image: myapp/api:v2
```

## Step 4: Configure Traffic Management

### Virtual Service for Canary Deployment

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api
  namespace: production
spec:
  hosts:
  - api
  http:
  # Route traffic by header
  - match:
    - headers:
        user-type:
          exact: beta
    route:
    - destination:
        host: api
        subset: v2
      weight: 100
  # Default routing
  - route:
    - destination:
        host: api
        subset: v1
      weight: 90
    - destination:
        host: api
        subset: v2
      weight: 10
  timeout: 30s
  retries:
    attempts: 3
    perTryTimeout: 10s
```

### Destination Rule for Load Balancing

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: api
  namespace: production
spec:
  host: api
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 1000
      http:
        http1MaxPendingRequests: 1000
        http2MaxRequests: 1000
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minRequestVolume: 5
      splitExternalLocalOriginErrors: true
    loadBalancer:
      round_robin: {}
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
    trafficPolicy:
      connectionPool:
        tcp:
          maxConnections: 500
```

## Step 5: Configure Ingress

### Istio Ingress Gateway

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: api-gateway
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
    - "api.example.com"
    - "*.api.example.com"
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: api-cert
    hosts:
    - "api.example.com"
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-routes
  namespace: production
spec:
  hosts:
  - "api.example.com"
  gateways:
  - api-gateway
  http:
  - match:
    - uri:
        prefix: /v1
    route:
    - destination:
        host: api
        subset: v1
        port:
          number: 8080
  - match:
    - uri:
        prefix: /v2
    route:
    - destination:
        host: api
        subset: v2
        port:
          number: 8080
  - route:
    - destination:
        host: api
        port:
          number: 8080
```

## Step 6: Configure Security

### Mutual TLS

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT  # Enforce mTLS for all services
---
# Allow specific services to use plaintext
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: allow-plaintext-probes
  namespace: production
spec:
  selector:
    matchLabels:
      app: api
  mtls:
    mode: PERMISSIVE  # Allow both mTLS and plaintext
  portLevelMtls:
    8090:
      mode: DISABLE  # Health check port
```

### Authorization Policy

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-api-access
  namespace: production
spec:
  selector:
    matchLabels:
      app: api
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/frontend"]
      namespaces: ["production"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/v1/*", "/api/v2/*"]
  - from:
    - source:
        namespaces: ["monitoring"]
    to:
    - operation:
        ports: ["8090"]  # Metrics port
---
# Default deny all
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: default-deny
  namespace: production
spec:
  {}
```

## Step 7: Configure Observability

### Monitoring with Prometheus

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: istio-system
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'istio-mesh'
      kubernetes_sd_configs:
      - role: endpoint
        namespaces:
          names:
          - istio-system
          - production
    - job_name: 'envoy-stats'
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - production
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_container_port_name]
        action: keep
        regex: '.*-envoy-prom'
```

### Jaeger Tracing

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mesh-config
  namespace: istio-system
data:
  mesh: |
    enableTracing: true
    defaultConfig:
      tracing:
        zipkin:
          address: jaeger-collector:9411
        sampling: 100.0
```

## Step 8: Deploy & Test

### Deployment

```bash
# Apply all configurations
kubectl apply -f istio-config/

# Verify resources
kubectl get vs -n production
kubectl get dr -n production
kubectl get gateway -n production
kubectl get authorizationpolicy -n production

# Check sidecar injection
kubectl get pods -n production -o jsonpath='{..containerStatuses[?(@.name=="istio-proxy")].imageID}'
```

### Traffic Flow Testing

```bash
# Test canary traffic split
for i in {1..100}; do
  curl -H "user-type: beta" http://api.example.com/api/v1/data
done

# Monitor traffic distribution
istioctl dashboard kiali

# View metrics
kubectl port-forward -n istio-system svc/prometheus 9090:9090
# Access http://localhost:9090

# View traces
kubectl port-forward -n istio-system svc/jaeger 16686:16686
# Access http://localhost:16686
```

## Step 9: Advanced Features

### Request Routing by Headers

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-advanced
  namespace: production
spec:
  hosts:
  - api
  http:
  # Premium users get v2
  - match:
    - headers:
        x-customer-tier:
          exact: premium
    route:
    - destination:
        host: api
        subset: v2
  # Beta testers get v2
  - match:
    - queryParams:
        version:
          exact: beta
    route:
    - destination:
        host: api
        subset: v2
  # Default to v1
  - route:
    - destination:
        host: api
        subset: v1
```

### Rate Limiting

```yaml
apiVersion: config.istio.io/v1alpha2
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: production
spec:
  jwtRules:
  - issuer: "https://auth.example.com"
    jwksUri: "https://auth.example.com/.well-known/jwks.json"
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: rate-limit
  namespace: production
spec:
  selector:
    matchLabels:
      app: api
  rules:
  - from:
    - source:
        requestPrincipals: ["*"]
    to:
    - operation:
        methods: ["GET"]
  rateLimit: &rate_limit
    actions:
    - metadata:
        descriptor_key: "header_match"
```

## Best Practices

1. **Gradual Rollout** - Start with demo profile
2. **Test Policies** - Verify before production
3. **Monitor Metrics** - Track key indicators
4. **Version Control** - Git-track all configs
5. **Document Flows** - Maintain architecture
6. **Secure by Default** - STRICT mTLS
7. **Observability First** - Enable tracing
8. **Resource Limits** - Prevent runaway traffic
9. **Regular Updates** - Keep Istio current
10. **Team Training** - Ensure operator skills

---

**Last Updated:** 2025-11-19
