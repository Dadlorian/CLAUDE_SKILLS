# Azure Monitor and Metrics Reference

## Azure Monitor Architecture

### Data Collection
- **Metrics**: Numerical time-series data (CPU%, memory, requests/sec)
- **Logs**: Event and diagnostic data (application logs, security logs)
- **Traces**: Distributed tracing data (Application Insights)
- **Changes**: Resource configuration changes

### Data Storage
- **Metrics Database**: 93 days retention
- **Log Analytics Workspace**: 30 days (default), up to 730 days
- **Application Insights**: 90 days (default)
- **Long-term**: Export to Storage Account

## Platform Metrics

### Virtual Machine Metrics

**Host Metrics** (No agent required):
- CPU Percentage
- Network In/Out
- Disk Read/Write Bytes
- Disk Read/Write Operations/Sec

**Guest Metrics** (Requires Azure Monitor Agent):
- Available Memory Bytes
- Processor Time
- Logical Disk Free Space
- Process Count

```bash
# Install Azure Monitor Agent
az vm extension set \
  --resource-group myRG \
  --vm-name myVM \
  --name AzureMonitorLinuxAgent \
  --publisher Microsoft.Azure.Monitor \
  --enable-auto-upgrade true
```

### App Service Metrics

- **CPU Time**: Total CPU consumed
- **Memory Working Set**: Memory usage
- **Http Server Errors**: 5xx errors
- **Response Time**: Average response time
- **Requests**: Total requests
- **Data In/Out**: Network traffic

### SQL Database Metrics

- **DTU Percentage**: Database transaction unit usage (DTU model)
- **CPU Percentage**: CPU usage (vCore model)
- **Storage Percentage**: Storage used
- **Deadlocks**: Number of deadlocks
- **Blocked by Firewall**: Connection attempts blocked
- **Sessions Percentage**: Active sessions

### Storage Account Metrics

- **Transactions**: Number of requests
- **Ingress/Egress**: Data in/out
- **Success E2E Latency**: End-to-end latency
- **Availability**: Service availability %
- **Used Capacity**: Total storage used

### AKS Metrics

- **Node CPU Usage**: CPU percentage per node
- **Node Memory Usage**: Memory percentage per node
- **Pod Count**: Running pods
- **Node Count**: Active nodes
- **Disk Used Percentage**: Disk utilization

## Log Analytics

### Kusto Query Language (KQL)

**Basic Query**:
```kql
// Get all events from last hour
Event
| where TimeGenerated > ago(1h)
| project TimeGenerated, Computer, EventLog, EventLevelName, EventID
| order by TimeGenerated desc
```

**Aggregate Data**:
```kql
// Count events by computer
Event
| where TimeGenerated > ago(24h)
| summarize count() by Computer
| order by count_ desc
```

**Join Tables**:
```kql
// Correlate security events with performance
SecurityEvent
| where TimeGenerated > ago(1h)
| join kind=inner (
    Perf
    | where TimeGenerated > ago(1h)
    | where CounterName == "% Processor Time"
) on Computer
| project TimeGenerated, Computer, Activity, CounterValue
```

**Time-Series Analysis**:
```kql
// CPU over time in 5-minute buckets
Perf
| where CounterName == "% Processor Time"
| where TimeGenerated > ago(24h)
| summarize avg(CounterValue) by bin(TimeGenerated, 5m), Computer
| render timechart
```

**Percentiles**:
```kql
// Response time percentiles
requests
| where timestamp > ago(24h)
| summarize
    p50=percentile(duration, 50),
    p95=percentile(duration, 95),
    p99=percentile(duration, 99)
by bin(timestamp, 1h)
| render timechart
```

### Common Log Tables

**AzureActivity**: Azure Resource Manager operations
```kql
AzureActivity
| where OperationNameValue contains "Microsoft.Compute/virtualMachines"
| where ActivityStatusValue == "Success"
| project TimeGenerated, Caller, OperationNameValue, ResourceGroup
```

**AzureDiagnostics**: Resource diagnostic logs
```kql
AzureDiagnostics
| where Category == "SQLSecurityAuditEvents"
| where TimeGenerated > ago(1d)
```

**SecurityEvent**: Windows security events
```kql
SecurityEvent
| where EventID == 4625  // Failed logon
| summarize count() by Account, Computer
| order by count_ desc
```

**Syslog**: Linux system logs
```kql
Syslog
| where Facility == "auth" or Facility == "authpriv"
| where SeverityLevel == "err"
```

**Heartbeat**: Agent health
```kql
Heartbeat
| summarize LastHeartbeat=max(TimeGenerated) by Computer
| where LastHeartbeat < ago(5m)  // Agents not responding
```

## Application Insights

### Telemetry Types

**Requests**: HTTP requests
```kql
requests
| where timestamp > ago(24h)
| summarize
    count=count(),
    avgDuration=avg(duration),
    p95Duration=percentile(duration, 95)
by name
| order by count desc
```

**Dependencies**: External calls (DB, HTTP, etc.)
```kql
dependencies
| where timestamp > ago(1h)
| where success == false
| project timestamp, name, type, target, resultCode, duration
```

**Exceptions**: Application exceptions
```kql
exceptions
| where timestamp > ago(24h)
| summarize count() by type, outerMessage
| order by count_ desc
```

**Page Views**: Client-side page views
```kql
pageViews
| where timestamp > ago(7d)
| summarize count() by name
| order by count_ desc
```

**Custom Events**: Application-specific events
```kql
customEvents
| where name == "OrderPlaced"
| extend OrderValue = todouble(customDimensions.OrderValue)
| summarize TotalRevenue=sum(OrderValue) by bin(timestamp, 1d)
```

### Distributed Tracing

**End-to-End Transaction**:
```kql
let operationId = "abc123";
union requests, dependencies
| where operation_Id == operationId
| project timestamp, itemType, name, duration, success
| order by timestamp asc
```

**Dependency Map**:
```kql
dependencies
| where timestamp > ago(1h)
| summarize count() by cloud_RoleName, target
```

### Application Insights SDK

**C# Example**:
```csharp
using Microsoft.ApplicationInsights;
using Microsoft.ApplicationInsights.DataContracts;

var telemetryClient = new TelemetryClient();

// Track event
telemetryClient.TrackEvent("OrderPlaced",
    properties: new Dictionary<string, string> { { "OrderId", "12345" } },
    metrics: new Dictionary<string, double> { { "OrderValue", 99.99 } });

// Track exception
try
{
    ProcessOrder();
}
catch (Exception ex)
{
    telemetryClient.TrackException(ex);
    throw;
}

// Track custom metric
telemetryClient.TrackMetric("QueueLength", queue.Count);

// Track dependency
var stopwatch = Stopwatch.StartNew();
try
{
    await httpClient.GetAsync("https://api.example.com");
    telemetryClient.TrackDependency("HTTP", "https://api.example.com", "GET", startTime, stopwatch.Elapsed, success: true);
}
catch (Exception ex)
{
    telemetryClient.TrackDependency("HTTP", "https://api.example.com", "GET", startTime, stopwatch.Elapsed, success: false);
}
```

## Alerts

### Metric Alerts

```bash
# CPU alert
az monitor metrics alert create \
  --name HighCPU \
  --resource-group myRG \
  --scopes /subscriptions/.../virtualMachines/myVM \
  --condition "avg Percentage CPU > 80" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action-group /subscriptions/.../actionGroups/myActionGroup
```

**Dynamic Thresholds**:
```bash
az monitor metrics alert create \
  --name DynamicCPU \
  --resource-group myRG \
  --scopes /subscriptions/.../virtualMachines/myVM \
  --condition "avg Percentage CPU > dynamic medium 4 of 4" \
  --window-size 5m \
  --evaluation-frequency 1m
```

### Log Alerts

```bash
# Alert on failed logins
az monitor scheduled-query create \
  --name FailedLogins \
  --resource-group myRG \
  --scopes /subscriptions/.../workspaces/myWorkspace \
  --condition "count > 5" \
  --condition-query "SecurityEvent | where EventID == 4625 | summarize count()" \
  --window-size 5m \
  --evaluation-frequency 5m \
  --action-groups /subscriptions/.../actionGroups/myActionGroup
```

### Activity Log Alerts

```bash
# Alert on VM deletion
az monitor activity-log alert create \
  --name VMDeleted \
  --resource-group myRG \
  --scopes /subscriptions/... \
  --condition category=Administrative and operationName=Microsoft.Compute/virtualMachines/delete \
  --action-group /subscriptions/.../actionGroups/myActionGroup
```

### Action Groups

```bash
# Create action group
az monitor action-group create \
  --name myActionGroup \
  --resource-group myRG \
  --short-name myAG \
  --email-receiver name=admin email=admin@example.com \
  --sms-receiver name=oncall country-code=1 phone-number=5551234567 \
  --webhook-receiver name=webhook service-uri=https://example.com/webhook
```

**Action Types**:
- Email/SMS/Push/Voice
- Azure Function
- Logic App
- Webhook
- ITSM (ServiceNow, etc.)
- Automation Runbook
- Secure Webhook

## Workbooks

### Interactive Dashboards

**Template Example**:
```json
{
  "version": "Notebook/1.0",
  "items": [
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "requests\n| where timestamp > ago(24h)\n| summarize count() by bin(timestamp, 1h)\n| render timechart",
        "size": 0,
        "title": "Requests per Hour"
      }
    }
  ]
}
```

### Common Use Cases
- Performance analysis
- Failure investigation
- Usage analytics
- Security monitoring
- Cost analysis

## Diagnostic Settings

### Enable Diagnostics

```bash
az monitor diagnostic-settings create \
  --resource /subscriptions/.../virtualMachines/myVM \
  --name myDiagSettings \
  --workspace /subscriptions/.../workspaces/myWorkspace \
  --logs '[{"category": "Administrative", "enabled": true}]' \
  --metrics '[{"category": "AllMetrics", "enabled": true}]'
```

**Destinations**:
- Log Analytics Workspace (query with KQL)
- Storage Account (archive, long-term retention)
- Event Hub (stream to external systems)

### Resource-Specific Logs

**Storage Account**:
- StorageRead/StorageWrite/StorageDelete

**SQL Database**:
- SQLInsights
- AutomaticTuning
- QueryStoreRuntimeStatistics
- Errors
- Timeouts
- Blocks
- Deadlocks

**App Service**:
- AppServiceHTTPLogs
- AppServiceConsoleLogs
- AppServiceAppLogs
- AppServicePlatformLogs

## Autoscale

### VM Scale Set Autoscale

```bash
az monitor autoscale create \
  --resource-group myRG \
  --resource /subscriptions/.../virtualMachineScaleSets/myVMSS \
  --min-count 2 \
  --max-count 10 \
  --count 3

# Scale out rule
az monitor autoscale rule create \
  --resource-group myRG \
  --autoscale-name myAutoscale \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1

# Scale in rule
az monitor autoscale rule create \
  --resource-group myRG \
  --autoscale-name myAutoscale \
  --condition "Percentage CPU < 30 avg 5m" \
  --scale in 1
```

### App Service Autoscale

```bash
az monitor autoscale create \
  --resource-group myRG \
  --resource /subscriptions/.../serverFarms/myAppServicePlan \
  --min-count 1 \
  --max-count 5 \
  --count 1

# Scale based on HTTP queue length
az monitor autoscale rule create \
  --resource-group myRG \
  --autoscale-name myAutoscale \
  --condition "HttpQueueLength > 100 avg 5m" \
  --scale out 2
```

### Schedule-Based Scaling

```bash
az monitor autoscale profile create \
  --resource-group myRG \
  --autoscale-name myAutoscale \
  --name BusinessHours \
  --min-count 5 \
  --max-count 20 \
  --count 5 \
  --start "2024-01-01T09:00:00Z" \
  --end "2024-12-31T17:00:00Z" \
  --recurrence week mon tue wed thu fri
```

## Metrics Explorer

### Advanced Charting

**Split by Dimension**:
```
Metric: CPU Percentage
Aggregation: Average
Split by: Cloud role instance
Chart type: Line chart
```

**Multiple Metrics**:
```
1. CPU Percentage (left axis)
2. Available Memory Bytes (right axis)
Time range: Last 24 hours
Granularity: 5 minutes
```

### Metric Namespaces

- **microsoft.compute/virtualmachines**: VM metrics
- **microsoft.web/sites**: App Service metrics
- **microsoft.sql/servers/databases**: SQL Database metrics
- **microsoft.storage/storageaccounts**: Storage metrics
- **microsoft.containerservice/managedclusters**: AKS metrics
- **microsoft.insights/components**: Application Insights metrics

## Cost Management with Monitor

### Monitor Costs

**Data Ingestion Costs**:
- First 5 GB/day: Free (per workspace)
- Additional data: ~$2.30/GB
- Retention beyond 90 days: ~$0.10/GB/month

**Optimization**:
```kql
// Find high-volume tables
Usage
| where TimeGenerated > ago(31d)
| where IsBillable == true
| summarize IngestedGB = sum(Quantity) / 1000 by DataType
| order by IngestedGB desc
```

### Data Sampling

**Application Insights Sampling**:
```csharp
builder.Services.AddApplicationInsightsTelemetry(options =>
{
    options.EnableAdaptiveSampling = true;
    options.EnableDependencyTrackingTelemetryModule = true;
});
```

**Ingestion-Time Sampling**:
```json
{
  "samplingSettings": {
    "isEnabled": true,
    "maxTelemetryItemsPerSecond": 5
  }
}
```

## Monitoring Best Practices

1. **Collect the Right Data**: Don't over-collect, focus on actionable metrics
2. **Set Meaningful Alerts**: Avoid alert fatigue, use action groups effectively
3. **Use Workbooks**: Create dashboards for different audiences
4. **Implement Distributed Tracing**: Track requests across services
5. **Monitor Business Metrics**: Not just infrastructure
6. **Set Up Health Checks**: Liveness and readiness probes
7. **Use Log Retention Appropriately**: Balance cost and compliance
8. **Tag Resources**: Enable filtering and grouping in queries
9. **Regular Review**: Clean up unused alert rules and dashboards
10. **Security Monitoring**: Track authentication failures, privilege changes

## Common KQL Patterns

### Find Top N
```kql
requests
| summarize count() by name
| top 10 by count_
```

### Time Window Comparison
```kql
let current = requests | where timestamp > ago(1h) | count;
let previous = requests | where timestamp between (ago(2h) .. ago(1h)) | count;
print current, previous, change = (current - previous) * 100.0 / previous
```

### Anomaly Detection
```kql
requests
| make-series count=count() default=0 on timestamp step 1h
| extend anomalies = series_decompose_anomalies(count, 1.5)
| render anomalychart with (anomalycolumns=anomalies)
```

### Cohort Analysis
```kql
customEvents
| where name == "UserSignup"
| extend week = startofweek(timestamp)
| extend userId = tostring(customDimensions.userId)
| summarize signups = dcount(userId) by week
| order by week asc
```

## Integration with Other Services

### Export to Storage
- Archive old logs
- Compliance requirements
- Long-term analytics

### Stream to Event Hub
- SIEM integration (Splunk, QRadar)
- Real-time processing
- Custom analytics pipelines

### Power BI Integration
```kql
// Export query to Power BI
requests
| where timestamp > ago(30d)
| summarize
    Requests=count(),
    AvgDuration=avg(duration),
    FailureRate=countif(success == false) * 100.0 / count()
by bin(timestamp, 1d)
```

### Azure Automation Integration
```powershell
# Runbook triggered by alert
param (
    [object] $WebhookData
)

$data = ConvertFrom-Json $WebhookData.RequestBody
$resourceId = $data.data.context.resourceId

# Take action (e.g., scale up, restart)
Restart-AzVM -ResourceGroupName $rgName -Name $vmName
```
