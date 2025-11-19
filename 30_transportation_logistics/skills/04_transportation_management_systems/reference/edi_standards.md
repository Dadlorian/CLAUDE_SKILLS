# EDI Standards for Transportation Management

## Overview

Electronic Data Interchange (EDI) is the computer-to-computer exchange of business documents in a standard electronic format. In transportation management, EDI enables seamless communication between shippers, carriers, and third-party logistics providers without manual intervention.

## ANSI ASC X12 Standards

The ANSI ASC X12 (Accredited Standards Committee X12) develops and maintains EDI standards for cross-industry exchange of business transactions.

### Core Transportation Transaction Sets

#### EDI 204 - Motor Carrier Load Tender

**Purpose**: Shipper sends load tender to carrier requesting transportation services

**Key Elements**:
- Shipment identification and reference numbers
- Bill of lading (BOL) number
- Origin and destination locations
- Pickup and delivery date/time windows
- Equipment type and quantity
- Weight, cube, and piece count
- Special services and requirements
- Rate and charges (optional)

**Sample Structure**:
```
ST*204*0001~
B2*00*SHIPMENT123*1234567890~
B2A*00~
L11*BOL123456*BM~
MS3*CHICAGO*IL*US~
MS3*DALLAS*TX*US~
AT8*G*L*4800*3500~
SE*15*0001~
```

**Business Process**:
1. Shipper creates shipment in TMS
2. TMS generates EDI 204
3. Carrier receives tender
4. Carrier responds with EDI 990 (accept/decline)

#### EDI 990 - Response to a Load Tender

**Purpose**: Carrier accepts or declines a load tender

**Key Elements**:
- Reference to original 204 shipment
- Acceptance or rejection code
- Rejection reason (if declined)
- Pro number assignment (if accepted)
- Estimated pickup and delivery dates

**Sample Structure**:
```
ST*990*0001~
B1*SHIPMENT123*1234567890*PP~
L11*ACCEPT*ZZ~
L11*PRO987654*PR~
SE*5*0001~
```

**Response Codes**:
- `A` - Accepted
- `D` - Declined
- `R` - Rejected due to rate
- `C` - Rejected due to capacity

#### EDI 214 - Transportation Carrier Shipment Status

**Purpose**: Carrier provides shipment status updates to shipper

**Key Elements**:
- Shipment reference and pro number
- Status code and date/time
- Current location (city, state, zip)
- Reason code for exceptions
- Equipment and seal numbers
- Next scheduled status

**Sample Structure**:
```
ST*214*0001~
B10*PRO987654*1234567890*PP~
L11*BOL123456*BM~
AT7*AG*NS*20251119*1430*ET~
MS1*CHICAGO*IL*US~
AT7*D1*NS*20251120*0900*ET~
MS1*DALLAS*TX*US~
SE*10*0001~
```

**Common Status Codes**:
- `AG` - Shipment picked up
- `I1` - In transit
- `D1` - Delivered
- `X1` - Delivery exception
- `X3` - Equipment failure
- `CD` - Carrier departure from pick-up
- `AR` - Arrival at delivery location

#### EDI 210 - Motor Carrier Freight Details and Invoice

**Purpose**: Carrier sends freight invoice to shipper for payment

**Key Elements**:
- Invoice number and date
- Pro number and BOL reference
- Origin and destination
- Weight and rate per CWT
- Line haul charges
- Accessorial charges (fuel surcharge, detention, etc.)
- Total amount due
- Payment terms

**Sample Structure**:
```
ST*210*0001~
B3*1234567890*INV987654*PP*20251119~
N9*BM*BOL123456~
N9*PRO*PRO987654~
G62*86*20251119~
L0*1*4800*L*3500*N~
L1*1*800*FR*450.00~
L1*2*0*FSC*75.00~
L1*3*2*DET*100.00~
L3*4800*L*3500*625.00~
SE*15*0001~
```

**Common Charge Codes**:
- `FR` - Freight charges
- `FSC` - Fuel surcharge
- `DET` - Detention
- `LFT` - Liftgate service
- `APT` - Appointment fee
- `RSI` - Residential delivery
- `IND` - Inside delivery

#### EDI 211 - Motor Carrier Bill of Lading

**Purpose**: Electronic bill of lading document

**Key Elements**:
- Shipper and consignee information
- Complete commodity descriptions
- Freight class and NMFC codes
- Hazmat information (if applicable)
- Special handling instructions
- Value and insurance information

#### EDI 110 - Air Freight Details and Invoice

**Purpose**: Air freight billing and shipment details

**Key Elements**:
- Air waybill number
- Origin and destination airports
- Commodity information
- Weight and volume
- Service level and routing
- Charges and fees

## EDIFACT Standards (International)

EDIFACT (Electronic Data Interchange for Administration, Commerce and Transport) is the international EDI standard developed by the UN.

### Key Transportation Messages

#### IFTMIN - Instruction Message

**Purpose**: Booking and transport order instructions

**Equivalent**: Similar to ANSI X12 204

**Key Segments**:
- `BGM` - Beginning of message
- `DTM` - Date/time/period
- `LOC` - Place/location identification
- `GDS` - Nature of cargo
- `EQD` - Equipment details

#### IFTSTA - Status Report Message

**Purpose**: Transport status information

**Equivalent**: Similar to ANSI X12 214

**Key Segments**:
- `BGM` - Beginning of message
- `STS` - Status
- `CNI` - Consignment information
- `LOC` - Location information
- `DTM` - Event date/time

#### IFTMBC - Booking Confirmation

**Purpose**: Carrier confirms transport booking

**Equivalent**: Similar to ANSI X12 990

## EDI Implementation Architecture

### EDI Translation Process

```
Internal Format (TMS) → EDI Translator → ANSI X12/EDIFACT → VAN/AS2 → Partner
```

### Translation Components

1. **Mapping**:
   - Field-level mapping between TMS and EDI
   - Data transformation rules
   - Code value conversion

2. **Validation**:
   - Syntax validation (segment structure)
   - Semantic validation (business rules)
   - Partner-specific validation

3. **Envelope Management**:
   - ISA/IEA (Interchange Control)
   - GS/GE (Functional Group)
   - ST/SE (Transaction Set)

### Sample EDI Envelope Structure

```
ISA*00*          *00*          *ZZ*SHIPPER123     *ZZ*CARRIER456     *251119*1430*U*00401*000000001*0*P*>~
GS*QM*SHIPPER123*CARRIER456*20251119*1430*1*X*004010~
ST*204*0001~
[Transaction Set Data]
SE*15*0001~
GE*1*1~
IEA*1*000000001~
```

### Envelope Segments

**ISA (Interchange Control Header)**:
- Authorization information
- Security information
- Sender/receiver identifiers
- Interchange date and time
- Standards identifier
- Acknowledgment requested

**GS (Functional Group Header)**:
- Functional identifier code
- Application sender/receiver code
- Date and time
- Group control number

**ST (Transaction Set Header)**:
- Transaction set identifier code
- Transaction set control number

## EDI Communication Methods

### Value-Added Networks (VAN)

**Description**: Third-party networks that facilitate EDI exchange

**Major Providers**:
- SPS Commerce
- TrueCommerce
- DiCentral
- B2BGateway

**Advantages**:
- Mailbox service for asynchronous exchange
- Protocol translation
- One connection to many partners
- Audit trail and archiving

**Disadvantages**:
- Monthly and per-transaction fees
- Potential latency
- Additional point of failure

### AS2 (Applicability Statement 2)

**Description**: Point-to-point EDI transmission over Internet

**Features**:
- Secure transmission via HTTPS
- Message encryption and digital signatures
- Message Disposition Notification (MDN) for confirmation
- Lower cost than VAN

**Implementation**:
```
[TMS] → AS2 Client → HTTPS → AS2 Server → [Carrier System]
         ↓                                      ↓
    [MDN Receipt] ← HTTPS ← [MDN Response]
```

### SFTP/FTPS

**Description**: File-based EDI exchange using secure FTP

**Common Pattern**:
1. Generate EDI files in TMS
2. Upload to partner's SFTP server
3. Poll for inbound EDI files
4. Download and process

**Directory Structure**:
```
/outbound/
  /204_load_tenders/
  /210_invoices/
/inbound/
  /990_responses/
  /214_status/
/archive/
```

### API-Based Integration (Modern Alternative)

**Description**: RESTful APIs replacing traditional EDI

**Advantages**:
- Real-time synchronous communication
- JSON/XML instead of X12
- Easier to implement and debug
- Lower latency

**Example**: JSON equivalent of EDI 204
```json
{
  "loadTender": {
    "shipmentId": "SHIPMENT123",
    "referenceNumbers": {
      "bol": "BOL123456"
    },
    "origin": {
      "city": "Chicago",
      "state": "IL",
      "zip": "60601",
      "appointmentStart": "2025-11-19T08:00:00Z",
      "appointmentEnd": "2025-11-19T12:00:00Z"
    },
    "destination": {
      "city": "Dallas",
      "state": "TX",
      "zip": "75201",
      "appointmentStart": "2025-11-20T08:00:00Z",
      "appointmentEnd": "2025-11-20T17:00:00Z"
    },
    "equipment": {
      "type": "van53",
      "quantity": 1
    },
    "weight": {
      "value": 4800,
      "unit": "lbs"
    },
    "cube": {
      "value": 3500,
      "unit": "cubic_feet"
    }
  }
}
```

## EDI Processing Best Practices

### 1. Error Handling

**Validation Errors**:
- Log all EDI parsing errors with full context
- Send TA1 (Interchange Acknowledgment) for ISA-level errors
- Send 997 (Functional Acknowledgment) for transaction-level errors

**Business Rule Violations**:
- Reject invalid shipment data (missing required fields)
- Flag warnings for questionable data
- Maintain audit trail of all rejections

### 2. Performance Optimization

**Batch Processing**:
- Group multiple transactions in single GS envelope
- Process EDI files in batches during off-peak hours
- Use parallel processing for large volumes

**Asynchronous Processing**:
- Queue inbound EDI for background processing
- Don't block real-time transactions
- Implement retry logic for failures

### 3. Partner Management

**Partner Profiles**:
- Store partner-specific EDI requirements
- Maintain sender/receiver ID mappings
- Document custom validation rules

**Testing**:
- Test with sample EDI before go-live
- Maintain test and production partner profiles
- Perform regression testing after changes

### 4. Monitoring & Alerting

**Key Metrics**:
- EDI processing throughput
- Error rate by transaction type
- Average processing latency
- Partner-specific success rates

**Alerts**:
- Failed EDI transmissions
- High error rates
- Missing expected EDI (e.g., no 214 updates)
- VAN/AS2 connectivity issues

## EDI vs API Comparison

| Aspect | EDI (X12/EDIFACT) | Modern API (REST/JSON) |
|--------|-------------------|------------------------|
| **Format** | Fixed-position, delimited | JSON, XML |
| **Learning Curve** | Steep | Moderate |
| **Implementation** | Complex, requires translation | Straightforward |
| **Real-time** | Typically batch/async | Synchronous, real-time |
| **Industry Adoption** | Universal (legacy) | Growing (modern) |
| **Cost** | Higher (VAN fees) | Lower (direct integration) |
| **Debugging** | Difficult | Easy |
| **Standards** | Rigid, versioned | Flexible, evolving |

## Hybrid Approach

Many modern TMS implementations support both:

1. **EDI** for established carrier partners with legacy systems
2. **APIs** for newer carriers and technology-forward partners
3. **Abstraction layer** in TMS to handle both protocols uniformly

```
TMS Core
    ↓
[Integration Layer]
    ↓
    ├── EDI Translation → VAN/AS2 → Legacy Carriers
    └── API Gateway → REST/JSON → Modern Carriers
```

## Compliance & Standards Bodies

### Organizations

**ASC X12**: Develops North American EDI standards
- Website: x12.org
- Membership-based
- Regular updates to transaction sets

**UN/CEFACT**: Develops EDIFACT standards
- Website: unece.org/cefact
- International focus
- Harmonization with other standards

**GS1**: Product and logistics standards
- GTIN (Global Trade Item Number)
- GLN (Global Location Number)
- SSCC (Serial Shipping Container Code)

### Versioning

**X12 Versions**:
- 4010 (legacy, still widely used)
- 5010 (current standard)
- 6020 (latest, limited adoption)

**Backward Compatibility**:
- Always specify version in ISA segment
- Maintain support for multiple versions
- Plan migration timeline for version upgrades

## Resources

### EDI Validators
- **EDI Notepad**: Free EDI viewer and validator
- **X12 Parser**: Online X12 transaction parser
- **Stedi**: Modern EDI platform with validation

### Documentation
- **X12.org**: Official X12 standards documentation (requires membership)
- **EDI Academy**: Free EDI learning resources
- **EDIFICE**: EDI guides and implementation examples

### Translation Software
- **Gentran**: IBM Sterling Gentran Integration Suite
- **BizTalk**: Microsoft BizTalk Server
- **Mulesoft**: Anypoint Platform with EDI module
- **TrueCommerce**: Cloud-based EDI platform
- **SPS Commerce**: Full-service EDI provider

## Future Trends

### Blockchain EDI
- Immutable audit trail of EDI transactions
- Smart contracts for automated acceptance/rejection
- Shared ledger between trading partners

### AI-Enhanced EDI
- Automatic error correction
- Predictive filling of missing data
- Anomaly detection for fraudulent transactions

### API-First Architecture
- Gradual replacement of EDI with APIs
- EDI-to-API transformation gateways
- Unified integration platform supporting both

---

**Document Version**: 1.0
**Last Updated**: 2025-11-19
**Standard References**: ANSI ASC X12, UN/EDIFACT
