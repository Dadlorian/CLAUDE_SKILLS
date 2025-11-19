# AWS Application Load Balancer (ALB) Configuration
# Terraform - Production Load Balancing Setup
# Last Updated: 2025-11-19

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "prod-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.subnet_ids

  enable_deletion_protection = true
  enable_http2              = true
  enable_cross_zone_load_balancing = true

  tags = {
    Name = "prod-alb"
    Environment = "production"
  }
}

# Security Group for ALB
resource "aws_security_group" "alb" {
  name        = "prod-alb-sg"
  description = "Security group for ALB"
  vpc_id      = var.vpc_id

  # Allow inbound HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow inbound HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "prod-alb-sg"
  }
}

# HTTP Listener - redirect to HTTPS
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# HTTPS Listener
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate.main.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web.arn
  }
}

# Target Group for Web Application
resource "aws_lb_target_group" "web" {
  name        = "prod-web-tg"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "instance"

  # Health check configuration
  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 3
    interval            = 30
    path                = "/health"
    matcher             = "200"
    port                = "80"
  }

  # Sticky sessions
  stickiness {
    type            = "lb_cookie"
    enabled         = true
    cookie_duration = 3600
  }

  tags = {
    Name = "prod-web-tg"
  }
}

# Target Group for API
resource "aws_lb_target_group" "api" {
  name        = "prod-api-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "instance"

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 10
    path                = "/api/health"
    matcher             = "200"
    port                = "8080"
  }

  tags = {
    Name = "prod-api-tg"
  }
}

# Listener Rule: Path-based routing
resource "aws_lb_listener_rule" "api" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }

  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }
}

# Listener Rule: Host-based routing
resource "aws_lb_listener_rule" "api_subdomain" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 101

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }

  condition {
    host_header {
      values = ["api.example.com"]
    }
  }
}

# Register EC2 instances as targets
resource "aws_lb_target_group_attachment" "web_instance" {
  count            = length(var.web_instance_ids)
  target_group_arn = aws_lb_target_group.web.arn
  target_id       = var.web_instance_ids[count.index]
  port             = 80
}

resource "aws_lb_target_group_attachment" "api_instance" {
  count            = length(var.api_instance_ids)
  target_group_arn = aws_lb_target_group.api.arn
  target_id       = var.api_instance_ids[count.index]
  port             = 8080
}

# SSL Certificate (ACM)
resource "aws_acm_certificate" "main" {
  domain_name       = var.domain_name
  validation_method = "DNS"

  subject_alternative_names = [
    "*.${var.domain_name}",
    "api.${var.domain_name}"
  ]

  tags = {
    Name = "prod-cert"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "alb_target_group_health" {
  alarm_name          = "prod-alb-unhealthy-targets"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "UnHealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Average"
  threshold           = 1

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
    TargetGroup  = aws_lb_target_group.web.arn_suffix
  }

  alarm_description = "Alert when web targets are unhealthy"
  alarm_actions     = [var.sns_topic_arn]
}

# Outputs
output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "alb_arn" {
  description = "ARN of the load balancer"
  value       = aws_lb.main.arn
}

output "alb_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}
