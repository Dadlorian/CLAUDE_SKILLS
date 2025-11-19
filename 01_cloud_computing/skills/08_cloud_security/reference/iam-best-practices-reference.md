# Identity & Access Management (IAM) Best Practices Reference

## Introduction

Identity and Access Management (IAM) is the cornerstone of cloud security. This reference provides comprehensive best practices for implementing robust IAM controls across AWS, Azure, and GCP, covering authentication, authorization, and access governance.

## Core IAM Principles

### Principle of Least Privilege
Grant only the minimum permissions required to perform a task:
- Start with zero permissions and add only what's necessary
- Use managed policies over inline policies where possible
- Regularly review and remove unused permissions
- Implement time-bound access for elevated privileges
- Avoid wildcard (*) permissions in production

### Defense in Depth
Implement multiple layers of access controls:
- Multi-factor authentication (MFA)
- Network-based access controls (VPC, Private Endpoints)
- Resource-based policies in addition to identity-based
- Service Control Policies (SCPs) for organizational boundaries
- Permission boundaries to limit maximum permissions

### Separation of Duties
Divide responsibilities to prevent conflicts of interest:
- Separate administrative roles from operational roles
- Different roles for developers, operators, and auditors
- Break-glass procedures for emergency access
- No single person should have complete control

### Zero Trust Access
Never trust, always verify:
- Authenticate and authorize every request
- Verify identity, device, location, and context
- Continuous authentication and re-authorization
- Assume breach mentality in design

## AWS IAM Best Practices

### Root Account Security
- **Never use root account for daily operations**
- Enable MFA on root account (hardware MFA preferred)
- Delete root access keys if they exist
- Use AWS Organizations and SCPs to limit root account actions
- Secure root account email and password in a safe location
- Set up account contacts and alternative email

### Human User Access
- **Use AWS IAM Identity Center (formerly SSO)** for workforce users
- Integrate with corporate identity provider (Azure AD, Okta)
- Enable MFA for all users
- Use temporary credentials (no long-term access keys)
- Implement permission sets based on job functions
- Regular access reviews (quarterly recommended)

### Programmatic Access
- **Use IAM roles instead of access keys when possible**:
  - EC2 instance profiles for EC2 instances
  - IAM roles for Lambda functions
  - EKS IRSA (IAM Roles for Service Accounts) for Kubernetes pods
  - IAM roles for ECS tasks
- When access keys are necessary:
  - Rotate access keys every 90 days
  - Use AWS Secrets Manager for storage
  - Never embed in code or version control
  - Use different credentials per application

### IAM Policy Best Practices
**Structure and Organization**:
- Use managed policies over inline policies
- Create custom managed policies for common patterns
- Use policy versioning for change management
- Tag policies for organization and cost allocation

**Security**:
- Avoid wildcard (*) resources in production
- Use condition keys to restrict access:
  - `aws:SourceIp` for IP-based restrictions
  - `aws:MultiFactorAuthPresent` to require MFA
  - `aws:SecureTransport` to require HTTPS
  - `aws:PrincipalOrgID` to restrict to organization
- Use permission boundaries to set maximum permissions
- Implement service control policies (SCPs) for organization-wide limits

**Example Least Privilege S3 Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/app-data/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-server-side-encryption": "aws:kms"
        }
      }
    }
  ]
}
```

### Cross-Account Access
- Use IAM roles for cross-account access (never share credentials)
- Require external ID for third-party access
- Use AWS Organizations for multi-account management
- Implement SCPs to prevent privilege escalation
- Enable CloudTrail in all accounts for audit trail

### Service Accounts and Application Identity
- Use IAM roles for EC2 instances (instance profiles)
- Use IAM roles for AWS services (Lambda, ECS, EKS)
- Implement IRSA for Kubernetes workloads
- Use resource-based policies for service-to-service access
- Enable CloudTrail to track service account activities

## Azure IAM Best Practices

### Azure AD (Entra ID) Configuration
- **Enable Conditional Access policies**:
  - Require MFA for all users
  - Block legacy authentication protocols
  - Require compliant devices for access
  - Risk-based conditional access
- Use Azure AD Privileged Identity Management (PIM) for just-in-time access
- Enable Azure AD Identity Protection for risk detection
- Implement self-service password reset with MFA
- Regular Azure AD access reviews

### Role-Based Access Control (RBAC)
**Built-in Roles** (use when possible):
- Owner, Contributor, Reader (management plane)
- Specific service roles (e.g., Virtual Machine Contributor)
- Custom roles only when built-in roles don't fit

**Custom Role Best Practices**:
- Start with least privilege
- Use NotActions to exclude specific permissions
- Assign at appropriate scope (management group, subscription, resource group, resource)
- Document the purpose of custom roles
- Regular review and cleanup

**Example Custom Role**:
```json
{
  "Name": "Storage Account Key Operator",
  "Description": "Can list and regenerate storage account keys",
  "Actions": [
    "Microsoft.Storage/storageAccounts/listkeys/action",
    "Microsoft.Storage/storageAccounts/regeneratekey/action"
  ],
  "NotActions": [],
  "AssignableScopes": [
    "/subscriptions/{subscription-id}"
  ]
}
```

### Managed Identities
- **Use system-assigned managed identities** for single-resource scenarios
- **Use user-assigned managed identities** for multi-resource scenarios
- Never store credentials in code or configuration
- Use managed identities for:
  - VMs accessing Azure resources
  - App Service/Functions accessing Azure services
  - AKS pods accessing Azure resources (pod identity)
  - Logic Apps, Data Factory, etc.

### Service Principals
- Use managed identities instead of service principals when possible
- When service principals are necessary:
  - Use certificate-based authentication over passwords
  - Rotate credentials every 90 days
  - Store credentials in Azure Key Vault
  - Assign minimal RBAC permissions
  - Enable service principal sign-in logging

### Azure AD Application Registration
- Register applications in Azure AD
- Use different app registrations for dev/test/prod
- Implement least privilege for API permissions
- Use certificate credentials over client secrets
- Enable app consent policies
- Regular review of app permissions

### Privileged Identity Management (PIM)
- Enable PIM for all privileged roles
- Require justification for activation
- Require MFA for activation
- Set maximum activation duration (8 hours recommended)
- Enable approval workflows for critical roles
- Regular PIM access reviews
- Monitor PIM alerts and usage

## GCP IAM Best Practices

### Organization and Resource Hierarchy
- Use Organizations for centralized management
- Implement folder hierarchy for organizational structure
- Use projects for workload isolation
- Inherit policies from organization and folders
- Apply IAM policies at appropriate level

### Predefined Roles
**Primitive Roles** (avoid in production):
- Owner, Editor, Viewer (too broad)

**Predefined Roles** (use these):
- Service-specific roles (e.g., `roles/compute.instanceAdmin.v1`)
- Job function roles (e.g., `roles/iam.securityReviewer`)

**Custom Roles**:
- Create when predefined roles are too permissive
- Start with predefined role and remove permissions
- Use role recommendations from recommender
- Test in non-production first
- Regular review and updates

### Service Accounts
- **Use Workload Identity for GKE pods** (preferred)
- One service account per application/service
- Use short-lived service account tokens (not JSON keys)
- When keys are necessary:
  - Rotate every 90 days
  - Store in Secret Manager
  - Never commit to version control
- Use service account impersonation for admin tasks
- Disable unused service accounts

### Workload Identity Federation
- Use Workload Identity Federation for external workloads
- Avoid exporting service account keys
- Configure OIDC providers (AWS, Azure, GitHub Actions)
- Map external identities to GCP service accounts
- Implement attribute-based access control

### IAM Policy Best Practices
**Condition-Based Access**:
```yaml
bindings:
- role: roles/storage.objectViewer
  members:
  - user:alice@example.com
  condition:
    title: "Expire after 2025"
    expression: >
      request.time < timestamp("2025-01-01T00:00:00Z")
```

**Resource-Based Policies**:
- Use when access is resource-specific
- Combine with identity-based policies
- Use for cross-project access

### Organization Policies
- Enforce security controls organization-wide
- Common policies:
  - Disable service account key creation
  - Restrict public IP on VMs
  - Require VPC Service Controls
  - Domain restricted sharing
  - Uniform bucket-level access
- Use policy inheritance effectively
- Test policies in folders before org-wide rollout

### Context-Aware Access
- Define access levels based on:
  - IP address/CIDR ranges
  - Device policy compliance
  - Geographic location
  - Access time windows
- Apply access levels to resources
- Combine with IAM policies for defense-in-depth

## Multi-Cloud IAM Strategies

### Identity Federation
**SAML 2.0/OIDC Federation**:
- Use corporate IdP as single source of truth (Azure AD, Okta, Google Workspace)
- Configure SAML/OIDC federation in each cloud:
  - AWS: IAM Identity Center or IAM SAML providers
  - Azure: Native Azure AD integration
  - GCP: Cloud Identity or Workforce Identity Federation
- Map IdP groups to cloud roles
- Single sign-on (SSO) for all cloud platforms

**Cross-Cloud Workload Identity**:
- AWS → GCP: Workload Identity Federation with AWS OIDC
- Azure → AWS: OIDC federation with Azure AD
- GCP → AWS: Workload Identity Federation
- Avoid exporting long-term credentials

### Unified Access Control
- Centralized identity provider (Azure AD, Okta)
- Consistent role naming across clouds
- Centralized audit logging (SIEM)
- Unified access reviews and governance
- Common MFA enforcement

## Advanced IAM Patterns

### Just-in-Time (JIT) Access
**Implementation**:
- Azure: Azure AD PIM
- AWS: Custom solution with Step Functions + Lambda
- GCP: Custom solution with Cloud Scheduler + IAM API

**Benefits**:
- Reduced standing privileges
- Time-bound access (e.g., 4-hour elevation)
- Approval workflows for sensitive access
- Audit trail of privilege escalation

### Attribute-Based Access Control (ABAC)
**AWS ABAC with Tags**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "ec2:*",
    "Resource": "*",
    "Condition": {
      "StringEquals": {
        "ec2:ResourceTag/Owner": "${aws:username}",
        "ec2:ResourceTag/Environment": "dev"
      }
    }
  }]
}
```

**Benefits**:
- Scalable access control
- Dynamic permission assignment
- Reduced policy management overhead
- Fine-grained access based on attributes

### Break-Glass Access
**Purpose**: Emergency access when normal access paths fail

**Implementation**:
- Dedicated emergency accounts with strong credentials
- MFA required (hardware tokens in secure location)
- Highly restricted normal usage (SCPs, Conditional Access)
- Immediate alerting on use
- Mandatory post-use review and documentation
- Separate break-glass accounts per severity level

**Example AWS Break-Glass SCP**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*",
    "Condition": {
      "StringNotLike": {
        "aws:PrincipalArn": "arn:aws:iam::*:role/BreakGlass*"
      },
      "StringEquals": {
        "aws:RequestedRegion": "us-gov-east-1"
      }
    }
  }]
}
```

## IAM Security Monitoring

### Key Metrics to Track
- Failed login attempts (potential brute force)
- Successful logins from unusual locations
- Privilege escalation events
- Role/policy changes
- Creation of new users/service accounts
- Access key age and usage
- MFA compliance rate
- Unused credentials (90+ days)

### AWS Monitoring
- Enable CloudTrail in all regions
- Monitor IAM Access Analyzer findings
- Use AWS Config Rules:
  - `iam-user-mfa-enabled`
  - `iam-root-access-key-check`
  - `iam-password-policy`
  - `access-keys-rotated`
- Set up EventBridge rules for critical IAM events
- Use AWS Security Hub for aggregated findings

### Azure Monitoring
- Enable Azure Activity Logs
- Configure Azure AD sign-in logs and audit logs
- Use Azure Sentinel for SIEM
- Azure AD Identity Protection risk events
- Azure AD Conditional Access insights
- Monitor PIM activations and approvals

### GCP Monitoring
- Enable Cloud Audit Logs (Admin, Data Access, System Event)
- Use Security Command Center for IAM insights
- Monitor IAM policy changes via Cloud Logging
- Set up log-based metrics and alerts
- Use Access Transparency logs (for Google support access)

## IAM Access Reviews

### Review Frequency
- **Critical/Production**: Monthly
- **Standard**: Quarterly
- **Low-Risk**: Annually
- **After Incidents**: Immediately

### Review Process
1. **Inventory**: List all identities and their permissions
2. **Validate**: Confirm each identity still requires access
3. **Assess**: Evaluate if permissions are still appropriate
4. **Remediate**: Remove/reduce unnecessary permissions
5. **Document**: Record review results and actions
6. **Automate**: Use cloud-native tools where possible

### Automation Tools
- **AWS**: IAM Access Analyzer, AWS Config, custom Lambda functions
- **Azure**: Azure AD Access Reviews, PIM reviews
- **GCP**: IAM Recommender, Cloud Asset Inventory

## Common IAM Anti-Patterns to Avoid

### Anti-Pattern 1: Shared Credentials
**Problem**: Multiple users sharing one set of credentials
**Solution**: Individual user accounts with appropriate roles

### Anti-Pattern 2: Long-Lived Credentials
**Problem**: Access keys or passwords never rotated
**Solution**: Temporary credentials, automatic rotation, roles

### Anti-Pattern 3: Overly Permissive Policies
**Problem**: Using wildcards (*) for actions and resources
**Solution**: Specific permissions, least privilege, gradual expansion

### Anti-Pattern 4: Inline Policies Everywhere
**Problem**: Difficult to manage, audit, and reuse
**Solution**: Managed policies, policy reuse, centralized management

### Anti-Pattern 5: No MFA Enforcement
**Problem**: Username/password only authentication
**Solution**: Mandatory MFA for all users, conditional access

### Anti-Pattern 6: Hardcoded Credentials
**Problem**: Credentials in code, config files, environment variables
**Solution**: Secrets management, IAM roles, managed identities

### Anti-Pattern 7: Admin Rights by Default
**Problem**: Developers with full admin access
**Solution**: Least privilege, JIT access, separation of duties

### Anti-Pattern 8: No Access Reviews
**Problem**: Permissions accumulate over time (privilege creep)
**Solution**: Regular access reviews, automated cleanup

## IAM Testing and Validation

### Policy Validation
- **AWS IAM Policy Simulator**: Test policies before deployment
- **Azure ARM "What-If" Operations**: Preview policy effects
- **GCP Policy Simulator**: Test IAM condition expressions
- **Open Policy Agent (OPA)**: Test policies as code

### Penetration Testing
- Attempt privilege escalation (authorized testing only)
- Test for lateral movement opportunities
- Validate MFA enforcement
- Test break-glass procedures
- Validate cross-account access restrictions

### Compliance Validation
- CIS Benchmark automated scanning
- SOC 2 control validation
- PCI DSS IAM requirements
- HIPAA access control requirements
- GDPR data access controls

## Resources and Tools

### AWS IAM Resources
- IAM Policy Simulator: https://policysim.aws.amazon.com/
- IAM Access Analyzer: AWS Console → IAM → Access analyzer
- CloudTrail Lake: Advanced CloudTrail querying
- IAM Credential Reports: User credential status

### Azure IAM Resources
- Azure AD Privileged Identity Management (PIM)
- Azure AD Identity Protection
- Azure AD Access Reviews
- Conditional Access Policy templates
- Azure AD sign-in and audit logs

### GCP IAM Resources
- IAM Recommender: Permission recommendations
- Policy Analyzer: Policy analysis and testing
- Security Command Center: IAM insights
- Cloud Asset Inventory: Resource and IAM inventory
- Policy Troubleshooter: Debug access issues

### Third-Party Tools
- **Terraform**: IAM as code for all three clouds
- **Pulumi**: Infrastructure and IAM as code
- **Cloud Custodian**: Policy-based IAM management
- **Prowler**: Multi-cloud security assessment (includes IAM)
- **ScoutSuite**: Multi-cloud security auditing

## Compliance Mapping

### SOC 2 IAM Controls
- Access provisioning and deprovisioning (CC6.2)
- Authentication and MFA (CC6.1)
- Authorization (CC6.3)
- Access reviews (CC6.3)
- Audit logging (CC7.2)

### ISO 27001 IAM Controls
- A.9.1 Access control policy
- A.9.2 User access management
- A.9.4 System and application access control
- A.18.1.4 Privacy and protection of personal data

### PCI DSS IAM Requirements
- Requirement 7: Restrict access to cardholder data
- Requirement 8: Identify and authenticate access
- Requirement 10: Track and monitor all access

### HIPAA IAM Requirements
- 164.308(a)(3) Workforce security
- 164.308(a)(4) Access management
- 164.312(a)(1) Access controls
- 164.312(d) Person or entity authentication
