# CloudWatch Metrics Reference

## CloudWatch Core Concepts

### Metrics
Time-ordered data points representing measurements of system or application behavior.

**Components:**
- **Namespace**: Container for metrics (e.g., AWS/EC2, CustomApp)
- **Metric Name**: Name of the metric (e.g., CPUUtilization)
- **Dimensions**: Name/value pairs for filtering (e.g., InstanceId=i-1234)
- **Timestamp**: Time of the measurement
- **Value**: Measurement value
- **Unit**: Measurement unit (Seconds, Bytes, Percent, etc.)

### Standard vs Detailed Monitoring
```
Standard (Free):
- 5-minute intervals
- Included with most AWS services
- Limited metrics

Detailed ($$$):
- 1-minute intervals
- EC2: $0.14 per instance per month (first 10 metrics)
- Additional granularity for troubleshooting
```

### Custom Metrics
```python
import boto3
from datetime import datetime

cloudwatch = boto3.client('cloudwatch')

# Put single metric
cloudwatch.put_metric_data(
    Namespace='MyApplication',
    MetricData=[{
        'MetricName': 'PageLoadTime',
        'Value': 245.5,
        'Unit': 'Milliseconds',
        'Timestamp': datetime.utcnow(),
        'Dimensions': [
            {'Name': 'Environment', 'Value': 'production'},
            {'Name': 'Region', 'Value': 'us-east-1'}
        ]
    }]
)

# Batch put (up to 1000 metrics per call)
metric_data = []
for i in range(100):
    metric_data.append({
        'MetricName': 'RequestCount',
        'Value': i,
        'Unit': 'Count',
        'Timestamp': datetime.utcnow(),
        'Dimensions': [{'Name': 'ServiceName', 'Value': 'API'}]
    })

cloudwatch.put_metric_data(
    Namespace='MyApplication',
    MetricData=metric_data
)
```

## AWS Service Metrics

### EC2 Metrics

**Basic Metrics (Standard):**
```
CPUUtilization          - Percentage (0-100)
DiskReadOps            - Count
DiskWriteOps           - Count
DiskReadBytes          - Bytes
DiskWriteBytes         - Bytes
NetworkIn              - Bytes
NetworkOut             - Bytes
NetworkPacketsIn       - Count
NetworkPacketsOut      - Count
StatusCheckFailed      - Count (0 or 1)
StatusCheckFailed_Instance - Count
StatusCheckFailed_System   - Count

Dimensions: InstanceId, InstanceType, ImageId, AutoScalingGroupName
```

**Memory and Disk Metrics (Requires CloudWatch Agent):**
```
mem_used_percent       - Percentage
mem_available          - Bytes
disk_used_percent      - Percentage
disk_free              - Bytes
swap_used_percent      - Percentage
```

**CloudWatch Agent Configuration:**
```json
{
  "metrics": {
    "namespace": "CWAgent",
    "metrics_collected": {
      "cpu": {
        "measurement": [
          {"name": "cpu_usage_idle", "rename": "CPU_IDLE", "unit": "Percent"},
          {"name": "cpu_usage_iowait", "rename": "CPU_IOWAIT", "unit": "Percent"}
        ],
        "metrics_collection_interval": 60,
        "resources": ["*"],
        "totalcpu": false
      },
      "disk": {
        "measurement": [
          {"name": "used_percent", "rename": "DISK_USED", "unit": "Percent"}
        ],
        "metrics_collection_interval": 60,
        "resources": ["*"]
      },
      "mem": {
        "measurement": [
          {"name": "mem_used_percent", "rename": "MEM_USED", "unit": "Percent"}
        ],
        "metrics_collection_interval": 60
      }
    }
  }
}
```

### RDS Metrics
```
CPUUtilization         - Percentage
DatabaseConnections    - Count
FreeableMemory        - Bytes
FreeStorageSpace      - Bytes
ReadIOPS              - Count/Second
WriteIOPS             - Count/Second
ReadLatency           - Seconds
WriteLatency          - Seconds
ReadThroughput        - Bytes/Second
WriteThroughput       - Bytes/Second
NetworkReceiveThroughput - Bytes/Second
NetworkTransmitThroughput - Bytes/Second
SwapUsage             - Bytes
ReplicaLag            - Seconds (read replicas)

Dimensions: DBInstanceIdentifier, DBClusterIdentifier
```

### Lambda Metrics
```
Invocations           - Count
Errors                - Count
Duration              - Milliseconds
Throttles             - Count
ConcurrentExecutions  - Count
UnreservedConcurrentExecutions - Count
DeadLetterErrors      - Count
IteratorAge           - Milliseconds (stream-based)

Dimensions: FunctionName, Resource (version/alias), ExecutedVersion
```

### DynamoDB Metrics
```
ConsumedReadCapacityUnits  - Count
ConsumedWriteCapacityUnits - Count
ProvisionedReadCapacityUnits - Count
ProvisionedWriteCapacityUnits - Count
UserErrors                 - Count
SystemErrors               - Count
ThrottledRequests          - Count
ConditionalCheckFailedRequests - Count
SuccessfulRequestLatency   - Milliseconds
ReturnedItemCount          - Count
ReturnedBytes              - Bytes

Dimensions: TableName, GlobalSecondaryIndexName, Operation
```

### ELB/ALB Metrics
```
RequestCount          - Count
TargetResponseTime    - Seconds
HealthyHostCount      - Count
UnHealthyHostCount    - Count
HTTPCode_Target_2XX_Count - Count
HTTPCode_Target_4XX_Count - Count
HTTPCode_Target_5XX_Count - Count
HTTPCode_ELB_4XX_Count    - Count
HTTPCode_ELB_5XX_Count    - Count
ActiveConnectionCount     - Count
NewConnectionCount        - Count
ProcessedBytes           - Bytes
RejectedConnectionCount  - Count

Dimensions: LoadBalancer, TargetGroup, AvailabilityZone
```

### S3 Metrics
```
NumberOfObjects       - Count
BucketSizeBytes       - Bytes
AllRequests           - Count
GetRequests           - Count
PutRequests           - Count
DeleteRequests        - Count
HeadRequests          - Count
PostRequests          - Count
4xxErrors             - Count
5xxErrors             - Count
FirstByteLatency      - Milliseconds
TotalRequestLatency   - Milliseconds
BytesDownloaded       - Bytes
BytesUploaded         - Bytes

Dimensions: BucketName, StorageType, FilterId
```

### API Gateway Metrics
```
Count                 - Count (total API requests)
IntegrationLatency    - Milliseconds
Latency              - Milliseconds (overall latency)
4XXError             - Count
5XXError             - Count
CacheHitCount        - Count
CacheMissCount       - Count

Dimensions: ApiName, ApiId, Method, Resource, Stage
```

### SQS Metrics
```
NumberOfMessagesSent      - Count
NumberOfMessagesReceived  - Count
NumberOfMessagesDeleted   - Count
ApproximateNumberOfMessagesVisible - Count
ApproximateNumberOfMessagesNotVisible - Count
ApproximateNumberOfMessagesDelayed - Count
ApproximateAgeOfOldestMessage - Seconds
SentMessageSize              - Bytes

Dimensions: QueueName
```

### SNS Metrics
```
NumberOfMessagesPublished - Count
NumberOfNotificationsDelivered - Count
NumberOfNotificationsFailed - Count
PublishSize                     - Bytes
SMSSuccessRate                  - Percentage

Dimensions: TopicName, Application, Platform
```

## CloudWatch Alarms

### Alarm States
- **OK**: Metric is within threshold
- **ALARM**: Metric breached threshold
- **INSUFFICIENT_DATA**: Not enough data to determine state

### Creating Alarms
```python
# Simple threshold alarm
cloudwatch.put_metric_alarm(
    AlarmName='HighCPU',
    ComparisonOperator='GreaterThanThreshold',
    EvaluationPeriods=2,
    MetricName='CPUUtilization',
    Namespace='AWS/EC2',
    Period=300,
    Statistic='Average',
    Threshold=80.0,
    ActionsEnabled=True,
    AlarmActions=['arn:aws:sns:us-east-1:123456789012:alerts'],
    AlarmDescription='Alert when CPU exceeds 80%',
    Dimensions=[
        {'Name': 'InstanceId', 'Value': 'i-1234567890abcdef0'}
    ],
    Unit='Percent'
)

# Anomaly detection alarm
cloudwatch.put_metric_alarm(
    AlarmName='AnomalousTraffic',
    ComparisonOperator='LessThanLowerOrGreaterThanUpperThreshold',
    EvaluationPeriods=2,
    Metrics=[
        {
            'Id': 'm1',
            'ReturnData': True,
            'MetricStat': {
                'Metric': {
                    'Namespace': 'AWS/ApplicationELB',
                    'MetricName': 'RequestCount',
                    'Dimensions': [
                        {'Name': 'LoadBalancer', 'Value': 'app/my-alb/abc123'}
                    ]
                },
                'Period': 300,
                'Stat': 'Sum'
            }
        },
        {
            'Id': 'ad1',
            'Expression': 'ANOMALY_DETECTION_BAND(m1, 2)'
        }
    ],
    ThresholdMetricId='ad1',
    ActionsEnabled=True,
    AlarmActions=['arn:aws:sns:us-east-1:123456789012:alerts']
)
```

### Composite Alarms
```python
cloudwatch.put_composite_alarm(
    AlarmName='CriticalSystemFailure',
    AlarmRule='(ALARM(HighCPU) OR ALARM(HighMemory)) AND ALARM(HighErrorRate)',
    ActionsEnabled=True,
    AlarmActions=['arn:aws:sns:us-east-1:123456789012:critical-alerts'],
    AlarmDescription='Composite alarm for critical system issues'
)
```

## CloudWatch Dashboards

### Creating Dashboard
```python
dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/EC2", "CPUUtilization", {"stat": "Average"}]
                ],
                "period": 300,
                "stat": "Average",
                "region": "us-east-1",
                "title": "EC2 CPU Utilization",
                "yAxis": {"left": {"min": 0, "max": 100}}
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/ApplicationELB", "TargetResponseTime", {"stat": "Average"}],
                    [".", "RequestCount", {"stat": "Sum", "yAxis": "right"}]
                ],
                "period": 60,
                "region": "us-east-1",
                "title": "ALB Performance",
                "yAxis": {
                    "left": {"label": "Response Time (s)"},
                    "right": {"label": "Requests"}
                }
            }
        },
        {
            "type": "log",
            "properties": {
                "query": """SOURCE '/aws/lambda/my-function'
                | fields @timestamp, @message
                | filter @message like /ERROR/
                | stats count() by bin(5m)""",
                "region": "us-east-1",
                "title": "Lambda Errors"
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName='ApplicationMonitoring',
    DashboardBody=json.dumps(dashboard_body)
)
```

## CloudWatch Logs

### Log Groups and Streams
```python
logs = boto3.client('logs')

# Create log group
logs.create_log_group(logGroupName='/aws/myapp/production')

# Set retention
logs.put_retention_policy(
    logGroupName='/aws/myapp/production',
    retentionInDays=30
)

# Create log stream
logs.create_log_stream(
    logGroupName='/aws/myapp/production',
    logStreamName='instance-i-12345'
)

# Put log events
logs.put_log_events(
    logGroupName='/aws/myapp/production',
    logStreamName='instance-i-12345',
    logEvents=[
        {
            'timestamp': int(time.time() * 1000),
            'message': 'Application started successfully'
        }
    ]
)
```

### CloudWatch Logs Insights Queries

**Error Analysis:**
```sql
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() as error_count by bin(5m)
| sort error_count desc
```

**Latency Percentiles:**
```sql
fields @timestamp, request_duration
| filter ispresent(request_duration)
| stats avg(request_duration), pct(request_duration, 50), pct(request_duration, 95), pct(request_duration, 99)
```

**Top Errors:**
```sql
fields @timestamp, error_type
| filter level = "ERROR"
| stats count() as error_count by error_type
| sort error_count desc
| limit 10
```

**User Activity:**
```sql
fields @timestamp, user_id, action
| filter action in ["login", "logout", "purchase"]
| stats count() by user_id, action
```

**Lambda Cold Starts:**
```sql
filter @type = "REPORT"
| fields @memorySize / 1000000 as memorySize, @duration, @billedDuration, @maxMemoryUsed / 1000000 as maxMemoryUsed
| filter @message like /(?i)Init Duration/
| parse @message /Init Duration: (?<initDuration>.*) ms/
| stats count() as coldStarts, avg(initDuration) as avgInitDuration by memorySize
```

### Metric Filters
```python
# Create metric filter from logs
logs.put_metric_filter(
    logGroupName='/aws/lambda/my-function',
    filterName='ErrorCount',
    filterPattern='[timestamp, request_id, level = ERROR*, ...]',
    metricTransformations=[{
        'metricName': 'ErrorCount',
        'metricNamespace': 'MyApp',
        'metricValue': '1',
        'defaultValue': 0,
        'unit': 'Count'
    }]
)
```

### Subscription Filters
```python
# Stream logs to Lambda
logs.put_subscription_filter(
    logGroupName='/aws/myapp/production',
    filterName='ProcessErrors',
    filterPattern='[timestamp, request_id, level = ERROR*, ...]',
    destinationArn='arn:aws:lambda:us-east-1:123456789012:function:ProcessLogs'
)

# Stream to Kinesis
logs.put_subscription_filter(
    logGroupName='/aws/myapp/production',
    filterName='StreamToKinesis',
    filterPattern='',  # All logs
    destinationArn='arn:aws:kinesis:us-east-1:123456789012:stream/log-stream',
    roleArn='arn:aws:iam::123456789012:role/CloudWatchLogsRole'
)
```

## CloudWatch Contributor Insights

### Rules for Top Contributors
```python
# Create rule to find top error sources
cloudwatch.put_insight_rule(
    RuleName='TopErrorSources',
    RuleState='ENABLED',
    RuleDefinition=json.dumps({
        "Schema": {
            "Name": "CloudWatchLogRule",
            "Version": 1
        },
        "LogGroupNames": ["/aws/lambda/my-function"],
        "LogFormat": "JSON",
        "Fields": {
            "4": "$.errorType",
            "2": "$.sourceIP"
        },
        "Contribution": {
            "Keys": ["$.sourceIP"],
            "Filters": [
                {
                    "Match": "$.level",
                    "EqualTo": "ERROR"
                }
            ]
        },
        "AggregateOn": "Count"
    })
)
```

## CloudWatch Synthetics (Canaries)

### Creating Canary
```python
import boto3

synthetics = boto3.client('synthetics')

# Create heartbeat canary
synthetics.create_canary(
    Name='api-heartbeat',
    Code={
        'Handler': 'apiCanaryBlueprint.handler',
        'S3Bucket': 'my-canary-scripts',
        'S3Key': 'canary.zip'
    },
    ArtifactS3Location='s3://my-canary-results',
    ExecutionRoleArn='arn:aws:iam::123456789012:role/CanaryRole',
    Schedule={
        'Expression': 'rate(5 minutes)',
        'DurationInSeconds': 0
    },
    RunConfig={
        'TimeoutInSeconds': 60,
        'MemoryInMB': 960
    },
    SuccessRetentionPeriodInDays=31,
    FailureRetentionPeriodInDays=31
)
```

## Best Practices

### 1. Use Namespaces for Organization
```python
# Organize metrics by application/environment
cloudwatch.put_metric_data(
    Namespace='Production/WebApp',
    MetricData=[...]
)
```

### 2. Leverage Dimensions for Filtering
```python
# Add relevant dimensions
dimensions = [
    {'Name': 'Environment', 'Value': 'production'},
    {'Name': 'Service', 'Value': 'api'},
    {'Name': 'Version', 'Value': 'v2.1.0'}
]
```

### 3. Use High-Resolution Metrics for Real-Time
```python
# 1-second resolution custom metrics
cloudwatch.put_metric_data(
    Namespace='MyApp',
    MetricData=[{
        'MetricName': 'RequestLatency',
        'Value': 42.5,
        'Unit': 'Milliseconds',
        'StorageResolution': 1  # 1-second resolution
    }]
)
```

### 4. Set Appropriate Alarm Evaluation Periods
```python
# 2 out of 3 datapoints must breach threshold
cloudwatch.put_metric_alarm(
    AlarmName='TransientSpike',
    EvaluationPeriods=3,
    DatapointsToAlarm=2,
    Threshold=80.0,
    ComparisonOperator='GreaterThanThreshold',
    # ... other parameters
)
```

### 5. Use Anomaly Detection for Dynamic Baselines
```python
# Automatically adjust thresholds based on patterns
cloudwatch.put_anomaly_detector(
    Namespace='AWS/ApplicationELB',
    MetricName='RequestCount',
    Dimensions=[
        {'Name': 'LoadBalancer', 'Value': 'app/my-alb/abc123'}
    ],
    Stat='Sum'
)
```

## Pricing

**Metrics:**
- Standard monitoring: Free
- Detailed monitoring: $0.14 per instance per month (EC2)
- Custom metrics: $0.30 per metric per month
- High-resolution: $0.30 per metric per month

**Alarms:**
- Standard: $0.10 per alarm per month
- High-resolution: $0.30 per alarm per month

**Dashboards:**
- $3.00 per dashboard per month

**Logs:**
- Ingestion: $0.50 per GB
- Storage: $0.03 per GB per month
- Logs Insights queries: $0.005 per GB scanned

**API Requests:**
- GetMetricData: $0.01 per 1,000 metrics requested
- PutMetricData: Free

This comprehensive reference covers CloudWatch for effective monitoring and observability in AWS environments.
