# AWS Security Best Practices Checklist

## IAM

- [ ] Root account MFA enabled
- [ ] Root access keys deleted
- [ ] IAM password policy enforced (14+ chars, complexity)
- [ ] IAM users have MFA enabled
- [ ] No hardcoded credentials in code
- [ ] Least privilege IAM policies
- [ ] IAM roles used for EC2/Lambda (not access keys)
- [ ] Regular access key rotation
- [ ] Unused credentials removed
- [ ] CloudTrail enabled for IAM events

## S3

- [ ] Block all public access enabled (account-level)
- [ ] Bucket policies enforce encryption
- [ ] Versioning enabled for critical buckets
- [ ] Server-side encryption enabled (SSE-S3 or SSE-KMS)
- [ ] Bucket logging enabled
- [ ] MFA Delete enabled for critical buckets
- [ ] Object Lock for compliance data
- [ ] Lifecycle policies configured
- [ ] Access Analyzer enabled

## EC2

- [ ] Security groups follow least privilege
- [ ] No 0.0.0.0/0 inbound rules (except load balancers)
- [ ] SSH key pairs rotated regularly
- [ ] IMDSv2 enforced (disable IMDSv1)
- [ ] EBS encryption enabled by default
- [ ] Patch management automated (SSM Patch Manager)
- [ ] Instance profiles used (not IAM user keys)
- [ ] Detailed monitoring enabled

## VPC

- [ ] VPC Flow Logs enabled
- [ ] Network ACLs configured
- [ ] Private subnets for databases/apps
- [ ] NAT Gateway for outbound traffic
- [ ] VPC endpoints for AWS services
- [ ] Transit Gateway for multi-VPC
- [ ] Security groups documented

## Database (RDS)

- [ ] Encryption at rest enabled
- [ ] Encryption in transit enforced (SSL/TLS)
- [ ] Automated backups enabled
- [ ] Multi-AZ for production
- [ ] Database in private subnet
- [ ] IAM database authentication enabled
- [ ] Enhanced monitoring enabled
- [ ] Performance Insights enabled
- [ ] Deletion protection enabled

## Logging & Monitoring

- [ ] CloudTrail enabled (all regions)
- [ ] CloudTrail log validation enabled
- [ ] CloudWatch Logs encryption enabled
- [ ] GuardDuty enabled
- [ ] Security Hub enabled
- [ ] Config enabled and recording
- [ ] EventBridge rules for security events
- [ ] SNS topics for critical alerts

## Lambda

- [ ] Execution role with least privilege
- [ ] Environment variables encrypted (KMS)
- [ ] VPC configuration if accessing private resources
- [ ] Reserved concurrency set
- [ ] CloudWatch Logs enabled
- [ ] X-Ray tracing enabled
- [ ] Code signing enabled
- [ ] Secrets in Secrets Manager (not env vars)

## KMS

- [ ] CMKs for sensitive data
- [ ] Key rotation enabled
- [ ] Key policies restrict access
- [ ] CloudTrail logging of key usage
- [ ] Separate keys per environment

## WAF

- [ ] Deployed on ALB/CloudFront
- [ ] Rate-based rules configured
- [ ] IP blocklist/allowlist
- [ ] Managed rule groups enabled
- [ ] Custom rules for application
- [ ] Logging enabled

## Cost & Compliance

- [ ] Budgets and alerts configured
- [ ] Trusted Advisor checks reviewed
- [ ] Resource tagging strategy
- [ ] Compliance framework selected (CIS, PCI, etc.)
- [ ] Automated compliance scanning
