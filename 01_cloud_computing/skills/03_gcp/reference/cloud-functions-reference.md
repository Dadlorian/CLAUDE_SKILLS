# Cloud Functions Reference

## Overview

Google Cloud Functions is a serverless execution environment for building and connecting cloud services. It allows you to write simple, single-purpose functions that are attached to events.

## Generations Comparison

| Feature | 1st Gen | 2nd Gen |
|---------|---------|---------|
| **Runtime** | Cloud Functions runtime | Cloud Run infrastructure |
| **Max Timeout** | 9 minutes | 60 minutes (HTTP), 60 minutes (event) |
| **Max Memory** | 8 GB | 32 GB |
| **Max CPU** | 2 vCPUs | 8 vCPUs |
| **Max Instances** | 3,000 | 1,000 per region |
| **Concurrency** | 1 request/instance | Up to 1,000 concurrent requests/instance |
| **Min Instances** | 0-1 | 0-100 |
| **Cold Start** | Longer | Shorter |
| **VPC Connector** | Serverless VPC Access | Direct VPC |
| **Traffic Splitting** | No | Yes |
| **Cloud Events** | No | Yes (CloudEvents format) |
| **Pricing** | Per invocation + compute time | Per invocation + compute time + always-on cost |
| **Recommendation** | Legacy only | Use for all new functions |

## Supported Runtimes

### 2nd Generation
- **Node.js**: 16, 18, 20
- **Python**: 3.10, 3.11, 3.12
- **Go**: 1.19, 1.20, 1.21
- **Java**: 11, 17
- **.NET**: Core 3.1, 6, 7
- **Ruby**: 3.0, 3.1, 3.2
- **PHP**: 8.1, 8.2

### 1st Generation (Legacy)
- Node.js 10, 12, 14, 16, 18, 20
- Python 3.7, 3.8, 3.9, 3.10, 3.11
- Go 1.13, 1.16, 1.19, 1.20, 1.21
- Java 11, 17
- .NET Core 3.1, 6
- Ruby 2.6, 2.7, 3.0
- PHP 7.4, 8.1

## Trigger Types

### HTTP Triggers
Direct HTTP requests (GET, POST, etc.)

**1st Gen Example** (Python):
```python
def hello_http(request):
    request_json = request.get_json(silent=True)
    name = request_json.get('name', 'World') if request_json else 'World'
    return f'Hello {name}!'
```

**2nd Gen Example** (Python):
```python
import functions_framework

@functions_framework.http
def hello_http(request):
    request_json = request.get_json(silent=True)
    name = request_json.get('name', 'World') if request_json else 'World'
    return f'Hello {name}!'
```

**Deployment**:
```bash
# 2nd gen
gcloud functions deploy hello-http \
    --gen2 \
    --runtime=python312 \
    --region=us-central1 \
    --source=. \
    --entry-point=hello_http \
    --trigger-http \
    --allow-unauthenticated
```

### Cloud Storage Triggers
Respond to object create, delete, archive, metadata update events.

**Events**:
- `google.cloud.storage.object.v1.finalized` (object created/overwritten)
- `google.cloud.storage.object.v1.deleted` (object deleted)
- `google.cloud.storage.object.v1.archived` (object archived)
- `google.cloud.storage.object.v1.metadataUpdated` (metadata updated)

**2nd Gen Example** (Python):
```python
import functions_framework
from cloudevents.http import CloudEvent

@functions_framework.cloud_event
def process_file(cloud_event: CloudEvent) -> None:
    data = cloud_event.data
    bucket = data["bucket"]
    name = data["name"]
    print(f"Processing file: gs://{bucket}/{name}")
```

**Deployment**:
```bash
gcloud functions deploy process-file \
    --gen2 \
    --runtime=python312 \
    --region=us-central1 \
    --source=. \
    --entry-point=process_file \
    --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
    --trigger-event-filters="bucket=my-bucket"
```

### Pub/Sub Triggers
Process messages from Pub/Sub topics.

**2nd Gen Example** (Python):
```python
import functions_framework
import base64
import json

@functions_framework.cloud_event
def process_pubsub(cloud_event):
    # Decode Pub/Sub message
    pubsub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode()
    print(f"Received message: {pubsub_message}")

    # Process message
    data = json.loads(pubsub_message)
    # Your processing logic here
```

**Deployment**:
```bash
gcloud functions deploy process-pubsub \
    --gen2 \
    --runtime=python312 \
    --region=us-central1 \
    --source=. \
    --entry-point=process_pubsub \
    --trigger-topic=my-topic
```

### Firestore Triggers
React to document create, update, delete events.

**Events**:
- `google.cloud.firestore.document.v1.created`
- `google.cloud.firestore.document.v1.updated`
- `google.cloud.firestore.document.v1.deleted`
- `google.cloud.firestore.document.v1.written` (created or updated)

**2nd Gen Example** (Python):
```python
import functions_framework
from cloudevents.http import CloudEvent

@functions_framework.cloud_event
def on_document_created(cloud_event: CloudEvent):
    data = cloud_event.data
    path = data["value"]["name"]
    fields = data["value"]["fields"]
    print(f"Document created at: {path}")
    print(f"Fields: {fields}")
```

**Deployment**:
```bash
gcloud functions deploy on-document-created \
    --gen2 \
    --runtime=python312 \
    --region=us-central1 \
    --source=. \
    --entry-point=on_document_created \
    --trigger-event-filters="type=google.cloud.firestore.document.v1.created" \
    --trigger-event-filters="database=(default)" \
    --trigger-location=us-central1 \
    --trigger-event-filters-path-pattern="document=users/{userId}"
```

### Cloud Audit Logs Triggers (Eventarc)
Trigger on any GCP service that produces audit logs.

**Example** (Python):
```python
@functions_framework.cloud_event
def on_compute_instance_created(cloud_event):
    data = cloud_event.data
    payload = data["protoPayload"]
    resource_name = payload["resourceName"]
    print(f"Instance created: {resource_name}")
```

**Deployment**:
```bash
gcloud functions deploy on-compute-instance-created \
    --gen2 \
    --runtime=python312 \
    --region=us-central1 \
    --source=. \
    --entry-point=on_compute_instance_created \
    --trigger-event-filters="type=google.cloud.audit.log.v1.written" \
    --trigger-event-filters="serviceName=compute.googleapis.com" \
    --trigger-event-filters="methodName=v1.compute.instances.insert"
```

### Firebase Triggers (1st Gen)
- **Firebase Authentication**: User creation, deletion
- **Firebase Realtime Database**: Data written, updated, deleted
- **Firebase Remote Config**: Config updated
- **Firebase Analytics**: Events logged

## Configuration Options

### Memory and CPU
**2nd Gen**:
```bash
--memory=512Mi     # 128Mi, 256Mi, 512Mi, 1Gi, 2Gi, 4Gi, 8Gi, 16Gi, 32Gi
--cpu=1            # 0.08, 0.17, 0.33, 0.5, 1, 2, 4, 6, 8
```

**1st Gen**:
```bash
--memory=256MB     # 128MB, 256MB, 512MB, 1024MB, 2048MB, 4096MB, 8192MB
```

**CPU Allocation**:
| Memory (2nd Gen) | CPUs |
|-----------------|------|
| 128-512 Mi | 0.08-0.5 |
| 1 Gi | 0.5-1 |
| 2 Gi | 1-2 |
| 4 Gi | 2-4 |
| 8+ Gi | 4-8 |

### Timeout
```bash
# 2nd gen
--timeout=60s      # Max: 3600s (60 minutes)

# 1st gen
--timeout=540s     # Max: 540s (9 minutes)
```

### Concurrency (2nd Gen Only)
Number of concurrent requests per instance:
```bash
--concurrency=80   # Default: 1, Max: 1000
```

**Best Practices**:
- Start with concurrency=1 for CPU-intensive functions
- Increase to 80-100 for I/O-bound functions
- Maximum 1000 for very light operations

### Scaling
**Min/Max Instances**:
```bash
# 2nd gen
--min-instances=0      # Keep warm instances
--max-instances=100    # Limit scaling

# 1st gen
--min-instances=0
--max-instances=3000
```

**Auto Scaling** (2nd Gen):
```bash
--autoscaling-algorithm=concurrent-requests
--max-instance-request-concurrency=80
```

### Environment Variables
```bash
--set-env-vars="KEY1=value1,KEY2=value2"
--env-vars-file=env.yaml
```

**env.yaml**:
```yaml
KEY1: value1
KEY2: value2
DATABASE_URL: postgres://...
```

### Secrets (2nd Gen)
```bash
--set-secrets="DB_PASSWORD=db-password:latest,API_KEY=api-key:1"
```

## Networking

### VPC Access
**2nd Gen** (Direct VPC):
```bash
--vpc-connector=projects/PROJECT_ID/locations/REGION/connectors/CONNECTOR_NAME
--vpc-egress=all-traffic    # or private-ranges-only
```

**1st Gen** (Serverless VPC Access):
```bash
--vpc-connector=CONNECTOR_NAME
--egress-settings=all       # or private-ranges-only
```

### Ingress Settings
```bash
--ingress-settings=all                  # Allow all traffic
--ingress-settings=internal-only        # Only VPC and Cloud Load Balancing
--ingress-settings=internal-and-gclb    # Internal + GCLB
```

## Security

### Authentication
**Require Authentication**:
```bash
# Default - requires authentication
gcloud functions deploy my-function --no-allow-unauthenticated
```

**Allow Unauthenticated**:
```bash
gcloud functions deploy my-function --allow-unauthenticated
```

**Invoke with Service Account**:
```bash
gcloud functions add-iam-policy-binding my-function \
    --region=us-central1 \
    --member=serviceAccount:invoker@project.iam.gserviceaccount.com \
    --role=roles/cloudfunctions.invoker
```

### Service Account
**Runtime Service Account**:
```bash
--service-account=my-sa@project.iam.gserviceaccount.com
```

**IAM Permissions**:
```bash
# Grant function access to other services
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=serviceAccount:my-sa@project.iam.gserviceaccount.com \
    --role=roles/storage.objectViewer
```

## Best Practices

### 1. Use 2nd Generation
- Better performance
- More features
- Higher limits
- CloudEvents standard

### 2. Optimize Cold Starts
- Use min-instances for latency-sensitive functions
- Keep dependencies minimal
- Use global variables for reused resources
- Enable HTTP/2

### 3. Handle Errors Properly
```python
import functions_framework
from google.cloud import error_reporting

error_client = error_reporting.Client()

@functions_framework.http
def my_function(request):
    try:
        # Your logic
        return "Success"
    except Exception as e:
        error_client.report_exception()
        return ("Error occurred", 500)
```

### 4. Implement Retry Logic for Event-Driven
```python
@functions_framework.cloud_event
def idempotent_function(cloud_event):
    # Check if already processed (idempotency)
    event_id = cloud_event['id']
    if already_processed(event_id):
        return "Already processed"

    # Process
    process_event(cloud_event)

    # Mark as processed
    mark_processed(event_id)
```

### 5. Use Structured Logging
```python
import json
import sys

def log_message(severity, message, **kwargs):
    log_entry = {
        "severity": severity,
        "message": message,
        **kwargs
    }
    print(json.dumps(log_entry))

@functions_framework.http
def my_function(request):
    log_message("INFO", "Function started", request_id=request.headers.get('X-Request-Id'))
    # Your logic
    log_message("INFO", "Function completed")
    return "OK"
```

### 6. Manage Dependencies
**requirements.txt** (Python):
```
functions-framework==3.*
google-cloud-storage==2.*
google-cloud-firestore==2.*
```

**package.json** (Node.js):
```json
{
  "dependencies": {
    "@google-cloud/functions-framework": "^3.0.0",
    "@google-cloud/storage": "^7.0.0"
  }
}
```

### 7. Connection Pooling
```python
from google.cloud import firestore

# Initialize outside handler (reused across invocations)
db = firestore.Client()

@functions_framework.http
def query_data(request):
    # Reuses connection
    docs = db.collection('users').get()
    return f"Found {len(docs)} users"
```

### 8. Set Appropriate Timeouts
```
Short operations (< 30s):     --timeout=30s
API calls (30s-2min):          --timeout=120s
Batch processing (2-10min):    --timeout=600s
Long jobs (10-60min):          --timeout=3600s
```

### 9. Monitor and Alert
- Use Cloud Monitoring for metrics
- Set up alerts for errors and latency
- Track invocation count and duration
- Monitor memory and CPU usage

### 10. Test Locally
```bash
# Install Functions Framework
pip install functions-framework

# Run locally
functions-framework --target=my_function --debug
```

## Monitoring and Logging

### Key Metrics
- **Invocations**: Total function executions
- **Execution Time**: Duration per invocation
- **Memory Usage**: Peak memory per invocation
- **Error Rate**: Failed invocations percentage
- **Active Instances**: Current running instances

### Logs
```bash
# View logs
gcloud functions logs read my-function --region=us-central1 --limit=50

# Stream logs
gcloud functions logs read my-function --region=us-central1 --follow
```

### Custom Metrics
```python
from google.cloud import monitoring_v3

client = monitoring_v3.MetricServiceClient()
project_name = f"projects/{PROJECT_ID}"

def write_custom_metric(value):
    series = monitoring_v3.TimeSeries()
    series.metric.type = "custom.googleapis.com/my_metric"
    point = series.points.add()
    point.value.int64_value = value
    # ... configure and write
```

## Cost Optimization

### Pricing Components (2nd Gen)
1. **Invocations**: $0.40 per million
2. **Compute Time**:
   - CPU: $0.0000100 per GHz-second
   - Memory: $0.0000025 per GB-second
3. **Networking**: Standard egress rates
4. **Always-On**: For min-instances > 0

### Cost Reduction Strategies
1. Right-size memory/CPU
2. Use concurrency > 1
3. Minimize cold starts with appropriate min-instances
4. Optimize code for faster execution
5. Use VPC connector efficiently
6. Batch operations when possible

### Example Cost Calculation
**Function**: 512 MB memory, 100ms average duration, 1M invocations/month
```
Invocations:  1M × $0.40/million = $0.40
Memory:       1M × 0.1s × 0.5 GB × $0.0000025 = $0.13
CPU:          1M × 0.1s × 0.33 GHz × $0.0000100 = $0.33
Total:        ~$0.86/month
```

## Deployment Patterns

### CI/CD Deployment
```bash
# Using Cloud Build
gcloud builds submit --config=cloudbuild.yaml

# cloudbuild.yaml
steps:
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    args:
      - gcloud
      - functions
      - deploy
      - my-function
      - --gen2
      - --runtime=python312
      - --region=us-central1
      - --source=.
      - --entry-point=my_function
      - --trigger-http
```

### Traffic Splitting (2nd Gen)
```bash
# Deploy new revision
gcloud functions deploy my-function --gen2 ...

# Split traffic
gcloud run services update-traffic my-function \
    --region=us-central1 \
    --to-revisions=LATEST=50,PREVIOUS=50
```

### Blue/Green Deployment
```bash
# Deploy green
gcloud functions deploy my-function-green --gen2 ...

# Test green
curl https://REGION-PROJECT_ID.cloudfunctions.net/my-function-green

# Switch traffic (update DNS/load balancer)
# Delete blue after validation
```

## Troubleshooting

### Common Issues

1. **Cold Start Latency**: Use min-instances
2. **Timeout Errors**: Increase --timeout or optimize code
3. **Memory Issues**: Increase --memory or optimize usage
4. **Dependency Errors**: Verify requirements.txt versions
5. **Permission Errors**: Check service account IAM roles
6. **VPC Connectivity**: Verify VPC connector and firewall rules
7. **Concurrency Issues**: Reduce --concurrency or add locking

### Debug Mode
```bash
# Deploy with debug
gcloud functions deploy my-function --gen2 ... --log-http

# View detailed logs
gcloud functions logs read my-function --region=us-central1
```

## Migration from 1st to 2nd Gen

### Key Changes
1. Update trigger syntax to CloudEvents
2. Change entry point decorator
3. Update deployment command with --gen2
4. Adjust timeout limits
5. Configure concurrency if needed
6. Update VPC connector configuration

### Migration Checklist
- [ ] Update runtime to supported version
- [ ] Modify code for CloudEvents format
- [ ] Test locally with Functions Framework
- [ ] Deploy to staging environment
- [ ] Validate all triggers work
- [ ] Monitor performance and errors
- [ ] Update CI/CD pipelines
- [ ] Update documentation
- [ ] Deprecate 1st gen function after validation
