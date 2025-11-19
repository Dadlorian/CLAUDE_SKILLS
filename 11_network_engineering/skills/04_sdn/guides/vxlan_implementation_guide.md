# VXLAN Implementation Guide

## VXLAN Planning

### Design Decisions

**1. Underlay Network**
```
Option A: Existing IP network
├─ Advantage: Quick deployment
├─ Disadvantage: Shared bandwidth
└─ Use case: Small deployments

Option B: Dedicated underlay
├─ Advantage: Performance, isolation
├─ Disadvantage: Cost, complexity
└─ Use case: Large deployments
```

**2. Control Plane**
```
Option A: Multicast flooding
├─ MAC learning: Dynamic from traffic
├─ Requirement: Multicast routing
└─ Use case: Small networks

Option B: BGP EVPN
├─ MAC learning: Controlled distribution
├─ Requirement: BGP infrastructure
└─ Use case: Production networks
```

**3. VTEP Placement**
```
Location options:
├─ Hypervisors (distributed)
├─ TOR switches (aggregated)
├─ Dedicated appliances
└─ Combination (hybrid)
```

### Capacity Planning

```
MTU Calculation:
Physical MTU: 1500 bytes (standard)
VXLAN overhead: 50 bytes
  ├─ Outer Ethernet: 14 bytes
  ├─ Outer IP: 20 bytes (IPv4)
  ├─ UDP: 8 bytes
  ├─ VXLAN: 8 bytes
  └─ CRC: (accounted separately)
Effective payload: 1450 bytes

Recommendation: Set physical MTU to 1550-1600 (jumbo frames)
```

---

## Step-by-Step VXLAN Configuration

### Step 1: Verify Underlay Connectivity

```bash
# 1. Confirm IP reachability between all VTEPs
# VTEP-A to VTEP-B
ping 10.0.0.2  # From VTEP-A (10.0.0.1)

# 2. Verify MTU
# Linux
ip link show
# Example output: mtu 1500

# 3. Test with large packets
ping -M do -s 1472 10.0.0.2
# -M do: Don't fragment
# -s 1472: Test close to limit
```

### Step 2: Enable VXLAN on Switches/Hypervisors

**On Cisco Nexus Switches**:
```
! Enable features
feature nv overlay
feature vn-segment-vlan-based
feature bgp
feature evpn

! Configure VTEP
nv overlay evpn
!
interface nve1
  no shutdown
  source-interface Loopback1
  member vni 1001
    mcast-group 224.1.1.1
  member vni 1002
    mcast-group 224.1.1.2
```

**On Linux with OVS**:
```bash
# Create VXLAN tunnel
ovs-vsctl add-port br0 vxlan0 -- set interface vxlan0 type=vxlan options:remote_ip=10.0.0.2 options:local_ip=10.0.0.1 options:key=1001

# Verify
ovs-vsctl show
# Example output:
# Port "vxlan0"
#   Interface "vxlan0"
#     type: vxlan
#     options: {key="1001", local_ip="10.0.0.1", remote_ip="10.0.0.2"}
```

### Step 3: Configure VNIs and Bridges

**Create VXLAN Network (VNI 1001)**:
```bash
# On each VTEP

# Cisco:
vlan 1001
  vn-segment 1001

interface vlan1001
  ip address 10.100.0.1 255.255.255.0
  no shutdown

# Linux OVS:
ovs-vsctl add-br br-vxlan
ovs-vsctl set Bridge br-vxlan datapath_type=system
ip link add link br-vxlan vlan1001 type vlan id 1001
ip addr add 10.100.0.1/24 dev vlan1001
ip link set vlan1001 up
```

### Step 4: Configure BGP EVPN (Recommended)

**On Spine Switches (Route Reflector)**:
```
router bgp 65000
  neighbor 10.1.1.1 remote-as 65000  ! Leaf-1
  neighbor 10.1.1.2 remote-as 65000  ! Leaf-2
  !
  address-family l2vpn evpn
    neighbor 10.1.1.1 activate
    neighbor 10.1.1.2 activate
    neighbor 10.1.1.1 route-reflector-client
    neighbor 10.1.1.2 route-reflector-client
    advertise-all-vni
```

**On Leaf Switches (VTEP)**:
```
router bgp 65000
  neighbor 10.1.0.1 remote-as 65000  ! Spine-1
  neighbor 10.1.0.2 remote-as 65000  ! Spine-2
  !
  address-family l2vpn evpn
    neighbor 10.1.0.1 activate
    neighbor 10.1.0.2 activate
    advertise-all-vni
    default-information originate
```

### Step 5: Configure MAC-VRF

```
! Cisco example
vlan 1001
  vn-segment 1001

interface nve1
  member vni 1001
    mcast-group 224.1.1.1
    associate-vrf  ! For inter-subnet routing

! Alternative: Point to point
interface nve1
  member vni 1001
    vrf associate vrf-a
    ingress-replication protocol bgp
```

### Step 6: Enable Routing Between VNIs

**Symmetric IRB (Recommended)**:
```
! Cisco
interface vlan1001
  vrf member vrf-a
  ip address 10.100.0.254 255.255.255.0
  fabric forwarding mode anycast-gateway

! BGP EVPN Type 5 (Route advertisement)
router bgp 65000
  address-family ipv4 unicast
    advertise l2vpn evpn
```

---

## VXLAN with Multicast

### Configure Multicast Routing

```
! Sparse mode multicast
ip multicast-routing
ip pim rp-address 10.0.0.254

! On all switches
interface GigabitEthernet0/0/0
  ip pim sparse-mode

! Configure VXLAN for multicast
interface nve1
  member vni 1001
    mcast-group 224.1.1.1
```

### Verify Multicast Operation

```bash
# Show RP
show ip pim rp-hash 224.1.1.1

# Show group members
show ip pim group-map

# Test multicast
mping -I 10.0.0.1 224.1.1.1
```

---

## VXLAN Testing and Verification

### Step 1: Verify VTEP Status

```bash
# Cisco
show nve interface
# Example:
# Interface: nve1, State: Up
# Source-Interface: Loopback1 (address: 10.0.0.1)

show nve vni
# Example:
# NVE-VNI    VLAN   VRF    MulticastGroup   Mode   Flags
# 1001       1001   -      224.1.1.1        flood  oper
```

### Step 2: Verify MAC Learning

```bash
# Cisco
show mac address-table vlan 1001

# Expected output:
# vlan   mac address   type        ports
# 1001   aabb.cc00.1111  dynamic   nve1(10.0.0.2/1001)

# Linux
bridge fdb show
# Expected: <mac> dev vxlan0 dst <remote_vtep> src_vni <vni>
```

### Step 3: Test Connectivity

```bash
# VM1 on VTEP-A (IP 10.100.0.10)
# VM2 on VTEP-B (IP 10.100.0.20)

# From VM1:
ping 10.100.0.20
# Should succeed

# Verify using ARP:
arp -a
# Should show 10.100.0.20 as reachable

# Packet capture:
tcpdump -i eth0 -w vxlan-test.pcap host 10.100.0.20
# Examine outer headers showing VXLAN encapsulation
```

### Step 4: Verify BGP EVPN Routes

```bash
# On Leaf switch
show bgp l2vpn evpn summary
# Should show neighbor UP

show bgp l2vpn evpn neighbors
# Check for active sessions

show bgp l2vpn evpn
# Type 2 routes: MAC/IP advertisements
# Type 5 routes: IP prefixes
```

---

## Performance Optimization

### 1. Adjust MTU

```bash
# Linux
ip link set eth0 mtu 1600

# Cisco
interface GigabitEthernet0/0/0
  mtu 1600

# ESXi
esxcli network nic get -n vmnic0  # Check current
esxcli network nic set -n vmnic0 -m 1600  # Set new
```

### 2. Enable Hardware Offload

```bash
# Linux OVS with DPDK
# Install DPDK libraries first

# Configure DPDK
ovs-vsctl set Open_vSwitch . other_config:dpdk-init=true
ovs-vsctl set Open_vSwitch . other_config:dpdk-lcore-mask=0x1

# Create DPDK netdev
ovs-vsctl set Interface dpdk0 type=dpdk options:dpdk-devargs=0000:04:00.0
```

### 3. Tune VXLAN Parameters

```bash
# Linux kernel parameters
sysctl -w net.ipv4.ip_forward=1
sysctl -w net.ipv4.conf.all.rp_filter=0

# OVS configuration
ovs-vsctl set Open_vSwitch . other_config:max-idle=30000
```

---

## High Availability Configuration

### VXLAN with Redundancy

```
VM connects to two hypervisors
  ├─ Hypervisor-A (VTEP-A)
  ├─ Hypervisor-B (VTEP-B)
  └─ Active-Backup or Active-Active

VXLAN tunnel
  ├─ VTEP-A ←→ VTEP-B (UDP 4789)
  ├─ VTEP-A ←→ VTEP-C (UDP 4789)
  └─ VTEP-B ←→ VTEP-C (UDP 4789)
```

### Dual Uplinks

```bash
# Cisco - Port Channel
interface port-channel100
  ip address 10.0.0.1 255.255.255.0

interface GigabitEthernet0/0/0
  channel-group 100 mode active

interface GigabitEthernet0/0/1
  channel-group 100 mode active

interface nve1
  source-interface Loopback1
```

---

## Troubleshooting VXLAN

### Issue: VMs Can't Ping Across VXLAN

```bash
# Debug steps:

# 1. Check VTEP status
show nve interface
# Status should be UP

# 2. Check VXLAN tunnel
show nve peers
# Both VTEPs should see each other

# 3. Check MAC learning
show mac address-table dynamic vlan 1001
# Remote MACs should show nve1 as port

# 4. Check multicast (if using)
show ip igmp groups
# Multicast group should show as active

# 5. Packet capture
tcpdump -i <vxlan_interface> -w debug.pcap
# Analyze outer/inner headers
```

### Issue: High Packet Loss on VXLAN

```bash
# 1. Check MTU configuration
show interface <interface> | include mtu

# 2. Monitor packet drops
show interface nve1 | include drops

# 3. Check underlay latency
ping -M do -s 1472 <remote_vtep>
# If high loss, MTU is likely issue

# Solution: Increase MTU as described above
```

### Issue: BGP EVPN Not Establishing

```bash
# 1. Verify BGP configuration
show bgp l2vpn evpn summary
# Neighbors should show "Up"

# 2. Check BGP errors
show bgp l2vpn evpn neighbors | include State

# 3. Verify local VLAN/VNI mapping
show vlan id 1001
show vn-segment vlan 1001

# 4. Check loopback reachability
ping <remote_loopback>
```

---

## Monitoring and Maintenance

### Key Metrics to Monitor

```
1. VTEP Status
   - nve1 interface status
   - Source loopback reachability
   - BGP neighbor state

2. MAC Learning
   - Dynamic MAC count per VNI
   - ARP learning rate
   - Duplicate MAC detection

3. Performance
   - VXLAN encapsulation latency
   - Packet loss per tunnel
   - Underlay bandwidth utilization

4. BGP EVPN
   - Route advertisements (Type 2, Type 5)
   - Route convergence time
   - Peer state stability
```

### Regular Maintenance Tasks

```
Weekly:
☐ Review VTEP status
☐ Check for spanning tree issues
☐ Monitor CPU/memory on VTEPs

Monthly:
☐ Review and update topology diagram
☐ Analyze traffic patterns
☐ Verify disaster recovery plan

Quarterly:
☐ Full network failover test
☐ Update VXLAN documentation
☐ Review scaling requirements
```

---

## Migration from Multicast to BGP EVPN

### Phased Approach

```
Phase 1: Run parallel
├─ BGP EVPN enabled alongside multicast
├─ Control plane via EVPN
└─ Multicast still operational

Phase 2: Gradual cutover
├─ Move one VNI at a time
├─ Disable multicast on completed VNIs
└─ Monitor for issues

Phase 3: Complete
├─ Disable multicast entirely
├─ BGP EVPN becomes primary control plane
└─ Remove multicast configuration
```

---

## Best Practices Summary

1. **Planning**: Design for underlay robustness
2. **MTU**: Always use jumbo frames in production
3. **Control Plane**: Use BGP EVPN for scalability
4. **Redundancy**: Multi-VTEP per location
5. **Monitoring**: Track VTEP health continuously
6. **Testing**: Validate before production deployment
7. **Documentation**: Keep topology and configs updated
