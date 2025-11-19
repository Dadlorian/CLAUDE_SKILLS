# Infrastructure as Code Best Practices

## Table of Contents
- [General Principles](#general-principles)
- [Code Organization](#code-organization)
- [Security](#security)
- [Testing](#testing)
- [CI/CD Integration](#cicd-integration)
- [State Management](#state-management)
- [Version Control](#version-control)
- [Documentation](#documentation)
- [Monitoring and Compliance](#monitoring-and-compliance)
- [Cost Management](#cost-management)

## General Principles

### 1. Infrastructure as Code Philosophy
- **Declarative over Imperative**: Define the desired state, not the steps to get there
- **Idempotency**: Running the same code multiple times produces the same result
- **Version Everything**: All infrastructure changes should be versioned
- **Immutable Infrastructure**: Replace rather than modify infrastructure
- **Automation First**: Manual changes should be exceptions, not the norm

### 2. DRY (Don't Repeat Yourself)
```hcl
# Bad: Repetitive code
resource "aws_subnet" "public_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"
}

resource "aws_subnet" "public_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-west-2b"
}

# Good: Use loops and modules
resource "aws_subnet" "public" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "${var.environment}-public-${var.availability_zones[count.index]}"
  }
}
```

### 3. Single Source of Truth
- Use remote state for collaboration
- Reference outputs from other stacks/modules
- Avoid hardcoding values that exist elsewhere

```hcl
# Use data sources to query existing infrastructure
data "aws_vpc" "existing" {
  id = var.vpc_id
}

# Use stack references (Pulumi)
const networkStack = new pulumi.StackReference("org/networking/prod");
const vpcId = networkStack.requireOutput("vpcId");
```

### 4. Fail Fast
- Use validation rules
- Implement pre-commit hooks
- Run checks in CI/CD before apply

```hcl
variable "environment" {
  type        = string
  description = "Environment name"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "instance_count" {
  type        = number
  description = "Number of instances"

  validation {
    condition     = var.instance_count > 0 && var.instance_count <= 10
    error_message = "Instance count must be between 1 and 10."
  }
}
```

## Code Organization

### 1. Directory Structure

#### Small Project
```
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
├── terraform.tfvars
└── README.md
```

#### Medium Project
```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   └── prod/
├── modules/
│   ├── vpc/
│   ├── ec2/
│   └── rds/
├── shared/
│   ├── data.tf
│   └── locals.tf
└── README.md
```

#### Large Project (Multi-Account/Region)
```
infrastructure/
├── terraform/
│   ├── accounts/
│   │   ├── production/
│   │   │   ├── us-west-2/
│   │   │   │   ├── networking/
│   │   │   │   ├── compute/
│   │   │   │   └── data/
│   │   │   └── us-east-1/
│   │   ├── staging/
│   │   └── dev/
│   ├── modules/
│   │   ├── networking/
│   │   ├── compute/
│   │   ├── database/
│   │   └── monitoring/
│   └── global/
│       ├── iam/
│       └── route53/
├── scripts/
│   ├── validate.sh
│   └── deploy.sh
├── .github/
│   └── workflows/
└── README.md
```

### 2. File Organization
```hcl
# main.tf - Primary resources
terraform {
  required_version = ">= 1.6"
}

resource "aws_vpc" "main" {
  # ...
}

# variables.tf - Input variables
variable "environment" {
  description = "Environment name"
  type        = string
}

# outputs.tf - Output values
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

# locals.tf - Local values
locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# data.tf - Data sources
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
}

# versions.tf - Provider versions
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# backend.tf - Backend configuration
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

### 3. Naming Conventions
```hcl
# Resources: <resource_type>_<descriptive_name>
resource "aws_vpc" "main" {}
resource "aws_subnet" "public" {}
resource "aws_security_group" "web_server" {}

# Variables: descriptive_snake_case
variable "vpc_cidr_block" {}
variable "enable_dns_hostnames" {}

# Outputs: descriptive_snake_case
output "vpc_id" {}
output "public_subnet_ids" {}

# Modules: descriptive-kebab-case
module "web-application" {
  source = "./modules/web-app"
}

# Tags: PascalCase for keys
tags = {
  Name        = "my-resource"
  Environment = "production"
  CostCenter  = "engineering"
  ManagedBy   = "Terraform"
}
```

## Security

### 1. Secrets Management

#### Never Commit Secrets
```bash
# .gitignore
*.tfvars
*.tfstate
*.tfstate.backup
.terraform/
*.pem
*.key
secrets/
```

#### Use Secret Management Tools
```hcl
# AWS Secrets Manager
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/db/password"
}

resource "aws_db_instance" "main" {
  password = data.aws_secretsmanager_secret_version.db_password.secret_string
  # ...
}

# HashiCorp Vault
data "vault_generic_secret" "db_creds" {
  path = "secret/database/production"
}

# Environment variables (for CI/CD)
variable "database_password" {
  type      = string
  sensitive = true
}

# Mark sensitive values
output "db_endpoint" {
  value     = aws_db_instance.main.endpoint
  sensitive = true
}
```

#### Use KMS for Encryption
```hcl
resource "aws_kms_key" "main" {
  description             = "KMS key for encrypting sensitive data"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = var.tags
}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.main.id
    }
  }
}
```

### 2. Least Privilege Access
```hcl
# IAM policy with minimal permissions
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${var.environment}-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

data "aws_iam_policy_document" "lambda_permissions" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject"
    ]

    resources = ["${aws_s3_bucket.data.arn}/*"]
  }
}

resource "aws_iam_role_policy" "lambda" {
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.lambda_permissions.json
}
```

### 3. Network Security
```hcl
# Security group with minimal access
resource "aws_security_group" "web" {
  name_prefix = "${var.environment}-web-"
  vpc_id      = aws_vpc.main.id

  # Only allow HTTPS from specific CIDR blocks
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "HTTPS from allowed networks"
  }

  # Explicit egress rules (don't use 0.0.0.0/0 unless necessary)
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS to internet"
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-web-sg"
    }
  )
}

# Network ACLs for additional layer
resource "aws_network_acl" "private" {
  vpc_id     = aws_vpc.main.id
  subnet_ids = aws_subnet.private[*].id

  # Deny all inbound by default, allow specific
  ingress {
    rule_no    = 100
    protocol   = "tcp"
    from_port  = 443
    to_port    = 443
    cidr_block = var.vpc_cidr
    action     = "allow"
  }

  tags = var.tags
}
```

### 4. Compliance and Auditing
```hcl
# Enable CloudTrail
resource "aws_cloudtrail" "main" {
  name                          = "${var.environment}-audit-trail"
  s3_bucket_name                = aws_s3_bucket.audit_logs.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["${aws_s3_bucket.data.arn}/"]
    }
  }

  tags = var.tags
}

# Enable VPC Flow Logs
resource "aws_flow_log" "main" {
  iam_role_arn    = aws_iam_role.flow_logs.arn
  log_destination = aws_cloudwatch_log_group.flow_logs.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id

  tags = var.tags
}

# Enable AWS Config
resource "aws_config_configuration_recorder" "main" {
  name     = "${var.environment}-config-recorder"
  role_arn = aws_iam_role.config.arn

  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }
}
```

### 5. Security Scanning
```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  tfsec:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: tfsec
        uses: aquasecurity/tfsec-action@v1.0.0
        with:
          soft_fail: false

  checkov:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: terraform/
          framework: terraform

  terrascan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Terrascan
        uses: tenable/terrascan-action@main
        with:
          iac_type: 'terraform'
          iac_dir: 'terraform/'
```

## Testing

### 1. Static Analysis
```bash
# Terraform validate
terraform init -backend=false
terraform validate

# Format check
terraform fmt -check -recursive

# tfsec security scanning
tfsec .

# Checkov policy scanning
checkov -d .

# terraform-docs for documentation
terraform-docs markdown table . > README.md
```

### 2. Unit Testing with Terratest
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
        TerraformDir: "../modules/vpc",

        Vars: map[string]interface{}{
            "vpc_name":           "test-vpc",
            "vpc_cidr":           "10.0.0.0/16",
            "availability_zones": []string{"us-west-2a", "us-west-2b"},
        },

        EnvVars: map[string]string{
            "AWS_DEFAULT_REGION": "us-west-2",
        },
    }

    defer terraform.Destroy(t, terraformOptions)

    terraform.InitAndApply(t, terraformOptions)

    // Test outputs
    vpcID := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcID)

    subnetIDs := terraform.OutputList(t, terraformOptions, "public_subnet_ids")
    assert.Len(t, subnetIDs, 2)
}

func TestInstanceCreation(t *testing.T) {
    t.Parallel()

    terraformOptions := &terraform.Options{
        TerraformDir: "../examples/ec2",

        Vars: map[string]interface{}{
            "instance_type": "t3.micro",
            "environment":   "test",
        },
    }

    defer terraform.Destroy(t, terraformOptions)

    terraform.InitAndApply(t, terraformOptions)

    instanceID := terraform.Output(t, terraformOptions, "instance_id")
    assert.Regexp(t, "^i-[a-f0-9]+$", instanceID)
}
```

### 3. Integration Testing
```go
func TestWebApplicationEndToEnd(t *testing.T) {
    t.Parallel()

    terraformOptions := &terraform.Options{
        TerraformDir: "../",
    }

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    // Get the load balancer URL
    lbURL := terraform.Output(t, terraformOptions, "load_balancer_url")

    // Validate HTTP response
    http_helper.HttpGetWithRetry(
        t,
        fmt.Sprintf("http://%s", lbURL),
        nil,
        200,
        "Hello World",
        30,
        5*time.Second,
    )
}
```

### 4. Compliance Testing
```python
# Using InSpec
describe aws_vpc(vpc_id: vpc_id) do
  it { should exist }
  its('cidr_block') { should eq '10.0.0.0/16' }
  its('state') { should eq 'available' }
end

describe aws_security_group(group_id: sg_id) do
  it { should exist }
  it { should_not allow_in(port: 22, ipv4_range: '0.0.0.0/0') }
  it { should allow_in(port: 443, ipv4_range: '10.0.0.0/8') }
end

describe aws_s3_bucket(bucket_name: bucket_name) do
  it { should have_default_encryption_enabled }
  it { should have_versioning_enabled }
  it { should_not be_public }
end
```

### 5. Policy as Code
```hcl
# Sentinel (Terraform Cloud/Enterprise)
import "tfplan/v2" as tfplan

# Ensure all S3 buckets have encryption enabled
all_s3_buckets = filter tfplan.resource_changes as _, rc {
    rc.type is "aws_s3_bucket" and
    rc.mode is "managed" and
    (rc.change.actions contains "create" or rc.change.actions contains "update")
}

encryption_enabled = rule {
    all all_s3_buckets as _, bucket {
        bucket.change.after.server_side_encryption_configuration is not null
    }
}

main = rule {
    encryption_enabled
}
```

## CI/CD Integration

### 1. GitHub Actions Workflow
```yaml
name: Terraform CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  TF_VERSION: '1.6.0'
  AWS_REGION: 'us-west-2'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Format
        run: terraform fmt -check -recursive

      - name: Terraform Init
        run: terraform init -backend=false

      - name: Terraform Validate
        run: terraform validate

      - name: tfsec
        uses: aquasecurity/tfsec-action@v1.0.0

      - name: Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: terraform

  plan:
    needs: validate
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Terraform Init
        run: terraform init

      - name: Terraform Plan
        id: plan
        run: terraform plan -no-color -out=tfplan
        continue-on-error: true

      - name: Upload Plan
        uses: actions/upload-artifact@v3
        with:
          name: tfplan
          path: tfplan

      - name: Comment PR
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const output = `#### Terraform Plan 📖
            \`\`\`
            ${{ steps.plan.outputs.stdout }}
            \`\`\`

            *Pushed by: @${{ github.actor }}, Action: \`${{ github.event_name }}\`*`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: output
            })

  apply:
    needs: validate
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    environment:
      name: production
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Terraform Init
        run: terraform init

      - name: Terraform Apply
        run: terraform apply -auto-approve

      - name: Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Terraform apply completed'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 2. GitLab CI/CD
```yaml
# .gitlab-ci.yml
image: hashicorp/terraform:1.6

variables:
  TF_ROOT: ${CI_PROJECT_DIR}
  TF_STATE_NAME: default

cache:
  paths:
    - ${TF_ROOT}/.terraform

before_script:
  - cd ${TF_ROOT}
  - terraform --version
  - terraform init

stages:
  - validate
  - plan
  - apply
  - destroy

validate:
  stage: validate
  script:
    - terraform fmt -check
    - terraform validate

plan:
  stage: plan
  script:
    - terraform plan -out=tfplan
  artifacts:
    paths:
      - tfplan
    expire_in: 1 day
  only:
    - merge_requests
    - main

apply:
  stage: apply
  script:
    - terraform apply -auto-approve tfplan
  dependencies:
    - plan
  only:
    - main
  when: manual
  environment:
    name: production

destroy:
  stage: destroy
  script:
    - terraform destroy -auto-approve
  only:
    - main
  when: manual
```

### 3. Atlantis for Pull Request Automation
```yaml
# atlantis.yaml
version: 3

projects:
  - name: production
    dir: environments/production
    workspace: prod
    terraform_version: v1.6.0
    autoplan:
      when_modified: ["*.tf", "*.tfvars"]
      enabled: true
    apply_requirements: ["approved", "mergeable"]
    workflow: production

  - name: staging
    dir: environments/staging
    workspace: staging
    terraform_version: v1.6.0
    autoplan:
      when_modified: ["*.tf", "*.tfvars"]
      enabled: true
    workflow: default

workflows:
  production:
    plan:
      steps:
        - init
        - plan:
            extra_args: ["-lock=false"]
    apply:
      steps:
        - apply:
            extra_args: ["-auto-approve"]
```

### 4. Drift Detection
```yaml
# .github/workflows/drift-detection.yml
name: Drift Detection

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  detect-drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2

      - name: Terraform Init
        run: terraform init

      - name: Terraform Plan
        id: plan
        run: |
          terraform plan -detailed-exitcode -no-color
        continue-on-error: true

      - name: Notify on Drift
        if: steps.plan.outputs.exitcode == 2
        uses: 8398a7/action-slack@v3
        with:
          status: custom
          custom_payload: |
            {
              text: "⚠️ Infrastructure Drift Detected!",
              attachments: [{
                color: 'warning',
                text: 'Terraform plan shows changes from current state'
              }]
            }
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## State Management

### 1. Remote State Configuration
```hcl
# S3 backend with DynamoDB locking
terraform {
  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "prod/us-west-2/vpc/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    kms_key_id     = "arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012"
    dynamodb_table = "terraform-state-lock"

    # Optional: Use role assumption
    role_arn = "arn:aws:iam::123456789012:role/TerraformBackendRole"
  }
}
```

### 2. State Bucket Setup
```hcl
# state-bucket/main.tf
resource "aws_s3_bucket" "terraform_state" {
  bucket = "mycompany-terraform-state"

  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name        = "Terraform State"
    Environment = "global"
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.terraform_state.id
    }
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-state-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "Terraform State Lock"
    Environment = "global"
  }
}
```

### 3. State Locking
```bash
# Manual lock acquisition (emergency)
terraform force-unlock <lock-id>

# Prevent concurrent runs
terraform plan -lock-timeout=10m
```

### 4. State Backup and Recovery
```bash
# Backup state before making changes
terraform state pull > backup-$(date +%Y%m%d-%H%M%S).tfstate

# Restore from backup
terraform state push backup-20240115-120000.tfstate

# S3 versioning allows state recovery
aws s3api list-object-versions \
  --bucket mycompany-terraform-state \
  --prefix prod/vpc/terraform.tfstate

# Download specific version
aws s3api get-object \
  --bucket mycompany-terraform-state \
  --key prod/vpc/terraform.tfstate \
  --version-id <version-id> \
  restored-state.tfstate
```

## Version Control

### 1. Git Workflow
```bash
# Feature branch workflow
git checkout -b feature/add-monitoring
# Make changes
git add .
git commit -m "feat: add CloudWatch monitoring for EC2 instances"
git push origin feature/add-monitoring
# Create pull request
```

### 2. Commit Message Convention
```
type(scope): subject

body

footer

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Formatting changes
- refactor: Code refactoring
- test: Adding tests
- chore: Maintenance tasks

Examples:
feat(vpc): add NAT gateway for private subnets
fix(ec2): correct security group attachment
docs(readme): update deployment instructions
refactor(modules): extract RDS module from main config
```

### 3. .gitignore
```
# Local .terraform directories
**/.terraform/*

# .tfstate files
*.tfstate
*.tfstate.*

# Crash log files
crash.log
crash.*.log

# Exclude all .tfvars files (contain secrets)
*.tfvars
*.tfvars.json

# Ignore override files
override.tf
override.tf.json
*_override.tf
*_override.tf.json

# Include example tfvars
!example.tfvars

# Ignore CLI configuration files
.terraformrc
terraform.rc

# Ignore plan files
*.tfplan

# Ignore lock files in non-root directories
**/.terraform.lock.hcl
!.terraform.lock.hcl
```

### 4. Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.83.0
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_docs
        args:
          - --hook-config=--path-to-file=README.md
          - --hook-config=--add-to-existing-file=true
          - --hook-config=--create-file-if-not-exist=true
      - id: terraform_tflint
        args:
          - --args=--config=__GIT_WORKING_DIR__/.tflint.hcl
      - id: terraform_tfsec
        args:
          - --args=--minimum-severity=MEDIUM

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
```

## Documentation

### 1. Module Documentation
```markdown
# AWS VPC Module

## Overview
Creates a VPC with public and private subnets across multiple availability zones.

## Architecture
[Architecture diagram]

## Usage
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-west-2a", "us-west-2b", "us-west-2c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}
```

## Requirements
| Name | Version |
|------|---------|
| terraform | >= 1.6 |
| aws | >= 5.0 |

## Providers
| Name | Version |
|------|---------|
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

## Examples
- [Complete](examples/complete) - Complete VPC with all features
- [Simple](examples/simple) - Simple VPC setup

## License
MIT
```

### 2. Inline Documentation
```hcl
# Create VPC with DNS support enabled
# This VPC will host our production workloads
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  # Tags are required for cost allocation
  tags = merge(
    {
      Name = var.vpc_name
    },
    var.tags
  )
}

# Public subnets are created in each availability zone
# These subnets have route to Internet Gateway
resource "aws_subnet" "public" {
  count = length(var.availability_zones)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.vpc_name}-public-${var.availability_zones[count.index]}"
    Type = "public"
  }
}
```

### 3. ADR (Architecture Decision Records)
```markdown
# ADR 001: Use Terraform for Infrastructure as Code

## Status
Accepted

## Context
We need to manage our cloud infrastructure in a repeatable, version-controlled manner.

## Decision
We will use Terraform as our primary IaC tool because:
- Declarative syntax
- Multi-cloud support
- Large community and ecosystem
- State management capabilities

## Consequences
**Positive:**
- Infrastructure changes are version controlled
- Consistent environments across dev/staging/prod
- Easy to review changes via pull requests

**Negative:**
- Team needs to learn HCL
- State management adds complexity
- Requires additional tooling for secrets management
```

## Monitoring and Compliance

### 1. Resource Tagging
```hcl
locals {
  common_tags = {
    ManagedBy   = "Terraform"
    Environment = var.environment
    Project     = var.project_name
    CostCenter  = var.cost_center
    Owner       = var.owner_email
    Compliance  = var.compliance_level
    CreatedBy   = "terraform"
    CreatedAt   = timestamp()
  }
}

resource "aws_instance" "web" {
  # ...

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-web-${count.index}"
      Role = "web-server"
    }
  )
}
```

### 2. Cost Tracking
```hcl
# Use tags for cost allocation
resource "aws_instance" "web" {
  # ...

  tags = {
    CostCenter  = "engineering"
    Project     = "web-app"
    Environment = "production"
  }
}

# Implement budget alerts
resource "aws_budgets_budget" "monthly" {
  name              = "${var.environment}-monthly-budget"
  budget_type       = "COST"
  limit_amount      = "1000"
  limit_unit        = "USD"
  time_period_start = "2024-01-01_00:00"
  time_unit         = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.billing_alert_email]
  }
}
```

### 3. Compliance Monitoring
```hcl
# AWS Config Rules
resource "aws_config_config_rule" "s3_bucket_encryption" {
  name = "s3-bucket-server-side-encryption-enabled"

  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.main]
}

resource "aws_config_config_rule" "rds_encryption" {
  name = "rds-storage-encrypted"

  source {
    owner             = "AWS"
    source_identifier = "RDS_STORAGE_ENCRYPTED"
  }

  depends_on = [aws_config_configuration_recorder.main]
}
```

## Cost Management

### 1. Right-sizing Resources
```hcl
# Use variables for environment-specific sizing
locals {
  instance_types = {
    dev     = "t3.micro"
    staging = "t3.small"
    prod    = "t3.large"
  }

  instance_counts = {
    dev     = 1
    staging = 2
    prod    = 3
  }
}

resource "aws_instance" "web" {
  count         = local.instance_counts[var.environment]
  instance_type = local.instance_types[var.environment]
  # ...
}
```

### 2. Lifecycle Policies
```hcl
# S3 lifecycle rules
resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "log-retention"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}
```

### 3. Auto-scaling
```hcl
resource "aws_autoscaling_group" "web" {
  name                = "${var.environment}-web-asg"
  min_size            = var.min_instances
  max_size            = var.max_instances
  desired_capacity    = var.desired_instances
  vpc_zone_identifier = aws_subnet.private[*].id

  launch_template {
    id      = aws_launch_template.web.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${var.environment}-web"
    propagate_at_launch = true
  }
}

# Scale down during off-hours
resource "aws_autoscaling_schedule" "scale_down" {
  scheduled_action_name  = "scale-down-evening"
  min_size               = 1
  max_size               = 2
  desired_capacity       = 1
  recurrence             = "0 20 * * MON-FRI"
  autoscaling_group_name = aws_autoscaling_group.web.name
}

resource "aws_autoscaling_schedule" "scale_up" {
  scheduled_action_name  = "scale-up-morning"
  min_size               = var.min_instances
  max_size               = var.max_instances
  desired_capacity       = var.desired_instances
  recurrence             = "0 8 * * MON-FRI"
  autoscaling_group_name = aws_autoscaling_group.web.name
}
```
