# Logging Reference

## Overview

Logs are time-stamped records of discrete events that occurred within a system. They provide detailed context for debugging, auditing, and understanding system behavior.

## Log Levels

### Standard Levels (Most to Least Severe)

#### FATAL/CRITICAL
- **Purpose**: System is unusable, immediate action required
- **Examples**: Database connection lost, out of memory
- **Action**: Page on-call engineer immediately
- **Color**: Red

#### ERROR
- **Purpose**: Significant problem, operation failed
- **Examples**: Failed to process payment, API call failed
- **Action**: Create ticket, investigate soon
- **Color**: Red

#### WARN/WARNING
- **Purpose**: Unexpected but handled, potential issue
- **Examples**: Deprecated API used, slow query, retry succeeded
- **Action**: Review periodically, may indicate future problems
- **Color**: Yellow

#### INFO
- **Purpose**: Normal significant events, business logic flow
- **Examples**: User logged in, order created, service started
- **Action**: General awareness, business analytics
- **Color**: Green/Blue

#### DEBUG
- **Purpose**: Detailed diagnostic information
- **Examples**: Variable values, execution flow, function calls
- **Action**: Used during development and troubleshooting
- **Color**: Gray

#### TRACE
- **Purpose**: Very detailed diagnostic information
- **Examples**: Loop iterations, detailed state changes
- **Action**: Extremely verbose, typically disabled in production
- **Color**: Gray

### Level Selection Guidelines

```python
# Good examples
logger.info(f"User {user_id} successfully authenticated")
logger.warning(f"API rate limit at 80% for user {user_id}")
logger.error(f"Failed to send email to {email}: {error}")
logger.fatal(f"Cannot connect to database after 10 retries")

# Bad examples - wrong level
logger.error("User clicked button")  # Should be DEBUG
logger.info("Database connection failed")  # Should be ERROR
logger.debug("Payment failed for $1000 order")  # Should be ERROR
```

## Structured Logging

### JSON Format (Recommended)

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "service": "payment-api",
  "version": "1.2.3",
  "environment": "production",
  "message": "Payment processed successfully",
  "context": {
    "user_id": "user_12345",
    "order_id": "order_67890",
    "amount": 99.99,
    "currency": "USD",
    "payment_method": "credit_card"
  },
  "trace_id": "abc123def456",
  "span_id": "span789",
  "duration_ms": 245,
  "http": {
    "method": "POST",
    "path": "/api/v1/payments",
    "status": 200,
    "user_agent": "Mobile/iOS/14.5"
  }
}
```

### Key Fields

#### Required Fields
- **timestamp**: ISO 8601 format with milliseconds/microseconds
- **level**: Log severity level
- **message**: Human-readable description
- **service**: Service name producing the log

#### Recommended Fields
- **version**: Application version
- **environment**: prod, staging, dev
- **host**: Hostname or container ID
- **trace_id**: Distributed trace ID
- **span_id**: Current span ID
- **user_id**: User context (if applicable)
- **request_id**: Unique request identifier

#### Optional Fields
- **duration_ms**: Operation duration
- **error**: Error object with stack trace
- **http**: HTTP request/response details
- **db**: Database query details
- **labels/tags**: Additional metadata

### Language Examples

#### Python (structlog)
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "payment_processed",
    user_id="user_12345",
    order_id="order_67890",
    amount=99.99,
    currency="USD",
    duration_ms=245
)
```

#### Go (zap)
```go
import "go.uber.org/zap"

logger, _ := zap.NewProduction()
defer logger.Sync()

logger.Info("payment processed",
    zap.String("user_id", "user_12345"),
    zap.String("order_id", "order_67890"),
    zap.Float64("amount", 99.99),
    zap.String("currency", "USD"),
    zap.Int("duration_ms", 245),
)
```

#### Node.js (pino)
```javascript
const pino = require('pino');
const logger = pino();

logger.info({
  user_id: 'user_12345',
  order_id: 'order_67890',
  amount: 99.99,
  currency: 'USD',
  duration_ms: 245
}, 'payment processed');
```

#### Java (Logback with JSON)
```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import net.logstash.logback.argument.StructuredArguments.*;

Logger logger = LoggerFactory.getLogger(PaymentService.class);

logger.info("payment processed",
    keyValue("user_id", "user_12345"),
    keyValue("order_id", "order_67890"),
    keyValue("amount", 99.99),
    keyValue("currency", "USD")
);
```

## Context Enrichment

### Automatic Context

```python
# Bind context at logger creation
logger = logger.bind(
    service="payment-api",
    version="1.2.3",
    environment="production",
    host=socket.gethostname()
)

# All subsequent logs include this context
logger.info("payment_processed", order_id="12345")
# Output includes service, version, environment, host automatically
```

### Request Context

```python
# Add request-scoped context
def process_request(request):
    request_logger = logger.bind(
        request_id=request.id,
        user_id=request.user_id,
        trace_id=request.headers.get('X-Trace-Id')
    )

    request_logger.info("request_started")
    # ... process request ...
    request_logger.info("request_completed", status=200)
```

### Correlation IDs

```python
# Trace ID for distributed tracing
trace_id = generate_trace_id()

# Pass in headers
response = requests.post(
    url,
    headers={'X-Trace-Id': trace_id}
)

# Log with trace ID
logger.info("api_call_made", trace_id=trace_id, url=url)
```

## Log Patterns

### Request/Response Logging

```python
@app.before_request
def log_request():
    g.start_time = time.time()
    logger.info(
        "request_started",
        method=request.method,
        path=request.path,
        remote_addr=request.remote_addr
    )

@app.after_request
def log_response(response):
    duration_ms = (time.time() - g.start_time) * 1000
    logger.info(
        "request_completed",
        method=request.method,
        path=request.path,
        status=response.status_code,
        duration_ms=duration_ms
    )
    return response
```

### Error Logging

```python
try:
    result = process_payment(order)
    logger.info("payment_processed", order_id=order.id, amount=order.amount)
except PaymentException as e:
    logger.error(
        "payment_failed",
        order_id=order.id,
        amount=order.amount,
        error=str(e),
        error_type=type(e).__name__,
        exc_info=True  # Include stack trace
    )
    raise
```

### Performance Logging

```python
import time

class LogExecutionTime:
    def __init__(self, operation_name):
        self.operation_name = operation_name

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        logger.info(
            "operation_completed",
            operation=self.operation_name,
            duration_ms=duration_ms
        )

# Usage
with LogExecutionTime("database_query"):
    results = db.execute(query)
```

### Security/Audit Logging

```python
def log_security_event(event_type, user_id, details):
    logger.warning(
        "security_event",
        event_type=event_type,
        user_id=user_id,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        details=details,
        severity="security"
    )

# Examples
log_security_event("failed_login", user_id, {"attempts": 3})
log_security_event("permission_denied", user_id, {"resource": "/admin"})
log_security_event("password_changed", user_id, {})
```

## Log Aggregation Patterns

### Centralized Logging Flow

```
Application → Log Shipper → Aggregator → Storage → Visualization
   (JSON)    (Fluentd/FB)   (Logstash)   (ES/Loki)  (Kibana/Grafana)
```

### Common Patterns

#### Pattern 1: ELK Stack
```
App → Filebeat → Logstash → Elasticsearch → Kibana
```

#### Pattern 2: EFK Stack
```
App → Fluentd → Elasticsearch → Kibana
```

#### Pattern 3: Grafana Loki
```
App → Promtail → Loki → Grafana
```

#### Pattern 4: Cloud Native
```
App → CloudWatch Logs → CloudWatch Insights
App → Cloud Logging → Log Explorer
```

## Sampling and Rate Limiting

### Log Sampling

```python
import random

class SampledLogger:
    def __init__(self, logger, sample_rate=0.1):
        self.logger = logger
        self.sample_rate = sample_rate

    def debug(self, msg, **kwargs):
        if random.random() < self.sample_rate:
            self.logger.debug(msg, sampled=True, **kwargs)

# Log only 10% of debug messages
sampled_logger = SampledLogger(logger, sample_rate=0.1)
```

### Rate Limiting

```python
from collections import defaultdict
import time

class RateLimitedLogger:
    def __init__(self, logger, max_per_second=10):
        self.logger = logger
        self.max_per_second = max_per_second
        self.message_counts = defaultdict(list)

    def log(self, level, msg, **kwargs):
        now = time.time()
        key = f"{level}:{msg}"

        # Remove old timestamps
        self.message_counts[key] = [
            t for t in self.message_counts[key]
            if now - t < 1.0
        ]

        # Check rate limit
        if len(self.message_counts[key]) < self.max_per_second:
            self.message_counts[key].append(now)
            getattr(self.logger, level)(msg, **kwargs)
        else:
            # Log rate limit exceeded (once)
            if len(self.message_counts[key]) == self.max_per_second:
                self.logger.warning(f"Rate limit exceeded for: {msg}")
```

## Best Practices

### Do's

1. **Use structured logging (JSON)**
   ```python
   # Good
   logger.info("user_login", user_id=123, ip="1.2.3.4")

   # Bad
   logger.info(f"User 123 logged in from 1.2.3.4")
   ```

2. **Include correlation IDs**
   ```python
   logger.info("payment_started", trace_id=trace_id, user_id=user_id)
   ```

3. **Log at appropriate levels**
   ```python
   logger.info("normal_operation")
   logger.warning("degraded_performance")
   logger.error("operation_failed")
   ```

4. **Add context, not just messages**
   ```python
   # Good
   logger.error("payment_failed", user_id=123, amount=99.99, reason="card_declined")

   # Bad
   logger.error("Payment failed")
   ```

5. **Use consistent field names**
   ```python
   # Consistent across all services
   user_id, order_id, request_id, trace_id
   ```

### Don'ts

1. **Don't log sensitive data**
   ```python
   # Bad - logs PII
   logger.info(f"Password: {password}, SSN: {ssn}, Card: {card_number}")

   # Good - sanitize
   logger.info("user_authenticated", user_id=user_id)
   ```

2. **Don't log at too high volume**
   ```python
   # Bad - logs on every loop iteration
   for item in million_items:
       logger.debug(f"Processing {item}")

   # Good - log summary
   logger.info("batch_processing_started", count=len(million_items))
   # ... process ...
   logger.info("batch_processing_completed", processed=count, failed=failed_count)
   ```

3. **Don't use string interpolation**
   ```python
   # Bad - expensive even if level disabled
   logger.debug(f"Complex calculation: {expensive_function()}")

   # Good - lazy evaluation
   logger.debug("complex_calculation", result=lambda: expensive_function())
   ```

4. **Don't mix log formats**
   ```python
   # Bad - inconsistent format
   logger.info("User login")  # Plain text
   logger.info(json.dumps({"event": "user_login"}))  # JSON string

   # Good - consistent structured logging
   logger.info("user_login", user_id=123)
   ```

## Log Retention

### Retention Policies

```yaml
# Example retention policy
log_retention:
  error_logs: 90_days
  warn_logs: 30_days
  info_logs: 7_days
  debug_logs: 1_day

  # By service
  payment_service: 1_year  # Compliance requirement
  analytics_service: 7_days

  # By environment
  production: 90_days
  staging: 7_days
  development: 1_day
```

### Cost Optimization

```python
# Hot vs Cold storage strategy
if log_level in ['ERROR', 'FATAL']:
    send_to_hot_storage(log)  # Fast, expensive (Elasticsearch)
    send_to_cold_storage(log)  # Slow, cheap (S3)
elif log_level == 'WARN':
    send_to_hot_storage(log) if recent else send_to_cold_storage(log)
else:
    send_to_cold_storage(log)  # Keep INFO/DEBUG in cheap storage
```

## Performance Considerations

### Async Logging

```python
import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

# Create queue and handlers
log_queue = Queue()
queue_handler = QueueHandler(log_queue)

# Configure logger
logger = logging.getLogger()
logger.addHandler(queue_handler)

# Start listener in background thread
file_handler = logging.FileHandler('app.log')
listener = QueueListener(log_queue, file_handler)
listener.start()
```

### Buffering

```python
# Buffer logs and flush periodically
class BufferedLogger:
    def __init__(self, logger, buffer_size=100):
        self.logger = logger
        self.buffer = []
        self.buffer_size = buffer_size

    def log(self, level, msg, **kwargs):
        self.buffer.append((level, msg, kwargs))
        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def flush(self):
        for level, msg, kwargs in self.buffer:
            getattr(self.logger, level)(msg, **kwargs)
        self.buffer.clear()
```

## Common Log Queries

### Elasticsearch

```json
// Find all errors for a user
{
  "query": {
    "bool": {
      "must": [
        {"term": {"level": "ERROR"}},
        {"term": {"user_id": "user_12345"}},
        {"range": {"timestamp": {"gte": "now-1h"}}}
      ]
    }
  }
}

// Aggregate error counts by service
{
  "aggs": {
    "errors_by_service": {
      "terms": {"field": "service"},
      "aggs": {
        "error_count": {"value_count": {"field": "level"}}
      }
    }
  }
}
```

### LogQL (Loki)

```logql
// All errors from payment service
{service="payment-api"} |= "level=ERROR"

// Count of errors per minute
sum(rate({service="payment-api"} |= "level=ERROR" [1m]))

// Extract and count error types
{service="payment-api"}
  | json
  | level="ERROR"
  | count_over_time([5m]) by (error_type)
```

## Anti-Patterns to Avoid

1. **Logging in loops**
2. **No log levels** (everything is INFO)
3. **String concatenation** in log messages
4. **Logging passwords/secrets**
5. **Too verbose** (logging everything)
6. **Too sparse** (not enough context)
7. **Inconsistent formats** across services
8. **No correlation IDs**
9. **Logging exceptions** without stack traces
10. **Logging to multiple destinations** (slow)

## Tools and Platforms

### Open Source
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Grafana Loki
- Fluentd / Fluent Bit
- Graylog
- Apache Flume

### Commercial
- Splunk
- Datadog Logs
- New Relic Logs
- Sumo Logic
- Loggly

### Cloud Native
- AWS CloudWatch Logs
- Azure Monitor Logs
- Google Cloud Logging
- Papertrail
