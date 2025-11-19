# Microservices Documentation Patterns

## Table of Contents

1. [Overview](#overview)
2. [Core Patterns](#core-patterns)
3. [Service Catalog Documentation](#service-catalog-documentation)
4. [Inter-Service Communication](#inter-service-communication)
5. [Service Mesh Documentation](#service-mesh-documentation)
6. [Dependency Mapping](#dependency-mapping)
7. [Configuration Management](#configuration-management)
8. [Monitoring and Observability](#monitoring-and-observability)
9. [Deployment and Release Notes](#deployment-and-release-notes)
10. [Best Practices](#best-practices)

## Overview

Microservices architectures introduce unique documentation challenges compared to monolithic systems. Each service operates independently while contributing to a larger ecosystem, requiring documentation patterns that capture both service-level and system-level perspectives.

This guide provides comprehensive patterns for documenting microservices-based systems effectively, ensuring that teams can navigate, maintain, and evolve distributed systems with clarity.

## Core Patterns

### Pattern 1: Service Blueprint Template

Every microservice should have a comprehensive blueprint document covering essential information.

```yaml
Service Name: user-authentication-service
Domain: Identity & Access
Owner Team: Platform Security
Version: 2.3.1
Status: Production
Last Updated: 2025-11-19

Purpose:
  Primary: Centralized authentication and authorization provider
  Responsibilities:
    - OAuth 2.0 token generation and validation
    - JWT token lifecycle management
    - User identity verification
    - Multi-factor authentication coordination

Technology Stack:
  Language: Go 1.21
  Runtime: Kubernetes 1.28
  Database: PostgreSQL 15 with TimescaleDB extension
  Message Queue: RabbitMQ for async token revocation events
  Cache: Redis 7.0 for token blacklisting

Dependencies:
  Internal:
    - user-profile-service: v1.2.0
    - notification-service: v2.0.0
  External:
    - Auth0 (backup authentication)
    - SendGrid (email delivery)

Exposed Interfaces:
  - REST API (v2)
  - gRPC services (internal)
  - Event streams (RabbitMQ)

SLA:
  Availability: 99.99%
  Response Time: P95 < 100ms
  Recovery Time: < 5 minutes
```

### Pattern 2: Bounded Context Documentation

Establish clear boundaries for each service's responsibility area.

```markdown
## Order Processing Service - Bounded Context

### Core Entities

- **Order**: Represents a customer's purchase request
  - Aggregates: Items, Pricing, Customer Reference
  - Lifecycle: Draft → Submitted → Confirmed → Shipped → Delivered

- **OrderItem**: Individual product within an order
  - Relationships: Product Catalog Service (external)
  - Immutable once order confirmed

- **OrderStatus**: Enumeration of order states
  - Values: DRAFT, SUBMITTED, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED

### Aggregate Roots

1. **Order (Aggregate Root)**
   - Commands: CreateOrder, ConfirmOrder, CancelOrder, UpdateShippingAddress
   - Events: OrderCreated, OrderConfirmed, OrderCancelled, OrderShipped
   - Invariants:
     - Order cannot be confirmed with zero items
     - Only Draft orders can be modified
     - Cancellation only allowed before shipment

### Domain Events

```json
{
  "event_type": "OrderConfirmed",
  "order_id": "ORD-20251119-001",
  "timestamp": "2025-11-19T14:32:00Z",
  "customer_id": "CUST-12345",
  "total_amount": 299.99,
  "currency": "USD",
  "shipping_address": {
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip": "10001"
  }
}
```

### Ubiquitous Language

- **Order**: Complete customer purchase request with items and delivery details
- **Fulfillment**: Process of preparing and shipping items to customer
- **Backorder**: Item temporarily out of stock, fulfilled when available
- **Cancellation Window**: 24-hour period when order can be cancelled without penalty
```

### Pattern 3: Service Contract Documentation

Document explicit contracts for all service interactions.

```markdown
## Service Contract: Payment Service → Order Service

### Synchronous Call Contract

**Endpoint**: POST /api/v2/payments/authorize

**Request Schema**:
```json
{
  "order_id": "string (36 chars, UUID v4)",
  "amount_cents": "integer (> 0)",
  "currency": "string (ISO 4217, e.g., 'USD')",
  "payment_method": {
    "type": "string (CREDIT_CARD|BANK_TRANSFER|DIGITAL_WALLET)",
    "token": "string (tokenized, never raw card data)"
  },
  "metadata": {
    "customer_id": "string (UUID v4)",
    "transaction_id": "string (idempotency key)",
    "risk_score": "number (0-100)"
  }
}
```

**Response Schema (Success)**: HTTP 200
```json
{
  "authorization_id": "AUTH-20251119-89234",
  "status": "AUTHORIZED",
  "amount_authorized_cents": 29999,
  "expires_at": "2025-11-26T14:32:00Z",
  "processor_reference": "proc_xyz789"
}
```

**Response Schema (Failure)**: HTTP 4xx/5xx
```json
{
  "error_code": "INSUFFICIENT_FUNDS|CARD_DECLINED|PROCESSOR_ERROR",
  "error_message": "Card declined by issuer",
  "request_id": "req-89234",
  "retry_after_seconds": 60
}
```

**Error Handling**:
- 3xx retries: Automatic with exponential backoff
- 4xx client errors: Do not retry; handle in application logic
- 5xx server errors: Retry up to 3 times with 2s base delay
- Network timeouts: Retry up to 2 times; timeout after 30s total

**Rate Limiting**:
- 10,000 requests per minute per API key
- Burst allowance: 500 requests
- Rate limit headers: X-RateLimit-Limit, X-RateLimit-Remaining

**Versioning**:
- Current version: v2
- Supported versions: v1 (deprecated, EOL 2026-06-01), v2
- Migration guide: See [Payment API Migration Guide](./payment-api-migration-v1-v2.md)
```

## Service Catalog Documentation

### Registry Structure

```markdown
# Microservices Registry

## Production Services

### Payment Processing Domain
- **payment-service** (Go, gRPC)
  - Status: ✅ Stable
  - Owner: @platform-payments
  - Endpoint: payment-svc.default.svc.cluster.local:50051
  - Docs: docs/payment-service

- **billing-service** (Node.js, REST)
  - Status: ✅ Stable
  - Owner: @finance-systems
  - Endpoint: https://api.example.com/billing
  - Docs: docs/billing-service

### Customer Management Domain
- **customer-service** (Python, REST + gRPC)
  - Status: ✅ Stable
  - Owner: @customer-platform
  - Database: PostgreSQL (us-east-1a)
  - Docs: docs/customer-service

- **user-preferences-service** (Rust, gRPC)
  - Status: 🟡 Beta
  - Owner: @customer-platform
  - Endpoint: grpc://preferences.default.svc.cluster.local
  - Docs: docs/user-preferences

## Staging Services

### Experimental/Feature Development
- **recommendation-engine** (Python ML, gRPC)
  - Status: 🟠 Alpha
  - Owner: @data-science
  - Feature: ML-based product recommendations
  - Timeline: GA expected Q2 2026
```

### Ownership and Accountability

```markdown
## Service Ownership Model

### Payment Service Ownership

**Primary Owner**: Alice Chen (alice.chen@example.com)
- Responsible for: Design decisions, on-call escalations, major version upgrades
- Office Hours: Tuesdays/Thursdays 2-4 PM ET

**Secondary Owners**:
- Bob Martinez (bob.martinez@example.com) - Database administrator
- Carol Santos (carol.santos@example.com) - Performance optimization

**Team**: Platform Payments (9 engineers)

**Escalation Path**:
1. Primary owner
2. Payment Service Team Lead (Dan Kumar)
3. Platform Engineering Director (Emma Thompson)

**Operational Responsibilities**:
- On-call rotation: 1-week schedules, starts Mondays
- Incident response: P1 within 15 min, P2 within 1 hour
- Post-mortems: Required for all incidents affecting SLA
```

## Inter-Service Communication

### Synchronous Communication Patterns

```markdown
## REST-to-gRPC Bridge Pattern

For services that need to communicate across protocol boundaries:

### Use Case
- Frontend calls REST API
- Backend services use gRPC internally
- Translation layer required at boundary

### Architecture
```
┌──────────────┐
│   Web Client │
│   (REST)     │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  API Gateway     │
│  (REST/gRPC)     │
└──────┬───────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Order Service (gRPC)                │
│  - Receives OrderRequest             │
│  - Calls Payment Service (gRPC)      │
│  - Calls Inventory Service (gRPC)    │
└──────────────────────────────────────┘
```

### Timeout Strategies

| Operation Type | Default Timeout | Max Retries | Backoff Strategy |
|---|---|---|---|
| Query Operations | 5 seconds | 3 | Exponential (base 100ms) |
| Mutation Operations | 30 seconds | 1 | None (no retries) |
| Batch Operations | 60 seconds | 0 | None (no retries) |
| Event Publishing | 10 seconds | 3 | Linear (1s increment) |

### Circuit Breaker Patterns

```markdown
## Circuit Breaker Configuration

Service-to-service calls should implement circuit breakers to prevent cascading failures.

**Closed State** (normal operation):
- Call through to downstream service
- Track failure rate
- Transition to Open if failure_rate > 50% OR error_count > 10

**Open State** (fast-fail):
- Reject requests immediately
- Emit circuit breaker exception
- Transition to Half-Open after wait_duration (60 seconds)

**Half-Open State** (recovery test):
- Allow test request through
- If successful: transition to Closed
- If fails: return to Open state

**Configuration Example**:
```yaml
circuit_breaker:
  failure_threshold: 50  # 50% failure rate triggers open
  error_count_threshold: 10  # or 10 consecutive errors
  timeout_seconds: 30
  wait_duration_seconds: 60
  half_open_test_requests: 3
  sliding_window_type: COUNT_BASED
  sliding_window_size: 100
```
```

### Asynchronous Communication Patterns

```markdown
## Event-Driven Service Communication

### Order Placement Flow

1. **Order Service** receives CreateOrder request
   - Creates Order aggregate
   - Publishes OrderCreated event
   - Returns immediate confirmation

2. **Inventory Service** subscribes to OrderCreated
   - Reserves stock asynchronously
   - Publishes StockReserved event (success) or ReservationFailed event (failure)

3. **Payment Service** subscribes to StockReserved
   - Initiates payment processing
   - Publishes PaymentAuthorized or PaymentFailed event

4. **Notification Service** subscribes to all events
   - Sends confirmation email on OrderCreated
   - Sends payment confirmation email on PaymentAuthorized
   - Sends cancellation email on ReservationFailed

### Advantages
- Services are loosely coupled
- Easy to add new subscribers without modifying existing services
- Better scalability through asynchronous processing
- Natural handling of temporal concerns

### Challenges
- Eventual consistency instead of strong consistency
- Debugging distributed flows more complex
- Event schema evolution requires careful management
- Order of events across services must be considered
```

## Service Mesh Documentation

### Observability Configuration

```markdown
## Service Mesh Metrics and Tracing

### Prometheus Metrics

Every service must export metrics in Prometheus format:

```
# HELP payment_requests_total Total number of payment requests
# TYPE payment_requests_total counter
payment_requests_total{service="payment-service",method="POST",endpoint="/authorize",status="200"} 1523
payment_requests_total{service="payment-service",method="POST",endpoint="/authorize",status="400"} 18
payment_requests_total{service="payment-service",method="POST",endpoint="/authorize",status="500"} 2

# HELP payment_request_duration_seconds Request duration in seconds
# TYPE payment_request_duration_seconds histogram
payment_request_duration_seconds_bucket{service="payment-service",le="0.005"} 450
payment_request_duration_seconds_bucket{service="payment-service",le="0.01"} 892
payment_request_duration_seconds_bucket{service="payment-service",le="0.1"} 1498
payment_request_duration_seconds_bucket{service="payment-service",le="1"} 1520
payment_request_duration_seconds_bucket{service="payment-service",le="+Inf"} 1523
payment_request_duration_seconds_sum{service="payment-service"} 127.435
payment_request_duration_seconds_count{service="payment-service"} 1523
```

### Distributed Tracing

```
Order Service              Payment Service            Inventory Service
├─ TraceID: abc123        │                         │
├─ SpanID: span-001       │                         │
│  StartTime: T0          │                         │
│  Operation: CreateOrder │                         │
│                         │                         │
│  ├─ Call PaymentService │                         │
│  │  SpanID: span-002    ├─ TraceID: abc123       │
│  │  StartTime: T0+5ms   │  SpanID: span-002      │
│  │  Duration: 150ms     │  Operation: Authorize  │
│  │                      │  StartTime: T0+5ms     │
│  │                      │  Duration: 120ms       │
│  │                      └─────────────────┐      │
│  │                                        │      │
│  ├─ Call InventoryService                │      │
│  │  SpanID: span-003                      │      │
│  │  StartTime: T0+170ms                   │      │
│  │  Duration: 200ms                       │      │
│  │                                        │      │
│  │                                    Request    │
│  │                                        │      │
│  │                                    ├─ TraceID: abc123
│  │                                    │  SpanID: span-003
│  │                                    │  Operation: ReserveStock
│  │                                    └─ StartTime: T0+170ms
│  │                                       Duration: 180ms
│  │
│  EndTime: T0+400ms
│  Duration: 400ms
└─ Status: SUCCESS
```

### Istio VirtualService Configuration Example

```yaml
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: payment-service
  namespace: production
spec:
  hosts:
  - payment-service
  http:
  # Canary deployment: 5% traffic to v2, 95% to v1
  - match:
    - sourceLabels:
        user: canary-tester
    route:
    - destination:
        host: payment-service
        subset: v2
      weight: 100
  - route:
    - destination:
        host: payment-service
        subset: v1
      weight: 95
    - destination:
        host: payment-service
        subset: v2
      weight: 5
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: payment-service
  namespace: production
spec:
  host: payment-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 1000
      http:
        http1MaxPendingRequests: 100
        http1MaxRequests: 100
        maxRequestsPerConnection: 2
    loadBalancer:
      simple: LEAST_REQUEST
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      splitExternalLocalOriginErrors: true
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```
```

## Dependency Mapping

### Service Dependency Graph

```markdown
## Order Service Dependencies

### Direct Dependencies

**Synchronous (Request/Response)**:
1. Payment Service
   - Endpoint: gRPC payment-service:50051
   - Operation: AuthorizePayment
   - Required: Yes
   - Critical: Yes
   - SLA: P95 < 100ms

2. Inventory Service
   - Endpoint: gRPC inventory-service:50051
   - Operation: ReserveStock
   - Required: Yes
   - Critical: Yes
   - SLA: P95 < 150ms

3. Customer Service
   - Endpoint: REST https://customer-api:8443/api/v2
   - Operation: ValidateCustomerProfile
   - Required: Yes
   - Critical: No (fallback: skip validation)
   - SLA: P95 < 200ms

**Asynchronous (Event-Based)**:
1. Notification Service
   - Channel: RabbitMQ topic: order.events
   - Events: OrderCreated, OrderConfirmed, OrderShipped
   - Delivery: Best-effort (dead-letter queue configured)

2. Analytics Service
   - Channel: Kafka topic: order-analytics
   - Events: All order events
   - Retention: 7 days

### Transitive Dependencies

```
order-service
├── payment-service
│   ├── postgres-db (payment-db.us-east-1a)
│   ├── fraud-detection-service
│   │   └── ML-model-server
│   └── audit-logger (syslog)
├── inventory-service
│   ├── postgres-db (inventory-db.us-east-1a)
│   ├── cache-service (Redis)
│   └── event-broker (RabbitMQ)
├── customer-service
│   ├── postgres-db (customer-db.us-east-1b)
│   ├── identity-provider (OAuth)
│   └── cache-service (Redis)
└── notification-service
    └── email-provider (SendGrid)
    └── sms-provider (Twilio)
```

### Dependency Impact Analysis

```markdown
## Payment Service Outage Impact

If payment-service becomes unavailable:
- **Order Service**: Cannot create orders (critical)
- **Invoice Service**: Cannot generate invoices for new orders
- **Revenue Reporting**: Missing real-time data
- **Refund Service**: Cannot process refunds

**RTO** (Recovery Time Objective): 15 minutes
**RPO** (Recovery Point Objective): 5 minutes
**Mitigation**: Use payment pre-authorization cache for up to 30 minutes
```
```

## Configuration Management

### Service Configuration Pattern

```yaml
# config-production.yaml
service:
  name: payment-service
  version: 2.3.1
  environment: production

server:
  port: 8080
  shutdown_timeout_seconds: 30
  grpc_port: 50051
  tls:
    enabled: true
    cert_path: /etc/secrets/server.crt
    key_path: /etc/secrets/server.key

logging:
  level: INFO
  format: json
  request_logging: true
  slow_request_threshold_ms: 5000

database:
  primary:
    host: payment-db.us-east-1a.rds.amazonaws.com
    port: 5432
    database: payment_prod
    credentials_secret: /etc/secrets/db-credentials
    max_connections: 50
    connection_timeout_seconds: 10
  replicas:
    - host: payment-db-replica-1.us-east-1b.rds.amazonaws.com
      port: 5432
    - host: payment-db-replica-2.us-east-1c.rds.amazonaws.com
      port: 5432

cache:
  type: redis
  endpoints:
    - payment-cache-1.cache.amazonaws.com:6379
    - payment-cache-2.cache.amazonaws.com:6379
  ttl_seconds: 3600
  max_size: 100000

external_apis:
  stripe:
    api_key_secret: /etc/secrets/stripe-api-key
    timeout_seconds: 30
    retry_attempts: 3
  fraud_detection:
    endpoint: https://fraud-api.example.com
    api_key_secret: /etc/secrets/fraud-api-key
    timeout_seconds: 5
    circuit_breaker_failure_threshold: 50

observability:
  metrics:
    enabled: true
    port: 9090
    histogram_buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5]
  tracing:
    enabled: true
    sampling_rate: 0.1
    jaeger_endpoint: http://jaeger-collector.monitoring:14268/api/traces

feature_flags:
  enable_async_payment_processing: true
  enable_payment_retry_logic: true
  max_payment_retry_attempts: 3
```

### Secrets Management

```markdown
## Configuration Secrets

All sensitive data must be stored in secrets management system (e.g., HashiCorp Vault, AWS Secrets Manager):

### Database Credentials
- Key: `payment-service/db/primary`
- Contents: username, password, connection_string
- Rotation: Every 90 days
- Access: Limited to payment-service pods only

### API Keys
- Key: `payment-service/external-apis/stripe`
- Contents: API key, webhook signing key
- Rotation: Every 180 days or on API request

### TLS Certificates
- Key: `payment-service/tls/server-cert`
- Contents: certificate, private key
- Rotation: 30 days before expiration
- Monitoring: Alert if certificate expires in < 7 days
```

## Monitoring and Observability

### Health Check Patterns

```markdown
## Health Check Implementation

### Liveness Check
- Endpoint: `GET /health/live`
- Purpose: Is the service running and responding?
- Frequency: Every 10 seconds
- Timeout: 5 seconds
- Failure threshold: 3 consecutive failures
- Response:
  ```json
  { "status": "alive" }
  ```

### Readiness Check
- Endpoint: `GET /health/ready`
- Purpose: Can the service handle traffic?
- Frequency: Every 5 seconds
- Timeout: 5 seconds
- Failure threshold: 1 failure
- Checks:
  - Database connectivity
  - Cache/Redis connectivity
  - Downstream service availability (via circuit breaker state)
- Response:
  ```json
  {
    "status": "ready",
    "components": {
      "database": "ok",
      "cache": "ok",
      "payment_processor": "ok"
    }
  }
  ```

### Startup Check
- Endpoint: `GET /health/startup`
- Purpose: Has service completed initialization?
- Called once during pod startup
- Checks:
  - Database migrations completed
  - Configuration loaded
  - Connections established
```

### Alerting Rules

```yaml
# prometheus-rules-payment-service.yaml
groups:
- name: payment-service-alerts
  rules:
  # High error rate
  - alert: HighErrorRate
    expr: rate(payment_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    labels:
      severity: critical
      service: payment-service
    annotations:
      summary: "Payment service error rate > 5%"
      description: "Payment service {{ $labels.instance }} has error rate {{ $value }}"
      runbook: "https://wiki.example.com/payment-service-errors"

  # High latency
  - alert: HighLatency
    expr: histogram_quantile(0.95, payment_request_duration_seconds) > 0.5
    for: 10m
    labels:
      severity: warning
      service: payment-service
    annotations:
      summary: "Payment service P95 latency > 500ms"
      description: "P95 latency is {{ $value }}s"

  # Database connection issues
  - alert: DatabaseConnectionErrors
    expr: rate(payment_service_db_connection_errors[5m]) > 0
    for: 2m
    labels:
      severity: critical
      service: payment-service
    annotations:
      summary: "Payment service database connection failures"
      description: "Cannot establish database connection"
      runbook: "https://wiki.example.com/payment-service-db-issues"
```

## Deployment and Release Notes

### Release Notes Template

```markdown
# Payment Service v2.3.1 Release Notes

**Release Date**: 2025-11-19
**Previous Version**: 2.3.0
**Changelog**: [Full changelog](./CHANGELOG.md)

## New Features
- Implement advanced fraud detection for high-value transactions
- Add support for 3D Secure 2.0 authentication
- Introduce payment retry logic with exponential backoff

## Bug Fixes
- Fix race condition in payment authorization workflow (#1234)
- Correct currency conversion calculation edge case (#1235)
- Resolve memory leak in connection pool (#1236)

## Performance Improvements
- Reduce P95 latency by 40% through database query optimization
- Implement connection pooling improvements (50 → 100 max connections)
- Add caching layer for customer fraud profiles (500ms → 50ms lookup)

## Breaking Changes
- **Deprecated**: `/api/v1/payments/authorize` endpoint (use `/api/v2/payments/authorize`)
- **Changed**: Error response format now includes `request_id` field
- **Removed**: Support for legacy payment methods (deprecated in v2.0)

## Security Updates
- Update cryptographic libraries (OpenSSL 1.1.1 → 3.0)
- Rotate API keys for external payment processors
- Implement stricter TLS 1.2+ requirement (was TLS 1.0+)

## Migration Guide
If upgrading from v2.2.x:
1. Update client libraries to latest version
2. Review error handling for new error codes
3. Test with staging environment minimum 48 hours
4. Follow [upgrade procedure](./UPGRADE.md)

## Deployment Checklist
- [ ] Verify database migration scripts
- [ ] Review configuration changes
- [ ] Validate downstream service compatibility
- [ ] Run smoke tests in staging
- [ ] Schedule gradual rollout (canary 5% → 25% → 100%)
- [ ] Monitor error rates and latency post-deployment

## Rollback Plan
If critical issues detected:
1. Trigger automated canary failure detection (error rate > 5%)
2. Automatically rollback to v2.3.0
3. Notify on-call team and post-mortem coordinator
4. Estimated rollback time: 2-3 minutes

## Support
- Release notes questions: [@platform-payments](https://slack.com/archives/team)
- Migration assistance: Post in [#platform-payments-support](https://slack.com/archives/channel)
- Bug reports: [GitHub Issues](https://github.com/example/payment-service/issues)
```

### Blue-Green Deployment Documentation

```markdown
## Blue-Green Deployment Procedure

### Overview
Blue-green deployment allows running two identical production environments:
- **Blue**: Current production version
- **Green**: New version being tested

### Step 1: Prepare Green Environment
```
Green Environment (v2.3.1)
├── 3 Pods (3 replicas)
├── Dedicated load balancer
├── Separate database instance (restored from Blue snapshot)
└── Health checks running (all passing)
```

### Step 2: Smoke Testing
- Run automated test suite against Green (100 tests, 5 minutes)
- Run manual functional tests (critical paths, 15 minutes)
- Monitor Green metrics for 10 minutes (error rate < 0.1%, latency stable)

### Step 3: Traffic Switch
```
Before:
  Requests → Load Balancer → Blue (100%) | Green (0%)

After:
  Requests → Load Balancer → Blue (0%) | Green (100%)
```

Traffic switch takes < 30 seconds due to load balancer configuration updates.

### Step 4: Monitoring (60 minutes)
- Error rate stays below 0.5%
- P95 latency remains stable
- Database replication lag < 5 seconds
- No increase in timeout errors

### Step 5: Rollback Readiness
- Blue environment remains online and ready
- Can rollback with single load balancer config update
- Rollback time: < 30 seconds
- No data loss (both environments share database)

## Rollback Procedure
If issues detected within 2 hours of deployment:
1. Load balancer reverts traffic to Blue
2. Green environment remains running for diagnostics
3. Incident post-mortem conducted before next deployment attempt
4. Root cause must be identified before retry
```

## Best Practices

### Documentation Standards

1. **Keep Documentation Close to Code**
   - API documentation next to endpoint definitions
   - Configuration documentation with config files
   - Database schema changes with migration scripts

2. **Document the "Why" Not Just the "What"**
   ```markdown
   ❌ Bad: "The service timeout is 30 seconds"
   ✅ Good: "The service timeout is 30 seconds because external
   payment processors typically respond within 25s; we add 5s buffer
   for occasional network delays. Longer timeouts increase resource
   utilization under failure conditions."
   ```

3. **Version Your Documentation**
   - Document which service version applies
   - Include migration guides for major changes
   - Archive old documentation with clear deprecation dates

4. **Use Runbooks for Common Issues**
   ```markdown
   ## Runbook: Payment Service High Error Rate

   **Symptoms**: Error rate > 5% for > 5 minutes

   **Diagnosis**:
   1. Check payment-service pod logs:
      `kubectl logs -n production -l app=payment-service`
   2. Verify database connectivity
   3. Check payment processor status (Stripe dashboard)
   4. Review recent deployments in the last hour

   **Resolution**:
   - If database issue: check RDS CPU/memory
   - If payment processor issue: no action needed (wait for restoration)
   - If recent deployment: trigger rollback procedure

   **Escalation**:
   If unresolved after 15 minutes, page payment-service on-call lead.
   ```

5. **Create Architecture Decision Records (ADRs)**
   ```markdown
   # ADR-042: Use gRPC for Internal Service Communication

   **Status**: Accepted
   **Date**: 2025-10-15

   **Context**:
   Need to improve internal service communication performance.
   Evaluated REST, gRPC, and message queues.

   **Decision**:
   Use gRPC for synchronous service-to-service communication.
   Use message queues for asynchronous event propagation.

   **Consequences**:
   - Positive: 10x faster latency, better bandwidth utilization
   - Negative: Requires additional infrastructure (gRPC proxies)
   - Requires: Team training on Protocol Buffers
   ```

6. **Living Documentation Pattern**
   - Tools: WikiJS, GitBook, Notion with GitHub sync
   - Reviews: Monthly documentation audits
   - Ownership: Each service team responsible for their docs
   - Automation: Auto-generate API docs from code annotations

### Service Communication Checklist

```markdown
## Before Deploying New Service-to-Service Communication

- [ ] Define explicit contract (request/response schemas)
- [ ] Document timeout values and retry logic
- [ ] Implement circuit breaker pattern
- [ ] Add comprehensive error handling
- [ ] Define SLAs for synchronous calls
- [ ] Implement rate limiting if necessary
- [ ] Add monitoring/alerting for call failures
- [ ] Document failure scenarios and fallbacks
- [ ] Test against service unavailability
- [ ] Load test communication patterns
- [ ] Document in service registry
- [ ] Notify dependent service teams
- [ ] Update architecture diagrams
```

### Team Communication

```markdown
## Service Changes Communication Plan

### Minor Updates (bug fixes, performance improvements)
- Announce in #engineering Slack channel
- Include version number and brief summary
- No pre-notification needed

### Feature Additions (backward-compatible)
- Pre-announce in service-specific channel 48 hours before
- Include migration guide if applicable
- Mention in team standup day-of deployment

### Breaking Changes (API modifications)
- Announce in all-hands meeting 2 weeks before
- Provide detailed migration guide 1 week before
- Schedule office hours for migration questions
- Support v1 API for minimum 6 months
- Schedule EOL notification 1 month before support ends

### Major Outages (unavailability > 5 minutes)
- Real-time updates in #incidents channel
- Status page updates every 5 minutes
- Post-mortem within 24 hours
- Root cause and prevention plan within 1 week
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-19
**Author**: Platform Architecture Team
**Review Frequency**: Quarterly
