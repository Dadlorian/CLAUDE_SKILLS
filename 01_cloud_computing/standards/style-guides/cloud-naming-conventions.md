# Cloud Naming Conventions

## Overview

This guide establishes comprehensive naming conventions for cloud resources across AWS, Azure, and GCP. Based on Microsoft's Cloud Adoption Framework, AWS Well-Architected naming guidance, Google Cloud best practices, and Fortune 500 enterprise patterns.

## Table of Contents

1. [General Naming Principles](#general-naming-principles)
2. [Universal Naming Pattern](#universal-naming-pattern)
3. [AWS Naming Conventions](#aws-naming-conventions)
4. [Azure Naming Conventions](#azure-naming-conventions)
5. [GCP Naming Conventions](#gcp-naming-conventions)
6. [Multi-Cloud Standards](#multi-cloud-standards)
7. [Tagging Standards](#tagging-standards)
8. [Naming Registry](#naming-registry)
9. [Anti-Patterns](#anti-patterns)
10. [References](#references)

## General Naming Principles

### Core Tenets

1. **Descriptive**: Name should indicate resource type and purpose
2. **Consistent**: Follow same pattern across all resources
3. **Unique**: Global uniqueness where required (S3 buckets, storage accounts)
4. **Hierarchical**: Reflect organizational and environment structure
5. **Length-Aware**: Respect platform length limits
6. **Character-Safe**: Use only allowed characters
7. **Future-Proof**: Allow for growth and changes
8. **Human-Readable**: Engineers should understand at a glance

### Case Conventions

- **kebab-case**: AWS resource names, GCP resources (`my-app-prod-api`)
- **snake_case**: Database objects, variables (`user_profile_table`)
- **PascalCase**: Azure resources, CloudFormation logical IDs (`MyAppProdApi`)
- **camelCase**: Programming constructs (`myAppProdApi`)
- **lowercase**: DNS names, S3 buckets (`myapp-prod-bucket`)

### Character Restrictions

**Allowed Characters by Platform**:

| Platform | Allowed | Notes |
|----------|---------|-------|
| AWS | a-z, A-Z, 0-9, - _ . : / | Varies by service |
| Azure | a-z, A-Z, 0-9, - _ . | Varies by service |
| GCP | a-z, 0-9, - | Must start with letter |

**Safe Universal Set**: `a-z`, `0-9`, `-` (lowercase letters, numbers, hyphens)

## Universal Naming Pattern

### Standard Format

```
{organization}-{product}-{environment}-{region}-{resource-type}-{instance}
```

**Components**:

1. **organization**: Company/division abbreviation (2-4 chars)
2. **product**: Product/application name (3-10 chars)
3. **environment**: Environment type (3-4 chars)
4. **region**: Geographic region abbreviation (optional, 4-6 chars)
5. **resource-type**: Type of resource (2-10 chars)
6. **instance**: Unique identifier or sequence (01, 02, api, web)

### Examples

```
# Full format
acme-ecomm-prod-useast1-eks-cluster-01
acme-ecomm-dev-uswest2-rds-postgres-primary

# Without region (global resources)
acme-ecomm-prod-s3-logs
acme-ecomm-staging-cloudfront-cdn

# Simplified (small orgs)
ecomm-prod-api-server-01
ecomm-dev-db-postgres
```

### Component Specifications

#### Organization Codes

| Organization | Code | Example |
|--------------|------|---------|
| Acme Corp | `acme` | acme-myapp-prod |
| Company Engineering | `eng` | eng-platform-dev |
| Finance Division | `fin` | fin-reporting-prod |
| Shared Services | `shared` | shared-monitoring-prod |

#### Environment Codes

| Environment | Code | Usage |
|-------------|------|-------|
| Development | `dev` | Developer workloads |
| Testing | `test` | QA/testing |
| Staging | `stage` or `staging` | Pre-production |
| Production | `prod` | Live production |
| UAT | `uat` | User acceptance testing |
| Sandbox | `sbx` or `sandbox` | Experimentation |
| DR | `dr` | Disaster recovery |

#### Region Codes

**AWS Regions**:

| AWS Region | Code | Alternative |
|------------|------|-------------|
| us-east-1 | `use1` | `useast1` |
| us-west-2 | `usw2` | `uswest2` |
| eu-west-1 | `euw1` | `euwest1` |
| ap-southeast-1 | `apse1` | `apsouth1` |

**Azure Regions**:

| Azure Region | Code |
|--------------|------|
| East US | `eus` |
| West US 2 | `wus2` |
| West Europe | `weu` |
| Southeast Asia | `sea` |

**GCP Regions**:

| GCP Region | Code |
|------------|------|
| us-east1 | `use1` |
| us-central1 | `usc1` |
| europe-west1 | `euw1` |
| asia-southeast1 | `ase1` |

## AWS Naming Conventions

### Resource-Specific Patterns

#### EC2 Instances

**Format**: `{org}-{product}-{env}-{role}-{az}-{instance}`

```
acme-webapp-prod-api-1a-01
acme-webapp-prod-web-1b-02
acme-webapp-dev-worker-1a-01
```

**Tags** (additional context):
```json
{
  "Name": "acme-webapp-prod-api-1a-01",
  "Environment": "prod",
  "Application": "webapp",
  "Role": "api-server",
  "ManagedBy": "terraform",
  "CostCenter": "engineering",
  "Owner": "platform-team@acme.com"
}
```

#### S3 Buckets

**Format**: `{org}-{product}-{env}-{purpose}-{region}`

**Constraints**:
- 3-63 characters
- Lowercase letters, numbers, hyphens, periods
- Globally unique
- DNS-compliant

```
acme-webapp-prod-logs-us-east-1
acme-webapp-prod-assets-global
acme-data-prod-backup-us-west-2
acme-terraform-prod-state-us-east-1

# With GUID for uniqueness
acme-webapp-prod-uploads-a1b2c3d4
```

#### RDS Instances

**Format**: `{org}-{product}-{env}-{engine}-{role}`

```
acme-webapp-prod-postgres-primary
acme-webapp-prod-postgres-replica-01
acme-analytics-dev-mysql-main
```

#### VPCs

**Format**: `{org}-{product}-{env}-vpc`

```
acme-webapp-prod-vpc
acme-shared-services-vpc
acme-webapp-dev-vpc
```

#### Subnets

**Format**: `{org}-{product}-{env}-{visibility}-{az}-subnet`

```
acme-webapp-prod-public-1a-subnet
acme-webapp-prod-private-1b-subnet
acme-webapp-prod-db-1c-subnet
```

#### Security Groups

**Format**: `{org}-{product}-{env}-{purpose}-sg`

```
acme-webapp-prod-alb-sg
acme-webapp-prod-app-sg
acme-webapp-prod-db-sg
acme-webapp-prod-egress-sg
```

#### Load Balancers

**Format**: `{org}-{product}-{env}-{type}-lb`

```
acme-webapp-prod-public-alb
acme-webapp-prod-internal-nlb
acme-api-dev-app-alb
```

#### EKS Clusters

**Format**: `{org}-{product}-{env}-eks`

```
acme-webapp-prod-eks
acme-platform-staging-eks
acme-ml-dev-eks
```

#### Lambda Functions

**Format**: `{org}-{product}-{env}-{function-name}`

```
acme-webapp-prod-image-processor
acme-api-prod-auth-handler
acme-etl-prod-data-transformer
```

#### DynamoDB Tables

**Format**: `{org}-{product}-{env}-{table-name}`

```
acme-webapp-prod-users
acme-webapp-prod-sessions
acme-analytics-prod-events
```

#### IAM Roles

**Format**: `{org}-{product}-{env}-{service}-role`

```
acme-webapp-prod-ec2-role
acme-webapp-prod-lambda-role
acme-eks-prod-cluster-role
acme-eks-prod-node-role
```

#### CloudWatch Log Groups

**Format**: `/aws/{service}/{org}/{product}/{env}/{component}`

```
/aws/lambda/acme/webapp/prod/image-processor
/aws/eks/acme/webapp/prod/cluster
/aws/ec2/acme/webapp/prod/api-server
```

#### SNS Topics

**Format**: `{org}-{product}-{env}-{event-type}-topic`

```
acme-webapp-prod-user-signup-topic
acme-orders-prod-order-created-topic
acme-alerts-prod-critical-topic
```

#### SQS Queues

**Format**: `{org}-{product}-{env}-{queue-purpose}-queue`

```
acme-webapp-prod-image-processing-queue
acme-orders-prod-order-fulfillment-queue
acme-webapp-prod-dlq (dead letter queue)
```

### AWS Resource Length Limits

| Resource | Max Length | Case | Notes |
|----------|------------|------|-------|
| S3 Bucket | 63 | lowercase | Globally unique |
| EC2 Instance | 255 | any | Tag "Name" |
| RDS Instance | 63 | lowercase | DB identifier |
| Lambda Function | 64 | any | Function name |
| IAM Role | 64 | any | Role name |
| Security Group | 255 | any | Group name |
| DynamoDB Table | 255 | any | Table name |
| EKS Cluster | 100 | any | Cluster name |

## Azure Naming Conventions

### Resource-Specific Patterns

#### Virtual Machines

**Format**: `{org}-{product}-{env}-{role}-vm-{instance}`

```
acme-webapp-prod-api-vm-01
acme-webapp-prod-web-vm-02
acme-db-prod-postgres-vm-01
```

#### Resource Groups

**Format**: `rg-{org}-{product}-{env}-{region}`

```
rg-acme-webapp-prod-eastus
rg-acme-shared-services-westus2
rg-acme-networking-prod-eastus
```

#### Storage Accounts

**Format**: `st{org}{product}{env}{purpose}{uniqueid}`

**Constraints**:
- 3-24 characters
- Lowercase letters and numbers only
- Globally unique

```
stacmewebappprodlogs01
stacmewebappprodassets
stacmedataprodbackup01

# Alternative with minimal org code
stacmewapprdlog01  # acme webapp prod logs
```

#### Virtual Networks

**Format**: `vnet-{org}-{product}-{env}-{region}`

```
vnet-acme-webapp-prod-eastus
vnet-acme-shared-services-westus2
```

#### Subnets

**Format**: `snet-{purpose}-{env}-{region}`

```
snet-app-prod-eastus
snet-db-prod-eastus
snet-gateway-prod-eastus
```

#### Network Security Groups

**Format**: `nsg-{purpose}-{env}-{region}`

```
nsg-app-prod-eastus
nsg-db-prod-eastus
nsg-web-prod-eastus
```

#### Application Gateways

**Format**: `agw-{org}-{product}-{env}-{region}`

```
agw-acme-webapp-prod-eastus
agw-acme-api-staging-westus2
```

#### AKS Clusters

**Format**: `aks-{org}-{product}-{env}-{region}`

```
aks-acme-webapp-prod-eastus
aks-acme-platform-dev-westus2
```

#### Azure Functions

**Format**: `func-{org}-{product}-{env}-{purpose}`

```
func-acme-webapp-prod-imageprocessor
func-acme-api-prod-authhandler
```

#### SQL Databases

**Format**: `sql-{org}-{product}-{env}-{database}`

```
sql-acme-webapp-prod-users
sql-acme-analytics-prod-events
```

#### Key Vaults

**Format**: `kv-{org}-{product}-{env}-{region}`

**Constraints**: 3-24 characters, globally unique

```
kv-acme-webapp-prod-eus
kv-acme-shared-prod-wus2
```

#### Managed Identities

**Format**: `id-{purpose}-{env}`

```
id-webapp-prod
id-aks-cluster-prod
id-funcapp-staging
```

### Azure Resource Length Limits

| Resource | Max Length | Case | Notes |
|----------|------------|------|-------|
| Resource Group | 90 | any | Alphanumeric, underscore, hyphen, period |
| VM | 64 (Win), 15 (Linux) | any | |
| Storage Account | 24 | lowercase | Letters and numbers only |
| Virtual Network | 64 | any | |
| Key Vault | 24 | any | Globally unique |
| AKS Cluster | 63 | lowercase | DNS-1035 label |

## GCP Naming Conventions

### Resource-Specific Patterns

#### Compute Instances

**Format**: `{org}-{product}-{env}-{role}-{zone}-{instance}`

```
acme-webapp-prod-api-us-central1-a-01
acme-webapp-prod-web-us-central1-b-02
acme-db-prod-postgres-us-central1-a-01
```

#### VPC Networks

**Format**: `{org}-{product}-{env}-vpc`

```
acme-webapp-prod-vpc
acme-shared-services-vpc
acme-webapp-dev-vpc
```

#### Subnets

**Format**: `{org}-{product}-{env}-{purpose}-{region}-subnet`

```
acme-webapp-prod-app-us-central1-subnet
acme-webapp-prod-db-us-central1-subnet
acme-webapp-prod-public-us-east1-subnet
```

#### Cloud Storage Buckets

**Format**: `{org}-{product}-{env}-{purpose}-{region}`

**Constraints**: Globally unique, lowercase, hyphens allowed

```
acme-webapp-prod-logs-us-central1
acme-webapp-prod-assets-multi-region
acme-terraform-prod-state-us-central1
```

#### GKE Clusters

**Format**: `{org}-{product}-{env}-gke`

```
acme-webapp-prod-gke
acme-platform-staging-gke
acme-ml-dev-gke
```

#### Cloud SQL Instances

**Format**: `{org}-{product}-{env}-{engine}-{role}`

```
acme-webapp-prod-postgres-primary
acme-webapp-prod-mysql-replica-01
acme-analytics-dev-postgres-main
```

#### Cloud Functions

**Format**: `{org}-{product}-{env}-{function-name}`

```
acme-webapp-prod-image-processor
acme-api-prod-auth-handler
acme-etl-prod-data-transformer
```

#### Cloud Run Services

**Format**: `{org}-{product}-{env}-{service-name}`

```
acme-webapp-prod-api-service
acme-ml-prod-inference-service
acme-worker-prod-queue-processor
```

#### Firewall Rules

**Format**: `{org}-{product}-{env}-{direction}-{purpose}-fw`

```
acme-webapp-prod-ingress-https-fw
acme-webapp-prod-egress-db-fw
acme-shared-allow-ssh-fw
```

#### Service Accounts

**Format**: `{product}-{env}-{purpose}@{project-id}.iam.gserviceaccount.com`

```
webapp-prod-gke@acme-prod-123456.iam.gserviceaccount.com
cloudrun-prod-api@acme-prod-123456.iam.gserviceaccount.com
```

#### BigQuery Datasets

**Format**: `{org}_{product}_{env}_{dataset_name}`

```
acme_webapp_prod_analytics
acme_data_prod_warehouse
acme_ml_dev_training_data
```

### GCP Resource Length Limits

| Resource | Max Length | Case | Notes |
|----------|------------|------|-------|
| Instance | 63 | lowercase | RFC 1035 label |
| VPC Network | 63 | lowercase | RFC 1035 label |
| Storage Bucket | 63 | lowercase | Globally unique |
| GKE Cluster | 40 | lowercase | |
| Cloud Function | 63 | lowercase | |
| Service Account | 30 | lowercase | Account name only |

## Multi-Cloud Standards

### Unified Naming for Multi-Cloud Deployments

```
# Same resource across clouds
acme-webapp-prod-k8s-cluster      # Logical name
  ├─ AWS: acme-webapp-prod-eks
  ├─ Azure: aks-acme-webapp-prod-eastus
  └─ GCP: acme-webapp-prod-gke

acme-webapp-prod-object-storage   # Logical name
  ├─ AWS: acme-webapp-prod-assets-us-east-1 (S3)
  ├─ Azure: stacmewebapprodassets (Storage Account)
  └─ GCP: acme-webapp-prod-assets-us-central1 (Cloud Storage)
```

### Cross-Cloud Tagging Standard

Use consistent tags across all clouds:

```json
{
  "Environment": "prod",
  "Application": "webapp",
  "Owner": "platform-team@acme.com",
  "CostCenter": "engineering",
  "DataClassification": "confidential",
  "Compliance": "pci-dss",
  "ManagedBy": "terraform",
  "BackupPolicy": "daily",
  "DisasterRecovery": "critical",
  "SLA": "99.99"
}
```

## Tagging Standards

### Required Tags (All Resources)

| Tag Key | Description | Example Values |
|---------|-------------|----------------|
| Name | Resource name | acme-webapp-prod-api-01 |
| Environment | Deployment environment | dev, staging, prod |
| Application | Application/product name | webapp, api, analytics |
| Owner | Team/email responsible | platform-team@acme.com |
| CostCenter | Billing allocation | engineering, marketing |
| ManagedBy | How resource is managed | terraform, cloudformation, manual |

### Optional Tags (Recommended)

| Tag Key | Description | Example Values |
|---------|-------------|----------------|
| Project | Project or initiative | mobile-app-v2, migration-2024 |
| DataClassification | Data sensitivity | public, internal, confidential, restricted |
| Compliance | Compliance requirements | pci-dss, hipaa, sox, gdpr |
| BackupPolicy | Backup requirements | none, daily, hourly |
| DisasterRecovery | DR tier | critical, high, medium, low |
| MaintenanceWindow | Allowed maintenance time | sun-02:00-04:00-utc |
| SLA | Availability target | 99.99, 99.95, 99.9 |
| EndDate | Resource expiration | 2024-12-31 (for temporary) |
| Version | Application version | v1.2.3, 2024.03 |
| Repository | Source code location | github.com/acme/webapp |

### AWS-Specific Tags

```json
{
  "aws:cloudformation:stack-name": "webapp-prod-stack",
  "aws:cloudformation:logical-id": "WebAppInstance",
  "aws:autoscaling:groupName": "webapp-prod-asg"
}
```

### Azure-Specific Tags

```json
{
  "created-by": "john.doe@acme.com",
  "deployment-id": "12345",
  "resource-type": "virtual-machine"
}
```

### GCP-Specific Labels

```json
{
  "created-by": "john_doe",
  "deployment-id": "12345",
  "goog-dm-deployment": "webapp-prod"
}
```

### Tag Naming Conventions

1. **PascalCase for Keys**: `CostCenter`, `DataClassification`, `BackupPolicy`
2. **lowercase-with-hyphens for values**: `pci-dss`, `platform-team`, `us-east-1`
3. **No spaces in values**: Use hyphens or underscores
4. **Date format**: ISO 8601 (`2024-03-15` or `2024-03-15T10:30:00Z`)
5. **Email format**: Standard email addresses

### Tag Automation

**Terraform Example**:

```hcl
locals {
  common_tags = {
    Environment        = var.environment
    Application        = var.application_name
    Owner             = var.owner_email
    CostCenter        = var.cost_center
    ManagedBy         = "Terraform"
    Repository        = "github.com/acme/infrastructure"
    TerraformWorkspace = terraform.workspace
  }
}

resource "aws_instance" "app" {
  ami           = data.aws_ami.app.id
  instance_type = var.instance_type

  tags = merge(
    local.common_tags,
    {
      Name = "acme-webapp-prod-api-01"
      Role = "api-server"
    }
  )
}
```

## Naming Registry

### Maintaining a Naming Registry

Create a central registry of naming patterns and abbreviations:

```yaml
# naming-registry.yaml
organization:
  code: acme
  full_name: Acme Corporation

products:
  webapp:
    full_name: E-Commerce Web Application
    abbreviation: webapp
    team: platform-team@acme.com

  analytics:
    full_name: Analytics Platform
    abbreviation: analytics
    team: data-team@acme.com

environments:
  dev:
    full_name: Development
    suffix: dev
  prod:
    full_name: Production
    suffix: prod

regions:
  aws:
    us-east-1:
      code: use1
      backup_region: us-west-2
    us-west-2:
      code: usw2
      backup_region: us-east-1

resource_types:
  ec2:
    pattern: "{org}-{product}-{env}-{role}-{az}-{instance}"
    example: "acme-webapp-prod-api-1a-01"

  s3:
    pattern: "{org}-{product}-{env}-{purpose}-{region}"
    example: "acme-webapp-prod-logs-us-east-1"
    constraints:
      max_length: 63
      case: lowercase
      globally_unique: true
```

### Validation Script Example

```python
# validate_naming.py
import re

PATTERNS = {
    'ec2': r'^[a-z0-9]+-[a-z0-9]+-[a-z0-9]+-[a-z0-9]+-[0-9][a-z]-[0-9]{2}$',
    's3': r'^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$',
    'rds': r'^[a-z0-9]+-[a-z0-9]+-[a-z0-9]+-[a-z0-9]+-(primary|replica-[0-9]{2})$',
}

def validate_name(resource_type, name):
    if resource_type not in PATTERNS:
        return False, f"Unknown resource type: {resource_type}"

    if not re.match(PATTERNS[resource_type], name):
        return False, f"Name '{name}' doesn't match pattern for {resource_type}"

    return True, "Valid"

# Usage
is_valid, message = validate_name('ec2', 'acme-webapp-prod-api-1a-01')
print(f"Validation: {message}")
```

## Anti-Patterns

### Don't: Use Ambiguous Abbreviations

```
❌ acme-wp-p-api-01     # What is 'wp'? WordPress? WebApp?
❌ acme-app1-env1-srv1  # Non-descriptive

✅ acme-webapp-prod-api-01
✅ acme-ecommerce-staging-api-server-01
```

### Don't: Include Redundant Information

```
❌ acme-webapp-prod-ec2-instance-server
❌ acme-webapp-prod-s3-bucket-storage

✅ acme-webapp-prod-api-01 (EC2)
✅ acme-webapp-prod-logs (S3)
```

### Don't: Use Special Characters Unsupported by Platform

```
❌ acme_webapp#prod@api  # @ and # not allowed
❌ acme/webapp/prod/api  # / may cause issues

✅ acme-webapp-prod-api
```

### Don't: Hard-code Environment in Code

```
❌ Resource name: "production-api-server"
   Terraform var: environment = "staging"  # Mismatch!

✅ Use variables consistently
   "${var.organization}-${var.product}-${var.environment}-api-server"
```

### Don't: Exceed Length Limits

```
❌ acme-very-long-application-name-production-east-us-api-server-instance-01
   (Exceeds limits for many resources)

✅ Use abbreviations thoughtfully
   acme-vlapp-prod-eus-api-01
```

### Don't: Use Non-Descriptive Sequences

```
❌ acme-resource-001, acme-resource-002  # What are these?

✅ acme-webapp-prod-api-01, acme-webapp-prod-web-01
```

## References

### Cloud Provider Guidelines

- **AWS Naming Conventions**: https://docs.aws.amazon.com/whitepapers/latest/tagging-best-practices/
- **Azure Naming Rules**: https://docs.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/naming-and-tagging
- **GCP Naming Conventions**: https://cloud.google.com/architecture/best-practices-vpc-design#naming

### Standards and Frameworks

- **Microsoft Cloud Adoption Framework**: https://docs.microsoft.com/azure/cloud-adoption-framework/
- **AWS Well-Architected**: https://aws.amazon.com/architecture/well-architected/
- **Google Cloud Architecture Framework**: https://cloud.google.com/architecture/framework

### Tools

- **AWS Tag Editor**: https://console.aws.amazon.com/resource-groups/tag-editor
- **Azure Resource Graph**: https://azure.microsoft.com/services/resource-graph/
- **GCP Asset Inventory**: https://cloud.google.com/asset-inventory
- **Terraform Naming**: https://www.terraform.io/docs/language/syntax/configuration.html
- **Cloud Custodian**: https://cloudcustodian.io/ (Policy-as-Code for compliance)

### Enterprise Examples

- **Capital One Cloud Naming**: https://www.capitalone.com/tech/cloud/
- **Netflix Cloud Standards**: https://netflixtechblog.com/
- **Lyft Infrastructure**: https://eng.lyft.com/
