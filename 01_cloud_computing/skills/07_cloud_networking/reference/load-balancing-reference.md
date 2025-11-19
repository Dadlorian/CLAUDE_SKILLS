# Load Balancing Reference

## Introduction

Load balancing distributes incoming traffic across multiple servers, ensuring high availability, fault tolerance, and optimal resource utilization in cloud environments.

## Load Balancer Types

### Layer 4 vs Layer 7

**Layer 4 (Transport Layer)**:
- TCP/UDP load balancing
- IP address and port-based routing
- High performance, low latency
- Connection-level load balancing
- No content inspection

**Layer 7 (Application Layer)**:
- HTTP/HTTPS load balancing
- Content-based routing (URL, headers, cookies)
- SSL/TLS termination
- WebSocket support
- Request-level load balancing

### Comparison Table

| Feature | Layer 4 | Layer 7 |
|---------|---------|---------|
| Protocol | TCP/UDP | HTTP/HTTPS |
| Performance | Higher throughput | Lower throughput |
| Routing | IP/Port | URL/Headers/Content |
| SSL Termination | Pass-through | Supported |
| WebSocket | Limited | Full support |
| Cost | Lower | Higher |
| Use Case | High performance | Web applications |

## AWS Elastic Load Balancing

### Application Load Balancer (ALB)

**Characteristics**:
- Layer 7 load balancer
- HTTP/HTTPS/HTTP/2
- WebSocket and gRPC support
- Content-based routing
- Host-based and path-based routing
- Lambda targets
- IP address targets

**Architecture**:
```
Internet
    |
Application Load Balancer
    |
Target Groups
    |
+-- Web App (EC2/ECS/Lambda)
|
+-- API (EC2/ECS/Lambda)
|
+-- Admin (EC2)
```

**Routing Rules**:
```
Host-based:
  api.example.com     --> API target group
  web.example.com     --> Web target group
  admin.example.com   --> Admin target group

Path-based:
  /api/*   --> API target group
  /images/* --> Static content group
  /*       --> Default web group

Header-based:
  User-Agent: Mobile --> Mobile target group
  User-Agent: Desktop --> Desktop target group
```

**Features**:
- Sticky sessions (cookie-based)
- SSL/TLS termination
- SNI support (multiple certificates)
- HTTP/2 and gRPC
- Fixed response actions
- Redirect actions
- Authentication (OIDC, Cognito)

### Network Load Balancer (NLB)

**Characteristics**:
- Layer 4 load balancer
- Ultra-high performance (millions of requests/sec)
- Static IP addresses
- Elastic IP support
- Preserve source IP
- TCP, UDP, TLS
- PrivateLink support

**Architecture**:
```
Internet
    |
Network Load Balancer (Static IPs)
    |
Target Groups (TCP/UDP)
    |
+-- Database Proxy (RDS Proxy)
|
+-- Game Servers (UDP)
|
+-- TCP Services
```

**Use Cases**:
- High-performance applications
- Static IP requirements
- Non-HTTP protocols
- PrivateLink services
- Extreme scale (millions of requests)

### Gateway Load Balancer (GWLB)

**Characteristics**:
- Layer 3 gateway + Layer 4 load balancing
- Deploy third-party virtual appliances
- Transparent to applications
- GENEVE protocol (port 6081)
- Centralized security appliances

**Architecture**:
```
Internet --> IGW --> GWLB --> Firewall/IDS Target Group --> Application
```

**Use Cases**:
- Network firewalls
- Intrusion detection/prevention
- Deep packet inspection
- Third-party security appliances

### Classic Load Balancer (Legacy)

**Characteristics**:
- Previous generation
- Layer 4 and basic Layer 7
- Not recommended for new applications
- Migration to ALB/NLB recommended

## Azure Load Balancing

### Azure Load Balancer

**Characteristics**:
- Layer 4 load balancer
- Internal and public
- Zone-redundant
- HA ports
- Outbound connections (SNAT)

**SKUs**:

**Basic**:
- Up to 300 instances
- Single availability set
- No SLA
- Free

**Standard**:
- Up to 1000 instances
- Availability zones
- 99.99% SLA
- HA ports
- Secure by default

**Architecture**:
```
Internet
    |
Azure Load Balancer (Standard)
    |
Backend Pool
    |
+-- VM Scale Set
|
+-- Availability Set
|
+-- Individual VMs
```

### Azure Application Gateway

**Characteristics**:
- Layer 7 load balancer
- WAF integration
- URL-based routing
- SSL/TLS termination
- Cookie-based session affinity
- Autoscaling

**SKUs**:
- Standard_v2: ALB features
- WAF_v2: ALB + WAF

**Architecture**:
```
Internet
    |
Application Gateway + WAF
    |
Backend Pools
    |
+-- App Service
|
+-- VM Scale Sets
|
+-- Internal IPs
```

**Routing**:
```
Path-based:
  /images/* --> Static storage backend
  /api/*    --> API backend
  /*        --> Web app backend

Multi-site:
  contoso.com --> Contoso backend
  fabrikam.com --> Fabrikam backend
```

### Azure Front Door

**Characteristics**:
- Global Layer 7 load balancer
- Microsoft edge network
- URL-based routing
- Session affinity
- SSL/TLS offload
- Web Application Firewall
- CDN integration

**Architecture**:
```
Users (Global)
    |
Azure Front Door (Edge Locations)
    |
Backend Pools (Multi-Region)
    |
+-- Region 1: App Service
|
+-- Region 2: App Service
|
+-- Region 3: App Service
```

**Use Cases**:
- Global applications
- Multi-region failover
- Performance acceleration
- WAF at edge

### Azure Traffic Manager

**Characteristics**:
- DNS-based load balancer
- Global traffic distribution
- Multiple routing methods
- Health monitoring
- Endpoint prioritization

**Routing Methods**:
- Priority: Failover
- Weighted: Traffic distribution
- Performance: Lowest latency
- Geographic: User location
- Multivalue: Multiple endpoints
- Subnet: Client IP ranges

## GCP Load Balancing

### Global Load Balancing

**HTTP(S) Load Balancing**:
- Global, anycast IP
- Layer 7 load balancing
- URL-based routing
- SSL offload
- Cloud CDN integration
- Cloud Armor (WAF)

**Architecture**:
```
Global Users
    |
Global Anycast IP (GLB)
    |
Backend Services (Multi-Region)
    |
+-- us-central1: Instance Group
|
+-- europe-west1: Instance Group
|
+-- asia-east1: Instance Group
```

**SSL Proxy Load Balancing**:
- Global SSL/TLS termination
- Non-HTTP SSL traffic
- Layer 4 with SSL intelligence

**TCP Proxy Load Balancing**:
- Global TCP load balancing
- IPv6 to IPv4 translation
- Intelligent routing

### Regional Load Balancing

**Network Load Balancing**:
- Regional Layer 4
- Ultra-high performance
- Preserve source IP
- UDP, TCP, ESP, ICMP support

**Internal Load Balancing**:
- Private load balancing
- RFC 1918 IPs only
- Layer 4 (TCP/UDP)
- No external exposure

**Internal HTTP(S) Load Balancing**:
- Private Layer 7
- Service mesh integration
- Traffic Director compatible

## Load Balancing Algorithms

### Round Robin

**Mechanism**:
- Distributes requests sequentially
- Each server gets equal share
- Simple and effective

**Best For**:
- Homogeneous server pool
- Similar request processing time
- Stateless applications

### Least Connections

**Mechanism**:
- Routes to server with fewest active connections
- Dynamic load distribution
- Accounts for long-lived connections

**Best For**:
- Variable request processing time
- Non-uniform traffic patterns
- Long-lived connections

### Least Response Time

**Mechanism**:
- Routes to server with lowest response time
- Combines connections and latency
- Performance-aware

**Best For**:
- Performance-critical applications
- Mixed workload types
- Geographic distribution

### IP Hash

**Mechanism**:
- Hash source IP to determine server
- Consistent routing per client
- Session persistence

**Best For**:
- Session-based applications
- Stateful connections
- Cache optimization

### Weighted Round Robin

**Mechanism**:
- Assigns weight to each server
- Higher weight = more traffic
- Accounts for server capacity

**Best For**:
- Heterogeneous server pool
- Different server capacities
- Gradual rollouts (canary)

## Health Checks

### Health Check Types

**HTTP/HTTPS Health Checks**:
```
Protocol: HTTP/HTTPS
Path: /health or /
Expected: 200 OK
Interval: 5-30 seconds
Timeout: 2-10 seconds
Healthy Threshold: 2-10
Unhealthy Threshold: 2-10
```

**TCP Health Checks**:
```
Protocol: TCP
Port: Application port
Connection: Success/failure
Interval: 5-30 seconds
```

**Custom Health Checks**:
```
Application-specific logic
Database connectivity
Dependency checks
Resource availability
```

### Health Check Best Practices

1. **Lightweight**: Fast response, minimal resource usage
2. **Comprehensive**: Check dependencies
3. **Appropriate Intervals**: Balance detection speed and load
4. **Proper Thresholds**: Avoid flapping
5. **Graceful Degradation**: Warm-up period after deployment

## SSL/TLS Configuration

### Certificate Management

**AWS Certificate Manager (ACM)**:
- Free SSL/TLS certificates
- Automatic renewal
- Multiple domain names (SAN)
- Wildcard certificates
- Easy integration with ALB/NLB

**Azure Key Vault**:
- Certificate storage
- Automatic renewal
- RBAC integration
- Managed certificates

**GCP Managed Certificates**:
- Free Google-managed certificates
- Automatic renewal
- DV (Domain Validated)

### SSL Policies

**AWS SSL Policies**:
```
ELBSecurityPolicy-TLS-1-2-2017-01 (Recommended)
- TLS 1.2 only
- Strong ciphers

ELBSecurityPolicy-FS-1-2-Res-2020-10
- Forward secrecy
- TLS 1.2+
- Strict security
```

**Cipher Suites**:
```
Recommended:
- ECDHE-RSA-AES128-GCM-SHA256
- ECDHE-RSA-AES256-GCM-SHA384
- ECDHE-RSA-AES128-SHA256

Avoid:
- DES, 3DES
- RC4
- MD5
```

### SNI (Server Name Indication)

**Multiple Certificates**:
```
ALB/Application Gateway
  |
  +-- cert1.pem (example.com)
  |
  +-- cert2.pem (api.example.com)
  |
  +-- cert3.pem (admin.example.com)

Route based on SNI hostname
```

## Session Persistence

### Sticky Sessions

**Cookie-Based Stickiness** (ALB):
```
Load Balancer Generated:
- AWSALB cookie
- Duration: 1 second to 7 days

Application Generated:
- Custom application cookie
- Load balancer forwards to same target
```

**Source IP Affinity** (NLB):
```
Hash source IP address
Route to same target
Duration: Configurable
```

**Best Practices**:
- Use for session-based apps
- Consider external session store (Redis, DynamoDB)
- Monitor target distribution
- Plan for target failures

## Cross-Zone Load Balancing

### AWS

**Enabled by Default**: ALB, GWLB
**Optional**: NLB (data transfer charges apply)

**Architecture**:
```
ALB (us-east-1)
    |
    +-- AZ-1: 2 instances (33% each)
    |
    +-- AZ-2: 4 instances (16% each)

With cross-zone: Even distribution
Without cross-zone: Uneven distribution
```

### Azure

**Availability Zones**:
- Zone-redundant load balancer
- Distributes across zones
- Survives zone failure

### GCP

**Global Load Balancing**:
- Distributes across regions
- Automatic failover
- Intelligent routing

## Auto Scaling Integration

### AWS Auto Scaling

**Target Tracking**:
```
ALB + Target Group + Auto Scaling Group

Metrics:
- ALBRequestCountPerTarget
- CPUUtilization
- NetworkIn/Out

Scale Out: Add instances
Scale In: Remove instances
```

### Azure VMSS

**Auto Scaling Rules**:
```
Application Gateway + VMSS

Metrics:
- CPU percentage
- Network in/out
- HTTP queue length

Custom metrics via Application Insights
```

### GCP Managed Instance Groups

**Auto Scaling**:
```
Load Balancer + MIG

Metrics:
- CPU utilization
- HTTP load balancing utilization
- Cloud Monitoring metrics

Scale up/down based on policy
```

## Advanced Routing

### Content-Based Routing

**Host Header**:
```
Host: api.example.com --> API target group
Host: web.example.com --> Web target group
```

**Path Pattern**:
```
/api/*     --> API target group
/static/*  --> S3 static website
/admin/*   --> Admin target group
/*         --> Default target group
```

**HTTP Method**:
```
POST /api/users --> Write API target group
GET  /api/users --> Read API target group
```

**Query String**:
```
?version=v1 --> V1 target group
?version=v2 --> V2 target group
```

**HTTP Headers**:
```
X-Mobile-App: true --> Mobile target group
X-Region: us --> US target group
```

### Weighted Target Groups

**Canary Deployments**:
```
/api/* routing:
- 90% --> Production target group (v1)
- 10% --> Canary target group (v2)

Gradually shift:
- 80% v1, 20% v2
- 50% v1, 50% v2
- 0% v1, 100% v2
```

## Global Load Balancing

### Multi-Region Architecture

**Active-Active**:
```
Route 53 (Geolocation Routing)
    |
    +-- us-east-1: ALB --> Application
    |
    +-- eu-west-1: ALB --> Application
    |
    +-- ap-southeast-1: ALB --> Application

Users routed to nearest region
```

**Active-Passive**:
```
Route 53 (Failover Routing)
    |
    +-- Primary: us-east-1 ALB
    |
    +-- Secondary: us-west-2 ALB

Failover on health check failure
```

### Global Accelerator (AWS)

**Architecture**:
```
Users (Global)
    |
AWS Global Accelerator (Anycast IPs)
    |
AWS Edge Locations
    |
AWS Private Network
    |
Regional Endpoints (ALB/NLB/EC2/EIP)
```

**Benefits**:
- Static anycast IPs
- Improved performance (up to 60%)
- Automatic failover
- DDoS protection

## Performance Optimization

### Connection Optimization

**Connection Pooling**:
- Reuse connections to targets
- HTTP Keep-Alive
- Reduce connection overhead

**HTTP/2**:
- Multiplexing
- Header compression
- Server push
- Binary protocol

### Pre-warming

**High Traffic Events**:
```
Contact cloud provider support
Provide:
- Expected traffic pattern
- Start/end time
- Estimated requests per second

Load balancer scaled in advance
```

### Caching

**CloudFront + ALB**:
```
Users --> CloudFront (Edge Cache) --> ALB --> Application

Cache static and dynamic content
Reduce backend load
Improve response time
```

## Monitoring and Metrics

### Key Metrics

**AWS CloudWatch**:
```
Request Count
Target Response Time
Healthy/Unhealthy Host Count
HTTP 4xx/5xx Count
Active Connection Count
Processed Bytes
```

**Azure Monitor**:
```
Data Path Availability
Health Probe Status
SNAT Connection Count
Byte Count
Packet Count
```

**GCP Cloud Monitoring**:
```
Request Count
Request Bytes
Backend Latency
Error Rate
Frontend RTT
```

### Alerting

**Critical Alerts**:
- All targets unhealthy
- High error rate (5xx)
- Extreme latency
- Connection failures

**Warning Alerts**:
- Some targets unhealthy
- Elevated error rate (4xx)
- Increased latency
- Approaching limits

## Security Best Practices

### DDoS Protection

**AWS Shield**:
- Standard (automatic, free)
- Advanced (paid, additional protection)
- Integration with ALB/NLB

**Azure DDoS Protection**:
- Basic (free)
- Standard (paid)
- Always-on monitoring

**GCP Cloud Armor**:
- DDoS protection
- WAF rules
- Edge security policies

### WAF Integration

**AWS WAF + ALB**:
```
ALB --> WAF Rules
  |
  +-- Rate limiting
  |
  +-- IP allowlist/blocklist
  |
  +-- SQL injection protection
  |
  +-- XSS protection
  |
  +-- Geo-blocking
```

### SSL Best Practices

1. Use TLS 1.2 or higher
2. Strong cipher suites
3. Perfect Forward Secrecy
4. HSTS (HTTP Strict Transport Security)
5. Certificate rotation
6. Monitor certificate expiration

## Cost Optimization

### Cost Factors

**AWS**:
- Load Balancer hours
- Load Balancer Capacity Units (LCU)
- Data processed
- Cross-zone data transfer (NLB)

**Azure**:
- Load Balancer rules
- Data processed
- Outbound data transfer

**GCP**:
- Forwarding rules
- Ingress/egress traffic
- Premium vs Standard tier

### Optimization Strategies

1. Right-size load balancer type
2. Consolidate rules and targets
3. Use appropriate health check intervals
4. Enable cross-zone when beneficial
5. Monitor and eliminate unused resources
6. Use reserved capacity (if available)

## Troubleshooting

### Common Issues

**Unhealthy Targets**:
- Check health check configuration
- Verify security group rules
- Review application logs
- Test connectivity manually

**High Latency**:
- Check target performance
- Review connection limits
- Analyze slow requests
- Verify cross-zone settings

**Connection Timeouts**:
- Verify idle timeout settings
- Check application timeout
- Review connection limits
- Analyze network path

**SSL Certificate Errors**:
- Verify certificate validity
- Check certificate chain
- Confirm SNI configuration
- Review SSL policy

## Best Practices Summary

### Design

1. Use appropriate load balancer type
2. Deploy across availability zones
3. Implement health checks
4. Enable access logs
5. Plan for scale

### Security

1. Use SSL/TLS
2. Integrate WAF
3. Enable DDoS protection
4. Restrict security groups
5. Monitor for anomalies

### Operations

1. Monitor key metrics
2. Set up alerting
3. Regular health check reviews
4. Test failover scenarios
5. Document configuration

### Cost

1. Right-size resources
2. Monitor usage
3. Delete unused load balancers
4. Optimize data transfer
5. Use cost allocation tags

## Conclusion

Load balancing is critical for building highly available, scalable, and performant cloud applications. Choose the appropriate load balancer type, implement proper health checks, enable monitoring, and follow security best practices for production-ready deployments.
