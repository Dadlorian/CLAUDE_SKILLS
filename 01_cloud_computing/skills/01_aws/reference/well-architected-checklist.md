# AWS Well-Architected Framework Checklist

## Overview

The AWS Well-Architected Framework helps you understand the pros and cons of decisions you make while building systems on AWS. The framework consists of six pillars.

## Operational Excellence

### Design Principles
- Perform operations as code
- Make frequent, small, reversible changes
- Refine operations procedures frequently
- Anticipate failure
- Learn from all operational failures

### Best Practices Checklist

**Organization**
- [ ] Documented team priorities and goals
- [ ] Defined operational model (DevOps, SRE, etc.)
- [ ] Clear roles and responsibilities
- [ ] Internal standards for workload architecture
- [ ] Regular review and improvement processes

**Prepare**
- [ ] Infrastructure as Code for all resources (CloudFormation/Terraform)
- [ ] Automated testing in CI/CD pipeline
- [ ] Runbooks for routine operations
- [ ] Playbooks for incident response
- [ ] Game days and chaos engineering practiced
- [ ] Deployment strategies defined (blue/green, canary)
- [ ] Rollback procedures documented and tested

**Operate**
- [ ] Automated monitoring and alerting configured
- [ ] CloudWatch dashboards for key metrics
- [ ] Centralized logging (CloudWatch Logs, S3)
- [ ] Distributed tracing (X-Ray) implemented
- [ ] On-call rotation and escalation defined
- [ ] Incident management process documented
- [ ] Change management process in place

**Evolve**
- [ ] Regular post-incident reviews
- [ ] Metrics for operational success defined
- [ ] Continuous improvement backlog maintained
- [ ] Knowledge sharing processes (wikis, docs)
- [ ] Regular training and skill development

**AWS Services:**
- CloudFormation, CDK, Terraform
- CodePipeline, CodeBuild, CodeDeploy
- CloudWatch, X-Ray, EventBridge
- Systems Manager, Config, Service Catalog

## Security

### Design Principles
- Implement a strong identity foundation
- Enable traceability
- Apply security at all layers
- Automate security best practices
- Protect data in transit and at rest
- Keep people away from data
- Prepare for security events

### Best Practices Checklist

**Identity and Access Management**
- [ ] Root account MFA enabled
- [ ] Root account not used for daily operations
- [ ] IAM users with individual accounts (no sharing)
- [ ] MFA enabled for privileged users
- [ ] Least privilege access policies
- [ ] IAM roles used instead of access keys
- [ ] Regular access key rotation
- [ ] Password policy enforced
- [ ] AWS Organizations for multi-account management
- [ ] Service Control Policies (SCPs) implemented
- [ ] IAM Access Analyzer enabled

**Detection**
- [ ] CloudTrail enabled in all regions
- [ ] CloudTrail log file validation enabled
- [ ] CloudWatch Logs for CloudTrail
- [ ] GuardDuty enabled for threat detection
- [ ] Security Hub for centralized findings
- [ ] Config rules for compliance monitoring
- [ ] VPC Flow Logs enabled
- [ ] AWS Macie for data classification (if applicable)

**Infrastructure Protection**
- [ ] VPCs with public/private subnet design
- [ ] Security groups follow least privilege
- [ ] Network ACLs configured appropriately
- [ ] NAT Gateways in each AZ
- [ ] VPC endpoints for AWS services
- [ ] WAF protecting web applications
- [ ] Shield Standard enabled (automatic)
- [ ] Shield Advanced for DDoS protection (if needed)
- [ ] Firewall Manager for centralized rules

**Data Protection**
- [ ] Data classified by sensitivity level
- [ ] Encryption at rest for all sensitive data
- [ ] KMS for encryption key management
- [ ] S3 bucket encryption enabled
- [ ] EBS volumes encrypted
- [ ] RDS encryption enabled
- [ ] Encryption in transit (TLS/SSL)
- [ ] S3 bucket policies prevent public access
- [ ] S3 versioning enabled for critical buckets
- [ ] S3 Object Lock for compliance (if needed)
- [ ] Secrets Manager for credentials
- [ ] Parameter Store for configuration

**Incident Response**
- [ ] Incident response plan documented
- [ ] Forensics capabilities prepared
- [ ] Automated incident response (EventBridge + Lambda)
- [ ] Security incident simulation exercises
- [ ] Backup and restore procedures tested

**AWS Services:**
- IAM, Organizations, SSO, Cognito
- CloudTrail, GuardDuty, Security Hub, Macie
- KMS, Secrets Manager, Certificate Manager
- WAF, Shield, Firewall Manager
- VPC, Security Groups, Network ACLs

## Reliability

### Design Principles
- Automatically recover from failure
- Test recovery procedures
- Scale horizontally for availability
- Stop guessing capacity
- Manage change in automation

### Best Practices Checklist

**Foundations**
- [ ] Service quotas monitored and increased as needed
- [ ] Network topology supports HA requirements
- [ ] Appropriate AWS account structure
- [ ] Connectivity to AWS and internet is reliable
- [ ] Disaster recovery requirements defined (RTO/RPO)

**Workload Architecture**
- [ ] Multi-AZ deployment (minimum 3 AZs)
- [ ] Stateless application design
- [ ] Loosely coupled components
- [ ] Service-oriented architecture or microservices
- [ ] Auto Scaling groups configured
- [ ] Load balancers distributing traffic
- [ ] Health checks implemented
- [ ] Circuit breakers and retries implemented
- [ ] Graceful degradation strategies

**Change Management**
- [ ] Automated deployment pipelines
- [ ] Blue/green or canary deployments
- [ ] Feature flags for gradual rollout
- [ ] Automated rollback on failure
- [ ] Infrastructure changes via IaC only
- [ ] Change windows for risky operations
- [ ] Capacity planning processes

**Failure Management**
- [ ] Regular backup automation
- [ ] Backup restoration tested regularly
- [ ] Multi-region strategy for DR (if needed)
- [ ] Chaos engineering practiced
- [ ] Failure modes identified and mitigated
- [ ] SLO/SLA defined and monitored
- [ ] Runbooks for common failures
- [ ] Dead letter queues for failed messages
- [ ] Data durability strategies (replication, backup)

**AWS Services:**
- Auto Scaling, ELB, Route 53
- Multi-AZ RDS, Aurora Global Database
- S3 Cross-Region Replication, S3 Glacier
- Lambda, Step Functions, SQS, SNS
- Backup, CloudEndure

## Performance Efficiency

### Design Principles
- Democratize advanced technologies
- Go global in minutes
- Use serverless architectures
- Experiment more often
- Consider mechanical sympathy

### Best Practices Checklist

**Selection**
- [ ] Compute: Right instance types selected
- [ ] Compute: Graviton evaluated for better price-performance
- [ ] Compute: Spot instances for fault-tolerant workloads
- [ ] Compute: Lambda for event-driven workloads
- [ ] Storage: Appropriate storage type for access patterns
- [ ] Storage: S3 Intelligent-Tiering for unknown patterns
- [ ] Database: Right database engine for use case
- [ ] Database: Read replicas for read-heavy workloads
- [ ] Network: CloudFront for global content delivery
- [ ] Network: VPC endpoints to avoid internet egress

**Review**
- [ ] Architecture reviewed quarterly
- [ ] New AWS services evaluated
- [ ] Performance benchmarks established
- [ ] Load testing performed regularly
- [ ] CloudWatch metrics analyzed
- [ ] Cost Explorer reviewed for optimization

**Monitoring**
- [ ] Performance metrics defined and tracked
- [ ] CloudWatch alarms for performance degradation
- [ ] X-Ray for application tracing
- [ ] CloudWatch Synthetics for endpoint monitoring
- [ ] Performance dashboards created
- [ ] Automated remediation for issues

**Tradeoffs**
- [ ] Caching layers implemented (CloudFront, ElastiCache, DAX)
- [ ] Read replicas for database scaling
- [ ] Async processing where appropriate (SQS, SNS)
- [ ] Eventual consistency acceptable where possible
- [ ] Compression enabled for data transfer
- [ ] Connection pooling implemented

**AWS Services:**
- EC2, Lambda, ECS, EKS, Fargate
- S3, EBS, EFS, FSx
- RDS, Aurora, DynamoDB, ElastiCache, Redshift
- CloudFront, Global Accelerator, Route 53
- CloudWatch, X-Ray, Compute Optimizer

## Cost Optimization

### Design Principles
- Implement Cloud Financial Management
- Adopt a consumption model
- Measure overall efficiency
- Stop spending on undifferentiated heavy lifting
- Analyze and attribute expenditure

### Best Practices Checklist

**Practice Cloud Financial Management**
- [ ] Cost allocation tags strategy implemented
- [ ] Cost and usage reports configured
- [ ] Billing alerts configured
- [ ] AWS Budgets created
- [ ] Cost anomaly detection enabled
- [ ] Regular cost reviews scheduled
- [ ] Showback/chargeback implemented

**Expenditure and Usage Awareness**
- [ ] CloudWatch billing metrics monitored
- [ ] Cost Explorer used for analysis
- [ ] Service quotas align with needs
- [ ] Unused resources identified and removed
- [ ] Resource inventory maintained
- [ ] Rightsizing recommendations reviewed
- [ ] Trusted Advisor checks enabled

**Cost-Effective Resources**
- [ ] Instances right-sized based on utilization
- [ ] Reserved Instances for steady workloads
- [ ] Savings Plans evaluated and purchased
- [ ] Spot Instances for fault-tolerant workloads
- [ ] Graviton instances evaluated
- [ ] Appropriate storage classes selected
- [ ] S3 lifecycle policies configured
- [ ] EBS snapshots managed (delete old)
- [ ] Unattached EBS volumes deleted
- [ ] Old AMIs deregistered
- [ ] Elastic IPs released when not in use

**Manage Demand and Supply**
- [ ] Auto Scaling configured
- [ ] Buffer/throttle requests to smooth demand
- [ ] Reserved capacity for predictable loads
- [ ] Dynamic pricing for customer demand shaping

**Optimize Over Time**
- [ ] Regular architecture reviews
- [ ] New AWS services evaluated for cost savings
- [ ] Compute Optimizer recommendations reviewed
- [ ] Cost optimization backlog maintained
- [ ] Migration to managed services considered
- [ ] Serverless options evaluated

**AWS Services:**
- Cost Explorer, Budgets, Cost and Usage Reports
- Compute Optimizer, Trusted Advisor
- Auto Scaling, Lambda, Fargate
- S3 Intelligent-Tiering, S3 Glacier
- Reserved Instances, Savings Plans, Spot

## Sustainability

### Design Principles
- Understand your impact
- Establish sustainability goals
- Maximize utilization
- Anticipate and adopt efficient hardware and software
- Use managed services
- Reduce downstream impact

### Best Practices Checklist

**Region Selection**
- [ ] Regions selected based on carbon footprint data
- [ ] User proximity considered to reduce network traffic
- [ ] Multi-region only when required

**User Behavior Patterns**
- [ ] Usage patterns analyzed
- [ ] Underutilized resources identified
- [ ] Scale infrastructure with demand
- [ ] Off-peak schedules for dev/test environments

**Software and Architecture**
- [ ] Efficient algorithms implemented
- [ ] Code optimized for performance
- [ ] Modern programming languages considered
- [ ] Managed services used where possible
- [ ] Serverless architectures adopted
- [ ] Graviton processors evaluated
- [ ] Minimal data movement between services

**Data**
- [ ] Data classification implemented
- [ ] Data lifecycle policies configured
- [ ] Unnecessary data deleted
- [ ] Deduplication and compression used
- [ ] Data storage optimized for access patterns
- [ ] Replication only when necessary

**Hardware and Services**
- [ ] Latest instance generations used
- [ ] Graviton instances for better efficiency
- [ ] Managed services preferred over self-managed
- [ ] Serverless options evaluated
- [ ] Right-sized resources
- [ ] GPU instances only when needed

**Development and Deployment**
- [ ] Infrastructure as Code to avoid drift
- [ ] Automated testing to reduce rework
- [ ] Blue/green deployments to reduce waste
- [ ] Feature flags to avoid rebuilds
- [ ] Efficient CI/CD pipelines

**AWS Services:**
- Graviton-based instances
- Lambda, Fargate (serverless)
- Auto Scaling, Compute Optimizer
- S3 Lifecycle, Intelligent-Tiering
- Customer Carbon Footprint Tool

## Review Process

### Well-Architected Tool
```bash
# Use AWS Well-Architected Tool for guided review
aws wellarchitected list-workloads

aws wellarchitected create-workload \
    --workload-name "MyApplication" \
    --description "Production web application" \
    --environment PRODUCTION \
    --lenses "wellarchitected" \
    --aws-regions "us-east-1"

# Answer questions and get improvement plan
```

### Review Schedule
- [ ] Initial architecture review before launch
- [ ] Review after significant changes
- [ ] Quarterly reviews for active workloads
- [ ] Annual comprehensive reviews
- [ ] Post-incident reviews
- [ ] Review when adopting new AWS services

### Documentation
- [ ] Architecture diagrams maintained
- [ ] Decision log for significant choices
- [ ] Risk register updated
- [ ] Improvement backlog prioritized
- [ ] Review findings tracked to completion

## Scoring

For each pillar, track:
- **High Risk**: 0-33% of best practices implemented
- **Medium Risk**: 34-66% of best practices implemented
- **Low Risk**: 67-100% of best practices implemented

Target: All pillars in Low Risk category

## Resources

- AWS Well-Architected Framework Whitepaper
- AWS Well-Architected Tool
- AWS Well-Architected Labs
- AWS Architecture Center
- Pillar-specific whitepapers and best practice guides

This comprehensive checklist helps ensure AWS workloads follow best practices across all six pillars of the Well-Architected Framework.
