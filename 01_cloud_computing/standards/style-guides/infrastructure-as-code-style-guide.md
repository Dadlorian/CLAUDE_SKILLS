# Infrastructure as Code (IaC) Style Guide

## Overview

This guide establishes best practices for Infrastructure as Code across Terraform, Pulumi, CloudFormation, and other IaC tools. Based on HashiCorp's Terraform standards, Pulumi best practices, AWS CloudFormation guidelines, and FAANG infrastructure patterns.

## Table of Contents

1. [General IaC Principles](#general-iac-principles)
2. [Terraform Standards](#terraform-standards)
3. [Pulumi Conventions](#pulumi-conventions)
4. [CloudFormation Guidelines](#cloudformation-guidelines)
5. [Module Design](#module-design)
6. [Naming Conventions](#naming-conventions)
7. [State Management](#state-management)
8. [Testing and Validation](#testing-and-validation)
9. [CI/CD Integration](#cicd-integration)
10. [Anti-Patterns](#anti-patterns)
11. [References](#references)

## General IaC Principles

### Core Tenets

1. **Immutable Infrastructure**: Replace, don't modify
2. **Version Everything**: Code, modules, providers, state
3. **DRY (Don't Repeat Yourself)**: Use modules and composition
4. **Declarative over Imperative**: Describe desired state, not steps
5. **Security by Default**: Least privilege, encryption, secrets management
6. **Observable**: Outputs, tags, documentation
7. **Testable**: Unit tests, integration tests, policy validation

### Project Structure

```
infrastructure/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── backend.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── prod/
├── modules/
│   ├── networking/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── README.md
│   │   └── examples/
│   ├── compute/
│   └── security/
├── policies/
│   ├── sentinel/
│   └── opa/
├── scripts/
│   ├── validate.sh
│   └── plan-all.sh
└── docs/
    └── architecture/
```

## Terraform Standards

### File Organization

**Standard Files** (in order):
1. `versions.tf` - Terraform and provider version constraints
2. `main.tf` - Primary resources
3. `variables.tf` - Input variables
4. `outputs.tf` - Output values
5. `locals.tf` - Local values (if needed)
6. `data.tf` - Data sources (if many)
7. `backend.tf` - Backend configuration

### versions.tf Example

```hcl
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
}
```

### Resource Naming

**Format**: `<resource_type>.<descriptive_name>`

**Good**:
```hcl
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
}

resource "aws_subnet" "private" {
  count  = length(var.availability_zones)
  vpc_id = aws_vpc.main.id
  # ...
}

resource "aws_security_group" "application_lb" {
  name        = "${var.project_name}-alb-sg"
  description = "Security group for application load balancer"
  vpc_id      = aws_vpc.main.id
}
```

**Bad**:
```hcl
# Too generic
resource "aws_vpc" "vpc1" {}

# Includes type in name (redundant)
resource "aws_security_group" "sg_alb" {}

# Non-descriptive
resource "aws_subnet" "subnet_1" {}
```

### Variable Definitions

```hcl
# variables.tf

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "Must be a valid IPv4 CIDR block."
  }
}

variable "availability_zones" {
  description = "List of availability zones for subnet distribution"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]

  validation {
    condition     = length(var.availability_zones) >= 2
    error_message = "At least 2 availability zones required for high availability."
  }
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnet internet access"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "db_config" {
  description = "Database configuration"
  type = object({
    instance_class    = string
    allocated_storage = number
    engine_version    = string
    multi_az          = bool
  })
  default = {
    instance_class    = "db.t3.medium"
    allocated_storage = 100
    engine_version    = "14.7"
    multi_az          = true
  }
}
```

### Outputs

```hcl
# outputs.tf

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

# Sensitive outputs
output "db_connection_string" {
  description = "Database connection string"
  value       = "postgresql://${aws_db_instance.main.endpoint}/${aws_db_instance.main.name}"
  sensitive   = true
}

# Complex outputs for downstream consumption
output "vpc_config" {
  description = "VPC configuration object for use in other modules"
  value = {
    vpc_id             = aws_vpc.main.id
    cidr_block         = aws_vpc.main.cidr_block
    private_subnet_ids = aws_subnet.private[*].id
    public_subnet_ids  = aws_subnet.public[*].id
    nat_gateway_ips    = aws_eip.nat[*].public_ip
  }
}
```

### Locals

Use locals for:
- Computed values used multiple times
- Complex expressions
- Combining variables

```hcl
# locals.tf

locals {
  # Common tags applied to all resources
  common_tags = merge(
    var.tags,
    {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Project     = var.project_name
      CostCenter  = var.cost_center
    }
  )

  # Computed names
  cluster_name = "${var.project_name}-${var.environment}-eks"

  # Conditional logic
  enable_monitoring = var.environment == "prod" ? true : var.enable_monitoring

  # Complex computations
  az_subnet_mapping = {
    for idx, az in var.availability_zones :
    az => cidrsubnet(var.vpc_cidr, 8, idx)
  }

  # Data transformations
  subnet_ids_by_type = {
    public  = aws_subnet.public[*].id
    private = aws_subnet.private[*].id
  }
}
```

### Resource Meta-Arguments

**count** - For similar resources:

```hcl
resource "aws_subnet" "private" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-private-${count.index + 1}"
      Type = "private"
    }
  )
}
```

**for_each** - For distinct resources (preferred over count):

```hcl
resource "aws_subnet" "private" {
  for_each = local.az_subnet_mapping

  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value
  availability_zone = each.key

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-private-${each.key}"
      Type = "private"
      AZ   = each.key
    }
  )
}
```

**depends_on** - Use sparingly, only for hidden dependencies:

```hcl
resource "aws_iam_role_policy_attachment" "cluster" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.cluster.name
}

resource "aws_eks_cluster" "main" {
  name     = local.cluster_name
  role_arn = aws_iam_role.cluster.arn

  # Ensure IAM policy is attached before creating cluster
  depends_on = [
    aws_iam_role_policy_attachment.cluster
  ]

  vpc_config {
    subnet_ids = concat(
      aws_subnet.private[*].id,
      aws_subnet.public[*].id
    )
  }
}
```

### Data Sources

```hcl
# data.tf

# Get latest AMI
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Get current region
data "aws_region" "current" {}

# Get current account
data "aws_caller_identity" "current" {}

# Get availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# Remote state data source
data "terraform_remote_state" "networking" {
  backend = "s3"
  config = {
    bucket = "mycompany-terraform-state"
    key    = "networking/${var.environment}/terraform.tfstate"
    region = "us-east-1"
  }
}
```

### Dynamic Blocks

```hcl
resource "aws_security_group" "application" {
  name        = "${var.project_name}-app-sg"
  description = "Security group for application servers"
  vpc_id      = var.vpc_id

  # Dynamic ingress rules
  dynamic "ingress" {
    for_each = var.allowed_ingress_ports
    content {
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = "tcp"
      cidr_blocks = ingress.value.cidr_blocks
      description = ingress.value.description
    }
  }

  # Single egress rule (prefer explicit over dynamic)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-app-sg"
    }
  )
}
```

## Pulumi Conventions

### Project Structure

```
pulumi-project/
├── Pulumi.yaml
├── Pulumi.dev.yaml
├── Pulumi.staging.yaml
├── Pulumi.prod.yaml
├── index.ts (or __main__.py)
├── config/
│   └── config.ts
├── resources/
│   ├── networking.ts
│   ├── compute.ts
│   └── database.ts
├── policies/
│   └── policy-pack/
├── tests/
│   ├── unit/
│   └── integration/
└── package.json (or requirements.txt)
```

### TypeScript Example

```typescript
// index.ts
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import { createVpc } from "./resources/networking";
import { createEksCluster } from "./resources/compute";

// Get configuration
const config = new pulumi.Config();
const environment = pulumi.getStack();
const projectName = config.require("projectName");
const vpcCidr = config.get("vpcCidr") || "10.0.0.0/16";

// Create VPC
const vpc = createVpc({
  projectName,
  environment,
  cidr: vpcCidr,
  azCount: 3,
});

// Create EKS cluster
const cluster = createEksCluster({
  projectName,
  environment,
  vpcId: vpc.vpcId,
  privateSubnetIds: vpc.privateSubnetIds,
  publicSubnetIds: vpc.publicSubnetIds,
});

// Export outputs
export const vpcId = vpc.vpcId;
export const clusterName = cluster.clusterName;
export const clusterEndpoint = cluster.endpoint;
export const kubeconfig = pulumi.secret(cluster.kubeconfig);
```

```typescript
// resources/networking.ts
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

export interface VpcArgs {
  projectName: string;
  environment: string;
  cidr: string;
  azCount: number;
}

export function createVpc(args: VpcArgs) {
  const { projectName, environment, cidr, azCount } = args;

  // Common tags
  const tags = {
    Project: projectName,
    Environment: environment,
    ManagedBy: "Pulumi",
  };

  // Create VPC
  const vpc = new aws.ec2.Vpc(`${projectName}-${environment}-vpc`, {
    cidrBlock: cidr,
    enableDnsHostnames: true,
    enableDnsSupport: true,
    tags: {
      ...tags,
      Name: `${projectName}-${environment}-vpc`,
    },
  });

  // Get availability zones
  const azs = aws.getAvailabilityZones({
    state: "available",
  });

  // Create private subnets
  const privateSubnets = [];
  for (let i = 0; i < azCount; i++) {
    const subnet = new aws.ec2.Subnet(
      `${projectName}-private-${i}`,
      {
        vpcId: vpc.id,
        cidrBlock: pulumi.interpolate`${cidrSubnet(cidr, 8, i)}`,
        availabilityZone: azs.then((az) => az.names[i]),
        tags: {
          ...tags,
          Name: `${projectName}-private-${i}`,
          Type: "private",
        },
      },
      { parent: vpc }
    );
    privateSubnets.push(subnet);
  }

  return {
    vpcId: vpc.id,
    vpcCidr: vpc.cidrBlock,
    privateSubnetIds: privateSubnets.map((s) => s.id),
  };
}

// Helper function
function cidrSubnet(cidr: string, newBits: number, netNum: number): string {
  // Implementation of CIDR subnet calculation
  // Or use a library like ip-cidr
}
```

### Python Example

```python
# __main__.py
import pulumi
import pulumi_aws as aws
from resources.networking import create_vpc
from resources.compute import create_eks_cluster

# Configuration
config = pulumi.Config()
environment = pulumi.get_stack()
project_name = config.require("projectName")
vpc_cidr = config.get("vpcCidr") or "10.0.0.0/16"

# Create VPC
vpc = create_vpc(
    project_name=project_name,
    environment=environment,
    cidr=vpc_cidr,
    az_count=3,
)

# Create EKS cluster
cluster = create_eks_cluster(
    project_name=project_name,
    environment=environment,
    vpc_id=vpc["vpc_id"],
    private_subnet_ids=vpc["private_subnet_ids"],
)

# Exports
pulumi.export("vpcId", vpc["vpc_id"])
pulumi.export("clusterName", cluster["cluster_name"])
pulumi.export("clusterEndpoint", cluster["endpoint"])
```

## CloudFormation Guidelines

### Template Organization

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'VPC with public and private subnets across 3 AZs'

Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: "Network Configuration"
        Parameters:
          - VpcCidr
          - Environment
      - Label:
          default: "Availability"
        Parameters:
          - AvailabilityZones

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod
    Description: Environment name

  VpcCidr:
    Type: String
    Default: 10.0.0.0/16
    AllowedPattern: '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$'
    Description: CIDR block for VPC

Mappings:
  EnvironmentConfig:
    dev:
      EnableNatGateway: false
      MultiAz: false
    staging:
      EnableNatGateway: true
      MultiAz: false
    prod:
      EnableNatGateway: true
      MultiAz: true

Conditions:
  IsProduction: !Equals [!Ref Environment, 'prod']
  EnableNatGateway: !FindInMap [EnvironmentConfig, !Ref Environment, EnableNatGateway]

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-vpc'
        - Key: Environment
          Value: !Ref Environment
        - Key: ManagedBy
          Value: CloudFormation

  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-igw'

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

Outputs:
  VpcId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-VpcId'

  VpcCidr:
    Description: VPC CIDR block
    Value: !GetAtt VPC.CidrBlock
    Export:
      Name: !Sub '${AWS::StackName}-VpcCidr'
```

## Module Design

### Module Structure

```
module-name/
├── README.md
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
├── examples/
│   ├── basic/
│   │   ├── main.tf
│   │   └── README.md
│   └── complete/
│       ├── main.tf
│       └── README.md
├── tests/
│   └── module_test.go
└── CHANGELOG.md
```

### Module README Template

```markdown
# Module Name

## Description
Brief description of what this module creates and its purpose.

## Usage

### Basic Example
```hcl
module "vpc" {
  source = "../../modules/vpc"

  project_name = "myapp"
  environment  = "dev"
  vpc_cidr     = "10.0.0.0/16"
}
```

### Complete Example
See [examples/complete](./examples/complete)

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.6 |
| aws | ~> 5.0 |

## Providers

| Name | Version |
|------|---------|
| aws | ~> 5.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| project_name | Project name | `string` | n/a | yes |
| environment | Environment name | `string` | n/a | yes |
| vpc_cidr | VPC CIDR block | `string` | `"10.0.0.0/16"` | no |

## Outputs

| Name | Description |
|------|-------------|
| vpc_id | VPC ID |
| private_subnet_ids | List of private subnet IDs |

## Examples
- [Basic](./examples/basic) - Minimal configuration
- [Complete](./examples/complete) - Full configuration with all options

## Contributing
See main repository CONTRIBUTING.md
```

### Module Best Practices

1. **Single Responsibility**: One module = one logical infrastructure component
2. **Composition over Inheritance**: Combine simple modules rather than creating complex ones
3. **Sane Defaults**: Provide sensible defaults, require minimal inputs
4. **Complete Outputs**: Export all useful resource attributes
5. **Versioning**: Use semantic versioning for published modules

**Good Module Example**:

```hcl
# modules/eks-cluster/main.tf
resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  role_arn = aws_iam_role.cluster.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids              = var.subnet_ids
    endpoint_private_access = var.endpoint_private_access
    endpoint_public_access  = var.endpoint_public_access
    public_access_cidrs     = var.public_access_cidrs
    security_group_ids      = [aws_security_group.cluster.id]
  }

  enabled_cluster_log_types = var.enabled_cluster_log_types

  encryption_config {
    provider {
      key_arn = var.kms_key_arn
    }
    resources = ["secrets"]
  }

  dynamic "kubernetes_network_config" {
    for_each = var.cluster_service_ipv4_cidr != null ? [1] : []
    content {
      service_ipv4_cidr = var.cluster_service_ipv4_cidr
    }
  }

  tags = merge(
    var.tags,
    {
      Name = var.cluster_name
    }
  )

  depends_on = [
    aws_iam_role_policy_attachment.cluster_policy,
    aws_cloudwatch_log_group.cluster,
  ]
}
```

## Naming Conventions

See [cloud-naming-conventions.md](./cloud-naming-conventions.md) for comprehensive naming standards.

### Terraform-Specific Naming

**Variables**: `snake_case`
```hcl
variable "vpc_cidr" {}
variable "availability_zones" {}
variable "enable_nat_gateway" {}
```

**Resources**: `snake_case` with descriptive names
```hcl
resource "aws_vpc" "main" {}
resource "aws_security_group" "application_lb" {}
resource "aws_eks_node_group" "workers" {}
```

**Outputs**: `snake_case` matching resource attributes
```hcl
output "vpc_id" {}
output "cluster_endpoint" {}
output "node_group_id" {}
```

**Locals**: `snake_case`
```hcl
locals {
  cluster_name = "${var.project_name}-${var.environment}"
  common_tags  = { ... }
}
```

## State Management

### Backend Configuration

**S3 Backend (Recommended for AWS)**:

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "networking/prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
    kms_key_id     = "arn:aws:kms:us-east-1:123456789:key/xxx"

    # Workspace isolation
    workspace_key_prefix = "workspaces"
  }
}
```

**GCS Backend**:

```hcl
terraform {
  backend "gcs" {
    bucket  = "mycompany-terraform-state"
    prefix  = "networking/prod"
  }
}
```

### State Best Practices

1. **Remote Backend**: Always use remote backend for team collaboration
2. **State Locking**: Enable locking (DynamoDB for S3, native for GCS/Azure)
3. **Encryption**: Enable encryption at rest and in transit
4. **Backup**: Enable versioning on state bucket
5. **Separation**: Separate state per environment and major component

```
terraform-state/
├── networking/
│   ├── dev/terraform.tfstate
│   ├── staging/terraform.tfstate
│   └── prod/terraform.tfstate
├── compute/
│   ├── dev/terraform.tfstate
│   └── prod/terraform.tfstate
└── security/
    └── prod/terraform.tfstate
```

## Testing and Validation

### Pre-Commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.83.5
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_docs
      - id: terraform_tflint
      - id: terraform_tfsec
      - id: terraform_checkov
```

### Terratest Example

```go
// tests/vpc_test.go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestVpcCreation(t *testing.T) {
    t.Parallel()

    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../examples/basic",
        Vars: map[string]interface{}{
            "project_name": "test",
            "environment":  "dev",
        },
    })

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    vpcId := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcId)
}
```

### Policy as Code

**Sentinel (Terraform Cloud/Enterprise)**:

```python
# policies/enforce-tags.sentinel
import "tfplan/v2" as tfplan

required_tags = ["Environment", "Project", "CostCenter"]

main = rule {
    all tfplan.resource_changes as _, rc {
        all required_tags as tag {
            rc.change.after.tags contains tag
        }
    }
}
```

**OPA (Open Policy Agent)**:

```rego
# policies/require_encryption.rego
package terraform.encryption

deny[msg] {
    r := input.resource_changes[_]
    r.type == "aws_s3_bucket"
    not r.change.after.server_side_encryption_configuration
    msg := sprintf("S3 bucket '%s' must have encryption enabled", [r.address])
}
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/terraform.yml
name: Terraform

on:
  pull_request:
    paths:
      - 'infrastructure/**'
  push:
    branches:
      - main

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.6.0

      - name: Terraform Format
        run: terraform fmt -check -recursive

      - name: Terraform Init
        run: terraform init
        working-directory: infrastructure/environments/prod

      - name: Terraform Validate
        run: terraform validate
        working-directory: infrastructure/environments/prod

      - name: Terraform Plan
        if: github.event_name == 'pull_request'
        run: terraform plan -no-color
        working-directory: infrastructure/environments/prod
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: terraform apply -auto-approve
        working-directory: infrastructure/environments/prod
```

## Anti-Patterns

### Don't: Hardcode Values

**Bad**:
```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"  # Hardcoded AMI
  instance_type = "t3.medium"
  subnet_id     = "subnet-12345678"       # Hardcoded subnet
}
```

**Good**:
```hcl
data "aws_ami" "app" {
  most_recent = true
  owners      = ["self"]
  filter {
    name   = "name"
    values = ["myapp-*"]
  }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.app.id
  instance_type = var.instance_type
  subnet_id     = var.subnet_id
}
```

### Don't: Create God Modules

**Bad**: One module that creates VPC, EKS, RDS, Redis, etc.

**Good**: Separate modules composed together

### Don't: Ignore State File Security

**Bad**: Commit state files to git, use local state for prod

**Good**: Remote encrypted backend with access controls

### Don't: Skip Testing

**Bad**: Apply directly to production

**Good**: Test modules, validate with policies, plan before apply

### Don't: Mix Terraform Versions

**Bad**: Different versions across team members

**Good**: Lock version in `versions.tf` and CI/CD

## References

### Official Documentation

- **Terraform**: https://www.terraform.io/docs
- **Terraform Style Guide**: https://www.terraform.io/language/syntax/style
- **Pulumi**: https://www.pulumi.com/docs/
- **CloudFormation**: https://docs.aws.amazon.com/cloudformation/
- **AWS CDK**: https://docs.aws.amazon.com/cdk/

### Tools

- **Terratest**: https://terratest.gruntwork.io/
- **TFLint**: https://github.com/terraform-linters/tflint
- **Checkov**: https://www.checkov.io/
- **tfsec**: https://aquasecurity.github.io/tfsec/
- **Terraform Docs**: https://terraform-docs.io/
- **Sentinel**: https://docs.hashicorp.com/sentinel
- **OPA**: https://www.openpolicyagent.org/

### Best Practices

- **Gruntwork Production Framework**: https://gruntwork.io/
- **AWS Provider Best Practices**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- **Google Cloud Foundation Toolkit**: https://cloud.google.com/foundation-toolkit
- **Azure Terraform Quickstarts**: https://github.com/Azure/terraform

### Books and Courses

- "Terraform: Up & Running" - Yevgeniy Brikman
- "Infrastructure as Code" - Kief Morris
- HashiCorp Learn: https://learn.hashicorp.com/terraform
