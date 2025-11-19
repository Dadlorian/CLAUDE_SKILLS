# Cisco ACI Deployment Guide

## ACI Architecture Review

```
APIC Cluster (Control Plane)
├─ APIC Node 1 (Leader)
├─ APIC Node 2 (Follower)
└─ APIC Node 3 (Follower)
    ↓
ACI Fabric (Data Plane)
├─ Spine Nodes (1-4 typical)
├─ Leaf Nodes (2-24 typical)
└─ External connectivity nodes
    ↓
Endpoints
├─ VMs (via hypervisor)
├─ Bare-metal servers
├─ Containers
└─ External networks (L3Out)
```

## Pre-Deployment Checklist

### Hardware Requirements

```
APIC Appliance
├─ CPU: 16+ cores
├─ RAM: 64GB minimum
├─ Storage: 500GB+ SSD
├─ Network: Dual 10G minimum
└─ Qty: 1, 3, or 5 nodes (odd)

Spine Switches
├─ Model: Nexus 9500 series recommended
├─ Memory: 16GB minimum
├─ Forwarding capacity: Line-rate throughput
└─ Qty: 2 for small, 3+ for production

Leaf Switches
├─ Model: Nexus 9300 series recommended
├─ Uplink ports: Minimum 2 connections to spines
└─ Qty: 2+ (minimum for redundancy)
```

### Network Requirements

```
✓ NTP synchronization (critical)
✓ DNS resolution
✓ VLAN for APIC management (separate)
✓ IP addressing scheme planned
✓ Firewall rules for APIC (TCP 443, 8181)
✓ SSH access to all devices
✓ Out-of-band management network
```

---

## APIC Installation

### Step 1: Initial Setup

```bash
# 1. Connect to APIC console
# Username: admin
# Password: (first login, change required)

# 2. Basic configuration
apic1# set-hostname apic1
apic1# set-mgmt-ip 10.0.0.10 255.255.255.0
apic1# set-mgmt-gw 10.0.0.1
apic1# set-primary-dns 8.8.8.8
apic1# set-ntp-server 10.0.0.1

# 3. Verify
apic1# show configuration
apic1# ping 8.8.8.8  # Test external connectivity
```

### Step 2: Form Cluster

**For 3-node cluster**:
```bash
# On APIC1 (becomes leader)
apic1# set-cluster apic1 apic2 apic3

# Wait for cluster formation (5-10 minutes)
apic1# show cluster status
# Expected:
# apic1: LEADER, Health: OK
# apic2: FOLLOWER, Health: OK
# apic3: FOLLOWER, Health: OK

# Access UI: https://10.0.0.10/
# Login: admin / password
```

### Step 3: Fabric Configuration

**Via APIC GUI**:
```
1. Navigate to: Fabric > Fabric Nodes
2. Click "+ Add Fabric Node"
3. Configure:
   ├─ Node ID (unique per node)
   ├─ Serial Number
   ├─ Type (Spine or Leaf)
   └─ Role (Border, Spine, Leaf)
4. Assign to node group
5. Commit configuration
```

**Via REST API**:
```bash
curl -X POST https://apic1/api/node/mo/uni/fabric/nodecont/nodefeats.xml \
  -H 'Content-Type: application/xml' \
  -d '
<fabricNodeContainer>
  <fabricNode serial="ABC123456" role="leaf" />
</fabricNodeContainer>'
```

---

## Network Configuration

### Step 1: Create VRF

```bash
# Via GUI:
Tenants > Create Tenant > Configure VRF

# Via REST:
curl -X POST https://apic1/api/node/mo/uni/tn-Tenant-A.json \
  -d '{
    "fvTenant": {
      "attributes": {"name": "Tenant-A"},
      "children": [{
        "fvCtx": {
          "attributes": {"name": "VRF-A"}
        }
      }]
    }
  }'
```

### Step 2: Create Bridge Domain

```bash
# Via GUI:
Tenants > Tenant-A > Networking > Bridge Domains

# Configuration:
Name: BD-1001
VRF: VRF-A
Subnets: 10.100.0.0/24
  └─ Gateway: 10.100.0.1/24
  └─ Enable routing
```

### Step 3: Create EPGs

```bash
# Via GUI:
Tenants > Tenant-A > Application Profiles > App1 > EPGs

# Configuration:
Name: Web-Tier-EPG
Bridge Domain: BD-1001
VLAN: 1001
Physical Domain: PhysDom-1
```

---

## Policy Configuration

### Contract Definition

```bash
# Create contract: allow-web-to-db

# Contract structure:
Contract: web-to-db
├─ Subject: allow-tcp-443
│  ├─ Filter: tcp-443
│  │  ├─ Protocol: tcp
│  │  ├─ Dest Port: 443
│  │  └─ Action: permit
│  └─ Direction: both
├─ Provider EPG: DB-Tier-EPG
└─ Consumer EPG: Web-Tier-EPG
```

### Filter Creation (Reusable)

```bash
# Via REST:
curl -X POST https://apic1/api/node/mo/uni/tn-Tenant-A.json \
  -d '{
    "vzFilter": {
      "attributes": {"name": "tcp-443"},
      "children": [{
        "vzEntry": {
          "attributes": {
            "name": "https",
            "protocol": "tcp",
            "dFromPort": "443",
            "dToPort": "443",
            "etherT": "ip"
          }
        }
      }]
    }
  }'
```

---

## External Connectivity (L3Out)

### Step 1: Create L3Out

```bash
# Via GUI:
Tenants > Tenant-A > Networking > L3Outs > Create L3Out

# Configuration:
Name: L3Out-External
VRF: VRF-A
Routing Protocol: BGP
External EPGs: External-Subnets
```

### Step 2: Configure Routing

**BGP Peering**:
```bash
# On Leaf switch connected to external router

interface ethernet 1/49
  ip address 10.99.0.1 255.255.255.0
  no shutdown

router bgp 65000
  neighbor 10.99.0.2 remote-as 65001
  address-family ipv4 unicast
    neighbor 10.99.0.2 activate
    exit-address-family
  exit
```

### Step 3: Route Summarization

```bash
# Via REST:
curl -X POST https://apic1/api/node/mo/uni/tn-Tenant-A/out-L3Out-External \
  -d '{
    "l3extSubnet": {
      "attributes": {
        "ip": "192.168.0.0/16",
        "scope": ["import-security"]
      }
    }
  }'
```

---

## Multi-Site Deployment

### Step 1: Configure Multi-Site Orchestrator

```
Site-A (APIC-1)  ←────────→  Multi-Site Orchestrator
                               ↑
                               ↓
Site-B (APIC-2)  ←────────────→
```

### Step 2: Create Stretched EPG

```bash
# Via APIC GUI:
Tenants > Tenant-A > Application Profiles > EPG-Name

# Configuration:
Enable Multi-Site: Yes
Stretch to Sites: Site-A, Site-B
```

### Step 3: BGP EVPN between sites

```bash
# On border leaves (for inter-site routing)
router bgp 65000
  vrf context vrf-a
    rd auto
    address-family l2vpn evpn
      allocate-index 1
      advertise l2vpn evpn
      redistribute connected
```

---

## Endpoint Provisioning

### VM Discovery and Registration

```bash
# Option 1: VMware Integration
Fabric > External Connectivity > vCenter
├─ Add vCenter URL: 10.0.1.100
├─ Username: administrator@vsphere.local
├─ Password: ****
└─ Associate with domains

# VMs automatically discovered

# Option 2: Manual EPG assignment
# Tag VM with EPG label via VMware
# ACI automatically provisions VLAN
```

### Bare-Metal Server Registration

```bash
# Via APIC:
Tenants > Tenant-A > Endpoints > Static Endpoints

# Configuration:
EPG: Web-Tier-EPG
Leaf: Leaf-2
Interface: eth1
VLAN: 1001
IP: 10.100.0.50/24
MAC: aa:bb:cc:dd:ee:ff
```

---

## Monitoring and Troubleshooting

### Health Monitoring

```bash
# Via APIC GUI:
System > Health > Overall Health

# Expected: Green (all healthy)

# Check components:
├─ APIC health
├─ Leaf health
├─ Spine health
├─ Controller communication
└─ Data plane connectivity
```

### Flow Verification

```bash
# Via APIC GUI:
Tenants > Tenant-A > Application Profiles > Flows

# View:
├─ Active contracts
├─ Traffic flow statistics
├─ Denied connections
└─ Policy evaluation
```

### Endpoint Tracing

```bash
# Via APIC CLI:
apic1# acidiag fnvread

# Trace endpoints:
apic1# show endpoint summary
apic1# show endpoint interface Leaf102 ethernet 1/10

# Expected:
# Endpoint: 10.100.0.10
# MAC: 11:22:33:44:55:66
# EPG: Web-Tier-EPG
# VLAN: 1001
```

---

## Validation and Testing

### Post-Deployment Tests

```bash
# Test 1: Same subnet communication
VM1 (10.100.0.10) → ping VM2 (10.100.0.20)
# Should succeed

# Test 2: Contract enforcement
VM1 → ping DB-server (10.200.0.10)
# Should fail initially (no contract)
# Succeed after contract added

# Test 3: External connectivity
Internal VM → External Host
# Should route via L3Out

# Test 4: Failover
Disable primary leaf
# Traffic should reroute to alternate leaf
```

### Performance Baseline

```bash
# Using iperf:
# Terminal 1 (server):
iperf3 -s -i 1

# Terminal 2 (client):
iperf3 -c 10.100.0.20 -t 60 -i 1

# Expected: Near line rate if no contracts blocking
```

---

## Best Practices

### Design Principles
- **Application-centric**: Policy by application, not network
- **Zero-trust**: Deny all by default, allow explicitly
- **Scalability**: Plan for 3-5 year growth
- **Redundancy**: No single points of failure

### Operational Procedures
- **Change management**: Test in lab first
- **Documentation**: Keep diagrams and configs updated
- **Monitoring**: Establish baselines, alert on anomalies
- **Training**: Ensure ops team understands fabric

### Security
- **Contract-based filtering**: Microsegmentation
- **Endpoint isolation**: VPC-like per-application
- **Audit logging**: Track all policy changes
- **RBAC**: Role-based access control for APIC

---

## Common Deployment Issues

### Issue: EPG Not Reaching Bridge Domain

**Symptoms**:
- Endpoints not learning
- Traffic drops at leaf

**Solution**:
```bash
# 1. Verify EPG-BD attachment:
show run interface ethernet 1/10

# 2. Check VLAN configuration:
show vlan id 1001

# 3. Verify encapsulation:
show vlan id 1001 | include encap
```

### Issue: Contract Not Enforcing

**Symptoms**:
- Traffic allowed when it shouldn't be

**Solution**:
```bash
# 1. Verify contract pushed from APIC:
apic1# show application status

# 2. Check policy in leaf:
leaf1# show platform internal hal l4log
```

---

## Next Steps

1. **Design review** with Cisco architect
2. **PoC deployment** on 2-3 devices
3. **Integration testing** with existing systems
4. **Staff training** before production
5. **Runbook creation** for common tasks
6. **Phased rollout** to production fabric
