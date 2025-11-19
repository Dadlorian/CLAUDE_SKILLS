# VLAN Design and Implementation Guide

## VLAN Numbering Scheme

### Recommended Allocation Strategy
```
1-99:       Reserved/Management VLANs
1:          Default (do not use for user traffic)
10-19:      Management/Admin VLANs
20-99:      Reserved future use

100-199:    Engineering/Production VLANs
200-299:    Marketing/Operations VLANs
300-399:    Finance/HR VLANs
400-499:    Guest/Visitor VLANs
500-999:    Department-specific VLANs
1000-1001:  Reserved (edge cases)
1006-4094:  Extended range (if needed)
```

### VLAN Naming Convention
```
! Descriptive names
vlan 10
  name Management

vlan 100
  name Engineering

vlan 200
  name Marketing

vlan 300
  name Finance

vlan 500
  name Guest-WiFi

vlan 999
  name Voice-VLAN
```

## Access Port Configuration

### Single VLAN Assignment
```
interface GigabitEthernet0/1
  description User-Port-Floor1
  switchport mode access
  switchport access vlan 100    ! Engineering VLAN
  spanning-tree portfast
  spanning-tree bpduguard enable
  switch port port-security
  switchport port-security maximum 1
  switchport port-security mac-address sticky
```

### Voice VLAN (IP Phone)
```
interface GigabitEthernet0/2
  description IP-Phone-Port
  switchport mode access
  switchport access vlan 100           ! Data VLAN
  switchport voice vlan 999            ! Voice VLAN
  mls qos trust cos                    ! Trust CoS marking from phone
  no shutdown
```

## Trunk Configuration Design

### Inter-Switch Trunks
```
interface GigabitEthernet0/48
  description Trunk-to-Switch-B
  switchport mode trunk
  switchport trunk encapsulation dot1q
  switchport nonegotiate
  switchport trunk native vlan 99      ! Management VLAN
  switchport trunk allowed vlan 10-99,100-199
  no shutdown
```

### Trunk Allowed VLAN Strategy
```
! Approach 1: Explicit allow list
switchport trunk allowed vlan 10,20,99,100-199,200-299

! Approach 2: Block specific VLANs
switchport trunk allowed vlan except 1,1002-1005

! Approach 3: All VLANs (less secure)
switchport trunk allowed vlan all
```

## Multi-Layer VLAN Design

### Distribution-Core Architecture
```
CORE LAYER (Inter-VLAN Routing)
├── VLAN 99 (Management)
├── VLAN 100-199 (User Data)
└── VLAN 200-299 (Services)
        ↓
DISTRIBUTION LAYER (VLAN Termination)
├── Switch-A (Access Aggregation)
│   └── VLAN Trunks to Core
└── Switch-B (Access Aggregation)
    └── VLAN Trunks to Core
        ↓
ACCESS LAYER (User Ports)
├── Floor 1 (VLAN 100)
├── Floor 2 (VLAN 200)
└── Floor 3 (VLAN 300)
```

## VLAN Segmentation by Function

### Department-Based Segmentation
```
vlan 100
  name Engineering-Dept

vlan 200
  name Finance-Dept

vlan 300
  name Manufacturing-Dept

! Physical location independent
! Users move, VLAN assignment updates
```

### Location-Based Segmentation (Alternative)
```
vlan 110
  name Building-A-Floor1

vlan 120
  name Building-A-Floor2

vlan 210
  name Building-B-Floor1
```

### Hybrid Approach (Recommended)
```
vlan 100
  name Corporate-Office   ! Primary department

vlan 500
  name WiFi-Guest         ! Concurrent guest access

vlan 600
  name IoT-Devices        ! IoT segmentation

vlan 700
  name Voice-Phones       ! VoIP separate VLAN
```

## Inter-VLAN Routing Design

### Router-on-Stick (Single Router, Multiple Interfaces)
```
! Router configuration
interface GigabitEthernet0/0
  no shutdown

interface GigabitEthernet0/0.100
  encapsulation dot1Q 100
  ip address 10.1.0.1 255.255.255.0

interface GigabitEthernet0/0.200
  encapsulation dot1Q 200
  ip address 10.2.0.1 255.255.255.0

! Switch configuration
interface GigabitEthernet0/48
  switchport mode trunk
  switchport trunk encapsulation dot1q
  switchport trunk allowed vlan 100,200

! Traffic flows through router via trunk link
```

### Multi-Switch Inter-VLAN (Layer 3 Switch)
```
! Layer 3 Switch with SVI
ip routing

interface Vlan100
  ip address 10.1.0.1 255.255.255.0
  no shutdown

interface Vlan200
  ip address 10.2.0.1 255.255.255.0
  no shutdown

interface Vlan300
  ip address 10.3.0.1 255.255.255.0
  no shutdown

! Routing protocol (OSPF/EIGRP) for dynamic routing
router ospf 1
  network 10.0.0.0 0.255.255.255 area 0
```

## Private VLAN Implementation

### Use Case: Hosting Environment
```
vlan 100
  private-vlan primary

vlan 101
  private-vlan isolated

vlan 102
  private-vlan community

vlan 100
  private-vlan association 101,102

! Server port (can talk to all)
interface GigabitEthernet0/1
  switchport private-vlan host-association 100 101

! Isolated tenant port (can only talk to gateway)
interface GigabitEthernet0/2
  switchport private-vlan host-association 100 101

! Community port (can talk within community)
interface GigabitEthernet0/3
  switchport private-vlan host-association 100 102
```

## Voice VLAN Deployment

### VoIP QoS with Voice VLAN
```
! Switch port configuration
interface GigabitEthernet0/1
  switchport mode access
  switchport access vlan 100       ! Data VLAN
  switchport voice vlan 500        ! Voice VLAN
  mls qos trust cos               ! Trust COS from phone

! Voice VLAN subnet
interface Vlan500
  ip address 10.99.0.1 255.255.255.0

! DHCP for VoIP phones
ip dhcp pool VOICE_DHCP
  network 10.99.0.0 255.255.255.0
  option 150 10.99.0.1  ! Phone server IP
```

## Guest and Visitor VLAN

### Guest Network Isolation
```
vlan 400
  name Guest-WiFi

interface Vlan400
  ip address 192.168.100.1 255.255.255.0

! Guest portal via VLAN
! Restricted access (no internal resources)
! Separate DHCP pool
ip dhcp pool GUEST_POOL
  network 192.168.100.0 255.255.255.0
  default-router 192.168.100.1
  domain-name guest.example.com
```

## VLAN Security Best Practices

### Port Security on Access Ports
```
interface GigabitEthernet0/1
  switchport port-security
  switchport port-security maximum 1
  switchport port-security mac-address sticky
  switchport port-security violation shutdown
  spanning-tree bpduguard enable
```

### VLAN Hopping Prevention
```
! Set consistent native VLAN on all trunks
interface GigabitEthernet0/48
  switchport mode trunk
  switchport trunk native vlan 99
  switchport nonegotiate
  switchport trunk allowed vlan 10-99,100-299
```

### DHCP Snooping per VLAN
```
ip dhcp snooping
ip dhcp snooping vlan 100,200,300

interface GigabitEthernet0/1
  ip dhcp snooping trust  ! Uplink port

interface GigabitEthernet0/2
  ip dhcp snooping limit rate 100  ! User port
```

## VLAN Migration Strategy

### Step-by-Step Migration
```
1. Plan new VLAN design
2. Create new VLANs on all switches
3. Configure new VLAN interfaces
4. Migrate users gradually (1-2 per day)
5. Monitor for issues
6. Remove old VLAN after validation
```

### Pre-Migration Validation
```
! Verify VLAN exists globally
show vlan brief

! Verify trunk configuration
show interfaces trunk

! Verify routing
show ip route
show ip vlan
```

## Monitoring and Troubleshooting

### VLAN Verification
```
show vlan
show vlan id 100
show vlan name Engineering

show interfaces GigabitEthernet0/1 switchport
show interfaces trunk
show interfaces status

show vlan access-map
show vlan filter
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| VLAN not visible | Not created on switch | Create VLAN with `vlan 100` command |
| Port won't stay in VLAN | Misconfig or err-disabled | Fix config, reset port |
| Trunk not working | Native VLAN mismatch | Set same native VLAN on both sides |
| Users can't communicate | Inter-VLAN routing missing | Configure SVI or router-on-stick |
| Traffic flooding | Spanning-tree issue | Check STP status, verify roots |

## Deployment Checklist

### Pre-Deployment
- [ ] Document VLAN design and numbering
- [ ] Plan IP addressing for each VLAN
- [ ] Identify inter-VLAN routing method
- [ ] Plan voice VLAN if needed
- [ ] Design security controls (DHCP snooping, etc)

### Configuration
- [ ] Create all VLANs on all switches
- [ ] Configure access ports with correct VLANs
- [ ] Configure trunk ports with allowed VLANs
- [ ] Set native VLAN on trunks
- [ ] Configure inter-VLAN routing (SVI or router)
- [ ] Enable port security on access ports
- [ ] Implement DHCP snooping if needed
- [ ] Verify spanning-tree convergence

### Verification
- [ ] Verify all VLANs visible: `show vlan brief`
- [ ] Check trunk status: `show interfaces trunk`
- [ ] Verify inter-VLAN routing
- [ ] Test user connectivity
- [ ] Verify QoS (if voice VLAN)

### Production Monitoring
- [ ] Monitor VLAN membership changes
- [ ] Track spanning-tree topology changes
- [ ] Monitor inter-VLAN traffic
- [ ] Alert on DHCP snooping violations
- [ ] Monitor trunk port status

## Best Practices Summary

1. **Plan thoroughly:** Document VLAN design before deployment
2. **Use descriptive names:** Easier identification and troubleshooting
3. **Consistent native VLAN:** All trunks use same native VLAN
4. **Disable DTP:** Use `switchport nonegotiate` on trunks
5. **Port security:** Enable on all access ports
6. **Segmentation:** Isolate guest/IoT/voice traffic
7. **Inter-VLAN routing:** Use Layer 3 switch for scalability
8. **Monitoring:** Track VLAN membership and changes
9. **Documentation:** Maintain accurate VLAN database
10. **Testing:** Validate inter-VLAN connectivity before production
