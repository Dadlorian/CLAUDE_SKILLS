# Serverless Event Sources Reference

## Overview

Event sources are the triggers that invoke serverless functions. Understanding event sources is critical for designing event-driven serverless architectures.

## Event-Driven Architecture Patterns

### Event Types

1. **Event Notification**: Inform that something happened
   - Example: "File uploaded to S3"
   - Lightweight payload
   - Receiver fetches details if needed

2. **Event-Carried State Transfer**: Event contains full state
   - Example: Complete order object
   - Self-contained payload
   - Reduces coupling, increases payload size

3. **Event Sourcing**: Events as source of truth
   - Append-only event log
   - State derived from events
   - Complete audit trail

## AWS Event Sources

### HTTP/API Sources

#### API Gateway (REST/HTTP)
```yaml
Type: Synchronous
Use Cases: REST APIs, webhooks
Limits:
  - Timeout: 29 seconds
  - Payload: 10 MB
  - Throttling: 10,000 RPS (default)
```

**Integration Types**:
- **Lambda Proxy**: Request/response pass-through
- **Lambda Non-Proxy**: Custom mapping templates

**Features**:
- Request validation
- Rate limiting and quotas
- API keys
- Custom domain names
- CORS support
- Caching

#### Lambda Function URLs
```yaml
Type: Synchronous
Use Cases: Simple webhooks, single-function APIs
Benefits:
  - No API Gateway cost
  - Lower latency
  - Simpler setup
Limits:
  - No rate limiting (use on function)
  - No caching
  - No usage plans
```

#### Application Load Balancer (ALB)
```yaml
Type: Synchronous
Use Cases: HTTP services, health checks
Benefits:
  - Target group health checks
  - Path-based routing
  - Multi-value headers
Limits:
  - Timeout: 30 seconds
  - Regional only
```

### Storage Events

#### S3 Event Notifications
```yaml
Type: Asynchronous
Events:
  - s3:ObjectCreated:*
  - s3:ObjectRemoved:*
  - s3:ObjectRestore:*
  - s3:Replication:*
```

**Event Structure**:
```json
{
  "Records": [{
    "eventName": "ObjectCreated:Put",
    "s3": {
      "bucket": {"name": "my-bucket"},
      "object": {
        "key": "uploads/image.jpg",
        "size": 1024
      }
    }
  }]
}
```

**Best Practices**:
- Use prefix/suffix filters to reduce noise
- Handle partial failures in batch
- Implement idempotency (events may duplicate)
- Consider S3 Batch Operations for bulk processing

#### EFS (Elastic File System)
```yaml
Type: Mounted file system (not event-driven)
Use Cases: Shared state, large files, ML models
Limits:
  - Regional only
  - VPC required
  - 25 concurrent connections per instance
```

### Database Streams

#### DynamoDB Streams
```yaml
Type: Stream processing
Use Cases: Change data capture, real-time analytics
Characteristics:
  - Ordered records per shard
  - 24-hour retention
  - At-least-once delivery
```

**Record Types**:
- KEYS_ONLY
- NEW_IMAGE
- OLD_IMAGE
- NEW_AND_OLD_IMAGES

**Event Processing**:
```python
def handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_item = record['dynamodb']['NewImage']
        elif record['eventName'] == 'MODIFY':
            old_item = record['dynamodb']['OldImage']
            new_item = record['dynamodb']['NewImage']
        elif record['eventName'] == 'REMOVE':
            old_item = record['dynamodb']['OldImage']
```

**Configuration**:
- Batch size: 1-10,000
- Batch window: 0-300 seconds
- Concurrent batches per shard: 1-10
- Retry on failure until success or expiry
- Bisect on error: Split batch on failure

### Message Queues & Topics

#### SQS (Simple Queue Service)
```yaml
Type: Poll-based
Use Cases: Asynchronous processing, decoupling
Queue Types:
  - Standard: At-least-once, best-effort ordering
  - FIFO: Exactly-once, strict ordering
```

**Configuration**:
```yaml
Batch Size: 1-10 (Standard), 1-10 (FIFO)
Visibility Timeout: Match function timeout + buffer
MaxReceiveCount: 5 (typical), then DLQ
Long Polling: Reduce empty receives
```

**Advantages**:
- Built-in retry mechanism
- Visibility timeout prevents duplicate processing
- DLQ for poison messages
- Cost-effective buffering

#### SNS (Simple Notification Service)
```yaml
Type: Fan-out (one-to-many)
Use Cases: Broadcasting events, multiple consumers
Delivery: At-least-once
```

**Fan-Out Pattern** (SNS → multiple SQS → Lambdas):
```
SNS Topic
  ├── SQS Queue 1 → Lambda 1 (Email service)
  ├── SQS Queue 2 → Lambda 2 (Analytics)
  └── SQS Queue 3 → Lambda 3 (Audit log)
```

**Message Filtering**:
```json
{
  "event_type": ["order_created", "order_updated"],
  "amount": [{"numeric": [">=", 100]}]
}
```

### Streaming Platforms

#### Kinesis Data Streams
```yaml
Type: Real-time streaming
Use Cases: Log aggregation, real-time analytics, clickstreams
Characteristics:
  - 1-365 day retention
  - Ordered per partition key
  - Parallel processing (shards)
```

**Shard Capacity**:
- 1 MB/s or 1000 records/s writes per shard
- 2 MB/s reads per shard
- Lambda can consume at full shard capacity

**Configuration**:
```yaml
Batch Size: 100 (default) - 10,000
Batch Window: 0-300 seconds
Parallelization Factor: 1-10 per shard
Starting Position: LATEST | TRIM_HORIZON | AT_TIMESTAMP
```

**Enhanced Fan-Out**: Dedicated read throughput (2 MB/s per consumer)

#### Kinesis Data Firehose
```yaml
Type: Delivery stream (not direct Lambda trigger)
Use Cases: Data lake ingestion, transformation
Lambda Role: Transform data before delivery
```

### Event Buses

#### EventBridge (CloudWatch Events)
```yaml
Type: Event bus
Use Cases: Application events, scheduled tasks, cross-account events
```

**Event Sources**:
- AWS services (90+ services)
- Custom applications
- SaaS integrations (Salesforce, Datadog, etc.)
- Scheduled (cron/rate)

**Event Pattern Matching**:
```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "bucket": {"name": ["my-production-bucket"]},
    "object": {"size": [{"numeric": [">", 1048576]}]}
  }
}
```

**Advantages**:
- Schema registry
- Archive and replay
- Cross-account/region
- Content-based filtering
- API destinations (HTTP endpoints)

### Other AWS Sources

#### Step Functions
```yaml
Type: State machine tasks
Use Cases: Long-running workflows, orchestration
```

#### Cognito
```yaml
Events:
  - Pre Sign-up
  - Pre Authentication
  - Post Authentication
  - Pre Token Generation
```

#### ALB/CloudFront
- Origin request/response (Lambda@Edge)
- Viewer request/response

#### IoT Core
```yaml
Type: MQTT messages
Use Cases: IoT device events
```

## Azure Event Sources

### HTTP Sources

#### HTTP Trigger
```yaml
Type: Synchronous
Authorization Levels: Anonymous, Function, Admin
Features: Route parameters, query strings, request body
```

#### Event Grid
```yaml
Type: Publish-subscribe
Use Cases: Azure resource events, custom events
Characteristics:
  - 24-hour retry
  - Dead letter on failure
  - Event filtering
```

**Event Schema**:
```json
{
  "topic": "/subscriptions/.../resourceGroups/.../providers/Microsoft.Storage/storageAccounts/...",
  "subject": "/blobServices/default/containers/testcontainer/blobs/testfile.txt",
  "eventType": "Microsoft.Storage.BlobCreated",
  "eventTime": "2024-01-15T13:00:00Z",
  "data": {
    "api": "PutBlob",
    "url": "https://..."
  }
}
```

### Storage Events

#### Blob Storage
```yaml
Events:
  - Microsoft.Storage.BlobCreated
  - Microsoft.Storage.BlobDeleted
  - Microsoft.Storage.BlobRenamed
Delivery: Via Event Grid
```

#### Queue Storage
```yaml
Type: Poll-based queue
Use Cases: Asynchronous work queues
Features:
  - Visibility timeout
  - Poison queue (after 5 failures)
```

### Messaging

#### Service Bus
```yaml
Queue: One-to-one
Topic/Subscription: One-to-many
Features:
  - Sessions (ordered processing)
  - Dead letter queue
  - Scheduled delivery
  - Duplicate detection
```

#### Event Hubs
```yaml
Type: Streaming platform (like Kinesis)
Use Cases: Telemetry, log aggregation
Partitions: 2-32 (Standard), up to 2000 (Dedicated)
Retention: 1-90 days
```

### Database

#### Cosmos DB Trigger (Change Feed)
```yaml
Type: Change data capture
Use Cases: Real-time sync, event sourcing
Delivery: At-least-once
Lease Container: Required for checkpointing
```

### Other Azure Sources

#### Timer Trigger
```yaml
Type: CRON-based schedule
Expression: "0 */5 * * * *" (every 5 minutes)
```

#### SignalR
```yaml
Use Case: Real-time web applications
Pattern: Client connects, backend pushes via Functions
```

## Google Cloud Event Sources

### HTTP Sources

#### HTTP Functions
```yaml
Type: Direct HTTPS endpoint
Authentication: IAM, unauthenticated
```

#### Cloud Load Balancing
```yaml
Type: Serverless NEG (Network Endpoint Group)
Features: Global load balancing, SSL, CDN
```

### Storage Events

#### Cloud Storage
```yaml
Events (2nd gen):
  - google.cloud.storage.object.v1.finalized
  - google.cloud.storage.object.v1.deleted
  - google.cloud.storage.object.v1.archived
  - google.cloud.storage.object.v1.metadataUpdated
```

### Messaging

#### Pub/Sub
```yaml
Type: Global message bus
Delivery: At-least-once
Features:
  - Message ordering
  - Dead letter topics
  - Filtering
  - Retry policies
```

**Subscription Types**:
- Push: HTTP endpoint (Cloud Functions, Cloud Run)
- Pull: Application polls
- BigQuery: Direct to BigQuery
- Cloud Storage: Direct to buckets

### Database

#### Firestore
```yaml
Events:
  - document.created
  - document.updated
  - document.deleted
  - document.written
Path Pattern: "users/{userId}/orders/{orderId}"
```

### Cloud Functions-Specific

#### Cloud Scheduler
```yaml
Type: Managed cron
Targets: HTTP, Pub/Sub, App Engine
Example: "0 2 * * *" (daily at 2 AM)
```

#### Eventarc (2nd gen)
```yaml
Sources:
  - Cloud Storage
  - Pub/Sub
  - Cloud Audit Logs (100+ services)
  - Direct events
  - Custom events
```

**Audit Log Example**:
```bash
# Trigger on BigQuery table creation
--trigger-event-filters="type=google.cloud.audit.log.v1.written"
--trigger-event-filters="serviceName=bigquery.googleapis.com"
--trigger-event-filters="methodName=google.cloud.bigquery.v2.JobService.InsertJob"
```

## Event Patterns & Best Practices

### Idempotency
**Problem**: Events may be delivered more than once

**Solutions**:
1. **Idempotency Token**:
   ```python
   def process_order(event):
       order_id = event['order_id']
       idempotency_key = event.get('request_id')

       # Check if already processed
       if db.get(idempotency_key):
           return {"status": "already_processed"}

       # Process
       result = process(order_id)

       # Store idempotency key
       db.put(idempotency_key, result, ttl=86400)
       return result
   ```

2. **Database Constraints**: Use unique constraints
3. **Conditional Writes**: DynamoDB condition expressions

### Error Handling

#### Retry Strategies
```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5)
)
def call_external_api(data):
    # Transient failures will retry
    response = requests.post(API_URL, json=data)
    response.raise_for_status()
    return response.json()
```

#### Dead Letter Queues (DLQ)
```yaml
Purpose: Capture failed events for investigation
Configuration:
  - Set maxReceiveCount (SQS) or max retries (Lambda async)
  - Route failures to DLQ (SQS/SNS)
  - Alert on DLQ depth
  - Manual inspection and replay
```

#### Circuit Breaker
```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
def call_downstream_service(data):
    # Prevents cascading failures
    return downstream_api.call(data)
```

### Event Filtering

**Why Filter**:
- Reduce function invocations
- Lower costs
- Simplify function logic
- Improve performance

**Where to Filter**:
1. **At Source**: S3 prefix/suffix, EventBridge patterns
2. **At Queue**: SNS filter policies
3. **In Function**: Early return (least efficient)

**Example (EventBridge)**:
```json
{
  "source": ["myapp.orders"],
  "detail-type": ["Order Created"],
  "detail": {
    "amount": [{"numeric": [">", 100]}],
    "region": ["us-west-2", "us-east-1"]
  }
}
```

### Batch Processing
```yaml
Advantages:
  - Fewer function invocations
  - Lower costs
  - Amortized initialization
  - Bulk database operations

Considerations:
  - Timeout limits
  - Memory limits
  - Partial failure handling
  - Increased latency
```

**Best Practices**:
- Process all records even if some fail
- Return partial batch failure (SQS, Kinesis)
- Track failed records for DLQ or retry

**Example (SQS Batch)**:
```python
def handler(event, context):
    failed_items = []

    for record in event['Records']:
        try:
            process_message(record)
        except Exception as e:
            failed_items.append({
                "itemIdentifier": record['messageId']
            })

    # Return failed items (Lambda deletes successful ones)
    return {"batchItemFailures": failed_items}
```

### Ordering Guarantees

#### Strict Ordering
```yaml
SQS FIFO: Same message group ID
Kinesis: Same partition key
Service Bus: Sessions
Pub/Sub: Ordering key
```

#### Best-Effort Ordering
```yaml
SQS Standard: No ordering guarantee
SNS: No ordering guarantee
EventBridge: No ordering guarantee
```

**Handling Out-of-Order**:
- Event versioning/timestamps
- Conflict resolution (last-write-wins, custom logic)
- Event sourcing patterns

### Event Schema Evolution

#### Versioning Strategies
1. **Additive Changes**: Add optional fields (backward compatible)
2. **Version Field**: Include version in event
3. **Separate Event Types**: `order.created.v1`, `order.created.v2`
4. **Schema Registry**: Centralized schema management (EventBridge, Confluent)

**Example**:
```json
{
  "version": "2.0",
  "event_type": "order.created",
  "timestamp": "2024-01-15T12:00:00Z",
  "data": {
    "order_id": "12345",
    "amount": 99.99,
    "new_field": "value"  // Added in v2
  }
}
```

## Multi-Cloud Event Standardization

### CloudEvents
Industry standard for event data (CNCF).

**Specification**:
```json
{
  "specversion": "1.0",
  "type": "com.example.order.created",
  "source": "https://example.com/orders",
  "id": "A234-1234-1234",
  "time": "2024-01-15T12:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "order_id": "12345",
    "amount": 99.99
  }
}
```

**Adoption**:
- Google Cloud Functions (2nd gen): Native support
- Azure Event Grid: Supports CloudEvents schema
- AWS EventBridge: Custom events can use CloudEvents format
- Knative: Native CloudEvents

## Monitoring Event Sources

### Metrics to Track
```yaml
Throughput:
  - Events received
  - Events processed
  - Processing rate

Latency:
  - Event age (producer → function)
  - Processing duration
  - End-to-end latency

Errors:
  - Function errors
  - Throttles
  - DLQ messages

Backlog:
  - Queue depth (SQS)
  - Iterator age (Kinesis/DynamoDB)
  - Unacked messages (Pub/Sub)
```

### Alerts
```yaml
Critical:
  - DLQ depth > 0
  - Error rate > 1%
  - Iterator age > 1 hour

Warning:
  - Processing lag > 5 minutes
  - Throttles > 0
  - Cost anomaly
```

## Resources

- [AWS Lambda Event Sources](https://docs.aws.amazon.com/lambda/latest/dg/invocation-eventsourcemapping.html)
- [Azure Functions Triggers and Bindings](https://docs.microsoft.com/azure/azure-functions/functions-triggers-bindings)
- [Google Cloud Functions Triggers](https://cloud.google.com/functions/docs/calling)
- [CloudEvents Specification](https://cloudevents.io/)
- [Eventarc Documentation](https://cloud.google.com/eventarc/docs)
