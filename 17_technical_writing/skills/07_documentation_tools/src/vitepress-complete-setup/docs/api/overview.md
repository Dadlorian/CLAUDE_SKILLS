# API Overview

The Project API provides RESTful endpoints for all platform operations.

## Base URL

```
https://api.example.com/v1
```

## Authentication

Include your API key in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.example.com/v1/users
```

## Response Format

All responses are JSON:

```json
{
  "data": {
    "id": "user_123",
    "name": "John Doe"
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Rate Limits

- 1,000 requests per minute
- 10,000 requests per hour
- 100,000 requests per day

## Error Handling

Errors include appropriate HTTP status codes:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required field: name"
  }
}
```

## API Endpoints

### Users

- `GET /users` - List users
- `POST /users` - Create user
- `GET /users/{id}` - Get user
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

### Projects

- `GET /projects` - List projects
- `POST /projects` - Create project
- `GET /projects/{id}` - Get project
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

## See Also

- [Users Endpoint](/api/users)
- [Projects Endpoint](/api/projects)
- [Error Codes](/api/errors)
