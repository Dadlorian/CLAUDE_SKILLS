# Cerner Millennium Architecture Reference

## Overview
Oracle Health (formerly Cerner Corporation) Millennium is a comprehensive EHR platform used globally across hospitals, ambulatory clinics, and health systems. This reference documents the architectural components, data models, and integration capabilities of the Millennium platform.

## Core Architecture Components

### 1. Millennium Database Architecture

Cerner Millennium uses Oracle Database as its primary data repository, with a relational structure optimized for healthcare workflows.

#### Database Schema Organization
```
Clinical Domain (CLINICAL)
├── PERSON (Patient demographics)
├── ENCOUNTER (Clinical encounters)
├── ORDERS (Clinical orders)
├── CLINICAL_EVENT (Results, vitals, assessments)
├── MED_ORDER_DETAIL (Medication order details)
└── ORDER_DETAIL (General order details)

Reference Domain (REFERENCE)
├── CODE_VALUE (System-wide code values)
├── CODE_VALUE_SET (Code value sets)
├── NOMENCLATURE (Clinical terminologies)
└── CODE_VALUE_EXTENSION (Extended code attributes)

Administration Domain (ADMIN)
├── PRSNL (Personnel/Provider records)
├── LOCATION (Facility locations)
├── ORGANIZATION (Organizations)
└── FACILITY (Facility information)
```

#### Key Database Tables

**PERSON Table** - Patient Demographics
```sql
-- Core patient demographic information
PERSON_ID (Primary Key)
NAME_FULL_FORMATTED
NAME_FIRST
NAME_LAST
BIRTH_DT_TM
SEX_CD
ACTIVE_IND
CREATE_DT_TM
CREATE_PRSNL_ID
```

**ENCOUNTER Table** - Patient Encounters
```sql
ENCNTR_ID (Primary Key)
PERSON_ID (Foreign Key to PERSON)
ENCNTR_TYPE_CD
ENCNTR_STATUS_CD
REG_DT_TM (Registration date/time)
DISCH_DT_TM (Discharge date/time)
LOC_FACILITY_CD
LOC_BUILDING_CD
ACTIVE_IND
```

**ORDERS Table** - Clinical Orders
```sql
ORDER_ID (Primary Key)
PERSON_ID
ENCNTR_ID
CATALOG_CD (Order catalog item)
ORDER_STATUS_CD
ORDERED_DT_TM
ORDER_MNEMONIC
SYNONYM_ID
ACTIVE_IND
```

**CLINICAL_EVENT Table** - Clinical Results and Observations
```sql
EVENT_ID (Primary Key)
PERSON_ID
ENCNTR_ID
EVENT_CD (Type of event)
EVENT_CLASS_CD
EVENT_TITLE_TEXT
RESULT_VAL
RESULT_UNITS_CD
PERFORMED_DT_TM
VALID_FROM_DT_TM
NORMAL_REF_RANGE_TXT
```

### 2. PowerChart - Clinical User Interface

PowerChart is Cerner's primary clinical documentation and order entry interface.

#### Key PowerChart Components

**PowerChart Organizer**
- Patient summary view
- Problem list
- Allergy list
- Medication list
- Immunization history
- Active orders

**PowerChart Sections**
- **PowerOrders**: Order entry module (CPOE)
- **PowerNote**: Clinical documentation
- **PowerPlan**: Care plans and order sets
- **PowerForm**: Structured data entry forms
- **iBrief**: Patient handoff communication
- **PowerInsight**: Clinical decision support

#### PowerChart Navigation Model
```
Patient Selection → Chart Opening → Organizer View →
Section Navigation → Data Entry → Clinical Decision Support →
Order Entry → Documentation → Sign/Submit
```

### 3. CCL - Cerner Command Language

CCL is Cerner's proprietary programming language for queries, reports, and customizations.

#### CCL Structure
```ccl
-- Basic CCL Query Structure
DROP PROGRAM my_program:dba GO
CREATE PROGRAM my_program:dba

PROMPT
    "Output to File/Printer/MINE" = "MINE"
    ,"Person ID" = 0
    ,"Encounter ID" = 0

WITH OUTDEV, PERSON_ID, ENCNTR_ID

-- Main query logic
SELECT INTO "nl:"
FROM PERSON P
    ,ENCOUNTER E
    ,ORDERS O
WHERE P.PERSON_ID = $PERSON_ID
  AND E.PERSON_ID = P.PERSON_ID
  AND O.ENCNTR_ID = E.ENCNTR_ID
  AND E.ACTIVE_IND = 1
  AND O.ACTIVE_IND = 1
ORDER BY O.ORDERED_DT_TM DESC

WITH TIME = 60, MAXREC = 1000

END GO
```

#### Common CCL Operations
- **Queries**: Data retrieval from Millennium tables
- **Reports**: Formatted output (PDF, Excel, text)
- **Modifications**: Data updates and inserts
- **Scheduled Tasks**: Automated batch jobs
- **Custom Components**: DCP (Dynamic Content Program)

### 4. Cerner Open Engine - Integration Platform

#### Interface Engine Architecture
```
External System → TCP/IP Connection → Open Engine →
Message Processing → Routing Rules → Millennium Database
                   → Outbound Interfaces
```

#### Supported Standards
- **HL7 v2.x**: ADT, ORM, ORU, SIU, MDM, DFT
- **HL7 v3**: CDA (Clinical Document Architecture)
- **FHIR**: R4 implementation
- **X12**: 835, 837 (billing transactions)
- **NCPDP**: Pharmacy transactions
- **DICOM**: Medical imaging

#### Message Processing Flow
```
1. Message Receipt (TCP listener)
2. Validation (schema, syntax)
3. Transformation (mapping rules)
4. Routing (destination determination)
5. Processing (database updates)
6. Acknowledgment (ACK generation)
7. Error Handling (retry logic)
```

### 5. Cerner FHIR API

Cerner's FHIR implementation provides standards-based access to clinical data.

#### FHIR Base URLs
```
Production: https://fhir.cerner.com/r4/{tenant_id}
Sandbox: https://fhir-myrecord-sc.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d
Authorization: https://authorization.cerner.com/tenants/{tenant_id}
```

#### Supported FHIR Resources
**Patient Information**
- Patient
- Person
- RelatedPerson

**Clinical Data**
- Condition
- Observation
- Procedure
- AllergyIntolerance
- Immunization
- DiagnosticReport

**Medications**
- MedicationRequest
- MedicationAdministration
- MedicationStatement

**Encounters and Care**
- Encounter
- Appointment
- CarePlan
- CareTeam

**Documents**
- DocumentReference
- DiagnosticReport

#### OAuth 2.0 Authentication Flow
```
1. Authorization Request
   GET /tenants/{tenant}/authorize
   ?response_type=code
   &client_id={client_id}
   &redirect_uri={redirect}
   &scope=patient/Patient.read patient/Observation.read
   &state={state}
   &aud={fhir_url}

2. Authorization Code Exchange
   POST /tenants/{tenant}/token
   grant_type=authorization_code
   code={auth_code}
   redirect_uri={redirect}
   client_id={client_id}

3. Access Token Response
   {
     "access_token": "eyJhbGc...",
     "token_type": "Bearer",
     "expires_in": 3600,
     "scope": "patient/Patient.read patient/Observation.read",
     "patient": "12345"
   }
```

### 6. PowerChart Touch - Mobile Interface

Native mobile applications for iOS and Android providing clinician access.

#### Architecture
```
Mobile App (iOS/Android) → HTTPS/TLS →
Cerner Mobile Gateway → Millennium Application Server →
Millennium Database
```

#### Capabilities
- Patient chart review
- Order entry (medications, labs)
- Result viewing
- Clinical documentation (limited)
- Secure messaging
- Task management

## Data Models

### Patient Record Model

```
PERSON (Core Demographics)
├── PERSON_ID (Primary identifier)
├── Demographics
│   ├── NAME (multiple entries for name history)
│   ├── BIRTH_DT_TM
│   ├── SEX_CD
│   ├── RACE_CD
│   ├── ETHNIC_GRP_CD
│   └── VIP_CD
├── Identifiers (PERSON_ALIAS)
│   ├── MRN (Medical Record Number)
│   ├── SSN
│   ├── Driver's License
│   └── External IDs
├── Addresses (ADDRESS)
│   ├── Home address
│   ├── Work address
│   └── Temporary address
├── Phone Numbers (PHONE)
│   ├── Home phone
│   ├── Mobile phone
│   └── Work phone
└── Relationships (PERSON_PERSON_RELTN)
    ├── Emergency contacts
    ├── Guarantor
    └── Next of kin
```

### Medication Order Model

```
ORDERS (Core order)
├── ORDER_ID
├── CATALOG_CD → MED_IDENTIFIER
├── ORDER_MNEMONIC
└── ORDER_STATUS_CD

MED_ORDER_DETAIL (Medication specifics)
├── ORDER_ID (FK)
├── DOSE_QUANTITY
├── DOSE_UNIT_CD
├── FREQUENCY_CD
├── ROUTE_CD
├── PRN_IND
└── PRN_REASON_CD

MED_ADMIN_EVENT (Administration record)
├── EVENT_ID
├── ORDER_ID (FK)
├── ADMIN_DT_TM
├── ADMIN_DOSE_QUANTITY
├── ADMIN_ROUTE_CD
└── ADMIN_PRSNL_ID
```

### Clinical Event Model

```
CLINICAL_EVENT
├── EVENT_ID
├── EVENT_CD (Code for event type)
├── EVENT_CLASS_CD
│   ├── MED (Medication)
│   ├── LAB (Laboratory)
│   ├── VIT (Vital Signs)
│   ├── RAD (Radiology)
│   └── DOC (Documentation)
├── RESULT_VAL (Text result value)
├── RESULT_UNITS_CD
├── NORMALCY_CD (Normal/Abnormal flag)
├── EVENT_RELTN (Parent-child relationships)
└── EVENT_PRSNL (Performing personnel)
```

## Code Value System

Cerner uses a comprehensive code value system for all coded data.

### CODE_VALUE Table Structure
```sql
CODE_VALUE
├── CODE_VALUE (Unique numeric identifier)
├── CODE_SET (Group of related codes)
├── DISPLAY (Human-readable display)
├── DESCRIPTION
├── MEANING (Internal meaning)
├── CDF_MEANING (Clinical data foundation meaning)
└── ACTIVE_IND
```

### Common Code Sets
```
Code Set 2   - SEX_CD (Male, Female, Unknown)
Code Set 4   - ORDERS_STATUS (Active, Completed, Discontinued)
Code Set 6   - ENCNTR_TYPE (Inpatient, Outpatient, Emergency)
Code Set 72  - EVENT_CLASS (Med, Lab, Vitals, etc.)
Code Set 87  - ENCNTR_STATUS (In Progress, Discharged)
Code Set 212 - CONTRIBUTOR_SYSTEM (Source systems)
Code Set 220 - POSITION_CD (Staff positions)
```

### Nomenclature Integration
Cerner integrates standard terminologies:
- **SNOMED CT**: Clinical concepts
- **LOINC**: Laboratory and clinical observations
- **RxNorm**: Medications
- **ICD-10-CM**: Diagnoses
- **ICD-10-PCS**: Procedures
- **CPT**: Procedure codes

## Security and Access Control

### Authentication Methods
1. **Kerberos**: Windows integrated authentication
2. **LDAP**: Directory services
3. **SAML 2.0**: Single sign-on
4. **OAuth 2.0**: FHIR API authentication
5. **CAC/PIV**: Smart card authentication

### Position-Based Access Control

```
User (PRSNL)
└── Position Assignment (PRSNL_POSITION)
    └── Position (POSITION)
        └── Role Assignment (POSITION_ROLE_RELTN)
            └── Role (SECURITY_ROLE)
                └── Permissions (SECURITY_ACCESS)
```

### Audit Trail
Cerner maintains comprehensive audit logs:
- User authentication events
- Patient record access (AUDIT_LOG)
- Data modifications (table-specific audit trails)
- Print/export activities
- Break-the-glass access
- Order entry and signing

## Performance and Scalability

### Database Partitioning
```sql
-- Partitioning by encounter date
PARTITION BY RANGE (REG_DT_TM)
(
    PARTITION p_2023_q1 VALUES LESS THAN (TO_DATE('2023-04-01', 'YYYY-MM-DD')),
    PARTITION p_2023_q2 VALUES LESS THAN (TO_DATE('2023-07-01', 'YYYY-MM-DD')),
    PARTITION p_2023_q3 VALUES LESS THAN (TO_DATE('2023-10-01', 'YYYY-MM-DD')),
    PARTITION p_2023_q4 VALUES LESS THAN (TO_DATE('2024-01-01', 'YYYY-MM-DD'))
)
```

### Caching Architecture
- **Application Server Cache**: Session data, user preferences
- **Database Result Cache**: Frequently accessed queries
- **Static Content Cache**: Code values, reference data
- **PowerChart Client Cache**: Local cache for responsiveness

### High Availability
```
Load Balancer (F5 or similar)
├── Web Application Servers (Cluster)
├── Millennium Application Servers (Cluster)
├── CCL Execution Servers
└── Oracle RAC Database (Active-Active)
    ├── Node 1
    └── Node 2
```

## Development Tools

### CCL Development Environment
- **Discern Explorer**: IDE for CCL development
- **CCL Testing**: Unit testing framework
- **Debugger**: Step-through debugging
- **Version Control**: Integration with Git/SVN

### PowerForms Designer
Visual designer for creating structured data entry forms:
- Drag-and-drop interface
- Component library
- Validation rules
- Conditional logic
- Calculation fields

### IQHealth Configuration
Configuration tool for:
- Order catalogs
- Care plans (PowerPlans)
- Clinical decision support rules
- Reference tables
- Workflow configuration

## Integration Patterns

### Pattern 1: ADT Interface (Inbound)
```
Registration System → HL7 ADT Message (A01, A02, A03, etc.) →
Open Engine → CCL Receiving Script → PERSON/ENCOUNTER tables →
Downstream systems notification
```

### Pattern 2: Lab Results Interface (Inbound)
```
Laboratory System → HL7 ORU Message →
Open Engine → Result Processing → ORDERS/CLINICAL_EVENT →
PowerChart Display → Clinical Alert (if abnormal)
```

### Pattern 3: FHIR Patient Data Access (Outbound)
```
External App → OAuth Authorization → FHIR API Request →
Millennium FHIR Service → CCL Query → Database →
FHIR JSON Response
```

### Pattern 4: Billing Interface (Outbound)
```
Millennium Charge Capture → HL7 DFT Message →
Open Engine → Billing System → Claims Processing
```

## PowerChart Customization

### Dynamic Content Programming (DCP)
Custom components embedded in PowerChart using CCL:

```ccl
-- Example: Custom allergy display component
DROP PROGRAM mp_custom_allergy_display:dba GO
CREATE PROGRAM mp_custom_allergy_display:dba

EXECUTE mp_get_person_id
EXECUTE mp_get_encntr_id

SELECT INTO "nl:"
FROM ALLERGY A
WHERE A.PERSON_ID = $PERSON_ID
  AND A.ACTIVE_IND = 1
ORDER BY A.REACTION_CLASS_CD DESC

-- Format output for PowerChart display
CALL ECHO(BUILD2("<p><b>Active Allergies:</b></p>"))

HEAD A.PERSON_ID
  cnt = 0
DETAIL
  cnt = cnt + 1
  CALL ECHO(BUILD2(
    "<div class='allergy'>",
    A.SUBSTANCE_NM, " - ",
    UAR_GET_CODE_DISPLAY(A.REACTION_CLASS_CD),
    "</div>"
  ))
FOOT A.PERSON_ID
  IF (cnt = 0)
    CALL ECHO("<p>No Known Allergies</p>")
  ENDIF

WITH TIME = 30

END GO
```

### MPages (Customizable Workspace)
XML-based customizable PowerChart views:
- Component-based architecture
- CCL-powered data retrieval
- JavaScript for client-side logic
- Responsive design support

## Best Practices

### CCL Development
1. Always use bind variables to prevent SQL injection
2. Include appropriate error handling (ERRORQUIT)
3. Use MAXREC and TIME limits
4. Optimize queries with proper indexing
5. Test with production-like data volumes
6. Document code with comments
7. Use meaningful variable names

### Interface Development
1. Implement robust error handling and logging
2. Use standard HL7 segments and fields when possible
3. Document custom Z-segments thoroughly
4. Test with various message scenarios
5. Monitor interface queues and error logs
6. Implement retry logic with exponential backoff

### FHIR API Usage
1. Implement OAuth token refresh logic
2. Handle pagination for large result sets
3. Use appropriate FHIR search parameters
4. Cache reference data when possible
5. Respect rate limits (default: 60 requests/minute)
6. Implement proper error handling for HTTP status codes

### Database Queries
1. Always include ACTIVE_IND = 1 in WHERE clauses
2. Use appropriate date/time range filters
3. Avoid SELECT * queries
4. Join on indexed columns (PERSON_ID, ENCNTR_ID, ORDER_ID)
5. Consider using Oracle hints for query optimization
6. Test queries in non-production first

## Common Troubleshooting

### Performance Issues
1. Check execution plans for queries
2. Review database statistics and indexes
3. Monitor application server resources
4. Check network latency
5. Review CCL script optimization

### Interface Errors
1. Check Open Engine logs
2. Verify message format and syntax
3. Review routing and transformation rules
4. Check authentication and connectivity
5. Validate code value mappings

### PowerChart Issues
1. Clear client cache
2. Check user position assignments
3. Verify security access
4. Review custom components (DCP/MPages)
5. Check browser compatibility

## References

- **uCern**: Cerner's official documentation portal
- **CernerCare**: Technical support and community
- **Oracle Health Cloud**: Cloud-based Cerner platform
- **FHIR Documentation**: https://fhir.cerner.com/
- **HL7.org**: HL7 messaging standards
- **Oracle Database Documentation**: Database optimization and administration

## Version History

Major Millennium releases:
- **2024.01**: Current release (January 2024)
- **2023.04**: Previous major release
- **2023.01**: Legacy support

Oracle Health (formerly Cerner) typically releases updates quarterly.

## Regulatory Compliance

- **ONC Certification**: 21st Century Cures Act compliant
- **HIPAA**: Comprehensive compliance features
- **HITECH**: Meaningful Use certification
- **GDPR**: International data protection
- **SOC 2 Type II**: Security certification

---

**Document Version**: 2.0
**Last Updated**: November 2024
**Author**: Healthcare Technology Team
**Classification**: Public - Educational Use
