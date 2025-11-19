---
sidebar_position: 3
title: Error Codes
description: Complete error code reference
---

# Error Codes

Reference of all error codes returned by the Project API.

## HTTP Status Codes

| Status | Code | Description |
|--------|------|-------------|
| 200 | OK | Request successful |
| 201 | CREATED | Resource created |
| 400 | BAD_REQUEST | Invalid request |
| 401 | UNAUTHORIZED | Invalid API key |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 429 | RATE_LIMITED | Too many requests |
| 500 | SERVER_ERROR | Internal server error |

## Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {
      "field": "Additional context"
    }
  }
}
```

## Common Errors

### INVALID_REQUEST
Missing or invalid parameters

### AUTHENTICATION_FAILED
Invalid or expired API key

### RESOURCE_NOT_FOUND
The requested resource doesn't exist

### RATE_LIMITED
Too many requests - try again later
