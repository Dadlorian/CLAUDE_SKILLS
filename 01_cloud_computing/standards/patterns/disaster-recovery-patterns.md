# Disaster Recovery Architecture Patterns

## Overview

Disaster Recovery (DR) patterns ensure business continuity by protecting applications and data from catastrophic failures, natural disasters, and regional outages. This guide covers proven DR strategies with varying levels of cost, complexity, and recovery capabilities.

## Table of Contents

1. [Backup and Restore](#backup-and-restore)
2. [Pilot Light](#pilot-light)
3. [Warm Standby](#warm-standby)
4. [Multi-Site Active-Active](#multi-site-active-active)
5. [Multi-Site Active-Passive](#multi-site-active-passive)
6. [Cross-Region Failover](#cross-region-failover)
7. [RPO and RTO Patterns](#rpo-and-rto-patterns)

## Key Metrics

**RTO (Recovery Time Objective)**: Maximum acceptable time to restore service after a disaster.

**RPO (Recovery Point Objective)**: Maximum acceptable data loss measured in time.

```
Cost vs Recovery Speed Spectrum:
Low Cost ←──────────────────────────────────→ High Cost
High RTO/RPO                          Low RTO/RPO

Backup    →    Pilot    →    Warm    →    Active
Restore        Light          Standby       Active

Hours         Minutes        Seconds       Zero
to Days       to Hours       to Minutes    Downtime
```

---

## 1. Backup and Restore

### Description

The most basic DR pattern: regularly backup data and restore when needed. Lowest cost but highest RTO/RPO.

### When to Use

- Non-critical applications
- Budget constraints
- Long RTO/RPO acceptable (hours to days)
- Compliance requires data retention
- Development/testing environments

### Architecture Diagram

```
Primary Region                    Backup Region
┌─────────────────┐              ┌─────────────────┐
│                 │              │                 │
│  ┌───────────┐  │              │  ┌───────────┐  │
│  │Application│  │              │  │           │  │
│  └─────┬─────┘  │              │  │  Backup   │  │
│        │        │              │  │  Storage  │  │
│  ┌─────▼─────┐  │   Periodic   │  │           │  │
│  │           │  │   Backup     │  │  ┌─────┐  │  │
│  │ Database  │  ├─────────────►│  │  │Data │  │  │
│  │           │  │              │  │  └─────┘  │  │
│  └───────────┘  │              │  │           │  │
│                 │              │  └───────────┘  │
│  ┌───────────┐  │              │                 │
│  │ File      │  │   Snapshots  │  ┌───────────┐  │
│  │ Storage   │  ├─────────────►│  │ Snapshots │  │
│  └───────────┘  │              │  └───────────┘  │
│                 │              │                 │
└─────────────────┘              └─────────────────┘

        ▲                                │
        │                                │
        │    Disaster Recovery           │
        │    Manual Restore              │
        └────────────────────────────────┘
```

### Implementation Example

```python
# backup_manager.py
import boto3
from datetime import datetime, timedelta
from typing import List, Dict
import json

class BackupManager:
    def __init__(self, primary_region: str, backup_region: str):
        self.primary_region = primary_region
        self.backup_region = backup_region
        self.s3_client = boto3.client('s3')
        self.rds_client = boto3.client('rds', region_name=primary_region)
        self.backup_rds = boto3.client('rds', region_name=backup_region)

    def create_database_snapshot(self, db_instance_id: str) -> str:
        """Create RDS snapshot"""
        snapshot_id = f"{db_instance_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        response = self.rds_client.create_db_snapshot(
            DBSnapshotIdentifier=snapshot_id,
            DBInstanceIdentifier=db_instance_id,
            Tags=[
                {'Key': 'BackupType', 'Value': 'Automated'},
                {'Key': 'Timestamp', 'Value': datetime.now().isoformat()}
            ]
        )

        print(f"Created snapshot: {snapshot_id}")
        return snapshot_id

    def copy_snapshot_to_backup_region(self, snapshot_id: str) -> str:
        """Copy snapshot to backup region"""
        source_snapshot_arn = f"arn:aws:rds:{self.primary_region}:123456789012:snapshot:{snapshot_id}"

        response = self.backup_rds.copy_db_snapshot(
            SourceDBSnapshotIdentifier=source_snapshot_arn,
            TargetDBSnapshotIdentifier=f"{snapshot_id}-backup",
            CopyTags=True,
            KmsKeyId='alias/aws/rds'  # Encrypt with KMS
        )

        print(f"Copying snapshot to {self.backup_region}")
        return response['DBSnapshot']['DBSnapshotIdentifier']

    def backup_to_s3(self, source_bucket: str, destination_bucket: str,
                    prefix: str = "") -> List[str]:
        """Backup S3 objects to another bucket/region"""
        backed_up_files = []

        # List objects
        paginator = self.s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=source_bucket, Prefix=prefix)

        for page in pages:
            if 'Contents' not in page:
                continue

            for obj in page['Contents']:
                key = obj['Key']

                # Copy to backup bucket
                copy_source = {'Bucket': source_bucket, 'Key': key}
                self.s3_client.copy_object(
                    CopySource=copy_source,
                    Bucket=destination_bucket,
                    Key=key,
                    StorageClass='GLACIER_IR',  # Use cheaper storage
                    ServerSideEncryption='AES256'
                )

                backed_up_files.append(key)

        return backed_up_files

    def restore_database_from_snapshot(self, snapshot_id: str,
                                      new_instance_id: str) -> Dict:
        """Restore RDS instance from snapshot"""
        response = self.backup_rds.restore_db_instance_from_db_snapshot(
            DBInstanceIdentifier=new_instance_id,
            DBSnapshotIdentifier=snapshot_id,
            DBInstanceClass='db.t3.medium',
            MultiAZ=True,
            PubliclyAccessible=False,
            Tags=[
                {'Key': 'RestoredFrom', 'Value': snapshot_id},
                {'Key': 'RestoreDate', 'Value': datetime.now().isoformat()}
            ]
        )

        return response['DBInstance']

    def cleanup_old_backups(self, db_instance_id: str, retention_days: int = 30):
        """Delete backups older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        # List snapshots
        snapshots = self.rds_client.describe_db_snapshots(
            DBInstanceIdentifier=db_instance_id,
            SnapshotType='manual'
        )

        for snapshot in snapshots['DBSnapshots']:
            create_time = snapshot['SnapshotCreateTime'].replace(tzinfo=None)

            if create_time < cutoff_date:
                snapshot_id = snapshot['DBSnapshotIdentifier']
                self.rds_client.delete_db_snapshot(
                    DBSnapshotIdentifier=snapshot_id
                )
                print(f"Deleted old snapshot: {snapshot_id}")


# Automated backup schedule using EventBridge
def lambda_handler(event, context):
    """Lambda function for automated backups"""
    backup_mgr = BackupManager(
        primary_region='us-east-1',
        backup_region='us-west-2'
    )

    # Backup database
    snapshot_id = backup_mgr.create_database_snapshot('production-db')

    # Copy to backup region
    backup_mgr.copy_snapshot_to_backup_region(snapshot_id)

    # Backup S3 data
    files = backup_mgr.backup_to_s3(
        source_bucket='production-data',
        destination_bucket='backup-data-us-west-2'
    )

    # Cleanup old backups
    backup_mgr.cleanup_old_backups('production-db', retention_days=30)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'snapshot': snapshot_id,
            'files_backed_up': len(files)
        })
    }
```

### Terraform Configuration

```hcl
# Automated backup configuration
resource "aws_backup_vault" "dr_vault" {
  name = "disaster-recovery-vault"

  tags = {
    Environment = "production"
    Purpose     = "DisasterRecovery"
  }
}

resource "aws_backup_plan" "daily_backup" {
  name = "daily-backup-plan"

  rule {
    rule_name         = "daily_backup_rule"
    target_vault_name = aws_backup_vault.dr_vault.name
    schedule          = "cron(0 2 * * ? *)"  # 2 AM daily

    lifecycle {
      delete_after = 30  # Retain for 30 days
      cold_storage_after = 7  # Move to cold storage after 7 days
    }

    copy_action {
      destination_vault_arn = aws_backup_vault.dr_vault_backup_region.arn

      lifecycle {
        delete_after = 90
        cold_storage_after = 30
      }
    }
  }
}

# Backup selection
resource "aws_backup_selection" "production_resources" {
  name         = "production-backup-selection"
  iam_role_arn = aws_iam_role.backup_role.arn
  plan_id      = aws_backup_plan.daily_backup.id

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = "true"
  }

  resources = [
    aws_db_instance.production.arn,
    aws_ebs_volume.data.arn
  ]
}
```

### Metrics

- **RTO**: 4-24 hours
- **RPO**: 24 hours (daily backups)
- **Cost**: Very Low ($$)
- **Complexity**: Low

### Trade-offs

**Pros:**
- Lowest cost option
- Simple to implement
- Works for any application
- Good for compliance/archival

**Cons:**
- Highest recovery time
- Most data loss potential
- Manual restore process
- Limited testing capability

### Anti-patterns

- **No Testing**: Never testing restore procedures
- **Single Location**: Keeping backups in same region/account
- **No Automation**: Manual backup processes
- **No Verification**: Not validating backup integrity
- **Inadequate Retention**: Not keeping backups long enough

### Real-world Examples

**Dropbox**: Uses backup and restore for user file versioning with 30-day retention.

**GitHub**: Implements automated backups with point-in-time recovery for repository data.

---

## 2. Pilot Light

### Description

Minimal version of infrastructure running in DR region. Core services (databases) replicated, but compute resources are minimal or off until needed.

### When to Use

- Moderate RTO/RPO requirements (minutes to hours)
- Cost-conscious but need faster recovery
- Database replication critical
- Can tolerate brief downtime

### Architecture Diagram

```
Primary Region (Active)          DR Region (Pilot Light)
┌─────────────────────┐         ┌─────────────────────┐
│                     │         │                     │
│  ┌───────────────┐  │         │  ┌───────────────┐  │
│  │               │  │         │  │               │  │
│  │ Load Balancer │  │         │  │ Load Balancer │  │
│  │    (Active)   │  │         │  │  (Standby)    │  │
│  └───────┬───────┘  │         │  └───────────────┘  │
│          │          │         │          │          │
│  ┌───────▼───────┐  │         │  ┌───────▼───────┐  │
│  │ EC2 Instances │  │         │  │  EC2 (Stopped)│  │
│  │   (Running)   │  │         │  │  AMI Ready    │  │
│  │   ████████    │  │         │  │               │  │
│  └───────┬───────┘  │         │  └───────┬───────┘  │
│          │          │         │          │          │
│  ┌───────▼───────┐  │  Real   │  ┌───────▼───────┐  │
│  │   Primary     │  │  Time   │  │   Read        │  │
│  │   Database    │  ├─Replica─┤  │   Replica     │  │
│  │   (Master)    │  ├────────►│  │   (Synced)    │  │
│  └───────────────┘  │         │  └───────────────┘  │
│                     │         │                     │
└─────────────────────┘         └─────────────────────┘

         Normal Operation           Disaster Occurs
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │  1. Promote │
                                    │  DB Replica │
                                    │  to Master  │
                                    ├─────────────┤
                                    │  2. Start   │
                                    │  EC2        │
                                    │  Instances  │
                                    ├─────────────┤
                                    │  3. Update  │
                                    │  DNS/Route  │
                                    │  53         │
                                    └─────────────┘
```

### Implementation Example

```python
# pilot_light_failover.py
import boto3
import time
from typing import List, Dict

class PilotLightFailover:
    def __init__(self, primary_region: str, dr_region: str):
        self.primary_region = primary_region
        self.dr_region = dr_region

        self.primary_ec2 = boto3.client('ec2', region_name=primary_region)
        self.dr_ec2 = boto3.client('ec2', region_name=dr_region)

        self.primary_rds = boto3.client('rds', region_name=primary_region)
        self.dr_rds = boto3.client('rds', region_name=dr_region)

        self.route53 = boto3.client('route53')

    def promote_read_replica(self, replica_identifier: str) -> Dict:
        """Promote read replica to standalone instance"""
        print(f"Promoting read replica: {replica_identifier}")

        response = self.dr_rds.promote_read_replica(
            DBInstanceIdentifier=replica_identifier
        )

        # Wait for promotion to complete
        waiter = self.dr_rds.get_waiter('db_instance_available')
        waiter.wait(DBInstanceIdentifier=replica_identifier)

        print(f"Replica promoted successfully")
        return response['DBInstance']

    def start_dr_instances(self, instance_ids: List[str]) -> List[Dict]:
        """Start stopped EC2 instances in DR region"""
        print(f"Starting {len(instance_ids)} EC2 instances")

        self.dr_ec2.start_instances(InstanceIds=instance_ids)

        # Wait for instances to be running
        waiter = self.dr_ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=instance_ids)

        instances = self.dr_ec2.describe_instances(
            InstanceIds=instance_ids
        )

        return instances['Reservations'][0]['Instances']

    def scale_auto_scaling_group(self, asg_name: str, desired_capacity: int):
        """Scale up auto-scaling group in DR region"""
        asg_client = boto3.client('autoscaling', region_name=self.dr_region)

        print(f"Scaling ASG {asg_name} to {desired_capacity}")

        asg_client.set_desired_capacity(
            AutoScalingGroupName=asg_name,
            DesiredCapacity=desired_capacity,
            HonorCooldown=False
        )

        # Wait for instances to be in service
        time.sleep(60)  # Give instances time to launch

    def update_dns_failover(self, hosted_zone_id: str,
                           record_name: str,
                           dr_endpoint: str):
        """Update Route 53 to point to DR region"""
        print(f"Updating DNS to point to DR endpoint: {dr_endpoint}")

        self.route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': record_name,
                            'Type': 'CNAME',
                            'TTL': 60,
                            'ResourceRecords': [
                                {'Value': dr_endpoint}
                            ]
                        }
                    }
                ]
            }
        )

        print("DNS updated successfully")

    def execute_failover(self, config: Dict) -> Dict:
        """Execute complete failover to DR region"""
        start_time = time.time()
        results = {}

        try:
            # Step 1: Promote database
            if 'db_replica' in config:
                db_result = self.promote_read_replica(config['db_replica'])
                results['database'] = {
                    'status': 'promoted',
                    'endpoint': db_result['Endpoint']['Address']
                }

            # Step 2: Start/scale compute
            if 'instance_ids' in config:
                instances = self.start_dr_instances(config['instance_ids'])
                results['instances'] = {
                    'count': len(instances),
                    'status': 'running'
                }

            if 'asg_name' in config:
                self.scale_auto_scaling_group(
                    config['asg_name'],
                    config['asg_capacity']
                )
                results['auto_scaling'] = {
                    'status': 'scaled',
                    'capacity': config['asg_capacity']
                }

            # Step 3: Update DNS
            if 'dns_config' in config:
                self.update_dns_failover(
                    config['dns_config']['hosted_zone_id'],
                    config['dns_config']['record_name'],
                    config['dns_config']['dr_endpoint']
                )
                results['dns'] = {'status': 'updated'}

            # Calculate recovery time
            recovery_time = time.time() - start_time
            results['recovery_time_seconds'] = recovery_time

            print(f"\nFailover completed in {recovery_time:.2f} seconds")
            return results

        except Exception as e:
            print(f"Failover failed: {e}")
            raise

    def test_failover(self, config: Dict) -> bool:
        """Test failover process without DNS change"""
        print("Starting failover test (non-destructive)")

        try:
            # Test database promotion (use test replica)
            test_replica = config.get('test_db_replica')
            if test_replica:
                self.promote_read_replica(test_replica)

            # Test instance startup
            test_instances = config.get('test_instance_ids', [])
            if test_instances:
                instances = self.start_dr_instances(test_instances)
                # Verify instances are healthy
                time.sleep(30)
                # Stop them again
                self.dr_ec2.stop_instances(InstanceIds=test_instances)

            print("Failover test completed successfully")
            return True

        except Exception as e:
            print(f"Failover test failed: {e}")
            return False


# AWS Lambda function for automated failover
def lambda_handler(event, context):
    """Automated failover trigger"""
    failover = PilotLightFailover(
        primary_region='us-east-1',
        dr_region='us-west-2'
    )

    config = {
        'db_replica': 'production-db-replica',
        'asg_name': 'production-asg-dr',
        'asg_capacity': 3,
        'dns_config': {
            'hosted_zone_id': 'Z1234567890ABC',
            'record_name': 'api.example.com',
            'dr_endpoint': 'dr-alb-123456.us-west-2.elb.amazonaws.com'
        }
    }

    results = failover.execute_failover(config)

    return {
        'statusCode': 200,
        'body': results
    }
```

### Terraform Configuration

```hcl
# Pilot Light Infrastructure

# DR Region Database (Read Replica)
resource "aws_db_instance" "dr_replica" {
  provider = aws.dr_region

  identifier = "production-db-replica"
  replicate_source_db = aws_db_instance.primary.arn

  instance_class = aws_db_instance.primary.instance_class
  multi_az       = true

  backup_retention_period = 7
  skip_final_snapshot     = false
  final_snapshot_identifier = "dr-replica-final-snapshot"

  tags = {
    Name        = "DR Read Replica"
    Environment = "production"
    DR          = "true"
  }
}

# Launch Template for DR instances
resource "aws_launch_template" "dr_template" {
  provider = aws.dr_region

  name_prefix   = "dr-instance-"
  image_id      = data.aws_ami.app_ami.id
  instance_type = "t3.medium"

  user_data = base64encode(templatefile("${path.module}/userdata.sh", {
    db_endpoint = aws_db_instance.dr_replica.endpoint
  }))

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "DR Instance"
      DR   = "true"
    }
  }
}

# Auto Scaling Group (starts at 0, scales up on failover)
resource "aws_autoscaling_group" "dr_asg" {
  provider = aws.dr_region

  name                = "production-asg-dr"
  vpc_zone_identifier = var.dr_private_subnets
  min_size            = 0
  max_size            = 10
  desired_capacity    = 0  # Starts at 0 for pilot light

  launch_template {
    id      = aws_launch_template.dr_template.id
    version = "$Latest"
  }

  health_check_type         = "ELB"
  health_check_grace_period = 300

  tag {
    key                 = "Name"
    value               = "DR Application Instance"
    propagate_at_launch = true
  }
}

# Route 53 Health Check
resource "aws_route53_health_check" "primary" {
  fqdn              = "api.example.com"
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = "3"
  request_interval  = "30"

  tags = {
    Name = "Primary Region Health Check"
  }
}

# CloudWatch Alarm for failover trigger
resource "aws_cloudwatch_metric_alarm" "primary_health" {
  alarm_name          = "primary-region-health-alarm"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HealthCheckStatus"
  namespace           = "AWS/Route53"
  period              = "60"
  statistic           = "Minimum"
  threshold           = "1"

  dimensions = {
    HealthCheckId = aws_route53_health_check.primary.id
  }

  alarm_actions = [aws_sns_topic.dr_failover.arn]
}
```

### Metrics

- **RTO**: 10-60 minutes
- **RPO**: Seconds to minutes (database replication lag)
- **Cost**: Low to Medium ($$-$$$)
- **Complexity**: Medium

### Trade-offs

**Pros:**
- Faster recovery than backup/restore
- Lower cost than warm standby
- Database always synchronized
- Can test failover process

**Cons:**
- Time needed to start compute resources
- Replication lag can cause data loss
- Requires automation for quick failover
- Some infrastructure always running

### Real-world Examples

**Pinterest**: Uses pilot light for disaster recovery with read replicas in multiple regions.

**Airbnb**: Implements pilot light pattern for core services with rapid scale-up capability.

---

## 3. Warm Standby

### Description

Scaled-down but fully functional version of production environment running in DR region. Can handle traffic immediately but at reduced capacity.

### When to Use

- Low RTO requirements (minutes)
- Mission-critical applications
- Can afford higher DR costs
- Need to serve reduced traffic immediately

### Architecture Diagram

```
Primary Region (Active)         DR Region (Warm Standby)
┌──────────────────────┐        ┌──────────────────────┐
│  ┌────────────────┐  │        │  ┌────────────────┐  │
│  │ Load Balancer  │  │        │  │ Load Balancer  │  │
│  │   (Active)     │  │        │  │   (Standby)    │  │
│  └────────┬───────┘  │        │  └────────┬───────┘  │
│           │          │        │           │          │
│  ┌────────▼───────┐  │        │  ┌────────▼───────┐  │
│  │ EC2 Instances  │  │        │  │ EC2 Instances  │  │
│  │   ██████████   │  │        │  │    ████        │  │
│  │   (10 nodes)   │  │        │  │   (2 nodes)    │  │
│  └────────┬───────┘  │        │  └────────┬───────┘  │
│           │          │        │           │          │
│  ┌────────▼───────┐  │ Async  │  ┌────────▼───────┐  │
│  │   Primary DB   │  │ Replic │  │  Standby DB    │  │
│  │   (Master)     │  ├───────►│  │  (Replica)     │  │
│  └────────────────┘  │        │  └────────────────┘  │
└──────────────────────┘        └──────────────────────┘

Route 53 Weighted/Failover Routing
        │
        ├──► 100% to Primary (Normal)
        │
        └──► 100% to DR (Failover)
```

### Metrics

- **RTO**: 1-10 minutes
- **RPO**: Seconds (near real-time replication)
- **Cost**: Medium to High ($$$-$$$$)
- **Complexity**: Medium-High

### Trade-offs

**Pros:**
- Very fast failover
- Can handle immediate traffic
- Regular testing possible
- Minimal data loss

**Cons:**
- Higher cost (always running)
- Resources underutilized normally
- More complex to maintain
- Syncing configuration changes

### Real-world Examples

**Netflix**: Runs warm standby across AWS regions for critical streaming services.

**Uber**: Implements warm standby for ride-matching and payment systems.

---

## 4. Multi-Site Active-Active

### Description

Multiple fully operational regions serving traffic simultaneously. No failover needed - traffic automatically routes to healthy regions.

### When to Use

- Zero downtime requirements
- Global user base
- Latency optimization critical
- Can handle distributed data challenges

### Architecture Diagram

```
                  ┌──────────────┐
                  │   Route 53   │
                  │ Geoproximity │
                  │   Routing    │
                  └──────┬───────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
     ┌────▼────┐    ┌───▼────┐    ┌───▼────┐
     │  US-EAST│    │ EU-WEST│    │ASIA-PAC│
     │ (Active)│    │(Active)│    │(Active)│
     └────┬────┘    └───┬────┘    └───┬────┘
          │             │              │
     ┌────▼────┐   ┌───▼────┐    ┌───▼────┐
     │   ALB   │   │  ALB   │    │  ALB   │
     └────┬────┘   └───┬────┘    └───┬────┘
          │            │              │
     ┌────▼────┐   ┌───▼────┐    ┌───▼────┐
     │  EC2    │   │  EC2   │    │  EC2   │
     │ ████████│   │████████│    │████████│
     └────┬────┘   └───┬────┘    └───┬────┘
          │            │              │
     ┌────▼────┐   ┌───▼────┐    ┌───▼────┐
     │  Aurora │   │ Aurora │    │ Aurora │
     │ Global  │◄──┤ Global ├───►│ Global │
     │Database │   │Database│    │Database│
     └─────────┘   └────────┘    └────────┘
              Cross-Region Replication
```

### Implementation Example

```python
# active_active_manager.py
import boto3
from typing import List, Dict

class ActiveActiveManager:
    def __init__(self, regions: List[str]):
        self.regions = regions
        self.route53 = boto3.client('route53')

    def create_global_database(self, cluster_id: str) -> Dict:
        """Create Aurora Global Database"""
        rds_primary = boto3.client('rds', region_name=self.regions[0])

        # Create global cluster
        response = rds_primary.create_global_cluster(
            GlobalClusterIdentifier=f"{cluster_id}-global",
            Engine='aurora-postgresql',
            EngineVersion='13.7',
            DatabaseName='production',
            StorageEncrypted=True
        )

        return response['GlobalCluster']

    def add_region_to_global_db(self, global_cluster_id: str,
                                region: str,
                                cluster_id: str):
        """Add secondary region to global database"""
        rds_secondary = boto3.client('rds', region_name=region)

        rds_secondary.create_db_cluster(
            DBClusterIdentifier=cluster_id,
            Engine='aurora-postgresql',
            GlobalClusterIdentifier=global_cluster_id,
            ReplicationSourceIdentifier=global_cluster_id
        )

    def setup_traffic_distribution(self, hosted_zone_id: str,
                                   domain: str,
                                   endpoints: Dict[str, str]):
        """Configure Route 53 for active-active routing"""

        changes = []

        # Create latency-based routing for each region
        for region, endpoint in endpoints.items():
            changes.append({
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': domain,
                    'Type': 'CNAME',
                    'SetIdentifier': f'Region-{region}',
                    'Region': region,
                    'TTL': 60,
                    'ResourceRecords': [{'Value': endpoint}],
                    'HealthCheckId': self._create_health_check(endpoint)
                }
            })

        self.route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={'Changes': changes}
        )

    def _create_health_check(self, endpoint: str) -> str:
        """Create health check for endpoint"""
        response = self.route53.create_health_check(
            HealthCheckConfig={
                'Type': 'HTTPS',
                'ResourcePath': '/health',
                'FullyQualifiedDomainName': endpoint,
                'Port': 443,
                'RequestInterval': 30,
                'FailureThreshold': 3
            }
        )
        return response['HealthCheck']['Id']
```

### Metrics

- **RTO**: 0 (no downtime)
- **RPO**: Near-zero (synchronous replication)
- **Cost**: Very High ($$$$$$)
- **Complexity**: Very High

### Trade-offs

**Pros:**
- Zero downtime
- Best user experience
- Geographic distribution
- Load balancing benefits

**Cons:**
- Highest cost
- Complex data consistency
- Difficult to test
- Operational complexity

### Real-world Examples

**Amazon.com**: Runs active-active across multiple regions for retail platform.

**Facebook/Meta**: Global active-active deployment across numerous datacenters.

**Google**: Active-active infrastructure for all major services (Search, Gmail, etc.).

---

## 5. Multi-Site Active-Passive

### Description

Full production environment in DR region but not serving traffic. Can be promoted to active instantly.

### Metrics

- **RTO**: 1-5 minutes
- **RPO**: Seconds
- **Cost**: Very High ($$$$$)
- **Complexity**: High

---

## 6. Cross-Region Failover

### Implementation with Terraform

```hcl
# Complete cross-region failover setup

# Primary Region Resources
provider "aws" {
  alias  = "primary"
  region = "us-east-1"
}

# DR Region Resources
provider "aws" {
  alias  = "dr"
  region = "us-west-2"
}

# Aurora Global Database
resource "aws_rds_global_cluster" "main" {
  provider = aws.primary

  global_cluster_identifier = "production-global-db"
  engine                    = "aurora-postgresql"
  engine_version            = "13.7"
  database_name             = "production"
  storage_encrypted         = true
}

# Primary cluster
resource "aws_rds_cluster" "primary" {
  provider = aws.primary

  cluster_identifier        = "production-primary"
  engine                    = aws_rds_global_cluster.main.engine
  engine_version            = aws_rds_global_cluster.main.engine_version
  global_cluster_identifier = aws_rds_global_cluster.main.id
  master_username           = var.db_username
  master_password           = var.db_password
  database_name             = "production"

  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
}

# DR cluster
resource "aws_rds_cluster" "dr" {
  provider = aws.dr

  cluster_identifier        = "production-dr"
  engine                    = aws_rds_global_cluster.main.engine
  engine_version            = aws_rds_global_cluster.main.engine_version
  global_cluster_identifier = aws_rds_global_cluster.main.id

  depends_on = [aws_rds_cluster.primary]
}
```

---

## 7. RPO and RTO Patterns

### Pattern Selection Matrix

```
┌────────────────────────────────────────────────────┐
│  RTO/RPO Requirements → DR Pattern Selection       │
├────────────────────────────────────────────────────┤
│                                                    │
│  RTO: Days     │  Backup and Restore              │
│  RPO: Days     │  Cost: $                         │
│                │                                   │
│  RTO: Hours    │  Pilot Light                     │
│  RPO: Minutes  │  Cost: $$                        │
│                │                                   │
│  RTO: Minutes  │  Warm Standby                    │
│  RPO: Seconds  │  Cost: $$$                       │
│                │                                   │
│  RTO: Seconds  │  Active-Passive                  │
│  RPO: Seconds  │  Cost: $$$$                      │
│                │                                   │
│  RTO: Zero     │  Active-Active                   │
│  RPO: Zero     │  Cost: $$$$$                     │
│                │                                   │
└────────────────────────────────────────────────────┘
```

### Cost Comparison

| Pattern | Monthly Cost (Estimate) | % of Production Cost |
|---------|------------------------|---------------------|
| Backup & Restore | $500 - $2K | 5-10% |
| Pilot Light | $2K - $10K | 15-25% |
| Warm Standby | $10K - $50K | 40-60% |
| Active-Passive | $50K - $100K | 70-90% |
| Active-Active | $100K+ | 150-200% |

---

## Tool Recommendations

### Disaster Recovery Tools

**AWS:**
- AWS Backup
- AWS Elastic Disaster Recovery (DRS)
- Route 53 Health Checks
- CloudEndure (acquired by AWS)

**Azure:**
- Azure Site Recovery (ASR)
- Azure Backup
- Traffic Manager

**GCP:**
- Google Cloud Backup and DR
- Cloud Storage Transfer Service
- Cloud Load Balancing

**Multi-Cloud:**
- Zerto
- Veeam Backup & Replication
- Commvault
- Rubrik

### Monitoring & Orchestration

- Terraform/Pulumi (IaC)
- Ansible (automation)
- PagerDuty (incident management)
- Datadog/New Relic (observability)

---

## Testing & Validation

### DR Testing Schedule

```yaml
# dr-testing-schedule.yaml
testing_schedule:
  backup_restore_test:
    frequency: monthly
    duration: 4_hours
    success_criteria:
      - RTO_met: true
      - data_integrity: 100%

  pilot_light_test:
    frequency: quarterly
    duration: 2_hours
    success_criteria:
      - failover_time: < 15_minutes
      - data_loss: < 1_minute

  warm_standby_test:
    frequency: quarterly
    duration: 1_hour
    success_criteria:
      - failover_time: < 5_minutes
      - traffic_handling: 100%

  active_active_test:
    frequency: monthly
    duration: continuous
    success_criteria:
      - automatic_failover: true
      - zero_downtime: true
```

---

## Summary

Disaster recovery is critical for business continuity. Choose the pattern that balances your:

- **Recovery requirements** (RTO/RPO)
- **Budget constraints**
- **Operational complexity tolerance**
- **Regulatory requirements**

Most organizations use a **tiered approach**:
- Critical systems: Active-Active or Warm Standby
- Important systems: Pilot Light
- Non-critical systems: Backup and Restore

**Key Success Factors:**
1. Automate everything
2. Test regularly
3. Document procedures
4. Train teams
5. Monitor continuously
6. Review and improve

Remember: **A DR plan is only as good as your last successful test!**
