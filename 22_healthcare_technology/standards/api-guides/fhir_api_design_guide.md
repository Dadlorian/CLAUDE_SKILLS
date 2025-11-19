# FHIR API Design Guide

**Version**: 4.0.1
**Last Updated**: 2025-11-19
**Status**: Production Ready
**Standards Compliance**: FHIR R4, HL7v3, ISO 27001, HIPAA

---

## Executive Summary

This guide provides comprehensive standards and best practices for designing, implementing, and maintaining FHIR (Fast Healthcare Interoperability Resources) APIs. It establishes baseline requirements for all healthcare API implementations across the organization.

---

## 1. FHIR Resource Implementation Standards

### 1.1 REST API Compliance

**Mandatory Requirements:**
- All APIs MUST implement RESTful principles adhering to FHIR R4 specification
- Support HTTP/1.1 and HTTP/2 protocols
- Implement proper HTTP status codes per RFC 7231
- Use application/fhir+json (preferred) or application/fhir+xml (legacy support)
- Mandatory content negotiation via Accept headers

**Required Response Codes:**
```
200 OK             - Successful GET/PUT/PATCH
201 Created        - Successful POST with new resource
204 No Content     - Successful DELETE
400 Bad Request    - Invalid request format/parameters
401 Unauthorized   - Authentication required
403 Forbidden      - Insufficient permissions
404 Not Found      - Resource doesn't exist
409 Conflict       - Duplicate resource attempt
422 Unprocessable  - Validation failure
429 Rate Limited   - Quota exceeded
500 Server Error   - Internal server error
503 Unavailable    - Service temporarily unavailable
```

### 1.2 FHIR Resource Profiles

**Standard Profile Requirements:**
- Must extend base FHIR R4 resources
- Must validate against approved Implementation Guides (IGs)
- Must be registered in organizational profile registry
- Must document any must-support elements clearly
- Must implement cardinality constraints

**Required Profiles:**
- Patient (Core Patient Profile)
- Observation (Laboratory, Vital Signs)
- Medication (Drug Formulary)
- Condition (Clinical Diagnosis)
- Encounter (Clinical Visit)
- Practitioner (Provider Directory)
- Organization (Healthcare Organization)
- MedicationAdministration (Medication Administration)
- Immunization (Immunization Records)

**Profile Definition Template:**
```xml
<StructureDefinition>
  <url>https://organization.health/fhir/StructureDefinition/[ResourceType]</url>
  <version>1.0.0</version>
  <title>[Resource] Profile</title>
  <publisher>Healthcare Organization</publisher>
  <status>active</status>
  <experimental>false</experimental>
  <baseDefinition>http://hl7.org/fhir/StructureDefinition/[BaseResource]</baseDefinition>
  <kind>resource</kind>
  <abstract>false</abstract>
</StructureDefinition>
```

### 1.3 Search Parameter Standards

**Mandatory Search Capabilities:**
- All GET operations must support standard FHIR search parameters
- Implement _count parameter (default: 100, max: 1000)
- Implement _offset parameter for pagination
- Implement _sort parameter with security constraints
- Implement _elements for partial resource requests
- Support _lastUpdated for change detection

**Search Parameter Definition:**
```
Parameter Format:   [parameter]=[value]
Date Range:         param=ge2023-01-01&param=le2023-12-31
Text Search:        name:contains=text OR name:exact=text
Reference:          subject=Patient/123 OR subject=123
Token:              status=active OR status=system|code
Composite:          birthdate=ge2000-01-01&gender=female
```

**Performance Requirements:**
- Search results must return within 5 seconds for 10,000+ records
- Index critical search parameters: id, identifier, status, date
- Implement cursor-based pagination for large result sets
- Cache search results for 5 minutes minimum

---

## 2. API Authentication & Authorization

### 2.1 Authentication Methods

**Required Implementation:**
- OAuth 2.0 with Bearer token (RFC 6750)
- OpenID Connect for user identity
- Mutual TLS (mTLS) for service-to-service
- API Key support for legacy systems (deprecated pathway)

**Token Requirements:**
```
Token Format:       JWT (RS256 signature minimum)
Expiration:         15-60 minutes (short-lived)
Refresh Token:      7-90 days
Scope Format:       [resource]/[operation]
  Examples:         Patient/read
                    Observation/write
                    Encounter/read.search-type
                    *.read
```

### 2.2 Authorization Patterns

**Scopes Matrix:**
```
Patient Data:
  patient/Patient.read         - Read patient records (same patient)
  patient/Patient.write        - Write patient records (same patient)
  user/Patient.read            - Read any patient (authorized user)
  user/Patient.write           - Write any patient (authorized user)
  system/Patient.read          - System read access

Clinical Data:
  user/Observation.read        - Read observations
  user/Observation.write       - Write observations
  user/MedicationAdministration.read
  user/MedicationAdministration.write

Administrative:
  system/Organization.read     - System organization access
  system/Practitioner.read     - System practitioner access
```

**Role-Based Access Control (RBAC):**
```
Physician Role:
  - Patient/read, Patient/write (all patients)
  - Observation/read, Observation/write
  - Medication/read, Medication/write
  - Encounter/read, Encounter/write

Nurse Role:
  - Patient/read (assigned patients)
  - Observation/read, Observation/write
  - MedicationAdministration/read, MedicationAdministration/write

Admin Role:
  - *.read, *.write (all resources)
  - Organization/read, Organization/write
```

---

## 3. Data Validation & Consistency

### 3.1 Validation Framework

**Validation Layers:**
1. **Format Validation**: JSON structure, XML wellformedness
2. **Type Validation**: Data types match FHIR specification
3. **Profile Validation**: Resource conforms to StructureDefinition
4. **Business Logic**: Cross-field validation, invariants
5. **Clinical Validation**: Domain-specific rules

**Required Validation Tools:**
- FHIR Validator (hapi-fhir-validator)
- Custom business rule engine
- Terminology validation against SNOMED CT, ICD-10, RxNorm

**Validation Response:**
```json
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error",
      "code": "invalid",
      "details": {
        "text": "Patient birthDate must be in past"
      },
      "expression": ["Patient.birthDate"]
    }
  ]
}
```

### 3.2 Data Quality Standards

**Mandatory Data Quality Rules:**
- Required fields: id, status, meta (resourceType, profile, lastUpdated)
- Reference integrity: All references must resolve to existing resources
- Identifier uniqueness: Duplicate identifiers must be managed
- Date consistency: Dates must follow logical order (admission < discharge)
- Coding requirements: Use standard terminologies (SNOMED CT, ICD-10)

---

## 4. Error Handling & Resilience

### 4.1 Error Response Standards

**Required Error Structure:**
```json
{
  "resourceType": "OperationOutcome",
  "id": "error-uuid",
  "meta": {
    "lastUpdated": "2025-11-19T10:30:00Z"
  },
  "issue": [
    {
      "severity": "error|warning|information",
      "code": "business-rule|conflict|duplicate|not-found|processing",
      "details": {
        "coding": [
          {
            "system": "http://hl7.org/fhir/operation-outcome",
            "code": "MSG_AUTH_FAILED",
            "display": "Authentication failed"
          }
        ],
        "text": "Detailed error message with remediation steps"
      },
      "expression": ["Patient.birthDate"],
      "diagnostics": "Additional technical details"
    }
  ]
}
```

### 4.2 Resilience Requirements

**Retry Strategy:**
- Implement exponential backoff: 1s, 2s, 4s, 8s (max 5 retries)
- Idempotency: All POST/PUT operations must be idempotent
- Implement Idempotency-Key header (UUID v4)
- Circuit breaker pattern for downstream service failures
- Graceful degradation when secondary services unavailable

**Timeout Requirements:**
```
API Response:     5 seconds
Database Query:   2 seconds
External Service: 3 seconds
Batch Operations: 30 seconds
```

---

## 5. Performance & Scalability

### 5.1 Performance Requirements

**API Performance Targets:**
```
Operation Type          Target Response Time    Max Response Time
GET (single)           50ms                    500ms
GET (search, 100)      200ms                   2s
POST (create)          100ms                   1s
PUT (update)           100ms                   1s
PATCH (partial)        100ms                   1s
DELETE                 50ms                    500ms
Batch operation        5s                      30s
```

### 5.2 Pagination Strategy

**Required Pagination Implementation:**
```
Query:    GET /Patient?_count=50&_offset=0
Response:
{
  "resourceType": "Bundle",
  "type": "searchset",
  "total": 1250,
  "link": [
    {
      "relation": "self",
      "url": "/Patient?_count=50&_offset=0"
    },
    {
      "relation": "next",
      "url": "/Patient?_count=50&_offset=50"
    },
    {
      "relation": "previous",
      "url": "/Patient?_count=50&_offset=0"
    }
  ],
  "entry": [...]
}
```

### 5.3 Caching Strategy

**Caching Guidelines:**
- Cache search results: 5 minutes (non-sensitive)
- Cache reference lookups: 15 minutes
- Cache terminology: 24 hours
- Cache organizational data: 1 hour
- Never cache patient-specific clinical data
- Use ETag headers for cache validation

---

## 6. Security Requirements

### 6.1 Data Protection Standards

**Encryption Requirements:**
- TLS 1.2+ for all API traffic (TLS 1.3 preferred)
- AES-256-GCM for data at rest
- Encrypt PII in database: SSN, MRN, DOB, phone
- Implement key rotation every 90 days
- HSM-backed key management

**PII Data Classification:**
```
Highly Sensitive:     SSN, passwords, credit cards (encryption mandatory)
Sensitive:            MRN, DOB, phone, address (encryption/access control)
Internal:             Organization name, general location (access control)
Public:               Generic educational content (no restriction)
```

### 6.2 Audit & Compliance

**Audit Logging Requirements:**
```json
{
  "timestamp": "2025-11-19T10:30:00Z",
  "eventType": "FHIR_RESOURCE_ACCESS",
  "userId": "user-uuid",
  "organization": "org-uuid",
  "resourceType": "Patient",
  "resourceId": "patient-uuid",
  "action": "READ|WRITE|DELETE|SEARCH",
  "status": "SUCCESS|FAILURE",
  "ipAddress": "192.168.1.1",
  "userAgent": "application/fhir-client-v2.1",
  "securityLabel": "L|M|H",
  "changeDetails": "what changed"
}
```

**Retention Requirements:**
- Audit logs: 7 years (regulatory requirement)
- Access logs: 1 year
- Error logs: 90 days
- Immutable storage with tamper detection

---

## 7. API Versioning & Deployment

### 7.1 Versioning Strategy

**Semantic Versioning (SemVer):**
```
Format:               /v{MAJOR}.{MINOR}.{PATCH}
Example:              /v2.1.3

Major Version:        Breaking changes (new endpoint structure)
Minor Version:        Backward-compatible enhancements
Patch Version:        Bug fixes and security patches

Deprecation Timeline:
  - Announce: 6 months before removal
  - Sunset:   12 months before removal
  - Remove:   After deprecation period
```

### 7.2 Deployment Standards

**Required Checks Before Production:**
- All unit tests passing (minimum 80% code coverage)
- Integration tests with all dependencies
- Security scanning (OWASP Top 10)
- Performance testing (load test at 2x expected traffic)
- Penetration testing (quarterly)
- FHIR validation compliance
- Documentation complete and reviewed

---

## 8. Monitoring & Observability

### 8.1 Metrics Collection

**Required Metrics:**
```
Performance:
  - API response time (p50, p95, p99)
  - Request throughput (requests/second)
  - Error rate (errors/total requests)
  - Database query duration
  - Cache hit ratio

Business:
  - Resource create/update/delete counts
  - Search operation volume
  - API usage by client
  - Top search parameters

Reliability:
  - Service availability (99.5%+ SLA)
  - Dependency health
  - Queue depth (if applicable)
  - Circuit breaker state
```

### 8.2 Alerting Thresholds

```
Critical:  Response time > 5s (immediate escalation)
           Error rate > 5% (immediate escalation)
           API down > 5 minutes (page on-call)

Warning:   Response time > 2s (review capacity)
           Error rate > 1% (investigate root cause)
           Database slow queries (optimize)

Info:      New API version deployed
           Deprecation deadline approaching
           Cache performance degradation
```

---

## 9. Documentation Standards

**Required Documentation:**
- OpenAPI/Swagger specification (maintained in sync)
- StructureDefinition for all custom profiles
- Implementation guides for non-standard use cases
- Example requests/responses for all operations
- Change log for all versions
- Security considerations document
- Data governance and retention policy
- Troubleshooting guide for common issues

---

## 10. Governance & Review

**Quarterly API Review Checklist:**
- [ ] Security assessment completed
- [ ] Performance metrics within SLA
- [ ] No critical vulnerabilities outstanding
- [ ] Documentation current and accurate
- [ ] Deprecated versions removed on schedule
- [ ] Compliance audit passed
- [ ] Client feedback addressed
- [ ] Incident post-mortems completed

---

## Appendix: Common FHIR Operations

**Standard Operations:**
```
GET /Patient/123                     - Read patient
GET /Patient?identifier=MRN|12345    - Search by identifier
GET /Patient?name=John&gender=male   - Search by criteria
POST /Patient                        - Create new patient
PUT /Patient/123                     - Replace patient
PATCH /Patient/123                   - Partial update
DELETE /Patient/123                  - Delete patient
GET /Patient/$search                 - Custom search operation
POST /Patient/$validate              - Validate patient data
```

---

**Contact**: Healthcare API Standards Committee
**Last Reviewed**: 2025-11-19
