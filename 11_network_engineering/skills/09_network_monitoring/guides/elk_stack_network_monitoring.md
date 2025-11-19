# ELK Stack Network Monitoring Guide

## ELK Stack Overview

### Architecture
```
Devices (Syslog)
    ↓ (UDP/TCP 514)
Logstash (Processing)
    ↓ (Parsing, enrichment)
Elasticsearch (Storage)
    ↓ (Indexing, search)
Kibana (Visualization)
```

## Elasticsearch Installation

### Single Node Setup (Development)
```bash
# Download
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.10.0-linux-x86_64.tar.gz
tar xzf elasticsearch-8.10.0-linux-x86_64.tar.gz
cd elasticsearch-8.10.0

# Configure (config/elasticsearch.yml)
cat > config/elasticsearch.yml << 'EOF'
cluster.name: network-monitoring
node.name: node-1
network.host: 0.0.0.0
http.port: 9200
xpack.security.enabled: true
xpack.security.enrollment.enabled: true
EOF

# Generate security credentials
bin/elasticsearch-users useradd elastic -p changeme123 -r superuser

# Start
./bin/elasticsearch
```

### Production Cluster (3 nodes)
```bash
# Create config for each node
# elasticsearch-node1.yml
cluster.name: network-monitoring
node.name: node-1
node.master: true
node.data: true
network.host: 10.0.0.11
http.port: 9200
discovery.seed_hosts: ["10.0.0.11", "10.0.0.12", "10.0.0.13"]
cluster.initial_master_nodes: ["node-1", "node-2", "node-3"]
xpack.security.enabled: true
xpack.security.authc.api_key.enabled: true

# Repeat for nodes 2 and 3 (different IPs and node names)

# Use systemd to manage all 3 nodes
sudo systemctl start elasticsearch@node1
sudo systemctl start elasticsearch@node2
sudo systemctl start elasticsearch@node3

# Verify cluster
curl -u elastic:password http://localhost:9200/_cluster/health
# Expected: "status": "green"
```

## Logstash Configuration

### Basic Network Syslog Pipeline
```bash
# /etc/logstash/conf.d/network-syslog.conf

input {
  udp {
    host => "0.0.0.0"
    port => 514
    codec => plain
    type => "syslog"
  }
  tcp {
    host => "0.0.0.0"
    port => 514
    codec => plain
    type => "syslog"
  }
}

filter {
  if [type] == "syslog" {
    # Parse syslog message
    grok {
      match => {
        "message" => "%{SYSLOGLINE}"
      }
    }

    # Parse RFC 5424 format (newer Cisco, Juniper)
    grok {
      match => {
        "message" => "<%{INT:priority}>%{TIMESTAMP_ISO8601:timestamp} %{HOSTNAME:hostname} %{WORD:program} %{INT:pid}: %{GREEDYDATA:msg}"
      }
    }

    # Extract facility and severity
    ruby {
      code => '
        priority = event.get("priority").to_i
        event.set("facility", priority / 8)
        event.set("severity", priority % 8)
      '
    }

    # Parse common network messages
    if [message] =~ /LINK-3-UPDOWN/ {
      grok {
        match => {
          "message" => "LINK-3-UPDOWN: Interface %{DATA:interface}, changed state to %{WORD:state}"
        }
      }
      mutate {
        add_tag => [ "interface_change" ]
      }
    }

    if [message] =~ /BGP.*down/ {
      mutate {
        add_tag => [ "bgp_change" ]
      }
    }

    # Set timestamp
    date {
      match => [ "timestamp", "MMM d HH:mm:ss", "MMM dd HH:mm:ss" ]
      timezone => "UTC"
    }

    # Clean up fields
    mutate {
      remove_field => ["priority"]
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    user => "elastic"
    password => "changeme123"
    index => "network-logs-%{+YYYY.MM.dd}"
    document_type => "_doc"
  }

  # Also output to console for debugging
  stdout {
    codec => rubydebug
  }
}
```

### Advanced NetFlow Processing
```bash
# /etc/logstash/conf.d/netflow.conf

input {
  udp {
    host => "0.0.0.0"
    port => 2055
    codec => netflow {
      definitions => "/etc/logstash/netflow-definitions.yml"
      cache_ttl => 4000
      versions => [9, 5]
    }
  }
}

filter {
  if [netflow][ipv4_src_addr] {
    # Enrich with geolocation
    geoip {
      source => "[netflow][ipv4_src_addr]"
      target => "geoip"
    }

    # Parse ports
    mutate {
      add_field => {
        "src_ip" => "%{[netflow][ipv4_src_addr]}"
        "dst_ip" => "%{[netflow][ipv4_dst_addr]}"
        "src_port" => "%{[netflow][src_port]}"
        "dst_port" => "%{[netflow][dst_port]}"
        "bytes" => "%{[netflow][in_bytes]}"
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    user => "elastic"
    password => "changeme123"
    index => "netflow-%{+YYYY.MM.dd}"
  }
}
```

## Kibana Configuration

### Index Pattern Setup
```
1. Open Kibana (http://localhost:5601)
2. Go to Stack Management → Index Patterns
3. Create new index pattern
4. Name: network-logs-*
5. Time field: @timestamp
6. Create index pattern
```

### Network Dashboard Creation
```json
{
  "version": "8.0",
  "objects": [
    {
      "type": "dashboard",
      "id": "network-overview",
      "attributes": {
        "title": "Network Syslog Overview",
        "panels": [
          {
            "type": "visualization",
            "title": "Event Count by Severity",
            "query": "type:syslog",
            "aggs": [
              {
                "type": "terms",
                "field": "severity"
              }
            ]
          },
          {
            "type": "visualization",
            "title": "Top Devices Sending Logs",
            "query": "type:syslog",
            "aggs": [
              {
                "type": "terms",
                "field": "hostname",
                "size": 10
              }
            ]
          },
          {
            "type": "data_table",
            "title": "Recent Critical Events",
            "query": "type:syslog AND severity:[0 TO 2]"
          }
        ]
      }
    }
  ]
}
```

### Saved Searches
```
Device Down Events:
  message:("LINK-3-UPDOWN" OR "BGP" OR "down") AND severity:[0 TO 2]

Configuration Changes:
  message:("Config changed" OR "configuration" OR "CONFCHANGE")

Error Events:
  severity:3

Security Events:
  message:("denied" OR "attack" OR "unauthorized" OR "failed")
```

## Data Retention Management

### Index Lifecycle Management (ILM)
```bash
# Create ILM policy for network logs
curl -X PUT "localhost:9200/_ilm/policy/network-logs-policy" \
  -H 'Content-Type: application/json' \
  -d '{
    "policy": "network-logs-policy",
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
      "cold": {
        "min_age": "30d",
        "actions": {
          "searchable_snapshot": {}
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }'

# Apply policy to index template
curl -X PUT "localhost:9200/_index_template/network-logs-template" \
  -H 'Content-Type: application/json' \
  -d '{
    "index_patterns": ["network-logs-*"],
    "template": {
      "settings": {
        "index.lifecycle.name": "network-logs-policy",
        "index.lifecycle.rollover_alias": "network-logs"
      }
    }
  }'
```

## Alerting & Monitoring

### Create Watcher Alerts
```json
{
  "trigger": {
    "schedule": {
      "interval": "5m"
    }
  },
  "input": {
    "search": {
      "request": {
        "indices": ["network-logs-*"],
        "body": {
          "query": {
            "bool": {
              "must": [
                {
                  "range": {
                    "@timestamp": {
                      "gte": "now-5m"
                    }
                  }
                },
                {
                  "term": {
                    "severity": 0
                  }
                }
              ]
            }
          }
        }
      }
    }
  },
  "condition": {
    "compare": {
      "ctx.payload.hits.total.value": {
        "gt": 0
      }
    }
  },
  "actions": {
    "send_email": {
      "email": {
        "to": "alerts@example.com",
        "subject": "Critical Network Events Detected",
        "body": "Found {{ctx.payload.hits.total.value}} critical events"
      }
    }
  }
}
```

## Performance Optimization

### Shard Strategy
```
For 1GB/day syslog volume:
  - Primary shards: 3
  - Replicas: 1
  - Shard size target: 30-50GB

For high-volume NetFlow:
  - Primary shards: 10-20
  - Replicas: 1
  - Shard size target: 50GB
```

### Disk Space Planning
```
Syslog (1000 devices, 500 msgs/device/day):
  Messages: 500,000/day
  Average size: 150 bytes
  Daily volume: 75MB
  Yearly: 27.4GB with 1 replica = 54.8GB

Retention: 90 days = ~5TB (including replicas)
```

## Maintenance Tasks

### Daily
```bash
# Check cluster health
curl -u elastic:password http://localhost:9200/_cluster/health | jq '.status'

# Monitor heap usage
curl -u elastic:password http://localhost:9200/_nodes/stats/jvm | jq '.nodes[].jvm.mem.heap_percent'

# Check disk space
df -h /var/lib/elasticsearch
```

### Weekly
```bash
# Review index sizes
curl -u elastic:password http://localhost:9200/_cat/indices?v | grep network-logs

# Check unassigned shards
curl -u elastic:password http://localhost:9200/_cat/shards?v | grep UNASSIGNED
```

## Implementation Checklist

- [ ] Install Elasticsearch cluster
- [ ] Install Logstash
- [ ] Install Kibana
- [ ] Configure syslog collection
- [ ] Create Logstash pipelines
- [ ] Create index patterns
- [ ] Build dashboards
- [ ] Configure alerting
- [ ] Set up ILM policies
- [ ] Plan disk retention
- [ ] Test failover
- [ ] Document procedures
- [ ] Train team

---

**Guide Type**: Implementation
**Technologies**: Elasticsearch 8.x, Logstash 8.x, Kibana 8.x
**Use Case**: Network syslog aggregation and analysis
**Timeline**: 2-3 weeks
**Last Updated**: 2025-11-19
