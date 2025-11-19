# API Rate Limiting Strategies

## Table of Contents

1. [Overview](#overview)
2. [Token Bucket Algorithm](#token-bucket-algorithm)
3. [Leaky Bucket Algorithm](#leaky-bucket-algorithm)
4. [Fixed Window Counter](#fixed-window-counter)
5. [Sliding Window Log](#sliding-window-log)
6. [Sliding Window Counter](#sliding-window-counter)
7. [Implementation Comparison](#implementation-comparison)
8. [Production Implementations](#production-implementations)
9. [Best Practices](#best-practices)

---

## Overview

Rate limiting controls the number of requests a client can make to an API within a specific time period. It prevents abuse, ensures fair resource allocation, and protects infrastructure from overload.

### Key Objectives

1. **Prevent abuse** - Block excessive requests from single clients
2. **Ensure fairness** - Distribute resources equitably
3. **Protect infrastructure** - Prevent cascading failures
4. **Improve performance** - Reduce server load

### Rate Limiting Dimensions

```
+-------------------+
|  Rate Limiting    |
+-------------------+
        |
    +---+---+---+---+
    |   |   |   |   |
    v   v   v   v   v
  User API  IP  API  Custom
  Level Key Level Method Level
```

---

## Token Bucket Algorithm

The Token Bucket algorithm is the most widely used rate limiting strategy.

### How It Works

```
┌─────────────────────────────┐
│     Token Bucket (size=10)  │
│  Tokens: ●●●●●●●●●●        │
└─────────────────────────────┘
            │
            ├─ Add 1 token/sec
            ├─ Max 10 tokens
            └─ Each request costs 1 token

TIME 0:00   Tokens: 10 ✓ Request allowed  (9 remaining)
TIME 0:01   Tokens: 6  ✓ Request allowed  (5 remaining)
TIME 0:02   Tokens: 0  ✗ Request rejected (wait for tokens)
TIME 0:03   Tokens: 1  ✓ Request allowed  (0 remaining)
TIME 0:04   Tokens: 1  ✓ Request allowed  (0 remaining)
TIME 0:05   Tokens: 1  ✓ Request allowed  (0 remaining)
```

### Algorithm Mechanics

```
1. Tokens = min(Tokens + rate × (now - lastRefill), capacity)
2. lastRefill = now
3. If Tokens >= costOfRequest:
     Tokens -= costOfRequest
     Allow request
   Else:
     Reject request
```

### Implementation (Python)

```python
import time
from threading import Lock

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        """
        capacity: Maximum tokens in bucket
        refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = Lock()

    def _refill(self):
        """Add tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill

        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def allow_request(self, tokens_required=1):
        """Check if request should be allowed"""
        with self.lock:
            self._refill()

            if self.tokens >= tokens_required:
                self.tokens -= tokens_required
                return True, self.tokens

        return False, self.tokens

    def get_retry_after(self, tokens_required=1):
        """Calculate seconds until request would be allowed"""
        with self.lock:
            self._refill()
            deficit = tokens_required - self.tokens
            return deficit / self.refill_rate if deficit > 0 else 0


# Example usage
limiter = TokenBucket(capacity=10, refill_rate=2)  # 10 token capacity, 2 tokens/second

for i in range(5):
    allowed, remaining = limiter.allow_request()
    if allowed:
        print(f"Request {i+1}: Allowed. Remaining tokens: {remaining}")
    else:
        retry_after = limiter.get_retry_after()
        print(f"Request {i+1}: Denied. Retry after {retry_after:.2f}s")
```

### Distributed Token Bucket with Redis

```python
import redis
import time
import math

class DistributedTokenBucket:
    def __init__(self, client_id, capacity, refill_rate, redis_client):
        self.client_id = client_id
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.redis = redis_client
        self.bucket_key = f"rate_limit:bucket:{client_id}"
        self.last_refill_key = f"rate_limit:last_refill:{client_id}"

    def allow_request(self, tokens_required=1):
        """Atomic rate limit check using Lua script"""

        script = """
        local bucket_key = KEYS[1]
        local last_refill_key = KEYS[2]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local tokens_required = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])

        -- Get current state
        local tokens = tonumber(redis.call('GET', bucket_key)) or capacity
        local last_refill = tonumber(redis.call('GET', last_refill_key)) or now

        -- Calculate tokens to add
        local elapsed = math.max(0, now - last_refill)
        local tokens_to_add = elapsed * refill_rate
        tokens = math.min(capacity, tokens + tokens_to_add)

        -- Update last refill time
        redis.call('SET', last_refill_key, now)

        -- Check if request allowed
        if tokens >= tokens_required then
            tokens = tokens - tokens_required
            redis.call('SET', bucket_key, tokens)
            redis.call('EXPIRE', bucket_key, 3600)
            return {1, tokens}
        else
            return {0, tokens}
        end
        """

        result = self.redis.eval(
            script,
            2,
            self.bucket_key,
            self.last_refill_key,
            self.capacity,
            self.refill_rate,
            tokens_required,
            time.time()
        )

        return bool(result[0]), result[1]


# Flask integration
from flask import request, jsonify

@app.before_request
def rate_limit_check():
    client_id = get_client_id(request)  # From API key or IP
    limiter = DistributedTokenBucket(
        client_id,
        capacity=100,
        refill_rate=10,  # 10 tokens/second
        redis_client=redis_client
    )

    allowed, remaining = limiter.allow_request()

    g.rate_limit_remaining = remaining

    if not allowed:
        return jsonify({'error': 'Rate limit exceeded'}), 429

@app.after_request
def add_rate_limit_headers(response):
    if hasattr(g, 'rate_limit_remaining'):
        response.headers['X-RateLimit-Remaining'] = str(int(g.rate_limit_remaining))
    return response
```

### Advantages

- Allows burst traffic up to capacity
- Smooth rate limiting with consistent refill
- Works well with varying request sizes
- Industry standard (used by AWS, Google Cloud)

### Disadvantages

- Requires tracking per-client state
- Allows bursts which could overwhelm backend
- More complex than fixed window

---

## Leaky Bucket Algorithm

The Leaky Bucket algorithm processes requests at a constant rate, discarding excess requests.

### How It Works

```
        INCOMING REQUESTS
               │
               ↓
        ┌──────────────┐
        │ Leaky Bucket │
        │  (capacity=5)│
        │ Processing:  │
        │ 1 req/sec    │
        └──────────────┘
               │
               ↓
         OUTGOING RESPONSES
         (constant rate)
```

### Algorithm Mechanics

```
1. Queue request if bucket not full
2. Process queued requests at constant rate
3. Drop requests if bucket is full
```

### Implementation

```python
import time
from collections import deque
from threading import Lock

class LeakyBucket:
    def __init__(self, capacity, leak_rate):
        """
        capacity: Maximum queued requests
        leak_rate: Requests processed per second
        """
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.queue = deque()
        self.last_leak = time.time()
        self.lock = Lock()

    def _leak(self):
        """Process queued requests at constant rate"""
        now = time.time()
        elapsed = now - self.last_leak

        requests_to_process = elapsed * self.leak_rate
        processed = 0

        while self.queue and processed < requests_to_process:
            self.queue.popleft()
            processed += 1

        self.last_leak = now
        return len(self.queue)

    def allow_request(self):
        """Try to add request to queue"""
        with self.lock:
            queue_size = self._leak()

            if len(self.queue) < self.capacity:
                self.queue.append(time.time())
                return True

            return False

    def queue_length(self):
        """Current queue size"""
        with self.lock:
            return len(self.queue)


# Example usage
bucket = LeakyBucket(capacity=10, leak_rate=2)  # Process 2 requests/second

for i in range(15):
    if bucket.allow_request():
        print(f"Request {i+1}: Accepted. Queue size: {bucket.queue_length()}")
    else:
        print(f"Request {i+1}: Rejected. Bucket full.")
    time.sleep(0.3)
```

### Advantages

- Smooth, predictable output rate
- Prevents traffic bursts from overwhelming backend
- Simple to understand conceptually
- Guaranteed processing time

### Disadvantages

- Requests in queue may experience unpredictable delay
- High latency during burst traffic
- Doesn't utilize server capacity during idle periods
- Not ideal for handling traffic spikes

---

## Fixed Window Counter

Simple counter-based approach using fixed time windows.

### How It Works

```
TIME: 00:00-00:59        01:00-01:59        02:00-02:59
      ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
      │  Window 1    │  │  Window 2    │  │  Window 3    │
      │ Count: 45/100│  │ Count: 52/100│  │ Count: 23/100│
      └──────────────┘  └──────────────┘  └──────────────┘

Request arrives at 00:58:50
→ Add to current window (Window 1)
→ Check: 45/100 allowed ✓

Request arrives at 01:00:05
→ New window starts (Window 2)
→ Counter resets
→ Check: 1/100 allowed ✓
```

### Algorithm

```
1. Get current time window
2. Get request count for current window
3. If count < limit:
     Increment count
     Allow request
   Else:
     Reject request
```

### Implementation

```python
import time
from threading import Lock

class FixedWindowCounter:
    def __init__(self, window_size_seconds, limit):
        """
        window_size_seconds: Duration of each window
        limit: Max requests per window
        """
        self.window_size = window_size_seconds
        self.limit = limit
        self.current_window = None
        self.request_count = 0
        self.lock = Lock()

    def allow_request(self):
        """Check if request is within limit"""
        with self.lock:
            now = int(time.time())
            current_window = now // self.window_size

            # New window started, reset counter
            if current_window != self.current_window:
                self.current_window = current_window
                self.request_count = 0

            if self.request_count < self.limit:
                self.request_count += 1
                return True

            return False

    def get_reset_time(self):
        """Get unix timestamp when counter resets"""
        with self.lock:
            if self.current_window is None:
                return time.time()
            return (self.current_window + 1) * self.window_size


# Redis implementation
import redis

class RedisFixedWindowCounter:
    def __init__(self, client_id, window_size, limit, redis_client):
        self.client_id = client_id
        self.window_size = window_size
        self.limit = limit
        self.redis = redis_client
        self.key = f"rate_limit:fixed:{client_id}"

    def allow_request(self):
        """Atomic fixed window check"""
        script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window_size = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])

        local current_window = math.floor(now / window_size)
        local window_key = key .. ":" .. current_window

        local count = tonumber(redis.call('GET', window_key)) or 0

        if count < limit then
            redis.call('INCR', window_key)
            redis.call('EXPIRE', window_key, window_size + 1)
            return 1
        else
            return 0
        end
        """

        result = self.redis.eval(
            script,
            1,
            self.key,
            self.limit,
            self.window_size,
            time.time()
        )

        return bool(result)
```

### Problem: Boundary Burst

```
Window 1: [00:00-00:59]     Window 2: [01:00-01:59]
Limit: 100 requests         Limit: 100 requests

00:59:50 - 100 requests sent ✓
00:59:55 - Request denied (limit reached)
01:00:00 - 100 more requests sent ✓
         - 200 requests in 10 seconds! ⚠️
```

### Advantages

- Simple to implement
- Low memory footprint
- Easy to understand

### Disadvantages

- **Boundary burst problem** - Allows double burst at window boundaries
- No protection against concentrated traffic bursts
- Inflexible rate limiting

---

## Sliding Window Log

Records timestamps of all requests in a time window.

### How It Works

```
Current time: 01:03:30
Window: Last 60 seconds [01:02:30 - 01:03:30]

Timestamps in window:
01:02:35  ●
01:02:40  ●
01:02:45  ●
01:03:10  ●
01:03:15  ●
01:03:20  ●
01:03:25  ●

Count: 7/10 ✓ Request allowed

Outside window (discarded):
01:02:20  ✗ (before window start)
```

### Algorithm

```
1. Get current timestamp
2. Remove all timestamps older than window start
3. Count remaining timestamps
4. If count < limit:
     Add current timestamp
     Allow request
   Else:
     Reject request
```

### Implementation

```python
import time
from collections import deque
from threading import Lock

class SlidingWindowLog:
    def __init__(self, window_size_seconds, limit):
        self.window_size = window_size_seconds
        self.limit = limit
        self.request_log = deque()
        self.lock = Lock()

    def allow_request(self):
        """Check using sliding window log"""
        with self.lock:
            now = time.time()
            window_start = now - self.window_size

            # Remove old requests outside the window
            while self.request_log and self.request_log[0] < window_start:
                self.request_log.popleft()

            # Check if under limit
            if len(self.request_log) < self.limit:
                self.request_log.append(now)
                return True

            return False


# Redis implementation with sorted set
import redis

class RedisSlidingWindowLog:
    def __init__(self, client_id, window_size, limit, redis_client):
        self.client_id = client_id
        self.window_size = window_size
        self.limit = limit
        self.redis = redis_client
        self.key = f"rate_limit:sliding_log:{client_id}"

    def allow_request(self):
        """Atomic sliding window check using sorted set"""
        script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window_size = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])

        local window_start = now - window_size

        -- Remove old entries outside window
        redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)

        -- Count entries in window
        local count = redis.call('ZCARD', key)

        if count < limit then
            -- Add current request
            redis.call('ZADD', key, now, now)
            redis.call('EXPIRE', key, window_size + 1)
            return 1
        else
            return 0
        end
        """

        result = self.redis.eval(
            script,
            1,
            self.key,
            self.limit,
            self.window_size,
            time.time()
        )

        return bool(result)
```

### Advantages

- Accurate rate limiting
- No boundary burst problem
- Precise per-request tracking
- Easy to debug (can see all requests)

### Disadvantages

- High memory usage (stores all timestamps)
- Doesn't scale to millions of requests
- Overkill for most applications

---

## Sliding Window Counter

Hybrid approach combining fixed windows with sliding window smoothing.

### How It Works

```
Current time: 01:03:30

Previous window [01:02:00-01:03:00]  Current window [01:03:00-01:04:00]
     Requests: 60                         Requests: 35
          ↓                                    ↓
    ┌─────────────────────────────────────────────────┐
    │                    60 seconds                    │
    └─────────────────────────────────────────────────┘
              ↑
         01:03:30
         (30 seconds into current window)

Rolling window request count:
= (60 × (60-30)/60) + 35
= (60 × 0.5) + 35
= 30 + 35
= 65 requests in last 60 seconds
```

### Algorithm

```
1. Get previous window count and current window count
2. elapsed_percentage = (now - window_start) / window_size
3. estimated_count = previous_count × (1 - elapsed_percentage) + current_count
4. If estimated_count < limit:
     Increment current window count
     Allow request
   Else:
     Reject request
```

### Implementation

```python
import time
from threading import Lock

class SlidingWindowCounter:
    def __init__(self, window_size_seconds, limit):
        self.window_size = window_size_seconds
        self.limit = limit
        self.current_window_start = int(time.time())
        self.current_window_count = 0
        self.previous_window_count = 0
        self.lock = Lock()

    def allow_request(self):
        """Check using sliding window counter"""
        with self.lock:
            now = time.time()
            current_window_start = int(now / self.window_size) * self.window_size

            # Check if we've moved to a new window
            if current_window_start != self.current_window_start:
                self.previous_window_count = self.current_window_count
                self.current_window_count = 0
                self.current_window_start = current_window_start

            # Calculate elapsed time as fraction of window
            elapsed_percentage = (now - self.current_window_start) / self.window_size

            # Estimate rolling window count
            rolling_count = (
                self.previous_window_count * (1 - elapsed_percentage) +
                self.current_window_count
            )

            # Check limit
            if rolling_count < self.limit:
                self.current_window_count += 1
                return True

            return False


# Redis implementation
import redis

class RedisSlidingWindowCounter:
    def __init__(self, client_id, window_size, limit, redis_client):
        self.client_id = client_id
        self.window_size = window_size
        self.limit = limit
        self.redis = redis_client

    def allow_request(self):
        """Atomic sliding window counter"""
        script = """
        local limit = tonumber(ARGV[1])
        local window_size = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])

        local current_window = math.floor(now / window_size)
        local previous_window = current_window - 1

        local current_key = KEYS[1] .. ":" .. current_window
        local previous_key = KEYS[1] .. ":" .. previous_window

        local current_count = tonumber(redis.call('GET', current_key)) or 0
        local previous_count = tonumber(redis.call('GET', previous_key)) or 0

        local window_start = current_window * window_size
        local elapsed_percentage = (now - window_start) / window_size

        local rolling_count = previous_count * (1 - elapsed_percentage) + current_count

        if rolling_count < limit then
            redis.call('INCR', current_key)
            redis.call('EXPIRE', current_key, window_size + 1)
            return 1
        else
            return 0
        end
        """

        result = self.redis.eval(
            script,
            1,
            f"rate_limit:sliding:{self.client_id}",
            self.limit,
            self.window_size,
            time.time()
        )

        return bool(result)
```

### Advantages

- Prevents boundary burst
- More accurate than fixed window
- Lower memory than sliding window log
- Good balance of accuracy and efficiency

### Disadvantages

- Slightly more complex
- Approximate (not exact) count
- Estimation at window boundaries

---

## Implementation Comparison

### Performance Characteristics

| Algorithm | Memory | CPU | Accuracy | Burst Protection |
|-----------|--------|-----|----------|------------------|
| **Token Bucket** | Low | Low | High | Allows burst |
| **Leaky Bucket** | Low | Medium | High | Prevents burst |
| **Fixed Window** | Very Low | Very Low | Low | Poor |
| **Sliding Window Log** | High | Low | Very High | Excellent |
| **Sliding Window Counter** | Very Low | Medium | High | Good |

### Use Cases

```
Token Bucket
├─ AWS API rate limiting
├─ Google Cloud APIs
├─ General-purpose rate limiting
└─ When you want to allow bursts

Leaky Bucket
├─ Stable output requirements
├─ Network traffic shaping
├─ Load balancing
└─ When burst protection needed

Fixed Window
├─ Simple monitoring
├─ Quota tracking
├─ Not recommended for critical systems
└─ Easy to understand

Sliding Window Log
├─ High-accuracy billing
├─ Security monitoring
├─ Detailed request tracking
└─ When you need exact counts

Sliding Window Counter
├─ Most production systems
├─ Stripe-like rate limiting
├─ Distributed systems
└─ Best balance of simplicity/accuracy
```

---

## Production Implementations

### Stripe's Approach

Stripe uses a hybrid approach with per-customer and per-endpoint limits:

```python
# Simplified version of Stripe's model
class StripeRateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client

    def check_rate_limit(self, customer_id, endpoint, method):
        """Multi-dimensional rate limiting"""

        limits = {
            ('create', 'charges'): 100,      # 100 creates/min
            ('read', 'charges'): 500,        # 500 reads/min
            ('write', 'subscriptions'): 50,  # 50 writes/min
            ('read', 'subscriptions'): 200   # 200 reads/min
        }

        key = f"rate:{customer_id}:{endpoint}:{method}"
        limit = limits.get((method, endpoint), 100)

        script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])

        local count = redis.call('GET', key)
        if not count then
            redis.call('SET', key, 1)
            redis.call('EXPIRE', key, window)
            return 1
        end

        count = tonumber(count) + 1
        if count <= limit then
            redis.call('SET', key, count)
            return 1
        else
            return 0
        end
        """

        result = self.redis.eval(script, 1, key, limit, 60, time.time())
        return bool(result)
```

### Twilio's Approach

Twilio uses token bucket with per-account rate limits:

```
Account Rate Limits:
├─ REST API: 200 requests/second
├─ Voice API: 100 concurrent calls
├─ SMS API: 1 message/second per phone number
└─ Messaging API: 100 messages/second
```

### GitHub API Rate Limiting

GitHub uses a complex system with multiple limits:

```
Primary Rate Limit:
├─ Authenticated: 5000 requests/hour
├─ Unauthenticated: 60 requests/hour
└─ Search API: 30 requests/minute

Custom Rate Limits:
├─ Search API reduces on high load
├─ GraphQL has cost-based limits
└─ Different limits for different endpoints

Headers Returned:
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4999
X-RateLimit-Used: 1
X-RateLimit-Reset: 1372700873
```

---

## Best Practices

### 1. Provide Clear Headers

```python
@app.after_request
def add_rate_limit_headers(response):
    """Include rate limit info in response"""
    response.headers['X-RateLimit-Limit'] = '1000'
    response.headers['X-RateLimit-Remaining'] = str(remaining_requests)
    response.headers['X-RateLimit-Reset'] = str(reset_timestamp)
    response.headers['Retry-After'] = str(retry_seconds)
    return response
```

### 2. Graduated Response

```python
def get_rate_limit_behavior(utilization):
    """Graduated response based on utilization"""

    if utilization < 0.8:
        return 'allow'           # Full speed
    elif utilization < 0.95:
        return 'allow_with_warning'  # Warn client
    else:
        return 'reject'          # Hard reject
```

### 3. Different Limits per Tier

```python
RATE_LIMITS = {
    'free': {
        'requests_per_minute': 10,
        'monthly_quota': 10000
    },
    'pro': {
        'requests_per_minute': 1000,
        'monthly_quota': 1000000
    },
    'enterprise': {
        'requests_per_minute': None,  # Unlimited
        'monthly_quota': None
    }
}
```

### 4. Quota Tracking

```python
def track_quota_usage(user_id, cost):
    """Track monthly quota with daily breakdown"""

    current_month = datetime.utcnow().strftime('%Y-%m')
    quota_key = f"quota:{user_id}:{current_month}"
    daily_key = f"quota:daily:{user_id}:{current_date()}"

    pipe = redis.pipeline()
    pipe.incr(quota_key, cost)
    pipe.incr(daily_key, cost)
    pipe.expire(quota_key, 30 * 24 * 60 * 60)
    pipe.expire(daily_key, 24 * 60 * 60)
    pipe.execute()
```

### 5. Monitoring and Alerting

```python
def monitor_rate_limits():
    """Alert on rate limit abuse"""

    # Check for high rejection rates
    total_requests = redis.get('stats:total_requests')
    rejected_requests = redis.get('stats:rejected_requests')

    if total_requests:
        rejection_rate = rejected_requests / total_requests
        if rejection_rate > 0.1:  # >10% rejection
            send_alert('High rate limit rejection rate')

    # Check for specific users hitting limits frequently
    for user in get_top_rejected_users(limit=10):
        send_alert(f"User {user} frequently hitting rate limits")
```

---

## Response Codes and Headers

### Standard HTTP Status Codes

```
200 OK                - Request succeeded
429 Too Many Requests - Rate limit exceeded
503 Service Unavailable - Server throttling
```

### Standard Headers

```
X-RateLimit-Limit       - Total allowed requests
X-RateLimit-Remaining   - Requests remaining in window
X-RateLimit-Reset       - Unix timestamp when limit resets
X-RateLimit-Used        - Requests used in current window
Retry-After             - Seconds to wait before retrying
```

### Example Response

```json
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Used: 1000
X-RateLimit-Reset: 1640275260
Retry-After: 3600

{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the rate limit of 1000 requests per hour",
  "retry_after": 3600
}
```

---

## References

- [Token Bucket Algorithm](https://en.wikipedia.org/wiki/Token_bucket)
- [Leaky Bucket Algorithm](https://en.wikipedia.org/wiki/Leaky_bucket)
- [API Rate Limiting (AWS)](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-request-throttling.html)
- [GitHub API Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
- [Stripe Rate Limiting](https://stripe.com/docs/rate-limiting)
