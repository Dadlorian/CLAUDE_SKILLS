# Terraform Network Infrastructure Guide

## Getting Started

### Installation
```bash
# macOS
brew install terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
unzip terraform_1.5.0_linux_amd64.zip
mv terraform /usr/local/bin/

# Verify installation
terraform version
```

### Project Structure
```
network-infrastructure/
├── main.tf                  # Main configuration
├── variables.tf             # Input variables
├── outputs.tf               # Output values
├── terraform.tfvars         # Variable values (local, not committed)
├── terraform.tfvars.example # Example file for documentation
├── providers.tf             # Provider configuration
├── modules/
│   ├── network/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── routing/
│   └── security/
├── environments/
│   ├── dev/
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   ├── prod/
└── .gitignore
```

## Basic Configuration

### main.tf
```hcl
terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "terraform-state-prod"
    key            = "network/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Project     = "NetworkInfra"
    }
  }
}
```

### variables.tf
```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Must be dev, staging, or prod."
  }
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "Must be a valid CIDR block."
  }
}

variable "subnets" {
  description = "Subnet configuration"
  type = map(object({
    cidr              = string
    availability_zone = string
    public            = bool
  }))

  default = {
    public-1 = {
      cidr              = "10.0.1.0/24"
      availability_zone = "us-east-1a"
      public            = true
    }
    private-1 = {
      cidr              = "10.0.2.0/24"
      availability_zone = "us-east-1b"
      public            = false
    }
  }
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Team       = "NetworkOps"
    CostCenter = "Infrastructure"
  }
}
```

### outputs.tf
```hcl
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}

output "subnet_ids" {
  description = "Subnet IDs"
  value       = {
    for subnet in aws_subnet.main : subnet.tags["Name"] => subnet.id
  }
}

output "public_subnets" {
  description = "Public subnet IDs"
  value = [
    for subnet in aws_subnet.main : subnet.id
    if subnet.map_public_ip_on_launch
  ]
}

output "private_subnets" {
  description = "Private subnet IDs"
  value = [
    for subnet in aws_subnet.main : subnet.id
    if !subnet.map_public_ip_on_launch
  ]
}

output "nat_gateway_eips" {
  description = "NAT Gateway Elastic IP addresses"
  value = [
    for eip in aws_eip.nat : eip.public_ip
  ]
}
```

## VPC Configuration

### VPC and Subnets
```hcl
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-vpc"
    }
  )
}

resource "aws_subnet" "main" {
  for_each = var.subnets

  vpc_id                  = aws_vpc.main.id
  cidr_block              = each.value.cidr
  availability_zone       = each.value.availability_zone
  map_public_ip_on_launch = each.value.public

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${each.key}"
      Type = each.value.public ? "public" : "private"
    }
  )
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-igw"
    }
  )
}
```

### Route Tables
```hcl
# Public route table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block      = "0.0.0.0/0"
    gateway_id      = aws_internet_gateway.main.id
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-public-rt"
    }
  )
}

# Associate public subnets
resource "aws_route_table_association" "public" {
  for_each = {
    for k, v in var.subnets : k => v if v.public
  }

  subnet_id      = aws_subnet.main[each.key].id
  route_table_id = aws_route_table.public.id
}

# Private route table (with NAT)
resource "aws_route_table" "private" {
  count  = var.enable_nat_gateway ? 1 : 0
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[0].id
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-private-rt"
    }
  )
}

# Associate private subnets
resource "aws_route_table_association" "private" {
  for_each = {
    for k, v in var.subnets : k => v if !v.public
  }

  subnet_id      = aws_subnet.main[each.key].id
  route_table_id = var.enable_nat_gateway ? aws_route_table.private[0].id : ""
}
```

### NAT Gateway
```hcl
resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? 1 : 0
  domain = "vpc"

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-nat-eip"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

resource "aws_nat_gateway" "main" {
  count         = var.enable_nat_gateway ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = [for subnet in aws_subnet.main : subnet.id if subnet.map_public_ip_on_launch][0]

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-nat"
    }
  )

  depends_on = [aws_internet_gateway.main]
}
```

## Security Groups

### Network ACLs and Security Groups
```hcl
resource "aws_security_group" "allow_ssh" {
  name_prefix = "allow-ssh-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Restrict in production
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-allow-ssh"
    }
  )
}

resource "aws_security_group" "allow_http_https" {
  name_prefix = "allow-http-https-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-allow-http-https"
    }
  )
}
```

## Modules

### Module Structure
```hcl
# modules/network/main.tf
variable "vpc_cidr" {
  type = string
}

variable "environment" {
  type = string
}

resource "aws_vpc" "vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
}

output "vpc_id" {
  value = aws_vpc.vpc.id
}

# Main configuration using module
module "network" {
  source = "./modules/network"

  vpc_cidr    = var.vpc_cidr
  environment = var.environment
}
```

## Workflow Commands

### Initialize
```bash
# Download providers and initialize
terraform init

# Upgrade providers
terraform init -upgrade
```

### Validate
```bash
# Check syntax
terraform validate

# Format code
terraform fmt -recursive
```

### Plan
```bash
# Generate execution plan
terraform plan

# Save plan to file
terraform plan -out=tfplan

# Show plan
terraform show tfplan
```

### Apply
```bash
# Apply changes (with approval)
terraform apply

# Apply without approval
terraform apply -auto-approve

# Apply from saved plan
terraform apply tfplan
```

### Destroy
```bash
# Destroy resources (with confirmation)
terraform destroy

# Destroy without confirmation
terraform destroy -auto-approve

# Destroy specific resource
terraform destroy -target='aws_instance.web'
```

## State Management

### Local State
```bash
# Show state
terraform state list
terraform state show 'aws_vpc.main'

# Remove from state (doesn't delete resource)
terraform state rm 'aws_instance.web'

# Move resources
terraform state mv 'aws_instance.web' 'aws_instance.app'
```

### Remote State (S3 + DynamoDB)
```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

Initialize with remote backend:
```bash
terraform init -backend=true \
  -backend-config="bucket=my-terraform-state" \
  -backend-config="key=prod/terraform.tfstate" \
  -backend-config="region=us-east-1"
```

## Environment Management

### Environment Variables
```bash
# Use different tfvars for each environment
terraform apply -var-file="environments/prod/terraform.tfvars"

# Override variables
terraform apply -var="environment=prod" -var="vpc_cidr=10.0.0.0/16"
```

### Workspaces
```bash
# Create workspace
terraform workspace new prod
terraform workspace new dev

# List workspaces
terraform workspace list

# Switch workspace
terraform workspace select prod

# Delete workspace
terraform workspace delete dev
```

## Best Practices

1. **Use Variable Validation**
   ```hcl
   variable "port" {
     type = number
     validation {
       condition     = var.port >= 1 && var.port <= 65535
       error_message = "Port must be between 1 and 65535."
     }
   }
   ```

2. **Implement Naming Conventions**
   ```hcl
   locals {
     name_prefix = "${var.environment}-${var.project}"
   }

   resource "aws_subnet" "main" {
     tags = {
       Name = "${local.name_prefix}-subnet"
     }
   }
   ```

3. **Use Modules for Reusability**
   ```hcl
   module "vpc" {
     source = "./modules/vpc"
     cidr   = var.vpc_cidr
   }
   ```

4. **Commit State Locks**
   ```bash
   # Never commit tfstate files
   echo "*.tfstate" >> .gitignore
   echo "*.tfstate.*" >> .gitignore
   echo ".terraform/" >> .gitignore
   ```

5. **Use terraform fmt**
   ```bash
   terraform fmt -recursive
   ```

---

**Last Updated**: 2025-11-19
**Reference**: terraform.io/docs, registry.terraform.io
