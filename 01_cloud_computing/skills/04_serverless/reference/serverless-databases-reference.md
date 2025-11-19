# Serverless Databases Reference

## Overview

Serverless databases automatically scale capacity based on demand, offering pay-per-use pricing without infrastructure management. Critical for serverless application architectures.

## AWS Serverless Databases

### DynamoDB
**Type**: NoSQL (Key-Value and Document)

**Characteristics**:
- Fully managed, multi-region, multi-active
- Single-digit millisecond latency
- Auto-scaling or on-demand capacity
- Built-in security, backup, restore

**Capacity Modes**:

#### On-Demand
```yaml
Pricing: Pay per request
  - $1.25 per million writes
  - $0.25 per million reads
  - No capacity planning
Best For: Unpredictable workloads, new applications
Scaling: Automatic, instant
```

#### Provisioned
```yaml
Pricing: $0.00065 per WCU-hour, $0.00013 per RCU-hour
Best For: Predictable traffic, cost optimization
Auto-scaling: Yes (target utilization)
Reserved Capacity: Save up to 77%
```

**Data Model**:
```python
# Table
{
  "PK": "USER#123",           # Partition Key
  "SK": "PROFILE#",            # Sort Key (optional)
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2024-01-15",
  "status": "active"
}

# Global Secondary Index (GSI)
GSI_PK: "email"
GSI_SK: "created_at"
```

**Access Patterns**:
```python
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

# Put item
table.put_item(Item={'PK': 'USER#123', 'name': 'John'})

# Get item
response = table.get_item(Key={'PK': 'USER#123'})

# Query (efficient)
response = table.query(
    KeyConditionExpression='PK = :pk',
    ExpressionAttributeValues={':pk': 'USER#123'}
)

# Scan (avoid if possible)
response = table.scan(
    FilterExpression='status = :status',
    ExpressionAttributeValues={':status': 'active'}
)
```

**Best Practices**:
- Design for access patterns, not normalization
- Use single-table design for related entities
- Leverage GSIs for alternate access patterns
- Use sparse indexes to save costs
- Enable Point-in-Time Recovery (PITR)
- Use DynamoDB Accelerator (DAX) for caching

**DynamoDB Streams**:
```yaml
Purpose: Change data capture (CDC)
Retention: 24 hours
Use Cases:
  - Real-time aggregations
  - Cross-region replication
  - Event-driven architectures
  - Audit logging
```

### Aurora Serverless v2
**Type**: Relational (MySQL, PostgreSQL compatible)

**Characteristics**:
- Auto-scales from 0.5 ACU to 128 ACU
- Sub-second scaling
- Maintains connections during scaling
- Multi-AZ availability

**Aurora Capacity Units (ACU)**:
```yaml
1 ACU: ~2 GB RAM, CPU, networking
Min Capacity: 0.5 ACU
Max Capacity: 128 ACU
Scaling: Increments of 0.5 ACU
```

**Pricing**:
```
$0.12 per ACU-hour (MySQL)
$0.14 per ACU-hour (PostgreSQL)
Storage: $0.10 per GB-month
I/O: $0.20 per million requests
```

**Use Cases**:
- Variable workloads with unpredictable patterns
- Development/test environments
- Multi-tenant SaaS applications
- Infrequently used applications

**Connection Management**:
```python
# Use connection pooling (RDS Proxy recommended)
import pymysql

# Outside handler (reuse across invocations)
connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

def handler(event, context):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchall()
```

**Best Practices**:
- Use RDS Proxy for connection pooling
- Set appropriate min/max ACU limits
- Use read replicas for read-heavy workloads
- Enable Aurora Global Database for multi-region
- Monitor and tune scaling configuration

### Aurora Serverless v1 (Legacy)
**Limitations**:
- Pauses after inactivity (cold starts)
- Scaling disrupts connections
- Limited to single AZ
- No read replicas

**Recommendation**: Use Aurora Serverless v2 for new applications.

### Amazon Timestream
**Type**: Time-series database

**Use Cases**:
- IoT telemetry
- Application metrics
- DevOps monitoring
- Real-time analytics

**Pricing**:
```
Writes: $0.50 per million writes
Memory Store: $0.036 per GB-hour
Magnetic Store: $0.03 per GB-month
Queries: $0.01 per GB scanned
```

### Amazon QLDB (Quantum Ledger Database)
**Type**: Ledger database (immutable, cryptographically verifiable)

**Use Cases**:
- Audit trails
- Blockchain alternatives
- Financial transactions
- Supply chain tracking

## Azure Serverless Databases

### Cosmos DB
**Type**: Multi-model (Document, Key-Value, Graph, Column-Family)

**Characteristics**:
- Global distribution (turnkey)
- 5 consistency models
- Single-digit millisecond latency
- Multi-master writes

**Capacity Modes**:

#### Serverless
```yaml
Pricing:
  - $0.25 per million RUs consumed
  - $0.25 per GB stored
Best For: Intermittent, unpredictable workloads
Limits:
  - Max 5,000 RU/s
  - Max 50 GB storage
  - Auto-pause after inactivity
```

#### Provisioned
```yaml
Pricing:
  - $0.008 per 100 RU/s-hour (standard)
  - $0.016 per 100 RU/s-hour (autoscale)
Autoscale: 10% of max to max RU/s
Best For: Consistent workloads
```

**Request Units (RU)**:
- 1 RU = 1 KB document read (point read)
- Writes consume more RUs (~5x reads)
- Queries vary based on complexity

**APIs**:
- **Core (SQL)**: Document database (most popular)
- **MongoDB**: Wire protocol compatible
- **Cassandra**: Column-family
- **Gremlin**: Graph database
- **Table**: Key-value

**Example (SQL API)**:
```python
from azure.cosmos import CosmosClient

client = CosmosClient(ENDPOINT, KEY)
database = client.get_database_client('mydb')
container = database.get_container_client('users')

# Create
container.create_item({
    'id': '123',
    'userId': '123',
    'name': 'John Doe',
    'email': 'john@example.com'
})

# Read (point read - 1 RU)
item = container.read_item(item='123', partition_key='123')

# Query (variable RU)
items = container.query_items(
    query='SELECT * FROM c WHERE c.email = @email',
    parameters=[{'name': '@email', 'value': 'john@example.com'}]
)
```

**Best Practices**:
- Choose appropriate partition key (even distribution)
- Use point reads when possible (1 RU vs query RUs)
- Enable indexing selectively
- Use change feed for event-driven patterns
- Consider geo-replication for global apps

**Change Feed**:
```yaml
Purpose: Listen to document changes
Use Cases:
  - Real-time notifications
  - Materialized views
  - Event sourcing
  - Data synchronization
Delivery: Azure Functions, Change Feed Processor
```

### Azure SQL Database Serverless
**Type**: Relational (T-SQL)

**Characteristics**:
- Auto-pause after inactivity
- Auto-resume on connection
- Pay for vCore-seconds used
- Storage always online

**Pricing**:
```yaml
Compute: $0.000145 per vCore-second (Gen5)
Storage: $0.115 per GB-month
Auto-pause delay: 1-7 days (configurable)
```

**Compute Tiers**:
```yaml
Min vCores: 0.5
Max vCores: 40
Auto-scaling: Within min-max range
Pause: After inactivity (saves compute cost)
```

**Use Cases**:
- Development/test environments
- Infrequent production workloads
- Lightweight applications
- Multi-tenant SaaS (per-tenant databases)

**Connection Handling**:
```csharp
using Microsoft.Data.SqlClient;

// Connection string with retry logic
var connectionString = new SqlConnectionStringBuilder
{
    DataSource = "server.database.windows.net",
    InitialCatalog = "mydb",
    UserID = "user",
    Password = "password",
    ConnectRetryCount = 3,
    ConnectRetryInterval = 10
}.ConnectionString;

using (var connection = new SqlConnection(connectionString))
{
    connection.Open();
    // First connection may take 30-60s (auto-resume)
    var command = new SqlCommand("SELECT * FROM Users", connection);
    var reader = command.ExecuteReader();
}
```

**Best Practices**:
- Set appropriate auto-pause delay
- Handle auto-resume latency in application
- Use elastic pools for multiple databases
- Monitor vCore utilization for rightsizing

## Google Cloud Serverless Databases

### Firestore
**Type**: NoSQL (Document database)

**Modes**:

#### Native Mode (Recommended)
```yaml
Pricing:
  - $0.06 per 100,000 document reads
  - $0.18 per 100,000 document writes
  - $0.02 per 100,000 deletes
  - $0.18 per GB stored
Real-time: Yes (live listeners)
Scaling: Automatic
Consistency: Strong
```

#### Datastore Mode (Legacy)
```yaml
For: Backwards compatibility with Datastore
Use: Existing Datastore users only
```

**Data Model**:
```
Collection → Document → Subcollection → Document
                ↓
            Fields (key-value pairs)
```

**Example**:
```python
from google.cloud import firestore

db = firestore.Client()

# Create
doc_ref = db.collection('users').document('user123')
doc_ref.set({
    'name': 'John Doe',
    'email': 'john@example.com',
    'created_at': firestore.SERVER_TIMESTAMP
})

# Read
doc = doc_ref.get()
if doc.exists:
    print(doc.to_dict())

# Query
users_ref = db.collection('users')
query = users_ref.where('email', '==', 'john@example.com')
results = query.stream()

# Real-time listener
def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        print(f'Received document: {doc.id}')

doc_ref.on_snapshot(on_snapshot)
```

**Best Practices**:
- Design for efficient queries (composite indexes)
- Use subcollections for hierarchical data
- Leverage real-time listeners for live updates
- Batch writes to reduce costs
- Use TTL for automatic deletion

### Cloud SQL (Serverless - limited)
**Note**: Cloud SQL is not truly serverless but offers some features:
- **Cloud SQL Editions**: Enterprise, Enterprise Plus (high availability)
- **Autoscaling**: Storage auto-increases
- **Scheduled Scaling**: Scale up/down on schedule
- **Serverless Export**: Scheduled exports without downtime

**For Serverless**: Use Cloud Run with Cloud SQL via Unix socket or RDS Proxy equivalent.

### Bigtable (Not Fully Serverless)
**Type**: Wide-column NoSQL

**Characteristics**:
- Petabyte-scale
- Single-digit millisecond latency
- Not serverless (requires provisioned nodes)
- Use Cloud Run + Bigtable for serverless access

**When to Use**: Massive scale (TB-PB), time-series, IoT

### Spanner (Serverless Considerations)
**Type**: Globally distributed SQL

**Characteristics**:
- Horizontal scalability
- Strong consistency
- Auto-scaling (within node limits)
- Not pay-per-request (node-based pricing)

**Autoscaler**: Open-source Cloud Functions-based autoscaler available.

## Multi-Cloud & Serverless Databases

### MongoDB Atlas Serverless
```yaml
Clouds: AWS, Azure, GCP
Pricing: $0.10 per million reads, $1.00 per million writes
Auto-scaling: Yes
Storage: $0.25 per GB-month
Best For: MongoDB workloads, multi-cloud portability
```

### FaunaDB
```yaml
Type: Document-relational hybrid
Pricing: Pay per operation + storage
Features:
  - ACID transactions
  - GraphQL and FQL
  - Global replication
  - Multi-cloud (AWS, GCP, Azure)
Best For: JAMstack, serverless apps
```

### PlanetScale (MySQL)
```yaml
Type: Serverless MySQL
Based On: Vitess (YouTube's MySQL scaling solution)
Pricing: Free tier + pay-as-you-grow
Features:
  - Schema branching
  - Non-blocking schema changes
  - Horizontal sharding
Best For: MySQL apps needing scale
```

### Supabase
```yaml
Type: PostgreSQL-based
Pricing: Free tier + usage-based
Features:
  - Real-time subscriptions
  - Auth, storage, functions included
  - PostgreSQL full features
Best For: Firebase alternative, PostgreSQL preference
```

## Database Selection Guide

### Key Decision Factors

| Factor | DynamoDB | Cosmos DB | Firestore | Aurora Serverless |
|--------|----------|-----------|-----------|-------------------|
| **Data Model** | NoSQL | Multi-model | NoSQL (Document) | SQL (Relational) |
| **Consistency** | Eventual/Strong | 5 models | Strong | Strong |
| **Latency** | Single-digit ms | Single-digit ms | Low ms | Low ms |
| **Scale** | Unlimited | Unlimited | Automatic | Up to 128 ACU |
| **Transactions** | Limited | ACID | ACID | ACID |
| **Pricing** | Per request | Per RU | Per operation | Per ACU-hour |
| **Global** | Multi-region | Turnkey global | Multi-region | Aurora Global |
| **Real-time** | Streams | Change Feed | Listeners | Change streams |
| **SQL Support** | PartiQL (limited) | SQL (Core API) | No | Yes (full) |

### Use Case Recommendations

**High-throughput, low-latency key-value**:
- AWS: DynamoDB
- Azure: Cosmos DB (Table API)
- GCP: Firestore

**Relational with variable load**:
- AWS: Aurora Serverless v2
- Azure: Azure SQL Serverless
- GCP: Cloud SQL (with Cloud Run)

**Global distribution, multi-region writes**:
- AWS: DynamoDB Global Tables
- Azure: Cosmos DB
- GCP: Firestore, Spanner

**Real-time updates, mobile/web apps**:
- AWS: DynamoDB + AppSync
- Azure: Cosmos DB Change Feed
- GCP: Firestore (native real-time)

**Complex queries, reporting**:
- AWS: Aurora Serverless v2
- Azure: Azure SQL Serverless, Cosmos DB (SQL API)
- GCP: Cloud SQL, BigQuery

**Time-series, IoT**:
- AWS: Timestream, DynamoDB
- Azure: Cosmos DB, Time Series Insights
- GCP: Bigtable, Firestore

## Connection Management in Serverless

### Problem
Serverless functions can create thousands of database connections, exhausting connection pools.

### Solutions

#### 1. Connection Pooling (Reuse)
```python
# Initialize outside handler (reused across warm invocations)
import psycopg2

connection = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

def handler(event, context):
    # Reuse connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()
```

**Considerations**:
- Connection may be stale (implement health check)
- Lambda freezes/thaws state between invocations
- Not guaranteed across all invocations

#### 2. RDS Proxy (AWS)
```yaml
Purpose: Managed connection pooling for RDS/Aurora
Benefits:
  - Reduces connection overhead
  - Improves failover time
  - Manages authentication (IAM)
  - Pinning prevention
Pricing: $0.015 per vCPU-hour
```

**Configuration**:
```python
import pymysql

# Connect through RDS Proxy
connection = pymysql.connect(
    host='proxy-endpoint.proxy-xyz.us-east-1.rds.amazonaws.com',
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
```

#### 3. HTTP-based Databases
```yaml
DynamoDB: HTTP API (SDK)
Cosmos DB: HTTP API (SDK)
Firestore: gRPC/HTTP API (SDK)
Aurora Serverless Data API: HTTP API (no persistent connections)
```

**Aurora Data API Example**:
```python
import boto3

rds_data = boto3.client('rds-data')

response = rds_data.execute_statement(
    resourceArn=CLUSTER_ARN,
    secretArn=SECRET_ARN,
    database=DB_NAME,
    sql='SELECT * FROM users WHERE id = :id',
    parameters=[{'name': 'id', 'value': {'longValue': 123}}]
)
```

**Pros**:
- No connection management
- Automatic scaling
- IAM authentication

**Cons**:
- Higher latency vs direct connection
- Limited to Aurora Serverless v1/v2

## Best Practices

### General
1. Choose the right database for access patterns
2. Use connection pooling or HTTP APIs
3. Implement caching (in-memory, Redis, CDN)
4. Monitor costs and optimize queries
5. Enable backups and point-in-time recovery

### Performance
1. Design for database strengths (e.g., DynamoDB single-table design)
2. Use indexes appropriately
3. Batch operations when possible
4. Cache frequently accessed data
5. Use read replicas for read-heavy workloads

### Cost Optimization
1. Use on-demand/serverless for variable workloads
2. Use provisioned for predictable workloads
3. Monitor and alert on anomalies
4. Delete unused data (TTL, lifecycle policies)
5. Use reserved capacity for baseline load

### Security
1. Use IAM roles for authentication (avoid hardcoded credentials)
2. Encrypt at rest and in transit
3. Use VPC for private connectivity
4. Implement least privilege access
5. Enable audit logging

## Resources

- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [Cosmos DB Best Practices](https://docs.microsoft.com/azure/cosmos-db/best-practice)
- [Firestore Best Practices](https://cloud.google.com/firestore/docs/best-practices)
- [Aurora Serverless Guide](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html)
