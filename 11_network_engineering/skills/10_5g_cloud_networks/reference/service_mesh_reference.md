# Service Mesh Reference

## Service Mesh Fundamentals

A service mesh is a dedicated infrastructure layer that handles service-to-service communication in microservices architectures, providing traffic management, security, and observability.

## Core Concepts

### Control Plane
- **API server** - Resource management
- **Configuration distribution** - Policy propagation
- **Certificate management** - mTLS certificates
- **Telemetry aggregation** - Metrics collection

### Data Plane
- **Sidecar proxies** - Per-pod proxy injection
- **Traffic interception** - Transparent proxy
- **Policy enforcement** - Rules application
- **Metric collection** - Traffic telemetry

## Istio Service Mesh

### Architecture

**Control Plane Components**
- **Istiod** - Unified control plane
  - Pilot: Service discovery, configuration
  - Citadel: Certificate management
  - Galley: Configuration validation

**Data Plane**
- **Envoy proxy** - High-performance proxy
- **sidecar injection** - Automatic or manual
- **iptables rules** - Traffic redirection

### Traffic Management

#### VirtualService
**Routing rules for subsets**
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
    - uri:
        prefix: /v2
    route:
    - destination:
        host: reviews
        subset: v2
  - route:
    - destination:
        host: reviews
        subset: v1
```

**Features**
- Canary deployments
- A/B testing
- Circuit breaker integration
- Timeout/retry configuration

#### DestinationRule
**Load balancing and circuit breaker policies**
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
        http1MaxPendingRequests: 100
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

#### Gateway & VirtualService
**Ingress traffic management**
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
    - "bookinfo.com"
```

### Security

#### RequestAuthentication
**JWT validation**
```yaml
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-authn
spec:
  jwtRules:
  - issuer: "https://example.com"
    jwksUri: "https://example.com/.well-known/jwks.json"
```

#### AuthorizationPolicy
**Fine-grained access control**
```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-get
spec:
  selector:
    matchLabels:
      app: httpbin
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/sleep"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/status", "/delay/*"]
```

#### Mutual TLS (mTLS)
- **Automatic mTLS** - Between all services
- **Certificate rotation** - Automatic
- **Enforcement policies** - Strict/permissive modes
- **Peer authentication** - mTLS configuration

### Observability

#### Metrics
- **Request metrics** - Volume, latency, errors
- **Connection metrics** - Opened, closed
- **Envoy metrics** - Proxy statistics
- **Scrape format** - Prometheus-compatible

#### Distributed Tracing
- **Jaeger integration** - Trace collection
- **Trace propagation** - Header forwarding
- **Span generation** - Per service
- **Sampling policies** - Configurable sampling

#### Logs
- **Access logs** - Request/response logs
- **Proxy logs** - Envoy diagnostics
- **Control plane logs** - Istiod logs
- **Log aggregation** - ELK, Loki integration

### Service Mesh Gateway

**IngressGateway**
- External traffic entry point
- TLS termination
- Virtual host routing
- Protocol support (HTTP, TCP, gRPC)

**EgressGateway**
- Outbound traffic control
- Destination restriction
- Egress TLS termination
- Egress traffic monitoring

## Linkerd Service Mesh

### Lightweight Architecture
- **Data plane** - Lightweight proxy written in Rust
- **Control plane** - Minimal resource overhead
- **Simpler API** - Less configuration
- **Fast adoption** - Quicker deployment

### Core Features

**Traffic Management**
- Automatic load balancing
- Automatic retries
- Connection pooling
- Timeouts

**Security**
- Automatic mTLS
- Automatic certificate rotation
- Fine-grained policy
- Kubernetes-native

**Observability**
- Out-of-box metrics
- Live tap functionality
- Golden metrics (latency, throughput, errors)
- Real-time dashboards

### Traffic Policy
```yaml
apiVersion: policy.linkerd.io/v1beta1
kind: TrafficPolicy
metadata:
  name: example
  namespace: default
spec:
  targetRef:
    group: core
    kind: Namespace
    name: default
  routes:
  - name: default
    isRetry: true
    timeout: 5s
    backoff:
      minBackoff: 10ms
      maxBackoff: 10s
      jitterFraction: 0.25
```

## Comparing Service Meshes

### Feature Comparison

| Feature | Istio | Linkerd | Consul |
|---------|-------|---------|--------|
| Data Plane | Envoy | Linkerd-proxy | Envoy/Native |
| Control Plane | Complex | Lightweight | Distributed |
| Learning Curve | Steep | Moderate | Moderate |
| Resource Usage | High | Low | Medium |
| mTLS | Yes | Yes | Yes |
| Policies | Advanced | Simple | Advanced |

### Use Case Selection

**Choose Istio When:**
- Complex traffic routing needed
- Multi-cluster networking required
- Advanced observability required
- Multiple protocols (HTTP, gRPC, TCP)

**Choose Linkerd When:**
- Lightweight deployment preferred
- Quick time-to-value needed
- Resource constraints exist
- Kubernetes-native approach desired

## Service Mesh Patterns

### Canary Deployments
1. Route small % to new version
2. Monitor metrics
3. Gradually increase traffic
4. Full rollout or rollback

**Implementation**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: app
spec:
  hosts:
  - app
  http:
  - match:
    - headers:
        user-type:
          exact: beta
    route:
    - destination:
        host: app
        subset: v2
  - route:
    - destination:
        host: app
        subset: v1
      weight: 95
    - destination:
        host: app
        subset: v2
      weight: 5
```

### Circuit Breaking
- **Consecutive errors** - Trip circuit
- **Request volume** - Minimum threshold
- **Time windows** - Recovery intervals
- **Host ejection** - Remove failing instances

### Retry Policies
- **Automatic retries** - Failed requests
- **Exponential backoff** - Increasing delays
- **Max retries** - Limit attempts
- **Retry-able errors** - Specific status codes

## Observability Integration

### Prometheus Integration
- Envoy metrics export
- Service mesh metrics
- Custom metrics collection
- Scrape configuration

### Grafana Dashboards
- Out-of-box dashboards
- Custom visualizations
- Alert configuration
- Multi-cluster views

### Jaeger Tracing
- Distributed trace collection
- Service dependency mapping
- Latency analysis
- Error tracking

## Best Practices

### Deployment
- Start with single cluster
- Implement gradually
- Monitor before scaling
- Plan for complexity

### Configuration
- Use minimal policies initially
- Gradually add complexity
- Version control all configs
- Regular audits

### Performance
- Monitor resource usage
- Tune proxy settings
- Monitor proxy latency
- Right-size infrastructure

### Security
- Enable mTLS everywhere
- Implement authorization policies
- Regular certificate validation
- Audit access logs

### Observability
- Collect all metrics
- Configure sampling appropriately
- Implement alerting
- Regular review of traces

---

**Reference:** Istio Documentation, Linkerd Documentation
**Last Updated:** 2025-11-19
