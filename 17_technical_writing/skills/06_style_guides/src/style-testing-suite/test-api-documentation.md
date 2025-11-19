# Test: API Documentation Standards

## Purpose

Validate consistent API documentation patterns and completeness.

## Passing Examples

### Complete Endpoint Documentation

## GET /api/users

Retrieve a list of all users in the system.

### Request

```bash
curl -X GET https://api.example.com/api/users \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Parameters

- `page` (integer, optional) - Page number (default: 1)
- `limit` (integer, optional) - Results per page (default: 20)
- `filter` (string, optional) - Filter by name or email

### Response

**Status Code:** 200 OK

```json
{
  "data": [
    {
      "id": "user123",
      "name": "John Doe",
      "email": "john@example.com",
      "created_at": "2023-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150
  }
}
```

### Error Handling

**Status Code:** 401 Unauthorized

```json
{
  "error": "Invalid or missing authentication token",
  "code": "AUTH_FAILED"
}
```

**Status Code:** 429 Too Many Requests

```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

### Example Usage

```javascript
const response = await fetch('https://api.example.com/api/users', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  }
});

const data = await response.json();
console.log(data);
```

## Failing Examples

### Incomplete Endpoint Documentation

## GET /api/users

Get users.

This documentation is incomplete.

### Missing Response Example

## POST /api/users

Create a new user.

**Request Parameters:**
- name: User's full name
- email: User's email address

No response example provided.

### Unclear Error Documentation

Errors may occur.

Bad request if validation fails.

Authentication may fail.

### Inconsistent HTTP Methods

```bash
POST /api/users
curl /api/users -X GET
```

Mixed notation for HTTP methods.

### Missing Parameter Documentation

## DELETE /api/users/{id}

Delete a user.

The endpoint requires an ID but doesn't document parameter details.

## Notes

API documentation must include:
- HTTP method (GET, POST, PUT, DELETE)
- Complete endpoint path
- Request parameters/body
- Response examples
- Error codes and messages
- Authentication requirements
- Code examples in multiple languages

## Related Rules

- TechWriter.CommandFormatting - Command syntax
- TechWriter.CodeFormatting - Code block standards
- TechWriter.MetaInformation - Documentation requirements
