# OLAP Troubleshooting Guide

## Common Issues

### 1. Slow Queries

**Symptoms:**
- Queries taking > 10 seconds
- Timeouts
- User complaints

**Diagnosis:**
```mdx
-- Check query plan
SET SHOWPLAN_XML ON

SELECT [Measures].[Sales] ON 0
FROM [Sales]

-- Review aggregation usage
SELECT AGGREGATION_NAME, USED_COUNT
FROM $SYSTEM.DISCOVER_PARTITION_STAT
```

**Solutions:**
- Add aggregations for common query patterns
- Implement partitioning
- Optimize MDX/DAX queries
- Increase memory allocation

### 2. Processing Failures

**Symptoms:**
- Processing jobs fail
- Error messages in logs
- Data not refreshing

**Common Causes:**
- Source database unavailable
- Memory pressure
- Lock timeouts
- Schema changes

**Solutions:**
```powershell
# Check processing errors
Get-EventLog -LogName Application -Source MSOLAP |
    Where-Object { $_.EntryType -eq "Error" } |
    Select-Object -First 10

# Retry processing
try {
    $db.Process([ProcessType]::ProcessFull)
}
catch {
    Write-Log "Processing failed: $_"
    # Implement retry logic
}
```

### 3. Memory Issues

**Symptoms:**
- Out of memory errors
- Slow performance
- Processing failures

**Diagnosis:**
```mdx
SELECT *
FROM $SYSTEM.DISCOVER_MEMORYUSAGE

SELECT MEMORY_USAGE_KB
FROM $SYSTEM.DISCOVER_OBJECT_MEMORY_USAGE
ORDER BY MEMORY_USAGE_KB DESC
```

**Solutions:**
- Increase memory allocation (80% of RAM)
- Reduce cache size
- Implement partitioning
- Process during off-hours

### 4. Security Issues

**Symptoms:**
- Users see no data
- "Insufficient permissions" errors
- Wrong data visible

**Diagnosis:**
```mdx
-- Test security
EXECUTE AS LOGIN = 'DOMAIN\User'
SELECT [Measures].[Sales] ON 0 FROM [Sales]
REVERT
```

**Solutions:**
- Verify role membership
- Check AllowedSet MDX
- Review role precedence
- Test with View As

### 5. Incorrect Results

**Symptoms:**
- Totals don't match source
- Missing data
- Duplicate counts

**Diagnosis:**
```sql
-- Compare cube to source
SELECT SUM(SalesAmount)
FROM FactSales
-- vs cube total

-- Check for duplicates
SELECT DateKey, ProductKey, COUNT(*)
FROM FactSales
GROUP BY DateKey, ProductKey
HAVING COUNT(*) > 1
```

**Solutions:**
- Verify grain definition
- Check dimension relationships
- Review SCD implementation
- Validate source data quality

## Debugging Tools

### 1. SQL Server Profiler
Capture:
- Query events
- Processing events
- Errors

### 2. Flight Recorder
```powershell
# Enable flight recorder
$server.ServerProperties["Log\FlightRecorder\Enabled"].Value = $true
$server.Update()
```

### 3. DMVs
```mdx
-- Current activity
SELECT * FROM $SYSTEM.DISCOVER_SESSIONS
SELECT * FROM $SYSTEM.DISCOVER_COMMANDS
SELECT * FROM $SYSTEM.DISCOVER_LOCKS
```

## Prevention

1. **Monitoring**
   - Set up alerts
   - Regular health checks
   - Capacity planning

2. **Testing**
   - Test in non-production
   - Performance testing
   - Security testing

3. **Documentation**
   - Document architecture
   - Record changes
   - Maintain runbooks
