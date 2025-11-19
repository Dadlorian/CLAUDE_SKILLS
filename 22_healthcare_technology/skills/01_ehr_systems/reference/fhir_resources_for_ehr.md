# FHIR Resources for EHR Systems

## Overview

Fast Healthcare Interoperability Resources (FHIR) is a modern standard for exchanging healthcare information electronically. This reference covers the core FHIR resources used in EHR systems, based on FHIR R4 specification.

## FHIR Fundamentals

### Base URL Structure
```
https://fhir-server.example.com/[base]/[resourceType]/[id]
```

Example:
```
https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Patient/eM8ExaPxLEY8z6j9QKI.Z.Q3
```

### HTTP Methods
- **GET**: Read/Search resources
- **POST**: Create resources
- **PUT**: Update resources
- **PATCH**: Partial update
- **DELETE**: Delete resources

### Common MIME Types
- `application/fhir+json` - FHIR JSON (preferred)
- `application/fhir+xml` - FHIR XML

### Authentication
Most EHR FHIR APIs use OAuth 2.0:
```
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Core Resource Types

### Patient Resource

Represents the patient/individual receiving healthcare services.

#### Key Elements
```json
{
  "resourceType": "Patient",
  "id": "example-patient-123",
  "identifier": [
    {
      "use": "official",
      "type": {
        "coding": [
          {
            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
            "code": "MR",
            "display": "Medical Record Number"
          }
        ]
      },
      "system": "http://hospital.example.org",
      "value": "MRN123456"
    }
  ],
  "active": true,
  "name": [
    {
      "use": "official",
      "family": "Doe",
      "given": ["John", "Robert"],
      "prefix": ["Mr."],
      "suffix": ["Jr."]
    }
  ],
  "telecom": [
    {
      "system": "phone",
      "value": "(555) 555-1234",
      "use": "home"
    },
    {
      "system": "email",
      "value": "john.doe@example.com",
      "use": "home"
    }
  ],
  "gender": "male",
  "birthDate": "1980-01-15",
  "address": [
    {
      "use": "home",
      "type": "both",
      "line": ["123 Main Street", "Apt 4B"],
      "city": "Anytown",
      "state": "CA",
      "postalCode": "12345",
      "country": "USA"
    }
  ],
  "maritalStatus": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
        "code": "M",
        "display": "Married"
      }
    ]
  },
  "contact": [
    {
      "relationship": [
        {
          "coding": [
            {
              "system": "http://terminology.hl7.org/CodeSystem/v2-0131",
              "code": "C",
              "display": "Emergency Contact"
            }
          ]
        }
      ],
      "name": {
        "family": "Doe",
        "given": ["Jane"]
      },
      "telecom": [
        {
          "system": "phone",
          "value": "(555) 555-5678"
        }
      ]
    }
  ],
  "communication": [
    {
      "language": {
        "coding": [
          {
            "system": "urn:ietf:bcp:47",
            "code": "en-US",
            "display": "English (United States)"
          }
        ]
      },
      "preferred": true
    }
  ],
  "generalPractitioner": [
    {
      "reference": "Practitioner/dr-smith-123",
      "display": "Dr. John Smith"
    }
  ]
}
```

#### Common Search Parameters
```
GET /Patient?name=doe
GET /Patient?birthdate=1980-01-15
GET /Patient?identifier=MRN123456
GET /Patient?family=Doe&given=John
GET /Patient?gender=male
GET /Patient?_id=example-patient-123
```

### Practitioner Resource

Represents healthcare providers, clinicians, and staff.

#### Key Elements
```json
{
  "resourceType": "Practitioner",
  "id": "dr-smith-123",
  "identifier": [
    {
      "system": "http://hl7.org/fhir/sid/us-npi",
      "value": "1234567890"
    }
  ],
  "active": true,
  "name": [
    {
      "family": "Smith",
      "given": ["John", "Andrew"],
      "prefix": ["Dr."],
      "suffix": ["MD"]
    }
  ],
  "telecom": [
    {
      "system": "phone",
      "value": "(555) 123-4567",
      "use": "work"
    },
    {
      "system": "email",
      "value": "john.smith@hospital.example.org",
      "use": "work"
    }
  ],
  "address": [
    {
      "use": "work",
      "line": ["456 Hospital Drive"],
      "city": "Anytown",
      "state": "CA",
      "postalCode": "12345"
    }
  ],
  "gender": "male",
  "qualification": [
    {
      "code": {
        "coding": [
          {
            "system": "http://terminology.hl7.org/CodeSystem/v2-0360",
            "code": "MD",
            "display": "Doctor of Medicine"
          }
        ]
      },
      "issuer": {
        "display": "State Medical Board of California"
      }
    }
  ]
}
```

### Encounter Resource

Represents an interaction between a patient and healthcare provider(s).

#### Key Elements
```json
{
  "resourceType": "Encounter",
  "id": "encounter-example-123",
  "identifier": [
    {
      "use": "official",
      "system": "http://hospital.example.org/encounters",
      "value": "VISIT123456"
    }
  ],
  "status": "finished",
  "class": {
    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
    "code": "IMP",
    "display": "inpatient encounter"
  },
  "type": [
    {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "32485007",
          "display": "Hospital admission"
        }
      ]
    }
  ],
  "priority": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActPriority",
        "code": "R",
        "display": "routine"
      }
    ]
  },
  "subject": {
    "reference": "Patient/example-patient-123",
    "display": "John Doe"
  },
  "participant": [
    {
      "type": [
        {
          "coding": [
            {
              "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
              "code": "ATND",
              "display": "attender"
            }
          ]
        }
      ],
      "individual": {
        "reference": "Practitioner/dr-smith-123",
        "display": "Dr. John Smith"
      }
    }
  ],
  "period": {
    "start": "2023-11-19T08:30:00Z",
    "end": "2023-11-21T09:00:00Z"
  },
  "reasonCode": [
    {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "233604007",
          "display": "Pneumonia"
        }
      ]
    }
  ],
  "hospitalization": {
    "admitSource": {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/admit-source",
          "code": "emd",
          "display": "From accident/emergency department"
        }
      ]
    },
    "dischargeDisposition": {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/discharge-disposition",
          "code": "home",
          "display": "Home"
        }
      ]
    }
  },
  "location": [
    {
      "location": {
        "reference": "Location/room-301",
        "display": "Room 301, 3 North"
      },
      "status": "completed",
      "period": {
        "start": "2023-11-19T08:30:00Z",
        "end": "2023-11-21T09:00:00Z"
      }
    }
  ],
  "serviceProvider": {
    "reference": "Organization/main-hospital",
    "display": "Main Hospital"
  }
}
```

#### Encounter Status Values
- `planned` - Planned/scheduled
- `arrived` - Patient arrived
- `triaged` - Patient triaged
- `in-progress` - Encounter in progress
- `onleave` - Encounter temporarily suspended
- `finished` - Encounter completed
- `cancelled` - Encounter cancelled

### Observation Resource

Clinical observations including vital signs, lab results, and assessments.

#### Vital Signs Example
```json
{
  "resourceType": "Observation",
  "id": "blood-pressure-example",
  "status": "final",
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/observation-category",
          "code": "vital-signs",
          "display": "Vital Signs"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "85354-9",
        "display": "Blood pressure panel"
      }
    ]
  },
  "subject": {
    "reference": "Patient/example-patient-123"
  },
  "encounter": {
    "reference": "Encounter/encounter-example-123"
  },
  "effectiveDateTime": "2023-11-19T09:00:00Z",
  "performer": [
    {
      "reference": "Practitioner/nurse-jones-456"
    }
  ],
  "component": [
    {
      "code": {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "8480-6",
            "display": "Systolic blood pressure"
          }
        ]
      },
      "valueQuantity": {
        "value": 120,
        "unit": "mmHg",
        "system": "http://unitsofmeasure.org",
        "code": "mm[Hg]"
      }
    },
    {
      "code": {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "8462-4",
            "display": "Diastolic blood pressure"
          }
        ]
      },
      "valueQuantity": {
        "value": 80,
        "unit": "mmHg",
        "system": "http://unitsofmeasure.org",
        "code": "mm[Hg]"
      }
    }
  ]
}
```

#### Lab Result Example
```json
{
  "resourceType": "Observation",
  "id": "glucose-example",
  "status": "final",
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/observation-category",
          "code": "laboratory",
          "display": "Laboratory"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "2339-0",
        "display": "Glucose [Mass/volume] in Blood"
      }
    ]
  },
  "subject": {
    "reference": "Patient/example-patient-123"
  },
  "effectiveDateTime": "2023-11-19T10:30:00Z",
  "valueQuantity": {
    "value": 95,
    "unit": "mg/dL",
    "system": "http://unitsofmeasure.org",
    "code": "mg/dL"
  },
  "referenceRange": [
    {
      "low": {
        "value": 70,
        "unit": "mg/dL"
      },
      "high": {
        "value": 100,
        "unit": "mg/dL"
      },
      "type": {
        "coding": [
          {
            "system": "http://terminology.hl7.org/CodeSystem/referencerange-meaning",
            "code": "normal",
            "display": "Normal Range"
          }
        ]
      }
    }
  ],
  "interpretation": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
          "code": "N",
          "display": "Normal"
        }
      ]
    }
  ]
}
```

### Condition Resource

Represents diagnoses, problems, or clinical conditions.

```json
{
  "resourceType": "Condition",
  "id": "pneumonia-example",
  "clinicalStatus": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
        "code": "active",
        "display": "Active"
      }
    ]
  },
  "verificationStatus": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
        "code": "confirmed",
        "display": "Confirmed"
      }
    ]
  },
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/condition-category",
          "code": "encounter-diagnosis",
          "display": "Encounter Diagnosis"
        }
      ]
    }
  ],
  "severity": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "24484000",
        "display": "Severe"
      }
    ]
  },
  "code": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "233604007",
        "display": "Pneumonia"
      },
      {
        "system": "http://hl7.org/fhir/sid/icd-10-cm",
        "code": "J18.9",
        "display": "Pneumonia, unspecified organism"
      }
    ],
    "text": "Pneumonia"
  },
  "subject": {
    "reference": "Patient/example-patient-123"
  },
  "encounter": {
    "reference": "Encounter/encounter-example-123"
  },
  "onsetDateTime": "2023-11-17T00:00:00Z",
  "recordedDate": "2023-11-19T08:30:00Z",
  "recorder": {
    "reference": "Practitioner/dr-smith-123"
  },
  "asserter": {
    "reference": "Practitioner/dr-smith-123"
  },
  "evidence": [
    {
      "detail": [
        {
          "reference": "Observation/chest-xray-finding",
          "display": "Chest X-ray showing infiltrate"
        }
      ]
    }
  ]
}
```

### MedicationRequest Resource

Represents medication orders/prescriptions.

```json
{
  "resourceType": "MedicationRequest",
  "id": "medication-example",
  "status": "active",
  "intent": "order",
  "medicationCodeableConcept": {
    "coding": [
      {
        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "code": "1049221",
        "display": "Amoxicillin 500 MG Oral Capsule"
      }
    ],
    "text": "Amoxicillin 500mg capsule"
  },
  "subject": {
    "reference": "Patient/example-patient-123"
  },
  "encounter": {
    "reference": "Encounter/encounter-example-123"
  },
  "authoredOn": "2023-11-19T10:00:00Z",
  "requester": {
    "reference": "Practitioner/dr-smith-123",
    "display": "Dr. John Smith"
  },
  "reasonCode": [
    {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "233604007",
          "display": "Pneumonia"
        }
      ]
    }
  ],
  "dosageInstruction": [
    {
      "sequence": 1,
      "text": "Take 1 capsule by mouth three times daily for 10 days",
      "timing": {
        "repeat": {
          "frequency": 3,
          "period": 1,
          "periodUnit": "d",
          "boundsDuration": {
            "value": 10,
            "unit": "days",
            "system": "http://unitsofmeasure.org",
            "code": "d"
          }
        }
      },
      "route": {
        "coding": [
          {
            "system": "http://snomed.info/sct",
            "code": "26643006",
            "display": "Oral route"
          }
        ]
      },
      "doseAndRate": [
        {
          "type": {
            "coding": [
              {
                "system": "http://terminology.hl7.org/CodeSystem/dose-rate-type",
                "code": "ordered",
                "display": "Ordered"
              }
            ]
          },
          "doseQuantity": {
            "value": 1,
            "unit": "capsule",
            "system": "http://terminology.hl7.org/CodeSystem/v3-orderableDrugForm",
            "code": "CAP"
          }
        }
      ]
    }
  ],
  "dispenseRequest": {
    "numberOfRepeatsAllowed": 0,
    "quantity": {
      "value": 30,
      "unit": "capsule",
      "system": "http://terminology.hl7.org/CodeSystem/v3-orderableDrugForm",
      "code": "CAP"
    },
    "expectedSupplyDuration": {
      "value": 10,
      "unit": "days",
      "system": "http://unitsofmeasure.org",
      "code": "d"
    }
  },
  "substitution": {
    "allowedBoolean": true
  }
}
```

### AllergyIntolerance Resource

Patient allergies and adverse reactions.

```json
{
  "resourceType": "AllergyIntolerance",
  "id": "allergy-penicillin",
  "clinicalStatus": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
        "code": "active",
        "display": "Active"
      }
    ]
  },
  "verificationStatus": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
        "code": "confirmed",
        "display": "Confirmed"
      }
    ]
  },
  "type": "allergy",
  "category": ["medication"],
  "criticality": "high",
  "code": {
    "coding": [
      {
        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "code": "7980",
        "display": "Penicillin"
      }
    ],
    "text": "Penicillin"
  },
  "patient": {
    "reference": "Patient/example-patient-123"
  },
  "onsetDateTime": "2015-05-10",
  "recordedDate": "2015-05-10T14:30:00Z",
  "recorder": {
    "reference": "Practitioner/dr-smith-123"
  },
  "reaction": [
    {
      "substance": {
        "coding": [
          {
            "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
            "code": "7980",
            "display": "Penicillin"
          }
        ]
      },
      "manifestation": [
        {
          "coding": [
            {
              "system": "http://snomed.info/sct",
              "code": "39579001",
              "display": "Anaphylaxis"
            }
          ]
        },
        {
          "coding": [
            {
              "system": "http://snomed.info/sct",
              "code": "271807003",
              "display": "Skin rash"
            }
          ]
        }
      ],
      "severity": "severe",
      "exposureRoute": {
        "coding": [
          {
            "system": "http://snomed.info/sct",
            "code": "26643006",
            "display": "Oral route"
          }
        ]
      }
    }
  ]
}
```

### DiagnosticReport Resource

Results of diagnostic investigations (labs, imaging, pathology).

```json
{
  "resourceType": "DiagnosticReport",
  "id": "lab-panel-example",
  "status": "final",
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
          "code": "LAB",
          "display": "Laboratory"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "24323-8",
        "display": "Comprehensive metabolic 2000 panel - Serum or Plasma"
      }
    ],
    "text": "Comprehensive Metabolic Panel"
  },
  "subject": {
    "reference": "Patient/example-patient-123"
  },
  "encounter": {
    "reference": "Encounter/encounter-example-123"
  },
  "effectiveDateTime": "2023-11-19T10:30:00Z",
  "issued": "2023-11-19T14:30:00Z",
  "performer": [
    {
      "reference": "Organization/lab-services",
      "display": "Hospital Laboratory Services"
    }
  ],
  "result": [
    {
      "reference": "Observation/glucose-example"
    },
    {
      "reference": "Observation/sodium-example"
    },
    {
      "reference": "Observation/potassium-example"
    }
  ],
  "conclusion": "All values within normal limits"
}
```

### Immunization Resource

Vaccination records.

```json
{
  "resourceType": "Immunization",
  "id": "flu-vaccine-example",
  "status": "completed",
  "vaccineCode": {
    "coding": [
      {
        "system": "http://hl7.org/fhir/sid/cvx",
        "code": "141",
        "display": "Influenza, seasonal, injectable"
      }
    ],
    "text": "Seasonal Influenza Vaccine"
  },
  "patient": {
    "reference": "Patient/example-patient-123"
  },
  "encounter": {
    "reference": "Encounter/encounter-example-123"
  },
  "occurrenceDateTime": "2023-11-19T11:00:00Z",
  "recorded": "2023-11-19T11:00:00Z",
  "primarySource": true,
  "location": {
    "reference": "Location/clinic-room-5"
  },
  "lotNumber": "FL2023-001",
  "expirationDate": "2024-06-30",
  "site": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "72098002",
        "display": "Entire left upper arm"
      }
    ]
  },
  "route": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/v3-RouteOfAdministration",
        "code": "IM",
        "display": "Intramuscular"
      }
    ]
  },
  "doseQuantity": {
    "value": 0.5,
    "unit": "mL",
    "system": "http://unitsofmeasure.org",
    "code": "mL"
  },
  "performer": [
    {
      "function": {
        "coding": [
          {
            "system": "http://terminology.hl7.org/CodeSystem/v2-0443",
            "code": "AP",
            "display": "Administering Provider"
          }
        ]
      },
      "actor": {
        "reference": "Practitioner/nurse-jones-456"
      }
    }
  ]
}
```

### Procedure Resource

Clinical procedures performed on patients.

```json
{
  "resourceType": "Procedure",
  "id": "appendectomy-example",
  "status": "completed",
  "category": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "387713003",
        "display": "Surgical procedure"
      }
    ]
  },
  "code": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "80146002",
        "display": "Appendectomy"
      },
      {
        "system": "http://www.ama-assn.org/go/cpt",
        "code": "44950",
        "display": "Appendectomy"
      }
    ],
    "text": "Appendectomy"
  },
  "subject": {
    "reference": "Patient/example-patient-123"
  },
  "encounter": {
    "reference": "Encounter/encounter-example-123"
  },
  "performedPeriod": {
    "start": "2023-11-20T14:00:00Z",
    "end": "2023-11-20T16:30:00Z"
  },
  "performer": [
    {
      "function": {
        "coding": [
          {
            "system": "http://snomed.info/sct",
            "code": "304292004",
            "display": "Surgeon"
          }
        ]
      },
      "actor": {
        "reference": "Practitioner/surgeon-johnson-789",
        "display": "Dr. Sarah Johnson"
      }
    }
  ],
  "location": {
    "reference": "Location/operating-room-2"
  },
  "reasonCode": [
    {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "74400008",
          "display": "Appendicitis"
        }
      ]
    }
  ],
  "bodySite": [
    {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "66754008",
          "display": "Appendix structure"
        }
      ]
    }
  ],
  "outcome": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "385669000",
        "display": "Successful"
      }
    ]
  }
}
```

## FHIR Search Patterns

### Basic Search
```
GET /Patient?name=doe
GET /Observation?code=http://loinc.org|2339-0
GET /MedicationRequest?patient=Patient/123
```

### Date Range Search
```
GET /Observation?date=ge2023-01-01&date=le2023-12-31
GET /Encounter?date=ge2023-11-01
```

### Chained Parameters
```
GET /Observation?patient.name=doe
GET /DiagnosticReport?subject:Patient.identifier=MRN123456
```

### Reverse Chaining
```
GET /Patient?_has:Observation:patient:code=http://loinc.org|2339-0
```

### Includes
```
GET /MedicationRequest?patient=Patient/123&_include=MedicationRequest:patient
GET /Encounter?_id=123&_include=Encounter:patient&_include=Encounter:practitioner
```

### Result Limiting
```
GET /Patient?_count=10
GET /Observation?_count=50&_offset=100
```

## Common Code Systems

### LOINC (Logical Observation Identifiers Names and Codes)
```
http://loinc.org
```
Used for: Laboratory tests, vital signs, clinical observations

### SNOMED CT (Systematized Nomenclature of Medicine - Clinical Terms)
```
http://snomed.info/sct
```
Used for: Clinical findings, procedures, body structures

### RxNorm
```
http://www.nlm.nih.gov/research/umls/rxnorm
```
Used for: Medications and drug products

### ICD-10-CM (International Classification of Diseases)
```
http://hl7.org/fhir/sid/icd-10-cm
```
Used for: Diagnoses

### CPT (Current Procedural Terminology)
```
http://www.ama-assn.org/go/cpt
```
Used for: Procedures (billing)

### CVX (Vaccine Codes)
```
http://hl7.org/fhir/sid/cvx
```
Used for: Vaccines

## Bundle Resource

Bundles contain multiple resources in a single request/response.

### Transaction Bundle (Creating Multiple Resources)
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "fullUrl": "urn:uuid:patient-temp-id",
      "resource": {
        "resourceType": "Patient",
        "name": [{
          "family": "Doe",
          "given": ["John"]
        }]
      },
      "request": {
        "method": "POST",
        "url": "Patient"
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "status": "final",
        "code": {
          "coding": [{
            "system": "http://loinc.org",
            "code": "8480-6"
          }]
        },
        "subject": {
          "reference": "urn:uuid:patient-temp-id"
        },
        "valueQuantity": {
          "value": 120,
          "unit": "mmHg"
        }
      },
      "request": {
        "method": "POST",
        "url": "Observation"
      }
    }
  ]
}
```

### Search Results Bundle
```json
{
  "resourceType": "Bundle",
  "type": "searchset",
  "total": 2,
  "link": [
    {
      "relation": "self",
      "url": "https://fhir.example.com/Patient?name=doe"
    }
  ],
  "entry": [
    {
      "fullUrl": "https://fhir.example.com/Patient/123",
      "resource": {
        "resourceType": "Patient",
        "id": "123"
      }
    }
  ]
}
```

## Best Practices

### Resource Design
1. Use standardized code systems (LOINC, SNOMED CT, RxNorm)
2. Include both coded values and text representations
3. Populate key search parameters
4. Use references for related resources
5. Include narrative text for human readability

### API Implementation
1. Implement proper OAuth 2.0 authentication
2. Support pagination for large result sets
3. Implement rate limiting
4. Use conditional create/update operations
5. Support common search parameters
6. Return OperationOutcome for errors

### Data Quality
1. Validate resources against FHIR profiles
2. Use appropriate value sets for coded elements
3. Include provenance information
4. Maintain referential integrity
5. Support resource versioning

### Security
1. Encrypt data in transit (TLS 1.2+)
2. Implement SMART on FHIR for patient context
3. Use scopes to limit access
4. Audit all API access
5. Support patient consent directives

## References

- **FHIR R4 Specification**: http://hl7.org/fhir/R4/
- **FHIR Resource Index**: http://hl7.org/fhir/R4/resourcelist.html
- **US Core Implementation Guide**: http://hl7.org/fhir/us/core/
- **SMART on FHIR**: https://smarthealthit.org/
- **Epic FHIR**: https://fhir.epic.com/
- **Cerner FHIR**: https://fhir.cerner.com/

---

**Document Version**: 1.0
**Last Updated**: November 2024
**Author**: Healthcare Technology Team
**Classification**: Public - Educational Use
