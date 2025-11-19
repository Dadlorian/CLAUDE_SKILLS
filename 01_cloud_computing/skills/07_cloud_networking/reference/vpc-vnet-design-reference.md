# VPC/VNet Design Reference

## Introduction

Virtual Private Cloud (VPC) or Virtual Network (VNet) design is foundational to cloud architecture. Proper design ensures scalability, security, and operational efficiency.

## VPC/VNet Fundamentals

### AWS VPC

**Characteristics**:
- Regional resource
- Supports IPv4 and IPv6
- Size range: /16 (65,536 IPs) to /28 (16 IPs)
- Default VPC provided per region
- Multiple VPCs per region (soft limit: 5)

**Components**:
- Subnets (AZ-specific)
- Route tables
- Internet gateway (one per VPC)
- NAT gateway (per AZ)
- Virtual private gateway (VPN)
- VPC endpoints
- Security groups (stateful)
- Network ACLs (stateless)

### Azure VNet

**Characteristics**:
- Regional resource
- Supports IPv4 and IPv6
- Size range: /8 to /29
- Multiple VNets per subscription
- Service endpoints for Azure services

**Components**:
- Subnets
- Route tables (User-Defined Routes)
- VNet gateway (VPN or ExpressRoute)
- NAT gateway
- Network Security Groups (NSG)
- Application Security Groups (ASG)
- Service endpoints
- Private endpoints

### GCP VPC

**Characteristics**:
- Global resource (unique among cloud providers)
- Subnets are regional
- Auto mode (automatic subnet creation) or custom mode
- Shared VPC for multi-project access
- VPC peering and Cloud Interconnect

**Components**:
- Subnets (regional, can span zones)
- Routes (global)
- Cloud NAT (regional)
- Cloud VPN
- Firewall rules (global)
- Private Google Access
- Shared VPC

## IP Address Planning

### CIDR Block Selection

**Best Practices**:
1. Use RFC 1918 private address space
2. Avoid conflicts with on-premises networks
3. Plan for growth (use larger CIDR blocks)
4. Reserve IP ranges for future use
5. Document IP allocation

**Common VPC CIDR Blocks**:

```
Production:    10.0.0.0/16   (65,536 addresses)
Development:   10.1.0.0/16   (65,536 addresses)
Staging:       10.2.0.0/16   (65,536 addresses)
Testing:       10.3.0.0/16   (65,536 addresses)
```

**Subnet Sizing**:

```
/24 = 256 addresses (251 usable)
/25 = 128 addresses
/26 = 64 addresses
/27 = 32 addresses
/28 = 16 addresses (11 usable in AWS)
```

**Reserved IPs (AWS Example)**:
- `.0`: Network address
- `.1`: VPC router
- `.2`: DNS server
- `.3`: Reserved for future use
- `.255`: Broadcast (not used but reserved)

### Multi-Tier Subnet Design

**Three-Tier Architecture**:

```
VPC: 10.0.0.0/16

Public Tier (DMZ):
  - us-east-1a: 10.0.1.0/24
  - us-east-1b: 10.0.2.0/24
  - us-east-1c: 10.0.3.0/24

Private Tier (Application):
  - us-east-1a: 10.0.11.0/24
  - us-east-1b: 10.0.12.0/24
  - us-east-1c: 10.0.13.0/24

Database Tier:
  - us-east-1a: 10.0.21.0/24
  - us-east-1b: 10.0.22.0/24
  - us-east-1c: 10.0.23.0/24

Management/Operations:
  - us-east-1a: 10.0.31.0/24
  - us-east-1b: 10.0.32.0/24
```

### Variable-Length Subnet Masking (VLSM)

**Efficient IP Allocation**:

```
Large subnets (applications): /24 (256 IPs)
Medium subnets (services):    /26 (64 IPs)
Small subnets (management):   /28 (16 IPs)
```

**Example**:

```
10.0.0.0/16 VPC
  10.0.0.0/24   - Public subnet AZ-1 (256)
  10.0.1.0/24   - Public subnet AZ-2 (256)
  10.0.10.0/23  - App subnet AZ-1 (512)
  10.0.12.0/23  - App subnet AZ-2 (512)
  10.0.20.0/26  - DB subnet AZ-1 (64)
  10.0.20.64/26 - DB subnet AZ-2 (64)
  10.0.30.0/28  - Mgmt subnet (16)
```

## Subnet Types and Patterns

### Public Subnets

**Characteristics**:
- Route to internet gateway
- Public IP addresses
- Hosts web servers, load balancers, bastion hosts

**Route Table**:
```
Destination      Target
10.0.0.0/16      local
0.0.0.0/0        igw-xxxxx
```

### Private Subnets

**Characteristics**:
- No direct internet access
- Outbound via NAT gateway
- Application servers, databases

**Route Table**:
```
Destination      Target
10.0.0.0/16      local
0.0.0.0/0        nat-xxxxx
```

### Isolated Subnets

**Characteristics**:
- No internet access
- Databases, sensitive data
- VPC endpoints for AWS/Azure services

**Route Table**:
```
Destination      Target
10.0.0.0/16      local
(no default route)
```

### Transit Subnets

**Characteristics**:
- Dedicated to network appliances
- Firewalls, IDS/IPS, VPN endpoints
- Transit gateway attachments

## Availability Zone Strategies

### High Availability Design

**Multi-AZ Deployment**:

```
Region: us-east-1

AZ-1 (us-east-1a):
  - Public:  10.0.1.0/24
  - Private: 10.0.11.0/24
  - Data:    10.0.21.0/24

AZ-2 (us-east-1b):
  - Public:  10.0.2.0/24
  - Private: 10.0.12.0/24
  - Data:    10.0.22.0/24

AZ-3 (us-east-1c):
  - Public:  10.0.3.0/24
  - Private: 10.0.13.0/24
  - Data:    10.0.23.0/24
```

**Benefits**:
- Fault tolerance
- High availability
- No single point of failure
- Load distribution

### Subnet Allocation Per AZ

**Consistent Pattern**:

```
First octet: Region identifier
Second octet: Environment
Third octet: AZ and tier
  0-9:   AZ-1
  10-19: AZ-2
  20-29: AZ-3

  x1-x3: Public
  x4-x6: Private/App
  x7-x9: Database
```

## VPC Connectivity Patterns

### VPC Peering

**Use Cases**:
- Connect VPCs within same region
- Share resources between accounts
- Microservices architectures

**Characteristics**:
- Non-transitive (no daisy-chaining)
- No overlapping CIDR blocks
- Cross-region peering supported (AWS, Azure)
- No single point of failure
- Low latency, high bandwidth

**Design Considerations**:
```
VPC-A (10.0.0.0/16) <--Peering--> VPC-B (10.1.0.0/16)
VPC-B (10.1.0.0/16) <--Peering--> VPC-C (10.2.0.0/16)

VPC-A cannot reach VPC-C without direct peering
```

### Transit Gateway (AWS)

**Use Cases**:
- Hub-and-spoke architecture
- Centralized connectivity
- Shared services VPC
- Complex network topologies

**Characteristics**:
- Transitive routing
- Supports VPN and Direct Connect
- Inter-region peering
- Route table isolation
- Multicast support

**Architecture**:
```
              Transit Gateway
                    |
        +-----------+-----------+
        |           |           |
     VPC-Prod   VPC-Dev   VPC-Shared
```

### Virtual WAN (Azure)

**Use Cases**:
- Global transit network
- Branch office connectivity
- Hub-and-spoke at scale

**Characteristics**:
- Global Microsoft network
- Integrated VPN and ExpressRoute
- Routing through Azure backbone
- Any-to-any connectivity

### Shared VPC (GCP)

**Use Cases**:
- Multi-project organizations
- Centralized network management
- Shared networking resources

**Characteristics**:
- Host project owns VPC
- Service projects use subnets
- Centralized security policies
- Simplified IPAM

## Security Design Patterns

### Network Segmentation

**Tier-Based Segmentation**:

```
Internet Tier (Public):
  - Load balancers
  - NAT gateways
  - Bastion hosts

Application Tier (Private):
  - Application servers
  - Container workloads
  - API services

Data Tier (Isolated):
  - Databases
  - Data warehouses
  - Cache clusters
```

**Environment Segmentation**:
```
Production VPC:   10.0.0.0/16
Staging VPC:      10.1.0.0/16
Development VPC:  10.2.0.0/16
Testing VPC:      10.3.0.0/16
```

### Defense in Depth

**Layered Security**:

1. **Edge Protection**: CloudFront, WAF, DDoS protection
2. **Network Perimeter**: Internet gateway, security groups
3. **Subnet Level**: Network ACLs
4. **Instance Level**: Host firewalls, security groups
5. **Application Level**: Application authentication/authorization

### Micro-Segmentation

**Fine-Grained Control**:

```
Application: E-commerce
  - Web tier security group
  - API tier security group
  - Database tier security group
  - Cache tier security group
  - Queue tier security group

Each with specific ingress/egress rules
```

## Scalability Patterns

### Horizontal Scaling

**Auto Scaling Groups**:
```
Load Balancer
    |
Auto Scaling Group (2-20 instances)
    |
Multiple Subnets (Multi-AZ)
```

### Vertical Scaling

**Instance Sizing**:
- Start with appropriate instance types
- Monitor and adjust based on metrics
- Use burstable instances for variable workloads

### Geographic Scaling

**Multi-Region Architecture**:

```
Region 1 (us-east-1):
  VPC: 10.0.0.0/16

Region 2 (us-west-2):
  VPC: 10.10.0.0/16

Region 3 (eu-west-1):
  VPC: 10.20.0.0/16

Global Load Balancer / Route 53
```

## Advanced VPC Features

### VPC Endpoints (AWS)

**Interface Endpoints**:
- Private access to AWS services
- Powered by PrivateLink
- Elastic network interface with private IP

**Gateway Endpoints**:
- S3 and DynamoDB
- Route table entry
- No data transfer charges

### Azure Private Link

**Characteristics**:
- Private access to Azure services
- Private access to customer services
- No internet exposure
- Global reach

### GCP Private Google Access

**Characteristics**:
- Access Google services from private IPs
- No external IPs needed
- Restricted to Google APIs
- Regional configuration

## DNS Architecture

### DNS Resolution Patterns

**AWS Route 53 Private Hosted Zones**:
```
VPC DNS: 10.0.0.2
Private Zone: internal.example.com
```

**Azure Private DNS Zones**:
```
Private DNS Zone: internal.azure.net
VNet link for resolution
```

**GCP Cloud DNS Private Zones**:
```
Private zone: internal.example.com
VPC network association
```

### Hybrid DNS

**Split-Horizon DNS**:
- Different responses for internal vs external queries
- Private zone for VPC resources
- Public zone for internet-facing resources

## Best Practices

### Design Principles

1. **Plan IP space carefully**: Avoid future conflicts
2. **Use consistent naming**: Document and standardize
3. **Implement least privilege**: Restrict access by default
4. **Deploy across AZs**: Ensure high availability
5. **Segment by tier and environment**: Isolation and security
6. **Use infrastructure as code**: Terraform, CloudFormation
7. **Document architecture**: Network diagrams and runbooks

### Security

1. Enable VPC flow logs
2. Use private subnets for non-public resources
3. Implement security groups with least privilege
4. Use network ACLs as additional layer
5. Enable encryption in transit
6. Use VPC endpoints to avoid internet traversal
7. Regular security audits

### Operations

1. Tag all resources consistently
2. Monitor network metrics
3. Implement centralized logging
4. Create network inventory
5. Automate network provisioning
6. Test disaster recovery procedures
7. Document runbooks

### Cost Optimization

1. Use single NAT gateway per AZ (if affordable)
2. Leverage VPC endpoints for AWS services
3. Minimize data transfer costs
4. Right-size network resources
5. Delete unused resources

## Common Anti-Patterns

### Avoid

1. **Overlapping CIDR blocks**: Prevents peering
2. **Single AZ deployment**: No high availability
3. **Too small CIDR**: Can't scale
4. **Default security groups allowing all traffic**: Security risk
5. **No flow logs**: Blind to network issues
6. **Manual network changes**: Configuration drift
7. **Overly complex routing**: Hard to troubleshoot

## VPC Design Checklist

- [ ] IP address plan documented
- [ ] CIDR blocks don't overlap with other networks
- [ ] Multi-AZ deployment for high availability
- [ ] Public and private subnets defined
- [ ] Security groups configured with least privilege
- [ ] Network ACLs configured
- [ ] NAT gateways for private subnet internet access
- [ ] VPC flow logs enabled
- [ ] VPC endpoints for cloud services
- [ ] Route tables configured correctly
- [ ] DNS resolution configured
- [ ] Monitoring and alerting set up
- [ ] Infrastructure as code implemented
- [ ] Documentation complete
- [ ] Security review completed
- [ ] Cost optimization reviewed

## Conclusion

Proper VPC/VNet design is critical for secure, scalable, and efficient cloud infrastructure. Follow established patterns, implement security best practices, and always plan for growth and change.
