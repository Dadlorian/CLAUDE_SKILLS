# FHIR API Integration Guide

## Overview

This comprehensive guide covers FHIR (Fast Healthcare Interoperability Resources) R4 API integration, including authentication, resource access patterns, and production deployment strategies.

## Part 1: FHIR API Fundamentals

### Understanding FHIR

**Key Concepts**:
```
Resources:
├── Base unit of interoperability
├── Structured data in JSON or XML
├── Self-contained with references
└── Examples: Patient, Observation, Medication Request

RESTful Operations:
├── Create (POST)
├── Read (GET)
├── Update (PUT/PATCH)
├── Delete (DELETE)
└── Search (GET with parameters)

Resource Identity:
├── Logical ID: Resource unique identifier
├── Version ID: Specific version of resource
└── Full URL: Complete resource location
```

### FHIR R4 Architecture

```
FHIR API Structure:
[Base URL]/[Resource Type]/[ID]
```

**Example**:
```
https://fhir.example.com/r4/Patient/12345
https://fhir.example.com/r4/Observation?patient=12345&category=laboratory
```

## Part 2: Authentication and Authorization

### OAuth 2.0 / SMART on FHIR Implementation

**Step 1: Discover FHIR Server Capabilities**

```javascript
// Discover SMART configuration
async function discoverSmartConfig(fhirBaseUrl) {
  const response = await fetch(
    `${fhirBaseUrl}/.well-known/smart-configuration`
  );
  
  const config = await response.json();
  
  /*
  Expected response:
  {
    "authorization_endpoint": "https://fhir.example.com/auth/authorize",
    "token_endpoint": "https://fhir.example.com/auth/token",
    "capabilities": [
      "launch-ehr",
      "client-public",
      "client-confidential-symmetric",
      "sso-openid-connect"
    ],
    "scopes_supported": [
      "patient/*.read",
      "user/*.read",
      "launch",
      "offline_access"
    ]
  }
  */
  
  return config;
}
```

**Step 2: Authorization Request**

```javascript
// Standalone patient launch
async function authorizePatientAccess(smartConfig, clientId, redirectUri) {
  const state = crypto.randomUUID();
  sessionStorage.setItem('oauth_state', state);
  
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: clientId,
    redirect_uri: redirectUri,
    scope: 'launch/patient patient/*.read offline_access',
    state: state,
    aud: smartConfig.fhirBaseUrl
  });
  
  // Redirect to authorization endpoint
  window.location.href = `${smartConfig.authorization_endpoint}?${params}`;
}

// EHR launch (provider-facing app)
async function handleEhrLaunch(launchToken, iss) {
  // Received from EHR: ?launch={token}&iss={fhir_url}
  const smartConfig = await discoverSmartConfig(iss);
  
  const state = crypto.randomUUID();
  sessionStorage.setItem('oauth_state', state);
  sessionStorage.setItem('iss', iss);
  
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: 'your_client_id',
    redirect_uri: 'https://yourapp.com/callback',
    scope: 'launch user/Patient.read user/Observation.read',
    state: state,
    aud: iss,
    launch: launchToken  // Include launch token from EHR
  });
  
  window.location.href = `${smartConfig.authorization_endpoint}?${params}`;
}
```

**Step 3: Token Exchange**

```javascript
async function exchangeCodeForToken(code, redirectUri, smartConfig) {
  const response = await fetch(smartConfig.token_endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      code: code,
      redirect_uri: redirectUri,
      client_id: 'your_client_id',
      // Include client_secret for confidential clients
      client_secret: 'your_client_secret'
    })
  });
  
  if (!response.ok) {
    throw new Error(`Token exchange failed: ${response.statusText}`);
  }
  
  const tokenData = await response.json();
  
  /*
  Response:
  {
    "access_token": "eyJhbGc...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": "patient/Patient.read patient/Observation.read",
    "patient": "12345",  // Patient in context
    "encounter": "67890",  // Encounter in context (if applicable)
    "refresh_token": "eyJhbGc..."  // If offline_access requested
  }
  */
  
  // Store tokens securely
  await securelyStoreTokens(tokenData);
  
  return tokenData;
}

async function securelyStoreTokens(tokenData) {
  // Use secure storage (encrypted, HTTP-only cookies, or secure backend)
  // NOT localStorage or sessionStorage for production
  
  // Example using sessionStorage (for demo only):
  sessionStorage.setItem('access_token', tokenData.access_token);
  sessionStorage.setItem('refresh_token', tokenData.refresh_token);
  sessionStorage.setItem('patient_id', tokenData.patient);
  sessionStorage.setItem('token_expiry', Date.now() + (tokenData.expires_in * 1000));
}
```

**Step 4: Token Refresh**

```javascript
async function refreshAccessToken(smartConfig) {
  const refreshToken = sessionStorage.getItem('refresh_token');
  
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }
  
  const response = await fetch(smartConfig.token_endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
      client_id: 'your_client_id',
      client_secret: 'your_client_secret'
    })
  });
  
  const tokenData = await response.json();
  
  // Update stored tokens
  sessionStorage.setItem('access_token', tokenData.access_token);
  sessionStorage.setItem('token_expiry', Date.now() + (tokenData.expires_in * 1000));
  
  return tokenData.access_token;
}
```

## Part 3: FHIR Resource Operations

### Creating a FHIR Client

```javascript
class FHIRClient {
  constructor(baseUrl, smartConfig) {
    this.baseUrl = baseUrl;
    this.smartConfig = smartConfig;
  }
  
  async getAccessToken() {
    const token = sessionStorage.getItem('access_token');
    const expiry = sessionStorage.getItem('token_expiry');
    
    // Refresh if expired or expiring soon (5 min buffer)
    if (Date.now() >= (parseInt(expiry) - 300000)) {
      return await refreshAccessToken(this.smartConfig);
    }
    
    return token;
  }
  
  async request(url, options = {}) {
    const token = await this.getAccessToken();
    
    const defaultHeaders = {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/fhir+json',
      'Content-Type': 'application/fhir+json'
    };
    
    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new FHIRError(error);
    }
    
    return await response.json();
  }
  
  // READ operation
  async read(resourceType, id) {
    const url = `${this.baseUrl}/${resourceType}/${id}`;
    return await this.request(url);
  }
  
  // SEARCH operation
  async search(resourceType, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = `${this.baseUrl}/${resourceType}?${queryString}`;
    return await this.request(url);
  }
  
  // CREATE operation
  async create(resource) {
    const url = `${this.baseUrl}/${resource.resourceType}`;
    return await this.request(url, {
      method: 'POST',
      body: JSON.stringify(resource)
    });
  }
  
  // UPDATE operation
  async update(resource) {
    const url = `${this.baseUrl}/${resource.resourceType}/${resource.id}`;
    return await this.request(url, {
      method: 'PUT',
      body: JSON.stringify(resource)
    });
  }
  
  // DELETE operation (if supported)
  async delete(resourceType, id) {
    const url = `${this.baseUrl}/${resourceType}/${id}`;
    return await this.request(url, {
      method: 'DELETE'
    });
  }
  
  // Handle pagination
  async *searchPaginated(resourceType, params = {}, pageSize = 50) {
    params._count = pageSize;
    let bundle = await this.search(resourceType, params);
    
    while (bundle) {
      if (bundle.entry) {
        for (const entry of bundle.entry) {
          yield entry.resource;
        }
      }
      
      // Get next page
      const nextLink = bundle.link?.find(l => l.relation === 'next');
      if (nextLink) {
        bundle = await this.request(nextLink.url);
      } else {
        bundle = null;
      }
    }
  }
}

class FHIRError extends Error {
  constructor(operationOutcome) {
    const message = operationOutcome.issue?.[0]?.diagnostics || 'FHIR request failed';
    super(message);
    this.name = 'FHIRError';
    this.operationOutcome = operationOutcome;
  }
}
```

### Common Resource Patterns

**Patient Demographics**:
```javascript
async function getPatientDemographics(client, patientId) {
  const patient = await client.read('Patient', patientId);
  
  return {
    id: patient.id,
    name: patient.name?.[0] ? {
      family: patient.name[0].family,
      given: patient.name[0].given?.join(' '),
      full: `${patient.name[0].given?.join(' ')} ${patient.name[0].family}`
    } : null,
    birthDate: patient.birthDate,
    gender: patient.gender,
    phone: patient.telecom?.find(t => t.system === 'phone')?.value,
    email: patient.telecom?.find(t => t.system === 'email')?.value,
    address: patient.address?.[0] ? {
      line: patient.address[0].line?.join(', '),
      city: patient.address[0].city,
      state: patient.address[0].state,
      postalCode: patient.address[0].postalCode
    } : null
  };
}
```

**Lab Results (Observations)**:
```javascript
async function getLabResults(client, patientId, startDate, endDate) {
  const params = {
    patient: patientId,
    category: 'laboratory',
    _sort: '-date',
    _count: 100
  };
  
  if (startDate) {
    params.date = `ge${startDate}`;
  }
  if (endDate) {
    params.date = (params.date || '') + (params.date ? ',' : '') + `le${endDate}`;
  }
  
  const observations = [];
  for await (const obs of client.searchPaginated('Observation', params)) {
    observations.push({
      id: obs.id,
      date: obs.effectiveDateTime || obs.effectivePeriod?.start,
      code: {
        code: obs.code.coding?.[0]?.code,
        display: obs.code.coding?.[0]?.display || obs.code.text
      },
      value: extractObservationValue(obs),
      unit: obs.valueQuantity?.unit,
      referenceRange: obs.referenceRange?.[0] ? {
        low: obs.referenceRange[0].low?.value,
        high: obs.referenceRange[0].high?.value,
        text: obs.referenceRange[0].text
      } : null,
      interpretation: obs.interpretation?.[0]?.coding?.[0]?.code,
      status: obs.status
    });
  }
  
  return observations;
}

function extractObservationValue(obs) {
  if (obs.valueQuantity) {
    return obs.valueQuantity.value;
  } else if (obs.valueString) {
    return obs.valueString;
  } else if (obs.valueCodeableConcept) {
    return obs.valueCodeableConcept.coding?.[0]?.display || obs.valueCodeableConcept.text;
  } else if (obs.component) {
    // Handle component observations (e.g., blood pressure)
    return obs.component.map(c => ({
      code: c.code.coding?.[0]?.display,
      value: c.valueQuantity?.value,
      unit: c.valueQuantity?.unit
    }));
  }
  return null;
}
```

**Medications**:
```javascript
async function getCurrentMedications(client, patientId) {
  const params = {
    patient: patientId,
    status: 'active',
    _sort: '-_lastUpdated'
  };
  
  const medications = [];
  for await (const medReq of client.searchPaginated('MedicationRequest', params)) {
    medications.push({
      id: medReq.id,
      medication: medReq.medicationCodeableConcept?.coding?.[0]?.display ||
                  medReq.medicationCodeableConcept?.text,
      dosage: medReq.dosageInstruction?.[0]?.text,
      status: medReq.status,
      authoredOn: medReq.authoredOn,
      prescriber: medReq.requester?.display
    });
  }
  
  return medications;
}
```

**Conditions/Problems**:
```javascript
async function getActiveConditions(client, patientId) {
  const params = {
    patient: patientId,
    'clinical-status': 'active',
    _sort: '-onset-date'
  };
  
  const conditions = [];
  for await (const condition of client.searchPaginated('Condition', params)) {
    conditions.push({
      id: condition.id,
      code: {
        code: condition.code.coding?.[0]?.code,
        display: condition.code.coding?.[0]?.display || condition.code.text
      },
      clinicalStatus: condition.clinicalStatus?.coding?.[0]?.code,
      verificationStatus: condition.verificationStatus?.coding?.[0]?.code,
      severity: condition.severity?.coding?.[0]?.display,
      onsetDate: condition.onsetDateTime || condition.onsetPeriod?.start,
      recordedDate: condition.recordedDate
    });
  }
  
  return conditions;
}
```

## Part 4: Advanced Features

### Batch/Transaction Operations

```javascript
async function createObservationBatch(client, observations) {
  const bundle = {
    resourceType: 'Bundle',
    type: 'transaction',
    entry: observations.map(obs => ({
      resource: obs,
      request: {
        method: 'POST',
        url: 'Observation'
      }
    }))
  };
  
  const result = await client.request(`${client.baseUrl}`, {
    method: 'POST',
    body: JSON.stringify(bundle)
  });
  
  return result;
}
```

### Search with _include and _revinclude

```javascript
// Get patient with all their observations
async function getPatientWithObservations(client, patientId) {
  const params = {
    _id: patientId,
    _revinclude: 'Observation:patient'
  };
  
  const bundle = await client.search('Patient', params);
  
  const patient = bundle.entry.find(e => e.resource.resourceType === 'Patient')?.resource;
  const observations = bundle.entry
    .filter(e => e.resource.resourceType === 'Observation')
    .map(e => e.resource);
  
  return { patient, observations };
}
```

### Conditional Create/Update

```javascript
// Upsert patient (create if doesn't exist, update if exists)
async function upsertPatient(client, patient, identifier) {
  const url = `${client.baseUrl}/Patient?identifier=${identifier}`;
  
  const response = await client.request(url, {
    method: 'PUT',
    body: JSON.stringify(patient)
  });
  
  return response;
}
```

## Part 5: Error Handling and Resilience

### Comprehensive Error Handling

```javascript
class ResilientFHIRClient extends FHIRClient {
  constructor(baseUrl, smartConfig, options = {}) {
    super(baseUrl, smartConfig);
    this.maxRetries = options.maxRetries || 3;
    this.retryDelay = options.retryDelay || 1000;
  }
  
  async request(url, options = {}, attempt = 1) {
    try {
      return await super.request(url, options);
    } catch (error) {
      // Handle rate limiting (429)
      if (error.operationOutcome?.issue?.[0]?.code === 'throttled') {
        const retryAfter = error.headers?.get('Retry-After') || 60;
        console.log(`Rate limited. Waiting ${retryAfter}s before retry`);
        await this.sleep(retryAfter * 1000);
        return this.request(url, options, attempt);
      }
      
      // Retry on server errors (5xx)
      if (error.operationOutcome?.issue?.[0]?.code >= 500 && attempt <= this.maxRetries) {
        const delay = this.retryDelay * Math.pow(2, attempt - 1); // Exponential backoff
        console.log(`Server error. Retrying in ${delay}ms (attempt ${attempt}/${this.maxRetries})`);
        await this.sleep(delay);
        return this.request(url, options, attempt + 1);
      }
      
      throw error;
    }
  }
  
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

### Validation

```javascript
function validateFHIRResource(resource) {
  if (!resource.resourceType) {
    throw new Error('Missing resourceType');
  }
  
  // Validate against FHIR profiles
  // Use library like fhir.js or validate.js
  
  return true;
}
```

## Part 6: Testing

### Unit Tests

```javascript
// test/fhir-client.test.js
const { expect } = require('chai');

describe('FHIR Client', () => {
  let client;
  
  beforeEach(() => {
    client = new FHIRClient(
      'https://fhir.example.com/r4',
      mockSmartConfig
    );
  });
  
  it('should read patient resource', async () => {
    const patient = await client.read('Patient', '12345');
    expect(patient.resourceType).to.equal('Patient');
    expect(patient.id).to.equal('12345');
  });
  
  it('should search observations', async () => {
    const bundle = await client.search('Observation', {
      patient: '12345',
      category: 'laboratory'
    });
    
    expect(bundle.resourceType).to.equal('Bundle');
    expect(bundle.entry).to.be.an('array');
  });
  
  it('should handle pagination', async () => {
    const observations = [];
    for await (const obs of client.searchPaginated('Observation', {patient: '12345'})) {
      observations.push(obs);
    }
    
    expect(observations.length).to.be.greaterThan(0);
  });
});
```

## Part 7: Production Deployment

### Configuration Management

```javascript
// config/production.js
module.exports = {
  fhir: {
    baseUrl: process.env.FHIR_BASE_URL,
    clientId: process.env.FHIR_CLIENT_ID,
    clientSecret: process.env.FHIR_CLIENT_SECRET,
    redirectUri: process.env.FHIR_REDIRECT_URI,
    scopes: process.env.FHIR_SCOPES || 'patient/*.read',
    timeout: 30000,
    maxRetries: 3
  },
  security: {
    tokenEncryptionKey: process.env.TOKEN_ENCRYPTION_KEY,
    sessionSecret: process.env.SESSION_SECRET
  }
};
```

### Monitoring and Logging

```javascript
class MonitoredFHIRClient extends ResilientFHIRClient {
  async request(url, options = {}) {
    const startTime = Date.now();
    const requestId = crypto.randomUUID();
    
    try {
      console.log(`[${requestId}] FHIR Request: ${options.method || 'GET'} ${url}`);
      
      const result = await super.request(url, options);
      
      const duration = Date.now() - startTime;
      console.log(`[${requestId}] FHIR Success: ${duration}ms`);
      
      // Send metrics to monitoring service
      this.recordMetric('fhir.request.success', duration, {
        endpoint: url,
        method: options.method || 'GET'
      });
      
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      console.error(`[${requestId}] FHIR Error: ${error.message}`, {
        url,
        duration,
        error: error.operationOutcome
      });
      
      // Send error metrics
      this.recordMetric('fhir.request.error', duration, {
        endpoint: url,
        error: error.message
      });
      
      throw error;
    }
  }
  
  recordMetric(name, value, tags = {}) {
    // Integration with monitoring service (DataDog, New Relic, etc.)
  }
}
```

## Troubleshooting

### Common Issues

```
1. OAuth Token Expired
   - Symptom: 401 Unauthorized
   - Solution: Implement token refresh logic

2. Invalid Scope
   - Symptom: 403 Forbidden
   - Solution: Request necessary scopes during authorization

3. Rate Limiting
   - Symptom: 429 Too Many Requests
   - Solution: Implement exponential backoff, reduce request frequency

4. Resource Not Found
   - Symptom: 404 Not Found
   - Solution: Verify resource ID, check patient context

5. Invalid Resource
   - Symptom: 400 Bad Request with OperationOutcome
   - Solution: Validate resource structure before submission
```

## References

- FHIR R4 Specification: http://hl7.org/fhir/R4/
- SMART App Launch: http://www.hl7.org/fhir/smart-app-launch/
- US Core Implementation Guide: http://hl7.org/fhir/us/core/

---

**Document Version**: 1.0
**Last Updated**: November 2024
**Classification**: Production Guide
