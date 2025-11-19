# Production-Ready API Client Examples

This directory contains comprehensive, production-ready API client implementations in multiple programming languages. Each client demonstrates best practices for API interaction including OAuth2 authentication, error handling, retry logic, and rate limiting.

## Overview

All clients implement the same core functionality:

- **OAuth2 Client Credentials Flow** - Secure authentication
- **Retry Logic with Exponential Backoff** - Resilient request handling
- **Comprehensive Error Handling** - Graceful failure scenarios
- **Request/Response Logging** - Debugging and monitoring
- **Rate Limit Headers** - Response header parsing
- **Connection Pooling** - Efficient resource usage
- **Timeout Configuration** - Preventing hanging requests
- **Type Safety** - Language-appropriate type handling

## Quick Start

### Python

```bash
pip install requests pydantic
python python_client.py
```

**Key Features:**
- Context manager support for resource cleanup
- Automatic retry strategy with `requests.adapters.Retry`
- Type hints for better IDE support
- Specialized client classes for domain-specific operations

**File:** `python_client.py` (425 lines)

### Ruby

```bash
gem install httpclient
ruby ruby_client.rb
```

**Key Features:**
- Thread-safe HTTP client
- Flexible request/response handling
- Exception-based error handling
- Time-based token expiration tracking

**File:** `ruby_client.rb` (398 lines)

### Go

```bash
go run go_client.go
```

**Key Features:**
- Concurrent request handling
- Custom backoff strategy
- Efficient error management
- Minimal dependencies (standard library only)

**File:** `go_client.go` (445 lines)

### Java

```bash
javac JavaAPIClient.java
java JavaAPIClient
```

**Requires:**
- Java 11+
- Gson library for JSON handling

**Key Features:**
- Type-safe API interactions
- HTTP/2 support via HttpClient
- Comprehensive logging
- Extensible design patterns

**File:** `JavaAPIClient.java` (512 lines)

## Core Components

### OAuth2Client

Handles OAuth2 authentication using the Client Credentials flow:

```python
oauth2 = OAuth2Client(config)
oauth2.get_token('https://auth.example.com/oauth/token', ['scope1', 'scope2'])
```

**Responsibilities:**
- Token acquisition
- Token refresh
- Token expiration tracking
- Secure credential storage

### APIClient

Main client for making HTTP requests:

```python
api_client = APIClient(config, oauth2)
response = api_client.get('/users', params={'page': 1})
```

**Capabilities:**
- HTTP method support (GET, POST, PATCH, DELETE)
- Query parameter handling
- JSON payload encoding/decoding
- Error response handling
- Automatic token refresh
- Retry with exponential backoff

### Specialized Clients

Domain-specific client implementations:

```python
user_client = UserClient(api_client)
users = user_client.list_users(page=1, limit=10)
user = user_client.get_user('123')
```

## Configuration

All clients accept configuration via a config object:

```python
config = APIConfig(
    base_url='https://api.example.com/v1',
    client_id='your-client-id',
    client_secret='your-client-secret',
    timeout=30,
    max_retries=3,
    backoff_factor=0.5,
    verify_ssl=True
)
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| base_url | string | Required | API base URL |
| client_id | string | Required | OAuth2 client ID |
| client_secret | string | Required | OAuth2 client secret |
| timeout | int | 30 | Request timeout in seconds |
| max_retries | int | 3 | Maximum retry attempts |
| backoff_factor | float | 0.5 | Exponential backoff factor |
| verify_ssl | bool | true | SSL certificate verification |

## Error Handling

All clients handle common HTTP errors gracefully:

```python
try:
    user = api_client.get('/users/123')
except ValueError as e:
    if 'Unauthorized' in str(e):
        # Handle authentication failure
    elif 'not found' in str(e):
        # Handle missing resource
    else:
        # Handle other errors
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Error: {e}")
```

### Error Codes and Handling

| Status | Error | Action |
|--------|-------|--------|
| 401 | Unauthorized | Refresh token or re-authenticate |
| 403 | Forbidden | Check permissions/scopes |
| 404 | Not Found | Verify endpoint and parameters |
| 429 | Rate Limited | Implement backoff/retry |
| 5xx | Server Error | Retry with exponential backoff |

## Rate Limiting

All clients respect HTTP rate limit headers:

```python
response = api_client.get('/users')
# Response headers include:
# X-RateLimit-Limit: 1000
# X-RateLimit-Remaining: 999
# X-RateLimit-Reset: 2024-11-19T08:00:00Z
```

**Handling Rate Limits:**
1. Check `X-RateLimit-Remaining` before making requests
2. Implement exponential backoff when limited
3. Parse `X-RateLimit-Reset` for retry timing

## Retry Strategy

All clients implement exponential backoff:

```
Attempt 1: 0.5s delay
Attempt 2: 1s delay
Attempt 3: 2s delay
Attempt 4: 4s delay
Attempt 5: 8s delay
```

**Retryable Status Codes:**
- 429 (Rate Limited)
- 500-599 (Server Errors)

**Non-Retryable Status Codes:**
- 401 (Authentication)
- 403 (Authorization)
- 404 (Not Found)
- 4xx (Client Errors)

## Security Considerations

### Credential Management

- Never hardcode credentials in source code
- Use environment variables for sensitive data
- Implement secure credential storage
- Rotate secrets regularly

```python
import os

config = APIConfig(
    base_url=os.getenv('API_BASE_URL'),
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET')
)
```

### SSL/TLS

All clients support HTTPS with certificate verification:

```python
config = APIConfig(
    ...
    verify_ssl=True  # Enable SSL verification (default)
)
```

### Token Security

- Tokens are stored in memory only
- No token caching to disk
- Automatic expiration tracking
- Immediate revocation on error

## Testing

### Unit Testing Example (Python)

```python
import unittest
from unittest.mock import Mock, patch

class TestAPIClient(unittest.TestCase):
    def setUp(self):
        self.config = APIConfig(
            base_url='https://api.example.com',
            client_id='test',
            client_secret='test'
        )
        self.client = APIClient(self.config)

    @patch('requests.post')
    def test_post_user(self, mock_post):
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {'id': '123'}

        result = self.client.post('/users', {'name': 'John'})
        self.assertEqual(result['id'], '123')
```

### Integration Testing

```python
# Using real credentials (test environment only)
oauth2 = OAuth2Client(config)
oauth2.get_token(auth_endpoint, ['test.read', 'test.write'])

api_client = APIClient(config, oauth2)
response = api_client.get('/health')
assert response.status_code == 200
```

## Performance Considerations

### Connection Pooling

All clients use connection pooling for efficiency:

**Python:** HTTPAdapter with pooling
**Ruby:** HTTPClient with persistent connections
**Go:** HTTP Client with built-in pooling
**Java:** HttpClient with connection pool

### Timeouts

Configure appropriate timeouts for your use case:

```python
# Short timeout for health checks
config = APIConfig(..., timeout=5)

# Longer timeout for file uploads
config = APIConfig(..., timeout=300)
```

### Memory Usage

- Token storage is minimal (typically < 1KB)
- Session cleanup is automatic
- No persistent caching by default
- Memory-efficient streaming for large responses

## Migration Guide

### From Older Clients

```python
# Old way
response = requests.get('https://api.example.com/v1/users')

# New way with client
api_client = APIClient(config, oauth2)
response = api_client.get('/users')
```

### Adding to Existing Projects

1. Copy client file to your project
2. Update imports and dependencies
3. Initialize with configuration
4. Replace direct HTTP calls with client methods
5. Test thoroughly in development environment

## Troubleshooting

### Authentication Failures

```python
# Check credentials
if oauth2.is_token_expired():
    oauth2.refresh(auth_endpoint)

# Verify scopes
oauth2.get_token(auth_endpoint, ['required.scope'])
```

### Connection Timeouts

```python
# Increase timeout
config = APIConfig(..., timeout=60)

# Check network connectivity
import socket
socket.create_connection(('api.example.com', 443), timeout=10)
```

### Rate Limiting

```python
# Implement backoff
time.sleep(60)  # Wait 60 seconds
response = api_client.get('/users')

# Check remaining requests
remaining = response.headers.get('X-RateLimit-Remaining')
if int(remaining) < 10:
    # Wait before next request
    time.sleep(30)
```

## Examples

### Complete User Management Workflow

```python
# Python example
config = APIConfig(
    base_url='https://api.example.com/v1',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET')
)

oauth2 = OAuth2Client(config)
oauth2.get_token('https://auth.example.com/oauth/token', ['users.manage'])

with APIClient(config, oauth2) as api_client:
    user_client = UserClient(api_client)

    # Create user
    new_user = user_client.create_user({
        'firstName': 'John',
        'lastName': 'Doe',
        'email': 'john@example.com'
    })
    user_id = new_user['id']

    # Get user
    user = user_client.get_user(user_id)

    # Update user
    updated = user_client.update_user(user_id, {
        'phone': '+1-555-0100'
    })

    # List users
    users = user_client.list_users(page=1, limit=10)

    # Delete user
    user_client.delete_user(user_id)
```

## Best Practices

1. **Always use context managers** to ensure proper cleanup
2. **Implement exponential backoff** for retries
3. **Log all requests/responses** for debugging
4. **Validate responses** before processing
5. **Handle timeouts gracefully** with appropriate messages
6. **Never commit credentials** to version control
7. **Use type hints** for better IDE support
8. **Test with real API** before production
9. **Monitor error rates** and implement alerting
10. **Document API behavior** specific to your implementation

## Contributing

To add a new client implementation:

1. Follow the established patterns
2. Implement all core functionality (OAuth2, retries, etc.)
3. Add comprehensive error handling
4. Include logging and debugging support
5. Write example usage code
6. Update this README

## License

These examples are provided for reference and educational purposes. Adapt them to your specific needs and security requirements.

## Support

For issues or questions:
1. Check the examples in each language file
2. Review the error handling sections
3. Examine the Postman collection for API structure
4. Refer to the OpenAPI specification

## Additional Resources

- OpenAPI Specification: `openapi-complete-example.yaml`
- Postman Collection: `postman-collection.json`
- Authentication Examples: `../authentication-examples.js`
- Rate Limiting: `../rate-limiting-middleware.js`
- Webhook Handler: `../webhook-handler.py`
