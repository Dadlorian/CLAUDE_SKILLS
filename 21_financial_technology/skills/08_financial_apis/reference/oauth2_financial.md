# OAuth 2.0 for Financial APIs

## OAuth 2.0 Fundamentals

OAuth 2.0 is the industry-standard authorization protocol. Financial APIs use enhanced profiles for security.

## Grant Types for Financial APIs

### 1. Authorization Code Grant (Most Common)
**Use Case**: Web apps, mobile apps with user interaction

**Flow**:
```
1. User clicks "Login with Bank"
2. App redirects to bank's login page
3. User authenticates and grants permission
4. Bank redirects back with authorization code
5. App exchanges code for access token
6. App uses access token to call APIs
```

**Code Example**:
```python
from urllib.parse import urlencode, parse_qs
import requests

class OAuthClient:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_server = "https://auth.example.com"

    def get_authorization_url(self, scope="accounts transactions"):
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": scope,
            "redirect_uri": self.redirect_uri,
            "state": "random-state-string"
        }
        return f"{self.auth_server}/authorize?{urlencode(params)}"

    def exchange_code_for_token(self, code):
        response = requests.post(
            f"{self.auth_server}/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri
            }
        )
        return response.json()

    def refresh_token(self, refresh_token):
        response = requests.post(
            f"{self.auth_server}/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
        )
        return response.json()
```

### 2. Refresh Token Grant
**Use Case**: Renewing expired access tokens

**Token Rotation Pattern**:
```python
class TokenManager:
    def get_valid_token(self, token_data):
        # Check if access token is still valid
        if not self.is_token_expired(token_data["access_token"]):
            return token_data["access_token"]

        # Refresh token if expired
        new_token_data = self.oauth_client.refresh_token(
            token_data["refresh_token"]
        )

        # Store new token
        self.store_token(new_token_data)

        return new_token_data["access_token"]

    def is_token_expired(self, token):
        import jwt
        try:
            claims = jwt.decode(token, options={"verify_signature": False})
            exp = claims.get("exp")
            import time
            return exp < time.time()
        except:
            return True
```

### 3. Client Credentials Grant
**Use Case**: Backend-to-backend communication

**Use Cases**:
- Server-to-server payment processing
- Administrative operations
- Data synchronization

**Implementation**:
```python
def get_server_token():
    response = requests.post(
        "https://auth.example.com/token",
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "payments read write"
        }
    )
    return response.json()["access_token"]
```

## PKCE (Proof Key for Public Clients)

**Purpose**: Secure authorization code flow for public clients (mobile apps)

**Flow**:
```
1. Generate code_verifier (random string)
2. Create code_challenge = BASE64URL(SHA256(code_verifier))
3. Include code_challenge in authorization request
4. Exchange authorization code WITH code_verifier
5. Authorization server validates challenge matches verifier
```

**Implementation**:
```python
import secrets
import hashlib
import base64

def create_pkce_pair():
    # Generate code verifier
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode('utf-8').rstrip('=')

    # Generate code challenge
    challenge_bytes = hashlib.sha256(
        code_verifier.encode('utf-8')
    ).digest()
    code_challenge = base64.urlsafe_b64encode(
        challenge_bytes
    ).decode('utf-8').rstrip('=')

    return code_verifier, code_challenge

def get_authorization_url_with_pkce():
    code_verifier, code_challenge = create_pkce_pair()

    # Store code_verifier securely for later
    session["code_verifier"] = code_verifier

    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "accounts transactions",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }

    return f"https://auth.example.com/authorize?{urlencode(params)}"

def exchange_code_with_pkce(code):
    code_verifier = session["code_verifier"]

    response = requests.post(
        "https://auth.example.com/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier
        }
    )

    return response.json()
```

## Scope Management

**Common Scopes**:
```
accounts - List accounts
balances - Read balance information
transactions - Read transaction history
payments - Initiate payments
payment_status - Check payment status
offline_access - Get refresh tokens
openid - OpenID Connect (user identity)
```

**Granular Scopes**:
```
accounts:read - Read accounts only
accounts:write - Modify accounts
transactions:read:3m - Last 3 months transactions
transactions:read:12m - Last 12 months transactions
payments:initiate:sepa - SEPA credit transfers
```

**Requesting Scopes**:
```
GET /authorize?...&scope=accounts+balances+transactions+payments
```

## Token Types

### Bearer Token
**Format**: `Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...`

**JWT Structure**:
```json
Header: {
  "alg": "RS256",
  "typ": "JWT"
}

Payload: {
  "iss": "https://auth-server.com",
  "sub": "user-123",
  "aud": "https://api.example.com",
  "iat": 1605793634,
  "exp": 1605797234,
  "scope": "accounts balances transactions"
}

Signature: (RS256 signature)
```

### Refresh Token
**Purpose**: Obtain new access token when expired
**Lifetime**: Longer than access token (months/years)
**Usage**: Server-side only
**Security**: Rotate on each refresh

### Token Introspection
**Purpose**: Check if token is valid

```python
def is_token_valid(token):
    response = requests.post(
        "https://auth.example.com/introspect",
        data={
            "token": token,
            "client_id": client_id,
            "client_secret": client_secret
        }
    )
    return response.json()["active"]
```

## Token Security

### Token Storage
**Mobile Apps**:
- Secure Enclave (iOS)
- Android Keystore (Android)
- NOT in SharedPreferences or localStorage

**Web Apps**:
- HttpOnly cookies (not accessible to JavaScript)
- Secure flag (HTTPS only)
- SameSite=Strict

**Backend**:
- Encrypted database
- HSM or Key Management Service
- Never log tokens

### Token Rotation

```python
class SecureTokenManager:
    def refresh_access_token(self, refresh_token):
        # Get new tokens
        response = requests.post(
            f"{AUTH_SERVER}/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret
            }
        )

        new_tokens = response.json()

        # Revoke old refresh token
        self.revoke_token(refresh_token)

        # Store new tokens
        self.store_tokens(new_tokens)

        return new_tokens["access_token"]

    def revoke_token(self, token):
        requests.post(
            f"{AUTH_SERVER}/revoke",
            data={
                "token": token,
                "client_id": client_id,
                "client_secret": client_secret
            }
        )
```

## Consent & Permissions

### Two-Level Consent

**Level 1: Application Consent**
- User approves app to access financial data
- Managed by authorization server
- Scopes define permissions

**Level 2: Bank Consent (PSD2)**
- User confirms at their bank
- Fine-grained permissions per account
- Time-limited access
- Can be revoked anytime

### Consent UI

```python
def show_consent_screen():
    """
    Display what the app is requesting:
    ☐ View your bank accounts
    ☐ View your transaction history
    ☐ Initiate payments
    ☐ View your balances

    The bank will ask you to confirm these permissions.
    This permission can be revoked at any time.
    """
```

## Error Handling

### OAuth Errors

| Error | Cause | Solution |
|-------|-------|----------|
| invalid_request | Missing/invalid parameter | Check request format |
| invalid_client | Unknown client | Verify client_id |
| invalid_grant | Invalid code or refresh token | Restart OAuth flow |
| unauthorized_client | Grant not allowed | Check client configuration |
| access_denied | User denied permission | Inform user |
| server_error | Authorization server error | Retry with exponential backoff |
| temporarily_unavailable | Server overloaded | Retry later |

**Error Response**:
```json
{
  "error": "invalid_grant",
  "error_description": "Authorization code has expired",
  "error_uri": "https://auth-server.com/docs/errors/invalid-grant"
}
```

## Best Practices

### 1. Use HTTPS Always
- All OAuth endpoints must use HTTPS
- Modern TLS (1.2+)
- Valid certificates

### 2. Validate State Parameter
```python
def callback(code, state):
    if state != session.get("oauth_state"):
        raise ValueError("Invalid state parameter - CSRF attack?")

    # Continue with token exchange
```

### 3. Implement Timeout
```python
def exchange_code_with_timeout(code):
    try:
        return requests.post(
            TOKEN_ENDPOINT,
            data=token_data,
            timeout=5  # 5 second timeout
        )
    except requests.Timeout:
        # Handle timeout
        log_error("Token endpoint timeout")
```

### 4. Secure Logout
```python
def logout(refresh_token):
    # Revoke token
    requests.post(
        f"{AUTH_SERVER}/revoke",
        data={"token": refresh_token}
    )

    # Clear local session
    session.clear()

    # Redirect to login
```

## Testing Checklist

- [ ] Test authorization code flow
- [ ] Test refresh token flow
- [ ] Test PKCE flow
- [ ] Test invalid client
- [ ] Test invalid code
- [ ] Test expired token
- [ ] Test revoked token
- [ ] Test rate limiting
- [ ] Test state validation
- [ ] Security audit

## References

- OAuth 2.0 Core (RFC 6749): https://tools.ietf.org/html/rfc6749
- OAuth 2.0 Bearer Token (RFC 6750): https://tools.ietf.org/html/rfc6750
- PKCE (RFC 7636): https://tools.ietf.org/html/rfc7636
- Token Introspection (RFC 7662): https://tools.ietf.org/html/rfc7662
- Token Revocation (RFC 7009): https://tools.ietf.org/html/rfc7009
