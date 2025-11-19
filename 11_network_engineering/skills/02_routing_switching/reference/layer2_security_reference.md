# Layer 2 Security Quick Reference

## Port Security Overview

- **Purpose:** Prevent MAC address flooding and unauthorized access
- **Scope:** Per-port configuration on access ports
- **Violation Actions:** Protect, Restrict, Shutdown

## Port Security Configuration

```
interface GigabitEthernet0/1
  switchport port-security
  switchport port-security maximum 1
  switchport port-security mac-address [MAC | sticky]
  switchport port-security violation [protect | restrict | shutdown]
```

### Violation Actions

| Action | Frames Dropped | Violation Count | Alert | Port Status |
|--------|----------------|-----------------|-------|-------------|
| Protect | Yes | No | No | Active |
| Restrict | Yes | Yes | SNMP | Active |
| Shutdown | Yes | Yes | SNMP, Syslog | Disabled (err-disabled) |

## MAC Address Learning

### Static Sticky MAC
```
! Manual MAC entry
switchport port-security mac-address aabb.ccdd.eeff

! Dynamic sticky learning
switchport port-security mac-address sticky
! Saves to running-config after sticky learning
```

### Aging
```
! MAC address aging
switchport port-security aging type [absolute | inactivity]
switchport port-security aging time 120  ! Minutes
```

## Port Err-Disabled State

```
! View err-disabled ports
show interfaces status err-disabled

! Re-enable port
interface GigabitEthernet0/1
  shutdown
  no shutdown

! Or auto-recovery
errdisable recovery cause psecure-violation
errdisable recovery interval 300  ! Seconds
```

## DHCP Snooping

- **Purpose:** Prevent unauthorized DHCP servers and rogue clients
- **Scope:** VLAN-wide configuration
- **Trusted/Untrusted Ports:** Uplink vs access ports

```
! Enable DHCP snooping globally
ip dhcp snooping

! Enable per VLAN
ip dhcp snooping vlan 10,20,30

! Configure trusted ports (uplinks)
interface GigabitEthernet0/48
  ip dhcp snooping trust

! Configure rate limiting
ip dhcp snooping limit rate 100  ! Per port

! View DHCP snooping bindings
show ip dhcp snooping binding
```

### DHCP Snooping Binding Database

- **Format:** MAC, IP, lease time, VLAN, port
- **Storage:** RAM (automatic) or file (persistent)

```
ip dhcp snooping database tftp://192.168.1.1/dhcp_bindings
```

## Dynamic ARP Inspection (DAI)

- **Purpose:** Prevent ARP spoofing and MAC table poisoning
- **Mechanism:** Verify ARP packets against DHCP binding table
- **Trusted/Untrusted:** Same as DHCP snooping

```
! Enable DAI globally
ip arp inspection vlan 10,20,30

! Configure trusted ports
interface GigabitEthernet0/48
  ip arp inspection trust

! Configure ARP ACLs for static IPs
arp access-list STATIC_ARP
  permit ip host 10.0.0.1 mac host aabb.ccdd.eeff
  deny ip any mac any

! Apply ARP ACL
ip arp inspection filter STATIC_ARP vlan 10

! View DAI configuration
show ip arp inspection
show ip arp inspection statistics
```

## BPDU Guard and Filtering

### BPDU Guard
```
! Enable on PortFast ports
interface GigabitEthernet0/1
  spanning-tree bpduguard enable

! Global on all PortFast ports
spanning-tree portfast bpduguard default

! View BPDU Guard violations
show spanning-tree inconsistency
```

### BPDU Filter
```
! Disable BPDU on access port (use with caution)
interface GigabitEthernet0/1
  spanning-tree bpdufilter enable

! Prevent sending BPDUs on untrusted ports
spanning-tree portfast bpdufilter default
```

## Root Guard

```
! Prevent port from becoming root port
interface GigabitEthernet0/1
  spanning-tree guard root

! View root guard violations
show spanning-tree inconsistency
```

## VLAN Access Control Lists (VACLs)

```
! Create VACL map
vlan access-map SALES 10
  match ip address 100
  action forward

vlan access-map SALES 20
  action forward

! Apply to VLANs
vlan filter SALES vlan-list 10,20,30

! View VACL
show vlan access-map
show vlan filter
```

## Private VLAN (PVLAN)

- **Primary VLAN:** Communication allowed
- **Isolated VLAN:** No communication between ports
- **Community VLAN:** Communication within community only

```
! Configure PVLAN
vlan 100
  private-vlan primary
vlan 101
  private-vlan isolated
vlan 102
  private-vlan community

vlan 100
  private-vlan association 101,102

! Apply to ports
interface FastEthernet0/1
  switchport private-vlan host-association 100 101

! Trunk PVLAN
interface GigabitEthernet0/1
  switchport mode private-vlan trunk

! View PVLAN
show vlan private-vlan
```

## 802.1X Port-Based Authentication

```
! Enable AAA
aaa new-model
aaa authentication dot1x default group radius

! Enable 802.1X globally
dot1x system-auth-control

! Configure port
interface GigabitEthernet0/1
  authentication port-control auto
  dot1x pae authenticator
  dot1x timeout tx-period 30
  dot1x timeout reattempt-period 30
  dot1x max-reauth-req 2

! View 802.1X status
show dot1x all
show dot1x statistics all
```

## Storm Control

```
! Configure storm control
interface GigabitEthernet0/1
  storm-control broadcast level 100  ! Percentage
  storm-control multicast level 100
  storm-control unicast level 100
  storm-control action [shutdown | trap]
  storm-control logging
```

## DHCP Snooping vs DAI Comparison

| Feature | DHCP Snooping | DAI |
|---------|----------------|-----|
| Prevents | Rogue DHCP servers | ARP spoofing |
| Based on | DHCP binding table | ARP packets |
| Scope | DHCP clients | All ARP traffic |
| Impact | DHCP process only | All ARP |
| Overhead | Low | Medium |
| Static IPs | Requires ARP ACL | Requires ARP ACL |

## Security Best Practices

1. **Port Security:**
   - Set maximum MAC to 1 on access ports
   - Use sticky MAC for learning
   - Set violation action to shutdown
   - Monitor err-disabled ports

2. **DHCP Snooping:**
   - Enable globally
   - Mark uplinks as trusted
   - Store bindings persistently
   - Use with DAI for ARP security

3. **Dynamic ARP Inspection:**
   - Enable for VLANs with DHCP snooping
   - Configure ARP ACLs for static IPs
   - Monitor false positives
   - Combine with DHCP snooping

4. **STP Security:**
   - Enable BPDU Guard on all access ports
   - Enable Root Guard on trunk ports
   - Implement PortFast on access ports
   - Monitor topology changes

5. **VLAN Security:**
   - Use VACLs for VLAN filtering
   - Implement PVLANs for isolation
   - Document VLAN policies
   - Test filtering rules

6. **General:**
   - Implement defense-in-depth
   - Monitor switch resources
   - Log security events
   - Test failover scenarios
   - Keep switch firmware current
