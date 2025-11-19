-- Access Control Setup for Self-Service Analytics
-- Snowflake example (adapt for your warehouse)

-- ======================
-- 1. CREATE ROLES
-- ======================

-- Viewer role: Dashboard access only
CREATE ROLE IF NOT EXISTS data_viewer
  COMMENT = 'Can view pre-built dashboards';

-- Analyst role: Query and create dashboards
CREATE ROLE IF NOT EXISTS data_analyst
  COMMENT = 'Can query data and create dashboards';

-- Engineer role: Build pipelines
CREATE ROLE IF NOT EXISTS data_engineer
  COMMENT = 'Can create tables and pipelines';

-- Admin role: Full access
CREATE ROLE IF NOT EXISTS data_admin
  COMMENT = 'Full administrative access';

-- ======================
-- 2. GRANT DATABASE ACCESS
-- ======================

-- Grant usage on database
GRANT USAGE ON DATABASE analytics TO ROLE data_viewer;
GRANT USAGE ON DATABASE analytics TO ROLE data_analyst;
GRANT USAGE ON DATABASE analytics TO ROLE data_engineer;
GRANT ALL ON DATABASE analytics TO ROLE data_admin;

-- Grant usage on schemas
GRANT USAGE ON SCHEMA analytics.public TO ROLE data_viewer;
GRANT USAGE ON ALL SCHEMAS IN DATABASE analytics TO ROLE data_analyst;
GRANT ALL ON ALL SCHEMAS IN DATABASE analytics TO ROLE data_engineer;

-- ======================
-- 3. GRANT TABLE PERMISSIONS
-- ======================

-- Viewer: SELECT on public schema only
GRANT SELECT ON ALL TABLES IN SCHEMA analytics.public TO ROLE data_viewer;
GRANT SELECT ON ALL VIEWS IN SCHEMA analytics.public TO ROLE data_viewer;
GRANT SELECT ON FUTURE TABLES IN SCHEMA analytics.public TO ROLE data_viewer;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA analytics.public TO ROLE data_viewer;

-- Analyst: SELECT on all schemas, CREATE in sandbox
GRANT SELECT ON ALL TABLES IN DATABASE analytics TO ROLE data_analyst;
GRANT SELECT ON ALL VIEWS IN DATABASE analytics TO ROLE data_analyst;
GRANT SELECT ON FUTURE TABLES IN DATABASE analytics TO ROLE data_analyst;
GRANT CREATE TABLE ON SCHEMA analytics.sandbox TO ROLE data_analyst;
GRANT CREATE VIEW ON SCHEMA analytics.sandbox TO ROLE data_analyst;

-- Engineer: CREATE, INSERT, UPDATE, DELETE
GRANT ALL ON ALL TABLES IN DATABASE analytics TO ROLE data_engineer;
GRANT ALL ON FUTURE TABLES IN DATABASE analytics TO ROLE data_engineer;

-- ======================
-- 4. WAREHOUSE ACCESS
-- ======================

-- Create warehouses for different workloads
CREATE WAREHOUSE IF NOT EXISTS analytics_wh
  WITH WAREHOUSE_SIZE = 'SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'General analytics queries';

CREATE WAREHOUSE IF NOT EXISTS adhoc_wh
  WITH WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Ad-hoc exploration';

-- Grant warehouse usage
GRANT USAGE ON WAREHOUSE analytics_wh TO ROLE data_viewer;
GRANT USAGE ON WAREHOUSE analytics_wh TO ROLE data_analyst;
GRANT USAGE ON WAREHOUSE adhoc_wh TO ROLE data_analyst;
GRANT ALL ON WAREHOUSE analytics_wh TO ROLE data_engineer;

-- ======================
-- 5. ROW-LEVEL SECURITY
-- ======================

-- Example: Sales territory access
CREATE OR REPLACE ROW ACCESS POLICY sales_territory_policy
AS (territory_id VARCHAR) RETURNS BOOLEAN ->
  CASE
    WHEN CURRENT_ROLE() = 'DATA_ADMIN' THEN TRUE
    WHEN EXISTS (
      SELECT 1 FROM analytics.security.user_territories
      WHERE user_email = CURRENT_USER()
        AND territory_id = territory_id
    ) THEN TRUE
    ELSE FALSE
  END
COMMENT = 'Users see only their territory data';

-- Apply policy to sales table
ALTER TABLE analytics.core.fct_sales
  ADD ROW ACCESS POLICY sales_territory_policy
  ON (territory_id);

-- ======================
-- 6. COLUMN MASKING
-- ======================

-- Email masking policy
CREATE OR REPLACE MASKING POLICY email_mask AS
  (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('DATA_ADMIN', 'PII_VIEWER')
      THEN val
    ELSE REGEXP_REPLACE(val, '^.(.*)@', '*****@')
  END
COMMENT = 'Mask email except for authorized roles';

-- Apply masking to email columns
ALTER TABLE analytics.core.dim_customers
  MODIFY COLUMN email
  SET MASKING POLICY email_mask;

-- SSN masking
CREATE OR REPLACE MASKING POLICY ssn_mask AS
  (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('DATA_ADMIN', 'PII_VIEWER')
      THEN val
    ELSE CONCAT('XXX-XX-', SUBSTR(val, -4))
  END;

-- ======================
-- 7. ASSIGN USERS TO ROLES
-- ======================

-- Grant roles to specific users
GRANT ROLE data_viewer TO USER john.doe@company.com;
GRANT ROLE data_analyst TO USER jane.smith@company.com;
GRANT ROLE data_engineer TO USER bob.jones@company.com;
GRANT ROLE data_admin TO USER admin@company.com;

-- ======================
-- 8. RESOURCE MONITORS
-- ======================

-- Create cost control monitor
CREATE RESOURCE MONITOR IF NOT EXISTS monthly_quota
  WITH CREDIT_QUOTA = 1000
  FREQUENCY = MONTHLY
  START_TIMESTAMP = IMMEDIATELY
  TRIGGERS
    ON 75 PERCENT DO NOTIFY
    ON 100 PERCENT DO SUSPEND
    ON 110 PERCENT DO SUSPEND_IMMEDIATE;

-- Apply to warehouse
ALTER WAREHOUSE analytics_wh
  SET RESOURCE_MONITOR = monthly_quota;

-- ======================
-- 9. QUERY TIMEOUTS
-- ======================

-- Set statement timeout (5 minutes)
ALTER ACCOUNT SET STATEMENT_TIMEOUT_IN_SECONDS = 300;

-- Or per user
ALTER USER jane.smith@company.com
  SET STATEMENT_TIMEOUT_IN_SECONDS = 600;

-- ======================
-- 10. AUDIT LOGGING
-- ======================

-- Create audit log view
CREATE OR REPLACE VIEW analytics.security.access_audit AS
SELECT
  query_id,
  query_text,
  user_name,
  role_name,
  warehouse_name,
  database_name,
  schema_name,
  execution_status,
  error_message,
  start_time,
  end_time,
  total_elapsed_time / 1000 as seconds,
  bytes_scanned,
  rows_produced
FROM TABLE(information_schema.query_history())
WHERE start_time >= DATEADD('day', -7, CURRENT_TIMESTAMP())
ORDER BY start_time DESC;

-- Grant access to audit log
GRANT SELECT ON analytics.security.access_audit TO ROLE data_admin;
