# API Overview

The Project API provides RESTful and GraphQL interfaces for integrating with our platform.

## Base URL

```
https://api.example.com/v1
```

## Authentication

All API requests require an API key in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.example.com/v1/users
```

## Response Format

All responses are in JSON format:

```json
{
  "data": {
    "id": "user_123",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "v1"
  }
}
```

## Rate Limits

- 1,000 requests per minute per API key
- 10,000 requests per hour per API key
- 100,000 requests per day per API key

Rate limit information is included in response headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642262400
```

## Pagination

List endpoints support pagination:

```bash
GET /users?page=1&limit=20
```

## Filtering

Filter results using query parameters:

```bash
GET /users?name=John&email=john@example.com
```

## Sorting

Sort results using the `sort` parameter:

```bash
GET /users?sort=createdAt:-1
```

## Error Handling

Errors are returned with appropriate HTTP status codes and error details:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required field: name",
    "details": {
      "field": "name",
      "value": null
    }
  }
}
```

See [Error Codes](errors.md) for complete reference.

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
