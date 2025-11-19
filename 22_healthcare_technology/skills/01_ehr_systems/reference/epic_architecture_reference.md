# Epic EHR Architecture Reference

## Overview
Epic Systems Corporation's EHR platform is one of the world's most widely deployed healthcare information systems, serving major health systems globally. This reference covers Epic's architectural components, data models, and integration patterns.

## Core Architecture Components

### 1. Chronicles Database
Chronicles is Epic's proprietary hierarchical database that forms the foundation of all Epic applications.

#### Database Structure
- **Master Files**: Primary data storage units (e.g., Patient, Provider, Medications)
- **Items**: Individual records within master files (e.g., specific patient record)
- **Contacts**: Time-stamped encounters or events (e.g., office visits, procedures)
- **Instant Records (INIs)**: Configuration and template data

#### Key Master Files
```
EPT - Patient Demographics (Epic Patient)
EMP - Employee/Provider Records
DAT - Scheduling/Appointment Data
ORD - Orders (medications, labs, procedures)
RXN - Medication Database
LRR - Lab Results
FDI - Flowsheet Data
NOE - Clinical Notes
```

#### Data Access Patterns
- **Direct Chronicles Access**: Via Clarity, Epic's relational database mirror
- **Interconnect**: Real-time HL7 and proprietary messaging
- **Web Services**: FHIR and Epic-specific APIs
- **Reporting Database**: Clarity, Caboodle (analytics warehouse)

### 2. Hyperspace
Epic's thick-client user interface for clinicians and administrative staff.

#### Components
- **Patient Station**: Primary clinical documentation interface
- **Cadence**: Scheduling and registration
- **Resolute**: Professional billing
- **Prelude**: Patient registration and access
- **Willow**: Inventory and supply chain
- **Beaker**: Laboratory information system
- **Radiant**: Radiology/PACS integration

#### Hyperspace Workflow Architecture
```
User Login → Activity Selection → Context Selection →
Workspace Opening → Patient Chart Access → Documentation →
Clinical Decision Support → Order Entry → Sign/Submit
```

### 3. Integration Layer

#### Interconnect Engine
Epic's proprietary integration engine for HL7 messaging.

**Message Types Supported**:
- ADT (Admission/Discharge/Transfer)
- ORM (Order Messages)
- ORU (Results)
- SIU (Scheduling)
- DFT (Charge Posting)
- BAR (Billing Account Records)

**Configuration Components**:
- Interface Master File (ITF)
- In Basket (IB) for manual message handling
- Error handling and retry logic
- Transformation and routing rules

#### Web Services Architecture

**Epic FHIR Implementation**:
- Based on FHIR R4 standard
- OAuth 2.0 with SMART on FHIR
- Supports: Patient, Practitioner, Observation, Condition, MedicationRequest, etc.
- Rate limiting: 1000 requests/hour (configurable)
- Sandbox environment for testing

**Legacy Web Services**:
- GetPatient, GetEncounter, GetOrders
- SOAP-based (legacy)
- Custom Epic XML schemas
- Certificate-based authentication

### 4. Clarity Reporting Database

Epic's relational database that mirrors Chronicles data for reporting and analytics.

#### Key Schemas
```sql
-- Patient Demographics
PATIENT table
PATIENT_2, PATIENT_3 (extension tables)
ZC_PATIENT_TYPE (patient type reference)

-- Encounters
PAT_ENC (Patient Encounter)
PAT_ENC_HSP (Hospital encounter details)
HSP_ACCOUNT (Hospital account)

-- Orders
ORDER_PROC (Procedure orders)
ORDER_MED (Medication orders)
ORDER_METRICS (Order timing metrics)

-- Results
ORDER_RESULTS (Lab/diagnostic results)
COMPONENT (Result components)

-- Clinical Documentation
HNO_INFO (Note metadata)
HNO_NOTE_TEXT (Note text)
```

#### Performance Considerations
- Updated every 15-30 minutes (not real-time)
- Indexed on patient IDs, encounter numbers, order IDs
- Use Clarity for retrospective reporting only
- Never update Clarity directly (read-only)

### 5. MyChart Patient Portal

Epic's patient-facing application for health record access and engagement.

#### Technical Components
- **Web Application**: ASP.NET/IIS-based
- **Mobile Apps**: iOS and Android native applications
- **Authentication**: Multi-factor authentication, MyChart login
- **API Backend**: Epic FHIR APIs

#### Key Features
- Health summary viewing
- Medication lists and refill requests
- Test result viewing
- Appointment scheduling
- Secure messaging with providers
- Questionnaire completion
- Proxy access for dependents

#### Integration Points
```
MyChart → FHIR API → Interconnect → Chronicles
         → Direct Chronicles read (cached)
         → Haiku/Canto (mobile platform)
```

### 6. App Orchard Ecosystem

Epic's third-party application marketplace and integration platform.

#### Integration Methods
1. **SMART on FHIR Apps**: JavaScript apps launched within Epic
2. **Native Apps**: Desktop applications launched via EpicCare Link
3. **Web Apps**: External web applications with FHIR access
4. **Backend Services**: Server-to-server integration

#### Authentication Flow
```
1. Launch request from Epic
2. OAuth 2.0 authorization
3. Token exchange
4. FHIR API access with patient context
5. Session management
```

## Data Models

### Patient Record Structure

```
Patient Master (EPT)
├── Demographics
│   ├── Name, DOB, Gender, SSN
│   ├── Addresses (multiple)
│   ├── Phone numbers (multiple)
│   ├── Email addresses
│   └── Emergency contacts
├── Identifiers
│   ├── MRN (Medical Record Number)
│   ├── Enterprise ID
│   ├── External IDs
│   └── SSN/Government ID
├── Coverage (Insurance)
│   ├── Primary insurance
│   ├── Secondary insurance
│   └── Guarantor information
└── Preferences
    ├── Language preference
    ├── Communication preferences
    ├── Advance directives
    └── Organ donor status
```

### Encounter Model

```
Encounter (PAT_ENC)
├── Encounter metadata
│   ├── CSN (Contact Serial Number) - unique encounter ID
│   ├── Encounter type (office visit, ED, inpatient)
│   ├── Department
│   ├── Attending provider
│   └── Visit date/time
├── Diagnosis list
│   ├── Primary diagnosis
│   ├── Secondary diagnoses
│   └── Problem list updates
├── Orders
│   ├── Medication orders
│   ├── Lab orders
│   ├── Imaging orders
│   └── Procedure orders
├── Clinical documentation
│   ├── Chief complaint
│   ├── HPI (History of Present Illness)
│   ├── ROS (Review of Systems)
│   ├── Physical exam
│   ├── Assessment and plan
│   └── Procedure notes
└── Billing
    ├── CPT codes
    ├── ICD-10 codes
    ├── Charges
    └── Professional billing records
```

### Medication Order Model

```
Medication Order (ORD)
├── Order metadata
│   ├── Order ID
│   ├── Order date/time
│   ├── Ordering provider
│   └── Order status (active, discontinued, completed)
├── Medication details
│   ├── Generic name
│   ├── Brand name
│   ├── RxNorm code
│   ├── Dose
│   ├── Route
│   ├── Frequency
│   └── Duration
├── Clinical decision support
│   ├── Drug-drug interactions
│   ├── Drug-allergy checks
│   ├── Renal dosing
│   └── Duplicate therapy checks
└── Fulfillment
    ├── Pharmacy routing
    ├── Dispense quantity
    ├── Refills
    └── Prescription printing/e-prescribing
```

## Security Architecture

### Authentication and Authorization

#### Single Sign-On (SSO)
- SAML 2.0 integration
- Active Directory integration
- Kerberos authentication
- Smart card/CAC support

#### Role-Based Access Control (RBAC)
```
User Template → Security Class → Record Access
                              → Break-the-Glass
                              → VIP Patient Restrictions
```

#### Audit Logging
Epic maintains comprehensive audit logs:
- User access to patient records
- Print/fax/export activities
- Clinical documentation changes
- Order entry and modifications
- Medication administration
- Break-the-glass access events

### Data Security

#### Encryption
- Database encryption at rest (TDE - Transparent Data Encryption)
- Network traffic encryption (TLS 1.2+)
- Backup encryption
- Field-level encryption for sensitive data

#### De-identification Tools
- Epic's De-ID tool for research databases
- HIPAA-compliant data masking
- Date shifting algorithms
- Synthetic data generation for testing

## Performance and Scalability

### Caching Strategy
Epic uses multi-tier caching:
1. **Client-side cache**: Hyperspace local cache
2. **Application server cache**: Reference data, templates
3. **Database cache**: Chronicles cache servers
4. **Web services cache**: FHIR response caching

### High Availability Architecture
```
Load Balancer
├── Web Server Cluster (IIS)
├── Application Server Cluster (Interconnect, Web Services)
├── Database Servers
│   ├── Primary Chronicles server
│   ├── Cache servers (Chronicles)
│   └── Clarity database (SQL Server)
└── Storage Array (SAN/NAS)
```

### Disaster Recovery
- Real-time database replication
- Geographic redundancy
- RPO (Recovery Point Objective): < 15 minutes
- RTO (Recovery Time Objective): < 4 hours for critical systems

## Development Environments

### Environment Tiers
1. **Production**: Live patient care
2. **Preproduction**: Final testing before production release
3. **Test**: Integration testing and training
4. **Development**: Configuration and build environment
5. **Sandbox**: FHIR API testing (external developers)

### Version Control
- Chronicles tracks all configuration changes
- Version history with user/timestamp
- Rollback capabilities
- Build and extract tools for environment promotion

## Best Practices

### Interface Development
1. Always use Interconnect for HL7 messaging (not point-to-point)
2. Implement robust error handling and retry logic
3. Use acknowledgment messages (ACK/NACK)
4. Monitor interface queues and error buckets
5. Test with production-like data volumes

### FHIR API Development
1. Use SMART on FHIR for patient context
2. Implement OAuth 2.0 refresh token handling
3. Respect rate limits and pagination
4. Cache reference data (practitioners, organizations)
5. Handle HTTP 429 (rate limiting) gracefully

### Clarity Reporting
1. Never query Clarity for real-time clinical workflows
2. Use appropriate indexes and query optimization
3. Limit result sets with WHERE clauses
4. Avoid SELECT * queries
5. Consider Caboodle for complex analytics

### Clinical Decision Support (CDS)
1. Use Epic's BPA (Best Practice Advisory) framework
2. Minimize interruptive alerts (alert fatigue)
3. Provide clear, actionable recommendations
4. Include evidence-based references
5. Allow easy dismissal with required reasons

## Common Integration Patterns

### Pattern 1: ADT Feed to External System
```
Epic Chronicles → Interconnect → HL7 ADT Message →
External Interface Engine → External System
```

### Pattern 2: Lab Results Interface
```
Lab Instrument → Lab System → HL7 ORU →
Interconnect → Epic Beaker → Chronicles
```

### Pattern 3: Patient Portal Data Access
```
MyChart Mobile App → OAuth 2.0 Auth → FHIR API →
Interconnect → Chronicles → Cached Response
```

### Pattern 4: Clinical Decision Support Integration
```
Order Entry → CDS Hooks API → External CDS Engine →
Recommendation Cards → Epic BPA Display → Provider Action
```

## Troubleshooting Guide

### Common Issues

#### Interface Down
1. Check Interconnect status (Scoop tool)
2. Review error logs in Interface Error Bucket
3. Verify network connectivity
4. Check authentication credentials
5. Review recent configuration changes

#### Slow Clarity Queries
1. Check query execution plan
2. Verify index usage
3. Review table join strategies
4. Consider date range limitations
5. Check Clarity update lag time

#### FHIR API Errors
1. Verify OAuth token validity
2. Check API rate limits
3. Review FHIR resource conformance
4. Validate request payload syntax
5. Check Epic FHIR version compatibility

## References

- Epic UserWeb: Official Epic documentation portal
- Epic Galaxy: Epic's community forum
- App Orchard: https://apporchard.epic.com/
- Epic FHIR Documentation: https://fhir.epic.com/
- HL7 International: https://www.hl7.org/
- SMART on FHIR: https://smarthealthit.org/

## Version History

Epic releases major versions approximately annually:
- **2024**: Epic November 2024 version
- **2023**: Epic November 2023 version
- **2022**: Epic November 2022 version

Always check version-specific documentation for feature availability and API changes.

## Regulatory Compliance

Epic is certified for:
- ONC Health IT Certification (21st Century Cures Act)
- HIPAA compliance
- GDPR compliance (for international implementations)
- SOC 2 Type II compliance
- HITRUST certification

---

**Document Version**: 2.0
**Last Updated**: November 2024
**Author**: Healthcare Technology Team
**Classification**: Public - Educational Use
