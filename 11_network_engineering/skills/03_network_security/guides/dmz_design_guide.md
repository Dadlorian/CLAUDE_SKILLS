# DMZ Design Guide

## DMZ Architecture Overview

### Single-Tier DMZ

```
Architecture:
┌──────────────┐
│  Internet    │
└──────┬───────┘
       │
   [Perimeter FW]
       │
    ┌──┴──┐
    │ DMZ │
    │ • Web servers
    │ • Mail servers
    │ • DNS servers
    └──┬──┘
       │
   [Internal FW]
       │
┌──────┴────────┐
│ Internal Net  │
│ • Workstations
│ • File servers
│ • Databases
└───────────────┘
```

### Multi-Tier DMZ (Recommended)

```
Architecture:
┌──────────────┐
│  Internet    │
└──────┬───────┘
       │
   [Perimeter FW]
       │
    ┌──┴──────────────────┐
    │ Web Tier (DMZ 1)     │
    │ • Load balancers     │
    │ • Web servers        │
    │ • API gateways       │
    └────────┬─────────────┘
             │
        [Internal FW]
             │
    ┌────────┴──────────────┐
    │ App Tier (DMZ 2)       │
    │ • App servers          │
    │ • Cache servers        │
    │ • Integration services │
    └────────┬───────────────┘
             │
        [Database FW]
             │
    ┌────────┴─────────────────┐
    │ Data Tier (Internal)      │
    │ • Database servers        │
    │ • Storage                 │
    │ • Backup systems          │
    └───────────────────────────┘
```

## DMZ Design Principles

### Access Control Rules

```
To DMZ (Inbound):
Internet → Web Tier:
- HTTP (80): Load balancers
- HTTPS (443): Load balancers
- SSH (22): Admin jump host only
- All others: DENY

To Internal (from DMZ):
Web Tier → App Tier:
- Application port (8080): Specific servers only
- SSH (22): Admin only
- DNS (53): Specific resolvers
- NTP (123): Time servers
- All others: DENY

App Tier → Data Tier:
- Database port (3306): Specific servers only
- SSH (22): DBA jump host only
- All others: DENY

From Internal (to DMZ):
- Admin access (SSH/RDP): Controlled
- Updates: Package manager servers
- Monitoring: Monitoring servers
- All others: DENY
```

## Multi-Tier DMZ Implementation

### Tier 1: Web Tier Design

```
Components:
- Load balancers (HAProxy, F5)
- Web servers (Apache, Nginx)
- API gateways (Kong, AWS API Gateway)
- WAF (Web Application Firewall)

Security:
- Auto-scaling (no manual scaling)
- DDoS protection
- SSL/TLS termination
- Rate limiting
- Input validation
- WAF rules

Network:
- Separate VLAN (10.1.10.0/24)
- Load balancer IP: 10.1.10.1
- Web servers: 10.1.10.5-10
- Outbound to App only
- Inbound from Internet only

Firewall Rules:
permit tcp any 10.1.10.0/24 eq 80
permit tcp any 10.1.10.0/24 eq 443
permit tcp any 10.1.10.1 eq 22 (SSH from jump host)
deny tcp any 10.1.10.0/24
```

### Tier 2: Application Tier Design

```
Components:
- App servers (Java, Python, Node.js)
- Cache servers (Redis, Memcached)
- Message queues (RabbitMQ, Kafka)
- Integration services (API, webhooks)

Security:
- Service-to-service auth (mTLS)
- API authentication (OAuth, JWT)
- Rate limiting
- Input validation
- Output encoding
- Error handling

Network:
- Separate VLAN (10.1.20.0/24)
- App servers: 10.1.20.5-20
- Cache servers: 10.1.20.30-35
- Message queue: 10.1.20.40-41

Firewall Rules:
permit tcp 10.1.10.0/24 10.1.20.0/24 eq 8080 (Web → App)
permit tcp 10.1.20.0/24 10.1.30.0/24 eq 3306 (App → DB)
permit tcp 10.1.20.0/24 10.1.20.30 eq 6379 (App → Cache)
permit tcp 10.1.20.0/24 10.1.20.40 eq 5672 (App → Queue)
deny tcp any 10.1.20.0/24
```

### Tier 3: Data Tier Design

```
Location: Internal (not DMZ)

Components:
- Primary database
- Secondary database (replication)
- Backup systems
- Data warehouse
- Analytics systems

Security:
- Encryption at rest (TLS, AES-256)
- Encryption in transit (SSL/TLS)
- Access control (IP-based, app account)
- Audit logging (all access)
- Regular backups
- Disaster recovery

Network:
- Internal VLAN only (10.1.30.0/24)
- Database servers: 10.1.30.5-10
- Backup servers: 10.1.30.20
- Analytics: 10.1.30.30
- No internet access
- No DMZ access

Firewall Rules:
permit tcp 10.1.20.0/24 10.1.30.5 eq 3306 (App only)
permit tcp 10.1.100.0/24 10.1.30.5 eq 3306 (DBA only)
permit tcp 10.1.30.0/24 10.1.30.0/24 (Internal replication)
deny tcp any 10.1.30.0/24 log
```

## DMZ Deployment Process

### Phase 1: Planning (Week 1-2)

```
Tasks:
☐ Define DMZ scope
☐ Identify systems needed
☐ Document traffic flows
☐ Design network topology
☐ Plan IP allocation
☐ Design firewall rules
☐ Create test lab
☐ Document architecture
```

### Phase 2: Lab Testing (Week 3-4)

```
Tasks:
☐ Deploy in lab
☐ Test all traffic flows
☐ Verify firewall rules
☐ Load test systems
☐ Validate performance
☐ Test failover
☐ Security scan
☐ Create runbooks
```

### Phase 3: Production Deployment (Week 5-8)

```
Phase 3A: Infrastructure
- Deploy switches/routers
- Configure VLANs
- Configure firewall zones
- Test basic connectivity

Phase 3B: Web Tier
- Deploy load balancers
- Deploy web servers
- Test internet connectivity
- Validate performance

Phase 3C: App Tier
- Deploy app servers
- Configure service-to-service
- Connect to database
- Test full application flow

Phase 3D: Monitoring
- Deploy monitoring
- Configure alerting
- Verify logging
- Test incident response
```

## DMZ Security Hardening

### System Hardening

```
All DMZ Servers:
- Minimal OS installation (remove unnecessary packages)
- Disable unnecessary services
- Enable firewall on each host
- Antivirus/malware protection
- Regular patching
- File integrity monitoring
- Audit logging
- No local admin accounts (disable)

Configuration:

Linux:
# Remove unnecessary packages
apt-get autoremove

# Disable unnecessary services
systemctl disable cups
systemctl disable avahi-daemon

# Enable host firewall
ufw enable
ufw default deny incoming
ufw allow from 10.1.10.0/24 to any port 22

# File integrity
aide --init
aide --check

Windows:
# Disable unnecessary services
Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol
Disable-WindowsOptionalFeature -Online -FeatureName NetBT

# Enable host firewall
Set-NetFirewallProfile -Enabled True

# File integrity monitoring
Enable-NTFSShortNames -Disable
```

### Application Hardening

```
Web Servers:
- HTTPS only (TLS 1.2+)
- Security headers (CSP, HSTS, X-Frame-Options)
- WAF enabled
- Error page customization
- Rate limiting
- DDoS protection

Configuration (Nginx):

server {
    listen 443 ssl http2;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
```

### Logging and Monitoring

```
Collect Logs:
- Web server access logs (per request)
- Application logs (errors, events)
- Firewall logs (all zone transitions)
- System logs (authentication, changes)
- Database logs (queries, access)

Centralize:
- Syslog server (10.1.50.10)
- ELK stack (Elasticsearch, Logstash, Kibana)
- Splunk
- Datadog
- CloudWatch

Retention:
- Hot: 30 days (online, searchable)
- Warm: 90 days (online, slower)
- Cold: 1 year (archive)
```

## DMZ Monitoring

### Health Checks

```
Application Health:
- HTTP status codes
- Response times
- Error rates
- Database connectivity
- Cache hit ratio
- Queue depth

Monitoring Tools:
- Prometheus/Grafana
- Elastic Stack
- Datadog
- New Relic
- CloudWatch

Metrics by Component:

Web Tier:
- CPU: < 75%
- Memory: < 80%
- Network: < 70%
- 5xx errors: < 0.5%
- Response time: < 200ms p99

App Tier:
- CPU: < 75%
- Memory: < 80%
- Thread pool: < 80%
- Queue depth: < 1000
- Cache hit rate: > 80%

Data Tier:
- CPU: < 70%
- Memory: < 80%
- Disk I/O: < 80%
- Query time p99: < 100ms
- Replication lag: < 1 second
```

### Alerting

```
Critical Alerts (Immediate):
- Zone down
- Database unreachable
- Failed authentication spike
- DDoS detected
- Security incident

High Priority (< 15 min):
- 5xx error rate > 5%
- Response time > 1 second
- CPU > 90%
- Disk > 90%

Medium Priority (< 1 hour):
- CPU > 75%
- Memory > 85%
- Cache hit rate drops
- Unusual traffic pattern
```

## Disaster Recovery

### Backup Strategy

```
Web Tier:
- Config management (Infrastructure as Code)
- Auto-scaling (redeploy if needed)
- RTO: 15 minutes
- RPO: 0 (stateless)

App Tier:
- Database backups
- Configuration backups
- RTO: 30 minutes
- RPO: < 1 hour

Data Tier:
- Full daily backups
- Incremental hourly
- Replicated to secondary site
- RTO: < 1 hour
- RPO: < 15 minutes

Test Recovery:
- Monthly full recovery test
- Quarterly failover test
- Annual disaster recovery exercise
```

## Troubleshooting Guide

```
Issue: Web Server Not Responding
Diagnosis:
1. Ping from firewall
2. Check web server status
3. Review logs
4. Check firewall rule
5. Verify load balancer health

Issue: Slow Application Response
Diagnosis:
1. Check database performance
2. Check cache hit ratio
3. Monitor network latency
4. Check app server CPU/memory
5. Review application logs

Issue: Connection Refused
Diagnosis:
1. Verify firewall rule allows
2. Check service running
3. Verify port correct
4. Check ACL/security group
5. Review firewall logs
```
