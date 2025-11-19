# Production-Ready API Documentation Examples

This directory contains comprehensive, production-ready examples demonstrating best practices for API documentation, authentication, rate limiting, webhooks, and client implementations.

## Files Overview

### 1. authentication-examples.js
**Purpose:** OAuth2 and JWT authentication patterns for Node.js/Express

**Content:**
- `OAuth2Handler` - Complete OAuth2 authorization code flow implementation
- `JWTValidator` - JWT creation, verification, and validation
- `AuthenticationMiddleware` - Express middleware for authentication

**Use Cases:**
- Setting up OAuth2 login flows
- JWT token validation in APIs
- Implementing scope-based access control
- Role-based authorization

**Key Features:**
- CSRF protection with state tokens
- Token refresh mechanisms
- Idempotent token exchange
- Comprehensive error handling
- Production-grade security

**Example:**
```javascript
const oauth2 = new OAuth2Handler({
  clientId: 'your-client-id',
  clientSecret: 'your-client-secret',
  redirectUri: 'http://localhost:3000/callback',
  authorizationEndpoint: 'https://provider.com/oauth/authorize',
  tokenEndpoint: 'https://provider.com/oauth/token'
});

const authUrl = oauth2.getAuthorizationUrl({ state: generateState() });
// Redirect user to authUrl for authentication
```

**Dependencies:**
- jsonwebtoken
- axios
- express

**Size:** ~420 lines
**Complexity:** Intermediate

---

### 2. rate-limiting-middleware.js
**Purpose:** Express middleware for API rate limiting and quota management

**Content:**
- `TokenBucketLimiter` - Token bucket algorithm for rate limiting
- `SlidingWindowLimiter` - Sliding window approach
- `RateLimitMiddleware` - Factory for creating Express middleware
- Tiered rate limiting support
- Route-specific rate limiting

**Use Cases:**
- Implementing API rate limits
- Protecting against abuse
- Tiered/freemium pricing models
- Per-endpoint rate limiting
- DDoS mitigation

**Key Features:**
- Flexible capacity and refill rates
- Automatic cleanup of inactive buckets
- Tiered limiting based on user tier
- Per-user and per-IP tracking
- Standard rate limit headers (X-RateLimit-*)
- Graceful handling when limits exceeded

**Example:**
```javascript
app.use(RateLimitMiddleware.createTokenBucketMiddleware({
  capacity: 100,
  refillRate: 10,
  refillInterval: 1000,
  keyGenerator: (req) => req.user?.id || req.ip
}));
```

**Dependencies:**
- express

**Size:** ~450 lines
**Complexity:** Intermediate

---

### 3. webhook-handler.py
**Purpose:** Production-ready webhook handling with signature verification

**Content:**
- `SignatureVerifier` - HMAC-SHA256 signature verification
- `WebhookPayload` - Pydantic models for payload validation
- `WebhookRetryPolicy` - Exponential backoff for failed deliveries
- `WebhookProcessor` - Main webhook processing engine
- Event handler registration and routing
- Flask blueprint factory

**Use Cases:**
- Handling incoming webhooks from payment processors
- Event-driven architectures
- Third-party integrations
- Asynchronous event processing
- Webhook endpoint security

**Key Features:**
- HMAC-SHA256 and SHA-512 signature verification
- Payload validation with Pydantic
- Idempotent processing (duplicate detection)
- Exponential backoff retry logic
- Thread-safe event queueing
- Event handler registration
- Replay attack prevention (timestamp validation)
- Multiple algorithm support

**Example:**
```python
processor = WebhookProcessor(secret='webhook-secret')
processor.register_handler(
    WebhookEventType.USER_CREATED.value,
    handle_user_created
)

# Verify incoming webhook
is_valid, error = processor.verify_request(
    body=request.get_data(),
    signature=request.headers.get('X-Webhook-Signature-Sha256'),
    timestamp=request.headers.get('X-Webhook-Timestamp')
)
```

**Dependencies:**
- flask
- pydantic
- cryptography

**Size:** ~450 lines
**Complexity:** Intermediate

---

### 4. postman-collection.json
**Purpose:** Complete Postman collection for API testing and documentation

**Content:**
- OAuth2 authentication flow requests
- CRUD operations (Users, Products, Orders)
- Webhook management endpoints
- Rate limiting test requests
- Health and status checks
- Pre-configured variables
- Test scripts

**Use Cases:**
- API endpoint testing
- Onboarding new developers
- Integration testing
- API documentation
- Load testing
- Manual exploratory testing

**Key Features:**
- Environment variables for flexible configuration
- OAuth2 flow with automatic token storage
- Pre and post-request scripts
- Response validation
- Example payloads
- Rate limit testing
- Complete CRUD examples

**Variables:**
- `base_url` - API base URL
- `jwt_token` - Stored access token
- `client_id` - OAuth2 client ID
- `client_secret` - OAuth2 client secret
- `webhook_secret` - Webhook signing secret

**Size:** ~600 lines
**Complexity:** Beginner

---

### 5. api-client-examples/
**Purpose:** Production-ready API clients in multiple languages

#### python_client.py
**Features:**
- OAuth2 Client Credentials flow
- Automatic retry with exponential backoff
- Request/response logging
- Type hints for IDE support
- Context manager support
- Specialized client classes

**Example:**
```python
config = APIConfig(
    base_url='https://api.example.com/v1',
    client_id='your-id',
    client_secret='your-secret'
)
oauth2 = OAuth2Client(config)
oauth2.get_token('https://auth.example.com/oauth/token')
with APIClient(config, oauth2) as client:
    users = client.get('/users', params={'limit': 10})
```

**Size:** 425 lines

#### ruby_client.rb
**Features:**
- HTTPClient with persistent connections
- Thread-safe operations
- Exception-based error handling
- Time-based token expiration
- Comprehensive logging

**Size:** 398 lines

#### go_client.go
**Features:**
- Concurrent request handling
- Minimal dependencies
- Efficient memory usage
- Custom backoff strategy
- HTTP/2 support

**Size:** 445 lines

#### JavaAPIClient.java
**Features:**
- Java 11+ HttpClient
- Type-safe operations
- HTTP/2 support
- Comprehensive logging
- Gson integration

**Size:** 512 lines

### api-client-examples/README.md
Comprehensive guide covering:
- Quick start for each language
- Configuration options
- Error handling patterns
- Rate limiting strategies
- Security considerations
- Testing approaches
- Troubleshooting guide

---

### openapi-complete-example.yaml
**Purpose:** OpenAPI 3.0 specification for the example API

**Content:**
- Complete API specification
- All endpoints documented
- Request/response schemas
- Authentication schemes
- Error responses
- Rate limit definitions

---

## Quick Start

### Setting Up Authentication
```javascript
// Use authentication-examples.js
const { OAuth2Handler, JWTValidator, AuthenticationMiddleware } =
  require('./authentication-examples.js');

const oauth2 = new OAuth2Handler(config);
const authUrl = oauth2.getAuthorizationUrl({ state: 'random' });
```

### Adding Rate Limiting
```javascript
// Use rate-limiting-middleware.js
const { RateLimitMiddleware } = require('./rate-limiting-middleware.js');

app.use(RateLimitMiddleware.createTokenBucketMiddleware({
  capacity: 100,
  refillRate: 10
}));
```

### Processing Webhooks
```python
# Use webhook-handler.py
from webhook_handler import WebhookProcessor

processor = WebhookProcessor(secret='your-secret')
processor.register_handler('user.created', handle_user_created)
```

### Testing API
```
1. Import postman-collection.json into Postman
2. Set environment variables
3. Run OAuth2 authentication flow
4. Execute any request
```

### Using Client Libraries
```python
# Python
python api-client-examples/python_client.py

# Ruby
ruby api-client-examples/ruby_client.rb

# Go
go run api-client-examples/go_client.go

# Java
javac api-client-examples/JavaAPIClient.java
java JavaAPIClient
```

## Directory Structure

```
src/
├── README.md (this file)
├── authentication-examples.js
├── rate-limiting-middleware.js
├── webhook-handler.py
├── postman-collection.json
├── openapi-complete-example.yaml
└── api-client-examples/
    ├── README.md
    ├── python_client.py
    ├── ruby_client.rb
    ├── go_client.go
    └── JavaAPIClient.java
```

## Key Patterns Demonstrated

### OAuth2 Flow
```
1. Get authorization URL
2. User logs in and grants permission
3. Exchange code for tokens
4. Use tokens for API requests
5. Refresh tokens when expired
```

### Rate Limiting
```
1. Check available tokens
2. Decrement tokens for request
3. Return rate limit headers
4. Implement client-side backoff
5. Periodic cleanup
```

### Webhook Handling
```
1. Receive webhook POST
2. Verify signature
3. Validate timestamp (prevent replay)
4. Parse and validate payload
5. Process asynchronously
6. Return 202 Accepted
```

## Best Practices Implemented

### Security
- CSRF protection with state tokens
- HMAC signature verification
- SSL/TLS enforcement
- Credentials never logged
- Secure token storage

### Reliability
- Exponential backoff for retries
- Idempotent operations
- Error recovery
- Connection pooling
- Request timeouts

### Performance
- Minimal dependencies
- Connection reuse
- Efficient retry strategy
- Memory-efficient queuing
- Automatic cleanup

### Maintainability
- Comprehensive logging
- Clear error messages
- Type hints (where applicable)
- Well-documented code
- Extensible design

## Testing Approach

### Unit Tests
Each component includes testable interfaces:
- Mock HTTP responses
- Verify error handling
- Test retry logic
- Validate signature verification

### Integration Tests
Test complete workflows:
- OAuth2 authentication flow
- API request/response cycle
- Webhook delivery and processing
- Rate limit enforcement

### Load Testing
Use Postman collection for:
- Rate limit triggering
- Performance measurement
- Concurrent request testing

## Migration Guide

### From Other API Clients
```python
# Before: Using requests directly
import requests
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('https://api.example.com/v1/users', headers=headers)

# After: Using provided client
api_client = APIClient(config, oauth2)
response = api_client.get('/users')
```

## Troubleshooting

### Authentication Failures
1. Verify credentials in environment variables
2. Check OAuth2 endpoint URLs
3. Ensure scopes are correct
4. Verify token expiration

### Rate Limiting Issues
1. Check X-RateLimit-* headers in response
2. Implement proper backoff
3. Verify rate limit configuration
4. Check if tiered limits apply

### Webhook Failures
1. Verify webhook secret matches
2. Check timestamp is recent (within 5 minutes)
3. Validate signature computation
4. Check payload format

## Performance Metrics

| Component | Memory | CPU | Latency |
|-----------|--------|-----|---------|
| OAuth2Client | ~1KB | Minimal | ~100ms |
| RateLimiter | ~10KB per 100 users | Minimal | <1ms |
| WebhookHandler | ~5KB per event | Low | ~10ms |
| APIClient | ~50KB per request | Low | Variable |

## Security Checklist

- [ ] Credentials stored in environment variables
- [ ] HTTPS/TLS enforced
- [ ] CSRF tokens implemented
- [ ] Webhook signatures verified
- [ ] Token expiration handled
- [ ] Error messages don't leak sensitive data
- [ ] Logging doesn't include credentials
- [ ] Rate limiting prevents abuse
- [ ] Input validation on all endpoints
- [ ] CORS properly configured

## Resources

### External Documentation
- OAuth2 Specification: https://tools.ietf.org/html/rfc6749
- JWT Introduction: https://jwt.io/
- OpenAPI 3.0: https://spec.openapis.org/oas/v3.0.0
- Webhook Best Practices: https://webhooks.example.com/docs

### Related Files
- [API Documentation Guide](../guides/)
- [Reference Materials](../reference/)
- [Skill Definition](../skill.md)

## Contributing

When adding new examples:
1. Follow established patterns
2. Include comprehensive error handling
3. Add logging/debugging support
4. Write example usage code
5. Update this README
6. Test with real API endpoints
7. Document security considerations
8. Include performance notes

## License

These examples are provided for reference and educational purposes. Adapt them to your specific needs.

## Support

For detailed help:
1. Read the component-specific documentation
2. Check api-client-examples/README.md for language-specific guidance
3. Review example usage in each file
4. Examine the Postman collection
5. Study the OpenAPI specification

## Summary Table

| File | Language | Purpose | Lines | Complexity |
|------|----------|---------|-------|-----------|
| authentication-examples.js | JavaScript | OAuth2 & JWT | 420 | Intermediate |
| rate-limiting-middleware.js | JavaScript | Rate Limiting | 450 | Intermediate |
| webhook-handler.py | Python | Webhooks | 450 | Intermediate |
| postman-collection.json | JSON | Testing | 600 | Beginner |
| python_client.py | Python | Client | 425 | Intermediate |
| ruby_client.rb | Ruby | Client | 398 | Intermediate |
| go_client.go | Go | Client | 445 | Intermediate |
| JavaAPIClient.java | Java | Client | 512 | Intermediate |

**Total Examples:** 8 files
**Total Lines:** ~3,700 lines of production-ready code
**Total Coverage:** Authentication, Rate Limiting, Webhooks, Testing, Clients in 4 languages
