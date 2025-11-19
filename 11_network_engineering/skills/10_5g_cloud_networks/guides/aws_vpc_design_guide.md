# AWS VPC Design Guide

## VPC Architecture Planning

### Network Design Principles

**IP Address Planning**
```
Total Address Space: 10.0.0.0/16 (65,536 addresses)
├── Public Subnets: 10.0.1.0/24, 10.0.2.0/24 (512 addresses)
├── Private App Subnets: 10.0.10.0/23, 10.0.12.0/23 (1,024 addresses)
└── Database Subnets: 10.0.20.0/24, 10.0.21.0/24 (512 addresses)

Reserved for future expansion: 10.0.100.0/20 (4,096 addresses)
```

### Multi-AZ Deployment

**High Availability Design**
```
Region: us-east-1
├── AZ: us-east-1a
│   ├── Public Subnet: 10.0.1.0/24
│   ├── App Subnet: 10.0.10.0/25
│   └── DB Subnet: 10.0.20.0/25
├── AZ: us-east-1b
│   ├── Public Subnet: 10.0.2.0/24
│   ├── App Subnet: 10.0.10.128/25
│   └── DB Subnet: 10.0.20.128/25
└── AZ: us-east-1c (optional)
    └── Similar subnet structure
```

## Step 1: Create VPC

### VPC Creation Script

```bash
#!/bin/bash

# Create VPC
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=prod-vpc}]' \
  --query 'Vpc.VpcId' \
  --output text)

echo "Created VPC: $VPC_ID"

# Enable DNS hostname
aws ec2 modify-vpc-attribute \
  --vpc-id $VPC_ID \
  --enable-dns-hostnames

# Enable DNS resolution
aws ec2 modify-vpc-attribute \
  --vpc-id $VPC_ID \
  --enable-dns-support
```

### Using Terraform

```hcl
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "prod-vpc"
    Environment = "production"
  }
}

resource "aws_vpc_ipv4_cidr_block_association" "secondary" {
  vpc_id             = aws_vpc.main.id
  cidr_block         = "10.1.0.0/16"
  depends_on         = [aws_vpc.main]
}
```

## Step 2: Create Subnets

### Public Subnets

```hcl
resource "aws_subnet" "public_1a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet-1a"
    Type = "Public"
  }
}

resource "aws_subnet" "public_1b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet-1b"
    Type = "Public"
  }
}
```

### Private Application Subnets

```hcl
resource "aws_subnet" "private_app_1a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.10.0/25"
  availability_zone = "us-east-1a"

  tags = {
    Name = "private-app-1a"
    Type = "Private"
  }
}

resource "aws_subnet" "private_app_1b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.10.128/25"
  availability_zone = "us-east-1b"

  tags = {
    Name = "private-app-1b"
    Type = "Private"
  }
}
```

### Database Subnets

```hcl
resource "aws_db_subnet_group" "main" {
  name            = "prod-db-subnet-group"
  subnet_ids      = [aws_subnet.db_1a.id, aws_subnet.db_1b.id]

  tags = {
    Name = "prod-db-subnet-group"
  }
}

resource "aws_subnet" "db_1a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.20.0/25"
  availability_zone = "us-east-1a"

  tags = {
    Name = "db-subnet-1a"
    Type = "Database"
  }
}
```

## Step 3: Internet Connectivity

### Internet Gateway

```hcl
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "prod-igw"
  }
}
```

### NAT Gateway for Private Subnets

```hcl
# Elastic IP for NAT Gateway
resource "aws_eip" "nat_1a" {
  domain = "vpc"
  depends_on = [aws_internet_gateway.main]

  tags = {
    Name = "nat-eip-1a"
  }
}

# NAT Gateway in public subnet
resource "aws_nat_gateway" "nat_1a" {
  allocation_id = aws_eip.nat_1a.id
  subnet_id     = aws_subnet.public_1a.id
  depends_on    = [aws_internet_gateway.main]

  tags = {
    Name = "nat-gateway-1a"
  }
}
```

## Step 4: Routing Configuration

### Public Route Table

```hcl
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block      = "0.0.0.0/0"
    gateway_id      = aws_internet_gateway.main.id
  }

  tags = {
    Name = "public-rt"
  }
}

resource "aws_route_table_association" "public_1a" {
  subnet_id      = aws_subnet.public_1a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_1b" {
  subnet_id      = aws_subnet.public_1b.id
  route_table_id = aws_route_table.public.id
}
```

### Private Route Table

```hcl
resource "aws_route_table" "private_1a" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_1a.id
  }

  tags = {
    Name = "private-rt-1a"
  }
}

resource "aws_route_table_association" "private_app_1a" {
  subnet_id      = aws_subnet.private_app_1a.id
  route_table_id = aws_route_table.private_1a.id
}
```

## Step 5: Security Groups

### Web Server Security Group

```hcl
resource "aws_security_group" "web" {
  name_prefix = "web-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web-sg"
  }
}
```

### Database Security Group

```hcl
resource "aws_security_group" "database" {
  name_prefix = "database-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "database-sg"
  }
}
```

## Step 6: VPC Endpoints

### S3 Gateway Endpoint

```hcl
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.us-east-1.s3"
  route_table_ids = [aws_route_table.private_1a.id]

  tags = {
    Name = "s3-endpoint"
  }
}

resource "aws_vpc_endpoint_policy" "s3" {
  vpc_endpoint_id = aws_vpc_endpoint.s3.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = "*"
        Action = "s3:*"
        Resource = "*"
      }
    ]
  })
}
```

### ECR VPC Endpoint

```hcl
resource "aws_vpc_endpoint" "ecr" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.us-east-1.ecr.api"
  vpc_endpoint_type = "Interface"
  subnet_ids        = [aws_subnet.private_app_1a.id, aws_subnet.private_app_1b.id]
  security_group_ids = [aws_security_group.vpce.id]

  tags = {
    Name = "ecr-endpoint"
  }
}
```

## Step 7: VPC Flow Logs

### Enable Flow Logs

```hcl
resource "aws_flow_log" "main" {
  iam_role_arn    = aws_iam_role.flow_log.arn
  log_destination = aws_cloudwatch_log_group.flow_log.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id

  tags = {
    Name = "vpc-flow-logs"
  }
}

resource "aws_cloudwatch_log_group" "flow_log" {
  name              = "/aws/vpc/flowlogs"
  retention_in_days = 30
}

resource "aws_iam_role" "flow_log" {
  name = "vpc-flow-log-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}
```

## Step 8: Multi-Region Architecture

### Region-to-Region Peering

```hcl
# VPC in region 1 (provider alias: aws_east)
resource "aws_vpc_peering_connection" "east_to_west" {
  provider = aws_east
  vpc_id   = aws_vpc_east.main.id

  peer_owner_id = data.aws_caller_identity.current.account_id
  peer_region   = "us-west-2"
  peer_vpc_id   = aws_vpc_west.main.id

  tags = {
    Name = "east-to-west-peering"
  }
}

# Accept peering in region 2 (provider alias: aws_west)
resource "aws_vpc_peering_connection_accepter" "west" {
  provider                  = aws_west
  vpc_peering_connection_id = aws_vpc_peering_connection.east_to_west.id
  auto_accept               = true

  tags = {
    Name = "accept-east-to-west"
  }
}
```

## Step 9: Transit Gateway Setup

### Deploy Transit Gateway

```hcl
resource "aws_ec2_transit_gateway" "main" {
  description                    = "Main Transit Gateway"
  default_route_table_association = "enable"
  default_route_table_propagation = "enable"

  tags = {
    Name = "prod-tgw"
  }
}

resource "aws_ec2_transit_gateway_vpc_attachment" "main" {
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  vpc_id             = aws_vpc.main.id
  subnet_ids         = [aws_subnet.private_app_1a.id, aws_subnet.private_app_1b.id]

  tags = {
    Name = "tgw-attachment-main"
  }
}
```

## Best Practices Checklist

- [ ] CIDR planning allows for growth (20% future expansion)
- [ ] Multi-AZ deployment for high availability
- [ ] Public/private subnet separation
- [ ] NAT Gateway for private subnet internet access
- [ ] Security group least privilege
- [ ] Network ACL ingress/egress rules
- [ ] VPC Flow Logs enabled
- [ ] VPC Endpoints for AWS services
- [ ] Monitoring and alerting configured
- [ ] Disaster recovery plan documented

---

**Last Updated:** 2025-11-19
