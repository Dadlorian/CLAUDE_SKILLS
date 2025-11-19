# Development Rules
## Non-Negotiable Standards for Elite Software Development

### Philosophy

These rules are derived from:
- **Decades of production incidents** - Learn from others' mistakes
- **Industry leaders** - Google, Amazon, Netflix, Stripe engineering practices
- **Security breaches** - OWASP, security research, incident reports
- **Performance failures** - Scalability lessons from high-traffic systems

**Core Belief**: Rules exist because breaking them causes real damage: security breaches, data loss, downtime, or unmaintainable code.

---

## Category 1: Security Rules (NEVER BREAK)

### Rule 1.1: Never Trust User Input
**Why**: SQL injection, XSS, and command injection are still in OWASP Top 10

```typescript
// ✅ CORRECT
function searchUsers(query: string): Promise<User[]> {
  // Parameterized query prevents SQL injection
  return db.query('SELECT * FROM users WHERE name LIKE $1', [`%${query}%`]);
}

// ❌ FORBIDDEN
function searchUsers(query: string) {
  return db.query(`SELECT * FROM users WHERE name LIKE '%${query}%'`);
}
```

**Enforcement**: All database queries must use parameterized statements. No exceptions.

### Rule 1.2: Never Store Secrets in Code
**Why**: Millions of secrets leaked via GitHub every year

```typescript
// ✅ CORRECT
const apiKey = process.env.STRIPE_API_KEY;
if (!apiKey) throw new Error('STRIPE_API_KEY required');

// ❌ FORBIDDEN
const apiKey = 'sk_live_51abc123...'; // Hardcoded secret
```

**Enforcement**:
- All secrets in environment variables or secret managers
- Add `.env` to `.gitignore`
- Use git-secrets or similar pre-commit hooks
- Rotate any accidentally committed secrets immediately

### Rule 1.3: Always Validate and Sanitize Input
**Why**: Prevents injection attacks, data corruption, and crashes

```typescript
// ✅ CORRECT
import { z } from 'zod';

const UserSchema = z.object({
  email: z.string().email().max(255),
  age: z.number().int().min(0).max(150),
});

function createUser(input: unknown): User {
  const data = UserSchema.parse(input); // Throws if invalid
  return db.createUser(data);
}

// ❌ FORBIDDEN
function createUser(input: any) {
  return db.createUser(input); // No validation
}
```

**Enforcement**: Every external input must pass validation before use.

### Rule 1.4: Use HTTPS Everywhere
**Why**: Credentials and data intercepted over HTTP

```typescript
// ✅ CORRECT
const API_URL = 'https://api.example.com';

// ❌ FORBIDDEN
const API_URL = 'http://api.example.com';
```

**Enforcement**:
- Redirect HTTP to HTTPS
- Use HSTS headers
- Enable HTTPS in all environments (including development)

### Rule 1.5: Principle of Least Privilege
**Why**: Limit blast radius of security breaches

```typescript
// ✅ CORRECT
// Database user has only SELECT permission
const reportDb = createConnection({
  user: 'reporting_user', // Can only read
  database: 'analytics',
});

// ❌ FORBIDDEN
// Using admin/root account for application
const db = createConnection({
  user: 'root',
  database: 'production',
});
```

**Enforcement**: Applications run with minimal required permissions.

### Rule 1.6: Never Log Sensitive Data
**Why**: Logs often stored insecurely, accessible to many people

```typescript
// ✅ CORRECT
logger.info('User login successful', {
  userId: user.id,
  timestamp: Date.now()
});

// ❌ FORBIDDEN
logger.info('User login', {
  password: user.password,
  ssn: user.ssn,
  creditCard: user.creditCard
});
```

**Enforcement**: Code review must catch any PII/credentials in logs.

---

## Category 2: Reliability Rules

### Rule 2.1: Every Function Has One Responsibility
**Why**: Single Responsibility Principle - easier to test, debug, and modify

```typescript
// ✅ CORRECT
function calculateOrderTotal(items: OrderItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

function applyDiscount(total: number, discountCode: string): number {
  const discount = getDiscount(discountCode);
  return total * (1 - discount);
}

function processOrder(items: OrderItem[], discountCode: string): Order {
  const total = calculateOrderTotal(items);
  const finalTotal = applyDiscount(total, discountCode);
  return createOrder(items, finalTotal);
}

// ❌ FORBIDDEN
function processOrder(items: OrderItem[], discountCode: string) {
  // Calculating total
  let total = 0;
  for (const item of items) {
    total += item.price * item.quantity;
  }

  // Applying discount
  const discount = db.query('SELECT * FROM discounts WHERE code = ?', discountCode);
  total = total * (1 - discount.percentage);

  // Creating order
  const orderId = generateId();
  db.insert('orders', { id: orderId, total });

  // Sending email
  sendEmail(user.email, 'Order confirmation', orderTemplate);

  // Updating inventory
  for (const item of items) {
    db.update('inventory', { quantity: quantity - item.quantity });
  }
}
```

**Enforcement**: Functions over 50 lines require justification in code review.

### Rule 2.2: Fail Fast, Fail Loudly
**Why**: Silent failures hide bugs until production

```typescript
// ✅ CORRECT
function divide(a: number, b: number): number {
  if (b === 0) {
    throw new Error('Division by zero');
  }
  return a / b;
}

// ❌ FORBIDDEN
function divide(a: number, b: number): number {
  if (b === 0) return 0; // Silent failure
  return a / b;
}
```

**Enforcement**: Never swallow errors without logging and proper handling.

### Rule 2.3: Idempotency for Critical Operations
**Why**: Network failures happen - operations should be safely retryable

```typescript
// ✅ CORRECT
async function createPayment(orderId: string, amount: number): Promise<Payment> {
  const idempotencyKey = `payment_${orderId}`;

  // Check if payment already exists
  const existing = await db.findPayment({ idempotencyKey });
  if (existing) return existing;

  // Create payment with idempotency key
  return stripe.payments.create({
    amount,
    idempotencyKey,
  });
}

// ❌ FORBIDDEN
async function createPayment(orderId: string, amount: number) {
  return stripe.payments.create({ amount }); // No idempotency
}
```

**Enforcement**: All payment/financial operations must be idempotent.

### Rule 2.4: Always Handle Errors
**Why**: Unhandled errors crash applications

```typescript
// ✅ CORRECT
async function fetchUserData(userId: string): Promise<User | null> {
  try {
    const response = await fetch(`/api/users/${userId}`);

    if (!response.ok) {
      if (response.status === 404) return null;
      throw new Error(`API error: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    if (error instanceof NetworkError) {
      logger.error('Network failure fetching user', { userId, error });
      throw new UserFetchError('Unable to fetch user data');
    }
    throw error;
  }
}

// ❌ FORBIDDEN
async function fetchUserData(userId: string) {
  const response = await fetch(`/api/users/${userId}`);
  return response.json(); // No error handling
}
```

**Enforcement**: No try-catch blocks without proper error handling.

### Rule 2.5: Timeout All External Calls
**Why**: Prevents hanging on slow/dead services

```typescript
// ✅ CORRECT
const response = await fetch(url, {
  signal: AbortSignal.timeout(5000), // 5 second timeout
});

// Or with axios
const response = await axios.get(url, {
  timeout: 5000,
});

// ❌ FORBIDDEN
const response = await fetch(url); // No timeout
```

**Enforcement**: All HTTP requests, database queries, and external calls must have timeouts.

---

## Category 3: Performance Rules

### Rule 3.1: No N+1 Queries
**Why**: Kills database performance and scalability

```typescript
// ✅ CORRECT
async function getUsersWithPosts(): Promise<UserWithPosts[]> {
  const users = await db.query('SELECT * FROM users');
  const userIds = users.map(u => u.id);

  const posts = await db.query(
    'SELECT * FROM posts WHERE user_id = ANY($1)',
    [userIds]
  );

  // Combine in memory
  return users.map(user => ({
    ...user,
    posts: posts.filter(p => p.userId === user.id),
  }));
}

// ❌ FORBIDDEN
async function getUsersWithPosts() {
  const users = await db.query('SELECT * FROM users');

  for (const user of users) {
    user.posts = await db.query(
      'SELECT * FROM posts WHERE user_id = $1',
      [user.id]
    ); // N+1 query!
  }

  return users;
}
```

**Enforcement**: Code review must catch N+1 patterns. Use query logging in development.

### Rule 3.2: Index Database Queries
**Why**: Unindexed queries cause table scans and slow queries

```sql
-- ✅ CORRECT
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);

-- Query uses index
SELECT * FROM users WHERE email = 'user@example.com';
```

**Enforcement**:
- All foreign keys must be indexed
- All columns in WHERE/ORDER BY clauses should be indexed
- Run EXPLAIN on all queries in code review

### Rule 3.3: Pagination for Large Result Sets
**Why**: Loading thousands of records crashes browsers and wastes bandwidth

```typescript
// ✅ CORRECT
async function getUsers(page: number = 1, pageSize: number = 50): Promise<PaginatedResult<User>> {
  const offset = (page - 1) * pageSize;

  const [users, total] = await Promise.all([
    db.query('SELECT * FROM users LIMIT $1 OFFSET $2', [pageSize, offset]),
    db.query('SELECT COUNT(*) FROM users'),
  ]);

  return {
    data: users,
    page,
    pageSize,
    total,
    totalPages: Math.ceil(total / pageSize),
  };
}

// ❌ FORBIDDEN
async function getUsers() {
  return db.query('SELECT * FROM users'); // Could return millions of rows
}
```

**Enforcement**: Any list endpoint must implement pagination.

### Rule 3.4: Cache Expensive Operations
**Why**: Don't recalculate what doesn't change

```typescript
// ✅ CORRECT
const cache = new Map<string, CachedValue>();

async function getStatistics(userId: string): Promise<Statistics> {
  const cached = cache.get(userId);

  if (cached && Date.now() - cached.timestamp < 5 * 60 * 1000) {
    return cached.value; // Cache hit, less than 5 minutes old
  }

  const stats = await calculateStatistics(userId); // Expensive operation

  cache.set(userId, {
    value: stats,
    timestamp: Date.now(),
  });

  return stats;
}

// ❌ FORBIDDEN
async function getStatistics(userId: string) {
  return calculateStatistics(userId); // Recalculates every time
}
```

**Enforcement**: Operations taking >100ms should be cached if called frequently.

---

## Category 4: Code Quality Rules

### Rule 4.1: No Magic Numbers
**Why**: Numbers without context are unreadable and error-prone

```typescript
// ✅ CORRECT
const MAX_LOGIN_ATTEMPTS = 5;
const LOCKOUT_DURATION_MS = 15 * 60 * 1000; // 15 minutes
const PASSWORD_MIN_LENGTH = 12;

if (loginAttempts > MAX_LOGIN_ATTEMPTS) {
  lockoutUntil = Date.now() + LOCKOUT_DURATION_MS;
}

// ❌ FORBIDDEN
if (loginAttempts > 5) {
  lockoutUntil = Date.now() + 900000;
}
```

**Enforcement**: All numbers (except 0, 1) should be named constants.

### Rule 4.2: Descriptive Variable Names
**Why**: Code is read 10x more than written

```typescript
// ✅ CORRECT
const activeUserCount = users.filter(u => u.isActive).length;
const averageOrderValue = totalRevenue / orderCount;
const isEligibleForDiscount = user.orderCount > 5 && user.totalSpent > 1000;

// ❌ FORBIDDEN
const x = users.filter(u => u.isActive).length;
const avg = rev / cnt;
const flag = user.orderCount > 5 && user.totalSpent > 1000;
```

**Enforcement**: Single-letter variables only in short loops (i, j, k).

### Rule 4.3: No Commented-Out Code
**Why**: Creates confusion, clutters codebase. Use version control instead.

```typescript
// ❌ FORBIDDEN
function processOrder(order: Order) {
  // const tax = calculateTax(order); // Old implementation
  // const shipping = getShippingCost(order);

  const total = calculateTotal(order);

  // if (order.isPriority) {
  //   expediteShipping(order);
  // }

  return total;
}
```

**Enforcement**: Delete commented code. If needed later, retrieve from git history.

### Rule 4.4: DRY (Don't Repeat Yourself)
**Why**: Duplication multiplies bugs and maintenance burden

```typescript
// ✅ CORRECT
function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function createUser(email: string) {
  if (!validateEmail(email)) throw new ValidationError('Invalid email');
  // ...
}

function updateEmail(userId: string, email: string) {
  if (!validateEmail(email)) throw new ValidationError('Invalid email');
  // ...
}

// ❌ FORBIDDEN
function createUser(email: string) {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new Error('Invalid email');
  }
}

function updateEmail(userId: string, email: string) {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new Error('Invalid email');
  }
}
```

**Enforcement**: Duplicated code blocks >3 lines should be extracted to functions.

---

## Category 5: Testing Rules

### Rule 5.1: No Untested Code in Production
**Why**: Untested code is broken code

```typescript
// ✅ CORRECT - Has tests
export function calculateDiscount(total: number, discountPercent: number): number {
  if (total < 0) throw new Error('Total cannot be negative');
  if (discountPercent < 0 || discountPercent > 100) {
    throw new Error('Discount must be between 0 and 100');
  }
  return total * (discountPercent / 100);
}

// tests/calculateDiscount.test.ts
describe('calculateDiscount', () => {
  it('calculates correct discount amount', () => {
    expect(calculateDiscount(100, 10)).toBe(10);
  });

  it('throws for negative total', () => {
    expect(() => calculateDiscount(-100, 10)).toThrow();
  });

  it('throws for invalid discount percentage', () => {
    expect(() => calculateDiscount(100, 150)).toThrow();
  });
});
```

**Enforcement**:
- Minimum 80% code coverage
- CI fails if coverage drops
- All bug fixes must include regression tests

### Rule 5.2: Tests Must Be Independent
**Why**: Dependent tests create flaky test suites

```typescript
// ✅ CORRECT
describe('UserService', () => {
  beforeEach(async () => {
    await db.clear(); // Clean slate for each test
  });

  it('creates user', async () => {
    const user = await userService.create({ email: 'test@example.com' });
    expect(user.email).toBe('test@example.com');
  });

  it('finds user by email', async () => {
    await userService.create({ email: 'test@example.com' });
    const user = await userService.findByEmail('test@example.com');
    expect(user).toBeDefined();
  });
});

// ❌ FORBIDDEN
describe('UserService', () => {
  let userId: string;

  it('creates user', async () => {
    const user = await userService.create({ email: 'test@example.com' });
    userId = user.id; // Next test depends on this
  });

  it('updates user', async () => {
    await userService.update(userId, { name: 'John' }); // Breaks if first test fails
  });
});
```

**Enforcement**: Tests must pass in any order and in isolation.

### Rule 5.3: Mock External Dependencies
**Why**: Tests should be fast, reliable, and not depend on external services

```typescript
// ✅ CORRECT
import { vi } from 'vitest';

vi.mock('./emailService', () => ({
  sendEmail: vi.fn(),
}));

it('sends welcome email on user creation', async () => {
  await userService.create({ email: 'test@example.com' });

  expect(emailService.sendEmail).toHaveBeenCalledWith(
    'test@example.com',
    'Welcome!',
    expect.any(String)
  );
});

// ❌ FORBIDDEN
it('sends welcome email on user creation', async () => {
  await userService.create({ email: 'test@example.com' });

  // Checking real email service - slow, unreliable, could send real emails
  const emails = await emailService.getSentEmails();
  expect(emails).toContainEqual(expect.objectContaining({
    to: 'test@example.com',
  }));
});
```

**Enforcement**: Unit tests must not make real HTTP requests, database calls, or file I/O.

---

## Category 6: Git & Deployment Rules

### Rule 6.1: Never Commit to Main Directly
**Why**: Bypasses code review and CI checks

**Enforcement**:
- Main branch protected
- Require pull request reviews
- Require passing CI checks

### Rule 6.2: Atomic Commits
**Why**: Makes git history readable and reverts clean

```bash
# ✅ CORRECT - Each commit does one thing
feat: add user email validation
fix: resolve race condition in order processing
refactor: extract payment logic to service layer

# ❌ FORBIDDEN - Commits doing multiple unrelated things
fix: various bugs and add new feature and refactor code
```

**Enforcement**: Each commit should be revertible independently.

### Rule 6.3: Run Tests Before Committing
**Why**: Don't push broken code to the team

```bash
# ✅ CORRECT - Pre-commit hook
#!/bin/sh
npm test || exit 1
npm run lint || exit 1
```

**Enforcement**: Pre-commit hooks enforce this automatically.

### Rule 6.4: No Secrets in Version Control
**Why**: Git history is permanent - secrets can't be fully removed

**Enforcement**:
- Use git-secrets or similar tools
- Add `.env` to `.gitignore`
- Scan commits with tools like TruffleHog
- If secret leaked: rotate immediately, rewrite git history

---

## Category 7: Documentation Rules

### Rule 7.1: Public APIs Must Be Documented
**Why**: Undocumented APIs cause confusion and misuse

```typescript
// ✅ CORRECT
/**
 * Fetches user by ID with optional related data.
 *
 * @param userId - The unique identifier of the user
 * @param options - Optional parameters for the fetch
 * @param options.includePosts - Include user's posts in response
 * @param options.includeComments - Include user's comments in response
 * @returns Promise resolving to User object with optional relations
 * @throws {UserNotFoundError} If user doesn't exist
 * @throws {DatabaseError} If database query fails
 *
 * @example
 * ```typescript
 * const user = await getUser('123', { includePosts: true });
 * console.log(user.posts.length);
 * ```
 */
export async function getUser(
  userId: string,
  options?: { includePosts?: boolean; includeComments?: boolean }
): Promise<User> {
  // Implementation
}

// ❌ FORBIDDEN
export async function getUser(userId: string, options?: any) {
  // No documentation
}
```

**Enforcement**: Exported functions/classes must have JSDoc/docstrings.

### Rule 7.2: README for Every Project
**Why**: New developers need onboarding documentation

**Required Sections**:
1. Purpose - What the project does
2. Installation - How to set up
3. Usage - How to use
4. Configuration - Environment variables, settings
5. Development - How to contribute
6. License

**Enforcement**: CI checks for README.md existence.

### Rule 7.3: Update Documentation with Code Changes
**Why**: Stale docs are worse than no docs

```typescript
// ✅ CORRECT
// Update both code and docs in same commit
feat: add user role-based permissions

- Add 'role' field to User model
- Implement permission checking middleware
- Update API docs with new auth requirements
```

**Enforcement**: PRs that change behavior must update related docs.

---

## Emergency Overrides

Sometimes rules must be broken. When they are:

### Override Process
1. **Document why** in code comments
2. **Create a ticket** to fix properly
3. **Get approval** from tech lead
4. **Set a deadline** for fix

```typescript
// SECURITY OVERRIDE: Temporarily accepting HTTP for legacy client migration
// TODO: Remove after legacy client EOL on 2025-12-31
// Approved by: @tech-lead
// Ticket: PROJ-1234
if (process.env.ALLOW_HTTP === 'true') {
  // Allow HTTP
}
```

---

## Enforcement

These rules are enforced through:

1. **Automated Tools**:
   - ESLint / Pylint for code style
   - TypeScript strict mode for type safety
   - SonarQube for code quality
   - Dependabot for security updates
   - Git hooks for pre-commit checks

2. **Code Review**:
   - All code must be reviewed
   - Reviewers check for rule violations
   - Cannot merge without approval

3. **CI/CD Pipeline**:
   - Tests must pass
   - Linting must pass
   - Security scans must pass
   - Coverage thresholds must be met

4. **Architecture Review**:
   - Major changes require design review
   - Performance implications evaluated
   - Security implications evaluated

---

## Conclusion

These rules exist because breaking them has caused real damage in production systems:

- **Security rules** prevent breaches and data leaks
- **Reliability rules** prevent outages and data loss
- **Performance rules** prevent slow, unusable systems
- **Quality rules** prevent unmaintainable codebases
- **Testing rules** catch bugs before production
- **Git rules** maintain clean, traceable history
- **Documentation rules** enable team collaboration

**Remember**: These aren't arbitrary restrictions - they're lessons learned from millions of dollars in incidents and outages.

**When in doubt**: Choose the safer, more conservative option. It's easier to relax rules than to recover from a security breach or data loss.

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Authority**: Engineering Standards Committee
