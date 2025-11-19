# Database Migration Patterns Reference

## Overview
This reference covers strategies and patterns for safely migrating databases in production environments with zero or minimal downtime, focusing on backward compatibility and rollback safety.

---

## Core Principles

### 1. Backward Compatibility
**Always maintain compatibility with N-1 version**
- Old code must work with new schema
- New code must work with old schema
- Enables zero-downtime deployments
- Allows safe rollbacks

### 2. Expand-Contract Pattern
**Three-phase migration approach**:
1. **Expand**: Add new structures alongside old
2. **Migrate**: Dual-write to both old and new
3. **Contract**: Remove old structures

### 3. Migration Safety Rules
```
✓ DO:
  - Add columns with defaults
  - Add nullable columns
  - Add tables
  - Add indexes (carefully)
  - Rename via dual-write

✗ DON'T:
  - Remove columns (immediately)
  - Rename columns (directly)
  - Change column types (directly)
  - Add NOT NULL without default
  - Remove tables (immediately)
  - Large data migrations in transaction
```

---

## Safe Migration Patterns

### Pattern 1: Adding a Column

#### Simple Addition (Nullable)
```sql
-- SAFE: Adding nullable column
ALTER TABLE users
ADD COLUMN phone_number VARCHAR(20);

-- Application code handles NULL gracefully
SELECT id, email, COALESCE(phone_number, '') as phone
FROM users;
```

#### Addition with Default (PostgreSQL)
```sql
-- SAFE: Adding column with default (PostgreSQL 11+)
-- Default is stored in catalog, not written to all rows
ALTER TABLE users
ADD COLUMN status VARCHAR(20) DEFAULT 'active';

-- For older PostgreSQL or large tables, use multi-step:
-- Step 1: Add nullable column
ALTER TABLE users ADD COLUMN status VARCHAR(20);

-- Step 2: Backfill in batches (outside transaction)
UPDATE users SET status = 'active'
WHERE id >= 1000000 AND id < 2000000 AND status IS NULL;
-- Repeat for all ranges

-- Step 3: Add NOT NULL constraint
ALTER TABLE users
ALTER COLUMN status SET NOT NULL;

-- Step 4: Add default for new rows
ALTER TABLE users
ALTER COLUMN status SET DEFAULT 'active';
```

#### Addition with NOT NULL
```sql
-- MULTI-STEP PROCESS

-- Step 1: Add nullable column with default
ALTER TABLE orders
ADD COLUMN priority INTEGER DEFAULT 1;

-- Step 2: Backfill existing rows (in batches)
DO $$
DECLARE
  batch_size INTEGER := 10000;
  min_id INTEGER;
  max_id INTEGER;
BEGIN
  SELECT MIN(id), MAX(id) INTO min_id, max_id FROM orders;

  FOR i IN min_id..max_id BY batch_size LOOP
    UPDATE orders
    SET priority = 1
    WHERE id >= i AND id < i + batch_size
      AND priority IS NULL;

    COMMIT; -- Commit each batch
  END LOOP;
END $$;

-- Step 3: Add NOT NULL constraint (after all rows filled)
ALTER TABLE orders
ALTER COLUMN priority SET NOT NULL;
```

---

### Pattern 2: Removing a Column

**Use Expand-Contract Pattern**

```sql
-- DON'T DO THIS (breaks old app version):
ALTER TABLE users DROP COLUMN middle_name;

-- DO THIS (3-phase approach):

-- Phase 1: EXPAND (Deploy app that doesn't use column)
-- Just stop using column in application code
-- Wait for deployment to complete

-- Phase 2: MIGRATE (Optional - archive data if needed)
CREATE TABLE users_archive AS
SELECT id, middle_name, archived_at
FROM users
WHERE middle_name IS NOT NULL;

-- Phase 3: CONTRACT (Remove column in next migration)
-- Deploy this in NEXT release cycle
ALTER TABLE users DROP COLUMN middle_name;
```

**Timeline**:
```
Week 1: Deploy app v2.0 (doesn't read/write middle_name)
Week 2: Verify no usage, archive data if needed
Week 3: Deploy migration to drop column
```

---

### Pattern 3: Renaming a Column

**Never rename directly** - Use dual-write approach

```sql
-- DON'T DO THIS:
ALTER TABLE users RENAME COLUMN name TO full_name;

-- DO THIS (4-phase approach):

-- Phase 1: EXPAND - Add new column
ALTER TABLE users ADD COLUMN full_name VARCHAR(255);

-- Phase 2: MIGRATE - Backfill data
UPDATE users SET full_name = name WHERE full_name IS NULL;

-- Phase 3: Deploy app that dual-writes
-- Application code:
-- When writing:
--   UPDATE users SET name = ?, full_name = ? WHERE id = ?
-- When reading:
--   SELECT COALESCE(full_name, name) as full_name FROM users

-- Phase 4: Deploy app that only uses new column
-- Application only reads/writes full_name

-- Phase 5: CONTRACT - Remove old column (next release)
ALTER TABLE users DROP COLUMN name;
```

**With Trigger (Alternative)**:
```sql
-- Phase 1: Add new column
ALTER TABLE users ADD COLUMN full_name VARCHAR(255);

-- Phase 2: Create sync trigger
CREATE OR REPLACE FUNCTION sync_user_name()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.name IS DISTINCT FROM OLD.name THEN
    NEW.full_name := NEW.name;
  END IF;
  IF NEW.full_name IS DISTINCT FROM OLD.full_name THEN
    NEW.name := NEW.full_name;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sync_user_name_trigger
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION sync_user_name();

-- Phase 3: Backfill
UPDATE users SET full_name = name WHERE full_name IS NULL;

-- Phase 4: Deploy app using new column

-- Phase 5: Remove trigger and old column
DROP TRIGGER sync_user_name_trigger ON users;
DROP FUNCTION sync_user_name();
ALTER TABLE users DROP COLUMN name;
```

---

### Pattern 4: Changing Column Type

**Multi-phase approach**

```sql
-- DON'T DO THIS (can lock table or fail):
ALTER TABLE products
ALTER COLUMN price TYPE DECIMAL(10,2);

-- DO THIS:

-- Phase 1: EXPAND - Add new column with new type
ALTER TABLE products
ADD COLUMN price_decimal DECIMAL(10,2);

-- Phase 2: MIGRATE - Backfill with conversion
UPDATE products
SET price_decimal = price::DECIMAL(10,2)
WHERE price_decimal IS NULL;

-- Phase 3: Deploy app that dual-writes
-- Write to both columns, read from new column

-- Phase 4: Verify data consistency
SELECT COUNT(*) FROM products
WHERE price::DECIMAL(10,2) != price_decimal;

-- Phase 5: CONTRACT - Remove old column
ALTER TABLE products DROP COLUMN price;

-- Phase 6: Rename new column (optional)
ALTER TABLE products
RENAME COLUMN price_decimal TO price;
```

**PostgreSQL Type Change (Safe Cases)**:
```sql
-- These are SAFE (no table rewrite in PostgreSQL):

-- Increasing VARCHAR length
ALTER TABLE users
ALTER COLUMN name TYPE VARCHAR(500); -- from VARCHAR(255)

-- VARCHAR to TEXT
ALTER TABLE users
ALTER COLUMN description TYPE TEXT; -- from VARCHAR

-- Numeric precision increase
ALTER TABLE products
ALTER COLUMN price TYPE NUMERIC(12,2); -- from NUMERIC(10,2)

-- These REQUIRE table rewrite (use expand-contract):
-- INT to BIGINT
-- VARCHAR to UUID
-- TEXT to JSON/JSONB
-- Any change that requires data transformation
```

---

### Pattern 5: Adding an Index

**Large Table Index Creation**

```sql
-- DON'T DO THIS on large production table:
CREATE INDEX idx_users_email ON users(email);

-- DO THIS (PostgreSQL):
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- MySQL equivalent:
ALTER TABLE users ADD INDEX idx_users_email(email), ALGORITHM=INPLACE, LOCK=NONE;
```

**Monitoring Index Creation**:
```sql
-- PostgreSQL: Check progress
SELECT
  now()::time,
  query,
  state,
  wait_event_type,
  wait_event
FROM pg_stat_activity
WHERE query LIKE '%CREATE INDEX%';

-- Check index size as it builds
SELECT pg_size_pretty(pg_relation_size('idx_users_email'));
```

**Partial Index for Performance**:
```sql
-- Index only active users (smaller, faster)
CREATE INDEX CONCURRENTLY idx_active_users_email
ON users(email)
WHERE status = 'active';
```

---

### Pattern 6: Removing an Index

```sql
-- Safe to do immediately (doesn't affect reads)
DROP INDEX CONCURRENTLY idx_old_index;

-- But verify it's not used first
-- Check pg_stat_user_indexes for usage
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE indexname = 'idx_old_index';
```

---

### Pattern 7: Adding a Foreign Key

**Safe Addition**:
```sql
-- DON'T DO THIS (locks table):
ALTER TABLE orders
ADD CONSTRAINT fk_orders_user
FOREIGN KEY (user_id) REFERENCES users(id);

-- DO THIS (PostgreSQL 12+):
-- Step 1: Add constraint as NOT VALID (doesn't lock)
ALTER TABLE orders
ADD CONSTRAINT fk_orders_user
FOREIGN KEY (user_id) REFERENCES users(id)
NOT VALID;

-- Step 2: Validate in background (can run during traffic)
ALTER TABLE orders
VALIDATE CONSTRAINT fk_orders_user;
```

**MySQL Approach**:
```sql
-- Step 1: Add index first (if not exists)
ALTER TABLE orders
ADD INDEX idx_user_id (user_id),
ALGORITHM=INPLACE, LOCK=NONE;

-- Step 2: Add FK (still locks, but faster with index)
ALTER TABLE orders
ADD CONSTRAINT fk_orders_user
FOREIGN KEY (user_id) REFERENCES users(id);
```

---

### Pattern 8: Splitting a Table

**Vertical Split** (move columns to new table):

```sql
-- Goal: Move rarely-used columns from users to user_details

-- Phase 1: EXPAND - Create new table
CREATE TABLE user_details (
  user_id INTEGER PRIMARY KEY REFERENCES users(id),
  bio TEXT,
  preferences JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Phase 2: MIGRATE - Copy data
INSERT INTO user_details (user_id, bio, preferences)
SELECT id, bio, preferences
FROM users
WHERE bio IS NOT NULL OR preferences IS NOT NULL;

-- Phase 3: Deploy app that dual-writes
-- Writes go to both tables
-- Reads join when needed

-- Phase 4: Verify consistency
SELECT COUNT(*) FROM users u
LEFT JOIN user_details ud ON u.id = ud.user_id
WHERE (u.bio IS NOT NULL AND u.bio != ud.bio);

-- Phase 5: CONTRACT - Remove columns from users
ALTER TABLE users DROP COLUMN bio;
ALTER TABLE users DROP COLUMN preferences;
```

**Horizontal Split** (sharding):

```sql
-- Goal: Split users table by region

-- Phase 1: Create regional tables
CREATE TABLE users_us (LIKE users INCLUDING ALL);
CREATE TABLE users_eu (LIKE users INCLUDING ALL);
CREATE TABLE users_asia (LIKE users INCLUDING ALL);

-- Phase 2: Copy data
INSERT INTO users_us
SELECT * FROM users WHERE region = 'US';

-- Phase 3: Set up dual-write in application
-- Route reads/writes based on region

-- Phase 4: Verify and contract
-- Eventually remove main users table
```

---

## Large Data Migrations

### Batched Migration Pattern

```python
# Python example for large data migration
import psycopg2
import time

def migrate_users_in_batches():
    conn = psycopg2.connect(DATABASE_URL)
    batch_size = 10000

    # Get range
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(id), MAX(id) FROM users")
    min_id, max_id = cursor.fetchone()

    processed = 0
    start_time = time.time()

    for batch_start in range(min_id, max_id + 1, batch_size):
        batch_end = batch_start + batch_size

        # Process batch in its own transaction
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users
                SET normalized_email = LOWER(TRIM(email))
                WHERE id >= %s AND id < %s
                  AND normalized_email IS NULL
            """, (batch_start, batch_end))

            rows_affected = cur.rowcount
            conn.commit()

            processed += rows_affected

            # Progress logging
            elapsed = time.time() - start_time
            rate = processed / elapsed if elapsed > 0 else 0
            print(f"Processed {processed} rows ({rate:.0f} rows/sec)")

            # Throttle to avoid overload
            time.sleep(0.1)

    print(f"Migration complete: {processed} rows in {elapsed:.1f}s")
```

### Parallel Batch Migration

```python
from concurrent.futures import ThreadPoolExecutor
import psycopg2.pool

def migrate_batch(connection_pool, start_id, end_id):
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users
                SET normalized_email = LOWER(TRIM(email))
                WHERE id >= %s AND id < %s
                  AND normalized_email IS NULL
            """, (start_id, end_id))
            conn.commit()
            return cur.rowcount
    finally:
        connection_pool.putconn(conn)

def parallel_migrate_users():
    pool = psycopg2.pool.ThreadedConnectionPool(
        minconn=5,
        maxconn=20,
        dsn=DATABASE_URL
    )

    # Get ID ranges
    conn = pool.getconn()
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(id), MAX(id) FROM users")
    min_id, max_id = cursor.fetchone()
    pool.putconn(conn)

    # Create batches
    batch_size = 10000
    batches = []
    for start in range(min_id, max_id + 1, batch_size):
        batches.append((start, start + batch_size))

    # Execute in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(migrate_batch, pool, start, end)
            for start, end in batches
        ]

        total = sum(f.result() for f in futures)

    print(f"Migrated {total} rows")
    pool.closeall()
```

---

## Zero-Downtime Migration Strategies

### Strategy 1: Blue-Green Database

```sql
-- Setup:
-- - Clone production DB to "green" database
-- - Apply migrations to green
-- - Set up replication from production (blue) to green
-- - Switch application to green
-- - Promote green to production

-- Step 1: Create replica
-- (Using PostgreSQL logical replication)

-- On blue (source):
CREATE PUBLICATION users_pub FOR TABLE users;

-- On green (target):
CREATE SUBSCRIPTION users_sub
CONNECTION 'host=blue-db port=5432 dbname=prod user=repl'
PUBLICATION users_pub;

-- Step 2: Apply migrations to green
-- (Migrations run on green while it's replicating)

-- Step 3: Switch application to green
-- Update connection string

-- Step 4: Stop replication
DROP SUBSCRIPTION users_sub;
```

### Strategy 2: Shadow Writing

```python
class DualWriteRepository:
    """Write to both old and new schema during migration"""

    def __init__(self, old_db, new_db):
        self.old_db = old_db
        self.new_db = new_db
        self.write_to_new = feature_flags.is_enabled('new_schema')

    def save_user(self, user_data):
        # Always write to old schema (safe fallback)
        old_result = self._save_to_old_schema(user_data)

        # Optionally write to new schema
        if self.write_to_new:
            try:
                new_result = self._save_to_new_schema(user_data)

                # Log discrepancies
                if old_result.id != new_result.id:
                    logger.warning(f"ID mismatch: {old_result.id} vs {new_result.id}")
            except Exception as e:
                logger.error(f"New schema write failed: {e}")
                # Don't fail request - old schema write succeeded

        return old_result
```

### Strategy 3: Read-Verify Pattern

```python
def get_user(user_id):
    """Read from old, verify against new"""

    # Primary read from old schema
    old_data = old_db.get_user(user_id)

    # Shadow read from new schema (if enabled)
    if feature_flags.is_enabled('new_schema_reads'):
        try:
            new_data = new_db.get_user(user_id)

            # Compare results
            if old_data != new_data:
                metrics.increment('schema_migration.discrepancy')
                logger.warning(
                    f"Data mismatch for user {user_id}",
                    extra={
                        'old': old_data,
                        'new': new_data
                    }
                )
        except Exception as e:
            metrics.increment('schema_migration.new_read_error')

    return old_data
```

---

## Rollback Strategies

### Immediate Rollback

```sql
-- If migration is in progress (not committed)
ROLLBACK;

-- If migration is committed but application not deployed
-- Run reverse migration:

-- Forward migration:
ALTER TABLE users ADD COLUMN age INTEGER;

-- Reverse migration:
ALTER TABLE users DROP COLUMN age;
```

### Delayed Rollback

```sql
-- If application is deployed with new schema

-- Phase 1: Deploy old application version
-- (Must be compatible with current schema)

-- Phase 2: Run reverse migration
-- (Only after old app is deployed and verified)

-- Phase 3: Verify data consistency
```

### Safety Checklist for Rollbacks

```
✓ Can old code run with new schema?
✓ Have we deployed old code successfully?
✓ Is there data in new columns that would be lost?
✓ Are there new foreign keys that would be violated?
✓ Can reverse migration run without data loss?
✓ Have we tested rollback in staging?
```

---

## Migration Tools

### Flyway

#### Configuration
```properties
# flyway.conf
flyway.url=jdbc:postgresql://localhost:5432/mydb
flyway.user=dbuser
flyway.password=secret
flyway.locations=filesystem:./sql
flyway.baselineOnMigrate=true
flyway.outOfOrder=false
```

#### Migration Files
```sql
-- V1__initial_schema.sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- V2__add_users_name.sql
ALTER TABLE users ADD COLUMN name VARCHAR(255);

-- V3__add_users_name_index.sql
CREATE INDEX CONCURRENTLY idx_users_name ON users(name);
```

#### Repeatable Migrations
```sql
-- R__create_views.sql
-- Runs every time checksum changes
CREATE OR REPLACE VIEW active_users AS
SELECT * FROM users WHERE deleted_at IS NULL;
```

### Liquibase

#### Changelog (XML)
```xml
<!-- db/changelog/db.changelog-master.xml -->
<databaseChangeLog>
    <changeSet id="1" author="developer">
        <createTable tableName="users">
            <column name="id" type="int" autoIncrement="true">
                <constraints primaryKey="true"/>
            </column>
            <column name="email" type="varchar(255)">
                <constraints nullable="false"/>
            </column>
        </createTable>
    </changeSet>

    <changeSet id="2" author="developer">
        <addColumn tableName="users">
            <column name="name" type="varchar(255)"/>
        </addColumn>
    </changeSet>

    <changeSet id="3" author="developer">
        <createIndex indexName="idx_users_email"
                     tableName="users">
            <column name="email"/>
        </createIndex>
    </changeSet>
</databaseChangeLog>
```

#### Changelog (YAML)
```yaml
# db/changelog/db.changelog-master.yaml
databaseChangeLog:
  - changeSet:
      id: 1
      author: developer
      changes:
        - createTable:
            tableName: users
            columns:
              - column:
                  name: id
                  type: int
                  autoIncrement: true
                  constraints:
                    primaryKey: true
              - column:
                  name: email
                  type: varchar(255)
                  constraints:
                    nullable: false

  - changeSet:
      id: 2
      author: developer
      changes:
        - addColumn:
            tableName: users
            columns:
              - column:
                  name: name
                  type: varchar(255)
```

#### Rollback Support
```yaml
databaseChangeLog:
  - changeSet:
      id: 3
      author: developer
      changes:
        - addColumn:
            tableName: users
            columns:
              - column:
                  name: status
                  type: varchar(20)
      rollback:
        - dropColumn:
            tableName: users
            columnName: status
```

### Alembic (Python)

#### Configuration
```python
# alembic/env.py
from alembic import context
from myapp.models import Base

target_metadata = Base.metadata

def run_migrations_online():
    connectable = create_engine(database_url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
```

#### Migration File
```python
# alembic/versions/001_add_user_name.py
"""add user name

Revision ID: 001
Revises:
Create Date: 2024-01-15
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users',
        sa.Column('name', sa.String(255), nullable=True)
    )

def downgrade():
    op.drop_column('users', 'name')
```

#### Batch Operations (SQLite)
```python
def upgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(
            sa.Column('age', sa.Integer(), nullable=True)
        )
        batch_op.create_index('idx_age', ['age'])
```

---

## Testing Migrations

### Test Strategy

```python
import pytest
from alembic import command
from alembic.config import Config

@pytest.fixture
def migration_test_db():
    """Create test database for migration testing"""
    db = create_test_database()
    yield db
    drop_test_database(db)

def test_migration_forward_backward(migration_test_db):
    """Test migration up and down"""
    alembic_cfg = Config("alembic.ini")

    # Apply all migrations
    command.upgrade(alembic_cfg, "head")

    # Verify schema
    assert table_exists('users')
    assert column_exists('users', 'name')

    # Rollback one version
    command.downgrade(alembic_cfg, "-1")

    # Verify rollback
    assert not column_exists('users', 'name')

    # Re-apply
    command.upgrade(alembic_cfg, "head")
    assert column_exists('users', 'name')

def test_migration_with_data(migration_test_db):
    """Test migration preserves data"""
    # Insert test data before migration
    insert_test_data()

    # Run migration
    command.upgrade(alembic_cfg, "head")

    # Verify data still exists and is valid
    assert count_users() == 100
    assert all_users_have_required_fields()
```

---

## Best Practices Summary

### ✓ DO
1. **Test migrations in staging** with production-like data
2. **Use transactions** for small migrations
3. **Batch large migrations** to avoid long locks
4. **Create indexes concurrently** on large tables
5. **Monitor performance** during migrations
6. **Keep migrations small** and focused
7. **Version control** all migrations
8. **Document** complex migrations
9. **Plan rollback strategy** before executing
10. **Communicate** with team about migrations

### ✗ DON'T
1. **Don't modify old migrations** once applied
2. **Don't remove columns immediately** (use expand-contract)
3. **Don't change types directly** (use expand-contract)
4. **Don't run large migrations in transactions**
5. **Don't add NOT NULL without default** immediately
6. **Don't test in production first**
7. **Don't skip code review** for migrations
8. **Don't ignore warnings** from migration tools
9. **Don't forget** to update documentation
10. **Don't rush** critical migrations

---

## Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Flyway: https://flywaydb.org/
- Liquibase: https://www.liquibase.org/
- Alembic: https://alembic.sqlalchemy.org/
- Expand-Contract Pattern: https://martinfowler.com/bliki/ParallelChange.html
- Zero-Downtime Deployments: https://blog.codinghorror.com/zero-downtime-deployments/
