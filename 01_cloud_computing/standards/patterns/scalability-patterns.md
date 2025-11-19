# Scalability Architecture Patterns

## Overview

Scalability patterns enable systems to handle increased load by efficiently distributing workloads across resources. This guide covers essential patterns for building systems that scale horizontally and vertically to meet growing demands.

## Table of Contents

1. [Auto-Scaling Pattern](#auto-scaling-pattern)
2. [Load Balancing Pattern](#load-balancing-pattern)
3. [Sharding Pattern](#sharding-pattern)
4. [Read Replicas Pattern](#read-replicas-pattern)
5. [CDN Pattern](#cdn-pattern)
6. [Database Scaling Patterns](#database-scaling-patterns)
7. [Async Processing Pattern](#async-processing-pattern)

## Scalability Fundamentals

```
┌──────────────────────────────────────────┐
│        Scalability Dimensions            │
├──────────────────────────────────────────┤
│                                          │
│  Vertical Scaling (Scale Up)            │
│  - Increase resource size               │
│  - Bigger CPU, RAM, disk                │
│  - Limited by hardware limits           │
│  - Downtime for scaling                 │
│                                          │
│  Horizontal Scaling (Scale Out)         │
│  - Add more instances                   │
│  - Distribute load across nodes         │
│  - Nearly unlimited scaling             │
│  - No downtime for scaling              │
│                                          │
└──────────────────────────────────────────┘

Performance Metrics:
  - Throughput: Requests per second (RPS)
  - Latency: Response time (p50, p95, p99)
  - Concurrency: Simultaneous connections
  - Resource Utilization: CPU, Memory, Network
```

---

## 1. Auto-Scaling Pattern

### Description

Automatically adjust the number of compute resources based on demand metrics, ensuring optimal resource utilization and cost efficiency.

### When to Use

- Variable traffic patterns
- Cost optimization important
- Handle traffic spikes
- Maintain consistent performance
- Cloud-native applications

### Scaling Strategies

```
┌──────────────────────────────────────────┐
│        Auto-Scaling Strategies           │
├──────────────────────────────────────────┤
│                                          │
│  1. Target Tracking                     │
│     - Maintain specific metric value    │
│     - e.g., CPU at 70%                  │
│                                          │
│  2. Step Scaling                        │
│     - Add/remove instances in steps     │
│     - Based on metric thresholds        │
│                                          │
│  3. Scheduled Scaling                   │
│     - Scale based on time patterns      │
│     - e.g., business hours              │
│                                          │
│  4. Predictive Scaling                  │
│     - ML-based forecasting              │
│     - Proactive scaling                 │
│                                          │
└──────────────────────────────────────────┘
```

### Architecture Diagram

```
┌──────────────────────────────────────────────────┐
│          Auto-Scaling Architecture               │
└──────────────────────────────────────────────────┘

         CloudWatch Metrics
              │
              │ CPU, Memory, Network
              │ Custom Metrics
              ▼
     ┌─────────────────┐
     │  Auto Scaling   │
     │     Policy      │
     └────────┬────────┘
              │
         Scaling Decision
              │
    ┌─────────┼─────────┐
    │                   │
Scale Out          Scale In
    │                   │
    ▼                   ▼
┌─────────────────────────────────┐
│    Auto Scaling Group           │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐  │
│  │EC2 │ │EC2 │ │EC2 │ │EC2 │  │
│  │ 1  │ │ 2  │ │ 3  │ │ 4  │  │
│  └────┘ └────┘ └────┘ └────┘  │
└─────────────────────────────────┘
         │
         ▼
   ┌──────────┐
   │   Load   │
   │ Balancer │
   └──────────┘
```

### Implementation Example - Terraform AWS

```hcl
# auto_scaling.tf

# Launch Template
resource "aws_launch_template" "app" {
  name_prefix   = "app-server-"
  image_id      = data.aws_ami.amazon_linux_2.id
  instance_type = "t3.medium"

  vpc_security_group_ids = [aws_security_group.app.id]

  user_data = base64encode(templatefile("${path.module}/userdata.sh", {
    app_version = var.app_version
  }))

  iam_instance_profile {
    name = aws_iam_instance_profile.app.name
  }

  block_device_mappings {
    device_name = "/dev/sda1"

    ebs {
      volume_size           = 20
      volume_type           = "gp3"
      delete_on_termination = true
      encrypted             = true
    }
  }

  monitoring {
    enabled = true
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "App Server"
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "app" {
  name                = "app-asg"
  vpc_zone_identifier = var.private_subnet_ids
  target_group_arns   = [aws_lb_target_group.app.arn]
  health_check_type   = "ELB"
  health_check_grace_period = 300

  min_size         = 2
  max_size         = 10
  desired_capacity = 3

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  enabled_metrics = [
    "GroupDesiredCapacity",
    "GroupInServiceInstances",
    "GroupMinSize",
    "GroupMaxSize",
    "GroupPendingInstances",
    "GroupTerminatingInstances",
  ]

  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 50
      instance_warmup        = 300
    }
  }

  tag {
    key                 = "Name"
    value               = "App Server"
    propagate_at_launch = true
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Target Tracking Scaling Policy - CPU
resource "aws_autoscaling_policy" "cpu_target" {
  name                   = "cpu-target-tracking"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

# Target Tracking Scaling Policy - ALB Request Count
resource "aws_autoscaling_policy" "request_count_target" {
  name                   = "request-count-target-tracking"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.app.arn_suffix}/${aws_lb_target_group.app.arn_suffix}"
    }
    target_value = 1000.0
  }
}

# Step Scaling Policy - Scale Out
resource "aws_autoscaling_policy" "scale_out" {
  name                   = "scale-out"
  autoscaling_group_name = aws_autoscaling_group.app.name
  adjustment_type        = "ChangeInCapacity"
  policy_type            = "StepScaling"

  step_adjustment {
    scaling_adjustment          = 1
    metric_interval_lower_bound = 0
    metric_interval_upper_bound = 10
  }

  step_adjustment {
    scaling_adjustment          = 2
    metric_interval_lower_bound = 10
    metric_interval_upper_bound = 20
  }

  step_adjustment {
    scaling_adjustment          = 3
    metric_interval_lower_bound = 20
  }
}

# CloudWatch Alarm for Step Scaling
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "app-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "60"
  statistic           = "Average"
  threshold           = "80"

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.app.name
  }

  alarm_actions = [aws_autoscaling_policy.scale_out.arn]
}

# Scheduled Scaling - Scale up for business hours
resource "aws_autoscaling_schedule" "business_hours_scale_up" {
  scheduled_action_name  = "business-hours-scale-up"
  min_size               = 5
  max_size               = 10
  desired_capacity       = 5
  recurrence             = "0 8 * * MON-FRI"
  autoscaling_group_name = aws_autoscaling_group.app.name
}

# Scheduled Scaling - Scale down after hours
resource "aws_autoscaling_schedule" "after_hours_scale_down" {
  scheduled_action_name  = "after-hours-scale-down"
  min_size               = 2
  max_size               = 10
  desired_capacity       = 2
  recurrence             = "0 18 * * MON-FRI"
  autoscaling_group_name = aws_autoscaling_group.app.name
}
```

### Kubernetes Horizontal Pod Autoscaler

```yaml
# kubernetes-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  minReplicas: 3
  maxReplicas: 50
  metrics:
  # CPU-based scaling
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

  # Memory-based scaling
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

  # Custom metric (requests per second)
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"

  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Min

    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 4
        periodSeconds: 30
      selectPolicy: Max

---
# Vertical Pod Autoscaler
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: app
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2
        memory: 2Gi
```

### Trade-offs

**Pros:**
- Cost optimization
- Handle traffic spikes
- Improved availability
- No manual intervention
- Right-sizing resources

**Cons:**
- Scaling lag (startup time)
- Cost of over-provisioning
- Complexity in tuning
- Stateful applications challenges

### Anti-patterns

- **Too Aggressive Scaling**: Thrashing (constant scaling up/down)
- **No Cooldown**: Scaling too frequently
- **Wrong Metrics**: Scaling on inappropriate signals
- **No Pre-warming**: Cold start delays

### Real-world Examples

**Netflix**: Auto-scaling across thousands of instances based on streaming demand.

**Amazon**: Auto-scaling for all major services (Prime Day traffic handling).

**Spotify**: Kubernetes-based auto-scaling for music streaming services.

---

## 2. Load Balancing Pattern

### Description

Distribute incoming traffic across multiple servers to ensure no single server becomes overwhelmed, improving availability and performance.

### Load Balancing Algorithms

```
┌──────────────────────────────────────────┐
│     Load Balancing Algorithms            │
├──────────────────────────────────────────┤
│                                          │
│  Round Robin                            │
│  └─ Distribute evenly in rotation       │
│                                          │
│  Least Connections                      │
│  └─ Route to server with fewest active  │
│                                          │
│  Least Response Time                    │
│  └─ Route to fastest responding server  │
│                                          │
│  IP Hash                                │
│  └─ Same client → same server           │
│                                          │
│  Weighted Round Robin                   │
│  └─ Weight based on capacity            │
│                                          │
│  Geolocation                            │
│  └─ Route based on client location      │
│                                          │
└──────────────────────────────────────────┘
```

### Architecture Diagram

```
┌──────────────────────────────────────────────────┐
│        Load Balancer Architecture                │
└──────────────────────────────────────────────────┘

         Internet
             │
             ▼
    ┌────────────────┐
    │  Application   │
    │ Load Balancer  │
    │     (ALB)      │
    └────────┬───────┘
             │
    ┌────────┼────────┬────────┐
    │        │        │        │
    ▼        ▼        ▼        ▼
┌──────┐┌──────┐┌──────┐┌──────┐
│Server││Server││Server││Server│
│  1   ││  2   ││  3   ││  4   │
└──────┘└──────┘└──────┘└──────┘

Health Checks:
  ✓ Server 1: Healthy
  ✓ Server 2: Healthy
  ✓ Server 3: Healthy
  ✗ Server 4: Unhealthy (removed from pool)
```

### Implementation Example - AWS ALB

```hcl
# load_balancer.tf

# Application Load Balancer
resource "aws_lb" "app" {
  name               = "app-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = true
  enable_http2              = true
  enable_cross_zone_load_balancing = true

  access_logs {
    bucket  = aws_s3_bucket.lb_logs.id
    prefix  = "app-alb"
    enabled = true
  }

  tags = {
    Name = "Application Load Balancer"
  }
}

# Target Group
resource "aws_lb_target_group" "app" {
  name     = "app-tg"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  deregistration_delay = 30

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
    protocol            = "HTTP"
  }

  stickiness {
    type            = "lb_cookie"
    cookie_duration = 86400
    enabled         = true
  }

  tags = {
    Name = "App Target Group"
  }
}

# HTTPS Listener
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.app.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# HTTP to HTTPS Redirect
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
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

# Path-based Routing
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

# Host-based Routing
resource "aws_lb_listener_rule" "admin" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 200

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.admin.arn
  }

  condition {
    host_header {
      values = ["admin.example.com"]
    }
  }
}

# Network Load Balancer (for TCP/UDP)
resource "aws_lb" "network" {
  name               = "app-nlb"
  internal           = false
  load_balancer_type = "network"
  subnets            = var.public_subnet_ids

  enable_cross_zone_load_balancing = true

  tags = {
    Name = "Network Load Balancer"
  }
}
```

### Nginx Load Balancer Configuration

```nginx
# nginx-load-balancer.conf

upstream backend {
    # Load balancing algorithm
    least_conn;

    # Backend servers
    server backend1.example.com:8080 weight=3 max_fails=3 fail_timeout=30s;
    server backend2.example.com:8080 weight=2 max_fails=3 fail_timeout=30s;
    server backend3.example.com:8080 weight=1 max_fails=3 fail_timeout=30s;
    server backend4.example.com:8080 backup;

    # Health check
    keepalive 32;
}

server {
    listen 80;
    server_name example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # Connection timeout
    proxy_connect_timeout 5s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # Buffer settings
    proxy_buffering on;
    proxy_buffer_size 4k;
    proxy_buffers 8 4k;

    location / {
        proxy_pass http://backend;

        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Health check
        proxy_next_upstream error timeout http_500 http_502 http_503;
        proxy_next_upstream_tries 3;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;

    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://backend;
    }
}
```

### Real-world Examples

**Google**: Global load balancing across datacenters.

**Amazon**: ELB handling millions of requests per second.

**Cloudflare**: Global load balancing with DDoS protection.

---

## 3. Sharding Pattern

### Description

Partition data across multiple databases based on a shard key, enabling horizontal scaling of databases.

### When to Use

- Data volume exceeds single database capacity
- Write throughput bottleneck
- Geographic data distribution
- Tenant isolation (multi-tenancy)

### Sharding Strategies

```
┌──────────────────────────────────────────┐
│         Sharding Strategies              │
├──────────────────────────────────────────┤
│                                          │
│  1. Hash-Based Sharding                 │
│     shard = hash(key) % num_shards      │
│     - Even distribution                 │
│     - Adding shards requires rebalancing│
│                                          │
│  2. Range-Based Sharding                │
│     e.g., A-M → Shard1, N-Z → Shard2   │
│     - Predictable location              │
│     - Risk of hot spots                 │
│                                          │
│  3. Geographic Sharding                 │
│     By region/country                   │
│     - Low latency                       │
│     - Compliance benefits               │
│                                          │
│  4. Entity/Tenant-Based                 │
│     One tenant per shard                │
│     - Isolation                         │
│     - Easier to manage                  │
│                                          │
└──────────────────────────────────────────┘
```

### Architecture Diagram

```
┌──────────────────────────────────────────────────┐
│            Sharding Architecture                 │
└──────────────────────────────────────────────────┘

         Application
              │
              ▼
      ┌──────────────┐
      │   Shard      │
      │   Router     │
      │  (hash key)  │
      └──────┬───────┘
             │
    ┌────────┼────────┬────────┐
    │        │        │        │
    ▼        ▼        ▼        ▼
┌────────┐┌────────┐┌────────┐┌────────┐
│Shard 1 ││Shard 2 ││Shard 3 ││Shard 4 │
│        ││        ││        ││        │
│Users   ││Users   ││Users   ││Users   │
│0-24999 ││25K-49K ││50K-74K ││75K-99K │
└────────┘└────────┘└────────┘└────────┘
```

### Implementation Example

```python
# sharding.py
import hashlib
from typing import Any, List
import psycopg2

class ShardRouter:
    def __init__(self, shard_configs: List[dict]):
        """
        Args:
            shard_configs: List of shard connection configurations
        """
        self.shards = [
            psycopg2.connect(**config)
            for config in shard_configs
        ]
        self.num_shards = len(self.shards)

    def get_shard(self, shard_key: str):
        """Get shard connection for given key"""
        shard_id = self._compute_shard_id(shard_key)
        return self.shards[shard_id]

    def _compute_shard_id(self, shard_key: str) -> int:
        """Compute shard ID using consistent hashing"""
        hash_value = int(hashlib.md5(shard_key.encode()).hexdigest(), 16)
        return hash_value % self.num_shards


class ShardedUserRepository:
    """User repository with sharding"""

    def __init__(self, router: ShardRouter):
        self.router = router

    def create_user(self, user_id: str, name: str, email: str):
        """Create user in appropriate shard"""
        shard = self.router.get_shard(user_id)

        with shard.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (user_id, name, email)
                VALUES (%s, %s, %s)
            """, (user_id, name, email))
            shard.commit()

    def get_user(self, user_id: str) -> dict:
        """Get user from appropriate shard"""
        shard = self.router.get_shard(user_id)

        with shard.cursor() as cursor:
            cursor.execute(
                "SELECT user_id, name, email FROM users WHERE user_id = %s",
                (user_id,)
            )
            row = cursor.fetchone()

            if row:
                return {
                    'user_id': row[0],
                    'name': row[1],
                    'email': row[2]
                }

        return None

    def get_all_users(self) -> List[dict]:
        """Get users from all shards (scatter-gather)"""
        all_users = []

        for shard in self.router.shards:
            with shard.cursor() as cursor:
                cursor.execute("SELECT user_id, name, email FROM users")
                rows = cursor.fetchall()

                for row in rows:
                    all_users.append({
                        'user_id': row[0],
                        'name': row[1],
                        'email': row[2]
                    })

        return all_users


# Consistent Hashing for better redistribution
class ConsistentHashRouter:
    def __init__(self, shards: List[str], virtual_nodes: int = 150):
        """
        Args:
            shards: List of shard identifiers
            virtual_nodes: Number of virtual nodes per shard
        """
        self.ring = {}
        self.sorted_keys = []
        self.shards = shards

        for shard in shards:
            for i in range(virtual_nodes):
                key = self._hash(f"{shard}:{i}")
                self.ring[key] = shard
                self.sorted_keys.append(key)

        self.sorted_keys.sort()

    def get_shard(self, key: str) -> str:
        """Get shard using consistent hashing"""
        if not self.ring:
            return None

        hash_key = self._hash(key)

        # Find first node >= hash_key
        for ring_key in self.sorted_keys:
            if ring_key >= hash_key:
                return self.ring[ring_key]

        # Wrap around to first node
        return self.ring[self.sorted_keys[0]]

    def _hash(self, key: str) -> int:
        """Hash function"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
```

### Real-world Examples

**Instagram**: User data sharded across thousands of PostgreSQL instances.

**Pinterest**: Sharded MySQL for pin and board data.

**Discord**: Sharded architecture for messages across millions of servers.

---

## 4. Read Replicas Pattern

### Description

Create read-only copies of the database to offload read traffic from the primary database, improving read scalability.

### Architecture Diagram

```
┌──────────────────────────────────────────────────┐
│         Read Replicas Architecture               │
└──────────────────────────────────────────────────┘

    Application
         │
    ┌────┴────┐
  Writes   Reads
    │        │
    │        ▼
    │   ┌──────────┐
    │   │Read Load │
    │   │Balancer  │
    │   └────┬─────┘
    │        │
    │   ┌────┼────┬────┐
    ▼   ▼    ▼    ▼    ▼
┌─────────┐┌───┐┌───┐┌───┐
│ Primary ││R1 ││R2 ││R3 │
│Database ││   ││   ││   │
│(Master) ││   ││   ││   │
└────┬────┘└───┘└───┘└───┘
     │        ▲   ▲   ▲
     │Replication  │   │
     └─────────────┴───┘
```

### Implementation Example

```python
# read_replicas.py
import psycopg2
from typing import List
import random

class DatabaseCluster:
    def __init__(self, master_config: dict, replica_configs: List[dict]):
        self.master = psycopg2.connect(**master_config)
        self.replicas = [
            psycopg2.connect(**config)
            for config in replica_configs
        ]

    def execute_write(self, query: str, params: tuple = None):
        """Execute write on master"""
        with self.master.cursor() as cursor:
            cursor.execute(query, params)
            self.master.commit()

    def execute_read(self, query: str, params: tuple = None,
                    use_master: bool = False):
        """Execute read on replica (or master if specified)"""
        conn = self.master if use_master else random.choice(self.replicas)

        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
```

### Real-world Examples

**Amazon RDS**: Read replicas for MySQL, PostgreSQL, MariaDB.

**Twitter**: Extensive use of read replicas for timeline queries.

---

## 5. CDN Pattern

### Description

Content Delivery Network caches static content at edge locations close to users, reducing latency and origin server load.

### Architecture

```
┌──────────────────────────────────────────────────┐
│           CDN Architecture                       │
└──────────────────────────────────────────────────┘

       Users                    Edge Locations
         │                           │
    ┌────┼────┐              ┌───────┼───────┐
    │    │    │              │       │       │
    ▼    ▼    ▼              ▼       ▼       ▼
┌──────────────────┐    ┌──────┐┌──────┐┌──────┐
│Global Users      │───►│Edge 1││Edge 2││Edge 3│
│                  │    │(US)  ││(EU)  ││(APAC)│
└──────────────────┘    └───┬──┘└───┬──┘└───┬──┘
                            │Cache  │Cache  │Cache
                            │Miss   │Miss   │Miss
                            └───────┼───────┘
                                    │
                              ┌─────▼─────┐
                              │  Origin   │
                              │  Server   │
                              └───────────┘
```

### Real-world Examples

**Netflix**: Massive CDN (OpenConnect) for video streaming.

**Spotify**: CDN for music streaming and album art.

---

## Summary

Scalability patterns enable systems to:
- **Handle Growth**: Accommodate increasing load
- **Improve Performance**: Lower latency, higher throughput
- **Optimize Costs**: Efficient resource utilization
- **Ensure Availability**: Distribute load and eliminate SPOFs

### Pattern Selection Matrix

| Requirement | Pattern |
|-------------|---------|
| Variable traffic | Auto-Scaling |
| Distribute requests | Load Balancing |
| Large datasets | Sharding |
| Read-heavy workload | Read Replicas |
| Static content | CDN |
| Global users | Multi-region + CDN |

### FAANG Scalability

- **Amazon**: Auto-scaling handles Prime Day traffic spikes
- **Facebook**: Sharding for billions of users
- **Netflix**: CDN + auto-scaling for global streaming
- **Google**: Massive distributed systems (Spanner, Bigtable)
- **Uber**: Sharding + replication for ride data
