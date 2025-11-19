# NetFlow, sFlow, and IPFIX Reference

## NetFlow Overview

### NetFlow Versions

#### NetFlow v5
- **Format**: Fixed 30-byte flow record
- **Scalability**: Limited cardinality
- **Supported**: Cisco IOS, most legacy devices
- **Data**: Source/Dest IP, ports, protocol, counters
- **Export Interval**: Typically 1-5 minute aggregation
- **Limitations**: No extensibility, 5-tuple only

#### NetFlow v9
- **Format**: Variable-length templates
- **Scalability**: Unlimited fields via templates
- **Flexibility**: Custom information elements
- **Introduction**: Cisco IOS 12.0(2)T
- **Templates**: Periodically sent, define schema
- **Support**: Most modern Cisco devices

#### IPFIX (IP Flow Information Export)
- **Standard**: RFC 7011, RFC 7012 (information model)
- **Evolution**: NetFlow v9 based but standardized
- **Advantages**: Vendor-neutral, standardized fields
- **Extensibility**: Private enterprise numbers (PENs)
- **Transport**: TCP, UDP, SCTP
- **Current**: IANA standards track

### Flow Record Components

#### Tuple Fields
```
Source IP Address
Destination IP Address
IP Protocol (TCP, UDP, etc.)
Transport Source Port
Transport Destination Port
Input Interface (SNMP ifIndex)
```

#### Counter Fields
```
Byte Count (Cumulative)
Packet Count (Cumulative)
Timestamp Fields
  - sysUptime at Start
  - sysUptime at End
  - Actual Flow Start Time (IPFIX)
  - Actual Flow End Time (IPFIX)
```

#### Optional Fields (v9/IPFIX)
```
Source/Destination AS Number
Source/Destination Prefix Length
Output Interface
TCP Flags (Cumulative)
IP TOS/DSCP
Vlan IDs (802.1Q)
MAC Addresses
Application Layer Protocol
Flow State
Flow Direction
```

## NetFlow Collection

### Collector Configuration

#### Exporter Configuration (Cisco IOS)
```
flow exporter COLLECTOR_1
 destination 10.0.0.100
 source Ethernet 0/0
 transport udp 2055
 template data timeout 60
 export-protocol netflow-v9
```

#### Flow Monitor
```
flow monitor NETWORK_MONITOR
 exporter COLLECTOR_1
 record netflow ipv4 original-input
 cache timeout active 60
 cache timeout inactive 15
```

#### Interface Application
```
interface GigabitEthernet 0/0
 ip flow monitor NETWORK_MONITOR input
 ip flow monitor NETWORK_MONITOR output
```

### Flow Caching

#### Cache Parameters
- **Active Timeout**: 30 minutes (default)
  - Forces flow export after timeout
  - Even if still active
- **Inactive Timeout**: 15 seconds (default)
  - Exports flow if no activity
  - Recovers cache memory
- **Cache Size**: Device dependent
  - Typical: 100K - 1M flows
  - Overflow: Drop or degrade

### Sampling Strategies

#### Fixed Sampling (1:N)
```
ip flow-cache entries 1000000
ip flow ingress-sampler sample 1 out of 100
```

#### Distributed Sampling
- Sample at line-rate (minimal CPU)
- Still see accurate flow distribution
- Reduces export overhead
- Typical ratio: 1:100 to 1:1000

#### Adaptive Sampling
- Adjust rate based on cache utilization
- Maintain accuracy as load varies
- More complex implementation

## sFlow (Sampling Flow)

### Overview
- **RFC 3176**: Standardized sFlow specification
- **Approach**: Packet-based statistical sampling
- **Deployment**: Hardware-based, line-rate sampling
- **Overhead**: Minimal CPU impact

### Collection Method
```
Agent (sFlow enabled device)
  ↓ Random packet sampling
  ↓ Flow state tracking
  ↓ Interface counters
  ↓ UDP port 6343 (default)
Collector
```

### sFlow Packet Format
```
sFlow Datagram
├── Sysem Records
│   ├── Generic interface counters
│   ├── Ethernet interface counters
│   ├── Token Ring counters
│   └── VLan counters
├── Flow Samples
│   ├── Raw packet data
│   └── Extracted fields
└── Counter Samples
    └── Interface statistics
```

### Sampling Rate
- **Typical**: 1:512 to 1:4096
- **Port Speed**: Drive sampling rate
  - 1Gbps: 1:1000
  - 10Gbps: 1:10000
  - 100Gbps: 1:100000

## IPFIX Details

### Information Elements
```
Standard IEs (0-383): IANA-defined
Reverse IEs (16384-16767): Bidirectional flow info
Enterprise-specific (8000+): Vendor extensions
```

### Common Information Elements
```
sourceIPv4Address (8)
sourceIPv6Address (27)
destinationIPv4Address (12)
destinationIPv6Address (28)
ipProtocolVersion (60)
protocolIdentifier (4)
sourceTransportPort (7)
destinationTransportPort (11)
flowStartSysUpTime (22)
flowEndSysUpTime (21)
inBytes (1)
inPackets (2)
inInterface (10)
outInterface (14)
```

### Template Management
```
IPFIX Message
├── Message Header
│   ├── IPFIX Version (10)
│   ├── Length
│   ├── Timestamp (seconds since epoch)
│   └── Sequence Number
├── Template Set (ID 2)
│   └── Template Records
└── Data Set
    └── Flow Records
```

## Performance Metrics

### Flow Export Rate
```
Flows/second = (Packets/second × Sampling Ratio)
Example: 1M pps, 1:1000 sample = 1000 flows/s
```

### Bandwidth Overhead
```
Overhead = Flow Export Rate × Record Size
NetFlow v5: 48 bytes overhead
NetFlow v9: 20-200 bytes (variable)
IPFIX: Similar to v9

Example: 1000 flows/s × 50 bytes = 400 Kbps
```

### CPU Impact
- **sFlow**: Minimal (<1%)
- **NetFlow v5**: Moderate (2-5%)
- **NetFlow v9**: Low (1-3%)
- **IPFIX**: Low (1-3%)

## Use Cases

### Traffic Analysis
- Identify top talkers
- Track application bandwidth
- Detect traffic spikes
- Capacity planning

### Network Troubleshooting
- Path analysis
- Latency tracking
- Packet loss detection
- Congestion identification

### Security Monitoring
- DDoS detection
- Anomaly detection
- Policy enforcement
- Threat hunting

### Billing & Chargeback
- Usage accounting
- Bandwidth allocation
- Service metering
- Customer billing

## Tools & Platforms

### Collectors
- **Cisco NetFlow Collector**: Legacy, limited
- **sFlow-RT**: Open-source, real-time
- **nProbe**: NetFlow/sFlow/IPFIX collector
- **FlowVisor**: Virtual network flows

### Analysis Platforms
- **Elasticsearch + Kibana**: Log-based flow storage
- **Splunk**: Enterprise flow analytics
- **Traffic Analytics**: Cloud platforms
- **Grafana**: With database backend

### Flow Databases
- **InfluxDB**: Time series for flows
- **Cassandra**: Distributed flow storage
- **Clickhouse**: Analytics database
- **MySQL/PostgreSQL**: Traditional RDBMS

## Implementation Checklist

- [ ] Verify NetFlow/sFlow support on devices
- [ ] Choose flow standard (v5, v9, or IPFIX)
- [ ] Size collector infrastructure
- [ ] Configure sampling rate
- [ ] Deploy collector platform
- [ ] Configure device exporters
- [ ] Validate flow export
- [ ] Create flow templates
- [ ] Establish data retention
- [ ] Build analysis dashboards
- [ ] Set up alerting rules
- [ ] Document retention policies

---

**Reference Type**: Flow Collection Standards
**Primary Use**: Traffic analysis, capacity planning
**Current Standard**: IPFIX (RFC 7011)
**Last Updated**: 2025-11-19
