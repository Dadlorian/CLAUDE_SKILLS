# HL7 v2 Interface Design Guide

**Version**: 5.0.2
**Last Updated**: 2025-11-19
**Status**: Production Ready
**Standards Compliance**: HL7 v2.5.1, ISO 8859-1/UTF-8, HIPAA, HITRUST

---

## Executive Summary

This comprehensive guide establishes production standards for implementing, maintaining, and integrating HL7 v2 messaging interfaces across healthcare systems. HL7 v2 remains the dominant standard for clinical data exchange despite FHIR adoption.

---

## 1. HL7 v2 Message Structure Standards

### 1.1 Character Encoding & Delimiters

**Mandatory Encoding Standards:**
```
Character Set:      ISO-8859-1 (Latin-1) - Primary
Alternative:        UTF-8 (for non-Latin text, must be declared)
Encoding Header:     MSH-3-1: ASCII|UNICODE UTF-8|UNICODE UTF-16

Delimiter Definitions:
  Field Separator:   | (pipe)
  Component Sep:     ^ (caret)
  Subcomponent Sep:  & (ampersand)
  Escape Character:  \ (backslash)
  Repetition Sep:    ~ (tilde)

MSH Segment Format:
  MSH|^~\&|SENDER|FACILITY|RECEIVER|FAC2|20251119101500||ADT^A01^ADT_A01|MSG-ID|P|2.5.1
      ↑    ↑      ↑       ↑        ↑       ↑
      |    Field/Component/Subcomponent/Escape/Repetition
      Field Separator (must follow MSH)
```

**Encoding Validation Rules:**
- All messages must declare encoding in MSH-3
- UTF-8 messages must include BOM (Byte Order Mark) if using UTF-16
- Invalid characters must be escaped using \ prefix
- Segment terminator: Carriage Return (CR) - mandatory
- Never use Line Feed (LF) alone; always pair with CR

### 1.2 Message Segment Standards

**Required Segment Types (Mandatory):**

**MSH - Message Header:**
```
MSH|^~\&|SendingApp|SendingFac|ReceivingApp|ReceivingFac|
    20251119101500+0500||ADT^A01^ADT_A01|MSG-ID-123|P|2.5.1|
    ||||||||LAB^LIS_INTEGRATION

Mandatory Fields:
  MSH-1: Field separator (|)
  MSH-2: Encoding characters (^~\&)
  MSH-3: Sending application
  MSH-4: Sending facility
  MSH-5: Receiving application
  MSH-6: Receiving facility
  MSH-7: Timestamp (YYYYMMDDHHMM[SS[.SSSS]][+/-HHMM])
  MSH-9: Message type (MSG^TRIGGER^MESSAGE_STRUCTURE)
  MSH-10: Message control ID (unique identifier)
  MSH-11: Processing ID (P=Production, T=Test, D=Debug)
  MSH-12: Version ID (2.5.1 minimum)
```

**EVN - Event Type (Conditional):**
```
EVN|A01|20251119101500|20251119101000||ADMITTING_USER^Admin

EVN-1: Event type code (A01-A52)
EVN-2: Recorded date/time
EVN-3: Date/time of event
EVN-4: Event reason code
EVN-5: Operator ID
```

**PID - Patient Identification (Mandatory):**
```
PID|1||MRN-12345^^^HOSPITAL~SSN123456789^^^SSA~OLDMRN^^^FACILITY||
    DOE^JOHN^A^JR||19850315|M|||123 MAIN ST^^SPRINGFIELD^IL^62701^USA|
    |217-555-1234|(217)555-4567|DOE^JANE|S|||||||||||||||||||||

PID-1: Set ID
PID-2: Patient ID (deprecated, use PID-3)
PID-3: Patient identifier list (MRN, SSN, etc.)
PID-4: Alternate patient ID
PID-5: Patient name (surname^given^middle^prefix^suffix)
PID-7: Date/time of birth (YYYYMMDD)
PID-8: Sex (M|F|O|U)
PID-11: Patient address
PID-13: Phone number (home)
PID-14: Phone number (business)
PID-15: Primary language
PID-16: Marital status
PID-19: SSN
PID-30: Patient death indicator
```

**OBX - Observation/Result (Lab/Imaging):**
```
OBX|1|NM|GLUCOSE^Glucose Level|1|125|mg/dL|70-100|H|||F|||
    20251119101500|USER123

OBX-1: Set ID
OBX-2: Value type (NM=numeric, ST=string, DT=date, TM=time)
OBX-3: Observation identifier (code^text)
OBX-4: Observation sub-ID
OBX-5: Observation value
OBX-6: Units of measure
OBX-7: Reference range
OBX-8: Abnormal flags (L=low, H=high, LL=critical low, HH=critical high)
OBX-11: Observation result status (F=final, P=pending, C=corrected)
OBX-14: Date/time of observation
OBX-15: Producer's ID
```

**RXA - Medication Administration:**
```
RXA|1|1|20251119101500|||25^LISINOPRIL 10MG TABLET^NDC~
    101-19-01^LISINOPRIL 10MG TABLET^RXN|1|||ADMINS123|
    200|20251119|USER123|P|F||||||||||||||||||

RXA-1: Sequence
RXA-3: Date/time started
RXA-5: Administered code
RXA-6: Dose
RXA-7: Route
RXA-11: Administering provider
RXA-15: Substance status
```

**DG1 - Diagnosis (ICD Coding):**
```
DG1|1|ICD-10-CM|E11.9||Type 2 diabetes without complications||
    A|20251119101500||PHYSICIAN123

DG1-1: Sequence
DG1-2: Coding system (ICD-10-CM, SNOMED, etc.)
DG1-3: Diagnosis code
DG1-4: Diagnosis description
DG1-5: Diagnosis description (text)
DG1-6: Diagnosis type (A=Admission, W=Working, F=Final)
DG1-7: Major diagnostic category
DG1-12: Diagnosis datetime
DG1-16: Attending physician
```

### 1.3 Common Message Types

**ADT (Admission/Discharge/Transfer):**
```
Triggers:    A01=Admit, A02=Discharge, A03=Transfer, A04=Registration,
             A05=Pre-admit, A08=Update Patient Info, A40=Merge

Structure:   MSH -> EVN -> PID -> PV1 -> [DG1] -> [OBX] -> [AL1]
```

**ORU (Observation Result Unsolicited):**
```
Triggers:    R01=Unsolicited transmission, R02=Query response

Structure:   MSH -> PID -> OBR -> [OBX] (repeating)
             (OBR = Observation Request segment)
```

**RAS (Pharmacy/Treatment Administration):**
```
Triggers:    A01=Administer dose, A02=Infuse medication

Structure:   MSH -> PID -> ORC -> RXA -> [RXE]
             (ORC = Order segment, RXE = Pharmacy encoded order)
```

**SIU (Schedule Information Unsolicited):**
```
Triggers:    S12=New appointment booking, S13=Appointment rescheduling,
             S14=Appointment cancellation, S15=Appointment discontinuation

Structure:   MSH -> SCH -> [TQ1] -> [RGS] -> [AIS]
             (SCH = Schedule segment for appointments)
```

---

## 2. Message Validation & Integrity

### 2.1 Segment Validation Rules

**Mandatory Validation Checks:**

```
1. Structural Validation
   ✓ All messages must start with MSH segment
   ✓ Segment sequence follows message structure definition
   ✓ Required fields present and non-empty
   ✓ Data type matches specification
   ✓ Field cardinality respected (0..1, 0..*. 1..1)

2. Identifier Validation
   ✓ MRN format matches institutional standard
   ✓ SSN must be 9 digits (if present)
   ✓ Account numbers properly formatted
   ✓ Identifiers are unique within message context

3. Date/Time Validation
   ✓ Dates follow YYYYMMDD format (minimum)
   ✓ Times follow HHMM[SS[.SSSS]] format
   ✓ Timestamps include timezone offset
   ✓ Logical date ordering (birth < admission < discharge)

4. Coding Validation
   ✓ Diagnosis codes valid ICD-10-CM
   ✓ Procedure codes valid CPT or ICD-10-PCS
   ✓ Drug codes valid RxNorm or NDC
   ✓ Observation codes valid LOINC
   ✓ All codes mapped to institutional dictionary

5. Clinical Data Validation
   ✓ Patient gender matches clinical data
   ✓ Medication routes valid for drug type
   ✓ Allergy substances properly coded
   ✓ Lab values in realistic range
   ✓ Dose units appropriate for medication
```

### 2.2 Error Detection & ACK Generation

**Acknowledgment (ACK) Message:**
```
MSH|^~\&|RECEIVING_APP|FAC|SENDING_APP|FAC|
    20251119101500||ACK^A01|ACK-MSG-ID|P|2.5.1
MSA|AA|ORIGINAL_MSG_ID|Message accepted|
    0|||0|0|
ERR||^^^0|322|E|Duplicate MRN - Multiple records for identifier

MSA-1: Acknowledgment code
  AA = Application accept
  AE = Application error
  AR = Application reject
  CA = Commit accept
  CE = Commit error
  CR = Commit reject

MSA-2: Message Control ID (from original message)
MSA-3: Text message
MSA-4: Expected sequence number
MSA-5: Delayed acknowledgment type
MSA-6: Error condition
```

**Error Response Example:**
```
MSH|^~\&|RECEIVING_APP|FAC|SENDING_APP|FAC|
    20251119101500||ACK|ACK-MSG-ID|P|2.5.1
MSA|AE|ORIGINAL_MSG-123|Validation error|
    0|||0|0|
ERR||PID^5^0|101|E|Invalid patient name format: empty surname
ERR||OBX^5^0|304|E|Observation date cannot be in future
```

---

## 3. Transport & Protocol Standards

### 3.1 Connection Protocol Standards

**Minimum Lower Layer Protocol (MLLP):**
```
Block Format:
  <BLOCK_START> message_text <BLOCK_END> <CARRIAGE_RETURN>

  <BLOCK_START>: 0x0B (vertical tab, ASCII 11)
  <BLOCK_END>:   0x1C (file separator, ASCII 28)
  <CR>:          0x0D (carriage return, ASCII 13)

Example (hexadecimal):
  0x0B + [message bytes] + 0x1C + 0x0D

Connection Parameters:
  TCP/IP Port:      Minimum 2575 (privileged, default HL7)
  Timeout:          60 seconds (receive)
  Keep-alive:       Every 30 seconds for idle connections
  TLS/SSL:          Mandatory for all production connections

Example in Python:
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect(('hl7-server', 2575))
  message = b'\x0b' + hl7_message.encode('ascii') + b'\x1c\x0d'
  sock.send(message)
```

**Alternative Transport Protocols:**
```
1. HL7 over HTTP/REST
   POST /hl7/v2/receive
   Content-Type: application/x-hl7-v2+er7

2. HL7 over SFTP (batch processing)
   Encrypted file transfer for high-volume batches

3. HL7 over HTTPS with OAuth 2.0
   Secured REST endpoint for modern integrations

4. Message Queue (RabbitMQ, Kafka)
   For asynchronous processing and buffering
```

### 3.2 Network Security

**Mandatory Security Controls:**
```
1. TLS Encryption
   ✓ TLS 1.2 minimum (TLS 1.3 preferred)
   ✓ RSA 2048-bit minimum or ECDSA P-256
   ✓ Certificate validation (no self-signed in production)
   ✓ Certificate pinning for critical integrations
   ✓ Perfect Forward Secrecy (PFS) required

2. Authentication
   ✓ Mutual TLS (mTLS) for partner integrations
   ✓ Application credentials (unique per interface)
   ✓ Time-based token validation
   ✓ Credential rotation every 90 days

3. Encryption at Rest
   ✓ Message storage: AES-256-GCM
   ✓ Database fields: Encrypt PII columns
   ✓ Audit logs: Encrypt security-sensitive fields
   ✓ Key management: HSM-backed keys

4. Network Access Controls
   ✓ IP whitelisting for known partners
   ✓ Firewall rules: Limit to required ports
   ✓ VPN/private network for critical partners
   ✓ Network segmentation from public internet
```

---

## 4. Message Processing & Handling

### 4.1 Inbound Message Processing

**Standard Processing Pipeline:**
```
1. Transport Layer
   ✓ Receive message over MLLP/TLS
   ✓ Strip MLLP envelope
   ✓ Validate encoding (detect charset)
   ✓ Log raw message (audit trail)

2. Parsing Layer
   ✓ Split into segments (CR delimiter)
   ✓ Parse each segment (field/component delimiters)
   ✓ Build internal message object
   ✓ Handle escaped characters (\ prefix)

3. Validation Layer
   ✓ Check MSH segment present and valid
   ✓ Validate segment sequence against message type
   ✓ Check required fields populated
   ✓ Validate data types and formats
   ✓ Normalize identifiers and codes

4. Business Logic Layer
   ✓ Lookup patient by MRN/identifiers
   ✓ Resolve coding lookups (ICD, RxNorm, LOINC)
   ✓ Apply business rules (duplicate detection, merging)
   ✓ Cross-reference with external systems
   ✓ Apply transformations (unit conversion, value normalization)

5. Storage Layer
   ✓ Write to database atomically
   ✓ Create audit trail entry
   ✓ Store raw message for audit/reprocessing
   ✓ Update caches and indices

6. Response Layer
   ✓ Generate ACK message
   ✓ Send back over same connection
   ✓ Log ACK response
   ✓ Close connection (or keep-alive for next message)
```

**Sequence Example:**
```
Receive:   [MLLP wrapper] ADT^A01 message [MLLP wrapper]
           ↓
Parse:     Extract segments, fields, components
           ↓
Validate:  Check structure, types, cardinality
           ↓
Process:   Database operations, business logic
           ↓
Response:  Generate ACK^A01 message
           ↓
Send:      [MLLP wrapper] ACK message [MLLP wrapper]
```

### 4.2 Error Handling & Retry Logic

**Transient Error Handling:**
```
Retryable Errors:          Non-Retryable Errors:
  - Timeout                  - Malformed message
  - Connection reset         - Invalid identifiers
  - Temporary service down   - Duplicate patient/order
  - Database locked          - Business rule violation
  - Memory exhaustion        - Invalid coding

Retry Algorithm:
  Attempt 1:  Immediate send
  Attempt 2:  Wait 5 seconds, resend
  Attempt 3:  Wait 30 seconds, resend
  Attempt 4:  Wait 5 minutes, resend
  Attempt 5:  Wait 30 minutes, resend

  After 5 attempts: Route to manual review queue
  Retain message for 7 days for operator intervention
```

### 4.3 Duplicate Detection & Handling

**Duplicate Prevention Strategy:**
```
Detection Method:  Message Control ID (MSH-10)
  Store in database: Hash(Sender|MessageID|Timestamp)
  Lookup window: 24 hours
  Action on duplicate:
    - Return ACK with same response as original
    - Log duplicate detection event
    - Alert if >5 duplicates from same sender

Prevention:
  ✓ Implement message persistence queue
  ✓ Idempotent processing (safe to reprocess)
  ✓ Distributed request ID tracking
  ✓ Database unique constraints on business identifiers
```

---

## 5. Specific Integration Patterns

### 5.1 Lab System Integration (LIS)

**ORU (Observation Result Unsolicited) Message:**
```
MSH|^~\&|LABSYSTEM|LAB_FACILITY|EMR|MAIN_FACILITY|
    20251119143000||ORU^R01^ORU_R01|LAB-MSG-001|P|2.5.1
PID|1||MRN-98765^^^EMR||SMITH^JANE^A||19780520|F
OBR|1|ORD-12345^LABSYSTEM|LAB-RES-001|CHEM_PANEL^Chemistry
    Panel^LN||20251119100000|20251119120000
OBX|1|NM|2345-7^GLUCOSE^LN||125|mg/dL|70-100|N|||F
OBX|2|NM|2349-9^SODIUM^LN||138|mmol/L|135-145|N|||F
OBX|3|NM|2823-3^POTASSIUM^LN||4.2|mmol/L|3.5-5.0|N|||F
OBX|4|NM|2075-0^CHLORIDE^LN||102|mmol/L|96-106|N|||F
OBX|5|NM|3094-0^BICARBONATE^LN||24|mmol/L|23-29|N|||F
```

**Required Validations:**
- LOINC codes must be valid and current
- Lab identifiers (specimen ID, accession) unique
- Critical values trigger alerts
- Reference ranges match patient demographics
- Report dates cannot be future dates

### 5.2 Medication Administration (Pharmacy)

**RXA Medication Administration:**
```
MSH|^~\&|PHARMACY|HOSPITAL|EMR|MAIN|
    20251119103000||RAS^A01^RAS_A01|PHARM-MSG-001|P|2.5.1
PID|1||MRN-54321^^^EMR||JOHNSON^ROBERT||19650310|M
ORC|RE|ORD-456^PHARMACY|PHA-456^PHARMACY|
RXA|1|1|20251119103000|||40^LISINOPRIL 10MG TABLET^NDC~
    104-25-45^LISINOPRIL 10MG^RXN|1|TABLET|||NURSE-001|
    200|20251119|NURSE-001|P|F
```

**Required Validations:**
- RxNorm code valid and dose appropriate
- Route valid for medication type
- Patient not on conflicting medications
- Frequency follows clinical guidelines
- No drug-allergy interactions

---

## 6. Monitoring & Auditing

### 6.1 Message Logging Standards

**Required Log Fields:**
```json
{
  "timestamp": "2025-11-19T14:30:00Z",
  "interface_name": "LIS_Integration",
  "direction": "INBOUND",
  "message_type": "ORU^R01",
  "message_id": "LAB-MSG-001",
  "sender_app": "LABSYSTEM",
  "sender_facility": "LAB_FACILITY",
  "receiver_app": "EMR",
  "patient_id": "MRN-98765",
  "status": "ACCEPTED",
  "ack_code": "AA",
  "record_count": 3,
  "processing_time_ms": 245,
  "validation_errors": [],
  "database_records_affected": {
    "observation": 3,
    "result": 3
  }
}
```

**Log Retention:**
- Raw messages: 7 years (regulatory requirement)
- Processing logs: 3 years
- Error logs: 1 year
- Access logs: 1 year
- Immutable storage with cryptographic integrity

### 6.2 Metrics & Alerts

**Key Performance Indicators:**
```
Performance:
  - Message throughput: messages/hour
  - Processing latency: p50, p95, p99 milliseconds
  - ACK response time: seconds
  - Error rate: percentage of messages with errors

Business:
  - ADT messages: admits/transfers/discharges per hour
  - Lab results: test results received per hour
  - Medication administrations: doses recorded per hour
  - Order placements: new orders per hour

Reliability:
  - Interface availability: 99.9% SLA
  - Duplicate message rate: < 0.1%
  - Retransmitted messages: percentage
  - Partner system response times: seconds

Alerting Thresholds:
  Critical: Error rate > 10%, interface down > 30 min
  Warning:  Error rate > 5%, latency > 5 seconds
  Info:     Error rate > 1%, partner system slow
```

---

## 7. Governance & Compliance

### 7.1 Change Management

**Before deploying message changes:**
- [ ] Get approval from all partner systems
- [ ] Update StructureDefinition/message definition
- [ ] Update integration documentation
- [ ] Test in staging environment with real data
- [ ] Validate backward compatibility with legacy systems
- [ ] Plan rollback procedure
- [ ] Announce deployment window 2 weeks in advance
- [ ] Monitor first 100 messages in production
- [ ] Keep previous version available for 30 days

### 7.2 Partner Onboarding

**Required for new interface partner:**
1. Establish transport mechanism (MLLP, sFTP, REST)
2. Configure security (mTLS, VPN, firewall rules)
3. Exchange test credentials
4. Validate message structure in staging
5. Execute end-to-end test with production-like data
6. Sign interface agreement and SLA document
7. Document interface in CMDB
8. Configure monitoring and alerting
9. Plan support escalation path
10. Schedule production cutover

---

## Appendix: Common Message Templates

**ADT^A01 (Patient Admit):**
```
MSH|^~\&|REGISTRATION|HOSPITAL|EMR|FACILITY|
    20251119100000||ADT^A01^ADT_A01|ADT-MSG-001|P|2.5.1
EVN|A01|20251119100000|20251119095500||ADMITTING_USER
PID|1||MRN-11111^^^HOSPITAL||DOE^JOHN^A^JR||19850315|M|||
    123 MAIN ST^^SPRINGFIELD^IL^62701^USA|
PV1|1|I|ICU^301^A^BED01|H|||PHYSICIAN-ID|PHYSICIAN-ID|
    CARDIOLOGY||||A|||PHYSICIAN-ID|||||||||||||||
    20251119100000|20251119100000
DG1|1|ICD-10-CM|I10||Essential hypertension||A
```

**ORU^R01 (Lab Results):**
```
MSH|^~\&|LAB|LABFAC|EMR|FACILITY|20251119143000||ORU^R01|
    LAB-MSG-001|P|2.5.1
PID|1||MRN-22222^^^EMR||SMITH^JANE||19800520|F
OBR|1|ORDER-001^LAB|RESULT-001^LAB|CBC^CBC Panel||20251119100000
OBX|1|NM|5821-4^WHITE BLOOD CELLS^LN||7.5|10*3/uL|4.5-11.0|N|||F
OBX|2|NM|718-7^HEMOGLOBIN^LN||14.2|g/dL|12.0-16.0|N|||F
OBX|3|NM|787-2^HEMATOCRIT^LN||42|%|36-46|N|||F
```

---

**Contact**: HL7 v2 Integration Standards Committee
**Last Reviewed**: 2025-11-19
