# Firewall Deployment Guide

## Pre-Deployment Planning

### 1. Requirements Gathering
```
Define Scope:
- Network topology
- Protected subnets
- Expected traffic volume
- Security zones needed
- Redundancy requirements
- Performance requirements

Stakeholder Input:
- Business requirements
- Compliance requirements
- Performance expectations
- Budget constraints
- Timeline
- Training needs
```

### 2. Firewall Selection
```
Considerations:
- Throughput requirements
- Feature requirements (IPS, app control, etc.)
- Existing infrastructure
- Management interface preferences
- Support and licensing
- Budget

Platform Selection:
- Enterprise: Palo Alto, Cisco ASA
- Mid-market: Fortinet, Checkpoint
- SMB: Fortinet, pfSense
- Cost-sensitive: Fortinet, Open source
```

### 3. Network Design

```
Basic Topology:
┌─────────────┐
│  Internet   │
└──────┬──────┘
       │
   [Primary FW]
       │
    [Core Switch]
       │
  ┌────┴─────┐
  │           │
[DMZ]     [Internal]
```

### 4. Rule Planning

```
Firewall Rules Categories:

Inbound (Internet → Internal):
- Allow: Web (443, 80)
- Allow: Email (25, 110, 143)
- Allow: VPN (500, 4500, 1194)
- Deny: All others

Outbound (Internal → Internet):
- Allow: DNS (53)
- Allow: HTTP/HTTPS (80, 443)
- Allow: NTP (123)
- Deny: Others

Inter-zone (DMZ ↔ Internal):
- Allow: Specific application ports
- Deny: Direct database access
- Deny: File server access
- Allow: Management SSH
```

## Hardware Deployment

### 1. Physical Installation

**In-line Placement**
```
Internet → [Firewall] → Core Switch → Internal Network

Considerations:
- Power requirements
- Cooling requirements
- Physical space
- Cable management
- Console access
- Serial cable for out-of-band
```

### 2. Network Interface Configuration

```
Interface Planning:

Management Interface:
- Out-of-band if possible
- Separate network
- Limited access
- Encrypted (HTTPS)

WAN Interface:
- Internet connection
- Primary IP
- Secondary for failover
- DHCP or static

Internal Interface:
- Internal network connection
- VLAN for management
- VLAN for internal zone

DMZ Interface:
- Separate from internal
- Limited connectivity
- VLAN tagged
```

### 3. High Availability Setup

```
Active-Passive Configuration:
┌──────────────────┐
│ Primary Firewall │ (Active)
│   IP: X.X.X.X   │
│  Heartbeat Link  │
└────────┬─────────┘
         │
         │ Synchronized
         │
┌────────┴─────────┐
│Secondary Firewall│ (Standby)
│   IP: X.X.X.Y   │
└──────────────────┘

Virtual IP (VIP): X.X.X.Z (active FW)
All traffic through VIP
Automatic failover on heartbeat loss
```

## Software Configuration

### 1. Initial Setup

```
Step 1: Factory Reset (if used equipment)
- Erase all configuration
- Reset to defaults
- Document original state

Step 2: Initial Access
- Console connection
- Set management IP
- Set root password
- Set timezone

Step 3: Network Interface Configuration
- Configure WAN interface (DHCP/static)
- Configure internal interface
- Configure DMZ interface
- Configure management interface

Step 4: Hostname and Domain
- Set hostname
- Set domain name
- Configure DNS servers
- Set NTP server
```

### 2. Basic Security Configuration

```
Step 1: Admin Access Hardening
- Change default password (strong password)
- Disable telnet (SSH only)
- Disable HTTP (HTTPS only)
- Set session timeout

Step 2: SNMP Configuration (if needed)
- Disable SNMPv1/v2c
- Enable SNMPv3
- Set community strings
- Limit SNMP access

Step 3: Logging Configuration
- Centralize syslog
- Enable security logging
- Set log level
- Configure log rotation
```

### 3. Firewall Rules Configuration

```
Step 1: Create Zones
Zone Internal:
- Name: INTERNAL
- Interface: Eth1
- Type: Trust

Zone DMZ:
- Name: DMZ
- Interface: Eth2
- Type: DMZ

Zone Internet:
- Name: EXTERNAL
- Interface: Eth0
- Type: Untrust

Step 2: Create Address Objects
object-group network INTERNAL_NETS
 network-object 10.1.0.0 255.255.0.0

object-group network WEB_SERVERS
 network-object host 10.1.10.5
 network-object host 10.1.10.6

object-group network DNS_SERVERS
 network-object host 10.1.20.1

Step 3: Create Service Objects
object-group service WEB_SERVICES tcp
 port-object eq 80
 port-object eq 443

object-group service DNS_SERVICES udp
 port-object eq 53

Step 4: Create Rules
! Allow WEB from Internet to DMZ
access-list OUTBOUND permit tcp any object-group WEB_SERVERS object-group WEB_SERVICES

! Allow DNS
access-list OUTBOUND permit udp any object-group DNS_SERVERS object-group DNS_SERVICES

! Deny all others
access-list OUTBOUND deny ip any any log

Step 5: Apply Rules to Interfaces
interface Ethernet0
 ip access-group OUTBOUND in
```

## Testing and Validation

### 1. Basic Connectivity Testing

```
Test 1: Internet Connectivity
- Ping external host (e.g., 8.8.8.8)
- Traceroute to external site
- Verify default route

Test 2: Internal Connectivity
- Ping internal server
- Ping internal workstation
- Verify internal routes

Test 3: DMZ Connectivity
- Ping DMZ server
- Ping from DMZ to internal
- Verify inter-zone rules
```

### 2. Rule Validation Testing

```
Test 1: Inbound Traffic
- Web server accessible (port 80/443)
- Verify other ports blocked
- Check logs for denied traffic

Test 2: Outbound Traffic
- Internal user can browse web
- Internal user can use DNS
- Verify unauthorized services blocked

Test 3: Inter-zone Traffic
- DMZ → Database (allowed port only)
- DMZ → File server (should be denied)
- Internal → DMZ (management access)
```

### 3. Performance Testing

```
Baseline Metrics:
- Throughput: Can achieve rated speed?
- Latency: Acceptable delay?
- Connection rate: Handles expected load?
- CPU utilization: <80%?
- Memory utilization: <80%?

Load Testing:
- Ramp up traffic slowly
- Monitor resources
- Identify breaking points
- Verify failover capability
```

### 4. Security Testing

```
Vulnerability Scanning:
- Run Nessus or similar
- Check for open ports
- Verify service banners
- Check SSL configuration

Penetration Testing:
- Attempt port scans (should be blocked)
- Attempt unauthorized access
- Test SSL/TLS vulnerabilities
- Verify rule effectiveness
```

## Operations Handoff

### 1. Documentation

```
Critical Documentation:
- Network diagram
- Interface configuration
- VLAN layout
- Firewall rules (with justification)
- User accounts and roles
- Change management procedures
- Troubleshooting guide
- Escalation procedures
```

### 2. Operations Team Training

```
Topics:
- Basic firewall concepts
- Log review and interpretation
- Common troubleshooting scenarios
- Alert handling procedures
- When to escalate
- Backup/restore procedures
- Failover procedures
- Emergency contact procedures
```

### 3. Monitoring Setup

```
Configure Monitoring:
- CPU utilization
- Memory utilization
- Disk space
- Connection count
- Failed authentications
- Denied traffic volume
- High-risk alerts

Alerting Thresholds:
- CPU > 80%: Alert
- Memory > 80%: Alert
- Denial rate spike: Alert
- Failed auth attempts: Alert
- Service status down: Alert
```

## Post-Deployment

### 1. Optimization

```
First Week:
- Monitor false positives
- Adjust logging levels
- Fine-tune performance
- Document issues discovered

First Month:
- Review security logs
- Identify blocked legitimate traffic
- Create exceptions
- Optimize rules
- Review performance metrics

First Quarter:
- Full security audit
- Test failover
- Penetration test
- Review compliance
- Update documentation
```

### 2. Maintenance

```
Daily:
- Monitor critical alerts
- Check system health
- Review security logs

Weekly:
- Review denied traffic logs
- Check for failed connections
- Review failed authentications
- Verify backups completed

Monthly:
- Review rule hits
- Identify unused rules
- Update threat intelligence
- Test backup/restore
- Compliance check

Quarterly:
- Full security review
- Penetration testing
- Policy review
- Update procedures
- Training refresher

Annually:
- Full audit
- Upgrade assessment
- Capacity planning
- Risk assessment
- Compliance validation
```

### 3. Change Management

```
For Any Changes:
1. Document the change
2. Get approval
3. Create implementation plan
4. Test in lab if possible
5. Schedule maintenance window
6. Communicate to stakeholders
7. Execute change
8. Validate successful
9. Document results
10. Communicate completion
```

## Common Deployment Patterns

### Pattern 1: SMB (Single Site)

```
Configuration:
- Single firewall
- Basic rules
- Simple zones
- Minimal redundancy

Typical Rules:
- Allow specific services
- Deny everything else
- Basic logging
- Weekly updates

Timeline: 2-4 weeks
Cost: Low to moderate
Complexity: Low
```

### Pattern 2: Medium Enterprise (Multiple Sites)

```
Configuration:
- Central firewall + branch firewalls
- Site-to-site VPN
- Complex rules
- High availability

Typical Features:
- Advanced threat protection
- Application control
- Detailed logging
- SIEM integration

Timeline: 2-3 months
Cost: Moderate to high
Complexity: Moderate
```

### Pattern 3: Large Enterprise (Many Sites)

```
Configuration:
- Multi-layer security
- Central + regional + branch firewalls
- Advanced segmentation
- Full redundancy

Typical Features:
- Zero trust architecture
- Advanced threat prevention
- Integration with other security tools
- Centralized management

Timeline: 3-6+ months
Cost: High
Complexity: High
```

## Troubleshooting Common Issues

### Issue 1: Traffic Blocked Unexpectedly

```
Diagnosis:
1. Check firewall logs
2. Identify denying rule
3. Verify rule accuracy
4. Check for implicit deny

Solution:
1. Create specific allow rule
2. Update object groups
3. Verify rule order
4. Test and document
```

### Issue 2: Performance Degradation

```
Diagnosis:
1. Check CPU utilization
2. Check memory utilization
3. Check connection count
4. Analyze traffic patterns

Solution:
1. Optimize rules (order)
2. Enable hardware acceleration
3. Increase resources
4. Upgrade if needed
```

### Issue 3: VPN Connection Failures

```
Diagnosis:
1. Check VPN logs
2. Verify endpoint reachability
3. Check firewall rules for VPN ports
4. Verify encryption settings

Solution:
1. Verify firewall rule allows VPN traffic
2. Check VPN configuration
3. Test connectivity to VPN endpoint
4. Review encryption compatibility
```
