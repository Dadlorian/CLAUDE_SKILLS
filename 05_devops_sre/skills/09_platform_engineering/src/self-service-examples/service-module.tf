# Self-Service Terraform Module for Services
# This module provisions a complete service with all necessary infrastructure

terraform {
  required_version = ">= 1.0"

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

# Variables
variable "service_name" {
  description = "Name of the service"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.service_name))
    error_message = "Service name must contain only lowercase letters, numbers, and hyphens"
  }
}

variable "team" {
  description = "Team that owns this service"
  type        = string
}

variable "environment" {
  description = "Environment (development, staging, production)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production"
  }
}

variable "runtime" {
  description = "Runtime for the service"
  type        = string
  default     = "node18"

  validation {
    condition     = contains(["node18", "node20", "python311", "python312", "go121", "java17"], var.runtime)
    error_message = "Invalid runtime specified"
  }
}

variable "replicas" {
  description = "Number of replicas"
  type        = number
  default     = 3

  validation {
    condition     = var.replicas >= 1 && var.replicas <= 100
    error_message = "Replicas must be between 1 and 100"
  }
}

variable "cpu" {
  description = "CPU allocation in millicores"
  type        = number
  default     = 500
}

variable "memory" {
  description = "Memory allocation in Mi"
  type        = number
  default     = 512
}

variable "enable_autoscaling" {
  description = "Enable horizontal pod autoscaling"
  type        = bool
  default     = true
}

variable "min_replicas" {
  description = "Minimum replicas for autoscaling"
  type        = number
  default     = 2
}

variable "max_replicas" {
  description = "Maximum replicas for autoscaling"
  type        = number
  default     = 10
}

variable "enable_database" {
  description = "Enable database provisioning"
  type        = bool
  default     = false
}

variable "database_type" {
  description = "Type of database (postgres, mysql, mongodb)"
  type        = string
  default     = "postgres"
}

variable "enable_cache" {
  description = "Enable Redis cache"
  type        = bool
  default     = false
}

variable "enable_monitoring" {
  description = "Enable monitoring and alerting"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

# Local variables
locals {
  common_tags = merge(
    var.tags,
    {
      Service     = var.service_name
      Team        = var.team
      Environment = var.environment
      ManagedBy   = "Terraform"
      Platform    = "IDP"
    }
  )

  namespace = "${var.team}-${var.environment}"
}

# Kubernetes Namespace
resource "kubernetes_namespace" "service" {
  metadata {
    name = local.namespace
    labels = {
      team        = var.team
      environment = var.environment
      managed-by  = "platform"
    }
  }
}

# Kubernetes Deployment
resource "kubernetes_deployment" "service" {
  metadata {
    name      = var.service_name
    namespace = kubernetes_namespace.service.metadata[0].name

    labels = {
      app         = var.service_name
      team        = var.team
      environment = var.environment
    }
  }

  spec {
    replicas = var.replicas

    selector {
      match_labels = {
        app = var.service_name
      }
    }

    template {
      metadata {
        labels = {
          app         = var.service_name
          team        = var.team
          environment = var.environment
          version     = "1.0.0"
        }

        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = "8080"
          "prometheus.io/path"   = "/metrics"
        }
      }

      spec {
        service_account_name = kubernetes_service_account.service.metadata[0].name

        container {
          name  = var.service_name
          image = "registry.company.com/${var.service_name}:latest"

          port {
            container_port = 8080
            name           = "http"
          }

          port {
            container_port = 9090
            name           = "metrics"
          }

          resources {
            requests = {
              cpu    = "${var.cpu}m"
              memory = "${var.memory}Mi"
            }
            limits = {
              cpu    = "${var.cpu * 2}m"
              memory = "${var.memory * 2}Mi"
            }
          }

          env {
            name  = "SERVICE_NAME"
            value = var.service_name
          }

          env {
            name  = "ENVIRONMENT"
            value = var.environment
          }

          env {
            name  = "TEAM"
            value = var.team
          }

          dynamic "env" {
            for_each = var.enable_database ? [1] : []
            content {
              name  = "DATABASE_URL"
              value_from {
                secret_key_ref {
                  name = kubernetes_secret.database[0].metadata[0].name
                  key  = "url"
                }
              }
            }
          }

          dynamic "env" {
            for_each = var.enable_cache ? [1] : []
            content {
              name  = "REDIS_URL"
              value_from {
                secret_key_ref {
                  name = kubernetes_secret.cache[0].metadata[0].name
                  key  = "url"
                }
              }
            }
          }

          liveness_probe {
            http_get {
              path = "/health/live"
              port = 8080
            }
            initial_delay_seconds = 30
            period_seconds        = 10
            timeout_seconds       = 5
            failure_threshold     = 3
          }

          readiness_probe {
            http_get {
              path = "/health/ready"
              port = 8080
            }
            initial_delay_seconds = 10
            period_seconds        = 5
            timeout_seconds       = 3
            failure_threshold     = 3
          }
        }
      }
    }
  }
}

# Kubernetes Service
resource "kubernetes_service" "service" {
  metadata {
    name      = var.service_name
    namespace = kubernetes_namespace.service.metadata[0].name

    labels = {
      app  = var.service_name
      team = var.team
    }
  }

  spec {
    selector = {
      app = var.service_name
    }

    port {
      name        = "http"
      port        = 80
      target_port = 8080
      protocol    = "TCP"
    }

    port {
      name        = "metrics"
      port        = 9090
      target_port = 9090
      protocol    = "TCP"
    }

    type = "ClusterIP"
  }
}

# Kubernetes Service Account
resource "kubernetes_service_account" "service" {
  metadata {
    name      = var.service_name
    namespace = kubernetes_namespace.service.metadata[0].name

    annotations = {
      "eks.amazonaws.com/role-arn" = aws_iam_role.service.arn
    }
  }
}

# Kubernetes Ingress
resource "kubernetes_ingress_v1" "service" {
  metadata {
    name      = var.service_name
    namespace = kubernetes_namespace.service.metadata[0].name

    annotations = {
      "kubernetes.io/ingress.class"                = "nginx"
      "cert-manager.io/cluster-issuer"            = "letsencrypt-prod"
      "nginx.ingress.kubernetes.io/ssl-redirect"   = "true"
      "nginx.ingress.kubernetes.io/rate-limit"     = "100"
    }
  }

  spec {
    tls {
      hosts = ["${var.service_name}.${var.environment}.company.com"]
      secret_name = "${var.service_name}-tls"
    }

    rule {
      host = "${var.service_name}.${var.environment}.company.com"

      http {
        path {
          path      = "/"
          path_type = "Prefix"

          backend {
            service {
              name = kubernetes_service.service.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }
}

# Horizontal Pod Autoscaler
resource "kubernetes_horizontal_pod_autoscaler_v2" "service" {
  count = var.enable_autoscaling ? 1 : 0

  metadata {
    name      = var.service_name
    namespace = kubernetes_namespace.service.metadata[0].name
  }

  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.service.metadata[0].name
    }

    min_replicas = var.min_replicas
    max_replicas = var.max_replicas

    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 70
        }
      }
    }

    metric {
      type = "Resource"
      resource {
        name = "memory"
        target {
          type                = "Utilization"
          average_utilization = 80
        }
      }
    }
  }
}

# AWS IAM Role for Service Account
resource "aws_iam_role" "service" {
  name = "${var.service_name}-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/${data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer}"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer}:sub" = "system:serviceaccount:${local.namespace}:${var.service_name}"
          }
        }
      }
    ]
  })

  tags = local.common_tags
}

# RDS Database (if enabled)
resource "aws_db_instance" "database" {
  count = var.enable_database ? 1 : 0

  identifier = "${var.service_name}-${var.environment}"

  engine         = var.database_type == "postgres" ? "postgres" : "mysql"
  engine_version = var.database_type == "postgres" ? "15.3" : "8.0"
  instance_class = var.environment == "production" ? "db.t3.medium" : "db.t3.small"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = true

  db_name  = replace(var.service_name, "-", "_")
  username = "admin"
  password = random_password.database[0].result

  multi_az               = var.environment == "production"
  backup_retention_period = 7
  skip_final_snapshot    = var.environment != "production"
  deletion_protection    = var.environment == "production"

  vpc_security_group_ids = [aws_security_group.database[0].id]
  db_subnet_group_name   = aws_db_subnet_group.database[0].name

  tags = local.common_tags
}

resource "random_password" "database" {
  count = var.enable_database ? 1 : 0

  length  = 32
  special = true
}

resource "aws_security_group" "database" {
  count = var.enable_database ? 1 : 0

  name        = "${var.service_name}-${var.environment}-db"
  description = "Security group for ${var.service_name} database"
  vpc_id      = data.aws_vpc.main.id

  ingress {
    from_port   = var.database_type == "postgres" ? 5432 : 3306
    to_port     = var.database_type == "postgres" ? 5432 : 3306
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.main.cidr_block]
  }

  tags = local.common_tags
}

resource "aws_db_subnet_group" "database" {
  count = var.enable_database ? 1 : 0

  name       = "${var.service_name}-${var.environment}"
  subnet_ids = data.aws_subnets.private.ids

  tags = local.common_tags
}

# Kubernetes Secret for Database
resource "kubernetes_secret" "database" {
  count = var.enable_database ? 1 : 0

  metadata {
    name      = "${var.service_name}-database"
    namespace = kubernetes_namespace.service.metadata[0].name
  }

  data = {
    url      = "postgresql://${aws_db_instance.database[0].username}:${random_password.database[0].result}@${aws_db_instance.database[0].endpoint}/${aws_db_instance.database[0].db_name}"
    host     = aws_db_instance.database[0].address
    port     = aws_db_instance.database[0].port
    username = aws_db_instance.database[0].username
    password = random_password.database[0].result
    database = aws_db_instance.database[0].db_name
  }
}

# ElastiCache Redis (if enabled)
resource "aws_elasticache_cluster" "cache" {
  count = var.enable_cache ? 1 : 0

  cluster_id         = "${var.service_name}-${var.environment}"
  engine             = "redis"
  engine_version     = "7.0"
  node_type          = var.environment == "production" ? "cache.t3.medium" : "cache.t3.micro"
  num_cache_nodes    = 1
  parameter_group_name = "default.redis7"

  subnet_group_name    = aws_elasticache_subnet_group.cache[0].name
  security_group_ids   = [aws_security_group.cache[0].id]

  tags = local.common_tags
}

resource "aws_security_group" "cache" {
  count = var.enable_cache ? 1 : 0

  name        = "${var.service_name}-${var.environment}-cache"
  description = "Security group for ${var.service_name} cache"
  vpc_id      = data.aws_vpc.main.id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.main.cidr_block]
  }

  tags = local.common_tags
}

resource "aws_elasticache_subnet_group" "cache" {
  count = var.enable_cache ? 1 : 0

  name       = "${var.service_name}-${var.environment}"
  subnet_ids = data.aws_subnets.private.ids
}

# Kubernetes Secret for Cache
resource "kubernetes_secret" "cache" {
  count = var.enable_cache ? 1 : 0

  metadata {
    name      = "${var.service_name}-cache"
    namespace = kubernetes_namespace.service.metadata[0].name
  }

  data = {
    url  = "redis://${aws_elasticache_cluster.cache[0].cache_nodes[0].address}:${aws_elasticache_cluster.cache[0].cache_nodes[0].port}"
    host = aws_elasticache_cluster.cache[0].cache_nodes[0].address
    port = aws_elasticache_cluster.cache[0].cache_nodes[0].port
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "service" {
  name              = "/aws/platform/${var.service_name}/${var.environment}"
  retention_in_days = var.environment == "production" ? 30 : 7

  tags = local.common_tags
}

# Data Sources
data "aws_caller_identity" "current" {}
data "aws_eks_cluster" "cluster" {
  name = "platform-${var.environment}"
}
data "aws_vpc" "main" {
  tags = {
    Name = "platform-${var.environment}"
  }
}
data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }
  tags = {
    Type = "private"
  }
}

# Outputs
output "service_url" {
  description = "Service URL"
  value       = "https://${var.service_name}.${var.environment}.company.com"
}

output "namespace" {
  description = "Kubernetes namespace"
  value       = kubernetes_namespace.service.metadata[0].name
}

output "service_account" {
  description = "Kubernetes service account"
  value       = kubernetes_service_account.service.metadata[0].name
}

output "database_endpoint" {
  description = "Database endpoint"
  value       = var.enable_database ? aws_db_instance.database[0].endpoint : null
}

output "cache_endpoint" {
  description = "Cache endpoint"
  value       = var.enable_cache ? "${aws_elasticache_cluster.cache[0].cache_nodes[0].address}:${aws_elasticache_cluster.cache[0].cache_nodes[0].port}" : null
}

output "iam_role_arn" {
  description = "IAM role ARN for service account"
  value       = aws_iam_role.service.arn
}
