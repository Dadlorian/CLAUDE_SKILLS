# API Security Best Practices

> Comprehensive API security guidance based on OWASP API Security Top 10, OAuth 2.0 Security Best Current Practice, and practices from Stripe, Google, AWS, and Microsoft.

---

## API Security Fundamentals

### Defense in Depth for APIs
1. **Authentication**: Verify identity
2. **Authorization**: Verify permissions
3. **Rate Limiting**: Prevent abuse
4. **Input Validation**: Validate all inputs
5. **Encryption**: TLS for all communication
6. **Monitoring**: Log and alert on anomalies

---

## Authentication

### OAuth 2.0 / OpenID Connect (Recommended)

```javascript
// ✅ GOOD: OAuth 2.0 with PKCE for public clients
const express = require('express');
const { auth } = require('express-oauth2-jwt-bearer');

// Validate access tokens
const checkJwt = auth({
    audience: 'https://api.example.com',
    issuerBaseURL: 'https://auth.example.com',
    tokenSigningAlg: 'RS256'  // Asymmetric algorithm
});

app.get('/api/protected', checkJwt, (req, res) => {
    // req.auth contains validated token payload
    res.json({ data: 'protected data' });
});
```

**OAuth 2.0 Best Practices**:
- Use Authorization Code flow with PKCE
- Short-lived access tokens (15 minutes)
- Rotate refresh tokens after use
- Use HTTPS only
- Validate token signature and claims (iss, aud, exp)
- Use asymmetric algorithms (RS256, ES256)

### API Keys (For Server-to-Server)

```python
# API key authentication with secure storage
import hashlib
import hmac
import secrets
from fastapi import HTTPException, Header

def generate_api_key():
    """Generate cryptographically secure API key"""
    key_prefix = 'sk_prod_'  # Helps identify key type/environment
    random_part = secrets.token_urlsafe(32)
    return f"{key_prefix}{random_part}"

async def verify_api_key(x_api_key: str = Header()):
    """Verify API key using constant-time comparison"""
    # Hash the provided key
    provided_hash = hashlib.sha256(x_api_key.encode()).hexdigest()

    # Get stored hash from database
    stored_hash = await db.get_api_key_hash(x_api_key[:10])  # Use prefix for lookup

    # Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(provided_hash, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Log usage for monitoring
    await log_api_key_usage(x_api_key[:10])
```

**API Key Best Practices**:
- Generate with cryptographic PRNG
- Store hashed (like passwords)
- Include metadata in key format (prefix for type/env)
- Allow key rotation
- Support multiple keys per user
- Rate limit by key
- Log all usage
- Revocation mechanism

---

## Authorization

### Role-Based Access Control (RBAC)

```typescript
// Express middleware for RBAC
interface User {
    id: string;
    roles: string[];
    permissions: string[];
}

const requirePermission = (...requiredPermissions: string[]) => {
    return (req: Request, res: Response, next: NextFunction) => {
        const user = req.user as User;

        // Check if user has at least one required permission
        const hasPermission = requiredPermissions.some(permission =>
            user.permissions.includes(permission)
        );

        if (!hasPermission) {
            return res.status(403).json({
                error: 'Forbidden',
                message: 'Insufficient permissions'
            });
        }

        next();
    };
};

// Usage
app.delete('/api/users/:id',
    authenticateToken,
    requirePermission('users:delete'),
    deleteUser
);

app.post('/api/admin/settings',
    authenticateToken,
    requirePermission('admin:write', 'settings:write'),  // OR logic
    updateSettings
);
```

### Resource-Level Authorization

```python
# FastAPI resource ownership check
from fastapi import Depends, HTTPException

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # Validate token and return user
    return await validate_token(token)

async def verify_resource_ownership(
    resource_id: str,
    current_user: User = Depends(get_current_user)
):
    """Verify user owns or has access to resource"""
    resource = await db.get_resource(resource_id)

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Check ownership or admin role
    if resource.owner_id != current_user.id and 'admin' not in current_user.roles:
        raise HTTPException(status_code=403, detail="Access denied")

    return resource

# Usage
@app.get("/api/documents/{document_id}")
async def get_document(
    document: Document = Depends(verify_resource_ownership)
):
    return document
```

---

## Rate Limiting & Throttling

### Token Bucket Algorithm

```go
// Go implementation of token bucket rate limiter
package ratelimit

import (
    "sync"
    "time"
)

type RateLimiter struct {
    tokens         float64
    maxTokens      float64
    refillRate     float64
    lastRefillTime time.Time
    mu             sync.Mutex
}

func NewRateLimiter(maxTokens, refillRate float64) *RateLimiter {
    return &RateLimiter{
        tokens:         maxTokens,
        maxTokens:      maxTokens,
        refillRate:     refillRate,
        lastRefillTime: time.Now(),
    }
}

func (rl *RateLimiter) Allow() bool {
    rl.mu.Lock()
    defer rl.mu.Unlock()

    // Refill tokens based on time elapsed
    now := time.Now()
    elapsed := now.Sub(rl.lastRefillTime).Seconds()
    rl.tokens = min(rl.maxTokens, rl.tokens+elapsed*rl.refillRate)
    rl.lastRefillTime = now

    // Check if we have tokens available
    if rl.tokens >= 1.0 {
        rl.tokens -= 1.0
        return true
    }

    return false
}

// Middleware
func RateLimitMiddleware(limiter *RateLimiter) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            if !limiter.Allow() {
                w.Header().Set("Retry-After", "60")
                http.Error(w, "Rate limit exceeded", http.StatusTooManyRequests)
                return
            }
            next.ServeHTTP(w, r)
        })
    }
}
```

**Rate Limiting Strategies**:
- **Per API Key**: Different limits per tier (free/paid)
- **Per IP**: Prevent abuse from single source
- **Per Endpoint**: Different limits for expensive operations
- **Global**: Protect overall system capacity

**Response Headers**:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
Retry-After: 60
```

---

## Input Validation

### Request Validation with JSON Schema

```javascript
const Ajv = require('ajv');
const ajv = new Ajv();

// Define schema
const userSchema = {
    type: 'object',
    required: ['email', 'name'],
    properties: {
        email: {
            type: 'string',
            format: 'email',
            maxLength: 255
        },
        name: {
            type: 'string',
            minLength: 1,
            maxLength: 100,
            pattern: '^[a-zA-Z\\s]+$'
        },
        age: {
            type: 'integer',
            minimum: 18,
            maximum: 120
        }
    },
    additionalProperties: false  // Reject unknown properties
};

const validate = ajv.compile(userSchema);

app.post('/api/users', (req, res) => {
    // Validate request body
    const valid = validate(req.body);

    if (!valid) {
        return res.status(400).json({
            error: 'Validation failed',
            details: validate.errors
        });
    }

    // Process valid data
    createUser(req.body);
    res.status(201).json({ success: true });
});
```

### SQL Injection Prevention

```python
# ❌ BAD: String formatting (SQL injection!)
def get_user_bad(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# ✅ GOOD: Parameterized query
def get_user_good(username):
    query = "SELECT * FROM users WHERE username = ?"
    return db.execute(query, (username,))

# Using ORM (still validate input!)
def get_user_orm(username):
    # Validate input even with ORM
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValueError("Invalid username format")

    return User.query.filter_by(username=username).first()
```

---

## API Security Headers

### Essential Security Headers

```javascript
const helmet = require('helmet');

app.use(helmet({
    // Content Security Policy
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            scriptSrc: ["'self'"],
            styleSrc: ["'self'"],
            imgSrc: ["'self'", "data:", "https:"],
            connectSrc: ["'self'"],
            fontSrc: ["'self'"],
            objectSrc: ["'none'"],
            mediaSrc: ["'self'"],
            frameSrc: ["'none'"],
        },
    },
    // Strict Transport Security
    hsts: {
        maxAge: 31536000,  // 1 year
        includeSubDomains: true,
        preload: true
    },
    // X-Frame-Options
    frameguard: {
        action: 'deny'
    },
    // X-Content-Type-Options
    noSniff: true,
    // Referrer Policy
    referrerPolicy: {
        policy: 'strict-origin-when-cross-origin'
    }
}));

// CORS configuration
const cors = require('cors');
app.use(cors({
    origin: ['https://app.example.com'],  // Whitelist specific origins
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    exposedHeaders: ['X-RateLimit-Limit', 'X-RateLimit-Remaining'],
    credentials: true,
    maxAge: 86400  // 24 hours
}));
```

---

## OWASP API Security Top 10 (2023)

### API1: Broken Object Level Authorization (BOLA)

```python
# ❌ VULNERABLE: No authorization check
@app.get("/api/orders/{order_id}")
async def get_order(order_id: str):
    order = await db.get_order(order_id)
    return order  # Any user can access any order!

# ✅ SECURE: Verify ownership
@app.get("/api/orders/{order_id}")
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    order = await db.get_order(order_id)

    if not order:
        raise HTTPException(status_code=404)

    # Verify user owns this order
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    return order
```

### API2: Broken Authentication

```javascript
// ✅ Secure JWT validation
const jwt = require('jsonwebtoken');
const jwksClient = require('jwks-rsa');

const client = jwksClient({
    jwksUri: 'https://auth.example.com/.well-known/jwks.json',
    cache: true,
    cacheMaxAge: 600000  // 10 minutes
});

function getKey(header, callback) {
    client.getSigningKey(header.kid, (err, key) => {
        const signingKey = key.publicKey || key.rsaPublicKey;
        callback(null, signingKey);
    });
}

function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];  // Bearer TOKEN

    if (!token) {
        return res.status(401).json({ error: 'Token required' });
    }

    jwt.verify(token, getKey, {
        audience: 'https://api.example.com',
        issuer: 'https://auth.example.com',
        algorithms: ['RS256']  // Only allow secure algorithms
    }, (err, user) => {
        if (err) {
            return res.status(403).json({ error: 'Invalid token' });
        }

        req.user = user;
        next();
    });
}
```

### API3: Broken Object Property Level Authorization

```python
# Use DTOs to control exposed fields
from pydantic import BaseModel
from typing import Optional

class UserPublic(BaseModel):
    """Public user information"""
    id: str
    username: str
    display_name: str
    avatar_url: Optional[str]

class UserPrivate(BaseModel):
    """Private user information (own profile only)"""
    id: str
    username: str
    display_name: str
    avatar_url: Optional[str]
    email: str
    phone: Optional[str]
    created_at: datetime

class UserAdmin(BaseModel):
    """Admin view includes everything"""
    id: str
    username: str
    email: str
    is_active: bool
    role: str
    last_login: datetime
    # ... all fields

@app.get("/api/users/{user_id}", response_model=UserPublic)
async def get_user_profile(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    user = await db.get_user(user_id)

    # Return appropriate DTO based on authorization
    if user.id == current_user.id:
        return UserPrivate(**user.dict())
    elif current_user.is_admin:
        return UserAdmin(**user.dict())
    else:
        return UserPublic(**user.dict())
```

### API4: Unrestricted Resource Consumption

```javascript
// Implement multiple protection layers
const rateLimit = require('express-rate-limit');
const slowDown = require('express-slow-down');

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000,  // 15 minutes
    max: 100,  // Limit each IP to 100 requests per windowMs
    standardHeaders: true,
    legacyHeaders: false,
    message: 'Too many requests, please try again later'
});

// Speed limiting (slow down instead of block)
const speedLimiter = slowDown({
    windowMs: 15 * 60 * 1000,
    delayAfter: 50,  // Allow 50 requests per window
    delayMs: 500  // Add 500ms delay per request after delayAfter
});

// Request size limiting
app.use(express.json({
    limit: '10kb'  // Limit request body size
}));

// Pagination for large datasets
app.get('/api/items', limiter, async (req, res) => {
    const page = parseInt(req.query.page) || 1;
    const limit = Math.min(parseInt(req.query.limit) || 20, 100);  // Max 100 items
    const offset = (page - 1) * limit;

    const items = await db.getItems({ limit, offset });
    const total = await db.countItems();

    res.json({
        items,
        pagination: {
            page,
            limit,
            total,
            pages: Math.ceil(total / limit)
        }
    });
});
```

### API5-API10 Quick Reference

**API5: Broken Function Level Authorization**
- Check authorization for each function/action
- Don't rely on client-side role checks
- Implement RBAC/ABAC consistently

**API6: Unrestricted Access to Sensitive Business Flows**
- Implement business logic rate limiting
- Add CAPTCHA for sensitive actions
- Monitor for automated abuse

**API7: Server Side Request Forgery (SSRF)**
- Whitelist allowed URLs/domains
- Validate and sanitize URLs
- Use network segmentation

**API8: Security Misconfiguration**
- Disable unnecessary HTTP methods
- Remove default credentials
- Keep software updated
- Proper error messages (no stack traces)

**API9: Improper Inventory Management**
- Document all API endpoints
- Version control for APIs
- Deprecation policy
- Remove old/unused endpoints

**API10: Unsafe Consumption of APIs**
- Validate third-party API responses
- Use timeouts and circuit breakers
- Don't trust external data
- Encrypt third-party API credentials

---

## API Versioning

```javascript
// URL path versioning (recommended for breaking changes)
app.get('/api/v1/users', getUsersV1);
app.get('/api/v2/users', getUsersV2);

// Header versioning (for minor changes)
app.get('/api/users', (req, res) => {
    const version = req.headers['api-version'] || '1';

    if (version === '2') {
        return getUsersV2(req, res);
    }
    return getUsersV1(req, res);
});

// Deprecation headers
res.set({
    'Deprecation': 'true',
    'Sunset': 'Sat, 31 Dec 2025 23:59:59 GMT',
    'Link': '<https://api.example.com/v2/users>; rel="successor-version"'
});
```

---

## Monitoring & Logging

```python
import structlog
from datetime import datetime

logger = structlog.get_logger()

# Log API requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log request
    logger.info("api_request",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    response = await call_next(request)

    # Log response
    duration = time.time() - start_time
    logger.info("api_response",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration * 1000, 2)
    )

    # Alert on security events
    if response.status_code == 401:
        logger.warning("authentication_failure",
            path=request.url.path,
            ip=request.client.host
        )
    elif response.status_code == 403:
        logger.warning("authorization_failure",
            path=request.url.path,
            ip=request.client.host
        )

    return response
```

---

## Security Testing

### Automated Security Tests

```python
# pytest example for API security testing
import pytest
from fastapi.testclient import TestClient

def test_authentication_required():
    """Test that endpoints require authentication"""
    response = client.get("/api/protected")
    assert response.status_code == 401

def test_authorization_enforced():
    """Test that users can only access their own resources"""
    user1_token = get_token_for_user(user1)
    user2_token = get_token_for_user(user2)

    # User1 creates resource
    response = client.post("/api/documents",
        headers={"Authorization": f"Bearer {user1_token}"},
        json={"title": "User1 Doc"}
    )
    doc_id = response.json()["id"]

    # User2 should NOT be able to access User1's document
    response = client.get(f"/api/documents/{doc_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 403

def test_sql_injection_protection():
    """Test SQL injection prevention"""
    malicious_input = "admin' OR '1'='1"
    response = client.get(f"/api/users?username={malicious_input}")
    # Should return 400 (validation error) or 404, not 200 with all users
    assert response.status_code in [400, 404]

def test_rate_limiting():
    """Test rate limiting works"""
    # Make requests up to limit
    for i in range(100):
        response = client.get("/api/items")
        assert response.status_code == 200

    # Next request should be rate limited
    response = client.get("/api/items")
    assert response.status_code == 429
```

---

## References

- **OWASP API Security Top 10**: https://owasp.org/API-Security/
- **OAuth 2.0 Security BCP**: RFC 8252, RFC 8628
- **REST API Security**: OWASP REST Security Cheat Sheet
- **Industry Practices**: Stripe, Google, AWS API documentation

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Compliance**: OWASP API Security Top 10 2023, OAuth 2.0 BCP
