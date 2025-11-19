# ISA-95 Enterprise Integration Reference

## ISA-95 Standard Overview

ANSI/ISA-95.00.01-2010 "Enterprise-Control Systems Integration" defines the standard for integrating enterprise systems (ERP) with manufacturing control systems (PLC, SCADA, DCS).

**Official Title**: "Batch Control Standard"
**Effective Date**: 2010
**Latest Amendment**: 2013
**Development Organization**: International Society of Automation (ISA)

## Purpose and Scope

**Purpose**: Create a unified model for manufacturing system architecture and data flow.

**Scope**:
- Functional hierarchy of manufacturing systems (Levels 0-5)
- Data models for manufacturing information
- Business-to-operations (B2O) integration patterns
- Equipment models and hierarchies
- Product structure representation
- Quality and compliance tracking

**Benefits of ISA-95 Compliance**:
- Standardized data definitions across systems
- Reduced integration complexity
- Easier system migration and upgrades
- Vendor independence
- Regulatory compliance alignment
- Improved interoperability

## Five-Level Functional Hierarchy

### Level 5: Enterprise Business Planning & Logistics

**Systems**:
- ERP systems (SAP S/4HANA, Oracle EBS, Microsoft Dynamics)
- Business intelligence and analytics
- Supply chain planning
- Financial systems
- Customer relationship management (CRM)

**Functions**:
- Strategic planning
- Sales and order management
- Demand forecasting
- Financial planning and budgeting
- Procurement planning
- Logistics planning

**Time Horizon**: Days to months

**Data**:
- Master sales orders
- Demand forecasts
- Financial budgets
- Supplier and customer master data
- Long-term capacity plans

**Interfaces**:
- To Level 4: Sends production orders, receives completion notices
- External: Customers, suppliers, financial institutions

### Level 4: Plant Site / Area Production Scheduling & Execution Control

**Systems**:
- Manufacturing Execution Systems (MES)
- Advanced Planning & Scheduling (APS)
- Quality Management Systems (QMS)
- Production control systems

**Functions**:
- Demand scheduling
- Production order creation and sequencing
- Resource scheduling
- Production control and execution tracking
- Quality planning and execution
- Genealogy and traceability

**Time Horizon**: Hours to shifts

**Data**:
- Production orders
- Resource schedules
- Work orders
- Execution status
- Quality results
- Genealogy records

**Interfaces**:
- From Level 5: Production orders, product specifications
- To Level 3: Detailed work orders, equipment commands
- Bi-directional: Status updates, compliance reporting

### Level 3: Supervisory Control (SCADA/DCS)

**Systems**:
- SCADA (Supervisory Control and Data Acquisition)
- Distributed Control Systems (DCS)
- Process control systems
- Batch management systems (ISA-88 compatible)
- Local industrial networks

**Functions**:
- Production recipe execution
- Sequence control
- Setpoint management
- Batch process control
- Data logging and trending
- Local alarm management

**Time Horizon**: Minutes to seconds

**Data**:
- Batch recipes and procedures
- Equipment setpoints and parameters
- Equipment status
- Process measurements
- Alarms and events
- Historical data

**Interfaces**:
- From Level 4: Work orders, recipes, parameters
- To Level 2: Equipment commands, monitoring signals
- Bi-directional: Real-time status, data collection

### Level 2: Automation & Control (PLCs, PACs, Smart Devices)

**Systems**:
- Programmable Logic Controllers (PLCs)
- Programmable Automation Controllers (PACs)
- Intelligent field devices
- Safety controllers
- Vision systems
- Motion controllers

**Functions**:
- Hardware-level control logic
- Real-time command execution
- Sensor data acquisition
- Equipment sequencing
- Safety enforcement
- Local interlocks

**Time Horizon**: Milliseconds to seconds

**Data**:
- Digital and analog signals
- Equipment states
- Sensor readings
- Actuator commands
- Diagnostics and alarms

**Interfaces**:
- From Level 3: Commands and setpoints
- To Level 1: Control signals
- Bi-directional: Equipment status, diagnostic data

### Level 1: Equipment & Machines

**Systems**:
- Production equipment (machines, reactors, conveyors)
- Sensors and transmitters
- Actuators (motors, valves, solenoids)
- Weighing and measurement devices
- Packaging equipment

**Functions**:
- Physical production
- Material transformation
- Part movement
- Environmental sensing

**Time Horizon**: Microseconds to milliseconds

**Data**:
- Physical movements
- Material flow
- Energy consumption
- Environmental conditions

**Interfaces**:
- From Level 2: Control signals
- Bi-directional: Sensor data, equipment feedback

### Level 0: Raw Materials and Finished Products

**Physical elements**:
- Raw materials
- Work-in-progress (WIP)
- Finished products
- Consumables and utilities

## ISA-95 Data Models

### Product Definition

**Hierarchical Structure**:
```
Product Family
    ├─ Product Type
    │   ├─ Product Definition
    │   │   ├─ Product Segment (version/variant)
    │   │   │   └─ Product Component (BOM item)
    │   │   │       ├─ Component Quantity
    │   │   │       ├─ Component Unit
    │   │   │       └─ Component Specification
```

**Example**:
```
Widget Family
    ├─ Standard Widget Type
    │   ├─ Widget Model A (Definition)
    │   │   ├─ Version 1.0 (Segment)
    │   │   │   ├─ Steel Part A (100 units/batch)
    │   │   │   ├─ Plastic Handle (100 units/batch)
    │   │   │   ├─ Fasteners (500 units/batch)
    │   │   │   └─ Paint (5 liters/batch)
    │   │   └─ Version 1.1 (Segment - improved handle)
    │   │       └─ [Modified BOM]
    │   └─ Widget Model B (Definition)
    │       └─ [Different specification]
```

**Data Elements**:
- Product ID and description
- Product family classification
- Specification version
- Creation and effective dates
- Responsible organization
- Quality specifications
- Storage requirements
- Shelf life

### Process Segment Model

**Hierarchical Structure**:
```
Process Segment Definition
    ├─ Operation Definition
    │   ├─ Phase Definition
    │   │   ├─ Action Description
    │   │   └─ Parameter Specification
    │   ├─ Skill Definition
    │   └─ Equipment Requirement
    ├─ Transition Definition
    └─ Evaluation Criteria
```

**Example**:
```
Batch Process: Widget Mixing
    ├─ Operation 1: Material Loading
    │   ├─ Phase 1.1: Load Material A
    │   │   └─ Quantity: 50 kg
    │   │   └─ Skill: Operator qualified for mixers
    │   ├─ Phase 1.2: Load Material B
    │   │   └─ Quantity: 30 kg
    │   └─ Phase 1.3: Load Additive
    │       └─ Quantity: 5 kg
    ├─ Operation 2: Mixing Execution
    │   ├─ Phase 2.1: Start Mixer
    │   │   └─ Speed: 800 RPM
    │   ├─ Phase 2.2: Temperature Control
    │   │   └─ Target: 65°C ± 2°C
    │   │   └─ Duration: 10 minutes
    │   └─ Phase 2.3: Stop Mixer
    ├─ Operation 3: Quality Verification
    │   ├─ Phase 3.1: Homogeneity Check
    │   │   └─ Method: Visual inspection
    │   └─ Phase 3.2: Density Test
    │       └─ Spec: 1.2 ± 0.05 g/ml
    └─ Transition: To Discharge if all operations pass
```

**Data Elements**:
- Process segment ID
- Product produced
- Equipment used
- Operator skills required
- Phase sequence
- Decision criteria
- Exception handling

### Equipment Hierarchy

**ISA-95 Equipment Model**:
```
Enterprise
    ├─ Site
    │   ├─ Area
    │   │   ├─ Production Line
    │   │   │   ├─ Work Cell
    │   │   │   │   ├─ Equipment Module (logical grouping)
    │   │   │   │   │   └─ Equipment Unit (physical device)
    │   │   │   │   └─ Control Module
    │   │   │   └─ Equipment Unit (stand-alone)
    │   │   └─ Storage Area
    │   │       └─ Inventory Location
    │   └─ Support Area
    │       └─ Lab / Quality Center
    └─ Remote Site
```

**Equipment Data Elements**:
- Equipment ID and serial number
- Equipment type and manufacturer
- Location (hierarchical path)
- Capabilities and capacity
- Operating parameters
- Maintenance schedule
- Safety certifications
- Environmental conditions

### Resource Allocation

**Resource Types in ISA-95**:
1. **Equipment Resources**
   - Production equipment (machines, reactors)
   - Support equipment (scales, test equipment)
   - Transportation equipment (conveyors, lifts)

2. **Personnel Resources**
   - Operator qualifications and certifications
   - Supervisor availability
   - Quality inspector skills
   - Maintenance technician specialization

3. **Physical Resources**
   - Raw materials and components
   - Consumables (filters, spark plugs, etc.)
   - Utilities (electricity, water, compressed air)
   - Storage locations

4. **Logical Resources**
   - Time slots and shifts
   - Software licenses
   - Approval authorities

## MES Integration with ISA-95

### Data Flow: Level 5 to Level 3

```
Level 5: ERP System
    ├─ Sends to MES (Level 4):
    │   ├─ Production orders
    │   ├─ Product specifications
    │   ├─ Material availability
    │   ├─ Resource constraints
    │   ├─ Quality requirements
    │   └─ Delivery deadlines
    │
    └─ Receives from MES:
        ├─ Schedule feasibility (can this be done?)
        ├─ Resource availability (when available?)
        ├─ Completion forecasts
        ├─ Actual production quantities
        ├─ Quality metrics
        └─ Genealogy summary data

Level 4: MES
    ├─ Sends to SCADA (Level 3):
    │   ├─ Work orders
    │   ├─ Batch recipes
    │   ├─ Equipment allocation
    │   ├─ Quality checkpoints
    │   ├─ Parameter setpoints
    │   └─ Resource assignments
    │
    └─ Receives from SCADA:
        ├─ Equipment status
        ├─ Production progress
        ├─ Quality results
        ├─ Equipment alarms
        ├─ Data trends
        └─ Completeness verification
```

### Information Exchange Patterns

**Synchronous Exchange** (Request-Response):
```
MES Requests Equipment Status
    → "What is the current temperature in Reactor 1?"
    ← SCADA Returns: 72.5°C at timestamp

MES Sends Command
    → "Start Mixer A at 500 RPM"
    ← SCADA Confirms: "Mixer started, RPM increasing"

Benefits:
- Real-time verification
- Immediate response

Drawbacks:
- Tight coupling
- Timeout risk
- Network latency impact
```

**Asynchronous Exchange** (Event-Driven):
```
SCADA Detects High Temperature
    → Publishes: "Event: HighTemp, Reactor1, 85°C, 14:35:22"

MES Subscribes: "Temperature alerts"
    ← Receives: High temp event
    → Evaluates: Is this critical?
    → Takes action: Hold batch, alert supervisor

Benefits:
- Loose coupling
- Scalable to many sources
- Better resilience

Drawbacks:
- Eventual consistency
- Potential data loss if not carefully designed
```

**Batch Exchange** (Scheduled):
```
Every 15 minutes:
SCADA Exports:
    - Equipment status snapshot
    - Production counts (good, defect, total)
    - Energy consumption
    - Quality results from previous 15 minutes

MES Imports:
    - Updates WIP inventory
    - Calculates OEE
    - Triggers any scheduled reports

Appropriate for:
- Non-critical updates
- Historical data
- Legacy system integration
- High-volume data
```

### Message Content Standards

**ISA-95 Information Models**:

**Production Order Message**:
```xml
<ProductionOrder>
    <OrderID>PO-2024-001234</OrderID>
    <Product>
        <ProductID>Widget-A-001</ProductID>
        <ProductVersion>1.0</ProductVersion>
    </Product>
    <OrderQuantity>
        <Value>500</Value>
        <Unit>Units</Unit>
    </OrderQuantity>
    <ScheduledStart>2024-11-19T08:00:00Z</ScheduledStart>
    <ScheduledEnd>2024-11-19T10:00:00Z</ScheduledEnd>
    <Specification>
        <Parameter name="Color" value="Red" />
        <Parameter name="Size" value="Large" />
    </Specification>
    <MaterialList>
        <Material>
            <MaterialID>Steel-001</MaterialID>
            <LotNumber>Lot-2024-5678</LotNumber>
            <Quantity value="500" unit="Units" />
        </Material>
    </MaterialList>
</ProductionOrder>
```

**Work Order (MES to SCADA)**:
```yaml
WorkOrder:
  ID: WO-2024-001234-01
  ProductionOrder: PO-2024-001234
  Equipment: Line1-Machine1
  OperatorAssignment: jsmith
  Priority: High
  StartTime: 2024-11-19T08:00:00Z
  DueTime: 2024-11-19T10:00:00Z

  Recipe: Mixing_Process_v1.0
  Phases:
    - Phase: Material_Loading
      Equipment: Hopper1
      Parameters:
        - MaterialA: 50kg
        - MaterialB: 30kg
        - MaterialC: 5kg

    - Phase: Mixing
      Equipment: Mixer1
      Parameters:
        - Speed: 800 RPM
        - Temperature: 65°C +/- 2°C
        - Duration: 10 minutes

    - Phase: Quality_Check
      Tests:
        - Homogeneity: Visual
        - Density: 1.2 +/- 0.05 g/ml

  Genealogy:
    TrackLots: true
    TrackOperator: true
    TrackEquipmentParameters: true
```

**Production Completion Report (SCADA to MES)**:
```yaml
CompletionReport:
  WorkOrderID: WO-2024-001234-01
  Status: Success
  StartTime: 2024-11-19T08:05:00Z
  EndTime: 2024-11-19T09:55:00Z

  Production:
    PlannedQuantity: 500 units
    ActualQuantity: 495 units
    ScrappedQuantity: 5 units
    ReworkQuantity: 0 units

  Materials:
    - MaterialA: 50.2 kg (spec: 50 kg)
    - MaterialB: 29.8 kg (spec: 30 kg)
    - MaterialC: 5.1 kg (spec: 5 kg)

  Equipment:
    MixerID: Mixer1
    CycleTime: 110 minutes
    AverageMixSpeed: 798 RPM (spec: 800 RPM)
    AverageTemperature: 65.1°C (spec: 65 ± 2°C)

  Quality:
    - Homogeneity: Pass
    - Density: 1.205 g/ml (spec: 1.2 ± 0.05)
    - Result: Approved for release

  Genealogy:
    Operator: jsmith
    MaterialLots:
      - MaterialA: Lot-2024-5670
      - MaterialB: Lot-2024-5671
      - MaterialC: Lot-2024-5672
    OutputBatch: Batch-2024-1456
    OutputSerialRange: SN-100001 to SN-100495
```

## Integration Technologies for ISA-95

### Protocol Layer

**Industrial Protocols**:
- **OPC (OLE for Process Control)**
  - OPC Classic: Windows COM-based, deprecated
  - OPC-UA: Modern standard, cross-platform, recommended
  - Provides: Real-time data, hierarchical namespace

- **Profibus/Profinet** (Siemens)
  - Industrial Ethernet variant
  - Real-time capability
  - Wide equipment support

- **EtherNet/IP** (Rockwell)
  - Common in Allen-Bradley ecosystem
  - Native TCP/IP
  - Real-time via IGMP

- **Modbus** (legacy)
  - Simple, widely supported
  - Limited features
  - Slow but reliable

**Modern Protocols**:
- **MQTT**: Publish-subscribe, IoT-friendly, lightweight
- **REST/HTTP**: Web standard, easy integration, not real-time
- **AMQP**: Message-oriented, reliable, enterprise messaging
- **GraphQL**: Query language for complex data retrieval

### Middleware/Integration Platforms

**Purpose**: Translate between different protocols and data models.

**Examples**:
- **MuleSoft**: Cloud-based integration platform
- **Apache Kafka**: Event streaming platform
- **TIBCO**: Enterprise messaging and integration
- **Software AG**: webMethods integration platform
- **SAP Integration Suite**: Cloud-based B2B and system integration

**Benefits**:
- Protocol abstraction
- Data transformation
- Workflow orchestration
- Error handling and retry logic
- Monitoring and auditing

### Implementation Pattern: SAP ME to Equipment Integration

```
SAP S/4HANA (ERP)
    ↓ (CPI Integration)
SAP Manufacturing Execution (MES)
    ↓ (REST API or OPC-UA)
Integration Layer
    ├─ Data Transformation
    ├─ Protocol Translation
    ├─ Error Handling
    └─ Logging & Audit Trail
    ↓
Equipment Integration Gateway
    ├─ OPC-UA Clients
    ├─ Profinet Drivers
    ├─ Custom Device Adapters
    └─ Data Collection Agents
    ↓
Production Equipment (PLCs, SCADA, DCS)
```

## ISA-95 Compliance Best Practices

### 1. Data Model Adherence

- Use ISA-95 hierarchical structures for equipment and products
- Define clear relationships between entities
- Implement referential integrity
- Document all data element mappings
- Use consistent naming conventions

### 2. Temporal Alignment

- Synchronize clocks across all systems (NTP)
- Record timestamps at data origin point (equipment)
- Maintain timezone consistency
- Archive historical data with appropriate retention
- Enable time-based queries and analytics

### 3. Traceability Implementation

- Implement genealogy data capture at MES level
- Link production execution to materials, equipment, personnel
- Enable forward and backward queries
- Support impact analysis for defects
- Archive genealogy data per regulatory requirements

### 4. Integration Governance

- Establish standards for new system integrations
- Define data ownership and stewardship
- Create integration architecture documentation
- Implement health monitoring for integration flows
- Plan for system scaling and evolution

### 5. Security and Compliance

- Implement role-based access control at MES level
- Encrypt sensitive data in transit and at rest
- Maintain audit trails of all changes
- Conduct regular security assessments
- Align with regulatory requirements (21 CFR Part 11, GAMP 5)

## ISA-95 vs ISA-88 Relationship

**ISA-88 (Batch Control Standard)**:
- Focuses on batch process control (Levels 2-3)
- Defines phase/operation/action control model
- Suitable for pharmaceutical, chemical, food industries
- Very detailed equipment and control logic

**ISA-95 (Enterprise Integration Standard)**:
- Focuses on enterprise-to-operations integration (Levels 3-5)
- Defines functional architecture and data models
- Suitable for all manufacturing types
- Higher-level abstraction

**Integration**:
```
ISA-95 Defines: "Produce Widget-A, 500 units by 10:00 AM"
    ↓
ISA-88 Defines: "Execute Batch Recipe, Phase-by-phase control, validation"
    ↓
Equipment: Executes detailed batch process
```

## Summary

ISA-95 provides the framework for manufacturing system integration:
- **Levels**: Five-level hierarchy from equipment to enterprise
- **Data Models**: Product, process, equipment, resource definitions
- **Integration**: Patterns for system communication
- **Standards**: Vendor-independent approach to system architecture

Compliance with ISA-95 ensures:
- Interoperability between systems
- Standardized data definitions
- Reduced integration complexity
- Better scalability and flexibility
- Regulatory compliance alignment
