# Service Mesh Reference

## Service Mesh Overview

### What is a Service Mesh?
A dedicated infrastructure layer for managing service-to-service communication, providing traffic management, security, and observability without changing application code.

### Key Capabilities
- **Traffic Management**: Routing, load balancing, circuit breaking, retries, timeouts
- **Security**: mTLS encryption, authentication, authorization
- **Observability**: Metrics, logs, distributed tracing
- **Resilience**: Fault injection, circuit breaking, retries
- **Policy Enforcement**: Rate limiting, access control

### Architecture Pattern
- **Data Plane**: Sidecar proxies (Envoy, Linkerd proxy) handle traffic
- **Control Plane**: Manages and configures proxies

## Istio

### Architecture Components

**Control Plane** (Istiod):
- Pilot: Service discovery, traffic management
- Citadel: Certificate authority, credential management
- Galley: Configuration validation and distribution (merged into Istiod)

**Data Plane**:
- Envoy proxy: Sidecar proxy for each pod

**Gateways**:
- Ingress Gateway: Entry point for external traffic
- Egress Gateway: Exit point for outbound traffic

### Installation

**istioctl**:
```bash
# Install with default profile
istioctl install --set profile=default

# Install with custom profile
istioctl install --set profile=production \
  --set components.egressGateways[0].enabled=true

# Verify installation
istioctl verify-install
```

**Helm**:
```bash
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm install istio-base istio/base -n istio-system --create-namespace
helm install istiod istio/istiod -n istio-system
helm install istio-ingress istio/gateway -n istio-ingress --create-namespace
```

### Sidecar Injection

**Automatic (namespace label)**:
```bash
kubectl label namespace default istio-injection=enabled
```

**Manual**:
```bash
istioctl kube-inject -f deployment.yaml | kubectl apply -f -
```

**Sidecar Resource**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: Sidecar
metadata:
  name: default
  namespace: production
spec:
  outboundTrafficPolicy:
    mode: REGISTRY_ONLY
  egress:
  - hosts:
    - "./*"
    - "istio-system/*"
```

### Traffic Management

**VirtualService**:
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
      weight: 75
    - destination:
        host: reviews
        subset: v2
      weight: 25
```

**DestinationRule**:
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
        http2MaxRequests: 100
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
    loadBalancer:
      simple: LEAST_REQUEST
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

**Gateway**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: bookinfo-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "bookinfo.example.com"
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: bookinfo-tls
    hosts:
    - "bookinfo.example.com"
```

**ServiceEntry** (external services):
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
```

### Resilience

**Retries**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ratings
spec:
  hosts:
  - ratings
  http:
  - route:
    - destination:
        host: ratings
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: 5xx,reset,connect-failure,refused-stream
```

**Timeouts**:
```yaml
spec:
  http:
  - route:
    - destination:
        host: reviews
    timeout: 10s
```

**Circuit Breaking**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: httpbin
spec:
  host: httpbin
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 1
      http:
        http1MaxPendingRequests: 1
        maxRequestsPerConnection: 1
    outlierDetection:
      consecutive5xxErrors: 1
      interval: 1s
      baseEjectionTime: 3m
      maxEjectionPercent: 100
```

**Fault Injection**:
```yaml
spec:
  http:
  - fault:
      delay:
        percentage:
          value: 10
        fixedDelay: 5s
      abort:
        percentage:
          value: 5
        httpStatus: 500
    route:
    - destination:
        host: ratings
```

### Security

**PeerAuthentication** (mTLS):
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT  # STRICT, PERMISSIVE, DISABLE
```

**RequestAuthentication** (JWT):
```yaml
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: production
spec:
  selector:
    matchLabels:
      app: httpbin
  jwtRules:
  - issuer: "testing@secure.istio.io"
    jwksUri: "https://raw.githubusercontent.com/istio/istio/master/security/tools/jwt/samples/jwks.json"
```

**AuthorizationPolicy**:
```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-read
  namespace: production
spec:
  selector:
    matchLabels:
      app: httpbin
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/frontend"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/api/*"]
    when:
    - key: request.auth.claims[iss]
      values: ["testing@secure.istio.io"]
```

### Observability

**Telemetry API**:
```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: namespace-metrics
  namespace: production
spec:
  metrics:
  - providers:
    - name: prometheus
    dimensions:
      request_path:
        value: request.path
```

**Distributed Tracing**:
```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: tracing
spec:
  tracing:
  - providers:
    - name: jaeger
    randomSamplingPercentage: 100
```

## Linkerd

### Architecture

**Control Plane**:
- Controller: API server and control loops
- Destination: Service discovery and routing
- Identity: Certificate authority
- Proxy Injector: Admission webhook

**Data Plane**:
- linkerd2-proxy: Rust-based ultralight proxy

### Installation

```bash
# Install CLI
curl -sL https://run.linkerd.io/install | sh

# Pre-check
linkerd check --pre

# Install CRDs
linkerd install --crds | kubectl apply -f -

# Install control plane
linkerd install | kubectl apply -f -

# Verify
linkerd check
```

### Proxy Injection

**Automatic**:
```bash
kubectl annotate namespace default linkerd.io/inject=enabled
```

**Manual**:
```bash
kubectl get deploy -o yaml | linkerd inject - | kubectl apply -f -
```

### Traffic Splitting

**TrafficSplit**:
```yaml
apiVersion: split.smi-spec.io/v1alpha2
kind: TrafficSplit
metadata:
  name: backend-split
spec:
  service: backend
  backends:
  - service: backend-v1
    weight: 900
  - service: backend-v2
    weight: 100
```

### Service Profiles

```yaml
apiVersion: linkerd.io/v1alpha2
kind: ServiceProfile
metadata:
  name: webapp.default.svc.cluster.local
spec:
  routes:
  - name: GET /api/users
    condition:
      method: GET
      pathRegex: /api/users
    timeout: 5s
    retryBudget:
      retryRatio: 0.2
      minRetriesPerSecond: 10
      ttl: 10s
  - name: POST /api/users
    condition:
      method: POST
      pathRegex: /api/users
    timeout: 10s
```

### mTLS

**Automatic**: Linkerd automatically enables mTLS between meshed pods

**Policy** (authorization):
```yaml
apiVersion: policy.linkerd.io/v1beta1
kind: Server
metadata:
  name: webapp-server
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: webapp
  port: 8080
  proxyProtocol: HTTP/1
---
apiVersion: policy.linkerd.io/v1beta1
kind: ServerAuthorization
metadata:
  name: webapp-authz
  namespace: default
spec:
  server:
    name: webapp-server
  client:
    meshTLS:
      serviceAccounts:
      - name: frontend
```

### Multi-Cluster

```bash
# Link clusters
linkerd multicluster link --cluster-name target | kubectl apply -f -

# Export service
kubectl label svc/backend mirror.linkerd.io/exported=true
```

## Consul Connect

### Architecture

**Components**:
- Consul Server: Cluster state, service catalog
- Consul Client: Agent on each node
- Envoy Proxy: Sidecar (default) or gateway

### Installation (Helm)

```yaml
global:
  name: consul
  datacenter: dc1
connectInject:
  enabled: true
  default: true
controller:
  enabled: true
```

### Service Defaults

```yaml
apiVersion: consul.hashicorp.com/v1alpha1
kind: ServiceDefaults
metadata:
  name: web
spec:
  protocol: http
```

### Service Intentions

```yaml
apiVersion: consul.hashicorp.com/v1alpha1
kind: ServiceIntentions
metadata:
  name: web
spec:
  destination:
    name: web
  sources:
  - name: frontend
    action: allow
  - name: "*"
    action: deny
```

### Service Router

```yaml
apiVersion: consul.hashicorp.com/v1alpha1
kind: ServiceRouter
metadata:
  name: web
spec:
  routes:
  - match:
      http:
        pathPrefix: /admin
    destination:
      service: admin-web
  - match:
      http:
        header:
        - name: x-debug
          exact: "1"
    destination:
      service: web
      serviceSubset: canary
  - destination:
      service: web
```

### Service Splitter

```yaml
apiVersion: consul.hashicorp.com/v1alpha1
kind: ServiceSplitter
metadata:
  name: web
spec:
  splits:
  - weight: 90
    service: web
    serviceSubset: v1
  - weight: 10
    service: web
    serviceSubset: v2
```

## Service Mesh Comparison

| Feature | Istio | Linkerd | Consul Connect |
|---------|-------|---------|----------------|
| Proxy | Envoy | linkerd2-proxy | Envoy |
| Language | Go, C++ | Rust, Go | Go |
| Resource Usage | High | Low | Medium |
| Complexity | High | Low | Medium |
| Features | Extensive | Core features | Service discovery + mesh |
| Multi-cluster | Yes | Yes | Yes |
| mTLS | Yes | Yes (automatic) | Yes |
| Traffic Management | Advanced | Basic | Good |
| Observability | Extensive | Good | Good |
| Platform Support | Any | Kubernetes-only | Multi-platform |

## Service Mesh Interface (SMI)

### SMI Specs

**TrafficTarget** (access control):
```yaml
apiVersion: access.smi-spec.io/v1alpha3
kind: TrafficTarget
metadata:
  name: api-service-target
spec:
  destination:
    kind: ServiceAccount
    name: api-service
    namespace: default
  rules:
  - kind: HTTPRouteGroup
    name: api-routes
    matches:
    - metrics
  sources:
  - kind: ServiceAccount
    name: prometheus
    namespace: monitoring
```

**TrafficSplit** (canary):
```yaml
apiVersion: split.smi-spec.io/v1alpha2
kind: TrafficSplit
metadata:
  name: api-service-split
spec:
  service: api-service
  backends:
  - service: api-service-stable
    weight: 90
  - service: api-service-canary
    weight: 10
```

**TrafficMetrics**:
```yaml
apiVersion: metrics.smi-spec.io/v1alpha1
kind: TrafficMetrics
metadata:
  name: api-service-metrics
spec:
  resource:
    kind: Deployment
    name: api-service
```

## Best Practices

### Performance
- Right-size sidecar resources
- Enable proxy protocol where possible
- Use connection pooling
- Configure appropriate timeouts
- Monitor resource usage

### Security
- Enable mTLS in STRICT mode
- Implement least-privilege authorization
- Use JWT validation for external requests
- Regular certificate rotation
- Audit authorization policies

### Reliability
- Set appropriate circuit breaker thresholds
- Configure retries for transient failures
- Use outlier detection
- Implement proper timeouts
- Test fault injection scenarios

### Observability
- Enable distributed tracing
- Export metrics to Prometheus
- Configure appropriate sampling rates
- Use service profiles/routes
- Monitor golden signals (latency, traffic, errors, saturation)

### Operations
- Start with permissive mode for mTLS
- Gradual rollout (namespace by namespace)
- Test in non-production first
- Monitor control plane health
- Plan for upgrades
- Document mesh topology

## References

- [Istio Documentation](https://istio.io/latest/docs/)
- [Linkerd Documentation](https://linkerd.io/2/overview/)
- [Consul Connect](https://www.consul.io/docs/connect)
- [Service Mesh Interface (SMI)](https://smi-spec.io/)
- [Envoy Proxy](https://www.envoyproxy.io/)
