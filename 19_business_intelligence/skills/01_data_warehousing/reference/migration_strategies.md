# Data Warehouse Migration Strategies

Quick reference for migrating between data warehouses, modernization approaches, and cloud migration best practices.

## Migration Approaches

### Big Bang Migration

**Concept**: Switch from old to new system in single cutover

```
Preparation → Testing → Cutover Weekend → Go-Live
(Weeks/Months)         (Friday-Sunday)    (Monday)
```

**Pros**:
- ✅ Single transition event
- ✅ Shorter overall timeline
- ✅ No parallel operations
- ✅ Clean break from legacy

**Cons**:
- ❌ High risk
- ❌ Difficult to rollback
- ❌ All-or-nothing success
- ❌ Limited testing time

**When to Use**:
- Small data volumes (< 1 TB)
- Simple architecture
- Weekend downtime acceptable
- Low number of dependencies

### Phased Migration (Trickle)

**Concept**: Migrate incrementally, domain by domain or table by table

```
Phase 1: Migrate Customers (2 weeks)
Phase 2: Migrate Products (2 weeks)
Phase 3: Migrate Orders (3 weeks)
Phase 4: Migrate Inventory (2 weeks)
Phase 5: Decommission legacy (1 week)
```

**Pros**:
- ✅ Lower risk per phase
- ✅ Easier rollback
- ✅ Learn and adjust
- ✅ Continuous operation

**Cons**:
- ❌ Longer timeline
- ❌ Dual maintenance
- ❌ Complex data synchronization
- ❌ Incremental costs

**When to Use**:
- Large organizations
- Complex dependencies
- Zero downtime requirement
- Multiple stakeholder groups

### Parallel Run

**Concept**: Run old and new systems simultaneously

```
         Old Warehouse (Still active)
Source →
         New Warehouse (Parallel)

         Compare results → Validate → Cutover
```

**Duration**: 1-6 months parallel operation

**Pros**:
- ✅ Extensive validation
- ✅ Easy rollback
- ✅ Build confidence
- ✅ Users can test

**Cons**:
- ❌ Double infrastructure costs
- ❌ Double operational effort
- ❌ Long migration timeline
- ❌ Data synchronization complexity

**When to Use**:
- Critical business systems
- Complex logic to validate
- Regulatory compliance
- Risk-averse organization

### Hybrid Approach

**Concept**: Combine strategies for different components

```
Phase 1: Big Bang for Dimensions (Weekend)
Phase 2-6: Trickle for Fact Tables (5 weeks)
Phase 7: Parallel run for validation (2 weeks)
Phase 8: Cutover
```

## Migration Patterns

### Lift and Shift

**Approach**: Move existing design to new platform with minimal changes

```sql
-- Example: Redshift → Snowflake

-- 1. Export DDL from Redshift
-- 2. Convert to Snowflake syntax
-- 3. Create tables in Snowflake
-- 4. Copy data
-- 5. Recreate views and procedures

-- Redshift → Snowflake conversions
DISTKEY → CLUSTER BY
SORTKEY → CLUSTER BY (or partition)
ENCODE → Automatic in Snowflake
DISTSTYLE ALL → No equivalent (use clustering)
```

**Timeline**: 1-3 months
**Risk**: Low
**Benefit**: Fast, predictable
**Limitation**: Doesn't leverage new platform features

### Refactor and Optimize

**Approach**: Redesign to leverage target platform capabilities

```
Before (Redshift):
- Manually defined DISTKEY, SORTKEY
- Manual VACUUM and ANALYZE
- Table-level statistics

After (Snowflake):
- Automatic micro-partitioning
- Automatic clustering
- Zero-copy cloning
- Time travel
```

**Timeline**: 3-6 months
**Risk**: Medium
**Benefit**: Optimized performance, lower costs
**Limitation**: More complex, longer timeline

### Rearchitect

**Approach**: Complete redesign using modern patterns

```
Before: Traditional EDW (Inmon)
- Normalized 3NF
- ETL pipelines
- Batch processing

After: Modern Lakehouse (Medallion)
- Bronze → Silver → Gold
- ELT with dbt
- Streaming + Batch
```

**Timeline**: 6-12 months
**Risk**: High
**Benefit**: Modern architecture, future-proof
**Limitation**: Significant effort, business disruption

## Platform-Specific Migrations

### On-Premise → Snowflake

**Migration Steps**:

1. **Assessment**
```sql
-- Inventory current state
SELECT
    schema_name,
    table_name,
    row_count,
    size_gb
FROM current_warehouse.information_schema.tables
ORDER BY size_gb DESC;

-- Identify dependencies
-- - ETL jobs
-- - BI reports
-- - Stored procedures
-- - Custom applications
```

2. **DDL Conversion**
```sql
-- Oracle → Snowflake
NUMBER → NUMBER (compatible)
VARCHAR2 → VARCHAR
DATE → DATE or TIMESTAMP_NTZ
CLOB → VARCHAR (max 16 MB)

-- Stored procedures → JavaScript UDFs or Python UDFs
-- ETL jobs → dbt or Snowflake tasks
```

3. **Data Migration**
```sql
-- Option 1: Export to S3, COPY into Snowflake
-- Oracle export
expdp system/password DIRECTORY=dump_dir DUMPFILE=export.dmp

-- Upload to S3
aws s3 cp export.dmp s3://bucket/migration/

-- Snowflake COPY
COPY INTO snowflake_table
FROM @s3_stage/export.dmp
FILE_FORMAT = (TYPE = 'CSV');

-- Option 2: Use migration tools
-- AWS DMS, Fivetran, Matillion, SnowConvert
```

4. **Validation**
```sql
-- Row count validation
SELECT COUNT(*) FROM oracle_table;    -- 1,000,000
SELECT COUNT(*) FROM snowflake_table; -- 1,000,000

-- Checksum validation
SELECT SUM(order_amount) FROM oracle_table;
SELECT SUM(order_amount) FROM snowflake_table;

-- Sample data comparison
SELECT * FROM oracle_table WHERE id = 12345;
SELECT * FROM snowflake_table WHERE id = 12345;
```

### Redshift → BigQuery

**Key Considerations**:
```sql
-- Redshift DISTKEY → BigQuery Partition
-- Redshift
CREATE TABLE orders (...)
DISTKEY(order_date)
SORTKEY(order_date, customer_id);

-- BigQuery
CREATE TABLE orders (...)
PARTITION BY DATE(order_date)
CLUSTER BY customer_id;

-- Data loading
-- Option 1: Redshift → S3 → BigQuery
UNLOAD ('SELECT * FROM orders')
TO 's3://bucket/orders/'
PARALLEL ON;

bq load --source_format=PARQUET \
  dataset.orders \
  gs://bucket/orders/*

-- Option 2: Federated query
CREATE EXTERNAL TABLE bq_dataset.orders_external
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://bucket/orders/*']
);

INSERT INTO bq_dataset.orders
SELECT * FROM bq_dataset.orders_external;
```

### BigQuery → Snowflake

```sql
-- Export from BigQuery
bq extract \
  --destination_format PARQUET \
  dataset.table \
  gs://bucket/export/*

-- Load into Snowflake
COPY INTO snowflake_table
FROM @gcs_stage/export/
FILE_FORMAT = (TYPE = 'PARQUET');
```

### SQL Server → Azure Synapse

```sql
-- Option 1: Azure Data Factory
-- Create pipeline: SQL Server → ADLS → Synapse

-- Option 2: PolyBase
-- External table on ADLS
CREATE EXTERNAL TABLE staging.customers
WITH (
    LOCATION = '/customers/',
    DATA_SOURCE = adls_source,
    FILE_FORMAT = parquet_format
);

-- Load into Synapse table
CREATE TABLE synapse.customers
WITH (
    DISTRIBUTION = HASH(customer_id),
    CLUSTERED COLUMNSTORE INDEX
)
AS SELECT * FROM staging.customers;
```

## Migration Tools

### AWS Database Migration Service (DMS)
```
Use Case: On-premise → AWS (Redshift, S3)
Features:
- Continuous replication
- Schema conversion
- Minimal downtime
- Supports 20+ sources
```

### Striim
```
Use Case: Real-time CDC to cloud
Features:
- Real-time streaming
- Change data capture
- Low latency
- Multiple targets
```

### Fivetran
```
Use Case: SaaS → Cloud warehouse
Features:
- Automated connectors
- Schema drift handling
- Managed service
- 150+ connectors
```

### Matillion
```
Use Case: ETL transformation
Features:
- Cloud-native ETL
- Visual designer
- Snowflake/BigQuery/Redshift
- Built-in connectors
```

## Migration Checklist

### Pre-Migration (Weeks 1-4)
- [ ] Inventory all tables, views, procedures
- [ ] Document dependencies (jobs, reports, apps)
- [ ] Identify stakeholders
- [ ] Choose migration approach
- [ ] Select migration tools
- [ ] Create project plan and timeline
- [ ] Set up target environment
- [ ] Establish rollback plan
- [ ] Define success criteria

### Migration Preparation (Weeks 5-8)
- [ ] Convert DDL for target platform
- [ ] Refactor stored procedures
- [ ] Update ETL pipelines
- [ ] Create data validation scripts
- [ ] Set up monitoring and alerting
- [ ] Prepare test data and scenarios
- [ ] Train team on new platform
- [ ] Document migration procedures

### Execution (Weeks 9-12)
- [ ] Migrate reference data first
- [ ] Migrate dimension tables
- [ ] Migrate fact tables (incremental)
- [ ] Validate row counts and checksums
- [ ] Test ETL pipelines
- [ ] Execute UAT with business users
- [ ] Performance test critical queries
- [ ] Update documentation

### Post-Migration (Weeks 13-16)
- [ ] Monitor performance metrics
- [ ] Optimize slow queries
- [ ] Adjust warehouse sizing
- [ ] Review and optimize costs
- [ ] Gather user feedback
- [ ] Decommission legacy system
- [ ] Update disaster recovery plan
- [ ] Conduct post-mortem review

## Validation Strategies

### Data Validation
```sql
-- Row count comparison
SELECT
    'Source' as location,
    COUNT(*) as row_count
FROM source_table
UNION ALL
SELECT
    'Target' as location,
    COUNT(*) as row_count
FROM target_table;

-- Aggregation comparison
SELECT
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount,
    MIN(order_date) as min_date,
    MAX(order_date) as max_date
FROM source_table;

-- Sample comparison (random 1000 rows)
SELECT * FROM source_table SAMPLE (1000 ROWS);
SELECT * FROM target_table SAMPLE (1000 ROWS);
```

### Schema Validation
```sql
-- Column count and types
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;

-- Primary key validation
SELECT constraint_name, column_name
FROM information_schema.key_column_usage
WHERE table_schema = 'public';
```

### Performance Validation
```sql
-- Benchmark queries
-- Run same queries on old and new platforms
-- Compare execution times

-- Example
EXPLAIN ANALYZE
SELECT
    customer_id,
    COUNT(*) as order_count,
    SUM(amount) as total_amount
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY customer_id
ORDER BY total_amount DESC
LIMIT 100;
```

## Risk Mitigation

### Rollback Strategy
```
1. Keep old system operational during parallel run
2. Document rollback procedures
3. Maintain data synchronization
4. Test rollback in non-production
5. Define rollback decision criteria
6. Communicate rollback plan to stakeholders
```

### Data Integrity
```
- Use transactions where possible
- Implement checksums
- Validate before and after
- Maintain audit logs
- Keep backups of source data
```

### Business Continuity
```
- Plan for minimal downtime
- Schedule during low-usage periods
- Communicate timeline to users
- Have support team on standby
- Prepare rollback communication
```

## Cost Considerations

### Pre-Migration Costs
```
- Assessment and planning
- Tool licenses
- Training
- Test environment setup
- Consulting/contractors
```

### Migration Costs
```
- Target platform setup
- Data transfer costs
- Parallel run (dual systems)
- Testing and validation
- Team overtime
```

### Post-Migration Costs
```
- Target platform monthly costs
- Monitoring tools
- Support and optimization
- Decommissioning legacy system
- Documentation updates
```

### Cost Optimization Post-Migration
```
- Right-size warehouses/clusters
- Implement auto-suspend/auto-resume
- Use reserved capacity where applicable
- Optimize queries for new platform
- Implement cost monitoring and alerting
- Review and adjust partition strategies
```

## Timeline Estimates

### Small Migration (< 1 TB, < 100 tables)
```
Planning: 2-4 weeks
Preparation: 4-6 weeks
Execution: 2-4 weeks
Validation: 2 weeks
Total: 10-16 weeks (2.5-4 months)
```

### Medium Migration (1-10 TB, 100-500 tables)
```
Planning: 4-6 weeks
Preparation: 8-12 weeks
Execution: 4-8 weeks
Validation: 4 weeks
Total: 20-30 weeks (5-7.5 months)
```

### Large Migration (> 10 TB, > 500 tables)
```
Planning: 6-8 weeks
Preparation: 12-16 weeks
Execution: 8-16 weeks
Validation: 6-8 weeks
Total: 32-48 weeks (8-12 months)
```

## Common Pitfalls

❌ **Underestimating dependencies**: Map all downstream systems
❌ **Insufficient testing**: Test all reports, dashboards, integrations
❌ **Ignoring performance**: Optimize for target platform characteristics
❌ **Poor communication**: Keep stakeholders informed throughout
❌ **No rollback plan**: Always have a way back
❌ **Inadequate validation**: Verify data integrity thoroughly
❌ **Neglecting documentation**: Update all docs during migration
❌ **Rushing go-live**: Take time to validate before cutover

## Success Factors

✅ **Executive sponsorship**: Clear ownership and support
✅ **Detailed planning**: Comprehensive project plan
✅ **Experienced team**: Platform expertise critical
✅ **Adequate testing**: Thorough validation before go-live
✅ **User involvement**: Include end users in UAT
✅ **Clear communication**: Regular updates to stakeholders
✅ **Flexible timeline**: Buffer for unexpected issues
✅ **Post-go-live support**: Dedicated team for first weeks
