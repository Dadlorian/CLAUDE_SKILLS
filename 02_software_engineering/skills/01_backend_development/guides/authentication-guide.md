# Authentication & Authorization Guide

Complete guide to implementing secure authentication and authorization in Node.js applications.

## JWT Authentication

### Setup

```bash
npm install jsonwebtoken bcrypt
npm install -D @types/jsonwebtoken @types/bcrypt
```

### Password Hashing

```typescript
import bcrypt from 'bcrypt';

const SALT_ROUNDS = 12;

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

export async function verifyPassword(
  password: string,
  hash: string
): Promise<boolean> {
  return bcrypt.compare(password, hash);
}
```

### Token Generation

```typescript
import jwt from 'jsonwebtoken';

interface TokenPayload {
  userId: string;
  email: string;
  role: string;
}

const ACCESS_SECRET = process.env.JWT_ACCESS_SECRET!;
const REFRESH_SECRET = process.env.JWT_REFRESH_SECRET!;

export function generateAccessToken(payload: TokenPayload): string {
  return jwt.sign(payload, ACCESS_SECRET, {
    expiresIn: '15m',
    issuer: 'your-app',
    audience: 'your-app-users',
  });
}

export function generateRefreshToken(payload: TokenPayload): string {
  return jwt.sign(payload, REFRESH_SECRET, {
    expiresIn: '7d',
    issuer: 'your-app',
    audience: 'your-app-users',
  });
}

export function verifyAccessToken(token: string): TokenPayload {
  return jwt.verify(token, ACCESS_SECRET) as TokenPayload;
}

export function verifyRefreshToken(token: string): TokenPayload {
  return jwt.verify(token, REFRESH_SECRET) as TokenPayload;
}
```

### Authentication Middleware

```typescript
import { Request, Response, NextFunction } from 'express';

export interface AuthRequest extends Request {
  user?: TokenPayload;
}

export function authenticateToken(
  req: AuthRequest,
  res: Response,
  next: NextFunction
) {
  const authHeader = req.headers.authorization;
  const token = authHeader?.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const payload = verifyAccessToken(token);
    req.user = payload;
    next();
  } catch (error) {
    if (error instanceof jwt.TokenExpiredError) {
      return res.status(401).json({ error: 'Token expired' });
    }
    return res.status(403).json({ error: 'Invalid token' });
  }
}
```

### Login/Register Endpoints

```typescript
// auth.controller.ts
import { Request, Response } from 'express';

export class AuthController {
  async register(req: Request, res: Response) {
    try {
      const { email, password, name } = req.body;

      // Check if user exists
      const existing = await userRepository.findByEmail(email);
      if (existing) {
        return res.status(409).json({ error: 'Email already exists' });
      }

      // Hash password
      const passwordHash = await hashPassword(password);

      // Create user
      const user = await userRepository.create({
        email,
        name,
        passwordHash,
      });

      // Generate tokens
      const accessToken = generateAccessToken({
        userId: user.id,
        email: user.email,
        role: user.role,
      });

      const refreshToken = generateRefreshToken({
        userId: user.id,
        email: user.email,
        role: user.role,
      });

      // Store refresh token
      await refreshTokenRepository.create({
        token: refreshToken,
        userId: user.id,
        expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      });

      res.status(201).json({
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
        },
        accessToken,
        refreshToken,
      });
    } catch (error) {
      res.status(500).json({ error: 'Registration failed' });
    }
  }

  async login(req: Request, res: Response) {
    try {
      const { email, password } = req.body;

      // Find user
      const user = await userRepository.findByEmailWithPassword(email);
      if (!user) {
        return res.status(401).json({ error: 'Invalid credentials' });
      }

      // Verify password
      const isValid = await verifyPassword(password, user.passwordHash);
      if (!isValid) {
        return res.status(401).json({ error: 'Invalid credentials' });
      }

      // Generate tokens
      const accessToken = generateAccessToken({
        userId: user.id,
        email: user.email,
        role: user.role,
      });

      const refreshToken = generateRefreshToken({
        userId: user.id,
        email: user.email,
        role: user.role,
      });

      // Store refresh token
      await refreshTokenRepository.create({
        token: refreshToken,
        userId: user.id,
        expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      });

      res.json({
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
        },
        accessToken,
        refreshToken,
      });
    } catch (error) {
      res.status(500).json({ error: 'Login failed' });
    }
  }

  async refreshToken(req: Request, res: Response) {
    try {
      const { refreshToken } = req.body;

      if (!refreshToken) {
        return res.status(401).json({ error: 'Refresh token required' });
      }

      // Verify token
      const payload = verifyRefreshToken(refreshToken);

      // Check if token exists and not revoked
      const storedToken = await refreshTokenRepository.findByToken(refreshToken);
      if (!storedToken || storedToken.revoked) {
        return res.status(401).json({ error: 'Invalid refresh token' });
      }

      // Generate new access token
      const newAccessToken = generateAccessToken({
        userId: payload.userId,
        email: payload.email,
        role: payload.role,
      });

      res.json({ accessToken: newAccessToken });
    } catch (error) {
      res.status(401).json({ error: 'Invalid refresh token' });
    }
  }

  async logout(req: AuthRequest, res: Response) {
    try {
      const { refreshToken } = req.body;

      if (refreshToken) {
        // Revoke refresh token
        await refreshTokenRepository.revoke(refreshToken);
      }

      res.json({ message: 'Logged out successfully' });
    } catch (error) {
      res.status(500).json({ error: 'Logout failed' });
    }
  }
}
```

## Role-Based Access Control (RBAC)

### Authorization Middleware

```typescript
export function authorize(...allowedRoles: string[]) {
  return (req: AuthRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
}

// Usage
router.delete(
  '/users/:id',
  authenticateToken,
  authorize('admin'),
  userController.delete
);

router.patch(
  '/posts/:id',
  authenticateToken,
  authorize('admin', 'editor'),
  postController.update
);
```

### Resource-Based Authorization

```typescript
export function authorizeResource(
  resourceGetter: (req: AuthRequest) => Promise<{ userId: string }>
) {
  return async (req: AuthRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
      const resource = await resourceGetter(req);

      // Allow admins or resource owners
      if (req.user.role === 'admin' || req.user.userId === resource.userId) {
        return next();
      }

      res.status(403).json({ error: 'Not authorized to access this resource' });
    } catch (error) {
      next(error);
    }
  };
}

// Usage
router.patch(
  '/posts/:id',
  authenticateToken,
  authorizeResource(async (req) => {
    const post = await postRepository.findById(req.params.id);
    if (!post) throw new NotFoundError('Post not found');
    return { userId: post.authorId };
  }),
  postController.update
);
```

## OAuth 2.0 Integration

### Google OAuth

```bash
npm install passport passport-google-oauth20
npm install -D @types/passport @types/passport-google-oauth20
```

```typescript
import passport from 'passport';
import { Strategy as GoogleStrategy } from 'passport-google-oauth20';

passport.use(
  new GoogleStrategy(
    {
      clientID: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      callbackURL: '/auth/google/callback',
    },
    async (accessToken, refreshToken, profile, done) => {
      try {
        // Find or create user
        let user = await userRepository.findByGoogleId(profile.id);

        if (!user) {
          user = await userRepository.create({
            googleId: profile.id,
            email: profile.emails?.[0].value,
            name: profile.displayName,
            avatar: profile.photos?.[0].value,
          });
        }

        done(null, user);
      } catch (error) {
        done(error);
      }
    }
  )
);

// Routes
router.get('/auth/google', passport.authenticate('google', {
  scope: ['profile', 'email'],
}));

router.get('/auth/google/callback',
  passport.authenticate('google', { session: false }),
  (req, res) => {
    const user = req.user as User;

    const accessToken = generateAccessToken({
      userId: user.id,
      email: user.email,
      role: user.role,
    });

    // Redirect with token
    res.redirect(`${process.env.FRONTEND_URL}/auth/callback?token=${accessToken}`);
  }
);
```

## Rate Limiting (Brute Force Protection)

```typescript
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import Redis from 'ioredis';

const redis = new Redis();

// General API rate limit
export const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // 100 requests per window
  standardHeaders: true,
  legacyHeaders: false,
});

// Strict rate limit for auth endpoints
export const authLimiter = rateLimit({
  store: new RedisStore({
    client: redis,
    prefix: 'rl:auth:',
  }),
  windowMs: 15 * 60 * 1000,
  max: 5, // 5 attempts per 15 minutes
  skipSuccessfulRequests: true, // Don't count successful logins
  handler: (req, res) => {
    res.status(429).json({
      error: 'Too many login attempts. Please try again later.',
    });
  },
});

// Usage
app.use('/api', apiLimiter);
app.use('/auth/login', authLimiter);
app.use('/auth/register', authLimiter);
```

## Security Best Practices

### Password Requirements

```typescript
import { z } from 'zod';

const passwordSchema = z
  .string()
  .min(12, 'Password must be at least 12 characters')
  .regex(/[A-Z]/, 'Password must contain uppercase letter')
  .regex(/[a-z]/, 'Password must contain lowercase letter')
  .regex(/[0-9]/, 'Password must contain number')
  .regex(/[^A-Za-z0-9]/, 'Password must contain special character');
```

### Account Lockout

```typescript
const MAX_FAILED_ATTEMPTS = 5;
const LOCKOUT_DURATION = 30 * 60 * 1000; // 30 minutes

async function handleFailedLogin(userId: string) {
  const user = await userRepository.findById(userId);

  user.failedLoginAttempts += 1;

  if (user.failedLoginAttempts >= MAX_FAILED_ATTEMPTS) {
    user.lockedUntil = new Date(Date.now() + LOCKOUT_DURATION);
  }

  await userRepository.update(userId, user);
}

async function handleSuccessfulLogin(userId: string) {
  await userRepository.update(userId, {
    failedLoginAttempts: 0,
    lockedUntil: null,
    lastLoginAt: new Date(),
  });
}
```

### Security Headers

```typescript
import helmet from 'helmet';

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  },
}));
```

## Testing Authentication

```typescript
describe('Authentication', () => {
  describe('POST /auth/register', () => {
    it('should register new user', async () => {
      const response = await request(app)
        .post('/auth/register')
        .send({
          email: 'test@example.com',
          password: 'SecurePass123!',
          name: 'Test User',
        })
        .expect(201);

      expect(response.body.user).toBeDefined();
      expect(response.body.accessToken).toBeDefined();
      expect(response.body.refreshToken).toBeDefined();
    });

    it('should reject weak password', async () => {
      await request(app)
        .post('/auth/register')
        .send({
          email: 'test@example.com',
          password: '123',
          name: 'Test',
        })
        .expect(400);
    });
  });

  describe('POST /auth/login', () => {
    it('should login with valid credentials', async () => {
      const response = await request(app)
        .post('/auth/login')
        .send({
          email: 'test@example.com',
          password: 'SecurePass123!',
        })
        .expect(200);

      expect(response.body.accessToken).toBeDefined();
    });

    it('should reject invalid credentials', async () => {
      await request(app)
        .post('/auth/login')
        .send({
          email: 'test@example.com',
          password: 'wrongpassword',
        })
        .expect(401);
    });
  });

  describe('Protected routes', () => {
    let token: string;

    beforeEach(async () => {
      const response = await request(app)
        .post('/auth/login')
        .send({
          email: 'test@example.com',
          password: 'SecurePass123!',
        });

      token = response.body.accessToken;
    });

    it('should access protected route with valid token', async () => {
      await request(app)
        .get('/api/profile')
        .set('Authorization', `Bearer ${token}`)
        .expect(200);
    });

    it('should reject request without token', async () => {
      await request(app).get('/api/profile').expect(401);
    });
  });
});
```

## References

- OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- JWT.io: https://jwt.io/
- Passport.js: http://www.passportjs.org/
