# Database Testing Playbook

## SQL Database Testing

### Schema Testing
```sql
-- Verify table exists
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'users';

-- Verify columns
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users';

-- Verify constraints
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'users';

-- Verify indexes
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'users';

-- Verify foreign keys
SELECT tc.constraint_name,
       tc.table_name,
       kcu.column_name,
       ccu.table_name AS foreign_table_name,
       ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name = 'orders';
```

### Data Integrity Testing
```sql
-- Test NOT NULL constraint
INSERT INTO users (email) VALUES (NULL);
-- Should fail

-- Test UNIQUE constraint
INSERT INTO users (email) VALUES ('test@example.com');
INSERT INTO users (email) VALUES ('test@example.com');
-- Second should fail

-- Test CHECK constraint
INSERT INTO users (age) VALUES (-5);
-- Should fail if CHECK age >= 0

-- Test foreign key constraint
INSERT INTO orders (user_id) VALUES (99999);
-- Should fail if user 99999 doesn't exist

-- Test cascade delete
DELETE FROM users WHERE id = 1;
-- Related orders should also be deleted

-- Test default values
INSERT INTO users (email) VALUES ('test@example.com');
SELECT created_at FROM users WHERE email = 'test@example.com';
-- created_at should have default timestamp
```

### Query Performance Testing
```sql
-- Explain analyze query
EXPLAIN ANALYZE
SELECT u.*, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > NOW() - INTERVAL '30 days'
GROUP BY u.id
HAVING COUNT(o.id) > 5;

-- Check for sequential scans (bad)
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';
-- Should use Index Scan, not Seq Scan

-- Test index usage
CREATE INDEX idx_users_email ON users(email);
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';
-- Should show Index Scan on idx_users_email

-- Test slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- > 1 second
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Transaction Testing
```sql
-- Test ACID properties
BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
  UPDATE accounts SET balance = balance + 100 WHERE id = 2;
  -- Verify both updates
  SELECT SUM(balance) FROM accounts WHERE id IN (1, 2);
COMMIT;

-- Test rollback
BEGIN;
  DELETE FROM users WHERE id = 1;
  -- Verify deleted
  SELECT * FROM users WHERE id = 1;  -- Should be empty
ROLLBACK;
-- Verify restored
SELECT * FROM users WHERE id = 1;  -- Should exist

-- Test isolation levels
-- Session 1:
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
UPDATE accounts SET balance = 1000 WHERE id = 1;

-- Session 2:
SELECT balance FROM accounts WHERE id = 1;  -- Should see old value

-- Session 1:
COMMIT;

-- Session 2:
SELECT balance FROM accounts WHERE id = 1;  -- Should see new value
```

## NoSQL Database Testing

### MongoDB Testing
```javascript
// Test document validation
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      required: ['email', 'password'],
      properties: {
        email: { bsonType: 'string', pattern: '^.+@.+$' },
        age: { bsonType: 'int', minimum: 18, maximum: 120 }
      }
    }
  }
});

// Valid insert
db.users.insertOne({
  email: 'test@example.com',
  password: 'hashed_password',
  age: 25
});

// Invalid insert (should fail)
db.users.insertOne({
  email: 'invalid-email',
  age: 15
});

// Test index
db.users.createIndex({ email: 1 }, { unique: true });

// Test duplicate (should fail)
db.users.insertOne({ email: 'test@example.com' });

// Test query performance
db.users.find({ email: 'test@example.com' }).explain('executionStats');

// Should use index:
// executionStats.executionStages.stage === 'IXSCAN'
```

### Redis Testing
```javascript
// Test string operations
await redis.set('user:1:name', 'John Doe');
const name = await redis.get('user:1:name');
expect(name).toBe('John Doe');

// Test expiration
await redis.setex('session:abc', 3600, 'user123');
const ttl = await redis.ttl('session:abc');
expect(ttl).toBeGreaterThan(0);

// Test hash
await redis.hset('user:1', 'name', 'John', 'age', 30);
const userData = await redis.hgetall('user:1');
expect(userData).toEqual({ name: 'John', age: '30' });

// Test list
await redis.lpush('queue:tasks', 'task1', 'task2', 'task3');
const task = await redis.rpop('queue:tasks');
expect(task).toBe('task1');

// Test set
await redis.sadd('tags:post:1', 'javascript', 'testing', 'qa');
const tags = await redis.smembers('tags:post:1');
expect(tags).toHaveLength(3);
```

## Database Migration Testing

### Forward Migration Test
```typescript
describe('Migration: Add email_verified column', () => {
  beforeEach(async () => {
    await db.migrate.rollback();
  });

  it('should add email_verified column', async () => {
    // Run migration
    await db.migrate.latest();

    // Verify column exists
    const columns = await db('users').columnInfo();
    expect(columns.email_verified).toBeDefined();
    expect(columns.email_verified.type).toBe('boolean');
    expect(columns.email_verified.defaultValue).toBe(false);
  });

  it('should preserve existing data', async () => {
    // Insert test data before migration
    await db.migrate.rollback();
    await db('users').insert({
      email: 'test@example.com',
      password: 'hashed'
    });

    // Run migration
    await db.migrate.latest();

    // Verify data preserved
    const user = await db('users').where({ email: 'test@example.com' }).first();
    expect(user).toBeDefined();
    expect(user.email_verified).toBe(false);  // Default value
  });
});
```

### Rollback Migration Test
```typescript
describe('Migration Rollback', () => {
  it('should rollback cleanly', async () => {
    // Run migration
    await db.migrate.latest();

    // Verify column exists
    let columns = await db('users').columnInfo();
    expect(columns.email_verified).toBeDefined();

    // Rollback
    await db.migrate.rollback();

    // Verify column removed
    columns = await db('users').columnInfo();
    expect(columns.email_verified).toBeUndefined();
  });

  it('should preserve data after rollback', async () => {
    // Insert data
    await db('users').insert({
      email: 'test@example.com',
      password: 'hashed'
    });

    // Migrate and rollback
    await db.migrate.latest();
    await db.migrate.rollback();

    // Verify data still exists
    const user = await db('users').where({ email: 'test@example.com' }).first();
    expect(user).toBeDefined();
  });
});
```

## Database Performance Testing

### Load Testing Database
```typescript
import { performance } from 'perf_hooks';

describe('Database Performance', () => {
  it('should handle 1000 concurrent inserts', async () => {
    const startTime = performance.now();
    
    const promises = Array(1000).fill(null).map((_, i) =>
      db('users').insert({
        email: `user${i}@example.com`,
        password: 'hashed'
      })
    );
    
    await Promise.all(promises);
    const duration = performance.now() - startTime;
    
    expect(duration).toBeLessThan(5000);  // < 5 seconds
  });

  it('should query large dataset efficiently', async () => {
    // Insert 10,000 records
    const users = Array(10000).fill(null).map((_, i) => ({
      email: `user${i}@example.com`,
      created_at: new Date()
    }));
    await db('users').insert(users);

    // Query with index
    const startTime = performance.now();
    const result = await db('users')
      .where('email', 'user5000@example.com')
      .first();
    const duration = performance.now() - startTime;

    expect(result).toBeDefined();
    expect(duration).toBeLessThan(50);  // < 50ms
  });
});
```

## Database Testing Checklist

### Schema
- [ ] Tables created correctly
- [ ] Columns have correct data types
- [ ] NOT NULL constraints enforced
- [ ] UNIQUE constraints enforced
- [ ] CHECK constraints enforced
- [ ] Default values set
- [ ] Foreign keys configured
- [ ] Indexes created
- [ ] Cascade rules correct

### Data Integrity
- [ ] Duplicate prevention
- [ ] Referential integrity
- [ ] Data validation
- [ ] Transaction atomicity
- [ ] Isolation levels correct
- [ ] Cascade deletes work
- [ ] Orphaned records prevented

### Performance
- [ ] Indexes used for queries
- [ ] No sequential scans on large tables
- [ ] Query execution time acceptable
- [ ] Connection pooling configured
- [ ] Slow query log reviewed
- [ ] N+1 queries eliminated

### Migrations
- [ ] Forward migration succeeds
- [ ] Rollback succeeds
- [ ] Data preserved
- [ ] Idempotent (can run multiple times)
- [ ] Reversible
- [ ] Tested in staging
