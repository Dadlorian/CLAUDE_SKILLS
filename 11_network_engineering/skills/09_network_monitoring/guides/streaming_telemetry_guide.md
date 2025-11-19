# Streaming Telemetry Guide

## Pre-Implementation Planning

### Requirements Assessment
```
1. Device Capability Check
   - NETCONF/RESTCONF support
   - gRPC capability (for streaming)
   - YANG model availability
   - IOS-XE, IOS-XR, Junos, or other

2. Define Data Needs
   - Which operational data to stream
   - Subscription frequency requirements
   - On-change vs periodic model
   - Required sample intervals

3. Infrastructure Planning
   - Collector capacity
   - Network bandwidth impact
   - Storage architecture
   - High availability design
```

## Cisco IOS-XE Streaming Telemetry

### Step 1: Enable NETCONF/RESTCONF
```
router(config)# netconf-yang
router(config)# restconf
router(config)# end

! Verify
router# show platform software yang-management process
NETCONF: Yes
RESTCONF: Yes
```

### Step 2: Configure Sensor Groups
```
router(config)# telemetry ietf subscription base
router(config-telemetry)# sensor-group-list INTERFACE_STATS
  sensor-group INTERFACE_STATS
    sensor-path ietf-interfaces:interfaces/interface
    sensor-path openconfig-interfaces:interfaces
    sensor-path Cisco-IOS-XE-interfaces-oper:interfaces-state/interface
  !
  exit

router(config)# sensor-group-list ROUTING
  sensor-group ROUTING
    sensor-path openconfig-routing:routing
    sensor-path Cisco-IOS-XE-bgp-oper:bgp-state
  !
  exit
```

### Step 3: Define Subscriptions (Push Model)
```
router(config)# telemetry model-driven
  ! Sensor group definition
  sensor-group INTF_TELEMETRY
    sensor-path ietf-interfaces:interfaces/interface/statistics
    sensor-path openconfig-interfaces:interfaces/interface/state
  !

  ! Subscription definition
  subscription INTERFACE_STREAM
    sensor-group-id INTF_TELEMETRY 100
    update-policy on-change
    destination-id COLLECTOR1
  !

  ! Destination configuration
  destination-group COLLECTOR1
    address-family ipv4 10.0.0.100 port 5432
    transport grpc
    encoding self-describing-gpb
    connect-timeout 30000
    idle-timeout 300000
  !
end

! Verify
show telemetry model-driven subscription INTERFACE_STREAM
```

### Step 4: Verify Streaming
```
router# show telemetry model-driven subscription INTERFACE_STREAM brief
Subscription INTERFACE_STREAM
  Telemetry Routes: 100
  Sensor Groups: 1
  Destinations: 1
  Active: Yes

router# show telemetry model-driven subscription statistics
  Subscriptions: 1
  Active subscriptions: 1
  Messages transmitted: 45230
  Bytes transmitted: 23.4M
```

## Cisco IOS-XR Streaming Telemetry

### Configuration
```
router(config)# telemetry model-driven
  ! Sensor group for interface stats
  sensor-group INTERFACE_METRICS
    sensor-path Cisco-IOS-XR-infra-statsd-oper:infra-statistics/interfaces
    sensor-path Cisco-IOS-XR-pfi-ma-oper:interfaces/interface-statistics
  !

  ! Sensor group for BGP
  sensor-group BGP_METRICS
    sensor-path openconfig-bgp:bgp/neighbors
    sensor-path Cisco-IOS-XR-bgp-oper:bgp/instances/instance/neighbors
  !

  ! Subscription with periodic updates
  subscription PERIODIC_INTF
    sensor-group-id INTERFACE_METRICS 100
    sensor-group-id BGP_METRICS 50
    update-policy periodic 30000
    destination-group COLLECTOR
  !

  ! Destination
  destination-group COLLECTOR
    address-family ipv4 10.0.0.100 port 5432
    encoding gpb
    transport grpc
    connect-timeout 30
  !
end

! Verify
show telemetry model-driven subscription PERIODIC_INTF stats
```

## Juniper Junos Telemetry

### Configuration
```
system {
    telemetry {
        port 32768;
        max-clients 10;
        max-wait-time 30;
        max-msg-size 65536;
    }
}

routing-options {
    telemetry {
        # Interface statistics
        statistics {
            interface {
                name "ge-0/0/*";
                reporting-interval 30;
            }
        }
        # BGP information
        bgp {
            reporting-interval 60;
        }
    }
}

system {
    services {
        netconf {
            rfc-compliant;
            ssh;
        }
        rest {
            enable-streaming;
        }
    }
}
```

### YANG Paths
```
/interfaces
/routing/route-views/route-view[route-distinguisher]
/openconfig-interfaces:interfaces
/openconfig-bgp:bgp/neighbors
/junos-telemetry-interface:telemetry-interface
```

## Collector Setup

### Option 1: Telegraf (Universal Collector)
```
# telegraf.conf
[agent]
  interval = "30s"
  flush_interval = "30s"

[[inputs.cisco_telemetry_mdt]]
  transport = "grpc"
  service_address = "0.0.0.0:5432"
  max_msg_len = 524288

[[outputs.influxdb_v2]]
  urls = ["http://localhost:8086"]
  token = "YOUR_TOKEN"
  organization = "monitoring"
  bucket = "network_telemetry"
  tagpass = {
    device_type = ["router", "switch"]
  }
```

### Option 2: Custom gRPC Receiver (Python)
```python
import grpc
import telemetry_pb2
from concurrent import futures

class TelemetryReceiver:
    def __init__(self, port=5432):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self.port = port

    def process_telemetry(self, telemetry_msg):
        """
        Parse incoming telemetry message
        Extract metrics and store in database
        """
        node_id = telemetry_msg.node_id
        timestamp = telemetry_msg.timestamp

        for content in telemetry_msg.data_json:
            # Parse JSON content
            data = json.loads(content)

            # Extract metrics
            # Store to database (InfluxDB, Elasticsearch, etc.)
            self.store_metrics(node_id, timestamp, data)

    def store_metrics(self, device, ts, data):
        """Store metrics in time series database"""
        # Example: InfluxDB write
        write_api = influx_client.write_api(write_options=SYNCHRONOUS)
        points = []

        for metric_name, value in data.items():
            point = Point(metric_name) \
                .tag("device", device) \
                .field("value", value) \
                .time(ts)
            points.append(point)

        write_api.write(bucket="telemetry", records=points)

if __name__ == "__main__":
    receiver = TelemetryReceiver()
    receiver.start()
    print("Telemetry receiver listening on port 5432")
```

### Option 3: Kafka-based Pipeline
```
# Architecture:
Devices → gRPC → Kafka Producer → Kafka Broker → Kafka Consumers
                                       ↓
                            InfluxDB/Elasticsearch/S3
```

## YANG Data Models

### Standard Models
```
ietf-interfaces:
  /interfaces/interface[name]
    /name
    /enabled
    /mtu
    /statistics

ietf-ip:
  /interfaces/interface[name]/ipv4
    /address
    /enabled

openconfig-interfaces:
  /interfaces/interface[name]/state
    /oper-status
    /admin-status
    /counters
```

### Vendor-Specific Models
```
Cisco IOS-XE:
  Cisco-IOS-XE-interfaces-oper
  Cisco-IOS-XE-bgp-oper
  Cisco-IOS-XE-device-hardware-oper

Juniper:
  juniper-interfaces
  juniper-routing
```

## Subscription Configuration Patterns

### Periodic Updates (Fixed Interval)
```
Use case: Regular statistics collection
Interval: 30-60 seconds typical
Configuration:
  update-policy periodic 30000  # milliseconds

Advantages:
  - Predictable data arrival
  - Consistent processing load
  - Easy aggregation

Disadvantages:
  - Fixed overhead even if no changes
  - Potential lag for urgent events
```

### On-Change Updates (Event-Driven)
```
Use case: State transitions, rapid anomaly detection
Trigger: Data change detected
Configuration:
  update-policy on-change

Examples:
  - Interface status transitions
  - BGP neighbor state changes
  - Configuration modifications

Advantages:
  - Minimal overhead
  - Immediate notification

Disadvantages:
  - Variable traffic patterns
  - May miss rapid changes
```

### Hybrid Approach
```
Combine periodic + on-change:
- Periodic: 5-minute updates (baseline)
- On-change: Immediate for critical metrics

Configuration:
  subscription HYBRID
    sensor-group-id BASELINE 300000      # 5-min periodic
    sensor-group-id CRITICAL on-change   # Event-driven
```

## Data Processing Pipeline

### Ingestion & Normalization
```
Telemetry Stream
    ↓
Parser (Extract from gRPC/JSON)
    ↓
Enrichment (Add metadata, device info)
    ↓
Normalization (Standard format)
    ↓
Storage (Time series database)
```

### Stream Processing (Kafka Streams)
```java
StreamsBuilder builder = new StreamsBuilder();

KStream<String, String> telemetry = builder.stream("telemetry-topic");

telemetry
    .filter((key, value) -> isInterfaceMetric(value))
    .map((key, value) -> enrichMetric(key, value))
    .to("enriched-telemetry-topic");

KafkaStreams streams = new KafkaStreams(builder.build(), props);
streams.start();
```

## Performance Tuning

### Bandwidth Optimization
```
Default message size: 64KB
Typical per-device: 0.5-2 KB per second
Scale factors:
  - 100 devices: 50-200 KB/s
  - 1000 devices: 500 KB/s - 2 MB/s

Optimization:
  1. Reduce sensor path scope
  2. Increase subscription interval
  3. Use on-change for non-critical data
  4. Enable compression (if supported)
```

### Collector Resource Planning
```
CPU: 1 vCPU per 1000 devices
Memory: 2GB base + 1MB per 100 subscriptions
Network: 1 Gbps for ~500 devices (periodic 30s)

Scale testing:
  - Start with 10 devices
  - Increase by 100 per iteration
  - Monitor resource consumption
```

## Testing & Validation

### Test Data Collection
```
1. Enable single subscription
2. Generate test traffic
3. Verify data arrival
4. Monitor latency
5. Check completeness

Tools:
  - tcpdump: Monitor gRPC traffic
  - Wireshark: Analyze message structure
  - Logs: Collector and device logs
```

### Performance Validation
```bash
# Check message rates
tcpdump -i eth0 'port 5432' -c 1000 | wc -l

# Monitor latency
# Compare device timestamp vs collector receipt time
# Target: <100ms latency

# Verify message completeness
# Ensure all expected fields present
# Check data type conversions
```

## Implementation Checklist

- [ ] Verify NETCONF/RESTCONF support
- [ ] Identify YANG models to use
- [ ] Design subscription strategy
- [ ] Determine sampling intervals
- [ ] Plan collector infrastructure
- [ ] Deploy collector software
- [ ] Configure device telemetry
- [ ] Test data collection
- [ ] Build data processing pipeline
- [ ] Create monitoring dashboards
- [ ] Set up alerting
- [ ] Document procedures
- [ ] Plan scaling strategy

---

**Guide Type**: Implementation
**Technologies**: NETCONF, RESTCONF, YANG, gRPC
**Devices**: Cisco IOS-XE/XR, Juniper Junos
**Typical Timeline**: 3-4 weeks
**Last Updated**: 2025-11-19
