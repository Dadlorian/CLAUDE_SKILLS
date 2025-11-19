# Cloud Network Migration Guide

## Migration Planning & Assessment

### Network Assessment Framework

**Existing Network Inventory**
```
On-Premises:
├── Subnets: 10 total (10.0.0.0/16)
├── VLANs: 50+ active
├── Routers: 5 (aggregation + distribution)
├── Firewalls: 3 (active-active-standby)
├── Links: 4x 10Gbps
└── Services: 200+ applications

Target Cloud:
├── Primary: AWS (us-east-1)
├── Secondary: Azure (East US)
├── Backup: GCP (us-central1)
└── Gateway: Direct Connect + ExpressRoute
```

### Migration Phases

**Phase 1: Assessment (4-6 weeks)**
- Network diagram and documentation
- Application dependency mapping
- Bandwidth requirements
- Compliance requirements

**Phase 2: Design (6-8 weeks)**
- Cloud network architecture
- IP addressing scheme
- Security group/firewall rules
- Routing strategy

**Phase 3: Pilot (8-12 weeks)**
- Non-critical application migration
- Test failover procedures
- Validate performance
- Train operations team

**Phase 4: Production (4-6 weeks)**
- Cutover of critical systems
- Parallel running period
- Final decommissioning
- Lessons learned

## Step 1: Network Architecture Design

### Hybrid Network Design

```
┌─────────────────────────┐
│  On-Premises Data Center │
│  10.0.0.0/16             │
│  • 100+ Applications      │
│  • Legacy infrastructure  │
└────────────┬─────────────┘
             │ (Direct Connect / VPN)
             │
    ┌────────┴────────┐
    │                 │
┌───▼──────┐   ┌──────▼──┐
│   AWS    │   │  Azure  │
│ VPC      │   │  VNet   │
│ 10.1/16  │   │ 10.2/16 │
└───┬──────┘   └──────┬──┘
    │                 │
    └────────┬────────┘
             │
        ┌────▼─────┐
        │   GCP    │
        │   VPC    │
        │ 10.3/16  │
        └──────────┘
```

### IP Addressing Scheme

```hcl
variable "network_design" {
  default = {
    "AWS" = {
      "vpc_cidr"     = "10.1.0.0/16"
      "public_subnets" = ["10.1.1.0/24", "10.1.2.0/24"]
      "private_subnets" = ["10.1.10.0/23", "10.1.12.0/23"]
      "database_subnets" = ["10.1.20.0/24", "10.1.21.0/24"]
    }
    "Azure" = {
      "vnet_cidr"    = "10.2.0.0/16"
      "web_subnet"   = "10.2.1.0/24"
      "app_subnets"  = ["10.2.2.0/25", "10.2.2.128/25"]
      "db_subnets"   = ["10.2.3.0/24", "10.2.4.0/24"]
    }
    "GCP" = {
      "vpc_cidr"      = "10.3.0.0/16"
      "us_central"    = "10.3.0.0/20"
      "europe_west"   = "10.3.16.0/20"
    }
  }
}
```

## Step 2: Establish Hybrid Connectivity

### AWS Direct Connect Setup

```hcl
# Step 1: Create Direct Connect connection
resource "aws_dx_connection" "onprem_to_aws" {
  name      = "onprem-aws-dx"
  location  = "Your-DC-Location"
  bandwidth = "10Gbps"

  tags = {
    Name = "onprem-aws-dx"
  }
}

# Step 2: Create Virtual Interface
resource "aws_dx_virtual_interface" "onprem_to_aws_vif" {
  name             = "onprem-aws-vif"
  connection_id    = aws_dx_connection.onprem_to_aws.id
  vlan             = 100
  asn              = 65000
  auth_key         = "secret-auth-key"
  amazon_address   = "169.254.10.1/30"
  customer_address = "169.254.10.2/30"
  address_family   = "ipv4"

  depends_on = [aws_dx_connection.onprem_to_aws]
}

# Step 3: Create Virtual Private Gateway
resource "aws_vpn_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "vpn-gateway"
  }
}

# Step 4: Attach to DX
resource "aws_dx_gateway_association" "onprem_to_aws" {
  dx_gateway_id         = aws_dx_gateway.main.id
  associated_gateway_id = aws_vpn_gateway.main.id
}
```

### Azure ExpressRoute Setup

```hcl
resource "azurerm_express_route_circuit" "onprem_to_azure" {
  name                = "onprem-azure-expressroute"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_provider_name = "Your-SP"
  peering_location    = "Your-Location"
  bandwidth_in_mbps   = 10000

  sku {
    tier   = "Premium"
    family = "MeteredData"
  }

  tags = {
    Name = "onprem-azure-expressroute"
  }
}

# Configure private peering
resource "azurerm_express_route_circuit_peering" "private" {
  peering_type                  = "AzurePrivatePeering"
  express_route_circuit_name    = azurerm_express_route_circuit.onprem_to_azure.name
  resource_group_name           = azurerm_resource_group.main.name
  peer_asn                      = 65000
  primary_peer_address_prefix   = "169.254.21.0/30"
  secondary_peer_address_prefix = "169.254.22.0/30"
  vlan_id                       = 300
}
```

## Step 3: DNS Migration Strategy

### Hybrid DNS Resolution

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns-config
  namespace: kube-system
data:
  Corefile: |
    . {
      errors
      health {
        lameduck 5s
      }
      ready
      kubernetes cluster.local in-addr.arpa ip6.arpa {
        pods insecure
        fallthrough in-addr.arpa ip6.arpa
        ttl 30
      }
      prometheus :9153
      # Forward on-premises DNS
      forward onprem.local 10.0.0.1 {
        policy round_robin
      }
      # Forward AWS Route53
      forward aws.local 10.1.0.2 {
        policy round_robin
      }
      forward . /etc/resolv.conf {
        policy round_robin
      }
      cache 30
      loop
      reload
      loadbalance round_robin
    }
```

## Step 4: Application Migration

### Database Migration (Example: PostgreSQL)

```bash
#!/bin/bash
# 1. Create backup from on-premises
pg_dump -h onprem-db.local -U postgres -d myapp > backup.sql

# 2. Create RDS instance in AWS
aws rds create-db-instance \
  --db-instance-identifier myapp-db \
  --db-instance-class db.r5.2xlarge \
  --engine postgres \
  --allocated-storage 1000 \
  --master-username admin \
  --master-user-password "SecurePassword123!"

# 3. Restore from backup
psql -h myapp-db.xxxxx.us-east-1.rds.amazonaws.com \
  -U admin -d postgres -f backup.sql

# 4. Test connectivity from application
psql -h myapp-db.xxxxx.us-east-1.rds.amazonaws.com \
  -U admin -d myapp -c "SELECT 1"
```

### Application Network Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_host: |
    # Phase 1 & 2: On-premises database
    onprem-db.local:5432
    # Phase 3: Dual-write to both
    onprem-db.local:5432,myapp-db.rds.amazonaws.com:5432
    # Phase 4: Cloud database only
    myapp-db.rds.amazonaws.com:5432
  cache_host: |
    # Use cloud cache from start
    elasticache.amazonaws.com:6379
```

## Step 5: Security Migration

### Firewall Rule Migration

```hcl
# Old on-premises rule
# Allow web traffic from DMZ (10.0.1.0/24) to app tier (10.0.2.0/24) port 8080

# New AWS security group
resource "aws_security_group" "web_to_app" {
  name_prefix = "web-to-app-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
    cidr_blocks     = ["10.0.1.0/24"]  # Allow from on-premises during migration
  }

  tags = {
    MigratedFrom = "onprem-firewall-rule-123"
  }
}

# New Azure NSG
resource "azurerm_network_security_rule" "web_to_app" {
  name                        = "AllowWebToApp"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "8080"
  source_address_prefixes     = ["10.0.1.0/24", "10.1.1.0/24"]
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.main.name
  network_security_group_name = azurerm_network_security_group.app.name
}
```

## Step 6: Monitoring During Migration

### Health Checks

```hcl
# AWS Health Check
resource "aws_route53_health_check" "onprem_endpoint" {
  ip_address        = "203.0.113.1"
  port              = 443
  type              = "HTTPS"
  failure_threshold = 3
  request_interval  = 30

  tags = {
    Name = "onprem-health-check"
  }
}

resource "aws_route53_health_check" "cloud_endpoint" {
  fqdn              = aws_lb.main.dns_name
  port              = 443
  type              = "HTTPS"
  failure_threshold = 3
  request_interval  = 30

  tags = {
    Name = "cloud-health-check"
  }
}

# Route53 weighted routing for gradual cutover
resource "aws_route53_record" "app_weighted" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "app.example.com"
  type    = "A"

  weighted_routing_policy {
    weight = 10  # 10% to cloud
  }

  alias {
    name                   = aws_lb.cloud.dns_name
    zone_id                = aws_lb.cloud.zone_id
    evaluate_target_health = true
  }

  set_identifier = "cloud"
}

resource "aws_route53_record" "app_on_prem" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "app.example.com"
  type    = "A"

  weighted_routing_policy {
    weight = 90  # 90% to on-premises
  }

  ttl     = 60
  records = ["203.0.113.2"]
  set_identifier = "onprem"
}
```

## Step 7: Cutover Planning

### Cutover Checklist

```
Pre-Cutover (72 hours before):
- [ ] All data synchronized
- [ ] Final backup taken
- [ ] Network tested (full load)
- [ ] Rollback plan reviewed
- [ ] Team on-call confirmed

Cutover Day:
- [ ] Reduce DNS TTL (5 minutes)
- [ ] Monitor applications closely
- [ ] Alert team of any issues
- [ ] Have rollback ready

Post-Cutover (24 hours):
- [ ] Verify all services working
- [ ] Check data integrity
- [ ] Monitor performance
- [ ] Begin decommissioning on-prem

Post-Cutover (1 week):
- [ ] Disable VPN/Direct Connect to on-prem
- [ ] Archive on-premises data
- [ ] Conduct lessons learned
- [ ] Update documentation
```

## Step 8: Post-Migration Optimization

### Performance Optimization

```hcl
# Optimize data transfer
resource "aws_s3_bucket" "migration_cache" {
  bucket = "migration-cache-${data.aws_caller_identity.current.account_id}"

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

# CloudFront distribution for low latency
resource "aws_cloudfront_distribution" "migration" {
  origin {
    domain_name = aws_s3_bucket.migration_cache.bucket_regional_domain_name
    origin_id   = "S3Migration"
  }

  enabled = true

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3Migration"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "allow-all"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
```

## Best Practices

1. **Plan thoroughly** - 70% success factor
2. **Test extensively** - Multiple test runs
3. **Gradual cutover** - Reduce risk
4. **Monitor obsessively** - 24/7 during cutover
5. **Maintain fallback** - Keep old system running
6. **Document everything** - For future reference
7. **Train team first** - Ensure capabilities
8. **Start small** - Non-critical applications first
9. **Parallel running** - 1-2 weeks minimum
10. **Have rollback plan** - Ready to execute

---

**Last Updated:** 2025-11-19
