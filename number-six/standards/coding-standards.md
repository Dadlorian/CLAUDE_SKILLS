# Coding Standards
## Elite Professional Development Standards

### Philosophy

These standards synthesize best practices from:
- **Google Style Guides** - Industry-leading code style
- **Airbnb JavaScript Style Guide** - Community-vetted standards
- **Microsoft Framework Design Guidelines** - Enterprise patterns
- **Clean Code by Robert C. Martin** - Fundamental principles
- **OWASP** - Security best practices

---

## Core Principles

### 1. Readability First
**Standard**: Code is read 10x more than it's written
- Optimize for the reader, not the writer
- Use descriptive names over clever brevity
- Favor clarity over performance (unless profiling proves otherwise)
- Reference: "Clean Code" by Robert C. Martin

### 2. Security by Design
**Standard**: Security is not a feature, it's a requirement
- Input validation at all boundaries
- Principle of least privilege
- Defense in depth
- Regular security audits
- Reference: OWASP Top 10, CWE Top 25

### 3. Testability
**Standard**: Untested code is broken code
- Minimum 80% code coverage
- Test-driven development (TDD) encouraged
- Unit, integration, and E2E tests
- Reference: "Growing Object-Oriented Software, Guided by Tests"

### 4. Maintainability
**Standard**: Code should be easy to modify
- Single Responsibility Principle
- Don't Repeat Yourself (DRY)
- YAGNI (You Aren't Gonna Need It)
- Reference: "Refactoring" by Martin Fowler

---

## Language-Specific Standards

### JavaScript/TypeScript

**File Structure**:
```typescript
// 1. Imports (grouped and sorted)
import { External } from 'external-package';
import { Internal } from '@/internal';
import type { Types } from './types';

// 2. Constants
const MAX_RETRIES = 3;

// 3. Types/Interfaces
interface UserData {
  id: string;
  name: string;
}

// 4. Main code
export function processUser(data: UserData): void {
  // Implementation
}

// 5. Helper functions (not exported)
function validateUser(data: UserData): boolean {
  // Implementation
}
```

**Naming Conventions**:
```typescript
// Classes: PascalCase
class UserRepository {}

// Functions/Variables: camelCase
const userName = 'John';
function getUserData() {}

// Constants: SCREAMING_SNAKE_CASE
const API_BASE_URL = 'https://api.example.com';

// Interfaces: PascalCase with 'I' prefix (optional, team decision)
interface IUserService {} // or just UserService

// Types: PascalCase
type UserId = string;

// Enums: PascalCase for enum, SCREAMING_SNAKE_CASE for values
enum UserRole {
  ADMIN = 'ADMIN',
  USER = 'USER',
}

// Private properties: underscore prefix
class User {
  private _password: string;
}
```

**Function Standards**:
```typescript
// ✅ GOOD: Clear, single responsibility
function calculateTotalPrice(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// ❌ BAD: Doing too much
function handleCheckout(items: CartItem[], user: User) {
  // Calculate price
  // Validate payment
  // Update inventory
  // Send email
  // Log analytics
}

// ✅ GOOD: Descriptive boolean names
function isUserAuthenticated(): boolean {}
function hasPermission(): boolean {}
function canEditPost(): boolean {}

// ❌ BAD: Vague names
function check(): boolean {}
function verify(): boolean {}
```

**Error Handling**:
```typescript
// ✅ GOOD: Specific error types
class ValidationError extends Error {
  constructor(public field: string, message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

// ✅ GOOD: Handle all cases
async function fetchUserData(id: string): Promise<User> {
  try {
    const response = await api.get(`/users/${id}`);
    return response.data;
  } catch (error) {
    if (error instanceof NetworkError) {
      logger.error('Network failure', { error, userId: id });
      throw new UserFetchError('Unable to connect to server');
    }
    throw error; // Re-throw unknown errors
  }
}

// ❌ BAD: Silent failures
async function fetchUserData(id: string) {
  try {
    return await api.get(`/users/${id}`);
  } catch (error) {
    return null; // Lost error context!
  }
}
```

**Comments**:
```typescript
// ✅ GOOD: Explain WHY, not WHAT
// Using quadratic probing to reduce clustering
// Reference: Knuth TAOCP Vol 3, Section 6.4
const nextIndex = (index + i * i) % tableSize;

// ✅ GOOD: Document complex algorithms
/**
 * Implements exponential backoff with jitter for retry logic
 * Based on AWS Architecture Blog best practices
 * @param attempt - Current retry attempt (0-indexed)
 * @returns Delay in milliseconds
 */
function calculateBackoff(attempt: number): number {
  const baseDelay = 100;
  const maxDelay = 30000;
  const exponentialDelay = Math.min(baseDelay * 2 ** attempt, maxDelay);
  const jitter = Math.random() * 0.3 * exponentialDelay;
  return exponentialDelay + jitter;
}

// ❌ BAD: Stating the obvious
// Increment i by 1
i++;

// ❌ BAD: Commented-out code
// const oldImplementation = () => { ... }
```

**TypeScript Specifics**:
```typescript
// ✅ GOOD: Use strict mode
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}

// ✅ GOOD: Prefer type inference
const users = await getUsers(); // Type inferred

// ✅ GOOD: Use unknown instead of any
function parseJSON(input: string): unknown {
  return JSON.parse(input);
}

// ✅ GOOD: Discriminated unions for complex types
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: string };

// ❌ BAD: Disabling TypeScript
// @ts-ignore
const value = dangerousOperation();
```

---

### Python

**File Structure**:
```python
"""Module docstring explaining purpose."""

# 1. Imports (grouped: standard library, third-party, local)
import os
from typing import List, Optional

import requests
from pydantic import BaseModel

from .utils import helper_function

# 2. Constants
MAX_RETRIES = 3
API_BASE_URL = "https://api.example.com"

# 3. Classes
class UserService:
    """Service for user operations."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def get_user(self, user_id: str) -> Optional[dict]:
        """Retrieve user by ID."""
        pass

# 4. Functions
def process_users(users: List[dict]) -> List[dict]:
    """Process list of users."""
    pass
```

**Naming Conventions**:
```python
# Classes: PascalCase
class UserRepository:
    pass

# Functions/Variables: snake_case
user_name = "John"
def get_user_data():
    pass

# Constants: SCREAMING_SNAKE_CASE
API_BASE_URL = "https://api.example.com"

# Private: leading underscore
class User:
    def __init__(self):
        self._password = None

    def _validate(self):
        pass

# "Magic" methods: double underscore
def __str__(self):
    pass
```

**Type Hints (PEP 484)**:
```python
from typing import List, Dict, Optional, Union, Callable

# ✅ GOOD: Always use type hints
def calculate_total(prices: List[float]) -> float:
    return sum(prices)

def find_user(user_id: str) -> Optional[User]:
    """Returns User or None if not found."""
    pass

# ✅ GOOD: Complex types
def process_data(
    data: Dict[str, Union[int, str]],
    callback: Callable[[str], None]
) -> List[str]:
    pass

# Use from __future__ import annotations for forward references
from __future__ import annotations

class Node:
    def __init__(self, parent: Optional[Node] = None):
        self.parent = parent
```

**Docstrings (Google Style)**:
```python
def fetch_user_data(user_id: str, include_posts: bool = False) -> dict:
    """Fetch user data from the API.

    Args:
        user_id: The unique identifier for the user.
        include_posts: Whether to include user's posts in the response.
            Defaults to False.

    Returns:
        A dictionary containing user data with keys:
            - id: User's unique identifier
            - name: User's full name
            - posts: List of posts (if include_posts=True)

    Raises:
        UserNotFoundError: If user_id doesn't exist.
        APIError: If the API request fails.

    Example:
        >>> user = fetch_user_data("123", include_posts=True)
        >>> print(user['name'])
        'John Doe'
    """
    pass
```

---

### Go

**File Structure**:
```go
// Package documentation
package user

import (
    // Standard library
    "context"
    "fmt"

    // Third-party
    "github.com/pkg/errors"

    // Internal
    "myapp/internal/db"
)

// Constants
const (
    MaxRetries = 3
    DefaultTimeout = 30 * time.Second
)

// Types
type UserService struct {
    db *db.Client
}

// Functions
func NewUserService(db *db.Client) *UserService {
    return &UserService{db: db}
}
```

**Naming Conventions**:
```go
// Exported (public): PascalCase
type UserService struct {}
func GetUser() {}

// Unexported (private): camelCase
type userRepository struct {}
func validateInput() {}

// Acronyms: All caps if exported, lowercase if not
type HTTPServer struct {} // Exported
type xmlParser struct {}  // Unexported

// Interface names: -er suffix
type Reader interface {
    Read(p []byte) (n int, err error)
}
```

**Error Handling**:
```go
// ✅ GOOD: Return errors, don't panic
func GetUser(id string) (*User, error) {
    user, err := db.Query(id)
    if err != nil {
        return nil, fmt.Errorf("failed to get user %s: %w", id, err)
    }
    return user, nil
}

// ✅ GOOD: Wrap errors with context
import "github.com/pkg/errors"

func ProcessUser(id string) error {
    user, err := GetUser(id)
    if err != nil {
        return errors.Wrap(err, "processing user")
    }
    // ...
}

// ✅ GOOD: Custom error types
type ValidationError struct {
    Field string
    Msg   string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed for %s: %s", e.Field, e.Msg)
}
```

---

## Security Standards

### Input Validation

```typescript
// ✅ GOOD: Validate all inputs
function createUser(email: string, password: string): User {
  // Validate email format
  if (!isValidEmail(email)) {
    throw new ValidationError('email', 'Invalid email format');
  }

  // Validate password strength
  if (password.length < 12) {
    throw new ValidationError('password', 'Password must be at least 12 characters');
  }

  // Sanitize inputs
  const sanitizedEmail = sanitizeEmail(email);

  // Use parameterized queries (prevent SQL injection)
  return db.query(
    'INSERT INTO users (email, password) VALUES ($1, $2)',
    [sanitizedEmail, hashPassword(password)]
  );
}

// ❌ BAD: No validation, SQL injection risk
function createUser(email: string, password: string) {
  return db.query(`INSERT INTO users VALUES ('${email}', '${password}')`);
}
```

### Authentication & Authorization

```typescript
// ✅ GOOD: Use established libraries
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';

async function hashPassword(password: string): Promise<string> {
  const saltRounds = 12; // OWASP recommendation
  return bcrypt.hash(password, saltRounds);
}

// ✅ GOOD: Verify permissions
async function deletePost(postId: string, userId: string): Promise<void> {
  const post = await getPost(postId);

  if (post.authorId !== userId && !isAdmin(userId)) {
    throw new UnauthorizedError('Cannot delete post');
  }

  await db.deletePost(postId);
}
```

### Secrets Management

```typescript
// ✅ GOOD: Use environment variables
const apiKey = process.env.API_KEY;
if (!apiKey) {
  throw new Error('API_KEY environment variable is required');
}

// ✅ GOOD: Never log sensitive data
logger.info('User logged in', { userId: user.id }); // ✅
logger.info('User logged in', { password: user.password }); // ❌

// ✅ GOOD: Use secrets management services
import { SecretsManager } from '@aws-sdk/client-secrets-manager';

async function getApiKey(): Promise<string> {
  const secret = await secretsManager.getSecretValue({
    SecretId: 'prod/api-key',
  });
  return secret.SecretString;
}
```

---

## Testing Standards

### Unit Tests

```typescript
// ✅ GOOD: Descriptive test names
describe('calculateTotalPrice', () => {
  it('should return 0 for empty cart', () => {
    expect(calculateTotalPrice([])).toBe(0);
  });

  it('should sum all item prices', () => {
    const items = [
      { price: 10, quantity: 2 },
      { price: 5, quantity: 1 },
    ];
    expect(calculateTotalPrice(items)).toBe(25);
  });

  it('should throw error for negative prices', () => {
    const items = [{ price: -10, quantity: 1 }];
    expect(() => calculateTotalPrice(items)).toThrow(ValidationError);
  });
});

// ✅ GOOD: AAA pattern (Arrange, Act, Assert)
it('should update user email', async () => {
  // Arrange
  const user = await createTestUser();
  const newEmail = 'newemail@example.com';

  // Act
  await updateUserEmail(user.id, newEmail);

  // Assert
  const updatedUser = await getUser(user.id);
  expect(updatedUser.email).toBe(newEmail);
});
```

### Test Coverage

```yaml
# Minimum thresholds (enforce in CI)
coverage:
  global:
    statements: 80%
    branches: 75%
    functions: 80%
    lines: 80%
```

---

## Performance Standards

### Database Queries

```typescript
// ✅ GOOD: Use indexes
CREATE INDEX idx_users_email ON users(email);

// ✅ GOOD: Select only needed columns
const user = await db.query(
  'SELECT id, name, email FROM users WHERE id = $1',
  [userId]
);

// ❌ BAD: SELECT *
const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);

// ✅ GOOD: Use pagination
const users = await db.query(
  'SELECT * FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2',
  [pageSize, offset]
);

// ✅ GOOD: Avoid N+1 queries
const users = await db.query('SELECT * FROM users WHERE team_id = $1', [teamId]);
const userIds = users.map(u => u.id);
const posts = await db.query('SELECT * FROM posts WHERE user_id = ANY($1)', [userIds]);
```

### Caching

```typescript
// ✅ GOOD: Cache expensive operations
import Redis from 'ioredis';

const redis = new Redis();

async function getUser(userId: string): Promise<User> {
  // Check cache first
  const cached = await redis.get(`user:${userId}`);
  if (cached) {
    return JSON.parse(cached);
  }

  // Fetch from database
  const user = await db.getUser(userId);

  // Cache for 1 hour
  await redis.setex(`user:${userId}`, 3600, JSON.stringify(user));

  return user;
}
```

---

## Documentation Standards

### Code Comments

```typescript
/**
 * Processes payment using the Stripe API with retry logic.
 *
 * Implements exponential backoff for transient failures and idempotency
 * to prevent duplicate charges.
 *
 * @param amount - Amount in cents (e.g., 1000 = $10.00)
 * @param currency - ISO 4217 currency code (e.g., 'usd')
 * @param customerId - Stripe customer ID
 * @returns Payment intent object
 * @throws {PaymentError} If payment fails after all retries
 *
 * @example
 * ```typescript
 * const payment = await processPayment(1000, 'usd', 'cus_123');
 * console.log(payment.status); // 'succeeded'
 * ```
 *
 * @see https://stripe.com/docs/api/payment_intents
 */
async function processPayment(
  amount: number,
  currency: string,
  customerId: string
): Promise<PaymentIntent> {
  // Implementation
}
```

### README Standards

Every project must include:
1. **Purpose**: What the project does
2. **Installation**: How to set up
3. **Usage**: Examples
4. **Configuration**: Environment variables, config files
5. **Development**: How to contribute
6. **License**: Licensing information

---

## Version Control Standards

### Commit Messages

```bash
# ✅ GOOD: Conventional Commits format
feat: add user authentication with JWT
fix: resolve memory leak in image processor
docs: update API documentation for v2 endpoints
refactor: extract validation logic into separate module
test: add integration tests for payment flow
chore: update dependencies to latest versions

# Format: <type>(<scope>): <subject>
feat(auth): implement OAuth2 login flow

# Include body for complex changes
fix: prevent race condition in order processing

Previously, concurrent orders could modify the same inventory
record, leading to overselling. This adds pessimistic locking
to prevent the issue.

Fixes #123
```

### Branch Naming

```bash
# Pattern: <type>/<short-description>
feature/user-authentication
bugfix/payment-processing-error
hotfix/security-vulnerability
refactor/database-layer
docs/api-documentation
```

---

## References

### Essential Books
1. "Clean Code" - Robert C. Martin
2. "The Pragmatic Programmer" - Hunt & Thomas
3. "Refactoring" - Martin Fowler
4. "Design Patterns" - Gang of Four
5. "Code Complete" - Steve McConnell

### Style Guides
- [Google Style Guides](https://google.github.io/styleguide/)
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [PEP 8 - Python Style Guide](https://pep8.org/)
- [Effective Go](https://go.dev/doc/effective_go)

### Security References
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Guidelines](https://www.nist.gov/cybersecurity)

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Compliance**: OWASP Top 10, CWE Top 25, industry best practices
