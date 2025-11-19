# Infrastructure as Code (IaC) - Elite Professional Practices

**Declarative, version-controlled infrastructure management at scale**

---

## Overview

Infrastructure as Code (IaC) is the practice of managing and provisioning infrastructure through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. This transforms infrastructure from manual, error-prone processes into version-controlled, repeatable, auditable procedures. This subskill covers elite practices from HashiCorp, AWS, Google Cloud, Netflix, and other tier-1 organizations that manage billions of infrastructure components.

You are an expert in designing infrastructure as code solutions that enable organizations to provision, update, and manage infrastructure at scale with confidence, consistency, and speed.

## Core Principles

### 1. Declarative over Imperative

**Declarative**: Define *what* infrastructure should exist
```hcl
# Terraform (declarative)
resource "aws_instance" "web" {
  ami                    = "ami-0c55b159cbfafe1f0"
  instance_type         = "t2.micro"
  vpc_security_group_ids = [aws_security_group.web.id]

  tags = {
    Name = "web-server"
  }
}
```

**Imperative**: Define *how* to build infrastructure (avoid)
```bash
# Shell script (imperative - fragile)
aws ec2 run-instances --image-id ami-0c55b159cbfafe1f0 --instance-type t2.micro
```

**Benefits of declarative**:
- Desired state is always clear
- Tool handles convergence automatically
- Repeatable regardless of current state
- Can detect and fix drift automatically

### 2. Idempotency

Running the same IaC code produces the same result, regardless of how many times it's run.

```hcl
# This is idempotent - running it multiple times is safe
resource "aws_security_group" "web" {
  name = "web-sg"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Running apply multiple times doesn't create duplicate rules
```

**Why it matters**:
- Safe to run infrastructure updates repeatedly
- Enables automation without fear
- Fixing failed deployments is simple (re-run)
- Infrastructure remains stable

### 3. Version Control

All infrastructure definitions stored in Git alongside application code.

```yaml
# Git repository structure
infrastructure/
├── terraform/
│   ├── environments/
│   │   ├── dev/
│   │   ├── staging/
│   │   └── production/
│   └── modules/
│       ├── networking/
│       ├── compute/
│       └── database/
├── .gitignore (excludes state files)
└── README.md
```

**Benefits**:
- Complete audit trail of infrastructure changes
- Review and approval process (pull requests)
- Rollback capability
- Team collaboration and knowledge sharing
- Disaster recovery (rebuild from Git)

### 4. Immutability

Replace infrastructure rather than modify in-place.

```hcl
# Good: Replace the instance
resource "aws_launch_template" "app" {
  image_id      = aws_ami_from_container.app.id
  instance_type = "t3.medium"
}

resource "aws_autoscaling_group" "app" {
  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }
  # Old instances are terminated, new ones launched
}

# Instead of modifying: server patch, reboot, pray nothing breaks
```

**Benefits**:
- Predictable behavior
- Simpler rollbacks (replace with old version)
- No configuration drift
- Consistent deployments

### 5. Modularity

Infrastructure code organized into reusable, composable components.

```hcl
# Module usage
module "vpc" {
  source = "./modules/vpc"

  cidr_block = "10.0.0.0/16"
  name       = "production"
}

module "rds" {
  source = "./modules/rds"

  vpc_id             = module.vpc.vpc_id
  db_subnet_group_id = module.vpc.db_subnet_group_id
  engine             = "postgres"
  instance_class     = "db.t3.medium"
}

# Modules are:
# - Reusable across projects
# - Version-controlled independently
# - Testable in isolation
# - Shared across teams
```

## Core Competencies

### State Management

Infrastructure state is critical - tracks what exists, enables updates, prevents resource conflicts.

**Challenges**:
- State files contain sensitive data (passwords, keys)
- Multiple users can conflict (race conditions)
- State can drift from real infrastructure
- Loss of state file means resource orphaning

**State Management Best Practices**:

```hcl
# Use remote state with locking
terraform {
  backend "s3" {
    bucket         = "terraform-state-production"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

# Benefits:
# - State stored remotely (AWS S3)
# - Encrypted at rest
# - DynamoDB prevents concurrent modifications (locking)
# - Team can safely share state
```

### Environment Separation

Development, staging, and production require different configurations.

```hcl
# Workspace-based separation
terraform workspace select dev
# Operates on dev-specific state

# Or directory-based separation
environments/
├── dev/main.tf
├── staging/main.tf
└── production/main.tf

# Variable-based customization
variable "instance_type" {
  default = {
    dev        = "t2.micro"
    staging    = "t2.small"
    production = "t3.large"
  }
}
```

### Drift Detection

Ensure actual infrastructure matches declared state.

```hcl
# Terraform refresh detects changes made outside Terraform
terraform refresh
terraform plan  # Shows what changed

# For continuous drift detection
# - Regular terraform plan runs
# - Compare results to baseline
# - Alert on unexpected drift
# - Auto-remediate if configured
```

## Technology Stack

### Terraform (HashiCorp)

**Industry standard for multi-cloud IaC**

```hcl
# Terraform configuration
terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Simple resource
resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id

  versioning_configuration {
    status = "Enabled"
  }
}
```

**Advantages**:
- Multi-cloud support (AWS, GCP, Azure, Kubernetes, etc.)
- 3,000+ providers and modules
- HCL language (readable, powerful)
- Excellent state management
- Strong community

### Pulumi

**IaC using real programming languages (Python, Go, TypeScript)**

```python
import pulumi
import pulumi_aws as aws

# Using Python for infrastructure
vpc = aws.ec2.Vpc("main",
    cidr_block="10.0.0.0/16")

subnet = aws.ec2.Subnet("main",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="us-east-1a")

# Use full programming language features
for i in range(3):
    instance = aws.ec2.Instance(f"web-{i}",
        ami="ami-0c55b159cbfafe1f0",
        instance_type="t2.micro",
        subnet_id=subnet.id)
```

**Advantages**:
- Full programming language power
- Better code reuse and abstraction
- Less boilerplate than declarative
- IDE support and type checking

### CloudFormation (AWS)

**AWS-native Infrastructure as Code**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Web application stack'

Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-app-bucket
      VersioningConfiguration:
        Status: Enabled

  MyRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole

Outputs:
  BucketName:
    Value: !Ref MyBucket
    Description: S3 bucket name
```

**Advantages**:
- AWS-native with deep integration
- Drift detection built-in
- Change sets for preview before apply
- Console integration

### Crossplane (Kubernetes-native)

**Infrastructure via Kubernetes API**

```yaml
apiVersion: s3.aws.crossplane.io/v1beta1
kind: Bucket
metadata:
  name: my-bucket
spec:
  forProvider:
    acl: private
    locationConstraint: us-west-2
  providerConfigRef:
    name: aws-provider
```

**Advantages**:
- Native Kubernetes experience
- GitOps-friendly
- Application and infrastructure together
- Control plane extensible

## Implementation Patterns

### Multi-Environment Architecture

```hcl
# shared/vpc.tf - Shared infrastructure
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr

  tags = {
    Name        = var.environment
    Environment = var.environment
  }
}

# environments/dev/terraform.tfvars
environment = "dev"
vpc_cidr    = "10.0.0.0/16"
instance_type = "t2.micro"

# environments/production/terraform.tfvars
environment = "production"
vpc_cidr    = "10.1.0.0/16"
instance_type = "t3.large"

# Deployment command
terraform -chdir=environments/production plan
terraform -chdir=environments/production apply
```

### Modular Infrastructure

```hcl
# modules/rds/main.tf
variable "db_name" {}
variable "db_user" {}
variable "db_password" {}
variable "vpc_id" {}

resource "aws_rds_cluster" "main" {
  cluster_identifier  = var.db_name
  master_username     = var.db_user
  master_password     = var.db_password
  database_name       = var.db_name
  engine              = "aurora-postgresql"

  db_subnet_group_name = aws_db_subnet_group.main.name
}

output "cluster_endpoint" {
  value = aws_rds_cluster.main.endpoint
}

# main.tf - Using the module
module "database" {
  source = "./modules/rds"

  db_name     = "myapp"
  db_user     = "admin"
  db_password = random_password.db.result
  vpc_id      = aws_vpc.main.id
}
```

## Best Practices

### 1. State Management

```bash
# Prevent accidental commits of state files
echo "*.tfstate*" >> .gitignore

# Use remote state with locking
terraform init -backend-config="bucket=my-bucket"

# Regular state backups
aws s3 cp s3://terraform-state-prod/terraform.tfstate backup-$(date +%Y%m%d).tfstate
```

### 2. CI/CD for Infrastructure

```yaml
# GitLab CI example
stages:
  - validate
  - plan
  - apply

validate:
  stage: validate
  script:
    - terraform fmt -recursive -check
    - terraform init -backend=false
    - terraform validate

plan:
  stage: plan
  script:
    - terraform init
    - terraform plan -out=tfplan
  artifacts:
    paths:
      - tfplan

apply:
  stage: apply
  script:
    - terraform apply tfplan
  when: manual
  only:
    - main
```

### 3. Policy as Code

```hcl
# Sentinel policy (HashiCorp)
import "tfplan/v2" as tfplan

main = rule {
  all tfplan.resource_changes as _, rc {
    rc.type is not "aws_security_group" or
    all rc.change.after.ingress[*].cidr_blocks[*] as _ { . is not ["0.0.0.0/0"] }
  }
}
# This policy requires explicit IP ranges for security groups

# OPA/Rego policy (Open Policy Agent)
package main

deny[msg] {
  input.resource_type == "aws_s3_bucket"
  not input.properties.server_side_encryption_configuration
  msg := "S3 buckets must have encryption enabled"
}
```

### 4. Resource Tagging

```hcl
# Standard tags applied to all resources
locals {
  common_tags = {
    Environment = var.environment
    Project     = var.project
    CreatedBy   = "terraform"
    CreatedAt   = timestamp()
    ManagedBy   = "terraform"
  }
}

resource "aws_instance" "web" {
  ami           = var.ami_id
  instance_type = var.instance_type

  tags = merge(local.common_tags, {
    Name = "web-server"
    Role = "web"
  })
}
```

## Common Challenges and Solutions

### Configuration Drift

**Problem**: Manual changes made outside IaC cause actual state to differ from declared state

**Solutions**:
- Automated drift detection
- Scheduled `terraform plan` runs
- Policy enforcement (prevent manual changes)
- Continuous reconciliation

### State File Conflicts

**Problem**: Multiple users applying changes simultaneously

**Solutions**:
- Use remote state with locking
- Implement approval process
- Serial deployments for critical changes
- Team communication and coordination

### Secret Management

**Problem**: Terraform state contains sensitive data (passwords, API keys)

**Solutions**:
```hcl
# Store secrets in external vault
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
}

resource "aws_rds_cluster" "main" {
  master_password = data.aws_secretsmanager_secret_version.db_password.secret_string
}

# Use sensitive attribute
variable "api_key" {
  type      = string
  sensitive = true
}
```

## Tools and Integration

**Testing Infrastructure Code**:
- Terratest - Go framework for infrastructure testing
- TFLint - Terraform linter and validator
- Checkov - Policy as code scanning
- Snyk - Infrastructure vulnerability scanning

**Monitoring and Observability**:
- CloudTrail/Audit Logs - Track infrastructure changes
- AWS Config - Compliance and configuration tracking
- Prometheus - Cost and resource metrics

---

**Version**: 2.0
**Last Updated**: 2025-11-19
**Expertise Level**: Elite Professional
**Based on**: HashiCorp, AWS, Google Cloud, Netflix practices
