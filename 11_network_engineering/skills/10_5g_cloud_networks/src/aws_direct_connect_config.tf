# AWS Direct Connect Configuration

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

variable "customer_bgp_asn" {
  type    = number
  default = 65000
}

provider "aws" {
  region = var.aws_region
}

# Direct Connect Connection (1 Gbps)
resource "aws_dx_connection" "main" {
  name      = "main-dx-connection"
  location  = "Your-DataCenter-Location"
  bandwidth = "10Gbps"

  tags = {
    Name = "main-dx"
  }
}

# BGP Configuration
resource "aws_dx_virtual_interface" "private_vif" {
  connection_id      = aws_dx_connection.main.id
  name               = "main-private-vif"
  vlan               = 100
  asn                = var.customer_bgp_asn
  auth_key           = "CustomerAuthKey12345"
  amazon_address     = "169.254.10.1/30"
  customer_address   = "169.254.10.2/30"
  address_family     = "ipv4"
  virtual_gateway_id = aws_vpn_gateway.main.id

  depends_on = [aws_vpn_gateway.main]
}

# VPN Gateway for DX
resource "aws_vpn_gateway" "main" {
  vpc_id = var.vpc_id

  tags = {
    Name = "dx-gateway"
  }
}

# Enable route propagation
resource "aws_vpn_gateway_route_propagation" "main" {
  vpn_gateway_id = aws_vpn_gateway.main.id
  route_table_id = var.route_table_id
}

# Direct Connect Gateway (for multi-VPC/multi-region)
resource "aws_dx_gateway" "main" {
  name            = "main-dx-gateway"
  amazon_asn      = 64512

  tags = {
    Name = "main-dx-gateway"
  }
}

# Associate VPNGateway with DX Gateway
resource "aws_dx_gateway_association" "main" {
  dx_gateway_id         = aws_dx_gateway.main.id
  associated_gateway_id = aws_vpn_gateway.main.id

  proposal_id = aws_dx_gateway_association_proposal.main.id
}

resource "aws_dx_gateway_association_proposal" "main" {
  dx_gateway_id             = aws_dx_gateway.main.id
  dx_gateway_owner_account_id = data.aws_caller_identity.current.account_id
  associated_gateway_id     = aws_vpn_gateway.main.id
}

# CloudWatch Alarms for DX
resource "aws_cloudwatch_metric_alarm" "dx_connection_down" {
  alarm_name          = "dx-connection-down"
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "ConnectionState"
  namespace           = "AWS/DX"
  period              = "60"
  statistic           = "Average"
  threshold           = "0"
  alarm_description   = "Alert when Direct Connect connection is down"

  dimensions = {
    ConnectionId = aws_dx_connection.main.id
  }
}

# Variables
variable "vpc_id" {
  type = string
}

variable "route_table_id" {
  type = string
}

# Data source for current account
data "aws_caller_identity" "current" {}

# Outputs
output "dx_connection_id" {
  value = aws_dx_connection.main.id
}

output "dx_connection_name_server" {
  value = aws_dx_connection.main.name_server
}

output "dx_gateway_id" {
  value = aws_dx_gateway.main.id
}

output "private_vif_id" {
  value = aws_dx_virtual_interface.private_vif.id
}
