-- ============================================================
-- Self-Service Analytics Platform - Usage Analytics Queries
-- Production-ready analytics for platform monitoring
-- ============================================================
-- Version: 1.0
-- Last Updated: November 2024
-- Owner: Analytics Platform Team

-- ============================================================
-- 1. DAILY PLATFORM ACTIVITY DASHBOARD
-- ============================================================

-- Query 1.1: Daily Active Users by Role
CREATE OR REPLACE VIEW analytics_platform.vw_daily_active_users AS
SELECT
  DATE(query_timestamp) as activity_date,
  user_role,
  COUNT(DISTINCT user_email) as unique_users,
  COUNT(DISTINCT query_id) as total_queries,
  AVG(query_execution_time_seconds) as avg_execution_time,
  SUM(CASE WHEN query_execution_time_seconds > 300 THEN 1 ELSE 0 END) as slow_queries
FROM analytics_platform.query_execution_log
WHERE query_timestamp >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE(query_timestamp), user_role
ORDER BY activity_date DESC, unique_users DESC;

-- Query 1.2: Platform Adoption Trend
SELECT
  DATE_TRUNC('week', query_timestamp) as week_start,
  COUNT(DISTINCT user_email) as active_users,
  COUNT(DISTINCT CASE WHEN user_role = 'analyst' THEN user_email END) as analyst_count,
  COUNT(DISTINCT CASE WHEN user_role = 'viewer' THEN user_email END) as viewer_count,
  COUNT(DISTINCT CASE WHEN user_role = 'engineer' THEN user_email END) as engineer_count,
  COUNT(DISTINCT dashboard_id) as dashboards_accessed,
  COUNT(*) as total_query_count
FROM analytics_platform.query_execution_log
WHERE query_timestamp >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('week', query_timestamp)
ORDER BY week_start DESC;

-- ============================================================
-- 2. QUERY PERFORMANCE ANALYTICS
-- ============================================================

-- Query 2.1: Slowest Queries by User
SELECT
  user_email,
  user_team,
  COUNT(*) as query_count,
  AVG(query_execution_time_seconds) as avg_time,
  MAX(query_execution_time_seconds) as max_time,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY query_execution_time_seconds) as p95_time,
  SUM(warehouse_credits_consumed) as total_credits
FROM analytics_platform.query_execution_log
WHERE query_timestamp >= CURRENT_DATE - INTERVAL '7 days'
  AND query_execution_time_seconds IS NOT NULL
GROUP BY user_email, user_team
HAVING AVG(query_execution_time_seconds) > 60
ORDER BY avg_time DESC
LIMIT 20;

-- Query 2.2: Query Performance Distribution
SELECT
  DATE(query_timestamp) as query_date,
  CASE
    WHEN query_execution_time_seconds < 5 THEN '<5s'
    WHEN query_execution_time_seconds < 30 THEN '5-30s'
    WHEN query_execution_time_seconds < 120 THEN '30-120s'
    WHEN query_execution_time_seconds < 300 THEN '2-5min'
    WHEN query_execution_time_seconds < 600 THEN '5-10min'
    ELSE '>10min'
  END as execution_bucket,
  COUNT(*) as query_count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY DATE(query_timestamp)), 2) as pct_of_day
FROM analytics_platform.query_execution_log
WHERE query_timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(query_timestamp), execution_bucket
ORDER BY query_date DESC, execution_bucket;

-- Query 2.3: Most Expensive Queries
SELECT
  query_id,
  user_email,
  query_text,
  warehouse_credits_consumed,
  bytes_scanned / 1024.0 / 1024.0 / 1024.0 as gb_scanned,
  rows_returned,
  query_execution_time_seconds,
  query_timestamp,
  ROUND(warehouse_credits_consumed * 4.0, 2) as estimated_cost_usd
FROM analytics_platform.query_execution_log
WHERE query_timestamp >= CURRENT_DATE - INTERVAL '7 days'
  AND warehouse_credits_consumed > 0
ORDER BY warehouse_credits_consumed DESC
LIMIT 50;

-- ============================================================
-- 3. DASHBOARD & METRIC USAGE
-- ============================================================

-- Query 3.1: Most Used Dashboards
SELECT
  d.dashboard_id,
  d.dashboard_name,
  d.owner_email,
  d.owner_team,
  COUNT(DISTINCT dv.viewer_session_id) as view_count,
  COUNT(DISTINCT dv.viewer_email) as unique_viewers,
  AVG(dv.time_spent_seconds) as avg_time_spent,
  MAX(dv.viewed_at) as last_viewed,
  d.created_at,
  d.last_modified_at
FROM analytics_platform.dashboards d
LEFT JOIN analytics_platform.dashboard_views dv ON d.dashboard_id = dv.dashboard_id
  AND dv.viewed_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY d.dashboard_id, d.dashboard_name, d.owner_email, d.owner_team,
         d.created_at, d.last_modified_at
HAVING COUNT(DISTINCT dv.viewer_session_id) > 0
ORDER BY view_count DESC;

-- Query 3.2: Metric Certification Status & Usage
SELECT
  m.metric_id,
  m.metric_name,
  m.owner_team,
  m.certification_status,
  COUNT(DISTINCT qm.query_id) as usage_count_30days,
  COUNT(DISTINCT qm.user_email) as unique_users,
  m.created_at,
  m.last_calculated_at,
  CASE
    WHEN m.last_calculated_at < CURRENT_TIMESTAMP - INTERVAL '24 hours' THEN 'STALE'
    WHEN m.last_calculated_at < CURRENT_TIMESTAMP - INTERVAL '1 hour' THEN 'AGING'
    ELSE 'FRESH'
  END as freshness_status
FROM analytics_platform.metrics m
LEFT JOIN analytics_platform.query_metric_usage qm ON m.metric_id = qm.metric_id
  AND qm.query_timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY m.metric_id, m.metric_name, m.owner_team, m.certification_status,
         m.created_at, m.last_calculated_at
ORDER BY usage_count_30days DESC;

-- Query 3.3: Unused Dashboards (Cleanup Candidates)
SELECT
  dashboard_id,
  dashboard_name,
  owner_email,
  owner_team,
  created_at,
  last_modified_at,
  (CURRENT_DATE - DATE(last_modified_at))::INT as days_since_modified,
  (CURRENT_DATE - DATE(created_at))::INT as days_since_created
FROM analytics_platform.dashboards
WHERE NOT EXISTS (
  SELECT 1 FROM analytics_platform.dashboard_views
  WHERE dashboard_id = dashboards.dashboard_id
    AND viewed_at >= CURRENT_DATE - INTERVAL '90 days'
)
  AND (CURRENT_DATE - DATE(created_at))::INT > 30
ORDER BY last_modified_at ASC;

-- ============================================================
-- 4. DATA ACCESS & GOVERNANCE
-- ============================================================

-- Query 4.1: Access Request Trends
SELECT
  DATE_TRUNC('week', requested_at) as week_start,
  COUNT(*) as total_requests,
  SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
  SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected,
  SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
  AVG(EXTRACT(EPOCH FROM (approved_at - requested_at)) / 3600.0) as avg_approval_hours
FROM analytics_platform.access_requests
WHERE requested_at >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('week', requested_at)
ORDER BY week_start DESC;

-- Query 4.2: Active Access by Dataset & User
SELECT
  d.dataset_id,
  d.dataset_name,
  d.owner_team,
  COUNT(DISTINCT ag.user_email) as user_count,
  SUM(CASE WHEN ag.access_level = 'analyst' THEN 1 ELSE 0 END) as analyst_access,
  SUM(CASE WHEN ag.access_level = 'viewer' THEN 1 ELSE 0 END) as viewer_access,
  SUM(CASE WHEN ag.access_level = 'engineer' THEN 1 ELSE 0 END) as engineer_access,
  COUNT(DISTINCT CASE WHEN ag.expires_at < CURRENT_TIMESTAMP THEN ag.grant_id END) as expired_grants
FROM analytics_platform.datasets d
JOIN analytics_platform.access_grants ag ON d.dataset_id = ag.dataset_id
WHERE ag.is_active = TRUE
GROUP BY d.dataset_id, d.dataset_name, d.owner_team
ORDER BY user_count DESC;

-- Query 4.3: Data Quality Issues by Dataset
SELECT
  dq.dataset_id,
  dq.dataset_name,
  COUNT(DISTINCT CASE WHEN dq.severity = 'critical' THEN dq.quality_check_id END) as critical_issues,
  COUNT(DISTINCT CASE WHEN dq.severity = 'high' THEN dq.quality_check_id END) as high_issues,
  COUNT(DISTINCT CASE WHEN dq.severity = 'medium' THEN dq.quality_check_id END) as medium_issues,
  MAX(dq.detected_at) as last_issue_detected,
  COUNT(DISTINCT CASE WHEN dq.resolved_at IS NULL THEN dq.quality_check_id END) as unresolved_issues
FROM analytics_platform.data_quality_issues dq
WHERE dq.detected_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY dq.dataset_id, dq.dataset_name
HAVING COUNT(DISTINCT dq.quality_check_id) > 0
ORDER BY critical_issues DESC, last_issue_detected DESC;

-- ============================================================
-- 5. USER ENGAGEMENT & BEHAVIOR
-- ============================================================

-- Query 5.1: User Segmentation by Activity
WITH user_activity AS (
  SELECT
    user_email,
    user_team,
    user_role,
    COUNT(DISTINCT DATE(query_timestamp)) as active_days,
    COUNT(DISTINCT query_id) as total_queries,
    SUM(warehouse_credits_consumed) as total_credits,
    COUNT(DISTINCT dashboard_id) as dashboards_used,
    MAX(query_timestamp) as last_activity
  FROM analytics_platform.query_execution_log
  WHERE query_timestamp >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY user_email, user_team, user_role
)
SELECT
  CASE
    WHEN active_days >= 20 AND total_queries >= 50 THEN 'POWER_USER'
    WHEN active_days >= 15 AND total_queries >= 20 THEN 'REGULAR_USER'
    WHEN active_days >= 5 AND total_queries >= 5 THEN 'CASUAL_USER'
    ELSE 'INACTIVE_USER'
  END as user_segment,
  user_role,
  COUNT(*) as user_count,
  ROUND(AVG(total_queries), 1) as avg_queries,
  ROUND(AVG(active_days), 1) as avg_active_days,
  ROUND(AVG(total_credits), 1) as avg_credits
FROM user_activity
GROUP BY user_segment, user_role
ORDER BY CASE
  WHEN user_segment = 'POWER_USER' THEN 1
  WHEN user_segment = 'REGULAR_USER' THEN 2
  WHEN user_segment = 'CASUAL_USER' THEN 3
  ELSE 4
END;

-- Query 5.2: Learning & Certification Engagement
SELECT
  u.user_email,
  u.user_team,
  COALESCE(c.certification_level, 'NONE') as certification,
  COALESCE(DATE(c.certified_at), 'N/A'::TEXT) as certification_date,
  COUNT(DISTINCT lm.module_id) as completed_modules,
  SUM(CASE WHEN lm.passed = TRUE THEN 1 ELSE 0 END) as passed_assessments,
  MAX(lm.completed_at) as last_module_completion,
  DATEDIFF(day, MAX(lm.completed_at), CURRENT_DATE) as days_since_learning
FROM analytics_platform.users u
LEFT JOIN analytics_platform.certifications c ON u.user_id = c.user_id
LEFT JOIN analytics_platform.learning_modules lm ON u.user_id = lm.user_id
GROUP BY u.user_email, u.user_team, c.certification_level, c.certified_at
ORDER BY certification DESC, completed_modules DESC;

-- ============================================================
-- 6. SYSTEM HEALTH & MONITORING
-- ============================================================

-- Query 6.1: Query Errors & Failures
SELECT
  DATE(query_timestamp) as error_date,
  error_category,
  COUNT(*) as error_count,
  COUNT(DISTINCT user_email) as affected_users,
  STRING_AGG(DISTINCT error_message, '; ' ORDER BY error_message) as error_messages
FROM analytics_platform.query_execution_log
WHERE query_timestamp >= CURRENT_DATE - INTERVAL '7 days'
  AND execution_status = 'FAILED'
GROUP BY DATE(query_timestamp), error_category
ORDER BY error_date DESC, error_count DESC;

-- Query 6.2: Warehouse Performance
SELECT
  DATE(query_timestamp) as warehouse_date,
  HOUR(query_timestamp) as hour_of_day,
  warehouse_name,
  COUNT(*) as query_count,
  AVG(query_execution_time_seconds) as avg_execution_time,
  MAX(query_execution_time_seconds) as max_execution_time,
  SUM(warehouse_credits_consumed) as credits_used,
  COUNT(DISTINCT user_email) as concurrent_users
FROM analytics_platform.query_execution_log
WHERE query_timestamp >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(query_timestamp), HOUR(query_timestamp), warehouse_name
ORDER BY warehouse_date DESC, hour_of_day DESC;

-- Query 6.3: API Usage Statistics
SELECT
  api_endpoint,
  COUNT(*) as request_count,
  COUNT(DISTINCT requester_email) as unique_users,
  ROUND(100.0 * SUM(CASE WHEN response_code = 200 THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate,
  AVG(response_time_ms) as avg_response_time,
  MAX(response_time_ms) as max_response_time,
  SUM(CASE WHEN response_code >= 400 THEN 1 ELSE 0 END) as error_count
FROM analytics_platform.api_request_log
WHERE request_timestamp >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY api_endpoint
ORDER BY request_count DESC;

-- ============================================================
-- 7. LINEAGE & DEPENDENCY TRACKING
-- ============================================================

-- Query 7.1: Most Referenced Tables
SELECT
  t.table_name,
  t.schema_name,
  COUNT(DISTINCT l.source_query_id) as referenced_in_queries,
  COUNT(DISTINCT l.user_email) as users_who_reference,
  MAX(l.last_referenced) as last_referenced_date,
  (CURRENT_DATE - DATE(MAX(l.last_referenced)))::INT as days_since_reference
FROM analytics_platform.tables t
JOIN analytics_platform.table_lineage l ON t.table_id = l.table_id
WHERE l.last_referenced >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY t.table_name, t.schema_name
ORDER BY referenced_in_queries DESC
LIMIT 30;

-- Query 7.2: Impact Analysis - Potential Downstream Effects
SELECT
  source_table_id,
  source_table_name,
  COUNT(DISTINCT dependent_metric_id) as dependent_metrics,
  COUNT(DISTINCT dependent_dashboard_id) as dependent_dashboards,
  COUNT(DISTINCT dependent_query_id) as dependent_queries,
  MAX(last_dependency_reference) as most_recent_dependency_use
FROM analytics_platform.vw_dependency_tree
WHERE depth <= 3
GROUP BY source_table_id, source_table_name
HAVING COUNT(DISTINCT dependent_metric_id) > 0
  OR COUNT(DISTINCT dependent_dashboard_id) > 0
ORDER BY dependent_dashboards DESC, dependent_metrics DESC;

-- ============================================================
-- 8. COST & RESOURCE OPTIMIZATION
-- ============================================================

-- Query 8.1: Credit Spend by Team
SELECT
  user_team,
  SUM(warehouse_credits_consumed) as total_credits,
  COUNT(*) as query_count,
  COUNT(DISTINCT user_email) as team_members,
  ROUND(SUM(warehouse_credits_consumed) / COUNT(*), 2) as avg_credits_per_query,
  MAX(warehouse_credits_consumed) as max_query_cost,
  ROUND(SUM(warehouse_credits_consumed) * 4.0, 2) as estimated_monthly_cost_usd
FROM analytics_platform.query_execution_log
WHERE query_timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY user_team
ORDER BY total_credits DESC;

-- Query 8.2: Query Efficiency Score (Credits vs Rows Returned)
SELECT
  user_email,
  user_team,
  AVG(CASE
    WHEN rows_returned > 0 THEN warehouse_credits_consumed / NULLIF(rows_returned::NUMERIC, 0)
    ELSE warehouse_credits_consumed
  END) as credits_per_row,
  COUNT(DISTINCT query_id) as query_count,
  SUM(warehouse_credits_consumed) as total_credits,
  ROUND(AVG(query_execution_time_seconds), 2) as avg_execution_seconds,
  CASE
    WHEN AVG(CASE WHEN rows_returned > 0 THEN warehouse_credits_consumed / NULLIF(rows_returned::NUMERIC, 0) ELSE warehouse_credits_consumed END) < 0.001 THEN 'EXCELLENT'
    WHEN AVG(CASE WHEN rows_returned > 0 THEN warehouse_credits_consumed / NULLIF(rows_returned::NUMERIC, 0) ELSE warehouse_credits_consumed END) < 0.01 THEN 'GOOD'
    WHEN AVG(CASE WHEN rows_returned > 0 THEN warehouse_credits_consumed / NULLIF(rows_returned::NUMERIC, 0) ELSE warehouse_credits_consumed END) < 0.1 THEN 'FAIR'
    ELSE 'NEEDS_OPTIMIZATION'
  END as efficiency_rating
FROM analytics_platform.query_execution_log
WHERE query_timestamp >= CURRENT_DATE - INTERVAL '30 days'
  AND warehouse_credits_consumed > 0
GROUP BY user_email, user_team
HAVING COUNT(DISTINCT query_id) >= 10
ORDER BY credits_per_row ASC;

-- ============================================================
-- 9. ALERTING & ANOMALY DETECTION
-- ============================================================

-- Query 9.1: Unusual Query Patterns
SELECT
  user_email,
  user_team,
  COUNT(*) as query_count_today,
  LAG(COUNT(*)) OVER (PARTITION BY user_email ORDER BY DATE(query_timestamp)) as queries_yesterday,
  ROUND(100.0 * (COUNT(*) - LAG(COUNT(*)) OVER (PARTITION BY user_email ORDER BY DATE(query_timestamp))) /
    NULLIF(LAG(COUNT(*)) OVER (PARTITION BY user_email ORDER BY DATE(query_timestamp)), 0), 2) as pct_change
FROM analytics_platform.query_execution_log
WHERE query_timestamp >= CURRENT_DATE - INTERVAL '2 days'
GROUP BY user_email, user_team, DATE(query_timestamp)
HAVING ROUND(100.0 * (COUNT(*) - LAG(COUNT(*)) OVER (PARTITION BY user_email ORDER BY DATE(query_timestamp))) /
  NULLIF(LAG(COUNT(*)) OVER (PARTITION BY user_email ORDER BY DATE(query_timestamp)), 0), 2) > 200
ORDER BY pct_change DESC;

-- Query 9.2: Data Freshness Alerts
SELECT
  dataset_id,
  dataset_name,
  owner_team,
  last_refresh_time,
  (CURRENT_TIMESTAMP - last_refresh_time) as time_since_refresh,
  EXTRACT(HOUR FROM (CURRENT_TIMESTAMP - last_refresh_time)) as hours_since_refresh,
  sla_refresh_hours,
  CASE
    WHEN EXTRACT(HOUR FROM (CURRENT_TIMESTAMP - last_refresh_time)) > sla_refresh_hours THEN 'VIOLATED'
    WHEN EXTRACT(HOUR FROM (CURRENT_TIMESTAMP - last_refresh_time)) > sla_refresh_hours * 0.8 THEN 'AT_RISK'
    ELSE 'ON_TRACK'
  END as sla_status
FROM analytics_platform.datasets
WHERE EXTRACT(HOUR FROM (CURRENT_TIMESTAMP - last_refresh_time)) > sla_refresh_hours
ORDER BY hours_since_refresh DESC;

-- ============================================================
-- 10. SUMMARY METRICS & KPIs
-- ============================================================

-- Query 10.1: Overall Platform KPIs (Last 30 Days)
SELECT
  'ACTIVE_USERS' as metric,
  COUNT(DISTINCT user_email)::TEXT as value,
  'COUNT' as unit
FROM analytics_platform.query_execution_log
WHERE query_timestamp >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT
  'TOTAL_QUERIES' as metric,
  COUNT(*)::TEXT as value,
  'COUNT' as unit
FROM analytics_platform.query_execution_log
WHERE query_timestamp >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT
  'AVG_QUERY_TIME' as metric,
  ROUND(AVG(query_execution_time_seconds), 2)::TEXT as value,
  'SECONDS' as unit
FROM analytics_platform.query_execution_log
WHERE query_timestamp >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT
  'TOTAL_CREDITS' as metric,
  ROUND(SUM(warehouse_credits_consumed), 2)::TEXT as value,
  'CREDITS' as unit
FROM analytics_platform.query_execution_log
WHERE query_timestamp >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT
  'DASHBOARDS_CREATED' as metric,
  COUNT(*)::TEXT as value,
  'COUNT' as unit
FROM analytics_platform.dashboards
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT
  'DATA_QUALITY_ISSUES' as metric,
  COUNT(*)::TEXT as value,
  'COUNT' as unit
FROM analytics_platform.data_quality_issues
WHERE detected_at >= CURRENT_DATE - INTERVAL '30 days'
  AND resolved_at IS NULL;

