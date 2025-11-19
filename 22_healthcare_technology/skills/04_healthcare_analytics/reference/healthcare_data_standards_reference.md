# Healthcare Data Standards Reference

## Clinical Terminologies

### ICD-10-CM (International Classification of Diseases, 10th Revision, Clinical Modification)

**Purpose**: Diagnosis coding for billing and clinical documentation (US)
**Maintained by**: CDC and NCHS
**Structure**: Alphanumeric codes, 3-7 characters

**Format**:
```
E11.9    - Category (E11 = Type 2 diabetes)
E11.65   - Subcategory (diabetes with hyperglycemia)
E11.641  - Full code (Type 2 diabetes with hypoglycemia with coma)
```

**Code Categories**:
- A00-B99: Infectious diseases
- C00-D49: Neoplasms
- E00-E89: Endocrine, nutritional, metabolic
- I00-I99: Circulatory system
- J00-J99: Respiratory system
- ...and more

**Laterality**: 1 = right, 2 = left, 3 = bilateral, 9 = unspecified

**Example Codes**:
```
I21.01 - ST elevation myocardial infarction involving left main coronary artery
N18.3  - Chronic kidney disease, stage 3
F17.210 - Nicotine dependence, cigarettes, uncomplicated
Z79.4  - Long-term use of insulin
```

### ICD-10-PCS (Procedure Coding System)

**Purpose**: Inpatient hospital procedure coding (US)
**Structure**: 7-character alphanumeric codes

**Code Structure**:
```
Position 1: Section (0 = Medical/Surgical)
Position 2: Body System (5 = Upper Arteries)
Position 3: Root Operation (9 = Drainage)
Position 4: Body Part (1 = Celiac Artery)
Position 5: Approach (3 = Percutaneous)
Position 6: Device (Z = No Device)
Position 7: Qualifier (Z = No Qualifier)

Example: 0259 3ZZ - Drainage of celiac artery, percutaneous approach
```

### CPT (Current Procedural Terminology)

**Purpose**: Procedure and service coding for billing (US)
**Maintained by**: AMA (American Medical Association)
**Structure**: 5-digit numeric codes

**Categories**:
```
Category I: 00100-99499 (Procedures and services)
  - Evaluation & Management (E&M): 99201-99499
  - Anesthesia: 00100-01999
  - Surgery: 10000-69990
  - Radiology: 70000-79999
  - Pathology & Lab: 80000-89999
  - Medicine: 90000-99199

Category II: Performance measurement codes (optional)

Category III: Temporary codes for emerging technology
```

**E&M Codes (Common)**:
```
99213 - Office visit, established patient, level 3
99214 - Office visit, established patient, level 4
99285 - Emergency department visit, level 5 (high complexity)
99221 - Initial hospital care, level 1
```

**Modifiers**: 2-character codes that provide additional information
```
25 - Significant, separately identifiable E&M service
59 - Distinct procedural service
LT - Left side
RT - Right side
```

### SNOMED CT (Systematized Nomenclature of Medicine - Clinical Terms)

**Purpose**: Comprehensive clinical terminology for EHRs
**Maintained by**: SNOMED International
**Structure**: Concept ID + Description + Relationships

**Concept Types**:
- Clinical findings
- Procedures
- Body structures
- Organisms
- Substances
- Pharmaceutical products

**Example**:
```
Concept ID: 44054006
FSN (Fully Specified Name): Diabetes mellitus type 2 (disorder)
Preferred Term: Type 2 diabetes mellitus
Synonyms: NIDDM, Adult onset diabetes

Relationships:
- Is a: Diabetes mellitus (disorder)
- Finding site: Structure of endocrine system
- Associated morphology: Endocrine disorder
```

**SNOMED CT Hierarchy**:
```
Disorder
  └─ Diabetes mellitus
      ├─ Type 1 diabetes mellitus
      ├─ Type 2 diabetes mellitus
      │   ├─ Type 2 diabetes with ketoacidosis
      │   ├─ Type 2 diabetes with renal complications
      │   └─ Type 2 diabetes with ophthalmic complications
      └─ Gestational diabetes mellitus
```

### LOINC (Logical Observation Identifiers Names and Codes)

**Purpose**: Laboratory and clinical observations
**Maintained by**: Regenstrief Institute
**Structure**: 6-part naming convention

**LOINC Parts**:
```
Component: What is measured (e.g., Glucose, Hemoglobin A1c)
Property: Characteristic (e.g., Mass, Substance)
Time: When (e.g., Point in time, 24 hour)
System: Sample type (e.g., Serum, Blood, Urine)
Scale: How measured (e.g., Quantitative, Ordinal)
Method: Measurement method (optional)
```

**Example LOINC Codes**:
```
4548-4: Hemoglobin A1c/Hemoglobin.total in Blood
  Component: Hemoglobin A1c
  Property: Mass Fraction
  Time: Point in time
  System: Blood
  Scale: Quantitative

2345-7: Glucose [Mass/volume] in Serum or Plasma
2160-0: Creatinine [Mass/volume] in Serum or Plasma
33914-3: Glomerular filtration rate/1.73 sq M.predicted
8480-6: Systolic blood pressure
8867-4: Heart rate
```

### RxNorm

**Purpose**: Normalized medication terminology
**Maintained by**: NLM (National Library of Medicine)
**Structure**: Hierarchical drug names

**RxNorm Hierarchy**:
```
Ingredient (generic drug)
  └─ Clinical Drug (strength + dose form)
      ├─ Branded Drug (brand name version)
      └─ Clinical Drug Component (ingredient + strength)

Example:
Metformin (Ingredient)
  └─ Metformin 500 MG Oral Tablet (Clinical Drug)
      ├─ Glucophage 500 MG Oral Tablet (Branded Drug)
      └─ Metformin 500 MG (Clinical Drug Component)
```

**Example RxNorm Concepts**:
```
RxCUI 6809: Metformin (Ingredient)
RxCUI 860975: Metformin 500 MG Oral Tablet
RxCUI 861007: Metformin 1000 MG Oral Tablet
RxCUI 105377: insulin glargine (Ingredient)
RxCUI 261551: insulin glargine 100 UNT/ML Injectable Solution
```

**Relationships**:
- has_ingredient
- has_dose_form
- has_strength
- tradename_of

### NDC (National Drug Code)

**Purpose**: Unique drug product identifier (US)
**Maintained by**: FDA
**Structure**: 10-11 digit code

**Format**:
```
XXXXX-YYYY-ZZ
Labeler-Product-Package

Example: 00002-8215-01
  00002 = Eli Lilly (Labeler)
  8215 = Humalog 100 units/mL (Product)
  01 = 10 mL vial (Package)
```

**Mapping**: NDC → RxNorm (for semantic interoperability)

## Health Information Exchange Standards

### HL7 v2.x

**Purpose**: Clinical and administrative data exchange
**Format**: Pipe-delimited messages
**Common Message Types**:
- ADT (Admit, Discharge, Transfer)
- ORM (Order)
- ORU (Observation Result)
- SIU (Scheduling)

**Example ADT Message (Simplified)**:
```
MSH|^~\&|SENDING_APP|SENDING_FACILITY|RECEIVING_APP|RECEIVING_FACILITY|20231015120000||ADT^A01|MSG00001|P|2.5
EVN|A01|20231015120000
PID|1||123456^^^MRN||DOE^JOHN^A||19650315|M|||123 MAIN ST^^ANYTOWN^CA^12345
PV1|1|I|4W^401^01^MAIN HOSPITAL||||12345^SMITH^JANE^A^^^MD
```

**Segments**:
- MSH: Message Header
- EVN: Event Type
- PID: Patient Identification
- PV1: Patient Visit
- OBX: Observation/Result

### HL7 FHIR (Fast Healthcare Interoperability Resources)

**Purpose**: Modern RESTful API standard for health data exchange
**Format**: JSON or XML
**Structure**: Resources (modular health data components)

**Core Resources**:
- Patient
- Practitioner
- Organization
- Encounter
- Observation
- Condition
- MedicationRequest
- Procedure
- DiagnosticReport

**Example Patient Resource (JSON)**:
```json
{
  "resourceType": "Patient",
  "id": "example",
  "identifier": [
    {
      "system": "http://hospital.org/mrn",
      "value": "123456"
    }
  ],
  "name": [
    {
      "use": "official",
      "family": "Doe",
      "given": ["John", "A"]
    }
  ],
  "gender": "male",
  "birthDate": "1965-03-15",
  "address": [
    {
      "line": ["123 Main St"],
      "city": "Anytown",
      "state": "CA",
      "postalCode": "12345"
    }
  ]
}
```

**Example Observation Resource (Lab Result)**:
```json
{
  "resourceType": "Observation",
  "id": "lab-result-hba1c",
  "status": "final",
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/observation-category",
          "code": "laboratory"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "4548-4",
        "display": "Hemoglobin A1c"
      }
    ]
  },
  "subject": {
    "reference": "Patient/example"
  },
  "effectiveDateTime": "2023-10-15T10:30:00Z",
  "valueQuantity": {
    "value": 7.2,
    "unit": "%",
    "system": "http://unitsofmeasure.org",
    "code": "%"
  },
  "referenceRange": [
    {
      "low": {
        "value": 4.0,
        "unit": "%"
      },
      "high": {
        "value": 6.0,
        "unit": "%"
      }
    }
  ]
}
```

**FHIR API Operations**:
```
GET /Patient/123        # Read patient
GET /Patient?name=Doe   # Search patients
POST /Observation       # Create observation
PUT /Patient/123        # Update patient
DELETE /Patient/123     # Delete patient
```

### CDA (Clinical Document Architecture)

**Purpose**: XML-based standard for clinical documents
**Uses**: Continuity of Care Document (CCD), Discharge Summary

**CDA Document Structure**:
```xml
<ClinicalDocument>
  <realmCode code="US"/>
  <typeId root="2.16.840.1.113883.1.3" extension="POCD_HD000040"/>
  <templateId root="2.16.840.1.113883.10.20.22.1.1"/>  <!-- CCD template -->
  <id root="2.16.840.1.113883.19.5" extension="c266"/>
  <code code="34133-9" codeSystem="2.16.840.1.113883.6.1" displayName="Summarization of Episode Note"/>
  <title>Continuity of Care Document</title>
  <effectiveTime value="20231015120000"/>
  <recordTarget>
    <patientRole>
      <id extension="123456" root="2.16.840.1.113883.19.5"/>
      <patient>
        <name>
          <given>John</given>
          <family>Doe</family>
        </name>
        <administrativeGenderCode code="M" codeSystem="2.16.840.1.113883.5.1"/>
        <birthTime value="19650315"/>
      </patient>
    </patientRole>
  </recordTarget>
  <!-- Additional sections: Allergies, Medications, Problems, Procedures, etc. -->
</ClinicalDocument>
```

### C-CDA (Consolidated CDA)

**Common Document Types**:
- Continuity of Care Document (CCD)
- Consultation Note
- Discharge Summary
- History and Physical
- Operative Note
- Progress Note

## Data Quality Standards

### FHIR Data Quality

**Data Quality Dimensions**:
```
- Completeness: Required fields populated
- Conformance: Adheres to FHIR spec and profiles
- Plausibility: Values within expected ranges
- Consistency: Logically coherent
```

**FHIR Validation**:
```python
import requests

def validate_fhir_resource(resource_json, profile_url=None):
    """Validate FHIR resource against specification"""

    validation_url = "http://fhir-validator.org/validate"

    payload = {
        "resource": resource_json,
        "profile": profile_url  # Optional IG profile
    }

    response = requests.post(validation_url, json=payload)

    if response.status_code == 200:
        result = response.json()
        return {
            'valid': result['valid'],
            'errors': result.get('errors', []),
            'warnings': result.get('warnings', [])
        }
```

### US Core Implementation Guide

**Purpose**: Define minimum FHIR profiles for US healthcare

**Core Profiles**:
- US Core Patient
- US Core Encounter
- US Core Condition
- US Core Medication Request
- US Core Observation (Lab, Vital Signs)

**Must Support Elements**: Required to be supported if data available

## Interoperability Frameworks

### USCDI (US Core Data for Interoperability)

**Purpose**: Define minimum health data elements for nationwide interoperability

**USCDI v3 Data Classes**:
1. Patient Demographics
2. Encounter Information
3. Problems
4. Medications
5. Allergies and Intolerances
6. Procedures
7. Immunizations
8. Laboratory Results
9. Vital Signs
10. Clinical Notes
11. Care Team Member(s)
12. Smoking Status
13. Pediatric Data (weight-for-length, etc.)
14. Sexual Orientation and Gender Identity (SOGI)
15. Social Determinants of Health

### QHIN (Qualified Health Information Network)

**Purpose**: Nationwide health information exchange under TEFCA

**Exchange Purposes**:
- Treatment
- Payment
- Healthcare Operations
- Public Health
- Government Benefits
- Individual Access Services

## Reference Data & Code Sets

### Code System URIs (FHIR)**:
```
http://snomed.info/sct              - SNOMED CT
http://loinc.org                     - LOINC
http://www.nlm.nih.gov/research/umls/rxnorm - RxNorm
http://hl7.org/fhir/sid/icd-10-cm   - ICD-10-CM
http://hl7.org/fhir/sid/ndc          - NDC
http://www.ama-assn.org/go/cpt      - CPT
```

### Value Sets

**VSAC (Value Set Authority Center)**: Central repository for clinical value sets

**Example Value Set**:
```
OID: 2.16.840.1.113883.3.464.1003.103.12.1001
Name: Diabetes
Includes codes from:
- ICD-10-CM: E08.*, E09.*, E10.*, E11.*, E13.*
- SNOMED CT: 44054006, 46635009, 73211009, etc.
```

---

*Healthcare Data Standards Reference - Terminologies, exchange standards, and interoperability frameworks for healthcare data.*
