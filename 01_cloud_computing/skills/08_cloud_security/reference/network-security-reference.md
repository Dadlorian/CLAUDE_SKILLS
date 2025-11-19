# Network Security Reference

## Introduction

Network security in cloud environments involves protecting network infrastructure, controlling traffic flow, preventing unauthorized access, and defending against network-based attacks. This reference covers VPC security, firewalls, DDoS protection, and network segmentation strategies.

## Cloud Network Security Fundamentals

### Shared Responsibility Model

**Cloud Provider Responsibilities**:
- Physical network infrastructure security
- Network infrastructure redundancy and availability
- DDoS protection at infrastructure level
- Network isolation between tenants

**Customer Responsibilities**:
- Virtual network configuration (VPC, VNet, VPC)
- Security groups and firewall rules
- Network segmentation and isolation
- Application-layer DDoS protection
- Network monitoring and logging

### Defense-in-Depth Layers

**Layer 1: Network Perimeter**:
- DDoS protection
- Web Application Firewall (WAF)
- Edge security and CDN protection

**Layer 2: Network Segmentation**:
- VPC/VNet architecture
- Subnets (public, private, isolated)
- Network ACLs and NSGs

**Layer 3: Instance-Level Firewalls**:
- Security groups (AWS, GCP)
- Network security groups (Azure)
- Host-based firewalls

**Layer 4: Application Layer**:
- API gateways
- Load balancer security
- TLS/SSL termination

**Layer 5: Data Layer**:
- Private endpoints
- Encryption in transit
- Database firewall rules

## Virtual Private Cloud (VPC) Security

### AWS VPC Security

**VPC Architecture**:
```
VPC (10.0.0.0/16)
├── Public Subnet 1 (10.0.1.0/24) - AZ1
├── Public Subnet 2 (10.0.2.0/24) - AZ2
├── Private Subnet 1 (10.0.10.0/24) - AZ1
├── Private Subnet 2 (10.0.20.0/24) - AZ2
├── Isolated Subnet 1 (10.0.100.0/24) - AZ1 (Databases)
└── Isolated Subnet 2 (10.0.200.0/24) - AZ2 (Databases)
```

**Security Groups** (Stateful):
- Default deny all inbound, allow all outbound
- Allow only necessary inbound traffic
- Reference security groups instead of CIDR blocks
- Separate security groups per tier (web, app, db)
- Use descriptions for all rules

**Example**:
```json
{
  "IpPermissions": [{
    "IpProtocol": "tcp",
    "FromPort": 443,
    "ToPort": 443,
    "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "HTTPS from internet"}]
  }, {
    "IpProtocol": "tcp",
    "FromPort": 8080,
    "ToPort": 8080,
    "UserIdGroupPairs": [{"GroupId": "sg-alb", "Description": "App port from ALB"}]
  }]
}
```

**Network ACLs** (Stateless):
- Subnet-level firewall
- Numbered rules (evaluated in order)
- Separate inbound and outbound rules
- Ephemeral port considerations

**Best Practices**:
- Enable VPC Flow Logs (all ENIs)
- Use private subnets for application and data tiers
- NAT Gateway for outbound internet from private subnets
- VPC endpoints for AWS services (no internet routing)
- Enable DNS resolution and DNS hostnames
- Use multiple availability zones

### Azure Virtual Network Security

**VNet Architecture**:
```
VNet (10.0.0.0/16)
├── Frontend Subnet (10.0.1.0/24)
├── Application Subnet (10.0.10.0/24)
├── Database Subnet (10.0.100.0/24)
└── AzureBastionSubnet (10.0.255.0/27)
```

**Network Security Groups (NSGs)**:
- Stateful firewall rules
- Applied to subnets or NICs
- Priority-based rule evaluation (100-4096, lower = higher priority)
- Default rules (allow VNet, allow Azure Load Balancer, deny all)

**Example**:
```json
{
  "name": "Allow-HTTPS",
  "priority": 100,
  "direction": "Inbound",
  "access": "Allow",
  "protocol": "Tcp",
  "sourcePortRange": "*",
  "destinationPortRange": "443",
  "sourceAddressPrefix": "Internet",
  "destinationAddressPrefix": "*"
}
```

**Application Security Groups (ASGs)**:
- Logical grouping of VMs
- Reference in NSG rules instead of IP addresses
- Simplifies rule management for dynamic environments

**Best Practices**:
- Enable NSG Flow Logs
- Use Azure Firewall for centralized network security
- Implement Azure Bastion for secure RDP/SSH access
- Use Private Endpoints for Azure PaaS services
- Service endpoints for Azure services from VNet
- Hub-spoke network topology for multi-VNet environments

### GCP VPC Security

**VPC Architecture**:
- Global VPC with regional subnets
- No subnets span regions, but VPC is global
- Custom or auto mode VPC

**Firewall Rules**:
- Stateful firewall
- Priority-based (0-65535, lower = higher priority)
- Implied deny all ingress, allow all egress
- Target tags or service accounts

**Example**:
```yaml
gcloud compute firewall-rules create allow-https \
  --network=my-vpc \
  --allow=tcp:443 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=web-server \
  --description="Allow HTTPS to web servers"
```

**Hierarchical Firewall Policies**:
- Organization or folder-level policies
- Inherited by all VPCs in scope
- Centralized firewall management

**Best Practices**:
- Enable VPC Flow Logs
- Use Private Google Access for GCP API access
- VPC Service Controls for data exfiltration protection
- Shared VPC for multi-project environments
- Use service accounts for targeting instead of tags
- Cloud NAT for private instances outbound access

## Firewall Solutions

### Web Application Firewall (WAF)

**AWS WAF**:
- Managed rules (AWS Managed Rules, OWASP Top 10)
- Custom rules (IP sets, regex, geo-blocking, rate limiting)
- Integration: CloudFront, Application Load Balancer, API Gateway, AppSync
- Rule groups and priorities

**Common Rule Types**:
```json
{
  "Name": "BlockSQLInjection",
  "Priority": 1,
  "Statement": {
    "ManagedRuleGroupStatement": {
      "VendorName": "AWS",
      "Name": "AWSManagedRulesSQLiRuleSet"
    }
  },
  "Action": {"Block": {}},
  "VisibilityConfig": {
    "SampledRequestsEnabled": true,
    "CloudWatchMetricsEnabled": true,
    "MetricName": "SQLInjectionRule"
  }
}
```

**Azure WAF**:
- Integration: Application Gateway WAF v2, Azure Front Door
- OWASP ModSecurity Core Rule Set (CRS)
- Custom rules and exclusions
- Policy modes: Detection, Prevention

**GCP Cloud Armor**:
- DDoS protection and WAF
- Preconfigured rules (ModSecurity CRS, XSS, SQL injection)
- Rate limiting and geographic blocking
- Adaptive protection (ML-based)

**WAF Best Practices**:
- Start in detection mode, tune rules, then enable prevention
- Use managed rule sets for baseline protection
- Custom rules for application-specific threats
- Rate limiting to prevent abuse
- Geo-blocking for known threat regions
- Monitor WAF metrics and sampled requests
- Regular rule tuning based on false positives

### Cloud-Native Firewalls

**AWS Network Firewall**:
- Stateful firewall with IDS/IPS
- Suricata-compatible rules
- Domain filtering, SNI inspection
- Centralized firewall for multiple VPCs (Transit Gateway)

**Azure Firewall**:
- Fully stateful firewall
- Application rules (FQDN, HTTP/S filtering)
- Network rules (IP, port, protocol)
- Threat intelligence integration
- Forced tunneling support

**Azure Firewall Premium**:
- TLS inspection
- IDPS (Intrusion Detection and Prevention)
- URL filtering
- Web categories

**GCP Cloud Next-Generation Firewall**:
- Layer 7 inspection
- IDPS with Palo Alto Networks threat intelligence
- FQDN-based rules
- Geo-IP-based filtering

## DDoS Protection

### AWS Shield

**Shield Standard** (Free):
- Automatic protection for all AWS customers
- Protection against common Layer 3/4 attacks
- Always-on detection and mitigation

**Shield Advanced** ($3000/month):
- Enhanced protection for EC2, ELB, CloudFront, Route 53, Global Accelerator
- Real-time metrics and reports
- DDoS Response Team (DRT) support
- Cost protection (credits for scaling during attack)
- Integration with WAF (no extra cost for WAF on protected resources)

**Best Practices**:
- Use CloudFront with Shield Advanced
- Enable Route 53 health checks and failover
- Configure WAF rate-based rules
- Set up CloudWatch alarms for DDoS metrics
- Document incident response plan

### Azure DDoS Protection

**Basic** (Free):
- Automatic protection for all Azure resources
- Always-on traffic monitoring
- Protection against common attacks

**Standard** ($2,944/month per subscription):
- Enhanced mitigation capabilities
- Application-layer protection with WAF
- Real-time attack metrics and alerts
- Post-attack reports
- Cost protection during DDoS attacks

**Best Practices**:
- Enable DDoS Protection Standard on all public-facing VNets
- Use Azure Front Door with WAF
- Configure health probes and failover
- Set up alerts for DDoS attack metrics

### GCP Cloud Armor

**Features** (No separate DDoS pricing):
- Protection against Layer 3/4 and Layer 7 attacks
- Anycast-based mitigation
- Always-on protection
- Adaptive protection (ML-based anomaly detection)
- Rate limiting and geographic blocking

**Adaptive Protection**:
- Learns normal traffic patterns
- Detects and mitigates Layer 7 DDoS attacks
- Provides suggested rules based on attack signatures

**Best Practices**:
- Enable Cloud Armor on all external load balancers
- Configure rate limiting policies
- Enable Adaptive Protection for ML-based detection
- Set up alerts for DDoS events
- Use Cloud CDN to absorb traffic spikes

## Network Segmentation

### Multi-Tier Architecture

**Three-Tier Pattern**:
```
┌──────────────────────┐
│  Public Subnet       │  Web Tier (Load Balancer)
│  (0.0.0.0/0 ingress) │  - Internet-facing
└──────────┬───────────┘  - HTTPS only
           │
┌──────────▼───────────┐
│  Private Subnet      │  Application Tier
│  (No internet)       │  - NAT Gateway for outbound
└──────────┬───────────┘  - Security group allows traffic from Web tier only
           │
┌──────────▼───────────┐
│  Isolated Subnet     │  Data Tier
│  (No internet)       │  - No internet access at all
└──────────────────────┘  - Security group allows traffic from App tier only
```

**Benefits**:
- Reduced attack surface
- Lateral movement prevention
- Compliance alignment
- Defense-in-depth

### Micro-Segmentation

**Concept**: Fine-grained network isolation at workload level

**Implementation**:
- Security groups per application component
- Service mesh with network policies (Istio, Linkerd)
- Kubernetes NetworkPolicies
- Zero trust network architecture

**Example** (Kubernetes NetworkPolicy):
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-policy
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
```

## Private Connectivity

### AWS PrivateLink

**Use Cases**:
- Private access to AWS services (S3, DynamoDB, etc.)
- Expose your service to other AWS accounts
- No internet gateway or NAT required

**VPC Endpoints**:
- **Gateway Endpoints**: S3, DynamoDB (route table entry)
- **Interface Endpoints**: Most AWS services (ENI in subnet)

**Endpoint Services**:
- Expose your service behind Network Load Balancer
- Other accounts connect via VPC endpoint
- Private DNS names

**Best Practices**:
- Use VPC endpoints for all supported AWS services
- Enable endpoint policies for fine-grained access control
- Use PrivateLink for multi-account service exposure
- Private DNS enabled for interface endpoints

### Azure Private Link

**Private Endpoints**:
- Private IP for Azure PaaS services (Storage, SQL, Key Vault, etc.)
- Traffic stays on Microsoft backbone
- No public IP exposure

**Private Link Service**:
- Expose your service behind Standard Load Balancer
- Customers connect via Private Endpoint

**Best Practices**:
- Use Private Endpoints for all production PaaS services
- Disable public access when using Private Endpoints
- Use Private DNS zones for name resolution
- Apply NSGs to Private Endpoint subnets

### GCP Private Service Connect

**Private Service Connect Endpoints**:
- Private access to Google APIs (storage.googleapis.com, etc.)
- Private IP address in your VPC

**Published Services**:
- Expose your service for private consumption
- Service Attachment configuration

**Best Practices**:
- Use Private Google Access for GCP API access
- Private Service Connect for third-party services
- Configure DNS for private endpoints

## Network Monitoring and Logging

### Flow Logs

**AWS VPC Flow Logs**:
```
version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes start end action log-status
2 123456789012 eni-abc123 10.0.1.5 10.0.2.10 443 49152 6 20 4000 1620000000 1620000060 ACCEPT OK
```

**Use Cases**:
- Traffic analysis and troubleshooting
- Security monitoring and anomaly detection
- Network optimization
- Compliance and audit

**Best Practices**:
- Enable for all VPCs, subnets, and ENIs
- Send to S3 for long-term storage and analysis
- Stream to CloudWatch Logs for real-time analysis
- Use Athena for ad-hoc querying
- Partition by date for cost efficiency

**Azure NSG Flow Logs**:
- Version 1: Basic flow information
- Version 2: Includes flow state and throughput

**GCP VPC Flow Logs**:
- Sampled packet metadata (configurable sampling rate)
- Sent to Cloud Logging
- Export to BigQuery for analysis

### Traffic Mirroring

**AWS VPC Traffic Mirroring**:
- Copy network traffic from ENI
- Send to security appliances for deep packet inspection
- Filter by traffic direction, protocol, port

**Use Cases**:
- Intrusion detection systems (IDS)
- Network monitoring and forensics
- Troubleshooting
- Compliance

**Alternatives**:
- Azure Network Watcher packet capture
- GCP Packet Mirroring

### Network Detection and Response

**Tools**:
- **AWS GuardDuty**: Threat detection including VPC Flow Log analysis
- **Azure Sentinel**: SIEM with NSG Flow Log integration
- **GCP Chronicle**: Security analytics with VPC Flow Log support
- **Third-Party**: Darktrace, ExtraHop, Vectra AI

**Detection Scenarios**:
- Port scanning
- Unusual traffic patterns
- Data exfiltration attempts
- Lateral movement
- C2 communication

## Zero Trust Networking

### BeyondCorp / Zero Trust Principles

**Traditional Perimeter**:
```
Internet → Firewall → Trusted Internal Network → Resources
```

**Zero Trust**:
```
Internet → Identity-Aware Proxy → Per-Request Authorization → Resource
         (Authentication + Device Trust + Context)
```

**Principles**:
1. Verify explicitly (identity, device, location, data sensitivity)
2. Least privilege access (JIT, just enough access)
3. Assume breach (minimize blast radius, segment access, verify end-to-end encryption)

### Implementation Patterns

**Google BeyondCorp**:
- Identity-Aware Proxy (IAP)
- Context-Aware Access
- Binary Authorization
- VPC Service Controls

**Microsoft Zero Trust**:
- Azure AD Conditional Access
- Azure Firewall with threat intelligence
- Defender for Cloud Apps
- Microsoft Defender for Endpoint (device trust)

**AWS Zero Trust**:
- IAM with Condition Keys
- PrivateLink for service access
- Network segmentation
- Client VPN with SAML authentication

### Service Mesh Security

**Istio**:
- Automatic mTLS between services
- Authorization policies
- Authentication with JWT validation
- Traffic routing and encryption

**Example**:
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
spec:
  mtls:
    mode: STRICT  # Require mTLS for all services
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: api-policy
spec:
  selector:
    matchLabels:
      app: api
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/frontend"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
```

## Network Security Best Practices

### Design Principles
- ✅ Default deny all traffic, explicitly allow necessary
- ✅ Defense-in-depth with multiple security layers
- ✅ Principle of least privilege for network access
- ✅ Network segmentation (public, private, isolated)
- ✅ Private connectivity for sensitive traffic
- ✅ Encryption in transit for all traffic
- ✅ Comprehensive network logging and monitoring
- ✅ Regular security group and firewall rule audits

### Common Mistakes
- ❌ 0.0.0.0/0 access on non-public resources
- ❌ All ports open (0-65535)
- ❌ No network segmentation
- ❌ Disabled flow logs
- ❌ Using deprecated protocols (Telnet, FTP, HTTP)
- ❌ No DDoS protection for public-facing resources
- ❌ Overly permissive security groups
- ❌ No network monitoring or alerting

### Security Checklist
- [ ] VPC Flow Logs enabled
- [ ] Security groups follow least privilege
- [ ] Private subnets for application and data tiers
- [ ] VPC endpoints/Private Link for cloud services
- [ ] WAF enabled on public-facing applications
- [ ] DDoS protection configured
- [ ] Network ACLs for subnet-level controls
- [ ] TLS 1.2+ enforced for all traffic
- [ ] Regular security group audits
- [ ] Network anomaly detection configured

## Compliance and Network Security

### PCI DSS Requirements
- Requirement 1: Install and maintain network security controls
- Network segmentation (CDE isolation)
- Firewall rules documented and reviewed
- Restricted inbound/outbound traffic

### HIPAA Requirements
- 164.312(e)(1): Transmission security
- Encryption in transit
- Network integrity controls

### SOC 2 Controls
- CC6.6: Logical access - network segmentation
- CC7.2: System monitoring - network monitoring

## Tools and Resources

### Network Security Tools
- **Nmap**: Network scanning and discovery
- **Wireshark**: Packet analysis
- **tcpdump**: Packet capture
- **iptables/nftables**: Linux firewall
- **Zeek (Bro)**: Network security monitoring

### Cloud-Native Services
- AWS: VPC, Security Groups, Network Firewall, WAF, Shield
- Azure: VNet, NSG, Azure Firewall, WAF, DDoS Protection
- GCP: VPC, Firewall Rules, Cloud Armor, Cloud NAT

### Third-Party Solutions
- Palo Alto Networks Prisma Cloud
- Fortinet FortiGate
- Check Point CloudGuard
- Cisco Secure Firewall
- F5 BIG-IP

### Resources
- AWS VPC Security: https://docs.aws.amazon.com/vpc/latest/userguide/security.html
- Azure Network Security: https://docs.microsoft.com/azure/security/fundamentals/network-overview
- GCP VPC Security: https://cloud.google.com/vpc/docs/vpc
- NIST SP 800-41: Guidelines on Firewalls and Firewall Policy
- CIS Benchmarks: AWS, Azure, GCP network security sections
