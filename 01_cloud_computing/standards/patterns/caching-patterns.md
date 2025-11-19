# Caching Architecture Patterns

## Overview

Caching patterns improve application performance by storing frequently accessed data in fast-access storage layers. This guide covers essential caching strategies, implementations, and best practices for building high-performance systems.

## Table of Contents

1. [Cache-Aside Pattern](#cache-aside-pattern)
2. [Write-Through Pattern](#write-through-pattern)
3. [Write-Behind Pattern](#write-behind-pattern)
4. [Refresh-Ahead Pattern](#refresh-ahead-pattern)
5. [Distributed Caching Pattern](#distributed-caching-pattern)
6. [Cache Invalidation Patterns](#cache-invalidation-patterns)
7. [Multi-Level Caching Pattern](#multi-level-caching-pattern)

## Caching Fundamentals

```
┌──────────────────────────────────────────┐
│         Cache Performance Metrics         │
├──────────────────────────────────────────┤
│                                          │
│  Hit Rate: % of requests served by cache│
│  Miss Rate: % of requests missing cache │
│  Latency: Response time (cache vs DB)   │
│  Throughput: Requests per second        │
│  Eviction Rate: Items removed from cache│
│  Memory Usage: Cache size vs data size  │
│                                          │
└──────────────────────────────────────────┘

Typical Latency Comparison:
  L1 Cache:        ~1 ns
  L2 Cache:        ~10 ns
  RAM:             ~100 ns
  Redis/Memcached: ~1 ms
  Database:        ~10-100 ms
  Disk:            ~10 ms
```

---

## 1. Cache-Aside Pattern

### Description

Application is responsible for loading data into cache. On read, check cache first; if miss, load from database and populate cache. Most common caching pattern.

### When to Use

- Read-heavy workloads
- Data doesn't change frequently
- Cache failures should not break application
- Simple caching requirements
- Need control over what/when to cache

### Architecture Diagram

```
┌──────────────────────────────────────────┐
│        Cache-Aside (Lazy Loading)        │
└──────────────────────────────────────────┘

   Application
       │
       │ 1. Read Request
       ▼
   ┌────────┐
   │ Cache  │
   │(Redis) │
   └────┬───┘
        │
   ┌────┴────┐
   │         │
Hit│         │Miss
   │         │
   │    2. Query Database
   │         │
   │         ▼
   │    ┌─────────┐
   │    │Database │
   │    │(Postgres│
   │    └────┬────┘
   │         │
   │    3. Return Data
   │         │
   │    ◄────┘
   │         │
   │    4. Update Cache
   │         │
   └────►────┘
        │
   5. Return to Application
```

### Implementation Example

```python
# cache_aside.py
import redis
import json
import hashlib
from typing import Optional, Callable, Any
import psycopg2
from functools import wraps

class CacheAside:
    def __init__(self, redis_client: redis.Redis, default_ttl: int = 3600):
        self.redis = redis_client
        self.default_ttl = default_ttl

    def get(self, key: str, loader: Callable[[], Any],
            ttl: Optional[int] = None) -> Any:
        """
        Get value from cache or load from source

        Args:
            key: Cache key
            loader: Function to load data if cache miss
            ttl: Time to live in seconds
        """
        # Try to get from cache
        cached_value = self.redis.get(key)

        if cached_value:
            print(f"Cache HIT: {key}")
            return json.loads(cached_value)

        # Cache miss - load from source
        print(f"Cache MISS: {key}")
        value = loader()

        # Store in cache
        if value is not None:
            self.set(key, value, ttl)

        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )

    def delete(self, key: str):
        """Delete from cache"""
        self.redis.delete(key)

    def cache_decorator(self, key_prefix: str = "", ttl: Optional[int] = None):
        """Decorator for caching function results"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                cache_key = self._generate_key(key_prefix or func.__name__,
                                               args, kwargs)

                # Try cache first
                cached = self.redis.get(cache_key)
                if cached:
                    print(f"Cache HIT: {cache_key}")
                    return json.loads(cached)

                # Cache miss - execute function
                print(f"Cache MISS: {cache_key}")
                result = func(*args, **kwargs)

                # Cache result
                if result is not None:
                    self.set(cache_key, result, ttl)

                return result

            return wrapper
        return decorator

    def _generate_key(self, prefix: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key from function arguments"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()


# Example usage with database
class UserRepository:
    def __init__(self, db_connection, cache: CacheAside):
        self.db = db_connection
        self.cache = cache

    def get_user(self, user_id: int) -> Optional[dict]:
        """Get user with caching"""
        cache_key = f"user:{user_id}"

        return self.cache.get(
            cache_key,
            loader=lambda: self._load_user_from_db(user_id),
            ttl=1800  # 30 minutes
        )

    def _load_user_from_db(self, user_id: int) -> Optional[dict]:
        """Load user from database"""
        with self.db.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, email FROM users WHERE id = %s",
                (user_id,)
            )
            row = cursor.fetchone()

            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2]
                }

        return None

    def update_user(self, user_id: int, updates: dict):
        """Update user and invalidate cache"""
        # Update database
        with self.db.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET name = %s, email = %s WHERE id = %s",
                (updates['name'], updates['email'], user_id)
            )
            self.db.commit()

        # Invalidate cache
        cache_key = f"user:{user_id}"
        self.cache.delete(cache_key)


# Using decorator
class ProductService:
    def __init__(self, cache: CacheAside):
        self.cache = cache

    @cache.cache_decorator(key_prefix="product", ttl=3600)
    def get_product(self, product_id: int) -> dict:
        """Get product - automatically cached"""
        # This will only execute on cache miss
        return self._fetch_from_database(product_id)

    def _fetch_from_database(self, product_id: int) -> dict:
        # Database query
        return {'id': product_id, 'name': 'Product Name'}
```

### Terraform - Redis Cache Setup

```hcl
# AWS ElastiCache Redis for cache-aside pattern
resource "aws_elasticache_subnet_group" "cache" {
  name       = "cache-subnet-group"
  subnet_ids = var.private_subnet_ids
}

resource "aws_security_group" "redis" {
  name        = "redis-security-group"
  description = "Security group for Redis cache"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "app-cache"
  replication_group_description = "Redis cluster for cache-aside pattern"

  engine               = "redis"
  engine_version       = "7.0"
  node_type            = "cache.r6g.large"
  number_cache_clusters = 3
  parameter_group_name = "default.redis7"

  subnet_group_name  = aws_elasticache_subnet_group.cache.name
  security_group_ids = [aws_security_group.redis.id]

  automatic_failover_enabled = true
  multi_az_enabled          = true

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  snapshot_retention_limit = 5
  snapshot_window         = "03:00-05:00"

  maintenance_window = "sun:05:00-sun:07:00"

  tags = {
    Name        = "Application Cache"
    Pattern     = "Cache-Aside"
    Environment = "production"
  }
}

output "redis_endpoint" {
  value = aws_elasticache_replication_group.redis.primary_endpoint_address
}
```

### Trade-offs

**Pros:**
- Simple to implement
- Handles cache failures gracefully
- Application controls caching logic
- Works with any database
- Only requested data is cached

**Cons:**
- Cache miss penalty (two round trips)
- Potential for stale data
- Thundering herd problem
- Application complexity

### Anti-patterns

- **No Expiration**: Setting no TTL causes stale data
- **Cache Stampede**: Multiple threads loading same key simultaneously
- **Huge Cache Keys**: Using large objects as keys
- **No Monitoring**: Not tracking hit rates and performance

### Real-world Examples

**Facebook**: Memcached with cache-aside for user profiles and social graph data.

**Twitter**: Redis cache-aside for timeline and user data.

**Stack Overflow**: Cache-aside for questions, answers, and user reputation.

---

## 2. Write-Through Pattern

### Description

Data is written to cache and database simultaneously. Cache always in sync with database. Write operations are slower but reads are fast and consistent.

### When to Use

- Data consistency is critical
- Read-heavy with occasional writes
- Cannot tolerate stale data
- Acceptable write latency increase

### Architecture Diagram

```
┌──────────────────────────────────────────┐
│          Write-Through Pattern           │
└──────────────────────────────────────────┘

   Application
       │
       │ Write Request
       ▼
   ┌────────┐
   │ Cache  │
   │(Redis) │◄────┐
   └────┬───┘     │
        │         │
        │ 1. Write to cache
        │         │
        ▼         │
   ┌─────────┐   │
   │Database │   │
   │(Postgres│   │
   └────┬────┘   │
        │        │
        │ 2. Write to DB
        │        │
        └────────┘
        │
   3. Confirm write
        │
        ▼
   Application
```

### Implementation Example

```python
# write_through.py
import redis
import psycopg2
import json
from typing import Any, Dict

class WriteThrough:
    def __init__(self, redis_client: redis.Redis, db_connection,
                 default_ttl: int = 3600):
        self.redis = redis_client
        self.db = db_connection
        self.default_ttl = default_ttl

    def set(self, key: str, value: Any, ttl: int = None):
        """Write to both cache and database"""
        ttl = ttl or self.default_ttl

        # Write to cache first (faster)
        self.redis.setex(key, ttl, json.dumps(value))

        # Write to database
        self._persist_to_db(key, value)

        print(f"Written to cache and DB: {key}")

    def get(self, key: str) -> Any:
        """Read from cache (always up-to-date)"""
        cached = self.redis.get(key)

        if cached:
            return json.loads(cached)

        # If not in cache, load from DB and cache it
        value = self._load_from_db(key)
        if value:
            self.set(key, value)

        return value

    def delete(self, key: str):
        """Delete from both cache and database"""
        self.redis.delete(key)
        self._delete_from_db(key)

    def _persist_to_db(self, key: str, value: Any):
        """Persist to database"""
        with self.db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO cache_data (key, value, updated_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (key)
                DO UPDATE SET value = %s, updated_at = NOW()
            """, (key, json.dumps(value), json.dumps(value)))
            self.db.commit()

    def _load_from_db(self, key: str) -> Any:
        """Load from database"""
        with self.db.cursor() as cursor:
            cursor.execute(
                "SELECT value FROM cache_data WHERE key = %s",
                (key,)
            )
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None

    def _delete_from_db(self, key: str):
        """Delete from database"""
        with self.db.cursor() as cursor:
            cursor.execute("DELETE FROM cache_data WHERE key = %s", (key,))
            self.db.commit()


# Repository with write-through
class UserRepository:
    def __init__(self, cache: WriteThrough):
        self.cache = cache

    def save_user(self, user: Dict):
        """Save user with write-through caching"""
        key = f"user:{user['id']}"
        self.cache.set(key, user, ttl=3600)

    def get_user(self, user_id: int) -> Dict:
        """Get user from cache (always fresh)"""
        key = f"user:{user_id}"
        return self.cache.get(key)

    def update_user(self, user_id: int, updates: Dict):
        """Update user"""
        user = self.get_user(user_id)
        user.update(updates)
        self.save_user(user)
```

### Trade-offs

**Pros:**
- Strong consistency
- Simple read logic (always hit cache)
- No stale data
- Cache always warm

**Cons:**
- Slower writes (two operations)
- Wasted cache space (caching infrequently read data)
- Higher write latency
- Cache/DB failures impact writes

### Real-world Examples

**DynamoDB DAX**: Write-through caching for DynamoDB.

**Amazon Aurora**: Write-through caching in database layer.

---

## 3. Write-Behind Pattern

### Description

Data written to cache immediately, then asynchronously written to database. Optimizes write performance at the cost of potential data loss.

### When to Use

- Write-heavy workloads
- Can tolerate eventual consistency
- Write latency critical
- Batch writes possible
- Some data loss acceptable

### Architecture Diagram

```
┌──────────────────────────────────────────┐
│      Write-Behind (Write-Back) Pattern   │
└──────────────────────────────────────────┘

   Application
       │
       │ Write Request
       ▼
   ┌────────┐
   │ Cache  │
   │(Redis) │
   └────┬───┘
        │
        │ 1. Write to cache
        │ 2. Return immediately
        │
        ▼
   Application (Write complete)

        ... Time passes ...

   ┌────────┐
   │ Cache  │
   │(Redis) │
   └────┬───┘
        │
        │ Async Writer
        │ (Background Process)
        │
        ▼
   ┌─────────┐
   │Database │
   │(Postgres│
   └─────────┘

   3. Batch write to DB
```

### Implementation Example

```python
# write_behind.py
import redis
import psycopg2
import json
import threading
import time
from queue import Queue
from typing import Dict, Any

class WriteBehind:
    def __init__(self, redis_client: redis.Redis, db_connection,
                 flush_interval: int = 5, batch_size: int = 100):
        self.redis = redis_client
        self.db = db_connection
        self.flush_interval = flush_interval
        self.batch_size = batch_size

        # Write queue
        self.write_queue = Queue()

        # Start background writer
        self.writer_thread = threading.Thread(target=self._background_writer, daemon=True)
        self.writer_thread.start()

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Write to cache immediately, queue for DB write"""
        # Write to cache (fast)
        self.redis.setex(key, ttl, json.dumps(value))

        # Queue for database write
        self.write_queue.put({
            'key': key,
            'value': value,
            'operation': 'set'
        })

        print(f"Cached and queued: {key}")

    def get(self, key: str) -> Any:
        """Read from cache"""
        cached = self.redis.get(key)
        return json.loads(cached) if cached else None

    def delete(self, key: str):
        """Delete from cache and queue DB deletion"""
        self.redis.delete(key)

        self.write_queue.put({
            'key': key,
            'operation': 'delete'
        })

    def _background_writer(self):
        """Background thread for async DB writes"""
        batch = []

        while True:
            try:
                # Collect batch
                while len(batch) < self.batch_size:
                    try:
                        item = self.write_queue.get(timeout=self.flush_interval)
                        batch.append(item)
                    except:
                        # Timeout - flush current batch
                        break

                if batch:
                    self._flush_batch(batch)
                    batch = []

            except Exception as e:
                print(f"Background writer error: {e}")
                time.sleep(1)

    def _flush_batch(self, batch: list):
        """Flush batch to database"""
        if not batch:
            return

        try:
            with self.db.cursor() as cursor:
                for item in batch:
                    if item['operation'] == 'set':
                        cursor.execute("""
                            INSERT INTO cache_data (key, value, updated_at)
                            VALUES (%s, %s, NOW())
                            ON CONFLICT (key)
                            DO UPDATE SET value = %s, updated_at = NOW()
                        """, (item['key'], json.dumps(item['value']),
                              json.dumps(item['value'])))
                    elif item['operation'] == 'delete':
                        cursor.execute(
                            "DELETE FROM cache_data WHERE key = %s",
                            (item['key'],)
                        )

                self.db.commit()
                print(f"Flushed {len(batch)} items to database")

        except Exception as e:
            print(f"Batch flush error: {e}")
            self.db.rollback()


# Usage with write coalescing
class SessionStore:
    """Session store with write-behind caching"""

    def __init__(self, cache: WriteBehind):
        self.cache = cache

    def save_session(self, session_id: str, data: Dict):
        """Save session - immediate cache, async DB"""
        key = f"session:{session_id}"
        self.cache.set(key, data, ttl=1800)  # 30 min

    def get_session(self, session_id: str) -> Dict:
        """Get session from cache"""
        key = f"session:{session_id}"
        return self.cache.get(key)
```

### Trade-offs

**Pros:**
- Very fast writes
- Reduced database load
- Batch writes for efficiency
- Good for high write throughput

**Cons:**
- Potential data loss (if cache fails)
- Eventual consistency
- Complex error handling
- Recovery challenges

### Real-world Examples

**LinkedIn**: Write-behind caching for activity feeds.

**Pinterest**: Write-behind for user engagement data.

---

## 4. Refresh-Ahead Pattern

### Description

Automatically refresh cache entries before they expire, ensuring popular items always available and fresh.

### When to Use

- Predictable access patterns
- Expensive to compute data
- Low tolerance for cache misses
- High read rates on specific keys

### Implementation Example

```python
# refresh_ahead.py
import redis
import time
import threading
from typing import Callable, Any
import json

class RefreshAhead:
    def __init__(self, redis_client: redis.Redis, default_ttl: int = 3600,
                 refresh_threshold: float = 0.8):
        self.redis = redis_client
        self.default_ttl = default_ttl
        self.refresh_threshold = refresh_threshold
        self.refresh_threads = {}

    def get(self, key: str, loader: Callable[[], Any],
            ttl: int = None) -> Any:
        """Get with refresh-ahead"""
        ttl = ttl or self.default_ttl

        # Get from cache
        cached = self.redis.get(key)

        if cached:
            # Check time to expiration
            remaining_ttl = self.redis.ttl(key)

            # If approaching expiration, trigger refresh
            if remaining_ttl < (ttl * self.refresh_threshold):
                self._trigger_refresh(key, loader, ttl)

            return json.loads(cached)

        # Cache miss - load and cache
        value = loader()
        if value is not None:
            self.redis.setex(key, ttl, json.dumps(value))

        return value

    def _trigger_refresh(self, key: str, loader: Callable, ttl: int):
        """Trigger async refresh of cache entry"""
        # Avoid multiple refresh threads for same key
        if key in self.refresh_threads:
            return

        def refresh():
            try:
                print(f"Refreshing cache: {key}")
                value = loader()
                if value is not None:
                    self.redis.setex(key, ttl, json.dumps(value))
            finally:
                self.refresh_threads.pop(key, None)

        thread = threading.Thread(target=refresh, daemon=True)
        self.refresh_threads[key] = thread
        thread.start()


# Example: Popular product cache
class ProductCache:
    def __init__(self, cache: RefreshAhead):
        self.cache = cache

    def get_product(self, product_id: int) -> dict:
        """Get product with refresh-ahead"""
        key = f"product:{product_id}"

        return self.cache.get(
            key,
            loader=lambda: self._load_product(product_id),
            ttl=3600
        )

    def _load_product(self, product_id: int) -> dict:
        """Load product from database"""
        # Expensive operation
        time.sleep(0.5)  # Simulate DB query
        return {
            'id': product_id,
            'name': f'Product {product_id}',
            'price': 99.99
        }
```

### Real-world Examples

**Google**: Refresh-ahead for search result caching.

**Amazon**: Product page caching with proactive refresh.

---

## 5. Distributed Caching Pattern

### Description

Shared cache across multiple application instances, ensuring consistency and scalability.

### Architecture Diagram

```
┌──────────────────────────────────────────┐
│       Distributed Cache Architecture     │
└──────────────────────────────────────────┘

┌──────────┐  ┌──────────┐  ┌──────────┐
│  App     │  │  App     │  │  App     │
│Instance 1│  │Instance 2│  │Instance 3│
└─────┬────┘  └─────┬────┘  └─────┬────┘
      │             │             │
      └─────────────┼─────────────┘
                    │
         ┌──────────▼──────────┐
         │  Redis Cluster      │
         │  (Distributed)      │
         │  ┌────┐  ┌────┐    │
         │  │Node│  │Node│ ...│
         │  │ 1  │  │ 2  │    │
         │  └────┘  └────┘    │
         └─────────────────────┘
              Consistent Hashing
              Replication
              Sharding
```

### Real-world Examples

**Facebook**: Distributed Memcached clusters across datacenters.

**Redis Labs**: Redis Enterprise for distributed caching.

---

## 6. Cache Invalidation Patterns

### Description

Strategies for keeping cache synchronized with source of truth.

### Invalidation Strategies

```
┌──────────────────────────────────────────┐
│      Cache Invalidation Strategies       │
├──────────────────────────────────────────┤
│                                          │
│  1. TTL-Based (Time-based)              │
│     - Set expiration time               │
│     - Simplest approach                 │
│                                          │
│  2. Event-Based                         │
│     - Invalidate on data changes        │
│     - Most accurate                     │
│                                          │
│  3. Write-Through                       │
│     - Update cache on every write       │
│     - Always consistent                 │
│                                          │
│  4. Tag-Based                           │
│     - Group related cache entries       │
│     - Invalidate by tag                 │
│                                          │
│  5. Version-Based                       │
│     - Include version in key            │
│     - Old versions expire naturally     │
│                                          │
└──────────────────────────────────────────┘
```

### Implementation Example

```python
# cache_invalidation.py
import redis
from typing import Set, List

class CacheInvalidator:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def invalidate_by_tag(self, tag: str):
        """Invalidate all cache entries with tag"""
        # Get all keys with tag
        tag_key = f"tag:{tag}"
        keys = self.redis.smembers(tag_key)

        if keys:
            # Delete all keys
            self.redis.delete(*keys)
            # Delete tag set
            self.redis.delete(tag_key)

            print(f"Invalidated {len(keys)} entries with tag: {tag}")

    def set_with_tags(self, key: str, value: Any,
                     tags: List[str], ttl: int = 3600):
        """Set cache value with tags"""
        # Set value
        self.redis.setex(key, ttl, json.dumps(value))

        # Add to tag sets
        for tag in tags:
            tag_key = f"tag:{tag}"
            self.redis.sadd(tag_key, key)
            self.redis.expire(tag_key, ttl)

    def invalidate_by_pattern(self, pattern: str):
        """Invalidate by key pattern"""
        cursor = 0
        while True:
            cursor, keys = self.redis.scan(cursor, match=pattern)

            if keys:
                self.redis.delete(*keys)

            if cursor == 0:
                break
```

---

## 7. Multi-Level Caching Pattern

### Description

Multiple caching layers (L1, L2, L3) with different characteristics optimizing for different use cases.

### Architecture

```
┌──────────────────────────────────────────┐
│        Multi-Level Cache Hierarchy       │
└──────────────────────────────────────────┘

Application
     │
     ▼
┌─────────┐  L1: Application Memory
│In-Memory│  - Fastest
│  Cache  │  - Smallest
└────┬────┘  - Process-local
     │
     ▼
┌─────────┐  L2: Distributed Cache
│  Redis  │  - Fast
│  Cache  │  - Medium size
└────┬────┘  - Shared across instances
     │
     ▼
┌─────────┐  L3: CDN/Edge Cache
│   CDN   │  - Geographic distribution
│  Cache  │  - Large size
└────┬────┘  - Static content
     │
     ▼
┌─────────┐
│Database │  Source of Truth
└─────────┘
```

### Real-world Examples

**Netflix**: Multi-tier caching (EVCache, Memcached, CDN).

**Twitter**: In-memory + Redis + database caching hierarchy.

---

## Tool Recommendations

### In-Memory Caches

**Redis**
- Most popular
- Rich data structures
- Persistence options
- Pub/sub capabilities

**Memcached**
- Simple key-value
- Very fast
- Good for simple caching

**Hazelcast**
- Distributed caching
- In-memory data grid
- Java-focused

### Cloud-Managed Caches

**AWS**
- ElastiCache (Redis/Memcached)
- CloudFront (CDN)
- DAX (DynamoDB Accelerator)

**Azure**
- Azure Cache for Redis
- Azure CDN
- Azure Front Door

**GCP**
- Memorystore (Redis/Memcached)
- Cloud CDN

---

## Summary

Caching patterns enable:
- **Performance**: 10-100x faster than database
- **Scalability**: Reduce database load
- **Cost**: Lower infrastructure costs
- **Availability**: Reduce dependency on database

### Pattern Selection

| Use Case | Pattern |
|----------|---------|
| General purpose | Cache-Aside |
| Strong consistency | Write-Through |
| High write throughput | Write-Behind |
| Predictable traffic | Refresh-Ahead |
| Multi-instance apps | Distributed Cache |

### Best Practices

1. **Monitor Hit Rates**: Target >80% hit rate
2. **Set Appropriate TTLs**: Balance freshness vs performance
3. **Handle Cache Failures**: Graceful degradation
4. **Use Consistent Keys**: Naming conventions
5. **Implement Warming**: Pre-populate cache
6. **Size Appropriately**: Monitor memory usage

### FAANG Caching Strategies

- **Amazon**: Multi-tier caching across all services
- **Facebook**: TAO (distributed cache) for social graph
- **Netflix**: EVCache for distributed caching at scale
- **Google**: Distributed caching in every major product
- **Uber**: Redis-based caching for trip data
