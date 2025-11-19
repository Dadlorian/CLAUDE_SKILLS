-- Governance Dashboard - Production-Grade SQL
-- Comprehensive view of data governance, access controls, and compliance metrics
-- Purpose: Support governance teams in monitoring access, usage patterns, and compliance

-- ============================================================================
-- 1. ACCESS CONTROL AUDIT VIEW
-- ============================================================================

CREATE OR REPLACE VIEW governance.access_control_audit AS
WITH user_roles AS (
  SELECT
    ur.user_id,
    u.email,
    u.full_name,
    r.role_name,
    r.role_type,
    ur.granted_at,
    ur.expires_at,
    CASE
      WHEN ur.expires_at < CURRENT_TIMESTAMP THEN 'expired'
      WHEN ur.expires_at < CURRENT_TIMESTAMP + INTERVAL '30 days' THEN 'expiring_soon'
      ELSE 'active'
    END as role_status
  FROM iam.user_roles ur
  JOIN iam.users u ON ur.user_id = u.user_id
  JOIN iam.roles r ON ur.role_id = r.role_id
  WHERE u.deleted_at IS NULL
),
dataset_access AS (
  SELECT
    da.dataset_id,
    d.dataset_name,
    d.owner_id,
    ur.user_id,
    ur.role_name,
    da.permission_type,
    da.granted_at,
    da.granted_by,
    ur.role_status,
    ROW_NUMBER() OVER (
      PARTITION BY da.dataset_id, ur.user_id
      ORDER BY da.granted_at DESC
    ) as grant_recency
  FROM governance.dataset_access_grants da
  JOIN user_roles ur ON da.role_id = ur.role_id
  JOIN analytics.datasets d ON da.dataset_id = d.dataset_id
)
SELECT
  da.dataset_id,
  da.dataset_name,
  da.user_id,
  ur.email,
  ur.full_name,
  da.role_name,
  da.permission_type,
  da.role_status,
  da.granted_at,
  DATEDIFF(day, da.granted_at, CURRENT_TIMESTAMP) as days_since_grant,
  ur.expires_at,
  DATEDIFF(day, CURRENT_TIMESTAMP, ur.expires_at) as days_until_expiry
FROM dataset_access da
JOIN user_roles ur ON da.user_id = ur.user_id
  AND da.role_name = ur.role_name
WHERE da.grant_recency = 1
ORDER BY da.dataset_id, ur.email;

-- ============================================================================
-- 2. DATA CLASSIFICATION COMPLIANCE REPORT
-- ============================================================================

CREATE OR REPLACE VIEW governance.data_classification_compliance AS
WITH dataset_classifications AS (
  SELECT
    d.dataset_id,
    d.dataset_name,
    d.owner_id,
    dcs.classification_level,
    dcs.pii_indicator,
    dcs.phi_indicator,
    dcs.pci_indicator,
    dcs.classified_at,
    dcs.classification_confidence,
    COUNT(DISTINCT c.column_id) as classified_columns,
    COUNT(DISTINCT CASE WHEN c.is_sensitive = TRUE THEN c.column_id END) as sensitive_columns
  FROM analytics.datasets d
  LEFT JOIN governance.dataset_classifications dcs ON d.dataset_id = dcs.dataset_id
  LEFT JOIN analytics.columns c ON d.dataset_id = c.dataset_id
  WHERE d.deleted_at IS NULL
  GROUP BY
    d.dataset_id,
    d.dataset_name,
    d.owner_id,
    dcs.classification_level,
    dcs.pii_indicator,
    dcs.phi_indicator,
    dcs.pci_indicator,
    dcs.classified_at,
    dcs.classification_confidence
)
SELECT
  dc.dataset_id,
  dc.dataset_name,
  dc.owner_id,
  COALESCE(dc.classification_level, 'unclassified') as classification_level,
  CASE
    WHEN dc.pii_indicator = TRUE THEN 'YES'
    WHEN dc.pii_indicator = FALSE THEN 'NO'
    ELSE 'UNKNOWN'
  END as contains_pii,
  CASE
    WHEN dc.phi_indicator = TRUE THEN 'YES'
    WHEN dc.phi_indicator = FALSE THEN 'NO'
    ELSE 'UNKNOWN'
  END as contains_phi,
  CASE
    WHEN dc.pci_indicator = TRUE THEN 'YES'
    WHEN dc.pci_indicator = FALSE THEN 'NO'
    ELSE 'UNKNOWN'
  END as contains_pci,
  dc.classified_columns,
  dc.sensitive_columns,
  ROUND(dc.classified_columns * 100.0 / NULLIF(dc.classified_columns + dc.sensitive_columns, 0), 2) as classification_coverage_pct,
  COALESCE(dc.classification_confidence, 0) as confidence_score,
  DATEDIFF(day, dc.classified_at, CURRENT_TIMESTAMP) as days_since_classification,
  CASE
    WHEN dc.classified_at IS NULL THEN 'FAIL'
    WHEN dc.classification_confidence < 0.8 THEN 'WARN'
    ELSE 'PASS'
  END as compliance_status
FROM dataset_classifications dc
ORDER BY
  CASE WHEN dc.classified_at IS NULL THEN 0 ELSE 1 END,
  dc.classification_confidence DESC;

-- ============================================================================
-- 3. USER ACTIVITY COMPLIANCE MONITORING
-- ============================================================================

CREATE OR REPLACE VIEW governance.user_activity_monitoring AS
WITH daily_activity AS (
  SELECT
    DATE(ua.activity_timestamp) as activity_date,
    ua.user_id,
    u.email,
    u.department,
    COUNT(*) as query_count,
    COUNT(DISTINCT ua.dataset_id) as distinct_datasets,
    COUNT(DISTINCT CASE WHEN ua.activity_type = 'export' THEN ua.activity_id END) as export_count,
    COUNT(DISTINCT CASE WHEN ua.activity_type = 'share' THEN ua.activity_id END) as share_count,
    COUNT(DISTINCT CASE WHEN ua.activity_type = 'download' THEN ua.activity_id END) as download_count,
    SUM(CASE WHEN ua.result_rows > 10000 THEN 1 ELSE 0 END) as large_result_queries,
    AVG(CASE WHEN ua.query_execution_time_ms > 0
           THEN ua.query_execution_time_ms END) as avg_query_time_ms
  FROM audit.user_activity ua
  JOIN iam.users u ON ua.user_id = u.user_id
  WHERE ua.activity_timestamp >= CURRENT_TIMESTAMP - INTERVAL '30 days'
    AND u.deleted_at IS NULL
  GROUP BY
    DATE(ua.activity_timestamp),
    ua.user_id,
    u.email,
    u.department
)
SELECT
  da.activity_date,
  da.user_id,
  da.email,
  da.department,
  da.query_count,
  da.distinct_datasets,
  da.export_count,
  da.share_count,
  da.download_count,
  da.large_result_queries,
  ROUND(da.avg_query_time_ms, 2) as avg_query_time_ms,
  CASE
    WHEN da.export_count > 5 THEN 'HIGH_EXPORT_ACTIVITY'
    WHEN da.large_result_queries > 2 THEN 'LARGE_RESULT_QUERIES'
    WHEN da.download_count > 10 THEN 'HIGH_DOWNLOAD_ACTIVITY'
    ELSE 'NORMAL'
  END as activity_risk_level,
  ROW_NUMBER() OVER (
    PARTITION BY da.activity_date
    ORDER BY da.query_count DESC
  ) as daily_user_rank
FROM daily_activity da
ORDER BY da.activity_date DESC, da.query_count DESC;

-- ============================================================================
-- 4. POLICY VIOLATION DETECTION
-- ============================================================================

CREATE OR REPLACE VIEW governance.policy_violations AS
WITH user_access_summary AS (
  SELECT
    ur.user_id,
    u.email,
    COUNT(DISTINCT d.dataset_id) as accessible_datasets,
    COUNT(DISTINCT CASE
      WHEN dcs.classification_level IN ('confidential', 'restricted')
      THEN d.dataset_id
    END) as sensitive_dataset_access
  FROM iam.user_roles ur
  JOIN iam.users u ON ur.user_id = u.user_id
  JOIN governance.dataset_access_grants dag ON ur.role_id = dag.role_id
  JOIN analytics.datasets d ON dag.dataset_id = d.dataset_id
  JOIN governance.dataset_classifications dcs ON d.dataset_id = dcs.dataset_id
  WHERE u.deleted_at IS NULL
    AND ur.expires_at > CURRENT_TIMESTAMP
  GROUP BY ur.user_id, u.email
),
excessive_permissions AS (
  SELECT
    uas.user_id,
    uas.email,
    uas.accessible_datasets,
    uas.sensitive_dataset_access,
    CASE
      WHEN uas.accessible_datasets > 50 THEN 'excessive_dataset_access'
      WHEN uas.sensitive_dataset_access > 10 THEN 'excessive_sensitive_access'
      ELSE NULL
    END as violation_type
  FROM user_access_summary uas
  WHERE uas.accessible_datasets > 50
     OR uas.sensitive_dataset_access > 10
),
expired_access AS (
  SELECT
    ur.user_id,
    u.email,
    COUNT(*) as expired_roles,
    'expired_role_access' as violation_type
  FROM iam.user_roles ur
  JOIN iam.users u ON ur.user_id = u.user_id
  WHERE ur.expires_at < CURRENT_TIMESTAMP
    AND u.deleted_at IS NULL
  GROUP BY ur.user_id, u.email
),
all_violations AS (
  SELECT
    ep.user_id,
    ep.email,
    ep.violation_type,
    CAST(NULL as INTEGER) as violation_detail_1,
    CAST(NULL as INTEGER) as violation_detail_2,
    CURRENT_TIMESTAMP as detected_at
  FROM excessive_permissions ep
  WHERE ep.violation_type IS NOT NULL

  UNION ALL

  SELECT
    ea.user_id,
    ea.email,
    ea.violation_type,
    ea.expired_roles as violation_detail_1,
    NULL as violation_detail_2,
    CURRENT_TIMESTAMP as detected_at
  FROM expired_access ea
)
SELECT
  av.user_id,
  av.email,
  av.violation_type,
  av.violation_detail_1,
  av.detected_at,
  'OPEN' as violation_status,
  NULL as resolved_at,
  ROW_NUMBER() OVER (
    PARTITION BY av.user_id
    ORDER BY av.detected_at DESC
  ) as violation_sequence
FROM all_violations av
ORDER BY av.detected_at DESC;

-- ============================================================================
-- 5. DATA LINEAGE & IMPACT ANALYSIS
-- ============================================================================

CREATE OR REPLACE VIEW governance.data_lineage_impact AS
WITH recursive lineage_chain AS (
  SELECT
    dl.source_dataset_id,
    dl.target_dataset_id,
    ds.dataset_name as source_name,
    dt.dataset_name as target_name,
    dl.transformation_type,
    1 as lineage_depth,
    ARRAY[dl.source_dataset_id] as path
  FROM governance.data_lineage dl
  JOIN analytics.datasets ds ON dl.source_dataset_id = ds.dataset_id
  JOIN analytics.datasets dt ON dl.target_dataset_id = dt.dataset_id

  UNION ALL

  SELECT
    lc.source_dataset_id,
    dl.target_dataset_id,
    lc.source_name,
    dt.dataset_name,
    dl.transformation_type,
    lc.lineage_depth + 1,
    lc.path || dl.target_dataset_id
  FROM lineage_chain lc
  JOIN governance.data_lineage dl ON lc.target_dataset_id = dl.source_dataset_id
  JOIN analytics.datasets dt ON dl.target_dataset_id = dt.dataset_id
  WHERE lc.lineage_depth < 5
    AND NOT dl.target_dataset_id = ANY(lc.path)
)
SELECT
  lc.source_dataset_id,
  lc.source_name,
  lc.target_dataset_id,
  lc.target_name,
  lc.transformation_type,
  lc.lineage_depth,
  ARRAY_LENGTH(lc.path, 1) as affected_datasets,
  COUNT(DISTINCT dag.user_id) as users_accessing_target,
  MAX(ua.activity_timestamp) as last_access_target,
  CASE
    WHEN lc.lineage_depth > 3 THEN 'DEEP'
    WHEN lc.lineage_depth > 1 THEN 'MEDIUM'
    ELSE 'SHALLOW'
  END as lineage_complexity
FROM lineage_chain lc
LEFT JOIN governance.dataset_access_grants dag ON lc.target_dataset_id = dag.dataset_id
LEFT JOIN audit.user_activity ua ON dag.dataset_id = ua.dataset_id
GROUP BY
  lc.source_dataset_id,
  lc.source_name,
  lc.target_dataset_id,
  lc.target_name,
  lc.transformation_type,
  lc.lineage_depth,
  lc.path
ORDER BY lc.source_dataset_id, lc.lineage_depth;

-- ============================================================================
-- 6. GOVERNANCE METRICS SUMMARY
-- ============================================================================

CREATE OR REPLACE VIEW governance.metrics_summary AS
SELECT
  CURRENT_TIMESTAMP as report_timestamp,

  -- Access Control Metrics
  (SELECT COUNT(DISTINCT user_id) FROM governance.access_control_audit
   WHERE role_status = 'active') as active_users,

  (SELECT COUNT(DISTINCT dataset_id) FROM governance.access_control_audit) as datasets_with_access_grants,

  (SELECT COUNT(*) FROM governance.access_control_audit
   WHERE role_status = 'expiring_soon') as expiring_access_grants,

  -- Classification Metrics
  (SELECT COUNT(*) FROM governance.data_classification_compliance
   WHERE compliance_status = 'PASS') as fully_classified_datasets,

  (SELECT COUNT(*) FROM governance.data_classification_compliance
   WHERE contains_pii = 'YES') as datasets_containing_pii,

  -- Compliance Metrics
  (SELECT COUNT(*) FROM governance.policy_violations) as open_policy_violations,

  (SELECT COUNT(DISTINCT user_id) FROM governance.policy_violations) as users_with_violations,

  -- Activity Metrics
  (SELECT COUNT(DISTINCT user_id) FROM governance.user_activity_monitoring
   WHERE activity_date = CAST(CURRENT_TIMESTAMP as DATE)) as active_users_today,

  (SELECT SUM(query_count) FROM governance.user_activity_monitoring
   WHERE activity_date = CAST(CURRENT_TIMESTAMP as DATE)) as queries_today,

  (SELECT SUM(export_count) FROM governance.user_activity_monitoring
   WHERE activity_date >= CURRENT_TIMESTAMP - INTERVAL '7 days') as exports_last_7_days,

  -- Lineage Metrics
  (SELECT COUNT(DISTINCT source_dataset_id) FROM governance.data_lineage_impact) as datasets_with_lineage,

  (SELECT AVG(lineage_depth) FROM governance.data_lineage_impact) as avg_lineage_depth;

-- ============================================================================
-- 7. DASHBOARD DRILL-DOWN QUERIES
-- ============================================================================

-- Top datasets by user access
CREATE OR REPLACE VIEW governance.top_datasets_by_access AS
SELECT
  TOP 20
  da.dataset_id,
  da.dataset_name,
  COUNT(DISTINCT da.user_id) as unique_users,
  COUNT(*) as total_access_grants
FROM governance.access_control_audit da
GROUP BY da.dataset_id, da.dataset_name
ORDER BY unique_users DESC;

-- Department access patterns
CREATE OR REPLACE VIEW governance.department_access_patterns AS
SELECT
  u.department,
  COUNT(DISTINCT u.user_id) as department_users,
  COUNT(DISTINCT da.dataset_id) as accessible_datasets,
  COUNT(DISTINCT CASE WHEN da.permission_type = 'write' THEN da.dataset_id END) as writable_datasets,
  AVG(CASE WHEN dcs.classification_level IN ('confidential', 'restricted') THEN 1 ELSE 0 END) as avg_sensitive_access
FROM iam.users u
LEFT JOIN governance.access_control_audit da ON u.user_id = da.user_id
LEFT JOIN governance.dataset_classifications dcs ON da.dataset_id = dcs.dataset_id
WHERE u.deleted_at IS NULL
GROUP BY u.department
ORDER BY accessible_datasets DESC;
