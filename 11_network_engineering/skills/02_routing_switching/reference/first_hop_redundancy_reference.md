# First Hop Redundancy Protocol Quick Reference

## FHRP Comparison

| Feature | HSRP | VRRP | GLBP |
|---------|------|------|------|
| Standard | Cisco proprietary | RFC 5798 | Cisco proprietary |
| Active/Standby | One active | One master | One AVG (load balance) |
| Virtual MAC | 0000.0c07.acXX | 0000.5e00.01XX | 0000.07ac.XXXX |
| Multicast Address | 224.0.0.2 | 224.0.0.18 | 224.0.0.102 |
| Hello (default) | 3 seconds | 1 second | 3 seconds |
| Hold Time (default) | 10 seconds | 3 seconds | 10 seconds |
| Preemption | Optional | Default yes | N/A |
| IPv6 Support | Yes | Yes | Partial |
| Tracking | Yes | Yes | Yes |
| Load Balancing | No | No | Yes (4 AVF) |

## HSRP Configuration

### Basic Configuration
```
interface GigabitEthernet0/1
  ip address 10.0.0.1 255.255.255.0
  standby 1 ip 10.0.0.3
  standby 1 priority 150
  standby 1 preempt
```

### HSRP Groups (Versions)

| Version | Maximum Groups | MAC Format |
|---------|------------------|-----------|
| HSRPv1 | 256 | 0000.0c07.acXX (XX=group) |
| HSRPv2 | 4096 | 0000.0c9f.fXXX (XXX=group) |

```
! Change HSRP version
standby version 2
```

### HSRP States

| State | Purpose |
|-------|---------|
| Initial | Router just started or disabled |
| Learn | No hello heard, waiting to learn VIP |
| Listen | VIP known, not active/standby |
| Speak | Sending hellos, eligible for active |
| Standby | Backup for active router |
| Active | Primary gateway, forwarding traffic |

### HSRP Timers
```
! Millisecond-based (HSRPv2)
standby 1 timers msec 500 msec 1500

! Second-based (default)
standby 1 timers 3 10
```

### HSRP Priority
- **Range:** 0-255 (higher wins)
- **Default:** 100

```
standby 1 priority 150
```

### HSRP Preemption
```
! Enable preemption (immediately take over)
standby 1 preempt

! Preemption with delay
standby 1 preempt delay 30

! Minimum preemption delay
standby 1 preempt delay minimum 30

! Reload preemption delay
standby 1 preempt delay reload 300
```

### HSRP Authentication
```
! Clear-text (not recommended)
standby 1 authentication text PASSWORD

! MD5 Authentication (recommended)
standby 1 authentication md5 key-string MYKEY

! MD5 with key chain
key chain HSRP
  key 1
    key-string MYKEY

standby 1 authentication md5 key-chain HSRP
```

## VRRP Configuration

### Basic Configuration
```
interface GigabitEthernet0/1
  ip address 10.0.0.1 255.255.255.0
  vrrp 1 ip 10.0.0.3
  vrrp 1 priority 200
```

### VRRP Priority
- **Range:** 0-255 (higher wins)
- **Default:** 100
- **254:** Assigned to IP owner
- **0:** Owner renounced role

```
vrrp 1 priority 200
```

### VRRP Authentication (deprecated in RFC 5798)
```
! MD5 Authentication (RFC 3768)
vrrp 1 authentication md5 key-string MYKEY
```

### VRRP Timers
```
! Advertisement interval (default 1 second)
vrrp 1 timers advertise 1

! Master down interval (calculated)
vrrp 1 timers learn
```

### VRRP Preemption
```
! Preemption (enabled by default)
vrrp 1 preempt

! Disable preemption
no vrrp 1 preempt
```

### VRRP States
| State | Purpose |
|-------|---------|
| Initialize | Initial state, disabled |
| Backup | Standby, learning from master |
| Master | Active gateway |

## GLBP Configuration

### Basic Configuration
```
interface GigabitEthernet0/1
  ip address 10.0.0.1 255.255.255.0
  glbp 1 ip 10.0.0.3
  glbp 1 priority 200
```

### GLBP Roles

| Role | Function |
|------|----------|
| AVG (Active Virtual Gateway) | Manager of GLBP group |
| AVF (Active Virtual Forwarder) | Forwards traffic |
| Standby AVG | Backup for AVG |
| Standby AVF | Backup for AVF |

### GLBP Preemption
```
! Enable preemption (default)
glbp 1 preempt

! Preemption with delay
glbp 1 preempt delay 30
```

### GLBP Load Balancing
```
! Default: round-robin
glbp 1 load-balancing [round-robin | weighted | host-dependent]
```

### GLBP Weighting
```
! AVG weighting
glbp 1 weighting 110 lower 100

! Track object
track 1 interface GigabitEthernet0/2 line-protocol

glbp 1 weighting track 1 decrement 10
```

## Object Tracking

```
! Track interface state
track 1 interface GigabitEthernet0/2 line-protocol

! Track IP routing
track 2 ip routing 10.0.0.0 255.0.0.0

! Use in HSRP
standby 1 track 1 decrement 20

! View tracking
show track
show track brief
show track 1
```

## Virtual IP Considerations

- **MAC Address:** Virtual gateway MAC (not router MAC)
- **ARP:** Clients learn virtual MAC via ARP
- **Gratuitous ARP:** Sent when state changes

```
! Send gratuitous ARP on state change (automatic)
standby 1 arp ip-learning

! Gratuitous ARP count
standby 1 name GATEWAY1
```

## Debugging and Monitoring

```
! View HSRP status
show standby
show standby brief
show standby GigabitEthernet0/1
show standby neighbors

! View VRRP status
show vrrp
show vrrp brief
show vrrp interface GigabitEthernet0/1

! View GLBP status
show glbp
show glbp brief
show glbp GigabitEthernet0/1

! Enable debugging
debug standby
debug vrrp
debug glbp
```

## IPv6 FHRP

### HSRPv6
```
interface GigabitEthernet0/1
  ipv6 address 2001:db8::1/64
  standby version 2
  standby 1 ipv6 2001:db8::3
  standby 1 priority 150
  standby 1 preempt
```

### VRRPv6
```
interface GigabitEthernet0/1
  ipv6 address 2001:db8::1/64
  vrrp 1 ipv6 2001:db8::3
  vrrp 1 priority 200
```

## FHRP Deployment Best Practices

1. **Choose Protocol:**
   - HSRP: Cisco-only, feature-rich
   - VRRP: Multi-vendor standard
   - GLBP: Active-active load balancing

2. **Configuration:**
   - Set priority explicitly (avoid defaults)
   - Configure preemption delays
   - Implement authentication

3. **Monitoring:**
   - Track critical links
   - Configure weight-based failover
   - Monitor state transitions

4. **Testing:**
   - Failover to backup manually
   - Verify gratuitous ARP
   - Test client failover

5. **Documentation:**
   - Document virtual IP scheme
   - Note priority assignments
   - Record tracked interfaces
