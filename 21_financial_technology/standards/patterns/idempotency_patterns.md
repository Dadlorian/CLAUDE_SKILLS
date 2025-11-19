# Idempotency Patterns in Financial Systems

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Implementation Strategies](#implementation-strategies)
4. [Request Deduplication](#request-deduplication)
5. [Result Caching](#result-caching)
6. [State Tracking](#state-tracking)
7. [Real-World Examples](#real-world-examples)
8. [Best Practices](#best-practices)

## Overview

Idempotency is the property that a request can be applied multiple times with the same result. In financial systems, idempotency prevents duplicate charges, double-debit entries, and other critical errors.

### Why Idempotency Matters

```
Without Idempotency:
┌─────────────────┐
│ POST /charge    │
│ amount: $100    │
└────────┬────────┘
         │
         ├─► Charge $100 (Success, but timeout)
         │
         ├─► Client retries
         │
         └─► Charge $100 again (DUPLICATE!)

Result: Customer charged $200 instead of $100

With Idempotency:
┌─────────────────┐
│ POST /charge    │
│ idempotency_key │
│ amount: $100    │
└────────┬────────┘
         │
         ├─► Check cache: not found
         │
         ├─► Execute: Charge $100
         │
         ├─► Cache result with key
         │
         ├─► Client retries
         │
         └─► Check cache: found!
             Return cached result

Result: Customer charged $100 (correct)
```

## Core Concepts

### Idempotency Key

An idempotency key is a unique identifier for a request that allows the server to recognize duplicate requests.

```python
from dataclasses import dataclass
from typing import Optional
import uuid
from datetime import datetime, timedelta

@dataclass
class IdempotencyKey:
    key: str
    request_hash: str  # Hash of request parameters
    created_at: datetime
    expires_at: datetime = None
    status: str = "processing"  # processing, completed, failed

    def __post_init__(self):
        if not self.expires_at:
            # Default: 24 hours
            self.expires_at = datetime.utcnow() + timedelta(hours=24)

    @staticmethod
    def generate() -> str:
        """Generate idempotency key"""
        return str(uuid.uuid4())

    def is_expired(self) -> bool:
        """Check if key has expired"""
        return datetime.utcnow() > self.expires_at

class IdempotencyKeyValidator:
    """Validate idempotency keys"""

    def __init__(self, database):
        self.db = database

    def validate_format(self, key: str) -> bool:
        """Check if key has valid format"""
        try:
            # Try parsing as UUID
            uuid.UUID(key)
            return True
        except ValueError:
            # Or alphanumeric string
            return key.isalnum() and len(key) >= 20

    def hash_request(self, method: str, path: str, body: dict) -> str:
        """Hash request for duplicate detection"""
        import hashlib
        import json

        content = f"{method}:{path}:{json.dumps(body, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()
```

## Implementation Strategies

### Strategy 1: Request Log Pattern

Store all requests with their results:

```
Request: POST /transfer
idempotency_key: abc-123
status: PENDING

↓ Process

idempotency_key: abc-123
status: COMPLETED
result: transfer_id=xyz, amount=$100

Retry: POST /transfer
idempotency_key: abc-123
↓ Lookup
Found! Return previous result

Result: Same transfer_id=xyz, amount=$100
```

**Code Example**:

```python
from datetime import datetime
import json

class RequestLogStore:
    """Store request logs for idempotency"""

    def __init__(self, database):
        self.db = database
        self._initialize_schema()

    def _initialize_schema(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS idempotency_requests (
                idempotency_key TEXT PRIMARY KEY,
                request_hash TEXT NOT NULL,
                method TEXT NOT NULL,
                path TEXT NOT NULL,
                request_body JSONB,
                response_status TEXT NOT NULL,
                response_body JSONB,
                response_code INTEGER,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                processed_at TIMESTAMP
            );

            CREATE INDEX idx_expires_at ON idempotency_requests(expires_at);
            CREATE INDEX idx_created_at ON idempotency_requests(created_at);
        ''')

    def store_request(self, key: str, request_hash: str,
                     method: str, path: str, body: dict) -> bool:
        """Store incoming request"""
        try:
            expires_at = datetime.utcnow() + timedelta(hours=24)

            self.db.execute('''
                INSERT INTO idempotency_requests (
                    idempotency_key, request_hash, method, path,
                    request_body, response_status, expires_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                key,
                request_hash,
                method,
                path,
                json.dumps(body),
                'PENDING',
                expires_at
            ))

            return True
        except Exception as e:
            raise Exception(f"Failed to store request: {str(e)}")

    def store_response(self, key: str, status: str, response: dict,
                      code: int = 200, error: str = None) -> bool:
        """Store response for completed request"""
        try:
            self.db.execute('''
                UPDATE idempotency_requests
                SET response_status = %s,
                    response_body = %s,
                    response_code = %s,
                    error_message = %s,
                    processed_at = CURRENT_TIMESTAMP
                WHERE idempotency_key = %s
            ''', (
                status,
                json.dumps(response),
                code,
                error,
                key
            ))

            return True
        except Exception as e:
            raise Exception(f"Failed to store response: {str(e)}")

    def get_request_result(self, key: str) -> Optional[dict]:
        """Get stored result if request was processed"""
        result = self.db.query('''
            SELECT response_status, response_body, response_code, error_message
            FROM idempotency_requests
            WHERE idempotency_key = %s
            AND expires_at > NOW()
        ''', (key,))

        return result[0] if result else None

    def cleanup_expired(self) -> int:
        """Remove expired idempotency records"""
        self.db.execute('''
            DELETE FROM idempotency_requests
            WHERE expires_at < NOW()
        ''')

        return self.db.rowcount
```

### Strategy 2: Deduplication with State Machine

Track request states through processing:

```python
class RequestDeduplicationEngine:
    """Prevent duplicate processing of requests"""

    def __init__(self, request_log_store: RequestLogStore, cache):
        self.request_log = request_log_store
        self.cache = cache

    async def process_request_idempotent(self, key: str, processor_fn,
                                        *args, **kwargs):
        """Process request with idempotency guarantee"""

        # Check cache first (fastest)
        cached_result = self.cache.get(f"idempotent:{key}")
        if cached_result:
            return cached_result

        # Check database
        stored_result = self.request_log.get_request_result(key)
        if stored_result:
            if stored_result['response_status'] == 'COMPLETED':
                return {
                    'status': stored_result['response_code'],
                    'body': json.loads(stored_result['response_body'])
                }
            elif stored_result['response_status'] == 'PROCESSING':
                # Still processing - return 202 Accepted
                return {
                    'status': 202,
                    'body': {'status': 'processing', 'idempotency_key': key}
                }
            elif stored_result['response_status'] == 'FAILED':
                return {
                    'status': stored_result['response_code'],
                    'error': stored_result['error_message']
                }

        # Store request as PENDING
        request_hash = self.request_log.hash_request(
            kwargs.get('method', 'POST'),
            kwargs.get('path', '/'),
            kwargs.get('body', {})
        )

        self.request_log.store_request(
            key,
            request_hash,
            kwargs.get('method', 'POST'),
            kwargs.get('path', '/'),
            kwargs.get('body', {})
        )

        try:
            # Execute processor
            result = await processor_fn(*args, **kwargs)

            # Store successful response
            self.request_log.store_response(
                key,
                'COMPLETED',
                result,
                code=200
            )

            # Cache result
            self.cache.set(f"idempotent:{key}", result, ttl=86400)

            return {
                'status': 200,
                'body': result
            }

        except Exception as e:
            # Store failed response
            self.request_log.store_response(
                key,
                'FAILED',
                {},
                code=400,
                error=str(e)
            )

            raise
```

### Strategy 3: Natural Idempotency with Entity Identifiers

Instead of checking for duplicates, generate deterministic identifiers:

```python
import hashlib

class DeterministicIDGenerator:
    """Generate same ID for same input"""

    @staticmethod
    def generate_transfer_id(source: str, target: str,
                            amount: float, timestamp: str) -> str:
        """Generate deterministic ID for transfer"""

        # Create deterministic hash from input
        content = f"{source}:{target}:{amount}:{timestamp}"
        hash_value = hashlib.md5(content.encode()).hexdigest()

        return f"transfer_{hash_value[:16]}"

    @staticmethod
    def generate_charge_id(customer: str, amount: float,
                          timestamp: str, merchant: str) -> str:
        """Generate deterministic ID for charge"""

        content = f"{customer}:{amount}:{timestamp}:{merchant}"
        hash_value = hashlib.sha256(content.encode()).hexdigest()

        return f"charge_{hash_value[:16]}"

class NaturalIdempotencyService:
    """Use natural keys for idempotency"""

    def __init__(self, database):
        self.db = database

    def create_charge(self, customer_id: str, amount: float,
                     merchant_id: str, timestamp: str) -> dict:
        """Create charge with natural idempotency"""

        # Generate deterministic ID
        charge_id = DeterministicIDGenerator.generate_charge_id(
            customer_id,
            amount,
            timestamp,
            merchant_id
        )

        # Try to create
        try:
            result = self.db.execute('''
                INSERT INTO charges (
                    charge_id, customer_id, amount, merchant_id, timestamp
                )
                VALUES (%s, %s, %s, %s, %s)
            ''', (charge_id, customer_id, amount, merchant_id, timestamp))

            return {
                'charge_id': charge_id,
                'status': 'created',
                'amount': amount
            }

        except IntegrityError:
            # Already exists - return existing charge
            existing = self.db.query('''
                SELECT * FROM charges WHERE charge_id = %s
            ''', (charge_id,))

            return {
                'charge_id': charge_id,
                'status': 'already_exists',
                'amount': existing[0]['amount']
            }
```

## Request Deduplication

### Deduplication Cache

```python
from functools import wraps
from typing import Callable
import hashlib

class IdempotencyCacheManager:
    """Manage idempotency cache"""

    def __init__(self, redis_client, ttl_seconds: int = 86400):
        self.redis = redis_client
        self.ttl = ttl_seconds

    def idempotent(self, ttl_override: int = None):
        """Decorator for idempotent endpoints"""

        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(self_arg, request, *args, **kwargs):
                # Extract idempotency key from request
                idempotency_key = request.headers.get('Idempotency-Key')

                if not idempotency_key:
                    # No idempotency key provided
                    return await func(self_arg, request, *args, **kwargs)

                # Create cache key
                cache_key = f"idempotent:{idempotency_key}"

                # Check cache
                cached_response = self.redis.get(cache_key)
                if cached_response:
                    return json.loads(cached_response)

                # Execute function
                result = await func(self_arg, request, *args, **kwargs)

                # Cache result
                ttl = ttl_override or self.ttl
                self.redis.setex(
                    cache_key,
                    ttl,
                    json.dumps(result)
                )

                return result

            return wrapper
        return decorator

# Usage
cache_manager = IdempotencyCacheManager(redis_client)

class PaymentAPI:
    @cache_manager.idempotent(ttl_override=3600)
    async def create_payment(self, request):
        """Create payment with idempotency"""
        amount = request.json['amount']
        customer = request.json['customer_id']

        # Process payment
        payment = await self.payment_service.process(amount, customer)

        return {
            'payment_id': payment.id,
            'status': 'created',
            'amount': amount
        }
```

## Result Caching

### Smart Cache Invalidation

```python
class SmartIdempotencyCache:
    """Cache with smart invalidation"""

    def __init__(self, database, redis_client):
        self.db = database
        self.redis = redis_client

    def cache_result(self, idempotency_key: str, operation_type: str,
                     result: dict, ttl: int = 86400):
        """Cache result with metadata"""

        cache_entry = {
            'operation_type': operation_type,
            'result': result,
            'timestamp': datetime.utcnow().isoformat(),
            'ttl': ttl
        }

        # Store in Redis
        self.redis.setex(
            f"idempotent:{idempotency_key}",
            ttl,
            json.dumps(cache_entry)
        )

        # Store in database
        self.db.execute('''
            INSERT INTO idempotency_cache (
                key, operation_type, result, expires_at
            )
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP + INTERVAL '1 second' * %s)
        ''', (
            idempotency_key,
            operation_type,
            json.dumps(result),
            ttl
        ))

    def get_cached_result(self, idempotency_key: str):
        """Get cached result"""

        # Try Redis first
        cached = self.redis.get(f"idempotent:{idempotency_key}")
        if cached:
            return json.loads(cached)

        # Fall back to database
        result = self.db.query('''
            SELECT result FROM idempotency_cache
            WHERE key = %s
            AND expires_at > NOW()
        ''', (idempotency_key,))

        return json.loads(result[0]['result']) if result else None

    def invalidate_related(self, customer_id: str, operation_type: str):
        """Invalidate related cache entries"""
        self.redis.delete_pattern(f"idempotent:*{customer_id}*")

        self.db.execute('''
            DELETE FROM idempotency_cache
            WHERE operation_type = %s
        ''', (operation_type,))
```

## State Tracking

### Idempotency State Tracking

```python
class IdempotencyStateTracker:
    """Track state of idempotent operations"""

    def __init__(self, database):
        self.db = database
        self._initialize_schema()

    def _initialize_schema(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS idempotency_states (
                idempotency_key TEXT PRIMARY KEY,
                operation_id TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                result JSONB
            );

            CREATE INDEX idx_operation_id ON idempotency_states(operation_id);
            CREATE INDEX idx_state ON idempotency_states(state);
        ''')

    def create_state(self, idempotency_key: str, operation_id: str) -> bool:
        """Create new idempotency state"""
        try:
            self.db.execute('''
                INSERT INTO idempotency_states (
                    idempotency_key, operation_id, state
                )
                VALUES (%s, %s, %s)
            ''', (
                idempotency_key,
                operation_id,
                'PENDING'
            ))
            return True
        except IntegrityError:
            # Already exists
            return False

    def update_state(self, idempotency_key: str, state: str,
                    result: dict = None) -> bool:
        """Update operation state"""
        query = '''
            UPDATE idempotency_states
            SET state = %s, updated_at = CURRENT_TIMESTAMP
        '''
        params = [state, idempotency_key]

        if state == 'COMPLETED':
            query += ', completed_at = CURRENT_TIMESTAMP, result = %s'
            params = [state, json.dumps(result) if result else None, idempotency_key]

        query += ' WHERE idempotency_key = %s'

        self.db.execute(query, params)
        return True

    def get_state(self, idempotency_key: str) -> Optional[dict]:
        """Get current state of operation"""
        result = self.db.query('''
            SELECT * FROM idempotency_states
            WHERE idempotency_key = %s
        ''', (idempotency_key,))

        return result[0] if result else None
```

## Real-World Examples

### Example 1: Stripe-Style Idempotency

```python
class StripeStyleIdempotency:
    """Implement Stripe's idempotency approach"""

    def __init__(self, request_store: RequestLogStore):
        self.request_store = request_store

    async def create_payment_intent(self, idempotency_key: str,
                                   amount: float, currency: str):
        """Create payment intent with Stripe idempotency"""

        # Check if already processed
        existing = self.request_store.get_request_result(idempotency_key)

        if existing:
            if existing['response_status'] == 'COMPLETED':
                return json.loads(existing['response_body'])

        # Create new intent
        intent_id = str(uuid.uuid4())[:20]

        result = {
            'id': intent_id,
            'amount': int(amount * 100),  # Cents
            'currency': currency,
            'status': 'succeeded',
            'created': datetime.utcnow().isoformat()
        }

        # Store for idempotency
        self.request_store.store_response(
            idempotency_key,
            'COMPLETED',
            result
        )

        return result
```

### Example 2: Square-Style Idempotency

```python
class SquareStyleIdempotency:
    """Implement Square's idempotency approach"""

    def __init__(self, database):
        self.db = database

    async def create_payment(self, idempotency_key: str,
                            source_id: str, amount: int):
        """Create payment with Square idempotency"""

        # Square uses idempotency key + automatic deduplication
        try:
            # Try to create payment
            payment = {
                'id': f"payment_{uuid.uuid4().hex[:16]}",
                'source_id': source_id,
                'amount_money': {
                    'amount': amount,
                    'currency': 'USD'
                },
                'status': 'COMPLETED',
                'receipt_number': uuid.uuid4().hex[:12],
                'created_at': datetime.utcnow().isoformat()
            }

            # Store with idempotency key
            self.db.execute('''
                INSERT INTO payments (
                    idempotency_key, payment_id, source_id, amount, data
                )
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                idempotency_key,
                payment['id'],
                source_id,
                amount,
                json.dumps(payment)
            ))

            return payment

        except IntegrityError:
            # Payment already exists for this key
            existing = self.db.query('''
                SELECT data FROM payments WHERE idempotency_key = %s
            ''', (idempotency_key,))

            return json.loads(existing[0]['data'])
```

## Best Practices

### 1. Idempotency Key Lifecycle

```python
class IdempotencyKeyLifecycle:
    """Manage idempotency key lifecycle"""

    def __init__(self, database, cache):
        self.db = database
        self.cache = cache

    def generate_with_validation(self, request_headers: dict) -> str:
        """Generate or validate idempotency key"""

        # Check if client provided key
        provided_key = request_headers.get('Idempotency-Key')

        if provided_key:
            # Validate format
            if len(provided_key) < 20:
                raise ValueError("Idempotency key too short")
            if not self._is_valid_format(provided_key):
                raise ValueError("Invalid idempotency key format")
            return provided_key

        # Generate new key
        return str(uuid.uuid4())

    def _is_valid_format(self, key: str) -> bool:
        """Check idempotency key format"""
        return key.isalnum() or key.count('-') <= 4

    def extend_ttl(self, idempotency_key: str, extension_seconds: int = 3600):
        """Extend idempotency key expiration"""

        # Check if operation is complete
        state = self.db.query('''
            SELECT state FROM idempotency_states
            WHERE idempotency_key = %s
        ''', (idempotency_key,))

        if state and state[0]['state'] == 'COMPLETED':
            # Extend TTL
            self.cache.expire(f"idempotent:{idempotency_key}", extension_seconds)

    def cleanup_expired(self, batch_size: int = 1000):
        """Cleanup expired idempotency records"""

        # Delete from database
        self.db.execute('''
            DELETE FROM idempotency_states
            WHERE completed_at < NOW() - INTERVAL '24 hours'
            LIMIT %s
        ''', (batch_size,))

        # Clear from cache automatically (via TTL)
```

### 2. Monitoring Idempotency

```python
class IdempotencyMonitoring:
    """Monitor idempotency system"""

    def __init__(self, database):
        self.db = database

    def get_idempotency_stats(self, time_window_hours: int = 24) -> dict:
        """Get idempotency statistics"""

        stats = self.db.query(f'''
            SELECT
                COUNT(*) as total_requests,
                SUM(CASE WHEN created_at > NOW() - INTERVAL '{time_window_hours} hours'
                    THEN 1 ELSE 0 END) as recent_requests,
                COUNT(DISTINCT idempotency_key) as unique_keys,
                SUM(CASE WHEN response_status = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN response_status = 'FAILED' THEN 1 ELSE 0 END) as failed
            FROM idempotency_requests
        '''[0])

        return {
            'total_requests': stats['total_requests'],
            'recent_requests': stats['recent_requests'],
            'unique_keys': stats['unique_keys'],
            'completed': stats['completed'],
            'failed': stats['failed'],
            'failure_rate': (
                stats['failed'] / stats['completed']
                if stats['completed'] > 0 else 0
            )
        }
```

## Conclusion

Idempotency patterns provide:

1. **Request deduplication** to prevent duplicate processing
2. **Result caching** for fast retry responses
3. **State tracking** for monitoring operations
4. **Deterministic IDs** as an alternative approach
5. **Natural idempotency** by design

Combine these patterns based on your requirements:
- **High throughput**: Use caching
- **Complex operations**: Use state tracking
- **Financial accuracy**: Use request logs and natural IDs
