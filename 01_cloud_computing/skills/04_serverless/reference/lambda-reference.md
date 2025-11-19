# AWS Lambda Reference Guide

## Overview

AWS Lambda is Amazon's Function-as-a-Service (FaaS) platform that lets you run code without provisioning or managing servers. You pay only for the compute time you consume.

## Core Concepts

### Function
A Lambda function is the basic unit of execution containing:
- **Handler**: Entry point for execution (e.g., `index.handler`)
- **Runtime**: Execution environment (Node.js, Python, Java, Go, Ruby, .NET, custom)
- **Code**: Your application logic
- **Configuration**: Memory, timeout, environment variables, IAM role

### Execution Model
```
Event Source → Lambda Service → Function Instance
                    ↓
              Container Initialization (Cold Start)
                    ↓
              Handler Execution
                    ↓
              Response/Error
```

### Concurrency
- **Definition**: Number of function instances serving requests simultaneously
- **Account Limit**: 1,000 concurrent executions per region (soft limit, can be increased)
- **Reserved Concurrency**: Guarantee capacity for critical functions
- **Provisioned Concurrency**: Keep instances warm to avoid cold starts

## Supported Runtimes

### Managed Runtimes (AWS-Maintained)

| Runtime | Versions | Cold Start | Use Case |
|---------|----------|------------|----------|
| **Node.js** | 18.x, 20.x | 100-300ms | APIs, lightweight processing |
| **Python** | 3.9, 3.10, 3.11, 3.12 | 100-400ms | Data processing, ML inference |
| **Java** | 8, 11, 17, 21 | 1-3s | Enterprise applications |
| **Go** | 1.x | 100-200ms | High performance, low latency |
| **.NET** | 6, 8 | 500ms-2s | Windows workloads, enterprise |
| **Ruby** | 3.2, 3.3 | 200-500ms | Web applications, scripting |

### Custom Runtimes
- **Runtime API**: Implement any language using Runtime API
- **Container Images**: Up to 10GB, bring any runtime
- **Lambda Layers**: Share code, libraries, custom runtimes (max 5 layers, 250MB total)

**Popular Custom Runtimes**:
- Rust (via custom runtime or container)
- PHP (via custom runtime layer)
- Swift (via custom runtime)
- Elixir/Erlang (via custom runtime)

## Function Configuration

### Memory & CPU
```yaml
Memory: 128 MB - 10,240 MB (10 GB)
  - Increments: 1 MB
  - CPU: Scales proportionally with memory
  - 1,769 MB = 1 full vCPU
  - 10,240 MB = ~6 vCPUs
```

**Memory Allocation Strategy**:
- More memory = more CPU = faster execution = potentially lower cost
- Use [AWS Lambda Power Tuning](https://github.com/alexcasalboni/aws-lambda-power-tuning) to find optimal setting

### Timeout
```yaml
Min: 1 second
Max: 15 minutes (900 seconds)
Default: 3 seconds
```

**Best Practices**:
- Set timeout based on 99th percentile execution time + buffer
- Don't use 15 minutes as default
- Consider Step Functions for longer workflows

### Environment Variables
```yaml
Max Size: 4 KB total (all env vars combined)
Encryption: Optional KMS encryption at rest
Runtime: Decrypted and available to function
```

**Best Practices**:
- Use AWS Secrets Manager or Parameter Store for secrets
- Use environment variables for configuration
- Avoid hardcoding values

### Ephemeral Storage (/tmp)
```yaml
Default: 512 MB
Max: 10,240 MB (10 GB)
Pricing: $0.0000000309 per GB-second
```

**Characteristics**:
- Available at `/tmp` directory
- Persists for lifetime of execution environment
- Shared across invocations in same instance
- Encrypted at rest

**Use Cases**:
- Download large files for processing
- Cache data between invocations (warm instances)
- Temporary file operations

## Invocation Models

### 1. Synchronous (Request-Response)
```
Client → Lambda (wait) → Response
```

**Event Sources**:
- API Gateway (REST, HTTP API)
- Application Load Balancer
- Lambda Function URLs
- CloudFront (Lambda@Edge)
- Cognito
- Alexa
- Direct invocations (SDK, CLI)

**Characteristics**:
- Client waits for response
- Error handling is client responsibility
- Timeout: API Gateway 29s, ALB 30s, direct 15min

**Error Behavior**:
- Returns error to caller
- No automatic retries (client must retry)

### 2. Asynchronous (Event)
```
Event Source → SQS Queue (internal) → Lambda
              ↓ (immediate)
            Success Response
```

**Event Sources**:
- S3
- SNS
- EventBridge
- SES
- CloudFormation
- CodeCommit
- Config

**Characteristics**:
- Event queued internally (SQS)
- Immediate success response (202 Accepted)
- Automatic retries (2 times, with delays)
- Dead Letter Queue (DLQ) for failed events

**Configuration**:
```yaml
Retry Attempts: 2 (default)
Maximum Age: 6 hours
DLQ: SQS or SNS
Destinations:
  - On Success: SQS, SNS, Lambda, EventBridge
  - On Failure: SQS, SNS, Lambda, EventBridge
```

### 3. Stream Processing (Poll-Based)
```
Stream → Lambda (polls) → Batch Processing
```

**Event Sources**:
- Kinesis Data Streams
- DynamoDB Streams
- Amazon MQ (RabbitMQ, ActiveMQ)
- Apache Kafka (MSK, self-managed)
- Amazon SQS

**Characteristics**:
- Lambda polls the stream
- Processes records in batches
- Sequential processing per shard
- Checkpointing for resumption

**Configuration**:
```yaml
Batch Size: 1-10,000 records
Batch Window: 0-300 seconds
Concurrent Batches Per Shard: 1-10
Starting Position: LATEST | TRIM_HORIZON | AT_TIMESTAMP
On Failure:
  - Retry until success (Kinesis/DynamoDB)
  - Max age or max retries (SQS)
  - DLQ (SQS only)
Bisect on Error: Split batch on failure (Kinesis/DynamoDB)
```

## Lambda Execution Environment

### Lifecycle
```
INIT Phase (Cold Start):
  1. Download code
  2. Start runtime
  3. Run init code (outside handler)
  4. Run handler

INVOKE Phase (Warm):
  1. Run handler
  2. Return response
  3. Environment may be reused

SHUTDOWN Phase:
  1. No new invocations
  2. Runtime shutdown hook
  3. Environment terminated
```

### Cold Start Optimization

**Factors Affecting Cold Start**:
1. **Runtime**: Go, Python, Node.js fastest; Java, .NET slowest
2. **Code Size**: Smaller packages = faster cold starts
3. **VPC**: VPC functions add 500ms-1s (ENI creation) - improved with Hyperplane
4. **Dependencies**: Fewer dependencies = faster initialization

**Optimization Strategies**:
1. **Use Lightweight Runtimes**: Python, Node.js, Go over Java, .NET
2. **Minimize Package Size**:
   ```bash
   # Node.js: Remove dev dependencies
   npm install --production

   # Python: Use slim packages, avoid unnecessary libraries
   pip install requests --target ./package
   ```
3. **Lazy Load Dependencies**:
   ```python
   # Bad: Import at top
   import heavy_library

   def handler(event, context):
       return heavy_library.process()

   # Good: Import when needed
   def handler(event, context):
       import heavy_library
       return heavy_library.process()
   ```
4. **Use Lambda SnapStart** (Java only):
   - Snapshot initialized environment
   - Restore from snapshot for sub-second starts
   - Reduces Java cold starts by 90%
5. **Provisioned Concurrency**:
   - Keep instances warm
   - Pricing: $0.000004167 per GB-second
   - Use for latency-critical APIs
6. **Connection Pooling**:
   ```python
   # Initialize outside handler (reused)
   import psycopg2
   conn = psycopg2.connect(DATABASE_URL)

   def handler(event, context):
       # Reuse connection from warm instance
       cursor = conn.cursor()
       # ...
   ```

### SnapStart (Java 11+)
```yaml
Enable: SnapStart enabled for function
How It Works:
  1. Lambda initializes function
  2. Takes snapshot of memory and disk state
  3. Caches snapshot
  4. Restores from snapshot for new invocations
Result: ~90% reduction in cold start time
Considerations:
  - Network connections not restored
  - Randomness/uniqueness issues (use afterRestore hook)
  - Secrets should be refreshed in afterRestore
```

## IAM & Permissions

### Execution Role (Function → AWS Services)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/MyTable"
    }
  ]
}
```

**Managed Policies**:
- `AWSLambdaBasicExecutionRole`: CloudWatch Logs permissions
- `AWSLambdaVPCAccessExecutionRole`: VPC network interfaces
- `AWSLambdaDynamoDBExecutionRole`: DynamoDB streams
- `AWSLambdaKinesisExecutionRole`: Kinesis streams
- `AWSLambdaSQSQueueExecutionRole`: SQS polling

### Resource Policy (Services → Function)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:MyFunction",
      "Condition": {
        "StringEquals": {
          "AWS:SourceAccount": "123456789012"
        },
        "ArnLike": {
          "AWS:SourceArn": "arn:aws:s3:::my-bucket"
        }
      }
    }
  ]
}
```

## Networking

### Without VPC (Default)
- Public internet access
- AWS services via public endpoints
- No access to private resources
- Fastest cold starts

### With VPC
- Access to private resources (RDS, ElastiCache, internal services)
- Can access internet via NAT Gateway
- Hyperplane ENI (shared, fast attachment)
- Security groups control outbound/inbound traffic

**VPC Configuration**:
```yaml
VPC:
  SubnetIds:
    - subnet-12345678  # Private subnet (2+ recommended)
    - subnet-87654321
  SecurityGroupIds:
    - sg-12345678      # Allows outbound to RDS, ElastiCache
```

**Best Practices**:
- Use private subnets for Lambda
- Use NAT Gateway for internet access
- Configure security groups for least privilege
- Use VPC endpoints for AWS services (cost savings, no NAT needed)

## Versioning & Aliases

### Versions
- **$LATEST**: Mutable, latest code
- **Published Versions**: Immutable snapshots (1, 2, 3, ...)
- **Version ARN**: `arn:aws:lambda:us-east-1:123456789012:function:MyFunction:1`

**Publishing a Version**:
```bash
aws lambda publish-version \
  --function-name MyFunction \
  --description "Production release 2024-01-15"
```

### Aliases
- **Pointer to Version**: prod → v5, staging → v6, dev → $LATEST
- **Traffic Shifting**: Canary, Linear, All-at-once
- **Weighted Aliases**: 90% v5, 10% v6

**Creating an Alias**:
```bash
aws lambda create-alias \
  --function-name MyFunction \
  --name prod \
  --function-version 5
```

**Traffic Shifting (Canary)**:
```bash
aws lambda update-alias \
  --function-name MyFunction \
  --name prod \
  --routing-config '{"AdditionalVersionWeights": {"6": 0.10}}'
```

## Lambda Layers

**Purpose**: Share code, dependencies, configuration across functions

**Characteristics**:
- Max 5 layers per function
- Max 250 MB total (unzipped)
- Extracted to `/opt` directory
- Versioned and immutable

**Use Cases**:
- Shared libraries (boto3, requests, etc.)
- Custom runtimes (PHP, Rust)
- Configuration files
- Monitoring agents (X-Ray, Datadog)

**Creating a Layer**:
```bash
# Package layer
mkdir -p layer/python
pip install requests -t layer/python

# Create layer
cd layer
zip -r ../layer.zip .

# Publish layer
aws lambda publish-layer-version \
  --layer-name my-dependencies \
  --zip-file fileb://../layer.zip \
  --compatible-runtimes python3.11
```

**Using a Layer**:
```bash
aws lambda update-function-configuration \
  --function-name MyFunction \
  --layers arn:aws:lambda:us-east-1:123456789012:layer:my-dependencies:1
```

## Container Image Support

**Benefits**:
- Up to 10 GB image size (vs 250 MB for zip)
- Use familiar Docker workflow
- Bring any runtime or binary
- Test locally with Docker

**Requirements**:
- Must implement Lambda Runtime API
- Use AWS base images or runtime interface clients
- Push to Amazon ECR
- Function code at `/var/task`

**Example Dockerfile**:
```dockerfile
FROM public.ecr.aws/lambda/python:3.11

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "app.handler" ]
```

**Build and Push**:
```bash
# Build
docker build -t my-function .

# Authenticate to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag my-function:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-function:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-function:latest
```

## Function URLs

**Purpose**: HTTPS endpoint for Lambda without API Gateway

**Features**:
- Automatic endpoint: `https://<url-id>.lambda-url.<region>.on.aws/`
- IAM or public authentication
- CORS configuration
- Lower latency than API Gateway
- No cost (included in Lambda pricing)

**Use Cases**:
- Webhooks
- Simple APIs
- Serverless backends
- Form handlers

**Configuration**:
```bash
aws lambda create-function-url-config \
  --function-name MyFunction \
  --auth-type AWS_IAM \
  --cors '{
    "AllowOrigins": ["https://example.com"],
    "AllowMethods": ["GET", "POST"],
    "AllowHeaders": ["Content-Type"],
    "MaxAge": 300
  }'
```

## Monitoring & Logging

### CloudWatch Metrics (Automatic)
- **Invocations**: Total invocation count
- **Duration**: Execution time (min, max, avg)
- **Errors**: Function errors (exceptions)
- **Throttles**: Invocations throttled due to concurrency limits
- **ConcurrentExecutions**: Concurrent executions
- **DeadLetterErrors**: Failures writing to DLQ
- **IteratorAge**: Age of last record processed (streams)

### CloudWatch Logs
**Log Groups**: `/aws/lambda/<function-name>`

**Structured Logging** (recommended):
```python
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info(json.dumps({
        "event": "process_order",
        "order_id": "12345",
        "amount": 99.99,
        "request_id": context.request_id
    }))
```

### AWS X-Ray (Distributed Tracing)
**Enable**: Checkbox in Lambda console or `TracingConfig: {Mode: Active}`

**Benefits**:
- Trace requests across services
- Identify bottlenecks
- Visualize service map
- Analyze latency

**SDK Usage**:
```python
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

@xray_recorder.capture('process_payment')
def process_payment(order_id):
    # Traced automatically
    pass
```

## Pricing

### Compute Pricing
```
Requests: $0.20 per 1M requests
Duration: $0.0000166667 per GB-second

Free Tier (per month):
  - 1M requests
  - 400,000 GB-seconds
```

### Example Calculation
```
Scenario: 5M requests, 128 MB memory, 200ms average duration

Compute Time:
  - 5M requests × 0.2 seconds = 1M seconds
  - 1M seconds × 128 MB / 1024 = 125,000 GB-seconds
  - (125,000 - 400,000 free) = 0 (covered by free tier)

Requests:
  - (5M - 1M free) = 4M requests
  - 4M × $0.20 / 1M = $0.80

Total: $0.80/month
```

### Additional Costs
- **Provisioned Concurrency**: $0.000004167 per GB-second
- **Data Transfer**: $0.09 per GB (outbound)
- **Ephemeral Storage**: $0.0000000309 per GB-second (above 512 MB)

## Limits & Quotas

### Soft Limits (Can Request Increase)
- Concurrent executions: 1,000 per region
- Function and layer storage: 75 GB
- Elastic network interfaces (VPC): 250 per region

### Hard Limits (Cannot Increase)
- Function timeout: 15 minutes
- Function memory: 10,240 MB
- Deployment package (zip): 50 MB (zipped), 250 MB (unzipped)
- Container image: 10 GB
- Environment variables: 4 KB
- Layers: 5 per function, 250 MB total
- /tmp storage: 10 GB (configurable)
- File descriptors: 1,024
- Execution processes/threads: 1,024

## Best Practices

### Performance
1. Minimize cold starts (lightweight runtimes, small packages)
2. Use provisioned concurrency for critical paths
3. Optimize memory allocation (use Power Tuning)
4. Reuse connections and resources across invocations
5. Use layers for shared dependencies

### Security
1. Least privilege IAM roles
2. Encrypt environment variables with KMS
3. Use Secrets Manager for sensitive data
4. Enable VPC only when necessary
5. Scan dependencies for vulnerabilities
6. Enable AWS X-Ray for observability

### Cost Optimization
1. Right-size memory allocation
2. Use asynchronous invocation where possible
3. Batch processing over individual invocations
4. Use provisioned concurrency sparingly
5. Monitor and alert on costs

### Reliability
1. Implement idempotency
2. Configure DLQs for async invocations
3. Set appropriate timeouts
4. Handle errors gracefully
5. Use retries with exponential backoff for external services

## Resources

### Official Documentation
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Lambda Operator Guide](https://docs.aws.amazon.com/lambda/latest/operatorguide/)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)

### Tools
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [AWS Lambda Power Tuning](https://github.com/alexcasalboni/aws-lambda-power-tuning)
- [Serverless Framework](https://www.serverless.com/)

### Community
- [AWS Serverless Patterns](https://serverlessland.com/patterns)
- [AWS Compute Blog](https://aws.amazon.com/blogs/compute/)
- [r/aws subreddit](https://www.reddit.com/r/aws/)
