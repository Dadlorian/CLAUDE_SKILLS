# Self-Service Infrastructure Examples

This directory contains Terraform modules and examples for self-service infrastructure provisioning in the internal developer platform.

## Overview

These modules enable developers to provision infrastructure through simple, declarative configuration without needing deep infrastructure knowledge.

## Modules

### Service Module

Complete service provisioning with:
- Kubernetes deployment
- Auto-scaling
- Database (optional)
- Redis cache (optional)
- Monitoring and logging
- IAM roles and permissions
- Ingress/routing

## Usage Examples

### Basic Service

```hcl
module "my_service" {
  source = "git::https://github.com/company/terraform-modules.git//service"

  service_name = "user-api"
  team         = "identity-team"
  environment  = "production"
  runtime      = "node18"
}
```

### Service with Database

```hcl
module "payment_service" {
  source = "git::https://github.com/company/terraform-modules.git//service"

  service_name = "payment-api"
  team         = "payments-team"
  environment  = "production"
  runtime      = "go121"

  # Resource configuration
  replicas = 5
  cpu      = 1000
  memory   = 2048

  # Auto-scaling
  enable_autoscaling = true
  min_replicas       = 3
  max_replicas       = 20

  # Database
  enable_database = true
  database_type   = "postgres"

  # Cache
  enable_cache = true
}
```

### Complete Example

```hcl
# main.tf
terraform {
  required_version = ">= 1.0"

  backend "s3" {
    bucket = "company-terraform-state"
    key    = "services/my-service/terraform.tfstate"
    region = "us-east-1"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.region
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

# Service module
module "my_service" {
  source = "git::https://github.com/company/terraform-modules.git//service"

  service_name = var.service_name
  team         = var.team
  environment  = var.environment
  runtime      = var.runtime

  replicas = var.replicas
  cpu      = var.cpu
  memory   = var.memory

  enable_autoscaling = var.enable_autoscaling
  min_replicas       = var.min_replicas
  max_replicas       = var.max_replicas

  enable_database = var.enable_database
  database_type   = var.database_type

  enable_cache = var.enable_cache

  tags = {
    Project     = "my-project"
    CostCenter  = "engineering"
  }
}

# Variables
variable "region" {
  default = "us-east-1"
}

variable "service_name" {
  description = "Name of the service"
  type        = string
}

variable "team" {
  description = "Team that owns this service"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
  default     = "production"
}

variable "runtime" {
  description = "Runtime"
  type        = string
  default     = "node18"
}

variable "replicas" {
  description = "Number of replicas"
  type        = number
  default     = 3
}

variable "cpu" {
  description = "CPU in millicores"
  type        = number
  default     = 500
}

variable "memory" {
  description = "Memory in Mi"
  type        = number
  default     = 512
}

variable "enable_autoscaling" {
  description = "Enable autoscaling"
  type        = bool
  default     = true
}

variable "min_replicas" {
  type    = number
  default = 2
}

variable "max_replicas" {
  type    = number
  default = 10
}

variable "enable_database" {
  description = "Enable database"
  type        = bool
  default     = false
}

variable "database_type" {
  description = "Database type"
  type        = string
  default     = "postgres"
}

variable "enable_cache" {
  description = "Enable cache"
  type        = bool
  default     = false
}

# Outputs
output "service_url" {
  value = module.my_service.service_url
}

output "database_endpoint" {
  value     = module.my_service.database_endpoint
  sensitive = true
}

output "namespace" {
  value = module.my_service.namespace
}
```

### Variable File (terraform.tfvars)

```hcl
# terraform.tfvars
service_name = "user-authentication-api"
team         = "identity-team"
environment  = "production"
runtime      = "node20"

# Resources
replicas = 5
cpu      = 1000
memory   = 2048

# Autoscaling
enable_autoscaling = true
min_replicas       = 3
max_replicas       = 20

# Database
enable_database = true
database_type   = "postgres"

# Cache
enable_cache = true
```

## Deployment Process

### 1. Initialize Terraform

```bash
terraform init
```

### 2. Plan Changes

```bash
terraform plan -out=tfplan
```

### 3. Apply Changes

```bash
terraform apply tfplan
```

### 4. Verify Deployment

```bash
# Check service status
kubectl get deployment -n <namespace>

# Check service URL
curl https://<service-name>.<environment>.company.com/health
```

## Module Features

### Built-in Best Practices

- **Security**: Encrypted databases, secrets management, IAM least privilege
- **Reliability**: Health checks, auto-scaling, multi-AZ (production)
- **Observability**: Prometheus metrics, structured logging, distributed tracing
- **Cost Optimization**: Right-sized resources, auto-scaling, environment-based configs

### Validation

The module includes validation for:
- Service name format (lowercase, alphanumeric, hyphens)
- Environment values (development, staging, production)
- Resource limits (CPU, memory, replicas)
- Runtime versions

### Default Behaviors

| Setting | Development | Staging | Production |
|---------|-------------|---------|------------|
| Replicas | 1 | 2 | 3 |
| Auto-scaling | Disabled | Enabled | Enabled |
| Database Multi-AZ | No | No | Yes |
| Backup Retention | 1 day | 3 days | 7 days |
| Deletion Protection | No | No | Yes |

## Advanced Usage

### Custom IAM Policies

```hcl
module "my_service" {
  source = "git::https://github.com/company/terraform-modules.git//service"

  # ... other configuration ...
}

# Attach custom policy to service IAM role
resource "aws_iam_role_policy" "custom" {
  name = "custom-policy"
  role = module.my_service.iam_role_name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "arn:aws:s3:::my-bucket/*"
      }
    ]
  })
}
```

### Multiple Environments

```hcl
# environments/production/main.tf
module "service_production" {
  source = "../../modules/service"

  service_name = "user-api"
  team         = "identity-team"
  environment  = "production"

  replicas       = 5
  min_replicas   = 3
  max_replicas   = 20
  enable_database = true
}

# environments/staging/main.tf
module "service_staging" {
  source = "../../modules/service"

  service_name = "user-api"
  team         = "identity-team"
  environment  = "staging"

  replicas       = 2
  min_replicas   = 1
  max_replicas   = 5
  enable_database = true
}
```

### Database Migration

```hcl
# Include database migration job
resource "kubernetes_job" "migration" {
  metadata {
    name      = "${var.service_name}-migration"
    namespace = module.my_service.namespace
  }

  spec {
    template {
      metadata {
        labels = {
          app = "${var.service_name}-migration"
        }
      }

      spec {
        container {
          name  = "migration"
          image = "registry.company.com/${var.service_name}:${var.version}"
          command = ["npm", "run", "migrate"]

          env_from {
            secret_ref {
              name = "${var.service_name}-database"
            }
          }
        }

        restart_policy = "Never"
      }
    }
  }

  depends_on = [module.my_service]
}
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy Infrastructure

on:
  push:
    branches:
      - main
    paths:
      - 'terraform/**'

jobs:
  terraform:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.5.0

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-east-1

      - name: Terraform Init
        run: terraform init
        working-directory: terraform

      - name: Terraform Plan
        run: terraform plan -out=tfplan
        working-directory: terraform

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main'
        run: terraform apply -auto-approve tfplan
        working-directory: terraform
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - plan
  - apply

variables:
  TF_ROOT: terraform
  TF_VERSION: 1.5.0

.terraform:
  image: hashicorp/terraform:${TF_VERSION}
  before_script:
    - cd ${TF_ROOT}
    - terraform init

validate:
  extends: .terraform
  stage: validate
  script:
    - terraform fmt -check
    - terraform validate

plan:
  extends: .terraform
  stage: plan
  script:
    - terraform plan -out=tfplan
  artifacts:
    paths:
      - ${TF_ROOT}/tfplan

apply:
  extends: .terraform
  stage: apply
  script:
    - terraform apply -auto-approve tfplan
  dependencies:
    - plan
  only:
    - main
  when: manual
```

## Troubleshooting

### Common Issues

#### Service Not Starting

```bash
# Check pod status
kubectl get pods -n <namespace>

# View pod logs
kubectl logs -f deployment/<service-name> -n <namespace>

# Describe pod for events
kubectl describe pod <pod-name> -n <namespace>
```

#### Database Connection Issues

```bash
# Verify database secret
kubectl get secret <service-name>-database -n <namespace> -o yaml

# Test database connectivity from pod
kubectl exec -it deployment/<service-name> -n <namespace> -- \
  psql $DATABASE_URL -c "SELECT 1"
```

#### Terraform State Issues

```bash
# Refresh state
terraform refresh

# Import existing resource
terraform import module.my_service.kubernetes_deployment.service <namespace>/<deployment-name>

# Unlock state (if locked)
terraform force-unlock <lock-id>
```

## Best Practices

### 1. Use Version Pinning

```hcl
module "my_service" {
  source = "git::https://github.com/company/terraform-modules.git//service?ref=v1.2.3"
  # ...
}
```

### 2. Separate State Per Environment

```
terraform/
├── environments/
│   ├── production/
│   │   ├── main.tf
│   │   ├── backend.tf      # S3 backend for production
│   │   └── terraform.tfvars
│   └── staging/
│       ├── main.tf
│       ├── backend.tf      # Separate S3 backend for staging
│       └── terraform.tfvars
```

### 3. Use Remote State

```hcl
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "services/${var.service_name}/${var.environment}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

### 4. Tag Everything

```hcl
locals {
  common_tags = {
    Service     = var.service_name
    Team        = var.team
    Environment = var.environment
    ManagedBy   = "Terraform"
    CostCenter  = var.cost_center
    Project     = var.project
  }
}
```

### 5. Use Workspaces for Environments

```bash
# Create workspace
terraform workspace new production

# Switch workspace
terraform workspace select production

# List workspaces
terraform workspace list
```

## Support

- **Documentation**: https://docs.company.com/platform/terraform
- **Slack**: #platform-support
- **Email**: platform-team@company.com
- **Office Hours**: Thursdays 2-3pm

## Contributing

To contribute improvements to these modules:

1. Create a feature branch
2. Make your changes
3. Add tests
4. Submit a pull request
5. Request review from platform team

## Resources

- [Terraform Documentation](https://www.terraform.io/docs)
- [Kubernetes Provider](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs)
- [AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Module Best Practices](https://www.terraform.io/docs/modules/index.html)
