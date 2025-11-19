# SDN Deployment Guide

## Pre-Deployment Planning

### 1. Requirements Assessment
**Questions to Answer**:
- How many network devices will be managed?
- What's the geographic scale? (single DC, multi-DC, WAN)
- What are the performance requirements?
- What devices support SDN protocols?
- What's the budget and timeline?

### 2. Network Topology Analysis
```
Step 1: Document existing network
├─ Device inventory
├─ Link topology
├─ Current routing protocols
└─ Performance baselines

Step 2: Design new topology
├─ Spine-leaf vs traditional
├─ Controller placement
├─ Redundancy requirements
└─ Scaling plan

Step 3: Validate design
├─ Simulation testing
├─ Capacity planning
└─ Failover scenarios
```

### 3. Controller Selection
**Evaluation Criteria**:
```
OpenDaylight: R&D, custom requirements
ONOS: Carrier-grade, large scale
Cisco APIC: ACI environment
VMware NSX: VMware environment
Juniper Contrail: Cloud integration
```

---

## ONOS Deployment Example

### Step 1: Environment Preparation

**Hardware Requirements**:
```
ONOS Cluster (3 nodes recommended):
├─ CPU: 4+ cores per node
├─ RAM: 8GB+ per node
├─ Disk: 50GB+ per node
├─ Network: Gigabit minimum
└─ OS: Linux (Ubuntu, CentOS)
```

**Network Prerequisites**:
```
Prerequisites:
├─ Java 11+ installed
├─ SSH access to all nodes
├─ NTP synchronized
├─ Firewall rules configured (ports 6640, 6653, 9876)
└─ DNS working
```

### Step 2: Installation

```bash
# On each ONOS node
# 1. Download ONOS
wget http://repo1.maven.org/maven2/org/onosproject/onos-releases/2.5.1/onos-2.5.1.tar.gz

# 2. Extract
tar xzf onos-2.5.1.tar.gz
cd onos-2.5.1

# 3. Install cell configuration
# Edit ~/.bash_aliases
export ONOS_APPS="drivers,openflow,fwd,proxyarp,hostprovider"
export ONOS_USER=onos
export ONOS_GROUP=onos
export ONOS_INSTANCES="10.0.0.1 10.0.0.2 10.0.0.3"
export OCI=10.0.0.1  # Instance to interact with

# 4. Start ONOS
./bazel run onos-local -- clean

# 5. Verify startup
# Access: http://10.0.0.1:8181/onos/ui
# Username: onos, Password: rocks
```

### Step 3: Cluster Formation

```bash
# Join cluster on all nodes except first
# On node 1:
onos-cluster.sh broadcast config 10.0.0.1 10.0.0.2 10.0.0.3

# Verify cluster status
onos $OCI "cluster-nodes"

# Expected output:
# id=1, state=ACTIVE, addr=10.0.0.1:9876, lastUpdated=now
# id=2, state=ACTIVE, addr=10.0.0.2:9876, lastUpdated=now
# id=3, state=ACTIVE, addr=10.0.0.3:9876, lastUpdated=now
```

### Step 4: Switch Integration

```bash
# Connect OpenFlow switches
# Switches must be configured to point to controller:
# Example (on switch):
# openflow-controller ipv4 10.0.0.1 port 6653

# Verify devices connected
onos $OCI "devices"

# Expected output:
# id=of:0000000000000001, available=true, role=MASTER, mfr=Vendor, ...
# id=of:0000000000000002, available=true, role=MASTER, mfr=Vendor, ...
```

### Step 5: Application Deployment

```bash
# Install built-in applications
onos $OCI "app activate openflow"
onos $OCI "app activate fwd"
onos $OCI "app activate hostprovider"
onos $OCI "app activate proxyarp"

# Or install custom app
onos-app $OCI install myapp-1.0.oar
```

---

## OpenDaylight Deployment

### Installation Steps

```bash
# 1. Download
wget https://nexus.opendaylight.org/content/repositories/opendaylight.release/org/opendaylight/integration/karaf/2021.09.0/karaf-2021.09.0.tar.gz

# 2. Extract
tar xzf karaf-2021.09.0.tar.gz
cd karaf-2021.09.0

# 3. Start
./bin/karaf

# 4. Install required features
feature:install odl-openflowplugin-all
feature:install odl-restconf-all
feature:install odl-netconf-all

# 5. Verify
log:tail
# Check for any errors
```

---

## Controller High Availability

### Active-Active Setup (ONOS)

```
┌────────────────┐         ┌────────────────┐         ┌────────────────┐
│ ONOS Node 1    │         │ ONOS Node 2    │         │ ONOS Node 3    │
│ (Active)       │────────│ (Active)       │────────│ (Active)       │
└────────────────┘         └────────────────┘         └────────────────┘
      │                         │                         │
      └─────────────────────────┼─────────────────────────┘
                                │
                            Consensus DB
                         (distributed state)
```

**Configuration**:
```yaml
# cluster.cfg
NODE_IP: 10.0.0.1
CLUSTER_NODES: 10.0.0.1:9876 10.0.0.2:9876 10.0.0.3:9876
PARTITION_SIZE: 2
```

### Controller Redundancy Options

**Option 1: Master-Backup**
- One active, others standby
- Fast failover
- Simpler to manage

**Option 2: Active-Active**
- All active, distributed state
- Better utilization
- Complex consistency

**Option 3: Multi-Region**
- Regional controllers
- Regional failover
- Global redundancy

---

## Fabric Provisioning

### Device Registration

```bash
# Add switch to controller
# Method 1: Using curl
curl -X POST http://controller:8181/api/topology/device \
  -H "Content-Type: application/json" \
  -d '{
    "id": "of:0000000000000001",
    "ip": "10.0.1.1",
    "port": 6653
  }'

# Method 2: Using onos CLI
onos $OCI "device-add of:0000000000000001 10.0.1.1 6653"
```

### Fabric Discovery

```bash
# Automatic device discovery via:
# 1. BGP session info
# 2. LLDP (Link Layer Discovery Protocol)
# 3. OpenFlow hello messages

# Verify discovered topology
onos $OCI "links"
# Output:
# src=of:0000000000000001/1 dst=of:0000000000000002/1 state=ACTIVE
```

---

## Underlay Network Configuration

### VXLAN Underlay

```
# On all switches:
# 1. Enable VXLAN support
vxlan enable

# 2. Configure VTEP (VXLAN Tunnel Endpoint)
vtep local-ip 10.0.0.1

# 3. Configure remote VTEPs
vtep remote-ip 10.0.0.2
vtep remote-ip 10.0.0.3

# 4. Enable EVPN
bgp 65001
  address-family l2vpn evpn
    redistribute connected
    redistribute static
    redistribute learned
```

### BGP EVPN Configuration

```
# Spine switch
router bgp 65001
  neighbor 10.0.0.10 remote-as 65001
  !
  address-family l2vpn evpn
    neighbor 10.0.0.10 activate
    advertise-all-vni
```

---

## Overlay Network Setup

### VXLAN Tenant Network

```python
# Using ONOS REST API
import requests
import json

controller = "10.0.0.1"
base_url = f"http://{controller}:8181/onos/v1"
auth = ("onos", "rocks")

# Create logical network
logical_network = {
  "name": "Tenant-A-Network",
  "type": "VXLAN",
  "vni": 1001,
  "underlay_vrf": "default"
}

response = requests.post(
  f"{base_url}/networks",
  json=logical_network,
  auth=auth
)
print(response.json())
```

### Subnet Assignment

```bash
# Configure subnet on logical network
# Subnet: 10.100.0.0/24, VNI: 1001

curl -X POST http://controller:8181/api/networks/Tenant-A-Network/subnets \
  -H "Content-Type: application/json" \
  -d '{
    "subnet_id": "subnet-1",
    "cidr": "10.100.0.0/24",
    "gateway": "10.100.0.1",
    "vni": 1001
  }'
```

---

## Validation & Testing

### Post-Deployment Checklist

```
☐ Controller cluster health
  - All nodes active
  - Quorum achieved
  - No split-brain

☐ Device connectivity
  - All switches connected
  - No disconnections
  - Latency < 50ms

☐ Overlay networks
  - VXLANs created
  - MACs learned
  - Traffic flows

☐ Routing
  - BGP EVPN working
  - Routes advertised
  - No path loops

☐ Performance
  - No packet loss
  - Latency within SLA
  - CPU/memory reasonable

☐ Security
  - TLS enabled
  - Authentication working
  - No unauthorized access
```

### Testing Procedures

```bash
# Test 1: Ping across VXLAN
# VM1 (10.100.0.10) → VM2 (10.100.0.20)
ping 10.100.0.20  # Should succeed

# Test 2: Traffic flow verification
# On controller:
onos $OCI "flows any"  # Verify flows installed

# Test 3: Failover testing
# Disable primary controller
# Verify traffic continues on backup

# Test 4: Load testing
# Use tools like iperf, netperf
iperf3 -c 10.100.0.20 -t 60  # 60 second test
```

---

## Monitoring & Telemetry

### Prometheus Integration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'onos'
    static_configs:
      - targets: ['10.0.0.1:8181']
    metrics_path: '/onos/metrics'
    scrape_interval: 15s
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "SDN Controller Metrics",
    "panels": [
      {
        "title": "Active Devices",
        "targets": [
          {"expr": "onos_devices_active"}
        ]
      },
      {
        "title": "Flow Rules Installed",
        "targets": [
          {"expr": "onos_flows_total"}
        ]
      }
    ]
  }
}
```

---

## Troubleshooting Common Issues

### Issue: Switches Not Connecting

```bash
# 1. Check controller connectivity
ssh switch "show connection"
# Expected: Connected to 10.0.0.1:6653

# 2. Check firewall
ssh controller "netstat -tlnp | grep 6653"
# Expected: LISTEN on port 6653

# 3. Verify credentials
ssh switch "show controller"
# Expected: Active connection to controller IP
```

### Issue: High Packet-In Rate

```
Symptom: CPU high, response slow
Cause: Reactive forwarding (every packet to controller)

Solution:
1. Install default rules proactively
2. Enable ARP caching
3. Use table-miss rule with action=drop

onos $OCI "flows <switch-id>"
# Check for massive number of flows
```

### Issue: Controller Cluster Unstable

```bash
# Check consensus status
onos $OCI "cluster-nodes"

# If nodes disagreeing:
# 1. Verify NTP sync: ntpstat
# 2. Check network connectivity: ping
# 3. Review logs: tail -f karaf.log
# 4. Force re-election if needed: cluster-force-election
```

---

## Next Steps

1. **Design Review**: Have architecture reviewed by experts
2. **Pilot Deployment**: Start with 2-3 switches
3. **Performance Testing**: Load test before full rollout
4. **Staff Training**: Train operations team
5. **Documentation**: Document deployment specifics
6. **Operational Procedures**: Define runbooks for common tasks
