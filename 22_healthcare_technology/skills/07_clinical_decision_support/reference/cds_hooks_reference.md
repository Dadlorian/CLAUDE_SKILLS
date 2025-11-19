# CDS Hooks Reference

## Overview
CDS Hooks is an HL7 standard specification for integrating clinical decision support (CDS) services with electronic health record (EHR) systems using a service-oriented architecture.

## Core Concepts

### Service Discovery
EHR systems discover available CDS services through a discovery endpoint:
```
GET {baseUrl}/cds-services
```

Returns array of available services with metadata.

### Hook Types

#### patient-view
- **When**: Opening a patient's chart
- **Context**: Patient ID
- **Use Cases**: Patient-specific alerts, preventive care reminders, care gaps

#### medication-prescribe
- **When**: Provider is prescribing medications
- **Context**: Patient ID, medication orders (draft)
- **Use Cases**: Drug-drug interactions, allergy checking, duplicate therapy

#### order-select
- **When**: Clinician selects order from catalog
- **Context**: Patient ID, draft orders
- **Use Cases**: Appropriateness criteria, cost transparency, alternatives

#### order-sign
- **When**: Clinician signing/finalizing orders
- **Context**: Patient ID, orders being signed
- **Use Cases**: Final safety checks, required documentation

#### encounter-start
- **When**: Starting patient encounter
- **Context**: Patient ID, encounter ID
- **Use Cases**: Clinical pathway initiation, documentation reminders

#### encounter-discharge
- **When**: Discharging patient
- **Context**: Patient ID, encounter ID
- **Use Cases**: Discharge planning, medication reconciliation, follow-up

## Request Format

### Basic Structure
```json
{
  "hook": "medication-prescribe",
  "hookInstance": "unique-instance-id",
  "fhirServer": "https://fhir.example.org",
  "fhirAuthorization": {
    "access_token": "bearer-token",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": "patient/*.read",
    "subject": "Practitioner/123"
  },
  "context": {
    "patientId": "Patient/123",
    "encounterId": "Encounter/456",
    "medications": [
      {
        "resourceType": "MedicationRequest",
        "medicationCodeableConcept": {
          "coding": [{
            "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
            "code": "1049502",
            "display": "Warfarin Sodium 5 MG Oral Tablet"
          }]
        }
      }
    ]
  },
  "prefetch": {
    "patient": {
      "resourceType": "Patient",
      "id": "123",
      "name": [{"family": "Smith", "given": ["John"]}]
    }
  }
}
```

## Response Format

### Card Structure
```json
{
  "cards": [
    {
      "uuid": "card-unique-id",
      "summary": "Major drug-drug interaction detected",
      "detail": "Warfarin and aspirin increase bleeding risk by 2-3x. Consider gastroprotection or alternative anticoagulation.",
      "indicator": "critical",
      "source": {
        "label": "First DataBank",
        "url": "https://fdb.com/interaction/12345"
      },
      "suggestions": [
        {
          "label": "Use apixaban instead",
          "uuid": "suggestion-1",
          "actions": [
            {
              "type": "delete",
              "description": "Remove warfarin order",
              "resourceId": ["MedicationRequest/789"]
            },
            {
              "type": "create",
              "description": "Order apixaban 5mg BID",
              "resource": {
                "resourceType": "MedicationRequest",
                "medicationCodeableConcept": {
                  "coding": [{
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": "1364430",
                    "display": "apixaban 5 MG Oral Tablet"
                  }]
                }
              }
            }
          ]
        },
        {
          "label": "Add PPI for gastroprotection",
          "uuid": "suggestion-2",
          "actions": [
            {
              "type": "create",
              "description": "Order omeprazole 20mg daily",
              "resource": {
                "resourceType": "MedicationRequest",
                "medicationCodeableConcept": {
                  "coding": [{
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": "861634",
                    "display": "omeprazole 20 MG Delayed Release Oral Capsule"
                  }]
                }
              }
            }
          ]
        }
      ],
      "links": [
        {
          "label": "Read interaction monograph",
          "url": "https://fdb.com/monograph/warfarin-aspirin",
          "type": "absolute"
        },
        {
          "label": "Calculate HAS-BLED score",
          "url": "https://smart.example.org/launch?iss=...",
          "type": "smart",
          "appContext": "{\"patient\": \"123\"}"
        }
      ],
      "overrideReasons": [
        {
          "code": "patient-preference",
          "display": "Patient preference"
        },
        {
          "code": "benefit-outweighs-risk",
          "display": "Benefit outweighs risk"
        },
        {
          "code": "close-monitoring",
          "display": "Patient will be closely monitored"
        }
      ]
    }
  ]
}
```

## Indicator Levels

### info
- Informational, non-actionable
- Background/context information
- Educational content

### warning
- Potential issue requiring awareness
- Suggested best practice
- Quality improvement opportunity

### critical
- Serious safety concern
- Requires immediate attention
- May block workflow (hard stop)

## Prefetch

### Purpose
Reduce FHIR server queries by sending anticipated data with hook request.

### Template Format
```json
{
  "id": "cds-service-123",
  "prefetch": {
    "patient": "Patient/{{context.patientId}}",
    "conditions": "Condition?patient={{context.patientId}}",
    "medications": "MedicationRequest?patient={{context.patientId}}&status=active",
    "allergies": "AllergyIntolerance?patient={{context.patientId}}&clinical-status=active",
    "labs": "Observation?patient={{context.patientId}}&category=laboratory&_sort=-date&_count=10"
  }
}
```

## FHIR Authorization

### OAuth 2.0 Token
EHR provides access token for CDS service to query FHIR API:
```json
{
  "fhirAuthorization": {
    "access_token": "eyJhbGci...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": "patient/*.read",
    "subject": "Practitioner/123"
  }
}
```

### Scopes
- `patient/*.read` - Read all patient resources
- `patient/Observation.read` - Read observations only
- `user/Practitioner.read` - Read practitioner info
- `launch/patient` - Patient-specific context

## System Actions

### Action Types

#### create
Add new FHIR resource (order, medication, etc.)

#### update
Modify existing FHIR resource

#### delete
Remove FHIR resource (cancel order)

## Security Considerations

### Authentication
- Mutual TLS recommended
- Bearer token authentication
- IP allowlisting

### Authorization
- Service-level authorization
- User/role-based access
- Patient consent enforcement

### Data Protection
- HTTPS required
- PHI encryption in transit
- Audit logging of all requests

## Performance Requirements

### Response Time
- < 3 seconds for synchronous hooks
- < 5 seconds absolute maximum
- Timeout handling in EHR

### Scalability
- Handle 1000+ concurrent requests
- Horizontal scaling support
- Caching strategies

## Analytics & Feedback

### Feedback Endpoint
```
POST {baseUrl}/cds-services/{serviceId}/feedback
```

Payload:
```json
{
  "cardUuid": "card-123",
  "outcomeTimestamp": "2023-11-19T10:30:00Z",
  "override": {
    "reason": {
      "code": "benefit-outweighs-risk",
      "display": "Benefit outweighs risk"
    },
    "userComment": "Patient tolerates both meds well"
  },
  "acceptedSuggestions": ["suggestion-2"]
}
```

## Best Practices

### Card Design
1. **Concise Summary**: < 140 characters
2. **Actionable Detail**: Clear clinical guidance
3. **Evidence Links**: Link to source guidelines
4. **Appropriate Severity**: Don't overuse "critical"

### Performance
1. **Optimize Prefetch**: Request only needed data
2. **Cache Reference Data**: Drug databases, guidelines
3. **Async Processing**: Use queues for slow operations
4. **Timeouts**: Handle EHR timeouts gracefully

### Clinical Integration
1. **Workflow-Aware**: Integrate at right time
2. **Override Options**: Always allow clinical judgment
3. **Feedback Loop**: Track outcomes and overrides
4. **Iteration**: Refine based on real-world use

## Version History
- **1.0**: Initial specification (2019)
- **2.0**: Added system actions, enhanced prefetch (2023)

## Resources
- Specification: https://cds-hooks.org
- Sandbox: https://sandbox.cds-hooks.org
- Registry: https://cds-hooks.org/registry
