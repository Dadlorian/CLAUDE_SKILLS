# Azure Functions Best Practices Reference

## Hosting Plans

### Consumption Plan
**Billing**: Pay per execution (GB-s and executions)
**Scaling**: Automatic, event-driven
**Timeout**: 5 minutes (default), 10 minutes (max)
**Memory**: 1.5 GB
**Cold Start**: Yes (first request after idle may be slow)
**Always On**: No

**Best For**:
- Event-driven workloads with variable load
- Cost optimization (only pay when running)
- Batch processing with unpredictable schedules
- Low to medium consistent load

**Pricing Example**:
- First 1M executions free per month
- $0.20 per million executions
- $0.000016 per GB-s
- Typical cost for moderate usage: $5-20/month

### Premium Plan
**Billing**: Pre-warmed instances (per vCPU-s and memory)
**Scaling**: Faster than Consumption, pre-warmed instances
**Timeout**: 30 minutes (default), unlimited (max)
**Memory**: Up to 14 GB per instance
**Cold Start**: Eliminated (always-on instances)
**VNet Integration**: Yes

**Best For**:
- Low-latency requirements
- Avoiding cold starts
- VNet integration needed
- Longer execution times
- Predictable scaling

**Pricing**: Starts at ~$150/month for smallest instance

### Dedicated (App Service) Plan
**Billing**: Pay for App Service plan (hourly)
**Scaling**: Manual or auto-scale rules
**Timeout**: 30 minutes (default), unlimited (max)
**Shared Resources**: Can run alongside web apps
**VNet Integration**: Yes

**Best For**:
- Existing underutilized App Service plans
- Need for predictable billing
- Long-running functions
- Hybrid scenarios with web apps

## Function Design Patterns

### Single Responsibility
```csharp
// Good: One function per task
[FunctionName("ProcessOrder")]
public static async Task ProcessOrder(
    [QueueTrigger("orders")] Order order,
    [Queue("order-confirmation")] IAsyncCollector<OrderConfirmation> confirmations,
    ILogger log)
{
    // Only process order
    var confirmation = await ProcessOrderLogic(order);
    await confirmations.AddAsync(confirmation);
}

// Bad: Multiple responsibilities
[FunctionName("DoEverything")]
public static async Task DoEverything(
    [QueueTrigger("tasks")] Task task)
{
    // Process order, send email, update inventory, etc.
    // Too many responsibilities
}
```

### Stateless Design
Functions should be stateless; use external storage for state:
- Azure Storage (Blob, Queue, Table)
- Cosmos DB
- Redis Cache
- Durable Functions for orchestration state

```csharp
// Good: Stateless
[FunctionName("ProcessData")]
public static async Task ProcessData(
    [BlobTrigger("input/{name}")] Stream input,
    [Blob("output/{name}")] Stream output,
    string name,
    [Table("ProcessingLog")] IAsyncCollector<LogEntry> log)
{
    // Use bindings for state, function remains stateless
}

// Bad: Maintains state
private static Dictionary<string, int> _cache = new(); // Don't do this!
```

### Idempotency
Design functions to handle duplicate messages safely:

```csharp
[FunctionName("ProcessPayment")]
public static async Task ProcessPayment(
    [QueueTrigger("payments")] Payment payment,
    [Table("Payments")] CloudTable table)
{
    // Check if already processed
    var operation = TableOperation.Retrieve<PaymentEntity>(
        payment.OrderId, payment.TransactionId);
    var result = await table.ExecuteAsync(operation);

    if (result.Result != null)
    {
        // Already processed, skip
        return;
    }

    // Process payment
    await ProcessPaymentLogic(payment);

    // Record processing
    await table.ExecuteAsync(TableOperation.Insert(
        new PaymentEntity(payment.OrderId, payment.TransactionId)));
}
```

## Performance Optimization

### Minimize Cold Starts

**Use Premium Plan or Dedicated Plan** if cold starts are unacceptable.

**For Consumption Plan**:
```csharp
// Keep dependencies minimal
// Use dependency injection properly
[assembly: FunctionsStartup(typeof(Startup))]
public class Startup : FunctionsStartup
{
    public override void Configure(IFunctionsHostBuilder builder)
    {
        // Register only necessary services
        builder.Services.AddSingleton<IMyService, MyService>();

        // Use lazy initialization
        builder.Services.AddSingleton(sp =>
            new Lazy<ExpensiveService>(() => new ExpensiveService()));
    }
}
```

**Optimize package size**:
- Minimize dependencies
- Use trim/tree-shaking for deployed code
- Avoid large NuGet packages when possible

### Connection Management

**Reuse HTTP clients** (critical for avoiding port exhaustion):

```csharp
// Good: Static HttpClient
public static class HttpClientFactory
{
    private static readonly HttpClient _httpClient = new HttpClient();
    public static HttpClient Instance => _httpClient;
}

[FunctionName("CallApi")]
public static async Task<IActionResult> CallApi(
    [HttpTrigger(AuthorizationLevel.Function, "get")] HttpRequest req)
{
    var response = await HttpClientFactory.Instance.GetAsync("https://api.example.com");
    return new OkObjectResult(await response.Content.ReadAsStringAsync());
}

// Bad: New HttpClient per invocation
[FunctionName("CallApiBad")]
public static async Task<IActionResult> CallApiBad(
    [HttpTrigger(AuthorizationLevel.Function, "get")] HttpRequest req)
{
    using var client = new HttpClient(); // Don't do this!
    var response = await client.GetAsync("https://api.example.com");
    return new OkObjectResult(await response.Content.ReadAsStringAsync());
}
```

**Database connections**:
```csharp
// Good: Connection pooling with static instance
private static Lazy<SqlConnection> _connection = new Lazy<SqlConnection>(() =>
    new SqlConnection(Environment.GetEnvironmentVariable("SqlConnectionString")));

// Use connection pooling in connection string
// "Server=myserver;Database=mydb;Pooling=true;Min Pool Size=0;Max Pool Size=50;"
```

### Async/Await Best Practices

```csharp
// Good: Async all the way
[FunctionName("AsyncExample")]
public static async Task<IActionResult> AsyncExample(
    [HttpTrigger(AuthorizationLevel.Function, "get")] HttpRequest req,
    [Blob("container/blob")] Stream blob,
    ILogger log)
{
    using var reader = new StreamReader(blob);
    var content = await reader.ReadToEndAsync();
    var result = await ProcessAsync(content);
    return new OkObjectResult(result);
}

// Bad: Blocking calls
[FunctionName("BlockingExample")]
public static IActionResult BlockingExample(...)
{
    var content = reader.ReadToEnd(); // Blocks thread
    var result = ProcessAsync(content).Result; // Blocks thread, risk of deadlock
    return new OkObjectResult(result);
}
```

### Batch Processing

```csharp
// Process queue messages in batches
[FunctionName("ProcessBatch")]
public static async Task ProcessBatch(
    [QueueTrigger("items", Connection = "AzureWebJobsStorage")] string[] messages,
    ILogger log)
{
    // Process up to 16 messages at once (default)
    foreach (var message in messages)
    {
        await ProcessMessageAsync(message);
    }
}

// Configure in host.json
{
  "version": "2.0",
  "extensions": {
    "queues": {
      "batchSize": 16,
      "maxDequeueCount": 5,
      "newBatchThreshold": 8
    }
  }
}
```

## Error Handling and Retry

### Poison Queue Pattern

```csharp
[FunctionName("ProcessMessage")]
public static async Task ProcessMessage(
    [QueueTrigger("orders")] Order order,
    int dequeueCount,
    [Queue("orders-poison")] IAsyncCollector<Order> poisonQueue,
    ILogger log)
{
    try
    {
        await ProcessOrderAsync(order);
    }
    catch (Exception ex)
    {
        log.LogError(ex, $"Error processing order {order.Id}");

        if (dequeueCount >= 3)
        {
            // Move to poison queue for manual review
            await poisonQueue.AddAsync(order);
            return; // Don't throw, message will be removed from main queue
        }

        throw; // Retry
    }
}

// Configure max dequeue count in host.json
{
  "extensions": {
    "queues": {
      "maxDequeueCount": 3
    }
  }
}
```

### Retry Policies (Durable Functions)

```csharp
[FunctionName("OrchestrationWithRetry")]
public static async Task<string> RunOrchestrator(
    [OrchestrationTrigger] IDurableOrchestrationContext context)
{
    var retryOptions = new RetryOptions(
        firstRetryInterval: TimeSpan.FromSeconds(5),
        maxNumberOfAttempts: 3)
    {
        BackoffCoefficient = 2.0,
        MaxRetryInterval = TimeSpan.FromMinutes(1),
        RetryTimeout = TimeSpan.FromMinutes(5)
    };

    try
    {
        return await context.CallActivityWithRetryAsync<string>(
            "ProcessActivity", retryOptions, "input");
    }
    catch (FunctionFailedException ex)
    {
        // All retries failed
        await context.CallActivityAsync("SendAlert", ex.Message);
        throw;
    }
}
```

### Defensive Coding

```csharp
[FunctionName("DefensiveExample")]
public static async Task<IActionResult> DefensiveExample(
    [HttpTrigger(AuthorizationLevel.Function, "post")] HttpRequest req,
    ILogger log)
{
    try
    {
        // Validate input
        string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
        if (string.IsNullOrWhiteSpace(requestBody))
        {
            return new BadRequestObjectResult("Request body cannot be empty");
        }

        var data = JsonConvert.DeserializeObject<MyData>(requestBody);

        // Validate deserialized object
        if (data == null || string.IsNullOrWhiteSpace(data.RequiredField))
        {
            return new BadRequestObjectResult("Invalid data format");
        }

        // Process with timeout
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
        var result = await ProcessDataAsync(data, cts.Token);

        return new OkObjectResult(result);
    }
    catch (JsonException ex)
    {
        log.LogError(ex, "JSON parsing error");
        return new BadRequestObjectResult("Invalid JSON format");
    }
    catch (OperationCanceledException)
    {
        log.LogWarning("Operation timed out");
        return new StatusCodeResult(408); // Request Timeout
    }
    catch (Exception ex)
    {
        log.LogError(ex, "Unexpected error");
        return new StatusCodeResult(500);
    }
}
```

## Security Best Practices

### Authentication and Authorization

```csharp
// Function-level authorization
[FunctionName("SecureFunction")]
public static async Task<IActionResult> SecureFunction(
    [HttpTrigger(AuthorizationLevel.Function, "get")] HttpRequest req,
    ILogger log)
{
    // Requires function key in query string or header
    // x-functions-key: <key>
}

// Azure AD authentication
[FunctionName("AadSecuredFunction")]
public static async Task<IActionResult> AadSecuredFunction(
    [HttpTrigger(AuthorizationLevel.Anonymous, "get")] HttpRequest req,
    ILogger log)
{
    // Configure Azure AD in portal
    // Check claims
    if (!req.HttpContext.User.Identity.IsAuthenticated)
    {
        return new UnauthorizedResult();
    }

    var userEmail = req.HttpContext.User.FindFirst("email")?.Value;
    // Process request
}
```

### Managed Identity for Azure Resources

```csharp
// Use managed identity instead of connection strings
[FunctionName("UseManagedIdentity")]
public static async Task UseManagedIdentity(
    [TimerTrigger("0 */5 * * * *")] TimerInfo timer,
    ILogger log)
{
    // Access Key Vault
    var credential = new DefaultAzureCredential();
    var client = new SecretClient(
        new Uri("https://myvault.vault.azure.net/"), credential);
    var secret = await client.GetSecretAsync("MySecret");

    // Access Storage
    var blobServiceClient = new BlobServiceClient(
        new Uri("https://mystorage.blob.core.windows.net/"), credential);

    // Access SQL Database
    var sqlConnection = new SqlConnection(
        "Server=myserver.database.windows.net;Database=mydb;");
    sqlConnection.AccessToken = await credential.GetTokenAsync(
        new TokenRequestContext(new[] { "https://database.windows.net/.default" }));
}
```

### Secrets Management

```csharp
// Good: Use Key Vault references in app settings
// @Microsoft.KeyVault(SecretUri=https://myvault.vault.azure.net/secrets/MySecret/)

// Access in code
var secret = Environment.GetEnvironmentVariable("MySecret");

// Bad: Hardcoded secrets
var apiKey = "sk-1234567890abcdef"; // Never do this!
```

## Monitoring and Logging

### Structured Logging

```csharp
[FunctionName("StructuredLogging")]
public static async Task<IActionResult> StructuredLogging(
    [HttpTrigger(AuthorizationLevel.Function, "post")] HttpRequest req,
    ILogger log)
{
    var stopwatch = Stopwatch.StartNew();
    var orderId = req.Query["orderId"];

    log.LogInformation("Processing order {OrderId}", orderId);

    try
    {
        var result = await ProcessOrderAsync(orderId);

        stopwatch.Stop();
        log.LogInformation(
            "Order {OrderId} processed successfully in {ElapsedMs}ms. Result: {Result}",
            orderId, stopwatch.ElapsedMilliseconds, result);

        return new OkObjectResult(result);
    }
    catch (Exception ex)
    {
        log.LogError(ex, "Failed to process order {OrderId}", orderId);
        throw;
    }
}
```

### Application Insights Integration

```json
// host.json configuration
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20,
        "excludedTypes": "Request;Exception"
      },
      "enableDependencyTracking": true,
      "enablePerformanceCountersCollection": true
    },
    "logLevel": {
      "default": "Information",
      "Function": "Information",
      "Host.Aggregator": "Information"
    }
  }
}
```

### Custom Metrics

```csharp
[FunctionName("CustomMetrics")]
public static async Task CustomMetrics(
    [QueueTrigger("orders")] Order order,
    ILogger log)
{
    var telemetryClient = new TelemetryClient();

    // Track custom metric
    telemetryClient.TrackMetric("OrderValue", order.TotalAmount);

    // Track custom event
    telemetryClient.TrackEvent("OrderProcessed",
        properties: new Dictionary<string, string>
        {
            { "OrderId", order.Id },
            { "CustomerId", order.CustomerId }
        },
        metrics: new Dictionary<string, double>
        {
            { "ItemCount", order.Items.Count },
            { "TotalAmount", order.TotalAmount }
        });

    await ProcessOrderAsync(order);
}
```

## Configuration Management

### Environment-Specific Settings

```csharp
public class Startup : FunctionsStartup
{
    public override void Configure(IFunctionsHostBuilder builder)
    {
        var environment = Environment.GetEnvironmentVariable("AZURE_FUNCTIONS_ENVIRONMENT");

        var config = new ConfigurationBuilder()
            .SetBasePath(Environment.CurrentDirectory)
            .AddJsonFile("local.settings.json", optional: true)
            .AddJsonFile($"appsettings.{environment}.json", optional: true)
            .AddEnvironmentVariables()
            .Build();

        builder.Services.AddSingleton<IConfiguration>(config);
    }
}
```

### Feature Flags

```csharp
[FunctionName("FeatureFlag")]
public static async Task<IActionResult> FeatureFlag(
    [HttpTrigger(AuthorizationLevel.Function, "get")] HttpRequest req,
    ILogger log)
{
    var useNewFeature = Environment.GetEnvironmentVariable("UseNewFeature") == "true";

    if (useNewFeature)
    {
        return new OkObjectResult(await NewFeatureAsync());
    }
    else
    {
        return new OkObjectResult(await OldFeatureAsync());
    }
}
```

## Deployment Best Practices

### Deployment Slots

```bash
# Create staging slot
az functionapp deployment slot create \
    --name myFunctionApp \
    --resource-group myRG \
    --slot staging

# Deploy to staging
func azure functionapp publish myFunctionApp --slot staging

# Test staging slot
# https://myFunctionApp-staging.azurewebsites.net

# Swap to production
az functionapp deployment slot swap \
    --name myFunctionApp \
    --resource-group myRG \
    --slot staging
```

### CI/CD Pipeline (Azure DevOps YAML)

```yaml
trigger:
  branches:
    include:
    - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  buildConfiguration: 'Release'

steps:
- task: DotNetCoreCLI@2
  displayName: 'Restore packages'
  inputs:
    command: 'restore'
    projects: '**/*.csproj'

- task: DotNetCoreCLI@2
  displayName: 'Build'
  inputs:
    command: 'build'
    projects: '**/*.csproj'
    arguments: '--configuration $(buildConfiguration)'

- task: DotNetCoreCLI@2
  displayName: 'Run tests'
  inputs:
    command: 'test'
    projects: '**/*Tests.csproj'

- task: DotNetCoreCLI@2
  displayName: 'Publish'
  inputs:
    command: 'publish'
    publishWebProjects: false
    projects: '**/*.csproj'
    arguments: '--configuration $(buildConfiguration) --output $(Build.ArtifactStagingDirectory)'

- task: AzureFunctionApp@1
  displayName: 'Deploy to Azure Functions'
  inputs:
    azureSubscription: 'MyAzureSubscription'
    appType: 'functionApp'
    appName: 'myFunctionApp'
    package: '$(Build.ArtifactStagingDirectory)/**/*.zip'
    deploymentMethod: 'zipDeploy'
```

### Blue-Green Deployment

```bash
# Current production is "blue"
# Deploy new version to staging slot ("green")
func azure functionapp publish myFunctionApp --slot staging

# Run smoke tests against staging
curl https://myFunctionApp-staging.azurewebsites.net/api/health

# Swap staging to production (green becomes production)
az functionapp deployment slot swap \
    --name myFunctionApp \
    --resource-group myRG \
    --slot staging

# If issues occur, swap back immediately
az functionapp deployment slot swap \
    --name myFunctionApp \
    --resource-group myRG \
    --slot staging
```

## Common Anti-Patterns to Avoid

### Don't: Store State in Memory
```csharp
// Bad
private static List<Order> _orders = new List<Order>(); // Lost on scale-out!
```

### Don't: Block on Async
```csharp
// Bad
var result = SomeAsyncMethod().Result; // Can cause deadlocks
```

### Don't: Create New HttpClient per Request
```csharp
// Bad
using var client = new HttpClient(); // Port exhaustion!
```

### Don't: Ignore Concurrency
```csharp
// Bad: No consideration for concurrent executions
// Multiple functions might process the same message
```

### Don't: Log Sensitive Data
```csharp
// Bad
log.LogInformation($"Credit card: {creditCard.Number}"); // PCI violation!
```

### Don't: Use Console.WriteLine
```csharp
// Bad
Console.WriteLine("Processing order"); // Won't appear in Application Insights

// Good
log.LogInformation("Processing order");
```

## Performance Checklist

- [ ] Use Premium or Dedicated plan if cold starts are unacceptable
- [ ] Reuse connections (HTTP, DB, etc.)
- [ ] Use async/await throughout
- [ ] Implement batch processing where appropriate
- [ ] Configure appropriate scaling limits
- [ ] Enable Application Insights
- [ ] Use structured logging
- [ ] Implement retry logic for transient failures
- [ ] Design for idempotency
- [ ] Use managed identities instead of connection strings
- [ ] Minimize deployment package size
- [ ] Use dependency injection properly
- [ ] Configure appropriate timeout values
- [ ] Implement circuit breakers for external dependencies
- [ ] Monitor and alert on key metrics
