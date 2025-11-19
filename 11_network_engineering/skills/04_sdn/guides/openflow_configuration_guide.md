# OpenFlow Configuration Guide

## OpenFlow Switch Setup

### Step 1: Enable OpenFlow on Switch

**Cisco Catalyst/Nexus**:
```bash
# Enter global configuration
configure terminal

# Enable OpenFlow
openflow mode standalone

# Configure OpenFlow controller
openflow controller ipv4 10.0.0.1 port 6653
openflow controller ipv4 10.0.0.2 port 6653 (backup)

# Verify
show openflow summary
# Expected: OpenFlow enabled, controllers connected
```

**Open vSwitch (Linux)**:
```bash
# Check if installed
ovs-vsctl --version

# If not installed
apt-get install openvswitch-switch

# Start service
systemctl start openvswitch-switch

# Create bridge
ovs-vsctl add-br br0

# Set controller
ovs-vsctl set-controller br0 tcp:10.0.0.1:6653

# Verify
ovs-vsctl show
# Expected: br0 connected to controller
```

### Step 2: Configure OpenFlow Version

```bash
# Cisco (use negotiated version)
openflow version negotiate

# Linux OVS (set specific version)
ovs-vsctl set bridge br0 protocols=OpenFlow15

# Verify negotiated version
ovs-appctl -t ovsdb-server list-br
```

### Step 3: Configure Datapath ID

```bash
# Cisco (automatic from MAC)
show openflow switch

# OVS (manual if needed)
ovs-vsctl set bridge br0 other-config:datapath-id=0000000000000001

# Format: 16 hex digits representing 64-bit ID
# Usually derived from switch MAC address
```

---

## Flow Rule Installation

### Method 1: Controller-Driven Installation

**ONOS Example**:
```bash
# Install flow via REST API
curl -X POST http://10.0.0.1:8181/onos/v1/flows/of:0000000000000001 \
  -H "Content-Type: application/json" \
  -d '{
    "priority": 40000,
    "timeout": 0,
    "isPermanent": true,
    "deviceId": "of:0000000000000001",
    "treatment": {
      "instructions": [
        {
          "type": "OUTPUT",
          "port": "CONTROLLER"
        }
      ]
    },
    "selector": {
      "criteria": [
        {
          "type": "IN_PORT",
          "port": "1"
        }
      ]
    }
  }'
```

**Flow Details**:
```
Match Criteria (Selector):
├─ Incoming port: 1
├─ Ethernet type: IPv4
├─ Destination IP: 10.100.0.20
└─ Protocol: TCP

Actions (Treatment):
├─ Rewrite VLAN to 100
├─ Modify destination MAC
└─ Output to port 2
```

### Method 2: OpenFlow CLI Installation

**Direct to Switch**:
```bash
# OVS - add flow rule via ovs-ofctl
ovs-ofctl add-flow br0 "in_port=1,actions=output:2"

# Syntax: in_port=X,match_criteria=value,actions=action

# Examples:
# Simple forward
ovs-ofctl add-flow br0 "in_port=1,actions=output:2"

# L2 learning switch
ovs-ofctl add-flow br0 "priority=0,actions=controller(max_len=65535)"

# VLAN tagging
ovs-ofctl add-flow br0 "in_port=1,actions=mod_vlan_vid:100,output:2"

# MAC filtering
ovs-ofctl add-flow br0 "eth_dst=aa:bb:cc:dd:ee:ff,actions=output:3"

# Priority-based (higher = more specific)
ovs-ofctl add-flow br0 "priority=1000,in_port=1,eth_type=0x0800,actions=output:2"
```

### Method 3: Flow Rules via OpenDaylight

**ODL REST API**:
```bash
# Get available switches
curl http://10.0.0.1:8181/restconf/operational/opendaylight-inventory:nodes

# Add flow rule
curl -X PUT http://10.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/table/0/flow/1 \
  -H "Content-Type: application/json" \
  -d '{
    "flow": [
      {
        "id": "1",
        "match": {
          "in-port": "1",
          "ethernet-match": {
            "ethernet-type": {
              "type": "0x0800"
            }
          }
        },
        "instructions": {
          "instruction": [
            {
              "order": "0",
              "apply-actions": {
                "action": [
                  {
                    "order": "0",
                    "output-action": {
                      "output-node-connector": "2"
                    }
                  }
                ]
              }
            }
          ]
        },
        "priority": "100",
        "flow-name": "forward-eth0-to-eth1"
      }
    ]
  }'
```

---

## Advanced Flow Rules

### Group Tables

**Group for Load Balancing**:
```bash
# Add group table
ovs-ofctl -O OpenFlow15 add-group br0 \
  group_id=1,type=select,bucket=weight:50,output:2,bucket=weight:50,output:3

# Use group in flow rule
ovs-ofctl add-flow br0 "in_port=1,actions=group:1"
```

**Group for Broadcast (Multicast)**:
```bash
# Add group for broadcast
ovs-ofctl -O OpenFlow15 add-group br0 \
  group_id=2,type=all,bucket=output:2,bucket=output:3,bucket=output:4

# Flow rule for broadcast
ovs-ofctl add-flow br0 "eth_dst=ff:ff:ff:ff:ff:ff,actions=group:2"
```

### Meters (Rate Limiting)

```bash
# Add meter for rate limiting
ovs-ofctl -O OpenFlow13 add-meter br0 meter_id=1,kbps,burst,band=type=drop,rate=1000,burst_size=200

# Use meter in flow
ovs-ofctl add-flow br0 "in_port=1,actions=meter:1,output:2"

# Result: Limit traffic from port 1 to 1 Mbps
```

### Match Field Examples

```bash
# Various match criteria
ovs-ofctl add-flow br0 "eth_src=00:11:22:33:44:55,actions=output:2"
# Match source MAC

ovs-ofctl add-flow br0 "ip,nw_dst=10.100.0.0/24,actions=output:3"
# Match destination IP subnet

ovs-ofctl add-flow br0 "tcp,tp_dst=80,actions=output:4"
# Match TCP port 80 (HTTP)

ovs-ofctl add-flow br0 "udp,tp_dst=53,actions=output:5"
# Match UDP port 53 (DNS)

ovs-ofctl add-flow br0 "ipv6,ipv6_dst=2001:db8::/32,actions=output:6"
# Match IPv6 prefix

ovs-ofctl add-flow br0 "vlan_vid=100,actions=mod_vlan_vid:200,output:2"
# Match and modify VLAN
```

---

## Table Pipeline Configuration

### Multiple Flow Tables

```bash
# Table 0: Ingress classification
ovs-ofctl add-flow br0 "table=0,in_port=1,actions=goto_table:1"
# Forward to table 1 for further processing

# Table 1: MAC learning
ovs-ofctl add-flow br0 "table=1,eth_type=0x0800,actions=goto_table:2"
# Forward IP traffic to table 2

# Table 2: Routing
ovs-ofctl add-flow br0 "table=2,nw_dst=10.100.0.0/24,actions=output:2"

# Table 3: Output/QoS
ovs-ofctl add-flow br0 "table=3,priority=10,actions=set_queue:1,output:2"
```

### Metadata Handling

```bash
# Write metadata in early table
ovs-ofctl add-flow br0 "table=0,priority=1000,in_port=1,actions=write_metadata:0x100/0xff,goto_table:1"

# Use metadata in later table
ovs-ofctl add-flow br0 "table=1,metadata=0x100/0xff,actions=output:2"
```

---

## Packet-In Handling

### Send Packets to Controller

```bash
# Add default rule to send unmatched packets to controller
ovs-ofctl add-flow br0 "priority=0,actions=controller(max_len=65535)"

# Limit packet-in rate
ovs-ofctl add-meter br0 meter_id=100,pps,band=type=drop,rate=100
ovs-ofctl add-flow br0 "priority=0,actions=meter:100,controller"

# Specific packet-in for certain traffic
ovs-ofctl add-flow br0 "arp,actions=controller"
# Send all ARP packets to controller for learning
```

---

## Statistics and Monitoring

### View Flow Statistics

```bash
# List all flows
ovs-ofctl dump-flows br0
# Output shows: priority, match criteria, actions, packet/byte counts

# Sample output:
# priority=40000, n_packets=1000, n_bytes=1000000 in_port=1 actions=output:2
# priority=100,   n_packets=500,  n_bytes=500000   eth_dst=aa:bb:cc:dd:ee:ff actions=output:3
```

### Monitor Real-Time

```bash
# Watch flow statistics in real-time
watch -n 1 'ovs-ofctl dump-flows br0'

# Show table statistics
ovs-ofctl dump-table-stats br0
# Shows: lookup count, matched count, active flows per table

# Monitor packet-in messages
ovs-appctl -t ovs-vswitchd coverage/show | grep packet_in
```

---

## QoS Configuration

### Queue Configuration

```bash
# Create queues on interface
ovs-vsctl add-queue br0 eth0 0 -- set Queue eth0-q0 dscp=10
# Queue 0: Real-time traffic (DSCP 46/EF)

ovs-vsctl add-queue br0 eth0 1 -- set Queue eth0-q1 dscp=24
# Queue 1: Standard traffic (DSCP 24/AF)

ovs-vsctl add-queue br0 eth0 2 -- set Queue eth0-q2 dscp=0
# Queue 2: Best-effort traffic

# Assign flows to queues
ovs-ofctl add-flow br0 "udp,tp_dst=5060,actions=set_queue:0,output:eth0"
# VoIP to high-priority queue

ovs-ofctl add-flow br0 "tcp,tp_dst=80,actions=set_queue:1,output:eth0"
# HTTP to standard queue
```

### Rate Limiting per Queue

```bash
# Configure QoS policy
ovs-vsctl set port eth0 qos=@newqos -- --id=@newqos create qos type=linux-htb other-config:max-rate=10000000

# Add queue with bandwidth limit
ovs-vsctl set queue eth0-q0 other-config:min-rate=2000000
# Minimum 2 Mbps guaranteed

ovs-vsctl set queue eth0-q0 other-config:max-rate=5000000
# Maximum 5 Mbps burst
```

---

## Troubleshooting OpenFlow

### Issue: Flows Not Installing

```bash
# Check switch status
ovs-vsctl show
# Verify controller connection

# Check controller connection status
ovs-ofctl show br0
# Expected: connected to controller

# Verify OpenFlow version
ovs-vsctl list-br
# Ensure bridge exists

# Check logs
tail -f /var/log/openvswitch/ovs-vswitchd.log
```

### Issue: High CPU on Flow Misses

```bash
# Symptom: Every packet sent to controller

# Solution 1: Add default rule
ovs-ofctl add-flow br0 "priority=0,actions=drop"
# Default drop instead of sending to controller

# Solution 2: Add learning rule
ovs-ofctl add-flow br0 "priority=0,actions=controller(max_len=128)"
# Limit controller packet size

# Solution 3: Rate limit packet-in
ovs-ofctl add-meter br0 meter_id=1,pps,band=type=drop,rate=1000
ovs-ofctl add-flow br0 "priority=0,actions=meter:1,controller"
```

### Issue: Traffic Drops

```bash
# Check for drop actions
ovs-ofctl dump-flows br0 | grep drop

# Monitor drops
ovs-vsctl get-interface br0 statistics
# Check: rx_dropped, tx_dropped

# Verify flow count
ovs-ofctl dump-flows br0 | wc -l
# If too many, consolidate rules

# Check table saturation
ovs-ofctl dump-table-stats br0
# Look for active_flows near table capacity
```

---

## Performance Optimization

### Flow Rule Optimization

```
Optimization Tips:
├─ Priority ordering (most specific highest)
├─ Combine related rules
├─ Use masks for broader matching
├─ Offload to hardware if supported
└─ Minimize controller communication

Example:
Instead of:
├─ 10 rules for port 80
├─ 10 rules for port 443
└─ 10 rules for port 8080

Combine into:
└─ 1 rule matching tcp,nw_dst=x.x.x.x (all ports)
```

### Hardware Offload

```bash
# Check if switch supports offload
ethtool -k eth0 | grep offload

# Enable offload for supported features
ethtool -K eth0 tx-checksum on
ethtool -K eth0 rx-checksum on

# OVS DPDK for high performance
ovs-vsctl set Open_vSwitch . other_config:dpdk-init=true
# Requires DPDK libraries and CPU cores
```

---

## Best Practices

### Flow Rule Design
- **Keep it simple**: Start with basic rules
- **Test in lab**: Validate before production
- **Document**: Comment on flow purpose
- **Monitor**: Watch statistics for anomalies

### Controller Integration
- **High availability**: Multiple controller instances
- **Backup operation**: Switch can operate without controller
- **Recovery**: Persist critical flows

### Performance
- **Flow timeouts**: Set appropriately
- **Meter rates**: Match link capacity
- **Queue sizes**: Prevent buffer bloat
- **Table depth**: Monitor utilization

### Scaling
- **Flow limits**: Know your switch capacity (thousands to millions)
- **Controller capacity**: Process flows efficiently
- **Underlay network**: Ensure sufficient bandwidth
- **Controller distribution**: Load balance across instances
