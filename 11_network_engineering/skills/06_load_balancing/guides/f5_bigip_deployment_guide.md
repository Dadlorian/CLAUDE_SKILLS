# F5 BIG-IP Deployment Guide

## Pre-Deployment Planning

### Hardware Sizing

**Key Factors**:
```
1. Concurrent Connections
   - Estimate: Peak users × avg connections per user
   - Example: 50,000 users × 2 connections = 100,000

2. New Connections Per Second (CPS)
   - Estimate: Peak users / avg session duration
   - Example: 50,000 users / 300 sec = ~167 CPS

3. SSL Transactions Per Second
   - Estimate: New connections × % SSL
   - Example: 167 CPS × 50% = ~80 SSL TPS

4. Throughput
   - Estimate: Peak traffic bandwidth
   - Example: 100 Mbps peak data rate
```

**Model Selection**:
```
Entry Level: i5600
  - 50k-500k concurrent connections
  - 5k-50k CPS
  - 10k-100k SSL TPS
  - For: Small to mid-sized deployments

Mid-Range: i7600
  - 500k-2M concurrent connections
  - 50k-200k CPS
  - 100k-300k SSL TPS
  - For: Large enterprise deployments

High-End: i9600
  - 2M+ concurrent connections
  - 200k+ CPS
  - 300k+ SSL TPS
  - For: Massive scale, telecom, ISP
```

### Network Planning

**Physical Connections**:
```
┌─────────────────────────────────────┐
│                                     │
│      F5 BIG-IP Load Balancer        │
│  ┌───────────────────────────────┐  │
│  │ Data Ports (multiple 1GE/10GE)│  │
│  │ ・ Port 1: Client traffic      │  │
│  │ ・ Port 2: Backend traffic     │  │
│  │ ・ Port 3: HA Failover sync    │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ Management Port                 │  │
│  │ ・ Out-of-band mgmt (separate) │  │
│  └───────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘

Network Layout:
  Clients → Port 1 (VLANs, IP space)
  Port 2 → Backend servers (internal network)
  Port 3 ↔ Secondary F5 (HA sync, heartbeat)
  Mgmt Port → Administration access only
```

**IP Address Planning**:
```
Management IP: 203.0.113.100 (out-of-band)
Floating IP (HA): 203.0.113.1 (virtual IP for HA)

Virtual Server IPs:
  VS-Web: 203.0.113.10
  VS-API: 203.0.113.11
  VS-Admin: 203.0.113.12

Self IP Addresses:
  Internal: 192.168.1.100 (internal vlan)
  Failover: 192.168.1.101 (ha failover)
```

## Initial Setup

### Out-of-Band Management

**First Steps**:
```
1. Physical installation
   - Rack mounting
   - Power connections
   - Network cables

2. Console access
   - Connect serial/console cable
   - Credentials: root / default

3. IP configuration
   - Set management IP via console
   - Example: 203.0.113.100/24

4. Access web UI
   - Connect to https://203.0.113.100
   - Default: admin / admin (change immediately!)
```

### Initial Configuration

**System Settings**:
```
1. Change default passwords
   admin user
   root user

2. Set hostname
   example-f5-1

3. Set time/date
   NTP servers
   Timezone

4. Network license
   Register system
   Provision modules (LTM, AFM, etc.)
```

### Provisioning Modules

**Module Selection**:
```
LTM (Load Transmission Module): Core functionality
  - Local load balancing
  - Virtual servers, pools, monitors
  - SSL/TLS support

GTM (Global Traffic Manager): GSLB
  - Geographic routing
  - Global failover
  - Multi-datacenter management

AFM (Application Firewall Module): Security
  - WAF capabilities
  - DDoS protection
  - Advanced filtering

ASM (Application Security Module): Web security
  - Web application firewall
  - Bot detection
  - API security
```

## Virtual Server Configuration

### HTTP Virtual Server

**Configuration Steps**:
```
1. Create Virtual Server
   Name: vs_web_http
   Address: 203.0.113.10
   Service Port: 80
   Type: Standard
   Protocol: HTTP

2. Assign Pool
   Default Pool: pool_web_backends

3. Apply Profiles
   http profile: http
   tcp profile: tcp

4. Save and Activate
```

### HTTPS Virtual Server with SSL

**Configuration Steps**:
```
1. Import Certificate & Key
   Certificate: /Common/example.com.crt
   Key: /Common/example.com.key
   Chain: /Common/DigiCert.crt

2. Create Client SSL Profile
   Name: clientssl_example_com
   Certificate: example.com.crt
   Key: example.com.key
   Ciphers: Strong ciphers only
   Version: TLS 1.2+

3. Create Virtual Server
   Name: vs_web_https
   Address: 203.0.113.10
   Service Port: 443
   Type: Standard

4. Apply Profiles
   clientssl: clientssl_example_com (client side SSL)
   http: http
   tcp: tcp

5. Assign Pool
   Default Pool: pool_web_backends
```

## Pool Configuration

### Basic Pool Setup

**Pool Creation**:
```
1. Create Pool
   Name: pool_web_backends
   Load Balancing Method: Least Connections

2. Add Pool Members
   Member 1: 192.168.1.10:80
   Member 2: 192.168.1.11:80
   Member 3: 192.168.1.12:80

3. Configure Monitor
   Type: HTTP
   Path: /health
   Interval: 5 seconds
   Timeout: 3 seconds

4. Session Persistence
   Type: Cookie Insert
   Cookie Name: LB_SESSIONID

5. Save Pool
```

### Health Monitor Configuration

**HTTP Health Check**:
```
1. Create Monitor
   Name: monitor_http_health
   Type: HTTP
   Method: GET
   Path: /health-check

2. HTTP Response Validation
   Send String: GET /health-check HTTP/1.1\r\nHost: localhost\r\n\r\n
   Receive String: 200
   Expected Status: 200 OK

3. Timeout Configuration
   Interval: 5 seconds
   Timeout: 3 seconds
   Up Threshold: 2
   Down Threshold: 3

4. Assign to Pool
   Select Pool: pool_web_backends
   Monitors: monitor_http_health

5. Verify
   All members show UP status
```

## High Availability Configuration

### Active-Standby HA Pair

**Primary F5**:
```
Hostname: f5-primary
Management IP: 203.0.113.100
Floating IP: 203.0.113.1 (active)
Internal IP: 192.168.1.100
Role: Active (serving traffic)
```

**Secondary F5**:
```
Hostname: f5-secondary
Management IP: 203.0.113.101
Floating IP: 203.0.113.1 (standby)
Internal IP: 192.168.1.101
Role: Standby (monitoring)
```

**HA Configuration**:
```
1. Network Setup
   - Dedicated HA network (Port 3)
   - Configure HA VLANs
   - Set HA IPs (192.168.1.100, 192.168.1.101)

2. Device Trust
   - Primary: Generate cert
   - Secondary: Install primary cert
   - Establish device trust

3. HA Group
   Create HA group with:
   - Primary device
   - Secondary device
   - Floating IP: 203.0.113.1
   - Failover method: HA

4. Configuration Sync
   - Primary syncs config to secondary
   - Both have identical configs
   - Changes on primary → secondary

5. State Sync
   - Connection state synchronized
   - Session persistence data synced
   - Connection tracking synced

6. Test Failover
   - Primary graceful shutdown
   - Verify secondary takes floating IP
   - Verify traffic continues
   - Restore primary
   - Verify failback (if configured)
```

## Configuration Management

### Configuration Backup

**Automatic Backup**:
```
1. Schedule regular backups
   Daily: 02:00 UTC
   Weekly: Sunday 03:00 UTC

2. Backup Scope
   UCS file (all configuration)

3. Backup Location
   Local storage
   Remote NFS
   Remote S3
```

**Manual Backup**:
```
System > Configuration > Backup:
  1. Create new backup
  2. Download UCS file
  3. Store securely (encrypted storage)
  4. Document backup procedure
```

### Configuration Restore

**Restore Procedure**:
```
1. Upload backup file
   System > Configuration > Restore

2. Restore UCS file
   Validates backup integrity
   Restores all configuration

3. Restart services
   Automatic or manual

4. Verify
   Check all virtual servers
   Verify pools status
   Test application access
```

## Monitoring and Alerting

### Key Metrics

**System Health**:
```
CPU Utilization: Should be < 80%
  Alert: > 85%
  Critical: > 95%

Memory Usage: Should be < 80%
  Alert: > 85%
  Critical: > 95%

Disk Space: Should be > 10% free
  Alert: < 20% free
  Critical: < 5% free

Temperature: Should be within range
  Alert: Threshold exceeded
  Critical: Too hot
```

**Connection Metrics**:
```
Active Connections: Baseline dependent
  Alert: > 1.5x baseline

New Connections/sec: Baseline dependent
  Alert: Spike > 2x baseline

Connection Errors: Baseline dependent
  Alert: > 0.5% error rate

Throughput (Mbps): Peak dependent
  Alert: Approaching line rate
```

**Pool Metrics**:
```
Pool Member Status:
  Alert: Any member DOWN
  Alert: Pool at < 50% capacity

Response Time:
  Alert: P95 > 1 second
  Critical: P99 > 5 seconds

Error Rate:
  Alert: > 1% 5xx responses
  Critical: > 5% errors
```

### Alerting Configuration

**Setup SNMP Traps**:
```
1. SNMP Configuration
   Enable SNMP
   Add trap receiver: monitoring.example.com
   SNMP version: v3

2. Trap Events
   Device UP/DOWN
   Pool member status change
   CPU/Memory threshold exceeded
   Virtual server status change

3. Monitor the traps
   SNMP monitoring software
   Alert if trap not received
```

**Setup Syslog**:
```
System > Event Processing > Event Handlers

Configure Syslog:
  Syslog Server: syslog.example.com
  Port: 514
  Facility: Local0

Log Events:
  Virtual server changes
  Pool member status
  Configuration changes
  Authentication
```

## Maintenance Procedures

### Software Upgrade

**Pre-Upgrade**:
```
1. Backup current configuration
   Download UCS file
   Store securely

2. Plan maintenance window
   Notify stakeholders
   Schedule during low traffic

3. Test in staging
   Upgrade test F5 first
   Verify all functionality
   Test failover
```

**Upgrade Process**:
```
1. Upload firmware image
   System > Software Management

2. Install on secondary
   Primary continues serving traffic

3. Verify secondary
   Reboot and test
   Verify failover works

4. Perform failover
   Traffic now on upgraded secondary
   Primary is now standby

5. Upgrade primary
   Install firmware
   Reboot and rejoin HA pair

6. Failback (optional)
   Restore primary as active
```

## Troubleshooting

### Virtual Server Not Working

**Symptoms**: Users can't access service

**Diagnosis**:
```
1. Check virtual server status
   Status should be: Enabled, Available

2. Check pool status
   All members should be: Enabled, UP

3. Check network connectivity
   Verify VIP is responding to ping
   Verify ARP for floating IP

4. Check port listening
   netstat -tulpn | grep :443

5. Check firewall
   tcpdump on LB port
   Verify traffic flow
```

**Solution**:
```
Possible causes:
- Pool member down → Check backend services
- Network connectivity → Check cables/config
- Policy/rule blocking → Review iRules
- SSL certificate issue → Check cert validity
- Configuration error → Review virtual server config
```

### Pool Members Failing Health Checks

**Diagnosis**:
```
1. Check health check results
   Pool details > Monitoring

2. Manual health check
   telnet/curl to backend directly
   Verify endpoint responding

3. Check firewall rules
   Ensure LB can reach backend
   tcpdump on backend

4. Check health check config
   Interval too short?
   Timeout too short?
   Wrong endpoint?
```

**Solution**:
```
- Fix backend service
- Adjust health check parameters
- Open firewall rules
- Fix application health endpoint
```

---

**Last Updated**: 2025-11-19
**Version**: 2.0
