# Healthcare Interface Engine Patterns

**Production-grade patterns for Mirth, Rhapsody, Ensemble, and healthcare integration platforms**

---

## Executive Summary

Healthcare interface engines are critical infrastructure components that facilitate real-time bidirectional communication between clinical systems. This guide covers proven architectural patterns, configuration practices, and operational procedures for the three dominant enterprise healthcare integration platforms: Mirth Connect (open-source), Rhapsody (Welltok/KPMG), and Ensemble (InterSystems).

## Platform Comparison Matrix

| Aspect | Mirth Connect | Rhapsody | Ensemble |
|--------|---------------|----------|----------|
| **Licensing** | Open-source (LGPL) | Commercial | Commercial |
| **Primary Language** | JavaScript | Proprietary | ObjectScript/MUMPS |
| **Cloud-Native** | Growing support | Strong | Strong |
| **HL7 v2 Support** | Excellent | Excellent | Excellent |
| **FHIR Support** | Moderate | Strong | Strong |
| **Deployment** | Standalone server | Cloud/On-prem | Cloud/On-prem |
| **Learning Curve** | Moderate | Steep | Moderate |
| **Enterprise Scale** | 300+ hospitals | 500+ hospitals | 1000+ hospitals |

---

## Mirth Connect Architecture

### 1. Core Concepts

#### Channel Architecture
```
Data Flow: Source System → Connector (In) →
           Preprocessor → Router → Transformer →
           Connector (Out) → Target System

Channel Types:
├── Source Channel: Receives inbound messages
│   ├── TCP Listener (port-based input)
│   ├── HTTP Listener (REST/SOAP)
│   ├── File poller (directory watching)
│   └── Database query (scheduled reads)
│
├── Processing Channel: Enriches/transforms data
│   ├── Transformer: Maps data structures
│   ├── Router: Routes to destinations based on rules
│   └── Filters: Controls message flow
│
└── Destination Channel: Sends outbound messages
    ├── TCP Sender (point-to-point)
    ├── HTTP Sender (REST/SOAP)
    ├── File writer (batch output)
    └── Database writer (direct insert)
```

#### Message Flow
```javascript
// Message structure in Mirth (JavaScript context)
var msg = {
    raw: $('raw'),                    // Original message
    msh: $('msh'),                    // HL7 MSH segment
    pid: $('pid'),                    // HL7 PID segment
    metadata: {
        id: $('id'),                  // Message ID
        type: $('type'),              // HL7 message type
        version: $('version'),        // HL7 version
        timestamp: new Date(),        // Processing time
        source: $sourceConnector      // Source identifier
    }
};

// Router: Determine destination based on message
if (msg.msh['9']['1'] == 'ADT') {
    // Patient admission/discharge/transfer message
    router.routeMessage('ADT_PROCESSOR', msg);
} else if (msg.msh['9']['1'] == 'ORU') {
    // Observation result message (lab results)
    router.routeMessage('LAB_PROCESSOR', msg);
}
```

### 2. Typical Implementation Pattern: ADT Integration

#### Scenario: Hospital A → EHR Integration

**Requirement**: Route patient admission/discharge/transfer (ADT) messages from hospital system to EHR

```mirth
// Channel: HOSPITAL_ADT_TO_EHR

// 1. SOURCE CONNECTOR: TCP Listener
Port: 2575
Protocol: HL7 v2.5
Encoding: ASCII
ACK: MSA.1 = AA (Application Accept)

// 2. PREPROCESSOR
// Validate message structure
if (!msg.msh) {
    channelMap.put('error', 'Invalid HL7 message - missing MSH segment');
    var timestamp = java.time.LocalDateTime.now();
    logger.error('ADT validation failed at ' + timestamp);
}

// 3. TRANSFORMER
// Convert hospital-specific patient ID to EHR MRN
var patientId = msg.pid['3']['1'];
var facilityCode = msg.msh['3']['1'];

// Query database for patient mapping
var query = "SELECT ehr_mrn FROM patient_mapping WHERE facility_code='" +
            facilityCode + "' AND legacy_patient_id='" + patientId + "'";
var result = dbLookup('production', query);
var ehrMrn = result.get(0)['ehr_mrn'];

// Rebuild message with EHR MRN
msg.pid['3']['1'] = ehrMrn;

// Extract encounter details
var admitDate = msg.pid['5'];
var patientName = msg.pid['5']['1']['1'] + ', ' + msg.pid['5']['2'];
var sex = msg.pid['8'];
var dob = msg.pid['7'];

// 4. ROUTER
// Route based on message event type
var messageEvent = msg.msh['9']['2'];

switch(messageEvent) {
    case 'A01':  // Admission
        router.routeMessage('EHR_ADMIT', msg);
        break;
    case 'A03':  // Discharge
        router.routeMessage('EHR_DISCHARGE', msg);
        break;
    case 'A04':  // Registration
        router.routeMessage('EHR_REGISTER', msg);
        break;
    case 'A05':  // Pre-admission
        router.routeMessage('EHR_PREADMIT', msg);
        break;
    case 'A06':  // Transfer
        router.routeMessage('EHR_TRANSFER', msg);
        break;
    default:
        router.routeMessage('EHR_DEFAULT', msg);
}

// 5. DESTINATION CONNECTOR: HTTP Sender
URL: https://ehr.hospital.local/api/adt/process
Method: POST
Content-Type: application/json
Authentication: Bearer ${token}

// Convert HL7 to JSON for EHR
{
    "messageType": "ADT",
    "eventType": messageEvent,
    "patient": {
        "mrn": ehrMrn,
        "firstName": msg.pid['5']['2'],
        "lastName": msg.pid['5']['1']['1'],
        "dateOfBirth": msg.pid['7'],
        "sex": msg.pid['8']
    },
    "encounter": {
        "admitDate": msg.pid['5'],
        "facility": msg.msh['3']['1'],
        "department": msg.pid['6'],
        "bed": msg.pid['3']['2']
    }
}
```

#### Error Handling Pattern

```javascript
// Global error handling in Mirth
try {
    // Main message processing
    processingLogic();

} catch (e) {
    // Capture error details
    var errorRecord = {
        messageId: msg.msh['10'],
        sourceSystem: msg.msh['3']['1'],
        destinationSystem: msg.msh['5']['1'],
        errorCode: e.code || 'UNKNOWN',
        errorMessage: e.message,
        errorStack: e.stack,
        timestamp: new Date(),
        messageContent: msg.raw.substring(0, 500)  // First 500 chars
    };

    // Log to error table
    dbExecute('production',
        "INSERT INTO message_errors (message_id, error_code, error_message, timestamp) " +
        "VALUES (?, ?, ?, ?)",
        [errorRecord.messageId, errorRecord.errorCode, errorRecord.errorMessage, errorRecord.timestamp]);

    // Send alert if critical
    if (e.severity === 'CRITICAL') {
        sendAlert({
            recipient: 'integration-support@hospital.local',
            subject: 'CRITICAL: ADT Processing Failed - ' + msg.msh['10'],
            body: 'Message ID: ' + errorRecord.messageId + '\n' +
                  'Error: ' + errorRecord.errorMessage
        });
    }

    // Route to dead letter queue
    router.routeMessage('ERROR_PROCESSOR', {
        originalMessage: msg,
        error: errorRecord
    });
}
```

---

## Rhapsody Architecture

### 1. Core Concepts

#### Intelligent Mapper Framework

Rhapsody's strength is its visual IDE and sophisticated data mapping engine.

```
Data Flow:
Source → Parser (protocol conversion) →
Mapper (data transformation) →
Filter (conditional routing) →
Generator (output format) → Destination

Key Components:
├── Parser: Converts input format to internal representation
│   ├── HL7 parser (v2.x, v3.x)
│   ├── EDI parser
│   ├── X12 parser
│   ├── XML parser
│   └── Custom parsers
│
├── Mapper: Intelligent data mapping with lookups
│   ├── Field-to-field mapping
│   ├── Database lookups
│   ├── Business logic transformations
│   ├── Conditional routing
│   └── Aggregation/splitting
│
└── Generator: Constructs output message
    ├── HL7 generator
    ├── JSON generator
    ├── XML generator
    └── Custom output formats
```

### 2. Rhapsody Lookup Pattern

#### Use Case: Provider Matching Across Institutions

```
Challenge: Hospital A identifies physicians by
         internal provider ID (e.g., "45802")
         EHR requires NPI (National Provider Identifier)

Solution: Use Rhapsody lookup table to map
         Hospital A Provider ID → NPI
```

**Configuration**:
```xml
<!-- Rhapsody Lookup Definition -->
<lookupTable>
    <name>ProviderIDLookup</name>
    <source>
        <connection>PostgreSQL_Production</connection>
        <query>
            SELECT provider_id, npi, full_name
            FROM provider_mapping
            WHERE facility_code = ?
        </query>
    </source>

    <cache>
        <enabled>true</enabled>
        <ttl>3600</ttl>  <!-- Refresh hourly -->
    </cache>
</lookupTable>

<!-- Usage in Mapper -->
<mapping>
    <from>
        <path>OBR/OBR.16/OBR.16.1</path>  <!-- Ordering provider -->
    </from>

    <to>
        <path>OBR_OUT/OBR.16/OBR.16.1</path>
    </to>

    <transformation>
        <lookup>
            <table>ProviderIDLookup</table>
            <input>${from}</input>
            <output>npi</output>
            <default>UNKNOWN_PROVIDER</default>
        </lookup>
    </transformation>
</mapping>
```

### 3. Multi-Instance Routing Pattern

#### Rhapsody Route Groups

```
Scenario: Single lab message generates
         multiple output messages

Lab System sends ORU (Observation Result)
with multiple lab tests → Route to:
├── EHR (clinical viewing)
├── LIS (historical lab data)
├── Data warehouse (analytics)
└── Patient portal (patient access)

Rhapsody Configuration:
```

```javascript
// Filter condition: Split ORU by test type
var testType = input.OBX[0]['OBX.3']['1'];  // LOINC code
var result = input.OBX[0]['OBX.5'];         // Result value
var units = input.OBX[0]['OBX.6'];          // Units

if (testType.startsWith('2345-')) {
    // Chemistry tests → EHR + Data warehouse
    routeToDestination('EHR_LABS', output);
    routeToDestination('WAREHOUSE', output);
} else if (testType.startsWith('2797-')) {
    // Hematology → All three
    routeToDestination('EHR_LABS', output);
    routeToDestination('LIS', output);
    routeToDestination('WAREHOUSE', output);
}
```

---

## Ensemble (InterSystems) Architecture

### 1. Core Concepts

#### Production Architecture

Ensemble uses a "production" paradigm where all components are defined in configuration classes.

```
Production Structure:

Production
├── BusinessService (inbound)
│   ├── TCPService: Listen on port
│   ├── HTTPService: REST/SOAP endpoint
│   ├── FileService: Directory monitoring
│   └── DBService: Query scheduling
│
├── BusinessRule (conditional logic)
│   └── Dynamic routing based on message content
│
├── BusinessProcess (orchestration)
│   ├── Complex workflows
│   ├── Stateful operations
│   ├── Synchronous correlation
│   └── Error handling
│
└── BusinessOperation (outbound)
    ├── TCPOperation: Send TCP
    ├── HTTPOperation: REST/SOAP
    ├── FileOperation: Write file
    └── DBOperation: Execute query
```

#### ObjectScript Message Processing

```objectscript
// Ensemble uses ObjectScript (MUMPS derivative)
// Production processing example:

Class Hospital.ADT.Process Extends Ens.BusinessProcess
{
    Method OnRequest(pRequest As EnsLib.HL7.Message, pResponse As Ens.Response) As %Status
    {
        Set tStatus = $$$OK

        Try {
            // Extract HL7 segments
            Set messageType = pRequest.GetValueAt("1:MSH:9.1")
            Set eventType = pRequest.GetValueAt("1:MSH:9.2")
            Set facilityCode = pRequest.GetValueAt("1:MSH:3.1")
            Set patientId = pRequest.GetValueAt("1:PID:3.1")
            Set mrn = pRequest.GetValueAt("1:PID:3.5")

            // Query for patient mapping
            Set query = "SELECT ehr_mrn FROM patient_mapping "
                      _ "WHERE facility_code = ? AND legacy_patient_id = ?"
            Set statement = ##class(%SQL.Statement).%New()
            Set tStatus = statement.%Prepare(query)
            If tStatus {
                Set resultSet = statement.%Execute(facilityCode, patientId)
                If resultSet.%Next() {
                    Set ehrMrn = resultSet.%Get("ehr_mrn")
                }
            }

            // Route based on event type
            Do ##switch(eventType)
                Case "A01": Do ..RouteAdmit(pRequest, ehrMrn)
                Case "A03": Do ..RouteDischarge(pRequest, ehrMrn)
                Case "A04": Do ..RouteRegister(pRequest, ehrMrn)
                Default: Do ..RouteDefault(pRequest)
            }

        } Catch ex {
            Set tStatus = ex.AsStatus()
            Do ..HandleError(pRequest, ex)
        }

        Return tStatus
    }

    Method RouteAdmit(pRequest As EnsLib.HL7.Message, ehrMrn As %String) As %Status
    {
        // Create new admission message
        Set requestMsg = ##class(Ens.Request).%New()
        Set requestMsg.MessageBody = pRequest

        // Send to EHR admission handler
        Return ..SendRequestSync("EHR.AdmissionHandler", requestMsg)
    }
}
```

### 2. Error Handling in Ensemble

```objectscript
Class Hospital.ErrorHandler Extends Ens.BusinessProcess
{
    Method OnError(pErrorObject As Ens.ErrorResponse) As %Status
    {
        Set tStatus = $$$OK

        // Log error with full context
        Set errorRecord = ##class(Hospital.MessageError).%New()
        Set errorRecord.MessageID = pErrorObject.MessageId
        Set errorRecord.ErrorCode = pErrorObject.ErrorCode
        Set errorRecord.ErrorMessage = pErrorObject.ErrorMessage
        Set errorRecord.SourceSystem = pErrorObject.SourceSystem
        Set errorRecord.TargetSystem = pErrorObject.TargetSystem
        Set errorRecord.Timestamp = $Now()

        // Attempt retry with exponential backoff
        Set retryCount = pErrorObject.RetryCount
        If retryCount < 3 {
            Set retryDelay = 60 * (2 ^ retryCount)  // 60s, 120s, 240s
            Set status = ..SendRequest(pErrorObject.OriginalRequest, retryDelay)
        } Else {
            // Move to dead letter queue
            Set errorRecord.Status = "DEAD_LETTER"
            Do ..RouteToManualReview(pErrorObject)
        }

        Do errorRecord.%Save()
        Return tStatus
    }
}
```

---

## Common Integration Patterns

### 1. Bidirectional Patient Synchronization

#### Use Case: Keeping multiple systems synchronized

```javascript
// Pattern: Master patient data in one system,
//          distributed to others

Trigger Points:
├── Patient demographics update in EHR
├── Insurance information change
├── Emergency contact update
└── Consent/preference change

Mirth Implementation:

// 1. Listen for change notification
Source: EHR Web Hook
Event: Patient.Updated
Payload: {patientMRN, changedFields, timestamp}

// 2. Query for full patient data
var query = "SELECT * FROM patient WHERE mrn = '" + patientMRN + "'";
var patientData = dbLookup('production', query);

// 3. Distribute to downstream systems
// → Hospital Information System (HIS)
// → Pharmacy Information System (PIS)
// → Lab Information System (LIS)
// → Billing system

router.routeMessage('HIS_UPDATE', {
    patient: patientData,
    changeType: changedFields
});
```

### 2. Lab Result Aggregation Pattern

#### Scenario: Multiple lab systems → Single EHR

```javascript
// Challenge: Four different lab systems submit results
//           Consolidate into single observation

// Mirth channels:
├── LAB_SYSTEM_1_RECEIVER (parser for Lab1 format)
├── LAB_SYSTEM_2_RECEIVER (parser for Lab2 format)
├── LAB_SYSTEM_3_RECEIVER (parser for Lab3 format)
└── LAB_RESULT_AGGREGATOR (merge and normalize)

// Each receiver maps to standard ORU format:

// LAB_SYSTEM_1_RECEIVER transformer:
var standardORU = {
    type: 'ORU^R01',
    labCode: 'LAB001',
    timestamp: msg.analysisTime,
    patientId: msg.patientNumber,
    tests: []
};

// Map Lab1-specific test codes to LOINC
var testMapping = {
    'WBC': '6690-2',      // WBC [#/volume] in Blood
    'HGB': '718-7',       // Hemoglobin
    'HCT': '4544-3',      // Hematocrit
    'GLUCOSE': '2345-7'   // Glucose
};

for (var testCode in msg.results) {
    var loincCode = testMapping[testCode];
    standardORU.tests.push({
        loincCode: loincCode,
        value: msg.results[testCode].value,
        units: msg.results[testCode].units
    });
}

router.routeMessage('LAB_AGGREGATOR', standardORU);
```

### 3. Scheduled Bulk Data Export Pattern

#### Use Case: Daily lab result batch export

```javascript
// Mirth Channel: DAILY_LAB_EXPORT

// Trigger: Scheduled at 02:00 UTC daily

// 1. Query source system for new results
var yesterday = new Date();
yesterday.setDate(yesterday.getDate() - 1);
var fromDate = dateFormat(yesterday, 'yyyy-MM-dd');

var query = "SELECT * FROM lab_results WHERE " +
            "result_date >= '" + fromDate + "' AND " +
            "export_status = 'PENDING'";

var results = dbLookup('legacy_lab', query);
logger.info('Found ' + results.size() + ' lab results for export');

// 2. Batch into reasonable-sized chunks
var batchSize = 1000;
for (var i = 0; i < results.size(); i += batchSize) {
    var endIdx = Math.min(i + batchSize, results.size());
    var batch = results.subList(i, endIdx);

    // 3. Create batch message
    var batchMsg = {
        batchNumber: i / batchSize,
        totalBatches: Math.ceil(results.size() / batchSize),
        recordCount: batch.size(),
        records: batch
    };

    // 4. Send to destination
    router.routeMessage('LAB_BATCH_PROCESSOR', batchMsg);
}

// 5. Mark as exported
dbExecute('legacy_lab',
    "UPDATE lab_results SET export_status = 'EXPORTED', " +
    "export_timestamp = NOW() WHERE result_date >= ?",
    [fromDate]);
```

---

## Performance Optimization

### 1. Message Throughput Tuning

#### Database Connection Pooling
```
Mirth: Configure JDBC connection pool
├── Initial pool size: 10
├── Max pool size: 50 (adjust based on load)
├── Connection timeout: 30 seconds
└── Idle timeout: 300 seconds

Rhapsody: Connection manager settings
├── Max connections: 100
├── Queue timeout: 60 seconds

Ensemble: Connection definitions
├── Pool size: 20-50 (based on peak)
└── Timeout: 30 seconds
```

#### Message Queue Optimization
```
Queue Configuration:

Production queues should be sized for peak load:
├── Inbound queue: 10,000+ messages
├── Error queue: 1,000+ messages
├── Retry queue: 5,000+ messages

Monitoring:
├── Track queue depth (alert if > 80% capacity)
├── Monitor message processing time
├── Alert if message age > 1 hour
```

### 2. Caching Strategy

```javascript
// Mirth caching for frequent lookups

// 1. Provider lookup cache (updates hourly)
var providerCache = new java.util.HashMap();

function getProviderNPI(providerID) {
    // Check cache first (5-minute refresh)
    if (providerCache.containsKey(providerID)) {
        var cached = providerCache.get(providerID);
        if (new Date().getTime() - cached.timestamp < 300000) {
            return cached.npi;
        }
    }

    // Query database
    var query = "SELECT npi FROM provider_mapping WHERE provider_id = ?";
    var result = dbLookup('production', query, [providerID]);

    if (result && result.size() > 0) {
        var npi = result.get(0)['npi'];
        providerCache.put(providerID, {
            npi: npi,
            timestamp: new Date().getTime()
        });
        return npi;
    }

    return null;
}
```

---

## Security Best Practices

### 1. Message Encryption

```
In-Transit Encryption:
├── HL7 over TLS 1.2+ (required)
├── SFTP for file transfers (not FTP)
├── VPN for legacy protocols
└── Certificate pinning for critical connections

At-Rest Encryption:
├── Database: AES-256 encryption for PHI tables
├── File storage: Encrypted containers
├── Backup: Encrypted archives (AES-256)
└── Audit logs: Protected from modification
```

### 2. Access Controls

```
Role-Based Access Control (RBAC):

├── ADT_ADMIN: Can view/modify ADT integrations
├── LAB_ADMIN: Can view/modify lab integrations
├── INTEGRATION_VIEWER: Read-only access to logs
├── INTEGRATION_SUPER: Full administrative access (audit all access)
└── SERVICE_ACCOUNT: System-to-system authentication

Audit Requirements:
├── Log all message access
├── Track configuration changes
├── Monitor failed authentications
├── Review weekly access logs
```

---

## Troubleshooting Common Issues

| Issue | Symptoms | Resolution |
|-------|----------|-----------|
| Message Queue Backlog | Messages delayed, queue depth increasing | Check destination system health; increase queue size; review transformer performance |
| Connection Drops | Random message failures, timeout errors | Verify network stability; increase connection timeout; check firewall rules |
| Data Validation Failures | Messages stuck in error queue | Review mapping rules; validate source data quality; check code mapping tables |
| Performance Degradation | Processing time increases over time | Monitor memory usage; restart interface engine weekly; optimize database queries |
| ACK Not Returned | Source system times out waiting | Verify destination is returning HL7 acknowledgments; check network latency |

---

## References

- HL7 Standard: http://www.hl7.org/
- Mirth Connect: https://www.mirthcorp.com/community/wiki
- Rhapsody Integration Engine: https://www.kpmg.com/us/en/insights/rhapsody.html
- InterSystems Ensemble: https://www.intersystems.com/ensemble/
- HIPAA Security Rule: 45 CFR 164.300-320
