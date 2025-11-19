# Industry 4.0 Architecture Patterns

## Overview

This document presents proven architectural patterns for Industry 4.0 implementations, covering edge-to-cloud architectures, data management, integration patterns, and reference architectures used by leading manufacturers globally.

---

## Reference Architectures

### RAMI 4.0 (Reference Architecture Model Industrie 4.0)

**Three-Dimensional Model**

```
Dimension 1: Hierarchy Levels (ISA-95)
├── Connected World (Enterprise + Partners)
├── Enterprise (ERP, PLM, CRM)
├── Work Centers (MES, WMS)
├── Station (SCADA, HMI)
├── Control Device (PLC, DCS)
├── Field Device (Sensors, Actuators)
└── Product (Smart Products with embedded intelligence)

Dimension 2: Life Cycle & Value Stream
├── Development
├── Maintenance/Usage
├── Type (Product Design)
└── Instance (Physical Product)

Dimension 3: Layers
├── Business (Business Processes, Rules)
├── Functional (Functions, Services)
├── Information (Data Models, Semantics)
├── Communication (Protocols, Integration)
├── Integration (Human-Machine Interface)
└── Asset (Physical World)
```

**Application**: Use RAMI 4.0 when:
- Designing greenfield smart factories
- Creating digital twin strategies
- Planning asset lifecycle management
- Ensuring interoperability across vendors
- Aligning with European Industry 4.0 standards

---

### Industrial Internet Reference Architecture (IIRA)

**Four-Tier Architecture**

```
Tier 1: Business Layer
├── Business Applications (ERP, CRM, Analytics)
├── Business Intelligence & Reporting
├── Decision Support Systems
└── KPI Dashboards

Tier 2: Information Layer
├── Data Lakes & Warehouses
├── Analytics Engines
├── Information Models
└── Knowledge Management

Tier 3: Operations Layer
├── MES (Manufacturing Execution)
├── Asset Management
├── Quality Management
└── Operations Analytics

Tier 4: Edge/Control Layer
├── Edge Computing
├── Control Systems (PLC, DCS)
├── SCADA/HMI
└── Field Devices
```

**Cross-Cutting Concerns**:
- Security (Defense-in-Depth)
- Safety (IEC 61508, ISO 13849)
- Connectivity (Network Architecture)
- Data Management (Lifecycle, Governance)

**Application**: Use IIRA when:
- Implementing IIoT platforms
- Designing multi-vendor ecosystems
- Planning edge-to-cloud architectures
- Ensuring scalability and flexibility
- Aligning with IIC (Industrial Internet Consortium) standards

---

## Network Architecture Patterns

### Pattern 1: Purdue Model (ISA-95 Network Segmentation)

**Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│ Level 5: Enterprise Network                                 │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ERP │ PLM │ CRM │ Email │ Internet                      │ │
│ └─────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │ Firewall + DMZ
┌──────────────────────▼──────────────────────────────────────┐
│ Level 4.5: Industrial DMZ                                    │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Historians │ Data Lakes │ Replication Servers          │ │
│ └─────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │ Industrial Firewall
┌──────────────────────▼──────────────────────────────────────┐
│ Level 3-4: Manufacturing Operations Network                 │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ MES Servers │ HMI Servers │ SCADA Servers              │ │
│ │ Engineering Workstations │ Application Servers         │ │
│ └─────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │ Industrial Firewall / Unidirectional Gateway
┌──────────────────────▼──────────────────────────────────────┐
│ Level 2: Supervisory Control Network                        │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ HMI Clients │ Operator Stations │ SCADA Clients        │ │
│ │ Engineering Tools │ Remote Access (VPN)                │ │
│ └─────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │ No Firewall (Performance Critical)
┌──────────────────────▼──────────────────────────────────────┐
│ Level 1: Basic Control Network                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ PLCs │ DCS │ Safety PLCs │ Robot Controllers          │ │
│ │ Motion Controllers │ Industrial PCs                    │ │
│ └─────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │ Fieldbus / Industrial Ethernet
┌──────────────────────▼──────────────────────────────────────┐
│ Level 0: Process / Field Devices                            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Sensors │ Actuators │ VFDs │ I/O Modules │ Valves      │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Security Rules**:
- **Data flows primarily upward** (Level 0 → Level 5)
- **Downward flows** (commands) are carefully controlled
- **Firewalls between all levels** (except Level 1-2 for performance)
- **No direct internet access** from OT networks
- **DMZ for data exchange** between IT and OT
- **Separate VLANs** for each level

**Implementation Example**:
```yaml
Level 5 (Enterprise):
  Network: 10.0.0.0/16
  VLAN: 10
  Firewall: Allow outbound to internet, block inbound except VPN

Level 4.5 (DMZ):
  Network: 172.16.0.0/24
  VLAN: 45
  Firewall:
    - Inbound: Allow from Level 3-4 (specific ports/protocols)
    - Outbound: Allow to Level 5 (specific services)
    - No initiation from Level 5

Level 3-4 (MES/SCADA):
  Network: 192.168.10.0/24
  VLAN: 34
  Firewall:
    - Inbound: Allow from Level 2 (OPC UA, MQTT, etc.)
    - Outbound: Allow to DMZ (data push only)
    - Deep packet inspection enabled

Level 2 (Supervisory):
  Network: 192.168.20.0/24
  VLAN: 20
  No Firewall: Direct connection to Level 1 for real-time control

Level 1 (Control):
  Network: 192.168.30.0/24
  VLAN: 30
  Protocols: PROFINET, EtherNet/IP, EtherCAT (deterministic)

Level 0 (Field):
  Network: Various fieldbuses (PROFIBUS, Modbus RTU, etc.)
  Isolated from Ethernet networks
```

---

### Pattern 2: Edge-to-Cloud Architecture

**Multi-Tier Processing**

```
┌─────────────────────────────────────────────────────────────┐
│ Cloud Tier                                                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Enterprise Analytics │ ML Training │ Long-term Storage │ │
│ │ Cross-site Benchmarking │ Supply Chain Integration    │ │
│ └─────────────────────────────────────────────────────────┘ │
│  AWS IoT / Azure IoT / GCP IoT                              │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS / MQTT / AMQP
┌──────────────────────▼──────────────────────────────────────┐
│ Fog/Edge Tier (Factory Level)                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Edge Analytics │ Local ML Inference │ Data Aggregation│ │
│ │ Historians │ Local MES │ Edge Orchestration           │ │
│ └─────────────────────────────────────────────────────────┘ │
│  Industrial Servers / Edge Gateways                         │
└──────────────────────┬──────────────────────────────────────┘
                       │ OPC UA / MQTT / Industrial Protocols
┌──────────────────────▼──────────────────────────────────────┐
│ Edge Tier (Line/Machine Level)                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Protocol Conversion │ Local Buffering │ Filtering      │ │
│ │ Real-time Analytics │ Alerting │ Control Feedback     │ │
│ └─────────────────────────────────────────────────────────┘ │
│  Edge Gateways / Industrial PCs                             │
└──────────────────────┬──────────────────────────────────────┘
                       │ Modbus / PROFINET / Proprietary
┌──────────────────────▼──────────────────────────────────────┐
│ Device Tier                                                  │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ PLCs │ Sensors │ Actuators │ Controllers │ Drives      │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Processing Distribution**:

| Tier | Latency | Processing | Data Volume | Use Cases |
|------|---------|------------|-------------|-----------|
| Device | <10ms | Immediate control | Raw, high-frequency | Safety, motion control |
| Edge (Machine) | <100ms | Local analytics | Filtered, buffered | Quality checks, alerts |
| Edge (Factory) | <1s | Aggregation, ML inference | Aggregated, contextualized | OEE, predictive maintenance |
| Cloud | >1s | Training, optimization | Historical, cross-site | Enterprise analytics, AI training |

**Example Implementation**:
```python
# Edge Gateway (Machine Level)
class EdgeGateway:
    def __init__(self):
        self.plc_client = OpcUaClient("opc.tcp://192.168.30.10:4840")
        self.mqtt_client = MqttClient("factory-mqtt-broker:1883")
        self.buffer = CircularBuffer(size=10000)
        self.ml_model = load_model("quality_inspection.onnx")

    async def process_data(self):
        while True:
            # Read from PLC at high frequency
            raw_data = await self.plc_client.read_values([
                "Temperature", "Pressure", "Flow_Rate", "Vibration"
            ])

            # Local processing & filtering
            if raw_data["Vibration"] > ANOMALY_THRESHOLD:
                # Immediate local alert
                await self.trigger_alarm("HIGH_VIBRATION", raw_data)

            # ML inference at edge
            quality_score = self.ml_model.predict(raw_data)
            if quality_score < QUALITY_THRESHOLD:
                await self.notify_operator(quality_score)

            # Buffer for cloud transmission (reduced frequency)
            self.buffer.append({
                "timestamp": time.time(),
                "data": raw_data,
                "quality_score": quality_score
            })

            # Transmit to cloud every 10 seconds (aggregated)
            if time.time() % 10 == 0:
                aggregated = self.buffer.aggregate()
                await self.mqtt_client.publish(
                    topic="factory/line1/machine3",
                    payload=json.dumps(aggregated)
                )

            await asyncio.sleep(0.1)  # 100ms cycle
```

---

## Data Management Patterns

### Pattern 3: Unified Namespace (UNS)

**Concept**: Single, centralized data infrastructure where all systems publish and subscribe to a hierarchical event-driven architecture.

**Architecture**:

```
                    ┌──────────────────────┐
                    │   MQTT Broker (UNS)  │
                    │  Unified Namespace   │
                    └──────────┬───────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
    ┌─────▼─────┐        ┌────▼────┐        ┌─────▼─────┐
    │Publishers │        │  Topics  │        │Subscribers│
    └───────────┘        └─────────┘        └───────────┘
         │                     │                    │
    ┌────┼──────┐         Hierarchy           ┌────┼─────┐
    │    │      │              │               │    │     │
   PLC  MES   ERP    site/area/line/...      HMI  Cloud Analytics
```

**Topic Hierarchy**:
```
enterprise/
├── chicago/                    # Site
│   ├── assembly/              # Area
│   │   ├── line1/             # Line
│   │   │   ├── station1/      # Station
│   │   │   │   ├── robot/     # Equipment
│   │   │   │   │   ├── position
│   │   │   │   │   ├── speed
│   │   │   │   │   ├── status
│   │   │   │   │   ├── alarms
│   │   │   │   │   └── commands
│   │   │   │   └── conveyor/
│   │   │   ├── station2/
│   │   │   └── metadata/      # Line-level data
│   │   │       ├── oee
│   │   │       ├── production_count
│   │   │       └── downtime_reason
│   │   ├── line2/
│   │   └── welding/
│   ├── packaging/
│   └── quality_lab/
└── phoenix/
    └── ...
```

**Benefits**:
- **Decoupled systems**: Publishers don't know subscribers
- **Scalability**: Add systems without reconfiguring existing ones
- **Real-time data flow**: Event-driven, not polling
- **Single source of truth**: All systems use same data
- **Contextualized data**: Hierarchical organization provides context

**Implementation**:
```yaml
# PLC publishes data to UNS
plc_publisher:
  broker: mqtt://uns-broker.factory.local:1883
  base_topic: enterprise/chicago/assembly/line1/station1
  data_points:
    - robot/position -> OPC UA ns=2;s=Robot1.ActualPosition
    - robot/speed -> OPC UA ns=2;s=Robot1.ActualSpeed
    - conveyor/speed -> OPC UA ns=2;s=Conveyor1.Speed
  publish_rate: 100ms
  qos: 1

# MES subscribes to UNS
mes_subscriber:
  broker: mqtt://uns-broker.factory.local:1883
  subscriptions:
    - enterprise/chicago/assembly/+/+/robot/status  # All robots
    - enterprise/chicago/+/+/+/production_count     # All production
    - enterprise/+/+/line1/+/alarms                 # Line 1 alarms
  qos: 1

# Cloud analytics subscribes to aggregated data
cloud_subscriber:
  broker: mqtt://uns-broker.factory.local:1883
  subscriptions:
    - enterprise/+/+/+/metadata/oee                 # OEE from all lines
    - enterprise/+/+/+/metadata/downtime_reason     # Downtime tracking
  qos: 1
  store_and_forward: true  # Buffer during connectivity loss
```

---

### Pattern 4: Lambda Architecture for Manufacturing Data

**Batch + Real-Time Processing**

```
┌──────────────────────────────────────────────────────────────┐
│ Data Sources                                                  │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│ │   PLCs   │ │  SCADA   │ │   MES    │ │  ERP     │        │
│ └─────┬────┘ └─────┬────┘ └─────┬────┘ └─────┬────┘        │
└───────┼────────────┼────────────┼────────────┼──────────────┘
        │            │            │            │
        └────────────┼────────────┼────────────┘
                     │
        ┌────────────▼────────────────┐
        │  Data Ingestion Layer       │
        │  (Kafka / Event Hub)        │
        └────────┬──────────┬─────────┘
                 │          │
        ┌────────▼──┐  ┌───▼──────────────────────┐
        │ Batch     │  │ Real-Time Stream         │
        │ Layer     │  │ Processing               │
        │           │  │                          │
        │ Hadoop/   │  │ Spark Streaming/         │
        │ Spark     │  │ Flink/Azure Stream       │
        │           │  │                          │
        │ Process:  │  │ Process:                 │
        │ - ETL     │  │ - Aggregation            │
        │ - ML      │  │ - Alerting               │
        │ Training  │  │ - Real-time dashboards   │
        │ - Reports │  │ - Anomaly detection      │
        └────────┬──┘  └───┬──────────────────────┘
                 │         │
                 │    ┌────▼────────┐
                 │    │  Real-Time  │
                 │    │  Views      │
                 │    └────┬────────┘
                 │         │
        ┌────────▼─────────▼─────────┐
        │   Serving Layer            │
        │                            │
        │ Batch Views + Real-Time    │
        │ (Data Warehouse / Lake)    │
        └────────────┬───────────────┘
                     │
        ┌────────────▼───────────────┐
        │ Application Layer          │
        │ - Dashboards               │
        │ - Analytics                │
        │ - ML Models                │
        └────────────────────────────┘
```

**Use Cases**:
- **Batch Layer**: Historical analysis, model training, compliance reports
- **Speed Layer**: Real-time OEE, alerts, operator dashboards
- **Serving Layer**: Combined views for complete analytics

---

### Pattern 5: Digital Twin Architecture

**Levels of Digital Twins**

```
Level 1: Digital Model (Static)
┌────────────────────────────────┐
│ 3D CAD Model                   │
│ - Geometry                     │
│ - Bill of Materials            │
│ - No real-time connection      │
└────────────────────────────────┘

Level 2: Digital Shadow (One-Way)
┌────────────────────────────────┐
│ Virtual Representation         │
│ ┌──────────────────────────┐   │
│ │ Real-Time Data from      │   │
│ │ Physical Asset           │   │
│ └──────────┬───────────────┘   │
│            ▼                   │
│ ┌────────────────────────┐     │
│ │ Simulation / Analytics │     │
│ └────────────────────────┘     │
└────────────────────────────────┘
        Physical → Virtual

Level 3: Digital Twin (Bi-Directional)
┌────────────────────────────────┐
│ Autonomous Twin                │
│ ┌──────────────────────────┐   │
│ │ Physical Asset           │   │
│ └──────┬──────────▲────────┘   │
│        │          │            │
│        ▼          │            │
│ ┌──────────────────────────┐   │
│ │ Virtual Twin             │   │
│ │ - Simulation             │   │
│ │ - Optimization           │   │
│ │ - Predictive Analytics   │   │
│ └──────────────────────────┘   │
└────────────────────────────────┘
   Physical ⟷ Virtual (Closed Loop)
```

**Implementation Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│ Physical Asset (Production Line)                            │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│ │ Robot       │ │ Conveyor    │ │ Quality     │           │
│ │ (Sensors)   │ │ (Sensors)   │ │ Inspection  │           │
│ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘           │
└────────┼───────────────┼───────────────┼───────────────────┘
         │               │               │
    (OPC UA / MQTT Data Streaming)
         │               │               │
┌────────▼───────────────▼───────────────▼───────────────────┐
│ Data Integration Layer                                      │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Real-Time Data Pipeline (Kafka/Event Hub)              │ │
│ │ - Time synchronization                                  │ │
│ │ - Data quality validation                               │ │
│ │ - Contextualization                                     │ │
│ └─────────────────────────────────────────────────────────┘ │
└────────┬────────────────────────────────────────────────────┘
         │
┌────────▼────────────────────────────────────────────────────┐
│ Digital Twin Core                                           │
│ ┌──────────────────────┐  ┌──────────────────────┐         │
│ │ Geometric Model      │  │ Behavior Model       │         │
│ │ (CAD/3D)             │  │ (Physics-based)      │         │
│ └──────────────────────┘  └──────────────────────┘         │
│ ┌──────────────────────┐  ┌──────────────────────┐         │
│ │ Data Model           │  │ Analytics Model      │         │
│ │ (State/Properties)   │  │ (ML/AI)              │         │
│ └──────────────────────┘  └──────────────────────┘         │
└────────┬────────────────────────────────────────────────────┘
         │
┌────────▼────────────────────────────────────────────────────┐
│ Twin Applications                                           │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│ │ Virtual     │ │ Predictive  │ │ What-If     │           │
│ │ Commission  │ │ Maintenance │ │ Analysis    │           │
│ └─────────────┘ └─────────────┘ └─────────────┘           │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│ │ Process     │ │ Training    │ │ Optimization│           │
│ │ Optimization│ │ Simulator   │ │ Algorithms  │           │
│ └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
         │ (Control Commands if closed-loop)
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Physical Asset (receives optimized parameters)              │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration Patterns

### Pattern 6: Event-Driven Architecture

**Pub/Sub Manufacturing Events**

```python
# Event definitions
class ManufacturingEvent:
    MACHINE_STATE_CHANGED = "machine.state.changed"
    QUALITY_CHECK_FAILED = "quality.check.failed"
    PRODUCTION_ORDER_STARTED = "production.order.started"
    MAINTENANCE_REQUIRED = "maintenance.required"
    MATERIAL_LOW = "material.low"

# Event publisher (PLC Gateway)
class PLCEventPublisher:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.last_state = {}

    async def monitor_machine_states(self):
        while True:
            current_states = await self.read_machine_states()

            for machine_id, state in current_states.items():
                if state != self.last_state.get(machine_id):
                    # Publish state change event
                    await self.event_bus.publish(
                        event_type=ManufacturingEvent.MACHINE_STATE_CHANGED,
                        payload={
                            "machine_id": machine_id,
                            "previous_state": self.last_state.get(machine_id),
                            "current_state": state,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                    self.last_state[machine_id] = state

            await asyncio.sleep(0.1)

# Event subscriber (MES)
class MESEventSubscriber:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.event_bus.subscribe(
            ManufacturingEvent.MACHINE_STATE_CHANGED,
            self.handle_machine_state_change
        )
        self.event_bus.subscribe(
            ManufacturingEvent.QUALITY_CHECK_FAILED,
            self.handle_quality_failure
        )

    async def handle_machine_state_change(self, event):
        if event["current_state"] == "FAULT":
            # Create work order for maintenance
            await self.create_maintenance_work_order(event["machine_id"])
            # Update OEE calculations
            await self.update_oee(event["machine_id"], downtime=True)
        elif event["current_state"] == "RUNNING":
            # Resume production tracking
            await self.resume_production_tracking(event["machine_id"])

    async def handle_quality_failure(self, event):
        # Hold lot for quality review
        await self.hold_lot(event["lot_id"])
        # Notify quality engineer
        await self.notify_quality_team(event)
        # Adjust process parameters if within authority
        if event["auto_adjust_allowed"]:
            await self.adjust_process_parameters(event["recommendations"])
```

---

### Pattern 7: API Gateway for Manufacturing

**Unified API Access**

```
┌────────────────────────────────────────────────────────────┐
│ Clients (Web, Mobile, Analytics, Partners)                 │
└────────────────────┬───────────────────────────────────────┘
                     │ HTTPS / REST / GraphQL
┌────────────────────▼───────────────────────────────────────┐
│ API Gateway                                                 │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Authentication & Authorization                          │ │
│ │ Rate Limiting                                           │ │
│ │ Request/Response Transformation                         │ │
│ │ Caching                                                 │ │
│ │ Analytics & Logging                                     │ │
│ └────────────────────────────────────────────────────────┘ │
└──────┬──────┬──────┬──────┬──────┬──────┬──────────────────┘
       │      │      │      │      │      │
  ┌────▼──┐┌──▼───┐┌─▼───┐┌─▼───┐┌─▼───┐┌─▼──────┐
  │ MES   ││SCADA ││ ERP ││ PLM ││ QMS ││Historian│
  │Service││Svc   ││ Svc ││ Svc ││ Svc ││Service  │
  └───────┘└──────┘└─────┘└─────┘└─────┘└─────────┘
```

**API Design**:
```yaml
# REST API for production data
GET /api/v1/production/orders
  Returns: List of active production orders

GET /api/v1/production/orders/{id}
  Returns: Specific order details

POST /api/v1/production/orders
  Body: { product_id, quantity, due_date }
  Returns: Created order ID

GET /api/v1/equipment/{equipment_id}/status
  Returns: Real-time equipment status

GET /api/v1/equipment/{equipment_id}/metrics
  Query: ?from=2025-11-01&to=2025-11-19&metric=oee
  Returns: Time-series metric data

# GraphQL API (flexible queries)
query {
  productionLine(id: "Line1") {
    name
    currentStatus
    oee
    stations {
      name
      equipment {
        name
        status
        sensors {
          name
          value
          unit
        }
      }
    }
  }
}
```

---

## Microservices Pattern for Manufacturing

### Service Decomposition

```
┌─────────────────────────────────────────────────────────────┐
│ Manufacturing Microservices Architecture                    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Production   │  │ Quality      │  │ Maintenance  │      │
│  │ Service      │  │ Service      │  │ Service      │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐      │
│  │ Inventory    │  │ Scheduling   │  │ Analytics    │      │
│  │ Service      │  │ Service      │  │ Service      │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│  ┌──────▼──────────────────▼──────────────────▼───────┐     │
│  │ Shared Services                                     │     │
│  │ - Authentication                                    │     │
│  │ - Configuration                                     │     │
│  │ - Logging & Monitoring                              │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ Data Layer                                          │     │
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐            │     │
│  │ │Production│ │ Quality  │ │Asset     │            │     │
│  │ │ DB       │ │ DB       │ │ DB       │            │     │
│  │ └──────────┘ └──────────┘ └──────────┘            │     │
│  └─────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

**Service Boundaries**:
- Each service owns its data
- Communication via APIs or message bus
- Independent deployment and scaling
- Domain-driven design principles

---

## Summary

These architectural patterns provide proven foundations for Industry 4.0 implementations:

1. **RAMI 4.0 & IIRA**: Reference architectures for overall system design
2. **Purdue Model**: Network segmentation for security
3. **Edge-to-Cloud**: Distributed processing for latency and bandwidth
4. **Unified Namespace**: Event-driven data architecture
5. **Lambda Architecture**: Batch + real-time analytics
6. **Digital Twin**: Virtual representation for optimization
7. **Event-Driven**: Reactive, decoupled systems
8. **API Gateway**: Unified access to manufacturing systems
9. **Microservices**: Modular, scalable services

Choose patterns based on:
- Business requirements (latency, scalability, security)
- Existing infrastructure (brownfield vs. greenfield)
- Organizational maturity (start simple, evolve)
- Budget and timeline constraints

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**References**: ISA-95, RAMI 4.0, IIRA, Industry 4.0 Platform
