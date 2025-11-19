# NetFlow Implementation Guide

## Pre-Implementation Planning

### Requirement Analysis
```
1. Assess NetFlow Support
   - Device capability (v5, v9, IPFIX)
   - Current feature level
   - Bandwidth impact estimation

2. Define Use Cases
   - Traffic analysis
   - Capacity planning
   - Security monitoring
   - Application classification

3. Plan Infrastructure
   - Collector capacity
   - Storage requirements
   - Network bandwidth for flow exports
```

### Design Considerations
```
NetFlow vs sFlow vs IPFIX:
  NetFlow v5: Legacy, fixed format, limited
  NetFlow v9: Flexible templates, extensible
  IPFIX: Standardized v9 alternative
  sFlow: Hardware sampling, low overhead

Choice factors:
  - Device support
  - Deployment scale
  - Budget constraints
  - Feature requirements
```

## Device Configuration

### Cisco IOS NetFlow v9

#### Step 1: Create Flow Exporter
```
router(config)# flow exporter COLLECTOR_PRIMARY
router(config-flow-exporter)# destination 10.0.0.100
router(config-flow-exporter)# source GigabitEthernet0/0
router(config-flow-exporter)# transport udp 2055
router(config-flow-exporter)# export-protocol netflow-v9
router(config-flow-exporter)# template data timeout 60
router(config-flow-exporter)# exit

! Optional: Secondary collector for redundancy
router(config)# flow exporter COLLECTOR_SECONDARY
router(config-flow-exporter)# destination 10.0.0.101
router(config-flow-exporter)# source GigabitEthernet0/0
router(config-flow-exporter)# transport udp 2055
router(config-flow-exporter)# export-protocol netflow-v9
```

#### Step 2: Create Flow Monitor
```
router(config)# flow monitor NETWORK_MONITOR
router(config-flow-monitor)# exporter COLLECTOR_PRIMARY
router(config-flow-monitor)# exporter COLLECTOR_SECONDARY
router(config-flow-monitor)# record netflow ipv4 original-input
router(config-flow-monitor)# cache timeout active 300
router(config-flow-monitor)# cache timeout inactive 15
router(config-flow-monitor)# cache timeout update-timeout 60
router(config-flow-monitor)# exit
```

#### Step 3: Apply to Interfaces
```
! Apply to all monitored interfaces
router(config)# interface GigabitEthernet0/0
router(config-if)# ip flow monitor NETWORK_MONITOR input
router(config-if)# ip flow monitor NETWORK_MONITOR output
router(config-if)# exit

! Repeat for all interfaces:
! - Internet uplink
! - Data center uplink
! - Branch site links
! - Internal backbone
```

#### Step 4: Verify Configuration
```
router# show flow exporter
router# show flow monitor NETWORK_MONITOR
router# show ip flow interfaces
router# show flow cache monitor NETWORK_MONITOR
  Exporter: COLLECTOR_PRIMARY
  Flows: 45230
  Cache size: 1000000
  Cache utilization: 4.5%
```

### Cisco IOS-XE NetFlow with Sampling
```
router(config)# flow monitor SAMPLED_MONITOR
router(config-flow-monitor)# exporter COLLECTOR_PRIMARY
router(config-flow-monitor)# record netflow ipv4 original-input
router(config-flow-monitor)# sampler RANDOM_SAMPLE
router(config-flow-monitor)# exit

router(config)# sampler RANDOM_SAMPLE
router(config-sampler)# mode random 1 out-of 1000
router(config-sampler)# exit

! Apply sampled monitoring to high-speed interfaces
router(config)# interface TenGigabitEthernet0/0
router(config-if)# ip flow monitor SAMPLED_MONITOR sampler RANDOM_SAMPLE input
router(config-if)# ip flow monitor SAMPLED_MONITOR sampler RANDOM_SAMPLE output
```

### Juniper Junos NetFlow

#### Configuration
```
system {
    syslog {
        file messages {
            any notice;
        }
    }
}

forwarding-options {
    sampling {
        input {
            rate 1000;
            run-length 0;
        }
    }
    port-mirroring {
        input {
            rate 1000;
        }
        output {
            interface ge-0/0/0.0 family inet;
        }
    }
}

services {
    analytics {
        export {
            profile NETFLOW_EXPORTER {
                local-address 192.168.1.1;
                local-port 4739;
                target-address 10.0.0.100;
                target-port 2055;
                target-format netflow-v9;
                target-version 9;
                flow-active-timeout 300;
                flow-inactive-timeout 15;
            }
        }
    }
}
```

### Arista EOS NetFlow

#### Configuration
```
router(config)# flow-spec ipv4
router(config)# flow-spec ipv6

router(config)# flow exporter NETFLOW_COLLECTOR
router(config-flow-exporter)# ipv4 address 10.0.0.100
router(config-flow-exporter)# transport udp 2055
router(config-flow-exporter)# source-interface GigabitEthernet1/1
router(config-flow-exporter)# template export timeout 300

router(config)# flow monitor NETWORK_MONITOR
router(config-flow-monitor)# exporter NETFLOW_COLLECTOR

router(config)# interface GigabitEthernet1/1
router(config-if)# flow monitor NETWORK_MONITOR input

router(config)# ip flow ingress-sampler SAMPLED 1 out-of 1000
router(config-if)# ip flow ingress-sampler SAMPLED
```

## Collector Setup

### NetFlow Collector Installation

#### Open Source Option: nProbe
```bash
# Download
wget https://releases.ntop.org/nprobe/nProbe-10.4.231022.tar.gz
tar xzf nProbe-10.4.231022.tar.gz
cd nprobe

# Configure
./nprobe -i eth0 -n "10.0.0.100:2055" -w 3000 -f "json" -o /var/log/nprobe/flows.json

# Run as daemon
sudo /path/to/nprobe -i eth0 -n "10.0.0.100:2055" \
  -d "/var/log/nprobe" \
  -w 3000 \
  -D 500000

# Verify
netstat -uln | grep 2055
```

#### Elasticsearch + Kibana Setup

##### Logstash Pipeline
```
input {
  udp {
    host => "0.0.0.0"
    port => 2055
    codec => netflow {
      definitions => "/etc/logstash/netflow-definitions.yml"
      cache_ttl => 4000
      versions => [9]
    }
  }
}

filter {
  # Extract flow information
  if [netflow][ipv4_src_addr] {
    mutate {
      add_field => { "[@metadata][index_name]" => "netflow-%{+YYYY.MM.dd}" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "%{[@metadata][index_name]}"
  }
}
```

##### Start Logstash
```bash
# Start logstash with netflow config
sudo /usr/share/logstash/bin/logstash \
  -f /etc/logstash/netflow.conf

# Verify UDP listener
netstat -uln | grep 2055

# Check Elasticsearch indices
curl http://localhost:9200/_cat/indices | grep netflow
```

### Commercial Collector Options
```
SolarWinds NetFlow Analyzer:
  - Purpose-built NetFlow analysis
  - Integrated dashboards
  - Flow-based alerting

Cisco Prime Infrastructure:
  - Cisco-native platform
  - Policy management
  - Integrated network automation

ntop Enterprise:
  - Commercial nProbe support
  - Advanced analytics
  - Professional services
```

## Storage & Retention

### Disk Space Calculation
```
Flow Size:
  NetFlow v5: 48 bytes (fixed)
  NetFlow v9: 50-200 bytes (variable)
  IPFIX: Similar to v9

Example Calculation:
  Flows/second: 1000
  Average record size: 100 bytes
  Daily volume: 1000 × 86400 × 100 = 8.6 GB
  Monthly: 8.6 GB × 30 = 258 GB
  Yearly: 258 GB × 12 = 3,096 GB (3 TB)

Retention Planning:
  Hot storage (real-time analysis): 7 days = 60 GB
  Warm storage (trending): 1 month = 250 GB
  Cold storage (archive): 1 year = 3 TB
```

### Database Configuration

#### Elasticsearch Index Management
```bash
# Create index template
PUT /_index_template/netflow
{
  "index_patterns": ["netflow-*"],
  "template": {
    "settings": {
      "index": {
        "number_of_shards": 3,
        "number_of_replicas": 1,
        "refresh_interval": "30s"
      }
    },
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "netflow": {
          "properties": {
            "ipv4_src_addr": { "type": "ip" },
            "ipv4_dst_addr": { "type": "ip" },
            "ipv4_src_port": { "type": "integer" },
            "ipv4_dst_port": { "type": "integer" },
            "in_bytes": { "type": "long" },
            "in_pkts": { "type": "long" }
          }
        }
      }
    }
  },
  "priority": 100
}
```

#### Index Lifecycle Management (ILM)
```bash
# Create ILM policy for hot/warm/delete
PUT /_ilm/policy/netflow-policy
{
  "policy": "netflow-policy",
  "phases": {
    "hot": {
      "min_age": "0d",
      "actions": {
        "rollover": {
          "max_primary_shard_size": "50GB"
        }
      }
    },
    "warm": {
      "min_age": "7d",
      "actions": {
        "set_priority": {
          "priority": 50
        }
      }
    },
    "delete": {
      "min_age": "90d",
      "actions": {
        "delete": {}
      }
    }
  }
}
```

## Validation & Testing

### Flow Verification

#### Generate Test Traffic
```bash
# Create synthetic traffic between hosts
iperf3 -s &
iperf3 -c target_host -t 60 -i 10

# Monitor NetFlow exports
tcpdump -i eth0 'udp port 2055' -A

# Check flows in collector
# Elasticsearch query:
GET netflow-*/_search
{
  "query": {
    "range": {
      "@timestamp": { "gte": "now-5m" }
    }
  }
}
```

#### Validate Flow Data
```bash
# SSH to device
show ip flow top-talkers

# Expected output:
# SRC IP             DST IP             PROTO SRC PORT DST PORT PKT  BYTES
# 192.168.1.50      10.0.0.100        TCP   5432     2055     10K  1.2M

# Check flow cache utilization
show flow cache monitor NETWORK_MONITOR
```

### Performance Testing

#### Load Testing
```bash
# Use tools like Spirent or IXIA to generate:
# - Varying flow rates
# - Packet size distribution
# - Concurrent flows

Baseline Testing:
  1. Normal traffic (8 hours)
  2. Peak traffic (simulate 3x normal)
  3. Attack traffic (DDoS patterns)
  4. Monitor flow export overhead
```

## Monitoring & Troubleshooting

### Flow Export Health

#### Device Perspective
```
! Cisco IOS
show ip flow cache monitor NETWORK_MONITOR
  Active flows:  45230
  Cache entries used:  45230/1000000
  Exporter packets sent:  523400
  Exporter packets dropped: 0
  Sample rate: 1 in 1000

! Red flags:
# - High dropped count
# - Cache utilization > 80%
# - Sample rate too aggressive
```

#### Collector Perspective
```bash
# Monitor incoming flows
netstat -u -s | grep received

# Check Elasticsearch
curl http://localhost:9200/_cat/indices | grep netflow
curl http://localhost:9200/netflow-*/_count

# Monitor lag
# Compare: Device last flow export time vs collector receipt time
# Lag > 5 seconds indicates network/collector issues
```

### Common Issues

#### No Flows Arriving
```
1. Verify interface is up
   show interfaces GigabitEthernet0/0

2. Verify flow monitor is applied
   show ip flow interfaces

3. Verify exporter connectivity
   ping <collector_ip>
   traceroute <collector_ip>

4. Check firewall rules
   Allow UDP 2055 from device to collector

5. Monitor device CPU
   show processes cpu | include netflow
   # If high, reduce sampling rate or polling interval
```

#### Incomplete Flow Data
```
Issues:
  - Missing destination AS number
  - Missing application identification
  - Incomplete bidirectional flow

Solutions:
  - Verify device config exports required fields
  - Check collector is parsing all fields
  - Enable application tracking (if supported)
  - Review template definitions
```

## Implementation Checklist

- [ ] Verify NetFlow support on devices
- [ ] Plan flow export sampling rate
- [ ] Design collector infrastructure
- [ ] Size storage requirements
- [ ] Configure device NetFlow exporters
- [ ] Deploy collector software
- [ ] Configure database storage
- [ ] Test flow export
- [ ] Generate sample traffic
- [ ] Validate flow data accuracy
- [ ] Create dashboards for flow analysis
- [ ] Set up alerting rules
- [ ] Document procedures
- [ ] Train operations team

---

**Guide Type**: Implementation
**Technologies**: NetFlow v5, NetFlow v9, IPFIX
**Typical Scale**: 100-1000s of devices
**Timeline**: 2-3 weeks
**Last Updated**: 2025-11-19
