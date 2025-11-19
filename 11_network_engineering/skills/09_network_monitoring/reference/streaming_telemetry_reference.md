# Streaming Telemetry Reference

## Overview
Streaming telemetry delivers network device data via push-based subscriptions in near real-time, enabling faster detection and response compared to traditional polling.

## Core Concepts

### Push vs Pull
```
Pull Model (SNMP):
NMS → Query → Device (latency, polling interval)

Push Model (Telemetry):
Device → Stream → Collector (immediate, continuous)
```

### Subscription Model

#### On-Change Subscription
- Report data only when value changes
- Reduces network overhead
- Example: Interface status change

#### Periodic Subscription
- Report data at fixed intervals
- Predictable traffic patterns
- Suitable for metrics monitoring

#### Event-Driven Subscription
- Report on specific events
- High-priority notifications
- Example: Critical threshold exceeded

## YANG Data Model

### YANG Structure
```
module ietf-interfaces {
  namespace "urn:ietf:params:xml:ns:yang:ietf-interfaces";
  prefix if;

  container interfaces {
    list interface {
      key "name";
      leaf name {
        type string;
      }
      leaf enabled {
        type boolean;
      }
      leaf mtu {
        type uint16;
      }
      container statistics {
        leaf in-octets {
          type yang:counter64;
        }
      }
    }
  }
}
```

### Standard YANG Modules
- **ietf-interfaces**: Interface definitions
- **ietf-ip**: IP protocol configuration
- **ietf-routing**: Routing configuration
- **openconfig-interfaces**: OpenConfig interface model
- **openconfig-bgp**: OpenConfig BGP model

### Vendor Extensions
- **cisco-ios-xe-bgp**: Cisco BGP extensions
- **junos-conf**: Juniper configuration model
- **arista-eapi**: Arista API model

## NETCONF/RESTCONF

### NETCONF (RFC 6241)

#### Protocol Details
- **Port**: 830 (standard), 22 (SSH)
- **Transport**: SSH (RFC 6242)
- **RPC Model**: Request/Reply
- **Encoding**: XML

#### Basic Operations
```
<rpc message-id="1">
  <get-config>
    <source>
      <running/>
    </source>
  </get-config>
</rpc>
```

#### RPC Methods
- **get-config**: Retrieve configuration
- **edit-config**: Modify configuration
- **copy-config**: Copy configuration
- **delete-config**: Delete configuration
- **lock/unlock**: Configuration locking
- **close-session**: Terminate session

### RESTCONF (RFC 8040)

#### Protocol Details
- **Port**: 443 (HTTPS)
- **HTTP Method Mapping**:
  - GET → retrieve data
  - POST → create resource
  - PUT → replace resource
  - DELETE → remove resource
  - PATCH → modify resource
- **Content Types**: JSON, XML

#### REST Operations
```
GET /restconf/data/ietf-interfaces:interfaces
POST /restconf/data/ietf-interfaces:interfaces/interface
PUT /restconf/data/ietf-interfaces:interfaces/interface=eth0
DELETE /restconf/data/ietf-interfaces:interfaces/interface=eth0
PATCH /restconf/data/ietf-interfaces:interfaces/interface=eth0
```

## Cisco Streaming Telemetry

### IOS-XE Telemetry

#### Subscription Configuration
```
telemetry ietf subscription subscription-id 101
 stream NETCONF-YANG
 filter xpath /ietf-interfaces:interfaces/interface/statistics
 update-policy on-change
 receiver ip address 10.0.0.100 5432
```

#### Sensor Groups
```
telemetry model-driven
 sensor-group INTERFACE_STATS
  sensor-path ietf-interfaces:interfaces/interface/statistics
  sample-interval 30000
```

#### Subscriptions
```
telemetry model-driven
 subscription INTERFACE_SUB 101
  sensor-group-id INTERFACE_STATS 100
  destination-id COLLECTOR1
```

#### Destinations
```
telemetry model-driven
 destination-group COLLECTOR1
  address family ipv4 10.0.0.100 port 5432
  encoding self-describing-gpb
  transport grpc
```

### IOS-XR Telemetry

#### Configuration
```
telemetry model-driven
 destination-group COLLECTOR
  address family ipv4 10.0.0.100 port 5432
  encoding self-describing-gpb
  transport grpc
  !
 !
 sensor-group STATS
  sensor-path Cisco-IOS-XR-infra-statsd-oper:infra-statistics
  sensor-path openconfig-interfaces:interfaces
  !
 !
 subscription STREAM1
  sensor-group-id STATS 100
  destination-id COLLECTOR
  !
```

## Juniper Telemetry Interface (JTI)

### Configuration

#### Sensor Configuration
```
system syslog {
    file messages {
        any notice;
    }
}

system telemetry {
    metric-server {
        192.168.1.1 {
            port 50000;
            local-address 192.168.1.2;
        }
    }
}
```

#### Sensor Paths
```
/interfaces/interface/state/statistics
/routing/route-views/route-view/routes/route
/openconfig-interfaces:interfaces
/openconfig-bgp:bgp/neighbors
```

## OpenConfig

### OpenConfig Models
- **openconfig-interfaces**: Interface management
- **openconfig-network-instance**: VRF/instance definitions
- **openconfig-bgp**: BGP configuration
- **openconfig-isis**: ISIS configuration
- **openconfig-ospf**: OSPF configuration
- **openconfig-acl**: Access control lists
- **openconfig-qos**: Quality of service

### OpenConfig Philosophy
- Vendor-agnostic models
- Configuration + operational state
- Hierarchical structure
- Community-driven development

## Data Encoding

### Protocol Buffers (gRPC)
```
message Interface {
  string name = 1;
  uint64 ifindex = 2;
  bool enabled = 3;
  uint64 mtu = 4;
  Statistics stats = 5;
}

message Statistics {
  uint64 in_octets = 1;
  uint64 in_errors = 2;
  uint64 out_octets = 3;
}
```

### GPB (Self-Describing GPB)
- Self-describing: Schema included in data
- Binary encoding: Efficient transmission
- Type information: Data interpretation

### JSON Encoding
```json
{
  "ietf-interfaces:interfaces": {
    "interface": [
      {
        "name": "eth0",
        "enabled": true,
        "mtu": 1500,
        "statistics": {
          "in-octets": 1024000,
          "in-errors": 0,
          "out-octets": 512000
        }
      }
    ]
  }
}
```

## Collector Architecture

### Collector Components
```
Telemetry Stream (gRPC/UDP)
    ↓
Receiver/Parser
    ↓
Data Processor
    ↓
Database/Time Series Storage
    ↓
Analytics/Visualization
```

### Popular Collectors
- **Telegraf**: Universal metrics agent
- **TD Agent (Fluentd)**: Flexible collection
- **Logstash**: Event processing pipeline
- **Kafka**: Distributed streaming platform
- **Custom gRPC Receivers**: Purpose-built

## Performance Characteristics

### Bandwidth Efficiency
- **gRPC/TLS**: ~500 bytes/second per device
- **JSON/HTTP**: ~2KB/second per device
- **Sampling**: Reduces update frequency
- **Compression**: Optional for large payloads

### Latency
- **On-Change**: Milliseconds to seconds
- **Periodic**: 30-60 second intervals typical
- **Transport**: <100ms typical latency

### Scalability
- **Devices**: 100-10,000s with proper infrastructure
- **Sampling Rate**: Control via subscription parameters
- **Retention**: Database dependent (24 hours to years)

## Use Cases

### Real-Time Monitoring
- Interface state changes
- BGP neighbor transitions
- Optical power fluctuations
- Temperature exceedances

### Performance Analytics
- Interface counters trending
- CPU/memory utilization
- Packet loss detection
- Latency measurement

### Event Driven Automation
- Intent-based networking
- Automated remediation
- Policy enforcement
- Resource optimization

## Implementation Patterns

### Pipeline Architecture
```
Device Fleet
    ↓ (Streaming Telemetry)
Kafka Cluster
    ↓
Consumer 1 → Time Series DB (Prometheus/InfluxDB)
Consumer 2 → Event Store (Elasticsearch)
Consumer 3 → Stream Processing (Flink/Spark)
```

### High Availability
- Multiple collectors
- Load balancing
- Automatic failover
- Data replication

## Implementation Checklist

- [ ] Verify NETCONF/RESTCONF support
- [ ] Plan YANG data models
- [ ] Design subscription strategy
- [ ] Size collector infrastructure
- [ ] Configure transport encryption
- [ ] Deploy telemetry agents
- [ ] Build data pipelines
- [ ] Create dashboards
- [ ] Establish alerting rules
- [ ] Test failover scenarios
- [ ] Document access controls
- [ ] Plan data retention

---

**Reference Type**: Modern Telemetry Standards
**Primary Use**: Real-time device monitoring
**Standards**: RFC 6241 (NETCONF), RFC 8040 (RESTCONF)
**Last Updated**: 2025-11-19
