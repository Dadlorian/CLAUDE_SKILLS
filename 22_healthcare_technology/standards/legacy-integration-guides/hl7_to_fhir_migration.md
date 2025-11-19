# HL7 v2 to FHIR Migration Guide

**Version**: 2.2.0
**Last Updated**: 2025-11-19
**Status**: Production Ready
**Standards Compliance**: FHIR R4, HL7 v2.5.1, HIPAA, HITRUST

---

## Executive Summary

This comprehensive guide provides step-by-step procedures for migrating healthcare data and integrations from HL7 v2 messaging to modern FHIR APIs. Organizations transitioning from legacy messaging must carefully plan data transformation, validate mapping completeness, and manage bi-directional flows during transition periods.

---

## 1. Migration Planning & Assessment

### 1.1 Pre-Migration Assessment

**Scope Discovery Phase (Weeks 1-2):**

```
Questions to Answer:

1. Current State Analysis
   □ How many HL7 v2 interfaces currently in production?
   □ What message types? (ADT, ORU, RAS, SIU, etc.)
   □ What volume per message type? (msgs/hour)
   □ How many years of historical data?
   □ Which systems send/receive HL7?
   □ What custom extensions or modifications?
   □ Current error rate and issues?

2. Target State Definition
   □ Which FHIR resources replace each HL7 message?
   □ What FHIR profiles will be used?
   □ What APIs will replace MLLP connections?
   □ Timeline for full migration?
   □ Budget and resource constraints?
   □ Risk tolerance for downtime?

3. Data Mapping Analysis
   □ Does every HL7 field map to FHIR?
   □ Are there HL7 custom fields?
   □ How are identifiers managed?
   □ What code system mappings needed?
   □ Are there data quality issues?
   □ What validation rules apply?

4. Integration Partner Assessment
   □ How many external systems integrate?
   □ Do partners support FHIR?
   □ What's their migration timeline?
   □ Can they run parallel HL7+FHIR?
   □ What training is needed?
   □ What SLA commitments exist?
```

**Impact Assessment Matrix:**

```
System                  HL7 Msgs/Day    Complexity    Effort (hrs)
────────────────────────────────────────────────────────────────────
Laboratory System        5,000           Medium        320
Pharmacy                   800           Low           160
Radiology                  600           Medium        240
Registration             2,100           High         400
Billing                    500           High         360
Scheduling                 400           Low          120
```

### 1.2 Resource Planning

**Typical Migration Team:**

```
Role                        Count    Responsibilities
─────────────────────────────────────────────────────────────────
Project Manager              1       Timeline, budget, risks
Solution Architect           1       Design, standards compliance
HL7/FHIR Developer          2       Mapping, transformation code
QA/Tester                    2       Validation, testing
Data Analyst                 1       Data quality, reconciliation
Clinician/Domain Expert      1       Clinical validation
Operations/DevOps           1       Deployment, monitoring
```

**Timeline Estimate:**
```
Phase 1: Planning & Assessment           4 weeks
Phase 2: Design & Mapping               4 weeks
Phase 3: Development & Transformation   8 weeks
Phase 4: Testing & Validation           6 weeks
Phase 5: Parallel Running               8 weeks
Phase 6: Cutover & Stabilization        4 weeks
Phase 7: Monitoring & Optimization      4 weeks
────────────────────────────────────────────────
Total                                   38 weeks (~9 months)
```

---

## 2. Data Mapping & Transformation

### 2.1 HL7 Message to FHIR Resource Mapping

**ADT (Admission/Discharge/Transfer) → FHIR:**

```
HL7 ADT Message Structure          FHIR Resources
─────────────────────────────────────────────────────────
MSH (Message Header)          →    (Meta information)
EVN (Event Type)              →    (Provenance)
PID (Patient ID)              →    Patient
PV1 (Patient Visit)           →    Encounter + Location
DG1 (Diagnosis)               →    Condition
PR1 (Procedure)               →    Procedure
AL1 (Allergy)                 →    AllergyIntolerance
OBX (Observation)             →    Observation

Mapping Rules:

PID → Patient:
  PID[3]  → Patient.identifier (MRN)
  PID[5]  → Patient.name
  PID[7]  → Patient.birthDate
  PID[8]  → Patient.gender (M/F → male/female)
  PID[11] → Patient.address
  PID[13] → Patient.telecom (phone)
  PID[15] → Patient.communication
  PID[19] → Patient.identifier (SSN, if included)

PV1 → Encounter:
  PV1[2]  → Encounter.class (I=inpatient, O=outpatient, E=emergency)
  PV1[3]  → Encounter.location.location (facility/unit/bed)
  PV1[5]  → Encounter.type (patient class)
  PV1[7]  → Encounter.participant.individual (attending physician)
  PV1[19] → Encounter.diagnosis
  PV1[44] → Encounter.admissionSource
  PV1[50] → Encounter.dischargeDisposition (condition at discharge)
  (Timestamp from EVN) → Encounter.period.start/end

DG1 → Condition:
  DG1[3]  → Condition.code (ICD-10)
  DG1[4]  → Condition.code.text (diagnosis description)
  DG1[5]  → Condition.code.text
  DG1[6]  → Condition.category (A=Admission, W=Working, F=Final)

AL1 → AllergyIntolerance:
  AL1[2]  → AllergyIntolerance.code (allergen type)
  AL1[3]  → AllergyIntolerance.reaction.substance.code
  AL1[4]  → AllergyIntolerance.reaction.manifestation
  AL1[5]  → AllergyIntolerance.severity
```

**ORU (Observation Result Unsolicited) → FHIR:**

```
HL7 ORU Message               FHIR Resources
──────────────────────────────────────────────────────
MSH                     →     (Meta information)
PID                     →     Patient
OBR (Observation Req)   →     DiagnosticReport
OBX (Observation)       →     Observation (repeating)
NTE (Notes)             →     Observation.note

Mapping Rules:

OBR → DiagnosticReport:
  OBR[1]  → DiagnosticReport.identifier (report ID)
  OBR[4]  → DiagnosticReport.code (test code, LOINC)
  OBR[7]  → DiagnosticReport.effectiveDateTime
  OBR[24] → DiagnosticReport.result (references OBX)

OBX → Observation:
  OBX[1]  → Observation.id (set ID)
  OBX[2]  → Observation.value type (NM=numeric, ST=string)
  OBX[3]  → Observation.code (LOINC code^text)
  OBX[5]  → Observation.value
  OBX[6]  → Observation.value.unit
  OBX[7]  → Observation.referenceRange
  OBX[8]  → Observation.interpretation (L=low, H=high, N=normal)
  OBX[11] → Observation.status (F=final, P=preliminary)
  OBX[14] → Observation.effectiveDateTime
```

**RAS (Pharmacy/Treatment Admin) → FHIR:**

```
HL7 RAS Message               FHIR Resources
──────────────────────────────────────────────────────
MSH                     →     (Meta information)
PID                     →     Patient
ORC (Order)             →     MedicationRequest
RXE (Pharmacy Order)    →     MedicationRequest details
RXA (Administration)    →     MedicationAdministration
RXR (Route)             →     (Route in RXA/RXE)

Mapping Rules:

ORC → MedicationRequest:
  ORC[1]  → MedicationRequest.status (NW=new, RF=refill)
  ORC[2]  → MedicationRequest.identifier (order number)

RXE → MedicationRequest details:
  RXE[5]  → MedicationRequest.medication.reference (drug code)
  RXE[6]  → MedicationRequest.dosageInstruction.dose
  RXE[7]  → MedicationRequest.dosageInstruction.route
  RXE[11] → MedicationRequest.dosageInstruction.timing

RXA → MedicationAdministration:
  RXA[1]  → MedicationAdministration.dosage.dose
  RXA[3]  → MedicationAdministration.effectiveDateTime
  RXA[5]  → MedicationAdministration.medication
  RXA[6]  → MedicationAdministration.dosage.dose
  RXA[11] → MedicationAdministration.performer.actor
  RXA[15] → MedicationAdministration.status
```

### 2.2 Code System & Terminology Mapping

**Creating Mapping Tables:**

```sql
-- ICD-9 to ICD-10 Mapping
CREATE TABLE terminology_mapping (
    source_code VARCHAR(20),
    source_system VARCHAR(50),      -- ICD-9-CM
    target_code VARCHAR(20),
    target_system VARCHAR(50),      -- ICD-10-CM
    mapping_status VARCHAR(20),     -- 1:1, 1:many, approximate
    confidence_score DECIMAL(3,2),  -- 0.00 to 1.00
    last_updated TIMESTAMP,
    PRIMARY KEY (source_code, source_system)
);

-- Examples:
-- 401.9 (ICD-9) → I10 (ICD-10) - Essential hypertension
-- 250.00 (ICD-9) → E11.9 (ICD-10) - Type 2 diabetes
```

**Gender Code Mapping:**

```python
GENDER_MAPPING = {
    # HL7 v2 → FHIR
    'M': 'male',
    'F': 'female',
    'O': 'other',
    'U': 'unknown',
    # Legacy codes
    '1': 'male',
    '2': 'female',
    '3': 'other',
    '0': 'unknown',
    '9': 'unknown',
}

ADMINISTRATIVE_GENDER_MAPPING = {
    # HL7 v2 admin gender → FHIR administrativeGender
    'M': 'male',
    'F': 'female',
    'B': 'other',  # Both/other
    'U': 'unknown',
}
```

**Patient Class/Visit Type Mapping:**

```python
ENCOUNTER_CLASS_MAPPING = {
    # HL7 v2 PV1[2] → FHIR Encounter.class
    'I': 'IMP',      # Inpatient
    'O': 'AMB',      # Outpatient/Ambulatory
    'E': 'EMER',     # Emergency
    'H': 'HH',       # Home health
    'R': 'ACUTE',    # Acute care
    'P': 'PRENC',    # Pre-admission/Preadmit
    'C': 'IMP',      # Consultation (treat as inpatient)
}
```

### 2.3 Identifier Management

**MRN Mapping During Migration:**

```
Scenario: Patient has MRN in legacy HL7, multiple IDs in FHIR

HL7 Message (Old):
  PID|1||12345^^^HOSPITAL||DOE^JOHN

FHIR Patient (New):
  {
    "resourceType": "Patient",
    "identifier": [
      {
        "system": "http://hospital.example.com/mrn",
        "value": "12345",
        "use": "official"
      },
      {
        "system": "http://hospital.example.com/fhir-id",
        "value": "patient-uuid-12345",
        "use": "secondary"
      },
      {
        "system": "http://hl7.org/fhir/sid/us-ssn",
        "value": "123-45-6789",
        "use": "secondary"
      }
    ]
  }

Migration Strategy:
  1. Create reference mapping table:
     hl7_mrn | fhir_patient_id | facility | status
     "12345" | "pt-uuid-789"   | "HSP"    | "active"

  2. During transformation:
     hl7_mrn → lookup FHIR patient_id
     → If exists: use existing FHIR patient
     → If not found: create new FHIR patient

  3. After migration:
     Keep mapping table for reverse lookups
     Support legacy MRN queries indefinitely
```

---

## 3. Transformation Implementation

### 3.1 Transformation Code Example

**Python Implementation (Using FHIR Client):**

```python
from fhirclient.models.patient import Patient
from fhirclient.models.encounter import Encounter
from datetime import datetime
import hl7

def transform_adt_a01_to_fhir(hl7_message):
    """Transform HL7 ADT^A01 message to FHIR Bundle"""

    # Parse HL7 message
    parsed_hl7 = hl7.parse(hl7_message)

    # Extract segments
    msh = parsed_hl7['MSH'][0]
    pid = parsed_hl7['PID'][0]
    pv1 = parsed_hl7['PV1'][0]
    evn = parsed_hl7['EVN'][0]

    # Create FHIR Patient
    patient = create_patient_from_pid(pid, pv1)

    # Create FHIR Encounter
    encounter = create_encounter_from_pv1_evn(pv1, evn, patient)

    # Create Bundle with both resources
    bundle = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "resource": patient,
                "request": {
                    "method": "PUT",
                    "url": f"Patient/{patient['id']}"
                }
            },
            {
                "resource": encounter,
                "request": {
                    "method": "POST",
                    "url": "Encounter"
                }
            }
        ]
    }

    return bundle

def create_patient_from_pid(pid, pv1):
    """Create FHIR Patient from HL7 PID segment"""

    # Extract fields
    mrn = pid[3][0][0]
    name_parts = pid[5][0]
    dob = pid[7][0]
    gender = pid[8][0]
    address = pid[11][0] if len(pid) > 11 else None
    phone = pid[13][0] if len(pid) > 13 else None

    # Transform to FHIR
    patient = {
        "resourceType": "Patient",
        "identifier": [
            {
                "system": "http://hospital.example.com/mrn",
                "value": mrn,
                "use": "official"
            }
        ],
        "name": [
            {
                "use": "official",
                "family": name_parts[0],
                "given": [name_parts[1]] if len(name_parts) > 1 else []
            }
        ],
        "gender": "male" if gender == "M" else "female" if gender == "F" else "unknown",
        "birthDate": format_date(dob),
        "active": True
    }

    # Add address if present
    if address:
        patient["address"] = [
            {
                "use": "home",
                "line": [address[0]],
                "city": address[2] if len(address) > 2 else None,
                "state": address[3] if len(address) > 3 else None,
                "postalCode": address[4] if len(address) > 4 else None
            }
        ]

    # Add phone if present
    if phone:
        patient["telecom"] = [
            {
                "system": "phone",
                "value": phone,
                "use": "home"
            }
        ]

    return patient

def create_encounter_from_pv1_evn(pv1, evn, patient):
    """Create FHIR Encounter from HL7 PV1 and EVN segments"""

    admit_timestamp = evn[2][0]  # Event timestamp
    class_code = pv1[2][0]
    location = pv1[3][0]

    encounter_class = class_code_to_fhir(class_code)

    encounter = {
        "resourceType": "Encounter",
        "status": "in-progress" if class_code == "I" else "finished",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": encounter_class
        },
        "subject": {
            "reference": f"Patient/{patient['id']}"
        },
        "period": {
            "start": format_timestamp(admit_timestamp)
        },
        "location": [
            {
                "location": {
                    "display": f"{location[0]}/{location[1]}/{location[2]}"
                }
            }
        ]
    }

    return encounter

def format_date(hl7_date):
    """Convert HL7 YYYYMMDD to ISO 8601"""
    if not hl7_date or len(hl7_date) < 8:
        return None
    return f"{hl7_date[0:4]}-{hl7_date[4:6]}-{hl7_date[6:8]}"

def format_timestamp(hl7_ts):
    """Convert HL7 YYYYMMDDHHmmss to ISO 8601"""
    if not hl7_ts or len(hl7_ts) < 8:
        return None

    # Pad with zeros if needed
    hl7_ts = hl7_ts.ljust(14, '0')

    return f"{hl7_ts[0:4]}-{hl7_ts[4:6]}-{hl7_ts[6:8]}T{hl7_ts[8:10]}:{hl7_ts[10:12]}:{hl7_ts[12:14]}Z"

def class_code_to_fhir(code):
    """Map HL7 patient class to FHIR encounter class"""
    mapping = {
        'I': 'IMP',      # Inpatient
        'O': 'AMB',      # Outpatient
        'E': 'EMER',     # Emergency
        'H': 'HH',       # Home health
    }
    return mapping.get(code, 'IMP')
```

### 3.2 Reverse Transformation (FHIR → HL7)

**Handling bidirectional flow during migration:**

```python
def transform_fhir_to_hl7_adt_a01(patient_resource, encounter_resource):
    """Transform FHIR Patient/Encounter to HL7 ADT^A01 message"""

    # Extract FHIR data
    mrn = get_identifier(patient_resource, "http://hospital.example.com/mrn")
    name = patient_resource['name'][0]
    dob = patient_resource['birthDate']
    gender = patient_resource['gender']
    admit_date = encounter_resource['period']['start']

    # Build HL7 segments
    msh = f"MSH|^~\\&|FHIR_ADAPTER|FACILITY|LEGACY_EHR|FAC2|{get_timestamp()}||ADT^A01^ADT_A01|{get_message_id()}|P|2.5.1"

    evn = f"EVN|A01|{format_fhir_timestamp(admit_date)}"

    pid = f"PID|1||{mrn}^^^HOSPITAL||{name['family']}^{name['given'][0]}||{dob.replace('-', '')}|{gender[0].upper()}|||"

    pv1 = f"PV1|1|I|ICU^301^A||"

    # Build complete message
    message = f"{msh}\r{evn}\r{pid}\r{pv1}"

    return message

def format_fhir_timestamp(iso_timestamp):
    """Convert ISO 8601 to HL7 YYYYMMDDHHmmss"""
    # "2025-11-19T14:30:00Z" → "20251119143000"
    dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
    return dt.strftime('%Y%m%d%H%M%S')
```

---

## 4. Testing & Validation

### 4.1 Data Validation Testing

**Reconciliation Testing:**

```
Test Case: Validate Patient Demographics

HL7 Input:
  PID|1||MRN-12345^^^HOSPITAL||SMITH^JOHN^A||19850315|M|||123 MAIN ST^^SPRINGFIELD^IL^62701

Expected FHIR Output:
  {
    "resourceType": "Patient",
    "identifier": [{"value": "MRN-12345"}],
    "name": [{"family": "SMITH", "given": ["JOHN", "A"]}],
    "birthDate": "1985-03-15",
    "gender": "male",
    "address": [{"line": ["123 MAIN ST"], "city": "SPRINGFIELD", "state": "IL", "postalCode": "62701"}]
  }

Validation Checks:
  ✓ MRN preserved exactly
  ✓ Name parsed correctly (family, given, middle)
  ✓ DOB converted to ISO 8601
  ✓ Gender normalized (M → male)
  ✓ Address components extracted correctly
  ✓ FHIR resource conforms to profile
```

**Test Data Sets:**

```
Test Scenarios:
  1. Happy Path: Complete demographics
  2. Minimal Data: Only required fields
  3. Special Characters: Names with apostrophes, accents
  4. Missing Fields: Empty optional fields
  5. Legacy Codes: Old gender codes (1/2/3)
  6. Date Variations: Partial dates (YYYYMM, YYYY)
  7. Large Datasets: 10,000+ records performance
  8. Duplicate Detection: Duplicate MRNs
  9. Inactive Records: Archived patients
  10. Error Handling: Malformed input
```

### 4.2 Interface Testing

**End-to-End Integration Testing:**

```
Test Environment:
  ┌─ HL7 v2 Sender (Test Legacy EHR)
  │  └→ Sends test ADT messages
  │
  ├─ Transformation Service (Adapter)
  │  └→ Transforms HL7 → FHIR
  │  └→ Validates FHIR
  │
  ├─ FHIR API Server (Test)
  │  └→ Receives Bundle
  │  └→ Creates/updates resources
  │
  └─ Verification Service
     └→ Query FHIR API
     └→ Validate data parity
     └→ Report discrepancies
```

**Test Execution Plan:**

```
Week 1-2: Unit Testing
  □ Individual transformation functions
  □ Code mapping accuracy
  □ Date/time formatting
  □ Identifier generation

Week 3-4: Integration Testing
  □ End-to-end HL7 → FHIR
  □ FHIR API integration
  □ Database inserts/updates
  □ Error handling paths

Week 5-6: UAT (User Acceptance Testing)
  □ Clinician workflow validation
  □ Data accuracy spot checks
  □ Report generation
  □ Edge case handling

Week 7-8: Performance Testing
  □ Load testing: 5,000 msgs/hour
  □ Latency: p95 < 5 seconds
  □ Database query optimization
  □ Memory usage monitoring
```

---

## 5. Parallel Running & Cutover

### 5.1 Dual Writing Strategy

**Architecture during parallel phase (6 months):**

```
Legacy Systems          Adapter Layer           New Infrastructure
──────────────────                              ──────────────────
Legacy EHR
  │ (HL7 msgs)
  └──────────────→ Parser
                    ├─→ Validate
                    ├─→ Transform
                    └─→ Write to Both
                      ├──→ Legacy DB (rollback)
                      └──→ FHIR API (primary)

New EHR
  (Continues to receive
   HL7 from legacy)     Verification
                        Service
                        ├─ Query both systems
                        ├─ Compare data
                        └─ Alert on discrepancies
```

**Verification Checklist:**

```
Daily Reconciliation:
  □ Patient counts match (within 0.1%)
  □ ADT volume matches
  □ Lab result counts match
  □ Medication orders match
  □ Error rates within tolerance
  □ No orphaned records

Weekly Audit:
  □ MRN mapping completeness
  □ Code translation accuracy
  □ Date/time consistency
  □ Reference integrity
  □ Duplicate detection effectiveness
  □ Performance metrics acceptable

Monthly Review:
  □ Clinical validation by domain experts
  □ Compliance audit
  □ Security assessment
  □ Incident analysis
  □ Readiness for cutover
```

### 5.2 Cutover Execution

**Cutover Day Plan (Example for 100,000 patient records):**

```
Timeline:
  12:00 AM - Stop all HL7 receiving
            - Begin final data sync
            - Verify data parity 100%

  02:00 AM - Switch legacy EHR to read-only mode
            - Begin directed HL7 v2 migration
            - Run reconciliation queries

  04:00 AM - Parallel system freeze
            - No new data accepted
            - Final validation pass
            - Backup all systems

  06:00 AM - Enable new FHIR API for primary write
            - Verify all health checks pass
            - Test sample queries
            - Pre-position support team

  08:00 AM - Gradual traffic cutover begins
            - Route 10% of traffic to new API
            - Monitor error rates
            - Have rollback ready

  10:00 AM - Route 50% of traffic to new API
            - Verify database performance
            - Check alert systems
            - Monitor team readiness

  12:00 PM - Route 100% of traffic to new API
            - Legacy HL7 disabled
            - Legacy system read-only
            - Intensive monitoring begins

  12:00 PM - 7 days: Rollback window open
            - Keep legacy system running
            - Be ready to switch back
            - 24/7 support staffing

  Day 8+:   Legacy system archived
            - Backup all data
            - Remove from active infrastructure
            - Maintain for 7-year audit trail
```

---

## 6. Post-Migration Monitoring

### 6.1 Metrics & Alerts

**Critical Metrics (First 30 Days):**

```
Data Completeness:
  □ All patient records migrated: 100%
  □ All HL7 mappings accurate: 99.9%
  □ Identifier mapping completeness: 100%

Data Quality:
  □ Data parity with legacy: 99.9%
  □ Code translation failures: 0%
  □ Reference integrity violations: 0%

Performance:
  □ API response time p95: < 2 seconds
  □ Database query time p95: < 1 second
  □ Message processing latency: < 500ms

Reliability:
  □ API availability: 99.9%
  □ Error rate: < 0.1%
  □ Unplanned downtime: 0 minutes

User Experience:
  □ System response time acceptable
  □ Data retrieval accuracy verified
  □ Clinical workflows uninterrupted
  □ Clinician feedback positive
```

---

## 7. Rollback Planning

**Rollback Trigger Criteria:**

```
CRITICAL - Rollback Immediately:
  ✗ Data loss detected
  ✗ Patient safety concern
  ✗ System unavailable > 5 minutes
  ✗ Data corruption discovered
  ✗ Compliance violation

MAJOR - Rollback Within 1 Hour:
  ✗ Error rate > 10%
  ✗ API latency > 30 seconds
  ✗ Database integrity issues
  ✗ Multiple system failures
  ✗ Inability to process urgent requests

MINOR - Assessment & Remediation:
  ✗ Error rate 1-10%
  ✗ Latency 5-30 seconds
  ✗ Single component degradation
  ✗ Intermittent failures
```

**Rollback Procedure:**

```
1. Decision Point (< 15 min to decide)
   - Assess severity
   - Consult incident commander
   - Review impact scope
   - Decide: Fix In-Place vs. Rollback

2. Rollback Execution (if approved)
   - Notify all stakeholders
   - Stop new FHIR writes
   - Re-enable legacy HL7 ingestion
   - Verify legacy system accepting messages
   - Switch router back to legacy API
   - Begin data reconciliation

3. Post-Rollback (within 1 hour)
   - Verify data integrity
   - Document root cause
   - Create action items
   - Schedule investigation meeting
   - Determine retry timeline
```

---

## Appendix: Migration Checklist

**Pre-Migration:**
- [ ] Stakeholder approval obtained
- [ ] Project team assigned
- [ ] Budget allocated
- [ ] Timeline agreed
- [ ] Risk register created
- [ ] Communications plan finalized

**Design Phase:**
- [ ] FHIR profiles selected
- [ ] Mapping document completed
- [ ] Code translation table created
- [ ] Identifier strategy defined
- [ ] Transformation algorithm designed
- [ ] Error handling procedures defined

**Development:**
- [ ] Adapter code developed
- [ ] Transformation logic implemented
- [ ] Bidirectional flow implemented
- [ ] Error handling coded
- [ ] Logging/auditing added
- [ ] Code review completed

**Testing:**
- [ ] Unit tests pass (80%+ coverage)
- [ ] Integration tests pass
- [ ] End-to-end tests pass
- [ ] UAT approved by clinicians
- [ ] Performance tests meet SLA
- [ ] Security scan completed

**Migration Preparation:**
- [ ] Cutover plan documented
- [ ] Rollback plan tested
- [ ] Support team trained
- [ ] Communication sent to users
- [ ] Legacy system backup completed
- [ ] Parallel running verified

**Cutover:**
- [ ] Health checks pass
- [ ] Data sync 100%
- [ ] Gradual traffic migration
- [ ] All systems operational
- [ ] Support team monitoring 24/7

**Post-Migration:**
- [ ] Data validation complete
- [ ] Performance acceptable
- [ ] No critical incidents
- [ ] Lessons learned documented
- [ ] Rollback window closed
- [ ] Legacy system archived

---

**Contact**: Data Migration & Integration Team
**Last Reviewed**: 2025-11-19
**Next Review**: 2026-05-19
