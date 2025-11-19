# AWS Transit Gateway Configuration
# Multi-VPC / Multi-region connectivity

terraform {
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

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

# Transit Gateway
resource "aws_ec2_transit_gateway" "main" {
  description                    = "Main Transit Gateway for multi-VPC connectivity"
  default_route_table_association = "enable"
  default_route_table_propagation = "enable"
  dns_support                    = "enable"
  vpn_ecn_support                = "enable"

  tags = {
    Name = "production-tgw"
  }
}

# Transit Gateway Route Table
resource "aws_ec2_transit_gateway_route_table" "main" {
  transit_gateway_id = aws_ec2_transit_gateway.main.id

  tags = {
    Name = "production-tgw-rt"
  }
}

# VPC 1 Attachment
resource "aws_ec2_transit_gateway_vpc_attachment" "vpc1" {
  subnet_ids         = var.vpc1_subnet_ids
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  vpc_id             = var.vpc1_id

  tags = {
    Name = "vpc1-attachment"
  }
}

# VPC 2 Attachment
resource "aws_ec2_transit_gateway_vpc_attachment" "vpc2" {
  subnet_ids         = var.vpc2_subnet_ids
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  vpc_id             = var.vpc2_id

  tags = {
    Name = "vpc2-attachment"
  }
}

# Transit Gateway Route - VPC1 to VPC2
resource "aws_ec2_transit_gateway_route" "vpc1_to_vpc2" {
  destination_cidr_block          = var.vpc2_cidr
  transit_gateway_attachment_id   = aws_ec2_transit_gateway_vpc_attachment.vpc2.id
  transit_gateway_route_table_id  = aws_ec2_transit_gateway_route_table.main.id
}

# Transit Gateway Route - VPC2 to VPC1
resource "aws_ec2_transit_gateway_route" "vpc2_to_vpc1" {
  destination_cidr_block          = var.vpc1_cidr
  transit_gateway_attachment_id   = aws_ec2_transit_gateway_vpc_attachment.vpc1.id
  transit_gateway_route_table_id  = aws_ec2_transit_gateway_route_table.main.id
}

# Update VPC Route Tables to use TGW
resource "aws_route" "vpc1_to_vpc2" {
  route_table_id            = var.vpc1_route_table_id
  destination_cidr_block    = var.vpc2_cidr
  transit_gateway_id        = aws_ec2_transit_gateway.main.id
}

resource "aws_route" "vpc2_to_vpc1" {
  route_table_id            = var.vpc2_route_table_id
  destination_cidr_block    = var.vpc1_cidr
  transit_gateway_id        = aws_ec2_transit_gateway.main.id
}

# Transit Gateway Policy Document
resource "aws_ec2_transit_gateway_policy_table" "policy" {
  transit_gateway_id = aws_ec2_transit_gateway.main.id

  tags = {
    Name = "production-tgw-policy"
  }
}

# Variables
variable "vpc1_id" {
  type = string
}

variable "vpc1_cidr" {
  type = string
}

variable "vpc1_subnet_ids" {
  type = list(string)
}

variable "vpc1_route_table_id" {
  type = string
}

variable "vpc2_id" {
  type = string
}

variable "vpc2_cidr" {
  type = string
}

variable "vpc2_subnet_ids" {
  type = list(string)
}

variable "vpc2_route_table_id" {
  type = string
}

# Outputs
output "transit_gateway_id" {
  value = aws_ec2_transit_gateway.main.id
}

output "transit_gateway_route_table_id" {
  value = aws_ec2_transit_gateway_route_table.main.id
}

output "vpc1_attachment_id" {
  value = aws_ec2_transit_gateway_vpc_attachment.vpc1.id
}

output "vpc2_attachment_id" {
  value = aws_ec2_transit_gateway_vpc_attachment.vpc2.id
}
