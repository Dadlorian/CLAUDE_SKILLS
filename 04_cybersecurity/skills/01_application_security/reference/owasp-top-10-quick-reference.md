# OWASP Top 10 2021 - Quick Reference

## A01:2021 – Broken Access Control

**Risk**: Users can access unauthorized functionality or data

**Common Issues**:
- Missing authorization checks
- Insecure direct object references (IDOR)
- Elevation of privilege

**Prevention**:
```python
# ✅ Check authorization on every request
@app.route('/api/documents/<doc_id>')
@login_required
def get_document(doc_id):
    doc = Document.query.get_or_404(doc_id)

    # Verify ownership
    if doc.owner_id != current_user.id and not current_user.is_admin:
        abort(403)

    return jsonify(doc.to_dict())
```

---

## A02:2021 – Cryptographic Failures

**Risk**: Sensitive data exposure due to weak or missing encryption

**Common Issues**:
- Transmitting data in cleartext
- Weak cryptographic algorithms (MD5, SHA1)
- Hardcoded secrets

**Prevention**:
```python
# ✅ Use strong encryption
from cryptography.fernet import Fernet
import bcrypt

# Password hashing
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

# Data encryption
key = Fernet.generate_key()
cipher = Fernet(key)
encrypted = cipher.encrypt(data.encode())
```

---

## A03:2021 – Injection

**Risk**: Untrusted data sent to interpreter as command or query

**Common Issues**:
- SQL injection
- NoSQL injection
- OS command injection
- LDAP injection

**Prevention**:
```javascript
// ✅ Use parameterized queries
const query = 'SELECT * FROM users WHERE email = ?';
db.query(query, [email], (err, results) => {
    // Safe from SQL injection
});

// ❌ Never do this
const badQuery = `SELECT * FROM users WHERE email = '${email}'`;  // VULNERABLE!
```

---

## A04:2021 – Insecure Design

**Risk**: Missing or ineffective security controls in design

**Prevention**:
- Threat modeling (STRIDE, PASTA)
- Security requirements
- Secure design patterns
- Defense in depth

---

## A05:2021 – Security Misconfiguration

**Risk**: Insecure default configurations, incomplete setups

**Common Issues**:
- Default accounts enabled
- Unnecessary features enabled
- Detailed error messages
- Missing security headers

**Prevention**:
```javascript
// ✅ Security headers
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            scriptSrc: ["'self'"],
        },
    },
    hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
    }
}));
```

---

## A06:2021 – Vulnerable and Outdated Components

**Risk**: Using components with known vulnerabilities

**Prevention**:
```bash
# Regularly scan dependencies
npm audit
snyk test
dependabot

# Update regularly
npm update
npm audit fix
```

---

## A07:2021 – Identification and Authentication Failures

**Risk**: Weak authentication, session management

**Common Issues**:
- Weak passwords allowed
- No MFA
- Session fixation
- Credential stuffing

**Prevention**:
```python
# ✅ Strong password policy + MFA
from password_strength import PasswordPolicy

policy = PasswordPolicy.from_names(
    length=12,
    uppercase=1,
    numbers=1,
    special=1
)

# Require MFA for sensitive operations
if sensitive_operation and not user.mfa_verified:
    return {"error": "MFA required"}
```

---

## A08:2021 – Software and Data Integrity Failures

**Risk**: Code/infrastructure without integrity verification

**Prevention**:
- Code signing
- Subresource Integrity (SRI)
- Verify dependencies
- Secure CI/CD pipeline

```html
<!-- ✅ Subresource Integrity -->
<script
    src="https://cdn.example.com/library.js"
    integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/ux..."
    crossorigin="anonymous">
</script>
```

---

## A09:2021 – Security Logging and Monitoring Failures

**Risk**: Insufficient logging, no monitoring

**What to Log**:
- Authentication events (success/failure)
- Authorization failures
- Input validation failures
- Security exceptions

**Prevention**:
```python
# ✅ Comprehensive security logging
import logging

# Log security events
logger.warning("Failed login attempt", extra={
    'user_id': user_id,
    'ip_address': request.remote_addr,
    'user_agent': request.user_agent.string,
    'timestamp': datetime.utcnow()
})

# Alert on suspicious patterns
if failed_login_count(user_id) > 5:
    send_security_alert("Multiple failed login attempts")
```

---

## A10:2021 – Server-Side Request Forgery (SSRF)

**Risk**: Application fetches remote resource without validating URL

**Prevention**:
```python
# ✅ Validate and whitelist URLs
from urllib.parse import urlparse

ALLOWED_DOMAINS = ['api.example.com', 'cdn.example.com']

def fetch_url(url):
    parsed = urlparse(url)

    # Check protocol
    if parsed.scheme not in ['https']:
        raise ValueError("Only HTTPS allowed")

    # Check domain whitelist
    if parsed.netloc not in ALLOWED_DOMAINS:
        raise ValueError("Domain not allowed")

    # Prevent internal network access
    if is_private_ip(parsed.hostname):
        raise ValueError("Private IPs not allowed")

    return requests.get(url, timeout=5)
```

---

## Testing Checklist

- [ ] Input validation on all user inputs
- [ ] Parameterized queries (no string concatenation)
- [ ] Output encoding for display
- [ ] Authorization checks on all endpoints
- [ ] Secure session management
- [ ] Strong cryptography (TLS 1.2+, AES-256, bcrypt)
- [ ] Security headers (CSP, HSTS, etc.)
- [ ] No secrets in code
- [ ] Dependencies scanned for vulnerabilities
- [ ] Comprehensive logging
- [ ] Rate limiting on APIs
- [ ] MFA for sensitive operations

---

**Reference**: https://owasp.org/Top10/
**Version**: OWASP Top 10 2021
