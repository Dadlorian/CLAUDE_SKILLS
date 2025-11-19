# Database Optimization Guide

Complete guide to optimizing PostgreSQL database performance.

## Query Optimization

### Use EXPLAIN ANALYZE

```sql
EXPLAIN ANALYZE
SELECT u.*, COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON p.user_id = u.id
GROUP BY u.id;
```

Look for:
- **Seq Scan**: Full table scan (bad for large tables)
- **Index Scan**: Using index (good)
- **Execution time**: Total time taken
- **Rows**: Estimated vs actual rows

### Index Strategies

**Single Column Index**:
```sql
-- Fast lookups by email
CREATE INDEX idx_users_email ON users(email);

-- Usage
SELECT * FROM users WHERE email = 'john@example.com';
-- Uses: Index Scan using idx_users_email
```

**Composite Index** (column order matters!):
```sql
-- Index for common query pattern
CREATE INDEX idx_posts_user_created ON posts(user_id, created_at DESC);

-- Optimized query
SELECT * FROM posts
WHERE user_id = '123'
ORDER BY created_at DESC
LIMIT 10;
-- Uses: Index Scan using idx_posts_user_created
```

**Partial Index**:
```sql
-- Index only active users
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- Optimized for
SELECT * FROM users WHERE status = 'active' AND email = 'john@example.com';
```

**Expression Index**:
```sql
-- Index for case-insensitive search
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- Usage
SELECT * FROM users WHERE LOWER(email) = LOWER('John@Example.com');
```

## N+1 Query Problem

### Problem

```typescript
// ❌ Bad: N+1 queries
const users = await User.findAll(); // 1 query

for (const user of users) {
  user.posts = await Post.findAll({ where: { userId: user.id } }); // N queries
}
// Total: 1 + N queries!
```

### Solution 1: JOIN

```typescript
// ✅ Good: Single query with join
const users = await User.findAll({
  include: [{ model: Post }]
});
// Total: 1 query
```

### Solution 2: DataLoader (GraphQL)

```typescript
import DataLoader from 'dataloader';

const postLoader = new DataLoader(async (userIds: string[]) => {
  const posts = await Post.findAll({
    where: { userId: { [Op.in]: userIds } }
  });

  const postsByUserId = new Map<string, Post[]>();
  posts.forEach(post => {
    if (!postsByUserId.has(post.userId)) {
      postsByUserId.set(post.userId, []);
    }
    postsByUserId.get(post.userId)!.push(post);
  });

  return userIds.map(id => postsByUserId.get(id) || []);
});

// Usage
const users = await User.findAll();
await Promise.all(
  users.map(async user => {
    user.posts = await postLoader.load(user.id);
  })
);
```

## Connection Pooling

```typescript
import { Pool } from 'pg';

const pool = new Pool({
  max: 20,                      // Max connections in pool
  min: 5,                       // Min connections to maintain
  idleTimeoutMillis: 30000,     // Close idle connections after 30s
  connectionTimeoutMillis: 2000, // Wait max 2s for connection
  maxUses: 7500,                // Recycle connection after 7500 uses
});

// Get connection from pool
const client = await pool.connect();
try {
  await client.query('SELECT * FROM users');
} finally {
  client.release(); // Return to pool
}
```

## Pagination Strategies

### Offset-Based (Simple but slow for large offsets)

```sql
-- Page 1 (fast)
SELECT * FROM posts ORDER BY created_at DESC LIMIT 20 OFFSET 0;

-- Page 1000 (slow - scans 20,000 rows)
SELECT * FROM posts ORDER BY created_at DESC LIMIT 20 OFFSET 20000;
```

### Cursor-Based (Efficient for large datasets)

```sql
-- First page
SELECT * FROM posts ORDER BY created_at DESC, id DESC LIMIT 20;

-- Next page (using last item's values)
SELECT * FROM posts
WHERE (created_at, id) < ('2025-01-15 10:00:00', '12345')
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Need composite index
CREATE INDEX idx_posts_cursor ON posts(created_at DESC, id DESC);
```

### Keyset Pagination (Best performance)

```typescript
async function getPosts(afterCursor?: string, limit = 20) {
  let query = 'SELECT * FROM posts';
  const params: any[] = [];

  if (afterCursor) {
    const decoded = Buffer.from(afterCursor, 'base64').toString();
    const [createdAt, id] = decoded.split('|');
    query += ' WHERE (created_at, id) < ($1, $2)';
    params.push(createdAt, id);
  }

  query += ' ORDER BY created_at DESC, id DESC LIMIT $' + (params.length + 1);
  params.push(limit);

  const posts = await db.query(query, params);

  const nextCursor = posts.length === limit
    ? Buffer.from(`${posts[posts.length - 1].created_at}|${posts[posts.length - 1].id}`).toString('base64')
    : null;

  return { posts, nextCursor };
}
```

## Query Caching

### Database-Level Caching

```sql
-- Materialized View (pre-computed results)
CREATE MATERIALIZED VIEW user_post_counts AS
SELECT
  u.id,
  u.name,
  COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON p.user_id = u.id
GROUP BY u.id, u.name;

-- Create index on materialized view
CREATE INDEX idx_user_post_counts_id ON user_post_counts(id);

-- Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY user_post_counts;
```

### Application-Level Caching

```typescript
import Redis from 'ioredis';

const redis = new Redis();

async function getUser(id: string) {
  const cacheKey = `user:${id}`;

  // Try cache first
  const cached = await redis.get(cacheKey);
  if (cached) {
    return JSON.parse(cached);
  }

  // Cache miss
  const user = await db.query('SELECT * FROM users WHERE id = $1', [id]);

  if (user) {
    // Cache for 1 hour
    await redis.setex(cacheKey, 3600, JSON.stringify(user));
  }

  return user;
}

// Invalidate on update
async function updateUser(id: string, data: any) {
  const user = await db.query(
    'UPDATE users SET name = $1 WHERE id = $2 RETURNING *',
    [data.name, id]
  );

  // Invalidate cache
  await redis.del(`user:${id}`);

  return user;
}
```

## Bulk Operations

### Bulk Insert

```typescript
// ❌ Bad: Multiple inserts
for (const user of users) {
  await db.query('INSERT INTO users (name, email) VALUES ($1, $2)', [user.name, user.email]);
}

// ✅ Good: Single bulk insert
const values = users.map((u, i) => `($${i * 2 + 1}, $${i * 2 + 2})`).join(',');
const params = users.flatMap(u => [u.name, u.email]);

await db.query(
  `INSERT INTO users (name, email) VALUES ${values}`,
  params
);

// ✅ Better: Using UNNEST
await db.query(
  `INSERT INTO users (name, email)
   SELECT * FROM UNNEST($1::text[], $2::text[])`,
  [users.map(u => u.name), users.map(u => u.email)]
);
```

## Database Monitoring

### Slow Query Log

```sql
-- Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 100; -- Log queries > 100ms
SELECT pg_reload_conf();

-- View slow queries
SELECT
  query,
  calls,
  total_time,
  mean_time,
  max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Index Usage Stats

```sql
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE 'pg_toast%'
ORDER BY schemaname, tablename;
```

### Table Bloat

```sql
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS external_size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Optimization Checklist

- [ ] Add indexes for WHERE, JOIN, ORDER BY columns
- [ ] Use composite indexes for multi-column queries
- [ ] Analyze queries with EXPLAIN ANALYZE
- [ ] Eliminate N+1 queries
- [ ] Use connection pooling
- [ ] Implement query result caching
- [ ] Use cursor-based pagination for large datasets
- [ ] Monitor slow queries
- [ ] Regular VACUUM and ANALYZE
- [ ] Remove unused indexes
- [ ] Use prepared statements
- [ ] Batch bulk operations

## Advanced Techniques

### Partitioning

```sql
-- Partition large tables by date
CREATE TABLE posts (
  id UUID PRIMARY KEY,
  content TEXT,
  created_at TIMESTAMP NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE posts_2024 PARTITION OF posts
  FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE posts_2025 PARTITION OF posts
  FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

### Read Replicas

```typescript
// Master for writes
const masterPool = new Pool({
  host: 'master.db.example.com',
  // ...
});

// Replica for reads
const replicaPool = new Pool({
  host: 'replica.db.example.com',
  // ...
});

// Write to master
async function createUser(data: any) {
  return masterPool.query('INSERT INTO users ...');
}

// Read from replica
async function getUsers() {
  return replicaPool.query('SELECT * FROM users');
}
```

## References

- PostgreSQL Performance Tuning: https://wiki.postgresql.org/wiki/Performance_Optimization
- Use The Index, Luke: https://use-the-index-luke.com/
- pg_stat_statements: https://www.postgresql.org/docs/current/pgstatstatements.html
