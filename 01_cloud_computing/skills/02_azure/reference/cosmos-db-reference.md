# Azure Cosmos DB Reference

## Overview

Azure Cosmos DB is a globally distributed, multi-model NoSQL database service designed for mission-critical applications requiring:
- Single-digit millisecond latency at any scale
- 99.999% availability SLA
- Global distribution with multi-region writes
- Multiple consistency models
- Comprehensive SLAs for throughput, consistency, availability, and latency

## API Options

### SQL (Core) API
**Use Case**: Document-based data with SQL-like query syntax
**Data Model**: JSON documents
**Query Language**: SQL-like syntax with JavaScript expressions
**Best For**: New applications, flexible schemas, rich query capabilities

**Example**:
```sql
SELECT c.id, c.name, c.address.city
FROM customers c
WHERE c.address.state = 'CA'
ORDER BY c.name
```

**When to Choose**:
- Starting a new Cosmos DB project
- Need rich query capabilities
- JSON document storage
- Flexible schema requirements

### MongoDB API
**Use Case**: MongoDB workload migration to Azure
**Data Model**: BSON documents
**Query Language**: MongoDB Query Language (MQL)
**Best For**: Existing MongoDB applications, minimal code changes

**Wire Protocol**: MongoDB 4.0, 4.2, 5.0, 6.0 support
**Compatibility**: Can use existing MongoDB drivers and tools

**Migration Path**:
- Minimal application changes
- Change connection string
- May need to adjust for Cosmos DB-specific features

### Cassandra API
**Use Case**: Wide-column store, Cassandra workload migration
**Data Model**: Column families/tables
**Query Language**: CQL (Cassandra Query Language)
**Best For**: Existing Cassandra applications, time-series data

**Compatibility**: Cassandra 3.x and 4.x wire protocol
**Drivers**: Use native Cassandra drivers

**Use Cases**:
- IoT telemetry
- Time-series data
- Event sourcing
- Recommendation engines

### Gremlin (Graph) API
**Use Case**: Graph databases, relationship-heavy data
**Data Model**: Vertices and edges
**Query Language**: Gremlin (Apache TinkerPop)
**Best For**: Social networks, recommendation engines, fraud detection

**Example Query**:
```gremlin
g.V().hasLabel('person')
  .has('firstName', 'John')
  .outE('knows')
  .inV()
  .values('firstName')
```

**Use Cases**:
- Social networks
- Recommendation systems
- Fraud detection
- Knowledge graphs
- Network topology

### Table API
**Use Case**: Azure Table Storage migration with premium features
**Data Model**: Key-value pairs
**Query Language**: OData queries
**Best For**: Migrating from Azure Table Storage

**Advantages over Table Storage**:
- Global distribution
- Low latency
- Automatic indexing
- Higher throughput

## Partition Strategy

### Partition Key Selection

**Critical Decision**: Cannot change after container creation

**Good Partition Key Characteristics**:
1. **High Cardinality**: Many distinct values
2. **Even Distribution**: Data spread evenly across partitions
3. **Query Alignment**: Queries include partition key
4. **Storage Balance**: No single partition grows too large

**Examples**:

```json
// Good: User ID for user data
{
  "id": "user123",
  "partitionKey": "user123",  // Each user is a partition
  "name": "John Doe",
  "email": "john@example.com"
}

// Good: Tenant ID for multi-tenant application
{
  "id": "order456",
  "partitionKey": "tenant-abc",  // All tenant data together
  "customerId": "cust789",
  "total": 99.99
}

// Bad: Boolean field (only 2 partitions!)
{
  "id": "item123",
  "partitionKey": "true",  // Don't do this!
  "isActive": true
}

// Bad: Status field with few values
{
  "id": "order789",
  "partitionKey": "pending",  // Only a few status values
  "status": "pending"
}
```

### Synthetic Partition Keys

**Scenario**: Natural partition key has uneven distribution

**Solution**: Combine multiple fields or add suffix

```json
// Combine fields
{
  "id": "order123",
  "partitionKey": "tenant-abc_2024-01",  // Tenant + month
  "tenantId": "tenant-abc",
  "orderDate": "2024-01-15"
}

// Add random suffix for hot partitions
{
  "id": "event123",
  "partitionKey": "device456_7",  // Device + random 0-9
  "deviceId": "device456",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Hierarchical Partition Keys

**Available**: Cosmos DB now supports multi-level partition keys (preview)

```json
{
  "id": "order123",
  "tenantId": "tenant-abc",      // Level 1
  "customerId": "customer456",   // Level 2
  "orderId": "order123"          // Level 3
}
```

## Request Units (RU/s)

### Understanding RUs

**1 RU** = Cost to read a 1 KB document by its ID and partition key (point read)

**Common Operations**:
- Point read (1 KB): 1 RU
- Query (1 KB result): 2-3+ RUs (depends on complexity)
- Write (1 KB): ~5 RUs
- Replace (1 KB): ~5 RUs
- Delete: ~5 RUs
- Stored procedure: Varies by operations

**Factors Affecting RU Cost**:
- Document size
- Property count
- Index complexity
- Query complexity (joins, sorts, filters)
- Consistency level

### Provisioning Models

#### Provisioned Throughput (Manual)
**Model**: Reserve RU/s capacity
**Billing**: Per hour for provisioned RU/s
**Best For**: Predictable, consistent workloads

**Example Pricing**:
- 400 RU/s (minimum): ~$24/month
- 1,000 RU/s: ~$58/month
- 10,000 RU/s: ~$584/month
- 100,000 RU/s: ~$5,840/month

**Container-level**:
```bash
az cosmosdb sql container create \
  --account-name myCosmosAccount \
  --database-name myDatabase \
  --name myContainer \
  --partition-key-path "/partitionKey" \
  --throughput 1000
```

**Database-level** (shared across containers):
```bash
az cosmosdb sql database create \
  --account-name myCosmosAccount \
  --name myDatabase \
  --throughput 1000
```

#### Autoscale
**Model**: Automatically scales between 10% and 100% of max RU/s
**Billing**: Per hour based on actual scaled RU/s
**Best For**: Variable or unpredictable workloads

**Pricing**: ~1.5x of equivalent manual provisioned throughput

**Example**:
- Max 10,000 RU/s
- Scales: 1,000 - 10,000 RU/s
- Pay for actual usage per hour

```bash
az cosmosdb sql container create \
  --account-name myCosmosAccount \
  --database-name myDatabase \
  --name myContainer \
  --partition-key-path "/partitionKey" \
  --max-throughput 10000
```

#### Serverless
**Model**: Pay per request (no provisioned capacity)
**Billing**: $0.25 per million RUs consumed
**Best For**: Dev/test, sporadic workloads, small applications

**Limitations**:
- Single region only
- Maximum 5,000 RU/s per operation
- Maximum 50 GB storage per container
- No SLA guarantees

**Best For**:
- Development and testing
- Applications with sporadic traffic
- Proofs of concept
- Small-scale applications

## Consistency Levels

### Strong
**Guarantee**: Linearizability - reads guaranteed to return most recent committed write
**Latency**: Highest read latency
**Availability**: Lower availability during outages
**Use Case**: Financial systems, inventory management

**Behavior**:
- Reads in any region reflect all writes
- Requires quorum read
- Higher latency (round-trip to multiple regions)

### Bounded Staleness
**Guarantee**: Reads lag behind writes by at most K versions or T time
**Latency**: Moderate
**Availability**: Better than Strong
**Use Case**: Collaborative apps, auctions with time constraints

**Configuration**:
- Max lag: 100,000 operations OR 5 minutes (default)
- Configurable per account

**Example**:
```csharp
// Max 100 versions or 5 minutes lag
client = new CosmosClient(endpoint, key, new CosmosClientOptions
{
    ConsistencyLevel = ConsistencyLevel.BoundedStaleness
});
```

### Session (Default)
**Guarantee**: Consistent within a user session
**Latency**: Low
**Availability**: High
**Use Case**: Most applications (90%+ use cases)

**Behavior**:
- Single client sees consistent data
- Own writes always visible
- Monotonic reads and writes

**Best Balance**: Performance, consistency, and availability

### Consistent Prefix
**Guarantee**: Reads never see out-of-order writes
**Latency**: Low
**Availability**: High
**Use Case**: Social media updates, news feeds

**Example**: If writes are A, B, C, you might see A, AB, or ABC, but never AC or B

### Eventual
**Guarantee**: Reads will eventually converge
**Latency**: Lowest
**Availability**: Highest
**Use Case**: Non-critical data, caching, analytics

**Behavior**: Highest performance, lowest consistency guarantees

### Consistency Level Selection

```
Strong (Highest Consistency, Lowest Availability)
  ↓
Bounded Staleness
  ↓
Session (DEFAULT - Best Balance)
  ↓
Consistent Prefix
  ↓
Eventual (Lowest Consistency, Highest Availability)
```

## Indexing

### Automatic Indexing

**Default**: All properties automatically indexed

```json
{
  "indexingMode": "consistent",
  "automatic": true,
  "includedPaths": [
    {
      "path": "/*"  // Index everything
    }
  ],
  "excludedPaths": [
    {
      "path": "/\"_etag\"/?"  // Exclude system properties
    }
  ]
}
```

### Custom Indexing Policy

**Optimize for specific query patterns**:

```json
{
  "indexingMode": "consistent",
  "automatic": true,
  "includedPaths": [
    {
      "path": "/name/?",     // Index name property only
      "indexes": [
        {
          "kind": "Range",
          "dataType": "String",
          "precision": -1
        }
      ]
    },
    {
      "path": "/age/?",
      "indexes": [
        {
          "kind": "Range",
          "dataType": "Number",
          "precision": -1
        }
      ]
    }
  ],
  "excludedPaths": [
    {
      "path": "/description/*"  // Don't index description field
    },
    {
      "path": "/largeBinaryData/*"  // Exclude large fields
    }
  ]
}
```

### Composite Indexes

**For ORDER BY on multiple fields or efficient multi-field queries**:

```json
{
  "compositeIndexes": [
    [
      {
        "path": "/category",
        "order": "ascending"
      },
      {
        "path": "/price",
        "order": "descending"
      }
    ]
  ]
}
```

**Enables efficient query**:
```sql
SELECT * FROM c
ORDER BY c.category ASC, c.price DESC
```

### Spatial Indexes

**For geospatial queries**:

```json
{
  "includedPaths": [
    {
      "path": "/location/?",
      "indexes": [
        {
          "kind": "Spatial",
          "dataType": "Point"
        }
      ]
    }
  ]
}
```

**Query**:
```sql
SELECT * FROM c
WHERE ST_DISTANCE(c.location, {'type': 'Point', 'coordinates':[31.9, -4.8]}) < 30000
```

## Change Feed

**Purpose**: Read-only, ordered log of all changes to documents

**Use Cases**:
- Event sourcing
- Real-time analytics
- Data replication
- Triggering workflows
- Materialized views

### Change Feed Processor (Recommended)

```csharp
Container monitoredContainer = client.GetContainer("myDatabase", "myContainer");
Container leaseContainer = client.GetContainer("myDatabase", "leases");

ChangeFeedProcessor changeFeedProcessor = monitoredContainer
    .GetChangeFeedProcessorBuilder<MyDocument>("myProcessor", HandleChangesAsync)
    .WithInstanceName("consoleHost")
    .WithLeaseContainer(leaseContainer)
    .WithStartTime(DateTime.UtcNow.AddDays(-1))
    .Build();

await changeFeedProcessor.StartAsync();

async Task HandleChangesAsync(
    ChangeFeedProcessorContext context,
    IReadOnlyCollection<MyDocument> changes,
    CancellationToken cancellationToken)
{
    foreach (var document in changes)
    {
        Console.WriteLine($"Change detected: {document.id}");
        // Process change
        await ProcessDocumentAsync(document);
    }
}
```

### Push Model (Azure Functions)

```csharp
[FunctionName("CosmosDBTrigger")]
public static void Run(
    [CosmosDBTrigger(
        databaseName: "myDatabase",
        containerName: "myContainer",
        Connection = "CosmosDBConnection",
        LeaseContainerName = "leases",
        CreateLeaseContainerIfNotExists = true)]
    IReadOnlyList<Document> documents,
    ILogger log)
{
    foreach (var doc in documents)
    {
        log.LogInformation($"Document Id: {doc.Id}");
    }
}
```

## Global Distribution

### Multi-Region Setup

```bash
# Add regions
az cosmosdb update \
  --name myCosmosAccount \
  --resource-group myRG \
  --locations regionName=eastus failoverPriority=0 \
  --locations regionName=westus failoverPriority=1 \
  --locations regionName=westeurope failoverPriority=2
```

### Multi-Region Writes

```bash
az cosmosdb update \
  --name myCosmosAccount \
  --resource-group myRG \
  --enable-multiple-write-locations true
```

**Conflict Resolution**:
- **Last Write Wins** (default): Based on _ts timestamp
- **Custom**: User-defined stored procedure
- **Custom Async**: Application handles conflicts

### Automatic Failover

```bash
az cosmosdb failover-priority-change \
  --name myCosmosAccount \
  --resource-group myRG \
  --failover-policies eastus=0 westus=1
```

## Performance Optimization

### Point Reads vs Queries

```csharp
// Fast: Point read (1 RU for 1 KB)
var response = await container.ReadItemAsync<MyDocument>(
    id: "doc123",
    partitionKey: new PartitionKey("partition123"));

// Slower: Query (3+ RUs)
var query = container.GetItemQueryIterator<MyDocument>(
    "SELECT * FROM c WHERE c.id = 'doc123'");
```

### Batch Operations

```csharp
// Efficient: Transactional batch (single partition)
PartitionKey partitionKey = new PartitionKey("partition123");
TransactionalBatch batch = container.CreateTransactionalBatch(partitionKey);

batch.CreateItem(new MyDocument { id = "doc1", partitionKey = "partition123" });
batch.CreateItem(new MyDocument { id = "doc2", partitionKey = "partition123" });
batch.UpsertItem(new MyDocument { id = "doc3", partitionKey = "partition123" });

TransactionalBatchResponse response = await batch.ExecuteAsync();
```

### Bulk Operations

```csharp
List<Task> tasks = new List<Task>();

foreach (var document in documents)
{
    tasks.Add(container.CreateItemAsync(document, new PartitionKey(document.partitionKey)));
}

await Task.WhenAll(tasks);
```

### Query Optimization

```csharp
// Use parameters
var query = new QueryDefinition(
    "SELECT * FROM c WHERE c.category = @category AND c.price > @minPrice")
    .WithParameter("@category", "Electronics")
    .WithParameter("@minPrice", 100);

// Limit results
QueryRequestOptions options = new QueryRequestOptions
{
    MaxItemCount = 100  // Page size
};

// Include partition key when possible
QueryRequestOptions options = new QueryRequestOptions
{
    PartitionKey = new PartitionKey("partition123")
};
```

## Backup and Restore

### Continuous Backup (Recommended)
**Features**: Point-in-time restore (PITR)
**Retention**: 7 or 30 days
**Granularity**: Restore to any second
**Cost**: ~20% of provisioned throughput

```bash
# Enable continuous backup
az cosmosdb create \
  --name myCosmosAccount \
  --resource-group myRG \
  --backup-policy-type Continuous

# Restore to specific point in time
az cosmosdb sql database restore \
  --account-name myCosmosAccount \
  --resource-group myRG \
  --name myDatabase \
  --restore-timestamp "2024-01-15T10:30:00Z"
```

### Periodic Backup (Legacy)
**Features**: Snapshot-based
**Interval**: Every 4 hours (default)
**Retention**: 8 hours (default)
**Restore**: Contact Azure support

## Cost Optimization

### Reserved Capacity
- 1-year: 20% discount
- 3-year: 30% discount
- Applies to provisioned throughput

### Optimize Indexing
- Exclude unnecessary properties
- Reduce index precision
- Use composite indexes

### Right-Size Throughput
- Monitor RU consumption
- Use autoscale for variable workloads
- Share database-level throughput across containers

### TTL (Time to Live)
```csharp
// Container-level default TTL
ContainerProperties containerProperties = new ContainerProperties
{
    Id = "myContainer",
    PartitionKeyPath = "/partitionKey",
    DefaultTimeToLive = 90 * 24 * 60 * 60  // 90 days in seconds
};

// Document-level TTL
{
  "id": "doc123",
  "partitionKey": "partition123",
  "ttl": 3600  // Delete after 1 hour
}
```

## Monitoring

### Key Metrics
- Total Requests
- Total Request Units
- Throttled Requests (429 errors)
- Server-Side Latency
- Replication Latency
- Availability

### Alerts
```bash
# Create alert for throttled requests
az monitor metrics alert create \
  --name HighThrottling \
  --resource-group myRG \
  --scopes /subscriptions/.../cosmosAccounts/myAccount \
  --condition "avg TotalRequests > 100 where StatusCode = 429" \
  --window-size 5m \
  --evaluation-frequency 1m
```

## SDK Best Practices

### Connection Mode
```csharp
CosmosClient client = new CosmosClient(endpoint, key, new CosmosClientOptions
{
    ConnectionMode = ConnectionMode.Direct,  // Better performance
    ConsistencyLevel = ConsistencyLevel.Session
});
```

### Singleton Pattern
```csharp
// One instance per application lifetime
private static readonly Lazy<CosmosClient> _client = new Lazy<CosmosClient>(() =>
    new CosmosClient(endpoint, key));

public static CosmosClient Client => _client.Value;
```

### Retry Policy
```csharp
CosmosClient client = new CosmosClient(endpoint, key, new CosmosClientOptions
{
    MaxRetryAttemptsOnRateLimitedRequests = 9,
    MaxRetryWaitTimeOnRateLimitedRequests = TimeSpan.FromSeconds(30)
});
```
