# HL7 ADT Message Reference

## Overview

HL7 ADT (Admission, Discharge, Transfer) messages are the most common message type in healthcare interoperability. They communicate patient demographic and visit information between systems. This reference covers ADT message structure, common event types, and implementation patterns.

## HL7 v2.x Message Structure

### Message Components Hierarchy
```
Message
├── Segments (MSH, EVN, PID, PV1, etc.)
│   ├── Fields (separated by |)
│   │   ├── Components (separated by ^)
│   │   │   ├── Sub-components (separated by &)
│   │   │   └── ...
│   │   └── Repetitions (separated by ~)
│   └── ...
└── ...
```

### Standard Delimiters
- **Field Separator**: `|` (pipe)
- **Component Separator**: `^` (caret)
- **Repetition Separator**: `~` (tilde)
- **Escape Character**: `\` (backslash)
- **Sub-component Separator**: `&` (ampersand)

### Encoding Characters
Defined in MSH-2: `^~\&`

## Common ADT Event Types

### A01 - Admit/Visit Notification
Patient admitted to inpatient setting or registered for outpatient visit.

**Use Cases**:
- Inpatient admission
- Emergency department registration
- Outpatient clinic registration
- Observation admission

**Required Segments**: MSH, EVN, PID, PV1

### A02 - Transfer a Patient
Patient transferred to a new location within the facility.

**Use Cases**:
- Transfer to different nursing unit
- Transfer to ICU
- Transfer to different bed
- Change in attending physician

**Required Segments**: MSH, EVN, PID, PV1

### A03 - Discharge/End Visit
Patient discharged from inpatient setting or outpatient visit completed.

**Use Cases**:
- Inpatient discharge
- Emergency department departure
- Outpatient visit completion
- Transfer to another facility

**Required Segments**: MSH, EVN, PID, PV1

### A04 - Register a Patient
Patient registration without admission (outpatient context).

**Use Cases**:
- Pre-admission registration
- Outpatient registration
- Patient enrollment

**Required Segments**: MSH, EVN, PID, PV1

### A05 - Pre-admit a Patient
Patient pre-registered for upcoming admission.

**Use Cases**:
- Scheduled surgery admission
- Planned inpatient admission

**Required Segments**: MSH, EVN, PID, PV1

### A08 - Update Patient Information
Update to patient demographic or visit information.

**Use Cases**:
- Name change
- Address update
- Insurance update
- Visit information correction

**Required Segments**: MSH, EVN, PID, PV1

### A11 - Cancel Admit/Visit Notification
Cancellation of a previous A01 (admission).

**Required Segments**: MSH, EVN, PID, PV1

### A13 - Cancel Discharge/End Visit
Cancellation of a previous A03 (discharge).

**Required Segments**: MSH, EVN, PID, PV1

### A28 - Add Person Information
Add a new person to the system (not encounter-specific).

**Required Segments**: MSH, EVN, PID

### A31 - Update Person Information
Update person information (not encounter-specific).

**Required Segments**: MSH, EVN, PID

### A34 - Merge Patient Information
Merge two patient records (patient identified as duplicate).

**Required Segments**: MSH, EVN, PID, MRG

### A40 - Merge Patient - Internal ID
Merge patients using internal patient identifiers.

**Required Segments**: MSH, EVN, PID, MRG

## Segment Definitions

### MSH - Message Header Segment
Contains message metadata and routing information.

**Structure**:
```
MSH|^~\&|SENDING_APP|SENDING_FACILITY|RECEIVING_APP|RECEIVING_FACILITY|TIMESTAMP||MSG_TYPE^EVENT|MSG_CONTROL_ID|PROCESSING_ID|VERSION_ID
```

**Fields**:
```
MSH-1: Field Separator (|)
MSH-2: Encoding Characters (^~\&)
MSH-3: Sending Application
MSH-4: Sending Facility
MSH-5: Receiving Application
MSH-6: Receiving Facility
MSH-7: Date/Time of Message (YYYYMMDDHHMMSS)
MSH-8: Security (optional)
MSH-9: Message Type (ADT^A01, ADT^A03, etc.)
MSH-10: Message Control ID (unique identifier)
MSH-11: Processing ID (P=Production, T=Training, D=Debugging)
MSH-12: Version ID (2.3, 2.4, 2.5, 2.5.1, etc.)
```

**Example**:
```
MSH|^~\&|EPIC|EPICADT|LAB|LABSYS|202311190830||ADT^A01|MSG00001|P|2.5
```

### EVN - Event Type Segment
Contains information about the trigger event.

**Fields**:
```
EVN-1: Event Type Code (A01, A03, etc.)
EVN-2: Recorded Date/Time (when event recorded)
EVN-3: Date/Time Planned Event
EVN-4: Event Reason Code
EVN-5: Operator ID (who entered the event)
EVN-6: Event Occurred (actual event date/time)
```

**Example**:
```
EVN|A01|20231119083000|||JOHNDOE|20231119082500
```

### PID - Patient Identification Segment
Contains patient demographic and identification information.

**Fields**:
```
PID-1: Set ID - PID (usually 1)
PID-2: Patient ID (legacy, often empty)
PID-3: Patient Identifier List (MRN, Account #, etc.)
       Format: ID^ID_TYPE^ASSIGNING_AUTHORITY
PID-4: Alternate Patient ID
PID-5: Patient Name
       Format: LAST^FIRST^MIDDLE^SUFFIX^PREFIX
PID-6: Mother's Maiden Name
PID-7: Date/Time of Birth (YYYYMMDD)
PID-8: Administrative Sex (M, F, U, O)
PID-9: Patient Alias
PID-10: Race
PID-11: Patient Address
        Format: STREET^LINE2^CITY^STATE^ZIP^COUNTRY
PID-12: County Code
PID-13: Phone Number - Home
        Format: (NNN)NNN-NNNN
PID-14: Phone Number - Business
PID-15: Primary Language
PID-16: Marital Status
PID-17: Religion
PID-18: Patient Account Number
PID-19: SSN - Patient
PID-20: Driver's License Number
PID-21: Mother's Identifier
PID-22: Ethnic Group
PID-23: Birth Place
PID-24: Multiple Birth Indicator
PID-25: Birth Order
PID-26: Citizenship
PID-27: Veterans Military Status
PID-28: Nationality
PID-29: Patient Death Date and Time
PID-30: Patient Death Indicator (Y/N)
```

**Example**:
```
PID|1||MRN123456^^^FACILITY^MRN~SSN987654321^^^SSN||DOE^JOHN^ROBERT^JR^MR||19800115|M||W^White^HL70005|123 MAIN ST^^ANYTOWN^CA^12345^USA|||||||12345678|987-65-4321||||N||||||||N
```

### PD1 - Patient Additional Demographic
Additional patient demographic and marketing information.

**Fields**:
```
PD1-1: Living Dependency
PD1-2: Living Arrangement
PD1-3: Patient Primary Facility
PD1-4: Patient Primary Care Provider
       Format: ID^LAST^FIRST^MI^SUFFIX^PREFIX^DEGREE^SOURCE^ID_TYPE
PD1-5: Student Indicator
PD1-6: Handicap
PD1-7: Living Will Code
PD1-8: Organ Donor Code
PD1-9: Separate Bill
PD1-10: Duplicate Patient
PD1-11: Publicity Code
PD1-12: Protection Indicator (Y/N)
```

### NK1 - Next of Kin/Associated Parties
Emergency contact and next of kin information.

**Fields**:
```
NK1-1: Set ID - NK1
NK1-2: Name
       Format: LAST^FIRST^MIDDLE^SUFFIX^PREFIX
NK1-3: Relationship (C=Emergency Contact, E=Employer, F=Federal Agency, etc.)
NK1-4: Address
NK1-5: Phone Number
NK1-6: Business Phone Number
NK1-7: Contact Role
NK1-8: Start Date
NK1-9: End Date
NK1-10: Next of Kin/Associated Party's Job Title
NK1-11: Next of Kin/Associated Party's Job Code/Class
NK1-12: Next of Kin/Associated Party's Employee Number
NK1-13: Organization Name
```

**Example**:
```
NK1|1|DOE^JANE^MARIE||123 MAIN ST^^ANYTOWN^CA^12345|(555)555-1234||C|||||||||||||||||
```

### PV1 - Patient Visit
Information about the patient's visit or encounter.

**Fields**:
```
PV1-1: Set ID - PV1 (usually 1)
PV1-2: Patient Class (E=Emergency, I=Inpatient, O=Outpatient, etc.)
PV1-3: Assigned Patient Location
       Format: NURSING_UNIT^ROOM^BED^FACILITY^BED_STATUS
PV1-4: Admission Type (E=Emergency, R=Routine, etc.)
PV1-5: Preadmit Number
PV1-6: Prior Patient Location
PV1-7: Attending Doctor
       Format: ID^LAST^FIRST^MI^SUFFIX^PREFIX^DEGREE^SOURCE^ID_TYPE
PV1-8: Referring Doctor
PV1-9: Consulting Doctor
PV1-10: Hospital Service (MED, SUR, OBS, etc.)
PV1-11: Temporary Location
PV1-12: Preadmit Test Indicator
PV1-13: Re-admission Indicator
PV1-14: Admit Source
PV1-15: Ambulatory Status
PV1-16: VIP Indicator
PV1-17: Admitting Doctor
PV1-18: Patient Type
PV1-19: Visit Number (Encounter ID)
PV1-20: Financial Class
PV1-21: Charge Price Indicator
PV1-22: Courtesy Code
PV1-23: Credit Rating
PV1-24: Contract Code
PV1-25: Contract Effective Date
PV1-26: Contract Amount
PV1-27: Contract Period
PV1-28: Interest Code
PV1-29: Transfer to Bad Debt Code
PV1-30: Transfer to Bad Debt Date
PV1-31: Bad Debt Agency Code
PV1-32: Bad Debt Transfer Amount
PV1-33: Bad Debt Recovery Amount
PV1-34: Delete Account Indicator
PV1-35: Delete Account Date
PV1-36: Discharge Disposition
PV1-37: Discharged to Location
PV1-38: Diet Type
PV1-39: Servicing Facility
PV1-40: Bed Status
PV1-41: Account Status
PV1-42: Pending Location
PV1-43: Prior Temporary Location
PV1-44: Admit Date/Time
PV1-45: Discharge Date/Time
PV1-50: Alternate Visit ID
```

**Example**:
```
PV1|1|I|3N^301^01^MAIN^1|||123456^SMITH^JOHN^A^^DR^MD||123456^JONES^MARY^B^^DR^MD|MED||||R||||123456^BROWN^JAMES^C^^DR^MD||V123456789|||||||||||||||||||||||||202311190830|202311210900
```

### PV2 - Patient Visit - Additional Information
Additional visit-related information.

**Fields**:
```
PV2-1: Prior Pending Location
PV2-2: Accommodation Code
PV2-3: Admit Reason
PV2-8: Expected Discharge Date/Time
PV2-9: Expected Discharge Disposition
PV2-47: Expected Discharge Date
```

### IN1 - Insurance
Primary insurance information.

**Fields**:
```
IN1-1: Set ID - IN1
IN1-2: Insurance Plan ID
IN1-3: Insurance Company ID
IN1-4: Insurance Company Name
IN1-5: Insurance Company Address
IN1-15: Plan Type
IN1-16: Name of Insured
IN1-17: Insured's Relationship to Patient
IN1-36: Policy Number
IN1-49: Insured's ID Number
```

### AL1 - Patient Allergy Information
Allergy and adverse reaction information.

**Fields**:
```
AL1-1: Set ID - AL1
AL1-2: Allergen Type Code (DA=Drug allergy, FA=Food allergy, etc.)
AL1-3: Allergen Code/Mnemonic/Description
AL1-4: Allergy Severity Code (SV=Severe, MO=Moderate, MI=Mild, U=Unknown)
AL1-5: Allergy Reaction Code (Anaphylaxis, Rash, etc.)
AL1-6: Identification Date
```

**Example**:
```
AL1|1|DA|^PENICILLIN|SV|ANAPHYLAXIS~RASH
```

### DG1 - Diagnosis
Diagnosis information for the encounter.

**Fields**:
```
DG1-1: Set ID - DG1
DG1-2: Diagnosis Coding Method (I9=ICD-9, I10=ICD-10)
DG1-3: Diagnosis Code
DG1-4: Diagnosis Description
DG1-5: Diagnosis Date/Time
DG1-6: Diagnosis Type (A=Admitting, F=Final, W=Working)
```

**Example**:
```
DG1|1|I10|J18.9^Pneumonia, unspecified organism||20231119|F
```

### MRG - Merge Patient Information
Used in merge messages (A34, A40) to identify the old/incorrect patient.

**Fields**:
```
MRG-1: Prior Patient Identifier List (patient being merged FROM)
MRG-2: Prior Alternate Patient ID
MRG-3: Prior Patient Account Number
MRG-4: Prior Patient ID
MRG-5: Prior Visit Number
MRG-6: Prior Alternate Visit ID
MRG-7: Prior Patient Name
```

**Example**:
```
MRG|OLDMRN123^^^FACILITY^MRN|||||OLDNAME^PATIENT
```

## Complete ADT Message Examples

### A01 - Inpatient Admission
```
MSH|^~\&|EPIC|MAIN_HOSPITAL|LABSYS|LABSYS|20231119083000||ADT^A01|MSG00001|P|2.5
EVN|A01|20231119083000|||REGCLERK^REGISTRATION^CLERK|20231119082500
PID|1||MRN123456^^^MAIN_HOSPITAL^MRN~SSN987654321^^^SSN||DOE^JOHN^ROBERT^JR^MR||19800115|M||W^White^HL70005|123 MAIN ST^^ANYTOWN^CA^12345^USA|(555)555-1234|(555)555-5678||S|CHR|12345678|987-65-4321||||N||||||||N
PD1|||MAIN_HOSPITAL^^12345|123456^SMITH^JOHN^A^^DR^MD^^^^^NPI
NK1|1|DOE^JANE^MARIE|SPO^Spouse|123 MAIN ST^^ANYTOWN^CA^12345|(555)555-1234||C
PV1|1|I|3N^301^01^MAIN_HOSPITAL|||123456^SMITH^JOHN^A^^DR^MD|123456^JONES^MARY^B^^DR^MD||MED||||R||||123456^SMITH^JOHN^A^^DR^MD||V123456789|||||||||||||||||||||||||20231119083000
PV2|||Pneumonia
IN1|1|PLAN001|INS001|BLUE CROSS BLUE SHIELD|PO BOX 12345^^SACRAMENTO^CA^95814|||||||||||DOE^JOHN^ROBERT|SEL|19800115|123 MAIN ST^^ANYTOWN^CA^12345||||||||||||||||987654321
AL1|1|DA|^PENICILLIN|SV|ANAPHYLAXIS~RASH|20200101
DG1|1|I10|J18.9^Pneumonia, unspecified organism||20231119|A
```

### A03 - Patient Discharge
```
MSH|^~\&|EPIC|MAIN_HOSPITAL|LABSYS|LABSYS|20231121090000||ADT^A03|MSG00002|P|2.5
EVN|A03|20231121090000|||NURSEDISCHARGE|20231121085000
PID|1||MRN123456^^^MAIN_HOSPITAL^MRN||DOE^JOHN^ROBERT^JR^MR||19800115|M
PV1|1|I|3N^301^01^MAIN_HOSPITAL|||123456^SMITH^JOHN^A^^DR^MD||||MED||||||123456^SMITH^JOHN^A^^DR^MD||V123456789|||||||||||||||||||||||01^Home^HL70112|||||20231119083000|20231121090000
DG1|1|I10|J18.9^Pneumonia, unspecified organism||20231121|F
DG1|2|I10|E11.9^Type 2 diabetes mellitus without complications||20231121|F
```

### A08 - Update Patient Information
```
MSH|^~\&|EPIC|MAIN_HOSPITAL|LABSYS|LABSYS|20231119100000||ADT^A08|MSG00003|P|2.5
EVN|A08|20231119100000|||ADMITCLERK
PID|1||MRN123456^^^MAIN_HOSPITAL^MRN||DOE^JOHN^ROBERT^SR^MR||19800115|M||W^White^HL70005|456 NEW ST^^NEWTOWN^CA^54321^USA|(555)555-9999|(555)555-5678||M|CHR|12345678|987-65-4321
PV1|1|I|3N^301^01^MAIN_HOSPITAL||||||||||||||||||V123456789
```

### A34 - Merge Patient Information
```
MSH|^~\&|EPIC|MAIN_HOSPITAL|LABSYS|LABSYS|20231119110000||ADT^A34|MSG00004|P|2.5
EVN|A34|20231119110000|||DATASTEWARD
PID|1||MRN123456^^^MAIN_HOSPITAL^MRN||DOE^JOHN^ROBERT^JR^MR||19800115|M
MRG|MRN789012^^^MAIN_HOSPITAL^MRN|||||DOE^JON^R
```

## Message Acknowledgment (ACK)

Every ADT message should receive an acknowledgment.

### Positive Acknowledgment (AA - Application Accept)
```
MSH|^~\&|LABSYS|LABSYS|EPIC|MAIN_HOSPITAL|20231119083001||ACK^A01|MSG00001ACK|P|2.5
MSA|AA|MSG00001|Message accepted successfully
```

### Error Acknowledgment (AE - Application Error)
```
MSH|^~\&|LABSYS|LABSYS|EPIC|MAIN_HOSPITAL|20231119083001||ACK^A01|MSG00001ACK|P|2.5
MSA|AE|MSG00001|Patient not found in receiving system
ERR|||207^Application internal error^HL70357
```

### Acknowledgment Codes
- **AA**: Application Accept - Message accepted
- **AE**: Application Error - Message rejected due to error
- **AR**: Application Reject - Message rejected for business reasons
- **CA**: Commit Accept (for enhanced mode)
- **CE**: Commit Error
- **CR**: Commit Reject

## Data Types and Formatting

### Date/Time Formats
- **YYYY**: Year (e.g., 2023)
- **YYYYMM**: Year and month (e.g., 202311)
- **YYYYMMDD**: Complete date (e.g., 20231119)
- **YYYYMMDDHHMM**: Date and time to minute (e.g., 202311190830)
- **YYYYMMDDHHMMSS**: Complete date and time (e.g., 20231119083045)
- **YYYYMMDDHHMMSS.SSSS**: With fractional seconds

### Extended Composite ID
Format: `ID^ID_TYPE^ASSIGNING_AUTHORITY^ID_TYPE_CODE`

Example: `MRN123456^^^FACILITY^MRN`

### Extended Person Name (XPN)
Format: `FAMILY^GIVEN^MIDDLE^SUFFIX^PREFIX^DEGREE^NAME_TYPE`

Example: `DOE^JOHN^ROBERT^JR^MR^^^L` (L=Legal Name)

### Extended Address (XAD)
Format: `STREET^OTHER_DESIGNATION^CITY^STATE^ZIP^COUNTRY^ADDRESS_TYPE^OTHER_GEOGRAPHIC_DESIGNATION`

Example: `123 MAIN ST^APT 4B^ANYTOWN^CA^12345^USA^H` (H=Home)

### Extended Telecommunication (XTN)
Format: `[(999)]999-9999^USE^EQUIPMENT_TYPE^EMAIL^COUNTRY_CODE^AREA_CODE^LOCAL_NUMBER^EXTENSION`

Example: `(555)555-1234^PRN^PH` (PRN=Primary, PH=Telephone)

## Common Code Sets

### Patient Class (PV1-2)
- **E**: Emergency
- **I**: Inpatient
- **O**: Outpatient
- **P**: Preadmit
- **R**: Recurring patient
- **B**: Obstetrics
- **C**: Commercial Account
- **N**: Not Applicable
- **U**: Unknown

### Admission Type (PV1-4)
- **A**: Accident
- **C**: Elective
- **E**: Emergency
- **L**: Labor and Delivery
- **N**: Newborn
- **R**: Routine
- **U**: Urgent

### Discharge Disposition (PV1-36)
- **01**: Discharged to home or self care
- **02**: Discharged/transferred to short-term general hospital
- **03**: Discharged/transferred to skilled nursing facility (SNF)
- **04**: Discharged/transferred to intermediate care facility (ICF)
- **05**: Discharged/transferred to another type of institution
- **06**: Discharged/transferred to home under care of home health service
- **07**: Left against medical advice or discontinued care
- **20**: Expired (died)
- **50**: Hospice - home
- **51**: Hospice - medical facility

### Administrative Sex (PID-8)
- **M**: Male
- **F**: Female
- **O**: Other
- **U**: Unknown
- **A**: Ambiguous
- **N**: Not applicable

### Marital Status (PID-16)
- **A**: Separated
- **D**: Divorced
- **M**: Married
- **S**: Single
- **W**: Widowed
- **C**: Common law
- **P**: Domestic partner
- **U**: Unknown

## Best Practices

### Message Construction
1. **Always include required segments** (MSH, EVN, PID, PV1 for most ADT events)
2. **Use consistent field delimiters** across all messages
3. **Populate MSH-10 with unique message control IDs**
4. **Include timestamp in MSH-7** (current date/time when message created)
5. **Specify correct HL7 version** in MSH-12

### Patient Identification
1. **Always send multiple patient identifiers** (MRN, Account Number, SSN)
2. **Include assigning authority** in all identifiers
3. **Format names consistently** (LAST^FIRST^MIDDLE^SUFFIX^PREFIX)
4. **Validate SSN format** before sending (no dashes in HL7)

### Error Handling
1. **Implement acknowledgment processing** (handle AA, AE, AR)
2. **Log all messages** for troubleshooting
3. **Implement retry logic** for rejected messages
4. **Monitor error queues** regularly
5. **Document custom Z-segments** clearly

### Data Quality
1. **Validate required fields** before sending
2. **Remove leading/trailing spaces** from all fields
3. **Escape special characters** properly (\F\, \S\, \T\, \E\, \R\)
4. **Use standard code sets** when available
5. **Validate date/time formats**

### Security
1. **Encrypt messages in transit** (TLS/SSL)
2. **Authenticate sending systems**
3. **Implement audit logging**
4. **Sanitize data** (remove unnecessary PHI)
5. **Comply with HIPAA** minimum necessary rule

## Escape Sequences

- `\F\`: Field separator (|)
- `\S\`: Component separator (^)
- `\T\`: Sub-component separator (&)
- `\R\`: Repetition separator (~)
- `\E\`: Escape character (\)
- `\.br\`: Line break (for formatting text)
- `\Xnn\`: Hexadecimal data (nn = hex characters)

**Example**:
```
Patient name with apostrophe: DOE^JOHN\S\JACK
Message with pipe character: This is text with \F\ character
```

## Testing Strategies

### Unit Testing
1. Test each event type (A01, A03, A08, etc.)
2. Test required vs. optional segments
3. Test with missing data
4. Test with maximum field lengths
5. Test special characters and escape sequences

### Integration Testing
1. End-to-end message flow testing
2. Acknowledgment handling
3. Error scenario testing
4. Performance testing (message throughput)
5. Concurrent message handling

### Validation Tools
- **HL7 Inspector**: Free HL7 message viewer
- **7Edit**: HL7 message editor
- **Mirth Connect**: Open-source integration engine with testing capabilities
- **HL7 Soup**: Online HL7 message parser

## References

- **HL7 International**: https://www.hl7.org/
- **HL7 Version 2.5.1 Standard**: Official specification
- **HL7 Version 2.7 Standard**: Latest v2.x specification
- **NIST HL7 V2 Testing**: https://hl7v2-iz-r1.5-testing.nist.gov/
- **Caristix HL7 Resources**: https://www.caristix.com/hl7-resources/

---

**Document Version**: 1.0
**Last Updated**: November 2024
**Author**: Healthcare Technology Team
**Classification**: Public - Educational Use
