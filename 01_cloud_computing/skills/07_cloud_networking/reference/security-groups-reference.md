# Security Groups and Network ACLs Reference

## Introduction

Security groups and network ACLs (Access Control Lists) provide network-level security for cloud resources. Understanding their differences, capabilities, and best practices is essential for building secure cloud architectures.

## Security Groups vs Network ACLs

### Comparison Table

| Feature | Security Groups | Network ACLs |
|---------|----------------|--------------|
| Level | Instance/ENI | Subnet |
| State | Stateful | Stateless |
| Rules | Allow only | Allow and Deny |
| Rule Processing | All rules evaluated | Rules in order |
| Association | Multiple per instance | One per subnet |
| Default | Deny all inbound | Allow all |
| Return Traffic | Automatic | Must be explicitly allowed |

### Stateful vs Stateless

**Security Groups (Stateful)**:
```
Inbound rule: Allow port 80
Outbound: Automatically allowed (return traffic)

Connection tracked
No need for explicit outbound rule
```

**Network ACLs (Stateless)**:
```
Inbound rule: Allow port 80
Outbound rule: Must allow ephemeral ports (1024-65535)

Each direction independent
Both directions must be explicitly allowed
```

## AWS Security Groups

### Structure

**Security Group Components**:
```
Security Group ID: sg-0123456789abcdef0
VPC: vpc-abc123
Name: web-server-sg
Description: Security group for web servers

Inbound Rules:
- Type: HTTP, Protocol: TCP, Port: 80, Source: 0.0.0.0/0
- Type: HTTPS, Protocol: TCP, Port: 443, Source: 0.0.0.0/0
- Type: SSH, Protocol: TCP, Port: 22, Source: 10.0.0.0/16

Outbound Rules:
- All traffic, All protocols, All ports, Destination: 0.0.0.0/0
```

### Rule Types

**Source/Destination Types**:

**IP Address**:
```
0.0.0.0/0           # All IPv4
::/0                # All IPv6
10.0.0.0/16         # Specific CIDR
203.0.113.25/32     # Single IP
```

**Security Group**:
```
sg-0123456789abcdef0    # Another security group
                        # Allows instances in that SG
```

**Prefix List**:
```
pl-12345678    # Managed prefix list (S3, CloudFront, etc.)
```

### Common Patterns

**Web Server Security Group**:
```
Inbound:
- HTTP (80) from 0.0.0.0/0
- HTTPS (443) from 0.0.0.0/0
- SSH (22) from bastion-sg

Outbound:
- All traffic to 0.0.0.0/0
```

**Application Server Security Group**:
```
Inbound:
- Application port (8080) from alb-sg
- SSH (22) from bastion-sg

Outbound:
- PostgreSQL (5432) to database-sg
- HTTPS (443) to 0.0.0.0/0 (for API calls)
```

**Database Security Group**:
```
Inbound:
- PostgreSQL (5432) from app-sg
- PostgreSQL (5432) from bastion-sg

Outbound:
- None (default deny)
```

**Bastion Security Group**:
```
Inbound:
- SSH (22) from corporate-ip/32

Outbound:
- SSH (22) to 10.0.0.0/16
```

**Load Balancer Security Group**:
```
Inbound:
- HTTP (80) from 0.0.0.0/0
- HTTPS (443) from 0.0.0.0/0

Outbound:
- HTTP (80) to web-sg
- HTTPS (443) to web-sg
```

### Security Group Chaining

**Referencing Security Groups**:
```
ALB Security Group (sg-alb)
    |
    +-- Allows traffic to Web SG
        |
        Web Security Group (sg-web)
            |
            +-- Allows traffic from sg-alb only
```

**Benefits**:
- No IP address management
- Automatic updates when instances change
- Cleaner rule management
- Better security (least privilege)

### Limits and Quotas

**AWS Limits** (default, can be increased):
```
Security groups per VPC: 2,500
Rules per security group: 60 (inbound + outbound)
Security groups per network interface: 5
Total rules per network interface: 300
```

## AWS Network ACLs

### Structure

**Network ACL Components**:
```
Network ACL ID: acl-0123456789abcdef0
VPC: vpc-abc123
Associated Subnets: subnet-123, subnet-456

Inbound Rules:
Rule #  Type    Protocol  Port Range  Source        Allow/Deny
100     HTTP    TCP       80          0.0.0.0/0     ALLOW
110     HTTPS   TCP       443         0.0.0.0/0     ALLOW
120     SSH     TCP       22          10.0.0.0/16   ALLOW
*       All     All       All         0.0.0.0/0     DENY

Outbound Rules:
Rule #  Type    Protocol  Port Range  Destination   Allow/Deny
100     All     All       All         0.0.0.0/0     ALLOW
*       All     All       All         0.0.0.0/0     DENY
```

### Rule Processing

**Sequential Evaluation**:
```
1. Rules evaluated in order (lowest rule number first)
2. First match applies
3. Processing stops
4. Default rule (*) is implicit deny

Example:
Rule 100: Allow 10.0.0.0/16
Rule 200: Deny 10.0.1.0/24

10.0.1.5 is allowed (rule 100 matches first)
```

### Ephemeral Ports

**Stateless Return Traffic**:
```
Client connects to server on port 80
Server responds from port 80 to client ephemeral port (1024-65535)

Network ACL must allow:
Inbound: TCP 80 from client
Outbound: TCP 1024-65535 to client

AND

Inbound: TCP 1024-65535 from server (for client)
Outbound: TCP 80 to server (for client)
```

**OS Ephemeral Port Ranges**:
```
Linux: 32768-60999
Windows: 49152-65535
NAT Gateway: 1024-65535

Recommendation: Allow 1024-65535 for compatibility
```

### Common Patterns

**Public Subnet NACL**:
```
Inbound:
100  HTTP       TCP  80       0.0.0.0/0        ALLOW
110  HTTPS      TCP  443      0.0.0.0/0        ALLOW
120  SSH        TCP  22       203.0.113.0/24   ALLOW
130  Ephemeral  TCP  1024-65535  0.0.0.0/0     ALLOW
*    All        All  All      0.0.0.0/0        DENY

Outbound:
100  HTTP       TCP  80       0.0.0.0/0        ALLOW
110  HTTPS      TCP  443      0.0.0.0/0        ALLOW
120  Ephemeral  TCP  1024-65535  0.0.0.0/0     ALLOW
*    All        All  All      0.0.0.0/0        DENY
```

**Private Subnet NACL**:
```
Inbound:
100  All TCP    TCP  0-65535  10.0.0.0/16      ALLOW
110  HTTPS      TCP  443      0.0.0.0/0        ALLOW
120  Ephemeral  TCP  1024-65535  0.0.0.0/0     ALLOW
*    All        All  All      0.0.0.0/0        DENY

Outbound:
100  All TCP    TCP  0-65535  10.0.0.0/16      ALLOW
110  All        All  All      0.0.0.0/0        ALLOW
*    All        All  All      0.0.0.0/0        DENY
```

**Database Subnet NACL**:
```
Inbound:
100  PostgreSQL TCP  5432     10.0.1.0/24      ALLOW
110  PostgreSQL TCP  5432     10.0.2.0/24      ALLOW
120  Ephemeral  TCP  1024-65535  10.0.0.0/16   ALLOW
*    All        All  All      0.0.0.0/0        DENY

Outbound:
100  All TCP    TCP  0-65535  10.0.0.0/16      ALLOW
110  HTTPS      TCP  443      0.0.0.0/0        ALLOW
*    All        All  All      0.0.0.0/0        DENY
```

## Azure Network Security Groups (NSG)

### Structure

**NSG Components**:
```
NSG Name: web-nsg
Resource Group: rg-production
Location: eastus

Inbound Security Rules:
Priority  Name     Port  Protocol  Source    Destination  Action
100       AllowHTTP  80   TCP      Internet  *            Allow
110       AllowHTTPS 443  TCP      Internet  *            Allow
65000     DenyAllInBound *   *     *         *            Deny

Outbound Security Rules:
Priority  Name     Port  Protocol  Source    Destination  Action
100       AllowAll  *    *         *         Internet     Allow
```

### Rule Priority

**Priority Ranges**:
```
100-4096: Custom rules (lower number = higher priority)
65000-65500: Default rules
    - AllowVNetInBound (65000)
    - AllowAzureLoadBalancerInBound (65001)
    - DenyAllInBound (65500)

Rules processed by priority
First match wins
```

### Service Tags

**Azure Service Tags**:
```
Internet: All internet addresses
VirtualNetwork: All addresses in VNet
AzureLoadBalancer: Azure load balancer probes
Sql: Azure SQL Database
Storage: Azure Storage
AzureMonitor: Azure Monitor

Example:
Allow HTTPS to Storage:
Destination: Storage
Port: 443
Protocol: TCP
```

### Application Security Groups (ASG)

**Logical Grouping**:
```
ASG: web-asg
Members:
- web-vm-1
- web-vm-2
- web-vm-3

ASG: app-asg
Members:
- app-vm-1
- app-vm-2

NSG Rule:
Allow TCP 8080 from web-asg to app-asg

No IP management needed
Dynamic membership
```

### Common Patterns

**Web Tier NSG**:
```
Inbound:
100  AllowHTTP      80   TCP  Internet        VirtualNetwork  Allow
110  AllowHTTPS     443  TCP  Internet        VirtualNetwork  Allow
120  AllowAppTier   8080 TCP  app-asg         web-asg         Allow

Outbound:
100  AllowAppTier   8080 TCP  web-asg         app-asg         Allow
110  AllowInternet  *    *    VirtualNetwork  Internet        Allow
```

**Database Tier NSG**:
```
Inbound:
100  AllowSQL       1433 TCP  app-asg         db-asg          Allow
110  AllowBastion   3389 TCP  bastion-subnet  *               Allow

Outbound:
100  AllowStorage   443  TCP  *               Storage         Allow
110  DenyInternet   *    *    *               Internet        Deny
```

## GCP Firewall Rules

### Structure

**Firewall Rule Components**:
```
Name: allow-http-https
Network: default
Priority: 1000
Direction: Ingress
Action: Allow
Targets: Tagged instances (web-server)
Source: 0.0.0.0/0
Protocols/Ports: tcp:80, tcp:443
```

### Implied Rules

**Default Firewall Rules**:
```
Implied Allow Egress:
- Priority: 65535
- Destination: 0.0.0.0/0
- Action: Allow

Implied Deny Ingress:
- Priority: 65535
- Source: 0.0.0.0/0
- Action: Deny

Cannot be deleted
Can be overridden with lower priority rules
```

### Target Specification

**Target Types**:

**All instances in network**:
```
Targets: All instances in network
Applies to every instance in VPC
```

**Specified target tags**:
```
Target tags: web-server, api-server
Applies to instances with matching tags
```

**Specified service accounts**:
```
Target service accounts: web-app@project.iam.gserviceaccount.com
Applies to instances using service account
```

### Source/Destination Types

**Source for Ingress Rules**:
```
IP ranges: 0.0.0.0/0, 10.0.0.0/8
Source tags: internal-server
Source service accounts: app@project.iam.gserviceaccount.com
```

**Destination for Egress Rules**:
```
IP ranges: 0.0.0.0/0, 192.168.1.0/24
Destination ranges: Can be any IP
```

### Common Patterns

**Web Server Firewall**:
```
Name: allow-web-traffic
Direction: Ingress
Priority: 1000
Targets: Tag: web-server
Source: 0.0.0.0/0
Protocols: tcp:80, tcp:443
Action: Allow
```

**Internal Communication**:
```
Name: allow-internal
Direction: Ingress
Priority: 1000
Targets: All instances in network
Source: 10.0.0.0/8
Protocols: All
Action: Allow
```

**SSH from Corporate Network**:
```
Name: allow-ssh-corp
Direction: Ingress
Priority: 1000
Targets: All instances in network
Source: 203.0.113.0/24
Protocols: tcp:22
Action: Allow
```

**Deny Specific Traffic**:
```
Name: deny-rdp
Direction: Ingress
Priority: 900
Targets: All instances in network
Source: 0.0.0.0/0
Protocols: tcp:3389
Action: Deny
```

## Defense in Depth

### Layered Security

**Multi-Layer Protection**:
```
Layer 1: Edge Protection (WAF, DDoS)
    |
Layer 2: Network ACL (Subnet level)
    |
Layer 3: Security Group (Instance level)
    |
Layer 4: Host Firewall (OS level)
    |
Layer 5: Application Security
```

### Security Group Strategy

**Principle of Least Privilege**:
```
1. Deny all by default
2. Allow only required traffic
3. Use specific ports, not ranges
4. Restrict sources to minimum necessary
5. Separate by tier/function
6. Regular audits and cleanup
```

### Network Segmentation

**Tier Isolation**:
```
Public Tier (Web):
- Internet access inbound
- Restricted to web ports
- Access to app tier only

Private Tier (App):
- No internet access inbound
- Accept from web tier only
- Access to database tier only

Database Tier:
- No internet access
- Accept from app tier only
- Outbound for patches only
```

## Best Practices

### Security Groups

**Design**:
1. Use descriptive names and descriptions
2. One security group per function/tier
3. Reference other security groups, not IPs
4. Document purpose of each rule
5. Use tags for organization

**Security**:
1. Principle of least privilege
2. Avoid 0.0.0.0/0 for sensitive ports
3. Use specific protocols and ports
4. Remove unused rules
5. Regular security audits

**Operations**:
1. Use infrastructure as code
2. Version control security group configs
3. Test changes in non-prod first
4. Monitor security group changes
5. Alert on high-risk changes

### Network ACLs

**Design**:
1. Start with default deny
2. Use rule number increments (100, 110, 120)
3. Leave gaps for future insertions
4. Document rule purpose
5. Keep rules simple

**Security**:
1. Use for broad subnet-level restrictions
2. Complement security groups, don't replace
3. Block known bad actors
4. Restrict by protocol and port
5. Regular rule review

**Operations**:
1. Remember stateless nature
2. Allow ephemeral ports for return traffic
3. Test connectivity after changes
4. Monitor for unexpected blocks
5. Use for compliance requirements

## Monitoring and Auditing

### VPC Flow Logs

**Enable Flow Logs**:
```
Capture:
- Source and destination IPs
- Source and destination ports
- Protocol
- Packets and bytes
- Action (ACCEPT or REJECT)

Analyze:
- Rejected connections (security group blocks)
- Traffic patterns
- Security anomalies
- Compliance reporting
```

**Flow Log Analysis**:
```
Frequent rejects from same source: Potential attack
Unexpected traffic patterns: Security investigation
High volume to unexpected destination: Data exfiltration?
Rejected traffic to expected destination: Configuration issue
```

### AWS Config

**Track Security Group Changes**:
```
AWS Config Rules:
- restricted-ssh (SSH not from 0.0.0.0/0)
- restricted-common-ports
- vpc-sg-open-only-to-authorized-ports

Automatic compliance checking
Alert on non-compliant changes
```

### Azure Security Center

**Security Recommendations**:
```
- Adaptive network hardening
- Just-in-time VM access
- NSG recommendations
- Network map visualization
```

### Cloud Logging

**Audit Logs**:
```
Log all security group changes:
- Who made the change
- What was changed
- When it was changed
- Source IP of change

Alerts for sensitive changes
Compliance reporting
```

## Troubleshooting

### Common Issues

**Cannot Connect to Instance**:
```
Check:
1. Security group inbound rules
2. Network ACL inbound rules
3. Route table configuration
4. Instance has public IP (if connecting from internet)
5. Instance is running
6. Application is listening on port
```

**Intermittent Connectivity**:
```
Check:
1. Network ACL ephemeral port rules
2. Security group vs NACL conflict
3. Connection timeout settings
4. Load balancer health checks
```

**Database Connection Timeout**:
```
Check:
1. Database security group allows app tier
2. Network ACL allows database port
3. Route table configuration
4. Database is running
5. Connection string correct
```

### Diagnostic Commands

**Test Connectivity**:
```bash
# Test TCP connection
nc -zv hostname 80
telnet hostname 80

# Trace route
traceroute hostname

# Check DNS
nslookup hostname

# VPC Reachability Analyzer (AWS)
aws ec2 analyze-path-request
```

## Automation and IaC

### Terraform Example

**Security Group**:
```hcl
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description     = "App port from ALB"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web-sg"
  }
}
```

### CloudFormation Example

```yaml
WebSecurityGroup:
  Type: AWS::EC2::SecurityGroup
  Properties:
    GroupDescription: Web server security group
    VpcId: !Ref VPC
    SecurityGroupIngress:
      - IpProtocol: tcp
        FromPort: 80
        ToPort: 80
        CidrIp: 0.0.0.0/0
      - IpProtocol: tcp
        FromPort: 443
        ToPort: 443
        CidrIp: 0.0.0.0/0
    Tags:
      - Key: Name
        Value: web-sg
```

## Compliance Considerations

### PCI-DSS

**Requirements**:
- Network segmentation
- Restrict access to cardholder data
- Deny all by default
- Logging and monitoring
- Regular firewall reviews

### HIPAA

**Requirements**:
- Network isolation
- Encryption in transit
- Access controls
- Audit logging
- Regular security assessments

### SOC 2

**Requirements**:
- Documented network security policies
- Change management process
- Access control reviews
- Incident response
- Monitoring and alerting

## Conclusion

Security groups and network ACLs are fundamental to cloud network security. Implement layered security, follow least privilege principle, use infrastructure as code, and maintain continuous monitoring for a secure cloud network architecture.
