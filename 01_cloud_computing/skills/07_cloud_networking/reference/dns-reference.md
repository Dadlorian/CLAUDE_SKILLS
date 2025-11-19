# DNS and Traffic Management Reference

## Introduction

Domain Name System (DNS) translates human-readable domain names into IP addresses. Cloud DNS services provide global traffic management, routing policies, health monitoring, and disaster recovery capabilities.

## DNS Fundamentals

### DNS Resolution Flow

```
1. User types www.example.com
2. Browser checks local cache
3. Query to recursive DNS resolver
4. Resolver checks cache
5. Query to root nameserver (.)
6. Query to TLD nameserver (.com)
7. Query to authoritative nameserver (example.com)
8. Returns IP address
9. Browser connects to IP
```

### Record Types

**A Record** (IPv4 Address):
```
www.example.com.  300  IN  A  192.0.2.1
```

**AAAA Record** (IPv6 Address):
```
www.example.com.  300  IN  AAAA  2001:0db8::1
```

**CNAME Record** (Canonical Name):
```
blog.example.com.  300  IN  CNAME  example.com.
```

**MX Record** (Mail Exchange):
```
example.com.  300  IN  MX  10  mail.example.com.
```

**TXT Record** (Text):
```
example.com.  300  IN  TXT  "v=spf1 include:_spf.example.com ~all"
```

**NS Record** (Name Server):
```
example.com.  300  IN  NS  ns1.example.com.
```

**SOA Record** (Start of Authority):
```
example.com.  300  IN  SOA  ns1.example.com. admin.example.com. (
    2025011901  ; Serial
    7200        ; Refresh
    3600        ; Retry
    1209600     ; Expire
    300         ; Minimum TTL
)
```

**SRV Record** (Service):
```
_service._proto.example.com.  300  IN  SRV  10  60  8080  target.example.com.
```

**CAA Record** (Certificate Authority Authorization):
```
example.com.  300  IN  CAA  0  issue  "letsencrypt.org"
```

### TTL (Time To Live)

**Purpose**:
- How long to cache DNS record
- Balance between propagation speed and query volume

**Recommendations**:
```
Long TTL (hours/days):
- Stable records
- High query volume
- Cost optimization

Short TTL (seconds/minutes):
- Frequent changes
- Failover scenarios
- Testing/migration

Common values:
- 60s: Very dynamic
- 300s (5 min): Dynamic
- 3600s (1 hour): Standard
- 86400s (24 hours): Static
```

## AWS Route 53

### Hosted Zones

**Public Hosted Zone**:
```
Domain: example.com
Name servers:
- ns-123.awsdns-12.com
- ns-456.awsdns-34.net
- ns-789.awsdns-56.org
- ns-012.awsdns-78.co.uk

Internet-accessible
Global DNS resolution
```

**Private Hosted Zone**:
```
Domain: internal.example.com
Associated VPCs:
- vpc-123abc (us-east-1)
- vpc-456def (us-west-2)

VPC-only access
Split-horizon DNS
```

### Routing Policies

**Simple Routing**:
```
www.example.com --> 192.0.2.1

Single resource
No health checks
```

**Weighted Routing**:
```
www.example.com:
- 70% --> Server A (us-east-1)
- 30% --> Server B (us-west-2)

Traffic distribution
A/B testing
Gradual migrations
```

**Latency-Based Routing**:
```
www.example.com:
- us-east-1: Server A
- us-west-2: Server B
- eu-west-1: Server C

Route to lowest latency
User location based
AWS measures latency
```

**Geolocation Routing**:
```
www.example.com:
- North America --> us-east-1
- Europe --> eu-west-1
- Asia --> ap-southeast-1
- Default --> us-east-1

Content localization
Regional compliance
Language-specific content
```

**Geoproximity Routing**:
```
www.example.com:
- us-east-1 (bias: +20)
- us-west-2 (bias: 0)
- eu-west-1 (bias: -10)

Fine-grained geographic control
Bias adjusts region size
Traffic Flow visual editor
```

**Failover Routing**:
```
www.example.com:
- Primary: us-east-1 (health checked)
- Secondary: us-west-2 (health checked)

Active-passive
Disaster recovery
Automatic failover
```

**Multi-Value Answer Routing**:
```
www.example.com:
- 192.0.2.1 (health checked)
- 192.0.2.2 (health checked)
- 192.0.2.3 (health checked)

Returns multiple IPs
Client-side load balancing
Health check per record
```

### Health Checks

**Endpoint Health Checks**:
```
Protocol: HTTP/HTTPS/TCP
IP or Domain: 192.0.2.1
Port: 80
Path: /health
Interval: 30 seconds (or 10 seconds fast)
Failure threshold: 3
String matching: Optional
```

**Calculated Health Checks**:
```
Child checks:
- us-east-1-web-1
- us-east-1-web-2
- us-east-1-web-3

Logic: 2 of 3 must be healthy
Parent reports aggregate health
```

**CloudWatch Alarm Health Checks**:
```
CloudWatch Alarm --> Health Check

Monitor any AWS metric
Custom application metrics
Complex health logic
```

### Traffic Flow

**Visual Policy Editor**:
```
Policy:
1. Geolocation rule (Region-based)
   - NA --> Failover rule
     - Primary: us-east-1
     - Secondary: us-west-2
   - EU --> eu-west-1
   - Default --> us-east-1

2. Health checks on all endpoints

Complex routing policies
Visual diagram
Reusable policies
Versioning support
```

### DNSSEC

**DNS Security Extensions**:
```
Enable DNSSEC signing
Chain of trust
Prevents DNS spoofing
RRSIG, DNSKEY, DS records

Supported on Route 53
```

## Azure DNS

### DNS Zones

**Public DNS Zone**:
```
example.com
Name servers:
- ns1-01.azure-dns.com
- ns2-01.azure-dns.net
- ns3-01.azure-dns.org
- ns4-01.azure-dns.info
```

**Private DNS Zone**:
```
internal.example.com
Virtual network links:
- vnet-prod
- vnet-dev

Auto-registration: Enabled/Disabled
```

### Traffic Manager

**Profile Types**:

**Priority (Failover)**:
```
Priority 1: Primary endpoint (US East)
Priority 2: Secondary endpoint (US West)
Priority 3: Tertiary endpoint (EU West)

Health monitoring
Automatic failover
```

**Weighted**:
```
Endpoint A: Weight 70
Endpoint B: Weight 30

Traffic distribution
Blue-green deployments
Canary releases
```

**Performance**:
```
Endpoint: us-east-1 (for US users)
Endpoint: eu-west-1 (for EU users)
Endpoint: asia-east-1 (for Asia users)

Lowest latency routing
Global performance
```

**Geographic**:
```
North America --> US East endpoint
Europe --> EU West endpoint
Asia --> Asia East endpoint
Default --> US East endpoint

Compliance requirements
Content localization
```

**MultiValue**:
```
Returns multiple healthy endpoints
Client-side load balancing
Up to 8 IPv4 or IPv6 addresses
```

**Subnet**:
```
IP range 10.0.0.0/8 --> Endpoint A
IP range 172.16.0.0/12 --> Endpoint B
Default --> Endpoint C

Corporate network routing
VPN user routing
```

### Azure Private DNS

**Auto-Registration**:
```
VNet Link: Enabled
Auto-registration: Enabled

VM deployed in VNet
DNS record auto-created
VM deleted, record auto-removed
```

## Google Cloud DNS

### Managed Zones

**Public Zone**:
```
example.com
Name servers:
- ns-cloud-a1.googledomains.com
- ns-cloud-a2.googledomains.com
- ns-cloud-a3.googledomains.com
- ns-cloud-a4.googledomains.com
```

**Private Zone**:
```
internal.example.com
VPC networks:
- vpc-prod
- vpc-dev

DNS peering
Forwarding zones
```

### Routing Policies

**Weighted Round Robin**:
```
www.example.com:
- 80% --> Backend pool A
- 20% --> Backend pool B

Health checks
Graceful rollouts
```

**Geolocation Routing**:
```
www.example.com:
- us-east1 --> US users
- europe-west1 --> EU users
- asia-east1 --> Asia users
```

**Failover**:
```
Primary: Backend pool A
Backup: Backend pool B

Health check-based
Automatic failover
```

### DNS Peering

**Cross-Project DNS Resolution**:
```
Project A (DNS zone owner)
    |
DNS Peering
    |
Project B (Consumer)

Centralized DNS management
Shared services architecture
```

### Cloud DNS Forwarding

**Hybrid DNS Resolution**:
```
GCP VPC --> Cloud DNS
    |
Forwarding Zone: onprem.example.com
    |
Forward to: On-premises DNS (10.1.1.53)
```

### DNSSEC Support

**Signed Zones**:
```
Enable DNSSEC on zone
Automatic key rotation
DS records for parent zone
Chain of trust validation
```

## Advanced DNS Patterns

### Split-Horizon DNS

**Internal and External Views**:

**External Zone** (Public):
```
www.example.com --> 203.0.113.10 (Public IP)
api.example.com --> 203.0.113.20 (Public IP)
```

**Internal Zone** (Private):
```
www.example.com --> 10.0.1.10 (Private IP)
api.example.com --> 10.0.1.20 (Private IP)
db.example.com --> 10.0.2.10 (Private IP, not public)
```

### Subdomain Delegation

**Delegate Subdomain to Another Zone**:

**Parent Zone** (example.com):
```
dev.example.com.  IN  NS  ns1.dev-dns.example.com.
dev.example.com.  IN  NS  ns2.dev-dns.example.com.
```

**Child Zone** (dev.example.com):
```
Managed separately
Different team/account
Independent record management
```

### Alias Records

**AWS Route 53 Alias**:
```
example.com --> ALB (dualstack.my-alb-123.us-east-1.elb.amazonaws.com)

Benefits:
- No charge for alias queries to AWS resources
- Automatic IP updates
- Health checks at apex
- Can use for zone apex (@)
```

**Azure Alias Record**:
```
example.com --> Traffic Manager endpoint
example.com --> Azure CDN endpoint
example.com --> Public IP resource
```

### Wildcard Records

**Catch-All Subdomain**:
```
*.example.com.  300  IN  A  192.0.2.1

Matches:
- anything.example.com
- sub.domain.example.com

Does not match:
- example.com (apex)
```

## Global Traffic Management

### Multi-Region Active-Active

**Route 53 Architecture**:
```
Route 53 (Latency-based routing)
    |
    +-- us-east-1: ALB + Health Check
    |
    +-- us-west-2: ALB + Health Check
    |
    +-- eu-west-1: ALB + Health Check

Users routed to nearest healthy region
Automatic failover
Even load distribution
```

### Disaster Recovery

**Active-Passive Failover**:

**Normal State**:
```
www.example.com (Primary) --> us-east-1 (Healthy)
www.example.com (Secondary) --> us-west-2 (Standby)

Primary serving all traffic
```

**Failure State**:
```
www.example.com (Primary) --> us-east-1 (Unhealthy)
www.example.com (Secondary) --> us-west-2 (Active)

Automatic failover
Secondary now serving traffic
```

**RTO/RPO**:
```
RTO (Recovery Time Objective):
- DNS TTL + Health check interval
- Typically 1-5 minutes

RPO (Recovery Point Objective):
- Data replication lag
- Application-dependent
```

### Blue-Green Deployments

**Weighted Routing Strategy**:

**Phase 1** (Initial):
```
www.example.com:
- 100% Blue (current version)
- 0% Green (new version)
```

**Phase 2** (Testing):
```
www.example.com:
- 95% Blue
- 5% Green (canary)
```

**Phase 3** (Rollout):
```
www.example.com:
- 50% Blue
- 50% Green
```

**Phase 4** (Complete):
```
www.example.com:
- 0% Blue (deprecated)
- 100% Green (live)
```

## DNS Security

### DNSSEC (DNS Security Extensions)

**Purpose**:
- Prevent DNS spoofing
- Verify DNS data integrity
- Chain of trust from root

**Record Types**:
```
RRSIG: Digital signature
DNSKEY: Public key
DS: Delegation Signer
NSEC/NSEC3: Proof of non-existence
```

**Implementation**:
```
1. Enable DNSSEC on zone
2. Generate key-signing key (KSK) and zone-signing key (ZSK)
3. Sign all records
4. Publish DS record at parent zone
5. Configure auto-renewal
```

### DDoS Protection

**Strategies**:
- Use managed DNS service (built-in protection)
- Distribute name servers geographically
- Rate limiting
- Anycast routing
- AWS Shield, Azure DDoS Protection
- Monitor query patterns

### DNS Firewall (Route 53 Resolver DNS Firewall)

**Block Malicious Domains**:
```
Rule groups:
- Block known malware domains
- Block phishing sites
- Allow corporate domains
- Alert on suspicious queries

VPC-level enforcement
Centralized management
```

## Performance Optimization

### TTL Optimization

**Strategy**:
```
Pre-change: Short TTL (60s)
During change: Make DNS update
Post-change: Long TTL (3600s)

Minimize propagation time
Reduce query volume
```

### Anycast Routing

**Global Distribution**:
```
Same IP announced from multiple locations
User routed to nearest location
Reduced latency
DDoS mitigation

Supported: Route 53, Cloud DNS, Azure DNS
```

### DNS Query Optimization

**Reduce Queries**:
- Browser DNS cache
- Application DNS caching
- Longer TTLs for stable records
- Use CNAMEs sparingly (additional lookup)

## Monitoring and Logging

### Route 53 Query Logging

**Enable Logging**:
```
Logs queries to CloudWatch Logs
Information logged:
- Timestamp
- Hosted zone ID
- Query name
- Query type
- Response code
- Edge location

Analyze with CloudWatch Insights
```

### Azure DNS Analytics

**Metrics**:
```
Query count
Query latency
Record set count
Record set capacity

Alerts on anomalies
Query pattern analysis
```

### Cloud DNS Logging

**Cloud Logging Integration**:
```
Query logs exported to Cloud Logging
Fields:
- Source IP
- Query name
- Query type
- Response code
- Latency

Analyze with Log Analytics
```

### Health Check Monitoring

**Key Metrics**:
```
Health check status
Response time
Failure count
Child health check status

Alerts:
- Endpoint unhealthy
- Failover triggered
- High latency
```

## Cost Optimization

### Pricing Models

**Route 53**:
```
Hosted zone: $0.50/month
Standard queries: $0.40/million
Latency-based: $0.60/million
Geo DNS: $0.70/million
Health checks: $0.50/month each

Cost optimization:
- Consolidate hosted zones
- Use alias records (free to AWS resources)
- Optimize health check count
```

**Azure DNS**:
```
Hosted zone: $0.50/month (first 25)
First billion queries: $0.40/million
Additional: $0.20/million

Traffic Manager:
Endpoint: $0.54/month
Health checks: Included
DNS queries: $0.54/million
```

**Cloud DNS**:
```
Managed zone: $0.20/month
First billion queries: $0.40/million
Additional: $0.20/million

Cost optimization:
- Appropriate TTLs
- Consolidate zones
```

## Troubleshooting

### DNS Resolution Issues

**Common Problems**:

**NXDOMAIN** (Non-Existent Domain):
```
Cause: Record doesn't exist
Fix: Verify record created, check zone
```

**SERVFAIL** (Server Failure):
```
Cause: DNS server error, DNSSEC validation failure
Fix: Check name server logs, verify DNSSEC configuration
```

**Timeout**:
```
Cause: Firewall blocking, server unreachable
Fix: Verify network path, check security groups
```

**Wrong IP Returned**:
```
Cause: DNS cache, wrong record
Fix: Check TTL, clear cache, verify record
```

### Diagnostic Tools

**Command Line**:
```bash
# Query DNS
dig example.com
nslookup example.com

# Trace DNS resolution
dig +trace example.com

# Check specific nameserver
dig @8.8.8.8 example.com

# Check record type
dig example.com MX

# Reverse lookup
dig -x 192.0.2.1
```

**Online Tools**:
- DNS Checker (global propagation)
- MX Toolbox
- WhatsMyDNS.net
- IntoDNS

## Best Practices

### Design

1. Use managed DNS services for reliability
2. Implement health checks for failover
3. Use appropriate routing policies
4. Plan for disaster recovery
5. Document DNS architecture

### Security

1. Enable DNSSEC where supported
2. Use private zones for internal resources
3. Implement DNS firewall
4. Monitor for DDoS attacks
5. Restrict zone transfer (AXFR)
6. Use CAA records for certificate control

### Operations

1. Monitor DNS queries and latency
2. Set up alerting for health check failures
3. Test failover scenarios regularly
4. Document DNS changes
5. Use infrastructure as code
6. Maintain DNS inventory

### Performance

1. Optimize TTLs
2. Use alias records for AWS resources
3. Minimize CNAME chains
4. Enable query logging selectively
5. Use geolocation/latency routing
6. Cache DNS at application level

## Conclusion

DNS and traffic management are critical for global application delivery, disaster recovery, and performance optimization. Proper routing policies, health checks, and monitoring ensure reliable and performant DNS resolution for users worldwide.
