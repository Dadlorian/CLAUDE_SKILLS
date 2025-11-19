# SD-WAN Deployment Guide

## Overview
Implement Cisco SD-WAN (Catalyst, Meraki) to modernize WAN architecture with application intelligence, cost optimization, and centralized control.

## Phase 1: Planning and Design

### Current State Assessment

```
Existing WAN:
  - Primary: MPLS to data center ($5k/month, 50 Mbps)
  - Backup: Internet DIA ($1k/month, 10 Mbps)
  - Branches: 50 locations
  - Users: 2000 total

Problem Areas:
  - MPLS expensive
  - Limited bandwidth scalability
  - Inefficient routing
  - Manual provisioning
  - No app awareness
```

### Target State Architecture

```
SD-WAN Future:
  - Primary: MPLS (critical apps only) ($3k/month)
  - Secondary: Internet DIA ($1k/month, 100 Mbps)
  - Tertiary: 4G/LTE backup ($500/month)
  - Direct Internet Breakout for SaaS
  - Centralized application policies
  - Real-time bandwidth optimization
```

### Capacity Planning

**Branch Site Sizing**
```
Typical Branch:
  - Users: 30-50
  - Bandwidth: MPLS 10 Mbps + DIA 25 Mbps
  - Devices: 2-4 SD-WAN appliances
  - Power: UPS for 30-minute battery
  - Storage: 100 GB SSD local logging

Data Center:
  - Hub appliances: 2-3 (redundancy)
  - Throughput: 10+ Gbps aggregate
  - Licenses: Enterprise tier for all features
```

## Phase 2: Cisco SD-WAN Infrastructure

### Component Deployment

**1. Management and Control Plane**

```
vManage (Management)
  Role: Central management console
  Deployment: 1 instance (cloud or on-premises)
  CPU: 16 cores minimum
  RAM: 64 GB minimum
  Storage: 500 GB SSD
  High Availability: Cluster of 3 vManage (optional)

vSmart (Control Plane)
  Role: Distributes routing policies
  Deployment: 2-4 instances (redundancy)
  Cluster: All communicate
  No state: Fully redundant
  Failure: Other vSmart takeover automatically

vBond (Bootstrap)
  Role: Initial registration point
  Deployment: 1-2 instances
  Function: NAT traversal, orchestrator discovery
  Persistence: Not required after registration
  Failure: Can be temporary down (registered devices work)
```

**2. Data Plane (Branch Devices)**

```
Vedge Devices:
  - Vedge 100: Small branch (10-50 users)
  - Vedge 1000: Medium branch (50-200 users)
  - Vedge 2000: Large branch or data center (200+ users)
  - Vedge Cloud: Virtual deployment on AWS/Azure

Cedge Devices:
  - Cisco Catalyst 8000: Modern edge, scalable
  - ISR 4000 series: Existing hardware reused
  - ASR 1000 series: High-end branch
  - Cloud instances: AWS, Azure, GCP
```

### Control Plane Configuration

**vManage Setup**
```
1. Initial Access
   URL: https://[vmanage-ip]:8443
   Default: admin/admin
   Change password immediately

2. System Settings
   System Timezone: UTC
   NTP Servers: 10.0.0.1, 8.8.8.8
   DNS Servers: 8.8.8.8, 1.1.1.1
   Syslog Server: 10.0.1.100

3. Organization
   Organization Name: XYZ Company
   Generate Certificates: Yes
   Certificate Validity: 10 years

4. Controller Configuration
   vSmartIP: 10.0.0.1
   vSmartIP2: 10.0.0.2 (redundancy)
   vBondIP: 10.0.0.3
   Organization ID: 12345
```

**vSmart Configuration**
```
vSmart Cluster:
  - Node 1: 10.0.0.1
  - Node 2: 10.0.0.2
  - Cluster Address: 10.0.0.10

Route Policy:
  - Distribute routes for all branches
  - Load balance across transports
  - Failover on transport failure

OMP Configuration:
  - Hello interval: 10 seconds
  - Hold time: 60 seconds
  - Graceful restart: Enabled
```

## Phase 3: Branch Device Deployment

### Zero-Touch Provisioning (ZTP)

**Process**
1. Ship branch device to site
2. Power on and connect to any internet
3. Device contacts vBond automatically
4. Download certificate and policies
5. Configure self with site-specific settings
6. No manual CLI configuration required

**Prerequisites**
```
- Organization certificate already installed
- Branch to vBond connectivity (UDP 12346)
- DNS resolution for vBond (or IP hard-coded)
- Vedge accepts ZTP (not default)
```

**Configuration**
```
vedge# system
system
 host-name branch-001
 system-ip 192.168.1.1
 site-id 100
 admin-tech-on-failure
 controller-group-list 0
 enable-module-loader
 timezone UTC
 ntp
  server 10.0.0.1 prefer

vedge# omp
omp
 send-path-limit 4
 ecmp-limit 4
 graceful-restart
 advertise aggregate
 graceful-restart-timer 600
 eor-timer 300
```

### Interface Configuration

```
vedge# interfaces
vpn 0
 interface eth0
  ip address 203.0.113.1 255.255.255.0
  tunnel-interface
   encapsulation ipsec
   color mpls
   restrict
  exit
  no shutdown
 exit

vpn 0
 interface eth1
  ip address 209.0.113.1 255.255.255.0
  tunnel-interface
   encapsulation ipsec
   color public-internet
   carrier-class
  exit
  no shutdown
 exit
```

### Routing Configuration

```
vedge# omp
omp
 bgp 65001
  neighbor 10.0.0.1
   remote-as 65000
  neighbor 10.0.0.2
   remote-as 65000
  !
  address-family ipv4 unicast
   network 192.168.1.0 255.255.255.0
   network 172.16.0.0 255.255.0.0
  exit
 exit
exit

vedge# service bgp-0
service bgp-0
 router bgp 65001
  bgp log-neighbor-changes
  neighbor 10.0.0.1 remote-as 65000
  neighbor 10.0.0.2 remote-as 65000
  !
  address-family ipv4
   network 192.168.1.0 mask 255.255.255.0
   network 172.16.0.0 mask 255.255.0.0
  exit
 exit
exit
```

## Phase 4: Application-Aware Routing

### Application Identification

```
app-route-policy branch-policy
 rule 10
  match
   app-list critical-apps
  action
   count
   set
    tloc 203.0.113.1 color mpls preference 1
    tloc 209.0.113.1 color public-internet preference 10
  exit
 exit

 rule 20
  match
   app-list video-apps
  action
   set
    tloc 209.0.113.1 color public-internet preference 1
  exit
 exit

 rule 30
  match
   app-list cloud-apps
  action
   set
    tloc 209.0.113.1 color public-internet preference 1
  exit
 exit

 rule 65535
  action
   count
   set
    tloc 203.0.113.1 color mpls preference 1
    tloc 209.0.113.1 color public-internet preference 2
  exit
 exit
exit
```

### Traffic Classification

```
app-list critical-apps
 app SAP
 app Oracle
 app SQL-Server
exit

app-list video-apps
 app YouTube
 app Cisco-WebEx
 app Microsoft-Teams
exit

app-list cloud-apps
 app Salesforce
 app Office-365
 app Slack
exit
```

## Phase 5: Security Integration

### Threat Prevention

```
vedge# security
security
 zone-pair untrusted vpn-0
  zone vpn-0
   inspect
    enabled
   exit
  exit
 exit
exit

vedge# firewall
firewall
 policy-definition DLP-Policy
  sequence 10
   match
    source-address 192.168.1.0/24
    application-list sensitive-apps
   action
    drop
    log
   exit
  exit

  sequence 20
   action
    drop
    log
   exit
  exit
 exit
exit
```

### DLP (Data Loss Prevention)

```
vedge# data-policy
data-policy
 vpn 10
  rule 10
   match
    source-address 192.168.1.0/24
    file-type credit-card-data
   action
    log
    drop
   exit
  exit

  rule 20
   match
    destination-address 8.8.8.8/32
    application-list social-media
   action
    log
    drop
   exit
  exit
 exit
exit
```

## Phase 6: Central Control and Policy

### vManage Policy Configuration

**Device Template**
```
Templates > Create Device Template
  Template Name: Branch-Template-100
  Device Type: Vedge-100

  System Settings:
    hostname: <HOSTNAME>
    system-ip: <SYSTEM_IP>
    site-id: <SITE_ID>

  Interfaces:
    eth0: MPLS color
    eth1: Internet color

  Routing:
    BGP AS: 65001
    Neighbors: vSmart controllers

  Encryption:
    IPsec Suite: AES-256-GCM
    Authentication: SHA-256
```

**Feature Templates**
```
Templates > Feature Templates:
  1. System
  2. Interface
  3. VPN
  4. BGP
  5. Service VPN
  6. Security
  7. Application-aware routing
```

**Policy Definitions**
```
Policies > Policy Definitions:
  - Traffic Policy: QoS rules, bandwidth limits
  - Device Acl: Per-device firewall rules
  - App-Route Policy: Application-based routing
  - Data Policy: DLP, traffic filtering
  - Service Chaining: Service insertion points
```

## Phase 7: Monitoring and Analytics

### Real-time Monitoring

```
vManage Dashboard:
  Active Devices: 150/150 (100%)
  Health Score: 98.5%

  Transport Status:
    MPLS: 95% utilization
    Internet: 40% utilization
    4G: 5% utilization (backup)

  Application Performance:
    Critical Apps: 0 drops, 5ms latency
    Video Apps: 0% loss, 25ms latency

  Top Applications: Office 365, Salesforce, WebEx

  Geographic View: Location-based branch status
```

### Performance Analytics

```
Reports > Network Performance:
  - Bandwidth utilization by transport
  - Application latency trends
  - Packet loss rates
  - Top talkers (source/destination)
  - SLA compliance metrics

Custom Reports:
  - Hourly application performance
  - Daily cost per branch
  - Weekly SLA violations
  - Monthly trends and forecasting
```

### Alerting

```
Monitor > Alerts:
  - Transport down: Immediate alert
  - SLA violation: Email notification
  - Device offline: Escalate if > 5 min
  - Unusual traffic pattern: Log and review
  - Certificate expiration: 30 days before

Alert Rules:
  - High CPU on branch: > 80% for 5 min
  - Bandwidth constraint: > 95% for 2 min
  - Packet loss: > 1% for 1 min
```

## Phase 8: Optimization and Tuning

### Transport Optimization

```
Branch Configuration:
  - MPLS: 10 Mbps, Preferred, Business hours
  - Internet DIA: 25 Mbps, Preferred, Always on
  - 4G/LTE: Backup only, Cost optimization

Failover Rules:
  1. If MPLS available: Use it
  2. If MPLS down: Failover to DIA
  3. If both down: Use 4G (limited traffic)
  4. If 4G down: Buffer traffic, retry
  5. Recovery: Failback to MPLS when recovered
```

### QoS and Shaping

```
QoS Policy:
  Critical (10%): SAP, Oracle, SQL - No drops
  Business (30%): Office 365, Email - Low latency
  Normal (40%): Web, General traffic - Best effort
  Low (20%): Video, Social media - Delay tolerant

Rate Limiting per Application:
  - Teams: 5 Mbps minimum, 10 Mbps burst
  - YouTube: 10 Mbps cap
  - SQL: Unlimited (priority)
```

## Phase 9: Migration Strategy

### Phased Rollout Plan

**Week 1-2: Pilot Phase**
- Deploy at 5 branch locations
- Test application routing
- Verify security policies
- Collect performance baseline

**Week 3-4: Early Adopter Phase**
- 15 additional branches
- Monitor for issues
- Optimize policies
- Plan for scaling

**Week 5-8: Full Rollout**
- Migrate remaining 30 branches
- Two per week
- Parallel run with legacy WAN (2 weeks)
- Decommission MPLS at end

### Rollback Plan

```
If Major Issues:
  1. Revert to legacy WAN immediately
  2. Investigate root cause
  3. Fix configuration in lab
  4. Re-test thoroughly
  5. Plan retry for next window

Common Issues:
  - Application performance: Check app-route policy
  - Connectivity loss: Verify transport status
  - Latency: Check TLOC selection
  - Security: Review security policies
```

## Phase 10: Ongoing Operations

### Maintenance Windows

```
Scheduled Maintenance: 2nd Sunday, 2-3 AM UTC
Notification: 2 weeks in advance
Expected Downtime: None (full redundancy)
Activities:
  - Firmware updates
  - Policy changes
  - Configuration optimization
  - Certificate rotation
```

### Cost Savings Analysis

```
Pre-SD-WAN:
  MPLS: $5,000/month x 12 = $60,000/year
  DIA backup: $1,000/month x 12 = $12,000/year
  Total: $72,000/year

Post-SD-WAN:
  MPLS (optimized): $3,000/month x 12 = $36,000/year
  DIA (primary): $1,000/month x 12 = $12,000/year
  4G backup: $500/month x 12 = $6,000/year
  License (SD-WAN): $2,000/month x 12 = $24,000/year
  Total: $78,000/year (Year 1 with licensing)

Year 2+ Savings: $72,000 - 42,000 = $30,000/year

ROI: Positive by month 16
```

## Best Practices Checklist

- [ ] Zero-touch provisioning configured
- [ ] All transports load balanced
- [ ] Application-aware routing verified
- [ ] Security policies integrated
- [ ] DLP rules enforced
- [ ] Monitoring/alerting active
- [ ] Redundant vSmart controllers
- [ ] Disaster recovery plan documented
- [ ] Staff trained on operations
- [ ] Performance baseline established
- [ ] Cost savings tracked monthly
- [ ] Regular policy optimization reviews
