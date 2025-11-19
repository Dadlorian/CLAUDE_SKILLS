# Cloud Security Overview Reference

## Introduction

Cloud security encompasses the technologies, policies, controls, and practices designed to protect cloud-based systems, data, and infrastructure. This reference provides a comprehensive overview of cloud security principles, the shared responsibility model, and key security domains.

## Shared Responsibility Model

### Cloud Provider Responsibilities (Security OF the Cloud)
- **Physical Security**: Data centers, hardware, physical access controls
- **Infrastructure Security**: Hypervisor, network infrastructure, storage infrastructure
- **Service Availability**: SLA commitments, redundancy, disaster recovery
- **Compliance Certifications**: SOC 2, ISO 27001, PCI DSS, FedRAMP, regional certifications
- **Platform Security**: Base security controls, patching, platform-level protections

### Customer Responsibilities (Security IN the Cloud)
- **Data Security**: Encryption, classification, DLP, backup
- **Identity & Access Management**: User authentication, authorization, federation
- **Application Security**: Secure coding, vulnerability management, security testing
- **Operating System**: Patching, hardening, configuration management
- **Network Security**: Security groups, firewalls, network segmentation
- **Compliance**: Meeting regulatory requirements, audit evidence, policy enforcement

### Shared Responsibilities (Varies by Service Model)
- **IaaS**: Customer responsible for OS and above
- **PaaS**: Customer responsible for applications and data
- **SaaS**: Customer responsible for data and user access

## Core Security Domains

### 1. Identity & Access Management (IAM)
**Purpose**: Control who can access what resources and under what conditions

**Key Components**:
- Authentication (who you are): MFA, SSO, federation
- Authorization (what you can do): RBAC, ABAC, policies
- Auditing (what you did): Access logs, activity monitoring

**Best Practices**:
- Implement least privilege access
- Use temporary credentials when possible
- Enable MFA for all users, especially privileged accounts
- Regular access reviews and permission audits
- Centralized identity management

### 2. Data Protection
**Purpose**: Ensure confidentiality, integrity, and availability of data

**Key Components**:
- Encryption at rest: Block storage, object storage, databases
- Encryption in transit: TLS/SSL, VPNs, private links
- Key management: KMS, HSM, key rotation, lifecycle
- Secrets management: Credentials, API keys, certificates
- Data classification: Sensitivity levels, handling requirements

**Best Practices**:
- Encrypt all sensitive data at rest and in transit
- Use cloud-native key management services
- Implement automated key rotation
- Never hardcode secrets in code or configuration
- Classify data and apply appropriate controls

### 3. Network Security
**Purpose**: Protect network traffic and prevent unauthorized access

**Key Components**:
- Network segmentation: VPCs, subnets, VNets
- Traffic filtering: Security groups, NACLs, NSGs, firewalls
- DDoS protection: Rate limiting, distributed defense
- Web application firewall (WAF): OWASP Top 10 protection
- Private connectivity: PrivateLink, Private Endpoints

**Best Practices**:
- Default deny, explicitly allow necessary traffic
- Implement defense-in-depth with multiple layers
- Use private subnets for sensitive resources
- Enable VPC Flow Logs for visibility
- Implement micro-segmentation for critical workloads

### 4. Application Security
**Purpose**: Secure applications throughout the development lifecycle

**Key Components**:
- Secure SDLC: Security requirements, threat modeling
- Security testing: SAST, DAST, SCA, penetration testing
- Container security: Image scanning, runtime protection
- API security: Authentication, authorization, rate limiting
- Supply chain security: Dependency scanning, SBOM

**Best Practices**:
- Shift security left in the development process
- Implement security gates in CI/CD pipelines
- Regular vulnerability scanning and patching
- Input validation and output encoding
- Security training for developers

### 5. Compliance & Governance
**Purpose**: Meet regulatory requirements and maintain security standards

**Key Components**:
- Compliance frameworks: SOC 2, ISO 27001, PCI DSS, HIPAA, GDPR
- Security standards: CIS Benchmarks, NIST, OWASP
- Policy as code: Automated policy enforcement
- Audit logging: Comprehensive, immutable logs
- Security assessments: Vulnerability assessments, penetration testing

**Best Practices**:
- Understand applicable compliance requirements
- Implement security baselines (CIS Benchmarks)
- Enable comprehensive audit logging
- Regular compliance validation and audits
- Document security controls and procedures

### 6. Threat Detection & Response
**Purpose**: Detect, investigate, and respond to security threats

**Key Components**:
- Threat detection: GuardDuty, Sentinel, Security Command Center
- SIEM: Centralized security event management
- Anomaly detection: ML-based behavioral analysis
- Incident response: Playbooks, runbooks, automation
- Forensics: Evidence collection, analysis, preservation

**Best Practices**:
- Centralize security logs and events
- Implement automated threat detection
- Define incident response procedures
- Regular tabletop exercises and drills
- Measure MTTD (Mean Time to Detect) and MTTR (Mean Time to Respond)

## Security Architecture Principles

### Defense-in-Depth
Implement multiple layers of security controls across different levels:
- **Edge Layer**: WAF, DDoS protection, CDN security
- **Network Layer**: Firewalls, security groups, network segmentation
- **Compute Layer**: OS hardening, runtime protection, antimalware
- **Application Layer**: Input validation, authentication, authorization
- **Data Layer**: Encryption, access controls, data loss prevention

### Zero Trust Architecture
Never trust, always verify:
- **Verify Explicitly**: Always authenticate and authorize
- **Least Privilege Access**: Just-in-time, just-enough access
- **Assume Breach**: Minimize blast radius, segment access

### Security by Design
Build security into systems from the ground up:
- Threat modeling during design phase
- Security requirements as first-class requirements
- Secure defaults and configurations
- Fail securely (deny by default)
- Regular security reviews and updates

### Principle of Least Privilege
Grant minimum necessary permissions:
- Role-based access control with minimal roles
- Time-bound access (temporary elevation)
- Regular permission audits and reviews
- Separate duties and responsibilities
- Avoid overly permissive wildcard permissions

## Cloud Security Frameworks

### NIST Cybersecurity Framework
Five core functions:
1. **Identify**: Asset management, risk assessment, governance
2. **Protect**: Access control, data security, protective technology
3. **Detect**: Anomalies, continuous monitoring, detection processes
4. **Respond**: Response planning, communications, analysis, mitigation
5. **Recover**: Recovery planning, improvements, communications

### CIS Controls v8
20 critical security controls organized into:
- **Basic**: Foundational security hygiene
- **Foundational**: Building comprehensive security
- **Organizational**: Organization-wide security practices

### OWASP Cloud-Native Application Security Top 10
1. Insecure cloud, container, or orchestration configuration
2. Injection flaws (application layer, cloud events, cloud services)
3. Improper authentication & authorization
4. CI/CD pipeline & software supply chain flaws
5. Insecure secrets storage
6. Over-permissive or insecure network policies
7. Using components with known vulnerabilities
8. Improper assets management
9. Inadequate compute resource quota limits
10. Ineffective logging & monitoring (e.g., runtime activity)

## Security Best Practices by Cloud Provider

### AWS Security Best Practices
- Enable AWS Organizations and Service Control Policies (SCPs)
- Use AWS IAM Identity Center (formerly SSO) for human access
- Enable MFA for root account and protect root credentials
- Use IAM roles for EC2 instances and Lambda functions
- Enable CloudTrail in all regions and protect logs
- Use AWS Config for configuration management
- Enable GuardDuty for threat detection
- Implement S3 bucket encryption and block public access
- Use VPC endpoints for AWS service access
- Enable VPC Flow Logs for network visibility

### Azure Security Best Practices
- Use Azure AD (Entra ID) for identity management
- Implement Conditional Access policies
- Enable Azure AD Privileged Identity Management (PIM)
- Use Managed Identities for Azure resources
- Enable Azure Activity Logs and Azure Monitor
- Use Azure Policy for governance and compliance
- Enable Microsoft Defender for Cloud (formerly Security Center)
- Implement network security groups (NSGs) and Azure Firewall
- Use Private Endpoints for Azure services
- Enable Azure Key Vault for secrets management

### GCP Security Best Practices
- Use Google Cloud Identity for user management
- Implement Organization Policies for governance
- Enable VPC Service Controls for data exfiltration protection
- Use Workload Identity for GKE pods
- Enable Cloud Audit Logs in all projects
- Use Security Command Center for security posture
- Implement VPC firewall rules with priority-based ordering
- Use Private Google Access for API access from VMs
- Enable Cloud Key Management Service (Cloud KMS)
- Implement Binary Authorization for container deployment

## Security Metrics and KPIs

### Key Security Metrics
- **Mean Time to Detect (MTTD)**: Average time to detect security incidents
- **Mean Time to Respond (MTTR)**: Average time to respond and remediate
- **Vulnerability Density**: Number of vulnerabilities per asset
- **Patch Compliance**: Percentage of systems with current patches
- **Security Finding Remediation Time**: Time to fix security findings
- **Failed Login Attempts**: Indicator of potential attacks
- **Privilege Escalation Events**: Unauthorized elevation attempts
- **Data Exfiltration Attempts**: Unusual data transfer patterns

### Compliance Metrics
- Compliance score (percentage of controls met)
- Audit findings and remediation status
- Policy violations and exceptions
- Security training completion rates
- Access review completion rates

## Common Cloud Security Risks

### Top Cloud Security Threats (CSA)
1. **Data Breaches**: Unauthorized access to sensitive data
2. **Misconfiguration and Inadequate Change Control**: Improperly configured cloud resources
3. **Lack of Cloud Security Architecture and Strategy**: No comprehensive security approach
4. **Insufficient Identity, Credential, Access, and Key Management**: Weak IAM practices
5. **Account Hijacking**: Compromised user credentials
6. **Insider Threat**: Malicious or negligent insiders
7. **Insecure Interfaces and APIs**: Vulnerable cloud service interfaces
8. **Weak Control Plane**: Inadequate management of cloud resources
9. **Metastructure and Applistructure Failures**: Infrastructure and application layer issues
10. **Limited Cloud Usage Visibility**: Lack of visibility into cloud consumption

### Common Misconfigurations
- Publicly accessible storage buckets (S3, Blob Storage, Cloud Storage)
- Overly permissive security groups (0.0.0.0/0 access)
- Disabled logging and monitoring
- Unencrypted data at rest
- Missing MFA on privileged accounts
- Unused or orphaned resources
- Excessive IAM permissions
- Exposed secrets in code or configuration
- Unpatched vulnerabilities
- Disabled security features

## Security Tools and Services

### Cloud-Native Security Services
**AWS**:
- AWS IAM, AWS Organizations, IAM Identity Center
- AWS KMS, AWS Secrets Manager
- AWS Security Hub, AWS GuardDuty, AWS Inspector
- AWS WAF, AWS Shield, AWS Network Firewall
- AWS CloudTrail, AWS Config, Amazon Detective

**Azure**:
- Azure AD (Entra ID), Azure AD PIM
- Azure Key Vault
- Microsoft Defender for Cloud, Azure Sentinel
- Azure WAF, Azure DDoS Protection, Azure Firewall
- Azure Monitor, Azure Activity Logs, Azure Policy

**GCP**:
- Google Cloud IAM, Cloud Identity
- Cloud KMS, Secret Manager
- Security Command Center, Chronicle
- Cloud Armor, Cloud IDS
- Cloud Audit Logs, Cloud Logging, Cloud Monitoring

### Third-Party Security Tools
- **CSPM**: Prisma Cloud, Wiz, Orca Security, Lacework
- **CWPP**: Aqua Security, Sysdig, Palo Alto Prisma Cloud
- **SIEM/SOAR**: Splunk, Sumo Logic, Datadog Security
- **Secrets Management**: HashiCorp Vault, CyberArk
- **Container Security**: Snyk, Aqua, Twistlock
- **Policy as Code**: Open Policy Agent, HashiCorp Sentinel

## Practical Implementation Examples

### Example 1: Least Privilege IAM Policy (AWS)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ReadSpecificBucket",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-app-bucket",
        "arn:aws:s3:::my-app-bucket/*"
      ],
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": ["10.0.0.0/8"]
        }
      }
    },
    {
      "Sid": "AllowDynamoDBReadWrite",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/MyAppTable"
    }
  ]
}
```

### Example 2: Secure Security Group Configuration (AWS Terraform)

```hcl
# Application Load Balancer Security Group
resource "aws_security_group" "alb" {
  name_description = "Security group for ALB - only HTTPS from internet"
  vpc_id      = aws_vpc.main.id

  # HTTPS from internet
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS from internet"
  }

  # HTTP redirect (optional)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP redirect to HTTPS"
  }

  # Egress to application tier only
  egress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "To application tier"
  }

  tags = {
    Name        = "alb-sg"
    Environment = "production"
    Compliance  = "pci-dss"
  }
}

# Application Tier Security Group
resource "aws_security_group" "app" {
  name_description = "Security group for application tier"
  vpc_id      = aws_vpc.main.id

  # Only from ALB
  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "From ALB only"
  }

  # Egress to database tier only
  egress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.database.id]
    description     = "To database tier"
  }

  # HTTPS for external API calls
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS for external APIs"
  }

  tags = {
    Name        = "app-sg"
    Environment = "production"
  }
}

# Database Tier Security Group
resource "aws_security_group" "database" {
  name_description = "Security group for database tier"
  vpc_id      = aws_vpc.main.id

  # Only from application tier
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "PostgreSQL from app tier only"
  }

  # No egress needed for database
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound (for updates)"
  }

  tags = {
    Name        = "database-sg"
    Environment = "production"
  }
}
```

### Example 3: Encryption at Rest Configuration (AWS)

```python
import boto3
import json

def create_encrypted_s3_bucket(bucket_name, kms_key_id, region='us-east-1'):
    """
    Create S3 bucket with encryption, versioning, and public access block
    """
    s3_client = boto3.client('s3', region_name=region)

    # Create bucket
    if region == 'us-east-1':
        s3_client.create_bucket(Bucket=bucket_name)
    else:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )

    # Enable default encryption with KMS
    s3_client.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            'Rules': [{
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'aws:kms',
                    'KMSMasterKeyID': kms_key_id
                },
                'BucketKeyEnabled': True
            }]
        }
    )

    # Enable versioning
    s3_client.put_bucket_versioning(
        Bucket=bucket_name,
        VersioningConfiguration={'Status': 'Enabled'}
    )

    # Block all public access
    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )

    # Enable access logging
    s3_client.put_bucket_logging(
        Bucket=bucket_name,
        BucketLoggingStatus={
            'LoggingEnabled': {
                'TargetBucket': f'{bucket_name}-logs',
                'TargetPrefix': 'access-logs/'
            }
        }
    )

    # Add bucket policy requiring encryption
    bucket_policy = {
        'Version': '2012-10-17',
        'Statement': [{
            'Sid': 'DenyUnencryptedObjectUploads',
            'Effect': 'Deny',
            'Principal': '*',
            'Action': 's3:PutObject',
            'Resource': f'arn:aws:s3:::{bucket_name}/*',
            'Condition': {
                'StringNotEquals': {
                    's3:x-amz-server-side-encryption': 'aws:kms'
                }
            }
        }]
    }

    s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(bucket_policy)
    )

    print(f"Secure bucket {bucket_name} created successfully")
    return True

# Usage
kms_key_arn = 'arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012'
create_encrypted_s3_bucket('my-secure-app-bucket', kms_key_arn)
```

### Example 4: Secrets Management with AWS Secrets Manager

```python
import boto3
import json
from botocore.exceptions import ClientError

def store_database_credentials(secret_name, username, password, host, port=5432):
    """
    Store database credentials in AWS Secrets Manager with automatic rotation
    """
    secrets_client = boto3.client('secretsmanager', region_name='us-east-1')

    secret_value = {
        'username': username,
        'password': password,
        'engine': 'postgres',
        'host': host,
        'port': port,
        'dbname': 'production_db'
    }

    try:
        response = secrets_client.create_secret(
            Name=secret_name,
            Description='Production database credentials',
            SecretString=json.dumps(secret_value),
            Tags=[
                {'Key': 'Environment', 'Value': 'production'},
                {'Key': 'Application', 'Value': 'web-app'},
                {'Key': 'Compliance', 'Value': 'pci-dss'}
            ]
        )

        # Enable automatic rotation (requires Lambda function)
        secrets_client.rotate_secret(
            SecretId=secret_name,
            RotationLambdaARN='arn:aws:lambda:us-east-1:123456789012:function:RotateRDSSecret',
            RotationRules={'AutomaticallyAfterDays': 30}
        )

        print(f"Secret created: {response['ARN']}")
        return response['ARN']

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceExistsException':
            print(f"Secret {secret_name} already exists")
        raise

def retrieve_secret(secret_name):
    """
    Retrieve secret from AWS Secrets Manager
    """
    secrets_client = boto3.client('secretsmanager', region_name='us-east-1')

    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        return secret
    except ClientError as e:
        print(f"Error retrieving secret: {e}")
        raise

# Usage in application
def get_database_connection():
    """
    Get database connection using credentials from Secrets Manager
    """
    import psycopg2

    secret = retrieve_secret('prod/database/credentials')

    connection = psycopg2.connect(
        host=secret['host'],
        port=secret['port'],
        database=secret['dbname'],
        user=secret['username'],
        password=secret['password'],
        sslmode='require'
    )

    return connection
```

### Example 5: Security Scanning Automation

```python
import boto3
import json
from datetime import datetime

def scan_security_configuration():
    """
    Automated security configuration scanner
    """
    findings = []

    # Check S3 buckets
    s3_client = boto3.client('s3')
    buckets = s3_client.list_buckets()['Buckets']

    for bucket in buckets:
        bucket_name = bucket['Name']

        # Check encryption
        try:
            encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
        except:
            findings.append({
                'severity': 'HIGH',
                'resource': bucket_name,
                'issue': 'S3 bucket not encrypted',
                'remediation': 'Enable default encryption with KMS'
            })

        # Check public access block
        try:
            public_block = s3_client.get_public_access_block(Bucket=bucket_name)
            config = public_block['PublicAccessBlockConfiguration']
            if not all([config['BlockPublicAcls'], config['BlockPublicPolicy'],
                       config['IgnorePublicAcls'], config['RestrictPublicBuckets']]):
                findings.append({
                    'severity': 'CRITICAL',
                    'resource': bucket_name,
                    'issue': 'S3 bucket may allow public access',
                    'remediation': 'Enable all public access block settings'
                })
        except:
            findings.append({
                'severity': 'CRITICAL',
                'resource': bucket_name,
                'issue': 'No public access block configured',
                'remediation': 'Configure S3 public access block'
            })

    # Check EC2 security groups
    ec2_client = boto3.client('ec2')
    security_groups = ec2_client.describe_security_groups()['SecurityGroups']

    for sg in security_groups:
        for rule in sg['IpPermissions']:
            for ip_range in rule.get('IpRanges', []):
                if ip_range.get('CidrIp') == '0.0.0.0/0':
                    if rule.get('FromPort') not in [80, 443]:  # Allow HTTP/HTTPS
                        findings.append({
                            'severity': 'HIGH',
                            'resource': sg['GroupId'],
                            'issue': f"Security group allows port {rule.get('FromPort')} from 0.0.0.0/0",
                            'remediation': 'Restrict source IP ranges'
                        })

    # Check IAM users without MFA
    iam_client = boto3.client('iam')
    users = iam_client.list_users()['Users']

    for user in users:
        username = user['UserName']
        mfa_devices = iam_client.list_mfa_devices(UserName=username)['MFADevices']

        if not mfa_devices:
            findings.append({
                'severity': 'MEDIUM',
                'resource': username,
                'issue': 'IAM user without MFA enabled',
                'remediation': 'Enable MFA for this user'
            })

    # Generate report
    report = {
        'scan_time': datetime.now().isoformat(),
        'total_findings': len(findings),
        'critical': len([f for f in findings if f['severity'] == 'CRITICAL']),
        'high': len([f for f in findings if f['severity'] == 'HIGH']),
        'medium': len([f for f in findings if f['severity'] == 'MEDIUM']),
        'findings': findings
    }

    return report

# Run scan and send to SNS
def run_security_scan():
    report = scan_security_configuration()

    # Send to SNS if critical findings
    if report['critical'] > 0:
        sns_client = boto3.client('sns')
        sns_client.publish(
            TopicArn='arn:aws:sns:us-east-1:123456789012:security-alerts',
            Subject='CRITICAL: Security Configuration Issues Detected',
            Message=json.dumps(report, indent=2)
        )

    return report
```

### Example 6: Network Security with AWS Network Firewall (Terraform)

```hcl
resource "aws_networkfirewall_firewall_policy" "production" {
  name = "production-firewall-policy"

  firewall_policy {
    stateless_default_actions          = ["aws:forward_to_sfe"]
    stateless_fragment_default_actions = ["aws:forward_to_sfe"]

    stateful_rule_group_reference {
      resource_arn = aws_networkfirewall_rule_group.block_malicious_domains.arn
    }

    stateful_rule_group_reference {
      resource_arn = aws_networkfirewall_rule_group.allow_approved_domains.arn
    }
  }
}

resource "aws_networkfirewall_rule_group" "block_malicious_domains" {
  capacity = 100
  name     = "block-malicious-domains"
  type     = "STATEFUL"

  rule_group {
    rules_source {
      rules_source_list {
        generated_rules_type = "DENYLIST"
        target_types         = ["HTTP_HOST", "TLS_SNI"]
        targets              = [
          ".malicious-domain.com",
          ".phishing-site.net",
          "known-bad-actor.org"
        ]
      }
    }

    stateful_rule_options {
      rule_order = "STRICT_ORDER"
    }
  }
}

resource "aws_networkfirewall_rule_group" "allow_approved_domains" {
  capacity = 100
  name     = "allow-approved-domains"
  type     = "STATEFUL"

  rule_group {
    rules_source {
      stateful_rule {
        action = "PASS"
        header {
          destination      = "api.approved-service.com"
          destination_port = "443"
          direction        = "FORWARD"
          protocol         = "TCP"
          source           = "10.0.0.0/8"
          source_port      = "ANY"
        }
        rule_option {
          keyword = "sid:1"
        }
      }
    }
  }
}

resource "aws_networkfirewall_firewall" "production" {
  name                = "production-firewall"
  firewall_policy_arn = aws_networkfirewall_firewall_policy.production.arn
  vpc_id              = aws_vpc.main.id

  dynamic "subnet_mapping" {
    for_each = aws_subnet.firewall[*].id
    content {
      subnet_id = subnet_mapping.value
    }
  }

  tags = {
    Environment = "production"
    Compliance  = "pci-dss"
  }
}
```

### Example 7: CloudTrail Security Monitoring (Python)

```python
import boto3
import json
from datetime import datetime, timedelta

def monitor_security_events():
    """
    Monitor CloudTrail for security-related events
    """
    cloudtrail = boto3.client('cloudtrail')
    sns = boto3.client('sns')

    # Define critical events to monitor
    critical_events = [
        'DeleteBucket',
        'PutBucketPolicy',
        'DeleteDBInstance',
        'AuthorizeSecurityGroupIngress',
        'CreateAccessKey',
        'DeleteAccessKey',
        'PutUserPolicy',
        'AttachUserPolicy',
        'CreateRole',
        'PutRolePolicy',
        'UpdateAccountPasswordPolicy',
        'DeactivateMFADevice'
    ]

    # Look for events in last hour
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)

    alerts = []

    response = cloudtrail.lookup_events(
        StartTime=start_time,
        EndTime=end_time,
        MaxResults=50
    )

    for event in response['Events']:
        event_name = event['EventName']

        if event_name in critical_events:
            cloud_trail_event = json.loads(event['CloudTrailEvent'])

            # Check for root account usage
            if cloud_trail_event.get('userIdentity', {}).get('type') == 'Root':
                alerts.append({
                    'severity': 'CRITICAL',
                    'event': event_name,
                    'time': event['EventTime'].isoformat(),
                    'user': 'ROOT ACCOUNT',
                    'source_ip': cloud_trail_event.get('sourceIPAddress'),
                    'message': 'Root account used for API call'
                })

            # Check for console login without MFA
            if event_name == 'ConsoleLogin':
                mfa_used = cloud_trail_event.get('additionalEventData', {}).get('MFAUsed')
                if mfa_used != 'Yes':
                    alerts.append({
                        'severity': 'HIGH',
                        'event': event_name,
                        'time': event['EventTime'].isoformat(),
                        'user': cloud_trail_event.get('userIdentity', {}).get('userName'),
                        'source_ip': cloud_trail_event.get('sourceIPAddress'),
                        'message': 'Console login without MFA'
                    })

            # Check for failed authentication
            if cloud_trail_event.get('errorCode') in ['UnauthorizedOperation', 'AccessDenied']:
                alerts.append({
                    'severity': 'MEDIUM',
                    'event': event_name,
                    'time': event['EventTime'].isoformat(),
                    'user': cloud_trail_event.get('userIdentity', {}).get('userName'),
                    'source_ip': cloud_trail_event.get('sourceIPAddress'),
                    'message': 'Unauthorized API call attempted'
                })

    # Send alerts if any found
    if alerts:
        message = f"Security Events Detected:\n\n"
        for alert in alerts:
            message += f"[{alert['severity']}] {alert['event']}\n"
            message += f"  User: {alert['user']}\n"
            message += f"  IP: {alert['source_ip']}\n"
            message += f"  Time: {alert['time']}\n"
            message += f"  Details: {alert['message']}\n\n"

        sns.publish(
            TopicArn='arn:aws:sns:us-east-1:123456789012:security-alerts',
            Subject=f'Security Alert: {len(alerts)} events detected',
            Message=message
        )

    return alerts

# Lambda handler for scheduled execution
def lambda_handler(event, context):
    alerts = monitor_security_events()
    return {
        'statusCode': 200,
        'body': json.dumps({
            'alerts_found': len(alerts),
            'alerts': alerts
        })
    }
```

## Resources and References

### Official Documentation
- AWS Security Best Practices: https://aws.amazon.com/security/best-practices/
- Azure Security Documentation: https://docs.microsoft.com/azure/security/
- GCP Security Best Practices: https://cloud.google.com/security/best-practices

### Security Frameworks
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- CIS Benchmarks: https://www.cisecurity.org/cis-benchmarks/
- OWASP Cloud-Native Application Security: https://owasp.org/www-project-cloud-native-application-security-top-10/

### Industry Resources
- Cloud Security Alliance (CSA): https://cloudsecurityalliance.org/
- SANS Cloud Security: https://www.sans.org/cloud-security/
- MITRE ATT&CK Cloud Matrix: https://attack.mitre.org/matrices/enterprise/cloud/

### Compliance Resources
- SOC 2: https://www.aicpa.org/soc4so
- ISO 27001: https://www.iso.org/isoiec-27001-information-security.html
- PCI DSS: https://www.pcisecuritystandards.org/
- HIPAA: https://www.hhs.gov/hipaa/
- GDPR: https://gdpr.eu/
