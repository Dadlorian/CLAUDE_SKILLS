# OPC UA Integration Guide

## Overview

OPC UA (Unified Architecture) is the industry-standard protocol for industrial interoperability, providing platform-independent communication between industrial equipment, SCADA systems, MES, and cloud platforms. This guide covers best practices for OPC UA implementation in manufacturing environments.

---

## Why OPC UA?

### Advantages Over Legacy Protocols

**vs. OPC Classic (DA/HDA/AE)**
- Platform-independent (not Windows-only)
- Built-in security (encryption, authentication)
- Firewall-friendly (single port, HTTPS tunneling)
- Rich information modeling (not just tags)
- Works across internet and cloud

**vs. Modbus**
- Self-describing data (metadata included)
- Complex data structures supported
- Event-driven notifications (not polling)
- Standardized across vendors
- Better security

**vs. Proprietary Protocols**
- Vendor-neutral standard
- Interoperability guaranteed
- Supported by all major manufacturers
- Future-proof technology
- Lower integration costs

---

## OPC UA Architecture

### Information Model Hierarchy

```
AddressSpace
├── Objects
│   ├── Server (system information)
│   ├── DeviceSet
│   │   └── Device_PLC1
│   │       ├── Configuration
│   │       ├── Diagnostics
│   │       └── FunctionalGroups
│   │           ├── Line1
│   │           │   ├── Station1
│   │           │   │   ├── Robot
│   │           │   │   │   ├── ActualPosition
│   │           │   │   │   ├── ActualSpeed
│   │           │   │   │   ├── Status
│   │           │   │   │   └── Methods
│   │           │   │   │       ├── Home()
│   │           │   │   │       ├── Start()
│   │           │   │   │       └── Stop()
│   │           │   │   └── Conveyor
│   │           │   │       ├── MotorSpeed
│   │           │   │       ├── Running
│   │           │   │       └── Methods
│   │           │   └── Station2
│   │           └── Line2
├── Types
│   ├── ObjectTypes
│   ├── VariableTypes
│   ├── DataTypes
│   └── ReferenceTypes
└── Views
```

### Node Structure

Every OPC UA node contains:
- **NodeId**: Unique identifier (e.g., `ns=2;s=Line1.Robot.Status`)
- **BrowseName**: Human-readable name
- **DisplayName**: Localized display name
- **Description**: Optional description
- **Value**: Current value (for variables)
- **DataType**: Integer, Float, String, Boolean, etc.
- **AccessLevel**: Read, Write, or ReadWrite
- **References**: Relationships to other nodes

---

## Security Implementation

### Security Policies

**None (NOT Recommended)**
```
Use Case: Lab/development only
Risk: No encryption or authentication
Status: NEVER use in production
```

**Basic256Sha256 (Recommended)**
```xml
<SecurityPolicy>
    <PolicyUri>http://opcfoundation.org/UA/SecurityPolicy#Basic256Sha256</PolicyUri>
    <Mode>SignAndEncrypt</Mode>
</SecurityPolicy>

Encryption: AES-256-CBC
Signature: HMAC-SHA2-256
Certificate: X.509 2048-bit RSA minimum
```

**Aes128_Sha256_RsaOaep (Modern Standard)**
```xml
<SecurityPolicy>
    <PolicyUri>http://opcfoundation.org/UA/SecurityPolicy#Aes128_Sha256_RsaOaep</PolicyUri>
    <Mode>SignAndEncrypt</Mode>
</SecurityPolicy>

Encryption: AES-128-CBC
Signature: HMAC-SHA2-256
Certificate: X.509 2048-bit RSA minimum
Key Derivation: RSA-OAEP
```

### Certificate Management

**Certificate Generation**
```bash
# Generate self-signed certificate (development)
openssl req -new -x509 -days 365 \
  -keyout opc_ua_key.pem \
  -out opc_ua_cert.pem \
  -config opcua_openssl.cnf

# Certificate requirements:
- Key length: 2048-bit minimum (4096-bit recommended)
- Valid period: 1-5 years
- Subject Alternative Name: Include server hostname/IP
- Key Usage: digitalSignature, keyEncipherment, dataEncipherment
```

**Production Certificate Management**
```yaml
Certificate Authority:
  Type: Internal CA or Commercial CA
  Renewal: Automated process (e.g., Let's Encrypt style)
  Expiry Monitoring: Alert 90 days before expiration
  Revocation: CRL or OCSP support

Certificate Trust List:
  Location: Per OPC UA specification
  Update: Automated or manual with approval
  Validation: Check expiry, signature, trust chain

Client Certificates:
  Per-Application: Each client has unique certificate
  No Sharing: Never reuse certificates across clients
  Storage: Secure certificate store (encrypted)
```

### User Authentication

**Anonymous (NOT Recommended)**
```csharp
// No authentication - development only
var userIdentity = new UserIdentity();
```

**Username/Password**
```csharp
// Basic authentication
var userIdentity = new UserIdentity("operator1", "SecurePassword123!");

// Server-side validation against:
- Local user database
- LDAP/Active Directory
- External authentication service
```

**Certificate-Based**
```csharp
// Certificate authentication (recommended for M2M)
var userCertificate = new X509Certificate2("client_cert.pfx", "password");
var userIdentity = new UserIdentity(userCertificate);
```

**Kerberos/OAuth (Enterprise)**
```csharp
// Integration with enterprise identity
var kerberos Token = GetKerberosToken();
var userIdentity = new UserIdentity(new IssuedIdentityToken {
    TokenData = kerberosToken
});
```

---

## Connection Configuration

### Endpoint URL Formats

**Secure Channel (Recommended)**
```
opc.tcp://192.168.1.100:4840
opc.tcp://plc-line1.factory.local:4840
opc.tcp://localhost:4840
```

**HTTPS (Firewall/Internet)**
```
https://plc-line1.factory.local:443/opcua
https://cloud-gateway.example.com:8443/opcua
```

### Session Configuration

```csharp
// Create application configuration
var config = new ApplicationConfiguration {
    ApplicationName = "MES_Client",
    ApplicationType = ApplicationType.Client,
    SecurityConfiguration = new SecurityConfiguration {
        ApplicationCertificate = new CertificateIdentifier {
            StoreType = "Directory",
            StorePath = "/opt/opcua/pki/own",
            SubjectName = "CN=MES_Client"
        },
        TrustedPeerCertificates = new CertificateTrustList {
            StoreType = "Directory",
            StorePath = "/opt/opcua/pki/trusted"
        },
        RejectedCertificateStore = new CertificateTrustList {
            StoreType = "Directory",
            StorePath = "/opt/opcua/pki/rejected"
        },
        AutoAcceptUntrustedCertificates = false, // NEVER true in production
    },
    TransportConfigurations = new TransportConfigurationCollection(),
    TransportQuotas = new TransportQuotas {
        OperationTimeout = 120000,      // 2 minutes
        MaxStringLength = 65535,        // 64 KB
        MaxArrayLength = 65535,         // 64K elements
        MaxByteStringLength = 1048576,  // 1 MB
        MaxMessageSize = 4194304,       // 4 MB
        MaxBufferSize = 65535,          // 64 KB
    },
    ClientConfiguration = new ClientConfiguration {
        DefaultSessionTimeout = 60000,  // 1 minute
        MinSubscriptionLifetime = 10000 // 10 seconds
    }
};

// Create session
var endpointUrl = "opc.tcp://plc-line1:4840";
var endpointDescription = CoreClientUtils.SelectEndpoint(endpointUrl, true);
var endpointConfiguration = EndpointConfiguration.Create(config);
var endpoint = new ConfiguredEndpoint(
    null,
    endpointDescription,
    endpointConfiguration
);

var session = await Session.Create(
    config,
    endpoint,
    false,  // updateBeforeConnect
    "MES_Client_Session",
    60000,  // sessionTimeout in ms
    new UserIdentity("opcuser", "SecurePassword!"),
    null    // preferredLocales
);

// Keep-alive handling
session.KeepAlive += (sender, e) => {
    if (ServiceResult.IsBad(e.Status)) {
        Console.WriteLine($"Keep-alive failed: {e.Status}");
        // Implement reconnection logic
    }
};
```

---

## Data Access Patterns

### Reading Data

**Read Single Value**
```csharp
// Read a single variable
var nodeId = new NodeId("ns=2;s=Line1.Robot.ActualPosition");
var value = session.ReadValue(nodeId);

Console.WriteLine($"Position: {value.Value}");
Console.WriteLine($"Timestamp: {value.SourceTimestamp}");
Console.WriteLine($"Quality: {value.StatusCode}");
```

**Read Multiple Values**
```csharp
// Batch read for efficiency
var nodesToRead = new ReadValueIdCollection {
    new ReadValueId { NodeId = new NodeId("ns=2;s=Line1.Robot.ActualPosition") },
    new ReadValueId { NodeId = new NodeId("ns=2;s=Line1.Robot.ActualSpeed") },
    new ReadValueId { NodeId = new NodeId("ns=2;s=Line1.Robot.Status") }
};

session.Read(
    null,  // requestHeader
    0,     // maxAge (0 = read from device)
    TimestampsToReturn.Both,
    nodesToRead,
    out DataValueCollection results,
    out DiagnosticInfoCollection diagnosticInfos
);

foreach (var result in results) {
    Console.WriteLine($"Value: {result.Value}, Quality: {result.StatusCode}");
}
```

**Read with Metadata**
```csharp
// Read value with full metadata
var nodeId = new NodeId("ns=2;s=Line1.Robot.Temperature");

// Read value
var value = session.ReadValue(nodeId);

// Read display name
var displayName = session.ReadDisplayName(nodeId);

// Read data type
var dataType = session.ReadDataType(nodeId);

// Read engineering units (if available)
var browse = session.Browse(
    null,
    null,
    nodeId,
    0,
    BrowseDirection.Forward,
    ReferenceTypeIds.HasProperty,
    true,
    0
);

foreach (var reference in browse.References) {
    if (reference.BrowseName.Name == "EngineeringUnits") {
        var euRange = session.ReadValue(ExpandedNodeId.ToNodeId(reference.NodeId, session.NamespaceUris));
        Console.WriteLine($"Units: {euRange.Value}");
    }
}
```

### Writing Data

**Write Single Value**
```csharp
// Write a setpoint
var nodeId = new NodeId("ns=2;s=Line1.Conveyor.SpeedSetpoint");
var valueToWrite = new WriteValue {
    NodeId = nodeId,
    AttributeId = Attributes.Value,
    Value = new DataValue(new Variant(75.5))  // 75.5% speed
};

var writeResults = session.Write(
    null,
    new WriteValueCollection { valueToWrite },
    out StatusCodeCollection results,
    out DiagnosticInfoCollection diagnosticInfos
);

if (StatusCode.IsGood(results[0])) {
    Console.WriteLine("Write successful");
} else {
    Console.WriteLine($"Write failed: {results[0]}");
}
```

**Write with Validation**
```csharp
// Read constraints before writing
var nodeId = new NodeId("ns=2;s=Line1.Temperature.Setpoint");

// Check access level
var accessLevel = (byte)session.ReadValue(new NodeId(nodeId.ToString() + ".AccessLevel")).Value;
if ((accessLevel & 0x02) == 0) {
    throw new Exception("Node is not writable");
}

// Read value range
var euRange = session.ReadValue(new NodeId(nodeId.ToString() + ".EURange"));
var range = (Range)euRange.Value;

double setpoint = 85.5;
if (setpoint < range.Low || setpoint > range.High) {
    throw new ArgumentOutOfRangeException(
        $"Setpoint {setpoint} out of range [{range.Low}, {range.High}]"
    );
}

// Write validated value
var writeValue = new WriteValue {
    NodeId = nodeId,
    AttributeId = Attributes.Value,
    Value = new DataValue(new Variant(setpoint))
};
session.Write(null, new WriteValueCollection { writeValue }, out var results, out var diagnostics);
```

### Subscriptions (Event-Driven)

**Create Monitored Items**
```csharp
// Create subscription for data change notifications
var subscription = new Subscription(session.DefaultSubscription) {
    PublishingInterval = 1000,  // 1 second
    KeepAliveCount = 10,
    LifetimeCount = 100,
    MaxNotificationsPerPublish = 1000,
    PublishingEnabled = true,
    Priority = 100
};

// Add monitored items
var monitoredItem1 = new MonitoredItem(subscription.DefaultItem) {
    DisplayName = "Robot Position",
    StartNodeId = "ns=2;s=Line1.Robot.ActualPosition",
    AttributeId = Attributes.Value,
    SamplingInterval = 100,  // 100ms
    QueueSize = 10,
    DiscardOldest = true
};

// Data change notification handler
monitoredItem1.Notification += (item, e) => {
    var notification = (MonitoredItemNotification)e.NotificationValue;
    Console.WriteLine($"{item.DisplayName}: {notification.Value.Value} @ {notification.Value.SourceTimestamp}");
};

subscription.AddItem(monitoredItem1);

// Add more monitored items...
var monitoredItem2 = new MonitoredItem(subscription.DefaultItem) {
    DisplayName = "Conveyor Speed",
    StartNodeId = "ns=2;s=Line1.Conveyor.ActualSpeed",
    SamplingInterval = 500,  // 500ms
    QueueSize = 5
};
monitoredItem2.Notification += (item, e) => {
    var notification = (MonitoredItemNotification)e.NotificationValue;
    // Process conveyor speed change
    ProcessSpeedChange(notification.Value);
};

subscription.AddItem(monitoredItem2);

// Activate subscription
session.AddSubscription(subscription);
subscription.Create();

// Keep subscription alive
subscription.PublishStatusChanged += (s, e) => {
    if (ServiceResult.IsBad(e.Status)) {
        Console.WriteLine($"Subscription publish failed: {e.Status}");
    }
};
```

**Deadband Filtering**
```csharp
// Only notify on significant changes (reduce network traffic)
var monitoredItem = new MonitoredItem {
    DisplayName = "Tank Level",
    StartNodeId = "ns=2;s=Process.Tank1.Level",
    SamplingInterval = 1000,  // Check every second
    QueueSize = 1,
    Filter = new DataChangeFilter {
        Trigger = DataChangeTrigger.StatusValue,  // Value or status change
        DeadbandType = (uint)DeadbandType.Absolute,
        DeadbandValue = 2.0  // Only notify if change > 2 units
    }
};
```

---

## Method Calls

### Invoking Server Methods

```csharp
// Call method to start production
var objectId = new NodeId("ns=2;s=Line1.Station1");
var methodId = new NodeId("ns=2;s=Line1.Station1.StartProduction");

// Input arguments
var inputArguments = new VariantCollection {
    new Variant("Product_ABC"),  // Product code
    new Variant((uint)100),      // Quantity
    new Variant(true)            // Quality check enabled
};

// Call method
var outputs = session.Call(
    objectId,
    methodId,
    inputArguments
);

// Process outputs
if (outputs.Count > 0) {
    var jobId = (string)outputs[0].Value;
    Console.WriteLine($"Production started. Job ID: {jobId}");
}
```

### Error Handling

```csharp
try {
    var outputs = session.Call(objectId, methodId, inputArguments);
    // Process results
} catch (ServiceResultException ex) {
    switch (ex.StatusCode) {
        case StatusCodes.BadInvalidArgument:
            Console.WriteLine("Invalid input arguments");
            break;
        case StatusCodes.BadUserAccessDenied:
            Console.WriteLine("Access denied - check user permissions");
            break;
        case StatusCodes.BadMethodInvalid:
            Console.WriteLine("Method not found or not executable");
            break;
        default:
            Console.WriteLine($"Method call failed: {ex.Message}");
            break;
    }
}
```

---

## Historical Data Access (HDA)

### Read Historical Values

```csharp
// Read last 24 hours of temperature data
var nodeId = new NodeId("ns=2;s=Process.Tank1.Temperature");
var startTime = DateTime.UtcNow.AddHours(-24);
var endTime = DateTime.UtcNow;

var historyReadDetails = new ReadRawModifiedDetails {
    IsReadModified = false,
    StartTime = startTime,
    EndTime = endTime,
    NumValuesPerNode = 0,  // 0 = all values
    ReturnBounds = false
};

session.HistoryRead(
    null,
    new ExtensionObject(historyReadDetails),
    TimestampsToReturn.Both,
    false,
    new HistoryReadValueIdCollection {
        new HistoryReadValueId {
            NodeId = nodeId
        }
    },
    out HistoryReadResultCollection results,
    out DiagnosticInfoCollection diagnosticInfos
);

if (StatusCode.IsGood(results[0].StatusCode)) {
    var data = (HistoryData)ExtensionObject.ToEncodeable(results[0].HistoryData);
    foreach (var value in data.DataValues) {
        Console.WriteLine($"{value.SourceTimestamp}: {value.Value}");
    }
}
```

### Aggregated Historical Data

```csharp
// Get hourly averages
var aggregateId = ObjectIds.AggregateFunction_Average;
var processingInterval = 3600000;  // 1 hour in milliseconds

var aggregateDetails = new ReadProcessedDetails {
    StartTime = startTime,
    EndTime = endTime,
    ProcessingInterval = processingInterval,
    AggregateType = new NodeIdCollection { aggregateId }
};

// Execute historical read with aggregation
// Similar to raw historical read but with aggregateDetails
```

---

## Information Modeling Best Practices

### Custom Type Definitions

```xml
<!-- Define custom object type for robot -->
<UAObjectType NodeId="ns=2;i=1001" BrowseName="2:RobotType">
    <DisplayName>Robot</DisplayName>
    <Description>Industrial robot with standard properties</Description>
    <References>
        <Reference ReferenceType="HasSubtype" IsForward="false">i=58</Reference>
        <Reference ReferenceType="HasComponent">
            <TargetId>ns=2;i=1002</TargetId>  <!-- ActualPosition -->
        </Reference>
        <Reference ReferenceType="HasComponent">
            <TargetId>ns=2;i=1003</TargetId>  <!-- ActualSpeed -->
        </Reference>
        <Reference ReferenceType="HasComponent">
            <TargetId>ns=2;i=1004</TargetId>  <!-- Status -->
        </Reference>
    </References>
</UAObjectType>

<!-- Variable for position -->
<UAVariable NodeId="ns=2;i=1002" BrowseName="2:ActualPosition" DataType="Double" AccessLevel="1">
    <DisplayName>Actual Position</DisplayName>
    <Description>Current robot position in mm</Description>
    <References>
        <Reference ReferenceType="HasTypeDefinition">i=63</Reference>
        <Reference ReferenceType="HasModellingRule">i=78</Reference>  <!-- Mandatory -->
        <Reference ReferenceType="HasProperty">
            <TargetId>ns=2;i=1005</TargetId>  <!-- EngineeringUnits -->
        </Reference>
    </References>
</UAVariable>

<!-- Engineering units property -->
<UAVariable NodeId="ns=2;i=1005" BrowseName="EngineeringUnits" DataType="i=887">
    <DisplayName>Engineering Units</DisplayName>
    <Value>
        <EUInformation>
            <NamespaceUri>http://www.opcfoundation.org/UA/units/un/cefact</NamespaceUri>
            <UnitId>4405427</UnitId>  <!-- mm -->
            <DisplayName>mm</DisplayName>
            <Description>millimeter</Description>
        </EUInformation>
    </Value>
</UAVariable>
```

### Companion Specifications

**PackML (Packaging Machine Language)**
```
Use OPC UA companion spec for PackML (OMAC):
- Standardized state machine
- Standard tags (UnitMode, MachineSpeed, ProductCount)
- Interchangeable machines from different vendors

Implementation:
1. Import PackML companion spec NodeSet
2. Instantiate PackML base object type
3. Extend with machine-specific data
```

**OPC UA for Robotics**
```
Companion spec provides:
- Standard robot properties (joints, speed, load)
- Standard methods (MoveTo, Home, Stop)
- Standard events (CollisionDetected, LimitReached)

Benefit: Same client code works with ABB, FANUC, KUKA, etc.
```

**AutoID (RFID/Barcode)**
```
Companion spec for automatic identification:
- RFID reader integration
- Barcode scanner integration
- Standardized read events
```

---

## Performance Optimization

### Reduce Network Traffic

**Batch Operations**
```csharp
// BAD: Individual reads (multiple network round trips)
var pos = session.ReadValue("ns=2;s=Robot.Position");
var speed = session.ReadValue("ns=2;s=Robot.Speed");
var status = session.ReadValue("ns=2;s=Robot.Status");

// GOOD: Single batch read
var nodes = new ReadValueIdCollection {
    new ReadValueId { NodeId = "ns=2;s=Robot.Position" },
    new ReadValueId { NodeId = "ns=2;s=Robot.Speed" },
    new ReadValueId { NodeId = "ns=2;s=Robot.Status" }
};
session.Read(null, 0, TimestampsToReturn.Both, nodes, out var results, out _);
```

**Use Subscriptions Instead of Polling**
```csharp
// BAD: Polling every second
while (true) {
    var value = session.ReadValue("ns=2;s=Tank.Level");
    ProcessValue(value);
    Thread.Sleep(1000);
}

// GOOD: Subscription with data change notification
var subscription = new Subscription(session.DefaultSubscription);
var item = new MonitoredItem {
    StartNodeId = "ns=2;s=Tank.Level",
    SamplingInterval = 1000
};
item.Notification += (s, e) => ProcessValue(e.NotificationValue);
subscription.AddItem(item);
session.AddSubscription(subscription);
subscription.Create();
```

### Connection Pooling

```csharp
// Reuse sessions instead of creating new ones
public class OpcUaConnectionPool {
    private static readonly ConcurrentDictionary<string, Session> _sessions = new();

    public static Session GetSession(string endpointUrl) {
        return _sessions.GetOrAdd(endpointUrl, url => {
            // Create and configure session
            var session = CreateSession(url);

            // Handle disconnection
            session.KeepAlive += (s, e) => {
                if (ServiceResult.IsBad(e.Status)) {
                    _sessions.TryRemove(url, out _);
                }
            };

            return session;
        });
    }

    private static Session CreateSession(string endpointUrl) {
        // Session creation logic
    }
}
```

---

## Troubleshooting

### Common Issues

**Certificate Trust Issues**
```
Error: "The certificate is not trusted"

Solutions:
1. Copy server certificate to client's trusted store
2. Ensure certificate is not expired
3. Verify Subject Alternative Name matches connection URL
4. Check certificate chain (intermediate CAs)
```

**Connection Timeouts**
```
Error: "The operation timed out"

Solutions:
1. Increase OperationTimeout in TransportQuotas
2. Check network connectivity and firewall rules
3. Verify server is running and accepting connections
4. Check server load (may be too busy)
```

**Bad Quality Data**
```
StatusCode: BadWaitingForInitialData

Meaning: Server hasn't received value from device yet
Action: Wait for device connection or check device communication
```

### Diagnostics

**Enable Trace Logging**
```csharp
// Enable OPC UA stack tracing
Utils.SetTraceMask(Utils.TraceMasks.All);
Utils.SetTraceOutput(Utils.TraceOutput.FileOnly);
Utils.SetTraceLog("/var/log/opcua/client_%date%.log", true);

// Trace levels:
- TraceMasks.None
- TraceMasks.Error
- TraceMasks.Information
- TraceMasks.StackTrace
- TraceMasks.Service
- TraceMasks.All
```

**Monitor Session Health**
```csharp
session.KeepAlive += (sender, e) => {
    Console.WriteLine($"KeepAlive: {e.CurrentState}");
    Console.WriteLine($"Server Status: {e.ServerState}");

    if (ServiceResult.IsBad(e.Status)) {
        Console.WriteLine($"KeepAlive failed: {e.Status}");
        // Trigger reconnection
        ReconnectSession();
    }
};
```

---

## Integration Patterns

### OPC UA to MQTT Bridge

```csharp
// Bridge OPC UA data to MQTT for cloud/IIoT integration
public class OpcUaToMqttBridge {
    private Session _opcSession;
    private IMqttClient _mqttClient;

    public async Task BridgeData(string nodeId, string mqttTopic) {
        // Create OPC UA subscription
        var subscription = new Subscription(_opcSession.DefaultSubscription) {
            PublishingInterval = 1000
        };

        var monitoredItem = new MonitoredItem {
            StartNodeId = nodeId,
            SamplingInterval = 1000
        };

        // On OPC UA data change, publish to MQTT
        monitoredItem.Notification += async (item, e) => {
            var notification = (MonitoredItemNotification)e.NotificationValue;
            var payload = JsonSerializer.Serialize(new {
                timestamp = notification.Value.SourceTimestamp,
                value = notification.Value.Value,
                quality = notification.Value.StatusCode.ToString()
            });

            await _mqttClient.PublishAsync(new MqttApplicationMessage {
                Topic = mqttTopic,
                Payload = Encoding.UTF8.GetBytes(payload),
                QualityOfServiceLevel = MqttQualityOfServiceLevel.AtLeastOnce
            });
        };

        subscription.AddItem(monitoredItem);
        _opcSession.AddSubscription(subscription);
        subscription.Create();
    }
}
```

### OPC UA to Time-Series Database

```csharp
// Write OPC UA data to InfluxDB
public class OpcUaToInfluxBridge {
    private Session _opcSession;
    private InfluxDBClient _influxClient;

    public void StreamToInflux(List<string> nodeIds) {
        var subscription = new Subscription(_opcSession.DefaultSubscription);

        foreach (var nodeId in nodeIds) {
            var item = new MonitoredItem {
                StartNodeId = nodeId,
                SamplingInterval = 1000
            };

            item.Notification += async (sender, e) => {
                var notification = (MonitoredItemNotification)e.NotificationValue;
                var tagName = ExtractTagName(item.StartNodeId);

                var point = PointData
                    .Measurement("manufacturing")
                    .Tag("equipment", tagName)
                    .Field("value", Convert.ToDouble(notification.Value.Value))
                    .Timestamp(notification.Value.SourceTimestamp, WritePrecision.Ms);

                await _influxClient.GetWriteApiAsync().WritePointAsync(point);
            };

            subscription.AddItem(item);
        }

        _opcSession.AddSubscription(subscription);
        subscription.Create();
    }
}
```

---

## PLC Server Implementation

### Siemens S7-1500 OPC UA Server

```
Configuration Steps:
1. Enable OPC UA server in TIA Portal
2. Configure security policy (Basic256Sha256 minimum)
3. Define address space structure
4. Export server certificate
5. Configure user authentication
6. Set access permissions per user role
7. Test with UAExpert client

Access:
- Endpoint: opc.tcp://<PLC_IP>:4840
- Username: From PLC user management
- Security: Sign & Encrypt required
```

### Allen-Bradley ControlLogix OPC UA

```
Implementation:
- Use FactoryTalk Linx Gateway
- Maps tags to OPC UA address space
- Supports array and UDT types
- Alarms mapped to OPC UA events

Configuration:
1. Install FactoryTalk Linx on server
2. Add PLC to device tree
3. Enable OPC UA endpoint
4. Configure security certificates
5. Map tag groups to OPC UA folders
```

---

## Testing & Validation

### UAExpert (Free Client Tool)

```
Download: https://www.unified-automation.com/products/development-tools/uaexpert.html

Features:
- Browse OPC UA servers
- Read/write values
- Create subscriptions
- Test method calls
- Monitor connection quality
- Certificate management
- Export address space to NodeSet XML

Use for:
- Server validation
- Address space exploration
- Integration testing
- Performance testing
```

### Automated Testing

```csharp
[Test]
public async Task TestOpcUaConnection() {
    var endpoint = "opc.tcp://localhost:4840";
    var session = await CreateSessionAsync(endpoint);

    Assert.IsNotNull(session);
    Assert.IsTrue(session.Connected);

    await session.CloseAsync();
}

[Test]
public async Task TestReadWrite() {
    var session = await CreateSessionAsync("opc.tcp://localhost:4840");
    var nodeId = new NodeId("ns=2;s=TestVariable");

    // Write test value
    var writeValue = new WriteValue {
        NodeId = nodeId,
        Value = new DataValue(new Variant(42.5))
    };
    session.Write(null, new WriteValueCollection { writeValue }, out var results, out _);
    Assert.IsTrue(StatusCode.IsGood(results[0]));

    // Read back
    var readValue = session.ReadValue(nodeId);
    Assert.AreEqual(42.5, (double)readValue.Value);
}
```

---

## References

- **OPC Foundation**: https://opcfoundation.org/
- **OPC UA Specifications**: https://opcfoundation.org/developer-tools/specifications-unified-architecture
- **UA .NET Standard Library**: https://github.com/OPCFoundation/UA-.NETStandard
- **Companion Specifications**: https://opcfoundation.org/about/opc-technologies/opc-ua/ua-companion-specifications/
- **UAExpert**: https://www.unified-automation.com/products/development-tools/uaexpert.html

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**OPC UA Version**: 1.04+
**Applies To**: Industrial automation, MES integration, IIoT platforms
