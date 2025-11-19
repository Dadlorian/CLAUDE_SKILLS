# HL7 v2.x Reference Guide

## Overview

HL7 v2.x is a standards framework for exchanging clinical and administrative data between healthcare applications. It defines message structures and segments for healthcare workflows.

## Message Structure

### Basic Format
```
MSH|^~\&|SENDING_APP|SENDING_FAC|RECV_APP|RECV_FAC|20231119120000||ADT^A01|MSG001|P|2.5.1
PID|||12345^^^MRN||DOE^JOHN||19700101|M||...
```

### Key Components

1. **Field Separator (|)** - Separates fields
2. **Component Separator (^)** - Separates components within fields
3. **Repetition Separator (~)** - Separates repetitions
4. **Escape Character (\)** - Escapes special characters
5. **Sub-component Separator (&)** - Separates subcomponents

## Common Segments

| Segment | Purpose | Example |
|---------|---------|---------|
| MSH | Message Header | Sender, receiver, timestamp |
| PID | Patient Identification | Demographics, MRN, DOB |
| PV1 | Patient Visit | Admission, location, insurance |
| OBX | Observation Result | Lab values, vital signs |
| ORC | Order Control | Order details, status |
| RXE | Prescription/Encoded Order | Medication orders |
| DG1 | Diagnosis | Patient diagnoses |
| NK1 | Next of Kin | Emergency contacts |
| PD1 | Patient Additional Demo | Primary care provider |
| AL1 | Allergy Information | Allergies, reactions |

## Message Types

| Type | Code | Purpose |
|------|------|---------|
| Admission | ADT^A01 | Patient admission |
| Discharge | ADT^A03 | Patient discharge |
| Transfer | ADT^A02 | Patient transfer |
| Update Demographics | ADT^A08 | Patient info update |
| Order | OMG^O19 | General order message |
| Lab Order | ORM^O01 | Lab specific orders |
| Lab Result | ORU^R01 | Lab results reporting |
| Pharmacy | RGV^O15 | Pharmacy/medication orders |
| Referral | REF^I12 | Patient referral |

## Data Types

- **ST** - String
- **DT** - Date (YYYYMMDD)
- **TM** - Time (HHMMSS)
- **DTM** - Date/Time (YYYYMMDDHHmmss)
- **NM** - Numeric
- **CX** - Extended Composite ID (for identifiers)
- **XPN** - Extended Person Name
- **XAD** - Extended Address
- **XTN** - Extended Telecommunication Number
- **CE** - Coded Element
- **CF** - Coded Element for HL7 Defined Tables
- **CWE** - Coded with Exceptions
- **XCN** - Extended Composite ID Number and Name

## Encoding Rules

### Field Separator Declaration
```
MSH|^~\&|...
     ^^^^
     ||||
     |||Escape character
     ||Sub-component separator
     |Component separator
     Repetition separator
```

### Special Character Handling
```
\S\ = Component separator (^)
\T\ = Sub-component separator (&)
\E\ = Escape character (\)
\R\ = Repetition separator (~)
\F\ = Field separator (|)
```

## Common Workflows

### 1. Admission/Discharge/Transfer (ADT)
```
A01 - Admit/Visit Notification
A02 - Transfer a patient
A03 - Discharge/End visit
A04 - Register a patient
A08 - Update patient information
```

### 2. Order/Results (ORM/ORU)
```
ORM - Order message
ORU - Unsolicited transmission of observation results
```

### 3. Pharmacy (RGV)
```
RGV - Pharmacy/treatment encoded order
```

## Versions

| Version | Release | Status |
|---------|---------|--------|
| 2.3.1 | 1998 | Archived |
| 2.4 | 2000 | Supported |
| 2.5 | 2003 | Legacy |
| 2.5.1 | 2007 | Production |
| 2.6 | 2011 | Production |
| 2.7 | 2015 | Current |
| 2.8 | 2020 | Latest |

## Implementation Considerations

### Message Parsing
- Handle optional segments
- Deal with field repetitions
- Manage escape sequences
- Validate segment sequences

### Validation
- Check required fields
- Validate field types
- Ensure identifier uniqueness
- Verify segment ordering

### Error Handling
- ACK (Application Accept Acknowledgment)
- NAK (Negative Acknowledgment)
- MSA segment for responses

### Common Challenges
- Multiple identifiers per patient
- Different date/time formats
- Character encoding issues
- Backward compatibility with v2.3

## Integration Points

- **EHR Systems** - ADT feeds, order placement
- **Lab Systems** - Order submission, result transmission
- **Pharmacy Systems** - Medication order routing
- **Imaging Systems** - Order and result management
- **Billing Systems** - Patient demographics and visit info

## Performance Tips

1. Use MLLP (Minimal Lower Layer Protocol) for TCP transport
2. Implement batch processing for volume
3. Cache frequently accessed segments
4. Use efficient string parsing libraries
5. Monitor message queue depth

## Compliance Notes

- HIPAA requires encryption of HL7 messages in transit
- Implement non-repudiation for critical messages
- Maintain audit logs of all message exchanges
- Use SFTP or MLLP over TLS for secure transmission
- Implement message acknowledgment and retry logic
