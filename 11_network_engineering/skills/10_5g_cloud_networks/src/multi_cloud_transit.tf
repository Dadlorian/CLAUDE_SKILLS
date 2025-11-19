# Multi-Cloud Transit Gateway Configuration

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
  alias  = "primary"
}

provider "aws" {
  region = "eu-west-1"
  alias  = "secondary"
}

# Primary Region Transit Gateway
resource "aws_ec2_transit_gateway" "primary" {
  provider                       = aws.primary
  description                    = "Multi-cloud Transit Gateway - Primary"
  default_route_table_association = "enable"
  default_route_table_propagation = "enable"
  dns_support                    = "enable"
  vpn_ecn_support                = "enable"

  tags = {
    Name = "prod-tgw-primary"
  }
}

# Secondary Region Transit Gateway
resource "aws_ec2_transit_gateway" "secondary" {
  provider                       = aws.secondary
  description                    = "Multi-cloud Transit Gateway - Secondary"
  default_route_table_association = "enable"
  default_route_table_propagation = "enable"
  dns_support                    = "enable"
  vpn_ecn_support                = "enable"

  tags = {
    Name = "prod-tgw-secondary"
  }
}

# Inter-Region Peering
resource "aws_ec2_transit_gateway_peering_attachment" "primary_to_secondary" {
  provider                    = aws.primary
  transit_gateway_id          = aws_ec2_transit_gateway.primary.id
  peer_transit_gateway_id     = aws_ec2_transit_gateway.secondary.id
  peer_region                 = "eu-west-1"

  tags = {
    Name = "tgw-peering-primary-secondary"
  }
}

resource "aws_ec2_transit_gateway_peering_attachment_accepter" "secondary" {
  provider                      = aws.secondary
  transit_gateway_attachment_id = aws_ec2_transit_gateway_peering_attachment.primary_to_secondary.id

  tags = {
    Name = "tgw-peering-secondary-accept"
  }
}

# Transit Gateway Route Table - Primary
resource "aws_ec2_transit_gateway_route_table" "primary" {
  provider           = aws.primary
  transit_gateway_id = aws_ec2_transit_gateway.primary.id

  tags = {
    Name = "prod-tgw-primary-rt"
  }
}

# Transit Gateway Route Table - Secondary
resource "aws_ec2_transit_gateway_route_table" "secondary" {
  provider           = aws.secondary
  transit_gateway_id = aws_ec2_transit_gateway.secondary.id

  tags = {
    Name = "prod-tgw-secondary-rt"
  }
}

# Route for inter-region traffic through TGW peering
resource "aws_ec2_transit_gateway_route" "primary_to_secondary" {
  provider                       = aws.primary
  destination_cidr_block         = "10.1.0.0/16"  # Secondary region CIDR
  transit_gateway_attachment_id  = aws_ec2_transit_gateway_peering_attachment.primary_to_secondary.id
  transit_gateway_route_table_id = aws_ec2_transit_gateway_route_table.primary.id
  blackhole                      = false
}

resource "aws_ec2_transit_gateway_route" "secondary_to_primary" {
  provider                       = aws.secondary
  destination_cidr_block         = "10.0.0.0/16"  # Primary region CIDR
  transit_gateway_attachment_id  = aws_ec2_transit_gateway_peering_attachment.primary_to_secondary.id
  transit_gateway_route_table_id = aws_ec2_transit_gateway_route_table.secondary.id
  blackhole                      = false
}

# VPC Attachments - Primary Region
resource "aws_ec2_transit_gateway_vpc_attachment" "primary_vpc1" {
  provider           = aws.primary
  subnet_ids         = var.primary_vpc1_subnet_ids
  transit_gateway_id = aws_ec2_transit_gateway.primary.id
  vpc_id             = var.primary_vpc1_id

  tags = {
    Name = "vpc1-attachment-primary"
  }
}

resource "aws_ec2_transit_gateway_vpc_attachment" "primary_vpc2" {
  provider           = aws.primary
  subnet_ids         = var.primary_vpc2_subnet_ids
  transit_gateway_id = aws_ec2_transit_gateway.primary.id
  vpc_id             = var.primary_vpc2_id

  tags = {
    Name = "vpc2-attachment-primary"
  }
}

# VPC Attachments - Secondary Region
resource "aws_ec2_transit_gateway_vpc_attachment" "secondary_vpc3" {
  provider           = aws.secondary
  subnet_ids         = var.secondary_vpc3_subnet_ids
  transit_gateway_id = aws_ec2_transit_gateway.secondary.id
  vpc_id             = var.secondary_vpc3_id

  tags = {
    Name = "vpc3-attachment-secondary"
  }
}

# Route propagation and association
resource "aws_ec2_transit_gateway_route_table_association" "primary_vpc1" {
  provider                       = aws.primary
  transit_gateway_attachment_id  = aws_ec2_transit_gateway_vpc_attachment.primary_vpc1.id
  transit_gateway_route_table_id = aws_ec2_transit_gateway_route_table.primary.id
}

resource "aws_ec2_transit_gateway_route_table_association" "secondary_vpc3" {
  provider                       = aws.secondary
  transit_gateway_attachment_id  = aws_ec2_transit_gateway_vpc_attachment.secondary_vpc3.id
  transit_gateway_route_table_id = aws_ec2_transit_gateway_route_table.secondary.id
}

# Variables
variable "primary_vpc1_id" {
  type = string
}

variable "primary_vpc1_subnet_ids" {
  type = list(string)
}

variable "primary_vpc2_id" {
  type = string
}

variable "primary_vpc2_subnet_ids" {
  type = list(string)
}

variable "secondary_vpc3_id" {
  type = string
}

variable "secondary_vpc3_subnet_ids" {
  type = list(string)
}

# Outputs
output "primary_tgw_id" {
  value = aws_ec2_transit_gateway.primary.id
}

output "secondary_tgw_id" {
  value = aws_ec2_transit_gateway.secondary.id
}

output "peering_attachment_id" {
  value = aws_ec2_transit_gateway_peering_attachment.primary_to_secondary.id
}
