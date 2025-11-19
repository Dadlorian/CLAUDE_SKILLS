# Google Cloud Functions Reference Guide

## Overview

Google Cloud Functions is a lightweight, event-driven serverless compute platform that executes code in response to cloud events. Fully integrated with the Google Cloud ecosystem.

## Generations

### Cloud Functions (2nd gen) - Recommended
- Built on **Cloud Run** infrastructure
- Based on **Knative** and **CloudEvents**
- Longer timeouts (60 minutes vs 9 minutes)
- Larger instances (16 GB RAM vs 8 GB)
- Traffic splitting and min instances
- Eventarc for unified eventing
- Better integration with Cloud Run features

### Cloud Functions (1st gen) - Legacy
- Original implementation
- Limited to 8 GB RAM, 9-minute timeout
- Legacy event formats
- Still supported but consider 2nd gen for new projects

## Core Concepts

### Function
A Cloud Function consists of:
- **Source code**: Node.js, Python, Go, Java, Ruby, PHP, .NET
- **Trigger**: HTTP, Cloud Storage, Pub/Sub, Firestore, etc.
- **Runtime configuration**: Memory, timeout, environment variables
- **Region**: Deployment location

### Runtime Environment
```
Request → Load Balancer → Function Instance
                            ↓
                    Container (if cold)
                            ↓
                    Execute Handler
                            ↓
                    Return Response
```

## Supported Runtimes

| Runtime | Versions | Cold Start | Best For |
|---------|----------|------------|----------|
| **Node.js** | 16, 18, 20 | 100-400ms | APIs, webhooks, lightweight processing |
| **Python** | 3.9, 3.10, 3.11, 3.12 | 200-600ms | Data processing, ML, backend services |
| **Go** | 1.18, 1.19, 1.20, 1.21 | 100-300ms | High performance, compiled efficiency |
| **Java** | 11, 17, 21 | 2-5s | Enterprise applications |
| **Ruby** | 3.0, 3.1, 3.2 | 300-800ms | Web applications, scripting |
| **PHP** | 8.1, 8.2 | 200-500ms | Web backends, WordPress integration |
| **.NET** | 6, 8 | 500ms-2s | Windows workloads, enterprise |

## Function Types

### HTTP Functions
Invoked via HTTP requests.

**Node.js Example**:
```javascript
const functions = require('@google-cloud/functions-framework');

functions.http('helloHttp', (req, res) => {
  res.status(200).send('Hello, World!');
});
```

**Python Example**:
```python
import functions_framework

@functions_framework.http
def hello_http(request):
    return 'Hello, World!'
```

**Go Example**:
```go
package function

import (
    "fmt"
    "net/http"
)

func HelloHTTP(w http.ResponseWriter, r *http.Request) {
    fmt.Fprint(w, "Hello, World!")
}
```

### Event-Driven Functions (2nd gen)
Use CloudEvents format for all events.

**Cloud Storage Example** (Python):
```python
import functions_framework
from cloudevents.http import CloudEvent

@functions_framework.cloud_event
def hello_gcs(cloud_event: CloudEvent):
    data = cloud_event.data

    bucket = data["bucket"]
    name = data["name"]

    print(f"File {name} uploaded to {bucket}")
```

**Pub/Sub Example** (Node.js):
```javascript
const functions = require('@google-cloud/functions-framework');

functions.cloudEvent('helloPubSub', cloudEvent => {
  const base64data = cloudEvent.data.message.data;
  const message = Buffer.from(base64data, 'base64').toString();

  console.log(`Message: ${message}`);
});
```

**Firestore Example** (Python):
```python
@functions_framework.cloud_event
def hello_firestore(cloud_event: CloudEvent):
    data = cloud_event.data

    print(f"Document: {data['value']['name']}")
    print(f"Operation: {cloud_event['type']}")
```

## Triggers & Events

### HTTP Trigger
- Direct HTTP requests
- HTTPS endpoint automatically provisioned
- Supports CORS
- Can integrate with Cloud Load Balancer

**Authentication Options**:
- **Allow unauthenticated**: Public access
- **Require authentication**: Cloud IAM authentication

### Cloud Storage Trigger
**Events**:
- `google.cloud.storage.object.v1.finalized` - Object created/overwritten
- `google.cloud.storage.object.v1.deleted` - Object deleted
- `google.cloud.storage.object.v1.archived` - Object archived
- `google.cloud.storage.object.v1.metadataUpdated` - Object metadata changed

**Example Filter**:
```bash
gcloud functions deploy myFunction \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=my-bucket"
```

### Pub/Sub Trigger
Subscribe to Pub/Sub topic messages.

**Characteristics**:
- At-least-once delivery
- Automatic retry on failure
- Dead letter topic for failed messages
- Ordered messages (with ordering key)

**Deployment**:
```bash
gcloud functions deploy myFunction \
  --trigger-topic=my-topic \
  --runtime=python311 \
  --entry-point=hello_pubsub
```

### Firestore Trigger
React to document changes.

**Events**:
- `google.cloud.firestore.document.v1.created`
- `google.cloud.firestore.document.v1.updated`
- `google.cloud.firestore.document.v1.deleted`
- `google.cloud.firestore.document.v1.written` (created or updated)

**Example**:
```bash
gcloud functions deploy myFunction \
  --trigger-event-filters="type=google.cloud.firestore.document.v1.written" \
  --trigger-event-filters="database=(default)" \
  --trigger-event-filters-path-pattern="document=users/{userId}"
```

### Firebase Triggers
- **Authentication**: User creation, deletion
- **Realtime Database**: Data written, deleted
- **Remote Config**: Template updated
- **Analytics**: Log events

### Cloud Scheduler
CRON-based scheduled invocations.

**Create Scheduler**:
```bash
gcloud scheduler jobs create http my-job \
  --schedule="0 */2 * * *" \
  --uri="https://REGION-PROJECT_ID.cloudfunctions.net/myFunction" \
  --oidc-service-account-email=SA_EMAIL
```

### Eventarc (2nd gen only)
Unified eventing platform supporting 100+ event sources.

**Example** (Cloud Audit Logs):
```bash
gcloud functions deploy audit-function \
  --trigger-event-filters="type=google.cloud.audit.log.v1.written" \
  --trigger-event-filters="serviceName=storage.googleapis.com" \
  --trigger-event-filters="methodName=storage.objects.create"
```

## Configuration

### Memory & CPU
```yaml
Memory: 128 MB - 32 GB (2nd gen), 8 GB (1st gen)
  - CPU scales with memory
  - 1 vCPU at 1 GB (2nd gen)
  - 2 vCPUs at 2 GB
  - 4 vCPUs at 4 GB, etc.
```

**Deployment**:
```bash
gcloud functions deploy myFunction \
  --memory=2GB \
  --cpu=2
```

### Timeout
```yaml
1st gen: 1s - 540s (9 minutes)
2nd gen: 1s - 3600s (60 minutes)
Default: 60s
```

### Concurrency (2nd gen)
```yaml
Default: 1 request per instance
Max: 1000 concurrent requests per instance
```

**Higher concurrency**:
- Reduces cold starts
- Lower cost (fewer instances)
- Shared memory/connections

**Lower concurrency**:
- Isolation between requests
- Predictable performance

### Min/Max Instances (2nd gen)
```yaml
Min Instances: 0-1000 (keep warm, eliminate cold starts)
Max Instances: 0-3000 (limit cost, prevent runaway scaling)
```

**Use Cases**:
- Min > 0: Latency-sensitive applications
- Max < default: Cost control, downstream rate limiting

### Environment Variables
```bash
gcloud functions deploy myFunction \
  --set-env-vars=KEY1=value1,KEY2=value2 \
  --set-secrets=SECRET1=projects/PROJECT/secrets/secret1:latest
```

**Secret Manager Integration**:
```python
import os

# Automatically injected by Secret Manager
api_key = os.environ['SECRET_API_KEY']
```

## Deployment

### gcloud CLI
```bash
# Deploy HTTP function
gcloud functions deploy my-function \
  --runtime=python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point=hello_http \
  --region=us-central1 \
  --memory=512MB \
  --timeout=60s

# Deploy Pub/Sub function
gcloud functions deploy my-pubsub-function \
  --runtime=nodejs20 \
  --trigger-topic=my-topic \
  --entry-point=processPubSub

# Deploy Cloud Storage function (2nd gen)
gcloud functions deploy storage-function \
  --gen2 \
  --runtime=python311 \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=my-bucket"
```

### Terraform
```hcl
resource "google_cloudfunctions2_function" "function" {
  name     = "my-function"
  location = "us-central1"

  build_config {
    runtime     = "python311"
    entry_point = "hello_http"
    source {
      storage_source {
        bucket = google_storage_bucket.bucket.name
        object = google_storage_bucket_object.object.name
      }
    }
  }

  service_config {
    max_instance_count = 100
    min_instance_count = 1
    available_memory   = "512M"
    timeout_seconds    = 60
    environment_variables = {
      ENV = "production"
    }
  }
}
```

### Cloud Build (CI/CD)
```yaml
steps:
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    args:
      - gcloud
      - functions
      - deploy
      - my-function
      - --runtime=python311
      - --trigger-http
      - --region=us-central1
      - --source=.
```

## Local Development

### Functions Framework
**Python**:
```bash
pip install functions-framework

# Run locally
functions-framework --target=hello_http --debug
```

**Node.js**:
```bash
npm install @google-cloud/functions-framework

# package.json
{
  "scripts": {
    "start": "functions-framework --target=helloHttp"
  }
}
```

**Testing HTTP Function**:
```bash
curl http://localhost:8080
```

**Testing CloudEvent Function**:
```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -H "ce-id: 1234" \
  -H "ce-source: //pubsub.googleapis.com" \
  -H "ce-type: google.cloud.pubsub.topic.v1.messagePublished" \
  -H "ce-specversion: 1.0" \
  -d '{
    "message": {
      "data": "SGVsbG8sIFdvcmxkIQ==",
      "attributes": {}
    }
  }'
```

## Monitoring & Logging

### Cloud Logging
**Automatic Logging**:
- `console.log()` / `print()` → INFO logs
- `console.error()` / `print(..., file=sys.stderr)` → ERROR logs
- Unhandled exceptions → ERROR logs

**Structured Logging**:
```python
import json

def hello_http(request):
    log_entry = {
        "severity": "INFO",
        "message": "Processing request",
        "request_id": request.headers.get('X-Request-Id'),
        "user_agent": request.headers.get('User-Agent')
    }
    print(json.dumps(log_entry))
```

**Log Queries**:
```
resource.type="cloud_function"
resource.labels.function_name="my-function"
severity>=ERROR
```

### Cloud Monitoring
**Automatic Metrics**:
- `cloudfunctions.googleapis.com/function/execution_count`
- `cloudfunctions.googleapis.com/function/execution_times`
- `cloudfunctions.googleapis.com/function/user_memory_bytes`
- `cloudfunctions.googleapis.com/function/instance_count`
- `cloudfunctions.googleapis.com/function/active_instances`

**Custom Metrics**:
```python
from google.cloud import monitoring_v3

client = monitoring_v3.MetricServiceClient()
project_name = f"projects/{project_id}"

series = monitoring_v3.TimeSeries()
series.metric.type = "custom.googleapis.com/my_metric"
series.resource.type = "cloud_function"

point = monitoring_v3.Point()
point.value.int64_value = 42
series.points = [point]

client.create_time_series(name=project_name, time_series=[series])
```

### Cloud Trace
**Automatic Tracing**: HTTP functions automatically traced

**Custom Spans**:
```python
from google.cloud import trace_v2

tracer = trace_v2.Client()

with tracer.span(name='process_data'):
    # Traced operation
    process_data()
```

### Error Reporting
Automatic error detection and grouping:
- Unhandled exceptions
- HTTP 5xx errors
- Structured error logs

## Networking

### VPC Connector (Serverless VPC Access)
Access resources in VPC (databases, internal services).

**Create Connector**:
```bash
gcloud compute networks vpc-access connectors create my-connector \
  --region=us-central1 \
  --subnet-project=PROJECT_ID \
  --subnet=my-subnet
```

**Deploy with VPC**:
```bash
gcloud functions deploy my-function \
  --vpc-connector=my-connector \
  --egress-settings=private-ranges-only
```

**Egress Settings**:
- `private-ranges-only`: Only private IPs via VPC
- `all-traffic`: All traffic via VPC (costly, slower)

### VPC Firewall Rules
Control egress from functions in VPC.

### Cloud Armor (2nd gen with Load Balancer)
DDoS protection and WAF for HTTP functions.

## Security

### Authentication & Authorization

**IAM-based Invocation**:
```bash
# Grant invoker permission
gcloud functions add-iam-policy-binding my-function \
  --member='user:alice@example.com' \
  --role='roles/cloudfunctions.invoker'
```

**Service Account**:
```bash
gcloud functions deploy my-function \
  --service-account=my-service-account@PROJECT.iam.gserviceaccount.com
```

**Identity-Aware Proxy (IAP)**:
- User authentication for HTTP functions
- Integration with Google Sign-In

### Secrets Management
**Secret Manager**:
```bash
# Mount secret as environment variable
gcloud functions deploy my-function \
  --set-secrets=API_KEY=my-secret:latest

# Mount secret as file
gcloud functions deploy my-function \
  --set-secrets=/secrets/api-key=my-secret:latest
```

**Access in Code**:
```python
import os

# From environment variable
api_key = os.environ['API_KEY']

# From mounted file
with open('/secrets/api-key', 'r') as f:
    api_key = f.read()
```

## Pricing (2nd gen)

### Compute
```
Invocations: $0.40 per million
vCPU: $0.00001667 per vCPU-second
Memory: $0.00000231 per GB-second
```

### Free Tier (per month)
```
Invocations: 2 million
vCPU-time: 400,000 vCPU-seconds
Memory: 400,000 GB-seconds
Outbound data: 5 GB
```

### Example Calculation
```
Scenario: 10M requests/month, 512MB, 200ms avg duration

Invocations:
  (10M - 2M free) × $0.40 / 1M = $3.20

Compute (assuming 0.5 vCPU at 512MB):
  10M × 0.2s × 0.5 vCPU = 1M vCPU-seconds
  (1M - 400k free) × $0.00001667 = $10.00

  10M × 0.2s × 0.5 GB = 1M GB-seconds
  (1M - 400k free) × $0.00000231 = $1.39

Total: $14.59/month
```

## Best Practices

### Performance
1. Use 2nd gen for better performance and features
2. Increase memory for CPU-bound tasks
3. Use concurrency > 1 for high throughput (2nd gen)
4. Set min instances for latency-sensitive apps
5. Optimize cold starts (minimize dependencies, use compiled languages)

### Cost Optimization
1. Right-size memory allocation
2. Use concurrency to reduce instance count
3. Set max instances to prevent runaway costs
4. Use Cloud Scheduler instead of warming functions
5. Minimize execution time

### Security
1. Use least privilege service accounts
2. Store secrets in Secret Manager
3. Enable VPC when accessing private resources
4. Require authentication (no --allow-unauthenticated in production)
5. Implement input validation

### Reliability
1. Implement idempotency (especially for retries)
2. Set appropriate timeouts
3. Use dead letter topics for Pub/Sub
4. Monitor error rates and latencies
5. Test failure scenarios

## Limits & Quotas

### 2nd Gen Limits
- Max execution time: 60 minutes
- Max memory: 32 GB
- Max instances per function: 3,000
- Max concurrent requests per instance: 1,000
- Max deployment size: 500 MB (compressed), 5 GB (uncompressed)

### 1st Gen Limits
- Max execution time: 9 minutes
- Max memory: 8 GB
- Max instances per function: 3,000
- Concurrent requests per instance: 1
- Max deployment size: 100 MB (compressed), 500 MB (uncompressed)

## Migration from 1st gen to 2nd gen

**Key Differences**:
1. Event format: Custom → CloudEvents
2. Signature: Different handler signatures
3. Configuration: New deployment commands
4. Networking: Different VPC setup

**Example Migration (Python)**:
```python
# 1st gen
def hello_pubsub(event, context):
    import base64
    message = base64.b64decode(event['data']).decode('utf-8')
    print(f'Message: {message}')

# 2nd gen
@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    import base64
    message = base64.b64decode(cloud_event.data['message']['data']).decode('utf-8')
    print(f'Message: {message}')
```

## Resources

### Official Documentation
- [Cloud Functions Docs](https://cloud.google.com/functions/docs)
- [CloudEvents Spec](https://cloudevents.io/)
- [Eventarc](https://cloud.google.com/eventarc/docs)

### Tools
- [Functions Framework](https://cloud.google.com/functions/docs/functions-framework)
- [gcloud CLI](https://cloud.google.com/sdk/gcloud/reference/functions)

### Community
- [GitHub Samples](https://github.com/GoogleCloudPlatform/functions-samples)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/google-cloud-functions)
