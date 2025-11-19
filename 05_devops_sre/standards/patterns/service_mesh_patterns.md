# Service Mesh Patterns

## Table of Contents
- [Introduction to Service Mesh](#introduction-to-service-mesh)
- [Istio Patterns](#istio-patterns)
- [Linkerd Patterns](#linkerd-patterns)
- [Traffic Management Patterns](#traffic-management-patterns)
- [Security Patterns](#security-patterns)
- [Observability Patterns](#observability-patterns)
- [Resilience Patterns](#resilience-patterns)

---

## Introduction to Service Mesh

A service mesh provides:
- **Traffic Management**: Intelligent routing, load balancing, traffic splitting
- **Security**: mTLS, authorization, authentication
- **Observability**: Metrics, traces, logs
- **Resilience**: Retries, timeouts, circuit breaking

### When to Use a Service Mesh

**Use When**:
- Microservices architecture with 10+ services
- Need for mTLS without application changes
- Complex traffic routing requirements
- Advanced observability needs
- Multi-cluster or multi-cloud deployments

**Avoid When**:
- Simple monolithic applications
- Less than 5 microservices
- Team lacks operational maturity
- Performance overhead is critical concern

---

## Istio Patterns

### 1. Traffic Splitting Pattern (Canary with Istio)

**Use Case**: Gradual rollout with percentage-based traffic distribution

**Pattern**:
```yaml
# Gateway for external traffic
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: app-gateway
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
    - "app.example.com"
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: app-tls-cert
    hosts:
    - "app.example.com"

---
# DestinationRule defining service subsets
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: app-destination
  namespace: production
spec:
  host: app-service
  trafficPolicy:
    loadBalancer:
      consistentHash:
        httpCookie:
          name: user-session
          ttl: 3600s
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2

---
# VirtualService for traffic routing
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: app-routes
  namespace: production
spec:
  hosts:
  - "app.example.com"
  - app-service
  gateways:
  - app-gateway
  - mesh  # For internal traffic
  http:
  - match:
    - headers:
        user-type:
          exact: "beta-tester"
    route:
    - destination:
        host: app-service
        subset: v2
  - route:
    - destination:
        host: app-service
        subset: v1
      weight: 90
    - destination:
        host: app-service
        subset: v2
      weight: 10
```

**Progressive Rollout Steps**:
```bash
# Step 1: 10% to v2
kubectl apply -f virtualservice-10-90.yaml

# Monitor metrics
istioctl dashboard grafana

# Step 2: 50% to v2
kubectl patch virtualservice app-routes --type merge -p '
spec:
  http:
  - route:
    - destination:
        host: app-service
        subset: v1
      weight: 50
    - destination:
        host: app-service
        subset: v2
      weight: 50'

# Step 3: 100% to v2
kubectl patch virtualservice app-routes --type merge -p '
spec:
  http:
  - route:
    - destination:
        host: app-service
        subset: v2
      weight: 100'
```

---

### 2. Circuit Breaking Pattern

**Use Case**: Prevent cascade failures, protect upstream services

**Pattern**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: backend-circuit-breaker
  namespace: production
spec:
  host: backend-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100  # Max TCP connections
      http:
        http1MaxPendingRequests: 50  # Max queued requests
        http2MaxRequests: 100  # Max parallel requests
        maxRequestsPerConnection: 2  # Requests per connection
        maxRetries: 3  # Max concurrent retries
    outlierDetection:
      consecutiveErrors: 5  # Errors before ejection
      interval: 30s  # Detection interval
      baseEjectionTime: 30s  # Min ejection duration
      maxEjectionPercent: 50  # Max % of hosts to eject
      minHealthPercent: 40  # Min healthy hosts required
```

**Testing**:
```bash
# Generate load to trigger circuit breaker
kubectl run -it --rm load-generator \
  --image=busybox --restart=Never -- /bin/sh -c \
  "while true; do wget -q -O- http://backend-service; done"

# Check circuit breaker stats
istioctl proxy-config cluster <pod-name> --fqdn backend-service -o json | \
  jq '.outlierDetection'
```

---

### 3. Request Timeout and Retry Pattern

**Use Case**: Handle slow services, transient failures

**Pattern**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: backend-resilience
  namespace: production
spec:
  hosts:
  - backend-service
  http:
  - route:
    - destination:
        host: backend-service
    timeout: 10s  # Total request timeout
    retries:
      attempts: 3
      perTryTimeout: 3s
      retryOn: 5xx,reset,connect-failure,refused-stream
    fault:
      delay:
        percentage:
          value: 0.1  # 10% of requests
        fixedDelay: 5s  # Chaos testing
```

---

### 4. mTLS Security Pattern

**Use Case**: Automatic mutual TLS between services

**Pattern**:
```yaml
# Namespace-wide strict mTLS
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT  # or PERMISSIVE for gradual migration

---
# Authorization Policy
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: backend-authz
  namespace: production
spec:
  selector:
    matchLabels:
      app: backend
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/frontend-sa"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]

---
# Deny all by default
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: production
spec:
  {}  # Empty spec denies all traffic
```

**mTLS Migration Strategy**:
```yaml
# Step 1: PERMISSIVE mode (allows both mTLS and plaintext)
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: PERMISSIVE

# Step 2: Monitor traffic
# Check if any plaintext connections exist
istioctl authn tls-check <pod-name> backend-service

# Step 3: Switch to STRICT
# (update mode to STRICT in above resource)
```

---

### 5. Multi-Cluster Pattern

**Use Case**: Cross-cluster service discovery and routing

**Pattern**:
```yaml
# ServiceEntry for remote cluster service
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: external-cluster-service
  namespace: production
spec:
  hosts:
  - api.cluster2.local
  location: MESH_EXTERNAL
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  resolution: DNS
  endpoints:
  - address: api.cluster2.example.com
    ports:
      https: 443

---
# VirtualService for cross-cluster routing
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: multi-cluster-routing
spec:
  hosts:
  - api-service
  http:
  - match:
    - headers:
        region:
          exact: "us-west"
    route:
    - destination:
        host: api-service  # Local cluster
  - route:
    - destination:
        host: api.cluster2.local  # Remote cluster
```

---

### 6. Request Mirroring (Dark Traffic) Pattern

**Use Case**: Test new versions with production traffic without affecting users

**Pattern**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: app-mirror
  namespace: production
spec:
  hosts:
  - app-service
  http:
  - route:
    - destination:
        host: app-service
        subset: v1
      weight: 100
    mirror:
      host: app-service
      subset: v2  # Mirror to v2
    mirrorPercentage:
      value: 100.0  # Percentage of requests to mirror
```

**Use Cases**:
- Test performance of new version
- Validate behavior with real traffic
- Load testing without user impact
- Compare metrics between versions

---

## Linkerd Patterns

### 1. Service Profile Pattern

**Use Case**: Per-route metrics and traffic policies

**Pattern**:
```yaml
apiVersion: linkerd.io/v1alpha2
kind: ServiceProfile
metadata:
  name: backend-service.production.svc.cluster.local
  namespace: production
spec:
  routes:
  - name: GET /api/users
    condition:
      method: GET
      pathRegex: /api/users
    timeout: 1000ms
    retryBudget:
      retryRatio: 0.2
      minRetriesPerSecond: 10
      ttl: 10s
  - name: POST /api/orders
    condition:
      method: POST
      pathRegex: /api/orders
    timeout: 5000ms
    isRetryable: false  # Don't retry POST requests
  - name: GET /api/products
    condition:
      method: GET
      pathRegex: /api/products/.*
    timeout: 2000ms
```

**Creating ServiceProfile from Swagger**:
```bash
# Generate ServiceProfile from OpenAPI spec
linkerd profile --open-api swagger.yaml backend-service \
  --namespace production | kubectl apply -f -
```

---

### 2. Traffic Split Pattern (SMI)

**Use Case**: Canary deployments using SMI standard

**Pattern**:
```yaml
# TrafficSplit resource (SMI)
apiVersion: split.smi-spec.io/v1alpha1
kind: TrafficSplit
metadata:
  name: backend-split
  namespace: production
spec:
  service: backend-service
  backends:
  - service: backend-v1
    weight: 900  # 90%
  - service: backend-v2
    weight: 100  # 10%

---
# Services for each version
apiVersion: v1
kind: Service
metadata:
  name: backend-v1
  namespace: production
spec:
  selector:
    app: backend
    version: v1
  ports:
  - port: 8080

---
apiVersion: v1
kind: Service
metadata:
  name: backend-v2
  namespace: production
spec:
  selector:
    app: backend
    version: v2
  ports:
  - port: 8080
```

---

### 3. mTLS with Policy Pattern

**Use Case**: Automatic mTLS with fine-grained control

**Pattern**:
```yaml
# Server configuration
apiVersion: policy.linkerd.io/v1beta1
kind: Server
metadata:
  name: backend-server
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  port: http
  proxyProtocol: HTTP/2

---
# Authorization Policy
apiVersion: policy.linkerd.io/v1beta1
kind: ServerAuthorization
metadata:
  name: backend-authz
  namespace: production
spec:
  server:
    name: backend-server
  client:
    meshTLS:
      serviceAccounts:
      - name: frontend-sa
        namespace: production
      - name: api-gateway-sa
        namespace: production

---
# Default deny
apiVersion: policy.linkerd.io/v1alpha1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: production
spec:
  targetRef:
    kind: Namespace
    name: production
  requiredAuthenticationRefs: []
```

---

### 4. Multi-Cluster Gateway Pattern

**Use Case**: Cross-cluster communication with Linkerd

**Pattern**:
```bash
# Link clusters
linkerd multicluster link --cluster-name cluster1 | \
  kubectl apply -f - --context=cluster2

# Export service from cluster1
kubectl label svc/backend-service -n production \
  mirror.linkerd.io/exported=true --context=cluster1

# Service is now available in cluster2 as:
# backend-service-cluster1.production.svc.cluster.local
```

```yaml
# Use exported service in cluster2
apiVersion: v1
kind: Service
metadata:
  name: backend-aggregator
  namespace: production
spec:
  type: ClusterIP
  ports:
  - port: 8080

---
apiVersion: v1
kind: Endpoints
metadata:
  name: backend-aggregator
  namespace: production
subsets:
- addresses:
  - ip: <backend-service-cluster1-ip>
  ports:
  - port: 8080
```

---

## Traffic Management Patterns

### 1. Header-Based Routing Pattern

**Use Case**: Route based on user type, API version, or feature flags

**Istio Implementation**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: header-routing
spec:
  hosts:
  - api-service
  http:
  # Route premium users to high-performance backend
  - match:
    - headers:
        user-tier:
          exact: "premium"
    route:
    - destination:
        host: api-service
        subset: high-perf
  # Route API v2 requests
  - match:
    - headers:
        api-version:
          prefix: "v2"
    route:
    - destination:
        host: api-service
        subset: v2
  # Default route
  - route:
    - destination:
        host: api-service
        subset: v1
```

---

### 2. Geographic Routing Pattern

**Use Case**: Route to nearest region for latency optimization

**Pattern**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: geo-routing
spec:
  hosts:
  - api-service
  http:
  - match:
    - sourceLabels:
        topology.kubernetes.io/region: us-west-2
    route:
    - destination:
        host: api-service
        subset: us-west
  - match:
    - sourceLabels:
        topology.kubernetes.io/region: us-east-1
    route:
    - destination:
        host: api-service
        subset: us-east
  - route:  # Default
    - destination:
        host: api-service
        subset: us-west
      weight: 50
    - destination:
        host: api-service
        subset: us-east
      weight: 50

---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: api-geo-subsets
spec:
  host: api-service
  subsets:
  - name: us-west
    labels:
      region: us-west
  - name: us-east
    labels:
      region: us-east
```

---

### 3. Load Balancing Patterns

**Consistent Hash Load Balancing** (Sticky Sessions):
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: sticky-session
spec:
  host: app-service
  trafficPolicy:
    loadBalancer:
      consistentHash:
        httpCookie:
          name: session-id
          ttl: 3600s
```

**Locality-Based Load Balancing**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: locality-lb
spec:
  host: app-service
  trafficPolicy:
    loadBalancer:
      localityLbSetting:
        enabled: true
        distribute:
        - from: us-west-2/*
          to:
            "us-west-2/*": 80
            "us-east-1/*": 20
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
```

---

## Security Patterns

### 1. JWT Authentication Pattern

**Use Case**: Validate JWT tokens at mesh level

**Pattern**:
```yaml
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: production
spec:
  selector:
    matchLabels:
      app: api-gateway
  jwtRules:
  - issuer: "https://auth.example.com"
    jwksUri: "https://auth.example.com/.well-known/jwks.json"
    audiences:
    - "api.example.com"
    forwardOriginalToken: true

---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: require-jwt
  namespace: production
spec:
  selector:
    matchLabels:
      app: api-gateway
  action: ALLOW
  rules:
  - from:
    - source:
        requestPrincipals: ["*"]  # Any valid JWT
    to:
    - operation:
        paths: ["/api/*"]
  - to:
    - operation:
        paths: ["/health", "/metrics"]  # Public endpoints
```

---

### 2. Rate Limiting Pattern

**Use Case**: Protect services from excessive requests

**Pattern** (using Envoy rate limit):
```yaml
apiVersion: networking.istio.io/v1beta1
kind: EnvoyFilter
metadata:
  name: rate-limit-filter
  namespace: istio-system
spec:
  workloadSelector:
    labels:
      istio: ingressgateway
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: GATEWAY
      listener:
        filterChain:
          filter:
            name: "envoy.filters.network.http_connection_manager"
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.ratelimit
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.ratelimit.v3.RateLimit
          domain: production-ratelimit
          failure_mode_deny: false
          rate_limit_service:
            grpc_service:
              envoy_grpc:
                cluster_name: rate_limit_cluster
            transport_api_version: V3

---
# VirtualService with rate limit action
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-ratelimit
spec:
  hosts:
  - api.example.com
  http:
  - match:
    - uri:
        prefix: "/api"
    route:
    - destination:
        host: api-service
    headers:
      request:
        set:
          x-envoy-ratelimit-descriptor: user-id
```

---

## Observability Patterns

### 1. Distributed Tracing Pattern

**Use Case**: End-to-end request tracing

**Pattern**:
```yaml
# Istio telemetry configuration
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: tracing-default
  namespace: istio-system
spec:
  tracing:
  - providers:
    - name: jaeger
    randomSamplingPercentage: 100.0
    customTags:
      environment:
        literal:
          value: "production"
      version:
        header:
          name: "x-app-version"

---
# Application should propagate trace headers:
# - x-request-id
# - x-b3-traceid
# - x-b3-spanid
# - x-b3-parentspanid
# - x-b3-sampled
# - x-b3-flags
```

---

### 2. Custom Metrics Pattern

**Use Case**: Application-specific metrics

**Istio Implementation**:
```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: custom-metrics
  namespace: production
spec:
  metrics:
  - providers:
    - name: prometheus
    dimensions:
      request_path:
        value: "request.path"
      response_status:
        value: "response.code"
      api_version:
        value: "request.headers['x-api-version'] | 'unknown'"
    overrides:
    - match:
        metric: REQUEST_COUNT
      tagOverrides:
        request_path:
          operation: UPSERT
```

---

## Resilience Patterns

### 1. Bulkhead Pattern

**Use Case**: Isolate critical resources

**Pattern**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: bulkhead-pattern
spec:
  host: database-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 10  # Limit connections
      http:
        http1MaxPendingRequests: 5
        http2MaxRequests: 10
        maxRequestsPerConnection: 1
```

---

### 2. Fallback Pattern

**Use Case**: Graceful degradation

**Pattern**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: fallback-pattern
spec:
  hosts:
  - recommendation-service
  http:
  - timeout: 3s
    route:
    - destination:
        host: recommendation-service
    retries:
      attempts: 2
      perTryTimeout: 1s
    fault:
      abort:
        percentage:
          value: 0  # Can inject failures for testing
        httpStatus: 503
  - match:
    - sourceLabels:
        app: frontend
    route:
    - destination:
        host: recommendation-cache  # Fallback service
```

---

## Best Practices

### 1. Gradual Rollout Strategy

1. **Enable sidecar injection**: `kubectl label namespace production istio-injection=enabled`
2. **Deploy with permissive mTLS**: Test without breaking existing traffic
3. **Enable metrics**: Monitor before making routing changes
4. **Implement circuit breakers**: Protect against cascading failures
5. **Add timeouts and retries**: Improve resilience
6. **Enable strict mTLS**: After validating all services
7. **Add authorization policies**: Fine-grained access control

### 2. Performance Considerations

- **Sidecar overhead**: 1-3ms latency, 50-100MB memory per pod
- **mTLS overhead**: ~10% CPU increase
- **Control plane**: Size appropriately (3 replicas minimum)
- **Use HTTP/2**: Better performance than HTTP/1.1

### 3. Troubleshooting

```bash
# Istio
istioctl analyze -n production
istioctl proxy-config routes <pod> -o json
istioctl dashboard kiali

# Linkerd
linkerd check
linkerd viz stat deploy -n production
linkerd viz tap deploy/frontend

# Common issues
kubectl describe pod <pod> | grep -A 10 Events
kubectl logs <pod> -c istio-proxy
```

---

## Summary

Service meshes provide powerful capabilities for microservices architectures:

- **Traffic Management**: Sophisticated routing, load balancing, traffic splitting
- **Security**: Zero-trust networking with mTLS and authorization
- **Observability**: Automatic metrics, tracing, and visualization
- **Resilience**: Circuit breaking, retries, timeouts, failover

Choose Istio for feature richness and flexibility; choose Linkerd for simplicity and performance.
