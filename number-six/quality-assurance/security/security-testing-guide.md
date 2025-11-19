# Security Testing Guide
## Comprehensive Application Security Testing Strategy

---

## 🎯 Overview

Security testing is **critical** to protecting your application, users, and business from threats. This guide covers the complete security testing lifecycle based on OWASP, NIST, and industry best practices.

**Goal**: Identify and fix security vulnerabilities before attackers can exploit them.

---

## 🛡️ Security Testing Types

### 1. SAST (Static Application Security Testing)

**What**: Analyze source code without executing it

**Tools**:
- **JavaScript/TypeScript**: ESLint security plugins, Semgrep, SonarQube
- **Python**: Bandit, Semgrep, Pyre
- **Go**: gosec, staticcheck
- **Multi-language**: Snyk Code, CodeQL (GitHub), Checkmarx

**When**: Every commit (in CI/CD)

**Example**:
```yaml
# .github/workflows/security.yml
- name: Run Semgrep
  uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/owasp-top-ten
      p/javascript
      p/typescript
```

**Common Findings**:
- SQL injection vulnerabilities
- XSS vulnerabilities
- Hardcoded secrets
- Insecure cryptography
- Path traversal
- Command injection

### 2. DAST (Dynamic Application Security Testing)

**What**: Test running application by simulating attacks

**Tools**:
- OWASP ZAP (free, open-source)
- Burp Suite Professional
- Acunetix
- Netsparker

**When**: After deployment to staging

**Example**:
```bash
# OWASP ZAP scan
docker run -v $(pwd):/zap/wrk/:rw \
  owasp/zap2docker-stable \
  zap-baseline.py \
  -t https://staging.example.com \
  -r zap-report.html
```

**Common Findings**:
- Authentication bypass
- Session management issues
- Insecure configurations
- Missing security headers
- HTTPS/TLS issues

### 3. IAST (Interactive Application Security Testing)

**What**: Monitor application during runtime using agents

**Tools**:
- Contrast Security
- Hdiv
- Quotium Seeker

**When**: During integration/E2E testing

**Benefits**:
- Low false positives
- Precise vulnerability location
- Real-time feedback

### 4. SCA (Software Composition Analysis)

**What**: Scan dependencies for known vulnerabilities

**Tools**:
- Snyk
- Dependabot (GitHub)
- npm audit / pip-audit
- OWASP Dependency-Check

**When**: Every commit + weekly scans

**Example**:
```bash
# Scan dependencies
npm audit --audit-level=high

# Or use Snyk
snyk test --severity-threshold=high
```

### 5. Container Security Scanning

**What**: Scan Docker images for vulnerabilities

**Tools**:
- Trivy (free, comprehensive)
- Snyk Container
- Aqua Security
- Clair

**When**: On image build

**Example**:
```bash
# Scan with Trivy
trivy image myapp:latest \
  --severity HIGH,CRITICAL \
  --exit-code 1
```

---

## 🔍 OWASP Top 10 Testing

### A01:2021 – Broken Access Control

**Testing**:
```markdown
1. Horizontal Privilege Escalation:
   - Try accessing other users' data
   - Change user_id in requests
   - Test: GET /api/users/123/orders (try other user IDs)

2. Vertical Privilege Escalation:
   - Try accessing admin functions as regular user
   - Test: POST /api/admin/delete-user (as non-admin)

3. Missing Function Level Access Control:
   - Test all admin endpoints without auth
   - Test API endpoints directly (bypass UI)

4. Insecure Direct Object References:
   - Enumerate IDs (1, 2, 3, ...)
   - Test guessable IDs
   - Test UUID leakage
```

**Test Cases**:
```typescript
describe('Access Control', () => {
  it('should prevent users from accessing other users data', async () => {
    const user1Token = await login('user1');
    const user2Token = await login('user2');

    // User1 tries to access User2's data
    const response = await request(app)
      .get('/api/users/user2-id/orders')
      .set('Authorization', `Bearer ${user1Token}`);

    expect(response.status).toBe(403); // Forbidden
  });

  it('should prevent regular users from accessing admin endpoints', async () => {
    const userToken = await login('regularuser');

    const response = await request(app)
      .delete('/api/admin/users/123')
      .set('Authorization', `Bearer ${userToken}`);

    expect(response.status).toBe(403);
  });
});
```

### A02:2021 – Cryptographic Failures

**Testing**:
```markdown
1. Data in Transit:
   - Verify HTTPS enforcement
   - Check TLS version (>= TLS 1.2)
   - Test certificate validity
   - Check for mixed content

2. Data at Rest:
   - Verify database encryption
   - Check password hashing (bcrypt, Argon2)
   - Test key management
   - Verify secrets encryption

3. Sensitive Data Exposure:
   - Check API responses for passwords
   - Verify credit card masking
   - Test PII logging
   - Check error messages
```

**Test Cases**:
```typescript
describe('Cryptography', () => {
  it('should hash passwords with bcrypt', async () => {
    const user = await createUser({
      email: 'test@example.com',
      password: 'mypassword123'
    });

    // Password should not be stored in plain text
    expect(user.password).not.toBe('mypassword123');

    // Should start with bcrypt prefix
    expect(user.password).toMatch(/^\$2[aby]\$/);
  });

  it('should enforce HTTPS', async () => {
    const response = await request
      .get('http://example.com/api/users');

    // Should redirect to HTTPS
    expect(response.status).toBe(301);
    expect(response.headers.location).toMatch(/^https:/);
  });
});
```

### A03:2021 – Injection

**Testing**:
```markdown
1. SQL Injection:
   Test inputs:
   - ' OR '1'='1
   - '; DROP TABLE users--
   - ' UNION SELECT * FROM passwords--

2. NoSQL Injection:
   Test inputs:
   - {"$ne": null}
   - {"$gt": ""}

3. Command Injection:
   Test inputs:
   - ; ls -la
   - && cat /etc/passwd
   - | whoami

4. LDAP Injection:
   Test inputs:
   - *
   - admin)(&(password=*))
```

**Test Cases**:
```typescript
describe('SQL Injection Prevention', () => {
  it('should use parameterized queries', async () => {
    const maliciousEmail = "' OR '1'='1";

    const response = await request(app)
      .post('/api/login')
      .send({ email: maliciousEmail, password: 'anything' });

    // Should not bypass authentication
    expect(response.status).toBe(401);
  });

  it('should sanitize search inputs', async () => {
    const maliciousSearch = "'; DROP TABLE users--";

    const response = await request(app)
      .get(`/api/search?q=${encodeURIComponent(maliciousSearch)}`);

    // Should not execute SQL
    expect(response.status).not.toBe(500);

    // Verify users table still exists
    const users = await db.query('SELECT COUNT(*) FROM users');
    expect(users).toBeDefined();
  });
});
```

### A04:2021 – Insecure Design

**Testing**:
```markdown
1. Business Logic Flaws:
   - Try negative quantities in cart
   - Try applying discount multiple times
   - Test price manipulation
   - Test workflow bypasses

2. Rate Limiting:
   - Test brute force protection
   - Test API rate limits
   - Test concurrent requests

3. Trust Boundaries:
   - Test all user inputs
   - Verify server-side validation
   - Test client-side bypass
```

**Test Cases**:
```typescript
describe('Business Logic', () => {
  it('should prevent negative quantities in cart', async () => {
    const response = await request(app)
      .post('/api/cart/add')
      .send({
        productId: '123',
        quantity: -5 // Negative quantity
      });

    expect(response.status).toBe(400);
    expect(response.body.error).toContain('quantity must be positive');
  });

  it('should enforce rate limiting on login', async () => {
    const attempts = [];

    // Try 10 failed logins
    for (let i = 0; i < 10; i++) {
      attempts.push(
        request(app)
          .post('/api/login')
          .send({ email: 'test@example.com', password: 'wrong' })
      );
    }

    const responses = await Promise.all(attempts);
    const lastResponse = responses[responses.length - 1];

    // Should be rate limited
    expect(lastResponse.status).toBe(429); // Too Many Requests
  });
});
```

### A05:2021 – Security Misconfiguration

**Testing**:
```markdown
1. Default Credentials:
   - Try admin/admin, admin/password
   - Check default API keys
   - Test default database passwords

2. Unnecessary Features:
   - Check for debug endpoints in production
   - Verify directory listing disabled
   - Test for exposed .git folders

3. Error Handling:
   - Verify stack traces not exposed
   - Check for verbose error messages
   - Test 404/500 error pages

4. Security Headers:
   - Content-Security-Policy
   - X-Frame-Options
   - X-Content-Type-Options
   - Strict-Transport-Security
```

**Automated Test**:
```typescript
describe('Security Headers', () => {
  it('should include security headers', async () => {
    const response = await request(app).get('/');

    // HSTS
    expect(response.headers['strict-transport-security']).toBeDefined();

    // Prevent clickjacking
    expect(response.headers['x-frame-options']).toBe('DENY');

    // Prevent MIME sniffing
    expect(response.headers['x-content-type-options']).toBe('nosniff');

    // XSS Protection
    expect(response.headers['x-xss-protection']).toBe('1; mode=block');

    // CSP
    expect(response.headers['content-security-policy']).toBeDefined();
  });
});
```

### A06:2021 – Vulnerable and Outdated Components

**Testing**:
```bash
# Check for outdated dependencies
npm outdated

# Check for known vulnerabilities
npm audit
snyk test

# Check Docker base image
trivy image node:14-alpine
```

**CI/CD Integration**:
```yaml
- name: Security audit
  run: |
    npm audit --audit-level=high || exit 1
    snyk test --severity-threshold=high || exit 1
```

### A07:2021 – Identification and Authentication Failures

**Testing**:
```markdown
1. Weak Passwords:
   - Test password complexity requirements
   - Try common passwords (123456, password)
   - Verify minimum length

2. Credential Stuffing:
   - Test rate limiting on login
   - Verify CAPTCHA after failed attempts
   - Test account lockout

3. Session Management:
   - Test session timeout
   - Verify logout clears session
   - Test concurrent sessions
   - Check session fixation

4. Multi-Factor Authentication:
   - Test MFA bypass
   - Verify backup codes
   - Test MFA recovery
```

**Test Cases**:
```typescript
describe('Authentication', () => {
  it('should require strong passwords', async () => {
    const weakPasswords = [
      '123456',
      'password',
      'abc123',
      'short'
    ];

    for (const password of weakPasswords) {
      const response = await request(app)
        .post('/api/register')
        .send({
          email: 'test@example.com',
          password
        });

      expect(response.status).toBe(400);
      expect(response.body.error).toContain('password');
    }
  });

  it('should expire sessions after timeout', async () => {
    const { token } = await login('user@example.com');

    // Fast-forward time (mock)
    jest.advanceTimersByTime(30 * 60 * 1000); // 30 minutes

    const response = await request(app)
      .get('/api/profile')
      .set('Authorization', `Bearer ${token}`);

    expect(response.status).toBe(401); // Unauthorized
  });
});
```

### A08:2021 – Software and Data Integrity Failures

**Testing**:
```markdown
1. Unsigned/Unverified Updates:
   - Verify update signature
   - Test update source validation
   - Check integrity hashes

2. CI/CD Pipeline Security:
   - Verify pipeline authentication
   - Check secrets management
   - Test artifact signing

3. Deserialization:
   - Test untrusted data deserialization
   - Verify input validation
   - Check for RCE vectors
```

### A09:2021 – Security Logging and Monitoring Failures

**Testing**:
```markdown
1. Security Events Logged:
   - Failed login attempts
   - Privilege escalation attempts
   - Input validation failures
   - Access control failures

2. Log Protection:
   - Verify logs not world-readable
   - Check log tampering protection
   - Test log injection prevention

3. Alerting:
   - Test alert generation
   - Verify alert delivery
   - Check alert thresholds
```

**Test Cases**:
```typescript
describe('Security Logging', () => {
  it('should log failed login attempts', async () => {
    const logSpy = jest.spyOn(logger, 'warn');

    await request(app)
      .post('/api/login')
      .send({ email: 'test@example.com', password: 'wrong' });

    expect(logSpy).toHaveBeenCalledWith(
      'Failed login attempt',
      expect.objectContaining({
        email: 'test@example.com',
        ip: expect.any(String)
      })
    );
  });
});
```

### A10:2021 – Server-Side Request Forgery (SSRF)

**Testing**:
```markdown
1. URL Parameter Testing:
   Test inputs:
   - http://localhost
   - http://127.0.0.1
   - http://169.254.169.254 (AWS metadata)
   - file:///etc/passwd

2. Redirect Validation:
   - Test open redirects
   - Verify whitelist enforcement
   - Check protocol restrictions
```

**Test Cases**:
```typescript
describe('SSRF Prevention', () => {
  it('should block requests to internal IPs', async () => {
    const maliciousUrls = [
      'http://localhost/admin',
      'http://127.0.0.1:8080',
      'http://169.254.169.254/latest/meta-data'
    ];

    for (const url of maliciousUrls) {
      const response = await request(app)
        .post('/api/fetch-url')
        .send({ url });

      expect(response.status).toBe(400);
      expect(response.body.error).toContain('Invalid URL');
    }
  });
});
```

---

## 🔧 Security Testing Toolkit

### Essential Tools

```bash
# 1. SAST
npm install --save-dev eslint-plugin-security
semgrep --config=auto .

# 2. Dependency Scanning
npm audit
snyk test

# 3. DAST
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://example.com

# 4. Container Scanning
trivy image myapp:latest

# 5. Secret Scanning
git-secrets --scan
trufflehog git https://github.com/org/repo
```

### Security Test Checklist

```markdown
Authentication & Authorization:
- [ ] Test password strength requirements
- [ ] Test rate limiting on login
- [ ] Test session management
- [ ] Test MFA implementation
- [ ] Test privilege escalation
- [ ] Test access control on all endpoints

Input Validation:
- [ ] Test SQL injection
- [ ] Test XSS
- [ ] Test command injection
- [ ] Test path traversal
- [ ] Test SSRF
- [ ] Test deserialization attacks

Configuration:
- [ ] Test security headers
- [ ] Verify HTTPS enforcement
- [ ] Check error handling
- [ ] Test CORS configuration
- [ ] Verify CSP policy

Data Protection:
- [ ] Test password hashing
- [ ] Verify data encryption
- [ ] Test PII handling
- [ ] Check logging (no secrets)
- [ ] Verify data retention

Dependencies:
- [ ] Scan for vulnerable dependencies
- [ ] Check outdated packages
- [ ] Verify license compliance
- [ ] Test container security

Compliance:
- [ ] GDPR compliance
- [ ] PCI-DSS (if handling payments)
- [ ] HIPAA (if healthcare data)
- [ ] SOC 2 (if enterprise)
```

---

## 📊 Security Metrics

```yaml
Vulnerability Metrics:
  Critical Vulnerabilities: 0 (zero tolerance)
  High Vulnerabilities: 0 (zero tolerance)
  Medium Vulnerabilities: < 5
  Low Vulnerabilities: < 20

Time to Remediation:
  Critical: < 24 hours
  High: < 7 days
  Medium: < 30 days
  Low: < 90 days

Security Test Coverage:
  OWASP Top 10: 100%
  Authentication: 100%
  Authorization: 100%
  API Endpoints: 100%

Penetration Testing:
  Frequency: Quarterly
  Scope: Full application
  Findings: Tracked to remediation
```

---

## 🎓 Best Practices

### Do's ✅

1. **Test early and often** (shift-left security)
2. **Automate security testing** (in CI/CD)
3. **Fix vulnerabilities promptly** (track MTTR)
4. **Use defense in depth** (multiple layers)
5. **Follow least privilege** (minimal permissions)
6. **Keep dependencies updated** (regular audits)
7. **Train developers** (security awareness)
8. **Perform penetration testing** (quarterly)
9. **Monitor security events** (real-time)
10. **Have incident response plan** (be prepared)

### Don'ts ❌

1. **Don't ignore security warnings**
2. **Don't skip security testing**
3. **Don't store secrets in code**
4. **Don't trust user input**
5. **Don't use outdated crypto**
6. **Don't disable security features**
7. **Don't forget mobile security**
8. **Don't neglect API security**
9. **Don't forget third-party services**
10. **Don't assume you're secure**

---

## 🔗 Related Resources

- [Security Checklist](security-checklist.md)
- [Penetration Testing Guide](penetration-testing.md)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [NIST Security Guidelines](https://www.nist.gov/cybersecurity)

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Compliance**: OWASP Top 10 2021, CWE Top 25
