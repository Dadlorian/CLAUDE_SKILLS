# VRF Configuration Guide

## VRF Fundamentals

### Virtual Routing and Forwarding

**VRF enables:**
- Separate routing domains on same router
- Customer/tenant isolation
- Parallel routing tables
- Independent IP addressing

### VRF Types

| Type | Use | Isolation | Complexity |
|------|-----|-----------|-----------|
| VRF-Lite | Small deployments | Layer 3 only | Low |
| MPLS VPN | Service provider | Layer 3 + MPLS | High |
| VRF IPv6 | Dual-stack networks | IPv4 and IPv6 | Medium |

## VRF Creation and Management

### Basic VRF Creation
```
vrf definition CUSTOMER-A
  description "Customer A Network"
  rd 65000:100           ! Route Distinguisher (ASN:number)
  route-target export 65000:100
  route-target import 65000:100
```

### RD (Route Distinguisher)
```
! Format: ASN:number or IP:number
rd 65000:100    ! ASN 65000, customer 100
rd 192.168.1.1:100  ! Router IP, customer 100

! Must be unique across all VRFs
! Same VRF can have multiple RDs for import/export
```

### Route Targets (RT)
```
route-target export 65000:100  ! Routes from this VRF
route-target import 65000:100  ! Accept these routes

! Export to other VRF
route-target export 65000:200
route-target import 65000:200

! Selective import/export
route-target export 65000:100
route-target import 65000:100  ! Allows same VRF import
route-target import 65000:200  ! Also import from VRF-B
```

## Interface Assignment to VRF

### Assign Interface to VRF
```
interface GigabitEthernet0/1
  vrf forwarding CUSTOMER-A
  ip address 10.0.0.1 255.255.255.0
  no shutdown

! Note: IP address lost during vrf forwarding assignment
! Must re-configure IP after VRF assignment
```

### VRF Loopback Interface
```
interface Loopback 100
  vrf forwarding CUSTOMER-A
  ip address 192.168.100.1 255.255.255.255
  ! Loopback for source addressing in VRF
```

## IGP Configuration in VRF

### OSPF in VRF
```
router ospf 1 vrf CUSTOMER-A
  router-id 192.168.100.1
  network 10.0.0.0 0.0.255.255 area 0
  network 192.168.1.0 0.0.0.255 area 0

! Separate OSPF instance per VRF
router ospf 2 vrf CUSTOMER-B
  router-id 192.168.200.1
  network 10.1.0.0 0.0.255.255 area 0
```

### EIGRP in VRF
```
router eigrp CUSTOMER-A
  address-family ipv4 unicast autonomous-system 100 vrf CUSTOMER-A
    network 10.0.0.0 0.255.255.255
    network 192.168.1.0 0.0.0.255
  exit-address-family

router eigrp CUSTOMER-B
  address-family ipv4 unicast autonomous-system 100 vrf CUSTOMER-B
    network 10.1.0.0 0.255.255.255
```

## BGP in VRF

### BGP Peering in VRF
```
router bgp 65000
  bgp router-id 192.168.100.1

  address-family ipv4 vrf CUSTOMER-A
    neighbor 10.0.0.2 remote-as 65001
    neighbor 10.0.0.2 activate
    network 192.168.1.0 mask 255.255.255.0
    aggregate-address 192.168.0.0 255.255.0.0
  exit-address-family

  address-family ipv4 vrf CUSTOMER-B
    neighbor 10.1.0.2 remote-as 65002
    neighbor 10.1.0.2 activate
    network 192.168.2.0 mask 255.255.255.0
  exit-address-family
```

## Static Routes in VRF

### VRF Static Routes
```
ip route vrf CUSTOMER-A 192.168.0.0 255.255.0.0 10.0.0.254
ip route vrf CUSTOMER-B 192.168.0.0 255.255.0.0 10.1.0.254

! Recursive lookup in VRF routing table
ip route vrf CUSTOMER-A 10.2.0.0 255.255.0.0 192.168.1.1

! Default route
ip route vrf CUSTOMER-A 0.0.0.0 0.0.0.0 10.0.0.254
```

## VRF Route Leaking

### Controlled Route Sharing
```
! Re-export routes from CUSTOMER-A to CUSTOMER-B
route-map LEAK-A-TO-B permit 10
  match ip address prefix-list CUSTOMER-A-ROUTES
  set extcommunity rt 65000:200 additive

! On CUSTOMER-A vrf:
router bgp 65000
  address-family ipv4 vrf CUSTOMER-A
    route-map LEAK-A-TO-B out
  exit-address-family

! Manually redistribute in CUSTOMER-B
router bgp 65000
  address-family ipv4 vrf CUSTOMER-B
    import map CUSTOMER-A-IMPORT
  exit-address-family
```

## VRF Troubleshooting and Verification

### Verify VRF Configuration
```
show vrf
show vrf detail
show vrf CUSTOMER-A

! Interfaces in VRF
show ip vrf interfaces
show ip vrf interfaces CUSTOMER-A

! Routing table per VRF
show ip route vrf CUSTOMER-A
show ip bgp vrf CUSTOMER-A
show ip eigrp vrf CUSTOMER-A as 100 topology
```

### Ping in VRF
```
ping vrf CUSTOMER-A 10.0.0.1
ping vrf CUSTOMER-A 192.168.1.1

! Verify connectivity in specific VRF
```

### Traceroute in VRF
```
traceroute vrf CUSTOMER-A 10.0.0.1
! Trace path within VRF
```

## VRF-Lite Configuration Pattern

### Simple Customer Isolation
```
! VRF 1: Sales Department
vrf definition SALES
  rd 65000:1
  route-target export 65000:1
  route-target import 65000:1

interface GigabitEthernet0/1
  vrf forwarding SALES
  ip address 10.1.0.1 255.255.255.0

interface GigabitEthernet0/2
  vrf forwarding SALES
  ip address 10.2.0.1 255.255.255.0

router ospf 1 vrf SALES
  network 10.1.0.0 0.0.0.255 area 0
  network 10.2.0.0 0.0.0.255 area 0

! VRF 2: Engineering Department
vrf definition ENGINEERING
  rd 65000:2
  route-target export 65000:2
  route-target import 65000:2

interface GigabitEthernet0/3
  vrf forwarding ENGINEERING
  ip address 10.3.0.1 255.255.255.0

! Separate routing, no inter-VLAN communication
```

## Central Services in VRF

### Shared Services VRF
```
! Global VRF for services
vrf definition SHARED-SERVICES
  rd 65000:999
  route-target export 65000:999
  route-target import 65000:999

! All customer VRFs import shared services
vrf definition CUSTOMER-A
  rd 65000:100
  route-target export 65000:100
  route-target import 65000:100
  route-target import 65000:999  ! Import shared services
```

## VRF Performance Considerations

### Routing Table Size
```
! Each VRF has separate routing table
show ip route vrf CUSTOMER-A summary
! View routes per VRF

! Total routers = sum of all VRF routing tables
```

### OSPF Scaling
```
! Each OSPF instance per VRF
! More VRFs = more SPF calculations
! Consider consolidation if SPF CPU high
```

### BGP Scalability
```
! BGP peering per VRF
! Each neighbor relationship separate
! More VRFs = more BGP sessions
```

## Management and Monitoring

### VRF Access Control
```
! Limit management access to specific VRF
line vty 0 4
  access-class MGMT-VRF in
  vrf MANAGEMENT  ! Management VRF

ip access-list standard MGMT-VRF
  permit 192.168.100.0 0.0.0.255
```

### SNMP in VRF
```
snmp-server trap-source vrf MANAGEMENT Loopback 0
! Traps sent from management VRF

snmp-server community PUBLIC RO vrf CUSTOMER-A
! SNMP access per VRF
```

### Syslog in VRF
```
logging source-interface Loopback 100 vrf CUSTOMER-A
! Syslog from specific VRF
```

## Multi-VRF Design Patterns

### Pattern 1: Customer Separation
```
VRF: CUSTOMER-A      VRF: CUSTOMER-B      VRF: CUSTOMER-C
├─ 10.0.0.0/8        ├─ 172.16.0.0/12     ├─ 192.168.0.0/16
├─ OSPF AS 100       ├─ OSPF AS 101       ├─ EIGRP AS 200
└─ BGP to upstream   └─ BGP to upstream   └─ BGP to upstream
```

### Pattern 2: Service Segregation
```
VRF: PRODUCTION      VRF: TESTING         VRF: MANAGEMENT
├─ User traffic      ├─ QA networks       ├─ Admin access
├─ Production IGP    ├─ Test IGP          ├─ Monitoring
└─ Production BGP    └─ Test BGP          └─ Syslog/SNMP
```

### Pattern 3: Hybrid Environment
```
VRF: CORPORATE       VRF: PARTNER         VRF: GUEST
├─ 10.0.0.0/8        ├─ 172.16.0.0/12     ├─ 192.168.100.0/24
├─ OSPF/EIGRP        ├─ BGP               ├─ Static routes
└─ Internal only     └─ With encryption   └─ Restricted access
```

## Deployment Checklist

### Pre-Deployment
- [ ] Define RD scheme (must be unique)
- [ ] Plan RT allocation
- [ ] Identify VRF requirements
- [ ] Design route leaking strategy
- [ ] Plan IP addressing per VRF

### Configuration
- [ ] Create VRF definitions
- [ ] Assign interfaces to VRFs
- [ ] Configure routing protocol in each VRF
- [ ] Configure route-targets for import/export
- [ ] Test connectivity per VRF

### Verification
- [ ] Verify VRF creation: `show vrf`
- [ ] Check interface assignment: `show ip vrf interfaces`
- [ ] Verify routing tables: `show ip route vrf [name]`
- [ ] Test ping/traceroute within VRF
- [ ] Validate route redistribution

### Monitoring
- [ ] Monitor VRF routing table sizes
- [ ] Track OSPF/EIGRP convergence per VRF
- [ ] Monitor BGP session stability
- [ ] Alert on VRF route loss
- [ ] Track performance per VRF

## Best Practices

1. **Consistent RD scheme:** Document allocation
2. **Import/export clarity:** Document RT strategy
3. **Separate IGPs:** One protocol per VRF preferred
4. **Route leaking control:** Explicit, documented
5. **Monitoring per VRF:** Track each separately
6. **Testing:** Lab test multi-VRF design
7. **Documentation:** Detailed VRF mapping
8. **Gradual deployment:** Add VRFs incrementally
9. **Scalability planning:** Consider growth
10. **Backup strategy:** Recovery per VRF
