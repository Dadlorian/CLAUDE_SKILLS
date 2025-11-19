# HTTP Status Codes - Quick Reference

## Success Codes (2xx)

| Code | Name | Use in APIs |
|------|------|-------------|
| **200** | OK | Successful GET, PUT, PATCH, DELETE |
| **201** | Created | Successful POST (resource created) |
| **202** | Accepted | Request accepted, processing async |
| **204** | No Content | Successful DELETE (no response body) |

## Client Error Codes (4xx)

| Code | Name | Use in APIs |
|------|------|-------------|
| **400** | Bad Request | Invalid request syntax/parameters |
| **401** | Unauthorized | Missing or invalid authentication |
| **403** | Forbidden | Authenticated but not authorized |
| **404** | Not Found | Resource doesn't exist |
| **405** | Method Not Allowed | Wrong HTTP method for endpoint |
| **409** | Conflict | Resource already exists |
| **422** | Unprocessable Entity | Validation failed |
| **429** | Too Many Requests | Rate limit exceeded |

## Server Error Codes (5xx)

| Code | Name | Use in APIs |
|------|------|-------------|
| **500** | Internal Server Error | Server error (catch-all) |
| **502** | Bad Gateway | Upstream server error |
| **503** | Service Unavailable | Temporary outage/maintenance |
| **504** | Gateway Timeout | Upstream server timeout |

## Special Codes

| Code | Name | Use in APIs |
|------|------|-------------|
| **410** | Gone | Resource permanently deleted |
| **451** | Unavailable For Legal Reasons | Legally restricted content |

## Common Patterns

### Success Flow
```
POST /users → 201 Created
GET /users/123 → 200 OK
PUT /users/123 → 200 OK
DELETE /users/123 → 204 No Content
GET /users/123 → 404 Not Found
```

### Error Flow
```
POST /users (missing email) → 422 Unprocessable Entity
POST /users (duplicate email) → 409 Conflict
GET /users/999 → 404 Not Found
PUT /users/123 (unauthorized) → 403 Forbidden
```

## When to Use Each Code

### 200 vs 201 vs 204
- **200**: Successful request with response body
- **201**: Resource created, return new resource
- **204**: Successful, no response body needed

### 400 vs 422
- **400**: Malformed request (invalid JSON, wrong content-type)
- **422**: Valid request but failed validation (invalid email format)

### 401 vs 403
- **401**: Not authenticated (missing/invalid credentials)
- **403**: Authenticated but not authorized (insufficient permissions)

### 404 vs 410
- **404**: Resource not found (may exist in future)
- **410**: Resource permanently removed (won't return)

## Best Practices

✅ **Do**:
- Use appropriate status codes
- Include error details in response body
- Document all possible status codes per endpoint
- Be consistent across your API

❌ **Don't**:
- Return 200 for errors with error in body
- Use obscure codes (451 rarely needed)
- Mix success and error semantics

## Example Responses

### 201 Created
```http
HTTP/1.1 201 Created
Location: /users/usr_123
Content-Type: application/json

{
  "id": "usr_123",
  "email": "alice@example.com",
  "created_at": "2025-11-19T10:30:00Z"
}
```

### 400 Bad Request
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": {
    "code": "invalid_json",
    "message": "Request body is not valid JSON"
  }
}
```

### 422 Unprocessable Entity
```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "error": {
    "code": "validation_error",
    "message": "Validation failed",
    "details": {
      "email": ["Invalid email format"],
      "age": ["Must be at least 18"]
    }
  }
}
```

### 429 Too Many Requests
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1732017120

{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Retry after 60 seconds."
  }
}
```

---

**Quick Rule**: 2xx = success, 4xx = client error, 5xx = server error
