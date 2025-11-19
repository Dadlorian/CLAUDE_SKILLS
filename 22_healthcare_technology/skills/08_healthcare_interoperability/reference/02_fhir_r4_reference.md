# FHIR R4 (Fast Healthcare Interoperability Resources) Reference

## Overview

FHIR is a modern healthcare interoperability standard based on RESTful principles. It uses JSON/XML and defines resources for clinical and administrative data.

## Core Concepts

### Resources
Self-contained units of healthcare information. Each resource has:
- **id** - Unique identifier
- **resourceType** - Type of resource
- **meta** - Metadata (version, last updated, profile)
- **text** - Human-readable summary
- **contained** - Nested resources
- **extension** - Custom extensions

### Resource Categories

| Category | Resources | Purpose |
|----------|-----------|---------|
| Patient | Patient, RelatedPerson | Demographics |
| Clinical | Condition, Procedure, Observation | Clinical findings |
| Medications | Medication, MedicationRequest, MedicationStatement | Drug therapy |
| Care | CarePlan, EpisodeOfCare, Encounter | Care delivery |
| Diagnostics | DiagnosticReport, Specimen, ServiceRequest | Testing |
| Documents | Document, DocumentReference, Composition | Clinical documents |

## Key Resources

### Patient
```json
{
  "resourceType": "Patient",
  "id": "patient-123",
  "identifier": [
    {
      "system": "http://hospital.example.com/mrn",
      "value": "12345"
    }
  ],
  "name": [{"use": "official", "family": "Doe", "given": ["John"]}],
  "birthDate": "1970-01-01",
  "gender": "male"
}
```

### Observation
```json
{
  "resourceType": "Observation",
  "id": "obs-123",
  "status": "final",
  "code": {
    "coding": [{"system": "http://loinc.org", "code": "2345-7", "display": "Glucose"}]
  },
  "subject": {"reference": "Patient/patient-123"},
  "value": {"value": 85, "unit": "mg/dL"}
}
```

### MedicationRequest
```json
{
  "resourceType": "MedicationRequest",
  "id": "medreq-123",
  "status": "active",
  "intent": "order",
  "medicationCodeableConcept": {
    "coding": [{"system": "http://rxnorm.nlm.nih.gov", "code": "342051"}]
  },
  "subject": {"reference": "Patient/patient-123"},
  "dosageInstruction": [{
    "text": "Take 1 tablet twice daily",
    "timing": {"repeat": {"frequency": 2, "period": 1, "periodUnit": "d"}}
  }]
}
```

## RESTful Operations

### CRUD Operations
- **CREATE** - POST /ResourceType
- **READ** - GET /ResourceType/[id]
- **UPDATE** - PUT /ResourceType/[id]
- **DELETE** - DELETE /ResourceType/[id]
- **SEARCH** - GET /ResourceType?search-parameters

### Custom Operations
```
GET /Patient/$everything?patient=123
POST /Claim/$submit
GET /CodeSystem/$lookup?system=...&code=...
```

## Search Parameters

Common patterns:
- **_id** - Resource identifier
- **_lastUpdated** - Last modification time
- **_profile** - Implementation guide profile
- **_count** - Number of results
- **_sort** - Sort order
- **_include** - Include related resources
- **_revinclude** - Reverse include

Example search:
```
GET /Patient?name=doe&birthdate=ge1970-01-01&_count=50
```

## Bundle Operations

### Bundle Types
- **searchset** - Search results
- **history** - Version history
- **searchset** - Search results
- **document** - Immutable document
- **message** - Message delivery
- **transaction** - Atomic operations
- **batch** - Multiple requests
- **batch-response** - Batch responses
- **subscription-notification** - Subscription events

### Transaction Example
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {"resourceType": "Patient", ...},
      "request": {"method": "POST", "url": "Patient"}
    },
    {
      "resource": {"resourceType": "Observation", ...},
      "request": {"method": "POST", "url": "Observation"}
    }
  ]
}
```

## Profiles & Extensions

### Profiles
Specify constraints and requirements on resources:
```json
{
  "resourceType": "Patient",
  "meta": {
    "profile": ["http://example.com/fhir/StructureDefinition/Patient-profile"]
  }
}
```

### Extensions
Add additional data elements:
```json
{
  "url": "http://example.com/fhir/StructureDefinition/race",
  "valueCodeableConcept": {
    "coding": [{"system": "http://hl7.org/fhir/v3/Race", "code": "2106-3"}]
  }
}
```

## Terminology Binding

### Binding Strength
- **required** - Must use codes from valueset
- **extensible** - Should use valueset codes
- **preferred** - Recommended but not required
- **example** - Example codes only

### Code System References
```json
{
  "coding": [
    {
      "system": "http://loinc.org",
      "code": "2345-7",
      "display": "Glucose"
    }
  ]
}
```

## API Response Codes

| Code | Meaning | Notes |
|------|---------|-------|
| 200 | OK | Successful |
| 201 | Created | Resource created |
| 204 | No Content | Successful, no content |
| 400 | Bad Request | Invalid request |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Server Error | Internal error |

## Conformance & Capabilities

### CapabilityStatement
Describes server capabilities:
```json
{
  "resourceType": "CapabilityStatement",
  "rest": [{
    "mode": "server",
    "resource": [{
      "type": "Patient",
      "interaction": [
        {"code": "read"},
        {"code": "search-type"}
      ]
    }]
  }]
}
```

## Pagination

### Page-based
```
GET /Patient?_count=50&_offset=100
```

### Cursor-based
```
GET /Patient?_pageId=abc123
```

### Link-based (Bundle)
```json
{
  "link": [
    {"relation": "self", "url": "..."},
    {"relation": "next", "url": "...?page-id=..."}
  ]
}
```

## Versioning

### Versions Supported
- FHIR R4 (current)
- FHIR R3 (deprecated)
- FHIR R2 (deprecated)
- FHIR DSTU2 (legacy)

### Version Negotation
```
GET /Patient/123
Accept: application/fhir+json; fhirVersion=4.0
```

## Security

### Authentication Methods
- OAuth 2.0
- SMART on FHIR
- API Keys
- Mutual TLS
- SAML

### Encryption
- TLS 1.2+ for transport
- May be signed and encrypted at resource level

## Performance Tips

1. Use _include and _revinclude for related resources
2. Implement server-side pagination
3. Cache frequently accessed resources
4. Use conditional updates
5. Implement bulk data operations

## Common Extensions

- **Patient Race** - http://hl7.org/fhir/us/core/StructureDefinition/us-core-race
- **Patient Ethnicity** - http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity
- **Practitioner Qualification** - http://hl7.org/fhir/StructureDefinition/practitioner-qualification
- **Medication Refills** - http://hl7.org/fhir/StructureDefinition/medication-refills

## Validation

FHIR resources must:
- Have valid resourceType
- Have valid element names
- Have elements with correct cardinality
- Match their profile if specified
- Have valid code bindings
