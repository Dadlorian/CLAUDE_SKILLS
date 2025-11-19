# Multi-Region Networking Reference

## Introduction

Multi-region networking enables global application deployment with high availability, disaster recovery, and optimal user experience through geographic distribution and intelligent traffic routing.

## Multi-Region Architecture Patterns

### Active-Active

**Equal Load Distribution**:
```
Route 53 (Geolocation/Latency)
    |
    +-- us-east-1: Full Stack (Active)
    |
    +-- eu-west-1: Full Stack (Active)
    |
    +-- ap-southeast-1: Full Stack (Active)

All regions serve traffic
Data replication between regions
Highest availability
Most complex
```

**Characteristics**:
- All regions actively serving traffic
- Read and write in all regions
- Complex data synchronization
- Highest cost
- Best user experience
- No failover delay

### Active-Passive

**Primary with Standby**:
```
Route 53 (Failover)
    |
    +-- Primary: us-east-1 (Active)
    |
    +-- Secondary: us-west-2 (Standby)

Only primary serves traffic normally
Automatic failover to secondary
Lower cost than active-active
Data replication lag considerations
```

**Characteristics**:
- Single active region
- Passive regions on standby
- Automatic failover
- Data replication (async)
- Lower cost
- RTO/RPO considerations

### Active-Read Replica

**Write Primary, Read Anywhere**:
```
Route 53 (Latency-based)
    |
    +-- us-east-1: Primary (Read/Write)
    |
    +-- eu-west-1: Read Replica (Read)
    |
    +-- ap-southeast-1: Read Replica (Read)

Writes to primary only
Reads from nearest region
Global read performance
Eventual consistency
```

**Characteristics**:
- Centralized writes
- Distributed reads
- Simpler consistency model
- Cost-effective
- Good read performance

## Regional Connectivity

### VPC Peering

**Cross-Region VPC Peering**:
```
us-east-1 VPC (10.0.0.0/16)
    |
    +-- Peering Connection
    |
eu-west-1 VPC (10.1.0.0/16)

Non-transitive
Encrypted in transit
AWS global network
```

**AWS Configuration**:
```
1. Create peering connection
2. Accept in remote region
3. Update route tables:
   - us-east-1: 10.1.0.0/16 --> pcx-xxxxx
   - eu-west-1: 10.0.0.0/16 --> pcx-xxxxx
4. Update security groups
```

### AWS Transit Gateway

**Multi-Region Transit Gateway**:
```
                Transit Gateway Peering
                        |
      +-----------------+-----------------+
      |                                   |
TGW us-east-1                       TGW eu-west-1
      |                                   |
  VPC-A, VPC-B                       VPC-C, VPC-D

Inter-region routing
Centralized management
Transitive routing
```

**Benefits**:
- Simplified architecture
- Transitive routing
- Centralized management
- CloudWatch metrics
- Scalable

### Azure Virtual WAN

**Global Transit Network**:
```
Virtual WAN (Global)
    |
    +-- Hub us-east: VNets, VPN, ExpressRoute
    |
    +-- Hub eu-west: VNets, VPN, ExpressRoute
    |
    +-- Hub asia-east: VNets, VPN, ExpressRoute

Any-to-any connectivity
Microsoft global network
Integrated routing
```

**Features**:
- Hub-and-spoke at scale
- Branch connectivity
- ExpressRoute integration
- Global reach
- Routing through Azure backbone

### GCP Global VPC

**Native Global VPC**:
```
VPC (Global)
    |
    +-- Subnet us-central1 (10.0.1.0/24)
    |
    +-- Subnet europe-west1 (10.0.2.0/24)
    |
    +-- Subnet asia-east1 (10.0.3.0/24)

Single VPC spans regions
Regional subnets
Global firewall rules
Simplified architecture
```

**Benefits**:
- No VPC peering needed
- Global resources by default
- Simplified routing
- Regional subnets
- Private Google backbone

## Global Load Balancing

### AWS Global Accelerator

**Anycast IP with Health-Based Routing**:
```
Users (Global)
    |
Static Anycast IPs (2)
    |
AWS Edge Locations
    |
AWS Global Network
    |
Regional Endpoints (ALB/NLB/EC2/EIP)
    |
    +-- us-east-1
    |
    +-- us-west-2
    |
    +-- eu-west-1
```

**Features**:
- Static anycast IPs
- Automatic failover
- Continuous health monitoring
- DDoS protection (Shield)
- Up to 60% performance improvement
- Client affinity

**Traffic Dials**:
```
Traffic dial controls percentage to region:
us-east-1: 100 (full traffic)
us-west-2: 50 (50% traffic)
eu-west-1: 0 (no traffic, standby)

Use for:
- Regional traffic shaping
- Maintenance windows
- Gradual rollouts
```

### Azure Front Door

**Global HTTP Load Balancer**:
```
Users (Global)
    |
Azure Front Door (Edge POPs)
    |
Backend Pools (Multi-Region)
    |
    +-- us-east: App Service
    |
    +-- eu-west: App Service
    |
    +-- asia-east: App Service
```

**Features**:
- URL-based routing
- Session affinity
- CDN capabilities
- WAF integration
- SSL offload
- Health monitoring

**Routing Methods**:
- Latency (lowest latency)
- Priority (failover)
- Weighted (traffic distribution)
- Session affinity (sticky sessions)

### GCP Global Load Balancing

**Anycast Global Load Balancing**:
```
Users (Global)
    |
Single Anycast IP (Global)
    |
Google Edge POPs
    |
Google Private Network
    |
Backend Services (Multi-Region)
    |
    +-- us-central1: Instance Group
    |
    +-- europe-west1: Instance Group
    |
    +-- asia-east1: Instance Group
```

**Features**:
- Single global IP
- Intelligent routing
- Fast failover (seconds)
- DDoS protection (Cloud Armor)
- CDN integration
- Cross-region load balancing

## DNS-Based Global Traffic Management

### Route 53 Routing Policies

**Geolocation Routing**:
```
example.com:
- North America --> us-east-1
- Europe --> eu-west-1
- Asia --> ap-southeast-1
- Default --> us-east-1

Location-based
Content localization
Compliance
```

**Latency-Based Routing**:
```
example.com:
- us-east-1: Resource
- us-west-2: Resource
- eu-west-1: Resource

AWS measures latency
Routes to lowest latency
Best performance
```

**Geoproximity Routing**:
```
example.com:
- us-east-1 (bias: +30)
- eu-west-1 (bias: 0)
- ap-southeast-1 (bias: -20)

Geographic bias
Traffic engineering
Gradual regional shifts
```

### Azure Traffic Manager

**Profile Configuration**:
```
Priority (Failover):
Priority 1: Primary region
Priority 2: Secondary region
Priority 3: Tertiary region

Performance (Latency):
Route to lowest latency endpoint

Weighted (Distribution):
Region A: 70%
Region B: 30%
```

### Google Cloud DNS

**Routing Policies**:
```
Weighted Round Robin:
- us-central1: 50%
- europe-west1: 30%
- asia-east1: 20%

Geolocation:
- North America --> us-central1
- Europe --> europe-west1
- Asia --> asia-east1
```

## Data Replication Strategies

### Database Replication

**RDS Multi-Region** (Read Replicas):
```
Primary: us-east-1 (Write)
    |
    +-- Async Replication
    |
Read Replicas:
- us-west-2 (Read)
- eu-west-1 (Read)

Read scaling
Disaster recovery
Eventual consistency
```

**RDS Cross-Region Automated Backups**:
```
Primary: us-east-1
Automated backups copied to: us-west-2

RPO: Backup frequency
RTO: Restore time
```

**Aurora Global Database**:
```
Primary: us-east-1 (Read/Write)
    |
    +-- Physical Replication (< 1 sec lag)
    |
Secondary Regions:
- eu-west-1 (Read, can promote)
- ap-southeast-1 (Read, can promote)

RPO: < 1 second
RTO: < 1 minute
```

**Azure SQL Database**:
```
Active Geo-Replication:
Primary: East US (Read/Write)
Secondaries (up to 4):
- West US (Read/Write possible)
- North Europe (Read/Write possible)

Auto-Failover Groups:
Automatic failover
Read/write listener endpoint
Read-only listener endpoint
```

**Cloud SQL** (GCP):
```
Primary: us-central1
    |
    +-- Async Replication
    |
Read Replicas:
- us-west1
- europe-west1

Cross-region replicas
Read scaling
DR capability
```

**DynamoDB Global Tables**:
```
Multi-region, multi-active
    |
    +-- us-east-1 (Read/Write)
    |
    +-- eu-west-1 (Read/Write)
    |
    +-- ap-southeast-1 (Read/Write)

Bidirectional replication
Eventual consistency
Last-writer-wins
```

**Cosmos DB** (Azure):
```
Multi-region writes
    |
    +-- East US (Read/Write)
    |
    +-- West US (Read/Write)
    |
    +-- North Europe (Read/Write)

Tunable consistency
Multi-model
Global distribution
```

**Cloud Spanner** (GCP):
```
Multi-region configuration
    |
    +-- nam3 (us-east4, us-central1, us-west1)
    |
Strong consistency
ACID transactions
Global scale
```

### Object Storage Replication

**S3 Cross-Region Replication**:
```
Source Bucket (us-east-1)
    |
    +-- CRR Rule
    |
Destination Bucket (eu-west-1)

Automatic replication
Versioning required
IAM role based
Optional: Encryption, metrics
```

**Azure Blob Storage**:
```
Object Replication:
Source: East US
Destination: West US

Async replication
Versioning required
```

**Cloud Storage Transfer**:
```
Source: us-central1 bucket
Destination: europe-west1 bucket

Scheduled transfers
One-time or recurring
```

## Network Performance Optimization

### Edge Locations and POPs

**CloudFront Edge Locations**:
```
225+ Edge Locations Worldwide
    |
13 Regional Edge Caches
    |
Origin (S3, ALB, Custom)

Cache content globally
Reduce latency
Improve user experience
```

**Azure CDN with Front Door**:
```
118+ Edge Locations
    |
Premium Verizon / Akamai
    |
Origin (Azure or Custom)

Global content delivery
Dynamic site acceleration
```

**Cloud CDN with Cloud Load Balancing**:
```
Google Edge Network (90+ locations)
    |
Cloud CDN
    |
Backend Services

Integrated with load balancing
Anycast IPs
```

### Private Connectivity

**AWS PrivateLink Cross-Region**:
```
Service Provider (us-east-1)
    |
VPC Endpoint Service
    |
PrivateLink
    |
VPC Endpoint (eu-west-1)

Private connectivity
No internet exposure
Cross-region supported
```

**Azure Private Link**:
```
Service Provider (East US)
    |
Private Link Service
    |
Private Endpoint (West Europe)

Private connectivity
Cross-region supported
Global reach with VNet peering
```

## Disaster Recovery

### RTO and RPO

**Definitions**:
```
RTO (Recovery Time Objective):
- Maximum acceptable downtime
- Time to restore service
- Minutes to hours

RPO (Recovery Point Objective):
- Maximum acceptable data loss
- Time between last backup and failure
- Minutes to hours
```

**DR Strategies**:
```
Backup & Restore:
- RTO: Hours to days
- RPO: Hours
- Cost: Lowest

Pilot Light:
- RTO: 10 minutes to hours
- RPO: Minutes
- Cost: Low

Warm Standby:
- RTO: Minutes
- RPO: Seconds
- Cost: Medium

Active-Active:
- RTO: None (automatic)
- RPO: None
- Cost: Highest
```

### Automated Failover

**Route 53 Health Checks**:
```
Health Check Configuration:
Protocol: HTTPS
Domain: api.example.com
Path: /health
Interval: 30 seconds
Failure threshold: 3

Failover:
Primary unhealthy --> Route to secondary
Primary healthy again --> Route back
```

**Global Accelerator Failover**:
```
Health checks every 30 seconds
Unhealthy endpoint removed from rotation
Automatic failover in seconds
Client affinity maintained
```

**Azure Traffic Manager**:
```
Endpoint monitoring:
Protocol: HTTPS
Path: /health
Interval: 30 seconds
Tolerated failures: 3

Automatic endpoint marking
```

### Runbook Automation

**Failover Automation**:
```
1. Detect failure (health checks)
2. Trigger automation (Lambda, Logic Apps)
3. Promote read replica to primary
4. Update DNS records
5. Redirect traffic
6. Notify team
7. Monitor new primary
```

## Cost Optimization

### Data Transfer Costs

**Expensive**:
```
- Cross-region data transfer
- Internet egress
- Cross-AZ transfer (AWS)

Strategies:
- Minimize cross-region replication
- Use regional caching
- Compress data
- Regional processing
```

**Free/Cheap**:
```
- Ingress (into cloud)
- Same-region transfer (GCP/Azure)
- VPC peering within region
- CloudFront to origin (AWS)

Strategies:
- Keep related resources in same region
- Use CDN for content delivery
- Regional data processing
```

### Regional Resource Optimization

**Active-Passive Cost Savings**:
```
Primary Region:
- Full production environment
- Normal sizing

Secondary Region:
- Minimal standby resources
- Scaled down instances
- RDS read replicas (small)
- Auto-scaling for failover
- Start resources on demand

Save 50-70% vs active-active
```

**Reserved Capacity**:
```
Reserve capacity in primary region:
- Compute instances (1-3 years)
- Database instances
- Data transfer (CloudFront)

Up to 60% savings
```

## Monitoring and Observability

### Global Metrics

**Key Metrics**:
```
Availability:
- Uptime per region
- Health check status
- Failover events

Performance:
- Latency per region
- Response time per endpoint
- DNS resolution time

Traffic:
- Requests per region
- Traffic distribution
- Failover patterns

Replication:
- Replication lag
- Data sync status
- Conflict resolution
```

### Cross-Region Tracing

**Distributed Tracing**:
```
Request: User (EU) --> eu-west-1 --> us-east-1 DB
    |
Trace spans:
- User to edge: 20ms
- Edge to eu-west-1: 5ms
- eu-west-1 processing: 50ms
- eu-west-1 to us-east-1: 100ms
- us-east-1 DB query: 10ms
- Total: 185ms

Identify cross-region latency
Optimize data locality
```

### Alerts

**Critical Alerts**:
```
- Region failure detected
- Failover triggered
- All regions degraded
- High replication lag
- Data sync failure
```

**Warning Alerts**:
```
- Single region degraded
- Increased latency
- Elevated error rate
- Approaching quotas
```

## Best Practices

### Design

1. Plan IP address space globally (no overlaps)
2. Design for failure (multi-region from start)
3. Choose appropriate DR strategy (RTO/RPO)
4. Implement health checks and monitoring
5. Use infrastructure as code
6. Document architecture and runbooks

### Data

1. Understand consistency requirements
2. Choose appropriate replication strategy
3. Monitor replication lag
4. Test data recovery procedures
5. Implement conflict resolution
6. Consider data sovereignty

### Traffic Management

1. Use global load balancing
2. Implement intelligent routing
3. Enable automatic failover
4. Test failover regularly
5. Monitor traffic distribution
6. Plan for regional maintenance

### Cost

1. Minimize cross-region data transfer
2. Use appropriate DR strategy (not always active-active)
3. Right-size regional deployments
4. Use reserved capacity where possible
5. Monitor and optimize regularly
6. Implement regional caching

### Operations

1. Automate failover procedures
2. Regular DR testing
3. Monitor all regions continuously
4. Implement centralized logging
5. Create detailed runbooks
6. Train team on DR procedures

## Conclusion

Multi-region networking enables global scale, high availability, and disaster recovery. Choose appropriate patterns based on requirements, implement intelligent routing, ensure proper data replication, and maintain operational excellence through monitoring and testing.
