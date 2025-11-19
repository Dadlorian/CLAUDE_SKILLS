# Database Migrations Examples

This directory contains examples of safe database migration patterns using Flyway and Liquibase, following industry best practices for zero-downtime deployments.

## Directory Structure

```
database-migrations/
├── flyway-migrations/          # Flyway SQL migration examples
│   ├── V1__initial_schema.sql
│   ├── V2__add_user_preferences.sql
│   ├── V3__rename_column_expand.sql
│   └── V4__rename_column_contract.sql
│
├── liquibase-migrations/       # Liquibase YAML migration examples
│   ├── db.changelog-master.yaml
│   └── changelogs/
│       ├── 001-initial-schema.yaml
│       └── 005-migrate-column-type.yaml
│
└── README.md                   # This file
```

---

## Migration Tools

### Flyway

Flyway uses SQL-based migrations with versioning in filenames.

**Naming Convention**: `V{version}__{description}.sql`
- `V1__initial_schema.sql`
- `V2__add_column.sql`

**Advantages**:
- Simple SQL-based migrations
- Easy to understand and review
- Versioning built into filenames
- Supports Java-based migrations

**Run Flyway**:
```bash
flyway -url=jdbc:postgresql://localhost:5432/mydb \
       -user=postgres \
       -password=secret \
       -locations=filesystem:./flyway-migrations \
       migrate
```

### Liquibase

Liquibase uses XML/YAML/JSON changelogs with more structured approach.

**Advantages**:
- Database-agnostic (generates appropriate SQL)
- Built-in rollback support
- Preconditions and contexts
- More structured change management

**Run Liquibase**:
```bash
liquibase --changeLogFile=db.changelog-master.yaml \
          --url=jdbc:postgresql://localhost:5432/mydb \
          --username=postgres \
          --password=secret \
          update
```

---

## Migration Patterns Demonstrated

### 1. Initial Schema (V1, 001)
- Creating tables with proper indexes
- Adding foreign key constraints
- Setting up default values
- Creating triggers for auto-timestamps

### 2. Adding Columns (V2)
**Safe Pattern**:
```sql
-- Add nullable column (safe)
ALTER TABLE users ADD COLUMN preferences JSONB;

-- Add column with default (safe in PostgreSQL 11+)
ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active';
```

**Unsafe Pattern** (avoid):
```sql
-- DON'T: Add NOT NULL column without default
ALTER TABLE users ADD COLUMN required_field VARCHAR(20) NOT NULL;
```

### 3. Renaming Columns (V3, V4) - Expand-Contract Pattern

**Phase 1: EXPAND** (V3)
```sql
-- Add new column
ALTER TABLE users ADD COLUMN full_name VARCHAR(200);

-- Backfill data
UPDATE users SET full_name = first_name || ' ' || last_name;

-- Create sync trigger for dual-write
CREATE TRIGGER sync_full_name_trigger...
```

**Phase 2: CONTRACT** (V4)
```sql
-- Remove old columns (only after app is updated)
ALTER TABLE users DROP COLUMN first_name;
ALTER TABLE users DROP COLUMN last_name;
```

**Timeline**:
```
Week 1: Deploy V3 migration + app v2.0 (uses both old and new columns)
Week 2: Monitor for issues
Week 3: Deploy app v2.1 (only uses new column)
Week 4: Deploy V4 migration (removes old columns)
```

### 4. Changing Column Types (005) - Expand-Contract Pattern

**Phase 1: EXPAND**
```sql
-- Add new column with new type
ALTER TABLE products ADD COLUMN price_v2 DECIMAL(12,4);

-- Backfill data
UPDATE products SET price_v2 = price::DECIMAL(12,4);

-- Create sync trigger
CREATE TRIGGER sync_price_columns_trigger...
```

**Phase 2: MIGRATE**
- Deploy application that writes to both columns
- Monitor for data consistency

**Phase 3: CONTRACT** (separate migration)
```sql
-- Remove old column
ALTER TABLE products DROP COLUMN price;

-- Rename new column
ALTER TABLE products RENAME COLUMN price_v2 TO price;
```

---

## Safe Migration Checklist

### ✓ DO

1. **Add columns as nullable**
   ```sql
   ALTER TABLE users ADD COLUMN new_field VARCHAR(100);
   ```

2. **Backfill in batches**
   ```sql
   -- Use batches to avoid long locks
   UPDATE users SET new_field = 'value'
   WHERE id >= 1000 AND id < 2000;
   ```

3. **Create indexes concurrently**
   ```sql
   CREATE INDEX CONCURRENTLY idx_name ON table(column);
   ```

4. **Use expand-contract for breaking changes**
   - Add new → Migrate → Remove old

5. **Test migrations in staging**
   - With production-like data volume

6. **Keep migrations small and focused**
   - One logical change per migration

7. **Add rollback instructions**
   - Document how to undo the migration

### ✗ DON'T

1. **Don't add NOT NULL without default immediately**
   ```sql
   -- BAD
   ALTER TABLE users ADD COLUMN required VARCHAR(20) NOT NULL;

   -- GOOD
   ALTER TABLE users ADD COLUMN required VARCHAR(20);
   UPDATE users SET required = 'default' WHERE required IS NULL;
   ALTER TABLE users ALTER COLUMN required SET NOT NULL;
   ```

2. **Don't rename or drop columns directly**
   ```sql
   -- BAD
   ALTER TABLE users DROP COLUMN old_field;

   -- GOOD (use expand-contract)
   -- 1. Add new column
   -- 2. Dual-write period
   -- 3. Remove old column in later migration
   ```

3. **Don't run large data migrations in a single transaction**
   ```sql
   -- BAD (locks table for long time)
   BEGIN;
   UPDATE users SET normalized_email = LOWER(email);
   COMMIT;

   -- GOOD (batched)
   -- Process in batches outside transaction
   ```

4. **Don't modify old migrations**
   - Once applied, migrations are immutable
   - Create new migration to fix issues

5. **Don't skip testing rollback**
   - Always test the rollback procedure

---

## Backward Compatibility

### N-1 Compatibility Rule

Your database schema must be compatible with:
- **N**: Current application version
- **N-1**: Previous application version

This enables:
- Zero-downtime deployments
- Safe rollbacks
- Gradual rollouts

### Example: Adding a Required Field

```
Week 1: Migration adds nullable column + app reads it
Week 2: App starts writing to new column
Week 3: Backfill old data
Week 4: Make column NOT NULL
```

At each step, both old and new app versions work.

---

## Testing Migrations

### Local Testing

```bash
# Start local database
docker run -d --name postgres-test \
  -e POSTGRES_PASSWORD=secret \
  -p 5432:5432 \
  postgres:14

# Run migrations
flyway -url=jdbc:postgresql://localhost:5432/postgres \
       -user=postgres \
       -password=secret \
       -locations=filesystem:./flyway-migrations \
       migrate

# Test rollback (if applicable)
flyway -url=jdbc:postgresql://localhost:5432/postgres \
       -user=postgres \
       -password=secret \
       -locations=filesystem:./flyway-migrations \
       undo
```

### Staging Testing

1. **Restore production data to staging**
   ```bash
   pg_dump production_db | psql staging_db
   ```

2. **Run migration**
   ```bash
   flyway migrate
   ```

3. **Validate**
   - Check row counts
   - Verify data integrity
   - Test application functionality
   - Measure migration duration

4. **Test rollback**
   ```bash
   flyway undo
   ```

### Performance Testing

```sql
-- Check table size
SELECT pg_size_pretty(pg_total_relation_size('users'));

-- Estimate migration time
EXPLAIN ANALYZE UPDATE users SET status = 'active' WHERE status IS NULL;

-- Monitor locks
SELECT * FROM pg_locks WHERE NOT granted;
```

---

## Migration Best Practices

### 1. Version Control
- All migrations in Git
- Code review required
- Immutable once applied

### 2. Documentation
- Comment each migration
- Document rollback procedure
- Include ticket/issue references

### 3. Monitoring
- Track migration duration
- Alert on failures
- Log progress for long migrations

### 4. Communication
- Announce maintenance windows
- Notify team of schema changes
- Update API documentation

### 5. Automation
- CI/CD pipeline integration
- Automated testing
- Dry-run in staging

---

## Common Patterns

### Pattern: Add Index Safely

```sql
-- PostgreSQL
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- MySQL
ALTER TABLE users ADD INDEX idx_users_email(email), ALGORITHM=INPLACE, LOCK=NONE;
```

### Pattern: Add Foreign Key Safely

```sql
-- PostgreSQL 12+
ALTER TABLE orders
ADD CONSTRAINT fk_orders_user
FOREIGN KEY (user_id) REFERENCES users(id)
NOT VALID;

-- Validate in background
ALTER TABLE orders VALIDATE CONSTRAINT fk_orders_user;
```

### Pattern: Split Table (Vertical)

```sql
-- 1. Create new table
CREATE TABLE user_details (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    bio TEXT,
    preferences JSONB
);

-- 2. Copy data
INSERT INTO user_details (user_id, bio, preferences)
SELECT id, bio, preferences FROM users;

-- 3. Drop old columns (later)
ALTER TABLE users DROP COLUMN bio, DROP COLUMN preferences;
```

---

## Troubleshooting

### Issue: Migration Hangs

**Cause**: Table locks from other transactions

**Solution**:
```sql
-- Check locks
SELECT pid, usename, query, state
FROM pg_stat_activity
WHERE datname = 'mydb' AND state != 'idle';

-- Kill blocking queries (if safe)
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE datname = 'mydb' AND state = 'active' AND pid != pg_backend_pid();
```

### Issue: Out of Memory During Backfill

**Cause**: Trying to update too many rows at once

**Solution**: Use batched updates (see V3 example)

### Issue: Migration Failed Halfway

**Cause**: Error in SQL or constraint violation

**Solution**:
1. Check migration state
   ```sql
   SELECT * FROM flyway_schema_history ORDER BY installed_on DESC LIMIT 5;
   ```

2. Fix data issues manually if needed

3. Re-run migration or rollback

---

## Resources

- **Flyway**: https://flywaydb.org/documentation/
- **Liquibase**: https://docs.liquibase.com/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Expand-Contract**: https://martinfowler.com/bliki/ParallelChange.html
- **Zero-Downtime**: https://blog.codinghorror.com/zero-downtime-deployments/

---

## Netflix & Facebook Practices

### Netflix
- Automated migration testing in CI/CD
- Canary migrations to subset of database shards
- Chaos engineering during migrations
- Automated rollback on error

### Facebook
- Gradual schema rollout across datacenters
- Online schema change (OSC) tooling
- Automated compatibility testing
- Extensive pre-production validation

---

## Summary

Safe database migrations require:
1. **Backward compatibility** (N-1 support)
2. **Expand-contract pattern** for breaking changes
3. **Batched operations** for large datasets
4. **Thorough testing** in staging
5. **Monitoring and validation**
6. **Clear rollback procedures**

Always prioritize **zero downtime** and **safe rollbacks** over speed of migration.
