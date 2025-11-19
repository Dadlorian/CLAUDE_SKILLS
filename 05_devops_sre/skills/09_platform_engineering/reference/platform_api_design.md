# Platform API Design Reference

## Overview

Platform APIs are the primary interface through which developers interact with your internal platform. Well-designed APIs enable self-service, reduce cognitive load, and accelerate development velocity.

## Design Principles

### 1. Developer-First Design

**Intent-Based Rather Than Implementation-Based**

Good platform APIs express what developers want to achieve, not how to achieve it.

```yaml
# Bad: Implementation-focused
createEC2Instance:
  instanceType: t3.medium
  ami: ami-12345
  securityGroups: [sg-123]
  subnet: subnet-456
  tags:
    - Key: Name
      Value: my-app

# Good: Intent-focused
createWebService:
  name: my-app
  runtime: node18
  resources: medium
  environment: production
```

### 2. Sensible Defaults

Provide smart defaults that work for 80% of use cases.

```yaml
# Minimal required input
service:
  name: payment-api
  type: rest-api
  # Defaults applied:
  # - runtime: node18 (from org standard)
  # - replicas: 3 (high availability default)
  # - autoScaling: enabled
  # - monitoring: enabled
  # - logging: enabled
  # - security: organization baseline
```

### 3. Progressive Disclosure

Allow simple things to be simple, complex things to be possible.

```yaml
# Simple use case
database:
  name: users-db
  type: postgres

# Advanced use case
database:
  name: analytics-db
  type: postgres
  version: "15.2"
  resources:
    cpu: 4
    memory: 16Gi
    storage: 100Gi
  backup:
    retention: 30d
    schedule: "0 2 * * *"
  replication:
    enabled: true
    replicas: 2
  performance:
    connectionPooling: true
    queryOptimization: aggressive
```

### 4. Consistency

Maintain consistent patterns across all platform APIs.

```yaml
# Consistent structure across resources
apiVersion: platform.company.com/v1
kind: WebService | Database | Queue | Cache
metadata:
  name: resource-name
  labels:
    team: platform
    cost-center: engineering
spec:
  # Resource-specific configuration
status:
  # Runtime state (read-only)
```

### 5. Discoverability

Make it easy to learn what's possible.

```bash
# Self-documenting CLI
platform create --help
platform create service --help
platform create database --help

# Schema validation with helpful errors
platform validate service.yaml
# Error: 'runtime' must be one of: [node18, python311, go121]
# Available runtimes: platform runtime list
```

## API Patterns

### Declarative Configuration

Use declarative YAML/JSON for resource definitions.

```yaml
# service.yaml
apiVersion: platform.company.com/v1
kind: Service
metadata:
  name: user-service
  namespace: production
  labels:
    team: identity
    component: backend
  annotations:
    docs: https://wiki.company.com/user-service
    oncall: identity-team
spec:
  runtime:
    language: go
    version: "1.21"

  deployment:
    replicas: 3
    strategy: rollingUpdate
    resources:
      requests:
        cpu: 500m
        memory: 512Mi
      limits:
        cpu: 2000m
        memory: 2Gi

  networking:
    port: 8080
    ingress:
      enabled: true
      domains:
        - users.company.com
      paths:
        - /api/v1/users

  dependencies:
    databases:
      - name: users-db
        type: postgres
    caches:
      - name: session-cache
        type: redis
    queues:
      - name: events
        type: kafka

  observability:
    metrics:
      enabled: true
      path: /metrics
    logging:
      level: info
      format: json
    tracing:
      enabled: true
      samplingRate: 0.1

  security:
    authentication: oauth2
    authorization: rbac
    secrets:
      - db-credentials
      - api-keys
```

### REST API

Provide HTTP APIs for programmatic access.

```yaml
# OpenAPI Specification
openapi: 3.0.0
info:
  title: Platform API
  version: v1
  description: Internal developer platform API

servers:
  - url: https://platform.company.com/api/v1

paths:
  /services:
    get:
      summary: List all services
      parameters:
        - name: team
          in: query
          schema:
            type: string
        - name: environment
          in: query
          schema:
            type: string
      responses:
        200:
          description: List of services
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Service'

    post:
      summary: Create a new service
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ServiceSpec'
      responses:
        201:
          description: Service created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Service'

  /services/{id}:
    get:
      summary: Get service details
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Service details

    put:
      summary: Update service
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ServiceSpec'
      responses:
        200:
          description: Service updated

    delete:
      summary: Delete service
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        204:
          description: Service deleted

components:
  schemas:
    Service:
      type: object
      properties:
        id:
          type: string
        metadata:
          $ref: '#/components/schemas/Metadata'
        spec:
          $ref: '#/components/schemas/ServiceSpec'
        status:
          $ref: '#/components/schemas/ServiceStatus'
```

### CLI Interface

Provide a user-friendly command-line interface.

```bash
# Service management
platform service create --file service.yaml
platform service list --team identity
platform service get user-service
platform service update user-service --replicas 5
platform service delete user-service
platform service logs user-service --follow
platform service exec user-service -- bash

# Database management
platform database create postgres users-db
platform database list
platform database backup users-db
platform database restore users-db --backup-id abc123

# Secrets management
platform secret create api-key --value "secret-value"
platform secret list
platform secret rotate api-key

# Environment management
platform env create staging --from production
platform env list
platform env promote staging production

# Status and debugging
platform status
platform health
platform events --follow
platform troubleshoot user-service
```

### SDK/Client Libraries

Provide language-specific SDKs for programmatic integration.

```python
# Python SDK
from platform_sdk import PlatformClient, Service, Database

client = PlatformClient(
    api_key=os.environ['PLATFORM_API_KEY']
)

# Create service
service = Service(
    name='user-service',
    runtime='python311',
    replicas=3
)
result = client.services.create(service)

# Create database
database = Database(
    name='users-db',
    type='postgres',
    version='15'
)
db = client.databases.create(database)

# Link service to database
client.services.link_database(
    service_id=result.id,
    database_id=db.id
)

# Query status
service = client.services.get('user-service')
print(f"Status: {service.status.state}")
print(f"URL: {service.status.url}")
```

```javascript
// JavaScript SDK
const { PlatformClient } = require('@company/platform-sdk');

const client = new PlatformClient({
  apiKey: process.env.PLATFORM_API_KEY
});

// Create service
const service = await client.services.create({
  name: 'user-service',
  runtime: 'node18',
  replicas: 3
});

// Deploy service
await client.services.deploy(service.id, {
  image: 'registry.company.com/user-service:v1.2.3'
});

// Monitor deployment
const deployment = await client.services.getDeployment(service.id);
console.log(`Deployment status: ${deployment.status}`);

// Stream logs
client.services.logs(service.id, {
  follow: true,
  onData: (log) => console.log(log.message)
});
```

## API Capabilities

### Resource Management

#### CRUD Operations

```go
// Go SDK
package main

import (
    "context"
    "github.com/company/platform-sdk-go/platform"
)

func main() {
    client := platform.NewClient(
        platform.WithAPIKey(os.Getenv("PLATFORM_API_KEY")),
    )

    ctx := context.Background()

    // Create
    service, err := client.Services.Create(ctx, &platform.ServiceSpec{
        Name: "payment-service",
        Runtime: "go121",
        Replicas: 3,
    })

    // Read
    service, err = client.Services.Get(ctx, "payment-service")

    // Update
    service.Spec.Replicas = 5
    service, err = client.Services.Update(ctx, service)

    // Delete
    err = client.Services.Delete(ctx, "payment-service")

    // List
    services, err := client.Services.List(ctx, &platform.ListOptions{
        Team: "payments",
        Environment: "production",
    })
}
```

#### Filtering and Pagination

```http
GET /api/v1/services?team=payments&environment=production&page=1&limit=50
GET /api/v1/services?labels=tier:critical,region:us-east-1
GET /api/v1/services?search=payment&sort=created_at:desc
```

### Lifecycle Management

#### Deployment

```yaml
# Deployment configuration
deployment:
  strategy: blue-green | canary | rolling

  blueGreen:
    previewService: true
    autoPromotion: false

  canary:
    steps:
      - setWeight: 10
      - pause: {duration: 5m}
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 100
    analysis:
      metrics:
        - name: error-rate
          threshold: 0.01
        - name: latency-p99
          threshold: 500ms
```

#### Scaling

```bash
# Manual scaling
platform service scale user-service --replicas 10

# Auto-scaling
platform service autoscale user-service \
  --min 3 \
  --max 20 \
  --cpu 70 \
  --memory 80
```

#### Rollback

```bash
# Rollback to previous version
platform service rollback user-service

# Rollback to specific version
platform service rollback user-service --version v1.2.0

# Rollback with custom strategy
platform service rollback user-service \
  --strategy canary \
  --steps 25,50,100 \
  --step-duration 5m
```

### Observability

#### Metrics

```yaml
observability:
  metrics:
    enabled: true
    endpoint: /metrics
    scrapeInterval: 30s
    customMetrics:
      - name: orders_total
        type: counter
        help: Total number of orders processed
      - name: order_processing_duration
        type: histogram
        help: Order processing duration in seconds
        buckets: [0.1, 0.5, 1, 2, 5, 10]
```

#### Logging

```bash
# View logs
platform service logs user-service

# Follow logs
platform service logs user-service --follow

# Filter logs
platform service logs user-service \
  --since 1h \
  --level error \
  --grep "timeout"

# Multiple services
platform service logs --selector team=identity --follow
```

#### Tracing

```yaml
observability:
  tracing:
    enabled: true
    backend: jaeger
    samplingRate: 0.1
    propagation: w3c
    exporters:
      - type: otlp
        endpoint: tracing.company.com:4317
```

### Security

#### Authentication

```yaml
security:
  authentication:
    type: oauth2
    provider: okta
    scopes:
      - read:users
      - write:users

  serviceAccount:
    enabled: true
    name: user-service-sa
```

#### Secrets Management

```bash
# Create secret
platform secret create db-password \
  --value "secure-password" \
  --ttl 90d \
  --rotation auto

# Use in service
spec:
  env:
    - name: DB_PASSWORD
      valueFrom:
        secretRef:
          name: db-password
          key: password
```

#### Network Policies

```yaml
security:
  network:
    ingress:
      - from:
          - service: api-gateway
        ports:
          - 8080
      - from:
          - service: monitoring
        ports:
          - 9090

    egress:
      - to:
          - service: users-db
        ports:
          - 5432
      - to:
          - external: api.stripe.com
        ports:
          - 443
```

## API Versioning

### URL Versioning

```http
GET /api/v1/services
GET /api/v2/services
```

### Header Versioning

```http
GET /api/services
Accept: application/vnd.platform.v2+json
```

### Deprecation Strategy

```yaml
# Deprecation notice
deprecated: true
deprecatedAt: "2024-06-01"
sunsetAt: "2024-12-01"
migrationGuide: "https://docs.company.com/migration/v1-to-v2"
replacement:
  apiVersion: platform.company.com/v2
  kind: Service
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid service configuration",
    "details": [
      {
        "field": "spec.replicas",
        "message": "must be between 1 and 100",
        "value": 150
      }
    ],
    "requestId": "req-abc123",
    "documentation": "https://docs.company.com/errors/validation-error"
  }
}
```

### Error Codes

```yaml
# Standard error codes
VALIDATION_ERROR:        # Input validation failed
RESOURCE_NOT_FOUND:      # Resource doesn't exist
RESOURCE_CONFLICT:       # Resource already exists
PERMISSION_DENIED:       # Insufficient permissions
QUOTA_EXCEEDED:          # Resource quota exceeded
RATE_LIMIT_EXCEEDED:     # API rate limit hit
DEPENDENCY_ERROR:        # Dependency unavailable
INTERNAL_ERROR:          # Platform error
```

### Retry Logic

```python
import backoff
from platform_sdk import PlatformClient, PlatformError

@backoff.on_exception(
    backoff.expo,
    PlatformError,
    max_tries=5,
    giveup=lambda e: e.status_code < 500
)
def create_service(spec):
    return client.services.create(spec)
```

## Testing & Validation

### Schema Validation

```yaml
# JSON Schema for service spec
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["name", "runtime"],
  "properties": {
    "name": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$",
      "minLength": 3,
      "maxLength": 63
    },
    "runtime": {
      "type": "string",
      "enum": ["node18", "python311", "go121", "java17"]
    },
    "replicas": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "default": 3
    }
  }
}
```

### Dry Run

```bash
# Validate without creating
platform service create --file service.yaml --dry-run

# Output shows what would be created
# Service 'user-service' would be created with:
#   - Runtime: python311
#   - Replicas: 3
#   - Resources: 500m CPU, 512Mi memory
#   - URL: https://user-service.company.com
```

### Policy Validation

```yaml
# OPA policy for service creation
package platform.services

deny[msg] {
  input.spec.replicas < 2
  input.metadata.labels.tier == "critical"
  msg := "Critical services must have at least 2 replicas"
}

deny[msg] {
  input.spec.resources.requests.memory < "256Mi"
  msg := "Services must request at least 256Mi memory"
}
```

## Rate Limiting

### Implementation

```yaml
# Rate limit configuration
rateLimit:
  global:
    requests: 1000
    period: 1m

  perUser:
    requests: 100
    period: 1m

  perEndpoint:
    /services:
      POST:
        requests: 10
        period: 1m
```

### Response Headers

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 75
X-RateLimit-Reset: 1640000000
```

## Documentation

### Interactive Documentation

```yaml
# Swagger UI configuration
swagger:
  enabled: true
  url: https://platform.company.com/docs

  examples:
    createService:
      summary: Create a simple web service
      value:
        name: my-service
        runtime: node18
        replicas: 3
```

### Code Generation

```bash
# Generate client from OpenAPI spec
platform-cli codegen \
  --spec platform-api.yaml \
  --language python \
  --output sdk/python/

# Generate TypeScript types
platform-cli codegen \
  --spec platform-api.yaml \
  --language typescript \
  --output sdk/typescript/types/
```

## Best Practices

### 1. Design for Evolution

- Use API versioning from day one
- Support multiple versions simultaneously
- Provide clear migration paths
- Deprecate gracefully with notice

### 2. Optimize for Common Cases

- Make common operations simple
- Provide shortcuts for frequent tasks
- Bundle related operations
- Cache aggressively

### 3. Provide Rich Feedback

- Detailed error messages
- Actionable suggestions
- Links to documentation
- Request IDs for support

### 4. Enable Automation

- Idempotent operations
- Support for CI/CD
- Webhook notifications
- Event streams

### 5. Measure and Iterate

- Track API usage
- Monitor error rates
- Collect user feedback
- A/B test improvements

## Monitoring & Analytics

### API Metrics

```yaml
metrics:
  - requests_total
    labels: [method, endpoint, status]

  - request_duration_seconds
    labels: [method, endpoint]
    buckets: [0.01, 0.05, 0.1, 0.5, 1, 5]

  - errors_total
    labels: [method, endpoint, error_code]

  - active_connections
    type: gauge
```

### Usage Analytics

```sql
-- Most used endpoints
SELECT
  endpoint,
  COUNT(*) as requests,
  AVG(duration_ms) as avg_duration
FROM api_requests
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY endpoint
ORDER BY requests DESC;

-- Error rates by endpoint
SELECT
  endpoint,
  COUNT(*) as total_requests,
  SUM(CASE WHEN status >= 400 THEN 1 ELSE 0 END) as errors,
  SUM(CASE WHEN status >= 400 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as error_rate
FROM api_requests
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY endpoint
HAVING error_rate > 1
ORDER BY error_rate DESC;
```

## Resources

- REST API Design: https://restfulapi.net/
- OpenAPI Specification: https://swagger.io/specification/
- gRPC: https://grpc.io/docs/what-is-grpc/
- GraphQL: https://graphql.org/learn/
- JSON Schema: https://json-schema.org/
