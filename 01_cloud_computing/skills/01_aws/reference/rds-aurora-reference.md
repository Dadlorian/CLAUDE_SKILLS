# Amazon RDS and Aurora Reference

## RDS Overview

Amazon RDS is a managed relational database service supporting multiple database engines with automated provisioning, patching, backup, and recovery.

### Supported Database Engines

| Engine | Latest Version | Use Case | License |
|--------|---------------|----------|---------|
| Aurora MySQL | 3.04.0 (MySQL 8.0) | High performance, AWS-native | Commercial/GPL |
| Aurora PostgreSQL | 15.3 | High performance, AWS-native | PostgreSQL |
| MySQL | 8.0.35 | Open source applications | GPL |
| PostgreSQL | 16.1 | Advanced features, compliance | PostgreSQL |
| MariaDB | 10.11.6 | MySQL fork, open source | GPL |
| Oracle | 19c, 21c | Enterprise apps, legacy | BYOL/License Included |
| SQL Server | 2022, 2019, 2017 | Microsoft ecosystem | BYOL/License Included |

## Amazon Aurora Architecture

### Aurora MySQL/PostgreSQL Features

**Performance:**
- 5x throughput of MySQL, 3x PostgreSQL
- Up to 128 TiB automatic storage scaling
- Up to 15 read replicas with <10ms replica lag
- 6-way replication across 3 AZs
- Self-healing storage with continuous backups to S3

**High Availability:**
- 99.99% availability SLA
- Automatic failover in <30 seconds
- Zero-downtime patching
- Backtrack (MySQL): Rewind database to specific point in time
- Global Database: <1 second RPO, <1 minute RTO for cross-region DR

### Aurora Cluster Architecture

```
                          [Cluster Endpoint]
                                  ↓
                        [Primary DB Instance]
                                  ↓
                    [Aurora Shared Storage]
                   /        |         |      \
            [AZ-1]      [AZ-2]     [AZ-3]   [Replica Storage]
                                                    ↓
                                          [Reader Endpoint]
                                                    ↓
                        ┌────────────────┬────────────────┐
                [Read Replica 1]  [Read Replica 2]  [Read Replica N]
```

**Endpoints:**
- **Cluster Endpoint**: Always points to primary (write) instance
- **Reader Endpoint**: Load balances across read replicas
- **Custom Endpoints**: Route to specific instances based on tags
- **Instance Endpoint**: Connect to specific instance directly

### Aurora Storage

**Architecture:**
- Distributed, fault-tolerant, self-healing storage
- 6 copies across 3 AZs
- Continuous backup to Amazon S3
- Can lose 2 copies for writes, 3 copies for reads

**Scaling:**
- Automatic growth in 10 GiB increments
- No downtime during storage scaling
- No performance impact during backups
- Maximum size: 128 TiB (Aurora), 64 TiB (RDS)

**I/O Performance:**
```
Aurora I/O Optimization:
- Standard: Pay per million I/O requests ($0.20/million)
- I/O-Optimized: No I/O charges, higher storage cost (better for high I/O)

Break-even calculation:
- I/O-Optimized worth it if: Monthly I/O cost > Storage cost increase
- Example: >7.8 million I/O per GB/month
```

## Aurora Serverless v2

### Features
- Instantly scales from 0.5 ACU to 128 ACU
- Fine-grained scaling in 0.5 ACU increments
- Sub-second scaling response
- Pay only for resources used (per-second billing)
- Compatible with provisioned Aurora features

### Aurora Capacity Units (ACU)
```
1 ACU = approximately:
- 2 GiB RAM
- Corresponding CPU
- Networking

Pricing (us-east-1):
- Aurora MySQL: $0.12 per ACU-hour
- Aurora PostgreSQL: $0.12 per ACU-hour
- Storage: $0.10 per GB-month
- I/O: $0.20 per million requests
```

### Configuration Example
```python
import boto3

rds = boto3.client('rds')

# Create Aurora Serverless v2 cluster
response = rds.create_db_cluster(
    DBClusterIdentifier='my-serverless-cluster',
    Engine='aurora-mysql',
    EngineVersion='8.0.mysql_aurora.3.04.0',
    MasterUsername='admin',
    MasterUserPassword='SecurePassword123!',
    DatabaseName='myapp',
    ServerlessV2ScalingConfiguration={
        'MinCapacity': 0.5,
        'MaxCapacity': 16
    },
    EnableHttpEndpoint=True,  # Data API for serverless apps
    BackupRetentionPeriod=7,
    PreferredBackupWindow='03:00-04:00',
    PreferredMaintenanceWindow='mon:04:00-mon:05:00',
    StorageEncrypted=True
)

# Add Serverless v2 instance
rds.create_db_instance(
    DBInstanceIdentifier='my-serverless-instance',
    DBInstanceClass='db.serverless',
    Engine='aurora-mysql',
    DBClusterIdentifier='my-serverless-cluster'
)
```

### Use Cases
- Variable workloads (dev/test, staging, infrequently used apps)
- Multi-tenant applications (scaling per tenant)
- New applications with unknown capacity needs
- Intermittent workloads (batch processing, reporting)

## RDS Multi-AZ Deployments

### Standard Multi-AZ (Synchronous Replication)

```
    [Primary DB Instance - AZ1]
              ↓ Sync Replication
    [Standby DB Instance - AZ2]
              ↓
      [Automatic Failover]
```

**Features:**
- Synchronous replication to standby in different AZ
- Automatic failover (1-2 minutes)
- Standby not accessible for reads
- Zero data loss during failover
- Automatic backups from standby (no I/O impact on primary)

### Multi-AZ DB Cluster (Readable Standbys)

```
    [Writer DB Instance - AZ1]
         ↓             ↓
    [Reader AZ2]  [Reader AZ3]
```

**Features (MySQL/PostgreSQL only):**
- 2 readable standby instances
- Faster failover (typically <35 seconds)
- Up to 2x write performance vs standard Multi-AZ
- Read from standbys to scale read workload
- Available for db.m5d, db.m6gd, db.r5d, db.r6gd instance types

**Comparison:**
```
                    Standard Multi-AZ    Multi-AZ Cluster
Readable standbys:       No                   Yes (2)
Failover time:         1-2 min              <35 sec
Write performance:     Baseline             Up to 2x
Read scaling:          No                   Yes
Cost:                  Lower                ~2x higher
```

## Read Replicas

### Cross-Region Read Replicas

```
Primary Region (us-east-1):
    [Primary DB Instance]
         ↓ Async Replication
Secondary Region (eu-west-1):
    [Read Replica]
```

**Capabilities:**
- Asynchronous replication (seconds of lag)
- Up to 5 read replicas per primary (Aurora: 15)
- Can be promoted to standalone DB
- Cross-region disaster recovery
- Serve read traffic closer to users
- No replication charge within same region
- Cross-region replication: data transfer costs apply

**Promotion:**
```bash
# Promote read replica to standalone database
aws rds promote-read-replica \
    --db-instance-identifier my-read-replica \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00"
```

## Backup and Recovery

### Automated Backups

**Features:**
- Daily full snapshot + transaction logs
- Point-in-time recovery (PITR) to any second
- Retention: 0-35 days (default 7 days, 0 disables)
- Stored in S3
- No performance impact (uses Multi-AZ standby or Aurora storage)
- Deleted when DB instance is deleted (unless final snapshot created)

**Configuration:**
```sql
-- Enable automated backups
MODIFY DB INSTANCE my-database
    BACKUP_RETENTION_PERIOD 30
    PREFERRED_BACKUP_WINDOW '03:00-04:00'
    PREFERRED_MAINTENANCE_WINDOW 'sun:04:00-sun:05:00';
```

### Manual Snapshots

**Features:**
- User-initiated full snapshots
- Retained until explicitly deleted
- Can copy across regions
- Can share with other AWS accounts
- Used for backup before major changes

**Creating Snapshots:**
```bash
# Create manual snapshot
aws rds create-db-snapshot \
    --db-instance-identifier production-db \
    --db-snapshot-identifier prod-before-migration-2024-01-15

# Copy snapshot to another region
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier arn:aws:rds:us-east-1:123456789012:snapshot:prod-snapshot \
    --target-db-snapshot-identifier prod-snapshot-replica \
    --region eu-west-1 \
    --kms-key-id arn:aws:kms:eu-west-1:123456789012:key/abc-123

# Share snapshot with another account
aws rds modify-db-snapshot-attribute \
    --db-snapshot-identifier shared-snapshot \
    --attribute-name restore \
    --values-to-add '["123456789012"]'
```

### Aurora Backtrack

**MySQL Only:**
- Rewind database to specific point in time
- No need to restore from backup
- Completes in minutes
- Multiple backtrack operations per day
- Retention: 0-72 hours

```bash
# Backtrack database to 1 hour ago
aws rds backtrack-db-cluster \
    --db-cluster-identifier my-cluster \
    --backtrack-to "$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ)"
```

### Point-in-Time Recovery (PITR)

```bash
# Restore to specific time
aws rds restore-db-instance-to-point-in-time \
    --source-db-instance-identifier original-db \
    --target-db-instance-identifier restored-db \
    --restore-time 2024-01-15T12:30:00Z

# Restore to latest restorable time
aws rds restore-db-instance-to-point-in-time \
    --source-db-instance-identifier original-db \
    --target-db-instance-identifier restored-db \
    --use-latest-restorable-time
```

## Performance Optimization

### Instance Classes

**General Purpose (T, M classes):**
```
db.t4g.micro    - 2 vCPU, 1 GiB RAM, Burstable
db.t4g.medium   - 2 vCPU, 4 GiB RAM, Burstable
db.m6g.large    - 2 vCPU, 8 GiB RAM
db.m6g.xlarge   - 4 vCPU, 16 GiB RAM
db.m6g.2xlarge  - 8 vCPU, 32 GiB RAM
db.m7g.16xlarge - 64 vCPU, 256 GiB RAM
```

**Memory Optimized (R, X classes):**
```
db.r6g.large     - 2 vCPU, 16 GiB RAM
db.r6g.xlarge    - 4 vCPU, 32 GiB RAM
db.r6g.4xlarge   - 16 vCPU, 128 GiB RAM
db.r7g.16xlarge  - 64 vCPU, 512 GiB RAM
db.x2g.xlarge    - 4 vCPU, 64 GiB RAM (1:16 ratio)
```

**Graviton (g suffix) Benefits:**
- Up to 35% price-performance improvement
- ARM-based architecture
- Lower power consumption
- Available for: Aurora, PostgreSQL, MySQL, MariaDB

### Storage Types

**Aurora:**
- Single storage type (SSD)
- Auto-scaling, distributed storage
- No storage type selection needed

**RDS (Non-Aurora):**

1. **General Purpose SSD (gp3)** - Default
   - 3,000-16,000 IOPS baseline
   - 125-1,000 MB/s throughput
   - $0.115 per GB-month
   - Best for: Most workloads

2. **General Purpose SSD (gp2)** - Previous generation
   - 3 IOPS per GB (min 100, max 16,000)
   - Burst to 3,000 IOPS
   - $0.115 per GB-month

3. **Provisioned IOPS SSD (io1/io2)**
   - Up to 256,000 IOPS (io2 Block Express)
   - Up to 4,000 MB/s throughput
   - 50:1 IOPS to GB ratio
   - $0.125 per GB-month + $0.10 per provisioned IOPS
   - Best for: I/O intensive, latency-sensitive workloads

4. **Magnetic (Standard)** - Legacy, not recommended
   - 100 IOPS average
   - $0.10 per GB-month

### Parameter Groups

**Key Parameters for Performance:**

**MySQL/Aurora MySQL:**
```ini
# Connection Management
max_connections = 1000              # Based on instance memory
max_connect_errors = 100

# Buffer Pool (70-80% of RAM for dedicated DB server)
innodb_buffer_pool_size = 24G      # For 32 GB instance
innodb_buffer_pool_instances = 8

# Query Cache (Deprecated in MySQL 8.0)
query_cache_type = 0
query_cache_size = 0

# InnoDB Settings
innodb_flush_log_at_trx_commit = 2  # 1 for ACID, 2 for performance
innodb_log_file_size = 512M
innodb_flush_method = O_DIRECT

# Slow Query Log
slow_query_log = 1
long_query_time = 2
log_queries_not_using_indexes = 1
```

**PostgreSQL/Aurora PostgreSQL:**
```ini
# Connection Management
max_connections = 500

# Memory Settings
shared_buffers = 8GB               # 25% of RAM
effective_cache_size = 24GB        # 75% of RAM
work_mem = 64MB                    # Per operation
maintenance_work_mem = 512MB

# WAL Settings
wal_buffers = 16MB
min_wal_size = 1GB
max_wal_size = 4GB
wal_compression = on

# Query Planning
random_page_cost = 1.1             # SSD
effective_io_concurrency = 200

# Monitoring
log_min_duration_statement = 1000  # Log queries > 1 second
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

### Performance Insights

**Features:**
- Visual dashboard of database load
- Identify performance bottlenecks
- Free for 7 days retention (paid for longer)
- Available for all RDS engines

**Key Metrics:**
- Database load (AAS - Average Active Sessions)
- Top SQL queries by load
- Top wait events
- Top users, hosts, databases

**API Access:**
```python
import boto3

pi = boto3.client('pi')

# Get resource metrics
response = pi.get_resource_metrics(
    ServiceType='RDS',
    Identifier='db-ABCDEFGHIJKLMNOP',
    MetricQueries=[
        {
            'Metric': 'db.load.avg',
            'GroupBy': {'Group': 'db.wait_event'}
        }
    ],
    StartTime='2024-01-15T00:00:00Z',
    EndTime='2024-01-15T23:59:59Z',
    PeriodInSeconds=3600
)
```

### Enhanced Monitoring

**Metrics (1-60 second granularity):**
- OS processes
- CPU utilization
- Memory usage
- File system usage
- Disk I/O
- Network traffic

**CloudWatch Integration:**
```python
import boto3

cloudwatch = boto3.client('cloudwatch')

# Get CPU utilization
response = cloudwatch.get_metric_statistics(
    Namespace='AWS/RDS',
    MetricName='CPUUtilization',
    Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': 'production-db'}],
    StartTime='2024-01-15T00:00:00Z',
    EndTime='2024-01-15T23:59:59Z',
    Period=300,
    Statistics=['Average', 'Maximum']
)
```

## Security

### Encryption

**At Rest:**
- AES-256 encryption using AWS KMS
- Encrypt new DB: specify KMS key during creation
- Encrypt existing: create encrypted snapshot, restore
- Includes backups, snapshots, replicas, logs

**In Transit:**
- SSL/TLS for connections
- Force SSL in parameter group:
  - MySQL: `require_secure_transport = 1`
  - PostgreSQL: `rds.force_ssl = 1`

**Connection Example:**
```python
import pymysql
import ssl

# MySQL with SSL
connection = pymysql.connect(
    host='mydb.cluster-abc.us-east-1.rds.amazonaws.com',
    user='admin',
    password='SecurePassword123!',
    database='myapp',
    ssl={'ssl_ca': '/path/to/rds-ca-bundle.pem'}
)

# PostgreSQL with SSL
import psycopg2
connection = psycopg2.connect(
    host='mydb.cluster-abc.us-east-1.rds.amazonaws.com',
    user='admin',
    password='SecurePassword123!',
    database='myapp',
    sslmode='verify-full',
    sslrootcert='/path/to/rds-ca-bundle.pem'
)
```

### IAM Database Authentication

**Benefits:**
- No passwords in code
- Centralized access management
- Encryption in transit enforced
- 15-minute token lifetime

**Enable and Connect:**
```python
import boto3
import pymysql

# Generate auth token
rds = boto3.client('rds')
token = rds.generate_db_auth_token(
    DBHostname='mydb.cluster-abc.us-east-1.rds.amazonaws.com',
    Port=3306,
    DBUsername='iam_user',
    Region='us-east-1'
)

# Connect using token as password
connection = pymysql.connect(
    host='mydb.cluster-abc.us-east-1.rds.amazonaws.com',
    user='iam_user',
    password=token,
    database='myapp',
    ssl={'ssl_ca': '/path/to/rds-ca-bundle.pem'}
)
```

**Required IAM Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "rds-db:connect",
    "Resource": "arn:aws:rds-db:us-east-1:123456789012:dbuser:cluster-ABCDEFGH/iam_user"
  }]
}
```

### Network Isolation

**Best Practices:**
- Deploy in private subnets
- Use DB subnet groups (minimum 2 AZs)
- Security groups allow only required sources
- No public accessibility for production
- Use VPC endpoints for AWS service access
- PrivateLink for cross-VPC access

## Aurora Global Database

### Architecture
```
Primary Region (us-east-1):
    [Primary Cluster]
         ↓ <1 second replication
Secondary Region (ap-southeast-1):
    [Secondary Cluster] (read-only)
         ↓ Can be promoted
    [Promoted Primary] (after disaster)
```

### Features
- Up to 5 secondary regions
- <1 second replication lag
- <1 minute RTO (recovery time objective)
- <1 second RPO (recovery point objective)
- Read from secondary regions (global reads)
- Managed cross-region replication

### Disaster Recovery
```bash
# Promote secondary region during DR
aws rds failover-global-cluster \
    --global-cluster-identifier my-global-cluster \
    --target-db-cluster-identifier arn:aws:rds:ap-southeast-1:123456789012:cluster:secondary-cluster
```

This comprehensive reference covers RDS and Aurora for production database deployments. For specific engine documentation, consult AWS RDS and Aurora documentation.
