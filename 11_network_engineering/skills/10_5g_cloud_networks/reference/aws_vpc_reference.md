# AWS VPC Reference

## Amazon Virtual Private Cloud (VPC) Overview

AWS VPC provides isolated cloud computing resources with complete control over network configuration including IP address space, subnets, routing, and security.

## VPC Architecture Components

### VPC Fundamentals
- **CIDR Block** - Primary IP address range (e.g., 10.0.0.0/16)
- **Secondary CIDR** - Additional IP ranges for expansion
- **Region-specific** - Exists within single AWS region
- **Multiple AZ support** - Subnets span availability zones

### Subnets
- **Public Subnet** - Routes through Internet Gateway
- **Private Subnet** - No direct internet access
- **Default Route Table** - Defines routing behavior
- **Route Propagation** - BGP propagation for VPN/VGW

### Internet Connectivity

#### Internet Gateway (IGW)
- Allows EC2 instances to access internet
- Provides NAT for public addresses
- Stateless, highly available
- No bandwidth constraints

#### NAT Gateway/Instance
- Enables outbound internet for private instances
- One-way translation (private to public)
- Elastic IP association
- Per-AZ deployment

#### VPN Gateway (VGW)
- Site-to-Site VPN connectivity
- IPSec termination
- Dynamic routing via BGP
- HA across multiple tunnels

### Network Segmentation

#### Security Groups
- **Stateful firewall** - Return traffic allowed
- **Inbound rules** - Source IP, protocol, port
- **Outbound rules** - Default allow all
- **Instance-level** - Applied directly to ENI

#### Network ACLs (NACLs)
- **Stateless firewall** - Both directions required
- **Subnet-level** - Applied to all traffic
- **Ordered rules** - First match wins
- **Implicit deny** - Rules before implicit deny

### Network Interfaces

#### Elastic Network Interface (ENI)
- Primary ENI (eth0) - Cannot detach
- Secondary ENI - Can attach/detach
- Multiple private IPs per ENI
- Security group assignment

#### Elastic IP (EIP)
- Static public IPv4 address
- Persists when instance stops
- Remappable across instances
- Associated with AWS account

## VPC Communication

### Intra-VPC Communication
- Direct routing via longest prefix match
- No internet gateway required
- Automatic ARP resolution
- Layer 2 domain per subnet

### Inter-VPC Communication

#### VPC Peering
- **Direct connection** between VPCs
- **Non-transitive** - No transitive peering
- **Same/different region** - Supported
- **Non-overlapping CIDR** - Required

#### AWS Transit Gateway
- **Hub-and-spoke** topology
- **Transitive routing** - Peering through TGW
- **Route tables** - Per-attachment routing
- **Scalable** - Thousands of attachments

#### PrivateLink
- **Service exposure** - VPC endpoint service
- **Consumer access** - VPC endpoint
- **Privateconnections** - No internet exposure
- **Cross-account** - Supported

### External Connectivity

#### Direct Connect
- **Dedicated physical connection** to AWS
- **Predictable network performance**
- **Lower latency** vs internet
- **Consistent bandwidth** - No internet contention

#### Site-to-Site VPN
- **IPSec encryption** - Secure connection
- **Dynamic routing** - BGP support
- **Redundant tunnels** - HA built-in
- **Quick provisioning** - Minutes to setup

## Routing

### Route Tables
- **Main route table** - Default for VPC
- **Custom route tables** - Subnet-specific routing
- **Route priority** - Longest prefix match
- **Blackhole routes** - Drops traffic to CIDR

### Route Types
- **Local routes** - VPC CIDR (automatic)
- **IGW routes** - Internet traffic
- **NAT routes** - Private subnet internet
- **VPN routes** - On-premises access
- **TGW routes** - Inter-VPC/VPN traffic
- **VPC endpoint routes** - AWS services

## AWS Services Integration

### VPC Endpoints

#### Gateway Endpoints
- **S3 and DynamoDB** access without NAT
- **No additional charge** - Included
- **Route table entries** - Automatic

#### Interface Endpoints
- **ENI-based** access to services
- **Security groups** applied
- **PrivateLink** technology
- **Cross-account** capable

### Elastic Load Balancing
- **Application Load Balancer (ALB)** - Layer 7
- **Network Load Balancer (NLB)** - Layer 4
- **Cross-zone** enabled for HA
- **Target group** routing

### RDS/ElastiCache
- **DB Subnet Groups** - Multi-AZ deployment
- **Parameter group** for DB config
- **Enhanced monitoring** within VPC
- **Backup retention** across AZs

## VPC Flow Logs

### Log Types
- **Accept logs** - Permitted traffic
- **Reject logs** - Denied traffic
- **All traffic** - Combined logs

### Log Fields
```
version account-id interface-id srcaddr dstaddr
srcport dstport protocol packets bytes
start end action log-status
```

### Delivery Methods
- **CloudWatch Logs** - Detailed query capability
- **S3** - Long-term storage
- **Kinesis Data Firehose** - Real-time processing

## VPC Peering vs Transit Gateway

| Aspect | Peering | Transit Gateway |
|--------|---------|-----------------|
| Connectivity | Point-to-point | Hub-and-spoke |
| Transitivity | Non-transitive | Transitive |
| Scalability | Limited | Thousands |
| Complex routing | No | Yes |
| Route tables | Per-VPC | Attachment-specific |

## Security Best Practices

### Network Design
- **Public/Private separation** - Tier 1/3
- **Multi-AZ deployment** - High availability
- **Centralized logging** - VPC Flow Logs
- **Least privilege** - Minimal rules

### Access Control
- **Security group defaults** - Deny all inbound
- **NACL deny rules** - Implicit deny
- **Source/destination check** - Enabled by default
- **Bastion hosts** - Jump server pattern

### Encryption
- **EBS encryption** - Default enabled
- **S3 encryption** - Server/client side
- **Secrets Manager** - Credential storage
- **KMS keys** - Encryption key management

## Performance Optimization

### Network Performance
- **Placement groups** - Low-latency instances
- **Enhanced networking** - ENA/SR-IOV
- **EBS optimization** - Dedicated throughput
- **Route optimization** - Least-hop routing

### Cost Optimization
- **Data transfer costs** - Monitor egress
- **NAT Gateway costs** - Consider NAT instances
- **VPN costs** - Optimize tunnel usage
- **Reserved bandwidth** - Volume discounts

## Multi-Region VPC Architecture

### Global Connectivity
- **Region-to-region Transit Gateway peering**
- **Route propagation** across regions
- **DR scenarios** - Failover routing
- **Data residency** - Region constraint

### Disaster Recovery
- **RTO/RPO targets** - Define objectives
- **Backup VPCs** - Standby regions
- **Route failover** - Dynamic rerouting
- **Cross-region replication** - Data sync

---

**Reference:** AWS VPC Documentation
**Last Updated:** 2025-11-19
