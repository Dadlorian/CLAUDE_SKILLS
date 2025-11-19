# Security Checklist

## OWASP Top 10 Protection

### 1. Broken Access Control
- [ ] Implement authentication on all protected routes
- [ ] Verify user authorization for each resource access
- [ ] Use RBAC or ABAC for permissions
- [ ] Deny by default (whitelist approach)
- [ ] Prevent IDOR attacks (validate ownership)
- [ ] Disable directory listing
- [ ] Log access control failures

### 2. Cryptographic Failures
- [ ] Use HTTPS/TLS 1.3 for all traffic
- [ ] Hash passwords with bcrypt (12+ rounds) or Argon2
- [ ] Encrypt sensitive data at rest
- [ ] Use strong encryption algorithms (AES-256)
- [ ] Secure key management (use secrets manager)
- [ ] Rotate encryption keys regularly
- [ ] Don't store sensitive data unnecessarily

### 3. Injection
- [ ] Use parameterized queries (prevent SQL injection)
- [ ] Validate and sanitize all inputs
- [ ] Use ORM/query builders
- [ ] Escape output (prevent XSS)
- [ ] Use Content-Security-Policy header
- [ ] Validate file uploads (type, size, content)
- [ ] Use safe APIs (avoid eval, exec)

### 4. Insecure Design
- [ ] Threat modeling during design phase
- [ ] Security requirements defined early
- [ ] Principle of least privilege
- [ ] Defense in depth strategy
- [ ] Secure development lifecycle
- [ ] Security review before deployment

### 5. Security Misconfiguration
- [ ] Disable unnecessary features/ports
- [ ] Remove default credentials
- [ ] Use security headers (Helmet.js)
- [ ] Keep software updated
- [ ] Proper error handling (don't leak info)
- [ ] Secure cloud storage permissions
- [ ] Regular security audits

### 6. Vulnerable Components
- [ ] Regular dependency audits (npm audit)
- [ ] Automated updates (Dependabot)
- [ ] Monitor CVE databases
- [ ] Remove unused dependencies
- [ ] Verify package integrity
- [ ] Use Software Bill of Materials (SBOM)

### 7. Authentication Failures
- [ ] Multi-factor authentication
- [ ] Strong password policy (12+ chars, complexity)
- [ ] Account lockout after failed attempts
- [ ] Rate limiting on auth endpoints
- [ ] Secure session management
- [ ] Token expiration (short-lived access tokens)
- [ ] Secure password reset flow

### 8. Software and Data Integrity
- [ ] Code signing
- [ ] Verify third-party libraries
- [ ] Use lock files (package-lock.json)
- [ ] CI/CD pipeline security
- [ ] Integrity checks for updates
- [ ] Subresource Integrity (SRI) for CDNs

### 9. Security Logging & Monitoring
- [ ] Log security events (logins, access attempts)
- [ ] Monitor for suspicious patterns
- [ ] Set up security alerts
- [ ] Centralized log management
- [ ] Log retention policy
- [ ] Don't log sensitive data (passwords, tokens)
- [ ] Incident response plan

### 10. Server-Side Request Forgery
- [ ] Validate and sanitize URLs
- [ ] Whitelist allowed domains
- [ ] Disable HTTP redirects
- [ ] Use separate network for external requests
- [ ] Implement network segmentation

## Application Security

### Input Validation
- [ ] Validate all inputs (client and server)
- [ ] Use validation library (Zod, Joi)
- [ ] Whitelist valid inputs
- [ ] Sanitize user-generated content
- [ ] Validate file uploads
- [ ] Check Content-Type headers
- [ ] Limit input length

### Authentication
- [ ] Use proven libraries (Passport, NextAuth)
- [ ] Implement rate limiting
- [ ] Hash passwords before storage
- [ ] Use secure session management
- [ ] Implement CSRF protection
- [ ] Use secure cookies (httpOnly, secure, sameSite)
- [ ] Implement account lockout

### Authorization
- [ ] Check permissions on every request
- [ ] Implement resource-level authorization
- [ ] Use role-based access control
- [ ] Principle of least privilege
- [ ] Regular permission audits

### Data Protection
- [ ] Encrypt sensitive data at rest
- [ ] Use TLS for data in transit
- [ ] Secure API keys and secrets
- [ ] Don't store credit card data
- [ ] Implement data retention policies
- [ ] Secure backup encryption

## API Security

- [ ] Use HTTPS only
- [ ] Implement rate limiting
- [ ] Use API authentication (JWT, OAuth)
- [ ] Validate request/response schemas
- [ ] Implement CORS properly
- [ ] Use API versioning
- [ ] Monitor API usage
- [ ] Implement request signing

## Database Security

- [ ] Use parameterized queries
- [ ] Principle of least privilege for DB users
- [ ] Encrypt database backups
- [ ] Regular security patches
- [ ] Monitor database access
- [ ] Disable remote root access
- [ ] Use database firewall

## Infrastructure Security

- [ ] Keep systems updated
- [ ] Configure firewall rules
- [ ] Disable unnecessary services
- [ ] Use security groups/network policies
- [ ] Implement DDoS protection
- [ ] Regular security scans
- [ ] Backup and disaster recovery plan

## Security Headers

```javascript
// Helmet.js configuration
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  },
  frameguard: { action: 'deny' },
  noSniff: true,
  xssFilter: true,
}));
```

## Secrets Management

- [ ] Never commit secrets to git
- [ ] Use environment variables
- [ ] Use secrets manager (Vault, AWS Secrets)
- [ ] Rotate secrets regularly
- [ ] Audit secret access
- [ ] Encrypt secrets at rest

## Compliance

- [ ] GDPR compliance (if applicable)
- [ ] HIPAA compliance (if healthcare)
- [ ] PCI DSS (if handling payments)
- [ ] SOC 2 (for SaaS)
- [ ] Data residency requirements

## Security Testing

- [ ] Static Application Security Testing (SAST)
- [ ] Dynamic Application Security Testing (DAST)
- [ ] Dependency scanning
- [ ] Penetration testing (annually)
- [ ] Security code review
- [ ] Vulnerability scanning

## Incident Response

- [ ] Incident response plan
- [ ] Security incident contacts
- [ ] Backup and recovery procedures
- [ ] Communication plan
- [ ] Post-incident review process

## Training

- [ ] Security awareness training
- [ ] Secure coding training
- [ ] Phishing awareness
- [ ] Regular security updates
