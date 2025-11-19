# Syslog Centralization Guide

## Planning & Design

### Architecture Assessment
```
Questions:
  1. How many devices will send syslog?
  2. What volume (messages/day)?
  3. Retention requirements?
  4. Compliance needs?
  5. Redundancy requirements?

Sizing example:
  100 devices × 1000 messages/day = 100K messages
  Average message size: 150 bytes
  Daily volume: 15 MB
  30-day retention: 450 MB
  90-day retention: 1.35 GB
```

### Transport Decision

#### UDP (Traditional)
```
Pros:
  - Low overhead
  - Minimal CPU impact
  - Works over any network

Cons:
  - Unreliable (no delivery guarantee)
  - Fire-and-forget
  - Messages can be lost

Use case:
  - High-volume logs (many devices)
  - Non-critical messages
  - Local LAN only
```

#### TCP
```
Pros:
  - Reliable delivery
  - In-order message delivery
  - Connection-oriented

Cons:
  - Higher overhead
  - Connection management
  - Firewall complexity

Use case:
  - Critical logs
  - WAN transport
  - Compliance requirements
```

#### TLS (RFC 5425)
```
Pros:
  - Encrypted transmission
  - Authenticated endpoints
  - Integrity checking

Cons:
  - Highest overhead
  - Certificate management
  - Performance impact

Use case:
  - Sensitive data
  - Security logs
  - Regulatory compliance (HIPAA, PCI)
```

## Server Setup

### Linux rsyslog Setup

#### Installation
```bash
# Ubuntu/Debian
sudo apt-get install rsyslog rsyslog-relp

# RHEL/CentOS
sudo yum install rsyslog rsyslog-relp

# Verify
rsyslogd -v
```

#### Basic Configuration
```bash
# /etc/rsyslog.conf

# Enable UDP listener
module(load="imudp")
input(type="imudp" port="514")

# Enable TCP listener
module(load="imtcp")
input(type="imtcp" port="514")

# Create directory structure
$FileCreateMode 0644
$DirCreateMode 0755
$Umask 0022

# Dynamic file naming by hostname
$Template HostLogFile,"/var/log/network/%HOSTNAME%/%PROGRAMNAME%.log"

# Log all facility local0-local7 from network devices
local0.* ?HostLogFile
local1.* ?HostLogFile
local2.* ?HostLogFile
local3.* ?HostLogFile
local4.* ?HostLogFile
local5.* ?HostLogFile
local6.* ?HostLogFile
local7.* ?HostLogFile

# Action to take at server startup
$ActionFileDefaultTemplate RSYSLOG_FileFormat

# Restart rsyslog
sudo systemctl restart rsyslog
```

#### TLS Configuration (RFC 5425)
```bash
# /etc/rsyslog.d/tls.conf

module(load="imtcp"
  StreamDriver.Name="gtls"
  StreamDriver.Mode="1"
  PermitExpiredCerts="off"
)

input(
  type="imtcp"
  port="6514"
  StreamDriver.Name="gtls"
  StreamDriver.Mode="1"
  PermitExpiredCerts="off"
  GnuTLSPriority="NORMAL"
  AuthMode="anon"
)

# Certificate paths
global(
  DefaultNetstreamDriver="gtls"
  DefaultNetstreamDriverCAFile="/etc/rsyslog/ca.crt"
  DefaultNetstreamDriverCertFile="/etc/rsyslog/server.crt"
  DefaultNetstreamDriverKeyFile="/etc/rsyslog/server.key"
)
```

### Linux syslog-ng Setup
```bash
# /etc/syslog-ng/syslog-ng.conf

source network {
  # UDP listener
  udp(ip(0.0.0.0) port(514));
  # TCP listener
  tcp(ip(0.0.0.0) port(514) max-connections(256));
};

destination network_logs {
  file("/var/log/network/${YEAR}/${MONTH}/${DAY}/$HOST/$PROGRAM.log");
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

## Device Configuration

### Cisco IOS

#### Basic Configuration
```
router(config)# logging 10.0.0.100
router(config)# logging facility local0
router(config)# logging trap informational

! Source interface for proper identification
router(config)# logging source-interface GigabitEthernet0/0

! Buffer size (local storage in case of server failure)
router(config)# logging buffer 16384 informational

! Timestamp format (recommended)
router(config)# service timestamps log datetime msec localtime

! Show configuration
router# show logging
  Syslog logging: enabled (0 messages dropped, 16 messages rate-limited, 0 flushes, 0 overruns)
  Console logging: disabled
  Buffer logging: enabled (4096 bytes)
  Logging to 10.0.0.100 (27 messages logged)
    Facility: local0
    Severity: informational
```

#### High Availability (Multiple Servers)
```
router(config)# logging 10.0.0.100 transport tcp port 514
router(config)# logging 10.0.0.101 transport tcp port 514
router(config)# logging facility local0
router(config)# logging trap informational

! Device will failover to second server if first is unreachable
```

### Juniper Junos
```
system {
    syslog {
        user * {
            any emergency;
        }
        host 10.0.0.100 {
            any informational;
            facility local0;
            port 514;
        }
        file messages {
            any notice;
            authorization info;
        }
    }
}

! Verify
show log messages | first 20
```

### Arista EOS
```
router(config)# logging host 10.0.0.100 514 transport tcp
router(config)# logging facility LOCAL0
router(config)# logging level INFO
router(config)# logging source-interface Management1

! Verify
show logging | include "Logging to"
```

## Log Processing & Analysis

### Logstash Syslog Pipeline

#### Basic Pipeline
```
input {
  tcp {
    port => 514
    type => syslog
  }
  udp {
    port => 514
    type => syslog
  }
}

filter {
  if [type] == "syslog" {
    grok {
      match => {
        "message" => "%{SYSLOGLINE}"
      }
    }

    date {
      match => [ "timestamp", "MMM d HH:mm:ss", "MMM dd HH:mm:ss" ]
      timezone => "UTC"
    }

    mutate {
      remove_field => [ "timestamp" ]
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

## Data Management

### Log Rotation

#### Rsyslog Rotation
```bash
# /etc/logrotate.d/network-syslog

/var/log/network/*/*.log {
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

#### Manual Rotation Verification
```bash
# Test rotation
logrotate -f /etc/logrotate.d/network-syslog

# Verify
ls -la /var/log/network/*/
# Should show rotated files with .1, .2, .gz extensions
```

### Storage Planning

#### Disk Space Calculation
```
Volume: 100 devices × 1000 msgs/day = 100K/day
Message size: 150 bytes average
Daily: 15 MB
Monthly: 450 MB
Yearly: 5.4 GB

With 2x replication (backup): 10.8 GB

Retention policy:
  Hot (searchable): 30 days = 450 MB
  Archive (compressed): 1 year = 5.4 GB
  Total: ~6 GB
```

### Cleanup Script
```bash
#!/bin/bash
# Cleanup old logs

LOG_DIR="/var/log/network"
RETAIN_DAYS=90

find $LOG_DIR -name "*.log*" -type f -mtime +$RETAIN_DAYS -delete
find $LOG_DIR -name "*.gz" -type f -mtime +$RETAIN_DAYS -delete

# Log cleanup
logger "Cleanup: Deleted logs older than $RETAIN_DAYS days"
```

## Monitoring & Troubleshooting

### Health Checks

#### Verify Syslog Server
```bash
# Check if listening
sudo netstat -tlnp | grep 514
# Output: tcp  0  0  0.0.0.0:514  0.0.0.0:*  LISTEN  1234/rsyslogd

# Monitor incoming logs
sudo tail -100f /var/log/network/*/syslog

# Count messages per device
find /var/log/network -type f | xargs wc -l | sort -n | tail

# Check disk usage
du -sh /var/log/network/*
```

#### Verify Device Sending
```
Device:
  router# show logging
  Syslog logging: enabled
  Logging to 10.0.0.100

Server (tail the log):
  tail -f /var/log/network/<device_name>/syslog
  [Should see new messages]

If not receiving:
  1. Verify connectivity: ping device from server
  2. Verify firewall: check ACLs
  3. Check device config: show logging
  4. Check server: netstat -uln | grep 514
  5. Monitor tcpdump: tcpdump -i eth0 'port 514'
```

## Compliance & Retention

### Archival Strategy
```
Active (30 days):
  Location: /var/log/network
  Format: Plain text (fast access)
  Retention: 30 days rolling

Archive (1 year):
  Location: /archive/network-logs
  Format: Compressed (gzip)
  Retention: 1 year

Compliance hold (7+ years):
  Location: Offline storage/tape
  Format: Compressed, signed
  Retention: Legal/regulatory requirement
```

### Immutability & Integrity
```bash
# Make logs immutable (prevent tampering)
sudo chattr +i /var/log/network/*/*log
# Only root can remove this with:
# sudo chattr -i /var/log/network/*/*log

# Create checksums for integrity verification
find /var/log/network -type f -name "*.log*" | \
  xargs sha256sum > /var/log/network.sums

# Verify integrity
sha256sum -c /var/log/network.sums
```

## Implementation Checklist

- [ ] Design syslog architecture
- [ ] Choose transport (UDP, TCP, TLS)
- [ ] Install syslog server
- [ ] Configure logging directories
- [ ] Configure devices to send syslog
- [ ] Verify log receipt
- [ ] Set up log processing (Logstash/ELK)
- [ ] Configure log rotation
- [ ] Plan storage strategy
- [ ] Set up monitoring/alerts
- [ ] Document procedures
- [ ] Configure compliance requirements
- [ ] Test failover/HA
- [ ] Train operations team

---

**Guide Type**: Implementation
**Transport Options**: UDP, TCP, TLS
**Tools**: rsyslog, syslog-ng, Logstash
**Typical Scale**: 100-10,000 devices
**Timeline**: 1-2 weeks
**Last Updated**: 2025-11-19
