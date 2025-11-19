# Syslog Reference

## Overview
Syslog is the standard protocol for network device logging, providing centralized event collection and management for network troubleshooting and compliance.

## Syslog Protocol Versions

### Syslog (RFC 3164) - Legacy

#### Message Format
```
<PRI>HEADER MESSAGE

Priority = Facility * 8 + Severity
<PRI> = <Facility * 8 + Severity>

Example: <34>Oct  5 16:33:23 192.168.1.100 %LINK-3-UPDOWN
```

#### Facilities
```
0 = kernel messages
1 = user-level messages
2 = mail system
3 = system daemons
4 = security/authorization messages
5 = syslogd internal messages
16 = local use 0 (local0)
17 = local use 1 (local1)
...
23 = local use 7 (local7)
```

#### Severity Levels
```
0 = Emergency (system is unusable)
1 = Alert (action must be taken immediately)
2 = Critical (critical conditions)
3 = Error (error conditions)
4 = Warning (warning conditions)
5 = Notice (normal but significant condition)
6 = Informational (informational messages)
7 = Debug (debug-level messages)
```

#### Issues
- Timestamp ambiguity (no year/timezone)
- IP address not in standard format
- No standardized structure
- Free-form message content

### Syslog (RFC 5424) - Current Standard

#### Message Format
```
<PRI>TIMESTAMP HOSTNAME TAG PID MSGID STRUCTDATA MSG

Example:
<34>2025-11-19T10:15:23.456+00:00 router01 LINK-3-UPDOWN
  1234 - [NETCONF@32473 ifName="Gi0/0/0" severity="warning"]
  Interface up
```

#### New Features
- RFC 3339 timestamp format with timezone
- Structured data (STRUCTURED-DATA)
- Message ID field
- Process ID field
- Enterprise-specific fields

#### Structured Data Format
```
[SDID@enterpriseNumber field1="value1" field2="value2"]
[NETCONF@32473 ifName="eth0" severity="warn"]
[EXAMPLESD@32473 eventID="1234" eventName="interface_up"]
```

## Syslog Transport

### UDP Transport (RFC 3164)
- **Port**: 514 (default)
- **Reliability**: Unreliable (fire-and-forget)
- **Advantages**: Low overhead, minimal CPU
- **Disadvantages**: Message loss possible
- **Use Case**: Legacy devices, high-volume logs

### TCP Transport (RFC 5424)
- **Port**: 514 (standard), 601 (IANA assigned)
- **Reliability**: Connection-oriented, delivery guaranteed
- **Format**: Octet counting for message delimitation
- **Advantages**: Guaranteed delivery, ordered messages
- **Disadvantages**: Higher overhead, connection management

### TLS/SSL Transport (RFC 5425)
- **Port**: 6514 (IANA assigned)
- **Encryption**: TLS 1.2+ recommended
- **Authentication**: Client and server certificates
- **Advantages**: Confidentiality, integrity, authenticity
- **Use Case**: Secure syslog transmission

## Syslog Message Examples

### Interface State Change
```
<34>2025-11-19T10:15:23.456+00:00 router01 LINK 3 -
  [DEVICE@32473 ifName="GigabitEthernet0/0/0" status="up"]
  Interface GigabitEthernet0/0/0 changed state to up
```

### Authentication Failure
```
<31>2025-11-19T10:16:45.789+00:00 router01 SNMP 567 -
  [SECURITY@32473 type="authFail" source="192.168.1.50"]
  SNMP authentication failure from 192.168.1.50
```

### BGP Neighbor Change
```
<30>2025-11-19T10:17:12.321+00:00 router01 BGP 891 -
  [ROUTING@32473 neighbor="192.168.1.1" status="down"]
  BGP neighbor 192.168.1.1 down
```

### CPU Threshold
```
<28>2025-11-19T10:18:33.654+00:00 router01 SYSLOG 234 -
  [THRESHOLD@32473 resource="cpu" current="92%" threshold="80%"]
  CPU utilization 92% exceeds threshold of 80%
```

## Syslog Server Setup

### Linux Syslog-ng

#### Configuration
```
# /etc/syslog-ng/syslog-ng.conf

source network {
  udp(ip(0.0.0.0) port(514));
  tcp(ip(0.0.0.0) port(514) max-connections(256));
};

destination network_logs {
  file("/var/log/network/${YEAR}/${MONTH}/${DAY}/$HOST.log");
};

filter network_only {
  facility(local0..local7);
};

log {
  source(network);
  filter(network_only);
  destination(network_logs);
};
```

### Linux Rsyslog

#### Configuration
```
# /etc/rsyslog.conf

# UDP listener
module(load="imudp")
input(type="imudp" port="514")

# TCP listener
module(load="imtcp")
input(type="imtcp" port="514")

# Dynamic log filename
$FileCreateMode 0644
$DirCreateMode 0755
$Template DynamicFile,"/var/log/network/%HOSTNAME%/%PROGRAMNAME%.log"

# Log all facility local0-local7
local0.* ?DynamicFile
local1.* ?DynamicFile
```

## Syslog Collection Architecture

### Single Server
```
Devices -----> Syslog Server
                  └─ Log Files
```

### High Availability
```
Devices -----> Syslog Server 1 ----┐
            └─> Syslog Server 2 ----├──> Centralized Storage
                                    ↓
                            Shared NFS/GFS
```

### Log Aggregation Pipeline
```
Devices
    ↓ (Syslog: UDP/TCP/TLS)
Syslog Servers
    ↓ (Log rotation)
Log Files
    ↓ (Logstash processing)
Elasticsearch
    ↓ (Kibana visualization)
Dashboards & Alerts
```

## Log Processing & Analysis

### Logstash Pipeline
```
input {
  udp {
    host => "0.0.0.0"
    port => 514
    codec => "plain"
  }
}

filter {
  if [type] == "syslog" {
    grok {
      match => { "message" => "%{SYSLOGLINE}" }
    }

    date {
      match => [ "timestamp", "MMM  d HH:mm:ss", "MMM dd HH:mm:ss" ]
    }

    if [message] =~ /LINK.*UPDOWN/ {
      mutate { add_tag => [ "interface_change" ] }
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "network-logs-%{+YYYY.MM.dd}"
  }
}
```

## Device Configuration Examples

### Cisco IOS

#### Basic Configuration
```
logging 10.0.0.100
logging facility local0
logging trap informational
logging source-interface GigabitEthernet0/0
logging buffer 8192 informational
logging console informational
```

#### Advanced Configuration
```
logging host 10.0.0.100 transport tcp port 514
logging host 10.0.0.101 transport tcp port 514
logging source-interface GigabitEthernet0/0
logging facility local0

! Buffer for local logging
logging buffer 16384 debugging

! Console logging
logging console critical

! Timestamp format
service timestamps log datetime msec localtime
```

### Juniper Junos

#### Configuration
```
system {
    syslog {
        user * {
            any emergency;
        }
        host 10.0.0.100 {
            any informational;
            facility local0;
        }
        file messages {
            any notice;
            authorization info;
        }
    }
}
```

### Arista EOS

#### Configuration
```
logging host 10.0.0.100
logging facility LOCAL0
logging level INFO
logging source-interface Management1
logging buffered 4096 informational
```

## Log Retention & Management

### Disk Space Planning
```
Average syslog message size: ~150 bytes
Devices: 100
Messages/device/day: 1000-10000

Daily volume:
100 devices × 5000 msgs × 150 bytes = 75 MB
Yearly retention: 75 MB × 365 = 27.4 GB
```

### Log Rotation
```
# /etc/logrotate.d/network-logs

/var/log/network/*.log {
    daily
    rotate 90
    compress
    delaycompress
    missingok
    notifempty
    create 0644 syslog syslog
    postrotate
        /usr/lib/rsyslog/rsyslog-rotate
    endscript
}
```

## Syslog Use Cases

### Troubleshooting
- Device startup/shutdown events
- Interface state changes
- Configuration changes
- Error conditions

### Compliance
- User authentication logs
- Configuration modification logs
- System access logs
- Security events

### Alerting
- Critical errors
- Threshold exceedances
- Device unreachability
- Protocol state changes

### Trending
- Event frequency analysis
- Error rate tracking
- Configuration change history
- System stability metrics

## Implementation Checklist

- [ ] Design syslog infrastructure
- [ ] Choose transport (UDP, TCP, TLS)
- [ ] Plan log retention
- [ ] Size storage requirements
- [ ] Configure syslog servers
- [ ] Deploy collector agents
- [ ] Test device logging
- [ ] Configure log parsing
- [ ] Create dashboards
- [ ] Set up alerting
- [ ] Document log format
- [ ] Establish backup procedures

---

**Reference Type**: Logging Protocol Standards
**Primary Use**: Device event collection and analysis
**Current Standard**: RFC 5424 with RFC 5425 (TLS)
**Last Updated**: 2025-11-19
