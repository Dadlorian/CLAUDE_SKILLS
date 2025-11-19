# Industrial Protocols Reference Guide

## Protocol Comparison Matrix

| Feature | Modbus TCP | OPC UA | PROFINET | EtherCAT | DeviceNet |
|---------|-----------|--------|----------|----------|-----------|
| Media | Ethernet | Ethernet | Ethernet | Ethernet | Coax/Ethernet |
| Determinism | Non-real-time | Real-time capable | Real-time (IRT) | Ultra real-time | Deterministic |
| Cycle Time | 10-100ms | 10-100ms | <10ms | <1ms | 5-100ms |
| Devices/Network | 200+ | Unlimited | 500+ | 65,535 | 64 |
| Bandwidth | Moderate | Moderate | High | Very High | Medium |
| Security | Optional | Built-in | Optional | Optional | Proprietary |
| Topology | Star, Multi-drop | Star | Star, Ring | Line | Multi-drop |
| Range | ~100m | ~100m | ~100m | ~100m | ~250m |
| Cost/Device | Low | Medium | Medium | Medium-High | Medium |
| Primary Use | Remote I/O | Enterprise integration | Plant floor | High-speed machines | Legacy systems |

---

## Modbus Protocol Family

### Modbus TCP/IP Overview

**Protocol Characteristics:**
```
Open Standard:        YES - No licensing fees
Vendor-Independent:   YES - Widely supported
Platform:            Linux, Windows, Embedded
Determinism:         NO - Best-effort delivery
Complexity:          LOW - Simple to implement
Security:            Optional (no built-in encryption)
Adoption:            70% of industrial devices
```

### Modbus TCP Message Structure

**Raw Message Format:**

```
┌────────┬───────┬──────────┬──────────┬────────┐
│ MBAP   │ Func  │ Starting │ Quantity │ CRC    │
│Header  │ Code  │ Address  │ Of Items │        │
│(12 B)  │(1 B)  │ (2 B)    │ (2 B)    │ (2 B)  │
└────────┴───────┴──────────┴──────────┴────────┘

MBAP Header (Modbus Application Protocol):
Byte 0-1: Transaction ID     (0x0001-0xFFFF)
Byte 2-3: Protocol ID        (0x0000 = Modbus)
Byte 4-5: Length             (Number of following bytes)
Byte 6:   Unit ID            (Slave address 0-247)
```

**Example: Read 10 Temperature Registers**

```
Request:
Hex: 00 01 00 00 00 06 01 03 75 30 00 0A
     └─────────────────────────────────────┘
     Transaction ID = 0x0001
     Protocol ID = 0x0000
     Length = 6 bytes (Function code + Address + Count)
     Unit ID = 0x01 (Slave 1)
     Function = 0x03 (Read Holding Registers)
     Starting Address = 0x7530 (Register 30000)
     Quantity = 0x000A (10 registers)

Response (10 registers × 2 bytes each):
Hex: 00 01 00 00 00 15 01 03 14 [20 bytes of data] FF FF
     Transaction ID = 0x0001 (matches request)
     Length = 21 bytes
     Byte count = 0x14 (20 bytes of temperature data)
     Data: 10 REAL values (0x0CA4 = 32.2°C, etc.)
```

### Modbus RTU vs TCP

```
Modbus RTU (Serial):
├─ Media: RS-485, RS-232
├─ Baud rate: 9600-115200
├─ CRC-16: Yes (error checking)
├─ Overhead: Low (1 byte slave ID + CRC)
├─ Distance: ~1200m (RS-485)
└─ Latency: 20-100ms typical

Modbus TCP (Ethernet):
├─ Media: 10/100/1000 Mbps Ethernet
├─ Baud rate: N/A (packet-based)
├─ TCP checksum: Yes (built-in)
├─ Overhead: Higher (12-byte MBAP header)
├─ Distance: ~100m per segment (with repeaters)
└─ Latency: 1-10ms typical

Choice Criteria:
- < 20 devices, serial, < 100m → Modbus RTU
- > 20 devices, any topology, any distance → Modbus TCP
- Factory automation, time-critical → Consider PROFINET/EtherCAT
```

### Common Modbus Function Codes

**FC 01: Read Coils**
```
Request:  Slave_ID | 0x01 | Starting_Address(2B) | Qty_Coils(2B) | CRC
Response: Slave_ID | 0x01 | Byte_Count | Coil_Values | CRC

Example: Read coils 100-107 (8 coils = 1 byte)
Request:  01 | 01 | 00 64 | 00 08 | CRC
Response: 01 | 01 | 01 | 0xA5 | CRC
          (Coils 100-107 = binary 10100101)
```

**FC 03: Read Holding Registers**
```
Request:  Slave_ID | 0x03 | Starting_Address(2B) | Qty_Registers(2B) | CRC
Response: Slave_ID | 0x03 | Byte_Count | Register_Values | CRC

Example: Read registers 40001-40005 (5 registers = 10 bytes)
Request:  01 | 03 | 9C 40 | 00 05 | CRC
Response: 01 | 03 | 0A | [10 bytes of data] | CRC
```

**FC 05: Write Single Coil**
```
Request:  Slave_ID | 0x05 | Coil_Address(2B) | Value(2B) | CRC
Response: Echo request (if successful)

Example: Set coil 173 to ON
Request:  01 | 05 | 00 AD | FF 00 | CRC  (0xFF00 = ON)
Response: 01 | 05 | 00 AD | FF 00 | CRC
```

**FC 06: Write Single Register**
```
Request:  Slave_ID | 0x06 | Register_Address(2B) | Value(2B) | CRC
Response: Echo request (if successful)

Example: Set register 40001 to 25.5°C (2550 in 0.01°C units)
Request:  01 | 06 | 9C 40 | 09 F6 | CRC  (0x09F6 = 2550)
Response: 01 | 06 | 9C 40 | 09 F6 | CRC
```

**FC 16: Write Multiple Registers**
```
Request:  Slave_ID | 0x10 | Starting_Address(2B) | Qty(2B) |
          Byte_Count | Register_Values | CRC

Example: Write 3 registers starting at 40001
Request:  01 | 10 | 9C 40 | 00 03 | 06 |
          00 32 | 00 64 | 00 C8 | CRC

Sets:
- Register 40001 = 0x0032 (50)
- Register 40002 = 0x0064 (100)
- Register 40003 = 0x00C8 (200)
```

---

## OPC UA (IEC 62541)

### OPC UA Architecture

**Three-Layer Model:**

```
┌───────────────────────────────────────┐
│ Application Layer                     │
│ - Business logic                      │
│ - Client applications                 │
│ - Analysis engines                    │
└───────────────┬───────────────────────┘
                │
┌───────────────v───────────────────────┐
│ OPC UA Service Layer                  │
│ ┌─────────────────────────────────┐   │
│ │ Services:                       │   │
│ │ - Browse                        │   │
│ │ - Read/Write                    │   │
│ │ - Subscribe                     │   │
│ │ - CreateSession                 │   │
│ │ - Call Methods                  │   │
│ └─────────────────────────────────┘   │
└───────────────┬───────────────────────┘
                │
┌───────────────v───────────────────────┐
│ OPC UA Encoding & Transport Layer     │
│ ┌─────────────┬─────────────────────┐ │
│ │ Binary      │ XML/JSON            │ │
│ │ Encoding    │ Encoding            │ │
│ └────────┬────┴────────┬────────────┘ │
│          │             │              │
│      ┌───v─────┐  ┌────v─────┐       │
│      │  TCP    │  │   HTTP   │       │
│      │ Binding │  │  Binding  │       │
│      └─────────┘  └──────────┘       │
└───────────────────────────────────────┘
```

### OPC UA Information Model

**Node Class Examples:**

```
Object (Real-world entity)
├─ Properties (Characteristics)
│  ├─ Name
│  ├─ NodeVersion
│  └─ NodeClass
│
├─ Variables (Data values)
│  ├─ Temperature (REAL)
│  ├─ Pressure (REAL)
│  └─ Status (Enumeration)
│
└─ Methods (Callable functions)
   ├─ StartProcess()
   ├─ StopProcess()
   └─ GetHistoricalData()

ObjectType (Template)
├─ MotorType
│  ├─ Speed (Variable)
│  ├─ Current (Variable)
│  ├─ Status (Variable)
│  └─ Start() (Method)
│
└─ PumpType
   ├─ FlowRate (Variable)
   ├─ Pressure (Variable)
   ├─ Status (Variable)
   └─ StartPump() (Method)

DataType (Data structure)
├─ SensorReading
│  ├─ Timestamp (DateTime)
│  ├─ Value (Float)
│  └─ Quality (Byte)
│
└─ MotorStatus
   ├─ Running (Boolean)
   ├─ Speed (Int32)
   └─ Temperature (Float)
```

### OPC UA Security Mechanisms

**Authentication Methods:**

```
1. Username/Password
   ├─ Simple but effective
   ├─ Password sent over encrypted channel
   └─ Not suitable for machine-to-machine

2. X.509 Certificates
   ├─ Mutual authentication
   ├─ Strong encryption
   ├─ Industry standard
   └─ Requires PKI infrastructure

3. Windows Integrated (Kerberos)
   ├─ Enterprise environment
   ├─ Single sign-on
   └─ No shared credentials
```

**Encryption & Signing:**

```
Transport Security:
├─ None: TCP connection (no security)
├─ Sign: Messages signed, not encrypted
│  └─ Verifies integrity and authenticity
├─ Sign & Encrypt: Full protection
│  └─ AES-256 encryption typical
└─ Available algorithms:
   ├─ None (empty)
   ├─ Basic128Rsa15
   ├─ Basic192Rsa15
   ├─ Basic256
   ├─ Basic256Sha256
   └─ Aes128-Sha256-RsaOaep (recommended)
```

### OPC UA Subscription Model

**Publisher-Subscriber Pattern:**

```
Client 1 ─┐
Client 2 ├─ Subscribe to Variables ─ Server ─ PLC/Equipment
Client 3 ┘
              │
              ├─ Monitored Items
              │  ├─ Temperature (deadband 0.5°C)
              │  ├─ Pressure (deadband 5 PSI)
              │  └─ Status (every change)
              │
              ├─ Publish Interval
              │  └─ 100ms (server batches updates)
              │
              └─ Keep Alive
                 └─ Every 10 publish intervals

Notification sent when:
- Value exceeds deadband
- Status changes
- Keep-alive interval expires
- Client requests immediate update
```

---

## PROFIBUS/PROFINET

### PROFIBUS Overview

**PROFIBUS Variants:**

```
PROFIBUS DP (Decentralized Periphery)
├─ Primary: Discrete manufacturing
├─ Distance: Up to 1.2 km (with repeaters)
├─ Speed: 9.6 kbps to 12 Mbps
├─ Devices: I/O modules, drives, sensors
├─ Topology: Linear (daisy-chain)
└─ Latency: 1-10ms typical

PROFIBUS PA (Process Automation)
├─ Primary: Continuous processes (pharma, chem)
├─ Distance: Up to 1.9 km
├─ Speed: 31.25 kbps (fixed)
├─ Devices: Smart instruments, valves
├─ Features: Intrinsically safe (Ex-certified)
└─ Latency: 10-100ms typical

PROFIBUS FMS (Fieldbuses Message Specification)
├─ Primary: Complex communication
├─ Complex message sequences
├─ Rarely used in modern systems
└─ Being replaced by PROFINET
```

### PROFINET Overview

**PROFINET Real-Time Capabilities:**

```
Real-Time Class A (RT)
├─ Cycle time: 10-100ms
├─ Jitter: < 1%
├─ Suitable for: Standard control
├─ Uses: Standard Ethernet

Real-Time Class B (IRT - Isochronous Real-Time)
├─ Cycle time: 1-10ms
├─ Jitter: < 1μs
├─ Suitable for: High-speed machines, synchronization
├─ Uses: Dedicated real-time switches, cables
└─ Requires: Special network infrastructure

Real-Time Class C (NRT)
├─ Cycle time: 100ms - seconds
├─ Suitable for: Web services, IT integration
└─ Uses: Standard Ethernet, no guarantees
```

**PROFINET Topology:**

```
Network Structure:

Star Topology (Most Common):
        ┌─────────────┐
        │ Managed     │
        │ Switch      │
        └────────┬────┘
                 │
        ┌────────┼────────┬────────┬───────┐
        │        │        │        │       │
        v        v        v        v       v
      PLC1    PLC2    Drive    Valve   Sensor


Ring Topology:
    ┌──────────────────────────┐
    │                          │
    v                          │
  PLC1 ─── Switch ─── Drive   │
    │        │         │       │
    └────────┼─────────┼───────┘
             │         │
           Valve    Sensor

Benefits: High availability, auto-reroute on cable break
```

### PROFINET Addressing

**Device Identification:**

```
MAC Address: 00:20:25:XX:XX:XX (Siemens PROFINET)
IP Address: 192.168.0.X (typical default)
Device Name: "SiemensS71200-1234" (DNS resolvable)

Discovery & Configuration:
├─ PROFINET Topology Discovery Protocol
├─ Automatic IP assignment available
├─ DCP (Device Configuration Protocol) for setup
└─ No additional naming service needed (unlike OPC UA)
```

---

## EtherCAT (Real-time Ethernet)

### EtherCAT Overview

**Ultra-Deterministic Real-Time:**

```
Cycle Time:     100μs - 65.5ms (configurable)
Jitter:         < 100ns (sub-microsecond precision)
Latency:        <1μs (ideal for motion control)
Scalability:    65,535 slaves per line
Bandwidth:      1 Gbit/s (all slaves share)
Topology:       Point-to-point line (no switches needed)
Media:          Single twisted pair for EtherCAT (optional dual)
Distance:       100m per segment, unlimited with repeaters

Primary Uses:
├─ Machine tool multi-axis coordination
├─ Assembly line synchronized motion
├─ High-speed packaging equipment
├─ Synchronized vision systems
└─ Industry 4.0 edge computing
```

### EtherCAT Master-Slave Architecture

**Distributed Processing:**

```
Master (PLC)
    ↓
Send telegram (command frame)
    ↓
┌────────────────────────────────┐
│ EtherCAT Slave 1 (Motor Drive)  │
│ - Read input data              │
│ - Process command              │
│ - Update output data           │
│ - Forward to next slave        │
└────────────┬───────────────────┘
             ↓
┌────────────────────────────────┐
│ EtherCAT Slave 2 (Encoder)      │
│ - Read input data              │
│ - Insert position feedback     │
│ - Forward to next slave        │
└────────────┬───────────────────┘
             ↓
┌────────────────────────────────┐
│ EtherCAT Slave 3 (Digital I/O)  │
│ - Read input data              │
│ - Update outputs               │
│ - Return to master             │
└────────────┬───────────────────┘
             ↓
Master receives full telegram
    (Total time: < 1ms for 100+ nodes)

Key Advantage:
All slaves process in parallel during one cycle
vs. Modbus/Profinet which address one device at a time
```

### EtherCAT CANopen over EtherCAT (CoE)

**Leverages CANopen device profiles:**

```
Motor Drive Profile (DS402):
├─ 0x6040: Controlword
│  ├─ Bit 0: Switch On
│  ├─ Bit 1: Enable Voltage
│  ├─ Bit 2: Quick Stop
│  ├─ Bit 3: Enable Operation
│  └─ Bits 4-6: Operation Mode
│
├─ 0x6041: Status word (feedback)
│  ├─ Bit 0: Ready to Switch On
│  ├─ Bit 1: Switched On
│  ├─ Bit 2: Operation Enabled
│  ├─ Bit 3: Fault
│  └─ Bits 4-6: Current state
│
├─ 0x607A: Target Position
├─ 0x607B: Position Range Limit
├─ 0x6080: Maximum Motor Speed
└─ 0x6083: Profile Acceleration

Drive State Machine:
NOT_READY → READY → SWITCHED_ON → OPERATION_ENABLED
```

---

## Industrial Ethernet Protocols Comparison

### Determinism and Real-Time Guarantees

```
Protocol        Mechanism                  Cycle Time   Jitter
──────────────────────────────────────────────────────────────
Modbus TCP      Best effort (TCP)         10-100ms     < 10%
OPC UA          Best effort (TCP)         10-100ms     < 10%
PROFINET RT     Standard Ethernet         10-100ms     < 1%
PROFINET IRT    Dedicated time slots      1-10ms       < 1μs
EtherCAT        Temporal slotting         100μs-65ms   < 100ns

Guarantee Mechanism:
- Modbus/OPC UA: None (relies on TCP/IP stack)
- PROFINET RT: Managed switches, priority queues
- PROFINET IRT: Time-slotted scheduling, real-time switches
- EtherCAT: Master controls all timing, no collisions
```

### Cable & Connector Standards

```
Standard Ethernet (Category 5e/6):
├─ 10/100/1000 Mbps
├─ Uses: OPC UA, Modbus TCP, PROFINET
├─ Connector: RJ-45
└─ Distance: 100m per segment

IEC 61076-2-109 (M12 X-coded):
├─ Sturdier than RJ-45
├─ Uses: PROFINET, EtherCAT
├─ Connector: M12 circular
└─ Distance: 100-400m depending on shielding

Real-time Ethernet (IRT):
├─ Special cabling required
├─ Dual-fiber or redundant pairs
├─ Uses: PROFINET IRT
├─ Distance: 100m per segment
└─ Requires: Real-time capable switches

Power over Ethernet (PoE):
├─ Up to 90W (IEEE 802.3bt)
├─ Uses: IIoT devices, edge cameras
├─ Connector: Standard RJ-45
└─ Reduces wiring complexity
```

---

## Device Profile Standards

### CANopen (DS-301/DS-401/DS-402)

**Used by:** EtherCAT CoE, PROFIBUS, CANbus systems

```
Device Object Dictionary (OD):

0x0000-0x00FF   Device Information
0x1000-0x1FFF   Device & Communication Parameters
0x2000-0x2FFF   Manufacturer Specific
0x3000-0x3FFF   Device Specific
0x4000-0x4FFF   Manufacturer Specific
0x5000-0x5FFF   Device Specific
0x6000-0x6FFF   Standardized Profiles
0x7000-0x7FFF   Manufacturer Specific
0x8000-0xFFFF   Device Specific

Common Indices:
0x1000   Device Type
0x1001   Error Register
0x1008   Device Name
0x1009   Hardware Version
0x100A   Software Version
0x1018   Identity Object
0x1F80   NMT Master Time Base
0x2000   Comm Error Field
```

---

## Protocol Selection Guide

**Factory Automation (Discrete Manufacturing):**
```
Primary choice: PROFINET
- Ubiquitous in automotive/electronics
- Good real-time performance
- Mature ecosystem

Secondary choice: EtherCAT (if motion control synchronization needed)
- High-speed multi-axis coordination
- Better determinism than PROFINET
```

**Process Industry (Continuous Manufacturing):**
```
Primary choice: PROFIBUS PA or PROFINET
- PA for legacy systems, safety-critical
- PROFINET for greenfield projects

Secondary choice: Modbus TCP (if simplicity prioritized)
- Many process devices support it
- Legacy system integration
```

**Enterprise Integration (IT/OT Bridge):**
```
Primary choice: OPC UA
- Platform-agnostic
- Strong security
- Semantic information preservation

Supporting protocol: Modbus TCP (for equipment connectivity)
```

**High-Speed Motion Control:**
```
Primary choice: EtherCAT
- Sub-microsecond timing
- Unlimited scaling
- Cost-effective for large device counts

Alternative: PROFINET IRT (if EtherCAT ecosystem unavailable)
```

---

## Document Version: 2.0
**Last Updated:** January 2024
**Reference Standards:** IEC 61158, IEC 62541, DIN EN 61784
