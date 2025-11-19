# NoSQL Database Design Template

## Purpose
Use this template when designing a NoSQL database (document store, key-value, wide-column, or graph database).

## Step 1: NoSQL Type Selection

### Document Store (MongoDB, Couchbase, DynamoDB)
**Best for**:
- Flexible, evolving schemas
- Nested/hierarchical data
- JSON-like documents
- Content management systems

**Use when**:
- Data naturally groups into documents
- Relationships are mostly one-to-many embedded
- Need flexible schema evolution

### Key-Value Store (Redis, DynamoDB, Memcached)
**Best for**:
- Simple lookups by key
- Caching layer
- Session storage
- High-throughput reads/writes

**Use when**:
- Access pattern is always by primary key
- Need sub-millisecond latency
- Data model is simple key → value

### Wide-Column Store (Cassandra, ScyllaDB, HBase)
**Best for**:
- Time-series data
- Event logging
- High write throughput
- Massive scale (petabytes)

**Use when**:
- Write-heavy workloads
- Need linear scalability
- Time-series or append-only data

### Graph Database (Neo4j, Neptune, ArangoDB)
**Best for**:
- Complex relationships
- Social networks
- Recommendation engines
- Fraud detection

**Use when**:
- Relationships are first-class citizens
- Need traversal queries
- Many-to-many relationships dominate

**Selected Type**: ________________

**Reasoning**:
-
-

## Step 2: Access Pattern Analysis

### Critical Queries
List all query patterns (NoSQL design is query-driven):

1. **Query Pattern**: Get user by ID
   - **Frequency**: Very high (1000/s)
   - **Latency requirement**: < 10ms
   - **Data access**: user_id → user document

2. **Query Pattern**:
   - **Frequency**:
   - **Latency requirement**:
   - **Data access**:

3. **Query Pattern**:
   - **Frequency**:
   - **Latency requirement**:
   - **Data access**:

### Access Pattern Priorities
Rank patterns by importance (1 = highest):
1.
2.
3.

## Step 3: Data Modeling

### For Document Stores (MongoDB)

#### Embedding vs Referencing Decision Matrix

| Scenario | Embed | Reference |
|----------|-------|-----------|
| One-to-few relationship | ✅ Embed | |
| One-to-many relationship | Consider | ✅ Reference |
| One-to-millions relationship | | ✅ Reference |
| Data changes frequently | | ✅ Reference |
| Data read together | ✅ Embed | |
| Need atomicity across entities | ✅ Embed | |

#### Collection Design

```javascript
// Collection: users
{
  _id: ObjectId("..."),
  username: "johndoe",
  email: "john@example.com",

  // Embedded document (one-to-one or one-to-few)
  profile: {
    firstName: "John",
    lastName: "Doe",
    avatar: "https://...",
    preferences: {
      theme: "dark",
      language: "en"
    }
  },

  // Embedded array (one-to-few, items rarely change)
  addresses: [
    {
      type: "home",
      street: "123 Main St",
      city: "New York",
      country: "USA"
    }
  ],

  // Reference (one-to-many, items change frequently)
  orderIds: [],  // Don't embed order IDs if there are thousands

  createdAt: ISODate("2024-01-15T10:30:00Z"),
  updatedAt: ISODate("2024-01-15T10:30:00Z")
}

// Collection: orders (separate collection)
{
  _id: ObjectId("..."),
  userId: ObjectId("..."),  // Reference to user
  status: "delivered",

  // Embed order items (one-to-few, read together, atomic updates)
  items: [
    {
      productId: ObjectId("..."),
      name: "Product Name",  // Denormalized for performance
      quantity: 2,
      unitPrice: 29.99
    }
  ],

  totalAmount: 59.98,
  createdAt: ISODate("2024-01-15T10:30:00Z")
}
```

#### Schema Validation

```javascript
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["username", "email", "createdAt"],
      properties: {
        username: {
          bsonType: "string",
          minLength: 3,
          maxLength: 50
        },
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        },
        profile: {
          bsonType: "object",
          properties: {
            firstName: { bsonType: "string" },
            lastName: { bsonType: "string" }
          }
        }
      }
    }
  }
});
```

#### Index Strategy

```javascript
// Single field index
db.users.createIndex({ email: 1 }, { unique: true });

// Compound index (order matters!)
db.orders.createIndex({ userId: 1, createdAt: -1 });

// Text index (for search)
db.products.createIndex({ name: "text", description: "text" });

// Geospatial index
db.stores.createIndex({ location: "2dsphere" });

// TTL index (auto-delete after time)
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 });

// Partial index (filter)
db.orders.createIndex(
  { userId: 1, createdAt: -1 },
  { partialFilterExpression: { status: { $in: ["pending", "processing"] } } }
);
```

### For Key-Value Stores (Redis)

#### Key Design Patterns

```
# Pattern 1: Simple key-value
user:123 → { "username": "johndoe", "email": "..." }

# Pattern 2: Namespaced keys
app:production:user:123
app:staging:user:123

# Pattern 3: Hash (field-value pairs)
user:123 → { username: "johndoe", email: "john@...", age: 30 }

# Pattern 4: List (ordered collection)
user:123:orders → [order:1, order:2, order:3]

# Pattern 5: Set (unique collection)
user:123:tags → {java, python, nodejs}

# Pattern 6: Sorted Set (scored collection)
leaderboard → {user1: 1000, user2: 950, user3: 900}
```

#### Data Structures

```redis
# String (simple value)
SET user:123:name "John Doe"
GET user:123:name

# Hash (object with fields)
HSET user:123 username "johndoe" email "john@example.com" age 30
HGETALL user:123
HGET user:123 email

# List (ordered)
LPUSH user:123:notifications "New message"
LRANGE user:123:notifications 0 9  # First 10

# Set (unique items)
SADD user:123:tags "python" "nodejs"
SMEMBERS user:123:tags

# Sorted Set (ranked)
ZADD leaderboard 1000 "user:123"
ZREVRANGE leaderboard 0 9 WITHSCORES  # Top 10

# TTL (expiration)
SET session:xyz "..." EX 3600  # Expires in 1 hour
EXPIRE user:123:cache 300  # 5 minutes
```

### For Wide-Column Stores (Cassandra)

#### Table Design (One Table Per Query Pattern!)

```cql
-- Query: Get user by user_id
CREATE TABLE users_by_id (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    email TEXT,
    created_at TIMESTAMP
);

-- Query: Get user's recent orders (user_id + time range)
CREATE TABLE orders_by_user (
    user_id BIGINT,
    created_at TIMESTAMP,
    order_id BIGINT,
    status TEXT,
    total_amount DECIMAL,
    PRIMARY KEY ((user_id), created_at, order_id)
) WITH CLUSTERING ORDER BY (created_at DESC, order_id DESC);

-- Query: Get orders by status (for admin)
CREATE TABLE orders_by_status (
    status TEXT,
    created_at TIMESTAMP,
    order_id BIGINT,
    user_id BIGINT,
    total_amount DECIMAL,
    PRIMARY KEY ((status), created_at, order_id)
) WITH CLUSTERING ORDER BY (created_at DESC);

-- Query: Get product orders (for analytics)
CREATE TABLE orders_by_product (
    product_id BIGINT,
    ordered_at TIMESTAMP,
    order_id BIGINT,
    user_id BIGINT,
    quantity INT,
    PRIMARY KEY ((product_id), ordered_at, order_id)
) WITH CLUSTERING ORDER BY (ordered_at DESC);
```

#### Partition Key Selection

**Rules**:
- Determines data distribution across nodes
- Should have high cardinality (many unique values)
- Should distribute data evenly
- Avoid hot partitions

**Good partition keys**:
- ✅ user_id (if many users)
- ✅ (user_id, month) (for time-series with many users)
- ✅ product_id (if many products)

**Bad partition keys**:
- ❌ status (only few values, creates hot partitions)
- ❌ country (uneven distribution)
- ❌ boolean flags

### For Graph Databases (Neo4j)

#### Node and Relationship Design

```cypher
// Nodes (entities)
CREATE (u:User {
  userId: 123,
  username: "johndoe",
  email: "john@example.com",
  createdAt: datetime()
})

CREATE (p:Product {
  productId: 456,
  name: "Laptop",
  price: 999.99
})

CREATE (o:Order {
  orderId: 789,
  totalAmount: 999.99,
  createdAt: datetime()
})

// Relationships
CREATE (u)-[:PLACED {timestamp: datetime()}]->(o)
CREATE (o)-[:CONTAINS {quantity: 1}]->(p)
CREATE (u)-[:VIEWED {timestamp: datetime()}]->(p)

// Complex relationships
CREATE (u1:User)-[:FOLLOWS {since: datetime()}]->(u2:User)
CREATE (u1)-[:FRIEND {mutualSince: datetime()}]-(u2)
```

#### Index Strategy

```cypher
// Unique constraint (creates index)
CREATE CONSTRAINT user_id_unique FOR (u:User) REQUIRE u.userId IS UNIQUE;

// Index for lookups
CREATE INDEX user_email FOR (u:User) ON (u.email);

// Composite index
CREATE INDEX order_user_date FOR (o:Order) ON (o.userId, o.createdAt);

// Full-text index
CREATE FULLTEXT INDEX product_search FOR (p:Product) ON EACH [p.name, p.description];
```

## Step 4: Denormalization Strategy

### When to Denormalize
- [ ] Improve read performance
- [ ] Reduce number of queries/lookups
- [ ] Data is read together
- [ ] Data changes infrequently

### Denormalization Patterns

```javascript
// Pattern 1: Embed frequently accessed fields
{
  orderId: 123,
  userId: 456,
  userEmail: "john@example.com",  // Denormalized from users collection
  userName: "John Doe",  // Denormalized
  items: [...]
}

// Pattern 2: Pre-compute aggregates
{
  userId: 456,
  totalOrders: 42,  // Pre-computed count
  lifetimeValue: 4299.99,  // Pre-computed sum
  lastOrderDate: ISODate("...")  // Pre-computed max
}

// Pattern 3: Maintain multiple representations
// users collection
{ _id: 123, username: "johndoe", email: "..." }

// users_by_email collection (for email lookup)
{ _id: "john@example.com", userId: 123, username: "johndoe" }
```

## Step 5: Consistency & Transaction Strategy

### Consistency Model
- [ ] Strong consistency (wait for all replicas)
- [ ] Eventual consistency (faster, may see stale data)
- [ ] Session consistency (read your own writes)

### Transaction Approach

**MongoDB** (multi-document transactions):
```javascript
const session = client.startSession();
session.startTransaction();

try {
  await users.updateOne({ _id: userId }, { $inc: { balance: -100 } }, { session });
  await orders.insertOne({ userId, amount: 100 }, { session });

  await session.commitTransaction();
} catch (err) {
  await session.abortTransaction();
  throw err;
} finally {
  session.endSession();
}
```

**Cassandra** (lightweight transactions):
```cql
-- Use sparingly (performance impact)
INSERT INTO users (user_id, username, email)
VALUES (123, 'johndoe', 'john@example.com')
IF NOT EXISTS;

UPDATE accounts
SET balance = balance - 100
WHERE account_id = 123
IF balance >= 100;
```

## Step 6: Scalability Planning

### Sharding/Partitioning
**Shard key**: ________________

**Sharding strategy**:
- [ ] Hash-based (even distribution)
- [ ] Range-based (range queries)
- [ ] Geographic (data locality)

**MongoDB sharding**:
```javascript
sh.enableSharding("mydb")
sh.shardCollection("mydb.orders", { userId: 1, createdAt: 1 })
```

### Replication
**Replication factor**: ________ (3 recommended)

**Read preference**:
- [ ] Primary (strong consistency)
- [ ] Primary preferred
- [ ] Secondary (lower latency, eventual consistency)
- [ ] Nearest (lowest latency)

## Step 7: Migration & Backfill

### Migration Script

```javascript
// Migrate from SQL to MongoDB
async function migrateSQLToMongo() {
  const sqlUsers = await sqlDB.query('SELECT * FROM users');

  const mongoUsers = sqlUsers.rows.map(user => ({
    _id: new ObjectId(),
    userId: user.user_id,
    username: user.username,
    email: user.email,
    profile: {
      firstName: user.first_name,
      lastName: user.last_name
    },
    createdAt: new Date(user.created_at)
  }));

  await mongoDB.collection('users').insertMany(mongoUsers);
}
```

## Step 8: Monitoring

### Key Metrics
- [ ] Query latency (p50, p95, p99)
- [ ] Throughput (ops/second)
- [ ] Index usage
- [ ] Collection/table sizes
- [ ] Replication lag
- [ ] Connection pool utilization

### MongoDB Monitoring

```javascript
// Slow queries
db.setProfilingLevel(1, { slowms: 100 });
db.system.profile.find().limit(10).sort({ ts: -1 });

// Collection stats
db.collection.stats();

// Index usage
db.collection.aggregate([{ $indexStats: {} }]);
```

## Checklist

- [ ] NoSQL type selected based on access patterns
- [ ] All query patterns documented
- [ ] Data model optimized for most frequent queries
- [ ] Denormalization strategy defined
- [ ] Indexes created for all query patterns
- [ ] Sharding/partitioning strategy defined
- [ ] Replication configured
- [ ] Consistency model selected
- [ ] Migration plan tested
- [ ] Monitoring and alerting configured

## Resources

- [MongoDB Data Modeling Guide](https://www.mongodb.com/docs/manual/core/data-modeling-introduction/)
- [Cassandra Data Modeling Best Practices](https://cassandra.apache.org/doc/latest/data_modeling/)
- [Redis Data Structures](https://redis.io/docs/data-types/)
- [Neo4j Graph Data Modeling](https://neo4j.com/developer/guide-data-modeling/)

---

**Template Version**: 1.0
**Last Updated**: 2025-11-19
