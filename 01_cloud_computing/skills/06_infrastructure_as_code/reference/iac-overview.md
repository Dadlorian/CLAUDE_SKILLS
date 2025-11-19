# Infrastructure as Code Overview

## What is Infrastructure as Code?

Infrastructure as Code (IaC) is the practice of managing and provisioning infrastructure through machine-readable definition files rather than physical hardware configuration or interactive configuration tools.

## Core Concepts

### Declarative vs Imperative

**Declarative IaC**
- Describe the desired end state
- Tool determines how to achieve it
- Examples: Terraform, CloudFormation, Pulumi (declarative mode)
- Benefits: Idempotent, easier to reason about, self-correcting

```hcl
# Terraform - Declarative
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
  count         = 3
}
```

**Imperative IaC**
- Describe specific commands to execute
- You control the exact steps
- Examples: Ansible, Chef, scripting languages
- Benefits: Fine-grained control, procedural logic

```yaml
# Ansible - Imperative
- name: Create EC2 instances
  ec2:
    count: 3
    instance_type: t3.micro
    image: ami-0c55b159cbfafe1f0
    state: present
```

### Idempotency

Running the same IaC code multiple times produces the same result:
- No duplicate resources created
- Only changes are applied
- Safe to re-run repeatedly
- Critical for automation reliability

### State Management

**State File Purpose**
- Maps real-world resources to configuration
- Tracks metadata and resource attributes
- Enables performance optimization
- Required for proper updates and deletions

**State Backends**
- Local: File on disk (default, not recommended for teams)
- Remote: S3, Azure Blob, GCS, Terraform Cloud
- Features: Locking, encryption, versioning, collaboration

## IaC Tools Comparison

### Terraform

**Strengths**
- Cloud-agnostic with 3000+ providers
- Large ecosystem and community
- Mature state management
- Terraform Cloud for collaboration
- HCL is declarative and readable

**Use Cases**
- Multi-cloud deployments
- Complex infrastructure dependencies
- Module reusability across projects
- Teams familiar with declarative approaches

**Example**
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name        = "${var.environment}-vpc"
    Environment = var.environment
  }
}
```

### Pulumi

**Strengths**
- Use familiar programming languages (TypeScript, Python, Go, C#, Java)
- Full programming language features (loops, conditionals, functions)
- Strong typing and IDE support
- Excellent testing capabilities
- Secrets management built-in

**Use Cases**
- Teams preferring general-purpose languages
- Complex logic and conditionals
- Strong typing requirements
- Integration with existing codebases

**Example**
```typescript
import * as aws from "@pulumi/aws";
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config();
const environment = config.require("environment");

const vpc = new aws.ec2.Vpc("main", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
    tags: {
        Name: `${environment}-vpc`,
        Environment: environment,
    },
});

export const vpcId = vpc.id;
```

### AWS CloudFormation

**Strengths**
- Native AWS integration
- No additional tooling required
- Deep AWS feature coverage on day one
- StackSets for multi-account/region
- Native drift detection

**Use Cases**
- AWS-only environments
- AWS service catalog integration
- Organizations heavily invested in AWS
- Compliance requirements for AWS-native tools

**Example**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: VPC Infrastructure

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]

Resources:
  MainVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: !Sub ${Environment}-vpc
        - Key: Environment
          Value: !Ref Environment

Outputs:
  VPCId:
    Value: !Ref MainVPC
    Export:
      Name: !Sub ${Environment}-VPC-ID
```

### AWS CDK

**Strengths**
- Object-oriented infrastructure definitions
- Construct library with high-level abstractions
- Synthesizes to CloudFormation
- Strong TypeScript/Python ecosystem
- L3 constructs encapsulate best practices

**Use Cases**
- Developers preferring OOP patterns
- Reusable infrastructure patterns
- Complex application infrastructure
- Teams using TypeScript/Python

**Example**
```typescript
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

export class VpcStack extends cdk.Stack {
  public readonly vpc: ec2.Vpc;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const environment = this.node.tryGetContext('environment');

    this.vpc = new ec2.Vpc(this, 'MainVPC', {
      ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
      maxAzs: 3,
      natGateways: 1,
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
        {
          cidrMask: 24,
          name: 'Private',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        },
      ],
    });

    cdk.Tags.of(this.vpc).add('Environment', environment);
  }
}
```

## Key IaC Principles

### 1. Version Control Everything
```bash
# All IaC code in Git
infrastructure/
├── terraform/
│   ├── modules/
│   ├── environments/
│   └── README.md
├── .gitignore          # Exclude secrets, state files
└── .terraform-version  # Pin tool version
```

### 2. DRY (Don't Repeat Yourself)
```hcl
# Use modules instead of duplicating code
module "vpc" {
  source = "./modules/vpc"

  for_each = toset(["dev", "staging", "prod"])

  environment = each.key
  cidr_block  = var.vpc_cidrs[each.key]
}
```

### 3. Immutable Infrastructure
- Never modify running resources
- Deploy new versions, destroy old
- Blue/green deployments
- Eliminates configuration drift

### 4. Small, Incremental Changes
```hcl
# Good: Single, focused change
resource "aws_security_group_rule" "allow_https" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.web.id
}

# Avoid: Large, monolithic changes that are hard to review
```

### 5. Test Before Apply
```bash
# Terraform workflow
terraform fmt -check     # Format validation
terraform validate       # Syntax validation
terraform plan          # Preview changes
tflint                  # Linting
checkov -d .           # Security scan
terraform apply        # Only after review
```

## IaC Workflow Patterns

### GitOps Workflow
```
Developer → Git Push → CI Pipeline → Plan → PR Review → Merge → CD Pipeline → Apply → Monitor
```

**Key Components**
1. **Branch Protection**: Require reviews, status checks
2. **Automated Planning**: Run on every PR
3. **Approval Gates**: Manual approval for production
4. **Automated Apply**: On merge to main branch
5. **Drift Detection**: Scheduled reconciliation

### Multi-Environment Strategy

**Workspace-Based**
```bash
# Terraform workspaces
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod
```

**Directory-Based**
```
environments/
├── dev/
│   ├── main.tf
│   └── terraform.tfvars
├── staging/
│   ├── main.tf
│   └── terraform.tfvars
└── prod/
    ├── main.tf
    └── terraform.tfvars
```

**Git Branch-Based**
```
git-flow:
  main → production
  develop → staging
  feature/* → dev
```

## State Management Best Practices

### Remote State Configuration

**Terraform (S3 Backend)**
```hcl
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "prod/vpc/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
    kms_key_id     = "arn:aws:kms:us-east-1:ACCOUNT:key/KEY-ID"
  }
}
```

**Key Features**
- Encryption at rest
- State locking (DynamoDB)
- Versioning enabled
- Access controls via IAM
- Separate state per environment

### State Security

**Never Commit State Files**
```gitignore
# .gitignore
*.tfstate
*.tfstate.*
.terraform/
.terragrunt-cache/
```

**Encrypt Sensitive Data**
```hcl
# Use sensitive variable marking
variable "db_password" {
  type      = string
  sensitive = true
}

# Use secret management
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/database/password"
}
```

## Cost Management

### Cost Estimation Tools

**Infracost**
```yaml
# .github/workflows/infracost.yml
- name: Run Infracost
  run: |
    infracost breakdown --path . \
      --format json \
      --out-file /tmp/infracost.json

    infracost comment github \
      --path /tmp/infracost.json \
      --repo $GITHUB_REPOSITORY \
      --pull-request $PR_NUMBER
```

**Benefits**
- Cost estimates in PRs
- Budget threshold enforcement
- Cost trend tracking
- Multi-project aggregation

## Security Best Practices

### 1. Least Privilege
```hcl
# IAM role with minimal permissions
resource "aws_iam_role_policy" "minimal" {
  role = aws_iam_role.app.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:PutObject"
      ]
      Resource = "${aws_s3_bucket.app.arn}/*"
    }]
  })
}
```

### 2. Security Scanning
```bash
# Multiple scanners for comprehensive coverage
checkov -d .                    # General security
tfsec .                         # Terraform-specific
terrascan scan                  # Policy violations
trivy config .                  # Misconfigurations
```

### 3. Secret Management
```hcl
# Never hardcode secrets
# Bad
variable "api_key" {
  default = "sk-1234567890abcdef"  # NEVER DO THIS
}

# Good
data "aws_secretsmanager_secret_version" "api_key" {
  secret_id = "prod/api/key"
}

# Even better: Use dynamic credentials
provider "aws" {
  assume_role {
    role_arn = "arn:aws:iam::ACCOUNT:role/TerraformExecution"
  }
}
```

## Compliance & Governance

### Policy as Code

**OPA/Rego Example**
```rego
package terraform.analysis

deny[msg] {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket"
  not resource.change.after.server_side_encryption_configuration

  msg := sprintf(
    "S3 bucket '%s' must have encryption enabled",
    [resource.address]
  )
}
```

### Compliance Frameworks
- CIS Benchmarks
- PCI-DSS
- HIPAA
- SOC 2
- NIST
- GDPR

## Disaster Recovery

### State Backup Strategy
```bash
# Automated state backups
aws s3 cp s3://terraform-state/prod/ \
  s3://terraform-state-backup/prod/$(date +%Y%m%d)/ \
  --recursive
```

### Recovery Procedures
1. Identify state corruption
2. Restore from versioned backup
3. Validate state integrity
4. Test with terraform plan
5. Document incident
6. Update runbooks

## Monitoring & Observability

### Drift Detection
```bash
# Scheduled drift detection
#!/bin/bash
terraform plan -detailed-exitcode
if [ $? -eq 2 ]; then
  echo "Drift detected!"
  # Send alert
  # Create ticket
  # Notify team
fi
```

### Metrics to Track
- Deployment frequency
- Lead time for changes
- Mean time to recovery
- Change failure rate
- Drift detection frequency
- Security scan results
- Cost variance

## Tools Ecosystem

### Terraform Ecosystem
- **Terragrunt**: DRY Terraform configurations
- **Terraspace**: Ruby-based Terraform framework
- **Atlantis**: Terraform automation via pull requests
- **Terraform Cloud**: Managed Terraform execution
- **Spacelift**: Alternative to Terraform Cloud

### Testing Tools
- **Terratest**: Go-based testing framework
- **Kitchen-Terraform**: Ruby test framework
- **Terraform Compliance**: BDD for Terraform
- **InSpec**: Compliance testing

### Security Tools
- **Checkov**: Static analysis
- **tfsec**: Terraform security scanner
- **Terrascan**: Policy enforcement
- **Sentinel**: Policy as code (Terraform Enterprise)
- **OPA**: Open Policy Agent

### CI/CD Integration
- **GitHub Actions**: GitHub-native automation
- **GitLab CI**: GitLab-native automation
- **Jenkins**: Flexible automation server
- **CircleCI**: Cloud-based CI/CD
- **Azure DevOps**: Microsoft ecosystem

## Best Practices Summary

1. **Always use remote state** with encryption and locking
2. **Version control everything** except secrets and state
3. **Use modules** for reusability and maintainability
4. **Test before apply** with multiple validation layers
5. **Implement CI/CD** for consistency and automation
6. **Scan for security** issues continuously
7. **Monitor for drift** and remediate promptly
8. **Document thoroughly** with README and examples
9. **Follow naming conventions** consistently
10. **Plan for disaster recovery** with backups and procedures

## Learning Resources

- HashiCorp Learn: terraform.io/learn
- Pulumi Documentation: pulumi.com/docs
- AWS CloudFormation User Guide
- CDK Workshop: cdkworkshop.com
- Terraform Registry: registry.terraform.io
- Cloud Provider Documentation
- IaC Community Forums
- Conference Talks: HashiConf, PulumiConf

## Next Steps

1. Review tool-specific references for deep dives
2. Explore guides for hands-on tutorials
3. Examine src/ for production code examples
4. Set up your first IaC project
5. Implement CI/CD automation
6. Establish governance policies
