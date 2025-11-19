# Network Monitoring & Observability Subskill

## Overview
Complete mastery of network monitoring, observability platforms, and performance measurement technologies for enterprise network operations.

## Core Competencies

### 1. SNMP (Simple Network Management Protocol)
- **SNMPv1, v2c, v3 configuration** - Protocol versions and backward compatibility
- **MIB (Management Information Base)** - Standard and custom MIBs, OID hierarchies
- **SNMP traps and notifications** - Event-driven monitoring, trap handling
- **Community strings and security** - Authentication, privacy, access controls
- **Polling strategies** - Interval optimization, threshold detection

### 2. NetFlow & Flow Analysis
- **NetFlow v5, v9, IPFIX** - Version differences and capabilities
- **Flow data collection** - Exporter configuration, sampling strategies
- **Traffic analysis** - Application identification, bandwidth accounting
- **Flow analytics** - Top talkers, protocol distribution, traffic patterns
- **Flow storage and analysis** - Database design, query optimization

### 3. Streaming Telemetry
- **gRPC and subscription models** - Push-based telemetry
- **Model-driven telemetry** - YANG data models, NETCONF/RESTCONF
- **Cisco Streaming Telemetry** - IOS-XE, IOS-XR platforms
- **Junos Telemetry Interface (JTI)** - Juniper implementations
- **OpenConfig and standard schemas** - Vendor-neutral models

### 4. Syslog & Event Management
- **Syslog protocol (RFC 3164/5424)** - Message format, severity levels
- **Syslog servers and aggregation** - Centralized logging infrastructure
- **Log parsing and correlation** - Structured logging, log processing
- **Event classification** - Alert severity, impact analysis
- **Log retention and archival** - Compliance, storage optimization

### 5. Packet Capture & Analysis
- **Tcpdump and WinDump** - Packet capture tools and filters
- **Wireshark analysis** - Deep packet inspection, protocol analysis
- **Display filters and capture filters** - Advanced filtering techniques
- **Packet forensics** - Evidence collection, investigation techniques
- **Payload analysis** - Content inspection, security analysis

### 6. Network KPIs & Metrics
- **Latency measurement** - RTT, jitter, MOS
- **Throughput and bandwidth** - Actual vs provisioned, saturation analysis
- **Packet loss monitoring** - Loss rate, packet error detection
- **Availability metrics** - Uptime percentage, MTBF/MTTR
- **Application performance** - Response time, transaction tracking

### 7. Observability Platforms

#### Prometheus for Network Monitoring
- **Network exporters** - SNMP exporter, network device exporters
- **Custom metrics** - Application-specific metrics, derived metrics
- **Time series storage** - Retention, compression, optimization
- **Querying and alerting** - PromQL, alert rules, routing

#### Grafana Dashboard Design
- **Network visualization** - Topology maps, flow diagrams
- **Real-time dashboards** - Auto-refresh, interactive elements
- **Dashboard templates** - Reusable components, standardization
- **Alerting integration** - Alert annotations, incident tracking

#### ELK Stack Integration
- **Logstash pipelines** - Network log processing, field extraction
- **Elasticsearch indexing** - Log storage, search optimization
- **Kibana visualization** - Log analysis, correlation searching

### 8. Advanced Monitoring Tools
- **Neteye and network automation** - Integrated monitoring platforms
- **Telegraf and Influx** - Metrics collection and time series database
- **NetBox integration** - Network IPAM and monitoring correlation
- **Splunk for network analytics** - Enterprise log and metrics platform
- **Datadog and cloud monitoring** - Cloud-native observability

### 9. Network Troubleshooting Methodology
- **Layered diagnostics** - Bottom-up and top-down approaches
- **Baseline establishment** - Historical data, anomaly detection
- **Root cause analysis** - Systematic elimination, correlation analysis
- **Performance optimization** - Bottleneck identification and resolution
- **Incident response** - Triage, escalation, documentation

### 10. Observability Best Practices
- **Instrumentation strategy** - What to monitor, sampling decisions
- **Metric design** - Cardinality management, aggregation
- **Alert tuning** - False positive reduction, alert fatigue prevention
- **Data retention** - Storage costs vs visibility tradeoffs
- **Security and privacy** - Data protection, sensitive field masking

## Reference Materials

### Key Documents
- **SNMP Monitoring Reference** - Protocol details, OID management
- **NetFlow/sFlow/IPFIX Reference** - Flow data standards
- **Streaming Telemetry Reference** - Push-based data collection
- **Syslog Reference** - Log message standards
- **Packet Capture Reference** - Capture techniques and analysis
- **Network KPIs Reference** - Metric definitions and targets
- **Monitoring Tools Comparison** - Feature matrix and selection criteria
- **Prometheus Network Monitoring** - Exporter configuration
- **Grafana Dashboards Reference** - Dashboard best practices
- **Wireshark Reference** - Protocol dissectors and analysis
- **Network Troubleshooting Tools** - Diagnostic tool reference
- **Observability Best Practices** - Industry standards

## Implementation Guides

### Configuration Guides
1. **SNMP Deployment Guide** - End-to-end SNMP setup
2. **NetFlow Implementation Guide** - NetFlow collector setup
3. **Streaming Telemetry Guide** - Telemetry configuration
4. **Network Observability Guide** - Full observability implementation
5. **ELK Stack Network Monitoring** - Log processing pipeline

### Platform Guides
6. **Prometheus & Grafana Setup** - Complete monitoring stack
7. **Packet Capture Analysis Guide** - Tcpdump and Wireshark
8. **Syslog Centralization Guide** - Log aggregation architecture
9. **Network Performance Monitoring** - Performance metrics strategy
10. **Network Alerting Guide** - Alert rule design and management

### Advanced Guides
11. **Capacity Planning Guide** - Growth projection and trending
12. **Troubleshooting Methodology** - Systematic problem-solving

## Implementation Resources

### Configuration Files
- SNMPv3 configuration templates
- NetFlow exporter configurations
- sFlow and IPFIX setups
- Streaming telemetry configs
- Prometheus/Grafana configurations
- Telegraf network monitoring configs
- ELK Stack pipeline definitions

### Automation Scripts
- SNMP monitoring and discovery scripts
- NetFlow analyzer implementations
- Packet capture automation
- Network baseline monitoring
- Syslog parsing utilities
- Network health check scripts
- Bandwidth and latency monitoring
- Wireshark filter templates
- Troubleshooting automation scripts

### Configuration Standards
- Display filter templates
- Capture filter examples
- tcpdump command reference
- Syslog format patterns

## Monitoring Architecture

### Pull-Based (SNMP)
```
NMS (Network Management System)
    ↓ SNMP GET/WALK
Device Agents (SNMP v1/v2c/v3)
    ↓ Traps
NMS Trap Receiver
```

### Push-Based (Streaming Telemetry)
```
Network Devices (Telemetry Agents)
    ↓ gRPC/UDP Streaming
Telemetry Collectors
    ↓
Time Series Database/Message Queue
    ↓
Analytics & Dashboards
```

### Flow-Based (NetFlow)
```
Network Devices (Flow Exporters)
    ↓ NetFlow v9/IPFIX
Flow Collector
    ↓
Flow Database
    ↓
Flow Analysis & Reporting
```

### Log-Based (Syslog)
```
Network Devices (Syslog Agents)
    ↓ Syslog (UDP 514 / TCP 514/601)
Syslog Server
    ↓ Logstash Processing
Elasticsearch
    ↓
Kibana/Analytics
```

## Key Technologies & Versions

### Protocol Versions
- **SNMP**: v1, v2c, v3 (current standard)
- **NetFlow**: v5, v9, IPFIX (RFC 7011)
- **Syslog**: RFC 3164 (legacy), RFC 5424 (current)
- **Telemetry**: NETCONF (RFC 6241), YANG (RFC 6020)

### Monitoring Platforms
- **Prometheus**: Time series database + alerting
- **Grafana**: Visualization layer
- **Elasticsearch + Logstash + Kibana (ELK)**: Log aggregation
- **Influx + Telegraf**: Agent-based metrics collection
- **NetBox**: IPAM and network source of truth

### Tools & Utilities
- **Tcpdump/WinDump**: Packet capture
- **Wireshark**: Interactive packet analysis
- **Neteye**: Integrated monitoring platform
- **Netmiko**: Network device automation
- **Scapy**: Packet manipulation library

## Career Path
Network monitoring and observability expertise is critical for:
- Network Operations Center (NOC) engineers
- Network architects designing observability
- DevOps engineers implementing monitoring
- Cloud platform engineers
- Security operations center (SOC) analysts

## Certification Alignment
- CCNA: Network monitoring basics
- CCNP Enterprise: Advanced monitoring
- Certified Kubernetes Administrator (CKA): Container observability
- Splunk User Certification: Log analysis
- Prometheus Certified Associate: Metrics and alerting

---

**Last Updated**: 2025-11-19
**Skill Level**: Advanced
**Status**: Complete
