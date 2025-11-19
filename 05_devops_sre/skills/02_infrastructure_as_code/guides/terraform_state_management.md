# Terraform State Management Guide

## Table of Contents
- [Understanding State](#understanding-state)
- [Local State](#local-state)
- [Remote State](#remote-state)
- [State Locking](#state-locking)
- [State Operations](#state-operations)
- [Workspaces](#workspaces)
- [State Migration](#state-migration)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Understanding State

### What is Terraform State?
Terraform state is a JSON file that maps your configuration to real-world resources. It tracks metadata and enables Terraform to know what infrastructure exists and what needs to be created, updated, or destroyed.

### State File Structure
```json
{
  "version": 4,
  "terraform_version": "1.6.0",
  "serial": 1,
  "lineage": "c3ab8ff13720e8ad9047dd39466b3c8974e592c2fa383d4a3960714caef0c4f2",
  "outputs": {
    "instance_id": {
      "value": "i-1234567890abcdef0",
      "type": "string"
    }
  },
  "resources": [
    {
      "mode": "managed",
      "type": "aws_instance",
      "name": "web",
      "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
      "instances": [
        {
          "schema_version": 1,
          "attributes": {
            "id": "i-1234567890abcdef0",
            "ami": "ami-0c55b159cbfafe1f0",
            "instance_type": "t3.micro"
          }
        }
      ]
    }
  ]
}
```

### Why State Matters
1. **Mapping**: Maps configuration to real resources
2. **Metadata**: Tracks resource dependencies
3. **Performance**: Caches resource attributes
4. **Collaboration**: Enables team workflows

### State File Contents
- **Version**: State file format version
- **Serial**: Increments with each state change
- **Lineage**: UUID to prevent state conflicts
- **Outputs**: Output values from configuration
- **Resources**: All managed resources with attributes

## Local State

### Default Local State
```bash
# Initialize Terraform (creates local state)
terraform init

# Apply configuration (creates terraform.tfstate)
terraform apply

# State file is created in current directory
ls -la
# terraform.tfstate
# terraform.tfstate.backup
```

### Local State Files
```bash
# Primary state file
terraform.tfstate

# Backup of previous state
terraform.tfstate.backup

# Lock file (created during operations)
.terraform.tfstate.lock.info
```

### Limitations of Local State
1. **No Collaboration**: Can't share with team
2. **No Locking**: Risk of concurrent modifications
3. **No Security**: Stored in plain text
4. **Single Point of Failure**: Loss of file = loss of state
5. **No Versioning**: Limited ability to recover

## Remote State

### Why Remote State?
1. **Collaboration**: Multiple team members can access
2. **Locking**: Prevents concurrent modifications
3. **Security**: Encrypted storage
4. **Backup**: Automatic versioning and backup
5. **Automation**: CI/CD integration

### S3 Backend (AWS)

#### Setup S3 Backend Infrastructure
```hcl
# state-backend/main.tf
provider "aws" {
  region = "us-west-2"
}

# S3 Bucket for state
resource "aws_s3_bucket" "terraform_state" {
  bucket = "mycompany-terraform-state"

  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name        = "Terraform State"
    Environment = "global"
    ManagedBy   = "Terraform"
  }
}

# Enable versioning
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.terraform_state.id
    }
  }
}

# KMS key for encryption
resource "aws_kms_key" "terraform_state" {
  description             = "KMS key for Terraform state encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name = "Terraform State Encryption Key"
  }
}

resource "aws_kms_alias" "terraform_state" {
  name          = "alias/terraform-state"
  target_key_id = aws_kms_key.terraform_state.key_id
}

# Block public access
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB table for state locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-state-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name        = "Terraform State Lock"
    Environment = "global"
  }
}

# IAM policy for Terraform users
data "aws_iam_policy_document" "terraform_state_access" {
  statement {
    effect = "Allow"

    actions = [
      "s3:ListBucket",
    ]

    resources = [
      aws_s3_bucket.terraform_state.arn,
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
    ]

    resources = [
      "${aws_s3_bucket.terraform_state.arn}/*",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
    ]

    resources = [
      aws_dynamodb_table.terraform_locks.arn,
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "kms:Decrypt",
      "kms:Encrypt",
      "kms:DescribeKey",
      "kms:GenerateDataKey",
    ]

    resources = [
      aws_kms_key.terraform_state.arn,
    ]
  }
}

resource "aws_iam_policy" "terraform_state_access" {
  name        = "TerraformStateAccess"
  description = "Policy for accessing Terraform state"
  policy      = data.aws_iam_policy_document.terraform_state_access.json
}

# Output values
output "state_bucket_id" {
  value = aws_s3_bucket.terraform_state.id
}

output "state_lock_table_id" {
  value = aws_dynamodb_table.terraform_locks.id
}

output "kms_key_id" {
  value = aws_kms_key.terraform_state.id
}
```

#### Deploy Backend Infrastructure
```bash
# Deploy the backend infrastructure first (using local state)
cd state-backend
terraform init
terraform apply

# Note the outputs
terraform output
```

#### Configure Backend in Project
```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "prod/us-west-2/vpc/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    kms_key_id     = "arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012"
    dynamodb_table = "terraform-state-lock"

    # Optional: Use role assumption
    role_arn     = "arn:aws:iam::123456789012:role/TerraformRole"
    session_name = "TerraformSession"
  }
}
```

#### Migrate to Remote Backend
```bash
# Initialize with new backend
terraform init

# Terraform will prompt to migrate state
# Type "yes" to copy local state to S3

# Verify state is in S3
aws s3 ls s3://mycompany-terraform-state/prod/us-west-2/vpc/

# Remove local state files (after verification)
rm terraform.tfstate terraform.tfstate.backup
```

### Azure Backend

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfstatestorage"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"

    # Optional: Use service principal
    client_id       = "00000000-0000-0000-0000-000000000000"
    client_secret   = var.client_secret
    tenant_id       = "00000000-0000-0000-0000-000000000000"
    subscription_id = "00000000-0000-0000-0000-000000000000"
  }
}
```

### GCS Backend (Google Cloud)

```hcl
terraform {
  backend "gcs" {
    bucket = "mycompany-terraform-state"
    prefix = "prod/vpc"

    # Optional: encryption
    encryption_key = var.encryption_key
  }
}
```

### Terraform Cloud Backend

```hcl
terraform {
  cloud {
    organization = "my-organization"

    workspaces {
      name = "production-vpc"
    }
  }
}
```

### Consul Backend

```hcl
terraform {
  backend "consul" {
    address = "consul.example.com"
    scheme  = "https"
    path    = "terraform/state/prod"

    # Optional: authentication
    http_auth = "${var.consul_username}:${var.consul_password}"
  }
}
```

## State Locking

### What is State Locking?
State locking prevents concurrent operations that could corrupt state. When one user runs `terraform apply`, the state is locked until the operation completes.

### DynamoDB Locking (AWS)
```hcl
terraform {
  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "terraform-state-lock"  # Enables locking
  }
}
```

### Lock Information
```bash
# Lock is automatically acquired
terraform apply

# If locked, you'll see:
# Error: Error locking state: Error acquiring the state lock
# Lock Info:
#   ID:        a1b2c3d4-e5f6-7890-abcd-ef1234567890
#   Path:      mycompany-terraform-state/prod/terraform.tfstate
#   Operation: OperationTypeApply
#   Who:       user@hostname
#   Version:   1.6.0
#   Created:   2024-01-15 10:30:00.000000 UTC
```

### Force Unlock
```bash
# If operation was interrupted and lock wasn't released
terraform force-unlock <lock-id>

# Example
terraform force-unlock a1b2c3d4-e5f6-7890-abcd-ef1234567890

# WARNING: Only use if you're certain no operation is running
```

### Lock Timeout
```hcl
# Configure custom lock timeout
terraform {
  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "terraform-state-lock"

    # Wait up to 30 minutes for lock
    lock_timeout = "30m"
  }
}
```

## State Operations

### View State
```bash
# List all resources in state
terraform state list

# Show specific resource
terraform state show aws_instance.web

# Show all resources in detail
terraform show

# Output state as JSON
terraform show -json

# Pull remote state
terraform state pull > current-state.json
```

### Modify State
```bash
# Move resource within state (rename)
terraform state mv aws_instance.old aws_instance.new

# Move resource to another module
terraform state mv aws_instance.web module.web.aws_instance.web

# Move resource to another state file
terraform state mv -state-out=../other/terraform.tfstate aws_instance.web aws_instance.web

# Remove resource from state (doesn't destroy)
terraform state rm aws_instance.web

# Remove all instances of a resource
terraform state rm 'aws_instance.web[*]'
```

### Replace Resources
```bash
# Mark resource for replacement
terraform apply -replace=aws_instance.web

# Replace multiple resources
terraform apply -replace=aws_instance.web -replace=aws_instance.db
```

### Import Resources
```bash
# Import existing AWS instance
terraform import aws_instance.web i-1234567890abcdef0

# Import S3 bucket
terraform import aws_s3_bucket.data my-existing-bucket

# Import with module
terraform import module.vpc.aws_vpc.main vpc-12345678

# Import with for_each
terraform import 'aws_instance.web["instance-1"]' i-1234567890abcdef0
```

### Backup and Restore
```bash
# Backup current state
terraform state pull > backup-$(date +%Y%m%d-%H%M%S).tfstate

# Push state (restore from backup)
terraform state push backup-20240115-120000.tfstate

# WARNING: This overwrites remote state
```

### Refresh State
```bash
# Refresh state from real infrastructure
terraform refresh

# Or use -refresh-only flag
terraform plan -refresh-only
terraform apply -refresh-only

# Refresh is automatic with plan/apply (can disable)
terraform plan -refresh=false
```

## Workspaces

### What are Workspaces?
Workspaces allow multiple state files within a single backend, useful for managing multiple environments.

### Workspace Commands
```bash
# List workspaces (* indicates current)
terraform workspace list

# Show current workspace
terraform workspace show

# Create new workspace
terraform workspace new dev

# Switch workspace
terraform workspace select dev

# Delete workspace (must be empty and not selected)
terraform workspace delete dev
```

### Using Workspaces in Configuration
```hcl
# main.tf
locals {
  workspace_config = {
    dev = {
      instance_type  = "t3.micro"
      instance_count = 1
    }
    staging = {
      instance_type  = "t3.small"
      instance_count = 2
    }
    prod = {
      instance_type  = "t3.large"
      instance_count = 3
    }
  }

  config = local.workspace_config[terraform.workspace]
}

resource "aws_instance" "web" {
  count = local.config.instance_count

  ami           = data.aws_ami.ubuntu.id
  instance_type = local.config.instance_type

  tags = {
    Name        = "${terraform.workspace}-web-${count.index}"
    Workspace   = terraform.workspace
    Environment = terraform.workspace
  }
}
```

### Workspace State Storage

#### S3 Backend with Workspaces
```bash
# S3 structure with workspaces:
# s3://bucket/path/
#   default/terraform.tfstate
#   dev/terraform.tfstate
#   staging/terraform.tfstate
#   prod/terraform.tfstate
```

#### Configuration
```hcl
terraform {
  backend "s3" {
    bucket = "mycompany-terraform-state"
    key    = "project/terraform.tfstate"
    region = "us-west-2"

    # Workspace prefix (optional)
    workspace_key_prefix = "workspaces"
  }
}

# Results in:
# s3://bucket/workspaces/dev/project/terraform.tfstate
# s3://bucket/workspaces/prod/project/terraform.tfstate
```

### Workspace Best Practices
1. **Use for ephemeral environments**: Dev, feature branches
2. **Not for production**: Use separate state files for prod
3. **Document workspace strategy**: Clear naming conventions
4. **Avoid in modules**: Modules shouldn't depend on workspaces

### Alternative: Separate Directories
```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   └── backend.tf  # state key: dev/terraform.tfstate
│   ├── staging/
│   │   ├── main.tf
│   │   └── backend.tf  # state key: staging/terraform.tfstate
│   └── prod/
│       ├── main.tf
│       └── backend.tf  # state key: prod/terraform.tfstate
```

## State Migration

### Migrate from Local to Remote
```bash
# 1. Add backend configuration
cat > backend.tf << EOF
terraform {
  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}
EOF

# 2. Re-initialize
terraform init

# 3. Terraform detects existing state and prompts to migrate
# Enter "yes" to copy local state to remote backend

# 4. Verify migration
terraform state list

# 5. Remove local state files
rm terraform.tfstate terraform.tfstate.backup
```

### Migrate Between Backends
```bash
# 1. Export current state
terraform state pull > current-state.json

# 2. Update backend configuration
# Edit backend.tf with new backend config

# 3. Re-initialize with -migrate-state
terraform init -migrate-state

# 4. Verify migration
terraform state list
```

### Migrate Between Workspaces
```bash
# 1. Switch to source workspace
terraform workspace select dev

# 2. Pull state
terraform state pull > dev-state.json

# 3. Switch to target workspace
terraform workspace select new-dev

# 4. Push state
terraform state push dev-state.json
```

### Split State File
```bash
# 1. List resources in monolithic state
terraform state list

# 2. Move resources to new state file
terraform state mv -state-out=../networking/terraform.tfstate \
  aws_vpc.main \
  'aws_subnet.public[*]' \
  'aws_subnet.private[*]'

# 3. In new directory, initialize with appropriate backend
cd ../networking
terraform init

# 4. Verify resources moved correctly
terraform state list
terraform plan  # Should show no changes
```

### Merge State Files
```bash
# 1. Pull both state files
cd project-a
terraform state pull > state-a.json

cd ../project-b
terraform state pull > state-b.json

# 2. Manually merge JSON (carefully!)
# Or use terraform state mv to move resources

# 3. In target project, push merged state
cd ../project-merged
terraform state push merged-state.json
```

## Security

### State File Security Risks
State files can contain sensitive data:
- Database passwords
- API keys
- SSL certificates
- Private keys
- Connection strings

### Secure State Storage

#### Encryption at Rest
```hcl
# S3 with KMS encryption
terraform {
  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true  # Enable encryption
    kms_key_id     = "arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012"
  }
}
```

#### Access Control
```hcl
# IAM policy with least privilege
data "aws_iam_policy_document" "terraform_state" {
  statement {
    effect = "Allow"
    actions = [
      "s3:ListBucket",
    ]
    resources = [
      "arn:aws:s3:::mycompany-terraform-state",
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
    ]
    resources = [
      "arn:aws:s3:::mycompany-terraform-state/prod/*",
    ]
    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-server-side-encryption"
      values   = ["aws:kms"]
    }
  }
}
```

#### Sensitive Values
```hcl
# Mark outputs as sensitive
output "database_password" {
  value     = random_password.db.result
  sensitive = true
}

# Mark variables as sensitive
variable "api_key" {
  type      = string
  sensitive = true
}

# Sensitive values are still in state, but won't be shown in logs
```

### Audit Logging
```hcl
# Enable S3 bucket logging
resource "aws_s3_bucket_logging" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "terraform-state-access/"
}

# Enable CloudTrail for API calls
resource "aws_cloudtrail" "terraform_state" {
  name                          = "terraform-state-audit"
  s3_bucket_name                = aws_s3_bucket.audit_logs.id
  include_global_service_events = true

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["${aws_s3_bucket.terraform_state.arn}/"]
    }
  }
}
```

### State File Versioning
```hcl
# Enable S3 versioning for recovery
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Lifecycle policy for version management
resource "aws_s3_bucket_lifecycle_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    id     = "state-version-expiration"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "STANDARD_IA"
    }
  }
}
```

## Troubleshooting

### State Corruption
```bash
# Symptoms: "state snapshot was created by a newer version"
# or JSON parsing errors

# Solution 1: Restore from backup
terraform state pull > corrupted-state.json
# Download previous version from S3
aws s3api get-object \
  --bucket mycompany-terraform-state \
  --key prod/terraform.tfstate \
  --version-id <previous-version-id> \
  restored-state.tfstate
terraform state push restored-state.tfstate

# Solution 2: Rebuild state
# Remove resources and re-import
terraform state rm aws_instance.web
terraform import aws_instance.web i-1234567890abcdef0
```

### State Drift
```bash
# Detect drift
terraform plan -refresh-only

# Show what changed
terraform show

# Update state to match reality
terraform apply -refresh-only

# Or ignore drift for specific attributes
resource "aws_instance" "web" {
  # ...

  lifecycle {
    ignore_changes = [
      tags,
      user_data,
    ]
  }
}
```

### Locked State
```bash
# Error: state is locked
# Check who has the lock
aws dynamodb get-item \
  --table-name terraform-state-lock \
  --key '{"LockID": {"S": "mycompany-terraform-state/prod/terraform.tfstate"}}' \
  --query 'Item.Info.S' \
  --output text | jq .

# If safe to do so, force unlock
terraform force-unlock <lock-id>
```

### Missing State
```bash
# If state file is lost but resources exist

# Option 1: Recover from backup
aws s3api list-object-versions \
  --bucket mycompany-terraform-state \
  --prefix prod/terraform.tfstate

aws s3api get-object \
  --bucket mycompany-terraform-state \
  --key prod/terraform.tfstate \
  --version-id <version-id> \
  recovered-state.tfstate

# Option 2: Rebuild state by importing
terraform import aws_vpc.main vpc-12345678
terraform import aws_subnet.public[0] subnet-12345678
# ... continue for all resources
```

### State Conflicts
```bash
# Error: state conflict, lineage doesn't match

# This happens when state files diverge

# Solution: Identify the correct state
terraform state pull > local-state.json
aws s3 cp s3://mycompany-terraform-state/prod/terraform.tfstate remote-state.json

# Compare lineage
jq '.lineage' local-state.json
jq '.lineage' remote-state.json

# Choose correct state and push
terraform state push correct-state.json
```

## Best Practices

### 1. Always Use Remote State for Teams
```hcl
# Never use local state in team environments
terraform {
  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}
```

### 2. Enable State Locking
```hcl
# Always use locking to prevent concurrent modifications
terraform {
  backend "s3" {
    # ...
    dynamodb_table = "terraform-state-lock"  # Required for locking
  }
}
```

### 3. Enable Versioning
```hcl
# Keep historical versions for recovery
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}
```

### 4. Encrypt State
```hcl
# Always encrypt sensitive state data
terraform {
  backend "s3" {
    # ...
    encrypt    = true
    kms_key_id = "arn:aws:kms:us-west-2:123456789012:key/..."
  }
}
```

### 5. Use Least Privilege Access
```hcl
# Restrict who can access state
# Separate read and write permissions
# Use IAM roles with temporary credentials
```

### 6. Regular Backups
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="state-backups"
mkdir -p $BACKUP_DIR

# Pull current state
terraform state pull > "$BACKUP_DIR/state-$(date +%Y%m%d-%H%M%S).json"

# Keep only last 30 days
find $BACKUP_DIR -name "state-*.json" -mtime +30 -delete
```

### 7. Organize State Files
```bash
# Use hierarchical key structure
s3://bucket/
  └── organization/
      ├── dev/
      │   ├── us-west-2/
      │   │   ├── networking/terraform.tfstate
      │   │   ├── compute/terraform.tfstate
      │   │   └── data/terraform.tfstate
      │   └── eu-west-1/
      └── prod/
          ├── us-west-2/
          └── eu-west-1/
```

### 8. Document State Structure
```markdown
# State Organization

## Structure
- `dev/`: Development environment
- `staging/`: Staging environment
- `prod/`: Production environment

## State Files
- `networking/`: VPC, subnets, routing
- `compute/`: EC2, ECS, Lambda
- `data/`: RDS, DynamoDB, S3

## Access
- Developers: Read access to dev, no access to prod
- Ops: Full access to all environments
- CI/CD: Write access via assumed roles
```

### 9. Periodic State Audits
```bash
# Check for orphaned resources
terraform plan

# Verify resource tags
terraform state show | grep tags

# Review state size
aws s3 ls s3://mycompany-terraform-state --recursive --human-readable
```

### 10. Disaster Recovery Plan
```markdown
# State Recovery Procedure

1. **Identify Issue**: State corruption or loss
2. **Stop Operations**: Prevent further changes
3. **Assess Damage**: Check what was lost
4. **Restore from Backup**: Use S3 versioning or backup
5. **Verify**: Run `terraform plan` to ensure consistency
6. **Document**: Record incident and resolution
7. **Prevent**: Review what caused the issue
```
