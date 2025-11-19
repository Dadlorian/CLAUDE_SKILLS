# API Testing Best Practices

## Test Coverage

### DO ✅
- Test all HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Test all status codes (2xx, 4xx, 5xx)
- Test authentication and authorization
- Test input validation
- Test error scenarios

### DON'T ❌
- Only test happy path
- Skip authentication tests
- Ignore error handling
- Test only 200 responses
- Forget edge cases

## Request/Response Validation

### DO ✅
- Validate response status code
- Validate response schema
- Validate response headers
- Check response time
- Verify data types

### DON'T ❌
- Only check status code
- Skip schema validation
- Ignore headers
- Allow slow responses
- Assume data types

## Security Testing

### DO ✅
- Test SQL injection
- Test XSS prevention
- Test CSRF protection
- Test rate limiting
- Test authentication bypass

### DON'T ❌
- Skip security tests
- Trust user input
- Expose sensitive data
- Allow unlimited requests
- Ignore OWASP Top 10
