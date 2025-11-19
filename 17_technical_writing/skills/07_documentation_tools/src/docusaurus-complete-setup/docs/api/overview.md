---
sidebar_position: 1
title: API Overview
description: Project API documentation
---

# API Overview

The Project API provides RESTful and GraphQL interfaces for integrating with our platform.

## Base URL

```
https://api.example.com/v1
```

## Authentication

All API requests require an API key:

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
    "name": "John Doe"
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Rate Limits

- 1000 requests per minute per API key
- 10000 requests per hour per API key

## API Endpoints

### Users
- `GET /users` - List users
- `POST /users` - Create user
- `GET /users/:id` - Get user
- `PUT /users/:id` - Update user
- `DELETE /users/:id` - Delete user

### Projects
- `GET /projects` - List projects
- `POST /projects` - Create project
- `GET /projects/:id` - Get project
- `PUT /projects/:id` - Update project
- `DELETE /projects/:id` - Delete project

## Error Handling

Errors are returned with appropriate HTTP status codes:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required field: name"
  }
}
```

See [Error Codes](./errors.md) for details.
