# IAM Policies Reference

## IAM Core Components

### Identity Types
- **Users**: Individual person or service
- **Groups**: Collection of users
- **Roles**: Assumed by users, services, or external identities
- **Policies**: JSON documents defining permissions

### Policy Types
1. **Identity-based**: Attached to users, groups, or roles
2. **Resource-based**: Attached to resources (S3 buckets, SQS queues)
3. **Permissions boundaries**: Maximum permissions for identity
4. **Service Control Policies (SCPs)**: Organization-wide restrictions
5. **Session policies**: Temporary session constraints

## Policy Structure

### Basic Policy Syntax
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "UniqueStatementId",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::123456789012:user/alice"},
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalTag/Department": "Engineering"
        }
      }
    }
  ]
}
```

### Elements Explained

**Version**: Policy language version (always use "2012-10-17")

**Statement**: Array of permission statements

**Sid**: Optional statement identifier

**Effect**: "Allow" or "Deny"

**Principal**: Who the policy applies to (resource-based only)
```json
"Principal": {
  "AWS": "arn:aws:iam::123456789012:root",
  "Service": "lambda.amazonaws.com",
  "Federated": "arn:aws:iam::123456789012:saml-provider/ExampleProvider",
  "CanonicalUser": "79a59df900b949e55d96a1e698fbacedfd6e09d98eacf8f8d5218e7cd47ef2be"
}

// Wildcard
"Principal": "*"

// Multiple principals
"Principal": {
  "AWS": [
    "arn:aws:iam::123456789012:user/alice",
    "arn:aws:iam::123456789012:user/bob"
  ]
}
```

**Action**: API operations allowed or denied
```json
// Single action
"Action": "s3:GetObject"

// Multiple actions
"Action": ["s3:GetObject", "s3:PutObject"]

// Wildcard
"Action": "s3:*"
"Action": "s3:Get*"

// All actions
"Action": "*"
```

**Resource**: ARN of resources affected
```json
// Specific resource
"Resource": "arn:aws:s3:::my-bucket/documents/*"

// Multiple resources
"Resource": [
  "arn:aws:s3:::bucket1/*",
  "arn:aws:s3:::bucket2/*"
]

// Wildcard
"Resource": "arn:aws:s3:::*"

// All resources
"Resource": "*"
```

**NotAction**, **NotResource**: Inverse matching (use carefully)

## Common Policy Patterns

### 1. Read-Only Access
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:Get*",
      "s3:List*",
      "s3:Describe*"
    ],
    "Resource": "*"
  }]
}
```

### 2. Admin Access to Specific Service
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "ec2:*",
    "Resource": "*"
  }]
}
```

### 3. Resource-Specific Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:Query"
    ],
    "Resource": [
      "arn:aws:dynamodb:us-east-1:123456789012:table/UserData",
      "arn:aws:dynamodb:us-east-1:123456789012:table/UserData/index/*"
    ]
  }]
}
```

### 4. Deny Override (Explicit Deny)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*"
    },
    {
      "Effect": "Deny",
      "Action": [
        "s3:DeleteBucket",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::critical-data/*"
    }
  ]
}
```

### 5. Multi-Factor Authentication Requirement
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*",
    "Condition": {
      "BoolIfExists": {"aws:MultiFactorAuthPresent": "false"}
    }
  }]
}
```

## Policy Conditions

### String Conditions
```json
"Condition": {
  "StringEquals": {"aws:PrincipalTag/Department": "Finance"},
  "StringLike": {"s3:prefix": ["documents/*", "reports/*"]},
  "StringNotEquals": {"aws:SourceVpce": "vpce-12345"}
}
```

### Numeric Conditions
```json
"Condition": {
  "NumericLessThan": {"aws:MultiFactorAuthAge": "3600"},
  "NumericGreaterThan": {"s3:max-keys": "10"}
}
```

### Date Conditions
```json
"Condition": {
  "DateGreaterThan": {"aws:CurrentTime": "2024-01-01T00:00:00Z"},
  "DateLessThan": {"aws:CurrentTime": "2024-12-31T23:59:59Z"}
}
```

### IP Address Conditions
```json
"Condition": {
  "IpAddress": {
    "aws:SourceIp": ["203.0.113.0/24", "198.51.100.0/24"]
  },
  "NotIpAddress": {
    "aws:SourceIp": "192.0.2.0/24"
  }
}
```

### ARN Conditions
```json
"Condition": {
  "ArnLike": {
    "aws:SourceArn": "arn:aws:s3:::my-bucket/*"
  }
}
```

### Boolean Conditions
```json
"Condition": {
  "Bool": {
    "aws:SecureTransport": "true",
    "aws:MultiFactorAuthPresent": "true"
  }
}
```

### Existence Conditions
```json
"Condition": {
  "Null": {
    "aws:PrincipalTag/Department": "false"
  }
}
```

## Advanced Patterns

### 1. Tag-Based Access Control (ABAC)
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ec2:StartInstances",
      "ec2:StopInstances"
    ],
    "Resource": "arn:aws:ec2:*:*:instance/*",
    "Condition": {
      "StringEquals": {
        "ec2:ResourceTag/Owner": "${aws:username}",
        "ec2:ResourceTag/Environment": "${aws:PrincipalTag/Environment}"
      }
    }
  }]
}
```

### 2. Prevent Unencrypted Uploads
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:PutObject",
    "Resource": "arn:aws:s3:::my-bucket/*",
    "Condition": {
      "StringNotEquals": {
        "s3:x-amz-server-side-encryption": "AES256"
      }
    }
  }]
}
```

### 3. Require VPC Endpoint
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:*",
    "Resource": [
      "arn:aws:s3:::my-bucket",
      "arn:aws:s3:::my-bucket/*"
    ],
    "Condition": {
      "StringNotEquals": {
        "aws:SourceVpce": "vpce-12345"
      }
    }
  }]
}
```

### 4. Time-Based Access
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "ec2:*",
    "Resource": "*",
    "Condition": {
      "DateGreaterThan": {"aws:CurrentTime": "2024-01-01T09:00:00Z"},
      "DateLessThan": {"aws:CurrentTime": "2024-01-01T17:00:00Z"}
    }
  }]
}
```

### 5. Source VPC Restriction
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Principal": "*",
    "Action": "*",
    "Resource": "*",
    "Condition": {
      "StringNotEquals": {
        "aws:SourceVpc": "vpc-12345"
      }
    }
  }]
}
```

### 6. Cross-Account Access with External ID
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::111122223333:root"},
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {"sts:ExternalId": "unique-external-id-12345"}
    }
  }]
}
```

## IAM Roles

### Service Role (Lambda Example)
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
```

### Cross-Account Role
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "AWS": "arn:aws:iam::111122223333:root"
    },
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {
        "sts:ExternalId": "unique-external-id"
      }
    }
  }]
}
```

### SAML Federation Role
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::123456789012:saml-provider/ExampleProvider"
    },
    "Action": "sts:AssumeRoleWithSAML",
    "Condition": {
      "StringEquals": {
        "SAML:aud": "https://signin.aws.amazon.com/saml"
      }
    }
  }]
}
```

## Service Control Policies (SCPs)

### Prevent Leaving Organization
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": "organizations:LeaveOrganization",
    "Resource": "*"
  }]
}
```

### Require Encryption for S3
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": "s3:PutObject",
    "Resource": "*",
    "Condition": {
      "StringNotEquals": {
        "s3:x-amz-server-side-encryption": ["AES256", "aws:kms"]
      }
    }
  }]
}
```

### Restrict Regions
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "NotAction": [
      "iam:*",
      "organizations:*",
      "route53:*",
      "cloudfront:*",
      "globalaccelerator:*",
      "sts:*"
    ],
    "Resource": "*",
    "Condition": {
      "StringNotEquals": {
        "aws:RequestedRegion": ["us-east-1", "us-west-2"]
      }
    }
  }]
}
```

## Permissions Boundaries

```python
import boto3

iam = boto3.client('iam')

# Create permissions boundary
boundary_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": [
            "s3:*",
            "dynamodb:*",
            "lambda:*"
        ],
        "Resource": "*"
    }]
}

# Attach as boundary
iam.put_user_permissions_boundary(
    UserName='developer',
    PermissionsBoundary='arn:aws:iam::123456789012:policy/DeveloperBoundary'
)
```

## Policy Evaluation Logic

```
Decision Flow:
1. Explicit Deny? → DENY (stops here)
2. Explicit Allow? → Continue
3. SCP Allows? → Continue
4. Permissions Boundary Allows? → Continue
5. Resource Policy Allows? → ALLOW
6. No Explicit Allow? → DENY (implicit)

Rule: Explicit Deny always wins
```

## Best Practices

### 1. Least Privilege
```json
// Bad: Too broad
{
  "Effect": "Allow",
  "Action": "*",
  "Resource": "*"
}

// Good: Specific actions and resources
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::my-app-bucket/user-data/*"
}
```

### 2. Use IAM Roles Instead of Users
```python
# Bad: Hardcoded credentials
AWS_ACCESS_KEY_ID = "AKIA..."
AWS_SECRET_ACCESS_KEY = "..."

# Good: Use IAM role (EC2, Lambda, ECS)
session = boto3.Session()
s3 = session.client('s3')
```

### 3. Enable MFA for Privileged Actions
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": [
      "ec2:TerminateInstances",
      "rds:DeleteDBInstance",
      "s3:DeleteBucket"
    ],
    "Resource": "*",
    "Condition": {
      "BoolIfExists": {"aws:MultiFactorAuthPresent": "false"}
    }
  }]
}
```

### 4. Use Policy Variables
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:ListBucket"],
    "Resource": "arn:aws:s3:::my-bucket",
    "Condition": {
      "StringLike": {
        "s3:prefix": ["home/${aws:username}/*"]
      }
    }
  }]
}
```

### 5. Regular Audit with Access Analyzer
```bash
aws accessanalyzer create-analyzer \
    --analyzer-name my-account-analyzer \
    --type ACCOUNT

aws accessanalyzer list-findings \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-account-analyzer
```

### 6. Use Managed Policies When Possible
```python
# Attach AWS managed policy
iam.attach_user_policy(
    UserName='developer',
    PolicyArn='arn:aws:iam::aws:policy/ReadOnlyAccess'
)

# Create customer managed policy for reuse
policy = iam.create_policy(
    PolicyName='S3ReadWriteAppBucket',
    PolicyDocument=json.dumps(policy_document)
)
```

### 7. Implement Service Control Policies
```json
// Prevent root user usage in member accounts
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*",
    "Condition": {
      "StringLike": {
        "aws:PrincipalArn": "arn:aws:iam::*:root"
      }
    }
  }]
}
```

## Policy Testing

### IAM Policy Simulator
```bash
# Test policy via CLI
aws iam simulate-principal-policy \
    --policy-source-arn arn:aws:iam::123456789012:user/alice \
    --action-names s3:GetObject s3:PutObject \
    --resource-arns arn:aws:s3:::my-bucket/file.txt
```

### Access Analyzer Policy Validation
```bash
aws accessanalyzer validate-policy \
    --policy-document file://policy.json \
    --policy-type IDENTITY_POLICY
```

## Common AWS Managed Policies

- **AdministratorAccess**: Full access to all services
- **PowerUserAccess**: Admin access except IAM
- **ReadOnlyAccess**: Read-only access to all services
- **SecurityAudit**: Security audit permissions
- **ViewOnlyAccess**: View-only (more restrictive than ReadOnly)
- **AmazonEC2FullAccess**: Full EC2 access
- **AmazonS3ReadOnlyAccess**: Read-only S3 access
- **AWSSupportAccess**: AWS Support access

## Policy Size Limits

- **User policy**: Max 10 managed policies, 2 KB each inline
- **Group policy**: Max 10 managed policies, 5 KB each inline
- **Role policy**: Max 10 managed policies, 10 KB each inline
- **Resource policy**: Varies by service (20 KB for S3)
- **SCP**: Max 5 SCPs per entity, 5 KB each

This comprehensive reference covers IAM policies for implementing least-privilege access control in AWS environments.
