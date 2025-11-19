# Edge Computing Architecture and Processing Reference

## Overview of Edge Computing

Edge computing brings computation, storage, and data processing closer to devices and sensors that generate data, rather than relying exclusively on centralized cloud infrastructure. In manufacturing, this dramatically improves latency, bandwidth efficiency, and system resilience.

## 1. Edge Computing Hierarchy

```
┌───────────────────────────────────────────────────┐
│         Cloud / Centralized Layer                 │
│  - Machine learning model training                │
│  - Long-term data storage and analytics           │
│  - Enterprise application integration             │
│  - Complex cross-facility analytics               │
└───────────────────┬─────────────────────────────────┘
                    │ 100s-1000s ms latency
                    │ Periodic data sync
                    │
┌───────────────────▼──────────────────────────────┐
│    Fog / Regional Layer                           │
│  - Regional data aggregation                      │
│  - Historical data compression                    │
│  - Multi-site correlation analysis                │
│  - Disaster recovery coordination                 │
└───────────────────┬──────────────────────────────┘
                    │ 10-100 ms latency
                    │ Event-driven updates
                    │
┌───────────────────▼──────────────────────────────┐
│    Edge / Local Layer                             │
│  - Real-time anomaly detection                    │
│  - Local decision-making                          │
│  - Bandwidth optimization                         │
│  - Offline operation capability                   │
└───────────────────┬──────────────────────────────┘
                    │ 1-50 ms latency
                    │ Immediate actions
                    │
┌───────────────────▼──────────────────────────────┐
│    Device / Endpoint Layer                        │
│  - Sensors and actuators                          │
│  - PLCs and local controllers                     │
│  - Smart instruments                              │
│  - Wireless sensor nodes                          │
└───────────────────────────────────────────────────┘
```

## 2. Edge Node Architecture

### Typical Edge Node Components

```
┌─────────────────────────────────────────────────┐
│         Edge Node                               │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │ Data Collection Layer                     │  │
│  │ ├── Modbus RTU/TCP gateway               │  │
│  │ ├── OPC UA client                         │  │
│  │ ├── Profibus/CANopen bridge               │  │
│  │ ├── Analog I/O module                     │  │
│  │ └── Serial port handlers                  │  │
│  └──────────────────────────────────────────┘  │
│                  ↓                              │
│  ┌──────────────────────────────────────────┐  │
│  │ Processing Engine                         │  │
│  │ ├── Real-time filters                     │  │
│  │ ├── Statistical calculations              │  │
│  │ ├── Rule engine                           │  │
│  │ ├── Stream processing                     │  │
│  │ └── Local AI/ML inference                 │  │
│  └──────────────────────────────────────────┘  │
│                  ↓                              │
│  ┌──────────────────────────────────────────┐  │
│  │ Storage & Buffering                       │  │
│  │ ├── Local database (InfluxDB, SQLite)    │  │
│  │ ├── Message queue (local persistence)     │  │
│  │ ├── Data compression                      │  │
│  │ └── Retention policies                    │  │
│  └──────────────────────────────────────────┘  │
│                  ↓                              │
│  ┌──────────────────────────────────────────┐  │
│  │ Communication Layer                       │  │
│  │ ├── MQTT client (Sparkplug B)            │  │
│  │ ├── OPC UA server                         │  │
│  │ ├── REST API server                       │  │
│  │ └── Sync & conflict resolution            │  │
│  └──────────────────────────────────────────┘  │
│                  ↓                              │
│  ┌──────────────────────────────────────────┐  │
│  │ Management & Security                     │  │
│  │ ├── Health monitoring                     │  │
│  │ ├── OTA updates                           │  │
│  │ ├── Certificate management                │  │
│  │ ├── Local authentication                  │  │
│  │ └── Audit logging                         │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
```

## 3. Edge Computing Patterns

### Pattern 1: Streaming Analytics

```
Raw Equipment Data Stream
    ↓
Edge Node
├── Real-time aggregation (rolling averages)
├── Anomaly detection (statistical bounds)
├── Threshold checking (alert generation)
└── Filtering (send only important changes)
    ↓
Cloud
└── Trend analysis, model training
```

**Use Case:** Monitor temperature across 100 sensors, send alerts only when abnormal.

### Pattern 2: Local Decision-Making

```
Sensor Data
    ↓
Edge Node
├── Read multiple inputs
├── Run decision logic
├── Generate local response
└── Cache decision for audit trail
    ↓
Actuator Control
(millisecond response)
    ↓
Cloud
└── Asynchronous notification
```

**Use Case:** Emergency stop on safety violation.

### Pattern 3: Data Aggregation and Transformation

```
Multiple Data Sources
├── PLC (Modbus)
├── Sensors (analog)
└── Wireless devices (MQTT)
    ↓
Edge Node
├── Protocol translation
├── Data enrichment (metadata, context)
├── Format standardization (Sparkplug B)
└── Compression and filtering
    ↓
Cloud Platform
```

**Use Case:** Integration with legacy systems for cloud analytics.

### Pattern 4: Offline-First Operation

```
Normal Operation
├── Collect data locally
├── Process and alert locally
└── Sync to cloud periodically
    ↓
Network Outage
├── Continue local operation
├── Buffer data in local storage
└── Maintain device control capability
    ↓
Network Restored
└── Sync buffered data to cloud
```

**Use Case:** Manufacturing plant with unreliable internet connection.

### Pattern 5: Collaborative Edge

```
Edge Node 1              Edge Node 2
    ├─────────────────────┤
    │ Local Sync (fast)   │
    └─────────────────────┘
          ↓
    Cloud Synchronization
    (slower, for analytics)
```

**Use Case:** Multiple production areas sharing data for cross-line optimization.

## 4. Edge Computing Hardware

### Industrial PCs (IPC)

```
Specifications:
├── CPU: Intel Core/Xeon i7-10700, AMD Ryzen
├── RAM: 8-64 GB
├── Storage: 256GB-2TB SSD
├── Connectivity: Gigabit Ethernet, WiFi, Serial, USB
├── I/O: DIO, analog inputs, relay outputs
├── Power: 100-240V AC, UPS capable
├── Operating Temp: 0-60°C (industrial grade)
├── Vibration Tolerance: IEC 60068-2-6
└── Certifications: CE, FCC, UL

Advantages:
- Full OS support (Linux, Windows)
- Extensive connector options
- Industrial reliability
- High performance for complex processing

Disadvantages:
- Higher power consumption
- Larger footprint
- Higher cost ($2000-5000)
```

### Single-Board Computers (SBC)

```
Raspberry Pi:
├── CPU: ARM Cortex-A72 (4 cores, 1.5 GHz)
├── RAM: 2-8 GB
├── Storage: microSD card
├── Connectivity: Gigabit Ethernet, WiFi, Bluetooth
├── I/O: GPIO pins (for sensors/relays)
├── Power: 5V USB-C
├── Operating Temp: 0-50°C
└── Cost: $35-100

NVIDIA Jetson Nano:
├── CPU: ARM Cortex-A57 (4 cores)
├── GPU: 128-core NVIDIA Maxwell
├── RAM: 2-4 GB
├── Power: 5-10W typical
├── GPU acceleration: Ideal for edge AI
└── Cost: $99-149

Advantages:
- Low power consumption
- Small form factor
- Low cost
- Easy prototyping
- Community support

Disadvantages:
- Limited processing power
- Limited connectivity options
- May struggle with heavy processing
- ARM architecture limitations
```

### Ruggedized Edge Devices

```
Specifications:
├── Industrial Chassis (metal, sealed)
├── Modular architecture (expandable)
├── Multiple network interfaces (Ethernet, 5G, satellite)
├── Extensive I/O (CAN, Profibus, EtherCAT)
├── Wide temp range (-40 to +70°C)
├── Redundancy features (dual CPUs, hot-swap)
├── Power: 24V DC with battery backup
├── IP Rating: IP65 or better
└── Certifications: IEC 61439, E-Mark, Atex (Ex hazardous areas)

Examples:
- Siemens SIMATIC IPC277E
- Beckhoff CX embedded PC
- National Instruments CompactRIO
- Kontron KBox series

Advantages:
- Built for manufacturing environment
- Extensive connectivity
- Professional support
- Reliability in harsh conditions

Disadvantages:
- Very high cost ($5000-20000+)
- Longer lead times
- May be overkill for simple applications
```

### Edge Gateway Appliances

```
Pre-configured, purpose-built for specific tasks:

Example: Dell Edge Gateway 5000
├── Intel Atom processor
├── 2-8 GB RAM
├── Linux OS
├── Multiple Ethernet ports
├── Modbus, OPC UA support
├── Pre-loaded analytics engine
└── Cost: $1000-1500

Advantages:
- Out-of-box functionality
- Vendor support
- Lower deployment time
- Optimized for edge tasks

Disadvantages:
- Less flexible
- Vendor lock-in
- May have unused capabilities
```

## 5. Edge Operating Systems and Runtimes

### Linux-Based

```
Options:
- Standard Ubuntu (Server or Core)
- Embedded Linux (Yocto, Buildroot)
- Real-time Linux (PREEMPT_RT patches)
- Container-optimized (Ubuntu Core)

Container Runtimes:
├── Docker: Standard containerization
├── Podman: Daemon-less alternative
└── containerd: Lightweight runtime

Orchestration:
├── Kubernetes: Full orchestration (resource-heavy)
├── k3s: Lightweight Kubernetes
├── microk8s: Snap-based minimal K8s
├── Docker Compose: Multi-container orchestration
└── systemd: Traditional service management
```

### Real-Time Linux

```
For deterministic manufacturing requirements:

PREEMPT_RT Patches:
- Reduce maximum latency to < 100 microseconds
- Kernel preemption
- Priority inheritance
- Suitable for motion control, safety systems

Installation:
# Patch kernel with real-time patches
# Compile with CONFIG_PREEMPT_RT_FULL
# High-priority processes with chrt

Limitations:
- Not suitable for SMP (multi-processor) audio/video
- CPU overhead ~5-10%
- Device driver compatibility issues
```

### Windows IoT

```
Windows IoT Core:
- Minimal Windows installation
- 256 MB minimum RAM
- Universal Windows Platform (UWP) apps
- Good for Microsoft ecosystem
- Limited device driver support
- Higher resource consumption than Linux

When to use:
- Heavy reliance on .NET Framework
- Windows-only legacy applications
- Microsoft ecosystem (Azure, Active Directory)
- Familiar Windows development tools
```

## 6. Edge Processing Technologies

### Node-RED

```
Visual programming for IoT:

Concepts:
├── Nodes: Individual functions (inject, function, output)
├── Flow: Visual arrangement of nodes
├── Deploy: Instantly activate changes
└── Persistent storage: JSON-based flow storage

Example Flow:
[Modbus Input] → [Filter] → [Aggregate] → [MQTT Output]

Advantages:
- Visual, intuitive programming
- Huge library of pre-built nodes
- Real-time updates without restart
- Good for integration tasks

Disadvantages:
- Performance overhead
- Not suitable for heavy computation
- Memory overhead (~200 MB typical)
- JavaScript execution for custom logic
```

### Apache Kafka for Edge

```
Edge Kafka Deployment:

Single-node cluster for edge:
- Minimal broker setup
- Local topics for data streams
- Retention policies for storage management
- Consumer groups for processing

Use Case:
├── Buffer data during cloud outage
├── Stream processing at edge
├── Multiple consumer patterns
└── Event sourcing architecture

Configuration:
broker.rack=edge-rack-01
log.retention.hours=168  # 1 week local
num.network.threads=2   # Minimal threads
log.segment.bytes=52428800  # 50 MB segments
```

### Telegraf Agent

```
Lightweight metrics collection:

Configuration:
[global_tags]
  facility = "plant-01"
  edge_node = "edge-01"

[[inputs.exec]]
  commands = ["python /opt/collectors/modbus.py"]
  data_format = "json"
  interval = "10s"

[[outputs.influxdb]]
  urls = ["http://localhost:8086"]
  database = "manufacturing"
  precision = "ms"

[[outputs.mqtt]]
  servers = ["mqtt://broker:1883"]
  topic_prefix = "spBv1.0"
  data_format = "json"

Advantages:
- Low memory footprint (< 50 MB)
- Extensive input plugins
- Multiple output support
- Easy configuration
```

### RabbitMQ for Edge

```
Lightweight message broker:

Edge Configuration:
- Single node (no clustering)
- Durable queues for persistence
- Dead-letter exchanges for error handling
- Limited TTL for old messages

Typical Setup:
├── Data queue: device → edge processing
├── Alert queue: edge → cloud
├── Command queue: cloud → edge
└── Dead-letter queue: failed messages

Memory optimization:
vm_memory_high_watermark.relative = 0.5  # Use 50% RAM
channel_max = 256  # Limit channels
heartbeat = 60  # Reduce heartbeat frequency
```

## 7. Edge Analytics Implementation

### Real-Time Filtering

```python
class RollingAverage:
    def __init__(self, window_size=10):
        self.window = []
        self.window_size = window_size

    def add_value(self, value):
        self.window.append(value)
        if len(self.window) > self.window_size:
            self.window.pop(0)
        return sum(self.window) / len(self.window)

class AnomalyDetector:
    def __init__(self, threshold_std=3.0):
        self.values = []
        self.threshold_std = threshold_std
        self.mean = 0
        self.std = 0

    def is_anomaly(self, value):
        self.values.append(value)
        if len(self.values) < 20:  # Need baseline
            return False

        self.mean = sum(self.values[-100:]) / 100  # 100-value window
        variance = sum((x - self.mean)**2 for x in self.values[-100:]) / 100
        self.std = variance ** 0.5

        z_score = abs(value - self.mean) / (self.std + 1e-6)
        return z_score > self.threshold_std
```

### Edge Machine Learning Inference

```python
import numpy as np
from tensorflow.lite.python import interpreter

class EdgeMLInference:
    def __init__(self, model_path):
        self.interpreter = interpreter.Interpreter(
            model_path=model_path
        )
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def predict(self, input_data):
        # Set input
        input_index = self.input_details[0]['index']
        self.interpreter.set_tensor(
            input_index,
            np.array(input_data, dtype=np.float32)
        )

        # Run inference
        self.interpreter.invoke()

        # Get output
        output_index = self.output_details[0]['index']
        output = self.interpreter.get_tensor(output_index)

        return output[0]  # Return prediction

# Example: Bearing failure prediction
predictor = EdgeMLInference('/models/bearing_failure.tflite')
vibration_data = [0.25, 0.24, 0.26, 0.25, 0.27]
rul_days = predictor.predict(vibration_data)
print(f"Estimated bearing life: {rul_days} days")
```

## 8. Edge Data Persistence

### Local Time-Series Database

```python
# InfluxDB Edge Configuration
from influxdb_client import InfluxDBClient, Point

client = InfluxDBClient(
    url="http://localhost:8086",
    token="edge-token",
    org="manufacturing",
    timeout=5000
)

write_api = client.write_api(write_options=SYNCHRONOUS)

# Write industrial data
point = Point("equipment_metrics") \
    .tag("facility", "plant-01") \
    .tag("equipment", "motor-01") \
    .field("temperature", 45.5) \
    .field("vibration", 0.25) \
    .field("power", 125.8) \
    .time("2024-01-15T10:30:00Z")

write_api.write(bucket="manufacturing", record=point)

# Query local data
query = """from(bucket:"manufacturing")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "equipment_metrics")
  |> group(columns: ["_time"])
  |> mean()"""

result = query_api.query(query)
```

### SQLite for Structured Data

```python
import sqlite3

class EdgeLocalDatabase:
    def __init__(self, db_path="/var/edge/local.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_schema()

    def create_schema(self):
        """Create edge database schema"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                equipment_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                synced BOOLEAN DEFAULT FALSE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                acknowledged BOOLEAN DEFAULT FALSE
            )
        """)

        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_metrics_synced
            ON metrics(synced, timestamp)
        """)

        self.conn.commit()

    def insert_metric(self, equipment_id, metric_name, value):
        self.cursor.execute("""
            INSERT INTO metrics (equipment_id, metric_name, value)
            VALUES (?, ?, ?)
        """, (equipment_id, metric_name, value))
        self.conn.commit()

    def get_unsynced_metrics(self, limit=1000):
        self.cursor.execute("""
            SELECT id, equipment_id, metric_name, value, timestamp
            FROM metrics
            WHERE synced = FALSE
            ORDER BY timestamp ASC
            LIMIT ?
        """, (limit,))
        return self.cursor.fetchall()

    def mark_synced(self, metric_ids):
        placeholders = ','.join('?' * len(metric_ids))
        self.cursor.execute(f"""
            UPDATE metrics
            SET synced = TRUE
            WHERE id IN ({placeholders})
        """, metric_ids)
        self.conn.commit()
```

## 9. Edge Security

### Secure Boot and Attestation

```
Edge Device Security Chain:

1. Hardware Security Module (HSM)
   └── Secure key storage
   └── Cryptographic operations
   └── Attestation certificates

2. Secure Boot
   ├── Signed bootloader
   ├── Verified kernel
   └── Integrity checking

3. Runtime Protection
   ├── TLS certificates for communication
   ├── Encrypted configuration
   └── Regular security updates
```

### Edge Authentication

```python
import ssl
from cryptography import x509
from cryptography.hazmat.primitives import hashes

class EdgeSecureConnection:
    def __init__(self, ca_cert, device_cert, device_key):
        self.ca_cert = ca_cert
        self.device_cert = device_cert
        self.device_key = device_key

    def create_secure_context(self):
        """Create TLS context for edge device"""
        context = ssl.create_default_context(
            cafile=self.ca_cert
        )

        context.load_cert_chain(
            certfile=self.device_cert,
            keyfile=self.device_key
        )

        # Enforce TLS 1.3
        context.minimum_version = ssl.TLSVersion.TLSv1_3

        # Use strong ciphers
        context.set_ciphers('HIGH:!aNULL:!eNULL:!EXPORT:!DES:!MD5:!PSK')

        return context

    def verify_server_certificate(self, hostname):
        """Verify cloud server certificate"""
        context = self.create_secure_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED

        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                print(f"Connected securely to {hostname}")
```

## 10. Edge Synchronization Patterns

### Eventual Consistency

```
Edge Node                Cloud
    │                     │
    ├─ Write locally ──┐  │
    │                  │  │
    │  ┌──────────────▼──┼──────┐
    │  │ Queue for upload       │
    │  └──────────┬─────┘       │
    │             │             │
    ├─ Read ◄─────┘ (may be stale)
    │
    │  ┌──────────────────────────┐
    │  │ When connection available│
    │  └──────────┬───────────────┘
    │             │
    │             ├─ Upload batch ────► ✓ Ack
    │             │
    │             ├─ Handle conflicts
    │             │
    │             └─ Sync state
```

### Conflict Resolution

```python
class SyncManager:
    def __init__(self):
        self.pending_uploads = []
        self.local_state = {}

    def on_local_write(self, key, value, timestamp):
        """Record local write"""
        self.local_state[key] = {
            'value': value,
            'timestamp': timestamp,
            'source': 'local'
        }
        self.pending_uploads.append({
            'key': key,
            'value': value,
            'timestamp': timestamp
        })

    def resolve_conflict(self, key, remote_version, local_version):
        """Resolve write conflicts"""
        # Last-write-wins (timestamp-based)
        if remote_version['timestamp'] > local_version['timestamp']:
            return remote_version['value']
        else:
            return local_version['value']

    def sync_to_cloud(self):
        """Upload pending changes"""
        if not self.pending_uploads:
            return

        # Send batch to cloud
        response = self.upload_batch(self.pending_uploads)

        # Process responses
        for item in response['conflicts']:
            resolved = self.resolve_conflict(
                item['key'],
                item['remote'],
                item['local']
            )
            self.local_state[item['key']]['value'] = resolved

        self.pending_uploads = []
```

## 11. Edge Monitoring and Management

### Health Checks

```python
import psutil
import subprocess

class EdgeHealthMonitor:
    def __init__(self):
        self.thresholds = {
            'cpu': 80,          # percent
            'memory': 85,       # percent
            'disk': 90,         # percent
            'temperature': 70   # celsius
        }

    def check_health(self):
        health = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'alerts': []
        }

        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > self.thresholds['cpu']:
            health['alerts'].append({
                'component': 'cpu',
                'value': cpu_percent,
                'threshold': self.thresholds['cpu']
            })

        # Memory usage
        memory = psutil.virtual_memory()
        if memory.percent > self.thresholds['memory']:
            health['alerts'].append({
                'component': 'memory',
                'value': memory.percent,
                'threshold': self.thresholds['memory']
            })

        # Disk usage
        disk = psutil.disk_usage('/')
        if disk.percent > self.thresholds['disk']:
            health['alerts'].append({
                'component': 'disk',
                'value': disk.percent,
                'threshold': self.thresholds['disk']
            })

        # System temperature
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                max_temp = max(max(t.current for t in temps[name])
                             for name in temps)
                if max_temp > self.thresholds['temperature']:
                    health['alerts'].append({
                        'component': 'temperature',
                        'value': max_temp,
                        'threshold': self.thresholds['temperature']
                    })
        except:
            pass

        # Overall status
        health['status'] = 'healthy' if not health['alerts'] else 'degraded'

        return health

    def publish_health(self, mqtt_client):
        """Publish health status to cloud"""
        health = self.check_health()
        topic = "spBv1.0/manufacturing/DDATA/edge-01/health"
        mqtt_client.publish(topic, json.dumps(health))
```

### OTA (Over-The-Air) Updates

```python
import hashlib

class EdgeUpdateManager:
    def __init__(self, update_dir="/opt/updates"):
        self.update_dir = update_dir

    def download_update(self, url, checksum):
        """Download and verify update"""
        response = requests.get(url, stream=True)
        filepath = os.path.join(self.update_dir, "pending_update.tar.gz")

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Verify checksum
        file_checksum = self.compute_checksum(filepath)
        if file_checksum != checksum:
            raise ValueError("Checksum mismatch - update corrupted")

        return filepath

    def compute_checksum(self, filepath):
        """Compute SHA256 checksum"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def apply_update(self, filepath):
        """Apply update with rollback capability"""
        # Backup current state
        backup_dir = os.path.join(self.update_dir, "backup")
        shutil.copytree("/opt/edge", backup_dir)

        try:
            # Extract update
            import tarfile
            with tarfile.open(filepath, "r:gz") as tar:
                tar.extractall(path="/opt/edge")

            # Verify new files
            self.verify_installation()

            # Success - remove backup
            shutil.rmtree(backup_dir)
            return True

        except Exception as e:
            # Rollback on failure
            shutil.rmtree("/opt/edge")
            shutil.move(backup_dir, "/opt/edge")
            raise e
```

## Conclusion

Edge computing is essential for modern manufacturing IoT. By bringing processing closer to data sources, you achieve lower latency, better reliability, reduced bandwidth costs, and enhanced data privacy. The right combination of hardware, software, and patterns ensures your edge infrastructure scales with your manufacturing needs while maintaining the cloud's analytical power for strategic insights.
