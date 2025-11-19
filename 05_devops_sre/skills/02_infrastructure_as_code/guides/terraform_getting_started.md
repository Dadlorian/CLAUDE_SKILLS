# Terraform Getting Started Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Your First Infrastructure](#your-first-infrastructure)
- [Building a Real-World Application](#building-a-real-world-application)
- [Managing Multiple Environments](#managing-multiple-environments)
- [Common Patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## Prerequisites

### Required Knowledge
- Basic understanding of cloud infrastructure concepts
- Familiarity with command-line interfaces
- Understanding of version control (Git)

### Required Tools
- Cloud provider account (AWS, Azure, or GCP)
- Terminal/Command prompt
- Text editor or IDE (VS Code, IntelliJ, etc.)
- Git

### AWS Setup (Example Provider)
```bash
# Install AWS CLI
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region name: us-west-2
# Default output format: json

# Verify configuration
aws sts get-caller-identity
```

## Installation

### macOS
```bash
# Using Homebrew
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

# Verify installation
terraform version
```

### Linux
```bash
# Using package manager (Ubuntu/Debian)
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# Or download binary directly
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify installation
terraform version
```

### Windows
```powershell
# Using Chocolatey
choco install terraform

# Or download from https://www.terraform.io/downloads.html

# Verify installation
terraform version
```

### IDE Setup (VS Code)
```bash
# Install Terraform extension
# Search for "HashiCorp Terraform" in VS Code extensions
# Or install from command line
code --install-extension hashicorp.terraform

# Install additional helpful extensions
code --install-extension ms-vscode.azure-terraform
```

## Your First Infrastructure

### Step 1: Create Project Directory
```bash
mkdir terraform-tutorial
cd terraform-tutorial

# Initialize git repository
git init

# Create .gitignore
cat > .gitignore << 'EOF'
# Local .terraform directories
**/.terraform/*

# .tfstate files
*.tfstate
*.tfstate.*

# Crash log files
crash.log

# Ignore tfvars files (may contain secrets)
*.tfvars
*.tfvars.json

# Ignore override files
override.tf
override.tf.json
*_override.tf
*_override.tf.json

# Ignore CLI configuration files
.terraformrc
terraform.rc
EOF
```

### Step 2: Create Your First Resource
Create `main.tf`:
```hcl
# Configure the AWS Provider
terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-west-2"
}

# Create an S3 bucket
resource "aws_s3_bucket" "my_first_bucket" {
  bucket = "my-first-terraform-bucket-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "My First Bucket"
    Environment = "Learning"
    ManagedBy   = "Terraform"
  }
}

# Generate random suffix for bucket name
resource "random_id" "bucket_suffix" {
  byte_length = 8
}

# Output the bucket name
output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.my_first_bucket.id
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.my_first_bucket.arn
}
```

### Step 3: Initialize Terraform
```bash
# Initialize the working directory
terraform init

# This will:
# - Download the AWS provider plugin
# - Create .terraform directory
# - Create .terraform.lock.hcl file
```

### Step 4: Plan Your Infrastructure
```bash
# Generate and show an execution plan
terraform plan

# Review the output carefully:
# - Resources to be created (+ sign)
# - Resources to be modified (~ sign)
# - Resources to be destroyed (- sign)
```

### Step 5: Apply Your Changes
```bash
# Create the infrastructure
terraform apply

# Terraform will show you the plan again and ask for confirmation
# Type "yes" to proceed

# After completion, you'll see:
# - Resources created
# - Output values
```

### Step 6: Verify Your Infrastructure
```bash
# Check the outputs
terraform output

# List resources in state
terraform state list

# Show details of a specific resource
terraform state show aws_s3_bucket.my_first_bucket

# Verify in AWS Console or CLI
aws s3 ls | grep my-first-terraform-bucket
```

### Step 7: Modify Your Infrastructure
Update `main.tf` to add versioning:
```hcl
# Add versioning to the bucket
resource "aws_s3_bucket_versioning" "my_first_bucket" {
  bucket = aws_s3_bucket.my_first_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}
```

Apply the changes:
```bash
terraform plan
terraform apply
```

### Step 8: Clean Up
```bash
# Destroy all resources
terraform destroy

# Type "yes" to confirm

# Verify resources are deleted
aws s3 ls | grep my-first-terraform-bucket
```

## Building a Real-World Application

### Project Structure
```bash
mkdir web-application
cd web-application

# Create directory structure
mkdir -p modules/{vpc,ec2,alb}
touch main.tf variables.tf outputs.tf versions.tf
```

### versions.tf
```hcl
terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

### variables.tf
```hcl
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "web-app"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b"]
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "instance_count" {
  description = "Number of EC2 instances"
  type        = number
  default     = 2
}
```

### main.tf
```hcl
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Data sources
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

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
}

# Application Load Balancer Module
module "alb" {
  source = "./modules/alb"

  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.public_subnet_ids
}

# EC2 Module
module "ec2" {
  source = "./modules/ec2"

  project_name       = var.project_name
  environment        = var.environment
  ami_id             = data.aws_ami.ubuntu.id
  instance_type      = var.instance_type
  instance_count     = var.instance_count
  subnet_ids         = module.vpc.private_subnet_ids
  vpc_id             = module.vpc.vpc_id
  target_group_arn   = module.alb.target_group_arn
  alb_security_group_id = module.alb.security_group_id
}
```

### modules/vpc/main.tf
```hcl
# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-${var.environment}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-${var.environment}-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count = length(var.availability_zones)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-${var.environment}-public-${var.availability_zones[count.index]}"
    Type = "public"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count = length(var.availability_zones)

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + length(var.availability_zones))
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "${var.project_name}-${var.environment}-private-${var.availability_zones[count.index]}"
    Type = "private"
  }
}

# Elastic IPs for NAT Gateways
resource "aws_eip" "nat" {
  count = length(var.availability_zones)

  domain = "vpc"

  tags = {
    Name = "${var.project_name}-${var.environment}-nat-eip-${count.index + 1}"
  }

  depends_on = [aws_internet_gateway.main]
}

# NAT Gateways
resource "aws_nat_gateway" "main" {
  count = length(var.availability_zones)

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = {
    Name = "${var.project_name}-${var.environment}-nat-${count.index + 1}"
  }

  depends_on = [aws_internet_gateway.main]
}

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-public-rt"
  }
}

# Public Route Table Associations
resource "aws_route_table_association" "public" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Private Route Tables
resource "aws_route_table" "private" {
  count = length(var.availability_zones)

  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-private-rt-${count.index + 1}"
  }
}

# Private Route Table Associations
resource "aws_route_table_association" "private" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}
```

### modules/vpc/variables.tf
```hcl
variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

variable "availability_zones" {
  type = list(string)
}
```

### modules/vpc/outputs.tf
```hcl
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "nat_gateway_ips" {
  description = "List of NAT Gateway public IPs"
  value       = aws_eip.nat[*].public_ip
}
```

### modules/alb/main.tf
```hcl
# Security Group for ALB
resource "aws_security_group" "alb" {
  name_prefix = "${var.project_name}-${var.environment}-alb-"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP from internet"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-alb-sg"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.subnet_ids

  enable_deletion_protection = false

  tags = {
    Name = "${var.project_name}-${var.environment}-alb"
  }
}

# Target Group
resource "aws_lb_target_group" "main" {
  name     = "${var.project_name}-${var.environment}-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/"
    matcher             = "200"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-tg"
  }
}

# Listener
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}
```

### modules/alb/variables.tf
```hcl
variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}
```

### modules/alb/outputs.tf
```hcl
output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "target_group_arn" {
  description = "ARN of the target group"
  value       = aws_lb_target_group.main.arn
}

output "security_group_id" {
  description = "Security group ID of the ALB"
  value       = aws_security_group.alb.id
}
```

### modules/ec2/main.tf
```hcl
# Security Group for EC2
resource "aws_security_group" "ec2" {
  name_prefix = "${var.project_name}-${var.environment}-ec2-"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [var.alb_security_group_id]
    description     = "Allow HTTP from ALB"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-ec2-sg"
  }
}

# User data script
locals {
  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y nginx
              systemctl start nginx
              systemctl enable nginx

              # Create a simple webpage
              cat > /var/www/html/index.html << 'HTML'
              <!DOCTYPE html>
              <html>
              <head>
                  <title>Hello from Terraform</title>
              </head>
              <body>
                  <h1>Hello from Terraform!</h1>
                  <p>Instance ID: $(ec2-metadata --instance-id | cut -d " " -f 2)</p>
                  <p>Availability Zone: $(ec2-metadata --availability-zone | cut -d " " -f 2)</p>
              </body>
              </html>
              HTML
              EOF
}

# EC2 Instances
resource "aws_instance" "web" {
  count = var.instance_count

  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = var.subnet_ids[count.index % length(var.subnet_ids)]

  vpc_security_group_ids = [aws_security_group.ec2.id]

  user_data = local.user_data

  tags = {
    Name = "${var.project_name}-${var.environment}-web-${count.index + 1}"
  }
}

# Attach instances to target group
resource "aws_lb_target_group_attachment" "web" {
  count = var.instance_count

  target_group_arn = var.target_group_arn
  target_id        = aws_instance.web[count.index].id
  port             = 80
}
```

### modules/ec2/variables.tf
```hcl
variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "ami_id" {
  type = string
}

variable "instance_type" {
  type = string
}

variable "instance_count" {
  type = number
}

variable "subnet_ids" {
  type = list(string)
}

variable "vpc_id" {
  type = string
}

variable "target_group_arn" {
  type = string
}

variable "alb_security_group_id" {
  type = string
}
```

### modules/ec2/outputs.tf
```hcl
output "instance_ids" {
  description = "List of instance IDs"
  value       = aws_instance.web[*].id
}

output "instance_private_ips" {
  description = "List of private IPs"
  value       = aws_instance.web[*].private_ip
}
```

### outputs.tf (root)
```hcl
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "alb_dns_name" {
  description = "Load balancer DNS name"
  value       = module.alb.alb_dns_name
}

output "instance_ids" {
  description = "EC2 instance IDs"
  value       = module.ec2.instance_ids
}

output "application_url" {
  description = "Application URL"
  value       = "http://${module.alb.alb_dns_name}"
}
```

### Deploy the Application
```bash
# Initialize
terraform init

# Plan
terraform plan

# Apply
terraform apply

# After successful deployment, get the URL
terraform output application_url

# Test the application
curl $(terraform output -raw application_url)

# Clean up when done
terraform destroy
```

## Managing Multiple Environments

### Using Workspaces
```bash
# Create workspaces
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# List workspaces
terraform workspace list

# Switch workspaces
terraform workspace select dev

# Use workspace in configuration
# main.tf
locals {
  instance_type = terraform.workspace == "prod" ? "t3.large" : "t3.micro"
  instance_count = terraform.workspace == "prod" ? 3 : 1
}
```

### Using Separate Directories
```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars
│       └── backend.tf
└── modules/
```

### Using tfvars Files
```bash
# dev.tfvars
environment    = "dev"
instance_type  = "t3.micro"
instance_count = 1

# prod.tfvars
environment    = "prod"
instance_type  = "t3.large"
instance_count = 3

# Deploy with specific vars file
terraform apply -var-file="dev.tfvars"
```

## Common Patterns

### Import Existing Resources
```bash
# Import an S3 bucket
terraform import aws_s3_bucket.existing my-existing-bucket

# Import an EC2 instance
terraform import aws_instance.web i-1234567890abcdef0
```

### Using Data Sources
```hcl
# Reference existing VPC
data "aws_vpc" "existing" {
  filter {
    name   = "tag:Name"
    values = ["production-vpc"]
  }
}

# Use in resources
resource "aws_subnet" "new" {
  vpc_id = data.aws_vpc.existing.id
  # ...
}
```

### Conditional Resources
```hcl
resource "aws_instance" "optional" {
  count = var.create_instance ? 1 : 0

  # ...
}
```

### Dynamic Blocks
```hcl
resource "aws_security_group" "app" {
  # ...

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
```

## Troubleshooting

### Common Issues

#### Provider Authentication Errors
```bash
# Check AWS credentials
aws sts get-caller-identity

# Set credentials explicitly
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"
```

#### State Lock Errors
```bash
# If state is locked
terraform force-unlock <lock-id>
```

#### Resource Already Exists
```bash
# Import the existing resource
terraform import <resource_type>.<name> <resource_id>

# Or remove from state and recreate
terraform state rm <resource_type>.<name>
```

#### Debugging
```bash
# Enable debug logging
export TF_LOG=DEBUG
terraform plan

# Disable logging
unset TF_LOG

# Show detailed crash log
cat crash.log
```

### Best Practices
1. Always run `terraform plan` before `terraform apply`
2. Use version control for all Terraform code
3. Never commit `.tfstate` files
4. Use remote state for team collaboration
5. Implement proper tagging strategy
6. Use modules for reusable components
7. Validate inputs with validation blocks
8. Document your infrastructure
9. Use consistent naming conventions
10. Implement proper secret management

## Next Steps

### Advanced Topics to Explore
1. **Remote State Management**: Set up S3 backend with DynamoDB locking
2. **Terraform Cloud**: Use Terraform Cloud for collaboration
3. **Module Development**: Create and publish reusable modules
4. **Testing**: Implement automated testing with Terratest
5. **CI/CD Integration**: Automate deployments with GitHub Actions
6. **Multi-Cloud**: Deploy to multiple cloud providers
7. **Kubernetes Integration**: Use Terraform with Kubernetes
8. **Policy as Code**: Implement compliance with Sentinel or OPA

### Resources
- [Terraform Documentation](https://www.terraform.io/docs)
- [Terraform Registry](https://registry.terraform.io/)
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [Learn Terraform](https://learn.hashicorp.com/terraform)

### Community
- [Terraform GitHub](https://github.com/hashicorp/terraform)
- [Terraform Community Forum](https://discuss.hashicorp.com/c/terraform-core)
- [Terraform Discord](https://discord.gg/terraform)
