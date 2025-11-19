# API Authentication Patterns

## Table of Contents

1. [Overview](#overview)
2. [OAuth 2.0](#oauth-20)
3. [JWT (JSON Web Tokens)](#jwt-json-web-tokens)
4. [API Keys](#api-keys)
5. [Webhook Security](#webhook-security)
6. [Comparison Matrix](#comparison-matrix)
7. [Implementation Best Practices](#implementation-best-practices)
8. [Industry Examples](#industry-examples)

---

## Overview

API authentication is the foundation of secure API design. This guide covers the most prevalent authentication patterns used by leading API providers like Stripe, Twilio, and others. Each pattern serves different use cases and security requirements.

### Authentication vs Authorization

- **Authentication**: Verifies WHO the user is (identity verification)
- **Authorization**: Determines WHAT the user can do (permissions)

### Security Principles

1. **Never store credentials in code**
2. **Always use HTTPS/TLS**
3. **Implement token expiration**
4. **Use strong secret generation**
5. **Rotate secrets regularly**
6. **Monitor for suspicious activity**

---

## OAuth 2.0

OAuth 2.0 is an industry-standard protocol for authorization, not authentication. It allows users to grant access to their resources without sharing passwords.

### OAuth 2.0 Grant Types

#### 1. Authorization Code Grant (Most Common)

Best for: Server-side web applications

```
+--------+                                   +---------------+
|        |--(A)- Authorization Request ----->|   Resource    |
|        |                                   |     Owner     |
|  User  |<-(B)-- Authorization Grant -------|               |
|        |                                   +---------------+
+--------+
    |
    |
    v
+---------+                                  +---------------+
|         |--(C)- Authorization Grant ------>|               |
| Browser |                                  |   OAuth       |
|         |<-(D)-- Access Token (Backend) ---|   Server      |
+---------+                                  |               |
    ^                                        +---------------+
    |
    |
    v
+---------+
|  Web    |
|  Server |
+---------+
```

**Flow Steps:**

1. User clicks "Login with Google/GitHub"
2. Browser redirected to OAuth provider
3. User authorizes and grants permission
4. Provider redirects back with authorization code
5. Backend exchanges code for access token
6. Backend uses access token to access resources

**Implementation Example:**

```javascript
// 1. Redirect user to OAuth provider
const authorizationUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
authorizationUrl.searchParams.append('client_id', GOOGLE_CLIENT_ID);
authorizationUrl.searchParams.append('redirect_uri', CALLBACK_URL);
authorizationUrl.searchParams.append('response_type', 'code');
authorizationUrl.searchParams.append('scope', 'openid email profile');
authorizationUrl.searchParams.append('state', generateRandomState());

// 2. Handle callback
app.get('/callback', async (req, res) => {
  const { code, state } = req.query;

  // Verify state parameter
  if (state !== req.session.state) {
    return res.status(400).send('Invalid state parameter');
  }

  // Exchange code for token
  const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      client_id: GOOGLE_CLIENT_ID,
      client_secret: GOOGLE_CLIENT_SECRET,
      code,
      redirect_uri: CALLBACK_URL,
      grant_type: 'authorization_code'
    })
  });

  const { access_token, refresh_token, expires_in } = await tokenResponse.json();

  // Store tokens securely
  req.session.accessToken = access_token;
  req.session.refreshToken = refresh_token;
  req.session.expiresAt = Date.now() + expires_in * 1000;

  res.redirect('/dashboard');
});

// 3. Refresh token when expired
async function getValidToken(session) {
  if (session.expiresAt > Date.now()) {
    return session.accessToken;
  }

  const refreshResponse = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      client_id: GOOGLE_CLIENT_ID,
      client_secret: GOOGLE_CLIENT_SECRET,
      refresh_token: session.refreshToken,
      grant_type: 'refresh_token'
    })
  });

  const { access_token, expires_in } = await refreshResponse.json();
  session.accessToken = access_token;
  session.expiresAt = Date.now() + expires_in * 1000;

  return access_token;
}
```

#### 2. Implicit Grant (Deprecated for Security Reasons)

**Status**: ⚠️ Deprecated for SPAs - use Authorization Code with PKCE instead

```
+--------+                                   +---------------+
|        |--(A)- Authorization Request ----->|   Resource    |
|        |     (with response_type=token)   |     Owner     |
|  User  |                                   |               |
|        |<-(B)-- Access Token in URL Fragment --|               |
+--------+                                   +---------------+
```

#### 3. Client Credentials Grant

Best for: Service-to-service authentication

```
+--------+                                   +---------------+
|        |--(A)- Client Credentials ------->|               |
| Service|     (client_id, client_secret)   |               |
|        |                                   |  OAuth        |
|        |<-(B)-- Access Token --------------|  Server       |
|        |                                   |               |
+--------+                                   +---------------+
```

**Example:**

```python
# Python implementation
import requests

def get_service_token():
    token_url = 'https://oauth.example.com/token'

    response = requests.post(
        token_url,
        data={
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'scope': 'api:read api:write'
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    if response.status_code == 200:
        token_data = response.json()
        return token_data['access_token']
    else:
        raise Exception(f"Failed to get token: {response.text}")

# Use token in API requests
token = get_service_token()
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('https://api.example.com/data', headers=headers)
```

#### 4. Resource Owner Password Credentials (Legacy)

**Status**: ⚠️ Not recommended for new implementations

Only use when implicit trust exists between user and application.

```
+--------+                                   +---------------+
|        |--(A)- Username & Password ------>|               |
| User   |                                   |  OAuth        |
|        |<-(B)-- Access Token --------------|  Server       |
|        |                                   |               |
+--------+                                   +---------------+
```

### OAuth 2.0 with PKCE (Proof Key for Code Exchange)

**Essential for mobile apps and SPAs**

```
+--------+                                   +---------------+
|        |--(A)- Authorization Request ----->|               |
|        |     (code_challenge)              |  Resource     |
| Client |                                   |  Owner        |
|        |<-(B)-- Authorization Code --------|               |
|        |                                   +---------------+
+--------+
    |
    |
    v
+---------+                                  +---------------+
| Mobile  |--(C)- Authorization Code ------>|               |
| App /   |     (code_verifier)              | OAuth         |
| SPA     |                                  | Server        |
|         |<-(D)-- Access Token --------------|               |
|         |                                  +---------------+
+---------+
```

**Implementation:**

```javascript
// 1. Generate code verifier and challenge
function generateCodeVerifier() {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return btoa(String.fromCharCode.apply(null, array))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

async function generateCodeChallenge(verifier) {
  const encoder = new TextEncoder();
  const data = encoder.encode(verifier);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);

  return btoa(String.fromCharCode(...new Uint8Array(hashBuffer)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

// 2. Redirect with PKCE parameters
const codeVerifier = generateCodeVerifier();
const codeChallenge = await generateCodeChallenge(codeVerifier);

sessionStorage.setItem('code_verifier', codeVerifier);

const authUrl = new URL('https://oauth.example.com/authorize');
authUrl.searchParams.append('client_id', CLIENT_ID);
authUrl.searchParams.append('redirect_uri', REDIRECT_URI);
authUrl.searchParams.append('response_type', 'code');
authUrl.searchParams.append('code_challenge', codeChallenge);
authUrl.searchParams.append('code_challenge_method', 'S256');
authUrl.searchParams.append('scope', 'openid profile email');

window.location.href = authUrl.toString();

// 3. Exchange code for token (using stored verifier)
const codeVerifier = sessionStorage.getItem('code_verifier');

const tokenResponse = await fetch('https://oauth.example.com/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    grant_type: 'authorization_code',
    client_id: CLIENT_ID,
    code: authCode,
    redirect_uri: REDIRECT_URI,
    code_verifier: codeVerifier
  })
});
```

---

## JWT (JSON Web Tokens)

JWT is a compact, self-contained way to represent claims between two parties.

### JWT Structure

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Three parts separated by dots:

1. **Header**: Algorithm and token type
2. **Payload**: Claims (data)
3. **Signature**: Verification

### Header

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload (Claims)

**Registered Claims (standard):**
- `iss`: Issuer
- `sub`: Subject (user ID)
- `aud`: Audience
- `exp`: Expiration time
- `nbf`: Not before
- `iat`: Issued at
- `jti`: JWT ID

**Custom Claims:**

```json
{
  "sub": "user_123",
  "name": "Jane Doe",
  "email": "jane@example.com",
  "role": "admin",
  "permissions": ["read", "write", "delete"],
  "iat": 1516239022,
  "exp": 1516242622,
  "iss": "https://auth.example.com",
  "aud": "https://api.example.com"
}
```

### JWT Implementation

**Signing and Verification (Node.js):**

```javascript
const jwt = require('jsonwebtoken');

// Secret should be stored in environment variable
const SECRET = process.env.JWT_SECRET;

// 1. Create JWT
function createToken(payload, expiresIn = '1h') {
  return jwt.sign(payload, SECRET, {
    expiresIn,
    issuer: 'https://auth.example.com',
    audience: 'https://api.example.com',
    algorithm: 'HS256'
  });
}

// Example
const token = createToken({
  sub: 'user_123',
  name: 'Jane Doe',
  email: 'jane@example.com',
  role: 'admin'
});

// 2. Verify JWT
function verifyToken(token) {
  try {
    return jwt.verify(token, SECRET, {
      issuer: 'https://auth.example.com',
      audience: 'https://api.example.com',
      algorithms: ['HS256']
    });
  } catch (error) {
    if (error instanceof jwt.TokenExpiredError) {
      throw new Error('Token expired');
    } else if (error instanceof jwt.JsonWebTokenError) {
      throw new Error('Invalid token');
    }
    throw error;
  }
}

// 3. Middleware for Express
function authMiddleware(req, res, next) {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or invalid authorization header' });
  }

  const token = authHeader.substring(7);

  try {
    const decoded = verifyToken(token);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: error.message });
  }
}

app.get('/protected', authMiddleware, (req, res) => {
  res.json({ message: `Hello ${req.user.name}!` });
});
```

### Refresh Token Pattern

JWTs should have short expiration times. Use refresh tokens for long-lived sessions:

```javascript
// Store refresh tokens in database
const refreshTokens = new Map();

function createTokenPair(userId) {
  const accessToken = jwt.sign(
    { sub: userId },
    SECRET,
    { expiresIn: '15m', algorithm: 'HS256' }
  );

  const refreshToken = jwt.sign(
    { sub: userId, type: 'refresh' },
    REFRESH_SECRET,
    { expiresIn: '7d', algorithm: 'HS256' }
  );

  // Store refresh token with expiration
  const jti = crypto.randomUUID();
  refreshTokens.set(jti, {
    userId,
    token: refreshToken,
    expiresAt: Date.now() + 7 * 24 * 60 * 60 * 1000
  });

  return { accessToken, refreshToken, jti };
}

// Refresh endpoint
app.post('/refresh', (req, res) => {
  const { refreshToken } = req.body;

  try {
    const decoded = jwt.verify(refreshToken, REFRESH_SECRET);

    if (decoded.type !== 'refresh') {
      return res.status(401).json({ error: 'Invalid token type' });
    }

    const { accessToken, refreshToken: newRefreshToken } = createTokenPair(decoded.sub);

    res.json({
      accessToken,
      refreshToken: newRefreshToken,
      expiresIn: 900 // 15 minutes
    });
  } catch (error) {
    res.status(401).json({ error: 'Invalid refresh token' });
  }
});
```

### Asymmetric Signing (RS256)

For distributed systems, use public/private key signing:

```javascript
const fs = require('fs');

const privateKey = fs.readFileSync('/path/to/private.key', 'utf8');
const publicKey = fs.readFileSync('/path/to/public.key', 'utf8');

// Sign with private key
const token = jwt.sign(
  { sub: 'user_123', name: 'Jane' },
  privateKey,
  { algorithm: 'RS256' }
);

// Verify with public key
const decoded = jwt.verify(token, publicKey, { algorithms: ['RS256'] });
```

---

## API Keys

Simple but effective for server-to-server communication or specific use cases.

### API Key Formats

**Prefixed Format (Production Services):**
```
prod_1234567890abcdef1234567890abcdef  # Production environment key
test_1234567890abcdef1234567890abcdef  # Testing environment key
```

**Opaque Token Format:**
```
auth_1234567890abcdefghijklmnopqrstu  # Authentication token
```

### Implementation

```python
import secrets
import hashlib
from datetime import datetime, timedelta

class APIKeyManager:
    def __init__(self, db):
        self.db = db

    def generate_key_pair(self, organization_id, name, permissions=None):
        """Generate API key pair"""
        # Generate 32-byte random key
        raw_key = secrets.token_bytes(32)
        api_key = f"sk_live_{secrets.token_urlsafe(24)}"

        # Store hashed version in database
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        key_record = {
            'id': secrets.token_hex(12),
            'organization_id': organization_id,
            'name': name,
            'key_hash': key_hash,
            'permissions': permissions or ['read', 'write'],
            'created_at': datetime.utcnow(),
            'last_used': None,
            'revoked': False,
            'expires_at': datetime.utcnow() + timedelta(days=365)
        }

        self.db.save_api_key(key_record)
        return api_key, key_record['id']

    def validate_key(self, api_key, required_permissions=None):
        """Validate API key and check permissions"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        key_record = self.db.get_key_by_hash(key_hash)

        if not key_record:
            return None, "Invalid API key"

        if key_record['revoked']:
            return None, "API key has been revoked"

        if key_record['expires_at'] < datetime.utcnow():
            return None, "API key has expired"

        if required_permissions:
            has_perms = all(
                perm in key_record['permissions']
                for perm in required_permissions
            )
            if not has_perms:
                return None, "Insufficient permissions"

        # Update last_used timestamp
        self.db.update_key_last_used(key_record['id'])

        return key_record, None

# Flask integration
from flask import request, jsonify

@app.before_request
def validate_api_key():
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing authorization header'}), 401

    api_key = auth_header[7:]

    key_record, error = api_key_manager.validate_key(api_key)

    if error:
        return jsonify({'error': error}), 401

    g.api_key = key_record
```

### API Key Best Practices

1. **Prefix keys** - Makes it clear where keys should be used
2. **Hash before storage** - Never store plaintext keys
3. **Set expiration** - Force rotation
4. **Log access** - Track key usage
5. **Rate limit** - Apply per-key rate limits
6. **Scope permissions** - Use least privilege principle

---

## Webhook Security

Webhooks require special security considerations since they involve outbound requests.

### Webhook Authentication Flow

```
+----------+                                 +-----------+
| API      |                                 | Customer  |
| Provider |                                 | Server    |
|          |                                 |           |
|          |--(1) Event occurs            ---|           |
|          |                                 |           |
|          |--(2) POST webhook payload ------->           |
|          |     with signature header       |           |
|          |                                 |           |
|          |     <-(3) Verify signature  ----|           |
|          |                                 |           |
|          |     <-(4) Process event    ----|           |
|          |                                 |           |
|          |     <-(5) Return 2xx status ----|           |
|          |<----(6) Acknowledge receipt -----           |
|          |                                 |           |
+----------+                                 +-----------+
```

### Signature Verification (HMAC-SHA256)

**Provider (Stripe/Twilio style):**

```python
from flask import request
import hmac
import hashlib
import json

WEBHOOK_SECRET = os.environ['WEBHOOK_SECRET']

def verify_webhook_signature(payload, signature, timestamp):
    """Verify webhook signature using HMAC-SHA256"""

    # Prevent replay attacks
    current_time = time.time()
    if abs(current_time - int(timestamp)) > 300:  # 5 minute window
        raise ValueError("Timestamp too old")

    # Create signed content (timestamp.payload)
    signed_content = f"{timestamp}.{payload}"

    # Compute HMAC
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        signed_content.encode(),
        hashlib.sha256
    ).hexdigest()

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_signature, signature)

@app.post('/webhook/events')
def handle_webhook():
    payload = request.get_data(as_text=True)
    signature = request.headers.get('x-webhook-signature')
    timestamp = request.headers.get('x-webhook-timestamp')

    if not signature or not timestamp:
        return jsonify({'error': 'Missing signature or timestamp'}), 400

    try:
        if not verify_webhook_signature(payload, signature, timestamp):
            return jsonify({'error': 'Invalid signature'}), 401
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    event_data = json.loads(payload)
    process_event(event_data)

    return jsonify({'status': 'success'}), 200
```

**Client (Your server):**

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature) {
  const secret = process.env.WEBHOOK_SECRET;

  // Payload should be raw request body (string)
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  // Constant-time comparison
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

app.post('/webhook', express.raw({ type: 'application/json' }), (req, res) => {
  const signature = req.headers['x-signature'];
  const rawBody = req.body; // Raw buffer

  try {
    if (!verifyWebhookSignature(rawBody.toString(), signature)) {
      return res.status(401).json({ error: 'Invalid signature' });
    }

    const event = JSON.parse(rawBody);
    handleEvent(event);

    res.json({ received: true });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});
```

### Webhook Retry Strategy

```python
from celery import shared_task
from datetime import datetime, timedelta
import requests

class WebhookEvent:
    def __init__(self, db):
        self.db = db

    def queue_webhook(self, organization_id, event_type, payload):
        """Queue webhook for delivery"""

        webhook_config = self.db.get_webhook_config(organization_id)
        if not webhook_config or not webhook_config['enabled']:
            return

        event = {
            'id': secrets.token_hex(16),
            'organization_id': organization_id,
            'event_type': event_type,
            'payload': payload,
            'url': webhook_config['url'],
            'secret': webhook_config['secret'],
            'status': 'pending',
            'attempts': 0,
            'max_attempts': 5,
            'created_at': datetime.utcnow(),
            'next_retry': datetime.utcnow()
        }

        self.db.save_webhook_event(event)
        self.deliver_webhook.delay(event['id'])

    @shared_task(bind=True)
    def deliver_webhook(self, event_id):
        """Deliver webhook with exponential backoff"""

        event = self.db.get_webhook_event(event_id)

        if event['status'] in ['delivered', 'failed']:
            return

        if event['attempts'] >= event['max_attempts']:
            self.db.update_webhook_status(event_id, 'failed')
            self.notify_failed_webhook(event)
            return

        # Create signature
        timestamp = int(time.time())
        signed_content = f"{timestamp}.{json.dumps(event['payload'])}"
        signature = hmac.new(
            event['secret'].encode(),
            signed_content.encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            'x-webhook-signature': signature,
            'x-webhook-timestamp': str(timestamp),
            'x-webhook-id': event['id'],
            'content-type': 'application/json'
        }

        try:
            response = requests.post(
                event['url'],
                json=event['payload'],
                headers=headers,
                timeout=10
            )

            if response.status_code >= 200 and response.status_code < 300:
                self.db.update_webhook_status(event_id, 'delivered')
                return

            # Retry on server errors
            if response.status_code >= 500:
                self.schedule_retry(event_id)
            else:
                # Don't retry on client errors
                self.db.update_webhook_status(event_id, 'failed')

        except requests.RequestException:
            self.schedule_retry(event_id)

    def schedule_retry(self, event_id):
        """Schedule retry with exponential backoff"""

        event = self.db.get_webhook_event(event_id)

        # Exponential backoff: 2^attempt minutes
        backoff_minutes = 2 ** event['attempts']
        max_backoff_hours = 24
        backoff_minutes = min(backoff_minutes, max_backoff_hours * 60)

        next_retry = datetime.utcnow() + timedelta(minutes=backoff_minutes)

        self.db.update_webhook_event(event_id, {
            'attempts': event['attempts'] + 1,
            'status': 'pending',
            'next_retry': next_retry
        })

        # Schedule task
        self.deliver_webhook.apply_async(
            args=[event_id],
            eta=next_retry
        )
```

---

## Comparison Matrix

| Feature | OAuth 2.0 | JWT | API Keys | Webhooks |
|---------|-----------|-----|----------|----------|
| **Use Case** | Delegated access | Stateless auth | Server-to-server | Event notifications |
| **User Interaction** | Required (grant) | No | No | No (one-way) |
| **Token Storage** | Secure | Memory/localStorage | Secure vault | N/A |
| **Expiration** | Configurable | Usually short-lived | Optional | N/A |
| **Scalability** | Good (OAuth server) | Excellent | Good | Good |
| **Complexity** | High | Medium | Low | Medium |
| **Standard** | Yes (RFC 6749) | Yes (RFC 7519) | Ad-hoc | No standard |
| **Refresh Support** | Yes | Yes (via refresh token) | Limited | N/A |
| **Revocation** | Supported | Complex | Easy | N/A |
| **Best For** | Third-party integrations | Internal APIs | Programmatic access | Event distribution |

---

## Implementation Best Practices

### 1. Secure Storage

```python
# Bad: Hardcoded secrets
API_KEY = "sk_live_abcd1234..."
SECRET = "my-secret-key"

# Good: Environment variables
import os
API_KEY = os.environ.get('API_KEY')
SECRET = os.environ.get('SECRET_KEY')

# Better: Secrets management service
from google.cloud import secretmanager

def get_secret(secret_id, version_id='latest'):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/my-project/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')

api_key = get_secret('api-key')
```

### 2. Key Rotation

```python
class KeyRotationManager:
    def __init__(self, db):
        self.db = db

    def schedule_key_rotation(self, key_id, rotation_days=90):
        """Schedule automatic key rotation"""

        key = self.db.get_key(key_id)

        rotation_date = datetime.utcnow() + timedelta(days=rotation_days)

        self.db.update_key(key_id, {
            'rotation_date': rotation_date,
            'rotation_status': 'scheduled'
        })

        # Send notification to user
        self.send_rotation_notification(key['owner_email'], key_id, rotation_date)

    def rotate_key(self, key_id):
        """Perform key rotation"""

        old_key = self.db.get_key(key_id)

        # Generate new key
        new_key_value, new_key_id = self.generate_new_key(old_key['organization_id'])

        # Grace period: keep old key valid for 30 days
        grace_period = datetime.utcnow() + timedelta(days=30)

        self.db.update_key(key_id, {
            'status': 'rotated',
            'rotated_at': datetime.utcnow(),
            'grace_period_until': grace_period
        })

        return new_key_value
```

### 3. Audit Logging

```python
def log_authentication_event(user_id, auth_method, status, ip_address, user_agent):
    """Log all authentication events for security auditing"""

    audit_log = {
        'timestamp': datetime.utcnow(),
        'user_id': user_id,
        'auth_method': auth_method,  # oauth, jwt, api_key, webhook
        'status': status,  # success, failure, invalid_signature
        'ip_address': ip_address,
        'user_agent': user_agent,
        'event_id': secrets.token_hex(12)
    }

    db.save_audit_log(audit_log)

    # Alert on suspicious activity
    if status == 'failure':
        recent_failures = db.count_recent_failures(user_id, minutes=15)
        if recent_failures > 5:
            send_security_alert(user_id, 'Multiple authentication failures detected')
```

### 4. Rate Limiting with Authentication

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: g.api_key['id'] if hasattr(g, 'api_key') else request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)

@app.get('/data')
@limiter.limit("10 per minute")
def get_data():
    """Rate limited by API key"""
    return jsonify({'data': 'protected'})
```

---

## Industry Examples

### Stripe Authentication

Stripe uses multiple authentication methods:

1. **API Keys** for direct API calls
   ```bash
   curl https://api.stripe.com/v1/charges \
     -u sk_live_abcd1234:
   ```

2. **OAuth 2.0** for third-party integrations
3. **Restricted API Keys** with limited permissions
4. **Webhook Signatures** using HMAC-SHA256

### Twilio Authentication

Twilio primarily uses HTTP Basic Authentication with Account SID and Auth Token:

```bash
curl -X POST https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json \
  -d "To=+1234567890" \
  -d "From=+0987654321" \
  -d "Body=Hello World" \
  -u {AccountSid}:{AuthToken}
```

### GitHub API

GitHub supports multiple authentication methods:

1. **OAuth 2.0** for web flow
2. **Personal Access Tokens** (JWT-like)
3. **GitHub App Installations** for installations

```bash
# Token authentication
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/user

# Signed app JWT
curl -H "Authorization: Bearer YOUR_JWT" \
  https://api.github.com/app
```

---

## Security Checklist

- [ ] All credentials stored in secure environment variables
- [ ] HTTPS/TLS used for all communication
- [ ] Tokens have appropriate expiration times
- [ ] Refresh tokens implemented for long-lived sessions
- [ ] Signatures verified on all signed requests
- [ ] Rate limiting implemented per authentication method
- [ ] Audit logging for all authentication events
- [ ] Key rotation policy established (90 days or less)
- [ ] Revocation mechanism implemented
- [ ] Replay attack prevention (timestamps, nonces)
- [ ] Constant-time comparison for signatures
- [ ] Webhook retry strategy with exponential backoff
- [ ] Monitoring for suspicious authentication patterns
- [ ] Documentation includes security best practices
- [ ] Regular security audits scheduled

---

## References

- [OAuth 2.0 Authorization Framework (RFC 6749)](https://tools.ietf.org/html/rfc6749)
- [JSON Web Token (RFC 7519)](https://tools.ietf.org/html/rfc7519)
- [Proof Key for Public Clients (RFC 7636 - PKCE)](https://tools.ietf.org/html/rfc7636)
- [Stripe API Security](https://stripe.com/docs/security)
- [Twilio API Security](https://www.twilio.com/docs/usage/api#authentication)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
