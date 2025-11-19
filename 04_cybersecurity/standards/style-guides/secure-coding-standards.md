# Secure Coding Standards

> Industry-standard secure coding practices based on OWASP, CERT, CWE Top 25, and security guidelines from Google, Microsoft, and NIST.

---

## Core Principles

### 1. Input Validation
**Never trust user input - validate everything**

```python
# ❌ BAD: No validation
def process_user_id(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection!
    return db.execute(query)

# ✅ GOOD: Parameterized queries + validation
def process_user_id(user_id):
    # Validate input
    if not isinstance(user_id, int) or user_id < 1:
        raise ValueError("Invalid user ID")

    # Use parameterized query
    query = "SELECT * FROM users WHERE id = ?"
    return db.execute(query, (user_id,))
```

**Validation Rules**:
- Whitelist over blacklist
- Validate type, length, format, range
- Reject invalid input, don't try to sanitize
- Validate on server-side (client-side is UX only)

### 2. Output Encoding
**Encode output based on context**

```javascript
// ❌ BAD: XSS vulnerability
function displayUsername(username) {
    document.getElementById('welcome').innerHTML =
        `Welcome, ${username}!`;  // XSS if username contains <script>
}

// ✅ GOOD: Proper encoding
function displayUsername(username) {
    const div = document.getElementById('welcome');
    div.textContent = `Welcome, ${username}!`;  // Auto-encoded
}

// For HTML context, use library
import DOMPurify from 'dompurify';
function displayUserBio(bio) {
    const clean = DOMPurify.sanitize(bio);
    document.getElementById('bio').innerHTML = clean;
}
```

**Encoding Contexts**:
- HTML: `&lt;`, `&gt;`, `&amp;`, `&quot;`, `&#x27;`
- JavaScript: JSON.stringify, escape special chars
- URL: encodeURIComponent
- SQL: Parameterized queries only
- Command: Avoid shell execution, use libraries

### 3. Authentication & Authorization
**Verify identity and permissions on every request**

```typescript
// ❌ BAD: Insecure direct object reference
app.get('/api/invoice/:id', (req, res) => {
    const invoice = db.getInvoice(req.params.id);
    res.json(invoice);  // Any user can access any invoice!
});

// ✅ GOOD: Authorization check
app.get('/api/invoice/:id', authenticateUser, (req, res) => {
    const invoice = db.getInvoice(req.params.id);

    // Verify ownership
    if (invoice.userId !== req.user.id && !req.user.isAdmin) {
        return res.status(403).json({ error: 'Forbidden' });
    }

    res.json(invoice);
});
```

**Authentication Best Practices**:
- Use established libraries (Passport.js, Spring Security)
- Enforce strong password requirements
- Implement MFA for sensitive operations
- Use secure session management
- Implement account lockout after failed attempts

### 4. Cryptography
**Use strong, modern cryptography correctly**

```python
# ❌ BAD: Weak/deprecated algorithms
import md5
password_hash = md5(password.encode()).hexdigest()  # MD5 is broken!

# ❌ BAD: ECB mode, predictable IV
from Crypto.Cipher import AES
cipher = AES.new(key, AES.MODE_ECB)  # ECB is insecure!

# ✅ GOOD: Modern algorithm with proper parameters
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

# ✅ GOOD: Authenticated encryption
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt_data(plaintext, key):
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # Random nonce
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ciphertext
```

**Cryptography Rules**:
- **Password hashing**: bcrypt, scrypt, Argon2 (NOT MD5, SHA1)
- **Symmetric encryption**: AES-256-GCM (authenticated encryption)
- **Asymmetric encryption**: RSA-2048+, ECDSA-256+
- **Random numbers**: Use cryptographic PRNG (crypto.randomBytes, os.urandom)
- **Key management**: Never hardcode keys, use HSM/KMS

### 5. Error Handling
**Fail securely, don't leak information**

```java
// ❌ BAD: Information leakage
try {
    authenticateUser(username, password);
} catch (Exception e) {
    return "Login failed: " + e.getMessage();
    // Reveals: "User 'admin' not found" vs "Invalid password"
}

// ✅ GOOD: Generic error message
try {
    authenticateUser(username, password);
} catch (Exception e) {
    logger.error("Login failed for user: " + username, e);  // Log details
    return "Invalid username or password";  // Generic message to user
}
```

**Error Handling Rules**:
- Generic error messages to users
- Detailed errors in secure logs (not client-side)
- Don't expose stack traces in production
- Fail closed (deny access on error)
- Set proper HTTP status codes (avoid 500 when possible)

### 6. Logging & Monitoring
**Log security events, not sensitive data**

```python
# ❌ BAD: Logging sensitive data
logger.info(f"User {username} logged in with password {password}")
logger.info(f"Credit card processed: {card_number}")

# ✅ GOOD: Log events without sensitive data
logger.info(f"Successful login: user_id={user_id}, ip={ip_address}")
logger.info(f"Payment processed: transaction_id={tx_id}, last4={card_last4}")

# Security event logging
def log_security_event(event_type, user_id, details):
    logger.warning({
        'event': event_type,
        'user_id': user_id,
        'timestamp': datetime.utcnow(),
        'ip_address': get_client_ip(),
        'user_agent': request.headers.get('User-Agent'),
        'details': details
    })

# Log security events
log_security_event('failed_login', user_id, {'attempts': 3})
log_security_event('password_change', user_id, {'forced': False})
log_security_event('permission_denied', user_id, {'resource': '/admin'})
```

**What to Log**:
- Authentication events (success/failure)
- Authorization failures
- Input validation failures
- Privilege changes
- Security configuration changes
- Data access (who accessed what)

**What NOT to Log**:
- Passwords, PINs, secrets
- Session tokens, API keys
- Credit card numbers, SSNs
- Full PII without justification

---

## Language-Specific Guidelines

### JavaScript/TypeScript

```typescript
// Use strict mode
'use strict';

// Avoid eval and similar dangerous functions
// ❌ BAD
eval(userInput);
new Function(userInput)();
setTimeout(userInput, 1000);

// ✅ GOOD: Use safe alternatives
const parsed = JSON.parse(userInput);  // If JSON expected

// Prevent prototype pollution
// ❌ BAD
function merge(target, source) {
    for (let key in source) {
        target[key] = source[key];  // Vulnerable to __proto__ pollution
    }
}

// ✅ GOOD
function merge(target, source) {
    for (let key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key) &&
            key !== '__proto__' && key !== 'constructor' && key !== 'prototype') {
            target[key] = source[key];
        }
    }
}

// Or use Object.assign / spread with care
const merged = { ...target, ...source };
```

### Python

```python
# Use secrets module for cryptographic randomness
import secrets

# ❌ BAD
import random
session_id = random.randint(1000000, 9999999)

# ✅ GOOD
session_id = secrets.token_urlsafe(32)

# Avoid pickle with untrusted data (code execution)
# ❌ BAD
import pickle
data = pickle.loads(untrusted_data)  # Can execute arbitrary code!

# ✅ GOOD
import json
data = json.loads(untrusted_data)  # Safe for data-only

# Use parameterized queries
# ❌ BAD
cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")

# ✅ GOOD
cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
```

### Java

```java
// Use PreparedStatement, never string concatenation
// ❌ BAD
String query = "SELECT * FROM users WHERE id = " + userId;
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery(query);

// ✅ GOOD
String query = "SELECT * FROM users WHERE id = ?";
PreparedStatement stmt = conn.prepareStatement(query);
stmt.setInt(1, userId);
ResultSet rs = stmt.executeQuery();

// Avoid deserialization of untrusted data
// ❌ BAD
ObjectInputStream ois = new ObjectInputStream(untrustedStream);
Object obj = ois.readObject();  // Can execute arbitrary code!

// ✅ GOOD: Use safe formats like JSON
ObjectMapper mapper = new ObjectMapper();
MyObject obj = mapper.readValue(jsonString, MyObject.class);
```

### C/C++

```c
// Avoid unsafe functions
// ❌ BAD
char buffer[100];
strcpy(buffer, userInput);  // Buffer overflow!
gets(buffer);  // Extremely dangerous!
sprintf(buffer, "%s", userInput);  // Unsafe

// ✅ GOOD
char buffer[100];
strncpy(buffer, userInput, sizeof(buffer) - 1);
buffer[sizeof(buffer) - 1] = '\0';
fgets(buffer, sizeof(buffer), stdin);
snprintf(buffer, sizeof(buffer), "%s", userInput);

// Or use modern C++ strings
std::string safeString = userInput;
```

---

## Security Checklist

### Before Committing Code

- [ ] **Input Validation**: All user input validated (type, length, format)
- [ ] **Output Encoding**: Context-appropriate encoding applied
- [ ] **SQL Injection**: Using parameterized queries only
- [ ] **XSS Prevention**: Proper encoding, CSP headers set
- [ ] **Authentication**: Using secure, tested library
- [ ] **Authorization**: Checking permissions on every request
- [ ] **Cryptography**: Using strong algorithms correctly
- [ ] **Secrets**: No hardcoded passwords, keys, or tokens
- [ ] **Error Handling**: Generic errors to users, detailed logs securely
- [ ] **Logging**: Security events logged, no sensitive data
- [ ] **Dependencies**: All dependencies scanned for vulnerabilities
- [ ] **Security Headers**: CSP, HSTS, X-Frame-Options set
- [ ] **HTTPS Only**: All communication over TLS 1.2+
- [ ] **Rate Limiting**: API endpoints protected from abuse

### Security Testing

- [ ] **SAST**: Static analysis passed (SonarQube, Semgrep)
- [ ] **Dependency Scan**: No known vulnerabilities (Snyk, Dependabot)
- [ ] **DAST**: Dynamic testing passed (OWASP ZAP)
- [ ] **Manual Review**: Security-focused code review completed
- [ ] **Penetration Test**: For critical features/endpoints

---

## Common Vulnerabilities (OWASP Top 10 2021)

### A01: Broken Access Control
- Implement authorization checks on every request
- Use indirect object references with access control
- Deny by default, explicit grant

### A02: Cryptographic Failures
- Use TLS 1.2+ for all communication
- Strong algorithms: AES-256, RSA-2048+, bcrypt/Argon2
- Secure random number generation
- Proper key management (KMS, HSM)

### A03: Injection
- Parameterized queries (SQL)
- Avoid eval, exec, shell execution
- Input validation and output encoding
- Use ORMs with care (they can still be vulnerable)

### A04: Insecure Design
- Threat modeling before implementation
- Security requirements in design phase
- Defense in depth
- Secure by default

### A05: Security Misconfiguration
- Remove default accounts
- Disable unnecessary features
- Keep software updated
- Secure cloud storage (S3 buckets, etc.)
- Error handling that doesn't leak info

### A06: Vulnerable and Outdated Components
- Automated dependency scanning
- Regular updates and patching
- Remove unused dependencies
- Monitor security advisories

### A07: Identification and Authentication Failures
- MFA for sensitive operations
- Secure session management
- Strong password requirements
- Account lockout on failed attempts
- Secure password recovery

### A08: Software and Data Integrity Failures
- Code signing
- Supply chain security
- Verify downloaded libraries
- Subresource Integrity (SRI) for CDNs
- Secure CI/CD pipelines

### A09: Security Logging and Monitoring Failures
- Log security events
- Real-time monitoring and alerting
- Centralized logging
- Log retention and protection
- Incident response plans

### A10: Server-Side Request Forgery (SSRF)
- Validate and sanitize URLs
- Whitelist allowed protocols and domains
- Network segmentation
- Disable unnecessary URL schemas

---

## Security Code Review Checklist

When reviewing code for security:

### Authentication & Authorization
- [ ] Authentication required where needed
- [ ] Authorization checks on all sensitive operations
- [ ] Session management secure (timeouts, CSRF protection)
- [ ] Password policies enforced
- [ ] MFA implemented for sensitive operations

### Input Validation
- [ ] All inputs validated (type, length, format, range)
- [ ] Whitelist validation used
- [ ] Server-side validation (not just client-side)
- [ ] Special characters handled properly

### Data Protection
- [ ] Sensitive data encrypted at rest
- [ ] TLS used for data in transit
- [ ] Secrets not hardcoded
- [ ] PII handled according to privacy requirements
- [ ] Data retention policies followed

### Error Handling
- [ ] Errors don't leak sensitive information
- [ ] Stack traces not exposed to users
- [ ] Appropriate logging of errors
- [ ] Graceful degradation

### Dependencies
- [ ] No known vulnerable dependencies
- [ ] Dependencies from trusted sources
- [ ] Dependency integrity verified (SRI, checksums)
- [ ] Minimal dependencies used

---

## References

- **OWASP Top 10**: https://owasp.org/Top10/
- **CWE Top 25**: https://cwe.mitre.org/top25/
- **CERT Secure Coding**: https://wiki.sei.cmu.edu/confluence/display/seccode
- **NIST SP 800-218**: Secure Software Development Framework
- **Google Secure Coding**: Internal security guidelines
- **Microsoft SDL**: Security Development Lifecycle

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Compliance**: OWASP ASVS v4.0, CWE Top 25, NIST SSDF
