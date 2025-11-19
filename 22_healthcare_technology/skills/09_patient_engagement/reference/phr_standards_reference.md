# Personal Health Record (PHR) Standards Reference

## Regulatory Framework

### USCDI (United States Core Data for Interoperability)

**Purpose:** Standard set of health data elements for EHR certification and patient access

**USCDI v1 (2015) Elements:**
1. Patient name
2. Sex
3. Date of birth
4. Race
5. Ethnicity
6. Contact information
7. Preferred language
8. Problems
9. Medications
10. Medication allergies
11. Lab results
12. Vital signs
13. Procedures
14. Care team members
15. Care plan
16. Goals
17. Health concerns

**USCDI v2 (2020) Additions:**
- Smoking status
- Pregnancy status
- Lab order and result
- Immunizations
- Functional status
- Assessment and plan
- Reasoning/justification for clinical interventions

**USCDI v3 (2021) Additions:**
- Discharge summary
- Referrals sent
- Reason for referral
- Response to referrals
- Patient goals
- Medication duplication therapy
- Substance use

**USCDI v4 (2024) Additions:**
- Mental health conditions
- Substance use disorder treatments
- Initial encounters
- Progress notes
- Pediatric vital signs
- Advance directives

### HL7 FHIR (Fast Healthcare Interoperability Resources)

**Core Resource Types for PHR:**
```
Patient Resource
- Demographics
- Contact information
- Preferred language
- General practitioner references

Observation Resource
- Lab results
- Vital signs
- Assessment scores
- Patient-reported outcomes

Medication/MedicationStatement
- Active medications
- Dosage information
- Instructions
- Allergy information

Condition Resource
- Diagnoses/problems
- Clinical status
- Onset date
- Resolution status

Procedure Resource
- Surgical and diagnostic procedures
- Dates and providers
- Anatomical location
- Outcome information

AllergyIntolerance Resource
- Substance details
- Reaction manifestation
- Severity (mild, moderate, severe)
- Recording status

Goal Resource
- Patient health goals
- Target date
- Priority
- Status

CarePlan Resource
- Goals and addresses
- Activities and interventions
- Performer information
- Timeline

Document Reference
- Clinical documents and reports
- Document type and access URLs
- Author and creation dates
```

**FHIR Implementation Profiles:**
- US Core Data for Interoperability (US Core)
- Da Vinci profiles (for insurance and value-based care)
- Argonaut profiles (for developer consistency)

### HL7 v2 Messaging Standards

**Common PHR-related Messages:**
```
ADT^A01 - Patient admission
ADT^A04 - Patient registration
ORU^R01 - Observation result
RGV^O15 - Pharmacy fill notification
PGL^PC6 - Care plan update
```

**Data Segments for PHR:**
- PID: Patient identification
- OBX: Observation results
- ORC: Common order segment
- RXA: Pharmacy administration
- PRB: Problem segment
- AL1: Allergy information

### CCDA (Continuity of Care Document) - XML Format

**Purpose:** XML-based CDA for clinical document exchange

**Core Sections:**
- Allergies
- Medications
- Problems
- Immunizations
- Vital signs
- Results (labs, imaging)
- Procedures
- Encounters
- Social history
- Family history
- Health insurance

## PHR Data Model Architecture

### Hierarchical Data Organization
```
Patient
├── Demographics
├── Clinical Data
│   ├── Problems/Diagnoses
│   ├── Medications
│   ├── Allergies
│   ├── Procedures
│   ├── Immunizations
│   └── Lab Results
├── Care Plan
├── Health Goals
├── Social Data
├── Insurance Information
└── Documents and Records
```

### Data Relationships
```
Patient → Provider Relationships
Patient → Organization Affiliations
Patient → Encounters (Visits)
  └→ Problems
  └→ Procedures
  └→ Medications
  └→ Observations
Problem → Procedures (addresses)
Problem → Medications (treats)
Medication → Allergies (drug allergies)
Goal → CarePlan (addressed by)
```

### Temporal Data Management
- **Effective dates:** When information becomes active
- **End dates:** When information expires or resolves
- **Version control:** Track changes over time
- **Audit trail:** Who made what changes when

## PHR Data Governance

### Patient Consent Management
**Consent Types:**
1. **Implicit Consent** - Agreed to via account creation
2. **Explicit Consent** - Specific approval for data use
3. **Granular Consent** - Control by data element/provider
4. **Delegated Consent** - Proxy/caregiver access
5. **Emergency Consent Override** - Life-threatening situations

**Consent Attributes:**
```
Consent {
  patientId: UUID
  scopeType: "full" | "partial"
  allowedProviders: [List of NPI numbers]
  allowedDataTypes: [medications, labs, imaging, etc.]
  purposeOfUse: ["treatment", "payment", "operations"]
  startDate: DateTime
  expirationDate: DateTime
  revokedDate: DateTime (optional)
}
```

### Data Minimization Principles
- Collect only necessary health information
- Don't collect information without patient purpose
- Regular review and purging of unused data
- Patient control over what is stored
- Clear retention policies

### Data Provenance Tracking
```
Data Element {
  value: String/Number/Date
  source: "Patient-entered" | "EHR-imported" | "Device-synced"
  sourceOrganization: Organization reference
  recordedDate: DateTime
  recordedBy: Practitioner reference
  confidence: "verified" | "unverified" | "estimated"
  notes: String (optional)
}
```

## PHR Data Quality Standards

### Completeness Requirements
**Critical Elements (MUST be present):**
- Patient identifying information
- Active problem list
- Current medication list
- Drug allergies
- At least one visit record

**Important Elements (SHOULD be present):**
- Vital signs from recent encounter
- Recent lab results
- Current immunizations
- Age-appropriate screening results
- Social determinants data (when available)

### Accuracy and Validation
- **Data type validation:** String, date, numeric formats
- **Range validation:** Values within reasonable ranges
- **Reference validation:** Valid ICD-10, RxNorm codes
- **Duplicate detection:** Flag duplicate entries
- **Inconsistency detection:** Conflicting information alerts

### Timeliness Requirements
- **Real-time data:** Vital signs, alerts (seconds)
- **Near real-time:** Lab results, prescriptions (hours)
- **Periodic:** Care summaries, encounters (days)
- **Historical:** Medical history, old records (variable)

## PHR Interoperability Standards

### Data Exchange Protocols
```
Protocol          Transport    Use Case
─────────────────────────────────────────────
Direct Protocol   SMTP/TLS    Secure messaging
SFTP              TCP/IP      Batch file transfer
HTTPS REST API    TCP/IP      Real-time API
HL7 Messaging     TCP/IP      System-to-system
FHIR via HTTP     HTTPS       Modern interop
WebDAV            HTTPS       Document sharing
```

### Semantic Interoperability

**Standard Code Systems:**
```
Diagnoses:         ICD-10-CM
Procedures:        CPT, ICD-10-PCS
Medications:       RxNorm
Laboratory:        LOINC
Physical Exams:    SNOMED CT
Vital Signs:       LOINC
Results:           SNOMED CT
Allergies:         SNOMED CT
```

**Value Set Bindings:**
- Care setting type
- Medication route
- Problem status
- Procedure status
- Observation interpretation

## PHR Privacy and Security Standards

### Encryption Standards
- **At Rest:** AES-256-GCM
- **In Transit:** TLS 1.2+ with perfect forward secrecy
- **Key Management:** HSM-stored, rotated quarterly
- **Algorithm Strength:** 256-bit minimum

### Access Control Patterns
```
RBAC Components:
├── Roles
│   ├── Patient (full access to own data)
│   ├── Provider (access per consent)
│   ├── Caregiver (delegated access)
│   └── Administrator (system management)
├── Permissions
│   ├── View
│   ├── Create
│   ├── Edit
│   ├── Delete
│   └── Share
└── Resources
    ├── All Personal Data
    ├── Medical Records
    ├── Appointment History
    └── Documents
```

### Audit Logging Requirements
**Log All:**
- Login attempts (successful and failed)
- PHI access (view, download, export)
- Data modifications
- Consent changes
- Share/delegation changes
- Account setting changes

**Log Details:**
- User ID and IP address
- Timestamp (UTC)
- Action performed
- Data accessed/modified
- Query parameters or data elements
- System response and status

## PHR Integration Patterns

### Patient Data Aggregation
```
Multiple EHR Systems
├── Hospital A
├── Clinic B
├── Urgent Care C
└── Specialist D
        ↓
Patient-Initiated Data Collection
        ↓
Data Normalization & FHIR Mapping
        ↓
Unified PHR
        ↓
Patient Access & Management
```

### Data Synchronization Methods
1. **Pull Model** - Portal pulls data on demand
2. **Push Model** - EHR pushes updates to portal
3. **Subscription Model** - Event-driven updates
4. **Batch Model** - Periodic synchronization

## PHR Security Compliance

### HIPAA Privacy and Security
- **Privacy Rule:** Patient access to PHI (45 CFR 164.524)
- **Security Rule:** Technical and administrative safeguards
- **Breach Notification:** 60-day notification requirement
- **Accounting of Disclosures:** Provide upon request

### FDA Guidance for PHR Products
- **Software as a Medical Device (SaMD):** If claims clinical functionality
- **Risk-based classification:** Determines regulatory pathway
- **Cybersecurity requirements:** FDA Premarket and Post-Market guidance
- **Pre-market and Post-Market reporting:** Adverse events, recalls

### State-Level Requirements
- **California (CCPA/CPRA):** Consumer privacy rights
- **New York (SHIELD Act):** Cybersecurity standards
- **Massachusetts:** Data security standards (201 CMR 17.00)
- **Vermont:** Breach notification law (6 V.S.A. § 4723)

## PHR System Performance Metrics

### Availability Requirements
- **Uptime SLA:** 99.9% (8.76 hours downtime/year)
- **Recovery Time Objective (RTO):** <4 hours
- **Recovery Point Objective (RPO):** <1 hour
- **Disaster Recovery Plan:** Tested quarterly

### Performance Targets
- **API Response Time:** <200ms (95th percentile)
- **Data Sync Latency:** <30 minutes
- **Portal Load Time:** <2 seconds
- **Search Query Time:** <500ms

### Scalability Metrics
- **Concurrent Users:** Support 10x expected peak load
- **Storage Capacity:** Plan for 10x current usage
- **Data Growth:** Handle 3-5 years growth
- **Geographic Distribution:** Multi-region support

## PHR Evolution and Future Standards

### Current Trends
- **FHIR-first:** Movement away from HL7 v2 and CDA
- **Patient APIs:** Direct patient access via standards (Apple Health, Google Health)
- **Interoperability Networks:** HIE (Health Information Exchanges)
- **Blockchain:** Emerging for immutable records
- **AI/ML:** Clinical decision support and analytics

### Emerging Standards
- **Care Services Discovery:** Helps find providers
- **Clinical Genomics:** FHIR extensions for genetics
- **Behavioral Health:** Mental health and substance use records
- **Social Determinants:** SDOH data capture and tracking
- **Real-world Data:** Integration of EHR and claims data
