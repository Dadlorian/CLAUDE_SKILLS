# Best Practices
## Professional Development & Skill Creation Excellence

### Philosophy

Best practices represent the collective wisdom of:
- **Industry Leaders**: FAANG engineering teams (Google, Meta, Netflix, Amazon)
- **Open Source Communities**: Proven patterns from successful projects
- **Research**: Academic studies on software engineering effectiveness
- **Production Experience**: Lessons from operating systems at scale

Unlike **Rules** (which are non-negotiable), best practices are strong recommendations that should be followed unless you have a compelling reason not to.

---

## Category 1: Development Workflow

### 1.1 Test-Driven Development (TDD)

**Practice**: Write tests before implementation code

**Benefits**:
- Better API design (you use it before implementing it)
- Higher test coverage (every feature has tests)
- Fewer bugs (catch issues during development)
- Living documentation (tests show usage)

**Example Workflow**:
```typescript
// 1. Write the test first (Red)
describe('EmailValidator', () => {
  it('should reject invalid email formats', () => {
    expect(validateEmail('notanemail')).toBe(false);
    expect(validateEmail('missing@domain')).toBe(false);
    expect(validateEmail('@nodomain.com')).toBe(false);
  });

  it('should accept valid email formats', () => {
    expect(validateEmail('user@example.com')).toBe(true);
    expect(validateEmail('user.name+tag@example.co.uk')).toBe(true);
  });
});

// 2. Run test - it fails (because function doesn't exist yet)

// 3. Write minimal code to make it pass (Green)
function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// 4. Refactor if needed (Refactor)
// Make improvements while tests ensure correctness
```

**When to use**: Always for new features, bug fixes, and refactoring

**Reference**: "Test Driven Development: By Example" - Kent Beck

### 1.2 Feature Branching & Pull Requests

**Practice**: Develop features in isolated branches, merge via pull requests

**Workflow**:
```bash
# Create feature branch
git checkout -b feature/user-authentication

# Make changes, commit regularly
git add src/auth/
git commit -m "feat: implement JWT token generation"

# Push and create PR
git push -u origin feature/user-authentication

# Code review, CI checks, then merge
```

**Benefits**:
- Code review catches bugs early
- CI runs automated checks
- Main branch stays stable
- Easy to revert if needed

**Best Practices**:
- Keep PRs small (<400 lines changed)
- Write descriptive PR descriptions
- Link to relevant tickets/issues
- Respond to review feedback promptly

### 1.3 Continuous Integration (CI)

**Practice**: Automated testing on every commit

**Example GitHub Actions**:
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run type check
        run: npm run type-check

      - name: Run tests
        run: npm test

      - name: Check coverage
        run: npm run coverage

      - name: Build
        run: npm run build
```

**Benefits**:
- Catch broken builds immediately
- Prevent regressions
- Ensure code quality standards
- Safe to merge when CI passes

### 1.4 Code Review Guidelines

**Practice**: Every code change reviewed by peers

**What to Look For**:
1. **Correctness**: Does the code do what it's supposed to?
2. **Tests**: Are there tests? Do they cover edge cases?
3. **Security**: Any vulnerabilities? Input validation?
4. **Performance**: Any N+1 queries or inefficient algorithms?
5. **Maintainability**: Is it readable? Well-structured?
6. **Documentation**: Are complex parts explained?

**Reviewer Checklist**:
```markdown
- [ ] Code follows style guide
- [ ] Tests are present and comprehensive
- [ ] No security vulnerabilities
- [ ] No performance anti-patterns
- [ ] Documentation updated if needed
- [ ] No hardcoded secrets or config
- [ ] Error handling is robust
- [ ] Edge cases handled
```

**Communication**:
- Be kind and constructive
- Explain *why* something should change
- Suggest alternatives, don't just criticize
- Approve when satisfied, not perfect

---

## Category 2: Architecture & Design

### 2.1 SOLID Principles

**S - Single Responsibility Principle**
```typescript
// ✅ GOOD: Each class has one reason to change
class UserRepository {
  async findById(id: string): Promise<User> { }
  async save(user: User): Promise<void> { }
}

class UserEmailService {
  async sendWelcomeEmail(user: User): Promise<void> { }
}

class UserRegistrationService {
  constructor(
    private userRepo: UserRepository,
    private emailService: UserEmailService
  ) {}

  async register(userData: CreateUserDTO): Promise<User> {
    const user = await this.userRepo.save(userData);
    await this.emailService.sendWelcomeEmail(user);
    return user;
  }
}

// ❌ BAD: UserRepository doing too much
class UserRepository {
  async findById(id: string): Promise<User> { }
  async save(user: User): Promise<void> { }
  async sendWelcomeEmail(user: User): Promise<void> { } // Not repository's job
  async validateEmail(email: string): boolean { } // Not repository's job
}
```

**O - Open/Closed Principle**
```typescript
// ✅ GOOD: Open for extension, closed for modification
interface PaymentProcessor {
  process(amount: number): Promise<PaymentResult>;
}

class StripeProcessor implements PaymentProcessor {
  async process(amount: number): Promise<PaymentResult> {
    // Stripe-specific logic
  }
}

class PayPalProcessor implements PaymentProcessor {
  async process(amount: number): Promise<PaymentResult> {
    // PayPal-specific logic
  }
}

class PaymentService {
  constructor(private processor: PaymentProcessor) {}

  async pay(amount: number) {
    return this.processor.process(amount);
  }
}

// Add new processor without modifying existing code
class CryptoProcessor implements PaymentProcessor {
  async process(amount: number): Promise<PaymentResult> {
    // Crypto-specific logic
  }
}
```

### 2.2 Dependency Injection

**Practice**: Inject dependencies instead of creating them

```typescript
// ✅ GOOD: Dependencies injected
class UserService {
  constructor(
    private userRepo: UserRepository,
    private emailService: EmailService,
    private logger: Logger
  ) {}

  async createUser(data: CreateUserDTO): Promise<User> {
    this.logger.info('Creating user', { email: data.email });
    const user = await this.userRepo.create(data);
    await this.emailService.sendWelcome(user);
    return user;
  }
}

// Easy to test with mocks
const mockRepo = { create: vi.fn() };
const mockEmail = { sendWelcome: vi.fn() };
const mockLogger = { info: vi.fn() };
const service = new UserService(mockRepo, mockEmail, mockLogger);

// ❌ BAD: Creating dependencies internally
class UserService {
  private userRepo = new UserRepository();
  private emailService = new EmailService();
  private logger = new Logger();

  // Hard to test - can't inject mocks
}
```

**Benefits**:
- Easy to test (inject mocks)
- Easy to change implementations
- Clear dependencies
- Inversion of Control

### 2.3 Domain-Driven Design (DDD)

**Practice**: Organize code around business domains

**Project Structure**:
```
src/
├── domain/                   # Business logic
│   ├── user/
│   │   ├── User.ts          # Entity
│   │   ├── UserRepository.ts # Repository interface
│   │   ├── UserService.ts    # Domain services
│   │   └── UserEvents.ts     # Domain events
│   └── order/
│       ├── Order.ts
│       ├── OrderRepository.ts
│       └── OrderService.ts
├── infrastructure/           # Technical details
│   ├── database/
│   │   ├── UserRepositoryImpl.ts
│   │   └── OrderRepositoryImpl.ts
│   └── email/
│       └── SendGridEmailService.ts
├── application/             # Use cases
│   ├── CreateUserUseCase.ts
│   └── PlaceOrderUseCase.ts
└── presentation/            # API/UI
    ├── controllers/
    └── routes/
```

**Benefits**:
- Clear separation of concerns
- Business logic independent of infrastructure
- Easy to understand for domain experts
- Testable without database/external services

**Reference**: "Domain-Driven Design" - Eric Evans

### 2.4 API Design

**RESTful Best Practices**:
```typescript
// ✅ GOOD: Resource-oriented, consistent patterns
GET    /api/users              # List users (paginated)
GET    /api/users/:id          # Get specific user
POST   /api/users              # Create user
PUT    /api/users/:id          # Update entire user
PATCH  /api/users/:id          # Update partial user
DELETE /api/users/:id          # Delete user

GET    /api/users/:id/posts    # List user's posts
POST   /api/users/:id/posts    # Create post for user

// ❌ BAD: Action-oriented, inconsistent
GET    /api/getUser?id=123
POST   /api/createNewUser
POST   /api/updateUser
POST   /api/removeUser
GET    /api/user-posts?userId=123
```

**Response Format**:
```typescript
// ✅ GOOD: Consistent response structure
interface APIResponse<T> {
  data: T;
  meta?: {
    page: number;
    pageSize: number;
    total: number;
  };
  links?: {
    self: string;
    next?: string;
    prev?: string;
  };
}

// Success response
{
  "data": {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com"
  }
}

// Error response
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is invalid",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      }
    ]
  }
}
```

**Versioning**:
```typescript
// Option 1: URL versioning (most common)
GET /api/v1/users
GET /api/v2/users

// Option 2: Header versioning
GET /api/users
Accept: application/vnd.api+json; version=1

// Option 3: Content negotiation
GET /api/users
Accept: application/vnd.api.v2+json
```

---

## Category 3: Performance Optimization

### 3.1 Database Optimization

**Indexing Strategy**:
```sql
-- Index foreign keys
CREATE INDEX idx_posts_user_id ON posts(user_id);

-- Composite indexes for common queries
CREATE INDEX idx_users_email_active ON users(email, is_active);

-- Partial indexes for specific conditions
CREATE INDEX idx_active_users ON users(email)
WHERE is_active = true;

-- Index for sorting
CREATE INDEX idx_posts_created_desc ON posts(created_at DESC);
```

**Query Optimization**:
```sql
-- ✅ GOOD: Select only needed columns
SELECT id, name, email FROM users WHERE id = $1;

-- ❌ BAD: Select everything
SELECT * FROM users WHERE id = $1;

-- ✅ GOOD: Use EXPLAIN to analyze
EXPLAIN ANALYZE
SELECT * FROM posts
WHERE user_id = $1
ORDER BY created_at DESC
LIMIT 10;
```

**Connection Pooling**:
```typescript
// ✅ GOOD: Use connection pool
import { Pool } from 'pg';

const pool = new Pool({
  max: 20, // Maximum number of connections
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

export async function query(text: string, params: any[]) {
  const client = await pool.connect();
  try {
    return await client.query(text, params);
  } finally {
    client.release(); // Return to pool
  }
}
```

### 3.2 Caching Strategies

**Multi-Level Caching**:
```typescript
// Level 1: In-memory cache (fastest)
const inMemoryCache = new Map<string, CacheEntry>();

// Level 2: Redis (shared across instances)
import Redis from 'ioredis';
const redis = new Redis();

// Level 3: Database (slowest)
async function getUser(userId: string): Promise<User> {
  // Check in-memory cache
  const memCached = inMemoryCache.get(userId);
  if (memCached && !isExpired(memCached)) {
    return memCached.value;
  }

  // Check Redis
  const redisCached = await redis.get(`user:${userId}`);
  if (redisCached) {
    const user = JSON.parse(redisCached);
    inMemoryCache.set(userId, { value: user, timestamp: Date.now() });
    return user;
  }

  // Fetch from database
  const user = await db.getUser(userId);

  // Cache in both levels
  await redis.setex(`user:${userId}`, 3600, JSON.stringify(user));
  inMemoryCache.set(userId, { value: user, timestamp: Date.now() });

  return user;
}
```

**Cache Invalidation**:
```typescript
// Strategy 1: Time-based expiration
await redis.setex(key, 3600, value); // Expire after 1 hour

// Strategy 2: Event-based invalidation
async function updateUser(userId: string, data: UpdateUserDTO) {
  const user = await db.updateUser(userId, data);

  // Invalidate cache
  await redis.del(`user:${userId}`);
  inMemoryCache.delete(userId);

  return user;
}

// Strategy 3: Cache-aside pattern with tags
await redis.set(
  `user:${userId}`,
  JSON.stringify(user),
  'EX', 3600,
  'TAG', 'users'
);

// Invalidate all user caches
await redis.deleteByTag('users');
```

### 3.3 Async Processing

**Background Jobs**:
```typescript
// ✅ GOOD: Long-running tasks in background
import Bull from 'bull';

const emailQueue = new Bull('email', {
  redis: { host: 'localhost', port: 6379 }
});

// API endpoint responds immediately
async function createUser(data: CreateUserDTO): Promise<User> {
  const user = await db.createUser(data);

  // Queue email instead of sending synchronously
  await emailQueue.add('welcome', {
    userId: user.id,
    email: user.email,
  });

  return user; // Return immediately
}

// Process queue in background worker
emailQueue.process('welcome', async (job) => {
  await emailService.sendWelcomeEmail(
    job.data.email,
    job.data.userId
  );
});

// ❌ BAD: Blocking API call
async function createUser(data: CreateUserDTO) {
  const user = await db.createUser(data);
  await emailService.sendWelcomeEmail(user.email); // Blocks response
  return user;
}
```

---

## Category 4: Security Best Practices

### 4.1 Authentication

**JWT Best Practices**:
```typescript
import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';

// ✅ GOOD: Secure token generation
async function login(email: string, password: string) {
  const user = await db.findUserByEmail(email);

  if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
    throw new UnauthorizedError('Invalid credentials');
  }

  const accessToken = jwt.sign(
    {
      userId: user.id,
      role: user.role,
    },
    process.env.JWT_SECRET!,
    {
      expiresIn: '15m', // Short-lived access token
      issuer: 'myapp',
      audience: 'myapp-api',
    }
  );

  const refreshToken = jwt.sign(
    { userId: user.id },
    process.env.REFRESH_TOKEN_SECRET!,
    { expiresIn: '7d' } // Longer-lived refresh token
  );

  // Store refresh token (for revocation)
  await db.saveRefreshToken(user.id, refreshToken);

  return { accessToken, refreshToken };
}
```

**Rate Limiting**:
```typescript
import rateLimit from 'express-rate-limit';

// Limit login attempts
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts
  message: 'Too many login attempts, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
});

app.post('/api/auth/login', loginLimiter, loginHandler);

// General API rate limit
const apiLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 100, // 100 requests per minute
});

app.use('/api/', apiLimiter);
```

### 4.2 Data Sanitization

**Input Sanitization**:
```typescript
import sanitizeHtml from 'sanitize-html';
import validator from 'validator';

function sanitizeUserInput(input: CreatePostDTO): CreatePostDTO {
  return {
    title: validator.escape(input.title.trim()),
    content: sanitizeHtml(input.content, {
      allowedTags: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
      allowedAttributes: {
        'a': ['href']
      },
      allowedSchemes: ['http', 'https', 'mailto'],
    }),
    tags: input.tags.map(tag => validator.escape(tag.trim())),
  };
}
```

**SQL Injection Prevention**:
```typescript
// ✅ GOOD: Parameterized queries
async function findUserByEmail(email: string): Promise<User | null> {
  const result = await db.query(
    'SELECT * FROM users WHERE email = $1',
    [email] // Parameters separate from query
  );
  return result.rows[0] || null;
}

// ✅ GOOD: Query builder (also safe)
const user = await db
  .select('*')
  .from('users')
  .where('email', '=', email)
  .first();

// ❌ BAD: String concatenation
const result = await db.query(
  `SELECT * FROM users WHERE email = '${email}'`
);
```

---

## Category 5: Monitoring & Observability

### 5.1 Logging

**Structured Logging**:
```typescript
import winston from 'winston';

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: {
    service: 'user-service',
    environment: process.env.NODE_ENV,
  },
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
});

// Usage
logger.info('User created', {
  userId: user.id,
  email: user.email,
  duration: Date.now() - startTime,
});

logger.error('Database query failed', {
  query: 'SELECT * FROM users',
  error: error.message,
  stack: error.stack,
});
```

**Log Levels**:
- **ERROR**: Something failed, needs immediate attention
- **WARN**: Something unexpected, but handled
- **INFO**: Important business events
- **DEBUG**: Detailed diagnostic information
- **TRACE**: Very detailed (usually off in production)

### 5.2 Metrics

**Application Metrics**:
```typescript
import { Counter, Histogram, Gauge } from 'prom-client';

// Count events
const httpRequestsTotal = new Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'route', 'status'],
});

// Measure durations
const httpRequestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration',
  labelNames: ['method', 'route'],
  buckets: [0.1, 0.5, 1, 2, 5], // seconds
});

// Track current values
const activeConnections = new Gauge({
  name: 'active_connections',
  help: 'Number of active connections',
});

// Middleware to track metrics
app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;

    httpRequestsTotal.labels(req.method, req.route?.path || req.path, res.statusCode.toString()).inc();
    httpRequestDuration.labels(req.method, req.route?.path || req.path).observe(duration);
  });

  next();
});
```

### 5.3 Distributed Tracing

**OpenTelemetry Example**:
```typescript
import { trace } from '@opentelemetry/api';

const tracer = trace.getTracer('user-service');

async function createUser(data: CreateUserDTO): Promise<User> {
  return tracer.startActiveSpan('createUser', async (span) => {
    try {
      span.setAttribute('user.email', data.email);

      const user = await tracer.startActiveSpan('db.createUser', async (dbSpan) => {
        const result = await db.createUser(data);
        dbSpan.end();
        return result;
      });

      await tracer.startActiveSpan('email.sendWelcome', async (emailSpan) => {
        await emailService.sendWelcome(user);
        emailSpan.end();
      });

      span.setStatus({ code: SpanStatusCode.OK });
      return user;
    } catch (error) {
      span.recordException(error);
      span.setStatus({ code: SpanStatusCode.ERROR });
      throw error;
    } finally {
      span.end();
    }
  });
}
```

---

## Category 6: Skill Development Best Practices

### 6.1 Skill Structure

**Anatomy of a Great Skill**:
```markdown
# Skill Name

## Purpose
[One sentence: What problem does this solve?]

## When to Use
- Use case 1
- Use case 2

## Prerequisites
- Required tools/dependencies
- Required knowledge

## Workflow

### Phase 1: [Name]
1. Step 1: [Specific, actionable]
2. Step 2: [Specific, actionable]

### Phase 2: [Name]
1. Step 1
2. Step 2

## Validation
How to verify the skill worked correctly

## Troubleshooting
Common issues and solutions

## Examples
Real-world usage examples
```

### 6.2 Skill Quality Checklist

```markdown
- [ ] Clear, specific purpose statement
- [ ] Actionable, numbered steps
- [ ] Success criteria defined
- [ ] Error handling included
- [ ] Examples provided
- [ ] No ambiguous language
- [ ] Follows a proven pattern
- [ ] References standards/guides
```

### 6.3 Skill Naming Conventions

```bash
# Pattern: <action>-<domain>-<specificity>
create-api-endpoint
review-security-vulnerabilities
generate-test-suite
migrate-database-schema
analyze-performance-bottlenecks

# NOT:
helper  # Too vague
doStuff  # Unclear
skill1  # Not descriptive
```

---

## Conclusion

Best practices are **strong recommendations** based on collective industry experience. While not as strict as rules, following them leads to:

- **Higher quality**: Fewer bugs, better performance
- **Better collaboration**: Consistent patterns, easier onboarding
- **Faster development**: Proven solutions, less reinventing
- **Easier maintenance**: Clear structure, good documentation

**Remember**: Best practices evolve with technology and team needs. Stay curious, keep learning, and adapt as necessary.

---

**References**:
- "Clean Code" - Robert C. Martin
- "The Pragmatic Programmer" - Hunt & Thomas
- "Domain-Driven Design" - Eric Evans
- "Designing Data-Intensive Applications" - Martin Kleppmann
- "Site Reliability Engineering" - Google
- "Release It!" - Michael Nygard

---

**Version**: 1.0
**Last Updated**: 2025-11-19
