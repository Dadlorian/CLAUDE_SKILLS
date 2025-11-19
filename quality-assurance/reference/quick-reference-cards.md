# QA Quick Reference Cards

**Fast lookup for common testing scenarios, commands, and patterns**

---

## Test Commands Reference

### JavaScript/TypeScript (Jest/Playwright)

```bash
# Run all tests
npm test

# Run specific test file
npm test -- user.test.ts

# Run tests matching pattern
npm test -- --testNamePattern="login"

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm test -- --watch

# Run only changed tests
npm test -- --onlyChanged

# Update snapshots
npm test -- -u

# Run tests in specific directory
npm test -- tests/unit

# Run with specific reporter
npm test -- --reporter=verbose

# Debug tests
node --inspect-brk node_modules/.bin/jest --runInBand

# Playwright specific
npx playwright test                    # Run all E2E tests
npx playwright test --headed           # Show browser
npx playwright test --debug            # Debug mode
npx playwright test --ui               # Interactive UI mode
npx playwright test --project=chromium # Specific browser
npx playwright codegen                 # Generate tests
npx playwright show-report             # View HTML report
```

### Python (Pytest)

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_user.py

# Run specific test
pytest tests/test_user.py::test_login

# Run with markers
pytest -m smoke                        # Smoke tests only
pytest -m "not slow"                   # Exclude slow tests

# Run with coverage
pytest --cov=src --cov-report=html

# Run in parallel
pytest -n auto                         # Auto-detect CPUs
pytest -n 4                            # Use 4 workers

# Stop on first failure
pytest -x

# Verbose output
pytest -v

# Show print statements
pytest -s

# Rerun failed tests
pytest --lf                            # Last failed
pytest --ff                            # Failed first

# Generate HTML report
pytest --html=report.html
```

---

## Test Assertions Cheat Sheet

### Jest/TypeScript

```typescript
// Equality
expect(value).toBe(5)                  // Strict equality (===)
expect(value).toEqual({ a: 1 })        // Deep equality
expect(value).not.toBe(10)             // Negation

// Truthiness
expect(value).toBeTruthy()             // Boolean true
expect(value).toBeFalsy()              // Boolean false
expect(value).toBeNull()               // Null
expect(value).toBeUndefined()          // Undefined
expect(value).toBeDefined()            // Not undefined

// Numbers
expect(value).toBeGreaterThan(10)
expect(value).toBeGreaterThanOrEqual(10)
expect(value).toBeLessThan(20)
expect(value).toBeLessThanOrEqual(20)
expect(value).toBeCloseTo(0.3)         // Floating point

// Strings
expect(value).toMatch(/pattern/)
expect(value).toContain('substring')

// Arrays
expect(array).toContain('item')
expect(array).toHaveLength(5)
expect(array).toEqual(expect.arrayContaining(['a', 'b']))

// Objects
expect(obj).toHaveProperty('key')
expect(obj).toHaveProperty('key', 'value')
expect(obj).toMatchObject({ a: 1 })

// Exceptions
expect(() => func()).toThrow()
expect(() => func()).toThrow('error message')
expect(() => func()).toThrow(Error)

// Async
await expect(promise).resolves.toBe(value)
await expect(promise).rejects.toThrow()

// Mocks
expect(mockFn).toHaveBeenCalled()
expect(mockFn).toHaveBeenCalledTimes(2)
expect(mockFn).toHaveBeenCalledWith(arg1, arg2)
expect(mockFn).toHaveBeenLastCalledWith(arg)
```

### Playwright

```typescript
// Element visibility
await expect(page.locator('.element')).toBeVisible()
await expect(page.locator('.element')).toBeHidden()
await expect(page.locator('.element')).toBeAttached()

// Element state
await expect(page.locator('input')).toBeEnabled()
await expect(page.locator('input')).toBeDisabled()
await expect(page.locator('checkbox')).toBeChecked()
await expect(page.locator('input')).toBeFocused()

// Text content
await expect(page.locator('.title')).toHaveText('Hello')
await expect(page.locator('.title')).toContainText('Hell')
await expect(page.locator('input')).toHaveValue('test')

// Attributes
await expect(page.locator('a')).toHaveAttribute('href', '/home')
await expect(page.locator('div')).toHaveClass('active')
await expect(page.locator('div')).toHaveCSS('color', 'rgb(255, 0, 0)')

// Count
await expect(page.locator('li')).toHaveCount(5)

// URL
await expect(page).toHaveURL('https://example.com')
await expect(page).toHaveTitle('Page Title')
```

---

## HTTP Status Codes Quick Reference

### 2xx Success

```
200 OK                  - Successful GET, PUT, PATCH
201 Created             - Successful POST
202 Accepted            - Request accepted, processing async
204 No Content          - Successful DELETE, no response body
206 Partial Content     - Range request successful
```

### 3xx Redirection

```
301 Moved Permanently   - Resource permanently moved
302 Found               - Temporary redirect
304 Not Modified        - Cached version valid (ETag match)
307 Temporary Redirect  - Like 302 but preserve method
308 Permanent Redirect  - Like 301 but preserve method
```

### 4xx Client Errors

```
400 Bad Request         - Invalid syntax, validation error
401 Unauthorized        - Authentication required/failed
403 Forbidden           - Authenticated but not authorized
404 Not Found           - Resource doesn't exist
405 Method Not Allowed  - HTTP method not supported
406 Not Acceptable      - Cannot produce requested format
409 Conflict            - Resource conflict (duplicate)
410 Gone                - Resource permanently deleted
415 Unsupported Media   - Invalid Content-Type
422 Unprocessable       - Validation error (semantic)
429 Too Many Requests   - Rate limit exceeded
```

### 5xx Server Errors

```
500 Internal Server     - Generic server error
501 Not Implemented     - Method not implemented
502 Bad Gateway         - Invalid response from upstream
503 Service Unavailable - Server overloaded/down
504 Gateway Timeout     - Upstream timeout
```

---

## Test Data Patterns

### Valid Test Data

```typescript
const validUser = {
  email: 'test@example.com',
  password: 'SecurePass123!',
  firstName: 'John',
  lastName: 'Doe',
  age: 25,
  phone: '+1-555-123-4567'
};

const validAddress = {
  street: '123 Main St',
  city: 'San Francisco',
  state: 'CA',
  zipCode: '94102',
  country: 'USA'
};

const validCreditCard = {
  number: '4532015112830366',        // Test Visa
  cvv: '123',
  expiry: '12/25'
};
```

### Invalid Test Data

```typescript
// Email validation
const invalidEmails = [
  '',                                  // Empty
  'invalid',                          // No @
  'test@',                            // No domain
  '@example.com',                     // No local part
  'test user@example.com',            // Space
  'test@@example.com',                // Double @
];

// Password validation  
const weakPasswords = [
  '',                                  // Empty
  '123',                              // Too short
  'password',                         // No numbers/special
  'PASSWORD',                         // No lowercase
  'password123',                      // No uppercase/special
];

// Age validation
const invalidAges = [
  -1,                                  // Negative
  0,                                   // Zero (depends on context)
  17,                                  // Below minimum (18)
  121,                                 // Above maximum (120)
  25.5,                               // Decimal (if int required)
  'twenty-five',                      // String
];
```

### Boundary Values

```typescript
// String length (3-20 characters)
const stringBoundaries = [
  'AB',                               // Below min (2)
  'ABC',                              // Min boundary (3)
  'ABCD',                             // Just above min (4)
  'A'.repeat(19),                     // Just below max
  'A'.repeat(20),                     // Max boundary
  'A'.repeat(21),                     // Above max
];

// Numeric range (0-100)
const numericBoundaries = [
  -1,                                 // Below min
  0,                                  // Min boundary
  1,                                  // Just above min
  50,                                 // Middle
  99,                                 // Just below max
  100,                                // Max boundary
  101,                                // Above max
];
```

---

## Common Selectors

### CSS Selectors

```css
/* By ID */
#header

/* By class */
.button

/* By attribute */
[data-testid="submit-btn"]
[type="email"]
[href^="https"]                      /* Starts with */
[href$=".pdf"]                       /* Ends with */
[class*="active"]                    /* Contains */

/* Combinators */
div > p                              /* Direct child */
div p                                /* Descendant */
div + p                              /* Adjacent sibling */
div ~ p                              /* General sibling */

/* Pseudo-classes */
:first-child
:last-child
:nth-child(2)
:nth-of-type(2)
:not(.disabled)
:hover
:focus
```

### XPath Selectors

```xpath
/* By ID */
//*[@id="header"]

/* By class */
//*[@class="button"]

/* By text */
//button[text()="Submit"]
//button[contains(text(), "Sub")]

/* By attribute */
//*[@data-testid="submit-btn"]
//*[@type="email"]

/* Axes */
//div/following-sibling::p
//div/preceding-sibling::p
//div/ancestor::form
//div/descendant::button

/* Conditions */
//button[@class="primary" and @type="submit"]
//button[@class="primary" or @class="secondary"]
```

---

## Performance Testing Metrics

### Response Time Percentiles

```
p50 (median)    - 50% of requests faster than this
p75             - 75% of requests faster than this
p90             - 90% of requests faster than this
p95             - 95% of requests faster than this
p99             - 99% of requests faster than this
p99.9           - 99.9% of requests faster than this

Example:
p50:  200ms     - Half of users experience <200ms
p95:  500ms     - 95% of users experience <500ms
p99:  1000ms    - 99% of users experience <1s
```

### Throughput Metrics

```
RPS   - Requests Per Second
TPS   - Transactions Per Second
QPM   - Queries Per Minute
CCU   - Concurrent Users

Example Load Test:
100 CCU × 10 requests/user/min = 1000 QPM = 16.7 RPS
```

### Apdex Score

```
Apdex = (Satisfied + (Tolerating / 2)) / Total Samples

Satisfied:   Response time ≤ T
Tolerating:  Response time > T and ≤ 4T
Frustrated:  Response time > 4T

Example (T = 500ms):
Satisfied:   ≤ 500ms
Tolerating:  501ms - 2000ms
Frustrated:  > 2000ms

Score:
1.0     - Excellent
0.94    - Good
0.85    - Fair
0.7     - Poor
< 0.5   - Unacceptable
```

---

## Security Testing Checklist

### OWASP Top 10 Quick Check

```
A01: Broken Access Control
  ✓ Test unauthorized access to resources
  ✓ Test privilege escalation
  ✓ Test IDOR (change IDs in URLs)

A02: Cryptographic Failures
  ✓ Check HTTPS everywhere
  ✓ Verify sensitive data encrypted
  ✓ Test password storage (hashed)

A03: Injection
  ✓ SQL injection: ' OR '1'='1
  ✓ XSS: <script>alert('XSS')</script>
  ✓ Command injection: ; ls -la

A04: Insecure Design
  ✓ Review threat model
  ✓ Check security requirements
  ✓ Verify secure design patterns

A05: Security Misconfiguration
  ✓ Default credentials removed
  ✓ Unnecessary features disabled
  ✓ Error messages not verbose

A06: Vulnerable Components
  ✓ npm audit / pip-audit
  ✓ Dependencies up to date
  ✓ No EOL libraries

A07: Authentication Failures
  ✓ Password complexity enforced
  ✓ Account lockout implemented
  ✓ MFA available
  ✓ Session management secure

A08: Integrity Failures
  ✓ CI/CD pipeline secure
  ✓ Code signing implemented
  ✓ Deserialization safe

A09: Logging Failures
  ✓ Security events logged
  ✓ Logs monitored
  ✓ Alerts configured

A10: SSRF
  ✓ URL validation implemented
  ✓ Internal network protected
  ✓ Whitelist allowed hosts
```

---

## Git Commands for QA

```bash
# Create feature branch
git checkout -b test/user-authentication

# Stash changes
git stash
git stash pop

# View changes
git diff
git diff --staged

# Commit
git add .
git commit -m "test: add user authentication tests"

# Push
git push origin test/user-authentication

# Update branch with main
git checkout main
git pull
git checkout test/user-authentication
git rebase main

# Reset changes
git reset --hard HEAD    # Discard all changes
git reset --soft HEAD~1  # Undo last commit, keep changes

# Cherry-pick commit
git cherry-pick <commit-hash>
```

---

## Regex Patterns for Testing

```regex
# Email
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$

# Phone (US)
^\+?1?[-.\s]?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}$

# URL
^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b

# Credit Card (Visa)
^4[0-9]{12}(?:[0-9]{3})?$

# Credit Card (MasterCard)
^5[1-5][0-9]{14}$

# Date (YYYY-MM-DD)
^\d{4}-\d{2}-\d{2}$

# Time (HH:MM)
^([01]\d|2[0-3]):([0-5]\d)$

# IPv4
^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$

# Password (8+ chars, upper, lower, number, special)
^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$
```

---

## Environment Variables

```bash
# Test environment
NODE_ENV=test
PLAYWRIGHT_BROWSER=chromium
JEST_TIMEOUT=30000

# API endpoints
API_URL=https://api-staging.example.com
API_KEY=test_key_12345

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=test_db
DB_USER=test_user
DB_PASSWORD=test_pass

# Feature flags
FEATURE_NEW_CHECKOUT=true
FEATURE_AB_TEST=false

# CI/CD
CI=true
GITHUB_ACTIONS=true
```

---

## Docker Commands for Testing

```bash
# Run tests in container
docker-compose run --rm test npm test

# Start test database
docker-compose up -d postgres

# View logs
docker-compose logs -f test

# Clean up
docker-compose down -v

# Build test image
docker build -t myapp-test -f Dockerfile.test .

# Run specific test
docker run --rm myapp-test npm test -- user.test.ts

# Interactive shell
docker-compose run --rm test bash
```

---

**Quick Reference Version**: 1.0
**Last Updated**: 2025-11-19
