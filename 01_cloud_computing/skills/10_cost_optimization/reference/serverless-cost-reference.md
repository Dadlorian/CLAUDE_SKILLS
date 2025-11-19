# Serverless Cost Reference

## Overview

Serverless computing offers a pay-per-use pricing model that can significantly reduce costs for appropriate workloads. However, without proper optimization, serverless can also become expensive. This reference covers cost optimization strategies for serverless services across AWS, Azure, and GCP.

## Serverless Pricing Models

### Function-as-a-Service (FaaS) Pricing

**AWS Lambda**:
- **Per Request**: $0.20 per 1M requests
- **Duration**: Based on GB-seconds of memory allocated × execution time
  - First 400,000 GB-seconds free per month
  - $0.0000166667 per GB-second after free tier
- **Provisioned Concurrency**: $0.0000041667 per GB-second (for warm instances)
- **Example**: 128MB function running 100ms
  - Duration cost: 0.128 GB × 0.1 sec × $0.0000166667 = $0.000000213 per invocation

**Azure Functions**:
- **Consumption Plan**:
  - Executions: $0.20 per 1M executions
  - Execution time: $0.000016 per GB-second
  - Free grant: 1M executions, 400,000 GB-seconds per month
- **Premium Plan**: Pre-warmed instances, VNet integration
  - Per vCPU per hour + per GB per hour
- **Dedicated Plan**: Run on App Service Plan (fixed cost)

**GCP Cloud Functions**:
- **Invocations**: $0.40 per 1M invocations
- **Compute Time**:
  - $0.0000025 per GB-second
  - $0.0000100 per GHz-second (CPU time)
- **Free tier**: 2M invocations, 400,000 GB-seconds, 200,000 GHz-seconds per month
- **Always-on**: Keep instances warm (additional cost)

### Comparison Matrix

| Provider | Request Cost (per 1M) | Duration Cost (per GB-second) | Free Tier Requests | Free Tier Duration |
|----------|----------------------|------------------------------|-------------------|-------------------|
| **AWS Lambda** | $0.20 | $0.0000166667 | 1M | 400,000 GB-sec |
| **Azure Functions** | $0.20 | $0.000016 | 1M | 400,000 GB-sec |
| **GCP Functions** | $0.40 | $0.0000025 | 2M | 400,000 GB-sec |

## Function Cost Optimization

### 1. Memory Allocation Optimization

**Concept**: Lambda/Functions allocate CPU proportionally to memory. More memory = more CPU = faster execution (but higher per-second cost).

**Optimization Process**:
1. Test function with different memory settings (128MB - 10,240MB)
2. Measure execution time for each
3. Calculate total cost: (memory cost per second) × (execution time) + (request cost)
4. Find sweet spot (minimum total cost)

**Example**:
```
128 MB: 1000ms execution → Cost: $0.0000021
256 MB: 500ms execution → Cost: $0.0000021
512 MB: 250ms execution → Cost: $0.0000021
1024 MB: 150ms execution → Cost: $0.0000025
```
Optimal: 512 MB (fastest for same cost)

**Tools**:
- AWS Lambda Power Tuning (open source): Automated memory optimization
- Azure Functions Testing: Manual benchmarking
- GCP Cloud Functions: Test different memory tiers

### 2. Execution Time Optimization

**Code Optimization**:
- Reduce dependencies and package size
- Lazy load libraries
- Efficient algorithms and data structures
- Minimize I/O operations
- Use connection pooling

**Example Optimizations**:
```python
# Bad: Import everything
import boto3
import pandas as pd
import numpy as np

# Good: Import only what you need
from boto3 import client
from pandas import DataFrame
```

**Cold Start Reduction**:
- Minimize package size
- Use lightweight runtimes (Node.js, Python vs. Java)
- Keep functions warm with provisioned concurrency (if justified)
- Use container image caching (Lambda)

**Caching**:
- Cache connections (database, API clients) outside handler
- Cache data in global scope
- Use external cache (ElastiCache, Redis) for shared data

```python
# Initialize outside handler (reused across invocations)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('MyTable')

def lambda_handler(event, context):
    # Use cached connection
    response = table.get_item(Key={'id': event['id']})
    return response
```

### 3. Concurrency Management

**AWS Lambda Concurrency**:
- **Reserved Concurrency**: Guarantee capacity, limit spend
- **Provisioned Concurrency**: Pre-warmed instances (eliminate cold starts)
- **Burst Concurrency**: 3000 initial (account-level), then +500/min

**Cost Impact**:
```
Provisioned Concurrency: $0.0000041667 per GB-second
vs
On-demand: $0.0000166667 per GB-second (but includes cold starts)
```

**When to Use Provisioned Concurrency**:
- Latency-sensitive applications (< 100ms cold start unacceptable)
- Predictable traffic patterns
- Cost justified by business value of reduced latency

**Optimization**:
- Use for production only, not dev/test
- Scale provisioned concurrency with scheduled scaling
- Monitor utilization (aim for > 60% utilization)

### 4. Request Optimization

**Batch Processing**:
- Process multiple records per invocation
- Reduce request count (cheaper than many small invocations)
- Trade-off: Increased execution time vs. fewer requests

**Example**:
```
Instead of: 1000 invocations processing 1 record each
Use: 10 invocations processing 100 records each
Savings: 990 fewer requests = $0.20 per 1M requests
```

**Async Processing**:
- Use queues (SQS, Service Bus, Pub/Sub) to buffer requests
- Batch processing from queue
- Smooths traffic spikes, reduces concurrency costs

### 5. Timeout Optimization

**Right-Size Timeout**:
- Default: Often 3-15 minutes
- Optimize: Set to expected duration + small buffer
- Avoid: Functions running to timeout on error (wasted cost)

**Example**:
```
Expected duration: 2 seconds
Appropriate timeout: 5 seconds (allows for variance)
Avoid: 15-minute timeout (runaway executions waste money)
```

**Error Handling**:
- Fail fast on errors
- Use circuit breakers
- Implement retries with backoff
- Monitor and alert on timeouts

## Serverless Data Services Cost Optimization

### DynamoDB (AWS)

**Capacity Modes**:

**On-Demand Mode**:
- Pay per request
- $1.25 per million write requests, $0.25 per million reads
- No capacity planning
- Best for: Unpredictable traffic, spiky workloads

**Provisioned Mode**:
- Pre-allocate read/write capacity units (RCUs/WCUs)
- $0.00065 per WCU-hour, $0.00013 per RCU-hour
- Auto-scaling available
- Best for: Predictable traffic, sustained load

**Cost Comparison**:
```
Workload: 1M writes/day, 5M reads/day

On-Demand:
- Writes: 1M × $1.25/million = $1.25/day
- Reads: 5M × $0.25/million = $1.25/day
- Total: $2.50/day = $75/month

Provisioned (with auto-scaling):
- Write capacity: ~12 WCUs × $0.00065 × 730 hours = $5.69/month
- Read capacity: ~60 RCUs × $0.00013 × 730 hours = $5.69/month
- Total: ~$11.38/month

Savings: $63.62/month (85% savings)
```

**Optimization Strategies**:
- Use provisioned for consistent workloads
- Enable auto-scaling for provisioned mode
- Use on-demand for unpredictable or new workloads
- Monitor and optimize capacity settings

**Additional DynamoDB Optimizations**:
- Use Global Secondary Indexes (GSIs) sparingly (consume capacity)
- Optimize item size (1KB item = 1 WCU, 4KB = 1 RCU)
- Batch operations (BatchGetItem, BatchWriteItem)
- Use DynamoDB Streams efficiently
- Enable point-in-time recovery selectively (adds 20% cost)

### Cosmos DB (Azure)

**Throughput Modes**:

**Provisioned Throughput**:
- Pre-allocate Request Units (RUs)
- $0.008 per 100 RU/s per hour
- Autoscale available (up to 10x base throughput)

**Serverless**:
- Pay per request
- $0.25 per million RU consumed
- Best for: Intermittent, unpredictable traffic

**Autoscale vs Manual**:
- Autoscale: Automatic scaling within configured range
- Manual: Fixed throughput (cheaper if stable)

**Optimization Strategies**:
- Right-size RU allocation
- Use autoscale for variable workloads
- Optimize queries (reduce RU consumption)
- Partition effectively (even distribution)
- Use TTL to automatically delete old data

### Firestore (GCP)

**Pricing Components**:
- **Document Reads**: $0.06 per 100,000
- **Document Writes**: $0.18 per 100,000
- **Document Deletes**: $0.02 per 100,000
- **Storage**: $0.18 per GB/month
- **Network Egress**: Standard GCP egress rates

**Optimization Strategies**:
- Minimize reads with caching
- Batch writes where possible
- Use subcollections to avoid reading unnecessary data
- Implement pagination (reduce reads per query)
- Clean up old data (storage costs)

## Serverless Compute Cost Optimization

### AWS Fargate

**Pricing**:
- Per vCPU per hour: $0.04048
- Per GB memory per hour: $0.004445
- Minimum: 0.25 vCPU, 0.5 GB memory

**Optimization Strategies**:
- Right-size CPU and memory allocations
- Use Spot Fargate (up to 70% discount for fault-tolerant workloads)
- Combine with Savings Plans (up to 50% savings)
- Use appropriate task size (avoid over-provisioning)
- Implement autoscaling (scale to zero when idle)

**Example**:
```
Task: 1 vCPU, 2 GB memory
On-Demand: $0.04048 + (2 × $0.004445) = $0.04937/hour = $36.04/month (24×7)
With Savings Plan (50%): $18.02/month
With Spot (70%): $10.81/month
```

### Azure Container Instances (ACI)

**Pricing**:
- Per vCPU-second: $0.0000012
- Per GB-second: $0.0000001 - $0.00000014 (by region)
- Minimum billing: 1 second

**Optimization Strategies**:
- Right-size container resources
- Use lifecycle policies (start/stop based on schedule)
- Optimize container startup time
- Batch processing in fewer, larger containers

### GCP Cloud Run

**Pricing**:
- **CPU**: $0.00002400 per vCPU-second (allocated)
- **Memory**: $0.00000250 per GB-second (allocated)
- **Requests**: $0.40 per million requests
- **CPU allocation**:
  - During request processing only (recommended): Lower cost
  - Always allocated: Higher cost but consistent performance

**Optimization Strategies**:
- CPU-allocated-during-request-processing (cheaper for bursty workloads)
- Right-size CPU and memory
- Optimize cold start (smaller images, lightweight languages)
- Set appropriate concurrency (requests per container instance)
- Use minimum instances sparingly (costs money when idle)

## Serverless Storage Cost Optimization

### S3 / Blob Storage / Cloud Storage

**Storage Classes and Tiering** (covered in storage-cost-reference.md):
- Intelligent tiering for automated cost optimization
- Lifecycle policies to move to cheaper tiers
- Delete old data automatically

**Request Optimization**:
- Batch operations (list, get multiple objects)
- Use CloudFront/CDN to cache (reduce requests)
- Compress objects (reduce storage and transfer costs)
- Use S3 Select to query data in place (reduce data transfer)

**Example S3 Costs**:
```
Storage: 1 TB × $0.023/GB = $23/month (Standard)
Requests: 10M GET × $0.0004/1000 = $4/month
Data Transfer: 1 TB egress × $0.09/GB = $90/month
Total: $117/month

With CloudFront:
- Cache hit rate: 80%
- Requests: 2M origin GET × $0.0004/1000 = $0.80/month
- CloudFront data transfer: $85/month (cheaper than S3 direct)
- Total: ~$109/month
```

## API Gateway and Event Services

### AWS API Gateway

**Pricing (REST API)**:
- **Requests**: $3.50 per million (first 333M), $2.80 per million (next 667M), $2.38 per million (> 1B)
- **Data Transfer**: Standard AWS egress rates
- **Caching**: $0.020 per hour per GB cache size

**HTTP API** (cheaper alternative):
- **Requests**: $1.00 per million (first 300M), $0.90 per million (> 300M)
- **Limited features vs. REST API but significantly cheaper

**WebSocket API**:
- **Connections**: $0.25 per million messages
- **Minutes**: $0.25 per million connection minutes

**Optimization Strategies**:
- Use HTTP API when features suffice (71% cheaper)
- Enable caching to reduce backend calls
- Implement request throttling to control costs
- Use custom domain to avoid per-API charges
- Compress responses (reduce data transfer)

### Azure API Management

**Consumption Tier**:
- Per execution: $3.50 per million
- No minimum fee, pay-per-use
- Best for: Serverless, variable traffic

**Developer, Basic, Standard, Premium Tiers**:
- Fixed monthly fee + included calls
- Higher tiers for advanced features and scale

### GCP Cloud Endpoints / API Gateway

**Cloud Endpoints** (with ESP):
- First 2M calls free
- $3.00 per million calls thereafter

**API Gateway** (managed):
- $0.20 per million API calls (cheaper than AWS/Azure)

## EventBridge / Event Grid / Pub/Sub

### AWS EventBridge

**Pricing**:
- **Events Published**: $1.00 per million (first 100M), $0.60 per million (beyond)
- **Schema Registry**: $0.10 per ingested event, $0.13 per schema version
- **Cross-Region/Account**: Additional data transfer fees

**Optimization**:
- Combine multiple events into single event where possible
- Filter events at source to reduce ingested events
- Use EventBridge carefully for high-volume (consider SNS/SQS)

### Azure Event Grid

**Pricing**:
- **Operations**: $0.60 per million operations (first 100K free)
- **Advanced filtering**: Additional $0.50 per million

**Optimization**:
- Batch events where possible
- Use filtering to reduce downstream processing

### GCP Pub/Sub

**Pricing**:
- **Message Ingestion**: $40 per TB
- **Message Delivery**: $40 per TB
- **Storage**: $0.27 per GB per month (retained messages)
- First 10 GB per month free

**Optimization**:
- Minimize message size
- Delete messages promptly (avoid storage costs)
- Batch publish and pull operations
- Use snapshots sparingly (storage costs)

## Step Functions / Logic Apps / Workflows

### AWS Step Functions

**Standard Workflows**:
- $25 per million state transitions
- Long-running workflows (up to 1 year)

**Express Workflows**:
- $1 per million requests
- Duration: $0.00001667 per GB-second
- Short-duration workflows (< 5 minutes)
- 97% cheaper for high-volume, short workflows

**Optimization**:
- Use Express for high-volume, short-duration workflows
- Optimize state transitions (fewer states where possible)
- Use Map state efficiently (parallel processing)
- Consider direct service integrations (skip Lambda where possible)

### Azure Logic Apps

**Consumption Plan**:
- $0.000025 per action execution
- Connectors: $0.000125 - $0.001 per execution (depends on connector)

**Standard Plan** (fixed pricing):
- Per vCPU per hour
- Best for high-volume workflows

## Optimization Best Practices

### 1. Architect for Cost
- Design with serverless pricing model in mind
- Batch operations to reduce request counts
- Use caching aggressively
- Choose right serverless service for workload

### 2. Monitor and Alert
- Track function duration and invocation count
- Alert on cost anomalies
- Monitor cold starts and provision concurrency judiciously
- Use cost allocation tags for serverless resources

### 3. Right-Size Allocations
- Optimize memory for functions
- Right-size container resources (Fargate, Cloud Run, ACI)
- Right-size database capacity (DynamoDB, Cosmos DB)

### 4. Leverage Free Tiers
- AWS Lambda: 1M requests, 400K GB-seconds/month
- Azure Functions: 1M executions, 400K GB-seconds/month
- GCP Functions: 2M invocations, 400K GB-seconds/month
- Use free tiers for dev/test environments

### 5. Use Appropriate Service Tier
- Functions: Consumption vs. Premium/Dedicated
- API Gateway: HTTP API vs. REST API
- Step Functions: Express vs. Standard
- Database: On-demand vs. Provisioned

### 6. Implement Timeout and Error Handling
- Set appropriate timeouts
- Implement retry logic with backoff
- Use dead letter queues
- Fail fast on errors (avoid wasted execution time)

### 7. Optimize Cold Starts (When Worth It)
- Minimize package size
- Use lightweight languages (Node.js, Python)
- Provisioned concurrency for critical paths
- Container image optimization

### 8. Control Concurrency
- Set reserved concurrency limits (avoid runaway costs)
- Implement throttling at API Gateway
- Use queue-based processing for buffering

## Common Pitfalls

1. **Over-Provisioning Memory**: Allocating more memory than needed
2. **Ignoring Cold Starts**: Using provisioned concurrency unnecessarily
3. **Too Many Invocations**: Not batching operations
4. **Runaway Executions**: No timeout or concurrency limits
5. **Wrong Service Choice**: Using serverless for always-on workloads
6. **Not Monitoring Costs**: Serverless costs can sneak up without monitoring
7. **Inefficient Code**: Not optimizing execution time
8. **Wrong Capacity Mode**: Using on-demand for predictable workloads

## Cost Estimation Tools

### AWS Lambda Cost Calculator
- Formula: (Invocations × $0.20/million) + (GB-seconds × $0.0000166667)
- Factor in provisioned concurrency if used
- Consider data transfer costs

### Azure Functions Cost Calculator
- Consumption plan calculator
- Premium plan sizing
- Dedicated plan costs

### GCP Cloud Functions Pricing Calculator
- Invocations + GB-seconds + GHz-seconds
- Consider always-on instances cost

### Third-Party Tools
- **Infracost**: IaC cost estimation including serverless
- **Cloud Cost Management Platforms**: CloudHealth, Cloudability

## Resources

### AWS Serverless
- Lambda Pricing: aws.amazon.com/lambda/pricing
- Lambda Power Tuning: github.com/alexcasalboni/aws-lambda-power-tuning
- Serverless Best Practices: docs.aws.amazon.com/lambda/latest/dg/best-practices.html

### Azure Serverless
- Functions Pricing: azure.microsoft.com/pricing/details/functions
- Logic Apps Pricing: azure.microsoft.com/pricing/details/logic-apps
- Serverless Best Practices: docs.microsoft.com/azure/azure-functions/functions-best-practices

### GCP Serverless
- Cloud Functions Pricing: cloud.google.com/functions/pricing
- Cloud Run Pricing: cloud.google.com/run/pricing
- Serverless Best Practices: cloud.google.com/architecture/serverless

### Tools and Communities
- Serverless Framework: serverless.com
- Serverless Stack (SST): sst.dev
- Serverless community: serverless.com/community
