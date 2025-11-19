# EHR Integration Patterns

**Production-proven patterns for integrating with Epic, Cerner, and other EHR systems**

---

## Pattern 1: HL7 v2.x ADT Integration

**Use Case**: Sync patient demographics between systems (Admit/Discharge/Transfer messages)

### Context
Your application needs real-time patient demographic updates from the hospital EHR (Epic, Cerner, etc.) to maintain current patient information.

### Solution Architecture

```
[EHR System]  ──HL7 ADT Messages──>  [Interface Engine]  ──Transform/Route──>  [Your Application]
   (Epic)            TCP/IP              (Mirth Connect)                            (REST API)
                     MLLP Protocol                                                  (Database)
```

### Implementation

#### HL7 ADT Message Types

| Message | Trigger Event | Purpose | Frequency |
|---------|---------------|---------|-----------|
| ADT^A01 | Patient Admission | Patient admitted to hospital | Per admission |
| ADT^A02 | Patient Transfer | Patient transferred to different unit/location | Per transfer |
| ADT^A03 | Patient Discharge | Patient discharged from hospital | Per discharge |
| ADT^A04 | Patient Registration | Outpatient registration | Per registration |
| ADT^A08 | Update Patient Info | Demographics changed (address, phone, insurance) | Per update |
| ADT^A11 | Cancel Admission | Admission cancelled | As needed |
| ADT^A13 | Cancel Discharge | Discharge cancelled | As needed |
| ADT^A31 | Update Person Info | MPI update (master patient index) | Per MPI change |

#### Sample HL7 ADT^A01 Message (Patient Admission)

```
MSH|^~\&|EPIC|HOSPITAL|RECEIVING_APP|RECEIVING_FACILITY|20231115140530||ADT^A01|MSG00001|P|2.5
EVN|A01|20231115140530|||JSMITH^SMITH^JOHN^A^DR^MD|20231115140000
PID|1||MRN123456^^^HOSPITAL^MRN||DOE^JOHN^MICHAEL||19800115|M|||123 MAIN ST^APT 4B^BOSTON^MA^02101^USA^H||555-123-4567^H^CP|555-987-6543^WP||ENG|M|PROT||||123-45-6789|||N|||||||||N
NK1|1|DOE^JANE^M|SPO|123 MAIN ST^APT 4B^BOSTON^MA^02101|555-123-4567^H|||EC|||||||||||||||||||||||||||||
PV1|1|I|4N^401^01^HOSPITAL^^^^DEPT^4 NORTH|||1234^JONES^ROBERT^A^DR^MD|5678^SMITH^SARAH^B^DR^MD|1234^JONES^ROBERT^A^DR^MD|MED||||ADM|||1234^JONES^ROBERT^A^DR^MD|IP|ACCT123456789|||||||||||||||||HOSPITAL||ACT|||20231115140000
AL1|1|DRUG|^PENICILLIN|SEV|ANAPHYLAXIS~HIVES
DG1|1|ICD10|I50.9^HEART FAILURE UNSPECIFIED^ICD10||20231115140530|A
```

#### Message Parsing Logic

**PID Segment (Patient Identification)**:
- `PID-3`: Patient Identifier (MRN) - Extract for patient matching
- `PID-5`: Patient Name - Parse as Last^First^Middle
- `PID-7`: Date of Birth - Format YYYYMMDD
- `PID-8`: Sex - M/F/O/U
- `PID-11`: Address - Extract street, city, state, zip
- `PID-13`: Phone - Home phone
- `PID-18`: Account Number - Encounter identifier
- `PID-19`: SSN - If present (optional, privacy concerns)

**PV1 Segment (Patient Visit)**:
- `PV1-2`: Patient Class - I (Inpatient), O (Outpatient), E (Emergency)
- `PV1-3`: Assigned Patient Location - Facility^Room^Bed
- `PV1-7`: Attending Doctor - ID^Last^First
- `PV1-44`: Admit Date/Time
- `PV1-19`: Visit Number - Encounter ID

**AL1 Segment (Allergy Information)**:
- `AL1-3`: Allergen Code/Description
- `AL1-4`: Allergy Severity
- `AL1-5`: Allergy Reaction

#### Mirth Connect Channel Configuration

```javascript
// Mirth Connect JavaScript Transformer

// Extract patient MRN from PID-3
var mrn = msg['PID']['PID.3']['PID.3.1'].toString();
var mrnSystem = msg['PID']['PID.3']['PID.3.4'].toString();

// Extract patient name from PID-5
var lastName = msg['PID']['PID.5']['PID.5.1'].toString();
var firstName = msg['PID']['PID.5']['PID.5.2'].toString();
var middleName = msg['PID']['PID.5']['PID.5.3'].toString();

// Extract date of birth from PID-7 (YYYYMMDD format)
var dobRaw = msg['PID']['PID.7']['PID.7.1'].toString();
var dob = dobRaw.substring(0,4) + '-' + dobRaw.substring(4,6) + '-' + dobRaw.substring(6,8);

// Extract gender from PID-8
var gender = msg['PID']['PID.8']['PID.8.1'].toString();

// Extract address from PID-11
var street = msg['PID']['PID.11']['PID.11.1'].toString();
var street2 = msg['PID']['PID.11']['PID.11.2'].toString();
var city = msg['PID']['PID.11']['PID.11.3'].toString();
var state = msg['PID']['PID.11']['PID.11.4'].toString();
var zip = msg['PID']['PID.11']['PID.11.5'].toString();

// Extract phone from PID-13
var homePhone = msg['PID']['PID.13']['PID.13.1'].toString();

// Extract message type
var messageType = msg['MSH']['MSH.9']['MSH.9.1'].toString() + '^' +
                 msg['MSH']['MSH.9']['MSH.9.2'].toString();

// Build JSON payload for REST API
var payload = {
  "messageType": messageType,
  "messageId": msg['MSH']['MSH.10']['MSH.10.1'].toString(),
  "messageTimestamp": msg['MSH']['MSH.7']['MSH.7.1'].toString(),
  "patient": {
    "identifiers": [
      {
        "system": mrnSystem,
        "type": "MRN",
        "value": mrn
      }
    ],
    "name": {
      "family": lastName,
      "given": [firstName, middleName],
      "use": "official"
    },
    "birthDate": dob,
    "gender": gender === 'M' ? 'male' : (gender === 'F' ? 'female' : 'unknown'),
    "address": {
      "line": [street, street2].filter(Boolean),
      "city": city,
      "state": state,
      "postalCode": zip,
      "country": "US"
    },
    "telecom": [
      {
        "system": "phone",
        "value": homePhone,
        "use": "home"
      }
    ]
  }
};

// Handle allergies if present
if (msg['AL1'] !== undefined) {
  var allergies = [];
  for each (var al1 in msg['AL1']) {
    allergies.push({
      "allergen": al1['AL1.3']['AL1.3.2'].toString(),
      "severity": al1['AL1.4']['AL1.4.1'].toString(),
      "reaction": al1['AL1.5']['AL1.5.1'].toString()
    });
  }
  payload.patient.allergies = allergies;
}

// Handle encounter info from PV1
if (msg['PV1'] !== undefined) {
  payload.encounter = {
    "class": msg['PV1']['PV1.2']['PV1.2.1'].toString(),
    "location": msg['PV1']['PV1.3']['PV1.3.1'].toString() + '-' +
                msg['PV1']['PV1.3']['PV1.3.2'].toString(),
    "attendingDoctor": {
      "id": msg['PV1']['PV1.7']['PV1.7.1'].toString(),
      "name": msg['PV1']['PV1.7']['PV1.7.2'].toString() + ', ' +
              msg['PV1']['PV1.7']['PV1.7.3'].toString()
    },
    "visitNumber": msg['PV1']['PV1.19']['PV1.19.1'].toString(),
    "admitDateTime": msg['PV1']['PV1.44']['PV1.44.1'].toString()
  };
}

// Set payload for HTTP destination
channelMap.put('jsonPayload', JSON.stringify(payload));

// Return ACK (positive acknowledgment)
var ack = ACKGenerator.generateAckResponse(msg, 'AA', 'Message accepted');
return ack;
```

#### REST API Endpoint (Receiving Application)

```javascript
// Node.js Express endpoint to receive transformed HL7 data

const express = require('express');
const { body, validationResult } = require('express-validator');

app.post('/api/v1/hl7/adt',
  // Authentication middleware
  authenticateHL7Interface,

  // Validation
  body('messageType').isIn(['ADT^A01', 'ADT^A02', 'ADT^A03', 'ADT^A04', 'ADT^A08']),
  body('patient.identifiers').isArray({ min: 1 }),
  body('patient.birthDate').isISO8601(),

  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { messageType, patient, encounter } = req.body;

    try {
      // Find or create patient by MRN
      const mrn = patient.identifiers.find(id => id.type === 'MRN');
      let dbPatient = await Patient.findOne({
        'identifiers.type': 'MRN',
        'identifiers.value': mrn.value
      });

      if (messageType === 'ADT^A01' || messageType === 'ADT^A04') {
        // Admission or Registration - Create or update patient

        if (!dbPatient) {
          dbPatient = new Patient({
            identifiers: patient.identifiers,
            name: patient.name,
            birthDate: new Date(patient.birthDate),
            gender: patient.gender,
            address: patient.address,
            telecom: patient.telecom,
            active: true
          });
        } else {
          // Update existing patient demographics
          Object.assign(dbPatient, {
            name: patient.name,
            birthDate: new Date(patient.birthDate),
            gender: patient.gender,
            address: patient.address,
            telecom: patient.telecom
          });
        }

        await dbPatient.save();

        // Create encounter record
        if (encounter) {
          const newEncounter = new Encounter({
            patient: dbPatient._id,
            visitNumber: encounter.visitNumber,
            class: encounter.class,
            location: encounter.location,
            attendingPhysician: encounter.attendingDoctor,
            admitDateTime: new Date(encounter.admitDateTime),
            status: 'active'
          });
          await newEncounter.save();
        }

        // Update allergies
        if (patient.allergies) {
          await Allergy.deleteMany({ patient: dbPatient._id });
          const allergyDocs = patient.allergies.map(a => ({
            patient: dbPatient._id,
            allergen: a.allergen,
            severity: a.severity,
            reaction: a.reaction,
            status: 'active'
          }));
          await Allergy.insertMany(allergyDocs);
        }

        // Audit log for HIPAA compliance
        await AuditLog.create({
          action: 'HL7_ADT_RECEIVED',
          messageType: messageType,
          patient: dbPatient._id,
          user: 'HL7_INTERFACE',
          timestamp: new Date(),
          details: { messageId: req.body.messageId }
        });

        res.status(200).json({
          success: true,
          patientId: dbPatient._id,
          message: 'Patient admitted successfully'
        });

      } else if (messageType === 'ADT^A03') {
        // Discharge - Update encounter status
        if (!dbPatient) {
          return res.status(404).json({ error: 'Patient not found' });
        }

        await Encounter.updateOne(
          { visitNumber: encounter.visitNumber },
          {
            status: 'completed',
            dischargeDateTime: new Date()
          }
        );

        res.status(200).json({
          success: true,
          message: 'Patient discharged successfully'
        });

      } else if (messageType === 'ADT^A08') {
        // Update patient info
        if (!dbPatient) {
          return res.status(404).json({ error: 'Patient not found' });
        }

        Object.assign(dbPatient, {
          name: patient.name,
          address: patient.address,
          telecom: patient.telecom
        });
        await dbPatient.save();

        res.status(200).json({
          success: true,
          message: 'Patient information updated successfully'
        });
      }

    } catch (error) {
      console.error('Error processing ADT message:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }
);
```

### Error Handling

#### Negative Acknowledgments (NACK)

```javascript
// Generate NACK when message cannot be processed

if (patientMrnMissing) {
  return ACKGenerator.generateAckResponse(msg, 'AE', 'Required field PID-3 (Patient MRN) is missing');
}

if (invalidDateFormat) {
  return ACKGenerator.generateAckResponse(msg, 'AE', 'Invalid date format in PID-7 (Date of Birth)');
}

if (duplicateMessageId) {
  return ACKGenerator.generateAckResponse(msg, 'AR', 'Duplicate message ID - message already processed');
}
```

ACK Code Meanings:
- `AA`: Application Accept - Message accepted and processed
- `AE`: Application Error - Message rejected due to error
- `AR`: Application Reject - Message rejected (e.g., duplicate)

#### Retry Logic

```javascript
// HTTP destination in Mirth - retry on failure

var maxRetries = 3;
var retryDelay = 5000; // 5 seconds

for (var attempt = 1; attempt <= maxRetries; attempt++) {
  try {
    var response = router.routeMessage('HTTP_Sender', message);
    if (response.getStatus() === 'SENT') {
      logger.info('Message sent successfully on attempt ' + attempt);
      return ACKGenerator.generateAckResponse(msg, 'AA', 'Message accepted');
    }
  } catch (error) {
    logger.error('Attempt ' + attempt + ' failed: ' + error.message);
    if (attempt < maxRetries) {
      java.lang.Thread.sleep(retryDelay * attempt); // Exponential backoff
    }
  }
}

// All retries exhausted
logger.error('All retry attempts exhausted for message ' + messageId);
return ACKGenerator.generateAckResponse(msg, 'AE', 'Unable to process message after ' + maxRetries + ' attempts');
```

### Testing

#### Unit Test HL7 Messages

```python
# Python script to generate test HL7 ADT messages

from hl7apy.core import Message
from hl7apy.parser import parse_message
import socket

def create_adt_a01():
    """Create sample ADT^A01 message"""

    msg = Message("ADT_A01")
    msg.msh.msh_3 = "EPIC"
    msg.msh.msh_4 = "HOSPITAL"
    msg.msh.msh_5 = "RECEIVING_APP"
    msg.msh.msh_6 = "RECEIVING_FACILITY"
    msg.msh.msh_9 = "ADT^A01"
    msg.msh.msh_10 = "MSG00001"
    msg.msh.msh_11 = "P"
    msg.msh.msh_12 = "2.5"

    msg.add_segment("EVN")
    msg.evn.evn_1 = "A01"

    msg.add_segment("PID")
    msg.pid.pid_1 = "1"
    msg.pid.pid_3 = "MRN123456^^^HOSPITAL^MRN"
    msg.pid.pid_5 = "DOE^JOHN^MICHAEL"
    msg.pid.pid_7 = "19800115"
    msg.pid.pid_8 = "M"
    msg.pid.pid_11 = "123 MAIN ST^APT 4B^BOSTON^MA^02101^USA"
    msg.pid.pid_13 = "555-123-4567"

    return msg.to_mllp()

def send_hl7_message(host, port, message):
    """Send HL7 message via MLLP"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.sendall(message)

        # Receive ACK
        ack = sock.recv(4096)
        return ack.decode('utf-8')
    finally:
        sock.close()

# Test
adt_message = create_adt_a01()
ack = send_hl7_message('localhost', 6661, adt_message)
print(f"Received ACK: {ack}")
```

### Performance Considerations

- **Message Volume**: Design for peak load (e.g., 500 ADT messages during shift change)
- **Response Time**: ACK should be returned within 2 seconds
- **Database Indexes**: Index on MRN for fast patient lookup
- **Connection Pooling**: Use connection pooling for database connections
- **Async Processing**: Consider async message processing for high volume

### HIPAA Compliance

- **Encryption in Transit**: Use TLS for HL7 message transmission
- **Audit Logging**: Log all ADT messages received (who, what, when)
- **Access Controls**: Restrict interface engine access to authorized personnel
- **Minimum Necessary**: Only transmit required data elements
- **Business Associate Agreement**: Establish BAA with EHR vendor

---

## Pattern 2: FHIR API Integration

**Use Case**: Read patient data from EHR via FHIR API (Epic, Cerner, etc.)

### Context
Your application needs to query patient clinical data (allergies, medications, problems, lab results) from Epic's FHIR API.

### Solution Architecture

```
[Your Application]  ──HTTPS REST──>  [EHR FHIR Server]
                                          (Epic on FHIR)
                                          (Cerner FHIR)
                                          (SMART on FHIR)
                    <──OAuth 2.0──
                    <──FHIR Resources JSON──
```

### Implementation

#### Step 1: App Registration (Epic Example)

Register your application in Epic App Orchard:
- **Application Type**: Provider-facing or Patient-facing
- **FHIR Version**: R4
- **Scopes Requested**:
  - `patient/Patient.read`
  - `patient/AllergyIntolerance.read`
  - `patient/MedicationRequest.read`
  - `patient/Condition.read`
  - `patient/Observation.read`
- **Redirect URI**: `https://yourapp.com/auth/callback`
- **Launch URI**: `https://yourapp.com/launch` (for EHR launch)

Receive:
- **Client ID**: `abc123xyz`
- **FHIR Endpoint**: `https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4`

#### Step 2: OAuth 2.0 Authorization (SMART on FHIR)

**EHR Launch Workflow**:

```javascript
// 1. EHR initiates launch by redirecting to your launch URI with parameters
// https://yourapp.com/launch?iss=https://fhir.epic.com/...&launch=xyz789

app.get('/launch', (req, res) => {
  const iss = req.query.iss; // FHIR server URL
  const launch = req.query.launch; // Launch context token

  // Store launch token in session
  req.session.launch = launch;

  // Discover authorization endpoints from FHIR server
  fetch(`${iss}/metadata`)
    .then(res => res.json())
    .then(metadata => {
      const authEndpoint = metadata.rest[0].security.extension
        .find(ext => ext.url === 'http://fhir-registry.smarthealthit.org/StructureDefinition/oauth-uris')
        .extension.find(ext => ext.url === 'authorize').valueUri;

      const tokenEndpoint = metadata.rest[0].security.extension
        .find(ext => ext.url === 'http://fhir-registry.smarthealthit.org/StructureDefinition/oauth-uris')
        .extension.find(ext => ext.url === 'token').valueUri;

      // Store endpoints
      req.session.authEndpoint = authEndpoint;
      req.session.tokenEndpoint = tokenEndpoint;

      // Redirect to authorization endpoint
      const authUrl = `${authEndpoint}?` +
        `response_type=code&` +
        `client_id=${CLIENT_ID}&` +
        `redirect_uri=${encodeURIComponent(REDIRECT_URI)}&` +
        `launch=${launch}&` +
        `scope=${encodeURIComponent('launch patient/Patient.read patient/AllergyIntolerance.read patient/MedicationRequest.read patient/Condition.read patient/Observation.read')}&` +
        `state=${generateSecureRandomState()}&` +
        `aud=${encodeURIComponent(iss)}`;

      res.redirect(authUrl);
    });
});

// 2. User authorizes, EHR redirects back with authorization code
// https://yourapp.com/auth/callback?code=auth_code_123&state=xyz

app.get('/auth/callback', async (req, res) => {
  const code = req.query.code;
  const state = req.query.state;

  // Verify state parameter (CSRF protection)
  if (state !== req.session.state) {
    return res.status(400).send('Invalid state parameter');
  }

  // Exchange authorization code for access token
  const tokenResponse = await fetch(req.session.tokenEndpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      code: code,
      redirect_uri: REDIRECT_URI,
      client_id: CLIENT_ID
    })
  });

  const tokenData = await tokenResponse.json();

  /*
  tokenData = {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": "patient/Patient.read patient/AllergyIntolerance.read ...",
    "patient": "erXuFYUfucBZaryVksYEcMg3", // Patient ID from Epic
    "encounter": "eXyZabc123"  // Current encounter ID (if applicable)
  }
  */

  // Store access token and patient ID in session
  req.session.accessToken = tokenData.access_token;
  req.session.patientId = tokenData.patient;
  req.session.encounterId = tokenData.encounter;

  // Redirect to main app
  res.redirect('/dashboard');
});
```

#### Step 3: Query FHIR Resources

```javascript
// Fetch patient demographics
async function getPatient(patientId, accessToken) {
  const response = await fetch(
    `${FHIR_BASE_URL}/Patient/${patientId}`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/fhir+json'
      }
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch patient: ${response.statusText}`);
  }

  return await response.json();
}

// Fetch patient allergies
async function getAllergies(patientId, accessToken) {
  const response = await fetch(
    `${FHIR_BASE_URL}/AllergyIntolerance?patient=${patientId}&clinical-status=active`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/fhir+json'
      }
    }
  );

  const bundle = await response.json();
  return bundle.entry ? bundle.entry.map(e => e.resource) : [];
}

// Fetch patient medications
async function getMedications(patientId, accessToken) {
  const response = await fetch(
    `${FHIR_BASE_URL}/MedicationRequest?patient=${patientId}&status=active&_include=MedicationRequest:medication`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/fhir+json'
      }
    }
  );

  const bundle = await response.json();
  return bundle.entry ? bundle.entry.map(e => e.resource) : [];
}

// Fetch patient problem list
async function getProblems(patientId, accessToken) {
  const response = await fetch(
    `${FHIR_BASE_URL}/Condition?patient=${patientId}&category=problem-list-item&clinical-status=active`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/fhir+json'
      }
    }
  );

  const bundle = await response.json();
  return bundle.entry ? bundle.entry.map(e => e.resource) : [];
}

// Fetch lab results (Observations)
async function getLabResults(patientId, accessToken, category = 'laboratory') {
  const response = await fetch(
    `${FHIR_BASE_URL}/Observation?patient=${patientId}&category=${category}&_sort=-date&_count=100`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/fhir+json'
      }
    }
  );

  const bundle = await response.json();
  return bundle.entry ? bundle.entry.map(e => e.resource) : [];
}

// Usage in Express route
app.get('/api/patient-summary', async (req, res) => {
  const { accessToken, patientId } = req.session;

  if (!accessToken || !patientId) {
    return res.status(401).json({ error: 'Not authenticated' });
  }

  try {
    const [patient, allergies, medications, problems, labs] = await Promise.all([
      getPatient(patientId, accessToken),
      getAllergies(patientId, accessToken),
      getMedications(patientId, accessToken),
      getProblems(patientId, accessToken),
      getLabResults(patientId, accessToken)
    ]);

    res.json({
      patient: {
        id: patient.id,
        name: patient.name[0].given.join(' ') + ' ' + patient.name[0].family,
        birthDate: patient.birthDate,
        gender: patient.gender
      },
      allergies: allergies.map(a => ({
        allergen: a.code.coding[0].display,
        criticality: a.criticality,
        reactions: a.reaction ? a.reaction.map(r => r.manifestation[0].coding[0].display) : []
      })),
      medications: medications
        .filter(m => m.resourceType === 'MedicationRequest')
        .map(m => ({
          medication: m.medicationCodeableConcept?.coding[0].display ||
                     medications.find(med => med.id === m.medicationReference?.reference?.split('/')[1])?.code?.coding[0].display,
          dosage: m.dosageInstruction ? m.dosageInstruction[0].text : 'N/A',
          status: m.status
        })),
      problems: problems.map(p => ({
        problem: p.code.coding[0].display,
        onsetDate: p.onsetDateTime || 'Unknown',
        clinicalStatus: p.clinicalStatus.coding[0].code
      })),
      labs: labs.map(l => ({
        test: l.code.coding[0].display,
        value: l.valueQuantity ? `${l.valueQuantity.value} ${l.valueQuantity.unit}` :
               l.valueString || 'N/A',
        date: l.effectiveDateTime,
        status: l.status
      }))
    });

  } catch (error) {
    console.error('Error fetching patient data:', error);
    res.status(500).json({ error: 'Failed to fetch patient data' });
  }
});
```

### Token Refresh

```javascript
async function refreshAccessToken(refreshToken) {
  const response = await fetch(TOKEN_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
      client_id: CLIENT_ID
    })
  });

  const newTokenData = await response.json();
  return newTokenData.access_token;
}

// Middleware to check token expiration and refresh if needed
async function ensureValidToken(req, res, next) {
  const { accessToken, tokenExpiry, refreshToken } = req.session;

  if (Date.now() >= tokenExpiry) {
    try {
      const newAccessToken = await refreshAccessToken(refreshToken);
      req.session.accessToken = newAccessToken;
      req.session.tokenExpiry = Date.now() + (3600 * 1000); // 1 hour
    } catch (error) {
      return res.status(401).json({ error: 'Session expired, please re-authenticate' });
    }
  }

  next();
}
```

### Error Handling

```javascript
async function fetchFHIRResource(url, accessToken) {
  try {
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/fhir+json'
      }
    });

    if (response.status === 401) {
      throw new Error('Unauthorized - token expired or invalid');
    }

    if (response.status === 403) {
      throw new Error('Forbidden - insufficient scopes');
    }

    if (response.status === 404) {
      return null; // Resource not found
    }

    if (response.status === 429) {
      // Rate limited - implement exponential backoff
      const retryAfter = response.headers.get('Retry-After') || 60;
      await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
      return fetchFHIRResource(url, accessToken); // Retry
    }

    if (!response.ok) {
      const errorBody = await response.json();
      throw new Error(`FHIR API error: ${errorBody.issue?.[0]?.diagnostics || response.statusText}`);
    }

    return await response.json();

  } catch (error) {
    console.error('FHIR API error:', error);
    throw error;
  }
}
```

### Best Practices

1. **Scope Minimization**: Request only necessary scopes
2. **Token Storage**: Store access tokens securely (encrypted session storage, never in localStorage for web apps)
3. **HTTPS Only**: All communication over HTTPS
4. **State Parameter**: Always use state parameter for CSRF protection
5. **PKCE**: Implement PKCE (Proof Key for Code Exchange) for public clients
6. **Rate Limiting**: Respect EHR API rate limits (typically 100-1000 requests/minute)
7. **Caching**: Cache FHIR resources where appropriate (consider patient data sensitivity)
8. **Error Handling**: Gracefully handle API errors and token expiration
9. **Audit Logging**: Log all FHIR API calls for HIPAA compliance
10. **Testing**: Use Epic Sandbox or Cerner Sandbox for development/testing

---

**References:**
- HL7 Version 2.5 Implementation Guide
- FHIR R4 Specification (hl7.org/fhir)
- SMART on FHIR Documentation (docs.smarthealthit.org)
- Epic on FHIR Documentation (fhir.epic.com)
- Cerner FHIR Documentation (fhir.cerner.com)

**Version**: 1.0
**Last Updated**: 2025-11-19
