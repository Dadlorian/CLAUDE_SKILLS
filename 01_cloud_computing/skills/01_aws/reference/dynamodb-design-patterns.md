# DynamoDB Design Patterns Reference

## DynamoDB Core Concepts

### Table Structure
- **Partition Key (PK)**: Required, determines data distribution
- **Sort Key (SK)**: Optional, enables range queries and sorting
- **Composite Primary Key**: PK + SK combination
- **Attributes**: Schemaless, can vary between items
- **Item Size Limit**: 400 KB maximum

### Capacity Modes

**Provisioned Capacity:**
- Read Capacity Units (RCU): 1 strongly consistent 4KB read/sec
- Write Capacity Units (WCU): 1 write of 1KB/sec
- Auto-scaling available
- Reserved capacity for cost savings
- Predictable workloads

**On-Demand:**
- Pay per request
- No capacity planning needed
- Automatic scaling
- Variable or unpredictable workloads
- ~5x more expensive per request

## Single Table Design Pattern

### Core Principle
Store multiple entity types in one table using generic attribute names.

### Example Schema
```
PK                    | SK                  | Type      | Attributes
---------------------|---------------------|-----------|------------------
USER#john@email.com  | PROFILE#            | User      | name, email, created
USER#john@email.com  | ORDER#2024-001      | Order     | total, status, date
USER#john@email.com  | ORDER#2024-002      | Order     | total, status, date
PRODUCT#PROD-123     | METADATA#           | Product   | name, price, stock
PRODUCT#PROD-123     | REVIEW#USER#john    | Review    | rating, comment, date
ORDER#2024-001       | ITEM#PROD-123       | OrderItem | quantity, price
```

### Access Patterns
```python
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ecommerce')

# 1. Get user profile
response = table.get_item(
    Key={
        'PK': 'USER#john@email.com',
        'SK': 'PROFILE#'
    }
)

# 2. Get all orders for user
response = table.query(
    KeyConditionExpression=
        Key('PK').eq('USER#john@email.com') &
        Key('SK').begins_with('ORDER#')
)

# 3. Get product with all reviews
response = table.query(
    KeyConditionExpression=
        Key('PK').eq('PRODUCT#PROD-123')
)

# 4. Get order with all items
response = table.query(
    KeyConditionExpression=
        Key('PK').eq('ORDER#2024-001') &
        Key('SK').begins_with('ITEM#')
)
```

### Benefits
- Single table reduces costs and latency
- Leverage DynamoDB's query capabilities
- Easier to maintain consistency
- Simpler backup and restore
- Better performance (fewer round trips)

## Advanced Key Design Patterns

### 1. Composite Sort Key Pattern

Encode multiple attributes in the sort key for complex queries.

```python
# Schema
PK: CUSTOMER#customer_id
SK: ORDER#YYYY-MM-DD#order_id

# Example data
{
    'PK': 'CUSTOMER#C001',
    'SK': 'ORDER#2024-01-15#ORD-1001',
    'total': 99.99,
    'status': 'SHIPPED'
}

# Query orders by date range
response = table.query(
    KeyConditionExpression=
        Key('PK').eq('CUSTOMER#C001') &
        Key('SK').between('ORDER#2024-01-01', 'ORDER#2024-01-31')
)
```

### 2. Hierarchical Data Pattern

Model hierarchical relationships with sort keys.

```python
# Organization hierarchy
PK              | SK                           | Type
----------------|------------------------------|----------
ORG#org1        | METADATA#                    | Org
ORG#org1        | DEPT#sales                   | Department
ORG#org1        | DEPT#sales#TEAM#east         | Team
ORG#org1        | DEPT#sales#TEAM#east#EMP#001 | Employee

# Get entire hierarchy
response = table.query(
    KeyConditionExpression=Key('PK').eq('ORG#org1')
)

# Get all employees in a team
response = table.query(
    KeyConditionExpression=
        Key('PK').eq('ORG#org1') &
        Key('SK').begins_with('DEPT#sales#TEAM#east#EMP#')
)
```

### 3. Adjacency List Pattern

Model graph relationships (many-to-many).

```python
# User followers/following
PK              | SK              | Type
----------------|-----------------|----------
USER#alice      | USER#bob        | Follows
USER#alice      | USER#charlie    | Follows
USER#bob        | USER#alice      | Follows
USER#bob        | USER#david      | Follows

# Get who alice follows
response = table.query(
    KeyConditionExpression=
        Key('PK').eq('USER#alice') &
        Key('SK').begins_with('USER#')
)

# Get alice's followers (requires GSI)
GSI: SK as PK, PK as SK
response = table.query(
    IndexName='InverseIndex',
    KeyConditionExpression=
        Key('SK').eq('USER#alice') &
        Key('PK').begins_with('USER#')
)
```

### 4. Time Series Data Pattern

Optimize for time-based queries.

```python
# Hot and cold partitions
PK                  | SK                    | Data
--------------------|------------------------|------
SENSOR#123#2024-01  | 2024-01-15T10:30:00   | {temp: 72}
SENSOR#123#2024-01  | 2024-01-15T10:35:00   | {temp: 73}
SENSOR#123#2024-02  | 2024-02-01T10:30:00   | {temp: 68}

# Query current month (hot partition)
response = table.query(
    KeyConditionExpression=
        Key('PK').eq('SENSOR#123#2024-01')
)

# Use TTL to auto-delete old data
table.update_item(
    Key={'PK': 'SENSOR#123#2024-01', 'SK': '2024-01-15T10:30:00'},
    UpdateExpression='SET #ttl = :ttl',
    ExpressionAttributeNames={'#ttl': 'TTL'},
    ExpressionAttributeValues={':ttl': 1739577600}  # Unix timestamp
)
```

### 5. Materialized Aggregations Pattern

Pre-calculate and store aggregations.

```python
# Store aggregations alongside detail records
PK              | SK                | Type      | Data
----------------|-------------------|-----------|------
ORDER#2024-001  | METADATA#         | Order     | {total: 150}
ORDER#2024-001  | ITEM#1            | Item      | {price: 50, qty: 2}
ORDER#2024-001  | ITEM#2            | Item      | {price: 50, qty: 1}
USER#john       | STATS#2024-01     | Stats     | {orders: 5, spent: 500}
USER#john       | STATS#LIFETIME    | Stats     | {orders: 47, spent: 4500}

# Update aggregation with transaction
response = table.transact_write_items(
    TransactItems=[
        {
            'Put': {
                'TableName': 'orders',
                'Item': {
                    'PK': 'ORDER#2024-002',
                    'SK': 'METADATA#',
                    'total': 75
                }
            }
        },
        {
            'Update': {
                'TableName': 'orders',
                'Key': {'PK': 'USER#john', 'SK': 'STATS#2024-01'},
                'UpdateExpression': 'ADD orders :inc, spent :amount',
                'ExpressionAttributeValues': {
                    ':inc': 1,
                    ':amount': 75
                }
            }
        }
    ]
)
```

## Global Secondary Index (GSI) Patterns

### 1. Sparse Index Pattern

Index only items with specific attributes to reduce costs.

```python
# Main table
PK           | SK        | Status    | GSI-PK       | GSI-SK
-------------|-----------|-----------|--------------|--------
ORDER#001    | METADATA# | SHIPPED   | -            | -
ORDER#002    | METADATA# | PENDING   | STATUS#PEND  | ORDER#002
ORDER#003    | METADATA# | PENDING   | STATUS#PEND  | ORDER#003

# Query all pending orders using sparse GSI
response = table.query(
    IndexName='StatusIndex',
    KeyConditionExpression=Key('GSI-PK').eq('STATUS#PENDING')
)

# Only pending orders are indexed, saving storage and costs
```

### 2. GSI Overloading Pattern

Use a single GSI for multiple query patterns.

```python
# Main table
PK           | SK        | GSI-PK           | GSI-SK
-------------|-----------|------------------|------------------
USER#alice   | PROFILE#  | -                | -
USER#alice   | ORDER#001 | ORDER#001        | USER#alice
PROD#123     | META#     | CATEGORY#books   | PROD#123
PROD#456     | META#     | CATEGORY#books   | PROD#456

# GSI supports multiple access patterns:
# 1. Get user by order ID
response = table.query(
    IndexName='OverloadedGSI',
    KeyConditionExpression=Key('GSI-PK').eq('ORDER#001')
)

# 2. Get products by category
response = table.query(
    IndexName='OverloadedGSI',
    KeyConditionExpression=Key('GSI-PK').eq('CATEGORY#books')
)
```

### 3. GSI Sharding Pattern

Distribute hot partitions across multiple shards.

```python
import random

# Add shard number to GSI key
def get_shard_id(num_shards=10):
    return random.randint(0, num_shards - 1)

# Write with shard
item = {
    'PK': 'USER#alice',
    'SK': 'ORDER#001',
    'GSI-PK': f'STATUS#PENDING#SHARD#{get_shard_id()}',
    'GSI-SK': 'ORDER#001'
}

# Query all shards and merge results
results = []
for shard in range(10):
    response = table.query(
        IndexName='StatusIndex',
        KeyConditionExpression=Key('GSI-PK').eq(f'STATUS#PENDING#SHARD#{shard}')
    )
    results.extend(response['Items'])
```

## DynamoDB Streams Patterns

### 1. Aggregate and Denormalize

Use streams to update materialized views.

```python
import boto3

def lambda_handler(event, context):
    """Process DynamoDB stream events to update aggregations"""
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_item = record['dynamodb']['NewImage']

            if new_item['Type']['S'] == 'Order':
                # Update user's order statistics
                update_user_stats(
                    user_id=new_item['PK']['S'],
                    order_total=Decimal(new_item['total']['N'])
                )

def update_user_stats(user_id, order_total):
    table = boto3.resource('dynamodb').Table('orders')
    table.update_item(
        Key={'PK': user_id, 'SK': 'STATS#LIFETIME'},
        UpdateExpression='ADD orders :inc, spent :amount',
        ExpressionAttributeValues={
            ':inc': 1,
            ':amount': order_total
        }
    )
```

### 2. Event Sourcing Pattern

Store events, rebuild state from event log.

```python
# Event log table
PK              | SK                    | EventType  | Data
----------------|------------------------|-----------|------
ACCOUNT#001     | EVENT#2024-01-15T10:00| Deposit   | {amount: 100}
ACCOUNT#001     | EVENT#2024-01-15T11:00| Withdraw  | {amount: 50}
ACCOUNT#001     | EVENT#2024-01-15T12:00| Deposit   | {amount: 200}
ACCOUNT#001     | BALANCE#CURRENT       | Balance   | {amount: 250}

# Rebuild state from events
def rebuild_account_state(account_id):
    response = table.query(
        KeyConditionExpression=
            Key('PK').eq(f'ACCOUNT#{account_id}') &
            Key('SK').begins_with('EVENT#')
    )

    balance = 0
    for event in response['Items']:
        if event['EventType'] == 'Deposit':
            balance += event['Data']['amount']
        elif event['EventType'] == 'Withdraw':
            balance -= event['Data']['amount']

    return balance
```

## Transactions

### ACID Transactions

DynamoDB supports transactions across up to 100 items.

```python
# Transfer money between accounts
response = table.transact_write_items(
    TransactItems=[
        {
            'Update': {
                'TableName': 'accounts',
                'Key': {'PK': 'ACCOUNT#001', 'SK': 'BALANCE#'},
                'UpdateExpression': 'SET balance = balance - :amount',
                'ExpressionAttributeValues': {':amount': 100},
                'ConditionExpression': 'balance >= :amount'
            }
        },
        {
            'Update': {
                'TableName': 'accounts',
                'Key': {'PK': 'ACCOUNT#002', 'SK': 'BALANCE#'},
                'UpdateExpression': 'SET balance = balance + :amount',
                'ExpressionAttributeValues': {':amount': 100}
            }
        },
        {
            'Put': {
                'TableName': 'accounts',
                'Item': {
                    'PK': 'TRANSACTION#001',
                    'SK': 'METADATA#',
                    'from': 'ACCOUNT#001',
                    'to': 'ACCOUNT#002',
                    'amount': 100,
                    'timestamp': '2024-01-15T10:00:00Z'
                }
            }
        }
    ]
)
```

## Optimistic Locking

```python
# Use version number for optimistic locking
def update_with_version(pk, sk, new_data, current_version):
    try:
        response = table.update_item(
            Key={'PK': pk, 'SK': sk},
            UpdateExpression='SET #data = :data, #version = :new_version',
            ConditionExpression='#version = :current_version',
            ExpressionAttributeNames={
                '#data': 'data',
                '#version': 'version'
            },
            ExpressionAttributeValues={
                ':data': new_data,
                ':current_version': current_version,
                ':new_version': current_version + 1
            },
            ReturnValues='ALL_NEW'
        )
        return response['Attributes']
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # Version conflict - item was modified
            print("Optimistic lock failed - item was modified")
            raise
```

## Performance Optimization

### 1. Batch Operations

```python
from decimal import Decimal

# Batch write (up to 25 items)
with table.batch_writer() as batch:
    for i in range(100):
        batch.put_item(Item={
            'PK': f'USER#{i}',
            'SK': 'PROFILE#',
            'name': f'User {i}',
            'score': Decimal(i * 10)
        })

# Batch get (up to 100 items)
response = dynamodb.batch_get_item(
    RequestItems={
        'my-table': {
            'Keys': [
                {'PK': f'USER#{i}', 'SK': 'PROFILE#'}
                for i in range(50)
            ]
        }
    }
)
```

### 2. Parallel Scans

```python
import concurrent.futures

def scan_segment(segment, total_segments):
    """Scan a single segment"""
    items = []
    response = table.scan(
        Segment=segment,
        TotalSegments=total_segments
    )
    items.extend(response['Items'])

    while 'LastEvaluatedKey' in response:
        response = table.scan(
            Segment=segment,
            TotalSegments=total_segments,
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        items.extend(response['Items'])

    return items

# Scan with 4 parallel workers
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(scan_segment, segment, 4)
        for segment in range(4)
    ]
    all_items = []
    for future in concurrent.futures.as_completed(futures):
        all_items.extend(future.result())
```

### 3. Projection Expressions

```python
# Fetch only needed attributes
response = table.query(
    KeyConditionExpression=Key('PK').eq('USER#alice'),
    ProjectionExpression='#name, email, created',
    ExpressionAttributeNames={'#name': 'name'}  # 'name' is reserved
)
```

### 4. Consistent Reads

```python
# Eventually consistent read (default, 1 RCU per 4KB)
response = table.get_item(
    Key={'PK': 'USER#alice', 'SK': 'PROFILE#'}
)

# Strongly consistent read (2x RCU cost)
response = table.get_item(
    Key={'PK': 'USER#alice', 'SK': 'PROFILE#'},
    ConsistentRead=True
)
```

## Common Anti-Patterns to Avoid

### ❌ Don't: Use Scans for Regular Access
```python
# BAD: Full table scan
response = table.scan(
    FilterExpression=Attr('email').eq('john@example.com')
)
```

### ✅ Do: Use Queries or GSI
```python
# GOOD: Query with GSI
response = table.query(
    IndexName='EmailIndex',
    KeyConditionExpression=Key('email').eq('john@example.com')
)
```

### ❌ Don't: Store Large Attributes
```python
# BAD: 400KB item with embedded data
item = {
    'PK': 'USER#alice',
    'SK': 'PROFILE#',
    'large_binary_data': b'...' * 100000  # Approaching 400KB limit
}
```

### ✅ Do: Store Large Data in S3
```python
# GOOD: Reference to S3
s3.put_object(Bucket='my-bucket', Key='user/alice/data.bin', Body=large_data)
item = {
    'PK': 'USER#alice',
    'SK': 'PROFILE#',
    's3_key': 'user/alice/data.bin'
}
```

### ❌ Don't: Use Too Many GSIs
```python
# BAD: 10+ GSIs for every possible query
# Each GSI doubles write costs and adds complexity
```

### ✅ Do: Overload GSIs and Use Composite Keys
```python
# GOOD: 2-3 well-designed GSIs covering multiple access patterns
```

## Cost Optimization

### 1. Use On-Demand for Variable Workloads
```python
# Switch to on-demand
table.update(
    BillingMode='PAY_PER_REQUEST'
)
```

### 2. Enable Auto-Scaling for Provisioned
```python
import boto3

autoscaling = boto3.client('application-autoscaling')

# Register table as scalable target
autoscaling.register_scalable_target(
    ServiceNamespace='dynamodb',
    ResourceId='table/my-table',
    ScalableDimension='dynamodb:table:ReadCapacityUnits',
    MinCapacity=5,
    MaxCapacity=100
)

# Create scaling policy
autoscaling.put_scaling_policy(
    ServiceNamespace='dynamodb',
    ResourceId='table/my-table',
    ScalableDimension='dynamodb:table:ReadCapacityUnits',
    PolicyName='MyTableReadScaling',
    PolicyType='TargetTrackingScaling',
    TargetTrackingScalingPolicyConfiguration={
        'TargetValue': 70.0,
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'DynamoDBReadCapacityUtilization'
        }
    }
)
```

### 3. Use TTL for Automatic Data Expiration
```python
# Enable TTL on table
table.meta.client.update_time_to_live(
    TableName='my-table',
    TimeToLiveSpecification={
        'Enabled': True,
        'AttributeName': 'expiration_time'
    }
)

# Set expiration time (Unix epoch)
import time
item = {
    'PK': 'SESSION#abc123',
    'SK': 'METADATA#',
    'expiration_time': int(time.time()) + 3600  # Expire in 1 hour
}
```

This comprehensive reference covers DynamoDB design patterns for building scalable, performant NoSQL applications on AWS.
