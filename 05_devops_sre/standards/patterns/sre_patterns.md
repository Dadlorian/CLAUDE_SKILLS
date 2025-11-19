# Site Reliability Engineering Patterns

**Production-proven patterns from Google, Netflix, Amazon, and tier-1 organizations**

---

## Overview

This document catalogs battle-tested SRE patterns that solve common reliability, scalability, and operational challenges. Each pattern includes context, implementation guidance, and real-world examples.

---

## Reliability Patterns

### 1. Circuit Breaker

**Problem**: Cascading failures when downstream services are degraded or unavailable

**Solution**: Automatically detect failures and "open the circuit" to fail fast

**Implementation**:
```go
// Example: Circuit Breaker in Go
type CircuitBreaker struct {
    maxFailures    int
    resetTimeout   time.Duration
    state          State // Closed, Open, HalfOpen
    failures       int
    lastFailTime   time.Time
}

func (cb *CircuitBreaker) Call(fn func() error) error {
    if cb.state == Open {
        if time.Since(cb.lastFailTime) > cb.resetTimeout {
            cb.state = HalfOpen
        } else {
            return errors.New("circuit breaker is open")
        }
    }

    err := fn()

    if err != nil {
        cb.failures++
        cb.lastFailTime = time.Now()

        if cb.failures >= cb.maxFailures {
            cb.state = Open
        }
        return err
    }

    // Success: reset failures
    if cb.state == HalfOpen {
        cb.state = Closed
    }
    cb.failures = 0
    return nil
}
```

**Configuration**:
- **Failure Threshold**: 5-10 consecutive failures (adjust based on traffic)
- **Reset Timeout**: 30-60 seconds (give downstream time to recover)
- **Half-Open State**: Test with single request before fully closing circuit

**Real-World Example** (Netflix Hystrix):
- Protects against latency and failure from dependencies
- Isolates failure in thread pools
- Provides fallback mechanisms
- Real-time monitoring of circuit state

**References**:
- "Release It!" by Michael Nygard
- Netflix Hystrix: https://github.com/Netflix/Hystrix

---

### 2. Bulkhead Isolation

**Problem**: One degraded dependency consuming all resources, affecting unrelated functionality

**Solution**: Isolate resources (threads, connections, memory) for different components

**Implementation**:
```yaml
# Kubernetes: Resource limits per workload
apiVersion: v1
kind: Pod
metadata:
  name: api-server
spec:
  containers:
  - name: api
    resources:
      requests:
        memory: "256Mi"
        cpu: "500m"
      limits:
        memory: "512Mi"
        cpu: "1000m"
```

**Connection Pool Bulkheads**:
```python
# Separate connection pools for different services
db_pool_auth = create_pool(
    max_connections=20,
    database="auth"
)

db_pool_billing = create_pool(
    max_connections=50,  # Critical path gets more resources
    database="billing"
)

db_pool_analytics = create_pool(
    max_connections=10,  # Less critical
    database="analytics"
)
```

**Real-World Example** (Amazon):
- Separate thread pools for different API operations
- Critical operations (checkout) get guaranteed capacity
- Non-critical operations (recommendations) can't starve critical paths

**References**:
- "Release It!" - Stability Patterns
- AWS Well-Architected Framework: Reliability Pillar

---

### 3. Retry with Exponential Backoff and Jitter

**Problem**: Transient failures and thundering herd on retries

**Solution**: Retry with increasing delays and randomization

**Implementation**:
```python
import random
import time

def retry_with_backoff(func, max_retries=5, base_delay=1, max_delay=60):
    """
    Retry function with exponential backoff and jitter

    Based on AWS Architecture Blog:
    https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    """
    for attempt in range(max_retries):
        try:
            return func()
        except RetryableException as e:
            if attempt == max_retries - 1:
                raise  # Final attempt failed

            # Exponential backoff: 1s, 2s, 4s, 8s, 16s, ...
            delay = min(base_delay * (2 ** attempt), max_delay)

            # Add jitter: randomize between 0 and calculated delay
            # Prevents thundering herd
            jittered_delay = random.uniform(0, delay)

            print(f"Attempt {attempt + 1} failed. Retrying in {jittered_delay:.2f}s")
            time.sleep(jittered_delay)
```

**Best Practices**:
- Only retry on transient errors (network, 5xx, timeouts)
- Don't retry on client errors (4xx except 429 Too Many Requests)
- Set max retry limits to prevent infinite loops
- Use jitter to prevent synchronized retries
- Implement circuit breakers as fallback

**Real-World Example** (AWS SDK):
- Default retry strategy for all AWS API calls
- Exponential backoff with jitter
- Respects Retry-After headers
- Configurable retry policies

---

### 4. Graceful Degradation

**Problem**: Complete service failure when dependencies are unavailable

**Solution**: Provide reduced functionality rather than complete failure

**Implementation Examples**:

**Stale Cache on Database Failure**:
```python
def get_user_profile(user_id):
    try:
        # Try fresh data from database
        return db.query("SELECT * FROM users WHERE id = ?", user_id)
    except DatabaseException:
        # Fallback to cached data (even if stale)
        cached = cache.get(f"user:{user_id}")
        if cached:
            logger.warn(f"Serving stale user data for {user_id}")
            return cached

        # Final fallback: minimal default profile
        return {
            "id": user_id,
            "name": "User",
            "status": "unavailable"
        }
```

**Feature Flags for Progressive Degradation**:
```python
def get_recommendations(user_id):
    if feature_flags.is_enabled("ml_recommendations"):
        try:
            return ml_service.get_recommendations(user_id)
        except Exception:
            feature_flags.disable("ml_recommendations")  # Auto-disable on failure
            logger.error("ML service failed, falling back to simple recommendations")

    # Fallback: simple popularity-based recommendations
    return db.query("SELECT * FROM popular_items LIMIT 10")
```

**Real-World Example** (Netflix):
- Homepage shows cached content if recommendation service fails
- Continues playback with lower quality if CDN is degraded
- Disables non-critical features (ratings, reviews) to preserve core experience

**References**:
- "Release It!" - Stability Antipatterns
- Netflix Tech Blog: "Embracing Failure"

---

### 5. Health Checks and Readiness Probes

**Problem**: Traffic routed to unhealthy instances causing errors

**Solution**: Comprehensive health checks with liveness and readiness separation

**Implementation**:
```go
// Liveness Probe: Is the application running?
// Failure: Restart the container
func livenessHandler(w http.ResponseWriter, r *http.Request) {
    // Simple check: is the process alive?
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("alive"))
}

// Readiness Probe: Is the application ready to serve traffic?
// Failure: Remove from load balancer
func readinessHandler(w http.ResponseWriter, r *http.Request) {
    checks := []HealthCheck{
        checkDatabaseConnection(),
        checkRedisConnection(),
        checkDiskSpace(),
        checkMemoryUsage(),
    }

    allHealthy := true
    for _, check := range checks {
        if !check.Healthy {
            allHealthy = false
            break
        }
    }

    if allHealthy {
        w.WriteHeader(http.StatusOK)
        json.NewEncoder(w).Encode(map[string]string{"status": "ready"})
    } else {
        w.WriteHeader(http.StatusServiceUnavailable)
        json.NewEncoder(w).Encode(map[string]string{"status": "not ready"})
    }
}
```

**Kubernetes Configuration**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: api-server
spec:
  containers:
  - name: api
    image: api:latest
    livenessProbe:
      httpGet:
        path: /health/live
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 2
```

**Best Practices**:
- Liveness checks should be simple (just "is process alive?")
- Readiness checks verify dependencies (database, cache, downstream services)
- Set appropriate timeouts (3-5 seconds)
- Avoid expensive operations in health checks
- Consider startup probes for slow-starting applications

**Real-World Example** (Kubernetes):
- Liveness probes restart stuck containers
- Readiness probes remove unhealthy pods from service load balancing
- Startup probes handle slow initialization without killing the pod

---

## Observability Patterns

### 6. Structured Logging

**Problem**: Unstructured logs are hard to parse and query

**Solution**: JSON-formatted logs with consistent fields

**Implementation**:
```python
import json
import logging
from datetime import datetime

class StructuredLogger:
    def __init__(self, service_name):
        self.service_name = service_name

    def log(self, level, message, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "service": self.service_name,
            "message": message,
            **kwargs  # Additional context
        }
        print(json.dumps(log_entry))

    def info(self, message, **kwargs):
        self.log("INFO", message, **kwargs)

    def error(self, message, error=None, **kwargs):
        log_data = kwargs.copy()
        if error:
            log_data["error"] = str(error)
            log_data["error_type"] = type(error).__name__
        self.log("ERROR", message, **log_data)

# Usage
logger = StructuredLogger("api-service")

logger.info(
    "User login successful",
    user_id=12345,
    ip_address="192.168.1.1",
    duration_ms=234
)

logger.error(
    "Database query failed",
    error=exception,
    query="SELECT * FROM users",
    duration_ms=5000,
    user_id=12345
)
```

**Output**:
```json
{
  "timestamp": "2025-11-19T14:23:45.123Z",
  "level": "INFO",
  "service": "api-service",
  "message": "User login successful",
  "user_id": 12345,
  "ip_address": "192.168.1.1",
  "duration_ms": 234
}
```

**Key Fields** (Consistent across all logs):
- `timestamp`: ISO 8601 format
- `level`: DEBUG, INFO, WARN, ERROR, FATAL
- `service`: Service name
- `message`: Human-readable description
- `trace_id`: Distributed tracing ID (correlate logs across services)
- `user_id`: User context (if applicable)
- `request_id`: Unique request identifier

**Real-World Example** (Google Cloud Logging):
- Structured logs automatically indexed
- Query by any field: `level=ERROR AND duration_ms>1000`
- Correlate logs across services using trace_id

---

### 7. RED Method Metrics

**Problem**: Too many metrics, unclear which indicate problems

**Solution**: Focus on Request rate, Error rate, Duration

**Implementation** (Prometheus):
```python
from prometheus_client import Counter, Histogram, generate_latest

# Request Rate
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Error Rate
http_requests_failed = Counter(
    'http_requests_failed_total',
    'Failed HTTP requests',
    ['method', 'endpoint', 'error_type']
)

# Duration
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
)

# Instrument your code
@app.route('/api/users/<user_id>')
def get_user(user_id):
    start_time = time.time()

    try:
        user = fetch_user(user_id)
        http_requests_total.labels(
            method='GET',
            endpoint='/api/users',
            status='200'
        ).inc()

        return jsonify(user), 200

    except UserNotFound:
        http_requests_total.labels(
            method='GET',
            endpoint='/api/users',
            status='404'
        ).inc()
        return jsonify({"error": "Not found"}), 404

    except Exception as e:
        http_requests_failed.labels(
            method='GET',
            endpoint='/api/users',
            error_type=type(e).__name__
        ).inc()
        return jsonify({"error": "Internal error"}), 500

    finally:
        duration = time.time() - start_time
        http_request_duration_seconds.labels(
            method='GET',
            endpoint='/api/users'
        ).observe(duration)
```

**Grafana Queries**:
```promql
# Request Rate (requests per second)
rate(http_requests_total[5m])

# Error Rate (percentage)
rate(http_requests_failed_total[5m]) / rate(http_requests_total[5m]) * 100

# Duration (p50, p95, p99)
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

**Alerting** (SLO-based):
```yaml
# Error rate too high
alert: HighErrorRate
expr: |
  (rate(http_requests_failed_total[5m]) / rate(http_requests_total[5m])) > 0.01
for: 5m
annotations:
  summary: "Error rate above 1% for 5 minutes"

# Latency degraded
alert: HighLatency
expr: |
  histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1.0
for: 5m
annotations:
  summary: "p99 latency above 1 second"
```

**Real-World Example** (Google SRE):
- RED metrics are the foundation of SLI monitoring
- Alert on symptoms (user impact), not causes
- Combine with USE method (Utilization, Saturation, Errors) for resources

**References**:
- "Site Reliability Engineering" - Google SRE Book, Chapter 6
- Tom Wilkie's "The RED Method": https://grafana.com/blog/2018/08/02/the-red-method-how-to-instrument-your-services/

---

### 8. Distributed Tracing

**Problem**: Debugging microservice interactions is complex

**Solution**: Trace requests across service boundaries

**Implementation** (OpenTelemetry):
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Instrument your code
@app.route('/api/checkout')
def checkout():
    with tracer.start_as_current_span("checkout") as span:
        span.set_attribute("user.id", user_id)
        span.set_attribute("cart.items", len(cart_items))

        # Call inventory service
        with tracer.start_as_current_span("check_inventory"):
            inventory_available = inventory_service.check(cart_items)

        # Call payment service
        with tracer.start_as_current_span("process_payment"):
            payment_result = payment_service.charge(user_id, total)

        # Call shipping service
        with tracer.start_as_current_span("create_shipment"):
            shipment = shipping_service.create(user_id, cart_items)

        return {"order_id": order_id}
```

**Trace Context Propagation** (HTTP Headers):
```python
import requests

# Propagate trace context to downstream services
headers = {
    "traceparent": f"00-{trace_id}-{span_id}-01",
    "tracestate": "vendor=state"
}
response = requests.get("https://api.example.com/users", headers=headers)
```

**What Traces Reveal**:
- End-to-end request latency breakdown
- Service dependencies and call patterns
- Critical path identification
- Error propagation across services
- Resource consumption per operation

**Real-World Example** (Uber):
- Traces every request across 1000+ microservices
- Identifies performance bottlenecks in complex workflows
- Correlates traces with logs and metrics
- Custom Jaeger implementation for scale

**References**:
- OpenTelemetry: https://opentelemetry.io/
- Jaeger Documentation: https://www.jaegertracing.io/docs/

---

## Deployment Patterns

### 9. Blue-Green Deployment

**Problem**: Minimize downtime and enable instant rollback

**Solution**: Maintain two identical environments, switch traffic atomically

**Implementation** (Kubernetes):
```yaml
# Blue deployment (current production)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
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
      - name: app
        image: myapp:v1.0

---
# Green deployment (new version)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-green
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
      - name: app
        image: myapp:v2.0

---
# Service: Switch traffic by changing selector
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: myapp
    version: blue  # Change to "green" to switch traffic
  ports:
  - port: 80
    targetPort: 8080
```

**Deployment Process**:
1. Deploy green environment with new version
2. Test green environment (smoke tests, health checks)
3. Switch traffic from blue to green (update service selector)
4. Monitor green for issues (15-30 minutes)
5. If issues: switch back to blue instantly
6. If stable: delete blue environment (or keep for next deployment)

**Pros**:
- Instant rollback (just change selector)
- Zero downtime
- Full testing in production-like environment before cutover

**Cons**:
- Requires 2x resources temporarily
- Database migrations need to be backward-compatible
- Not suitable for stateful applications without planning

**Real-World Example** (AWS Elastic Beanstalk):
- Built-in blue-green deployment
- Creates new environment with new version
- Swaps CNAMEs to switch traffic
- Keeps old environment for rollback

---

### 10. Canary Deployment

**Problem**: Reduce blast radius of bad deployments

**Solution**: Gradually roll out to increasing percentages of traffic

**Implementation** (Istio):
```yaml
# VirtualService: Route 90% to v1, 10% to v2
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: app-vs
spec:
  hosts:
  - app-service
  http:
  - match:
    - headers:
        user-type:
          exact: internal  # Internal users get canary
    route:
    - destination:
        host: app-service
        subset: v2
      weight: 100
  - route:
    - destination:
        host: app-service
        subset: v1
      weight: 90  # Stable version
    - destination:
        host: app-service
        subset: v2
      weight: 10  # Canary version
```

**Progressive Rollout**:
```bash
# Stage 1: 10% canary (monitor for 30 min)
kubectl apply -f canary-10pct.yaml
# Monitor metrics, logs, errors

# Stage 2: 50% canary (monitor for 30 min)
kubectl apply -f canary-50pct.yaml
# Monitor metrics, logs, errors

# Stage 3: 100% canary (complete rollout)
kubectl apply -f canary-100pct.yaml
# v2 is now production, v1 is deprecated
```

**Automated Canary Analysis** (Flagger):
```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: app-canary
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  service:
    port: 8080
  analysis:
    interval: 1m
    threshold: 5  # Number of failed checks before rollback
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99  # Rollback if success rate < 99%
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500  # Rollback if p99 latency > 500ms
      interval: 1m
```

**Monitoring During Canary**:
```promql
# Compare error rates between versions
rate(http_requests_failed_total{version="v1"}[5m]) /
rate(http_requests_total{version="v1"}[5m])

rate(http_requests_failed_total{version="v2"}[5m]) /
rate(http_requests_total{version="v2"}[5m])
```

**Real-World Example** (Netflix Spinnaker):
- Automated canary analysis with configurable metrics
- Progressive rollout stages (1% → 5% → 10% → 25% → 50% → 100%)
- Automatic rollback on regression
- Integration with monitoring and alerting

**References**:
- Netflix: "Automated Canary Analysis at Netflix"
- Flagger: https://flagger.app/

---

## Incident Response Patterns

### 11. Incident Command System (ICS)

**Problem**: Chaotic incident response with unclear responsibilities

**Solution**: Structured roles and communication during incidents

**Roles**:

**Incident Commander (IC)**
- Owns overall incident response coordination
- Makes decisions on escalation and strategy
- Delegates tasks to responders
- Does NOT directly troubleshoot (coordinates others)

**Communications Lead (Comms)**
- Provides status updates to stakeholders
- Updates external status page
- Manages war room communication
- Shields IC from interruptions

**Technical Lead (TL)**
- Investigates root cause
- Implements fixes and mitigations
- Coordinates with other engineers
- Reports findings to IC

**Scribe**
- Documents timeline of events
- Records actions taken and decisions made
- Notes key observations and data
- Prepares post-mortem draft

**Incident Declaration**:
```
Title: API Error Rate Spike
Severity: SEV-2
Impact: 15% of users seeing errors
Commander: @jane (on-call SRE)
Comms: @john (eng manager)
Tech Lead: @alice (backend engineer)
Scribe: @bob (junior SRE)
War Room: #incident-2025-11-19-api-errors
Status Page: Updated (Investigating)
```

**Communication Cadence**:
- Initial update: Within 15 minutes of incident start
- Regular updates: Every 30 minutes until resolved
- Final update: Resolution message + ETA for post-mortem

**Real-World Example** (PagerDuty Incident Response):
- Automated role assignment based on escalation policies
- Built-in status page integration
- War room creation (Slack, Zoom)
- Post-incident report generation

**References**:
- Google SRE Book: "Managing Incidents"
- Incident Management for Operations (PagerDuty)

---

## Scaling Patterns

### 12. Horizontal Pod Autoscaling (HPA)

**Problem**: Manual scaling is slow and reactive

**Solution**: Automatically scale based on metrics

**Implementation** (Kubernetes):
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  minReplicas: 3
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Scale when avg CPU > 70%
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"  # Scale at 1000 RPS per pod
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
      - type: Percent
        value: 50  # Scale down max 50% of pods at once
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0  # Scale up immediately
      policies:
      - type: Percent
        value: 100  # Double pods if needed
        periodSeconds: 15
```

**Custom Metrics** (Prometheus Adapter):
```yaml
# Scale based on request queue depth
- seriesQuery: 'queue_depth{namespace="production"}'
  resources:
    overrides:
      namespace: {resource: "namespace"}
      pod: {resource: "pod"}
  name:
    matches: "^(.*)$"
    as: "queue_depth"
  metricsQuery: 'avg_over_time(queue_depth{<<.LabelMatchers>>}[2m])'
```

**Best Practices**:
- Set appropriate min/max replicas (3-100 is typical)
- Use multiple metrics (CPU, memory, custom)
- Configure scale-down stabilization to prevent flapping
- Test autoscaling under load (load testing)
- Monitor scaling events and adjust thresholds

**Real-World Example** (Airbnb):
- HPA based on custom application metrics (request queue depth)
- Scales from 10 to 500 pods during peak traffic
- Combined with Cluster Autoscaler for node-level scaling
- Saved 30% on infrastructure costs

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Maintained by**: SRE Team

For more patterns, see:
- Google SRE Book: https://sre.google/sre-book/
- "Release It!" by Michael Nygard
- Netflix Tech Blog: https://netflixtechblog.com/
