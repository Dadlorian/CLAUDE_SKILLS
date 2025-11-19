# Security Best Practices for Embedded Analytics

## Overview

Comprehensive security guidelines for protecting embedded analytics implementations from common vulnerabilities and attacks.

## Authentication Security

### 1. Token-Based Authentication

```javascript
// Secure token generation
class SecureTokenGenerator {
  generateEmbedToken(user) {
    // Validate user session first
    if (!this.isValidSession(user.sessionId)) {
      throw new Error('Invalid session');
    }

    // Generate token with minimal claims
    const token = jwt.sign({
      // Required claims
      sub: user.id,
      iss: 'your-app.example.com',
      aud: 'bi-platform.example.com',
      exp: Math.floor(Date.now() / 1000) + (30 * 60), // 30 minutes
      iat: Math.floor(Date.now() / 1000),
      jti: crypto.randomBytes(16).toString('hex'), // Unique token ID

      // Application claims (minimal)
      tenant_id: user.tenantId,
      email: user.email,
      roles: [user.role], // Don't include all user data

      // RLS context
      rls: {
        tenant_id: user.tenantId,
        department: user.department
      }
    }, process.env.JWT_SECRET, {
      algorithm: 'HS256',
      header: {
        typ: 'JWT',
        alg: 'HS256'
      }
    });

    // Log token generation for audit
    this.auditLog.log({
      event: 'token_generated',
      userId: user.id,
      tenantId: user.tenantId,
      tokenId: token.jti,
      expiresAt: new Date((Date.now() / 1000 + 1800) * 1000)
    });

    return token;
  }

  // Verify token before use
  verifyToken(token) {
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET, {
        algorithms: ['HS256'],
        clockTolerance: 10 // 10 seconds clock skew tolerance
      });

      // Check if token has been revoked
      if (this.isTokenRevoked(decoded.jti)) {
        throw new Error('Token has been revoked');
      }

      return decoded;
    } catch (error) {
      this.auditLog.log({
        event: 'token_verification_failed',
        error: error.message,
        token: token.substring(0, 20) + '...'
      });

      throw error;
    }
  }

  // Revoke token (for logout, security incidents)
  async revokeToken(tokenId) {
    await redis.sadd('revoked_tokens', tokenId);
    await redis.expire('revoked_tokens', 86400); // 24 hours
  }

  async isTokenRevoked(tokenId) {
    return await redis.sismember('revoked_tokens', tokenId);
  }
}
```

### 2. Rate Limiting

```javascript
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');

// Rate limit token generation
const tokenRateLimiter = rateLimit({
  store: new RedisStore({
    client: redis,
    prefix: 'rl:token:'
  }),
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10, // 10 tokens per 15 minutes per user
  keyGenerator: (req) => {
    return req.user.id; // Rate limit per user
  },
  handler: (req, res) => {
    auditLog.log({
      event: 'rate_limit_exceeded',
      userId: req.user.id,
      ip: req.ip,
      endpoint: '/api/embed-token'
    });

    res.status(429).json({
      error: 'Too many token requests. Please try again later.',
      retryAfter: 900 // seconds
    });
  }
});

app.post('/api/embed-token', tokenRateLimiter, async (req, res) => {
  const token = tokenGenerator.generateEmbedToken(req.user);
  res.json({ token });
});

// Global API rate limiting
const apiRateLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 100, // 100 requests per minute
  standardHeaders: true,
  legacyHeaders: false
});

app.use('/api/', apiRateLimiter);
```

### 3. Session Security

```javascript
const session = require('express-session');
const RedisStore = require('connect-redis').default;

app.use(session({
  store: new RedisStore({
    client: redis,
    prefix: 'sess:'
  }),
  secret: process.env.SESSION_SECRET,
  name: 'sessionId', // Don't use default name
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true, // HTTPS only
    httpOnly: true, // Prevent JavaScript access
    sameSite: 'strict', // CSRF protection
    maxAge: 24 * 60 * 60 * 1000, // 24 hours
    domain: '.example.com' // Set appropriate domain
  },
  rolling: true // Extend session on activity
}));

// Session validation middleware
function validateSession(req, res, next) {
  if (!req.session || !req.session.userId) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  // Check session hasn't been revoked
  if (req.session.revoked) {
    req.session.destroy();
    return res.status(401).json({ error: 'Session revoked' });
  }

  // Verify session IP (optional, can break mobile)
  if (req.session.ip && req.session.ip !== req.ip) {
    auditLog.log({
      event: 'session_ip_mismatch',
      userId: req.session.userId,
      sessionIp: req.session.ip,
      requestIp: req.ip
    });
    // Optionally revoke session
  }

  next();
}
```

---

## Data Security

### 1. Row-Level Security (RLS)

```sql
-- PostgreSQL RLS policies
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their tenant's data
CREATE POLICY tenant_isolation ON sales
  FOR ALL
  TO app_user
  USING (tenant_id = current_setting('app.current_tenant')::int);

-- Policy: Admins can see all data
CREATE POLICY admin_all_access ON sales
  FOR ALL
  TO admin_user
  USING (true);

-- Set tenant context in connection
-- This MUST come from server-side user context, never client
SET app.current_tenant = '123';

-- Verify RLS is working
-- Should only return tenant 123 data
SELECT * FROM sales;
```

```javascript
// Application-level RLS enforcement
class SecureDataAccess {
  async executeQuery(user, query, params) {
    // NEVER trust client-provided tenant ID
    const tenantId = user.tenantId; // From authenticated session

    // Set RLS context
    await this.db.query('SET app.current_tenant = $1', [tenantId]);

    // Execute query with RLS applied
    const result = await this.db.query(query, params);

    // Verify all returned rows match tenant (paranoid check)
    if (process.env.NODE_ENV !== 'production') {
      const invalidRows = result.rows.filter(row =>
        row.tenant_id && row.tenant_id !== tenantId
      );

      if (invalidRows.length > 0) {
        throw new Error('RLS violation detected!');
      }
    }

    return result.rows;
  }
}
```

### 2. SQL Injection Prevention

```javascript
// NEVER construct SQL from user input
// BAD:
const query = `SELECT * FROM sales WHERE date >= '${req.query.startDate}'`;

// GOOD: Use parameterized queries
const query = 'SELECT * FROM sales WHERE date >= $1';
const result = await db.query(query, [req.query.startDate]);

// For dynamic filters, use whitelisting
function buildFilterQuery(allowedFilters, userFilters) {
  const whereClauses = [];
  const params = [];
  let paramIndex = 1;

  Object.entries(userFilters).forEach(([field, value]) => {
    // Whitelist allowed fields
    if (!allowedFilters.includes(field)) {
      throw new Error(`Invalid filter field: ${field}`);
    }

    whereClauses.push(`${field} = $${paramIndex}`);
    params.push(value);
    paramIndex++;
  });

  const query = `
    SELECT * FROM sales
    WHERE tenant_id = $${paramIndex}
    ${whereClauses.length > 0 ? 'AND ' + whereClauses.join(' AND ') : ''}
  `;

  return { query, params: [...params, tenantId] };
}

// Usage
const allowedFilters = ['product_id', 'category', 'region'];
const { query, params } = buildFilterQuery(allowedFilters, req.query.filters);
const result = await db.query(query, params);
```

### 3. Data Masking and Redaction

```javascript
// Mask sensitive data based on user role
class DataMasking {
  maskData(data, user) {
    return data.map(row => {
      const masked = { ...row };

      // Mask PII for non-admin users
      if (!user.roles.includes('admin')) {
        if (masked.email) {
          masked.email = this.maskEmail(masked.email);
        }
        if (masked.phone) {
          masked.phone = this.maskPhone(masked.phone);
        }
        if (masked.ssn) {
          delete masked.ssn; // Remove completely
        }
      }

      // Mask financial data for non-finance users
      if (!user.roles.includes('finance')) {
        if (masked.salary) {
          delete masked.salary;
        }
        if (masked.revenue) {
          masked.revenue = Math.round(masked.revenue / 1000) * 1000; // Round to nearest 1000
        }
      }

      return masked;
    });
  }

  maskEmail(email) {
    const [username, domain] = email.split('@');
    const maskedUsername = username[0] + '*'.repeat(username.length - 2) + username[username.length - 1];
    return `${maskedUsername}@${domain}`;
  }

  maskPhone(phone) {
    return phone.replace(/(\d{3})(\d{3})(\d{4})/, '***-***-$3');
  }
}
```

---

## Network Security

### 1. HTTPS Enforcement

```javascript
// Force HTTPS
app.use((req, res, next) => {
  if (req.protocol !== 'https' && process.env.NODE_ENV === 'production') {
    return res.redirect(301, `https://${req.headers.host}${req.url}`);
  }
  next();
});

// HSTS header
app.use((req, res, next) => {
  res.setHeader(
    'Strict-Transport-Security',
    'max-age=31536000; includeSubDomains; preload'
  );
  next();
});
```

### 2. CORS Configuration

```javascript
const cors = require('cors');

// Strict CORS policy
app.use(cors({
  origin: (origin, callback) => {
    const allowedOrigins = [
      'https://app.example.com',
      'https://admin.example.com'
    ];

    // Allow if origin is in whitelist or no origin (same-origin)
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      auditLog.log({
        event: 'cors_violation',
        origin: origin,
        ip: req.ip
      });

      callback(new Error('CORS not allowed'));
    }
  },
  credentials: true, // Allow cookies
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  exposedHeaders: ['X-Total-Count'],
  maxAge: 86400 // 24 hours
}));
```

### 3. Content Security Policy (CSP)

```javascript
const helmet = require('helmet');

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: [
        "'self'",
        'https://tableau.example.com',
        'https://app.powerbi.com',
        'https://cdn.example.com'
      ],
      styleSrc: [
        "'self'",
        "'unsafe-inline'", // Required for some BI tools
        'https://fonts.googleapis.com'
      ],
      imgSrc: [
        "'self'",
        'data:',
        'https://tableau.example.com',
        'https://app.powerbi.com'
      ],
      frameSrc: [
        "'self'",
        'https://tableau.example.com',
        'https://app.powerbi.com'
      ],
      connectSrc: [
        "'self'",
        'https://api.example.com',
        'https://tableau.example.com'
      ],
      fontSrc: [
        "'self'",
        'https://fonts.gstatic.com'
      ],
      objectSrc: ["'none'"],
      upgradeInsecureRequests: []
    }
  },
  xFrameOptions: { action: 'deny' }, // Prevent clickjacking
  xContentTypeOptions: true,
  referrerPolicy: { policy: 'strict-origin-when-cross-origin' }
}));
```

---

## Input Validation

### 1. Request Validation

```javascript
const Joi = require('joi');

// Define schemas
const schemas = {
  generateToken: Joi.object({
    dashboardId: Joi.string().uuid().required(),
    filters: Joi.object({
      startDate: Joi.date().iso().max('now'),
      endDate: Joi.date().iso().min(Joi.ref('startDate')),
      region: Joi.string().valid('north', 'south', 'east', 'west'),
      productId: Joi.number().integer().positive()
    }).optional()
  }),

  queryData: Joi.object({
    query: Joi.string().max(1000).required(),
    params: Joi.array().items(
      Joi.alternatives().try(
        Joi.string(),
        Joi.number(),
        Joi.date()
      )
    ).max(10)
  })
};

// Validation middleware
function validate(schema) {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.body, {
      abortEarly: false,
      stripUnknown: true
    });

    if (error) {
      const errors = error.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message
      }));

      return res.status(400).json({
        error: 'Validation failed',
        details: errors
      });
    }

    req.validatedBody = value;
    next();
  };
}

// Usage
app.post('/api/embed-token',
  validateSession,
  validate(schemas.generateToken),
  async (req, res) => {
    const token = generateToken(req.user, req.validatedBody);
    res.json({ token });
  }
);
```

### 2. Sanitization

```javascript
const DOMPurify = require('isomorphic-dompurify');

// Sanitize HTML inputs
function sanitizeHTML(dirty) {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a'],
    ALLOWED_ATTR: ['href']
  });
}

// Sanitize SQL identifiers (table/column names)
function sanitizeSQLIdentifier(identifier) {
  // Only allow alphanumeric and underscore
  if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(identifier)) {
    throw new Error('Invalid SQL identifier');
  }

  // Whitelist allowed identifiers
  const allowedIdentifiers = ['sales', 'customers', 'products', 'orders'];
  if (!allowedIdentifiers.includes(identifier)) {
    throw new Error('SQL identifier not in whitelist');
  }

  return identifier;
}
```

---

## Secrets Management

### 1. Environment Variables

```javascript
// .env file (NEVER commit to git)
JWT_SECRET=use-a-long-random-string-here-minimum-32-chars
DB_PASSWORD=secure-database-password
BI_API_KEY=tableau-or-powerbi-api-key
ENCRYPTION_KEY=encryption-key-for-sensitive-data

// Load with dotenv
require('dotenv').config();

// Validate required secrets on startup
const requiredSecrets = [
  'JWT_SECRET',
  'DB_PASSWORD',
  'BI_API_KEY',
  'ENCRYPTION_KEY'
];

requiredSecrets.forEach(secret => {
  if (!process.env[secret]) {
    console.error(`Missing required secret: ${secret}`);
    process.exit(1);
  }

  // Validate secret strength
  if (process.env[secret].length < 32) {
    console.error(`Secret ${secret} is too short (minimum 32 characters)`);
    process.exit(1);
  }
});
```

### 2. Secrets Rotation

```javascript
class SecretsManager {
  constructor() {
    this.currentSecret = process.env.JWT_SECRET;
    this.previousSecret = process.env.JWT_SECRET_PREVIOUS;
  }

  // Sign with current secret
  sign(payload) {
    return jwt.sign(payload, this.currentSecret);
  }

  // Verify with current secret, fallback to previous
  verify(token) {
    try {
      return jwt.verify(token, this.currentSecret);
    } catch (error) {
      if (this.previousSecret) {
        try {
          const payload = jwt.verify(token, this.previousSecret);

          // Log usage of old secret
          console.warn('Token signed with previous secret');

          return payload;
        } catch (secondError) {
          throw error; // Throw original error
        }
      }

      throw error;
    }
  }

  // Rotate secrets
  async rotate() {
    // Fetch new secret from secrets manager (AWS Secrets Manager, etc.)
    const newSecret = await this.fetchNewSecret();

    // Update environment
    this.previousSecret = this.currentSecret;
    this.currentSecret = newSecret;

    console.log('Secrets rotated successfully');

    // Schedule cleanup of previous secret
    setTimeout(() => {
      this.previousSecret = null;
    }, 7 * 24 * 60 * 60 * 1000); // 7 days
  }
}
```

### 3. AWS Secrets Manager Integration

```javascript
const AWS = require('aws-sdk');
const secretsManager = new AWS.SecretsManager({ region: 'us-east-1' });

async function getSecret(secretName) {
  try {
    const data = await secretsManager.getSecretValue({
      SecretId: secretName
    }).promise();

    if ('SecretString' in data) {
      return JSON.parse(data.SecretString);
    } else {
      const buff = Buffer.from(data.SecretBinary, 'base64');
      return JSON.parse(buff.toString('ascii'));
    }
  } catch (error) {
    console.error('Error retrieving secret:', error);
    throw error;
  }
}

// Usage
async function initialize() {
  const secrets = await getSecret('prod/analytics/secrets');

  process.env.JWT_SECRET = secrets.JWT_SECRET;
  process.env.DB_PASSWORD = secrets.DB_PASSWORD;
  process.env.BI_API_KEY = secrets.BI_API_KEY;
}
```

---

## Audit Logging

### 1. Comprehensive Audit Log

```javascript
class AuditLogger {
  async log(event) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      event: event.type,
      userId: event.userId,
      tenantId: event.tenantId,
      ip: event.ip,
      userAgent: event.userAgent,
      resource: event.resource,
      action: event.action,
      result: event.result,
      metadata: event.metadata,

      // Security context
      sessionId: event.sessionId,
      tokenId: event.tokenId,

      // Request context
      requestId: event.requestId,
      method: event.method,
      path: event.path
    };

    // Log to database
    await db.auditLogs.insert(logEntry);

    // Also send to SIEM/logging service
    if (this.shouldAlertSecurity(event)) {
      await this.sendSecurityAlert(logEntry);
    }

    // Log to stdout for container logs
    console.log('AUDIT:', JSON.stringify(logEntry));
  }

  shouldAlertSecurity(event) {
    const securityEvents = [
      'unauthorized_access',
      'rls_violation',
      'rate_limit_exceeded',
      'suspicious_activity',
      'token_verification_failed',
      'session_hijacking_detected'
    ];

    return securityEvents.includes(event.type);
  }

  async sendSecurityAlert(logEntry) {
    // Send to security team, SIEM, etc.
    await axios.post('https://siem.example.com/alerts', logEntry);

    // Also send email for critical events
    if (logEntry.event === 'rls_violation') {
      await sendEmail({
        to: 'security@example.com',
        subject: `SECURITY ALERT: ${logEntry.event}`,
        body: JSON.stringify(logEntry, null, 2)
      });
    }
  }
}

// Usage throughout application
auditLog.log({
  type: 'embed_access',
  userId: user.id,
  tenantId: user.tenantId,
  resource: `dashboard:${dashboardId}`,
  action: 'view',
  result: 'success',
  ip: req.ip,
  userAgent: req.headers['user-agent'],
  sessionId: req.sessionID,
  requestId: req.id
});
```

---

## Security Headers

```javascript
// Comprehensive security headers
app.use((req, res, next) => {
  // Prevent XSS
  res.setHeader('X-XSS-Protection', '1; mode=block');

  // Prevent MIME sniffing
  res.setHeader('X-Content-Type-Options', 'nosniff');

  // Prevent clickjacking
  res.setHeader('X-Frame-Options', 'DENY');

  // Referrer policy
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');

  // Permissions policy
  res.setHeader('Permissions-Policy',
    'geolocation=(), microphone=(), camera=()'
  );

  // HSTS
  res.setHeader('Strict-Transport-Security',
    'max-age=31536000; includeSubDomains; preload'
  );

  next();
});
```

---

## Security Checklist

### Authentication & Authorization
- [ ] Token expiration implemented (< 1 hour)
- [ ] Token refresh mechanism secure
- [ ] Rate limiting on token generation
- [ ] Session management secure (HttpOnly, Secure, SameSite)
- [ ] Multi-factor authentication available
- [ ] Token revocation implemented

### Data Security
- [ ] RLS enforced at database level
- [ ] Never trust client-provided tenant ID
- [ ] SQL injection prevention (parameterized queries)
- [ ] Data masking for sensitive fields
- [ ] Encryption at rest
- [ ] Encryption in transit (HTTPS)

### Network Security
- [ ] HTTPS enforced (no HTTP)
- [ ] CORS properly configured
- [ ] CSP headers implemented
- [ ] Security headers set
- [ ] Certificate pinning (mobile)
- [ ] WAF configured (if applicable)

### Secrets Management
- [ ] Secrets not in code/git
- [ ] Environment variables or secrets manager
- [ ] Secrets rotation policy
- [ ] Minimum 32 character secrets
- [ ] Different secrets per environment

### Monitoring & Auditing
- [ ] Comprehensive audit logging
- [ ] Security event alerting
- [ ] Regular security audits
- [ ] Penetration testing scheduled
- [ ] Vulnerability scanning automated
- [ ] Incident response plan documented

### Code Security
- [ ] Input validation on all endpoints
- [ ] Output sanitization
- [ ] Dependency vulnerability scanning
- [ ] Regular security patches
- [ ] Code review process
- [ ] Static analysis tools

### Compliance
- [ ] GDPR compliance (if applicable)
- [ ] SOC 2 compliance (if applicable)
- [ ] HIPAA compliance (if applicable)
- [ ] Data retention policies
- [ ] Right to deletion implemented
- [ ] Privacy policy updated
