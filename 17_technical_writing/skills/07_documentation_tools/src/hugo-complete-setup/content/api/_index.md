---
title: "API Reference"
description: "Complete API documentation"
weight: 2
---

# API Reference

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
    "name": "John Doe"
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Rate Limits

- 1,000 requests per minute per API key
- 10,000 requests per hour per API key

## API Endpoints

- [Users]({{< ref "users" >}}) - User management
- [Projects]({{< ref "projects" >}}) - Project management
- [Error Codes]({{< ref "errors" >}}) - Error reference

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
