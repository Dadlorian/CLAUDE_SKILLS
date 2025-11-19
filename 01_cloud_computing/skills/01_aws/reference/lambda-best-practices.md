# AWS Lambda Best Practices Reference

## Function Design Principles

### 1. Single Responsibility
Each Lambda function should do one thing well.

**Good Example:**
```python
# process_order.py - Handles order processing only
def lambda_handler(event, context):
    order = parse_order(event)
    validate_order(order)
    save_order(order)
    return {'statusCode': 200, 'body': 'Order processed'}
```

**Bad Example:**
```python
# monolith.py - Too many responsibilities
def lambda_handler(event, context):
    # Processes orders, manages inventory, sends emails, generates reports
    # This should be split into multiple functions
```

### 2. Stateless Design
Lambda functions should be stateless; use external storage for state.

```python
# Good: State stored in DynamoDB
import boto3
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('user-sessions')

def lambda_handler(event, context):
    user_id = event['user_id']
    session = table.get_item(Key={'user_id': user_id})
    # Process with session data
```

### 3. Idempotency
Functions should produce the same result when called multiple times with the same input.

```python
import hashlib
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('idempotency-tracking')

def lambda_handler(event, context):
    # Generate idempotency key
    request_id = event.get('request_id') or hashlib.sha256(
        json.dumps(event, sort_keys=True).encode()
    ).hexdigest()

    # Check if already processed
    response = table.get_item(Key={'request_id': request_id})
    if 'Item' in response:
        return response['Item']['result']

    # Process request
    result = process_request(event)

    # Store result
    table.put_item(Item={
        'request_id': request_id,
        'result': result,
        'ttl': int(time.time()) + 86400  # 24 hour TTL
    })

    return result
```

## Performance Optimization

### 1. Cold Start Reduction

#### Choose Appropriate Runtime
```
Cold start times (approximate):
- Python: 100-300ms
- Node.js: 100-300ms
- Java: 500-2000ms
- .NET: 500-1500ms
- Go: 100-400ms
- Rust: 100-300ms
```

#### Use Provisioned Concurrency
```bash
aws lambda put-provisioned-concurrency-config \
  --function-name my-function \
  --provisioned-concurrent-executions 10 \
  --qualifier prod
```

#### Optimize Package Size
```python
# Before: 250MB package with entire pandas library
import pandas as pd

# After: 5MB package using AWS Data Wrangler layer
import awswrangler as wr  # Use Lambda Layer
```

#### Initialize Outside Handler
```python
import boto3
import os

# Initialize once (cold start)
s3 = boto3.client('s3')
table_name = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

# Reused across invocations (warm start)
def lambda_handler(event, context):
    # Use pre-initialized clients
    s3.get_object(Bucket='my-bucket', Key='my-key')
    table.put_item(Item={'id': '123', 'data': 'value'})
```

### 2. Memory and CPU Optimization

Lambda CPU scales with memory. Optimal memory often reduces cost despite higher per-ms price.

```python
# Test different memory configurations
# 128 MB: 5000ms execution = $0.0000208
# 1024 MB: 1000ms execution = $0.0000167 (20% cheaper!)
# 2048 MB: 800ms execution = $0.0000268
```

**Finding Optimal Memory:**
```bash
# Use AWS Lambda Power Tuning
# https://github.com/alexcasalboni/aws-lambda-power-tuning

# Or use CloudWatch Insights to analyze
fields @timestamp, @memorySize, @maxMemoryUsed, @duration, @billedDuration
| filter @type = "REPORT"
| stats avg(@duration), avg(@maxMemoryUsed), count(*) by @memorySize
```

### 3. Connection Pooling and Reuse

```python
import os
from functools import lru_cache
import psycopg2

# Connection pooling for RDS
@lru_cache(maxsize=1)
def get_db_connection():
    """Cached database connection reused across invocations"""
    return psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        connect_timeout=3
    )

def lambda_handler(event, context):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (event['user_id'],))
    result = cursor.fetchone()
    return result
```

### 4. Async and Parallel Processing

```python
import asyncio
import aioboto3

async def process_item(s3_client, bucket, key):
    obj = await s3_client.get_object(Bucket=bucket, Key=key)
    data = await obj['Body'].read()
    # Process data
    return len(data)

async def lambda_handler_async(event, context):
    session = aioboto3.Session()
    async with session.client('s3') as s3_client:
        tasks = [
            process_item(s3_client, 'my-bucket', record['s3']['object']['key'])
            for record in event['Records']
        ]
        results = await asyncio.gather(*tasks)
        return {'processed': len(results)}

def lambda_handler(event, context):
    return asyncio.run(lambda_handler_async(event, context))
```

## Error Handling and Retries

### 1. Proper Exception Handling

```python
import json
import logging
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        # Validate input
        if 'user_id' not in event:
            raise ValidationError("user_id is required")

        # Process request
        result = process_request(event)

        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }

    except ValidationError as e:
        # Client error - don't retry
        logger.warning(f"Validation error: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }

    except Exception as e:
        # Server error - will be retried
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise  # Re-raise for retry
```

### 2. Dead Letter Queues (DLQ)

```python
# Configure DLQ in Terraform
resource "aws_lambda_function" "processor" {
  function_name = "order-processor"

  dead_letter_config {
    target_arn = aws_sqs_queue.dlq.arn
  }

  # Async invocation config
  retry_attempts = 2
  maximum_event_age_in_seconds = 3600
}

resource "aws_sqs_queue" "dlq" {
  name = "order-processor-dlq"
  message_retention_seconds = 1209600  # 14 days
}
```

### 3. Exponential Backoff for External Calls

```python
import time
import random
from functools import wraps

def exponential_backoff(max_retries=3, base_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise

                    # Calculate delay with jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s")
                    time.sleep(delay)
        return wrapper
    return decorator

@exponential_backoff(max_retries=3)
def call_external_api(endpoint):
    response = requests.get(endpoint, timeout=5)
    response.raise_for_status()
    return response.json()
```

### 4. Circuit Breaker Pattern

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

    def on_success(self):
        self.failures = 0
        self.state = CircuitState.CLOSED

    def on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Global circuit breaker (persists across warm invocations)
payment_api_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

def lambda_handler(event, context):
    try:
        result = payment_api_breaker.call(call_payment_api, event['payment_data'])
        return {'statusCode': 200, 'body': json.dumps(result)}
    except Exception as e:
        return {'statusCode': 503, 'body': 'Service temporarily unavailable'}
```

## Security Best Practices

### 1. Least Privilege IAM Roles

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/orders"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/orders/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt"
      ],
      "Resource": "arn:aws:kms:us-east-1:123456789012:key/abc-123",
      "Condition": {
        "StringEquals": {
          "kms:ViaService": "s3.us-east-1.amazonaws.com"
        }
      }
    }
  ]
}
```

### 2. Secrets Management

```python
import os
import json
import boto3
from functools import lru_cache

@lru_cache(maxsize=1)
def get_secret(secret_name):
    """Cache secrets for the lifetime of the container"""
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

def lambda_handler(event, context):
    # Get secret (cached after first call)
    db_creds = get_secret(os.environ['DB_SECRET_NAME'])

    # Use credentials
    conn = connect_to_db(
        host=db_creds['host'],
        user=db_creds['username'],
        password=db_creds['password']
    )
```

### 3. Environment Variable Encryption

```python
import os
import base64
import boto3

# Encrypt environment variables with KMS
kms = boto3.client('kms')

def decrypt_env_var(encrypted_var_name):
    encrypted = os.environ[encrypted_var_name]
    decrypted = kms.decrypt(
        CiphertextBlob=base64.b64decode(encrypted),
        EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']}
    )
    return decrypted['Plaintext'].decode('utf-8')

# Decrypt once during cold start
API_KEY = decrypt_env_var('ENCRYPTED_API_KEY')

def lambda_handler(event, context):
    # Use decrypted API_KEY
    pass
```

### 4. Input Validation

```python
from typing import Dict, Any
import re

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_request(event: Dict[str, Any]) -> Dict[str, Any]:
    errors = []

    # Required fields
    if 'email' not in event:
        errors.append("email is required")
    elif not validate_email(event['email']):
        errors.append("invalid email format")

    # Type validation
    if 'age' in event and not isinstance(event['age'], int):
        errors.append("age must be an integer")

    # Range validation
    if 'age' in event and not (0 < event['age'] < 150):
        errors.append("age must be between 1 and 150")

    # String length
    if 'name' in event and len(event['name']) > 100:
        errors.append("name must be less than 100 characters")

    if errors:
        raise ValidationError(f"Validation failed: {', '.join(errors)}")

    return event
```

## Observability and Monitoring

### 1. Structured Logging

```python
import json
import logging
from datetime import datetime

# Custom JSON formatter
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'function_name': record.funcName,
            'line': record.lineno
        }
        if hasattr(record, 'user_id'):
            log_obj['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_obj['request_id'] = record.request_id
        return json.dumps(log_obj)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
for handler in logger.handlers:
    handler.setFormatter(JSONFormatter())

def lambda_handler(event, context):
    logger.info("Processing request", extra={
        'user_id': event.get('user_id'),
        'request_id': context.request_id
    })
    # Processing logic
```

### 2. Custom CloudWatch Metrics

```python
import boto3
from datetime import datetime

cloudwatch = boto3.client('cloudwatch')

def put_metric(metric_name, value, unit='Count', dimensions=None):
    """Publish custom metric to CloudWatch"""
    cloudwatch.put_metric_data(
        Namespace='MyApplication',
        MetricData=[{
            'MetricName': metric_name,
            'Value': value,
            'Unit': unit,
            'Timestamp': datetime.utcnow(),
            'Dimensions': dimensions or []
        }]
    )

def lambda_handler(event, context):
    start_time = time.time()

    try:
        result = process_order(event)

        # Success metrics
        put_metric('OrdersProcessed', 1, dimensions=[
            {'Name': 'Environment', 'Value': os.environ['ENVIRONMENT']}
        ])
        put_metric('OrderValue', result['total'], unit='None')

    except Exception as e:
        # Error metrics
        put_metric('OrderErrors', 1, dimensions=[
            {'Name': 'ErrorType', 'Value': type(e).__name__}
        ])
        raise

    finally:
        # Duration metric
        duration = (time.time() - start_time) * 1000
        put_metric('ProcessingDuration', duration, unit='Milliseconds')
```

### 3. X-Ray Tracing

```python
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Patch libraries for automatic tracing
patch_all()

@xray_recorder.capture('process_order')
def process_order(order_data):
    # Add metadata to trace
    xray_recorder.put_metadata('order_id', order_data['id'])
    xray_recorder.put_annotation('customer_type', order_data['customer_type'])

    # Subsegments for detailed tracing
    with xray_recorder.capture('validate_order'):
        validate(order_data)

    with xray_recorder.capture('save_order'):
        save_to_db(order_data)

    return {'status': 'success'}

def lambda_handler(event, context):
    return process_order(event)
```

## Cost Optimization

### 1. Right-Sizing Memory

```python
# Add logging to track actual memory usage
import os

def lambda_handler(event, context):
    logger.info(f"Memory allocated: {context.memory_limit_in_mb} MB")

    # Process request
    result = process(event)

    # Log actual memory used (check CloudWatch REPORT logs)
    return result

# CloudWatch Insights query to find optimal memory
"""
fields @memorySize, @maxMemoryUsed, @billedDuration
| filter @type = "REPORT"
| stats
    max(@maxMemoryUsed) as maxMemory,
    avg(@maxMemoryUsed) as avgMemory,
    avg(@billedDuration) as avgDuration
  by @memorySize
| sort avgDuration desc
"""
```

### 2. Reduce Package Size

```bash
# Use Lambda Layers for common dependencies
# layer/python/lib/python3.9/site-packages/
pip install -t layer/python/lib/python3.9/site-packages requests boto3

# Exclude unnecessary files
cd layer
zip -r layer.zip . -x "*.pyc" "**/__pycache__/*" "*.dist-info/*"

# Use slim Docker images for container-based Lambda
FROM public.ecr.aws/lambda/python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
COPY app.py ${LAMBDA_TASK_ROOT}
CMD ["app.lambda_handler"]
```

### 3. Use Reserved Concurrency Carefully

```python
# Reserve concurrency only when necessary
# Costs: Provisioned concurrency charges + invocation charges
# Benefits: Eliminates cold starts

# Consider:
# - Do you need guaranteed availability?
# - Can you tolerate occasional cold starts?
# - Is the cost justified?

# Alternative: Use Application Auto Scaling
resource "aws_appautoscaling_target" "lambda_target" {
  max_capacity       = 100
  min_capacity       = 10
  resource_id        = "function:${aws_lambda_function.func.function_name}:provisioned"
  scalable_dimension = "lambda:function:ProvisionedConcurrentExecutions"
  service_namespace  = "lambda"
}
```

## Lambda Limits and Quotas

### Hard Limits (Cannot be Changed)
- **Deployment package size**: 50 MB (zipped), 250 MB (unzipped)
- **Container image size**: 10 GB
- **Execution timeout**: 15 minutes maximum
- **Environment variables**: 4 KB total
- **Temp disk (/tmp)**: 512 MB - 10 GB (configurable)
- **File descriptors**: 1,024
- **Execution processes/threads**: 1,024
- **Request/response payload**: 6 MB (synchronous), 256 KB (async)

### Soft Limits (Can Request Increase)
- **Concurrent executions**: 1,000 per region (default)
- **Function and layer storage**: 75 GB per region
- **Elastic network interfaces per VPC**: 250

### Best Practices for Limits
```python
# 1. For large payloads, use S3
import boto3
import json

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Instead of passing large data in event
    # Store in S3 and pass reference
    if 'data_s3_key' in event:
        obj = s3.get_object(Bucket='my-bucket', Key=event['data_s3_key'])
        data = json.loads(obj['Body'].read())
    else:
        data = event['data']

    # Process data
    result = process(data)

    # Return S3 reference for large results
    if len(json.dumps(result)) > 5 * 1024 * 1024:  # > 5 MB
        result_key = f"results/{context.request_id}.json"
        s3.put_object(
            Bucket='my-bucket',
            Key=result_key,
            Body=json.dumps(result)
        )
        return {'result_s3_key': result_key}

    return result
```

This comprehensive reference covers Lambda best practices for production-grade serverless applications. Apply these patterns to build reliable, performant, and cost-effective Lambda functions.
