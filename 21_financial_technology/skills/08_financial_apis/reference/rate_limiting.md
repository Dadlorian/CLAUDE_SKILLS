# Rate Limiting for Financial APIs

## Rate Limiting Overview

Rate limiting controls API request frequency to prevent abuse and ensure fair resource allocation.

## Rate Limiting Algorithms

### Token Bucket Algorithm
```python
import time
from threading import Lock

class TokenBucket:
    """Token bucket rate limiter"""

    def __init__(self, capacity, refill_rate):
        """
        capacity: max tokens in bucket
        refill_rate: tokens per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = Lock()

    def allow_request(self, tokens_needed=1):
        """Check if request is allowed"""
        with self.lock:
            # Refill tokens based on time passed
            now = time.time()
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * self.refill_rate

            self.tokens = min(
                self.capacity,
                self.tokens + tokens_to_add
            )
            self.last_refill = now

            # Check if enough tokens
            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
                return True

            return False

# Example usage
limiter = TokenBucket(capacity=100, refill_rate=10)  # 100 req burst, 10/sec sustained

if limiter.allow_request():
    # Process request
    pass
else:
    # Return 429 Too Many Requests
    pass
```

### Sliding Window Algorithm
```python
from collections import deque
import time

class SlidingWindow:
    """Sliding window rate limiter"""

    def __init__(self, limit, window_seconds):
        """
        limit: max requests per window
        window_seconds: time window in seconds
        """
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests = deque()

    def allow_request(self):
        """Check if request is allowed"""
        now = time.time()

        # Remove old requests outside window
        while self.requests and self.requests[0] < now - self.window_seconds:
            self.requests.popleft()

        # Check limit
        if len(self.requests) < self.limit:
            self.requests.append(now)
            return True

        return False

# Example usage
limiter = SlidingWindow(limit=100, window_seconds=60)  # 100 req per minute

if limiter.allow_request():
    # Process request
    pass
```

### Fixed Window Algorithm
```python
class FixedWindow:
    """Simple fixed-window rate limiter"""

    def __init__(self, limit, window_seconds):
        self.limit = limit
        self.window_seconds = window_seconds
        self.current_window = int(time.time() / window_seconds)
        self.count = 0

    def allow_request(self):
        """Check if request is allowed"""
        now = time.time()
        window = int(now / self.window_seconds)

        if window != self.current_window:
            # New window, reset counter
            self.current_window = window
            self.count = 0

        if self.count < self.limit:
            self.count += 1
            return True

        return False
```

## Rate Limiting Strategies for Financial APIs

### Per-User Rate Limiting
```python
import redis

class PerUserRateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client

    def get_user_limit(self, user_id, user_tier):
        """Get rate limit based on user tier"""
        limits = {
            "free": {"requests": 100, "window": 3600},      # 100/hour
            "basic": {"requests": 1000, "window": 3600},    # 1000/hour
            "premium": {"requests": 10000, "window": 3600}, # 10000/hour
            "enterprise": {"requests": 100000, "window": 3600}
        }
        return limits.get(user_tier, limits["free"])

    def is_allowed(self, user_id, user_tier):
        """Check if user request is allowed"""
        limit_config = self.get_user_limit(user_id, user_tier)
        key = f"ratelimit:{user_id}"

        # Get current request count
        current = self.redis.incr(key)

        # Set expiration on first request in window
        if current == 1:
            self.redis.expire(key, limit_config["window"])

        # Check against limit
        return current <= limit_config["requests"]

    def get_remaining(self, user_id, user_tier):
        """Get remaining requests"""
        limit_config = self.get_user_limit(user_id, user_tier)
        key = f"ratelimit:{user_id}"

        current = self.redis.get(key)
        current = int(current) if current else 0

        return max(0, limit_config["requests"] - current)
```

### Endpoint-Specific Limits
```python
class EndpointRateLimiter:
    """Different limits per endpoint"""

    LIMITS = {
        "GET /accounts": {"limit": 1000, "window": 3600},
        "GET /accounts/{id}/transactions": {"limit": 500, "window": 3600},
        "POST /payments": {"limit": 100, "window": 3600},
        "GET /payments/{id}/status": {"limit": 10000, "window": 3600}
    }

    def __init__(self, redis_client):
        self.redis = redis_client

    def is_allowed(self, user_id, endpoint):
        """Check endpoint rate limit"""
        if endpoint not in self.LIMITS:
            return True

        limit_config = self.LIMITS[endpoint]
        key = f"endpoint_ratelimit:{user_id}:{endpoint}"

        current = self.redis.incr(key)

        if current == 1:
            self.redis.expire(key, limit_config["window"])

        return current <= limit_config["limit"]
```

### Tiered Burst Limits
```python
class BurstLimiter:
    """Allow burst traffic up to limit"""

    def __init__(self, redis_client):
        self.redis = redis_client

    def check_limits(self, user_id):
        """
        Two-tier limit system:
        - Burst: 100 requests per minute
        - Sustained: 1000 requests per hour
        """
        minute_key = f"burst:{user_id}:minute"
        hour_key = f"sustained:{user_id}:hour"

        # Check burst limit
        minute_count = self.redis.incr(minute_key)
        if minute_count == 1:
            self.redis.expire(minute_key, 60)

        if minute_count > 100:
            return False, "Burst limit exceeded"

        # Check sustained limit
        hour_count = self.redis.incr(hour_key)
        if hour_count == 1:
            self.redis.expire(hour_key, 3600)

        if hour_count > 1000:
            return False, "Hourly limit exceeded"

        return True, None
```

## HTTP Headers for Rate Limiting

### Standard Headers
```
Response Headers:
X-RateLimit-Limit: 1000        (requests per window)
X-RateLimit-Remaining: 234     (requests left)
X-RateLimit-Reset: 1605897600  (Unix timestamp when limit resets)
Retry-After: 3600               (seconds until next attempt)

Example Response when limited:
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1605897600
Retry-After: 3600

{
  "error": "TOO_MANY_REQUESTS",
  "message": "Rate limit exceeded",
  "retry_after": 3600
}
```

## Flask Middleware Implementation

```python
from flask import Flask, request, jsonify, g
from functools import wraps
import time

app = Flask(__name__)

class RateLimitMiddleware:
    def __init__(self, app, limiter):
        self.app = app
        self.limiter = limiter

    def __call__(self, environ, start_response):
        request_obj = request

        # Get user ID from token
        auth_header = request_obj.headers.get("Authorization")
        user_id = self.extract_user_id(auth_header)

        # Check rate limit
        allowed, remaining, reset_time = self.limiter.check_rate_limit(user_id)

        # Store in g for use in route
        g.rate_limit_remaining = remaining
        g.rate_limit_reset = reset_time

        if not allowed:
            # Return 429
            response_body = jsonify({
                "error": "TOO_MANY_REQUESTS",
                "message": "Rate limit exceeded",
                "retry_after": reset_time - time.time()
            }).get_data(as_text=True)

            status = "429 Too Many Requests"
            headers = [
                ("Content-Type", "application/json"),
                ("Retry-After", str(int(reset_time - time.time())))
            ]

            start_response(status, headers)
            return [response_body.encode()]

        # Continue to app
        return self.app(environ, start_response)

    @staticmethod
    def extract_user_id(auth_header):
        """Extract user ID from Bearer token"""
        if not auth_header:
            return "anonymous"

        try:
            token = auth_header.split(" ")[1]
            # Decode token to get user_id
            import jwt
            decoded = jwt.decode(token, verify=False)
            return decoded.get("sub", "anonymous")
        except:
            return "anonymous"

def add_rate_limit_headers(response):
    """Add rate limit headers to response"""
    if hasattr(g, "rate_limit_remaining"):
        response.headers["X-RateLimit-Remaining"] = str(g.rate_limit_remaining)

    if hasattr(g, "rate_limit_reset"):
        response.headers["X-RateLimit-Reset"] = str(int(g.rate_limit_reset))

    return response

app.after_request(add_rate_limit_headers)
```

## Client-Side Handling

```python
import requests
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class RateLimitAwareClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.last_rate_limit_reset = 0

    def make_request(self, method, url, max_retries=3):
        """
        Make request with automatic rate limit handling
        """
        for attempt in range(max_retries):
            # Wait if rate limited
            if time.time() < self.last_rate_limit_reset:
                wait_time = self.last_rate_limit_reset - time.time()
                print(f"Rate limited, waiting {wait_time:.1f} seconds")
                time.sleep(wait_time)

            response = self.session.request(
                method, url,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )

            # Check rate limit headers
            if "Retry-After" in response.headers:
                self.last_rate_limit_reset = (
                    time.time() + int(response.headers["Retry-After"])
                )

            if response.status_code == 429:
                # Rate limited, retry
                if attempt < max_retries - 1:
                    continue
                else:
                    raise Exception("Max rate limit retries exceeded")

            return response

        raise Exception("Request failed")
```

## PSD2 Rate Limiting Requirements

### Standard Limits
```
Account Information Service (AIS):
- 1 request per second per account
- Fair access requirement
- Exemptions for low-value transactions

Payment Initiation Service (PIS):
- 100 requests per hour per payment
- Per account limits
- Payment frequency limits
```

## Rate Limiting Best Practices

1. **Transparent Communication**: Clear rate limit headers
2. **Graceful Degradation**: Prioritize critical operations
3. **User-Friendly Errors**: Explain why they're limited
4. **Graduated Limits**: Higher limits for trusted clients
5. **Monitor Usage**: Track patterns for issues
6. **Fair Distribution**: Prevent single user monopolizing
7. **Seasonal Adjustments**: Increase limits for peak times
8. **Documentation**: Clear rate limit policies

## Testing Rate Limits

```python
def test_rate_limiting():
    """Test rate limit behavior"""
    client = RateLimitAwareClient("test-key")

    # Make requests up to limit
    for i in range(100):
        response = client.make_request(
            "GET",
            "https://api.example.com/accounts"
        )
        assert response.status_code == 200

    # Next request should be rate limited
    response = client.make_request(
        "GET",
        "https://api.example.com/accounts"
    )

    assert response.status_code == 429
    assert "Retry-After" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
```

## References

- Token Bucket: https://en.wikipedia.org/wiki/Token_bucket
- Rate Limiting Algorithms: https://stripe.com/blog/rate-limits
- Rate Limiting Best Practices: https://cloud.google.com/architecture/rate-limiting-strategies-techniques
