# Cloud Monitoring and Observability Reference

## Google Cloud Observability Overview

Comprehensive monitoring, logging, tracing, and profiling for GCP and hybrid environments.

## Cloud Monitoring (formerly Stackdriver Monitoring)

### Metrics Types

**System Metrics**: Automatic for GCP services
- Compute Engine: CPU, disk, network
- Cloud Storage: request count, bandwidth
- BigQuery: slots, query count
- GKE: pod/container metrics

**Custom Metrics**: Application-specific metrics
**Log-Based Metrics**: Derived from log entries

### Metric Descriptors

**Metric Components**:
- **Type**: Unique identifier (e.g., `compute.googleapis.com/instance/cpu/utilization`)
- **Kind**: GAUGE, DELTA, CUMULATIVE
- **Value Type**: INT64, DOUBLE, BOOL, STRING, DISTRIBUTION
- **Labels**: Key-value pairs for filtering

### Creating Custom Metrics

**Python Example**:
```python
from google.cloud import monitoring_v3
import time

client = monitoring_v3.MetricServiceClient()
project_name = f"projects/{project_id}"

# Create time series
series = monitoring_v3.TimeSeries()
series.metric.type = "custom.googleapis.com/my_metric"
series.resource.type = "gce_instance"
series.resource.labels["instance_id"] = "1234567890123456789"
series.resource.labels["zone"] = "us-central1-a"

# Add data point
now = time.time()
seconds = int(now)
nanos = int((now - seconds) * 10 ** 9)
interval = monitoring_v3.TimeInterval(
    {"end_time": {"seconds": seconds, "nanos": nanos}}
)
point = monitoring_v3.Point(
    {"interval": interval, "value": {"double_value": 42.5}}
)
series.points = [point]

# Write time series
client.create_time_series(name=project_name, time_series=[series])
```

**Go Example**:
```go
import (
    monitoring "cloud.google.com/go/monitoring/apiv3/v2"
    "google.golang.org/genproto/googleapis/monitoring/v3"
)

func writeCustomMetric(projectID string) error {
    ctx := context.Background()
    client, _ := monitoring.NewMetricClient(ctx)
    defer client.Close()

    dataPoint := &monitoringpb.Point{
        Interval: &monitoringpb.TimeInterval{
            EndTime: timestamppb.Now(),
        },
        Value: &monitoringpb.TypedValue{
            Value: &monitoringpb.TypedValue_DoubleValue{
                DoubleValue: 42.5,
            },
        },
    }

    req := &monitoringpb.CreateTimeSeriesRequest{
        Name: "projects/" + projectID,
        TimeSeries: []*monitoringpb.TimeSeries{{
            Metric: &metricpb.Metric{
                Type: "custom.googleapis.com/my_metric",
            },
            Resource: &monitoredres.MonitoredResource{
                Type: "gce_instance",
                Labels: map[string]string{
                    "instance_id": "1234567890123456789",
                    "zone": "us-central1-a",
                },
            },
            Points: []*monitoringpb.Point{dataPoint},
        }},
    }

    return client.CreateTimeSeries(ctx, req)
}
```

### Dashboards

**Create Dashboard via API**:
```bash
curl -X POST \
  https://monitoring.googleapis.com/v1/projects/PROJECT_ID/dashboards \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d @dashboard.json
```

**dashboard.json**:
```json
{
  "displayName": "My Dashboard",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "CPU Utilization",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"gce_instance\" metric.type=\"compute.googleapis.com/instance/cpu/utilization\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_MEAN"
                  }
                }
              }
            }],
            "yAxis": {
              "scale": "LINEAR"
            }
          }
        }
      }
    ]
  }
}
```

### Alerting Policies

**CPU Alert**:
```bash
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="High CPU Alert" \
    --condition-display-name="CPU > 80%" \
    --condition-threshold-value=0.8 \
    --condition-threshold-duration=300s \
    --condition-filter='resource.type="gce_instance" AND metric.type="compute.googleapis.com/instance/cpu/utilization"' \
    --condition-aggregation='{"alignmentPeriod": "60s", "perSeriesAligner": "ALIGN_MEAN"}' \
    --condition-comparison=COMPARISON_GT
```

**Log-Based Alert**:
```bash
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="Error Rate Alert" \
    --condition-display-name="Error count > 10" \
    --condition-threshold-value=10 \
    --condition-threshold-duration=60s \
    --condition-filter='metric.type="logging.googleapis.com/user/error_count"' \
    --condition-comparison=COMPARISON_GT
```

**Alert Policy with MQL**:
```
fetch gce_instance
| metric 'compute.googleapis.com/instance/cpu/utilization'
| group_by 1m, [value_utilization_mean: mean(value.utilization)]
| every 1m
| condition value_utilization_mean > 0.8
```

### Notification Channels

**Email**:
```bash
gcloud alpha monitoring channels create \
    --display-name="Admin Email" \
    --type=email \
    --channel-labels=email_address=admin@example.com
```

**Slack**:
```bash
gcloud alpha monitoring channels create \
    --display-name="Slack Alerts" \
    --type=slack \
    --channel-labels=url=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```

**PagerDuty**:
```bash
gcloud alpha monitoring channels create \
    --display-name="PagerDuty" \
    --type=pagerduty \
    --channel-labels=service_key=YOUR_PAGERDUTY_KEY
```

### Uptime Checks

**HTTP Uptime Check**:
```bash
gcloud monitoring uptime create my-uptime-check \
    --resource-type=uptime-url \
    --resource-labels=host=example.com,project_id=PROJECT_ID \
    --http-check-path=/health \
    --period=60 \
    --timeout=10
```

**TCP Uptime Check**:
```bash
gcloud monitoring uptime create tcp-check \
    --resource-type=uptime-url \
    --resource-labels=host=example.com \
    --tcp-check-port=443 \
    --period=300
```

**With Alert**:
```bash
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="Website Down" \
    --condition-display-name="Uptime check failed" \
    --condition-threshold-value=1 \
    --condition-threshold-duration=300s \
    --condition-filter='metric.type="monitoring.googleapis.com/uptime_check/check_passed" AND resource.type="uptime_url"' \
    --condition-comparison=COMPARISON_LT
```

## Cloud Logging

### Log Types

**Platform Logs** (automatic):
- Admin Activity Audit Logs
- System Event Audit Logs
- Data Access Audit Logs (when enabled)
- Policy Denied Audit Logs

**Component Logs**:
- GKE cluster/node/pod logs
- Cloud Run logs
- Cloud Functions logs

**User Logs**: Application logs

### Writing Logs

**Structured Logging (JSON)**:
```python
import json
import sys

def log_structured(message, severity='INFO', **kwargs):
    log_entry = {
        'message': message,
        'severity': severity,
        **kwargs
    }
    print(json.dumps(log_entry), file=sys.stdout)

log_structured('User login', severity='INFO', user_id=12345, ip='203.0.113.1')
```

**Cloud Logging API**:
```python
from google.cloud import logging

logging_client = logging.Client()
logger = logging_client.logger('my-application')

logger.log_struct(
    {
        'message': 'User action',
        'user_id': 12345,
        'action': 'purchase',
        'amount': 99.99
    },
    severity='INFO'
)
```

**Log Levels**:
- DEFAULT
- DEBUG
- INFO
- NOTICE
- WARNING
- ERROR
- CRITICAL
- ALERT
- EMERGENCY

### Querying Logs

**gcloud**:
```bash
# Recent errors
gcloud logging read "severity>=ERROR" --limit=50 --format=json

# Specific resource
gcloud logging read "resource.type=gce_instance AND resource.labels.instance_id=1234567890" --limit=20

# Time range
gcloud logging read "timestamp>=\"2024-01-01T00:00:00Z\"" --limit=100

# Complex query
gcloud logging read 'resource.type="k8s_container" AND labels."k8s-pod/app"="frontend" AND severity="ERROR"' --limit=10
```

**Advanced Filters**:
```
# AND conditions
resource.type="gce_instance" AND severity>=ERROR

# OR conditions
severity="ERROR" OR severity="CRITICAL"

# Text search
textPayload=~"exception"

# JSON field
jsonPayload.user_id="12345"

# Regex
jsonPayload.email=~".*@example\.com"

# NOT operator
NOT severity="DEBUG"

# Time range
timestamp>="2024-01-01T00:00:00Z" AND timestamp<"2024-01-02T00:00:00Z"
```

### Log Sinks

**Export to Cloud Storage**:
```bash
gcloud logging sinks create my-sink \
    storage.googleapis.com/my-logs-bucket \
    --log-filter='resource.type="gce_instance" AND severity>=ERROR'
```

**Export to BigQuery**:
```bash
gcloud logging sinks create bigquery-sink \
    bigquery.googleapis.com/projects/PROJECT_ID/datasets/logs_dataset \
    --log-filter='resource.type="k8s_container"'
```

**Export to Pub/Sub**:
```bash
gcloud logging sinks create pubsub-sink \
    pubsub.googleapis.com/projects/PROJECT_ID/topics/log-topic \
    --log-filter='severity="ERROR"'
```

**Aggregated Export** (organization/folder level):
```bash
gcloud logging sinks create org-sink \
    storage.googleapis.com/org-logs-bucket \
    --organization=ORG_ID \
    --include-children \
    --log-filter='severity>=WARNING'
```

### Log-Based Metrics

**Counter Metric**:
```bash
gcloud logging metrics create error_count \
    --description="Count of error logs" \
    --log-filter='severity="ERROR"'
```

**Distribution Metric**:
```bash
gcloud logging metrics create response_time_distribution \
    --description="HTTP response time distribution" \
    --log-filter='resource.type="cloud_run_revision"' \
    --value-extractor='EXTRACT(jsonPayload.latency)' \
    --metric-kind=DELTA \
    --value-type=DISTRIBUTION \
    --bucket-options='exponentialBuckets: {numFiniteBuckets: 64, growthFactor: 2, scale: 0.01}'
```

### Log Exclusions

Reduce ingestion volume and costs.

```bash
# Exclude health check logs
gcloud logging exclusions create health-check-exclusion \
    --log-filter='resource.type="http_load_balancer" AND httpRequest.requestUrl=~"/health"' \
    --description="Exclude health check logs"

# Exclude debug logs
gcloud logging exclusions create debug-exclusion \
    --log-filter='severity="DEBUG"' \
    --description="Exclude debug logs from ingestion"
```

### Log Sampling

```bash
# Sample 10% of logs
gcloud logging exclusions create sample-exclusion \
    --log-filter='sample(insertId, 0.1)' \
    --description="Keep only 10% of logs"
```

## Cloud Trace

### Automatic Tracing
Automatically enabled for:
- App Engine
- Cloud Run
- Cloud Functions (2nd gen)

### Manual Instrumentation

**Python (OpenTelemetry)**:
```python
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_exporter = CloudTraceSpanExporter()
span_processor = BatchSpanProcessor(span_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Trace function
@tracer.start_as_current_span("process_request")
def process_request(request_id):
    span = trace.get_current_span()
    span.set_attribute("request.id", request_id)

    with tracer.start_as_current_span("database_query"):
        # Database operation
        result = query_database()

    with tracer.start_as_current_span("external_api_call"):
        # API call
        api_response = call_api()

    return result
```

**Go (OpenTelemetry)**:
```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/trace/cloudtrace"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
)

func initTracer() {
    exporter, _ := cloudtrace.New(cloudtrace.WithProjectID(projectID))
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithSampler(sdktrace.AlwaysSample()),
        sdktrace.WithBatcher(exporter),
    )
    otel.SetTracerProvider(tp)
}

func processRequest(ctx context.Context, requestID string) {
    tracer := otel.Tracer("my-app")
    ctx, span := tracer.Start(ctx, "process_request")
    defer span.End()

    span.SetAttributes(attribute.String("request.id", requestID))

    // Nested span
    ctx, dbSpan := tracer.Start(ctx, "database_query")
    queryDatabase(ctx)
    dbSpan.End()
}
```

### Viewing Traces

```bash
# List traces
gcloud trace list

# Get specific trace
gcloud trace describe TRACE_ID
```

**Query Traces** (in Cloud Console or API):
```
# Find slow traces
latency > 1000ms

# Specific URL
url:/api/users

# Error traces
hasError=true
```

## Cloud Profiler

### Enable Profiler

**Python**:
```python
import googlecloudprofiler

googlecloudprofiler.start(
    service='my-service',
    service_version='1.0.0',
    verbose=3,
)
```

**Go**:
```go
import "cloud.google.com/go/profiler"

func main() {
    if err := profiler.Start(profiler.Config{
        Service:        "my-service",
        ServiceVersion: "1.0.0",
        ProjectID:      projectID,
    }); err != nil {
        log.Fatalf("Failed to start profiler: %v", err)
    }
}
```

**Java**:
```java
import com.google.cloud.profiler.v1.ProfilerServiceClient;

public class Main {
    public static void main(String[] args) {
        Profiler.start(
            Profiler.newBuilder()
                .setServiceName("my-service")
                .setServiceVersion("1.0.0")
                .build()
        );
    }
}
```

### Profile Types

- **CPU**: CPU time consumption
- **Heap**: Memory allocation
- **Wall Time**: Total elapsed time (includes I/O wait)
- **Contention**: Thread lock contention (Java)

## Error Reporting

### Automatic Error Reporting
Enabled for:
- App Engine
- Cloud Functions
- Cloud Run
- GKE (with agent)

### Manual Error Reporting

**Python**:
```python
from google.cloud import error_reporting

client = error_reporting.Client()

try:
    # Your code
    risky_operation()
except Exception as e:
    client.report_exception()
```

**With Context**:
```python
client.report(
    message=str(exception),
    http_context={
        'method': 'GET',
        'url': 'https://example.com/api',
        'userAgent': 'Mozilla/5.0...',
        'remoteIp': '203.0.113.1',
        'statusCode': 500,
    },
    user='user@example.com'
)
```

**Go**:
```go
import "cloud.google.com/go/errorreporting"

func reportError(ctx context.Context, err error) {
    errorClient, _ := errorreporting.NewClient(ctx, projectID, errorreporting.Config{
        ServiceName: "my-service",
        ServiceVersion: "1.0.0",
    })
    defer errorClient.Close()

    errorClient.Report(errorreporting.Entry{
        Error: err,
        User:  "user@example.com",
    })
}
```

## Service Monitoring (SLIs/SLOs)

### Define SLI

**Availability SLI**:
```yaml
serviceLevelIndicator:
  requestBased:
    goodTotalRatio:
      goodServiceFilter: |
        metric.type="serviceruntime.googleapis.com/api/request_count"
        resource.type="api"
        metric.label.response_code_class="2xx"
      totalServiceFilter: |
        metric.type="serviceruntime.googleapis.com/api/request_count"
        resource.type="api"
```

**Latency SLI**:
```yaml
serviceLevelIndicator:
  requestBased:
    distributionCut:
      distributionFilter: |
        metric.type="serviceruntime.googleapis.com/api/request_latencies"
        resource.type="api"
      range:
        max: 500  # 500ms threshold
```

### Create SLO

```bash
gcloud monitoring services create my-service \
    --display-name="My Service"

gcloud monitoring slos create my-slo \
    --service=my-service \
    --goal=0.99 \
    --calendar-period=month \
    --request-based-good-total-ratio-filter-good='metric.type="serviceruntime.googleapis.com/api/request_count" AND metric.label.response_code_class="2xx"' \
    --request-based-good-total-ratio-filter-total='metric.type="serviceruntime.googleapis.com/api/request_count"'
```

### Alert on SLO Burn Rate

```bash
gcloud alpha monitoring policies create \
    --display-name="SLO Burn Rate Alert" \
    --condition-display-name="Fast burn detected" \
    --condition-threshold-value=10 \
    --condition-filter='select_slo_burn_rate("projects/PROJECT_ID/services/my-service/serviceLevelObjectives/my-slo", 3600)' \
    --condition-comparison=COMPARISON_GT
```

## Best Practices

1. **Use Structured Logging**: JSON format for better querying
2. **Implement SLIs/SLOs**: Measure user-facing reliability
3. **Set Up Alerts**: Proactive monitoring, not reactive
4. **Use Log Sinks**: Export for long-term retention and analysis
5. **Enable Tracing**: Understand request flows and bottlenecks
6. **Profile Production**: Find performance issues in real workloads
7. **Error Reporting**: Centralize exception tracking
8. **Log Sampling**: Reduce costs for high-volume logs
9. **Custom Metrics**: Track business-specific KPIs
10. **Dashboard Everything**: Visibility into system health
11. **Use MQL**: Powerful metric queries
12. **Monitor Resource Usage**: Prevent quota exhaustion
13. **Alert Fatigue**: Tune thresholds to avoid noise
14. **Log Exclusions**: Filter out unnecessary logs
15. **Uptime Checks**: Monitor external-facing services

## Cost Optimization

**Monitoring**:
- First 150 MB/month of metrics: Free
- Additional: $0.2580 per MB

**Logging**:
- First 50 GB/month: Free
- Additional: $0.50 per GB
- Use exclusions and sampling

**Tracing**:
- First 2.5 million spans/month: Free
- Additional: $0.20 per million spans

**Strategies**:
1. Use log exclusions for debug/health checks
2. Sample high-volume logs
3. Set log retention policies
4. Use metric aggregation
5. Disable unused metrics
6. Export to BigQuery for analysis (cheaper storage)
