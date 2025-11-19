# SD-WAN Implementation Guide

## Pre-Implementation Planning

### 1. Assess Current WAN

```
Existing WAN Analysis:
├─ Circuit inventory
│  ├─ MPLS bandwidth/cost
│  ├─ Internet bandwidth/cost
│  └─ 4G/LTE backup
├─ Application requirements
│  ├─ Latency sensitive (voice, video)
│  ├─ Bandwidth intensive (file transfer)
│  └─ Critical (backup requirements)
├─ Branch locations
│  ├─ Number of branches
│  ├─ Current throughput
│  └─ Internet availability
└─ Business goals
   ├─ Cost savings target
   ├─ Application performance improvement
   └─ Flexibility/Agility goals
```

### 2. Design SD-WAN Architecture

```
Site Topology Design:
├─ Hub-and-Spoke
│  └─ All traffic via hub (data center)
├─ Full Mesh
│  └─ Branch-to-branch direct
└─ Hybrid
   ├─ Regional hubs for mesh
   └─ Direct paths for critical traffic
```

### 3. WAN Link Selection

```
Per Branch:
├─ Primary: MPLS (if cost acceptable)
├─ Backup: Internet (always available)
├─ Tertiary: 4G/LTE (for emergencies)
└─ Direct to Cloud: Internet-based for SaaS

Link Preferences (typically):
1. Best path (MPLS for reliability)
2. Backup path (Internet)
3. Failover path (4G)

SD-WAN intelligently switches between them
```

---

## vEdge Deployment

### Step 1: Provision vEdge Device

```bash
# 1. Hardware setup
├─ Connect vEdge to network
├─ Connect one interface to SD-WAN controller
├─ Configure initial IP (DHCP or manual)
└─ Connect other interfaces to WAN links

# 2. Bootstrap device
# Access: https://<vEdge-IP>:8443
# Login: admin / admin (default)

# 3. Perform initial configuration
Configuration > System
├─ System Hostname: branch-1-vedge
├─ Domain ID: 1
├─ Organization Name: MyCompany
└─ Save and Reboot
```

### Step 2: Zero-Touch Provisioning (ZTP)

```
Option 1: vManage Auto-Provisioning
├─ Device powers on
├─ Sends bootstrap request
├─ vManage assigns certificate
├─ Device connects and receives config
└─ Ready for production

Option 2: Manual Certificate Installation
├─ Generate certificate request on device
├─ Sign with CA
├─ Install certificate on device
└─ Device connects to controller
```

### Step 3: Connect to SD-WAN Controller

```bash
# Configure controller IP
Configuration > VPN 0
├─ Interface: eth0 (management)
├─ Static IP: 10.0.1.100/24
├─ Gateway: 10.0.1.1
└─ DNS: 8.8.8.8

# Add vManage server
Configuration > Controllers
├─ vManage IP: 10.0.0.10 (DC-based)
├─ Port: 8443
└─ Commit

# Verify connection
show control connections
# Expected: vManage connected, state UP
```

---

## WAN Link Configuration

### Step 1: Configure WAN Interfaces

```bash
# MPLS Link (Primary)
Configuration > VPN 0
├─ Interface: ge0/1
├─ IP Address: 10.50.0.1/24 (MPLS-side)
├─ Color: mpls
├─ Restriction: None (preferred path)
├─ Speed: 50 Mbps
└─ Enable

# Internet Link (Backup)
Configuration > VPN 0
├─ Interface: ge0/2
├─ IP Address: 10.60.0.1/24 (Internet-side)
├─ Color: internet
├─ Restriction: Allow (backup only)
├─ Speed: 30 Mbps
└─ Enable

# 4G Link (Failover)
Configuration > VPN 0
├─ Interface: ge0/3
├─ IP Address: DHCP
├─ Color: 4g
├─ Restriction: Restrict (emergency only)
├─ Speed: 10 Mbps
└─ Enable
```

### Step 2: Configure Link Policies

```bash
# Create traffic policy for link selection
Configuration > Policies > Traffic Engineering

Policy: Select-Best-Path
├─ Rule 1: Voice Traffic
│  ├─ Match: Port 5060, 5061 (SIP)
│  ├─ Action: Prefer MPLS, allow Internet
│  └─ Priority: 10
├─ Rule 2: Video Traffic
│  ├─ Match: Port 80, 443, RTMP
│  ├─ Action: Prefer MPLS, failover Internet
│  └─ Priority: 20
├─ Rule 3: Bulk Traffic
│  ├─ Match: FTP, rsync
│  ├─ Action: Allow any link
│  └─ Priority: 100
└─ Default: Prefer MPLS, allow others
```

### Step 3: QoS Configuration

```bash
# Configure per-app QoS
Configuration > QoS

Policy: BranchQoS
├─ Traffic Class: Real-Time
│  ├─ Applications: Skype, Cisco Jabber
│  ├─ Queue: High Priority
│  ├─ Bandwidth: 20% reserved
│  └─ Loss Tolerance: Low
├─ Traffic Class: Transactional
│  ├─ Applications: HTTP, HTTPS
│  ├─ Queue: Standard
│  ├─ Bandwidth: 50% reserved
│  └─ Loss Tolerance: Medium
├─ Traffic Class: Bulk
│  ├─ Applications: FTP, Backup
│  ├─ Queue: Low Priority
│  └─ Bandwidth: Best effort
└─ Apply to: All traffic from branch
```

---

## Policy Configuration

### Step 1: DPI and Application Recognition

```bash
# Configure DPI rules
Configuration > DPI Rules

Rule Set: ApplicationControl
├─ Salesforce
│  ├─ Application ID: salesforce
│  ├─ Preferred Path: Internet (direct to cloud)
│  ├─ Action: Best quality path
│  └─ QoS: Standard
├─ Microsoft Teams
│  ├─ Application ID: teams
│  ├─ Preferred Path: MPLS (via DC)
│  ├─ Action: Failover to Internet
│  └─ QoS: Real-Time
└─ YouTube
   ├─ Application ID: youtube
   ├─ Action: Block or Limited
   └─ Quota: 1 GB/day
```

### Step 2: Application-Based Routing

```bash
# Route based on destination
Configuration > Routing Policies

Policy: CloudAppRouting
├─ Destination: 10.x.x.x/16 (Data Center)
│  ├─ Preferred Path: MPLS
│  ├─ Backup Path: Internet
│  └─ Action: Load balance
├─ Destination: Salesforce (SaaS Cloud)
│  ├─ Preferred Path: Internet (direct)
│  └─ Action: Shortest path to cloud
├─ Destination: Office365 (SaaS)
│  ├─ Preferred Path: Internet
│  └─ Action: Direct to cloud
└─ Default: MPLS primary, Internet backup
```

---

## Hub Configuration

### Step 1: Deploy Hub vEdge/Gateway

```bash
# Hub device (at data center)
Configuration > System
├─ System Hostname: dc1-vedge
├─ Site ID: 100 (hub)
├─ Role: Hub
└─ Enable Hub mode

# Configure uplinks
Configuration > VPN 0
├─ Uplink 1: To ISP-1
│  ├─ IP: 203.0.113.1/24
│  ├─ Gateway: 203.0.113.254
│  └─ Enable
├─ Uplink 2: To ISP-2
│  ├─ IP: 198.51.100.1/24
│  ├─ Gateway: 198.51.100.254
│  └─ Enable
└─ Enable redundancy and load balancing
```

### Step 2: Configure Hub Policies

```bash
# Hub acts as aggregation point
Policy: HubAggregation
├─ All branch traffic aggregates here
├─ Load balance across uplinks
├─ Health monitoring of branches
├─ Path optimization for all flows
└─ Statistics collection
```

---

## Monitoring and Analytics

### Step 1: Enable Telemetry Collection

```bash
# vManage collects statistics from all vEdges
Configuration > Monitoring

Enable Collection:
├─ Device Health
│  ├─ CPU, Memory, Disk
│  ├─ Tunnel status
│  └─ Link quality
├─ Application Analytics
│  ├─ Top applications
│  ├─ Traffic by app
│  └─ App performance metrics
├─ Network Performance
│  ├─ Latency, jitter, loss
│  ├─ Bandwidth utilization
│  └─ Path efficiency
└─ Security Events
   ├─ Threats detected
   ├─ Policy violations
   └─ IPS alerts
```

### Step 2: Create Dashboards

```
vManage Dashboard: SD-WAN Health
├─ Overall Network Health
│  ├─ Green: All systems normal
│  ├─ Yellow: Warnings
│  └─ Red: Critical issues
├─ Branch Status Map
│  ├─ Online/Offline status
│  ├─ Active links per branch
│  └─ Last known status
├─ Application Performance
│  ├─ Top 5 apps by bandwidth
│  ├─ App latency by branch
│  └─ App loss percentage
├─ WAN Link Utilization
│  ├─ MPLS vs Internet usage
│  ├─ Peak hours traffic
│  └─ Cost per GB trend
└─ Alerts
   ├─ Failed branch connections
   ├─ SLA breaches
   └─ Tunnel down events
```

---

## Validation and Testing

### Step 1: Link Validation

```bash
# From vManage: Monitor > Network
├─ Device Status: All Online
├─ Tunnel Status: All UP
├─ Link Status: All Active
└─ Control Connections: All Connected
```

### Step 2: Path Validation

```bash
# Verify traffic engineering
Monitor > Devices > Select Device
├─ Show active flows
├─ Path taken per application
├─ Verify preference order
└─ Check failover behavior

# From vEdge CLI:
show tunnel summary
# Should show tunnels to hub and other branches

show sdwan statistics
# Link quality metrics
```

### Step 3: Failover Testing

```bash
# Test MPLS link failure
1. Disconnect MPLS at branch
2. Observe traffic switch to Internet
3. Check latency/jitter
4. Reconnect MPLS
5. Verify automatic return to preferred path

Expected: Minimal disruption, automatic failover
```

### Step 4: Application Testing

```bash
# Verify critical apps work
1. Salesforce access: Direct path via Internet
2. File transfer to DC: Via MPLS
3. Video conferencing: Real-time QoS applied
4. Web browsing: Via preferred path

Check: Performance meets SLA
```

---

## Deployment Phases

### Phase 1: Pilot (1-2 branches)

```
Timeline: 4-6 weeks
├─ Deploy hub and controller
├─ Provision 1-2 edge devices
├─ Configure policies
├─ Monitor for 2-4 weeks
├─ Gather metrics and feedback
└─ Document lessons learned
```

### Phase 2: Rollout (25% of branches)

```
Timeline: 8-12 weeks
├─ Deploy to additional branches
├─ Same topology and policies
├─ Test failover scenarios
├─ Train branch staff
└─ Parallel with legacy WAN
```

### Phase 3: Migration (75% of branches)

```
Timeline: 8-12 weeks
├─ Migrate majority of sites
├─ Keep MPLS as backup
├─ Monitor for 4-6 weeks
├─ Decommission legacy circuits gradually
└─ Cost savings begin
```

### Phase 4: Completion (100% coverage)

```
Timeline: 4-8 weeks
├─ Final branch migrations
├─ Legacy WAN termination
├─ Performance optimization
└─ Operational handoff to NOC
```

---

## Cost Optimization

### Step 1: Analyze Savings

```
Before SD-WAN:
├─ MPLS: 500 sites × $2,000/month = $1,000,000
├─ Internet: 100 sites × $500/month = $50,000
└─ Total: $1,050,000/month

After SD-WAN:
├─ Internet: 500 sites × $500/month = $250,000
├─ MPLS: 50 sites × $2,000/month = $100,000 (critical only)
├─ SD-WAN appliances: $50,000/month (amortized)
└─ Total: $400,000/month

Savings: $650,000/month (62% reduction)
```

### Step 2: Optimize Link Utilization

```
Bandwidth Optimization:
├─ Primary path: Use full MPLS bandwidth
├─ Backup path: Share Internet capacity
├─ Burst: Allow temporary over-subscription
└─ Result: Reduced total required bandwidth
```

---

## Troubleshooting Common Issues

### Issue: Unexpected Path Selection

```bash
# Symptom: Traffic going through Internet instead of MPLS

Solution:
1. Check link status: show sdwan statistics
2. Verify policies: show policy
3. Check path metrics: show tunnel statistics
4. Review application rules: show dpi rules
5. Adjust preferences if needed
```

### Issue: High Latency on Internet Path

```bash
# Symptom: Users report slowness when using Internet

Solution:
1. Measure underlay: ping -c 100 <remote_ip>
2. Check QoS: show qos stats
3. Verify buffer control
4. Adjust bandwidth policies
5. Consider ISP upgrade
```

### Issue: Frequent Path Flapping

```bash
# Symptom: Traffic switches between paths frequently

Solution:
1. Check link instability: show interface statistics
2. Adjust convergence timers
3. Add hysteresis to path selection
4. Stabilize underlay quality
5. Review dynamic path algorithm settings
```

---

## Best Practices

### Network Design
- **Redundancy**: Never single ISP at branch
- **Capacity**: Over-provision by 20-30%
- **Latency**: Monitor baseline, alert on deviations
- **Scalability**: Design for 3-5 year growth

### Operational
- **Monitoring**: 24/7 visibility critical
- **Alerts**: Notify on SLA breach, not just failures
- **Reporting**: Weekly/monthly trends
- **Runbooks**: Document escalation procedures

### Security
- **Encryption**: All traffic encrypted
- **DPI**: Know what's traversing WAN
- **Policies**: Least privilege access
- **Compliance**: Log all policy actions

---

## Next Steps

1. **Design review** with business and technical teams
2. **Cost model validation** with procurement
3. **Pilot deployment** in 1-2 low-risk branches
4. **Success criteria** definition before rollout
5. **Runbook creation** for operations team
