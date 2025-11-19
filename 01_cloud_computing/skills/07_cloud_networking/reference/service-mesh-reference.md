# Service Mesh Reference

## Introduction

A service mesh is a dedicated infrastructure layer for managing service-to-service communication in microservices architectures. It provides traffic management, security, observability, and resilience without requiring application code changes.

## Service Mesh Fundamentals

### What is a Service Mesh?

**Core Concept**:
```
Service A --> Sidecar Proxy --> Sidecar Proxy --> Service B

Data Plane: Sidecar proxies (Envoy)
Control Plane: Configuration and policy management
```

**Key Capabilities**:
- Traffic management (routing, load balancing, retries)
- Security (mTLS, authentication, authorization)
- Observability (metrics, logs, traces)
- Resilience (circuit breaking, timeouts, retries)
- Service discovery

### Why Service Mesh?

**Problems Solved**:
- Complex service-to-service communication
- Distributed security policies
- Lack of visibility into service interactions
- Manual implementation of resilience patterns
- Inconsistent observability across services

**Benefits**:
- Zero-trust security
- Fine-grained traffic control
- Comprehensive observability
- Platform-agnostic
- Reduces code complexity

## Architecture Patterns

### Sidecar Pattern

**Deployment**:
```
Pod (Kubernetes)
  |
  +-- Application Container
  |
  +-- Envoy Sidecar Proxy

All traffic flows through sidecar
Transparent to application
```

**Benefits**:
- No application code changes
- Language agnostic
- Independent scaling
- Isolated failure domain

### Control Plane vs Data Plane

**Control Plane**:
```
Responsibilities:
- Configuration distribution
- Service discovery
- Certificate management
- Policy enforcement
- Telemetry collection

Components (Istio):
- Pilot: Traffic management
- Citadel: Certificate management
- Galley: Configuration validation
```

**Data Plane**:
```
Responsibilities:
- Request routing
- Load balancing
- Health checking
- Authentication/Authorization
- Metrics collection

Implementation: Envoy Proxy
```

## Istio

### Architecture

**Istio Components**:
```
istiod (Control Plane)
  |
  +-- Pilot: Service discovery, traffic management
  |
  +-- Citadel: Certificate authority
  |
  +-- Galley: Configuration management

Envoy Sidecars (Data Plane)
  |
  +-- Proxy all traffic
  |
  +-- Enforce policies
  |
  +-- Collect telemetry
```

### Traffic Management

**Virtual Service**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        end-user:
          exact: jason
    route:
    - destination:
        host: reviews
        subset: v2
  - route:
    - destination:
        host: reviews
        subset: v1
```

**Destination Rule**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews
spec:
  host: reviews
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
  trafficPolicy:
    loadBalancer:
      simple: ROUND_ROBIN
```

### Traffic Splitting (Canary)

**Progressive Rollout**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - route:
    - destination:
        host: reviews
        subset: v1
      weight: 90
    - destination:
        host: reviews
        subset: v2
      weight: 10
```

### Circuit Breaking

**Resilience Pattern**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews
spec:
  host: reviews
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 1
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 40
```

### Retries and Timeouts

**Automatic Retry**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - route:
    - destination:
        host: reviews
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: 5xx,reset,connect-failure
    timeout: 10s
```

### mTLS (Mutual TLS)

**Automatic Encryption**:
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: default
spec:
  mtls:
    mode: STRICT
```

**Modes**:
- **STRICT**: mTLS required
- **PERMISSIVE**: mTLS and plaintext allowed
- **DISABLE**: No mTLS

### Authorization Policies

**Fine-Grained Access Control**:
```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: httpbin
  namespace: default
spec:
  selector:
    matchLabels:
      app: httpbin
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/sleep"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/info*"]
  - to:
    - operation:
        methods: ["GET"]
        paths: ["/health"]
```

### Ingress Gateway

**Edge Traffic Management**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: httpbin-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "httpbin.example.com"

---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: httpbin
spec:
  hosts:
  - "httpbin.example.com"
  gateways:
  - httpbin-gateway
  http:
  - route:
    - destination:
        host: httpbin
        port:
          number: 8000
```

### Egress Gateway

**Outbound Traffic Control**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: external-svc-https
spec:
  hosts:
  - api.external.com
  location: MESH_EXTERNAL
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  resolution: DNS
```

## Linkerd

### Architecture

**Linkerd Components**:
```
Control Plane:
- controller: Core control plane
- web: Dashboard
- prometheus: Metrics storage
- grafana: Visualization

Data Plane:
- linkerd-proxy: Rust-based proxy
```

### Automatic mTLS

**Zero-Config Encryption**:
```bash
# Inject Linkerd proxy
linkerd inject deployment.yaml | kubectl apply -f -

# Automatic mTLS between services
# No configuration needed
```

### Traffic Split

**SMI TrafficSplit**:
```yaml
apiVersion: split.smi-spec.io/v1alpha1
kind: TrafficSplit
metadata:
  name: reviews-split
spec:
  service: reviews
  backends:
  - service: reviews-v1
    weight: 900m
  - service: reviews-v2
    weight: 100m
```

### Service Profiles

**Per-Route Metrics**:
```yaml
apiVersion: linkerd.io/v1alpha2
kind: ServiceProfile
metadata:
  name: reviews.default.svc.cluster.local
  namespace: default
spec:
  routes:
  - name: GET /api/v1/reviews
    condition:
      method: GET
      pathRegex: /api/v1/reviews
    timeout: 10s
    retries:
      limit: 3
      budget: 0.2
```

### Tap

**Real-Time Traffic Inspection**:
```bash
# Watch live requests
linkerd tap deploy/web -n default

# Filter by resource
linkerd tap deploy/web --to deploy/reviews

# Filter by status
linkerd tap deploy/web --to deploy/reviews --path /api/v1/reviews
```

## AWS App Mesh

### Architecture

**App Mesh Components**:
```
Service Mesh
  |
  +-- Virtual Services (DNS names)
  |
  +-- Virtual Nodes (Task groups)
  |
  +-- Virtual Routers (Traffic routing)
  |
  +-- Routes (Routing rules)

Envoy Proxy (Data plane)
```

### Virtual Service

**Service Abstraction**:
```json
{
  "meshName": "my-mesh",
  "spec": {
    "provider": {
      "virtualRouter": {
        "virtualRouterName": "reviews-router"
      }
    }
  },
  "virtualServiceName": "reviews.default.svc.cluster.local"
}
```

### Virtual Node

**Service Endpoint**:
```json
{
  "meshName": "my-mesh",
  "spec": {
    "backends": [
      {
        "virtualService": {
          "virtualServiceName": "database.default.svc.cluster.local"
        }
      }
    ],
    "listeners": [
      {
        "portMapping": {
          "port": 8080,
          "protocol": "http"
        }
      }
    ],
    "serviceDiscovery": {
      "dns": {
        "hostname": "reviews.default.svc.cluster.local"
      }
    }
  },
  "virtualNodeName": "reviews-v1"
}
```

### Route Configuration

**Weighted Routing**:
```json
{
  "meshName": "my-mesh",
  "spec": {
    "httpRoute": {
      "action": {
        "weightedTargets": [
          {
            "virtualNode": "reviews-v1",
            "weight": 90
          },
          {
            "virtualNode": "reviews-v2",
            "weight": 10
          }
        ]
      },
      "match": {
        "prefix": "/"
      },
      "retryPolicy": {
        "httpRetryEvents": ["server-error"],
        "maxRetries": 3,
        "perRetryTimeout": {
          "unit": "s",
          "value": 2
        }
      }
    }
  },
  "routeName": "reviews-route",
  "virtualRouterName": "reviews-router"
}
```

## Google Traffic Director

### Architecture

**Global Load Balancing + Service Mesh**:
```
Traffic Director (Control Plane)
  |
Envoy Proxies (Data Plane)
  |
+-- Sidecar mode (GKE)
|
+-- Standalone mode (VMs, GCE)
```

### Service Routing

**URL Map Configuration**:
```yaml
defaultService: backend-service
hostRules:
- hosts:
  - "api.example.com"
  pathMatcher: api-matcher
pathMatchers:
- name: api-matcher
  defaultService: api-service-v1
  routeRules:
  - priority: 0
    matchRules:
    - prefixMatch: "/v2/"
    routeAction:
      weightedBackendServices:
      - backendService: api-service-v2
        weight: 100
```

## Service Mesh Interface (SMI)

### Standard APIs

**Traffic Specs**:
```yaml
apiVersion: specs.smi-spec.io/v1alpha4
kind: HTTPRouteGroup
metadata:
  name: the-routes
spec:
  matches:
  - name: metrics
    pathRegex: "/metrics"
    methods:
    - GET
  - name: everything
    pathRegex: ".*"
    methods: ["*"]
```

**Traffic Split**:
```yaml
apiVersion: split.smi-spec.io/v1alpha1
kind: TrafficSplit
metadata:
  name: website-split
spec:
  service: website
  backends:
  - service: website-v1
    weight: 80
  - service: website-v2
    weight: 20
```

**Traffic Metrics**:
```yaml
apiVersion: metrics.smi-spec.io/v1alpha1
kind: TrafficMetrics
metadata:
  name: website-metrics
spec:
  resource:
    kind: Deployment
    name: website
    namespace: default
```

## Observability

### Distributed Tracing

**Jaeger Integration**:
```
Application generates trace spans
  |
Envoy proxy adds trace headers
  |
Traces sent to Jaeger
  |
End-to-end request visualization
```

**Trace Context Propagation**:
```
Required headers:
- x-request-id
- x-b3-traceid
- x-b3-spanid
- x-b3-parentspanid
- x-b3-sampled
- x-b3-flags
```

### Metrics

**Golden Signals**:
```
Latency:
- p50, p95, p99 response time
- Request duration histogram

Traffic:
- Requests per second
- Request rate by method/path

Errors:
- Error rate (4xx, 5xx)
- Success rate

Saturation:
- Connection pool utilization
- Queue depth
```

**Prometheus Metrics**:
```
istio_requests_total
istio_request_duration_milliseconds
istio_request_bytes
istio_response_bytes
istio_tcp_connections_opened_total
```

### Service Graph

**Topology Visualization**:
```
Service A --> Service B --> Service C
            \          \
             \          --> Service D
              \
               --> Service E

Traffic volume
Error rates
Latency
```

## Security

### Zero Trust Architecture

**Principles**:
- Never trust, always verify
- Least privilege access
- Encrypt all traffic
- Authenticate all services
- Authorize all requests

**Implementation**:
```
1. Mutual TLS for all service-to-service
2. Strong service identity
3. Authorization policies
4. Certificate rotation
5. Audit logging
```

### Identity and SPIFFE

**SPIFFE (Secure Production Identity Framework)**:
```
Service Identity: spiffe://cluster.local/ns/default/sa/reviews

X.509 certificates
Automatic rotation
Platform-agnostic
```

### Policy Enforcement

**AuthorizationPolicy Example**:
```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: frontend-policy
spec:
  selector:
    matchLabels:
      app: frontend
  action: ALLOW
  rules:
  - from:
    - source:
        namespaces: ["prod"]
    to:
    - operation:
        methods: ["GET", "POST"]
    when:
    - key: request.auth.claims[group]
      values: ["admin"]
```

## Advanced Patterns

### Multi-Cluster Service Mesh

**Federated Mesh**:
```
Cluster 1 (us-east-1)
    |
    +-- Istio Control Plane
    |
    +-- Services A, B

Cluster 2 (eu-west-1)
    |
    +-- Istio Control Plane
    |
    +-- Services C, D

Service discovery across clusters
Unified policy management
```

### Hybrid Mesh (VMs + Kubernetes)

**VM Integration**:
```
Kubernetes Cluster
    |
    +-- Service A (Pod)
    |
Service Mesh
    |
Virtual Machine
    |
    +-- Service B (VM with Envoy)

Unified service discovery
Consistent policies
```

### Egress Control

**External Service Access**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: external-api
spec:
  hosts:
  - api.external.com
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  location: MESH_EXTERNAL
  resolution: DNS

---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: external-api
spec:
  host: api.external.com
  trafficPolicy:
    tls:
      mode: SIMPLE
```

## Performance Optimization

### Resource Management

**Sidecar Resource Limits**:
```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi
```

### Connection Pooling

**HTTP Connection Pool**:
```yaml
trafficPolicy:
  connectionPool:
    http:
      http1MaxPendingRequests: 1024
      http2MaxRequests: 1024
      maxRequestsPerConnection: 10
      maxRetries: 3
```

### Locality-Aware Load Balancing

**Prioritize Local Traffic**:
```yaml
trafficPolicy:
  loadBalancer:
    localityLbSetting:
      enabled: true
      distribute:
      - from: us-east-1a
        to:
          "us-east-1a": 80
          "us-east-1b": 20
```

## Troubleshooting

### Common Issues

**503 Service Unavailable**:
```
Causes:
- Circuit breaker triggered
- Connection pool exhausted
- Upstream service down
- Misconfigured virtual service

Debug:
- Check Envoy logs
- Verify destination rule
- Review circuit breaker settings
```

**mTLS Errors**:
```
Causes:
- Certificate mismatch
- Strict mode without sidecar
- Certificate rotation issues

Debug:
- Check PeerAuthentication
- Verify sidecar injection
- Review certificate logs
```

**High Latency**:
```
Causes:
- Proxy overhead
- Resource constraints
- Complex routing rules
- External service latency

Debug:
- Analyze distributed traces
- Check proxy resources
- Simplify routing rules
```

### Diagnostic Tools

**Istio Commands**:
```bash
# Check proxy status
istioctl proxy-status

# Get proxy configuration
istioctl proxy-config routes deploy/productpage

# Analyze mesh configuration
istioctl analyze

# Debug authorization
istioctl experimental authz check
```

## Best Practices

### Deployment

1. Start with permissive mTLS, migrate to strict
2. Inject sidecars selectively (namespace labels)
3. Resource limit sidecars appropriately
4. Test in non-production first
5. Gradual rollout with traffic splitting

### Security

1. Enable mTLS in strict mode
2. Implement authorization policies
3. Rotate certificates regularly
4. Audit access regularly
5. Use service accounts for identity

### Operations

1. Monitor golden signals
2. Set up distributed tracing
3. Alert on error rate spikes
4. Regular configuration audits
5. Keep service mesh updated

### Performance

1. Optimize resource allocation
2. Use connection pooling
3. Implement circuit breakers
4. Enable locality-aware load balancing
5. Monitor proxy resource usage

## Conclusion

Service mesh provides powerful capabilities for managing microservices communication, security, and observability. Choose the right service mesh based on your platform, implement gradually, and follow best practices for production deployments.
