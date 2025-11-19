# SCADA System Development Guide

## 1. SCADA Architecture Design

### 1.1 System Requirements Definition

**Example: Pharmaceutical Manufacturing SCADA**

```
SYSTEM: Manufacturing Execution SCADA (MES Integration)
FACILITIES: 3 production sites, 45 manufacturing lines
DEVICES: 500+ PLCs, 2000+ sensors
USERS: 200+ operators, 50 engineers, 10 administrators

PERFORMANCE REQUIREMENTS:
├─ Data latency: < 5 seconds (sensor to database)
├─ Query response: < 2 seconds for last 24 hours
├─ System uptime: 99.5% (43.8 hours/year downtime max)
├─ Concurrent users: 100+ simultaneous
├─ Historical data retention: 5 years minimum
└─ Audit trail completeness: 100% (FDA requirement)

FUNCTIONAL REQUIREMENTS:
├─ Real-time trend displays (temperature, pressure, flow)
├─ Alarm & event management with multilevel acknowledgment
├─ Manual operator commands (setpoint changes, start/stop)
├─ Batch record generation (FDA 21 CFR Part 11)
├─ Integration with MES for recipe management
├─ Remote access via encrypted connection
└─ Mobile app for status monitoring

SECURITY REQUIREMENTS:
├─ User authentication (Active Directory integration)
├─ Role-based access control (RBAC)
│  ├─ Operator (read-only monitoring)
│  ├─ Supervisor (can change setpoints, acknowledge alarms)
│  ├─ Engineer (full access including diagnostics)
│  └─ Administrator (system configuration, user management)
├─ Encrypted communication (TLS 1.2 minimum)
├─ Audit logging (all actions with timestamp, user ID)
├─ Data encryption at rest (AES-256)
└─ Intrusion detection monitoring

COMPLIANCE REQUIREMENTS:
├─ FDA 21 CFR Part 11 (electronic records)
├─ EU GMP Annex 11 (computer systems validation)
├─ NIST Cybersecurity Framework
└─ ISO 13849-1 (safety-related systems)
```

### 1.2 Network Architecture

**Three-Tier Architecture:**

```
┌──────────────────────────────────────────────┐
│ TIER 1: PRESENTATION LAYER                   │
├──────────────────────────────────────────────┤
│ - Web browser (responsive design)            │
│ - Mobile app (iOS/Android)                   │
│ - Desktop HMI client                         │
│ - Remote access (VPN)                        │
└────────────────┬─────────────────────────────┘
                 │
    ┌────────────┴──────────────┐
    │ (HTTPS/TLS 1.2)          │
    │ Port 443                 │
    │
┌───v──────────────────────────────────────────┐
│ TIER 2: APPLICATION LAYER                    │
├──────────────────────────────────────────────┤
│ Application Server (IIS/Tomcat)              │
│ ├─ Web services (REST/SOAP)                  │
│ ├─ Business logic (rule engine)              │
│ ├─ Session management                        │
│ ├─ User authentication                       │
│ ├─ Authorization enforcement                 │
│ └─ Audit logging                             │
└────────────────┬─────────────────────────────┘
                 │
    ┌────────────┴──────────────┐
    │ (JDBC/OLEDB)             │
    │ Port 1433 (SQL Server)   │
    │
┌───v──────────────────────────────────────────┐
│ TIER 3: DATA LAYER                           │
├──────────────────────────────────────────────┤
│ Database Server (SQL Server 2019 Enterprise) │
│ ├─ Historian database (time-series data)     │
│ ├─ Alarm & event logs                        │
│ ├─ User accounts & permissions               │
│ ├─ System configuration                      │
│ └─ Batch records (FDA compliance)            │
│                                              │
│ Backup/Replication:                          │
│ ├─ Redundant database (Active-Active)        │
│ ├─ Synchronous replication (< 10ms)          │
│ └─ Automatic failover on primary failure     │
└───────────────────────────────────────────────┘

OT NETWORK (Manufacturing Floor):
             │
    ┌────────┴────────────┬──────────────┐
    │                     │              │
┌───v────────┐     ┌──────v──────┐   ┌──v──────┐
│ PLC Site 1 │     │ PLC Site 2  │   │ RTU #3  │
│ Modbus TCP │     │ PROFINET    │   │ Modbus  │
│ 192.168.1.0│     │ 192.168.2.0 │   │ Serial  │
└────────────┘     └─────────────┘   └─────────┘

Gateway Device:
├─ Industrial PC (IPC)
├─ Modbus Master (polls all devices)
├─ PROFINET Master (I-Task scheduling)
├─ OPC UA Server (aggregates data)
└─ Time sync (NTP client)
```

---

## 2. Database Design

### 2.1 Historian Schema (Time-Series Data)

**Core Tables:**

```sql
-- Tag Definition (Metadata)
CREATE TABLE TagDefinition (
    tag_id INT PRIMARY KEY IDENTITY(1,1),
    tag_name VARCHAR(255) UNIQUE NOT NULL,
    description VARCHAR(500),
    data_type TINYINT,              -- 1=BOOL, 2=INT, 3=REAL, 4=STRING
    min_value FLOAT,
    max_value FLOAT,
    engineering_units VARCHAR(50),
    scan_rate_ms INT DEFAULT 1000,
    compression_method TINYINT,     -- 0=none, 1=swinging_door
    compression_tolerance FLOAT,
    archive_enabled BIT DEFAULT 1,
    created_date DATETIME DEFAULT GETDATE(),
    modified_date DATETIME DEFAULT GETDATE()
);

-- Historical Values (Time-Series)
CREATE TABLE HistoricalValues (
    record_id BIGINT PRIMARY KEY IDENTITY(1,1),
    tag_id INT NOT NULL FOREIGN KEY (TagDefinition),
    timestamp DATETIME NOT NULL,
    value FLOAT,
    quality TINYINT,               -- 0=Good, 1=Uncertain, 2=Bad
    source_address VARCHAR(50),     -- e.g., "192.168.1.100:40001"
    INDEX idx_tag_timestamp (tag_id, timestamp DESC)
);

-- Aggregate Tables (for performance)
CREATE TABLE HistoricalValues_Minute (
    tag_id INT NOT NULL,
    timestamp_minute DATETIME NOT NULL,
    min_value FLOAT,
    max_value FLOAT,
    avg_value FLOAT,
    last_value FLOAT,
    sample_count INT,
    PRIMARY KEY (tag_id, timestamp_minute)
);

CREATE TABLE HistoricalValues_Hour (
    tag_id INT NOT NULL,
    timestamp_hour DATETIME NOT NULL,
    min_value FLOAT,
    max_value FLOAT,
    avg_value FLOAT,
    last_value FLOAT,
    sample_count INT,
    PRIMARY KEY (tag_id, timestamp_hour)
);

-- Alarms & Events
CREATE TABLE AlarmHistory (
    event_id BIGINT PRIMARY KEY IDENTITY(1,1),
    tag_id INT NOT NULL FOREIGN KEY (TagDefinition),
    alarm_type VARCHAR(50),         -- 'HIGH_ALARM', 'LOW_ALARM', 'DEVIATION'
    alarm_severity TINYINT,         -- 1=Info, 2=Warning, 3=Critical, 4=Emergency
    trigger_time DATETIME NOT NULL,
    clear_time DATETIME,
    operator_id INT FOREIGN KEY (Users.user_id),
    acknowledgement_time DATETIME,
    acknowledgement_comment VARCHAR(500),
    INDEX idx_alarm_time (trigger_time DESC)
);

-- User Access Audit
CREATE TABLE AuditLog (
    audit_id BIGINT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL FOREIGN KEY (Users.user_id),
    action_type VARCHAR(50),       -- 'LOGIN', 'LOGOUT', 'SETPOINT_CHANGE', 'ALARM_ACK'
    affected_resource VARCHAR(255),
    old_value VARCHAR(500),
    new_value VARCHAR(500),
    action_time DATETIME NOT NULL DEFAULT GETDATE(),
    ip_address VARCHAR(15),
    result VARCHAR(50),             -- 'SUCCESS', 'FAILED', 'DENIED'
    INDEX idx_audit_user_time (user_id, action_time DESC)
);

-- Batch Records (FDA 21 CFR Part 11)
CREATE TABLE BatchRecords (
    batch_id VARCHAR(50) PRIMARY KEY,
    batch_start_time DATETIME NOT NULL,
    batch_end_time DATETIME,
    recipe_id INT FOREIGN KEY (Recipes.recipe_id),
    product_id INT,
    operator_id INT FOREIGN KEY (Users.user_id),
    status VARCHAR(50),             -- 'ACTIVE', 'COMPLETED', 'FAILED', 'ABORTED'
    electronic_signature_user INT,
    electronic_signature_time DATETIME,
    created_date DATETIME DEFAULT GETDATE(),
    INDEX idx_batch_time (batch_start_time DESC)
);

-- Batch Data (Linked to batch)
CREATE TABLE BatchData (
    batch_data_id BIGINT PRIMARY KEY IDENTITY(1,1),
    batch_id VARCHAR(50) NOT NULL FOREIGN KEY (BatchRecords),
    tag_id INT NOT NULL FOREIGN KEY (TagDefinition),
    timestamp DATETIME NOT NULL,
    value FLOAT,
    unit VARCHAR(20),
    -- Important: This allows FDA audit trail of exact batch conditions
);

-- System Configuration
CREATE TABLE SystemParameters (
    param_id INT PRIMARY KEY IDENTITY(1,1),
    param_name VARCHAR(100) UNIQUE NOT NULL,
    param_value VARCHAR(1000),
    param_type VARCHAR(20),         -- 'BOOLEAN', 'INTEGER', 'FLOAT', 'STRING'
    description VARCHAR(500),
    last_modified DATETIME DEFAULT GETDATE(),
    modified_by INT FOREIGN KEY (Users.user_id)
);

-- Users & Roles
CREATE TABLE Users (
    user_id INT PRIMARY KEY IDENTITY(1,1),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100),
    full_name VARCHAR(100),
    role_id INT NOT NULL FOREIGN KEY (Roles.role_id),
    is_active BIT DEFAULT 1,
    created_date DATETIME DEFAULT GETDATE(),
    last_login DATETIME,
    account_locked BIT DEFAULT 0
);

CREATE TABLE Roles (
    role_id INT PRIMARY KEY IDENTITY(1,1),
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(500),
    permission_level TINYINT      -- 1=Operator, 2=Supervisor, 3=Engineer, 4=Admin
);
```

### 2.2 Indexing Strategy

**Performance Optimization:**

```sql
-- Critical indexes for query performance

-- Most common query: Get last N samples for tag
CREATE INDEX idx_tag_timestamp_desc
ON HistoricalValues (tag_id, timestamp DESC)
WHERE quality = 0;  -- Filtered index: only "good" quality data

-- Alarm query: Unacknowledged alarms in last 7 days
CREATE INDEX idx_unacknowledged_alarms
ON AlarmHistory (trigger_time DESC)
WHERE acknowledgement_time IS NULL;

-- Audit trail: User actions in date range
CREATE INDEX idx_audit_user_time
ON AuditLog (user_id, action_time DESC);

-- Batch data: All samples for specific batch
CREATE INDEX idx_batch_tag_time
ON BatchData (batch_id, tag_id, timestamp DESC);

-- Archive maintenance: Records older than retention period
CREATE INDEX idx_archivable_records
ON HistoricalValues (timestamp)
WHERE timestamp < DATEADD(year, -5, GETDATE());
```

---

## 3. SCADA Server Implementation

### 3.1 Real-Time Data Collection Service

**C# Example (WinCC Advanced / .NET)**

```csharp
using System;
using System.Collections.Concurrent;
using System.Threading;
using System.Threading.Tasks;
using EasyModbusTCP;

public class DataCollectionService
{
    private readonly ILogger<DataCollectionService> _logger;
    private readonly ModbusClient _modbusClient;
    private readonly IHistorianRepository _historian;
    private readonly ConcurrentDictionary<string, TagValue> _tagCache;
    private CancellationTokenSource _cancellationToken;

    public DataCollectionService(ILogger<DataCollectionService> logger,
                                  IHistorianRepository historian)
    {
        _logger = logger;
        _historian = historian;
        _tagCache = new ConcurrentDictionary<string, TagValue>();
        _modbusClient = new ModbusClient("192.168.1.100", 502)
        {
            ConnectTimeout = 2000,
            SendTimeout = 2000
        };
    }

    public async Task StartAsync(CancellationToken stoppingToken)
    {
        _cancellationToken = CancellationTokenSource.CreateLinkedTokenSource(stoppingToken);
        _logger.LogInformation("Data Collection Service starting");

        try
        {
            // Connect to Modbus device
            if (!_modbusClient.Connected)
            {
                _modbusClient.Connect();
            }

            // Start continuous polling loop
            await PollDevicesAsync(_cancellationToken.Token);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Data Collection Service error");
            await Task.Delay(5000, stoppingToken);  // Retry after 5 seconds
        }
    }

    private async Task PollDevicesAsync(CancellationToken cancellationToken)
    {
        int scanCount = 0;
        Stopwatch scanTimer = Stopwatch.StartNew();

        while (!cancellationToken.IsCancellationRequested)
        {
            try
            {
                // Read analog inputs (temperature sensors)
                // Function code 04: Read Input Registers
                float[] temperatures = _modbusClient.ReadFloats(1, 30000, 6);

                // Read digital inputs (status signals)
                bool[] statusBits = _modbusClient.ReadCoils(1, 100, 16);

                // Store in cache with timestamp
                for (int i = 0; i < temperatures.Length; i++)
                {
                    var tagValue = new TagValue
                    {
                        TagId = i + 1,
                        Value = temperatures[i],
                        Timestamp = DateTime.UtcNow,
                        Quality = ValidateTemperatureSensor(i, temperatures[i])
                    };
                    _tagCache.AddOrUpdate($"TEMP_ZONE_{i+1}", tagValue, (k, v) => tagValue);
                }

                // Periodically flush to historian (every 10 scan cycles)
                if ((++scanCount % 10) == 0)
                {
                    await FlushToHistorianAsync();
                }

                // Monitor scan cycle time
                if (scanTimer.ElapsedMilliseconds > 1000)  // Report every second
                {
                    _logger.LogDebug($"Scan cycle: {scanTimer.ElapsedMilliseconds}ms, Tags: {_tagCache.Count}");
                    scanTimer.Restart();
                }

                // Wait until next scan interval (500ms)
                await Task.Delay(500, cancellationToken);
            }
            catch (EasyModbusException ex)
            {
                _logger.LogWarning($"Modbus communication error: {ex.Message}");
                await Task.Delay(2000, cancellationToken);  // Wait before retry
            }
        }
    }

    private async Task FlushToHistorianAsync()
    {
        try
        {
            var valuesToWrite = _tagCache.Values.ToList();
            await _historian.InsertHistoricalValuesAsync(valuesToWrite);
            _logger.LogDebug($"Flushed {valuesToWrite.Count} values to historian");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error writing to historian");
        }
    }

    private int ValidateTemperatureSensor(int zoneIndex, float temperature)
    {
        // Quality: 0=Good, 1=Uncertain, 2=Bad

        if (temperature < -50 || temperature > 100)
            return 2;  // Bad - out of range

        if (temperature == _tagCache.TryGetValue($"TEMP_ZONE_{zoneIndex+1}", out var prev) ?
                          prev.Value : 0)
            return 1;  // Uncertain - no change (stuck sensor?)

        return 0;      // Good
    }

    public async Task StopAsync()
    {
        _logger.LogInformation("Data Collection Service stopping");
        _cancellationToken?.Cancel();
        _modbusClient?.Disconnect();
    }
}
```

### 3.2 Alarm Management Service

```csharp
public class AlarmService
{
    private readonly IHistorianRepository _historian;
    private readonly INotificationService _notifications;
    private readonly Dictionary<int, AlarmState> _alarmStates;

    public async Task EvaluateAlarmsAsync(List<TagValue> currentValues)
    {
        foreach (var value in currentValues)
        {
            var tagConfig = await _historian.GetTagConfigurationAsync(value.TagId);

            if (tagConfig?.AlarmHighThreshold != null && value.Value > tagConfig.AlarmHighThreshold)
            {
                await RaiseAlarmAsync(value.TagId, "HIGH_ALARM", value);
            }
            else if (tagConfig?.AlarmLowThreshold != null && value.Value < tagConfig.AlarmLowThreshold)
            {
                await RaiseAlarmAsync(value.TagId, "LOW_ALARM", value);
            }
            else
            {
                // Clear alarm if threshold no longer exceeded
                await ClearAlarmAsync(value.TagId);
            }
        }
    }

    private async Task RaiseAlarmAsync(int tagId, string alarmType, TagValue value)
    {
        if (!_alarmStates.ContainsKey(tagId) || !_alarmStates[tagId].IsActive)
        {
            var alarm = new AlarmEvent
            {
                TagId = tagId,
                AlarmType = alarmType,
                TriggerTime = DateTime.UtcNow,
                Severity = DetermineSeverity(alarmType),
                Value = value.Value
            };

            // Store in database
            await _historian.InsertAlarmEventAsync(alarm);

            // Send notification
            await _notifications.NotifyAsync(alarm);

            // Update state
            _alarmStates[tagId] = new AlarmState { IsActive = true, AlarmEvent = alarm };
        }
    }

    private async Task ClearAlarmAsync(int tagId)
    {
        if (_alarmStates.ContainsKey(tagId) && _alarmStates[tagId].IsActive)
        {
            _alarmStates[tagId].AlarmEvent.ClearTime = DateTime.UtcNow;
            await _historian.UpdateAlarmEventAsync(_alarmStates[tagId].AlarmEvent);
            _alarmStates[tagId].IsActive = false;
        }
    }
}
```

---

## 4. HMI Design Principles

### 4.1 Dashboard Layout Best Practices

**Effective Layout Structure:**

```
┌─────────────────────────────────────────────────────────┐
│ HEADER (Always visible)                                 │
│ ├─ System title, logo                                   │
│ ├─ Current time, operator name                         │
│ ├─ System status indicator (online/offline)            │
│ └─ Top navigation (Home, Details, Alarms, Reports)    │
├─────────────────────────────────────────────────────────┤
│ MAIN CONTENT AREA (Responsive to screen size)          │
│                                                          │
│ ┌─────────────────────────────────────────────────┐    │
│ │ QUICK STATUS (Top left - 25% width)            │    │
│ │ ├─ Active alarms (red badges)                  │    │
│ │ ├─ System mode (AUTOMATIC/MANUAL)              │    │
│ │ ├─ Production line status                      │    │
│ │ └─ Overall equipment effectiveness (OEE) %     │    │
│ └─────────────────────────────────────────────────┘    │
│                                                          │
│ ┌─────────────────────────────────────────────────┐    │
│ │ MAIN PROCESS VISUALIZATION (75% width)         │    │
│ │                                                  │    │
│ │ Zone 1: 45.2°C ●────────────●── Heater 85%   │    │
│ │         Target 45°C         Cooler  0%         │    │
│ │                                                  │    │
│ │ Zone 2: 46.1°C ●────────────●── Heater 70%   │    │
│ │         Target 45°C         Cooler  0%         │    │
│ │                                                  │    │
│ │ Zone 3: [ALARM] 52.5°C !    Heater OFF        │    │
│ │         Target 45°C         Cooler 100%        │    │
│ │                                                  │    │
│ └─────────────────────────────────────────────────┘    │
│                                                          │
│ ┌─────────────────────────────────────────────────┐    │
│ │ TREND CHART (2-hour rolling window)            │    │
│ │                                                  │    │
│ │  60°C ┤                                         │    │
│ │  50°C ┤   ╱╲                    ╱╲              │    │
│ │  40°C ┤  ╱  ╲      ╱╲          ╱  ╲             │    │
│ │  30°C ┤_╱____╲____╱__╲________╱____╲_           │    │
│ │       └──────┬──────┬──────┬──────┬──           │    │
│ │           0h    30m   1h    90m   2h            │    │
│ │                                                  │    │
│ │ Legend: Zone 1 ─── Zone 2 ──── Zone 3 ─ ─ ─   │    │
│ └─────────────────────────────────────────────────┘    │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ FOOTER                                                   │
│ ├─ Network status (● = Online)                         │
│ ├─ Last update: 12:45:30                               │
│ ├─ Database: Connected ✓                               │
│ └─ Help | Settings | Logout                            │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Color Coding & Visual Standards

```
Status Colors:
┌────────────────────────────────────────────┐
│ Color      | Use Case                      │
├────────────────────────────────────────────┤
│ #00AA00    │ Normal operation, running     │
│ #FFFF00    │ Caution, adjusting, warm     │
│ #FF9900    │ Warning, elevated alert      │
│ #FF0000    │ Critical, error, alarm       │
│ #808080    │ Offline, unknown, disabled   │
│ #0000FF    │ Information, mode selection  │
│ #CCCCCC    │ Neutral, background          │
└────────────────────────────────────────────┘

Alarm Indicators:
- RED box: Critical alarm (immediate action needed)
- ORANGE box: Warning (monitor closely)
- YELLOW text: Information (status update)
- Blinking: Attention-demanding (unacknowledged alarm)

Equipment Status (Pump Example):
Status          Color    Icon         Meaning
───────────────────────────────────────────────
Running         Green    ◉ (filled)   Normal operation
Stopped         Gray     ◯ (empty)    Off/standby
Warning         Yellow   ⚠ (triangle) Elevated load
Fault           Red      ✗ (X)        Alarm condition
Unknown         Gray     ? (question) Comms lost
```

---

## 5. Integration with Manufacturing Systems

### 5.1 MES Integration (ISA-95 Level 3-4 Bridge)

**Recipe Management Flow:**

```
MES → SCADA Recipe Handoff:

MES sends production order:
{
  "batch_id": "BATCH_20240115_001",
  "product_id": "PROD_DRYING_STANDARD",
  "recipe_id": "RECIPE_DRY_45C_8H",
  "start_time": "2024-01-15T14:00:00Z",
  "recipe_steps": [
    {
      "step": 1,
      "name": "Preheat",
      "duration_minutes": 30,
      "zones": [
        {
          "zone_id": 1,
          "setpoint": 35.0,
          "ramp_rate": 5.0,      // °C per minute
          "hold_tolerance": 1.0   // ±°C
        },
        {
          "zone_id": 2,
          "setpoint": 35.0,
          "ramp_rate": 5.0,
          "hold_tolerance": 1.0
        }
        // ... zones 3-6
      ]
    },
    {
      "step": 2,
      "name": "Drying",
      "duration_minutes": 480,    // 8 hours
      "zones": [
        {
          "zone_id": 1,
          "setpoint": 45.0,
          "ramp_rate": 2.0,
          "hold_tolerance": 2.0
        }
        // ...
      ]
    },
    {
      "step": 3,
      "name": "Cooldown",
      "duration_minutes": 60,
      "zones": [
        {
          "zone_id": 1,
          "setpoint": 25.0,
          "ramp_rate": 3.0,
          "hold_tolerance": 1.0
        }
        // ...
      ]
    }
  ]
}

SCADA Processes:
1. Parse recipe, validate against equipment limits
2. Display recipe step on HMI (e.g., "Step 1 of 3: Preheat")
3. Execute setpoint changes automatically
4. Monitor ramp rate compliance
5. Record actual vs. setpoint in batch record
6. Send completion signal back to MES
7. Archive batch record (FDA compliance)

Batch Record Capture:
- Every 1 second: temperature, pressure, flow
- Every alarm event: timestamp, severity, acknowledgment
- Every setpoint change: timestamp, new value, operator
- Every state change: step transitions, mode changes
- Electronic signature: Batch completion and approval
```

### 5.2 ERP Integration (ISA-95 Level 4-5)

**Production Data Flow:**

```
SAP/Oracle ERP
    │
    └──→ MES (Production scheduler)
         │
         ├──→ SCADA (Recipe + control)
         │    └──→ PLC (Real-time execution)
         │         └──→ Equipment (Sensors/Actuators)
         │
         └──→ SCADA (Collects results)
              │
              └──→ ERP (Stores production history)
                   └──→ Business intelligence (cost analysis)

Data Integration Points:

↓ Downward (ERP → SCADA):
- Production schedule (what to make, when)
- Recipes (how to make it)
- Quality specs (acceptable ranges)
- Configuration changes (maintenance, limits)

↑ Upward (SCADA → ERP):
- Batch completion notifications
- Equipment utilization (run time, idle time)
- Product quality data (actual temperatures achieved)
- Downtime events (root cause analysis)
- Batch cost data (energy consumed, consumables used)
```

---

## 6. Security Implementation

### 6.1 Authentication & Authorization

**User Management:**

```sql
-- Role-based access control (RBAC)

CREATE TABLE Roles (
    role_id INT PRIMARY KEY,
    role_name VARCHAR(50),
    description VARCHAR(200)
);

INSERT INTO Roles VALUES
(1, 'Operator', 'View monitoring, acknowledge alarms'),
(2, 'Supervisor', 'Operator + change setpoints, start/stop'),
(3, 'Engineer', 'Supervisor + diagnostics, tuning'),
(4, 'Administrator', 'Full system control');

CREATE TABLE UserRoles (
    user_id INT,
    role_id INT,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (role_id) REFERENCES Roles(role_id)
);

-- Permissions by role

Operator (read-only):
├─ View real-time data
├─ View historical trends
├─ Acknowledge alarms
└─ View batch reports

Supervisor (operational control):
├─ All Operator permissions
├─ Change temperature setpoint (±5°C from design)
├─ Start/stop production
└─ View diagnostics (read-only)

Engineer (system control):
├─ All Supervisor permissions
├─ Modify PID parameters
├─ Add/edit alarms
├─ Modify system limits
└─ Access control system diagnostics

Administrator (full control):
├─ All Engineer permissions
├─ Create/modify users & roles
├─ Configure network devices
├─ Database administration
└─ System backups & recovery
```

### 6.2 Encryption & Communication Security

**TLS Configuration:**

```
SCADA Web Interface (HTTPS):
├─ Protocol: TLS 1.2 (minimum), TLS 1.3 (preferred)
├─ Certificate: Wildcard or SAN (subject alternative names)
├─ Key exchange: ECDHE (elliptic curve Diffie-Hellman)
├─ Cipher suite: AES-256-GCM
├─ Forward secrecy: Enabled (prevent decryption if key compromised)
├─ HSTS header: Enabled (force HTTPS always)
│  └─ max-age: 31536000 seconds (1 year)
├─ Certificate pinning: Consider for mobile apps
└─ Certificate renewal: Automated before 30-day warning

Database Encryption (SQL Server):
├─ Transparent Data Encryption (TDE) enabled
├─ Encryption at rest: AES-256
├─ Encryption in transit: Encrypted connections only
├─ Database backups: Encrypted with CEK (Column Encryption Key)
└─ Master Key: Hardware security module (HSM) backed

API Authentication:
├─ Method: OAuth 2.0 with PKCE (Proof Key for Code Exchange)
├─ Token lifetime: 1 hour (access token)
├─ Refresh token: 7 days (offline access)
├─ Scope: Granular permissions (read:temperature, write:setpoint)
└─ Rate limiting: 100 requests/minute per user
```

---

## 7. Deployment & Operations

### 7.1 Deployment Checklist

```
PRE-DEPLOYMENT (1 week before):
□ Database backups verified (test restore)
□ Application binaries signed and verified
□ Configuration files reviewed and tested
□ SSL/TLS certificates valid and renewable
□ Firewall rules documented and tested
□ Load balancer configured for failover
□ Monitoring alarms configured
□ Disaster recovery plan reviewed

DEPLOYMENT DAY:
□ Maintenance window announced (1 hour duration)
□ Take full database backup
□ Deploy application to staging (parallel environment)
□ Run smoke tests (basic functionality)
□ Validate database migrations completed
□ Test user login with multiple roles
□ Verify historical data accessible
□ Check alarm generation & notifications
□ Monitor system performance (CPU, memory, disk I/O)
□ Validate backup system still working

POST-DEPLOYMENT (Day 1):
□ Monitor system logs for errors
□ Verify all scheduled tasks running
□ Test disaster recovery failover
□ Confirm network connectivity to all OT devices
□ Validate data flow from all sources
□ Check email alerts working
□ Audit log entries appropriate

ONGOING (Weekly):
□ Database consistency check
□ Backup validation (test restore to alternate location)
□ Performance metrics (query times, slow queries)
□ Security audit (failed logins, permission changes)
□ Disk space trending (archive old data if needed)
```

### 7.2 Monitoring & Alerting

**Key Metrics to Monitor:**

```
System Health:
├─ CPU utilization (alert if > 75%)
├─ Memory utilization (alert if > 80%)
├─ Disk space (alert if < 20% free)
├─ Database transaction log growth
├─ Network bandwidth (% of capacity)
└─ TLS certificate expiration (alert 60 days before)

Application Health:
├─ Web service response time (alert if > 2 seconds)
├─ Failed database connections (alert if > 0)
├─ Queue depth (Modbus requests pending)
├─ Historian write rate (expected ~1000 samples/second)
└─ OPC UA subscription count (expected ~50-100)

Data Quality:
├─ Tags with "bad" quality (alert if > 5%)
├─ Missing samples (gap detection)
├─ Outlier detection (unusual values)
└─ Sensor drift (temperature rising 0.5°C/week = recal needed)

Business Metrics:
├─ Production batches completed per day (trending)
├─ Average batch cycle time
├─ Scrap rate (correlated with alarms)
└─ Energy consumption (temperature overshoot = wasted energy)

Alert Thresholds:
┌─────────────────────────┬────────┬──────────┐
│ Metric                  │ Warning│ Critical │
├─────────────────────────┼────────┼──────────┤
│ CPU utilization         │ 60%    │ 80%      │
│ Memory utilization      │ 70%    │ 85%      │
│ Disk free space         │ 30%    │ 10%      │
│ SCADA unavailable time  │ 30min  │ 60min    │
│ Database response time  │ 500ms  │ 2000ms   │
│ Failed Modbus polls     │ 3 times│ 5 times  │
└─────────────────────────┴────────┴──────────┘
```

---

## Document Version: 2.0
**Last Updated:** January 2024
**Reference Standards:** ISA-95, IEC 62541, FDA 21 CFR Part 11
