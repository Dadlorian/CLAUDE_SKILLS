-- Usage Tracking Views and Tables
-- Track analytics asset access, queries, and engagement metrics
-- Purpose: Monitor data catalog usage and user adoption

-- ============================================================================
-- 1. Query Audit Log Table (stores all executed queries)
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.governance.query_audit_log (
    query_id STRING NOT NULL,
    session_id STRING NOT NULL,
    user_id STRING NOT NULL,
    user_email STRING NOT NULL,
    query_text STRING NOT NULL,
    database_name STRING NOT NULL,
    schema_name STRING,
    table_names ARRAY(STRING),
    execution_timestamp TIMESTAMP NOT NULL,
    query_duration_seconds DECIMAL(10, 2),
    rows_scanned BIGINT,
    rows_returned BIGINT,
    bytes_scanned BIGINT,
    bytes_returned BIGINT,
    warehouse_name STRING,
    is_success BOOLEAN,
    error_message STRING,
    query_type STRING,  -- SELECT, INSERT, UPDATE, DELETE, CREATE, DROP
    is_pii_query BOOLEAN,
    accessed_classifications ARRAY(STRING),
    ip_address STRING,
    user_agent STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) CLUSTER BY user_id, execution_timestamp;

-- Create hourly partitioning for performance
ALTER TABLE analytics.governance.query_audit_log
SET CLUSTER KEY (user_id, execution_timestamp);


-- ============================================================================
-- 2. Dataset Access Log (tracks which datasets were accessed)
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.governance.dataset_access_log (
    access_id STRING NOT NULL,
    user_id STRING NOT NULL,
    user_email STRING NOT NULL,
    user_department STRING,
    dataset_id STRING NOT NULL,
    dataset_name STRING NOT NULL,
    schema_name STRING NOT NULL,
    access_type STRING NOT NULL,  -- read, write, create, delete
    access_timestamp TIMESTAMP NOT NULL,
    query_id STRING,
    row_count BIGINT,
    bytes_accessed BIGINT,
    is_approved_access BOOLEAN,
    requires_pii_access BOOLEAN,
    access_duration_seconds DECIMAL(10, 2),
    success BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) CLUSTER BY user_id, dataset_id, access_timestamp;


-- ============================================================================
-- 3. Dashboard View Events (tracks dashboard interactions)
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.governance.dashboard_view_events (
    event_id STRING NOT NULL,
    user_id STRING NOT NULL,
    user_email STRING NOT NULL,
    dashboard_id STRING NOT NULL,
    dashboard_name STRING NOT NULL,
    dashboard_owner STRING,
    view_timestamp TIMESTAMP NOT NULL,
    view_duration_seconds DECIMAL(10, 2),
    filter_applied STRING,
    drilldown_used BOOLEAN,
    export_triggered BOOLEAN,
    export_format STRING,  -- csv, pdf, excel
    shared BOOLEAN,
    shared_with_users INT,
    device_type STRING,  -- desktop, mobile, tablet
    browser STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) CLUSTER BY user_id, dashboard_id, view_timestamp;


-- ============================================================================
-- 4. Report Subscription Events
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.governance.report_subscriptions (
    subscription_id STRING NOT NULL PRIMARY KEY,
    user_id STRING NOT NULL,
    user_email STRING NOT NULL,
    report_id STRING NOT NULL,
    report_name STRING NOT NULL,
    subscription_date TIMESTAMP NOT NULL,
    frequency STRING,  -- daily, weekly, monthly
    delivery_email STRING,
    delivery_format STRING,  -- pdf, excel, email_body
    is_active BOOLEAN DEFAULT TRUE,
    last_sent_timestamp TIMESTAMP,
    send_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);


-- ============================================================================
-- 5. Data Export Events (compliance tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.governance.data_export_events (
    export_id STRING NOT NULL PRIMARY KEY,
    user_id STRING NOT NULL,
    user_email STRING NOT NULL,
    dataset_id STRING NOT NULL,
    dataset_name STRING NOT NULL,
    export_timestamp TIMESTAMP NOT NULL,
    export_format STRING,  -- csv, parquet, excel
    row_count BIGINT,
    file_size_bytes BIGINT,
    is_encrypted BOOLEAN,
    encryption_method STRING,
    is_via_vpn BOOLEAN,
    destination STRING,  -- local, cloud, email
    approver_email STRING,
    approval_timestamp TIMESTAMP,
    classifications_exported ARRAY(STRING),
    pii_exported BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);


-- ============================================================================
-- 6. Metric Usage Tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.governance.metric_usage_log (
    usage_id STRING NOT NULL,
    metric_id STRING NOT NULL,
    metric_name STRING NOT NULL,
    user_id STRING NOT NULL,
    user_email STRING NOT NULL,
    dashboard_id STRING,
    report_id STRING,
    usage_timestamp TIMESTAMP NOT NULL,
    metric_value DECIMAL(20, 4),
    filter_values VARIANT,  -- JSON of applied filters
    query_id STRING,
    execution_time_seconds DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) CLUSTER BY metric_id, usage_timestamp;


-- ============================================================================
-- 7. User Engagement Summary View
-- ============================================================================

CREATE OR REPLACE VIEW analytics.governance.v_user_engagement_daily AS
SELECT
    DATE(access_timestamp) AS access_date,
    user_id,
    user_email,
    user_department,
    COUNT(DISTINCT access_id) AS total_accesses,
    COUNT(DISTINCT dataset_id) AS unique_datasets_accessed,
    SUM(row_count) AS total_rows_accessed,
    SUM(bytes_accessed) / (1024 * 1024) AS total_mb_accessed,
    SUM(CASE WHEN requires_pii_access THEN 1 ELSE 0 END) AS pii_accesses,
    SUM(CASE WHEN is_approved_access = FALSE THEN 1 ELSE 0 END) AS unapproved_accesses,
    SUM(CASE WHEN success = FALSE THEN 1 ELSE 0 END) AS failed_accesses
FROM analytics.governance.dataset_access_log
GROUP BY
    DATE(access_timestamp),
    user_id,
    user_email,
    user_department;


-- ============================================================================
-- 8. Dashboard Popularity View
-- ============================================================================

CREATE OR REPLACE VIEW analytics.governance.v_dashboard_popularity AS
SELECT
    dashboard_id,
    dashboard_name,
    dashboard_owner,
    DATE_TRUNC(MONTH, view_timestamp) AS month,
    COUNT(DISTINCT event_id) AS total_views,
    COUNT(DISTINCT user_id) AS unique_users,
    AVG(view_duration_seconds) AS avg_view_duration_seconds,
    SUM(CASE WHEN export_triggered THEN 1 ELSE 0 END) AS export_count,
    SUM(CASE WHEN shared THEN 1 ELSE 0 END) AS share_count,
    SUM(CASE WHEN drilldown_used THEN 1 ELSE 0 END) AS drilldown_count,
    ROUND(100.0 * SUM(CASE WHEN export_triggered THEN 1 ELSE 0 END) / COUNT(*), 2) AS export_rate_pct
FROM analytics.governance.dashboard_view_events
GROUP BY
    dashboard_id,
    dashboard_name,
    dashboard_owner,
    DATE_TRUNC(MONTH, view_timestamp);


-- ============================================================================
-- 9. Query Performance Summary
-- ============================================================================

CREATE OR REPLACE VIEW analytics.governance.v_query_performance AS
SELECT
    DATE(execution_timestamp) AS query_date,
    user_id,
    user_email,
    database_name,
    COUNT(query_id) AS total_queries,
    AVG(query_duration_seconds) AS avg_duration_seconds,
    MAX(query_duration_seconds) AS max_duration_seconds,
    MIN(query_duration_seconds) AS min_duration_seconds,
    SUM(CASE WHEN is_success = FALSE THEN 1 ELSE 0 END) AS failed_queries,
    SUM(rows_scanned) AS total_rows_scanned,
    SUM(bytes_scanned) / (1024 * 1024 * 1024) AS total_gb_scanned,
    ROUND(100.0 * SUM(CASE WHEN is_success THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate_pct
FROM analytics.governance.query_audit_log
GROUP BY
    DATE(execution_timestamp),
    user_id,
    user_email,
    database_name;


-- ============================================================================
-- 10. Data Governance Compliance View
-- ============================================================================

CREATE OR REPLACE VIEW analytics.governance.v_compliance_audit AS
SELECT
    access_timestamp,
    user_id,
    user_email,
    dataset_id,
    dataset_name,
    access_type,
    is_approved_access,
    requires_pii_access,
    success,
    CASE
        WHEN requires_pii_access AND is_approved_access = FALSE THEN 'VIOLATION: Unapproved PII Access'
        WHEN success = FALSE AND requires_pii_access THEN 'VIOLATION: Failed PII Query'
        WHEN is_approved_access = FALSE THEN 'WARNING: Unapproved Access'
        ELSE 'COMPLIANT'
    END AS compliance_status
FROM analytics.governance.dataset_access_log
WHERE
    access_timestamp >= CURRENT_DATE - 90
    AND (
        (requires_pii_access AND is_approved_access = FALSE)
        OR (success = FALSE AND requires_pii_access)
        OR is_approved_access = FALSE
    );


-- ============================================================================
-- 11. PII Access Audit Trail
-- ============================================================================

CREATE OR REPLACE VIEW analytics.governance.v_pii_access_audit AS
SELECT
    access_timestamp,
    user_id,
    user_email,
    dataset_id,
    dataset_name,
    schema_name,
    accessed_classifications,
    rows_scanned,
    bytes_accessed,
    execution_timestamp,
    query_duration_seconds,
    is_pii_query,
    ip_address,
    user_agent
FROM analytics.governance.query_audit_log
WHERE
    is_pii_query = TRUE
    OR accessed_classifications LIKE '%PII%'
ORDER BY
    execution_timestamp DESC;


-- ============================================================================
-- 12. Metadata Enrichment: Catalog Assets Heat Map
-- ============================================================================

CREATE OR REPLACE VIEW analytics.governance.v_catalog_heatmap AS
SELECT
    dal.dataset_id,
    dal.dataset_name,
    dal.schema_name,
    COUNT(DISTINCT dal.user_id) AS unique_users_30d,
    COUNT(DISTINCT dal.access_id) AS access_count_30d,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN dal.success THEN dal.user_id END) /
        NULLIF(COUNT(DISTINCT dal.user_id), 0), 2) AS success_rate_pct,
    SUM(dal.bytes_accessed) / (1024 * 1024) AS total_mb_accessed_30d,
    MAX(dal.access_timestamp) AS last_accessed,
    ROUND((CURRENT_TIMESTAMP - MAX(dal.access_timestamp))::INT / 24, 1) AS days_since_last_access,
    CASE
        WHEN COUNT(DISTINCT dal.user_id) >= 50 THEN 'HOT - Critical'
        WHEN COUNT(DISTINCT dal.user_id) >= 20 THEN 'WARM - Active'
        WHEN COUNT(DISTINCT dal.user_id) >= 5 THEN 'COOL - Moderate'
        ELSE 'COLD - Low Usage'
    END AS usage_tier
FROM analytics.governance.dataset_access_log dal
WHERE
    dal.access_timestamp >= CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY
    dal.dataset_id,
    dal.dataset_name,
    dal.schema_name;


-- ============================================================================
-- 13. Usage Metrics for Self-Service Analytics
-- ============================================================================

CREATE OR REPLACE VIEW analytics.governance.v_adoption_metrics AS
SELECT
    DATE_TRUNC(WEEK, access_timestamp) AS week,
    COUNT(DISTINCT user_id) AS active_users,
    COUNT(DISTINCT access_id) AS total_accesses,
    COUNT(DISTINCT dataset_id) AS datasets_used,
    SUM(bytes_accessed) / (1024 * 1024 * 1024) AS total_gb_accessed,
    ROUND(100.0 * SUM(CASE WHEN success THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS success_rate_pct,
    COUNT(DISTINCT CASE WHEN requires_pii_access THEN access_id END) AS pii_accesses
FROM analytics.governance.dataset_access_log
GROUP BY
    DATE_TRUNC(WEEK, access_timestamp)
ORDER BY
    week DESC;


-- ============================================================================
-- 14. Stored Procedure for Cleanup (optional)
-- ============================================================================

CREATE OR REPLACE PROCEDURE analytics.governance.sp_cleanup_old_logs(
    retention_days INT DEFAULT 90
)
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    DELETE FROM analytics.governance.query_audit_log
    WHERE execution_timestamp < CURRENT_TIMESTAMP - INTERVAL '{retention_days} day';

    DELETE FROM analytics.governance.dataset_access_log
    WHERE access_timestamp < CURRENT_TIMESTAMP - INTERVAL '{retention_days} day';

    DELETE FROM analytics.governance.dashboard_view_events
    WHERE view_timestamp < CURRENT_TIMESTAMP - INTERVAL '{retention_days} day';

    RETURN 'Cleanup completed successfully';
END
$$;

-- ============================================================================
-- 15. Create Usage Tracking Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_query_audit_user ON analytics.governance.query_audit_log (user_id, execution_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_query_audit_table ON analytics.governance.query_audit_log (database_name, schema_name);
CREATE INDEX IF NOT EXISTS idx_dataset_access_user ON analytics.governance.dataset_access_log (user_id, access_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_dataset_access_dataset ON analytics.governance.dataset_access_log (dataset_id, access_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_dashboard_views_user ON analytics.governance.dashboard_view_events (user_id, view_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_pii_access ON analytics.governance.query_audit_log (is_pii_query) WHERE is_pii_query = TRUE;
