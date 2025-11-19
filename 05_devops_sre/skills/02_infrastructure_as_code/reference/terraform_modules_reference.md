# Terraform Modules Reference

## Table of Contents
- [Module Basics](#module-basics)
- [Module Structure](#module-structure)
- [Module Sources](#module-sources)
- [Module Design Patterns](#module-design-patterns)
- [Module Best Practices](#module-best-practices)
- [Module Examples](#module-examples)
- [Module Publishing](#module-publishing)
- [Module Testing](#module-testing)

## Module Basics

### What is a Module?
A module is a container for multiple resources that are used together. Every Terraform configuration has at least one module, the root module, which consists of the resources defined in the `.tf` files in the main working directory.

### Why Use Modules?
- **Organize Configuration**: Group related resources
- **Encapsulate Logic**: Hide complexity behind simple interfaces
- **Reuse Code**: DRY (Don't Repeat Yourself) principle
- **Consistency**: Enforce standards and best practices
- **Collaboration**: Share modules across teams

### Calling a Module
```hcl
module "vpc" {
  source = "./modules/vpc"

  # Input variables
  vpc_cidr             = "10.0.0.0/16"
  availability_zones   = ["us-west-2a", "us-west-2b", "us-west-2c"]
  environment          = var.environment

  # Tags
  tags = {
    Project = var.project_name
  }
}

# Access module outputs
resource "aws_instance" "web" {
  subnet_id = module.vpc.public_subnet_ids[0]
  # ...
}
```

## Module Structure

### Standard Module Structure
```
terraform-aws-vpc/
├── README.md              # Module documentation
├── main.tf                # Primary resource definitions
├── variables.tf           # Input variable declarations
├── outputs.tf             # Output value declarations
├── versions.tf            # Provider version constraints
├── examples/              # Example usage
│   ├── complete/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── simple/
│       ├── main.tf
│       └── outputs.tf
├── modules/               # Nested modules
│   ├── subnets/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── security-groups/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── tests/                 # Module tests
    └── vpc_test.go
```

### Minimal Module Example

#### variables.tf
```hcl
variable "vpc_name" {
  description = "Name of the VPC"
  type        = string
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
  description = "List of availability zones"
  type        = list(string)
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
```

#### main.tf
```hcl
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    {
      Name = var.vpc_name
    },
    var.tags
  )
}

resource "aws_subnet" "public" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = true

  tags = merge(
    {
      Name = "${var.vpc_name}-public-${var.availability_zones[count.index]}"
      Type = "public"
    },
    var.tags
  )
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    {
      Name = "${var.vpc_name}-igw"
    },
    var.tags
  )
}
```

#### outputs.tf
```hcl
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "public_subnet_cidrs" {
  description = "List of public subnet CIDR blocks"
  value       = aws_subnet.public[*].cidr_block
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}
```

#### versions.tf
```hcl
terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}
```

## Module Sources

### Local Paths
```hcl
module "vpc" {
  source = "./modules/vpc"
}

module "vpc_relative" {
  source = "../shared-modules/vpc"
}

module "vpc_absolute" {
  source = "/opt/terraform/modules/vpc"
}
```

### Terraform Registry
```hcl
# Official HashiCorp modules
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"
}

# Specific version constraints
module "vpc_latest_minor" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.1"  # >= 5.1.0, < 5.2.0
}

module "vpc_minimum" {
  source  = "terraform-aws-modules/vpc/aws"
  version = ">= 5.0"
}
```

### GitHub
```hcl
# Public repo
module "vpc" {
  source = "github.com/terraform-aws-modules/terraform-aws-vpc"
}

# Specific branch
module "vpc_dev" {
  source = "github.com/terraform-aws-modules/terraform-aws-vpc?ref=develop"
}

# Specific tag
module "vpc_version" {
  source = "github.com/terraform-aws-modules/terraform-aws-vpc?ref=v5.1.2"
}

# Specific commit
module "vpc_commit" {
  source = "github.com/terraform-aws-modules/terraform-aws-vpc?ref=abc123def"
}

# Private repo with SSH
module "vpc_private" {
  source = "git@github.com:myorg/terraform-aws-vpc.git"
}

# Subdirectory
module "vpc_subdir" {
  source = "github.com/myorg/terraform-modules//aws/vpc"
}
```

### Git over HTTPS
```hcl
module "vpc" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v5.1.2"
}
```

### S3 Bucket
```hcl
module "vpc" {
  source = "s3::https://s3-us-west-2.amazonaws.com/my-bucket/vpc-module.zip"
}
```

### HTTP URLs
```hcl
module "vpc" {
  source = "https://example.com/modules/vpc-module.zip"
}
```

## Module Design Patterns

### 1. Simple Wrapper Module
Wraps a single resource with sensible defaults.

```hcl
# modules/s3-bucket/main.tf
resource "aws_s3_bucket" "main" {
  bucket = var.bucket_name

  tags = merge(
    {
      Name = var.bucket_name
    },
    var.tags
  )
}

resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
      kms_master_key_id = var.kms_key_id
    }
  }
}

resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

### 2. Composition Module
Combines multiple resources to create a complete solution.

```hcl
# modules/web-app/main.tf
module "vpc" {
  source = "./modules/vpc"

  vpc_name           = var.app_name
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
}

module "alb" {
  source = "./modules/alb"

  alb_name    = "${var.app_name}-alb"
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.public_subnet_ids
}

module "ecs_cluster" {
  source = "./modules/ecs"

  cluster_name = var.app_name
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.private_subnet_ids
  alb_arn      = module.alb.alb_arn
}

module "rds" {
  source = "./modules/rds"

  db_name    = var.app_name
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
}
```

### 3. Data-Driven Module
Uses input data structures to create multiple similar resources.

```hcl
# modules/iam-users/variables.tf
variable "users" {
  description = "Map of IAM users to create"
  type = map(object({
    path          = string
    force_destroy = bool
    tags          = map(string)
  }))
}

# modules/iam-users/main.tf
resource "aws_iam_user" "users" {
  for_each = var.users

  name          = each.key
  path          = each.value.path
  force_destroy = each.value.force_destroy

  tags = merge(
    {
      Name = each.key
    },
    each.value.tags
  )
}

# Usage
module "iam_users" {
  source = "./modules/iam-users"

  users = {
    "john.doe" = {
      path          = "/developers/"
      force_destroy = true
      tags          = { Team = "Backend" }
    }
    "jane.smith" = {
      path          = "/developers/"
      force_destroy = true
      tags          = { Team = "Frontend" }
    }
  }
}
```

### 4. Conditional Resource Module
Creates resources based on feature flags.

```hcl
# modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  # ...
}

resource "aws_vpc_ipv4_cidr_block_association" "secondary" {
  count = var.enable_secondary_cidr ? 1 : 0

  vpc_id     = aws_vpc.main.id
  cidr_block = var.secondary_cidr
}

resource "aws_vpc_endpoint" "s3" {
  count = var.enable_s3_endpoint ? 1 : 0

  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${data.aws_region.current.name}.s3"
}

resource "aws_flow_log" "main" {
  count = var.enable_flow_logs ? 1 : 0

  iam_role_arn    = aws_iam_role.flow_logs[0].arn
  log_destination = aws_cloudwatch_log_group.flow_logs[0].arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id
}
```

### 5. Factory Module
Creates multiple instances of resources from a list or map.

```hcl
# modules/security-group-factory/variables.tf
variable "security_groups" {
  description = "Map of security groups to create"
  type = map(object({
    description = string
    ingress_rules = list(object({
      from_port   = number
      to_port     = number
      protocol    = string
      cidr_blocks = list(string)
      description = string
    }))
    egress_rules = list(object({
      from_port   = number
      to_port     = number
      protocol    = string
      cidr_blocks = list(string)
      description = string
    }))
  }))
}

# modules/security-group-factory/main.tf
resource "aws_security_group" "groups" {
  for_each = var.security_groups

  name        = each.key
  description = each.value.description
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = each.value.ingress_rules
    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
      description = ingress.value.description
    }
  }

  dynamic "egress" {
    for_each = each.value.egress_rules
    content {
      from_port   = egress.value.from_port
      to_port     = egress.value.to_port
      protocol    = egress.value.protocol
      cidr_blocks = egress.value.cidr_blocks
      description = egress.value.description
    }
  }
}
```

### 6. Multi-Region Module
Deploys resources across multiple regions.

```hcl
# modules/multi-region-s3/main.tf
terraform {
  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = ">= 5.0"
      configuration_aliases = [aws.primary, aws.replica]
    }
  }
}

resource "aws_s3_bucket" "primary" {
  provider = aws.primary
  bucket   = "${var.bucket_name}-primary"
}

resource "aws_s3_bucket" "replica" {
  provider = aws.replica
  bucket   = "${var.bucket_name}-replica"
}

resource "aws_s3_bucket_replication_configuration" "replication" {
  provider = aws.primary
  bucket   = aws_s3_bucket.primary.id
  role     = aws_iam_role.replication.arn

  rule {
    id     = "replicate-all"
    status = "Enabled"

    destination {
      bucket        = aws_s3_bucket.replica.arn
      storage_class = "STANDARD_IA"
    }
  }
}

# Usage
provider "aws" {
  alias  = "us_east"
  region = "us-east-1"
}

provider "aws" {
  alias  = "us_west"
  region = "us-west-2"
}

module "replicated_bucket" {
  source = "./modules/multi-region-s3"

  providers = {
    aws.primary = aws.us_east
    aws.replica = aws.us_west
  }

  bucket_name = "my-replicated-bucket"
}
```

## Module Best Practices

### 1. Clear Input Variables
```hcl
variable "vpc_cidr" {
  description = "CIDR block for the VPC. Must be a valid IPv4 CIDR."
  type        = string

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "Must be a valid IPv4 CIDR block address."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
```

### 2. Useful Outputs
```hcl
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "List of IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "nat_gateway_ips" {
  description = "List of Elastic IPs associated with NAT Gateways"
  value       = aws_eip.nat[*].public_ip
}
```

### 3. Consistent Naming
```hcl
locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Module      = "vpc"
    },
    var.tags
  )
}

resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr

  tags = merge(
    {
      Name = "${local.name_prefix}-vpc"
    },
    local.common_tags
  )
}
```

### 4. Version Constraints
```hcl
terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0, < 6.0"
    }
  }
}
```

### 5. Documentation
```markdown
# AWS VPC Module

Creates a VPC with public and private subnets across multiple availability zones.

## Features

- VPC with configurable CIDR block
- Public and private subnets
- Internet Gateway for public subnets
- NAT Gateways for private subnets
- VPC Flow Logs (optional)
- VPC Endpoints (optional)

## Usage

```hcl
module "vpc" {
  source = "./modules/vpc"

  vpc_name           = "my-vpc"
  vpc_cidr           = "10.0.0.0/16"
  availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

  enable_nat_gateway = true
  enable_flow_logs   = true

  tags = {
    Project = "my-project"
  }
}
```

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.6 |
| aws | >= 5.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| vpc_name | Name of the VPC | `string` | n/a | yes |
| vpc_cidr | CIDR block for VPC | `string` | `"10.0.0.0/16"` | no |

## Outputs

| Name | Description |
|------|-------------|
| vpc_id | ID of the VPC |
| public_subnet_ids | List of public subnet IDs |
```

### 6. Handle Optional Features
```hcl
variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use a single NAT Gateway instead of one per AZ"
  type        = bool
  default     = false
}

locals {
  nat_gateway_count = var.enable_nat_gateway ? (
    var.single_nat_gateway ? 1 : length(var.availability_zones)
  ) : 0
}

resource "aws_nat_gateway" "main" {
  count = local.nat_gateway_count

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(
    {
      Name = "${var.vpc_name}-nat-${count.index + 1}"
    },
    var.tags
  )
}
```

## Module Examples

### Complete VPC Module
```hcl
# modules/vpc/variables.tf
variable "vpc_name" {
  description = "Name of the VPC"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = []
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = []
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use single NAT Gateway"
  type        = bool
  default     = false
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames in VPC"
  type        = bool
  default     = true
}

variable "enable_dns_support" {
  description = "Enable DNS support in VPC"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

# modules/vpc/main.tf
locals {
  # Calculate subnet CIDRs if not provided
  public_subnet_cidrs = length(var.public_subnet_cidrs) > 0 ? var.public_subnet_cidrs : [
    for i in range(length(var.availability_zones)) :
    cidrsubnet(var.vpc_cidr, 8, i)
  ]

  private_subnet_cidrs = length(var.private_subnet_cidrs) > 0 ? var.private_subnet_cidrs : [
    for i in range(length(var.availability_zones)) :
    cidrsubnet(var.vpc_cidr, 8, i + length(var.availability_zones))
  ]

  nat_gateway_count = var.enable_nat_gateway ? (
    var.single_nat_gateway ? 1 : length(var.availability_zones)
  ) : 0
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support

  tags = merge(
    {
      Name = var.vpc_name
    },
    var.tags
  )
}

resource "aws_subnet" "public" {
  count = length(var.availability_zones)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = local.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    {
      Name = "${var.vpc_name}-public-${var.availability_zones[count.index]}"
      Type = "public"
    },
    var.tags
  )
}

resource "aws_subnet" "private" {
  count = length(var.availability_zones)

  vpc_id            = aws_vpc.main.id
  cidr_block        = local.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    {
      Name = "${var.vpc_name}-private-${var.availability_zones[count.index]}"
      Type = "private"
    },
    var.tags
  )
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    {
      Name = "${var.vpc_name}-igw"
    },
    var.tags
  )
}

resource "aws_eip" "nat" {
  count = local.nat_gateway_count

  domain = "vpc"

  tags = merge(
    {
      Name = "${var.vpc_name}-nat-eip-${count.index + 1}"
    },
    var.tags
  )

  depends_on = [aws_internet_gateway.main]
}

resource "aws_nat_gateway" "main" {
  count = local.nat_gateway_count

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(
    {
      Name = "${var.vpc_name}-nat-${count.index + 1}"
    },
    var.tags
  )

  depends_on = [aws_internet_gateway.main]
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    {
      Name = "${var.vpc_name}-public-rt"
      Type = "public"
    },
    var.tags
  )
}

resource "aws_route" "public_internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}

resource "aws_route_table_association" "public" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  count = length(var.availability_zones)

  vpc_id = aws_vpc.main.id

  tags = merge(
    {
      Name = "${var.vpc_name}-private-rt-${var.availability_zones[count.index]}"
      Type = "private"
    },
    var.tags
  )
}

resource "aws_route" "private_nat" {
  count = var.enable_nat_gateway ? length(var.availability_zones) : 0

  route_table_id         = aws_route_table.private[count.index].id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = var.single_nat_gateway ? aws_nat_gateway.main[0].id : aws_nat_gateway.main[count.index].id
}

resource "aws_route_table_association" "private" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# modules/vpc/outputs.tf
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "public_subnet_cidrs" {
  description = "List of public subnet CIDR blocks"
  value       = aws_subnet.public[*].cidr_block
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "private_subnet_cidrs" {
  description = "List of private subnet CIDR blocks"
  value       = aws_subnet.private[*].cidr_block
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_ids" {
  description = "List of NAT Gateway IDs"
  value       = aws_nat_gateway.main[*].id
}

output "nat_gateway_ips" {
  description = "List of NAT Gateway Elastic IP addresses"
  value       = aws_eip.nat[*].public_ip
}
```

## Module Publishing

### Terraform Registry Requirements
1. GitHub repository named `terraform-<PROVIDER>-<NAME>`
2. Repository description
3. Standard module structure
4. Semantic versioning tags (x.y.z)
5. `LICENSE` file
6. `README.md` with examples

### Example Registry Module
```
terraform-aws-vpc/
├── .github/
│   └── workflows/
│       └── terraform.yml
├── examples/
│   ├── complete/
│   └── simple/
├── LICENSE
├── README.md
├── main.tf
├── variables.tf
├── outputs.tf
└── versions.tf
```

## Module Testing

### Manual Testing
```bash
cd examples/complete
terraform init
terraform plan
terraform apply
terraform destroy
```

### Automated Testing with Terratest
```go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestVPCModule(t *testing.T) {
    t.Parallel()

    terraformOptions := &terraform.Options{
        TerraformDir: "../examples/complete",
        Vars: map[string]interface{}{
            "vpc_name": "test-vpc",
            "vpc_cidr": "10.0.0.0/16",
            "availability_zones": []string{"us-west-2a", "us-west-2b"},
        },
    }

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    vpcID := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcID)

    subnetIDs := terraform.OutputList(t, terraformOptions, "public_subnet_ids")
    assert.Len(t, subnetIDs, 2)
}
```

### CI/CD Pipeline Example
```yaml
name: Terraform Module Tests

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: hashicorp/setup-terraform@v2
      - run: terraform fmt -check
      - run: terraform init
      - run: terraform validate

  test:
    runs-on: ubuntu-latest
    needs: validate
    steps:
      - uses: actions/checkout@v3
      - uses: hashicorp/setup-terraform@v2
      - uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      - run: go test -v ./tests/
```
