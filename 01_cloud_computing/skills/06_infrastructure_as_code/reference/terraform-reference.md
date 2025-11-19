# Terraform Reference

## Overview

Terraform is an open-source Infrastructure as Code tool created by HashiCorp that enables you to define and provision infrastructure using a declarative configuration language (HCL).

## Core Concepts

### HCL Syntax

**Resource Blocks**
```hcl
resource "resource_type" "resource_name" {
  argument1 = "value1"
  argument2 = "value2"

  nested_block {
    nested_argument = "value"
  }
}
```

**Data Sources**
```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}
```

**Variables**
```hcl
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"

  validation {
    condition     = can(regex("^t3\\.", var.instance_type))
    error_message = "Instance type must be from the t3 family."
  }
}
```

**Outputs**
```hcl
output "instance_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.web.public_ip
  sensitive   = false
}
```

**Locals**
```hcl
locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = var.project_name
  }

  vpc_cidr_blocks = {
    dev     = "10.0.0.0/16"
    staging = "10.1.0.0/16"
    prod    = "10.2.0.0/16"
  }
}
```

### Type System

**Primitive Types**
```hcl
variable "string_example" {
  type    = string
  default = "hello"
}

variable "number_example" {
  type    = number
  default = 42
}

variable "bool_example" {
  type    = bool
  default = true
}
```

**Complex Types**
```hcl
# List
variable "availability_zones" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

# Map
variable "instance_types" {
  type = map(string)
  default = {
    dev  = "t3.micro"
    prod = "t3.large"
  }
}

# Set
variable "allowed_cidrs" {
  type    = set(string)
  default = ["10.0.0.0/8", "172.16.0.0/12"]
}

# Object
variable "server_config" {
  type = object({
    instance_type = string
    volume_size   = number
    monitoring    = bool
  })
  default = {
    instance_type = "t3.micro"
    volume_size   = 20
    monitoring    = true
  }
}

# Tuple
variable "cidr_blocks" {
  type    = tuple([string, number, bool])
  default = ["10.0.0.0/16", 3, true]
}
```

## Functions

### String Functions
```hcl
# String manipulation
upper("hello")                          # "HELLO"
lower("WORLD")                          # "world"
title("hello world")                    # "Hello World"
trimspace("  hello  ")                  # "hello"
format("Hello, %s!", "world")           # "Hello, world!"
join(", ", ["a", "b", "c"])            # "a, b, c"
split(",", "a,b,c")                    # ["a", "b", "c"]
replace("hello", "l", "r")             # "herro"
substr("hello", 0, 4)                  # "hell"
regex("^[a-z]+$", "abc")              # true
regexall("[0-9]+", "a1b2c3")          # ["1", "2", "3"]
```

### Collection Functions
```hcl
# Lists and sets
length([1, 2, 3])                      # 3
concat([1, 2], [3, 4])                 # [1, 2, 3, 4]
distinct([1, 2, 2, 3])                 # [1, 2, 3]
flatten([[1, 2], [3, 4]])              # [1, 2, 3, 4]
reverse([1, 2, 3])                     # [3, 2, 1]
sort(["c", "a", "b"])                  # ["a", "b", "c"]
slice([1, 2, 3, 4], 1, 3)             # [2, 3]
contains(["a", "b"], "a")              # true
index(["a", "b", "c"], "b")           # 1

# Maps
keys({a = 1, b = 2})                   # ["a", "b"]
values({a = 1, b = 2})                 # [1, 2]
lookup({a = 1, b = 2}, "a", 0)        # 1
merge({a = 1}, {b = 2})               # {a = 1, b = 2}
zipmap(["a", "b"], [1, 2])            # {a = 1, b = 2}
```

### Numeric Functions
```hcl
abs(-5)                                # 5
ceil(5.1)                              # 6
floor(5.9)                             # 5
max(5, 12, 9)                          # 12
min(5, 12, 9)                          # 5
parseint("100", 10)                    # 100
pow(2, 3)                              # 8
signum(-5)                             # -1
```

### Encoding Functions
```hcl
base64encode("hello")                  # "aGVsbG8="
base64decode("aGVsbG8=")              # "hello"
jsonencode({a = 1})                    # "{\"a\":1}"
jsondecode("{\"a\":1}")                # {a = 1}
yamlencode({a = 1})                    # "a: 1\n"
yamldecode("a: 1")                     # {a = 1}
```

### Filesystem Functions
```hcl
file("path/to/file.txt")               # Read file contents
fileexists("path/to/file")             # Check if file exists
fileset(".", "*.tf")                   # Find files matching pattern
templatefile("template.tpl", {         # Render template
  name = "world"
})
```

### IP Network Functions
```hcl
cidrhost("10.0.0.0/16", 5)             # "10.0.0.5"
cidrnetmask("10.0.0.0/16")             # "255.255.0.0"
cidrsubnet("10.0.0.0/16", 8, 2)        # "10.0.2.0/24"
cidrsubnets("10.0.0.0/16", 8, 8, 8)   # ["10.0.0.0/24", ...]
```

### Type Conversion Functions
```hcl
tostring(42)                           # "42"
tonumber("42")                         # 42
tobool("true")                         # true
tolist(["a", "b"])                     # ["a", "b"]
toset(["a", "b", "a"])                # ["a", "b"]
tomap({a = 1})                         # {a = 1}
```

### Advanced Functions
```hcl
# Conditional
condition ? true_val : false_val

# For expressions
[for s in var.list : upper(s)]
{for k, v in var.map : k => upper(v)}

# Dynamic blocks
dynamic "tag" {
  for_each = var.tags
  content {
    key   = tag.key
    value = tag.value
  }
}

# Splat expressions
aws_instance.web[*].id
aws_instance.web[*].public_ip

# Try function
try(var.optional_value, "default")

# Can function
can(regex("^[a-z]+$", var.name))

# Sensitive function
sensitive("secret-value")
```

## Resource Meta-Arguments

### depends_on
```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  depends_on = [aws_security_group.web]
}
```

### count
```hcl
resource "aws_instance" "web" {
  count = 3

  ami           = "ami-12345678"
  instance_type = "t3.micro"

  tags = {
    Name = "web-${count.index}"
  }
}

# Reference: aws_instance.web[0].id
```

### for_each
```hcl
resource "aws_instance" "web" {
  for_each = toset(["dev", "staging", "prod"])

  ami           = "ami-12345678"
  instance_type = var.instance_types[each.key]

  tags = {
    Name        = "web-${each.key}"
    Environment = each.key
  }
}

# Reference: aws_instance.web["dev"].id
```

### provider
```hcl
provider "aws" {
  alias  = "west"
  region = "us-west-2"
}

resource "aws_instance" "web" {
  provider = aws.west

  ami           = "ami-12345678"
  instance_type = "t3.micro"
}
```

### lifecycle
```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  lifecycle {
    create_before_destroy = true
    prevent_destroy       = true
    ignore_changes        = [tags]

    precondition {
      condition     = var.instance_type != ""
      error_message = "Instance type must be specified."
    }

    postcondition {
      condition     = self.public_ip != ""
      error_message = "Instance must have a public IP."
    }
  }
}
```

## Provisioners

**file**
```hcl
resource "aws_instance" "web" {
  # ...

  provisioner "file" {
    source      = "script.sh"
    destination = "/tmp/script.sh"

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("~/.ssh/id_rsa")
      host        = self.public_ip
    }
  }
}
```

**remote-exec**
```hcl
provisioner "remote-exec" {
  inline = [
    "chmod +x /tmp/script.sh",
    "/tmp/script.sh",
  ]

  connection {
    type = "ssh"
    user = "ubuntu"
    host = self.public_ip
  }
}
```

**local-exec**
```hcl
provisioner "local-exec" {
  command = "echo ${self.private_ip} >> private_ips.txt"
}
```

## Modules

### Module Structure
```
modules/
└── vpc/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    ├── versions.tf
    └── README.md
```

### Module Usage
```hcl
module "vpc" {
  source = "./modules/vpc"
  # or: source = "git::https://github.com/org/repo.git//modules/vpc?ref=v1.0.0"
  # or: source = "app.terraform.io/org/vpc/aws"

  version = "~> 3.0"

  name            = "production-vpc"
  cidr            = "10.0.0.0/16"
  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = false

  tags = {
    Environment = "production"
  }
}

# Access outputs
output "vpc_id" {
  value = module.vpc.vpc_id
}
```

## State Management

### Backend Configuration

**S3 Backend**
```hcl
terraform {
  backend "s3" {
    bucket         = "terraform-state-bucket"
    key            = "prod/vpc/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
    kms_key_id     = "arn:aws:kms:us-east-1:ACCOUNT:key/KEY-ID"

    # Workspace-based keys
    workspace_key_prefix = "workspaces"
  }
}
```

**Terraform Cloud Backend**
```hcl
terraform {
  cloud {
    organization = "my-org"

    workspaces {
      name = "production-vpc"
      # or: tags = ["production", "vpc"]
    }
  }
}
```

### State Commands
```bash
# List resources in state
terraform state list

# Show resource details
terraform state show aws_instance.web

# Move resource to new address
terraform state mv aws_instance.web aws_instance.web_server

# Remove resource from state
terraform state rm aws_instance.web

# Pull remote state
terraform state pull > terraform.tfstate

# Push local state to remote
terraform state push terraform.tfstate

# Replace provider address
terraform state replace-provider hashicorp/aws registry.terraform.io/hashicorp/aws
```

### Workspaces
```bash
# Create workspace
terraform workspace new dev

# List workspaces
terraform workspace list

# Select workspace
terraform workspace select prod

# Show current workspace
terraform workspace show

# Delete workspace
terraform workspace delete dev
```

## Advanced Features

### Import Existing Resources
```bash
# Import EC2 instance
terraform import aws_instance.web i-1234567890abcdef0

# Import with for_each
terraform import 'aws_instance.web["prod"]' i-1234567890abcdef0
```

### Moved Blocks
```hcl
moved {
  from = aws_instance.web
  to   = aws_instance.web_server
}

moved {
  from = module.networking
  to   = module.vpc
}
```

### Terraform Cloud Integration
```hcl
terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  cloud {
    organization = "my-org"

    workspaces {
      name = "production"
    }
  }
}
```

### Remote State Data Source
```hcl
data "terraform_remote_state" "vpc" {
  backend = "s3"

  config = {
    bucket = "terraform-state-bucket"
    key    = "vpc/terraform.tfstate"
    region = "us-east-1"
  }
}

resource "aws_instance" "web" {
  subnet_id = data.terraform_remote_state.vpc.outputs.private_subnet_ids[0]
  # ...
}
```

## CLI Commands

### Essential Commands
```bash
# Initialize working directory
terraform init
terraform init -upgrade                 # Upgrade providers
terraform init -migrate-state           # Migrate state

# Validate configuration
terraform validate

# Format code
terraform fmt
terraform fmt -recursive
terraform fmt -check

# Plan changes
terraform plan
terraform plan -out=tfplan
terraform plan -target=aws_instance.web
terraform plan -var="instance_type=t3.large"
terraform plan -var-file="prod.tfvars"

# Apply changes
terraform apply
terraform apply tfplan
terraform apply -auto-approve
terraform apply -target=aws_instance.web

# Destroy resources
terraform destroy
terraform destroy -auto-approve
terraform destroy -target=aws_instance.web

# Show current state
terraform show
terraform show tfplan

# Output values
terraform output
terraform output instance_ip
terraform output -json

# Refresh state
terraform refresh

# Graph dependencies
terraform graph | dot -Tpng > graph.png

# Console for testing expressions
terraform console
```

### Advanced Commands
```bash
# Taint resource for recreation
terraform taint aws_instance.web

# Untaint resource
terraform untaint aws_instance.web

# Force unlock state
terraform force-unlock LOCK_ID

# Get providers
terraform providers
terraform providers lock              # Update lock file

# Get version info
terraform version

# Test configurations (1.6+)
terraform test
```

## Configuration Best Practices

### Directory Structure
```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   └── prod/
├── modules/
│   ├── vpc/
│   ├── eks/
│   └── rds/
├── .terraform-version
├── .gitignore
└── README.md
```

### Variable Management
```hcl
# variables.tf
variable "environment" {
  description = "Environment name"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

# terraform.tfvars
environment = "production"
instance_type = "t3.large"

# Environment-specific
# dev.tfvars
environment = "dev"
instance_type = "t3.micro"
```

### Naming Conventions
```hcl
# Resource naming: <resource_type>_<name>
resource "aws_vpc" "main" {}
resource "aws_subnet" "private" {}
resource "aws_instance" "web_server" {}

# Variable naming: snake_case
variable "instance_type" {}
variable "vpc_cidr_block" {}

# Output naming: descriptive
output "vpc_id" {}
output "public_subnet_ids" {}

# Module naming: purpose-based
module "production_vpc" {}
module "eks_cluster" {}
```

### Tagging Strategy
```hcl
locals {
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
    CostCenter  = var.cost_center
    Owner       = var.owner_email
  }
}

resource "aws_instance" "web" {
  # ...

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-web-server"
      Role = "web"
    }
  )
}
```

## Performance Optimization

### Parallelism
```bash
terraform apply -parallelism=20      # Default is 10
```

### Targeted Operations
```bash
# Target specific resources
terraform apply -target=module.vpc
terraform apply -target=aws_instance.web[0]
```

### Dependency Optimization
```hcl
# Explicit dependencies only when necessary
resource "aws_instance" "web" {
  # Implicit dependency
  subnet_id = aws_subnet.private.id

  # Explicit dependency only if no attribute reference
  depends_on = [aws_iam_role_policy_attachment.web]
}
```

## Security Best Practices

### Sensitive Data
```hcl
variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

output "db_endpoint" {
  value     = aws_db_instance.main.endpoint
  sensitive = true
}
```

### Provider Credentials
```hcl
# Use environment variables
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

# Or assume role
provider "aws" {
  assume_role {
    role_arn     = "arn:aws:iam::ACCOUNT:role/TerraformRole"
    session_name = "terraform-session"
  }
}

# Or use credentials file
provider "aws" {
  shared_credentials_files = ["~/.aws/credentials"]
  profile                  = "production"
}
```

## Troubleshooting

### Debug Output
```bash
TF_LOG=DEBUG terraform apply
TF_LOG=TRACE terraform plan
TF_LOG_PATH=terraform.log terraform apply
```

### Common Issues

**State Lock**
```bash
# If lock is stuck
terraform force-unlock <LOCK_ID>
```

**Dependency Cycles**
```bash
# View dependency graph
terraform graph | dot -Tpng > graph.png
# Review for circular dependencies
```

**Provider Issues**
```bash
# Clear provider cache
rm -rf .terraform
terraform init -upgrade
```

## Version Constraints

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.0, < 4.0"
    }
  }
}
```

**Constraint Syntax**
- `= 1.0.0` - Exact version
- `!= 1.0.0` - Exclude version
- `> 1.0.0` - Greater than
- `>= 1.0.0` - Greater than or equal
- `< 2.0.0` - Less than
- `<= 2.0.0` - Less than or equal
- `~> 1.0` - Pessimistic constraint (>= 1.0, < 2.0)
- `~> 1.0.0` - Pessimistic constraint (>= 1.0.0, < 1.1.0)

## Resources

- Official Documentation: terraform.io/docs
- Registry: registry.terraform.io
- Learn: learn.hashicorp.com/terraform
- Community: discuss.hashicorp.com
- GitHub: github.com/hashicorp/terraform
