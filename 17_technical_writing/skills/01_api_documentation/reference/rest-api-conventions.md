# REST API Conventions - Quick Reference

## URL Structure

### Resource Naming
```
✅ GOOD - Plural nouns:
/users
/payments
/subscriptions

❌ BAD - Singular or verbs:
/user
/getUsers
/createPayment
```

### Resource Hierarchy
```
Collection:     GET    /users
Specific:       GET    /users/{id}
Nested:         GET    /users/{id}/payments
```

### URL Guidelines
- Use lowercase
- Use hyphens for multi-word resources (`/payment-methods`, not `/paymentMethods`)
- No trailing slashes (`/users`, not `/users/`)
- Avoid deep nesting (max 2-3 levels)

## HTTP Methods

| Method | Purpose | Idempotent | Safe |
|--------|---------|------------|------|
| GET | Retrieve resource(s) | Yes | Yes |
| POST | Create resource | No | No |
| PUT | Replace entire resource | Yes | No |
| PATCH | Update partial resource | No* | No |
| DELETE | Delete resource | Yes | No |

*PATCH can be idempotent with proper implementation

### Standard Operations

```
GET    /users           # List all users
POST   /users           # Create a user
GET    /users/{id}      # Get specific user
PUT    /users/{id}      # Replace user
PATCH  /users/{id}      # Update user
DELETE /users/{id}      # Delete user
```

## Request Headers

### Required
```http
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY
```

### Recommended
```http
Accept: application/json
Accept-Language: en-US
User-Agent: MyApp/1.0
```

### Idempotency
```http
Idempotency-Key: unique_key_12345
```

## Response Format

### Success Response
```json
{
  "id": "usr_123",
  "email": "alice@example.com",
  "name": "Alice Johnson",
  "created_at": "2025-11-19T10:30:00Z"
}
```

### Collection Response
```json
{
  "data": [
    {"id": "usr_1", "name": "Alice"},
    {"id": "usr_2", "name": "Bob"}
  ],
  "has_more": false,
  "total_count": 2
}
```

### Error Response
```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid email format",
    "details": {
      "field": "email"
    }
  }
}
```

## Pagination

### Cursor-Based (Recommended)
```
GET /users?limit=20&starting_after=usr_123

Response:
{
  "data": [...],
  "has_more": true,
  "next_cursor": "usr_456"
}
```

### Offset-Based
```
GET /users?limit=20&offset=40

Response:
{
  "data": [...],
  "total": 156,
  "limit": 20,
  "offset": 40
}
```

## Filtering & Sorting

### Filtering
```
GET /payments?status=succeeded&amount_gte=1000
GET /users?created_after=2025-01-01
GET /posts?tags=api,documentation
```

### Sorting
```
GET /users?sort=created_at          # Ascending
GET /users?sort=-created_at         # Descending
GET /users?sort=name,-created_at    # Multiple fields
```

## Versioning

### URL Path (Recommended)
```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

### Header
```http
Accept: application/vnd.example.v2+json
```

### Query Parameter
```
https://api.example.com/users?version=2
```

## Rate Limiting

### Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1732017120
Retry-After: 60
```

### Response
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60

{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded"
  }
}
```

## Common Patterns

### Batch Operations
```http
POST /users/batch
{
  "users": [
    {"email": "alice@example.com", "name": "Alice"},
    {"email": "bob@example.com", "name": "Bob"}
  ]
}
```

### Actions on Resources
```http
POST /payments/{id}/capture
POST /payments/{id}/refund
POST /users/{id}/reset-password
```

### Search
```http
GET /search?q=documentation&type=posts
POST /search
{
  "query": "documentation",
  "filters": {"type": "posts"}
}
```

## Field Selection

### Sparse Fields
```
GET /users?fields=id,name,email
```

### Expansion
```
GET /payments?expand=customer
GET /payments?expand=customer,subscription
```

## Best Practices

✅ **Do**:
- Use plural nouns for resources
- Use HTTP methods correctly
- Return appropriate status codes
- Include pagination for lists
- Version your API
- Implement rate limiting
- Use ISO 8601 for dates
- Document all endpoints

❌ **Don't**:
- Use verbs in URLs
- Return 200 for errors
- Nest resources too deeply
- Ignore versioning
- Return all fields always
- Use inconsistent naming

---

**Quick Rules**:
1. Resources = Nouns (plural)
2. Actions = HTTP Methods
3. 2xx = Success, 4xx = Client Error, 5xx = Server Error
