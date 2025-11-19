# REST API Documentation Patterns

## Overview

Industry-standard patterns for documenting RESTful APIs based on leading practices from Stripe, Twilio, GitHub, and RESTful Web Services by Richardson & Ruby.

---

## Core REST Principles

### Resource-Based URLs

```markdown
✅ GOOD - Nouns, not verbs:
GET    /users
GET    /users/{id}
POST   /users
PUT    /users/{id}
DELETE /users/{id}

❌ BAD - Verbs in URLs:
GET    /getUsers
POST   /createUser
POST   /deleteUser
```

### HTTP Methods (Verbs)

| Method | Purpose | Idempotent | Safe |
|--------|---------|------------|------|
| GET | Retrieve resource(s) | Yes | Yes |
| POST | Create resource | No | No |
| PUT | Replace resource | Yes | No |
| PATCH | Update resource partially | No* | No |
| DELETE | Delete resource | Yes | No |

*PATCH can be idempotent with proper implementation

---

## URL Patterns

### Collection and Resource

```
GET    /payments           # List all payments
POST   /payments           # Create a payment
GET    /payments/{id}      # Get specific payment
PUT    /payments/{id}      # Replace payment
PATCH  /payments/{id}      # Update payment
DELETE /payments/{id}      # Delete payment
```

### Nested Resources

```
GET    /users/{id}/payments          # User's payments
POST   /users/{id}/payments          # Create payment for user
GET    /users/{id}/payments/{pid}    # Specific payment
```

**Guideline**: Limit nesting to 2 levels maximum for clarity.

---

## Response Patterns

### Successful Responses

```json
// GET /users/usr_123
{
  "id": "usr_123",
  "email": "alice@example.com",
  "name": "Alice Johnson",
  "created_at": "2025-11-19T10:30:00Z"
}

// GET /users (collection)
{
  "data": [
    {"id": "usr_123", "email": "alice@example.com", ...},
    {"id": "usr_456", "email": "bob@example.com", ...}
  ],
  "has_more": false,
  "total_count": 2
}
```

### Error Responses

```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "value": "not-an-email"
    },
    "request_id": "req_abc123"
  }
}
```

---

## Pagination Patterns

### Cursor-Based (Recommended)

**Best for**: Large datasets, real-time data

```markdown
GET /payments?limit=20&starting_after=pmt_123

Response:
{
  "data": [...],
  "has_more": true,
  "next_cursor": "pmt_456"
}
```

### Offset-Based

**Best for**: Smaller datasets, random access needed

```markdown
GET /users?limit=20&offset=40

Response:
{
  "data": [...],
  "total": 156,
  "limit": 20,
  "offset": 40
}
```

---

**Version**: 1.0 (Summary)
**Full documentation**: See complete version in comprehensive standards.
