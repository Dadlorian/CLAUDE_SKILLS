# Healthcare OAuth 2.0 & OpenID Connect Security Guide

**Version**: 3.1.0
**Last Updated**: 2025-11-19
**Status**: Production Ready
**Standards Compliance**: OAuth 2.0 (RFC 6749), OpenID Connect 1.0, SMART on FHIR, HIPAA, HITRUST

---

## Executive Summary

This guide establishes production-grade security standards for implementing OAuth 2.0 and OpenID Connect (OIDC) in healthcare environments. It addresses the specific requirements of SMART on FHIR applications, EHR integrations, and clinical workflow authentication.

---

## 1. OAuth 2.0 Core Implementation

### 1.1 Authorization Flows

**Healthcare Authorization Code Flow (Recommended for EHR Integration):**

```
┌─────────┐                            ┌────────────────┐
│ EHR App │                            │  Identity      │
│         │                            │  Provider      │
└────┬────┘                            └────────┬───────┘
     │                                          │
     │ 1. Redirect to authorization endpoint   │
     │ (with client_id, redirect_uri, scope)  │
     ├─────────────────────────────────────────>
     │                                          │
     │                2. User authentication   │
     │  (Login, MFA, consent to data access)  │
     │         <────────────────────────────────┤
     │                                          │
     │ 3. Authorization code returned          │
     │         <────────────────────────────────┤
     │         (code=abc123, state=xyz)        │
     │                                          │
     │ 4. Exchange code for token              │
     │ (code, client_id, client_secret)        │
     ├─────────────────────────────────────────>
     │                                          │
     │ 5. Access token + ID token returned     │
     │         <────────────────────────────────┤
     │         (access_token, id_token,        │
     │          refresh_token, expires_in)    │
     │                                          │
```

**Protocol Parameters:**

```
Authorization Request:
GET /authorize?
  client_id=ehr-app-123
  &response_type=code
  &scope=launch%20openid%20profile%20fhirUser%20
         patient%2FPatient.read%20patient%2FObservation.read
  &redirect_uri=https://app.example.com/callback
  &state=security_token_123
  &aud=https://fhir.example.com/Patient

Token Request:
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=SplxlOBeZQQYbYS6WxSbIA
&redirect_uri=https://app.example.com/callback
&client_id=ehr-app-123
&client_secret=[CONFIDENTIAL]

Token Response:
{
  "access_token": "SlAV32hkKG...",
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjE...",
  "refresh_token": "8xLOxBtZp8",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "openid profile patient/Patient.read"
}
```

### 1.2 Supported Grant Types for Healthcare

**Authorization Code Grant (Recommended):**
- Use case: Web applications, EHR integrations
- Flow: User redirected to login, receives code, code exchanged for token
- Security: Server-side token exchange, client secret protection
- PKCE support: Required for mobile/public clients

**Refresh Token Grant:**
```
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
&refresh_token=8xLOxBtZp8
&client_id=ehr-app-123
&client_secret=[CONFIDENTIAL]
```

**Client Credentials Grant:**
- Use case: Service-to-service, machine-to-machine access
- Restrictions: Cannot access patient data, only system/organizational data
- Requires: Valid client_id and client_secret

**PKCE (Proof Key for Code Exchange) - MANDATORY for Mobile:**
```
1. Client generates code_verifier (random 43-128 character string)
   code_verifier = "E9Mrozoa2owUednMAlxTeSCo-t4z22-50DPohfRQj_4"

2. Client creates code_challenge
   code_challenge = BASE64URL(SHA256(code_verifier))
   code_challenge = "E9Mrozoa2owUednMAlxTeSCo-t4z22-50DPohfRQj_4"

3. Authorization request includes code_challenge
   GET /authorize?
     ...
     &code_challenge=E9Mrozoa2owUednMAlxTeSCo-t4z22-50DPohfRQj_4
     &code_challenge_method=S256

4. Token request includes code_verifier
   POST /token
   ...
   &code_verifier=E9Mrozoa2owUednMAlxTeSCo-t4z22-50DPohfRQj_4
```

---

## 2. SMART on FHIR Implementation

### 2.1 SMART App Launch Flow

**Patient-Facing App Launch:**
```
1. EHR launches app with context:
   https://ehr.example.com/launch?
     iss=https://fhir.ehr.example.com
     &launch=eyJhbGciOiJSUzI1NiJ9...

2. App discovers OpenID Connect metadata:
   GET /.well-known/smart-configuration

   Response includes:
   {
     "authorization_endpoint": "https://fhir.ehr.example.com/authorize",
     "token_endpoint": "https://fhir.ehr.example.com/token",
     "userinfo_endpoint": "https://fhir.ehr.example.com/userinfo",
     "jwks_uri": "https://fhir.ehr.example.com/keys",
     "grant_types_supported": ["authorization_code", "refresh_token"],
     "scopes_supported": ["openid", "fhirUser", "launch",
                         "patient/Patient.read", "user/Observation.read"],
     "code_challenge_methods_supported": ["S256"]
   }

3. App redirects to authorization with launch context:
   GET /authorize?
     client_id=app-client-id
     &response_type=code
     &scope=openid%20profile%20fhirUser%20launch%20
            patient%2FPatient.read%20patient%2FObservation.read
     &redirect_uri=https://app.example.com/callback
     &launch=eyJhbGciOiJSUzI1NiJ9...
     &state=1234567890
     &aud=https://fhir.ehr.example.com

4. EHR returns authorization code:
   https://app.example.com/callback?
     code=SecurCodeValue123
     &state=1234567890

5. App exchanges code for tokens (includes client_secret):
   POST /token
   client_id=app-client-id
   &client_secret=[CONFIDENTIAL]
   &code=SecurCodeValue123
   &grant_type=authorization_code
   &redirect_uri=https://app.example.com/callback

6. Tokens returned with patient context:
   {
     "access_token": "eyJhbGciOiJSUzI1NiJ9...",
     "id_token": "eyJhbGciOiJSUzI1NiJ9...",
     "refresh_token": "eyJhbGciOiJSUzI1NiJ9...",
     "token_type": "Bearer",
     "expires_in": 3600
   }

7. App decodes ID token to get patient context:
   {
     "iss": "https://fhir.ehr.example.com",
     "sub": "user-123",
     "aud": "app-client-id",
     "exp": 1234567890,
     "iat": 1234564290,
     "fhirUser": "Practitioner/physician-456",
     "patient": "Patient/patient-789"  // <- Patient context
   }
```

### 2.2 SMART Scopes for Healthcare

**Scope Hierarchy:**
```
Core Scopes:
  openid              - Required for OpenID Connect
  fhirUser            - Returns FHIR Practitioner/Patient context
  launch              - Required for EHR launch context
  profile             - Access to user profile (name, email, etc.)

Clinical Scopes (FHIR Resources):
  patient/Patient.read        - Read patient demographics
  patient/Patient.write       - Write patient demographics
  user/Patient.read           - Read any patient
  user/Patient.write          - Write any patient
  system/Patient.read         - System-level patient access
  system/Patient.write        - System-level patient access

  patient/Observation.read    - Read patient observations
  patient/MedicationRequest.write  - Write prescriptions
  user/*.read                 - Read any FHIR resource
  system/*.read               - System read access
  system/*.write              - System write access

Additional Scopes:
  offline_access              - Request refresh token
  launch/patient              - Allow EHR to select patient context
  launch/encounter            - Allow EHR to select encounter context
```

**Scope Examples by Use Case:**

```
Patient Portal (Patient-Facing):
  scope=openid profile fhirUser patient/Patient.read
        patient/Observation.read patient/MedicationRequest.read
        offline_access

Clinical Decision Support:
  scope=openid fhirUser user/Patient.read user/Observation.read
        user/Condition.read user/MedicationRequest.read

Administrative Reporting:
  scope=system/Patient.read system/Observation.read
        system/Encounter.read

Research/Cohort Matching:
  scope=system/Patient.read system/Observation.read
        system/Condition.read (requires additional governance)
```

---

## 3. Token Security & Management

### 3.1 Access Token Standards

**Required Token Format:**
```
Type: JWT (JSON Web Token)
Header:
{
  "alg": "RS256",           // RSA with SHA-256
  "typ": "JWT",
  "kid": "2024-key-id"      // Key ID for rotation
}

Payload:
{
  "iss": "https://idp.example.com",           // Issuer
  "sub": "user-uuid-123",                     // Subject
  "aud": "https://fhir.ehr.example.com",      // Audience/Resource
  "exp": 1234567890,                          // Expiration
  "iat": 1234564290,                          // Issued at
  "nbf": 1234564290,                          // Not before
  "jti": "token-id-xyz",                      // JWT ID (unique)
  "client_id": "app-client-id",
  "scope": "openid patient/Patient.read",
  "fhirUser": "Practitioner/physician-456",
  "patient": "Patient/patient-789",
  "org": "Organization/hospital-001",
  "acr": "urn:mace:incommon:iap:silver"        // Auth context class
}

Signature:
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret
)
```

**Token Lifetime Requirements:**
```
Access Token:     15-60 minutes (shorter is better)
Refresh Token:    7-90 days
ID Token:         15-60 minutes (same as access token)
Authorization Code: 10 minutes (single-use)
```

**Token Validation Checklist:**
```
✓ Verify JWT signature using issuer's public key (jwks_uri)
✓ Check "iss" claim matches expected identity provider
✓ Check "aud" claim includes resource/API endpoint
✓ Verify token not expired (exp claim)
✓ Verify token not before issued (nbf claim)
✓ Check "sub" claim identifies user/principal
✓ Validate "scope" claim includes required permissions
✓ For FHIR: Validate patient context in "patient" claim
✓ Verify jti (JWT ID) not seen before (replay prevention)
✓ Validate client_id matches registered client
```

### 3.2 Refresh Token Management

**Refresh Token Rotation:**
```
Scenario: Access token expired, client requests new one

POST /token
grant_type=refresh_token
&refresh_token=old-refresh-token-value
&client_id=app-client-id
&client_secret=[CONFIDENTIAL]

Server Response:
✓ Validate refresh token hasn't been revoked
✓ Validate client credentials match original grant
✓ Issue new access token
✓ Return new refresh token (rotate)
✓ Invalidate old refresh token

Response:
{
  "access_token": "new-access-token-jwt",
  "refresh_token": "new-refresh-token-value",
  "token_type": "Bearer",
  "expires_in": 3600
}

Refresh Token Rotation:
  - Each refresh must return a new refresh token
  - Old refresh token becomes invalid
  - Prevents token compromise from being exploitable long-term
  - Enables detection of token theft (multiple refresh attempts)
```

**Token Revocation:**
```
Endpoint: POST /revoke

Client can revoke tokens:
  POST /revoke
  token=access_token_value
  &token_type_hint=access_token
  &client_id=app-client-id
  &client_secret=[CONFIDENTIAL]

Server revokes:
  ✓ Immediately invalidate token
  ✓ Remove from cache
  ✓ Log revocation event
  ✓ Return 200 OK

Use cases:
  - User logout
  - Application deinstallation
  - Suspicious activity detected
  - User permissions revoked
```

---

## 4. OpenID Connect Implementation

### 4.1 ID Token Claims

**Required ID Token Claims:**
```
Standard OIDC Claims:
{
  "iss": "https://idp.example.com",
  "sub": "user-unique-identifier",
  "aud": "client-application-id",
  "exp": 1234567890,
  "iat": 1234564290,
  "auth_time": 1234564290,
  "acr": "urn:mace:incommon:iap:silver"
}

Healthcare-Specific Claims:
{
  "fhirUser": "Practitioner/doctor-123 or Patient/patient-456",
  "email": "user@hospital.example.com",
  "email_verified": true,
  "given_name": "John",
  "family_name": "Doe",
  "name": "John Doe",
  "picture": "https://idp.example.com/pics/user.jpg"
}

SMART on FHIR Claims:
{
  "fhirUser": "Practitioner/123",
  "patient": "Patient/456",
  "encounter": "Encounter/789",
  "identity_assurance_level": "2"
}
```

### 4.2 UserInfo Endpoint

**Getting Additional User Information:**
```
Client requests user information:
GET /userinfo
Authorization: Bearer {access_token}

Server returns:
{
  "sub": "user-123",
  "email": "john.doe@hospital.example.com",
  "email_verified": true,
  "name": "John Doe",
  "given_name": "John",
  "family_name": "Doe",
  "phone_number": "+1-555-123-4567",
  "phone_number_verified": true,
  "fhirUser": "Practitioner/123",
  "organization": "Hospital Medical Center",
  "department": "Cardiology",
  "roles": ["physician", "researcher"],
  "security_labels": ["R", "U"]
}
```

---

## 5. Security Requirements

### 5.1 Client Registration & Authentication

**Client Registration Process:**

```
Dynamic Registration (OAuth 2.0 Dynamic Client Registration):
POST /register
Content-Type: application/json

{
  "client_name": "Clinical Decision Support App",
  "client_uri": "https://app.example.com",
  "response_types": ["code"],
  "grant_types": ["authorization_code", "refresh_token"],
  "redirect_uris": ["https://app.example.com/callback"],
  "token_endpoint_auth_method": "client_secret_basic",
  "scope": "openid fhirUser patient/Patient.read",
  "logo_uri": "https://app.example.com/logo.png",
  "jwks_uri": "https://app.example.com/jwks",
  "contacts": ["admin@app.example.com"]
}

Response:
{
  "client_id": "app-client-id-12345",
  "client_secret": "super-secret-value-do-not-share",
  "registration_access_token": "reg-access-token",
  "client_id_issued_at": 1234564290,
  "client_secret_expires_at": 1234564290 + (90 days in seconds)
}
```

**Client Authentication Methods:**

```
1. HTTP Basic Authentication (client_secret_basic)
   Authorization: Basic base64(client_id:client_secret)
   Most common, MUST use HTTPS

2. Request Body (client_secret_post) - Legacy, not recommended
   POST /token
   client_id=id&client_secret=secret

3. Mutual TLS (tls_client_auth) - Recommended for mobile
   Use client certificate for mutual authentication
   No client_secret transmitted

4. JWT Bearer Token (private_key_jwt)
   POST /token
   client_assertion_type=urn:ietf:params:oauth:assertion-type:jwt-bearer
   &client_assertion=signed-jwt-with-client-private-key
```

### 5.2 Threat Protection

**CSRF (Cross-Site Request Forgery) Protection:**
```
✓ State Parameter (REQUIRED for web apps)
  GET /authorize?
    ...
    &state=random-unguessable-value-xyz

  Response includes:
  ?code=auth-code&state=random-unguessable-value-xyz

  Client must verify returned state matches original state

✓ Nonce (REQUIRED for ID token binding)
  GET /authorize?
    ...
    &nonce=random-unguessable-value-abc

  ID Token includes nonce claim (must match)
  Prevents token substitution attacks
```

**Token Injection Protection:**
```
✓ JWT Validation
  - Verify signature on all JWTs
  - Check issuer (iss claim)
  - Check audience (aud claim)
  - Verify expiration (exp claim)

✓ Redirect URI Whitelisting
  - Must exactly match registered redirect_uri
  - Cannot use wildcard subdomains (*.example.com invalid)
  - HTTPS required (except localhost)
  - Prevents open redirects

✓ Response Type Binding
  - authorization_code flow: use code parameter
  - Implicit flow deprecated: never use id_token,token in response_type
  - Use form_post_response_mode when possible
```

**Man-in-the-Middle (MITM) Protection:**
```
✓ HTTPS/TLS
  - All endpoints MUST use HTTPS
  - TLS 1.2 minimum (TLS 1.3 preferred)
  - Valid certificate from trusted CA
  - Certificate pinning for mobile apps

✓ PKCE (Proof Key for Code Exchange)
  - Prevents authorization code interception
  - Mandatory for public clients (mobile, browser)
  - Recommended for all clients

✓ Mutual TLS (mTLS)
  - Client certificate authentication
  - Prevents impersonation attacks
  - Required for service-to-service
```

---

## 6. Consent & Privacy

### 6.1 User Consent Management

**Consent Screen Requirements:**
```
Before user grants access, application must display:

1. What data is being requested
   "This app requests access to:"
   ✓ Your name and email address
   ✓ Your health records (observations, medications)
   ✓ Your allergy information

2. What purposes (if not obvious)
   "For the purpose of:"
   ✓ Displaying your current medications
   ✓ Generating medication interaction alerts
   ✓ Tracking appointment compliance

3. What permissions are granted
   "This app will be able to:"
   ✓ Read your patient information
   ✓ Read your clinical observations
   ✓ NOT write or modify your records

4. Duration of access
   "Until you:"
   ✓ Logout from the application
   ✓ Revoke access in your privacy settings
   ✓ Delete the application (after 90 days inactivity)

5. Privacy policy link
   "For more information, see our privacy policy"
```

**Consent Recording:**
```json
{
  "consent_id": "consent-uuid-12345",
  "user_id": "user-uuid",
  "client_id": "app-client-id",
  "scope": "openid profile patient/Patient.read patient/Observation.read",
  "timestamp": "2025-11-19T10:30:00Z",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "consent_version": "1.0",
  "expires_at": "2026-11-19T10:30:00Z",
  "revoked_at": null,
  "revoked_reason": null
}
```

---

## 7. Healthcare-Specific Requirements

### 7.1 HIPAA & HITRUST Compliance

**Audit Logging for Authentication:**
```json
{
  "audit_id": "audit-uuid",
  "event_type": "OAUTH_TOKEN_ISSUED",
  "timestamp": "2025-11-19T10:30:00Z",
  "user_id": "user-123",
  "client_id": "app-client-id",
  "client_name": "Clinical Decision Support",
  "scope": "openid fhirUser patient/Patient.read",
  "result": "SUCCESS",
  "ip_address": "192.168.1.1",
  "authentication_method": "username_password_mfa",
  "mfa_method": "totp",
  "patient_context": "Patient/456",
  "organization": "Hospital Medical Center"
}
```

**Privacy & Security Requirements:**
- Encrypt tokens at rest in database
- Encrypt in transit (TLS 1.2+)
- Encrypt sensitive claims in JWT
- Log all authentication events
- Audit all token usage
- Implement automatic token expiration
- Monitor for suspicious patterns
- Implement rate limiting on token endpoints

### 7.2 MFA (Multi-Factor Authentication) Requirements

**MFA is MANDATORY for:**
```
✓ Clinician access (HIPAA requirement for healthcare staff)
✓ Administrator accounts (all privileged users)
✓ APIs accessing patient data
✓ Research applications with large datasets

Recommended MFA Methods:
  1. TOTP (Time-based One-Time Password)
     - Google Authenticator, Authy
     - Built into most smartphones
     - No external dependency

  2. SMS/Text Message OTP
     - Fallback for users without authenticator app
     - Less secure than TOTP
     - Cost implications at scale

  3. Push Notification
     - Okta, Duo, Microsoft Authenticator
     - User taps "Approve" on phone
     - Prevents phishing (user controls approval)

  4. Biometric (Fingerprint, Face ID)
     - Mobile app authentication
     - High security, good UX

MFA Configuration:
POST /oauth/mfa/setup
response_type: code
&mfa_method: totp

Returns: QR code for authenticator app
User scans QR, confirms 6-digit code
MFA enrollment complete

Login with MFA:
POST /token
username=user@hospital.example.com
&password=user-password
&mfa_code=123456 (from authenticator app)
```

---

## 8. Monitoring & Incident Response

### 8.1 Security Alerts & Thresholds

```
Critical (Immediate Investigation):
  - Failed login attempts > 10 in 5 minutes per user
  - Token validation failures > 50 per minute
  - Authorization failures for admin accounts
  - Refresh token reuse detected
  - Invalid client credentials > 20 attempts
  - Authorization endpoint response > 10 seconds

Warning (Review within 1 hour):
  - Failed login attempts > 5 in 5 minutes per user
  - Unusual client IP address
  - Token request from new geographic location
  - Unusual scopes requested
  - Off-hours authentication for sensitive accounts

Info (Monitor trend):
  - New client registration
  - Client scope upgrade
  - Token revocation events
  - Account deactivation
```

### 8.2 Metrics Collection

```
Performance Metrics:
  - Authorization endpoint response time (target: < 500ms)
  - Token endpoint response time (target: < 1s)
  - Token validation latency (target: < 50ms)
  - JWKS cache effectiveness
  - OIDC metadata freshness

Security Metrics:
  - Failed authentication rate (target: < 1%)
  - MFA adoption rate (target: 100% for clinicians)
  - Token expiration distribution
  - Refresh token rotation success rate
  - Consent grant count by application

Business Metrics:
  - Active OAuth clients
  - Unique users authenticated daily
  - Total tokens issued per hour
  - Patient data access requests
  - API usage by client application
```

---

## 9. Configuration Examples

### 9.1 .well-known/openid-configuration

```json
{
  "issuer": "https://idp.example.com",
  "authorization_endpoint": "https://idp.example.com/authorize",
  "token_endpoint": "https://idp.example.com/token",
  "userinfo_endpoint": "https://idp.example.com/userinfo",
  "jwks_uri": "https://idp.example.com/.well-known/jwks.json",
  "scopes_supported": [
    "openid", "profile", "email", "phone",
    "fhirUser", "launch",
    "patient/Patient.read", "patient/Observation.read",
    "user/Patient.read", "user/Observation.read",
    "offline_access"
  ],
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "token_endpoint_auth_methods_supported": [
    "client_secret_basic", "private_key_jwt"
  ],
  "token_endpoint_auth_signing_alg_values_supported": ["RS256"],
  "code_challenge_methods_supported": ["S256"],
  "response_modes_supported": ["query", "form_post"],
  "subject_types_supported": ["public", "pairwise"],
  "id_token_signing_alg_values_supported": ["RS256"],
  "claim_types_supported": ["normal", "aggregated"],
  "claims_supported": [
    "sub", "iss", "aud", "exp", "iat", "auth_time",
    "name", "given_name", "family_name", "email", "email_verified",
    "fhirUser", "patient", "encounter"
  ],
  "request_parameter_supported": false,
  "request_uri_parameter_supported": false,
  "require_request_uri_registration": false,
  "acr_values_supported": ["urn:mace:incommon:iap:silver"]
}
```

---

## 10. Common Issues & Troubleshooting

**Issue: "invalid_grant" error on token request**
- Cause: Authorization code expired (>10 min), already used, or invalid
- Solution: Verify code matches original grant, complete flow within timeout window

**Issue: Token validation failing with signature error**
- Cause: Using wrong JWKS endpoint, key rotation, or code/key mismatch
- Solution: Refresh JWKS from jwks_uri, verify iss and kid claims

**Issue: Patient context missing from tokens**
- Cause: SMART launch scope not requested, or EHR doesn't support SMART
- Solution: Include "launch" scope in authorization request

**Issue: Refresh token rejected**
- Cause: Token expired, revoked, or client_id mismatch
- Solution: Use within refresh_token lifetime, ensure client credentials correct

---

## Governance Checklist

**Before OAuth Implementation:**
- [ ] Identity provider selected and evaluated
- [ ] TLS certificates provisioned and configured
- [ ] JWKS endpoints configured for key rotation
- [ ] Audit logging implemented
- [ ] MFA requirement policy documented
- [ ] Consent screens reviewed for HIPAA compliance
- [ ] Rate limiting configured on auth endpoints
- [ ] Token lifetime policies defined
- [ ] Incident response procedures documented
- [ ] Security test plan completed

---

**Contact**: Healthcare Security & Identity Management Team
**Last Reviewed**: 2025-11-19
