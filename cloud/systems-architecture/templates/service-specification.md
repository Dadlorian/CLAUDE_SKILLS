# Service Specification: [Service Name]

**Version**: 1.0
**Last Updated**: YYYY-MM-DD
**Owner**: [Team Name]
**Status**: [Planning | Development | Production]

---

## Overview

### Purpose
[1-2 paragraphs describing what business capability this service provides and why it exists]

### Bounded Context
[Which DDD bounded context does this service belong to? What is the ubiquitous language?]

### Key Responsibilities
1. [Primary responsibility 1]
2. [Primary responsibility 2]
3. [Primary responsibility 3]

### Non-Responsibilities
[What this service explicitly does NOT do - important for maintaining boundaries]
- ❌ [Non-responsibility 1]
- ❌ [Non-responsibility 2]

---

## Business Context

### Business Capabilities
- [Business capability 1]
- [Business capability 2]
- [Business capability 3]

### Key Stakeholders
- **Product Owner**: [Name]
- **Business SME**: [Name]
- **Engineering Lead**: [Name]

### Success Metrics (KPIs)
- [Business metric 1]: Target [value]
- [Business metric 2]: Target [value]
- [Business metric 3]: Target [value]

---

## Domain Model

### Core Entities
```
[Entity Name]
├── Properties
│   ├── [property]: [type] - [description]
│   └── [property]: [type] - [description]
├── Behaviors
│   ├── [method] - [what it does]
│   └── [method] - [what it does]
└── Events Raised
    └── [EventName] - [when triggered]
```

### Value Objects
- **[ValueObject Name]**: [Description]
- **[ValueObject Name]**: [Description]

### Aggregates
**Aggregate Root**: [Name]
**Boundary**: [What entities/value objects are included]
**Invariants**: [Business rules that must always be true]

### Domain Events
| Event Name | Trigger | Payload | Consumers |
|------------|---------|---------|-----------|
| [EventName] | [When raised] | [Key fields] | [Which services consume] |
| [EventName] | [When raised] | [Key fields] | [Which services consume] |

---

## API Specification

### REST API Endpoints

#### Create [Resource]
```
POST /api/v1/[resources]
Content-Type: application/json
Authorization: Bearer {token}

Request Body:
{
  "[field]": "[value]",
  "[field]": "[value]"
}

Response: 201 Created
{
  "id": "[uuid]",
  "[field]": "[value]",
  "createdAt": "[timestamp]"
}

Errors:
- 400 Bad Request: Invalid input
- 401 Unauthorized: Missing/invalid token
- 409 Conflict: Resource already exists
```

#### Get [Resource]
```
GET /api/v1/[resources]/{id}
Authorization: Bearer {token}

Response: 200 OK
{
  "id": "[uuid]",
  "[fields]": "[values]"
}

Errors:
- 401 Unauthorized
- 404 Not Found
```

#### Update [Resource]
```
PUT /api/v1/[resources]/{id}
Content-Type: application/json
Authorization: Bearer {token}

Request Body:
{
  "[field]": "[new value]"
}

Response: 200 OK
{
  "id": "[uuid]",
  "[updated fields]": "[values]"
}

Errors:
- 400 Bad Request
- 401 Unauthorized
- 404 Not Found
- 409 Conflict
```

#### Delete [Resource]
```
DELETE /api/v1/[resources]/{id}
Authorization: Bearer {token}

Response: 204 No Content

Errors:
- 401 Unauthorized
- 404 Not Found
- 409 Conflict: Cannot delete (dependencies exist)
```

#### List [Resources]
```
GET /api/v1/[resources]?page=1&size=20&sort=createdAt:desc&filter=[field]:eq:[value]
Authorization: Bearer {token}

Response: 200 OK
{
  "data": [
    { "id": "...", "...": "..." }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 150,
    "totalPages": 8
  }
}
```

### Event Contracts

#### [EventName]
```json
{
  "eventId": "uuid",
  "eventType": "[EventName]",
  "eventVersion": "1.0",
  "timestamp": "2025-11-19T10:30:00Z",
  "aggregateId": "uuid",
  "aggregateType": "[AggregateType]",
  "payload": {
    "[field]": "[value]",
    "[field]": "[value]"
  },
  "metadata": {
    "correlationId": "uuid",
    "causationId": "uuid",
    "userId": "uuid"
  }
}
```

**Published To**: [topic/queue name]
**Consumers**: [Service1, Service2]
**Versioning**: [Strategy for schema evolution]

---

## Data Ownership

### Primary Data
[Data that this service is the source of truth for]

**Database**: [Type, e.g., PostgreSQL, MongoDB]

#### Tables/Collections

##### [Table Name]
```sql
CREATE TABLE [table_name] (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  [field] [TYPE] NOT NULL,
  [field] [TYPE],
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_[field] ON [table_name]([field]);
```

**Ownership**: Full ownership (create, read, update, delete)
**Access**: Private (only this service accesses directly)

### Cached/Replicated Data
[Data sourced from other services, cached locally for performance]

**Source Service**: [Service Name]
**Update Mechanism**: [Event-driven replication | Periodic sync | Cache with TTL]
**Consistency**: [Eventual | Strong]
**Retention**: [How long cached, refresh strategy]

### Referenced Data
[Data owned by other services, referenced by ID only]

- **[Entity]**: Owned by [Service], referenced by [ID field]

---

## Dependencies

### Upstream Dependencies (Services This Service Calls)

| Service | Type | Purpose | SLA | Failure Mode |
|---------|------|---------|-----|--------------|
| [Service Name] | Sync REST | [Why called] | 99.9%, <200ms | Circuit breaker, fallback to [strategy] |
| [Service Name] | Async Event | [Why subscribed] | At-least-once delivery | Retry with DLQ |

### Downstream Consumers (Services That Call This Service)

| Service | Type | Use Case | Contract |
|---------|------|----------|----------|
| [Service Name] | Sync REST | [Why calling] | [API version] |
| [Service Name] | Async Event | [Which events] | [Event schema version] |

### Infrastructure Dependencies

- **Database**: [PostgreSQL 14+]
- **Message Broker**: [Kafka, topic names]
- **Cache**: [Redis, use case]
- **Storage**: [S3 bucket, purpose]
- **External APIs**: [Third-party service, purpose]

---

## Service Level Objectives (SLOs)

### Availability
**Target**: 99.9% uptime (per 30-day window)
**Measurement**: Successful responses / Total requests
**Error Budget**: 43 minutes downtime per month

### Latency
**P50**: < 100ms
**P95**: < 200ms
**P99**: < 500ms
**Measurement**: Server-side request duration

### Throughput
**Expected**: [X] requests/second average
**Peak**: [Y] requests/second (bursts)
**Measurement**: Requests per second

### Error Rate
**Target**: < 0.1% of requests result in 5xx errors
**Measurement**: 5xx responses / Total responses

### Data Freshness
**Target**: Data updated within [X] minutes of source change
**Measurement**: Event processing lag

---

## Resilience Patterns

### Circuit Breaker
```
Failure Threshold: 50% errors in 10 requests
Timeout: 5 seconds
Half-Open Retry: After 30 seconds
Library: [Resilience4j | Hystrix | Polly]
```

### Retry Policy
```
Strategy: Exponential backoff with jitter
Base Delay: 100ms
Max Attempts: 3
Max Delay: 1 second
Retryable Errors: [Network timeouts, 503, 429]
```

### Timeout Policy
```
Request Timeout: 5 seconds
Connection Timeout: 2 seconds
Read Timeout: 3 seconds
```

### Bulkhead
```
Thread Pool Size: [X] threads
Queue Size: [Y] tasks
Isolation: [Per dependency]
```

### Rate Limiting
```
Per User: [X] requests/minute
Per API Key: [Y] requests/minute
Global: [Z] requests/second
Strategy: [Token bucket | Sliding window]
```

---

## Observability

### Logging
**Format**: Structured JSON
**Level**: INFO in production, DEBUG in staging
**Retention**: 30 days

**Key Log Events**:
- Request received (INFO)
- External call made (INFO)
- Business event occurred (INFO)
- Error occurred (ERROR with stack trace)

**Required Fields**:
```json
{
  "timestamp": "ISO8601",
  "level": "INFO|WARN|ERROR",
  "service": "service-name",
  "traceId": "uuid",
  "spanId": "uuid",
  "userId": "uuid",
  "message": "Human-readable message",
  "context": { /* Additional context */ }
}
```

### Metrics
**Tool**: [Prometheus | CloudWatch | Datadog]

**RED Metrics**:
- `http_requests_total` (counter) - labels: method, endpoint, status
- `http_request_duration_seconds` (histogram) - labels: method, endpoint
- `http_requests_errors_total` (counter) - labels: method, endpoint, error_type

**Custom Business Metrics**:
- `[resource]_created_total` (counter)
- `[resource]_processing_duration_seconds` (histogram)
- `[business_event]_total` (counter)

### Distributed Tracing
**Tool**: [Jaeger | X-Ray | Zipkin]
**Sampling**: 1% of successful requests, 100% of errors
**Propagation**: W3C Trace Context headers

**Instrumented Operations**:
- HTTP requests (inbound and outbound)
- Database queries
- Message broker publish/consume
- External API calls

### Health Checks

#### Liveness Probe
```
GET /health/live
Response: 200 OK if process is running
Use: Kubernetes liveness check
```

#### Readiness Probe
```
GET /health/ready
Response:
  200 OK if ready to serve traffic
  503 Service Unavailable if dependencies down

Checks:
  - Database connection pool healthy
  - Message broker connected
  - Critical upstream services reachable
```

#### Startup Probe
```
GET /health/startup
Response: 200 OK once service fully initialized
Timeout: 60 seconds
```

---

## Security

### Authentication & Authorization
**Method**: OAuth 2.0 / JWT
**Token Expiration**: 15 minutes
**Refresh Token**: 7 days
**Scopes**: [scope1, scope2, scope3]

### Authorization Rules
```
POST /api/v1/[resources]: Requires scope=[write:resources]
GET /api/v1/[resources]: Requires scope=[read:resources]
DELETE /api/v1/[resources]/{id}: Requires scope=[delete:resources] + ownership check
```

### Data Protection
**Encryption in Transit**: TLS 1.3
**Encryption at Rest**: AES-256 (database, S3)
**Sensitive Fields**: [List fields requiring encryption/masking]
**PII Data**: [List PII fields, retention policy, deletion process]

### Secrets Management
**Tool**: [AWS Secrets Manager | HashiCorp Vault | Azure Key Vault]
**Rotation**: Every 90 days
**Access**: Via IAM roles, least privilege

### Input Validation
- All inputs validated against schema (JSON Schema | OpenAPI)
- SQL injection prevention: Parameterized queries
- XSS prevention: Output encoding
- Request size limit: 1 MB

---

## Testing Strategy

### Unit Tests
**Coverage Target**: 80%+
**Tool**: [JUnit | pytest | Jest]
**Focus**: Business logic, domain model, edge cases

### Integration Tests
**Tool**: [Testcontainers | LocalStack]
**Coverage**:
- Database operations
- Message broker interactions
- Consumer-driven contract tests (Pact)

### End-to-End Tests
**Tool**: [Postman | REST Assured]
**Coverage**: Critical user journeys (5-10 tests maximum)

### Performance Tests
**Tool**: [k6 | JMeter | Gatling]
**Scenarios**:
- Load test: Expected traffic for 30 minutes
- Stress test: 2x expected traffic
- Soak test: Expected traffic for 8 hours

### Chaos Tests
- Random pod deletion
- Network latency injection (100-500ms)
- Dependency failure simulation

---

## Deployment

### Infrastructure
**Platform**: [Kubernetes | ECS | App Engine]
**Region**: [AWS us-east-1 | Azure East US | GCP us-central1]
**Multi-Region**: [Yes | No]

### Resources
```yaml
Production:
  CPU: 2 vCPU
  Memory: 4 GB
  Replicas: 3 (min), 10 (max)
  Auto-scaling: CPU > 70% or Memory > 80%

Staging:
  CPU: 1 vCPU
  Memory: 2 GB
  Replicas: 2
```

### Deployment Strategy
**Type**: [Blue-Green | Canary | Rolling]
**Canary**: 5% → 25% → 50% → 100% (15 min between stages)
**Rollback**: Automatic if error rate > 1% or latency P95 > 500ms

### Environment Variables
```bash
DATABASE_URL=[secret]
KAFKA_BROKERS=[config]
REDIS_URL=[config]
LOG_LEVEL=[INFO|DEBUG]
FEATURE_FLAG_[X]=[true|false]
```

---

## Operational Runbooks

### Incident Response

#### High Error Rate
1. Check `/health/ready` endpoint
2. Review recent deployments (rollback if recent)
3. Check dependency health
4. Review error logs for patterns
5. Escalate to on-call engineer if unresolved in 15 min

#### High Latency
1. Check database query performance
2. Review upstream service latencies
3. Check for resource saturation (CPU, memory, connections)
4. Review recent traffic patterns (DDoS?)
5. Consider scaling up if resource-bound

#### Database Connection Exhaustion
1. Check connection pool metrics
2. Look for long-running queries
3. Check for connection leaks in code
4. Restart service to reset connections (temporary)
5. Increase pool size if sustained high load

### Maintenance Procedures

#### Database Schema Migration
1. Write migration script (up and down)
2. Test in staging environment
3. Take database backup
4. Apply migration during low-traffic window
5. Validate application functionality
6. Monitor for errors

#### Secret Rotation
1. Generate new secret
2. Update secret in secret manager
3. Deploy new version of service (picks up new secret)
4. Validate service functionality
5. Delete old secret after 24 hours

---

## Contact & Ownership

**Team**: [Team Name]
**Slack Channel**: #team-[name]
**On-Call**: [PagerDuty rotation link]
**Documentation**: [Wiki link]
**Repository**: [GitHub/GitLab URL]
**CI/CD**: [Pipeline URL]
**Dashboards**: [Grafana/Datadog URL]

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | YYYY-MM-DD | Initial specification | [Name] |
| 1.1 | YYYY-MM-DD | Added new endpoint | [Name] |

---

## Related Documents

- **ADR-XXX**: [Architecture decision]
- **RFC-YYY**: [Design proposal]
- **[Service Name] Spec**: [Dependency or related service]
