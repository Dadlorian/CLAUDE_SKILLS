# EIGRP Configuration Guide

## EIGRP Named Mode vs Classic Mode

### Classic Mode (Legacy)
```
router eigrp 100
  network 10.0.0.0
  network 192.168.0.0 0.0.255.255
  passive-interface default
  no passive-interface GigabitEthernet0/0
```

### Named Mode (Recommended)
```
router eigrp CAMPUS
  !
  address-family ipv4 unicast autonomous-system 100
    network 10.0.0.0 0.255.255.255
    network 192.168.0.0 0.0.255.255
    af-interface default
      passive-interface
    exit-af-interface
    af-interface GigabitEthernet0/0
      no passive-interface
    exit-af-interface
```

**Advantages of Named Mode:**
- Hierarchical configuration
- Separate IPv4 and IPv6 address families
- Per-interface settings under address family
- More flexible policy application

## EIGRP Network Configuration

### Classful Network Declaration
```
router eigrp 100
  network 10.0.0.0              ! Advertise entire 10.0.0.0/8
  network 192.168.0.0           ! Advertise entire 192.168.0.0/16
```

### Classless Network Declaration (Named Mode)
```
address-family ipv4 unicast autonomous-system 100
  network 10.0.0.0 0.255.255.255       ! /8
  network 192.168.0.0 0.0.255.255      ! /16
```

### Interface-Level Advertisement
```
! Instead of classful network, use interface commands
interface GigabitEthernet0/0
  ip summary-address eigrp 100 10.1.0.0 255.255.255.0
  ! Or explicit in named mode:
  ! ip address 10.1.0.1 255.255.255.0
```

## K-Values Configuration

### Default K-Values
```
router eigrp 100
  ! K1=1, K2=0, K3=1, K4=0, K5=0
  ! Uses: Metric = BW + DELAY
```

### Custom K-Values
```
router eigrp 100
  metric weights 0 1 0 1 0 0
  ! tos k1 k2 k3 k4 k5
  ! If using k2, k4 must match all routers!
```

**Warning:** All routers in EIGRP domain must use same K-values!

## Bandwidth and Delay Configuration

### Default Bandwidth (Interface-based)
```
! Ethernet: 10 Mbps (inherited)
! Serial: 1.544 Mbps (T1 default)

! Override bandwidth
interface Serial0/0
  bandwidth 512  ! kbps

! Set delay (10 microsecond units)
interface Serial0/0
  delay 20000    ! 200,000 microseconds = 200ms
```

### Bandwidth vs Delay Tuning
```
! Favor faster link (lower delay)
interface GigabitEthernet0/0
  delay 100      ! Very low delay

! Deprioritize link (higher delay)
interface Serial0/0
  delay 50000    ! High delay = less desirable

! Set minimum bandwidth for WAN links
interface Serial0/0
  bandwidth 2048  ! 2 Mbps
```

## EIGRP Authentication

### MD5 Authentication Setup
```
key chain EIGRP_KEYS
  key 1
    key-string MYPASSWORD
    accept-lifetime local 12:00:00 Jan 1 2024 infinite
    send-lifetime local 12:00:00 Jan 1 2024 infinite
  key 2
    key-string NEWPASSWORD
    accept-lifetime local 12:00:00 Jan 1 2025 infinite
    send-lifetime local 12:00:00 Jan 1 2025 infinite

interface GigabitEthernet0/0
  ip authentication key-chain eigrp 100 EIGRP_KEYS
  ip authentication mode eigrp 100 md5
```

### SHA Authentication (Named Mode)
```
key chain EIGRP_SHA
  key 1
    key-string MYKEY
    cryptographic-algorithm hmac-sha-256

interface GigabitEthernet0/0
  ip authentication key-chain eigrp 100 EIGRP_SHA
  ip authentication mode eigrp 100 hmac-sha-256
```

## Neighbor Establishment

### Verify Neighbor Formation
```
show ip eigrp neighbors
show ip eigrp neighbors detail
show ip eigrp interface detail

! Neighbor requirements:
! - Same AS number
! - Same authentication (if enabled)
! - Interfaces up and in same subnet
! - K-values match
```

## Passive Interfaces

### Prevent EIGRP Updates on Link
```
! Classic mode
router eigrp 100
  passive-interface default
  no passive-interface GigabitEthernet0/0
  no passive-interface GigabitEthernet0/1

! Named mode
address-family ipv4 unicast autonomous-system 100
  af-interface default
    passive-interface
  exit-af-interface
  af-interface GigabitEthernet0/0
    no passive-interface
  exit-af-interface
```

## Route Summarization

### Auto-Summarization (Classic Mode)
```
router eigrp 100
  auto-summary    ! Summarize at classful boundary (default in Classic)
  no auto-summary ! Disable (required for discontiguous networks)
```

### Manual Summarization (At Boundary)
```
interface GigabitEthernet0/0
  ip summary-address eigrp 100 10.0.0.0 255.0.0.0
  ! Suppresses 10.x.x.x subnets if not via this interface
```

## Filtering and Redistribution

### Distribute-Lists
```
access-list 1 permit 10.0.0.0 0.255.255.255

router eigrp 100
  distribute-list 1 in GigabitEthernet0/0   ! Inbound filter
  distribute-list 1 out GigabitEthernet0/1  ! Outbound filter
```

### Prefix-List Filtering
```
ip prefix-list ALLOWED seq 10 permit 10.0.0.0/8
ip prefix-list ALLOWED seq 20 permit 192.168.0.0/16

router eigrp 100
  distribute-list prefix ALLOWED in GigabitEthernet0/0
```

### Route-Map Filtering
```
route-map FILTER_ROUTES in
  match ip address prefix-list ALLOWED
  set metric 100 100 255 1 1500  ! BW, Delay, Reliability, Load, MTU
  permit

neighbor 10.0.0.1 route-map FILTER_ROUTES in
```

## Metric Tuning

### Offset-Lists
```
! Increase metric by 100 on inbound routes from neighbor
offset-list 0 in 100 GigabitEthernet0/0

! Decrease metric on outbound routes
offset-list 0 out 50 GigabitEthernet0/1
```

### Unequal Cost Load Balancing
```
router eigrp 100
  variance 2
  ! Use feasible successors with metric <= 2 × best metric

! Example:
! Best path cost: 1000
! Feasible successor cost: 2000 (≤ 2×1000 = 2000)
! Both paths used in load balancing
```

## Stub Routing

### Stub Configuration
```
router eigrp 100
  network 10.0.0.0

! Reduce queries on hub
interface Serial0/0
  ip summary-address eigrp 100 10.1.0.0 255.255.0.0

! Hub configuration (spoke as stub)
interface Serial0/0
  ip split-horizon eigrp 100

! Prevent query propagation
router eigrp 100
  neighbor 10.0.0.2 remote-ipv4-unicast 100 source GigabitEthernet0/0
```

## Timers and Convergence

### Hello and Hold Timers
```
! Classic mode
interface GigabitEthernet0/0
  ip hello-interval eigrp 100 5
  ip hold-time eigrp 100 15

! Named mode
address-family ipv4 unicast autonomous-system 100
  af-interface GigabitEthernet0/0
    hello-interval 5
    hold-time 15
  exit-af-interface
```

### Default Timers by Network Type
- **LAN:** 5s hello, 15s hold
- **WAN (point-to-point):** 5s hello, 15s hold
- **WAN (point-to-multipoint):** 60s hello, 180s hold

### Active Time (SIA Prevention)
```
router eigrp 100
  timers active-time 180  ! Seconds before declaring SIA
```

## BFD Integration

### Enable BFD
```
interface GigabitEthernet0/0
  ip ospf bfd
  ! Or explicit BFD
  bfd interval 300 min_rx 300 multiplier 3

! EIGRP uses BFD automatically if available
show ip eigrp interface detail
```

## EIGRP for IPv6

### Address Family Configuration
```
router eigrp CAMPUS
  !
  address-family ipv6 unicast autonomous-system 100
    network 2001:db8::/32
    network 2001:db8:1::/48

    af-interface GigabitEthernet0/0
      no passive-interface
    exit-af-interface
  exit-address-family

interface GigabitEthernet0/0
  ipv6 address 2001:db8::1/64
```

## Monitoring EIGRP

### Key Commands
```
show ip eigrp topology
show ip eigrp topology detail
show ip eigrp traffic
show ip eigrp interfaces
show ip eigrp neighbors
show ip route eigrp
```

### Debugging
```
debug eigrp neighbors
debug eigrp packets
debug ip eigrp routing
```

## Deployment Checklist

### Pre-Configuration
- [ ] Plan EIGRP area design (hub-and-spoke vs mesh)
- [ ] Assign AS number globally
- [ ] Plan K-values (usually default)
- [ ] Determine summarization boundaries
- [ ] Plan stub routing locations
- [ ] Design metric strategy

### Configuration
- [ ] Use named mode for new deployments
- [ ] Configure network statements
- [ ] Set passive interfaces appropriately
- [ ] Implement authentication (MD5 or SHA)
- [ ] Configure summarization at boundaries
- [ ] Set up stub routing on spokes
- [ ] Configure BFD on critical links
- [ ] Implement filtering as needed

### Verification
- [ ] Verify neighbor adjacencies
- [ ] Check topology table
- [ ] Verify routing table entries
- [ ] Validate metrics
- [ ] Test failover scenarios
- [ ] Monitor SIA events

### Production Monitoring
- [ ] Track convergence time
- [ ] Monitor query/reply rates
- [ ] Alert on SIA conditions
- [ ] Monitor neighbor stability
- [ ] Track route count trends

## Best Practices

1. **Use Named Mode:** Better structure, future-proof
2. **Authentication:** Always use MD5/SHA on all interfaces
3. **Summarization:** Summarize at area boundaries
4. **Passive Interface:** Use `passive-interface default`
5. **Stub Routing:** Reduce queries on spoke networks
6. **BFD:** Use on WAN links for fast convergence
7. **Monitoring:** Track convergence and topology changes
8. **Testing:** Lab test before production
9. **Documentation:** Document AS numbers and design
10. **Graceful Shutdown:** Plan for maintenance windows
