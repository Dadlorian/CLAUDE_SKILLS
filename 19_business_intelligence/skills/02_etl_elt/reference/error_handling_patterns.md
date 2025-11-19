# Error Handling Patterns Reference

## Retry Strategies

### Exponential Backoff
```python
# Airflow task with retry logic
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import timedelta

default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(hours=1),
}

def risky_operation(**context):
    """Operation that might fail transiently"""
    try:
        # Your logic here
        extract_data_from_api()
    except APIRateLimitError:
        # Will retry with backoff: 5min, 10min, 20min
        raise
    except PermanentError:
        # Don't retry permanent errors
        context['task_instance'].skip()
```

### Custom Retry Logic
```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60):
    """
    Decorator for retry logic with exponential backoff
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        raise

                    delay = min(base_delay * (2 ** retries), max_delay)
                    print(f"Retry {retries}/{max_retries} after {delay}s: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry_with_backoff(max_retries=5, base_delay=2)
def fetch_data_from_api(endpoint):
    response = requests.get(endpoint)
    response.raise_for_status()
    return response.json()
```

## Dead Letter Queues

### SQL Pattern
```sql
-- Failed records table
CREATE TABLE etl.failed_records (
    id SERIAL PRIMARY KEY,
    source_table VARCHAR(255),
    source_record_id VARCHAR(255),
    record_data JSONB,
    error_message TEXT,
    error_type VARCHAR(100),
    failed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    resolved_at TIMESTAMP
);

-- Capture failed records
INSERT INTO etl.failed_records (
    source_table,
    source_record_id,
    record_data,
    error_message,
    error_type
)
SELECT
    'orders' as source_table,
    id::VARCHAR,
    to_jsonb(orders.*) as record_data,
    validation_error as error_message,
    'validation_failed' as error_type
FROM staging.orders
WHERE validation_status = 'FAILED';

-- Process DLQ with fixes
WITH fixed_records AS (
    SELECT
        id,
        jsonb_set(
            record_data,
            '{amount}',
            to_jsonb(COALESCE((record_data->>'amount')::DECIMAL, 0))
        ) as fixed_data
    FROM etl.failed_records
    WHERE source_table = 'orders'
      AND error_type = 'null_amount'
      AND resolved_at IS NULL
)
INSERT INTO analytics.orders
SELECT (fixed_data->>'id')::BIGINT, ...
FROM fixed_records;

-- Mark as resolved
UPDATE etl.failed_records
SET resolved_at = CURRENT_TIMESTAMP
WHERE id IN (SELECT id FROM fixed_records);
```

### Python DLQ Handler
```python
from typing import Dict, Any
import json
from datetime import datetime

class DeadLetterQueue:
    """Handle failed records"""

    def __init__(self, table_name: str, db_conn):
        self.table_name = table_name
        self.db_conn = db_conn

    def send_to_dlq(
        self,
        record: Dict[str, Any],
        error: Exception,
        source_table: str,
        record_id: str
    ):
        """Store failed record"""
        self.db_conn.execute("""
            INSERT INTO etl.failed_records
            (source_table, source_record_id, record_data, error_message, error_type)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            source_table,
            record_id,
            json.dumps(record),
            str(error),
            type(error).__name__
        ))

    def retry_failed_records(self, max_retries: int = 3):
        """Retry processing failed records"""
        failed_records = self.db_conn.execute("""
            SELECT id, source_table, record_data
            FROM etl.failed_records
            WHERE resolved_at IS NULL
              AND retry_count < %s
            ORDER BY failed_at ASC
            LIMIT 100
        """, (max_retries,))

        for record_id, source_table, record_data in failed_records:
            try:
                # Retry processing
                self.process_record(json.loads(record_data))

                # Mark as resolved
                self.db_conn.execute("""
                    UPDATE etl.failed_records
                    SET resolved_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (record_id,))

            except Exception as e:
                # Increment retry count
                self.db_conn.execute("""
                    UPDATE etl.failed_records
                    SET retry_count = retry_count + 1,
                        error_message = %s
                    WHERE id = %s
                """, (str(e), record_id))
```

## Circuit Breaker Pattern

### Implementation
```python
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """
    Prevent cascading failures by stopping requests to failing service
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: timedelta = timedelta(minutes=1),
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if datetime.now() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)

            # Success - reset if was in half-open
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0

            return result

        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

            raise

# Usage
api_circuit = CircuitBreaker(failure_threshold=5, timeout=timedelta(minutes=2))

def fetch_data():
    return api_circuit.call(requests.get, 'https://api.example.com/data')
```

## Validation & Data Quality Checks

### Pydantic Validation
```python
from pydantic import BaseModel, Field, validator, ValidationError
from typing import Optional, List
from datetime import date
from decimal import Decimal

class OrderRecord(BaseModel):
    """Validate order records before loading"""

    order_id: int = Field(..., gt=0)
    customer_id: int = Field(..., gt=0)
    order_date: date
    amount: Decimal = Field(..., ge=0, le=1000000)
    status: str
    items: List[dict]

    @validator('status')
    def validate_status(cls, v):
        allowed = ['pending', 'processing', 'completed', 'cancelled']
        if v not in allowed:
            raise ValueError(f'Status must be one of {allowed}')
        return v

    @validator('order_date')
    def validate_date_not_future(cls, v):
        if v > date.today():
            raise ValueError('Order date cannot be in the future')
        return v

    @validator('items')
    def validate_items_not_empty(cls, v):
        if not v:
            raise ValueError('Order must have at least one item')
        return v

# Process with validation
validated_records = []
failed_records = []

for raw_record in raw_data:
    try:
        validated = OrderRecord(**raw_record)
        validated_records.append(validated.dict())
    except ValidationError as e:
        failed_records.append({
            'record': raw_record,
            'errors': e.errors()
        })

# Load valid records
load_to_warehouse(validated_records)

# Send failed to DLQ
for failure in failed_records:
    dlq.send_to_dlq(failure['record'], failure['errors'], 'orders', ...)
```

### SQL Validation Checks
```sql
-- Pre-load validation view
CREATE VIEW etl.orders_validation AS
WITH validation_checks AS (
    SELECT
        id,
        -- Required field checks
        CASE WHEN order_id IS NULL THEN 'Missing order_id' END as check_order_id,
        CASE WHEN customer_id IS NULL THEN 'Missing customer_id' END as check_customer_id,

        -- Range checks
        CASE WHEN amount < 0 THEN 'Negative amount' END as check_amount_positive,
        CASE WHEN amount > 1000000 THEN 'Amount exceeds limit' END as check_amount_limit,

        -- Format checks
        CASE
            WHEN email IS NOT NULL
             AND email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
            THEN 'Invalid email format'
        END as check_email_format,

        -- Business logic checks
        CASE
            WHEN order_date > CURRENT_DATE
            THEN 'Future order date'
        END as check_order_date,

        CASE
            WHEN ship_date < order_date
            THEN 'Ship date before order date'
        END as check_ship_date

    FROM staging.orders
),
errors_combined AS (
    SELECT
        id,
        ARRAY_REMOVE(ARRAY[
            check_order_id,
            check_customer_id,
            check_amount_positive,
            check_amount_limit,
            check_email_format,
            check_order_date,
            check_ship_date
        ], NULL) as validation_errors
    FROM validation_checks
)
SELECT
    id,
    validation_errors,
    ARRAY_LENGTH(validation_errors, 1) as error_count,
    CASE
        WHEN ARRAY_LENGTH(validation_errors, 1) IS NULL THEN 'PASS'
        ELSE 'FAIL'
    END as validation_status
FROM errors_combined;

-- Only load valid records
INSERT INTO analytics.orders
SELECT * FROM staging.orders
WHERE id IN (
    SELECT id FROM etl.orders_validation WHERE validation_status = 'PASS'
);

-- Send failures to DLQ
INSERT INTO etl.failed_records (...)
SELECT id, validation_errors, ...
FROM staging.orders o
JOIN etl.orders_validation v ON o.id = v.id
WHERE v.validation_status = 'FAIL';
```

## Graceful Degradation

### Fallback Strategy
```python
def get_exchange_rate(date: str, from_currency: str, to_currency: str) -> float:
    """
    Get exchange rate with fallback sources
    """
    # Try primary API
    try:
        return primary_api.get_rate(date, from_currency, to_currency)
    except APIError as e:
        logger.warning(f"Primary API failed: {e}")

    # Fallback to secondary API
    try:
        return secondary_api.get_rate(date, from_currency, to_currency)
    except APIError as e:
        logger.warning(f"Secondary API failed: {e}")

    # Fallback to database cache
    try:
        cached_rate = db.get_cached_rate(date, from_currency, to_currency)
        if cached_rate:
            logger.info(f"Using cached rate from {cached_rate.cached_at}")
            return cached_rate.rate
    except Exception as e:
        logger.error(f"Cache lookup failed: {e}")

    # Last resort: use default rate
    logger.error(f"All sources failed, using default rate")
    return DEFAULT_EXCHANGE_RATES.get((from_currency, to_currency), 1.0)
```

### Partial Success Pattern
```python
def process_batch(records: List[dict]) -> dict:
    """
    Process batch, allowing partial success
    """
    results = {
        'success': [],
        'failed': [],
        'skipped': []
    }

    for record in records:
        try:
            # Validate
            validated_record = validate_record(record)

            # Transform
            transformed_record = transform_record(validated_record)

            # Load
            load_record(transformed_record)

            results['success'].append(record['id'])

        except ValidationError as e:
            logger.warning(f"Validation failed for {record['id']}: {e}")
            results['failed'].append({
                'id': record['id'],
                'error': str(e),
                'type': 'validation'
            })

        except TransformError as e:
            logger.error(f"Transform failed for {record['id']}: {e}")
            results['failed'].append({
                'id': record['id'],
                'error': str(e),
                'type': 'transform'
            })

        except Exception as e:
            logger.error(f"Unexpected error for {record['id']}: {e}")
            results['skipped'].append(record['id'])

    # Report results
    logger.info(f"Processed: {len(results['success'])} success, "
                f"{len(results['failed'])} failed, "
                f"{len(results['skipped'])} skipped")

    # Fail the job only if ALL records failed
    if len(results['success']) == 0:
        raise Exception("All records failed processing")

    return results
```

## Alerting & Notifications

### Airflow Callbacks
```python
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

def task_failure_alert(context):
    """Send alert on task failure"""
    task_instance = context['task_instance']
    exception = context.get('exception')

    slack_msg = f"""
    :red_circle: Task Failed
    *Task*: {task_instance.task_id}
    *DAG*: {task_instance.dag_id}
    *Execution Time*: {context['execution_date']}
    *Error*: {exception}
    *Log*: {task_instance.log_url}
    """

    failed_alert = SlackWebhookOperator(
        task_id='slack_failure',
        http_conn_id='slack_webhook',
        message=slack_msg,
        channel='#data-alerts'
    )
    return failed_alert.execute(context=context)

def dag_sla_miss_alert(dag, task_list, blocking_task_list, slas, blocking_tis):
    """Send alert on SLA miss"""
    message = f"""
    :warning: SLA Missed
    *DAG*: {dag.dag_id}
    *Tasks*: {', '.join([task.task_id for task in task_list])}
    """
    # Send to PagerDuty for critical DAGs
    if dag.dag_id in CRITICAL_DAGS:
        send_to_pagerduty(message)

# DAG configuration
default_args = {
    'on_failure_callback': task_failure_alert,
    'sla_miss_callback': dag_sla_miss_alert,
    'sla': timedelta(hours=2),
}
```

### dbt Error Handling
```python
# run_dbt_with_alerts.py
import subprocess
import json
from slack_sdk import WebClient

def run_dbt_with_error_handling():
    """Run dbt and handle errors"""

    # Run dbt
    result = subprocess.run(
        ['dbt', 'run', '--target', 'prod'],
        capture_output=True,
        text=True
    )

    # Parse results
    run_results = json.load(open('target/run_results.json'))

    failures = [
        r for r in run_results['results']
        if r['status'] == 'error'
    ]

    if failures:
        error_msg = "dbt run failed:\n"
        for failure in failures:
            error_msg += f"- {failure['unique_id']}: {failure['message']}\n"

        # Alert team
        slack = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
        slack.chat_postMessage(
            channel='#data-alerts',
            text=error_msg
        )

        # Fail the pipeline
        raise Exception(f"{len(failures)} dbt models failed")

    return run_results
```

## Transaction Management

### Database Transactions
```python
from contextlib import contextmanager

@contextmanager
def transaction(conn):
    """Context manager for database transactions"""
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Transaction rolled back: {e}")
        raise
    finally:
        conn.close()

# Usage
with transaction(db.connection()) as conn:
    # All-or-nothing operations
    conn.execute("DELETE FROM staging.orders WHERE date = %s", (process_date,))
    conn.execute("INSERT INTO staging.orders SELECT * FROM raw.orders WHERE date = %s", (process_date,))
    conn.execute("INSERT INTO analytics.orders SELECT * FROM staging.orders WHERE date = %s", (process_date,))
```

### Idempotent Operations
```sql
-- Delete and reload pattern (idempotent)
BEGIN;

-- Delete existing data for date range
DELETE FROM analytics.daily_sales
WHERE sale_date BETWEEN '{{ params.start_date }}' AND '{{ params.end_date }}';

-- Insert fresh data
INSERT INTO analytics.daily_sales
SELECT
    DATE(order_timestamp) as sale_date,
    product_id,
    SUM(quantity) as total_quantity,
    SUM(amount) as total_amount
FROM staging.orders
WHERE DATE(order_timestamp) BETWEEN '{{ params.start_date }}' AND '{{ params.end_date }}'
GROUP BY 1, 2;

COMMIT;

-- Safe to run multiple times for same date range
```

## Error Logging

### Structured Logging
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """JSON structured logging for better parsing"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log(self, level: str, message: str, **kwargs):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            **kwargs
        }
        self.logger.log(
            getattr(logging, level.upper()),
            json.dumps(log_entry)
        )

# Usage
logger = StructuredLogger('etl_pipeline')

logger.log('info', 'Starting extraction',
           source='postgres',
           table='orders',
           batch_size=1000)

logger.log('error', 'Validation failed',
           record_id=12345,
           error_type='InvalidAmount',
           error_details='Amount cannot be negative')
```

### Audit Trail
```sql
-- Track all ETL operations
CREATE TABLE etl.audit_log (
    id SERIAL PRIMARY KEY,
    pipeline_name VARCHAR(255),
    operation VARCHAR(50),  -- extract, transform, load
    source_table VARCHAR(255),
    target_table VARCHAR(255),
    rows_affected BIGINT,
    execution_time_seconds DECIMAL(10, 2),
    status VARCHAR(20),  -- success, failed, partial
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB
);

-- Log operations
INSERT INTO etl.audit_log (
    pipeline_name,
    operation,
    source_table,
    target_table,
    rows_affected,
    execution_time_seconds,
    status,
    started_at,
    completed_at,
    metadata
)
VALUES (
    'daily_orders_etl',
    'load',
    'staging.orders',
    'analytics.orders',
    15000,
    45.5,
    'success',
    '2024-01-15 10:00:00',
    '2024-01-15 10:00:45',
    '{"batch_date": "2024-01-15", "mode": "incremental"}'::jsonb
);
```

## Resources

- **Airflow Error Handling**: https://airflow.apache.org/docs/apache-airflow/stable/concepts/tasks.html#error-handling
- **dbt Test Failures**: https://docs.getdbt.com/reference/commands/test
- **Circuit Breaker Pattern**: https://martinfowler.com/bliki/CircuitBreaker.html
- **Dead Letter Queue**: https://aws.amazon.com/what-is/dead-letter-queue/
