# Performance Monitoring Guide

## Key Metrics

### Query Performance
- Average query duration: < 3 seconds
- 95th percentile: < 5 seconds
- Slow queries: < 5% of total

### Processing Performance
- Rows/second: > 10,000
- Partition processing: < 5 minutes
- Full process: < 4 hours

## Monitoring Tools

### DMVs (Dynamic Management Views)
```mdx
-- Active sessions
SELECT *
FROM $SYSTEM.DISCOVER_SESSIONS
WHERE SESSION_ELAPSED_TIME_MS > 10000

-- Long-running queries
SELECT
    SESSION_SPID,
    SESSION_USER_NAME,
    SESSION_ELAPSED_TIME_MS,
    SESSION_LAST_COMMAND
FROM $SYSTEM.DISCOVER_SESSIONS
ORDER BY SESSION_ELAPSED_TIME_MS DESC

-- Memory usage
SELECT *
FROM $SYSTEM.DISCOVER_MEMORYUSAGE

-- Cache hit rate
SELECT
    (CACHE_LOOKUPS - CACHE_MISSES) * 100.0 / CACHE_LOOKUPS as HitRatePercent
FROM $SYSTEM.DISCOVER_CACHES
```

### SQL Server Profiler
Monitor events:
- Query Begin/End
- Query Subcube
- Progress Report
- Error

### Performance Counters
- MSAS:Storage Engine Query
- MSAS:Processing
- MSAS:Memory

## Optimization Techniques

### 1. Aggregation Hit Rate
Target: > 70%

```sql
SELECT
    PARTITION_NAME,
    AGGREGATION_NAME,
    USED_COUNT
FROM $SYSTEM.DISCOVER_PARTITION_STAT
WHERE AGGREGATION_NAME IS NOT NULL
ORDER BY USED_COUNT DESC
```

### 2. Query Tuning
- Use NONEMPTY
- Filter early
- Avoid large crossjoins
- Use appropriate MDX/DAX patterns

### 3. Processing Optimization
- Parallel processing
- Incremental processing
- Optimize source queries
- Proper indexing

## Alerting

### Set Up Alerts
```powershell
# Monitor long-running queries
$threshold = 30000  # 30 seconds

$longQueries = Invoke-ASCmd -Query @"
    SELECT *
    FROM `$SYSTEM.DISCOVER_SESSIONS
    WHERE SESSION_ELAPSED_TIME_MS > $threshold
"@

if ($longQueries.Count -gt 0) {
    Send-Alert "Long running queries detected"
}
```

## Best Practices

1. **Baseline Performance**
   - Establish normal metrics
   - Track trends over time

2. **Regular Monitoring**
   - Daily: Query performance
   - Weekly: Processing metrics
   - Monthly: Capacity planning

3. **Proactive Optimization**
   - Review slow queries
   - Update aggregations
   - Archive old data
