# SCADA Systems Reference Guide

## SCADA Architecture Overview

### System Components

```
┌────────────────────────────────────────────────────┐
│            SCADA Application Server                │
│  ┌──────────────────────────────────────────────┐  │
│  │ Core Services:                               │  │
│  │ - Real-time data processing                  │  │
│  │ - Alarm & event management                   │  │
│  │ - Historical data storage                    │  │
│  │ - Report generation                          │  │
│  │ - User authentication & authorization        │  │
│  └──────────────────────────────────────────────┘  │
└──────────────┬─────────────────────────────────────┘
               │
    ┌──────────┴──────────┬───────────────┐
    │                     │               │
┌───v───────┐      ┌──────v────┐   ┌────v──────┐
│ HMI       │      │ Database   │   │ Protocol  │
│Dashboards │      │ (Historian)│   │Gateways   │
└───────────┘      └───────────┘   └────┬──────┘
                                        │
                   ┌────────────────────┼─────────────────┐
                   │                    │                 │
              ┌────v─────┐         ┌─────v────┐     ┌────v─────┐
              │PLC/DCS   │         │RTU       │     │Historian │
              │(Site 1)  │         │(Site 2)  │     │Database  │
              └──────────┘         └──────────┘     └──────────┘
```

### Data Flow Layers

```
Level 4: MES/ERP Integration
    ↓ (Batch data, recipes, production schedule)
Level 3: SCADA Supervisory
    - Process monitoring
    - Trending and alarms
    - Production metrics
    ↓ (Modbus TCP, OPC UA, PROFINET)
Level 2: PLC/DCS Controllers
    - Real-time logic
    - Device drivers
    - Local safety functions
    ↓ (I/O signals)
Level 1: Field Instruments
    - Sensors (temperature, pressure, flow)
    - Actuators (pumps, motors, valves)
    - Process equipment
    ↓
Level 0: Physical Process
    - Manufacturing equipment
    - Chemical reactors
    - Production lines
```

---

## SCADA Server Configuration

### Typical SCADA Server Specifications

**Hardware Requirements:**

```
Processor:      Intel Xeon / AMD EPYC (Multi-core, 3.5+ GHz)
RAM:            64-256 GB (depends on historian size)
Storage:        SSD RAID-10 (Enterprise grade)
                - 1-2 TB for historian (5 years data)
                - 500 GB for OS and applications
Network:        Dual Gigabit Ethernet (redundant)
UPS:            24+ hour battery backup, generator failover
Cooling:        Redundant CRAC units, hot-swappable fans
```

**Software Stack (Siemens WinCC Example):**

```
Operating System:  Windows Server 2019/2022 (Enterprise)
SCADA Software:    Siemens WinCC Advanced
Database:          Microsoft SQL Server (Standard/Enterprise)
Web Server:        IIS (Internet Information Services)
Runtime:           .NET Framework 4.8+
Communications:    PROFINET, Modbus TCP, OPC UA
```

---

## Real-Time Data Management

### Scan Cycle Architecture

```
Scan Cycle (typical: 100ms - 1 second)

┌─────────────────────────────┐
│ 1. Poll Controllers (50ms)  │
│   - Modbus requests         │
│   - OPC UA subscriptions    │
│   - PROFINET I/O updates    │
├─────────────────────────────┤
│ 2. Data Validation (10ms)   │
│   - Range checks            │
│   - Sensor failure detection│
│   - Dead-band filtering     │
├─────────────────────────────┤
│ 3. Alarm & Event Evaluation │
│   - Threshold checks        │
│   - Rate-of-change analysis │
│   - Alarm generation        │
├─────────────────────────────┤
│ 4. Historical Storage (30ms)│
│   - Data compression        │
│   - Historian database write│
│   - Archive management      │
├─────────────────────────────┤
│ 5. Report Generation        │
│   - Batch summaries         │
│   - Performance metrics     │
│   - Compliance reports      │
├─────────────────────────────┤
│ 6. Housekeeping (10ms)      │
│   - Database maintenance    │
│   - Log rotation            │
│   - Cache management        │
└─────────────────────────────┘

Total Cycle: ~150ms (actual varies by system load)
```

### Data Compression Algorithms

**Swinging Door Compression:**

```
Algorithm reduces historian data while preserving trends.

Before (100 samples):
[10, 10.5, 11, 11.2, 11.5, 11.3, 11.8, 12, 11.9, 12.1, ...]

After (compressed 10 samples):
[10, 11.5, 11.8, 12.1, ...]

Logic:
- Store first value
- Calculate door boundaries (±compression_tolerance)
- Skip values within door
- Store new value when door boundary crossed
- Result: 90% data reduction, minimal trend loss
```

**Compression Ratio Typical Values:**

```
Industry                Ratio       Storage saved
Chemical Plant          10:1-15:1   90-93%
Petrochemical          15:1-25:1   93-96%
Food & Beverage         5:1-8:1    80-87%
Pharmaceutical          8:1-12:1   87-92% (higher compliance needs)
```

---

## Alarm Management

### Alarm Severity Levels (ISA-18.2)

```
Level  Name          Color   Audible  Auto-ack  Response
─────────────────────────────────────────────────────────
1      EMERGENCY     Red     Loud     NO        Immediate action
2      ALERT         Red     Loud     NO        Urgent response
3      CRITICAL      Orange  Loud     NO        Priority handling
4      MAJOR         Yellow  Medium   NO        Timely response
5      MINOR         Blue    Soft     YES       Normal handling
6      INFORMATIONAL Green   NONE     YES       Logging only

EMERGENCY Example:
- Loss of primary cooling system
- Reactor temperature critical
- Safety interlocks activated

INFORMATIONAL Example:
- Batch started
- Equipment online
- Routine state changes
```

### Alarm Configuration Best Practices

**Dead-band Filtering:**

```
Temperature setpoint: 50°C
Dead-band: 2°C

Alarm HIGH set at: 52°C
    - Triggers when T > 52°C
    - Clears when T < 51°C (52 - 1 = hysteresis)

Alarm LOW set at: 48°C
    - Triggers when T < 48°C
    - Clears when T > 49°C

Result: Prevents alarm chatter near setpoint
```

**Alarm Suppression Strategies:**

```
1. Startup Suppression
   - Suppress alarms for 5 minutes after controller startup
   - Prevent false alarms during initialization

2. Permissive Suppression
   - Suppress high-flow alarms when pump not running
   - Only evaluate alarms when process active

3. Maintenance Suppression
   - Operator can manually suppress known alarms
   - Audit trail required per ISA-18.2

4. Cascading Alarm Prevention
   - If PRIMARY_SYSTEM fails, suppress dependent alarms
   - Reduce alarm storm from single failure
```

---

## Historical Data Management

### Historian Database Schema

**Tag Definition Table:**

```
CREATE TABLE TagDefinition (
    tag_id INT PRIMARY KEY,
    tag_name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    data_type INT,                  (* 1=DINT, 2=REAL, 3=BOOL, 4=STRING *)
    min_value FLOAT,
    max_value FLOAT,
    engineering_units VARCHAR(20),   (* 'C', 'PSI', 'L/min', etc. *)
    scan_rate INT,                  (* milliseconds *)
    compression_tolerance FLOAT,
    record_date DATETIME,
    UNIQUE (tag_name)
);
```

**Historical Data Table:**

```
CREATE TABLE HistoricalData (
    record_id BIGINT PRIMARY KEY IDENTITY,
    tag_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    value FLOAT,
    quality INT,                    (* 0=Good, 1=Uncertain, 2=Bad *)
    status VARCHAR(50),             (* 'NORMAL', 'ALARM', 'MAINTENANCE' *)
    FOREIGN KEY (tag_id) REFERENCES TagDefinition(tag_id),
    INDEX (tag_id, timestamp)
);

Typical Storage:
- 1000 tags × 1000 samples/hour × 24 hours/day × 365 days/year
- = 8.76 billion records per year
- ~650 GB per year (compressed)
- 5-year retention = 3.25 TB
```

**Typical Query Performance:**

```
Query: "Get temperature trend for last 24 hours"
SELECT timestamp, value FROM HistoricalData
WHERE tag_id = 42
  AND timestamp >= DATEADD(day, -1, GETDATE())
ORDER BY timestamp;

Expected execution: < 100ms
Rows returned: ~86,400 (1 sample per second)

Query: "Find all alarm events in past week"
SELECT * FROM AlarmHistory
WHERE alarm_level >= 3
  AND alarm_time >= DATEADD(day, -7, GETDATE())
ORDER BY alarm_time DESC;

Expected execution: < 50ms
Rows returned: 100-500 typical
```

---

## HMI/Visualization Design

### Dashboard Components

```
┌─────────────────────────────────────────────────────┐
│  SCADA Dashboard - Production Line Monitoring       │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ┌──────────────────────┐  ┌──────────────────────┐ │
│ │ Equipment Status     │  │ Real-time Values     │ │
│ │ ┌────────────────┐   │  │ ┌────────────────┐   │ │
│ │ │ [●] Pump 1 OK │   │  │ │ Temp: 48.5°C   │   │ │
│ │ │ [●] Motor 1 ON│   │  │ │ Press: 120 PSI │   │ │
│ │ │ [!] Valve 1 ⚠│   │  │ │ Flow: 150 L/min│   │ │
│ │ │ [X] Pump 2 ERR   │  │ │ Level: 45%     │   │ │
│ │ └────────────────┘   │  │ └────────────────┘   │ │
│ └──────────────────────┘  └──────────────────────┘ │
│                                                     │
│ ┌──────────────────────┐  ┌──────────────────────┐ │
│ │ Alarm Summary        │  │ Recent Events        │ │
│ │ Critical: 1          │  │ 14:35 Pump 1 started │ │
│ │ Major: 2             │  │ 14:30 Temp alarm clr │ │
│ │ Minor: 5             │  │ 14:25 Setpt updated  │ │
│ │ Info: 12             │  │                      │ │
│ └──────────────────────┘  └──────────────────────┘ │
│                                                     │
│ ┌──────────────────────────────────────────────┐   │
│ │ Trend Chart - Temperature Last 24 Hours       │   │
│ │ 60┤               ╱╲                          │   │
│ │ 50┤      ╱╲      ╱  ╲                         │   │
│ │ 40┤     ╱  ╲    ╱    ╲                        │   │
│ │ 30┤____╱____╲__╱______╲__                    │   │
│ │ 20└────┬────┬────┬────┬────               │   │
│ │     0h   6h  12h 18h  24h                │   │
│ └──────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Color Coding Standards

```
Color    Use Case                  Value
─────────────────────────────────────────────────
Green    Normal operation          Online, running, OK
Yellow   Caution state            Manual mode, adjusting
Orange   Warning condition        Minor alarm, degraded
Red      Critical state           Critical alarm, down
Gray     Offline/Unknown          Comms lost, initializing
Blue     Information              Selected, informational
White    Neutral/Background       UI background

Example Equipment Status:
┌─────────────┐
│ PUMP        │
│ ●●●●●       │ Green - Running at 100%
│ Status: ON  │
└─────────────┘

┌─────────────┐
│ MOTOR       │
│ ●●          │ Yellow - Running at 40%, manual control
│ Status: MAN │
└─────────────┘

┌─────────────┐
│ HEATER      │
│ ○           │ Red - Offline, critical alarm active
│ Status: ERR │
└─────────────┘
```

---

## Communication Protocols for SCADA

### Modbus TCP Configuration

**Master Server Setting:**

```
Device: Modbus TCP Slave on PLC
IP Address: 192.168.1.100
Port: 502 (standard Modbus TCP)
Unit ID: 1
Timeout: 2 seconds
Retries: 3
Scan Rate: 500ms

Register Map:
Register  Description              Data Type  R/W
────────────────────────────────────────────────
40001     Temperature Setpoint     REAL       RW
40003     Proportional Gain        REAL       RW
40005     Integral Gain            REAL       RW
40007     Output %                 REAL       RW
30001     Current Temperature      REAL       R
30003     Output Power             REAL       R
40009     Enable Control           BOOL       RW
00001     Alarm - High Temp        BOOL       R
00002     Alarm - Low Temp         BOOL       R
```

### OPC UA Server Integration

**Server Discovery:**

```
OPC UA Server URL: opc.tcp://192.168.1.50:4840/SCADA/Server

Root Node Structure:
Root
├── Namespaces (0 = OPC standard, 2 = Application-specific)
│
├── Objects
│   ├── Server (Read-only server info)
│   │   ├── ServerStatus
│   │   └── ServiceLevel
│   │
│   ├── Application
│   │   ├── ProductionLine1
│   │   │   ├── Pump1
│   │   │   │   ├── Running (Variable)
│   │   │   │   ├── Speed (Variable)
│   │   │   │   └── StartPump (Method)
│   │   │   │
│   │   │   ├── Temperature
│   │   │   │   ├── Value
│   │   │   │   ├── Alarm
│   │   │   │   └── Setpoint
│   │   │   │
│   │   │   └── Report (Method)
│   │   │
│   │   └── ProductionLine2
│   │       ├── [Similar structure]
│   │
│   └── Settings
│       ├── Historian
│       ├── Alarms
│       └── Security

(* Subscription example *)
Subscribe to: ProductionLine1.Temperature.Value
Update rate: 100ms
Deadband: 0.1°C
```

**OPC UA Subscription Handling:**

```
Server creates subscription for client
├─ Publish Interval: 100ms (server sends updates every 100ms)
├─ Lifetime: 30 seconds (client must refresh within 30s)
├─ Keep Alive: Every 5 messages
│
├─ Monitored Items:
│   ├─ Temperature (deadband 0.1°C)
│   ├─ Pressure (deadband 1 PSI)
│   ├─ Flow (deadband 5 L/min)
│   └─ Status (every change)
│
└─ Notifications sent to client when:
    - Value exceeds deadband
    - Status changes
    - Keep-alive interval reached
```

---

## Security Architecture

### ISA-62443 Security Levels

**Level 0 (Default):**
```
- No security measures
- All users same privileges
- No encryption
(Not acceptable for modern systems)
```

**Level 1 (Foundational):**
```
Access Control:
├─ Default credentials disabled
├─ Password policy enforced
│  └─ Minimum 12 characters
│  └─ Complexity required (upper, lower, digit, special)
│  └─ Change every 90 days
├─ Role-based access control (RBAC)
└─ Audit logging enabled

Data Protection:
├─ Backup/restore procedures
├─ Database encryption at rest
└─ Log protection (tamper-evident)
```

**Level 2 (Provisioned):**
```
Network Security:
├─ Firewall rules
│  └─ Explicit allow (default deny)
│  └─ Stateful inspection
├─ Network segmentation
│  └─ OT network isolated from IT
│  └─ DMZ between firewall and SCADA
├─ Intrusion detection
└─ VPN for remote access

System Hardening:
├─ Disable unnecessary services
├─ Apply security patches monthly
├─ Remove default accounts
└─ Configure secure protocols (TLS 1.2+)
```

**Level 3 (Managed):**
```
Monitoring & Response:
├─ SIEM (Security Information & Event Mgmt)
│  └─ Centralized log collection
│  └─ Real-time threat detection
│  └─ Incident response playbooks
├─ Vulnerability scanning
│  └─ Weekly network scans
│  └─ Monthly web application scans
├─ Penetration testing
│  └─ Annual by external firm
└─ Security awareness training (annual)

Compliance:
├─ Regular security audits
├─ Documented security policy
├─ Change management process
└─ Disaster recovery testing
```

**Level 4 (Dynamic):**
```
Advanced Threat Protection:
├─ Behavioral analysis
│  └─ ML models for anomaly detection
│  └─ Real-time threat hunting
├─ Automated response
│  └─ Quarantine infected systems
│  └─ Disable compromised accounts
│  └─ Alert SOC immediately
├─ Zero-trust architecture
│  └─ Every access verified
│  └─ Micro-segmentation
└─ Continuous monitoring
    └─ 24/7 security operations center
    └─ EDR (Endpoint Detection & Response)
```

### Network Topology (ISA-62443)

```
Internet
    ↓ (Protected link)
┌─────────────────┐
│ Corporate       │
│ Firewall        │
└────────┬────────┘
         ↓
┌─────────────────┐
│ IT Network      │
│ (ERP, Email)    │
│ 10.0.0.0/8      │
└────────┬────────┘
         ↓
┌─────────────────┐
│ DMZ             │
│ (Historian)     │
│ 10.1.0.0/24     │
│ ONE-WAY dataflow│
└────────┬────────┘
         ↓
┌─────────────────┐
│ OT Network      │
│ (SCADA/PLC)     │
│ 192.168.1.0/24  │
│ ISOLATED        │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Field Devices   │
│ (I/O, Motors)   │
└─────────────────┘

Firewall Rules:
- IT → DMZ: Allowed (HTTPS, SSH)
- DMZ → OT: Allowed (Modbus, OPC UA)
- OT → DMZ: BLOCKED (except historian sync)
- External → OT: BLOCKED
- OT → External: BLOCKED
```

---

## Redundancy and High Availability

### Active-Active Configuration

```
Load Balancer (Heartbeat monitoring)
    ↓
    ├── SCADA Server A (192.168.1.10)
    │   ├─ Processing: 50% of load
    │   ├─ Memory: Cache synchronized
    │   └─ Real-time sync: < 100ms
    │
    └── SCADA Server B (192.168.1.11)
        ├─ Processing: 50% of load
        ├─ Memory: Cache synchronized
        └─ Real-time sync: < 100ms
            ↓
        Shared Database Server (RAID 6)
        ├─ Automatic failover
        ├─ Replication lag: < 10ms
        └─ RPO (Recovery Point Objective): 0 seconds

Failure Scenario:
If Server A fails → Server B automatically takes 100% load
Client reconnects automatically (transparent failover)
Downtime: < 1 second
```

### Active-Standby Configuration

```
SCADA Server A (Active)      SCADA Server B (Standby)
├─ Processing all traffic    ├─ Monitoring heartbeat
├─ Writing database          ├─ Mirroring database (async)
├─ Generating reports        └─ Idle, not processing
└─ Monitoring controller

Heartbeat: Every 1 second
Failover threshold: 3 missed heartbeats (3 seconds)

Failure Scenario:
Server A fails
→ Heartbeat missing for 3 seconds
→ Server B detects failure
→ Server B transitions to ACTIVE
→ Database caught up (may be 10-60 seconds behind)
→ Clients reconnect

Total Downtime: 3-65 seconds
RPO (Recovery Point Objective): 60 seconds
RTO (Recovery Time Objective): 65 seconds
```

---

## Performance Metrics

### Key Performance Indicators (KPIs)

```
Metric              Target      Measurement
────────────────────────────────────────────
System Uptime       99.5%       Time online / Total time
Data Freshness      < 5 sec     Time from PLC to historian
Scan Cycle Time     < 500ms     Polling → storage cycle
Response Time       < 2 sec     Operator command → execution
Alarm Recognition   < 10 sec    Event → Alarm displayed
Query Performance   < 2 sec     Historical trend request
Database Size       Planned     Growth rate assessment
CPU Utilization     < 60%       Headroom for growth
Memory Utilization  < 70%       Swap usage avoided
Disk I/O            < 60%       No bottlenecks
Network Bandwidth   < 50%       Headroom for redundancy
```

### Capacity Planning

**1-Year Growth Projection:**

```
Current State:
- 500 tags scanned at 1 Hz
- Data retention: 3 years
- Database size: 1.2 TB
- Daily historian growth: ~3.5 GB
- CPU utilization: 35%

Projected Growth (10% annual):
- Year 1: 550 tags, 1.4 TB (CPU: 39%)
- Year 2: 605 tags, 1.7 TB (CPU: 43%)
- Year 3: 665 tags, 2.0 TB (CPU: 47%)
- Year 4: 732 tags, 2.3 TB (CPU: 52%)
- Year 5: 805 tags, 2.7 TB (CPU: 57%)

Recommendation:
- Monitor CPU, disk growth quarterly
- Plan infrastructure refresh Year 3-4
- Consider distributed architecture Year 5
```

---

## Document Version: 2.0
**Last Updated:** January 2024
**Reference:** ISA-95, IEC 62541 (OPC UA), IEC 61158 (Modbus)
