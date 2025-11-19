# REST API Design Guide

## Overview

This guide outlines best practices for designing RESTful APIs based on industry standards from Microsoft, Google, and the broader API community.

---

## Core REST Principles

### Resource-Oriented Design

**Resources as Nouns, Not Verbs**:
```
❌ Bad:
GET  /getUsers
POST /createUser
POST /deleteUser

✅ Good:
GET    /users
POST   /users
DELETE /users/:id
```

### HTTP Methods

| Method | Purpose | Idempotent | Safe |
|--------|---------|------------|------|
| GET | Retrieve resource(s) | ✅ | ✅ |
| POST | Create resource | ❌ | ❌ |
| PUT | Replace resource | ✅ | ❌ |
| PATCH | Update resource partially | ❌ | ❌ |
| DELETE | Delete resource | ✅ | ❌ |

**Proper Method Usage**:
```
GET    /users           # List all users
GET    /users/:id       # Get specific user
POST   /users           # Create new user
PUT    /users/:id       # Replace user
PATCH  /users/:id       # Update user fields
DELETE /users/:id       # Delete user
```

---

## URL Structure

### Naming Conventions

**Use Plural Nouns**:
```
✅ Good:
/users
/products
/orders

❌ Bad:
/user
/product
/order
```

**Hierarchical Resources**:
```
✅ Good:
GET /users/:userId/orders
GET /users/:userId/orders/:orderId
GET /products/:productId/reviews

❌ Bad:
GET /userOrders/:userId
GET /productReviews/:productId
```

**Lowercase and Hyphenation**:
```
✅ Good:
/product-categories
/user-preferences

❌ Bad:
/productCategories
/user_preferences
/Product-Categories
```

### Query Parameters

**Filtering**:
```
GET /users?status=active
GET /products?category=electronics&price_min=100
```

**Sorting**:
```
GET /users?sort=created_at:desc
GET /products?sort=price:asc,name:asc
```

**Pagination**:
```
GET /users?page=2&limit=50
GET /users?offset=100&limit=50
```

**Field Selection**:
```
GET /users?fields=id,name,email
GET /users/:id?fields=name,email,created_at
```

**Search**:
```
GET /users?q=john
GET /products?search=laptop&category=electronics
```

---

## Request & Response Formats

### Request Body (POST/PUT/PATCH)

**JSON Format**:
```json
POST /users
Content-Type: application/json

{
  "email": "john@example.com",
  "name": "John Doe",
  "role": "admin",
  "preferences": {
    "theme": "dark",
    "notifications": true
  }
}
```

**Field Naming**:
```json
✅ Good (snake_case or camelCase, be consistent):
{
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2025-01-15T10:30:00Z"
}

{
  "firstName": "John",
  "lastName": "Doe",
  "createdAt": "2025-01-15T10:30:00Z"
}
```

### Response Format

**Successful Response**:
```json
GET /users/123
Status: 200 OK

{
  "id": "123",
  "email": "john@example.com",
  "name": "John Doe",
  "role": "admin",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Collection Response**:
```json
GET /users?page=1&limit=20
Status: 200 OK

{
  "data": [
    {
      "id": "123",
      "name": "John Doe",
      "email": "john@example.com"
    },
    {
      "id": "124",
      "name": "Jane Smith",
      "email": "jane@example.com"
    }
  ],
  "meta": {
    "total": 150,
    "page": 1,
    "limit": 20,
    "total_pages": 8
  },
  "links": {
    "self": "/users?page=1&limit=20",
    "next": "/users?page=2&limit=20",
    "last": "/users?page=8&limit=20"
  }
}
```

**Error Response**:
```json
Status: 400 Bad Request

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      },
      {
        "field": "age",
        "message": "Must be at least 18"
      }
    ]
  }
}
```

---

## HTTP Status Codes

### Success Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 OK | Success | GET, PUT, PATCH successful |
| 201 Created | Resource created | POST successful |
| 204 No Content | Success, no body | DELETE successful |

### Client Error Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 400 Bad Request | Invalid request | Validation errors |
| 401 Unauthorized | Not authenticated | Missing/invalid token |
| 403 Forbidden | Not authorized | Insufficient permissions |
| 404 Not Found | Resource doesn't exist | Invalid ID |
| 409 Conflict | Resource conflict | Duplicate email |
| 422 Unprocessable Entity | Semantic errors | Business logic validation |
| 429 Too Many Requests | Rate limit exceeded | Too many requests |

### Server Error Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 500 Internal Server Error | Server error | Unexpected errors |
| 502 Bad Gateway | Upstream error | Dependency failure |
| 503 Service Unavailable | Temporarily down | Maintenance |
| 504 Gateway Timeout | Upstream timeout | Slow dependency |

**Proper Status Code Usage**:
```typescript
// ✅ Good status code selection
app.post('/users', async (req, res) => {
  try {
    const user = await createUser(req.body);
    return res.status(201).json(user); // Created
  } catch (error) {
    if (error instanceof ValidationError) {
      return res.status(400).json({ error: error.message });
    }
    if (error instanceof DuplicateEmailError) {
      return res.status(409).json({ error: 'Email already exists' });
    }
    return res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/users/:id', async (req, res) => {
  const user = await findUser(req.params.id);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  return res.status(200).json(user);
});

app.delete('/users/:id', async (req, res) => {
  await deleteUser(req.params.id);
  return res.status(204).send(); // No content
});
```

---

## Versioning

### URL Versioning (Recommended)
```
✅ Recommended:
https://api.example.com/v1/users
https://api.example.com/v2/users

Pros: Clear, easy to route, widely understood
Cons: More URLs to maintain
```

### Header Versioning
```
GET /users
Accept: application/vnd.example.v2+json

Pros: Cleaner URLs
Cons: Less visible, harder to test
```

### Version Strategy
```
- v1: Initial release
- v2: Breaking changes (e.g., field name changes, removed endpoints)
- v1.1: Non-breaking additions (new fields, new endpoints)
```

---

## Authentication & Authorization

### Bearer Token (JWT)
```
GET /users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Key
```
GET /users
X-API-Key: your-api-key-here
```

### OAuth 2.0
```
GET /users
Authorization: Bearer <access_token>
```

**Authorization Header Example**:
```typescript
// ✅ Proper authorization check
app.get('/users/:id', authenticateToken, async (req, res) => {
  const user = await findUser(req.params.id);

  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }

  // Check if user can access this resource
  if (req.user.id !== user.id && !req.user.isAdmin) {
    return res.status(403).json({ error: 'Access denied' });
  }

  return res.status(200).json(user);
});
```

---

## Pagination

### Cursor-Based Pagination (Recommended for large datasets)
```json
GET /users?cursor=eyJpZCI6MTIzfQ&limit=20

Response:
{
  "data": [...],
  "meta": {
    "next_cursor": "eyJpZCI6MTQzfQ",
    "has_more": true
  }
}
```

### Offset-Based Pagination (Simple, but expensive)
```json
GET /users?page=2&limit=20
GET /users?offset=40&limit=20

Response:
{
  "data": [...],
  "meta": {
    "total": 150,
    "page": 2,
    "limit": 20,
    "total_pages": 8
  }
}
```

---

## Rate Limiting

### Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642521600
```

### Response When Limited
```
Status: 429 Too Many Requests
Retry-After: 3600

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again in 1 hour."
  }
}
```

---

## HATEOAS (Hypermedia)

**Including Links**:
```json
GET /users/123

{
  "id": "123",
  "name": "John Doe",
  "email": "john@example.com",
  "_links": {
    "self": { "href": "/users/123" },
    "orders": { "href": "/users/123/orders" },
    "update": {
      "href": "/users/123",
      "method": "PATCH"
    },
    "delete": {
      "href": "/users/123",
      "method": "DELETE"
    }
  }
}
```

---

## Filtering, Sorting & Searching

### Advanced Filtering
```
GET /products?price[gte]=100&price[lte]=500
GET /users?created_at[gt]=2025-01-01
GET /orders?status[in]=pending,processing
```

### Complex Sorting
```
GET /users?sort=last_name:asc,first_name:asc
GET /products?sort=-price,name
```

### Full-Text Search
```
GET /articles?q=kubernetes&fields=title,content
```

---

## Bulk Operations

### Bulk Create
```json
POST /users/bulk

{
  "users": [
    { "email": "user1@example.com", "name": "User 1" },
    { "email": "user2@example.com", "name": "User 2" }
  ]
}

Response:
{
  "created": 2,
  "failed": 0,
  "results": [...]
}
```

### Bulk Update
```json
PATCH /users/bulk

{
  "ids": ["123", "124", "125"],
  "updates": {
    "status": "active"
  }
}
```

### Bulk Delete
```json
DELETE /users/bulk

{
  "ids": ["123", "124", "125"]
}
```

---

## Asynchronous Operations

**Long-Running Tasks**:
```
POST /reports/generate
Status: 202 Accepted
Location: /reports/tasks/abc-123

{
  "task_id": "abc-123",
  "status": "processing",
  "_links": {
    "status": "/reports/tasks/abc-123"
  }
}

GET /reports/tasks/abc-123
{
  "task_id": "abc-123",
  "status": "completed",
  "result": {
    "report_url": "/reports/download/xyz-789"
  }
}
```

---

## Caching

### Cache Headers
```
GET /users/123

Response Headers:
Cache-Control: public, max-age=3600
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
Last-Modified: Wed, 15 Jan 2025 10:30:00 GMT
```

### Conditional Requests
```
GET /users/123
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"

Response:
Status: 304 Not Modified
```

---

## Error Handling Best Practices

### Consistent Error Format
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "User not found",
    "details": "No user exists with ID: 123",
    "timestamp": "2025-01-15T10:30:00Z",
    "path": "/users/123",
    "request_id": "req-abc-123"
  }
}
```

### Error Codes
```typescript
// Define standard error codes
enum ErrorCode {
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  RESOURCE_NOT_FOUND = 'RESOURCE_NOT_FOUND',
  DUPLICATE_RESOURCE = 'DUPLICATE_RESOURCE',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  INTERNAL_SERVER_ERROR = 'INTERNAL_SERVER_ERROR'
}
```

---

## API Documentation (OpenAPI/Swagger)

**Example OpenAPI Spec**:
```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
    post:
      summary: Create user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Validation error
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        email:
          type: string
        name:
          type: string
        created_at:
          type: string
          format: date-time
```

---

## Security Best Practices

### HTTPS Only
```
✅ All API traffic over HTTPS
❌ Never use HTTP for sensitive data
```

### Input Validation
```typescript
// ✅ Validate all inputs
const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  age: z.number().min(0).max(150)
});

app.post('/users', async (req, res) => {
  const result = createUserSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({
      error: { code: 'VALIDATION_ERROR', details: result.error }
    });
  }
  // Process validated data
});
```

### SQL Injection Prevention
```typescript
// ✅ Use parameterized queries
db.query('SELECT * FROM users WHERE email = $1', [email]);

// ❌ Never concatenate SQL
db.query(`SELECT * FROM users WHERE email = '${email}'`);
```

### CORS Configuration
```typescript
app.use(cors({
  origin: ['https://example.com'],
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true
}));
```

---

## References

- **Microsoft REST API Guidelines**: https://github.com/microsoft/api-guidelines
- **Google API Design Guide**: https://cloud.google.com/apis/design
- **OpenAPI Specification**: https://swagger.io/specification/
- **HTTP Status Codes**: https://httpstatuses.com/
- **REST API Tutorial**: https://restfulapi.net/

---

## Version

**Version**: 1.0
**Last Updated**: 2025-11-19
