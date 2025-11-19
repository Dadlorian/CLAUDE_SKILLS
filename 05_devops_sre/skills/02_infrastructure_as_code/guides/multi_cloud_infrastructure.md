# Multi-Cloud Infrastructure Guide

## Table of Contents
- [Introduction](#introduction)
- [Multi-Cloud Strategies](#multi-cloud-strategies)
- [AWS Infrastructure](#aws-infrastructure)
- [Azure Infrastructure](#azure-infrastructure)
- [GCP Infrastructure](#gcp-infrastructure)
- [Cross-Cloud Patterns](#cross-cloud-patterns)
- [Networking](#networking)
- [Security](#security)
- [Cost Management](#cost-management)
- [Best Practices](#best-practices)

## Introduction

### What is Multi-Cloud?
Multi-cloud is a strategy that involves using multiple cloud service providers (AWS, Azure, GCP) simultaneously to avoid vendor lock-in, increase redundancy, and optimize costs and capabilities.

### Why Multi-Cloud?
- **Avoid Vendor Lock-in**: Reduce dependency on single provider
- **Best-of-Breed**: Use best services from each provider
- **Geographic Coverage**: Leverage different regions
- **Regulatory Compliance**: Meet data sovereignty requirements
- **High Availability**: Increase resilience across providers
- **Cost Optimization**: Leverage competitive pricing

### Challenges
- **Complexity**: Managing multiple platforms
- **Consistency**: Maintaining uniform policies
- **Networking**: Connecting across clouds
- **Skills**: Team expertise across platforms
- **Tooling**: Unified management tools

## Multi-Cloud Strategies

### 1. Cloud-Agnostic Design
Abstract cloud-specific resources behind interfaces.

```hcl
# versions.tf
terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}
```

### 2. Active-Active Multi-Cloud
Run workloads simultaneously across multiple clouds.

```hcl
# Deploy to AWS
module "aws_infrastructure" {
  source = "./modules/aws"

  environment = var.environment
  region      = var.aws_region
}

# Deploy to Azure
module "azure_infrastructure" {
  source = "./modules/azure"

  environment = var.environment
  location    = var.azure_location
}

# Deploy to GCP
module "gcp_infrastructure" {
  source = "./modules/gcp"

  environment = var.environment
  region      = var.gcp_region
}
```

### 3. Primary-Secondary (DR)
Use one cloud as primary, another for disaster recovery.

```hcl
locals {
  is_primary = var.deployment_type == "primary"
}

# Primary deployment (AWS)
module "primary" {
  count  = local.is_primary ? 1 : 0
  source = "./modules/aws"

  instance_count = 10
  instance_type  = "t3.large"
}

# DR deployment (Azure)
module "disaster_recovery" {
  count  = local.is_primary ? 0 : 1
  source = "./modules/azure"

  instance_count = 3
  instance_size  = "Standard_D2s_v3"
}
```

### 4. Service-Specific Multi-Cloud
Use specific services from each cloud based on strengths.

```hcl
# AWS for compute and storage
module "aws_compute" {
  source = "./modules/aws/compute"
}

# Azure for Active Directory integration
module "azure_identity" {
  source = "./modules/azure/identity"
}

# GCP for BigQuery analytics
module "gcp_analytics" {
  source = "./modules/gcp/bigquery"
}
```

## AWS Infrastructure

### Provider Configuration
```hcl
provider "aws" {
  region = "us-west-2"

  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Cloud       = "AWS"
    }
  }
}

# Multiple regions
provider "aws" {
  alias  = "us_east"
  region = "us-east-1"
}

provider "aws" {
  alias  = "eu_west"
  region = "eu-west-1"
}
```

### VPC and Networking
```hcl
module "aws_vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"

  name = "${var.environment}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-west-2a", "us-west-2b", "us-west-2c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway   = true
  enable_dns_hostnames = true

  tags = var.tags
}
```

### Compute
```hcl
resource "aws_instance" "web" {
  count = var.instance_count

  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.medium"
  subnet_id     = module.aws_vpc.private_subnets[count.index % length(module.aws_vpc.private_subnets)]

  vpc_security_group_ids = [aws_security_group.web.id]

  root_block_device {
    volume_type = "gp3"
    volume_size = 50
    encrypted   = true
  }

  tags = {
    Name = "${var.environment}-web-${count.index}"
  }
}
```

### Storage
```hcl
resource "aws_s3_bucket" "data" {
  bucket = "${var.environment}-${var.project}-data"

  tags = var.tags
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
```

### Database
```hcl
resource "aws_db_instance" "main" {
  identifier = "${var.environment}-db"

  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t3.medium"
  allocated_storage    = 100
  storage_encrypted    = true

  db_name  = var.database_name
  username = var.database_username
  password = var.database_password

  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"

  multi_az               = var.environment == "prod"
  skip_final_snapshot    = var.environment != "prod"

  tags = var.tags
}
```

## Azure Infrastructure

### Provider Configuration
```hcl
provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = true
    }

    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }

  subscription_id = var.azure_subscription_id
  tenant_id       = var.azure_tenant_id
}
```

### Resource Group and Virtual Network
```hcl
resource "azurerm_resource_group" "main" {
  name     = "${var.environment}-rg"
  location = var.azure_location

  tags = var.tags
}

resource "azurerm_virtual_network" "main" {
  name                = "${var.environment}-vnet"
  address_space       = ["10.1.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = var.tags
}

resource "azurerm_subnet" "private" {
  count = 3

  name                 = "${var.environment}-private-subnet-${count.index + 1}"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.1.${count.index}.0/24"]
}

resource "azurerm_subnet" "public" {
  count = 3

  name                 = "${var.environment}-public-subnet-${count.index + 1}"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.1.${count.index + 10}.0/24"]
}
```

### Compute
```hcl
resource "azurerm_linux_virtual_machine" "web" {
  count = var.instance_count

  name                = "${var.environment}-web-${count.index}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"

  admin_username = "azureuser"

  admin_ssh_key {
    username   = "azureuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.web[count.index].id,
  ]

  os_disk {
    name                 = "${var.environment}-web-osdisk-${count.index}"
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
    disk_size_gb         = 50
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }

  tags = var.tags
}

resource "azurerm_network_interface" "web" {
  count = var.instance_count

  name                = "${var.environment}-web-nic-${count.index}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.private[count.index % length(azurerm_subnet.private)].id
    private_ip_address_allocation = "Dynamic"
  }

  tags = var.tags
}
```

### Storage
```hcl
resource "azurerm_storage_account" "data" {
  name                     = "${var.environment}${var.project}data"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  blob_properties {
    versioning_enabled = true

    delete_retention_policy {
      days = 7
    }
  }

  min_tls_version = "TLS1_2"

  tags = var.tags
}

resource "azurerm_storage_container" "data" {
  name                  = "data"
  storage_account_name  = azurerm_storage_account.data.name
  container_access_type = "private"
}
```

### Database
```hcl
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "${var.environment}-postgres"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "15"
  administrator_login    = var.database_username
  administrator_password = var.database_password

  storage_mb = 32768
  sku_name   = "GP_Standard_D2s_v3"

  backup_retention_days        = 7
  geo_redundant_backup_enabled = var.environment == "prod"

  high_availability {
    mode = var.environment == "prod" ? "ZoneRedundant" : "Disabled"
  }

  tags = var.tags
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = var.database_name
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "utf8"
}
```

## GCP Infrastructure

### Provider Configuration
```hcl
provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

provider "google-beta" {
  project = var.gcp_project_id
  region  = var.gcp_region
}
```

### VPC and Networking
```hcl
resource "google_compute_network" "main" {
  name                    = "${var.environment}-vpc"
  auto_create_subnetworks = false
  mtu                     = 1460
}

resource "google_compute_subnetwork" "private" {
  count = 3

  name          = "${var.environment}-private-subnet-${count.index}"
  ip_cidr_range = "10.2.${count.index}.0/24"
  region        = var.gcp_region
  network       = google_compute_network.main.id

  private_ip_google_access = true

  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

resource "google_compute_subnetwork" "public" {
  count = 3

  name          = "${var.environment}-public-subnet-${count.index}"
  ip_cidr_range = "10.2.${count.index + 10}.0/24"
  region        = var.gcp_region
  network       = google_compute_network.main.id
}

resource "google_compute_router" "main" {
  name    = "${var.environment}-router"
  region  = var.gcp_region
  network = google_compute_network.main.id
}

resource "google_compute_router_nat" "main" {
  name   = "${var.environment}-nat"
  router = google_compute_router.main.name
  region = var.gcp_region

  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}
```

### Compute
```hcl
resource "google_compute_instance" "web" {
  count = var.instance_count

  name         = "${var.environment}-web-${count.index}"
  machine_type = "e2-medium"
  zone         = "${var.gcp_region}-a"

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 50
      type  = "pd-balanced"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.private[count.index % length(google_compute_subnetwork.private)].id
  }

  metadata_startup_script = file("${path.module}/startup-script.sh")

  service_account {
    email  = google_service_account.compute.email
    scopes = ["cloud-platform"]
  }

  shielded_instance_config {
    enable_secure_boot          = true
    enable_vtpm                 = true
    enable_integrity_monitoring = true
  }

  labels = var.tags
}

resource "google_service_account" "compute" {
  account_id   = "${var.environment}-compute-sa"
  display_name = "Service Account for Compute Instances"
}
```

### Storage
```hcl
resource "google_storage_bucket" "data" {
  name     = "${var.gcp_project_id}-${var.environment}-data"
  location = var.gcp_region

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.bucket.id
  }

  labels = var.tags
}

resource "google_kms_key_ring" "main" {
  name     = "${var.environment}-keyring"
  location = var.gcp_region
}

resource "google_kms_crypto_key" "bucket" {
  name     = "${var.environment}-bucket-key"
  key_ring = google_kms_key_ring.main.id

  rotation_period = "7776000s" # 90 days

  lifecycle {
    prevent_destroy = true
  }
}
```

### Database
```hcl
resource "google_sql_database_instance" "main" {
  name             = "${var.environment}-postgres"
  database_version = "POSTGRES_15"
  region           = var.gcp_region

  settings {
    tier              = "db-custom-2-8192"
    availability_type = var.environment == "prod" ? "REGIONAL" : "ZONAL"
    disk_type         = "PD_SSD"
    disk_size         = 100
    disk_autoresize   = true

    backup_configuration {
      enabled            = true
      start_time         = "03:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 7
        retention_unit   = "COUNT"
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.main.id
      require_ssl     = true
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
    }

    database_flags {
      name  = "max_connections"
      value = "100"
    }
  }

  deletion_protection = var.environment == "prod"
}

resource "google_sql_database" "main" {
  name     = var.database_name
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "main" {
  name     = var.database_username
  instance = google_sql_database_instance.main.name
  password = var.database_password
}
```

## Cross-Cloud Patterns

### Unified Module Interface
```hcl
# modules/compute/interface.tf
variable "cloud_provider" {
  type = string
  validation {
    condition     = contains(["aws", "azure", "gcp"], var.cloud_provider)
    error_message = "Must be aws, azure, or gcp."
  }
}

variable "instance_count" {
  type = number
}

variable "instance_size" {
  type = string
}

# modules/compute/main.tf
module "aws_compute" {
  count  = var.cloud_provider == "aws" ? 1 : 0
  source = "./aws"

  instance_count = var.instance_count
  instance_type  = var.instance_size
}

module "azure_compute" {
  count  = var.cloud_provider == "azure" ? 1 : 0
  source = "./azure"

  instance_count = var.instance_count
  vm_size        = var.instance_size
}

module "gcp_compute" {
  count  = var.cloud_provider == "gcp" ? 1 : 0
  source = "./gcp"

  instance_count = var.instance_count
  machine_type   = var.instance_size
}
```

### Multi-Cloud Load Balancing
```hcl
# Global load balancer using Cloudflare
resource "cloudflare_load_balancer" "global" {
  zone_id = var.cloudflare_zone_id
  name    = "${var.environment}.example.com"

  default_pool_ids = [
    cloudflare_load_balancer_pool.aws.id,
    cloudflare_load_balancer_pool.azure.id,
    cloudflare_load_balancer_pool.gcp.id,
  ]

  fallback_pool_id = cloudflare_load_balancer_pool.aws.id

  steering_policy = "dynamic_latency"
}

resource "cloudflare_load_balancer_pool" "aws" {
  name = "aws-pool"

  origins {
    name    = "aws-primary"
    address = module.aws_infrastructure.load_balancer_ip
    enabled = true
  }

  monitor = cloudflare_load_balancer_monitor.health.id
}

resource "cloudflare_load_balancer_pool" "azure" {
  name = "azure-pool"

  origins {
    name    = "azure-primary"
    address = module.azure_infrastructure.load_balancer_ip
    enabled = true
  }

  monitor = cloudflare_load_balancer_monitor.health.id
}

resource "cloudflare_load_balancer_pool" "gcp" {
  name = "gcp-pool"

  origins {
    name    = "gcp-primary"
    address = module.gcp_infrastructure.load_balancer_ip
    enabled = true
  }

  monitor = cloudflare_load_balancer_monitor.health.id
}
```

### Multi-Cloud DNS
```hcl
# Route 53 (AWS)
resource "aws_route53_zone" "main" {
  name = "example.com"
}

resource "aws_route53_record" "aws_region" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "aws.example.com"
  type    = "A"
  ttl     = 300
  records = [module.aws_infrastructure.load_balancer_ip]

  geolocation_routing_policy {
    continent = "NA"
  }

  set_identifier = "aws-us"
}

# Azure DNS
resource "azurerm_dns_zone" "main" {
  name                = "example.com"
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_dns_a_record" "azure_region" {
  name                = "azure"
  zone_name           = azurerm_dns_zone.main.name
  resource_group_name = azurerm_resource_group.main.name
  ttl                 = 300
  records             = [module.azure_infrastructure.load_balancer_ip]
}

# Cloud DNS (GCP)
resource "google_dns_managed_zone" "main" {
  name     = "example-com"
  dns_name = "example.com."
}

resource "google_dns_record_set" "gcp_region" {
  name         = "gcp.${google_dns_managed_zone.main.dns_name}"
  managed_zone = google_dns_managed_zone.main.name
  type         = "A"
  ttl          = 300
  rrdatas      = [module.gcp_infrastructure.load_balancer_ip]
}
```

## Networking

### VPN Connectivity
```hcl
# AWS to Azure VPN
module "aws_azure_vpn" {
  source = "./modules/vpn/aws-azure"

  aws_vpc_id        = module.aws_infrastructure.vpc_id
  aws_subnet_id     = module.aws_infrastructure.vpn_subnet_id
  azure_vnet_id     = module.azure_infrastructure.vnet_id
  azure_gateway_id  = module.azure_infrastructure.vpn_gateway_id

  shared_key = var.vpn_shared_key
}

# Azure to GCP VPN
module "azure_gcp_vpn" {
  source = "./modules/vpn/azure-gcp"

  azure_vnet_id       = module.azure_infrastructure.vnet_id
  azure_gateway_id    = module.azure_infrastructure.vpn_gateway_id
  gcp_network_id      = module.gcp_infrastructure.vpc_id
  gcp_gateway_address = module.gcp_infrastructure.vpn_gateway_ip

  shared_key = var.vpn_shared_key
}
```

### Transit Gateway (AWS) Integration
```hcl
resource "aws_ec2_transit_gateway" "main" {
  description = "${var.environment} Transit Gateway"

  default_route_table_association = "enable"
  default_route_table_propagation = "enable"
  dns_support                     = "enable"
  vpn_ecmp_support               = "enable"

  tags = var.tags
}

resource "aws_ec2_transit_gateway_vpc_attachment" "main" {
  subnet_ids         = module.aws_infrastructure.private_subnet_ids
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  vpc_id             = module.aws_infrastructure.vpc_id

  tags = var.tags
}

# Connect to on-premises via VPN
resource "aws_vpn_connection" "onprem" {
  customer_gateway_id = aws_customer_gateway.onprem.id
  transit_gateway_id  = aws_ec2_transit_gateway.main.id
  type                = "ipsec.1"

  static_routes_only = false

  tags = var.tags
}
```

### Azure Virtual WAN
```hcl
resource "azurerm_virtual_wan" "main" {
  name                = "${var.environment}-vwan"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  type = "Standard"

  tags = var.tags
}

resource "azurerm_virtual_hub" "main" {
  name                = "${var.environment}-vhub"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  virtual_wan_id      = azurerm_virtual_wan.main.id
  address_prefix      = "10.100.0.0/24"

  tags = var.tags
}

resource "azurerm_virtual_hub_connection" "main" {
  name                      = "${var.environment}-vhub-conn"
  virtual_hub_id            = azurerm_virtual_hub.main.id
  remote_virtual_network_id = azurerm_virtual_network.main.id
}
```

## Security

### Unified IAM Strategy
```hcl
# AWS IAM
resource "aws_iam_role" "app" {
  name = "${var.environment}-app-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

# Azure Managed Identity
resource "azurerm_user_assigned_identity" "app" {
  name                = "${var.environment}-app-identity"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}

# GCP Service Account
resource "google_service_account" "app" {
  account_id   = "${var.environment}-app-sa"
  display_name = "Application Service Account"
}
```

### Secret Management
```hcl
# AWS Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name = "${var.environment}/database/password"
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = var.database_password
}

# Azure Key Vault
resource "azurerm_key_vault" "main" {
  name                = "${var.environment}-kv"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"
}

resource "azurerm_key_vault_secret" "db_password" {
  name         = "database-password"
  value        = var.database_password
  key_vault_id = azurerm_key_vault.main.id
}

# GCP Secret Manager
resource "google_secret_manager_secret" "db_password" {
  secret_id = "${var.environment}-database-password"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = var.database_password
}
```

### Encryption
```hcl
# AWS KMS
resource "aws_kms_key" "main" {
  description             = "${var.environment} Encryption Key"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

# Azure Key Vault Key
resource "azurerm_key_vault_key" "main" {
  name         = "${var.environment}-encryption-key"
  key_vault_id = azurerm_key_vault.main.id
  key_type     = "RSA"
  key_size     = 2048

  key_opts = [
    "decrypt",
    "encrypt",
    "sign",
    "unwrapKey",
    "verify",
    "wrapKey",
  ]
}

# GCP KMS
resource "google_kms_key_ring" "main" {
  name     = "${var.environment}-keyring"
  location = var.gcp_region
}

resource "google_kms_crypto_key" "main" {
  name     = "${var.environment}-encryption-key"
  key_ring = google_kms_key_ring.main.id

  rotation_period = "7776000s" # 90 days
}
```

## Cost Management

### Budget Alerts
```hcl
# AWS Budget
resource "aws_budgets_budget" "monthly" {
  name              = "${var.environment}-monthly-budget"
  budget_type       = "COST"
  limit_amount      = var.monthly_budget
  limit_unit        = "USD"
  time_period_start = "2024-01-01_00:00"
  time_unit         = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.billing_email]
  }
}

# Azure Cost Management
resource "azurerm_consumption_budget_resource_group" "monthly" {
  name              = "${var.environment}-monthly-budget"
  resource_group_id = azurerm_resource_group.main.id

  amount     = var.monthly_budget
  time_grain = "Monthly"

  time_period {
    start_date = "2024-01-01T00:00:00Z"
  }

  notification {
    enabled   = true
    threshold = 80
    operator  = "GreaterThan"

    contact_emails = [var.billing_email]
  }
}

# GCP Budget Alert
resource "google_billing_budget" "monthly" {
  billing_account = var.gcp_billing_account
  display_name    = "${var.environment}-monthly-budget"

  budget_filter {
    projects = ["projects/${var.gcp_project_id}"]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = var.monthly_budget
    }
  }

  threshold_rules {
    threshold_percent = 0.8
    spend_basis       = "FORECASTED_SPEND"
  }

  all_updates_rule {
    monitoring_notification_channels = [
      google_monitoring_notification_channel.email.id,
    ]
  }
}
```

### Resource Tagging for Cost Allocation
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

# Apply to all resources
resource "aws_instance" "web" {
  # ...
  tags = local.common_tags
}

resource "azurerm_linux_virtual_machine" "web" {
  # ...
  tags = local.common_tags
}

resource "google_compute_instance" "web" {
  # ...
  labels = local.common_tags
}
```

## Best Practices

### 1. Use Cloud-Agnostic Abstractions
```hcl
# Create abstraction layer
module "storage" {
  source = "./modules/storage"

  cloud_provider = var.cloud_provider
  bucket_name    = var.bucket_name
  encryption     = true
  versioning     = true
}
```

### 2. Consistent Naming Conventions
```hcl
locals {
  resource_prefix = "${var.environment}-${var.cloud_provider}-${var.region_code}"

  naming_convention = {
    aws   = "${local.resource_prefix}"
    azure = replace(local.resource_prefix, "-", "")
    gcp   = local.resource_prefix
  }
}
```

### 3. Unified Monitoring
```hcl
# Use Datadog, New Relic, or similar for unified monitoring
resource "datadog_monitor" "multi_cloud_health" {
  name    = "${var.environment} Multi-Cloud Health"
  type    = "metric alert"
  message = "Multi-cloud infrastructure health check"

  query = "avg(last_5m):( avg:aws.ec2.cpu{env:${var.environment}} + avg:azure.vm.percentage_cpu{env:${var.environment}} + avg:gcp.compute.instance.cpu.utilization{env:${var.environment}} ) / 3 > 80"

  monitor_thresholds {
    critical = 80
    warning  = 60
  }
}
```

### 4. Disaster Recovery Planning
```hcl
# Automated backup across clouds
module "backup_to_aws" {
  source = "./modules/backup"

  source_cloud      = "azure"
  source_storage    = module.azure_infrastructure.storage_account
  destination_cloud = "aws"
  destination_bucket = module.aws_infrastructure.backup_bucket
}
```

### 5. Cost Optimization
```hcl
# Use spot/preemptible instances where appropriate
resource "aws_spot_instance_request" "batch" {
  count = var.use_spot ? var.batch_instance_count : 0
  # ...
}

resource "azurerm_linux_virtual_machine" "batch" {
  count    = var.use_spot ? var.batch_instance_count : 0
  priority = "Spot"
  # ...
}

resource "google_compute_instance" "batch" {
  count = var.use_spot ? var.batch_instance_count : 0

  scheduling {
    preemptible       = true
    automatic_restart = false
  }
}
```

### 6. Unified Compliance
```hcl
# Apply consistent security policies
module "compliance" {
  source = "./modules/compliance"

  providers = {
    aws    = aws
    azurerm = azurerm
    google = google
  }

  enable_encryption     = true
  enable_logging        = true
  enable_monitoring     = true
  require_mfa           = true
  data_classification   = "confidential"
}
```

### 7. Documentation
```markdown
# Multi-Cloud Architecture

## Overview
Application deployed across AWS, Azure, and GCP for high availability.

## Cloud Distribution
- **AWS (Primary)**: us-west-2
  - Compute: EC2 instances
  - Storage: S3
  - Database: RDS PostgreSQL

- **Azure (Secondary)**: West US 2
  - Compute: Virtual Machines
  - Storage: Blob Storage
  - Database: PostgreSQL Flexible Server

- **GCP (Analytics)**: us-west1
  - Compute: Compute Engine
  - Storage: Cloud Storage
  - Analytics: BigQuery

## Traffic Routing
Global load balancing via Cloudflare with geo-routing.

## Failover Strategy
Automatic failover with health checks every 30 seconds.
```

### 8. Testing Multi-Cloud Deployments
```bash
# Test script
#!/bin/bash

# Test AWS deployment
cd aws
terraform init
terraform plan
terraform apply -auto-approve

# Test Azure deployment
cd ../azure
terraform init
terraform plan
terraform apply -auto-approve

# Test GCP deployment
cd ../gcp
terraform init
terraform plan
terraform apply -auto-approve

# Verify connectivity between clouds
./test-connectivity.sh
```

### 9. Gradual Migration
```hcl
# Phase 1: AWS only
locals {
  deploy_to_aws   = true
  deploy_to_azure = false
  deploy_to_gcp   = false
}

# Phase 2: Add Azure
locals {
  deploy_to_aws   = true
  deploy_to_azure = true
  deploy_to_gcp   = false
}

# Phase 3: Full multi-cloud
locals {
  deploy_to_aws   = true
  deploy_to_azure = true
  deploy_to_gcp   = true
}
```

### 10. Vendor Relationship Management
- Maintain certifications across all platforms
- Leverage support channels appropriately
- Monitor service health dashboards
- Participate in cloud provider communities
- Stay updated on new services and deprecations
