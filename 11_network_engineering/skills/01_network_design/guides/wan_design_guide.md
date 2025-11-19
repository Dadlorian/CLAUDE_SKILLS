# WAN Design Guide

## Introduction
This guide covers designing resilient, cost-effective wide-area networks connecting multiple geographically distributed sites.

## Step 1: WAN Requirements Analysis

### Site Assessment

```
Data collection:

Site inventory:
  HQ Data Center:
    - Size: 2,000 users
    - Servers: 200+
    - Internet requirement: Critical

Regional Hub (US-East):
    - Size: 500 users
    - Servers: 20
    - Internet requirement: Important

Branches (10 locations):
    - Size: 50-100 users each
    - Servers: Local file storage
    - Internet requirement: Required

Remote offices (5 locations):
    - Size: 10-25 users each
    - Servers: None
    - Internet requirement: Important

Total WAN: 15 sites, peak 4,500 users
```

### Traffic Classification

```
Traffic types and requirements:

Data Center access (30%):
  - From: Branch users
  - To: HQ database/file servers
  - Requirement: Predictable latency (<100ms)
  - Bandwidth: 30% of total (based on 850 Mbps peak)
  - Protocol: TCP (E-mail, file shares)

Cloud/SaaS access (40%):
  - From: All sites
  - To: AWS, Office 365, Salesforce
  - Requirement: Low latency (<200ms), high availability
  - Bandwidth: 40% of total
  - Protocol: HTTPS, variable

Internet access (20%):
  - From: All sites
  - To: General web, email, streaming
  - Requirement: Best-effort acceptable
  - Bandwidth: 20% of total
  - Protocol: HTTP/HTTPS

VoIP/Video (10%):
  - From: All sites
  - To: Headquarters communication
  - Requirement: Low latency (<150ms), low loss (<0.1%)
  - Bandwidth: 10% of total
  - Protocol: UDP (RTP)
```

## Step 2: Topology Selection

### Evaluate Options

```
Hub-and-Spoke:
  Pros: Simple, low cost, centralized control
  Cons: Hub bottleneck, single point of failure
  Best for: Branch offices only

Partial Mesh:
  Pros: Balanced cost and redundancy
  Cons: Moderate complexity
  Best for: Multiple regional hubs + branches

Full Mesh:
  Pros: Optimal paths, full redundancy
  Cons: Very high cost (N² links)
  Best for: < 5 critical sites

Recommendation for this organization:
  - HQ-DC: Center hub
  - Regional hubs: Connected to HQ + each other (partial mesh)
  - Branches: Connected to nearest regional hub (spoke)
```

### Topology Design

```
WAN Topology:

                HQ-DC (Hub)
              /   |   |   \
             /    |   |    \
        RH-1   RH-2  RH-3  RH-4 (Regional Hubs)
         /\     /\     /\     /\
        /  \   /  \   /  \   /  \
       B   B  B   B  B   B  B   B  (Branches)

Connectivity:
  HQ-DC: 4 × 300 Mbps circuits (one to each regional hub)
  Regional hubs: Dual connections (primary to HQ, backup to each other)
  Branches: 100 Mbps circuit (primary), optional backup (50 Mbps LTE)

Cost structure:
  HQ: 4 × $2,500 = $10,000/month
  Regional (4): 4 × 2 × $1,500 = $12,000/month
  Branches (10): 10 × $500 = $5,000/month
  Backup LTE (10): 10 × $200 = $2,000/month
  Total: $29,000/month
```

## Step 3: Technology Selection

### MPLS vs Internet VPN vs SD-WAN

```
Technology comparison:

MPLS (Traditional):
  Cost: $$$ (high)
  Performance: Guaranteed QoS, low jitter
  Redundancy: Provider controlled
  Setup time: 4-6 weeks
  Flexibility: Low (provider dependent)
  Security: Provider responsibility
  Best for: Finance, trading, real-time apps

Internet VPN (IPsec):
  Cost: $ (low)
  Performance: Variable, internet dependent
  Redundancy: Manual
  Setup time: 1-2 weeks (many providers)
  Flexibility: High (any ISP)
  Security: Shared responsibility
  Best for: Cost-sensitive, multiple ISP diversity

SD-WAN:
  Cost: $$ (medium)
  Performance: Optimized path selection
  Redundancy: Automatic failover, multiple paths
  Setup time: 1-2 weeks
  Flexibility: Very high (multiple link types)
  Security: Built-in
  Best for: Modern, cloud-first enterprises
```

### Recommended Strategy

```
Hybrid approach for this organization:

HQ-DC to Regional Hubs:
  - Primary: MPLS 300 Mbps (guaranteed QoS)
  - Backup: SD-WAN over Internet (automatic failover)
  - Cost: MPLS $2,500 + SD-WAN $500 = $3,000/month
  - Benefit: Redundancy with cost control

Regional Hubs to Branches:
  - Primary: SD-WAN over Internet 100 Mbps
  - Backup: 4G LTE 50 Mbps (mobile)
  - Cost: $500 + $200 = $700/month per branch
  - Benefit: Flexibility, low cost, automatic failover

Total WAN cost:
  HQ circuits: $3,000 × 4 = $12,000/month
  Branch circuits: $700 × 10 = $7,000/month
  Total: $19,000/month (cheaper than all-MPLS)
```

## Step 4: Bandwidth Calculation

### Per-Site Calculation

```
HQ-DC requirements:

User count: 2,000
Avg per-user: 2 Mbps (calculated from traffic analysis)
Peak multiplier: 2.5x
Peak bandwidth: 2,000 × 2 × 2.5 = 10,000 Mbps = 10 Gbps

But traffic distribution:
  - Internal: 30% (stayed local via servers)
  - Cloud/SaaS: 40% (went to internet, not WAN)
  - DC access from branches: 30% of branch traffic

HQ outbound on WAN: ~4 Gbps peak
HQ inbound from branches: Varies by branch (100-500 Mbps each)

Regional Hub calculation:

User count: 500
Local servers: 20% traffic local
Outbound to HQ or cloud: 80%
Peak: 500 × 2 × 2.5 × 0.8 = 2,000 Mbps = 2 Gbps

But distributed:
  - Some go to HQ (30%): 600 Mbps
  - Some go to cloud (40%): 800 Mbps
  - Some stay local (20%): (local switching)
  - Some to internet (10%): 200 Mbps

Required uplink: 1.6 Gbps (600+800+200)
Choose circuit: 2 × 1 Gbps redundant, or 1 × 2 Gbps + backup

Branch calculation:

User count: 75 (average)
Peak: 75 × 2 × 2.5 = 375 Mbps
But: Most traffic to cloud (40%) + local (20%) = 60% off-net
To WAN (HQ): Only 40% of peak
Required: 375 × 0.4 = 150 Mbps

Chosen circuit: 100 Mbps (adequate with 30% growth buffer)
```

## Step 5: QoS and Traffic Engineering

### QoS Design

```
Traffic priority:

1. Voice (VoIP/Video): Highest priority
   - Target: < 150ms latency, < 1% loss
   - Reserve: 10% of WAN link
   - Bandwidth: 10 Mbps per 100 calls

2. Data Center access: High priority
   - Target: < 100ms latency, < 0.1% loss
   - Reserve: 40% of WAN link
   - Bandwidth: Variable but predictable

3. Cloud/SaaS: Medium priority
   - Target: < 200ms latency, < 1% loss
   - Reserve: 30% of WAN link
   - Bandwidth: Variable

4. Internet/Other: Low priority
   - Target: Best-effort
   - Reserve: Remaining bandwidth
   - Bandwidth: Limited during peak

Example for 300 Mbps circuit:
  Voice reserve: 30 Mbps
  Data Center: 120 Mbps
  Cloud/SaaS: 90 Mbps
  Internet: 60 Mbps
  Total: 300 Mbps
```

### Failover Design

```
Primary path failure triggers:

MPLS circuit fails:
  - Detected: <1 second (hardware)
  - Failover: SD-WAN takes over
  - Time to full: <2 seconds
  - Impact: Minor (all traffic shifts to backup)
  - QoS: Degraded (no guaranteed QoS on internet)

Internet circuit fails:
  - Detected: <10 seconds (BGP timeout)
  - Failover: Automatic
  - Reroute: Via MPLS (if available)
  - Impact: Minor if MPLS available
  - Alternative: Queue at local site until restored

All circuits fail:
  - Local internet access: Direct (optional local ISP)
  - HQ access: Queued until restored
  - Cloud access: Direct local internet (cached)
  - Impact: Degraded service, 1-2 hours recovery
```

## Step 6: Implementation

### Circuit Provisioning

```
Typical lead times:

MPLS circuits:
  - Order: 2-3 days
  - Carrier install: 2-4 weeks
  - Testing/validation: 1 week
  - Total: 4-6 weeks

Internet circuits (fiber):
  - Order: 1-2 days
  - ISP install: 1-3 weeks
  - Testing: 2-3 days
  - Total: 2-4 weeks

4G LTE:
  - Order: 1 day
  - Device ship: 2-3 days
  - Activation: 1 day
  - Total: 4-5 days

Project timeline:
  Week 1: Submit orders (MPLS + Internet)
  Week 3-4: Circuit arrival, CPE shipping
  Week 5-6: On-site installation and config
  Week 6-7: Testing and cutover
  Week 7-8: Parallel operation, final cutover
```

### CPE Configuration

```
Branch CPE (Cisco ASR 1000):

interface Gi0/0/0
 description Internet circuit
 ip address 203.0.113.50 255.255.255.0
 !

interface Gi0/0/1
 description MPLS circuit
 ip address 192.0.2.50 255.255.255.0
 !

ip route 0.0.0.0 0.0.0.0 203.0.113.1 10
ip route 0.0.0.0 0.0.0.0 192.0.2.1 5

! Primary route via MPLS (lower AD)
! Backup route via Internet (higher AD)
! Failover time: 3-5 seconds when primary fails

crypto ikev2 proposal PROPOSAL-1
 encryption aes-cbc-256
 integrity sha512
 dh_group 21
 !

crypto ikev2 policy POLICY-1
 proposal PROPOSAL-1
 !

crypto ikev2 keyring KEY-1
 peer 203.0.113.1
  address 203.0.113.1
  pre-shared-key cisco123
  !
 !

crypto ikev2 profile PROFILE-1
 match identity address 203.0.113.1
 authentication remote pre-share
 authentication local pre-share
 keyring KEY-1
 lifetime 86400
 dpd 10 3 on-demand
 !

crypto ipsec transform-set TS esp-aes 256 esp-sha512-hmac
 mode tunnel
 !

crypto ipsec profile IPSEC-1
 set transform-set TS
 set pfs group21
 !

tunnel-group 203.0.113.1 type ipsec-l2l
 tunnel-group 203.0.113.1 ipsec-attributes
  ikev2 remote-authentication pre-share
  ikev2 local-authentication pre-share
  ikev2 profile PROFILE-1
  !
 !
```

## Testing and Validation

```
Pre-production testing:

Connectivity:
  [ ] Ping HQ-DC from all branches
  [ ] Ping all regional hubs
  [ ] Verify DNS resolution
  [ ] Test route symmetry (ping returns same path)

Failover:
  [ ] Unplug MPLS circuit, verify failover to internet
  [ ] Unplug internet circuit, verify failover to MPLS
  [ ] Verify both restore correctly
  [ ] Test automatic failback

Performance:
  [ ] Measure latency (< 100ms to HQ)
  [ ] Measure jitter (< 30ms preferred)
  [ ] Measure throughput (meets requirement)
  [ ] Measure packet loss (< 0.1% required)

QoS:
  [ ] Voice traffic passes with priority
  [ ] Video doesn't starve voice
  [ ] Background traffic doesn't impact foreground
```

## Monitoring and Optimization

```
Daily monitoring:

Circuit health:
  - Check all links operational (no outages)
  - Verify QoS policies active
  - Monitor jitter/latency trending

Weekly monitoring:

Capacity:
  - Check peak utilization (< 70% target)
  - Trending over time
  - Identify growing sites

Monthly monitoring:

Cost analysis:
  - Cost per Mbps per month
  - Identify expensive circuits
  - Plan optimization

Quarterly review:

Optimization opportunities:
  - Consolidate underutilized circuits
  - Shift traffic to lower-cost paths
  - Plan for growth (add capacity)
  - Review SLA compliance
```

---

**Guide Version:** 1.0
**Last Updated:** November 2025
**Experience Level:** Advanced
**Technologies:** MPLS, IPsec, SD-WAN, BGP
