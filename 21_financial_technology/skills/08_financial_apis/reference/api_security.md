# API Security for Financial Systems

## Core Security Principles

### Defense in Depth
Multiple security layers:
1. Network security (TLS, mTLS)
2. Authentication (OAuth, certificates)
3. Authorization (scopes, permissions)
4. Input validation (data type, range, format)
5. Output encoding (prevent injection)
6. Monitoring and logging

### Principle of Least Privilege
Users/applications only access what they need:
```
├─ User: Can read own accounts (no write)
├─ Admin: Can manage users (no account data)
├─ App: Can access authorized accounts only
└─ Service: Can access its own resources only
```

## Transport Security

### TLS Requirements
```python
import ssl
import requests

# Enforce TLS 1.2+
context = ssl.create_default_context()
context.minimum_version = ssl.TLSVersion.TLSv1_2
context.maximum_version = ssl.TLSVersion.TLSv1_3

# Strong cipher suites only
context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')

# Certificate verification
response = requests.get(
    'https://api.example.com/accounts',
    verify=True,  # Verify server certificate
    cert=('client.pem', 'key.pem')  # mTLS client certificate
)
```

### Certificate Pinning
```python
import requests
from requests.adapters import HTTPAdapter
import ssl

class PinnedHTTPSAdapter(HTTPAdapter):
    """HTTPS adapter with certificate pinning"""

    def __init__(self, pinned_cert_hash, **kwargs):
        self.pinned_cert_hash = pinned_cert_hash
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        # Implement certificate pinning
        super().init_poolmanager(*args, **kwargs)

# Usage
session = requests.Session()
adapter = PinnedHTTPSAdapter(
    pinned_cert_hash="sha256/X3pGTSOuJeED5d+d..."
)
session.mount('https://', adapter)

response = session.get('https://api.example.com/accounts')
```

## Authentication

### OAuth 2.0 Implementation
```python
from authlib.integrations.requests_client import OAuth2Session

class OAuthClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = "https://auth.example.com"

    def get_access_token(self, auth_code):
        """Exchange authorization code for token"""
        client = OAuth2Session(
            self.client_id,
            redirect_uri="https://app.example.com/callback"
        )

        token = client.fetch_token(
            f"{self.auth_url}/token",
            code=auth_code,
            client_secret=self.client_secret,
            verify=True
        )

        return token

    def refresh_token(self, refresh_token):
        """Get new access token"""
        client = OAuth2Session(self.client_id)

        token = client.refresh_token(
            f"{self.auth_url}/token",
            refresh_token=refresh_token,
            client_secret=self.client_secret
        )

        return token
```

### mTLS Implementation
```python
import requests
from certifi import where

class mTLSClient:
    def __init__(self, client_cert, client_key, ca_cert):
        self.client_cert = (client_cert, client_key)
        self.ca_cert = ca_cert

    def make_request(self, method, url, **kwargs):
        """Make mTLS request"""
        response = requests.request(
            method,
            url,
            cert=self.client_cert,
            verify=self.ca_cert,
            **kwargs
        )

        return response

# Usage
client = mTLSClient(
    client_cert="client-cert.pem",
    client_key="client-key.pem",
    ca_cert="ca-cert.pem"
)

response = client.make_request(
    "GET",
    "https://api.example.com/accounts"
)
```

## Authorization

### Scope-Based Access Control
```python
SCOPE_PERMISSIONS = {
    "accounts:read": ["GET /accounts"],
    "accounts:write": ["GET /accounts", "PUT /accounts/*"],
    "transactions:read": ["GET /accounts/*/transactions"],
    "payments:write": ["POST /payments"],
    "payments:read": ["GET /payments/*"]
}

def check_scopes(required_scopes, token_scopes):
    """Check if token has required scopes"""
    user_scopes = set(token_scopes.split(" "))
    required = set(required_scopes)

    return required.issubset(user_scopes)

@app.route('/accounts', methods=['GET'])
def get_accounts():
    """Check scopes before accessing accounts"""
    token = get_token_from_request(request)

    if not check_scopes(["accounts:read"], token["scope"]):
        return jsonify({"error": "Insufficient scopes"}), 403

    # Return accounts
    return jsonify({"accounts": [...]})
```

## Input Validation

### Parameter Validation
```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class PaymentRequest(BaseModel):
    """Validated payment request"""

    amount: float = Field(..., gt=0, le=1000000)  # Positive, max 1M
    currency: str = Field(..., regex=r"^[A-Z]{3}$")  # 3-letter code
    creditor_iban: str = Field(..., regex=r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$")
    debtor_iban: str = Field(..., regex=r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$")
    reference: Optional[str] = Field(None, max_length=140)

    @validator('amount')
    def amount_not_zero(cls, v):
        if v == 0:
            raise ValueError("Amount must be non-zero")
        return v

    @validator('creditor_iban')
    def validate_creditor_iban(cls, v):
        if v == cls.debtor_iban:
            raise ValueError("Creditor and debtor must be different")
        return v

@app.route('/payments', methods=['POST'])
def create_payment():
    """Create payment with validation"""
    try:
        payment = PaymentRequest(**request.json)
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400

    # Process validated payment
    return process_payment(payment)
```

### SQL Injection Prevention
```python
import pymysql
from pymysql.converters import escape_string

class DatabaseClient:
    def __init__(self, connection):
        self.conn = connection

    def get_account(self, account_id):
        """
        Use parameterized queries (not string formatting!)
        """
        cursor = self.conn.cursor()

        # ✓ GOOD: Parameterized query
        query = "SELECT * FROM accounts WHERE id = %s"
        cursor.execute(query, (account_id,))

        # ✗ BAD: String formatting (vulnerable to SQL injection)
        # query = f"SELECT * FROM accounts WHERE id = '{account_id}'"
        # cursor.execute(query)

        return cursor.fetchone()
```

## Output Encoding

### JSON Encoding
```python
import json

def safe_json_response(data):
    """
    Safely encode response as JSON
    Prevents XSS via JSON injection
    """
    # Ensure all strings are properly escaped
    response = json.dumps(data, ensure_ascii=True)

    return response
```

## Sensitive Data Protection

### Field-Level Encryption
```python
from cryptography.fernet import Fernet

class EncryptedField:
    """Encrypt sensitive fields in database"""

    def __init__(self, encryption_key):
        self.cipher = Fernet(encryption_key)

    def encrypt(self, value):
        """Encrypt field"""
        if value is None:
            return None

        return self.cipher.encrypt(value.encode()).decode()

    def decrypt(self, encrypted_value):
        """Decrypt field"""
        if encrypted_value is None:
            return None

        return self.cipher.decrypt(encrypted_value.encode()).decode()

# Usage
class Account(Base):
    __tablename__ = 'accounts'

    id = Column(String)
    iban = Column(String)  # Encrypted
    balance = Column(Float)

    def __init__(self, iban):
        encryptor = EncryptedField(ENCRYPTION_KEY)
        self.iban = encryptor.encrypt(iban)
```

### Password Security
```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

hasher = PasswordHasher()

def hash_password(password):
    """Hash password using Argon2"""
    return hasher.hash(password)

def verify_password(password, hash):
    """Verify password"""
    try:
        hasher.verify(hash, password)
        return True
    except VerifyMismatchError:
        return False
```

## CSRF Prevention

### CSRF Token Implementation
```python
import secrets
from flask import session, request

def generate_csrf_token():
    """Generate CSRF token"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)

    return session['csrf_token']

@app.before_request
def verify_csrf_token():
    """Verify CSRF token on POST requests"""
    if request.method == 'POST':
        token = request.form.get('_csrf_token')

        if not token or token != session.get('csrf_token'):
            return jsonify({"error": "CSRF validation failed"}), 403

# In template
def render_payment_form():
    csrf_token = generate_csrf_token()
    return f"""
    <form method="post" action="/payments">
        <input type="hidden" name="_csrf_token" value="{csrf_token}">
        ...
    </form>
    """
```

## Security Headers

### HTTP Security Headers
```python
from flask import Flask

app = Flask(__name__)

@app.after_request
def set_security_headers(response):
    """Set security headers"""

    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'

    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # Strict Transport Security
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    # Content Security Policy
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'"

    # Prevent referrer leakage
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    return response
```

## Logging and Monitoring

### Security Logging
```python
import logging
import json

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger('security')

    def log_authentication(self, user_id, success, reason=None):
        """Log authentication attempts"""
        self.logger.info(json.dumps({
            "event": "authentication",
            "user_id": user_id,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason
        }))

    def log_authorization_failure(self, user_id, resource, reason):
        """Log authorization failures"""
        self.logger.warning(json.dumps({
            "event": "authorization_failure",
            "user_id": user_id,
            "resource": resource,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }))

    def log_data_access(self, user_id, data_type, account_id):
        """Log data access for audit"""
        self.logger.info(json.dumps({
            "event": "data_access",
            "user_id": user_id,
            "data_type": data_type,
            "account_id": account_id,
            "timestamp": datetime.utcnow().isoformat()
        }))
```

## Vulnerability Scanning

### Common Vulnerabilities
```
OWASP Top 10 for APIs:
1. Broken authentication
2. Broken authorization
3. Excessive data exposure
4. Lack of resource & rate limiting
5. Broken function level authorization
6. Mass assignment
7. Security misconfiguration
8. Injection
9. Improper assets management
10. Insufficient logging & monitoring
```

## Security Checklist

- [ ] TLS 1.2+ for all communications
- [ ] mTLS for sensitive endpoints
- [ ] OAuth 2.0 or equivalent authentication
- [ ] Scope-based authorization
- [ ] Input validation on all parameters
- [ ] SQL injection prevention
- [ ] CSRF protection
- [ ] Security headers set
- [ ] HTTPS redirect
- [ ] Rate limiting enabled
- [ ] Comprehensive logging
- [ ] Error handling (no sensitive data)
- [ ] Regular security updates
- [ ] Penetration testing
- [ ] Certificate management

## References

- OWASP API Security: https://owasp.org/www-project-api-security/
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Secure Coding: https://cheatsheetseries.owasp.org/
