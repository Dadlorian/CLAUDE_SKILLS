# VMware NSX Deployment Guide

## NSX-T Architecture

```
NSX Manager (Management Plane)
├─ Policies
├─ Configuration
└─ APIs

NSX Controller Cluster (Control Plane)
├─ 3 nodes (minimum)
├─ BUM handling
└─ Logical switch control

Transport Nodes (Data Plane)
├─ Hypervisors (ESXi/KVM)
├─ Physical TOR switches
└─ Bare-metal servers
```

## Prerequisites

### Infrastructure Requirements

```
NSX Manager:
├─ CPU: 8+ vCPU
├─ RAM: 32GB+
├─ Disk: 200GB+ SSD
├─ Network: Gigabit minimum

NSX Controller (3+ nodes):
├─ CPU: 4+ vCPU each
├─ RAM: 16GB+ each
├─ Network: Gigabit, low-latency

Transport Nodes:
├─ vSphere 6.5+
├─ 10GB+ network
├─ VLAN trunking capability
└─ MTU 1600+ recommended

NSX Edge Gateway:
├─ CPU: 4+ vCPU
├─ RAM: 16GB+
├─ Disk: 100GB+ SSD
└─ Qty: 2+ (HA)
```

### Networking Requirements

```
✓ Management network (vNIC)
✓ Overlay transport network
  ├─ VXLAN/Geneve capable
  ├─ Jumbo frames enabled
  └─ Multicast or replication
✓ Edge uplink network
✓ IP addressing scheme
✓ NTP synchronization
✓ DNS resolution
```

---

## NSX Manager Deployment

### Step 1: Deploy NSX Manager OVA

```bash
# 1. Download NSX-T Manager OVA from VMware
# Example: nsx-unified-appliance-3.2.0.0.0-xxxxxxxxxx.ova

# 2. Deploy via vCenter
vCenter > VMs and Templates > Deploy OVF Template
├─ Select OVA file
├─ Configure virtual machine
│  ├─ Name: nsx-mgr-1
│  ├─ Datastore: SSD-datastore
│  └─ Network: Management-VLAN
├─ Customize configuration
│  ├─ Root password
│  ├─ IP address: 10.0.0.10
│  ├─ Netmask: 255.255.255.0
│  ├─ Gateway: 10.0.0.1
│  ├─ DNS: 8.8.8.8
│  └─ NTP: 10.0.0.1
└─ Power on

# 3. Verify deployment
ping 10.0.0.10
ssh admin@10.0.0.10
```

### Step 2: Initial Configuration

```bash
# Access NSX Manager CLI
ssh admin@10.0.0.10
Password: (initial temporary password from OVA)

# Change root password
set user admin password
# Enter new password

# Configure management DNS/NTP
set service dns servers 8.8.8.8
set service ntp servers 10.0.0.1

# Verify connectivity
get service dns
get service ntp
```

### Step 3: Form Controller Cluster

```bash
# Deploy controllers
NSX Manager Web UI (https://10.0.0.10/)
├─ Fabric > Nodes > Controllers
├─ Click "Add"
├─ Provide OVA details:
│  ├─ Name: controller-1
│  ├─ IP: 10.0.0.11
│  ├─ Cluster: Join existing or create
│  └─ Datastore: SSD-datastore
└─ Deploy (repeat for controllers 2 and 3)

# Wait 10-15 minutes for cluster formation
# Verify: Fabric > Nodes > Controllers
# All should show: Realized + Status = Up
```

---

## Networking Configuration

### Step 1: Create Transport Zones

```
System > Fabric > Transport Zones

1. Create Overlay Transport Zone
   ├─ Name: tz-overlay
   ├─ Type: Overlay
   ├─ Traffic Type: Overlay
   └─ Hosts: Auto-added when connected

2. Create VLAN Transport Zone
   ├─ Name: tz-vlan
   ├─ Type: VLAN
   ├─ N-VDS backing: auto
   └─ Used for physical uplinks
```

### Step 2: Prepare Transport Nodes (Hypervisors)

**On each ESXi host**:
```bash
# Via vCenter > Hosts > Configure > VMware NSX

# 1. Select hosts to add
# 2. Configure interfaces:
#    ├─ Tunnel Endpoint (underlay)
#    │  ├─ IP: 10.0.1.x (from host management)
#    │  └─ Interface: vmk0 (or dedicated)
#    └─ VLAN (uplink)
#       ├─ vNIC: vmnic0, vmnic1
#       └─ MTU: 1600

# 3. Create N-VDS (NSX Virtual Distributed Switch)
#    ├─ Port groups created automatically
#    └─ VM vNICs attached to N-VDS

# Result: Transport Node registered in NSX Manager
```

### Step 3: Create Logical Switches

```
Networking > Logical Switches > Add

1. Tenant Network
   ├─ Name: Tenant-A-Net-1
   ├─ VNI: 5000 (auto-assigned)
   ├─ Transport Zone: tz-overlay
   ├─ Replication Mode: Multicast (or Unicast)
   └─ Create

2. Verify
   Networking > Logical Switches > Tenant-A-Net-1
   ├─ Status: Realized
   ├─ VNI: 5000
   └─ Segment Ports: Available
```

### Step 4: Create Logical Routers

```
1. Tier-0 Router (External Gateway)
   ├─ Name: Tier-0-GW
   ├─ Type: Active-Active
   ├─ High Availability:
   │  ├─ Mode: Active-Active
   │  ├─ Deployment: 2 Edge nodes
   │  └─ VRF: Global VRF
   └─ Create

2. Tier-1 Router (Tenant Router)
   ├─ Name: Tier-1-A
   ├─ Type: Centralized (or Distributed)
   ├─ Tier-0 Link: Connect to Tier-0-GW
   ├─ Failover: Enable HA
   └─ Create

3. Attach Logical Switch
   Tier-1-A > Interfaces > Add Interface
   ├─ Type: Downlink
   ├─ Logical Switch: Tenant-A-Net-1
   ├─ IP: 10.100.0.1/24
   └─ Create
```

---

## Edge Gateway Deployment

### Step 1: Deploy NSX Edge Appliance

```bash
# Via vCenter > OVF Deployment

# Configuration:
├─ Name: nsx-edge-1
├─ Datastore: SSD-datastore
├─ Network: Management
│  ├─ IP: 10.0.2.10
│  ├─ Netmask: 255.255.255.0
│  └─ Gateway: 10.0.0.1
├─ Data Network: auto
├─ Backup Edge:
│  ├─ Hostname: nsx-edge-2
│  └─ IP: 10.0.2.11
└─ Power on

# Verify: Fabric > Nodes > Edges
# Status should be: Up
```

### Step 2: Create Edge Cluster

```
System > Fabric > Edge Clusters > Add

├─ Name: edge-cluster-1
├─ Edge Nodes:
│  ├─ nsx-edge-1
│  └─ nsx-edge-2
├─ Member Index: 0, 1
├─ HA Mode: Active-Passive (or N+1)
└─ Create

# Verify: Fabric > Nodes > Edge Clusters
# Members: All up, Health: Good
```

### Step 3: Connect Tier-0 to Edge Cluster

```
Networking > Tier-0 > Routing
├─ Select Tier-0-GW
├─ Configuration:
│  ├─ Edge Cluster: edge-cluster-1
│  ├─ Failover Mode: Active-Passive
│  └─ Save

# Add external interfaces
├─ Uplink Interfaces:
│  ├─ Name: ext-if-1
│  ├─ IP: 10.99.0.1/24
│  ├─ Transport Node: nsx-edge-1
│  ├─ Segment: uplink-segment
│  └─ Add
```

---

## Security Configuration

### Step 1: Configure DFW Rules

```
Security > Distributed Firewall

# Create rule group
├─ Name: Production-Rules
├─ Rules:
│  │
│  ├─ Allow: Web-Tier to DB-Tier
│  │  ├─ Source: Web-Group
│  │  ├─ Destination: DB-Group
│  │  ├─ Service: TCP 3306
│  │  ├─ Action: Allow
│  │  └─ Logging: Yes
│  │
│  ├─ Allow: Client to Web-Tier
│  │  ├─ Source: ANY
│  │  ├─ Destination: Web-Group
│  │  ├─ Service: TCP 443
│  │  ├─ Action: Allow
│  │  └─ Logging: Yes
│  │
│  └─ Drop: Default
│     └─ Action: Drop (implicit deny)
│
└─ Applied to: VMs with tag: production
```

### Step 2: Create Security Groups (Dynamic)

```
Security > Security Groups > Add

1. Web-Tier Group
   ├─ Name: Web-Tier
   ├─ Membership Criteria:
   │  ├─ Tag: tier=web
   │  └─ Match: Equals
   └─ Create

2. DB-Tier Group
   ├─ Name: DB-Tier
   ├─ Membership Criteria:
   │  ├─ Tag: tier=database
   │  └─ Match: Equals
   └─ Create

# Tag VMs with labels:
vCenter > VM > Configure > Tags
├─ Add tag: tier=web
└─ Add tag: tier=database
```

### Step 3: Configure NAT

```
Networking > Tier-0 > NAT

1. SNAT (Source NAT)
   ├─ Applied On: edge-cluster-1
   ├─ Source IP: 10.100.0.0/24 (internal)
   ├─ Translated IP: 10.99.0.100 (external)
   ├─ Enabled: Yes
   └─ Create

2. DNAT (Destination NAT)
   ├─ Applied On: edge-cluster-1
   ├─ Translated IP: 10.99.0.50 (external)
   ├─ Destination IP: 10.100.0.50 (internal)
   ├─ Service: TCP 443
   └─ Create
```

---

## Load Balancing

### Step 1: Create Load Balancer

```
Networking > Load Balancing > Load Balancers > Add

├─ Name: LB-Web
├─ Attachment: Tier-1-A
├─ Configuration:
│  ├─ Virtual Servers:
│  │  ├─ Name: VS-Web-HTTPS
│  │  ├─ Application Profile: HTTPS
│  │  ├─ IP: 10.100.0.100
│  │  ├─ Port: 443
│  │  └─ Default Pool: pool-web
│  │
│  ├─ Server Pools:
│  │  ├─ Name: pool-web
│  │  ├─ Algorithm: LEAST_CONN
│  │  ├─ Members:
│  │  │  ├─ web-server-1 (10.100.0.10)
│  │  │  └─ web-server-2 (10.100.0.11)
│  │  └─ Health Monitor: HTTP-Monitor
│  │
│  └─ Health Monitors:
│     ├─ Name: HTTP-Monitor
│     ├─ Type: HTTP
│     ├─ Path: /health
│     └─ Interval: 10 seconds
│
└─ Create
```

---

## Kubernetes Integration

### Step 1: Deploy NSX-NCP

```bash
# NSX Container Plug-in for Kubernetes

# 1. Download NSX-NCP manifest
# 2. Deploy to Kubernetes
kubectl create namespace nsx-system

# 3. Configure NSX-NCP
cat <<EOF | kubectl create -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: nsx-ncp-config
  namespace: nsx-system
data:
  nsx_v3_url: "https://10.0.0.10"
  nsx_username: "admin"
  nsx_password: "password"
  cluster: "K8S-Cluster-1"
  apiserver_host_ip: "10.1.1.1"
  apiserver_host_port: "6443"
  container_ip_blocks: "10.200.0.0/16"
  service_ip_blocks: "172.30.0.0/16"
EOF

# 4. Deploy NSX-NCP DaemonSet
kubectl apply -f nsx-ncp.yaml

# Verify:
kubectl get pods -n nsx-system
# Expected: nsx-ncp, nsx-node-agent pods running
```

### Step 2: Create Network Policies

```yaml
# Pod communication with NSX DFW enforcement
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-db-to-web
spec:
  podSelector:
    matchLabels:
      app: web
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 443
```

---

## Monitoring and Troubleshooting

### Health Check

```
System > Monitoring > Health

Verify:
├─ NSX Manager: Up
├─ Controllers: All Up
├─ Transport Nodes: All Realized
├─ Logical Switches: All Realized
├─ Logical Routers: All Realized
└─ Overall: Healthy (green)
```

### Flow Verification

```bash
# Test connectivity
nsx-manager# get logical-switch Tenant-A-Net-1
# Verify VNI and port count

# Test routing
# From VM: traceroute 10.99.0.1
# Should show path through Tier-1 → Tier-0 → external

# Check firewall logs
Security > Firewall > Logs
# Verify rules enforcing correctly
```

### Troubleshooting

```bash
# Issue: Logical switch not realized
# Solution:
1. Check transport nodes status
   get transport-nodes  # All should be realized
2. Check controller status
   get controllers
3. Check overlay tunnel status
   get tunnels state

# Issue: High latency
# Solution:
1. Check controller load
   get service metrics
2. Check network MTU
   get network interfaces
3. Check underlay latency
   ping remote_node
```

---

## Best Practices

### Design
- **Redundancy**: Multiple controllers (3+), multiple edges (2+)
- **Sizing**: Plan for growth
- **Segmentation**: Use security groups for zero-trust
- **Monitoring**: Enable logging on all rules

### Operations
- **Backup**: Regular backup of NSX configuration
- **Updates**: Test patches in lab first
- **Scaling**: Monitor control plane load
- **Documentation**: Keep topology diagram updated

### Security
- **DFW**: Default deny, explicit allow
- **Secrets**: Use vSphere Secrets Engine
- **Audit**: Enable audit logging
- **TLS**: Enforce encryption

---

## Migration from NSX-V

```
Phase 1: Planning
├─ Assess NSX-V environment
├─ Document all segments/policies
└─ Design NSX-T equivalent

Phase 2: Deploy NSX-T Parallel
├─ Deploy NSX-T infrastructure
├─ Create logical networks
├─ Configure security policies

Phase 3: Migrate Workloads
├─ VM-by-VM migration (vMotion)
├─ Verify connectivity after each move
└─ Gradually shift to NSX-T

Phase 4: Decommission NSX-V
├─ Confirm all workloads on NSX-T
├─ Remove NSX-V controllers
└─ Decommission infrastructure
```
