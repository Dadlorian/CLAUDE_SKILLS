# AWS PrivateLink Configuration

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

# VPC Endpoint Service (Provider)
resource "aws_vpc_endpoint_service" "api" {
  acceptance_required = true

  tags = {
    Name = "api-endpoint-service"
  }
}

# Network Load Balancer for VPC Endpoint Service
resource "aws_lb" "endpoint_nlb" {
  name               = "endpoint-nlb"
  internal           = true
  load_balancer_type = "network"
  subnets            = var.subnet_ids

  tags = {
    Name = "endpoint-nlb"
  }
}

resource "aws_lb_target_group" "endpoint_tg" {
  name     = "endpoint-tg"
  port     = 443
  protocol = "TCP"
  vpc_id   = var.vpc_id

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    protocol            = "TCP"
    port                = "443"
  }
}

resource "aws_lb_listener" "endpoint" {
  load_balancer_arn = aws_lb.endpoint_nlb.arn
  port              = "443"
  protocol          = "TLS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.endpoint_tg.arn
  }
}

resource "aws_vpc_endpoint_service_configuration" "api" {
  acceptance_required        = false
  network_load_balancer_arns = [aws_lb.endpoint_nlb.arn]

  tags = {
    Name = "api-endpoint-service-config"
  }
}

# VPC Endpoint (Consumer)
resource "aws_vpc_endpoint" "api_consumer" {
  vpc_id       = var.consumer_vpc_id
  service_name = aws_vpc_endpoint_service_configuration.api.service_name
  vpc_endpoint_type = "Interface"
  subnet_ids   = var.consumer_subnet_ids
  security_groups = [aws_security_group.vpce.id]

  private_dns_enabled = true

  tags = {
    Name = "api-endpoint"
  }
}

resource "aws_security_group" "vpce" {
  name   = "api-vpce-sg"
  vpc_id = var.consumer_vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "api-vpce-sg"
  }
}

# Private DNS
resource "aws_vpc_endpoint_private_dns_name_options" "api" {
  vpc_endpoint_id             = aws_vpc_endpoint.api_consumer.id
  private_dns_enabled         = true
  private_dns_name_options_on_launch_enabled = true
}

# Variables
variable "subnet_ids" {
  type = list(string)
}

variable "vpc_id" {
  type = string
}

variable "certificate_arn" {
  type = string
}

variable "consumer_vpc_id" {
  type = string
}

variable "consumer_subnet_ids" {
  type = list(string)
}

# Outputs
output "service_name" {
  value = aws_vpc_endpoint_service_configuration.api.service_name
}

output "endpoint_id" {
  value = aws_vpc_endpoint.api_consumer.id
}
