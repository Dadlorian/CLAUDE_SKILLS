# State Management Reference

## Overview

Terraform state is a critical component that maps your configuration to real-world resources. Proper state management is essential for team collaboration, security, and infrastructure reliability.

## State File Structure

```json
{
  "version": 4,
  "terraform_version": "1.6.0",
  "serial": 42,
  "lineage": "unique-uuid-here",
  "outputs": {
    "vpc_id": {
      "value": "vpc-12345678",
      "type": "string"
    }
  },
  "resources": [
    {
      "mode": "managed",
      "type": "aws_vpc",
      "name": "main",
      "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
      "instances": [
        {
          "schema_version": 1,
          "attributes": {
            "id": "vpc-12345678",
            "cidr_block": "10.0.0.0/16",
            "tags": {
              "Name": "main-vpc"
            }
          },
          "private": "sensitive-data-encrypted"
        }
      ]
    }
  ]
}
```

## Local vs Remote State

### Local State (Default)
```hcl
# No backend configuration - state stored in terraform.tfstate
terraform {
  required_version = ">= 1.5"
}
```

**Pros:**
- Simple setup
- No external dependencies
- Fast operations

**Cons:**
- Not suitable for teams
- No locking mechanism
- Risk of state loss
- Secrets stored in plaintext

### Remote State (Recommended)
```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/vpc/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

**Pros:**
- Team collaboration
- State locking
- Encryption
- Versioning
- Centralized management

## Backend Types

### S3 Backend (AWS)
```hcl
terraform {
  backend "s3" {
    bucket         = "terraform-state-bucket"
    key            = "path/to/terraform.tfstate"
    region         = "us-east-1"

    # Encryption
    encrypt        = true
    kms_key_id     = "arn:aws:kms:us-east-1:ACCOUNT:key/KEY-ID"

    # Locking
    dynamodb_table = "terraform-locks"

    # Access
    role_arn       = "arn:aws:iam::ACCOUNT:role/TerraformRole"

    # Workspace support
    workspace_key_prefix = "workspaces"
  }
}
```

**Setup:**
```hcl
# State bucket
resource "aws_s3_bucket" "terraform_state" {
  bucket = "my-terraform-state"

  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name        = "Terraform State"
    Environment = "prod"
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
      kms_master_key_id = aws_kms_key.terraform_state.arn
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

# DynamoDB table for locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "Terraform State Locks"
    Environment = "prod"
  }
}

# KMS key for encryption
resource "aws_kms_key" "terraform_state" {
  description             = "KMS key for Terraform state encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = {
    Name = "Terraform State KMS Key"
  }
}

resource "aws_kms_alias" "terraform_state" {
  name          = "alias/terraform-state"
  target_key_id = aws_kms_key.terraform_state.key_id
}
```

### Azure Backend
```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "terraformstate"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"

    # Optional
    use_azuread_auth     = true
    subscription_id      = "00000000-0000-0000-0000-000000000000"
    tenant_id            = "00000000-0000-0000-0000-000000000000"
  }
}
```

### GCS Backend (Google Cloud)
```hcl
terraform {
  backend "gcs" {
    bucket  = "terraform-state-bucket"
    prefix  = "terraform/state"

    # Optional
    encryption_key = "base64-encoded-key"
  }
}
```

### Terraform Cloud
```hcl
terraform {
  cloud {
    organization = "my-org"

    workspaces {
      name = "production-vpc"
      # or use tags for dynamic workspaces
      # tags = ["production", "vpc"]
    }
  }
}
```

### Consul Backend
```hcl
terraform {
  backend "consul" {
    address = "consul.example.com:8500"
    scheme  = "https"
    path    = "terraform/state"

    # Optional
    lock    = true
  }
}
```

### HTTP Backend
```hcl
terraform {
  backend "http" {
    address        = "https://api.example.com/terraform/state"
    lock_address   = "https://api.example.com/terraform/lock"
    unlock_address = "https://api.example.com/terraform/unlock"

    # Authentication
    username = "terraform"
    password = var.backend_password
  }
}
```

## State Locking

### DynamoDB Locking (S3 Backend)
```hcl
terraform {
  backend "s3" {
    bucket         = "terraform-state"
    key            = "state.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"  # Enable locking
  }
}
```

**Lock Table Schema:**
- Primary Key: `LockID` (String)
- Attributes: Automatically managed by Terraform

### Manual Lock Override
```bash
# Force unlock (use with caution!)
terraform force-unlock LOCK_ID

# Get lock ID from error message
# Error: Error acquiring the state lock
# Lock ID: f4c2a7b8-1234-5678-90ab-cdef12345678
```

## State Commands

### List Resources
```bash
# List all resources in state
terraform state list

# Filter by resource type
terraform state list aws_instance

# Filter by module
terraform state list module.vpc
```

### Show Resource Details
```bash
# Show specific resource
terraform state show aws_instance.web

# Output in JSON
terraform state show -json aws_instance.web | jq
```

### Move Resources
```bash
# Rename resource
terraform state mv aws_instance.web aws_instance.web_server

# Move to module
terraform state mv aws_instance.web module.compute.aws_instance.web

# Move from module
terraform state mv module.compute.aws_instance.web aws_instance.web

# Move with for_each/count
terraform state mv 'aws_instance.web[0]' 'aws_instance.web["primary"]'
```

### Remove Resources
```bash
# Remove from state (resource still exists in cloud)
terraform state rm aws_instance.web

# Remove module
terraform state rm module.vpc

# Remove with count
terraform state rm 'aws_instance.web[0]'
```

### Pull/Push State
```bash
# Pull remote state to local file
terraform state pull > terraform.tfstate

# Push local state to remote
terraform state push terraform.tfstate

# Verify before pushing
terraform state push -lock=true terraform.tfstate
```

### Replace Provider
```bash
# Update provider address in state
terraform state replace-provider \
  registry.terraform.io/-/aws \
  hashicorp/aws
```

## Workspaces

### Workspace Commands
```bash
# List workspaces
terraform workspace list

# Create workspace
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Select workspace
terraform workspace select dev

# Show current workspace
terraform workspace show

# Delete workspace
terraform workspace delete dev
```

### Using Workspaces in Configuration
```hcl
locals {
  environment = terraform.workspace

  instance_type = {
    dev     = "t3.micro"
    staging = "t3.small"
    prod    = "t3.large"
  }

  instance_count = {
    dev     = 1
    staging = 2
    prod    = 5
  }
}

resource "aws_instance" "web" {
  count = local.instance_count[local.environment]

  ami           = data.aws_ami.ubuntu.id
  instance_type = local.instance_type[local.environment]

  tags = {
    Name        = "${local.environment}-web-${count.index}"
    Environment = local.environment
  }
}

# Workspace-specific S3 key
terraform {
  backend "s3" {
    bucket = "terraform-state"
    key    = "state.tfstate"  # Becomes: workspaces/dev/state.tfstate
    region = "us-east-1"

    workspace_key_prefix = "workspaces"
  }
}
```

### Workspace Best Practices

**Good Use Cases:**
- Development/staging/production environments
- Feature branch testing
- Temporary infrastructure for testing

**Avoid For:**
- Completely different applications
- Different AWS accounts (use separate backends)
- Different regions (can complicate management)

## State Import

### Import Existing Resources
```bash
# Basic import
terraform import aws_instance.web i-1234567890abcdef0

# Import with module
terraform import module.vpc.aws_vpc.main vpc-12345678

# Import with for_each
terraform import 'aws_instance.web["prod"]' i-1234567890abcdef0

# Import with count
terraform import 'aws_instance.web[0]' i-1234567890abcdef0
```

### Import Process
```hcl
# 1. Write configuration
resource "aws_instance" "imported" {
  ami           = "ami-12345678"  # Get from console
  instance_type = "t3.micro"      # Get from console

  # Add other required attributes
}

# 2. Import
# terraform import aws_instance.imported i-1234567890abcdef0

# 3. Run plan to see differences
# terraform plan

# 4. Update configuration to match
# 5. Verify with plan (should show no changes)
```

### Bulk Import Script
```bash
#!/bin/bash

# Import multiple resources
resources=(
  "aws_vpc.main:vpc-12345678"
  "aws_subnet.public_1:subnet-12345678"
  "aws_subnet.public_2:subnet-87654321"
  "aws_security_group.web:sg-12345678"
)

for resource in "${resources[@]}"; do
  IFS=':' read -r tf_resource aws_id <<< "$resource"
  echo "Importing $tf_resource with ID $aws_id"
  terraform import "$tf_resource" "$aws_id"
done
```

## State Migration

### Migrate Local to Remote
```bash
# 1. Add backend configuration
cat >> backend.tf <<EOF
terraform {
  backend "s3" {
    bucket = "terraform-state"
    key    = "state.tfstate"
    region = "us-east-1"
  }
}
EOF

# 2. Re-initialize with migration
terraform init -migrate-state

# 3. Verify state was migrated
aws s3 ls s3://terraform-state/

# 4. Remove local state (after verification)
rm terraform.tfstate terraform.tfstate.backup
```

### Migrate Between Backends
```hcl
# Old backend (comment out)
# terraform {
#   backend "s3" {
#     bucket = "old-terraform-state"
#     key    = "state.tfstate"
#     region = "us-east-1"
#   }
# }

# New backend
terraform {
  backend "s3" {
    bucket = "new-terraform-state"
    key    = "state.tfstate"
    region = "us-west-2"
  }
}
```

```bash
# Migrate
terraform init -migrate-state
```

### Split State Files
```bash
# 1. Pull current state
terraform state pull > full-state.json

# 2. Create new configuration for subset
mkdir ../vpc-stack
cp vpc.tf ../vpc-stack/

# 3. Initialize new stack
cd ../vpc-stack
terraform init

# 4. Move resources
cd ../original-stack
terraform state mv -state-out=../vpc-stack/terraform.tfstate \
  aws_vpc.main \
  ../vpc-stack/aws_vpc.main

# Repeat for all VPC resources
```

## State Encryption

### S3 Backend Encryption
```hcl
terraform {
  backend "s3" {
    bucket  = "terraform-state"
    key     = "state.tfstate"
    region  = "us-east-1"
    encrypt = true  # Enable SSE-S3 or SSE-KMS

    # Use KMS encryption
    kms_key_id = "arn:aws:kms:us-east-1:ACCOUNT:key/KEY-ID"
  }
}
```

### Sensitive Data Handling
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

# Sensitive values are redacted in logs but stored in state
```

## State Backup and Recovery

### Automatic S3 Versioning
```hcl
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}
```

### Manual Backup
```bash
# Backup current state
terraform state pull > backup-$(date +%Y%m%d-%H%M%S).tfstate

# Automated backup script
#!/bin/bash
BACKUP_DIR="./state-backups"
mkdir -p "$BACKUP_DIR"
terraform state pull > "$BACKUP_DIR/terraform-$(date +%Y%m%d-%H%M%S).tfstate"

# Keep only last 30 days of backups
find "$BACKUP_DIR" -name "terraform-*.tfstate" -mtime +30 -delete
```

### Recovery from Backup
```bash
# List S3 versions
aws s3api list-object-versions \
  --bucket terraform-state \
  --prefix state.tfstate

# Download specific version
aws s3api get-object \
  --bucket terraform-state \
  --key state.tfstate \
  --version-id VERSION_ID \
  recovered-state.tfstate

# Push recovered state
terraform state push recovered-state.tfstate
```

## State Locking Best Practices

### Handle Lock Contention
```bash
# Set custom lock timeout (default: 0s)
terraform apply -lock-timeout=10m

# Check lock status
aws dynamodb get-item \
  --table-name terraform-locks \
  --key '{"LockID":{"S":"bucket/path/to/state"}}'
```

### Graceful Lock Handling
```bash
#!/bin/bash
# Deployment script with lock handling

MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if terraform apply -auto-approve -lock-timeout=5m; then
    echo "Deployment successful"
    exit 0
  else
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Deployment failed, retry $RETRY_COUNT of $MAX_RETRIES"
    sleep 60
  fi
done

echo "Deployment failed after $MAX_RETRIES attempts"
exit 1
```

## State File Security

### IAM Policies

**State Bucket Access**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketVersioning"
      ],
      "Resource": "arn:aws:s3:::terraform-state"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::terraform-state/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:ACCOUNT:table/terraform-locks"
    }
  ]
}
```

### Audit Logging
```hcl
# Enable CloudTrail for state bucket
resource "aws_cloudtrail" "terraform_state" {
  name                          = "terraform-state-audit"
  s3_bucket_name                = aws_s3_bucket.cloudtrail.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["${aws_s3_bucket.terraform_state.arn}/*"]
    }
  }
}
```

## Troubleshooting

### Corrupted State
```bash
# Backup current state
terraform state pull > corrupted-state.json

# Manually edit state file (use with extreme caution)
# Fix JSON formatting issues

# Validate state
terraform state list

# Push corrected state
terraform state push corrected-state.json
```

### State Drift Detection
```bash
# Detect drift
terraform plan -refresh-only

# Apply drift (update state without changing resources)
terraform apply -refresh-only
```

### State Lock Issues
```bash
# View lock information
aws dynamodb get-item \
  --table-name terraform-locks \
  --key '{"LockID":{"S":"terraform-state/path/state.tfstate-md5"}}' \
  | jq -r '.Item.Info.S' | jq

# Force unlock
terraform force-unlock LOCK_ID
```

## Resources

- State Documentation: terraform.io/docs/language/state
- Backend Types: terraform.io/docs/language/settings/backends
- State Commands: terraform.io/docs/cli/commands/state
- Workspaces: terraform.io/docs/language/state/workspaces
