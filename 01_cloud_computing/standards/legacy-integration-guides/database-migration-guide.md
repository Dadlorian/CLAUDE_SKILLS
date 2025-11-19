# Database Migration to Cloud Guide

## Table of Contents
1. [Overview](#overview)
2. [Migration Strategies](#migration-strategies)
3. [Cloud Database Services](#cloud-database-services)
4. [Migration Methodologies](#migration-methodologies)
5. [Risk Mitigation](#risk-mitigation)
6. [Rollback Plans](#rollback-plans)
7. [Case Studies](#case-studies)
8. [Tool Recommendations](#tool-recommendations)

## Overview

Database migration to the cloud is one of the most critical and complex aspects of cloud transformation. Databases are the foundation of enterprise applications, containing business-critical data that must be migrated with zero data loss while maintaining availability and performance.

### Migration Drivers

**Business Benefits**:
- Reduced total cost of ownership (TCO)
- Elimination of hardware refresh cycles
- Pay-as-you-go pricing model
- Global availability and disaster recovery
- Faster time to market for new features

**Technical Benefits**:
- Automated backups and point-in-time recovery
- High availability and fault tolerance
- Automated patching and updates
- Elastic scalability
- Advanced features (read replicas, multi-region)

### Migration Challenges

**Technical Challenges**:
- Data volume and transfer time
- Downtime constraints
- Schema compatibility
- Feature parity
- Performance optimization
- Application dependencies

**Business Challenges**:
- Risk aversion for mission-critical data
- Compliance and regulatory requirements
- Cost management
- Skills gap
- Vendor lock-in concerns

## Migration Strategies

### 1. Homogeneous Migration

**Definition**: Migrating to the same database engine in the cloud (e.g., Oracle to Oracle, MySQL to MySQL).

**Advantages**:
- Minimal application changes
- Proven compatibility
- Lower risk
- Faster migration
- Familiar administration

**Disadvantages**:
- May not optimize costs
- Limited feature improvements
- Potential licensing costs (Oracle, SQL Server)

**Common Paths**:
```
On-Premises → Cloud
- Oracle → Oracle on EC2/RDS
- SQL Server → SQL Server on Azure VM/RDS/Azure SQL
- MySQL → MySQL on RDS/Azure Database
- PostgreSQL → PostgreSQL on RDS/Azure/Cloud SQL
- MongoDB → MongoDB Atlas
```

### 2. Heterogeneous Migration

**Definition**: Migrating to a different database engine (e.g., Oracle to PostgreSQL, SQL Server to Aurora).

**Advantages**:
- Cost optimization (eliminate licensing)
- Cloud-native features
- Modern capabilities
- Vendor flexibility

**Disadvantages**:
- Higher complexity
- Schema conversion required
- Application code changes
- Thorough testing needed
- Longer timeline

**Common Paths**:
```
Commercial → Open Source
- Oracle → PostgreSQL/Aurora PostgreSQL
- SQL Server → PostgreSQL/MySQL
- DB2 → PostgreSQL

Relational → NoSQL
- Oracle → DynamoDB
- SQL Server → Cosmos DB
- MySQL → DocumentDB

Legacy → Modern
- Mainframe DB2 → Aurora PostgreSQL
- Informix → PostgreSQL
```

### 3. Minimal Downtime Migration

**Definition**: Migrating with near-zero downtime using continuous replication.

**Approaches**:

**A. Change Data Capture (CDC)**
```
Source Database
    ↓ (Initial Full Load)
Target Database
    ↓ (Ongoing Replication via CDC)
Synchronized Databases
    ↓ (Cutover)
Production on Target
```

**B. Logical Replication**
```
Source Database
    ↓ (Transaction Log Streaming)
Target Database
    ↓ (Apply Changes)
Near Real-time Sync
```

**C. Dual Writes**
```
Application
    ↓
Write to Both Databases
    ├─ Source (Primary)
    └─ Target (Secondary)
    ↓
Validate Consistency
    ↓
Switch Primary to Target
```

### 4. Big Bang Migration

**Definition**: Complete database migration during a planned maintenance window.

**When to Use**:
- Small databases (<100 GB)
- Acceptable downtime window (4+ hours)
- Minimal dependencies
- Testing thoroughly completed

**Process**:
```
T-4 hours: Stop application writes
T-3 hours: Final backup
T-2 hours: Begin data transfer
T-1 hour: Data validation
T-0: Switch application to cloud database
T+1: Monitoring and validation
```

## Cloud Database Services

### AWS Database Services

#### 1. Amazon RDS (Relational Database Service)

**Supported Engines**:
- MySQL
- PostgreSQL
- MariaDB
- Oracle
- SQL Server

**Key Features**:
- Automated backups (35-day retention)
- Multi-AZ deployment for HA
- Read replicas for scalability
- Automated patching
- Performance Insights
- Enhanced monitoring

**Best For**:
- Traditional relational workloads
- Lift-and-shift migrations
- Applications requiring specific engine versions

**Sizing Guidance**:
```
Instance Types:
- db.t3: Burstable, dev/test (2-8 vCPU)
- db.m6g: General purpose (1-64 vCPU)
- db.r6g: Memory optimized (1-64 vCPU)
- db.x2g: Extreme memory (4-64 vCPU)

Storage:
- General Purpose SSD (gp3): 20 GB - 64 TB
- Provisioned IOPS (io1): High performance
- Magnetic: Legacy (not recommended)
```

#### 2. Amazon Aurora

**Variants**:
- Aurora MySQL (compatible with MySQL 5.7, 8.0)
- Aurora PostgreSQL (compatible with PostgreSQL 11, 12, 13, 14, 15)

**Key Features**:
- 5x faster than MySQL, 3x faster than PostgreSQL
- Up to 15 read replicas
- Storage auto-scales to 128 TB
- Continuous backup to S3
- Global Database (multi-region)
- Serverless option
- Parallel Query for analytics

**Best For**:
- High performance requirements
- MySQL/PostgreSQL migrations
- Global applications
- Variable workloads (Aurora Serverless)

**Architecture**:
```
Application
    ↓
Aurora Cluster Endpoint
    ├─ Writer Instance (Primary)
    └─ Reader Instances (0-15 Replicas)
    ↓
Shared Storage (6 copies across 3 AZs)
```

#### 3. Amazon DynamoDB

**Type**: NoSQL, key-value and document database

**Key Features**:
- Fully managed, serverless
- Single-digit millisecond latency
- Unlimited throughput and storage
- Global Tables (multi-region)
- Point-in-time recovery
- Auto-scaling

**Best For**:
- Web-scale applications
- IoT and mobile apps
- Gaming leaderboards
- Session stores
- Shopping carts

**Migration From**:
- MongoDB
- Cassandra
- Oracle (selective tables)
- SQL Server (selective tables)

### Azure Database Services

#### 4. Azure SQL Database

**Deployment Options**:
- Single Database: Isolated database
- Elastic Pool: Shared resources for multiple databases
- Managed Instance: Near 100% SQL Server compatibility

**Key Features**:
- Hyperscale tier (100 TB)
- Serverless compute
- Advanced threat protection
- Intelligent performance
- Automatic tuning

**Best For**:
- SQL Server migrations
- SaaS applications
- Modern cloud apps

**Tiers**:
```
DTU Model:
- Basic: Light workloads
- Standard: General purpose
- Premium: IO-intensive

vCore Model:
- General Purpose: Balanced
- Business Critical: Low latency, high IOPS
- Hyperscale: Large databases
```

#### 5. Azure Database for PostgreSQL/MySQL

**Deployment Options**:
- Single Server: Simple deployment
- Flexible Server: Advanced configuration
- Hyperscale (Citus): Distributed PostgreSQL

**Key Features**:
- High availability (99.99% SLA)
- Automated backups
- Intelligent performance
- Advanced threat protection

**Best For**:
- PostgreSQL/MySQL migrations
- Open-source preferences
- Hybrid scenarios

#### 6. Azure Cosmos DB

**Type**: Multi-model NoSQL database

**APIs Supported**:
- Core (SQL) API
- MongoDB API
- Cassandra API
- Gremlin (Graph) API
- Table API

**Key Features**:
- Global distribution (turnkey)
- 99.999% availability SLA
- <10ms latency (P99)
- Multiple consistency models
- Automatic indexing

**Best For**:
- Globally distributed apps
- Multi-model requirements
- Mission-critical applications
- IoT and real-time analytics

### Google Cloud Database Services

#### 7. Cloud SQL

**Supported Engines**:
- MySQL
- PostgreSQL
- SQL Server

**Key Features**:
- Automated backups and replication
- High availability configuration
- Read replicas
- Private IP connectivity
- Data encryption at rest and in transit

**Best For**:
- Standard database workloads
- Existing MySQL/PostgreSQL apps
- Regional applications

#### 8. Cloud Spanner

**Type**: Horizontally scalable, globally distributed relational database

**Key Features**:
- 99.999% availability
- ACID transactions
- SQL support
- Automatic sharding
- Global scale

**Best For**:
- Mission-critical applications
- Global scale requirements
- Financial services
- Gaming leaderboards

#### 9. Firestore / Datastore

**Type**: NoSQL document database

**Key Features**:
- Real-time updates
- Offline support
- Automatic scaling
- Strong consistency

**Best For**:
- Mobile and web apps
- Real-time synchronization
- Serverless applications

## Migration Methodologies

### Phase 1: Assessment and Planning

#### Discovery
```
Database Inventory:
- Database engine and version
- Database size (data + indexes)
- Number of databases and tables
- Transaction volume (TPS)
- Connection count
- Peak usage patterns
- Backup and recovery requirements
```

#### Compatibility Assessment

**Schema Analysis**:
```sql
-- Example: Assess schema compatibility
-- Identify features that may not translate

-- Oracle-specific features
SELECT * FROM user_objects WHERE object_type = 'PACKAGE';
SELECT * FROM user_mviews; -- Materialized views
SELECT * FROM user_sequences;

-- SQL Server-specific features
SELECT * FROM sys.procedures WHERE type = 'P';
SELECT * FROM sys.triggers;
SELECT * FROM sys.xml_schema_collections;
```

**Tool-Based Assessment**:
```
AWS Schema Conversion Tool (SCT):
1. Connect to source database
2. Create database migration assessment report
3. Review incompatibilities
4. Estimate effort
5. Export assessment report
```

#### Sizing and Cost Estimation

**AWS RDS Sizing**:
```python
# Calculate RDS instance size
source_cpu = 16  # cores
source_memory = 128  # GB
source_iops = 10000
source_storage = 2000  # GB

# RDS instance mapping
if source_memory > 64:
    instance_type = "db.r6g.4xlarge"  # 16 vCPU, 128 GB
else:
    instance_type = "db.m6g.2xlarge"  # 8 vCPU, 32 GB

# Storage calculation
storage_type = "gp3"  # General Purpose SSD
storage_size = source_storage * 1.2  # 20% buffer
iops = max(3000, source_iops)  # gp3 baseline 3000 IOPS
```

**Cost Estimation**:
```
Monthly Cost Components:
1. Compute: Instance type × hours
2. Storage: GB × $0.115/month (gp3)
3. IOPS: Provisioned IOPS × $0.20/month
4. Backup storage: GB × $0.095/month
5. Data transfer: GB out × $0.09/GB
6. License (if applicable): SQL Server, Oracle

Example: db.r6g.4xlarge
- On-Demand: ~$2,352/month
- 1-Year Reserved: ~$1,530/month (35% savings)
- 3-Year Reserved: ~$1,020/month (57% savings)
```

### Phase 2: Schema Migration

#### Automated Schema Conversion

**Using AWS SCT**:
```
1. Install AWS Schema Conversion Tool
2. Create project
3. Configure source connection
4. Configure target connection
5. Create database migration assessment report
6. Convert schema
7. Review action items
8. Apply converted schema to target
```

**Common Conversions**:

**Oracle to PostgreSQL**:
```sql
-- Oracle
CREATE SEQUENCE emp_seq START WITH 1 INCREMENT BY 1;
CREATE TABLE employees (
    emp_id NUMBER DEFAULT emp_seq.NEXTVAL,
    hire_date DATE,
    salary NUMBER(10,2)
);

-- PostgreSQL
CREATE TABLE employees (
    emp_id SERIAL PRIMARY KEY,
    hire_date DATE,
    salary NUMERIC(10,2)
);
```

**SQL Server to Aurora MySQL**:
```sql
-- SQL Server
CREATE TABLE employees (
    emp_id INT IDENTITY(1,1) PRIMARY KEY,
    hire_date DATETIME,
    salary MONEY,
    notes NVARCHAR(MAX)
);

-- Aurora MySQL
CREATE TABLE employees (
    emp_id INT AUTO_INCREMENT PRIMARY KEY,
    hire_date DATETIME,
    salary DECIMAL(19,4),
    notes LONGTEXT
) ENGINE=InnoDB;
```

#### Stored Procedure Conversion

**Oracle PL/SQL to PostgreSQL PL/pgSQL**:
```sql
-- Oracle
CREATE OR REPLACE PROCEDURE update_salary(
    p_emp_id IN NUMBER,
    p_increase IN NUMBER
) AS
BEGIN
    UPDATE employees
    SET salary = salary * (1 + p_increase)
    WHERE emp_id = p_emp_id;

    COMMIT;
END;
/

-- PostgreSQL
CREATE OR REPLACE FUNCTION update_salary(
    p_emp_id INTEGER,
    p_increase NUMERIC
) RETURNS VOID AS $$
BEGIN
    UPDATE employees
    SET salary = salary * (1 + p_increase)
    WHERE emp_id = p_emp_id;
END;
$$ LANGUAGE plpgsql;
```

### Phase 3: Data Migration

#### Option 1: Offline Migration (Backup/Restore)

**MySQL Example**:
```bash
# On-premises: Export database
mysqldump -h localhost -u root -p \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    --databases mydb > mydb_dump.sql

# Compress for transfer
gzip mydb_dump.sql

# Transfer to EC2 instance
aws s3 cp mydb_dump.sql.gz s3://my-migration-bucket/

# On EC2: Download and restore
aws s3 cp s3://my-migration-bucket/mydb_dump.sql.gz .
gunzip mydb_dump.sql.gz

mysql -h my-rds-instance.abc123.us-east-1.rds.amazonaws.com \
    -u admin -p < mydb_dump.sql
```

**PostgreSQL Example**:
```bash
# Export using pg_dump
pg_dump -h localhost -U postgres -Fc mydb > mydb.dump

# Transfer to S3
aws s3 cp mydb.dump s3://my-migration-bucket/

# Restore using pg_restore
pg_restore -h my-rds-instance.abc123.us-east-1.rds.amazonaws.com \
    -U postgres -d mydb -v mydb.dump
```

#### Option 2: Online Migration (AWS DMS)

**Setup AWS Database Migration Service**:

1. **Create Replication Instance**:
```json
{
    "ReplicationInstanceIdentifier": "my-replication-instance",
    "ReplicationInstanceClass": "dms.c5.xlarge",
    "AllocatedStorage": 100,
    "VpcSecurityGroupIds": ["sg-12345678"],
    "AvailabilityZone": "us-east-1a",
    "MultiAZ": true,
    "PubliclyAccessible": false
}
```

2. **Create Source Endpoint**:
```json
{
    "EndpointIdentifier": "source-oracle",
    "EndpointType": "source",
    "EngineName": "oracle",
    "ServerName": "on-prem-oracle.company.com",
    "Port": 1521,
    "DatabaseName": "ORCL",
    "Username": "admin",
    "Password": "password",
    "SslMode": "require"
}
```

3. **Create Target Endpoint**:
```json
{
    "EndpointIdentifier": "target-postgres",
    "EndpointType": "target",
    "EngineName": "postgres",
    "ServerName": "my-aurora.cluster-abc123.us-east-1.rds.amazonaws.com",
    "Port": 5432,
    "DatabaseName": "mydb",
    "Username": "postgres",
    "Password": "password"
}
```

4. **Create Migration Task**:
```json
{
    "MigrationTaskIdentifier": "oracle-to-postgres",
    "SourceEndpointArn": "arn:aws:dms:...:endpoint/source-oracle",
    "TargetEndpointArn": "arn:aws:dms:...:endpoint/target-postgres",
    "ReplicationInstanceArn": "arn:aws:dms:...:rep/my-replication-instance",
    "MigrationType": "full-load-and-cdc",
    "TableMappings": {
        "rules": [
            {
                "rule-type": "selection",
                "rule-id": "1",
                "rule-name": "include-all-tables",
                "object-locator": {
                    "schema-name": "HR",
                    "table-name": "%"
                },
                "rule-action": "include"
            }
        ]
    }
}
```

5. **Monitor Migration**:
```python
import boto3

dms = boto3.client('dms')

response = dms.describe_replication_tasks(
    Filters=[
        {
            'Name': 'replication-task-id',
            'Values': ['oracle-to-postgres']
        }
    ]
)

task = response['ReplicationTasks'][0]
print(f"Status: {task['Status']}")
print(f"Progress: {task['ReplicationTaskStats']['TablesLoaded']} tables loaded")
print(f"CDC Latency: {task['ReplicationTaskStats'].get('FreshStartDate')}")
```

#### Option 3: Native Replication

**MySQL to Aurora MySQL**:
```sql
-- On source MySQL
CREATE USER 'repl_user'@'%' IDENTIFIED BY 'password';
GRANT REPLICATION SLAVE ON *.* TO 'repl_user'@'%';
FLUSH PRIVILEGES;

SHOW MASTER STATUS;  -- Note File and Position

-- On Aurora (target)
CALL mysql.rds_set_external_master(
    'source-mysql-host',
    3306,
    'repl_user',
    'password',
    'mysql-bin.000001',  -- From SHOW MASTER STATUS
    12345,               -- Position from SHOW MASTER STATUS
    0
);

CALL mysql.rds_start_replication;

-- Monitor replication
SHOW SLAVE STATUS\G
```

**PostgreSQL to Aurora PostgreSQL**:
```sql
-- On source PostgreSQL
-- Enable logical replication
ALTER SYSTEM SET wal_level = logical;
-- Restart PostgreSQL

CREATE PUBLICATION my_publication FOR ALL TABLES;

-- On Aurora (target)
CREATE SUBSCRIPTION my_subscription
    CONNECTION 'host=source-host port=5432 dbname=mydb user=postgres password=password'
    PUBLICATION my_publication;

-- Monitor replication
SELECT * FROM pg_stat_subscription;
```

### Phase 4: Application Migration

#### Connection String Updates

**Before (On-Premises)**:
```python
# Python example
import psycopg2

conn = psycopg2.connect(
    host="on-prem-db.company.local",
    port=5432,
    database="mydb",
    user="app_user",
    password="password"
)
```

**After (Cloud)**:
```python
import psycopg2
import boto3
import json

# Option 1: Direct connection
conn = psycopg2.connect(
    host="my-aurora.cluster-abc123.us-east-1.rds.amazonaws.com",
    port=5432,
    database="mydb",
    user="app_user",
    password="password",
    sslmode="require"
)

# Option 2: Using Secrets Manager
secrets = boto3.client('secretsmanager')
secret = secrets.get_secret_value(SecretId='prod/db/credentials')
credentials = json.loads(secret['SecretString'])

conn = psycopg2.connect(
    host=credentials['host'],
    port=credentials['port'],
    database=credentials['database'],
    user=credentials['username'],
    password=credentials['password'],
    sslmode="require"
)
```

#### Connection Pooling

**Using RDS Proxy**:
```python
# Application connects to RDS Proxy instead of database
conn = psycopg2.connect(
    host="my-rds-proxy.proxy-abc123.us-east-1.rds.amazonaws.com",
    port=5432,
    database="mydb",
    user="app_user",
    password="password",
    sslmode="require"
)

# Benefits:
# - Connection pooling and reuse
# - Improved application availability during failover
# - IAM authentication support
# - Reduced database memory usage
```

### Phase 5: Validation and Cutover

#### Data Validation

**Row Count Comparison**:
```sql
-- Source
SELECT table_name, COUNT(*) as row_count
FROM all_tables
WHERE owner = 'HR';

-- Target
SELECT table_name, COUNT(*) as row_count
FROM information_schema.tables
WHERE table_schema = 'hr';
```

**Checksum Validation**:
```python
import hashlib
import psycopg2

def calculate_table_checksum(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY id")

    checksum = hashlib.sha256()
    for row in cursor:
        checksum.update(str(row).encode())

    return checksum.hexdigest()

# Compare checksums
source_checksum = calculate_table_checksum(source_conn, 'employees')
target_checksum = calculate_table_checksum(target_conn, 'employees')

if source_checksum == target_checksum:
    print("Data validated successfully")
else:
    print("Data mismatch detected!")
```

#### Performance Validation

**Query Performance Comparison**:
```python
import time
import psycopg2

def benchmark_query(conn, query):
    cursor = conn.cursor()
    start_time = time.time()
    cursor.execute(query)
    cursor.fetchall()
    elapsed_time = time.time() - start_time
    return elapsed_time

queries = [
    "SELECT * FROM orders WHERE order_date > '2024-01-01'",
    "SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id",
    "SELECT * FROM products WHERE category = 'Electronics'"
]

for query in queries:
    source_time = benchmark_query(source_conn, query)
    target_time = benchmark_query(target_conn, query)

    print(f"Query: {query[:50]}...")
    print(f"Source: {source_time:.2f}s")
    print(f"Target: {target_time:.2f}s")
    print(f"Difference: {((target_time - source_time) / source_time) * 100:.1f}%")
    print()
```

#### Cutover Checklist

```
T-1 Week:
[ ] Final migration rehearsal
[ ] Update DNS TTL to 60 seconds
[ ] Brief all teams on cutover plan
[ ] Confirm rollback procedures
[ ] Prepare monitoring dashboards

T-24 Hours:
[ ] Freeze schema changes
[ ] Verify replication lag < 1 second
[ ] Final application testing
[ ] Confirm on-call coverage

T-4 Hours:
[ ] Stop batch jobs
[ ] Enable read-only mode on source
[ ] Final data validation

T-2 Hours:
[ ] Stop all writes to source database
[ ] Wait for replication lag = 0
[ ] Final checksum validation
[ ] Update DNS/connection strings

T-0 (Cutover):
[ ] Switch application to target database
[ ] Enable writes on target
[ ] Monitor application logs
[ ] Verify transactions processing
[ ] Monitor database performance

T+1 Hour:
[ ] Validate business transactions
[ ] Check application error rates
[ ] Review database metrics
[ ] User communication

T+4 Hours:
[ ] Extended monitoring
[ ] Performance optimization if needed
[ ] Update documentation

T+24 Hours:
[ ] Review post-migration metrics
[ ] Go/No-Go for decommission
```

## Risk Mitigation

### Risk Assessment Matrix

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Data loss during migration | Low | Critical | DMS CDC, validation, backups |
| Extended downtime | Medium | High | Minimal downtime strategy, rehearsals |
| Performance degradation | Medium | High | Load testing, optimization, sizing |
| Application compatibility | Medium | Medium | Testing, code review, gradual rollout |
| Cost overrun | High | Medium | Accurate sizing, Reserved Instances |
| Incomplete data migration | Low | Critical | Validation scripts, checksums |
| Replication lag | Medium | Medium | Monitoring, network optimization |
| Security vulnerabilities | Low | Critical | Security groups, encryption, IAM |

### Mitigation Strategies

#### 1. Data Integrity Protection

**Continuous Validation**:
```python
import boto3
import psycopg2

def monitor_dms_task():
    dms = boto3.client('dms')
    cloudwatch = boto3.client('cloudwatch')

    # Monitor replication lag
    response = dms.describe_replication_tasks()
    for task in response['ReplicationTasks']:
        stats = task.get('ReplicationTaskStats', {})

        # Alert if lag > 5 minutes
        if stats.get('CDCLatencySource', 0) > 300:
            send_alert(f"High replication lag: {stats['CDCLatencySource']}s")

        # Monitor errors
        if stats.get('Errors', 0) > 0:
            send_alert(f"DMS errors detected: {stats['Errors']}")
```

**Automated Testing**:
```python
def continuous_data_validation():
    while migration_in_progress:
        # Row count validation
        source_count = get_row_count(source_conn, 'orders')
        target_count = get_row_count(target_conn, 'orders')

        if abs(source_count - target_count) > 100:
            alert("Row count mismatch detected")

        # Sample data validation
        validate_sample_records('orders', sample_size=1000)

        time.sleep(60)  # Check every minute
```

#### 2. Performance Optimization

**Pre-Migration Optimization**:
```sql
-- Analyze query patterns
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 20;

-- Identify missing indexes
SELECT schemaname, tablename, attname
FROM pg_stats
WHERE correlation < 0.1
AND n_distinct > 100;

-- Create appropriate indexes
CREATE INDEX idx_orders_customer_date
ON orders(customer_id, order_date)
WHERE status = 'completed';
```

**Post-Migration Tuning**:
```sql
-- PostgreSQL parameter tuning for RDS/Aurora
-- (via parameter group)

shared_buffers = 25% of RAM
effective_cache_size = 75% of RAM
maintenance_work_mem = 2GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1  (for SSD)
effective_io_concurrency = 200
work_mem = 32MB
min_wal_size = 2GB
max_wal_size = 8GB
```

#### 3. Downtime Minimization

**Strategy: Blue/Green Deployment**:
```
1. Keep source database running (Blue)
2. Build and sync target database (Green)
3. Test Green environment thoroughly
4. Switch traffic to Green
5. Monitor for issues
6. Keep Blue as fallback
7. Decommission Blue after validation period
```

**Implementation**:
```python
def blue_green_cutover():
    # Step 1: Verify Green is ready
    assert check_replication_lag() < 1  # < 1 second
    assert validate_data_integrity()
    assert run_health_checks()

    # Step 2: Enable read-only on Blue
    execute_on_source("SET GLOBAL read_only = ON;")

    # Step 3: Final sync
    wait_for_replication_lag(0)

    # Step 4: Validate Green
    assert final_data_validation()

    # Step 5: Update DNS/Load Balancer
    update_route53_record(
        hosted_zone_id='Z123456',
        record_name='db.example.com',
        new_value='green-db.us-east-1.rds.amazonaws.com'
    )

    # Step 6: Monitor
    monitor_application_metrics()

    # Step 7: Rollback if needed (within 1 hour)
    if detect_issues():
        rollback_to_blue()
```

## Rollback Plans

### Rollback Decision Criteria

**Critical Issues (Immediate Rollback)**:
- Data corruption detected
- Application unable to connect
- Error rate > 10%
- Data loss identified
- Security breach

**Warning Issues (Consider Rollback)**:
- Performance degradation > 50%
- Error rate 5-10%
- Replication lag issues
- User complaints

### Rollback Procedures by Strategy

#### 1. DMS-Based Migration Rollback

**Scenario**: Issues detected during CDC phase

```
Step 1: Assessment (5 minutes)
- Identify issue severity
- Check replication status
- Assess data integrity

Step 2: Pause Migration (5 minutes)
- Stop DMS task
- Enable read-only on target
- Preserve target state for analysis

Step 3: Redirect Traffic (10 minutes)
- Update application connection strings
- OR update DNS records
- OR update load balancer configuration

Step 4: Re-enable Source (5 minutes)
- Disable read-only mode
- Verify source database health
- Monitor application connectivity

Step 5: Validation (15 minutes)
- Confirm applications functioning
- Check transaction processing
- Monitor error logs

Step 6: Communication (Ongoing)
- Notify stakeholders
- Update status page
- Plan remediation

Total Rollback Time: ~40 minutes
```

**Rollback Script**:
```python
def rollback_to_source():
    print("Starting rollback procedure...")

    # 1. Stop DMS task
    dms.stop_replication_task(
        ReplicationTaskArn=task_arn
    )
    print("DMS task stopped")

    # 2. Update Route53 to point to source
    route53.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            'Changes': [{
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': 'db.example.com',
                    'Type': 'CNAME',
                    'TTL': 60,
                    'ResourceRecords': [
                        {'Value': 'source-db.company.local'}
                    ]
                }
            }]
        }
    )
    print("DNS updated to source")

    # 3. Disable read-only on source
    execute_on_source("SET GLOBAL read_only = OFF;")
    print("Source database write-enabled")

    # 4. Validate
    assert test_database_connectivity('source')
    assert test_write_operations('source')
    print("Rollback successful")

    # 5. Alert team
    send_alert("Rollback to source database completed")
```

#### 2. Native Replication Rollback

**Scenario**: Issues after cutover to replica

```
Step 1: Stop Writes to Target (2 minutes)
- Enable maintenance mode in application
- OR update application config to read-only

Step 2: Sync Back to Source (Variable)
- If bidirectional replication: wait for sync
- If unidirectional: accept data loss or manual merge

Step 3: Switch Back to Source (5 minutes)
- Update connection strings/DNS
- Disable maintenance mode
- Enable writes on source

Step 4: Validate (10 minutes)
- Test functionality
- Monitor transactions

Total Rollback Time: ~20 minutes (+ sync time)
```

#### 3. Offline Migration Rollback

**Scenario**: Issues after big bang migration

```
Step 1: Restore Source from Backup (1-4 hours)
- Restore database from pre-migration backup
- Replay any transaction logs if available
- Validate restore

Step 2: Redirect Applications (10 minutes)
- Update connection strings
- Restart application servers if needed

Step 3: Data Recovery (Variable)
- Identify data created in target
- Manual export if needed
- Plan re-migration

Total Rollback Time: 1-4 hours
```

**Backup Verification Before Cutover**:
```bash
# Verify backup exists and is valid
aws rds describe-db-snapshots \
    --db-instance-identifier source-db \
    --query 'DBSnapshots[0].[DBSnapshotIdentifier,Status,SnapshotCreateTime]'

# Test restore to verify backup integrity
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier test-restore \
    --db-snapshot-identifier pre-migration-snapshot-2024-01-15

# After validation, delete test instance
aws rds delete-db-instance \
    --db-instance-identifier test-restore \
    --skip-final-snapshot
```

### Rollback Testing

**Pre-Migration Rollback Rehearsal**:
```
Week -4: First rollback test
1. Perform migration to test environment
2. Simulate issues
3. Execute rollback procedure
4. Measure rollback time
5. Document issues

Week -2: Second rollback test
1. Repeat on production-like environment
2. Include application teams
3. Refine procedures
4. Update runbooks

Week -1: Final validation
1. Review rollback procedures with all teams
2. Confirm decision criteria
3. Designate decision makers
4. Establish communication plan
```

## Case Studies

### Case Study 1: E-commerce Platform - Oracle to Aurora PostgreSQL

**Background**:
- Online retailer with 10M+ customers
- Oracle RAC database (5 TB)
- 24/7 operation, no maintenance windows
- $500K annual Oracle licensing costs

**Migration Strategy**: Heterogeneous with DMS

**Implementation**:

```
Phase 1: Assessment (2 months)
- Used AWS SCT to analyze schema
- Identified 85% automatic conversion
- Manual conversion needed for 200 stored procedures
- Estimated 40% cost reduction

Phase 2: Schema Conversion (2 months)
- Converted schema with SCT
- Manually converted complex PL/SQL to PL/pgSQL
- Implemented application code changes
- Created comprehensive test suite

Phase 3: Data Migration Setup (1 month)
- Deployed DMS replication instance (dms.c5.4xlarge)
- Configured CDC from Oracle
- Initial full load to Aurora PostgreSQL
- Established continuous replication

Phase 4: Parallel Run (3 months)
- Ran both databases in parallel
- Dual writes from application
- Daily data validation
- Performance tuning

Phase 5: Cutover (1 day)
- Sunday 2 AM: Enable read-only on Oracle
- Waited for replication lag = 0
- Validated data integrity
- Updated Route53 DNS
- Switched application to Aurora
- Monitored for 8 hours intensive
```

**Results**:
- Zero data loss
- 5 minutes of read-only downtime
- 30% performance improvement
- 60% cost reduction ($300K annual savings)
- Eliminated Oracle licensing dependency

**Challenges Overcome**:
- Converted 200 Oracle packages to PostgreSQL functions
- Optimized 50 slow-performing queries
- Handled sequence behavior differences
- Managed time zone conversion issues

### Case Study 2: SaaS Company - SQL Server to Azure SQL Database

**Background**:
- B2B SaaS platform
- SQL Server 2016 (2 TB)
- 500 concurrent users
- Multi-tenant architecture

**Migration Strategy**: Homogeneous lift-and-shift with optimization

**Implementation**:

```
Phase 1: Planning (1 month)
- Chose Azure SQL Database Hyperscale tier
- Created migration runbook
- Set up Azure environment
- Configured ExpressRoute

Phase 2: Schema Migration (2 weeks)
- Used SQL Server Management Studio
- Generated schema scripts
- Created Azure SQL Database
- Applied schema with minor adjustments

Phase 3: Data Migration (1 week)
- Used Azure Database Migration Service
- Full load: 2 TB migrated in 36 hours
- CDC replication enabled
- Monitored replication lag

Phase 4: Application Testing (2 weeks)
- Updated connection strings
- Tested all features
- Performance benchmarking
- Load testing with 1000 concurrent users

Phase 5: Cutover (Weekend)
- Friday 10 PM: Enable read-only
- Final sync (lag < 5 seconds)
- Updated application configuration
- Switched traffic to Azure
- Disabled old connections
```

**Results**:
- 2-hour downtime window
- 99.99% SLA (improved from 99.95%)
- Hyperscale allowed instant read replicas
- Automatic backups (35-day retention)
- Geo-replication for disaster recovery

**Business Impact**:
- Faster feature deployment (weekly vs. monthly)
- Global read replicas improved customer experience
- 25% cost reduction through elastic scaling
- Improved security posture with Advanced Threat Protection

### Case Study 3: Financial Services - Multi-Database Consolidation

**Background**:
- Regional bank with 50+ databases
- Mix of MySQL, PostgreSQL, SQL Server
- Legacy applications with minimal documentation
- Compliance requirements (PCI-DSS, SOX)

**Migration Strategy**: Consolidation to AWS Aurora and RDS

**Target Architecture**:
```
Legacy Databases (50+) →
    ├─ Transactional DBs → Aurora MySQL Clusters (3)
    ├─ Reporting DBs → Aurora PostgreSQL (2)
    └─ Legacy Apps → RDS SQL Server (5)
```

**Implementation**:

```
Phase 1: Discovery (3 months)
- Cataloged all 50+ databases
- Mapped application dependencies
- Identified consolidation opportunities
- Created migration waves (8 waves)

Phase 2: Pilot (2 months)
- Migrated 5 low-risk databases
- Tested DMS and native tools
- Established patterns and procedures
- Validated compliance controls

Phase 3: Wave Migrations (18 months)
Wave 1-8, each wave:
  - 2 weeks: Preparation
  - 1 week: Data migration
  - 1 week: Testing
  - 1 week: Cutover and validation
  - 1 week: Buffer

Phase 4: Consolidation (6 months)
- Merged similar databases
- Optimized schema designs
- Implemented multi-tenancy where appropriate
```

**Results**:
- 50 databases → 10 Aurora/RDS instances
- 70% reduction in database management overhead
- $800K annual cost savings
- Improved compliance posture
- Automated backups and patching
- RTO: 24 hours → 1 hour
- RPO: 24 hours → 15 minutes

**Compliance Achievements**:
- Automated audit logging to CloudWatch
- Encryption at rest and in transit
- Automated compliance reporting
- Immutable backups for SOX
- Network isolation with security groups

## Tool Recommendations

### Assessment Tools

**1. AWS Schema Conversion Tool (SCT)**
- Purpose: Assess and convert database schemas
- Supported: Oracle, SQL Server, DB2 → Aurora, RDS
- Features: Assessment reports, automated conversion, code conversion
- Best For: Heterogeneous migrations

**2. Azure Database Migration Assistant**
- Purpose: Assess SQL Server compatibility with Azure
- Features: Compatibility issues, recommendations, assessment reports
- Best For: SQL Server to Azure migrations

**3. Google Database Migration Assessment**
- Purpose: Assess Oracle/SQL Server migration readiness
- Features: Complexity analysis, effort estimation
- Best For: GCP migrations

### Migration Tools

**4. AWS Database Migration Service (DMS)**
- Purpose: Online database migration with minimal downtime
- Features: Homogeneous and heterogeneous, CDC, validation
- Best For: Minimal downtime migrations
- Cost: Replication instance hours (~$0.30/hour for c5.xlarge)

**5. Azure Database Migration Service**
- Purpose: Migrate to Azure databases
- Features: Online/offline migration, assessment
- Best For: Azure-bound migrations
- Tiers: Standard (online), Premium (minimal downtime)

**6. Google Database Migration Service**
- Purpose: Migrate to Cloud SQL
- Features: Continuous replication, minimal downtime
- Best For: MySQL, PostgreSQL to Cloud SQL

**7. Native Database Tools**

**mysqldump/mysqlpump**:
- Purpose: MySQL logical backups
- Best For: Small databases (<100 GB)
- Advantages: Simple, reliable
- Disadvantages: Slower for large databases

**pg_dump/pg_restore**:
- Purpose: PostgreSQL backup and restore
- Best For: Offline migrations
- Formats: Custom, directory, tar
- Features: Parallel restore

**Oracle Data Pump**:
- Purpose: Oracle export/import
- Best For: Oracle migrations
- Features: Parallel processing, compression
- Usage: expdp/impdp utilities

### Validation Tools

**8. AWS DMS Data Validation**
- Purpose: Validate migrated data
- Features: Automatic row-level validation
- Limitations: Performance impact during CDC

**9. Precisely Data Integrity Suite**
- Purpose: Enterprise data validation
- Features: Schema comparison, data comparison, reconciliation
- Best For: Large-scale migrations

**10. Custom Validation Scripts**
```python
# Example validation framework
class DatabaseValidator:
    def __init__(self, source_conn, target_conn):
        self.source = source_conn
        self.target = target_conn

    def validate_schema(self):
        # Compare table structures
        pass

    def validate_row_counts(self):
        # Compare row counts for all tables
        pass

    def validate_data_samples(self, sample_size=1000):
        # Compare random data samples
        pass

    def validate_checksums(self):
        # Compare table checksums
        pass

    def generate_report(self):
        # Create validation report
        pass
```

### Monitoring Tools

**11. AWS CloudWatch**
- Metrics: CPU, memory, IOPS, connections, replication lag
- Alarms: Automated alerting
- Logs: Query logs, error logs, slow query logs

**12. Azure Monitor**
- Metrics: DTU/vCore usage, storage, connections
- Insights: Query Performance Insights
- Alerts: Metric-based alerting

**13. Datadog / New Relic**
- Purpose: Third-party monitoring
- Features: Database monitoring, APM, distributed tracing
- Best For: Multi-cloud environments

## Conclusion

Successful database migration to the cloud requires:

**Thorough Planning**:
- Comprehensive assessment
- Appropriate strategy selection
- Detailed migration plan
- Risk mitigation strategies

**Technical Excellence**:
- Schema conversion accuracy
- Data integrity validation
- Performance optimization
- Security implementation

**Risk Management**:
- Parallel run validation
- Comprehensive testing
- Rollback procedures
- Continuous monitoring

**Operational Readiness**:
- Team training
- Documentation
- Runbooks
- Support processes

Database migration is often the most critical and risk-sensitive component of cloud migration. Taking a methodical, well-tested approach with appropriate tools and strategies ensures successful outcomes while minimizing risk to business operations.
