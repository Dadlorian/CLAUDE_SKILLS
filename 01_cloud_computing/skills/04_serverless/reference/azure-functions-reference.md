# Azure Functions Reference Guide

## Overview

Azure Functions is Microsoft's event-driven serverless compute platform that enables you to run code on-demand without managing infrastructure. Deeply integrated with Azure services and enterprise ecosystems.

## Core Concepts

### Function App
A **Function App** is a container for one or more functions that share:
- **Runtime stack**: Node.js, Python, .NET, Java, PowerShell, Custom
- **Hosting plan**: Consumption, Premium, Dedicated (App Service)
- **Configuration**: App settings, connection strings, deployment settings
- **Storage account**: Required for function management and triggers

### Hosting Plans

#### Consumption Plan (Serverless)
```yaml
Pricing: Pay-per-execution
Scaling: Automatic (0 to 200 instances)
Timeout: 5 minutes (default), 10 minutes (max)
Memory: 1.5 GB per instance
Cold Start: Yes
Best For: Event-driven, variable workloads
```

**Pricing**:
- $0.20 per million executions
- $0.000016 per GB-second
- Free grant: 1M executions and 400,000 GB-seconds/month

#### Premium Plan (Elastic Premium)
```yaml
Pricing: Per-second based on vCPUs and memory
Scaling: Pre-warmed instances (min 1, max 100)
Timeout: 30 minutes (default), unlimited (configurable)
Memory: Up to 14 GB per instance
Cold Start: Eliminated (always warm)
Features: VNet integration, unlimited execution time
Best For: Production workloads, no cold starts
```

**Pricing Example**: EP1 (1 vCPU, 3.5 GB RAM) = ~$150/month for 1 instance

#### Dedicated Plan (App Service)
```yaml
Pricing: Standard App Service pricing
Scaling: Manual or auto-scale (rules-based)
Timeout: Unlimited
Memory: Based on App Service Plan
Cold Start: No
Best For: Long-running, predictable workloads
```

## Supported Runtimes

| Language | Versions | In-Process | Isolated Worker | Best For |
|----------|----------|------------|-----------------|----------|
| **.NET** | 6 (LTS), 8 | ✅ (.NET 6 only) | ✅ | Enterprise applications |
| **Node.js** | 18 (LTS), 20 | ❌ | ✅ | APIs, webhooks |
| **Python** | 3.9, 3.10, 3.11 | ❌ | ✅ | Data processing, ML |
| **Java** | 8, 11, 17, 21 | ❌ | ✅ | Enterprise Java apps |
| **PowerShell** | 7.2, 7.4 | ❌ | ✅ | Automation, admin tasks |
| **Custom** | Any | ❌ | ✅ | Custom runtimes |

### In-Process vs Isolated Worker

**In-Process (.NET Only)**:
- Function code runs in same process as Functions host
- Direct access to bindings
- Lower memory overhead
- .NET 6 only (legacy model)

**Isolated Worker (Recommended)**:
- Function code runs in separate worker process
- Language flexibility
- Independent versioning
- Better isolation
- Required for .NET 8+

## Triggers

Triggers define how a function is invoked. Each function has exactly one trigger.

### HTTP Trigger
```csharp
[Function("HttpExample")]
public IActionResult Run(
    [HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest req)
{
    return new OkObjectResult("Hello, World!");
}
```

**Authorization Levels**:
- **Anonymous**: No API key required
- **Function**: Function-specific key required
- **Admin**: Master key required

### Timer Trigger (CRON)
```csharp
[Function("TimerFunction")]
public void Run(
    [TimerTrigger("0 */5 * * * *")] TimerInfo myTimer)
{
    // Runs every 5 minutes
}
```

**CRON Format**: `{second} {minute} {hour} {day} {month} {day-of-week}`

### Blob Storage Trigger
```csharp
[Function("BlobTrigger")]
public void Run(
    [BlobTrigger("samples-workitems/{name}")] Stream myBlob,
    string name)
{
    // Triggered when blob created/updated in container
}
```

### Queue Storage Trigger
```csharp
[Function("QueueTrigger")]
public void Run(
    [QueueTrigger("myqueue-items")] string myQueueItem)
{
    // Process queue message
}
```

**Poison Queue**: Automatic handling after 5 failed attempts

### Event Grid Trigger
```csharp
[Function("EventGridTrigger")]
public void Run(
    [EventGridTrigger] EventGridEvent eventGridEvent)
{
    // Process Event Grid event
}
```

**Use Cases**: React to Azure service events (resource changes, blob uploads, etc.)

### Event Hub Trigger
```csharp
[Function("EventHubTrigger")]
public void Run(
    [EventHubTrigger("myeventhub", Connection = "EventHubConnectionString")]
    string[] events)
{
    // Process batch of events
}
```

**Batch Processing**: Configure batch size (1-1000)

### Service Bus Trigger
```csharp
[Function("ServiceBusTrigger")]
public void Run(
    [ServiceBusTrigger("myqueue", Connection = "ServiceBusConnection")]
    string myQueueItem)
{
    // Process Service Bus message
}
```

**Features**:
- Message lock and auto-complete
- Dead letter queue support
- Session support

### Cosmos DB Trigger (Change Feed)
```csharp
[Function("CosmosDBTrigger")]
public void Run(
    [CosmosDBTrigger(
        databaseName: "mydb",
        containerName: "mycontainer",
        Connection = "CosmosDBConnection",
        LeaseContainerName = "leases")]
    IReadOnlyList<MyDocument> documents)
{
    // Process document changes
}
```

**Use Cases**: React to database changes, CDC, event sourcing

## Bindings

Bindings declaratively connect resources to functions without writing integration code.

### Input Bindings
Read data from external sources.

**Blob Input**:
```csharp
[Function("BlobInput")]
public IActionResult Run(
    [HttpTrigger(AuthorizationLevel.Anonymous, "get")] HttpRequest req,
    [BlobInput("samples/{Query.name}", Connection = "AzureWebJobsStorage")] string blobContent)
{
    return new OkObjectResult(blobContent);
}
```

**Cosmos DB Input**:
```csharp
[CosmosDBInput(
    databaseName: "mydb",
    containerName: "mycontainer",
    Id = "{Query.id}",
    PartitionKey = "{Query.pk}",
    Connection = "CosmosDBConnection")] MyDocument doc
```

### Output Bindings
Write data to external services.

**Queue Output**:
```csharp
[Function("QueueOutput")]
[QueueOutput("myqueue-items", Connection = "AzureWebJobsStorage")]
public string Run([HttpTrigger(AuthorizationLevel.Function, "post")] HttpRequest req)
{
    return "Message to queue";
}
```

**Multiple Outputs**:
```csharp
public class MultiOutput
{
    [QueueOutput("queue1")]
    public string Queue1 { get; set; }

    [QueueOutput("queue2")]
    public string Queue2 { get; set; }

    [HttpResult]
    public IActionResult HttpResponse { get; set; }
}

[Function("MultipleOutputs")]
public MultiOutput Run([HttpTrigger] HttpRequest req)
{
    return new MultiOutput
    {
        Queue1 = "Message 1",
        Queue2 = "Message 2",
        HttpResponse = new OkResult()
    };
}
```

## Durable Functions

**Durable Functions** extend Azure Functions with stateful workflows and orchestrations.

### Function Types

#### Orchestrator Function
```csharp
[FunctionName("OrchestratorFunction")]
public async Task<string> RunOrchestrator(
    [OrchestrationTrigger] IDurableOrchestrationContext context)
{
    var result1 = await context.CallActivityAsync<string>("Activity1", null);
    var result2 = await context.CallActivityAsync<string>("Activity2", result1);
    return result2;
}
```

**Constraints**:
- Must be deterministic (no random, DateTime.Now, etc.)
- No direct I/O (use activity functions)
- Use `context.CurrentUtcDateTime` instead of `DateTime.UtcNow`

#### Activity Function
```csharp
[FunctionName("Activity1")]
public string DoWork([ActivityTrigger] string input)
{
    // Perform actual work
    return "Result";
}
```

#### Entity Function (Virtual Actors)
```csharp
[FunctionName("Counter")]
public void Counter([EntityTrigger] IDurableEntityContext context)
{
    int current = context.GetState<int>();

    switch (context.OperationName)
    {
        case "add":
            current += context.GetInput<int>();
            break;
        case "get":
            context.Return(current);
            return;
    }

    context.SetState(current);
}
```

### Orchestration Patterns

#### Function Chaining
```csharp
var result1 = await context.CallActivityAsync<string>("Step1", null);
var result2 = await context.CallActivityAsync<string>("Step2", result1);
var result3 = await context.CallActivityAsync<string>("Step3", result2);
```

#### Fan-Out/Fan-In (Parallel Execution)
```csharp
var tasks = new List<Task<string>>();
for (int i = 0; i < 10; i++)
{
    tasks.Add(context.CallActivityAsync<string>("ProcessItem", i));
}

await Task.WhenAll(tasks);
var results = tasks.Select(t => t.Result).ToList();
```

#### Async HTTP APIs (Long-Running Operations)
```csharp
var instanceId = await client.StartNewAsync("LongRunningOrchestration", null);
return client.CreateCheckStatusResponse(req, instanceId);
```

**Response**:
```json
{
  "statusQueryGetUri": "https://.../status/{instanceId}",
  "sendEventPostUri": "https://.../raiseEvent/{instanceId}/{eventName}",
  "terminatePostUri": "https://.../terminate/{instanceId}"
}
```

#### Monitor (Polling)
```csharp
while (true)
{
    var status = await context.CallActivityAsync<string>("CheckStatus", jobId);
    if (status == "Complete") break;

    var nextCheck = context.CurrentUtcDateTime.AddMinutes(5);
    await context.CreateTimer(nextCheck, CancellationToken.None);
}
```

#### Human Interaction (Approval Workflow)
```csharp
var approvalEvent = context.WaitForExternalEvent<bool>("ApprovalEvent");
var timeout = context.CreateTimer(context.CurrentUtcDateTime.AddHours(72), CancellationToken.None);

var winner = await Task.WhenAny(approvalEvent, timeout);
if (winner == approvalEvent && approvalEvent.Result)
{
    // Approved
}
else
{
    // Rejected or timeout
}
```

## Configuration & Settings

### Application Settings
Managed in Azure Portal or `local.settings.json` (local development).

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "dotnet-isolated",
    "MyDatabaseConnection": "Server=...",
    "MyApiKey": "@Microsoft.KeyVault(SecretUri=https://...)"
  }
}
```

**Key Vault References**:
```
@Microsoft.KeyVault(SecretUri=https://myvault.vault.azure.net/secrets/mysecret/)
@Microsoft.KeyVault(VaultName=myvault;SecretName=mysecret)
```

### Host.json (Function App Configuration)
```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20
      }
    }
  },
  "functionTimeout": "00:05:00",
  "extensions": {
    "http": {
      "routePrefix": "api",
      "maxOutstandingRequests": 200,
      "maxConcurrentRequests": 100
    },
    "queues": {
      "maxPollingInterval": "00:00:02",
      "batchSize": 16,
      "maxDequeueCount": 5
    }
  }
}
```

## Scaling Behavior

### Consumption Plan Scaling
- **Scale Unit**: Function App instance
- **Scale Controller**: Monitors event rate and determines scale
- **Max Instances**: 200 (default), can request increase
- **Scale Out**: Add instances based on demand
- **Scale In**: Remove instances when load decreases
- **Scale to Zero**: After 20 minutes of inactivity (HTTP triggers excluded)

**Scaling Triggers**:
- **HTTP**: Queue-based (internal), based on requests/second
- **Timer**: No scaling (runs on single instance)
- **Queue**: Based on queue length and message age
- **Event Hub**: Based on partition count (1 instance per partition)
- **Service Bus**: Based on message count

### Premium Plan Scaling
- **Pre-warmed Instances**: Minimum always-on instances (1-20)
- **Max Burst**: Up to 100 instances
- **No Cold Start**: Pre-warmed instances eliminate cold starts
- **VNet Integration**: Private networking

## Monitoring & Diagnostics

### Application Insights Integration
**Automatic**:
- Request telemetry
- Dependency tracking (SQL, HTTP, etc.)
- Exception tracking
- Performance counters
- Custom metrics/events

**Configuration**:
```json
{
  "APPINSIGHTS_INSTRUMENTATIONKEY": "your-key",
  "APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=..."
}
```

**Custom Telemetry**:
```csharp
using Microsoft.ApplicationInsights;
using Microsoft.ApplicationInsights.DataContracts;

TelemetryClient telemetry = new TelemetryClient();

telemetry.TrackEvent("OrderProcessed", new Dictionary<string, string>
{
    { "OrderId", "12345" },
    { "Amount", "99.99" }
});
```

### Live Metrics
Real-time monitoring:
- Incoming requests
- Outgoing dependencies
- Exceptions
- Performance counters

### Log Streaming
Real-time log tailing from Azure Portal or CLI.

```bash
func azure functionapp logstream <FunctionAppName>
```

## Deployment

### Deployment Methods

#### 1. ZIP Deploy (Recommended)
```bash
func azure functionapp publish <FunctionAppName>
```

#### 2. Azure DevOps Pipelines
```yaml
- task: AzureFunctionApp@1
  inputs:
    azureSubscription: 'MySubscription'
    appType: 'functionApp'
    appName: 'MyFunctionApp'
    package: '$(Build.ArtifactStagingDirectory)/**/*.zip'
```

#### 3. GitHub Actions
```yaml
- name: Deploy to Azure Functions
  uses: Azure/functions-action@v1
  with:
    app-name: 'MyFunctionApp'
    package: './output'
    publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }}
```

#### 4. Container Deployment
```bash
az functionapp create --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --storage-account mystorageaccount \
  --plan MyPremiumPlan \
  --deployment-container-image-name myregistry.azurecr.io/myfunction:latest
```

### Deployment Slots
- **Production**: Main slot
- **Staging**: Pre-production testing
- **Swap**: Zero-downtime deployment

```bash
az functionapp deployment slot create \
  --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --slot staging

az functionapp deployment slot swap \
  --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --slot staging
```

## Networking

### VNet Integration (Premium/Dedicated Plans)
```bash
az functionapp vnet-integration add \
  --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --vnet MyVNet \
  --subnet MySubnet
```

**Use Cases**:
- Access private databases (SQL, Cosmos DB)
- Call internal APIs
- Hybrid cloud scenarios

### Private Endpoints
- Inbound connections via private IP
- Restrict public access
- Azure Private Link integration

### IP Restrictions
```json
{
  "ipSecurityRestrictions": [
    {
      "ipAddress": "192.168.1.0/24",
      "action": "Allow",
      "priority": 100
    },
    {
      "ipAddress": "0.0.0.0/0",
      "action": "Deny",
      "priority": 200
    }
  ]
}
```

## Best Practices

### Performance
1. Use Premium Plan for production (no cold starts)
2. Enable Application Insights sampling for high-volume apps
3. Use async/await properly in .NET
4. Batch process where possible (Event Hub, Service Bus)
5. Use output bindings instead of SDK clients

### Security
1. Use Managed Identity for Azure resource access
2. Store secrets in Key Vault
3. Enable authentication (Easy Auth, Azure AD)
4. Use VNet integration for private resources
5. Implement IP restrictions

### Cost Optimization
1. Use Consumption Plan for variable workloads
2. Monitor execution times and right-size timeout
3. Use batching to reduce invocations
4. Clean up old function versions
5. Use reserved capacity for predictable workloads

### Reliability
1. Implement idempotent functions
2. Use poison queues for failed messages
3. Set appropriate retry policies
4. Monitor and alert on failures
5. Test failure scenarios

## Limits & Quotas

### Consumption Plan
- Max execution time: 10 minutes
- Max memory: 1.5 GB
- Max instances: 200
- HTTP request timeout: 230 seconds (behind API Gateway)

### Premium Plan
- Max execution time: Unlimited (60 minutes default)
- Max memory: 14 GB
- Max instances: 100

### Function App Limits
- Max functions per app: No limit (but affects cold start)
- Max deployment package: 1 GB (ZIP), 100 GB (container)
- App Settings: 64 KB total

## Resources

### Official Documentation
- [Azure Functions Documentation](https://docs.microsoft.com/azure/azure-functions/)
- [Durable Functions](https://docs.microsoft.com/azure/azure-functions/durable/)
- [Azure Functions Best Practices](https://docs.microsoft.com/azure/azure-functions/functions-best-practices)

### Tools
- [Azure Functions Core Tools](https://docs.microsoft.com/azure/azure-functions/functions-run-local)
- [Visual Studio Code Extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions)
- [Durable Functions Monitor](https://github.com/microsoft/DurableFunctionsMonitor)

### Community
- [Azure Functions GitHub](https://github.com/Azure/Azure-Functions)
- [Azure Updates](https://azure.microsoft.com/updates/?product=functions)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/azure-functions)
