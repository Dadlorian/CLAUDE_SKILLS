-- Performance Monitoring and Optimization Queries
-- Platform-agnostic warehouse performance analysis
-- Description: Monitor and optimize data warehouse performance

-- ============================================
-- QUERY PERFORMANCE ANALYSIS - SNOWFLAKE
-- ============================================

-- Top 10 longest running queries in the last 24 hours
SELECT
    query_id,
    query_text,
    user_name,
    warehouse_name,
    database_name,
    schema_name,
    execution_status,
    total_elapsed_time / 1000 AS execution_time_seconds,
    bytes_scanned / (1024 * 1024 * 1024) AS gb_scanned,
    rows_produced,
    compilation_time / 1000 AS compilation_seconds,
    execution_time / 1000 AS execution_seconds,
    queued_provisioning_time / 1000 AS queue_time_seconds,
    start_time,
    end_time
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
  AND execution_status = 'SUCCESS'
ORDER BY total_elapsed_time DESC
LIMIT 10;

-- Queries with high data spillage
SELECT
    query_id,
    query_text,
    user_name,
    warehouse_name,
    bytes_spilled_to_local_storage / (1024 * 1024 * 1024) AS local_spillage_gb,
    bytes_spilled_to_remote_storage / (1024 * 1024 * 1024) AS remote_spillage_gb,
    total_elapsed_time / 1000 AS execution_time_seconds,
    start_time
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
  AND (bytes_spilled_to_local_storage > 0 OR bytes_spilled_to_remote_storage > 0)
ORDER BY bytes_spilled_to_remote_storage DESC
LIMIT 20;

-- Most frequently executed queries
SELECT
    SUBSTR(query_text, 1, 100) AS query_preview,
    COUNT(*) AS execution_count,
    AVG(total_elapsed_time) / 1000 AS avg_execution_seconds,
    SUM(total_elapsed_time) / 1000 AS total_execution_seconds,
    AVG(bytes_scanned) / (1024 * 1024 * 1024) AS avg_gb_scanned
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
  AND execution_status = 'SUCCESS'
GROUP BY SUBSTR(query_text, 1, 100)
HAVING COUNT(*) > 10
ORDER BY execution_count DESC
LIMIT 20;

-- ============================================
-- WAREHOUSE USAGE ANALYSIS - SNOWFLAKE
-- ============================================

-- Warehouse credit consumption by day
SELECT
    warehouse_name,
    DATE_TRUNC('day', start_time) AS usage_date,
    SUM(credits_used) AS total_credits,
    COUNT(*) AS query_count,
    AVG(credits_used) AS avg_credits_per_query
FROM snowflake.account_usage.warehouse_metering_history
WHERE start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
GROUP BY warehouse_name, DATE_TRUNC('day', start_time)
ORDER BY usage_date DESC, total_credits DESC;

-- Warehouse idle time analysis
SELECT
    warehouse_name,
    DATE_TRUNC('hour', start_time) AS hour,
    SUM(CASE WHEN query_count = 0 THEN credits_used ELSE 0 END) AS idle_credits,
    SUM(credits_used) AS total_credits,
    ROUND(100.0 * SUM(CASE WHEN query_count = 0 THEN credits_used ELSE 0 END) /
          NULLIF(SUM(credits_used), 0), 2) AS idle_percentage
FROM snowflake.account_usage.warehouse_metering_history
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY warehouse_name, DATE_TRUNC('hour', start_time)
HAVING SUM(CASE WHEN query_count = 0 THEN credits_used ELSE 0 END) > 0
ORDER BY idle_credits DESC;

-- ============================================
-- QUERY PERFORMANCE ANALYSIS - BIGQUERY
-- ============================================

-- Top expensive queries by slot time
SELECT
    job_id,
    user_email,
    project_id,
    TIMESTAMP_MILLIS(creation_time) AS created_at,
    query,
    total_slot_ms / 1000 / 60 AS total_slot_minutes,
    total_bytes_processed / (1024 * 1024 * 1024) AS gb_processed,
    total_bytes_billed / (1024 * 1024 * 1024) AS gb_billed,
    (total_bytes_billed / (1024 * 1024 * 1024)) * 5 / 1000 AS estimated_cost_usd,
    ROUND((end_time - start_time) / 1000, 2) AS duration_seconds,
    cache_hit,
    state
FROM `project.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
  AND state = 'DONE'
ORDER BY total_slot_ms DESC
LIMIT 20;

-- Queries that would benefit from partitioning
SELECT
    table_schema,
    table_name,
    SUM(total_bytes_processed) / (1024 * 1024 * 1024) AS total_gb_scanned,
    COUNT(*) AS query_count,
    AVG(total_bytes_processed) / (1024 * 1024 * 1024) AS avg_gb_per_query
FROM `project.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT` j
CROSS JOIN UNNEST(referenced_tables) AS t
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND state = 'DONE'
  AND NOT cache_hit
GROUP BY table_schema, table_name
HAVING SUM(total_bytes_processed) > 1024 * 1024 * 1024 * 100  -- > 100 GB
ORDER BY total_gb_scanned DESC;

-- ============================================
-- TABLE OPTIMIZATION ANALYSIS
-- ============================================

-- Tables with poor clustering (Snowflake)
SELECT
    table_schema,
    table_name,
    clustering_key,
    AVG(average_depth) AS avg_cluster_depth,
    AVG(average_overlaps) AS avg_cluster_overlaps,
    CASE
        WHEN AVG(average_depth) > 10 THEN 'Needs Reclustering'
        WHEN AVG(average_depth) > 5 THEN 'Monitor'
        ELSE 'Good'
    END AS clustering_health
FROM snowflake.account_usage.automatic_clustering_history
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY table_schema, table_name, clustering_key
ORDER BY avg_cluster_depth DESC;

-- Partition health analysis (BigQuery)
SELECT
    table_schema,
    table_name,
    partition_id,
    total_rows,
    total_logical_bytes / (1024 * 1024 * 1024) AS logical_gb,
    total_billable_bytes / (1024 * 1024 * 1024) AS billable_gb,
    TIMESTAMP_MILLIS(last_modified_time) AS last_modified
FROM `project.dataset.INFORMATION_SCHEMA.PARTITIONS`
WHERE partition_id IS NOT NULL
ORDER BY total_billable_bytes DESC;

-- ============================================
-- MATERIALIZED VIEW PERFORMANCE
-- ============================================

-- Materialized view refresh statistics (Snowflake)
SELECT
    database_name,
    schema_name,
    name AS view_name,
    state,
    refresh_action,
    refresh_trigger,
    behind_by,
    last_refresh_start_time,
    last_refresh_end_time,
    DATEDIFF(second, last_refresh_start_time, last_refresh_end_time) AS refresh_duration_seconds
FROM snowflake.account_usage.materialized_view_refresh_history
WHERE last_refresh_start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY refresh_duration_seconds DESC;

-- ============================================
-- INDEX AND STATISTICS ANALYSIS
-- ============================================

-- Missing statistics on frequently queried columns
WITH column_usage AS (
    SELECT
        table_name,
        column_name,
        COUNT(*) AS usage_count
    FROM snowflake.account_usage.query_history
    CROSS JOIN LATERAL FLATTEN(input => columns_used)
    WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    GROUP BY table_name, column_name
),
table_stats AS (
    SELECT
        table_name,
        column_name,
        last_altered
    FROM information_schema.columns
)
SELECT
    cu.table_name,
    cu.column_name,
    cu.usage_count,
    ts.last_altered AS stats_last_updated,
    DATEDIFF(day, ts.last_altered, CURRENT_TIMESTAMP()) AS days_since_stats_update
FROM column_usage cu
LEFT JOIN table_stats ts
    ON cu.table_name = ts.table_name
    AND cu.column_name = ts.column_name
WHERE cu.usage_count > 100
  AND DATEDIFF(day, ts.last_altered, CURRENT_TIMESTAMP()) > 7
ORDER BY cu.usage_count DESC;

-- ============================================
-- JOIN PERFORMANCE ANALYSIS
-- ============================================

-- Identify inefficient joins (cross joins, cartesian products)
SELECT
    query_id,
    query_text,
    user_name,
    total_elapsed_time / 1000 AS execution_seconds,
    rows_produced,
    bytes_scanned / (1024 * 1024 * 1024) AS gb_scanned,
    compilation_time / 1000 AS compilation_seconds
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
  AND (
      LOWER(query_text) LIKE '%cross join%'
      OR (rows_produced > 1000000 AND bytes_scanned / rows_produced > 10000)
  )
ORDER BY rows_produced DESC;

-- ============================================
-- STORAGE OPTIMIZATION
-- ============================================

-- Tables with high storage but low query frequency
WITH table_sizes AS (
    SELECT
        table_schema,
        table_name,
        active_bytes / (1024 * 1024 * 1024) AS active_gb,
        time_travel_bytes / (1024 * 1024 * 1024) AS time_travel_gb,
        failsafe_bytes / (1024 * 1024 * 1024) AS failsafe_gb
    FROM snowflake.account_usage.table_storage_metrics
    WHERE deleted IS NULL
),
query_frequency AS (
    SELECT
        tables_used.value:objectName::STRING AS table_name,
        COUNT(*) AS query_count
    FROM snowflake.account_usage.access_history
    LATERAL FLATTEN(input => base_objects_accessed) AS tables_used
    WHERE query_start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
    GROUP BY table_name
)
SELECT
    ts.table_schema,
    ts.table_name,
    ts.active_gb,
    ts.time_travel_gb,
    ts.failsafe_gb,
    ts.active_gb + ts.time_travel_gb + ts.failsafe_gb AS total_gb,
    COALESCE(qf.query_count, 0) AS queries_last_30_days,
    CASE
        WHEN COALESCE(qf.query_count, 0) = 0 THEN 'Never Queried'
        WHEN COALESCE(qf.query_count, 0) < 10 THEN 'Rarely Queried'
        WHEN COALESCE(qf.query_count, 0) < 100 THEN 'Occasionally Queried'
        ELSE 'Frequently Queried'
    END AS usage_category
FROM table_sizes ts
LEFT JOIN query_frequency qf ON ts.table_name = qf.table_name
WHERE ts.active_gb > 1
ORDER BY total_gb DESC;

-- ============================================
-- QUERY ACCELERATION OPPORTUNITIES
-- ============================================

-- Queries that scan large amounts of data repeatedly
SELECT
    SUBSTR(query_text, 1, 100) AS query_pattern,
    COUNT(*) AS execution_count,
    AVG(bytes_scanned) / (1024 * 1024 * 1024) AS avg_gb_scanned,
    SUM(bytes_scanned) / (1024 * 1024 * 1024) AS total_gb_scanned,
    AVG(total_elapsed_time) / 1000 AS avg_execution_seconds,
    SUM(total_elapsed_time) / 1000 AS total_execution_seconds
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
  AND execution_status = 'SUCCESS'
  AND bytes_scanned > 1024 * 1024 * 1024  -- > 1 GB
GROUP BY SUBSTR(query_text, 1, 100)
HAVING COUNT(*) > 5
ORDER BY total_gb_scanned DESC;

-- ============================================
-- CONCURRENCY MONITORING
-- ============================================

-- Peak concurrency periods
SELECT
    DATE_TRUNC('hour', start_time) AS hour,
    MAX(concurrent_queries) AS peak_concurrency,
    AVG(concurrent_queries) AS avg_concurrency,
    SUM(credits_used) AS total_credits
FROM (
    SELECT
        start_time,
        COUNT(*) OVER (
            ORDER BY start_time
            RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS concurrent_queries,
        1 AS credits_used
    FROM snowflake.account_usage.query_history
    WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
)
GROUP BY DATE_TRUNC('hour', start_time)
ORDER BY peak_concurrency DESC;

-- ============================================
-- PERFORMANCE RECOMMENDATIONS
-- ============================================

-- Generate optimization recommendations
WITH performance_issues AS (
    SELECT
        query_id,
        query_text,
        'High spillage detected' AS issue,
        'Consider increasing warehouse size' AS recommendation,
        bytes_spilled_to_remote_storage / (1024 * 1024 * 1024) AS severity
    FROM snowflake.account_usage.query_history
    WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
      AND bytes_spilled_to_remote_storage > 1024 * 1024 * 1024

    UNION ALL

    SELECT
        query_id,
        query_text,
        'Long compilation time' AS issue,
        'Review query complexity and consider simplifying' AS recommendation,
        compilation_time / 1000 AS severity
    FROM snowflake.account_usage.query_history
    WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
      AND compilation_time > execution_time * 0.5

    UNION ALL

    SELECT
        query_id,
        query_text,
        'Full table scan detected' AS issue,
        'Add clustering keys or filters' AS recommendation,
        bytes_scanned / (1024 * 1024 * 1024) AS severity
    FROM snowflake.account_usage.query_history
    WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
      AND bytes_scanned > 10 * 1024 * 1024 * 1024
      AND partitions_scanned > 100
)
SELECT
    issue,
    recommendation,
    COUNT(*) AS occurrence_count,
    AVG(severity) AS avg_severity,
    MAX(severity) AS max_severity
FROM performance_issues
GROUP BY issue, recommendation
ORDER BY occurrence_count DESC;

-- ============================================
-- CACHE EFFICIENCY ANALYSIS
-- ============================================

-- Query result cache hit rate
SELECT
    DATE_TRUNC('day', start_time) AS date,
    warehouse_name,
    COUNT(*) AS total_queries,
    SUM(CASE WHEN query_load_percent = 0 THEN 1 ELSE 0 END) AS cache_hits,
    ROUND(100.0 * SUM(CASE WHEN query_load_percent = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS cache_hit_rate
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
  AND execution_status = 'SUCCESS'
GROUP BY DATE_TRUNC('day', start_time), warehouse_name
ORDER BY date DESC, warehouse_name;

-- ============================================
-- COST OPTIMIZATION QUERIES
-- ============================================

-- Estimate query costs (BigQuery)
SELECT
    user_email,
    DATE(TIMESTAMP_MILLIS(creation_time)) AS query_date,
    COUNT(*) AS query_count,
    SUM(total_bytes_billed) / (1024 * 1024 * 1024) AS total_gb_billed,
    SUM(total_bytes_billed) / (1024 * 1024 * 1024) * 5 / 1000 AS estimated_cost_usd
FROM `project.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND state = 'DONE'
  AND job_type = 'QUERY'
GROUP BY user_email, DATE(TIMESTAMP_MILLIS(creation_time))
ORDER BY estimated_cost_usd DESC;
