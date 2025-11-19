# Backend API Patterns Quick Reference

## RESTful API Patterns

### Resource Naming
```
✅ Good:
GET    /api/v1/users
GET    /api/v1/users/:id
POST   /api/v1/users
PUT    /api/v1/users/:id
PATCH  /api/v1/users/:id
DELETE /api/v1/users/:id

GET    /api/v1/users/:userId/orders
GET    /api/v1/users/:userId/orders/:orderId
```

### Response Formats

**Success (200)**:
```json
{
  "data": { "id": "123", "name": "John" },
  "meta": { "timestamp": "2025-01-15T10:30:00Z" }
}
```

**Collection with Pagination**:
```json
{
  "data": [...],
  "meta": {
    "total": 150,
    "page": 1,
    "limit": 20,
    "total_pages": 8
  },
  "links": {
    "self": "/users?page=1",
    "next": "/users?page=2",
    "last": "/users?page=8"
  }
}
```

**Error (400)**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ]
  }
}
```

## Database Patterns

### Connection Pooling
```typescript
// PostgreSQL with pg
import { Pool } from 'pg';

const pool = new Pool({
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  max: 20, // Maximum connections
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000
});

export const query = (text: string, params?: any[]) =>
  pool.query(text, params);
```

### Query Optimization
```sql
-- ❌ Bad: Table scan
SELECT * FROM users WHERE LOWER(email) = 'john@example.com';

-- ✅ Good: Use index
CREATE INDEX idx_users_email_lower ON users (LOWER(email));
SELECT * FROM users WHERE LOWER(email) = 'john@example.com';

-- ✅ Better: Use functional index
CREATE INDEX idx_users_email ON users (email);
SELECT * FROM users WHERE email = 'john@example.com';
```

## Caching Patterns

### Cache-Aside
```typescript
async function getUser(id: string) {
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);

  const user = await db.users.findById(id);
  if (user) {
    await redis.setex(`user:${id}`, 3600, JSON.stringify(user));
  }
  return user;
}
```

### Cache Invalidation
```typescript
async function updateUser(id: string, data: UpdateData) {
  const updated = await db.users.update(id, data);

  // Invalidate cache
  await redis.del(`user:${id}`);

  return updated;
}
```

## Authentication Patterns

### JWT Authentication
```typescript
import jwt from 'jsonwebtoken';

interface TokenPayload {
  userId: string;
  email: string;
}

function generateTokens(payload: TokenPayload) {
  const accessToken = jwt.sign(payload, ACCESS_SECRET, {
    expiresIn: '15m'
  });

  const refreshToken = jwt.sign(payload, REFRESH_SECRET, {
    expiresIn: '7d'
  });

  return { accessToken, refreshToken };
}

async function authenticateToken(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, ACCESS_SECRET) as TokenPayload;
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(403).json({ error: 'Invalid token' });
  }
}
```

## Error Handling Patterns

### Custom Error Classes
```typescript
class AppError extends Error {
  constructor(
    public statusCode: number,
    public code: string,
    message: string,
    public isOperational = true
  ) {
    super(message);
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

class NotFoundError extends AppError {
  constructor(resource: string) {
    super(404, 'NOT_FOUND', `${resource} not found`);
  }
}

class ValidationError extends AppError {
  constructor(message: string, public details?: any[]) {
    super(400, 'VALIDATION_ERROR', message);
  }
}
```

### Error Middleware
```typescript
app.use((err: Error, req, res, next) => {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: {
        code: err.code,
        message: err.message,
        details: err.details
      }
    });
  }

  // Log unexpected errors
  logger.error('Unexpected error:', err);

  res.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred'
    }
  });
});
```

## Async Patterns

### Promise-Based
```typescript
async function processOrder(orderId: string) {
  try {
    const order = await orderRepository.findById(orderId);
    const payment = await paymentService.process(order);
    const inventory = await inventoryService.reserve(order.items);

    await orderRepository.updateStatus(orderId, 'confirmed');

    return { order, payment, inventory };
  } catch (error) {
    await orderRepository.updateStatus(orderId, 'failed');
    throw error;
  }
}
```

### Parallel Execution
```typescript
async function getUserDashboard(userId: string) {
  const [user, orders, preferences] = await Promise.all([
    userService.getUser(userId),
    orderService.getUserOrders(userId),
    preferenceService.getUserPreferences(userId)
  ]);

  return { user, orders, preferences };
}
```

## Rate Limiting

### Simple In-Memory
```typescript
const requests = new Map<string, number[]>();

function rateLimit(maxRequests: number, windowMs: number) {
  return (req, res, next) => {
    const key = req.ip;
    const now = Date.now();
    const windowStart = now - windowMs;

    const userRequests = requests.get(key) || [];
    const recentRequests = userRequests.filter(time => time > windowStart);

    if (recentRequests.length >= maxRequests) {
      return res.status(429).json({
        error: 'Too many requests'
      });
    }

    recentRequests.push(now);
    requests.set(key, recentRequests);
    next();
  };
}
```

### Redis-Based
```typescript
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';

const limiter = rateLimit({
  store: new RedisStore({ client: redis }),
  windowMs: 15 * 60 * 1000,
  max: 100
});
```

## Validation Patterns

### Using Zod
```typescript
import { z } from 'zod';

const userSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  age: z.number().min(0).max(150).optional(),
  role: z.enum(['user', 'admin', 'moderator'])
});

function validateRequest(schema: z.Schema) {
  return (req, res, next) => {
    try {
      req.body = schema.parse(req.body);
      next();
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({
          error: {
            code: 'VALIDATION_ERROR',
            details: error.errors
          }
        });
      }
      next(error);
    }
  };
}

app.post('/users', validateRequest(userSchema), createUser);
```

## Logging Patterns

### Structured Logging
```typescript
import winston from 'winston';

const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'app.log' })
  ]
});

logger.info('User created', {
  userId: user.id,
  email: user.email,
  requestId: req.id
});
```

## References

- Express.js: https://expressjs.com/
- NestJS: https://nestjs.com/
- FastAPI: https://fastapi.tiangolo.com/
- Node.js Best Practices: https://github.com/goldbergyoni/nodebestpractices
