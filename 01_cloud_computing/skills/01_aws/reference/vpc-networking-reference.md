# VPC Networking Reference

## VPC Fundamentals

### CIDR Block Planning

**IPv4 CIDR Ranges (RFC 1918):**
- 10.0.0.0/8 (10.0.0.0 - 10.255.255.255) - 16,777,216 addresses
- 172.16.0.0/12 (172.16.0.0 - 172.31.255.255) - 1,048,576 addresses
- 192.168.0.0/16 (192.168.0.0 - 192.168.255.255) - 65,536 addresses

**AWS VPC CIDR Constraints:**
- Minimum size: /28 (16 IP addresses)
- Maximum size: /16 (65,536 IP addresses)
- Can add up to 5 CIDR blocks per VPC
- Cannot overlap with existing peered VPCs

**Reserved IPs Per Subnet:**
```
Example: 10.0.1.0/24 (256 addresses)
- 10.0.1.0: Network address
- 10.0.1.1: VPC router
- 10.0.1.2: DNS server (Route 53 Resolver)
- 10.0.1.3: Future use
- 10.0.1.255: Broadcast (not supported but reserved)

Usable IPs: 256 - 5 = 251 addresses
```

### Sample CIDR Plans

**Small Organization (10.0.0.0/16):**
```
VPC: 10.0.0.0/16

Availability Zone 1:
  Public Subnet:  10.0.0.0/24  (251 usable IPs)
  Private Subnet: 10.0.1.0/24  (251 usable IPs)
  Database Subnet: 10.0.2.0/24 (251 usable IPs)

Availability Zone 2:
  Public Subnet:  10.0.10.0/24 (251 usable IPs)
  Private Subnet: 10.0.11.0/24 (251 usable IPs)
  Database Subnet: 10.0.12.0/24 (251 usable IPs)

Availability Zone 3:
  Public Subnet:  10.0.20.0/24 (251 usable IPs)
  Private Subnet: 10.0.21.0/24 (251 usable IPs)
  Database Subnet: 10.0.22.0/24 (251 usable IPs)

Reserved for future: 10.0.100.0/22, 10.0.200.0/22, etc.
```

**Large Organization (Multi-VPC Strategy):**
```
Production VPC:    10.0.0.0/16
Staging VPC:       10.1.0.0/16
Development VPC:   10.2.0.0/16
Shared Services:   10.10.0.0/16
DR Region:         10.100.0.0/16
```

## Subnet Design Patterns

### Public Subnet
Instances with public IPs, accessible from internet.

**Components:**
- Internet Gateway (IGW) attached to VPC
- Route table with route to IGW (0.0.0.0/0 → IGW)
- Public IP or Elastic IP assigned to instances
- Security groups allowing inbound internet traffic

```python
import boto3

ec2 = boto3.client('ec2')

# Create public subnet
subnet = ec2.create_subnet(
    VpcId='vpc-12345',
    CidrBlock='10.0.1.0/24',
    AvailabilityZone='us-east-1a'
)

# Enable auto-assign public IP
ec2.modify_subnet_attribute(
    SubnetId=subnet['Subnet']['SubnetId'],
    MapPublicIpOnLaunch={'Value': True}
)

# Associate with public route table
ec2.associate_route_table(
    SubnetId=subnet['Subnet']['SubnetId'],
    RouteTableId='rtb-public-12345'
)
```

### Private Subnet
Instances without public IPs, outbound internet via NAT.

**Components:**
- NAT Gateway or NAT Instance in public subnet
- Route table with route to NAT (0.0.0.0/0 → NAT Gateway)
- No public IPs on instances
- Outbound internet access, no inbound from internet

### Isolated Subnet (Database Tier)
No internet access, fully isolated.

**Components:**
- No routes to Internet Gateway or NAT Gateway
- Only internal VPC communication
- VPC Endpoints for AWS services
- Highest security for sensitive data

## Route Tables

### Default Route Table
Created automatically with VPC, contains only local route.

```
Destination     Target
10.0.0.0/16     local
```

### Custom Route Tables

**Public Route Table:**
```
Destination     Target              Description
10.0.0.0/16     local               VPC internal routing
0.0.0.0/0       igw-12345           Internet via IGW
```

**Private Route Table:**
```
Destination     Target              Description
10.0.0.0/16     local               VPC internal routing
0.0.0.0/0       nat-12345           Internet via NAT Gateway
10.1.0.0/16     pcx-12345           Peer VPC routing
pl-12345        vpce-12345          S3 via VPC Endpoint
```

**Database Route Table:**
```
Destination     Target              Description
10.0.0.0/16     local               VPC internal routing only
pl-12345        vpce-12345          S3 via VPC Endpoint (optional)
```

### Route Priority
Most specific route wins (longest prefix match).

```
Routes:
10.0.0.0/16     → local
10.0.1.0/24     → tgw-12345
10.0.1.50/32    → eni-12345

Traffic to 10.0.1.50 → uses /32 route (most specific)
Traffic to 10.0.1.100 → uses /24 route
Traffic to 10.0.2.50 → uses /16 route
```

## Internet Connectivity

### Internet Gateway (IGW)
- Horizontally scaled, redundant, highly available
- No bandwidth constraints
- Performs NAT for instances with public IPs
- One IGW per VPC
- Free (no hourly charge, only data transfer costs)

### NAT Gateway
**Characteristics:**
- Managed NAT service
- Scales automatically up to 100 Gbps
- Deployed in specific AZ (create one per AZ for HA)
- Requires Elastic IP
- Charged per hour + per GB processed

**Pricing (us-east-1):**
```
Hourly charge: $0.045/hour (~$32.40/month)
Data processing: $0.045/GB

Example monthly cost (1 TB outbound):
- NAT Gateway hours: $32.40
- Data processing: 1024 GB × $0.045 = $46.08
- Total: $78.48
```

**High Availability Setup:**
```python
# Create NAT Gateway in each AZ
for az in ['us-east-1a', 'us-east-1b', 'us-east-1c']:
    # Allocate Elastic IP
    eip = ec2.allocate_address(Domain='vpc')

    # Create NAT Gateway in public subnet
    nat_gw = ec2.create_nat_gateway(
        SubnetId=public_subnet_ids[az],
        AllocationId=eip['AllocationId']
    )

    # Update private route table for this AZ
    ec2.create_route(
        RouteTableId=private_route_tables[az],
        DestinationCidrBlock='0.0.0.0/0',
        NatGatewayId=nat_gw['NatGateway']['NatGatewayId']
    )
```

### NAT Instance (Legacy, Not Recommended)
- EC2 instance performing NAT
- Manual scaling and management
- Single point of failure (requires HA setup)
- Lower cost but higher operational overhead
- Use NAT Gateway instead for production

### Egress-Only Internet Gateway
- For IPv6 only
- Allows outbound IPv6 traffic
- Blocks inbound IPv6 traffic
- Free, no bandwidth limits

## Security

### Security Groups (Stateful)

**Characteristics:**
- Stateful (return traffic automatically allowed)
- Applied at ENI level
- Only ALLOW rules (no DENY)
- Evaluated as a whole (all rules apply)
- Default: Deny all inbound, allow all outbound
- Can reference other security groups

**Example Security Group Rules:**
```python
# Web server security group
web_sg = ec2.create_security_group(
    GroupName='web-servers',
    Description='Security group for web servers',
    VpcId='vpc-12345'
)

# Allow HTTP from anywhere
ec2.authorize_security_group_ingress(
    GroupId=web_sg['GroupId'],
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 443,
            'ToPort': 443,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        # SSH from bastion security group
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'UserIdGroupPairs': [{'GroupId': 'sg-bastion-12345'}]
        }
    ]
)
```

### Network ACLs (Stateless)

**Characteristics:**
- Stateless (return traffic must be explicitly allowed)
- Applied at subnet level
- ALLOW and DENY rules
- Rules processed in number order
- Default: Allow all inbound and outbound
- Cannot reference security groups

**Example NACL:**
```
Inbound Rules:
Rule #  Type      Protocol  Port Range  Source        Allow/Deny
100     HTTP      TCP       80          0.0.0.0/0     ALLOW
110     HTTPS     TCP       443         0.0.0.0/0     ALLOW
120     SSH       TCP       22          10.0.0.0/16   ALLOW
130     Ephemeral TCP       1024-65535  0.0.0.0/0     ALLOW
*       All       All       All         0.0.0.0/0     DENY

Outbound Rules:
Rule #  Type      Protocol  Port Range  Destination   Allow/Deny
100     HTTP      TCP       80          0.0.0.0/0     ALLOW
110     HTTPS     TCP       443         0.0.0.0/0     ALLOW
120     Ephemeral TCP       1024-65535  0.0.0.0/0     ALLOW
*       All       All       All         0.0.0.0/0     DENY
```

**Ephemeral Ports:**
```
Different operating systems use different ranges:
- Linux: 32768-61000
- Windows Server: 49152-65535
- NAT Gateway: 1024-65535

Recommendation: Allow 1024-65535 for maximum compatibility
```

### Security Groups vs NACLs

| Feature | Security Groups | Network ACLs |
|---------|----------------|--------------|
| State | Stateful | Stateless |
| Level | Instance (ENI) | Subnet |
| Rules | ALLOW only | ALLOW and DENY |
| Rule processing | All rules | Number order |
| References | Can reference SGs | IP ranges only |
| Default | Deny inbound | Allow all |

## VPC Peering

### Characteristics
- Private connectivity between VPCs
- No internet gateway, VPN, or separate hardware
- No single point of failure
- No bandwidth bottleneck
- Can peer across regions and accounts
- Non-transitive (A↔B, B↔C does not mean A↔C)
- CIDR blocks must not overlap

### Setup
```python
# Create peering connection
pcx = ec2.create_vpc_peering_connection(
    VpcId='vpc-source-12345',
    PeerVpcId='vpc-target-67890',
    PeerOwnerId='123456789012',
    PeerRegion='us-west-2'
)

# Accept peering connection (in peer account/region)
ec2_peer = boto3.client('ec2', region_name='us-west-2')
ec2_peer.accept_vpc_peering_connection(
    VpcPeeringConnectionId=pcx['VpcPeeringConnection']['VpcPeeringConnectionId']
)

# Add routes in both VPCs
ec2.create_route(
    RouteTableId='rtb-source-12345',
    DestinationCidrBlock='10.1.0.0/16',  # Peer VPC CIDR
    VpcPeeringConnectionId=pcx['VpcPeeringConnection']['VpcPeeringConnectionId']
)
```

### Peering Limitations
- Maximum 125 peering connections per VPC
- Cannot have overlapping CIDR blocks
- No transitive peering
- No edge-to-edge routing (on-premises via VPN)

## AWS Transit Gateway

### Architecture
Hub-and-spoke model for VPC connectivity.

```
        [Transit Gateway]
        /     |     |    \
    VPC-A  VPC-B VPC-C  VPN
```

### Benefits
- Centralized connectivity hub
- Transitive routing (VPC-A ↔ VPC-B via TGW)
- Connect thousands of VPCs
- On-premises integration (VPN, Direct Connect)
- Multi-region with Transit Gateway peering
- Simplified network topology

### Features
- Up to 5,000 VPC attachments
- Up to 50 Gbps per VPC attachment
- Multi-cast support
- Route tables for traffic segmentation
- Network Manager for monitoring

### Pricing
```
Attachment fee: $0.05/hour per attachment (~$36/month)
Data processing: $0.02/GB

Example (100 VPCs, 10 TB/month):
- Attachments: 100 × $36 = $3,600/month
- Data processing: 10,240 GB × $0.02 = $204.80/month
- Total: $3,804.80/month
```

## VPC Endpoints

### Interface Endpoints (PrivateLink)

**Characteristics:**
- Elastic Network Interface (ENI) in your subnet
- Private IP from subnet range
- Requires security group
- Charged per hour + per GB
- Supports most AWS services

**Pricing:**
```
Hourly charge: $0.01/hour per AZ (~$7.20/month per AZ)
Data processing: $0.01/GB

Example (3 AZs, 1 TB/month):
- Endpoint hours: 3 × $7.20 = $21.60/month
- Data processing: 1024 GB × $0.01 = $10.24/month
- Total: $31.84/month
```

**Setup:**
```python
# Create interface endpoint for EC2
endpoint = ec2.create_vpc_endpoint(
    VpcId='vpc-12345',
    ServiceName='com.amazonaws.us-east-1.ec2',
    VpcEndpointType='Interface',
    SubnetIds=['subnet-1', 'subnet-2', 'subnet-3'],
    SecurityGroupIds=['sg-12345'],
    PrivateDnsEnabled=True
)
```

### Gateway Endpoints

**Characteristics:**
- Route table target (not ENI)
- Free (no hourly or data charges)
- Only supports S3 and DynamoDB
- Cannot access across VPN or Direct Connect
- Must be in same region

**Setup:**
```python
# Create gateway endpoint for S3
endpoint = ec2.create_vpc_endpoint(
    VpcId='vpc-12345',
    ServiceName='com.amazonaws.us-east-1.s3',
    VpcEndpointType='Gateway',
    RouteTableIds=['rtb-private-1', 'rtb-private-2']
)
```

**Endpoint Policies:**
```json
{
  "Statement": [{
    "Effect": "Allow",
    "Principal": "*",
    "Action": [
      "s3:GetObject",
      "s3:PutObject"
    ],
    "Resource": "arn:aws:s3:::my-bucket/*"
  }]
}
```

## AWS PrivateLink

### Consumer-Provider Model
- Service provider exposes service via NLB
- Service consumer creates interface endpoint
- Private connectivity without internet/NAT/peering
- Scalable to thousands of VPCs

### Setup
```python
# Provider: Create VPC Endpoint Service
vpce_config = ec2.create_vpc_endpoint_service_configuration(
    NetworkLoadBalancerArns=['arn:aws:elasticloadbalancing:...'],
    AcceptanceRequired=True
)

# Consumer: Create VPC Endpoint
endpoint = ec2.create_vpc_endpoint(
    VpcId='vpc-consumer-12345',
    ServiceName='com.amazonaws.vpce.us-east-1.vpce-svc-12345',
    VpcEndpointType='Interface',
    SubnetIds=['subnet-1', 'subnet-2'],
    SecurityGroupIds=['sg-12345']
)

# Provider: Accept connection request
ec2.accept_vpc_endpoint_connections(
    ServiceId='vpce-svc-12345',
    VpcEndpointIds=[endpoint['VpcEndpoint']['VpcEndpointId']]
)
```

## VPC Flow Logs

### Characteristics
- Capture IP traffic metadata
- Published to CloudWatch Logs or S3
- Can be created at VPC, subnet, or ENI level
- Does not capture all traffic (DHCP, DNS, metadata, etc.)

### Log Format
```
version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes start end action log-status

Example:
2 123456789012 eni-1a2b3c4d 172.31.16.139 172.31.16.21 20641 22 6 20 4249 1418530010 1418530070 ACCEPT OK
```

### Setup
```python
# Create flow log to CloudWatch
flow_log = ec2.create_flow_logs(
    ResourceIds=['vpc-12345'],
    ResourceType='VPC',
    TrafficType='ALL',  # ACCEPT, REJECT, or ALL
    LogDestinationType='cloud-watch-logs',
    LogGroupName='/aws/vpc/flowlogs',
    DeliverLogsPermissionArn='arn:aws:iam::123456789012:role/flowlogsRole'
)

# Create flow log to S3
flow_log = ec2.create_flow_logs(
    ResourceIds=['vpc-12345'],
    ResourceType='VPC',
    TrafficType='ALL',
    LogDestinationType='s3',
    LogDestination='arn:aws:s3:::my-flow-logs-bucket/prefix/'
)
```

### Analysis with CloudWatch Insights
```sql
-- Top talkers by bytes
fields @timestamp, srcaddr, dstaddr, bytes
| filter action = "ACCEPT"
| stats sum(bytes) as totalbytes by srcaddr, dstaddr
| sort totalbytes desc
| limit 20

-- Rejected connections
fields @timestamp, srcaddr, dstaddr, srcport, dstport
| filter action = "REJECT"
| limit 100
```

## Direct Connect

### Features
- Dedicated 1 Gbps, 10 Gbps, or 100 Gbps connection
- Consistent network performance
- Lower data transfer costs than internet
- Private connectivity to VPCs (via Virtual Private Gateway)
- Public connectivity to AWS services
- LAG (Link Aggregation Groups) for redundancy

### Virtual Interfaces (VIF)
1. **Private VIF**: Connect to VPC via VGW
2. **Public VIF**: Connect to public AWS services (S3, DynamoDB)
3. **Transit VIF**: Connect to Transit Gateway

### High Availability
```
On-Premises
    ├── DX Location 1 → Private VIF → VGW → VPC
    └── DX Location 2 → Private VIF → VGW → VPC
    └── VPN Connection → VGW → VPC (backup)
```

## DNS Resolution

### Route 53 Resolver
- DNS server at VPC CIDR base + 2 (e.g., 10.0.0.2)
- Automatic for AWS service endpoints
- Resolves public and private DNS names

### Private Hosted Zones
```python
route53 = boto3.client('route53')

# Create private hosted zone
zone = route53.create_hosted_zone(
    Name='internal.mycompany.com',
    VPC={'VPCRegion': 'us-east-1', 'VPCId': 'vpc-12345'},
    CallerReference=str(time.time())
)

# Create record
route53.change_resource_record_sets(
    HostedZoneId=zone['HostedZone']['Id'],
    ChangeBatch={
        'Changes': [{
            'Action': 'CREATE',
            'ResourceRecordSet': {
                'Name': 'db.internal.mycompany.com',
                'Type': 'A',
                'TTL': 300,
                'ResourceRecords': [{'Value': '10.0.1.50'}]
            }
        }]
    }
)
```

### Route 53 Resolver Endpoints
- Inbound Endpoint: On-premises queries AWS resources
- Outbound Endpoint: AWS queries on-premises resources
- Supports hybrid cloud DNS

## Best Practices

1. **CIDR Planning**: Plan for growth, avoid overlaps
2. **Multi-AZ**: Deploy across at least 3 AZs for HA
3. **NAT Gateways**: One per AZ for high availability
4. **Security Layers**: Security Groups + NACLs + flow logs
5. **VPC Endpoints**: Use for AWS services to save costs
6. **Transit Gateway**: For complex multi-VPC topologies
7. **Monitoring**: Enable VPC Flow Logs, CloudWatch metrics
8. **Tagging**: Consistent tagging for cost allocation
9. **Least Privilege**: Restrictive security group rules
10. **Documentation**: Maintain network diagrams and CIDR inventory

This comprehensive reference covers VPC networking for building secure, scalable AWS network architectures.
