# Terraform Modules Reference

## Module Basics

### What is a Module?

A Terraform module is a container for multiple resources that are used together. Every Terraform configuration has at least one module, known as the root module, which consists of the resources defined in the `.tf` files in the main working directory.

### Module Structure

```
modules/
└── vpc/
    ├── main.tf          # Primary resources
    ├── variables.tf     # Input variables
    ├── outputs.tf       # Output values
    ├── versions.tf      # Provider requirements
    ├── README.md        # Documentation
    ├── examples/        # Usage examples
    │   └── complete/
    │       ├── main.tf
    │       └── variables.tf
    └── tests/           # Module tests
        └── vpc_test.go
```

## Creating a Module

### main.tf
```hcl
# VPC
resource "aws_vpc" "this" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support

  tags = merge(
    {
      Name = var.name
    },
    var.tags
  )
}

# Internet Gateway
resource "aws_internet_gateway" "this" {
  count = var.create_igw ? 1 : 0

  vpc_id = aws_vpc.this.id

  tags = merge(
    {
      Name = "${var.name}-igw"
    },
    var.tags
  )
}

# Public Subnets
resource "aws_subnet" "public" {
  count = length(var.public_subnet_cidrs)

  vpc_id                  = aws_vpc.this.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    {
      Name = "${var.name}-public-${var.availability_zones[count.index]}"
      Type = "public"
    },
    var.tags
  )
}

# Private Subnets
resource "aws_subnet" "private" {
  count = length(var.private_subnet_cidrs)

  vpc_id            = aws_vpc.this.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    {
      Name = "${var.name}-private-${var.availability_zones[count.index]}"
      Type = "private"
    },
    var.tags
  )
}

# NAT Gateways
resource "aws_eip" "nat" {
  count = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(var.public_subnet_cidrs)) : 0

  domain = "vpc"

  tags = merge(
    {
      Name = "${var.name}-nat-${count.index}"
    },
    var.tags
  )
}

resource "aws_nat_gateway" "this" {
  count = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(var.public_subnet_cidrs)) : 0

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(
    {
      Name = "${var.name}-nat-${count.index}"
    },
    var.tags
  )

  depends_on = [aws_internet_gateway.this]
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  tags = merge(
    {
      Name = "${var.name}-public"
    },
    var.tags
  )
}

resource "aws_route" "public_internet_gateway" {
  count = var.create_igw ? 1 : 0

  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.this[0].id
}

resource "aws_route_table_association" "public" {
  count = length(var.public_subnet_cidrs)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  count = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(var.private_subnet_cidrs)) : 0

  vpc_id = aws_vpc.this.id

  tags = merge(
    {
      Name = "${var.name}-private-${count.index}"
    },
    var.tags
  )
}

resource "aws_route" "private_nat_gateway" {
  count = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(var.private_subnet_cidrs)) : 0

  route_table_id         = aws_route_table.private[count.index].id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.this[count.index].id
}

resource "aws_route_table_association" "private" {
  count = length(var.private_subnet_cidrs)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[var.single_nat_gateway ? 0 : count.index].id
}
```

### variables.tf
```hcl
variable "name" {
  description = "Name to be used on all resources"
  type        = string
}

variable "cidr_block" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "Must be a valid CIDR block."
  }
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

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames in the VPC"
  type        = bool
  default     = true
}

variable "enable_dns_support" {
  description = "Enable DNS support in the VPC"
  type        = bool
  default     = true
}

variable "create_igw" {
  description = "Create Internet Gateway"
  type        = bool
  default     = true
}

variable "enable_nat_gateway" {
  description = "Create NAT Gateway(s)"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use a single NAT Gateway for all private subnets"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}
```

### outputs.tf
```hcl
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.this.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.this.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "nat_gateway_ids" {
  description = "IDs of NAT Gateways"
  value       = aws_nat_gateway.this[*].id
}

output "internet_gateway_id" {
  description = "ID of Internet Gateway"
  value       = try(aws_internet_gateway.this[0].id, null)
}

output "public_route_table_id" {
  description = "ID of public route table"
  value       = aws_route_table.public.id
}

output "private_route_table_ids" {
  description = "IDs of private route tables"
  value       = aws_route_table.private[*].id
}
```

### versions.tf
```hcl
terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}
```

### README.md
```markdown
# VPC Module

Terraform module to create AWS VPC with public and private subnets across multiple availability zones.

## Features

- VPC with configurable CIDR
- Public and private subnets
- Internet Gateway for public subnets
- NAT Gateway(s) for private subnets
- Customizable route tables
- Flexible subnet configuration

## Usage

```hcl
module "vpc" {
  source = "./modules/vpc"

  name               = "production-vpc"
  cidr_block         = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

  public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = false

  tags = {
    Environment = "production"
    Project     = "my-project"
  }
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| name | Name for VPC | string | n/a | yes |
| cidr_block | VPC CIDR block | string | "10.0.0.0/16" | no |
| availability_zones | List of AZs | list(string) | n/a | yes |
| public_subnet_cidrs | Public subnet CIDRs | list(string) | [] | no |
| private_subnet_cidrs | Private subnet CIDRs | list(string) | [] | no |

## Outputs

| Name | Description |
|------|-------------|
| vpc_id | VPC ID |
| public_subnet_ids | Public subnet IDs |
| private_subnet_ids | Private subnet IDs |

## Examples

See [examples/](./examples/) directory.
```

## Using Modules

### Local Module
```hcl
module "vpc" {
  source = "./modules/vpc"

  name               = "production"
  cidr_block         = "10.0.0.0/16"
  availability_zones = data.aws_availability_zones.available.names

  public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]

  tags = {
    Environment = "production"
  }
}

# Use module outputs
resource "aws_instance" "web" {
  subnet_id = module.vpc.public_subnet_ids[0]
  # ...
}
```

### Git Repository
```hcl
module "vpc" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v5.0.0"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = true

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}
```

### Terraform Registry
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}
```

## Module Patterns

### Conditional Resources
```hcl
# Create resource based on condition
resource "aws_nat_gateway" "this" {
  count = var.enable_nat_gateway ? 1 : 0

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
}

# Output handling null
output "nat_gateway_id" {
  value = var.enable_nat_gateway ? aws_nat_gateway.this[0].id : null
}
```

### Dynamic Blocks
```hcl
resource "aws_security_group" "this" {
  name        = var.name
  description = var.description
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
      description = ingress.value.description
    }
  }

  dynamic "egress" {
    for_each = var.egress_rules
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

### For Each with Maps
```hcl
variable "instances" {
  type = map(object({
    instance_type = string
    ami           = string
  }))
}

resource "aws_instance" "this" {
  for_each = var.instances

  instance_type = each.value.instance_type
  ami           = each.value.ami

  tags = {
    Name = each.key
  }
}

# Usage
module "instances" {
  source = "./modules/instance"

  instances = {
    web = {
      instance_type = "t3.micro"
      ami           = "ami-12345678"
    }
    api = {
      instance_type = "t3.small"
      ami           = "ami-87654321"
    }
  }
}
```

### Module Composition
```hcl
# Network module uses VPC module
module "vpc" {
  source = "./modules/vpc"
  # ...
}

# Application module uses network outputs
module "application" {
  source = "./modules/application"

  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.private_subnet_ids
  security_group = module.vpc.default_security_group_id
}
```

## Module Testing

### Structure
```
modules/vpc/
├── main.tf
├── variables.tf
├── outputs.tf
├── tests/
│   ├── vpc_test.go
│   └── fixtures/
│       └── complete/
│           ├── main.tf
│           └── outputs.tf
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

func TestVPCModule(t *testing.T) {
    t.Parallel()

    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "./fixtures/complete",
        Vars: map[string]interface{}{
            "name":       "test-vpc",
            "cidr_block": "10.0.0.0/16",
            "availability_zones": []string{
                "us-east-1a",
                "us-east-1b",
            },
            "public_subnet_cidrs": []string{
                "10.0.1.0/24",
                "10.0.2.0/24",
            },
            "private_subnet_cidrs": []string{
                "10.0.11.0/24",
                "10.0.12.0/24",
            },
        },
    })

    defer terraform.Destroy(t, terraformOptions)

    terraform.InitAndApply(t, terraformOptions)

    // Test outputs
    vpcID := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcID)

    publicSubnetIDs := terraform.OutputList(t, terraformOptions, "public_subnet_ids")
    assert.Equal(t, 2, len(publicSubnetIDs))

    privateSubnetIDs := terraform.OutputList(t, terraformOptions, "private_subnet_ids")
    assert.Equal(t, 2, len(privateSubnetIDs))
}
```

## Module Best Practices

### 1. Use Consistent Naming
```hcl
# Good
variable "name" {}
variable "vpc_id" {}
variable "subnet_ids" {}

# Avoid
variable "VPCName" {}
variable "vpc" {}
variable "subnets" {}
```

### 2. Provide Defaults Where Appropriate
```hcl
variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "enable_monitoring" {
  type    = bool
  default = false
}
```

### 3. Use Variable Validation
```hcl
variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "cidr_block" {
  type = string

  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "Must be a valid CIDR block."
  }
}
```

### 4. Document Everything
```hcl
variable "name" {
  description = "Name to be used on all resources as prefix"
  type        = string
}

output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.this.id
}
```

### 5. Use Outputs Effectively
```hcl
# Export important values
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.this.id
}

# Export resource objects for maximum flexibility
output "vpc" {
  description = "VPC resource object"
  value       = aws_vpc.this
}
```

### 6. Version Constraints
```hcl
terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

### 7. Use Data Sources
```hcl
# Instead of hardcoding
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}
```

### 8. Tagging Strategy
```hcl
locals {
  common_tags = merge(
    var.tags,
    {
      ManagedBy = "Terraform"
      Module    = "vpc"
    }
  )
}

resource "aws_vpc" "this" {
  # ...
  tags = merge(
    local.common_tags,
    {
      Name = var.name
    }
  )
}
```

## Module Registry Publishing

### Directory Structure
```
terraform-aws-vpc/
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
├── README.md
├── LICENSE
├── examples/
│   ├── complete/
│   └── simple/
└── .github/
    └── workflows/
        └── terraform.yml
```

### Naming Convention
```
terraform-<PROVIDER>-<NAME>
terraform-aws-vpc
terraform-azurerm-network
terraform-google-gke
```

### Semantic Versioning
```
v1.0.0 - Major version
v1.1.0 - Minor version (backward compatible)
v1.1.1 - Patch version (bug fixes)
```

### Git Tags
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Resources

- Module Development: terraform.io/docs/language/modules/develop
- Registry Publishing: terraform.io/docs/registry/modules/publish
- Best Practices: terraform.io/docs/language/modules/develop/best-practices
- Community Modules: registry.terraform.io/browse/modules
