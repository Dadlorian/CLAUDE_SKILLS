# Terraform Reference Guide

## Table of Contents
- [Core Concepts](#core-concepts)
- [HCL Syntax](#hcl-syntax)
- [Providers](#providers)
- [Resources](#resources)
- [Data Sources](#data-sources)
- [Variables](#variables)
- [Outputs](#outputs)
- [State Management](#state-management)
- [Functions](#functions)
- [Meta-Arguments](#meta-arguments)
- [Provisioners](#provisioners)
- [Workspaces](#workspaces)

## Core Concepts

### Infrastructure as Code
Terraform uses declarative configuration files to define infrastructure. The desired state is described, and Terraform determines the necessary changes to achieve that state.

### Terraform Workflow
1. **Write**: Define infrastructure in `.tf` files
2. **Plan**: Preview changes with `terraform plan`
3. **Apply**: Execute changes with `terraform apply`
4. **Destroy**: Remove infrastructure with `terraform destroy`

### Directory Structure
```
project/
├── main.tf           # Primary resource definitions
├── variables.tf      # Input variable declarations
├── outputs.tf        # Output value declarations
├── versions.tf       # Provider version constraints
├── terraform.tfvars  # Variable value assignments
└── modules/          # Reusable module directory
    └── vpc/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

## HCL Syntax

### Basic Block Structure
```hcl
<BLOCK_TYPE> "<BLOCK_LABEL>" "<BLOCK_LABEL>" {
  # Block body
  <IDENTIFIER> = <EXPRESSION>
}
```

### Comments
```hcl
# Single line comment

// Also a single line comment

/*
Multi-line
comment
*/
```

### Data Types

#### Primitive Types
```hcl
# String
variable "region" {
  type    = string
  default = "us-west-2"
}

# Number
variable "instance_count" {
  type    = number
  default = 3
}

# Boolean
variable "enable_monitoring" {
  type    = bool
  default = true
}
```

#### Complex Types
```hcl
# List
variable "availability_zones" {
  type    = list(string)
  default = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

# Set
variable "security_groups" {
  type = set(string)
}

# Map
variable "tags" {
  type = map(string)
  default = {
    Environment = "production"
    Team        = "platform"
  }
}

# Object
variable "instance_config" {
  type = object({
    instance_type = string
    volume_size   = number
    monitoring    = bool
  })
  default = {
    instance_type = "t3.medium"
    volume_size   = 100
    monitoring    = true
  }
}

# Tuple
variable "network_config" {
  type = tuple([string, number, bool])
}
```

### Expressions

#### Conditional
```hcl
resource "aws_instance" "web" {
  instance_type = var.environment == "production" ? "t3.large" : "t3.micro"

  tags = {
    Name = var.use_prefix ? "${var.prefix}-web" : "web"
  }
}
```

#### For Expressions
```hcl
# List transformation
locals {
  uppercase_names = [for name in var.names : upper(name)]

  # Filtering
  production_instances = [
    for instance in var.instances : instance
    if instance.environment == "production"
  ]

  # Map transformation
  instance_ips = {
    for instance in aws_instance.web : instance.id => instance.private_ip
  }
}
```

#### Splat Expressions
```hcl
# Get all IDs from a list of resources
output "instance_ids" {
  value = aws_instance.web[*].id
}

# Get attribute from all map elements
output "subnet_cidrs" {
  value = aws_subnet.private[*].cidr_block
}
```

#### Dynamic Blocks
```hcl
resource "aws_security_group" "web" {
  name = "web-sg"

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = "tcp"
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
```

## Providers

### Provider Configuration
```hcl
# versions.tf
terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

# Provider configuration
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      ManagedBy   = "Terraform"
      Environment = var.environment
      Project     = var.project_name
    }
  }
}

# Assume role configuration
provider "aws" {
  alias  = "prod"
  region = "us-east-1"

  assume_role {
    role_arn     = "arn:aws:iam::123456789012:role/TerraformRole"
    session_name = "TerraformSession"
  }
}
```

### Multiple Provider Instances
```hcl
provider "aws" {
  alias  = "west"
  region = "us-west-2"
}

provider "aws" {
  alias  = "east"
  region = "us-east-1"
}

resource "aws_instance" "west" {
  provider = aws.west
  # ...
}

resource "aws_instance" "east" {
  provider = aws.east
  # ...
}
```

## Resources

### Basic Resource Syntax
```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.medium"

  subnet_id              = aws_subnet.public[0].id
  vpc_security_group_ids = [aws_security_group.web.id]

  root_block_device {
    volume_type = "gp3"
    volume_size = 30
    encrypted   = true
  }

  tags = {
    Name = "${var.environment}-web-server"
  }
}
```

### Resource Dependencies
```hcl
# Implicit dependency (referencing attributes)
resource "aws_eip" "web" {
  instance = aws_instance.web.id
  domain   = "vpc"
}

# Explicit dependency
resource "aws_instance" "web" {
  # ...

  depends_on = [
    aws_iam_role_policy_attachment.instance_policy
  ]
}
```

### Resource Lifecycle
```hcl
resource "aws_instance" "web" {
  # ...

  lifecycle {
    create_before_destroy = true
    prevent_destroy       = true
    ignore_changes        = [
      tags,
      user_data
    ]
  }
}
```

## Data Sources

### Querying Existing Infrastructure
```hcl
# Get latest Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Get current AWS region
data "aws_region" "current" {}

# Get current AWS account ID
data "aws_caller_identity" "current" {}

# Get availability zones
data "aws_availability_zones" "available" {
  state = "available"

  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

# Reference data source
resource "aws_instance" "web" {
  ami               = data.aws_ami.ubuntu.id
  availability_zone = data.aws_availability_zones.available.names[0]
}
```

## Variables

### Variable Definition
```hcl
variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "instance_count" {
  description = "Number of instances to create"
  type        = number
  default     = 1

  validation {
    condition     = var.instance_count > 0 && var.instance_count <= 10
    error_message = "Instance count must be between 1 and 10."
  }
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "enable_backup" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

# Sensitive variables
variable "database_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}
```

### Variable Precedence (lowest to highest)
1. Environment variables (`TF_VAR_name`)
2. `terraform.tfvars` file
3. `terraform.tfvars.json` file
4. `*.auto.tfvars` files (alphabetical order)
5. `-var` and `-var-file` CLI flags

### Variable Files
```hcl
# terraform.tfvars
environment      = "production"
instance_count   = 3
enable_backup    = true

tags = {
  Owner   = "platform-team"
  Project = "web-app"
}
```

## Outputs

### Output Definition
```hcl
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.web.id
}

output "instance_public_ip" {
  description = "Public IP address of the instance"
  value       = aws_instance.web.public_ip
}

output "instance_private_ips" {
  description = "Private IP addresses of all instances"
  value       = aws_instance.web[*].private_ip
}

# Sensitive output
output "database_password" {
  description = "Database password"
  value       = random_password.db.result
  sensitive   = true
}

# Conditional output
output "lb_dns_name" {
  description = "DNS name of load balancer"
  value       = var.create_lb ? aws_lb.main[0].dns_name : null
}
```

### Using Outputs
```bash
# Show all outputs
terraform output

# Show specific output
terraform output instance_id

# JSON format
terraform output -json

# Use in scripts
INSTANCE_ID=$(terraform output -raw instance_id)
```

## State Management

### State File
The state file (`terraform.tfstate`) maps real-world resources to your configuration and tracks metadata.

```json
{
  "version": 4,
  "terraform_version": "1.6.0",
  "serial": 1,
  "lineage": "unique-id",
  "outputs": {},
  "resources": []
}
```

### Remote State Backend
```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"

    # Optional: use role assumption
    role_arn = "arn:aws:iam::123456789012:role/TerraformBackend"
  }
}
```

### State Commands
```bash
# List resources in state
terraform state list

# Show resource details
terraform state show aws_instance.web

# Move resource in state
terraform state mv aws_instance.web aws_instance.web_server

# Remove resource from state (doesn't destroy)
terraform state rm aws_instance.web

# Replace a resource (force recreation)
terraform apply -replace=aws_instance.web

# Import existing resource
terraform import aws_instance.web i-1234567890abcdef0

# Pull remote state
terraform state pull > terraform.tfstate

# Push local state to remote
terraform state push terraform.tfstate
```

### Remote State Data Source
```hcl
data "terraform_remote_state" "vpc" {
  backend = "s3"

  config = {
    bucket = "my-terraform-state"
    key    = "vpc/terraform.tfstate"
    region = "us-west-2"
  }
}

resource "aws_instance" "web" {
  subnet_id = data.terraform_remote_state.vpc.outputs.public_subnet_ids[0]
}
```

## Functions

### Numeric Functions
```hcl
# abs, ceil, floor, max, min
locals {
  absolute    = abs(-5)              # 5
  ceiling     = ceil(5.1)            # 6
  flooring    = floor(5.9)           # 5
  maximum     = max(5, 12, 9)        # 12
  minimum     = min(5, 12, 9)        # 5
  parse_int   = parseint("100", 10)  # 100
}
```

### String Functions
```hcl
locals {
  # format, join, split
  formatted = format("Hello, %s!", var.name)
  joined    = join(", ", ["a", "b", "c"])  # "a, b, c"
  split     = split(",", "a,b,c")          # ["a", "b", "c"]

  # upper, lower, title
  upper_case = upper("hello")              # "HELLO"
  lower_case = lower("HELLO")              # "hello"
  title_case = title("hello world")        # "Hello World"

  # trim, trimprefix, trimsuffix
  trimmed        = trim("  hello  ", " ")  # "hello"
  prefix_trimmed = trimprefix("hello", "hel")  # "lo"
  suffix_trimmed = trimsuffix("hello", "lo")   # "hel"

  # replace, regex, regexall
  replaced = replace("hello world", "world", "terraform")
  regex_matched = regex("[a-z]+", "hello123")  # "hello"

  # substr
  substring = substr("hello", 0, 3)  # "hel"
}
```

### Collection Functions
```hcl
locals {
  # length
  list_length = length(["a", "b", "c"])  # 3

  # contains
  has_item = contains(["a", "b", "c"], "b")  # true

  # concat
  combined = concat(["a", "b"], ["c", "d"])  # ["a", "b", "c", "d"]

  # distinct
  unique = distinct(["a", "b", "a", "c"])  # ["a", "b", "c"]

  # flatten
  flattened = flatten([["a", "b"], ["c", "d"]])  # ["a", "b", "c", "d"]

  # merge
  merged = merge(
    { a = "foo" },
    { b = "bar" },
    { c = "baz" }
  )  # { a = "foo", b = "bar", c = "baz" }

  # lookup
  value = lookup({ a = "foo", b = "bar" }, "a", "default")  # "foo"

  # keys, values
  map_keys   = keys({ a = 1, b = 2 })    # ["a", "b"]
  map_values = values({ a = 1, b = 2 })  # [1, 2]

  # zipmap
  zipped = zipmap(["a", "b"], [1, 2])  # { a = 1, b = 2 }
}
```

### Encoding Functions
```hcl
locals {
  # base64encode, base64decode
  encoded = base64encode("hello")
  decoded = base64decode(local.encoded)

  # jsonencode, jsondecode
  json_string = jsonencode({ foo = "bar" })
  json_obj    = jsondecode(local.json_string)

  # yamlencode, yamldecode
  yaml_string = yamlencode({ foo = "bar" })
  yaml_obj    = yamldecode(local.yaml_string)
}
```

### Filesystem Functions
```hcl
locals {
  # file
  file_content = file("${path.module}/config.json")

  # templatefile
  user_data = templatefile("${path.module}/user-data.sh", {
    cluster_name = var.cluster_name
    region       = var.region
  })

  # fileexists
  has_config = fileexists("${path.module}/config.json")

  # dirname, basename
  directory = dirname("/path/to/file.txt")  # "/path/to"
  filename  = basename("/path/to/file.txt") # "file.txt"

  # abspath
  absolute_path = abspath("./relative/path")
}
```

### Date and Time Functions
```hcl
locals {
  # timestamp
  current_time = timestamp()  # "2024-01-15T10:30:00Z"

  # formatdate
  formatted_date = formatdate("DD MMM YYYY hh:mm ZZZ", timestamp())

  # timeadd
  future_time = timeadd(timestamp(), "24h")
}
```

### IP Network Functions
```hcl
locals {
  # cidrhost
  first_ip = cidrhost("10.0.0.0/24", 1)  # "10.0.0.1"

  # cidrnetmask
  netmask = cidrnetmask("10.0.0.0/24")  # "255.255.255.0"

  # cidrsubnet
  subnet = cidrsubnet("10.0.0.0/16", 8, 1)  # "10.0.1.0/24"

  # cidrsubnets
  subnets = cidrsubnets("10.0.0.0/16", 8, 8, 8)
}
```

### Type Conversion Functions
```hcl
locals {
  # tostring, tonumber, tobool
  string_val = tostring(123)
  number_val = tonumber("123")
  bool_val   = tobool("true")

  # tolist, toset, tomap
  list_val = tolist(["a", "b"])
  set_val  = toset(["a", "b", "a"])
  map_val  = tomap({ a = "foo" })
}
```

## Meta-Arguments

### count
```hcl
resource "aws_instance" "web" {
  count = var.instance_count

  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.medium"

  tags = {
    Name = "${var.environment}-web-${count.index}"
  }
}

# Reference specific instances
output "first_instance_id" {
  value = aws_instance.web[0].id
}

# Reference all instances
output "all_instance_ids" {
  value = aws_instance.web[*].id
}
```

### for_each
```hcl
# With map
resource "aws_instance" "web" {
  for_each = var.instances

  ami           = data.aws_ami.ubuntu.id
  instance_type = each.value.instance_type
  subnet_id     = each.value.subnet_id

  tags = {
    Name = each.key
  }
}

# With set
resource "aws_iam_user" "users" {
  for_each = toset(var.user_names)

  name = each.value
}

# Reference
output "instance_ids" {
  value = {
    for k, instance in aws_instance.web : k => instance.id
  }
}
```

### depends_on
```hcl
resource "aws_instance" "web" {
  # ...

  depends_on = [
    aws_iam_role_policy_attachment.instance_policy,
    aws_security_group_rule.allow_http
  ]
}
```

### provider
```hcl
resource "aws_instance" "west" {
  provider = aws.west
  # ...
}
```

### lifecycle
```hcl
resource "aws_instance" "web" {
  # ...

  lifecycle {
    # Create replacement before destroying old
    create_before_destroy = true

    # Prevent accidental deletion
    prevent_destroy = false

    # Ignore changes to specific attributes
    ignore_changes = [
      tags,
      user_data,
    ]

    # Replace if attribute changes
    replace_triggered_by = [
      aws_security_group.web.id
    ]
  }
}
```

## Provisioners

### local-exec
```hcl
resource "aws_instance" "web" {
  # ...

  provisioner "local-exec" {
    command = "echo ${self.private_ip} >> private_ips.txt"

    environment = {
      INSTANCE_ID = self.id
    }

    when = create
  }

  provisioner "local-exec" {
    when    = destroy
    command = "echo 'Instance destroyed'"
  }
}
```

### remote-exec
```hcl
resource "aws_instance" "web" {
  # ...

  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = file("~/.ssh/id_rsa")
    host        = self.public_ip
  }

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y nginx",
      "sudo systemctl start nginx"
    ]
  }
}
```

### file
```hcl
resource "aws_instance" "web" {
  # ...

  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = file("~/.ssh/id_rsa")
    host        = self.public_ip
  }

  provisioner "file" {
    source      = "scripts/setup.sh"
    destination = "/tmp/setup.sh"
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/setup.sh",
      "/tmp/setup.sh"
    ]
  }
}
```

### Null Resource with Provisioners
```hcl
resource "null_resource" "cluster" {
  triggers = {
    cluster_instance_ids = join(",", aws_instance.cluster[*].id)
  }

  provisioner "local-exec" {
    command = "echo 'Cluster instances: ${join(",", aws_instance.cluster[*].id)}'"
  }
}
```

## Workspaces

### Workspace Commands
```bash
# List workspaces
terraform workspace list

# Show current workspace
terraform workspace show

# Create new workspace
terraform workspace new dev

# Switch workspace
terraform workspace select dev

# Delete workspace
terraform workspace delete dev
```

### Using Workspaces in Configuration
```hcl
resource "aws_instance" "web" {
  # ...

  instance_type = terraform.workspace == "production" ? "t3.large" : "t3.micro"

  tags = {
    Name        = "${terraform.workspace}-web"
    Workspace   = terraform.workspace
    Environment = terraform.workspace
  }
}

# Workspace-specific variable files
# terraform.tfvars.dev
# terraform.tfvars.staging
# terraform.tfvars.production

locals {
  workspace_config = {
    dev = {
      instance_type = "t3.micro"
      instance_count = 1
    }
    staging = {
      instance_type = "t3.small"
      instance_count = 2
    }
    production = {
      instance_type = "t3.large"
      instance_count = 3
    }
  }

  current_config = local.workspace_config[terraform.workspace]
}

resource "aws_instance" "web" {
  count         = local.current_config.instance_count
  instance_type = local.current_config.instance_type
  # ...
}
```

## Best Practices

1. **Use Version Constraints**: Pin provider versions to avoid breaking changes
2. **Remote State**: Always use remote state with locking for team environments
3. **Module Organization**: Break large configurations into reusable modules
4. **Variable Validation**: Add validation rules to catch errors early
5. **Sensitive Data**: Use sensitive variables and avoid committing secrets
6. **Consistent Naming**: Follow a naming convention for resources
7. **Tagging Strategy**: Implement consistent tagging across all resources
8. **State Locking**: Use DynamoDB or similar for state locking
9. **Plan Before Apply**: Always run `terraform plan` before `terraform apply`
10. **Documentation**: Document modules, variables, and complex logic
