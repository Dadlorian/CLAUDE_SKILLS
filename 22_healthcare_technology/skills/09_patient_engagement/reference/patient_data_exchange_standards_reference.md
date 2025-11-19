# Patient Data Exchange Standards Reference

## Standards Overview

### HL7 (Health Level 7) Standards

**HL7 v2.x - Messaging Standard**

Purpose: System-to-system communication
Current Version: v2.5.1 (still widely used)
Status: Maintained but legacy approach

**Common Messages:**
```
ADT (Admission, Discharge, Transfer)
├─ A01: Admit/Visit Notification
├─ A04: Patient Registration
└─ A03: Discharge/End Visit

ORU (Observation Result)
├─ R01: Unsolicited transmission of observation
└─ Used for lab results, vital signs

RGV (Pharmacy/Treatment Give)
├─ O15: Pharmacy treatment order
└─ Used for medication dispensing

PGL (Patient Goal)
├─ PC6: Goal add/update
└─ Used for health goals and care plans
```

**HL7 v3 - XML-Based Standard**

Purpose: Clinical document exchange and structured data
Format: XML with RIM (Reference Information Model)
Complexity: High, steep learning curve
Adoption: Limited except for specific use cases (CCDA)

### HL7 FHIR (Fast Healthcare Interoperability Resources)

**Modern Standard (2011-present)**
- RESTful API paradigm
- JSON or XML format
- Modular resource-based approach
- Developer-friendly
- Growing adoption and preferred standard

**Core Principles:**
```
1. RESTful Architecture
   ├─ Standard HTTP methods (GET, POST, PUT, DELETE)
   ├─ Resource-based URLs
   ├─ Stateless communication
   └─ Cacheable responses

2. Resource-Based Model
   ├─ Discrete clinical concepts as resources
   ├─ Composable resources
   ├─ Profiles and extensions for customization
   └─ Version evolution support

3. Standards-Compliant Coding
   ├─ ICD-10, SNOMED CT, LOINC, RxNorm
   ├─ Extensible Value Sets
   ├─ Concept Maps for translation
   └─ CodeSystem references

4. Security and Privacy
   ├─ OAuth2 and OpenID Connect
   ├─ Scopes for data access
   ├─ Audit logging capability
   └─ HIPAA compliance ready
```

## Standards Comparison

| Aspect | HL7 v2 | HL7 v3/CCDA | FHIR |
|--------|---------|-----------|------|
| Era | 1989-present | 2005-present | 2011-present |
| Format | Text/pipe-delimited | XML | JSON/XML |
| Complexity | Low | High | Medium |
| Learning Curve | Shallow | Steep | Moderate |
| RESTful Support | No | No | Yes |
| API Friendly | No | No | Yes |
| Industry Adoption | Highest | Moderate (CDA) | Rapidly growing |
| Best Use Case | Legacy integration | Clinical documents | Modern APIs |

## FHIR Architecture Deep Dive

### FHIR Resources for Patient Engagement

**Patient Resource:**
```
Core Elements:
- identifier: Medical record numbers
- name: Patient name(s)
- telecom: Contact information
- gender: Administrative gender
- birthDate: Date of birth
- address: Mailing address
- maritalStatus: Marital status
- communication: Languages and preferences

Extensions:
- race and ethnicity
- sexual orientation and gender identity
- preferred pronouns
- emergency contacts
```

**Encounter Resource (Visit):**
```
Elements:
- status: "planned", "arrived", "triaged", "in-progress", "onleave", "finished", "cancelled"
- type: Encounter type (visit, consultation, admission)
- serviceType: Type of service (emergency, urgent care)
- reasonCode: Chief complaint/reason
- subject: Patient reference
- participant: Involved practitioners
- period: Start and end times
- length: Duration
- location: Where encounter occurred
- diagnosis: Associated diagnoses
```

**Condition Resource (Problem):**
```
Elements:
- clinicalStatus: "active", "recurrence", "relapse", "inactive", "remission", "resolved"
- verificationStatus: "unconfirmed", "provisional", "differential", "confirmed", "refuted", "entered-in-error"
- code: ICD-10 or SNOMED code
- subject: Patient reference
- onsetDateTime or onsetAge: When condition started
- abatementDateTime: When condition resolved
- recordedDate: When documented
- recorder: Who documented
- note: Additional information
```

**Medication Resource and MedicationStatement:**
```
Medication Resource:
- code: Medication identifier (RxNorm)
- manufacturer: Drug manufacturer
- form: Tablet, liquid, injection, etc.
- ingredient: Components
- package: Packaging details

MedicationStatement:
- status: "active", "completed", "entered-in-error"
- medicationCodeableConcept: Drug and strength
- subject: Patient
- effectiveDateTime: When taking medication
- dateAsserted: When documented
- informationSource: Who provided info
- dosage: Route, frequency, dose
- reasonCode: Why taking
- note: Additional information
```

**Observation Resource (Labs, Vitals):**
```
Elements:
- status: "registered", "preliminary", "final", "amended", "cancelled", "entered-in-error"
- category: Type of observation
- code: LOINC code
- subject: Patient
- effectiveDateTime: When measured
- issued: When reported
- performer: Who performed
- value: Result value
- interpretation: Normal/abnormal
- referenceRange: Normal range
- note: Clinical notes
```

**Goal Resource:**
```
Elements:
- lifecycleStatus: "proposed", "planned", "accepted", "active", "on-hold", "completed", "cancelled", "entered-in-error"
- achievementStatus: "in-progress", "improving", "worsening", "no-change", "achieved", "not-achieved"
- description: Goal description
- subject: Patient
- startDate: Goal start date
- target: Target value/date for goal
- statusDate: When status updated
- statusReason: Why status changed
- addresses: Problem references
- note: Additional details
```

**CarePlan Resource:**
```
Elements:
- status: "draft", "active", "on-hold", "revoked", "completed", "entered-in-error"
- intent: "proposal", "plan", "order"
- category: Type of care plan
- subject: Patient
- period: Start and end dates
- created: When created
- author: Who created
- careTeam: Team members
- addresses: Problems addressed
- goal: Goals referenced
- activity: Care activities
  └─ detail: Implementation details
```

## API Patterns for Patient Data Exchange

### RESTful API Design

**Resource Endpoints:**
```
GET /fhir/Patient/{patientId}
GET /fhir/Patient/{patientId}/Condition
GET /fhir/Patient/{patientId}/Medication
GET /fhir/Patient/{patientId}/Observation
GET /fhir/Observation?code=LOINC_CODE&patient={patientId}
```

**HTTP Status Codes:**
```
2xx Success:
- 200 OK: Successful GET
- 201 Created: Successful POST (resource created)
- 204 No Content: Successful DELETE

4xx Client Error:
- 400 Bad Request: Invalid parameters
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Resource not found

5xx Server Error:
- 500 Internal Server Error: Server fault
- 503 Service Unavailable: Temporarily down
```

**Response Format:**
```json
{
  "resourceType": "Patient",
  "id": "example-patient-1",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2023-11-19T10:00:00Z"
  },
  "identifier": [
    {
      "system": "http://hospital.example.com/fhir/mrn",
      "value": "MRN-12345"
    }
  ],
  "name": [
    {
      "use": "official",
      "family": "Smith",
      "given": ["John", "James"]
    }
  ]
}
```

### SMART on FHIR

**Use Case: Third-Party App Access**

```
Step 1: App Launch
└─ User launches app from EHR portal
   Receives: launch_id and iss (EHR identity)

Step 2: Authorization
└─ App redirects to EHR authorization endpoint
   User logs in and grants permissions
   Receives: authorization_code

Step 3: Token Exchange
└─ App exchanges code for access token
   POST /fhir/oauth/token
   Receives: access_token, refresh_token

Step 4: Data Access
└─ App uses access token to fetch data
   GET /fhir/Patient/123 (with Bearer token)

Step 5: Context Awareness
└─ App knows patient context (no re-authentication)
   patient = 'example-patient-1'
```

**Common SMART Scopes:**
```
Patient Permissions:
- launch/patient: Patient context established
- patient/Patient.read: Read patient demographics
- patient/Condition.read: Read problems
- patient/Medication.read: Read medications
- patient/Observation.read: Read observations
- patient/MedicationStatement.read: Read med history

Practitioner Permissions:
- user/Practitioner.read: Read own provider info
- user/Organization.read: Read organization info

Data Sharing:
- offline_access: Refresh token for background access
- user/*.read: Broader provider access
```

## Direct Protocol for Secure Messaging

**Purpose:** HIPAA-compliant secure email
**Format:** Encrypted email over SMTP/TLS
**Addressing:** Direct addresses (name@domain.direct)

**Message Structure:**
```
Direct Protocol Message:

To: patient@patient.direct
From: doctor@provider.direct
Subject: Your Lab Results
Message: Encrypted medical information

Attachment Options:
- PDF documents
- CCDA files
- CDS reports
```

**Direct Advantages:**
- Simple HIPAA compliance
- No special licensing
- Any email client compatible
- Encrypted by default
- Audit logs available

**Limitations:**
- One-way communication (not real-time conversation)
- Not suitable for urgent messages
- Limited to document exchange
- Doesn't scale for bulk messaging

## Healthcare API Gateways

### API Gateway Architecture

```
Patient App/EHR
    ↓
┌─────────────────────────┐
│  API Gateway            │
├─────────────────────────┤
│ • Authentication        │
│ • Authorization         │
│ • Rate Limiting         │
│ • Data Transformation   │
│ • Logging and Audit     │
└─────────────────────────┘
    ↓
Backend Services
├─ Patient Service
├─ Clinical Data Service
├─ Messaging Service
└─ Analytics Service
```

**Gateway Responsibilities:**
1. **Authentication**
   - Verify user identity
   - Token validation
   - MFA enforcement

2. **Authorization**
   - Verify permissions
   - RBAC enforcement
   - Scope validation

3. **Request Processing**
   - Parameter validation
   - Data transformation
   - Request routing

4. **Response Processing**
   - Data filtering (privacy rules)
   - Format conversion
   - Compression

5. **Monitoring**
   - Request logging
   - Performance metrics
   - Error tracking
   - Security alerts

## Data Transformation and Mapping

### FHIR Transformation Pipeline

```
Source Format
    ↓
Parser (Extract data elements)
    ↓
Mapper (Map to FHIR concepts)
    ↓
Validator (Check FHIR compliance)
    ↓
Enricher (Add metadata, references)
    ↓
Target FHIR Resources
```

**Example Mapping:**

HL7 v2 Message → FHIR Resource:
```
HL7 v2 PID|1||MRN123||Smith^John||19850515
    ↓
FHIR Patient Resource:
{
  "resourceType": "Patient",
  "identifier": [{
    "value": "MRN123"
  }],
  "name": [{
    "family": "Smith",
    "given": ["John"]
  }],
  "birthDate": "1985-05-15"
}
```

**CCDA Section → FHIR Resources:**
```
CCDA Medications Section
    ↓
├─ Multiple MedicationStatement resources
├─ Each linked to Patient
├─ Codes mapped to RxNorm
└─ Dosage information extracted
```

### Semantic Interoperability

**Code System Translation:**
```
ICD-10 Code
    ↓
SNOMED CT Equivalent
    ↓
LOINC (for lab/vital signs)
    ↓
Local EHR Codes

Example:
ICD-10: E11.9 (Type 2 diabetes without complications)
SNOMED: 44054006 (Diabetes mellitus type 2)
RxNorm: Check for diabetes medications
```

**Value Set Harmonization:**
```
Condition Status:
├─ Active (current, ongoing)
├─ Inactive (resolved, not active)
├─ On Hold (temporary pause)
└─ Entered in Error (incorrect entry)

Standardized across all clinical systems
for semantic interoperability
```

## Compliance and Standards Certification

### FHIR Conformance

**Capability Statement:**
```json
{
  "resourceType": "CapabilityStatement",
  "status": "active",
  "date": "2023-11-19",
  "publisher": "Health System",
  "rest": [
    {
      "mode": "server",
      "resource": [
        {
          "type": "Patient",
          "interaction": [
            {"code": "read"},
            {"code": "search-type"}
          ]
        },
        {
          "type": "Condition",
          "interaction": [
            {"code": "read"},
            {"code": "search-type"}
          ]
        }
      ]
    }
  ]
}
```

**USCDI Compliance:**
- Publish list of supported FHIR resources
- Document which USCDI elements implemented
- Demonstrate API functionality
- Provide test data and sandbox

### Certification Programs

**ONC Certification:**
- Certify EHR systems for FHIR APIs
- Require USCDI compliance
- Verify information blocking prevention
- Ongoing surveillance

**HIPAA Compliance:**
- Encryption in transit (TLS 1.2+)
- Encryption at rest (AES-256)
- Access controls and audit logging
- Business Associate agreements

## Performance and Scalability

### API Performance Targets

**Response Times:**
- 90th percentile: <200ms
- 95th percentile: <500ms
- 99th percentile: <1000ms

**Throughput:**
- 100+ requests per second per instance
- Horizontal scaling capability
- Database query optimization

**Availability:**
- 99.9% uptime SLA
- Auto-failover capability
- Load balancing across instances

### Caching Strategies

```
Cache Hierarchy:

L1: Client-side (Browser/Mobile)
├─ Patient demographics (static)
└─ List of problems/medications (semi-static)

L2: CDN (Content Delivery Network)
├─ Patient portal pages
└─ Static resources

L3: Application Cache (Redis)
├─ Frequently accessed patient data
├─ Medication lists
└─ Vital signs summaries

L4: Database Query Cache
├─ Result set caching
└─ Query plan caching

Cache Invalidation:
├─ Time-based (TTL: 1-60 minutes)
├─ Event-based (on data update)
└─ Manual (admin override)
```

## Integration Patterns

### Hub-and-Spoke Model

```
Provider Systems (Spokes)
├─ Hospital EHR
├─ Clinic EHR
├─ Lab System
└─ Pharmacy System
    ↓
Integration Hub
├─ Data aggregation
├─ FHIR transformation
├─ Patient record matching
└─ Query distribution
    ↓
Patient Portal/Apps (Hub)
```

### Event-Driven Integration

```
Provider System Event
(New Lab Result, New Problem, Medication Change)
    ↓
Message Queue (HL7 or FHIR message)
    ↓
Patient Portal Listener
    ↓
Update Patient Record
    ↓
Trigger Patient Notification
```

## Migration Strategies

### Moving from HL7 v2 to FHIR

**Phase 1: Assessment**
- Catalog existing HL7 messages
- Identify FHIR resource equivalents
- Document transformation rules

**Phase 2: Parallel Operation**
- Deploy FHIR API alongside HL7
- Translate incoming HL7 to FHIR
- Route outgoing FHIR to HL7 format

**Phase 3: Client Migration**
- Migrate clients to FHIR API gradually
- Maintain backward compatibility
- Sunsetting of HL7 after all clients migrated

**Timeline:** Typically 12-24 months
