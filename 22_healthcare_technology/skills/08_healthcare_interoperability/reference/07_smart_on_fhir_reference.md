# SMART on FHIR Reference Guide

## Overview

SMART (Substitutable Medical Applications, Reusable Technology) on FHIR provides a secure authorization and integration framework for healthcare applications using OAuth 2.0 and FHIR APIs.

## Core Concepts

### SMART Workflow

```
1. User launches SMART app from EHR
2. EHR provides launch context
3. App initiates OAuth authorization
4. User grants consent
5. EHR provides access token
6. App calls FHIR API with token
7. FHIR server validates and returns data
8. App displays information
```

## OAuth 2.0 Framework

### Authorization Code Flow

```
┌─────────────┐
│   SMART     │
│     App     │
└──────┬──────┘
       │ 1. Redirects user to EHR
       │    with client_id, scopes
       ↓
┌─────────────────┐
│  Authorization  │    2. User authenticates
│   Endpoint      │       and grants consent
└────────┬────────┘
         │ 3. Returns authorization code
         ↓
┌─────────────┐
│  SMART App  │    4. Exchanges code
│             │       for access token
└──────┬──────┘
       │ 5. Token received
       ↓
┌─────────────────┐
│  FHIR API       │    6. App calls with token
│  Server         │    7. Returns protected resources
└─────────────────┘
```

### SMART Scopes

#### Patient-Facing Scopes
```
patient/Patient.read              - Read own demographics
patient/Observation.read          - Read own observations
patient/MedicationRequest.read    - Read own medications
patient/Condition.read            - Read own conditions
patient/DocumentReference.read    - Read own documents
patient/*.read                    - Read all patient resources
patient/*.write                   - Write all patient resources
```

#### Provider-Facing Scopes
```
user/Patient.read                 - Read any patient demographics
user/Observation.read             - Read any observations
user/MedicationRequest.*          - Full medication access
user/Condition.*                  - Full condition access
user/Encounter.read               - Read encounters
user/*.read                       - Read all resources
```

#### System Scopes
```
system/Patient.read               - System access to patients
system/Observation.read           - System access to observations
system/MedicationRequest.read     - System access to medications
system/*.read                     - Read all system resources
system/*.write                    - Write all system resources
```

### Launch Context

#### Patient Launch
```json
{
  "scope": "patient/Patient.read patient/Observation.read",
  "launch": "patient-123",
  "aud": "https://fhir-server.example.com"
}
```

#### Provider Launch
```json
{
  "scope": "user/Patient.read user/Encounter.read",
  "launch": "provider-context-xyz",
  "aud": "https://fhir-server.example.com",
  "patient": "patient-123",
  "encounter": "encounter-456"
}
```

#### Standalone Launch
```json
{
  "client_id": "app-123",
  "redirect_uri": "https://app.example.com/callback",
  "response_type": "code",
  "scope": "offline_access patient/Patient.read",
  "state": "random-state-string"
}
```

## Application Authorization

### Authorization Request
```
GET /auth/authorize?
  response_type=code&
  client_id=client-123&
  redirect_uri=https://app.example.com/callback&
  scope=patient/Patient.read%20patient/Observation.read&
  state=random-state&
  launch=launch-token
```

### Token Request
```
POST /auth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=authorization-code&
client_id=client-123&
redirect_uri=https://app.example.com/callback&
client_secret=secret-key (if confidential)
```

### Token Response
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "refresh-token-xyz",
  "scope": "patient/Patient.read patient/Observation.read"
}
```

## FHIR API Calls with SMART

### Request with Bearer Token
```
GET /fhir/Patient/patient-123 HTTP/1.1
Host: fhir-server.example.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/fhir+json
```

### Response
```json
{
  "resourceType": "Patient",
  "id": "patient-123",
  "name": [{"family": "Doe", "given": ["John"]}],
  "birthDate": "1970-01-01"
}
```

## Application Types

### Public/Standalone Applications
- No backend server
- JavaScript/web-based
- Cannot store secrets securely
- Uses PKCE (Proof Key for Code Exchange)
- Examples: Patient portals, mobile apps

### Confidential Applications
- Secure backend server
- Can store client secrets
- Direct OAuth flow
- Examples: EHR integrations, enterprise apps

## PKCE (Proof Key for Code Exchange)

### For Public Apps
```
1. Generate code_verifier (random string 43-128 chars)
2. Create code_challenge = base64url(sha256(code_verifier))
3. Send challenge in auth request
4. EHR validates: sha256(code) == challenge
5. Extra security layer without storing secret
```

### Implementation
```
code_verifier = "abcdefghijklmnopqrstuvwxyz123456789012345678"
code_challenge = base64url(sha256(code_verifier))

Authorization Request:
GET /auth/authorize?
  ...&
  code_challenge=E9Mrozoa2owUedPyAPfRAhgFrZs3CJJstucboj73KQ&
  code_challenge_method=S256
```

## JWT (JSON Web Tokens)

### Token Claims
```json
{
  "iss": "https://fhir-server.example.com",
  "aud": "client-123",
  "sub": "patient-123",
  "exp": 1700000000,
  "iat": 1699996400,
  "nbf": 1699996400,
  "fhir_user": "Practitioner/prov-456",
  "patient": "Patient/patient-123",
  "encounter": "Encounter/enc-789",
  "scope": "patient/Patient.read patient/Observation.read"
}
```

### Token Verification
1. Check signature using public key
2. Validate expiration time
3. Verify issuer matches expected server
4. Check audience matches client_id
5. Validate requested scopes

## User Context

### Patient Context
```
GET /fhir/Patient?_id=patient-123
```
Access limited to specific patient based on launch context.

### Provider Context
```
GET /fhir/Patient?general-practitioner=Practitioner/prov-456
```
Access limited to patients assigned to provider.

### Encounter Context
```
GET /fhir/Observation?encounter=Encounter/enc-789
```
Access limited to observations in specific encounter.

## SMART Backend Services (System-to-System)

### JWT Bearer Flow
```
1. Backend service creates JWT:
   {
     "iss": "service-id",
     "sub": "service-id",
     "aud": "https://fhir-server/auth/token",
     "exp": 1700000000
   }
2. Signs with private key
3. Sends JWT to token endpoint
4. Receives access token
5. Uses token for API calls
```

### Use Cases
- Scheduled data exchanges
- Batch processing
- Analytics systems
- Population health tools

## Refresh Tokens

### Purpose
- Long-lived offline access
- Obtain new access token without user interaction
- Typical scope: "offline_access"

### Refresh Request
```
POST /auth/token
grant_type=refresh_token&
refresh_token=refresh-token-xyz&
client_id=client-123&
client_secret=secret-key
```

### Security Considerations
- Store securely (encrypted database)
- Implement rotation policies
- Handle revocation/expiration
- Monitor usage patterns

## SMART Security Best Practices

### For Developers
1. **Store secrets securely** - Never hardcode
2. **Validate tokens** - Always verify signature
3. **Use HTTPS** - Always in transit
4. **Implement PKCE** - For public apps
5. **Validate scopes** - Only request needed access
6. **Handle errors** - Proper error messages
7. **Session management** - Clear expired tokens

### For Servers
1. **Validate redirects** - Whitelist URIs
2. **Rate limiting** - Prevent brute force
3. **Token expiration** - Reasonable timeouts
4. **Scope enforcement** - Enforce requested scopes
5. **Audit logging** - Log all access
6. **Certificate pinning** - Prevent man-in-middle
7. **Monitor anomalies** - Detect abuse

## Error Handling

### Authorization Errors
```
error=invalid_scope
error=unauthorized_client
error=access_denied
error=unsupported_response_type
error=invalid_request
```

### Token Errors
```
error=invalid_request
error=invalid_client
error=invalid_grant
error=unauthorized_client
error=unsupported_grant_type
```

### FHIR API Errors
```
401 Unauthorized - Invalid or missing token
403 Forbidden - Insufficient scopes
404 Not Found - Resource not found
422 Unprocessable Entity - Validation error
```

## Common Use Cases

### Patient Portal
- Patient launches from EHR
- Reads own medical records
- Views recent results
- Manages appointments

### Mobile App
- Standalone launch
- Offline support with refresh token
- Sync with phone storage
- Privacy-focused design

### Clinical Decision Support
- Provider launched
- Reads patient data
- Analyzes and recommends
- Writes back recommendations

### Population Health
- System launch (no user)
- Reads aggregated data
- Generates reports
- No real-time interaction

## Compliance Considerations

- **HIPAA** - Encryption and audit logs
- **State laws** - Privacy requirements
- **NIST** - Security guidelines
- **OWASP** - Application security
- **GDPR** - European privacy law
