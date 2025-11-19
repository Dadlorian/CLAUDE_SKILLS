# Step Functions & Workflow Orchestration Reference

## Overview

Serverless workflow orchestration services coordinate multiple distributed services into resilient, scalable applications using visual workflows.

## AWS Step Functions

### Overview
Step Functions is a serverless orchestration service that lets you coordinate multiple AWS services into serverless workflows.

### Workflow Types

#### Standard Workflows
```yaml
Duration: Up to 1 year
Execution Model: Exactly-once
Pricing: $25 per million state transitions
Use Cases:
  - Long-running workflows
  - Audit requirements
  - High durability needed
Features:
  - Full execution history
  - Visual execution tracking
  - Automatic retries
```

#### Express Workflows
```yaml
Duration: Up to 5 minutes
Execution Model: At-least-once
Pricing: $1 per million requests + duration
Types:
  - Synchronous: Wait for completion (API Gateway, Lambda)
  - Asynchronous: Fire-and-forget (EventBridge, IoT)
Use Cases:
  - High-volume event processing
  - IoT data ingestion
  - Streaming data transformation
Features:
  - Lower cost at high volume
  - CloudWatch Logs integration
  - Faster execution starts
```

### States

#### Task State
Execute work using Lambda, ECS, Fargate, Glue, SageMaker, etc.

```json
{
  "Type": "Task",
  "Resource": "arn:aws:states:::lambda:invoke",
  "Parameters": {
    "FunctionName": "ProcessOrder",
    "Payload": {
      "orderId.$": "$.orderId"
    }
  },
  "Retry": [{
    "ErrorEquals": ["States.TaskFailed"],
    "IntervalSeconds": 2,
    "MaxAttempts": 3,
    "BackoffRate": 2.0
  }],
  "Catch": [{
    "ErrorEquals": ["States.ALL"],
    "Next": "HandleError"
  }],
  "Next": "SendConfirmation"
}
```

**Supported Services** (AWS SDK Integrations):
- Lambda, ECS, Fargate, Batch
- DynamoDB, SNS, SQS, EventBridge
- Step Functions (nested workflows)
- SageMaker, Glue, EMR, Athena
- API Gateway HTTP endpoints
- 200+ AWS services via SDK integration

#### Choice State
Conditional branching based on input.

```json
{
  "Type": "Choice",
  "Choices": [
    {
      "Variable": "$.amount",
      "NumericGreaterThan": 100,
      "Next": "RequireApproval"
    },
    {
      "Variable": "$.amount",
      "NumericLessThanEquals": 100,
      "Next": "AutoApprove"
    }
  ],
  "Default": "DefaultState"
}
```

**Operators**: StringEquals, NumericGreaterThan, BooleanEquals, TimestampLessThan, And, Or, Not

#### Parallel State
Execute branches in parallel.

```json
{
  "Type": "Parallel",
  "Branches": [
    {
      "StartAt": "ProcessPayment",
      "States": {
        "ProcessPayment": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:...:ProcessPayment",
          "End": true
        }
      }
    },
    {
      "StartAt": "SendEmail",
      "States": {
        "SendEmail": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:...:SendEmail",
          "End": true
        }
      }
    }
  ],
  "Next": "CompleteOrder"
}
```

#### Map State
Process array items dynamically.

```json
{
  "Type": "Map",
  "ItemsPath": "$.orders",
  "MaxConcurrency": 10,
  "Iterator": {
    "StartAt": "ProcessOrder",
    "States": {
      "ProcessOrder": {
        "Type": "Task",
        "Resource": "arn:aws:lambda:...:ProcessOrder",
        "End": true
      }
    }
  },
  "Next": "AllOrdersProcessed"
}
```

**Distributed Map** (Standard Workflows):
- Process large datasets (millions of items)
- Read from S3, DynamoDB, or JSON
- Parallel execution at scale
- Export results to S3

#### Wait State
Delay execution.

```json
{
  "Type": "Wait",
  "Seconds": 300,
  "Next": "CheckStatus"
}

// Or wait until timestamp
{
  "Type": "Wait",
  "Timestamp": "2024-01-15T12:00:00Z",
  "Next": "ProcessScheduled"
}

// Or wait using input
{
  "Type": "Wait",
  "TimestampPath": "$.scheduledTime",
  "Next": "Process"
}
```

#### Pass State
Transform input, inject fixed data.

```json
{
  "Type": "Pass",
  "Result": {
    "status": "processing",
    "timestamp": "2024-01-15"
  },
  "ResultPath": "$.metadata",
  "Next": "NextState"
}
```

#### Succeed/Fail States
Terminal states.

```json
{
  "Type": "Succeed"
}

{
  "Type": "Fail",
  "Error": "OrderProcessingFailed",
  "Cause": "Payment declined"
}
```

### Error Handling

#### Retry
```json
{
  "Retry": [
    {
      "ErrorEquals": ["States.Timeout"],
      "IntervalSeconds": 1,
      "MaxAttempts": 2,
      "BackoffRate": 2.0
    },
    {
      "ErrorEquals": ["States.TaskFailed"],
      "IntervalSeconds": 2,
      "MaxAttempts": 3,
      "BackoffRate": 1.5
    },
    {
      "ErrorEquals": ["States.ALL"],
      "IntervalSeconds": 5,
      "MaxAttempts": 5,
      "BackoffRate": 2.0
    }
  ]
}
```

**Backoff Calculation**:
```
Delay = IntervalSeconds * (BackoffRate ^ retryAttempt)
Example: 2 * (2 ^ 0) = 2s, 2 * (2 ^ 1) = 4s, 2 * (2 ^ 2) = 8s
```

#### Catch
```json
{
  "Catch": [
    {
      "ErrorEquals": ["PaymentDeclined"],
      "ResultPath": "$.error",
      "Next": "RefundProcess"
    },
    {
      "ErrorEquals": ["States.ALL"],
      "ResultPath": "$.error",
      "Next": "FallbackHandler"
    }
  ]
}
```

**Error Types**:
- `States.ALL`: Catch-all
- `States.Timeout`: Task timeout
- `States.TaskFailed`: Task failed
- `States.Permissions`: IAM permissions error
- Custom errors from Lambda/services

### Input/Output Processing

#### InputPath
Select portion of input to pass to state.

```json
{
  "InputPath": "$.order",
  // State receives only $.order, not entire input
  "Next": "ProcessOrder"
}
```

#### OutputPath
Select portion of state result to pass to next state.

```json
{
  "OutputPath": "$.result",
  // Next state receives only $.result
  "Next": "NextState"
}
```

#### ResultPath
Where to place state result in input.

```json
{
  "ResultPath": "$.paymentResult",
  // Original input + payment result merged
  "Next": "NextState"
}

// ResultPath: null discards result, passes input unchanged
{
  "ResultPath": null,
  "Next": "NextState"
}
```

#### Parameters
Transform input before passing to task.

```json
{
  "Parameters": {
    "orderId.$": "$.id",
    "amount.$": "$.total",
    "currency": "USD",
    "timestamp.$": "$$.Execution.StartTime",
    "executionId.$": "$$.Execution.Id"
  }
}
```

**Context Object** (`$$`):
- `$$.Execution.Id`: Execution ARN
- `$$.Execution.StartTime`: Start timestamp
- `$$.State.Name`: Current state name
- `$$.StateMachine.Id`: State machine ARN

### Callbacks & Integrations

#### Callback Pattern (Wait for external completion)
```json
{
  "Type": "Task",
  "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
  "Parameters": {
    "FunctionName": "StartLongRunningJob",
    "Payload": {
      "taskToken.$": "$$.Task.Token",
      "input.$": "$"
    }
  },
  "Next": "ProcessResult"
}
```

**Lambda callback**:
```python
import boto3

stepfunctions = boto3.client('stepfunctions')

def handler(event, context):
    task_token = event['taskToken']

    # Start long-running job...

    # Later, send success
    stepfunctions.send_task_success(
        taskToken=task_token,
        output='{"status": "completed"}'
    )

    # Or send failure
    # stepfunctions.send_task_failure(
    #     taskToken=task_token,
    #     error='JobFailed',
    #     cause='Processing error'
    # )
```

### Optimized Integrations

#### DynamoDB
```json
{
  "Type": "Task",
  "Resource": "arn:aws:states:::dynamodb:putItem",
  "Parameters": {
    "TableName": "Orders",
    "Item": {
      "orderId": {"S.$": "$.orderId"},
      "amount": {"N.$": "$.amount"},
      "status": {"S": "processing"}
    }
  },
  "Next": "NextState"
}
```

#### SNS Publish
```json
{
  "Type": "Task",
  "Resource": "arn:aws:states:::sns:publish",
  "Parameters": {
    "TopicArn": "arn:aws:sns:us-east-1:123456789012:OrderNotifications",
    "Message.$": "$"
  },
  "Next": "NextState"
}
```

#### SQS SendMessage
```json
{
  "Type": "Task",
  "Resource": "arn:aws:states:::sqs:sendMessage",
  "Parameters": {
    "QueueUrl": "https://sqs.us-east-1.amazonaws.com/123456789012/MyQueue",
    "MessageBody.$": "$"
  },
  "Next": "NextState"
}
```

#### Athena StartQueryExecution
```json
{
  "Type": "Task",
  "Resource": "arn:aws:states:::athena:startQueryExecution.sync",
  "Parameters": {
    "QueryString": "SELECT * FROM orders WHERE date = '2024-01-15'",
    "QueryExecutionContext": {
      "Database": "mydb"
    },
    "ResultConfiguration": {
      "OutputLocation": "s3://my-bucket/results/"
    }
  },
  "Next": "ProcessResults"
}
```

### Workflow Patterns

#### Human Approval
```json
{
  "Type": "Task",
  "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
  "Parameters": {
    "FunctionName": "RequestApproval",
    "Payload": {
      "taskToken.$": "$$.Task.Token",
      "order.$": "$.order"
    }
  },
  "TimeoutSeconds": 86400,
  "Catch": [{
    "ErrorEquals": ["States.Timeout"],
    "Next": "ApprovalTimeout"
  }],
  "Next": "ProcessApproved"
}
```

#### Polling for Completion
```json
{
  "Type": "Task",
  "Resource": "arn:aws:lambda:...:CheckJobStatus",
  "Next": "JobComplete?"
},
{
  "Type": "Choice",
  "Choices": [{
    "Variable": "$.status",
    "StringEquals": "COMPLETE",
    "Next": "Success"
  }],
  "Default": "Wait30Seconds"
},
{
  "Type": "Wait",
  "Seconds": 30,
  "Next": "CheckJobStatus"
}
```

#### Saga Pattern (Distributed Transaction)
```json
{
  "StartAt": "ReserveInventory",
  "States": {
    "ReserveInventory": {
      "Type": "Task",
      "Resource": "...",
      "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "ReleaseReservation"}],
      "Next": "ProcessPayment"
    },
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "...",
      "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "ReleaseReservation"}],
      "Next": "ShipOrder"
    },
    "ShipOrder": {
      "Type": "Task",
      "Resource": "...",
      "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "RefundPayment"}],
      "End": true
    },
    "RefundPayment": {
      "Type": "Task",
      "Resource": "...",
      "Next": "ReleaseReservation"
    },
    "ReleaseReservation": {
      "Type": "Task",
      "Resource": "...",
      "Next": "Fail"
    },
    "Fail": {"Type": "Fail"}
  }
}
```

## Azure Durable Functions

### Overview
Extension of Azure Functions that enables stateful workflows in a serverless environment.

### Function Types

#### Orchestrator Function
```csharp
[FunctionName("OrderOrchestrator")]
public async Task<string> Run(
    [OrchestrationTrigger] IDurableOrchestrationContext context)
{
    var order = context.GetInput<Order>();

    // Sequential
    await context.CallActivityAsync("ReserveInventory", order);
    var payment = await context.CallActivityAsync<PaymentResult>("ProcessPayment", order);

    // Parallel (fan-out/fan-in)
    var tasks = new List<Task>();
    tasks.Add(context.CallActivityAsync("SendEmail", order));
    tasks.Add(context.CallActivityAsync("UpdateAnalytics", order));
    await Task.WhenAll(tasks);

    return "Order processed";
}
```

**Constraints**:
- Must be deterministic
- No direct I/O (use activity functions)
- No `DateTime.Now` (use `context.CurrentUtcDateTime`)
- No random numbers (use `context.NewGuid()`)
- No async operations except activity/sub-orchestration calls

#### Activity Function
```csharp
[FunctionName("ProcessPayment")]
public PaymentResult Run(
    [ActivityTrigger] Order order,
    ILogger log)
{
    // Perform actual work (I/O, external calls)
    var result = PaymentGateway.Charge(order.Amount);
    return result;
}
```

### Patterns

#### Function Chaining
```csharp
var result1 = await context.CallActivityAsync<string>("Step1", input);
var result2 = await context.CallActivityAsync<string>("Step2", result1);
var result3 = await context.CallActivityAsync<string>("Step3", result2);
```

#### Fan-Out/Fan-In
```csharp
var parallelTasks = new List<Task<int>>();
for (int i = 0; i < 10; i++)
{
    var task = context.CallActivityAsync<int>("ProcessItem", i);
    parallelTasks.Add(task);
}

await Task.WhenAll(parallelTasks);
var sum = parallelTasks.Sum(t => t.Result);
```

#### Async HTTP APIs
```csharp
[FunctionName("StartOrchestration")]
public async Task<IActionResult> HttpStart(
    [HttpTrigger(AuthorizationLevel.Function, "post")] HttpRequest req,
    [DurableClient] IDurableOrchestrationClient starter)
{
    string instanceId = await starter.StartNewAsync("OrderOrchestrator", input);

    return starter.CreateCheckStatusResponse(req, instanceId);
}
```

**Response**:
```json
{
  "id": "abc123",
  "statusQueryGetUri": "https://.../status/abc123",
  "sendEventPostUri": "https://.../raiseEvent/abc123/{eventName}",
  "terminatePostUri": "https://.../terminate/abc123"
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

#### Human Interaction
```csharp
using (var timeout = new CancellationTokenSource())
{
    var approvalEvent = context.WaitForExternalEvent<bool>("ApprovalEvent");
    var timeoutTask = context.CreateTimer(
        context.CurrentUtcDateTime.AddHours(72),
        timeout.Token
    );

    var winner = await Task.WhenAny(approvalEvent, timeoutTask);

    if (winner == approvalEvent && approvalEvent.Result)
    {
        timeout.Cancel();
        // Process approval
    }
    else
    {
        // Timeout or rejection
    }
}
```

**Raising External Event**:
```csharp
await client.RaiseEventAsync(instanceId, "ApprovalEvent", approved: true);
```

### Entity Functions (Virtual Actors)
```csharp
[FunctionName("Counter")]
public void Counter([EntityTrigger] IDurableEntityContext context)
{
    int current = context.GetState<int>();

    switch (context.OperationName)
    {
        case "add":
            current += context.GetInput<int>();
            context.SetState(current);
            break;
        case "get":
            context.Return(current);
            break;
        case "reset":
            context.SetState(0);
            break;
    }
}
```

**Signal Entity** (fire-and-forget):
```csharp
var entityId = new EntityId("Counter", "myCounter");
await client.SignalEntityAsync(entityId, "add", 5);
```

**Call Entity** (request-response):
```csharp
var result = await context.CallEntityAsync<int>(entityId, "get");
```

## Google Cloud Workflows

### Overview
Fully managed orchestration service using YAML/JSON syntax.

### Syntax (YAML)
```yaml
main:
  params: [order]
  steps:
    - reserveInventory:
        call: http.post
        args:
          url: https://inventory-service.example.com/reserve
          body:
            orderId: ${order.id}
            items: ${order.items}
        result: reservation

    - processPayment:
        call: http.post
        args:
          url: https://payment-service.example.com/charge
          body:
            amount: ${order.total}
            orderId: ${order.id}
        result: payment

    - checkPaymentStatus:
        switch:
          - condition: ${payment.status == "SUCCESS"}
            next: shipOrder
          - condition: ${payment.status == "DECLINED"}
            next: releaseInventory

    - shipOrder:
        call: http.post
        args:
          url: https://shipping-service.example.com/ship
          body:
            orderId: ${order.id}
        result: shipping
        next: end

    - releaseInventory:
        call: http.post
        args:
          url: https://inventory-service.example.com/release
          body:
            reservationId: ${reservation.id}
        next: fail

    - fail:
        raise: "Payment declined"
```

### Features

#### Parallel Execution
```yaml
- parallelTasks:
    parallel:
      branches:
        - sendEmail:
            call: http.post
            args:
              url: https://email-service/send
              body: ${emailData}
        - updateAnalytics:
            call: http.post
            args:
              url: https://analytics-service/update
              body: ${analyticsData}
        - logAudit:
            call: http.post
            args:
              url: https://audit-service/log
              body: ${auditData}
```

#### Iteration
```yaml
- processOrders:
    for:
      value: order
      in: ${orders}
      steps:
        - processOrder:
            call: http.post
            args:
              url: https://order-service/process
              body: ${order}
```

#### Retry and Error Handling
```yaml
- callExternalAPI:
    try:
      call: http.post
      args:
        url: https://external-api.example.com/data
        timeout: 30
      result: apiResponse
    retry:
      predicate: ${http.default_retry}
      max_retries: 5
      backoff:
        initial_delay: 1
        max_delay: 60
        multiplier: 2
    except:
      as: e
      steps:
        - handleError:
            call: http.post
            args:
              url: https://error-handler/log
              body: ${e}
```

#### Subworkflows
```yaml
main:
  steps:
    - callSubworkflow:
        call: processOrder
        args:
          order: ${orderData}

processOrder:
  params: [order]
  steps:
    - validate:
        call: http.post
        args:
          url: https://validator/validate
          body: ${order}
```

## Comparison

| Feature | Step Functions | Durable Functions | Cloud Workflows |
|---------|----------------|-------------------|-----------------|
| **Language** | JSON (ASL) | C#, JavaScript, Python | YAML, JSON |
| **Max Duration** | 1 year (Standard) | Unlimited | 1 year |
| **Pricing** | Per state transition | Per execution + duration | Per step + duration |
| **Integration** | 200+ AWS services | Azure services + HTTP | GCP services + HTTP |
| **Visual Designer** | Yes | No (code-based) | Yes |
| **Local Testing** | SAM CLI | Durable Functions SDK | Workflows emulator |
| **Stateful Actors** | No | Yes (Entity Functions) | No |

## Best Practices

### General
1. Keep workflows simple and focused
2. Use idempotent activities
3. Implement comprehensive error handling
4. Monitor execution metrics and costs
5. Version workflows for breaking changes

### Performance
1. Minimize state transitions (Step Functions cost)
2. Use Express Workflows for high volume (Step Functions)
3. Batch process where possible
4. Avoid tight polling loops (use exponential backoff)

### Reliability
1. Implement retry with exponential backoff
2. Use dead letter queues for failed executions
3. Set appropriate timeouts
4. Design for eventual consistency
5. Test failure scenarios

### Cost Optimization
1. Use Express Workflows for eligible workloads (AWS)
2. Minimize state transitions (consolidate logic in Lambda)
3. Use direct SDK integrations (avoid Lambda wrapper)
4. Monitor and alert on unexpected execution patterns

## Resources

- [Step Functions Documentation](https://docs.aws.amazon.com/step-functions/)
- [Durable Functions Documentation](https://docs.microsoft.com/azure/azure-functions/durable/)
- [Cloud Workflows Documentation](https://cloud.google.com/workflows/docs)
- [AWS Step Functions Workshop](https://step-functions-workshop.go-aws.com/)
