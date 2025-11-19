# DMVPN (Dynamic Multipoint VPN) Implementation Guide

## Overview
Deploy DMVPN for scalable hub-and-spoke and any-to-any VPN with 50+ branch offices.

## Phase 1: Design and Planning

### Hub Design

```
Hub Location: Data Center (Headquarters)
Hub Router: Cisco ASR 1006
Internet Connection: Dual 10 Gbps circuits

Hub Configuration:
  - Primary tunnel endpoint: 203.0.113.1
  - Backup tunnel endpoint: 203.0.113.2
  - NHRP server for branch registration
  - BGP route redistribution
  - QoS and DPI integration
```

### Branch Design

```
Typical Branch (30-50 users):
  - Branch Router: Cisco ISR 4331
  - Primary Internet: DIA 20 Mbps
  - Backup: 4G LTE connection
  - Tunnel Interface: mGRE (Multipoint GRE)
  - NHRP Client: Registers with hub
  - BGP Speaker: Learns routes from hub
```

## Phase 2: Hub Configuration (Cisco IOS XE)

### Basic Interface Setup

```
Router# configure terminal
Router(config)# hostname HUB-ROUTER

! Management Interface
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip address 10.0.0.1 255.255.255.0
Router(config-if)# no shutdown

! Internet-facing Interface
Router(config)# interface GigabitEthernet0/1
Router(config-if)# ip address 203.0.113.1 255.255.255.0
Router(config-if)# bandwidth 10000000
Router(config-if)# no shutdown

! Tunnel Interface (mGRE)
Router(config)# interface Tunnel0
Router(config-if)# ip address 172.16.0.1 255.255.255.0
Router(config-if)# ip mtu 1400
Router(config-if)# ip nhrp network-id 1
Router(config-if)# ip nhrp authentication DMVPN-KEY-123
Router(config-if)# ip nhrp server-only
Router(config-if)# tunnel source GigabitEthernet0/1
Router(config-if)# tunnel mode gre multipoint
Router(config-if)# no shutdown
```

### IPsec Configuration

```
! IKEv2 Policy
Router(config)# crypto ikev2 proposal HUB-PROPOSAL
Router(config-crypto-ikev2-proposal)# encryption aes-cbc-256
Router(config-crypto-ikev2-proposal)# integrity sha256
Router(config-crypto-ikev2-proposal)# group 14

! IKEv2 Policy
Router(config)# crypto ikev2 policy HUB-POLICY
Router(config-crypto-ikev2-policy)# proposal HUB-PROPOSAL

! IKEv2 Keyring
Router(config)# crypto ikev2 keyring HUB-KEYRING
Router(config-crypto-ikev2-keyring)# peer 0.0.0.0 0.0.0.0
Router(config-crypto-ikev2-keyring-peer)# address 0.0.0.0
Router(config-crypto-ikev2-keyring-peer)# pre-shared-key DMVPN-PSK-12345!

! IKEv2 Profile
Router(config)# crypto ikev2 profile HUB-PROFILE
Router(config-crypto-ikev2-profile)# match identity address 0.0.0.0
Router(config-crypto-ikev2-profile)# authentication remote pre-share
Router(config-crypto-ikev2-profile)# authentication local pre-share
Router(config-crypto-ikev2-profile)# keyring HUB-KEYRING
Router(config-crypto-ikev2-profile)# lifetime 28800
Router(config-crypto-ikev2-profile)# aaa-attributes

! IPsec Transform Set
Router(config)# crypto ipsec transform-set HUB-TRANSFORM esp-aes 256 esp-sha-hmac
Router(config-crypto-transform-set)# mode tunnel

! IPsec Profile
Router(config)# crypto ipsec profile HUB-IPSEC
Router(config-crypto-ipsec-profile)# set transform-set HUB-TRANSFORM
Router(config-crypto-ipsec-profile)# set pfs group14
Router(config-crypto-ipsec-profile)# set security-association lifetime seconds 3600

! Apply IPsec to Tunnel
Router(config)# interface Tunnel0
Router(config-if)# tunnel protection ipsec profile HUB-IPSEC ikev2 HUB-PROFILE
```

### Routing Configuration (EIGRP Phase 3)

```
! Enable EIGRP
Router(config)# router eigrp HUB-AS
Router(config-router)# eigrp router-id 1.1.1.1
Router(config-router)# network 172.16.0.0 0.0.0.255
Router(config-router)# network 10.0.0.0 0.0.0.255
Router(config-router)# passive-interface GigabitEthernet0/1

! Split Horizon OFF (critical for hub)
Router(config-router)# interface Tunnel0
Router(config-if)# no ip split-horizon eigrp HUB-AS

! NHRP Redirect (Phase 3)
Router(config-if)# ip nhrp redirect

! EIGRP Stub Spokes-only (hub is NOT stub)
Router(config-router)# no eigrp stub
```

## Phase 3: Spoke Configuration

### Spoke Router Setup (Cisco ISR 4331)

```
Router# configure terminal
Router(config)# hostname SPOKE-001

! Internet Interface (Public IP from ISP)
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip address dhcp
Router(config-if)# no shutdown

! Local LAN Interface
Router(config)# interface GigabitEthernet0/1
Router(config-if)# ip address 192.168.100.1 255.255.255.0
Router(config-if)# no shutdown

! Tunnel Interface
Router(config)# interface Tunnel0
Router(config-if)# ip address 172.16.0.101 255.255.255.0
Router(config-if)# ip mtu 1400
Router(config-if)# ip nhrp network-id 1
Router(config-if)# ip nhrp authentication DMVPN-KEY-123
Router(config-if)# ip nhrp nhs 203.0.113.1 multicast
Router(config-if)# ip nhrp registration timeout 600
Router(config-if)# ip nhrp holdtime 600
Router(config-if)# tunnel source GigabitEthernet0/0
Router(config-if)# tunnel mode gre multipoint
Router(config-if)# no shutdown
```

### Spoke IPsec Configuration

```
! Same IPsec configuration as hub (DMVPN-PSK-12345!)
Router(config)# crypto ikev2 keyring SPOKE-KEYRING
Router(config-crypto-ikev2-keyring)# peer 0.0.0.0 0.0.0.0
Router(config-crypto-ikev2-keyring-peer)# address 0.0.0.0
Router(config-crypto-ikev2-keyring-peer)# pre-shared-key DMVPN-PSK-12345!

! IKEv2 Profile
Router(config)# crypto ikev2 profile SPOKE-PROFILE
Router(config-crypto-ikev2-profile)# match identity address 0.0.0.0
Router(config-crypto-ikev2-profile)# authentication remote pre-share
Router(config-crypto-ikev2-profile)# authentication local pre-share
Router(config-crypto-ikev2-profile)# keyring SPOKE-KEYRING

! Apply to Tunnel
Router(config)# interface Tunnel0
Router(config-if)# tunnel protection ipsec profile HUB-IPSEC ikev2 SPOKE-PROFILE
```

### Spoke Routing (EIGRP)

```
! EIGRP Configuration
Router(config)# router eigrp HUB-AS
Router(config-router)# eigrp router-id 101.1.1.1
Router(config-router)# network 172.16.0.0 0.0.0.255
Router(config-router)# network 192.168.100.0 0.0.0.255
Router(config-router)# passive-interface GigabitEthernet0/0

! Stub Configuration (spoke is stub)
Router(config-router)# eigrp stub connected summary

! NHRP Shortcut (Phase 3)
Router(config)# interface Tunnel0
Router(config-if)# ip nhrp shortcut eigrp HUB-AS

! BFD for faster detection
Router(config)# interface Tunnel0
Router(config-if)# ip rsvp bandwidth 10000
Router(config-if)# bfd interval 300 min_rx 300 multiplier 3
```

## Phase 4: Testing and Verification

### Hub Tunnel Status

```
HUB-ROUTER# show ip nhrp summary

NHRP Summary:
Interface: Tunnel0
  NHRP Servers: Local
  Entries: 50
  Registrations: 50
  Authorizations: 0

HUB-ROUTER# show ip nhrp cache

Interface: Tunnel0 via 172.16.0.101
   Type: dynamic, Flags: routed
   To: 172.16.0.101, via 209.0.113.101
   Registration timeout: 600

HUB-ROUTER# show crypto session brief

Session ID: 1
Status: UP-ACTIVE
Peer: 209.0.113.101:500
IKEv2 Proposal: AES-256/SHA256/Group14
```

### Spoke Tunnel Status

```
SPOKE-001# show ip nhrp summary

NHRP Summary:
Interface: Tunnel0
  NHRP Servers: 203.0.113.1

SPOKE-001# show ip nhrp cache

NHRP Cache for Tunnel0:
172.16.0.1/32  -> 203.0.113.1
172.16.0.102/32 -> 209.0.113.102
172.16.0.103/32 -> 209.0.113.103

SPOKE-001# show crypto session brief

Crypto session status

Interface: Tunnel0
Session ID: 1
Status: UP-ACTIVE
Peer: 203.0.113.1:500
```

### EIGRP Verification

```
HUB-ROUTER# show ip eigrp neighbors

EIGRP Neighbors for AS 100
H   Address         Interface   Hold  Uptime   Q  Seq
0   172.16.0.101    Tu0         12    00:05:32 0  15
1   172.16.0.102    Tu0         14    00:04:18 0  12
2   172.16.0.103    Tu0         13    00:06:11 0  18

HUB-ROUTER# show ip route eigrp | include 192.168

172.16.0.0/24 is variably subnetted, 2 subnets, 2 masks
D       192.168.100.0/24 [90/2195456] via 172.16.0.101, 00:05:32, Tunnel0
D       192.168.101.0/24 [90/2195456] via 172.16.0.102, 00:04:18, Tunnel0
```

### Spoke-to-Spoke Validation

```
SPOKE-001# show ip nhrp cache

NHRP Cache for Tunnel0:
172.16.0.102/32 -> 209.0.113.102 [learned via NHRP shortcut]

SPOKE-001# tracert 192.168.101.100

Tracing route to 192.168.101.100 over a maximum of 30 hops
  1  172.16.0.102 (direct tunnel)
  2  192.168.101.1
  3  192.168.101.100

! Direct path (not through hub)
```

## Phase 5: Advanced Features

### NHRP Holdtime and Registration

```
! Adjust if branches have high churn
Router(config)# interface Tunnel0
Router(config-if)# ip nhrp holdtime 900  ! 15 minutes instead of 600
Router(config-if)# ip nhrp registration timeout 900

! Reduce if mobile branches (fast movement)
Router(config-if)# ip nhrp holdtime 300  ! 5 minutes
```

### MTU Optimization

```
! Check fragmentation
SPOKE-001# ping 172.16.0.1 size 1400

! Result: Needs fragmentation
! Solution: Reduce MTU on tunnel

Router(config)# interface Tunnel0
Router(config-if)# ip mtu 1300
Router(config-if)# ip tcp adjust-mss 1260
```

### DPD Configuration

```
Router(config)# crypto ikev2 profile HUB-PROFILE
Router(config-crypto-ikev2-profile)# dpd 10 3 on-demand

! Parameters:
!   10 = Check every 10 seconds
!   3 = Timeout after 3 retries (30 seconds total)
!   on-demand = Only if traffic delayed
```

## Phase 6: Scalability Management

### Phase 3 Deployment for 50+ Branches

```
Benefits:
  - Direct spoke-to-spoke communication
  - Reduced hub CPU load
  - Lower inter-spoke latency
  - Automatic shortcut creation

Requirements:
  - All spoke routers upgraded to Phase 3
  - EIGRP NHRP redirect enabled
  - Sufficient NHRP cache memory
  - Hub capacity for SAs (1000+ possible)
```

### Load Balancing Across Hubs

```
Dual Hub Configuration:
  Hub1: Primary (203.0.113.1)
  Hub2: Secondary (203.0.113.2)

Spoke Configuration:
  Primary Hub: HUB1 via EIGRP
  Secondary Hub: HUB2 via EIGRP
  Failover: Automatic if HUB1 down

EIGRP Metric Adjustment:
  ! Make HUB1 preferred
  Router(config-router)# distance eigrp 100 130

Load Balancing:
  ! Unequal cost load balancing
  Router(config-router)# variance 2
```

## Phase 7: Monitoring and Optimization

### Real-time Monitoring

```
HUB-ROUTER# show ip nhrp traffic

NHRP Traffic Stats:
Requests: 15,432
Replies: 15,401
Purges: 45
Errors: 31

HUB-ROUTER# show crypto ipsec sa

# Monitor encryption traffic
#pkts encaps: 50000, #pkts encrypt: 50000
#pkts decaps: 45000, #pkts decrypt: 45000

HUB-ROUTER# show interface Tunnel0 | include "packets input/output"

Packets input: 100,000   output: 95,000
```

### Bandwidth Management

```
! QoS for different traffic types
Router(config)# policy-map DMVPN-QOS
Router(config-pmap)# class critical-apps
Router(config-pmap-c)# priority percent 50
Router(config-pmap)# class normal-traffic
Router(config-pmap-c)# bandwidth percent 40
Router(config-pmap)# class best-effort
Router(config-pmap-c)# bandwidth percent 10

! Apply to tunnel
Router(config)# interface Tunnel0
Router(config-if)# service-policy output DMVPN-QOS
```

## Phase 8: Troubleshooting Guide

### NHRP Registration Failure

```
Symptoms:
  - NHRP cache empty
  - No tunnel establishment

Debug Commands:
  Router# debug ip nhrp
  Router# debug crypto ikev2 protocol

Common Causes:
  1. Network ID mismatch
  2. Hub unreachable
  3. Pre-shared key mismatch
  4. Firewall blocking NHRP (port 6209)

Solution:
  1. Verify network-id matches
  2. Test connectivity to hub IP
  3. Verify PSK matches
  4. Open firewall for NHRP/IPsec
```

### Routing Oscillation (Phase 2)

```
Symptoms:
  - Routes flapping
  - Intermittent connectivity
  - High CPU on hub

Cause:
  - Phase 2 with summarization

Solution:
  - Upgrade to Phase 3
  - Disable summarization
  - Add summary filtering
  - Review routing topology
```

### Slow Performance

```
Symptoms:
  - Low throughput
  - High latency
  - Packet loss

Causes:
  1. MTU too large -> fragmentation
  2. Encryption weak -> CPU bottleneck
  3. Hub congestion -> all traffic through hub
  4. Firewall QoS limiting

Solutions:
  1. Reduce tunnel MTU to 1400 or less
  2. Use AES-NI acceleration
  3. Verify spoke-to-spoke direct paths
  4. Check QoS policies
```

## Best Practices Checklist

- [ ] All PSKs strong and identical
- [ ] NHRP network-id consistent
- [ ] Phase 3 deployed for scale
- [ ] MTU optimized (1400 typical)
- [ ] Split horizon disabled on hub
- [ ] BFD enabled for fast failover
- [ ] DPD configured for keepalive
- [ ] Monitoring/alerting in place
- [ ] Documentation current
- [ ] Disaster recovery tested
- [ ] Backup NHRP server available
- [ ] Performance baseline established
