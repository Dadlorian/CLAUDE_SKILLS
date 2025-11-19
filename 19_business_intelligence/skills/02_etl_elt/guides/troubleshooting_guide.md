# Troubleshooting Guide

## dbt Issues

### Model Not Found
```
Error: Model 'stg_customers' not found
```
**Solutions**:
- Check spelling in `{{ ref('stg_customers') }}`
- Verify model file exists
- Run `dbt compile` to check compilation

### Circular Dependency
```
Found a cycle in the dependency graph
```
**Solutions**:
- Review model dependencies
- Break circular references
- Use ephemeral models if needed

### Compilation Error
```
Compilation Error in model dim_customers
  column "invalid_column" does not exist
```
**Solutions**:
- Check column names in source
- Verify schema hasn't changed
- Run `dbt debug` to test connection

### Incremental Issues
```
Duplicates found in incremental model
```
**Solutions**:
- Set correct `unique_key`
- Check incremental logic
- Run full refresh: `dbt run --full-refresh`

## Airflow Issues

### Task Stuck in Running
**Cause**: Deadlock, zombie process, or lost worker

**Solutions**:
```bash
# Clear task state
airflow tasks clear dag_id -t task_id

# Restart scheduler
airflow scheduler restart
```

### Import Errors
```
Broken DAG: No module named 'my_module'
```
**Solutions**:
- Install missing package: `pip install my_module`
- Check PYTHONPATH
- Verify DAG file syntax

### Connection Timeout
```
Could not connect to database
```
**Solutions**:
- Check connection settings in Airflow UI
- Verify firewall rules
- Test connection manually

## Data Quality Issues

### High Test Failure Rate
**Investigation**:
```sql
-- Find failing tests
SELECT
    test_name,
    failure_count,
    executed_at
FROM dbt_test_results
WHERE status = 'fail'
ORDER BY executed_at DESC
```

**Solutions**:
- Review test logic
- Check for data quality issues at source
- Adjust test thresholds if needed

### Schema Drift
```
Column 'new_field' not found in target
```
**Solutions**:
- Enable `on_schema_change='sync_all_columns'`
- Run full refresh
- Update dependent models

## Performance Issues

### Slow Queries
**Investigation**:
```sql
-- Snowflake
SELECT
    query_text,
    execution_time,
    bytes_scanned
FROM query_history
WHERE execution_time > 60000  -- > 1 minute
ORDER BY execution_time DESC
```

**Solutions**:
- Add WHERE clause to filter early
- Use incremental models
- Partition/cluster tables
- Optimize joins

### Out of Memory
**Solutions**:
- Increase warehouse size
- Process in batches
- Use incremental processing
- Optimize aggregations

## Connection Issues

### Warehouse Unavailable
```
Connection refused
```
**Solutions**:
- Check warehouse is running
- Verify credentials
- Check IP whitelist
- Review network settings

### Timeout Errors
```
Query timeout after 300 seconds
```
**Solutions**:
- Increase timeout setting
- Optimize query
- Use larger warehouse
- Process in smaller batches

## Cost Issues

### Unexpected High Costs
**Investigation**:
```sql
-- Find expensive queries
SELECT
    query_text,
    warehouse_name,
    credits_used
FROM query_history
WHERE start_time >= CURRENT_DATE - 7
ORDER BY credits_used DESC
LIMIT 100
```

**Solutions**:
- Optimize expensive queries
- Use appropriate warehouse size
- Enable auto-suspend
- Review full refreshes

## Recovery Procedures

### Restore from Backup
```sql
-- Snowflake time travel
CREATE TABLE orders_restored AS
SELECT * FROM orders
AT(TIMESTAMP => '2024-01-15 10:00:00');
```

### Rollback dbt Changes
```bash
# Revert to previous version
git revert HEAD

# Run full refresh
dbt run --full-refresh
```

### Replay Failed DAG Runs
```bash
# Clear and re-run
airflow dags backfill -s 2024-01-15 -e 2024-01-15 dag_id
```

## Getting Help

1. **Check Logs**: First place to look
2. **Search Docs**: Official documentation
3. **Community**: Slack, Discourse, Stack Overflow
4. **GitHub Issues**: Known bugs and workarounds
5. **Support**: Vendor support for production issues

