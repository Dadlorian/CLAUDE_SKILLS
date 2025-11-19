# Blue Button Specification Reference

## Overview

**Blue Button** is an initiative to enable patients to access, download, and transmit their health information in a machine-readable format. The movement has evolved through multiple phases, each with different specifications and capabilities.

## Blue Button Generations

### Blue Button 1.0
**Year:** 2010
**Format:** Text-based file download
**Limitations:**
- Not standardized format
- Manual patient download
- Limited machine-readability
- Vendor-specific variations

### Blue Button 2.0 / CCDA (C-CDA) XML
**Year:** 2014
**Standard:** Consolidated Clinical Document Architecture (CCDA) based on HL7 v3
**Capabilities:**
- Structured XML format
- Standardized data elements
- EHR export format
- Limited API capability

### Blue Button+ and SMART on FHIR
**Year:** 2015+
**Standards:** FHIR REST APIs, OAuth2, SMART on FHIR
**Capabilities:**
- Modern API access
- Real-time data exchange
- Third-party app integration
- Patient-authorized access
- Developer-friendly

### 21st Century Cures Act - Information Blocking Rules
**Year:** 2021
**Requirement:** Certified EHRs must provide patient access via FHIR APIs
**Standard:** USCDI data elements via FHIR

## CCDA (C-CDA) XML Format

### Document Structure

```xml
<ClinicalDocument xmlns="urn:hl7-org:v3">
  ├─ <typeId root="2.16.840.1.113883.1.3" extension="POCD_HD000040"/>
  ├─ <id root="2.16.840.1.113883.3.3.2" extension="document-id"/>
  ├─ <code code="34133-9" displayName="Summary of Episode Note"/>
  ├─ <effectiveTime value="20231119"/>
  ├─ <confidentialityCode code="N"/>
  ├─ <title>Patient Clinical Summary</title>
  ├─ <recordTarget>
  │  └─ <patientRole> ... </patientRole>
  ├─ <author>
  │  ├─ <time/> ... </time>
  │  └─ <assignedAuthor/> ... </assignedAuthor>
  ├─ <custodian>
  │  └─ <assignedCustodian/> ... </assignedCustodian>
  ├─ <component>
  │  └─ <structuredBody>
  │     ├─ Problems Section
  │     ├─ Medications Section
  │     ├─ Allergies Section
  │     ├─ Results Section
  │     ├─ Procedures Section
  │     ├─ Immunizations Section
  │     ├─ Encounters Section
  │     ├─ Vital Signs Section
  │     └─ ... Additional Sections
  └─ </structuredBody>
```

### Core Data Sections

#### 1. Problems/Diagnoses Section
```xml
<section>
  <templateId root="2.16.840.1.113883.10.20.22.2.1.1"/>
  <code code="11450-4" displayName="Problem List"/>
  <entry>
    <act classCode="ACT" moodCode="EVN">
      <id root="46d83d3d-6cda-11d0-192e-000475d90aaa"/>
      <code code="CONJ"/>
      <statusCode code="active"/>
      <entryRelationship>
        <observation classCode="OBS" moodCode="EVN">
          <code code="64572001" displayName="Condition">
            <originalText>Diabetes</originalText>
          </code>
          <statusCode code="completed"/>
          <effectiveTime value="20210515"/>
        </observation>
      </entryRelationship>
    </act>
  </entry>
</section>
```

#### 2. Medications Section
```xml
<section>
  <templateId root="2.16.840.1.113883.10.20.22.2.1"/>
  <code code="10160-0" displayName="History of Medication Use"/>
  <entry>
    <substanceAdministration classCode="SBADM" moodCode="EVN">
      <id root="cdbd33f0-6cda-11d0-192e-000475d90aaa"/>
      <statusCode code="active"/>
      <effectiveTime xsi:type="IVL_TS">
        <low value="20230101"/>
        <high nullFlavor="NA"/>
      </effectiveTime>
      <routeCode code="PO" displayName="Oral"/>
      <doseQuantity value="10" unit="mg"/>
      <rateQuantity value="1" unit="1 times per day"/>
      <consumable>
        <manufacturedProduct classCode="MANU">
          <manufacturedMaterial>
            <code code="198440" displayName="metformin 10mg tablet">
              <originalText>Metformin</originalText>
            </code>
          </manufacturedMaterial>
        </manufacturedProduct>
      </consumable>
    </substanceAdministration>
  </entry>
</section>
```

#### 3. Allergies/Reactions Section
```xml
<section>
  <templateId root="2.16.840.1.113883.10.20.22.2.6.1"/>
  <code code="48765-2" displayName="Allergies, adverse reactions, alerts"/>
  <entry>
    <act classCode="ACT" moodCode="EVN">
      <id root="36e3e930-7b14-11d9-bae4-000374ca6003"/>
      <code code="ALGY"/>
      <statusCode code="active"/>
      <entryRelationship>
        <observation classCode="OBS" moodCode="EVN">
          <code code="ASSERTION"/>
          <statusCode code="completed"/>
          <value xsi:type="CD" code="373270004" displayName="Penicillin allergy">
            <originalText>Penicillin</originalText>
          </value>
          <entryRelationship>
            <observation classCode="OBS" moodCode="EVN">
              <code code="SEV"/>
              <value code="H" displayName="High"/>
            </observation>
          </entryRelationship>
          <entryRelationship>
            <observation classCode="OBS" moodCode="EVN">
              <code code="ROLO" displayName="Reaction"/>
              <value code="24079001" displayName="Rash"/>
            </observation>
          </entryRelationship>
        </observation>
      </entryRelationship>
    </act>
  </entry>
</section>
```

#### 4. Results/Labs Section
```xml
<section>
  <templateId root="2.16.840.1.113883.10.20.22.2.3.1"/>
  <code code="30954-2" displayName="Relevant diagnostic tests and/or laboratory data"/>
  <entry>
    <organizer classCode="BATTERY" moodCode="EVN">
      <id root="7d5a02b0-67a4-11da-8cd6-000d9312bac1"/>
      <code code="57021-8"/>
      <statusCode code="completed"/>
      <effectiveTime value="20231115"/>
      <component>
        <observation classCode="OBS" moodCode="EVN">
          <code code="2345-7" displayName="Glucose">
            <originalText>Glucose</originalText>
          </code>
          <statusCode code="completed"/>
          <effectiveTime value="20231115"/>
          <value xsi:type="PQ" value="120" unit="mg/dL"/>
          <referenceRange>
            <observationRange>
              <value xsi:type="IVL_PQ">
                <low value="70" unit="mg/dL"/>
                <high value="100" unit="mg/dL"/>
              </value>
            </observationRange>
          </referenceRange>
        </observation>
      </component>
    </organizer>
  </entry>
</section>
```

#### 5. Procedures Section
```xml
<section>
  <templateId root="2.16.840.1.113883.10.20.22.2.7.1"/>
  <code code="47519-4" displayName="History of Procedures"/>
  <entry>
    <procedure classCode="PROC" moodCode="EVN">
      <id root="d68b7e32-7885-11d7-9ac0-00508db7d050"/>
      <code code="67412004" displayName="Angiography">
        <originalText>Cardiac Angiography</originalText>
      </code>
      <statusCode code="completed"/>
      <effectiveTime value="20230815"/>
      <performer>
        <assignedEntity>
          <id root="2.16.840.1.113883.4.6" extension="2000000"/>
          <assignedPerson>
            <name>
              <given>John</given>
              <family>Smith</family>
            </name>
          </assignedPerson>
        </assignedEntity>
      </performer>
      <targetSiteCode code="80891009" displayName="Heart"/>
    </procedure>
  </entry>
</section>
```

### Encoding Standards

**Code Systems:**
- ICD-10-CM: Diagnoses and conditions
- RxNorm: Medications and drugs
- LOINC: Laboratory and vital signs
- SNOMED CT: Clinical concepts
- CPT: Procedures and services
- CVX: Immunization/vaccine codes

## FHIR-based Blue Button+ (Modern)

### SMART on FHIR Architecture

```
Patient App
    ↓
OAuth2 Authorization
    ↓
FHIR-enabled EHR API
    ├─ /fhir/Patient
    ├─ /fhir/Condition
    ├─ /fhir/Medication
    ├─ /fhir/Observation
    ├─ /fhir/MedicationStatement
    ├─ /fhir/Procedure
    ├─ /fhir/Immunization
    └─ /fhir/DocumentReference
```

### FHIR Resource Examples

**Patient Resource:**
```json
{
  "resourceType": "Patient",
  "id": "12345",
  "identifier": [{
    "system": "http://acmehealthcare.com/mrn",
    "value": "MRN-12345"
  }],
  "name": [{
    "use": "official",
    "family": "Smith",
    "given": ["John"]
  }],
  "telecom": [{
    "system": "phone",
    "value": "555-1234"
  }],
  "gender": "male",
  "birthDate": "1985-05-15"
}
```

**Condition Resource:**
```json
{
  "resourceType": "Condition",
  "id": "67890",
  "subject": {
    "reference": "Patient/12345"
  },
  "code": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "44054006",
      "display": "Diabetes mellitus type 2"
    }]
  },
  "onsetDateTime": "2015-06-15",
  "clinicalStatus": "active"
}
```

### SMART on FHIR Launch Flow

```
1. Patient initiates from EHR
2. Browser redirected to app with launch code
3. App calls token endpoint with launch code
4. App receives access token and refresh token
5. App retrieves patient context
6. App fetches patient data via FHIR APIs
7. App displays patient information
```

## Blue Button Implementation Considerations

### Data Export Functionality

**Export Formats Needed:**
1. **CCDA XML** - Original Blue Button format
2. **FHIR JSON** - Modern FHIR format
3. **CSV** - Spreadsheet format
4. **PDF** - Human-readable format
5. **Plain Text** - Accessible format

### Data Validation and Transformation

**CCDA to FHIR Mapping:**
```
CCDA Problem Act → Condition Resource
CCDA SubstanceAdministration → MedicationStatement
CCDA Observation (lab) → Observation Resource
CCDA Procedure → Procedure Resource
CCDA Act (allergy) → AllergyIntolerance Resource
CCDA ImmunizationActivity → Immunization Resource
```

### Performance Considerations

**Large Exports:**
- Streaming responses for large datasets
- Pagination for API results
- Async processing for ZIP file generation
- Compression (GZIP for transport, ZIP for download)
- CDN for file distribution

### Security in Data Export

**Security Requirements:**
- Authentication verification before export
- Encryption during transmission
- Audit logging of all exports
- Time-limited access to export files
- Deletion of temp files after delivery

## Third-Party App Integration

### Patient-Authorized Data Access

**OAuth2 Scopes for FHIR:**
```
launch/patient - Patient context
patient/Patient.read - Read patient demographics
patient/Condition.read - Read problems
patient/Medication.read - Read medications
patient/Observation.read - Read observations
patient/MedicationStatement.read - Read med statements
patient/Procedure.read - Read procedures
patient/Immunization.read - Read immunizations
offline_access - Refresh tokens
```

### Data Sharing Agreement

**Apps Must Provide:**
- Clear privacy policy
- Data usage description
- Permissions request explanation
- Data retention policy
- Security measures in place
- Contact information for questions

### App Governance

**Vetting Process:**
1. Security assessment (CVSS vulnerability score)
2. Privacy policy review
3. Data retention compliance
4. User experience assessment
5. Clinical safety review (if applicable)
6. Regular re-certification

## Compliance with Information Blocking Rules

### ONC Requirements (21 CFR Part 2)

**Certified EHRs MUST:**
- Provide access via FHIR API
- Support USCDI data elements
- Enable patient authorization
- Allow third-party app connections
- Publish API documentation
- Not restrict data sharing
- Maintain interoperability

**Exceptions for Information Blocking:**
- Legitimate security concerns
- Compliance with law
- Patient safety concerns (if documented)
- Insufficient documentation from requestor

## Blue Button Testing and Validation

### CCDA Validation

**Tools:**
- HL7 CDA Validator
- NIST C-CDA Test Tool
- Schematron validation
- Conformance testing

**Checklist:**
- Valid XML structure
- Required sections present
- Code systems valid
- Date/time formats correct
- Required narrative text

### FHIR API Testing

**Tools:**
- Postman API testing
- FHIR Testing Tools
- Custom validation scripts

**Test Cases:**
- OAuth2 flow
- Token refresh
- Resource retrieval
- Pagination handling
- Error responses
- Data completeness

## Blue Button User Experience

### Patient Portal Integration

**Export Options:**
1. Click "Download My Health Information"
2. Select data to include (all or specific sections)
3. Choose export format (CCDA, FHIR, PDF, CSV)
4. Receive file download or email
5. Receive encryption key if secure

**Timeline:**
- Immediate (<1 second) - For small datasets
- Background job (5-60 minutes) - For large datasets
- Email delivery - Secure transmission

### Third-Party App Connection

**Patient Flow:**
1. Patient clicks "Connect to Health App"
2. Redirected to authorization screen
3. Reviews requested data access
4. Grants/denies permissions
5. Redirected back to app
6. App starts accessing data

## Compliance Checklist for Blue Button

- [ ] CCDA export functionality implemented
- [ ] FHIR API endpoints published (minimum USCDI)
- [ ] OAuth2 authorization server operational
- [ ] Patient audit logs for all data access
- [ ] Export formats include XML, PDF, CSV, JSON
- [ ] Performance targets met (<30 sec for typical export)
- [ ] Security testing completed (penetration, crypto)
- [ ] Accessibility tested (WCAG 2.1 AA)
- [ ] Documentation published and tested
- [ ] Third-party app vetting process documented
- [ ] User training materials created
- [ ] Regulatory compliance verified (ONC, FDA)

## Tools and Libraries

**CCDA Parsing:**
- Blue Button Plus Python library
- CCDA Parser (JavaScript)
- CDAUtil (Java)

**FHIR Libraries:**
- HAPI FHIR (Java)
- FHIR.js (JavaScript)
- fhirpy (Python)

**Testing Tools:**
- Postman (API testing)
- FHIR Test Tool
- NIST C-CDA Validator
- Blue Button Test Harness
