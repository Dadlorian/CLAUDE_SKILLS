# Epic Integration Guide

## Overview

This step-by-step guide covers integration with Epic Systems EHR, including HL7 interfaces, FHIR API integration, and best practices for production deployments.

## Prerequisites

Before beginning Epic integration:

```
Required Access:
├── Epic Interconnect license
├── Epic UserWeb account
├── Access to Epic test environment
├── Network connectivity to Epic servers
└── SSL certificates for secure communication

Required Knowledge:
├── HL7 messaging standards
├── FHIR R4 specification
├── OAuth 2.0 / SMART on FHIR
├── Healthcare workflows
└── HIPAA compliance requirements

Required Tools:
├── HL7 interface engine (Mirth Connect, Rhapsody, etc.)
├── Development environment
├── Testing tools (HL7 Inspector, Postman)
└── SSL/TLS certificates
```

## Part 1: HL7 Interface Integration with Epic Interconnect

### Step 1: Interface Planning and Design

**1.1 Define Integration Scope**
```
Questions to Answer:
├── What data needs to be exchanged?
│   ├── ADT (Patient demographics/movements)
│   ├── ORM (Orders)
│   ├── ORU (Results)
│   ├── SIU (Scheduling)
│   └── DFT (Charges)
├── What is the message flow direction?
│   ├── Inbound to Epic
│   ├── Outbound from Epic
│   └── Bidirectional
├── What is the frequency?
│   ├── Real-time
│   ├── Batch (scheduled)
│   └── Event-driven
└── What are the dependencies?
    ├── Master Patient Index (MPI) synchronization
    ├── Provider directory alignment
    └── Code set mapping
```

**1.2 Create Interface Specification Document**
```markdown
# Interface Specification: Lab Results (ORU)

## Overview
- **Source System**: Lab System XYZ
- **Destination System**: Epic
- **Message Type**: HL7 2.5.1 ORU^R01
- **Direction**: Inbound to Epic
- **Frequency**: Real-time (as results finalize)
- **Volume**: ~500 messages/day

## Message Structure
MSH|^~\&|LAB_SYSTEM|LAB_FAC|EPIC|EPIC_FAC|TIMESTAMP||ORU^R01|MSG_ID|P|2.5.1
PID|1||MRN^^^EPIC^MRN~SSN^^^SSN||LAST^FIRST^MIDDLE||DOB|GENDER
OBR|1||ACCESSION_NUMBER|TEST_CODE^TEST_NAME^LOINC
OBX|1|NM|LOINC_CODE^TEST_NAME||RESULT_VALUE|UNITS|REFERENCE_RANGE|FLAG

## Data Mapping
- Patient Identifier: MRN from Lab → Epic MRN (validated against PATIENT table)
- Test Code: Lab internal code → LOINC code
- Result Value: Numeric or text based on test
- Abnormal Flag: L (Low), H (High), Critical

## Error Handling
- Invalid MRN: Reject with AE acknowledgment
- Missing required fields: Reject with AR acknowledgment
- Test code not found: Log error, create pending order
```

### Step 2: Epic Interface Configuration

**2.1 Access Epic Interconnect**

Log into Epic via UserWeb and navigate to:
```
Interconnect > Interface Master File (ITF)
```

**2.2 Create New Interface Record**

```
Interface Type: HL7 Socket
Protocol: TCP/IP
Port: Assign available port (e.g., 6001)
IP Address: [Your system's IP]

Message Types Supported:
☑ ORU^R01 (Results)

Receiving Application: LAB_SYSTEM
Receiving Facility: LAB_FAC
```

**2.3 Configure Message Processing Rules**

```
Epic Interconnect Configuration:
├── Interface Activation
│   ├── Set active date/time
│   ├── Enable/disable interface
│   └── Maintenance window
├── Message Validation
│   ├── Required segments (MSH, PID, OBR, OBX)
│   ├── Field validation rules
│   └── Code set validation
├── Patient Matching
│   ├── Match algorithm (MRN, SSN, Name+DOB)
│   ├── Confidence threshold
│   └── Manual review queue
├── Order Matching
│   ├── Match on accession number
│   ├── Match on order ID
│   └── Auto-create order if not found
└── Error Handling
    ├── Send NACK for errors
    ├── Error bucket routing
    └── Alert notification
```

**2.4 Define Field Mappings**

```
Epic Chronicle Field ← HL7 Segment/Field
────────────────────────────────────────
Patient MRN ← PID-3.1 (where PID-3.5 = "MRN")
Patient Name ← PID-5
Date of Birth ← PID-7
Gender ← PID-8
Result Value ← OBX-5
Result Units ← OBX-6
Reference Range ← OBX-7
Abnormal Flag ← OBX-8
Result Date/Time ← OBR-7
```

### Step 3: Interface Engine Configuration (Mirth Connect Example)

**3.1 Install and Configure Mirth Connect**

```bash
# Download Mirth Connect
wget https://s3.amazonaws.com/downloads.mirthcorp.com/connect/3.12.0.b2945/mirthconnect-3.12.0.b2945-unix.tar.gz

# Extract and start
tar -xzf mirthconnect-3.12.0.b2945-unix.tar.gz
cd Mirth\ Connect
./mcserver start

# Access web admin at http://localhost:8080
```

**3.2 Create Mirth Channel for ORU Messages**

```xml
<!-- Mirth Channel Configuration -->
<channel version="3.12.0">
  <name>Lab Results to Epic (ORU)</name>
  <description>Send lab results to Epic via HL7 ORU^R01</description>

  <sourceConnector>
    <name>Lab System File Listener</name>
    <type>File Reader</type>
    <properties>
      <directory>/data/lab/outbound</directory>
      <filePattern>ORU_*.hl7</filePattern>
      <polling>1000</polling> <!-- 1 second -->
      <archive>true</archive>
      <errorDirectory>/data/lab/errors</errorDirectory>
    </properties>
  </sourceConnector>

  <transformer>
    <steps>
      <!-- Step 1: Parse HL7 -->
      <step>
        <name>Parse HL7</name>
        <type>JavaScript</type>
        <script>
          <![CDATA[
            // Access HL7 segments
            var msh = msg['MSH'];
            var pid = msg['PID'];
            var obr = msg['OBR'][0]; // First order
            var obx = msg['OBX']; // Array of results

            // Validate required fields
            if (!pid['PID.3']['PID.3.1']) {
              throw new Error('Missing patient MRN');
            }

            // Continue processing
            return msg;
          ]]>
        </script>
      </step>

      <!-- Step 2: Lookup Patient in Epic -->
      <step>
        <name>Validate MRN</name>
        <type>Database Query</type>
        <query>
          SELECT PATIENT_ID
          FROM EPIC_PATIENT
          WHERE MRN = '${pid['PID.3']['PID.3.1']}'
        </query>
      </step>

      <!-- Step 3: Map to Epic Format -->
      <step>
        <name>Map Fields</name>
        <type>Mapper</type>
        <mappings>
          <mapping>
            <target>MSH-3</target>
            <source>LAB_SYSTEM</source>
          </mapping>
          <mapping>
            <target>MSH-5</target>
            <source>EPIC</source>
          </mapping>
        </mappings>
      </step>
    </steps>
  </transformer>

  <destinationConnector>
    <name>Epic Interconnect</name>
    <type>TCP Sender</type>
    <properties>
      <host>epic-interconnect.hospital.org</host>
      <port>6001</port>
      <protocol>MLLP</protocol>
      <timeout>30000</timeout>
      <persistentConnection>true</persistentConnection>
      <processAck>true</processAck>
    </properties>
  </destinationConnector>
</channel>
```

### Step 4: Testing and Validation

**4.1 Unit Testing**

```javascript
// Test case 1: Valid ORU message
const testMessage1 = `MSH|^~\\&|LAB_SYSTEM|LAB_FAC|EPIC|EPIC_FAC|20231119120000||ORU^R01|MSG001|P|2.5.1
PID|1||MRN123456^^^EPIC^MRN||DOE^JOHN^M||19800115|M
OBR|1||ACC123456|GLUCOSE^Glucose^LN|||20231119100000
OBX|1|NM|2339-0^Glucose^LN||95|mg/dL|70-100|N|||F`;

// Expected outcome: ACK with AA (Application Accept)

// Test case 2: Invalid MRN
const testMessage2 = `MSH|^~\\&|LAB_SYSTEM|LAB_FAC|EPIC|EPIC_FAC|20231119120000||ORU^R01|MSG002|P|2.5.1
PID|1||INVALID_MRN^^^EPIC^MRN||DOE^JOHN^M||19800115|M
OBR|1||ACC123456|GLUCOSE^Glucose^LN|||20231119100000
OBX|1|NM|2339-0^Glucose^LN||95|mg/dL|70-100|N|||F`;

// Expected outcome: ACK with AE (Application Error)
```

**4.2 Integration Testing**

```
Test Scenarios:
├── Happy path (valid message, patient exists, order exists)
├── Patient not found (invalid MRN)
├── Order not found (auto-create vs. reject)
├── Duplicate message handling
├── Out-of-order message handling
├── Special characters in results
├── Multiple OBX segments
├── Corrected results (OBR-25 = 'F' → 'C')
└── Cancelled results (OBR-25 = 'X')

Validation Points:
├── Message arrives at Epic (check Interconnect logs)
├── Patient matched correctly
├── Results appear in Epic Beaker
├── Abnormal flags display correctly
├── Provider receives notification (if critical)
└── Interface runs without errors for 24 hours
```

### Step 5: Production Deployment

**5.1 Pre-Deployment Checklist**

```
☐ All test scenarios passed
☐ Epic sign-off received
☐ Network firewall rules configured
☐ SSL certificates installed
☐ Monitoring alerts configured
☐ Error notification distribution list created
☐ Runbook documentation completed
☐ Rollback plan documented
☐ Support team trained
☐ Go-live date/time scheduled
```

**5.2 Deployment Steps**

```bash
# Step 1: Backup current configuration
./backup_mirth_config.sh

# Step 2: Deploy Mirth channel to production
# (Export from test, import to production)

# Step 3: Update Epic interface to production settings
# In Epic Interconnect:
# - Change IP address to production server
# - Enable interface
# - Set activation date

# Step 4: Start interface
./start_interface.sh

# Step 5: Send test message
./send_test_oru.sh

# Step 6: Monitor for 1 hour
tail -f /var/log/mirth/mirth.log

# Step 7: Verify messages in Epic
# Check Epic Interconnect > Interface Activity
```

**5.3 Post-Deployment Monitoring**

```
Monitoring Metrics:
├── Message volume (expected vs. actual)
├── Error rate (< 1% target)
├── Average processing time (< 5 seconds target)
├── Epic Interconnect queue depth
├── Network latency
└── System resource utilization

Alerts to Configure:
├── Interface down for > 5 minutes
├── Error rate > 5%
├── Queue depth > 100 messages
├── No messages received for > 1 hour (during business hours)
└── Epic acknowledgment not received
```

## Part 2: Epic FHIR API Integration

### Step 1: App Registration

**1.1 Register Application on Epic App Orchard**

1. Go to https://apporchard.epic.com/
2. Create developer account
3. Register new application:

```
Application Details:
├── App Name: "Your App Name"
├── App Type:
│   ├── Patient-facing (standalone launch)
│   ├── Provider-facing (EHR launch)
│   └── Backend service (system-to-system)
├── FHIR Version: R4
├── Scopes Requested:
│   ├── patient/Patient.read
│   ├── patient/Observation.read
│   ├── patient/Condition.read
│   ├── patient/MedicationRequest.read
│   └── offline_access (for refresh tokens)
├── Redirect URIs:
│   ├── https://yourapp.com/callback
│   └── https://localhost:3000/callback (for testing)
└── Launch URIs (if EHR launch):
    └── https://yourapp.com/launch
```

**1.2 Obtain Client Credentials**

After approval, you'll receive:
```
Client ID: your-client-id-from-epic
Client Secret: your-client-secret (for confidential clients)
```

### Step 2: Implement OAuth 2.0 Authentication

**2.1 SMART on FHIR Standalone Launch (Patient App)**

```javascript
// File: auth.js

const EPIC_CONFIG = {
  authorizationEndpoint: 'https://fhir.epic.com/interconnect-fhir-oauth/oauth2/authorize',
  tokenEndpoint: 'https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token',
  fhirBaseUrl: 'https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4',
  clientId: 'your-client-id',
  redirectUri: 'https://yourapp.com/callback',
  scope: 'patient/Patient.read patient/Observation.read launch/patient offline_access'
};

// Step 1: Initiate authorization
function initiateAuth() {
  const state = generateRandomString(32);
  sessionStorage.setItem('oauth_state', state);

  const params = new URLSearchParams({
    response_type: 'code',
    client_id: EPIC_CONFIG.clientId,
    redirect_uri: EPIC_CONFIG.redirectUri,
    scope: EPIC_CONFIG.scope,
    state: state,
    aud: EPIC_CONFIG.fhirBaseUrl
  });

  window.location.href = `${EPIC_CONFIG.authorizationEndpoint}?${params.toString()}`;
}

// Step 2: Handle callback
async function handleCallback() {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  const state = urlParams.get('state');

  // Verify state
  const savedState = sessionStorage.getItem('oauth_state');
  if (state !== savedState) {
    throw new Error('State mismatch - possible CSRF attack');
  }

  // Exchange code for token
  const tokenResponse = await fetch(EPIC_CONFIG.tokenEndpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      code: code,
      redirect_uri: EPIC_CONFIG.redirectUri,
      client_id: EPIC_CONFIG.clientId
    })
  });

  const tokenData = await tokenResponse.json();

  // Store tokens securely
  sessionStorage.setItem('access_token', tokenData.access_token);
  sessionStorage.setItem('refresh_token', tokenData.refresh_token);
  sessionStorage.setItem('patient_id', tokenData.patient);
  sessionStorage.setItem('token_expiry', Date.now() + (tokenData.expires_in * 1000));

  return tokenData;
}

// Step 3: Refresh access token
async function refreshAccessToken() {
  const refreshToken = sessionStorage.getItem('refresh_token');

  const response = await fetch(EPIC_CONFIG.tokenEndpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
      client_id: EPIC_CONFIG.clientId
    })
  });

  const tokenData = await response.json();

  sessionStorage.setItem('access_token', tokenData.access_token);
  sessionStorage.setItem('token_expiry', Date.now() + (tokenData.expires_in * 1000));

  return tokenData.access_token;
}

function generateRandomString(length) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}
```

### Step 3: Make FHIR API Requests

**3.1 Read Patient Demographics**

```javascript
// File: fhirClient.js

async function getAccessToken() {
  const token = sessionStorage.getItem('access_token');
  const expiry = sessionStorage.getItem('token_expiry');

  // Refresh if expired or about to expire (5 min buffer)
  if (Date.now() >= (expiry - 300000)) {
    return await refreshAccessToken();
  }

  return token;
}

async function getPatient(patientId) {
  const token = await getAccessToken();

  const response = await fetch(
    `${EPIC_CONFIG.fhirBaseUrl}/Patient/${patientId}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/fhir+json'
      }
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch patient: ${response.statusText}`);
  }

  return await response.json();
}
```

**3.2 Search for Observations (Lab Results)**

```javascript
async function getLabResults(patientId, startDate, endDate) {
  const token = await getAccessToken();

  const params = new URLSearchParams({
    patient: patientId,
    category: 'laboratory',
    date: `ge${startDate}`,
    _sort: '-date',
    _count: 50
  });

  if (endDate) {
    params.append('date', `le${endDate}`);
  }

  const response = await fetch(
    `${EPIC_CONFIG.fhirBaseUrl}/Observation?${params.toString()}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/fhir+json'
      }
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch observations: ${response.statusText}`);
  }

  const bundle = await response.json();
  return bundle.entry ? bundle.entry.map(e => e.resource) : [];
}
```

**3.3 Error Handling and Retry Logic**

```javascript
async function fhirRequest(url, options = {}, retries = 3) {
  try {
    const response = await fetch(url, options);

    // Handle rate limiting
    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After') || 60;
      console.log(`Rate limited. Retrying after ${retryAfter} seconds`);
      await sleep(retryAfter * 1000);
      return fhirRequest(url, options, retries - 1);
    }

    // Handle server errors with retry
    if (response.status >= 500 && retries > 0) {
      console.log(`Server error. Retrying... (${retries} attempts remaining)`);
      await sleep(2000);
      return fhirRequest(url, options, retries - 1);
    }

    return response;
  } catch (error) {
    if (retries > 0) {
      console.log(`Network error. Retrying... (${retries} attempts remaining)`);
      await sleep(2000);
      return fhirRequest(url, options, retries - 1);
    }
    throw error;
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

### Step 4: Testing

**4.1 Use Epic Sandbox**

```javascript
// Test configuration
const EPIC_SANDBOX_CONFIG = {
  fhirBaseUrl: 'https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4',
  // Some Epic sandbox endpoints don't require authentication
  // Or use test credentials provided by Epic
};

// Test patient IDs (Epic provides these for testing)
const TEST_PATIENTS = {
  SMART_DEMO: 'eM8ExaPxLEY8z6j9QKI.Z.Q3',
  // Add more test patient IDs from Epic documentation
};
```

**4.2 Automated Testing**

```javascript
// test/epic-integration.test.js
const assert = require('assert');

describe('Epic FHIR Integration', function() {

  it('should fetch patient demographics', async function() {
    const patient = await getPatient(TEST_PATIENTS.SMART_DEMO);

    assert.ok(patient.resourceType === 'Patient');
    assert.ok(patient.name && patient.name.length > 0);
    assert.ok(patient.birthDate);
  });

  it('should fetch lab observations', async function() {
    const observations = await getLabResults(
      TEST_PATIENTS.SMART_DEMO,
      '2020-01-01'
    );

    assert.ok(Array.isArray(observations));
    observations.forEach(obs => {
      assert.ok(obs.resourceType === 'Observation');
      assert.ok(obs.category);
      assert.ok(obs.code);
    });
  });

  it('should handle rate limiting gracefully', async function() {
    this.timeout(65000); // Extend timeout for retry testing

    // Make many rapid requests to trigger rate limiting
    const promises = [];
    for (let i = 0; i < 100; i++) {
      promises.push(getPatient(TEST_PATIENTS.SMART_DEMO));
    }

    // Should not throw error, should handle rate limiting
    await Promise.all(promises);
  });
});
```

## Part 3: Production Best Practices

### Security

```
1. Token Management
   ├── Store tokens encrypted (not in localStorage)
   ├── Implement token refresh before expiry
   ├── Clear tokens on logout
   └── Use HTTPS only

2. API Security
   ├── Validate all Epic responses
   ├── Sanitize data before display
   ├── Implement CORS properly
   └── Use Content Security Policy headers

3. Audit Logging
   ├── Log all API requests
   ├── Log authentication events
   ├── Log errors and exceptions
   └── HIPAA-compliant audit trails
```

### Performance

```
1. Caching
   ├── Cache static resources (code systems)
   ├── Cache patient data (with expiry)
   ├── Implement ETag support
   └── Use service workers for offline capability

2. Pagination
   ├── Request appropriate page sizes (_count parameter)
   ├── Implement "next" link following
   ├── Show loading indicators
   └── Lazy load large result sets

3. Error Handling
   ├── Graceful degradation
   ├── User-friendly error messages
   ├── Retry with exponential backoff
   └── Circuit breaker pattern
```

## Troubleshooting

### Common Issues

```
Issue: "Invalid client_id"
Solution: Verify client ID matches Epic App Orchard registration

Issue: "Redirect URI mismatch"
Solution: Ensure redirect_uri exactly matches registered URI (including https://)

Issue: "Patient not found"
Solution: Verify patient ID is correct Epic FHIR patient ID

Issue: "Insufficient scope"
Solution: Request additional scopes during authorization

Issue: 429 Too Many Requests
Solution: Implement rate limiting, reduce request frequency

Issue: Connection timeout
Solution: Check network connectivity, Epic server status
```

## References

- Epic UserWeb: https://userweb.epic.com
- Epic App Orchard: https://apporchard.epic.com
- Epic FHIR Documentation: https://fhir.epic.com
- SMART on FHIR: https://smarthealthit.org

---

**Document Version**: 1.0
**Last Updated**: November 2024
**Classification**: Production Guide
