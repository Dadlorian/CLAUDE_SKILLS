# FAPI Security Standards

## FAPI Overview

Financial-grade API (FAPI) is an OpenID Foundation standard providing enhanced security for APIs serving financial services.

## FAPI Versions

### FAPI 1.0 (Stable)
- **Level 1**: Standard security for open banking
- **Level 2**: Enhanced security with mutual TLS and signatures

**Status**: Production ready
**Used by**: Major banks and fintechs worldwide

### FAPI 2.0 (Emerging)
- **Introduction**: Incorporates modern security practices
- **Status**: Specification in final stages
- **Focus**: Simplified but more secure approach

## FAPI 1 Level 1 Security

### OAuth 2.0 Baseline
- Authorization Code flow with PKCE
- Refresh token rotation
- Bearer token in Authorization header
- Token expiration enforcement

### Request/Response Integrity
- **JARM** (JWT Secured Authorization Response Mode)
- Signed and encrypted authorization responses
- Response object signing required
- Response object encryption optional

### Artifact Parameter
- Authorization server returns signed JWT instead of query parameters
- Client fetches actual response via backchannel
- Prevents accidental exposure in logs/URLs

## FAPI 1 Level 2 Security

### Mutual TLS (mTLS)
**Requirements**:
- Both client and server present certificates
- Certificate-based authentication
- mTLS_client_auth parameter

**Implementation**:
```
1. Client certificate validation
2. Server certificate validation
3. Certificate pinning recommended
4. Certificate rotation procedures
```

### Request Signing
**JAR** (JWT Secured Authorization Request)
- Authorization request wrapped in JWT
- Request claims signed
- Prevents parameter tampering
- Server validates signature

**Implementation**:
```
POST /authorize HTTP/1.1
Host: auth-server.example.com
Content-Type: application/x-www-form-urlencoded

response_type=code&
client_id=s6BhdRkqt3&
request=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response Signing
**JARM** (JWT Secured Authorization Response Mode)
- Authorization response as signed JWT
- Prevents man-in-the-middle attacks
- Response parameter encryption optional

**Format**:
```
HTTP/1.1 302 Found
Location: https://client.example.com/callback?response=eyJhbGciOi...
```

## Token Standards

### Access Token Requirements
- Bearer tokens in Authorization header
- Token lifetime: 15 minutes recommended
- Token endpoint uses mTLS or client authentication

### Refresh Token Requirements
- Issued at authorization
- Refresh token rotation mandatory
- Sender-constrained tokens
- Binding to client certificate

### Token Binding
**Types**:
1. **mTLS Sender Constraint** - Certificate matches
2. **Token Binding Header** - Cryptographic binding
3. **DPoP** (Demonstration of Proof-of-Possession) - HTTP signature

## Authorization Code Flow (FAPI 1 Level 2)

```
┌──────────┐                                  ┌──────────────┐
│  Client  │                                  │ Auth Server  │
└────┬─────┘                                  └────┬─────────┘
     │                                             │
     │ 1. POST /authorize (signed JAR)            │
     ├────────────────────────────────────────────>│
     │                                             │ Validate signature
     │                                             │ Validate client mTLS
     │                                             │
     │ 2. Redirect to login (same TLS session)    │
     │<────────────────────────────────────────────┤
     │                                             │
     │ 3. User authenticates + authorizes         │
     │ (all in secure TLS channel)                │
     │                                             │
     │ 4. Redirect with signed JWT response       │
     │<────────────────────────────────────────────┤
     │                                             │
     │ 5. Exchange code for token (mTLS)          │
     ├────────────────────────────────────────────>│
     │                                             │
     │ 6. Return access + refresh tokens          │
     │<────────────────────────────────────────────┤
     │                                             │
```

## Certificate Requirements

### QWAC (Qualified Website Authentication Certificate)
- Issued under eIDAS regulation (EU)
- Contains:
  - Organization identifier
  - Domain name
  - Organization contact info
- Validation: Check extended attributes

### Server Certificate
- Valid CA chain
- Proper domain matching
- Current validity period
- No revocation (check OCSP)

### Client Certificate
- Same requirements as QWAC for sensitive clients
- Self-signed acceptable for lower-risk operations
- Proper key management

### Certificate Pinning
```python
# Pin specific certificate for bank API
PINNED_CERT_HASH = "sha256/X3pGTSOuJeED5d..."

def verify_pinned_cert(cert):
    cert_hash = hashlib.sha256(cert).digest()
    return base64.b64encode(cert_hash).decode() == PINNED_CERT_HASH
```

## Implementation Steps

### 1. Register Client
```
POST /register
Content-Type: application/json

{
  "client_name": "FinTech App",
  "application_type": "web",
  "response_types": ["code id_token"],
  "grant_types": ["authorization_code", "refresh_token"],
  "redirect_uris": ["https://app.example.com/callback"],
  "token_endpoint_auth_method": "tls_client_auth",
  "request_object_signing_alg": "RS256",
  "response_types": ["code id_token"],
  "jwks_uri": "https://app.example.com/.well-known/jwks.json"
}
```

### 2. Build Signed Authorization Request
```python
import json
import jwt
from datetime import datetime, timedelta

def create_auth_request(client_id, scope, state, redirect_uri):
    claims = {
        "iss": client_id,
        "aud": "https://auth-server.example.com",
        "response_type": "code id_token",
        "client_id": client_id,
        "scope": scope,
        "state": state,
        "redirect_uri": redirect_uri,
        "nonce": "random-nonce",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=5),
        "response_mode": "jwt"
    }

    return jwt.encode(
        claims,
        private_key,
        algorithm="RS256"
    )
```

### 3. Handle JWT Response
```python
def verify_auth_response(response_jwt):
    # Verify signature
    claims = jwt.decode(
        response_jwt,
        server_public_key,
        algorithms=["RS256"],
        audience=client_id,
        issuer="https://auth-server.example.com"
    )

    # Verify claims
    assert claims["aud"] == client_id
    assert claims["state"] == original_state

    return claims.get("code"), claims.get("id_token")
```

### 4. Exchange Code for Token (mTLS)
```python
import requests
from requests.auth import HTTPBasicAuth

def exchange_code(code):
    # Create mTLS session
    session = requests.Session()
    session.cert = ("client_cert.pem", "client_key.pem")

    response = session.post(
        "https://auth-server.example.com/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "redirect_uri": redirect_uri
        },
        verify="bank_ca_cert.pem"
    )

    return response.json()
```

## Security Considerations

### Private Key Management
- Store in secure key management system (HSM/KMS)
- Rotate keys regularly (annually minimum)
- Use separate keys for signing and encryption
- Never log or expose private keys

### State Parameter
- Must be cryptographically random
- Validate state in callback
- One-time use per authorization
- Bind to user session

### Nonce Parameter
- Prevent replay attacks
- Validate in returned ID token
- One-time use
- Cryptographically random

### HTTPS Requirements
- TLS 1.3 preferred, 1.2 minimum
- Strong cipher suites only
- HSTS headers recommended
- No mixed content

## Common Vulnerabilities

### Insecure Redirect
**Risk**: OAuth code to wrong URL
**Protection**: Whitelist redirect URIs exactly

### Token Interception
**Risk**: Stealing bearer tokens
**Protection**: Use token binding or DPoP

### CSRF
**Risk**: Forcing user to authorize
**Protection**: State parameter + same-site cookies

### Code Injection
**Risk**: Tampering with authorization request
**Protection**: Sign all requests (JAR)

## Testing Checklist

- [ ] Validate certificate chain
- [ ] Test token expiration
- [ ] Test refresh token rotation
- [ ] Verify request signatures
- [ ] Verify response signatures
- [ ] Test mTLS connection
- [ ] Test state parameter
- [ ] Test nonce validation
- [ ] Test redirect URI validation
- [ ] Security audit
- [ ] Penetration testing

## References

- FAPI 1.0 Final: https://openid.net/specs/openid-financial-api-part-1-1_0.html
- FAPI 2.0 Draft: https://openid.net/fapi/
- JAR (RFC 9101): https://tools.ietf.org/html/rfc9101
- JARM: https://openid.net/specs/jwt-secured-authorization-response-mode.html
- mTLS: https://tools.ietf.org/html/draft-ietf-oauth-mtls
