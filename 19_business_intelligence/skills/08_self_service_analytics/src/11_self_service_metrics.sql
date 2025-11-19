-- Self-Service Analytics Metrics - Production SQL
-- Comprehensive tracking of adoption, usage, and business impact metrics
-- Purpose: Monitor self-service analytics program success and ROI

-- ============================================================================
-- 1. USER ADOPTION METRICS
-- ============================================================================

CREATE OR REPLACE VIEW analytics.adoption_metrics AS
WITH user_cohorts AS (
  SELECT
    u.user_id,
    u.email,
    u.department,
    u.job_title,
    DATE(u.created_at) as onboarding_date,
    DATE_TRUNC('month', u.created_at) as cohort_month
  FROM iam.users u
  WHERE u.deleted_at IS NULL
    AND u.created_at >= DATEADD(year, -2, CURRENT_TIMESTAMP)
),
first_activity AS (
  SELECT
    uc.user_id,
    uc.email,
    uc.department,
    uc.job_title,
    uc.onboarding_date,
    uc.cohort_month,
    MIN(DATE(ua.activity_timestamp)) as first_activity_date,
    DATEDIFF(day, uc.onboarding_date, MIN(DATE(ua.activity_timestamp))) as days_to_first_activity
  FROM user_cohorts uc
  LEFT JOIN audit.user_activity ua ON uc.user_id = ua.user_id
  GROUP BY
    uc.user_id, uc.email, uc.department, uc.job_title,
    uc.onboarding_date, uc.cohort_month
),
monthly_activity AS (
  SELECT
    uc.user_id,
    DATE_TRUNC('month', ua.activity_timestamp) as activity_month,
    COUNT(*) as monthly_queries,
    COUNT(DISTINCT ua.dataset_id) as datasets_accessed
  FROM user_cohorts uc
  LEFT JOIN audit.user_activity ua ON uc.user_id = ua.user_id
  GROUP BY uc.user_id, DATE_TRUNC('month', ua.activity_timestamp)
)
SELECT
  fa.user_id,
  fa.email,
  fa.department,
  fa.job_title,
  fa.onboarding_date,
  fa.cohort_month,
  fa.first_activity_date,
  fa.days_to_first_activity,
  CASE
    WHEN fa.first_activity_date IS NULL THEN 'NOT_ACTIVATED'
    WHEN fa.days_to_first_activity <= 7 THEN 'QUICK_ADOPTER'
    WHEN fa.days_to_first_activity <= 30 THEN 'STEADY_ADOPTER'
    ELSE 'SLOW_ADOPTER'
  END as adoption_category,
  COALESCE(SUM(ma.monthly_queries), 0) as lifetime_queries,
  COALESCE(MAX(ma.datasets_accessed), 0) as max_datasets_in_month,
  DATEDIFF(day, fa.onboarding_date, CURRENT_TIMESTAMP) as days_since_onboarding,
  CASE
    WHEN DATEDIFF(day, fa.onboarding_date, CURRENT_TIMESTAMP) <= 30 THEN 'NEW'
    WHEN DATEDIFF(day, fa.onboarding_date, CURRENT_TIMESTAMP) <= 90 THEN 'EMERGING'
    WHEN DATEDIFF(day, fa.onboarding_date, CURRENT_TIMESTAMP) <= 365 THEN 'ESTABLISHED'
    ELSE 'MATURE'
  END as user_tenure
FROM first_activity fa
LEFT JOIN monthly_activity ma ON fa.user_id = ma.user_id
GROUP BY
  fa.user_id, fa.email, fa.department, fa.job_title,
  fa.onboarding_date, fa.cohort_month, fa.first_activity_date,
  fa.days_to_first_activity
ORDER BY fa.cohort_month DESC, fa.onboarding_date DESC;

-- ============================================================================
-- 2. QUERY PERFORMANCE & EFFICIENCY METRICS
-- ============================================================================

CREATE OR REPLACE VIEW analytics.query_performance_metrics AS
WITH query_stats AS (
  SELECT
    DATE_TRUNC('day', ua.activity_timestamp) as query_date,
    ua.user_id,
    COUNT(*) as daily_queries,
    COUNT(DISTINCT ua.dataset_id) as distinct_datasets,
    AVG(ua.query_execution_time_ms) as avg_exec_time_ms,
    MAX(ua.query_execution_time_ms) as max_exec_time_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (
      ORDER BY ua.query_execution_time_ms
    ) as p95_exec_time_ms,
    SUM(CASE WHEN ua.query_cached = 1 THEN 1 ELSE 0 END) as cached_queries,
    SUM(CASE WHEN ua.result_rows > 1000000 THEN 1 ELSE 0 END) as large_result_queries,
    SUM(CASE WHEN ua.query_result_row_count > 0 THEN 1 ELSE 0 END) as successful_queries,
    SUM(CASE WHEN ua.query_result_row_count = 0 THEN 1 ELSE 0 END) as empty_result_queries,
    COUNT(DISTINCT CASE WHEN ua.query_error_flag = 1 THEN ua.activity_id END) as failed_queries
  FROM audit.user_activity ua
  WHERE ua.activity_type = 'query'
    AND ua.activity_timestamp >= DATEADD(month, -1, CURRENT_TIMESTAMP)
  GROUP BY
    DATE_TRUNC('day', ua.activity_timestamp),
    ua.user_id
)
SELECT
  qs.query_date,
  qs.user_id,
  qs.daily_queries,
  qs.distinct_datasets,
  ROUND(qs.avg_exec_time_ms, 2) as avg_exec_time_ms,
  qs.max_exec_time_ms,
  ROUND(qs.p95_exec_time_ms, 2) as p95_exec_time_ms,
  ROUND(qs.cached_queries * 100.0 / NULLIF(qs.daily_queries, 0), 1) as cache_hit_rate_pct,
  qs.large_result_queries,
  ROUND(qs.successful_queries * 100.0 / NULLIF(qs.daily_queries, 0), 1) as success_rate_pct,
  qs.failed_queries,
  CASE
    WHEN qs.avg_exec_time_ms > 5000 THEN 'SLOW'
    WHEN qs.avg_exec_time_ms > 1000 THEN 'MODERATE'
    WHEN qs.success_rate_pct >= 95 THEN 'GOOD'
    ELSE 'NEEDS_OPTIMIZATION'
  END as performance_grade
FROM query_stats qs
ORDER BY qs.query_date DESC, qs.user_id;

-- ============================================================================
-- 3. DATASET UTILIZATION & POPULARITY
-- ============================================================================

CREATE OR REPLACE VIEW analytics.dataset_utilization AS
WITH dataset_access_stats AS (
  SELECT
    ua.dataset_id,
    d.dataset_name,
    d.owner_id,
    COUNT(DISTINCT ua.user_id) as unique_users,
    COUNT(*) as total_queries,
    COUNT(DISTINCT DATE(ua.activity_timestamp)) as days_accessed,
    MIN(ua.activity_timestamp) as first_access,
    MAX(ua.activity_timestamp) as last_access,
    SUM(ua.result_rows) as total_rows_returned,
    AVG(ua.query_execution_time_ms) as avg_query_time_ms,
    SUM(CASE WHEN ua.query_cached = 1 THEN 1 ELSE 0 END) as cached_accesses
  FROM audit.user_activity ua
  JOIN analytics.datasets d ON ua.dataset_id = d.dataset_id
  WHERE ua.activity_timestamp >= DATEADD(year, -1, CURRENT_TIMESTAMP)
  GROUP BY ua.dataset_id, d.dataset_name, d.owner_id
),
daily_access AS (
  SELECT
    ua.dataset_id,
    DATE_TRUNC('day', ua.activity_timestamp) as access_date,
    COUNT(DISTINCT ua.user_id) as daily_unique_users
  FROM audit.user_activity ua
  WHERE ua.activity_timestamp >= DATEADD(month, -3, CURRENT_TIMESTAMP)
  GROUP BY ua.dataset_id, DATE_TRUNC('day', ua.activity_timestamp)
)
SELECT
  das.dataset_id,
  das.dataset_name,
  das.owner_id,
  das.unique_users,
  das.total_queries,
  das.days_accessed,
  ROUND(das.total_queries * 100.0 / SUM(das.total_queries) OVER (), 2) as query_share_pct,
  DATEDIFF(day, das.first_access, CURRENT_TIMESTAMP) as days_since_first_access,
  DATEDIFF(day, das.last_access, CURRENT_TIMESTAMP) as days_since_last_access,
  ROUND(das.total_rows_returned / 1000000.0, 2) as total_millions_rows_returned,
  ROUND(das.avg_query_time_ms, 2) as avg_query_time_ms,
  ROUND(das.cached_accesses * 100.0 / NULLIF(das.total_queries, 0), 1) as cache_rate_pct,
  CASE
    WHEN das.total_queries > 1000 THEN 'CRITICAL'
    WHEN das.total_queries > 100 THEN 'HIGH_VALUE'
    WHEN das.total_queries > 10 THEN 'MODERATE'
    ELSE 'LOW_USAGE'
  END as usage_tier,
  CASE
    WHEN DATEDIFF(day, das.last_access, CURRENT_TIMESTAMP) > 90 THEN 'DORMANT'
    WHEN DATEDIFF(day, das.last_access, CURRENT_TIMESTAMP) > 30 THEN 'DECLINING'
    ELSE 'ACTIVE'
  END as usage_trend
FROM dataset_access_stats das
ORDER BY das.total_queries DESC;

-- ============================================================================
-- 4. USER ENGAGEMENT FUNNEL
-- ============================================================================

CREATE OR REPLACE VIEW analytics.engagement_funnel AS
WITH user_actions AS (
  SELECT
    u.user_id,
    u.email,
    u.department,
    DATE(u.created_at) as signup_date,
    SUM(CASE WHEN ua.activity_type IN ('query', 'dashboard_view') THEN 1 ELSE 0 END) as exploration_actions,
    SUM(CASE WHEN ua.activity_type IN ('dashboard_create', 'saved_query') THEN 1 ELSE 0 END) as creation_actions,
    SUM(CASE WHEN ua.activity_type = 'share' THEN 1 ELSE 0 END) as sharing_actions,
    MAX(ua.activity_timestamp) as last_activity
  FROM iam.users u
  LEFT JOIN audit.user_activity ua ON u.user_id = ua.user_id
    AND ua.activity_timestamp >= DATEADD(month, -3, CURRENT_TIMESTAMP)
  WHERE u.deleted_at IS NULL
  GROUP BY u.user_id, u.email, u.department, DATE(u.created_at)
)
SELECT
  ua.user_id,
  ua.email,
  ua.department,
  ua.signup_date,
  CASE WHEN ua.last_activity IS NOT NULL THEN 'ACTIVATED' ELSE 'NOT_ACTIVATED' END as activation_status,
  CASE
    WHEN ua.exploration_actions > 0 THEN 'YES'
    ELSE 'NO'
  END as has_explored,
  CASE
    WHEN ua.creation_actions > 0 THEN 'YES'
    ELSE 'NO'
  END as has_created,
  CASE
    WHEN ua.sharing_actions > 0 THEN 'YES'
    ELSE 'NO'
  END as has_shared,
  ROUND(100.0 *
    (CASE WHEN ua.exploration_actions > 0 THEN 1 ELSE 0 END) *
    (CASE WHEN ua.creation_actions > 0 THEN 1 ELSE 0 END) *
    (CASE WHEN ua.sharing_actions > 0 THEN 1 ELSE 0 END), 0) as engagement_score,
  CASE
    WHEN ua.sharing_actions > 0 THEN 'CHAMPION'
    WHEN ua.creation_actions > 0 THEN 'CREATOR'
    WHEN ua.exploration_actions > 0 THEN 'EXPLORER'
    WHEN ua.last_activity IS NOT NULL THEN 'BROWSER'
    ELSE 'INACTIVE'
  END as user_segment
FROM user_actions ua
ORDER BY engagement_score DESC, ua.signup_date DESC;

-- ============================================================================
-- 5. BUSINESS IMPACT & ROI METRICS
-- ============================================================================

CREATE OR REPLACE VIEW analytics.business_impact_metrics AS
WITH self_service_queries AS (
  SELECT
    DATE_TRUNC('week', ua.activity_timestamp) as metric_week,
    COUNT(DISTINCT ua.user_id) as self_service_users,
    COUNT(*) as self_service_queries,
    SUM(ua.result_rows) as rows_analyzed
  FROM audit.user_activity ua
  WHERE ua.activity_timestamp >= DATEADD(month, -6, CURRENT_TIMESTAMP)
    AND ua.activity_type IN ('query', 'dashboard_view')
  GROUP BY DATE_TRUNC('week', ua.activity_timestamp)
),
analyst_requests AS (
  SELECT
    DATE_TRUNC('week', request_created_at) as metric_week,
    COUNT(*) as analyst_requests,
    AVG(DATEDIFF(day, request_created_at, request_completed_at)) as avg_turnaround_days
  FROM analytics.analyst_requests
  WHERE request_created_at >= DATEADD(month, -6, CURRENT_TIMESTAMP)
  GROUP BY DATE_TRUNC('week', request_created_at)
)
SELECT
  COALESCE(ssq.metric_week, ar.metric_week) as report_week,
  COALESCE(ssq.self_service_users, 0) as self_service_users,
  COALESCE(ssq.self_service_queries, 0) as self_service_queries,
  COALESCE(ar.analyst_requests, 0) as analyst_requests,
  ROUND(COALESCE(ar.avg_turnaround_days, 0), 1) as avg_analyst_turnaround_days,
  CASE
    WHEN COALESCE(ar.analyst_requests, 0) > 0
    THEN ROUND(COALESCE(ssq.self_service_queries, 0) * 100.0 / (COALESCE(ssq.self_service_queries, 0) + COALESCE(ar.analyst_requests, 0)), 1)
    ELSE 0
  END as self_service_rate_pct,
  COALESCE(ssq.rows_analyzed, 0) as total_rows_analyzed_by_users,
  ROUND(COALESCE(ssq.rows_analyzed, 0) / NULLIF(COALESCE(ssq.self_service_queries, 0), 0), 0) as avg_rows_per_query,
  DATEDIFF(day, COALESCE(ssq.metric_week, ar.metric_week), CURRENT_TIMESTAMP) as days_ago
FROM self_service_queries ssq
FULL OUTER JOIN analyst_requests ar ON ssq.metric_week = ar.metric_week
ORDER BY report_week DESC;

-- ============================================================================
-- 6. TRAINING & CERTIFICATION METRICS
-- ============================================================================

CREATE OR REPLACE VIEW analytics.training_metrics AS
SELECT
  t.training_id,
  t.training_name,
  t.training_type,
  COUNT(DISTINCT e.user_id) as total_enrollments,
  COUNT(DISTINCT CASE WHEN e.completion_status = 'completed' THEN e.user_id END) as completions,
  COUNT(DISTINCT CASE WHEN e.completion_status = 'in_progress' THEN e.user_id END) as in_progress,
  COUNT(DISTINCT CASE WHEN e.completion_status = 'not_started' THEN e.user_id END) as not_started,
  ROUND(COUNT(DISTINCT CASE WHEN e.completion_status = 'completed' THEN e.user_id END) * 100.0 /
        NULLIF(COUNT(DISTINCT e.user_id), 0), 1) as completion_rate_pct,
  AVG(CASE WHEN e.completion_status = 'completed' THEN e.completion_score END) as avg_completion_score,
  MIN(e.enrollment_date) as first_enrollment,
  MAX(e.completion_date) as latest_completion,
  COUNT(DISTINCT CASE WHEN e.completion_date >= DATEADD(week, -1, CURRENT_TIMESTAMP)
    THEN e.user_id END) as completions_this_week
FROM training.trainings t
LEFT JOIN training.enrollments e ON t.training_id = e.training_id
GROUP BY t.training_id, t.training_name, t.training_type
ORDER BY total_enrollments DESC;

-- ============================================================================
-- 7. SUPPORT & SATISFACTION METRICS
-- ============================================================================

CREATE OR REPLACE VIEW analytics.support_metrics AS
WITH ticket_stats AS (
  SELECT
    DATE_TRUNC('day', st.created_at) as ticket_date,
    COUNT(*) as tickets_created,
    COUNT(DISTINCT CASE WHEN st.status = 'resolved' THEN st.ticket_id END) as tickets_resolved,
    AVG(CASE WHEN st.status = 'resolved'
      THEN DATEDIFF(hour, st.created_at, st.resolved_at)
    END) as avg_resolution_hours,
    AVG(st.satisfaction_score) as avg_satisfaction_score,
    COUNT(DISTINCT st.user_id) as unique_users
  FROM support.tickets st
  WHERE st.created_at >= DATEADD(month, -3, CURRENT_TIMESTAMP)
  GROUP BY DATE_TRUNC('day', st.created_at)
)
SELECT
  ts.ticket_date,
  ts.tickets_created,
  ts.tickets_resolved,
  ROUND(ts.avg_resolution_hours, 1) as avg_resolution_hours,
  ROUND(ts.avg_satisfaction_score, 2) as avg_satisfaction_score,
  ts.unique_users,
  ROUND(ts.tickets_resolved * 100.0 / NULLIF(ts.tickets_created, 0), 1) as resolution_rate_pct,
  DATEDIFF(day, ts.ticket_date, CURRENT_TIMESTAMP) as days_ago
FROM ticket_stats ts
ORDER BY ts.ticket_date DESC;

-- ============================================================================
-- 8. COHORT RETENTION ANALYSIS
-- ============================================================================

CREATE OR REPLACE VIEW analytics.cohort_retention AS
WITH user_cohorts AS (
  SELECT
    DATE_TRUNC('month', u.created_at)::DATE as cohort_month,
    u.user_id,
    DATE_TRUNC('month', ua.activity_timestamp)::DATE as activity_month,
    ROW_NUMBER() OVER (
      PARTITION BY u.user_id
      ORDER BY DATE_TRUNC('month', ua.activity_timestamp)
    ) as month_number
  FROM iam.users u
  LEFT JOIN audit.user_activity ua ON u.user_id = ua.user_id
  WHERE u.deleted_at IS NULL
    AND u.created_at >= DATEADD(year, -2, CURRENT_TIMESTAMP)
)
SELECT
  uc.cohort_month,
  COUNT(DISTINCT CASE WHEN uc.month_number = 1 THEN uc.user_id END) as cohort_size,
  COUNT(DISTINCT CASE WHEN uc.month_number = 1 THEN uc.user_id END) as m0_users,
  COUNT(DISTINCT CASE WHEN uc.month_number = 2 THEN uc.user_id END) as m1_users,
  COUNT(DISTINCT CASE WHEN uc.month_number = 3 THEN uc.user_id END) as m2_users,
  COUNT(DISTINCT CASE WHEN uc.month_number = 4 THEN uc.user_id END) as m3_users,
  COUNT(DISTINCT CASE WHEN uc.month_number = 6 THEN uc.user_id END) as m6_users,
  COUNT(DISTINCT CASE WHEN uc.month_number = 12 THEN uc.user_id END) as m12_users,
  ROUND(COUNT(DISTINCT CASE WHEN uc.month_number = 2 THEN uc.user_id END) * 100.0 /
        NULLIF(COUNT(DISTINCT CASE WHEN uc.month_number = 1 THEN uc.user_id END), 0), 1) as m1_retention_pct
FROM user_cohorts uc
GROUP BY uc.cohort_month
ORDER BY uc.cohort_month DESC;
