# VPN High Availability Guide

## Overview
Design and implement highly available VPN infrastructure with redundancy, failover, and load balancing.

## Architecture Patterns

### Pattern 1: Active-Active Load Balancing

```
Configuration:
  VPN Gateway 1: 203.0.113.1 (50% traffic)
  VPN Gateway 2: 203.0.113.2 (50% traffic)
  DNS: Round-robin vpn.company.com
  Shared Certificate: Wildcard or SAN

Setup:
  1. Two identical VPN appliances
  2. Load balanced IP (virtual IP): 203.0.113.10
  3. DNS points to virtual IP
  4. Traffic distributed across both
```

**Advantages**
- Maximum utilization of both gateways
- No standby resources wasted
- Linear scalability

**Disadvantages**
- Both must be active and healthy
- Failover requires DNS change (slow)
- Session continuity not guaranteed

### Pattern 2: Active-Passive with Failover

```
Configuration:
  VPN Gateway 1 (Active): 203.0.113.1
  VPN Gateway 2 (Passive): 203.0.113.2
  Floating IP: 203.0.113.10
  Status: Gateway 1 owns floating IP

Failover Trigger:
  - Gateway 1 down
  - Heartbeat missed
  - Failover time: 10-30 seconds

Recovery:
  - When Gateway 1 recovers
  - Can be automatic or manual
  - Prevent failover flapping
```

**Advantages**
- Simple configuration
- Fast failover (< 30 seconds)
- Lower cost (only active unit processes)

**Disadvantages**
- Passive gateway underutilized
- Potential session loss during failover
- Requires IP takeover mechanism

### Pattern 3: Multi-Region with Geolocation

```
Configuration:
  US Region:
    Primary: 203.0.113.1
    Secondary: 203.0.113.2
  EU Region:
    Primary: 198.51.100.1
    Secondary: 198.51.100.2
  Asia Region:
    Primary: 192.0.2.1
    Secondary: 192.0.2.2

DNS Geolocation Routing:
  North America users -> US Region
  Europe users -> EU Region
  Asia users -> Asia Region
  Fallback: Closest healthy region
```

**Advantages**
- Lower latency (geographically close)
- Reduced WAN costs
- Resilient to regional failures

**Disadvantages**
- Higher complexity
- More appliances to manage
- Increased cost

## Implementation: Cisco ASA Failover

### Network Diagram

```
Corporate Network (10.0.0.0/8)
        |
        |
   Load Balancer
        |
    ____|____
   |         |
 ASA-1     ASA-2
(Active)  (Passive)
   |         |
 203.0.113.1 203.0.113.2

Floating IP: 203.0.113.10
```

### Configuration Steps

**ASA-1 (Active)**

```cisco
! Set failover mode
failover lan unit primary
failover lan interface FAILOVER-LINK GigabitEthernet0/2
failover lan key FAILOVER-SECRET-KEY
failover

! Configure interfaces normally
interface GigabitEthernet0/0
  nameif outside
  ip address 203.0.113.1 255.255.255.0
  no shutdown

interface GigabitEthernet0/1
  nameif inside
  ip address 10.0.0.1 255.255.255.0
  no shutdown

! Floating IP address
interface GigabitEthernet0/0
  ip address 203.0.113.10 255.255.255.0 standby 203.0.113.2

! Monitor interface for failover
failover monitor interface outside
failover monitor interface inside
```

**ASA-2 (Passive)**

```cisco
! Set failover mode
failover lan unit secondary
failover lan interface FAILOVER-LINK GigabitEthernet0/2
failover lan key FAILOVER-SECRET-KEY
failover

! Same interface configuration as primary
! Failover will sync automatically
```

### State Synchronization

```cisco
! Enable stateful failover
failover link FAILOVER-LINK GigabitEthernet0/2 115

! Configure replication
replication http 10.0.0.1 10.0.0.2
replication https 10.0.0.1 10.0.0.2

! Monitor replication
show failover history
show failover replication
```

## Checkpoint-Based HA (Palo Alto)

### Configuration

```
Setup:
  Palo Alto 1: 203.0.113.1 (Active)
  Palo Alto 2: 203.0.113.2 (Passive)
  Virtual IP: 203.0.113.10
  HA Link: Dedicated interface (no latency)
```

**Active Unit (Device > High Availability)**

```
HA Setup:
  Enabled: Yes
  Group ID: 1
  Priority: 100 (higher = more preferred)
  Interface: eth1/1 (dedicated HA link)
  State: Active

Heartbeat Interval: 1000 ms
Heartbeat Max Retries: 3
HA Key Exchange: Encrypted
```

**Passive Unit (Same Config, Priority: 50)**

```
HA Setup:
  Enabled: Yes
  Group ID: 1
  Priority: 50
  Interface: eth1/1 (same link)
  State: Passive
```

### Monitoring HA Status

```
Dashboard: Show
  - Active/Passive state
  - Peer status
  - Sync status (%)
  - Configuration version
  - HA heartbeat status

Monitor > Logs > HA Logs
  Track failover events
  Monitor sync failures
  Review state changes
```

## Load Balancing with HAProxy

### Architecture

```
Internet
   |
   | (Port 443, 1194, 4500)
   |
HAProxy Load Balancer (203.0.113.10)
   |
   |____ Backend-1 (203.0.113.1) - VPN-1
   |____ Backend-2 (203.0.113.2) - VPN-2
   |____ Backend-3 (203.0.113.3) - VPN-3
```

### Configuration

```bash
# /etc/haproxy/haproxy.cfg

global
  maxconn 4096
  daemon
  log 127.0.0.1 local0 debug

defaults
  mode tcp
  log global
  option tcplog
  timeout connect 5000
  timeout client 50000
  timeout server 50000
  retries 3
  option redispatch

# SSL/TLS VPN
listen ssl-vpn
  bind 0.0.0.0:443
  balance roundrobin
  mode tcp
  option tcplog
  option ssl-hello-chk
  default_backend ssl-backends

# OpenVPN
listen openvpn
  bind 0.0.0.0:1194
  balance roundrobin
  mode tcp
  default_backend openvpn-backends

# IPsec (with IKE and NAT-T)
listen ipsec
  bind 0.0.0.0:500
  bind 0.0.0.0:4500
  balance roundrobin
  mode tcp
  default_backend ipsec-backends

# SSL VPN Backends
backend ssl-backends
  balance roundrobin
  option httpchk GET /
  server vpn1 203.0.113.1:443 check
  server vpn2 203.0.113.2:443 check
  server vpn3 203.0.113.3:443 check

# OpenVPN Backends
backend openvpn-backends
  balance roundrobin
  server vpn1 203.0.113.1:1194 check
  server vpn2 203.0.113.2:1194 check
  server vpn3 203.0.113.3:1194 check

# IPsec Backends
backend ipsec-backends
  balance roundrobin
  server vpn1 203.0.113.1:500 check
  server vpn2 203.0.113.2:500 check
  server vpn3 203.0.113.3:500 check
```

### Health Checks

```bash
# Monitor backend status
echo "show stat" | nc localhost 8404 | grep BACKEND

# Expected output: All backends UP
```

## DNS Round-Robin

### Simple Round-Robin

```bash
# DNS A records
vpn.company.com  IN  A  203.0.113.1
vpn.company.com  IN  A  203.0.113.2
vpn.company.com  IN  A  203.0.113.3

# Clients randomly select one of three
# No health checking (manual intervention on failure)
```

### Geolocation-Based

```
GeoDNS Provider Configuration:
  Location: North America -> 203.0.113.1
  Location: Europe -> 198.51.100.1
  Location: Asia -> 192.0.2.1
  Default/Failback -> 203.0.113.10

Clients in US query:
  dig vpn.company.com
  ; ANSWER SECTION:
  vpn.company.com. 300 IN A 203.0.113.1

Clients in UK query:
  dig vpn.company.com
  ; ANSWER SECTION:
  vpn.company.com. 300 IN A 198.51.100.1
```

## Session Persistence

### Issue: Session Loss on Failover

```
Problem:
  User connected to VPN-1 (203.0.113.1)
  VPN-1 fails
  Connection drops
  User must reconnect to VPN-2

Solution 1: Stateful Failover
  - Full session state replicated
  - Transparent to user
  - Requires synchronized gateways

Solution 2: Persistent IKE SA
  - Resume capability
  - Fast reconnection (seconds)
  - Supported in IKEv2 (RFC 5723)

Solution 3: MOBIKE (IKEv2)
  - Seamless mobility
  - IP address changes ok
  - Session continues
```

### Implementation

**IKEv2 with MOBIKE**

```cisco
! Cisco ASA
crypto ikev2 policy 10
  encryption aes-256
  integrity sha256
  group 14
  prf sha256
  lifetime 28800

! Enable MOBIKE
crypto ikev2 profile REMOTE-PROFILE
  match identity remote address 0.0.0.0
  authentication remote pre-share
  authentication local rsa-sig
  lifetime 86400
  ipsec-proposal TRANSFORM
  mobility true

! Clients with IKEv2 MOBIKE support
vpn_client.conf:
ikev2-mobility enabled
```

## Disaster Recovery Planning

### RTO/RPO Targets

```
RTO (Recovery Time Objective):
  - Active-Active: 0 seconds (instant)
  - Active-Passive: 10-30 seconds
  - Load Balanced: 0 seconds (restart on another)

RPO (Recovery Point Objective):
  - Stateful: 0 (no session loss)
  - Stateless: User reconnects
```

### Backup Scenarios

**Complete Appliance Failure**
```
1. Detection: Health check failure (5 seconds)
2. Failover: Traffic redirected (< 10 seconds)
3. Recovery: Ship replacement unit
4. Re-integration: Update DNS/routing
5. Testing: Verify functionality

Downtime: 10-30 seconds per user
```

**Data Center Failure**
```
1. Detection: Multiple service failures
2. Activation: Failover to secondary DC
3. DNS: Update geolocation routing
4. Verification: All services operational
5. Recovery: Assess primary DC

Downtime: Depends on DNS TTL (typically 300 seconds)
```

**Network Partition**
```
Scenario: Link between sites fails

Solution:
  - Both sites continue operating
  - Clients from partition A -> Gateway A
  - Clients from partition B -> Gateway B
  - Sync resumed when partition heals

Requirements:
  - Independent VPN gateways in each site
  - DNS capable of site-specific responses
  - Users in one partition can't reach other
```

## Monitoring and Alerting

### Key Metrics

```
VPN Gateway Health:
  - Interface status (up/down)
  - IKE SA count
  - IPsec SA count
  - Encryption/decryption success
  - Failed authentication attempts
  - CPU/Memory utilization
  - Bandwidth utilization

Failover Metrics:
  - Failover events (count/time)
  - Failover duration (target < 30 sec)
  - Session loss (target 0)
  - Recovery time
```

### Alert Configuration

```
Critical Alerts:
  - Gateway down (immediate)
  - All backends failed (immediate)
  - HA sync lost (immediate)
  - Certificate expiration (1 week before)
  - Disk space low (80% full)

Warning Alerts:
  - Failover occurred (within 5 min)
  - High CPU (> 80% for 5 min)
  - Memory utilization (> 85%)
  - Connection queue (> 100)
  - Failed authentications (spike)
```

## Testing HA Failover

### Pre-Production Testing

```
Test 1: Manual Failover
  1. Note active gateway
  2. Admin console: Force failover
  3. Verify: Passive becomes active
  4. Measure: Time to recovery
  5. Result: Target < 30 seconds

Test 2: Simulate Gateway Failure
  1. Reboot active gateway
  2. Monitor: Failover triggers
  3. User impact: Brief disconnect
  4. Measure: Reconnection time
  5. Result: New gateway handles load

Test 3: Network Partition
  1. Block HA heartbeat link
  2. Monitor: Both think they're primary
  3. Result: Split brain (expected)
  4. Reconnect: Verify resync
  5. Verify: No data loss

Test 4: Load Balancing
  1. Connect 100 clients
  2. Distribute across backends
  3. Monitor: Balanced (33 each)
  4. Shut down one backend
  5. Verify: Remaining two handle load
```

## Best Practices Checklist

- [ ] Minimum 2 VPN appliances (N+1 redundancy)
- [ ] Dedicated HA heartbeat link
- [ ] Automated failover tested
- [ ] RTO/RPO targets defined
- [ ] Backup certificates generated
- [ ] Load balancing validated
- [ ] Health checks configured
- [ ] Monitoring and alerts active
- [ ] Runbook for failover documented
- [ ] DNS failover strategy planned
- [ ] Session persistence verified
- [ ] Regular failover drills (monthly)
- [ ] Capacity planning done
- [ ] Documentation updated
