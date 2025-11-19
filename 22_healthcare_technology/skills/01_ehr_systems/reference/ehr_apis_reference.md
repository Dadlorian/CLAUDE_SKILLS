# EHR APIs Reference

## Overview

This reference documents the API architectures, endpoints, and integration patterns for major EHR vendors including Epic, Cerner, athenahealth, and standard FHIR implementations.

## Epic APIs

### Epic FHIR API

**Base URLs**:
```
Production: https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
Sandbox: https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
```

**Authentication Endpoint**:
```
https://fhir.epic.com/interconnect-fhir-oauth/oauth2/authorize
https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token
```

#### OAuth 2.0 Authorization Flow

**Step 1: Authorization Request**
```http
GET /interconnect-fhir-oauth/oauth2/authorize
Host: fhir.epic.com

Parameters:
response_type=code
client_id=your_client_id
redirect_uri=https://yourapp.example.com/callback
scope=patient/Patient.read patient/Observation.read launch/patient
state=random_state_string
aud=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
```

**Step 2: Token Exchange**
```http
POST /interconnect-fhir-oauth/oauth2/token
Host: fhir.epic.com
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTHORIZATION_CODE&
redirect_uri=https://yourapp.example.com/callback&
client_id=your_client_id&
client_secret=your_client_secret
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "patient/Patient.read patient/Observation.read",
  "patient": "eM8ExaPxLEY8z6j9QKI.Z.Q3",
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6..."
}
```

#### Supported Resources

**Patient Resources**:
```
GET /Patient/{id}
GET /Patient?identifier=MRN|12345
GET /Patient?name=Doe&birthdate=1980-01-15
GET /Patient?family=Doe&given=John
```

**Observations** (Labs, Vitals):
```
GET /Observation?patient={id}
GET /Observation?patient={id}&category=laboratory
GET /Observation?patient={id}&category=vital-signs
GET /Observation?patient={id}&code=http://loinc.org|2339-0
GET /Observation?patient={id}&date=ge2023-01-01&date=le2023-12-31
```

**Medications**:
```
GET /MedicationRequest?patient={id}
GET /MedicationRequest?patient={id}&status=active
GET /MedicationStatement?patient={id}
```

**Conditions/Problems**:
```
GET /Condition?patient={id}
GET /Condition?patient={id}&clinical-status=active
GET /Condition?patient={id}&category=problem-list-item
```

**Encounters**:
```
GET /Encounter?patient={id}
GET /Encounter?patient={id}&date=ge2023-01-01
GET /Encounter?patient={id}&status=in-progress
```

**Procedures**:
```
GET /Procedure?patient={id}
GET /Procedure?patient={id}&date=ge2023-01-01
```

**Immunizations**:
```
GET /Immunization?patient={id}
GET /Immunization?patient={id}&date=ge2020-01-01
```

**Allergies**:
```
GET /AllergyIntolerance?patient={id}
GET /AllergyIntolerance?patient={id}&clinical-status=active
```

**Diagnostic Reports**:
```
GET /DiagnosticReport?patient={id}
GET /DiagnosticReport?patient={id}&category=LAB
GET /DiagnosticReport?patient={id}&status=final
```

**Documents**:
```
GET /DocumentReference?patient={id}
GET /DocumentReference?patient={id}&type=http://loinc.org|34117-2
GET /Binary/{id}  // To retrieve actual document
```

#### Rate Limiting
- 1000 requests per hour (default)
- 429 Too Many Requests returned when exceeded
- Retry-After header indicates wait time

#### Epic-Specific Extensions

**Patient photo**:
```json
{
  "resourceType": "Patient",
  "id": "eM8ExaPxLEY8z6j9QKI.Z.Q3",
  "photo": [
    {
      "url": "Binary/patient-photo-123"
    }
  ]
}
```

**Practitioner availability**:
```json
{
  "resourceType": "PractitionerRole",
  "extension": [
    {
      "url": "http://fhir.epic.com/StructureDefinition/availability",
      "valueString": "Monday-Friday 9AM-5PM"
    }
  ]
}
```

### Epic MyChart API (Patient-Facing)

**Capabilities**:
- Patient demographics access
- Appointment viewing and scheduling
- Medication list
- Lab results
- Immunization records
- Secure messaging
- Health summary access

**SMART on FHIR Launch**:
```javascript
// Patient standalone launch
const authUrl = 'https://fhir.epic.com/interconnect-fhir-oauth/oauth2/authorize';
const params = {
  response_type: 'code',
  client_id: 'your_client_id',
  redirect_uri: 'https://yourapp.com/callback',
  scope: 'launch/patient patient/*.read offline_access',
  state: generateRandomState(),
  aud: 'https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4'
};
window.location.href = authUrl + '?' + new URLSearchParams(params);
```

## Cerner (Oracle Health) APIs

### Cerner FHIR API

**Base URLs**:
```
Production: https://fhir.cerner.com/r4/{tenant_id}
Sandbox: https://fhir-myrecord-sc.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d
```

**Authorization Endpoints**:
```
https://authorization.cerner.com/tenants/{tenant_id}/protocols/oauth2/profiles/smart-v1/personas/provider/authorize
https://authorization.cerner.com/tenants/{tenant_id}/protocols/oauth2/profiles/smart-v1/token
```

#### OAuth 2.0 Flow

**Authorization Request**:
```http
GET /tenants/{tenant_id}/protocols/oauth2/profiles/smart-v1/personas/provider/authorize
Host: authorization.cerner.com

Parameters:
response_type=code
client_id=your_client_id
redirect_uri=https://yourapp.com/callback
scope=patient/Patient.read patient/Observation.read launch
state=random_state
aud=https://fhir.cerner.com/r4/{tenant_id}
launch=launch_token
```

**Token Request**:
```http
POST /tenants/{tenant_id}/protocols/oauth2/profiles/smart-v1/token
Host: authorization.cerner.com
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTH_CODE&
redirect_uri=https://yourapp.com/callback&
client_id=your_client_id
```

#### Supported Resources

**Core Resources**:
```
Patient, Practitioner, Organization
Encounter, Location
Condition, Procedure
AllergyIntolerance, Immunization
MedicationRequest, MedicationAdministration
Observation, DiagnosticReport
DocumentReference, Binary
Appointment, Schedule, Slot
```

**Search Examples**:
```
GET /r4/{tenant}/Patient?_id=12345
GET /r4/{tenant}/Observation?patient=12345&category=laboratory
GET /r4/{tenant}/MedicationRequest?patient=12345&status=active
GET /r4/{tenant}/Condition?patient=12345
GET /r4/{tenant}/Appointment?patient=12345&date=ge2023-11-01
```

#### Cerner-Specific Features

**Proprietary Code System**:
```
http://fhir.cerner.com/ec2458f2-1e24-41c8-b71b-0e701af7583d/codeSet/72
```

**Custom Extensions**:
```json
{
  "extension": [
    {
      "url": "http://fhir.cerner.com/StructureDefinition/patient-friendly-display",
      "valueString": "High blood sugar"
    }
  ]
}
```

### Cerner Ignite APIs (Legacy)

**SOAP-based Web Services**:
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:cer="http://www.cerner.com/ignite">
  <soapenv:Header/>
  <soapenv:Body>
    <cer:GetPatient>
      <cer:patientId>12345</cer:patientId>
    </cer:GetPatient>
  </soapenv:Body>
</soapenv:Envelope>
```

## athenahealth API

**Base URL**:
```
https://api.platform.athenahealth.com/v1/{practiceid}
```

### Authentication

**OAuth 2.0 Client Credentials**:
```bash
curl -X POST https://api.platform.athenahealth.com/oauth2/v1/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_KEY&client_secret=YOUR_SECRET"
```

**Response**:
```json
{
  "access_token": "Bearer eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Core Endpoints

**Patients**:
```
GET /v1/{practiceid}/patients
GET /v1/{practiceid}/patients/{patientid}
POST /v1/{practiceid}/patients
PUT /v1/{practiceid}/patients/{patientid}

// Search patients
GET /v1/{practiceid}/patients?firstname=John&lastname=Doe&dob=01/15/1980
```

**Appointments**:
```
GET /v1/{practiceid}/appointments
GET /v1/{practiceid}/appointments/open
POST /v1/{practiceid}/appointments/{appointmentid}/book
DELETE /v1/{practiceid}/appointments/{appointmentid}

// Parameters
?departmentid=123
&startdate=11/01/2023
&enddate=11/30/2023
&providerid=456
```

**Clinical Documents**:
```
GET /v1/{practiceid}/patients/{patientid}/documents
GET /v1/{practiceid}/patients/{patientid}/documents/{documentid}
POST /v1/{practiceid}/patients/{patientid}/documents
```

**Medications**:
```
GET /v1/{practiceid}/patients/{patientid}/medications
POST /v1/{practiceid}/patients/{patientid}/medications
PUT /v1/{practiceid}/patients/{patientid}/medications/{medicationid}
```

**Lab Results**:
```
GET /v1/{practiceid}/patients/{patientid}/labresults
GET /v1/{practiceid}/patients/{patientid}/labresults/{resultid}
```

**Orders**:
```
GET /v1/{practiceid}/patients/{patientid}/orders
POST /v1/{practiceid}/patients/{patientid}/orders/lab
POST /v1/{practiceid}/patients/{patientid}/orders/imaging
```

**Encounters**:
```
GET /v1/{practiceid}/patients/{patientid}/encounters
GET /v1/{practiceid}/patients/{patientid}/encounters/{encounterid}
```

### athenahealth-Specific Features

**Pagination**:
```
GET /v1/{practiceid}/patients?limit=100&offset=0
```

**Response Headers**:
```
X-Total-Count: 1500
Link: <next_page_url>; rel="next"
```

## SMART on FHIR

### EHR Launch Sequence

**Step 1: EHR initiates launch**:
```
https://yourapp.com/launch?iss={fhir_url}&launch={launch_token}
```

**Step 2: App discovery**:
```
GET {iss}/.well-known/smart-configuration
```

**Response**:
```json
{
  "authorization_endpoint": "https://ehr.example.com/auth/authorize",
  "token_endpoint": "https://ehr.example.com/auth/token",
  "capabilities": [
    "launch-ehr",
    "client-public",
    "client-confidential-symmetric",
    "context-ehr-patient",
    "sso-openid-connect"
  ],
  "scopes_supported": [
    "patient/*.read",
    "user/*.read",
    "openid",
    "profile",
    "launch",
    "launch/patient"
  ]
}
```

**Step 3: Authorization request**:
```
GET /authorize?
  response_type=code&
  client_id=your_app&
  redirect_uri=https://yourapp.com/callback&
  scope=launch patient/Patient.read patient/Observation.read&
  state=random_state&
  aud=https://ehr.example.com/fhir&
  launch=launch_token_from_step_1
```

**Step 4: Token exchange**:
```
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTH_CODE&
redirect_uri=https://yourapp.com/callback&
client_id=your_app
```

**Response includes patient context**:
```json
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "launch patient/Patient.read patient/Observation.read",
  "patient": "123",
  "encounter": "456"
}
```

### Standalone Launch

**Patient-facing app**:
```javascript
// Discover SMART configuration
const response = await fetch('https://fhir.example.com/.well-known/smart-configuration');
const config = await response.json();

// Redirect to authorization
const params = {
  response_type: 'code',
  client_id: 'your_client_id',
  redirect_uri: 'https://yourapp.com/callback',
  scope: 'launch/patient patient/*.read offline_access',
  state: generateState(),
  aud: 'https://fhir.example.com'
};
window.location.href = config.authorization_endpoint + '?' + new URLSearchParams(params);
```

## Common API Patterns

### Searching with Parameters

**Date Ranges**:
```
GET /Observation?date=ge2023-01-01&date=le2023-12-31
GET /Encounter?date=ge2023-11-01
```

**Token Search**:
```
GET /Observation?code=http://loinc.org|2339-0
GET /Condition?code=http://snomed.info/sct|73211009
```

**Reference Parameters**:
```
GET /Observation?patient=Patient/123
GET /MedicationRequest?patient=Patient/123&requester=Practitioner/456
```

**Chaining**:
```
GET /DiagnosticReport?subject:Patient.name=Doe
GET /Observation?subject:Patient.identifier=MRN|12345
```

**Reverse Chaining**:
```
GET /Patient?_has:Observation:patient:code=http://loinc.org|2339-0
```

**Include and RevInclude**:
```
GET /MedicationRequest?patient=123&_include=MedicationRequest:medication
GET /Patient?_id=123&_revinclude=Observation:patient
```

### Pagination

**FHIR Bundle with pagination**:
```json
{
  "resourceType": "Bundle",
  "type": "searchset",
  "total": 500,
  "link": [
    {
      "relation": "self",
      "url": "https://fhir.example.com/Observation?patient=123"
    },
    {
      "relation": "next",
      "url": "https://fhir.example.com/Observation?patient=123&page=2"
    }
  ],
  "entry": [...]
}
```

**Using _count parameter**:
```
GET /Observation?patient=123&_count=50
```

### Error Handling

**HTTP Status Codes**:
```
200 OK - Successful GET, PUT
201 Created - Successful POST
204 No Content - Successful DELETE
400 Bad Request - Invalid parameters
401 Unauthorized - Missing/invalid authentication
403 Forbidden - Insufficient permissions
404 Not Found - Resource doesn't exist
429 Too Many Requests - Rate limit exceeded
500 Internal Server Error - Server error
503 Service Unavailable - Temporary outage
```

**OperationOutcome Resource**:
```json
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error",
      "code": "invalid",
      "diagnostics": "Invalid patient identifier",
      "location": ["Patient.identifier"]
    }
  ]
}
```

### Batch and Transaction Operations

**Batch Bundle**:
```json
{
  "resourceType": "Bundle",
  "type": "batch",
  "entry": [
    {
      "request": {
        "method": "GET",
        "url": "Patient/123"
      }
    },
    {
      "request": {
        "method": "GET",
        "url": "Observation?patient=123"
      }
    }
  ]
}
```

**Transaction Bundle**:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "fullUrl": "urn:uuid:patient-temp-id",
      "resource": {
        "resourceType": "Patient",
        "name": [{"family": "Doe", "given": ["John"]}]
      },
      "request": {
        "method": "POST",
        "url": "Patient"
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "subject": {"reference": "urn:uuid:patient-temp-id"},
        "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6"}]},
        "valueQuantity": {"value": 120, "unit": "mmHg"}
      },
      "request": {
        "method": "POST",
        "url": "Observation"
      }
    }
  ]
}
```

## Security Best Practices

### 1. OAuth Token Management
```javascript
// Store tokens securely
const secureStorage = {
  setToken: (token) => {
    // Use encrypted storage, not localStorage
    sessionStorage.setItem('access_token', encrypt(token));
  },
  getToken: () => {
    const encrypted = sessionStorage.getItem('access_token');
    return encrypted ? decrypt(encrypted) : null;
  }
};

// Refresh token before expiration
const refreshToken = async () => {
  const response = await fetch(tokenEndpoint, {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: storedRefreshToken,
      client_id: clientId
    })
  });
  const data = await response.json();
  secureStorage.setToken(data.access_token);
};
```

### 2. Request Authentication
```javascript
// Always include Bearer token
const headers = {
  'Authorization': `Bearer ${accessToken}`,
  'Accept': 'application/fhir+json',
  'Content-Type': 'application/fhir+json'
};

// Make authenticated request
const response = await fetch('https://fhir.example.com/Patient/123', {
  headers: headers
});
```

### 3. Scope Limiting
```javascript
// Request only necessary scopes
const scopes = [
  'patient/Patient.read',
  'patient/Observation.read',
  'patient/MedicationRequest.read'
].join(' ');

// Not: 'patient/*.*' (too broad)
```

### 4. CORS and CSP Headers
```javascript
// Server-side CORS configuration
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', 'https://trustedapp.com');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
  res.header('Access-Control-Allow-Headers', 'Authorization, Content-Type');
  next();
});

// Content Security Policy
res.header('Content-Security-Policy', "default-src 'self'; connect-src https://fhir.example.com");
```

## Rate Limiting and Performance

### Rate Limit Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1637339400
Retry-After: 60
```

### Handling Rate Limits
```javascript
const makeRequest = async (url, options, retries = 3) => {
  try {
    const response = await fetch(url, options);

    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After') || 60;
      await sleep(retryAfter * 1000);
      return makeRequest(url, options, retries - 1);
    }

    return response;
  } catch (error) {
    if (retries > 0) {
      await sleep(1000);
      return makeRequest(url, options, retries - 1);
    }
    throw error;
  }
};
```

### Caching Strategies
```javascript
// Cache static reference data
const cache = new Map();

const getCachedResource = async (resourceType, id) => {
  const cacheKey = `${resourceType}/${id}`;

  if (cache.has(cacheKey)) {
    return cache.get(cacheKey);
  }

  const resource = await fetchResource(resourceType, id);
  cache.set(cacheKey, resource);

  // Expire after 1 hour
  setTimeout(() => cache.delete(cacheKey), 3600000);

  return resource;
};
```

## Testing and Development

### Sandbox Environments

**Epic Sandbox**:
```
Base URL: https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
Test Patients: Available in Epic documentation
No authentication required for certain read operations
```

**Cerner Sandbox**:
```
Base URL: https://fhir-myrecord-sc.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d
Test Patient ID: 12724066
Public access, no authentication required
```

**HAPI FHIR Test Server**:
```
Base URL: http://hapi.fhir.org/baseR4
Public test server
No authentication
```

### Testing Tools

**Postman Collections**:
- Epic FHIR Postman Collection
- Cerner FHIR Postman Collection
- SMART on FHIR testing

**Command Line (curl)**:
```bash
# Get patient
curl -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/fhir+json" \
  https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Patient/eM8ExaPxLEY8z6j9QKI.Z.Q3

# Search observations
curl -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/fhir+json" \
  "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Observation?patient=eM8ExaPxLEY8z6j9QKI.Z.Q3&category=laboratory"
```

## References

- **Epic FHIR Documentation**: https://fhir.epic.com/
- **Cerner FHIR Documentation**: https://fhir.cerner.com/
- **athenahealth API Documentation**: https://docs.athenahealth.com/
- **SMART on FHIR**: https://smarthealthit.org/
- **FHIR Specification**: http://hl7.org/fhir/

---

**Document Version**: 1.0
**Last Updated**: November 2024
**Author**: Healthcare Technology Team
**Classification**: Public - Educational Use
